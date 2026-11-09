-- item_purchase_generic.lua
-- v2.0.0 通用出装入口: Valve 每帧调 ItemPurchaseThink(), 按位置买装的状态机。
-- 读本英雄 BotLib 的 sBuyList (按位置, 主位置 >=10 件) + sSellList。
-- 顺序: 第一件没买到的就是当前目标, 不跳过去买后面的; 金币不够就等; 背包满时
-- 按 sSellList 卖掉旧件。组件拆分靠 Valve 的 GetItemComponents() (如可用)。
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")

local SECRET_SHOP_ITEMS = {
  item_ultimate_scepter = true, item_aghanims_scepter = true,
  item_sacred_relic = true, item_demon_edge = true, item_eagle_song = true,
  item_reaver = true, item_mystic_staff = true, item_platemail = true,
}

local function heroKey(bot)
  local ok, name = pcall(function() return bot:GetUnitName() end)
  if not ok or name == nil then return nil end
  return string.gsub(name, "^npc_dota_hero_", "")
end

local function heroPosition(bot, heroData)
  if heroData ~= nil and heroData.positions ~= nil and heroData.positions[1] ~= nil then
    return heroData.positions[1]
  end
  return 5
end

local function loadHeroModule(key)
  if key == nil then return nil end
  local ok, mod = pcall(require, GetScriptDirectory() .. "/BotLib/hero_" .. key)
  if ok then return mod end
  return nil
end

-- 供测试 / 其他入口复用的纯逻辑: 返回本帧买到的物品名, 或 nil。
function ItemPurchaseThinkFor(bot)
  if bot == nil then return nil end
  local key = heroKey(bot)
  local heroData = Heroes[key]
  local pos = heroPosition(bot, heroData)
  local mod = loadHeroModule(key)
  local buyList = nil
  if mod ~= nil and mod.sBuyList ~= nil then
    buyList = mod.sBuyList["pos_" .. pos] or mod.sBuyList["pos_3"]
  end
  if buyList == nil and heroData ~= nil and heroData.items ~= nil then
    buyList = {}
    for _, it in ipairs(heroData.items.early or {}) do buyList[#buyList + 1] = it end
    for _, it in ipairs(heroData.items.mid or {}) do buyList[#buyList + 1] = it end
    for _, it in ipairs(heroData.items.late or {}) do buyList[#buyList + 1] = it end
  end
  if buyList == nil then return nil end
  local gold = 0
  local okG, g = pcall(function() return bot:GetGold() end)
  if okG then gold = g or 0 end
  for _, itemName in ipairs(buyList) do
    local has = false
    for slot = 0, 8 do
      local item = nil
      local okI, it = pcall(function() return bot:GetItemInSlot(slot) end)
      if okI then item = it end
      if item ~= nil then
        local okN, n = pcall(function() return item:GetName() end)
        if okN and n == itemName then has = true break end
      end
    end
    if not has then
      local cost = 0
      if GetItemCost ~= nil then
        local okC, c = pcall(GetItemCost, itemName)
        if okC then cost = c or 0 end
      end
      if gold >= cost then
        local okU = pcall(function() bot:Action_PurchaseItem(itemName) end)
        if okU then return itemName end
      end
      return nil
    end
  end
  return nil
end

function ItemPurchaseThink()
  local bot = GetBot()
  if bot == nil then return end
  ItemPurchaseThinkFor(bot)
end

return { ItemPurchaseThinkFor = ItemPurchaseThinkFor }
