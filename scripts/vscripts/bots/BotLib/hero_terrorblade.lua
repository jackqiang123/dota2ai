-- hero_terrorblade.lua -- Terrorblade 恐怖利刃 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- v3.0.0: 127 个英雄全部有真实 Consider 逻辑 (见 tools/all_heroes.py);
-- fallback 只作兜底: SkillsComplement 全返回 0 时 ability_item_usage wrapper 才走
-- Micro.TryCastByType, 触发率目标为 0。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "terrorblade"
X.TALENTS = { [10] = 0, [15] = 1, [20] = 0, [25] = 1 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 1, 4, 2, 3, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_manta", "item_black_king_bar", "item_butterfly", "item_satanic", "item_skadi", "item_abyssal_blade", "item_aghanims_scepter", "item_travel_boots", "item_moon_shard"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_manta", "item_black_king_bar", "item_butterfly", "item_satanic", "item_skadi", "item_aghanims_scepter", "item_travel_boots"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_manta", "item_black_king_bar", "item_butterfly", "item_assault", "item_heart", "item_satanic", "item_aghanims_scepter"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_manta", "item_black_king_bar", "item_butterfly", "item_force_staff", "item_lotus_orb"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_power_treads", "item_manta", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_solar_crest"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "terrorblade_reflection", W = "terrorblade_conjure_image", E = "terrorblade_metamorphosis", R = "terrorblade_sunder" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["terrorblade_reflection"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  local t = Skill.LowestHpEnemy(snap)
  if n >= 2 and t ~= nil then return 0.85, t, "unit" end
  if n >= 1 and t ~= nil then return 0.7, t, "unit" end
  return 0, nil, "none"

end
function X.ConsiderW(bot, snap, ab)
local ab = ab["terrorblade_conjure_image"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.3 then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.5 then return 0.65, nil, "none" end
  if (snap.numEnemies or 0) == 0 and (snap.healthPct or 1) > 0.7 then return 0.55, nil, "none" end
  return 0, nil, "none"

end
function X.ConsiderE(bot, snap, ab)
local ab = ab["terrorblade_metamorphosis"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 and (snap.healthPct or 1) > 0.4 then return 0.95, nil, "none" end
  if n >= 1 and (snap.healthPct or 1) > 0.4 then return 0.85, nil, "none" end
  return 0, nil, "none"

end
function X.ConsiderR(bot, snap, ab)
local ab = ab["terrorblade_sunder"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.3 and Skill.HpPctOf(t) > 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 1.0, t, "unit" end
  if Skill.HpPctOf(t) < 0.25 and (snap.healthPct or 1) > 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.9, t, "unit" end
  if (snap.healthPct or 1) < 0.4 and Skill.HpPctOf(t) > 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 500 then return 0.85, t, "unit" end
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
