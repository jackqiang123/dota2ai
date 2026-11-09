-- bot_bounty_hunter.lua -- Bounty Hunter 赏金猎人 (agi, roam 路) -- 薄 wrapper,决策在 engine/core.lua。
local Core = require("bots/engine/core")

function Think()
  local bot = GetBot()
  if bot == nil then return end
  Core.Think(bot)
end
