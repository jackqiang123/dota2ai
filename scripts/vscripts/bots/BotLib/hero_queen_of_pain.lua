-- hero_queen_of_pain.lua -- Queen of Pain 痛苦女王 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- v3.0.0: 127 个英雄全部有真实 Consider 逻辑 (见 tools/all_heroes.py);
-- fallback 只作兜底: SkillsComplement 全返回 0 时 ability_item_usage wrapper 才走
-- Micro.TryCastByType, 触发率目标为 0。
-- 限制: heroes_data lists the third skill type as passive, but queenofpain_scream_of_pain is an active AoE nuke, so the E Consider is written as active; the heroes_data type tag looks wrong, not the skill name.
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "queen_of_pain"
X.TALENTS = { [10] = 1, [15] = 0, [20] = 1, [25] = 0 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 1, 4, 2, 3, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_scythe_of_vyse", "item_satanic", "item_travel_boots"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_aghanims_scepter", "item_octarine_core", "item_scythe_of_vyse", "item_kaya_and_sange", "item_travel_boots"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_null_talisman", "item_phase_boots", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_shivas_guard", "item_aghanims_scepter", "item_lotus_orb"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_null_talisman", "item_magic_wand", "item_arcane_boots", "item_orchid", "item_force_staff", "item_black_king_bar", "item_aether_lens", "item_aghanims_scepter"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_orchid", "item_aether_lens"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "queenofpain_shadow_strike", W = "queenofpain_blink", E = "queenofpain_scream_of_pain", R = "queenofpain_sonic_wave" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["queenofpain_shadow_strike"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 and Skill.HpPctOf(t) < 0.4 then return 0.85, t, "unit" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.65, t, "unit" end
  return 0, nil, "none"

end
function X.ConsiderW(bot, snap, ab)
local ab = ab["queenofpain_blink"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 600 and snap.nearestEnemyDist <= 1200 and Skill.HpPctOf(t) < 0.4 then return 0.85, snap.nearestEnemy, "location" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then
    local ally = Skill.LowestHpAlly(snap)
    if ally ~= nil then return 0.9, ally, "location" end
  end
  return 0, nil, "none"

end
function X.ConsiderE(bot, snap, ab)
local ab = ab["queenofpain_scream_of_pain"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.85, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and n >= 1 and Skill.HpPctOf(t) < 0.4 then return 0.75, nil, "none" end
  if n >= 1 then return 0.6, nil, "none" end
  return 0, nil, "none"

end
function X.ConsiderR(bot, snap, ab)
local ab = ab["queenofpain_sonic_wave"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  local low = Skill.CountLowHpEnemies(snap, 0.35)
  if low >= 1 and n >= 1 then return 0.85, snap.nearestEnemy, "location" end
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
