-- core.lua
-- 引擎门面:把 perception / utility / micro / macro / team 串成一个 Think()。
-- 任何英雄的 bot_<hero>.lua 和 bot_generic.lua 都只调 Core.Think(bot)。
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

  -- 1. 买装备:有钱先买,不占用走位/技能帧(购买不打断移动)。
  Micro.TryBuyNextItem(bot, heroData)

  -- 2. 保命物品先于技能。
  if Micro.TryUseItems(bot, snap) then return end

  -- 3. 技能:按类型抽象释放,命中即 return。
  if Micro.TryCastByType(bot, snap, heroData) then return end

  -- 4. 效用打分,选最优行为。
  local scores, best = Utility.Score(bot, snap, heroData, t)
  local diff = Utility.GetDifficulty()

  if best == "retreat" or best == "heal" then
    -- 撤回泉水:用 Action_MoveToLocation 回己方泉水(0,0 附近为地图中心,
    -- 泉水在己方基地角落,这里用 GetLocation 的反方向简化:直接回基地)。
    -- 更稳妥的做法是走向最近的己方防御塔,再回泉;此处先回塔。
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
    -- 无塔可回时原地待命,避免往敌方走。
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

  if best == "teamfight" then
    if snap.nearestEnemy ~= nil then
      Team.ReportIntent(bot, "teamfight")
      pcall(function() bot:Action_AttackUnit(snap.nearestEnemy, false) end)
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
