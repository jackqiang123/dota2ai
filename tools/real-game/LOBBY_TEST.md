# 真机本地 Lobby 测试（v3.3.0）

目的：第一次在真 Dota 2 客户端里跑这套 Bot 脚本。**先确认加载成立，
再看打得怎么样**——模拟器验不了真机加载（内部英雄名、房间难度、选人
API、控制台日志都只在真客户端里存在），所以这局的首要任务是回答
`known-questions.md` 里的问题，不是赢。

> 全程只做准备 + 记录，**不在你电脑上启动任何程序**。下面所有步骤都
> 是你（或你在自己电脑上）手动执行；脚本 `install.ps1` 只拷文件，
> 不启动 Steam、不启动 Dota 2。

## 0. 前置条件

| 条件 | 说明 |
|---|---|
| Steam + Dota 2 已安装 | 需要能进游戏建房间。磁盘空间：Bot 脚本约 2–3 MB，可忽略。 |
| 控制台已开启 | Steam 库 → Dota 2 → 属性 → 启动选项，加 `-console -condebug`（来源：Nostrademous Dota2-FullOverwrite wiki“Workflow for Debugging Bots”；danlniel/dota2bot-neigh 的 bot-iq 计划文档）。不加 `-condebug` 就没有 `console.log` 文件可事后查。 |
| 控制台热键 | 默认 `\`（反斜杠）。游戏中按 `\` 打开/关闭控制台。 |
| 本仓库已同步到 v3.3.0 | `git log --oneline -1` 应为 v3.3.0 提交；`scripts/vscripts/bots/engine/hero_key.lua` 存在。 |

## 1. 安装 Bot 脚本

**关键事实（v3.3.0 审计纠正）：Bot 脚本不走 `dota_addons`。**
游戏加载 Bot 脚本的位置是 `game/dota/scripts/vscripts/bots/`，Workshop
上传的也是这个目录的内容（Valve Developer Community, Dota Bot
Scripting；OHA Discussion #68）。`addoninfo.txt` 对 Bot 脚本加载不起
作用，不要拷它；`tools/`、测试文件也不拷。

### 方式 A：脚本安装（推荐）

1. 在 Windows PowerShell 里进仓库目录，跑：
   ```powershell
   .\tools\real-game\install.ps1
   ```
   脚本只做三件事：备份现有的 `bots/` 文件夹（改名
   `bots.valve-backup-<日期时间>`）、把仓库 `scripts/vscripts/bots/`
   的内容拷进 `game/dota/scripts/vscripts/bots/`、打印拷了多少文件。
   不启动 Steam、不启动 Dota 2。
2. Steam 库位置不是默认 `C:\Program Files (x86)\Steam` 时，改脚本顶部
   的 `$SteamPath` 变量，或传参：
   ```powershell
   .\tools\real-game\install.ps1 -SteamPath "D:\Steam"
   ```
3. 想用符号链接（改仓库即改游戏内文件，不用每次重拷，OHA 的 `mklink /d`
   做法）：
   ```powershell
   .\tools\real-game\install.ps1 -Link
   ```
   需要管理员权限或开发者模式。

**预期看到：** 脚本打印 `备份：... -> bots.valve-backup-...` 和
`已复制 N 个文件到 ...\game\dota\scripts\vscripts\bots`，无报错。
**如果不是：** 检查 `$SteamPath` 对不对、Dota 2 装在哪个库（Steam →
设置 → 存储里看）；`-Link` 报错先看是不是权限问题，换普通复制方式。

### 方式 B：手动安装

1. 找到 Dota 2 安装目录，例如
   `C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\`。
2. 把现有的 `game\dota\scripts\vscripts\bots\` 文件夹改名备份，
   例如 `bots.valve-backup-2026-11-09`（**不要直接覆盖 Valve 默认
   Bot 文件**，卸载/还原时要用）。
3. 把仓库 `scripts/vscripts/bots/` 里的**全部内容**（不是 `bots`
   文件夹本身）复制到 `game\dota\scripts\vscripts\bots/`。
   只拷这个目录的内容：不要拷仓库根目录的 `addoninfo.txt`、
   `README.md`，不要拷 `tools/`。

**预期看到：** 目标目录里有 `bot_generic.lua`、
`ability_item_usage_generic.lua`、`item_purchase_generic.lua`、
`hero_selection.lua`、`team_think.lua`、`mode_dispatcher.lua`、
`engine/hero_key.lua`、`BotLib/hero_axe.lua` 等。
**如果不是：** 很可能拷错了层级（多了一层 `bots/bots/` 或少了一层），
对照上面列的文件名检查。

## 2. 开控制台，确认日志在写

1. 启动 Dota 2（启动选项里已有 `-console -condebug`）。
2. 游戏中按 `\` 打开控制台，确认能打开、能输入。
3. 先不要急着开房间：退出一次 Dota 2，检查
   `<dota 2 beta>\game\dota\console.log` 是否存在且有新内容。
   （来源同上。注意：**`console.log` 是缓冲的，退出游戏后才落盘**，
   游戏进行中读它看不到最新内容——ex3lite
   Dota2_Workshop_MCP README；所以查 Lua 报错要么看游戏内控制台
   实时输出，要么等退出后再读文件。）

**预期看到：** `console.log` 存在，时间戳是你刚退出游戏的时间。
**如果不是：** 启动选项没加对（`-console -condebug` 两个都要），
或 Dota 2 装在别的库，`console.log` 在对应库的 `game\dota\` 下。

## 3. 建本地房间

1. Play → Create Lobby（自定义房间）。
2. **Server Location 选 Local Host**（来源：OHA Discussion #68——Bot
   脚本只在 Server Location 为 Local Host 的自定义房间里工作）。
3. 游戏模式：**All Pick**（本仓库只实现了 AP 式选人；CM 的
   ban/pick 未实现，见 `known-questions.md` 第 12 条）。
4. **Bot Script 选 Local Dev Script**（来源：Steam 社区讨论
   “To use your local bot script, create a custom lobby and select
   'Local dev script' as the bots”；OHA Discussion #68 同样说法）。
5. Bot 难度：先选 **Hard**（困难）。理由：与脚本内部默认难度 3
   一致，第一局先看加载对不对，难度对比以后再做。
   （Unfair 的引擎数值加成是另一回事，见 `known-questions.md` 第 1 条。）
6. **勾选 Enable Cheats**（调试命令和 `sv_cheats 1` 需要；来源：
   OHA #68、Nostrademous wiki）。
7. 填满两边：**主路径是你打 Radiant，1 个人 + 4 个 Bot 对 5 个 Bot**
   （OHA 标准的 playtest  setup，己方和敌方 Bot 都能测到）。
   备选：10 个 Bot + 你观战——如果房间允许观战位就优先用它，
   不行就回主路径（见 `known-questions.md` 第 5 条，回来确认）。

**预期看到：** 房间里 Bot Script 一栏显示 Local Dev Script，难度
Hard，Server Location 显示 Local Host。
**如果不是：**
- Bot 进游戏后名字没有变化、打法像默认 Bot → 很可能 Bot Script
  没选成 Local Dev Script，退回房间重选（OHA #68：加载正确的
  Bot 名字会有后缀，如 OHA 的 `.OHA`；本仓库没有改名逻辑，名字上
  看不出区别，**以控制台有无 Lua 报错和 checklist 的行为检查为准**，
  不要只看名字）。
- 找不到 Local Dev Script 选项 → 安装位置不对，回到第 1 步检查
  `game/dota/scripts/vscripts/bots/` 里有没有 `bot_generic.lua`。

## 4. 开局：敲命令，看加载

1. 进游戏，选人阶段：看 Bot 会不会自己选英雄。
   **预期：** Bot 在选人时间里陆续选出英雄（v3.3.0 的
   `hero_selection.lua` 会按阵容协同选；选了谁记进 checklist）。
   **如果不是：** 选人时间到后游戏会给 Bot 随机英雄——不卡死，但
   记下来（选人 API 没生效，见 `known-questions.md` 第 2 条）。
2. 按 `\` 打开控制台，逐条敲 `console-commands.txt` 里“开局必敲”的命令：
   ```
   sv_cheats 1
   dota_bot_debug_team 2
   dota_bot_debug_team 3
   dota_bot_debug_lanes
   ```
   （每条的来源写在文件里；`dota_bot_set_difficulty` 不要敲——
   刻度有争议，见 `known-questions.md` 第 7 条。）
3. 聊天框里敲 `-dumpbots`（聊天命令，不是控制台命令；来源：
   Liquipedia Cheats，显示 AI 状态）。
4. 开局 0:00–1:00 检查（填 `checklist.md`“开局检查”）：
   - 控制台有没有 Lua 报错（红色 `Lua Error` / `Script Error`）。
   - Bot 有没有出泉水、有没有往线上走。
   - 有没有买起始装（看 Bot 英雄物品栏）。
   - 有没有点技能（看技能栏亮没亮 1 级技能）。
   - **重点看 19 个改名英雄**（Zeus、Wraith King、Io、Magnus、
     Timbersaw、Doom、Anti-Mage 等，完整名单见 checklist）：他们
     会不会放技能、买装、点技能。v3.3.0 之前他们在真机里是全瞎的，
     这局就是验这个。

**如果 Bot 不动：** 先看控制台有没有 Lua 报错——有就把报错全文抄进
checklist，退出游戏读 `console.log`；没有报错但 Bot 不动，检查
Bot Script 是不是 Local Dev Script（第 3 步），以及 Server Location
是不是 Local Host。

## 5. 跑满一局

1. 正常打满一局（不用刻意送人头，也不用速推；想快可以只打到一方
   基地破，但**建议打满**，中后期的打盾/推塔/买装行为只在长局里出现）。
2. 10:00 左右填一次 `checklist.md`“10:00 快照”（等级、补刀、人头、
   卡住的 Bot）。
3. 过程中注意：有没有 Bot 长时间原地不动、有没有英雄全程没放过技能、
   有没有 Bot 从不买装、打盾时队伍去不去肉山。
4. 可选：想快速看高等级行为，聊天框敲 `-levelbots 5`、控制台
   `dota_bot_debug_team 2/3` 随时看（来源见 `console-commands.txt`）。

## 6. 退出，读日志，填表

1. **先完全退出 Dota 2**，再打开
   `<dota 2 beta>\game\dota\console.log`（缓冲原因见第 2 步）。
2. 在日志里搜：
   - `[dota2ai]`——第一行就是房间难度的原始值
     `lobby difficulty raw GetDifficulty()=X`，**把 X 抄进 checklist**
    （这是钉死难度映射的唯一证据，见 `known-questions.md` 第 1 条）。
   - `Lua Error` / `error` / `Script Error`——有就把全文贴进 checklist。
   - `hero_key` / `SelectHero` 相关的报错（如果有）。
3. 填完 `checklist.md`（胜方、时长、人头、推塔、补刀、卡住的 Bot、
   没放技能的英雄、打盾情况、每英雄一行）。
4. 回来对照 `known-questions.md`，能划掉的逐项划掉、写上答案；
   划不掉的写清楚当时看到的现象。

## 7. 还原（可选）

- 不想继续测了：删掉 `game/dota/scripts/vscripts/bots/`，把备份的
  `bots.valve-backup-<日期>` 改回 `bots`，即恢复 Valve 默认 Bot。
- Steam 更新/验证完整性后如果 `bots/` 被还原，重新跑一次
  `install.ps1` 即可（见 `known-questions.md` 第 11 条）。

## 附：本包文件

| 文件 | 用途 |
|---|---|
| `LOBBY_TEST.md`（本文件） | 完整步骤 |
| `install.ps1` | Windows 拷贝安装脚本（只拷文件，不启动 Steam/Dota 2） |
| `console-commands.txt` | 开局要敲的命令，每条带来源注释 |
| `checklist.md` | 打完一局直接填的观测记录表 |
| `known-questions.md` | 第一局之前回答不了的问题清单 |
