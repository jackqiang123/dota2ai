-- hero_axe.lua -- Axe 斧王 -- v2.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- 焦点英雄: 真实 Consider 逻辑 (见 tools/focus_heroes.py); 其余英雄: 通用类型驱动 fallback。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "axe"
X.TALENTS = { [10] = 0, [15] = 1, [20] = 0, [25] = 1 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 4, 1, 2, 3, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_blink", "item_blade_mail", "item_black_king_bar", "item_aghanims_shard", "item_heart", "item_assault", "item_overwhelming_blink", "item_travel_boots", "item_shivas_guard", "item_crimson_guard"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_blink", "item_blade_mail", "item_black_king_bar", "item_aghanims_shard", "item_heart", "item_assault", "item_overwhelming_blink", "item_travel_boots", "item_shivas_guard", "item_crimson_guard"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_blink", "item_blade_mail", "item_black_king_bar", "item_aghanims_shard", "item_heart", "item_assault", "item_overwhelming_blink", "item_travel_boots", "item_shivas_guard", "item_crimson_guard"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_blink", "item_blade_mail", "item_black_king_bar", "item_aghanims_shard", "item_heart", "item_assault", "item_overwhelming_blink", "item_travel_boots", "item_shivas_guard", "item_crimson_guard"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_vanguard", "item_phase_boots", "item_blink", "item_blade_mail", "item_black_king_bar", "item_aghanims_shard", "item_heart", "item_assault", "item_overwhelming_blink", "item_travel_boots", "item_shivas_guard", "item_crimson_guard"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.ABILITIES = { Q = "axe_berserkers_call", W = "axe_battle_hunger", E = "axe_counter_helix", R = "axe_culling_blade" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["axe_berserkers_call"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 300)
  local hp = snap.healthPct or 1
  if n >= 2 and hp > 0.35 then return 0.95, snap.nearestEnemy, "none" end
  if n >= 1 and hp > 0.6 then return 0.7, snap.nearestEnemy, "none" end
  if n >= 3 then return 0.85, snap.nearestEnemy, "none" end
  return 0, nil, "none"
end
function X.ConsiderW(bot, snap, ab)
local ab = ab["axe_battle_hunger"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 700 then return 0.6, t, "unit" end
  return 0, nil, "none"
end
function X.ConsiderE(bot, snap, ab)
return 0, nil, "none"
end
function X.ConsiderR(bot, snap, ab)
local ab = ab["axe_culling_blade"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local t = Skill.LowestHpEnemy(snap)
  if t == nil then return 0, nil, "none" end
  local hp = Skill.HpOf(t)
  if hp > 0 and hp < 250 then return 1.0, t, "unit" end
  local pct = Skill.HpPctOf(t)
  if pct > 0 and pct < 0.2 then return 0.9, t, "unit" end
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
