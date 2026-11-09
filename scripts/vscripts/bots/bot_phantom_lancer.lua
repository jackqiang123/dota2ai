-- bot_phantom_lancer.lua -- Phantom Lancer 幻影长矛手 (agi, safelane 路) -- 薄 wrapper,决策在 engine/core.lua。
local Core = require("bots/engine/core")

function Think()
  local bot = GetBot()
  if bot == nil then return end
  Core.Think(bot)
end
