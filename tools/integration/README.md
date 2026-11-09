# Integration 测试：5v5 全局模拟对局

把真 Bot 脚本放进一局模拟对局里全流程跑起来，测单元测试测不出的东西：
卡住、死循环、互相抢线、打盾不去、买装卡死、团战各打各的。

> **这是一局模拟（simulation），不是真机对局。** 以下所有胜负、人头、
> 补刀数字都只说明“Bot 脚本在模拟世界里能跑通、没有卡住或报错”，
> 不能说成真机 Dota 2 的胜负或强度结论。模拟的简化见文末。

## 怎么跑

仓库根目录，一条命令（`lua5.4`，不要用 `lua`）：

```sh
lua5.4 tools/integration/run.lua
```

默认 40 分钟、tick 1.0 秒、种子 42、难度 3（hard），阵容见下。
跑完打印报告并写到 `tools/integration/last_run.md`，退出码 0 表示 9 个门控全过。

常用参数：

```sh
lua5.4 tools/integration/run.lua --minutes 5 --seed 42        # 快速 5 分钟
lua5.4 tools/integration/run.lua --minutes 40 --seed 7         # 换种子
lua5.4 tools/integration/run.lua --difficulty 2                 # 难度 1-4
lua5.4 tools/integration/run.lua --radiant axe,zeus,lion,crystal_maiden,magnus \
    --dire sven,dazzle,enigma,faceless_void,huskar
lua5.4 tools/integration/run.lua --minutes 11 --trace enigma   # 跟踪单个英雄
lua5.4 tools/integration/run.lua --debug                       # 每 15 秒打全队快照
lua5.4 tools/integration/run.lua --out /tmp/run.md             # 报告写到别处
```

仓库根目录由 `arg[0]` 推导，不依赖绝对路径、不写死 `/home/hatch`。

## 文件

| 文件 | 作用 |
|---|---|
| `sim.lua` | 5v5 世界模型：三路兵线、防御塔、金钱/经验/等级、野区、Roshan、视野/眼位、击杀/复活、基地胜负。Lua 5.4 可跑，Lua 5.1 语法兼容。 |
| `valve_api.lua` | 模拟 Valve Bot API：`GetBot`、`DotaTime`、`GetTeam`、`GetNearbyHeroes/Creeps/Towers`、`GetAbilityInSlot/ByName`、`GetItemInSlot`、`GetCourier`、`Action_MoveToLocation/AttackUnit/UseAbility*/PurchaseItem/LevelAbility/Courier` 等。`GetNearby*` 只返回视野内单位；`Action_*` 真正改变世界（移动改位置、攻击扣血、技能扣蓝进 CD、买装扣钱进背包、插眼改视野），不是只记 log。 |
| `run.lua` | 入口：按 `TeamThink -> 各 Bot Think -> AbilityUsageThink / ItemPurchaseThink / AbilityLevelUpThink` 的顺序每 tick 调用（与 Valve 每帧的调用顺序一致）；每个 Bot 调用包 `pcall` + 指令数上限（防死循环）；写报告 + 9 个门控。 |
| `last_run.md` | 最近一次跑完的报告（每次跑都覆盖）。 |

## 默认阵容

- Radiant：Axe、Zeus、Lion、Crystal Maiden、Magnus
- Dire：Sven、Dazzle、Enigma、Faceless Void、Huskar

## 怎么看报告（`last_run.md`）

- **Gates**：9 个门控，全 PASS 才算通过——0 Lua 错误；胜负已决；
  人头 > 0；推塔 > 0；每个 Bot 都有移动/攻击/买装/升级；
  无 Bot 卡住 60 秒以上；无泉水挂机 120 秒以上；
  打盾计划（TeamThink 定 roshan）触发 ≥1 次；有 ≥2 人参与的团战。
- **Team totals**：每队人头 / 推塔 / 肉山击杀。
- **Per-bot actions**：每 Bot 的等级、K/D/A、补刀/反补、金钱、移动次数/
  里程、攻击指令/命中、放技能次数、买装次数、点技能次数、参团次数、
  是否卡住。
- **Stuck / fountain-camp list**：卡住（60 秒净位移 < 50）和泉水挂机
  （120 秒在泉水 600 内）的 Bot 列表；空表示没有。
- **Errors**：Lua 错误堆栈 + 当时的 tick 和 Bot；空表示没有。
- **Roshan / tower events**：最近 40 条事件（升级、击杀、推塔、肉山、
  复活、胜负）。

## 一局的结果（种子 42，v3.1.0，2026-11-09）

`lua5.4 tools/integration/run.lua`（默认参数）：

- **Radiant 胜**：基地摧毁，20:02；人头 10:2；推塔 7:7；团战 12 场，
  其中 11 场 ≥2 人参与，最多 6 人。
- **0 Lua 错误；0 卡住；0 泉水挂机**；每个 Bot 都有移动/攻击/买装/升级。
- **打盾计划触发 67 tick**（首次 10:25，TeamThink 定 roshan + 打盾模式
  被选中）；**肉山击杀 0**——触发不等于打掉：本局唯一一次成行的打盾
  是 Dire 的 Sven 单人前往 Radiant 侧肉山坑，途中在中路被击杀。
  打盾的队伍协同（多人同去）仍是已知短板，见下。
- 每 Bot 行动数（等级 / K/D/A / 补刀 / 攻击命中 / 放技能 / 买装 / 点技能）：
  Axe 11 / 1/1/4 / 8 / 114 / 32 / 36 / 11；Zeus 17 / 5/1/0 / 55 / 201 / 27 / 57 / 15；
  Lion 12 / 0/0/1 / 20 / 157 / 33 / 38 / 12；Crystal Maiden 11 / 2/1/1 / 22 / 168 / 31 / 36 / 11；
  Magnus 12 / 2/2/2 / 21 / 115 / 26 / 32 / 12；Sven 10 / 1/4/1 / 11 / 92 / 45 / 42 / 10；
  Dazzle 7 / 0/0/0 / 11 / 89 / 26 / 31 / 7；Enigma 5 / 0/0/0 / 10 / 83 / 33 / 10 / 5；
  Faceless Void 10 / 0/4/2 / 9 / 88 / 70 / 34 / 10；Huskar 8 / 1/4/1 / 4 / 83 / 60 / 34 / 8。
- 重跑同一命令结果完全一致（除 wall time 外报告逐字相同），可复现。

## 模拟里修掉的 Bot bug（v3.1.0）

跑模拟的过程中发现并修掉的（只记已修的；修不掉的见“已知限制”）：

1. `tools/integration/valve_api.lua`——`Valve.cast` 丢英雄目标：
   目标解析只认 `_unit`，英雄包装带的是 `_hero`，导致所有对英雄放的
   技能静默失败（Lion 的 voodoo 满蓝 0 次施放）。改成
   `_unit or _hero or targetUnit`。
2. `tools/generate.py` 模板 + `ability_item_usage_generic.lua`——加点把
   攒的点全砸进同一技能：`build[当前等级]` 在一次升多级时把所有点都点
   进同一个技能（Lion 一次升 13 级，20 次调用只点了 voodoo 到 4 级，
   Q/E/R 全 0）。改成由（等级 − 剩余点数）推出下一个 build 位置，
   依次点；天赋级（10/15/20/25）按天赋表点天赋（旧版 build[10] 不是 0，
   10 级天赋永远点不上）。
3. `tools/generate.py` `skill_build`——大招加点用 6/11/16，是 7.00 之前
   的规则；7.00 起大招等级要求是 6/12/18（Dota 2 Wiki / Liquipedia /
   dota2.com 7.00 changelog 三方核对，Meepo 除外）。改成 6/12/18 并重生成。
4. `mode_defend_tower_generic.lua`——GetDesire 误判：己方塔 1600 内且
   1200 内有敌方英雄就给 0.8，哪怕敌方离塔 1200+；导致 Axe 在两个点
   之间每 2 tick 折返、永远走不到兵线。改成仅当最近敌方英雄在最近己方
   塔 900 内才给 0.8；Think 在塔下直接打最近敌人。
5. `mode_push_generic.lua`——Think 到塔下也只下移动指令，塔只能靠小兵
   磨；无塔无目标时去 (0,0)，到了就原地打转、看着小兵路过也不打。
   改成在射程内直接攻击塔；无塔时沿本路攻击移动向敌方半场推进。
6. `mode_laning_generic.lua`——Think 无兵时不下任何指令，泉水边卡住；
   跟随静止小兵（Enigma 的 eidolon 原地待命）会永久站桩；远程英雄在
   最远射程等小兵自己走过来，60 秒以上零位移。改成：无兵去等兵落点
   （棘轮式推进，见 `engine/utility.lua` 的 `GetLaneWaitPoint`）；跟的
   小兵已在身边（≤150）时改去等兵落点。
7. `mode_retreat_generic.lua`——按“离塔 300”切塔/泉两个目的地，一步
   移动（~300/tick）就跨过阈值，残血 Bot 在塔和泉之间每帧折返、净位移
   为零。改成按 Bot 名记一个粘性撤退目标（塔 → 泉单向路线），到塔后
   血量未满继续去泉。
8. `mode_team_roam_generic.lua`——无连招窗口、无可见敌人时不下任何指令，
   但 GetDesire 保底 0.2 会让它长期胜出并站桩。改成找最近队友抱团；
   队友已在身边（≤150）时改去等兵落点（不继承对方的卡住）。
9. `mode_roshan_generic.lua`——只下移动指令，Bot 在坑边干站打不掉肉山。
   改成 400 内攻击移动（真实 Bot API，`pcall` 保护）。
10. `engine/team.lua` + `engine/macro.lua` + `mode_roshan_generic.lua`——
    打盾时间门全是 20:00（`t > 1200`），15–17 分钟结束的对局永远触发
    不了打盾逻辑。统一放宽到 10:00（`t > 600`；真实对局第一条肉山
    常见于 15 分钟前后，有优势阵容更早）。
11. `engine/macro.lua` `GetObjectiveLocation`——打盾目标只取己方半场坑位，
    而模拟肉山在两坑之间轮换（先 Radiant 侧）。Dire 选了 45 tick 打盾
    模式却去了空坑。改成优先用模拟扩展 `GetRoshanLocation()` 取肉山
    实际坑位（无此函数时回落到己方半场坑位；单元测试 mock 不受影响）。
12. `tools/generate.py` 模板 + 重生成 127 个 `ability_item_usage_<hero>.lua`——
    per-hero wrapper 从不调 `Micro.TryUseItems`（通用文件会调），药膏/
    树枝等消耗品永远不用；天赋级直接 return，1 点永远攒着不点天赋。
    改成最后 fallback 调 `TryUseItems`，天赋级按天赋表点天赋。
13. `mode_attack_generic.lua` / `mode_roam_generic.lua` /
    `mode_defend_tower_generic.lua`——同类无指令落点：attack 无目标时
    直接落空、roam 无敌人时去 (0,0) 原地打转、defend_tower 在塔下无敌方
    英雄时直接 return。统一改成打附近小兵或去等兵落点。

## 已知简化（模拟 ≠ 真机）

- 技能伤害、蓝耗、CD、射程是近似值；物品价格是近似值（55 种，未知物品
  默认 500，报告里会列出未知物品数，当前为 0）；每件物品只给 +100 最大
  生命 / +8 攻击（无合成、无组件逻辑、任何地方都能买）。
- 没有真实弹道/投射物；攻击是即时命中；小兵移向目标时不按攻击射程停步，
  会叠到目标脚下（d=0）。
- 没有中立物品、没有聊天、没有符文刷新以外的野区机制细节；
  召唤物（Enigma 的 eidolon 等）原地迎敌、不沿兵线走。
- `GetNearbyTowers` 除塔外还把基地作为最后一项返回（真实 API 只返回塔），
  否则终局推不进去——文档化的模拟偏差。
- 肉山坑边规则：带着去坑的指令（移动/攻击移动/攻击肉山）且在 450 内就
  自动攻击肉山，因为 `mode_roshan` 只下移动指令；另有模拟扩展
  `GetRoshanLocation()`（真实 Valve API 没有）返回肉山实际坑位。
- 双方共用一个 `_G.DOTA_AI_BLACKBOARD`（真机是每队独立 VM），所以
  TeamThink 的黑板数据（减员数、plan）在两队之间会互相覆盖；打盾/
  抱团的判断因此比真机更不稳定。
- 视野是完美的圆形范围（英雄 1800 / 塔 1200 / 小兵 900 / 眼 1200），
  没有树林遮挡、高低坡、夜间视野变化。
- 泉水回血 10%/秒（800 内）；被动金钱 2.0/秒、经验 0.25/秒；补刀金
  40/35/90、击杀赏金 200+25×等级；复活 6+2.5×等级（上限 60 秒）；
  均为近似值。
- 双方阵容固定为上面两套；换阵容用 `--radiant` / `--dire`（英雄名，
  逗号分隔，不带 `npc_dota_hero_` 前缀）。
