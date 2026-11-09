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
  if snap.nearbyAllyCreeps ~= nil and #snap.nearbyAllyCreeps > 0 then
    -- 跟随的小兵如果已经在身边 (召唤物原地待命 / 攻塔的小兵不再前进),
    -- 再跟下去就是站桩: 改去等兵落点 (棘轮式推进, 见 Utility.GetLaneWaitPoint)。
    -- (模拟实测 Enigma 跟 eidolon 卡住。)
    local c = snap.nearbyAllyCreeps[1]
    local cd = nil
    if snap.location ~= nil then
      local ok, loc = pcall(function() return c:GetLocation() end)
      if ok and loc ~= nil then
        local dx = loc.x - snap.location.x
        local dy = loc.y - snap.location.y
        cd = math.sqrt(dx * dx + dy * dy)
      end
    end
    if cd ~= nil and cd <= 150 then
      pcall(function() bot:Action_MoveToLocation(Utility.GetLaneWaitPoint(bot, snap)) end)
      return
    end
    pcall(function() bot:Action_MoveToUnit(c) end) return
  end
  -- 附近没有兵: 去等兵落点 (棘轮式推进), 不要在固定交汇点原地等下一波。
  -- 旧版此时不下任何指令, 泉水边无兵时会卡住不动 (模拟实测)。
  pcall(function() bot:Action_MoveToLocation(Utility.GetLaneWaitPoint(bot, snap)) end)
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
