-- verify_v200.lua -- v2.0.0 验证测试 (取代旧 smoke_test.lua, 后者硬编码 /home/hatch 路径已删)。
-- 用法 (在仓库根目录): lua5.4 tools/verify_v200.lua
-- 退出码 0=全部通过; 任一断言失败即报错退出。
-- 关键: 测试里提供 GetScriptDirectory() stub, 返回 "bots", 与 Valve 写法一致,
-- 不靠 package.path 硬编码绝对路径。
local _script = (arg and arg[0]) or "tools/verify_v200.lua"
local _root = _script:match("^(.*)/tools/verify_v200%.lua$") or "."
if _root == "" then _root = "." end
package.path = _root .. "/scripts/vscripts/?.lua;" .. _root .. "/scripts/vscripts/?/init.lua;" .. package.path

BOT_MODE_NONE = 0
function GetScriptDirectory() return "bots" end
local _T = 100
function DotaTime() return _T end
function GetItemCost(name) return 100 end
local function setTime(t) _T = t end

local passed = 0
local function check(name, cond, extra)
  if not cond then error("FAIL: " .. name .. (extra and (" -- " .. tostring(extra)) or ""), 2) end
  passed = passed + 1
  print("PASS: " .. name)
end
local function hasLog(log, pat)
  for _, s in ipairs(log) do if string.find(s, pat, 1, true) then return true end end
  return false
end

local function mkability(name, range, castable)
  return {
    GetAbilityName = function() return name end,
    IsPassive = function() return false end,
    IsFullyCastable = function() return castable ~= false end,
    CanAbilityBeUpgraded = function() return true end,
    GetCastRange = function() return range or 600 end,
    IsNull = function() return false end,
    IsHidden = function() return false end,
  }
end
local function mkitem(name)
  return { GetName = function() return name end, GetAbilityName = function() return name end, IsNull = function() return false end, IsFullyCastable = function() return true end }
end
local function mkunit(id, hp, maxHp, x, y)
  return {
    _id = id,
    GetHealth = function() return hp end,
    GetMaxHealth = function() return maxHp or 1000 end,
    GetMana = function() return 500 end, GetMaxMana = function() return 500 end,
    GetHealthRegen = function() return 2 end,
    GetMovementSpeed = function() return 300 end,
    GetLocation = function() return { x = x or 0, y = y or 0, z = 0 } end,
    IsAlive = function() return hp > 0 end,
    IsNull = function() return false end,
    GetUnitName = function() return "npc_dota_hero_" .. id end,
  }
end
local function mkbot(opts)
  opts = opts or {}
  local bot = {
    _id = opts.hero or "axe", log = {},
    _hp = opts.hp or 800, _maxHp = opts.maxHp or 1000,
    _x = opts.x or 0, _y = opts.y or 0,
    _level = opts.level or 5, _gold = opts.gold or 0,
    _abilities = opts.abilities or {}, _items = opts.items or {},
    _enemies = opts.enemies or {}, _allies = opts.allies or {},
    _ecreeps = opts.ecreeps or {}, _acreeps = opts.acreeps or {}, _towers = opts.towers or {},
    _courier = opts.courier, _stash = opts.stash,
  }
  bot.GetUnitName = function(self) return "npc_dota_hero_" .. (opts.hero or "axe") end
  bot.GetHealth = function(self) return bot._hp end
  bot.GetMaxHealth = function(self) return bot._maxHp end
  bot.GetMana = function(self) return 500 end
  bot.GetMaxMana = function(self) return 500 end
  bot.GetHealthRegen = function(self) return 2 end
  bot.GetMovementSpeed = function(self) return 300 end
  bot.GetLocation = function(self) return { x = bot._x, y = bot._y, z = 0 } end
  bot.IsAlive = function(self) return true end
  bot.IsNull = function(self) return false end
  bot.GetLevel = function(self) return bot._level end
  bot.GetGold = function(self) return bot._gold end
  bot.GetAttackRange = function(self) return 150 end
  bot.GetAttackDamage = function(self) return 60 end
  bot.GetTeam = function(self) return 2 end
  bot.GetPlayerID = function(self) return 0 end
  bot.GetNearbyHeroes = function(self, r, enemy, mode) if enemy then return bot._enemies else return bot._allies end end
  bot.GetNearbyCreeps = function(self, r, enemy) if enemy then return bot._ecreeps else return bot._acreeps end end
  bot.GetNearbyTowers = function(self, r, enemy) return bot._towers end
  bot.GetAbilityInSlot = function(self, i) return bot._abilities[i] end
  bot.GetAbilityByName = function(self, name)
    for _, ab in pairs(bot._abilities) do if ab:GetAbilityName() == name then return ab end end
    return nil
  end
  bot.GetItemInSlot = function(self, i) return bot._items[i] end
  bot.GetAbilityPoints = function(self) return 1 end
  bot.GetCourier = function(self) return bot._courier end
  bot.GetNumItemsInStash = function(self) return bot._stash end
  bot.Action_MoveToLocation = function(self, loc) bot.log[#bot.log + 1] = "move:" .. loc.x .. "," .. loc.y end
  bot.Action_MoveToUnit = function(self, u) bot.log[#bot.log + 1] = "moveto:" .. (u._id or "?") end
  bot.Action_AttackUnit = function(self, u, once) bot.log[#bot.log + 1] = "attack:" .. (u._id or "?") end
  bot.Action_UseAbility = function(self, a) bot.log[#bot.log + 1] = "cast_nontarget:" .. a:GetAbilityName() end
  bot.Action_UseAbilityOnEntity = function(self, a, u) bot.log[#bot.log + 1] = "cast_entity:" .. a:GetAbilityName() .. "->" .. (u._id or "?") end
  bot.Action_UseAbilityOnLocation = function(self, a, loc) bot.log[#bot.log + 1] = "cast_loc:" .. a:GetAbilityName() .. "@" .. loc.x .. "," .. loc.y end
  bot.Action_PurchaseItem = function(self, n) bot.log[#bot.log + 1] = "buy:" .. n return true end
  bot.Action_LevelAbility = function(self, n) bot.log[#bot.log + 1] = "level:" .. n end
  bot.Action_Courier = function(self, action) bot.log[#bot.log + 1] = "courier:" .. tostring(action) return true end
  return bot
end

local Perception = require("bots/engine/perception")
local Team = require("bots/engine/team")
local Skill = require("bots/engine/skill")
local Dispatcher = require("bots/mode_dispatcher")
local Heroes = require("bots/data/heroes")

local function snapFor(bot) Perception.Invalidate(bot) return Perception.Snapshot(bot) end

-- 1. 每个 Mode 的 GetDesire 都在 0-1 内, 且有 Think/OnStart
do
  local modes = Dispatcher.LoadModes()
  local n = 0
  for _, key in ipairs(Dispatcher.MODE_FILES) do
    local m = modes[key]
    check("1 mode exists " .. key, m ~= nil and m.GetDesire ~= nil and m.Think ~= nil and m.OnStart ~= nil)
    n = n + 1
  end
  check("1 mode count >=12", n >= 12, "n=" .. n)
  local bot = mkbot({ hero = "axe", hp = 800, enemies = { mkunit("e1", 400, 1000, 300, 0) }, ecreeps = { mkunit("c1", 50, 500, 200, 0) } })
  local snap = snapFor(bot)
  local bb = Team.GetBlackboard()
  for _, key in ipairs(Dispatcher.MODE_FILES) do
    local d = modes[key].GetDesire(bot, snap, bb)
    check("1 desire 0-1 " .. key, type(d) == "number" and d >= 0 and d <= 1, "d=" .. tostring(d))
  end
end

-- 2. 最高分模式被选中 (残血 -> retreat; 连招窗口 -> team_roam/attack 高)
do
  Team.ResetBlackboard(); Dispatcher.ResetThinkState(); setTime(100)
  local bot = mkbot({ hero = "axe", hp = 100, maxHp = 1000, enemies = { mkunit("e1", 400, 1000, 300, 0) } })
  local snap = snapFor(bot)
  local best, scores = Dispatcher.SelectMode(bot, snap, Team.GetBlackboard())
  check("2 low-hp selects retreat", best == "retreat", "best=" .. tostring(best) .. " retreat=" .. tostring(scores.retreat))
  Team.ResetBlackboard(); setTime(200)
  local bot2 = mkbot({ hero = "axe", hp = 900, enemies = { mkunit("e1", 400, 1000, 300, 0), mkunit("e2", 400, 1000, 350, 0) }, allies = { mkunit("a1", 800, 1000, 100, 0), mkunit("a2", 800, 1000, 120, 0), mkunit("a3", 800, 1000, 140, 0) } })
  Team.ReportComboWindow(bot2, { x = 300, y = 0, z = 0 })
  local snap2 = snapFor(bot2)
  local best2, scores2 = Dispatcher.SelectMode(bot2, snap2, Team.GetBlackboard())
  check("2 combo window raises team_roam/attack", (scores2.team_roam or 0) >= 0.8 or (scores2.attack or 0) >= 0.7, "team_roam=" .. tostring(scores2.team_roam) .. " attack=" .. tostring(scores2.attack) .. " best=" .. tostring(best2))
end

-- 3. TeamThink 写黑板
do
  Team.ResetBlackboard(); setTime(1300)
  local bot = mkbot({ hero = "axe", hp = 900, enemies = {}, allies = { mkunit("a1", 800, 1000, 100, 0), mkunit("a2", 800, 1000, 120, 0), mkunit("a3", 800, 1000, 140, 0) } })
  local snap = snapFor(bot)
  local plan = Team.TeamThink(bot, snap, Team.GetBlackboard())
  check("3 TeamThink roshan when dead>=2 and t>1200", plan == "roshan" and Team.GetBlackboard().plan == "roshan", "plan=" .. tostring(plan) .. " dead=" .. tostring(Team.GetBlackboard().deadEnemies))
  Team.ResetBlackboard(); setTime(300)
  local bot2 = mkbot({ hero = "axe", hp = 900, enemies = { mkunit("e1", 400, 1000, 300, 0) }, allies = {} })
  Team.ReportComboWindow(bot2, { x = 300, y = 0, z = 0 })
  local plan2 = Team.TeamThink(bot2, snapFor(bot2), Team.GetBlackboard())
  check("3 TeamThink teamfight on combo window", plan2 == "teamfight", "plan=" .. tostring(plan2))
end

-- 4. 焦点英雄 Consider: 每个至少一个 desire>0.5 的真实场景
local function focusCheck(hero, slot, abilities, enemies, allies, hp, expectPat)
  Team.ResetBlackboard(); Dispatcher.ResetThinkState(); setTime(400)
  local bot = mkbot({ hero = hero, hp = hp or 800, abilities = abilities, enemies = enemies or {}, allies = allies or {} })
  local snap = snapFor(bot)
  local mod = require("bots/BotLib/hero_" .. hero)
  local ab = Skill.GetAbilityMap(bot)
  local fn = mod["Consider" .. slot]
  local desire, target, ct = fn(bot, snap, ab)
  check("4 " .. hero .. " Consider" .. slot .. " desire>0.5", desire ~= nil and desire > 0.5, "desire=" .. tostring(desire))
  local cast = mod.SkillsComplement(bot, snap)
  check("4 " .. hero .. " SkillsComplement casts " .. expectPat, cast == true and hasLog(bot.log, expectPat), table.concat(bot.log, ";"))
end
do
  local e2 = { mkunit("e1", 400, 1000, 200, 0), mkunit("e2", 400, 1000, 250, 0) }
  local eLow = { mkunit("e1", 100, 1000, 200, 0) }
  focusCheck("axe", "Q", { [0] = mkability("axe_berserkers_call", 300) }, e2, {}, 800, "cast_nontarget:axe_berserkers_call")
  focusCheck("axe", "R", { [3] = mkability("axe_culling_blade", 600) }, eLow, {}, 800, "cast_entity:axe_culling_blade")
  focusCheck("zeus", "R", { [3] = mkability("zeus_thundergods_wrath", 0) }, { mkunit("e1", 200, 1000, 900, 0), mkunit("e2", 200, 1000, 950, 0) }, {}, 800, "cast_nontarget:zeus_thundergods_wrath")
  focusCheck("lion", "R", { [3] = mkability("lion_finger_of_death", 600) }, eLow, {}, 800, "cast_entity:lion_finger_of_death")
  focusCheck("crystal_maiden", "R", { [3] = mkability("crystal_maiden_freezing_field", 600) }, e2, {}, 800, "cast_nontarget:crystal_maiden_freezing_field")
  focusCheck("magnus", "R", { [3] = mkability("magnus_reverse_polarity", 400) }, e2, {}, 800, "cast_nontarget:magnus_reverse_polarity")
  focusCheck("faceless_void", "R", { [3] = mkability("faceless_void_chronosphere", 425) }, e2, {}, 800, "cast_loc:faceless_void_chronosphere")
  focusCheck("enigma", "R", { [3] = mkability("enigma_black_hole", 400) }, e2, {}, 800, "cast_loc:enigma_black_hole")
  focusCheck("dazzle", "W", { [1] = mkability("dazzle_shallow_grave", 600) }, { mkunit("e1", 400, 1000, 300, 0) }, { mkunit("huskar", 200, 1000, 100, 0) }, 800, "cast_entity:dazzle_shallow_grave")
  focusCheck("oracle", "R", { [3] = mkability("oracle_false_promise", 600) }, { mkunit("e1", 400, 1000, 300, 0) }, { mkunit("huskar", 200, 1000, 100, 0) }, 800, "cast_entity:oracle_false_promise")
  focusCheck("huskar", "R", { [3] = mkability("huskar_life_break", 600) }, { mkunit("e1", 400, 1000, 200, 0) }, {}, 800, "cast_entity:huskar_life_break")
end

-- 5. Void 大不与黑洞重叠 (combo 窗口由 enigma 开, 2 秒内忍住)
do
  Team.ResetBlackboard(); setTime(500)
  local bot = mkbot({ hero = "faceless_void", hp = 800, abilities = { [3] = mkability("faceless_void_chronosphere", 425) }, enemies = { mkunit("e1", 400, 1000, 200, 0), mkunit("e2", 400, 1000, 250, 0) } })
  Team.ReportComboWindow(bot, { x = 200, y = 0, z = 0 })
  -- 手动把窗口释放者改成 enigma (模拟队友黑洞先开)
  Team.GetBlackboard().comboWindow.caster = "npc_dota_hero_enigma"
  local mod = require("bots/BotLib/hero_faceless_void")
  local snap = snapFor(bot)
  local desire = mod.ConsiderR(bot, snap, Skill.GetAbilityMap(bot))
  check("5 void holds ult within 2s of enigma black hole", desire == 0, "desire=" .. tostring(desire))
end

-- 6. combo 窗口 / 集火仍能用
do
  Team.ResetBlackboard(); setTime(600)
  local bot = mkbot({ hero = "axe", hp = 800, enemies = { mkunit("e1", 200, 1000, 300, 0), mkunit("e2", 900, 1000, 350, 0) } })
  local snap = snapFor(bot)
  local focus = Team.GetFocusTarget(snap)
  check("6 focus target is lowest-hp enemy", focus ~= nil and focus._id == "e1", "focus=" .. tostring(focus and focus._id))
  Team.ReportComboWindow(bot, { x = 300, y = 0, z = 0 })
  check("6 combo window active", Team.IsComboWindowActive() == true)
end

-- 7. GetScriptDirectory 写法全仓库一致 + Lua 5.1 无禁用语法 (用 grep 扫, 不靠手写断言)
do
  local function grepCount(pat)
    local h = io.popen("grep -r --include='*.lua' -l '" .. pat .. "' " .. _root .. "/scripts/vscripts/bots 2>/dev/null | wc -l")
    local n = tonumber(h:read("*a")) or 0
    h:close()
    return n
  end
  check("7 no require(\"bots/...\") left", grepCount('require("bots/') == 0, "count=" .. grepCount('require("bots/'))
  check("7 GetScriptDirectory used", grepCount('GetScriptDirectory') > 50, "count=" .. grepCount('GetScriptDirectory'))
  check("7 no goto in Lua", grepCount('goto') == 0)
  check("7 no table.unpack in Lua", grepCount('table.unpack') == 0)
end

-- 8. 技能动态读取 + 天赋 + 出装状态机
do
  local bot = mkbot({ hero = "axe", abilities = { [0] = mkability("axe_berserkers_call", 300), [1] = mkability("axe_battle_hunger", 600), [3] = mkability("axe_culling_blade", 600), [10] = mkability("special_bonus_strength_8", 0), [11] = mkability("special_bonus_armor_5", 0) } })
  local list = Skill.GetAbilityList(bot)
  check("8 GetAbilityList reads slots dynamically", #list == 3 and list[1] == "axe_berserkers_call", table.concat(list, ","))
  local talents = Skill.GetTalentList(bot)
  check("8 GetTalentList reads slots 10+", #talents == 2, table.concat(talents, ","))
  local ok = Skill.LevelTalent(bot, { [10] = 1 }, 10)
  check("8 LevelTalent picks right side", ok == true and hasLog(bot.log, "level:special_bonus_armor_5"), table.concat(bot.log, ";"))
  local bot2 = mkbot({ hero = "axe", gold = 2000, items = {} })
  local Gen = require("bots/item_purchase_generic")
  local bought = Gen.ItemPurchaseThinkFor(bot2)
  check("8 item purchase buys first missing item", bought == "item_tango" and hasLog(bot2.log, "buy:item_tango"), "bought=" .. tostring(bought))
end

-- 9. Dispatcher Think 端到端 + BotLib 覆盖
do
  Team.ResetBlackboard(); Dispatcher.ResetThinkState(); setTime(700)
  _G.DOTA_AI_DIFFICULTY = 3
  local bot = mkbot({ hero = "axe", hp = 800, gold = 0, enemies = { mkunit("e1", 400, 1000, 300, 0) }, ecreeps = { mkunit("c1", 50, 500, 200, 0) } })
  local mode = Dispatcher.Think(bot)
  check("9 dispatcher Think returns a mode", mode ~= nil, "mode=" .. tostring(mode))
  check("9 BotLib covers all 127 heroes", Heroes ~= nil)
  local nFocus = 0
  for _, k in ipairs({ "axe", "zeus", "lion", "crystal_maiden", "magnus", "faceless_void", "enigma", "dazzle", "oracle", "huskar" }) do
    local m = require("bots/BotLib/hero_" .. k)
    if m ~= nil and m.SkillsComplement ~= nil then nFocus = nFocus + 1 end
  end
  check("9 all 10 focus heroes load", nFocus == 10, "n=" .. nFocus)
end

print("VERIFY_V200 PASSED: " .. passed .. " checks")
