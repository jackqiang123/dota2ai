# -*- coding: utf-8 -*-
"""D 组英雄深度数据 (v3.0.0)。
20 heroes: ogre_magi .. shadow_shaman. Format mirrors tools/focus_heroes.py.
abilities use only tools/skill_names_reference.json names; suspicious names are
flagged in each hero's limitations, never silently replaced.
"""
ALL_D = {
"ogre_magi": {
  "abilities": {"Q": "ogre_magi_fireblast", "W": "ogre_magi_ignite", "E": "ogre_magi_bloodlust", "R": "ogre_magi_unrefined_fireblast"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_bracer", "item_power_treads", "item_hand_of_midas", "item_aghanims_scepter", "item_black_king_bar", "item_assault", "item_heart", "item_moon_shard"],
    2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_power_treads", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_vanguard", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_assault", "item_heart"],
    4: ["item_tango", "item_flask", "item_clarity", "item_magic_wand", "item_bracer", "item_arcane_boots", "item_force_staff", "item_aether_lens", "item_aghanims_scepter", "item_glimmer_cape", "item_black_king_bar"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_bracer", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_aghanims_scepter", "item_lotus_orb", "item_black_king_bar"],
  },
  "consider": {
    "Q": """local ab = ab["ogre_magi_fireblast"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and Skill.HpPctOf(t) < 0.35 then return 0.95, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["ogre_magi_ignite"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and (snap.numAllies or 0) >= 1 then return 0.75, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and Skill.HpPctOf(t) < 0.5 then return 0.7, t, "unit" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["ogre_magi_bloodlust"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally = Skill.LowestHpAlly(snap)
  if ally ~= nil and (snap.numEnemies or 0) >= 1 then return 0.65, ally, "unit" end
  if (snap.healthPct or 1) > 0.5 and (snap.numEnemies or 0) >= 1 then return 0.55, bot, "unit" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["ogre_magi_unrefined_fireblast"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.5 then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and Skill.HpPctOf(t) < 0.35 then return 0.9, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and (snap.manaPct or 1) < 0.25 then return 0.75, t, "unit" end
  return 0, nil, "none"
""",
  },
  "limitations": "Reference R is ogre_magi_unrefined_fireblast, not multicast: multicast is the passive ult in-game, unrefined fireblast is the HP-cost nuke granted alongside it, so this R slot covers the nuke only and multicast procs are engine-side, not modelled here.",
},
"omniknight": {
  "abilities": {"Q": "omniknight_purification", "W": "omniknight_heavenly_grace", "E": "omniknight_degen_aura", "R": "omniknight_guardian_angel"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_bracer", "item_power_treads", "item_radiance", "item_black_king_bar", "item_assault", "item_heart", "item_manta", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_power_treads", "item_radiance", "item_black_king_bar", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_vanguard", "item_phase_boots", "item_radiance", "item_pipe_of_insight", "item_crimson_guard", "item_black_king_bar", "item_lotus_orb", "item_assault", "item_heart", "item_aghanims_scepter"],
    4: ["item_tango", "item_flask", "item_clarity", "item_magic_wand", "item_bracer", "item_arcane_boots", "item_force_staff", "item_pipe_of_insight", "item_lotus_orb", "item_glimmer_cape", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_pipe_of_insight", "item_lotus_orb", "item_aghanims_scepter"],
  },
  "consider": {
    "Q": """local ab = ab["omniknight_purification"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.35 then return 1.0, ally, "unit" end
  if ally ~= nil and pct < 0.6 and (snap.numEnemies or 0) >= 1 then return 0.8, ally, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 and Skill.HpPctOf(t) < 0.3 then return 0.7, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["omniknight_heavenly_grace"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.4 then return 0.9, ally, "unit" end
  if (snap.healthPct or 1) < 0.45 and (snap.numEnemies or 0) >= 1 then return 0.85, bot, "unit" end
  if ally ~= nil and pct < 0.65 and (snap.numEnemies or 0) >= 2 then return 0.6, ally, "unit" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["omniknight_guardian_angel"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.35 and (snap.numEnemies or 0) >= 2 then return 1.0, nil, "none" end
  if (snap.numAllies or 0) >= 2 and (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) < 0.6 then return 0.9, nil, "none" end
  return 0, nil, "none"
""",
  },
  "limitations": "v3.0 已订正: W 为 omniknight_heavenly_grace(天堂恩赐, 原 Repel 更名)。",
},
"outworld_destroyer": {
  "abilities": {"Q": "obsidian_destroyer_arcane_orb", "W": "obsidian_destroyer_astral_imprisonment", "E": "obsidian_destroyer_essence_aura", "R": "obsidian_destroyer_sanity_eclipse"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_meteor_hammer", "item_black_king_bar", "item_scythe_of_vyse", "item_octarine_core", "item_manta", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_meteor_hammer", "item_black_king_bar", "item_scythe_of_vyse", "item_octarine_core", "item_kaya_and_sange", "item_aghanims_scepter", "item_travel_boots", "item_moon_shard"],
    3: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_meteor_hammer", "item_black_king_bar", "item_shivas_guard", "item_scythe_of_vyse", "item_aghanims_scepter", "item_heart"],
    4: ["item_tango", "item_flask", "item_clarity", "item_null_talisman", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_meteor_hammer", "item_force_staff", "item_glimmer_cape", "item_black_king_bar"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer"],
  },
  "consider": {
    "Q": """local ab = ab["obsidian_destroyer_arcane_orb"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if (snap.manaPct or 0) < 0.25 then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and Skill.HpPctOf(t) < 0.35 then return 0.8, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.6, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["obsidian_destroyer_astral_imprisonment"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.3 and (snap.numEnemies or 0) >= 1 then return 0.95, ally, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and (snap.numAllies or 0) >= 1 and Skill.HpPctOf(t) < 0.5 then return 0.75, t, "unit" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["obsidian_destroyer_sanity_eclipse"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local low = Skill.CountLowHpEnemies(snap, 0.35)
  if low >= 2 then return 0.95, nil, "none" end
  if low >= 1 and (snap.numEnemies or 0) >= 2 then return 0.85, nil, "none" end
  if (snap.numEnemies or 0) >= 3 and (snap.manaPct or 0) > 0.5 then return 0.75, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"pangolier": {
  "abilities": {"Q": "pangolier_swashbuckle", "W": "pangolier_shield_crash", "E": "pangolier_heartpiercer", "R": "pangolier_rolling_thunder"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_phase_boots", "item_diffusal_blade", "item_black_king_bar", "item_abyssal_blade", "item_satanic", "item_butterfly", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_phase_boots", "item_diffusal_blade", "item_black_king_bar", "item_aghanims_scepter", "item_scythe_of_vyse", "item_octarine_core", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_phase_boots", "item_diffusal_blade", "item_black_king_bar", "item_aghanims_scepter", "item_assault", "item_heart", "item_scythe_of_vyse", "item_travel_boots", "item_moon_shard"],
    4: ["item_tango", "item_flask", "item_clarity", "item_magic_wand", "item_bracer", "item_arcane_boots", "item_diffusal_blade", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_aether_lens"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_diffusal_blade", "item_aether_lens"],
  },
  "consider": {
    "Q": """local ab = ab["pangolier_swashbuckle"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if snap.nearestEnemy == nil then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 900)
  if n >= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 then return 0.8, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 and Skill.HpPctOf(t) < 0.4 then return 0.85, snap.nearestEnemy, "location" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["pangolier_shield_crash"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.85, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) < 0.5 then return 0.75, nil, "none" end
  if n >= 1 and (snap.numAllies or 0) >= 1 then return 0.6, nil, "none" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["pangolier_rolling_thunder"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 3 and (snap.healthPct or 1) > 0.5 then return 1.0, snap.nearestEnemy, "none" end
  if n >= 2 and (snap.healthPct or 1) > 0.5 then return 0.9, snap.nearestEnemy, "none" end
  if n >= 1 and (snap.healthPct or 1) < 0.35 then return 0, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"phantom_assassin": {
  "abilities": {"Q": "phantom_assassin_stifling_dagger", "W": "phantom_assassin_phantom_strike", "E": "phantom_assassin_blur", "R": "phantom_assassin_coup_de_grace"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_battle_fury", "item_desolator", "item_black_king_bar", "item_satanic", "item_abyssal_blade", "item_butterfly", "item_daedalus", "item_moon_shard", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_desolator", "item_black_king_bar", "item_bloodthorn", "item_satanic", "item_abyssal_blade"],
    3: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_phase_boots", "item_desolator", "item_black_king_bar", "item_satanic", "item_abyssal_blade", "item_assault"],
    4: ["item_tango", "item_flask", "item_magic_wand", "item_wraith_band", "item_phase_boots", "item_desolator", "item_black_king_bar", "item_force_staff", "item_abyssal_blade", "item_satanic"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_phase_boots", "item_desolator", "item_black_king_bar", "item_force_staff", "item_glimmer_cape"],
  },
  "consider": {
    "Q": """local ab = ab["phantom_assassin_stifling_dagger"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 and Skill.HpPctOf(t) < 0.4 then return 0.9, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["phantom_assassin_phantom_strike"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then
    local ally = Skill.LowestHpAlly(snap)
    if ally ~= nil then return 0.85, ally, "unit" end
  end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist > 300 and snap.nearestEnemyDist <= 1000 and Skill.HpPctOf(t) < 0.5 then return 0.9, t, "unit" end
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist > 300 and snap.nearestEnemyDist <= 1000 then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """return 0, nil, "none"
""",
  },
},
"phantom_lancer": {
  "abilities": {"Q": "phantom_lancer_spirit_lance", "W": "phantom_lancer_doppelwalk", "E": "phantom_lancer_phantom_edge", "R": "phantom_lancer_juxtapose"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_diffusal_blade", "item_manta", "item_black_king_bar", "item_heart", "item_abyssal_blade", "item_butterfly", "item_satanic", "item_moon_shard", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_diffusal_blade", "item_manta", "item_black_king_bar", "item_scythe_of_vyse", "item_heart", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_phase_boots", "item_diffusal_blade", "item_manta", "item_black_king_bar", "item_heart", "item_assault", "item_abyssal_blade"],
    4: ["item_tango", "item_flask", "item_magic_wand", "item_wraith_band", "item_phase_boots", "item_diffusal_blade", "item_manta", "item_force_staff", "item_black_king_bar", "item_heart"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_phase_boots", "item_diffusal_blade", "item_manta", "item_force_staff", "item_glimmer_cape"],
  },
  "consider": {
    "Q": """local ab = ab["phantom_lancer_spirit_lance"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 and Skill.HpPctOf(t) < 0.35 then return 0.9, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["phantom_lancer_doppelwalk"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.9, snap.location, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist > 500 and snap.nearestEnemyDist <= 1000 and Skill.HpPctOf(t) < 0.4 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """return 0, nil, "none"
""",
  },
},
"phoenix": {
  "abilities": {"Q": "phoenix_icarus_dive", "W": "phoenix_fire_spirits", "E": "phoenix_sun_ray", "R": "phoenix_supernova"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_radiance", "item_shivas_guard", "item_black_king_bar", "item_heart", "item_assault", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_phase_boots", "item_radiance", "item_shivas_guard", "item_black_king_bar", "item_octarine_core", "item_aghanims_scepter"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_radiance", "item_shivas_guard", "item_black_king_bar", "item_heart", "item_pipe_of_insight", "item_aghanims_scepter"],
    4: ["item_tango", "item_flask", "item_clarity", "item_magic_wand", "item_bracer", "item_arcane_boots", "item_shivas_guard", "item_force_staff", "item_radiance", "item_black_king_bar", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_shivas_guard", "item_force_staff", "item_glimmer_cape", "item_radiance", "item_black_king_bar", "item_aghanims_scepter", "item_lotus_orb"],
  },
  "consider": {
    "Q": """local ab = ab["phoenix_icarus_dive"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.3 and (snap.numEnemies or 0) >= 1 then return 0.85, snap.nearestEnemy, "location" end
  if snap.nearestEnemy ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 400 and snap.nearestEnemyDist <= 1000 and (snap.healthPct or 1) > 0.6 then return 0.75, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 1000 and Skill.HpPctOf(t) < 0.35 then return 0.8, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["phoenix_fire_spirits"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.25 then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 900)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 and (snap.healthPct or 1) > 0.5 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["phoenix_sun_ray"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.5 and (snap.healthPct or 1) > 0.4 then return 0.8, ally, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 and Skill.HpPctOf(t) < 0.35 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["phoenix_supernova"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.55 then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 and (snap.numAllies or 0) >= 1 then return 1.0, nil, "none" end
  if n >= 1 and (snap.numAllies or 0) >= 2 and (snap.healthPct or 1) > 0.7 then return 0.85, nil, "none" end
  return 0, nil, "none"
""",
  },
  "limitations": "v3.0 已订正: R 为 phoenix_supernova(超新星)。",
},
"primal_beast": {
  "abilities": {"Q": "primal_beast_onslaught", "W": "primal_beast_trample", "E": "primal_beast_uproar", "R": "primal_beast_pulverize"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_satanic", "item_abyssal_blade", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_shivas_guard", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_vanguard", "item_phase_boots", "item_blink", "item_black_king_bar", "item_heart", "item_assault", "item_shivas_guard", "item_aghanims_scepter", "item_crimson_guard", "item_travel_boots"],
    4: ["item_tango", "item_flask", "item_clarity", "item_magic_wand", "item_bracer", "item_arcane_boots", "item_blink", "item_force_staff", "item_black_king_bar", "item_heart", "item_pipe_of_insight"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_black_king_bar"],
  },
  "consider": {
    "Q": """local ab = ab["primal_beast_onslaught"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 500 and snap.nearestEnemyDist <= 1300 then return 0.8, snap.nearestEnemy, "location" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 and Skill.HpPctOf(t) < 0.4 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["primal_beast_trample"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 and (snap.healthPct or 1) > 0.4 then return 0.8, snap.nearestEnemy, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.6 then return 0.65, snap.nearestEnemy, "none" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["primal_beast_uproar"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.6 and (snap.numEnemies or 0) >= 1 then return 0.85, nil, "none" end
  if Skill.CountEnemiesInRange(snap, 500) >= 2 then return 0.7, nil, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["primal_beast_pulverize"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 and (snap.numAllies or 0) >= 1 then return 0.95, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 and Skill.HpPctOf(t) < 0.5 then return 0.85, t, "unit" end
  return 0, nil, "none"
""",
  },
  "limitations": "v3.0 已订正: 槽位顺序为 Q 突袭 / W 践踏 / E 怒吼 / R 粉碎。",
},
"puck": {
  "abilities": {"Q": "puck_illusory_orb", "W": "puck_waning_rift", "E": "puck_phase_shift", "R": "puck_dream_coil"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_blink", "item_witch_blade", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_aeon_disk", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_null_talisman", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_lotus_orb", "item_octarine_core"],
    4: ["item_tango", "item_flask", "item_clarity", "item_null_talisman", "item_magic_wand", "item_arcane_boots", "item_blink", "item_force_staff", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_aghanims_scepter"],
  },
  "consider": {
    "Q": """local ab = ab["puck_illusory_orb"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if snap.nearestEnemy == nil then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 1000)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 1000 and Skill.HpPctOf(t) < 0.4 then return 0.85, snap.nearestEnemy, "location" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 1000 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["puck_waning_rift"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.85, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and n >= 1 and Skill.HpPctOf(t) < 0.4 then return 0.75, nil, "none" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["puck_phase_shift"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.9, nil, "none" end
  if (snap.healthPct or 1) < 0.5 and Skill.CountEnemiesInRange(snap, 400) >= 2 then return 0.8, nil, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["puck_dream_coil"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and n >= 1 and Skill.HpPctOf(t) < 0.4 then return 0.8, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
  },
},
"pudge": {
  "abilities": {"Q": "pudge_meat_hook", "W": "pudge_rot", "E": "pudge_flesh_heap", "R": "pudge_dismember"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_heart", "item_assault", "item_abyssal_blade", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_vanguard", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_heart", "item_assault", "item_shivas_guard"],
    4: ["item_tango", "item_flask", "item_clarity", "item_magic_wand", "item_bracer", "item_arcane_boots", "item_blink", "item_force_staff", "item_black_king_bar", "item_aghanims_scepter", "item_aether_lens", "item_lotus_orb", "item_ward_observer"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_aghanims_scepter"],
  },
  "consider": {
    "Q": """local ab = ab["pudge_meat_hook"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist == nil or snap.nearestEnemyDist > 1300 then return 0, nil, "none" end
  if snap.nearestEnemyDist >= 600 and (snap.numAllies or 0) >= 1 and Skill.HpPctOf(t) < 0.5 then return 0.9, t, "unit" end
  if snap.nearestEnemyDist >= 600 and (snap.numAllies or 0) >= 1 then return 0.8, t, "unit" end
  if Skill.HpPctOf(t) < 0.3 then return 0.85, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["pudge_rot"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 250 and (snap.numEnemies or 0) >= 1 then return 0.8, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 250 and Skill.HpPctOf(t) < 0.3 then return 0.9, nil, "none" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["pudge_dismember"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 250 and Skill.HpPctOf(t) < 0.4 then return 1.0, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 250 and (snap.numAllies or 0) >= 1 then return 0.9, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 250 and (snap.healthPct or 1) > 0.5 then return 0.7, t, "unit" end
  return 0, nil, "none"
""",
  },
  "limitations": "Hook has no true projectile prediction in the allowed API: there is no enemy velocity or facing in snap, so the hook fires on the lowest-HP enemy in 600-1300 range only when allies are nearby to follow up, never on a blind long-range guess.",
},
"pugna": {
  "abilities": {"Q": "pugna_nether_blast", "W": "pugna_decrepify", "E": "pugna_nether_ward", "R": "pugna_life_drain"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_dagon_5", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_aether_lens", "item_dagon_5", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_bloodstone", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_null_talisman", "item_phase_boots", "item_aether_lens", "item_dagon_5", "item_black_king_bar", "item_shivas_guard", "item_aghanims_scepter", "item_lotus_orb"],
    4: ["item_tango", "item_flask", "item_clarity", "item_null_talisman", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_dagon_5", "item_force_staff", "item_glimmer_cape", "item_black_king_bar"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_dagon_5", "item_aghanims_scepter"],
  },
  "consider": {
    "Q": """local ab = ab["pugna_nether_blast"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and n >= 1 and Skill.HpPctOf(t) < 0.4 then return 0.75, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["pugna_decrepify"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.9, ally, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 and (snap.numAllies or 0) >= 1 and Skill.HpPctOf(t) < 0.5 then return 0.8, t, "unit" end
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.6, t, "unit" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["pugna_nether_ward"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 800)
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  if n >= 1 and (snap.manaPct or 1) > 0.5 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["pugna_life_drain"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 and (snap.healthPct or 1) < 0.6 then return 0.9, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 and Skill.HpPctOf(t) < 0.3 then return 0.85, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 and (snap.numAllies or 0) >= 2 then return 0.7, t, "unit" end
  return 0, nil, "none"
""",
  },
},
"queen_of_pain": {
  "abilities": {"Q": "queenofpain_shadow_strike", "W": "queenofpain_blink", "E": "queenofpain_scream_of_pain", "R": "queenofpain_sonic_wave"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_scythe_of_vyse", "item_satanic", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_kaya_and_sange", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_null_talisman", "item_phase_boots", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_shivas_guard", "item_aghanims_scepter", "item_lotus_orb"],
    4: ["item_tango", "item_flask", "item_clarity", "item_null_talisman", "item_magic_wand", "item_arcane_boots", "item_orchid", "item_force_staff", "item_black_king_bar", "item_aether_lens", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_orchid", "item_aether_lens"],
  },
  "consider": {
    "Q": """local ab = ab["queenofpain_shadow_strike"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and Skill.HpPctOf(t) < 0.4 then return 0.85, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["queenofpain_blink"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 600 and snap.nearestEnemyDist <= 1200 and Skill.HpPctOf(t) < 0.4 then return 0.85, snap.nearestEnemy, "location" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then
    local ally = Skill.LowestHpAlly(snap)
    if ally ~= nil then return 0.9, ally, "location" end
  end
  return 0, nil, "none"
""",
    "E": """local ab = ab["queenofpain_scream_of_pain"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.85, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and n >= 1 and Skill.HpPctOf(t) < 0.4 then return 0.75, nil, "none" end
  if n >= 1 then return 0.6, nil, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["queenofpain_sonic_wave"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  local low = Skill.CountLowHpEnemies(snap, 0.35)
  if low >= 1 and n >= 1 then return 0.85, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
  },
  "limitations": "heroes_data lists the third skill type as passive, but queenofpain_scream_of_pain is an active AoE nuke, so the E Consider is written as active; the heroes_data type tag looks wrong, not the skill name.",
},
"razor": {
  "abilities": {"Q": "razor_plasma_field", "W": "razor_static_link", "E": "razor_unstable_current", "R": "razor_eye_of_the_storm"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_bloodstone", "item_black_king_bar", "item_satanic", "item_assault", "item_butterfly", "item_manta", "item_travel_boots", "item_moon_shard"],
    2: ["item_tango", "item_flask", "item_wraith_band", "item_bottle", "item_power_treads", "item_bloodstone", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_shivas_guard", "item_travel_boots", "item_moon_shard"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_bloodstone", "item_black_king_bar", "item_assault", "item_shivas_guard", "item_heart", "item_pipe_of_insight"],
    4: ["item_tango", "item_flask", "item_clarity", "item_magic_wand", "item_wraith_band", "item_arcane_boots", "item_bloodstone", "item_force_staff", "item_black_king_bar", "item_aether_lens", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_bloodstone", "item_aether_lens"],
  },
  "consider": {
    "Q": """local ab = ab["razor_plasma_field"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and n >= 1 and Skill.HpPctOf(t) < 0.4 then return 0.75, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["razor_static_link"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and (snap.healthPct or 1) > 0.5 then return 0.8, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["razor_eye_of_the_storm"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.95, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.6 then return 0.75, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"riki": {
  "abilities": {"Q": "riki_smoke_screen", "W": "riki_tricks_of_the_trade", "E": "riki_backstab", "R": "riki_blink_strike"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_phase_boots", "item_diffusal_blade", "item_black_king_bar", "item_abyssal_blade", "item_butterfly", "item_satanic", "item_monkey_king_bar", "item_manta", "item_travel_boots", "item_moon_shard"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_diffusal_blade", "item_black_king_bar", "item_orchid", "item_bloodthorn", "item_abyssal_blade", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_diffusal_blade", "item_black_king_bar", "item_abyssal_blade", "item_assault", "item_heart", "item_satanic"],
    4: ["item_tango", "item_flask", "item_magic_wand", "item_wraith_band", "item_phase_boots", "item_diffusal_blade", "item_force_staff", "item_black_king_bar", "item_abyssal_blade", "item_ward_observer", "item_ward_sentry"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_phase_boots", "item_diffusal_blade", "item_force_staff", "item_glimmer_cape", "item_black_king_bar"],
  },
  "consider": {
    "Q": """local ab = ab["riki_smoke_screen"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and n >= 1 and Skill.HpPctOf(t) < 0.4 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 and (snap.numAllies or 0) >= 1 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["riki_tricks_of_the_trade"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.75, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) < 0.5 then return 0.65, nil, "none" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["riki_blink_strike"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 and Skill.HpPctOf(t) < 0.3 then return 0.95, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 and (snap.numEnemies or 0) >= 2 then return 0.8, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
  },
  "limitations": "v3.0 已订正: W 为 riki_tricks_of_the_trade(诡计之雾, 主动 AoE)。",
},
"ringmaster": {
  "abilities": {"Q": "ringmaster_tame_the_beasts", "W": "ringmaster_the_box", "E": "ringmaster_escape_act", "R": "ringmaster_wheel_of_wonder"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_kaya_and_sange"],
    3: ["item_tango", "item_flask", "item_null_talisman", "item_phase_boots", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_lotus_orb", "item_octarine_core"],
    4: ["item_tango", "item_flask", "item_clarity", "item_null_talisman", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_aghanims_scepter", "item_ward_observer", "item_lotus_orb"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_aghanims_scepter"],
  },
  "consider": {
    "Q": """local ab = ab["ringmaster_tame_the_beasts"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if snap.nearestEnemy == nil then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 800)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 and Skill.HpPctOf(t) < 0.4 then return 0.8, snap.nearestEnemy, "location" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["ringmaster_the_box"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and (snap.numAllies or 0) >= 1 then return 0.8, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and Skill.HpPctOf(t) < 0.4 then return 0.75, t, "unit" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["ringmaster_escape_act"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.9, ally, "unit" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.85, bot, "unit" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["ringmaster_wheel_of_wonder"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and n >= 1 and Skill.HpPctOf(t) < 0.35 then return 0.8, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
  },
},
"rubick": {
  "abilities": {"Q": "rubick_telekinesis", "W": "rubick_fade_bolt", "E": "rubick_null_field", "R": "rubick_spell_steal"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_blink", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_null_talisman", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_lotus_orb", "item_octarine_core"],
    4: ["item_tango", "item_flask", "item_clarity", "item_null_talisman", "item_magic_wand", "item_arcane_boots", "item_blink", "item_aether_lens", "item_force_staff", "item_aghanims_scepter", "item_black_king_bar", "item_ward_observer"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_blink", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_aghanims_scepter", "item_black_king_bar", "item_lotus_orb"],
  },
  "consider": {
    "Q": """local ab = ab["rubick_telekinesis"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and (snap.numAllies or 0) >= 1 and Skill.HpPctOf(t) < 0.5 then return 0.9, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and (snap.numAllies or 0) >= 1 then return 0.8, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and Skill.HpPctOf(t) < 0.3 then return 0.75, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["rubick_fade_bolt"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 800)
  if n >= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.85, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 and Skill.HpPctOf(t) < 0.4 then return 0.8, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.6, t, "unit" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["rubick_spell_steal"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if snap.nearestEnemy == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 1000 and (snap.numEnemies or 0) >= 2 then return 0.7, snap.nearestEnemy, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 1000 and (snap.numAllies or 0) >= 1 then return 0.6, snap.nearestEnemy, "unit" end
  return 0, nil, "none"
""",
  },
  "limitations": "Spell Steal only covers the steal itself: the stolen spell arrives in a dynamic extra slot whose internal name and cast type are only known at runtime, and the Bot API has no generic cast-arbitrary-stolen-spell call in the allowed set, so this file deliberately does NOT pretend to cast stolen spells - using a stolen spell needs a runtime slot lookup plus a per-spell cast wrapper that is not in scope here.",
},
"sand_king": {
  "abilities": {"Q": "sandking_burrowstrike", "W": "sandking_sand_storm", "E": "sandking_caustic_finale", "R": "sandking_epicenter"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_assault", "item_heart", "item_shivas_guard", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_vanguard", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_heart", "item_assault", "item_crimson_guard", "item_lotus_orb", "item_travel_boots"],
    4: ["item_tango", "item_flask", "item_clarity", "item_magic_wand", "item_bracer", "item_arcane_boots", "item_blink", "item_force_staff", "item_black_king_bar", "item_aghanims_scepter", "item_aether_lens", "item_ward_observer"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_aghanims_scepter"],
  },
  "consider": {
    "Q": """local ab = ab["sandking_burrowstrike"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and n >= 1 and Skill.HpPctOf(t) < 0.4 then return 0.85, snap.nearestEnemy, "location" end
  if n >= 1 and (snap.numAllies or 0) >= 1 then return 0.7, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["sandking_sand_storm"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 and (snap.healthPct or 1) > 0.4 then return 0.8, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) < 0.4 then return 0.75, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.6 then return 0.6, nil, "none" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["sandking_epicenter"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 3 then return 1.0, nil, "none" end
  if n >= 2 then return 0.9, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and n >= 1 and Skill.HpPctOf(t) < 0.35 then return 0.8, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"shadow_demon": {
  "abilities": {"Q": "shadow_demon_disruption", "W": "shadow_demon_soul_catcher", "E": "shadow_demon_shadow_poison", "R": "shadow_demon_demonic_purge"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_kaya_and_sange"],
    3: ["item_tango", "item_flask", "item_null_talisman", "item_phase_boots", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_lotus_orb", "item_octarine_core"],
    4: ["item_tango", "item_flask", "item_clarity", "item_null_talisman", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_aghanims_scepter", "item_ward_observer"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_aghanims_scepter", "item_lotus_orb"],
  },
  "consider": {
    "Q": """local ab = ab["shadow_demon_disruption"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.3 and (snap.numEnemies or 0) >= 1 then return 0.95, ally, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 and (snap.numAllies or 0) >= 1 then return 0.8, t, "unit" end
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 and Skill.HpPctOf(t) < 0.4 then return 0.75, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["shadow_demon_soul_catcher"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 and (snap.numAllies or 0) >= 2 then return 0.85, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 and Skill.HpPctOf(t) < 0.4 then return 0.8, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.6, t, "unit" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["shadow_demon_shadow_poison"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and n >= 1 and Skill.HpPctOf(t) < 0.4 then return 0.7, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.55, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["shadow_demon_demonic_purge"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.9, t, "unit" end
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 and (snap.numEnemies or 0) >= 2 then return 0.75, t, "unit" end
  return 0, nil, "none"
""",
  },
  "limitations": "v3.0 已订正: R 为 shadow_demon_demonic_purge(恶魔净化)。",
},
"shadow_fiend": {
  "abilities": {"Q": "nevermore_shadowraze1", "W": "nevermore_necromastery", "E": "nevermore_presence_of_the_dark_lord", "R": "nevermore_requiem"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_black_king_bar", "item_daedalus", "item_satanic", "item_butterfly", "item_manta", "item_monkey_king_bar", "item_abyssal_blade", "item_travel_boots", "item_moon_shard"],
    2: ["item_tango", "item_flask", "item_wraith_band", "item_bottle", "item_power_treads", "item_black_king_bar", "item_daedalus", "item_satanic", "item_butterfly", "item_manta", "item_aghanims_scepter", "item_scythe_of_vyse", "item_travel_boots", "item_moon_shard"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_black_king_bar", "item_daedalus", "item_satanic", "item_assault", "item_heart", "item_butterfly"],
    4: ["item_tango", "item_flask", "item_magic_wand", "item_wraith_band", "item_phase_boots", "item_black_king_bar", "item_daedalus", "item_force_staff", "item_satanic", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_phase_boots", "item_black_king_bar", "item_daedalus", "item_force_staff", "item_glimmer_cape"],
  },
  "consider": {
    "Q": """local ab = ab["nevermore_shadowraze1"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if snap.nearestEnemy == nil then return 0, nil, "none" end
  local d = snap.nearestEnemyDist
  if d == nil then return 0, nil, "none" end
  if d <= 250 then return 0.9, snap.nearestEnemy, "location" end
  if d <= 450 then return 0.75, snap.nearestEnemy, "location" end
  if d <= 700 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["nevermore_requiem"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 3 then return 1.0, nil, "none" end
  if n >= 2 and (snap.healthPct or 1) > 0.5 then return 0.9, nil, "none" end
  local low = Skill.CountLowHpEnemies(snap, 0.35)
  if low >= 1 and n >= 1 then return 0.85, nil, "none" end
  return 0, nil, "none"
""",
  },
  "limitations": "Reference Q is only nevermore_shadowraze1 (the near raze); the mid and far razes (shadowraze2 / shadowraze3) have no slot in the reference, so the single Q Consider is distance-segmented (<=250 near 0.9, <=450 mid 0.75, <=700 far 0.6) as the raze entry and the engine must map the other two raze distances separately if it wants true three-raze play.",
},
"shadow_shaman": {
  "abilities": {"Q": "shadow_shaman_ether_shock", "W": "shadow_shaman_voodoo", "E": "shadow_shaman_shackles", "R": "shadow_shaman_mass_serpent_ward"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_blink", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_null_talisman", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_lotus_orb", "item_octarine_core"],
    4: ["item_tango", "item_flask", "item_clarity", "item_null_talisman", "item_magic_wand", "item_arcane_boots", "item_blink", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_aghanims_scepter", "item_ward_observer"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_blink", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_aghanims_scepter", "item_lotus_orb"],
  },
  "consider": {
    "Q": """local ab = ab["shadow_shaman_ether_shock"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.8, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and Skill.HpPctOf(t) < 0.4 then return 0.8, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.6, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["shadow_shaman_voodoo"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 and (snap.numAllies or 0) >= 1 then return 0.85, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 and Skill.HpPctOf(t) < 0.4 then return 0.8, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["shadow_shaman_shackles"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 and (snap.numAllies or 0) >= 1 then return 0.9, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 and Skill.HpPctOf(t) < 0.35 then return 0.85, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 and (snap.healthPct or 1) > 0.6 then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["shadow_shaman_mass_serpent_ward"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.95, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and n >= 1 and Skill.HpPctOf(t) < 0.35 then return 0.85, snap.nearestEnemy, "location" end
  if n >= 1 and (snap.numAllies or 0) >= 2 then return 0.75, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
  },
},
}
