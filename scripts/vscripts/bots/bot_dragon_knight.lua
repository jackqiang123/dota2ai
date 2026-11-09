-- bot_dragon_knight.lua -- Dragon Knight 龙骑士 (str, safelane 路) -- v2.0.0 薄 wrapper,决策在 mode_dispatcher.lua。
local ModeDispatcher = require(GetScriptDirectory() .. "/mode_dispatcher")

function Think()
  local bot = GetBot()
  if bot == nil then return end
  ModeDispatcher.Think(bot)
end
