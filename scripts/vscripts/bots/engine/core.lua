-- core.lua
-- 引擎门面:把 perception / utility / micro / macro / team 串成一个 Think()。
-- 任何英雄的 bot_<hero>.lua 和 bot_generic.lua 都只调 Core.Think(bot)。
-- v1.1.0:thinkDelay 真正节流;每帧接通 UpdateDeadEnemies / AssignLane /
--        信使 / 插眼;团战用集火目标,连招窗口内走向窗口位置。
local Core = {}

local Perception = require("bots/engine/perception")
local Utility = require("bots/engine/utility")
local Micro = require("bots/engine/micro")
local Macro = require("bots/engine/macro")
local Team = require("bots/engine/team")
local Heroes = require("bots/data/heroes")

Core.Perception = Perception
Core.Utility = Utility
Core.Micro = Micro
Core.Macro = Macro
Core.Team = Team
Core.Heroes = Heroes

-- 每个 Bot 上次决策的时间戳(按英雄名),用于 thinkDelay 节流。
local _lastThink = {}
local _laneAssigned = {}

-- 测试用:重置节流与分路状态。
function Core.ResetThinkState()
  _lastThink = {}
  _laneAssigned = {}
end

-- npc_dota_hero_axe -> axe
function Core.HeroKeyFromUnitName(unitName)
  if unitName == nil then return nil end
  local key = string.gsub(unitName, "^npc_dota_hero_", "")
  return key
end

function Core.GetHeroData(bot)
  if bot == nil then return nil end
  local ok, name = pcall(function() return bot:GetUnitName() end)
  if not ok then return nil end
  local key = Core.HeroKeyFromUnitName(name)
  if key == nil then return nil end
  return Heroes[key], key
end

local function gameTime()
  if DotaTime ~= nil then
    local ok, t = pcall(DotaTime)
    if ok and type(t) == "number" then return t end
  end
  return 0
end

local function botKey(bot)
  local ok, name = pcall(function() return bot:GetUnitName() end)
  if ok and name ~= nil and name ~= "" then return name end
  return tostring(bot)
end

-- 主循环:感知 -> 打分 -> 微操/技能 -> 执行行为。
-- 每帧只做一件事,发完指令立即 return,避免一帧内发多个冲突指令。
function Core.Think(bot)
  if bot == nil then return end
  local okNull, isNull = pcall(function() return bot:IsNull() end)
  if okNull and isNull then return end
  local okAlive, alive = pcall(function() return bot:IsAlive() end)
  if okAlive and not alive then return end

  local heroData, heroKey = Core.GetHeroData(bot)
  local snap = Perception.Snapshot(bot)
  if snap == nil then return end
  local t = gameTime()
  local bb = Team.GetBlackboard()

  -- v1.1.0 接通死代码(每帧):
  -- (a) 敌方阵亡数:可见敌方越少,推测减员越多,供 Macro 打盾判断用。
  Team.UpdateDeadEnemies(snap.numEnemies or 0, 5)
  -- (b) 分路去重:每个 Bot 只在首次 Think 时分配一次,避免 5 人挤一条线。
  local key = botKey(bot)
  if not _laneAssigned[key] then
    Team.AssignLane(bot, heroData)
    _laneAssigned[key] = true
  end

  -- 1. 买装备:有钱先买,不占用走位/技能帧(购买不打断移动)。
  --    信使送货同样不占决策帧。
  Micro.TryBuyNextItem(bot, heroData)
  Micro.TryDeliverCourier(bot)

  -- v1.1.0 thinkDelay 节流:买装备/信使除外,决策与技能按难度间隔执行。
  -- DotaTime() 为 0(测试环境时间冻结)时不节流,避免永久卡死。
  local diff = Utility.GetDifficulty()
  if t > 0 then
    local last = _lastThink[key]
    if last ~= nil and (t - last) < (diff.thinkDelay or 0) then
      return
    end
    _lastThink[key] = t
  end

  -- 2. 保命物品先于技能。
  if Micro.TryUseItems(bot, snap) then return end

  -- 3. 技能:按类型抽象释放,命中即 return。救人优先于进攻(见 micro.lua)。
  if Micro.TryCastByType(bot, snap, heroData) then return end

  -- 4. 效用打分,选最优行为。
  local scores, best = Utility.Score(bot, snap, heroData, t)

  if best == "retreat" or best == "heal" then
    -- 撤回泉水:先走向最近的己方防御塔;无塔时直接回己方基地角落
    -- (Radiant 泉水约 (-7000,-7000),Dire 约 (7000,7000)),不再原地站着。
    local towers = snap.nearbyAllyTowers or {}
    if #towers > 0 then
      local loc = nil
      local ok, l = pcall(function() return towers[1]:GetLocation() end)
      if ok then loc = l end
      if loc ~= nil then
        pcall(function() bot:Action_MoveToLocation(loc) end)
        return
      end
    end
    local team = snap.team or 2
    local fountain = { x = -7000, y = -7000, z = 0 }
    if team == 3 then fountain = { x = 7000, y = 7000, z = 0 } end
    pcall(function() bot:Action_MoveToLocation(fountain) end)
    return
  end

  if best == "lasthit" then
    local target = Micro.FindLastHitTarget(bot, snap, diff.lasthitMargin)
    if target ~= nil then
      pcall(function() bot:Action_AttackUnit(target, false) end)
      return
    end
  end

  if best == "deny" then
    if snap.deniable ~= nil and #snap.deniable > 0 then
      pcall(function() bot:Action_AttackUnit(snap.deniable[1], false) end)
      return
    end
  end

  -- v1.1.0 插眼分支:best=="ward" 且背包有眼时插眼;没眼则落到默认行为。
  if best == "ward" then
    if Micro.TryPlaceWard(bot, snap) then return end
  end

  if best == "teamfight" then
    Team.ReportIntent(bot, "teamfight")
    -- v1.1.0 连招窗口:队友刚开先手大、且自己离窗口较远时,先走向窗口位置。
    local window = Team.GetComboWindow()
    if window ~= nil and window.loc ~= nil then
      local myName = ""
      local okN, n = pcall(function() return bot:GetUnitName() end)
      if okN then myName = n or "" end
      if window.caster ~= myName and snap.location ~= nil then
        local dx = window.loc.x - snap.location.x
        local dy = window.loc.y - snap.location.y
        if math.sqrt(dx * dx + dy * dy) > 300 then
          pcall(function() bot:Action_MoveToLocation(window.loc) end)
          return
        end
      end
    end
    -- v1.1.0 集火:优先打全队共享的最低血量目标,不是各打各的最近目标。
    local focus = Team.GetFocusTarget(snap)
    local target = focus or snap.nearestEnemy
    if target ~= nil then
      pcall(function() bot:Action_AttackUnit(target, false) end)
      return
    end
  end

  if best == "push" or best == "roshan" then
    local plan = Macro.GetPlan(bot, snap, bb)
    Team.ReportIntent(bot, plan)
    local loc = Macro.GetObjectiveLocation(bot, plan, snap)
    if loc ~= nil then
      pcall(function() bot:Action_MoveToLocation(loc) end)
      return
    end
    if snap.nearbyEnemyTowers ~= nil and #snap.nearbyEnemyTowers > 0 then
      pcall(function() bot:Action_AttackUnit(snap.nearbyEnemyTowers[1], false) end)
      return
    end
  end

  if best == "roam" then
    -- 游走:走向中路最近的敌方英雄可见点;无目标时回线。
    if snap.nearestEnemy ~= nil then
      pcall(function() bot:Action_MoveToUnit(snap.nearestEnemy) end)
      return
    end
  end

  -- 默认:刷钱 / 跟线。优先打最近的敌方小兵,其次走向己方小兵。
  if snap.nearbyEnemyCreeps ~= nil and #snap.nearbyEnemyCreeps > 0 then
    pcall(function() bot:Action_AttackUnit(snap.nearbyEnemyCreeps[1], false) end)
    return
  end
  if snap.nearbyAllyCreeps ~= nil and #snap.nearbyAllyCreeps > 0 then
    pcall(function() bot:Action_MoveToUnit(snap.nearbyAllyCreeps[1]) end)
    return
  end
end

return Core
