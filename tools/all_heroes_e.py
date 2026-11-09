# -*- coding: utf-8 -*-
"""E 组英雄深度数据 (v3.0.0, tools/generate.py 的事实源之一)。
覆盖 20 个英雄: silencer, skywrath_mage, slardar, slark, snapfire, sniper,
spectre, spirit_breaker, storm_spirit, sven, techies, templar_assassin,
terrorblade, tidehunter, timbersaw, tinker, tiny, treant_protector,
troll_warlord, tusk。
格式与 tools/focus_heroes.py 一致:
  abilities: {Q/W/E/R: 真实内部技能名, 以 tools/skill_names_reference.json 为准}
  consider: {Q/W/E/R: Lua 函数体字符串}, 签名 ConsiderX(bot, snap, ab),
    返回 desire(0-1), target, castType ("unit"/"location"/"none")。
    被动技能的 Consider 只写 return 0, nil, "none"。
    只用允许的 API: Skill.IsCastable / Skill.CountEnemiesInRange /
    Skill.CountLowHpEnemies / Skill.LowestHpEnemy / Skill.LowestHpAlly /
    Skill.LowestHpAllyPct / Skill.HpOf / Skill.HpPctOf, snap 字段,
    Team.ShouldHoldUlt / Team.GetComboWindow。
  talents: {10/15/20/25: 0=左, 1=右}。本项目自选, 非官方推荐。
  items: {1..5: [>=8 件]}, 主位置 >=12 件且有前期-中期-后期递进,
    各位置列表不完全相同。
技能名可疑点见各英雄 limitations。
"""
ALL_E = {
"silencer": {
  "abilities": {"Q": "silencer_curse_of_the_silent", "W": "silencer_glaives_of_wisdom", "E": "silencer_last_word", "R": "silencer_global_silence"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_rod_of_atos", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_scythe_of_vyse", "item_hurricane_pike", "item_moon_shard", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_rod_of_atos", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_aghanims_scepter", "item_scythe_of_vyse", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_power_treads", "item_rod_of_atos", "item_black_king_bar", "item_lotus_orb", "item_shivas_guard", "item_aghanims_scepter", "item_scythe_of_vyse"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_rod_of_atos", "item_aether_lens", "item_ghost_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_rod_of_atos", "item_aether_lens", "item_ghost_scepter", "item_euls_scepter_of_divinity", "item_lotus_orb"],
  },
  "consider": {
    "Q": """local ab = ab["silencer_curse_of_the_silent"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.25 then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 800)
  local t = Skill.LowestHpEnemy(snap)
  if n >= 2 and t ~= nil then return 0.85, t, "unit" end
  if n >= 1 and t ~= nil and Skill.HpPctOf(t) < 0.6 then return 0.75, t, "unit" end
  if n >= 1 and t ~= nil then return 0.55, t, "unit" end
  return 0, nil, "none"
""",
    "W": """return 0, nil, "none"
""",
    "E": """local ab = ab["silencer_last_word"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "unit" end
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["silencer_global_silence"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 1000)
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if n >= 3 then return 0.95, nil, "none" end
  if n >= 2 and (snap.healthPct or 1) < 0.6 then return 0.9, nil, "none" end
  if n >= 2 and ally ~= nil and pct < 0.4 then return 0.9, nil, "none" end
  if n >= 1 and ally ~= nil and pct < 0.25 then return 0.85, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"skywrath_mage": {
  "abilities": {"Q": "skywrath_mage_arcane_bolt", "W": "skywrath_mage_concussive_shot", "E": "skywrath_mage_ancient_seal", "R": "skywrath_mage_mystic_flare"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_rod_of_atos", "item_aether_lens", "item_black_king_bar", "item_orchid", "item_bloodthorn", "item_scythe_of_vyse", "item_aghanims_scepter", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_rod_of_atos", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_arcane_boots", "item_rod_of_atos", "item_aether_lens", "item_black_king_bar", "item_ghost_scepter", "item_shivas_guard", "item_aghanims_scepter"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_rod_of_atos", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_ghost_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_rod_of_atos", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_ghost_scepter", "item_euls_scepter_of_divinity", "item_lotus_orb"],
  },
  "consider": {
    "Q": """local ab = ab["skywrath_mage_arcane_bolt"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.2 then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then
    if Skill.HpPctOf(t) < 0.5 then return 0.85, t, "unit" end
    return 0.65, t, "unit"
  end
  return 0, nil, "none"
""",
    "W": """local ab = ab["skywrath_mage_concussive_shot"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.25 then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.45 then return 0.8, t, "unit" end
    return 0.6, t, "unit"
  end
  return 0, nil, "none"
""",
    "E": """local ab = ab["skywrath_mage_ancient_seal"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.3 then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.6 then return 0.85, t, "unit" end
    if (snap.numAllies or 0) >= 1 then return 0.7, t, "unit" end
    return 0.55, t, "unit"
  end
  return 0, nil, "none"
""",
    "R": """local ab = ab["skywrath_mage_mystic_flare"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.35 then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  local t = Skill.LowestHpEnemy(snap)
  if n >= 2 and t ~= nil then return 0.95, t, "location" end
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.9, t, "location" end
  if n >= 1 and t ~= nil and (snap.numAllies or 0) >= 2 then return 0.75, t, "location" end
  return 0, nil, "none"
""",
  },
},
"slardar": {
  "abilities": {"Q": "slardar_sprint", "W": "slardar_slithereen_crush", "E": "slardar_bash", "R": "slardar_amplify_damage"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_echo_sabre", "item_blink", "item_black_king_bar", "item_assault", "item_abyssal_blade", "item_satanic", "item_harpoon", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_power_treads", "item_echo_sabre", "item_blink", "item_black_king_bar", "item_assault", "item_abyssal_blade", "item_satanic", "item_aghanims_scepter", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_assault", "item_abyssal_blade", "item_aghanims_scepter", "item_shivas_guard", "item_heart", "item_travel_boots", "item_lotus_orb", "item_crimson_guard"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_blink", "item_black_king_bar", "item_assault", "item_force_staff", "item_lotus_orb", "item_solar_crest"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_blink", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_solar_crest"],
  },
  "consider": {
    "Q": """local ab = ab["slardar_sprint"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.85, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 300 and snap.nearestEnemyDist <= 900 and (snap.healthPct or 1) > 0.5 then return 0.7, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) > 0.6 then return 0.65, nil, "none" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["slardar_slithereen_crush"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 350)
  if n >= 2 then return 0.9, snap.nearestEnemy, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.5 then return 0.7, snap.nearestEnemy, "none" end
  if n >= 1 and (snap.numAllies or 0) >= 1 then return 0.65, snap.nearestEnemy, "none" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["slardar_amplify_damage"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if (snap.numEnemies or 0) >= 2 then return 0.85, t, "unit" end
    if Skill.HpPctOf(t) < 0.6 then return 0.8, t, "unit" end
    return 0.6, t, "unit"
  end
  return 0, nil, "none"
""",
  },
},
"slark": {
  "abilities": {"Q": "slark_dark_pact", "W": "slark_pounce", "E": "slark_essence_shift", "R": "slark_shadow_dance"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_abyssal_blade", "item_satanic", "item_butterfly", "item_aghanims_scepter", "item_harpoon", "item_diffusal_blade", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_abyssal_blade", "item_satanic", "item_butterfly", "item_aghanims_scepter", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_power_treads", "item_echo_sabre", "item_blink", "item_black_king_bar", "item_abyssal_blade", "item_assault", "item_satanic", "item_aghanims_scepter"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_abyssal_blade", "item_diffusal_blade", "item_force_staff", "item_glimmer_cape"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_force_staff", "item_glimmer_cape"],
  },
  "consider": {
    "Q": """local ab = ab["slark_dark_pact"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 and (snap.healthPct or 1) > 0.4 then return 0.85, nil, "none" end
  if (snap.healthPct or 1) < 0.6 and n >= 1 then return 0.8, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.6 then return 0.6, nil, "none" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["slark_pounce"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.3 and (snap.numEnemies or 0) >= 1 then return 0.85, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 250 and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.5 then return 0.85, t, "location" end
    return 0.6, t, "location"
  end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["slark_shadow_dance"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.95, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.35 and (snap.healthPct or 1) < 0.6 and (snap.numEnemies or 0) >= 1 then return 0.75, nil, "none" end
  if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 2 then return 0.8, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"snapfire": {
  "abilities": {"Q": "snapfire_scatterblast", "W": "snapfire_firesnap_cookie", "E": "snapfire_lil_shredder", "R": "snapfire_mortimer_kisses"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_maelstrom", "item_black_king_bar", "item_mjollnir", "item_aghanims_scepter", "item_scythe_of_vyse", "item_hurricane_pike", "item_moon_shard", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_maelstrom", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_travel_boots", "item_mjollnir"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_maelstrom", "item_black_king_bar", "item_shivas_guard", "item_aghanims_scepter", "item_lotus_orb", "item_pipe_of_insight"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_aghanims_scepter", "item_euls_scepter_of_divinity"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_aghanims_scepter", "item_euls_scepter_of_divinity", "item_lotus_orb", "item_ghost_scepter"],
  },
  "consider": {
    "Q": """local ab = ab["snapfire_scatterblast"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 450)
  if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
  if n >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 450 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["snapfire_firesnap_cookie"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.5 and (snap.numEnemies or 0) >= 1 then return 0.8, ally, "unit" end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) > 0.5 then return 0.65, bot, "unit" end
  if ally ~= nil and pct < 0.35 then return 0.75, ally, "unit" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["snapfire_lil_shredder"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.3 then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, nil, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["snapfire_mortimer_kisses"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 800)
  local t = Skill.LowestHpEnemy(snap)
  if n >= 2 and t ~= nil then return 0.95, t, "location" end
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.8, t, "location" end
  if n >= 1 and (snap.numAllies or 0) >= 2 then return 0.7, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
  },
},
"sniper": {
  "abilities": {"Q": "sniper_shrapnel", "W": "sniper_headshot", "E": "sniper_take_aim", "R": "sniper_assassinate"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_maelstrom", "item_hurricane_pike", "item_black_king_bar", "item_mjollnir", "item_daedalus", "item_butterfly", "item_satanic", "item_moon_shard", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_wraith_band", "item_bottle", "item_power_treads", "item_maelstrom", "item_hurricane_pike", "item_black_king_bar", "item_mjollnir", "item_daedalus", "item_aghanims_scepter", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_power_treads", "item_maelstrom", "item_hurricane_pike", "item_black_king_bar", "item_shivas_guard", "item_assault", "item_mjollnir"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_maelstrom", "item_hurricane_pike", "item_black_king_bar", "item_force_staff", "item_glimmer_cape"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_power_treads", "item_maelstrom", "item_hurricane_pike", "item_black_king_bar", "item_force_staff", "item_glimmer_cape"],
  },
  "consider": {
    "Q": """local ab = ab["sniper_shrapnel"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.55, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["sniper_assassinate"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local hp = Skill.HpOf(t)
  if hp > 0 and hp < 400 then return 1.0, t, "unit" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 1400 then return 0.9, t, "unit" end
  if pct > 0 and pct < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 1000 then return 0.75, t, "unit" end
  return 0, nil, "none"
""",
  },
},
"spectre": {
  "abilities": {"Q": "spectre_spectral_dagger", "W": "spectre_desolate", "E": "spectre_dispersion", "R": "spectre_haunt"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_radiance", "item_manta", "item_black_king_bar", "item_heart", "item_abyssal_blade", "item_aghanims_scepter", "item_butterfly", "item_satanic", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_radiance", "item_manta", "item_black_king_bar", "item_heart", "item_abyssal_blade", "item_aghanims_scepter", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_radiance", "item_manta", "item_black_king_bar", "item_heart", "item_assault", "item_aghanims_scepter"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_radiance", "item_manta", "item_black_king_bar", "item_force_staff", "item_lotus_orb"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_power_treads", "item_radiance", "item_manta", "item_black_king_bar", "item_force_staff", "item_glimmer_cape"],
  },
  "consider": {
    "Q": """local ab = ab["spectre_spectral_dagger"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then
    if Skill.HpPctOf(t) < 0.5 then return 0.85, t, "location" end
    return 0.7, t, "location"
  end
  return 0, nil, "none"
""",
    "W": """return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["spectre_haunt"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local low = Skill.CountLowHpEnemies(snap, 0.4)
  if low >= 2 then return 0.95, nil, "none" end
  if low >= 1 and (snap.numAllies or 0) >= 1 then return 0.85, nil, "none" end
  if low >= 1 and (snap.healthPct or 1) > 0.6 then return 0.7, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"spirit_breaker": {
  "abilities": {"Q": "spirit_breaker_charge_of_darkness", "W": "spirit_breaker_empowering_haste", "E": "spirit_breaker_greater_bash", "R": "spirit_breaker_nether_strike"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_assault", "item_abyssal_blade", "item_satanic", "item_aghanims_scepter", "item_harpoon", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_assault", "item_abyssal_blade", "item_satanic", "item_aghanims_scepter", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blade_mail", "item_black_king_bar", "item_assault", "item_abyssal_blade", "item_aghanims_scepter", "item_shivas_guard", "item_heart"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_shadow_blade", "item_black_king_bar", "item_assault", "item_aghanims_scepter", "item_force_staff", "item_lotus_orb", "item_solar_crest"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_shadow_blade", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_solar_crest"],
  },
  "consider": {
    "Q": """local ab = ab["spirit_breaker_charge_of_darkness"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 300 and snap.nearestEnemyDist <= 1500 then
    if Skill.HpPctOf(t) < 0.6 then return 0.85, t, "unit" end
    if (snap.numEnemies or 0) == 1 then return 0.65, t, "unit" end
    return 0.55, t, "unit"
  end
  return 0, nil, "none"
""",
    "W": """return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["spirit_breaker_nether_strike"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    if Skill.HpPctOf(t) < 0.5 then return 0.95, t, "unit" end
    if (snap.numEnemies or 0) >= 2 then return 0.85, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none"
""",
  },
  "limitations": "W 奔腾之速按被动光环处理, 现版本若为可开关技能则此处会漏放。",
},
"storm_spirit": {
  "abilities": {"Q": "storm_spirit_static_remnant", "W": "storm_spirit_electric_vortex", "E": "storm_spirit_overload", "R": "storm_spirit_ball_lightning"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_bloodstone", "item_black_king_bar", "item_orchid", "item_bloodthorn", "item_scythe_of_vyse", "item_kaya_and_sange", "item_travel_boots", "item_moon_shard"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_bloodstone", "item_black_king_bar", "item_orchid", "item_bloodthorn", "item_kaya_and_sange", "item_scythe_of_vyse", "item_travel_boots", "item_aghanims_scepter"],
    3: ["item_tango", "item_flask", "item_bracer", "item_power_treads", "item_bloodstone", "item_black_king_bar", "item_shivas_guard", "item_kaya_and_sange", "item_aghanims_scepter", "item_lotus_orb"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_bloodstone", "item_black_king_bar", "item_orchid", "item_force_staff", "item_glimmer_cape"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_bloodstone", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_aether_lens"],
  },
  "consider": {
    "Q": """local ab = ab["storm_spirit_static_remnant"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.3 then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 300 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["storm_spirit_electric_vortex"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.35 then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    if Skill.HpPctOf(t) < 0.5 then return 0.85, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["storm_spirit_ball_lightning"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.45 then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.3 and (snap.numEnemies or 0) >= 1 and (snap.manaPct or 1) > 0.5 then return 0.9, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 400 and snap.nearestEnemyDist <= 1200 then return 0.9, t, "location" end
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 400 and snap.nearestEnemyDist <= 900 and (snap.manaPct or 1) > 0.6 then return 0.75, t, "location" end
  return 0, nil, "none"
""",
  },
},
"sven": {
  "abilities": {"Q": "sven_storm_bolt", "W": "sven_great_cleave", "E": "sven_warcry", "R": "sven_gods_strength"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_daedalus", "item_abyssal_blade", "item_satanic", "item_aghanims_scepter", "item_harpoon", "item_assault", "item_travel_boots", "item_moon_shard"],
    2: ["item_tango", "item_flask", "item_bottle", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_daedalus", "item_abyssal_blade", "item_satanic", "item_aghanims_scepter", "item_travel_boots", "item_harpoon"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_echo_sabre", "item_blink", "item_black_king_bar", "item_daedalus", "item_assault", "item_abyssal_blade", "item_aghanims_scepter", "item_heart"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_echo_sabre", "item_blink", "item_black_king_bar", "item_assault", "item_force_staff", "item_lotus_orb"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_power_treads", "item_echo_sabre", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_solar_crest"],
  },
  "consider": {
    "Q": """local ab = ab["sven_storm_bolt"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    if (snap.numEnemies or 0) >= 2 then return 0.85, t, "unit" end
    if Skill.HpPctOf(t) < 0.5 then return 0.8, t, "unit" end
    return 0.65, t, "unit"
  end
  return 0, nil, "none"
""",
    "W": """return 0, nil, "none"
""",
    "E": """local ab = ab["sven_warcry"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.8, nil, "none" end
  if n >= 1 and (snap.numAllies or 0) >= 1 then return 0.7, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) < 0.7 then return 0.65, nil, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["sven_gods_strength"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 and (snap.healthPct or 1) > 0.5 then return 0.95, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.5 then return 0.8, nil, "none" end
  if n >= 1 and (snap.numAllies or 0) >= 2 then return 0.75, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"techies": {
  "abilities": {"Q": "techies_land_mines", "W": "techies_stasis_trap", "E": "techies_blast_off", "R": "techies_focused_detonate"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_dagon_5", "item_travel_boots", "item_moon_shard"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_dagon_5", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_arcane_boots", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_pipe_of_insight", "item_lotus_orb"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_aghanims_scepter", "item_euls_scepter_of_divinity", "item_ghost_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_aghanims_scepter", "item_euls_scepter_of_divinity", "item_ghost_scepter", "item_lotus_orb"],
  },
  "consider": {
    "Q": """local ab = ab["techies_land_mines"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.4 then return 0, nil, "none" end
  if (snap.numEnemies or 0) == 0 and (snap.healthPct or 1) > 0.6 then return 0.6, snap.location, "location" end
  if (snap.numEnemies or 0) >= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.55, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["techies_stasis_trap"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.7, snap.location, "location" end
  if (snap.numEnemies or 0) == 0 and (snap.manaPct or 1) > 0.35 then return 0.5, snap.location, "location" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["techies_blast_off"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 and (snap.healthPct or 1) > 0.5 then return 0.8, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 then return 0.7, t, "location" end
  if n >= 1 and (snap.healthPct or 1) < 0.25 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["techies_focused_detonate"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  local t = Skill.LowestHpEnemy(snap)
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  if t ~= nil and Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.85, t, "location" end
  if n >= 1 and (snap.numAllies or 0) >= 2 then return 0.7, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
  },
  "limitations": "无精细布雷微操: 地雷/陷阱只在安全时原地布设或脚下防守, 不做路口预判布雷、雷区叠加与远程引爆选点; v3.0 已订正: E 为 techies_blast_off(自爆炸弹)。",
},
"templar_assassin": {
  "abilities": {"Q": "templar_assassin_refraction", "W": "templar_assassin_meld", "E": "templar_assassin_psi_blades", "R": "templar_assassin_trap"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_desolator", "item_black_king_bar", "item_daedalus", "item_blink", "item_aghanims_scepter", "item_butterfly", "item_satanic", "item_moon_shard", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_wraith_band", "item_bottle", "item_power_treads", "item_desolator", "item_blink", "item_black_king_bar", "item_daedalus", "item_aghanims_scepter", "item_butterfly", "item_satanic", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_desolator", "item_blink", "item_black_king_bar", "item_daedalus", "item_assault", "item_aghanims_scepter", "item_heart"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_desolator", "item_blink", "item_black_king_bar", "item_force_staff", "item_aghanims_scepter", "item_solar_crest"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_power_treads", "item_desolator", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_solar_crest"],
  },
  "consider": {
    "Q": """local ab = ab["templar_assassin_refraction"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.3 then return 0.75, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) <= 0.3 then return 0.65, nil, "none" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["templar_assassin_meld"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.7, nil, "none" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.65, nil, "none" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["templar_assassin_trap"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.6, snap.nearestEnemy, "location" end
  if (snap.numEnemies or 0) == 0 and (snap.manaPct or 1) > 0.5 then return 0.5, snap.location, "location" end
  return 0, nil, "none"
""",
  },
},
"terrorblade": {
  "abilities": {"Q": "terrorblade_reflection", "W": "terrorblade_conjure_image", "E": "terrorblade_metamorphosis", "R": "terrorblade_sunder"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_manta", "item_black_king_bar", "item_butterfly", "item_satanic", "item_skadi", "item_abyssal_blade", "item_aghanims_scepter", "item_travel_boots", "item_moon_shard"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_manta", "item_black_king_bar", "item_butterfly", "item_satanic", "item_skadi", "item_aghanims_scepter", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_manta", "item_black_king_bar", "item_butterfly", "item_assault", "item_heart", "item_satanic", "item_aghanims_scepter"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_manta", "item_black_king_bar", "item_butterfly", "item_force_staff", "item_lotus_orb"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_power_treads", "item_manta", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_solar_crest"],
  },
  "consider": {
    "Q": """local ab = ab["terrorblade_reflection"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  local t = Skill.LowestHpEnemy(snap)
  if n >= 2 and t ~= nil then return 0.85, t, "unit" end
  if n >= 1 and t ~= nil then return 0.7, t, "unit" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["terrorblade_conjure_image"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.3 then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.5 then return 0.65, nil, "none" end
  if (snap.numEnemies or 0) == 0 and (snap.healthPct or 1) > 0.7 then return 0.55, nil, "none" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["terrorblade_metamorphosis"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 and (snap.healthPct or 1) > 0.4 then return 0.95, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.4 then return 0.85, nil, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["terrorblade_sunder"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.3 and Skill.HpPctOf(t) > 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 1.0, t, "unit" end
  if Skill.HpPctOf(t) < 0.25 and (snap.healthPct or 1) > 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.9, t, "unit" end
  if (snap.healthPct or 1) < 0.4 and Skill.HpPctOf(t) > 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.85, t, "unit" end
  return 0, nil, "none"
""",
  },
},
"tidehunter": {
  "abilities": {"Q": "tidehunter_gush", "W": "tidehunter_kraken_shell", "E": "tidehunter_anchor_smash", "R": "tidehunter_ravage"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_blink", "item_black_king_bar", "item_assault", "item_abyssal_blade", "item_heart", "item_aghanims_scepter", "item_refresher_orb", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_power_treads", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_aghanims_scepter", "item_refresher_orb", "item_travel_boots", "item_shivas_guard"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_pipe_of_insight", "item_shivas_guard", "item_aghanims_scepter", "item_refresher_orb", "item_heart", "item_assault", "item_lotus_orb", "item_crimson_guard"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_blink", "item_black_king_bar", "item_pipe_of_insight", "item_force_staff", "item_aghanims_scepter", "item_lotus_orb"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_blink", "item_black_king_bar", "item_pipe_of_insight", "item_force_staff", "item_glimmer_cape"],
  },
  "consider": {
    "Q": """local ab = ab["tidehunter_gush"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.5 then return 0.8, t, "unit" end
    return 0.65, t, "unit"
  end
  return 0, nil, "none"
""",
    "W": """return 0, nil, "none"
""",
    "E": """local ab = ab["tidehunter_anchor_smash"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.85, snap.nearestEnemy, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.5 then return 0.6, snap.nearestEnemy, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["tidehunter_ravage"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 3 then return 1.0, snap.nearestEnemy, "none" end
  if n >= 2 and (snap.numAllies or 0) >= 1 then return 0.9, snap.nearestEnemy, "none" end
  if n >= 2 then return 0.8, snap.nearestEnemy, "none" end
  if n >= 1 and (snap.numAllies or 0) >= 2 then return 0.7, snap.nearestEnemy, "none" end
  return 0, nil, "none"
""",
  },
},
"timbersaw": {
  "abilities": {"Q": "shredder_whirling_death", "W": "shredder_timber_chain", "E": "shredder_reactive_armor", "R": "shredder_chakram"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_bloodstone", "item_black_king_bar", "item_shivas_guard", "item_octarine_core", "item_aghanims_scepter", "item_kaya_and_sange", "item_travel_boots", "item_moon_shard"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_bloodstone", "item_black_king_bar", "item_shivas_guard", "item_octarine_core", "item_aghanims_scepter", "item_kaya_and_sange", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_bloodstone", "item_black_king_bar", "item_shivas_guard", "item_octarine_core", "item_aghanims_scepter", "item_kaya_and_sange", "item_lotus_orb", "item_heart", "item_travel_boots"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_bloodstone", "item_black_king_bar", "item_shivas_guard", "item_force_staff", "item_aghanims_scepter", "item_lotus_orb"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_bloodstone", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_pipe_of_insight"],
  },
  "consider": {
    "Q": """local ab = ab["shredder_whirling_death"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.85, snap.nearestEnemy, "none" end
  if n >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 350 then return 0.65, snap.nearestEnemy, "none" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["shredder_timber_chain"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.85, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 400 and snap.nearestEnemyDist <= 900 then return 0.75, t, "location" end
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 400 and snap.nearestEnemyDist <= 700 then return 0.6, t, "location" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["shredder_chakram"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.25 then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  local t = Skill.LowestHpEnemy(snap)
  if n >= 2 and t ~= nil then return 0.9, t, "location" end
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.8, t, "location" end
  if n >= 1 and t ~= nil then return 0.65, t, "location" end
  return 0, nil, "none"
""",
  },
},
"tinker": {
  "abilities": {"Q": "tinker_laser", "W": "tinker_heat_seeking_missile", "E": "tinker_defense_matrix", "R": "tinker_rearm"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_dagon_5", "item_kaya_and_sange", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_dagon_5", "item_kaya_and_sange", "item_travel_boots", "item_aether_lens"],
    3: ["item_tango", "item_flask", "item_bracer", "item_arcane_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_octarine_core", "item_lotus_orb", "item_pipe_of_insight"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_force_staff", "item_glimmer_cape", "item_aether_lens"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_force_staff", "item_glimmer_cape", "item_aether_lens"],
  },
  "consider": {
    "Q": """local ab = ab["tinker_laser"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.2 then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.6 then return 0.85, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none"
""",
    "W": """local ab = ab["tinker_heat_seeking_missile"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.25 then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 800)
  local t = Skill.LowestHpEnemy(snap)
  if n >= 2 and t ~= nil then return 0.8, t, "unit" end
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.75, t, "unit" end
  if n >= 1 and t ~= nil then return 0.6, t, "unit" end
  return 0, nil, "none"
""",
    "E": """local ab = ab["tinker_defense_matrix"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.5 then return 0.85, ally, "unit" end
  if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 1 then return 0.8, bot, "unit" end
  if ally ~= nil and pct < 0.7 and (snap.numEnemies or 0) >= 2 then return 0.6, ally, "unit" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["tinker_rearm"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.55 then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) > 0.4 then return 0.85, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.4 then return 0.8, nil, "none" end
  return 0, nil, "none"
""",
  },
  "limitations": "v3.0 已订正: E 为 tinker_defense_matrix(防御矩阵, 给队友护盾)。Rearm 无冷却 API 可读: 只能按蓝量 >=55% + 敌方人数/残血目标的代理条件放, 不能按激光/导弹的真实冷却放; 刷新后激光/导弹的二次施放由它们各自的 Consider 在可施放时自然触发。",
},
"tiny": {
  "abilities": {"Q": "tiny_avalanche", "W": "tiny_toss", "E": "tiny_craggy_exterior", "R": "tiny_grow"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_echo_sabre", "item_blink", "item_black_king_bar", "item_assault", "item_daedalus", "item_satanic", "item_aghanims_scepter", "item_harpoon", "item_travel_boots", "item_moon_shard"],
    2: ["item_tango", "item_flask", "item_bottle", "item_power_treads", "item_echo_sabre", "item_blink", "item_black_king_bar", "item_daedalus", "item_aghanims_scepter", "item_assault", "item_satanic", "item_travel_boots", "item_harpoon"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_aghanims_scepter", "item_shivas_guard", "item_lotus_orb", "item_crimson_guard"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_force_staff", "item_lotus_orb", "item_solar_crest"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_blink", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_aghanims_scepter"],
  },
  "consider": {
    "Q": """local ab = ab["tiny_avalanche"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.85, t, "location" end
  if n >= 1 then return 0.7, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["tiny_toss"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  local t = Skill.LowestHpEnemy(snap)
  if n >= 2 and t ~= nil then return 0.85, t, "unit" end
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.8, t, "unit" end
  if n >= 1 and t ~= nil then return 0.65, t, "unit" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["tiny_grow"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 and (snap.healthPct or 1) > 0.4 then return 0.85, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.4 then return 0.7, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"treant_protector": {
  "abilities": {"Q": "treant_natures_grasp", "W": "treant_leech_seed", "E": "treant_living_armor", "R": "treant_overgrowth"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_bracer", "item_power_treads", "item_meteor_hammer", "item_black_king_bar", "item_assault", "item_heart", "item_aghanims_scepter", "item_shivas_guard", "item_lotus_orb", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_power_treads", "item_meteor_hammer", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_shivas_guard", "item_lotus_orb", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_meteor_hammer", "item_black_king_bar", "item_pipe_of_insight", "item_lotus_orb", "item_shivas_guard", "item_aghanims_scepter", "item_heart", "item_crimson_guard"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_meteor_hammer", "item_force_staff", "item_glimmer_cape", "item_pipe_of_insight", "item_lotus_orb", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_meteor_hammer", "item_force_staff", "item_glimmer_cape", "item_pipe_of_insight", "item_lotus_orb", "item_aghanims_scepter", "item_solar_crest"],
  },
  "consider": {
    "Q": """local ab = ab["treant_natures_grasp"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  if n >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.55, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["treant_leech_seed"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    if (snap.numEnemies or 0) >= 2 then return 0.8, t, "unit" end
    if Skill.HpPctOf(t) < 0.6 then return 0.75, t, "unit" end
    return 0.6, t, "unit"
  end
  return 0, nil, "none"
""",
    "E": """local ab = ab["treant_living_armor"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.5 then return 0.9, ally, "unit" end
  if (snap.healthPct or 1) < 0.5 then return 0.85, bot, "unit" end
  if ally ~= nil and pct < 0.7 and (snap.numEnemies or 0) >= 1 then return 0.6, ally, "unit" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["treant_overgrowth"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if n >= 2 then return 0.95, snap.nearestEnemy, "none" end
  if n >= 1 and ally ~= nil and pct < 0.4 then return 0.85, snap.nearestEnemy, "none" end
  if n >= 1 and (snap.numAllies or 0) >= 2 then return 0.75, snap.nearestEnemy, "none" end
  return 0, nil, "none"
""",
  },
},
"troll_warlord": {
  "abilities": {"Q": "troll_warlord_berserkers_rage", "W": "troll_warlord_whirling_axes_ranged", "E": "troll_warlord_fervor", "R": "troll_warlord_battle_trance"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_battle_fury", "item_black_king_bar", "item_satanic", "item_butterfly", "item_abyssal_blade", "item_aghanims_scepter", "item_moon_shard", "item_travel_boots", "item_monkey_king_bar"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_battle_fury", "item_black_king_bar", "item_satanic", "item_butterfly", "item_abyssal_blade", "item_aghanims_scepter", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_battle_fury", "item_black_king_bar", "item_assault", "item_satanic", "item_abyssal_blade", "item_aghanims_scepter", "item_heart"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_battle_fury", "item_black_king_bar", "item_satanic", "item_force_staff", "item_abyssal_blade", "item_solar_crest"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_power_treads", "item_battle_fury", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_solar_crest"],
  },
  "consider": {
    "Q": """local ab = ab["troll_warlord_berserkers_rage"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 350 then return 0.65, nil, "none" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["troll_warlord_whirling_axes_ranged"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["troll_warlord_battle_trance"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 and (snap.healthPct or 1) > 0.4 then return 0.95, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.4 then return 0.85, nil, "none" end
  if n >= 1 and (snap.numAllies or 0) >= 2 then return 0.75, nil, "none" end
  return 0, nil, "none"
""",
  },
},
"tusk": {
  "abilities": {"Q": "tusk_ice_shards", "W": "tusk_snowball", "E": "tusk_frozen_sigil", "R": "tusk_walrus_punch"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_echo_sabre", "item_blink", "item_black_king_bar", "item_assault", "item_abyssal_blade", "item_satanic", "item_aghanims_scepter", "item_harpoon", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_power_treads", "item_echo_sabre", "item_blink", "item_black_king_bar", "item_assault", "item_aghanims_scepter", "item_abyssal_blade", "item_satanic", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_assault", "item_abyssal_blade", "item_aghanims_scepter", "item_shivas_guard", "item_heart", "item_lotus_orb"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_force_staff", "item_solar_crest", "item_lotus_orb", "item_aeon_disk"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_blink", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_solar_crest"],
  },
  "consider": {
    "Q": """local ab = ab["tusk_ice_shards"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "W": """local ab = ab["tusk_snowball"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if (snap.numAllies or 0) >= 1 then return 0.8, t, "unit" end
    if Skill.HpPctOf(t) < 0.5 then return 0.7, t, "unit" end
    return 0.55, t, "unit"
  end
  return 0, nil, "none"
""",
    "E": """local ab = ab["tusk_frozen_sigil"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.numAllies or 0) >= 1 then return 0.6, nil, "none" end
  if (snap.numEnemies or 0) >= 2 then return 0.55, nil, "none" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["tusk_walrus_punch"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 then
    if Skill.HpPctOf(t) < 0.4 then return 0.95, t, "unit" end
    if (snap.numEnemies or 0) >= 1 and (snap.manaPct or 1) > 0.2 then return 0.7, t, "unit" end
  end
  return 0, nil, "none"
""",
  },
},
}
