-- mode_roshan_generic.lua -- 打盾模式: 敌方减员 + 我方占优 + 10 分钟后。
-- (v3.1.0: 打盾时间门从 20:00 放宽到 10:00, 与 TeamThink 一致 —— 见 team.lua。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local Roshan = require(GetScriptDirectory() .. "/engine/macro")
local M = {}
M.NAME = "roshan"

function M.GetDesire(bot, snap, bb)
  if bot == nil or snap == nil then return 0 end
  local bb2 = bb or {}
  local dead = bb2.deadEnemies or 0
  local t = snap.time or 0
  if t > 600 and dead >= 1 and (snap.numAllies or 0) + 1 >= 3 and (snap.healthPct or 1) > 0.6 then
    if dead >= 2 then return 0.9 end
    return 0.7
  end
  return 0
end

function M.Think(bot, snap, bb)
  local Macro = require(GetScriptDirectory() .. "/engine/macro")
  local Team = require(GetScriptDirectory() .. "/engine/team")
  local bb2 = bb or Team.GetBlackboard()
  local loc = Macro.GetObjectiveLocation(bot, "roshan", snap)
  if loc ~= nil then
    -- 已到坑边: 只下移动指令永远打不掉肉山 (旧版 bug: Bot 在坑边干站)。
    -- 改为攻击移动, 走到坑边就自动攻击肉山 (Action_AttackMove 为真实 Bot API)。
    if snap.location ~= nil then
      local dx = loc.x - snap.location.x
      local dy = loc.y - snap.location.y
      if math.sqrt(dx * dx + dy * dy) < 400 then
        pcall(function() bot:Action_AttackMove(loc) end) return
      end
    end
    pcall(function() bot:Action_MoveToLocation(loc) end) return
  end
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
