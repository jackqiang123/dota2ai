-- engine/hero_key.lua
-- v3.3.0: Valve 内部英雄名 <-> 本项目 key 的换算。
-- 真机里 bot:GetUnitName() 返回的是 Valve 内部名 (如 npc_dota_hero_zuus),
-- 其中 19 个与本项目 key 不同 (zuus=zeus, skeleton_king=wraith_king 等)。
-- 旧版直接拿内部名当 key 查表, 这 19 个英雄在真机里查不到数据:
-- 不放技能、不买装、不点技能、分路默认挤中路。模拟里 GetUnitName() 返回
-- npc_dota_hero_<key>, 映射是恒等, 模拟行为不变。
-- 事实来源只有一处: data/heroes.lua 的 npc_name 字段 (由 tools/generate.py
-- 的 INTERNAL_NAME 表生成, 来源见该表注释)。本模块只做反查, 不另存一份表。
local Heroes = require(GetScriptDirectory() .. "/data/heroes")

local HeroKey = {}

local _byInternal = nil
local function byInternal()
  if _byInternal ~= nil then return _byInternal end
  _byInternal = {}
  for key, h in pairs(Heroes) do
    if h ~= nil and h.npc_name ~= nil then
      local internal = string.gsub(h.npc_name, "^npc_dota_hero_", "")
      _byInternal[internal] = key
    end
    _byInternal[key] = key
  end
  return _byInternal
end

-- "npc_dota_hero_zuus" -> "zeus"; "npc_dota_hero_axe" -> "axe";
-- 未知名字返回 nil (调用方按缺数据处理, 不要猜)。
function HeroKey.FromUnitName(name)
  if name == nil or name == "" then return nil end
  local internal = string.gsub(name, "^npc_dota_hero_", "")
  return byInternal()[internal]
end

-- "zeus" -> "npc_dota_hero_zuus" (选人 SelectHero 要用真内部名)。
function HeroKey.NpcName(key)
  if key == nil then return nil end
  local h = Heroes[key]
  if h ~= nil and h.npc_name ~= nil then return h.npc_name end
  return "npc_dota_hero_" .. tostring(key)
end

return HeroKey
