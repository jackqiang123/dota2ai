-- mode_defend_tower_generic.lua -- 守塔模式: 敌方推我方塔时回防。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local DefendTower = require(GetScriptDirectory() .. "/engine/perception")
local M = {}
M.NAME = "defendtower"

function M.GetDesire(bot, snap, bb)
  if bot == nil or snap == nil then return 0 end
  if snap.nearbyAllyTowers ~= nil and #snap.nearbyAllyTowers > 0 and (snap.numEnemies or 0) >= 1 then return 0.8 end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) > 0.5 then return 0.5 end
  return 0.1
end

function M.Think(bot, snap, bb)
  if snap.nearbyAllyTowers ~= nil and #snap.nearbyAllyTowers > 0 then
    local loc = nil
    local ok, l = pcall(function() return snap.nearbyAllyTowers[1]:GetLocation() end)
    if ok then loc = l end
    if loc ~= nil then pcall(function() bot:Action_MoveToLocation(loc) end) return end
  end
  if snap.nearestEnemy ~= nil then pcall(function() bot:Action_AttackUnit(snap.nearestEnemy, false) end) return end
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
