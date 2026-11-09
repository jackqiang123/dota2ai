package.path = "/home/hatch/workspace/dota2-ai/scripts/vscripts/?.lua;/home/hatch/workspace/dota2-ai/scripts/vscripts/?/init.lua;" .. package.path
BOT_MODE_NONE = 0
local _t = 100
function DotaTime() _t = _t + 0.1 return _t end
function GetItemCost(name) return 100 end
local function mkunit(hp, x, y)
  return {
    GetHealth=function() return hp end, GetMaxHealth=function() return 1000 end,
    GetMana=function() return 500 end, GetMaxMana=function() return 500 end,
    GetHealthRegen=function() return 2 end, GetMovementSpeed=function() return 300 end,
    GetLocation=function() return {x=x, y=y, z=0} end,
    IsAlive=function() return true end, IsNull=function() return false end,
    GetUnitName=function() return "npc_dota_hero_axe" end,
  }
end
local mock = mkunit(800, 0, 0)
mock.GetLevel=function() return 5 end
mock.GetGold=function() return 2000 end
mock.GetAttackRange=function() return 150 end
mock.GetAttackDamage=function() return 60 end
mock.GetTeam=function() return 2 end
mock.GetNearbyHeroes=function(self, r, enemy, mode) if enemy then return {mkunit(400, 300, 0)} else return {} end end
mock.GetNearbyCreeps=function(self, r, enemy) if enemy then return {mkunit(50, 200, 0)} else return {mkunit(500, -200, 0)} end end
mock.GetNearbyTowers=function(self, r, enemy) return {} end
mock.GetAbilityInSlot=function(self, i) return nil end
mock.GetItemInSlot=function(self, i) return nil end
mock.GetAbilityPoints=function() return 1 end
mock.Action_MoveToLocation=function(self, loc) end
mock.Action_AttackUnit=function(self, u, once) end
mock.Action_UseAbilityOnEntity=function(self, a, u) end
mock.Action_UseAbilityOnLocation=function(self, a, loc) end
mock.Action_PurchaseItem=function(self, n) return true end
mock.Action_LevelAbility=function(self, n) end
mock.Action_MoveToUnit=function(self, u) end
function GetBot() return mock end
local Core = require("bots/engine/core")
assert(Core ~= nil, "core nil")
local data, key = Core.GetHeroData(mock)
assert(data ~= nil and key == "axe", "hero lookup failed")
assert(data.name_cn == "斧王", "cn name wrong: " .. tostring(data.name_cn))
assert(#data.skill_build == 25, "skill build len")
assert(data.items.early[1] == "item_tango", "early items")
Core.Think(mock)
Core.Think(mock)
-- hero selection
local hs = require("bots/hero_selection")
assert(hs.SelectHero({}, {"axe","zeus","crystal_maiden"}) == "zeus", "select failed:补2号位应选zeus")
assert(hs.SelectHero({}, {"axe","juggernaut"}) == "juggernaut", "select pos1 failed")
-- per-hero wrapper loads
dofile("/home/hatch/workspace/dota2-ai/scripts/vscripts/bots/bot_axe.lua")
Think()
dofile("/home/hatch/workspace/dota2-ai/scripts/vscripts/bots/bot_zeus.lua")
Think()
dofile("/home/hatch/workspace/dota2-ai/scripts/vscripts/bots/bot_largo.lua")
Think()
print("SMOKE OK: core Think x2, hero lookup, select, bot_axe/zeus/largo Think all ran without error")
