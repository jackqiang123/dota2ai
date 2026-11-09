-- hero_natures_prophet.lua -- Nature's Prophet 自然先知 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- v3.0.0: 127 个英雄全部有真实 Consider 逻辑 (见 tools/all_heroes.py);
-- fallback 只作兜底: SkillsComplement 全返回 0 时 ability_item_usage wrapper 才走
-- Micro.TryCastByType, 触发率目标为 0。
-- 限制: Teleportation has no map-aware destination choice (no global target selection from lane or fight state); treants from Force of Nature use generic summon logic.
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "natures_prophet"
X.TALENTS = { [10] = 0, [15] = 1, [20] = 0, [25] = 0 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 1, 4, 2, 3, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_hand_of_midas", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_hurricane_pike", "item_aghanims_scepter", "item_travel_boots", "item_moon_shard"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_bottle", "item_null_talisman", "item_power_treads", "item_hand_of_midas", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_scythe_of_vyse", "item_travel_boots", "item_aghanims_scepter"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_hand_of_midas", "item_orchid", "item_black_king_bar", "item_bloodthorn", "item_hurricane_pike", "item_aghanims_scepter", "item_scythe_of_vyse", "item_travel_boots", "item_moon_shard", "item_gleipnir"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_power_treads", "item_hand_of_midas", "item_force_staff", "item_black_king_bar", "item_glimmer_cape", "item_orchid", "item_gleipnir"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_hand_of_midas", "item_orchid", "item_gleipnir"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "furion_sprout", W = "furion_teleportation", E = "furion_force_of_nature", R = "furion_wrath_of_nature" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["furion_sprout"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then
    local pct = Skill.HpPctOf(t)
    if pct > 0 and pct < 0.4 then return 0.8, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none"
end
function X.ConsiderW(bot, snap, ab)
local ab = ab["furion_teleportation"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.3 and (snap.numEnemies or 0) >= 1 then return 0.85, snap.location, "location" end
  if (snap.numEnemies or 0) == 0 and snap.nearbyEnemyCreeps ~= nil and #snap.nearbyEnemyCreeps > 0 then return 0.5, snap.location, "location" end
  return 0, nil, "none"
end
function X.ConsiderE(bot, snap, ab)
local ab = ab["furion_force_of_nature"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if snap.nearbyEnemyCreeps ~= nil and #snap.nearbyEnemyCreeps > 0 then return 0.7, snap.nearestEnemy, "location" end
  if (snap.numEnemies or 0) >= 1 then return 0.65, snap.nearestEnemy, "location" end
  return 0, nil, "none"
end
function X.ConsiderR(bot, snap, ab)
local ab = ab["furion_wrath_of_nature"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local low = Skill.CountLowHpEnemies(snap, 0.35)
  if low >= 2 then return 0.95, nil, "none" end
  if low >= 1 then return 0.8, nil, "none" end
  if (snap.numEnemies or 0) >= 1 then return 0.6, nil, "none" end
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
