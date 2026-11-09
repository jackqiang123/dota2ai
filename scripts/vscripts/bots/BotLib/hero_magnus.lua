-- hero_magnus.lua -- Magnus 马格纳斯 -- v2.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- 焦点英雄: 真实 Consider 逻辑 (见 tools/focus_heroes.py); 其余英雄: 通用类型驱动 fallback。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "magnus"
X.TALENTS = { [10] = 0, [15] = 1, [20] = 0, [25] = 1 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 4, 1, 2, 3, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_refresher_orb", "item_assault", "item_shivas_guard", "item_heart", "item_echo_sabre", "item_harpoon"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_refresher_orb", "item_assault", "item_shivas_guard", "item_heart", "item_echo_sabre", "item_harpoon"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_refresher_orb", "item_assault", "item_shivas_guard", "item_heart", "item_echo_sabre", "item_harpoon"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_refresher_orb", "item_assault", "item_shivas_guard", "item_heart", "item_echo_sabre", "item_harpoon"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_blink", "item_black_king_bar", "item_aghanims_scepter", "item_refresher_orb", "item_assault", "item_shivas_guard", "item_heart", "item_echo_sabre", "item_harpoon"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.ABILITIES = { Q = "magnus_shockwave", W = "magnus_empower", E = "magnus_skewer", R = "magnus_reverse_polarity" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["magnus_shockwave"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 900)
  if n >= 2 then return 0.7, snap.nearestEnemy, "location" end
  if n >= 1 then return 0.5, snap.nearestEnemy, "location" end
  return 0, nil, "none"
end
function X.ConsiderW(bot, snap, ab)
local ab = ab["magnus_empower"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local ally = Skill.LowestHpAlly(snap)
  if ally ~= nil then return 0.6, ally, "unit" end
  if (snap.healthPct or 1) > 0.5 then return 0.55, bot, "unit" end
  return 0, nil, "none"
end
function X.ConsiderE(bot, snap, ab)
local ab = ab["magnus_skewer"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 500)
  if n >= 2 then return 0.75, snap.nearestEnemy, "location" end
  return 0, nil, "none"
end
function X.ConsiderR(bot, snap, ab)
local ab = ab["magnus_reverse_polarity"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if Team.ShouldHoldUlt(bot) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 3 then return 1.0, snap.nearestEnemy, "none" end
  if n >= 2 then return 0.9, snap.nearestEnemy, "none" end
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
