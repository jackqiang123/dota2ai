-- mode_attack_generic.lua -- 进攻模式: 打集火目标, 连招窗口内优先参团。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local Attack = require(GetScriptDirectory() .. "/engine/team")
local M = {}
M.NAME = "attack"

function M.GetDesire(bot, snap, bb)
  if bot == nil or snap == nil then return 0 end
  if (snap.numEnemies or 0) == 0 then return 0 end
  local Team = require(GetScriptDirectory() .. "/engine/team")
  local hp = snap.healthPct or 1
  local score = 0.55
  if Team.IsComboWindowActive() then score = score + 0.25 end
  if hp > 0.6 then score = score + 0.1 end
  if (snap.numAllies or 0) >= (snap.numEnemies or 0) then score = score + 0.1 end
  if score > 1 then score = 1 end
  return score
end

function M.Think(bot, snap, bb)
  local Team = require(GetScriptDirectory() .. "/engine/team")
  Team.ReportIntent(bot, "teamfight")
  local window = Team.GetComboWindow()
  if window ~= nil and window.loc ~= nil and snap.location ~= nil then
    local myName = ""
    local okN, n = pcall(function() return bot:GetUnitName() end)
    if okN then myName = n or "" end
    if window.caster ~= myName then
      local dx = window.loc.x - snap.location.x
      local dy = window.loc.y - snap.location.y
      if math.sqrt(dx * dx + dy * dy) > 300 then pcall(function() bot:Action_MoveToLocation(window.loc) end) return end
    end
  end
  local focus = Team.GetFocusTarget(snap)
  local target = focus or snap.nearestEnemy
  if target ~= nil then pcall(function() bot:Action_AttackUnit(target, false) end) return end
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
