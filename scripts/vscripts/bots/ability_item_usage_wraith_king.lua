-- ability_item_usage_wraith_king.lua -- Wraith King 骷髅王 -- v3.0.0: 技能走 BotLib SkillsComplement(),
-- 加点走 BotLib 的 SKILL_BUILD, 天赋级走 TALENTS。通用入口见 ability_item_usage_generic.lua。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Perception = require(GetScriptDirectory() .. "/engine/perception")
local HERO_KEY = "wraith_king"
local SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 1, 4, 2, 3, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0}

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
  Micro.TryUseItems(bot, snap)
end

function AbilityLevelUpThink()
  local bot = GetBot()
  if bot == nil then return end
  local okPts, pts = pcall(function() return bot:GetAbilityPoints() end)
  if not okPts or pts == nil or pts <= 0 then return end
  local okLvl, lvl = pcall(function() return bot:GetLevel() end)
  if not okLvl or lvl == nil or lvl < 1 then return end
  -- 下一个要点的 build 位置由 (等级 - 剩余点数) 推出, 不存文件级状态:
  -- 正常每次升级只攒 1 点时 idx == lvl, 与旧行为一致; 一次攒多点时从最早
  -- 没点的 build 位置开始依次点, 不会把所有攒的点都砸进 build[lvl] 同一技能。
  -- (模拟实测: Lion 一次升 13 级, 旧版 20 次调用只点了 voodoo 到 4 级, Q/E/R 全 0。)
  local idx = lvl - pts + 1
  if idx < 1 then idx = 1 end
  -- 跳过已满级后无技能可点的空位 (17/18/19/21-24, build==0 且不是天赋级);
  -- 天赋级 (10/15/20/25) 的 build==0 要留住, 下面走点天赋分支。
  while idx <= #SKILL_BUILD and SKILL_BUILD[idx] == 0
      and idx ~= 10 and idx ~= 15 and idx ~= 20 and idx ~= 25 do
    idx = idx + 1
  end
  if idx > #SKILL_BUILD then return end
  if idx == 10 or idx == 15 or idx == 20 or idx == 25 then  -- 天赋级
    local okM, mod = pcall(require, GetScriptDirectory() .. "/BotLib/hero_" .. HERO_KEY)
    if okM and mod ~= nil and mod.TALENTS ~= nil then
      Skill.LevelTalent(bot, mod.TALENTS, idx)
    end
    return
  end
  local slot = SKILL_BUILD[idx] - 1
  local ability = Micro.GetAbility(bot, slot)
  if ability == nil then return end
  local okName, name = pcall(function() return ability:GetAbilityName() end)
  if not okName or name == nil then return end
  local okUp, canUp = pcall(function() return ability:CanAbilityBeUpgraded() end)
  if okUp and canUp then
    pcall(function() bot:Action_LevelAbility(name) end)
  end
end
