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
    # 注意: 虚拟机换过之后 /usr/bin/luac 可能没了, 解释器在仓库外的用户空间副本
    # ~/workspace/.lua/usr/bin/luac5.4, 这里也找一下 (PATH 里没有时才用)。
    luac = shutil.which("luac") or shutil.which("luac5.4")
    if not luac:
        ws_luac = root.parent / ".lua" / "usr" / "bin" / "luac5.4"
        if ws_luac.exists():
            luac = str(ws_luac)
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

    # 9. v1.1.0:AbilityLevelUpThink 必须显式处理 SKILL_BUILD==0 (天赋级/已满级空位),
    # 禁止查询 -1 槽位。v3.1.0: 加点位置由 (等级-剩余点数) 推出 (idx),
    # 守卫形式是 SKILL_BUILD[idx] == 0, 意图与旧版 SKILL_BUILD[lvl] == 0 相同;
    # verify_v110 4a 直接断言 15 级不查询 -1 槽位。
    sample = (bots / "ability_item_usage_axe.lua").read_text(encoding="utf-8")
    if "SKILL_BUILD[idx] == 0" not in sample:
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

    # 13. v3.0.0: BotLib 127 个文件全部有真实 Consider; 每个英雄 ConsiderQ/W/E/R +
    # SkillsComplement + 天赋 + 分位置出装; 每个英雄至少 2 个非被动 Consider
    # (Invoker 另计 8 个 invoked Consider; Wraith King 当前版本只有 Q 一个主动
    # 技能, 是唯一允许 1 个的例外); 主位置出装 >=12 件, 每位置 >=8 件, 五位置互不相同。
    import json
    from all_heroes import ALL
    botlib = bots / "BotLib"
    ref = json.loads((root / "tools" / "skill_names_reference.json").read_text(encoding="utf-8"))
    for h in HEROES:
        key = h[0]
        if not (botlib / ("hero_%s.lua" % key)).exists():
            errors.append("missing BotLib hero_%s.lua" % key)
            continue
        txt = (botlib / ("hero_%s.lua" % key)).read_text(encoding="utf-8")
        for fn in ["ConsiderQ", "ConsiderW", "ConsiderE", "ConsiderR", "SkillsComplement", "TALENTS", "sBuyList", "sSellList"]:
            if fn not in txt:
                errors.append("BotLib %s missing %s" % (key, fn))
        # 非被动 Consider 计数
        bodies = re.findall(r"function X\.Consider[QWER]\(bot, snap, ab\)\n(.*?)\nend", txt, re.S)
        nonpassive = sum(1 for b in bodies if b.strip() != 'return 0, nil, "none"')
        invoked = len(re.findall(r"function X\.ConsiderInvoker\w+\(bot, snap, ab\)", txt))
        if key == "invoker":
            if invoked < 4:
                errors.append("invoker invoked Consider <4: %d" % invoked)
        elif key == "wraith_king":
            if nonpassive < 1:
                errors.append("wraith_king non-passive Consider <1")
        elif nonpassive < 2:
            errors.append("%s non-passive Consider <2: %d" % (key, nonpassive))
        # 五位置出装
        lists = re.findall(r'sBuyList\["pos_(\d+)"\] = \{([^}]*)\}', txt)
        if len(lists) != 5:
            errors.append("%s sBuyList positions != 5: %d" % (key, len(lists)))
        else:
            sets = {tuple(sorted(x.strip() for x in items.split(",") if x.strip())) for _, items in lists}
            if len(sets) != 5:
                errors.append("%s sBuyList five positions not all distinct" % key)
            for pos, items in lists:
                n = items.count("item_")
                if n < 8:
                    errors.append("%s pos_%s buy list <8 items: %d" % (key, pos, n))
            main_pos = str(h[4][0])
            for pos, items in lists:
                if pos == main_pos and items.count("item_") < 12:
                    errors.append("%s main pos_%s buy list <12 items: %d" % (key, pos, items.count("item_")))
        # 技能名对核对表
        m = re.search(r'X\.ABILITIES = \{ Q = "([^"]+)", W = "([^"]+)", E = "([^"]+)", R = "([^"]+)" \}', txt)
        if not m:
            errors.append("%s ABILITIES line not found" % key)
        else:
            for slot, name in zip("QWER", m.groups()):
                if ref.get(key, {}).get(slot) != name:
                    errors.append("%s %s skill name %s != reference %s" % (key, slot, name, ref.get(key, {}).get(slot)))
        # BotLib 内不得再有类型驱动 fallback 调用 (兜底只在 ability_item_usage wrapper 里;
        # 生成的头部注释里提到 Micro.TryCastByType 是说明文字, 不算调用)
        if "TryCastByType(bot" in txt:
            errors.append("BotLib %s still calls TryCastByType fallback" % key)
    if len(ALL) != 127:
        errors.append("tools/all_heroes.py ALL != 127: %d" % len(ALL))
    if set(ALL) != {h[0] for h in HEROES}:
        errors.append("tools/all_heroes.py ALL key set != HEROES")

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

    # 18. v3.0.0: 通用天赋表必须已删除 —— generate.py 不得再有 GENERIC_TALENTS
    # 或“按主属性通用表”; data/talents.lua 127 条必须与 BotLib 的 TALENTS 一致。
    gen_txt = (root / "tools" / "generate.py").read_text(encoding="utf-8")
    if "GENERIC_TALENTS" in gen_txt:
        errors.append("tools/generate.py still contains GENERIC_TALENTS")
    talents_lua = (bots / "data" / "talents.lua").read_text(encoding="utf-8")
    for h in HEROES:
        key = h[0]
        m = re.search(r"^\s{2}%s = \{ \[10\] = (\d), \[15\] = (\d), \[20\] = (\d), \[25\] = (\d) \}," % re.escape(key), talents_lua, re.M)
        if not m:
            errors.append("data/talents.lua missing %s" % key)
            continue
        bl = (bots / "BotLib" / ("hero_%s.lua" % key)).read_text(encoding="utf-8")
        m2 = re.search(r"X\.TALENTS = \{ \[10\] = (\d), \[15\] = (\d), \[20\] = (\d), \[25\] = (\d) \}", bl)
        if not m2 or m.groups() != m2.groups():
            errors.append("talents mismatch talents.lua vs BotLib for %s" % key)

    # 19. v3.0.0: verify_v300.lua 存在; tools/all_heroes.py 可导入且 127 齐。
    if not (root / "tools" / "verify_v300.lua").exists():
        errors.append("tools/verify_v300.lua missing")
    if not (root / "tools" / "all_heroes.py").exists():
        errors.append("tools/all_heroes.py missing")

    # 20. v3.1.0: integration 环境齐全 —— sim / valve_api / run / README 存在;
    # luac 过 integration 文件 (注意: 检查 1 的 luac 只扫 bots 目录, 这里单独扫);
    # 不得有 /home/hatch 硬编码 (run.lua 用 arg[0] 推导仓库根目录);
    # 版本号 3.2.0 (addoninfo.txt + 主 README 含 integration 一节)。
    # 注意: validate.py 里不跑完整对局 (那是 run.lua 的事, 40 分钟太长),
    # 只做存在性 / 语法 / 路径 / 版本检查。
    integ = root / "tools" / "integration"
    for name in ["sim.lua", "valve_api.lua", "run.lua", "README.md"]:
        if not (integ / name).exists():
            errors.append("tools/integration/%s missing" % name)
    if luac:
        for name in ["sim.lua", "valve_api.lua", "run.lua", "hero_tests.lua"]:
            f = integ / name
            if f.exists():
                r = subprocess.run([luac, "-p", str(f)], capture_output=True, text=True)
                if r.returncode != 0:
                    errors.append("luac FAIL tools/integration/%s: %s" % (name, (r.stderr or r.stdout).strip()))
    for name in ["sim.lua", "valve_api.lua", "run.lua", "hero_tests.lua"]:
        f = integ / name
        if f.exists():
            txt = f.read_text(encoding="utf-8", errors="replace")
            if "/home/hatch" in txt or "/home/" in txt:
                errors.append("tools/integration/%s contains hardcoded /home/ path" % name)
    addoninfo = (root / "addoninfo.txt").read_text(encoding="utf-8", errors="replace")
    if '"3.2.0"' not in addoninfo:
        errors.append("addoninfo.txt is not 3.2.0")
    main_readme = (root / "README.md").read_text(encoding="utf-8", errors="replace")
    if "v3.2.0" not in main_readme or "tools/integration" not in main_readme:
        errors.append("main README missing v3.2.0 / integration section")
    run_txt = ""
    if (integ / "run.lua").exists():
        run_txt = (integ / "run.lua").read_text(encoding="utf-8", errors="replace")
    if "arg[0]" not in run_txt:
        errors.append("tools/integration/run.lua does not derive repo root from arg[0]")

    # 21. v3.2.0: per-hero integration tests —— hero_tests.lua 存在; 报告存在且
    # 通过 + 已知限制 == 127 且失败 == 0 (已知限制见 hero_tests.lua 的
    # KNOWN_LIMITATIONS, 每个都要有真实原因; 不能用它掩盖未调查的失败)。
    if not (integ / "hero_tests.lua").exists():
        errors.append("tools/integration/hero_tests.lua missing")
    hero_report = integ / "hero_tests_report.md"
    if not hero_report.exists():
        errors.append("tools/integration/hero_tests_report.md missing (run hero_tests.lua)")
    else:
        rep_txt = hero_report.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"通过率: (\d+)/(\d+) \([\d.]+%\), 已知限制 (\d+), 失败 (\d+)", rep_txt)
        if m is None:
            errors.append("hero_tests_report.md pass-rate line not found")
        else:
            n_pass, n_total, n_known, n_fail = (int(m.group(1)), int(m.group(2)),
                                                int(m.group(3)), int(m.group(4)))
            if n_total != 127 or n_pass + n_known != 127 or n_fail != 0:
                errors.append("hero_tests_report.md: pass %d + known %d != 127 or fail %d != 0"
                              % (n_pass, n_known, n_fail))

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
