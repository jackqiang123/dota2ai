-- hero_dark_seer.lua -- Dark Seer 黑暗贤者 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
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
X.KEY = "dark_seer"
X.TALENTS = { [10] = 0, [15] = 1, [20] = 1, [25] = 0 }
X.SKILL_BUILD = {2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 4, 1, 3, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_bracer", "item_power_treads", "item_blink", "item_black_king_bar", "item_assault", "item_heart", "item_shivas_guard", "item_aghanims_scepter", "item_manta", "item_travel_boots", "item_octarine_core"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_blink", "item_aether_lens", "item_black_king_bar", "item_kaya_and_sange", "item_aghanims_scepter", "item_octarine_core", "item_shivas_guard"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_arcane_boots", "item_blink", "item_pipe_of_insight", "item_shivas_guard", "item_black_king_bar", "item_aghanims_scepter", "item_lotus_orb", "item_octarine_core", "item_aeon_disk", "item_travel_boots", "item_heart"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_blink", "item_force_staff", "item_glimmer_cape", "item_pipe_of_insight", "item_aghanims_scepter", "item_black_king_bar"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_medallion_of_courage", "item_pipe_of_insight", "item_lotus_orb"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "dark_seer_vacuum", W = "dark_seer_ion_shell", E = "dark_seer_surge", R = "dark_seer_wall_of_replica" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["dark_seer_vacuum"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"

end
function X.ConsiderW(bot, snap, ab)
local ab = ab["dark_seer_ion_shell"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally = Skill.LowestHpAlly(snap)
  if ally ~= nil then return 0.7, ally, "unit" end
  if #snap.nearbyAllyCreeps > 0 then return 0.6, snap.nearbyAllyCreeps[1], "unit" end
  if (snap.healthPct or 1) > 0.5 then return 0.55, bot, "unit" end
  return 0, nil, "none"

end
function X.ConsiderE(bot, snap, ab)
local ab = ab["dark_seer_surge"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally, pct = Skill.LowestHpAllyPct(snap)
  if ally ~= nil and pct < 0.5 then return 0.85, ally, "unit" end
  if (snap.healthPct or 1) < 0.4 then return 0.8, bot, "unit" end
  if ally ~= nil and (snap.numEnemies or 0) >= 2 then return 0.6, ally, "unit" end
  return 0, nil, "none"

end
function X.ConsiderR(bot, snap, ab)
local ab = ab["dark_seer_wall_of_replica"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  if n >= 3 then return 1.0, snap.nearestEnemy, "location" end
  if n >= 2 then return 0.9, snap.nearestEnemy, "location" end
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
