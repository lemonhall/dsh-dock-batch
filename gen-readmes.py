"""给这批右侧栏插件批量生成 README.md。

一个模板 + 每个插件自己的要点 —— 8 份手写容易写歪，模板能保证结构一致。

    python gen-readmes.py
"""
import os

# 公共部分：所有插件都一样的那几段
COMMON_HEAD = """# {title} {emoji}

{blurb}

> 这是给 [DSH（DeepSeek Harness）](https://github.com/deepseek-ai/deepseek-harness) 右侧栏做的一排日常插件之一。
> 右侧栏本来就是 DSH 的「apps 入口」—— 官方的文件/终端/浏览器和第三方插件走的是**完全同一套机制**。

## 效果

![面板](https://cdn.jsdelivr.net/gh/lemonhall/{pkg}@main/docs/screenshot-panel.png)

（截图只裁了右侧栏面板。想换订阅源/分类/时长这些，改配置就行，不用碰代码。）
"""

COMMON_TAIL = """## 装

```
plugin_manager  install_bundle  target=link:{devdir}
```

或从 npm：

```
dsh plugin --profile <你的 profile> add {pkg}
```

装好之后：右侧栏点「**+**」→ 选「**{guide}**」。

⚠️ **客户端半边改动要重启一次应用**；宿主半边热生效 —— 但**新增宿主路由要重启**（实测，别指望热重载）。

## 它是怎么work的

```
lib/index.js    宿主半：路由 + {tool} 工具（Agent 侧读写同一份状态）
lib/state.js    本地状态（原子写：临时文件 + rename，读的人不会撞上写了一半的文件）
lib/client.js   右侧栏 tab（整个模块包在 IIFE 里 —— DSH 把所有客户端插件拼成一个脚本，
                顶层 const 会跨插件撞名，实测撞过一次直接把应用挡在启动之外）
```

**双向通道**：状态存在宿主，客户端 2 秒轮询。所以**你在面板里点一下，Agent 调工具就能读到**；
**Agent 写一次，面板自己会跟着变**。这不是"一个只读的看板"。

## 已知限制

{limits}

## License

MIT
"""

PLUGINS = [
    dict(
        dir="dsh-rss-dock",
        title="dsh-rss-dock",
        emoji="📰",
        guide="RSS 阅读器",
        tool="rss_panel",
        blurb="DSH 右侧栏的 **RSS 阅读器**：左边订阅源（带未读数）、右边条目，点开即标已读，可收藏。",
        features=[
            "**订阅源写在配置里**，RSS 2.0 与 Atom 都认（正则解析，不引 XML 库）",
            "默认 8 个源：华尔街日报（国际/市场/科技/美国商业）+ Hacker News + 少数派 + 阮一峰 + Cloudflare",
            "**只看未读**开关、星标收藏、按时间倒序",
            "宿主用 curl 走本机代理抓取，带重试；10 分钟缓存",
            "`rss_panel` 工具：Agent 可以直接读条目、标已读、收藏",
        ],
        limits="""- 只做阅读，**不做全文抓取**（摘要来自 feed 本身）
- 已读/收藏存本地，**不跟任何在线服务同步**
- feed 的可用性取决于对方；取不到的源会在面板顶上给出行数提示，不会静默""",
    ),
    dict(
        dir="dsh-calendar-dock",
        title="dsh-calendar-dock",
        emoji="📅",
        guide="日历",
        tool="calendar_panel",
        blurb="DSH 右侧栏的**通用日历**：月视图点选、当天事件、接下来一览；事件存本地，Agent 也能加/删/勾。",
        features=[
            "月视图（周一开头、今天描边、有事件打点）+ 当天事件列表 + 左下「接下来」",
            "回车即加、点方框勾完成、一键删除",
            "`calendar_panel` 工具：`today` / `upcoming` / `add` / `remove` / `done`",
            "**日期一律用本地时区的 `YYYY-MM-DD` 字符串**跨进程传，不传 Date 对象（避免时区漂移）",
        ],
        limits="""- **不跟系统日历/Google Calendar 同步**，就是一份自己的清单
- 不做重复事件、提醒通知（DSH 里没有系统通知那个口子）
- 时间用本地时区，没有跨时区事件的语义""",
    ),
    dict(
        dir="dsh-ledger-dock",
        title="dsh-ledger-dock",
        emoji="💰",
        guide="记账本",
        tool="ledger_panel",
        blurb="DSH 右侧栏的**记账本**：记一笔、看本月结余、按分类统计。",
        features=[
            "**金额一律存成「分」的整数**（不用浮点）—— 记账类程序最容易翻车的地方",
            "输入认 `12.5` / `￥12.50` / `12.5元` / `1,234.5`，拒三位小数和中文数字",
            "本月支出/收入/结余 + 当月流水 + 按分类的条形统计",
            "`ledger_panel` 工具：`add` / `summary` / `list` / `remove`",
            "21 项单测（金额解析边界 + 汇总口径）",
        ],
        limits="""- 只有**单币种**（配置里改符号，不做汇率换算）
- 不做预算、不做周期账单、不做导入导出（数据就在 `state.json` 里，想导随时拷）
- 统计只有"按月 + 按分类"，没有同比环比""",
    ),
    dict(
        dir="dsh-calorie-dock",
        title="dsh-calorie-dock",
        emoji="🔥",
        guide="卡路里日记",
        tool="calorie_panel",
        blurb="DSH 右侧栏的**卡路里日记**：内置常见食物热量表，选食物 + 克数自动算 kcal，看当日进度与近 7 天。",
        features=[
            "**内置约 90 条常见食物热量表**（主食/蛋白/蔬果/零食/调料）",
            "食物名**模糊匹配**：输「鸡胸」能找到「鸡胸肉」，输「拿铁咖啡」会落到「咖啡」",
            "每条记录**把算好的 kcal 一起存下来**（不只存克数）—— 以后调食物表，历史记录不会跟着变形",
            "按餐次记（早餐/午餐/晚餐/加餐）+ 当日目标进度条 + 近 7 天趋势",
            "`calorie_panel` 工具：`add` / `today` / `days` / `search` / `goal`",
        ],
        limits="""- 热量是**常见参考值**，量级对，**不必当营养学依据**
- 不做营养素（蛋白/脂肪/碳水）拆分，不做运动消耗
- 目标只是面板上的一条线，插件**不提供任何健康建议**""",
    ),
    dict(
        dir="dsh-todo-dock",
        title="dsh-todo-dock",
        emoji="✅",
        guide="待办",
        tool="todo_panel",
        blurb="DSH 右侧栏的**轻量待办**：一行一件、回车就加、勾掉即完成。",
        features=[
            "刻意做轻：**只有文字 + 完成状态 + 创建时间**",
            "未完成在前（新的在上）、已完成在后；可折叠、可一键清掉",
            "三个筛选：未完成 / 全部 / 已完成",
            "`keepDone` 默认只留最近 200 条已完成，防止清单无限长",
            "`todo_panel` 工具：`add` / `list` / `done` / `remove` / `clear_done`",
        ],
        limits="""- **不做优先级、截止日期、子任务、标签、提醒** —— 那属于任务管理器，不属于"随手记一下"
- 没有多清单/多项目
- 不跟任何外部待办同步""",
    ),
    dict(
        dir="dsh-pomodoro-dock",
        title="dsh-pomodoro-dock",
        emoji="🍅",
        guide="番茄闹钟",
        tool="pomodoro_panel",
        blurb="DSH 右侧栏的**番茄闹钟**：专注/休息循环计时，**计时在宿主侧**，切 tab、关面板都不中断。",
        features=[
            "**只存 `endsAt`（结束时刻），不跑定时器** —— 剩余时间 = endsAt − now，谁都能算",
            "所以切 tab、关掉侧栏、甚至重启应用，剩余时间都是对的",
            "25/5 分钟默认，第 4 个专注后自动转长休息（15 分钟），可配置",
            "圆环倒计时 + 本轮四点进度 + 今日完成数 + 最近几条记录",
            "`pomodoro_panel` 工具：`status` / `start` / `pause` / `resume` / `skip` / `reset` / `config`",
        ],
        limits="""- **不弹系统通知**（DSH 里没有这个口子），到点靠面板上看
- 不做任务关联（不统计"这件事花了几个番茄"）
- 计时精度取决于读取时刻，不是高精度计时器""",
    ),
    dict(
        dir="dsh-irc-dock",
        title="dsh-irc-dock",
        emoji="💬",
        guide="IRC 聊天",
        tool="irc_panel",
        blurb="DSH 右侧栏的 **IRC 客户端**：宿主用 node `net`/`tls` 直连（也可走本机代理的 HTTP CONNECT 隧道），右侧栏收发消息。",
        features=[
            "自己写的薄协议层：NICK/USER → PING/PONG → JOIN → PRIVMSG，**不引 irc 库**",
            "**两种连接方式**：直连，或先跟本机 Clash 做 HTTP CONNECT 建隧道再套 TLS",
            "**SASL PLAIN 认证**（Libera 从某些网络出口连必须它）、**允许自签证书**（EFnet 就是自签）",
            "**限次自动重连**（最多 3 次）—— 认证被拒这类问题重连一万次也没用",
            "消息只在内存（环形缓冲），**不落盘**；`irc_panel` 工具能读能发",
        ],
        limits="""- **凭据只从 `$DSH_HOME/dsh-irc-dock/secret.json` 读**（`{saslUser, saslPass}`），绝不进 git
- 不支持 DCC、文件传输、多服务器并发
- 消息不持久化，关掉就没了（这是有意的：聊天记录没必要写盘）""",
    ),
    dict(
        dir="dsh-qqmail-dock",
        title="dsh-qqmail-dock",
        emoji="📧",
        guide="QQ 邮箱",
        tool="qqmail_panel",
        blurb="DSH 右侧栏的 **QQ 邮箱**：读最近邮件、看正文、发纯文本（发送要二次确认）。",
        features=[
            "IMAP over SSL（`imap.qq.com:993`）读，SMTP over SSL（`smtp.qq.com:465`）发",
            "**授权码只从 `$DSH_HOME/dsh-qqmail-dock/secret.json` 读**，绝不进 git、不进日志、**不回显**",
            "**发送门禁**：必须显式 `confirm=true`（面板上也要点两次）",
            "正文提取：在 `bodyStructure` 里挑 `text/plain` → 退 `text/html` → 剥标签",
            "输出默认是摘要；正文按 `previewChars` 截断，避免把长邮件灌进上下文",
        ],
        limits="""- **只做「读 + 发」最小闭环**：不做 HTML 发送、附件、富文本、移动/删除/标已读
- 只支持 QQ 邮箱的服务器地址（改配置可换，但没为别的邮箱做过适配）
- 授权码不是 QQ 密码：要去 QQ 邮箱设置里单独生成""",
    ),
]


def render(p):
    features = "\n".join(f"- {item}" for item in p["features"])
    head = COMMON_HEAD.format(title=p["title"], emoji=p["emoji"], blurb=p["blurb"], pkg=p["dir"])
    tail = COMMON_TAIL.format(devdir="E:\\development\\" + p["dir"], pkg=p["dir"], guide=p["guide"], tool=p["tool"], limits=p["limits"])
    body = f"\n## 它能干什么\n\n{features}\n\n"
    return head + body + tail


def main():
    root = r"E:\development"
    for plugin in PLUGINS:
        path = os.path.join(root, plugin["dir"], "README.md")
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(render(plugin))
        size = os.path.getsize(path)
        print(f"{plugin['dir']:<22} README.md  {size // 1024} KB")


if __name__ == "__main__":
    main()
