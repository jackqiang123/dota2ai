-- bot_night_stalker.lua -- Night Stalker 暗夜魔王 (str, offlane 路) -- 薄 wrapper,决策在 engine/core.lua。
local Core = require("bots/engine/core")

function Think()
  local bot = GetBot()
  if bot == nil then return end
  Core.Think(bot)
end
