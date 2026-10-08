# 应用中的 AI：OctoSense 的助手

[English](AI-SERVICES.md) | 简体中文

未注明中文版的链接指向英文文档。

用本仓库开发的脚本应用，可以通过三种方式在 OctoSense 设备上使用 AI：一次性模型调用（`model`）、与设备助手对话（`octos.*`），以及在应用包中声明一个应用自己的 Agent。下文的每项功能都标为**可用**（已在所列仓库的 `main` 上，可按描述使用）或**尚未支持**。

标为 **✓ 已运行**的命令，是在 macOS（Apple 芯片）上用 App Hub `main` 构建的 `hub` 和 `card-host` 运行的。其余内容读自代码，没有在 OctoSense Shell 中运行过。Shell 如何实现这些功能，见 OctoSense 的 [`docs/ai-services.zh-CN.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.zh-CN.md) 和 [`docs/architecture.zh-CN.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/architecture.zh-CN.md)。

> **开发应用不需要任何 AI。** 开发和检查脚本应用都不会调用模型，也不需要 API 密钥；你可以使用任何编程 Agent（Codex、Claude Code、Cursor、Gemini CLI、GitHub Copilot 等），也可以不用。只有 Sketch 设计套件流程会运行模型，而且只在你选用它旧版的视觉评审时：这个评审调用 `claude` CLI（`flows/core/llm.py`）。本文只讨论你*完成后的应用*在设备上可以请求的助手。

## 目录

- [简短回答](#简短回答)
- [助手的构成](#助手的构成)
- [系统 Agent 与应用 Agent](#系统-agent-与应用-agent)
- [助手相关能力](#助手相关能力)
- [最小调用示例与“不可用”状态](#最小调用示例与不可用状态)
- [用户看到什么](#用户看到什么)
- [错误](#错误)
- [测试](#测试)
- [一次性模型调用（`model`）](#一次性模型调用model)
- [应用自己的 Agent](#应用自己的-agent)
- [应用的工具与 peer 工具](#应用的工具与-peer-工具)
- [系统工具箱](#系统工具箱)
- [发布到速览栏](#发布到速览栏)
- [绑定到结果的卡片：`sys.digest`](#绑定到结果的卡片sysdigest)
- [AI 撰写的文字与卡片内对话：`model-copy`、`sys.chat`](#ai-撰写的文字与卡片内对话model-copysyschat)
- [卡片级别与渲染评审](#卡片级别与渲染评审)
- [来源](#来源)

<a id="状态一览"></a>

## 简短回答

**在 OctoSense 设备上，商店应用可以进行一次性模型调用（`model`），并在用户允许其 Agent 后与助手对话（`octos.*`）。** `tools/octo run` 使用的 App Hub `card-host` 除了用于发现宿主 API 的 `runtime`，不提供任何宿主服务，所以在那里两者都返回 `no service answers "…" on this device`。无论如何都请把应用做成不依赖 AI 也完整可用：用户可能拒绝，设备也可能没有内核（iOS）或没有提供商。

| 你想要 | 目前的结果 | 详见 |
| --- | --- | --- |
| 进行一次性模型调用（`model`） | 在 OctoSense Shell 中**可用**：按 schema 校验的调用，由用户自己的 AI 提供商回答，有每日预算。`card-host` 返回 `no service answers "model" on this device`（**✓ 已运行**）。 | [一次性模型调用](#一次性模型调用model) |
| 在自己的界面中与助手对话（`octos.*`） | 在托管内核的 Shell 中**可用**（iOS 除外）。第一次调用返回 `Waiting for the person to allow this app's agent (OctoSense asks the first time)`，同时 Shell 询问用户；之后应用与自己的 peer 对话。`card-host` 返回 `no service answers "octos" on this device`（**✓ 已运行**）。 | [最小调用示例](#最小调用示例与不可用状态) |
| 给应用一个自己的 Agent（`agent`、`tools.json`、`AGENT.md`、`skills/`） | **可用**：用户允许后，Agent 得到一个 peer、一个“Ask &lt;app&gt;”对话栏、`ask_user_question`、对账户文件夹的读取工具（仅 Unix）、已授权的宿主服务工具，并把 `AGENT.md` 和技能作为每个回合的指导。没有 `agent` 块的 `tools.json` 同样会让应用拥有一个 Agent。 | [应用自己的 Agent](#应用自己的-agent) |
| 运行由应用脚本实现的工具（`implemented_by: "app"`） | **尚未进入发布版本**：在 OctoSense `main` 上，清单声明了 `requires: ["script-tools-v1"]` 时，工具在打开的应用中运行；应用关闭时，调用返回 `app_not_running`。`desktop-v0.1.0-beta.2` 拒绝执行。 | [应用的工具](#应用的工具与-peer-工具)、[HOST-API-V1 §5](HOST-API-V1.zh-CN.md#5-实现声明的应用工具) |
| 用事件唤醒 Agent | Gmail 服务的 `<namespace>.new_message` **可用**；其他事件**尚未支持**。 | [清单中的 `agent`](#清单中的-agent) |
| 按定时唤醒 Agent，或根据 `needs` 挑选模型 | **尚未支持** | [清单中的 `agent`](#清单中的-agent) |
| 发布速览卡片（`glance`） | **可用**：L0、脚本和模板卡片，可附带通知。在 OctoSense `main` 上（尚未进入任何发布版本），Agent 的工具只能发布模板卡片和 L0 卡片。 | [发布到速览栏](#发布到速览栏) |
| 在卡片内与 Agent 对话，或显示模型写的文字（`sys.chat`、`model-copy`） | 在 Shell 中**可用**；本仓库的运行时能检查这两者。 | [AI 撰写的文字](#ai-撰写的文字与卡片内对话model-copysyschat) |
| 把卡片绑定到研究结果（`sys.digest`） | 系统应用**可用**；商店应用**尚未支持**，因为它们没有可绑定的研究运行结果。 | [绑定到结果的卡片](#绑定到结果的卡片sysdigest) |
| 通过系统工具箱搜索和抓取（`research`、`crawl`） | 商店应用**尚未支持**（[OctoSense#64](https://github.com/OctoSense-org/OctoSense/issues/64)）。 | [系统工具箱](#系统工具箱) |
| 使用用户的 GitHub 或 Google 账户（`auth` 加 `github`、`gcalendar` 或 `gmail`） | 在 OctoSense desktop-v0.1.0-beta.2 中**可用**；对真实提供商的大部分实际使用尚未验证。 | [CAPABILITIES](CAPABILITIES.zh-CN.md#使用已连接账户) |
| 管理设备的 AI 提供商（`llm`） | 仅限系统应用（返回 `llm is for OctoSense's own apps.`）。不要申请它。 | – |
| 渲染并评审卡片（`card-studio`） | 在 App Hub 中**可用**；由 Agent 自己运行这一循环**尚未支持**。 | [卡片级别](#卡片级别与渲染评审) |
| 在应用包中放入提供商的 API 密钥 | 绝不允许。应用中不得有密钥、令牌或密码（[AGENTS.md](../AGENTS.md#rules-for-every-app)）。 | – |

现在就能发布的做法：让每个界面不依赖 AI 也能工作，把 Agent 应该读取的数据放在 `accounts/device/` 下，并让带有 Agent 文件的应用包通过 `hub check`。

应用在 `net` 下声明的普通 HTTPS API 只是一次网络请求，即使背后运行着模型也是如此。常规规则照样适用：应用包中没有密钥或令牌，主机已列出，隐私说明写明哪些数据会离开设备。它不是设备的助手，也不使用用户配置的任何 AI 提供商。

## 助手的构成

- **每个 Shell 一个 octos 内核。** OctoSense 桌面端和 Home（手机 Shell）各运行一个内核，首次使用时启动。Android 把它打包在 APK 中，OpenHarmony 在进程内运行，iOS 没有内核。桌面端运行 `OCTOS_APP_CORE_BIN` 指定的二进制，没有指定时运行 Shell 旁边打包好的 `octos-kernel`。
- **AI providers**（一个系统应用）是用户选择模型、输入 API 密钥的地方，密钥只在宿主自有的面板上输入，并留在宿主：macOS 上在钥匙串中，其他平台在只有宿主能读的文件中。任何应用都看不到。
- **应用只能通过宿主服务和 app-peer 代理使用 AI**，永远接触不到内核、提供商或密钥（OctoSense [`AGENTS.md`](https://github.com/OctoSense-org/OctoSense/blob/main/AGENTS.md) 第 3、4 条）。
- **应用 peer。** 获得助手授权的应用，每个账户都有一个自己的 octos peer（除非清单写明 `storage.accounts: true`，否则只有一个 `device` 账户）：私有的会话上下文、工作区（该账户的文件夹，`apps/<app>/accounts/<account hash>/`）和记忆（`app/<app>/acct-<hash>`），归 Shell 的系统 Agent 所有（`crates/app-peers`）。
- **审批属于用户，并且在发起请求的应用中进行。** 系统 Agent 从不替应用审批。

**原生应用**是 Shell 按 OctoSense 的 `native-apps.json` 链接的已编译 Rust 应用。大多数作为**原生模块**在 Shell 进程内运行；在桌面端，Terminal 和 Task 作为独立的**进程应用**运行。Shell 的宿主策略授权的原生应用会得到 peer：OctoSense `crates/ai-host/src/lib.rs` 中的 `Policy::shipped()` 授权 `native_agents.rs` 列出的原生应用（Matrix 客户端 Rinx，以及 Terminal、App Hub、Calculator、Clock、Notes、Reminders 和 Weather）。Rinx 的迷你应用宿主再把 `octos.*` 这些名称提供给用户导入 Rinx 的迷你应用。**隔离运行的脚本应用**也会通过 Shell 的 `octos` 宿主服务得到自己的 peer（`card.<app id>`），前提是用户在首次使用时允许它的 Agent。`OCTOSENSE_CONTAINED_APPS=1` 对所有应用跳过这个询问（开发者用的覆盖开关），`0` 则为所有应用关闭助手。

## 系统 Agent 与应用 Agent

- **哪些应用有 Agent。** 脚本应用：清单声明了 `agent` 块或任意 `octos.*` 名称，或应用包附带 `tools.json`；原生应用：Shell 条目授予了 `octos.*`（即上面列出的那些）。Setup › Assistant › Approvals 逐一列出这些应用，用户可以在那里关闭其 Agent。系统应用中，News、Mail、Calendar、Photos、Maps 和 YouTube 都有 Agent，手机上还有 Camera。它们都没有声明 `octos.*` 名称，所以由 Shell 驱动它们的 Agent，应用本身从不调用 `host.request("octos…")`。
- **首次使用。** 用户在首次使用面板上允许应用的 Agent。这个面板可以由应用自己的第一次 `octos.*` 调用、它的“Ask &lt;app&gt;”对话栏（桌面端栏上的“Ask &lt;app&gt;”或 Shift+F8），或者系统 Agent 的 `agents.ask` 触发。此后 Shell 会在启动时准备好这个 peer 并注册它的工具，无论应用是否打开。脚本应用的 peer 是 `card.<app id>`（例如 `card.os.mail`）；原生应用的 peer id 都不以 `card.` 开头。
- **系统 Agent** 是 Shell 自己的会话（`_main:api:octosense#system`），用户在系统对话（助手窗格；桌面端按 F8）中与它交谈。它用 `peer_list` 看到每个已准备好的应用 peer，用 `peer_send_input` 把任务交给其中一个，用 `peer_gather` 读取对方写下的结果，并通过 `agents.list` / `agents.ask` 向 Shell 询问那些用户尚未允许其 Agent 的应用。应用户要求，它可以用 `agents.provision` 配置 Mail 的 Agent（指令、技能文字和来信处理），并用 `agents.status` 查看其状态。它不持有任何应用的工具，从不替应用审批，也不能关闭应用的 peer。
- **提问。** 保留了 `ask_user_question` 的 Agent 可以向用户提问。如果回合由用户或应用发起，问题显示在应用的对话里；如果回合由系统 Agent 发起，问题转到系统对话。问题 10 分钟内无人回答，Shell 就会拒绝它。
- **示例**（未运行）：用户请系统 Agent 生成一张日历卡片；系统 Agent 用 `peer_send_input` 把请求交给 Calendar 的 Agent（如果用户还没有允许，会先出现 Calendar 的首次使用面板）；Calendar 的 Agent 调用自己的一个工具（`calendar.notify`、`calendar.agenda`），它的宿主服务填好随服务附带的固定 L0 卡片，并以 Calendar 的身份发布到速览栏。模型从不编写卡片代码。
- **生命周期。** peer 在多次启动之间保留记忆。退出某个账户会暂停该账户的 Agent；删除账户或卸载应用会清除它（octos `peer/purge`），所以重新安装后是一个新的 Agent。

### 用户直接与应用的 Agent 对话

用户不必经过系统 Agent，可以在三个地方直接与应用的 Agent 对话。每个地方都有自己的**用户通道**，与系统 Agent 的通道并列。用户在首次使用面板上允许该应用的 Agent 之前，这些入口都不会运行。

| 在哪里 | 用户怎么做 | 应用作者要写什么 |
| --- | --- | --- |
| **Shell 的“Ask &lt;app&gt;”对话栏** | 在桌面端从栏上的“Ask &lt;app&gt;”按钮、Shift+F8，或 Setup › Assistant › “Ask this app's agent”，为当前焦点应用的 Agent 打开它。它的回合在用户通道中运行；它的 Stop 按钮只停止这条通道。应用的 Agent 在用户通道中提出的问题在这里回答。 | 什么都不用写：Shell 为**每个**有 Agent 的应用绘制这个对话栏，无论应用自己有没有对话界面。 |
| 速览栏上的**卡片内对话** | 在应用发布的卡片中输入；应用自己的 Agent 在卡片中回答。 | 一张带 `sys.chat` 和 `ChatEntry` 的 L0 卡片，用 `glance` 发布（见[下文](#ai-撰写的文字与卡片内对话model-copysyschat)）。 |
| **应用自己的界面** | 使用应用绘制的对话或“提问”控件。 | 在 `octos` 服务上调用 `host.request("octos.session.open" / "octos.turn.start" / "octos.session.history" / "octos.turn.interrupt", …)`，并在 `capabilities` 中列出这些名称（见[最小调用示例](#最小调用示例与不可用状态)）。 |

- **一个对话，两条通道。** 系统 Agent 的通道是 peer 自己的会话（`_main:api:octosense#peer-…`）；用户通道是一个以共享历史方式打开的请求上下文（`…#peerctx-…`）。每条通道都能只读地看到另一条通道最近的消息。回合按发言者标注，事件和 `octos.session.history` 的每一行都带有 `lane`（`person` 或 `system_agent`）和 `speaker`。
- **每个地方各有自己的用户通道。** OctoSense 按账户和客户端实例区分用户通道。对话栏的实例是 `shell-ask`，卡片内对话的是 `card-chat`，应用自己的 `octos.*` 调用用的是 `<peer>-g<generation>`。所以 `octos.session.history` 返回的是应用自己的对话，从不包含用户在对话栏或卡片中问的内容。
- 来自对话栏或系统对话的回合是用户本人的（`TurnTrigger::Person`）。
- **Shell 审批界面上的 Stop**（某个应用 Agent 的待审批事项和问题下方的按钮，`approvals::stop_agent`）会拒绝该 Agent 正在等待的事项，并停止它在**两条**通道中正在运行的回合：设备归用户所有。
- **在手机上**，这个对话栏做成了全屏面板，但在 `main` 上没有任何触控入口能打开它（手机的 Assistant 磁贴打开的是系统对话）；未在设备上运行。应用自己的界面和它的速览卡片在手机上与桌面端一样可用。
- 原生模块和进程应用通过各自的途径（注入服务上的 `open_conversation`，或 peer link）打开用户通道；脚本应用使用上面的 `octos.*` 名称。

## 助手相关能力

共有四个精确名称，每个都需要单独授权（App Hub `crates/app-contract/src/manifest.rs` 中的 `KNOWN_CAPABILITIES`）。前缀不授予任何能力：准入检查会拒绝 `octos.` 和 `octos.admin`。商店为每个名称显示的文字见 App Hub [PUBLISHING § 清单](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md#清单)。

| 能力与调用 | 参数 | 返回（`r.data`） |
| --- | --- | --- |
| `octos.session.open` | `{}` | `{open: true, conversation, shared_history, model: {lane, provider, model} or nil}` |
| `octos.session.history` | `{}` | 应用自己的会话内容，`{session_id, messages: [...], …}`：它的通道和系统 Agent 的通道按时间合并，每条消息带有它的 `lane` 和发言者。其中从不包含“Ask &lt;app&gt;”对话栏中的回合。 |
| `octos.turn.start` | `{text}`（1 字节到 32 KiB） | 回合结束后的 `{turn_id, text, speaker, lane}`，即回复 |
| `octos.turn.interrupt` | `{}` | `{interrupted, turns}`：在 OctoSense Shell 中，它停止两条通道中正在运行的回合，系统 Agent 的也包括在内 |

两个宿主提供这些名称，参数和返回的格式都沿用 OctoSense 的 `crates/app-peers`：OctoSense Shell 面向隔离应用的 `octos` 服务（`crates/ai-host/src/contained.rs`），以及 Rinx 的迷你应用宿主（[hagency-org/Rinx](https://github.com/hagency-org/Rinx) 中的 `src/host/octos.rs`）。

- 只给 `octos.turn.start` 发送 `text`，另外三个调用不带参数。OctoSense Shell 还接受随 `text` 传入的两个可选参数：`trigger`（`person`、`app`、`incoming`、`schedule` 或 `background`）和 `from`，说明是什么发起了这个回合；不传时，这个回合算作来源未知。其他参数一律返回 `Unsupported Octos arguments`：应用从不指定会话、配置、提供商、模型或审批决定。
- 每个应用实例同一时间只运行一个回合，一个回合超过 180 秒即超时。
- 脚本应用收不到推送的事件。请轮询 `octos.session.history`，其中也包括系统 Agent 的回合。

应用传来的 `trigger: "person"` 会在对话记录中把这个回合标为用户的，但审批规则把它当作应用自己发起的运行：“当我发起时”这类常设规则永远不会替它批准。只有 Shell 自己的输入框（“Ask &lt;app&gt;”对话栏、系统对话）才能证明是用户本人。

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

界面主体中包含 `prompt := TextInput{…}`、`answer := Label{…}` 和 `Button{text: "Ask the assistant" on_click: || ask()}`。

- `host.has("octos.turn.start")` 只说明能力是否**已授予**，不说明是否有服务响应。一定要处理 `r.is_ok == false`。
- 把“不可用”当作正常状态：设备上没有内核（iOS、没有内核的桌面端）、没有配置提供商、未授权、未登录。用一句话说明，并让其他界面照常工作。
- 永远不要向用户索要密钥或提供商。这些由宿主的 AI providers 应用管理。

在 `card-host` 中 **✓ 已运行**（`tools/octo run … --hidden`），应用启动后调用一次 `ask()`：

| 清单 | 读到的标签文字 |
| --- | --- |
| `["octos.session.open", "octos.turn.start"]` | `Assistant unavailable: no service answers "octos" on this device` |
| `["storage"]` | `Assistant unavailable: this app was not granted "octos", which "octos.session.open" needs` |

托管内核的 OctoSense Shell 的回答不同：第一次调用返回 `Waiting for the person to allow this app's agent (OctoSense asks the first time)`，同时 Shell 询问用户；用户允许后，下一次调用才到达应用自己的 peer（未运行）。各种拒绝的文字见[错误](#错误)。

**现在应该发布这个功能吗？** 只有在应用不依赖它也完整可用时才可以：用户可能拒绝，设备可能没有内核或提供商，而 `tools/octo run` 永远不会响应。审核人员会问界面上用不到的授权（`hub scan`），每个 `octos.*` 都会出现在商店的权限列表中。

## 用户看到什么

- **安装前**：商店为每个能力显示一行权限说明，并在隐私概要中写着“Asks the device's assistant to work for it; the assistant's keys stay with the device.”（申请 `octos.turn.start` 时），或“Opens or reads its own conversations with the device's assistant, but cannot ask it to work.”（只申请 open 或 history 时）。
- **声明了 `agent` 块的应用**：商店会为助手加上权限说明，内容因版本而异。`desktop-v0.1.0-beta.2` 的商店显示“Run an assistant for this app (&lt;tools&gt;), inside this app's own data only”，其中 `<tools>` 只列出 `agent.tools` 中不属于内核工具的条目，没有时写 `no tools`，不包括 `tools.json` 中的工具。OctoSense `main` 中的商店（尚未进入任何发布版本）先显示“Run an assistant for this app, only after you allow it”，再用“Its assistant can use these app tools: …”列出 `tools.json` 中的工具名，并用“Its assistant requests these additional tools: …”列出同样那些非内核的 `agent.tools` 条目。
- **密钥和提供商**只在 AI providers 应用中、在宿主面板上设置。
- 助手发起的**工具审批**交给用户，在发起请求的应用中、用宿主自己的控件进行（OctoSense Shell 使用它们的审批面板；Rinx 为它的迷你应用使用自己的控件）；系统 Agent 从不代为审批。脚本应用无法审批任何东西：没有任何参数能携带审批决定。审批面板会完整显示每个参数（隐藏字符和控制字符显示为码位，命令逐行显示），在用户把所有参数都滚动看过之前，批准按钮保持禁用。
- 应用 Agent 的**首次使用面板**，列出它能读什么（它自己的记忆，以及它的账户文件夹；在 `storage.agent_workspace: "none"` 时为“No files: only what its tools return”）、能用什么（保留了 `ask_user_question` 的 Agent 显示“Ask you questions”）以及模型在哪里运行（`crates/shell/src/approvals/consent.rs`）。Setup › Assistant › Approvals 可以再次关闭它。

## 错误

| `r.error` | 含义 | 应用该怎么做 |
| --- | --- | --- |
| `this app was not granted "octos", which "<service>" needs` | 清单中没有列出这个精确名称 | 把它加入 `capabilities`，或删除该调用 |
| `no service answers "octos" on this device` | 当前宿主不向应用提供助手（`card-host`，或没有内核的 Shell 构建） | 显示“不可用”，继续工作 |
| `Waiting for the person to allow this app's agent (OctoSense asks the first time)` | 用户还没有允许该应用的 Agent；Shell 正在询问 | 显示出来；用户回答后再调用一次 |
| `The assistant is turned off for apps on this device` | 设备为应用关闭了助手（`OCTOSENSE_CONTAINED_APPS=0`） | 显示“不可用”，继续工作 |
| `The assistant is not available on this device` | Shell 无法启动该应用的 peer | 显示“不可用”，继续工作 |
| `Add an account in the app before using its assistant` | 应用按账户保存数据（`storage.accounts: true`），但还没有任何账户 | 提供应用自己的添加账户入口 |
| `This app's manifest does not declare that assistant service` | 隔离环境检查之后 Shell 再做的检查：清单没有列出任何 `octos.*` 名称，或没有列出这一个 | 声明它，或删除该调用 |
| `no service answers "model" on this device` | 当前宿主没有 `model` 服务（`card-host`） | 显示“不可用”，继续工作 |
| `model.complete` 返回的 `<code>: <sentence>`，`<code>` 为 `capability`、`no_provider`、`rate`、`budget`、`bad_request`、`invalid_output`、`too_large`、`provider` 之一 | `model` 服务拒绝了这次调用（[详情](#model-服务)） | 显示这句话；让应用不依赖模型也能使用 |
| `Unsupported Octos arguments` | 给 `octos.turn.start` 传了 `text`、`trigger`、`from` 以外的参数，或给其他调用传了任何参数 | 只传这些参数 |
| `Provide text (at most 32 KiB)` | 提示词为空或过长 | 发送前检查 |
| `This app already has an assistant turn running` | 同一时间只能有一个回合 | 等待期间禁用按钮，或先中断 |
| `Nothing is running in this conversation` | 没有正在运行的回合时调用了 `octos.turn.interrupt`（Rinx 的迷你应用宿主返回 `No assistant turn is running`） | 无需处理 |
| 其他（未配置提供商、提供商出错、配额、未登录、授权已撤销） | 宿主原样传回的文字 | 显示出来；不要循环重试 |

`model` 服务按应用保存每日预算，`model.budget` 会返回它（见[下文](#model-服务)）。

## 测试

- **在本仓库的工具中：** 运行 `tools/octo run <bundle> --hidden --port 8141`，通过远程控制桥操作应用，用 `/snap` 读取标签，不要用系统截图（[QUICKSTART §4a](QUICKSTART.zh-CN.md#4a-无头模式不占屏幕同时测试多个应用)）。`card-host` 不注册任何宿主服务，所以助手、模型和速览的每次调用都会返回 `no service answers`；把这个状态截图，作为应用的“不可用”状态。在那里调用已授权的 `glance.publish`，返回 `no service answers "glance" on this device`（**✓ 已运行**）。
- **Agent 声明：** `tools/octo check <bundle>`（`hub check`）离线检查 `agent`、`tools.json`、`AGENT.md` 和技能，不涉及任何模型（见[清单中的 `agent`](#清单中的-agent)，**✓ 已运行**）。
- **卡片：** 用 `card-studio render --card … --data <fixture>.json` 渲染（见[下文](#卡片级别与渲染评审)）；数据是固定样例，不需要模型或网络。检查 `sys.chat` 卡片同样不需要模型：没有 Agent 时宿主会回一条 `host` 通知。
- **在 OctoSense 桌面端：** 按商店路径演练（[PUBLISHING §4](PUBLISHING.zh-CN.md#4-在本地演练商店流程)）。要让 Shell 拥有内核和提供商，见 OctoSense [`docs/ai-services.zh-CN.md` § 本地运行与测试](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.zh-CN.md#本地运行与测试)。在那里，应用的第一次 `octos.*` 调用会请用户允许它的 Agent。桌面端还能在启动时发布速览示例卡片（[OctoSense `desktop/README.zh-CN.md` § 命令行参数与环境变量](https://github.com/OctoSense-org/OctoSense/blob/main/desktop/README.zh-CN.md#命令行参数与环境变量)）。
- **Rinx 的迷你应用宿主**也会响应 `octos.*`，适用于用户检查后导入 Rinx 的应用包（需要登录 Matrix，使用 Rinx 自己的助手 peer）：[Rinx `examples/miniapps`](https://github.com/hagency-org/Rinx/tree/main/examples/miniapps)。这不是 App Hub 的安装路径，并且它会拒绝声明了 `agent` 的应用包。未运行。

测试时要注意两处版本差异：

- `tools/octo check` 运行的是本仓库旁边的 App Hub 检出（`main`）。OctoSense Shell 锁定自己的一个 App Hub commit（见 OctoSense 的 `Cargo.toml` 和 `native-apps.json`），它可能落后于 App Hub `main`。两者都从同一个 crate 取得清单规则：`octosense-app-contract`（[ADR 0005](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0005-app-contract.md)），App Hub 要求 1.7 版，该版本已发布到 crates.io。OctoSense `main` 从 crates.io 解析到的是 1.6.0；Host API v1 需要 1.6 或更高版本。默认 `schema_minor`（0）的清单仍会拒绝未知字段（**✓ 已运行**：``hub: manifest is not valid: unknown field `future_field`, expected one of `schema`, `id`, … `requires`, `schema_minor` ``），所以不要使用 Shell 锁定版本不认识的字段。
- 为本仓库构建的 `card-host` 和 `card-studio`（都是 App Hub 的工具）使用 [`native-runtime.lock.json`](../native-runtime.lock.json) 锁定的运行时：OctoScript-Makepad `33dea2f1`，它锁定 OctoScript `2e37d9e6`。这个运行时能检查 `sys.digest`、文本槽中的 `model-copy`、`sys.chat` 和 `ChatEntry`。Shell 使用的 OctoScript 版本与此相同，但 `desktop-v0.1.0-beta.2` 锁定的是较早的 OctoScript-Makepad `aa80f72c`，它不加载卡片打包的字体。

OctoSense 自己的测试为模型、工具箱、应用 peer 和内核准备了替身，见它的[架构导读 § 11. 测试](https://github.com/OctoSense-org/OctoSense/blob/main/docs/architecture-walkthrough.zh-CN.md#11-测试)。应用包无法换用这些替身。

## 一次性模型调用（`model`）

App Hub 还准入第二条更窄的路径：`model` 能力，由 OctoSense Shell 的 `model` 宿主服务提供。

- `host.request("model.complete", {task, input, schema, class}, fn(r){…})`，`class` 为 `fast` 或 `strong`。宿主从用户自己的 AI 提供商中挑选模型；应用永远看不到提供商、模型 id 或密钥。
- 一次性：没有工具、没有记忆，除 `input` 外没有历史。回复必须符合应用的 JSON Schema（有大小上限）；除非应用明确要求，宿主会拒绝回复中的 URL。每个应用有每日的调用次数和 token 预算，由宿主管理。
- 商店显示“Send what you give it to the AI provider you configured, within a daily budget”；隐私概要显示“Sends what you give it to the AI provider you configured, for one-off answers within a daily budget; it never sees your API keys.”

准入检查接受它，Shell 锁定的 App Hub 也认识这个名称。`card-host` 没有 `model` 服务：在那里调用返回 `no service answers "model" on this device`（**✓ 已运行**）。

### `model` 服务

服务（`apps/ai-providers/host-service/src/complete/`，crate `octosense-llm-service`，由 `crates/ai-host` 与 `llm` 一起注册）的接口如下。ADR 0002 §14“直接的一次性模型调用”明确：凡是需要工具、研究、记忆或审批的事情，主路径仍是应用自己的 Agent（见下文）。

| 方法 | 参数 | 返回（`r.data`） |
| --- | --- | --- |
| `model.complete` | `{task, input, schema, class?, allow_urls?}` | `{output, meta: {class, requested, attempts, usage: {input_tokens, output_tokens, estimated}, budget}}` |
| `model.budget` | – | 只返回调用者的 `budget` |

- **`task`**（最多 4 KiB）用文字说明要做什么；**`input`**（任意 JSON，最多 32 KiB）是要处理的内容，作为数据发送，并告诉模型不要执行其中的任何指令。
- **`class`**：`"fast"`（默认）或 `"strong"`。宿主按用户自己的顺序尝试提供商，同类型的优先，某个提供商失败就跳到下一个。`meta.class` 说明实际用的是哪一类。
- **`schema` 必填**（受限的 JSON Schema 子集，最多 8 KiB）；`output` 一定符合它。回复不是 JSON、不符合 schema、含有 URL 或超过 16 KiB 时重试一次，再失败就拒绝。
- **默认不允许 URL**：回复中出现 `http://`、`https://` 或 `www.` 时宿主会拒绝，因为回复最终会成为卡片数据。只有应用要从输入中提取链接时才传 `allow_urls: true`。
- **按应用计算的预算**，由宿主保存在应用的隔离目录之外：默认每分钟 6 次，每个 UTC 日 100 次调用和 100,000 个 token。`meta.budget` 和 `model.budget` 返回 `{calls_today, calls_per_day, tokens_today, tokens_per_day, tokens_left, per_minute, resets_at}`。
- **拒绝**的格式为 `"<code>: <sentence>"`，`code` 为 `capability`、`no_provider`、`rate`、`budget`、`bad_request`、`invalid_output`、`too_large` 或 `provider` 之一。这句话可以直接显示给用户。
- Card runner 检查能力之后，服务还会再检查应用自己的清单中是否有 `model`。

一次调用（未运行；字面量写法参照 Photos 应用包，列表和映射用空格分隔）：

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

## 应用自己的 Agent

在 App Hub 准入检查和 Shell 中都**可用**。对于声明了 Agent（或 `octos.*`，或附带 `tools.json`）的应用，Shell 会在用户允许后为它分配自己的 peer，把应用包中的工具注册到这个 peer，把它的 `AGENT.md` 和技能作为每个回合的指导加载，并让用户在“Ask &lt;app&gt;”对话栏中与它对话；系统 Agent 也可以把任务交给它（见[系统 Agent 与应用 Agent](#系统-agent-与应用-agent)）。Shell 向商店应用的 Agent 投递一种事件（见[下文](#清单中的-agent)）。尚未支持：其他事件、定时触发，以及根据清单中的 `needs` 挑选模型。

附带 `tools.json` 时，请声明 `agent` 块，并在商店信息和隐私说明中写明。不想要助手，就不要附带 `tools.json`。

契约见 App Hub 的 [PUBLISHING § 应用的 Agent 与工具](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md#应用的-agent-与工具)；完整示例是 App Hub 的 [`crates/app-policy/tests/fixtures/news-agent`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/crates/app-policy/tests/fixtures/news-agent)，[使用已连接账户的参考应用](../examples/connected-apps/README.zh-CN.md)展示了商店应用的 Agent。背后的设计是 OctoSense 的 [ADR 0002](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0002-event-driven-app-agents.md)（Proposed；部分已实现），它的[第一个落地场景](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0002-event-driven-app-agents.md#first-slice-news)是 News。

### 应用的 Agent 目前得到什么

Shell 在脚本应用的 peer（`card.<app id>`）上注册的内容，读自 OctoSense 的 `crates/shell/src/host_tools/`：

| 工具 | 来源 | 商店应用 | 系统应用（`os.*`） |
| --- | --- | --- | --- |
| `ask_user_question`（octos 内核工具） | `agent.tools: ["ask_user_question"]` | **有** | **有**（每个有 Agent 的系统应用） |
| `files.list`、`files.read`、`files.search`（只读，无需审批） | Agent 有工作区的每个 peer，限 Unix 平台 | **有**：只限它的账户文件夹，每次读取 128 KiB，每次列出 500 项，每次搜索 100 条匹配 | **有** |
| 它自己 `tools.json` 中 `implemented_by: "host-service"` 的工具 | 在工具的 `host_method` 所属能力族、或其命名空间对应的宿主服务上，以应用的身份运行，就像它自己调用 `host.request` 一样；该能力族必须已授予，或者是系统应用自己的命名空间 | 通过 `host_method` 调用已授予的 `github`、`gcalendar`、`gmail` 或 `glance` 时**有**。没有 `host_method` 时，工具调用其命名空间对应的服务，而没有任何能力能授予它：`dev.example.summary` 中的 `summary.list` 返回 `not_granted`，即 `dev.example.summary was not granted the summary service`。调用 `github`、`gcalendar` 或 `gmail` 还需要一个当前连接的账户，否则返回 `Connect this app account first` | **有**：News（`news.list`、`news.read`、`news.notify`）、Mail（12 个工具，例如 `mail.peek` 和 `mail.propose_reply`）、Calendar（`calendar.events`、`add_event`、`update_event`、`remove_event`、`notify`、`agenda`），以及 `photos.notify`、`maps.notify`、`youtube.notify`、`camera.notify` |
| 它自己 `tools.json` 中 `implemented_by: "app"` 的工具 | 打开的完整应用中的 `app_tool` 处理函数 | 仅限 OctoSense `main`，且清单声明了 `requires: ["script-tools-v1"]`；应用关闭时，调用返回 `app_not_running`。`desktop-v0.1.0-beta.2` 拒绝执行（`app_tool_unavailable`）：`<tool> declares a script implementation, but this host does not support script tool dispatch` | 同左 |
| 通用宿主工具 `ledger.read`、`ledger.write`、`net.fetch`、`storage.read`、`storage.write`、`card.render` | `agent.tools` | 准入检查接受，但没有任何 Shell 实现它们 | 同左 |
| 其他应用可共享的工具（`mail.send`） | `agent.tools` 中带点的名称 | 准入检查（`hub check`）拒绝：`app <id> requests tool "mail.send", which this host does not offer contained apps`（**✓ 已运行**） | 由 Shell 自己的策略授予；例如 Mail 保留 `calendar.events`、`calendar.add_event` 和 `calendar.notify` |
| 系统工具箱的工具 | `research` / `crawl` 能力 | **尚未支持** | 在启用 `toolbox-peers` 时（见[下文](#系统工具箱)）；没有系统应用声明 `research` |
| `dev.run`（一条 shell 命令） | 开发者模式，对它覆盖的应用 | 开发构建，以及用 `--dev-grant-all` 启动的发布构建；商店构建中永远没有 | 同左 |

转发层默认把每个 Agent 限制为每个回合 32 次、每天 1000 次工具调用（`crates/shell/src/host_tools/relay.rs`）。

### Agent 在哪里工作：`storage`

App Hub 的 `storage` 块（ADR 0004 §11）决定 Agent 能看到什么：

| 字段 | 含义 |
| --- | --- |
| `storage.accounts` | `true`：按账户保存数据，每个账户一个 Agent（Mail）。省略或 `false`：一个 `device` 文件夹、一个 Agent |
| `storage.agent_workspace` | `"account"`（默认）：Agent 的工作区就是该账户的文件夹，它的对话通过 octos `read_parent` 读取这个文件夹。`"none"`：没有文件，只有工具返回的内容 |
| `storage.cache_max_bytes` | 隔离目录中 `cache/` 的上限 |

账户文件夹是应用自己存储中的 `accounts/<account hash>/`（没有账户的应用为 `accounts/device/`）。系统应用把数据放在那里（News、YouTube、Photos、Maps 和 Camera 中都有 `let DATA = "accounts/device/"`），可重新获取的缓存放在 `cache/`，所以它们的 Agent 能读到这些数据；写在隔离目录顶层的数据，Agent 读不到。按同样布局（`fs` 路径放在 `accounts/device/` 下）的商店应用，由同一段代码得到同样的结果。未验证：没有在 Shell 中运行过商店应用的 Agent 读取这个文件夹。`storage.external` 只供原生应用使用，准入检查会拒绝写了它的脚本应用清单。卡片内对话的记录也保存在同一个文件夹的 `chat/` 下（见[下文](#ai-撰写的文字与卡片内对话model-copysyschat)）。

准入检查接受 `"storage": {"accounts": false, "agent_workspace": "account"}`（**✓ 已运行**）。

### 应用包

```text
bundle/
  manifest.json        "agent": { … } (below)
  tools.json           the app's own tools (next section)
  AGENT.md             named by agent.instructions
  skills/<name>/       SKILL.md + manifest.json, each named in agent.skills
  summary-card.splash  a glance card template its tool publishes
  main.splash, listing.json, assets/, screenshots/  as for any app
```

所有文件都在应用包摘要之内，所以运行的 Agent 就是审核过的那一个。准入检查会拒绝未声明的 `AGENT.md` 或技能目录（App Hub `crates/app-policy/src/agent.rs`）。只有 `tools.json`、没有 `agent` 块的应用包能通过准入检查，并且同样会得到一个 Agent，尽管 `hub check` 报告 `agent none`（**✓ 已运行**）。OctoSense `main` 中的商店（尚未进入任何发布版本）会在隐私概要中说明这一点：应用会在用户同意后提供宿主的 Ask 助手。`desktop-v0.1.0-beta.2` 的商店则显示 `Runs no assistant.` 这句话。

### 清单中的 `agent`

下面这个商店应用 Agent 能通过准入检查（**✓ 已运行**）：

1. 运行 `tools/octo new <dir> --platform macos --id dev.example.summary`。
2. 加入下方的 `agent` 块、下一节的 `tools.json` 和模板、一个 `AGENT.md`，以及下文的技能。
3. 运行 `hub stamp <bundle>`，再运行 `hub check <bundle> --allow-unsigned`：

```json
"capabilities": ["storage", "glance"],
"agent": {
  "profile": "read-only",
  "tools": ["ask_user_question"],
  "max_iterations": 6,
  "token_budget": 60000,
  "model": {
    "needs": ["tool_calling", "multilingual"],
    "tier": "standard",
    "local_only": false,
    "per_task": { "summary": { "needs": ["tool_calling", "reasoning"], "tier": "strong" } }
  },
  "instructions": "AGENT.md",
  "skills": ["daily-summary"]
}
```

```text
$ hub check <bundle> --allow-unsigned
  grants: capabilities {"glance", "storage"}, hosts {}, storage 16777216 bytes, agent read-only
```

唯一的拒绝项是模板缺少截图，用真实截图即可解决。系统应用 News、Photos、Maps、YouTube 和 Camera 声明的是一个更小的 Agent：

```json
"agent": { "profile": "read-only", "tools": ["ask_user_question"], "model": { "needs": ["tool_calling"] } }
```

Calendar 另外加了 `"instructions": "AGENT.md"`。Mail 另外加了其他应用的工具、`AGENT.md`、技能、`background` 和 `triggers.events: ["mail.messages.new"]`。配合 `"capabilities": ["storage", "glance"]`，这个更小的 Agent 得到同样的 `grants:` 行（**✓ 已运行**）。

| 字段 | 规则（App Hub `crates/app-contract/src/manifest.rs`、`crates/app-policy/src/policy.rs`） | 目前在哪里执行 |
| --- | --- | --- |
| `profile` | `read-only`、`workspace-write` 或 `workspace-write-never-ask`；没有完全访问权限 | 准入检查；Shell 不读取它（peer 的边界由它的工作区和已注册的工具决定） |
| `tools` | 通用宿主工具 `ledger.read ledger.write net.fetch storage.read storage.write card.render`（准入检查接受，但没有 Shell 实现），以及 octos 内核工具中的 `ask_user_question`（只允许这一个）；其他一律拒绝。**✓ 已运行**：`web_search` 得到 `[refused] agent: agent.tools names the octos kernel tool "web_search"; a contained app's agent may keep only ask_user_question` | 准入检查；Shell 把 `ask_user_question` 交给 peer |
| `max_iterations`、`token_budget` | 每次请求的模型轮数和 token 数，分别以 8 和 200,000 为上限（超出时取上限） | 准入检查（`grants:` 行只显示 profile） |
| `model.needs` | 取自 `tool_calling vision long_context reasoning structured_output multilingual` | 准入检查；应用有工具却没有 `tool_calling` 时会警告。尚未支持：Shell 不会据此挑选模型 |
| `model.tier` | `fast`、`standard`（默认）或 `strong` | 准入检查 |
| `model.local_only` | 对整个应用生效；数据不得离开用户的设备 | 准入检查（可共享的工具必须写明 `private_data: false`） |
| `model.per_task` | 命名任务 `[a-z_]{1,32}`，最多 8 个，由 `AGENT.md` 引用 | 准入检查 |
| 不写提供商或模型名称 | 准入检查拒绝未知键：``hub: manifest is not valid: unknown field `provider`, expected one of `needs`, `tier`, `local_only`, `per_task` ``（**✓ 已运行**） | 准入检查 |
| `background` | 申请在应用关闭时运行；必须同时有 `triggers` | 准入检查；Shell 为下面的 Gmail 事件唤醒商店应用的 Agent |
| `triggers.schedule` | 五段式 cron，本地时间，最多 16 个触发器 | 准入检查；尚未支持：没有 Shell 会按定时触发 |
| `triggers.events` | 应用自己宿主服务的事件，位于自己的命名空间（`news.items.new`） | 准入检查；Shell 投递 Gmail 服务的 `<namespace>.new_message` 和 Mail 自己的 `mail.messages.new`；其他事件尚未支持 |
| `instructions`、`skills` | `AGENT.md`（文本，最多 32 KiB，不含 HTML 脚本，不含 `#!`）；技能名 `[a-z0-9_-]{1,64}`，最多 16 个 | 准入检查；Shell 把两者作为每个回合的指导加载 |

**Gmail 事件。** 应用如果获得 `auth` 和 `gmail`，并写了 `background: true` 和 `triggers.events: ["<namespace>.new_message"]`（id 以 `.inbox` 结尾时为 `inbox.new_message`），那么当前连接的账户每收到一封新邮件，应用就得到一个回合。Shell 在前台运行或持有 Android 后台任务时，每 300 秒检查一次，并且只在用户允许该应用的 Agent 之后进行。第一次同步只建立基线，所以旧邮件不会唤醒任何东西。这个回合会告诉 Agent 邮件是不可信的输入；Agent 用自己的工具读取邮件，然后记录一个决定或发布一张卡片。只有回合完成、并且记录了决定或发布了卡片，事件才算处理完毕；否则它保持待处理。发送邮件都要用户在宿主中确认（`crates/shell/src/connected_events.rs`；未运行）。

**尚未支持：挑选模型。** 按 ADR 0002 §3，宿主应从用户的提供商中挑选满足 `needs` 和 `tier` 的模型；目前没有 Shell 这样做。

### `AGENT.md` 与技能

`AGENT.md` 描述 Agent 的角色：每个触发器发生时做什么、应用数据中什么重要、输出必须满足的评审标准，以及它的记忆规则。技能只包含数据：`skills/<name>/SKILL.md` 加一个 `manifest.json`，其中有 `name`（即目录名）、`version`、`description`、`uses`（每一项必须是应用自己的工具或在 `agent.tools` 中），以及可选的 `prompts.include`；只允许 `.md`、`.json` 和 `.txt` 文件；准入检查拒绝可执行字段（`tools`、`binaries`、`mcp_servers`、`hooks` 等）。

```json
{
  "name": "daily-summary",
  "version": "1.0.0",
  "description": "Write the short daily summary and put it on the glance screen.",
  "uses": ["summary.card.publish"]
}
```

准入检查拒绝 `uses` 中两者都不是的条目（**✓ 已运行**）：`[refused] skills: skill daily-summary uses summary.note.save, which is neither one of the app's tools nor in agent.tools`。

Shell 把已准入、经过摘要校验的 `AGENT.md` 和技能文字作为应用 Agent 每个回合的指导加载。它们不会安装为内核技能，也不授予任何工具。

## 应用的工具与 peer 工具

应用要写的部分现在就**可用**：应用包中的 `tools.json`，由 App Hub 准入检查校验（`crates/app-policy/src/agent.rs`）。下面这个工具通过共享的 `glance.publish` 方法，发布应用自己的卡片模板：

```json
{
  "schema": 1,
  "tools": [
    {
      "name": "summary.card.publish",
      "description": "Put today's summary on the glance screen, using the app's own card template.",
      "input_schema": {
        "type": "object",
        "properties": {
          "card_id": { "type": "string", "pattern": "^[a-z0-9-]{1,32}$" },
          "title": { "type": "string", "maxLength": 80 },
          "template": { "type": "string", "enum": ["summary-card.splash"] },
          "initial": { "type": "object" }
        },
        "required": ["card_id", "title", "template", "initial"],
        "additionalProperties": false
      },
      "output_schema": { "type": "object", "properties": { "card_id": { "type": "string" } } },
      "risk": "act",
      "private_data": true,
      "implemented_by": "host-service",
      "host_method": "glance.publish"
    }
  ]
}
```

- `name` 的形式是 `<namespace>.<tool>`；命名空间是**应用 id 的最后一段**（`dev.example.summary` → `summary`，`os.news` → `news`）。
- `input_schema` 和 `output_schema` 都必须提供（准入检查拒绝缺少 `output_schema` 的工具：``tools.json is not valid: missing field `output_schema` ``，**✓ 已运行**）。它们使用 JSON Schema 的一个子集（`type title description properties required items enum const default minimum maximum minLength maxLength minItems maxItems additionalProperties format pattern`）；输入必须是对象。最多 64 个工具，描述最长 1024 个字符。
- `implemented_by`：`host-service`（持有数据、网络或密钥的原生代码）或 `app`（应用自己的脚本）。Shell 以应用的身份在宿主服务上运行 `host-service` 工具，就像应用自己调用 `host.request` 一样，从不经由面板（`may_prompt: false`）。服务是工具的 `host_method` 指定的那个，没有时是它命名空间对应的那个（`news.list` → `news`）。该能力族必须已授予，或者是系统应用自己的命名空间（`os.calendar` → `calendar`）；否则返回 `<app> was not granted the <family> service`。商店应用的命名空间（例如 `summary`）不是能力，所以它的宿主服务工具只能通过 `host_method` 运行。准入检查接受 `app` 工具。`desktop-v0.1.0-beta.2` 拒绝对它的每次调用：`<tool> declares a script implementation, but this host does not support script tool dispatch`。OctoSense `main` 则在打开的完整应用中运行它，前提是清单声明了 `requires: ["script-tools-v1"]`（[HOST-API-V1 §5](HOST-API-V1.zh-CN.md#5-实现声明的应用工具)；OctoSense `crates/shell/src/host_tools/script_apps.rs`）。
- `host_method` 把普通应用的工具映射到一个经过 App Hub 审核的共享服务方法，例如上面的 `summary.card.publish` → `glance.publish`。App Hub 只接受 `SHARED_HOST_METHODS`（`crates/app-policy/src/agent.rs`）中的方法：`github`、`gcalendar` 和 `gmail` 的读取方法，`gmail.draft.open`、`gmail.draft.edit`、`gmail.event.decide`，以及 `glance.publish`、`glance.withdraw` 和 `glance.list`。这样的工具必须申请该方法的能力、声明 `private_data: true`，并且风险不低于该方法的要求。提供商写入、宿主确认面板上的批准和账户变更都不能作为别名。对 `github`、`gcalendar` 和 `gmail`，Shell 会把应用当前连接的账户加入参数。
- 发布速览卡片的 Agent 工具只应接受 `template` + `initial`（如上），或 L0 的 `source` + `data`，不要接受 `script`：脚本卡片按应用自己的策略运行，回合一旦受输入误导，就可能发布任意代码。`desktop-v0.1.0-beta.2` 会发布工具接受的任何卡片；OctoSense `main` 则拒绝 Agent 工具传来的 `script`（见[谁可以发布](#谁可以发布)）。
- `background`、`shareable`、`private_data`、`confirm`、`outward`、`auto_approvable`：见[审批：`risk` 与 `confirm`](#审批risk-与-confirm)。
- Shell 的转发层用 `input_schema` 校验每次调用的参数（最多 64 KiB），用 `output_schema` 校验结果（最多 256 KiB）。octos 要求 `output_schema` 是对象，所以返回裸数组的工具不能原样提供。

Shell 通过 octos 的 peer 工具协议把这些工具注册到应用的 peer；应用从不直接调用这个协议。模型看到的 `summary.card.publish` 名为 `summary_card_publish`，每次调用默认超过 30 秒即超时。要在 Shell 中追踪一次调用，见 OctoSense 的[架构导读 § 7. 把工具追到 Rust 代码](https://github.com/OctoSense-org/OctoSense/blob/main/docs/architecture-walkthrough.zh-CN.md#7-把工具追到-rust-代码)。

### 审批：`risk` 与 `confirm`

一次调用是否需要用户同意取决于 `risk` 和 `outward`；由谁的界面来询问取决于 `confirm`；常设规则能否替用户批准取决于 `auto_approvable`（App Hub PUBLISHING）：

| `risk` | 运行方式 |
| --- | --- |
| `read`（只查看）、`act`（修改应用自己的状态） | 无人值守运行 |
| `destructive`（发送、发帖、分享、购买、删除） | 只在用户批准后运行 |
| `act` 且 `outward: true`（到达设备之外） | 只在用户批准后运行，与 destructive 工具相同 |

- `read` 工具写了 `outward: true`，准入检查会拒绝（**✓ 已运行**）：`[refused] tools: summary.card.share is outward but its risk is read: a call that reaches outside the device is at least act`。`act` 工具写了它，准入检查会警告：`[warning] tools: summary.card.share is outward: every call waits for the host's approval`。
- 准入检查对每个 destructive 工具都会警告（**✓ 已运行**）：`[warning] tools: summary.card.publish is destructive: every call waits for the host's approval`。
- `auto_approvable: false`（默认 `true`）：任何常设规则（“一小时内允许”）都不能批准它，每次调用都需要用户当场同意。用于永久删除、付款、分享到设备之外、账户和安全设置的变更。Shell 取它自己的规则和工具声明中更严格的那一个。

| `risk: "destructive"` 且 | 用户在场 | 用户不在场 |
| --- | --- | --- |
| `confirm: "host"`（默认） | 由 Shell 的审批面板询问 | 调用作为一条审批请求，在 Shell 的面板上等待 |
| `confirm: "app"` | 应用自己的确认面板是唯一的确认 | 调用作为一条审批请求，在 Shell 的面板上等待 |

商店应用尚未支持 `confirm: "app"`：准入检查只允许 `implemented_by: "app"` 的工具（或原生模块的工具）使用它。`desktop-v0.1.0-beta.2` 拒绝执行这类工具；OctoSense `main` 则拒绝需要应用自己确认的脚本工具调用：`Script tools require host confirmation; confirm: app is not supported by this ABI`。宿主服务工具写了它，准入检查会拒绝（**✓ 已运行**）：`[refused] tools: summary.card.publish says confirm "app" but is implemented by the host service: …`。

后台工具应只做读取，以及用户在任何内容离开设备之前确认过的写入：后台回合处理的是不可信的输入，例如收到的邮件。

商店会根据清单和 `tools.json`，为每一项后果给用户显示一行说明，例如“Its assistant may work while the app is closed, on a schedule; only if you allow it, and you can turn it off.”和“Can ask to mail.send: nothing of this runs until you approve it.”

### 各部分在哪里执行

| 部分 | 状态 |
| --- | --- |
| 声明（字段、大小、名称、schema、risk、confirm） | **可用**：App Hub 准入检查会拒绝或警告 |
| 运行时审批（内核）：批准或拒绝 | **可用**：内核一侧和 Shell 的审批面板，面板提供 Once、Always 和 Deny 三个按钮；审批留在这些面板上，而不是在应用的对话中 |
| Shell 的审批路由（`crates/shell/src/approvals/`） | **可用**：依次是开发者模式、`confirm: "app"`（所属应用的面板）、`auto_approvable: false`（总是由用户决定）、用户的常设规则，最后是当场弹出的面板。规则的条件在读不懂参数时一律不通过；每一行参数都显示过之后，批准按钮才可用 |
| 每次工具调用的审计 | **可用**：每次调用在到达和结束时各记录一次，包括调用者、所属应用、工具和参数的 SHA-256（从不记录参数本身），写入 Shell 主目录下的 `logs/tool-calls.jsonl` |
| 在应用内与应用的 Agent 对话 | 在 Shell 的“Ask &lt;app&gt;”对话栏和速览卡片的 `sys.chat` 中**可用** |
| `app/<app>/acct-<hash>` 中的记忆，按账户保存并随账户清除 | **可用**；按规则提升**尚未支持**（ADR 0002 §9）。没有对应的清单字段；记忆规则写在 `AGENT.md` 的文字里 |
| 系统 Agent 的覆盖层 | **尚未支持**（ADR 0002 §11） |

## 系统工具箱

工具箱让应用的 Agent 通过宿主搜索和阅读网页，范围由清单顶层的 `research` 对象限定。`research` 提供 `workflow.run`、`workflow.fork`、`toolbox.search` 和 `toolbox.web_read`；`crawl` 在范围中 `max_depth` 和 `max_pages` 大于 0 时提供 `toolbox.deep_crawl`。Agent 从不自己抓取网页：宿主按应用的范围和预算执行每次调用，保存来源记录，并把结果写在应用无法伪造的位置。

- **商店应用尚未支持。** Shell 只把工具箱授予声明了它的系统应用（`os.*`），并且只在启用了 `toolbox-peers` 构建特性的版本中（手机端默认启用，桌面端没有）（[OctoSense#64](https://github.com/OctoSense-org/OctoSense/issues/64)）。没有系统应用声明 `research`。
- 声明了 `research` 的商店应用仍必须带上顶层的 `research` 范围对象，否则准入检查会拒绝（**✓ 已运行**）：`[refused] policy: app dev.example.summary requests research but declares no research scope; add a top-level "research" object (octos's scope; {} means no limits)`。

范围的字段见 App Hub [PUBLISHING § research 范围](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md#research-范围)。模板和工具见 OctoSense [`docs/ai-services.zh-CN.md` § 系统工具箱](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.zh-CN.md#系统工具箱)。

## 发布到速览栏

### `glance.publish`、`glance.withdraw`、`glance.list`

速览栏在手机上显示为速览信息流。它的服务在 OctoSense `main` 上**可用**（`crates/shell/src/glance.rs`）：

| 方法 | 参数 | 返回 |
| --- | --- | --- |
| `glance.publish` | `{card_id, source \| script \| template, data?, initial?, title, summary?, priority?, expires?, open?: {app, route?}, notify?, viewport?}` | `{card_id, replaced, expires_at}` |
| `glance.withdraw` | `{card_id}` | `{withdrawn}` |
| `glance.list` | – | `[{card_id, title, priority, published_at, expires_at}]`，只包含调用者自己的卡片 |
| `glance.take_open` | – | `{route}`：用户最近为这个应用打开的卡片的 `open.route`，只返回一次。只供前台的应用调用 |

- 三者选一：
  - `source`，一张 **L0 卡片**（头部声明时可以是 L1；不接受 L2），按 `data`（从卡片数据源名称到值的映射）实例化，并在保存前经过 Card runner 的流水线转换（lowering）。`sys.chat` 数据源必须写明发布卡片的应用（见[卡片内对话](#ai-撰写的文字与卡片内对话model-copysyschat)）。
  - `script`，一个 **Splash 程序**，与脚本应用的 `main.splash` 是同一种东西（有自己的状态、处理函数、`host.request` 调用和存储），不带 `data`：这是可交互的卡片（回复框、表单）。
  - `template`，应用自己已准入的应用包根目录下某个 `.splash` 文件的名字（`[A-Za-z0-9._-]`，最多 96 个字符），配合 `initial`，即模板起始用的 JSON 对象（最多 32 KiB）。宿主把 `initial.connection` 设为应用当前连接的账户（没有账户的应用为 `device`），并把卡片保存为可交互的脚本卡片，所以模板和 `initial` 合起来不能超过 `script` 的 16 KiB 上限。
- 脚本卡片和模板卡片按发布应用自己的策略运行。
- `notify: true` 还会发出一条通知（手机的通知栏、桌面端的 toast）；`summary`（最多 200 个字符）是通知的第二行。在桌面端点击 toast 会在卡片窗口中打开这张卡片；新卡片还会打开速览栏。
- **限制：** `card_id` 为 1–64 个 `[A-Za-z0-9._-]` 字符；`title` 最多 80 个字符；`source`（或 `script`）最多 16 KiB；`data` 按 JSON 计最多 32 KiB；`priority` 0–100（默认 50）；`expires` 60 秒到 7 天（默认 24 小时）；每个应用每分钟最多发布 6 次（替换和 L0 检查拒绝的卡片都计数）。卡片按字节预算保存：每个应用 8 MiB，总共 32 MiB；空间不够时，宿主先移除较旧、优先级较低的卡片。速览栏和手机的速览信息流会滚动显示所有保留下来的卡片。
- **身份：** 发布者就是调用者，永远不是参数；用相同的 `card_id` 发布会替换原卡片；`open.app` 必须是调用者自己的应用。点击卡片会在卡片窗口中打开它（手机上是一个展开的工作区）。桌面速览栏上的打开按钮，或卡片中的 `sys.link`，会打开应用；应用再用 `glance.take_open` 读取卡片的 `open.route`。
- 信息流中的每张卡片在自己的隔离环境中运行，遵循发布它的应用的策略（原生应用的卡片不受应用策略约束）。它是后台界面：它调用的宿主服务不能在那里弹出面板（`may_prompt: false`），卡片消失时，宿主会取消它还在等待的请求。在前台打开的卡片可以弹出宿主面板，与应用本身一样。

### 谁可以发布

- **任何获得 `glance` 授权的隔离应用**都可以发布、列出和撤回自己的卡片。系统应用没有例外。拒绝时返回：`<app> was not granted the glance capability`。
- 商店应用从自己的脚本发布，或通过用 `host_method` 映射到 `glance.publish` 的 Agent 工具发布；两种方式都需要 `glance` 授权。
- **Agent 能发布什么取决于版本。** 在 `desktop-v0.1.0-beta.2` 上，Agent 工具可以发布全部三种卡片。OctoSense `main`（尚未进入任何发布版本）会在执行前检查每个最终调用 `glance.publish` 的 Agent 请求：`script` 一律拒绝，并返回 `Agents cannot publish executable Splash; choose an admitted template with initial data, or L0 source`；模板卡片必须提供模板名和 `initial` 对象，不能带 `source` 或 `data`；`source` 必须是有效的 L0，不能含可执行代码或 L1 表达式。应用自己的脚本仍可以发布全部三种卡片。
- 原生模块也可以发布，系统应用的宿主服务也会替它们的应用 Agent 发布。Calendar 的 `calendar.notify` 和 `calendar.agenda` 会填好服务随附的固定 L0 卡片，其他每个系统应用的 `<namespace>.notify`，包括 Mail 和 News 的，都会填好 Shell 的通知卡片（`crates/shell/src/glance_notice.rs`）。Mail 的 `mail.publish_card` 发布模型撰写的卡片，仅限 L0。

应用中的调用如下（格式取自 `glance.rs`；未运行，因为 `card-host` 不注册任何宿主服务）：

```splash
host.request("glance.publish", {
    card_id: "morning"
    title: "Morning summary"
    source: card_source
    data: {}
    expires: 43200
}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) }
})
```

只有真正发布卡片的应用才申请 `glance`；商店显示“Show cards on your glance screen”。

## 绑定到结果的卡片：`sys.digest`

L0 数据源**可用**：Shell 的运行时和本仓库的锁定版本（OctoScript `2e37d9e6`）都能检查它，Shell 在卡片发布时解析它（`crates/shell/src/glance_digest.rs`）。摘要的 `summary` 以及要点的 `text` 和 `label` 是模型文字，显示时标为 AI 撰写（见[下文](#ai-撰写的文字与卡片内对话model-copysyschat)）。

商店应用尚未支持：宿主只用应用自己的研究运行结果填充摘要，而商店应用没有工具箱（见[上文](#系统工具箱)），所以商店应用的摘要始终解析为空记录。

L0 的“不写事实”规则禁止卡片把发现的内容当作自己的文字，所以这些发现变成由宿主解析的数据源：

```text
source brief sys.digest(app: "os.news", id: "glance",
                        fields: [topic, summary, points, sources, id, text, cite, n, title, source])
```

- `app` 是字面量，必须是发布卡片的应用；卡片写了别的应用，宿主会拒绝。`id` 是字面量（`[A-Za-z0-9_-]{1,64}`，与工具箱的 run-id 字符集相同）或指向状态的路径。
- 记录包含：`status`（`ready partial failed missing expired`）、`topic`、`language`、`summary`、`retrieved_at`、`count`、`points`（`{id, text, label, cite, citations}`）和 `sources`（`{id, n, title, source, url, published_at}`）。
- **链接只来自 `sources`**，即宿主取回过的内容；宿主丢弃含 URL 的文字。摘要缺失、过期或格式错误时解析为一条空记录，`$state` 为 `.failed`，而不是报错，这样卡片会显示它自己的“暂无内容”文案。
- 宿主读取该应用最新的 `toolbox/runs/<template>/<id>.json`（位于宿主目录下、应用的隔离目录之外），只保留运行时宿主记录的来源，限制文字长度（概要 800 个字符，8 条要点每条 400 个字符，8 个来源），并在运行开始 48 小时后让摘要过期；卡片的过期时间不晚于摘要。

完整的卡片见 OctoSense 的 [`crates/shell/resources/glance/news-brief.card`](https://github.com/OctoSense-org/OctoSense/blob/main/crates/shell/resources/glance/news-brief.card)。

## AI 撰写的文字与卡片内对话：`model-copy`、`sys.chat`

在 OctoSense Shell 中**可用**：L0 规则见 OctoScript 的 [`docs/ui-profile-l0.md`](https://github.com/OctoSense-org/OctoScript/blob/main/docs/ui-profile-l0.md) §4.2 和 §5.15，kit 中的标记在 OctoScript-Makepad 中，宿主一侧在 OctoSense 中（`crates/l0-chat`、`crates/shell/src/glance_chat.rs`）。本仓库锁定的运行时有相同的检查器和标记（见[测试](#测试)）。

L0 对模型文字有两条规则：一条管文字，一条管动作。

**文字：模型写的文字可以填入文本槽，并标为 AI 撰写。** 模型文字包括：声明为 `class: model-copy` 的 `copy`（`copy gist { class: model-copy, en: "Rates held." }`）、宿主数据源中由模型写的字段（`sys.digest` 的 `summary` 以及要点的 `text`/`label`，`sys.chat` 条目的 `text`，`sys.mail_draft` 的 `to`、`subject`、`body` 和 `suggestion_body`），以及写入了这类文字的 `text` 状态（草稿：`event use { draft: set(copy.suggestion) }`）。文本槽是 `TextHero`、`TextTitle`、`TextBody`、`TextRow`、`TextEyebrow`、`TextCaption`、`Band`、`Bubble`、`ChatEntry` 和 `Field` 的 `text` 参数；chip、磁贴和标签页的标签、头像、图标和占位文字都不是。kit 会在文字上方画一个小的闪光图标和 `AI` 眉题，颜色与文字本身相同；文字仍是纯文本（没有 Markdown、HTML 或链接）。

**动作：模型写的文字从不决定运行什么。** 它不能作为动作的载荷或目标、数据源参数、条件、循环键、控件标签、组件属性、状态初值，也不能写入宿主存储。检查器默认拒绝：除文本槽外的每个位置都不接受它。

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

- `app` 是字面量，必须是**发布卡片的应用**：写了别的应用的卡片，Shell 拒绝发布；这样的卡片读到的是 `unavailable` 的对话记录，也写不进任何东西。`thread` 是 `[A-Za-z0-9_-]{1,64}` 或指向状态的路径。
- 数据源返回 `status`、`count` 和 `entries`，每行为 `{id, role, text, at}`；`role` 为 `user`、`model` 或 `host`（一条通知）。`ChatEntry(text: m.text, role: m.role)` 按角色在对应一侧画出气泡；两个参数必须来自同一行，只有 `model` 条目标为 AI 撰写。
- **对话记录属于宿主。** 卡片 `data` 中放在该数据源名下的任何内容，宿主都会换成自己的对话记录。卡片唯一的写入是 `append`，只接受用户在 `Field` 中输入的内容，并记为一条 `user` 条目；然后宿主在应用的对话（用户通道）中运行一个回合，把回复作为 `model` 条目追加；如果应用没有 Agent，或用户还没有允许它，则追加一条 `host` 通知（`<app> has no agent to answer here yet.`）。卡片永远无法写入 `model` 条目。
- **限制**（`crates/l0-chat/src/lib.rs`）：去掉首尾空白后每条消息最多 4 KiB，每个会话每 2 秒最多一条、Agent 回答期间不接受新消息，保留最近 200 条，回复超出 16 KiB 的部分会截掉。
- **存储**：每个会话一个只有所有者可读写的文件，位于应用的账户文件夹 `apps/<app>/accounts/<account hash>/chat/<thread>.json`，这同时也是 Agent 的工作区，所以 Agent 能读到它参与的对话记录。
- **在哪里得到回答**：桌面端的卡片窗口（由卡片通知打开的那个窗口；`glance_sheet.rs`）、桌面速览栏中的在线卡片，以及手机上展开的工作区，都由同一条在线卡片路径回答；手机的速览信息流只显示概要。AppCard 是需要单独启用、会生成在线卡片的原生应用，它在自己的 L0 卡片中用一条 `host` 通知回答。App Hub 的 Card runner 不回答 `sys.chat`，所以卡片应用自己的 `page.card` 暂时不能使用它（在 App Hub `crates/` 中找不到）。

想用它的商店应用，用 `glance.publish`（`source`）发布一张写着自己 id 的这类卡片，并声明一个 Agent，好让用户能够允许它。

## 卡片级别与渲染评审

级别定义在 OctoScript 的 [`docs/ui-profile-l0.md`](https://github.com/OctoSense-org/OctoScript/blob/main/docs/ui-profile-l0.md)：

| 级别 | 允许的内容 | 用于 AI 输出 |
| --- | --- | --- |
| **L0** | 只有 UI 声明：数据来自宿主解析的、已登记的 `sys.*` 数据源，没有表达式，没有调用 | 生成卡片和速览卡片的默认级别 |
| **L1** | L0 加上算术表达式，用 `# level: L1` 头部声明 | 只在需要算术时使用 |
| **L2** | 命令式 Splash（`ui.<id>.set_*`） | 生成的卡片不允许；脚本应用的 `main.splash` 就是这一级 |

本仓库中的 L0 卡片示例：[docs/l0/](l0/)。

**渲染与评审**（**可用**，App Hub `main`，`crates/card-studio`；octos 技能 `skills/card-studio`，工具 `card_render` 和 `card_critique_payload`）：在隐藏的 `card-host --remote` 中按目标尺寸渲染卡片，运行可测量的检查（文字截断、放不下、数据源失败、lint、转换），再按评审标准生成一个视觉评审请求。取自 App Hub 的 [DEVELOPMENT.zh-CN.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/DEVELOPMENT.zh-CN.md#发布前检查卡片card-studio)（未运行）：

```sh
cargo build --release -p octosense-card-host -p octosense-card-studio
export CARD_STUDIO_KIT=../octoscript-makepad/components/l0
target/release/card-studio render --card news.card --data digest.json \
    --size glance --size phone --size desktop --out out/
target/release/card-studio critique --report out/report.json --rubric AGENT-rubric.md --inline > request.json
```

也可以手动使用同一套工具：`card-host … --remote`（或 `MAKEPAD_REMOTE=<port>`），然后用 `/snap` 读取控件文字和矩形，`/g` 抓取一帧（`/g?raw=1` 得到 PNG 字节），`/d` 查看控件树，以及 `/log` 和 `/quit`。`tools/octo run --hidden` 和 `tools/octo shot` 为应用包封装了这些操作（README，[无头测试](../README.zh-CN.md#无头测试同时测多个应用不占屏幕)）。

尚未支持：由应用的 Agent 自己运行这一循环。

## 来源

- OctoSense `main`：`AGENTS.md`；`docs/ai-services.md`；`docs/adr/0002-event-driven-app-agents.md`、ADR 0004、ADR 0005 和 `docs/adr/home/0004-system-apps-are-contained-script-apps.md`；`crates/app-peers`（`README.md`、`src/broker.rs`）；`crates/ai-host/src/`（`lib.rs`、`contained.rs`、`native_agents.rs`、`toolbox_peers.rs`）；`crates/shell/src/`（`agents.rs`、`apps.rs`、`agent_events.rs`、`connected_events.rs`、`questions/`、`approvals/`、`app_chat/`、带有 `script_apps.rs`、`files.rs` 和 `relay.rs` 的 `host_tools/`、`glance.rs`、`glance_card.rs`、`glance_chat.rs`、`glance_digest.rs`、`glance_notice.rs`、`glance_routes.rs`）；`crates/l0-chat`；`crates/toolbox`；`apps/ai-providers/host-service`、`apps/news/host-service`、`apps/mail/host-service`、`apps/calendar/host-service`；`apps/*/bundle/`。
- OctoSense-App-Hub `main`：`crates/app-contract/src/manifest.rs` 和 `policy.rs`；`crates/app-policy/src/services.rs`、`agent.rs`、`policy.rs`、`listing.rs`；`crates/appstore/src/services.rs`；`docs/PUBLISHING.md`；`docs/DEVELOPMENT.md`。
- Shell 锁定版本的 OctoScript：`docs/ui-profile-l0.md` §4.2、§5.14 和 §5.15；`crates/octoscript-ui-l0/tests/fixtures/chat.card`。
- OctoSense 锁定版本的 octos：`docs/OCTOS_UI_PROTOCOL_CHANGE_REQUEST_UPCR_2026_035_PEER_HOST_TOOLS.md`。
- Rinx：`src/host/octos.rs`。
