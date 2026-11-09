-- ability_item_usage_kez.lua -- Kez 凯 -- v3.0.0: 技能走 BotLib SkillsComplement(),
-- 加点走 BotLib 的 SKILL_BUILD, 天赋级走 TALENTS。通用入口见 ability_item_usage_generic.lua。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Perception = require(GetScriptDirectory() .. "/engine/perception")
local HERO_KEY = "kez"
local SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 4, 1, 2, 3, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0}

function AbilityUsageThink()
  local bot = GetBot()
  if bot == nil then return end
  local snap = Perception.Snapshot(bot)
  if snap == nil then return end
  if Micro.TryRescueAlly(bot, snap, Heroes[HERO_KEY]) then return end
  local ok, mod = pcall(require, GetScriptDirectory() .. "/BotLib/hero_" .. HERO_KEY)
  if ok and mod ~= nil and mod.SkillsComplement ~= nil then
    local ok2, cast = pcall(mod.SkillsComplement, bot, snap)
    if ok2 and cast then return end
  end
  Micro.TryCastByType(bot, snap, Heroes[HERO_KEY])
end

function AbilityLevelUpThink()
  local bot = GetBot()
  if bot == nil then return end
  local okPts, pts = pcall(function() return bot:GetAbilityPoints() end)
  if not okPts or pts == nil or pts <= 0 then return end
  local okLvl, lvl = pcall(function() return bot:GetLevel() end)
  if not okLvl or lvl == nil or lvl < 1 or lvl > #SKILL_BUILD then return end
  if SKILL_BUILD[lvl] == 0 then return end  -- 天赋级,显式跳过,禁止查询 -1 槽位。
  local slot = SKILL_BUILD[lvl] - 1
  local ability = Micro.GetAbility(bot, slot)
  if ability == nil then return end
  local okName, name = pcall(function() return ability:GetAbilityName() end)
  if not okName or name == nil then return end
  local okUp, canUp = pcall(function() return ability:CanAbilityBeUpgraded() end)
  if okUp and canUp then
    pcall(function() bot:Action_LevelAbility(name) end)
  end
end
