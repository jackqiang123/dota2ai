-- run.lua -- 5v5 全局模拟 integration 入口。
-- 用法 (仓库根目录): lua5.4 tools/integration/run.lua [--minutes 40] [--tick 1]
--   [--seed 42] [--difficulty 3] [--radiant axe,zeus,lion,crystal_maiden,magnus]
--   [--dire sven,dazzle,enigma,faceless_void,huskar] [--out tools/integration/last_run.md]
--   [--stats-out /tmp/run_stats.lua] [--debug]  (每 15 秒打印每个 Bot 的位置 / 快照 / 最后一道指令, 用于定位卡住)
-- --stats-out 写一份结构化 Lua 表 (return {...}, 可 dofile 加载), 供 hero_tests.lua
-- 逐英雄判定门控; 不给则不写。
-- 每 tick 顺序按 Valve 调用约定: TeamThink -> 各 Bot Think ->
-- 各 Bot AbilityUsageThink / ItemPurchaseThink / AbilityLevelUpThink -> 世界步进。
-- 退出码 0 = 全部 gate 通过; 1 = 有 gate 未通过 (见报告)。
-- Lua 5.1 语法兼容。

-- ---- 参数与仓库根目录推导 (不用绝对路径硬编码) ----
local function parseArgs()
  local o = {
    minutes = 40, tick = 1.0, seed = 42, difficulty = 3,
    radiant = "axe,zeus,lion,crystal_maiden,magnus",
    dire = "sven,dazzle,enigma,faceless_void,huskar",
    out = nil, statsOut = nil, debug = false, trace = nil,
  }
  local i = 1
  while arg[i] ~= nil do
    local a = arg[i]
    if a == "--minutes" then o.minutes = tonumber(arg[i + 1]) or 40 i = i + 2
    elseif a == "--tick" then o.tick = tonumber(arg[i + 1]) or 1.0 i = i + 2
    elseif a == "--seed" then o.seed = tonumber(arg[i + 1]) or 42 i = i + 2
    elseif a == "--difficulty" then o.difficulty = tonumber(arg[i + 1]) or 3 i = i + 2
    elseif a == "--radiant" then o.radiant = arg[i + 1] or o.radiant i = i + 2
    elseif a == "--dire" then o.dire = arg[i + 1] or o.dire i = i + 2
    elseif a == "--out" then o.out = arg[i + 1] i = i + 2
    elseif a == "--stats-out" then o.statsOut = arg[i + 1] i = i + 2
    elseif a == "--debug" then o.debug = true i = i + 1
    elseif a == "--trace" then o.trace = arg[i + 1] i = i + 2
    else i = i + 1 end
  end
  return o
end

local opts = parseArgs()
local rawArg0 = (arg and arg[0]) or "tools/integration/run.lua"
local ROOT = rawArg0
if rawArg0 == "run.lua" then
  ROOT = "../.."
else
  ROOT = rawArg0:gsub("/tools/integration/run%.lua$", "")
  if ROOT == rawArg0 then
    ROOT = rawArg0:gsub("tools/integration/run%.lua$", ".")
  end
  if ROOT == "" then ROOT = "." end
end
if opts.out == nil then opts.out = ROOT .. "/tools/integration/last_run.md" end

package.path = ROOT .. "/tools/integration/?.lua;"
  .. ROOT .. "/scripts/vscripts/?.lua;"
  .. ROOT .. "/scripts/vscripts/?/init.lua;"
  .. package.path

local Sim = require("sim")
local Valve = require("valve_api")

local function splitList(s)
  local out = {}
  for part in string.gmatch(s, "[^,]+") do
    part = part:gsub("^%s+", ""):gsub("%s+$", "")
    if part ~= "" then out[#out + 1] = part end
  end
  return out
end

local radiantKeys = splitList(opts.radiant)
local direKeys = splitList(opts.dire)
assert(#radiantKeys == 5, "radiant lineup must have 5 heroes")
assert(#direKeys == 5, "dire lineup must have 5 heroes")

print(string.format(
  "integration run: %d min, tick %.2fs, seed %d, difficulty %d",
  opts.minutes, opts.tick, opts.seed, opts.difficulty))
print("radiant: " .. table.concat(radiantKeys, ", "))
print("dire: " .. table.concat(direKeys, ", "))

math.randomseed(opts.seed)

-- ---- 阵容与分路 (读 data/heroes.lua 的 lane/positions) ----
local HeroesData = require("bots/data/heroes")
local function laneFor(team, key)
  local hd = HeroesData[key]
  local lane = "mid"
  if hd ~= nil and hd.lane ~= nil then lane = hd.lane end
  if lane == "mid" then return "mid" end
  if lane == "offlane" or lane == "roam" then
    -- roam (游走位) 开局跟劣势路走, 和 offlane 同一路; 与 utility.GetHeroLane
    -- 保持一致 (旧版 roam 掉到下面的 safelane 分支, 和 Bot 自认的中路也不一致)。
    if team == 2 then return "top" else return "bot" end
  end
  -- safelane 与 support 都跟大哥走安全线。
  if team == 2 then return "bot" else return "top" end
end
local function posFor(key)
  local hd = HeroesData[key]
  if hd ~= nil and hd.positions ~= nil and hd.positions[1] ~= nil then
    return hd.positions[1]
  end
  return 5
end

local cfgHeroes = {}
for _, key in ipairs(radiantKeys) do
  cfgHeroes[#cfgHeroes + 1] = { key = key, team = 2, pos = posFor(key), lane = laneFor(2, key) }
end
for _, key in ipairs(direKeys) do
  cfgHeroes[#cfgHeroes + 1] = { key = key, team = 3, pos = posFor(key), lane = laneFor(3, key) }
end

local world = Sim.new({
  minutes = opts.minutes, tick = opts.tick, seed = opts.seed, heroes = cfgHeroes,
})
Valve.install(world, { difficulty = opts.difficulty })

-- ---- 加载 Bot 脚本 (逐英雄 dofile, 立刻捕获全局入口, 避免互相覆盖) ----
local errors = {}
local function recordError(tick, botKey, phase, err)
  errors[#errors + 1] = { tick = tick, time = world.time, bot = botKey or "system", phase = phase, err = tostring(err) }
  if #errors <= 20 then
    print(string.format("[error] tick %d t=%.0f bot=%s phase=%s: %s", tick, world.time, botKey or "system", phase, tostring(err)))
  end
end

-- 指令数上限 (防死循环): 每段 Bot 调用最多 200 万条指令, 超限即报错并记入报告。
local INSTR_LIMIT = 2000000
local function guardedCall(fn, tick, botKey, phase)
  if fn == nil then return false, "no function" end
  local hook = function() error("instruction limit exceeded (" .. phase .. ")") end
  debug.sethook(hook, "", INSTR_LIMIT)
  local ok, err = pcall(fn)
  debug.sethook()
  if not ok then recordError(tick, botKey, phase, err) end
  return ok, err
end

local botsDir = ROOT .. "/scripts/vscripts/bots/"
local perBot = {}
local teamThinkFn = nil
do
  local ok, err = pcall(dofile, botsDir .. "team_think.lua")
  if ok and _G.TeamThink ~= nil then teamThinkFn = _G.TeamThink
  else recordError(0, "system", "load team_think", err or "TeamThink missing") end
end

local genericAbility = require("bots/ability_item_usage_generic")
local genericItem = require("bots/item_purchase_generic")

for _, hero in ipairs(world.heroes) do
  local fns = { key = hero.key, team = hero.team, hero = hero, bot = hero._bot }
  local ok, err = pcall(dofile, botsDir .. "bot_" .. hero.key .. ".lua")
  if ok and _G.Think ~= nil then
    fns.think = _G.Think
  else
    recordError(0, hero.key, "load bot_" .. hero.key, err or "Think missing")
    local ok2 = pcall(dofile, botsDir .. "bot_generic.lua")
    if ok2 and _G.Think ~= nil then fns.think = _G.Think end
  end
  local okA, errA = pcall(dofile, botsDir .. "ability_item_usage_" .. hero.key .. ".lua")
  if okA and _G.AbilityUsageThink ~= nil then
    fns.ability = _G.AbilityUsageThink
    fns.levelup = _G.AbilityLevelUpThink
  else
    recordError(0, hero.key, "load ability_item_usage_" .. hero.key, errA or "AbilityUsageThink missing")
    fns.ability = genericAbility.AbilityUsageThink
    fns.levelup = genericAbility.AbilityLevelUpThink
  end
  local okI, errI = pcall(dofile, botsDir .. "item_purchase_" .. hero.key .. ".lua")
  if okI and _G.ItemPurchaseThink ~= nil then
    fns.item = _G.ItemPurchaseThink
  else
    recordError(0, hero.key, "load item_purchase_" .. hero.key, errI or "ItemPurchaseThink missing")
    fns.item = function()
      local b = GetBot()
      if b ~= nil then genericItem.ItemPurchaseThinkFor(b) end
    end
  end
  perBot[#perBot + 1] = fns
end

-- ---- 主循环 ----
local totalTicks = math.floor(opts.minutes * 60 / opts.tick)
local wallStart = os.clock()
local wallLimit = 900
local planRoshanTicks = 0
local firstRoshanPlanAt = nil
local aborted = nil

-- 卡住检测状态 (每英雄): 60 秒窗口起点。
for _, hero in ipairs(world.heroes) do
  hero._stickX, hero._stickY, hero._stickT = hero.x, hero.y, 0
  hero._stickAlive = true
  -- 卡住检测的行动基线: 站桩补刀 (位移小但一直在攻击/放技能) 不是卡住,
  -- 只有位移 <50 且 60 秒内零行动 (无命中/施放/购买/移动指令) 才算卡住。
  hero._stickActs = 0
  hero._fountainSecs = 0
  hero._respawnGraceUntil = 0
end

for tick = 1, totalTicks do
  if world.winner ~= nil then break end
  if os.clock() - wallStart > wallLimit then
    aborted = "wall-clock limit " .. wallLimit .. "s exceeded"
    recordError(tick, "system", "watchdog", aborted)
    break
  end
  -- 1. TeamThink (每队一次, 当前 Bot 设为该队第一个活着的英雄)。
  if teamThinkFn ~= nil then
    for _, team in ipairs({ 2, 3 }) do
      local rep = nil
      for _, h in ipairs(world.heroes) do
        if h.team == team and h.alive then rep = h break end
      end
      if rep == nil then rep = world.heroes[1] end
      Valve.setCurrentBot(rep._bot)
      guardedCall(teamThinkFn, tick, "team" .. team, "TeamThink")
    end
  end
  -- 2. 各 Bot Think。
  for _, f in ipairs(perBot) do
    if f.hero.alive then
      Valve.setCurrentBot(f.bot)
      guardedCall(f.think, tick, f.key, "Think")
    end
  end
  -- 3. 技能 / 买装 / 加点。
  for _, f in ipairs(perBot) do
    if f.hero.alive then
      Valve.setCurrentBot(f.bot)
      guardedCall(f.ability, tick, f.key, "AbilityUsageThink")
      guardedCall(f.item, tick, f.key, "ItemPurchaseThink")
      guardedCall(f.levelup, tick, f.key, "AbilityLevelUpThink")
    end
  end
  Valve.setCurrentBot(nil)
  -- 黑板 plan 统计。
  local bb = _G.DOTA_AI_BLACKBOARD
  if bb ~= nil and bb.plan == "roshan" then
    planRoshanTicks = planRoshanTicks + 1
    if firstRoshanPlanAt == nil then firstRoshanPlanAt = world.time end
  end
  -- 4. 世界步进。
  local okStep, errStep = pcall(Sim.step, world)
  if not okStep then
    recordError(tick, "system", "Sim.step", errStep)
    break
  end
  Valve.tick(world, world.dt)
  -- 5. 卡住 / 泉水挂机检测。
  for _, h in ipairs(world.heroes) do
    if h.alive then
      if world.time - h._stickT >= 60 then
        if h._stickAlive then
          local d = Sim.dist(h._stickX, h._stickY, h.x, h.y)
          local acts = h.stats.attacksLanded + h.stats.casts + h.stats.buys + h.stats.moves
          if d < 50 and acts == (h._stickActs or 0) and h.stuck == nil then
            h.stuck = { at = world.time, x = h.x, y = h.y, moved = d }
          end
          h._stickActs = acts
        end
        h._stickX, h._stickY, h._stickT = h.x, h.y, world.time
        h._stickAlive = true
      end
      local fx, fy = Sim.fountain(h.team)
      if world.time > 60 and world.time > (h._respawnGraceUntil or 0)
        and Sim.dist(h.x, h.y, fx, fy) <= 600 then
        h._fountainSecs = (h._fountainSecs or 0) + world.dt
        if h._fountainSecs >= 120 and h.fountainCamp == nil then
          h.fountainCamp = { at = world.time }
        end
      else
        h._fountainSecs = 0
      end
    else
      h._stickAlive = false
      h._stickX, h._stickY, h._stickT = h.x, h.y, world.time
      h._respawnGraceUntil = world.time + 15
      h._fountainSecs = 0
    end
  end
  if opts.trace ~= nil then
    local disp = require("bots/mode_dispatcher")
    local cur = nil
    local ui = 1
    while true do
      local name, val = debug.getupvalue(disp.Think, ui)
      if name == nil then break end
      if name == "_currentMode" then cur = val end
      ui = ui + 1
    end
    for _, f in ipairs(perBot) do
      if f.key == opts.trace then
        local h = f.hero
        local mode = (cur ~= nil and cur["npc_dota_hero_" .. f.key]) or "?"
        local at = h.attackTarget
        local atInfo = "-"
        if at ~= nil then
          atInfo = (at.kind or "?") .. "@" .. math.floor(at.x) .. "," .. math.floor(at.y)
            .. " d=" .. math.floor(Sim.dist(h.x, h.y, at.x, at.y))
            .. " alive=" .. tostring(at.alive)
        end
        local order = "none"
        if h.attackTarget ~= nil then order = "attack"
        elseif h.attackMoveTarget ~= nil then order = "attackmove"
        elseif h.followUnit ~= nil then order = "follow"
        elseif h.moveTarget ~= nil then order = "move:" .. math.floor(h.moveTarget.x) .. "," .. math.floor(h.moveTarget.y) end
        print(string.format("[trace t=%d %s pos=(%d,%d) hp=%.0f mode=%s order=%s target=%s]",
          tick, f.key, math.floor(h.x), math.floor(h.y), 100 * h.hp / h.maxHp, mode, order, atInfo))
        break
      end
    end
  end
  if opts.debug and tick % math.floor(15 / opts.tick) == 0 then
    local Perception = require("bots/engine/perception")
    local bb = _G.DOTA_AI_BLACKBOARD
    print(string.format("[debug t=%s plan=%s]", string.format("%02d:%02d", math.floor(world.time / 60), math.floor(world.time % 60)), bb ~= nil and bb.plan or "?"))
    for _, f in ipairs(perBot) do
      local h = f.hero
      Valve.setCurrentBot(f.bot)
      local snap = Perception.Snapshot(f.bot)
      Perception.Invalidate(f.bot)
      local order = "none"
      if h.attackTarget ~= nil then order = "attack:" .. (h.attackTarget.kind or "?")
      elseif h.attackMoveTarget ~= nil then order = "attackmove"
      elseif h.followUnit ~= nil then order = "follow:" .. (h.followUnit.kind or "?")
      elseif h.moveTarget ~= nil then order = "move:" .. math.floor(h.moveTarget.x) .. "," .. math.floor(h.moveTarget.y) end
      print(string.format("  %-15s %-7s pos=(%d,%d) hp=%.0f%% lvl=%d gold=%d snap: E=%d A=%d eC=%d aC=%d eT=%d aT=%d nearE=%s order=%s",
        f.key, h.team == 2 and "Radiant" or "Dire", math.floor(h.x), math.floor(h.y),
        100 * h.hp / h.maxHp, h.level, math.floor(h.gold),
        snap ~= nil and snap.numEnemies or -1, snap ~= nil and snap.numAllies or -1,
        snap ~= nil and #snap.nearbyEnemyCreeps or -1, snap ~= nil and #snap.nearbyAllyCreeps or -1,
        snap ~= nil and #snap.nearbyEnemyTowers or -1, snap ~= nil and #snap.nearbyAllyTowers or -1,
        snap ~= nil and snap.nearestEnemy ~= nil and string.format("%.0f", snap.nearestEnemyDist) or "-",
        order))
    end
    Valve.setCurrentBot(nil)
  end
  if tick % math.floor(300 / opts.tick) == 0 then
    print(string.format("t=%02d:%02d kills %d:%d towers %d:%d heroes alive %d creeps %d",
      math.floor(world.time / 60), math.floor(world.time % 60),
      world.teamKills[2], world.teamKills[3],
      world.teamTowers[2], world.teamTowers[3],
      (function()
        local n = 0
        for _, h in ipairs(world.heroes) do if h.alive then n = n + 1 end end
        return n
      end)(), #world.creeps))
  end
end

local wallSecs = os.clock() - wallStart

-- ---- 统计与 gate ----
local totalKills = world.teamKills[2] + world.teamKills[3]
local totalTowers = world.teamTowers[2] + world.teamTowers[3]
local stuckList = {}
local fountainList = {}
local inactiveBots = {}
for _, h in ipairs(world.heroes) do
  if h.stuck ~= nil then stuckList[#stuckList + 1] = h end
  if h.fountainCamp ~= nil then fountainList[#fountainList + 1] = h end
  local s = h.stats
  if s.moves == 0 or s.attacksLanded == 0 or s.buys == 0 or s.levels == 0 then
    inactiveBots[#inactiveBots + 1] = h
  end
end
local multiFights = 0
for _, f in ipairs(world.teamfights) do
  if #f.parts >= 2 then multiFights = multiFights + 1 end
end
local maxPart = 0
for _, f in ipairs(world.teamfights) do
  if #f.parts > maxPart then maxPart = #f.parts end
end

local gates = {}
local function gate(name, ok, detail)
  gates[#gates + 1] = { name = name, ok = ok, detail = detail or "" }
end
gate("no Lua errors", #errors == 0, #errors .. " errors")
gate("winner decided", world.winner ~= nil,
  world.winner == nil and "none" or (world.winner == 0 and "draw" or (world.winner == 2 and "Radiant" or "Dire")))
gate("kills > 0", totalKills > 0, "kills=" .. totalKills)
gate("towers fallen > 0", totalTowers > 0, "towers=" .. totalTowers)
gate("every bot moved/attacked/bought/leveled", #inactiveBots == 0,
  #inactiveBots .. " inactive")
gate("no bot stuck 60s+", #stuckList == 0, #stuckList .. " stuck")
gate("no fountain camping 120s+", #fountainList == 0, #fountainList .. " camping")
gate("roshan plan triggered >= 1", planRoshanTicks > 0 or world.teamRoshan[2] + world.teamRoshan[3] > 0,
  "plan ticks=" .. planRoshanTicks .. " kills=" .. (world.teamRoshan[2] + world.teamRoshan[3]))
gate("teamfight with 2+ participants", multiFights > 0,
  "fights=" .. #world.teamfights .. " multi=" .. multiFights)

local allPass = true
for _, g in ipairs(gates) do
  if not g.ok then allPass = false end
end

-- ---- 报告 ----
local function fmtTime(t)
  return string.format("%02d:%02d", math.floor(t / 60), math.floor(t % 60))
end
local lines = {}
local function add(s) lines[#lines + 1] = s end
add("# Integration Run Report (v3.1.0)")
add("")
add("## Config")
add("")
add("- duration: " .. opts.minutes .. " min, tick: " .. opts.tick .. "s, seed: " .. opts.seed .. ", difficulty: " .. opts.difficulty)
add("- radiant: " .. table.concat(radiantKeys, ", "))
add("- dire: " .. table.concat(direKeys, ", "))
add("- wall time: " .. string.format("%.1f", wallSecs) .. "s, ticks run: " .. math.floor(world.time / opts.tick))
add("- result: " .. (world.winner == nil and "NO WINNER" or (world.winner == 0 and "DRAW (time)" or (world.winner == 2 and "Radiant wins" or "Dire wins")))
  .. " (" .. (world.endReason or "?") .. ", game time " .. fmtTime(world.time) .. ")")
add("- aborted: " .. (aborted or "no"))
add("")
add("## Gates: " .. (allPass and "PASS" or "FAIL"))
add("")
add("| gate | result | detail |")
add("|---|---|---|")
for _, g in ipairs(gates) do
  add("| " .. g.name .. " | " .. (g.ok and "PASS" or "FAIL") .. " | " .. g.detail .. " |")
end
add("")
add("## Team totals")
add("")
add("| team | kills | towers taken | roshan kills |")
add("|---|---|---|---|")
add("| Radiant | " .. world.teamKills[2] .. " | " .. world.teamTowers[2] .. " | " .. world.teamRoshan[2] .. " |")
add("| Dire | " .. world.teamKills[3] .. " | " .. world.teamTowers[3] .. " | " .. world.teamRoshan[3] .. " |")
add("")
add("teamfights (kill events): " .. #world.teamfights .. ", with 2+ participants: " .. multiFights .. ", max participants in one fight: " .. maxPart)
add("roshan plan (TeamThink) ticks: " .. planRoshanTicks .. (firstRoshanPlanAt ~= nil and (", first at " .. fmtTime(firstRoshanPlanAt)) or ""))
add("")
add("## Per-bot actions")
add("")
add("| hero | team | lvl | K/D/A | LH/D | gold earned | spent | moves | dist | attack orders | hits landed | casts | buys | abilities leveled | fights joined | stuck |")
add("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for _, h in ipairs(world.heroes) do
  local s = h.stats
  add("| " .. h.key .. " | " .. (h.team == 2 and "Radiant" or "Dire") .. " | " .. h.level
    .. " | " .. s.kills .. "/" .. s.deaths .. "/" .. s.assists
    .. " | " .. s.lasthits .. "/" .. s.denies
    .. " | " .. math.floor(h.goldEarned) .. " | " .. math.floor(h.goldSpent)
    .. " | " .. s.moves .. " | " .. math.floor(h.distance)
    .. " | " .. s.attackOrders .. " | " .. s.attacksLanded
    .. " | " .. s.casts .. " | " .. s.buys .. " | " .. (h.stats.abilitiesLeveled or 0)
    .. " | " .. s.fightsJoined .. "/" .. #world.teamfights
    .. " | " .. (h.stuck ~= nil and ("YES @" .. fmtTime(h.stuck.at)) or "no") .. " |")
end
add("")
add("## Stuck / fountain-camp list")
add("")
if #stuckList == 0 and #fountainList == 0 then
  add("none")
else
  for _, h in ipairs(stuckList) do
    add("- STUCK: " .. h.key .. " at " .. fmtTime(h.stuck.at) .. " (" .. math.floor(h.stuck.x) .. "," .. math.floor(h.stuck.y) .. ", moved " .. string.format("%.0f", h.stuck.moved) .. " in 60s)")
  end
  for _, h in ipairs(fountainList) do
    add("- FOUNTAIN CAMP: " .. h.key .. " at " .. fmtTime(h.fountainCamp.at))
  end
end
add("")
add("## Errors (" .. #errors .. ")")
add("")
if #errors == 0 then
  add("none")
else
  for i, e in ipairs(errors) do
    if i > 50 then break end
    add("- tick " .. e.tick .. " t=" .. fmtTime(e.time) .. " bot=" .. e.bot .. " phase=" .. e.phase .. ": " .. e.err)
  end
end
add("")
add("## Roshan / tower events (last 40)")
add("")
local evs = world.events
local startEv = #evs - 39
if startEv < 1 then startEv = 1 end
for i = startEv, #evs do
  add("- " .. fmtTime(evs[i].time) .. " " .. evs[i].text)
end
add("")
add("## Notes")
add("")
add("- This is a SIMULATION result, not a real Dota 2 match result. See tools/integration/README.md for the known simplifications.")
add("- Unknown item costs defaulted to 500 (should be none): " .. (function()
  local n = 0
  for _ in pairs(Valve.unknownItems) do n = n + 1 end
  return tostring(n)
end)())
for name in pairs(Valve.unknownItems) do add("  - " .. name) end

local report = table.concat(lines, "\n") .. "\n"
local f = io.open(opts.out, "w")
if f ~= nil then
  f:write(report)
  f:close()
  print("report written: " .. opts.out)
else
  print("WARNING: could not write report to " .. opts.out)
end
-- ---- 结构化 stats (hero_tests.lua 用 dofile 加载, 供逐英雄门控判定) ----
if opts.statsOut ~= nil then
  local function q(s) return string.format("%q", tostring(s)) end
  local sb = {}
  sb[#sb + 1] = "return {\n"
  sb[#sb + 1] = "  minutes = " .. opts.minutes .. ", tick = " .. opts.tick .. ", seed = " .. opts.seed
    .. ", difficulty = " .. opts.difficulty .. ",\n"
  sb[#sb + 1] = "  radiant = " .. q(table.concat(radiantKeys, ",")) .. ", dire = " .. q(table.concat(direKeys, ",")) .. ",\n"
  sb[#sb + 1] = "  wallSecs = " .. string.format("%.2f", wallSecs) .. ", gameTime = " .. string.format("%.1f", world.time)
    .. ", winner = " .. tostring(world.winner) .. ", endReason = " .. q(world.endReason or "") .. ",\n"
  sb[#sb + 1] = "  totalKills = " .. totalKills .. ", totalTowers = " .. totalTowers
    .. ", planRoshanTicks = " .. planRoshanTicks .. ", teamfights = " .. #world.teamfights .. ",\n"
  sb[#sb + 1] = "  errors = {\n"
  for _, e in ipairs(errors) do
    sb[#sb + 1] = "    { tick = " .. e.tick .. ", time = " .. string.format("%.1f", e.time)
      .. ", bot = " .. q(e.bot) .. ", phase = " .. q(e.phase) .. ", err = " .. q(e.err) .. " },\n"
  end
  sb[#sb + 1] = "  },\n"
  sb[#sb + 1] = "  heroes = {\n"
  for _, h in ipairs(world.heroes) do
    local s = h.stats
    sb[#sb + 1] = "    { key = " .. q(h.key) .. ", team = " .. h.team .. ", level = " .. h.level
      .. ", kills = " .. s.kills .. ", deaths = " .. s.deaths .. ", assists = " .. s.assists
      .. ", lasthits = " .. s.lasthits .. ", denies = " .. s.denies
      .. ", goldEarned = " .. math.floor(h.goldEarned) .. ", goldSpent = " .. math.floor(h.goldSpent)
      .. ", moves = " .. s.moves .. ", distance = " .. math.floor(h.distance)
      .. ", attackOrders = " .. s.attackOrders .. ", attacksLanded = " .. s.attacksLanded
      .. ", casts = " .. s.casts .. ", buys = " .. s.buys
      .. ", abilitiesLeveled = " .. (s.abilitiesLeveled or 0) .. ", fightsJoined = " .. s.fightsJoined
      .. ", wards = " .. s.wards .. ", roshanKills = " .. s.roshanKills
      .. ", stuck = " .. tostring(h.stuck ~= nil) .. ", stuckAt = " .. (h.stuck ~= nil and string.format("%.1f", h.stuck.at) or "nil")
      .. ", fountainCamp = " .. tostring(h.fountainCamp ~= nil)
      .. ", lastActionAt = " .. string.format("%.1f", h.lastActionAt or 0) .. " },\n"
  end
  sb[#sb + 1] = "  },\n"
  sb[#sb + 1] = "}\n"
  local sf = io.open(opts.statsOut, "w")
  if sf ~= nil then
    sf:write(table.concat(sb))
    sf:close()
    print("stats written: " .. opts.statsOut)
  else
    print("WARNING: could not write stats to " .. opts.statsOut)
  end
end
print("")
print(report)
if allPass then
  print("INTEGRATION PASS")
  os.exit(0)
else
  print("INTEGRATION FAIL")
  os.exit(1)
end
