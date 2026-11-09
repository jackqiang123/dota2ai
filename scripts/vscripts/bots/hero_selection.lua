-- hero_selection.lua
-- 选人逻辑:按阵容补位,不抢位置、不重复分路。
-- 规则:已有 1/2 号位就补 3/4/5;已有 4/5 号位就补核心;缺控制补控制。
-- v1.1.0 新增选人协同:补位之外按 combos.lua 的经典组合加分,协同分最高的优先。
-- 本文件由游戏在选人阶段调用,函数名 Think() 是 Bot 选人 API 的约定入口。
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local Combos = require(GetScriptDirectory() .. "/data/combos")
local HeroKey = require(GetScriptDirectory() .. "/engine/hero_key")

local function alreadyPicked(picked, key)
  for _, k in ipairs(picked or {}) do
    if k == key then return true end
  end
  return false
end

local function teamPositions(picked)
  local pos = {}
  for _, k in ipairs(picked or {}) do
    local h = Heroes[k]
    if h ~= nil and h.positions ~= nil then
      for _, p in ipairs(h.positions) do pos[p] = true end
    end
  end
  return pos
end

-- 在候选列表里按协同分(高到低)排序,同分保持原 pool 顺序(稳定排序)。
local function sortBySynergy(picked, candidates)
  local scored = {}
  for i, key in ipairs(candidates) do
    scored[#scored + 1] = { key = key, synergy = Combos.TotalSynergy(picked, key), order = i }
  end
  table.sort(scored, function(a, b)
    if a.synergy ~= b.synergy then return a.synergy > b.synergy end
    return a.order < b.order
  end)
  local out = {}
  for _, s in ipairs(scored) do out[#out + 1] = s.key end
  return out
end

-- picked:己方已选英雄 key 列表;pool:可选 key 列表(由调用方传入)。
-- 返回一个 key,调用方负责执行选择。
-- 顺序:先按缺位 1->5 找,同一缺位内协同分最高的优先;全部位置都有了,
-- 在全部未选里协同分最高的优先。
-- 注意: 这个函数必须是 local、名字不能叫 SelectHero——Valve 选人 API 的
-- 全局函数就叫 SelectHero(nPlayerID, sHeroName), 本文件如果定义同名
-- 全局函数, 加载时会把 Valve 的 API 覆盖掉, Think() 里的 pcall(_G.SelectHero, ...)
-- 就会调到这个纯逻辑函数上 (传数字+字符串, pairs 报错被 pcall 吞掉),
-- 结果一个英雄都选不出去。2026-11-09 的 mock 测试当场抓到了这个问题。
local function pickHero(picked, pool)
  pool = pool or {}
  local pos = teamPositions(picked)
  -- 优先补缺的位置,按 1 -> 5 顺序找。
  for want = 1, 5 do
    if not pos[want] then
      local candidates = {}
      for _, key in ipairs(pool) do
        if not alreadyPicked(picked, key) then
          local h = Heroes[key]
          if h ~= nil and h.positions ~= nil then
            for _, p in ipairs(h.positions) do
              if p == want then candidates[#candidates + 1] = key break end
            end
          end
        end
      end
      if #candidates > 0 then
        return sortBySynergy(picked, candidates)[1]
      end
    end
  end
  -- 全部位置都有了,在未选里协同分最高的优先。
  local rest = {}
  for _, key in ipairs(pool) do
    if not alreadyPicked(picked, key) then rest[#rest + 1] = key end
  end
  if #rest > 0 then return sortBySynergy(picked, rest)[1] end
  return nil
end

-- 供游戏在选人阶段调用的 Think: 给己方还没选英雄的 Bot 实际选人。
-- Valve 约定 (Dota Bot Scripting): 选人调全局 SelectHero(nPlayerID, sHeroName),
-- sHeroName 必须是真内部名 (如 npc_dota_hero_zuus, 见 HeroKey.NpcName);
-- 是否已选查 GetSelectedHeroName(nPlayerID); 是否轮到该 Bot 查
-- IsPlayerInHeroSelectionControl(nPlayerID)。全部用 pcall 包住:
-- 任一 API 不可用时直接返回, 游戏会在选人时间到后给 Bot 随机英雄, 不会卡死。
-- 旧版 Think() 只算出一个 pick 存在 _G 里、从不调用 SelectHero, 真机里选人
-- 协同等于不存在, Bot 全靠游戏随机选人。
-- 只处理 AP 式选人; CM 的 ban/pick (CMBanHero/CMPickHero) 未实现, 见
-- tools/real-game/known-questions.md。
function Think()
  if GetTeam == nil or GetTeamPlayers == nil or _G.SelectHero == nil then return end
  local okTeam, team = pcall(GetTeam)
  if not okTeam or team == nil then return end
  local okPlayers, players = pcall(GetTeamPlayers, team)
  if not okPlayers or players == nil then return end
  -- 已选英雄 (两队都算, 避免重复选): npc 名 -> key。
  local pickedKeys = {}
  local function collect(teamId)
    if GetTeamPlayers == nil or GetSelectedHeroName == nil then return end
    local ok, ps = pcall(GetTeamPlayers, teamId)
    if not ok or ps == nil then return end
    for _, pid in ipairs(ps) do
      local okN, name = pcall(GetSelectedHeroName, pid)
      if okN and name ~= nil and name ~= "" then
        local k = HeroKey.FromUnitName(name)
        if k ~= nil then pickedKeys[k] = true end
      end
    end
  end
  collect(team)
  if GetOpposingTeam ~= nil then
    local okOpp, opp = pcall(GetOpposingTeam)
    if okOpp and opp ~= nil then collect(opp) end
  end
  local picked = {}
  for k, _ in pairs(pickedKeys) do picked[#picked + 1] = k end
  local pool = {}
  for key, _ in pairs(Heroes) do pool[#pool + 1] = key end
  table.sort(pool)
  for _, pid in ipairs(players) do
    local isBot = true
    if IsPlayerBot ~= nil then
      local okB, b = pcall(IsPlayerBot, pid)
      if okB then isBot = b end
    end
    if isBot then
      local inControl = true
      if IsPlayerInHeroSelectionControl ~= nil then
        local okC, c = pcall(IsPlayerInHeroSelectionControl, pid)
        if okC then inControl = c end
      end
      if inControl then
        local hasHero = false
        if GetSelectedHeroName ~= nil then
          local okN, name = pcall(GetSelectedHeroName, pid)
          if okN and name ~= nil and name ~= "" then hasHero = true end
        end
        if not hasHero then
          local pick = pickHero(picked, pool)
          if pick ~= nil then
            local npc = HeroKey.NpcName(pick)
            local okS = pcall(_G.SelectHero, pid, npc)
            if okS then
              picked[#picked + 1] = pick
              _G.DOTA_AI_LAST_PICK = pick
            end
          end
        end
      end
    end
  end
end

return {
  SelectHero = pickHero,
  TeamPositions = teamPositions,
  SortBySynergy = sortBySynergy,
}
