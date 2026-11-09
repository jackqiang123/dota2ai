# -*- coding: utf-8 -*-
"""C 组英雄深度数据 (v3.0.0, tools/generate.py 的事实源之一)。
覆盖 20 个英雄: leshrac, lich, lifestealer, lina, lone_druid, luna, lycan,
marci, mars, medusa, meepo, mirana, monkey_king, morphling, muerta,
naga_siren, natures_prophet, necrophos, night_stalker, nyx_assassin。
技能名一律取自 tools/skill_names_reference.json, 不自编不替换;
可疑名只写进各英雄的 limitations, 不擅自改名。
位置/主属性/分路取自 tools/heroes_data.py。
格式抄 tools/focus_heroes.py: abilities / talents / items / consider。
consider 的 Lua 只用允许的 API:
Skill.IsCastable / CountEnemiesInRange / CountLowHpEnemies / LowestHpEnemy /
LowestHpAlly / LowestHpAllyPct / HpOf / HpPctOf, snap 字段,
Team.ShouldHoldUlt / Team.GetComboWindow。Lua 5.1 兼容写法, 不用新版语法。
talents 为本项目自选, 非官方推荐。
"""
ALL_C = {
"leshrac": {
  "abilities": {"Q": "leshrac_split_earth", "W": "leshrac_diabolic_edict", "E": "leshrac_lightning_storm", "R": "leshrac_pulse_nova"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_bottle", "item_kaya_and_sange", "item_bloodstone", "item_black_king_bar", "item_shivas_guard", "item_octarine_core", "item_aghanims_scepter", "item_travel_boots", "item_scythe_of_vyse"],
    2: ["item_tango", "item_flask", "item_clarity", "item_null_talisman", "item_bottle", "item_power_treads", "item_soul_ring", "item_kaya_and_sange", "item_bloodstone", "item_black_king_bar", "item_shivas_guard", "item_octarine_core", "item_aghanims_scepter", "item_travel_boots", "item_scythe_of_vyse"],
    3: ["item_tango", "item_flask", "item_bracer", "item_arcane_boots", "item_vanguard", "item_pipe_of_insight", "item_shivas_guard", "item_black_king_bar", "item_crimson_guard", "item_lotus_orb", "item_aghanims_scepter"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_ghost_scepter", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_euls_scepter_of_divinity", "item_aeon_disk"]},
  "consider": {
    "Q": """local ab = ab["leshrac_split_earth"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local w = Team.GetComboWindow()
  if w ~= nil and (snap.numEnemies or 0) >= 1 then return 0.85, snap.nearestEnemy, "location" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["leshrac_diabolic_edict"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 and (snap.manaPct or 1) > 0.25 then return 0.9, nil, "none" end
  if n >= 1 and (snap.manaPct or 1) > 0.4 then return 0.75, nil, "none" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["leshrac_lightning_storm"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.8, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.65, t, "unit" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["leshrac_pulse_nova"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 and (snap.manaPct or 1) > 0.4 then return 0.85, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.5 and (snap.manaPct or 1) > 0.5 then return 0.6, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "Pulse Nova and Diabolic Edict are toggles: the snippet only decides when to turn them on, toggle state is not tracked, so it may re-cast while already active.",
},
"lich": {
  "abilities": {"Q": "lich_frost_nova", "W": "lich_frost_armor", "E": "lich_sinister_gaze", "R": "lich_chain_frost"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_aether_lens", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_scythe_of_vyse", "item_shivas_guard", "item_travel_boots", "item_refresher_orb"],
    2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_aether_lens", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_scythe_of_vyse", "item_kaya_and_sange", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_arcane_boots", "item_pipe_of_insight", "item_crimson_guard", "item_shivas_guard", "item_black_king_bar", "item_lotus_orb", "item_aghanims_scepter"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_ghost_scepter", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_aghanims_scepter", "item_ghost_scepter", "item_lotus_orb", "item_aeon_disk", "item_euls_scepter_of_divinity"]},
  "consider": {
    "Q": """local ab = ab["lich_frost_nova"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.85, snap.nearestEnemy, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["lich_frost_armor"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.6 then return 0.85, ally, "unit" end
  if (snap.healthPct or 1) < 0.5 then return 0.7, bot, "unit" end
  if ally ~= nil and (snap.numAllies or 0) >= 1 and (snap.numEnemies or 0) >= 1 then return 0.55, ally, "unit" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["lich_sinister_gaze"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    if Skill.HpPctOf(t) < 0.4 then return 0.85, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none\"""",
    "R": """local ab = ab["lich_chain_frost"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.95, Skill.LowestHpEnemy(snap), "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.35 then return 0.8, t, "unit" end
  return 0, nil, "none\"""",
  },
  "limitations": "v3.0 已订正: E 为 lich_sinister_gaze(邪恶凝视, 引导控制)。W 名 lich_frost_armor 显示名为 Frost Shield(寒霜之盾), 内部名可能同样过时, 按原样保留。",
},
"lifestealer": {
  "abilities": {"Q": "life_stealer_rage", "W": "life_stealer_feast", "E": "life_stealer_open_wounds", "R": "life_stealer_infest"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_armlet", "item_desolator", "item_black_king_bar", "item_abyssal_blade", "item_assault", "item_satanic", "item_monkey_king_bar", "item_moon_shard", "item_travel_boots", "item_aghanims_scepter", "item_nullifier"],
    2: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_armlet", "item_echo_sabre", "item_black_king_bar", "item_desolator", "item_assault", "item_satanic", "item_abyssal_blade", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_armlet", "item_blade_mail", "item_black_king_bar", "item_assault", "item_crimson_guard", "item_heart", "item_aghanims_scepter"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_armlet", "item_force_staff", "item_black_king_bar", "item_desolator", "item_glimmer_cape"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_armlet", "item_black_king_bar"]},
  "consider": {
    "Q": """local ab = ab["life_stealer_rage"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 1 and (snap.healthPct or 1) < 0.6 then return 0.85, nil, "none" end
  if n >= 2 then return 0.8, nil, "none" end
  return 0, nil, "none\"""",
    "W": """return 0, nil, "none\"""",
    "E": """local ab = ab["life_stealer_open_wounds"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    local pct = Skill.HpPctOf(t)
    if pct > 0 and pct < 0.4 then return 0.85, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none\"""",
    "R": """local ab = ab["life_stealer_infest"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and snap.nearbyAllyCreeps ~= nil and #snap.nearbyAllyCreeps > 0 then return 0.8, snap.nearbyAllyCreeps[1], "unit" end
  if (snap.healthPct or 1) < 0.3 then
    local ally = Skill.LowestHpAlly(snap)
    if ally ~= nil then return 0.75, ally, "unit" end
  end
  if (snap.healthPct or 1) > 0.7 and (snap.numEnemies or 0) >= 1 then
    local ally2 = Skill.LowestHpAlly(snap)
    if ally2 ~= nil then return 0.55, ally2, "unit" end
  end
  return 0, nil, "none\"""",
  },
  "limitations": "No creep-host choice for Infest: it hides in the nearest allied creep or the lowest-HP ally only, with no pick of the best host; Feast is passive; no control over when to pop out of Infest.",
},
"lina": {
  "abilities": {"Q": "lina_dragon_slave", "W": "lina_light_strike_array", "E": "lina_fiery_soul", "R": "lina_laguna_blade"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_bloodthorn", "item_scythe_of_vyse", "item_octarine_core", "item_aghanims_scepter", "item_travel_boots", "item_moon_shard"],
    2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_euls_scepter_of_divinity", "item_aether_lens", "item_black_king_bar", "item_bloodthorn", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots", "item_kaya_and_sange", "item_dagon_5"],
    3: ["item_tango", "item_flask", "item_bracer", "item_arcane_boots", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_shivas_guard", "item_lotus_orb", "item_aghanims_scepter", "item_octarine_core"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_euls_scepter_of_divinity", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_euls_scepter_of_divinity", "item_ghost_scepter", "item_aeon_disk"]},
  "consider": {
    "Q": """local ab = ab["lina_dragon_slave"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 800)
  if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 then return 0.65, t, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["lina_light_strike_array"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local w = Team.GetComboWindow()
  if w ~= nil and (snap.numEnemies or 0) >= 1 then return 0.85, snap.nearestEnemy, "location" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "location" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["lina_laguna_blade"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local hp = Skill.HpOf(t)
  if hp > 0 and hp < 450 then return 1.0, t, "unit" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.25 then return 0.95, t, "unit" end
  if pct > 0 and pct < 0.4 and (snap.manaPct or 1) > 0.5 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
  },
  "limitations": "Light Strike Array into Laguna Blade sequencing is not guaranteed: Array is aimed at the lowest-HP enemy, not timed to hold the Laguna target; Fiery Soul is passive.",
},
"lone_druid": {
  "abilities": {"Q": "lone_druid_spirit_bear", "W": "lone_druid_rabid", "E": "lone_druid_synergy", "R": "lone_druid_true_form"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_hand_of_midas", "item_radiance", "item_black_king_bar", "item_assault", "item_butterfly", "item_heart", "item_moon_shard", "item_travel_boots", "item_aghanims_scepter", "item_manta", "item_nullifier"],
    2: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_radiance", "item_echo_sabre", "item_black_king_bar", "item_assault", "item_satanic", "item_butterfly", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_radiance", "item_blade_mail", "item_black_king_bar", "item_crimson_guard", "item_assault", "item_heart"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_radiance", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_assault"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_radiance", "item_black_king_bar"]},
  "consider": {
    "Q": """local ab = ab["lone_druid_spirit_bear"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) == 0 then return 0.6, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.6 then return 0.65, nil, "none" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["lone_druid_rabid"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 1 then return 0.7, nil, "none" end
  if snap.nearbyEnemyCreeps ~= nil and #snap.nearbyEnemyCreeps > 0 then return 0.55, nil, "none" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["lone_druid_true_form"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 and (snap.healthPct or 1) > 0.4 then return 0.85, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) < 0.35 then return 0.8, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "No independent Spirit Bear micro: the bear follows the generic summon logic, with no separate bear attack, item or positioning control; True Form switching is cast-only, with no form-aware positioning.",
},
"luna": {
  "abilities": {"Q": "luna_lucent_beam", "W": "luna_moon_glaive", "E": "luna_lunar_blessing", "R": "luna_eclipse"},
  "talents": {10: 1, 15: 0, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_manta", "item_black_king_bar", "item_butterfly", "item_satanic", "item_hurricane_pike", "item_moon_shard", "item_travel_boots", "item_aghanims_scepter", "item_monkey_king_bar"],
    2: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_maelstrom", "item_manta", "item_black_king_bar", "item_butterfly", "item_satanic", "item_mjollnir", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_manta", "item_black_king_bar", "item_assault", "item_crimson_guard", "item_heart", "item_butterfly"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_dragon_lance", "item_force_staff", "item_manta", "item_black_king_bar", "item_glimmer_cape"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_dragon_lance", "item_black_king_bar"]},
  "consider": {
    "Q": """local ab = ab["luna_lucent_beam"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.3 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.9, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
    "W": """return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["luna_eclipse"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.95, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.35 and n >= 1 then return 0.8, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "Eclipse damage scales with Lucent Beam stacks, which are not tracked, so it is cast on headcount alone; Moon Glaive bounces are not aimed.",
},
"lycan": {
  "abilities": {"Q": "lycan_summon_wolves", "W": "lycan_howl", "E": "lycan_feral_impulse", "R": "lycan_shapeshift"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_helm_of_the_dominator", "item_black_king_bar", "item_assault", "item_harpoon", "item_nullifier", "item_moon_shard", "item_travel_boots", "item_aghanims_scepter", "item_satanic", "item_butterfly", "item_abyssal_blade"],
    2: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_helm_of_the_dominator", "item_echo_sabre", "item_black_king_bar", "item_assault", "item_harpoon", "item_satanic", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_helm_of_the_dominator", "item_blade_mail", "item_black_king_bar", "item_crimson_guard", "item_assault", "item_heart"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_helm_of_the_dominator", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_assault"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_helm_of_the_dominator", "item_black_king_bar"]},
  "consider": {
    "Q": """local ab = ab["lycan_summon_wolves"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 then return 0.65, nil, "none" end
  if snap.nearbyEnemyCreeps ~= nil and #snap.nearbyEnemyCreeps > 0 then return 0.5, nil, "none" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["lycan_howl"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 800)
  if n >= 2 then return 0.8, nil, "none" end
  if n >= 1 and (snap.numAllies or 0) >= 2 then return 0.7, nil, "none" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["lycan_shapeshift"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.5 then return 0.85, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) < 0.4 then return 0.8, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "No wolf micro: summoned wolves use the generic summon logic, with no separate wolf target selection or scouting; Shapeshift is cast-only, with no pack-hunt coordination.",
},
"marci": {
  "abilities": {"Q": "marci_dispose", "W": "marci_rebound", "E": "marci_sidekick", "R": "marci_unleash"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_bracer", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_assault", "item_satanic", "item_abyssal_blade", "item_harpoon", "item_travel_boots", "item_butterfly"],
    2: ["item_tango", "item_flask", "item_bracer", "item_power_treads", "item_echo_sabre", "item_desolator", "item_black_king_bar", "item_harpoon", "item_assault", "item_satanic", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_echo_sabre", "item_blink", "item_black_king_bar", "item_assault", "item_harpoon", "item_aghanims_scepter", "item_heart", "item_travel_boots", "item_abyssal_blade", "item_satanic", "item_nullifier"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_blink", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_assault", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_blink", "item_black_king_bar", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["marci_dispose"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then
    local pct = Skill.HpPctOf(t)
    if pct > 0 and pct < 0.4 then return 0.85, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none\"""",
    "W": """local ab = ab["marci_rebound"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.5 and (snap.numEnemies or 0) >= 1 then return 0.8, ally, "unit" end
  if ally ~= nil and (snap.numEnemies or 0) >= 2 then return 0.65, ally, "unit" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["marci_unleash"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.9, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.5 then return 0.85, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "v3.0 已订正: Q 为 marci_dispose(摔跤行者)。Rebound 落点与二段跳目标未建模; Sidekick 为被动。",
},
"mars": {
  "abilities": {"Q": "mars_spear_of_mars", "W": "mars_gods_rebuke", "E": "mars_bulwark", "R": "mars_arena_of_blood"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_bracer", "item_power_treads", "item_desolator", "item_black_king_bar", "item_assault", "item_satanic", "item_abyssal_blade", "item_blink", "item_travel_boots", "item_heart"],
    2: ["item_tango", "item_flask", "item_bracer", "item_power_treads", "item_echo_sabre", "item_desolator", "item_black_king_bar", "item_blink", "item_assault", "item_satanic", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_desolator", "item_assault", "item_overwhelming_blink", "item_heart", "item_aghanims_scepter", "item_lotus_orb", "item_travel_boots", "item_satanic", "item_shivas_guard"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_blink", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_desolator", "item_assault"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_blink", "item_black_king_bar", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["mars_spear_of_mars"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.8, snap.nearestEnemy, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["mars_gods_rebuke"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.85, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.5 then return 0.6, nil, "none" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["mars_arena_of_blood"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  local w = Team.GetComboWindow()
  if n >= 2 and (snap.numAllies or 0) >= 1 then return 1.0, snap.nearestEnemy, "location" end
  if w ~= nil and n >= 1 then return 0.95, snap.nearestEnemy, "location" end
  if n >= 3 then return 0.95, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
  },
  "limitations": "Arena placement is headcount-only: no check that the ring actually traps the target, and no pin-against-wall or tree check for Spear of Mars; Bulwark is passive.",
},
"medusa": {
  "abilities": {"Q": "medusa_split_shot", "W": "medusa_mystic_snake", "E": "medusa_mana_shield", "R": "medusa_stone_gaze"},
  "talents": {10: 1, 15: 1, 20: 0, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_manta", "item_black_king_bar", "item_butterfly", "item_satanic", "item_hurricane_pike", "item_skadi", "item_moon_shard", "item_travel_boots", "item_aghanims_scepter", "item_monkey_king_bar"],
    2: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_maelstrom", "item_manta", "item_black_king_bar", "item_butterfly", "item_satanic", "item_mjollnir", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_manta", "item_black_king_bar", "item_assault", "item_crimson_guard", "item_heart", "item_skadi"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_dragon_lance", "item_force_staff", "item_manta", "item_black_king_bar", "item_glimmer_cape"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_dragon_lance", "item_black_king_bar"]},
  "consider": {
    "Q": """local ab = ab["medusa_split_shot"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 1 then return 0.6, nil, "none" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["medusa_mystic_snake"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 3 then return 0.85, snap.nearestEnemy, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["medusa_stone_gaze"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.95, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) < 0.4 then return 0.85, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "Split Shot is a toggle whose state is not tracked, so it may be re-cast while already on; Mana Shield mana drain is not managed, with no mana reserve kept for Stone Gaze.",
},
"meepo": {
  "abilities": {"Q": "meepo_earthbind", "W": "meepo_poof", "E": "meepo_geostrike", "R": "meepo_divided_we_stand"},
  "talents": {10: 0, 15: 0, 20: 1, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_blink", "item_black_king_bar", "item_skadi", "item_assault", "item_satanic", "item_aghanims_scepter", "item_heart", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_blink", "item_black_king_bar", "item_skadi", "item_aghanims_scepter", "item_assault", "item_heart", "item_travel_boots", "item_hurricane_pike", "item_satanic", "item_moon_shard"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_vanguard", "item_black_king_bar", "item_crimson_guard", "item_assault", "item_heart", "item_skadi"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_blink", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_skadi", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_blink", "item_black_king_bar", "item_aeon_disk"]},
  "consider": {
    "Q": """local ab = ab["meepo_earthbind"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.6 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.8, t, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["meepo_poof"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.85, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.3 and (snap.numEnemies or 0) >= 1 then return 0.75, nil, "none" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """return 0, nil, "none\"""",
  },
  "limitations": "No independent clone micro: all Meepo clones share the generic logic, with no separate Poof chains, clone positioning or clone-count awareness; Geostrike and Divided We Stand are passive.",
},
"mirana": {
  "abilities": {"Q": "mirana_starfall", "W": "mirana_arrow", "E": "mirana_leap", "R": "mirana_invis"},
  "talents": {10: 1, 15: 1, 20: 0, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_maelstrom", "item_black_king_bar", "item_manta", "item_butterfly", "item_satanic", "item_hurricane_pike", "item_mjollnir", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_maelstrom", "item_black_king_bar", "item_aghanims_scepter", "item_manta", "item_butterfly", "item_travel_boots", "item_mjollnir"],
    3: ["item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_maelstrom", "item_black_king_bar", "item_assault", "item_crimson_guard", "item_manta", "item_heart"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_power_treads", "item_maelstrom", "item_black_king_bar", "item_aghanims_scepter", "item_force_staff", "item_glimmer_cape", "item_manta", "item_travel_boots", "item_hurricane_pike"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_aghanims_scepter", "item_ghost_scepter", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["mirana_starfall"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.8, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.7, nil, "none" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["mirana_arrow"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local d = snap.nearestEnemyDist
  local pct = Skill.HpPctOf(t)
  if d ~= nil and d > 1000 and pct > 0 and pct < 0.4 then return 0.9, t, "location" end
  if d ~= nil and d > 600 and pct > 0 and pct < 0.5 then return 0.75, t, "location" end
  if d ~= nil and d <= 600 then return 0.55, t, "location" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["mirana_leap"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.9, snap.location, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.3 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.7, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["mirana_invis"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.85, nil, "none" end
  if (snap.numAllies or 0) >= 2 and (snap.numEnemies or 0) >= 1 then return 0.7, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "Sacred Arrow is a skillshot with no lead prediction, aimed at the target's current position; Leap has no retreat-vector computation, so the escape cast targets the bot's own location; R internal name mirana_invis is the old internal name for the display skill Moonlight Shadow.",
},
"monkey_king": {
  "abilities": {"Q": "monkey_king_boundless_strike", "W": "monkey_king_tree_dance", "E": "monkey_king_primal_spring", "R": "monkey_king_wukongs_command"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_desolator", "item_assault", "item_butterfly", "item_satanic", "item_abyssal_blade", "item_travel_boots", "item_aghanims_scepter", "item_monkey_king_bar"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_desolator", "item_harpoon", "item_assault", "item_travel_boots", "item_satanic"],
    3: ["item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_echo_sabre", "item_blade_mail", "item_black_king_bar", "item_assault", "item_crimson_guard", "item_heart", "item_desolator"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_echo_sabre", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_desolator", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_echo_sabre", "item_black_king_bar", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["monkey_king_boundless_strike"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.7, t, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["monkey_king_tree_dance"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.85, snap.location, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.3 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.7, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["monkey_king_primal_spring"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "location" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["monkey_king_wukongs_command"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.95, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
  },
  "limitations": "No tree awareness: Tree Dance has no tree targeting, and Primal Spring assumes a perch that is not verified; Boundless Strike is a line skillshot aimed at the nearest enemy with no line-up check.",
},
"morphling": {
  "abilities": {"Q": "morphling_waveform", "W": "morphling_adaptive_strike", "E": "morphling_morph_agi", "R": "morphling_replicate"},
  "talents": {10: 1, 15: 0, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_manta", "item_black_king_bar", "item_satanic", "item_butterfly", "item_hurricane_pike", "item_moon_shard", "item_travel_boots", "item_aghanims_scepter", "item_monkey_king_bar", "item_skadi"],
    2: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_manta", "item_black_king_bar", "item_butterfly", "item_satanic", "item_hurricane_pike", "item_travel_boots", "item_skadi"],
    3: ["item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_manta", "item_black_king_bar", "item_assault", "item_crimson_guard", "item_heart", "item_butterfly"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_dragon_lance", "item_force_staff", "item_manta", "item_black_king_bar", "item_glimmer_cape"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_dragon_lance", "item_black_king_bar"]},
  "consider": {
    "Q": """local ab = ab["morphling_waveform"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.3 and (snap.numEnemies or 0) >= 1 then return 0.8, t, "location" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.85, t, "location" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.7, t, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["morphling_adaptive_strike"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    local pct = Skill.HpPctOf(t)
    if pct > 0 and pct < 0.3 then return 0.9, t, "unit" end
    return 0.75, t, "unit"
  end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["morphling_replicate"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) > 0.5 then return 0.75, snap.nearestEnemy, "unit" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.6 then return 0.65, snap.nearestEnemy, "unit" end
  return 0, nil, "none\"""",
  },
  "limitations": "Attribute Morph (agi/str shift) is not modeled at all, so the bot never trades HP for damage or the reverse; Replicate's copy has no separate control and the bot cannot use the copied hero's spells; Adaptive Strike's agi/str forms are not distinguished.",
},
"muerta": {
  "abilities": {"Q": "muerta_dead_shot", "W": "muerta_the_calling", "E": "muerta_gunslinger", "R": "muerta_pierce_the_veil"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_maelstrom", "item_black_king_bar", "item_hurricane_pike", "item_butterfly", "item_satanic", "item_mjollnir", "item_moon_shard", "item_travel_boots", "item_aghanims_scepter", "item_monkey_king_bar"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_maelstrom", "item_black_king_bar", "item_hurricane_pike", "item_bloodthorn", "item_mjollnir", "item_travel_boots", "item_butterfly"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_maelstrom", "item_black_king_bar", "item_assault", "item_crimson_guard", "item_hurricane_pike", "item_heart"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_dragon_lance", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_maelstrom", "item_hurricane_pike"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_dragon_lance", "item_black_king_bar", "item_ghost_scepter"]},
  "consider": {
    "Q": """local ab = ab["muerta_dead_shot"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.8, snap.nearestEnemy, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["muerta_the_calling"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "location" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["muerta_pierce_the_veil"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.5 then return 0.8, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) < 0.4 then return 0.85, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "The Calling's revenants use generic targeting, with no revenant focus control; Gunslinger is passive.",
},
"naga_siren": {
  "abilities": {"Q": "naga_siren_mirror_image", "W": "naga_siren_ensnare", "E": "naga_siren_rip_tide", "R": "naga_siren_song_of_the_siren"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_radiance", "item_manta", "item_black_king_bar", "item_butterfly", "item_heart", "item_moon_shard", "item_travel_boots", "item_aghanims_scepter", "item_octarine_core", "item_nullifier"],
    2: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_radiance", "item_manta", "item_black_king_bar", "item_butterfly", "item_heart", "item_travel_boots", "item_octarine_core"],
    3: ["item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_radiance", "item_blade_mail", "item_black_king_bar", "item_crimson_guard", "item_heart", "item_manta"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_radiance", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_manta"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_radiance", "item_black_king_bar"]},
  "consider": {
    "Q": """local ab = ab["naga_siren_mirror_image"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.8, nil, "none" end
  if (snap.numEnemies or 0) >= 1 then return 0.65, nil, "none" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["naga_siren_ensnare"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    local pct = Skill.HpPctOf(t)
    if pct > 0 and pct < 0.3 then return 0.9, t, "unit" end
    return 0.75, t, "unit"
  end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["naga_siren_song_of_the_siren"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 3 then return 1.0, nil, "none" end
  if n >= 2 and (snap.numAllies or 0) >= 2 then return 0.9, nil, "none" end
  if n >= 2 and (snap.healthPct or 1) < 0.3 then return 0.9, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "No illusion micro: Mirror Images share the generic logic, with no separate image scouting, pushing or baiting; Song of the Siren follow-up depends only on ally headcount, not on ally readiness.",
},
"natures_prophet": {
  "abilities": {"Q": "furion_sprout", "W": "furion_teleportation", "E": "furion_force_of_nature", "R": "furion_wrath_of_nature"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_hand_of_midas", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_hurricane_pike", "item_aghanims_scepter", "item_travel_boots", "item_moon_shard"],
    2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_hand_of_midas", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_scythe_of_vyse", "item_travel_boots", "item_aghanims_scepter"],
    3: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_hand_of_midas", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_hurricane_pike", "item_aghanims_scepter", "item_scythe_of_vyse", "item_travel_boots", "item_moon_shard", "item_gleipnir"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_hand_of_midas", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_orchid", "item_gleipnir"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_hand_of_midas", "item_orchid", "item_gleipnir"]},
  "consider": {
    "Q": """local ab = ab["furion_sprout"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    local pct = Skill.HpPctOf(t)
    if pct > 0 and pct < 0.4 then return 0.8, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none\"""",
    "W": """local ab = ab["furion_teleportation"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.3 and (snap.numEnemies or 0) >= 1 then return 0.85, snap.location, "location" end
  if (snap.numEnemies or 0) == 0 and snap.nearbyEnemyCreeps ~= nil and #snap.nearbyEnemyCreeps > 0 then return 0.5, snap.location, "location" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["furion_force_of_nature"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if snap.nearbyEnemyCreeps ~= nil and #snap.nearbyEnemyCreeps > 0 then return 0.7, snap.nearestEnemy, "location" end
  if (snap.numEnemies or 0) >= 1 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["furion_wrath_of_nature"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local low = Skill.CountLowHpEnemies(snap, 0.35)
  if low >= 2 then return 0.95, nil, "none" end
  if low >= 1 then return 0.8, nil, "none" end
  if (snap.numEnemies or 0) >= 1 then return 0.6, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "Teleportation has no map-aware destination choice (no global target selection from lane or fight state); treants from Force of Nature use generic summon logic.",
},
"necrophos": {
  "abilities": {"Q": "necrolyte_death_pulse", "W": "necrolyte_ghost_shroud", "E": "necrolyte_heartstopper_aura", "R": "necrolyte_reapers_scythe"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_radiance", "item_black_king_bar", "item_heart", "item_assault", "item_shivas_guard", "item_aghanims_scepter", "item_travel_boots", "item_octarine_core"],
    2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_radiance", "item_black_king_bar", "item_heart", "item_shivas_guard", "item_octarine_core", "item_aghanims_scepter", "item_travel_boots", "item_scythe_of_vyse", "item_kaya_and_sange", "item_lotus_orb"],
    3: ["item_tango", "item_flask", "item_bracer", "item_arcane_boots", "item_vanguard", "item_radiance", "item_pipe_of_insight", "item_black_king_bar", "item_crimson_guard", "item_shivas_guard", "item_heart"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_radiance", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_lotus_orb", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_radiance", "item_ghost_scepter", "item_aeon_disk"]},
  "consider": {
    "Q": """local ab = ab["necrolyte_death_pulse"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.6 and (snap.numEnemies or 0) >= 1 then return 0.8, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.75, nil, "none" end
-- 对线消耗: Death Pulse 本来就是可反复放的治疗/伤害技能, 单个敌人也值得放
-- (否则对线单人满血对手时全程 0 施放, v3.2.0 实测); 蓝量留一半以上才放。
if (snap.numEnemies or 0) >= 1 and (snap.manaPct or 1) > 0.5 then return 0.6, nil, "none" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["necrolyte_ghost_shroud"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.9, nil, "none" end
  if (snap.healthPct or 1) < 0.55 and (snap.numEnemies or 0) >= 2 then return 0.75, nil, "none" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["necrolyte_reapers_scythe"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local hp = Skill.HpOf(t)
  if hp > 0 and hp < 400 then return 1.0, t, "unit" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.25 then return 0.95, t, "unit" end
  if pct > 0 and pct < 0.4 and (snap.manaPct or 1) > 0.4 then return 0.75, t, "unit" end
  return 0, nil, "none\"""",
  },
  "limitations": "Ghost Shroud silences the bot's own spells while active, which this cast decision does not weigh (no follow-up spell sequencing); Heartstopper Aura is passive.",
},
"night_stalker": {
  "abilities": {"Q": "night_stalker_void", "W": "night_stalker_crippling_fear", "E": "night_stalker_hunter_in_the_night", "R": "night_stalker_darkness"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_bracer", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_abyssal_blade", "item_assault", "item_satanic", "item_harpoon", "item_travel_boots", "item_heart"],
    2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_abyssal_blade", "item_assault", "item_satanic", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_echo_sabre", "item_black_king_bar", "item_abyssal_blade", "item_assault", "item_harpoon", "item_heart", "item_aghanims_scepter", "item_travel_boots", "item_satanic", "item_nullifier", "item_moon_shard"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_echo_sabre", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_abyssal_blade", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_echo_sabre", "item_black_king_bar", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["night_stalker_void"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    local pct = Skill.HpPctOf(t)
    if pct > 0 and pct < 0.3 then return 0.9, t, "unit" end
    return 0.75, t, "unit"
  end
  return 0, nil, "none\"""",
    "W": """local ab = ab["night_stalker_crippling_fear"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.85, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and n >= 1 then return 0.7, nil, "none" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["night_stalker_darkness"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 then return 0.7, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.6 then return 0.6, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "No day/night awareness: Void and Darkness bonuses are night-gated in reality, but the snapshot exposes no day/night flag, so Darkness may be cast while it is already night; Hunter in the Night is passive.",
},
"nyx_assassin": {
  "abilities": {"Q": "nyx_assassin_impale", "W": "nyx_assassin_mana_burn", "E": "nyx_assassin_spiked_carapace", "R": "nyx_assassin_burrow"},
  "talents": {10: 1, 15: 0, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_dagon_5", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_bloodthorn", "item_travel_boots", "item_kaya_and_sange"],
    2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_dagon_5", "item_black_king_bar", "item_aghanims_scepter", "item_euls_scepter_of_divinity", "item_octarine_core", "item_travel_boots", "item_bloodthorn"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_dagon_5", "item_vanguard", "item_black_king_bar", "item_aghanims_scepter", "item_lotus_orb", "item_shivas_guard"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_dagon_5", "item_black_king_bar", "item_aghanims_scepter", "item_force_staff", "item_glimmer_cape", "item_euls_scepter_of_divinity", "item_aether_lens", "item_octarine_core"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_dagon_5", "item_aghanims_scepter", "item_ghost_scepter"]},
  "consider": {
    "Q": """local ab = ab["nyx_assassin_impale"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.75, t, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["nyx_assassin_mana_burn"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    local pct = Skill.HpPctOf(t)
    if pct > 0 and pct < 0.35 then return 0.85, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none\"""",
    "E": """local ab = ab["nyx_assassin_spiked_carapace"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 1 then return 0.85, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.8, nil, "none" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["nyx_assassin_burrow"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.85, nil, "none" end
  if (snap.numEnemies or 0) >= 2 then return 0.7, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "No enemy-mana readout exists in the allowed API, so Mana Burn targets the lowest-HP enemy as a proxy instead of the highest-mana target it should prefer; Burrow's underground sub-abilities are not modeled (cast-only).",
},
}
