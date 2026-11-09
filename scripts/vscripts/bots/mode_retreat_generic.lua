-- mode_retreat_generic.lua -- 撤退模式: 血量低或敌多我少时回塔 / 回泉。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local Retreat = require(GetScriptDirectory() .. "/engine/utility")
local M = {}
M.NAME = "retreat"

function M.GetDesire(bot, snap, bb)
  if bot == nil or snap == nil then return 0 end
  local Utility = require(GetScriptDirectory() .. "/engine/utility")
  local diff = Utility.GetDifficulty()
  local hp = snap.healthPct or 1
  if hp < diff.retreatHp then
    local d = (diff.retreatHp - hp) / diff.retreatHp + 0.3
    if (snap.numEnemies or 0) > (snap.numAllies or 0) then d = d + 0.2 end
    if d > 1 then d = 1 end
    return d
  end
  if (snap.numEnemies or 0) >= 3 and (snap.numAllies or 0) <= 1 and hp < 0.6 then return 0.85 end
  return 0
end

function M.Think(bot, snap, bb)
  local towers = snap.nearbyAllyTowers or {}
  if #towers > 0 then
    local loc = nil
    local ok, l = pcall(function() return towers[1]:GetLocation() end)
    if ok then loc = l end
    if loc ~= nil then pcall(function() bot:Action_MoveToLocation(loc) end) return end
  end
  local fountain = { x = -7000, y = -7000, z = 0 }
  if (snap.team or 2) == 3 then fountain = { x = 7000, y = 7000, z = 0 } end
  pcall(function() bot:Action_MoveToLocation(fountain) end)
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
