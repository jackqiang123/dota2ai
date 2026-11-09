-- hero_earth_spirit.lua -- Earth Spirit 大地之灵 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- v3.0.0: 127 个英雄全部有真实 Consider 逻辑 (见 tools/all_heroes.py);
-- fallback 只作兜底: SkillsComplement 全返回 0 时 ability_item_usage wrapper 才走
-- Micro.TryCastByType, 触发率目标为 0。
-- 限制: 大地之灵的全部连招都依赖残岩(Stone Remnant)的数量与落点, 但允许的 API 里没有残岩计数/位置字段, 因此 Q/W/R 的时机判断默认残岩够用, 不做残岩约束; 实战中缺残岩时这些 Consider 会高估。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "earth_spirit"
X.TALENTS = { [10] = 0, [15] = 1, [20] = 1, [25] = 0 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 4, 1, 2, 3, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_aghanims_scepter", "item_shivas_guard", "item_blink", "item_octarine_core", "item_heart", "item_travel_boots"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_bottle", "item_bracer", "item_power_treads", "item_euls_scepter_of_divinity", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_octarine_core", "item_shivas_guard", "item_scythe_of_vyse"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_euls_scepter_of_divinity", "item_shivas_guard", "item_aghanims_scepter", "item_lotus_orb", "item_heart", "item_pipe_of_insight"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_blink", "item_euls_scepter_of_divinity", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_aghanims_scepter", "item_lotus_orb", "item_aeon_disk", "item_ghost_scepter"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_tranquil_boots", "item_force_staff", "item_glimmer_cape", "item_euls_scepter_of_divinity"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "earth_spirit_boulder_smash", W = "earth_spirit_rolling_boulder", E = "earth_spirit_geomagnetic_grip", R = "earth_spirit_magnetize" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["earth_spirit_boulder_smash"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 600)
if n >= 2 then return 0.8, snap.nearestEnemy, "unit" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.4 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.75, t, "unit" end
if n >= 1 and (snap.manaPct or 1) > 0.4 then return 0.55, snap.nearestEnemy, "unit" end
return 0, nil, "none"

end
function X.ConsiderW(bot, snap, ab)
local ab = ab["earth_spirit_rolling_boulder"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.manaPct or 1) < 0.4 then return 0, nil, "none" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and Skill.HpPctOf(t) < 0.35 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 900 then return 0.8, t, "location" end
if snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 300 and snap.nearestEnemyDist <= 900 then return 0.7, snap.nearestEnemy, "location" end
return 0, nil, "none"

end
function X.ConsiderE(bot, snap, ab)
local ab = ab["earth_spirit_geomagnetic_grip"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
local ally, pct = Skill.LowestHpAllyPct(snap)
if ally ~= nil and pct < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.85, ally, "unit" end
local t = Skill.LowestHpEnemy(snap)
if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.65, t, "unit" end
return 0, nil, "none"

end
function X.ConsiderR(bot, snap, ab)
local ab = ab["earth_spirit_magnetize"]
if not Skill.IsCastable(ab) then return 0, nil, "none" end
if (snap.manaPct or 1) < 0.35 then return 0, nil, "none" end
local n = Skill.CountEnemiesInRange(snap, 500)
if n >= 2 then return 0.9, snap.nearestEnemy, "none" end
local low = Skill.CountLowHpEnemies(snap, 0.35)
if low >= 1 then return 0.7, snap.nearestEnemy, "none" end
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
