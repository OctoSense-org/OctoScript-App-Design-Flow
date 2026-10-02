# 应用中的 AI：OctoSense 的助手

[English](AI-SERVICES.md) | 简体中文

用本仓库开发的脚本应用如何使用 OctoSense 内部的助手（Shell 运行的 octos Agent 内核）、
目前哪些可用、哪些还在规划中。本文描述 2026-10-01 的状态：App Hub `main` 为 `41bc959`，
OctoSense `main` 为 `f52620c`（它锁定 App Hub `58c3c8ae`、octos `ae230ce0`、Octoscript
`5991dfae` 和 Octoscript-Makepad `8f103d0c`）。自本文初稿（2026-09-27）以来，
Shell 增加了 `model` 服务、在首次使用征得同意后向隔离应用提供的 `octos` 服务、面向所有获得
授权的应用的 `glance`，以及为每个声明了 Agent 的应用提供的 Agent（一个 peer 和一个
“Ask <app>”面板）。自 2026-09-30 起，Shell 还为这个 Agent 提供 `ask_user_question` 和读取
它自己文件夹的工具，按账户各保留一个 Agent，在应用被卸载时清除它，允许用户在 L0 卡片内与它
对话（`sys.chat`，模型写的文字标为 AI 撰写），并让系统应用的 Agent 通过自己的工具把卡片放到
glance 屏幕上（Mail、Calendar）。Shell 一侧的说明见 OctoSense 的
[`docs/ai-services.zh-CN.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.zh-CN.md)、
[`docs/architecture.zh-CN.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/architecture.zh-CN.md)
和 [ADR 0004](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0004-native-apps-hosting-and-peers.md)。

后面几节介绍正在其上构建的内容：在应用包中声明应用自己的 Agent、它提供的工具、系统工具箱、
发布到 glance 屏幕、`sys.digest` 卡片、AI 撰写的文字与卡片内对话，以及 News 的端到端流程。那里的每项功能都标为
**可用**（已合入所列仓库的 `main`，可按描述使用）或**即将推出**（在所列的未合并 PR 中，
或只存在于 ADR 中：展示的形状在合入前可能变化，暂时不要让提交依赖它）。标为 **✓ 已运行**
的命令在 2026-09-27 为本文实际运行过（macOS，Apple silicon）；其他命令均引自所列来源，并
标明未运行。2026-09-30 的更新引自所列 PR 和代码，未运行。2026-10-01 的更新是在上述版本的
代码中读到的；标为 **✓ 2026-10-01 已运行** 的 `hub check` 输出来自按 App Hub `main` `41bc959`
（`app-contract`、`app-policy` 和 `app-hub` 三个 crate）构建的 `hub`；本文没有任何内容是在
OctoSense Shell 中运行的。

> **开发应用不需要任何 AI。** 本仓库中没有任何东西会调用模型或需要 API key，你可以使用
> 任何编程 Agent（Codex、Claude Code、Cursor、Gemini CLI、GitHub Copilot 等），也可以
> 不用。本文只讨论你*完成后的应用*在设备上可以请求的助手。

面向 Shell 和原生模块开发者的详细版本：
[OctoSense `docs/ai-services.zh-CN.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.zh-CN.md)。

## 目录

- [简短回答](#简短回答)
- [助手的构成](#助手的构成)
- [系统 Agent 与应用 Agent](#系统-agent-与应用-agent)
- [助手相关权限](#助手相关权限)
- [最小调用示例与“不可用”状态](#最小调用示例与不可用状态)
- [用户看到什么](#用户看到什么)
- [错误](#错误)
- [测试](#测试)
- [一次性模型调用（`model`）](#一次性模型调用model)
- [状态一览](#状态一览)
- [应用自己的 Agent](#应用自己的-agent)
- [应用的工具与 peer 工具](#应用的工具与-peer-工具)
- [系统工具箱](#系统工具箱)
- [发布到 glance 屏幕](#发布到-glance-屏幕)
- [绑定到结果的卡片：`sys.digest`](#绑定到结果的卡片sysdigest)
- [AI 撰写的文字与卡片内对话：`model-copy`、`sys.chat`](#ai-撰写的文字与卡片内对话model-copysyschat)
- [卡片级别与渲染评审](#卡片级别与渲染评审)
- [端到端示例：News](#端到端示例news)
- [不接真实提供方的测试](#不接真实提供方的测试)
- [来源](#来源)

## 简短回答

**在 OctoSense 设备上，商店应用可以进行一次性模型调用（`model`），并在用户允许其 Agent
后与助手对话（`octos.*`）。** `tools/octo run` 使用的 App Hub `card-host` 不提供任何宿主
服务，所以在那里两者都返回 `no service answers "…" on this device`。无论如何都请把应用做成
不依赖 AI 也完整可用：用户可能拒绝，设备也可能没有内核（iOS）或没有提供方。

| 你尝试 | 目前的结果 |
| --- | --- |
| 声明 `octos.turn.start`（及同组权限）并调用 | 准入检查接受这些名称。在 `card-host` 中调用返回 `no service answers "octos" on this device`（已验证，见下文）。在托管内核的 OctoSense Shell 中，第一次调用会等待用户允许该应用的 Agent（`Waiting for the person to allow this app's agent (OctoSense asks the first time)`）；之后应用与自己的 peer 对话（[OctoSense#106](https://github.com/OctoSense-org/OctoSense/pull/106)、[#120](https://github.com/OctoSense-org/OctoSense/pull/120)、[#184](https://github.com/OctoSense-org/OctoSense/pull/184)）。 |
| 声明 `model` 并调用 `model.complete` | 准入检查接受它（App Hub [#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24)），OctoSense Shell 也提供它（[OctoSense#95](https://github.com/OctoSense-org/OctoSense/pull/95)，已合并）：一次性、按 schema 校验的调用，由用户自己的 AI 提供方回答。`card-host` 返回 `no service answers "model" on this device`。见[一次性模型调用](#一次性模型调用model)。 |
| 声明 `llm` | 准入检查接受它，但 `llm` 服务用于管理设备的 AI 提供方（没有发送提示词的方法），并且只响应 `os.*` 系统应用：`llm is for OctoSense's own apps.`。不要申请它。 |
| 在 `manifest.json` 中声明 `agent` | 准入检查接受并按上限裁剪。用户允许后，Shell 为应用分配自己的 peer，用户可以在 Shell 的“Ask <app>”面板中与它对话（[OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)），系统 Agent 也可以把任务交给它。它的 Agent 可以保留内核的 `ask_user_question`（[OctoSense#190](https://github.com/OctoSense-org/OctoSense/pull/190)），并能读取自己的账户文件夹（[#205](https://github.com/OctoSense-org/OctoSense/pull/205)、[#249](https://github.com/OctoSense-org/OctoSense/pull/249)）。根据 `needs` 选择模型、触发器和后台运行仍**即将推出**（见[应用自己的 Agent](#应用自己的-agent)）。 |
| 附带 `tools.json`、`AGENT.md`、`skills/` | 准入检查接受。Shell 把应用包中的工具注册到应用的 peer，并转发对它们的调用（[OctoSense#145](https://github.com/OctoSense-org/OctoSense/pull/145)、[#184](https://github.com/OctoSense-org/OctoSense/pull/184)），但调用只会在应用命名空间对应的宿主服务上运行，所以目前只有系统应用的工具能运行（News、Mail、Calendar）；商店应用的工具会返回错误（见[应用的 Agent 目前得到什么](#应用的-agent-目前得到什么)）。`AGENT.md` 和技能还不会装进 peer。 |
| 调用 `glance.publish` | 任何被授予 `glance` 权限的隔离应用都会得到响应（[OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)）：一张 L0 卡片，或一张可交互的 Splash 卡片，可选同时发出通知（见[发布到 glance 屏幕](#发布到-glance-屏幕)）。 |
| 在 L0 卡片中使用 `sys.chat` 或 `model-copy` 文字 | OctoSense Shell 会用发布应用的 Agent 回答其 glance 卡片中的 `sys.chat`，并把模型写的文字标为 AI 撰写后绘制（[OctoSense#263](https://github.com/OctoSense-org/OctoSense/pull/263)、[OctoScript#53](https://github.com/OctoSense-org/OctoScript/pull/53)）。本仓库锁定的运行时早于这两者，所以这里 `card-host` 和 `card-studio` 使用的 L0 检查器不认识它们（读自 [`native-runtime.lock.json`](../native-runtime.lock.json)，未运行）（见[AI 撰写的文字与卡片内对话](#ai-撰写的文字与卡片内对话model-copysyschat)）。 |
| 把模型提供方的 API key 放进应用包 | 绝不允许。应用中不得有密钥、token 或密码（[AGENTS.md](../AGENTS.md#rules-for-every-app)）。 |

应用在 `net` 下声明的普通 HTTPS API 只是一次网络请求，即使背后运行着模型也是如此。
常规规则照样适用：应用包中没有密钥或 token，主机已列出，隐私说明写明哪些数据会离开设备。
它不是设备的助手，也不使用用户配置的任何 AI 提供方。

## 助手的构成

- **每个 Shell 一个 octos 内核。** OctoSense 桌面端和 Home（手机 Shell）各运行一个内核，
  首次使用时启动。Android 把它打包在 APK 中，OpenHarmony 在进程内运行，桌面端运行
  `OCTOS_APP_CORE_BIN` 指定的二进制，iOS 没有内核。
- **AI providers**（一个系统应用）是用户选择模型、输入密钥的地方，密钥只在宿主自有的面板
  上输入。密钥保存在平台的密钥存储中，任何应用都看不到。
- **应用 peer。** 获得助手授权的应用会为它保存的每个账户得到一个自己的 octos peer（除非
  manifest 写明 `storage.accounts: true`，否则只有一个 `device` 账户）：私有的会话上下文、
  工作区（该账户的文件夹，`apps/<app>/accounts/<account>/`）和记忆
  （`app/<app>/acct-<hash>`），归 Shell 的系统 Agent 所有（`crates/app-peers`）。应用拿到的
  是一个受限的服务，永远拿不到内核、提供方或密钥。
- **审批属于用户，并且在发起请求的应用中进行。** 系统 Agent 从不替应用审批。

Shell 的宿主策略授权的**原生模块**会得到 peer（随附的策略授权的是 Matrix 客户端 Rinx：
OctoSense `crates/ai-host/src/lib.rs` 中的 `Policy::shipped()`），Rinx 的迷你应用宿主再把
`octos.*` 这些名称提供给用户导入 Rinx 的迷你应用。**隔离运行的脚本应用**也会得到自己的
peer（`card.<app id>`），通过 Shell 的 `octos` 宿主服务
（[OctoSense#106](https://github.com/OctoSense-org/OctoSense/pull/106)），前提是用户在首次使用时允许它的 Agent
（[#120](https://github.com/OctoSense-org/OctoSense/pull/120)、[#184](https://github.com/OctoSense-org/OctoSense/pull/184)）。`OCTOSENSE_CONTAINED_APPS=1` 对所有应用跳过这个询问
（开发者用的覆盖开关），`0` 则关闭它。

## 系统 Agent 与应用 Agent

OctoSense `main` 的做法，读自 `crates/shell/src/agents.rs`、`crates/ai-host/src/contained.rs`、
`crates/shell/src/questions/` 和 `crates/app-peers`（ADR 0004 §4、§6）。本文未运行。

- **哪些应用有 Agent。** manifest 中声明了 `agent` 块或任意 `octos.*` 名称、或者应用包附带
  `tools.json` 的脚本应用；以及 Shell 条目授予了 `octos.*` 的原生应用（Rinx）。Settings ›
  Assistant 列出每一个，并可以关闭它。2026-10-01 时，系统应用 News、Mail 和 Calendar 都有
  Agent；它们都没有声明 `octos.*` 名称，所以由 Shell 驱动它们的 Agent，应用本身从不调用
  `host.request("octos…")`。
- **首次使用。** 用户在首次使用的确认页上允许应用的 Agent。这个确认页可以由应用自己的第一次
  `octos.*` 调用、它的“Ask <app>”面板（桌面端栏上的“Ask <app>”或 Shift+F8），或者系统
  Agent 的 `agents.ask` 引出。此后 Shell 会在启动时准备好这个 peer 并注册它的工具，无论应用
  是否打开。脚本应用的 peer 是 `card.<app id>`（例如 `card.os.mail`），永远不会是原生模块的
  peer。
- **系统 Agent** 是 Shell 自己的会话（`_main:api:octosense#system`），用户在系统对话（助手
  窗格：Dock 上的 Assistant 图标、桌面端的 F8、手机主屏上的磁贴）中与它交谈。它用
  `peer_list` 看到每个已准备好的应用 peer，用 `peer_send_input` 把任务交给其中一个，用
  `peer_gather` 读取对方写下的结果，并通过 `agents.list` / `agents.ask` 向 Shell 询问那些
  用户尚未允许其 Agent 的应用。它不持有任何应用的工具，从不替应用审批，也不能关闭应用的 peer。
- **每个应用 Agent 有两条通道。** 系统 Agent 的请求走一条通道，用户的请求走另一条，两者并行
  并共享历史；用户可以不经过系统 Agent，直接与应用的 Agent 对话
  （见[下文](#用户直接与应用的-agent-对话)）。
- **提问。** 保留了 `ask_user_question` 的 Agent 可以向用户提问。由用户或应用发起的回合中的
  问题显示在应用的对话里；由系统 Agent 发起的回合中的问题转到系统对话。10 分钟内无人回答
  就会被拒绝。
- **示例**（OctoSense#267 实际运行的形状，在那里用真实模型运行；本文未运行）：用户请系统
  Agent 放一张日历卡片；系统 Agent 用 `peer_send_input` 把请求交给 Calendar 的 Agent（如果
  用户还没有允许，会先出现 Calendar 的首次使用确认页）；Calendar 的 Agent 调用自己的一个工具
  （`calendar.notify`、`calendar.agenda`），它的宿主服务填好随服务附带的固定 L0 卡片，并以
  Calendar 的身份发布到 glance 屏幕。模型从不编写卡片代码。
- **生命周期。** peer 在多次启动之间保留记忆。退出某个账户会暂停该账户的 Agent；删除账户或
  卸载应用会清除它（octos `peer/purge`，
  [OctoSense#248](https://github.com/OctoSense-org/OctoSense/pull/248)），所以重新安装后是一个
  新的 Agent。

### 用户直接与应用的 Agent 对话

应用的 Agent 不只能通过系统 Agent 联系到：用户也可以直接与它对话，有三个地方，都属于同一个对话
中的**用户通道**。在用户于首次使用确认页上允许该应用的 Agent 之前，什么都不会运行。读自 OctoSense
`f52620c` 的 `crates/shell/src/app_chat/mod.rs`、`crates/shell/src/glance_chat.rs` 和
`crates/ai-host/src/contained.rs`；本文未运行。

| 在哪里 | 用户怎么做 | 应用作者要写什么 |
| --- | --- | --- |
| Shell 的 **“Ask <app>”面板** | 在桌面端从栏上的“Ask <app>”按钮、Shift+F8，或 Setup › Assistant › “Ask this app's agent”，为当前焦点应用的 Agent 打开它。它位于系统对话的右侧。发送的是用户自己的回合，与系统 Agent 的通道并行运行；面板的 Stop 只停止用户的回合，另有一行“Stop the system agent's task”停止另一条通道的回合。应用的 Agent 在用户通道中提出的问题在这里回答。 | 什么都不用写：Shell 为**每个**有 Agent 的应用绘制这个面板，无论应用自己有没有对话界面。 |
| glance 屏幕上的**卡片内对话** | 在应用发布的卡片中输入；应用自己的 Agent 在卡片中回答。 | 一张带 `sys.chat` 和 `ChatEntry` 的 L0 卡片，用 `glance` 发布（见[下文](#ai-撰写的文字与卡片内对话model-copysyschat)）。 |
| **应用自己的界面** | 使用应用绘制的对话或“提问”控件。 | 在 `octos` 服务上调用 `host.request("octos.session.open" / "octos.turn.start" / "octos.session.history" / "octos.turn.interrupt", …)`，并在 `capabilities` 中列出这些名称（见[最小调用示例](#最小调用示例与不可用状态)）。 |

- **一个对话，两条通道。** 系统 Agent 的通道是 peer 自己的会话（`_main:api:octosense#peer-…`）；
  用户的通道是一个以共享历史方式打开的请求上下文（`…#peerctx-…`）。每条通道都能只读地看到另一条
  通道最近的消息。回合按发言者标注，事件和 `octos.session.history` 的每一行都带有 `lane`
  （`person` 或 `system_agent`）和 `speaker`。
- 来自面板或系统对话的回合是用户本人的（`TurnTrigger::Person`）；应用用 `octos.turn.start`
  发起的回合，或卡片中的对话，会被标为用户的，但在审批规则中算作应用自己的运行
  （见[上文](#助手相关权限)）。
- **Shell 审批界面上的 Stop**（某个应用 Agent 的待审批事项和问题下方的按钮，
  `approvals::stop_agent`）会拒绝该 Agent 正在等待的事项，并停止它在**两条**通道中正在运行的
  回合：设备归用户所有。
- **在手机上**，这个面板被构建成全屏的面板，但在 `main` 上没有任何触控入口能打开它（手机的
  Assistant 磁贴打开的是系统对话）；未在设备上运行。应用自己的界面和它的 glance 卡片在手机上与
  桌面端一样可用。
- 原生模块和进程应用通过各自的通道（注入服务上的 `open_conversation`，或 peer link）到达同一条
  用户通道；脚本应用使用上面的 `octos.*` 名称。

## 助手相关权限

四个精确名称，每个都是单独的授权（App Hub `crates/app-contract/src/manifest.rs` 中的
`KNOWN_CAPABILITIES`；名称及其商店文字在 `crates/app-policy/src/services.rs`）。前缀不授予任何权限：`octos.` 或 `octos.admin`
会被准入检查拒绝。

| 权限 | 调用 | 参数 | 返回（`r.data`） | 商店显示 |
| --- | --- | --- | --- | --- |
| `octos.session.open` | `octos.session.open` | `{}` | `{open: true, model: {lane, provider, model} 或 nil}` | Open its own conversation with the assistant |
| `octos.session.history` | `octos.session.history` | `{}` | 会话内容，`{session_id, messages: [...], …}`：两条通道按时间合并，每条消息带有它的 `lane` 和发言者 | Read its own conversations with the assistant |
| `octos.turn.start` | `octos.turn.start` | `{text}`（1 字节到 32 KiB） | 回合结束后的 `{turn_id, text}`，即回复 | Ask the assistant to work for it, using the device's AI settings |
| `octos.turn.interrupt` | `octos.turn.interrupt` | `{}` | 停止正在运行的回合 | Stop assistant work it started |

参数和返回的形状取自提供这些名称的两个宿主，它们都基于 OctoSense 的 `crates/app-peers`：
OctoSense Shell 面向隔离应用的 `octos` 服务（`crates/ai-host/src/contained.rs`）和 Rinx 的
迷你应用宿主（[hagency-org/Rinx](https://github.com/hagency-org/Rinx) 中的
`src/host/octos.rs`）。其他参数会被拒绝（`Unsupported Octos arguments`）：应用只提供文本
（在 OctoSense Shell 中还可以提供 `trigger`，取 `person`、`app` 或 `incoming` 之一，以及
`from`，说明是什么发起了这个回合），从不提供会话、配置、提供方、模型或审批决定。每个应用实例
同一时间只运行一个回合，一个回合 180 秒后放弃。脚本应用收不到推送的事件：它用
`octos.session.history` 读取对话，其中也包括系统 Agent 的回合。

应用传来的 `trigger: "person"` 会在对话记录中把这个回合标为用户的，但审批规则把它当作应用自己
发起的运行：“当我发起时”这类常设规则永远不会替它批准。只有 Shell 自己的输入框（“Ask <app>”
面板、系统对话）才能证明是用户本人
（[OctoSense#215](https://github.com/OctoSense-org/OctoSense/pull/215)）。

## 最小调用示例与“不可用”状态

`manifest.json`（只申请界面用得到的）：

```json
"capabilities": ["octos.session.open", "octos.turn.start"]
```

`main.splash`：

```splash
fn ask(){
    ui.answer.set_text("Waiting for the assistant…")
    host.request("octos.session.open", {}, fn(s){
        if !s.is_ok {
            ui.answer.set_text("Assistant unavailable: " + s.error)
            return
        }
        host.request("octos.turn.start", {text: ui.prompt.text()}, fn(r){
            if r.is_ok { ui.answer.set_text(r.data.text) }
            else { ui.answer.set_text("Assistant unavailable: " + r.error) }
        })
    })
}
```

界面主体中包含 `prompt := TextInput{…}`、`answer := Label{…}` 和
`Button{text: "Ask the assistant" on_click: || ask()}`。

- `host.has("octos.turn.start")` 只说明权限是否**已授予**，不说明是否有服务响应。一定要
  处理 `r.is_ok == false`。
- 把“不可用”当作正常状态：设备上没有内核（iOS、没有内核的桌面端）、没有配置提供方、
  未授权、未登录。用一句话说明，并让其他界面照常工作。
- 永远不要向用户索要密钥或提供方。那属于宿主的 AI providers 应用。

2026-09-27 用 `tools/octo run … --hidden` 验证（App Hub `362d832`，运行时 `65d30a09`），
通过远程控制桥点击按钮：

| Manifest | 读到的标签文字 |
| --- | --- |
| `["octos.session.open", "octos.turn.start"]` | `Assistant unavailable: no service answers "octos" on this device` |
| `["storage"]` | `Assistant unavailable: this app was not granted "octos", which "octos.session.open" needs` |

托管内核的 OctoSense Shell 的回答不同：第一次调用会请用户允许该应用的 Agent，之后应用与
自己的 peer 对话（[OctoSense#106](https://github.com/OctoSense-org/OctoSense/pull/106)、[#184](https://github.com/OctoSense-org/OctoSense/pull/184)；本文未运行）。各种拒绝的文字见
[错误](#错误)。

**现在应该发布这个功能吗？** 只有在应用不依赖它也完整可用时才可以：用户可能拒绝，设备
可能没有内核或提供方，而 `tools/octo run` 永远不会响应。审核者会问界面上用不到的授权
（`hub scan`），每个 `octos.*` 都会出现在商店的权限列表中。

## 用户看到什么

- **安装前**：每个权限一行说明（见上表），隐私摘要中写着 "Asks the device's assistant
  to work for it; the assistant's keys stay with the device."（申请 `octos.turn.start`
  时），或 "Opens or reads its own conversations with the device's assistant, but
  cannot ask it to work."（只申请 open 或 history 时）。
- **密钥和提供方**只在 AI providers 中、在宿主面板上设置：桌面端为 Start → Settings →
  AI providers，手机上为 OctoSense Settings → Accounts → AI providers。
- 助手发起的**工具审批**交给用户，在发起请求的应用中、用宿主自己的控件进行（OctoSense
  Shell 使用它们的审批面板，[OctoSense#120](https://github.com/OctoSense-org/OctoSense/pull/120) 和 [#145](https://github.com/OctoSense-org/OctoSense/pull/145)；Rinx 为它的迷你
  应用使用自己的控件）；系统 Agent 从不回答审批。脚本应用无法审批任何东西：没有任何参数能
  携带审批决定。审批面板会完整显示每个参数（隐藏字符和控制字符显示为码位，命令每行一条），
  在用户把所有参数都滚动看过之前，“Approve”按钮保持禁用
  （[OctoSense#218](https://github.com/OctoSense-org/OctoSense/pull/218)）。
- 应用 Agent 的**首次使用确认页**，列出它能读什么（"Its own memory"，或在
  `storage.agent_workspace: "none"` 时为 "No files: only what its tools return"）、能用什么
  （保留了 `ask_user_question` 的 Agent 显示 "Ask you questions"）以及模型在哪里运行
  （`crates/shell/src/approvals/consent.rs`）。Settings › Assistant 可以再次关闭它。

## 错误

| `r.error` | 含义 | 应用该怎么做 |
| --- | --- | --- |
| `this app was not granted "octos", which "<service>" needs` | manifest 中没有列出这个精确名称 | 把它加入 `capabilities`，或删除该调用 |
| `no service answers "octos" on this device` | 当前宿主不向应用提供助手（`card-host`，或没有内核的 Shell 构建） | 显示“不可用”，继续工作 |
| `Waiting for the person to allow this app's agent (OctoSense asks the first time)` | 用户还没有允许该应用的 Agent；Shell 正在询问 | 显示出来；用户的回答决定下一次调用的结果 |
| `The assistant is turned off for apps on this device` | 设备为应用关闭了助手（`OCTOSENSE_CONTAINED_APPS=0`） | 显示“不可用”，继续工作 |
| `The assistant is not available on this device` | Shell 无法启动该应用的 peer | 同上 |
| `Add an account in the app before using its assistant` | 应用按账户保存数据（`storage.accounts: true`），但还没有任何账户 | 提供应用自己的添加账户入口 |
| `This app's manifest does not declare that assistant service` | 隔离环境之后 Shell 自己的检查：manifest 没有列出任何 `octos.*` 名称，或没有列出这一个 | 声明它，或删除该调用 |
| `no service answers "model" on this device` | 当前宿主没有 `model` 服务（`card-host`） | 同上 |
| `model.complete` 返回的 `<code>: <sentence>`，`<code>` 为 `capability`、`no_provider`、`rate`、`budget`、`bad_request`、`invalid_output`、`too_large`、`provider` 之一 | `model` 服务拒绝了这次调用（[详情](#model-服务)） | 显示这句话；让应用不依赖模型也能使用 |
| `Unsupported Octos arguments` | 传了 `text` 以外的参数（turn start），或给其他调用传了任何参数 | 只传 `{text}` 或 `{}` |
| `Provide text (at most 32 KiB)` | 提示词为空或过长 | 发送前检查 |
| `This app already has an assistant turn running` | 同一时间只能有一个回合 | 等待期间禁用按钮，或先中断 |
| `No assistant turn is running` | 没有正在运行的回合时调用了 `octos.turn.interrupt` | 无需处理 |
| 其他（未配置提供方、提供方出错、配额、未登录、授权被撤销） | 宿主原样传回的文字 | 显示出来；不要循环重试 |

没有按应用的配额 API。预算由宿主管理（见下文规划）。

## 测试

- **在本仓库的工具中：** `tools/octo run <bundle> --hidden --port 8141`，通过远程控制桥
  点击按钮，用 `/snap` 读取标签。预期得到 `no service answers` 状态；把它截图作为应用的
  “不可用”状态。
- **在 OctoSense 桌面端：** 按商店路径演练
  （[PUBLISHING §4](PUBLISHING.md#4-rehearse-the-store-path-locally)）。要让 Shell 拥有
  内核和提供方，见 OctoSense
  [`docs/ai-services.zh-CN.md` § 本地运行与测试](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.zh-CN.md#本地运行与测试)。
  在那里，应用的第一次 `octos.*` 调用会请用户允许它的 Agent。
- **Rinx 的迷你应用宿主**也会响应 `octos.*`，适用于用户审核后导入 Rinx 的应用包
  （需要登录 Matrix，使用 Rinx 自己的助手 peer）：
  [Rinx `examples/miniapps`](https://github.com/hagency-org/Rinx/tree/main/examples/miniapps)。
  这不是 App Hub 的安装路径，并且它会拒绝声明了 `agent` 的应用包。本文未重新运行这一路径。

## 一次性模型调用（`model`）

App Hub `main` 接受第二条更窄的路径
（[App-Hub#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24)，已合并）：
`model` 权限，由 OctoSense Shell 的 `model` 宿主服务提供
（[OctoSense#95](https://github.com/OctoSense-org/OctoSense/pull/95)，2026-09-28 合并）：

- `host.request("model.complete", {task, input, schema, class}, fn(r){…})`，`class`
  为 `fast` 或 `strong`。宿主从用户自己的 AI 提供方中挑选模型；应用永远看不到提供方、
  模型 id 或密钥。
- 一次性：没有工具、没有记忆，除 `input` 外没有历史。回复必须符合应用的 JSON Schema
  （有大小上限）；除非应用明确要求，回复中的 URL 会被拒绝。每个应用有每日的调用次数和
  token 预算，由宿主管理。
- 商店显示 "Send what you give it to the AI provider you configured, within a daily
  budget"；隐私摘要显示 "Sends what you give it to the AI provider you configured, for
  one-off answers within a daily budget; it never sees your API keys."

准入检查会通过（`grants: capabilities {"model"}`），Shell 锁定的 App Hub 也认识这个名称。
`card-host` 没有 `model` 服务：在那里调用返回 `no service answers "model" on this device`
（在 App Hub `e8601b8` 的 `card-host` 中运行）。

### `model` 服务

服务（`apps/ai-providers/host-service/src/complete/`，crate `octosense-llm-service`，
由 `crates/ai-host` 与 `llm` 一起注册；[OctoSense#95](https://github.com/OctoSense-org/OctoSense/pull/95)）的形状如下。#95 同时给
ADR 0002 增加了 §14“直接的一次性模型调用”，并明确：凡是需要工具、研究、记忆或审批的事情，主路径仍是应用自己的 Agent
（见下文）。

| 方法 | 参数 | 返回（`r.data`） |
| --- | --- | --- |
| `model.complete` | `{task, input, schema, class?, allow_urls?}` | `{output, meta: {class, requested, attempts, usage: {input_tokens, output_tokens, estimated}, budget}}` |
| `model.budget` | – | 只返回调用者的 `budget` |

- **`task`**（最多 4 KiB）用文字说明要做什么；**`input`**（任意 JSON，最多 32 KiB）是要
  处理的内容，作为数据发送，并告诉模型不要执行其中的任何指令。
- **`class`**：`"fast"`（默认）或 `"strong"`。宿主按用户自己的顺序尝试提供方，同类型的
  优先，某个提供方失败就跳到下一个。`meta.class` 说明实际用的是哪一类。应用永远看不到
  提供方、模型 id 或密钥。
- **`schema` 必填**（受限的 JSON Schema 子集，最多 8 KiB）；`output` 一定符合它。回复
  不是 JSON、不符合 schema、含有 URL 或超过 16 KiB 时重试一次，再失败就拒绝。
- **默认不允许 URL**：回复中出现 `http://`、`https://` 或 `www.` 就会被拒绝，因为回复
  最终会成为卡片数据。只有应用要从输入中提取链接时才传 `allow_urls: true`。
- **按应用计算的预算**，由宿主保存在应用的隔离目录之外：默认每分钟 6 次，每个 UTC 日
  100 次调用和 100,000 个 token。`meta.budget` 和 `model.budget` 返回
  `{calls_today, calls_per_day, tokens_today, tokens_per_day, tokens_left, per_minute, resets_at}`。
- **拒绝**的格式为 `"<code>: <sentence>"`，`code` 为 `capability`、`no_provider`、
  `rate`、`budget`、`bad_request`、`invalid_output`、`too_large` 或 `provider` 之一。
  这句话可以直接显示给用户。
- 服务在 Card runner 的准入检查之后，还会再检查应用自己的 manifest 中是否有 `model`。

一次调用（本文未运行；字面量写法参照 Photos
应用包，列表和映射用空格分隔）：

```splash
host.request("model.complete", {
    task: "Give the note a short title and up to three tags."
    input: {note: note_text}
    schema: {type: "object" required: ["title" "tags"] additionalProperties: false
             properties: {title: {type: "string" maxLength: 40}
                          tags: {type: "array" maxItems: 3 items: {type: "string"}}}}
    class: "fast"
}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) return }   // "budget: …", "no_provider: …"
    show_title(r.data.output.title)
})
```

## 状态一览

截至 2026 年 10 月 1 日。**可用**表示已合入所列仓库的 `main`；**即将推出**表示在所列的
未合并 PR 中，或只存在于 ADR 中。

| 功能 | 状态 | PR 与源码 |
| --- | --- | --- |
| 应用只能通过宿主服务和 app-peer 代理使用 AI，永远接触不到内核、提供方或密钥 | **可用**（规则） | OctoSense [`AGENTS.md`](https://github.com/OctoSense-org/OctoSense/blob/main/AGENTS.md) 第 3、4 条，[`crates/app-peers`](https://github.com/OctoSense-org/OctoSense/tree/main/crates/app-peers) |
| 宿主策略授权的原生模块（Rinx）使用 `octos.*`，以及通过 Rinx 的迷你应用宿主、供导入 Rinx 的应用包使用 | **可用** | OctoSense `crates/ai-host`（`Policy::shipped()`）；[Rinx](https://github.com/hagency-org/Rinx) `src/host/octos.rs` |
| OctoSense 中隔离运行的脚本应用使用 `octos.*` | 在托管内核的 Shell 中（iOS 除外）**可用**，前提是用户在首次使用时允许该应用的 Agent | OctoSense [#106](https://github.com/OctoSense-org/OctoSense/pull/106)、[#120](https://github.com/OctoSense-org/OctoSense/pull/120)、[#184](https://github.com/OctoSense-org/OctoSense/pull/184) |
| `llm`：用户的 AI 提供方、遮盖后的密钥状态、宿主面板 | **可用**，仅限系统应用（`os.*`）；没有发送提示词的方法 | OctoSense [`apps/ai-providers/host-service`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/ai-providers/host-service) |
| `model.complete`：一次性、按 schema 校验的模型调用 | **可用**：权限（[App-Hub#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24)）和服务（[OctoSense#95](https://github.com/OctoSense-org/OctoSense/pull/95)），都在 Shell 的 App Hub 锁定版本中 | [上文](#一次性模型调用model) |
| 应用包中声明应用自己的 Agent：`agent`（profile、模型需求、触发器、技能）、`tools.json`、`AGENT.md`、`skills/` | 在 App Hub 准入检查（[App-Hub#18](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/18)）和 Shell 中**可用**：用户允许后分配 peer、提供“Ask <app>”面板，系统 Agent 也能用 `peer_send_input` 把任务交给它（[OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)）；`AGENT.md` 和技能还不会装进 peer | [应用自己的 Agent](#应用自己的-agent) |
| 应用 Agent 使用内核的 `ask_user_question`（`agent.tools: ["ask_user_question"]`，隔离应用的 Agent 唯一能保留的内核工具） | **可用**（[App-Hub#37](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/37)、[OctoSense#190](https://github.com/OctoSense-org/OctoSense/pull/190)） | [应用的 Agent 目前得到什么](#应用的-agent-目前得到什么) |
| 应用 peer 上的宿主读取工具：`files.list`、`files.read`、`files.search`，作用于账户文件夹；用户通道通过 `read_parent` 读取该文件夹 | 在 Unix 平台上**可用**，Windows 除外（[OctoSense#205](https://github.com/OctoSense-org/OctoSense/pull/205)、[#249](https://github.com/OctoSense-org/OctoSense/pull/249)；octos [#2647](https://github.com/octos-org/octos/pull/2647)） | OctoSense `crates/shell/src/host_tools/files.rs` |
| 每个账户一个 Agent（`storage.accounts`），删除账户或应用时一并清除 Agent（`peer/purge`） | **可用**（[App-Hub#44](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/44)、[OctoSense#233](https://github.com/OctoSense-org/OctoSense/pull/233)、[#248](https://github.com/OctoSense-org/OctoSense/pull/248)；octos [#2649](https://github.com/octos-org/octos/pull/2649)） | [Agent 在哪里工作](#agent-在哪里工作storage) |
| 宿主按 `needs` 和 `tier` 挑选模型；触发器和 `background` 真正触发 | **即将推出**（ADR 0002 第 2 步、M3）。Shell 目前还不读取 `agent.profile` 或 `agent.model` | [manifest 中的 `agent`](#manifest-中的-agent) |
| 应用工具注册到应用的 peer（`peer/tools/register`、`peer/tool/call`） | **可用**：内核一侧（[octos#2567](https://github.com/octos-org/octos/pull/2567)）以及 Shell 注册应用包中的工具并转发调用（[OctoSense#145](https://github.com/OctoSense-org/OctoSense/pull/145)、[#184](https://github.com/OctoSense-org/OctoSense/pull/184)）。调用只会在应用命名空间对应的宿主服务上运行，所以只有系统应用的工具能运行；`implemented_by: "app"` 的工具在 Card runner 能接手之前返回错误（**即将推出**） | [应用的工具与 peer 工具](#应用的工具与-peer-工具) |
| 系统应用的 Agent 通过自己的工具把卡片放到 glance 屏幕（`mail.notify`、`calendar.notify`、`calendar.agenda`：由宿主服务填好固定的 L0 卡片） | Mail 和 Calendar **可用**（[OctoSense#267](https://github.com/OctoSense-org/OctoSense/pull/267)）；Calendar 只在桌面端 | OctoSense `apps/mail/host-service`、`apps/calendar/host-service` |
| 在应用内与应用的 Agent 对话、运行时审批、应用记忆 | 对话在 Shell 的“Ask <app>”面板中（[OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)）和卡片中（[`sys.chat`](#ai-撰写的文字与卡片内对话model-copysyschat)）**可用**；审批在 Shell 的面板上进行（[#120](https://github.com/OctoSense-org/OctoSense/pull/120)、[#145](https://github.com/OctoSense-org/OctoSense/pull/145)、[#215](https://github.com/OctoSense-org/OctoSense/pull/215)、[#218](https://github.com/OctoSense-org/OctoSense/pull/218)），每次工具调用都有审计记录（[#222](https://github.com/OctoSense-org/OctoSense/pull/222)）；peer 的记忆按账户保存，按规则提升**即将推出**（ADR 0002 §9，M7） | [各部分在哪里执行](#各部分在哪里执行) |
| 系统工具箱：模板、`workflow.run`、`workflow.fork`、`toolbox.search`、`toolbox.web_read`、`toolbox.deep_crawl` | 模板**可用**（[OctoSense#82](https://github.com/OctoSense-org/OctoSense/pull/82)，`crates/toolbox`），App Hub 中也有了 `research` 和 `crawl` 权限（[App-Hub#26](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/26)）。只授予声明了它们的系统应用（`os.*`）的 Agent，并且只在启用了 `toolbox-peers` 构建的 Shell 中（手机端默认启用，桌面端没有）；面向商店应用**即将推出**（[OctoSense#64](https://github.com/OctoSense-org/OctoSense/issues/64)） | [系统工具箱](#系统工具箱) |
| `news` 宿主服务（数据服务，不用模型） | **可用**，仅限系统应用（`os.*`） | OctoSense [`apps/news/host-service`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/news/host-service) |
| `glance.publish`、`glance.withdraw`、`glance.list`（服务本身） | **可用**（[OctoSense#72](https://github.com/OctoSense-org/OctoSense/pull/72)），面向任何被授予 `glance` 的隔离应用（[OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)）；`main` 上还支持可交互的 `script` 卡片和 `notify` 通知（`crates/shell/src/glance.rs`） | [发布到 glance 屏幕](#发布到-glance-屏幕) |
| `glance` 权限 | 在 App Hub（[App-Hub#22](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/22)）和 Shell（[OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)）中都**可用** | [谁可以发布](#谁可以发布) |
| L0 数据源 `sys.digest(app:, id:, fields:)` | 检查器**可用**（以 [OctoScript#40](https://github.com/OctoSense-org/OctoScript/pull/40) 合入，由 [OctoScript-Makepad#50](https://github.com/OctoSense-org/OctoScript-Makepad/pull/50) 更新锁定，已在 Shell 的运行时锁定版本中）；由 Shell 从工具箱的运行结果填充**即将推出**（[OctoSense#87](https://github.com/OctoSense-org/OctoSense/pull/87)，未合并） | [绑定到结果的卡片](#绑定到结果的卡片sysdigest) |
| L0 文本槽中模型写的文字，标为 AI 撰写；`sys.chat` 和 `ChatEntry`（卡片内与应用 Agent 对话） | **可用**：检查器（[OctoScript#53](https://github.com/OctoSense-org/OctoScript/pull/53)）、kit 中的标记（[OctoScript-Makepad#68](https://github.com/OctoSense-org/OctoScript-Makepad/pull/68)），以及 glance 卡片和 AppCard 中的宿主一侧（[OctoSense#263](https://github.com/OctoSense-org/OctoSense/pull/263)，`crates/l0-chat`）；不在本仓库锁定的运行时中 | [AI 撰写的文字与卡片内对话](#ai-撰写的文字与卡片内对话model-copysyschat) |
| 渲染并评审卡片：`card-studio`、`card-host --remote` | **可用**（App Hub `main`，[App-Hub#19](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/19)）；由应用的 Agent 运行这一循环**即将推出**（M6） | [卡片级别与渲染评审](#卡片级别与渲染评审) |

一句话概括：商店应用可以调用 `model.complete`，在被授予 `glance` 时发布 glance 卡片（卡片内
可以有由它的 Agent 回答的对话），并在用户允许其 Agent 后通过自己的 peer 与助手对话，这个 peer
保留 `ask_user_question` 并能读取应用自己的文件夹；商店应用自己的工具、根据 `needs` 选择模型、
触发器、后台运行、`AGENT.md` 和技能，以及面向商店应用的系统工具箱仍即将推出。

应用作者现在可以做的：

- 把应用自己的界面做成不依赖 AI 也完整可用，并把“不可用”当作正常状态显示。
- 声明一个能通过 `hub check` 的 Agent（带 `tools: ["ask_user_question"]` 的 `agent`、
  `tools.json`、`AGENT.md`、技能），同时清楚 Shell 会为它分配 peer、提供对话和对应用账户文件夹
  的读取权限，但还不会运行商店应用自己的工具、装入 `AGENT.md` 或技能、为它挑选模型或触发它的
  触发器。
- 把 Agent 应该看到的数据放在账户文件夹里（应用存储中的 `accounts/device/`），系统应用就是
  这样做的（见[Agent 在哪里工作](#agent-在哪里工作storage)）。
- 用 `card-studio` 编写并渲染 L0 卡片；可以围绕 `sys.digest`、`model-copy` 和 `sys.chat`
  设计卡片，但要知道本仓库的运行时还无法检查它们。

**需要知道的版本差异。**

- `tools/octo check` 运行的是本仓库旁边的 App Hub 检出（`main`）。OctoSense Shell 锁定自己的
  一个 App Hub 提交（2026-10-01 为 `58c3c8ae`，见 OctoSense 的 `Cargo.toml` 和
  `native-apps.json`），它可能落后于 App Hub `main`。两者都从同一个 crate 取得 manifest 规则：
  crates.io 上的 `octosense-app-contract` 1.x
  （[ADR 0005](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0005-app-contract.md)）。
  默认 `schema_minor`（0）的 manifest 仍会拒绝未知字段
  （**✓ 2026-10-01 已运行**：``hub: manifest is not valid: unknown field `future_field`, expected one of `schema`, `id`, … `requires`, `schema_minor` ``），
  所以不要使用 Shell 锁定版本不认识的字段。
- 本仓库的 `card-host` 和 `card-studio` 是按
  [`native-runtime.lock.json`](../native-runtime.lock.json) 锁定的运行时构建的：
  Octoscript-Makepad `2cc5ef37`，它锁定 Octoscript `5991dfae`，与 Shell 锁定的版本相同。它有
  `sys.digest`、文本槽中的 `model-copy`、`sys.chat` 和 `ChatEntry`（OctoScript #40、#53）。

如果想提前准备，可以参照 App Hub 的 News 示例
（[`crates/app-policy/tests/fixtures/news-agent`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/crates/app-policy/tests/fixtures/news-agent)），
在 `bundle/` 之外起草 `tools.json` 和 `AGENT.md`。

## 应用自己的 Agent

自 [App-Hub#18](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/18)（2026-09-27 合并）起在 App Hub 准入检查中**可用**，Shell 锁定的
App Hub 也包含它。自 [OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)（2026-09-30）起，对于声明了 Agent（或
`octos.*`，或附带 `tools.json`）的应用，Shell 会在用户允许后为它分配自己的 peer，把应用包
中的工具注册到这个 peer，并让用户在“Ask <app>”面板中与它对话；系统 Agent 也可以把任务交给它
（见[系统 Agent 与应用 Agent](#系统-agent-与应用-agent)）。还没有任何 Shell 把
`AGENT.md` 或技能装进 peer、挑选模型或触发触发器（ADR 0002 实施第 2 步）。

契约见 App Hub 的
[PUBLISHING § The app's agent and tools](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-apps-agent-and-tools)；
完整示例是 App Hub 的
[`crates/app-policy/tests/fixtures/news-agent`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/crates/app-policy/tests/fixtures/news-agent)。

### 应用的 Agent 目前得到什么

Shell 在脚本应用的 peer（`card.<app id>`）上注册的内容，读自 OctoSense `f52620c` 的
`crates/shell/src/host_tools/`（只读代码，未运行）：

| 工具 | 来源 | 商店应用 | 系统应用（`os.*`） |
| --- | --- | --- | --- |
| `ask_user_question`（octos 内核工具） | `agent.tools: ["ask_user_question"]` | **有** | **有**（News、Mail、Calendar） |
| `files.list`、`files.read`、`files.search`（只读，无需审批） | 每个其 Agent 有工作区的 peer，限 Unix 平台 | **有**：只限它的账户文件夹，每次读取 128 KiB，每次列出 500 项，每次搜索 100 条匹配 | **有** |
| 它自己 `tools.json` 中 `implemented_by: "host-service"` 的工具 | 在工具命名空间对应的宿主服务上、以应用的身份运行，就像它自己调用 `host.request` 一样；该服务族必须已被授予，或者是系统应用自己的命名空间 | 返回 `not_granted`：商店应用没有自己的宿主服务（除非它的命名空间恰好是它已被授予的服务族，例如 id 以 `.mail` 结尾并被授予 `mail`；那时调用等同于它自己的 `host.request`） | **有**：`news.list`、`news.read`、`mail.notify`、`calendar.events`、`calendar.add_event`、`calendar.remove_event`、`calendar.notify`、`calendar.agenda` |
| 它自己 `tools.json` 中 `implemented_by: "app"` 的工具 | 本应在应用的脚本中运行 | 在 Card runner 能接手之前返回 `<tool> runs in the app's own script; open the app to use it`（**即将推出**） | 同左 |
| 通用宿主工具 `ledger.read`、`ledger.write`、`net.fetch`、`storage.read`、`storage.write`、`card.render` | `agent.tools` | 准入检查接受，但没有任何 Shell 实现它们（在 OctoSense `crates/` 中找不到） | 同左 |
| 其他应用可共享的工具（`mail.send`） | `agent.tools` 中带点的名称 | 被商店的准入检查拒绝：`app <id> requests tool "mail.send", which this host does not offer contained apps`（**✓ 2026-10-01 已运行**） | 由 Shell 授予其命名空间所属的应用；目前没有任何授予 |
| 系统工具箱的工具 | `research` / `crawl` 权限 | **即将推出** | 在启用 `toolbox-peers` 时（见[下文](#系统工具箱)）；目前没有系统应用声明 `research` |
| `dev.run`（一条 shell 命令） | 开发者模式，对它覆盖的应用 | 只在开发构建中 | 同左 |

所以，商店应用的 Agent 可以与用户和系统 Agent 对话、向用户提问，并读取应用保存在账户文件夹
里的内容；它还不能通过自己的工具做事。转发层还默认把每个 Agent 限制为每个回合 32 次、每天
1000 次工具调用（`crates/shell/src/host_tools/relay.rs`）。

### Agent 在哪里工作：`storage`

App Hub 的 `storage` 块（[App-Hub#44](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/44)，
ADR 0004 §11）决定 Agent 能看到什么：

| 字段 | 含义 |
| --- | --- |
| `storage.accounts` | `true`：按账户保存数据，每个账户一个 Agent（Mail）。省略或 `false`：一个 `device` 文件夹、一个 Agent |
| `storage.agent_workspace` | `"account"`（默认）：Agent 的工作区就是该账户的文件夹，它的对话通过 octos `read_parent` 读取这个文件夹。`"none"`：没有文件，只有工具返回的内容 |
| `storage.cache_max_bytes` | 隔离目录中 `cache/` 的上限 |

账户文件夹是应用自己存储中的 `accounts/<account>/`（没有账户的应用为 `accounts/device/`）。
系统应用把数据放在那里（自 [OctoSense#229](https://github.com/OctoSense-org/OctoSense/pull/229)
起，News、YouTube、Photos 和 Maps 中都有 `let DATA = "accounts/device/"`），可重新获取的缓存
放在 `cache/`，所以它们的 Agent 能读到这些数据；写在隔离目录顶层的数据，Agent 读不到。按同样
布局（`fs` 路径放在 `accounts/device/` 下）的商店应用，按同一段代码应该得到同样的结果，但这一点
**未验证**：本文没有在 Shell 中运行过带 Agent 的商店应用。`storage.external` 只给原生应用，
脚本应用的 manifest 写了会被拒绝。卡片内对话的记录也保存在同一个文件夹的 `chat/` 下
（见[下文](#ai-撰写的文字与卡片内对话model-copysyschat)）。

准入检查接受 `"storage": {"accounts": false, "agent_workspace": "account"}`
（**✓ 2026-10-01 已运行**）。

### 设计（ADR 0002）

OctoSense
[ADR 0002](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0002-event-driven-app-agents.md)
（Proposed）对应用中 AI 的决定，简要如下：

| § | 决定 |
| --- | --- |
| 1 | 每个提出需要的应用都有自己的 Agent（它的应用 peer）；系统 Agent 负责监督，从不替应用 Agent 写提示词。 |
| 2 | 触发器属于应用：定时、来自其宿主服务的数据事件，或用户在应用中的操作。 |
| 3 | 应用随包提供自己的 Agent：`AGENT.md`、技能和模型**需求**；宿主从用户的提供方中挑选模型。 |
| 4 | 应用提供类型化工具（`tools.json`），带风险等级和确认归属；宿主把它们注册到应用的 peer。 |
| 5 | 采集是代码（数据服务，不用模型）；判断交给模型。 |
| 6 | 搜索、研究和抓取是宿主运行的系统工具箱，按应用授予，并带有范围限制。 |
| 7 | 卡片是 L0，绑定到宿主解析的数据源，在 `glance.publish` 之前渲染并评审。 |
| 8 | glance 屏幕由系统 Agent 编排。 |
| 9 | 记忆默认属于应用私有，只有规则或用户才能把它提升出去。 |
| 10 | 用户在应用内与应用的 Agent 对话；审批也在那里进行。 |
| 11 | 系统 Agent 用带版本的覆盖层调整应用 Agent；从不修改锁定的 `AGENT.md`。 |
| 12 | 脚本应用和原生模块遵循同一模型；不同的只是规则在哪里执行。 |
| 13 | 最小权限：工具、网络、文件、记忆、密钥、风险、模型、预算、输出、控制。 |
| 14 | 用于有界任务的、窄而直接的一次性模型调用（`model.complete`，见[上文](#一次性模型调用model)）；由 OctoSense#95 加入（已合并）。 |

### 应用包

```text
bundle/
  manifest.json      "agent": { … } (below)
  tools.json         the app's own tools (next section)
  AGENT.md           named by agent.instructions
  skills/<name>/     SKILL.md + manifest.json, each named in agent.skills
  main.splash, listing.json, assets/, screenshots/  as for any app
```

所有文件都在应用包摘要之内，所以运行的 Agent 就是审核过的那一个。manifest 中没有
`agent` 却带有 Agent 文件，或者有未声明的 `AGENT.md` 或技能目录，都会被拒绝（App Hub
`crates/app-policy/src/agent.rs`）。

### manifest 中的 `agent`

一个能通过准入检查的商店应用 Agent。**✓ 已运行**：`tools/octo new --id
dev.example.brief <dir>`，然后加入这个 `agent`、下一节的 `tools.json`（外加一个只读工具
`brief.topics.get`）、`AGENT.md` 和下面的技能，再用按 App Hub `main` `a72989f` 的
`crates/` 构建的 `hub` 运行 `hub stamp <bundle>` 和 `hub check <bundle> --allow-unsigned`：

```json
"capabilities": ["storage", "glance"],
"agent": {
  "profile": "read-only",
  "tools": [],
  "max_iterations": 6,
  "token_budget": 60000,
  "model": {
    "needs": ["tool_calling", "multilingual"],
    "tier": "standard",
    "local_only": false,
    "per_task": { "summary": { "needs": ["tool_calling", "reasoning"], "tier": "strong" } }
  },
  "background": true,
  "triggers": { "schedule": ["30 7 * * *"] },
  "instructions": "AGENT.md",
  "skills": ["morning-brief"]
}
```

```text
$ hub check <bundle> --allow-unsigned
  grants: capabilities {"glance", "storage"}, hosts {}, storage 16777216 bytes, agent read-only
```

（唯一的拒绝项是模板缺少截图，用真实截图即可解决。）系统应用声明的是一个更小的 Agent，
Shell 目前就会据此行事：

```json
"agent": { "profile": "read-only", "tools": ["ask_user_question"], "model": { "needs": ["tool_calling"] } }
```

配合 `"capabilities": ["storage", "glance"]`，它得到同样的 `grants:` 行
（**✓ 2026-10-01 已运行**，App Hub `41bc959`）。

| 字段 | 规则（App Hub `crates/app-contract/src/manifest.rs`、`crates/app-policy/src/policy.rs`） | 目前在哪里执行 |
| --- | --- | --- |
| `profile` | `read-only`、`workspace-write` 或 `workspace-write-never-ask`；没有完全访问 | 准入检查；Shell 目前还不读取它（peer 的边界来自它的工作区和注册的工具） |
| `tools` | 通用宿主工具 `ledger.read ledger.write net.fetch storage.read storage.write card.render`（准入检查接受，但还没有 Shell 实现），以及 octos 内核工具中唯一的 `ask_user_question`；其他一律拒绝。**✓ 2026-10-01 已运行**：`web_search` 得到 `[refused] agent: agent.tools names the octos kernel tool "web_search"; a contained app's agent may keep only ask_user_question` | 准入检查；Shell 把 `ask_user_question` 交给 peer（[OctoSense#190](https://github.com/OctoSense-org/OctoSense/pull/190)） |
| `max_iterations`、`token_budget` | 上限分别裁剪为 8 和 200 000 | 准入检查（`grants:` 行） |
| `model.needs` | 取自 `tool_calling vision long_context reasoning structured_output multilingual` | 准入检查；应用有工具却没有 `tool_calling` 时会警告。Shell 还不会据此挑选模型 |
| `model.tier` | `fast`、`standard`（默认）或 `strong` | 准入检查 |
| `model.local_only` | 对整个应用生效；数据不得离开用户的设备 | 准入检查（可共享的工具必须写明 `private_data: false`） |
| `model.per_task` | 命名任务 `[a-z_]{1,32}`，最多 8 个，由 `AGENT.md` 引用 | 准入检查 |
| 不写提供方或模型名称 | 未知键会被拒绝：``hub: manifest is not valid: unknown field `provider`, expected one of `needs`, `tier`, `local_only`, `per_task` ``（**✓ 已运行**） | 准入检查 |
| `background` | 请求在应用关闭时运行；由用户按应用授予；必须同时有 `triggers` | 准入检查；授予和唤醒**即将推出** |
| `triggers.schedule` | 五段式 cron，本地时间，最多 16 个触发器 | 准入检查；真正触发**即将推出**（ADR 0002 M3） |
| `triggers.events` | 应用自己宿主服务的事件，位于自己的命名空间（`news.items.new`） | 准入检查；事件投递**即将推出**（M3）。商店应用没有宿主服务，所以没有可以填写的事件 |
| `instructions`、`skills` | `AGENT.md`（文本，32 KB，不含 HTML 脚本，不含 `#!`）；技能名 `[a-z0-9_-]{1,64}`，最多 16 个 | 准入检查 |

**模型由宿主挑选**：从用户的提供方中选出满足 `needs` 和 `tier` 的模型（ADR 0002 §3，
octos `peer/model/set`）；策略可以降低 tier 或强制使用本地模型；用户可以按应用覆盖。
这一挑选**即将推出**（ADR 0002 第 2 步）。平局时如何取舍，是 ADR 中尚未解决的问题。

### `AGENT.md` 与技能

`AGENT.md` 描述 Agent 的角色：每个触发器发生时做什么、应用数据中什么重要、输出必须满足的
评审标准，以及它的记忆规则。技能只包含数据：`skills/<name>/SKILL.md` 加一个
`manifest.json`，其中有 `name`（即目录名）、`version`、`description`、`uses`（每一项必须
是应用自己的工具或在 `agent.tools` 中，否则拒绝，**✓ 已运行**），以及可选的
`prompts.include`；只允许 `.md`、`.json` 和 `.txt` 文件；可执行的字段（`tools`、
`binaries`、`mcp_servers`、`hooks` 等）会被拒绝。

```json
{
  "name": "morning-brief",
  "version": "1.0.0",
  "description": "Write the short morning note from the followed topics.",
  "uses": ["brief.topics.get", "brief.note.save"]
}
```

### 审批：`risk` 与 `confirm`

在 `tools.json` 中按工具声明（见下一节）。一次调用是否需要用户同意取决于 `risk` 和
`outward`；由谁的界面来询问取决于 `confirm`；常设规则能否替用户批准取决于 `auto_approvable`
（App Hub PUBLISHING；`outward` 和 `auto_approvable` 自
[App-Hub#44](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/44) 起）：

| `risk` | 运行方式 |
| --- | --- |
| `read`（只查看）、`act`（修改应用自己的状态） | 无人值守运行 |
| `destructive`（发送、发帖、分享、购买、删除） | 只在用户批准后运行 |
| `act` 且 `outward: true`（到达设备之外） | 只在用户批准后运行，与 destructive 工具相同 |

- `read` 工具写 `outward: true` 会被拒绝（**✓ 2026-10-01 已运行**）：
  `[refused] tools: brief.note.share is outward but its risk is read: a call that reaches outside the device is at least act`。
  `act` 工具写它时准入检查会警告：
  `[warning] tools: brief.note.share is outward: every call waits for the host's approval`。
- `auto_approvable: false`（默认 `true`）：任何常设规则（“一小时内允许”）都不能批准它，每次
  调用都需要用户当场同意。用于永久删除、付款、分享到设备之外、账户和安全设置的变更。Shell 取
  它自己的规则和工具声明中更严格的那一个。

| `risk: "destructive"` 且 | 用户在场 | 用户不在场 |
| --- | --- | --- |
| `confirm: "host"`（默认） | 由宿主的审批流程询问 | 在应用的对话中生成一条审批请求 |
| `confirm: "app"` | 应用自己的确认面板是唯一的确认 | 在应用的对话中生成一条审批请求 |

只有 `implemented_by: "app"` 的工具（或原生模块的工具）才允许 `confirm: "app"`。准入检查
会对每个 destructive 工具发出警告；把示例中的 `brief.note.save` 改为 destructive 后得到
（**✓ 已运行**）：

```text
  [warning] tools: brief.note.save is destructive and marked background: in a background run it only becomes an approval request, and runs after the person approves
  [warning] agent: a background agent with destructive tools: each destructive call waits as an approval request until the person answers
  [warning] tools: brief.note.save is destructive: every call waits for the host's approval
```

商店会根据 manifest 和 `tools.json`，为每一项后果给用户显示一行说明，例如 "Its assistant
may work while the app is closed, on a schedule; only if you allow it, and you can turn
it off." 和 "Can ask to mail.send: nothing of this runs until you approve it."

### 各部分在哪里执行

| 部分 | 状态 |
| --- | --- |
| 声明（字段、大小、名称、schema、risk、confirm） | **可用**：App Hub 准入检查会拒绝或警告 |
| 运行时的审批关卡（内核）；批准、修改或拒绝 | **可用**：内核一侧（[octos#2567](https://github.com/octos-org/octos/pull/2567)）和 Shell 的审批面板（[OctoSense#120](https://github.com/OctoSense-org/OctoSense/pull/120)、[#145](https://github.com/OctoSense-org/OctoSense/pull/145)）；审批留在这些面板上，而不是在应用的对话中（[#184](https://github.com/OctoSense-org/OctoSense/pull/184)） |
| Shell 的审批路由（`crates/shell/src/approvals/`） | **可用**：依次是开发者模式、`confirm: "app"`（所属应用的面板）、`auto_approvable: false`（总是由用户决定）、用户的常设规则，最后是当场弹出的面板。规则的条件在读不懂参数时一律不通过（[#215](https://github.com/OctoSense-org/OctoSense/pull/215)）；每一行参数都显示过之后，Approve 才可用（[#218](https://github.com/OctoSense-org/OctoSense/pull/218)） |
| 每次工具调用的审计 | **可用**：每次调用在到达和结束时各记录一次，包括调用者、所属应用、工具和参数的 SHA-256（从不记录参数本身），写入 Shell 主目录下的 `logs/tool-calls.jsonl`（[#222](https://github.com/OctoSense-org/OctoSense/pull/222)） |
| 在应用内与应用的 Agent 对话 | 在 Shell 的“Ask <app>”面板（[OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)）和 glance 卡片的 `sys.chat` 中（[#263](https://github.com/OctoSense-org/OctoSense/pull/263)）**可用** |
| `app/<app>/acct-<hash>` 中的记忆，按账户保存并随账户清除 | **可用**（[#248](https://github.com/OctoSense-org/OctoSense/pull/248)）；按规则提升**即将推出**（ADR 0002 §9，M7）。没有对应的 manifest 字段；记忆规则写在 `AGENT.md` 的文字里 |
| 系统 Agent 的覆盖层 | **即将推出**：ADR 0002 §11，M8 |

## 应用的工具与 peer 工具

应用要写的部分现在就**可用**：应用包中的 `tools.json`，由 App Hub 准入检查校验
（`crates/app-policy/src/agent.rs`）：

```json
{
  "schema": 1,
  "tools": [
    {
      "name": "brief.note.save",
      "description": "Save the morning note the app shows on its first screen.",
      "input_schema": {
        "type": "object",
        "properties": { "text": { "type": "string", "maxLength": 600 } },
        "required": ["text"],
        "additionalProperties": false
      },
      "output_schema": { "type": "object", "properties": { "saved": { "type": "boolean" } } },
      "risk": "act",
      "background": true,
      "implemented_by": "app"
    }
  ]
}
```

- `name` 的形式是 `<namespace>.<tool>`；命名空间是**应用 id 的最后一段**
  （`dev.example.brief` → `brief`，`os.news` → `news`）。
- `input_schema` 和 `output_schema` 都必须提供（缺少 `output_schema` 的工具会被拒绝：
  ``tools.json is not valid: missing field `output_schema` ``，**✓ 已运行**）。它们使用
  JSON Schema 的一个子集（`type title description properties required items enum const
  default minimum maximum minLength maxLength minItems maxItems additionalProperties
  format pattern`）；输入必须是对象。最多 64 个工具，描述最长 1024 个字符。
- `implemented_by`：`host-service`（持有数据、网络或密钥的原生代码）或 `app`（应用自己的
  脚本，用于只整理自身数据的工具）。Shell 在工具命名空间对应的宿主服务上、以应用的身份运行
  `host-service` 工具，就像应用自己调用 `host.request` 一样，从不经由面板（`may_prompt: false`），
  并且只在 manifest 被授予了该服务族、或该服务族是系统应用自己的命名空间（`os.calendar` →
  `calendar`）时才运行；否则返回 `<app> was not granted the <family> service`。`app` 工具目前会
  被拒绝（`<tool> runs in the app's own script; open the app to use it`；OctoSense
  `crates/shell/src/host_tools/script_apps.rs`）。商店应用没有自己的宿主服务，所以这两种工具
  对它都还不能运行。
- `background`、`shareable`、`private_data`、`confirm`、`outward`、`auto_approvable`：见
  [应用自己的 Agent](#审批risk-与-confirm)。
- Shell 的转发层会用 `input_schema` 校验每次调用的参数（最多 64 KiB），用 `output_schema`
  校验结果（最多 256 KiB）。octos 要求 `output_schema` 是对象，所以返回裸数组的工具（例如
  `mail.accounts`）不能原样提供（见 OctoSense#267 的后续事项）。

Shell 会把它们交给应用的 peer：内核一侧是
[octos#2567](https://github.com/octos-org/octos/pull/2567)（"host-registered tools per app
peer with tool-list and risk enforcement"，UPCR-2026-035，2026-09-29 合并），Shell 为应用的
peer 注册其 `tools.json` 并转发调用（[OctoSense#145](https://github.com/OctoSense-org/OctoSense/pull/145)、[#184](https://github.com/OctoSense-org/OctoSense/pull/184)）。按 #2567：

| 方法 | 方向 | 形状 |
| --- | --- | --- |
| `peer/tools/register` | 宿主 → 内核 | `{session_id, peer, host_token, tools: [{name, description, input_schema, output_schema?, risk, background?, outward?, confirm?, shareable?}], generic_tools?, if_version?, call_timeout_ms?, approval_ttl_secs?, max_result_bytes?}` → `{…, version, tools: [{name, model_name, risk, background, outward, confirm}], applies: "next_turn"}`。整组替换上一组。 |
| `peer/tool/call` | 内核 → 宿主 | `{peer, session_id, context_id, turn_id, call_id, tool_call_id, args_digest, name, args, risk, confirm_required, timeout_ms, tools_version}` |
| `peer/tool/result` | 宿主 → 内核 | `{session_id, peer, host_token, call_id, ok?, data?, error?, status?: "awaiting_confirmation"}` |
| `peer/tool/cancel` | 内核 → 宿主 | `{call_id, reason: timeout \| cancelled}` |
| `peer/tools/unregister` | 宿主 → 内核 | 释放已关闭应用的工具路由（[octos#2658](https://github.com/octos-org/octos/pull/2658)、[OctoSense#247](https://github.com/OctoSense-org/OctoSense/pull/247)） |
| `peer/purge` | 宿主 → 内核 | 在删除账户或卸载应用时清除宿主持有的 peer 及其对话记录和记忆（[octos#2649](https://github.com/octos-org/octos/pull/2649)、[OctoSense#248](https://github.com/OctoSense-org/OctoSense/pull/248)） |

模型看到的 `news.list` 名为 `news_list`。默认值：每次调用 30 秒，结果最多 256 KiB，审批
一小时后过期。需要把关的调用（destructive 或 outward）在 `confirm: host` 时等待内核审批；
在 `confirm: app` 且用户在场时，以 `confirm_required: true` 交给宿主。应用从不直接调用这些
方法：由 Shell（`crates/ai-host`）替应用的 peer 调用（ADR 0002 §12）。

## 系统工具箱

模板**可用**（[OctoSense#82](https://github.com/OctoSense-org/OctoSense/pull/82)，已合并：`crates/toolbox`，crate `octosense-toolbox`），
App Hub 也有了 `research` 和 `crawl` 权限（[App-Hub#26](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/26)）。把工具箱授予应用的 Agent
已在 `main` 上，位于 `toolbox-peers` 构建特性之后（`crates/ai-host/src/toolbox_peers.rs`）：
手机端的默认构建包含它，桌面端不包含。

- `research` 提供 `workflow.run`、`workflow.fork`、`toolbox.search` 和 `toolbox.web_read`；
  `crawl` 在范围中 `max_depth` 和 `max_pages` 大于 0 时提供 `toolbox.deep_crawl`。每个工具都只在
  用户允许该应用的 Agent 之后才提供。
- **目前只有系统应用（`os.*`）能得到它们**：脚本应用的 `research` / `crawl` 声明只对 `os.*` id
  生效，所以商店应用不能靠在 manifest 里写上它就给自己授予研究能力。代码中把这一点标为临时的，
  直到 Shell 读取 App Hub 校验过的研究范围为止。面向商店应用**即将推出**
  （[OctoSense#64](https://github.com/OctoSense-org/OctoSense/issues/64)）。2026-10-01 时没有
  系统应用声明 `research`。
- 声明了 `research` 的商店应用还必须带上顶层的 `research` 范围对象，否则准入检查会拒绝
  （**✓ 2026-10-01 已运行**）：
  `[refused] policy: app dev.example.brief requests research but declares no research scope; add a top-level "research" object (octos's scope; {} means no limits)`。

应用的 Agent 从不自己搜索、抓取或操作浏览器。它被授予工具箱中的工具，由宿主在应用之外、
按应用的范围和预算运行（ADR 0002 §6）。

### 模板

固定且有上限的 OctoScript 过程，带有一份 manifest（参数、调用的宿主模块、预算和输出
schema），取自 #82 的 `templates/*/template.json`：

| 模板 | 必填参数 | 可选参数（默认值） | 预算：调用 / 模型调用 / 页面 |
| --- | --- | --- | --- |
| `news-digest` | `topic`、`language` | `search_language`（"en"）、`translate_query`（false）、`limit`（3，1–5）、`max_age_hours`（72） | 8 / 2 / 7 |
| `topic-brief` | `topic`、`language`、`languages`（1–4 个 `{language, translate}`） | `per_language`（3）、`read_top`（4）、`max_age_hours`（72） | 20 / 5 / 10 |
| `market-brief` | `symbols`（1–3 个 `{symbol, name}`）、`language` | `search_language`、`per_symbol`（2）、`max_age_hours`（72） | 13 / 1 / 12 |
| `weather-plan` | `location`、`language` | `activity`、`days`（3）、`search_language`、`limit`（2）、`max_age_hours`（48） | 7 / 1 / 6 |
| `briefing` | `topics`（1–4）、`language` | `search_language`、`per_topic`（2）、`max_age_hours`（24） | 17 / 1 / 16 |
| `compare` | `subjects`（正好 2 个）、`aspect`、`language` | `search_language`、`per_subject`（2）、`max_age_hours`（72） | 9 / 1 / 8 |

任何模板都不能超过 64 次调用、8 次模型调用、32 个页面或 300 秒；一次运行的预算还会被
应用的预算和其范围中的 `max_pages` 进一步收紧。

### 工具

按 #82 的 `src/api.rs`，一次调用以工具名标记：

```json
{ "tool": "workflow.run",
  "arguments": { "id": "news-digest",
                 "params": { "topic": "electric cars", "language": "en" },
                 "run_id": "glance" } }
```

| 工具 | 参数 | 返回 |
| --- | --- | --- |
| `workflow.list` | – | `{templates, refused?}`（模板库加上应用的分支） |
| `workflow.run` | `{id, params, run_id?}`（`run_id` 为 `[A-Za-z0-9_-]{1,64}`） | `{run_id, app_id, template: {id, version, digest}, status: ready \| partial \| failed, data, provenance, diagnostics, stats, trace, started_at, result_path?}` |
| `workflow.fork` | `{id, new_id?}` | `{template, path: "toolbox/templates/<id>"}`；分支记录其来源，不能增加模块、提高预算或关闭来源记录 |
| `workflow.evaluate` | `{a, b, cases}`（1–32 个用例） | 两个模板在相同输入上的比较 |

错误的格式为 `{"error": {kind, message}}`，`kind` 为 `manifest check widening pin
not_found not_granted params runtime io` 之一。Agent 通过 peer 工具使用它们
（见[上一节](#应用的工具与-peer-工具)），而不是通过 `host.request`。这张表中，Shell 向应用 Agent
提供 `workflow.run` 和 `workflow.fork`，另外还有 `toolbox.search`、`toolbox.web_read` 和
`toolbox.deep_crawl`（`crates/toolbox/src/peer.rs`）。

### 范围、预算与来源记录

- **范围**（`host.rs`）：`languages, regions, allowed_domains, denied_domains,
  max_depth, max_pages, recency_hours`；超出范围的调用会被宿主拒绝。（#82 中声明了
  `max_depth` 但尚未使用。）
- **`research` 模块**：`query`、`search`（结构化条目）、`article`（只能读取本次运行中
  找到的 id；每次一个页面；正文会被哈希作为证据）和 `digest`（最多 1200 个字符的摘要，
  以及最多 12 条带引用的要点）。
- **来源记录属于宿主**，而不是模型：每个来源都带有 `id, url, title, source, language,
  published_at, retrieved_at, evidence_sha256, via`。输出中出现宿主没有取回过的 URL，
  这次运行就会失败。
- **结果**写入应用的工具箱文件夹下的 `toolbox/runs/<template>/<run_id>.json`，这个文件夹归宿主
  所有（`<apps root>/.host/toolbox/<app>/`，在应用的隔离目录之外），所以应用无法伪造摘要。
- **每个应用一份预算**：启用 `toolbox-peers` 时，工具箱的模型客户端经由 `model` 服务的
  `ModelHost::complete`（`crates/ai-host/src/toolbox_peers.rs`），所以模板中的调用和直接的
  `model.complete` 调用消耗同一份预算。

## 发布到 glance 屏幕

### `glance.publish`、`glance.withdraw`、`glance.list`

服务在 OctoSense `main` 上**可用**
（[#72](https://github.com/OctoSense-org/OctoSense/pull/72)，`crates/shell/src/glance.rs`）：

| 方法 | 参数 | 返回 |
| --- | --- | --- |
| `glance.publish` | `{card_id, source \| script, data?, title, priority?, expires?, open?: {app, route?}, notify?}` | `{card_id, replaced, expires_at}` |
| `glance.withdraw` | `{card_id}` | `{withdrawn}` |
| `glance.list` | – | `[{card_id, title, priority, published_at, expires_at}]`，只包含调用者自己的卡片 |

- 二者选一：
  - `source`，一张 **L0 卡片**（头部声明时可以是 L1；L2 会被拒绝），按 `data`（从卡片数据源
    名称到值的映射）实例化，并在保存前经过 Card runner 的流水线降级处理。`sys.chat` 数据源必须
    写发布卡片的应用（见[卡片内对话](#ai-撰写的文字与卡片内对话model-copysyschat)）。
  - `script`，一个 **Splash 程序**，与脚本应用的 `main.splash` 是同一种东西（有自己的状态、
    处理函数、`host.request` 调用和存储），不带 `data`：这是可交互的卡片（回复框、表单）。
- `notify: true` 还会发出一条通知（手机的通知栏、桌面端的 toast）。在桌面端点击 toast 会在
  卡片窗口中打开这张卡片；新卡片还会打开 glance 面板。
- **限制：** `card_id` 为 1–64 个 `[A-Za-z0-9._-]` 字符；`title` 最多 80 个字符；`source`
  （或 `script`）最多 16 KiB；`data` 按 JSON 计最多 32 KiB；`priority` 0–100（默认 50）；`expires` 60 秒
  到 7 天（默认 24 小时）；每个应用每分钟最多发布 6 次（替换和被 L0 检查拒绝的卡片都计数）；
  每个应用 4 张卡片；存储中共 32 张；显示 6 张。
- **身份：** 发布者就是调用者，永远不是参数；用相同的 `card_id` 发布会替换原卡片；
  `open.app` 必须是调用者自己的应用。点击卡片会打开该应用。`open.route` 会被保存，但尚未
  使用。
- 每个卡片块在自己的隔离环境中运行，遵循发布它的应用的策略（原生模块的卡片块没有任何
  权限）。它是后台界面：它调用的宿主服务不能在那里弹出面板（`may_prompt: false`，
  [OctoSense#204](https://github.com/OctoSense-org/OctoSense/pull/204)），卡片块消失时它还在等待的
  请求会被取消。

### 谁可以发布

- **任何被授予 `glance` 的隔离应用**都可以发布、列出和撤回自己的卡片
  （[OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)，已合并；权限是 [App-Hub#22](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/22)，已在 Shell 的 App Hub
  锁定版本中）。系统应用没有例外。拒绝时返回：`<app> was not granted the glance capability`。
- 原生模块也可以发布，系统应用的宿主服务也会替它们的应用 Agent 发布：Mail 的 `mail.notify`
  以及 Calendar 的 `calendar.notify` 和 `calendar.agenda` 会填好服务随附的固定 L0 卡片
  （`apps/mail/host-service/resources/notice.card`、
  `apps/calendar/host-service/resources/event.card`、`agenda.card`），并以该应用的身份发布
  （[OctoSense#267](https://github.com/OctoSense-org/OctoSense/pull/267)）。商店应用的 Agent
  还没有这样的工具：由应用自己的脚本发布。
- Shell 的演示会发布示例卡片：`OCTOSENSE_GLANCE_DEMO=mail` 发布两张 Mail 卡片（假数据），
  除 `0` 以外的其他值发布一份 News 摘要。

应用中的调用如下（形状取自 `glance.rs`；未运行，因为 `card-host` 不注册任何宿主服务）：

```splash
host.request("glance.publish", {
    card_id: "morning"
    title: "Morning brief"
    source: card_source
    data: {}
    expires: 43200
}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) }
})
```

只有真正发布卡片的应用才申请 `glance`；商店显示 "Show cards on your glance screen"。

## 绑定到结果的卡片：`sys.digest`

L0 数据源**可用**：以 [OctoScript#40](https://github.com/OctoSense-org/OctoScript/pull/40) 合入，
由 [OctoScript-Makepad#50](https://github.com/OctoSense-org/OctoScript-Makepad/pull/50) 更新锁定，
已在 Shell 的运行时锁定版本中（Octoscript `5991dfae`）。由 Shell 填充它**即将推出**：
[OctoSense#87](https://github.com/OctoSense-org/OctoSense/pull/87)（未合并；
`crates/shell/src/glance_digest.rs`）。摘要的 `summary` 以及要点的 `text` 和 `label` 是模型
文字，显示时标为 AI 撰写（见[下文](#ai-撰写的文字与卡片内对话model-copysyschat)）。

L0 的“不写事实”规则禁止卡片把发现的内容当作自己的文字，所以这些发现变成由宿主解析的数据源：

```text
source brief sys.digest(app: "os.news", id: "glance",
                        fields: [topic, summary, points, sources, id, text, cite, n, title, source])
```

- `app` 是字面量，必须是发布卡片的应用；卡片写了别的应用会被宿主拒绝。`id` 是字面量
  （`[A-Za-z0-9_-]{1,64}`，与工具箱的 run-id 字符集相同）或指向状态的路径。
- 记录包含：`status`（`ready partial failed missing expired`）、`topic`、`language`、
  `summary`、`retrieved_at`、`count`、`points`（`{id, text, label, cite, citations}`）
  和 `sources`（`{id, n, title, source, url, published_at}`）。
- **链接只来自 `sources`**，即宿主取回过的内容；含 URL 的文字会被丢弃。摘要缺失、过期或
  格式错误时解析为一条空记录，`$state` 为 `.failed`，而不是报错，这样卡片会显示它自己的
  “暂无内容”文案。
- 在 #87 中，宿主读取该应用最新的 `toolbox/runs/<template>/<id>.json`（位于宿主目录下、
  应用的隔离目录之外），只保留运行时宿主记录的来源，限制文字长度（摘要 800，8 条要点每条
  400，8 个来源），并在运行开始 48 小时后让摘要过期；卡片的过期时间不晚于摘要。

完整示例是 #87 的 `crates/shell/resources/glance/news-brief.card`：

```text
# ledger news.brief@1.0.0
# level:   L0
# profile: ui/l0

source brief sys.digest(app: "os.news", id: "glance",
                        fields: [topic, summary, points, sources,
                                 id, text, cite, n, title, source])

copy label   { class: vocabulary, en: "NEWS DIGEST", zh: "新闻摘要" }
copy nothing { class: vocabulary, en: "No digest yet. News will brief you after its next read.", zh: "暂无摘要。新闻读完下一批后会为你汇总。" }
copy sources { class: vocabulary, en: "SOURCES", zh: "来源" }

view root  Surface(pad: .page) {
             Col(gap: 6) {
               Row(gap: 8) {
                 TextCaption(text: copy.label, width: .fill)
                 TextCaption(text: brief.topic)
               }
               when brief.$state == .failed { TextBody(text: copy.nothing, width: .fill) }
               when brief.$state == .ready {
                 Col(gap: 6) {
                   TextBody(text: brief.summary, width: .fill)
                   for p in brief.points key p.id {
                     Row(gap: 8) {
                       TextRow(text: p.text, width: .fill)
                       TextCaption(text: p.cite)
                     }
                   }
                   TextCaption(text: copy.sources)
                   for s in brief.sources key s.id {
                     Row(gap: 8) {
                       TextCaption(text: s.n)
                       TextCaption(text: s.source)
                       TextCaption(text: s.title, width: .fill)
                     }
                   }
                 }
               }
             }
           }
```

（这里省略了部分头部注释。）Shell 的 L0 检查器接受 `sys.digest`；在 #87 合入之前，没有 Shell
会用工具箱的运行结果填充它（这时卡片显示什么，本文未运行）。本仓库锁定的运行时（Octoscript
`5991dfae`）包含 OctoScript#40，所以它的检查器也认识这个数据源（本文未运行）。

## AI 撰写的文字与卡片内对话：`model-copy`、`sys.chat`

自 2026-10-01 起在 OctoSense Shell 中**可用**：L0 规则见
[OctoScript#53](https://github.com/OctoSense-org/OctoScript/pull/53)（OctoScript 的
[`docs/ui-profile-l0.md`](https://github.com/OctoSense-org/OctoScript/blob/main/docs/ui-profile-l0.md)
§4.2 和 §5.15），kit 中的标记见
[OctoScript-Makepad#68](https://github.com/OctoSense-org/OctoScript-Makepad/pull/68)，宿主一侧见
[OctoSense#263](https://github.com/OctoSense-org/OctoSense/pull/263)（`crates/l0-chat`、
`crates/shell/src/glance_chat.rs`）。不在本仓库锁定的运行时中（见[版本差异](#状态一览)）；
本节内容均未为本文运行。

在此之前，L0 拒绝屏幕上任何由模型写的字符串。现在这条规则分成两条：一条管文字，一条管动作。

**文字：模型写的文字可以填入文本槽，并标为 AI 撰写。** 模型文字包括：声明为
`class: model-copy` 的 `copy`（`copy gist { class: model-copy, en: "Rates held." }`）、
宿主数据源中由模型写的字段（`sys.digest` 的 `summary` 以及要点的 `text`/`label`，`sys.chat`
条目的 `text`），以及被写入了这类文字的 `text` 状态（草稿：
`event use { draft: set(copy.suggestion) }`）。文本槽是 `TextHero`、`TextTitle`、`TextBody`、
`TextRow`、`TextEyebrow`、`TextCaption`、`Band`、`Bubble`、`ChatEntry` 和 `Field` 的 `text`
参数；chip、磁贴和标签页的标签、头像、图标和占位文字都不是。kit 会在文字上方画一个小的闪光
图标和 `AI` 眉题，颜色与文字本身相同；文字仍是纯文本（没有 Markdown、HTML 或链接）。

**动作：模型写的文字从不决定运行什么。** 它不能作为动作的载荷或目标、数据源参数、条件、循环键、
控件标签、组件属性、状态初值，也不能写入宿主存储。检查器默认拒绝：除文本槽外的每个位置都不接受它。

**卡片内与应用的 Agent 对话。** 取自 OctoScript 的 `chat.card` 样例：

```text
source convo sys.chat(app: "os.news", thread: "main", fields: [entries, id, role, text])

state draft { shape: text, initial: "" }

copy title { class: vocabulary, en: "ASK THE NEWS AGENT", zh: "问新闻助手" }
copy ask   { class: vocabulary, en: "Ask about today's news", zh: "问问今天的新闻" }

event send { convo: append($value), draft: clear }

view root  Surface(pad: .page) {
             Col(gap: 8) {
               TextEyebrow(text: copy.title)
               for m in convo.entries key m.id {
                 ChatEntry(text: m.text, role: m.role)
               }
               Field(text: draft, placeholder: copy.ask, on_commit: send, width: .fill)
             }
           }
```

- `app` 是字面量，必须是**发布卡片的应用**：写了别的应用的卡片，Shell 拒绝发布；这样的卡片读到
  的是 `unavailable` 的对话记录，也写不进任何东西。`thread` 是 `[A-Za-z0-9_-]{1,64}` 或指向
  状态的路径。
- 数据源返回 `status`、`count` 和 `entries`，每行为 `{id, role, text, at}`；`role` 为 `user`、
  `model` 或 `host`（一条通知）。`ChatEntry(text: m.text, role: m.role)` 按角色在对应一侧画出
  气泡；两个参数必须来自同一行，只有 `model` 条目会被标为 AI 撰写。
- **对话记录属于宿主。** 卡片 `data` 中放在该数据源名下的任何内容，都会被宿主自己的对话记录
  替换。卡片唯一的写入是 `append`，只接受用户在 `Field` 中输入的内容，并记为一条 `user` 条目；
  然后宿主在应用的对话（用户通道）中运行一个回合，把回复作为 `model` 条目追加；如果应用没有
  Agent，或用户还没有允许它，则追加一条 `host` 通知（"<app> has no agent to answer here yet."）。
  卡片永远无法写入 `model` 条目。
- **限制**（`crates/l0-chat/src/lib.rs`）：去掉首尾空白后每条消息最多 4 KiB，每个会话每 2 秒
  最多一条、Agent 回答期间不接受新消息，保留最近 200 条，回复超过 16 KiB 会被截断。
- **存储**：每个会话一个只有所有者可读写的文件，位于应用的账户文件夹
  `apps/<app>/accounts/<account>/chat/<thread>.json`，这同时也是 Agent 的工作区，所以 Agent
  能读到它参与的对话记录。
- **在哪里得到回答**：桌面端卡片窗口（由卡片通知打开的那个窗口；`glance_sheet.rs`）中的 glance
  卡片，以及 AppCard 的 L0 卡片（那里的回复目前仍是一条 `host` 通知）。手机的 glance 页面不走
  这条路径（在 `crates/shell/src/mobile_*` 中找不到）。App Hub 的 Card runner 不回答
  `sys.chat`，所以卡片应用自己的 `page.card` 暂时不能使用它（在 App Hub `crates/` 中找不到）。

想用它的商店应用，用 `glance.publish`（`source`）发布一张写着自己 id 的这类卡片，并声明一个
Agent，好让用户能够允许它。想试一下这个流程，可以用桌面 Shell 的
`OCTOSENSE_GLANCE_DEMO=mail`：它用假数据发布两张 Mail 卡片，其中一张带有 Ask 对话（OctoSense 中的
`desktop/scripts/mail_card_remote.sh` 以隐藏窗口驱动它；本文未运行）。


## 卡片级别与渲染评审

级别定义在 OctoScript 的
[`docs/ui-profile-l0.md`](https://github.com/OctoSense-org/OctoScript/blob/main/docs/ui-profile-l0.md)：

| 级别 | 允许的内容 | 用于 AI 输出 |
| --- | --- | --- |
| **L0** | 只有 UI 声明：数据来自宿主解析的、已登记的 `sys.*` 数据源，没有表达式，没有调用 | 生成卡片和 glance 卡片的默认级别 |
| **L1** | L0 加上算术表达式，用 `# level: L1` 头部声明 | 只在需要算术时使用 |
| **L2** | 命令式 Splash（`ui.<id>.set_*`） | 生成的卡片不允许；脚本应用的 `main.splash` 就是这一级 |

本仓库中的 L0 卡片示例：[docs/l0/](l0/)。

**渲染与评审**（**可用**，App Hub `main`，`crates/card-studio`；octos 技能
`skills/card-studio`，工具 `card_render` 和 `card_critique_payload`）：在隐藏的
`card-host --remote` 中按目标尺寸渲染卡片，运行可测量的检查（文字被截断、放不下、数据源
失败、lint、降级处理），再按评审标准生成一个视觉评审请求。取自 App Hub 的
[DEVELOPMENT.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/DEVELOPMENT.md#inspecting-a-card-before-publishing-card-studio)
（本文未运行）：

```sh
cargo build --release -p octosense-card-host -p octosense-card-studio
export CARD_STUDIO_KIT=../octoscript-makepad/components/l0
target/release/card-studio render --card news.card --data digest.json \
    --size glance --size phone --size desktop --out out/
target/release/card-studio critique --report out/report.json --rubric AGENT-rubric.md --inline > request.json
```

也可以手动使用同一套工具：`card-host … --remote`（或 `MAKEPAD_REMOTE=<port>`），然后用
`/snap` 读取控件文字和矩形，`/g` 抓取一帧（`/g?raw=1` 得到 PNG 字节），`/d` 查看控件树，
以及 `/log` 和 `/quit`。`tools/octo run --hidden` 和 `tools/octo shot` 为应用包封装了这些
操作（README，[无头测试](../README.zh-CN.md#无头测试同时测多个应用不占屏幕)）。

由应用的 Agent 运行这一循环（ADR 0002 M6）**即将推出**。

## 端到端示例：News

News 是 ADR 0002 的第一个切片。每一步及其现状：

| # | 步骤 | 状态 | 位置（未注明的均在 OctoSense） |
| --- | --- | --- | --- |
| 1 | **数据服务采集**，不用模型：HN、TechMeme、Google News、RSS、关注的话题（Google News、GDELT），已读条目账本，每 15 分钟一次 | **可用**（M1） | `apps/news/host-service`：`news.list`、`news.read`、`news.topics.get`、`news.topics.set`、`news.refresh`、`news.sources`、`news.feeds.import`；仅限 `os.*` |
| 2 | **应用包从中读取**：`host.has("news")`，然后 `news.list {feed, current: true, limit: 30}` | **可用**：News 的 manifest 申请了 `news`，并在 `host.has("news")` 时使用该服务 | `apps/news/bundle/main.splash` |
| 3 | **触发器唤醒 Agent**：服务的抓取报告（“N 条新内容”）作为 `news.items.new`，或定时（`0 7 * * *`） | **即将推出**（M3）：服务的 `on_fetch` 钩子目前只写日志 | `crates/shell/src/apps.rs` `register_news` |
| 4 | **News 的 Agent 运行**，使用应用包中声明的 `AGENT.md`、技能和工具 | 声明在 App Hub 中**可用**（#18）；用户允许后为 `os.news` 分配带有其 `tools.json` 工具（`news.list`、`news.read`）和 `ask_user_question` 的 peer，**可用**（[OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)、[#190](https://github.com/OctoSense-org/OctoSense/pull/190)）；把 `AGENT.md` 和技能装进 peer **即将推出** | `apps/news/bundle`、`crates/shell/src/agents.rs` |
| 5 | **运行 `news-digest` 模板**：`workflow.run {id: "news-digest", params: {topic, language}, run_id: "glance"}` | 模板**可用**（#82）；面向系统应用的工具箱 peer 工具已在 `main` 上，位于 `toolbox-peers` 之后，但 News 还没有声明 `research`，所以它的 Agent 没有 `workflow.run`（**即将推出**，M5，#64） | `crates/toolbox`、`crates/ai-host/src/toolbox_peers.rs` |
| 6 | **宿主保存结果**，附带来源记录：`toolbox/runs/news-digest/glance.json` | 在工具箱运行器中**可用**（#82）；由 Agent 发起**即将推出**（#64） | `crates/toolbox/src/runner.rs` |
| 7 | **卡片绑定到结果**：`news-brief.card`，`source brief sys.digest(app: "os.news", id: "glance", …)` | L0 数据源**可用**（OctoScript#40、OctoScript-Makepad#50）；由 Shell 填充**即将推出**（#87，未合并） | `crates/shell/src/glance_digest.rs`（在 #87 中） |
| 8 | **按 glance、手机和桌面尺寸渲染并评审**卡片 | 工具**可用**（`card-studio`）；由 Agent 运行**即将推出**（M6） | App Hub `crates/card-studio` |
| 9 | **`glance.publish`** 这张卡片（`card_id` 为 "brief"，`data: {}`；由宿主填入 `brief`） | **可用**，由被授予 `glance` 的隔离应用发布（#86） | `crates/shell/src/glance.rs` |
| 10 | **用户点击卡片，打开 News** | **可用**（桌面面板和手机的 glance 页面会打开发布卡片的应用） | `glance_panel.rs`、`mobile_pages.rs` |

想现在看到第 9–10 步，可以运行桌面 Shell 自带的检查：它在启动时以 `os.news` 身份发布一张
示例卡片（`OCTOSENSE_GLANCE_DEMO=1`），并从卡片打开 News，全程隐藏窗口、通过远程控制桥
操作（在 OctoSense 检出目录中运行；本文未运行）：

```sh
cargo build --release -p octosense && desktop/scripts/glance_remote.sh
```

Mail 的卡片窗口、其中的回复草稿和卡片内的 Ask 对话也有同类检查：
`desktop/scripts/mail_card_remote.sh`（`OCTOSENSE_GLANCE_DEMO=mail`，假数据；本文未运行）。

## 不接真实提供方的测试

- **以无头方式运行应用**，不要用系统截图，做法同[测试](#测试)和
  [QUICKSTART §4a](QUICKSTART.md#4a-headless-test-without-the-screen-several-apps-at-once)。
  `card-host` 不注册任何宿主服务，所以按上文对 `octos` 和 `model` 验证过的规则，已授权的
  `glance.*` 调用在那里返回 `no service answers "glance" on this device`，未授权的返回
  `this app was not granted "glance", which "glance.publish" needs`（未针对 `glance` 运行）。
  让每个这类调用的错误路径都在界面上可见，并实际走一遍。
- **用准入检查核对 Agent 声明**：`tools/octo check <bundle>`（`hub check`）离线校验
  `agent`、`tools.json`、`AGENT.md` 和技能，不涉及任何模型（见[应用自己的 Agent](#应用自己的-agent)，
  已用 `hub check` **✓ 运行**）。
- **卡片：** 用 `card-studio render --card … --data <fixture>.json` 渲染
  （见[上文](#卡片级别与渲染评审)）：数据是固定样例，不需要模型或网络。对于
  `sys.digest` 卡片，#87 带有一个运行结果样例
  `crates/shell/resources/glance/fixtures/news-digest-run.json`，以及
  `OCTOSENSE_GLANCE_DEMO=digest`（**即将推出**）。检查 `sys.chat` 卡片的布局同样不需要模型：没有
  Agent 时宿主会回一条 `host` 通知。这两种卡片都需要比本仓库锁定版本更新的运行时
  （见[版本差异](#状态一览)）。
- **平台自身测试中的替身**，供你修改某个服务或工具箱时使用（在 OctoSense 中，而不是在应用包
  中；本文未运行这些命令）：

  | 部件 | 替身 | 状态 |
  | --- | --- | --- |
  | `model` 服务 | 假的传输层，`cargo test --locked -p octosense-llm-service --test complete` | **可用**（#95） |
  | 工具箱模板 | `fixture::FakeModel`（确定性、抽取式；可以注入错误的 URL 或引用）和 `FixtureBackend`，录制好的用例在 `templates/*/fixtures/`；`cargo test --locked -p octosense-toolbox` | **可用**（#82） |
  | `news` 服务 | 固定样例 `Fetcher` 和可调的时钟；`cargo test -p octosense-news-service`（"fixtures, no network"） | **可用** |
  | `llm` 服务 | 本地的假提供方端点（`fake_provider`）、`FakeScanner`、`FakePicker`；`OCTOSENSE_LLM_VAULT=file` 让密钥不进入钥匙串 | **可用** |
  | 应用 peer | `tests/fixtures/mock_llm.py`（一个兼容 OpenAI 的服务器，回复 `ECHO: <text>`），以及 `model_id: "mock-model"` 的配置；只有设置 `OCTOS_APP_PEERS_TEST_KERNEL=<octos>` 时才运行真实内核测试 | **可用** |
  | 内核 | `crates/kernel/tests/fixtures/fake_kernel.py` | **可用** |

  应用包无法替换成其中任何一个；它们属于平台。

## 来源

- OctoSense `main`（`405139f`，并在 `89787ba` 上重新核对）：`AGENTS.md`；
  `docs/adr/0002-event-driven-app-agents.md`；
  `docs/adr/home/0004-system-apps-are-contained-script-apps.md`；
  `crates/app-peers/README.md`；`crates/ai-host/src/lib.rs`；
  `apps/ai-providers/host-service/src/lib.rs`；`apps/news/host-service`；
  `apps/news/bundle/main.splash`；`crates/shell/src/glance.rs`、
  `crates/shell/src/apps.rs`。PR #70、#82、#86、#87、#95
  （`apps/ai-providers/host-service/src/complete/`），以及用于 2026-09-30 更新的 #106、
  #120、#145 和 #184（`crates/ai-host/src/contained.rs`、`crates/shell/src/agents.rs`、
  `crates/shell/src/host_tools/script_apps.rs`），基于 `main` `7082ff5`。
- 用于 2026-10-01 更新的 OctoSense `main` `f52620c`：`crates/shell/src/agents.rs`、
  `crates/shell/src/host_tools/`（`mod.rs`、`script_apps.rs`、`files.rs`、`relay.rs`）、
  `crates/shell/src/questions/`、`crates/shell/src/glance.rs`、`glance_chat.rs`、
  `crates/l0-chat/src/lib.rs`、`crates/ai-host/src/contained.rs`、
  `crates/ai-host/src/toolbox_peers.rs`、`crates/shell/src/approvals/consent.rs`、
  `apps/mail/bundle/`、`apps/calendar/bundle/`、`apps/news/bundle/`；ADR 0004 和 ADR 0005；
  PR #190、#204、#205、#210、#215、#218、#222、#229、#232、#233、#243、#248、#249、#261、
  #263 和 #267。
- OctoSense-App-Hub `main`（`a72989f`；2026-09-30 更新基于 `0f33211`；2026-10-01 更新基于
  `41bc959`）：`crates/app-contract/src/manifest.rs` 和 `policy.rs`（manifest 及其规则，自
  App Hub #46 起）、`crates/app-policy/src/services.rs`、`agent.rs`、`policy.rs`、`listing.rs`；
  `docs/PUBLISHING.md`；`docs/DEVELOPMENT.md`。
- OctoScript `main` `5991dfae`：`docs/ui-profile-l0.md` §4.2、§5.14 和 §5.15；
  `crates/octoscript-ui-l0/tests/fixtures/chat.card`。PR #40 和 #53；Octoscript-Makepad PR #68。
- octos `ae230ce0`（OctoSense 锁定的版本）以及 PR #2567、#2647、#2649 和 #2658：
  `docs/OCTOS_UI_PROTOCOL_CHANGE_REQUEST_UPCR_2026_035_PEER_HOST_TOOLS.md`。
- Rinx：`src/host/octos.rs`。
