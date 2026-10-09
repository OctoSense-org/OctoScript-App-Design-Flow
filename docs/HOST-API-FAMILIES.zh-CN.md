# 宿主 API 能力族

[English](HOST-API-FAMILIES.md) | 简体中文

每个 `host.request` 能力族：申请它的能力、Shell 实际响应的对象、支持的平台，以及从哪个版本开始提供。**可以申请不等于会响应**：准入检查只要求能力在契约列表中，由哪些应用调用则由服务自己决定。本页由 [`host-api-families.json`](host-api-families.json) 生成，该文件是 [App Hub #172](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/172) 上那张表的快照；请用 `tools/gen_host_api_families.py` 重新生成，不要手工修改。

核对基准：desktop-v0.1.0-rc.1 (933abbcf)；OctoSense main a90e7c62 (2026-10-09)。

**审查中，任何可下载的构建都还没有**：OctoSense [#402](https://github.com/OctoSense-org/OctoSense/pull/402)（配合 App Hub [#175](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/175)，契约 1.9）新增 `files` 能力族（`files.status/import/export`）、`storage.binary_write@1`（`fs.write_bytes`）、`location.sample` 和原生外部链接打开器。在它们发行之前，不要依赖这些接口。

| 能力族 | 申请 | 响应对象 | 平台 | 起始版本 | 备注 |
| --- | --- | --- | --- | --- | --- |
| `ai-providers` | — | 某个系统应用自己的服务 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 系统应用 AI providers 自己的服务。 |
| `auth` | `auth` | 商店应用 | Android、macOS、Windows、Linux | beta.2 | 用户在宿主面板上批准的连接；RC1 支持后端登录。 |
| `cad` | — | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | `main`，尚未进入任何发行版 | 面向系统应用的 craft 引擎宿主服务（ADR 0013）。商店应用无法申请。 |
| `calendar` | `calendar` | 某个系统应用自己的服务 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | Calendar 自己的服务（`calendar is Calendar's own service`）。要访问用户的 Google Calendar，请用 `gcalendar`。 |
| `camera` | `camera` | 商店应用 | Android、macOS | rc.1 | RC1 的 Android 和 macOS，需要应用自己的授权和系统提示。 |
| `clipboard` | `clipboard` | 没有任何 Shell 提供 | — | — | 可以申请，准入检查也会通过，但任何发行版都没有 Shell 提供 `clipboard.*`：每次调用都会失败。 |
| `deck` | — | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | `main`，尚未进入任何发行版 | 面向系统应用的 craft 引擎宿主服务（ADR 0013）。商店应用无法申请。 |
| `design` | — | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | `main`，尚未进入任何发行版 | 面向系统应用的 craft 引擎宿主服务（ADR 0013）。商店应用无法申请。 |
| `effect` | — | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | `main`，尚未进入任何发行版 | 面向系统应用的 craft 引擎宿主服务（ADR 0013）。商店应用无法申请。 |
| `film` | — | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | `main`，尚未进入任何发行版 | 面向系统应用的 craft 引擎宿主服务（ADR 0013）。商店应用无法申请。 |
| `gcalendar` | `gcalendar` | 商店应用 | Android、macOS、Windows、Linux | beta.2 | 通过 `auth` 建立的连接；写入由 Shell 审阅，RC1 在 Windows 和 Linux 上无法批准。 |
| `github` | `github` | 商店应用 | Android、macOS、Windows、Linux | beta.2 | 通过 `auth` 建立的连接；保存由 Shell 审阅，RC1 在 Windows 和 Linux 上无法批准。 |
| `glance` | `glance` | 商店应用 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 速览栏上的卡片，只会打开本应用。 |
| `gmail` | `gmail` | 商店应用 | Android、macOS、Windows、Linux | beta.2 | 通过 `auth` 建立的连接；发送审阅由 Shell 负责，RC1 在 Windows 和 Linux 上无法批准。 |
| `light` | — | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | `main`，尚未进入任何发行版 | 面向系统应用的 craft 引擎宿主服务（ADR 0013）。商店应用无法申请。 |
| `llm` | `llm` | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 管理设备上的 AI 提供商；`llm is for OctoSense's own apps.` 请用 `model`。 |
| `location` | `location` | 商店应用 | Android、macOS | rc.1 | RC1 的 Android 和 macOS；`location.get` 仅限 Android。 |
| `mail` | `mail` | 部分方法；见备注 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 读取用户为应用连接的账户并发出通知。商店应用在 RC1 上没有发送路径：`mail.send` 返回 `approval_required`，审阅方法只响应 Mail（[OctoSense #409](https://github.com/OctoSense-org/OctoSense/issues/409)）。 |
| `maps` | — | 某个系统应用自己的服务 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 系统应用 Maps 自己的服务。 |
| `matrix` | `matrix.* (method-level)` | 没有任何 Shell 提供 | — | — | OctoSense 的 Shell 不提供。只有 Rinx 应用通过自己的宿主向其小程序提供 `matrix.*`。 |
| `microphone` | `microphone` | 商店应用 | Android、macOS | rc.1 | RC1 的 Android 和 macOS；为录像加入声音。 |
| `model` | `model` | 商店应用 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 每日预算内的一次性调用；媒体和向量从 RC1 起提供。 |
| `news` | `news` | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | `The news service serves system apps only.` |
| `octos` | `octos.session.open`, `octos.session.history`, `octos.turn.start`, `octos.turn.interrupt` | 商店应用 | Android、OpenHarmony、macOS、Windows、Linux | beta.1 | 应用自己的 Agent 会话，用户允许后可用。iOS 上不提供。 |
| `pdf` | — | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | `main`，尚未进入任何发行版 | 面向系统应用的 craft 引擎宿主服务（ADR 0013）。商店应用无法申请。 |
| `photo` | — | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | `main`，尚未进入任何发行版 | 面向系统应用的 craft 引擎宿主服务（ADR 0013）。商店应用无法申请。 |
| `photos` | `photos` | 某个系统应用自己的服务 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 只响应系统应用 Photos 的 `notify`。 |
| `runtime` | `runtime` | 商店应用 | Android、iOS、OpenHarmony、macOS、Windows、Linux、web | rc.1 | `runtime.list` 和 `runtime.describe`；`card-host` 也会响应。 |
| `sheet` | — | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | `main`，尚未进入任何发行版 | 面向系统应用的 craft 引擎宿主服务（ADR 0013）。商店应用无法申请。 |
| `sound` | — | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | `main`，尚未进入任何发行版 | 面向系统应用的 craft 引擎宿主服务（ADR 0013）。商店应用无法申请。 |
| `vector` | — | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | `main`，尚未进入任何发行版 | 面向系统应用的 craft 引擎宿主服务（ADR 0013）。商店应用无法申请。 |
| `wasm` | `wasm` | 商店应用 | Android、macOS、Linux | `main`，尚未进入任何发行版 | `main` 上 macOS、Linux 和 Android 的标准构建（特性 `wasm-functions`）；尚无发行版（[运行自己的 Rust 代码](RUST.zh-CN.md)）。 |
| `word` | — | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | `main`，尚未进入任何发行版 | 面向系统应用的 craft 引擎宿主服务（ADR 0013）。商店应用无法申请。 |
| `youtube` | `youtube` | 某个系统应用自己的服务 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 只响应系统应用 YouTube 的 `notify`。 |
