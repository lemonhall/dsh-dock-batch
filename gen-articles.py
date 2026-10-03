"""一次生成：8 篇插件公众号文章 + 1 篇《我一口气开发了十个 DSH 插件》+ 截图拼图。

    python gen-articles.py

规则：**所有散文一律用三引号字符串** —— 上一版我在双引号字符串里用了半角引号，
字符串被提前截断，Python 把中文标点报成非法字符；我再用正则去补，又误伤 35 处。
三引号没有这个问题。

文章里「它能干什么 / 已知限制」两段直接从各插件的 README.md 里抠，保证文档与文章一致。
"""
import os
import re

ROOT = r"E:\development"
OUT_BATCH = os.path.join(ROOT, "dsh-dock-batch")

ARTICLES = [
    dict(
        dir="dsh-rss-dock", emoji="📰", name="RSS 阅读器",
        headline="""我给 DSH 的右侧栏塞了个 RSS 阅读器""",
        why="""我不缺 RSS 阅读器，我缺的是**一个就在我干活的地方、不用切窗口的** RSS 阅读器。写代码的时候右侧栏点一下，扫一眼标题，够了。""",
        design="""**正则解析 feed，不引 XML 库。** RSS 2.0 和 Atom 的骨架都很规矩，真正常见的坑只有一个：`<![CDATA[...]]>`。我第一版先剥标签再处理 CDATA，结果 Hacker News 的条目标题被整段吃掉、一条都解析不出来 —— 顺序反过来就好了。这个 bug 现在有一条回归测试盯着。""",
    ),
    dict(
        dir="dsh-calendar-dock", emoji="📅", name="通用日历",
        headline="""我给 DSH 的右侧栏做了个日历""",
        why="""我需要知道今天还有什么事，而不是打开一个日历应用去找今天在哪一格。""",
        design="""**日期一律用本地时区的 `YYYY-MM-DD` 字符串跨进程传，绝不传 Date 对象。** 跨进程传时间戳是时区漂移的经典来源：宿主在东八区算出来的今天，序列化一圈回来可能就成了昨天。字符串没有这个问题，而且人眼可读、日志里一眼看得懂。""",
    ),
    dict(
        dir="dsh-ledger-dock", emoji="💰", name="记账本",
        headline="""记账这件事，我把它做进了 DSH 的右侧栏""",
        why="""记一笔账的成本必须低到顺手就记了。打开 app、找分类、填表，那就不记了。""",
        design="""**金额一律存成分的整数，不用浮点。** 0.1 + 0.2 那个故事在记账程序里是致命的 —— 小数累加会漂，月末对不上账，你就再也不信这个软件了。输入解析认 `12.5`、`￥12.50`、`12.5元`、`1,234.5`，但拒三位小数和中文数字：宁可让人重输一次，也别猜错。""",
    ),
    dict(
        dir="dsh-calorie-dock", emoji="🔥", name="卡路里日记",
        headline="""我给 DSH 的右侧栏做了个卡路里日记""",
        why="""记热量的最大摩擦是，我还得先去查这东西多少卡。这一步应该由程序做掉。""",
        design="""**每条记录把算好的 kcal 一起存下来，不只存克数。** 这看着冗余，但很关键：以后我调整食物热量表（数据总会有修正），已经记下的历史不会跟着变形。数值型日记都该这么存 —— 记录是当时的结论，不是当时的过程。""",
    ),
    dict(
        dir="dsh-todo-dock", emoji="✅", name="待办",
        headline="""一个轻量待办，到底该有多轻""",
        why="""待办应用的通病是：功能越多，我越不想打开它。我需要的只是想到了记一条、做完勾掉。""",
        design="""**刻意不做优先级、截止日期、子任务、标签。** 这不是还没做，是设计边界 —— 那些属于任务管理器，不属于随手记。唯一多给的一点点是 `keepDone`（默认只留最近 200 条已完成），因为它挡的是清单无限增长这种必然发生的退化。""",
    ),
    dict(
        dir="dsh-pomodoro-dock", emoji="🍅", name="番茄闹钟",
        headline="""番茄钟的关键居然是别用定时器""",
        why="""我在 DSH 里切 tab、关侧栏、跑去干别的，然后回来 —— 计时器不能因此就废了。""",
        design="""**只存 `endsAt`（结束时刻），不跑定时器。** 剩余时间 = endsAt − now，谁都能随时算。于是切 tab、关面板、刷新页面、甚至重启应用，剩余时间都是对的；宿主也不用养一个可能被挂起的 interval。暂停时把剩余毫秒存进 `remainingMs`，恢复时换算成新的 endsAt —— 整个状态机就三个字段。""",
    ),
    dict(
        dir="dsh-irc-dock", emoji="💬", name="IRC 客户端",
        headline="""我在 DSH 里自己写了个 IRC 客户端，然后被 Libera 拒了""",
        why="""想验证一件事：右侧栏能不能承载一个有状态的长连接，而不只是个看板。""",
        design="""**被拒的那次，恰恰证明代码是对的。** 我连上 Libera 的 6697，TLS 成功，收到 `Checking Ident → Looking up hostname → No Ident response`，然后被 Closing Link 拒了 —— 原因是这个网络出口**必须用 SASL 认证**。所以我补了三件事：SASL PLAIN、允许自签证书（EFnet 就是自签，那个证书错误其实说明连上了）、以及**限次**自动重连 —— 认证被拒这类问题重连一万次也没用，重试 3 次就停下并说明原因。""",
    ),
    dict(
        dir="dsh-qqmail-dock", emoji="📧", name="QQ 邮箱",
        headline="""把 QQ 邮箱接进 DSH 右侧栏：两个 409 和一个流""",
        why="""收件箱里的东西经常需要被我处理 —— 那它就该出现在我干活的地方，而不是另一个窗口。""",
        design="""**授权码只从私有文件读，且任何输出都先过一遍打码。** 凭据存在 `$DSH_HOME/dsh-qqmail-dock/secret.json`，不进 git、不进日志。真正难的不是 IMAP，是 imapflow 的 `download()`：它返回 Promise，而解出来的 `content` 是**流** —— 我第一版直接拿返回去 `for await`，面板上报 `not a function or its return value is not async iterable`；改成同步读又得到 `[object Object]`。正解是 `await` 之后再 `for await` 收集。另外**发送必须显式 confirm**（面板上也要点两次）。""",
    ),
]

TEN = [
    ("dsh-radio-dock", "📻", "车载电台", "右侧栏里的一个 3D 车载电台：车模、弯道、月亮星空、车流超车。"),
    ("dsh-finance-dock", "📈", "金融终端", "13 类 48 个标的 + three.js 地球，点列表里的标的，地球自动转过去。"),
    ("dsh-rss-dock", "📰", "RSS 阅读器", "8 个源、未读与收藏双向状态，Agent 也能读。"),
    ("dsh-calendar-dock", "📅", "通用日历", "月视图 + 当天事件 + 接下来，日期用本地字符串跨进程。"),
    ("dsh-ledger-dock", "💰", "记账本", "金额按分存整数，本月结余 + 分类统计。"),
    ("dsh-calorie-dock", "🔥", "卡路里日记", "内置食物热量表，选食物加克数自动算 kcal。"),
    ("dsh-todo-dock", "✅", "待办", "一行一件、回车就加、勾掉即完成。"),
    ("dsh-pomodoro-dock", "🍅", "番茄闹钟", "只存 endsAt 的计时，切 tab 不中断。"),
    ("dsh-irc-dock", "💬", "IRC 客户端", "自己写的薄协议层，SASL 加自签证书加限次重连。"),
    ("dsh-qqmail-dock", "📧", "QQ 邮箱", "读最近邮件、看正文、发纯文本，发送要 confirm。"),
]

STORY = """# 我一口气给 DSH 开发了十个插件

DSH（DeepSeek Harness）是个 Electron 桌面应用，界面左边是对话，右边是**右侧栏**。

右侧栏本来是放官方那三个 tab 的：文件、终端、浏览器。我把它的源码读了一遍才发现 ——
**官方的文件和第三方插件走的是完全同一套机制**。

那一瞬间我意识到：右侧栏不是「一个侧边栏」，它是这个应用的 **apps 入口**。

于是我从「给我自己加点工具」，变成了「给我自己写一排 app」。

## 十个，是这么攒出来的

一开始只是想要个电台。后来想要看行情。再后来发现：**我想要的东西基本都是「一小块信息 + 一点点交互」** ——
而这正好是右侧栏的尺寸。

{details}

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
{install_cmds}
```

装完**重启一次应用**（这类插件的界面半边在启动时就固化了，Ctrl+F5 不管用），
然后**右侧栏点「+」**才能看到它们 —— 右侧栏的 tab 不会自己蹦出来，都得点开一次。

## 这十个都是干什么的

{details}

## 地址（纯文本，方便复制）

**GitHub：**

{gh_list}

**npm：**

{npm_list}

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
"""


def section(text, title):
    hit = re.search(rf"## {re.escape(title)}\n(.*?)(?=\n## |\Z)", text, re.S)
    return hit.group(1).strip() if hit else ""


def render_article(item):
    with open(os.path.join(ROOT, item["dir"], "README.md"), encoding="utf-8") as handle:
        readme = handle.read()
    shot = "https://cdn.jsdelivr.net/gh/lemonhall/" + item["dir"] + "@main/docs/screenshot-panel.png"
    return (
        "# " + item["headline"] + "\n\n"
        + item["emoji"] + " **" + item["name"] + "** —— DSH 右侧栏的一个新 tab。\n\n"
        + "## 为什么做这个\n\n" + item["why"] + "\n\n"
        + "## 长什么样\n\n![" + item["name"] + "](" + shot + ")\n\n"
        + "（图只截了右侧栏面板。我这台机器桌面左下角有真名，所以截图从来不整屏。）\n\n"
        + "## 它能干什么\n\n" + section(readme, "它能干什么") + "\n\n"
        + "## 一个值得说的设计决定\n\n" + item["design"] + "\n\n"
        + "## 双向的，不只看\n\n"
        + "这是这批插件的共同点：**状态在宿主、界面 2 秒轮询**。所以我在面板里点一下，Agent 调工具就能读到；"
        + "Agent 写一次（比如「帮我记一笔午饭 12.5」），面板自己就变了。\n\n"
        + "装：\n\n```\n# 先装 DSH（桌面版从 https://harness.deepseek.com 下载安装包；只要 CLI 的话）：\n"
        + "npm i -g @deepseek-ai/dsh\n\n"
        + "# 再装这个插件（桌面版也可以走 GUI：右侧栏「插件 → 添加插件」）\n"
        + "dsh plugin --profile desktop add " + item["dir"] + "\n\n"
        + "# 如果你是开发者、想用本地目录直接挂：\n"
        + "plugin_manager install_bundle target=link:E:\\development\\" + item["dir"] + "\n```\n\n"
        + "代码在 <https://github.com/lemonhall/" + item["dir"] + ">，npm 上是 `" + item["dir"] + "`。"
        + "右侧栏点「**+**」→ 选「" + item["name"] + "」就能看到它。\n\n"
        + "## 已知限制\n\n" + section(readme, "已知限制") + "\n"
    )


def render_story():
    details = "\n".join("- " + e + " **" + n + "**（`" + p + "`）—— " + d for p, e, n, d in TEN)
    gh_list = "\n".join("https://github.com/lemonhall/" + p for p, _, _, _ in TEN)
    npm_list = "\n".join("https://www.npmjs.com/package/" + p for p, _, _, _ in TEN)
    # 一行一个，方便直接复制粘贴
    install_cmds = "\n".join("dsh plugin --profile desktop add " + p for p, _, _, _ in TEN)
    return (
        STORY.replace("{details}", details)
        .replace("{gh_list}", gh_list)
        .replace("{npm_list}", npm_list)
        .replace("{install_cmds}", install_cmds)
    )


def make_collage():
    from PIL import Image, ImageDraw

    images = []
    for item in ARTICLES:
        path = os.path.join(ROOT, item["dir"], "docs", "screenshot-panel.png")
        if os.path.exists(path):
            images.append((item["dir"], Image.open(path).convert("RGB")))
    if not images:
        print("没有可拼的截图")
        return
    cell_w, gap, label_h, cols = 420, 14, 26, 4
    scaled = []
    for name, image in images:
        ratio = cell_w / image.width
        scaled.append((name, image.resize((cell_w, round(image.height * ratio)), Image.LANCZOS)))
    cell_h = max(image.height for _, image in scaled)
    rows = (len(scaled) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * cell_w + (cols + 1) * gap, rows * (cell_h + label_h) + (rows + 1) * gap), (14, 18, 20))
    draw = ImageDraw.Draw(canvas)
    for index, (name, image) in enumerate(scaled):
        row, col = divmod(index, cols)
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + label_h + gap)
        canvas.paste(image, (x, y + label_h))
        draw.text((x + 4, y + 6), name, fill=(150, 230, 180))
    out = os.path.join(OUT_BATCH, "collage-panels.png")
    canvas.save(out, optimize=True)
    print(out + "  " + str(canvas.size[0]) + "x" + str(canvas.size[1]))


def main():
    for item in ARTICLES:
        path = os.path.join(ROOT, item["dir"], "docs", "wechat-article.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        text = render_article(item)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        print(item["dir"].ljust(22) + " docs/wechat-article.md  " + str(len(text)) + " 字")
    story = render_story()
    out = os.path.join(OUT_BATCH, "article-ten-plugins.md")
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(story)
    print("总文".ljust(20) + " article-ten-plugins.md  " + str(len(story)) + " 字")
    make_collage()


if __name__ == "__main__":
    main()
