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

## 先说 DSH 是什么

DSH（DeepSeek Harness）是 DeepSeek 的 agent 运行环境：左边是对话，右边是**右侧栏** ——
官方在那儿放了文件、终端、浏览器三个 tab。

关键在于：**它把第三方插件和官方那几个 tab 一视同仁，走的是同一套机制**。
所以给右侧栏加一个 app，就是装一个插件。

## 在 DSH 里怎么装这些插件（这条最重要）

桌面版最省事：**右侧栏 →「插件」→「添加插件」→ 把包名填进去**，比如 `dsh-rss-dock`。

或者用 CLI（`--profile` 换成你自己的 profile 名，桌面版默认叫 `desktop`）：

```
dsh plugin --profile desktop add dsh-rss-dock
```

十个一起装（一行一个，复制粘贴就行）：

```
dsh plugin --profile desktop add dsh-radio-dock
dsh plugin --profile desktop add dsh-finance-dock
dsh plugin --profile desktop add dsh-rss-dock
dsh plugin --profile desktop add dsh-calendar-dock
dsh plugin --profile desktop add dsh-ledger-dock
dsh plugin --profile desktop add dsh-calorie-dock
dsh plugin --profile desktop add dsh-todo-dock
dsh plugin --profile desktop add dsh-pomodoro-dock
dsh plugin --profile desktop add dsh-irc-dock
dsh plugin --profile desktop add dsh-qqmail-dock
```

装完**重启一次应用**（这类插件的界面半边在启动时就固化了，Ctrl+F5 不管用），
然后**右侧栏点「+」**才能看到它们 —— 右侧栏的 tab 不会自己蹦出来，都得点开一次。

## 这十个都是干什么的

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

## 地址（纯文本，方便复制）

**GitHub：**

https://github.com/lemonhall/dsh-radio-dock
https://github.com/lemonhall/dsh-finance-dock
https://github.com/lemonhall/dsh-rss-dock
https://github.com/lemonhall/dsh-calendar-dock
https://github.com/lemonhall/dsh-ledger-dock
https://github.com/lemonhall/dsh-calorie-dock
https://github.com/lemonhall/dsh-todo-dock
https://github.com/lemonhall/dsh-pomodoro-dock
https://github.com/lemonhall/dsh-irc-dock
https://github.com/lemonhall/dsh-qqmail-dock

**npm：**

https://www.npmjs.com/package/dsh-radio-dock
https://www.npmjs.com/package/dsh-finance-dock
https://www.npmjs.com/package/dsh-rss-dock
https://www.npmjs.com/package/dsh-calendar-dock
https://www.npmjs.com/package/dsh-ledger-dock
https://www.npmjs.com/package/dsh-calorie-dock
https://www.npmjs.com/package/dsh-todo-dock
https://www.npmjs.com/package/dsh-pomodoro-dock
https://www.npmjs.com/package/dsh-irc-dock
https://www.npmjs.com/package/dsh-qqmail-dock

十个都是 MIT。都只截右侧栏的面板图（我这台机器桌面左下角有真名，从不整屏）。

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
