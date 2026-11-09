-- mode_laning_generic.lua -- 对线模式: 前期赖线、补刀、反补。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local Laning = require(GetScriptDirectory() .. "/engine/perception")
local M = {}
M.NAME = "laning"

-- 跟随防呆 (模块级, 按英雄名记): 5 秒内没动过的小兵不跟 (召唤物原地待命 /
-- 卡住的小兵), 否则 follow 和等兵落点来回震荡、永远走不出泉水 (模拟实测
-- Arc Warden 复活后跟 Tempest Double 在泉水边乒乓 130 秒, 泉水挂机)。
-- 真机里同样适用: 不动的小兵不是正往线上走的兵线, 跟它没有意义。
local _stall = {}
local function creepStationary(bot, c, snap)
  -- 唯一键: 优先 PlayerID (同名英雄分属两队时名字会撞, 见 mode_dispatcher)。
  local key = "?"
  local ok, pid = pcall(function() return bot:GetPlayerID() end)
  if ok and pid ~= nil then key = "pid:" .. tostring(pid)
  else
    local ok2, name = pcall(function() return bot:GetUnitName() end)
    if ok2 and name ~= nil then key = name end
  end
  local now = snap.time or 0
  local okL, loc = pcall(function() return c:GetLocation() end)
  if not okL or loc == nil then return false end
  local st = _stall[key]
  if st ~= nil and math.abs(loc.x - st.x) < 20 and math.abs(loc.y - st.y) < 20 then
    if now - st.since >= 5 then return true end
    return false
  end
  _stall[key] = { x = loc.x, y = loc.y, since = now }
  return false
end

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
  local diff = Utility.GetDifficulty(bot)
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
    -- 5 秒没动过的小兵不跟: 去等兵落点, 不要在原地乒乓 (见文件头 _stall)。
    if creepStationary(bot, c, snap) then
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
