-- item_purchase_void_spirit.lua -- Void Spirit 虚无之灵 -- 出装顺序在 data/heroes.lua 的 items 表里。
local Heroes = require("bots/data/heroes")
local Micro = require("bots/engine/micro")
local HERO_KEY = "void_spirit"

function ItemPurchaseThink()
  local bot = GetBot()
  if bot == nil then return end
  Micro.TryBuyNextItem(bot, Heroes[HERO_KEY])
end
