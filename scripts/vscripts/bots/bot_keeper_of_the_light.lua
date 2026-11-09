-- bot_keeper_of_the_light.lua -- Keeper of the Light 光之守卫 (int, support 路) -- 薄 wrapper,决策在 engine/core.lua。
local Core = require("bots/engine/core")

function Think()
  local bot = GetBot()
  if bot == nil then return end
  Core.Think(bot)
end
