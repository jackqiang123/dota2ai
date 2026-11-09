# -*- coding: utf-8 -*-
"""生成器:读 tools/heroes_data.py,产出 data/heroes.lua + 每个英雄 3 个薄 wrapper 文件。
可复现:改 heroes_data.py 后重新跑本脚本即可随版本更新。
用法: python3 tools/generate.py [--root ~/workspace/dota2-ai]
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from heroes_data import HEROES  # noqa: E402

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


def dedup(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def skill_build(priority, n_abilities):
    """生成 1-25 级加点表:6/11/16 点大招,其余按优先级点满(每技能最多 4 级)。
    Invoker(6 个技能位)特殊处理:前 4 位循环加点。"""
    if n_abilities > 4:
        build, counts = [], [0] * n_abilities
        order = [1, 2, 3, 4]
        i = 0
        for lvl in range(1, 26):
            # Invoker 的 Invoke(第 4 位)尽早点 1 级,之后循环。
            pick = order[i % len(order)]
            i += 1
            build.append(pick)
        return build
    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    build = []
    pi = 0
    for lvl in range(1, 26):
        if lvl in (6, 11, 16):
            pick = 4
        else:
            # 按优先级找第一个未满 4 级的技能。
            pick = None
            for _ in range(len(priority)):
                cand = priority[pi % len(priority)]
                pi += 1
                if counts[cand] < 4:
                    pick = cand
                    break
            if pick is None:
                # 全部技能已满级:0 表示无技能可点(天赋点),AbilityLevelUpThink 会跳过。
                build.append(0)
                continue
        counts[pick] += 1
        build.append(pick)
    return build


def lua_str_list(items):
    return "{" + ", ".join('"%s"' % x for x in items) + "}"


def lua_int_list(items):
    return "{" + ", ".join(str(x) for x in items) + "}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parents[1]))
    args = ap.parse_args()
    root = pathlib.Path(args.root)
    bots = root / "scripts" / "vscripts" / "bots"
    data_dir = bots / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

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
            % (key, key, en, cn, key, attr, lua_int_list(positions), lane)
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

    # ---- 每个英雄 3 个薄 wrapper ----
    count = 0
    for key, en, cn, attr, positions, lane, ab_types, prio, sig in HEROES:
        build = skill_build(prio, len(ab_types))
        # bot_<hero>.lua
        (bots / ("bot_%s.lua" % key)).write_text(
            "-- bot_%s.lua -- %s %s (%s, %s 路) -- 薄 wrapper,决策在 engine/core.lua。\n"
            'local Core = require("bots/engine/core")\n\n'
            "function Think()\n"
            "  local bot = GetBot()\n"
            "  if bot == nil then return end\n"
            "  Core.Think(bot)\n"
            "end\n" % (key, en, cn, attr, lane),
            encoding="utf-8",
        )
        # ability_item_usage_<hero>.lua
        (bots / ("ability_item_usage_%s.lua" % key)).write_text(
            "-- ability_item_usage_%s.lua -- %s %s -- 技能释放走 engine/micro.lua 的类型抽象,加点走下表。\n"
            'local Heroes = require("bots/data/heroes")\n'
            'local Micro = require("bots/engine/micro")\n'
            'local Perception = require("bots/engine/perception")\n'
            'local HERO_KEY = "%s"\n'
            "local SKILL_BUILD = %s\n\n"
            "function AbilityUsageThink()\n"
            "  local bot = GetBot()\n"
            "  if bot == nil then return end\n"
            "  local snap = Perception.Snapshot(bot)\n"
            "  if snap == nil then return end\n"
            "  Micro.TryCastByType(bot, snap, Heroes[HERO_KEY])\n"
            "end\n\n"
            "function AbilityLevelUpThink()\n"
            "  local bot = GetBot()\n"
            "  if bot == nil then return end\n"
            "  local okPts, pts = pcall(function() return bot:GetAbilityPoints() end)\n"
            "  if not okPts or pts == nil or pts <= 0 then return end\n"
            "  local okLvl, lvl = pcall(function() return bot:GetLevel() end)\n"
            "  if not okLvl or lvl == nil or lvl < 1 or lvl > #SKILL_BUILD then return end\n"
            "  local slot = SKILL_BUILD[lvl] - 1\n"
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
        # item_purchase_<hero>.lua
        (bots / ("item_purchase_%s.lua" % key)).write_text(
            "-- item_purchase_%s.lua -- %s %s -- 出装顺序在 data/heroes.lua 的 items 表里。\n"
            'local Heroes = require("bots/data/heroes")\n'
            'local Micro = require("bots/engine/micro")\n'
            'local HERO_KEY = "%s"\n\n'
            "function ItemPurchaseThink()\n"
            "  local bot = GetBot()\n"
            "  if bot == nil then return end\n"
            "  Micro.TryBuyNextItem(bot, Heroes[HERO_KEY])\n"
            "end\n" % (key, en, cn, key),
            encoding="utf-8",
        )
        count += 1
    print("heroes: %d" % len(HEROES))
    print("per-hero files: %d (3 x %d)" % (count * 3, count))
    print("heroes.lua: %s" % (data_dir / "heroes.lua"))


if __name__ == "__main__":
    main()
