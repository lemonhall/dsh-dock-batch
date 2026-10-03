# 我一口气给 DSH 开发了十个插件

DSH（DeepSeek Harness）是个 Electron 桌面应用，界面左边是对话，右边是**右侧栏**。

右侧栏本来是放官方那三个 tab 的：文件、终端、浏览器。我把它的源码读了一遍才发现 ——
**官方的文件和第三方插件走的是完全同一套机制**。

那一瞬间我意识到：右侧栏不是「一个侧边栏」，它是这个应用的 **apps 入口**。

于是我从「给我自己加点工具」，变成了「给我自己写一排 app」。

## 十个，是这么攒出来的

一开始只是想要个电台。后来想要看行情。再后来发现：**我想要的东西基本都是「一小块信息 + 一点点交互」** ——
而这正好是右侧栏的尺寸。

- 📻 **车载电台**（`dsh-radio-dock`）—— 右侧栏里的一个 3D 车载电台：车模、弯道、月亮星空、车流超车。
- 📈 **金融终端**（`dsh-finance-dock`）—— 13 类 48 个标的 + three.js 地球，点列表里的标的，地球自动转过去。
- 📰 **RSS 阅读器**（`dsh-rss-dock`）—— 8 个源、未读与收藏双向状态，Agent 也能读。
- 📅 **通用日历**（`dsh-calendar-dock`）—— 月视图 + 当天事件 + 接下来，日期用本地字符串跨进程。
- 💰 **记账本**（`dsh-ledger-dock`）—— 金额按分存整数，本月结余 + 分类统计。
- 🔥 **卡路里日记**（`dsh-calorie-dock`）—— 内置食物热量表，选食物加克数自动算 kcal。
- ✅ **待办**（`dsh-todo-dock`）—— 一行一件、回车就加、勾掉即完成。
- 🍅 **番茄闹钟**（`dsh-pomodoro-dock`）—— 只存 endsAt 的计时，切 tab 不中断。
- 💬 **IRC 客户端**（`dsh-irc-dock`）—— 自己写的薄协议层，SASL 加自签证书加限次重连。
- 📧 **QQ 邮箱**（`dsh-qqmail-dock`）—— 读最近邮件、看正文、发纯文本，发送要 confirm。

## 全在这儿

| 插件 | 包名 | 地址 |
| --- | --- | --- |
| 📻 **车载电台** | `dsh-radio-dock` | [GitHub](https://github.com/lemonhall/dsh-radio-dock) · [npm](https://www.npmjs.com/package/dsh-radio-dock) |
| 📈 **金融终端** | `dsh-finance-dock` | [GitHub](https://github.com/lemonhall/dsh-finance-dock) · [npm](https://www.npmjs.com/package/dsh-finance-dock) |
| 📰 **RSS 阅读器** | `dsh-rss-dock` | [GitHub](https://github.com/lemonhall/dsh-rss-dock) · [npm](https://www.npmjs.com/package/dsh-rss-dock) |
| 📅 **通用日历** | `dsh-calendar-dock` | [GitHub](https://github.com/lemonhall/dsh-calendar-dock) · [npm](https://www.npmjs.com/package/dsh-calendar-dock) |
| 💰 **记账本** | `dsh-ledger-dock` | [GitHub](https://github.com/lemonhall/dsh-ledger-dock) · [npm](https://www.npmjs.com/package/dsh-ledger-dock) |
| 🔥 **卡路里日记** | `dsh-calorie-dock` | [GitHub](https://github.com/lemonhall/dsh-calorie-dock) · [npm](https://www.npmjs.com/package/dsh-calorie-dock) |
| ✅ **待办** | `dsh-todo-dock` | [GitHub](https://github.com/lemonhall/dsh-todo-dock) · [npm](https://www.npmjs.com/package/dsh-todo-dock) |
| 🍅 **番茄闹钟** | `dsh-pomodoro-dock` | [GitHub](https://github.com/lemonhall/dsh-pomodoro-dock) · [npm](https://www.npmjs.com/package/dsh-pomodoro-dock) |
| 💬 **IRC 客户端** | `dsh-irc-dock` | [GitHub](https://github.com/lemonhall/dsh-irc-dock) · [npm](https://www.npmjs.com/package/dsh-irc-dock) |
| 📧 **QQ 邮箱** | `dsh-qqmail-dock` | [GitHub](https://github.com/lemonhall/dsh-qqmail-dock) · [npm](https://www.npmjs.com/package/dsh-qqmail-dock) |

十个都是 MIT、都能从 npm 装、都只截右侧栏的面板图（我这台机器桌面左下角有真名，从不整屏）。

## 写这批插件，我反复踩的四个坑

**一、客户端插件被拼成同一个脚本，顶层 `const` 会撞名。**
DSH 把所有客户端插件拼成 `/plugins/??a/client.js,b/client.js,…` 一个文件。我加第二个插件时直接
`SyntaxError: Identifier 'TAB_KIND' has already been declared`，而且它把整个应用挡在启动之外。
从那以后每个客户端模块都包在 `;(() => { … })()` 里，并且提交前有脚本把全部 client.js
按顺序拼起来跑 `node --check`。

**二、新增的宿主路由不会热重载，必须重启。**
工具注册是当场生效的（很爽），但新加的 `webServer` 路由一直是 404，重启才通。客户端半边更彻底：
**改了必须重启**，Ctrl+F5 不够。

**三、宿主半要热重载，插件目录必须在 profile 的 `hmr.root` 名单里。**
这个我踩了两次 —— 改完 QQ 邮箱的宿主代码，报错一模一样，我以为是没改对，其实是**压根没热重载**。

**四、`npm publish` 用目录形式会永卡。**
debug 日志停在加载配置、一个 HTTP 都不发、CPU 近零；而 `npm ping`、`npm whoami`、`npm pack` 全秒回。
解法是**先 `npm pack` 出 tgz，再 `npm publish <tgz> --registry=https://registry.npmjs.org`**。

## 十个插件，一个共同的设计

它们都不是只读看板，而是**双向的**：

```
宿主半（lib/index.js）    ← 真相在这儿：状态 + 路由 + Agent 工具
    ↑ 2 秒轮询
客户端半（lib/client.js） ← 右侧栏那个 tab
```

所以你在面板里点一下，Agent 能读到；Agent 写一次，面板自己会变。

这也是我觉得右侧栏真正有意思的地方 —— 它不只是一个 UI 区域，
而是**人和 Agent 共用的一块操作台**。
