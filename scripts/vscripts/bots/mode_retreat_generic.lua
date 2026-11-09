-- mode_retreat_generic.lua -- 撤退模式: 血量低或敌多我少时回塔 / 回泉。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local Retreat = require(GetScriptDirectory() .. "/engine/utility")
local M = {}
M.NAME = "retreat"

-- 每 Bot 的撤退目的地 (塔 / 泉), 按 Bot 名索引。
-- 目标一旦选定就坚持走完 (塔 -> 泉单向路线), 不按距离/血量阈值每帧重选:
-- 旧版按“离塔 300”切塔/泉两个目的地, 一步移动 (~300/tick) 就跨过阈值,
-- 导致每帧在塔和泉之间来回折返、60 秒净位移为零 (模拟实测)。
-- 塔只是中途安全点 (塔不回血), 到塔后血量未满就继续去泉, 不在塔下干站。
local retreatTarget = {}

local function botKey(bot)
  local ok, name = pcall(function() return bot:GetUnitName() end)
  if ok and name ~= nil then return name end
  return tostring(bot)
end

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
  local Utility = require(GetScriptDirectory() .. "/engine/utility")
  local diff = Utility.GetDifficulty()
  local hp = snap.healthPct or 1
  local key = botKey(bot)
  local fountain = { x = -7000, y = -7000, z = 0 }
  if (snap.team or 2) == 3 then fountain = { x = 7000, y = 7000, z = 0 } end
  -- 血量基本回满: 清掉旧目标, 下次撤退重新选。
  if hp >= 0.75 then retreatTarget[key] = nil end
  local tgt = retreatTarget[key]
  if tgt == nil then
    -- 选目的地: 血量危急直接回泉; 否则先回最近的友方塔。
    if hp < diff.retreatHp then
      tgt = { x = fountain.x, y = fountain.y, z = 0, kind = "fountain" }
    else
      local towers = snap.nearbyAllyTowers or {}
      local tloc = nil
      if #towers > 0 then
        local ok, l = pcall(function() return towers[1]:GetLocation() end)
        if ok then tloc = l end
      end
      if tloc ~= nil then
        tgt = { x = tloc.x, y = tloc.y, z = 0, kind = "tower" }
      else
        tgt = { x = fountain.x, y = fountain.y, z = 0, kind = "fountain" }
      end
    end
    retreatTarget[key] = tgt
  end
  -- 到达目的地: 塔只是中途点, 血量未满就继续去泉; 到泉则目标完成。
  if snap.location ~= nil then
    local dx = tgt.x - snap.location.x
    local dy = tgt.y - snap.location.y
    if math.sqrt(dx * dx + dy * dy) <= 150 then
      if tgt.kind == "tower" and hp < 0.75 then
        tgt = { x = fountain.x, y = fountain.y, z = 0, kind = "fountain" }
        retreatTarget[key] = tgt
      else
        retreatTarget[key] = nil
        return
      end
    end
  end
  pcall(function() bot:Action_MoveToLocation({ x = tgt.x, y = tgt.y, z = 0 }) end)
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
