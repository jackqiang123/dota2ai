-- macro.lua
-- 宏观目标规划器:每 30s 重新评估一次,不是到点就打盾/推塔。
-- 评估三个目标的收益:推塔、打肉山、刷钱,选收益最大的。
local Macro = {}

Macro.REPLAN_INTERVAL = 30

local _lastPlanTime = -1000
local _currentPlan = "farm"

local function gameTime()
  if DotaTime ~= nil then
    local ok, t = pcall(DotaTime)
    if ok and type(t) == "number" then return t end
  end
  return 0
end

local function clamp01(x)
  if x < 0 then return 0 end
  if x > 1 then return 1 end
  return x
end

-- 收益评估:输入快照 + 团队黑板(见 team.lua)。
-- 推塔收益:兵线在塔下 + 敌方少人 + 我方人数占优。
-- 打盾收益:20 分钟后 + 我方占优 + 敌方减员 + 核心血量健康。
-- 刷钱收益:默认兜底,劣势 / 没视野时最安全。
function Macro.Evaluate(bot, snap, blackboard)
  local t = gameTime()
  local nE = 0
  local nA = 0
  local hp = 1
  if snap ~= nil then
    nE = snap.numEnemies or 0
    nA = snap.numAllies or 0
    hp = snap.healthPct or 1
  end
  local deadEnemies = 0
  if blackboard ~= nil and blackboard.deadEnemies ~= nil then
    deadEnemies = blackboard.deadEnemies
  end

  local pushScore = 0.3
  if t > 600 then pushScore = pushScore + 0.2 end
  if nE == 0 then pushScore = pushScore + 0.2 end
  if (nA + 1) > nE then pushScore = pushScore + 0.15 end
  if snap ~= nil and snap.nearbyEnemyTowers ~= nil and #snap.nearbyEnemyTowers > 0 then
    pushScore = pushScore + 0.15
  end

  local roshanScore = 0
  if t > 1200 and hp > 0.6 and (nA + 1) >= 3 and deadEnemies >= 1 then
    roshanScore = 0.65
    if deadEnemies >= 2 then roshanScore = roshanScore + 0.2 end
  end

  local farmScore = 0.5
  if nE >= 2 then farmScore = farmScore + 0.2 end
  if hp < 0.5 then farmScore = farmScore + 0.1 end
  if t < 600 then farmScore = farmScore + 0.1 end

  local scores = {
    push = clamp01(pushScore),
    roshan = clamp01(roshanScore),
    farm = clamp01(farmScore),
  }
  local best = "farm"
  local bestScore = -1
  for k, v in pairs(scores) do
    if v > bestScore then
      bestScore = v
      best = k
    end
  end
  return best, scores
end

-- 每 30s 才重算一次计划,中间沿用旧计划,避免目标来回横跳。
function Macro.GetPlan(bot, snap, blackboard)
  local t = gameTime()
  if t - _lastPlanTime >= Macro.REPLAN_INTERVAL or _lastPlanTime < 0 then
    local plan, _scores = Macro.Evaluate(bot, snap, blackboard)
    _currentPlan = plan
    _lastPlanTime = t
    if blackboard ~= nil then blackboard.plan = plan end
  end
  return _currentPlan
end

-- 目标点:推塔去最近敌塔,打盾去肉山坑(固定坐标),刷钱去己方野区。
-- 肉山坑坐标为游戏内固定点,不同版本略有偏移,此处用 7.38+ 的常规坑位。
function Macro.GetObjectiveLocation(bot, plan, snap)
  if plan == "roshan" then
    -- Roshan 坑:radiant 方 (-1800, -1700) 附近,dire 方镜像;用己方半场坑位简化。
    if bot ~= nil then
      local team = 2
      local ok, tm = pcall(function() return bot:GetTeam() end)
      if ok then team = tm or 2 end
      if team == 2 then
        return { x = -1800, y = -1700, z = 0 }
      else
        return { x = 1800, y = 1700, z = 0 }
      end
    end
    return { x = -1800, y = -1700, z = 0 }
  end
  if plan == "push" and snap ~= nil and snap.nearbyEnemyTowers ~= nil
    and #snap.nearbyEnemyTowers > 0 then
    local tower = snap.nearbyEnemyTowers[1]
    local ok, loc = pcall(function() return tower:GetLocation() end)
    if ok then return loc end
  end
  return nil
end

return Macro
