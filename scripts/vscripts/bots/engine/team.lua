-- team.lua
-- 团队黑板:5 个 Bot 共用一张全局表,互相写意图,不靠聊天轮盘。
-- 黑板只存“意图 + 时间戳”,过期意图自动失效,避免死锁。
local Team = {}

-- 全局黑板,同一局内所有 Bot 共享。
if _G.DOTA_AI_BLACKBOARD == nil then
  _G.DOTA_AI_BLACKBOARD = {
    plan = "farm",
    deadEnemies = 0,
    intent = {},
    lanes = {},
    roshanCalled = 0,
  }
end

function Team.GetBlackboard()
  return _G.DOTA_AI_BLACKBOARD
end

local function gameTime()
  if DotaTime ~= nil then
    local ok, t = pcall(DotaTime)
    if ok and type(t) == "number" then return t end
  end
  return 0
end

-- 上报意图:intent 如 "push_mid" / "roshan" / "defend" / "farm"。
function Team.ReportIntent(bot, intent)
  local bb = Team.GetBlackboard()
  if bot == nil or intent == nil then return end
  local name = ""
  local ok, n = pcall(function() return bot:GetUnitName() end)
  if ok then name = n or "" end
  bb.intent[name] = { intent = intent, time = gameTime() }
end

-- 统计当前有多少队友在做同一意图(60s 内有效)。
function Team.CountIntent(intent)
  local bb = Team.GetBlackboard()
  local t = gameTime()
  local n = 0
  for _, v in pairs(bb.intent or {}) do
    if v.intent == intent and (t - (v.time or 0)) < 60 then
      n = n + 1
    end
  end
  return n
end

-- 角色 / 分路分配:按 heroes.lua 的 positions 排序,1 号位先占安全线,
-- 5 号位跟 1 号位,4 号位游走,3 号位优势路,2 号位中路。
-- 分配结果写进黑板,避免 5 个人挤一条线。
function Team.AssignLane(bot, heroData, teamMembers)
  local bb = Team.GetBlackboard()
  if bot == nil or heroData == nil then return "mid" end
  local pos = 5
  if heroData.positions ~= nil and heroData.positions[1] ~= nil then
    pos = heroData.positions[1]
  end
  local lane = heroData.lane or "mid"
  -- 位置决定分路,数据表里已写明;这里只做冲突去重:
  -- 如果同分路已分配给更高优先级的队友,低优先级去野区/游走。
  local key = lane .. "_" .. tostring(pos)
  local name = ""
  local ok, n = pcall(function() return bot:GetUnitName() end)
  if ok then name = n or "" end
  if bb.lanes[key] == nil or bb.lanes[key] == name then
    bb.lanes[key] = name
    return lane
  end
  if pos == 4 or pos == 5 then return "roam" end
  return lane
end

-- 更新敌方阵亡数:由每个 Bot 的快照汇总,供 macro 打盾判断用。
-- 这里用最近快照的敌方可见数做保守估计,不假设全图视野。
function Team.UpdateDeadEnemies(visibleEnemies, totalEnemyHeroes)
  local bb = Team.GetBlackboard()
  totalEnemyHeroes = totalEnemyHeroes or 5
  visibleEnemies = visibleEnemies or 0
  -- 可见敌方越少,推测减员越多,但上限 2,避免过度乐观去打盾。
  local est = totalEnemyHeroes - visibleEnemies
  if est < 0 then est = 0 end
  if est > 2 then est = 2 end
  bb.deadEnemies = est
end

return Team
