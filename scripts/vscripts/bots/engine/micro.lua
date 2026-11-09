-- micro.lua
-- 微操层:技能释放、走位、补刀预判、物品使用。
-- 核心是“算 0.3s 后的状态再出手”,不是看当前血量。
local Micro = {}

Micro.PREDICT_DT = 0.3

local function safeCall(fn, ...)
  if type(fn) ~= "function" then return nil end
  local ok, r = pcall(fn, ...)
  if ok then return r end
  return nil
end

local function isAlive(unit)
  if unit == nil then return false end
  local ok, v = pcall(function() return unit:IsAlive() end)
  return ok and v == true
end

local function isNull(unit)
  if unit == nil then return true end
  local ok, v = pcall(function() return unit:IsNull() end)
  return (not ok) or v == true
end

-- 找可补的刀:敌方小兵在 dt 后血量 <= 我方攻击伤害 + 难度容错。
-- 难度越低容错越大(越晚出手、越容易漏刀),疯狂档容错为 0。
function Micro.FindLastHitTarget(bot, snap, margin)
  if bot == nil or snap == nil or snap.lastHittable == nil then return nil end
  local dmg = snap.attackDamage or 50
  local best = nil
  local bestHp = 1e9
  for _, c in ipairs(snap.lastHittable) do
    if isAlive(c) then
      local hp = 0
      local ok, v = pcall(function() return c:GetHealth() end)
      if ok then hp = v or 0 end
      if hp <= dmg + (margin or 0) and hp < bestHp then
        bestHp = hp
        best = c
      end
    end
  end
  return best
end

-- 技能是否可放:存在、非被动、CD 转好、蓝够。
function Micro.IsAbilityCastable(ability)
  if ability == nil or isNull(ability) then return false end
  local okP, passive = pcall(function() return ability:IsPassive() end)
  if okP and passive then return false end
  local ok, v = pcall(function() return ability:IsFullyCastable() end)
  return ok and v == true
end

function Micro.GetAbility(bot, slot)
  if bot == nil then return nil end
  return safeCall(function() return bot:GetAbilityInSlot(slot) end)
end

-- 按 heroes.lua 的技能类型抽象放技能,不为每个英雄手写一套。
-- 类型: point_control(点控) / aoe_damage / aoe_control / nuke / heal /
--       buff / debuff / blink(位移) / summon / passive / execute(斩杀) / channel
-- 返回 true 表示本帧已发出技能指令,调用方应直接 return。
function Micro.TryCastByType(bot, snap, heroData)
  if bot == nil or snap == nil or heroData == nil or heroData.abilities == nil then
    return false
  end
  local nearest = snap.nearestEnemy
  if nearest == nil or not isAlive(nearest) then return false end
  local dist = snap.nearestEnemyDist or 1e9

  for idx, ab in ipairs(heroData.abilities) do
    local ability = Micro.GetAbility(bot, idx - 1)
    if Micro.IsAbilityCastable(ability) then
      local castRange = 0
      local ok, v = pcall(function() return ability:GetCastRange() end)
      if ok then castRange = v or 0 end
      -- 射程 0 表示近战/自身范围技能,用攻击距离 + 100 估算。
      if castRange <= 0 then castRange = (snap.attackRange or 150) + 100 end
      if dist <= castRange then
        local typ = ab.type or ""
        if typ == "execute" then
          local hp = 0
          local ok2, h = pcall(function() return nearest:GetHealth() end)
          if ok2 then hp = h or 0 end
          local maxHp = 1
          local ok3, m = pcall(function() return nearest:GetMaxHealth() end)
          if ok3 then maxHp = m or 1 end
          if hp / maxHp < 0.35 then
            local okU = pcall(function() bot:Action_UseAbilityOnEntity(ability, nearest) end)
            if okU then return true end
          end
        elseif typ == "point_control" or typ == "nuke" or typ == "debuff" then
          local okU = pcall(function() bot:Action_UseAbilityOnEntity(ability, nearest) end)
          if okU then return true end
        elseif typ == "aoe_damage" or typ == "aoe_control" then
          local loc = safeCall(function() return nearest:GetLocation() end)
          if loc ~= nil then
            local okU = pcall(function() bot:Action_UseAbilityOnLocation(ability, loc) end)
            if okU then return true end
          end
        elseif typ == "heal" or typ == "buff" then
          -- 治疗/增益优先给自己或附近血量最低的友军。
          local target = bot
          local lowestPct = snap.healthPct or 1
          for _, ally in ipairs(snap.nearbyAllies or {}) do
            if isAlive(ally) then
              local ahp, amax = 0, 1
              local okA, va = pcall(function() return ally:GetHealth() end)
              if okA then ahp = va or 0 end
              local okB, vb = pcall(function() return ally:GetMaxHealth() end)
              if okB then amax = vb or 1 end
              local pct = ahp / math.max(1, amax)
              if pct < lowestPct then
                lowestPct = pct
                target = ally
              end
            end
          end
          if lowestPct < 0.7 or typ == "buff" then
            local okU = pcall(function() bot:Action_UseAbilityOnEntity(ability, target) end)
            if okU then return true end
          end
        elseif typ == "blink" then
          -- 位移技能只在追击(敌方残血)或逃生(己方残血)时用,不乱交。
          local ehp = 0
          local okE, eh = pcall(function() return nearest:GetHealth() end)
          if okE then ehp = eh or 0 end
          local emax = 1
          local okF, em = pcall(function() return nearest:GetMaxHealth() end)
          if okF then emax = em or 1 end
          if (snap.healthPct or 1) < 0.35 or (ehp / math.max(1, emax)) < 0.3 then
            local loc = safeCall(function() return nearest:GetLocation() end)
            if loc ~= nil then
              local okU = pcall(function() bot:Action_UseAbilityOnLocation(ability, loc) end)
              if okU then return true end
            end
          end
        end
      end
    end
  end
  return false
end

-- 物品使用:治疗药膏/净化药水/魔棒等基础消耗品,按血蓝阈值使用。
-- 大件主动物品(BKB/跳刀/吹风等)由 heroes.lua 的 situational 装备 + 类型驱动,
-- 这里只处理通用保命逻辑,不编造物品名。
function Micro.TryUseItems(bot, snap)
  if bot == nil or snap == nil then return false end
  local hp = snap.healthPct or 1
  if hp > 0.5 then return false end
  for slot = 0, 8 do
    local item = safeCall(function() return bot:GetItemInSlot(slot) end)
    if item ~= nil and not isNull(item) then
      local name = ""
      local ok, n = pcall(function() return item:GetName() end)
      if ok then name = n or "" end
      if name == "item_flask" or name == "item_tango" then
        if hp < 0.5 then
          local okU = pcall(function() bot:Action_UseAbility(item) end)
          if okU then return true end
        end
      elseif name == "item_clarity" then
        if (snap.manaPct or 1) < 0.3 then
          local okU = pcall(function() bot:Action_UseAbility(item) end)
          if okU then return true end
        end
      end
    end
  end
  return false
end

-- 买装备:按 heroes.lua 的 items.early -> mid -> late 顺序,逐件购买。
-- 用 GetItemCost 判断金币是否足够,避免在没钱时反复尝试。
function Micro.TryBuyNextItem(bot, heroData)
  if bot == nil or heroData == nil or heroData.items == nil then return false end
  local gold = safeCall(function() return bot:GetGold() end) or 0
  local queue = {}
  for _, it in ipairs(heroData.items.early or {}) do queue[#queue + 1] = it end
  for _, it in ipairs(heroData.items.mid or {}) do queue[#queue + 1] = it end
  for _, it in ipairs(heroData.items.late or {}) do queue[#queue + 1] = it end
  for _, itemName in ipairs(queue) do
    local has = false
    for slot = 0, 8 do
      local item = safeCall(function() return bot:GetItemInSlot(slot) end)
      if item ~= nil and not isNull(item) then
        local ok, n = pcall(function() return item:GetName() end)
        if ok and n == itemName then has = true break end
      end
    end
    if not has then
      local cost = 0
      if GetItemCost ~= nil then
        local ok, c = pcall(GetItemCost, itemName)
        if ok then cost = c or 0 end
      end
      if gold >= cost then
        local okU = pcall(function() bot:Action_PurchaseItem(itemName) end)
        if okU then return true end
      end
      -- 第一件没买到的装备就是当前目标,不要跳过去买后面的。
      return false
    end
  end
  return false
end

return Micro
