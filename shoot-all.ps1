# 批量给右侧栏的每个插件 tab 截图，并**只裁右侧栏面板**（柠檬叔左下角有真名，绝不整屏）。
#
#   pwsh -File E:\development\dsh-dock-batch\shoot-all.ps1
#
# 前置：应用带 --remote-debugging-port=9222 启动（E:\development\dsh-cdp-restart.ps1）。
#
# 三个踩过的坑，都写在这儿免得重犯：
#   ① 右侧栏关着时 [data-rightbar-col] 宽度是 0、「+」也点不到 → 先确保打开
#   ② **不要用"最后一个 button"当「+」** —— tab 条里最后那个是「收起右侧边栏」，
#      点了会开开关关一张图也截不到。认 aria-label="新标签页"（_addTab_）。
#   ③ rect 必须**每次截图前现量**：开头量一次时侧栏可能刚打开、宽度还是 0，
#      裁出来是空图，Pillow 会报 cannot write empty image。

$ErrorActionPreference = 'Continue'
$probe = 'E:\development\tools\cdp-probe.mjs'
$crop = 'E:\development\dsh-dock-batch\crop-panel.py'
$py = 'C:\Users\lemon\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
$batch = 'E:\development\dsh-dock-batch'

$tabs = [ordered]@{
    'RSS 阅读器' = @{ dir = 'dsh-rss-dock';      mark = '未读' }
    '日历'       = @{ dir = 'dsh-calendar-dock'; mark = '接下来' }
    '记账本'     = @{ dir = 'dsh-ledger-dock';   mark = '结余' }
    '卡路里日记' = @{ dir = 'dsh-calorie-dock';  mark = 'kcal' }
    '待办'       = @{ dir = 'dsh-todo-dock';     mark = '未完成' }
    '番茄闹钟'   = @{ dir = 'dsh-pomodoro-dock'; mark = '专注' }
    'IRC 聊天'   = @{ dir = 'dsh-irc-dock';      mark = 'IRC' }
    'QQ 邮箱'    = @{ dir = 'dsh-qqmail-dock';   mark = '收件箱' }
}

$rectJs = '(() => { const c = document.querySelector("[data-rightbar-col]"); const r = c.getBoundingClientRect(); return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height), vw: window.innerWidth }; })()'
$openJs = '(() => { const col = document.querySelector("[data-rightbar-col]"); if (col && col.getBoundingClientRect().width > 40) return "already"; const btn = [...document.querySelectorAll("button")].find(b => ((b.getAttribute("aria-label")||"") + b.title).includes("打开右侧")); if (btn) { btn.click(); return "opened"; } return "no-button"; })()'
$plusJs = '(() => { const btn = [...document.querySelectorAll("button")].find(b => (b.getAttribute("aria-label")||"") === "新标签页"); if (!btn) return "no-add"; btn.click(); return "plus"; })()'
$panelJs = '(() => { const c = document.querySelector("[data-rightbar-col]"); return c ? (c.innerText||"").replace(/\s+/g," ") : ""; })()'

function Measure-Panel {
    (node $probe $rectJs | Out-String) | ConvertFrom-Json
}

Write-Host '=== 0) 确保右侧栏打开 ==='
Write-Host ('  ' + ((node $probe $openJs | Out-String).Trim()))
Start-Sleep -Milliseconds 1800

foreach ($title in $tabs.Keys) {
    $dir = $tabs[$title].dir
    $mark = $tabs[$title].mark
    $docDir = "E:\development\$dir\docs"
    New-Item -ItemType Directory -Force -Path $docDir | Out-Null
    $done = $false

    for ($attempt = 1; $attempt -le 3 -and -not $done; $attempt++) {
        Write-Host ('  ' + ((node $probe $plusJs | Out-String).Trim()))
        Start-Sleep -Milliseconds 1100

        $esc = $title.Replace("'", "\'")
        $clickJs = "(() => { const hit = [...document.querySelectorAll('*')].filter(el => { const t = (el.textContent||'').trim(); const r = el.getBoundingClientRect(); return t === '$esc' && r.x > 600 && r.width && r.width < 460; }).pop(); if (!hit) return 'missing'; hit.click(); return 'clicked'; })()"
        $clicked = (node $probe $clickJs | Out-String).Trim()
        Start-Sleep -Milliseconds 2600

        # ⚠️ 点完入口，「+」菜单还开着、盖在面板上 —— 不关掉就截图，拍到的是菜单不是面板。
        # 而且校验也会被骗过：菜单里也有那 8 个标题。所以先关菜单，再校验、再截。
        $null = node $probe '(() => { document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true })); const el = document.activeElement; if (el && el.blur) el.blur(); return "escaped"; })()'
        Start-Sleep -Milliseconds 900

        $panel = (node $probe $panelJs | Out-String).Trim().Trim('"')
        # 菜单若还开着，面板文本会以那串标题开头
        $menuStillOpen = $panel.StartsWith('📰 RSS 📅 日历')
        if ($clicked -notmatch 'clicked' -or $menuStillOpen -or -not $panel.Contains($mark)) {
            Write-Host ("  … {0} 第{1}次没切成（clicked={2} 菜单还开={3} 面板={4}）" -f $title, $attempt, $clicked, $menuStillOpen, $panel.Substring(0, [Math]::Min(30, $panel.Length)))
            continue
        }

        $rect = Measure-Panel
        if ($rect.w -lt 40) {
            Write-Host ("  … {0}：面板宽度 {1}，开侧栏后重试" -f $title, $rect.w)
            $null = node $probe $openJs
            Start-Sleep -Milliseconds 1500
            $rect = Measure-Panel
        }

        $shot = "$batch\shot-$dir.png"
        $null = node $probe --shot $shot
        & $py $crop $shot "$docDir\screenshot-panel.png" $rect.x $rect.y $rect.w $rect.h $rect.vw 820 | Out-Null
        $kb = if (Test-Path "$docDir\screenshot-panel.png") { [int]((Get-Item "$docDir\screenshot-panel.png").Length / 1024) } else { 0 }
        Write-Host ("  ✓ {0,-12} 第{1}次 → {2} KB (rect {3}x{4})  {5}" -f $title, $attempt, $kb, $rect.w, $rect.h, $panel.Substring(0, [Math]::Min(52, $panel.Length)))
        $done = $true
    }

    if (-not $done) { Write-Host ("  ✗ {0}：三次都没切成" -f $title) }
}

Write-Host '=== 完成 ==='
