-- verify_hero_key.lua -- v3.3.0 验证测试: Valve 内部英雄名 <-> 本项目 key 换算。
-- 用法 (在仓库根目录): lua5.4 tools/verify_hero_key.lua
-- 退出码 0=全部通过; 任一断言失败即报错退出。
-- 背景: 真机里 bot:GetUnitName() 返回 Valve 内部名, 其中 19 个与本项目 key
-- 不同 (zuus=zeus, skeleton_king=wraith_king 等); 旧版直接拿内部名当 key
-- 查表, 这 19 个英雄在真机里不放技能、不买装、不点技能。engine/hero_key.lua
-- 按 data/heroes.lua 的 npc_name 字段反查, 不另存一份表。
-- 事实来源: tools/generate.py 的 INTERNAL_NAME 表 (Liquipedia Cheats +
-- skadi npc_heroes.txt, 两处独立核对一致)。
local _script = (arg and arg[0]) or "tools/verify_hero_key.lua"
local _root = _script:match("^(.*)/tools/verify_hero_key%.lua$") or "."
if _root == "" then _root = "." end
package.path = _root .. "/scripts/vscripts/?.lua;" .. _root .. "/scripts/vscripts/?/init.lua;" .. package.path

function GetScriptDirectory() return "bots" end

local HeroKey = require("bots/engine/hero_key")
local Heroes = require("bots/data/heroes")

local passed = 0
local function check(name, cond, extra)
  if not cond then error("FAIL: " .. name .. (extra and (" -- " .. tostring(extra)) or ""), 2) end
  passed = passed + 1
  print("PASS: " .. name)
end

-- 19 个改名英雄: 内部名 -> key, key -> 内部名。
local RENAMED = {
  anti_mage = "antimage", centaur_warrunner = "centaur", clockwerk = "rattletrap",
  doom = "doom_bringer", io = "wisp", lifestealer = "life_stealer",
  magnus = "magnataur", natures_prophet = "furion", necrophos = "necrolyte",
  outworld_destroyer = "obsidian_destroyer", queen_of_pain = "queenofpain",
  shadow_fiend = "nevermore", timbersaw = "shredder", treant_protector = "treant",
  underlord = "abyssal_underlord", vengeful_spirit = "vengefulspirit",
  windranger = "windrunner", wraith_king = "skeleton_king", zeus = "zuus",
}
local n_renamed = 0
for key, internal in pairs(RENAMED) do
  n_renamed = n_renamed + 1
  check("FromUnitName npc_dota_hero_" .. internal .. " == " .. key,
        HeroKey.FromUnitName("npc_dota_hero_" .. internal) == key)
  check("NpcName(" .. key .. ") == npc_dota_hero_" .. internal,
        HeroKey.NpcName(key) == "npc_dota_hero_" .. internal)
  check("heroes.lua npc_name(" .. key .. ") == npc_dota_hero_" .. internal,
        Heroes[key] ~= nil and Heroes[key].npc_name == "npc_dota_hero_" .. internal)
end
check("renamed count == 19", n_renamed == 19)

-- 其余 108 个: 内部名 == key, 恒等映射。
local n_identity = 0
for key, h in pairs(Heroes) do
  if RENAMED[key] == nil then
    n_identity = n_identity + 1
    if HeroKey.FromUnitName("npc_dota_hero_" .. key) ~= key then
      error("FAIL: identity FromUnitName(" .. key .. ")")
    end
    if HeroKey.NpcName(key) ~= "npc_dota_hero_" .. key then
      error("FAIL: identity NpcName(" .. key .. ")")
    end
    if h.npc_name ~= "npc_dota_hero_" .. key then
      error("FAIL: identity npc_name(" .. key .. ") = " .. tostring(h.npc_name))
    end
  end
end
check("identity count == 108", n_identity == 108)

-- 全部 127 个往返: FromUnitName(NpcName(key)) == key。
local n_total = 0
for key, _ in pairs(Heroes) do
  n_total = n_total + 1
  if HeroKey.FromUnitName(HeroKey.NpcName(key)) ~= key then
    error("FAIL: round-trip " .. key)
  end
end
check("round-trip all 127 heroes", n_total == 127)

-- 未知 / 空输入返回 nil, 不猜。
check("FromUnitName(nil) == nil", HeroKey.FromUnitName(nil) == nil)
check("FromUnitName('') == nil", HeroKey.FromUnitName("") == nil)
check("FromUnitName unknown == nil",
      HeroKey.FromUnitName("npc_dota_hero_nonexistent_hero") == nil)
check("NpcName(nil) == nil", HeroKey.NpcName(nil) == nil)

print("verify_hero_key: " .. passed .. " checks PASSED")
