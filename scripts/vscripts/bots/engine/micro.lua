-- micro.lua
-- 微操层:技能释放、走位、补刀预判、物品使用。
-- 核心是“算 0.3s 后的状态再出手”,不是看当前血量。
-- v1.1.0:补齐 channel / summon / aura / passive / escape 分支;救人优先于进攻;
--        连招窗口上报与 2 秒防重叠;插眼;信使送货(全 pcall,API 不存在时静默 no-op)。
local Micro = {}

Micro.PREDICT_DT = 0.3

local Team = require(GetScriptDirectory() .. "/engine/team")
local Combos = require(GetScriptDirectory() .. "/data/combos")

-- 引导类大招分组(按英雄 key,不猜技能名以外的东西):
-- 单体引导:对最近敌方英雄放;范围引导:对敌方位置放。
Micro.CHANNEL_SINGLE = { bane = true, pudge = true, pugna = true }
Micro.CHANNEL_AOE = { crystal_maiden = true, jakiro = true, witch_doctor = true }

-- 插眼点位:中路河道、己方野区、敌方野区各 1 个通用坐标(非精确眼位悬崖,仅作基础视野)。
Micro.WARD_SPOTS = {
  { x = 0, y = 0, z = 0, label = "river" },
  { x = -2500, y = -2500, z = 0, label = "own_jungle" },
  { x = 2500, y = 2500, z = 0, label = "enemy_jungle" },
}

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

local function gameTime()
  if DotaTime ~= nil then
    local ok, t = pcall(DotaTime)
    if ok and type(t) == "number" then return t end
  end
  return 0
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

-- 救人优先于进攻:队友血量 <35% 且本英雄在救人表里、有 heal/buff 技能时,
-- 先给最残的队友放救人技能(戴泽薄葬、神谕者大、亚巴顿盾、艾欧牵引等)。
-- 按类型 + 英雄 key 的救人表双重判断,不是所有带 heal 的英雄都救人。
function Micro.TryRescueAlly(bot, snap, heroData)
  if bot == nil or snap == nil or heroData == nil or heroData.abilities == nil then
    return false
  end
  if not Combos.RESCUE_HEROES[heroData.key or ""] then return false end
  -- 最残的队友(只看 nearbyAllies,不含自己)。
  local target, lowestPct = nil, 0.35
  for _, ally in ipairs(snap.nearbyAllies or {}) do
    if isAlive(ally) then
      local ahp, amax = 0, 1
      local okA, va = pcall(function() return ally:GetHealth() end)
      if okA then ahp = va or 0 end
      local okB, vb = pcall(function() return ally:GetMaxHealth() end)
      if okB then amax = vb or 1 end
      local pct = ahp / math.max(1, amax)
      if pct < lowestPct then lowestPct, target = pct, ally end
    end
  end
  -- 没有残血队友时,自己残血也可以自救。
  if target == nil and (snap.healthPct or 1) < 0.35 then
    target, lowestPct = bot, snap.healthPct
  end
  if target == nil then return false end
  for idx, ab in ipairs(heroData.abilities) do
    local typ = ab.type or ""
    if typ == "heal" or typ == "buff" then
      local ability = Micro.GetAbility(bot, idx - 1)
      if Micro.IsAbilityCastable(ability) then
        local okU = pcall(function() bot:Action_UseAbilityOnEntity(ability, target) end)
        if okU then return true end
      end
    end
  end
  return false
end

-- 召唤:无目标技能,有敌方英雄在附近或开局时就放,不等残血。
local function trySummon(bot, heroData)
  for idx, ab in ipairs(heroData.abilities or {}) do
    if (ab.type or "") == "summon" then
      local ability = Micro.GetAbility(bot, idx - 1)
      if Micro.IsAbilityCastable(ability) then
        local okU = pcall(function() bot:Action_UseAbility(ability) end)
        if okU then return true end
      end
    end
  end
  return false
end

-- 按 heroes.lua 的技能类型抽象放技能,不为每个英雄手写一套。
-- 类型: point_control / aoe_damage / aoe_control / nuke / heal /
--       buff / debuff / blink / summon / passive / execute / channel / aura / escape
-- 返回 true 表示本帧已发出技能指令,调用方应直接 return。
function Micro.TryCastByType(bot, snap, heroData)
  if bot == nil or snap == nil or heroData == nil or heroData.abilities == nil then
    return false
  end
  -- 0. 救人优先于一切进攻技能。
  if Micro.TryRescueAlly(bot, snap, heroData) then return true end

  local nearest = snap.nearestEnemy
  -- 没有敌方英雄时,召唤系仍可放(开局招宝宝/野怪),其余类型直接返回。
  if nearest == nil or not isAlive(nearest) then
    return trySummon(bot, heroData)
  end
  local dist = snap.nearestEnemyDist or 1e9
  local heroKey = heroData.key or ""

  for idx, ab in ipairs(heroData.abilities) do
    local typ = ab.type or ""
    -- aura / passive 是被动,明确跳过不放(不是漏处理)。
    if typ == "aura" or typ == "passive" then
      -- 什么都不做,继续看下一个技能。
    else
      local ability = Micro.GetAbility(bot, idx - 1)
      if Micro.IsAbilityCastable(ability) then
        -- 召唤系不看射程:有敌人在附近就放。
        if typ == "summon" then
          local okU = pcall(function() bot:Action_UseAbility(ability) end)
          if okU then return true end
        else
          local castRange = 0
          local ok, v = pcall(function() return ability:GetCastRange() end)
          if ok then castRange = v or 0 end
          -- 射程 0 表示近战/自身范围技能,用攻击距离 + 100 估算。
          if castRange <= 0 then castRange = (snap.attackRange or 150) + 100 end
          if dist <= castRange then
            -- 连招窗口防重叠:大招位(第 4 个技能)的 aoe_control / channel,
            -- 若队友 2 秒内刚开过窗口,本帧忍住不放。
            local isUltControl = (idx == 4) and (typ == "aoe_control" or typ == "channel")
            if isUltControl and Team.ShouldHoldUlt(bot) then
              -- 忍住,继续看下一个技能。
            elseif typ == "execute" then
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
                if okU then
                  if isUltControl then Team.ReportComboWindow(bot, loc) end
                  return true
                end
              end
            elseif typ == "channel" then
              -- 单体引导打最近敌方英雄;范围引导打敌方位置;未分组的默认打人。
              if Micro.CHANNEL_AOE[heroKey] then
                local loc = safeCall(function() return nearest:GetLocation() end)
                if loc ~= nil then
                  local okU = pcall(function() bot:Action_UseAbilityOnLocation(ability, loc) end)
                  if okU then
                    if isUltControl then Team.ReportComboWindow(bot, loc) end
                    return true
                  end
                end
              else
                local okU = pcall(function() bot:Action_UseAbilityOnEntity(ability, nearest) end)
                if okU then
                  if isUltControl then
                    local loc = safeCall(function() return nearest:GetLocation() end)
                    if loc ~= nil then Team.ReportComboWindow(bot, loc) end
                  end
                  return true
                end
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
            elseif typ == "blink" or typ == "escape" then
              -- 位移/逃生技能只在追击(敌方残血)或逃生(己方残血)时用,不乱交。
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
    end
  end
  return false
end

-- 插眼:背包里有 item_ward_observer 时,在预设点位插眼。
-- 点位按时间轮换(河道/己方野区/敌方野区),避免 5 个人插同一个点。
function Micro.TryPlaceWard(bot, snap)
  if bot == nil then return false end
  local ward = nil
  for slot = 0, 8 do
    local item = safeCall(function() return bot:GetItemInSlot(slot) end)
    if item ~= nil and not isNull(item) then
      local ok, n = pcall(function() return item:GetName() end)
      if ok and n == "item_ward_observer" then ward = item break end
    end
  end
  if ward == nil then return false end
  local spots = Micro.WARD_SPOTS
  local idx = (math.floor(gameTime() / 120) % #spots) + 1
  local spot = spots[idx]
  local okU = pcall(function() bot:Action_UseAbilityOnLocation(ward, spot) end)
  return okU == true
end

-- 信使送货:全程 pcall,任一 API 不存在就静默 no-op(不崩、不报错)。
-- 储藏里有物品时才尝试送货;读不到储藏数时不猜,直接尝试一次,失败即返回 false。
function Micro.TryDeliverCourier(bot)
  if bot == nil then return false end
  local courier = safeCall(function() return bot:GetCourier() end)
  if courier == nil and GetCourier ~= nil then
    local pid = safeCall(function() return bot:GetPlayerID() end)
    if pid ~= nil then
      courier = safeCall(function() return GetCourier(pid) end)
    end
  end
  if courier == nil then return false end
  -- 储藏物品数:能读到且为 0 就不送;读不到则继续尝试(由 pcall 兜底)。
  local stash = safeCall(function() return bot:GetNumItemsInStash() end)
  if stash == nil then stash = safeCall(function() return bot:GetStashItemCount() end) end
  if stash ~= nil and stash <= 0 then return false end
  local action = nil
  if COURIER_ACTION_TRANSFER_ITEMS ~= nil then action = COURIER_ACTION_TRANSFER_ITEMS end
  if bot.Action_Courier ~= nil then
    local ok = pcall(function() return bot:Action_Courier(action) end)
    if ok then return true end
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
