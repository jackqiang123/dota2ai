-- hero_selection.lua
-- 选人逻辑:按阵容补位,不抢位置、不重复分路。
-- 规则:已有 1/2 号位就补 3/4/5;已有 4/5 号位就补核心;缺控制补控制。
-- v1.1.0 新增选人协同:补位之外按 combos.lua 的经典组合加分,协同分最高的优先。
-- 本文件由游戏在选人阶段调用,函数名 Think() 是 Bot 选人 API 的约定入口。
local Heroes = require("bots/data/heroes")
local Combos = require("bots/data/combos")

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
function SelectHero(picked, pool)
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

-- 供游戏调用的选人 Think:遍历全英雄池,按补位选。
-- 注意:不同模式的选人 API 入口可能不同,本函数为可复用的纯逻辑,
-- 实际接入时由 bot_generic / 房间脚本按模式调用 SelectHero()。
function Think()
  local pool = {}
  for key, _ in pairs(Heroes) do pool[#pool + 1] = key end
  table.sort(pool)
  local pick = SelectHero({}, pool)
  -- 不在这里直接调用 SelectHero  API(不同模式入口不同),
  -- 调用方拿到 pick 后自行执行选择。
  _G.DOTA_AI_LAST_PICK = pick
end

return {
  SelectHero = SelectHero,
  TeamPositions = teamPositions,
  SortBySynergy = sortBySynergy,
}
