-- combos.lua -- 英雄互动数据:经典组合、连招先手英雄、救人英雄。
-- v1.1.0 新增。事实来源:经典 Dota 2 组合打法(公开常识),每组写清配合方式。
-- 本文件不依赖任何引擎模块,engine/micro.lua、engine/team.lua、hero_selection.lua 都可 require 它。
local Combos = {}

-- 经典组合:每组 { a=英雄key, b=英雄key, score=协同分(0-10), desc=配合方式 }。
-- 至少 12 组,此处 14 组。a/b 顺序无关,SynergyScore 会双向匹配。
Combos.COMBOS = {
  { a = "magnus",        b = "faceless_void",   score = 10, desc = "马格纳斯聚怪(RP)接虚空假面时间结界,圈内 AoE 打满" },
  { a = "magnus",        b = "enigma",          score = 10, desc = "马格纳斯聚怪接谜团黑洞,双团控不重叠、先后手衔接" },
  { a = "magnus",        b = "sven",            score = 8,  desc = "马格纳斯聚怪接斯温神之力量横扫,力量核收割" },
  { a = "io",            b = "tiny",            score = 10, desc = "艾欧牵引小小:移速+减伤,小小带艾欧全球飞、丢人" },
  { a = "io",            b = "chaos_knight",    score = 9,  desc = "艾欧牵引混沌骑士:幻象大军共享牵引攻速与减伤" },
  { a = "io",            b = "spectre",         score = 8,  desc = "艾欧+幽鬼双全球:幽鬼大招降临、艾欧跟飞支援" },
  { a = "dark_seer",     b = "enigma",          score = 9,  desc = "黑暗贤者真空拉人接谜团黑洞,墙+黑洞双 AoE" },
  { a = "dark_seer",     b = "faceless_void",   score = 9,  desc = "黑暗贤者真空拉人接虚空时间结界,聚怪后定住" },
  { a = "dark_seer",     b = "tidehunter",      score = 8,  desc = "黑暗贤者真空拉人接潮汐毁灭,离子外壳+大招清场" },
  { a = "oracle",        b = "huskar",          score = 10, desc = "神谕者虚妄之诺保哈斯卡:残血不死、活血之泉回满" },
  { a = "dazzle",        b = "huskar",          score = 10, desc = "戴泽薄葬保哈斯卡:残血 5 秒不死,活血之泉持续输出" },
  { a = "enigma",        b = "jakiro",          score = 8,  desc = "谜团黑洞接杰奇洛冰火交加,黑洞里吃满双火" },
  { a = "enigma",        b = "crystal_maiden",  score = 8,  desc = "谜团黑洞接冰女极寒之拥,黑洞里吃满大招" },
  { a = "faceless_void", b = "lina",            score = 8,  desc = "虚空时间结界接莉娜神灭斩,圈内单点秒杀" },
}

-- 先手大招英雄:放出 aoe_control / channel 类大招时会开连招窗口(见 team.lua)。
-- key -> true。只列大招是团控的英雄,不是所有带 aoe_control 的英雄。
Combos.COMBO_INITIATORS = {
  enigma = true, faceless_void = true, tidehunter = true, magnus = true,
  earthshaker = true, dark_seer = true, mars = true, sand_king = true,
  axe = true, elder_titan = true, underlord = true, jakiro = true,
}

-- 救人英雄:有 heal/buff 类救人技能,残血队友优先于进攻(见 micro.lua)。
-- key -> true。戴泽薄葬、神谕者大、亚巴顿盾、艾欧牵引等。
Combos.RESCUE_HEROES = {
  dazzle = true, oracle = true, abaddon = true, io = true,
  omniknight = true, winter_wyvern = true, treant_protector = true,
  enchantress = true, chen = true, warlock = true, witch_doctor = true,
  shadow_demon = true, keeper_of_the_light = true,
}

-- 双向协同分:picked 与 candidate 是同一组组合返回 score,否则 0。
function Combos.SynergyScore(picked, candidate)
  if picked == nil or candidate == nil or picked == candidate then return 0 end
  local best = 0
  for _, c in ipairs(Combos.COMBOS) do
    if (c.a == picked and c.b == candidate) or (c.a == candidate and c.b == picked) then
      if c.score > best then best = c.score end
    end
  end
  return best
end

-- 给定已选列表,候选英雄的总协同分(对每个已选英雄求和)。
function Combos.TotalSynergy(pickedList, candidate)
  local total = 0
  for _, p in ipairs(pickedList or {}) do
    total = total + Combos.SynergyScore(p, candidate)
  end
  return total
end

return Combos
