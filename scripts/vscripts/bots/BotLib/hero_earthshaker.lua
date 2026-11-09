-- hero_earthshaker.lua -- Earthshaker 撼地者 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- v3.0.0: 127 个英雄全部有真实 Consider 逻辑 (见 tools/all_heroes.py);
-- fallback 只作兜底: SkillsComplement 全返回 0 时 ability_item_usage wrapper 才走
-- Micro.TryCastByType, 触发率目标为 0。
-- 限制: 回响击的跳刀先手无法用允许的 API 直接检测是否持有跳刀, 这里用最近敌人距离 <=600 作为已经切入的代理条件; 若跳刀在冷却而人已在圈内, 该条件仍会放行。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "earthshaker"
X.TALENTS = { [10] = 1, [15] = 0, [20] = 1, [25] = 0 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 1, 4, 2, 3, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_assault", "item_heart", "item_shivas_guard", "item_overwhelming_blink", "item_travel_boots"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_bottle", "item_bracer", "item_arcane_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_refresher_orb", "item_octarine_core", "item_shivas_guard", "item_scythe_of_vyse"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_lotus_orb", "item_heart", "item_assault", "item_aeon_disk"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_force_staff", "item_glimmer_cape", "item_lotus_orb", "item_aether_lens", "item_euls_scepter_of_divinity", "item_refresher_orb"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_blink", "item_aether_lens", "item_aghanims_shard"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "earthshaker_fissure", W = "earthshaker_enchant_totem", E = "earthshaker_aftershock", R = "earthshaker_echo_slam" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["earthshaker_fissure"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 700)
if n >= 2 then return 0.85, snap.nearestEnemy, "location" end
if (snap.healthPct or 1) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 400 then return 0.8, snap.nearestEnemy, "location" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.7, t, "location" end
return 0, nil, "none"

end
function X.ConsiderW(bot, snap, ab)
local ab = ab["earthshaker_enchant_totem"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 500)
if n >= 2 and (snap.healthPct or 1) > 0.4 then return 0.8, snap.nearestEnemy, "none" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 300 and (snap.healthPct or 1) > 0.4 then return 0.7, snap.nearestEnemy, "none" end
return 0, nil, "none"

end
function X.ConsiderE(bot, snap, ab)
return 0, nil, "none"

end
function X.ConsiderR(bot, snap, ab)
local ab = ab["earthshaker_echo_slam"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
local w = Team.GetComboWindow()
if w ~= nil then return 0, nil, "none" end
if (snap.healthPct or 1) < 0.35 then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 400)
if n >= 3 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 1.0, snap.nearestEnemy, "none" end
if n >= 2 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.9, snap.nearestEnemy, "none" end
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
