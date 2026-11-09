-- team_think.lua
-- v2.0.0 Team 层入口: Valve 每帧先调一次 TeamThink(), 再调各 Bot 的 Think()。
-- 本文件只做转发, 真正的战略计算在 engine/team.lua 的 Team.TeamThink() 里。
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
