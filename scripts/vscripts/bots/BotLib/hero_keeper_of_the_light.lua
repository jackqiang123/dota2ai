-- hero_keeper_of_the_light.lua -- Keeper of the Light 光之守卫 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- v3.0.0: 127 个英雄全部有真实 Consider 逻辑 (见 tools/all_heroes.py);
-- fallback 只作兜底: SkillsComplement 全返回 0 时 ability_item_usage wrapper 才走
-- Micro.TryCastByType, 触发率目标为 0。
-- 限制: reference 注明 spirit_form 是 Ability6(大招槽), Recall/Blinding Light 是其子技能, 本文件只写 Spirit Form 本体的变身时机, 不建模子技能。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "keeper_of_the_light"
X.TALENTS = { [10] = 1, [15] = 0, [20] = 1, [25] = 0 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 4, 1, 2, 3, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_aether_lens", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_shivas_guard", "item_scythe_of_vyse", "item_refresher_orb", "item_travel_boots"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_arcane_boots", "item_aether_lens", "item_euls_scepter_of_divinity", "item_aghanims_scepter", "item_black_king_bar", "item_octarine_core", "item_kaya_and_sange", "item_scythe_of_vyse"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_aether_lens", "item_shivas_guard", "item_pipe_of_insight", "item_black_king_bar", "item_aghanims_scepter", "item_lotus_orb"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_aghanims_scepter"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_aether_lens", "item_glimmer_cape", "item_force_staff", "item_aghanims_scepter", "item_euls_scepter_of_divinity", "item_ghost_scepter", "item_black_king_bar"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "keeper_of_the_light_illuminate", W = "keeper_of_the_light_mana_leak", E = "keeper_of_the_light_chakra_magic", R = "keeper_of_the_light_spirit_form" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["keeper_of_the_light_illuminate"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.healthPct or 1) < 0.5 then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 800)
if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
if n >= 1 and (snap.manaPct or 1) > 0.5 then return 0.5, snap.nearestEnemy, "location" end
return 0, nil, "none"

end
function X.ConsiderW(bot, snap, ab)
local ab = ab["keeper_of_the_light_mana_leak"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t == nil then return 0, nil, "none" end
if Skill.HpPctOf(t) < 0.6 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist > 300 and snap.nearestEnemyDist <= 800 then return 0.65, t, "unit" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.55, t, "unit" end
return 0, nil, "none"

end
function X.ConsiderE(bot, snap, ab)
local ab = ab["keeper_of_the_light_chakra_magic"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.manaPct or 1) < 0.3 then return 0.8, bot, "unit" end
local ally = Skill.LowestHpAlly(snap)
if ally ~= nil and (snap.numEnemies or 0) >= 1 then return 0.55, ally, "unit" end
return 0, nil, "none"

end
function X.ConsiderR(bot, snap, ab)
local ab = ab["keeper_of_the_light_spirit_form"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 then return 0.85, snap.nearestEnemy, "none" end
if n >= 1 and (snap.manaPct or 1) < 0.6 then return 0.8, snap.nearestEnemy, "none" end
return 0, nil, "none"

end
function X.SkillsComplement(bot, snap)
  if bot == nil or snap == nil then return false end
  local ab = Skill.GetAbilityMap(bot)
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
