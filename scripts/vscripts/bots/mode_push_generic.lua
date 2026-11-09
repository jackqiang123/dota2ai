-- mode_push_generic.lua -- 推塔模式 (通用实现, 三个分路文件是它的包装)。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local Push = require(GetScriptDirectory() .. "/engine/macro")
local M = {}
M.NAME = "push"

function M.GetDesire(bot, snap, bb)
  if bot == nil or snap == nil then return 0 end
  local t = snap.time or 0
  local score = 0.3
  if t > 600 then score = score + 0.2 end
  if (snap.numEnemies or 0) == 0 then score = score + 0.15 end
  if snap.nearbyEnemyTowers ~= nil and #snap.nearbyEnemyTowers > 0 then score = score + 0.2 end
  if score > 1 then score = 1 end
  return score
end

function M.Think(bot, snap, bb)
  local Macro = require(GetScriptDirectory() .. "/engine/macro")
  local Team = require(GetScriptDirectory() .. "/engine/team")
  local bb2 = bb or Team.GetBlackboard()
  local plan = Macro.GetPlan(bot, snap, bb2)
  Team.ReportIntent(bot, plan)
  local loc = Macro.GetObjectiveLocation(bot, plan, snap)
  if loc ~= nil then pcall(function() bot:Action_MoveToLocation(loc) end) return end
  if snap.nearbyEnemyTowers ~= nil and #snap.nearbyEnemyTowers > 0 then pcall(function() bot:Action_AttackUnit(snap.nearbyEnemyTowers[1], false) end) return end
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
