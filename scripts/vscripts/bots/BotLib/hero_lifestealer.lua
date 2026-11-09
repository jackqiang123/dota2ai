-- hero_lifestealer.lua -- Lifestealer 噬魂鬼 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- v3.0.0: 127 个英雄全部有真实 Consider 逻辑 (见 tools/all_heroes.py);
-- fallback 只作兜底: SkillsComplement 全返回 0 时 ability_item_usage wrapper 才走
-- Micro.TryCastByType, 触发率目标为 0。
-- 限制: No creep-host choice for Infest: it hides in the nearest allied creep or the lowest-HP ally only, with no pick of the best host; Feast is passive; no control over when to pop out of Infest.
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "lifestealer"
X.TALENTS = { [10] = 0, [15] = 1, [20] = 1, [25] = 0 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 4, 1, 2, 3, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_armlet", "item_desolator", "item_black_king_bar", "item_abyssal_blade", "item_assault", "item_satanic", "item_monkey_king_bar", "item_moon_shard", "item_travel_boots", "item_aghanims_scepter", "item_nullifier"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_quelling_blade", "item_power_treads", "item_armlet", "item_echo_sabre", "item_black_king_bar", "item_desolator", "item_assault", "item_satanic", "item_abyssal_blade", "item_travel_boots"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_armlet", "item_blade_mail", "item_black_king_bar", "item_assault", "item_crimson_guard", "item_heart", "item_aghanims_scepter"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_phase_boots", "item_armlet", "item_force_staff", "item_black_king_bar", "item_desolator", "item_glimmer_cape"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_force_staff", "item_glimmer_cape", "item_armlet", "item_black_king_bar"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "life_stealer_rage", W = "life_stealer_feast", E = "life_stealer_open_wounds", R = "life_stealer_infest" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["life_stealer_rage"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 1 and (snap.healthPct or 1) < 0.6 then return 0.85, nil, "none" end
  if n >= 2 then return 0.8, nil, "none" end
  return 0, nil, "none"
end
function X.ConsiderW(bot, snap, ab)
return 0, nil, "none"
end
function X.ConsiderE(bot, snap, ab)
local ab = ab["life_stealer_open_wounds"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then
    local pct = Skill.HpPctOf(t)
    if pct > 0 and pct < 0.4 then return 0.85, t, "unit" end
    return 0.7, t, "unit"
  end
  return 0, nil, "none"
end
function X.ConsiderR(bot, snap, ab)
local ab = ab["life_stealer_infest"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and snap.nearbyAllyCreeps ~= nil and #snap.nearbyAllyCreeps > 0 then return 0.8, snap.nearbyAllyCreeps[1], "unit" end
  if (snap.healthPct or 1) < 0.3 then
    local ally = Skill.LowestHpAlly(snap)
    if ally ~= nil then return 0.75, ally, "unit" end
  end
  if (snap.healthPct or 1) > 0.7 and (snap.numEnemies or 0) >= 1 then
    local ally2 = Skill.LowestHpAlly(snap)
    if ally2 ~= nil then return 0.55, ally2, "unit" end
  end
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
