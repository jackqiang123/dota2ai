# install.ps1 -- 把本仓库的 Bot 脚本装进 Dota 2（Windows PowerShell）。
#
# 只拷文件，不启动 Steam、不启动 Dota 2。
#
# 关键事实（v3.3.0 审计纠正）：Bot 脚本不走 dota_addons。游戏加载 Bot 脚本
# 的位置是 game/dota/scripts/vscripts/bots/，Workshop 上传的也是这个目录的
# 内容（Valve Developer Community, Dota Bot Scripting；OHA Discussion #68）。
# 所以这里只拷 scripts/vscripts/bots/ 的内容，不拷 addoninfo.txt、README、
# tools/、测试文件。
#
# 用法（在仓库根目录）：
#   .\tools\real-game\install.ps1
#   .\tools\real-game\install.ps1 -SteamPath "D:\Steam"
#   .\tools\real-game\install.ps1 -Link        # 符号链接安装（需管理员权限或开发者模式）
#
# 行为：
#   1. 先备份现有的 bots/ 文件夹 -> bots.valve-backup-<yyyy-MM-dd-HHmmss>
#      （直接覆盖会丢 Valve 默认 Bot 文件，卸载/还原时要用备份。）
#   2. 默认复制；-Link 时改建符号链接（改仓库即改游戏内文件，不用每次重拷，
#      与 OHA 文档的 mklink /d 做法相同）。
#   3. 打印拷了多少文件 / 链接指到哪。

param(
    # Steam 安装根目录（默认 C 盘标准位置；改库位置时改这里，或传参覆盖）。
    [string]$SteamPath = "C:\Program Files (x86)\Steam",

    # 符号链接安装（-Link），代替复制。需要管理员权限或开发者模式。
    [switch]$Link
)

$ErrorActionPreference = "Stop"

# 仓库根目录：脚本在 tools/real-game/ 下，往上两级就是仓库根。
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$SourceBots = Join-Path $RepoRoot "scripts\vscripts\bots"
$DotaRoot = Join-Path $SteamPath "steamapps\common\dota 2 beta"
$TargetBots = Join-Path $DotaRoot "game\dota\scripts\vscripts\bots"

if (-not (Test-Path $SourceBots)) {
    Write-Error "找不到仓库 Bot 目录：$SourceBots（请确认在 dota2ai 仓库里跑本脚本）"
    exit 1
}
if (-not (Test-Path (Join-Path $SourceBots "bot_generic.lua"))) {
    Write-Error "仓库 Bot 目录里没有 bot_generic.lua：$SourceBots（仓库不完整？）"
    exit 1
}
if (-not (Test-Path $DotaRoot)) {
    Write-Error "找不到 Dota 2 安装目录：$DotaRoot（SteamPath 不对？改脚本顶部 `$SteamPath 或传 -SteamPath 参数）"
    exit 1
}

# 1. 备份现有 bots/（文件、文件夹、符号链接都算“存在”）。
if (Test-Path $TargetBots) {
    $stamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
    $Backup = "$TargetBots.valve-backup-$stamp"
    Write-Host "备份现有 bots/ -> $Backup"
    Rename-Item -LiteralPath $TargetBots -NewName (Split-Path $Backup -Leaf)
}

# 2. 安装：复制 或 符号链接。
if ($Link) {
    Write-Host "符号链接安装：$TargetBots -> $SourceBots"
    New-Item -ItemType SymbolicLink -Path $TargetBots -Target $SourceBots | Out-Null
    Write-Host "完成：$TargetBots 已链接到仓库（改仓库即改游戏内文件）。"
} else {
    Write-Host "复制：$SourceBots -> $TargetBots"
    New-Item -ItemType Directory -Path $TargetBots -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $SourceBots "*") -Destination $TargetBots -Recurse -Force
    $count = (Get-ChildItem -LiteralPath $TargetBots -Recurse -File).Count
    Write-Host "完成：已复制 $count 个文件到 $TargetBots"
}

Write-Host "下一步：按 tools/real-game/LOBBY_TEST.md 第 2 步开控制台、第 3 步建本地房间。"
Write-Host "还原：删掉 $TargetBots，把备份的 bots.valve-backup-<日期> 改回 bots 即可。"
