-- item_purchase_lion.lua -- Lion 莱恩 -- 出装顺序在 data/heroes.lua 的 items 表里。
local Heroes = require("bots/data/heroes")
local Micro = require("bots/engine/micro")
local HERO_KEY = "lion"

function ItemPurchaseThink()
  local bot = GetBot()
  if bot == nil then return end
  Micro.TryBuyNextItem(bot, Heroes[HERO_KEY])
end
