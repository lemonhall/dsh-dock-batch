# 右侧栏插件批次计划（2026-10-03）

柠檬叔点名要的 6 个，参照 `E:\development\kotlinagentapp` 里已有的同类能力（PRD-0018 日历 / PRD-0019 QQ邮箱 / PRD-0020 账本 / PRD-0024 RSS / PRD-0028 IRC）。

## 硬规则（每次都要遵守）

1. **截图只截右侧栏面板特写，绝不整屏** —— 柠檬叔桌面左下角有真名（余柠）。裁图必须先向浏览器要 `[data-rightbar-col]` 的真实 rect 再裁，别写死尺寸（dpr 会变，踩过）。
2. 每个插件三件套齐全：**GitHub 仓库（public）+ npm 包 + 公众号文章**。
3. **客户端插件必须整体包 IIFE**（顶层 const 会跨插件撞名，直接把 web boot 打挂，踩过）。
4. 新增宿主路由**要重启才生效**；工具注册当场生效。重启用计划任务脚本（会断我这一轮，所以**攒够再重启**）。
5. 装插件用 `plugin_manager install_bundle`，**装完必须回读 `profiles/desktop/package.json` 的 `bundles`**（它有时会把列表重置成只剩 base，踩过）。
6. 发布 npm：先 `npm pack` 再 `npm publish <tgz> --registry=https://registry.npmjs.org`（目录形式会永卡，踩过）。
7. 建仓库：**先 `github new-repo`（本地 git init 不会自动有 origin，我为此误判过两次 TLS 抖动）**。

## 共用骨架（从 dsh-finance-dock 抄，别重写）

```
package.json        dsh.bundle.patch + dsh.client{platform:'web'} + files 含运行时要的资源
cordis.patch.yml    insert 一行，config 放业务参数
lib/index.js        宿主半：ctx.inject(['webServer']) 注册路由 + ctx.inject(['tools']) 注册工具
lib/client.js       客户端半：IIFE + sidebarRightTabs.register + 两个 keyed slot
lib/state.js        本地 JSON 状态（原子写：临时文件 + rename）
```

**双向通道**（柠檬叔最看重的那点）沿用 finance-dock 的做法：状态放宿主 → 客户端 2s 轮询 → 工具读写同一份状态。
每个插件都该有自己的工具，名字前缀统一 `dsh_<域>_` 或直接 `<域>_panel` 风格。

## 六个插件

| # | 插件 | 数据放哪 | 外部依赖 | 备注 |
| --- | --- | --- | --- | --- |
| 1 | `dsh-rss-dock` | feeds 列表在宿主 config；已读/收藏在 state | 无（宿主用 curl 抓 RSS，走代理） | 最简单，先做。要能加 feed、按时间排、标记已读 |
| 2 | `dsh-calendar-dock` | 事件存插件目录 JSON | 无 | 通用日历：月视图 + 今天/本周列表 + 新建/删除。**不做**系统日历同步 |
| 3 | `dsh-ledger-dock` | 账本 JSON | 无 | 记账：记一笔（金额/分类/备注/日期）、本月汇总、按分类统计 |
| 4 | `dsh-calorie-dock` | 日记 JSON | 无 | 卡路里：记一餐（食物/份量/热量）、当日合计、目标线；内置常见食物热量表 |
| 5 | `dsh-irc-dock` | 服务器/频道在 config；消息只在内存 + 可选落盘 | IRC 服务器（默认 Libera.Chat） | 宿主用 node `tls` 连 IRC，客户端收发。**要能重连** |
| 6 | `dsh-qqmail-dock` | 凭据走插件私有配置（**绝不进 git**） | QQ 邮箱 IMAP（需要授权码） | ⚠️ 需要柠檬叔提供 QQ 邮箱**授权码**（不是登录密码）；用 imapflow 之类的库，先确认能否装依赖 |

## 顺序

1 → 2 → 3 → 4 → 5 → 6（由简到难；6 卡在授权码上，最后做，做之前先问柠檬叔要）。
每个做完：装 → 重启（攒批）→ 只截面板 → README → 建仓库/推 → npm → 文章。
