-- ability_item_usage_generic.lua
-- v2.0.0 通用技能入口: Valve 每帧都会调 AbilityUsageThink(), 与当前 Mode 无关。
-- 顺序: 救人优先 -> 本英雄 BotLib 的 SkillsComplement() (焦点英雄是真实 Consider,
-- 其余英雄是通用类型驱动 fallback) -> 通用物品使用。
-- 加点: AbilityLevelUpThink() 按 BotLib 的 skill_build, 天赋级按天赋表点天赋。
local Perception = require(GetScriptDirectory() .. "/engine/perception")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local HeroKey = require(GetScriptDirectory() .. "/engine/hero_key")

local function heroKey(bot)
  local ok, name = pcall(function() return bot:GetUnitName() end)
  if not ok or name == nil then return nil end
  return HeroKey.FromUnitName(name)
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
  if mod == nil or mod.SKILL_BUILD == nil then return end
  local build = mod.SKILL_BUILD
  -- 下一个要点的 build 位置由 (等级 - 剩余点数) 推出, 不存模块级状态:
  -- 正常每次升级只攒 1 点时 idx == lvl, 与旧行为一致; 一次攒多点时从最早
  -- 没点的 build 位置开始依次点, 不会把所有攒的点都砸进 build[lvl] 同一技能。
  -- (模拟实测: Lion 一次升 13 级, 旧版 20 次调用只点了 voodoo 到 4 级, Q/E/R 全 0。)
  local idx = lvl - pts + 1
  if idx < 1 then idx = 1 end
  -- 跳过已满级后无技能可点的空位 (17/18/19/21-24, build==0 且不是天赋级);
  -- 天赋级 (10/15/20/25) 的 build==0 要留住, 下面走点天赋分支。
  while idx <= #build and build[idx] == 0
      and idx ~= 10 and idx ~= 15 and idx ~= 20 and idx ~= 25 do
    idx = idx + 1
  end
  if idx > #build then return end
  -- 天赋级 (10/15/20/25): 按天赋表点天赋, 不查技能槽。
  if idx == 10 or idx == 15 or idx == 20 or idx == 25 then
    if mod.TALENTS ~= nil then
      if Skill.LevelTalent(bot, mod.TALENTS, idx) then return end
    end
    return
  end
  local slotIdx = build[idx]
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
