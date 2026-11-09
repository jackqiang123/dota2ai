-- bot_templar_assassin.lua -- Templar Assassin 圣堂刺客 (agi, mid 路) -- 薄 wrapper,决策在 engine/core.lua。
local Core = require("bots/engine/core")

function Think()
  local bot = GetBot()
  if bot == nil then return end
  Core.Think(bot)
end
