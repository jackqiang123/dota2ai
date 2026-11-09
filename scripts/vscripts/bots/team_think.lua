-- team_think.lua
-- v2.0.0 Team 层入口 (转发): 真正的战略计算在 engine/team.lua 的 Team.TeamThink() 里。
-- 注意, 以下两点在 v3.3.0 审计里纠正, 旧注释是错的:
--  1. Valve 不会按文件名调用本文件: 原生 Team 层钩子文件叫 team_desires.lua
--     (TeamThink/UpdatePushLaneDesires/...), 不是 team_think.lua; 本文件在
--     真机里没有任何加载方, 只是模拟器 run.lua 显式 dofile 它。
--  2. 真机里 Team 逻辑照常跑, 因为 bot_generic -> mode_dispatcher 每帧直接调
--     Team.TeamThink(); 原生 team_desires.lua 钩子故意不实现 (原生 Mode 系统
--     已被 bot_generic 的完全接管绕过, 原生队伍欲望无人消费)。
local Team = require(GetScriptDirectory() .. "/engine/team")

-- Valve 调用约定: 无参数, 全队共用一张黑板。
function TeamThink()
  local bot = nil
  if GetBot ~= nil then
    local ok, b = pcall(GetBot)
    if ok then bot = b end
  end
  return Team.TeamThink(bot, nil, nil)
end

return Team
