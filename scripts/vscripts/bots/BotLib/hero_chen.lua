-- hero_chen.lua -- Chen 陈 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- v3.0.0: 127 个英雄全部有真实 Consider 逻辑 (见 tools/all_heroes.py);
-- fallback 只作兜底: SkillsComplement 全返回 0 时 ability_item_usage wrapper 才走
-- Micro.TryCastByType, 触发率目标为 0。
-- 限制: Chen 无独立召唤物微操: Holy Persuasion 只在开局 180 秒内或无敌方英雄在场且附近有野怪时劝化, 且只取 nearbyEnemyCreeps 的第一只, 不挑选野怪种类、不控制劝化后的野怪。另参考文件注明 hand_of_god 是 Ability5, Q/W/E/R 映射按给定文件原样使用。Test of Faith 按救援队友(传送残血队友)的理解写, 若该技能现行机制不同, 此段需按实测修正。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "chen"
X.TALENTS = { [10] = 1, [15] = 0, [20] = 0, [25] = 1 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 1, 4, 2, 3, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_hand_of_midas", "item_black_king_bar", "item_manta", "item_butterfly", "item_satanic", "item_abyssal_blade", "item_aghanims_scepter", "item_travel_boots", "item_monkey_king_bar"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_hand_of_midas", "item_aether_lens", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_bloodstone"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_hand_of_midas", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_pipe_of_insight", "item_shivas_guard", "item_lotus_orb", "item_aeon_disk"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_hand_of_midas", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_aghanims_scepter", "item_pipe_of_insight"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_hand_of_midas", "item_aghanims_scepter", "item_pipe_of_insight", "item_force_staff", "item_glimmer_cape", "item_lotus_orb", "item_meteor_hammer"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "chen_penitence", W = "chen_test_of_faith", E = "chen_holy_persuasion", R = "chen_hand_of_god" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["chen_penitence"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    if Skill.HpPctOf(t) < 0.4 then return 0.8, t, "unit" end
    return 0.65, t, "unit"
  end
  return 0, nil, "none"

end
function X.ConsiderW(bot, snap, ab)
local ab = ab["chen_test_of_faith"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.4 then return 0.9, ally, "unit" end
  if ally ~= nil and pct < 0.6 and (snap.numEnemies or 0) >= 2 then return 0.8, ally, "unit" end
  return 0, nil, "none"

end
function X.ConsiderE(bot, snap, ab)
local ab = ab["chen_holy_persuasion"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.time or 0) < 180 and #snap.nearbyEnemyCreeps > 0 then return 0.8, snap.nearbyEnemyCreeps[1], "unit" end
  if (snap.numEnemies or 0) == 0 and #snap.nearbyEnemyCreeps > 0 then return 0.6, snap.nearbyEnemyCreeps[1], "unit" end
  return 0, nil, "none"

end
function X.ConsiderR(bot, snap, ab)
local ab = ab["chen_hand_of_god"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.35 then return 1.0, nil, "none" end
  if (snap.healthPct or 1) < 0.4 then return 0.9, nil, "none" end
  if ally ~= nil and pct < 0.5 and (snap.numEnemies or 0) >= 2 then return 0.85, nil, "none" end
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
