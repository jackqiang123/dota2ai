-- mode_dispatcher.lua
-- v2.0.0 Mode 分发器: Valve 原生 Mode 系统的中央调度。
-- 每帧: TeamThink() 先跑 -> 感知快照 -> 对全部 Mode 调 GetDesire() -> 分数最高的
-- 模式的 Think() 才跑, 其余模式本帧不执行。模式切换时调新模式的 OnStart()。
-- thinkDelay 按难度节流决策 (买装 / 信使除外, 见 Core 旧逻辑的保留)。
local ModeDispatcher = {}

local Perception = require(GetScriptDirectory() .. "/engine/perception")
local Utility = require(GetScriptDirectory() .. "/engine/utility")
local Team = require(GetScriptDirectory() .. "/engine/team")
local HeroKey = require(GetScriptDirectory() .. "/engine/hero_key")

ModeDispatcher.MODE_FILES = {
  "laning", "farm", "push", "push_tower_mid", "push_tower_bot", "push_tower_top",
  "retreat", "attack", "roam", "team_roam", "roshan", "ward",
  "defend_tower", "rune", "secret_shop",
}
ModeDispatcher.MODE_NAMES = {
  laning = "mode_laning_generic",
  farm = "mode_farm_generic",
  push = "mode_push_generic",
  push_tower_mid = "mode_push_tower_mid_generic",
  push_tower_bot = "mode_push_tower_bot_generic",
  push_tower_top = "mode_push_tower_top_generic",
  retreat = "mode_retreat_generic",
  attack = "mode_attack_generic",
  roam = "mode_roam_generic",
  team_roam = "mode_team_roam_generic",
  roshan = "mode_roshan_generic",
  ward = "mode_ward_generic",
  defend_tower = "mode_defend_tower_generic",
  rune = "mode_rune_generic",
  secret_shop = "mode_secret_shop_generic",
}

local _modes = nil
local _lastThink = {}
local _currentMode = {}

local function gameTime()
  if DotaTime ~= nil then
    local ok, t = pcall(DotaTime)
    if ok and type(t) == "number" then return t end
  end
  return 0
end

local function botKey(bot)
  -- 唯一键: 优先 PlayerID。按英雄名索引会在同名英雄分属两队时撞键:
  -- 模拟里所有 Bot 共用一个 Lua 状态, _lastThink/_currentMode 被互相覆盖,
  -- 第二个同名英雄每 tick 都被 thinkDelay 节流、Think 永远不执行 (实测 Dire
  -- Sven 走到拐角后永久冻结, 而 Radiant Sven 正常)。真机每个 Bot 独立 VM
  -- 不会撞; 模拟里必须按实例区分。
  local ok, pid = pcall(function() return bot:GetPlayerID() end)
  if ok and pid ~= nil then return "pid:" .. tostring(pid) end
  local ok2, name = pcall(function() return bot:GetUnitName() end)
  if ok2 and name ~= nil and name ~= "" then return name end
  return tostring(bot)
end

function ModeDispatcher.ResetThinkState()
  _lastThink = {}
  _currentMode = {}
  _modes = nil
end

function ModeDispatcher.LoadModes()
  if _modes ~= nil then return _modes end
  _modes = {}
  for _, key in ipairs(ModeDispatcher.MODE_FILES) do
    local fname = ModeDispatcher.MODE_NAMES[key]
    local ok, mod = pcall(require, GetScriptDirectory() .. "/" .. fname)
    if ok and mod ~= nil then _modes[key] = mod end
  end
  return _modes
end

-- 对全部模式算 Desire, 返回最高分模式名 / 分数表 / 模式表。
function ModeDispatcher.SelectMode(bot, snap, bb)
  local modes = ModeDispatcher.LoadModes()
  local best, bestScore, scores = nil, -1, {}
  for _, key in ipairs(ModeDispatcher.MODE_FILES) do
    local mod = modes[key]
    if mod ~= nil and mod.GetDesire ~= nil then
      local ok, d = pcall(mod.GetDesire, bot, snap, bb)
      if ok and type(d) == "number" then
        if d < 0 then d = 0 end
        if d > 1 then d = 1 end
        scores[key] = d
        if d > bestScore then best, bestScore = key, d end
      else
        scores[key] = 0
      end
    else
      scores[key] = 0
    end
  end
  return best, scores, modes[best]
end

-- 主入口: 供 bot_generic.lua 的 Think() 调用。
function ModeDispatcher.Think(bot)
  if bot == nil then return nil end
  local okNull, isNull = pcall(function() return bot:IsNull() end)
  if okNull and isNull then return nil end
  local okAlive, alive = pcall(function() return bot:IsAlive() end)
  if okAlive and not alive then return nil end
  local snap = Perception.Snapshot(bot)
  if snap == nil then return nil end
  local bb = Team.GetBlackboard()
  Team.TeamThink(bot, snap, bb)
  local key = botKey(bot)
  if not _modes then ModeDispatcher.LoadModes() end
  -- 买装不占决策帧 (Valve 的 ItemPurchaseThink 是独立入口, 这里顺带跑一次不冲突)。
  local okBuy, Micro = pcall(require, GetScriptDirectory() .. "/engine/micro")
  if okBuy and Micro ~= nil then
    local Heroes = require(GetScriptDirectory() .. "/data/heroes")
    local okName, name = pcall(function() return bot:GetUnitName() end)
    if okName and name ~= nil then
      local hkey = HeroKey.FromUnitName(name)
      if hkey ~= nil then Micro.TryBuyNextItem(bot, Heroes[hkey]) end
      Micro.TryDeliverCourier(bot)
    end
  end
  local t = gameTime()
  local diff = Utility.GetDifficulty(bot)
  if t > 0 then
    local last = _lastThink[key]
    if last ~= nil and (t - last) < (diff.thinkDelay or 0) then return _currentMode[key] end
    _lastThink[key] = t
  end
  local best, scores, mod = ModeDispatcher.SelectMode(bot, snap, bb)
  if best == nil or mod == nil then return nil end
  if _currentMode[key] ~= best then
    if mod.OnStart ~= nil then pcall(mod.OnStart, bot) end
    _currentMode[key] = best
  end
  if mod.Think ~= nil then pcall(mod.Think, bot, snap, bb) end
  return best
end

return ModeDispatcher
