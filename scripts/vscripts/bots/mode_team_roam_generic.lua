-- mode_team_roam_generic.lua -- 抱团游走: 连招窗口 / 队友集合时一起抓人。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local TeamRoam = require(GetScriptDirectory() .. "/engine/team")
local M = {}
M.NAME = "teamroam"

function M.GetDesire(bot, snap, bb)
  if bot == nil or snap == nil then return 0 end
  local Team = require(GetScriptDirectory() .. "/engine/team")
  if Team.IsComboWindowActive() then return 0.9 end
  if Team.CountIntent("teamfight") >= 2 then return 0.7 end
  if (snap.numAllies or 0) >= 3 and (snap.numEnemies or 0) >= 1 then return 0.6 end
  return 0.2
end

function M.Think(bot, snap, bb)
  local Team = require(GetScriptDirectory() .. "/engine/team")
  local window = Team.GetComboWindow()
  if window ~= nil and window.loc ~= nil then pcall(function() bot:Action_MoveToLocation(window.loc) end) return end
  if snap.nearestEnemy ~= nil then pcall(function() bot:Action_MoveToUnit(snap.nearestEnemy) end) return end
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
