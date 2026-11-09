# 真机第一局观测记录表（v3.3.0）

打完一局直接填。**先填“开局检查”和“日志”，再填胜负**——第一局的任务
首先是确认 v3.3.0 修掉的三个真机加载 blocker 在真客户端里成立，其次
才是看打得怎么样。模拟结果不要往这张表里填。

## 基本信息

| 项 | 填空 |
|---|---|
| 日期 | |
| 房间设置：Server Location | Local Host / 其他（写清楚） |
| 房间设置：Bot Script | Local Dev Script / 其他（写清楚） |
| 房间设置：难度 | Hard / 其他 |
| 房间设置：模式 | All Pick / 其他 |
| 你的位置 | Radiant 人类玩家 / 观战 / 其他 |
| 仓库版本 | v3.3.0（`git log --oneline -1`） |
| 安装方式 | install.ps1 复制 / install.ps1 -Link / 手动复制 |

## 开局检查（0:00–1:00）

| 检查项 | 结果（是/否 + 现象） |
|---|---|
| 控制台打开正常（`\`） | |
| 控制台有 Lua 报错（红色 Lua Error / Script Error） | 有 → 把全文贴到“日志发现” |
| Bot 出泉水、往线上走 | |
| Bot 买了起始装 | |
| Bot 点了 1 级技能 | |
| 选人阶段 Bot 自己选了英雄 | 选了谁： |
| `dota_bot_debug_team 2/3` 有显示 | |
| `dota_bot_debug_lanes` 分路合理（没全挤中路） | |
| `-dumpbots` 有输出 | |

## 10:00 快照

| 项 | 填空 |
|---|---|
| 人头（Radiant : Dire） | |
| 推塔（Radiant : Dire） | |
| 等级最高的 Bot / 最低的 Bot | |
| 补刀最高的 Bot / 最低的 Bot | |
| 有没有 Bot 长时间原地不动（谁、在哪、多久） | |
| 有没有英雄全程没放过技能（谁） | |

## 终局

| 项 | 填空 |
|---|---|
| 胜方 | Radiant / Dire |
| 时长 | |
| 人头（Radiant : Dire） | |
| 推塔（Radiant : Dire） | |
| Roshan 击杀次数（哪队、几点） | |
| 打盾时队伍去不去肉山 | |
| 全程没放过技能的英雄 | |
| 全程没买过装的英雄 | |
| 卡住过的 Bot（谁、在哪、多久、怎么恢复的） | |
| 泉水挂机过的 Bot（谁、多长时间） | |

## 每英雄一行（10 个 Bot，重点看 ★ 的 19 个改名英雄）

“会放技能 / 会买装 / 会点技能”三列只要有一列填“否”，就是 v3.3.0
要修的真机问题（模拟里这三列全是“是”）。

| 队伍 | 英雄 | ★改名 | 会放技能 | 会买装 | 会点技能 | 等级 | K/D/A | 补刀 | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| Radiant | | | | | | | | | |
| Radiant | | | | | | | | | |
| Radiant | | | | | | | | | |
| Radiant | | | | | | | | | |
| Radiant | | | | | | | | | |
| Dire | | | | | | | | | |
| Dire | | | | | | | | | |
| Dire | | | | | | | | | |
| Dire | | | | | | | | | |
| Dire | | | | | | | | | |

★ 19 个改名英雄（真内部名 ≠ 本项目 key，v3.3.0 之前真机全瞎）：
Anti-Mage（antimage）、Centaur Warrunner（centaur）、Clockwerk
（rattletrap）、Doom（doom_bringer）、Io（wisp）、Lifestealer
（life_stealer）、Magnus（magnataur）、Nature's Prophet（furion）、
Necrophos（necrolyte）、Outworld Destroyer（obsidian_destroyer）、
Queen of Pain（queenofpain）、Shadow Fiend（nevermore）、Timbersaw
（shredder）、Treant Protector（treant）、Underlord
（abyssal_underlord）、Vengeful Spirit（vengefulspirit）、Windranger
（windrunner）、Wraith King（skeleton_king）、Zeus（zuus）。

## 日志发现（退出 Dota 2 后读 `<dota 2 beta>\game\dota\console.log`）

| 项 | 填空 |
|---|---|
| `[dota2ai] lobby difficulty raw GetDifficulty()=` 的值 X | **X =** （钉死难度映射的唯一证据，见 known-questions.md 第 1 条） |
| 日志里 Lua Error / Script Error 全文 | （贴全文；没有就写“无”） |
| `hero_key` / `SelectHero` 相关报错 | |
| 其他值得记的日志行 | |

## 复盘问题（打完填，回来逐项修）

1. 哪个 blocker 没成立（内部名 / 难度 / 选人）？现象是什么？
2. 哪个英雄行为最离谱（不动/不放技能/不买装/乱走）？当时在干什么？
3. 哪条控制台命令没生效？
4. 下一局最想先修什么？
