# 应用中的 AI：OctoSense 的助手

[English](AI-SERVICES.md) | 简体中文

用本仓库开发的脚本应用如何使用 OctoSense 内部的助手（Shell 运行的 octos Agent 内核）、
目前哪些可用、哪些还在规划中。本文描述 2026-09-30 的状态：App Hub `main` 为 `0f33211`，
OctoSense `main` 为 `7082ff5`（它锁定 App Hub `0f332112`）。自本文初稿（2026-09-27）以来，
Shell 增加了 `model` 服务、在首次使用征得同意后向隔离应用提供的 `octos` 服务、面向所有获得
授权的应用的 `glance`，以及为每个声明了 Agent 的应用提供的 Agent（一个 peer 和一个
“Ask <app>”面板）。Shell 一侧的说明见 OctoSense 的
[`docs/ai-services.zh-CN.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.zh-CN.md)
和 [`docs/architecture.zh-CN.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/architecture.zh-CN.md)。

后面几节介绍正在其上构建的内容：在应用包中声明应用自己的 Agent、它提供的工具、系统工具箱、
发布到 glance 屏幕、`sys.digest` 卡片，以及 News 的端到端流程。那里的每项功能都标为
**可用**（已合入所列仓库的 `main`，可按描述使用）或**即将推出**（在所列的未合并 PR 中，
或只存在于 ADR 中：展示的形状在合入前可能变化，暂时不要让提交依赖它）。标为 **✓ 已运行**
的命令在 2026-09-27 为本文实际运行过（macOS，Apple silicon）；其他命令均引自所列来源，并
标明未运行。2026-09-30 的更新引自所列 PR 和代码，未运行。

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
- [一次性模型调用（`model`）](#一次性模型调用model)
- [状态一览](#状态一览)
- [应用自己的 Agent](#应用自己的-agent)
- [应用的工具与 peer 工具](#应用的工具与-peer-工具)
- [系统工具箱](#系统工具箱)
- [发布到 glance 屏幕](#发布到-glance-屏幕)
- [绑定到结果的卡片：`sys.digest`](#绑定到结果的卡片sysdigest)
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
| 在 `manifest.json` 中声明 `agent` | 准入检查接受并按上限裁剪。用户允许后，Shell 为应用分配自己的 peer，用户可以在 Shell 的“Ask <app>”面板中与它对话（[OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)）。根据 `needs` 选择模型、触发器和后台运行仍**即将推出**（见[应用自己的 Agent](#应用自己的-agent)）。 |
| 附带 `tools.json`、`AGENT.md`、`skills/` | 准入检查接受。Shell 把应用包中的工具注册到应用的 peer，并转发对它们的调用（[OctoSense#145](https://github.com/OctoSense-org/OctoSense/pull/145)、[#184](https://github.com/OctoSense-org/OctoSense/pull/184)）；`AGENT.md` 和技能还不会装进 peer。 |
| 调用 `glance.publish` | 任何被授予 `glance` 权限的隔离应用都会得到响应（[OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)）（见[发布到 glance 屏幕](#发布到-glance-屏幕)）。 |
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

Shell 的宿主策略授权的**原生模块**会得到 peer（随附的策略授权的是 Matrix 客户端 Rinx：
OctoSense `crates/ai-host/src/lib.rs` 中的 `Policy::shipped()`），Rinx 的迷你应用宿主再把
`octos.*` 这些名称提供给用户导入 Rinx 的迷你应用。**隔离运行的脚本应用**也会得到自己的
peer（`card.<app id>`），通过 Shell 的 `octos` 宿主服务
（[OctoSense#106](https://github.com/OctoSense-org/OctoSense/pull/106)），前提是用户在首次使用时允许它的 Agent
（[#120](https://github.com/OctoSense-org/OctoSense/pull/120)、[#184](https://github.com/OctoSense-org/OctoSense/pull/184)）。`OCTOSENSE_CONTAINED_APPS=1` 对所有应用跳过这个询问
（开发者用的覆盖开关），`0` 则关闭它。

## 助手相关权限

四个精确名称，每个都是单独的授权（App Hub `crates/app-policy/src/manifest.rs` 中的
`KNOWN_CAPABILITIES`；名称及其商店文字在 `crates/app-policy/src/services.rs`）。前缀不授予任何权限：`octos.` 或 `octos.admin`
会被准入检查拒绝。

| 权限 | 调用 | 参数 | 返回（`r.data`） | 商店显示 |
| --- | --- | --- | --- | --- |
| `octos.session.open` | `octos.session.open` | `{}` | `{open: true, model: {lane, provider, model} 或 nil}` | Open its own conversation with the assistant |
| `octos.session.history` | `octos.session.history` | `{}` | 会话内容，`{session_id, messages: [...], …}` | Read its own conversations with the assistant |
| `octos.turn.start` | `octos.turn.start` | `{text}`（1 字节到 32 KiB） | 回合结束后的 `{turn_id, text}`，即回复 | Ask the assistant to work for it, using the device's AI settings |
| `octos.turn.interrupt` | `octos.turn.interrupt` | `{}` | 停止正在运行的回合 | Stop assistant work it started |

参数和返回的形状取自提供这些名称的两个宿主，它们都基于 OctoSense 的 `crates/app-peers`：
OctoSense Shell 面向隔离应用的 `octos` 服务（`crates/ai-host/src/contained.rs`）和 Rinx 的
迷你应用宿主（[hagency-org/Rinx](https://github.com/hagency-org/Rinx) 中的
`src/host/octos.rs`）。其他参数会被拒绝（`Unsupported Octos arguments`）：应用只提供文本
（在 OctoSense Shell 中还可以提供 `trigger`，取 `person`、`app` 或 `incoming` 之一，以及
`from`，说明是什么发起了这个回合），从不提供会话、配置、提供方、模型或审批决定。每个应用实例
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
  携带审批决定。

## 错误

| `r.error` | 含义 | 应用该怎么做 |
| --- | --- | --- |
| `this app was not granted "octos", which "<service>" needs` | manifest 中没有列出这个精确名称 | 把它加入 `capabilities`，或删除该调用 |
| `no service answers "octos" on this device` | 当前宿主不向应用提供助手（`card-host`，或没有内核的 Shell 构建） | 显示“不可用”，继续工作 |
| `Waiting for the person to allow this app's agent (OctoSense asks the first time)` | 用户还没有允许该应用的 Agent；Shell 正在询问 | 显示出来；用户的回答决定下一次调用的结果 |
| `The assistant is turned off for apps on this device` | 设备为应用关闭了助手（`OCTOSENSE_CONTAINED_APPS=0`） | 显示“不可用”，继续工作 |
| `The assistant is not available on this device` | Shell 无法启动该应用的 peer | 同上 |
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

截至 2026 年 9 月 30 日。**可用**表示已合入所列仓库的 `main`；**即将推出**表示在所列的
未合并 PR 中，或只存在于 ADR 中。

| 功能 | 状态 | PR 与源码 |
| --- | --- | --- |
| 应用只能通过宿主服务和 app-peer 代理使用 AI，永远接触不到内核、提供方或密钥 | **可用**（规则） | OctoSense [`AGENTS.md`](https://github.com/OctoSense-org/OctoSense/blob/main/AGENTS.md) 第 3、4 条，[`crates/app-peers`](https://github.com/OctoSense-org/OctoSense/tree/main/crates/app-peers) |
| 宿主策略授权的原生模块（Rinx）使用 `octos.*`，以及通过 Rinx 的迷你应用宿主、供导入 Rinx 的应用包使用 | **可用** | OctoSense `crates/ai-host`（`Policy::shipped()`）；[Rinx](https://github.com/hagency-org/Rinx) `src/host/octos.rs` |
| OctoSense 中隔离运行的脚本应用使用 `octos.*` | 在托管内核的 Shell 中（iOS 除外）**可用**，前提是用户在首次使用时允许该应用的 Agent | OctoSense [#106](https://github.com/OctoSense-org/OctoSense/pull/106)、[#120](https://github.com/OctoSense-org/OctoSense/pull/120)、[#184](https://github.com/OctoSense-org/OctoSense/pull/184) |
| `llm`：用户的 AI 提供方、遮盖后的密钥状态、宿主面板 | **可用**，仅限系统应用（`os.*`）；没有发送提示词的方法 | OctoSense [`apps/ai-providers/host-service`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/ai-providers/host-service) |
| `model.complete`：一次性、按 schema 校验的模型调用 | **可用**：权限（[App-Hub#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24)）和服务（[OctoSense#95](https://github.com/OctoSense-org/OctoSense/pull/95)），都在 Shell 的 App Hub 锁定版本中 | [上文](#一次性模型调用model) |
| 应用包中声明应用自己的 Agent：`agent`（profile、模型需求、触发器、技能）、`tools.json`、`AGENT.md`、`skills/` | 在 App Hub 准入检查（[App-Hub#18](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/18)）和 Shell 中**可用**：用户允许后分配 peer 并提供“Ask <app>”面板（[OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)）；`AGENT.md` 和技能还不会装进 peer | [应用自己的 Agent](#应用自己的-agent) |
| 宿主按 `needs` 和 `tier` 挑选模型；触发器和 `background` 真正触发 | **即将推出**（ADR 0002 第 2 步、M3） | [manifest 中的 `agent`](#manifest-中的-agent) |
| 应用工具注册到应用的 peer（`peer/tools/register`、`peer/tool/call`） | **可用**：内核一侧（[octos#2567](https://github.com/octos-org/octos/pull/2567)）以及 Shell 注册应用包中的工具并转发调用（[OctoSense#145](https://github.com/OctoSense-org/OctoSense/pull/145)、[#184](https://github.com/OctoSense-org/OctoSense/pull/184)） | [应用的工具与 peer 工具](#应用的工具与-peer-工具) |
| 在应用内与应用的 Agent 对话、运行时审批、应用记忆 | 对话在 Shell 的“Ask <app>”面板中**可用**（[OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)）；审批在 Shell 的面板上进行（[#120](https://github.com/OctoSense-org/OctoSense/pull/120)、[#145](https://github.com/OctoSense-org/OctoSense/pull/145)）；应用记忆**即将推出**（ADR 0002 §9，M7） | [各部分在哪里执行](#各部分在哪里执行) |
| 系统工具箱：模板、`workflow.run`、`workflow.fork`、`research` 模块 | 模板**可用**（[OctoSense#82](https://github.com/OctoSense-org/OctoSense/pull/82)，`crates/toolbox`），App Hub 中也有了 `research` 和 `crawl` 权限（[App-Hub#26](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/26)）；把工具箱授予应用的 Agent **即将推出**（[OctoSense#64](https://github.com/OctoSense-org/OctoSense/issues/64)；随附的 Shell 中关闭了 `toolbox-peers` 构建特性） | [系统工具箱](#系统工具箱) |
| `news` 宿主服务（数据服务，不用模型） | **可用**，仅限系统应用（`os.*`） | OctoSense [`apps/news/host-service`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/news/host-service) |
| `glance.publish`、`glance.withdraw`、`glance.list`（服务本身） | **可用**（[OctoSense#72](https://github.com/OctoSense-org/OctoSense/pull/72)），面向任何被授予 `glance` 的隔离应用（[OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)） | [发布到 glance 屏幕](#发布到-glance-屏幕) |
| `glance` 权限 | 在 App Hub（[App-Hub#22](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/22)）和 Shell（[OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)）中都**可用** | [谁可以发布](#谁可以发布) |
| L0 数据源 `sys.digest(app:, id:, fields:)` | **即将推出**：[OctoScript#40](https://github.com/OctoSense-org/OctoScript/pull/40)、[OctoScript-Makepad#50](https://github.com/OctoSense-org/OctoScript-Makepad/pull/50)、[OctoSense#87](https://github.com/OctoSense-org/OctoSense/pull/87) | [绑定到结果的卡片](#绑定到结果的卡片sysdigest) |
| 渲染并评审卡片：`card-studio`、`card-host --remote` | **可用**（App Hub `main`，[App-Hub#19](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/19)）；由应用的 Agent 运行这一循环**即将推出**（M6） | [卡片级别与渲染评审](#卡片级别与渲染评审) |

一句话概括：商店应用可以调用 `model.complete`，在被授予 `glance` 时发布 glance 卡片，并在
用户允许其 Agent 后通过自己的 peer 与助手对话，Shell 会为这个 peer 注册应用的工具；根据
`needs` 选择模型、触发器、后台运行、应用记忆以及面向应用 Agent 的系统工具箱仍即将推出。

应用作者现在可以做的：

- 把应用自己的界面做成不依赖 AI 也完整可用，并把“不可用”当作正常状态显示。
- 声明一个能通过 `hub check` 的 Agent（`agent`、`tools.json`、`AGENT.md`、技能），同时
  清楚 Shell 会为它分配 peer 并注册它的工具，但还不会装入 `AGENT.md` 或技能、为它挑选模型
  或触发它的触发器。
- 用 `card-studio` 编写并渲染 L0 卡片；OctoScript#40 合入后，再围绕 `sys.digest` 设计卡片。

**需要知道的版本差异。** `tools/octo check` 运行的是本仓库旁边的 App Hub 检出
（`main`）。OctoSense Shell 锁定自己的一个 App Hub 提交（2026-09-30 为 `0f332112`，见
OctoSense 的 `native-apps.json`），它可能落后于 App Hub `main`。manifest 会拒绝未知字段，
所以比 Shell 锁定版本更新的字段能通过 `octo check`，却会被 Shell 拒绝，直到锁定版本更新。

如果想提前准备，可以参照 App Hub 的 News 示例
（[`crates/app-policy/tests/fixtures/news-agent`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/crates/app-policy/tests/fixtures/news-agent)），
在 `bundle/` 之外起草 `tools.json` 和 `AGENT.md`。

## 应用自己的 Agent

自 [App-Hub#18](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/18)（2026-09-27 合并）起在 App Hub 准入检查中**可用**，Shell 锁定的
App Hub 也包含它。自 [OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)（2026-09-30）起，对于声明了 Agent（或
`octos.*`，或附带 `tools.json`）的应用，Shell 会在用户允许后为它分配自己的 peer，把应用包
中的工具注册到这个 peer，并让用户在“Ask <app>”面板中与它对话。还没有任何 Shell 把
`AGENT.md` 或技能装进 peer、挑选模型或触发触发器（ADR 0002 实施第 2 步）。

契约见 App Hub 的
[PUBLISHING § The app's agent and tools](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-apps-agent-and-tools)；
完整示例是 App Hub 的
[`crates/app-policy/tests/fixtures/news-agent`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/crates/app-policy/tests/fixtures/news-agent)。

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

（唯一的拒绝项是模板缺少截图，用真实截图即可解决。）

| 字段 | 规则（App Hub `manifest.rs`、`policy.rs`） | 目前在哪里执行 |
| --- | --- | --- |
| `profile` | `read-only`、`workspace-write` 或 `workspace-write-never-ask`；没有完全访问 | 准入检查 |
| `tools` | 只能是通用宿主工具：`ledger.read ledger.write net.fetch storage.read storage.write card.render`；其他一律拒绝 | 准入检查 |
| `max_iterations`、`token_budget` | 上限分别裁剪为 8 和 200 000 | 准入检查（`grants:` 行） |
| `model.needs` | 取自 `tool_calling vision long_context reasoning structured_output multilingual` | 准入检查；应用有工具却没有 `tool_calling` 时会警告 |
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

在 `tools.json` 中按工具声明（见下一节）。一次调用是否需要用户同意取决于 `risk`；由谁的
界面来询问取决于 `confirm`（App Hub PUBLISHING）：

| `risk` | 运行方式 |
| --- | --- |
| `read`（只查看）、`act`（修改应用自己的状态） | 无人值守运行 |
| `destructive`（发送、发帖、分享、购买、删除） | 只在用户批准后运行 |

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
| 在应用内与应用的 Agent 对话 | 在 Shell 的“Ask <app>”面板中**可用**（[OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)） |
| `app/<app>/…` 中的记忆，按规则提升 | **即将推出**：ADR 0002 §9，M7。没有对应的 manifest 字段；记忆规则写在 `AGENT.md` 的文字里 |
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
  `host-service` 工具，就像应用自己调用 `host.request` 一样；`app` 工具目前会被拒绝
  （`<tool> runs in the app's own script; open the app to use it`；OctoSense
  `crates/shell/src/host_tools/script_apps.rs`）。
- `background`、`shareable`、`private_data`、`confirm`：见
  [应用自己的 Agent](#审批risk-与-confirm)。

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

模型看到的 `news.list` 名为 `news_list`。默认值：每次调用 30 秒，结果最多 256 KiB，审批
一小时后过期。需要把关的调用（destructive 或 outward）在 `confirm: host` 时等待内核审批；
在 `confirm: app` 且用户在场时，以 `confirm_required: true` 交给宿主。应用从不直接调用这些
方法：由 Shell（`crates/ai-host`）替应用的 peer 调用（ADR 0002 §12）。

## 系统工具箱

模板**可用**（[OctoSense#82](https://github.com/OctoSense-org/OctoSense/pull/82)，已合并：`crates/toolbox`，crate `octosense-toolbox`），
App Hub 也有了 `research` 和 `crawl` 权限（[App-Hub#26](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/26)）。把工具箱授予应用的 Agent
**即将推出**（[OctoSense#64](https://github.com/OctoSense-org/OctoSense/issues/64)）：随附的
Shell 构建中关闭了 `toolbox-peers` 构建特性，`crawl` / `deep_crawl` 也尚未实现（工具箱唯一的
模块是 `research`）。

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
（见[上一节](#应用的工具与-peer-工具)），而不是通过 `host.request`。

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
- **结果**写入 `<app folder>/toolbox/runs/<template>/<run_id>.json`。
- **每个应用一份预算**：启用 `toolbox-peers` 时，工具箱的模型客户端经由 `model` 服务的
  `ModelHost::complete`（`crates/ai-host/src/toolbox_peers.rs`），所以模板中的调用和直接的
  `model.complete` 调用消耗同一份预算。

## 发布到 glance 屏幕

### `glance.publish`、`glance.withdraw`、`glance.list`

服务在 OctoSense `main` 上**可用**
（[#72](https://github.com/OctoSense-org/OctoSense/pull/72)，`crates/shell/src/glance.rs`）：

| 方法 | 参数 | 返回 |
| --- | --- | --- |
| `glance.publish` | `{card_id, source, data?, title, priority?, expires?, open?: {app, route?}}` | `{card_id, replaced, expires_at}` |
| `glance.withdraw` | `{card_id}` | `{withdrawn}` |
| `glance.list` | – | `[{card_id, title, priority, published_at, expires_at}]`，只包含调用者自己的卡片 |

- `source` 是一张 **L0 卡片**（头部声明时可以是 L1；L2 会被拒绝），按 `data`（从卡片数据源
  名称到值的映射）实例化，并在保存前经过 Card runner 的流水线降级处理。
- **限制：** `card_id` 为 1–64 个 `[A-Za-z0-9._-]` 字符；`title` 最多 80 个字符；`source`
  最多 16 KiB；`data` 按 JSON 计最多 32 KiB；`priority` 0–100（默认 50）；`expires` 60 秒
  到 7 天（默认 24 小时）；每个应用每分钟最多发布 6 次（替换和被 L0 检查拒绝的卡片都计数）；
  每个应用 4 张卡片；存储中共 32 张；显示 6 张。
- **身份：** 发布者就是调用者，永远不是参数；用相同的 `card_id` 发布会替换原卡片；
  `open.app` 必须是调用者自己的应用。点击卡片会打开该应用。`open.route` 会被保存，但尚未
  使用。
- 每个卡片块在自己的隔离环境中运行，遵循发布它的应用的策略（原生模块的卡片块没有任何
  权限），并且不能弹出面板。

### 谁可以发布

- **任何被授予 `glance` 的隔离应用**都可以发布、列出和撤回自己的卡片
  （[OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)，已合并；权限是 [App-Hub#22](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/22)，已在 Shell 的 App Hub
  锁定版本中）。系统应用没有例外。拒绝时返回：`<app> was not granted the glance capability`。
- 原生模块和 Shell 的演示（`OCTOSENSE_GLANCE_DEMO=1`）也可以发布。

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

**即将推出**：[OctoScript#40](https://github.com/OctoSense-org/OctoScript/pull/40)
（L0 数据源）、[OctoScript-Makepad#50](https://github.com/OctoSense-org/OctoScript-Makepad/pull/50)
（更新锁定版本）、[OctoSense#87](https://github.com/OctoSense-org/OctoSense/pull/87)
（由 Shell 解析，`crates/shell/src/glance_digest.rs`）。

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

（这里省略了部分头部注释。）在 OctoScript#40 合入之前，L0 检查器不认识 `sys.digest`，
使用它的卡片会被拒绝。

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
| 4 | **News 的 Agent 运行**，使用应用包中声明的 `AGENT.md`、技能和工具 | 声明在 App Hub 中**可用**（#18）；用户允许后为 `os.news` 分配带有其 `tools.json` 工具的 peer，**可用**（[OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)）；把 `AGENT.md` 和技能装进 peer **即将推出** | `apps/news/bundle`、`crates/shell/src/agents.rs` |
| 5 | **运行 `news-digest` 模板**：`workflow.run {id: "news-digest", params: {topic, language}, run_id: "glance"}` | 模板**可用**（#82）；由应用的 Agent 运行**即将推出**（M5，#64） | `crates/toolbox` |
| 6 | **宿主保存结果**，附带来源记录：`toolbox/runs/news-digest/glance.json` | 在工具箱运行器中**可用**（#82）；由 Agent 发起**即将推出**（#64） | `crates/toolbox/src/runner.rs` |
| 7 | **卡片绑定到结果**：`news-brief.card`，`source brief sys.digest(app: "os.news", id: "glance", …)` | **即将推出**（OctoScript#40、OctoScript-Makepad#50、#87） | `crates/shell/src/glance_digest.rs` |
| 8 | **按 glance、手机和桌面尺寸渲染并评审**卡片 | 工具**可用**（`card-studio`）；由 Agent 运行**即将推出**（M6） | App Hub `crates/card-studio` |
| 9 | **`glance.publish`** 这张卡片（`card_id` 为 "brief"，`data: {}`；由宿主填入 `brief`） | **可用**，由被授予 `glance` 的隔离应用发布（#86） | `crates/shell/src/glance.rs` |
| 10 | **用户点击卡片，打开 News** | **可用**（桌面面板和手机的 glance 页面会打开发布卡片的应用） | `glance_panel.rs`、`mobile_pages.rs` |

想现在看到第 9–10 步，可以运行桌面 Shell 自带的检查：它在启动时以 `os.news` 身份发布一张
示例卡片（`OCTOSENSE_GLANCE_DEMO=1`），并从卡片打开 News，全程隐藏窗口、通过远程控制桥
操作（在 OctoSense 检出目录中运行；本文未运行）：

```sh
cargo build --release -p octosense && desktop/scripts/glance_remote.sh
```

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
  `OCTOSENSE_GLANCE_DEMO=digest`（**即将推出**）。
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
- OctoSense-App-Hub `main`（`a72989f`；2026-09-30 更新基于 `0f33211`）：`crates/app-policy/src/manifest.rs`、
  `services.rs`、`agent.rs`、`policy.rs`、`listing.rs`；`docs/PUBLISHING.md`；
  `docs/DEVELOPMENT.md`。
- OctoScript PR #40：`docs/ui-profile-l0.md` §5.14。
- octos PR #2567：
  `docs/OCTOS_UI_PROTOCOL_CHANGE_REQUEST_UPCR_2026_035_PEER_HOST_TOOLS.md`。
- Rinx：`src/host/octos.rs`。
