-- item_purchase_keeper_of_the_light.lua -- Keeper of the Light 光之守卫 -- v3.0.0: 出装走 item_purchase_generic.lua 的状态机,
-- 读 BotLib 的 sBuyList / sSellList。
local Generic = require(GetScriptDirectory() .. "/item_purchase_generic")

function ItemPurchaseThink()
  local bot = GetBot()
  if bot == nil then return end
  Generic.ItemPurchaseThinkFor(bot)
end
