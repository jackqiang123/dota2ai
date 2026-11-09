-- hero_zeus.lua -- Zeus 宙斯 -- v2.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- 焦点英雄: 真实 Consider 逻辑 (见 tools/focus_heroes.py); 其余英雄: 通用类型驱动 fallback。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "zeus"
X.TALENTS = { [10] = 1, [15] = 0, [20] = 1, [25] = 0 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 4, 1, 2, 3, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_aether_lens", "item_aghanims_scepter", "item_octarine_core", "item_black_king_bar", "item_refresher_orb", "item_scythe_of_vyse", "item_travel_boots", "item_kaya_and_sange"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_aether_lens", "item_aghanims_scepter", "item_octarine_core", "item_black_king_bar", "item_refresher_orb", "item_scythe_of_vyse", "item_travel_boots", "item_kaya_and_sange"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_aether_lens", "item_aghanims_scepter", "item_octarine_core", "item_black_king_bar", "item_refresher_orb", "item_scythe_of_vyse", "item_travel_boots", "item_kaya_and_sange"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_aether_lens", "item_aghanims_scepter", "item_octarine_core", "item_black_king_bar", "item_refresher_orb", "item_scythe_of_vyse", "item_travel_boots", "item_kaya_and_sange"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_aether_lens", "item_aghanims_scepter", "item_octarine_core", "item_black_king_bar", "item_refresher_orb", "item_scythe_of_vyse", "item_travel_boots", "item_kaya_and_sange"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.ABILITIES = { Q = "zeus_arc_lightning", W = "zeus_lightning_bolt", E = "zeus_static_field", R = "zeus_thundergods_wrath" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["zeus_arc_lightning"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 700)
  if n >= 2 then return 0.8, snap.nearestEnemy, "unit" end
  if n >= 1 then return 0.55, snap.nearestEnemy, "unit" end
  return 0, nil, "none"
end
function X.ConsiderW(bot, snap, ab)
local ab = ab["zeus_lightning_bolt"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 800 then return 0.75, t, "unit" end
  return 0, nil, "none"
end
function X.ConsiderE(bot, snap, ab)
return 0, nil, "none"
end
function X.ConsiderR(bot, snap, ab)
local ab = ab["zeus_thundergods_wrath"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local low = Skill.CountLowHpEnemies(snap, 0.35)
  if low >= 2 then return 0.95, nil, "none" end
  if low >= 1 then return 0.75, nil, "none" end
  return 0, nil, "none"
end
function X.SkillsComplement(bot, snap)
  if bot == nil or snap == nil then return false end
  local ab = Skill.GetAbilityMap(bot)
  for _, slot in ipairs({"R", "Q", "W", "E"}) do
    local fn = X["Consider" .. slot]
    if fn ~= nil then
      local desire, target, castType = fn(bot, snap, ab)
      if desire ~= nil and desire >= 0.5 then
        local name = X.ABILITIES[slot]
        local ability = ab[name]
        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then
          if slot == "R" then
            local loc = nil
            if target ~= nil then local ok, l = pcall(function() return target:GetLocation() end) if ok then loc = l end end
            if loc ~= nil then Team.ReportComboWindow(bot, loc) end
          end
          return true
        end
      end
    end
  end
  return false
end
return X
