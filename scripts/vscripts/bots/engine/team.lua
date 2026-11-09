-- team.lua
-- 团队黑板:5 个 Bot 共用一张全局表,互相写意图,不靠聊天轮盘。
-- 黑板只存“意图 + 时间戳”,过期意图自动失效,避免死锁。
-- v1.1.0 新增:连招窗口 ComboWindow、集火目标 FocusTarget。
local Team = {}

-- 全局黑板,同一局内所有 Bot 共享。
if _G.DOTA_AI_BLACKBOARD == nil then
  _G.DOTA_AI_BLACKBOARD = {
    plan = "farm",
    deadEnemies = 0,
    intent = {},
    lanes = {},
    roshanCalled = 0,
    comboWindow = nil, -- { loc={x,y,z}, time=秒, caster=英雄名 } 或 nil
    focusTarget = nil, -- { unit=敌方单位, hpPct=0-1, time=秒 } 或 nil
    focusUnit = nil,
  }
end

function Team.GetBlackboard()
  return _G.DOTA_AI_BLACKBOARD
end

-- 测试用:重置黑板(游戏内不调用,verify_v110 用它隔离各测试)。
function Team.ResetBlackboard()
  _G.DOTA_AI_BLACKBOARD = {
    plan = "farm",
    deadEnemies = 0,
    intent = {},
    lanes = {},
    roshanCalled = 0,
    comboWindow = nil,
    focusTarget = nil,
    focusUnit = nil,
  }
  return _G.DOTA_AI_BLACKBOARD
end

local function gameTime()
  if DotaTime ~= nil then
    local ok, t = pcall(DotaTime)
    if ok and type(t) == "number" then return t end
  end
  return 0
end

-- 上报意图:intent 如 "push_mid" / "roshan" / "defend" / "farm"。
function Team.ReportIntent(bot, intent)
  local bb = Team.GetBlackboard()
  if bot == nil or intent == nil then return end
  local name = ""
  local ok, n = pcall(function() return bot:GetUnitName() end)
  if ok then name = n or "" end
  bb.intent[name] = { intent = intent, time = gameTime() }
end

-- 统计当前有多少队友在做同一意图(60s 内有效)。
function Team.CountIntent(intent)
  local bb = Team.GetBlackboard()
  local t = gameTime()
  local n = 0
  for _, v in pairs(bb.intent or {}) do
    if v.intent == intent and (t - (v.time or 0)) < 60 then
      n = n + 1
    end
  end
  return n
end

-- 角色 / 分路分配:按 heroes.lua 的 positions 排序,1 号位先占安全线,
-- 5 号位跟 1 号位,4 号位游走,3 号位优势路,2 号位中路。
-- 分配结果写进黑板,避免 5 个人挤一条线。
function Team.AssignLane(bot, heroData, teamMembers)
  local bb = Team.GetBlackboard()
  if bot == nil or heroData == nil then return "mid" end
  local pos = 5
  if heroData.positions ~= nil and heroData.positions[1] ~= nil then
    pos = heroData.positions[1]
  end
  local lane = heroData.lane or "mid"
  -- 位置决定分路,数据表里已写明;这里只做冲突去重:
  -- 如果同分路已分配给更高优先级的队友,低优先级去野区/游走。
  local key = lane .. "_" .. tostring(pos)
  local name = ""
  local ok, n = pcall(function() return bot:GetUnitName() end)
  if ok then name = n or "" end
  if bb.lanes[key] == nil or bb.lanes[key] == name then
    bb.lanes[key] = name
    return lane
  end
  if pos == 4 or pos == 5 then return "roam" end
  return lane
end

-- 更新敌方阵亡数:由每个 Bot 的快照汇总,供 macro 打盾判断用。
-- 这里用最近快照的敌方可见数做保守估计,不假设全图视野。
-- v1.1.0:Core.Think 每帧都调它,之前是死代码。
function Team.UpdateDeadEnemies(visibleEnemies, totalEnemyHeroes)
  local bb = Team.GetBlackboard()
  totalEnemyHeroes = totalEnemyHeroes or 5
  visibleEnemies = visibleEnemies or 0
  -- 可见敌方越少,推测减员越多,但上限 2,避免过度乐观去打盾。
  local est = totalEnemyHeroes - visibleEnemies
  if est < 0 then est = 0 end
  if est > 2 then est = 2 end
  bb.deadEnemies = est
  return est
end

-- ---- v1.1.0:连招窗口 ComboWindow ----
-- 任一 Bot 放出大型先手/控制大招时调用,把位置+时间+释放者写进黑板。
-- 窗口有效期 5 秒;5 秒内队友走向该位置参团、优先放 AoE 跟进。
Team.COMBO_WINDOW_SECONDS = 5
Team.COMBO_HOLD_SECONDS = 2 -- 窗口开启后 2 秒内,别人不重复放同类先手大

function Team.ReportComboWindow(bot, loc)
  local bb = Team.GetBlackboard()
  if bot == nil or loc == nil then return false end
  local name = ""
  local ok, n = pcall(function() return bot:GetUnitName() end)
  if ok then name = n or "" end
  bb.comboWindow = { loc = loc, time = gameTime(), caster = name }
  return true
end

function Team.GetComboWindow()
  local bb = Team.GetBlackboard()
  local w = bb.comboWindow
  if w == nil then return nil end
  if (gameTime() - (w.time or 0)) >= Team.COMBO_WINDOW_SECONDS then
    bb.comboWindow = nil
    return nil
  end
  return w
end

function Team.IsComboWindowActive()
  return Team.GetComboWindow() ~= nil
end

-- 该 Bot 现在放同类先手大是否该忍住:窗口由别人开启、且开启不到 2 秒。
function Team.ShouldHoldUlt(bot)
  local w = Team.GetComboWindow()
  if w == nil then return false end
  local name = ""
  if bot ~= nil then
    local ok, n = pcall(function() return bot:GetUnitName() end)
    if ok then name = n or "" end
  end
  if w.caster == name then return false end
  return (gameTime() - (w.time or 0)) < Team.COMBO_HOLD_SECONDS
end

-- ---- v1.1.0:集火目标 FocusTarget ----
-- 全队共享目标 = 所有 Bot 可见敌方里血量百分比最低的。
-- 调用方每次传最新快照就重算;不传快照时返回 10 秒内有效的旧目标。
local function unitHpPct(u)
  if u == nil then return 1 end
  local okA, alive = pcall(function() return u:IsAlive() end)
  if okA and not alive then return 1 end
  local hp, maxHp = 0, 1
  local ok1, v1 = pcall(function() return u:GetHealth() end)
  if ok1 then hp = v1 or 0 end
  local ok2, v2 = pcall(function() return u:GetMaxHealth() end)
  if ok2 then maxHp = v2 or 1 end
  return hp / math.max(1, maxHp)
end

function Team.UpdateFocusTarget(snap)
  local bb = Team.GetBlackboard()
  if snap == nil or snap.nearbyEnemies == nil then return bb.focusUnit end
  local best, bestPct = nil, 1
  for _, e in ipairs(snap.nearbyEnemies) do
    if e ~= nil then
      local pct = unitHpPct(e)
      -- 只选活着的(血量>0);pct==1 且满血也参与比较,由最低者胜出。
      local okA, alive = pcall(function() return e:IsAlive() end)
      if (not okA) or alive then
        if pct < bestPct or best == nil then
          best, bestPct = e, pct
        end
      end
    end
  end
  if best ~= nil then
    bb.focusUnit = best
    bb.focusTarget = { unit = best, hpPct = bestPct, time = gameTime() }
  end
  return bb.focusUnit
end

function Team.GetFocusTarget(snap)
  if snap ~= nil then return Team.UpdateFocusTarget(snap) end
  local bb = Team.GetBlackboard()
  if bb.focusUnit == nil then return nil end
  if (gameTime() - ((bb.focusTarget or {}).time or 0)) > 10 then
    bb.focusUnit, bb.focusTarget = nil, nil
    return nil
  end
  return bb.focusUnit
end


-- ---- v2.0.0: Team 层战略 (TeamThink) ----
-- 每帧先跑一次 (team_think.lua 的 TeamThink() 调这里), 定全队战略并写进黑板,
-- 供各 Mode 读。不要让每个 Bot 各自猜全队意图。
-- 规则: 敌方减员>=2 且 20 分钟后 -> roshan; 敌方减员>=1 且我方占优 -> push;
-- 连招窗口有效 -> teamfight; 否则 farm。返回 plan 名。
function Team.TeamThink(bot, snap, bb)
  bb = bb or Team.GetBlackboard()
  if snap ~= nil then
    Team.UpdateDeadEnemies(snap.numEnemies or 0, 5)
  end
  local w = Team.GetComboWindow()
  if w ~= nil then
    bb.plan = "teamfight"
    return "teamfight"
  end
  local t = 0
  if DotaTime ~= nil then
    local ok, v = pcall(DotaTime)
    if ok and type(v) == "number" then t = v end
  end
  if snap ~= nil then t = snap.time or t end
  local dead = bb.deadEnemies or 0
  local nA = 0
  if snap ~= nil then nA = snap.numAllies or 0 end
  if t > 1200 and dead >= 2 and (nA + 1) >= 3 then
    bb.plan = "roshan"
    bb.roshanCalled = t
    return "roshan"
  end
  if dead >= 1 and (nA + 1) >= 3 then
    bb.plan = "push"
    return "push"
  end
  bb.plan = "farm"
  return "farm"
end

return Team
