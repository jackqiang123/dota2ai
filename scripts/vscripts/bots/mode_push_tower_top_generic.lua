-- mode_push_tower_top_generic.lua -- 推塔模式 (上路包装, 委托给 mode_push_generic)。
local Push = require(GetScriptDirectory() .. "/mode_push_generic")
local M = {}
M.NAME = "push-top"
M.LANE = "top"

function M.GetDesire(bot, snap, bb)
  local d = Push.GetDesire(bot, snap, bb)
  if snap ~= nil and snap.nearbyEnemyTowers ~= nil and #snap.nearbyEnemyTowers > 0 then d = d + 0.05 end
  if d > 1 then d = 1 end
  return d
end

function M.Think(bot, snap, bb)
  return Push.Think(bot, snap, bb)
end

function M.OnStart(bot)
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
