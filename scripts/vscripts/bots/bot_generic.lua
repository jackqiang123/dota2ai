-- bot_generic.lua
-- 通用 Bot 入口:没有专属 bot_<hero>.lua 的英雄走这里。
-- 所有决策都在 engine/core.lua 里,这里只做转发,保持薄入口。
local Core = require("bots/engine/core")

-- 难度:默认困难(3)。房间设置 / 控制台可通过 _G.DOTA_AI_DIFFICULTY 改,
-- 1=简单 2=中等 3=困难 4=疯狂(只靠反应与决策阈值区分,Lua 无法发金钱/经验,见 utility.lua)。
if _G.DOTA_AI_DIFFICULTY == nil then
  _G.DOTA_AI_DIFFICULTY = 3
end

function Think()
  local bot = GetBot()
  if bot == nil then return end
  Core.Think(bot)
end
