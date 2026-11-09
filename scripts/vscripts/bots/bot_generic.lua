-- bot_generic.lua
-- v2.0.0 通用 Bot 入口 (约 20 行): 只做初始化 + 调 Mode 分发器, 不再自己算全部行为。
-- 决策在 mode_dispatcher.lua + 各 mode_*_generic.lua 里; 技能在
-- ability_item_usage_generic.lua 里; 出装在 item_purchase_generic.lua 里。
-- 难度: 默认困难 (3)。1=简单 2=中等 3=困难 4=疯狂 (只靠反应与决策阈值区分,
-- Lua 无法发金钱/经验, 见 engine/utility.lua)。
local ModeDispatcher = require(GetScriptDirectory() .. "/mode_dispatcher")

if _G.DOTA_AI_DIFFICULTY == nil then
  _G.DOTA_AI_DIFFICULTY = 3
end

function Think()
  local bot = GetBot()
  if bot == nil then return end
  ModeDispatcher.Think(bot)
end
