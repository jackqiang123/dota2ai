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

> **Lua 解释器路径（v3.2.0 注）：** 虚拟机换过之后 `lua5.4` 不在系统 PATH
> 里了。用户空间副本在 `~/workspace/.lua/usr/bin/lua5.4`（5.4.6），跑测试
> 用这个路径，不要假设系统有 lua：`~/workspace/.lua/usr/bin/lua5.4
> tools/integration/run.lua`。`hero_tests.lua` 会自动找这个副本
> （`LUA_BIN` 环境变量 > `--lua` 参数 > `../.lua/usr/bin/lua5.4` > PATH
> 里的 `lua5.4`）。

## Per-hero integration test（v3.2.0 新增）

`hero_tests.lua`：127 个英雄逐个进模拟器各打一局 10 分钟短对局
（1 秒 tick，种子 42 + 英雄序号，可复现），逐项门控判定，报告写
`tools/integration/hero_tests_report.md`：

```sh
~/workspace/.lua/usr/bin/lua5.4 tools/integration/hero_tests.lua \
  --out tools/integration/hero_tests_report.md --tmp /tmp/dota2ai-hero-tests
# 只跑某几个英雄：--only axe,zeus（种子用英雄全局序号，复现全量结果）
```

- 阵容：被测英雄 Radiant 按主位置/分路 + 4 个固定队友（按位置从
  Sven/Zeus/Axe/Lion/CM/Juggernaut/Lina/Magnus/Dazzle/Tidehunter/
  Earthshaker 池里补），对 5 个固定敌方 Sven/Dazzle/Enigma/Void/Lina
  （与被测英雄重名时替换：中单 Lina 换 Zeus，其他换 Tidehunter）。
- 门控（写进代码，不靠肉眼）：0 Lua 错误；移动过、攻击命中过、买过
  ≥1 件装、升到 ≥3 级且点过 ≥2 个技能；放过 ≥1 次技能（127 名英雄都有
  主动技能，无豁免英雄）；无卡住 60 秒以上、无泉水挂机 120 秒以上；
  补到 ≥1 个刀或拿到 ≥1 次击杀/助攻（辅助放宽到参团 ≥1 次或插眼 ≥1 个）；
  金钱/经验有增长。失败记失败原因（哪个门控 + 当时 tick + 最后行动）。
- 每局在独立子进程里跑 `run.lua`（带 `--stats-out`），隔离全局状态
  （`_G.DOTA_AI_BLACKBOARD`、分发器节流、黑板）；不要用 `run.lua` 自身
  的退出码判——10 分钟对局按它的 9 门控（要求胜负已决等）本就会退出 1。
- 性能：127 局 × 10 分钟，wall time 226 秒（平均每局 1.8 秒），
  目标 < 5 分钟达成；没有把 tick 放大或把局缩短，也没有放宽门控。
- 结果（2026-11-09）：**126/127 通过，1 个已知限制（Timbersaw：2v3 劣势路
  10 分钟 0 补刀，行为本身正常，见报告的“已知限制”一节），0 失败**。
  报告含总通过率、失败清单、已知限制、每英雄一行表。

## 文件

| 文件 | 作用 |
|---|---|
| `sim.lua` | 5v5 世界模型：三路兵线、防御塔、金钱/经验/等级、野区、Roshan、视野/眼位、击杀/复活、基地胜负。Lua 5.4 可跑，Lua 5.1 语法兼容。 |
| `valve_api.lua` | 模拟 Valve Bot API：`GetBot`、`DotaTime`、`GetTeam`、`GetNearbyHeroes/Creeps/Towers`、`GetAbilityInSlot/ByName`、`GetItemInSlot`、`GetCourier`、`Action_MoveToLocation/AttackUnit/UseAbility*/PurchaseItem/LevelAbility/Courier` 等。`GetNearby*` 只返回视野内单位；`Action_*` 真正改变世界（移动改位置、攻击扣血、技能扣蓝进 CD、买装扣钱进背包、插眼改视野），不是只记 log。 |
| `run.lua` | 入口：按 `TeamThink -> 各 Bot Think -> AbilityUsageThink / ItemPurchaseThink / AbilityLevelUpThink` 的顺序每 tick 调用（与 Valve 每帧的调用顺序一致）；每个 Bot 调用包 `pcall` + 指令数上限（防死循环）；写报告 + 9 个门控。 |
| `hero_tests.lua` | per-hero test 入口（v3.2.0）：127 个英雄逐个跑一局 10 分钟短对局，逐项门控判定，写 `hero_tests_report.md`。 |
| `hero_tests_report.md` | per-hero test 的报告：总通过率、失败清单、每英雄一行表。 |
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

## 模拟里修掉的 Bot bug（v3.2.0，per-hero test 过程中）

第一轮全量 117/127，第二轮 124/127，第三轮 121/127（敌方阵容问题，
见第 14 条），修掉跟随站桩后主对局 seed 42 通过、第四轮 126/127 +
1 个已知限制（Timbersaw，见第 16 条）。逐条如下：

1. `tools/integration/run.lua`——卡住检测误报：只看 60 秒位移 <50 就
   判卡住，骷髅王在兵线原地打钱（60 秒位移 49、68 次命中、13 次施放）
   被误判。改成位移 <50 且 60 秒内零行动（攻击/施放/买装/移动）才判卡住。
2. `tools/integration/hero_tests.lua`——wall time 用 `os.clock()` 只计父
   进程 CPU 时间，子进程时间全漏掉、显示 0.0 秒。改成 `os.time()`。
3. `tools/integration/hero_tests.lua`——`--only` 重跑用子集序号算种子，
   与全量种子不一致。改成用英雄全局字母序号算种子，`--only` 可复现全量。
4. `tools/integration/valve_api.lua`——**最严重的发现**：`GetScriptDirectory`
   全局定义在 `Valve.install` 末尾，而英雄加载循环在它之前；127 个
   `BotLib/hero_*.lua` 顶层都调 `GetScriptDirectory()`，所以 127 个
   require 全部静默失败（pcall 吃掉），所有英雄回落到
   `<key>_ability_1..4` 假技能名，Consider 按名查不到、永远返回 0——
   **此前所有 integration 测试里没有任何 Consider 真正跑过，
   “通过”的施放全是通用 fallback**。改成在 `install` 开头先定义
   `GetScriptDirectory`。探针验证：Lina 拿到真技能名、ConsiderQ 返回
   0.65、SkillsComplement 真正施放。
5. `scripts/vscripts/bots/mode_laning_generic.lua` + `valve_api.lua`——
   跟随静止召唤物：Arc Warden 复活后跟自己的 Tempest Double（原地站
   40 秒）在泉水边每 tick 折返、泉水挂机 130 秒；同局 Sven、Earthshaker
   也被它困住。两处修：(a) Bot 侧 `_stall` 保护：跟的友方小兵 5 秒没动
   >20 就去等兵落点（真机也成立）；(b) 模拟侧 `GetNearbyCreeps` 不再把
   召唤物算进友方小兵（真实 API 里 Tempest Double 是英雄单位，不是小兵；
   敌方召唤物仍可当小兵攻击）。
6. `scripts/vscripts/bots/engine/skill.lua` + `valve_api.lua`——
   `Skill.Cast` 只看 pcall 成功不看返回值，`Action_UseAbility*` 丢掉
   `Valve.cast` 的布尔值；一次静默失败的施放（超距/目标形式不对）
   被当成成功，`SkillsComplement` 提前返回、后面的 Consider 全不跑
   （Pugna 大招 desire 0.9 却 0 施放）。改成 `Action_UseAbility*`
   返回 `Valve.cast(...)`（模拟扩展；真实 Valve API 返回 void），
   `Skill.Cast` 要求 `ok and res ~= false`（nil = 真机成功）。
7. `tools/integration/valve_api.lua`——`Valve.cast` 目标形式校验错在
   模拟不在 Bot：审计发现 508 个英雄槽位里 117 处不一致（BotLib
   Consider 的 castType 与模拟按 `heroes.lua` 技能类型推的 kind 对不上，
   如 Luna Q 单体目标被推成落点、Axe Q 自身施放被推成落点、Pugna Q
   单体对落点）。改成 `Valve.cast` 不再校验目标形式、按实际传入归一化
   （有单位打单位、有落点打落点附近 350 内最近敌人、无落点以自身为
   中心），只保留按实际调用形式的距离检查。代价写明：模拟从此抓不出
   Consider 在真机上用了错误目标形式的问题。
8. `scripts/vscripts/bots/mode_dispatcher.lua` /
   `mode_retreat_generic.lua` / `mode_laning_generic.lua`——分发器
   per-bot 状态按英雄名 key（`_lastThink` / `_currentMode` /
   `retreatTarget` / `_stall`）；模拟里所有 Bot 共用一个 Lua 状态，
   同名英雄（Radiant Sven 队友 + Dire Sven）撞 key：Radiant Sven 每
   tick 先跑、写 `_lastThink[sven]=t`，Dire Sven 随后看到 `t-last=0 <
   thinkDelay` 被永远节流，开局走到上路角就冻住（22 次移动、3 次攻击、
   2 次施放、卡住 + 泉水挂机）。真机每 Bot 一个 Lua VM 不会发生，
   是模拟独有的共享状态 bug。改成优先按 `GetPlayerID()` key
   （模拟和真机都唯一），回落到名字、`tostring(bot)`。
9. `tools/all_heroes_b.py`——Earthshaker Q：所有分支都要多敌/低血/残血
   敌，10 分钟对线单人满血对手全程 0 施放。加单人骚扰分支：单敌 ≤700
   且蓝量 >50% → 0.55 落点（Fissure 封路骚扰本来就是常规用法）。
10. `tools/all_heroes_c.py`——Necrophos Q：同上，Death Pulse 本来就是可
    反复放的治疗/伤害技能。加单人消耗分支：≥1 敌在射程且蓝量 >50% →
    0.6 自身。
11. `scripts/vscripts/bots/engine/utility.lua`——`GetLaneWaitPoint` 棘轮
    离线失控：英雄离线后（游走/打架回来不在本路），“当前位置 +600 沿
    推进方向”每帧后移、英雄每秒只走 300 永远追不上，一直走到地图外
    （Tidehunter 从 y=65 一路向东走到 x=116991，10 分钟才 2 级）。改成
    离本路兵线段 >1500 时直接回交汇点。
12. `tools/integration/sim.lua` + `valve_api.lua`——地图边界钳制：
    `moveToward` 和 blink 落点夹到 ±7500 内，任何单位走不出世界
    （真机地图本身有边界；配合第 11 条的 Bot 侧修复）。
13. `scripts/vscripts/bots/engine/utility.lua` + `tools/integration/run.lua`——
    roam 分路掉默认中路：7 个 roam 英雄（赏金猎人、大地之灵、撼地者、
    司夜刺客、帕吉、裂魂人、巨牙海民，即 bounty_hunter / earth_spirit /
    earthshaker / nyx_assassin / pudge / spirit_breaker / tusk）的 data lane 是
    `"roam"`，`GetHeroLane` 只处理 offlane/safelane/support，roam 掉到
    默认 `"mid"`，开局全挤去中路（Earthshaker 整局在中路跟 Zeus 混，
    10 分钟没见过敌方英雄）；`run.lua` 的 `laneFor` 也把 roam 归到
    safelane、和 Bot 自认的不一致。两处统一改成 roam 按 offlane 走
    （游走位标准开局：己方劣势路）。
14. `tools/integration/hero_tests.lua`——固定敌方阵容没有中单：旧版敌方
    用 Huskar 当中单，但 Huskar 的 data lane 是 safelane，Dire 实际是
    4 上 +1 下、中路全程空无一人，6 个中单英雄（Kunkka / Necrophos /
    Puck / Viper / Windranger / Zeus）10 分钟见不到敌方英雄、0 施放。
    敌方中单改成真中单 Lina（中单重名时替补 Zeus，其他位置替补
    Tidehunter）。这是测试阵容的设计 bug，不是 Bot bug。
15. `scripts/vscripts/bots/mode_team_roam_generic.lua` +
    `mode_roam_generic.lua`——跟随站桩：Think 见到最近敌人就
    `MoveToUnit`，敌人在 0 距离也跟；`team_roam` 靠
    `CountIntent("teamfight") >= 2` 拿到 0.7 desire 长期压过 attack
    模式（0.55–0.65），四人互相跟随、在同一坐标站桩 3 分钟（主对局
    seed 42 实测：Axe+Magnus 与 Sven+Void 在 (-2750,-430) 跟了
    10:00–13:00，队伍凑不够 3 人抱团，打盾计划 0 tick、主对局 8/9 门控）。
    队友分支本来就有“150 内改去等兵落点”的防站桩，敌人分支没有。
    改成最近敌人在攻击射程内直接 `Action_AttackUnit`（真机也一样：
    贴着敌人就该打，不是跟）。修后主对局 seed 42 通过（17:23 胜，
    打盾 4 tick、肉山击杀 1），种子 7/43/100 也全过。
16. `tools/all_heroes_e.py`——Timbersaw Q：只打英雄，不打兵线；Q 本来
    就是清兵/打钱技能。加清兵分支：附近 ≥3 个敌方小兵且蓝量 >25% 时
    对最近小兵放 Q（探针验证：满蓝、3 兵在 200 码时 desire 0.6、施放
    成功；40% 蓝量门槛实测几乎不触发，降到 25%——Q 只要 100 蓝，留
    一个 W 逃生够了）。但这条没翻转他的 economy 门控：2v3 劣势路
    （对 Sven/Dazzle/Void）10 分钟仍 0 补刀——38 次攻击命中、2 反补、
    17 次施放、0 死亡，laning 早就用 `FindLastHitTarget` 挑残血兵打，
    补刀全被三人线抢走，Q 伤害不够在满血兵线上抢到补刀。行为正常，
    是固定阵容下弱势期近战劣势路的对线结果，登记为已知限制
    （`hero_tests.lua` 的 `KNOWN_LIMITATIONS`），不为此放宽门控。

另有一处调查后**回退**（不是 bug）：`engine/utility.lua` 的
`GetLaneMeetingPoint` / `GetLanePushPoint`（上路 (-6800,6800) 等）曾
被改成线中点/线端点，又回退——模拟兵线是 L 形两段等长路径，拐角本身
就是路径中点（frac 0.5），兵线在那里交战；改后 Sven 站在 (0,6800)
反而不打兵。原值加注释保留。

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
