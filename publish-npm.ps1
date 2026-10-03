# 把这批插件发布到 npm。
#
#   pwsh -NoProfile -File E:\development\dsh-dock-batch\publish-npm.ps1
#
# 两个必须遵守的点（都踩过）：
#   ① **先 npm pack 再 npm publish <tgz>** —— 直接用目录发布会**永卡**在本地 prep 阶段
#      （debug 日志停在加载配置、CPU 近零、一个 HTTP 都不发；--dry-run 也一样）。
#   ② `~/.npmrc` 的 registry 是 npmmirror（只读镜像）→ 发布必须显式 --registry 到官方源。

$ErrorActionPreference = 'Continue'
$registry = 'https://registry.npmjs.org'

$dirs = @(
    'dsh-rss-dock', 'dsh-calendar-dock', 'dsh-ledger-dock', 'dsh-calorie-dock',
    'dsh-todo-dock', 'dsh-pomodoro-dock', 'dsh-irc-dock', 'dsh-qqmail-dock'
)

foreach ($dir in $dirs) {
    $path = "E:\development\$dir"
    Write-Host "===== $dir ====="
    Push-Location $path
    try {
        Remove-Item .\*.tgz -ErrorAction SilentlyContinue
        $packOut = npm pack 2>&1 | Select-Object -Last 1
        $tgz = Get-ChildItem .\*.tgz -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $tgz) {
            Write-Host "  ✗ 打包失败：$packOut"
            continue
        }
        Write-Host ("  打包 {0}（{1} KB）" -f $tgz.Name, [int]($tgz.Length / 1024))
        $out = npm publish $tgz.FullName --registry=$registry 2>&1 | Select-Object -Last 3
        foreach ($line in $out) { Write-Host "  $line" }
        Write-Host ("  publish exit={0}" -f $LASTEXITCODE)
        Remove-Item $tgz.FullName -ErrorAction SilentlyContinue
    } finally {
        Pop-Location
    }
}

Write-Host '=== 回读 profile 的 bundles（装插件会把列表重置成只剩 base，踩过两次）==='
$b = (Get-Content 'C:\Users\lemon\.dsh\profiles\desktop\package.json' -Raw | ConvertFrom-Json).dsh.profile.bundles
Write-Host ("  bundles 数量：{0}" -f ($b | Measure-Object).Count)
Write-Host '=== 完成 ==='
