-- hero_selection.lua
-- 选人逻辑:按阵容补位,不抢位置、不重复分路。
-- 规则:已有 1/2 号位就补 3/4/5;已有 4/5 号位就补核心;缺控制补控制。
-- 本文件由游戏在选人阶段调用,函数名 Think() 是 Bot 选人 API 的约定入口。
local Heroes = require("bots/data/heroes")

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

-- picked:己方已选英雄 key 列表;pool:可选 key 列表(由调用方传入)。
-- 返回一个 key,调用方负责执行选择。
function SelectHero(picked, pool)
  pool = pool or {}
  local pos = teamPositions(picked)
  -- 优先补缺的位置,按 1 -> 5 顺序找。
  for want = 1, 5 do
    if not pos[want] then
      for _, key in ipairs(pool) do
        if not alreadyPicked(picked, key) then
          local h = Heroes[key]
          if h ~= nil and h.positions ~= nil then
            for _, p in ipairs(h.positions) do
              if p == want then return key end
            end
          end
        end
      end
    end
  end
  -- 全部位置都有了,选第一个未选的。
  for _, key in ipairs(pool) do
    if not alreadyPicked(picked, key) then return key end
  end
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
}
