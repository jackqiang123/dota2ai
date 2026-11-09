# -*- coding: utf-8 -*-
"""焦点英雄深度数据 (v2.0.0, tools/generate.py 的第二事实源, 与 heroes_data.py 并列)。
只覆盖 10 个焦点英雄, 其余 117 个走通用 fallback (见 generate.py)。
每项:
  abilities: {Q/W/E/R: 真实内部技能名}。E 为被动时 ConsiderE 返回 0。
  consider: {Q/W/E/R: Lua 函数体字符串}。签名 ConsiderX(bot, snap, ab),
    ab 为 Skill.GetAbilityMap(bot) 返回的 name->ability 表, 返回 desire(0-1), target, castType。
    castType: "unit" / "location" / "none"。desire>=0.5 才由 SkillsComplement 真正施放。
  talents: {10/15/20/25: 0=左, 1=右}。本项目自选, 非官方推荐, 仅作可玩的完整选择。
  items: {pos: [>=10 件]} 主位置写满, 其余位置可复用主位置或通用表。
技能名均为 Dota 2 真实内部名, 用 GetAbilityByName / 动态槽位表读取, 不写死槽位号。
"""
FOCUS = {
"axe": {
  "abilities": {"Q": "axe_berserkers_call", "W": "axe_battle_hunger", "E": "axe_counter_helix", "R": "axe_culling_blade"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {3: ["item_tango","item_flask","item_vanguard","item_phase_boots","item_blink","item_blade_mail","item_black_king_bar","item_aghanims_shard","item_heart","item_assault","item_overwhelming_blink","item_travel_boots","item_shivas_guard","item_crimson_guard"]},
  "consider": {
    "Q": """local ab = ab["axe_berserkers_call"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 300)
  local hp = snap.healthPct or 1
  if n >= 2 and hp > 0.35 then return 0.95, snap.nearestEnemy, "none" end
  if n >= 1 and hp > 0.6 then return 0.7, snap.nearestEnemy, "none" end
  if n >= 3 then return 0.85, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["axe_battle_hunger"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.6, t, "unit" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["axe_culling_blade"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local hp = Skill.HpOf(t)
  if hp > 0 and hp < 250 then return 1.0, t, "unit" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.2 then return 0.9, t, "unit" end
  return 0, nil, "none\"""",
  },
},
"zeus": {
  "abilities": {"Q": "zeus_arc_lightning", "W": "zeus_lightning_bolt", "E": "zeus_static_field", "R": "zeus_thundergods_wrath"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {2: ["item_tango","item_flask","item_null_talisman","item_bottle","item_power_treads","item_aether_lens","item_aghanims_scepter","item_octarine_core","item_black_king_bar","item_refresher_orb","item_scythe_of_vyse","item_travel_boots","item_kaya_and_sange"]},
  "consider": {
    "Q": """local ab = ab["zeus_arc_lightning"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.8, snap.nearestEnemy, "unit" end
  if n >= 1 then return 0.55, snap.nearestEnemy, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["zeus_lightning_bolt"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.75, t, "unit" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["zeus_thundergods_wrath"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local low = Skill.CountLowHpEnemies(snap, 0.35)
  if low >= 2 then return 0.95, nil, "none" end
  if low >= 1 then return 0.75, nil, "none" end
  return 0, nil, "none\"""",
  },
},
"lion": {
  "abilities": {"Q": "lion_impale", "W": "lion_voodoo", "E": "lion_mana_drain", "R": "lion_finger_of_death"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {5: ["item_tango","item_flask","item_clarity","item_ward_observer","item_magic_wand","item_arcane_boots","item_blink","item_aether_lens","item_aghanims_scepter","item_black_king_bar","item_force_staff","item_glimmer_cape","item_scythe_of_vyse"]},
  "consider": {
    "Q": """local ab = ab["lion_impale"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["lion_voodoo"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["lion_mana_drain"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.4 and snap.nearestEnemy ~= nil then return 0.6, snap.nearestEnemy, "unit" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["lion_finger_of_death"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local hp = Skill.HpOf(t)
  if hp > 0 and hp < 500 then return 1.0, t, "unit" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.3 then return 0.85, t, "unit" end
  return 0, nil, "none\"""",
  },
},
"crystal_maiden": {
  "abilities": {"Q": "crystal_maiden_crystal_nova", "W": "crystal_maiden_frostbite", "E": "crystal_maiden_brilliance_aura", "R": "crystal_maiden_freezing_field"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {5: ["item_tango","item_flask","item_clarity","item_ward_observer","item_magic_wand","item_arcane_boots","item_glimmer_cape","item_force_staff","item_aether_lens","item_black_king_bar","item_aghanims_scepter","item_ghost_scepter","item_euls_scepter_of_divinity"]},
  "consider": {
    "Q": """local ab = ab["crystal_maiden_crystal_nova"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.55, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["crystal_maiden_frostbite"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "unit" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["crystal_maiden_freezing_field"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.95, snap.nearestEnemy, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.5 then return 0.6, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
  },
},
"magnus": {
  "abilities": {"Q": "magnus_shockwave", "W": "magnus_empower", "E": "magnus_skewer", "R": "magnus_reverse_polarity"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {3: ["item_tango","item_flask","item_bracer","item_phase_boots","item_blink","item_black_king_bar","item_aghanims_scepter","item_refresher_orb","item_assault","item_shivas_guard","item_heart","item_echo_sabre","item_harpoon"]},
  "consider": {
    "Q": """local ab = ab["magnus_shockwave"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 900)
  if n >= 2 then return 0.7, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.5, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["magnus_empower"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally = Skill.LowestHpAlly(snap)
  if ally ~= nil then return 0.6, ally, "unit" end
  if (snap.healthPct or 1) > 0.5 then return 0.55, bot, "unit" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["magnus_skewer"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["magnus_reverse_polarity"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 3 then return 1.0, snap.nearestEnemy, "none" end
  if n >= 2 then return 0.9, snap.nearestEnemy, "none" end
  return 0, nil, "none\"""",
  },
},
"faceless_void": {
  "abilities": {"Q": "faceless_void_time_walk", "W": "faceless_void_time_dilation", "E": "faceless_void_time_lock", "R": "faceless_void_chronosphere"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {1: ["item_tango","item_flask","item_quelling_blade","item_wraith_band","item_power_treads","item_maelstrom","item_black_king_bar","item_manta","item_satanic","item_butterfly","item_abyssal_blade","item_mjollnir","item_travel_boots"]},
  "consider": {
    "Q": """local ab = ab["faceless_void_time_walk"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.85, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.3 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["faceless_void_time_dilation"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["faceless_void_chronosphere"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local w = Team.GetComboWindow()
  if w ~= nil and w.caster ~= nil and string.find(w.caster, "enigma", 1, true) ~= nil then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 425)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
  },
},
"enigma": {
  "abilities": {"Q": "enigma_malefice", "W": "enigma_demonic_conversion", "E": "enigma_midnight_pulse", "R": "enigma_black_hole"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {3: ["item_tango","item_flask","item_bracer","item_arcane_boots","item_blink","item_black_king_bar","item_aghanims_scepter","item_refresher_orb","item_shivas_guard","item_octarine_core","item_travel_boots","item_aeon_disk","item_heart"]},
  "consider": {
    "Q": """local ab = ab["enigma_malefice"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.6, t, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["enigma_demonic_conversion"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) == 0 and #snap.nearbyEnemyCreeps > 0 then return 0.55, snap.nearbyEnemyCreeps[1], "unit" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["enigma_midnight_pulse"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.7, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["enigma_black_hole"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  return 0, nil, "none\"""",
  },
},
"dazzle": {
  "abilities": {"Q": "dazzle_poison_touch", "W": "dazzle_shallow_grave", "E": "dazzle_shadow_wave", "R": "dazzle_bad_juju"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {5: ["item_tango","item_flask","item_clarity","item_ward_observer","item_magic_wand","item_arcane_boots","item_force_staff","item_glimmer_cape","item_aether_lens","item_aghanims_scepter","item_lotus_orb","item_black_king_bar","item_ghost_scepter"]},
  "consider": {
    "Q": """local ab = ab["dazzle_poison_touch"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.6, t, "unit" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["dazzle_shallow_grave"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.35 then return 1.0, ally, "unit" end
  if (snap.healthPct or 1) < 0.35 then return 0.95, bot, "unit" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["dazzle_shadow_wave"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.6 then return 0.75, ally, "unit" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["dazzle_bad_juju"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 then return 0.55, nil, "none" end
  return 0, nil, "none\"""",
  },
},
"oracle": {
  "abilities": {"Q": "oracle_fortunes_end", "W": "oracle_fates_edict", "E": "oracle_purifying_flames", "R": "oracle_false_promise"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {5: ["item_tango","item_flask","item_clarity","item_ward_observer","item_magic_wand","item_arcane_boots","item_force_staff","item_glimmer_cape","item_aether_lens","item_aghanims_scepter","item_euls_scepter_of_divinity","item_ghost_scepter","item_lotus_orb"]},
  "consider": {
    "Q": """local ab = ab["oracle_fortunes_end"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.6, t, "location" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["oracle_fates_edict"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.4 then return 0.85, ally, "unit" end
  return 0, nil, "none\"""",
    "E": """local ab = ab["oracle_purifying_flames"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.6 then return 0.7, ally, "unit" end
  return 0, nil, "none\"""",
    "R": """local ab = ab["oracle_false_promise"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.3 then return 1.0, ally, "unit" end
  if (snap.healthPct or 1) < 0.3 then return 0.95, bot, "unit" end
  return 0, nil, "none\"""",
  },
},
"huskar": {
  "abilities": {"Q": "huskar_inner_fire", "W": "huskar_burning_spear", "E": "huskar_berserkers_blood", "R": "huskar_life_break"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {1: ["item_tango","item_flask","item_bracer","item_phase_boots","item_armlet","item_black_king_bar","item_satanic","item_aghanims_scepter","item_assault","item_heavens_halberd","item_travel_boots","item_heart","item_sange_and_yasha"]},
  "consider": {
    "Q": """local ab = ab["huskar_inner_fire"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.75, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) < 0.5 then return 0.65, nil, "none" end
  return 0, nil, "none\"""",
    "W": """local ab = ab["huskar_burning_spear"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 550 then return 0.65, t, "unit" end
  return 0, nil, "none\"""",
    "E": """return 0, nil, "none\"""",
    "R": """local ab = ab["huskar_life_break"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.5 and (snap.healthPct or 1) > 0.4 then return 0.9, t, "unit" end
  if pct > 0 and pct < 0.3 then return 0.95, t, "unit" end
  return 0, nil, "none\"""",
  },
},
}
FOCUS_HEROES = sorted(FOCUS.keys())
