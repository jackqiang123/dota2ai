-- item_purchase_arc_warden.lua -- Arc Warden 天穹守望者 -- v2.0.0: 出装走 item_purchase_generic.lua 的状态机,
-- 读 BotLib 的 sBuyList / sSellList。
local Generic = require(GetScriptDirectory() .. "/item_purchase_generic")

function ItemPurchaseThink()
  local bot = GetBot()
  if bot == nil then return end
  Generic.ItemPurchaseThinkFor(bot)
end
