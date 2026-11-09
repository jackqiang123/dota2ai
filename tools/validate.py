# -*- coding: utf-8 -*-
"""校验:luac 语法 + 文件齐全 + 计数一致 + 无占位符。
用法: python3 tools/validate.py [--root ~/workspace/dota2-ai]
退出码 0=全过,非 0=有失败。
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from heroes_data import HEROES  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parents[1]))
    args = ap.parse_args()
    root = pathlib.Path(args.root)
    bots = root / "scripts" / "vscripts" / "bots"
    errors, warnings = [], []

    lua_files = sorted(bots.rglob("*.lua"))
    print("lua files found: %d" % len(lua_files))

    # 1. luac 语法校验(优先);本机无 luac 时回退到 Python 括号/关键字配对检查。
    luac = shutil.which("luac") or shutil.which("luac5.4")
    if luac:
        print("validator: %s" % luac)
        for f in lua_files:
            r = subprocess.run([luac, "-p", str(f)], capture_output=True, text=True)
            if r.returncode != 0:
                errors.append("luac FAIL %s: %s" % (f.relative_to(root), (r.stderr or r.stdout).strip()))
    else:
        warnings.append("no luac found; fell back to bracket check (see README)")
        for f in lua_files:
            text = f.read_text(encoding="utf-8", errors="replace")
            for a, b in [("(", ")"), ("{", "}"), ("[", "]")]:
                if text.count(a) != text.count(b):
                    errors.append("bracket mismatch %s: %s=%d %s=%d" % (f, a, text.count(a), b, text.count(b)))

    # 2. 每个英雄 3 个文件齐全。
    missing = []
    for h in HEROES:
        key = h[0]
        for name in ("bot_%s.lua" % key, "ability_item_usage_%s.lua" % key, "item_purchase_%s.lua" % key):
            if not (bots / name).exists():
                missing.append(name)
    if missing:
        errors.append("missing per-hero files: %s" % missing[:10])

    # 3. heroes.lua 包含全部 127 个 key,无重复。
    heroes_lua = (bots / "data" / "heroes.lua").read_text(encoding="utf-8")
    keys_in_lua = re.findall(r"^\s{2}(\w+) = \{ key =", heroes_lua, re.M)
    if len(keys_in_lua) != len(HEROES):
        errors.append("heroes.lua keys=%d, expected %d" % (len(keys_in_lua), len(HEROES)))
    if len(set(keys_in_lua)) != len(keys_in_lua):
        errors.append("heroes.lua has duplicate keys")
    expected = {h[0] for h in HEROES}
    if set(keys_in_lua) != expected:
        errors.append("heroes.lua key set mismatch: missing=%s extra=%s"
                      % (sorted(expected - set(keys_in_lua))[:5], sorted(set(keys_in_lua) - expected)[:5]))

    # 4. 引擎 + 入口文件存在。
    for rel in ["bot_generic.lua", "hero_selection.lua", "team_think.lua",
                "mode_dispatcher.lua", "ability_item_usage_generic.lua",
                "item_purchase_generic.lua",
                "engine/perception.lua", "engine/utility.lua", "engine/micro.lua",
                "engine/macro.lua", "engine/team.lua", "engine/core.lua",
                "engine/skill.lua", "data/heroes.lua", "data/talents.lua",
                "data/combos.lua"]:
        if not (bots / rel).exists():
            errors.append("missing engine file: %s" % rel)

    # 5. 无占位符 / TODO。
    for f in lua_files:
        text = f.read_text(encoding="utf-8", errors="replace")
        if "TODO" in text or "FIXME" in text or "占位" in text:
            errors.append("placeholder found in %s" % f.relative_to(root))

    # 6. 引用检查:核心 API 名必须出现(防止编造 API 而不用真 API)。
    engine_text = (bots / "bot_generic.lua").read_text(encoding="utf-8") + "".join((bots / "engine" / f).read_text(encoding="utf-8") for f in ["core.lua", "micro.lua", "perception.lua"]) + "".join(f.read_text(encoding="utf-8") for f in sorted(bots.glob("mode_*_generic.lua")))
    for api in ["GetBot", "Action_MoveToLocation", "Action_AttackUnit", "Action_UseAbility"]:
        if api not in engine_text:
            warnings.append("engine does not mention %s" % api)

    # 7. v1.1.0:主属性按官方 7.41f 计数 36 力 / 35 敏 / 34 智 / 22 全才。
    from collections import Counter
    attr_counts = Counter(h[3] for h in HEROES)
    if dict(attr_counts) != {"str": 36, "agi": 35, "int": 34, "universal": 22}:
        errors.append("primary_attr counts wrong: %s, expected str36/agi35/int34/universal22" % dict(attr_counts))

    # 8. v1.1.0:Invoker 加点上限 Quas/Wex/Exort 各 7、Invoke 4;普通英雄每技能 <=4、大招 <=3。
    for m in re.finditer(r"^\s{2}(\w+) = \{ key = .*?skill_build = \{([^}]*)\}", heroes_lua, re.M | re.S):
        key, build_s = m.group(1), m.group(2)
        build = [int(x) for x in build_s.replace(",", " ").split() if x.strip()]
        if len(build) != 25:
            errors.append("skill_build len!=25: %s" % key)
            continue
        counts = Counter(build)
        counts.pop(0, None)
        if key == "invoker":
            if dict(counts) != {1: 7, 2: 7, 3: 7, 4: 4}:
                errors.append("invoker skill_build counts wrong: %s" % dict(counts))
            if build[1] != 4:
                errors.append("invoker must level Invoke at level 2, got %s" % build)
        else:
            for slot, c in counts.items():
                cap = 3 if slot == 4 else 4
                if c > cap:
                    errors.append("skill_build over cap: %s slot %d x%d" % (key, slot, c))

    # 9. v1.1.0:AbilityLevelUpThink 必须显式跳过 SKILL_BUILD==0,禁止查询 -1 槽位。
    sample = (bots / "ability_item_usage_axe.lua").read_text(encoding="utf-8")
    if "SKILL_BUILD[lvl] == 0" not in sample:
        errors.append("AbilityLevelUpThink missing explicit SKILL_BUILD==0 guard")

    # 10. v1.1.0:难度造假已删——goldMul/xpMul 字段定义、1.25x 说法不得再出现。
    # 注意:utility.lua 注释里解释“删掉了 goldMul/xpMul”是允许的,只查字段定义与数值说法。
    for f in list(bots.rglob("*.lua")) + [root / "README.md", root / "addoninfo.txt"]:
        if not f.exists():
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        if re.search(r"(goldMul|xpMul)\s*=", txt) or "1.25x" in txt or "1.25 / 1.25" in txt:
            errors.append("goldMul/xpMul field or 1.25x claim still present in %s" % f.relative_to(root))

    # 11. v1.1.0:combos 表存在、>=12 组、每组有 a/b/desc;互动入口存在。
    combos_path = bots / "data" / "combos.lua"
    if not combos_path.exists():
        errors.append("missing data/combos.lua")
    else:
        combos_text = combos_path.read_text(encoding="utf-8")
        n_combos = combos_text.count('score = ')
        if n_combos < 12:
            errors.append("combos <12 groups: %d" % n_combos)
        for fn in ["ReportComboWindow", "GetFocusTarget", "ShouldHoldUlt",
                   "TryRescueAlly", "TryPlaceWard", "TryDeliverCourier"]:
            all_text = "".join((bots / "engine" / f).read_text(encoding="utf-8") for f in ["team.lua", "micro.lua", "core.lua"])
            if fn not in all_text:
                errors.append("missing interaction entry: %s" % fn)


    # 12. v2.0.0: Mode 文件 >=12, 每个有 GetDesire/Think/OnStart。
    mode_files = sorted(bots.glob("mode_*_generic.lua"))
    if len(mode_files) < 12:
        errors.append("mode files <12: %d" % len(mode_files))
    for f in mode_files:
        txt = f.read_text(encoding="utf-8")
        for fn in ["GetDesire", "Think", "OnStart"]:
            if fn not in txt:
                errors.append("mode %s missing %s" % (f.name, fn))

    # 13. v2.0.0: BotLib 127 个文件; 焦点英雄 10 个有 ConsiderQ/W/E/R + SkillsComplement + 天赋 + 主位置出装>=10 件。
    from focus_heroes import FOCUS
    botlib = bots / "BotLib"
    for h in HEROES:
        if not (botlib / ("hero_%s.lua" % h[0])).exists():
            errors.append("missing BotLib hero_%s.lua" % h[0])
    for key in FOCUS:
        txt = (botlib / ("hero_%s.lua" % key)).read_text(encoding="utf-8")
        for fn in ["ConsiderQ", "ConsiderW", "ConsiderE", "ConsiderR", "SkillsComplement", "TALENTS", "sBuyList", "sSellList"]:
            if fn not in txt:
                errors.append("focus %s missing %s" % (key, fn))
        # 主位置出装件数: 取第一个 pos 列表的 item_ 出现次数
        import re as _re
        m = _re.search(r'sBuyList\["pos_\d+"\] = \{([^}]*)\}', txt)
        if m and m.group(1).count("item_") < 10:
            errors.append("focus %s main-pos buy list <10 items" % key)

    # 14. v2.0.0: require 写法全仓库一致为 GetScriptDirectory() 写法, 不许残留 require("bots/...")。
    for f in bots.rglob("*.lua"):
        txt = f.read_text(encoding="utf-8", errors="replace")
        if 'require("bots/' in txt or "require('bots/" in txt:
            errors.append("old require(bots/...) still in %s" % f.relative_to(root))
    if "GetScriptDirectory" not in (bots / "bot_generic.lua").read_text(encoding="utf-8"):
        errors.append("bot_generic.lua does not use GetScriptDirectory()")

    # 15. v2.0.0: Lua 5.1 兼容 —— 禁用 goto / table.unpack / // / 位运算 << >>。
    for f in bots.rglob("*.lua"):
        txt = f.read_text(encoding="utf-8", errors="replace")
        for pat in [r"\bgoto\b", r"table\.unpack", r"//", r"<<", r">>"]:
            if re.search(pat, txt):
                errors.append("Lua 5.1 forbidden syntax %s in %s" % (pat, f.relative_to(root)))

    # 16. v2.0.0: TeamThink 存在 (team.lua + team_think.lua), data/talents.lua 127 条。
    team_txt = (bots / "engine" / "team.lua").read_text(encoding="utf-8")
    if "function Team.TeamThink" not in team_txt:
        errors.append("Team.TeamThink missing in engine/team.lua")
    if "function TeamThink" not in (bots / "team_think.lua").read_text(encoding="utf-8"):
        errors.append("global TeamThink missing in team_think.lua")
    talents_txt = (bots / "data" / "talents.lua").read_text(encoding="utf-8")
    if talents_txt.count("[10] =") != len(HEROES):
        errors.append("data/talents.lua entries != %d" % len(HEROES))

    # 17. v2.0.0: 旧 smoke_test.lua 已删 (硬编码 /home/hatch 路径), 由 verify_v200.lua 取代。
    if (root / "tools" / "smoke_test.lua").exists():
        errors.append("tools/smoke_test.lua still exists (hardcoded absolute path)")
    if not (root / "tools" / "verify_v200.lua").exists():
        errors.append("tools/verify_v200.lua missing")

    print("heroes: %d" % len(HEROES))
    print("per-hero files expected: %d" % (len(HEROES) * 3))
    print("errors: %d  warnings: %d" % (len(errors), len(warnings)))
    for w in warnings:
        print("WARN: %s" % w)
    for e in errors:
        print("ERROR: %s" % e)
    if errors:
        print("VALIDATION FAILED")
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
