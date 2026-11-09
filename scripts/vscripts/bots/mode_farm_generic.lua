-- mode_farm_generic.lua -- 刷钱模式: 野区 / 线上刷钱, 无敌方威胁时兜底。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local Farm = require(GetScriptDirectory() .. "/engine/perception")
local M = {}
M.NAME = "farm"

function M.GetDesire(bot, snap, bb)
  if bot == nil or snap == nil then return 0 end
  if (snap.numEnemies or 0) >= 2 then return 0.2 end
  if #snap.nearbyEnemyCreeps > 0 then return 0.6 end
  return 0.5
end

function M.Think(bot, snap, bb)
  if snap.nearbyEnemyCreeps ~= nil and #snap.nearbyEnemyCreeps > 0 then pcall(function() bot:Action_AttackUnit(snap.nearbyEnemyCreeps[1], false) end) return end
  local loc = { x = -2500, y = -2500, z = 0 }
  if (snap.team or 2) == 3 then loc = { x = 2500, y = 2500, z = 0 } end
  pcall(function() bot:Action_MoveToLocation(loc) end)
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
