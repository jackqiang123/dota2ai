# -*- coding: utf-8 -*-
"""v3.0.0 全量英雄数据: 127 个英雄的 Consider / 天赋 / 分位置出装。

事实源合并:
- tools/focus_heroes.py: 10 个 v2.0 焦点英雄 (axe/zeus/lion/crystal_maiden/
  magnus/faceless_void/enigma/dazzle/oracle/huskar)。
- tools/all_heroes_a.py .. tools/all_heroes_f.py: 其余 117 个英雄。
两组互不重叠, 合计 127, 与 tools/heroes_data.py 的 HEROES 一一对应。

技能名核对表见 tools/skill_names_reference.json (d2vpk npc_heroes.txt/
npc_abilities.txt 为底, 15 处 worker 标记的过时名已在 v3.0 整合时订正,
见各 chunk 的 limitations 与 skill_names_reference.json 的 source 字段)。

不要手改生成的 BotLib 文件, 改这里(或各分块文件)再跑 tools/generate.py。
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from all_heroes_a import ALL_A  # noqa: E402
from all_heroes_b import ALL_B  # noqa: E402
from all_heroes_c import ALL_C  # noqa: E402
from all_heroes_d import ALL_D  # noqa: E402
from all_heroes_e import ALL_E  # noqa: E402
from all_heroes_f import ALL_F  # noqa: E402
from focus_heroes import FOCUS  # noqa: E402

ALL = {}
ALL.update(ALL_A)
ALL.update(ALL_B)
ALL.update(ALL_C)
ALL.update(ALL_D)
ALL.update(ALL_E)
ALL.update(ALL_F)
ALL.update(FOCUS)

# 特殊英雄: Invoker 的 invoked 技能表 (8 个) 在 ALL_F["invoker"]["invoked"]。
INVOKED_HEROES = [k for k, v in ALL.items() if v.get("invoked")]

assert len(ALL) == 127, "ALL must have exactly 127 heroes, got %d" % len(ALL)
assert len(ALL_A) + len(ALL_B) + len(ALL_C) + len(ALL_D) + len(ALL_E) + len(ALL_F) + len(FOCUS) == 127
