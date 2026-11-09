# -*- coding: utf-8 -*-
"""生成器 v3.0.0: 读 tools/heroes_data.py + tools/all_heroes.py (127 全量),
产出 data/heroes.lua + data/talents.lua + 每个英雄 3 个 wrapper + BotLib/hero_<name>.lua。
可复现: 改 tools/ 下的数据文件后重新跑本脚本即可随版本更新,
跑完 git diff 应为 0 (除非数据改了)。
用法: python3 tools/generate.py [--root ~/workspace/dota2-ai]
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from heroes_data import HEROES  # noqa: E402
from focus_heroes import FOCUS  # noqa: E402
from all_heroes import ALL  # noqa: E402

ROLE_EARLY = {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_magic_wand"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_magic_wand"],
    3: ["item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_magic_wand"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots"],
}
ROLE_LATE = {
    1: ["item_butterfly", "item_satanic", "item_abyssal_blade"],
    2: ["item_octarine_core", "item_black_king_bar", "item_scythe_of_vyse"],
    3: ["item_shivas_guard", "item_black_king_bar", "item_assault"],
    4: ["item_aghanims_scepter", "item_black_king_bar", "item_lotus_orb"],
    5: ["item_aghanims_scepter", "item_force_staff", "item_glimmer_cape"],
}
SITUATIONAL = ["item_black_king_bar", "item_linkens_sphere", "item_scythe_of_vyse", "item_nullifier", "item_monkey_king_bar"]
SELL_LIST = ["item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"]
# 分位置卖出表 (v3.0.0; item_purchase_generic.lua 目前只读 sBuyList,
# sSellList / sSellListByPos 为数据预留, 购买状态机尚未消费)。
SELL_LISTS = {
    1: ["item_tango", "item_flask", "item_quelling_blade", "item_wraith_band"],
    2: ["item_tango", "item_flask", "item_null_talisman", "item_bottle"],
    3: ["item_tango", "item_flask", "item_bracer"],
    4: ["item_tango", "item_flask", "item_clarity", "item_ward_observer"],
    5: ["item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand"],
}

# v3.3.0: Valve 内部英雄名 (npc_dota_hero_<internal>) 与本项目 key 不同的 19 个英雄。
# 其余 108 个内部名 == key。事实来源 (两处独立核对一致):
#  - Liquipedia Cheats 页的 Hero Code Name 列表 (https://liquipedia.net/dota2/Cheats)
#  - skadistats/skadi wiki 的 npc_heroes.txt / WebAPI 清单 (Hero Names and IDs)
# 旧版 npc_name 一律写成 npc_dota_hero_<key>, 导致真机里这 19 个英雄的
# bot_<internal>.lua / ability_item_usage_<internal>.lua 永远加载不到,
# 且所有按 GetUnitName() 查表的地方 (出装/技能/加点/分路) 全部 miss,
# 英雄在真机里不会放技能、不会买装、不会点技能、默认挤中路。
# npc_name 是唯一事实来源, engine/hero_key.lua 只做反查, 不另存一份表。
INTERNAL_NAME = {
    "anti_mage": "antimage",
    "centaur_warrunner": "centaur",
    "clockwerk": "rattletrap",
    "doom": "doom_bringer",
    "io": "wisp",
    "lifestealer": "life_stealer",
    "magnus": "magnataur",
    "natures_prophet": "furion",
    "necrophos": "necrolyte",
    "outworld_destroyer": "obsidian_destroyer",
    "queen_of_pain": "queenofpain",
    "shadow_fiend": "nevermore",
    "timbersaw": "shredder",
    "treant_protector": "treant",
    "underlord": "abyssal_underlord",
    "vengeful_spirit": "vengefulspirit",
    "windranger": "windrunner",
    "wraith_king": "skeleton_king",
    "zeus": "zuus",
}


def dedup(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


INVOKER_SKILL_BUILD = [1, 4, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 4, 4, 2]


def skill_build(priority, n_abilities):
    """生成 1-25 级加点表: 6/12/18 点大招 (7.00 起大招等级要求为 6/12/18,
    旧版 6/11/16 是 7.00 前规则), 其余按优先级点满 (每技能最多 4 级)。
    Invoker(6 个技能位)用显式表。全部技能满级后的等级填 0 (天赋级)。"""
    if n_abilities > 4:
        return list(INVOKER_SKILL_BUILD)
    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    build = []
    pi = 0
    for lvl in range(1, 26):
        if lvl in (6, 12, 18):
            pick = 4
        else:
            pick = None
            for _ in range(len(priority)):
                cand = priority[pi % len(priority)]
                pi += 1
                if counts[cand] < 4:
                    pick = cand
                    break
            if pick is None:
                build.append(0)
                continue
        counts[pick] += 1
        build.append(pick)
    return build


def lua_str_list(items):
    return "{" + ", ".join('"%s"' % x for x in items) + "}"


def lua_int_list(items):
    return "{" + ", ".join(str(x) for x in items) + "}"


def talent_lua(t):
    parts = []
    for tier in (10, 15, 20, 25):
        parts.append("[%d] = %d" % (tier, t[tier]))
    return "{ " + ", ".join(parts) + " }"


def buy_lists(key, hero):
    """返回 {pos: [>=8 件]}。v3.0.0: 全部 127 个英雄都用 tools/all_heroes.py
    里按位置写的出装表 (五个位置互不相同, 主位置 >=12 件)。"""
    data = ALL[key]
    out = {}
    for pos in (1, 2, 3, 4, 5):
        lst = data["items"].get(pos)
        assert lst and len(lst) >= 8, "%s pos_%d items < 8" % (key, pos)
        out[pos] = list(lst)
    assert len(set(tuple(v) for v in out.values())) == 5, "%s buy lists not distinct" % key
    return out


def _skills_complement_lines(try_list):
    """生成 SkillsComplement() 的 Lua 代码行。
    try_list: [(fn_name, kind, key)] 按顺序尝试, desire >= 0.5 且
    Skill.Cast 成功即返回 true; 全部失败返回 false (wrapper 再走
    Micro.TryCastByType 兜底, 目标触发率 0)。
    kind == "slot": 按 X.ABILITIES[slot] 取技能 (Q/W/E/R);
    kind == "name": 按完整内部名取技能 (Invoker 的 invoked 技能)。"""
    L = []
    L.append("function X.SkillsComplement(bot, snap)")
    L.append("  if bot == nil or snap == nil then return false end")
    L.append("  local ab = Skill.GetAbilityMap(bot)")
    for fn_name, kind, key in try_list:
        L.append("  do")
        L.append("    local fn = X[\"%s\"]" % fn_name)
        L.append("    if fn ~= nil then")
        L.append("      local desire, target, castType = fn(bot, snap, ab)")
        L.append("      if desire ~= nil and desire >= 0.5 then")
        if kind == "name":
            L.append("        local ability = ab[\"%s\"]" % key)
        else:
            L.append("        local ability = ab[X.ABILITIES[\"%s\"]]" % key)
        L.append("        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then")
        if kind == "slot" and key == "R":
            L.append("          local loc = nil")
            L.append("          if target ~= nil then local ok, l = pcall(function() return target:GetLocation() end) if ok then loc = l end end")
            L.append("          if loc ~= nil then Team.ReportComboWindow(bot, loc) end")
        L.append("          return true")
        L.append("        end")
        L.append("      end")
        L.append("    end")
        L.append("  end")
    L.append("  return false")
    L.append("end")
    return L


def _fn_name_for_invoked(spell):
    # invoker_cold_snap -> ConsiderInvokerColdSnap
    parts = spell.split("_")[1:]
    return "ConsiderInvoker" + "".join(p.capitalize() for p in parts)


def botlib_text(key, hero):
    _k, en, cn, attr, positions, lane, ab_types, prio, sig = hero
    data = ALL[key]
    build = skill_build(prio, len(ab_types))
    talents = data["talents"]
    buys = buy_lists(key, hero)
    lines = []
    lines.append("-- hero_%s.lua -- %s %s -- v3.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。\n-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):\n-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。\n-- v3.0.0: 127 个英雄全部有真实 Consider 逻辑 (见 tools/all_heroes.py);\n-- fallback 只作兜底: SkillsComplement 全返回 0 时 ability_item_usage wrapper 才走\n-- Micro.TryCastByType, 触发率目标为 0。" % (key, en, cn))
    if data.get("limitations"):
        for lim_line in str(data["limitations"]).split("\n"):
            lines.append("-- 限制: %s" % lim_line)
    lines.append('local Skill = require(GetScriptDirectory() .. "/engine/skill")')
    lines.append('local Micro = require(GetScriptDirectory() .. "/engine/micro")')
    lines.append('local Team = require(GetScriptDirectory() .. "/engine/team")')
    lines.append('local Heroes = require(GetScriptDirectory() .. "/data/heroes")')
    lines.append("local X = {}")
    lines.append('X.KEY = "%s"' % key)
    lines.append("X.TALENTS = %s" % talent_lua(talents))
    lines.append("X.SKILL_BUILD = %s" % lua_int_list(build))
    lines.append("X.sBuyList = {}")
    for pos in (1, 2, 3, 4, 5):
        lines.append('X.sBuyList["pos_%d"] = %s' % (pos, lua_str_list(buys[pos])))
    lines.append("X.sSellList = %s" % lua_str_list(SELL_LIST))
    lines.append("X.sSellListByPos = {}")
    for pos in (1, 2, 3, 4, 5):
        lines.append('X.sSellListByPos["pos_%d"] = %s' % (pos, lua_str_list(SELL_LISTS[pos])))
    ab = data["abilities"]
    lines.append("X.ABILITIES = { Q = \"%s\", W = \"%s\", E = \"%s\", R = \"%s\" }" % (ab["Q"], ab["W"], ab["E"], ab["R"]))
    for slot in ("Q", "W", "E", "R"):
        body = data["consider"][slot]
        lines.append("function X.Consider%s(bot, snap, ab)\n%s\nend" % (slot, body))
    if data.get("invoked"):
        # Invoker: Q/W/E 是被动球 (Consider 只返回 0), R Invoke 只做可用性检查;
        # 真正的施法逻辑在 8 个 invoked 技能的 ConsiderInvoker* 里。
        lines.append("-- Invoker: 球 Quas/Wex/Exort 为被动, 不施放; Invoke(R) 只检查可用性。")
        lines.append("-- 调用技能按球组合生成, 每次最多持有 2 个; 本表建模 8 个常用 invoked 技能。")
        invoked = data["invoked"]
        fn_names = []
        for spell in sorted(invoked.keys()):
            fn = _fn_name_for_invoked(spell)
            fn_names.append(fn)
            lines.append("function X.%s(bot, snap, ab)\n%s\nend" % (fn, invoked[spell]))
        lines.append("X.INVOKED = %s" % lua_str_list(sorted(invoked.keys())))
        try_list = [(fn, "name", spell) for fn, spell in zip(fn_names, sorted(invoked.keys()))]
        try_list += [("ConsiderR", "slot", "R"), ("ConsiderQ", "slot", "Q"), ("ConsiderW", "slot", "W"), ("ConsiderE", "slot", "E")]
        lines.extend(_skills_complement_lines(try_list))
    else:
        lines.extend(_skills_complement_lines([("ConsiderR", "slot", "R"), ("ConsiderQ", "slot", "Q"), ("ConsiderW", "slot", "W"), ("ConsiderE", "slot", "E")]))
    lines.append("return X")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parents[1]))
    args = ap.parse_args()
    root = pathlib.Path(args.root)
    bots = root / "scripts" / "vscripts" / "bots"
    data_dir = bots / "data"
    botlib_dir = bots / "BotLib"
    data_dir.mkdir(parents=True, exist_ok=True)
    botlib_dir.mkdir(parents=True, exist_ok=True)

    # ---- data/heroes.lua ----
    lines = []
    lines.append("-- heroes.lua -- 由 tools/generate.py 从 tools/heroes_data.py 生成,不要手改。")
    lines.append("-- 事实来源:tools/heroes_data.py。版本基准:7.41f,127 名英雄。")
    lines.append("-- 每个英雄:英文名/中文名/主属性/位置/分路/技能类型抽象/加点/出装。")
    lines.append("local HEROES = {")
    for key, en, cn, attr, positions, lane, ab_types, prio, sig in HEROES:
        pos = positions[0]
        early = ROLE_EARLY[pos]
        mid = dedup(list(sig) + ["item_black_king_bar", "item_aghanims_shard"])
        late = ROLE_LATE[pos]
        situ = [s for s in SITUATIONAL if s not in mid and s not in late]
        build = skill_build(prio, len(ab_types))
        ab_lua = ", ".join('{ type = "%s" }' % t for t in ab_types)
        lines.append(
            '  %s = { key = "%s", name_en = "%s", name_cn = "%s", npc_name = "npc_dota_hero_%s", primary_attr = "%s", positions = %s, lane = "%s",'
            % (key, key, en, cn, INTERNAL_NAME.get(key, key), attr, lua_int_list(positions), lane)
        )
        lines.append(
            '    abilities = { %s }, skill_build = %s,'
            % (ab_lua, lua_int_list(build))
        )
        lines.append(
            '    items = { early = %s, mid = %s, late = %s, situational = %s }, },'
            % (lua_str_list(early), lua_str_list(mid), lua_str_list(late), lua_str_list(situ))
        )
    lines.append("}")
    lines.append("return HEROES")
    (data_dir / "heroes.lua").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- data/talents.lua ----
    tlines = []
    tlines.append("-- talents.lua -- 由 tools/generate.py 生成,不要手改。")
    tlines.append("-- 天赋表: 127 个英雄各自的天赋表, 见 tools/all_heroes.py (v3.0.0 已删除按主属性的通用表)。")
    tlines.append("-- 格式: [10]/[15]/[20]/[25] = 0 左 / 1 右。")
    tlines.append("local TALENTS = {")
    for key, en, cn, attr, positions, lane, ab_types, prio, sig in HEROES:
        t = ALL[key]["talents"]
        tlines.append('  %s = %s,' % (key, talent_lua(t)))
    tlines.append("}")
    tlines.append("return TALENTS")
    (data_dir / "talents.lua").write_text("\n".join(tlines) + "\n", encoding="utf-8")

    # ---- 每个英雄: bot / ability / item_purchase / BotLib ----
    count = 0
    for key, en, cn, attr, positions, lane, ab_types, prio, sig in HEROES:
        build = skill_build(prio, len(ab_types))
        (botlib_dir / ("hero_%s.lua" % key)).write_text(botlib_text(key, (key, en, cn, attr, positions, lane, ab_types, prio, sig)), encoding="utf-8")
        (bots / ("bot_%s.lua" % key)).write_text(
            "-- bot_%s.lua -- %s %s (%s, %s 路) -- v3.0.0 薄 wrapper,决策在 mode_dispatcher.lua。\n"
            'local ModeDispatcher = require(GetScriptDirectory() .. "/mode_dispatcher")\n\n'
            "function Think()\n"
            "  local bot = GetBot()\n"
            "  if bot == nil then return end\n"
            "  ModeDispatcher.Think(bot)\n"
            "end\n" % (key, en, cn, attr, lane),
            encoding="utf-8",
        )
        (bots / ("ability_item_usage_%s.lua" % key)).write_text(
            "-- ability_item_usage_%s.lua -- %s %s -- v3.0.0: 技能走 BotLib SkillsComplement(),\n-- 加点走 BotLib 的 SKILL_BUILD, 天赋级走 TALENTS。通用入口见 ability_item_usage_generic.lua。\n"
            'local Skill = require(GetScriptDirectory() .. "/engine/skill")\n'
            'local Heroes = require(GetScriptDirectory() .. "/data/heroes")\n'
            'local Micro = require(GetScriptDirectory() .. "/engine/micro")\n'
            'local Perception = require(GetScriptDirectory() .. "/engine/perception")\n'
            'local HERO_KEY = "%s"\n'
            "local SKILL_BUILD = %s\n\n"
            "function AbilityUsageThink()\n"
            "  local bot = GetBot()\n"
            "  if bot == nil then return end\n"
            "  local snap = Perception.Snapshot(bot)\n"
            "  if snap == nil then return end\n"
            "  if Micro.TryRescueAlly(bot, snap, Heroes[HERO_KEY]) then return end\n"
            "  local ok, mod = pcall(require, GetScriptDirectory() .. \"/BotLib/hero_\" .. HERO_KEY)\n"
            "  if ok and mod ~= nil and mod.SkillsComplement ~= nil then\n"
            "    local ok2, cast = pcall(mod.SkillsComplement, bot, snap)\n"
            "    if ok2 and cast then return end\n"
            "  end\n"
            "  Micro.TryCastByType(bot, snap, Heroes[HERO_KEY])\n"
            "  Micro.TryUseItems(bot, snap)\n"
            "end\n\n"
            "function AbilityLevelUpThink()\n"
            "  local bot = GetBot()\n"
            "  if bot == nil then return end\n"
            "  local okPts, pts = pcall(function() return bot:GetAbilityPoints() end)\n"
            "  if not okPts or pts == nil or pts <= 0 then return end\n"
            "  local okLvl, lvl = pcall(function() return bot:GetLevel() end)\n"
            "  if not okLvl or lvl == nil or lvl < 1 then return end\n"
            "  -- 下一个要点的 build 位置由 (等级 - 剩余点数) 推出, 不存文件级状态:\n"
            "  -- 正常每次升级只攒 1 点时 idx == lvl, 与旧行为一致; 一次攒多点时从最早\n"
            "  -- 没点的 build 位置开始依次点, 不会把所有攒的点都砸进 build[lvl] 同一技能。\n"
            "  -- (模拟实测: Lion 一次升 13 级, 旧版 20 次调用只点了 voodoo 到 4 级, Q/E/R 全 0。)\n"
            "  local idx = lvl - pts + 1\n"
            "  if idx < 1 then idx = 1 end\n"
            "  -- 跳过已满级后无技能可点的空位 (17/18/19/21-24, build==0 且不是天赋级);\n"
            "  -- 天赋级 (10/15/20/25) 的 build==0 要留住, 下面走点天赋分支。\n"
            "  while idx <= #SKILL_BUILD and SKILL_BUILD[idx] == 0\n"
            "      and idx ~= 10 and idx ~= 15 and idx ~= 20 and idx ~= 25 do\n"
            "    idx = idx + 1\n"
            "  end\n"
            "  if idx > #SKILL_BUILD then return end\n"
            "  if idx == 10 or idx == 15 or idx == 20 or idx == 25 then  -- 天赋级\n"
            "    local okM, mod = pcall(require, GetScriptDirectory() .. \"/BotLib/hero_\" .. HERO_KEY)\n"
            "    if okM and mod ~= nil and mod.TALENTS ~= nil then\n"
            "      Skill.LevelTalent(bot, mod.TALENTS, idx)\n"
            "    end\n"
            "    return\n"
            "  end\n"
            "  local slot = SKILL_BUILD[idx] - 1\n"
            "  local ability = Micro.GetAbility(bot, slot)\n"
            "  if ability == nil then return end\n"
            "  local okName, name = pcall(function() return ability:GetAbilityName() end)\n"
            "  if not okName or name == nil then return end\n"
            "  local okUp, canUp = pcall(function() return ability:CanAbilityBeUpgraded() end)\n"
            "  if okUp and canUp then\n"
            "    pcall(function() bot:Action_LevelAbility(name) end)\n"
            "  end\n"
            "end\n" % (key, en, cn, key, lua_int_list(build)),
            encoding="utf-8",
        )
        (bots / ("item_purchase_%s.lua" % key)).write_text(
            "-- item_purchase_%s.lua -- %s %s -- v3.0.0: 出装走 item_purchase_generic.lua 的状态机,\n-- 读 BotLib 的 sBuyList / sSellList。\n"
            'local Generic = require(GetScriptDirectory() .. "/item_purchase_generic")\n\n'
            "function ItemPurchaseThink()\n"
            "  local bot = GetBot()\n"
            "  if bot == nil then return end\n"
            "  Generic.ItemPurchaseThinkFor(bot)\n"
            "end\n" % (key, en, cn),
            encoding="utf-8",
        )
        count += 1
    print("heroes: %d" % len(HEROES))
    print("per-hero files: %d (3 x %d) + BotLib %d" % (count * 3, count, count))
    print("deep heroes (real Consider): %d / %d" % (len(ALL), len(HEROES)))
    print("heroes.lua: %s" % (data_dir / "heroes.lua"))


if __name__ == "__main__":
    main()
