-- hero_shadow_fiend.lua -- Shadow Fiend 影魔 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- v3.0.0: 127 个英雄全部有真实 Consider 逻辑 (见 tools/all_heroes.py);
-- fallback 只作兜底: SkillsComplement 全返回 0 时 ability_item_usage wrapper 才走
-- Micro.TryCastByType, 触发率目标为 0。
-- 限制: Reference Q is only nevermore_shadowraze1 (the near raze); the mid and far razes (shadowraze2 / shadowraze3) have no slot in the reference, so the single Q Consider is distance-segmented (<=250 near 0.9, <=450 mid 0.75, <=700 far 0.6) as the raze entry and the engine must map the other two raze distances separately if it wants true three-raze play.
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "shadow_fiend"
X.TALENTS = { [10] = 0, [15] = 1, [20] = 0, [25] = 1 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 4, 1, 2, 3, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_black_king_bar", "item_daedalus", "item_satanic", "item_butterfly", "item_manta", "item_monkey_king_bar", "item_abyssal_blade", "item_travel_boots", "item_moon_shard"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_wraith_band", "item_bottle", "item_power_treads", "item_black_king_bar", "item_daedalus", "item_satanic", "item_butterfly", "item_manta", "item_aghanims_scepter", "item_scythe_of_vyse", "item_travel_boots", "item_moon_shard"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_black_king_bar", "item_daedalus", "item_satanic", "item_assault", "item_heart", "item_butterfly"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_magic_wand", "item_wraith_band", "item_phase_boots", "item_black_king_bar", "item_daedalus", "item_force_staff", "item_satanic", "item_aghanims_scepter"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_phase_boots", "item_black_king_bar", "item_daedalus", "item_force_staff", "item_glimmer_cape"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "nevermore_shadowraze1", W = "nevermore_necromastery", E = "nevermore_presence_of_the_dark_lord", R = "nevermore_requiem" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["nevermore_shadowraze1"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if snap.nearestEnemy == nil then return 0, nil, "none" end
  local d = snap.nearestEnemyDist
  if d == nil then return 0, nil, "none" end
  if d <= 250 then return 0.9, snap.nearestEnemy, "location" end
  if d <= 450 then return 0.75, snap.nearestEnemy, "location" end
  if d <= 700 then return 0.6, snap.nearestEnemy, "location" end
  return 0, nil, "none"

end
function X.ConsiderW(bot, snap, ab)
return 0, nil, "none"

end
function X.ConsiderE(bot, snap, ab)
return 0, nil, "none"

end
function X.ConsiderR(bot, snap, ab)
local ab = ab["nevermore_requiem"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 3 then return 1.0, nil, "none" end
  if n >= 2 and (snap.healthPct or 1) > 0.5 then return 0.9, nil, "none" end
  local low = Skill.CountLowHpEnemies(snap, 0.35)
  if low >= 1 and n >= 1 then return 0.85, nil, "none" end
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
