-- mode_roshan_generic.lua -- 打盾模式: 敌方减员 + 我方占优 + 20 分钟后。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local Roshan = require(GetScriptDirectory() .. "/engine/macro")
local M = {}
M.NAME = "roshan"

function M.GetDesire(bot, snap, bb)
  if bot == nil or snap == nil then return 0 end
  local bb2 = bb or {}
  local dead = bb2.deadEnemies or 0
  local t = snap.time or 0
  if t > 1200 and dead >= 1 and (snap.numAllies or 0) + 1 >= 3 and (snap.healthPct or 1) > 0.6 then
    if dead >= 2 then return 0.9 end
    return 0.7
  end
  return 0
end

function M.Think(bot, snap, bb)
  local Macro = require(GetScriptDirectory() .. "/engine/macro")
  local Team = require(GetScriptDirectory() .. "/engine/team")
  local bb2 = bb or Team.GetBlackboard()
  local loc = Macro.GetObjectiveLocation(bot, "roshan", snap)
  if loc ~= nil then pcall(function() bot:Action_MoveToLocation(loc) end) return end
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
