-- item_purchase_witch_doctor.lua -- Witch Doctor 巫医 -- 出装顺序在 data/heroes.lua 的 items 表里。
local Heroes = require("bots/data/heroes")
local Micro = require("bots/engine/micro")
local HERO_KEY = "witch_doctor"

function ItemPurchaseThink()
  local bot = GetBot()
  if bot == nil then return end
  Micro.TryBuyNextItem(bot, Heroes[HERO_KEY])
end
