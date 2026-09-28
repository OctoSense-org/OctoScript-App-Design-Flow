# 应用中的 AI：OctoSense 的助手

[English](AI-SERVICES.md) | 简体中文

用本仓库开发的脚本应用如何使用 OctoSense 内部的助手（Shell 运行的 octos Agent 内核）、
目前哪些可用、哪些还在规划中。本文描述 2026-09-27 的状态：App Hub `main` 为 `e8601b8`，
OctoSense `main` 为 `405139f`（它锁定 App Hub `46d67e51` 和 octos `a6ea8505`）。

> **开发应用不需要任何 AI。** 本仓库中没有任何东西会调用模型或需要 API key，你可以使用
> 任何编程 Agent（Codex、Claude Code、Cursor、Gemini CLI、GitHub Copilot 等），也可以
> 不用。本文只讨论你*完成后的应用*在设备上可以请求的助手。

面向 Shell 和原生模块开发者的详细版本：
[OctoSense `docs/ai-services.zh-CN.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.zh-CN.md)。

## 目录

- [简短回答](#简短回答)
- [助手的构成](#助手的构成)
- [助手相关权限](#助手相关权限)
- [最小调用示例与“不可用”状态](#最小调用示例与不可用状态)
- [用户看到什么](#用户看到什么)
- [错误](#错误)
- [测试](#测试)
- [即将到来：一次性模型调用（`model`）](#即将到来一次性模型调用model)
- [尚不可用的内容与规划路线](#尚不可用的内容与规划路线)

## 简短回答

**目前，商店应用在 OctoSense 设备上还不能向模型或助手提出任何请求。** 没有任何
OctoSense Shell 向隔离运行的应用提供助手请求，`card-host` 也不提供任何宿主服务。请把
应用做成不依赖 AI 也完整可用。

| 你尝试 | 目前的结果 |
| --- | --- |
| 声明 `octos.turn.start`（及同组权限）并调用 | 准入检查接受这些名称。调用返回 `no service answers "octos" on this device`，在 `card-host` 和 OctoSense Shell 中都一样（已在 `card-host` 中验证，见下文）。 |
| 声明 `model` 并调用 `model.complete` | 准入检查接受它（App Hub [#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24)，已合并）：一次性模型调用**即将到来**。OctoSense 的 `model` 服务尚未实现，所以调用返回 `no service answers "model" on this device`（已在 `card-host` 中验证）。见[即将到来：一次性模型调用](#即将到来一次性模型调用model)。 |
| 声明 `llm` | 准入检查接受它，但 `llm` 服务用于管理设备的 AI 提供方（没有发送提示词的方法），并且只响应 `os.*` 系统应用：`llm is for OctoSense's own apps.`。不要申请它。 |
| 在 `manifest.json` 中声明 `agent` | 准入检查接受并按上限裁剪；**没有任何地方运行它**。 |
| 附带 `tools.json`、`AGENT.md`、`skills/` | App Hub `main` 接受；**目前没有任何 Shell 加载它们**，而且 Shell 锁定的较旧 App Hub 会拒绝使用新 `agent` 字段的 manifest（见[下文](#尚不可用的内容与规划路线)）。 |
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
- **应用 peer。** 获得助手授权的应用会得到自己的 octos peer：私有的会话上下文、工作区和
  记忆（`app/<app>/acct-<hash>`），归 Shell 的系统 Agent 所有。应用拿到的是一个受限的
  服务，永远拿不到内核、提供方或密钥。
- **审批属于用户，并且在发起请求的应用中进行。** 系统 Agent 从不替应用审批。

目前只有 Shell 信任的**原生模块**会得到 peer（Matrix 客户端 Rinx）。脚本应用在下文的
规划中才会得到。

## 助手相关权限

四个精确名称，每个都是单独的授权（App Hub 的 `KNOWN_CAPABILITIES`，
`crates/app-policy/src/services.rs`）。前缀不授予任何权限：`octos.` 或 `octos.admin`
会被准入检查拒绝。

| 权限 | 调用 | 参数 | 返回（`r.data`） | 商店显示 |
| --- | --- | --- | --- | --- |
| `octos.session.open` | `octos.session.open` | `{}` | `{open: true, model: {lane, provider, model} 或 nil}` | Open its own conversation with the assistant |
| `octos.session.history` | `octos.session.history` | `{}` | 会话内容，`{session_id, messages: [...], …}` | Read its own conversations with the assistant |
| `octos.turn.start` | `octos.turn.start` | `{text}`（1 字节到 32 KiB） | 回合结束后的 `{turn_id, text}`，即回复 | Ask the assistant to work for it, using the device's AI settings |
| `octos.turn.interrupt` | `octos.turn.interrupt` | `{}` | 停止正在运行的回合 | Stop assistant work it started |

参数和返回的形状取自目前唯一提供这些名称的宿主：Rinx 的迷你应用宿主
（[hagency-org/Rinx](https://github.com/hagency-org/Rinx) 中的 `src/host/octos.rs`，
底层是 OctoSense 的 `crates/app-peers`）。其他参数会被拒绝（`Unsupported Octos
arguments`）：应用只提供文本，从不提供会话、配置、提供方、模型或审批决定。每个应用实例
同一时间只运行一个回合，一个回合 180 秒后放弃。

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

OctoSense Shell 使用同一份 App Hub 分发代码，同样没有注册 `octos` 服务（它们注册的是
`mail`、`llm`、`news` 和 `glance`），所以商店应用在那里得到的也是 `no service answers`。

**现在应该发布这个功能吗？** 只有在应用不依赖它也完整可用时才可以。审核者会问界面上
用不到的授权（`hub scan`），每个 `octos.*` 都会出现在商店的权限列表中。如果保留这个调用，
请在商店说明和你的报告中写明：在目前的设备上它不起作用。

## 用户看到什么

- **安装前**：每个权限一行说明（见上表），隐私摘要中写着 "Asks the device's assistant
  to work for it; the assistant's keys stay with the device."（申请 `octos.turn.start`
  时），或 "Opens or reads its own conversations with the device's assistant, but
  cannot ask it to work."（只申请 open 或 history 时）。
- **密钥和提供方**只在 AI providers 中、在宿主面板上设置：桌面端为 Start → Settings →
  AI providers，手机上为 OctoSense Settings → Accounts → AI providers。
- 助手发起的**工具审批**交给用户，在发起请求的应用中、用宿主自己的控件进行（目前这个宿主
  是 Rinx）；系统 Agent 从不回答审批。脚本应用无法审批任何东西：没有任何参数能携带审批决定。

## 错误

| `r.error` | 含义 | 应用该怎么做 |
| --- | --- | --- |
| `this app was not granted "octos", which "<service>" needs` | manifest 中没有列出这个精确名称 | 把它加入 `capabilities`，或删除该调用 |
| `no service answers "octos" on this device` | 当前宿主不向应用提供助手（目前：所有 OctoSense Shell 和 `card-host`） | 显示“不可用”，继续工作 |
| `no service answers "model" on this device` | 当前宿主没有 `model` 服务（目前：所有 OctoSense Shell 和 `card-host`） | 同上 |
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
  [`docs/ai-services.zh-CN.md` § 本地运行与测试](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.zh-CN.md#本地运行与测试)；
  目前你的应用在那里得到的仍是 `no service answers "octos"`。
- **目前唯一会响应的宿主**是 Rinx 的迷你应用宿主，适用于用户审核后导入 Rinx 的应用包
  （需要登录 Matrix，使用 Rinx 自己的助手 peer）：
  [Rinx `examples/miniapps`](https://github.com/hagency-org/Rinx/tree/main/examples/miniapps)。
  这不是 App Hub 的安装路径，并且它会拒绝声明了 `agent` 的应用包。本文未重新运行这一路径。

## 即将到来：一次性模型调用（`model`）

App Hub `main` 接受第二条更窄的路径
（[App-Hub#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24)，已合并）：
`model` 权限，对应 Shell 的 `model` 宿主服务。以下按 App Hub 的描述（OctoSense 一侧的服务
还是一个尚未提交的 PR，所以目前都不会运行）：

- `host.request("model.complete", {task, input, schema, class}, fn(r){…})`，`class`
  为 `fast` 或 `strong`。宿主从用户自己的 AI 提供方中挑选模型；应用永远看不到提供方、
  模型 id 或密钥。
- 一次性：没有工具、没有记忆，除 `input` 外没有历史。回复必须符合应用的 JSON Schema
  （有大小上限）；除非应用明确要求，回复中的 URL 会被拒绝。每个应用有每日的调用次数和
  token 预算，由宿主管理。
- 商店显示 "Send what you give it to the AI provider you configured, within a daily
  budget"；隐私摘要显示 "Sends what you give it to the AI provider you configured, for
  one-off answers within a daily budget; it never sees your API keys."

目前准入检查会通过（`grants: capabilities {"model"}`），而每次调用都返回
`no service answers "model" on this device`（在 App Hub `e8601b8` 的 `card-host` 中运行）。
Shell 锁定的 App Hub（`46d67e51`）不认识这个名称，所以目前的 Shell 会拒绝申请它的
manifest。确切的返回形状和错误文字要等 OctoSense 服务实现后才确定；在此之前不要依赖上述
字段以外的任何内容。

## 尚不可用的内容与规划路线

| 尚不可用 | 规划路线 | 状态 |
| --- | --- | --- |
| OctoSense 中隔离运行的应用发起助手请求 | Shell 给应用分配 peer 并提供服务，与原生模块相同 | 规划中：OctoSense [ADR 0002](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0002-event-driven-app-agents.md)（Proposed），先从 News 开始（[#61](https://github.com/OctoSense-org/OctoSense/issues/61)） |
| 直接访问内核、选择提供方或模型 | 永远不会：应用声明模型**需求**（`agent.model`：needs、tier、`local_only`），由宿主从用户的提供方中挑选 | App Hub 已接受（[App-Hub#18](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/18)）；尚未运行 |
| 应用自己的 Agent 和工具 | `tools.json`（名为 `<app>.<tool>` 的类型化工具，`risk` 为 read/act/destructive，`confirm` 为 host/app）、`AGENT.md`、只含数据的 `skills/`，以及 manifest 中的 `background` 和 `triggers`，由 App Hub 接受并锁定 | App Hub `main` 会检查它们（[PUBLISHING § The app's agent and tools](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-apps-agent-and-tools)）。内核一侧（[octos#2567](https://github.com/octos-org/octos/pull/2567)）尚未合并，也没有任何 Shell 注册或运行它们。 |
| 一次性模型调用 | 使用 `model` 权限调用 `model.complete` | 权限已合入 App Hub（[#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24)）；OctoSense 服务尚未实现 |
| 在 glance 屏幕上显示卡片 | 使用 `glance` 权限调用 `glance.publish` | 服务已合入 OctoSense（[#72](https://github.com/OctoSense-org/OctoSense/pull/72)），但只服务 `os.*` 应用；该权限已在 App Hub `main`（[App-Hub#22](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/22)），Shell 一侧正在进行（[#86](https://github.com/OctoSense-org/OctoSense/pull/86)） |

**需要知道的版本差异。** `tools/octo check` 运行的是本仓库旁边的 App Hub 检出
（`main`）。OctoSense Shell 仍锁定 App Hub `46d67e51`，它早于 `glance`、`news`、`model` 权限和新的
`agent` 字段（`model`、`background`、`triggers`、`instructions`、`skills`）。manifest 会
拒绝未知字段，所以使用了其中任何一项的应用包能通过 `octo check`，却会被目前的 Shell 拒绝。
想现在就在 OctoSense 中打开的应用包，请不要使用它们。较旧的 App Hub 是否接受带有
`tools.json`、`AGENT.md` 或 `skills/` 的应用包尚未测试，而且在那里也没有任何东西会用到它们。

如果想提前准备，可以参照 App Hub 的 News 示例
（[`crates/app-policy/tests/fixtures/news-agent`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/crates/app-policy/tests/fixtures/news-agent)），
在 `bundle/` 之外起草 `tools.json` 和 `AGENT.md`。
