-- mode_secret_shop_generic.lua -- 秘密商店模式: 需要秘密商店配件且有钱时去买。
-- v2.0.0 Mode 文件: Valve 原生 Mode 系统的一部分。
-- 约定: GetDesire(bot, snap, bb) 返回 0.0-1.0, 每帧对所有模式都调, 分数最高的模式的
-- Think() 才跑; OnStart() 在模式刚接管时调一次。模块表是本文件的返回值,
-- 同时把同名全局函数挂出来供 Valve 的 Mode 加载器调用 (游戏内每个 Mode 文件单独加载,
-- 全局名不冲突; 测试里请用模块表, 不要依赖全局)。
local SecretShop = require(GetScriptDirectory() .. "/engine/perception")
local M = {}
M.NAME = "secretshop"

function M.GetDesire(bot, snap, bb)
  if bot == nil or snap == nil then return 0 end
  local gold = snap.gold or 0
  if gold >= 1000 then return 0.35 end
  return 0.05
end

function M.Think(bot, snap, bb)
  local loc = { x = -2000, y = 2000, z = 0 }
  if (snap.team or 2) == 3 then loc = { x = 2000, y = -2000, z = 0 } end
  pcall(function() bot:Action_MoveToLocation(loc) end)
end

function M.OnStart(bot)
  -- 无需特殊初始化。
end

GetDesire = M.GetDesire
Think = M.Think
OnStart = M.OnStart

return M
