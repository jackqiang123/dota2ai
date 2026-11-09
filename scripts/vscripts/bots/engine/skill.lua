-- skill.lua
-- 技能读取层 (v2.0.0, 方法来源: Valve Bot API 文档 + OHA ARCHITECTURE.md 第 4 节描述的分段,
-- 实现全部自己写, 未复制 OHA 代码)。
-- 职责: 动态读槽位 (不写死槽位号)、按名取技能、天赋表、施放辅助、快照统计辅助。
-- 槽位约定 (Valve API): 0-9 为普通技能槽, 10-17 为天赋槽; generic_hidden 为填充槽, 跳过。
-- 天赋: 每档 2 个, t10=槽 10/11, t15=12/13, t20=14/15, t25=16/17。
local Skill = {}

local function safeCall(fn, ...)
  if type(fn) ~= "function" then return nil end
  local ok, r = pcall(fn, ...)
  if ok then return r end
  return nil
end

local function abilityName(ab)
  if ab == nil then return nil end
  local ok, n = pcall(function() return ab:GetAbilityName() end)
  if ok then return n end
  return nil
end

function Skill.IsCastable(ab)
  if ab == nil then return false end
  local okN, isNull = pcall(function() return ab:IsNull() end)
  if okN and isNull then return false end
  local okP, passive = pcall(function() return ab:IsPassive() end)
  if okP and passive then return false end
  local ok, v = pcall(function() return ab:IsFullyCastable() end)
  return ok and v == true
end

-- 返回按槽位顺序排好的可学技能名列表 (跳过 generic_hidden / 空槽 / 天赋槽)。
-- 不依赖写死的槽位号: Valve 重排技能后, 列表顺序跟着游戏走, 调用方按名查。
function Skill.GetAbilityList(bot)
  local list = {}
  if bot == nil then return list end
  for slot = 0, 9 do
    local ab = safeCall(function() return bot:GetAbilityInSlot(slot) end)
    local name = abilityName(ab)
    if name ~= nil and name ~= "" and name ~= "generic_hidden" then
      list[#list + 1] = name
    end
  end
  return list
end

-- 返回 name -> ability 对象表, 供 Consider 按真实技能名取技能。
function Skill.GetAbilityMap(bot)
  local map = {}
  if bot == nil then return map end
  for slot = 0, 9 do
    local ab = safeCall(function() return bot:GetAbilityInSlot(slot) end)
    local name = abilityName(ab)
    if name ~= nil and name ~= "" and name ~= "generic_hidden" then
      map[name] = ab
    end
  end
  return map
end

function Skill.GetAbilityByName(bot, name)
  if bot == nil or name == nil then return nil end
  local ab = safeCall(function() return bot:GetAbilityByName(name) end)
  if ab ~= nil then return ab end
  return Skill.GetAbilityMap(bot)[name]
end

-- 天赋名列表 (槽 10-17, 按槽位顺序)。
function Skill.GetTalentList(bot)
  local list = {}
  if bot == nil then return list end
  for slot = 10, 17 do
    local ab = safeCall(function() return bot:GetAbilityInSlot(slot) end)
    local name = abilityName(ab)
    if name ~= nil and name ~= "" then list[#list + 1] = name end
  end
  return list
end

-- 按天赋表 (t10/t15/t20/t25 各 0=左/1=右) 点天赋。tier 为 10/15/20/25。
-- 返回 true 表示已发出升级指令。
function Skill.LevelTalent(bot, talents, tier)
  if bot == nil or talents == nil or tier == nil then return false end
  local side = talents[tier]
  if side == nil then return false end
  local list = Skill.GetTalentList(bot)
  local idx = 1
  if tier == 10 then idx = 1 elseif tier == 15 then idx = 3
  elseif tier == 20 then idx = 5 elseif tier == 25 then idx = 7
  else return false end
  local name = list[idx + side]
  if name == nil then return false end
  local ok = pcall(function() return bot:Action_LevelAbility(name) end)
  return ok == true
end

-- 把加点表 (1-25 级, 元素为技能列表下标, 0=天赋级) 解析为技能名序列。
function Skill.GetSkillList(bot, build)
  local names = Skill.GetAbilityList(bot)
  local out = {}
  for _, idx in ipairs(build or {}) do
    if idx ~= nil and idx > 0 and names[idx] ~= nil then
      out[#out + 1] = names[idx]
    else
      out[#out + 1] = nil
    end
  end
  return out
end

-- 按 desire/target/castType 施放一次技能, 成功返回 true。
-- castType: "unit" 用 Action_UseAbilityOnEntity, "location" 用
-- Action_UseAbilityOnLocation (目标位置取 target 的位置), "none" 用 Action_UseAbility。
function Skill.Cast(bot, ability, target, castType)
  if bot == nil or ability == nil then return false end
  if castType == "unit" then
    if target == nil then return false end
    local ok = pcall(function() bot:Action_UseAbilityOnEntity(ability, target) end)
    return ok == true
  elseif castType == "location" then
    if target == nil then return false end
    local loc = safeCall(function() return target:GetLocation() end)
    if loc == nil then return false end
    local ok = pcall(function() bot:Action_UseAbilityOnLocation(ability, loc) end)
    return ok == true
  else
    local ok = pcall(function() bot:Action_UseAbility(ability) end)
    return ok == true
  end
end

-- ---- 快照统计辅助 (供 Consider 用, 只读 snap, 不调全图 API) ----
local function distTo(botLoc, u)
  if botLoc == nil or u == nil then return 1e9 end
  local loc = safeCall(function() return u:GetLocation() end)
  if loc == nil then return 1e9 end
  local dx = loc.x - botLoc.x
  local dy = loc.y - botLoc.y
  return math.sqrt(dx * dx + dy * dy)
end

function Skill.HpOf(u)
  if u == nil then return 0 end
  local ok, v = pcall(function() return u:GetHealth() end)
  if ok then return v or 0 end
  return 0
end

function Skill.HpPctOf(u)
  if u == nil then return 1 end
  local hp = Skill.HpOf(u)
  local ok, m = pcall(function() return u:GetMaxHealth() end)
  local maxHp = 1
  if ok then maxHp = m or 1 end
  return hp / math.max(1, maxHp)
end

function Skill.CountEnemiesInRange(snap, range)
  if snap == nil or snap.nearbyEnemies == nil then return 0 end
  local n = 0
  for _, e in ipairs(snap.nearbyEnemies) do
    if distTo(snap.location, e) <= range then n = n + 1 end
  end
  return n
end

function Skill.CountLowHpEnemies(snap, pct)
  if snap == nil or snap.nearbyEnemies == nil then return 0 end
  local n = 0
  for _, e in ipairs(snap.nearbyEnemies) do
    if Skill.HpPctOf(e) < pct then n = n + 1 end
  end
  return n
end

function Skill.LowestHpEnemy(snap)
  if snap == nil or snap.nearbyEnemies == nil then return nil end
  local best, bestPct = nil, 2
  for _, e in ipairs(snap.nearbyEnemies) do
    local p = Skill.HpPctOf(e)
    if p < bestPct then best, bestPct = e, p end
  end
  return best
end

function Skill.LowestHpAlly(snap)
  if snap == nil or snap.nearbyAllies == nil then return nil end
  local best, bestPct = nil, 2
  for _, a in ipairs(snap.nearbyAllies) do
    local p = Skill.HpPctOf(a)
    if p < bestPct then best, bestPct = a, p end
  end
  return best
end

function Skill.LowestHpAllyPct(snap)
  local ally = Skill.LowestHpAlly(snap)
  if ally == nil then return nil, 1 end
  return ally, Skill.HpPctOf(ally)
end

return Skill
