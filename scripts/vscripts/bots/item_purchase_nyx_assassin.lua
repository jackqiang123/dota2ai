-- item_purchase_nyx_assassin.lua -- Nyx Assassin 司夜刺客 -- 出装顺序在 data/heroes.lua 的 items 表里。
local Heroes = require("bots/data/heroes")
local Micro = require("bots/engine/micro")
local HERO_KEY = "nyx_assassin"

function ItemPurchaseThink()
  local bot = GetBot()
  if bot == nil then return end
  Micro.TryBuyNextItem(bot, Heroes[HERO_KEY])
end
