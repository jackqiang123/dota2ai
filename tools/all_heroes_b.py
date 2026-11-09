# -*- coding: utf-8 -*-
"""B 组英雄深度数据 (v3.0.0, tools/generate.py 的事实源之一, 与 heroes_data.py 并列)。
覆盖 20 个英雄: dawnbreaker, death_prophet, disruptor, doom, dragon_knight,
drow_ranger, earth_spirit, earthshaker, elder_titan, ember_spirit, enchantress,
grimstroke, gyrocopter, hoodwink, io, jakiro, juggernaut, keeper_of_the_light,
kunkka, legion_commander。
每项:
  abilities: {Q/W/E/R: 真实内部技能名}。一律取自 tools/skill_names_reference.json,
    一个不编、一个不换; 名字可疑时在 limitations 里写明, 不自行替换。
  consider: {Q/W/E/R: Lua 函数体字符串}。签名 ConsiderX(bot, snap, ab),
    ab 为 Skill.GetAbilityMap(bot) 返回的 name->ability 表, 返回 desire(0-1), target, castType。
    castType: "unit" / "location" / "none"。被动技能的 Consider 只写 return 0, nil, "none"。
    只用白名单 API: Skill.IsCastable / CountEnemiesInRange / CountLowHpEnemies /
    LowestHpEnemy / LowestHpAlly / LowestHpAllyPct / HpOf / HpPctOf,
    snap 字段, Team.ShouldHoldUlt(bot) / Team.GetComboWindow()。
  talents: {10/15/20/25: 0=左, 1=右}。本项目自选, 非官方推荐, 仅作可玩的完整选择。
  items: {pos: [>=8 件]} 主位置 >=12 件且前期-中期-后期有递进, 其余位置各不相同。
技能名均为 Dota 2 真实内部名, 用 GetAbilityByName / 动态槽位表读取, 不写死槽位号。
全部 Lua 条件均为原创, 未复制 OHA / adam 的任何代码。
"""
ALL_B = {
"dawnbreaker": {
  "abilities": {"Q": "dawnbreaker_starbreaker", "W": "dawnbreaker_celestial_hammer", "E": "dawnbreaker_luminosity", "R": "dawnbreaker_solar_guardian"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_echo_sabre", "item_desolator", "item_black_king_bar", "item_assault", "item_satanic", "item_butterfly", "item_harpoon", "item_aghanims_scepter"],
    2: ["item_tango", "item_flask", "item_bottle", "item_phase_boots", "item_echo_sabre", "item_desolator", "item_black_king_bar", "item_blink", "item_aghanims_shard", "item_assault", "item_satanic", "item_harpoon"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_echo_sabre", "item_desolator", "item_black_king_bar", "item_blink", "item_assault", "item_aghanims_shard", "item_harpoon", "item_satanic", "item_heart", "item_travel_boots"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_blink", "item_solar_crest", "item_force_staff", "item_glimmer_cape", "item_black_king_bar"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_solar_crest"],
  },
  "consider": {
    "Q": """local ab = ab["dawnbreaker_starbreaker"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 350)
if n >= 2 then return 0.9, snap.nearestEnemy, "none" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 then return 0.85, t, "none" end
if n >= 1 and (snap.healthPct or 1) > 0.6 then return 0.6, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
    "W": """local ab = ab["dawnbreaker_celestial_hammer"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 800)
if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.75, t, "location" end
if n >= 1 and (snap.manaPct or 1) > 0.5 then return 0.55, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["dawnbreaker_solar_guardian"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local ally, pct = Skill.LowestHpAllyPct(snap)
if ally ~= nil and pct < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.95, ally, "unit" end
if ally ~= nil and pct < 0.5 and (snap.numEnemies or 0) >= 2 then return 0.75, ally, "unit" end
if (snap.healthPct or 1) < 0.3 and (snap.numEnemies or 0) >= 2 then return 0.85, bot, "unit" end
return 0, nil, "none"
""",
  },
},
"death_prophet": {
  "abilities": {"Q": "death_prophet_carrion_swarm", "W": "death_prophet_silence", "E": "death_prophet_spirit_siphon", "R": "death_prophet_exorcism"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_octarine_core", "item_shivas_guard", "item_scythe_of_vyse", "item_aghanims_scepter", "item_travel_boots", "item_heart"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_octarine_core", "item_shivas_guard", "item_aghanims_scepter", "item_scythe_of_vyse", "item_kaya_and_sange", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_shivas_guard", "item_octarine_core", "item_pipe_of_insight", "item_aghanims_scepter"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_euls_scepter_of_divinity", "item_glimmer_cape", "item_force_staff", "item_aghanims_shard"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_euls_scepter_of_divinity"],
  },
  "consider": {
    "Q": """local ab = ab["death_prophet_carrion_swarm"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 700)
if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.75, t, "location" end
if n >= 1 and (snap.manaPct or 1) > 0.5 then return 0.55, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
    "W": """local ab = ab["death_prophet_silence"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
if n >= 1 and (snap.numAllies or 0) >= 1 then return 0.6, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
    "E": """local ab = ab["death_prophet_spirit_siphon"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and (snap.healthPct or 1) < 0.7 then return 0.75, t, "unit" end
  if t ~= nil and Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "unit" end
  return 0, nil, "none"
""",
    "R": """local ab = ab["death_prophet_exorcism"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 and (snap.healthPct or 1) > 0.4 and (snap.manaPct or 1) > 0.3 then return 0.95, snap.nearestEnemy, "none" end
local low = Skill.CountLowHpEnemies(snap, 0.35)
if low >= 1 and (snap.healthPct or 1) > 0.5 then return 0.8, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
  },
  "limitations": "v3.0 已订正: E 为 death_prophet_spirit_siphon(灵魂吸取)。",
},
"disruptor": {
  "abilities": {"Q": "disruptor_thunder_strike", "W": "disruptor_glimpse", "E": "disruptor_kinetic_field", "R": "disruptor_static_storm"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_aether_lens", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_scythe_of_vyse", "item_refresher_orb", "item_travel_boots", "item_shivas_guard"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_arcane_boots", "item_aether_lens", "item_euls_scepter_of_divinity", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_scythe_of_vyse", "item_refresher_orb"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_black_king_bar", "item_aghanims_scepter", "item_pipe_of_insight"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_euls_scepter_of_divinity"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_euls_scepter_of_divinity", "item_aghanims_scepter", "item_ghost_scepter", "item_black_king_bar"],
  },
  "consider": {
    "Q": """local ab = ab["disruptor_thunder_strike"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.8, t, "unit" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.6, t, "unit" end
return 0, nil, "none"
""",
    "W": """local ab = ab["disruptor_glimpse"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 then return 0.8, t, "unit" end
if (snap.numAllies or 0) >= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.65, t, "unit" end
return 0, nil, "none"
""",
    "E": """local ab = ab["disruptor_kinetic_field"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 500)
if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.7, t, "location" end
return 0, nil, "none"
""",
    "R": """local ab = ab["disruptor_static_storm"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
local w = Team.GetComboWindow()
if w ~= nil then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 500)
if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
if n >= 2 and (snap.manaPct or 1) > 0.25 then return 0.9, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
  },
},
"doom": {
  "abilities": {"Q": "doom_bringer_devour", "W": "doom_bringer_scorched_earth", "E": "doom_bringer_infernal_blade", "R": "doom_bringer_doom"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_phase_boots", "item_vanguard", "item_radiance", "item_black_king_bar", "item_blink", "item_assault", "item_heart", "item_satanic", "item_shivas_guard", "item_aghanims_scepter", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_phase_boots", "item_vanguard", "item_radiance", "item_black_king_bar", "item_blink", "item_octarine_core", "item_shivas_guard", "item_heart", "item_aghanims_scepter"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_radiance", "item_blink", "item_black_king_bar", "item_shivas_guard", "item_assault", "item_heart", "item_aghanims_shard", "item_travel_boots", "item_octarine_core"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_lotus_orb"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_pipe_of_insight"],
  },
  "consider": {
    "Q": """local ab = ab["doom_bringer_devour"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.numEnemies or 0) == 0 and (snap.manaPct or 1) > 0.4 and #snap.nearbyEnemyCreeps > 0 then return 0.6, snap.nearbyEnemyCreeps[1], "unit" end
return 0, nil, "none"
""",
    "W": """local ab = ab["doom_bringer_scorched_earth"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 400)
if n >= 2 then return 0.85, snap.nearestEnemy, "none" end
if n >= 1 and (snap.healthPct or 1) < 0.7 then return 0.75, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
    "E": """local ab = ab["doom_bringer_infernal_blade"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.8, t, "unit" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.6, t, "unit" end
return 0, nil, "none"
""",
    "R": """local ab = ab["doom_bringer_doom"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
local pct = Skill.HpPctOf(t)
local hp = Skill.HpOf(t)
if pct > 0 and pct < 0.5 and hp > 600 and (snap.healthPct or 1) > 0.45 then return 0.95, t, "unit" end
if pct > 0 and pct < 0.3 and (snap.healthPct or 1) > 0.35 then return 0.85, t, "unit" end
return 0, nil, "none"
""",
  },
  "limitations": "Devour 只能取 snap.nearbyEnemyCreeps 里最近的一只野怪, 没有野怪种类信息, 无法优先挑带光环/主动技能的野怪。",
},
"dragon_knight": {
  "abilities": {"Q": "dragon_knight_breathe_fire", "W": "dragon_knight_dragon_tail", "E": "dragon_knight_dragon_blood", "R": "dragon_knight_elder_dragon_form"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_armlet", "item_black_king_bar", "item_blink", "item_assault", "item_heart", "item_satanic", "item_daedalus", "item_aghanims_scepter", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_power_treads", "item_armlet", "item_black_king_bar", "item_blink", "item_assault", "item_daedalus", "item_satanic", "item_aghanims_shard"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_armlet", "item_black_king_bar", "item_blink", "item_assault", "item_shivas_guard", "item_heart", "item_aghanims_scepter", "item_pipe_of_insight"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_blink", "item_black_king_bar", "item_solar_crest", "item_force_staff", "item_aghanims_shard"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_solar_crest"],
  },
  "consider": {
    "Q": """local ab = ab["dragon_knight_breathe_fire"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
if n >= 1 and (snap.manaPct or 1) > 0.5 then return 0.55, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
    "W": """local ab = ab["dragon_knight_dragon_tail"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 then return 0.85, t, "unit" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 then return 0.65, t, "unit" end
return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["dragon_knight_elder_dragon_form"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 and (snap.healthPct or 1) > 0.5 then return 0.95, snap.nearestEnemy, "none" end
if n >= 1 and (snap.healthPct or 1) > 0.6 then return 0.8, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
  },
},
"drow_ranger": {
  "abilities": {"Q": "drow_ranger_frost_arrows", "W": "drow_ranger_wave_of_silence", "E": "drow_ranger_multishot", "R": "drow_ranger_marksmanship"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_manta", "item_butterfly", "item_satanic", "item_daedalus", "item_aghanims_shard", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_manta", "item_daedalus", "item_butterfly", "item_satanic", "item_monkey_king_bar"],
    3: ["item_tango", "item_flask", "item_wraith_band", "item_phase_boots", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_manta", "item_butterfly", "item_aghanims_scepter", "item_satanic", "item_assault"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_dragon_lance", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_hurricane_pike"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_dragon_lance"],
  },
  "consider": {
    "Q": """local ab = ab["drow_ranger_frost_arrows"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.8, t, "unit" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.6, t, "unit" end
return 0, nil, "none"
""",
    "W": """local ab = ab["drow_ranger_wave_of_silence"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 500)
if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 300 and (snap.healthPct or 1) < 0.6 then return 0.85, snap.nearestEnemy, "location" end
if n >= 1 and (snap.manaPct or 1) > 0.5 then return 0.55, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
    "E": """local ab = ab["drow_ranger_multishot"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
    "R": """return 0, nil, "none"
""",
  },
  "limitations": "v3.0 已订正: E 为 drow_ranger_multishot(多重射击)。W 名 wave_of_silence 可能是 Gust of Wind 保留的旧内部名, 按原样保留。",
},
"earth_spirit": {
  "abilities": {"Q": "earth_spirit_boulder_smash", "W": "earth_spirit_rolling_boulder", "E": "earth_spirit_geomagnetic_grip", "R": "earth_spirit_magnetize"},
  "talents": {10: 0, 15: 1, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_blink", "item_octarine_core", "item_heart", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_power_treads", "item_euls_scepter_of_divinity", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_shivas_guard", "item_scythe_of_vyse"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_euls_scepter_of_divinity", "item_shivas_guard", "item_aghanims_scepter", "item_lotus_orb", "item_heart", "item_pipe_of_insight"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_blink", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_aghanims_scepter", "item_lotus_orb", "item_aeon_disk", "item_ghost_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_euls_scepter_of_divinity"],
  },
  "consider": {
    "Q": """local ab = ab["earth_spirit_boulder_smash"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 then return 0.8, snap.nearestEnemy, "unit" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.75, t, "unit" end
if n >= 1 and (snap.manaPct or 1) > 0.4 then return 0.55, snap.nearestEnemy, "unit" end
return 0, nil, "none"
""",
    "W": """local ab = ab["earth_spirit_rolling_boulder"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.manaPct or 1) < 0.4 then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 then return 0.8, t, "location" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 300 and snap.nearestEnemyDist <= 900 then return 0.7, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
    "E": """local ab = ab["earth_spirit_geomagnetic_grip"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local ally, pct = Skill.LowestHpAllyPct(snap)
if ally ~= nil and pct < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.85, ally, "unit" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.65, t, "unit" end
return 0, nil, "none"
""",
    "R": """local ab = ab["earth_spirit_magnetize"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.manaPct or 1) < 0.35 then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 500)
if n >= 2 then return 0.9, snap.nearestEnemy, "none" end
local low = Skill.CountLowHpEnemies(snap, 0.35)
if low >= 1 then return 0.7, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
  },
  "limitations": "大地之灵的全部连招都依赖残岩(Stone Remnant)的数量与落点, 但允许的 API 里没有残岩计数/位置字段, 因此 Q/W/R 的时机判断默认残岩够用, 不做残岩约束; 实战中缺残岩时这些 Consider 会高估。",
},
"earthshaker": {
  "abilities": {"Q": "earthshaker_fissure", "W": "earthshaker_enchant_totem", "E": "earthshaker_aftershock", "R": "earthshaker_echo_slam"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_assault", "item_heart", "item_shivas_guard", "item_overwhelming_blink", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_arcane_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_refresher_orb", "item_octarine_core", "item_shivas_guard", "item_scythe_of_vyse"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_lotus_orb", "item_heart", "item_assault", "item_aeon_disk"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_force_staff", "item_glimmer_cape", "item_lotus_orb", "item_aether_lens", "item_euls_scepter_of_divinity", "item_refresher_orb"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_blink", "item_aether_lens", "item_aghanims_shard"],
  },
  "consider": {
    "Q": """local ab = ab["earthshaker_fissure"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 700)
if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
if (snap.healthPct or 1) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 then return 0.8, snap.nearestEnemy, "location" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.7, t, "location" end
return 0, nil, "none"
""",
    "W": """local ab = ab["earthshaker_enchant_totem"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 500)
if n >= 2 and (snap.healthPct or 1) > 0.4 then return 0.8, snap.nearestEnemy, "none" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 300 and (snap.healthPct or 1) > 0.4 then return 0.7, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["earthshaker_echo_slam"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
local w = Team.GetComboWindow()
if w ~= nil then return 0, nil, "none" end
if (snap.healthPct or 1) < 0.35 then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 400)
if n >= 3 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 1.0, snap.nearestEnemy, "none" end
if n >= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.9, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
  },
  "limitations": "回响击的跳刀先手无法用允许的 API 直接检测是否持有跳刀, 这里用最近敌人距离 <=600 作为已经切入的代理条件; 若跳刀在冷却而人已在圈内, 该条件仍会放行。",
},
"elder_titan": {
  "abilities": {"Q": "elder_titan_echo_stomp", "W": "elder_titan_ancestral_spirit", "E": "elder_titan_natural_order", "R": "elder_titan_earth_splitter"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_shivas_guard", "item_aghanims_scepter", "item_assault", "item_heart", "item_refresher_orb", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_arcane_boots", "item_blink", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_shivas_guard", "item_aghanims_scepter", "item_octarine_core", "item_refresher_orb"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_shivas_guard", "item_pipe_of_insight", "item_aghanims_scepter", "item_lotus_orb", "item_heart", "item_assault", "item_aeon_disk", "item_travel_boots"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_aether_lens"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_blink"],
  },
  "consider": {
    "Q": """local ab = ab["elder_titan_echo_stomp"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 400)
if n >= 2 then return 0.85, snap.nearestEnemy, "none" end
if n >= 1 and (snap.healthPct or 1) > 0.5 then return 0.6, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
    "W": """local ab = ab["elder_titan_ancestral_spirit"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 700)
if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
if n >= 1 and (snap.manaPct or 1) > 0.4 then return 0.6, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["elder_titan_earth_splitter"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  return 0, nil, "none"
""",
  },
  "limitations": "v3.0 已订正: R 为 elder_titan_earth_splitter(大地分裂)。",
},
"ember_spirit": {
  "abilities": {"Q": "ember_spirit_searing_chains", "W": "ember_spirit_sleight_of_fist", "E": "ember_spirit_flame_guard", "R": "ember_spirit_activate_fire_remnant"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_maelstrom", "item_black_king_bar", "item_desolator", "item_mjollnir", "item_daedalus", "item_butterfly", "item_aghanims_scepter", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_maelstrom", "item_black_king_bar", "item_desolator", "item_aghanims_scepter", "item_mjollnir", "item_daedalus", "item_octarine_core", "item_travel_boots", "item_satanic"],
    3: ["item_tango", "item_flask", "item_wraith_band", "item_phase_boots", "item_maelstrom", "item_black_king_bar", "item_desolator", "item_manta", "item_aghanims_scepter", "item_assault", "item_heart", "item_shivas_guard"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_maelstrom", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_force_staff", "item_glimmer_cape"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_euls_scepter_of_divinity"],
  },
  "consider": {
    "Q": """local ab = ab["ember_spirit_searing_chains"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 400)
if n >= 2 then return 0.8, snap.nearestEnemy, "unit" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.75, t, "unit" end
if n >= 1 then return 0.55, snap.nearestEnemy, "unit" end
return 0, nil, "none"
""",
    "W": """local ab = ab["ember_spirit_sleight_of_fist"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.manaPct or 1) < 0.4 then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 500)
if n >= 2 then return 0.75, snap.nearestEnemy, "none" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.3 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.7, t, "none" end
return 0, nil, "none"
""",
    "E": """local ab = ab["ember_spirit_flame_guard"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.manaPct or 1) < 0.3 then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 500)
if n >= 2 then return 0.75, snap.nearestEnemy, "none" end
if n >= 1 and (snap.healthPct or 1) < 0.8 then return 0.7, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
    "R": """local ab = ab["ember_spirit_activate_fire_remnant"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.healthPct or 1) < 0.3 and (snap.numEnemies or 0) >= 1 then return 0.95, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.25 and (snap.manaPct or 1) > 0.3 then return 0.7, nil, "none" end
return 0, nil, "none"
""",
  },
  "limitations": "R 名 activate_fire_remnant 是跳向余烬的子技能, 放置余烬本身是另一个子技能(ember_spirit_fire_remnant); 允许的 API 里没有余烬数量/位置字段, 因此 R 的 Consider 只管跳的时机(残血逃生或追残血), 无法确认场上是否真的有余烬可跳。",
},
"enchantress": {
  "abilities": {"Q": "enchantress_enchant", "W": "enchantress_natures_attendants", "E": "enchantress_untouchable", "R": "enchantress_impetus"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_manta", "item_butterfly", "item_daedalus", "item_aghanims_scepter", "item_monkey_king_bar"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_manta", "item_butterfly"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_force_staff", "item_lotus_orb", "item_aghanims_scepter", "item_assault", "item_heart"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_force_staff", "item_glimmer_cape", "item_hurricane_pike", "item_black_king_bar", "item_lotus_orb"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_hurricane_pike", "item_aether_lens", "item_aghanims_scepter", "item_lotus_orb", "item_black_king_bar"],
  },
  "consider": {
    "Q": """local ab = ab["enchantress_enchant"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.numEnemies or 0) == 0 and #snap.nearbyEnemyCreeps > 0 then return 0.5, snap.nearbyEnemyCreeps[1], "unit" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.6, t, "unit" end
return 0, nil, "none"
""",
    "W": """local ab = ab["enchantress_natures_attendants"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local ally, pct = Skill.LowestHpAllyPct(snap)
if ally ~= nil and pct < 0.6 and (snap.numEnemies or 0) >= 1 then return 0.8, ally, "none" end
if (snap.healthPct or 1) < 0.6 then return 0.75, nil, "none" end
return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["enchantress_impetus"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.manaPct or 1) < 0.3 then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.85, t, "unit" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.6, t, "unit" end
return 0, nil, "none"
""",
  },
  "limitations": "Enchant 魅惑野怪时只能取最近的一只敌方野怪, 没有野怪种类信息, 无法优先挑带控制/光环的野怪。",
},
"grimstroke": {
  "abilities": {"Q": "grimstroke_dark_artistry", "W": "grimstroke_ink_creature", "E": "grimstroke_spirit_walk", "R": "grimstroke_soul_chain"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_aether_lens", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_scythe_of_vyse", "item_refresher_orb", "item_shivas_guard", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_arcane_boots", "item_aether_lens", "item_euls_scepter_of_divinity", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_scythe_of_vyse", "item_kaya_and_sange"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_black_king_bar", "item_aghanims_scepter", "item_pipe_of_insight"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_euls_scepter_of_divinity"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_aghanims_scepter", "item_euls_scepter_of_divinity", "item_ghost_scepter", "item_black_king_bar"],
  },
  "consider": {
    "Q": """local ab = ab["grimstroke_dark_artistry"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 700)
if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
if n >= 1 and (snap.manaPct or 1) > 0.5 then return 0.55, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
    "W": """local ab = ab["grimstroke_ink_creature"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.8, t, "unit" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.65, t, "unit" end
return 0, nil, "none"
""",
    "E": """local ab = ab["grimstroke_spirit_walk"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 500)
if n >= 2 then
  local ally = Skill.LowestHpAlly(snap)
  if ally ~= nil then return 0.75, ally, "unit" end
end
return 0, nil, "none"
""",
    "R": """local ab = ab["grimstroke_soul_chain"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 then
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil then return 0.9, t, "unit" end
end
return 0, nil, "none"
""",
  },
},
"gyrocopter": {
  "abilities": {"Q": "gyrocopter_rocket_barrage", "W": "gyrocopter_homing_missile", "E": "gyrocopter_flak_cannon", "R": "gyrocopter_call_down"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_maelstrom", "item_black_king_bar", "item_mjollnir", "item_satanic", "item_butterfly", "item_daedalus", "item_aghanims_scepter", "item_monkey_king_bar", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_maelstrom", "item_black_king_bar", "item_aghanims_scepter", "item_mjollnir", "item_satanic", "item_daedalus", "item_butterfly"],
    3: ["item_tango", "item_flask", "item_wraith_band", "item_phase_boots", "item_maelstrom", "item_black_king_bar", "item_mjollnir", "item_satanic", "item_assault", "item_heart", "item_aghanims_scepter", "item_butterfly"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_maelstrom", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_aghanims_shard"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_maelstrom"],
  },
  "consider": {
    "Q": """local ab = ab["gyrocopter_rocket_barrage"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 400)
if n >= 2 and (snap.healthPct or 1) > 0.35 then return 0.85, snap.nearestEnemy, "none" end
if n >= 1 and (snap.healthPct or 1) > 0.5 then return 0.7, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
    "W": """local ab = ab["gyrocopter_homing_missile"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 then return 0.8, t, "unit" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 then return 0.6, t, "unit" end
return 0, nil, "none"
""",
    "E": """local ab = ab["gyrocopter_flak_cannon"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 then return 0.7, snap.nearestEnemy, "none" end
if n >= 1 and (snap.manaPct or 1) > 0.5 then return 0.55, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
    "R": """local ab = ab["gyrocopter_call_down"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
if n >= 2 and (snap.manaPct or 1) > 0.3 then return 0.9, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
  },
},
"hoodwink": {
  "abilities": {"Q": "hoodwink_acorn_shot", "W": "hoodwink_bushwhack", "E": "hoodwink_scurry", "R": "hoodwink_sharpshooter"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_wraith_band", "item_power_treads", "item_maelstrom", "item_black_king_bar", "item_mjollnir", "item_daedalus", "item_butterfly", "item_aghanims_scepter", "item_manta", "item_monkey_king_bar"],
    2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_maelstrom", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_mjollnir"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_maelstrom", "item_black_king_bar", "item_assault", "item_heart", "item_aghanims_scepter", "item_lotus_orb", "item_shivas_guard", "item_blink"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_aether_lens", "item_aghanims_scepter", "item_lotus_orb", "item_euls_scepter_of_divinity", "item_blink", "item_ghost_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens"],
  },
  "consider": {
    "Q": """local ab = ab["hoodwink_acorn_shot"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.75, t, "unit" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.6, t, "unit" end
return 0, nil, "none"
""",
    "W": """local ab = ab["hoodwink_bushwhack"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 500)
if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
if n >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 then return 0.6, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["hoodwink_sharpshooter"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.healthPct or 1) < 0.4 then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 1200 then return 0.85, t, "location" end
if (snap.numEnemies or 0) >= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 1000 then return 0.7, t, "location" end
return 0, nil, "none"
""",
  },
},
"io": {
  "abilities": {"Q": "wisp_tether", "W": "wisp_spirits", "E": "wisp_overcharge", "R": "wisp_relocate"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_mechanism", "item_pipe_of_insight", "item_lotus_orb", "item_black_king_bar", "item_aghanims_scepter", "item_heart", "item_assault", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_mechanism", "item_pipe_of_insight", "item_lotus_orb", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_heart"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_mechanism", "item_pipe_of_insight", "item_lotus_orb", "item_black_king_bar", "item_heart", "item_aghanims_scepter", "item_assault", "item_shivas_guard"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_mechanism", "item_force_staff", "item_glimmer_cape", "item_lotus_orb"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_mechanism", "item_pipe_of_insight", "item_lotus_orb", "item_force_staff", "item_glimmer_cape", "item_aghanims_scepter", "item_black_king_bar"],
  },
  "consider": {
    "Q": """local ab = ab["wisp_tether"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local ally, pct = Skill.LowestHpAllyPct(snap)
if ally ~= nil and pct < 0.7 and (snap.numEnemies or 0) >= 1 then return 0.85, ally, "unit" end
if ally ~= nil and pct < 0.5 then return 0.75, ally, "unit" end
if ally ~= nil and (snap.healthPct or 1) < 0.5 then return 0.7, ally, "unit" end
return 0, nil, "none"
""",
    "W": """local ab = ab["wisp_spirits"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 then return 0.85, snap.nearestEnemy, "none" end
if n >= 1 then return 0.7, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
    "E": """local ab = ab["wisp_overcharge"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local ally, pct = Skill.LowestHpAllyPct(snap)
if ally ~= nil and pct < 0.5 and (snap.numEnemies or 0) >= 1 then return 0.9, nil, "none" end
if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 1 then return 0.8, nil, "none" end
return 0, nil, "none"
""",
    "R": """local ab = ab["wisp_relocate"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local ally, pct = Skill.LowestHpAllyPct(snap)
if ally ~= nil and pct < 0.25 and (snap.numEnemies or 0) >= 2 then return 0.95, ally, "location" end
if (snap.healthPct or 1) < 0.2 and (snap.numEnemies or 0) >= 2 then return 0.9, bot, "location" end
return 0, nil, "none"
""",
  },
  "limitations": "Relocate 的真实落点(泉水/安全点)无法用允许的 API 表达, R 的 Consider 只管放大的时机(队友残血且敌方人数占优时带人撤离), 落点交给引擎处理。",
},
"jakiro": {
  "abilities": {"Q": "jakiro_dual_breath", "W": "jakiro_ice_path", "E": "jakiro_liquid_fire", "R": "jakiro_macropyre"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_aether_lens", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_shivas_guard", "item_scythe_of_vyse", "item_refresher_orb", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_arcane_boots", "item_aether_lens", "item_euls_scepter_of_divinity", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_kaya_and_sange", "item_scythe_of_vyse"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_aether_lens", "item_shivas_guard", "item_pipe_of_insight", "item_black_king_bar", "item_aghanims_scepter", "item_lotus_orb"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_euls_scepter_of_divinity"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_aghanims_scepter", "item_euls_scepter_of_divinity", "item_ghost_scepter", "item_black_king_bar"],
  },
  "consider": {
    "Q": """local ab = ab["jakiro_dual_breath"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 700)
if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
if n >= 1 and (snap.manaPct or 1) > 0.5 then return 0.55, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
    "W": """local ab = ab["jakiro_ice_path"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "location" end
return 0, nil, "none"
""",
    "E": """local ab = ab["jakiro_liquid_fire"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.75, t, "unit" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.6, t, "unit" end
return 0, nil, "none"
""",
    "R": """local ab = ab["jakiro_macropyre"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 700)
if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
if n >= 2 and (snap.manaPct or 1) > 0.3 then return 0.95, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
  },
},
"juggernaut": {
  "abilities": {"Q": "juggernaut_blade_fury", "W": "juggernaut_healing_ward", "E": "juggernaut_blade_dance", "R": "juggernaut_omni_slash"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_battle_fury", "item_manta", "item_black_king_bar", "item_abyssal_blade", "item_satanic", "item_butterfly", "item_aghanims_scepter", "item_daedalus", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_battle_fury", "item_manta", "item_black_king_bar", "item_abyssal_blade", "item_satanic", "item_butterfly", "item_monkey_king_bar"],
    3: ["item_tango", "item_flask", "item_wraith_band", "item_phase_boots", "item_battle_fury", "item_manta", "item_black_king_bar", "item_abyssal_blade", "item_assault", "item_heart", "item_satanic", "item_aghanims_scepter"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_battle_fury", "item_force_staff", "item_glimmer_cape", "item_black_king_bar", "item_manta"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_battle_fury"],
  },
  "consider": {
    "Q": """local ab = ab["juggernaut_blade_fury"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 400)
if n >= 1 and (snap.healthPct or 1) < 0.6 then return 0.85, snap.nearestEnemy, "none" end
if n >= 2 and (snap.healthPct or 1) > 0.5 then return 0.8, snap.nearestEnemy, "none" end
if n >= 1 and (snap.healthPct or 1) > 0.6 then return 0.6, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
    "W": """local ab = ab["juggernaut_healing_ward"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.numEnemies or 0) > 0 then return 0, nil, "none" end
local ally, pct = Skill.LowestHpAllyPct(snap)
if ally ~= nil and pct < 0.6 then return 0.75, nil, "none" end
if (snap.healthPct or 1) < 0.5 then return 0.7, nil, "none" end
return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["juggernaut_omni_slash"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.healthPct or 1) < 0.35 then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
local pct = Skill.HpPctOf(t)
if pct > 0 and pct < 0.3 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 1.0, t, "unit" end
if pct > 0 and pct < 0.5 and (snap.numEnemies or 0) <= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.9, t, "unit" end
return 0, nil, "none"
""",
  },
},
"keeper_of_the_light": {
  "abilities": {"Q": "keeper_of_the_light_illuminate", "W": "keeper_of_the_light_mana_leak", "E": "keeper_of_the_light_chakra_magic", "R": "keeper_of_the_light_spirit_form"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_aether_lens", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_shivas_guard", "item_scythe_of_vyse", "item_refresher_orb", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_arcane_boots", "item_aether_lens", "item_euls_scepter_of_divinity", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_kaya_and_sange", "item_scythe_of_vyse"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_aether_lens", "item_shivas_guard", "item_pipe_of_insight", "item_black_king_bar", "item_aghanims_scepter", "item_lotus_orb"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_aghanims_scepter"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_aghanims_scepter", "item_euls_scepter_of_divinity", "item_ghost_scepter", "item_black_king_bar"],
  },
  "consider": {
    "Q": """local ab = ab["keeper_of_the_light_illuminate"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.healthPct or 1) < 0.5 then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 800)
if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
if n >= 1 and (snap.manaPct or 1) > 0.5 then return 0.5, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
    "W": """local ab = ab["keeper_of_the_light_mana_leak"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.6 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist > 300 and snap.nearestEnemyDist <= 800 then return 0.65, t, "unit" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.55, t, "unit" end
return 0, nil, "none"
""",
    "E": """local ab = ab["keeper_of_the_light_chakra_magic"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.manaPct or 1) < 0.3 then return 0.8, bot, "unit" end
local ally = Skill.LowestHpAlly(snap)
if ally ~= nil and (snap.numEnemies or 0) >= 1 then return 0.55, ally, "unit" end
return 0, nil, "none"
""",
    "R": """local ab = ab["keeper_of_the_light_spirit_form"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 then return 0.85, snap.nearestEnemy, "none" end
if n >= 1 and (snap.manaPct or 1) < 0.6 then return 0.8, snap.nearestEnemy, "none" end
return 0, nil, "none"
""",
  },
  "limitations": "reference 注明 spirit_form 是 Ability6(大招槽), Recall/Blinding Light 是其子技能, 本文件只写 Spirit Form 本体的变身时机, 不建模子技能。",
},
"kunkka": {
  "abilities": {"Q": "kunkka_torrent", "W": "kunkka_tidebringer", "E": "kunkka_x_marks_the_spot", "R": "kunkka_ghostship"},
  "talents": {10: 0, 15: 1, 20: 0, 25: 1},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_armlet", "item_black_king_bar", "item_daedalus", "item_assault", "item_heart", "item_satanic", "item_aghanims_scepter", "item_harpoon", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_power_treads", "item_armlet", "item_black_king_bar", "item_daedalus", "item_aghanims_scepter", "item_assault", "item_harpoon", "item_octarine_core", "item_satanic", "item_travel_boots"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_armlet", "item_black_king_bar", "item_daedalus", "item_blink", "item_assault", "item_heart", "item_aghanims_scepter", "item_shivas_guard"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_armlet", "item_blink", "item_black_king_bar", "item_force_staff", "item_aghanims_shard"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_armlet"],
  },
  "consider": {
    "Q": """local ab = ab["kunkka_torrent"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.7, t, "location" end
return 0, nil, "none"
""",
    "W": """return 0, nil, "none"
""",
    "E": """local ab = ab["kunkka_x_marks_the_spot"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.9, t, "unit" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.7, t, "unit" end
return 0, nil, "none"
""",
    "R": """local ab = ab["kunkka_ghostship"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
if (snap.healthPct or 1) < 0.4 then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 700)
if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
if n >= 2 then return 0.95, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
  },
},
"legion_commander": {
  "abilities": {"Q": "legion_commander_overwhelming_odds", "W": "legion_commander_press_the_attack", "E": "legion_commander_moment_of_courage", "R": "legion_commander_duel"},
  "talents": {10: 1, 15: 0, 20: 1, 25: 0},
  "items": {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_phase_boots", "item_blink", "item_blade_mail", "item_black_king_bar", "item_assault", "item_heart", "item_satanic", "item_abyssal_blade", "item_aghanims_scepter", "item_travel_boots"],
    2: ["item_tango", "item_flask", "item_bottle", "item_bracer", "item_phase_boots", "item_blink", "item_blade_mail", "item_black_king_bar", "item_desolator", "item_assault", "item_satanic", "item_abyssal_blade"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_blade_mail", "item_black_king_bar", "item_assault", "item_heart", "item_aghanims_shard", "item_satanic", "item_abyssal_blade", "item_lotus_orb", "item_travel_boots"],
    4: ["item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_blink", "item_blade_mail", "item_force_staff", "item_glimmer_cape", "item_black_king_bar"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_blink"],
  },
  "consider": {
    "Q": """local ab = ab["legion_commander_overwhelming_odds"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
if n >= 1 and (snap.healthPct or 1) < 0.7 then return 0.6, snap.nearestEnemy, "location" end
return 0, nil, "none"
""",
    "W": """local ab = ab["legion_commander_press_the_attack"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local ally, pct = Skill.LowestHpAllyPct(snap)
if ally ~= nil and pct < 0.4 and (snap.numEnemies or 0) >= 1 then return 1.0, ally, "unit" end
if ally ~= nil and pct < 0.6 and (snap.numEnemies or 0) >= 1 then return 0.85, ally, "unit" end
if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 1 then return 0.85, bot, "unit" end
return 0, nil, "none"
""",
    "E": """return 0, nil, "none"
""",
    "R": """local ab = ab["legion_commander_duel"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.healthPct or 1) < 0.45 then return 0, nil, "none" end
if (snap.numEnemies or 0) >= 3 then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
local pct = Skill.HpPctOf(t)
if pct > 0 and pct < 0.5 and (snap.numAllies or 0) >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.95, t, "unit" end
if pct > 0 and pct < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.9, t, "unit" end
return 0, nil, "none"
""",
  },
},
}
