-- mode_laning_generic.lua -- 对线模式: 前期赖线、补刀、反补。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local Laning = require(GetScriptDirectory() .. "/engine/perception")
local M = {}
M.NAME = "laning"

function M.GetDesire(bot, snap, bb)
  if bot == nil or snap == nil then return 0 end
  local t = snap.time or 0
  if t > 600 then return 0.15 end
  local hp = snap.healthPct or 1
  if hp < 0.3 then return 0.1 end
  if #snap.nearbyEnemyCreeps > 0 or #snap.nearbyAllyCreeps > 0 then return 0.75 end
  return 0.5
end

function M.Think(bot, snap, bb)
  local Micro = require(GetScriptDirectory() .. "/engine/micro")
  local Utility = require(GetScriptDirectory() .. "/engine/utility")
  local diff = Utility.GetDifficulty()
  local target = Micro.FindLastHitTarget(bot, snap, diff.lasthitMargin)
  if target ~= nil then pcall(function() bot:Action_AttackUnit(target, false) end) return end
  if snap.deniable ~= nil and #snap.deniable > 0 then pcall(function() bot:Action_AttackUnit(snap.deniable[1], false) end) return end
  if snap.nearbyEnemyCreeps ~= nil and #snap.nearbyEnemyCreeps > 0 then pcall(function() bot:Action_AttackUnit(snap.nearbyEnemyCreeps[1], false) end) return end
  if snap.nearbyAllyCreeps ~= nil and #snap.nearbyAllyCreeps > 0 then pcall(function() bot:Action_MoveToUnit(snap.nearbyAllyCreeps[1]) end) return end
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
