# 给这批右侧栏插件建 GitHub 仓库并推送（用 gh.ps1，凭据只走进程内存）。
#
#   pwsh -NoProfile -File E:\development\dsh-dock-batch\make-repos.ps1
#
# 踩过的坑：**本地 git init 不会自动有 origin** —— 我曾把'没有远端'误判成 TLS 抖动、
# 白重试了四次。所以这里建完仓库就立刻 `git remote -v` 回读确认。

$ErrorActionPreference = 'Continue'
$gh = 'E:\development\tools\gh.ps1'

$repos = [ordered]@{
    'dsh-rss-dock'      = 'DSH 右侧栏 RSS 阅读器：订阅源在配置里，未读/收藏双向状态，Agent 也能读（rss_panel 工具）。'
    'dsh-calendar-dock' = 'DSH 右侧栏通用日历：月视图 + 当天事件 + 接下来；本地存储，Agent 也能加删勾（calendar_panel）。'
    'dsh-ledger-dock'   = 'DSH 右侧栏记账本：记一笔、本月结余、分类统计；金额按分存整数（ledger_panel）。'
    'dsh-calorie-dock'  = 'DSH 右侧栏卡路里日记：内置食物热量表，选食物+克数自动算 kcal（calorie_panel）。'
    'dsh-todo-dock'     = 'DSH 右侧栏轻量待办：一行一件、回车就加、勾掉即完成（todo_panel）。'
    'dsh-pomodoro-dock' = 'DSH 右侧栏番茄闹钟：专注/休息循环，计时只存 endsAt、切 tab 不中断（pomodoro_panel）。'
    'dsh-irc-dock'      = 'DSH 右侧栏 IRC 客户端：node tls 直连或走 HTTP CONNECT 隧道，SASL、自签证书、限次重连（irc_panel）。'
    'dsh-qqmail-dock'   = 'DSH 右侧栏 QQ 邮箱：读最近邮件、看正文、发纯文本；凭据只读私有文件，发送要 confirm（qqmail_panel）。'
}

foreach ($name in $repos.Keys) {
    $dir = "E:\development\$name"
    Write-Host "===== $name ====="
    Push-Location $dir
    try {
        if (-not (Test-Path .git)) { git init -b main -q }
        git add -A
        git -c core.safecrlf=false commit -q -m 'docs: README（功能、装法、双向通道、已知限制）' 2>&1 | Out-Null
        $remote = (git remote -v 2>&1 | Out-String).Trim()
        if ($remote -match 'origin') {
            Write-Host '  已有 origin，直接 push'
            git push -q origin main 2>&1 | Out-Null
            Write-Host "  push exit=$LASTEXITCODE"
        } else {
            & $gh new-repo $name $repos[$name] -Dir $dir -Push 2>&1 | Select-Object -Last 3 | ForEach-Object { "  $_" }
        }
        $after = (git remote -v 2>&1 | Out-String).Trim()
        Write-Host ("  远端：{0}" -f (($after -split "`n")[0]))
    } finally {
        Pop-Location
    }
}
Write-Host '=== 完成 ==='
