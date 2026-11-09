-- perception.lua
-- 感知层:每 0.25s 做一次快照并缓存,避免每帧全图扫描。
-- 只读 Valve Bot API 的真实函数,不做任何全图作弊:只能看到己方视野内的单位。
-- 设计:Snapshot(bot) 返回一张表,上层决策只读这张表,不直接调 API。
local Perception = {}

Perception.SNAPSHOT_INTERVAL = 0.25

local _cache = {}
local _cacheTime = {}

local function now()
  if DotaTime ~= nil then
    local ok, t = pcall(DotaTime)
    if ok and type(t) == "number" then return t end
  end
  return 0
end

local function safeCall(fn, ...)
  if type(fn) ~= "function" then return nil end
  local ok, r = pcall(fn, ...)
  if ok then return r end
  return nil
end

-- 预测目标在 dt 秒后的血量:当前血量 - 预计受到的伤害 + 预计回复。
-- 用于补刀 / 反补 / 斩杀判断,不是算当前血量。
function Perception.PredictHealth(unit, dt, incomingDps)
  if unit == nil or unit.IsNull == nil then return 0 end
  local okNull, isNull = pcall(function() return unit:IsNull() end)
  if okNull and isNull then return 0 end
  local hp = 0
  local ok, v = pcall(function() return unit:GetHealth() end)
  if ok then hp = v or 0 end
  local regen = 0
  local ok2, r = pcall(function() return unit:GetHealthRegen() end)
  if ok2 then regen = r or 0 end
  local dps = incomingDps or 0
  local predicted = hp + regen * dt - dps * dt
  if predicted < 0 then predicted = 0 end
  return predicted
end

-- 预测目标在 dt 秒后的位置:当前位置 + 朝向速度 * dt(直线外推,带钳制)。
function Perception.PredictLocation(unit, dt)
  if unit == nil then return nil end
  local loc = safeCall(function() return unit:GetLocation() end)
  if loc == nil then return nil end
  local speed = 0
  local ok, v = pcall(function() return unit:GetMovementSpeed() end)
  if ok then speed = v or 0 end
  -- 没有可靠的朝向 API 时不做方向外推,返回当前位置,避免编造走位。
  -- 调用方在有 GetForwardVector 时可自行外推。
  return loc
end

function Perception.Snapshot(bot)
  if bot == nil then return nil end
  local key = tostring(bot)
  local t = now()
  -- DotaTime() 在测试环境恒为 0 时不使用缓存,避免快照永不更新。
  if t > 0 and _cache[key] ~= nil and _cacheTime[key] ~= nil
    and (t - _cacheTime[key]) < Perception.SNAPSHOT_INTERVAL then
    return _cache[key]
  end

  local snap = {}
  snap.time = t
  snap.bot = bot
  snap.health = safeCall(function() return bot:GetHealth() end) or 0
  snap.maxHealth = safeCall(function() return bot:GetMaxHealth() end) or 1
  snap.mana = safeCall(function() return bot:GetMana() end) or 0
  snap.maxMana = safeCall(function() return bot:GetMaxMana() end) or 1
  snap.healthPct = snap.health / math.max(1, snap.maxHealth)
  snap.manaPct = snap.mana / math.max(1, snap.maxMana)
  snap.level = safeCall(function() return bot:GetLevel() end) or 1
  snap.gold = safeCall(function() return bot:GetGold() end) or 0
  snap.location = safeCall(function() return bot:GetLocation() end)
  snap.attackRange = safeCall(function() return bot:GetAttackRange() end) or 150
  snap.attackDamage = safeCall(function() return bot:GetAttackDamage() end) or 50
  snap.team = safeCall(function() return bot:GetTeam() end) or 2

  snap.nearbyEnemies = safeCall(function() return bot:GetNearbyHeroes(1200, true, BOT_MODE_NONE) end) or {}
  snap.nearbyAllies = safeCall(function() return bot:GetNearbyHeroes(1200, false, BOT_MODE_NONE) end) or {}
  snap.nearbyEnemyCreeps = safeCall(function() return bot:GetNearbyCreeps(1200, true) end) or {}
  snap.nearbyAllyCreeps = safeCall(function() return bot:GetNearbyCreeps(1200, false) end) or {}
  snap.nearbyEnemyTowers = safeCall(function() return bot:GetNearbyTowers(1600, true) end) or {}
  snap.nearbyAllyTowers = safeCall(function() return bot:GetNearbyTowers(1600, false) end) or {}
  snap.nearbyTrees = {}

  snap.numEnemies = #snap.nearbyEnemies
  snap.numAllies = #snap.nearbyAllies

  -- 最近的敌方英雄及其血量,供撤退 / 参团打分用。
  snap.nearestEnemy = nil
  snap.nearestEnemyDist = 1e9
  if snap.location ~= nil then
    for _, e in ipairs(snap.nearbyEnemies) do
      if e ~= nil and e.IsAlive ~= nil then
        local okAlive, alive = pcall(function() return e:IsAlive() end)
        if okAlive and alive then
          local eloc = safeCall(function() return e:GetLocation() end)
          if eloc ~= nil then
            local dx = eloc.x - snap.location.x
            local dy = eloc.y - snap.location.y
            local d = math.sqrt(dx * dx + dy * dy)
            if d < snap.nearestEnemyDist then
              snap.nearestEnemyDist = d
              snap.nearestEnemy = e
            end
          end
        end
      end
    end
  end

  -- 可补刀的敌方小兵:按“0.3s 后血量 <= 我方一击伤害”筛选,见 micro.lua。
  snap.lastHittable = {}
  snap.deniable = {}
  local attackPoint = 0.3
  for _, c in ipairs(snap.nearbyEnemyCreeps) do
    if c ~= nil then
      local hp = Perception.PredictHealth(c, attackPoint, 0)
      if hp > 0 and hp <= snap.attackDamage then
        snap.lastHittable[#snap.lastHittable + 1] = c
      end
    end
  end
  for _, c in ipairs(snap.nearbyAllyCreeps) do
    if c ~= nil then
      local hp = 0
      local ok, v = pcall(function() return c:GetHealth() end)
      if ok then hp = v or 0 end
      local maxHp = 1
      local ok2, m = pcall(function() return c:GetMaxHealth() end)
      if ok2 then maxHp = m or 1 end
      if hp > 0 and hp / maxHp < 0.5 then
        snap.deniable[#snap.deniable + 1] = c
      end
    end
  end

  if t > 0 then
    _cache[key] = snap
    _cacheTime[key] = t
  end
  return snap
end

function Perception.Invalidate(bot)
  if bot == nil then return end
  local key = tostring(bot)
  _cache[key] = nil
  _cacheTime[key] = nil
end

return Perception
