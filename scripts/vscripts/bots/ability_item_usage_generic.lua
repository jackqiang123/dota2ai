-- ability_item_usage_generic.lua
-- v2.0.0 通用技能入口: Valve 每帧都会调 AbilityUsageThink(), 与当前 Mode 无关。
-- 顺序: 救人优先 -> 本英雄 BotLib 的 SkillsComplement() (焦点英雄是真实 Consider,
-- 其余英雄是通用类型驱动 fallback) -> 通用物品使用。
-- 加点: AbilityLevelUpThink() 按 BotLib 的 skill_build, 天赋级按天赋表点天赋。
local Perception = require(GetScriptDirectory() .. "/engine/perception")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local Skill = require(GetScriptDirectory() .. "/engine/skill")

local function heroKey(bot)
  local ok, name = pcall(function() return bot:GetUnitName() end)
  if not ok or name == nil then return nil end
  return string.gsub(name, "^npc_dota_hero_", "")
end

local function loadHeroModule(key)
  if key == nil then return nil end
  local ok, mod = pcall(require, GetScriptDirectory() .. "/BotLib/hero_" .. key)
  if ok then return mod end
  return nil
end

function AbilityUsageThink()
  local bot = GetBot()
  if bot == nil then return end
  local snap = Perception.Snapshot(bot)
  if snap == nil then return end
  local key = heroKey(bot)
  local heroData = Heroes[key]
  -- 救人优先于一切进攻技能 (v1.1.0 保留)。
  if heroData ~= nil and Micro.TryRescueAlly(bot, snap, heroData) then return end
  local mod = loadHeroModule(key)
  if mod ~= nil and mod.SkillsComplement ~= nil then
    local ok, cast = pcall(mod.SkillsComplement, bot, snap)
    if ok and cast then return end
  end
  if heroData ~= nil then
    if Micro.TryCastByType(bot, snap, heroData) then return end
  end
  Micro.TryUseItems(bot, snap)
end

function AbilityLevelUpThink()
  local bot = GetBot()
  if bot == nil then return end
  local okPts, pts = pcall(function() return bot:GetAbilityPoints() end)
  if not okPts or pts == nil or pts <= 0 then return end
  local okLvl, lvl = pcall(function() return bot:GetLevel() end)
  if not okLvl or lvl == nil or lvl < 1 or lvl > 25 then return end
  local key = heroKey(bot)
  local mod = loadHeroModule(key)
  -- 天赋级 (10/15/20/25): 按天赋表点天赋, 不查技能槽。
  if lvl == 10 or lvl == 15 or lvl == 20 or lvl == 25 then
    if mod ~= nil and mod.TALENTS ~= nil then
      if Skill.LevelTalent(bot, mod.TALENTS, lvl) then return end
    end
  end
  if mod == nil or mod.SKILL_BUILD == nil then return end
  local build = mod.SKILL_BUILD
  if lvl > #build then return end
  local slotIdx = build[lvl]
  if slotIdx == nil or slotIdx == 0 then return end
  local names = Skill.GetAbilityList(bot)
  local name = names[slotIdx]
  if name == nil then return end
  local ability = Skill.GetAbilityByName(bot, name)
  if ability == nil then return end
  local okUp, canUp = pcall(function() return ability:CanAbilityBeUpgraded() end)
  if okUp and canUp then
    pcall(function() bot:Action_LevelAbility(name) end)
  end
end

return {
  AbilityUsageThink = AbilityUsageThink,
  AbilityLevelUpThink = AbilityLevelUpThink,
}
