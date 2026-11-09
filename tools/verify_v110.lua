-- verify_v110.lua -- v1.1.0 独立验证测试(不是原来那个返回 nil 技能的弱 smoke)。
-- 每个修复都有一条对应的测试,技能 mock 必须带 IsNull()=false 等真实方法。
-- 用法(在仓库根目录): lua5.4 tools/verify_v110.lua
-- 退出码 0=全部通过;任一断言失败即报错退出,打印失败的测试名。
local _script = (arg and arg[0]) or "tools/verify_v110.lua"
local _root = _script:match("^(.*)/tools/verify_v110%.lua$") or "."
if _root == "" then _root = "." end
package.path = _root .. "/scripts/vscripts/?.lua;" .. _root .. "/scripts/vscripts/?/init.lua;" .. package.path

BOT_MODE_NONE = 0
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

-- ---- mock 工厂 ----
local function mkability(name, range, castable)
  return {
    GetAbilityName = function() return name end,
    IsPassive = function() return false end,
    IsFullyCastable = function() return castable ~= false end,
    CanAbilityBeUpgraded = function() return true end,
    GetCastRange = function() return range or 600 end,
    IsNull = function() return false end,
    IsAlive = function() return true end,
  }
end
local function mkitem(name)
  -- 真实 Dota 物品也是 ability 对象,有 GetAbilityName;mock 必须补上,否则
  -- Action_UseAbilityOnLocation 里的 a:GetAbilityName() 会报错。
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
-- opts: hero, hp, maxHp, x, y, level, gold, abilities={[slot]=ability}, items={[slot]=item},
--       enemies={units}, allies={units}, ecreeps={units}, acreeps={units}, towers={units},
--       courier, stash
local function mkbot(opts)
  opts = opts or {}
  local bot = {
    _id = opts.hero or "axe", log = {},
    _hp = opts.hp or 800, _maxHp = opts.maxHp or 1000,
    _x = opts.x or 0, _y = opts.y or 0,
    _level = opts.level or 5, _gold = opts.gold or 0,
    _abilities = opts.abilities or {}, _items = opts.items or {},
    _enemies = opts.enemies or {}, _allies = opts.allies or {},
    _ecreeps = opts.ecreeps or {}, _acreeps = opts.acreeps or {},
    _towers = opts.towers or {}, _courier = opts.courier, _stash = opts.stash,
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
  bot.Action_UseAbilityOnLocation_item = nil
  bot.Action_Courier = function(self, action) bot.log[#bot.log + 1] = "courier:" .. tostring(action) return true end
  -- 注意:物品(眼)也是经由 Action_UseAbilityOnLocation 发出,上面已覆盖。
  return bot
end
function GetBot() return nil end

local Core = require("bots/engine/core")
local Micro = require("bots/engine/micro")
local Team = require("bots/engine/team")
local Utility = require("bots/engine/utility")
local Macro = require("bots/engine/macro")
local Perception = require("bots/engine/perception")
local Heroes = require("bots/data/heroes")
local Combos = require("bots/data/combos")
local HeroSel = require("bots/hero_selection")

-- 1. channel 单体:Pudge 肢解 / Bane 蚀脑
do
  local enemy = mkunit("enemy1", 400, 1000, 300, 0)
  local bot = mkbot({ hero = "pudge", abilities = { [3] = mkability("pudge_dismember", 600) }, enemies = { enemy } })
  local snap = Perception.Snapshot(bot)
  check("1a pudge channel single-target casts", Micro.TryCastByType(bot, snap, Heroes["pudge"]) == true and hasLog(bot.log, "cast_entity:pudge_dismember->enemy1"), table.concat(bot.log, ";"))
  Team.ResetBlackboard(); setTime(102)
  local bot2 = mkbot({ hero = "bane", abilities = { [3] = mkability("bane_fiends_grip", 600) }, enemies = { enemy } })
  local snap2 = Perception.Snapshot(bot2)
  check("1b bane channel single-target casts", Micro.TryCastByType(bot2, snap2, Heroes["bane"]) == true and hasLog(bot2.log, "cast_entity:bane_fiends_grip->enemy1"), table.concat(bot2.log, ";"))
end
-- 1c. channel 范围:CM 极寒之拥 / 巫医死亡守卫
do
  local enemy = mkunit("enemy1", 400, 1000, 300, 0)
  Team.ResetBlackboard(); setTime(104)
  local bot = mkbot({ hero = "crystal_maiden", abilities = { [3] = mkability("crystal_maiden_freezing_field", 600) }, enemies = { enemy } })
  check("1c crystal_maiden channel AoE casts on location", Micro.TryCastByType(bot, Perception.Snapshot(bot), Heroes["crystal_maiden"]) == true and hasLog(bot.log, "cast_loc:crystal_maiden_freezing_field"), table.concat(bot.log, ";"))
  Team.ResetBlackboard(); setTime(106)
  local bot2 = mkbot({ hero = "witch_doctor", abilities = { [3] = mkability("witch_doctor_death_ward", 600) }, enemies = { enemy } })
  check("1d witch_doctor channel AoE casts on location", Micro.TryCastByType(bot2, Perception.Snapshot(bot2), Heroes["witch_doctor"]) == true and hasLog(bot2.log, "cast_loc:witch_doctor_death_ward"), table.concat(bot2.log, ";"))
end
-- 1e. summon:陈劝化(有敌方 / 无敌方都放)
do
  local enemy = mkunit("enemy1", 400, 1000, 300, 0)
  local bot = mkbot({ hero = "chen", abilities = { [1] = mkability("chen_holy_persuasion", 600) }, enemies = { enemy } })
  check("1e chen summon casts with enemy nearby", Micro.TryCastByType(bot, Perception.Snapshot(bot), Heroes["chen"]) == true and hasLog(bot.log, "cast_nontarget:chen_holy_persuasion"), table.concat(bot.log, ";"))
  local bot2 = mkbot({ hero = "chen", abilities = { [1] = mkability("chen_holy_persuasion", 600) }, enemies = {} })
  check("1f chen summon casts at game start with no enemy", Micro.TryCastByType(bot2, Perception.Snapshot(bot2), Heroes["chen"]) == true and hasLog(bot2.log, "cast_nontarget:chen_holy_persuasion"), table.concat(bot2.log, ";"))
end
-- 1g. 回归:斧王旧技能仍能放
do
  local enemy = mkunit("enemy1", 400, 1000, 300, 0)
  local bot = mkbot({ hero = "axe", abilities = { [0] = mkability("axe_berserkers_call", 600) }, enemies = { enemy } })
  check("1g axe old aoe_control still casts", Micro.TryCastByType(bot, Perception.Snapshot(bot), Heroes["axe"]) == true and hasLog(bot.log, "cast_loc:axe_berserkers_call"), table.concat(bot.log, ";"))
end
-- 1h. aura/passive 明确跳过;escape 按 blink 条件放
do
  local enemy = mkunit("enemy1", 200, 1000, 300, 0) -- 敌方残血 20%
  local fake = { key = "test", abilities = { { type = "aura" }, { type = "passive" } } }
  local bot = mkbot({ hero = "axe", abilities = { [0] = mkability("fake_aura", 600), [1] = mkability("fake_passive", 600) }, enemies = { enemy } })
  check("1h aura/passive are skipped, not cast", Micro.TryCastByType(bot, Perception.Snapshot(bot), fake) == false and #bot.log == 0, table.concat(bot.log, ";"))
  local fake2 = { key = "test", abilities = { { type = "escape" } } }
  local bot2 = mkbot({ hero = "axe", abilities = { [0] = mkability("fake_escape", 600) }, enemies = { enemy } })
  check("1i escape casts when chasing a low-hp enemy", Micro.TryCastByType(bot2, Perception.Snapshot(bot2), fake2) == true and hasLog(bot2.log, "cast_loc:fake_escape"), table.concat(bot2.log, ";"))
end

-- 2. thinkDelay 节流
do
  _G.DOTA_AI_DIFFICULTY = 1 -- easy 0.50s
  Core.ResetThinkState()
  local creep = mkunit("creep1", 50, 500, 200, 0)
  local bot = mkbot({ hero = "axe", x = 0, y = 0, ecreeps = { creep } })
  setTime(100); Core.Think(bot)
  local n1 = #bot.log
  check("2a easy first Think acts", n1 > 0, table.concat(bot.log, ";"))
  setTime(100.2); Core.Think(bot)
  check("2b easy second Think within 0.5s is throttled", #bot.log == n1, "log grew to " .. #bot.log)
  setTime(100.6); Core.Think(bot)
  check("2c easy Think after 0.5s acts again", #bot.log > n1, table.concat(bot.log, ";"))
  _G.DOTA_AI_DIFFICULTY = 3 -- hard 0.15s
  Core.ResetThinkState()
  local bot2 = mkbot({ hero = "axe", x = 0, y = 0, ecreeps = { creep } })
  setTime(200); Core.Think(bot2)
  local m1 = #bot2.log
  setTime(200.1); Core.Think(bot2)
  check("2d hard Think within 0.15s is throttled", #bot2.log == m1, "log grew to " .. #bot2.log)
  setTime(200.2); Core.Think(bot2)
  check("2e hard Think after 0.15s acts again", #bot2.log > m1, table.concat(bot2.log, ";"))
  _G.DOTA_AI_DIFFICULTY = 3
end

-- 3. 死代码接通:UpdateDeadEnemies -> Macro 打盾分;插眼分支
do
  Team.ResetBlackboard()
  setTime(1300)
  local snap = { numEnemies = 0, numAllies = 2, healthPct = 0.8, nearbyEnemyTowers = {} }
  local _, scores0 = Macro.Evaluate(nil, snap, Team.GetBlackboard())
  check("3a roshan score is 0 when deadEnemies is 0", scores0.roshan == 0, "roshan=" .. tostring(scores0.roshan))
  Team.UpdateDeadEnemies(3, 5) -- 可见 3 人 -> 推测减员 2
  check("3b UpdateDeadEnemies estimates 2 dead", Team.GetBlackboard().deadEnemies == 2)
  local _, scores1 = Macro.Evaluate(nil, snap, Team.GetBlackboard())
  check("3c roshan score rises when deadEnemies>=1", scores1.roshan >= 0.65, "roshan=" .. tostring(scores1.roshan))
  -- 插眼:5 号位戴泽,背包有眼,时间 100(ward 0.4 > farm 0.35,roam/push 均为 0)
  Team.ResetBlackboard(); Core.ResetThinkState()
  setTime(100)
  local bot = mkbot({ hero = "dazzle", items = { [0] = mkitem("item_ward_observer") }, enemies = {}, allies = {} })
  Core.Think(bot)
  check("3d ward branch places an observer ward", hasLog(bot.log, "cast_loc:item_ward_observer"), table.concat(bot.log, ";"))
end

-- 4. 加点与属性表
do
  -- 15 级不查询 -1 槽位
  local queried = {}
  local bot = mkbot({ hero = "axe", level = 15 })
  bot.GetAbilityInSlot = function(self, i) queried[#queried + 1] = i return nil end
  bot.Action_LevelAbility = function(self, n) bot.log[#bot.log + 1] = "level:" .. n end
  _G.GetBot = function() return bot end
  dofile(_root .. "/scripts/vscripts/bots/ability_item_usage_axe.lua")
  local ok, err = pcall(AbilityLevelUpThink)
  local sawMinus1 = false
  for _, s in ipairs(queried) do if s == -1 then sawMinus1 = true end end
  check("4a level-15 level-up does not query slot -1 and does not crash", ok and not sawMinus1 and not hasLog(bot.log, "level:"), "queried=" .. table.concat(queried, ",") .. " log=" .. table.concat(bot.log, ";"))
  -- 6 级正常升级大招(正向对照)
  local bot2 = mkbot({ hero = "axe", level = 6 })
  bot2.GetAbilityInSlot = function(self, i) if i == 3 then return mkability("axe_culling_blade", 0) end return nil end
  bot2.Action_LevelAbility = function(self, n) bot2.log[#bot2.log + 1] = "level:" .. n end
  _G.GetBot = function() return bot2 end
  dofile(_root .. "/scripts/vscripts/bots/ability_item_usage_axe.lua")
  pcall(AbilityLevelUpThink)
  check("4b level-6 level-up still levels the ultimate", hasLog(bot2.log, "level:axe_culling_blade"), table.concat(bot2.log, ";"))
  -- Invoker 加点
  local inv = Heroes["invoker"]
  local counts = {}
  for _, s in ipairs(inv.skill_build) do counts[s] = (counts[s] or 0) + 1 end
  check("4c invoker skill_build is 25 long, Quas/Wex/Exort 7 each, Invoke 4", #inv.skill_build == 25 and counts[1] == 7 and counts[2] == 7 and counts[3] == 7 and counts[4] == 4, "counts=" .. tostring(counts[1]) .. "/" .. tostring(counts[2]) .. "/" .. tostring(counts[3]) .. "/" .. tostring(counts[4]))
  check("4d invoker levels Invoke at level 2", inv.skill_build[2] == 4, "lvl2=" .. tostring(inv.skill_build[2]))
  -- 主属性计数
  local ac = {}
  for _, h in pairs(Heroes) do ac[h.primary_attr] = (ac[h.primary_attr] or 0) + 1 end
  check("4e primary_attr counts are 36/35/34/22", ac.str == 36 and ac.agi == 35 and ac.int == 34 and ac.universal == 22, "str=" .. tostring(ac.str) .. " agi=" .. tostring(ac.agi) .. " int=" .. tostring(ac.int) .. " universal=" .. tostring(ac.universal))
  check("4f largo is a strength support (4/5, support lane)", Heroes["largo"].primary_attr == "str" and Heroes["largo"].positions[1] == 4 and Heroes["largo"].positions[2] == 5 and Heroes["largo"].lane == "support", "pos=" .. table.concat(Heroes["largo"].positions, ",") .. " lane=" .. Heroes["largo"].lane)
end

-- 5. 英雄互动
do
  -- 5a. 连招窗口提升参团分
  Team.ResetBlackboard()
  setTime(1000)
  local enemy = mkunit("enemy1", 800, 1000, 300, 0)
  local ally = mkunit("ally1", 900, 1000, -200, 0)
  local bot = mkbot({ hero = "zeus", hp = 900, enemies = { enemy }, allies = { ally } })
  local snap = Perception.Snapshot(bot)
  local _, best0 = Utility.Score(bot, snap, Heroes["zeus"], 1000)
  local scores0, _ = Utility.Score(bot, snap, Heroes["zeus"], 1000)
  local enigmaBot = mkbot({ hero = "enigma" })
  Team.ReportComboWindow(enigmaBot, { x = 300, y = 0, z = 0 })
  local scores1, best1 = Utility.Score(bot, snap, Heroes["zeus"], 1000)
  check("5a combo window raises teamfight score", scores1.teamfight > scores0.teamfight, "before=" .. tostring(scores0.teamfight) .. " after=" .. tostring(scores1.teamfight))
  check("5a2 combo window makes teamfight the best action", best1 == "teamfight", "best=" .. tostring(best1))
  -- 5b. 连招窗口:另一个 Bot 走向窗口位置
  Team.ResetBlackboard(); Core.ResetThinkState()
  setTime(1000)
  Team.ReportComboWindow(enigmaBot, { x = 300, y = 0, z = 0 })
  local bot2 = mkbot({ hero = "zeus", hp = 900, x = 2000, y = 2000, enemies = { enemy }, allies = { ally } })
  Core.Think(bot2)
  check("5b teammate walks to the combo window location", hasLog(bot2.log, "move:300,0"), table.concat(bot2.log, ";"))
  -- 5c. 集火:全队共享最低血量目标
  Team.ResetBlackboard()
  local nearFull = mkunit("nearFull", 800, 1000, 200, 0)
  local farLow = mkunit("farLow", 200, 1000, 800, 0)
  local snapF = { nearbyEnemies = { nearFull, farLow } }
  local focus = Team.GetFocusTarget(snapF)
  check("5c focus target is the lowest-hp enemy, not the nearest", focus == farLow, "focus=" .. tostring(focus and focus._id))
  -- Core 团战打集火目标而不是最近目标
  Team.ResetBlackboard(); Core.ResetThinkState()
  setTime(1000)
  local bot3 = mkbot({ hero = "zeus", hp = 900, x = 0, y = 0, enemies = { nearFull, farLow }, allies = { ally } })
  Core.Think(bot3)
  check("5d core teamfight attacks the focus target", hasLog(bot3.log, "attack:farLow"), table.concat(bot3.log, ";"))
  -- 5e. 救人:戴泽 / 神谕者先救人不先打人
  local hurtAlly = mkunit("allyLow", 300, 1000, -200, 0)
  local botD = mkbot({ hero = "dazzle", abilities = { [1] = mkability("dazzle_shallow_grave", 600), [2] = mkability("dazzle_shadow_wave", 600) }, enemies = { enemy }, allies = { hurtAlly } })
  local okD = Micro.TryCastByType(botD, Perception.Snapshot(botD), Heroes["dazzle"])
  check("5e dazzle rescues the low-hp ally instead of attacking", okD and hasLog(botD.log, "->allyLow"), table.concat(botD.log, ";"))
  local botO = mkbot({ hero = "oracle", abilities = { [0] = mkability("oracle_fates_edict", 600) }, enemies = { enemy }, allies = { hurtAlly } })
  local okO = Micro.TryCastByType(botO, Perception.Snapshot(botO), Heroes["oracle"])
  check("5f oracle rescues the low-hp ally instead of attacking", okO and hasLog(botO.log, "->allyLow"), table.concat(botO.log, ";"))
  -- 5g. 选人协同:已选 Magnus 时优先 Faceless Void
  local pick = HeroSel.SelectHero({ "magnus" }, { "sniper", "faceless_void", "axe" })
  check("5g draft with Magnus picks Faceless Void over Sniper", pick == "faceless_void", "pick=" .. tostring(pick))
  check("5h synergy table has at least 12 combos", #Combos.COMBOS >= 12, "combos=" .. #Combos.COMBOS)
  check("5i synergy score Magnus+Faceless Void is 10", Combos.SynergyScore("magnus", "faceless_void") == 10)
  -- 5j. 防重叠:窗口开启 2 秒内不重复放同类先手大,2 秒后可放
  Team.ResetBlackboard()
  setTime(100)
  Team.ReportComboWindow(enigmaBot, { x = 300, y = 0, z = 0 })
  local fv = mkbot({ hero = "faceless_void", abilities = { [2] = mkability("faceless_void_time_dilation", 600, false), [3] = mkability("faceless_void_chronosphere", 600) }, enemies = { enemy } })
  setTime(100.5)
  local held = Micro.TryCastByType(fv, Perception.Snapshot(fv), Heroes["faceless_void"])
  check("5j ult is held within 2s of another caster's combo window", held == false and not hasLog(fv.log, "chronosphere"), table.concat(fv.log, ";"))
  setTime(103)
  Perception.Invalidate(fv)
  local casted = Micro.TryCastByType(fv, Perception.Snapshot(fv), Heroes["faceless_void"])
  check("5k ult may follow up after the 2s hold (window still <5s)", casted == true and hasLog(fv.log, "chronosphere"), table.concat(fv.log, ";"))
  -- 5l. 先手大招上报连招窗口
  Team.ResetBlackboard()
  setTime(200)
  local eni = mkbot({ hero = "enigma", abilities = { [0] = mkability("enigma_malefice", 600, false), [1] = mkability("enigma_demonic_conversion", 600, false), [3] = mkability("enigma_black_hole", 600) }, enemies = { enemy } })
  local okC = Micro.TryCastByType(eni, Perception.Snapshot(eni), Heroes["enigma"])
  check("5l casting Black Hole reports a combo window", okC and Team.IsComboWindowActive() and Team.GetComboWindow().caster == "npc_dota_hero_enigma", "ok=" .. tostring(okC))
end

-- 6. 信使
do
  local courier = { _id = "courier" }
  local bot = mkbot({ hero = "axe", courier = courier, stash = 2 })
  check("6a courier delivers when stash has items", Micro.TryDeliverCourier(bot) == true and hasLog(bot.log, "courier:"), table.concat(bot.log, ";"))
  local bot2 = mkbot({ hero = "axe", courier = nil, stash = 0 })
  local ok, err = pcall(function() return Micro.TryDeliverCourier(bot2) end)
  check("6b no courier is a silent no-op, not an error", ok and Micro.TryDeliverCourier(bot2) == false, "err=" .. tostring(err))
  local bot3 = mkbot({ hero = "axe", courier = courier, stash = 0 })
  check("6c empty stash does not trigger a delivery", Micro.TryDeliverCourier(bot3) == false, table.concat(bot3.log, ";"))
end

print("VERIFY_V110 PASSED: " .. passed .. " checks")
