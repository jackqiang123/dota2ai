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
  -- 只在敌方真正威胁己方塔时守塔: 敌方英雄须在最近己方塔 900 码内。
  -- 旧版只要“塔在 1600 内 + 任意敌方英雄在 1200 视野内”就给 0.8, 导致
  -- 对线期每 tick 在 laning(0.75) 与 defend(0.8) 之间横跳、走到塔下又走回、
  -- 永远够不着小兵 (模拟实测: axe 在 (-325) 与 (-544) 之间 2 tick 一循环)。
  if snap.nearbyAllyTowers ~= nil and #snap.nearbyAllyTowers > 0 and (snap.numEnemies or 0) >= 1 then
    local towerLoc = nil
    local ok, l = pcall(function() return snap.nearbyAllyTowers[1]:GetLocation() end)
    if ok then towerLoc = l end
    local enemyLoc = nil
    if snap.nearestEnemy ~= nil then
      local ok2, el = pcall(function() return snap.nearestEnemy:GetLocation() end)
      if ok2 then enemyLoc = el end
    end
    if towerLoc ~= nil and enemyLoc ~= nil then
      local dx = towerLoc.x - enemyLoc.x
      local dy = towerLoc.y - enemyLoc.y
      if math.sqrt(dx * dx + dy * dy) < 900 then return 0.8 end
    end
  end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) > 0.5 then return 0.5 end
  return 0.1
end

function M.Think(bot, snap, bb)
  if snap.nearbyAllyTowers ~= nil and #snap.nearbyAllyTowers > 0 then
    local loc = nil
    local ok, l = pcall(function() return snap.nearbyAllyTowers[1]:GetLocation() end)
    if ok then loc = l end
    if loc ~= nil and snap.location ~= nil then
      local dx = loc.x - snap.location.x
      local dy = loc.y - snap.location.y
      if math.sqrt(dx * dx + dy * dy) > 300 then
        pcall(function() bot:Action_MoveToLocation(loc) end) return
      end
      -- 已在塔下: 直接打最近的敌方英雄, 不要只站着等 (旧版只下移动指令)。
      if snap.nearestEnemy ~= nil then pcall(function() bot:Action_AttackUnit(snap.nearestEnemy, false) end) return end
      -- 塔下没有敌方英雄: 打来攻塔的小兵, 没有小兵就去等兵落点, 不要原地干站
      -- (旧版此时直接 return、不下任何指令)。
      if snap.nearbyEnemyCreeps ~= nil and #snap.nearbyEnemyCreeps > 0 then pcall(function() bot:Action_AttackUnit(snap.nearbyEnemyCreeps[1], false) end) return end
      local Utility = require(GetScriptDirectory() .. "/engine/utility")
      pcall(function() bot:Action_MoveToLocation(Utility.GetLaneWaitPoint(bot, snap)) end) return
    end
  end
  if snap.nearestEnemy ~= nil then pcall(function() bot:Action_AttackUnit(snap.nearestEnemy, false) end) return end
  local Utility = require(GetScriptDirectory() .. "/engine/utility")
  pcall(function() bot:Action_MoveToLocation(Utility.GetLaneWaitPoint(bot, snap)) end)
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
