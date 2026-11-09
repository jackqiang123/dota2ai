-- hero_clinkz.lua -- Clinkz 克林克兹 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- v3.0.0: 127 个英雄全部有真实 Consider 逻辑 (见 tools/all_heroes.py);
-- fallback 只作兜底: SkillsComplement 全返回 0 时 ability_item_usage wrapper 才走
-- Micro.TryCastByType, 触发率目标为 0。
-- 限制: v3.0 已订正: E 为 clinkz_skeleton_walk(骷髅漫步)。Death Pact 只取附近第一只野怪, 不挑野怪种类。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "clinkz"
X.TALENTS = { [10] = 0, [15] = 1, [20] = 0, [25] = 0 }
X.SKILL_BUILD = {2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 4, 1, 3, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_desolator", "item_black_king_bar", "item_daedalus", "item_butterfly", "item_satanic", "item_monkey_king_bar", "item_abyssal_blade", "item_aghanims_scepter", "item_travel_boots"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_desolator", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_daedalus", "item_aghanims_scepter", "item_nullifier"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_desolator", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_daedalus", "item_aghanims_scepter", "item_lotus_orb"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_desolator", "item_force_staff", "item_glimmer_cape", "item_solar_crest", "item_black_king_bar", "item_aghanims_scepter"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_desolator", "item_lotus_orb"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "clinkz_strafe", W = "clinkz_searing_arrows", E = "clinkz_skeleton_walk", R = "clinkz_death_pact" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["clinkz_strafe"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    if Skill.HpPctOf(t) < 0.35 then return 0.85, nil, "none" end
    return 0.75, nil, "none"
  end
  return 0, nil, "none"

end
function X.ConsiderW(bot, snap, ab)
local ab = ab["clinkz_searing_arrows"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and (snap.manaPct or 1) > 0.3 then return 0.65, t, "unit" end
  return 0, nil, "none"

end
function X.ConsiderE(bot, snap, ab)
local ab = ab["clinkz_skeleton_walk"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.9, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.6 then return 0.6, nil, "none" end
  return 0, nil, "none"

end
function X.ConsiderR(bot, snap, ab)
local ab = ab["clinkz_death_pact"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) > 0.5 and #snap.nearbyEnemyCreeps > 0 then return 0.7, snap.nearbyEnemyCreeps[1], "unit" end
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
