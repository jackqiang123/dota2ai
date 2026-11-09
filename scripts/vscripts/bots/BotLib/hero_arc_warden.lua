-- hero_arc_warden.lua -- Arc Warden 天穹守望者 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
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
X.KEY = "arc_warden"
X.TALENTS = { [10] = 0, [15] = 0, [20] = 1, [25] = 1 }
X.SKILL_BUILD = {1, 3, 2, 1, 3, 4, 2, 1, 3, 2, 1, 4, 3, 2, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_hand_of_midas", "item_maelstrom", "item_manta", "item_hurricane_pike", "item_black_king_bar", "item_butterfly", "item_satanic", "item_mjollnir", "item_travel_boots"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_bottle", "item_wraith_band", "item_power_treads", "item_hand_of_midas", "item_maelstrom", "item_dragon_lance", "item_hurricane_pike", "item_black_king_bar", "item_manta", "item_scythe_of_vyse", "item_mjollnir", "item_travel_boots"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_hand_of_midas", "item_maelstrom", "item_black_king_bar", "item_assault", "item_heart", "item_manta", "item_aghanims_scepter", "item_shivas_guard"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_aether_lens", "item_gleipnir", "item_aghanims_scepter", "item_black_king_bar"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_rod_of_atos", "item_lotus_orb"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "arc_warden_flux", W = "arc_warden_magnetic_field", E = "arc_warden_spark_wraith", R = "arc_warden_tempest_double" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["arc_warden_flux"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if (snap.numEnemies or 0) == 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.85, t, "unit" end
  if (snap.numEnemies or 0) >= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.5, t, "unit" end
  return 0, nil, "none"

end
function X.ConsiderW(bot, snap, ab)
local ab = ab["arc_warden_magnetic_field"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 and (snap.healthPct or 1) < 0.5 then return 0.7, snap.nearestEnemy, "location" end
  return 0, nil, "none"

end
function X.ConsiderE(bot, snap, ab)
local ab = ab["arc_warden_spark_wraith"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.8, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none"

end
function X.ConsiderR(bot, snap, ab)
local ab = ab["arc_warden_tempest_double"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.level or 0) < 6 then return 0, nil, "none" end
  if (snap.numEnemies or 0) >= 2 and (snap.healthPct or 1) > 0.4 then return 0.85, nil, "none" end
  if (snap.numEnemies or 0) >= 1 and (snap.healthPct or 1) > 0.6 then return 0.6, nil, "none" end
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
