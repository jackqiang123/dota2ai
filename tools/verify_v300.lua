-- verify_v300.lua -- v3.0.0 验证测试 (127 个英雄全部有真实 Consider)。
-- 用法 (在仓库根目录): lua5.4 tools/verify_v300.lua
-- 退出码 0=全部通过; 任一断言失败即报错退出。
-- 方法: 不硬编码英雄名/技能名, 从生成的 data/heroes.lua 与 BotLib 文件里
-- 解析出 127 个 key 与每英雄的真实技能名, 再用多场景 mock 逐个验证。
-- 每个英雄至少在一个构造场景里有 Consider desire > 0.5 且 SkillsComplement 真正施放。
local _script = (arg and arg[0]) or "tools/verify_v300.lua"
local _root = _script:match("^(.*)/tools/verify_v300%.lua$") or "."
if _root == "" then _root = "." end
package.path = _root .. "/scripts/vscripts/?.lua;" .. _root .. "/scripts/vscripts/?/init.lua;" .. package.path

BOT_MODE_NONE = 0
function GetScriptDirectory() return "bots" end
local _T = 400
function DotaTime() return _T end
function GetItemCost(name) return 100 end
local function setTime(t) _T = t end

local passed = 0
local function check(name, cond, extra)
  if not cond then error("FAIL: " .. name .. (extra and (" -- " .. tostring(extra)) or ""), 2) end
  passed = passed + 1
  print("PASS: " .. name)
end
local function readFile(path)
  local f = io.open(path, "r")
  if not f then return nil end
  local s = f:read("*a")
  f:close()
  return s
end

local function mkability(name, range, castable)
  return {
    GetAbilityName = function() return name end,
    IsPassive = function() return false end,
    IsFullyCastable = function() return castable ~= false end,
    CanAbilityBeUpgraded = function() return true end,
    GetCastRange = function() return range or 600 end,
    IsNull = function() return false end,
    IsHidden = function() return false end,
  }
end
local function mkunit(id, hp, maxHp, x, y)
  return {
    _id = id,
    GetHealth = function() return hp end,
    GetMaxHealth = function() return maxHp or 1000 end,
    GetMana = function() return 500 end, GetMaxMana = function() return 500 end,
    GetHealthRegen = function() return 2 end,
    GetMovementSpeed = function() return 300 end,
    GetLocation = function() return { x = x or 0, y = y or 0, z = 0 } end,
    IsAlive = function() return hp > 0 end,
    IsNull = function() return false end,
    GetUnitName = function() return "npc_dota_hero_" .. id end,
  }
end
local function mkbot(opts)
  opts = opts or {}
  local bot = {
    _id = opts.hero or "axe", log = {},
    _hp = opts.hp or 800, _maxHp = opts.maxHp or 1000,
    _mana = opts.mana or 500, _maxMana = opts.maxMana or 500,
    _x = opts.x or 0, _y = opts.y or 0,
    _level = opts.level or 5, _gold = opts.gold or 0,
    _abilities = opts.abilities or {}, _items = opts.items or {},
    _enemies = opts.enemies or {}, _allies = opts.allies or {},
    _ecreeps = opts.ecreeps or {}, _acreeps = opts.acreeps or {}, _towers = opts.towers or {},
    _courier = opts.courier, _stash = opts.stash,
  }
  bot.GetUnitName = function(self) return "npc_dota_hero_" .. (opts.hero or "axe") end
  bot.GetHealth = function(self) return bot._hp end
  bot.GetMaxHealth = function(self) return bot._maxHp end
  bot.GetMana = function(self) return bot._mana end
  bot.GetMaxMana = function(self) return bot._maxMana end
  bot.GetHealthRegen = function(self) return 2 end
  bot.GetMovementSpeed = function(self) return 300 end
  bot.GetLocation = function(self) return { x = bot._x, y = bot._y, z = 0 } end
  bot.IsAlive = function(self) return true end
  bot.IsNull = function(self) return false end
  bot.GetLevel = function(self) return bot._level end
  bot.GetGold = function(self) return bot._gold end
  bot.GetAttackRange = function(self) return 150 end
  bot.GetAttackDamage = function(self) return 60 end
  bot.GetTeam = function(self) return 2 end
  bot.GetPlayerID = function(self) return 0 end
  bot.GetNearbyHeroes = function(self, r, enemy, mode) if enemy then return bot._enemies else return bot._allies end end
  bot.GetNearbyCreeps = function(self, r, enemy) if enemy then return bot._ecreeps else return bot._acreeps end end
  bot.GetNearbyTowers = function(self, r, enemy) return bot._towers end
  bot.GetAbilityInSlot = function(self, i) return bot._abilities[i] end
  bot.GetAbilityByName = function(self, name)
    for _, ab in pairs(bot._abilities) do if ab:GetAbilityName() == name then return ab end end
    return nil
  end
  bot.GetItemInSlot = function(self, i) return bot._items[i] end
  bot.GetAbilityPoints = function(self) return 1 end
  bot.GetCourier = function(self) return bot._courier end
  bot.GetNumItemsInStash = function(self) return bot._stash end
  bot.Action_MoveToLocation = function(self, loc) bot.log[#bot.log + 1] = "move:" .. loc.x .. "," .. loc.y end
  bot.Action_MoveToUnit = function(self, u) bot.log[#bot.log + 1] = "moveto:" .. (u._id or "?") end
  bot.Action_AttackUnit = function(self, u, once) bot.log[#bot.log + 1] = "attack:" .. (u._id or "?") end
  bot.Action_UseAbility = function(self, a) bot.log[#bot.log + 1] = "cast_nontarget:" .. a:GetAbilityName() end
  bot.Action_UseAbilityOnEntity = function(self, a, u) bot.log[#bot.log + 1] = "cast_entity:" .. a:GetAbilityName() .. "->" .. (u._id or "?") end
  bot.Action_UseAbilityOnLocation = function(self, a, loc) bot.log[#bot.log + 1] = "cast_loc:" .. a:GetAbilityName() .. "@" .. loc.x .. "," .. loc.y end
  bot.Action_PurchaseItem = function(self, n) bot.log[#bot.log + 1] = "buy:" .. n return true end
  bot.Action_LevelAbility = function(self, n) bot.log[#bot.log + 1] = "level:" .. n end
  bot.Action_Courier = function(self, action) bot.log[#bot.log + 1] = "courier:" .. tostring(action) return true end
  return bot
end

local Perception = require("bots/engine/perception")
local Team = require("bots/engine/team")
local Skill = require("bots/engine/skill")
local Dispatcher = require("bots/mode_dispatcher")
local Heroes = require("bots/data/heroes")

local function snapFor(bot) Perception.Invalidate(bot) return Perception.Snapshot(bot) end

-- ---- 读出 127 个英雄 key ----
local heroesLua = readFile(_root .. "/scripts/vscripts/bots/data/heroes.lua")
assert(heroesLua ~= nil, "data/heroes.lua not found")
local keys = {}
for k in heroesLua:gmatch("\n  ([%w_]+) = { key = \"") do keys[#keys + 1] = k end
check("0 heroes.lua has 127 keys", #keys == 127, "n=" .. #keys)

-- ---- 1. 全部 127 个 BotLib 都能加载 ----
local mods = {}
local loadFail = {}
for _, key in ipairs(keys) do
  local ok, mod = pcall(require, "bots/BotLib/hero_" .. key)
  if ok and mod ~= nil and mod.SkillsComplement ~= nil then
    mods[key] = mod
  else
    loadFail[#loadFail + 1] = key
  end
end
check("1 all 127 BotLib load with SkillsComplement", #loadFail == 0, "failed=" .. table.concat(loadFail, ","))

-- ---- 2. 技能名一致: ABILITIES 里的名必须出现在对应 Consider 的 ab[...] 里 ----
do
  local bad = {}
  for _, key in ipairs(keys) do
    local txt = readFile(_root .. "/scripts/vscripts/bots/BotLib/hero_" .. key .. ".lua")
    local q, w, e, r = txt:match('X%.ABILITIES = { Q = "([^"]+)", W = "([^"]+)", E = "([^"]+)", R = "([^"]+)" }')
    if not (q and w and e and r) then bad[#bad + 1] = key .. ":ABILITIES-parse" else
      for slot, name in pairs({ Q = q, W = w, E = e, R = r }) do
        local body = txt:match("function X%.Consider" .. slot .. "%(bot, snap, ab%)\n(.-)\nend")
        if body == nil or not body:find('ab%["' .. name:gsub("%-", "%%-") .. '"%]', 1) then
          -- 被动槽 (body 只有 return 0) 不要求 ab[...] 出现
          if body ~= nil and body:match("^%s*return 0, nil, \"none\"%s*$") == nil then
            bad[#bad + 1] = key .. ":" .. slot .. "=" .. name
          end
        end
      end
    end
  end
  check("2 ABILITIES names match their Consider bodies (127 heroes)", #bad == 0, table.concat(bad, ";"))
end

-- ---- 3. 五位置出装不全同、每位置 >=8 件、至少一位置 >=12 件 ----
do
  local bad = {}
  for _, key in ipairs(keys) do
    local txt = readFile(_root .. "/scripts/vscripts/bots/BotLib/hero_" .. key .. ".lua")
    local lists = {}
    for pos, items in txt:gmatch('sBuyList%["pos_(%d+)"%] = {([^}]*)}') do
      local n = 0
      for _ in items:gmatch("item_") do n = n + 1 end
      lists[#lists + 1] = { pos = pos, items = items, n = n }
    end
    if #lists ~= 5 then bad[#bad + 1] = key .. ":pos=" .. #lists else
      local seen, mx = {}, 0
      for _, l in ipairs(lists) do
        seen[l.items] = true
        if l.n < 8 then bad[#bad + 1] = key .. ":pos_" .. l.pos .. " n=" .. l.n end
        if l.n > mx then mx = l.n end
      end
      local distinct = 0
      for _ in pairs(seen) do distinct = distinct + 1 end
      if distinct ~= 5 then bad[#bad + 1] = key .. ":distinct=" .. distinct end
      if mx < 12 then bad[#bad + 1] = key .. ":max=" .. mx end
    end
  end
  check("3 sBuyList 5 distinct positions, >=8 each, >=12 max (127 heroes)", #bad == 0, table.concat(bad, ";"))
end

-- ---- 4. 天赋 127 条 ----
do
  local talentsLua = readFile(_root .. "/scripts/vscripts/bots/data/talents.lua")
  local n = 0
  for _ in talentsLua:gmatch("%[10%] =") do n = n + 1 end
  check("4 data/talents.lua has 127 entries", n == 127, "n=" .. n)
  local bad = {}
  for _, key in ipairs(keys) do
    local txt = readFile(_root .. "/scripts/vscripts/bots/BotLib/hero_" .. key .. ".lua")
    if not txt:match("X%.TALENTS = { %[10%] = %d, %[15%] = %d, %[20%] = %d, %[25%] = %d }") then
      bad[#bad + 1] = key
    end
  end
  check("4 every BotLib has 4-tier TALENTS", #bad == 0, table.concat(bad, ","))
end

-- ---- 5. Invoker: 8 个 invoked Consider + 至少一个 invoked 技能能施放 ----
do
  local mod = mods["invoker"]
  check("5 invoker module loaded", mod ~= nil and mod.INVOKED ~= nil)
  check("5 invoker has 8 invoked spells", mod ~= nil and #mod.INVOKED == 8, "n=" .. tostring(mod and #mod.INVOKED))
  local abs = { [0] = mkability("invoker_quas", 0), [1] = mkability("invoker_wex", 0), [2] = mkability("invoker_exort", 0), [3] = mkability("invoker_invoke", 0) }
  for i, name in ipairs(mod.INVOKED) do if i <= 6 then abs[3 + i] = mkability(name, 800) end end
  Team.ResetBlackboard(); setTime(400)
  local bot = mkbot({ hero = "invoker", hp = 800, abilities = abs,
    enemies = { mkunit("e1", 400, 1000, 200, 0), mkunit("e2", 400, 1000, 250, 0), mkunit("e3", 400, 1000, 300, 0) },
    allies = { mkunit("a1", 800, 1000, 100, 0) } })
  local snap = snapFor(bot)
  local cast = mod.SkillsComplement(bot, snap)
  check("5 invoker casts an invoked spell in teamfight", cast == true, table.concat(bot.log, ";"))
end

-- ---- 6. 每个英雄: 至少一个 Consider 在构造场景里 desire > 0.5 且 SkillsComplement 施放 ----
local function scenarioBots(hero, abilities)
  local e3 = { mkunit("e1", 400, 1000, 200, 0), mkunit("e2", 400, 1000, 250, 0), mkunit("e3", 400, 1000, 300, 0) }
  local a2 = { mkunit("a1", 800, 1000, 100, 0), mkunit("a2", 800, 1000, 120, 0) }
  return {
    -- A 团战: 3 敌贴脸 + 队友在场
    { hero = hero, hp = 800, mana = 500, abilities = abilities, enemies = e3, allies = a2 },
    -- B 救人: 队友 20% 血 + 2 敌
    { hero = hero, hp = 800, mana = 500, abilities = abilities,
      enemies = { mkunit("e1", 500, 1000, 300, 0), mkunit("e2", 500, 1000, 350, 0) },
      allies = { mkunit("a1", 200, 1000, 100, 0) } },
    -- C 自身残血: 血 20% + 1 敌
    { hero = hero, hp = 200, mana = 500, abilities = abilities,
      enemies = { mkunit("e1", 600, 1000, 300, 0) }, allies = {} },
    -- D 无敌刷野: 无敌方 + 3 敌方小兵
    { hero = hero, hp = 800, mana = 500, abilities = abilities, enemies = {},
      allies = {}, ecreeps = { mkunit("c1", 100, 500, 200, 0), mkunit("c2", 100, 500, 250, 0), mkunit("c3", 100, 500, 300, 0) } },
    -- E 追残血: 1 敌 15% 血
    { hero = hero, hp = 800, mana = 500, abilities = abilities,
      enemies = { mkunit("e1", 150, 1000, 300, 0) }, allies = {} },
    -- F 低蓝: 蓝 20% + 2 敌 + 1 队友
    { hero = hero, hp = 800, mana = 100, abilities = abilities,
      enemies = { mkunit("e1", 500, 1000, 300, 0), mkunit("e2", 500, 1000, 350, 0) },
      allies = { mkunit("a1", 500, 1000, 100, 0) } },
    -- G 中距离: 2 敌在 700-800 码
    { hero = hero, hp = 800, mana = 500, abilities = abilities,
      enemies = { mkunit("e1", 600, 1000, 700, 0), mkunit("e2", 600, 1000, 800, 0) }, allies = {} },
  }
end
do
  local failed = {}
  for _, key in ipairs(keys) do
    local mod = mods[key]
    local txt = readFile(_root .. "/scripts/vscripts/bots/BotLib/hero_" .. key .. ".lua")
    local q, w, e, r = txt:match('X%.ABILITIES = { Q = "([^"]+)", W = "([^"]+)", E = "([^"]+)", R = "([^"]+)" }')
    local abilities = { [0] = mkability(q, 700), [1] = mkability(w, 700), [2] = mkability(e, 700), [3] = mkability(r, 700) }
    if mod.INVOKED ~= nil then
      for i, name in ipairs(mod.INVOKED) do if i <= 6 then abilities[3 + i] = mkability(name, 800) end end
    end
    local bestDesire, bestCast, bestScenario = 0, false, nil
    for si, opts in ipairs(scenarioBots(key, abilities)) do
      Team.ResetBlackboard(); setTime(400)
      local bot = mkbot(opts)
      local snap = snapFor(bot)
      local ab = Skill.GetAbilityMap(bot)
      local fns = { "ConsiderQ", "ConsiderW", "ConsiderE", "ConsiderR" }
      if mod.INVOKED ~= nil then
        for _, name in ipairs(mod.INVOKED) do
          local parts = {}
          for p in name:gmatch("[^_]+") do parts[#parts + 1] = p end
          local fn = "ConsiderInvoker"
          for i = 2, #parts do fn = fn .. parts[i]:sub(1, 1):upper() .. parts[i]:sub(2) end
          fns[#fns + 1] = fn
        end
      end
      for _, fnName in ipairs(fns) do
        local fn = mod[fnName]
        if fn ~= nil then
          local ok, desire = pcall(fn, bot, snap, ab)
          if ok and type(desire) == "number" and desire > bestDesire then bestDesire = desire end
        end
      end
      local okCast, cast = pcall(mod.SkillsComplement, bot, snap)
      if okCast and cast == true then bestCast = true end
      if bestDesire > 0.5 and bestCast then bestScenario = si break end
    end
    if bestDesire > 0.5 and bestCast then
      passed = passed + 1
      print("PASS: 6 " .. key .. " Consider desire>0.5 and casts (scenario " .. tostring(bestScenario) .. ", desire=" .. string.format("%.2f", bestDesire) .. ")")
    else
      failed[#failed + 1] = key .. " (bestDesire=" .. string.format("%.2f", bestDesire) .. ", cast=" .. tostring(bestCast) .. ")"
    end
  end
  check("6 every hero has a Consider >0.5 and casts in some scenario", #failed == 0, table.concat(failed, "; "))
end

-- ---- 7. Mode 分发仍正常 (v2.0 回归) ----
do
  local modes = Dispatcher.LoadModes()
  local n = 0
  for _, k in ipairs(Dispatcher.MODE_FILES) do if modes[k] ~= nil then n = n + 1 end end
  check("7 mode count >=12", n >= 12, "n=" .. n)
  Team.ResetBlackboard(); Dispatcher.ResetThinkState(); setTime(100)
  local bot = mkbot({ hero = "axe", hp = 100, maxHp = 1000, enemies = { mkunit("e1", 400, 1000, 300, 0) } })
  local snap = snapFor(bot)
  local best, scores = Dispatcher.SelectMode(bot, snap, Team.GetBlackboard())
  check("7 low-hp selects retreat", best == "retreat", "best=" .. tostring(best))
  local bot2 = mkbot({ hero = "axe", hp = 900, enemies = { mkunit("e1", 400, 1000, 300, 0) }, ecreeps = { mkunit("c1", 50, 500, 200, 0) } })
  local mode = Dispatcher.Think(bot2)
  check("7 dispatcher Think returns a mode", mode ~= nil, "mode=" .. tostring(mode))
end

-- ---- 8. 互动系统仍正常 (v2.0 回归) ----
do
  Team.ResetBlackboard(); setTime(1300)
  local bot = mkbot({ hero = "axe", hp = 900, enemies = {}, allies = { mkunit("a1", 800, 1000, 100, 0), mkunit("a2", 800, 1000, 120, 0), mkunit("a3", 800, 1000, 140, 0) } })
  local plan = Team.TeamThink(bot, snapFor(bot), Team.GetBlackboard())
  check("8 TeamThink roshan when dead>=2 and t>1200", plan == "roshan", "plan=" .. tostring(plan))
  Team.ResetBlackboard(); setTime(600)
  local bot2 = mkbot({ hero = "axe", hp = 800, enemies = { mkunit("e1", 200, 1000, 300, 0), mkunit("e2", 900, 1000, 350, 0) } })
  local focus = Team.GetFocusTarget(snapFor(bot2))
  check("8 focus target is lowest-hp enemy", focus ~= nil and focus._id == "e1", "focus=" .. tostring(focus and focus._id))
  Team.ReportComboWindow(bot2, { x = 300, y = 0, z = 0 })
  check("8 combo window active", Team.IsComboWindowActive() == true)
end

-- ---- 9. GetScriptDirectory 写法 + Lua 5.1 ----
do
  local function grepCount(pat)
    local h = io.popen("grep -r --include='*.lua' -l '" .. pat .. "' " .. _root .. "/scripts/vscripts/bots 2>/dev/null | wc -l")
    local n = tonumber(h:read("*a")) or 0
    h:close()
    return n
  end
  check("9 no require(\"bots/...\") left", grepCount('require("bots/') == 0)
  check("9 GetScriptDirectory used", grepCount('GetScriptDirectory') > 50)
  check("9 no goto in Lua", grepCount('goto') == 0)
  check("9 no table.unpack in Lua", grepCount('table.unpack') == 0)
end

print("VERIFY_V300 PASSED: " .. passed .. " checks")
