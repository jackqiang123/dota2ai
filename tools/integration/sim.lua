-- sim.lua -- 5v5 全局模拟器: 最小世界模型 (Lua 5.1 语法兼容)。
-- 职责: 地图 / 兵线 / 防御塔 / 基地 / 经济 / 击杀复活 / 野区 / 肉山 / 视野。
-- 不依赖任何 Valve 全局; Valve API 的绑定在 valve_api.lua 里。
-- 坐标系沿用 Dota 习惯: Radiant 泉水 (-7000,-7000), Dire 泉水 (7000,7000)。
-- 三路: mid 为对角线, top 沿上边缘, bot 沿下边缘。
local Sim = {}

Sim.TEAM_RADIANT = 2
Sim.TEAM_DIRE = 3
Sim.TEAM_NEUTRAL = 0

Sim.MAP_HALF = 7000
Sim.WAVE_INTERVAL = 30
Sim.CREEP_SPEED = 325
Sim.TOWER_RANGE = 700
Sim.VISION_HERO = 1800
Sim.VISION_TOWER = 1200
Sim.VISION_CREEP = 900
Sim.VISION_WARD = 1200

-- 每路折线 (从 Radiant 基地到 Dire 基地)。
Sim.LANE_PATHS = {
  top = { { -6800, -6800 }, { -6800, 6800 }, { 6800, 6800 } },
  mid = { { -6800, -6800 }, { 6800, 6800 } },
  bot = { { -6800, -6800 }, { 6800, -6800 }, { 6800, 6800 } },
}
-- 每队每路 3 座塔在折线上的位置 (从己方基地起算的比例)。
-- 注意: 三座塔必须全在己方半场 (比例 < 0.5 对 Radiant, > 0.5 对 Dire),
-- 否则高地塔会落在敌方半场、挡住自家兵线 (2026-11-09 模拟实测抓包)。
Sim.TOWER_FRACS = {
  [2] = { 0.31, 0.39, 0.46 },
  [3] = { 0.69, 0.61, 0.54 },
}
Sim.TOWER_HP = { 1300, 1600, 1900 }
Sim.TOWER_DAMAGE = 110
Sim.ANCIENT_HP = 5000

-- 野区营地 (中立野怪刷新点); farm 模式的 (-2500,-2500)/(2500,2500) 各有一处。
Sim.CAMPS = {
  { x = -2500, y = -2500, team = 2 },
  { x = -4000, y = 0, team = 2 },
  { x = 0, y = -4000, team = 2 },
  { x = 2500, y = 2500, team = 3 },
  { x = 4000, y = 0, team = 3 },
  { x = 0, y = 4000, team = 3 },
}
Sim.CAMP_RESPAWN = 60

-- 肉山坑: Radiant 侧先开, 每次重生换边。
Sim.ROSHAN_PITS = {
  { x = -1800, y = -1700 },
  { x = 1800, y = 1700 },
}
Sim.ROSHAN_HP = 6000
Sim.ROSHAN_RESPAWN_MIN = 480
Sim.ROSHAN_RESPAWN_VAR = 120

-- 英雄基础数值 (近似值, 见 README 已知简化)。
Sim.HERO_BASE = {
  axe = { range = 150, dmg = 55, ms = 310, hp = 700, mana = 300, attr = "str" },
  zeus = { range = 380, dmg = 50, ms = 300, hp = 560, mana = 360, attr = "int" },
  lion = { range = 600, dmg = 48, ms = 295, hp = 560, mana = 340, attr = "int" },
  crystal_maiden = { range = 600, dmg = 46, ms = 280, hp = 540, mana = 360, attr = "int" },
  magnus = { range = 150, dmg = 55, ms = 305, hp = 660, mana = 300, attr = "universal" },
  sven = { range = 150, dmg = 58, ms = 310, hp = 680, mana = 300, attr = "str" },
  dazzle = { range = 550, dmg = 50, ms = 305, hp = 560, mana = 340, attr = "universal" },
  enigma = { range = 550, dmg = 50, ms = 300, hp = 580, mana = 320, attr = "universal" },
  faceless_void = { range = 150, dmg = 56, ms = 300, hp = 640, mana = 300, attr = "agi" },
  huskar = { range = 400, dmg = 52, ms = 300, hp = 650, mana = 300, attr = "str" },
}
Sim.HERO_DEFAULT = { range = 150, dmg = 50, ms = 300, hp = 600, mana = 320, attr = "str" }

function Sim.dist(x1, y1, x2, y2)
  local dx = x2 - x1
  local dy = y2 - y1
  return math.sqrt(dx * dx + dy * dy)
end

function Sim.fountain(team)
  if team == Sim.TEAM_RADIANT then return -7000, -7000 end
  return 7000, 7000
end

function Sim.enemyTeam(team)
  if team == Sim.TEAM_RADIANT then return Sim.TEAM_DIRE end
  return Sim.TEAM_RADIANT
end

-- 折线总长与按比例取点。
local function pathLength(pts)
  local len = 0
  for i = 2, #pts do
    len = len + Sim.dist(pts[i - 1][1], pts[i - 1][2], pts[i][1], pts[i][2])
  end
  return len
end

function Sim.lanePoint(lane, frac)
  local pts = Sim.LANE_PATHS[lane]
  local total = pathLength(pts)
  local target = frac * total
  local walked = 0
  for i = 2, #pts do
    local seg = Sim.dist(pts[i - 1][1], pts[i - 1][2], pts[i][1], pts[i][2])
    if walked + seg >= target then
      local f = 0
      if seg > 0 then f = (target - walked) / seg end
      return pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f,
        pts[i - 1][2] + (pts[i][2] - pts[i - 1][2]) * f
    end
    walked = walked + seg
  end
  return pts[#pts][1], pts[#pts][2]
end

function Sim.laneLength(lane)
  return pathLength(Sim.LANE_PATHS[lane])
end

-- 升级所需经验 (近似曲线, 25 级约 16500 总经验)。
function Sim.xpForLevel(level)
  return 120 + level * 45
end

function Sim.respawnTime(level)
  local t = 6 + level * 2.5
  if t > 60 then t = 60 end
  return t
end

function Sim.new(cfg)
  local world = {
    time = 0,
    dt = cfg.tick or 1.0,
    duration = (cfg.minutes or 40) * 60,
    seed = cfg.seed or 42,
    heroes = {},
    creeps = {},
    towers = {},
    ancients = {},
    wards = {},
    camps = {},
    roshan = nil,
    wave = 0,
    nextWaveAt = 0,
    nextId = 1,
    winner = nil,
    endReason = nil,
    teamKills = { [2] = 0, [3] = 0 },
    teamTowers = { [2] = 0, [3] = 0 },
    teamRoshan = { [2] = 0, [3] = 0 },
    teamfights = {},
    events = {},
    log = {},
  }
  -- 防御塔与基地。
  for _, team in ipairs({ 2, 3 }) do
    for _, lane in ipairs({ "top", "mid", "bot" }) do
      for tier = 1, 3 do
        local frac = Sim.TOWER_FRACS[team][tier]
        local x, y = Sim.lanePoint(lane, frac)
        world.towers[#world.towers + 1] = {
          id = world.nextId, kind = "tower", team = team, lane = lane, tier = tier,
          x = x, y = y, hp = Sim.TOWER_HP[tier], maxHp = Sim.TOWER_HP[tier],
          alive = true, attackCd = 0, dmg = Sim.TOWER_DAMAGE, range = Sim.TOWER_RANGE,
        }
        world.nextId = world.nextId + 1
      end
    end
    local fx, fy = Sim.fountain(team)
    world.ancients[#world.ancients + 1] = {
      id = world.nextId, kind = "ancient", team = team,
      x = fx, y = fy, hp = Sim.ANCIENT_HP, maxHp = Sim.ANCIENT_HP,
      alive = true, attackCd = 0, dmg = 0, range = 0,
    }
    world.nextId = world.nextId + 1
  end
  -- 野区营地。
  for i, c in ipairs(Sim.CAMPS) do
    world.camps[i] = { x = c.x, y = c.y, team = c.team, alive = false, respawnAt = 0 }
  end
  -- 肉山: 开局在 Radiant 侧坑。
  world.roshan = {
    id = world.nextId, kind = "roshan", team = 0,
    x = Sim.ROSHAN_PITS[1].x, y = Sim.ROSHAN_PITS[1].y,
    hp = Sim.ROSHAN_HP, maxHp = Sim.ROSHAN_HP,
    alive = true, attackCd = 0, dmg = 60, range = 300, pit = 1, respawnAt = nil,
  }
  world.nextId = world.nextId + 1
  -- 英雄。
  for _, h in ipairs(cfg.heroes) do
    local base = Sim.HERO_BASE[h.key] or Sim.HERO_DEFAULT
    local fx, fy = Sim.fountain(h.team)
    local hero = {
      id = world.nextId, kind = "hero", key = h.key, team = h.team, pos = h.pos or 5,
      lane = h.lane or "mid",
      x = fx, y = fy, hp = base.hp, maxHp = base.hp,
      mana = base.mana, maxMana = base.mana,
      level = 1, xp = 0, xpNext = Sim.xpForLevel(1), gold = 600, goldEarned = 600,
      goldSpent = 0, abilityPts = 1,
      baseRange = base.range, baseDmg = base.dmg, baseMs = base.ms,
      baseHp = base.hp, baseMana = base.mana,
      alive = true, respawnAt = nil, aegis = false,
      attackCd = 0, stunUntil = 0, graveUntil = 0,
      dmgMul = 1, dmgMulUntil = 0, bonusDmg = 0, bonusDmgUntil = 0,
      moveTarget = nil, followUnit = nil, attackTarget = nil, attackMoveTarget = nil,
      items = {}, stash = {}, abilities = {}, talents = {},
      lastX = fx, lastY = fy, distance = 0, lastActionAt = 0,
      damagers = {},
      stats = {
        moves = 0, attackOrders = 0, attacksLanded = 0, casts = 0, buys = 0,
        levels = 0, kills = 0, deaths = 0, assists = 0, lasthits = 0, denies = 0,
        damageDealt = 0, wards = 0, roshanKills = 0, fightsJoined = 0,
      },
      stuck = nil, fountainCamp = nil,
    }
    world.nextId = world.nextId + 1
    world.heroes[#world.heroes + 1] = hero
  end
  return world
end

function Sim.logEvent(world, text)
  world.events[#world.events + 1] = { time = world.time, text = text }
end

function Sim.heroById(world, id)
  for _, h in ipairs(world.heroes) do
    if h.id == id then return h end
  end
  return nil
end

function Sim.attackDamage(hero, time)
  local dmg = hero.baseDmg + 4 * (hero.level - 1) + 8 * #hero.items
  if time < (hero.bonusDmgUntil or 0) then dmg = dmg + (hero.bonusDmg or 0) end
  if time < (hero.dmgMulUntil or 0) then dmg = dmg * (hero.dmgMul or 1) end
  return dmg
end

function Sim.attackRange(hero)
  return hero.baseRange
end

function Sim.moveSpeed(hero)
  return hero.baseMs
end

function Sim.attackInterval(hero)
  if hero.baseRange > 150 then return 1.5 end
  return 1.7
end

function Sim.maxHp(hero)
  return hero.baseHp + 105 * (hero.level - 1) + 100 * #hero.items
end

function Sim.maxMana(hero)
  return hero.baseMana + 45 * (hero.level - 1)
end

-- 朝目标点移动一 tick, 返回是否到达。
local function moveToward(unit, tx, ty, speed, dt)
  local d = Sim.dist(unit.x, unit.y, tx, ty)
  if d < 1 then return true end
  local step = speed * dt
  if step >= d then
    unit.x, unit.y = tx, ty
  else
    unit.x = unit.x + (tx - unit.x) / d * step
    unit.y = unit.y + (ty - unit.y) / d * step
  end
  -- 地图边界 (v3.2.0): 钳制在 ±7500 内, 防止指令目标在地图外时英雄一路
  -- 走出世界 (实测 Tidehunter 走到 x=116991)。真机地图本身有边界。
  if unit.x > 7500 then unit.x = 7500 elseif unit.x < -7500 then unit.x = -7500 end
  if unit.y > 7500 then unit.y = 7500 elseif unit.y < -7500 then unit.y = -7500 end
  return step >= d
end

function Sim.giveGold(hero, amount)
  hero.gold = hero.gold + amount
  hero.goldEarned = hero.goldEarned + amount
end

function Sim.giveXp(world, hero, amount)
  if hero == nil or not hero.alive then return end
  hero.xp = hero.xp + amount
  while hero.level < 25 and hero.xp >= hero.xpNext do
    hero.xp = hero.xp - hero.xpNext
    hero.level = hero.level + 1
    hero.xpNext = Sim.xpForLevel(hero.level)
    hero.abilityPts = hero.abilityPts + 1
    hero.maxHp = Sim.maxHp(hero)
    hero.maxMana = Sim.maxMana(hero)
    hero.hp = math.min(hero.maxHp, hero.hp + 105)
    hero.mana = math.min(hero.maxMana, hero.mana + 45)
    hero.stats.levels = hero.stats.levels + 1
    Sim.logEvent(world, hero.key .. " 升到 " .. hero.level .. " 级")
  end
end

-- 附近的友方英雄 (用于经验/助攻分享)。
local function alliesNear(world, x, y, team, radius, exclude)
  local out = {}
  for _, h in ipairs(world.heroes) do
    if h.team == team and h.alive and h ~= exclude then
      if Sim.dist(x, y, h.x, h.y) <= radius then out[#out + 1] = h end
    end
  end
  return out
end

-- 通用伤害结算: 目标可以是英雄 / 小兵 / 塔 / 基地 / 肉山。
-- source 为造成伤害的单位 (英雄/小兵/塔, 可为 nil)。
function Sim.damage(world, target, amount, source)
  if target == nil or not target.alive then return false end
  if target.kind == "hero" and world.time < (target.graveUntil or 0) and target.hp - amount < 1 then
    target.hp = 1
    return false
  end
  local variance = 0.9 + math.random() * 0.2
  local dmg = amount * variance
  target.hp = target.hp - dmg
  if source ~= nil and source.kind == "hero" then
    source.stats.damageDealt = source.stats.damageDealt + dmg
  end
  if target.kind == "hero" and source ~= nil and source.kind == "hero" and source.team ~= target.team then
    target.damagers[source.id] = world.time
  end
  if target.hp > 0 then return false end
  target.hp = 0
  target.alive = false
  if target.kind == "hero" then
    target.stats.deaths = target.stats.deaths + 1
    target.moveTarget, target.followUnit, target.attackTarget, target.attackMoveTarget = nil, nil, nil, nil
    local killer = nil
    if source ~= nil and source.kind == "hero" and source.team ~= target.team then killer = source end
    if killer ~= nil then
      killer.stats.kills = killer.stats.kills + 1
      world.teamKills[killer.team] = world.teamKills[killer.team] + 1
      local bounty = 200 + 25 * target.level
      Sim.giveGold(killer, bounty)
      Sim.giveXp(world, killer, 100 + 20 * target.level)
      for _, ally in ipairs(alliesNear(world, target.x, target.y, killer.team, 1200, killer)) do
        Sim.giveXp(world, ally, 50 + 10 * target.level)
      end
      -- 助攻: 15 秒内打过受害者的队友。
      for hid, t in pairs(target.damagers) do
        if hid ~= killer.id and world.time - t < 15 then
          local a = Sim.heroById(world, hid)
          if a ~= nil and a.team == killer.team then a.stats.assists = a.stats.assists + 1 end
        end
      end
      -- 团战参与: 击杀点 1500 内双方英雄都算参战。
      local parts = {}
      for _, h in ipairs(world.heroes) do
        if h.alive and Sim.dist(target.x, target.y, h.x, h.y) <= 1500 then
          h.stats.fightsJoined = h.stats.fightsJoined + 1
          parts[#parts + 1] = h.key
        end
      end
      world.teamfights[#world.teamfights + 1] = { time = world.time, victim = target.key, killer = killer.key, parts = parts }
      Sim.logEvent(world, killer.key .. " 击杀 " .. target.key .. " (团战 " .. #parts .. " 人)")
    else
      Sim.logEvent(world, target.key .. " 死亡 (无击杀者)")
    end
    if target.aegis then
      target.aegis = false
      target.respawnAt = world.time + 3
      Sim.logEvent(world, target.key .. " 的不朽之守护触发, 3 秒后复活")
    else
      target.respawnAt = world.time + Sim.respawnTime(target.level)
    end
    target.damagers = {}
  elseif target.kind == "creep" then
    local killerHero = nil
    if source ~= nil and source.kind == "hero" then killerHero = source end
    if killerHero ~= nil and killerHero.team == target.team then
      -- 反补: 己方英雄反补己方小兵。
      killerHero.stats.denies = killerHero.stats.denies + 1
      for _, e in ipairs(alliesNear(world, target.x, target.y, Sim.enemyTeam(target.team), 1200, nil)) do
        Sim.giveXp(world, e, math.floor(target.xpValue * 0.25))
      end
    elseif killerHero ~= nil then
      killerHero.stats.lasthits = killerHero.stats.lasthits + 1
      Sim.giveGold(killerHero, target.bounty)
      Sim.giveXp(world, killerHero, target.xpValue)
      for _, ally in ipairs(alliesNear(world, target.x, target.y, killerHero.team, 1200, killerHero)) do
        Sim.giveXp(world, ally, target.xpValue)
      end
    else
      -- 被小兵/塔击杀: 敌方附近英雄分经验。
      for _, e in ipairs(alliesNear(world, target.x, target.y, Sim.enemyTeam(target.team), 1200, nil)) do
        Sim.giveXp(world, e, target.xpValue)
      end
    end
    if target.camp ~= nil then
      local camp = world.camps[target.camp]
      if camp ~= nil then
        local anyAlive = false
        for _, c in ipairs(world.creeps) do
          if c ~= target and c.alive and c.camp == target.camp then anyAlive = true break end
        end
        if not anyAlive then
          camp.alive = false
          camp.respawnAt = world.time + Sim.CAMP_RESPAWN
        end
      end
    end
  elseif target.kind == "tower" then
    world.teamTowers[Sim.enemyTeam(target.team)] = world.teamTowers[Sim.enemyTeam(target.team)] + 1
    Sim.logEvent(world, "防御塔被推掉 (" .. target.lane .. " 路 " .. target.tier .. " 塔, "
      .. (target.team == 2 and "Radiant" or "Dire") .. " 方)")
    if source ~= nil and source.kind == "hero" then
      Sim.giveGold(source, 150)
      for _, ally in ipairs(alliesNear(world, target.x, target.y, source.team, 1200, source)) do
        Sim.giveGold(ally, 100)
      end
    end
  elseif target.kind == "ancient" then
    world.winner = Sim.enemyTeam(target.team)
    world.endReason = "ancient"
    Sim.logEvent(world, "基地被摧毁, " .. (world.winner == 2 and "Radiant" or "Dire") .. " 获胜")
  elseif target.kind == "roshan" then
    local killerTeam = nil
    if source ~= nil and source.kind == "hero" then killerTeam = source.team end
    if killerTeam == nil then
      -- 附近英雄最多的队伍算作击杀方。
      local c2, c3 = 0, 0
      for _, h in ipairs(world.heroes) do
        if h.alive and Sim.dist(target.x, target.y, h.x, h.y) <= 600 then
          if h.team == 2 then c2 = c2 + 1 else c3 = c3 + 1 end
        end
      end
      if c2 >= c3 then killerTeam = 2 else killerTeam = 3 end
    end
    world.teamRoshan[killerTeam] = world.teamRoshan[killerTeam] + 1
    local holder = nil
    if source ~= nil and source.kind == "hero" then holder = source end
    if holder == nil then
      for _, h in ipairs(world.heroes) do
        if h.team == killerTeam and h.alive then holder = h break end
      end
    end
    if holder ~= nil then
      holder.aegis = true
      holder.stats.roshanKills = holder.stats.roshanKills + 1
    end
    Sim.logEvent(world, (killerTeam == 2 and "Radiant" or "Dire") .. " 击杀 Roshan"
      .. (holder ~= nil and (" (不朽盾: " .. holder.key .. ")") or ""))
    target.respawnAt = world.time + Sim.ROSHAN_RESPAWN_MIN + math.random(0, Sim.ROSHAN_RESPAWN_VAR)
    target.pit = 3 - target.pit
  end
  return true
end

function Sim.heal(world, target, amount)
  if target == nil or not target.alive then return end
  target.hp = math.min(target.maxHp, target.hp + amount)
end

-- 视野: 敌方单位是否在某队的视野内。
function Sim.isVisibleTo(world, team, unit)
  if unit.team == team then return true end
  if unit.team == Sim.TEAM_NEUTRAL then
    -- 中立单位: 任一友方单位靠近即可见。
    for _, h in ipairs(world.heroes) do
      if h.team == team and h.alive and Sim.dist(h.x, h.y, unit.x, unit.y) <= Sim.VISION_HERO then return true end
    end
    return false
  end
  for _, h in ipairs(world.heroes) do
    if h.team == team and h.alive and Sim.dist(h.x, h.y, unit.x, unit.y) <= Sim.VISION_HERO then return true end
  end
  for _, c in ipairs(world.creeps) do
    if c.team == team and c.alive and Sim.dist(c.x, c.y, unit.x, unit.y) <= Sim.VISION_CREEP then return true end
  end
  for _, t in ipairs(world.towers) do
    if t.team == team and t.alive and Sim.dist(t.x, t.y, unit.x, unit.y) <= Sim.VISION_TOWER then return true end
  end
  for _, w in ipairs(world.wards) do
    if w.team == team and Sim.dist(w.x, w.y, unit.x, unit.y) <= Sim.VISION_WARD then return true end
  end
  return false
end

local function spawnCreep(world, team, lane, isSiege)
  local frac = 0.03
  if team == Sim.TEAM_DIRE then frac = 0.97 end
  local x, y = Sim.lanePoint(lane, frac)
  local creep = {
    id = world.nextId, kind = "creep", team = team, lane = lane,
    x = x, y = y, hp = 550, maxHp = 550, dmg = 21, range = 150,
    speed = Sim.CREEP_SPEED, attackCd = 0, alive = true,
    pathFrac = frac, pathDir = 1, bounty = 40, xpValue = 62,
    isSiege = false, isNeutral = false, camp = nil, stunUntil = 0,
  }
  if team == Sim.TEAM_DIRE then creep.pathDir = -1 end
  if isSiege then
    creep.hp, creep.maxHp, creep.dmg, creep.bounty, creep.xpValue = 900, 900, 35, 90, 88
    creep.isSiege = true
  end
  world.nextId = world.nextId + 1
  world.creeps[#world.creeps + 1] = creep
  return creep
end

local function spawnRangedCreep(world, team, lane)
  local c = spawnCreep(world, team, lane, false)
  c.hp, c.maxHp, c.dmg, c.range, c.bounty, c.xpValue = 300, 300, 18, 400, 35, 41
  return c
end

function Sim.spawnWave(world)
  world.wave = world.wave + 1
  local isSiegeWave = (world.wave % 5 == 0)
  for _, team in ipairs({ 2, 3 }) do
    for _, lane in ipairs({ "top", "mid", "bot" }) do
      for _ = 1, 3 do spawnCreep(world, team, lane, false) end
      spawnRangedCreep(world, team, lane)
      if isSiegeWave then spawnCreep(world, team, lane, true) end
    end
  end
end

function Sim.spawnCamp(world, campIdx)
  local camp = world.camps[campIdx]
  if camp == nil or camp.alive then return end
  camp.alive = true
  for i = 1, 3 do
    local creep = {
      id = world.nextId, kind = "creep", team = 0, lane = nil,
      x = camp.x + (i - 2) * 120, y = camp.y + ((i % 2) * 2 - 1) * 80,
      hp = 500, maxHp = 500, dmg = 22, range = 150,
      speed = 0, attackCd = 0, alive = true,
      pathFrac = nil, pathDir = 0, bounty = 45, xpValue = 60,
      isSiege = false, isNeutral = true, camp = campIdx, stunUntil = 0,
      homeX = camp.x, homeY = camp.y,
    }
    world.nextId = world.nextId + 1
    world.creeps[#world.creeps + 1] = creep
  end
end

-- 最近的敌方单位 (小兵/英雄/塔/肉山/基地), 供小兵与防御塔 AI 用。
local function nearestEnemyUnit(world, unit, maxRange, includeTowers)
  local best, bestD = nil, 1e9
  local function consider(u, d)
    if u ~= nil and u.alive and u.team ~= unit.team and d <= maxRange and d < bestD then
      best, bestD = u, d
    end
  end
  for _, c in ipairs(world.creeps) do
    if c.alive then consider(c, Sim.dist(unit.x, unit.y, c.x, c.y)) end
  end
  for _, h in ipairs(world.heroes) do
    if h.alive then consider(h, Sim.dist(unit.x, unit.y, h.x, h.y)) end
  end
  if includeTowers then
    for _, t in ipairs(world.towers) do
      if t.alive then consider(t, Sim.dist(unit.x, unit.y, t.x, t.y)) end
    end
    local r = world.roshan
    if r ~= nil and r.alive then consider(r, Sim.dist(unit.x, unit.y, r.x, r.y)) end
  end
  return best, bestD
end

local function nearestEnemyTowerOrAncient(world, unit, maxRange)
  local best, bestD = nil, 1e9
  for _, t in ipairs(world.towers) do
    if t.alive and t.team ~= unit.team then
      local d = Sim.dist(unit.x, unit.y, t.x, t.y)
      if d <= maxRange and d < bestD then best, bestD = t, d end
    end
  end
  for _, a in ipairs(world.ancients) do
    if a.alive and a.team ~= unit.team then
      local d = Sim.dist(unit.x, unit.y, a.x, a.y)
      if d <= maxRange and d < bestD then best, bestD = a, d end
    end
  end
  return best, bestD
end

-- 一次世界步进 (dt 秒): 移动 / 攻击 / 小兵 AI / 塔 AI / 肉山 / 回复 / 复活 / 经济。
function Sim.step(world)
  local dt = world.dt
  world.time = world.time + dt
  local t = world.time

  if t >= world.nextWaveAt then
    Sim.spawnWave(world)
    world.nextWaveAt = world.nextWaveAt + Sim.WAVE_INTERVAL
  end
  for i, camp in ipairs(world.camps) do
    if not camp.alive and t >= (camp.respawnAt or 0) then
      Sim.spawnCamp(world, i)
    end
  end
  -- 肉山重生 (换边)。
  local r = world.roshan
  if r ~= nil and not r.alive and r.respawnAt ~= nil and t >= r.respawnAt then
    r.alive = true
    r.hp = r.maxHp
    r.x = Sim.ROSHAN_PITS[r.pit].x
    r.y = Sim.ROSHAN_PITS[r.pit].y
    r.respawnAt = nil
    Sim.logEvent(world, "Roshan 在 " .. (r.pit == 1 and "Radiant" or "Dire") .. " 侧重生")
  end
  -- 眼位过期。
  for i = #world.wards, 1, -1 do
    if t >= world.wards[i].expiresAt then table.remove(world.wards, i) end
  end

  -- ---- 英雄行动 ----
  for _, h in ipairs(world.heroes) do
    if h.alive then
      local stunned = t < (h.stunUntil or 0)
      if h.attackCd > 0 then h.attackCd = h.attackCd - dt end
      if not stunned then
        local at = h.attackTarget
        if at ~= nil and (not at.alive) then h.attackTarget, at = nil, nil end
        local acted = false
        if at ~= nil then
          local d = Sim.dist(h.x, h.y, at.x, at.y)
          local range = Sim.attackRange(h)
          if at.kind == "tower" or at.kind == "ancient" or at.kind == "roshan" then range = range + 100 end
          if d <= range then
            if h.attackCd <= 0 then
              Sim.damage(world, at, Sim.attackDamage(h, t), h)
              h.attackCd = Sim.attackInterval(h)
              h.stats.attacksLanded = h.stats.attacksLanded + 1
            end
            acted = true
          else
            moveToward(h, at.x, at.y, Sim.moveSpeed(h), dt)
            acted = true
          end
        elseif h.attackMoveTarget ~= nil then
          local amt = h.attackMoveTarget
          local enemy = nearestEnemyUnit(world, h, Sim.attackRange(h), true)
          if enemy ~= nil then
            if h.attackCd <= 0 then
              Sim.damage(world, enemy, Sim.attackDamage(h, t), h)
              h.attackCd = Sim.attackInterval(h)
              h.stats.attacksLanded = h.stats.attacksLanded + 1
            end
            acted = true
          else
            if moveToward(h, amt.x, amt.y, Sim.moveSpeed(h), dt) then
              h.attackMoveTarget = nil
            end
            acted = true
          end
        elseif h.followUnit ~= nil then
          local u = h.followUnit
          if u.alive ~= false then
            local d = Sim.dist(h.x, h.y, u.x, u.y)
            if d > 150 then moveToward(h, u.x, u.y, Sim.moveSpeed(h), dt) end
            acted = true
          else
            h.followUnit = nil
          end
        elseif h.moveTarget ~= nil then
          if moveToward(h, h.moveTarget.x, h.moveTarget.y, Sim.moveSpeed(h), dt) then
            h.moveTarget = nil
          end
          acted = true
        end
        -- 在肉山坑边: 带着去坑的指令就自动打肉山 (mode_roshan 只下移动指令)。
        do
          if r ~= nil and r.alive and Sim.dist(h.x, h.y, r.x, r.y) <= 450 then
            local goingPit = false
            if h.moveTarget ~= nil and Sim.dist(r.x, r.y, h.moveTarget.x, h.moveTarget.y) <= 600 then goingPit = true end
            if h.attackMoveTarget ~= nil and Sim.dist(r.x, r.y, h.attackMoveTarget.x, h.attackMoveTarget.y) <= 600 then goingPit = true end
            if h.attackTarget == r then goingPit = true end
            if goingPit and h.attackCd <= 0 then
              Sim.damage(world, r, Sim.attackDamage(h, t), h)
              h.attackCd = Sim.attackInterval(h)
              h.stats.attacksLanded = h.stats.attacksLanded + 1
            end
          end
        end
      end
      -- 回复: 基础 + 泉水。
      local fx, fy = Sim.fountain(h.team)
      local inFountain = Sim.dist(h.x, h.y, fx, fy) <= 800
      local hpRegen = (3 + 0.5 * h.level) * dt
      local manaRegen = (1.5 + 0.1 * h.level) * dt
      if inFountain then
        hpRegen = h.maxHp * 0.10 * dt
        manaRegen = h.maxMana * 0.10 * dt
      end
      h.hp = math.min(h.maxHp, h.hp + hpRegen)
      h.mana = math.min(h.maxMana, h.mana + manaRegen)
      -- 被动经济。
      Sim.giveGold(h, 2.0 * dt)
      Sim.giveXp(world, h, 0.25 * dt)
      -- 位移统计。
      h.distance = h.distance + Sim.dist(h.lastX, h.lastY, h.x, h.y)
      h.lastX, h.lastY = h.x, h.y
    end
  end

  -- ---- 小兵 AI ----
  for _, c in ipairs(world.creeps) do
    if c.alive then
      if c.attackCd > 0 then c.attackCd = c.attackCd - dt end
      local stunned = t < (c.stunUntil or 0)
      if not stunned then
        if c.isNeutral or c.summoned then
          -- 中立野怪与召唤物: 原地迎敌, 不沿兵线走 (召唤物没有 lane)。
          local enemy = nearestEnemyUnit(world, c, 450, false)
          if enemy ~= nil and c.attackCd <= 0 then
            Sim.damage(world, enemy, c.dmg, c)
            c.attackCd = 1.2
          end
        elseif c.lane == nil then
          -- 无兵线归属的小兵: 原地不动, 只打靠近的敌人。
          local enemy = nearestEnemyUnit(world, c, 450, false)
          if enemy ~= nil and c.attackCd <= 0 then
            Sim.damage(world, enemy, c.dmg, c)
            c.attackCd = 1.2
          end
        else
          local enemy = nearestEnemyUnit(world, c, 550, false)
          if enemy == nil then
            enemy = nearestEnemyTowerOrAncient(world, c, 700)
          end
          if enemy ~= nil then
            local d = Sim.dist(c.x, c.y, enemy.x, enemy.y)
            if d <= c.range then
              if c.attackCd <= 0 then
                Sim.damage(world, enemy, c.dmg, c)
                c.attackCd = 1.2
              end
            else
              moveToward(c, enemy.x, enemy.y, c.speed, dt)
            end
          else
            -- 沿兵线推进。
            local len = Sim.laneLength(c.lane)
            c.pathFrac = c.pathFrac + c.pathDir * c.speed * dt / len
            if c.pathFrac < 0.02 then c.pathFrac = 0.02 end
            if c.pathFrac > 0.98 then c.pathFrac = 0.98 end
            c.x, c.y = Sim.lanePoint(c.lane, c.pathFrac)
          end
        end
      end
    end
  end

  -- ---- 防御塔 AI ----
  for _, tw in ipairs(world.towers) do
    if tw.alive then
      if tw.attackCd > 0 then tw.attackCd = tw.attackCd - dt end
      if tw.attackCd <= 0 then
        local target = nil
        local bestD = 1e9
        for _, c in ipairs(world.creeps) do
          if c.alive and c.team ~= tw.team then
            local d = Sim.dist(tw.x, tw.y, c.x, c.y)
            if d <= tw.range and d < bestD then target, bestD = c, d end
          end
        end
        if target == nil then
          for _, h in ipairs(world.heroes) do
            if h.alive and h.team ~= tw.team then
              local d = Sim.dist(tw.x, tw.y, h.x, h.y)
              if d <= tw.range and d < bestD then target, bestD = h, d end
            end
          end
        end
        if target ~= nil then
          Sim.damage(world, target, tw.dmg, tw)
          tw.attackCd = 1.0
        end
      end
    end
  end

  -- ---- 肉山 AI ----
  if r ~= nil and r.alive then
    if r.attackCd > 0 then r.attackCd = r.attackCd - dt end
    if r.attackCd <= 0 then
      local target, bestD = nil, 1e9
      for _, h in ipairs(world.heroes) do
        if h.alive then
          local d = Sim.dist(r.x, r.y, h.x, h.y)
          if d <= r.range and d < bestD then target, bestD = h, d end
        end
      end
      if target ~= nil then
        Sim.damage(world, target, r.dmg, r)
        r.attackCd = 1.5
      end
    end
  end

  -- ---- 复活 ----
  for _, h in ipairs(world.heroes) do
    if not h.alive and h.respawnAt ~= nil and t >= h.respawnAt then
      h.alive = true
      h.respawnAt = nil
      local fx, fy = Sim.fountain(h.team)
      h.x, h.y = fx, fy
      h.hp = h.maxHp
      h.mana = h.maxMana
      h.moveTarget, h.followUnit, h.attackTarget, h.attackMoveTarget = nil, nil, nil, nil
      h.lastX, h.lastY = fx, fy
      Sim.logEvent(world, h.key .. " 复活")
    end
  end

  -- 清理死掉的小兵 (保留尸体一小会儿没有意义, 直接清)。
  for i = #world.creeps, 1, -1 do
    if not world.creeps[i].alive then table.remove(world.creeps, i) end
  end

  -- 胜负: 基地掉落由 Sim.damage 直接判; 时间到按推塔/人头判。
  if world.winner == nil and t >= world.duration then
    local rt, dtw = world.teamTowers[2], world.teamTowers[3]
    local rk, dk = world.teamKills[2], world.teamKills[3]
    if rt ~= dtw then
      world.winner = (rt > dtw) and 2 or 3
    elseif rk ~= dk then
      world.winner = (rk > dk) and 2 or 3
    else
      world.winner = 0
    end
    world.endReason = "time"
    Sim.logEvent(world, "时间到, 推塔 " .. rt .. ":" .. dtw .. " 人头 " .. rk .. ":" .. dk)
  end
end

return Sim
