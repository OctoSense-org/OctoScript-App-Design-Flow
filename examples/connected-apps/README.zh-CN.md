# 连接账户的参考应用

[English](README.md) | 简体中文

这三个 App Hub 应用通过 OctoSense 宿主登录 GitHub 或 Google。应用始终看不到密码或令牌，只拿到一个绑定单个账户的不透明连接句柄；所有对提供商的调用都由宿主完成。整个过程不涉及 OctoSense 账户。

三个应用均已发布，App Hub 的[提交指南](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md#三个参考应用)以它们为示例。研究它们，可以了解连接账户的应用如何构建，哪些做法值得照搬，哪些应当避免。

## 三个应用

| 应用 | 应用 ID | 发布源码 | 学习重点 |
| --- | --- | --- | --- |
| [GitHub Notes](github-notes/README.zh-CN.md) | `org.octosense.samples.githubnotes` | [ymote/octosense-github-notes](https://github.com/ymote/octosense-github-notes) | 经宿主确认后才执行的 GitHub 提交 |
| [Inbox Assistant](inbox/README.zh-CN.md) | `org.octosense.samples.inbox` | [ymote/octosense-inbox-assistant](https://github.com/ymote/octosense-inbox-assistant) | Gmail 读取、后台应用 Agent、速览卡片模板，以及必须亲手点按才会发出的邮件 |
| [Google Calendar](google-calendar/README.zh-CN.md) | `org.octosense.samples.googlecalendar` | [ymote/octosense-google-calendar](https://github.com/ymote/octosense-google-calendar) | 带缓存的日历同步、经宿主确认的日程保存、能回到应用的速览卡片，以及只提供建议的 Agent |

App Hub 签名目录第 10 版为每个应用收录了 0.1.0 和 0.1.1 两个版本，发布者都是 `ymote`，状态都是 `offered`。商店显示最新的 0.1.1。每个版本都从各自仓库的对应标签（`v0.1.0`、`v0.1.1`）发布。本指南以 0.1.0 中的三个问题为教训，0.1.1 对它们作了处理（见[不要照搬的做法](#不要照搬的做法)）。

这里的各个目录是已发布 0.1.1 的未签名开发副本。除两个文件外，其余文件都与发布版逐字节相同：

- `listing.json`：发布者名称、支持 URL 和隐私政策 URL 是占位内容，供你替换。商店信息的其余内容与发布版一致。
- `manifest.json`：没有签名；由于 `listing.json` 不同，摘要也不同。已发布的清单还写出了 `hub sign-manifest` 补全的默认值，例如 `"network": {"hosts": []}` 和 `"tier": "standard"`。GitHub Notes 的副本则写明了默认值 `"background": false`，而已发布的清单省略了这一项。每个副本声明的版本、能力、存储和 Agent 都与发布版相同。

## 运行这些应用

### 需要准备什么

| 条件 | 原因 |
| --- | --- |
| macOS（Apple 芯片）上的 [OctoSense desktop-v0.1.0-beta.2](https://github.com/OctoSense-org/OctoSense/releases/tag/desktop-v0.1.0-beta.2) | 从这个版本起，App Hub 契约（1.5）准入 `auth`、`github`、`gmail`、`gcalendar`，Shell 也提供这些服务。它还带有 GitHub Notes 使用的 `MarkdownEditor` 控件。 |
| 宿主 `<apps root>/.host/oauth/clients.json` 中的提供商注册信息 | OAuth 客户端归宿主所有，不归应用。beta.2 只从这个文件读取注册信息，下载包里也没有内置。[OctoSense 桌面版 0.1.0-rc.1](../../README.zh-CN.md#下载兼容-shell)（RC1）及之后的构建可以改为把注册信息编译进去，但公开的 RC1 安装包不含任何注册信息。 |
| 启用设备授权流程的 GitHub OAuth 应用 | GitHub Notes 用它登录。 |
| 启用 Gmail 和 Calendar API 的 Google 桌面 OAuth 客户端，并配置好同意界面和测试用户 | Inbox Assistant 和 Google Calendar 用它登录。 |

OctoSense 的[宿主配置指南](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/crates/oauth-service/README.zh-CN.md)给出 `clients.json` 的格式，以及各提供商的注册方法。

已知限制：

- 更早的版本会列出这些应用，但不提供安装：desktop-v0.1.0-beta.1 和 home-v0.1.0-beta.1 会拒绝安装每一个应用，报错 `unknown capability "auth"`。
- 缺少 `clients.json` 时，连接账户会失败：`OAuth is not configured. Add provider registrations in the host's oauth/clients.json`。
- **尚未支持：** Android 上的 Google 登录。宿主会返回 `Google authorization needs the Android host adapter; desktop login is not supported on this device`。目前没有任何已发布的手机版本能安装这些应用。
- **未验证：** 用真实 GitHub 和 Google 账户进行的大部分读取和写入。本目录记录的运行都使用模拟提供商；OctoSense 记录了两次 macOS 上的真实检查，见 [CAPABILITIES § 限制](../../docs/CAPABILITIES.zh-CN.md#限制)。

### 安装已发布的应用

1. 安装 OctoSense desktop-v0.1.0-beta.2，并把提供商注册信息写入 `clients.json`。
2. 在 OctoSense 中打开 App Hub，找到应用，查看它申请的权限，然后安装。如果能看到应用却无法安装，说明你的 Shell 早于 beta.2，请安装 beta.2。
3. 打开应用并连接账户。宿主显示自己的授权面板，并打开浏览器，让你在提供商页面登录；应用只拿到连接句柄。如果连接失败并提示 `OAuth is not configured`，说明宿主找不到你的注册信息，请检查 `clients.json` 的路径和其中的提供商条目。

### 运行开发副本

App Hub 的 `card-host` 运行这些应用包时不提供任何宿主服务。按 [QUICKSTART](../../docs/QUICKSTART.zh-CN.md) 构建它，再从仓库根目录启动应用：

```sh
tools/octo run examples/connected-apps/inbox/bundle --port 8141 --hidden --detach
```

各应用的表现如下：

- Inbox Assistant 打开虚构收件箱；Google Calendar 打开空日程，仍可编写本地草稿。所有连接账户的调用都会失败，应用会显示错误，例如 `Google sign-in unavailable: no service answers "auth" on this device`。
- GitHub Notes 不显示编辑器。`card-host` 没有 `MarkdownEditor`，日志中出现 `widget 'editor' not found in tree`。

哪个 Shell 提供哪个服务，见 [HOST-SERVICES](../../docs/HOST-SERVICES.zh-CN.md)。每个应用的 README 列出了本地检查和签名安装后的验收流程；后者使用 OctoSense 的测试宿主和模拟提供商。

## 每个应用的构成

| | GitHub Notes | Inbox Assistant | Google Calendar |
| --- | --- | --- | --- |
| 能力 | `storage`、`auth`、`github` | `storage`、`auth`、`gmail`、`model`、`glance`、`octos.session.open`、`octos.turn.start` | `storage`、`auth`、`gcalendar`、`glance`、`octos.session.open`、`octos.turn.start` |
| 存储 | 按账户，4 MiB | 按账户，16 MiB（默认值） | 按账户，1 MiB，Agent 不读取文件 |
| `agent` 块 | 仅前台，只读（0.1.0 中没有） | 后台运行，由 `inbox.new_message` 触发，一个技能 | 仅前台，只提供建议 |
| `tools.json` | 3 个读取工具 | 9 个工具：4 个读取，5 个操作 | 4 个读取工具 |
| 速览卡片 | 无 | 模板文件 `glance-workspace.splash` | `main.splash` 内的 [L0](../../docs/GLOSSARY.md) 卡片源码 |
| 受保护的写入 | 通过 `github.review_save` 提交到 GitHub | 通过 `gmail.draft.review` 发送 Gmail | 通过 `gcalendar.review_save` 保存日程 |
| 宿主确认时是否要求亲手点按：desktop-v0.1.0-beta.2 | 否 | 是 | 否 |
| 宿主确认时是否要求亲手点按：macOS 上的 RC1 | 是 | 是 | 是 |

三个应用遵循相同的规则：

- **用权限别名连接。** 应用以提供商和简短的权限名调用 `auth.connect`，只保存返回的句柄。
- **按账户保存数据。** `storage.accounts: true` 让每个已连接账户拥有独立的数据目录和独立的 Agent。
- **把工具映射到经过审核的宿主方法。** 每个工具都是 `implemented_by: "host-service"`，`host_method` 取自 App Hub 审核过的列表，并声明 `private_data: true` 和 `shareable: false`。该列表及各方法的最低风险等级见 App Hub 的 [PUBLISHING](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md#把工具映射到共享服务host_method)。
- **不让工具触及受保护的写入。** `github.review_save`、`gcalendar.review_save` 和 `gmail.draft.review` 都不在该列表中，`host_method` 也不能指向宿主面板。任何 Agent 工具都无法提交到 GitHub、保存日程或发送邮件。

### GitHub Notes

一个把笔记提交到 GitHub 仓库的 Markdown 编辑器。

| 能力 | 调用 | 用途 |
| --- | --- | --- |
| `auth` | `auth.connect`、`auth.accounts`、`auth.active`、`auth.select`、`auth.disconnect` | GitHub 授权、选择账户、退出登录 |
| `github` | `github.repositories`、`github.files`、`github.read`、`github.review_save` | 浏览仓库、加载笔记及其 blob SHA、确认后提交 |
| `storage` | 用 `fs.read`/`fs.write` 读写 `recovery.json` | 未发送的草稿和一份恢复副本 |

用户在连接前选择公开或私有仓库权限。公开权限申请 `read:user` 和 `public_repo`；私有权限申请 `read:user` 和 `repo`。

**存储。** 摘自 `bundle/manifest.json`：

```json
"storage": {
  "accounts": true,
  "max_bytes": 4194304
}
```

**Agent。** 0.1.0 版附带了 `tools.json`，却没有 `agent` 块，因此 Shell 照样给这个应用配了一个 Agent，见[没有 agent 块的工具](#没有-agent-块的工具)。0.1.1 版和本副本都声明了这个 Agent。摘自 `bundle/manifest.json`：

```json
"agent": {
  "background": false,
  "instructions": "AGENT.md",
  "model": {
    "local_only": false,
    "needs": [
      "tool_calling"
    ]
  },
  "profile": "read-only",
  "tools": []
}
```

这个 Agent 只在用户发起请求时通过 **Ask GitHub Notes** 运行，而且要先经用户允许；安装应用或连接 GitHub 都不会启动它。`AGENT.md` 把仓库内容视为不可信的数据，只让 Agent 使用三个只读工具，任何保存都请用户回到编辑器，经宿主确认。

**工具。** 三个读取工具映射到 GitHub 服务。摘自 `bundle/tools.json`（省略输入 schema）：

```json
{
  "name": "githubnotes.read",
  "description": "Read a UTF-8 note from the selected repository branch, including its current blob SHA.",
  "risk": "read",
  "background": false,
  "shareable": false,
  "private_data": true,
  "implemented_by": "host-service",
  "host_method": "github.read"
}
```

`githubnotes.repositories` 和 `githubnotes.files` 以同样方式分别映射到 `github.repositories` 和 `github.files`。

**速览卡片。** 无。

**受保护的写入。** 点纸飞机按钮会冻结草稿，并请宿主确认：

```text
host.request("github.review_save", {connection: frozen.connection, file: {owner: frozen.owner, repo: frozen.repo, branch: frozen.branch, path: frozen.path, sha: frozen.sha, content: frozen.content, message: frozen.message}}, fn(r){ … })
```

宿主打开自己的面板，显示确切的仓库、分支、路径、提交说明和内容。只有用户在面板中按下 **Approve & Save**，GitHub 才会收到提交。应答带有 `commit_sha` 时，应用才报告成功。有了 blob `sha`，过时的保存会因冲突而失败，而不会覆盖更新的文件。

宿主只在前台应用之上弹出面板；后台卡片或 Agent 的工具调用会得到 `Open the app to review this change`。确认请求 10 分钟后过期。宿主接受批准的方式因版本而异：

- **desktop-v0.1.0-beta.2：** 只接受来自自身面板的批准，但不检查是否为亲手点按。
- **macOS 上的 RC1：** 只接受用户在原生 **Approve & Save** 控件上亲手点按的批准，使用与 Gmail 发送同类的原生审阅界面。它同样在按下和点击时都检查 Makepad 的 `trusted_user_input()`，每次批准只能用一次。脚本或 Agent 发起的请求会得到 `Saving requires a physical activation of the native host review. Script and agent requests cannot approve it.`。在 Windows 和 Linux 上，RC1 不允许保存：受保护的写操作一律拒绝执行。

### Inbox Assistant

一个 Gmail 客户端：每封邮件保存一份回复，并由应用 Agent 分拣新邮件。

| 能力 | 调用 | 用途 |
| --- | --- | --- |
| `auth` | `auth.connect`、`auth.active`、`auth.disconnect` | Google 授权，申请 `openid`、`email`、`profile`、`mail.read`、`mail.send` |
| `gmail` | `gmail.messages`、`gmail.message`、`gmail.draft.open`、`gmail.draft.get`、`gmail.draft.edit`、`gmail.draft.review`、`gmail.events.status` | 读取邮件、在宿主保存一份回复草稿、请求发送审阅、显示新邮件监测状态 |
| `model` | `model.complete` | 前台的 **AI sort** 按钮 |
| `octos.session.open`、`octos.turn.start` | `octos.session.open`、`octos.turn.start` | 在 Chat 标签页中打开 Agent 会话并发送一轮对话 |
| `glance` | `glance.publish`、`glance.withdraw` | 发布邮件卡片，发送后撤下 |
| `storage` | 用 `fs.read`/`fs.write` 读写 `inbox-local.json` | 虚构草稿和所选句柄 |

应用源码是 `src/workspace.splash`。`build_bundle.py` 根据它生成 `bundle/main.splash` 和速览卡片模板，因此请修改源码后重新运行该脚本。

**存储。** `"storage": {"accounts": true}` 没有设置 `max_bytes`，因此准入检查（`hub check`）授予默认的 16 MiB。真实的回复草稿和发送回执保存在宿主，按应用和连接区分；应用自己的目录只保存虚构草稿和句柄。

**Agent。** 摘自 `bundle/manifest.json`：

```json
"agent": {
  "background": true,
  "instructions": "AGENT.md",
  "model": {
    "needs": [
      "tool_calling"
    ]
  },
  "profile": "read-only",
  "skills": [
    "incoming-mail-triage"
  ],
  "tools": [
    "ask_user_question"
  ],
  "triggers": {
    "events": [
      "inbox.new_message"
    ]
  }
}
```

- `background` 和 `triggers` 让宿主在新邮件到达时启动一轮对话。事件名是应用命名空间（ID 的最后一段，即 `inbox`）加上 `.new_message`。
- Shell 在每轮对话中把 `AGENT.md` 和技能的 `SKILL.md` 作为指引加载。两者都把邮件文本视为不可信数据。
- `profile: "read-only"` 是 OctoSense Agent 内核的文件权限配置：每次写文件都要先征得用户同意。它不阻止风险为 `act` 的工具。
- `ask_user_question` 是应用 Agent 唯一可以保留的内核工具。

**工具。** 九个工具都在宿主服务上运行，均为 `background: true`、`private_data: true`、`shareable: false`，没有一个能发送邮件。

| 工具 | `host_method` | 风险 |
| --- | --- | --- |
| `inbox.messages` | `gmail.messages` | `read` |
| `inbox.message` | `gmail.message` | `read` |
| `inbox.draft_open` | `gmail.draft.open` | `act` |
| `inbox.draft_get` | `gmail.draft.get` | `read` |
| `inbox.draft_edit` | `gmail.draft.edit` | `act` |
| `inbox.event_status` | `gmail.event.status` | `read` |
| `inbox.event_decide` | `gmail.event.decide` | `act` |
| `inbox.notify` | `glance.publish` | `act` |
| `inbox.withdraw` | `glance.withdraw` | `act` |

`inbox.event_status` 和 `inbox.event_decide` 读取并记录 Agent 对单封新邮件的分拣决定。应用自己调用的 `gmail.events.status` 则不同：它只报告新邮件基线是否就绪。

**速览卡片。** 卡片是应用包中的文件 `glance-workspace.splash`，与应用由同一份源码生成。发布时，应用指定模板并传入初始值。摘自 `bundle/main.splash`：

```text
if demo {args["script"]="let initial = "+{connection:connection demo:demo message:card_message}.to_json()+"\nlet card_source = \"\"\n"+card_source}
else {args["template"]="glance-workspace.splash" args["initial"]={message:card_message}}
```

使用真实账户时，宿主从已安装且通过摘要校验的应用包中读取模板，并把卡片绑定到应用当前的账户。如果模板之外还传入 `source`、`script` 或 `data`，宿主会拒绝。卡片按应用自身的策略运行，所以卡片里的 Reply 和 Chat 标签页操作的是同一份宿主草稿。只有虚构演示会发布 `script` 卡片。

**受保护的写入。** **Review & Send** 以草稿及其版本号调用 `gmail.draft.review`。宿主在原生审阅界面中显示完整的已保存邮件，只有亲手点按批准按钮后才发送。它在按下和点击时都检查 Makepad 的 `trusted_user_input()`。macOS 的指针输入和 Android 的触摸符合条件；其他平台、远程控制和合成输入都不符合，因此在这些情况下发送一律失败。应用或 Agent 试图批准时会得到 `Apps and agents cannot approve sending. Request draft.review and physically activate the native host control.`

### Google Calendar

一个日历客户端：缓存日程，编辑需经宿主确认，在速览栏中显示日程卡片，并带有只提供建议的 Agent。

| 能力 | 调用 | 用途 |
| --- | --- | --- |
| `auth` | `auth.connect`、`auth.accounts`、`auth.active`、`auth.select`、`auth.disconnect` | Google 授权，申请 `openid`、`email`、`calendar.list`、`calendar.events` |
| `gcalendar` | `gcalendar.calendars`、`gcalendar.cached`、`gcalendar.refresh`、`gcalendar.prepare`、`gcalendar.review_save` | 日历列表、缓存日程、同步、日期和时区检查、确认后保存 |
| `glance` | `glance.publish`、`glance.withdraw`、`glance.take_open` | 发布日程卡片、撤下卡片、从卡片回到对应日程 |
| `octos.session.open`、`octos.turn.start` | `octos.session.open`、`octos.turn.start` | 打开 Agent 会话，就所选日程聊天 |
| `storage` | 对 `draft.json`、`selection.json`、`publications.json` 的 `fs` 调用 | 未发送的草稿、所选账户和日历、已发布的卡片 |

**存储。** 摘自 `bundle/manifest.json`：

```json
"storage": {
  "accounts": true,
  "agent_workspace": "none",
  "max_bytes": 1048576
}
```

`agent_workspace: "none"` 不给 Agent 任何文件，它只能看到工具返回的内容。宿主在应用目录之外缓存日程，每个应用、连接和日历各一份缓存。

**Agent。** 摘自 `bundle/manifest.json`：

```json
"agent": {
  "instructions": "AGENT.md",
  "model": {
    "needs": [
      "tool_calling"
    ]
  },
  "profile": "read-only",
  "tools": []
}
```

没有 `background` 标志，也没有触发器，因此 Agent 只在用户提问时运行。`AGENT.md` 把日程文本视为不可信内容，并引导用户通过 **Edit** 和宿主确认来修改日程。

**工具。** 四个读取工具，均为 `background: false`：`googlecalendar.calendars`、`googlecalendar.cached` 和 `googlecalendar.refresh` 映射到同名的 `gcalendar` 方法，`googlecalendar.event` 映射到 `gcalendar.get`。

**速览卡片。** 卡片是 `bundle/main.splash` 中的一段 L0 源码字符串（`let glance_source = …`）。应用为每个日程的卡片设置独立的聊天线程，再连同数据和返回应用的路由一起发布：

```text
host.request("glance.publish", {card_id: event.card_id title: event.card_title summary: event.card_summary source: card data: {ev: {…}} open: {app: "org.octosense.samples.googlecalendar" route: route} expires: 86400 notify: false}, fn(r){ … })
```

点击卡片中的 **Open Calendar** 会启动应用。应用通过 `glance.take_open` 取得路由，打开同一账户、日历和日程。每次同步后，应用重新发布日程有变化的卡片，并撤下日程已不在同步结果中的卡片。

**受保护的写入。** 保存需要两次宿主调用。`gcalendar.prepare` 检查日期、时间和 IANA 时区，拒绝因夏令时切换而跳过或重复的本地时间。随后 `gcalendar.review_save` 打开宿主面板，显示确切的日程。编辑会带上日程的 ETag；如果远端已经修改过这个日程，保存会失败并返回 HTTP 412，不会覆盖远端的修改。批准方式与 GitHub Notes 相同：desktop-v0.1.0-beta.2 的面板不检查是否为亲手点按，RC1 则要求亲手点按。

## 哪些可以照搬，哪些不要照搬

### 可以照搬的做法

除了三个应用共同遵循的四条规则，还有：

- 每次写入提供商都经过宿主确认，并只凭提供商的回执报告成功：提交 SHA、刷新后的日程、Gmail 状态。
- 给每个工具选择够用的最低风险等级。
- Agent 只需要工具时，设置 `agent_workspace: "none"`。
- 在 `AGENT.md` 中告诉 Agent：提供商返回的内容是数据，不是指令。
- 用应用包内的模板发布速览卡片，由宿主绑定账户。
- 只列出测试过的平台。三个应用都在 `listing.json` 中设置 `"platforms": ["macos"]`。

### 不要照搬的做法

这四种做法都通过了 App Hub 审核，但各自带有风险或意外。0.1.1 修复了前两种，并为第三种显示日期范围；第四种仍留在 Inbox Assistant 中。宿主一侧的行为因版本而异，所以前三条教训都会分别说明 desktop-v0.1.0-beta.2 和 RC1 的情况。

#### 接受 `script` 的速览卡片工具

Inbox Assistant 0.1.0 的 `inbox.notify` 工具映射到 `glance.publish`，在后台运行；除了 `template` 和 `source`，它的输入 schema 还接受完整的 Splash 程序。摘自它的 `bundle/tools.json`：

```json
"script": {
  "type": "string",
  "maxLength": 16384
},
```

`script` 卡片是一段 Splash 程序，在速览栏中按应用的策略和权限运行。Agent 的后台对话由新邮件触发，因此一封邮件里的文字就可能引导这轮对话，发布发件人指定的任意程序。

- **0.1.1 的改动：** `inbox.notify` 去掉了 `script`、`source` 和 `data`，改为必须提供 `template`、`initial`、`card_id`、`title`、`summary` 和 `notify`。它的描述写明 `Executable card source is not accepted.`。本仓库的副本与之一致。
- **RC1：** 只要 Agent 工具映射到 `glance.publish`，宿主就拒绝其中的 `script`：`Agents cannot publish executable Splash; choose an admitted template with initial data, or L0 source`。模板卡片必须提供模板名和 `initial` 对象，Agent 提供的 `source` 也必须是有效的 L0。应用自己的脚本仍可以发布 `script` 卡片。
- **desktop-v0.1.0-beta.2：** 宿主没有这项检查，所以像 0.1.0 那样接受 `script` 的 Agent 工具仍能发布这种卡片。

**改用以下做法：** 发布卡片的工具只接受 `template` 和 `initial`，或 L0 `source` 加 `data`，绝不接受 `script`。把 `template` 限定为应用包内的文件，并给 `initial` 定义严格的 schema：

```json
"template": {
  "type": "string",
  "enum": [
    "glance-workspace.splash"
  ]
},
```

0.1.1 版和本仓库的副本都是这样做的，并设置了 `additionalProperties: false`。

#### 没有 agent 块的工具

GitHub Notes 0.1.0 没有声明 `agent` 块，却附带了 `tools.json`。`hub check` 报告 `agent none`，但 App Hub 仍把这些工具作为 Agent 包准入。OctoSense 把附带已准入工具的应用都视为 Agent 应用，于是 Shell 为它提供了 **Ask GitHub Notes**，商店显示的却是 `Runs no assistant.`。发布者在打 0.1.0 标签之后才修订隐私政策，补充说明这个 Agent。

- **0.1.1 的改动：** 清单声明了这个只在前台运行的只读 Agent 及其 `AGENT.md`，商店信息的描述也说明了 **Ask GitHub Notes**。三个读取工具没有变化。
- **RC1 和 desktop-v0.1.0-beta.2：** 两者仍会给附带 `tools.json` 的应用配一个 Agent，但商店里的说明不同：

| 商店文字 | desktop-v0.1.0-beta.2 | RC1 |
| --- | --- | --- |
| 隐私概要，0.1.0 | `Runs no assistant.` | `Offers the host's Ask assistant for its admitted tools, only after you consent. Your conversation and tool results may be sent to your configured AI provider.` 和 `No app-declared background assistant or automatic triggers.` |
| 隐私概要，0.1.1 | `Runs an assistant limited to this app's own data.` | 相同 |
| 权限说明，0.1.1 | `Run an assistant for this app (no tools), inside this app's own data only` | `Run an assistant for this app, only after you allow it` 和 `Its assistant can use these app tools: githubnotes.repositories, githubnotes.files, githubnotes.read` |

商店只列出最新版本，所以用户现在看到的是 0.1.1 的文字。beta.2 的商店显示 `(no tools)`，是因为它只统计 `agent.tools` 中的工具，而这里是空的；Agent 实际上仍能调用三个读取工具。

**改用以下做法：** 如果附带工具，就声明 `agent` 块，并在商店信息和隐私政策中说明这个 Agent。如果不想要 Agent，就不要附带 `tools.json`。

#### 同步整个日历

Google Calendar 通过 `gcalendar.refresh` 刷新。在 desktop-v0.1.0-beta.2 上，这会同步整个日历：宿主向 Google 请求全部日程，不设起始日期，并把快照按从旧到新排序。应用显示前 100 个日程，所以有多年历史的日历打开后显示的是最早的条目。大型日历一旦触及宿主上限就会同步失败：100 页、25,000 个日程、16 MiB 缓存，或每次刷新 35 秒。`googlecalendar.cached` 和 `googlecalendar.refresh` 工具会把整个快照交给模型。0.1.0 也没有告诉用户日程覆盖哪段日期。

- **0.1.1 的改动：** 宿主报告同步窗口时，状态行显示 `past 30 days / next 366 days`；不报告时显示 `date range unavailable`。所选日程在同步后消失时，应用会提示它可能在显示的日期范围之外，而不是说它已不在日历中。本仓库的副本也有这项改动。
- **RC1：** 宿主只同步一个固定窗口：按 UTC 日界，从今天之前 30 天到之后 366 天，并把重复日程展开为单次日程。上限不变。
- **desktop-v0.1.0-beta.2：** 宿主仍同步整个日历，从最早的日程开始排列，也不报告窗口，所以 0.1.1 显示 `date range unavailable`。

**改用以下做法：** 限定显示的范围和 Agent 读取的范围。按每个日程的开始时间筛选，让日程从今天开始，再向后翻页；给 Agent 提供 `googlecalendar.event` 这类针对单个日程的工具，而不是读取整个日历。

#### 在后台改写草稿的工具

Inbox Assistant 的 `inbox.draft_edit` 设为 `background: true`，并接受 `to`、`subject` 和 `body`。由新邮件触发的一轮对话可以改写任何未发出的回复，包括收件人。在这次改写和发送之间，唯一的防线是发送审阅界面要求的亲手点按。

**改用以下做法：** 后台工具只做读取，以及须经用户确认的写入。把编辑草稿的工具设为 `background: false`，OctoSense 的 Agent 内核就会在用户不在应用中时拒绝它们：`may only run while the person is in the app (the app did not mark it background)`。

## 以示例为起点创建自己的应用

不要原样提交副本。准入检查会对照签名目录核对 ID 和版本，而这些 ID 属于 `ymote`。用 [QUICKSTART](../../docs/QUICKSTART.zh-CN.md) 中构建的 `hub` 检查一份未改动的 GitHub Notes 副本：

```console
$ hub check bundle --allow-unsigned --catalog <App Hub checkout>/catalog.json
org.octosense.samples.githubnotes 0.1.1 — REFUSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  [refused] version: version 0.1.1 of org.octosense.samples.githubnotes is already published; publish a new version
  [refused] continuity: org.octosense.samples.githubnotes is already published by "ymote"; an update must carry that key
  grants: capabilities {"auth", "github", "storage"}, hosts {}, storage 4194304 bytes, agent read-only
hub: the bundle was refused
```

换一个版本号也无济于事：`continuity` 仍要求 `ymote` 的密钥。请给副本一个自己的 ID。

1. 在本仓库根目录，把应用的 `bundle/` 复制到新应用的目录。Inbox Assistant 还需要复制 `src/` 和 `build_bundle.py`。

   ```sh
   mkdir -p ~/apps/my-notes
   cp -R examples/connected-apps/github-notes/bundle ~/apps/my-notes/bundle
   cd ~/apps/my-notes
   ```

2. 在 `bundle/manifest.json` 中设置新的 `id`，例如 `com.example.mynotes`。它的最后一段会成为工具和事件的命名空间，且不能是保留名称，例如 `notes` 或 `weather`。保留名称列表见 App Hub 的 [PUBLISHING](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md#id-与保留名称)。
3. 替换所有出现旧命名空间的地方：

   | 应用 | 写有命名空间或 ID 的文件 |
   | --- | --- |
   | GitHub Notes | `tools.json`、`AGENT.md` |
   | Inbox Assistant | `tools.json`、`AGENT.md`、`skills/incoming-mail-triage/manifest.json`、`skills/incoming-mail-triage/SKILL.md`、`src/workspace.splash` 中的聊天提示，以及 `build_bundle.py` 写入 `manifest.json` 的 `inbox.new_message` 触发器 |
   | Google Calendar | `tools.json`、`AGENT.md`，以及 `main.splash` 中 `glance_source` 的 `sys.chat(app: …)` 一行、发布调用里的 `app://` 链接和 `open.app` |

4. 替换 `listing.json` 中的占位内容、图标和截图。按 [QUICKSTART](../../docs/QUICKSTART.zh-CN.md) 为你的应用重新截图。
5. 用 `hub stamp` 重新写入摘要，再对照签名目录检查：

   ```sh
   hub stamp bundle
   hub check bundle --allow-unsigned --catalog <App Hub checkout>/catalog.json
   ```

   `hub stamp` 把应用包 64 个字符的 BLAKE3 摘要写入 `integrity.bundle_blake3`，并把它打印出来。检查通过时只有未签名警告：

   ```text
   com.example.mynotes 0.1.1 — PASSED
     [warning] publisher-signature: unsigned: accountability rests on the hub alone
     grants: capabilities {"auth", "github", "storage"}, hosts {}, storage 4194304 bytes, agent read-only
   ```

   如果失败：

   | 拒绝原因 | 修复方法 |
   | --- | --- |
   | `tools: tool "githubnotes.repositories" is outside the app's namespace "mynotes"` | 把工具改到新的命名空间（第 3 步）。 |
   | `identity: app id "com.example.notes" ends in "notes", which is reserved` | 把 ID 的最后一段换成非保留名称（第 2 步）。 |
   | `version` 或 `continuity` | 换一个尚未发布的 ID（第 2 步）。 |

## 参考应用是如何提交的

每个已发布的仓库都是一份可以照着做的完整提交。仓库包含 `bundle/`（准入检查只读取这个目录），以及含公钥的 `publisher.json`、`PRIVACY.md` 和 `review/`。支持链接指向仓库的 issue 页面；GitHub Notes 还附带 `SUPPORT.md`。在 `review/` 中，`GATE.json` 是对已签名应用包运行 `hub check` 的报告，`ANSWERS.md` 是对 `hub scan` 问题的回答。每个版本都有自己的标签（`v0.1.0`、`v0.1.1`）和 GitHub release，冻结了该版本的字节。

从仓库结构到提交 issue 的每一步，见[提交指南](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md#三个参考应用)。每条准入规则以 App Hub 的 [PUBLISHING](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md) 为准。

## 开发证据

这里的记录描述的是 0.1.0 发布之前的开发副本。每份记录描述的都是运行当时的代码，而不是当前代码，且全部使用模拟提供商。

| 应用 | 记录 | 覆盖内容 |
| --- | --- | --- |
| GitHub Notes | [VALIDATION.md](github-notes/VALIDATION.md) | Rinx 编辑器布局、宿主授权和账户选择、签名安装后的完整流程 |
| Inbox Assistant | [evidence/README.md](inbox/evidence/README.md) | 测试数据检查、使用真实模型的集成运行、macOS 持续测试 |
| Google Calendar | [ACCEPTANCE.md](google-calendar/ACCEPTANCE.md) | 测试数据检查、安装后的流程、速览卡片路由、建议式聊天、macOS 持续测试 |
| 三个应用 | [signed-install-5c7a13f9.json](evidence/signed-install-5c7a13f9.json) | 签名安装和重新打开，以及拒绝遭篡改的签名目录、源码和暂存目录 |

**未验证：** 真实 OAuth 和提供商写入（OctoSense 记录的两次 macOS 检查除外，见 [CAPABILITIES § 限制](../../docs/CAPABILITIES.zh-CN.md#限制)）、Gmail 送达、在真机上亲手点按批准发送或保存、Android 后台行为，以及 Windows 和 Linux。App Hub 的 [0.1.1 准入记录](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/admissions/connected-apps-0.1.1/README.zh-CN.md)验证了签名商店安装、从 0.1.0 升级和 Agent 文件加载，没有验证原生界面、真实提供商或亲手点按批准。

## 数据规则

- 所有测试数据、截图和记录的邮件都必须是虚构的。
- 不要提交提供商令牌、OAuth 客户端 ID 或密钥、导出的邮件或日历数据、私有仓库内容、真实账户截图或 `.local-state/`。
- Agent 授权和提供商登录是两回事。允许应用 Agent 后，配置的模型就能读取 Agent 工具返回的内容。
- 模型不能批准受保护的写入。宿主确认面板展示已保存的内容，只有用户能批准。
