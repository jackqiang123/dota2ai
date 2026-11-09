# -*- coding: utf-8 -*-
"""A 组英雄深度数据 (Dota 2 AI v3.0.0)。
覆盖 20 个英雄: abaddon, alchemist, ancient_apparition, anti_mage, arc_warden,
bane, batrider, beastmaster, bloodseeker, bounty_hunter, brewmaster, bristleback,
broodmother, centaur_warrunner, chaos_knight, chen, clinkz, clockwerk, dark_seer,
dark_willow。
事实源: 技能名来自 tools/skill_names_reference.json (只用其中给定的 Q/W/E/R 四个
内部名); 位置/主属性/分路来自 tools/heroes_data.py; 格式抄 tools/focus_heroes.py。
consider: 每段 Lua 的签名与 focus_heroes 相同 ConsiderX(bot, snap, ab), 返回
desire(0-1), target, castType ("unit" / "location" / "none")。被动技能只返回
return 0, nil, "none"。talents 为本项目自选, 非官方推荐。
"""
ALL_A = {
"abaddon": {
  "abilities": {"Q": "abaddon_death_coil", "W": "abaddon_aphotic_shield", "E": "abaddon_frostmourne", "R": "abaddon_borrowed_time"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_vanguard", "item_radiance", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_manta", "item_aghanims_scepter", "item_travel_boots"], 2: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_echo_sabre", "item_radiance", "item_black_king_bar", "item_manta", "item_butterfly", "item_satanic", "item_aghanims_scepter", "item_travel_boots"], 3: ["item_tango", "item_flask", "item_bracer", "item_vanguard", "item_phase_boots", "item_blink", "item_radiance", "item_black_king_bar", "item_assault", "item_heart", "item_pipe_of_insight", "item_crimson_guard", "item_aghanims_scepter", "item_lotus_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_aghanims_scepter", "item_lotus_orb"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_lotus_orb", "item_pipe_of_insight"]},
  "consider": {
    "Q": """local ab = ab["abaddon_death_coil"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.55 then return 0.8, ally, "unit" end
  if (snap.healthPct or 1) < 0.4 then return 0.7, bot, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 and Skill.HpPctOf(t) < 0.4 then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["abaddon_aphotic_shield"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.5 then return 0.9, ally, "unit" end
  if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 1 then return 0.85, bot, "unit" end
  if ally ~= nil and pct < 0.7 and (snap.numEnemies or 0) >= 2 then return 0.6, ally, "unit" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["abaddon_borrowed_time"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 1.0, nil, "none" end
  if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 2 then return 0.85, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"alchemist": {
  "abilities": {"Q": "alchemist_acid_spray", "W": "alchemist_unstable_concoction", "E": "alchemist_goblins_greed", "R": "alchemist_chemical_rage"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_radiance", "item_armlet", "item_black_king_bar", "item_assault", "item_heart", "item_abyssal_blade", "item_manta", "item_aghanims_scepter", "item_travel_boots", "item_moon_shard"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_radiance", "item_black_king_bar", "item_octarine_core", "item_aghanims_scepter", "item_shivas_guard", "item_bloodstone", "item_travel_boots"], 3: ["item_tango", "item_flask", "item_bracer", "item_vanguard", "item_phase_boots", "item_radiance", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_pipe_of_insight", "item_aghanims_shard"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_aghanims_scepter", "item_lotus_orb", "item_spirit_vessel"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_pipe_of_insight", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["alchemist_acid_spray"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 and (snap.manaPct or 1) > 0.3 then return 0.55, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["alchemist_unstable_concoction"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.35 then return 0.9, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["alchemist_chemical_rage"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = snap.numEnemies or 0
  if n >= 2 and (snap.healthPct or 1) > 0.4 then return 0.85, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) < 0.4 then return 0.8, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.7 then return 0.55, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"ancient_apparition": {
  "abilities": {"Q": "ancient_apparition_cold_feet", "W": "ancient_apparition_ice_vortex", "E": "ancient_apparition_chilling_touch", "R": "ancient_apparition_ice_blast"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_manta", "item_butterfly", "item_satanic", "item_aghanims_scepter"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_aether_lens", "item_kaya_and_sange", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_aether_lens", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_shivas_guard", "item_aghanims_scepter", "item_pipe_of_insight", "item_lotus_orb", "item_ghost_scepter"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_euls_scepter_of_divinity", "item_rod_of_atos", "item_aghanims_scepter"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_aghanims_scepter", "item_ghost_scepter", "item_black_king_bar", "item_spirit_vessel"]},
  "consider": {
    "Q": """local ab = ab["ancient_apparition_cold_feet"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.35 then return 0.8, t, "unit" end
    return 0.6, t, "unit"
  end
  return 0, nil, "none"
""",
    "W": """local ab = ab["ancient_apparition_ice_vortex"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.5, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["ancient_apparition_chilling_touch"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.5 then return 0.6, bot, "unit" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["ancient_apparition_ice_blast"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local low = Skill.CountLowHpEnemies(snap, 0.35)
  if low >= 2 then return 0.95, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.25 then return 0.85, nil, "none" end
  if (snap.numEnemies or 0) >= 3 then return 0.7, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"anti_mage": {
  "abilities": {"Q": "antimage_mana_break", "W": "antimage_blink", "E": "antimage_counterspell", "R": "antimage_mana_void"},
  "talents": {10: 1, 15: 0, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_battle_fury", "item_manta", "item_black_king_bar", "item_abyssal_blade", "item_butterfly", "item_satanic", "item_monkey_king_bar", "item_aghanims_scepter", "item_travel_boots"], 2: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_battle_fury", "item_echo_sabre", "item_manta", "item_black_king_bar", "item_abyssal_blade", "item_butterfly", "item_aghanims_scepter", "item_nullifier"], 3: ["item_tango", "item_flask", "item_bracer", "item_vanguard", "item_phase_boots", "item_battle_fury", "item_black_king_bar", "item_manta", "item_assault", "item_heart", "item_abyssal_blade", "item_aghanims_shard"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_diffusal_blade", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_black_king_bar", "item_aghanims_scepter"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_lotus_orb", "item_diffusal_blade"]},
  "consider": {
    "Q": """return 0, nil, "none"
""",
    "W": """local ab = ab["antimage_blink"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.3 and (snap.numEnemies or 0) >= 1 then return 0.9, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.3 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.75, t, "location" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["antimage_counterspell"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) < 0.6 then return 0.7, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) < 0.45 then return 0.75, nil, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["antimage_mana_void"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local hp = Skill.HpOf(t)
  if hp > 0 and hp < 400 then return 1.0, t, "unit" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.3 then return 0.95, t, "unit" end
  if pct > 0 and pct < 0.45 then return 0.8, t, "unit" end
  return 0, nil, "none"
""",
  },
  "limitations": "技能名前缀 antimage_ 与英雄键 anti_mage 不一致, 是沿用的旧内部前缀, 按 skill_names_reference.json 原样使用, 未自行改名。",
},
"arc_warden": {
  "abilities": {"Q": "arc_warden_flux", "W": "arc_warden_magnetic_field", "E": "arc_warden_spark_wraith", "R": "arc_warden_tempest_double"},
  "talents": {10: 0, 15: 0, 20: 1, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_hand_of_midas", "item_maelstrom", "item_manta", "item_hurricane_pike", "item_black_king_bar", "item_butterfly", "item_satanic", "item_mjollnir", "item_travel_boots"], 2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_hand_of_midas", "item_maelstrom", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_manta", "item_scythe_of_vyse", "item_mjollnir", "item_travel_boots"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_hand_of_midas", "item_maelstrom", "item_black_king_bar", "item_assault", "item_heart", "item_manta", "item_aghanims_scepter", "item_shivas_guard"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_gleipnir", "item_aghanims_scepter", "item_black_king_bar"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_rod_of_atos", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["arc_warden_flux"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if (snap.numEnemies or 0) == 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.85, t, "unit" end
  if (snap.numEnemies or 0) >= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.5, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["arc_warden_magnetic_field"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 and (snap.healthPct or 1) < 0.5 then return 0.7, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["arc_warden_spark_wraith"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["arc_warden_tempest_double"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.level or 0) < 6 then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) > 0.4 then return 0.85, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.6 then return 0.6, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"bane": {
  "abilities": {"Q": "bane_enfeeble", "W": "bane_brain_sap", "E": "bane_nightmare", "R": "bane_fiends_grip"},
  "talents": {10: 1, 15: 1, 20: 0, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_manta", "item_abyssal_blade", "item_satanic", "item_butterfly", "item_aghanims_scepter"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_aether_lens", "item_kaya_and_sange", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_bloodstone"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_aether_lens", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_pipe_of_insight", "item_lotus_orb", "item_aeon_disk"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_aghanims_scepter", "item_euls_scepter_of_divinity"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_black_king_bar", "item_aghanims_scepter", "item_ghost_scepter", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["bane_enfeeble"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.6, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["bane_brain_sap"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    if (snap.healthPct or 1) < 0.5 then return 0.85, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none"
""",
    "E": """local ab = ab["bane_nightmare"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then
    if Skill.HpPctOf(t) < 0.4 then return 0.85, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none"
""",
    "R": """local ab = ab["bane_fiends_grip"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    if Skill.HpPctOf(t) < 0.5 then return 0.95, t, "unit" end
    if (snap.numEnemies or 0) >= 2 then return 0.8, t, "unit" end
  end
  return 0, nil, "none"
""",
  },
},
"batrider": {
  "abilities": {"Q": "batrider_sticky_napalm", "W": "batrider_flamebreak", "E": "batrider_firefly", "R": "batrider_flaming_lasso"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_blink", "item_black_king_bar", "item_manta", "item_assault", "item_heart", "item_radiance", "item_aghanims_scepter", "item_travel_boots", "item_butterfly"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_blink", "item_force_staff", "item_black_king_bar", "item_kaya_and_sange", "item_octarine_core", "item_aghanims_scepter", "item_shivas_guard"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_force_staff", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_pipe_of_insight", "item_shivas_guard", "item_lotus_orb", "item_travel_boots", "item_aeon_disk"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_euls_scepter_of_divinity", "item_aghanims_scepter", "item_black_king_bar"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_lotus_orb", "item_pipe_of_insight"]},
  "consider": {
    "Q": """local ab = ab["batrider_sticky_napalm"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.7, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["batrider_flamebreak"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["batrider_firefly"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.75, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.4 then return 0.7, nil, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["batrider_flaming_lasso"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then
    if Skill.HpPctOf(t) < 0.5 and (snap.numAllies or 0) >= 1 then return 0.95, t, "unit" end
    if Skill.HpPctOf(t) < 0.5 then return 0.9, t, "unit" end
    if (snap.numAllies or 0) >= 2 then return 0.75, t, "unit" end
  end
  return 0, nil, "none"
""",
  },
},
"beastmaster": {
  "abilities": {"Q": "beastmaster_wild_axes", "W": "beastmaster_call_of_the_wild", "E": "beastmaster_call_of_the_wild_boar", "R": "beastmaster_primal_roar"},
  "talents": {10: 1, 15: 0, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_helm_of_the_dominator", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_aghanims_scepter", "item_manta", "item_travel_boots", "item_abyssal_blade"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_helm_of_the_dominator", "item_blink", "item_black_king_bar", "item_kaya_and_sange", "item_aghanims_scepter", "item_octarine_core", "item_shivas_guard"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_helm_of_the_dominator", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_assault", "item_heart", "item_pipe_of_insight", "item_shivas_guard", "item_lotus_orb", "item_travel_boots"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_helm_of_the_dominator", "item_blink", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_aghanims_scepter"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_helm_of_the_dominator", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["beastmaster_wild_axes"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.55, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["beastmaster_call_of_the_wild"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 then return 0.6, nil, "none" end
  if (snap.time or 0) < 240 then return 0.55, nil, "none" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["beastmaster_call_of_the_wild_boar"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 then return 0.6, nil, "none" end
  if #snap.nearbyEnemyCreeps > 0 then return 0.5, nil, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["beastmaster_primal_roar"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and (snap.numAllies or 0) >= 1 then return 0.95, t, "unit" end
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.85, t, "unit" end
  return 0, nil, "none"
""",
  },
  "limitations": "v3.0 已订正: R 为 beastmaster_primal_roar(原始咆哮, 单体控制)。W/E 仍为 call_of_the_wild 与 call_of_the_wild_boar 两项旧版拆分名, 与现行单技能双召唤形态不符, 按原样使用, 野兽无独立微操。",
},
"bloodseeker": {
  "abilities": {"Q": "bloodseeker_bloodrage", "W": "bloodseeker_blood_bath", "E": "bloodseeker_thirst", "R": "bloodseeker_rupture"},
  "talents": {10: 0, 15: 0, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_blade_mail", "item_black_king_bar", "item_sange_and_yasha", "item_manta", "item_butterfly", "item_satanic", "item_abyssal_blade", "item_monkey_king_bar", "item_travel_boots"], 2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_blade_mail", "item_maelstrom", "item_black_king_bar", "item_sange_and_yasha", "item_manta", "item_mjollnir", "item_aghanims_scepter"], 3: ["item_tango", "item_flask", "item_bracer", "item_vanguard", "item_phase_boots", "item_blade_mail", "item_black_king_bar", "item_sange_and_yasha", "item_assault", "item_heart", "item_abyssal_blade", "item_aghanims_shard"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_blade_mail", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_black_king_bar", "item_spirit_vessel"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_blade_mail", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["bloodseeker_bloodrage"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.5 then return 0.75, t, "unit" end
    return 0.6, t, "unit"
  end
  return 0, nil, "none"
""",
    "W": """local ab = ab["bloodseeker_blood_bath"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if n >= 1 and t ~= nil and Skill.HpPctOf(t) < 0.5 then return 0.75, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["bloodseeker_rupture"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.4 then return 1.0, t, "unit" end
    if Skill.HpPctOf(t) < 0.6 and (snap.numAllies or 0) >= 1 then return 0.85, t, "unit" end
  end
  return 0, nil, "none"
""",
  },
  "limitations": "W 的内部名 blood_bath 对应显示名 Blood Rite, 是旧内部名, 按参考文件原样使用。Rupture 无法从 snap 读到目标是否正在移动或回血, 故用目标血量阈值(低于 40% 必放、低于 60% 且有队友跟进才放)作为是否值得撕裂的代理条件。",
},
"bounty_hunter": {
  "abilities": {"Q": "bounty_hunter_shuriken_toss", "W": "bounty_hunter_jinada", "E": "bounty_hunter_wind_walk", "R": "bounty_hunter_track"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_diffusal_blade", "item_black_king_bar", "item_manta", "item_butterfly", "item_satanic", "item_abyssal_blade", "item_monkey_king_bar", "item_aghanims_scepter", "item_travel_boots"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_diffusal_blade", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_aghanims_scepter", "item_scythe_of_vyse", "item_travel_boots"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_diffusal_blade", "item_blink", "item_black_king_bar", "item_solar_crest", "item_assault", "item_heart", "item_aghanims_scepter", "item_lotus_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_diffusal_blade", "item_solar_crest", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_aghanims_scepter", "item_urn_of_shadows", "item_spirit_vessel"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_solar_crest", "item_lotus_orb", "item_spirit_vessel", "item_diffusal_blade"]},
  "consider": {
    "Q": """local ab = ab["bounty_hunter_shuriken_toss"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.3 then return 0.9, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none"
""",
    "W": """return 0, nil, "none"
""",
    "E": """local ab = ab["bounty_hunter_wind_walk"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.85, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.6 then return 0.6, nil, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["bounty_hunter_track"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 then
    if (snap.numEnemies or 0) >= 2 then return 0.8, t, "unit" end
    if Skill.HpPctOf(t) < 0.5 then return 0.75, t, "unit" end
  end
  return 0, nil, "none"
""",
  },
  "limitations": "Track 无法从 snap 读到目标的身价/赏金价值, 故用团战人数(2 人以上必标记)和目标残血作为标记价值的代理条件, 不是按真实赏金挑选目标。",
},
"brewmaster": {
  "abilities": {"Q": "brewmaster_thunder_clap", "W": "brewmaster_drunken_haze", "E": "brewmaster_drunken_brawler", "R": "brewmaster_primal_split"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_radiance", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_manta", "item_aghanims_scepter", "item_travel_boots", "item_abyssal_blade"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_radiance", "item_blink", "item_black_king_bar", "item_kaya_and_sange", "item_octarine_core", "item_aghanims_scepter", "item_shivas_guard"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_blink", "item_radiance", "item_black_king_bar", "item_aghanims_scepter", "item_assault", "item_heart", "item_pipe_of_insight", "item_shivas_guard", "item_lotus_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_aghanims_scepter", "item_black_king_bar"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_lotus_orb", "item_pipe_of_insight"]},
  "consider": {
    "Q": """local ab = ab["brewmaster_thunder_clap"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["brewmaster_drunken_haze"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["brewmaster_primal_split"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 3 then return 1.0, nil, "none" end
  if n >= 2 and (snap.healthPct or 1) < 0.6 then return 0.9, nil, "none" end
  if n >= 2 then return 0.8, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"bristleback": {
  "abilities": {"Q": "bristleback_viscous_nasal_goo", "W": "bristleback_quill_spray", "E": "bristleback_bristleback", "R": "bristleback_warpath"},
  "talents": {10: 1, 15: 1, 20: 0, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_vanguard", "item_black_king_bar", "item_assault", "item_heart", "item_manta", "item_aghanims_scepter", "item_abyssal_blade", "item_travel_boots", "item_satanic"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_vanguard", "item_black_king_bar", "item_kaya_and_sange", "item_octarine_core", "item_aghanims_scepter", "item_shivas_guard", "item_heart"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_crimson_guard", "item_black_king_bar", "item_aghanims_scepter", "item_assault", "item_heart", "item_pipe_of_insight", "item_shivas_guard", "item_lotus_orb", "item_travel_boots"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_vanguard", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_black_king_bar", "item_aghanims_scepter"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_vanguard", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["bristleback_viscous_nasal_goo"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    if Skill.HpPctOf(t) < 0.4 then return 0.85, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none"
""",
    "W": """local ab = ab["bristleback_quill_spray"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.85, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.4 then return 0.6, nil, "none" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """return 0, nil, "none"
""",
  },
  "limitations": "R 的 Warpath 是被动叠层增益, 不是可施放大招, 故按被动处理, 只返回 0。",
},
"broodmother": {
  "abilities": {"Q": "broodmother_spawn_spiderlings", "W": "broodmother_spin_web", "E": "broodmother_incapacitating_bite", "R": "broodmother_insatiable_hunger"},
  "talents": {10: 0, 15: 0, 20: 1, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_manta", "item_butterfly", "item_satanic", "item_abyssal_blade", "item_monkey_king_bar", "item_travel_boots"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_orchid", "item_kaya_and_sange", "item_black_king_bar", "item_bloodthorn", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_orchid", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_bloodthorn", "item_aghanims_scepter", "item_lotus_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_orchid", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_black_king_bar", "item_aghanims_scepter"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_orchid", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["broodmother_spawn_spiderlings"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    if Skill.HpPctOf(t) < 0.3 then return 0.95, t, "unit" end
    return 0.75, t, "unit"
  end
  return 0, nil, "none"
""",
    "W": """local ab = ab["broodmother_spin_web"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 1 then return 0.7, snap.nearestEnemy, "location" end
  if (snap.numEnemies or 0) >= 1 then return 0.55, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["broodmother_insatiable_hunger"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) > 0.4 then return 0.85, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.4 then return 0.75, nil, "none" end
  return 0, nil, "none"
""",
  },
  "limitations": "E 的 Incapacitating Bite 是被动, 故按被动处理, 只返回 0。",
},
"centaur_warrunner": {
  "abilities": {"Q": "centaur_hoof_stomp", "W": "centaur_double_edge", "E": "centaur_return", "R": "centaur_stampede"},
  "talents": {10: 1, 15: 0, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_blink", "item_black_king_bar", "item_heart", "item_assault", "item_aghanims_scepter", "item_abyssal_blade", "item_manta", "item_travel_boots", "item_shivas_guard"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_blink", "item_black_king_bar", "item_kaya_and_sange", "item_heart", "item_aghanims_scepter", "item_octarine_core", "item_shivas_guard"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_blink", "item_black_king_bar", "item_heart", "item_assault", "item_pipe_of_insight", "item_crimson_guard", "item_shivas_guard", "item_aghanims_scepter", "item_lotus_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_black_king_bar", "item_aghanims_scepter"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_vanguard", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["centaur_hoof_stomp"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 350)
  if n >= 2 then return 0.9, nil, "none" end
  if n >= 1 then return 0.65, nil, "none" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["centaur_double_edge"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 and (snap.healthPct or 1) > 0.35 then
    if Skill.HpPctOf(t) < 0.3 then return 0.9, t, "unit" end
    return 0.75, t, "unit"
  end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["centaur_stampede"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  if (snap.numAllies or 0) >= 2 and (snap.numEnemies or 0) >= 2 then return 0.85, nil, "none" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.8, nil, "none" end
  if (snap.numEnemies or 0) >= 2 then return 0.7, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"chaos_knight": {
  "abilities": {"Q": "chaos_knight_chaos_bolt", "W": "chaos_knight_reality_rift", "E": "chaos_knight_chaos_strike", "R": "chaos_knight_phantasm"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_armlet", "item_manta", "item_black_king_bar", "item_heart", "item_assault", "item_satanic", "item_butterfly", "item_aghanims_scepter", "item_travel_boots"], 2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_power_treads", "item_armlet", "item_echo_sabre", "item_manta", "item_black_king_bar", "item_heart", "item_harpoon", "item_aghanims_scepter"], 3: ["item_tango", "item_flask", "item_bracer", "item_vanguard", "item_phase_boots", "item_armlet", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_manta", "item_aghanims_shard"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_armlet", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_black_king_bar", "item_aghanims_scepter"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_armlet", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["chaos_knight_chaos_bolt"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    if Skill.HpPctOf(t) < 0.35 then return 0.9, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none"
""",
    "W": """local ab = ab["chaos_knight_reality_rift"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then
    if (snap.numAllies or 0) >= 1 then return 0.85, t, "unit" end
    return 0.65, t, "unit"
  end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["chaos_knight_phantasm"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) > 0.5 then return 0.9, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.5 then return 0.8, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"chen": {
  "abilities": {"Q": "chen_penitence", "W": "chen_test_of_faith", "E": "chen_holy_persuasion", "R": "chen_hand_of_god"},
  "talents": {10: 1, 15: 0, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_hand_of_midas", "item_black_king_bar", "item_manta", "item_butterfly", "item_satanic", "item_abyssal_blade", "item_aghanims_scepter", "item_travel_boots", "item_monkey_king_bar"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_hand_of_midas", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_bloodstone"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_hand_of_midas", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_pipe_of_insight", "item_shivas_guard", "item_lotus_orb", "item_aeon_disk"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_hand_of_midas", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_aghanims_scepter", "item_pipe_of_insight"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_hand_of_midas", "item_aghanims_scepter", "item_pipe_of_insight", "item_force_staff", "item_glimmer_cape", "item_lotus_orb", "item_meteor_hammer"]},
  "consider": {
    "Q": """local ab = ab["chen_penitence"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.4 then return 0.8, t, "unit" end
    return 0.65, t, "unit"
  end
  return 0, nil, "none"
""",
    "W": """local ab = ab["chen_test_of_faith"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.4 then return 0.9, ally, "unit" end
  if ally ~= nil and pct < 0.6 and (snap.numEnemies or 0) >= 2 then return 0.8, ally, "unit" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["chen_holy_persuasion"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.time or 0) < 180 and #snap.nearbyEnemyCreeps > 0 then return 0.8, snap.nearbyEnemyCreeps[1], "unit" end
  if (snap.numEnemies or 0) == 0 and #snap.nearbyEnemyCreeps > 0 then return 0.6, snap.nearbyEnemyCreeps[1], "unit" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["chen_hand_of_god"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.35 then return 1.0, nil, "none" end
  if (snap.healthPct or 1) < 0.4 then return 0.9, nil, "none" end
  if ally ~= nil and pct < 0.5 and (snap.numEnemies or 0) >= 2 then return 0.85, nil, "none" end
  return 0, nil, "none"
""",
  },
  "limitations": "Chen 无独立召唤物微操: Holy Persuasion 只在开局 180 秒内或无敌方英雄在场且附近有野怪时劝化, 且只取 nearbyEnemyCreeps 的第一只, 不挑选野怪种类、不控制劝化后的野怪。另参考文件注明 hand_of_god 是 Ability5, Q/W/E/R 映射按给定文件原样使用。Test of Faith 按救援队友(传送残血队友)的理解写, 若该技能现行机制不同, 此段需按实测修正。",
},
"clinkz": {
  "abilities": {"Q": "clinkz_strafe", "W": "clinkz_searing_arrows", "E": "clinkz_skeleton_walk", "R": "clinkz_death_pact"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_desolator", "item_black_king_bar", "item_daedalus", "item_butterfly", "item_satanic", "item_monkey_king_bar", "item_abyssal_blade", "item_aghanims_scepter", "item_travel_boots"], 2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_desolator", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_daedalus", "item_aghanims_scepter", "item_nullifier"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_desolator", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_daedalus", "item_aghanims_scepter", "item_lotus_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_desolator", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_black_king_bar", "item_aghanims_scepter"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_desolator", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["clinkz_strafe"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    if Skill.HpPctOf(t) < 0.35 then return 0.85, nil, "none" end
    return 0.75, nil, "none"
  end
  return 0, nil, "none"
""",
    "W": """local ab = ab["clinkz_searing_arrows"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and (snap.manaPct or 1) > 0.3 then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["clinkz_skeleton_walk"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.9, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.6 then return 0.6, nil, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["clinkz_death_pact"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) > 0.5 and #snap.nearbyEnemyCreeps > 0 then return 0.7, snap.nearbyEnemyCreeps[1], "unit" end
  return 0, nil, "none"
""",
  },
  "limitations": "v3.0 已订正: E 为 clinkz_skeleton_walk(骷髅漫步)。Death Pact 只取附近第一只野怪, 不挑野怪种类。",
},
"clockwerk": {
  "abilities": {"Q": "rattletrap_battery_assault", "W": "rattletrap_power_cogs", "E": "rattletrap_rocket_flare", "R": "rattletrap_hookshot"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_blade_mail", "item_black_king_bar", "item_assault", "item_heart", "item_aghanims_scepter", "item_manta", "item_abyssal_blade", "item_travel_boots", "item_shivas_guard"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_blade_mail", "item_aether_lens", "item_black_king_bar", "item_kaya_and_sange", "item_aghanims_scepter", "item_octarine_core", "item_shivas_guard"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blade_mail", "item_force_staff", "item_black_king_bar", "item_aghanims_scepter", "item_pipe_of_insight", "item_shivas_guard", "item_lotus_orb", "item_aeon_disk", "item_travel_boots", "item_crimson_guard"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_blade_mail", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_black_king_bar", "item_aghanims_scepter"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_blade_mail", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["rattletrap_battery_assault"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 300)
  if n >= 2 then return 0.85, nil, "none" end
  if n >= 1 then return 0.75, nil, "none" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["rattletrap_power_cogs"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.85, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 then return 0.8, nil, "none" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["rattletrap_rocket_flare"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.35 then return 0.7, t, "location" end
  if (snap.numEnemies or 0) >= 1 then return 0.5, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["rattletrap_hookshot"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if Skill.HpPctOf(t) < 0.3 then return 0.9, t, "location" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist > 600 then return 0.75, t, "location" end
  return 0, nil, "none"
""",
  },
  "limitations": "技能名前缀 rattletrap_ 与英雄键 clockwerk 不一致, 是沿用的旧内部前缀(发条旧名 Rattletrap), 按 skill_names_reference.json 原样使用, 未自行改名。",
},
"dark_seer": {
  "abilities": {"Q": "dark_seer_vacuum", "W": "dark_seer_ion_shell", "E": "dark_seer_surge", "R": "dark_seer_wall_of_replica"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_shivas_guard", "item_aghanims_scepter", "item_manta", "item_travel_boots", "item_octarine_core"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_blink", "item_aether_lens", "item_black_king_bar", "item_kaya_and_sange", "item_aghanims_scepter", "item_octarine_core", "item_shivas_guard"], 3: ["item_tango", "item_flask", "item_bracer", "item_arcane_boots", "item_blink", "item_pipe_of_insight", "item_shivas_guard", "item_black_king_bar", "item_aghanims_scepter", "item_lotus_orb", "item_octarine_core", "item_aeon_disk", "item_travel_boots", "item_heart"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_pipe_of_insight", "item_aghanims_scepter", "item_black_king_bar"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_pipe_of_insight", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["dark_seer_vacuum"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["dark_seer_ion_shell"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally = Skill.LowestHpAlly(snap)
  if ally ~= nil then return 0.7, ally, "unit" end
  if #snap.nearbyAllyCreeps > 0 then return 0.6, snap.nearbyAllyCreeps[1], "unit" end
  if (snap.healthPct or 1) > 0.5 then return 0.55, bot, "unit" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["dark_seer_surge"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.5 then return 0.85, ally, "unit" end
  if (snap.healthPct or 1) < 0.4 then return 0.8, bot, "unit" end
  if ally ~= nil and (snap.numEnemies or 0) >= 2 then return 0.6, ally, "unit" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["dark_seer_wall_of_replica"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
  },
},
"dark_willow": {
  "abilities": {"Q": "dark_willow_bramble_maze", "W": "dark_willow_shadow_realm", "E": "dark_willow_cursed_crown", "R": "dark_willow_terrorize"},
  "talents": {10: 1, 15: 1, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_witch_blade", "item_black_king_bar", "item_manta", "item_butterfly", "item_satanic", "item_scythe_of_vyse", "item_aghanims_scepter", "item_travel_boots", "item_monkey_king_bar"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_witch_blade", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_kaya_and_sange", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_witch_blade", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_pipe_of_insight", "item_lotus_orb", "item_aeon_disk"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_euls_scepter_of_divinity", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_ghost_scepter", "item_rod_of_atos"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_euls_scepter_of_divinity", "item_lotus_orb", "item_aghanims_scepter", "item_spirit_vessel"]},
  "consider": {
    "Q": """local ab = ab["dark_willow_bramble_maze"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["dark_willow_shadow_realm"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.9, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.6 then return 0.6, nil, "none" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["dark_willow_cursed_crown"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.4 then return 0.9, t, "unit" end
    return 0.75, t, "unit"
  end
  return 0, nil, "none"
""",
    "R": """local ab = ab["dark_willow_terrorize"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if n >= 1 and t ~= nil and Skill.HpPctOf(t) < 0.3 then return 0.8, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
  },
},
}
