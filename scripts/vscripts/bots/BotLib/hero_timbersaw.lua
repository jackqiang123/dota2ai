-- hero_timbersaw.lua -- Timbersaw 伐木机 -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
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
X.KEY = "timbersaw"
X.TALENTS = { [10] = 0, [15] = 1, [20] = 0, [25] = 1 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 1, 4, 2, 3, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_null_talisman", "item_power_treads", "item_bloodstone", "item_black_king_bar", "item_shivas_guard", "item_octarine_core", "item_aghanims_scepter", "item_kaya_and_sange", "item_travel_boots", "item_moon_shard"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_bloodstone", "item_black_king_bar", "item_shivas_guard", "item_octarine_core", "item_aghanims_scepter", "item_kaya_and_sange", "item_travel_boots"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_bloodstone", "item_black_king_bar", "item_shivas_guard", "item_octarine_core", "item_aghanims_scepter", "item_kaya_and_sange", "item_lotus_orb", "item_heart", "item_travel_boots"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_bloodstone", "item_black_king_bar", "item_shivas_guard", "item_force_staff", "item_aghanims_scepter", "item_lotus_orb"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_ward_sentry", "item_magic_wand", "item_arcane_boots", "item_bloodstone", "item_black_king_bar", "item_force_staff", "item_glimmer_cape", "item_pipe_of_insight"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.sSellListByPos = {}
X.sSellListByPos["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"}
X.sSellListByPos["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle"}
X.sSellListByPos["pos_3"] = {"item_tango", "item_flask", "item_bracer"}
X.sSellListByPos["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer"}
X.sSellListByPos["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"}
X.ABILITIES = { Q = "shredder_whirling_death", W = "shredder_timber_chain", E = "shredder_reactive_armor", R = "shredder_chakram" }
function X.ConsiderQ(bot, snap, ab)
local ab = ab["shredder_whirling_death"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 400)
  if n >= 2 then return 0.85, snap.nearestEnemy, "none" end
  if n >= 1 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 350 then return 0.65, snap.nearestEnemy, "none" end
  -- 清兵: Whirling Death 是自身周围 AoE, 本来就是清兵/打钱技能; 2v3 劣势路被压制时只靠平 A 一个补刀都拿不到
  -- (v3.2.0 实测: 38 次命中、2 反补、0 补刀)。附近 >=3 个敌方小兵时对最近小兵放 Q, 顺带打到周围英雄
  -- (不要求 400 内无人: 技能本来就同时打英雄+小兵; 英雄分支在上面已优先处理, 这里只补清兵;
  -- 蓝量留 25% 以上即可: Q 只要 100 蓝, 留一个 W 逃生够了; 40% 的门槛实测几乎不触发)。
  local nc = 0
  local ncNear = nil
  local ncD = 1e9
  if snap.nearbyEnemyCreeps ~= nil and snap.location ~= nil then
    for _, c in ipairs(snap.nearbyEnemyCreeps) do
      local ok, l = pcall(function() return c:GetLocation() end)
      if ok and l ~= nil then
        local d = math.sqrt((l.x - snap.location.x) ^ 2 + (l.y - snap.location.y) ^ 2)
        if d <= 400 then nc = nc + 1 if d < ncD then ncD = d ncNear = c end end
      end
    end
  end
  if nc >= 3 and ncNear ~= nil and (snap.manaPct or 1) > 0.25 then return 0.6, ncNear, "none" end
  return 0, nil, "none"

end
function X.ConsiderW(bot, snap, ab)
local ab = ab["shredder_timber_chain"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.healthPct or 1) < 0.35 and (snap.numEnemies or 0) >= 1 then return 0.85, snap.nearestEnemy, "location" end
  local t = Skill.LowestHpEnemy(snap)
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 400 and snap.nearestEnemyDist <= 900 then return 0.75, t, "location" end
  if t ~= nil and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist >= 400 and snap.nearestEnemyDist <= 700 then return 0.6, t, "location" end
  return 0, nil, "none"

end
function X.ConsiderE(bot, snap, ab)
return 0, nil, "none"

end
function X.ConsiderR(bot, snap, ab)
local ab = ab["shredder_chakram"]
  if not Skill.IsCastable(ab) then return 0, nil, "none" end
  if (snap.manaPct or 1) < 0.25 then return 0, nil, "none" end
  local n = Skill.CountEnemiesInRange(snap, 600)
  local t = Skill.LowestHpEnemy(snap)
  if n >= 2 and t ~= nil then return 0.9, t, "location" end
  if t ~= nil and Skill.HpPctOf(t) < 0.5 and snap.nearestEnemyDist ~= nil and snap.nearestEnemyDist <= 600 then return 0.8, t, "location" end
  if n >= 1 and t ~= nil then return 0.65, t, "location" end
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
