-- valve_api.lua -- 模拟 Valve Bot API, 绑定到 sim.lua 的世界模型。
-- 全部按真实 API 语义实现: GetNearby* 只返回视野内单位; Action_* 真正改变世界
-- (移动改位置、攻击扣血、技能扣蓝进 CD、买装扣钱进背包、插眼改视野)。
-- 数值 (物品价格、技能蓝耗/CD/伤害/射程) 为近似值, 见 README 已知简化。
-- Lua 5.1 语法兼容。
local Sim = require("sim")

local Valve = {}

-- ---- 物品价格 (近似真实价格) ----
Valve.ITEM_COSTS = {
  item_tango = 90, item_flask = 110, item_clarity = 50,
  item_quelling_blade = 130, item_wraith_band = 250, item_bracer = 240,
  item_null_talisman = 240, item_bottle = 675, item_phase_boots = 1500,
  item_power_treads = 1400, item_tranquil_boots = 925, item_arcane_boots = 1300,
  item_magic_wand = 450, item_ward_observer = 50, item_ward_sentry = 75,
  item_vanguard = 1825, item_blade_mail = 2100, item_blink = 2250,
  item_overwhelming_blink = 4200, item_black_king_bar = 4050, item_heart = 5200,
  item_assault = 5200, item_satanic = 5050, item_abyssal_blade = 6250,
  item_aghanims_scepter = 4200, item_aghanims_shard = 1400, item_shivas_guard = 4700,
  item_crimson_guard = 3600, item_pipe_of_insight = 3000, item_force_staff = 2200,
  item_euls_scepter_of_divinity = 2725, item_lotus_orb = 3850, item_glimmer_cape = 1950,
  item_aether_lens = 2200, item_octarine_core = 4800, item_scythe_of_vyse = 5650,
  item_travel_boots = 2500, item_armlet = 2500, item_dragon_lance = 1900,
  item_echo_sabre = 2700, item_maelstrom = 2800, item_mjollnir = 5500,
  item_manta = 4600, item_butterfly = 5200, item_daedalus = 5500,
  item_desolator = 3400, item_harpoon = 3200, item_heavens_halberd = 3600,
  item_kaya_and_sange = 4100, item_sange_and_yasha = 4100, item_moon_shard = 3000,
  item_refresher_orb = 5000, item_solar_crest = 2800, item_ghost_scepter = 1500,
  item_aeon_disk = 3000,
}

-- ---- 技能数值 (近似值): mana 蓝耗, cd 秒, dmg 伤害, range 射程,
-- kind: unit 单体 / location 地点 / none 自身 / global 全图 / heal 治疗 /
--       buff 增益 / summon 召唤 / execute 斩杀 / blink 位移。
-- control: 控制秒数; hpCost: 自身扣血; hpCostPct: 按当前血量比例扣血。
Valve.ABILITY_DATA = {
  axe_berserkers_call = { mana = 80, cd = 14, dmg = 80, range = 300, kind = "none", control = 1.5 },
  axe_battle_hunger = { mana = 75, cd = 12, dmg = 60, range = 700, kind = "unit" },
  axe_counter_helix = { passive = true },
  axe_culling_blade = { mana = 60, cd = 10, dmg = 150, range = 150, kind = "execute" },
  zeus_arc_lightning = { mana = 65, cd = 2, dmg = 100, range = 700, kind = "unit" },
  zeus_lightning_bolt = { mana = 90, cd = 6, dmg = 200, range = 700, kind = "unit" },
  zeus_static_field = { passive = true },
  zeus_thundergods_wrath = { mana = 200, cd = 90, dmg = 350, range = 0, kind = "global" },
  lion_impale = { mana = 100, cd = 12, dmg = 120, range = 550, kind = "location", control = 2 },
  lion_voodoo = { mana = 120, cd = 15, dmg = 0, range = 500, kind = "unit", control = 2.5 },
  lion_mana_drain = { mana = 10, cd = 16, dmg = 60, range = 600, kind = "unit" },
  lion_finger_of_death = { mana = 200, cd = 30, dmg = 500, range = 900, kind = "unit" },
  crystal_maiden_crystal_nova = { mana = 100, cd = 12, dmg = 130, range = 700, kind = "location" },
  crystal_maiden_frostbite = { mana = 110, cd = 9, dmg = 100, range = 525, kind = "unit", control = 2 },
  crystal_maiden_brilliance_aura = { passive = true },
  crystal_maiden_freezing_field = { mana = 200, cd = 90, dmg = 250, range = 800, kind = "none", control = 1 },
  magnus_shockwave = { mana = 90, cd = 12, dmg = 150, range = 1200, kind = "location" },
  magnus_empower = { mana = 45, cd = 12, dmg = 0, range = 0, kind = "buff" },
  magnus_skewer = { mana = 80, cd = 12, dmg = 150, range = 900, kind = "location" },
  magnus_reverse_polarity = { mana = 200, cd = 120, dmg = 200, range = 400, kind = "none", control = 2.5 },
  sven_storm_bolt = { mana = 110, cd = 13, dmg = 120, range = 600, kind = "unit", control = 1.5 },
  sven_great_cleave = { passive = true },
  sven_warcry = { mana = 60, cd = 20, dmg = 0, range = 0, kind = "buff" },
  sven_gods_strength = { mana = 100, cd = 90, dmg = 0, range = 0, kind = "buff" },
  dazzle_poison_touch = { mana = 80, cd = 12, dmg = 90, range = 600, kind = "unit" },
  dazzle_shallow_grave = { mana = 90, cd = 18, dmg = 0, range = 800, kind = "heal" },
  dazzle_shadow_wave = { mana = 90, cd = 12, dmg = 120, range = 800, kind = "heal" },
  dazzle_weave = { mana = 100, cd = 30, dmg = 0, range = 800, kind = "buff" },
  enigma_malefice = { mana = 110, cd = 15, dmg = 120, range = 600, kind = "unit", control = 1.5 },
  enigma_demonic_conversion = { mana = 80, cd = 30, dmg = 0, range = 0, kind = "summon" },
  enigma_midnight_pulse = { mana = 100, cd = 25, dmg = 150, range = 700, kind = "location" },
  enigma_black_hole = { mana = 250, cd = 120, dmg = 200, range = 800, kind = "location", control = 3.5 },
  faceless_void_time_walk = { mana = 90, cd = 12, dmg = 0, range = 700, kind = "blink" },
  faceless_void_time_dilation = { mana = 75, cd = 12, dmg = 80, range = 700, kind = "location" },
  faceless_void_time_lock = { passive = true },
  faceless_void_chronosphere = { mana = 150, cd = 120, dmg = 100, range = 700, kind = "location", control = 4 },
  huskar_inner_fire = { mana = 100, cd = 14, dmg = 120, range = 400, kind = "none" },
  huskar_burning_spear = { mana = 0, cd = 2, dmg = 60, range = 400, kind = "unit", hpCost = 15 },
  huskar_berserkers_blood = { passive = true },
  huskar_life_break = { mana = 0, cd = 12, dmg = 250, range = 550, kind = "unit", hpCostPct = 0.3 },
}

-- 未在上表里的技能按 heroes.lua 的类型给缺省值。
local FALLBACK_BY_TYPE = {
  nuke = { mana = 80, cd = 10, dmg = 120, range = 600, kind = "unit" },
  aoe_damage = { mana = 100, cd = 12, dmg = 150, range = 700, kind = "location" },
  aoe_control = { mana = 120, cd = 20, dmg = 120, range = 600, kind = "location", control = 2 },
  point_control = { mana = 100, cd = 14, dmg = 60, range = 600, kind = "unit", control = 2 },
  debuff = { mana = 80, cd = 12, dmg = 80, range = 600, kind = "unit" },
  heal = { mana = 90, cd = 14, dmg = 0, range = 700, kind = "heal" },
  buff = { mana = 60, cd = 16, dmg = 0, range = 0, kind = "buff" },
  blink = { mana = 80, cd = 12, dmg = 0, range = 900, kind = "blink" },
  escape = { mana = 80, cd = 12, dmg = 0, range = 900, kind = "blink" },
  summon = { mana = 80, cd = 30, dmg = 0, range = 0, kind = "summon" },
  passive = { passive = true },
  aura = { passive = true },
  execute = { mana = 80, cd = 12, dmg = 200, range = 200, kind = "execute" },
  channel = { mana = 150, cd = 30, dmg = 150, range = 700, kind = "location", control = 2 },
}

Valve.world = nil
Valve.currentBot = nil
Valve.unknownItems = {}

local function copyTable(t)
  local out = {}
  for k, v in pairs(t) do out[k] = v end
  return out
end

-- 技能数据: 先查精确表, 再按类型给缺省值。
function Valve.abilityData(name, heroKey, slotIdx)
  local d = Valve.ABILITY_DATA[name]
  if d ~= nil then return copyTable(d) end
  local heroes = nil
  local ok, h = pcall(require, "bots/data/heroes")
  if ok then heroes = h end
  local typ = "nuke"
  if heroes ~= nil and heroes[heroKey] ~= nil and heroes[heroKey].abilities ~= nil then
    local ab = heroes[heroKey].abilities[slotIdx or 1]
    if ab ~= nil and ab.type ~= nil then typ = ab.type end
  end
  local fb = FALLBACK_BY_TYPE[typ] or FALLBACK_BY_TYPE.nuke
  return copyTable(fb)
end

-- ---- 技能 / 物品 / 天赋对象 ----

local function makeAbility(world, hero, name, slot, maxLevel, isTalent)
  local data = Valve.abilityData(name, hero.key, slot + 1)
  local ab = {
    _kind = "ability", _world = world, _hero = hero, _name = name,
    _slot = slot, _data = data, level = 0, cd = 0, maxLevel = maxLevel or 4,
    _isTalent = isTalent or false,
  }
  function ab.GetAbilityName(self) return self._name end
  function ab.IsPassive(self) return self._data.passive == true end
  function ab.IsHidden(self) return false end
  function ab.IsNull(self) return false end
  function ab.GetLevel(self) return self.level end
  function ab.GetManaCost(self) return self._data.mana or 0 end
  function ab.GetCastRange(self) return self._data.range or 0 end
  function ab.CanAbilityBeUpgraded(self)
    if self.level >= self.maxLevel then return false end
    local h = self._hero
    if self._isTalent then
      local tier = 10
      if self._slot >= 16 then tier = 25
      elseif self._slot >= 14 then tier = 20
      elseif self._slot >= 12 then tier = 15 end
      return h.level >= tier
    end
    if self._slot == 3 then
      local need = 6
      if self.level == 1 then need = 12 elseif self.level == 2 then need = 18 end
      return h.level >= need
    end
    local need = 1 + self.level * 2
    return h.level >= need
  end
  function ab.IsFullyCastable(self)
    if self.level <= 0 then return false end
    if self._data.passive == true then return false end
    if self.cd > 0 then return false end
    if self._hero.mana < (self._data.mana or 0) then return false end
    if world.time < (self._hero.stunUntil or 0) then return false end
    if not self._hero.alive then return false end
    return true
  end
  return ab
end

local function makeItem(world, hero, name)
  local item = { _kind = "item", _world = world, _hero = hero, _name = name, cd = 0 }
  function item.GetName(self) return self._name end
  function item.IsNull(self) return false end
  function item.IsFullyCastable(self) return self.cd <= 0 end
  function item.GetCastRange(self) return 600 end
  function item.GetManaCost(self) return 0 end
  return item
end

-- ---- 通用单位包装 (小兵 / 塔 / 基地 / 肉山): 方法读实时数值 ----
local function wrapUnit(world, u)
  if u._api ~= nil then return u._api end
  local api = { _kind = "unit", _world = world, _unit = u }
  function api.GetUnitName(self)
    local uu = self._unit
    if uu.kind == "creep" then
      if uu.isNeutral then return "npc_dota_neutral_creep" end
      return "npc_dota_creep"
    end
    if uu.kind == "tower" then return "npc_dota_tower" end
    if uu.kind == "ancient" then return "npc_dota_ancient" end
    if uu.kind == "roshan" then return "npc_dota_roshan" end
    return "npc_dota_unit"
  end
  function api.GetHealth(self) return self._unit.hp end
  function api.GetMaxHealth(self) return self._unit.maxHp end
  function api.GetMana(self) return 0 end
  function api.GetMaxMana(self) return 0 end
  function api.GetHealthRegen(self) return 0.5 end
  function api.GetMovementSpeed(self) return self._unit.speed or 0 end
  function api.GetLocation(self) return { x = self._unit.x, y = self._unit.y, z = 0 } end
  function api.IsAlive(self) return self._unit.alive end
  function api.IsNull(self) return false end
  function api.GetTeam(self) return self._unit.team end
  function api.GetAttackRange(self) return self._unit.range or 150 end
  function api.GetAttackDamage(self) return self._unit.dmg or 0 end
  u._api = api
  return api
end

Valve.wrapUnit = wrapUnit

-- ---- 施法结算 ----

local function enemiesInRadius(world, x, y, radius, team)
  local out = {}
  for _, h in ipairs(world.heroes) do
    if h.alive and h.team ~= team and Sim.dist(x, y, h.x, h.y) <= radius then
      out[#out + 1] = h
    end
  end
  for _, c in ipairs(world.creeps) do
    if c.alive and c.team ~= team and Sim.dist(x, y, c.x, c.y) <= radius then
      out[#out + 1] = c
    end
  end
  return out
end

local function applyControl(world, target, seconds)
  if target == nil or target.kind == nil then return end
  if target.kind == "hero" or target.kind == "creep" then
    target.stunUntil = math.max(target.stunUntil or 0, world.time + seconds)
  end
end

-- 召唤物 (谜团转化): 在施法者身边生成 2 只小 eidolon。
local function spawnSummon(world, hero)
  for i = 1, 2 do
    local creep = {
      id = world.nextId, kind = "creep", team = hero.team, lane = nil,
      x = hero.x + (i * 2 - 3) * 60, y = hero.y + 60,
      hp = 300, maxHp = 300, dmg = 25, range = 150,
      speed = 320, attackCd = 0, alive = true,
      pathFrac = nil, pathDir = 0, bounty = 20, xpValue = 20,
      isSiege = false, isNeutral = false, camp = nil, stunUntil = 0,
      homeX = hero.x, homeY = hero.y, summoned = true, lifeUntil = world.time + 40,
    }
    world.nextId = world.nextId + 1
    world.creeps[#world.creeps + 1] = creep
  end
end

-- 施法: ab 为技能对象或物品对象; target 为单位包装或 nil; loc 为位置表或 nil。
-- 返回 true 表示成功施放 (扣蓝、进 CD、生效)。
function Valve.cast(world, hero, ab, targetUnit, loc)
  if ab == nil or ab._kind == nil then return false end
  if not hero.alive then return false end
  if ab._kind == "item" then return Valve.useItem(world, hero, ab, targetUnit, loc) end
  local data = ab._data
  if ab.level <= 0 or ab.cd > 0 then return false end
  if data.passive == true then return false end
  local manaCost = data.mana or 0
  if hero.mana < manaCost then return false end
  local kind = data.kind or "unit"
  local target = nil
  if targetUnit ~= nil then
    -- 目标可能是小兵/塔包装 (_unit) 或英雄包装 (_hero), 都要解出来。
    -- 旧版只认 _unit, 英雄目标会落到包装表本身、因没有 alive 字段而静默失败。
    target = targetUnit._unit or targetUnit._hero or targetUnit
  end
  -- 射程检查: 够不着就往目标走 (下 tick 再试), 不扣蓝。
  if kind == "unit" or kind == "execute" or kind == "heal" then
    if target == nil or not target.alive then return false end
    local range = data.range or 600
    if Sim.dist(hero.x, hero.y, target.x, target.y) > range + 50 then
      hero.moveTarget = { x = target.x, y = target.y, z = 0 }
      hero.attackTarget = nil
      return false
    end
  elseif kind == "location" or kind == "blink" then
    if loc == nil then return false end
    local range = data.range or 600
    if kind == "location" and Sim.dist(hero.x, hero.y, loc.x, loc.y) > range + 200 then
      hero.moveTarget = { x = loc.x, y = loc.y, z = 0 }
      hero.attackTarget = nil
      return false
    end
  end
  hero.mana = hero.mana - manaCost
  ab.cd = data.cd or 8
  if data.hpCost ~= nil then
    hero.hp = math.max(1, hero.hp - data.hpCost)
  end
  if data.hpCostPct ~= nil then
    hero.hp = math.max(1, hero.hp - hero.hp * data.hpCostPct)
  end
  hero.stats.casts = hero.stats.casts + 1
  local dmg = (data.dmg or 0) * (1 + 0.25 * (ab.level - 1))
  local t = world.time
  if kind == "global" then
    for _, h in ipairs(world.heroes) do
      if h.alive and h.team ~= hero.team then Sim.damage(world, h, dmg, hero) end
    end
  elseif kind == "unit" or kind == "execute" then
    if kind == "execute" and target.hp <= 250 + 50 * ab.level then
      Sim.damage(world, target, target.hp + 1, hero)
    else
      Sim.damage(world, target, dmg, hero)
    end
    if data.control ~= nil then applyControl(world, target, data.control) end
    if ab._name == "lion_mana_drain" and target.kind == "hero" then
      local drain = math.min(100, target.mana)
      target.mana = target.mana - drain
      hero.mana = math.min(hero.maxMana, hero.mana + drain)
    end
  elseif kind == "heal" then
    if ab._name == "dazzle_shallow_grave" then
      target.graveUntil = t + 5
    elseif ab._name == "dazzle_shadow_wave" then
      Sim.heal(world, target, 150)
      for _, e in ipairs(enemiesInRadius(world, target.x, target.y, 300, hero.team)) do
        Sim.damage(world, e, dmg, hero)
      end
    else
      Sim.heal(world, target, 150)
    end
  elseif kind == "location" then
    local radius = 300
    if data.control ~= nil then radius = 350 end
    for _, e in ipairs(enemiesInRadius(world, loc.x, loc.y, radius, hero.team)) do
      Sim.damage(world, e, dmg, hero)
      if data.control ~= nil then applyControl(world, e, data.control) end
    end
    local r = world.roshan
    if r ~= nil and r.alive and Sim.dist(loc.x, loc.y, r.x, r.y) <= radius then
      Sim.damage(world, r, dmg, hero)
    end
  elseif kind == "blink" then
    hero.x, hero.y = loc.x, loc.y
    hero.moveTarget = nil
  elseif kind == "none" then
    local radius = 400
    if ab._name == "crystal_maiden_freezing_field" then radius = 600 end
    for _, e in ipairs(enemiesInRadius(world, hero.x, hero.y, radius, hero.team)) do
      Sim.damage(world, e, dmg, hero)
      if data.control ~= nil then applyControl(world, e, data.control) end
    end
    local r = world.roshan
    if r ~= nil and r.alive and Sim.dist(hero.x, hero.y, r.x, r.y) <= radius then
      Sim.damage(world, r, dmg, hero)
    end
  elseif kind == "buff" then
    if ab._name == "sven_gods_strength" then
      hero.dmgMul = 2
      hero.dmgMulUntil = t + 20
    elseif ab._name == "magnus_empower" or ab._name == "sven_warcry" then
      hero.bonusDmg = 30
      hero.bonusDmgUntil = t + 60
      if ab._name == "sven_warcry" then Sim.heal(world, hero, 100) end
    elseif ab._name == "dazzle_weave" then
      for _, a in ipairs(world.heroes) do
        if a.alive and a.team == hero.team and Sim.dist(hero.x, hero.y, a.x, a.y) <= 500 then
          Sim.heal(world, a, 50)
        end
      end
    end
  elseif kind == "summon" then
    spawnSummon(world, hero)
  end
  return true
end

-- 物品使用 (消耗品治疗 / 插眼)。
function Valve.useItem(world, hero, item, targetUnit, loc)
  local name = item._name
  if name == "item_ward_observer" then
    if loc == nil then return false end
    world.wards[#world.wards + 1] = { x = loc.x, y = loc.y, team = hero.team, expiresAt = world.time + 360 }
    hero.stats.wards = hero.stats.wards + 1
    Valve.removeItem(hero, item)
    return true
  end
  if name == "item_flask" then
    Sim.heal(world, hero, 150)
    Valve.removeItem(hero, item)
    return true
  end
  if name == "item_tango" then
    Sim.heal(world, hero, 80)
    Valve.removeItem(hero, item)
    return true
  end
  if name == "item_clarity" then
    hero.mana = math.min(hero.maxMana, hero.mana + 120)
    Valve.removeItem(hero, item)
    return true
  end
  if name == "item_magic_wand" then
    Sim.heal(world, hero, 100)
    hero.mana = math.min(hero.maxMana, hero.mana + 100)
    return true
  end
  -- 其他主动物品: 模拟里无效果, 只记一次使用。
  return true
end

function Valve.removeItem(hero, item)
  for i, it in ipairs(hero.items) do
    if it == item then table.remove(hero.items, i) return true end
  end
  for i, it in ipairs(hero.stash) do
    if it == item then table.remove(hero.stash, i) return true end
  end
  return false
end

function Valve.itemCost(name)
  local c = Valve.ITEM_COSTS[name]
  if c == nil then
    Valve.unknownItems[name] = true
    return 500
  end
  return c
end

-- ---- Bot 单位 (英雄) ----

local function makeBotUnit(world, hero)
  local bot = { _kind = "bot", _world = world, _hero = hero, _lastOrderKey = nil, _lastAttackKey = nil }
  function bot.GetUnitName(self) return "npc_dota_hero_" .. self._hero.key end
  function bot.GetHealth(self) return self._hero.hp end
  function bot.GetMaxHealth(self) return self._hero.maxHp end
  function bot.GetMana(self) return self._hero.mana end
  function bot.GetMaxMana(self) return self._hero.maxMana end
  function bot.GetHealthRegen(self) return 3 + 0.5 * self._hero.level end
  function bot.GetMovementSpeed(self) return Sim.moveSpeed(self._hero) end
  function bot.GetLocation(self) return { x = self._hero.x, y = self._hero.y, z = 0 } end
  function bot.GetAttackRange(self) return Sim.attackRange(self._hero) end
  function bot.GetAttackDamage(self) return Sim.attackDamage(self._hero, self._world.time) end
  function bot.GetLevel(self) return self._hero.level end
  function bot.GetGold(self) return math.floor(self._hero.gold) end
  function bot.GetAbilityPoints(self) return self._hero.abilityPts end
  function bot.GetTeam(self) return self._hero.team end
  function bot.GetPlayerID(self)
    for i, h in ipairs(self._world.heroes) do
      if h == self._hero then return i - 1 end
    end
    return 0
  end
  function bot.IsAlive(self) return self._hero.alive end
  function bot.IsNull(self) return false end
  function bot.GetForwardVector(self) return { x = 1, y = 0, z = 0 } end
  function bot.GetCourier(self) return self._hero._courier end
  function bot.GetNumItemsInStash(self) return #self._hero.stash end
  function bot.GetStashItemCount(self) return #self._hero.stash end

  function bot.GetNearbyHeroes(self, radius, bEnemy, mode)
    local out = {}
    local w = self._world
    local h = self._hero
    for _, eh in ipairs(w.heroes) do
      if eh ~= h and eh.alive then
        local isEnemy = eh.team ~= h.team
        if isEnemy == bEnemy then
          local d = Sim.dist(h.x, h.y, eh.x, eh.y)
          if d <= radius and (not isEnemy or Sim.isVisibleTo(w, h.team, eh)) then
            out[#out + 1] = eh._bot
          end
        end
      end
    end
    return out
  end
  function bot.GetNearbyCreeps(self, radius, bEnemy)
    local out = {}
    local w = self._world
    local h = self._hero
    for _, c in ipairs(w.creeps) do
      if c.alive then
        local isEnemy = (c.team ~= h.team)
        if isEnemy == bEnemy then
          local d = Sim.dist(h.x, h.y, c.x, c.y)
          if d <= radius and (not isEnemy or Sim.isVisibleTo(w, h.team, c)) then
            out[#out + 1] = wrapUnit(w, c)
          end
        end
      end
    end
    return out
  end
  function bot.GetNearbyTowers(self, radius, bEnemy)
    local out = {}
    local w = self._world
    local h = self._hero
    local list = {}
    for _, t in ipairs(w.towers) do
      if t.alive then
        local isEnemy = (t.team ~= h.team)
        if isEnemy == bEnemy then
          local d = Sim.dist(h.x, h.y, t.x, t.y)
          if d <= radius then list[#list + 1] = { d = d, u = wrapUnit(w, t) } end
        end
      end
    end
    -- 模拟偏差 (见 README): 基地古迹也随塔返回, 否则终局无人能推进。
    -- 真机 GetNearbyTowers 只返回防御塔。
    for _, a in ipairs(w.ancients) do
      if a.alive then
        local isEnemy = (a.team ~= h.team)
        if isEnemy == bEnemy then
          local d = Sim.dist(h.x, h.y, a.x, a.y)
          if d <= radius then list[#list + 1] = { d = d, u = wrapUnit(w, a) } end
        end
      end
    end
    table.sort(list, function(x, y) return x.d < y.d end)
    for _, e in ipairs(list) do out[#out + 1] = e.u end
    return out
  end

  function bot.GetAbilityInSlot(self, slot)
    return self._hero.abilities[slot]
  end
  function bot.GetAbilityByName(self, name)
    for _, ab in pairs(self._hero.abilities) do
      if ab ~= nil and ab._name == name then return ab end
    end
    return nil
  end
  function bot.GetItemInSlot(self, slot)
    return self._hero.items[slot + 1]
  end

  local function orderKey(kind, x, y)
    return kind .. ":" .. math.floor(x / 100) .. "," .. math.floor(y / 100)
  end
  function bot.Action_MoveToLocation(self, loc)
    if loc == nil or self._hero == nil then return end
    local h = self._hero
    local key = orderKey("move", loc.x or 0, loc.y or 0)
    if key ~= self._lastOrderKey then
      h.stats.moves = h.stats.moves + 1
      self._lastOrderKey = key
    end
    h.moveTarget = { x = loc.x, y = loc.y, z = loc.z or 0 }
    h.followUnit = nil
    h.attackTarget = nil
    h.attackMoveTarget = nil
  end
  function bot.Action_MoveToUnit(self, unit)
    if unit == nil then return end
    local h = self._hero
    local u = unit._unit or unit._hero or unit
    if u == nil then return end
    local key = "follow:" .. tostring(u.id or u)
    if key ~= self._lastOrderKey then
      h.stats.moves = h.stats.moves + 1
      self._lastOrderKey = key
    end
    h.followUnit = u
    h.moveTarget = nil
    h.attackTarget = nil
    h.attackMoveTarget = nil
  end
  function bot.Action_AttackUnit(self, unit, once)
    if unit == nil then return end
    local h = self._hero
    local u = unit._unit or unit._hero or unit
    if u == nil or not u.alive then return end
    local key = "attack:" .. tostring(u.id or u)
    if key ~= self._lastAttackKey then
      h.stats.attackOrders = h.stats.attackOrders + 1
      self._lastAttackKey = key
    end
    h.attackTarget = u
    h.moveTarget = nil
    h.followUnit = nil
    h.attackMoveTarget = nil
  end
  function bot.Action_AttackMove(self, loc)
    if loc == nil then return end
    local h = self._hero
    local key = orderKey("amove", loc.x or 0, loc.y or 0)
    if key ~= self._lastOrderKey then
      h.stats.moves = h.stats.moves + 1
      self._lastOrderKey = key
    end
    h.attackMoveTarget = { x = loc.x, y = loc.y, z = loc.z or 0 }
    h.moveTarget = nil
    h.followUnit = nil
    h.attackTarget = nil
  end
  function bot.Action_UseAbility(self, ab)
    if ab == nil then return end
    Valve.cast(self._world, self._hero, ab, nil, nil)
  end
  function bot.Action_UseAbilityOnEntity(self, ab, unit)
    if ab == nil or unit == nil then return end
    Valve.cast(self._world, self._hero, ab, unit, nil)
  end
  function bot.Action_UseAbilityOnLocation(self, ab, loc)
    if ab == nil or loc == nil then return end
    Valve.cast(self._world, self._hero, ab, nil, loc)
  end
  function bot.Action_PurchaseItem(self, name)
    local h = self._hero
    local w = self._world
    if name == nil then return false end
    local cost = Valve.itemCost(name)
    if h.gold < cost then return false end
    h.gold = h.gold - cost
    h.goldSpent = h.goldSpent + cost
    local item = makeItem(w, h, name)
    if #h.items < 9 then
      h.items[#h.items + 1] = item
    else
      h.stash[#h.stash + 1] = item
    end
    h.maxHp = Sim.maxHp(h)
    h.maxMana = Sim.maxMana(h)
    h.stats.buys = h.stats.buys + 1
    return true
  end
  function bot.Action_LevelAbility(self, name)
    local h = self._hero
    if name == nil or h.abilityPts <= 0 then return false end
    local ab = nil
    for _, a in pairs(h.abilities) do
      if a ~= nil and a._name == name then ab = a break end
    end
    if ab == nil then return false end
    local ok, can = pcall(function() return ab:CanAbilityBeUpgraded() end)
    if not ok or not can then return false end
    ab.level = ab.level + 1
    h.abilityPts = h.abilityPts - 1
    h.stats.abilitiesLeveled = (h.stats.abilitiesLeveled or 0) + 1
    return true
  end
  function bot.Action_Courier(self, action)
    local h = self._hero
    local moved = false
    for i = #h.stash, 1, -1 do
      if #h.items < 9 then
        h.items[#h.items + 1] = h.stash[i]
        table.remove(h.stash, i)
        moved = true
      end
    end
    return moved
  end
  hero._bot = bot
  return bot
end

-- ---- 安装全局 Valve API ----

function Valve.install(world, cfg)
  Valve.world = world
  local heroesData = require("bots/data/heroes")
  for _, hero in ipairs(world.heroes) do
    -- 技能槽 0-3: BotLib 的 ABILITIES; Invoker 另有 invoked 技能进 4-9 槽。
    local mod = nil
    local ok, m = pcall(require, "bots/BotLib/hero_" .. hero.key)
    if ok then mod = m end
    local names = {}
    if mod ~= nil and mod.ABILITIES ~= nil then
      names[0] = mod.ABILITIES.Q
      names[1] = mod.ABILITIES.W
      names[2] = mod.ABILITIES.E
      names[3] = mod.ABILITIES.R
    else
      local hd = heroesData[hero.key]
      local n = 0
      if hd ~= nil and hd.abilities ~= nil then n = #hd.abilities end
      for i = 0, 3 do
        if i < n then names[i] = hero.key .. "_ability_" .. (i + 1) end
      end
    end
    local maxLevels = { 4, 4, 4, 3 }
    for slot = 0, 3 do
      if names[slot] ~= nil then
        hero.abilities[slot] = makeAbility(world, hero, names[slot], slot, maxLevels[slot + 1], false)
      end
    end
    if mod ~= nil and mod.INVOKED ~= nil then
      for i, invName in ipairs(mod.INVOKED) do
        if i <= 6 then
          hero.abilities[3 + i] = makeAbility(world, hero, invName, 3 + i, 4, false)
        end
      end
    end
    -- 天赋槽 10-17。
    local talentNames = {
      "special_bonus_strength_6", "special_bonus_agility_6",
      "special_bonus_intelligence_6", "special_bonus_attack_damage_15",
      "special_bonus_hp_200", "special_bonus_mana_150",
      "special_bonus_armor_5", "special_bonus_magic_resistance_8",
    }
    for slot = 10, 17 do
      hero.abilities[slot] = makeAbility(world, hero, talentNames[slot - 9], slot, 1, true)
    end
    hero._courier = { _kind = "courier", IsNull = function() return false end }
    makeBotUnit(world, hero)
  end

  _G.DOTA_AI_DIFFICULTY = cfg.difficulty or 3
  _G._SIM_WORLD = world
  _G._SIM_CURRENT_BOT = nil

  function _G.GetBot()
    return Valve.currentBot
  end
  function _G.DotaTime()
    if Valve.world ~= nil then return Valve.world.time end
    return 0
  end
  -- 模拟扩展 (真实 Valve API 没有此函数): 返回当前肉山所在坑位, 肉山死亡 /
  -- 未刷新时返回 nil。真实对局里队伍靠视野和计时判断肉山在两个坑中的哪一个;
  -- 模拟里直接给出, 否则 Bot 只能去己方半场坑位、而肉山可能在另一边
  -- (模拟实测: Dire 选了 45 tick 打盾模式却去了空坑)。见 README 已知简化。
  function _G.GetRoshanLocation()
    local w = Valve.world
    if w == nil or w.roshan == nil or not w.roshan.alive then return nil end
    local pit = Sim.ROSHAN_PITS[w.roshan.pit]
    if pit == nil then return nil end
    return { x = pit.x, y = pit.y, z = 0 }
  end
  function _G.GetTeam()
    if Valve.currentBot ~= nil then return Valve.currentBot:GetTeam() end
    return 2
  end
  function _G.GetScriptDirectory()
    return "bots"
  end
  function _G.GetItemCost(name)
    return Valve.itemCost(name)
  end
  function _G.GetCourier(playerId)
    if playerId == nil then return nil end
    local h = Valve.world.heroes[playerId + 1]
    if h == nil then return nil end
    return h._courier
  end
  function _G.GetUnitToUnitDistance(u1, u2)
    if u1 == nil or u2 == nil then return 1e9 end
    local l1 = u1:GetLocation()
    local l2 = u2:GetLocation()
    return Sim.dist(l1.x, l1.y, l2.x, l2.y)
  end
  function _G.GetUnitToLocationDistance(u, loc)
    if u == nil or loc == nil then return 1e9 end
    local l = u:GetLocation()
    return Sim.dist(l.x, l.y, loc.x, loc.y)
  end
  function _G.RandomInt(n, m)
    if m == nil then return math.random(n) end
    return math.random(n, m)
  end
  function _G.RandomFloat(a, b)
    if b == nil then return math.random() * a end
    return a + math.random() * (b - a)
  end

  _G.BOT_MODE_NONE = 0
  _G.BOT_MODE_LANING = 1
  _G.BOT_MODE_ATTACK = 2
  _G.BOT_MODE_ROAM = 3
  _G.BOT_MODE_RETREAT = 4
  _G.BOT_MODE_PUSH = 5
  _G.BOT_MODE_DEFEND_ALLY = 6
  _G.BOT_MODE_FARM = 7
  _G.BOT_MODE_ROSHAN = 8
  _G.BOT_MODE_ITEM = 9
  _G.BOT_MODE_WARD = 10
  _G.BOT_MODE_TEAM_ROAM = 11
  _G.BOT_MODE_SECRET_SHOP = 12
  _G.BOT_MODE_SIDE_SHOP = 13
  _G.BOT_MODE_RUNE = 14
  _G.BOT_MODE_DEFEND_TOWER = 15
  _G.BOT_MODE_EVASIVE_MANEUVERS = 16
  _G.BOT_MODE_PUSH_TOWER_TOP = 17
  _G.BOT_MODE_PUSH_TOWER_MID = 18
  _G.BOT_MODE_PUSH_TOWER_BOT = 19
  _G.COURIER_ACTION_BURST = 0
  _G.COURIER_ACTION_TRANSFER_ITEMS = 1
  _G.COURIER_ACTION_RETURN = 2
  _G.COURIER_ACTION_SECRET_SHOP = 3
  return Valve
end

function Valve.setCurrentBot(botUnit)
  Valve.currentBot = botUnit
end

-- 每 tick 调用: 技能 CD 倒计时; 召唤物过期。
function Valve.tick(world, dt)
  for _, hero in ipairs(world.heroes) do
    for _, ab in pairs(hero.abilities) do
      if ab ~= nil and ab.cd ~= nil and ab.cd > 0 then
        ab.cd = ab.cd - dt
        if ab.cd < 0 then ab.cd = 0 end
      end
    end
    for _, item in ipairs(hero.items) do
      if item.cd ~= nil and item.cd > 0 then item.cd = item.cd - dt end
    end
  end
  for i = #world.creeps, 1, -1 do
    local c = world.creeps[i]
    if c.summoned and c.lifeUntil ~= nil and world.time >= c.lifeUntil then
      c.alive = false
      table.remove(world.creeps, i)
    end
  end
end

return Valve
