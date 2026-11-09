-- hero_invoker.lua -- Invoker 祈求者 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- v3.0.0: 127 个英雄全部有真实 Consider 逻辑 (见 tools/all_heroes.py);
-- fallback 只作兜底: SkillsComplement 全返回 0 时 ability_item_usage wrapper 才走
-- Micro.TryCastByType, 触发率目标为 0。
-- 限制: Invoke 机制：当已有 invoked 技能可用时不急着按 Invoke，R 的 Consider 因此只做可用性检查、不主动触发；球（Quas/Wex/Exort）是被动球、Q/W/E 的 Consider 只返回 0。本表只建模 8 个常用 invoked 技能，alacrity / ice_wall 未建模；锻造之灵无独立微操。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "invoker"
X.TALENTS = { [10] = 0, [15] = 1, [20] = 0, [25] = 1 }
X.SKILL_BUILD = {1, 4, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 4, 4, 2}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_hand_of_midas", "item_black_king_bar", "item_assault", "item_heart", "item_satanic", "item_butterfly", "item_travel_boots"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_scythe_of_vyse", "item_refresher_orb", "item_kaya_and_sange", "item_blink", "item_travel_boots", "item_aeon_disk", "item_bloodstone"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_vanguard", "item_pipe_of_insight", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_heart", "item_lotus_orb"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_force_staff", "item_glimmer_cape", "item_euls_scepter_of_divinity", "item_blink", "item_octarine_core"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_meteor_hammer", "item_aether_lens"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "invoker_quas", W = "invoker_wex", E = "invoker_exort", R = "invoker_invoke" }
function X.ConsiderQ(bot, snap, ab)
return 0, nil, "none"
end
function X.ConsiderW(bot, snap, ab)
return 0, nil, "none"
end
function X.ConsiderE(bot, snap, ab)
return 0, nil, "none"
end
function X.ConsiderR(bot, snap, ab)
local ab = ab["invoker_invoke"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  return 0, nil, "none"
end
-- Invoker: 球 Quas/Wex/Exort 为被动, 不施放; Invoke(R) 只检查可用性。
-- 调用技能按球组合生成, 每次最多持有 2 个; 本表建模 8 个常用 invoked 技能。
function X.ConsiderInvokerChaosMeteor(bot, snap, ab)
local ab = ab["invoker_chaos_meteor"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 3 then return 0.95, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  return 0, nil, "none"
end
function X.ConsiderInvokerColdSnap(bot, snap, ab)
local ab = ab["invoker_cold_snap"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.6 and (snap.numAllies or 0) >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.85, t, "unit" end
  if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.7, t, "unit" end
  return 0, nil, "none"
end
function X.ConsiderInvokerDeafeningBlast(bot, snap, ab)
local ab = ab["invoker_deafening_blast"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 and (snap.healthPct or 1) < 0.5 then return 0.9, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  return 0, nil, "none"
end
function X.ConsiderInvokerEmp(bot, snap, ab)
local ab = ab["invoker_emp"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 3 then return 0.95, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  return 0, nil, "none"
end
function X.ConsiderInvokerForgeSpirit(bot, snap, ab)
local ab = ab["invoker_forge_spirit"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.numAllies or 0) >= 1 then return 0.6, snap.nearestEnemy, "none" end
  if (snap.numEnemies or 0) == 0 and #snap.nearbyEnemyCreeps > 0 then return 0.55, snap.nearestEnemy, "none" end
  return 0, nil, "none"
end
function X.ConsiderInvokerGhostWalk(bot, snap, ab)
local ab = ab["invoker_ghost_walk"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 1.0, nil, "none" end
  if (snap.healthPct or 1) < 0.5 and (snap.numEnemies or 0) >= 2 then return 0.85, nil, "none" end
  return 0, nil, "none"
end
function X.ConsiderInvokerSunStrike(bot, snap, ab)
local ab = ab["invoker_sun_strike"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.25 then return 0.95, t, "location" end
  if pct > 0 and pct < 0.4 and (snap.numAllies or 0) >= 1 then return 0.8, t, "location" end
  return 0, nil, "none"
end
function X.ConsiderInvokerTornado(bot, snap, ab)
local ab = ab["invoker_tornado"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 800)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
  return 0, nil, "none"
end
X.INVOKED = {"invoker_chaos_meteor", "invoker_cold_snap", "invoker_deafening_blast", "invoker_emp", "invoker_forge_spirit", "invoker_ghost_walk", "invoker_sun_strike", "invoker_tornado"}
function X.SkillsComplement(bot, snap)
  if bot == nil or snap == nil then return false end
  local ab = Skill.GetAbilityMap(bot)
  do
    local fn = X["ConsiderInvokerChaosMeteor"]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local ability = ab["invoker_chaos_meteor"]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          return true
        end
      end
    end
  end
  do
    local fn = X["ConsiderInvokerColdSnap"]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local ability = ab["invoker_cold_snap"]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          return true
        end
      end
    end
  end
  do
    local fn = X["ConsiderInvokerDeafeningBlast"]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local ability = ab["invoker_deafening_blast"]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          return true
        end
      end
    end
  end
  do
    local fn = X["ConsiderInvokerEmp"]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local ability = ab["invoker_emp"]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          return true
        end
      end
    end
  end
  do
    local fn = X["ConsiderInvokerForgeSpirit"]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local ability = ab["invoker_forge_spirit"]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          return true
        end
      end
    end
  end
  do
    local fn = X["ConsiderInvokerGhostWalk"]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local ability = ab["invoker_ghost_walk"]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          return true
        end
      end
    end
  end
  do
    local fn = X["ConsiderInvokerSunStrike"]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local ability = ab["invoker_sun_strike"]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          return true
        end
      end
    end
  end
  do
    local fn = X["ConsiderInvokerTornado"]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local ability = ab["invoker_tornado"]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          return true
        end
      end
    end
  end
  do
    local fn = X["ConsiderR"]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local ability = ab[X.ABILITIES["R"]]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          local loc = nil
          if target ~= nil then local ok, l = pcall(function() return target:GetLocation() end) if ok then loc = l end end
          if loc ~= nil then Team.ReportComboWindow(bot, loc) end
          return true
        end
      end
    end
  end
  do
    local fn = X["ConsiderQ"]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local ability = ab[X.ABILITIES["Q"]]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          return true
        end
      end
    end
  end
  do
    local fn = X["ConsiderW"]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local ability = ab[X.ABILITIES["W"]]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          return true
        end
      end
    end
  end
  do
    local fn = X["ConsiderE"]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local ability = ab[X.ABILITIES["E"]]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          return true
        end
      end
    end
  end
  return false
end
return X
