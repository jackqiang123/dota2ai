# 待真机确认的问题（v3.3.0）

第一局之前回答不了的问题。跑完一局回来逐项划掉、写上答案；
划不掉的写清楚当时看到的现象，不要猜。

## 1. `GetDifficulty()` 返回值的映射（最重要）

- 现状：代码按 VDC 控制台命令表的口径映射（0=简单/1=中等/2=困难/
  3=疯狂，4/5 一律按疯狂处理），`Utility.GetDifficulty(bot)` 首次
  运行会把原始值 print 到控制台。
- 冲突：另有实测说 `dota_bot_practice_difficulty` 是 1=简单/2=中等/
  3=困难/4=疯狂；还有一种可能是枚举值（1=Passive/2=Easy/3=Medium/
  4=Hard/5=Unfair）。
- 第一局要确认：`console.log` 里 `[dota2ai] lobby difficulty raw
  GetDifficulty()=X` 的 X 是多少（房间选 Hard 时）。再结合 Bot 的
  实际反应速度（困难应为 0.15s thinkDelay）判断映射对不对。
- 状态：未确认。实测 X = ___，映射结论：___。

## 2. `hero_selection` 的 Think() 在 AP 房间里跑不跑

- 现状：v3.3.0 的 `Think()` 会调全局 `SelectHero(nPlayerID,
  npc_name)` 给己方未选英雄的 Bot 选人，全部 API 调用包 pcall，
  API 不可用时直接返回、游戏按时间到随机选人。
- 第一局要确认：选人阶段 Bot 有没有自己选英雄？选的是不是阵容协同
  的 pick（checklist 里记下了谁）？还是全靠时间到随机？
- 状态：未确认。实测：___。

## 3. 19 个改名英雄在真机里是不是真修好了

- 现状：`npc_name` 已按真内部名生成，`engine/hero_key.lua` 做换算，
  四处查表点全部改走它；`tools/verify_hero_key.lua` 64 项全过，
  但那是 mock + 模拟器，不是真机。
- 第一局要确认：checklist“每英雄一行”里，★ 的 19 个英雄（尤其
  Zeus、Wraith King、Io、Magnus）会不会放技能、买装、点技能。
- 状态：未确认。实测：___。

## 4. `console.log` 的路径与缓冲行为

- 现状：两处独立来源（Nostrademous wiki、danlniel/dota2bot-neigh
  文档）都说 `-console -condebug` 启动选项 → 日志在
  `<dota 2 beta>\game\dota\console.log`；ex3lite
  Dota2_Workshop_MCP README 说它是缓冲的、退出游戏后才落盘。
- 第一局要确认：文件在不在那个路径、时间戳对不对、退出前读它
  是不是确实看不到最新内容、游戏内控制台实时报错能不能看到。
- 状态：未确认。实测：___。

## 5. 10 个 Bot + 观战的房间行不行

- 现状：主路径是 1 个人 + 4 个 Bot 对 5 个 Bot（OHA 标准的
  playtest  setup）；10 Bot + 观战是备选，房间 UI 是否允许观战位
  未在真机上确认。
- 第一局要确认：能不能开 10 Bot + 观战？不行的话退回主路径。
- 状态：未确认。实测：___。

## 6. `script_reload` / `script_reload_code` 对 Bot 脚本能不能热更新

- 现状：ModDota 脚本入门说 `script_reload` 重载 vscripts，但对
  Bot 脚本是否适用未核实；`script_reload_code bots/fretbots` 是
  OHA 专属，本仓库没有 fretbots 文件。
- 第一局要确认（可选，不影响第一局本身）：改完脚本后敲
  `script_reload` 能不能生效，还是必须重新进房间。
- 状态：未确认。实测：___。

## 7. `dota_bot_set_difficulty` 的刻度

- 现状：VDC 控制台命令表说 0=简单/1=中等/2=困难/3=疯狂；另有实测
  说 `dota_bot_practice_difficulty` 是 1=简单/2=中等/3=困难/4=疯狂。
  第一局不要敲这条命令（console-commands.txt 已标明）。
- 第一局要确认：与第 1 条是同一个问题——按 `GetDifficulty()` 的
  实测原始值反推，看房间 UI 的 Hard 对应哪个数值。
- 状态：未确认。实测：___。

## 8. FretBots 那套适不适用

- 现状：不适用。FretBots 是 OHA 的功能（真实金钱/经验/属性加成，
  需手动安装 + `sv_cheats 1; script_reload_code bots/fretbots`），
  本仓库没有 fretbots 文件、也没有引擎级数值加成（Lua Bot 脚本
  没有发金钱/经验的 API，见 README“难度”一节）。
- 第一局要确认：无——这是已知不适用，列在这里是防止有人误以为
  房间难度 Unfair 会自动给 Bot 加钱加经验。
- 状态：已知不适用，无需确认。

## 9. `dota_launch_custom_game` 不是 Bot 脚本的启动命令

- 现状：已知不用。`dota_launch_custom_game <addon> <map>` 是自定义
  游戏 Addon 的命令（ModDota 脚本入门），Bot 脚本走自定义房间 +
  Local Dev Script，不走它。
- 状态：已知不用，无需确认。

## 10. Workshop 上传路径

- 现状：VDC 说 Workshop 上传的是 `game/dota/scripts/vscripts/bots/`
  目录的内容；`addoninfo.txt` 对 Bot 脚本加载不起作用。
  但 Workshop Tools 上传界面的具体步骤（选哪个上传类型、要不要填
  Addon 信息）尚未在真机上走通。
- 第一局要确认：不影响第一局（第一局用手动复制/ install.ps1）。
  以后想上 Workshop 时再走一遍上传流程、把步骤补进 LOBBY_TEST.md。
- 状态：未确认（不阻塞第一局）。

## 11. Steam 更新/验证完整性会不会覆盖 `bots/` 目录

- 现状：`game/dota/scripts/vscripts/bots/` 是游戏目录，Steam 更新
  或“验证游戏文件完整性”有可能把它还原成 Valve 默认 Bot 文件。
  install.ps1 每次都会先备份，所以丢了也能重装，但“会不会被覆盖”
  本身未确认。
- 第一局后要确认：下次 Steam 更新后检查 `bots/` 还在不在。
- 状态：未确认。实测：___。

## 12. CM / RD 等模式支不支持

- 现状：不支持。本仓库只实现了 AP 式选人（`hero_selection.lua`
  的 `Think()` 调 `SelectHero`）；CM 的 ban/pick
  （`CMBanHero`/`CMPickHero`）未实现，RD 等模式也未单独处理。
  第一局只开 All Pick。
- 状态：已知不支持，无需确认（以后想支持再做）。
