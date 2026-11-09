# -*- coding: utf-8 -*-
"""生成器 v2.0.0: 读 tools/heroes_data.py + tools/focus_heroes.py,
产出 data/heroes.lua + data/talents.lua + 每个英雄 3 个 wrapper + BotLib/hero_<name>.lua。
可复现: 改 heroes_data.py / focus_heroes.py 后重新跑本脚本即可随版本更新,
跑完 git diff 应为 0 (除非数据改了)。
用法: python3 tools/generate.py [--root ~/workspace/dota2-ai]
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from heroes_data import HEROES  # noqa: E402
from focus_heroes import FOCUS, FOCUS_HEROES  # noqa: E402

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
# 通用天赋表 (按主属性, 0=左/1=右, 本项目自选, 非官方推荐)。
GENERIC_TALENTS = {
    "str": {10: 0, 15: 0, 20: 0, 25: 0},
    "agi": {10: 1, 15: 1, 20: 1, 25: 1},
    "int": {10: 0, 15: 1, 20: 0, 25: 1},
    "universal": {10: 0, 15: 0, 20: 1, 25: 0},
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
    """生成 1-25 级加点表: 6/11/16 点大招, 其余按优先级点满 (每技能最多 4 级)。
    Invoker(6 个技能位)用显式表。全部技能满级后的等级填 0 (天赋级)。"""
    if n_abilities > 4:
        return list(INVOKER_SKILL_BUILD)
    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    build = []
    pi = 0
    for lvl in range(1, 26):
        if lvl in (6, 11, 16):
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
    """返回 {pos: [>=10 件]}。焦点英雄用 focus_heroes.py 的表, 其余用位置模板+招牌装。"""
    _k, _en, _cn, attr, positions, _lane, _ab, _prio, sig = hero
    if key in FOCUS:
        out = {}
        main = FOCUS[key]["items"]
        for pos in positions:
            out[pos] = list(main.get(pos) or main.get(positions[0]) or [])
        for pos in (1, 2, 3, 4, 5):
            if pos not in out:
                out[pos] = list(main.get(positions[0]) or [])
        return out
    out = {}
    for pos in (1, 2, 3, 4, 5):
        out[pos] = dedup(ROLE_EARLY[pos] + list(sig) + ["item_black_king_bar", "item_aghanims_shard"] + ROLE_LATE[pos])
    return out


def botlib_text(key, hero):
    _k, en, cn, attr, positions, lane, ab_types, prio, sig = hero
    build = skill_build(prio, len(ab_types))
    talents = FOCUS[key]["talents"] if key in FOCUS else GENERIC_TALENTS[attr]
    buys = buy_lists(key, hero)
    lines = []
    lines.append("-- hero_%s.lua -- %s %s -- v2.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。\n-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):\n-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。\n-- 焦点英雄: 真实 Consider 逻辑 (见 tools/focus_heroes.py); 其余英雄: 通用类型驱动 fallback。" % (key, en, cn))
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
    if key in FOCUS:
        ab = FOCUS[key]["abilities"]
        lines.append("X.ABILITIES = { Q = \"%s\", W = \"%s\", E = \"%s\", R = \"%s\" }" % (ab["Q"], ab["W"], ab["E"], ab["R"]))
        for slot in ("Q", "W", "E", "R"):
            body = FOCUS[key]["consider"][slot]
            lines.append("function X.Consider%s(bot, snap, ab)\n%s\nend" % (slot, body))
        lines.append("function X.SkillsComplement(bot, snap)")
        lines.append("  if bot == nil or snap == nil then return false end")
        lines.append("  local ab = Skill.GetAbilityMap(bot)")
        lines.append("  for _, slot in ipairs({\"R\", \"Q\", \"W\", \"E\"}) do")
        lines.append("    local fn = X[\"Consider\" .. slot]")
        lines.append("    if fn ~= nil then")
        lines.append("      local desire, target, castType = fn(bot, snap, ab)")
        lines.append("      if desire ~= nil and desire >= 0.5 then")
        lines.append('        local name = X.ABILITIES[slot]')
        lines.append("        local ability = ab[name]")
        lines.append("        if ability ~= nil and Skill.Cast(bot, ability, target, castType) then")
        lines.append("          if slot == \"R\" then")
        lines.append("            local loc = nil")
        lines.append("            if target ~= nil then local ok, l = pcall(function() return target:GetLocation() end) if ok then loc = l end end")
        lines.append("            if loc ~= nil then Team.ReportComboWindow(bot, loc) end")
        lines.append("          end")
        lines.append("          return true")
        lines.append("        end")
        lines.append("      end")
        lines.append("    end")
        lines.append("  end")
        lines.append("  return false")
        lines.append("end")
    else:
        lines.append("X.ABILITIES = {}")
        lines.append("-- 通用版: 无专属 Consider, 直接走 v1.1 的类型驱动 fallback。")
        lines.append("function X.SkillsComplement(bot, snap)")
        lines.append("  if bot == nil or snap == nil then return false end")
        lines.append("  local heroData = Heroes[X.KEY]")
        lines.append("  if heroData == nil then return false end")
        lines.append("  return Micro.TryCastByType(bot, snap, heroData)")
        lines.append("end")
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

    # ---- data/talents.lua ----
    tlines = []
    tlines.append("-- talents.lua -- 由 tools/generate.py 生成,不要手改。")
    tlines.append("-- 天赋表: 焦点英雄用 tools/focus_heroes.py 的自选表, 其余按主属性通用表。")
    tlines.append("-- 格式: [10]/[15]/[20]/[25] = 0 左 / 1 右。")
    tlines.append("local TALENTS = {")
    for key, en, cn, attr, positions, lane, ab_types, prio, sig in HEROES:
        t = FOCUS[key]["talents"] if key in FOCUS else GENERIC_TALENTS[attr]
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
            "-- bot_%s.lua -- %s %s (%s, %s 路) -- v2.0.0 薄 wrapper,决策在 mode_dispatcher.lua。\n"
            'local ModeDispatcher = require(GetScriptDirectory() .. "/mode_dispatcher")\n\n'
            "function Think()\n"
            "  local bot = GetBot()\n"
            "  if bot == nil then return end\n"
            "  ModeDispatcher.Think(bot)\n"
            "end\n" % (key, en, cn, attr, lane),
            encoding="utf-8",
        )
        (bots / ("ability_item_usage_%s.lua" % key)).write_text(
            "-- ability_item_usage_%s.lua -- %s %s -- v2.0.0: 技能走 BotLib SkillsComplement(),\n-- 加点走 BotLib 的 SKILL_BUILD, 天赋级走 TALENTS。通用入口见 ability_item_usage_generic.lua。\n"
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
            "end\n\n"
            "function AbilityLevelUpThink()\n"
            "  local bot = GetBot()\n"
            "  if bot == nil then return end\n"
            "  local okPts, pts = pcall(function() return bot:GetAbilityPoints() end)\n"
            "  if not okPts or pts == nil or pts <= 0 then return end\n"
            "  local okLvl, lvl = pcall(function() return bot:GetLevel() end)\n"
            "  if not okLvl or lvl == nil or lvl < 1 or lvl > #SKILL_BUILD then return end\n"
            "  if SKILL_BUILD[lvl] == 0 then return end  -- 天赋级,显式跳过,禁止查询 -1 槽位。\n"
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
        (bots / ("item_purchase_%s.lua" % key)).write_text(
            "-- item_purchase_%s.lua -- %s %s -- v2.0.0: 出装走 item_purchase_generic.lua 的状态机,\n-- 读 BotLib 的 sBuyList / sSellList。\n"
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
    print("focus heroes: %d (%s)" % (len(FOCUS_HEROES), ", ".join(FOCUS_HEROES)))
    print("heroes.lua: %s" % (data_dir / "heroes.lua"))


if __name__ == "__main__":
    main()
