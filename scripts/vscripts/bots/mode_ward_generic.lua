-- mode_ward_generic.lua -- 插眼模式: 背包有眼时去预设点插眼。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local Ward = require(GetScriptDirectory() .. "/engine/micro")
local M = {}
M.NAME = "ward"

function M.GetDesire(bot, snap, bb)
  if bot == nil or snap == nil then return 0 end
  local Utility = require(GetScriptDirectory() .. "/engine/utility")
  local scores, _best = Utility.Score(bot, snap, nil, snap.time or 0)
  if scores ~= nil and scores.ward ~= nil and scores.ward > 0 then return scores.ward end
  return 0.2
end

function M.Think(bot, snap, bb)
  local Micro = require(GetScriptDirectory() .. "/engine/micro")
  if Micro.TryPlaceWard(bot, snap) then return end
  pcall(function() bot:Action_MoveToLocation({ x = 0, y = 0, z = 0 }) end)
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
