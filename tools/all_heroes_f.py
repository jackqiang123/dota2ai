# -*- coding: utf-8 -*-
"""F 组英雄深度数据 (v3.0.0, tools/generate.py 的事实源之一)。
覆盖 17 个英雄: underlord, undying, ursa, vengeful_spirit, venomancer,
viper, visage, void_spirit, warlock, weaver, windranger, winter_wyvern,
witch_doctor, wraith_king, invoker, kez, largo。
技能名来源: tools/skill_names_reference.json (d2vpk / 手工按 Valve 命名规则)。
位置/主属性来源: tools/heroes_data.py。格式对照 tools/focus_heroes.py。
consider: Lua 函数体字符串, 签名 ConsiderX(bot, snap, ab), 返回
desire(0-1), target, castType ("unit"/"location"/"none")。
被动技能的 Consider 只返回 return 0, nil, "none"。
talents: {10/15/20/25: 0=左, 1=右}, 本项目自选, 非官方推荐。
items: {pos: [...]}, 每位置 >=8 件, 主位置 >=12 件且有前期-中期-后期递进。
"""
ALL_F = {
"underlord": {
  "abilities": {"Q": "abyssal_underlord_firestorm", "W": "abyssal_underlord_pit_of_malice", "E": "abyssal_underlord_atrophy_aura", "R": "abyssal_underlord_dark_rift"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_soul_ring", "item_power_treads", "item_vanguard", "item_radiance", "item_black_king_bar", "item_assault", "item_heart", "item_butterfly", "item_satanic", "item_travel_boots", "item_abyssal_blade"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_soul_ring", "item_arcane_boots", "item_kaya_and_sange", "item_shivas_guard", "item_black_king_bar", "item_octarine_core", "item_aghanims_scepter", "item_scythe_of_vyse"], 3: ["item_tango", "item_flask", "item_soul_ring", "item_phase_boots", "item_vanguard", "item_crimson_guard", "item_pipe_of_insight", "item_blink", "item_black_king_bar", "item_shivas_guard", "item_aghanims_scepter", "item_octarine_core", "item_heart", "item_lotus_orb", "item_travel_boots"], 4: ["item_tango", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_pipe_of_insight", "item_blink", "item_lotus_orb"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer", "item_pipe_of_insight"]},
  "consider": {
    "Q": """local ab = ab["abyssal_underlord_firestorm"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 and (snap.manaPct or 1) > 0.5 then return 0.55, snap.nearestEnemy, "location" end
  if #snap.nearbyEnemyCreeps > 0 and (snap.numEnemies or 0) == 0 then return 0.5, snap.nearbyEnemyCreeps[1], "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["abyssal_underlord_pit_of_malice"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.75, t, "location" end
  if (snap.numEnemies or 0) >= 1 and (snap.numAllies or 0) >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.8, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "E": 'return 0, nil, "none"',
    "R": """local ab = ab["abyssal_underlord_dark_rift"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally = Skill.LowestHpAlly(snap)
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 and ally ~= nil then return 0.85, ally, "unit" end
  if (snap.numEnemies or 0) >= 3 and (snap.numAllies or 0) >= 2 and ally ~= nil then return 0.7, ally, "unit" end
  return 0, nil, "none\"""",
  },
  "limitations": "技能名前缀 abyssal_underlord_ 来自手工整理的命名规则（英雄内部名为 abyssal_underlord），未在新版 d2vpk 中核对。",
},
"undying": {
  "abilities": {"Q": "undying_decay", "W": "undying_soul_rip", "E": "undying_tombstone", "R": "undying_flesh_golem"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_vanguard", "item_radiance", "item_black_king_bar", "item_assault", "item_heart", "item_satanic", "item_abyssal_blade"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_arcane_boots", "item_kaya_and_sange", "item_meteor_hammer", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_shivas_guard", "item_scythe_of_vyse"], 3: ["item_tango", "item_flask", "item_soul_ring", "item_phase_boots", "item_vanguard", "item_crimson_guard", "item_pipe_of_insight", "item_blink", "item_black_king_bar", "item_shivas_guard", "item_heart", "item_aghanims_scepter"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_meteor_hammer", "item_force_staff", "item_glimmer_cape", "item_blink", "item_lotus_orb", "item_pipe_of_insight"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_meteor_hammer", "item_glimmer_cape", "item_force_staff", "item_pipe_of_insight", "item_aghanims_scepter", "item_octarine_core", "item_lotus_orb", "item_ghost_scepter"]},
  "consider": {
    "Q": """local ab = ab["undying_decay"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 350)
  if n >= 2 and (snap.healthPct or 1) > 0.3 then return 0.85, snap.nearestEnemy, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.5 then return 0.6, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["undying_soul_rip"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.55 and ((snap.numAllies or 0) + #snap.nearbyAllyCreeps + #snap.nearbyEnemyCreeps) >= 2 then return 0.8, ally, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["undying_tombstone"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.numAllies or 0) >= 1 then return 0.85, snap.nearestEnemy, "location" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.75, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["undying_flesh_golem"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) > 0.4 then return 0.9, snap.nearestEnemy, "none" end
  if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 1 then return 0.7, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
  },
},
"ursa": {
  "abilities": {"Q": "ursa_earthshock", "W": "ursa_overpower", "E": "ursa_fury_swipes", "R": "ursa_enrage"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_phase_boots", "item_battle_fury", "item_blink", "item_black_king_bar", "item_abyssal_blade", "item_satanic", "item_butterfly", "item_monkey_king_bar", "item_aghanims_scepter", "item_travel_boots", "item_moon_shard", "item_harpoon"], 2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_echo_sabre", "item_blink", "item_black_king_bar", "item_abyssal_blade", "item_satanic", "item_butterfly", "item_aghanims_shard"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_blink", "item_black_king_bar", "item_blade_mail", "item_assault", "item_heart", "item_abyssal_blade", "item_crimson_guard"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_blink", "item_force_staff", "item_black_king_bar", "item_solar_crest"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_meteor_hammer"]},
  "consider": {
    "Q": """local ab = ab["ursa_earthshock"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 then return 0.8, t, "location" end
  local n = Skill.CountEnemiesInRange(snap, 300)
  if n >= 2 then return 0.7, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["ursa_overpower"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 300 and (snap.healthPct or 1) > 0.4 then return 0.85, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
    "E": 'return 0, nil, "none"',
    "R": """local ab = ab["ursa_enrage"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.95, snap.nearestEnemy, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and (snap.healthPct or 1) > 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 then return 0.7, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
  },
},
"vengeful_spirit": {
  "abilities": {"Q": "vengefulspirit_magic_missile", "W": "vengefulspirit_wave_of_terror", "E": "vengefulspirit_vengeance_aura", "R": "vengefulspirit_nether_swap"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_manta", "item_butterfly", "item_monkey_king_bar", "item_satanic"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_dragon_lance", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_scythe_of_vyse", "item_blink", "item_travel_boots"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_force_staff", "item_black_king_bar", "item_aghanims_scepter", "item_assault", "item_heart", "item_lotus_orb", "item_shivas_guard"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_solar_crest", "item_lotus_orb", "item_blink"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_aghanims_scepter", "item_lotus_orb", "item_blink", "item_solar_crest", "item_ghost_scepter"]},
  "consider": {
    "Q": """local ab = ab["vengefulspirit_magic_missile"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.85, snap.nearestEnemy, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.75, t, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["vengefulspirit_wave_of_terror"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 800)
  if n >= 2 then return 0.7, snap.nearestEnemy, "location" end
  if n >= 1 and (snap.numAllies or 0) >= 1 then return 0.55, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "E": 'return 0, nil, "none"',
    "R": """local ab = ab["vengefulspirit_nether_swap"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.3 and (snap.numEnemies or 0) >= 1 then return 1.0, ally, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and (snap.numAllies or 0) >= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.8, t, "unit" end
  return 0, nil, "none\"""",
  },
  "limitations": "技能名前缀 vengefulspirit_（无下划线分隔）来自手工整理的命名规则，英雄内部名即 vengefulspirit，未在新版 d2vpk 中核对。",
},
"venomancer": {
  "abilities": {"Q": "venomancer_venomous_gale", "W": "venomancer_poison_sting", "E": "venomancer_plague_ward", "R": "venomancer_poison_nova"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_manta", "item_butterfly", "item_monkey_king_bar", "item_daedalus"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_arcane_boots", "item_veil_of_discord", "item_kaya_and_sange", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_shivas_guard", "item_scythe_of_vyse"], 3: ["item_tango", "item_flask", "item_soul_ring", "item_phase_boots", "item_veil_of_discord", "item_force_staff", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_octarine_core", "item_pipe_of_insight", "item_lotus_orb", "item_travel_boots", "item_gleipnir"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_veil_of_discord", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_rod_of_atos", "item_gleipnir"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer", "item_pipe_of_insight"]},
  "consider": {
    "Q": """local ab = ab["venomancer_venomous_gale"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.55, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "W": 'return 0, nil, "none"',
    "E": """local ab = ab["venomancer_plague_ward"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.numAllies or 0) >= 1 then return 0.55, snap.nearestEnemy, "location" end
  if (snap.numEnemies or 0) == 0 and #snap.nearbyEnemyCreeps > 0 then return 0.6, snap.nearbyEnemyCreeps[1], "location" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["venomancer_poison_nova"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 900)
  local low = Skill.CountLowHpEnemies(snap, 0.5)
  if n >= 3 then return 1.0, snap.nearestEnemy, "none" end
  if n >= 2 and low >= 1 then return 0.9, snap.nearestEnemy, "none" end
  if n >= 2 then return 0.7, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
  },
},
"viper": {
  "abilities": {"Q": "viper_poison_attack", "W": "viper_nethertoxin", "E": "viper_corrosive_skin", "R": "viper_viper_strike"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_hurricane_pike", "item_manta", "item_black_king_bar", "item_butterfly", "item_monkey_king_bar", "item_satanic"], 2: ["item_tango", "item_flask", "item_wraith_band", "item_bottle", "item_power_treads", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_manta", "item_butterfly", "item_aghanims_scepter", "item_monkey_king_bar", "item_scythe_of_vyse", "item_travel_boots", "item_moon_shard"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_crimson_guard", "item_shivas_guard", "item_black_king_bar", "item_aghanims_scepter", "item_heart", "item_assault", "item_lotus_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_rod_of_atos", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_gleipnir", "item_meteor_hammer"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer", "item_pipe_of_insight"]},
  "consider": {
    "Q": """local ab = ab["viper_poison_attack"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and Skill.HpPctOf(t) < 0.6 then return 0.7, t, "unit" end
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.55, t, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["viper_nethertoxin"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.6, t, "location" end
  return 0, nil, "none\"""",
    "E": 'return 0, nil, "none"',
    "R": """local ab = ab["viper_viper_strike"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.9, t, "unit" end
  if pct > 0 and pct < 0.7 and (snap.numAllies or 0) >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
  },
},
"visage": {
  "abilities": {"Q": "visage_grave_chill", "W": "visage_soul_assumption", "E": "visage_gravekeepers_cloak", "R": "visage_summon_familiars"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_manta", "item_black_king_bar", "item_butterfly", "item_monkey_king_bar", "item_satanic", "item_hurricane_pike"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_arcane_boots", "item_kaya_and_sange", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_shivas_guard", "item_scythe_of_vyse", "item_travel_boots"], 3: ["item_tango", "item_flask", "item_soul_ring", "item_phase_boots", "item_pipe_of_insight", "item_shivas_guard", "item_aghanims_scepter", "item_blink", "item_black_king_bar", "item_octarine_core", "item_lotus_orb", "item_heart", "item_travel_boots", "item_solar_crest", "item_aeon_disk"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_pipe_of_insight", "item_blink", "item_lotus_orb"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer", "item_pipe_of_insight"]},
  "consider": {
    "Q": """local ab = ab["visage_grave_chill"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["visage_soul_assumption"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.6 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.8, t, "unit" end
  if pct > 0 and pct < 0.8 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.55, t, "unit" end
  return 0, nil, "none\"""",
    "E": 'return 0, nil, "none"',
    "R": """local ab = ab["visage_summon_familiars"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.numAllies or 0) >= 1 then return 0.85, snap.nearestEnemy, "none" end
  if (snap.numEnemies or 0) == 0 and #snap.nearbyEnemyCreeps > 0 then return 0.55, snap.nearestEnemy, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.6 then return 0.6, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "魔像（Familiars）无独立微操，只有通用召唤逻辑：R 只决定何时召唤，不控制魔像走位、集火或石化时机。",
},
"void_spirit": {
  "abilities": {"Q": "void_spirit_aether_remnant", "W": "void_spirit_dissimilate", "E": "void_spirit_resonant_pulse", "R": "void_spirit_astral_step"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_maelstrom", "item_mjollnir", "item_black_king_bar", "item_manta", "item_butterfly", "item_monkey_king_bar", "item_satanic"], 2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_kaya_and_sange", "item_travel_boots", "item_blink", "item_aeon_disk", "item_bloodstone"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_euls_scepter_of_divinity", "item_blink", "item_black_king_bar", "item_shivas_guard", "item_aghanims_scepter", "item_heart", "item_octarine_core", "item_lotus_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_euls_scepter_of_divinity", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_blink", "item_meteor_hammer"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer", "item_euls_scepter_of_divinity"]},
  "consider": {
    "Q": """local ab = ab["void_spirit_aether_remnant"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.6 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["void_spirit_dissimilate"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.45 and (snap.numEnemies or 0) >= 1 then return 0.85, snap.nearestEnemy, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 and (snap.healthPct or 1) > 0.5 then return 0.7, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["void_spirit_resonant_pulse"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.8, snap.nearestEnemy, "none" end
  if n >= 1 and (snap.healthPct or 1) < 0.6 then return 0.7, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["void_spirit_astral_step"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 1000 then return 0.9, t, "location" end
  if (snap.healthPct or 1) < 0.3 and (snap.numEnemies or 0) >= 1 then return 0.8, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
  },
  "limitations": "技能名前缀 void_spirit_ 来自手工整理的命名规则，未在新版 d2vpk 中核对。",
},
"warlock": {
  "abilities": {"Q": "warlock_fatal_bonds", "W": "warlock_shadow_word", "E": "warlock_upheaval", "R": "warlock_rain_of_chaos"},
  "talents": {10: 1, 15: 0, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_hand_of_midas", "item_radiance", "item_black_king_bar", "item_assault", "item_heart", "item_satanic", "item_travel_boots"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_arcane_boots", "item_aether_lens", "item_aghanims_scepter", "item_octarine_core", "item_black_king_bar", "item_refresher_orb", "item_scythe_of_vyse", "item_travel_boots"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_pipe_of_insight", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_heart", "item_refresher_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_blink", "item_aghanims_scepter", "item_lotus_orb"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_aghanims_scepter", "item_refresher_orb", "item_black_king_bar", "item_lotus_orb", "item_ghost_scepter"]},
  "consider": {
    "Q": """local ab = ab["warlock_fatal_bonds"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 3 then return 0.9, snap.nearestEnemy, "unit" end
  if n >= 2 then return 0.7, snap.nearestEnemy, "unit" end
  if n >= 1 and (snap.numAllies or 0) >= 2 then return 0.55, snap.nearestEnemy, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["warlock_shadow_word"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.6 then return 0.8, ally, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.6, t, "unit" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["warlock_upheaval"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 and (snap.numAllies or 0) >= 1 and (snap.healthPct or 1) > 0.5 then return 0.75, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["warlock_rain_of_chaos"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  local w = Team.GetComboWindow()
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 and w ~= nil then return 0.95, snap.nearestEnemy, "location" end
  if n >= 2 and (snap.numAllies or 0) >= 2 then return 0.85, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
  },
  "limitations": "地狱火（Golem）无独立微操，只有通用召唤逻辑：R 只决定何时召唤，不控制魔像走位与集火。",
},
"weaver": {
  "abilities": {"Q": "weaver_the_swarm", "W": "weaver_shukuchi", "E": "weaver_geminate_attack", "R": "weaver_time_lapse"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_diffusal_blade", "item_black_king_bar", "item_linkens_sphere", "item_manta", "item_butterfly", "item_monkey_king_bar", "item_satanic", "item_moon_shard", "item_hurricane_pike"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_dragon_lance", "item_diffusal_blade", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_linkens_sphere"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_diffusal_blade", "item_black_king_bar", "item_assault", "item_heart", "item_abyssal_blade", "item_lotus_orb", "item_crimson_guard"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_rod_of_atos", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_gleipnir", "item_meteor_hammer"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer", "item_solar_crest"]},
  "consider": {
    "Q": """local ab = ab["weaver_the_swarm"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.7, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["weaver_shukuchi"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.9, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.7, nil, "none" end
  return 0, nil, "none\"""",
    "E": 'return 0, nil, "none"',
    "R": """local ab = ab["weaver_time_lapse"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 then return 1.0, nil, "none" end
  if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 2 then return 0.8, nil, "none" end
  return 0, nil, "none\"""",
  },
},
"windranger": {
  "abilities": {"Q": "windrunner_shackleshot", "W": "windrunner_powershot", "E": "windrunner_windrun", "R": "windrunner_focusfire"},
  "talents": {10: 1, 15: 0, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_maelstrom", "item_mjollnir", "item_black_king_bar", "item_manta", "item_butterfly", "item_monkey_king_bar", "item_daedalus"], 2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_maelstrom", "item_mjollnir", "item_black_king_bar", "item_aghanims_scepter", "item_blink", "item_monkey_king_bar", "item_scythe_of_vyse", "item_travel_boots", "item_moon_shard", "item_daedalus"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_maelstrom", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_shivas_guard", "item_aghanims_scepter", "item_lotus_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_maelstrom", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_blink", "item_gleipnir"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer", "item_solar_crest"]},
  "consider": {
    "Q": """local ab = ab["windrunner_shackleshot"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.85, snap.nearestEnemy, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.6, t, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["windrunner_powershot"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 900)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 then return 0.7, t, "location" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["windrunner_windrun"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.45 and (snap.numEnemies or 0) >= 1 then return 0.9, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and (snap.healthPct or 1) > 0.6 then return 0.6, nil, "none" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["windrunner_focusfire"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.6 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.9, t, "unit" end
  if pct > 0 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and (snap.healthPct or 1) > 0.5 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
  },
  "limitations": "技能名前缀 windrunner_ 来自手工整理的命名规则（英雄内部名为 windrunner），未在新版 d2vpk 中核对。",
},
"winter_wyvern": {
  "abilities": {"Q": "winter_wyvern_arctic_burn", "W": "winter_wyvern_splinter_blast", "E": "winter_wyvern_cold_embrace", "R": "winter_wyvern_winters_curse"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_hurricane_pike", "item_manta", "item_black_king_bar", "item_butterfly", "item_monkey_king_bar", "item_satanic"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_arcane_boots", "item_aether_lens", "item_aghanims_scepter", "item_octarine_core", "item_black_king_bar", "item_scythe_of_vyse", "item_bloodstone", "item_travel_boots"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_pipe_of_insight", "item_blink", "item_black_king_bar", "item_shivas_guard", "item_aghanims_scepter", "item_heart", "item_lotus_orb", "item_aeon_disk"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_blink", "item_lotus_orb", "item_meteor_hammer"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_blink", "item_aghanims_scepter", "item_lotus_orb", "item_aeon_disk", "item_ghost_scepter"]},
  "consider": {
    "Q": """local ab = ab["winter_wyvern_arctic_burn"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.75, snap.nearestEnemy, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.5 then return 0.7, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["winter_wyvern_splinter_blast"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.55, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["winter_wyvern_cold_embrace"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.4 then return 0.95, ally, "unit" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.9, bot, "unit" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["winter_wyvern_winters_curse"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 3 then return 1.0, snap.nearestEnemy, "unit" end
  if n >= 2 and (snap.numAllies or 0) >= 1 then return 0.85, snap.nearestEnemy, "unit" end
  return 0, nil, "none\"""",
  },
},
"witch_doctor": {
  "abilities": {"Q": "witch_doctor_paralyzing_cask", "W": "witch_doctor_voodoo_restoration", "E": "witch_doctor_maledict", "R": "witch_doctor_death_ward"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_hand_of_midas", "item_radiance", "item_black_king_bar", "item_assault", "item_heart", "item_satanic", "item_travel_boots"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_arcane_boots", "item_aether_lens", "item_aghanims_scepter", "item_octarine_core", "item_black_king_bar", "item_scythe_of_vyse", "item_bloodstone", "item_travel_boots"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_pipe_of_insight", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_heart", "item_lotus_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_blink", "item_aghanims_scepter", "item_ghost_scepter"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_blink", "item_aghanims_scepter", "item_black_king_bar", "item_ghost_scepter", "item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["witch_doctor_paralyzing_cask"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.9, snap.nearestEnemy, "unit" end
  if n >= 1 then return 0.65, snap.nearestEnemy, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["witch_doctor_voodoo_restoration"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.6 and (snap.numAllies or 0) >= 1 then return 0.75, nil, "none" end
  if (snap.healthPct or 1) < 0.5 and (snap.numAllies or 0) >= 1 then return 0.7, nil, "none" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["witch_doctor_maledict"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.6 and (snap.numAllies or 0) >= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.85, t, "unit" end
  if pct > 0 and pct < 0.6 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.8, t, "unit" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["witch_doctor_death_ward"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  local t = Skill.LowestHpEnemy(snap)
  if n >= 2 and (snap.healthPct or 1) > 0.5 and (snap.numAllies or 0) >= 1 then return 0.95, snap.nearestEnemy, "none" end
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and (snap.healthPct or 1) > 0.5 then return 0.85, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
  },
},
"wraith_king": {
  "abilities": {"Q": "skeleton_king_hellfire_blast", "W": "skeleton_king_vampiric_aura", "E": "skeleton_king_mortal_strike", "R": "skeleton_king_reincarnation"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_armlet", "item_blink", "item_radiance", "item_black_king_bar", "item_assault", "item_heart", "item_satanic", "item_abyssal_blade", "item_travel_boots", "item_moon_shard"], 2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_power_treads", "item_armlet", "item_blink", "item_black_king_bar", "item_desolator", "item_satanic", "item_assault", "item_abyssal_blade"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_blink", "item_black_king_bar", "item_blade_mail", "item_assault", "item_heart", "item_crimson_guard", "item_abyssal_blade"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_blink", "item_force_staff", "item_solar_crest", "item_black_king_bar", "item_lotus_orb", "item_meteor_hammer"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer", "item_solar_crest"]},
  "consider": {
    "Q": """local ab = ab["skeleton_king_hellfire_blast"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.8, snap.nearestEnemy, "unit" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.75, t, "unit" end
  return 0, nil, "none\"""",
    "W": 'return 0, nil, "none"',
    "E": 'return 0, nil, "none"',
    "R": 'return 0, nil, "none"',
  },
  "limitations": "W（吸血光环）、E（致命一击）、R（重生）均为被动，仅 Q 地狱火爆有主动 Consider。技能名前缀 skeleton_king_ 来自手工整理的命名规则（英雄内部名为 skeleton_king），未在新版 d2vpk 中核对。",
},
"invoker": {
  "abilities": {"Q": "invoker_quas", "W": "invoker_wex", "E": "invoker_exort", "R": "invoker_invoke"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_hand_of_midas", "item_black_king_bar", "item_assault", "item_heart", "item_satanic", "item_butterfly", "item_travel_boots"], 2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_scythe_of_vyse", "item_refresher_orb", "item_kaya_and_sange", "item_blink", "item_travel_boots", "item_aeon_disk", "item_bloodstone"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_pipe_of_insight", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_heart", "item_lotus_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_euls_scepter_of_divinity", "item_blink", "item_octarine_core"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer", "item_aether_lens"]},
  "consider": {
    "Q": 'return 0, nil, "none"',
    "W": 'return 0, nil, "none"',
    "E": 'return 0, nil, "none"',
    "R": """local ab = ab["invoker_invoke"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  return 0, nil, "none\"""",
  },
  "invoked": {
    "invoker_cold_snap": """local ab = ab["invoker_cold_snap"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.6 and (snap.numAllies or 0) >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.85, t, "unit" end
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
    "invoker_emp": """local ab = ab["invoker_emp"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 3 then return 0.95, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "invoker_tornado": """local ab = ab["invoker_tornado"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 800)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "invoker_sun_strike": """local ab = ab["invoker_sun_strike"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.25 then return 0.95, t, "location" end
  if pct > 0 and pct < 0.4 and (snap.numAllies or 0) >= 1 then return 0.8, t, "location" end
  return 0, nil, "none\"""",
    "invoker_chaos_meteor": """local ab = ab["invoker_chaos_meteor"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 3 then return 0.95, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "invoker_deafening_blast": """local ab = ab["invoker_deafening_blast"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 and (snap.healthPct or 1) < 0.5 then return 0.9, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "invoker_forge_spirit": """local ab = ab["invoker_forge_spirit"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.numAllies or 0) >= 1 then return 0.6, snap.nearestEnemy, "none" end
  if (snap.numEnemies or 0) == 0 and #snap.nearbyEnemyCreeps > 0 then return 0.55, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
    "invoker_ghost_walk": """local ab = ab["invoker_ghost_walk"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 1.0, nil, "none" end
  if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 2 then return 0.85, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "Invoke 机制：当已有 invoked 技能可用时不急着按 Invoke，R 的 Consider 因此只做可用性检查、不主动触发；球（Quas/Wex/Exort）是被动球、Q/W/E 的 Consider 只返回 0。本表只建模 8 个常用 invoked 技能，alacrity / ice_wall 未建模；锻造之灵无独立微操。",
},
"kez": {
  "abilities": {"Q": "kez_echo_slash", "W": "kez_grappling_claw", "E": "kez_kazurai_katana", "R": "kez_raptor_dance"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_phase_boots", "item_echo_sabre", "item_black_king_bar", "item_manta", "item_butterfly", "item_abyssal_blade", "item_harpoon", "item_monkey_king_bar", "item_satanic", "item_moon_shard", "item_travel_boots"], 2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_echo_sabre", "item_diffusal_blade", "item_black_king_bar", "item_manta", "item_aghanims_scepter", "item_butterfly", "item_satanic"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_echo_sabre", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_abyssal_blade", "item_crimson_guard"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_echo_sabre", "item_force_staff", "item_blink", "item_black_king_bar", "item_solar_crest", "item_lotus_orb"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer", "item_solar_crest"]},
  "consider": {
    "Q": """local ab = ab["kez_echo_slash"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.85, t, "unit" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.7, snap.nearestEnemy, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["kez_grappling_claw"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.6 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 and snap.nearestEnemyDist > 300 then return 0.8, t, "unit" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 and snap.nearestEnemy ~= nil then return 0.75, snap.nearestEnemy, "unit" end
  return 0, nil, "none\"""",
    "E": 'return 0, nil, "none"',
    "R": """local ab = ab["kez_raptor_dance"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.5 then return 0.8, nil, "none" end
  if (snap.healthPct or 1) < 0.4 and (snap.numEnemies or 0) >= 1 then return 0.7, nil, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "只建模 Kazurai Katana 姿态，Sai 姿态未建模（falcon_rush / talon_toss / ravens_veil 不在 4 槽模型里）。技能名来自手工整理的命名规则，未在新版 d2vpk 中核对。",
},
"largo": {
  "abilities": {"Q": "largo_catchy_lick", "W": "largo_frogstomp", "E": "largo_croak_of_genius", "R": "largo_amphibian_rhapsody"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_vanguard", "item_radiance", "item_black_king_bar", "item_assault", "item_heart", "item_satanic", "item_abyssal_blade"], 2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_arcane_boots", "item_aether_lens", "item_aghanims_scepter", "item_octarine_core", "item_black_king_bar", "item_scythe_of_vyse", "item_bloodstone", "item_travel_boots"], 3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_pipe_of_insight", "item_blink", "item_black_king_bar", "item_shivas_guard", "item_heart", "item_assault", "item_lotus_orb"], 4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_blink", "item_aether_lens", "item_pipe_of_insight", "item_lotus_orb", "item_aghanims_scepter", "item_meteor_hammer"], 5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer", "item_solar_crest"]},
  "consider": {
    "Q": """local ab = ab["largo_catchy_lick"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and (snap.numAllies or 0) >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.7, t, "unit" end
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.55, t, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["largo_frogstomp"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.85, snap.nearestEnemy, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 then return 0.7, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["largo_croak_of_genius"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numAllies or 0) >= 1 and (snap.numEnemies or 0) >= 1 then return 0.7, nil, "none" end
  if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 1 then return 0.6, nil, "none" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["largo_amphibian_rhapsody"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.numAllies or 0) >= 1 then return 0.9, snap.nearestEnemy, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.numAllies or 0) >= 1 then return 0.6, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
  },
  "limitations": "内部名按命名规则推断，未在新版 d2vpk 中核对；R 的节奏玩法未建模，只写切换条件（团战开始且队友在附近时开）；Q/E 的具体机制未核实，条件为保守的通用条件。",
},
}
