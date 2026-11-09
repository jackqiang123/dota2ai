# Dota 2 AI — Valve Mode 系统 + 数据驱动的 Bot AI

一整套、可安装、可跑的 Dota 2 Workshop Bot AI。**不是 124 份手写脚本**，而是 Valve 原生 Team / Mode / Action 三层结构 + 一张英雄数据表 + 生成器。

> 版本：**v2.0.0**（2026-11-09）| 版本基准：**7.41f，127 名英雄**。
>
> **v2.0.0 更新日志：**架构换成 OHA 的方法（Valve 原生 Mode 系统）——(1) `bot_generic.lua` 只做入口，决策交给 `mode_dispatcher.lua` + 15 个 `mode_*_generic.lua`（每帧全部 GetDesire 打分，最高分模式的 Think 才跑）；(2) 新增 `team_think.lua` / `Team.TeamThink()`，每帧先定全队战略写进黑板；(3) 新增 `ability_item_usage_generic.lua` / `item_purchase_generic.lua`，技能走 BotLib `SkillsComplement()`，出装走按位置买装的状态机；(4) 新增 `BotLib/hero_<name>.lua`（127 个）：10 个焦点英雄写满真实 Consider 逻辑，117 个走通用 fallback；天赋表新增 `data/talents.lua`（焦点英雄自选，其余按主属性通用）；(5) 全仓库 require 改为 `require(GetScriptDirectory() .. "/...")` 的 Valve 写法；(6) Lua 5.1 兼容检查进 `validate.py`；旧 `smoke_test.lua`（硬编码 /home/hatch 路径）已删，由 `verify_v200.lua`（71 项）取代。v1.1.0 的修复与英雄互动全部保留，见下文。任务原文写“约 124 名”时还是 7.38 口径；经核实（Valve 官方英雄页 / datafeed，2026-11-09），2025-12-16 的 7.40 加入 **朗戈 Largo** 后总数为 **127**，此处按 127 名交付，一个不少。中文名以 dota2.com.cn 为准（已核实：Snapfire = 电炎绝手、Arc Warden = 天穹守望者、Outworld Destroyer = 殁境神蚀者、Pangolier = 石鳞剑士、Muerta = 琼英碧灵、Ringmaster = 百戏大王、Largo = 朗戈）。

## 统计（实测）

| 项目 | 数量 |
|---|---|
| 英雄总数 | 127 |
| 每英雄文件（bot / ability_item_usage / item_purchase） | 381（3 × 127） |
| Lua 文件总数 | 539（381 per-hero + 127 BotLib + 15 Mode + 通用入口 + 7 引擎 + 数据表） |
| 引擎文件 | 7（perception / utility / micro / macro / team / core 垫片 / skill） |
| Mode 文件 | 15（laning / farm / push + 三分路包装 / retreat / attack / roam / team_roam / roshan / ward / defend_tower / rune / secret_shop） |
| BotLib 英雄文件 | 127（10 个焦点深度版 + 117 个通用版） |
| 出装涉及的不同物品 | 64（均为真实物品名） |
| 校验 | `luac -p` 全过，0 错误 0 警告；见下文 |

分路分布（本项目分路分配）：{'safelane': 34, 'support': 34, 'offlane': 29, 'mid': 23, 'roam': 7}。主属性已按 Valve 官方 7.41f 核对：36 力 / 35 敏 / 34 智 / 22 全才（见 tools/heroes_data.py 注释），仅作信息展示，不参与决策。

## 架构

```
scripts/vscripts/bots/
  bot_generic.lua            # v2.0.0 通用入口 (约 20 行): 只初始化 + 调 mode_dispatcher, 不再自己算全部行为
  mode_dispatcher.lua        # Mode 分发器: 每帧对全部 Mode 调 GetDesire(), 最高分模式的 Think() 才跑; 模式切换调 OnStart()
  team_think.lua             # Team 层入口: Valve 每帧先调 TeamThink(), 转给 engine/team.lua 的 Team.TeamThink()
  mode_laning_generic.lua    # 对线: 前期赖线、补刀、反补
  mode_farm_generic.lua      # 刷钱: 野区 / 线上刷钱
  mode_push_generic.lua      # 推塔 (通用实现)
  mode_push_tower_mid/bot/top_generic.lua  # 推塔三分路包装
  mode_retreat_generic.lua   # 撤退: 血量低 / 敌多我少时回塔 / 回泉
  mode_attack_generic.lua    # 进攻: 打集火目标, 连招窗口内优先参团
  mode_roam_generic.lua      # 游走: 4/5 号位中期去别路抓人
  mode_team_roam_generic.lua # 抱团游走: 连招窗口 / 队友集合时一起抓人
  mode_roshan_generic.lua    # 打盾: 敌方减员 + 我方占优 + 20 分钟后
  mode_ward_generic.lua      # 插眼: 背包有眼时去预设点插眼
  mode_defend_tower_generic.lua  # 守塔: 敌方推我方塔时回防
  mode_rune_generic.lua      # 控符: 每 2 分钟前后的符点窗口
  mode_secret_shop_generic.lua   # 秘密商店: 需要秘密商店配件且有钱时去买
  ability_item_usage_generic.lua # 通用技能入口: 救人优先 -> BotLib SkillsComplement() -> 通用物品使用
  item_purchase_generic.lua  # 通用出装入口: 按位置买装的状态机, 读 BotLib 的 sBuyList / sSellList
  bot_<hero>.lua             # 每英雄 1 个薄 wrapper: 只调 ModeDispatcher.Think(bot)
  ability_item_usage_<hero>.lua  # 技能释放 + 加点 (走 BotLib, 加点表来自 SKILL_BUILD)
  item_purchase_<hero>.lua   # 出装 (委托给 item_purchase_generic)
  hero_selection.lua         # 选人: 按阵容补位 + 经典组合协同加分 (见 data/combos.lua)
  BotLib/hero_<name>.lua     # 每英雄 1 个文件: 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()
  data/heroes.lua            # 全英雄数据表 (生成器产物, 不要手改)
  data/talents.lua           # v2.0.0 新增: 天赋表 (焦点英雄自选, 其余按主属性通用)
  data/combos.lua            # 14 组经典组合 + 先手大招表 + 救人英雄表
  engine/
    perception.lua  # 感知: 每 0.25s 快照 + 缓存, 只读己方视野
    utility.lua     # 效用决策: Desire 打分 (供 Mode 参考); 难度表 (thinkDelay / 补刀容错 / 撤退阈值)
    micro.lua       # 微操: 技能按类型抽象释放 (含 channel/summon/escape); 救人优先; 插眼; 信使; 补刀算 0.3s 后的血量
    macro.lua       # 宏观: 每 30s 重评推塔 vs 打盾 vs 刷钱的收益
    team.lua        # 团队黑板 + TeamThink(): 5 人共享意图 + 分路分配 + 连招窗口 + 集火目标
    skill.lua       # v2.0.0 新增: 动态读槽位 (GetAbilityList/GetAbilityMap)、天赋表、施放辅助
    core.lua        # v2.0.0 兼容垫片: Core.Think() 转给 ModeDispatcher.Think(), 不再写决策逻辑
tools/
  heroes_data.py  # 单一事实来源: 127 名英雄 (中英文名/定位/分路/技能类型/加点优先级/招牌装)
  focus_heroes.py # v2.0.0 新增: 10 个焦点英雄的深度数据 (真实技能名 / Consider 条件 / 天赋自选 / 分位置出装)
  generate.py     # 生成器: 读 heroes_data.py + focus_heroes.py, 产出 heroes.lua + talents.lua + 381 个 per-hero 文件 + 127 个 BotLib 文件
  validate.py     # 校验: luac + 文件齐全 + 计数 + 无占位符 + 主属性 + Invoker 上限 + 无 goldMul/xpMul + combos>=12 + Mode>=12 + BotLib/Consider + GetScriptDirectory 一致 + Lua 5.1 检查 + TeamThink + talents 计数
  verify_v110.lua # v1.1.0 验证测试: 40 项 (已适配 v2.0.0 的 GetScriptDirectory stub 与 Mode 化插眼)
  verify_v200.lua # v2.0.0 验证测试: 71 项, 覆盖 Mode/TeamThink/焦点英雄 Consider/combo/GetScriptDirectory/Lua 5.1/天赋/出装
```

**方法来源与致谢 (v2.0.0):** 架构方法来自 Valve 官方 Bot API 文档的三层结构 (Team / Mode / Action) 与 Open Hyper AI (OHA, forest0xia, MIT 协议) 的 `docs/ARCHITECTURE.md` 描述的目录结构与文件分工 (BotLib 英雄文件分段: 天赋 / 加点 / 分位置出装 / SkillsComplement / Consider)。**本项目所有代码均为原创实现, 未复制 OHA 或其上游 adamqqq (GPLv3) 的任何代码文件, 未拷贝其具体数值、注释与变量名。** OHA 本身基于 Valve 默认 Bot 与多位作者的工作, 本项目在此致谢 Valve 与 OHA 的方法贡献。


**设计原则：**

1. **引擎与数据分离。** 技能抽象成类型（`point_control / aoe_damage / aoe_control / nuke / heal / buff / debuff / blink / summon / passive / execute / channel / aura / escape`），英雄只填表，不写逻辑。版本一变，改 `tools/heroes_data.py` 后重跑生成器即可。
2. **加点表是数据。** `skill_build` 为 1–25 级序列，6/11/16 点大招；全部技能满级后的等级填 `0`，表示该级无技能可点（点天赋），`AbilityLevelUpThink` 会显式跳过（v1.1.0 修：之前靠调 `GetAbilityInSlot(-1)` 意外跳过，现已显式 return）。Invoker 用显式表：Quas/Wex/Exort 各 7 级、Invoke 4 级，2 级点 Invoke。
3. **出装是数据。** `items = { early / mid / late / situational }`，按位置给模板 + 每英雄 3 件招牌装；`Micro.TryBuyNextItem` 按顺序逐件买，第一件没钱就不跳过去买后面的。
4. **不作弊。** 感知只用己方视野内的 `GetNearbyHeroes / GetNearbyCreeps / GetNearbyTowers`，没有全图视野，没有读敌方不可见信息。v1.1.0 诚实说明：Lua Bot 脚本没有给 Bot 发金钱/经验的 API，v1.0 的“疯狂档 1.25 倍金钱经验”是纸面数字，已删除；真正的引擎级 Unfair 由房间难度控制，本项目 Unfair 只靠反应延迟和决策阈值区分。
5. **英雄互动（v1.1.0 新增，v2.0.0 保留并搬进 Mode）。** 见下文“英雄互动”一节：连招窗口、集火、救人优先、选人协同；attack / team_roam 模式读连招窗口，attack 模式打 FocusTarget，技能入口先跑救人。
6. **焦点英雄深度（v2.0.0 新增）。** 10 个焦点英雄（axe / zeus / lion / crystal_maiden / magnus / faceless_void / enigma / dazzle / oracle / huskar）是真实 Consider 逻辑，其余 117 个是通用类型驱动 fallback——这正是 dragonghy fork 的策略：先把少数英雄做深，再扩覆盖。
7. **Lua 5.1 兼容。** Dota 的 Lua VM 是 5.1，不是 5.4；全仓库禁用 goto / table.unpack / // / 位运算，`validate.py` 有专门检查。`require` 全用 `require(GetScriptDirectory() .. "/...")` 的 Valve 写法，测试里用同名 stub。

## 安装

### 方法 A：Steam Workshop Tools（推荐，可订阅更新）

1. Steam 库 → Dota 2 → 属性 → DLC → 安装 **Dota 2 Workshop Tools**。
2. 把本仓库内容作为一个 Workshop Addon 导入（`addoninfo.txt` 已写好标题与描述），在 Workshop Tools 里 Build 并上传。
3. 游戏内建房间 → 选择该 Addon → 填满 Bot → 开始。

### 方法 B：手动复制（最快，不用等 Workshop 审核）

1. 找到 Dota 2 安装目录，例如 `Steam/steamapps/common/dota 2 beta/`。
2. 把 `scripts/` 整个复制到 `game/dota/scripts/` 下（与游戏自带的 `scripts/vscripts/bots/` 合并；**先备份原 `bots/` 文件夹**）。
3. 启动 Dota 2 → 建本地房间 → 选“填充 Bot”→ 开始。默认难度为困难（3）。

> 注意：本仓库是 Bot 脚本 Addon，不是替换游戏本体文件。方法 B 覆盖的是 `game/dota/scripts/vscripts/bots/` 下的同名文件，卸载时恢复备份即可。

## 难度（4 档，公开调参，不藏作弊）

在 `bot_generic.lua` 里 `_G.DOTA_AI_DIFFICULTY` 默认为 3；房间脚本可改。参数在 `engine/utility.lua` 的 `DIFFICULTY` 表里：

| 档 | 名称 | 反应延迟（thinkDelay，Core 真正节流） | 补刀容错 | 撤退血量阈值 | 激进程度 |
|---|---|---|---|---|---|
| 1 | 简单 | 0.50s | 25 | 55% | 0.35 |
| 2 | 中等 | 0.30s | 12 | 45% | 0.55 |
| 3 | 困难 | 0.15s | 5 | 35% | 0.75 |
| 4 | 疯狂 | 0.10s | 0 | 25% | 0.95 |

没有任何一档有金钱/经验加成：Lua Bot 脚本没有发金钱/经验的 API，v1.0 表里的金钱经验系数是纸面数字，v1.1.0 已删除。难度只靠反应延迟、补刀容错、撤退阈值、激进程度区分；想要引擎级数值加成的 Unfair，请用房间难度设置。

## 校验结果（本机实测，2026-11-09，v2.0.0）

```bash
python3 tools/generate.py   # heroes: 127 / per-hero files: 381 + BotLib 127 / focus: 10
python3 tools/validate.py   # lua files: 539, validator: /usr/bin/luac, errors: 0, warnings: 0 -> VALIDATION PASSED
lua5.4 tools/verify_v110.lua  # VERIFY_V110 PASSED: 40 checks (已适配 v2.0.0)
lua5.4 tools/verify_v200.lua  # VERIFY_V200 PASSED: 71 checks
```

`verify_v110.lua` 是 v1.1.0 新增的独立验证（不是原来那个返回 nil 技能的弱 smoke）：技能 mock 带 `IsNull()=false` 等真实方法，覆盖 channel 单体/范围、summon、aura/passive 跳过、escape、thinkDelay 节流（简单 0.5s / 困难 0.15s）、打盾分、插眼、15 级不查 -1 槽位、Invoker 上限、主属性计数、朗戈定位、连招窗口、集火、救人、选人协同、防重叠、信使。

- `luac`：本机已装 Lua 5.4.6（`apt-get install lua5.4`），用的是真 `luac -p`，不是 Python 括号检查。
- 冒烟测试用 mock Bot（假的 `GetBot / DotaTime / GetItemCost`）跑通了 `Core.Think`、选人补位和三个英雄的 `Think()`。**这不是真机对局测试**——真机测试仍需在 Dota 2 里建房间跑（见“已知限制”）。

## 英雄覆盖表（127 名，全部）

| 英文名 | 中文名 | 主属性 | 位置 | 分路 | 技能类型（4 位） | 招牌装 |
|---|---|---|---|---|---|---|
| Abaddon | 亚巴顿 | universal | 3, 5 | offlane | nuke, buff, passive, buff | item_vanguard, item_radiance, item_blink |
| Alchemist | 炼金术士 | str | 1, 2 | safelane | aoe_damage, point_control, passive, buff | item_radiance, item_black_king_bar, item_abyssal_blade |
| Ancient Apparition | 远古冰魄 | int | 5 | support | debuff, aoe_damage, buff, execute | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Anti-Mage | 敌法师 | agi | 1 | safelane | passive, blink, buff, aoe_damage | item_battle_fury, item_manta, item_abyssal_blade |
| Arc Warden | 天穹守望者 | universal | 2, 1 | mid | nuke, buff, aoe_damage, summon | item_hand_of_midas, item_manta, item_hurricane_pike |
| Axe | 斧王 | str | 3 | offlane | aoe_control, debuff, passive, execute | item_blink, item_blade_mail, item_black_king_bar |
| Bane | 祸乱之源 | universal | 5, 4 | support | debuff, nuke, point_control, channel | item_aether_lens, item_glimmer_cape, item_black_king_bar |
| Batrider | 蝙蝠骑士 | universal | 3, 2 | offlane | debuff, aoe_damage, buff, point_control | item_blink, item_force_staff, item_black_king_bar |
| Beastmaster | 兽王 | universal | 3 | offlane | aoe_damage, summon, aura, point_control | item_helm_of_the_dominator, item_blink, item_aghanims_scepter |
| Bloodseeker | 血魔 | agi | 1, 2 | safelane | buff, aoe_damage, passive, debuff | item_blade_mail, item_black_king_bar, item_sange_and_yasha |
| Bounty Hunter | 赏金猎人 | agi | 4 | roam | nuke, passive, blink, debuff | item_diffusal_blade, item_solar_crest, item_black_king_bar |
| Brewmaster | 酒仙 | universal | 3 | offlane | aoe_damage, debuff, passive, summon | item_radiance, item_blink, item_black_king_bar |
| Bristleback | 钢背兽 | str | 3 | offlane | debuff, aoe_damage, passive, buff | item_vanguard, item_crimson_guard, item_black_king_bar |
| Broodmother | 育母蜘蛛 | agi | 1, 3 | safelane | buff, buff, summon, aoe_damage | item_orchid, item_black_king_bar, item_bloodthorn |
| Centaur Warrunner | 半人马战行者 | str | 3 | offlane | aoe_control, nuke, passive, buff | item_blink, item_heart, item_black_king_bar |
| Chaos Knight | 混沌骑士 | str | 1 | safelane | point_control, debuff, passive, summon | item_armlet, item_manta, item_heart |
| Chen | 陈 | int | 5 | support | debuff, summon, heal, heal | item_hand_of_midas, item_aghanims_scepter, item_pipe_of_insight |
| Clinkz | 克林克兹 | agi | 1, 2 | safelane | buff, debuff, blink, buff | item_desolator, item_black_king_bar, item_daedalus |
| Clockwerk | 发条技师 | str | 3, 4 | offlane | aoe_damage, aoe_control, nuke, blink | item_blade_mail, item_force_staff, item_aghanims_scepter |
| Crystal Maiden | 水晶室女 | int | 5 | support | aoe_damage, point_control, aura, channel | item_glimmer_cape, item_force_staff, item_black_king_bar |
| Dark Seer | 黑暗贤者 | int | 3 | offlane | aoe_control, buff, buff, summon | item_arcane_boots, item_pipe_of_insight, item_shivas_guard |
| Dark Willow | 邪影芳灵 | int | 4, 5 | support | aoe_control, blink, point_control, aoe_control | item_euls_scepter_of_divinity, item_glimmer_cape, item_black_king_bar |
| Dawnbreaker | 破晓辰星 | str | 3, 1 | offlane | aoe_damage, aoe_damage, heal, aoe_damage | item_desolator, item_black_king_bar, item_assault |
| Dazzle | 戴泽 | universal | 5 | support | debuff, buff, heal, buff | item_force_staff, item_glimmer_cape, item_aghanims_scepter |
| Death Prophet | 死亡先知 | universal | 2 | mid | aoe_damage, aoe_control, debuff, summon | item_euls_scepter_of_divinity, item_black_king_bar, item_octarine_core |
| Disruptor | 干扰者 | int | 5 | support | nuke, debuff, aoe_control, aoe_damage | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Doom | 末日使者 | str | 3, 1 | offlane | buff, buff, debuff, point_control | item_radiance, item_blink, item_black_king_bar |
| Dragon Knight | 龙骑士 | str | 1, 2, 3 | safelane | aoe_damage, point_control, passive, buff | item_armlet, item_black_king_bar, item_assault |
| Drow Ranger | 卓尔游侠 | agi | 1 | safelane | debuff, aoe_control, aoe_damage, passive | item_dragon_lance, item_hurricane_pike, item_black_king_bar |
| Earth Spirit | 大地之灵 | str | 4, 2 | roam | aoe_damage, blink, point_control, aoe_damage | item_euls_scepter_of_divinity, item_blink, item_black_king_bar |
| Earthshaker | 撼地者 | str | 4, 3 | roam | aoe_control, buff, passive, aoe_damage | item_blink, item_black_king_bar, item_aghanims_scepter |
| Elder Titan | 上古巨神 | str | 3, 4 | offlane | aoe_damage, buff, aura, aoe_control | item_blink, item_shivas_guard, item_black_king_bar |
| Ember Spirit | 灰烬之灵 | agi | 2, 1 | mid | aoe_damage, blink, debuff, summon | item_maelstrom, item_black_king_bar, item_desolator |
| Enchantress | 魅惑魔女 | int | 5, 4 | support | debuff, heal, passive, nuke | item_force_staff, item_glimmer_cape, item_hurricane_pike |
| Enigma | 谜团 | universal | 3, 4 | offlane | debuff, summon, aura, aoe_control | item_blink, item_black_king_bar, item_refresher_orb |
| Faceless Void | 虚空假面 | agi | 1 | safelane | blink, passive, debuff, aoe_control | item_maelstrom, item_black_king_bar, item_manta |
| Grimstroke | 天涯墨客 | int | 5, 4 | support | nuke, debuff, buff, point_control | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Gyrocopter | 矮人直升机 | agi | 1 | safelane | aoe_damage, buff, passive, aoe_damage | item_maelstrom, item_black_king_bar, item_satanic |
| Hoodwink | 森海飞霞 | agi | 4, 5 | support | point_control, buff, debuff, aoe_damage | item_glimmer_cape, item_force_staff, item_black_king_bar |
| Huskar | 哈斯卡 | str | 1, 2 | safelane | debuff, heal, passive, blink | item_armlet, item_black_king_bar, item_satanic |
| Invoker | 祈求者 | int | 2 | mid | nuke, nuke, nuke, buff, aoe_damage, point_control | item_aghanims_scepter, item_black_king_bar, item_octarine_core |
| Io | 艾欧 | universal | 5, 4 | support | buff, heal, buff, blink | item_mechanism, item_pipe_of_insight, item_lotus_orb |
| Jakiro | 杰奇洛 | int | 5 | support | aoe_damage, aoe_damage, debuff, channel | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Juggernaut | 主宰 | agi | 1 | safelane | heal, buff, passive, aoe_damage | item_battle_fury, item_manta, item_abyssal_blade |
| Keeper of the Light | 光之守卫 | int | 5 | support | aoe_damage, buff, debuff, aoe_damage | item_aether_lens, item_force_staff, item_aghanims_scepter |
| Kez | 凯 | agi | 1, 2 | safelane | aoe_damage, blink, debuff, buff | item_echo_sabre, item_black_king_bar, item_manta |
| Kunkka | 昆卡 | str | 2, 3 | mid | aoe_damage, buff, passive, aoe_damage | item_armlet, item_black_king_bar, item_daedalus |
| Legion Commander | 军团指挥官 | str | 3, 1 | offlane | buff, heal, passive, point_control | item_blink, item_blade_mail, item_black_king_bar |
| Leshrac | 拉席克 | int | 2, 3 | mid | aoe_damage, aoe_damage, buff, aoe_damage | item_bloodstone, item_black_king_bar, item_shivas_guard |
| Lich | 巫妖 | int | 5 | support | nuke, debuff, aura, aoe_damage | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Lifestealer | 噬魂鬼 | str | 1 | safelane | debuff, buff, passive, buff | item_armlet, item_desolator, item_black_king_bar |
| Lina | 莉娜 | int | 2, 5 | mid | aoe_control, buff, passive, nuke | item_euls_scepter_of_divinity, item_black_king_bar, item_bloodthorn |
| Lion | 莱恩 | int | 5 | support | point_control, debuff, nuke, execute | item_blink, item_aether_lens, item_aghanims_scepter |
| Lone Druid | 独行德鲁伊 | agi | 1 | safelane | summon, buff, passive, summon | item_radiance, item_black_king_bar, item_assault |
| Luna | 露娜 | agi | 1 | safelane | aoe_damage, buff, aura, aoe_damage | item_manta, item_black_king_bar, item_satanic |
| Lycan | 狼人 | str | 1, 3 | safelane | summon, buff, aura, buff | item_helm_of_the_dominator, item_black_king_bar, item_assault |
| Magnus | 马格纳斯 | universal | 3, 2 | offlane | aoe_damage, buff, aura, aoe_control | item_blink, item_black_king_bar, item_refresher_orb |
| Marci | 玛西 | universal | 3, 4 | offlane | blink, buff, passive, aoe_damage | item_blink, item_black_king_bar, item_assault |
| Mars | 玛尔斯 | str | 3 | offlane | aoe_damage, buff, passive, aoe_control | item_blink, item_black_king_bar, item_desolator |
| Medusa | 美杜莎 | agi | 1 | safelane | aoe_damage, buff, passive, point_control | item_manta, item_butterfly, item_satanic |
| Meepo | 米波 | agi | 2, 1 | mid | aoe_damage, blink, passive, summon | item_blink, item_black_king_bar, item_skadi |
| Mirana | 米拉娜 | agi | 4, 2 | support | aoe_damage, buff, passive, buff | item_aghanims_scepter, item_black_king_bar, item_manta |
| Monkey King | 齐天大圣 | agi | 1, 2 | safelane | aoe_damage, buff, passive, aoe_control | item_echo_sabre, item_black_king_bar, item_desolator |
| Morphling | 变体精灵 | agi | 1 | safelane | nuke, buff, passive, blink | item_manta, item_black_king_bar, item_satanic |
| Muerta | 琼英碧灵 | int | 1, 2 | safelane | nuke, buff, passive, buff | item_maelstrom, item_black_king_bar, item_hurricane_pike |
| Naga Siren | 娜迦海妖 | agi | 1, 3 | safelane | aoe_damage, buff, passive, aoe_control | item_radiance, item_manta, item_heart |
| Nature's Prophet | 自然先知 | universal | 3, 1 | offlane | summon, blink, aura, aoe_damage | item_hand_of_midas, item_black_king_bar, item_orchid |
| Necrophos | 瘟疫法师 | int | 2, 3 | mid | aoe_damage, heal, aura, execute | item_radiance, item_black_king_bar, item_heart |
| Night Stalker | 暗夜魔王 | str | 3, 4 | offlane | debuff, buff, passive, aoe_control | item_echo_sabre, item_black_king_bar, item_abyssal_blade |
| Nyx Assassin | 司夜刺客 | universal | 4 | roam | point_control, aoe_damage, passive, buff | item_dagon, item_black_king_bar, item_aghanims_scepter |
| Ogre Magi | 食人魔魔法师 | str | 5 | support | nuke, buff, passive, buff | item_aether_lens, item_force_staff, item_aghanims_scepter |
| Omniknight | 全能骑士 | str | 3, 5 | offlane | heal, buff, aura, heal | item_pipe_of_insight, item_lotus_orb, item_radiance |
| Oracle | 神谕者 | int | 5 | support | heal, debuff, buff, heal | item_aether_lens, item_force_staff, item_glimmer_cape |
| Outworld Destroyer | 殁境神蚀者 | int | 2 | mid | nuke, buff, passive, aoe_damage | item_meteor_hammer, item_black_king_bar, item_scythe_of_vyse |
| Pangolier | 石鳞剑士 | universal | 3, 2 | offlane | aoe_damage, buff, passive, aoe_control | item_diffusal_blade, item_black_king_bar, item_aghanims_scepter |
| Phantom Assassin | 幻影刺客 | agi | 1 | safelane | blink, passive, debuff, passive | item_battle_fury, item_desolator, item_black_king_bar |
| Phantom Lancer | 幻影长矛手 | agi | 1 | safelane | nuke, buff, passive, summon | item_diffusal_blade, item_manta, item_heart |
| Phoenix | 凤凰 | str | 5, 4 | support | aoe_damage, heal, debuff, aoe_damage | item_shivas_guard, item_black_king_bar, item_radiance |
| Primal Beast | 獸 | str | 3, 2 | offlane | aoe_damage, debuff, passive, aoe_control | item_blink, item_black_king_bar, item_heart |
| Puck | 帕克 | int | 2 | mid | aoe_damage, blink, debuff, aoe_control | item_blink, item_black_king_bar, item_aghanims_scepter |
| Pudge | 帕吉 | str | 4, 3 | roam | point_control, aoe_damage, passive, channel | item_blink, item_black_king_bar, item_aghanims_scepter |
| Pugna | 帕格纳 | int | 2, 5 | mid | nuke, debuff, aura, channel | item_aether_lens, item_black_king_bar, item_dagon |
| Queen of Pain | 痛苦女王 | int | 2 | mid | aoe_damage, blink, passive, aoe_damage | item_orchid, item_black_king_bar, item_bloodthorn |
| Razor | 剃刀 | agi | 2, 1 | mid | debuff, buff, passive, aoe_damage | item_bloodstone, item_black_king_bar, item_refresher_orb |
| Riki | 力丸 | agi | 1, 4 | safelane | aoe_damage, blink, passive, aoe_control | item_diffusal_blade, item_black_king_bar, item_abyssal_blade |
| Ringmaster | 百戏大王 | int | 4, 5 | support | aoe_damage, buff, debuff, aoe_control | item_aether_lens, item_glimmer_cape, item_black_king_bar |
| Rubick | 拉比克 | int | 5, 4 | support | nuke, buff, passive, aoe_control | item_blink, item_aether_lens, item_aghanims_scepter |
| Sand King | 沙王 | universal | 3 | offlane | aoe_damage, buff, passive, aoe_damage | item_blink, item_black_king_bar, item_aghanims_scepter |
| Shadow Demon | 暗影恶魔 | int | 5 | support | point_control, debuff, buff, aoe_damage | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Shadow Fiend | 影魔 | agi | 2 | mid | aoe_damage, passive, debuff, aoe_damage | item_black_king_bar, item_daedalus, item_satanic |
| Shadow Shaman | 暗影萨满 | int | 5 | support | point_control, aoe_damage, debuff, summon | item_blink, item_aether_lens, item_aghanims_scepter |
| Silencer | 沉默术士 | int | 5, 2 | support | debuff, buff, passive, aoe_control | item_force_staff, item_glimmer_cape, item_black_king_bar |
| Skywrath Mage | 天怒法师 | int | 5, 4 | support | nuke, aoe_damage, debuff, aoe_damage | item_aether_lens, item_rod_of_atos, item_black_king_bar |
| Slardar | 斯拉达 | str | 3 | offlane | aoe_control, buff, passive, debuff | item_blink, item_black_king_bar, item_assault |
| Slark | 斯拉克 | agi | 1 | safelane | debuff, buff, passive, aoe_damage | item_echo_sabre, item_black_king_bar, item_abyssal_blade |
| Snapfire | 电炎绝手 | universal | 5, 4 | support | aoe_damage, buff, debuff, aoe_damage | item_force_staff, item_glimmer_cape, item_aghanims_scepter |
| Sniper | 狙击手 | agi | 1, 2 | safelane | aoe_damage, buff, passive, nuke | item_maelstrom, item_hurricane_pike, item_black_king_bar |
| Spectre | 幽鬼 | agi | 1 | safelane | debuff, buff, passive, summon | item_radiance, item_manta, item_heart |
| Spirit Breaker | 裂魂人 | str | 4, 3 | roam | blink, buff, passive, point_control | item_shadow_blade, item_black_king_bar, item_assault |
| Storm Spirit | 风暴之灵 | int | 2 | mid | aoe_damage, buff, passive, blink | item_bloodstone, item_black_king_bar, item_orchid |
| Sven | 斯温 | str | 1, 3 | safelane | aoe_control, buff, passive, buff | item_echo_sabre, item_black_king_bar, item_daedalus |
| Techies | 工程师 | universal | 4, 5 | support | aoe_damage, debuff, passive, aoe_damage | item_aether_lens, item_force_staff, item_aghanims_scepter |
| Templar Assassin | 圣堂刺客 | agi | 2 | mid | debuff, buff, passive, aoe_damage | item_desolator, item_black_king_bar, item_daedalus |
| Terrorblade | 恐怖利刃 | agi | 1 | safelane | summon, buff, passive, debuff | item_manta, item_satanic, item_butterfly |
| Tidehunter | 潮汐猎人 | str | 3 | offlane | aoe_damage, buff, passive, aoe_control | item_blink, item_black_king_bar, item_refresher_orb |
| Timbersaw | 伐木机 | str | 3 | offlane | aoe_damage, blink, passive, aoe_damage | item_bloodstone, item_black_king_bar, item_shivas_guard |
| Tinker | 修补匠 | int | 2 | mid | aoe_damage, blink, passive, buff | item_blink, item_black_king_bar, item_aghanims_scepter |
| Tiny | 小小 | str | 2, 3 | mid | aoe_damage, buff, passive, aoe_control | item_blink, item_black_king_bar, item_aghanims_scepter |
| Treant Protector | 树精卫士 | str | 5 | support | debuff, heal, buff, aoe_control | item_meteor_hammer, item_pipe_of_insight, item_lotus_orb |
| Troll Warlord | 巨魔战将 | agi | 1 | safelane | debuff, buff, passive, buff | item_battle_fury, item_black_king_bar, item_satanic |
| Tusk | 巨牙海民 | str | 4, 3 | roam | aoe_damage, buff, passive, aoe_control | item_blink, item_black_king_bar, item_aghanims_scepter |
| Underlord | 孽主 | str | 3 | offlane | aoe_damage, buff, aura, blink | item_pipe_of_insight, item_crimson_guard, item_black_king_bar |
| Undying | 不朽尸王 | str | 5, 4 | support | debuff, heal, aura, summon | item_meteor_hammer, item_pipe_of_insight, item_aghanims_scepter |
| Ursa | 熊战士 | agi | 1 | safelane | debuff, buff, passive, aoe_damage | item_blink, item_black_king_bar, item_abyssal_blade |
| Vengeful Spirit | 复仇之魂 | agi | 5, 4 | support | aoe_control, debuff, aura, blink | item_aether_lens, item_force_staff, item_aghanims_scepter |
| Venomancer | 剧毒术士 | universal | 3, 5 | offlane | debuff, summon, passive, aoe_damage | item_veil_of_discord, item_force_staff, item_aghanims_scepter |
| Viper | 毒龙 | agi | 2, 3 | mid | debuff, buff, passive, aoe_damage | item_hurricane_pike, item_black_king_bar, item_manta |
| Visage | 维萨吉 | universal | 3, 5 | offlane | debuff, buff, passive, summon | item_pipe_of_insight, item_aghanims_scepter, item_shivas_guard |
| Void Spirit | 虚无之灵 | universal | 2, 3 | mid | aoe_damage, buff, passive, blink | item_euls_scepter_of_divinity, item_black_king_bar, item_aghanims_scepter |
| Warlock | 术士 | int | 5 | support | debuff, heal, buff, summon | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Weaver | 编织者 | agi | 1, 4 | safelane | debuff, buff, passive, blink | item_diffusal_blade, item_black_king_bar, item_linkens_sphere |
| Windranger | 风行者 | universal | 2, 4 | mid | aoe_damage, buff, passive, aoe_damage | item_maelstrom, item_black_king_bar, item_aghanims_scepter |
| Winter Wyvern | 寒冬飞龙 | int | 5 | support | heal, buff, debuff, aoe_control | item_aether_lens, item_glimmer_cape, item_force_staff |
| Witch Doctor | 巫医 | int | 5 | support | aoe_control, heal, debuff, channel | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Wraith King | 骷髅王 | str | 1 | safelane | point_control, aura, passive, buff | item_radiance, item_black_king_bar, item_assault |
| Zeus | 宙斯 | int | 2, 5 | mid | aoe_damage, aoe_damage, passive, aoe_damage | item_aether_lens, item_black_king_bar, item_octarine_core |
| Largo | 朗戈 | str | 4, 5 | support | debuff, buff, summon, aoe_control | item_force_staff, item_glimmer_cape, item_black_king_bar |
> 注：Invoker 有 6 个技能位（Quas/Wex/Exort/Invoke + 2 个大招位），其 `skill_build` 是显式 25 级表（Quas/Wex/Exort 各 7、Invoke 4，2 级点 Invoke），validate.py 会断言上限；其余英雄均为 4 个技能位。Meepo / 陈 / 弧光守卫等多单位微操目前走通用召唤逻辑，未做独立多单位微操，是已知短板（见下文）。


## 英雄互动（v1.1.0 新增）

数据在 `scripts/vscripts/bots/data/combos.lua`，逻辑在 `engine/team.lua` / `engine/micro.lua` / `engine/utility.lua` / `hero_selection.lua`，测试在 `tools/verify_v110.lua` 第 5 节。

* **连招窗口 ComboWindow：**任一 Bot 放出大型先手/控制大招（aoe_control / channel 类大招，如黑洞、时间结界、潮汐大、猛犸大）时，把位置、时间、释放者写进黑板；5 秒内队友参团分 +0.25 并走向窗口位置，优先放自己的 AoE 跟进；窗口开启后 2 秒内，别人不重复放自己的同类先手大，避免黑洞+时间结界重叠浪费。
* **集火 FocusTarget：**黑板维护共享目标 = 所有 Bot 可见敌方里血量百分比最低的；团战时所有 Bot 优先攻击该目标，而不是各打各的最近目标。`Team.GetFocusTarget()`，`Core` 的 teamfight 分支使用它。
* **救人优先：**放进攻技能之前先检查队友：有队友血量 <35% 且本英雄在救人表里、有 heal/buff 技能（戴泽薄葬、神谕者大、亚巴顿盾、艾欧牵引等），优先给该队友放救人技能，而不是打敌方。
* **选人协同：**`SelectHero` 在补位之外按经典组合加分，协同分最高的优先。14 组组合：Magnus+Faceless Void、Magnus+Enigma、Magnus+Sven、Io+Tiny、Io+Chaos Knight、Io+Spectre、Dark Seer+Enigma、Dark Seer+Faceless Void、Dark Seer+Tidehunter、Oracle+Huskar、Dazzle+Huskar、Enigma+Jakiro、Enigma+Crystal Maiden、Faceless Void+Lina。

## 已知限制（实话）

1. **未做真机对局测试。** 本机无 Dota 2 客户端，只能做 `luac` 语法校验 + mock 冒烟测试。第一次进游戏前，务必先开一局 1v1 / 5v5 本地房间，确认 Bot 不卡在泉水、不无限回塔、不买错装备。
2. **出装与加点是“合理模板 + 招牌装”，不是逐版本的最优解。** 7.41f 的数值细节（例如某件装备改价、某技能重做）需要按补丁更新 `tools/heroes_data.py` 后重跑生成器。
3. **多单位微操弱。** Meepo、陈、德鲁伊、育母蜘蛛等召唤/多单位英雄目前用通用召唤逻辑控制（v1.1.0 已能放出召唤技能），没有独立的分身微操。
4. **视野 / 烟雾 / 假眼博弈弱。** v1.1.0 已实现基础插眼（辅助背包有眼时按河道/己方野区/敌方野区轮换插眼）和信使送货，但买雾时机、反眼、精确眼位悬崖仍是基础规则，没有读敌方动向的博弈层。
5. **肉山坑坐标是固定值。** `engine/macro.lua` 用的坑位坐标按 7.38+ 常规坑位写死，不同版本若移坑需改一处常量。
6. **没有机器学习。** 这是规则 + 效用打分系统，不是 OpenAI Five 式强化学习；“AI”指 Bot AI，不指神经网络。
7. **v2.0.0 仍没有 OHA 的这些：** 中立物品系统、多游戏模式（Turbo / AR / 队长模式等，本项目只按 AP 思路写）、Bot 聊天 / 游戏内指令（`!pick / !ban / !pos`）、小兵 / 召唤物独立微操、Rubick 偷技能等特殊英雄逻辑。Mode 文件是本项目自己写的 15 个，OHA 有 21 个 Mode 文件 + 8,429 行的通用技能入口 + 32k 行的 FretBots——深度仍有差距，见正文对比。
8. **天赋是自选，不是官方推荐。** 10 个焦点英雄的天赋左右选择是本项目自选的可玩方案，其余按主属性通用表；不是逐版本的最优天赋。

## 更新流程（随版本更新）

```bash
# 1. 改数据（只改这里；焦点英雄改 tools/focus_heroes.py）
vim tools/heroes_data.py
# 2. 重新生成（heroes.lua + talents.lua + 381 个文件 + 127 个 BotLib 文件全部重写）
python3 tools/generate.py
# 3. 校验 + 验证（两套都全过才算完）
python3 tools/validate.py
lua5.4 tools/verify_v110.lua  # v1.1.0 回归: 40 项
lua5.4 tools/verify_v200.lua  # v2.0.0: 71 项
```

## 许可证

本项目为社区 Bot 脚本，Dota 2 及英雄/物品名称版权归 Valve 所有。架构方法致谢 Valve 官方 Bot API 文档与 Open Hyper AI (forest0xia, MIT) 的 ARCHITECTURE.md；本项目代码均为原创，未复制 OHA 或其上游代码。
