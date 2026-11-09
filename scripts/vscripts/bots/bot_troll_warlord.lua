-- bot_troll_warlord.lua -- Troll Warlord 巨魔战将 (agi, safelane 路) -- 薄 wrapper,决策在 engine/core.lua。
local Core = require("bots/engine/core")

function Think()
  local bot = GetBot()
  if bot == nil then return end
  Core.Think(bot)
end
