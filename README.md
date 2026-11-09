# Dota 2 AI — 引擎 + 数据驱动的 Bot AI

一整套、可安装、可跑的 Dota 2 Workshop Bot AI。**不是 124 份手写脚本**，而是一个引擎 + 一张英雄数据表 + 生成器。

> 版本基准：**7.41f，127 名英雄**。任务原文写“约 124 名”时还是 7.38 口径；经核实（Valve 官方英雄页 / datafeed，2026-11-09），2025-12-16 的 7.40 加入 **朗戈 Largo** 后总数为 **127**，此处按 127 名交付，一个不少。中文名以 dota2.com.cn 为准（已核实：Snapfire = 电炎绝手、Arc Warden = 天穹守望者、Outworld Destroyer = 殁境神蚀者、Pangolier = 石鳞剑士、Muerta = 琼英碧灵、Ringmaster = 百戏大王、Largo = 朗戈）。

## 统计（实测）

| 项目 | 数量 |
|---|---|
| 英雄总数 | 127 |
| 每英雄文件（bot / ability_item_usage / item_purchase） | 381（3 × 127） |
| Lua 文件总数 | 390（381 + bot_generic + hero_selection + 6 个引擎 + heroes.lua） |
| 引擎文件 | 6（perception / utility / micro / macro / team / core） |
| 出装涉及的不同物品 | 64（均为真实物品名） |
| 校验 | `luac -p` 全过，0 错误 0 警告；见下文 |

分路分布（本项目分路分配）：{'offlane': 30, 'safelane': 34, 'support': 33, 'mid': 23, 'roam': 7}。主属性字段仅作信息展示，不参与决策，见 heroes_data.py 注释。

## 架构

```
scripts/vscripts/bots/
  bot_generic.lua            # 通用入口：没有专属文件时走这里，只转发给 engine/core
  bot_<hero>.lua             # 每英雄 1 个薄 wrapper：只调 Core.Think(bot)
  ability_item_usage_<hero>.lua  # 技能释放 + 加点（加点表来自 heroes.lua）
  item_purchase_<hero>.lua   # 出装（顺序来自 heroes.lua 的 items 表）
  hero_selection.lua         # 选人：按阵容补位（缺哪个位置补哪个）
  data/heroes.lua            # 全英雄数据表（生成器产物，不要手改）
  engine/
    perception.lua  # 感知：每 0.25s 快照 + 缓存，避免每帧全图扫描；只读己方视野
    utility.lua     # 效用决策：补刀/推线/打野/参团/撤退/打盾等 Desire 打分，选最高
    micro.lua       # 微操：技能按类型抽象释放；补刀算 0.3s 后的血量，不是当前血量
    macro.lua       # 宏观：每 30s 重评推塔 vs 打盾 vs 刷钱的收益，选最大的
    team.lua        # 团队黑板：5 人共享意图 + 分路分配，带过期失效
    core.lua        # 门面：感知 -> 打分 -> 微操 -> 执行，串成一个 Think()
tools/
  heroes_data.py  # 单一事实来源：127 名英雄（中英文名/定位/分路/技能类型/加点优先级/招牌装）
  generate.py     # 生成器：读 heroes_data.py，产出 heroes.lua + 381 个 per-hero 文件
  validate.py     # 校验：luac 语法 + 文件齐全 + 计数一致 + 无 TODO/占位符
  smoke_test.lua  # 运行时冒烟测试：mock Bot 跑 Core.Think / 选人 / 三个英雄的 Think
```

**设计原则：**

1. **引擎与数据分离。** 技能抽象成类型（`point_control / aoe_damage / aoe_control / nuke / heal / buff / debuff / blink / summon / passive / execute / channel / aura / escape`），英雄只填表，不写逻辑。版本一变，改 `tools/heroes_data.py` 后重跑生成器即可。
2. **加点表是数据。** `skill_build` 为 1–25 级序列，6/11/16 点大招；全部技能满级后的等级填 `0`，表示该级无技能可点（点天赋），`AbilityLevelUpThink` 会跳过，不会去点一个已满级的技能。
3. **出装是数据。** `items = { early / mid / late / situational }`，按位置给模板 + 每英雄 3 件招牌装；`Micro.TryBuyNextItem` 按顺序逐件买，第一件没钱就不跳过去买后面的。
4. **不作弊（除疯狂档公开加成外）。** 感知只用己方视野内的 `GetNearbyHeroes / GetNearbyCreeps / GetNearbyTowers`，没有全图视野，没有读敌方不可见信息。

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

| 档 | 名称 | 反应延迟 | 补刀容错 | 撤退血量阈值 | 激进程度 | 金钱/经验系数 |
|---|---|---|---|---|---|---|
| 1 | 简单 | 0.50s | 25 | 55% | 0.35 | 1.0 / 1.0 |
| 2 | 中等 | 0.30s | 12 | 45% | 0.55 | 1.0 / 1.0 |
| 3 | 困难 | 0.15s | 5 | 35% | 0.75 | 1.0 / 1.0 |
| 4 | 疯狂 | 0.10s | 0 | 25% | 0.95 | **1.25 / 1.25** |

只有疯狂档有数值加成，且写在这里、写在代码注释里。1–3 档没有任何金钱经验加成，纯靠反应与决策阈值区分。

## 校验结果（本机实测，2026-11-09）

```bash
python3 tools/generate.py   # heroes: 127 / per-hero files: 381
python3 tools/validate.py   # lua files: 390, validator: /usr/bin/luac, errors: 0, warnings: 0 -> VALIDATION PASSED
lua5.4 tools/smoke_test.lua  # SMOKE OK: Core.Think x2, 英雄查找, 选人, bot_axe/zeus/largo 的 Think 均无错误
```

- `luac`：本机已装 Lua 5.4.6（`apt-get install lua5.4`），用的是真 `luac -p`，不是 Python 括号检查。
- 冒烟测试用 mock Bot（假的 `GetBot / DotaTime / GetItemCost`）跑通了 `Core.Think`、选人补位和三个英雄的 `Think()`。**这不是真机对局测试**——真机测试仍需在 Dota 2 里建房间跑（见“已知限制”）。

## 英雄覆盖表（127 名，全部）

| 英文名 | 中文名 | 主属性 | 位置 | 分路 | 技能类型（4 位） | 招牌装 |
|---|---|---|---|---|---|---|
| Abaddon | 亚巴顿 | str | 3, 5 | offlane | nuke, buff, passive, buff | item_vanguard, item_radiance, item_blink |
| Alchemist | 炼金术士 | str | 1, 2 | safelane | aoe_damage, point_control, passive, buff | item_radiance, item_black_king_bar, item_abyssal_blade |
| Ancient Apparition | 远古冰魄 | int | 5 | support | debuff, aoe_damage, buff, execute | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Anti-Mage | 敌法师 | agi | 1 | safelane | passive, blink, buff, aoe_damage | item_battle_fury, item_manta, item_abyssal_blade |
| Arc Warden | 天穹守望者 | universal | 2, 1 | mid | nuke, buff, aoe_damage, summon | item_hand_of_midas, item_manta, item_hurricane_pike |
| Axe | 斧王 | str | 3 | offlane | aoe_control, debuff, passive, execute | item_blink, item_blade_mail, item_black_king_bar |
| Bane | 祸乱之源 | int | 5, 4 | support | debuff, nuke, point_control, channel | item_aether_lens, item_glimmer_cape, item_black_king_bar |
| Batrider | 蝙蝠骑士 | int | 3, 2 | offlane | debuff, aoe_damage, buff, point_control | item_blink, item_force_staff, item_black_king_bar |
| Beastmaster | 兽王 | str | 3 | offlane | aoe_damage, summon, aura, point_control | item_helm_of_the_dominator, item_blink, item_aghanims_scepter |
| Bloodseeker | 血魔 | agi | 1, 2 | safelane | buff, aoe_damage, passive, debuff | item_blade_mail, item_black_king_bar, item_sange_and_yasha |
| Bounty Hunter | 赏金猎人 | agi | 4 | roam | nuke, passive, blink, debuff | item_diffusal_blade, item_solar_crest, item_black_king_bar |
| Brewmaster | 酒仙 | str | 3 | offlane | aoe_damage, debuff, passive, summon | item_radiance, item_blink, item_black_king_bar |
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
| Dazzle | 戴泽 | int | 5 | support | debuff, buff, heal, buff | item_force_staff, item_glimmer_cape, item_aghanims_scepter |
| Death Prophet | 死亡先知 | int | 2 | mid | aoe_damage, aoe_control, debuff, summon | item_euls_scepter_of_divinity, item_black_king_bar, item_octarine_core |
| Disruptor | 干扰者 | int | 5 | support | nuke, debuff, aoe_control, aoe_damage | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Doom | 末日使者 | str | 3, 1 | offlane | buff, buff, debuff, point_control | item_radiance, item_blink, item_black_king_bar |
| Dragon Knight | 龙骑士 | str | 1, 2, 3 | safelane | aoe_damage, point_control, passive, buff | item_armlet, item_black_king_bar, item_assault |
| Drow Ranger | 卓尔游侠 | agi | 1 | safelane | debuff, aoe_control, aoe_damage, passive | item_dragon_lance, item_hurricane_pike, item_black_king_bar |
| Earth Spirit | 大地之灵 | str | 4, 2 | roam | aoe_damage, blink, point_control, aoe_damage | item_euls_scepter_of_divinity, item_blink, item_black_king_bar |
| Earthshaker | 撼地者 | str | 4, 3 | roam | aoe_control, buff, passive, aoe_damage | item_blink, item_black_king_bar, item_aghanims_scepter |
| Elder Titan | 上古巨神 | str | 3, 4 | offlane | aoe_damage, buff, aura, aoe_control | item_blink, item_shivas_guard, item_black_king_bar |
| Ember Spirit | 灰烬之灵 | agi | 2, 1 | mid | aoe_damage, blink, debuff, summon | item_maelstrom, item_black_king_bar, item_desolator |
| Enchantress | 魅惑魔女 | int | 5, 4 | support | debuff, heal, passive, nuke | item_force_staff, item_glimmer_cape, item_hurricane_pike |
| Enigma | 谜团 | int | 3, 4 | offlane | debuff, summon, aura, aoe_control | item_blink, item_black_king_bar, item_refresher_orb |
| Faceless Void | 虚空假面 | agi | 1 | safelane | blink, passive, debuff, aoe_control | item_maelstrom, item_black_king_bar, item_manta |
| Grimstroke | 天涯墨客 | int | 5, 4 | support | nuke, debuff, buff, point_control | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Gyrocopter | 矮人直升机 | agi | 1 | safelane | aoe_damage, buff, passive, aoe_damage | item_maelstrom, item_black_king_bar, item_satanic |
| Hoodwink | 森海飞霞 | agi | 4, 5 | support | point_control, buff, debuff, aoe_damage | item_glimmer_cape, item_force_staff, item_black_king_bar |
| Huskar | 哈斯卡 | str | 1, 2 | safelane | debuff, heal, passive, blink | item_armlet, item_black_king_bar, item_satanic |
| Invoker | 祈求者 | int | 2 | mid | nuke, nuke, nuke, buff, aoe_damage, point_control | item_aghanims_scepter, item_black_king_bar, item_octarine_core |
| Io | 艾欧 | str | 5, 4 | support | buff, heal, buff, blink | item_mechanism, item_pipe_of_insight, item_lotus_orb |
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
| Magnus | 马格纳斯 | str | 3, 2 | offlane | aoe_damage, buff, aura, aoe_control | item_blink, item_black_king_bar, item_refresher_orb |
| Marci | 玛西 | str | 3, 4 | offlane | blink, buff, passive, aoe_damage | item_blink, item_black_king_bar, item_assault |
| Mars | 玛尔斯 | str | 3 | offlane | aoe_damage, buff, passive, aoe_control | item_blink, item_black_king_bar, item_desolator |
| Medusa | 美杜莎 | agi | 1 | safelane | aoe_damage, buff, passive, point_control | item_manta, item_butterfly, item_satanic |
| Meepo | 米波 | agi | 2, 1 | mid | aoe_damage, blink, passive, summon | item_blink, item_black_king_bar, item_skadi |
| Mirana | 米拉娜 | agi | 4, 2 | support | aoe_damage, buff, passive, buff | item_aghanims_scepter, item_black_king_bar, item_manta |
| Monkey King | 齐天大圣 | agi | 1, 2 | safelane | aoe_damage, buff, passive, aoe_control | item_echo_sabre, item_black_king_bar, item_desolator |
| Morphling | 变体精灵 | agi | 1 | safelane | nuke, buff, passive, blink | item_manta, item_black_king_bar, item_satanic |
| Muerta | 琼英碧灵 | int | 1, 2 | safelane | nuke, buff, passive, buff | item_maelstrom, item_black_king_bar, item_hurricane_pike |
| Naga Siren | 娜迦海妖 | agi | 1, 3 | safelane | aoe_damage, buff, passive, aoe_control | item_radiance, item_manta, item_heart |
| Nature's Prophet | 自然先知 | int | 3, 1 | offlane | summon, blink, aura, aoe_damage | item_hand_of_midas, item_black_king_bar, item_orchid |
| Necrophos | 瘟疫法师 | int | 2, 3 | mid | aoe_damage, heal, aura, execute | item_radiance, item_black_king_bar, item_heart |
| Night Stalker | 暗夜魔王 | str | 3, 4 | offlane | debuff, buff, passive, aoe_control | item_echo_sabre, item_black_king_bar, item_abyssal_blade |
| Nyx Assassin | 司夜刺客 | agi | 4 | roam | point_control, aoe_damage, passive, buff | item_dagon, item_black_king_bar, item_aghanims_scepter |
| Ogre Magi | 食人魔魔法师 | int | 5 | support | nuke, buff, passive, buff | item_aether_lens, item_force_staff, item_aghanims_scepter |
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
| Sand King | 沙王 | str | 3 | offlane | aoe_damage, buff, passive, aoe_damage | item_blink, item_black_king_bar, item_aghanims_scepter |
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
| Techies | 工程师 | int | 4, 5 | support | aoe_damage, debuff, passive, aoe_damage | item_aether_lens, item_force_staff, item_aghanims_scepter |
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
| Vengeful Spirit | 复仇之魂 | int | 5, 4 | support | aoe_control, debuff, aura, blink | item_aether_lens, item_force_staff, item_aghanims_scepter |
| Venomancer | 剧毒术士 | int | 3, 5 | offlane | debuff, summon, passive, aoe_damage | item_veil_of_discord, item_force_staff, item_aghanims_scepter |
| Viper | 毒龙 | agi | 2, 3 | mid | debuff, buff, passive, aoe_damage | item_hurricane_pike, item_black_king_bar, item_manta |
| Visage | 维萨吉 | int | 3, 5 | offlane | debuff, buff, passive, summon | item_pipe_of_insight, item_aghanims_scepter, item_shivas_guard |
| Void Spirit | 虚无之灵 | int | 2, 3 | mid | aoe_damage, buff, passive, blink | item_euls_scepter_of_divinity, item_black_king_bar, item_aghanims_scepter |
| Warlock | 术士 | int | 5 | support | debuff, heal, buff, summon | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Weaver | 编织者 | agi | 1, 4 | safelane | debuff, buff, passive, blink | item_diffusal_blade, item_black_king_bar, item_linkens_sphere |
| Windranger | 风行者 | int | 2, 4 | mid | aoe_damage, buff, passive, aoe_damage | item_maelstrom, item_black_king_bar, item_aghanims_scepter |
| Winter Wyvern | 寒冬飞龙 | int | 5 | support | heal, buff, debuff, aoe_control | item_aether_lens, item_glimmer_cape, item_force_staff |
| Witch Doctor | 巫医 | int | 5 | support | aoe_control, heal, debuff, channel | item_aether_lens, item_glimmer_cape, item_aghanims_scepter |
| Wraith King | 骷髅王 | str | 1 | safelane | point_control, aura, passive, buff | item_radiance, item_black_king_bar, item_assault |
| Zeus | 宙斯 | int | 2, 5 | mid | aoe_damage, aoe_damage, passive, aoe_damage | item_aether_lens, item_black_king_bar, item_octarine_core |
| Largo | 朗戈 | str | 3, 4 | offlane | aoe_damage, buff, debuff, aoe_control | item_blink, item_black_king_bar, item_shivas_guard |

> 注：Invoker 有 6 个技能位（Quas/Wex/Exort/Invoke + 2 个大招位），其 `skill_build` 按前 4 位循环加点；其余英雄均为 4 个技能位。Meepo / 陈 / 弧光守卫等多单位微操目前走通用召唤逻辑，未做独立多单位微操，是已知短板（见下文）。

## 已知限制（实话）

1. **未做真机对局测试。** 本机无 Dota 2 客户端，只能做 `luac` 语法校验 + mock 冒烟测试。第一次进游戏前，务必先开一局 1v1 / 5v5 本地房间，确认 Bot 不卡在泉水、不无限回塔、不买错装备。
2. **出装与加点是“合理模板 + 招牌装”，不是逐版本的最优解。** 7.41f 的数值细节（例如某件装备改价、某技能重做）需要按补丁更新 `tools/heroes_data.py` 后重跑生成器。
3. **多单位微操弱。** Meepo、陈、德鲁伊、育母蜘蛛等召唤/多单位英雄目前用通用逻辑控制，没有独立的分身微操。
4. **视野 / 烟雾 / 假眼博弈弱。** 插眼点位、买雾时机、反眼目前是基础规则，没有读敌方动向的博弈层。
5. **肉山坑坐标是固定值。** `engine/macro.lua` 用的坑位坐标按 7.38+ 常规坑位写死，不同版本若移坑需改一处常量。
6. **没有机器学习。** 这是规则 + 效用打分系统，不是 OpenAI Five 式强化学习；“AI”指 Bot AI，不指神经网络。

## 更新流程（随版本更新）

```bash
# 1. 改数据（只改这里）
vim tools/heroes_data.py
# 2. 重新生成（heroes.lua + 381 个文件全部重写）
python3 tools/generate.py
# 3. 校验 + 冒烟
python3 tools/validate.py
lua5.4 tools/smoke_test.lua
```

## 许可证

本项目为社区 Bot 脚本，Dota 2 及英雄/物品名称版权归 Valve 所有。
