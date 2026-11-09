-- core.lua
-- v2.0.0 兼容垫片: v1.1 的 Core.Think() 已被 Mode 系统取代。
-- 新入口是 mode_dispatcher.lua; 本文件只保留 Core.Think(bot) 供旧代码 / 测试调用,
-- 内部直接转给 ModeDispatcher.Think(bot)。不要在这里再写决策逻辑。
local ModeDispatcher = require(GetScriptDirectory() .. "/mode_dispatcher")
local Perception = require(GetScriptDirectory() .. "/engine/perception")
local Utility = require(GetScriptDirectory() .. "/engine/utility")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Macro = require(GetScriptDirectory() .. "/engine/macro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")

local Core = {}
Core.Perception = Perception
Core.Utility = Utility
Core.Micro = Micro
Core.Macro = Macro
Core.Team = Team
Core.Heroes = Heroes
Core.ModeDispatcher = ModeDispatcher

function Core.ResetThinkState()
  ModeDispatcher.ResetThinkState()
end

function Core.Think(bot)
  return ModeDispatcher.Think(bot)
end

return Core
