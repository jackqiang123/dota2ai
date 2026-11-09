-- ability_item_usage_death_prophet.lua -- Death Prophet 死亡先知 -- 技能释放走 engine/micro.lua 的类型抽象,加点走下表。
local Heroes = require("bots/data/heroes")
local Micro = require("bots/engine/micro")
local Perception = require("bots/engine/perception")
local HERO_KEY = "death_prophet"
local SKILL_BUILD = {1, 3, 2, 1, 3, 4, 2, 1, 3, 2, 4, 1, 3, 2, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0}

function AbilityUsageThink()
  local bot = GetBot()
  if bot == nil then return end
  local snap = Perception.Snapshot(bot)
  if snap == nil then return end
  Micro.TryCastByType(bot, snap, Heroes[HERO_KEY])
end

function AbilityLevelUpThink()
  local bot = GetBot()
  if bot == nil then return end
  local okPts, pts = pcall(function() return bot:GetAbilityPoints() end)
  if not okPts or pts == nil or pts <= 0 then return end
  local okLvl, lvl = pcall(function() return bot:GetLevel() end)
  if not okLvl or lvl == nil or lvl < 1 or lvl > #SKILL_BUILD then return end
  if SKILL_BUILD[lvl] == 0 then return end  -- v1.1.0:该级无技能可点(天赋点),显式跳过,禁止查询 -1 槽位。
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
