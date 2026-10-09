# 宿主 API 能力族

[English](HOST-API-FAMILIES.md) | 简体中文

每个 `host.request` 能力族：申请它所需的能力、Shell 实际响应的对象、支持的平台，以及从哪个版本开始提供。**可以申请不等于会响应**：准入检查只要求能力在契约列表中，响应哪些应用则由服务自己决定。本页由 [`host-api-families.json`](host-api-families.json) 生成，该文件是 [App Hub #172](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/172) 上那张表的快照；请用 `tools/gen_host_api_families.py` 重新生成，不要手工修改。

核对基准：desktop-v0.1.0-rc.2 (4ccf8e06; App Hub 95e4831a; octosense-app-contract 1.10.0)；App Hub main 28745c0 (KNOWN_CAPABILITIES: engine names)。

**已随[桌面 RC2](../README.zh-CN.md#下载兼容-shell) 发行**（源码 `4ccf8e06`，App Hub `95e4831a`，契约 1.10.0）：`files` 能力族、`storage.binary_write@1`（`fs.write_bytes`）、`location.sample`、Windows 和 Linux 上原生的外部链接打开方式、面向应用本地文件的 `audio.play/status/stop` 和 `microphone.record_*`、`device_calendar` 能力族、面向应用的 `mail.compose`、`mail.compose_status` 和 `mail.review_send`，以及 `Video` 控件的 Splash 控制接口（`video.playback_controls@1`，不是 `host.request` 方法）。各行给出平台范围；音频、原生选择器、日历写入和 SMTP 投递的硬件验收仍待完成（[宿主 OS API 状态](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-rc.2/docs/host-os-api-status.zh-CN.md)）。某个平台上没有的方法要放在 `host_api.optional` 下：写进 `required` 会导致无法在该平台安装。

| 能力族 | 能力 | 响应对象 | 平台 | 起始版本 | 备注 |
| --- | --- | --- | --- | --- | --- |
| `ai-providers` | — | 某个系统应用自己的服务 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 系统应用 AI providers 自己的服务。 |
| `audio` | `audio` | 商店应用 | macOS、Android | rc.2 | RC2 在 macOS 和 Android 上提供：`audio.play/status/stop` 在前台播放应用存储中的一个 WAV、MP3、FLAC 或 Ogg 文件（最大 1 MiB、最长 60 秒）；需要 `storage`；硬件验收待完成。 |
| `auth` | `auth` | 商店应用 | Android、macOS、Windows、Linux | beta.2 | 用户在宿主面板上批准的连接；自 RC1 起支持后端登录（Windows 和 Linux 用浏览器登录，RC2 起可用；拒绝写操作）。 |
| `cad` | `cad`（仅 App Hub main） | 仅限系统应用（`os.*`） | macOS、Windows、Linux | rc.2（仅系统助手） | 面向系统助手的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行（特性 `craft-engines`）；Home 构建不包含。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。 |
| `calendar` | `calendar` | 某个系统应用自己的服务 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | Calendar 自己的服务（`calendar is Calendar's own service`）。要访问用户的 Google Calendar，请用 `gcalendar`。 |
| `camera` | `camera` | 商店应用 | Android、macOS | rc.1 | 自 RC1 起在 Android 和 macOS 上提供；需要用户在宿主面板上对本应用的授权，操作系统的相机授权仍然适用。 |
| `clipboard` | `clipboard` | 没有任何 Shell 提供 | — | — | 可以申请，准入检查也会通过，但任何发行版都没有 Shell 响应 `host.request("clipboard.*")`；授权只解锁 WebCard 自己的只写剪贴板桥接。 |
| `deck` | `deck`（仅 App Hub main） | 仅限系统应用（`os.*`） | macOS、Windows、Linux | rc.2（仅系统助手） | 面向系统助手的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行（特性 `craft-engines`）；Home 构建不包含。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。 |
| `design` | `design`（仅 App Hub main） | 仅限系统应用（`os.*`） | macOS、Windows、Linux | rc.2（仅系统助手） | 面向系统助手的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行（特性 `craft-engines`）；Home 构建不包含。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。 |
| `device_calendar` | `device_calendar` | 商店应用 | macOS、Android | rc.2 | RC2 在 macOS（EventKit）和 Android Home 上提供：授权、选择日历、有上限的日程读取和亲手点按确认的写入；与系统日历的实际交互待验收。与 `calendar` 和 `gcalendar` 是不同的服务。 |
| `effect` | `effect`（仅 App Hub main） | 仅限系统应用（`os.*`） | macOS、Windows、Linux | rc.2（仅系统助手） | 面向系统助手的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行（特性 `craft-engines`）；Home 构建不包含。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。 |
| `files` | `files` | 商店应用 | macOS、Windows、Android、Linux | rc.2 | RC2：`files.import`、`files.export` 和 `files.pick_photo` 在 macOS、Windows 和 Android 上提供，Linux 需要 zenity、qarma、matedialog 或 kdialog；`files.share` 仅限 Android；单个文件最大 1 MiB，仅限前台；选择器的验收待完成。 |
| `film` | `film`（仅 App Hub main） | 仅限系统应用（`os.*`） | macOS、Windows、Linux | rc.2（仅系统助手） | 面向系统助手的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行（特性 `craft-engines`）；Home 构建不包含。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。 |
| `gcalendar` | `gcalendar` | 商店应用 | Android、macOS、Windows、Linux | beta.2 | 通过 `auth` 建立的连接；写入由 Shell 审阅，任何发行版都无法在 Windows 和 Linux 上批准。 |
| `github` | `github` | 商店应用 | Android、macOS、Windows、Linux | beta.2 | 通过 `auth` 建立的连接；保存由 Shell 审阅，任何发行版都无法在 Windows 和 Linux 上批准。 |
| `glance` | `glance` | 商店应用 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 速览栏上的卡片，只会打开本应用。 |
| `gmail` | `gmail` | 商店应用 | Android、macOS、Windows、Linux | beta.2 | 通过 `auth` 建立的连接；发送审阅由 Shell 负责，任何发行版都无法在 Windows 和 Linux 上批准。 |
| `light` | `light`（仅 App Hub main） | 仅限系统应用（`os.*`） | macOS、Windows、Linux | rc.2（仅系统助手） | 面向系统助手的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行（特性 `craft-engines`）；Home 构建不包含。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。 |
| `llm` | `llm` | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 管理设备上的 AI 提供商；`llm is for OctoSense's own apps.` 请用 `model`。 |
| `location` | `location` | 商店应用 | Android、macOS | rc.1；`sample` rc.2 | 自 RC1 起在 Android 和 macOS 上提供；`location.get` 仅限 Android，RC2 新增的 `location.sample` 在两者上都能为前台应用获取实时位置。 |
| `mail` | `mail` | 部分方法；见备注 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1；`compose`/`review_send` rc.2 | 读取用户为应用连接的账户并发出通知。从 RC2 起，商店应用也能发送：`mail.compose` 和 `mail.compose_status` 保存草稿，`mail.review_send`（或 `mail.send`）打开宿主的原生审阅界面，它只在 macOS 和 Android 上能确认；在 Windows 和 Linux 上以 `Physical Mail send approval is unavailable on this platform` 失败。在 RC1 上，商店应用没有发送路径（[OctoSense #409](https://github.com/OctoSense-org/OctoSense/issues/409)）。 |
| `maps` | — | 某个系统应用自己的服务 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 系统应用 Maps 自己的服务。 |
| `matrix` | `matrix.*`（方法级） | 没有任何 Shell 提供 | — | — | OctoSense 的 Shell 不提供。只有 Rinx 应用通过自己的宿主向其迷你应用提供 `matrix.*`。 |
| `microphone` | `microphone` | 商店应用 | Android、macOS | rc.1；`record_*` rc.2 | 自 RC1 起在 Android 和 macOS 上提供；为相机录像加入声音。RC2 新增 `microphone.record_*`：在前台录一段短音频（单声道 WAV，最长 30 秒）存入应用存储；硬件验收待完成。 |
| `model` | `model` | 商店应用 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 每日预算内的一次性调用；媒体和嵌入向量从 RC1 起提供。 |
| `news` | `news` | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | `The news service serves system apps only.` |
| `octos` | `octos.session.open`、`octos.session.history`、`octos.turn.start`、`octos.turn.interrupt` | 商店应用 | Android、OpenHarmony、macOS、Windows、Linux | beta.1 | 应用自己的 Agent 会话，用户允许后可用。iOS 上不提供。 |
| `pdf` | `pdf`（仅 App Hub main） | 仅限系统应用（`os.*`） | macOS、Windows、Linux | rc.2（仅系统助手） | 面向系统助手的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行（特性 `craft-engines`）；Home 构建不包含。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。 |
| `photo` | `photo`（仅 App Hub main） | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | rc.2（仅系统助手） | 面向系统应用的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行，Home 构建保留。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。 |
| `photos` | `photos` | 某个系统应用自己的服务 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 只响应系统应用 Photos 的 `notify`。 |
| `runtime` | `runtime` | 商店应用 | Android、iOS、OpenHarmony、macOS、Windows、Linux、web | rc.1 | `runtime.list` 和 `runtime.describe`；`card-host` 也会响应。 |
| `sheet` | `sheet`（仅 App Hub main） | 仅限系统应用（`os.*`） | Android、iOS、OpenHarmony、macOS、Windows、Linux | rc.2（仅系统助手） | 面向系统应用的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行，Home 构建保留。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。 |
| `sound` | `sound`（仅 App Hub main） | 仅限系统应用（`os.*`） | macOS、Windows、Linux | rc.2（仅系统助手） | 面向系统助手的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行（特性 `craft-engines`）；Home 构建不包含。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。 |
| `vector` | `vector`（仅 App Hub main） | 仅限系统应用（`os.*`） | macOS、Windows、Linux | rc.2（仅系统助手） | 面向系统助手的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行（特性 `craft-engines`）；Home 构建不包含。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。 |
| `wasm` | `wasm` | 商店应用 | Android、macOS、Linux | rc.2（桌面 macOS/Linux） | 桌面 RC2 在 macOS 和 Linux 上提供（Windows 不提供），Android 上的标准 Home 源码构建也提供（特性 `wasm-functions`）；RC1 没有提供（[运行自己的 Rust 代码](RUST.zh-CN.md)）。 |
| `word` | `word`（仅 App Hub main） | 仅限系统应用（`os.*`） | macOS、Windows、Linux | rc.2（仅系统助手） | 面向系统助手的 craft 引擎宿主服务（[ADR 0013](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0013-craft-engines-as-pinned-services.zh-CN.md)），随桌面 RC2 发行（特性 `craft-engines`）；Home 构建不包含。App Hub `main` 已把该名称列为可申请的能力，但 RC2 的准入检查不认识它，也没有任何商店应用能得到服务。 |
| `youtube` | `youtube` | 某个系统应用自己的服务 | Android、iOS、OpenHarmony、macOS、Windows、Linux | beta.1 | 只响应系统应用 YouTube 的 `notify`。 |
