-- utility.lua
-- 效用决策层:对每个候选行为算 Desire(0~1),选最高分执行。
-- 权重全部放在 Difficulty / heroData 里,可离线调参后导出,不写死在 if-else 里。
local Team = require(GetScriptDirectory() .. "/engine/team")
local HeroKey = require(GetScriptDirectory() .. "/engine/hero_key")

local Utility = {}

Utility.BEHAVIORS = {
  "retreat", "lasthit", "deny", "push", "farm", "roam",
  "teamfight", "roshan", "heal", "ward",
}

-- 难度调参表:反应延迟越低、阈值越宽松,Bot 越强。
-- v1.1.0 诚实说明:删掉了 v1.0 的 goldMul/xpMul。Lua Bot 脚本没有给 Bot 发
-- 金钱/经验的 API,v1.0 所谓疯狂档金钱经验加成是纸面数字,从未生效。真正的引擎级
-- Unfair 由房间难度控制;本项目 Unfair 只靠反应延迟和决策阈值区分。
-- thinkDelay 由 Core.Think 真正执行节流,不是只写在表里。
Utility.DIFFICULTY = {
  [1] = { name = "easy",    thinkDelay = 0.50, lasthitMargin = 25, retreatHp = 0.55, aggression = 0.35 },
  [2] = { name = "medium",  thinkDelay = 0.30, lasthitMargin = 12, retreatHp = 0.45, aggression = 0.55 },
  [3] = { name = "hard",    thinkDelay = 0.15, lasthitMargin = 5,  retreatHp = 0.35, aggression = 0.75 },
  [4] = { name = "unfair",  thinkDelay = 0.10, lasthitMargin = 0,  retreatHp = 0.25, aggression = 0.95 },
}

function Utility.GetDifficulty(bot)
  -- 优先读真机房间难度 bot:GetDifficulty() (ModDota CDOTA_Bot_Script)。
  -- 返回值映射待真机确认: VDC 控制台命令表说 dota_bot_set_difficulty 是
  -- 0=easy/1=medium/2=hard/3=unfair; 另有实测说 dota_bot_practice_difficulty
  -- 是 1=easy/2=medium/3=hard/4=unfair。两种口径下 4/5 都按 unfair 处理,
  -- 且首次真机运行会把原始值 print 到控制台 (checklist 里让测试者抄下来),
  -- 回来再把映射钉死。旧版完全不读它, 房间难度选什么都按内部默认 3 打。
  -- 模拟的 mock bot 没有 GetDifficulty, pcall 失败后走 _G 兜底, 模拟行为不变。
  if bot ~= nil then
    local ok, raw = pcall(function() return bot:GetDifficulty() end)
    if ok and type(raw) == "number" then
      if _G.DOTA_AI_DIFFICULTY_RAW == nil then
        _G.DOTA_AI_DIFFICULTY_RAW = raw
        print("[dota2ai] lobby difficulty raw GetDifficulty()=" .. tostring(raw))
      end
      local map = { [0] = 1, [1] = 2, [2] = 3, [3] = 4, [4] = 4, [5] = 4 }
      local d = map[raw]
      if d ~= nil then return Utility.DIFFICULTY[d], d end
    end
  end
  local d = 3
  if _G.DOTA_AI_DIFFICULTY ~= nil then d = _G.DOTA_AI_DIFFICULTY end
  if d < 1 then d = 1 end
  if d > 4 then d = 4 end
  return Utility.DIFFICULTY[d], d
end

function Utility.SetDifficulty(level)
  if level == nil then return end
  if level < 1 then level = 1 end
  if level > 4 then level = 4 end
  _G.DOTA_AI_DIFFICULTY = level
end

-- 兵线落点 (简化坐标, 模拟与实战共用): 本路交汇点在己方半场, 推进点在敌方半场。
-- lane 取 "top" / "mid" / "bot", team 取 2 (Radiant) / 3 (Dire)。
-- 兵线交汇点: 两波小兵相遇的中点。注意模拟的兵线是 L 形折线 (见
-- Sim.LANE_PATHS): top/bottom 两段等长, 拐角正好在路径中点 (0.5), 所以
-- 两波兵在拐角相遇 —— top 是 (-6800,6800), bot 是 (6800,-6800),
-- 不是外侧中段 (0,±6800) (兵线只是路过那里, 不交战; v3.2.0 曾误改成
-- (0,±6800), 实测 Sven 在 (0,6800) 站桩 60 秒+、3 次攻击, 已 revert)。
function Utility.GetLaneMeetingPoint(lane, team)
  if lane == "top" then return { x = -6800, y = 6800, z = 0 } end
  if lane == "bot" then return { x = 6800, y = -6800, z = 0 } end
  return { x = 0, y = 0, z = 0 }
end

-- 推进点: 本路敌方那一端 (推线 / 推塔的前进方向, 沿兵线折线走)。
-- 注意: Dire 上单的推进点是 (-6800,-6800) (从拐角沿左边缘向下、去 Radiant
-- 基地), 不是 (-6800,6800) (那就是交汇点本身, 方向为零); 同理 Radiant 下单
-- 是 (6800,6800)。v3.2.0 曾误按“敌方端点”改过, 已 revert。
function Utility.GetLanePushPoint(lane, team)
  if lane == "mid" then
    if team == 3 then return { x = -5000, y = -5000, z = 0 } end
    return { x = 5000, y = 5000, z = 0 }
  end
  if team == 3 then return { x = -6800, y = -6800, z = 0 } end
  return { x = 6800, y = 6800, z = 0 }
end

-- 等兵落点 (棘轮式推进): 平时回本路交汇点; 如果已经在交汇点附近 (300 内)
-- 或已经在线上越过交汇点, 就从当前位置再向敌方半场前进 600 (不超过推进点)。
-- 固定交汇点会让英雄在两波兵之间原地等到卡住 (模拟实测: 两波兵的交战点
-- 固定, 英雄站在那儿有打不完的小兵, 60 秒以上零位移)。
-- 离线保护 (v3.2.0): 棘轮只在线上才成立 —— 如果英雄离本路兵线段超过 1500
-- (游走 / 打架后不在本路), 不要从当前位置再往前顶 600: 目标每帧后移,
-- 英雄每秒只走 300 永远追不上, 一直走到地图外 (模拟实测 Tidehunter 从
-- y=65 一路向东走到 x=116991)。离线时直接回交汇点。
function Utility.GetLaneWaitPoint(bot, snap)
  local lane = Utility.GetHeroLane(bot, snap)
  local team = 2
  if snap ~= nil and snap.team ~= nil then team = snap.team end
  local meet = Utility.GetLaneMeetingPoint(lane, team)
  local push = Utility.GetLanePushPoint(lane, team)
  local loc = nil
  if snap ~= nil then loc = snap.location end
  if loc ~= nil then
    local dx = push.x - meet.x
    local dy = push.y - meet.y
    local plen = math.sqrt(dx * dx + dy * dy)
    if plen > 0 then
      -- 点到兵线段 (meet->push) 的距离: 超过 1500 说明不在本路上。
      local vx, vy = loc.x - meet.x, loc.y - meet.y
      local tt = (vx * dx + vy * dy) / (plen * plen)
      if tt < 0 then tt = 0 elseif tt > 1 then tt = 1 end
      local cx, cy = meet.x + dx * tt, meet.y + dy * tt
      local offLane = math.sqrt((loc.x - cx) * (loc.x - cx) + (loc.y - cy) * (loc.y - cy))
      if offLane > 1500 then
        return meet
      end
      -- 沿兵线方向的投影: >0 表示已在交汇点或越过交汇点。
      local proj = (loc.x - meet.x) * dx + (loc.y - meet.y) * dy
      local ndx = loc.x - meet.x
      local ndy = loc.y - meet.y
      local nearMeet = math.sqrt(ndx * ndx + ndy * ndy) <= 300
      if proj > 0 or nearMeet then
        -- 从当前位置向推进点前进 600, 不越过推进点。
        local remx = push.x - loc.x
        local remy = push.y - loc.y
        if math.sqrt(remx * remx + remy * remy) <= 600 then
          return { x = push.x, y = push.y, z = 0 }
        end
        return { x = loc.x + dx / plen * 600, y = loc.y + dy / plen * 600, z = 0 }
      end
    end
  end
  return meet
end

-- 由 Bot 反推本路: 读 data/heroes 的 lane 字段 (offlane/safelane/support/mid),
-- 按队伍换算成 top/mid/bot。
function Utility.GetHeroLane(bot, snap)
  local lane = "mid"
  local ok, uname = pcall(function() return bot:GetUnitName() end)
  if ok and uname ~= nil then
    local Heroes = require(GetScriptDirectory() .. "/data/heroes")
    local key = HeroKey.FromUnitName(uname)
    local hd = nil
    if key ~= nil then hd = Heroes[key] end
    if hd ~= nil and hd.lane ~= nil then
      local team = 2
      if snap ~= nil and snap.team ~= nil then team = snap.team end
      if hd.lane == "offlane" or hd.lane == "roam" then
        -- roam (游走位, 4 号位) 开局跟劣势路走, 和 offlane 同一路: 旧版这里
        -- 没处理 "roam", 掉到默认 "mid", 7 个 roam 英雄开局全挤去中路
        -- (模拟实测 Earthshaker 整局在中路跟 Zeus 混, 10 分钟没见过敌方英雄)。
        lane = (team == 2) and "top" or "bot"
      elseif hd.lane == "safelane" or hd.lane == "support" then
        lane = (team == 2) and "bot" or "top"
      end
    end
  end
  return lane
end

local function clamp01(x)
  if x < 0 then return 0 end
  if x > 1 then return 1 end
  return x
end

-- snap: perception.Snapshot(bot) 的结果; heroData: data/heroes.lua 的条目。
-- 返回 scores 表 + 最优行为名。所有分数都可解释、可调参。
function Utility.Score(bot, snap, heroData, gameTime)
  local diff = Utility.GetDifficulty(bot)
  local scores = {}
  local t = gameTime or 0
  if snap == nil then
    scores.retreat = 0
    scores.lasthit = 0
    scores.farm = 0.5
    return scores, "farm"
  end

  local hp = snap.healthPct or 1
  local mp = snap.manaPct or 1
  local nE = snap.numEnemies or 0
  local nA = snap.numAllies or 0
  local role = 5
  if heroData ~= nil and heroData.positions ~= nil and heroData.positions[1] ~= nil then
    role = heroData.positions[1]
  end

  -- 撤退:血量越低、敌多我少、离塔越远,分数越高。血量高于阈值时为 0。
  local retreat = 0
  if hp < diff.retreatHp then
    retreat = clamp01((diff.retreatHp - hp) / math.max(0.05, diff.retreatHp))
    if nE > nA then retreat = retreat + 0.25 end
    if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist < 500 then
      retreat = retreat + 0.2
    end
  end
  if nE >= 3 and nA <= 1 and hp < 0.6 then retreat = math.max(retreat, 0.8) end
  scores.retreat = clamp01(retreat)

  -- 回家补给:血/蓝双低且无敌方威胁时才考虑,避免残血还赖线。
  local heal = 0
  if (hp < 0.3 or mp < 0.15) and nE == 0 then heal = 0.85 end
  if hp < 0.2 then heal = 0.95 end
  scores.heal = heal

  -- 补刀:有可补小兵时高分;难度越低,容错 margin 越大,反而更晚出手。
  local lasthit = 0
  if snap.lastHittable ~= nil and #snap.lastHittable > 0 then
    lasthit = 0.9
    if nE > 0 then lasthit = lasthit - 0.15 end
  end
  scores.lasthit = clamp01(lasthit)

  -- 反补:己方小兵半血以下。
  local deny = 0
  if snap.deniable ~= nil and #snap.deniable > 0 then deny = 0.55 end
  scores.deny = deny

  -- 推线/推塔:对线期后、有兵线优势、敌方少人时推;1/2 号位权重更高。
  local push = 0
  if t > 600 then
    push = 0.35 + diff.aggression * 0.2
    if nE == 0 then push = push + 0.25 end
    if snap.nearbyEnemyTowers ~= nil and #snap.nearbyEnemyTowers > 0 then
      push = push + 0.1
    end
    if role == 1 or role == 2 then push = push + 0.1 end
  end
  scores.push = clamp01(push)

  -- 打野/刷钱:没兵可补、没团可打时的默认行为;1 号位权重最高。
  local farm = 0.45
  if role == 1 then farm = farm + 0.2 end
  if role == 4 or role == 5 then farm = farm - 0.2 end
  if #snap.lastHittable == 0 and nE == 0 then farm = farm + 0.1 end
  scores.farm = clamp01(farm)

  -- 游走:4/5 号位、6 分钟后、有大招/控制时才游走。
  local roam = 0
  if (role == 4 or role == 5) and t > 360 and nE == 0 then roam = 0.5 end
  scores.roam = clamp01(roam)

  -- 参团:敌我人数接近或我方占优、血量健康时参团;劣势不硬接。
  local teamfight = 0
  if nE > 0 then
    local advantage = (nA + 1) - nE
    if advantage >= 0 and hp > 0.5 then
      teamfight = 0.55 + advantage * 0.12 + diff.aggression * 0.15
    elseif advantage >= 1 then
      teamfight = 0.7
    end
  end
  -- v1.1.0 连招窗口:队友刚开先手大(5 秒内),参团分 +0.25,去窗口位置跟进。
  -- 黑板上没窗口时这项为 0,不影响平时的打分。
  if Team.IsComboWindowActive() then
    teamfight = teamfight + 0.25
  end
  scores.teamfight = clamp01(teamfight)

  -- 打肉山:20 分钟后、我方人数占优、敌方减员时才考虑;不靠定时器硬打。
  local roshan = 0
  if t > 1200 and nE == 0 and (nA + 1) >= 3 and hp > 0.6 then
    roshan = 0.4
  end
  scores.roshan = clamp01(roshan)

  -- 插眼:辅助、身上有眼时才插(由 micro 层判断是否带眼)。
  -- v1.1.0:分数提到 0.4,高于 4/5 号位无敌无刀时的刷钱分(0.35),否则 ward
  -- 永远赢不了、Core 里的插眼分支是死代码。
  scores.ward = 0
  if (role == 4 or role == 5) and t > 60 then scores.ward = 0.4 end

  -- 选最高分;撤退/回家是硬优先级,分数超过 0.8 直接胜出。
  local best = "farm"
  local bestScore = -1
  if scores.retreat >= 0.8 then return scores, "retreat" end
  if scores.heal >= 0.9 then return scores, "heal" end
  for _, name in ipairs(Utility.BEHAVIORS) do
    local s = scores[name] or 0
    if s > bestScore then
      bestScore = s
      best = name
    end
  end
  return scores, best
end

return Utility
