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
  if snap.nearestEnemy ~= nil then
    -- 敌人已在攻击射程内就直接打, 不要 MoveToUnit 跟着站桩: 目标在 0 距离
    -- 时跟随指令等于原地不动, 多人互相跟随能卡几分钟 (模拟实测 seed 42:
    -- Axe+Magnus 与 Sven+Void 在同一坐标跟了 3 分钟, 队伍凑不够 3 人抱团,
    -- 打盾计划一次没触发)。真机也一样: 贴着敌人就该打, 不是跟。
    local ed = snap.nearestEnemyDist
    if ed ~= nil and ed <= (snap.attackRange or 150) then
      pcall(function() bot:Action_AttackUnit(snap.nearestEnemy, false) end) return
    end
    pcall(function() bot:Action_MoveToUnit(snap.nearestEnemy) end) return
  end
  -- 没有连招窗口、看不到敌人: 去找最近的队友抱团, 不要原地干站。
  -- 旧版此时不下任何指令, 但 GetDesire 保底 0.2 会让它在无目标时长期胜出并站桩 (模拟实测)。
  if snap.nearbyAllies ~= nil and #snap.nearbyAllies > 0 then
    -- 跟的队友如果已经在身边且不再移动, 再跟下去就是站桩 (会继承对方的卡住):
    -- 改去等兵落点 (棘轮式推进)。
    local ally = snap.nearbyAllies[1]
    local ad = nil
    if snap.location ~= nil then
      local ok, aloc = pcall(function() return ally:GetLocation() end)
      if ok and aloc ~= nil then
        local dx = aloc.x - snap.location.x
        local dy = aloc.y - snap.location.y
        ad = math.sqrt(dx * dx + dy * dy)
      end
    end
    if ad ~= nil and ad <= 150 then
      local Utility = require(GetScriptDirectory() .. "/engine/utility")
      pcall(function() bot:Action_MoveToLocation(Utility.GetLaneWaitPoint(bot, snap)) end) return
    end
    pcall(function() bot:Action_MoveToUnit(ally) end) return
  end
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
