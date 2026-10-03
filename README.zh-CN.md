# OctoScript App Design Flow

[English](README.md) | 简体中文

[OctoSense](https://github.com/OctoSense-org) 应用的开发工具集。它带着你（或编码
Agent）从一个想法（一段文字需求、一张生成的 UX 图）走到一个隔离运行的应用包：通过
[OctoSense App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) 的准入检查，
等待由人签名并提交。

仓库包含：给 Agent 的规则（[AGENTS.md](AGENTS.md)）、分步骤的设计流程
（[flows/](flows/README.zh-CN.md)）、开发者文档（[docs/](docs/)）、可直接运行的应用模板
（[templates/script-app](templates/script-app/README.zh-CN.md)）、完整示例
（[examples/](examples/README.zh-CN.md)），以及 `tools/octo`：一个包装 App Hub 真实
`card-host` 与 `hub` 二进制的小型命令行工具。它自己从不决定准入：`tools/octo check`
先为未签名的包写入摘要，再转发 `hub check` 的输出与退出码，并显示进度和清单（listing）
占位提示。摘要写入失败时，命令立即返回其错误码，不运行准入检查。

面向：参加黑客松的选手、其他开发 OctoSense 应用的开发者，以及与他们协作的编码 Agent。

原名 *Octoscript-AppCard*。AppCard 助手运行时和第一方应用先迁至 OctoSense-System-Apps，
自 2026-09-27 起位于 [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps)
（OctoSense-System-Apps 已归档，不再公开）。

## 代码导读

[代码导读（英文）](docs/CODE-WALKTHROUGH.md) 沿着 Python CLI，从脚本模板走到运行中的
应用，再进入 App Hub 与 OctoSense Shell。“总结已保存的笔记”这一请求解释 Peer、对话、
数据访问和应答路由；从画面图集到卡片的示例解释图像流水线的默认阶段。导读还介绍原生
Rust、Splash 与 L0 应用的差别、跨应用工具限制、运行时版本和 Tokio 所在的层级。
`tools/octo` 是开发命令；octos 是独立的 Agent 内核。

## 目录

- [黑客松：从这里开始](#黑客松从这里开始)
- [Agent 从这里开始](#agent-从这里开始)
- [现状](#现状)
- [快速上手](#快速上手)
- [`tools/octo`](#toolsocto)
- [设计流程](#设计流程)
- [应用是什么](#应用是什么)
- [隔离规则](#隔离规则)
- [应用中的 AI](#应用中的-ai)
- [运行应用](#运行应用)
- [无头测试：同时测多个应用，不占屏幕](#无头测试同时测多个应用不占屏幕)
- [发布](#发布)
- [仓库结构](#仓库结构)
- [示例](#示例)
- [参与贡献](#参与贡献)
- [相关仓库](#相关仓库)

## 黑客松：从这里开始

本仓库只负责技术路径。比赛本身（规则、日程、评审、作品如何提交）请见
[Agentic App Hackathon](https://create.gosim.org/agenticapp26/) 页面并咨询主办方，
这些都不在这里决定。选手需要从这里获得的内容：

| | |
| --- | --- |
| **起步** | 下面的[快速上手](#快速上手)：2026-09-26 的实测中，一个新应用从空目录到 `— PASSED` 约 10 分钟（克隆 1.5 分钟、setup 20 秒、首次构建在 Apple silicon Mac 上约 1 分钟），大部分时间用在编写应用上。每一步都是 shell 命令，任何编码 Agent（或不用 Agent）都能执行。 |
| **机器** | 已验证的平台是 Apple silicon 上的 macOS；Windows 和 Linux 未验证。需要 Rust stable（rustup）、Python 3.9+（macOS 自带的 `/usr/bin/python3` 即可）、git、图形会话、约 3 GB 可用空间（克隆约 1.9 GB，其中本仓库 1.3 GB，可用 `--depth 1`；构建产物约 1 GB），首次构建需要联网。 |
| **应用能做什么** | 自己的存储、访问已声明主机的 HTTPS 请求、图片与网页、相机、定位，以及通过宿主服务使用 Mail：[CAPABILITIES](docs/CAPABILITIES.md)。语言与全部 API：[SCRIPT-API](docs/SCRIPT-API.md)。完整示例：[系统应用](https://github.com/OctoSense-org/OctoSense/tree/main/apps)（News、Photos、Maps、Camera、Mail）和[模板](templates/script-app/README.zh-CN.md)。 |
| **应用不能做什么** | 持有密码、密钥或 token；自创权限或宿主服务（那是 App Hub 和 Shell 的修改）；使用 `llm` 或 `os.*` id（仅限系统应用）；把开发预览/安装当作商店发布。较新的 Android 版 OctoSense App Studio 工具有单独的[实测范围](docs/MODEL-VALIDATION.zh-CN.md#选择测试方式)。`card-host` 不提供任何宿主服务，所以类似 Mail 的应用在其中会显示 `no service answers`。 |
| **应用中的 AI** | 开发应用不需要任何 AI 服务，可以用任何编程 Agent，也可以不用。在设备上，商店应用可以进行一次性模型调用（`model`），并在用户允许其 Agent 后与助手对话（`octos.*`）；`card-host` 两者都不提供（`no service answers "octos"`），所以要把应用做成不依赖它们也完整可用。现在能用什么、计划做什么，以及一个经过验证、能处理“不可用”状态的示例：[docs/AI-SERVICES.zh-CN.md](docs/AI-SERVICES.zh-CN.md)。 |
| **演示** | 在 `card-host` 中运行应用（`tools/octo run`，通过远程控制桥操作），并用 `tools/octo shot` 截取真实截图。要在 OctoSense 内展示，让 OctoSense 桌面端 Shell 读取本地目录（[PUBLISHING §4](docs/PUBLISHING.md#4-rehearse-the-store-path-locally)）。 |
| **提交到 App Hub** | [发布](#发布)：`tools/octo check` 通过、回答 `hub scan` 的问题，然后由人签名，并在 [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub/issues) 开一个 `Submit <app id> <version>` issue。参赛作品不等于自动提交到 App Hub；请向主办方确认他们需要什么。 |
| **无头测试** | `tools/octo run … --hidden`：窗口不会出现，Agent 可以在不占用你屏幕的情况下测试应用（也可同时测多个应用，每个用自己的 `--port`）。见[无头测试](#无头测试同时测多个应用不占屏幕)。 |
| **验证模型输出** | [开发与验证循环](docs/MODEL-VALIDATION.zh-CN.md)：Makepad 输入/截图、OctoSense App Studio 与跨 APK 截图边界、模型失败的具体修复方法，以及与最终源码绑定的证据。 |
| **卡住了** | [QUICKSTART § Troubleshooting](docs/QUICKSTART.md#troubleshooting)，然后看 [SCRIPT-API § Gotchas](docs/SCRIPT-API.md#gotchas)。 |

## Agent 从这里开始

> **任何编程 Agent 都可以，不用 Agent 也可以。** 这些说明对 Codex、Claude Code、Cursor、Gemini CLI、GitHub Copilot 或直接在终端操作的人完全一样：每一步都是一条 shell 命令或一次文件修改，不依赖特定的 Agent、模型或厂商。规则以 `AGENTS.md` 为准；`CLAUDE.md` 和 `GEMINI.md` 只是为按这些文件名查找的 Agent 导入它。

`tools/octo` 是本仓库自带的 Python 命令行工具，封装 App Hub 的 `hub` 和 `card-host`；它与 OctoSense 内部的 Agent 内核 octos 无关，也不需要任何 AI 服务或 API key。

按顺序阅读（与 [OctoSense 组织主页](https://github.com/OctoSense-org) 给出的顺序一致）：

1. [AGENTS.md](AGENTS.md)：规则、完成标准，以及每一个必须停下来询问人的节点。
2. [flows/README.md](flows/README.zh-CN.md)：按起点选择设计流程，然后逐步执行该流程的
   `FLOW.md`。
3. [docs/QUICKSTART.md](docs/QUICKSTART.md) 与 [docs/SCRIPT-API.md](docs/SCRIPT-API.md)：
   用 `tools/octo` 构建并运行应用；只使用有文档的 API（或能在运行时源码、某个系统应用中
   找到出处的 API）。
4. [docs/PUBLISHING.md](docs/PUBLISHING.md)，以及 App Hub 的
   [发布契约](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md)：
   stamp、截图、检查、签名、提交。

需要人来把关的节点（发布者密钥与签名、发布者身份与隐私文本、平台声明、付费图像生成、
视觉确认、提交）列在 [AGENTS.md](AGENTS.md) 和
[flows/README.md](flows/README.zh-CN.md#每个流程都遵循同一份约定) 中。Agent
绝不伪造批准、审核结果或提交记录。

## 现状

脚本应用依赖的工作已于 2026-09-26 合入各仓库的 `main`；请使用各仓库的 `main`。

| 部分 | 状态 |
| --- | --- |
| `hub` 中的脚本应用准入检查、扫描与 `os.` id 检查 | 已在 App Hub `main`（[OctoSense-App-Hub#4](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/4)，合并为 `0d36f50b`）。本仓库文档基于其合并前的提交 `79a2c4f` 验证，并于 2026-09-26 在 `main` 上端到端重新跑通。 |
| 运行时中的隔离脚本应用与宿主服务 | 已在 makepad `main`（[OctoSense-org/makepad#30](https://github.com/OctoSense-org/makepad/pull/30)，合并为 `cd812acd`，现为 `c155f61d`），由 `native-runtime.lock.json` 固定的 Octoscript-Makepad `2cc5ef37` 选定。合并前在 `d94e5e6` 验证。 |
| Shell 中的系统应用与商店应用 | 已在 [OctoSense](https://github.com/OctoSense-org/OctoSense) 的 `main`，桌面端 Shell 与手机 Home 均包含（仓库合并前分别以 OctoSense-Desktop [#36](https://github.com/OctoSense-org/OctoSense/pull/36) 和 OctoSense-ROM #18 合入）。 |
| 提交途径 | 在 OctoSense-App-Hub 开一个 issue（见下文），如 App Hub 的 [PUBLISHING § Submitting](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#submitting) 所述。其中提到的索引仓库和 release action 尚不存在。 |
| 在手机上安装自己的应用包 | 不支持。见[运行应用](#运行应用)。 |

[docs/QUICKSTART.md §1](docs/QUICKSTART.md#1-prerequisites) 列出了确切版本以及搭建工作区的命令。

## 快速上手

前置条件（[QUICKSTART §1](docs/QUICKSTART.md#1-prerequisites)）：

- Rust（stable，通过 rustup 安装），并把 `~/.cargo/bin` 加入 `PATH`。
- Python 3.9 或更新版本（`tools/octo` 不需要额外的包；macOS 自带的 `/usr/bin/python3`
  3.9 即可）。
- 图形会话：`card-host` 会打开一个真实的 412x892 点窗口，即便由 Agent 驱动也是如此。
- 一个工作区目录，同时放置本仓库和它的兄弟仓库，因为 App Hub 的 `Cargo.toml` 把 Makepad
  和 Octoscript 指向这些路径：

  ```text
  <workspace>/
    OctoScript-App-Design-Flow/   this repository
    OctoSense-App-Hub/            hub, card-host, appstore
    makepad/                      OctoSense-org/makepad
    octoscript-makepad/           OctoSense-org/Octoscript-Makepad
    octoscript/                   OctoSense-org/Octoscript
  ```

然后创建工作区，并在本仓库中构建和使用这些工具：

```sh
# 0. The workspace: clone this repository and the App Hub side by side, then
#    let setup-native.py add makepad, octoscript and octoscript-makepad
mkdir octosense-ws && cd octosense-ws
git clone https://github.com/OctoSense-org/OctoScript-App-Design-Flow.git
git clone https://github.com/OctoSense-org/OctoSense-App-Hub.git
cd OctoScript-App-Design-Flow && python3 tools/setup-native.py

# 1. Build the two tools once (in the App Hub checkout)
(cd ../OctoSense-App-Hub && cargo build --release -p octosense-card-host -p octosense-app-hub)
tools/octo doctor                                        # finds hub and card-host; prints fixes if not

# 2. Create an app from the template
tools/octo new ~/apps/my-app --id my-notes --name "My Notes"

# 3. Run it in a real window with the remote-control bridge
tools/octo run ~/apps/my-app/bundle --port 8141 --detach
#    Agent 和脚本请加 --hidden（无头模式：不占用你的屏幕，
#    可同时运行多个应用，每个用自己的 --port；见 QUICKSTART §4a）
curl -s "127.0.0.1:8141/snap?q=Notes"                    # what is on screen

# 4. Iterate: edit bundle/main.splash, then quit and run again
curl -s 127.0.0.1:8141/quit
tools/octo run ~/apps/my-app/bundle --port 8141 --detach

# 5. Capture a real screenshot, then check against the App Hub gate
tools/octo shot 8141 ~/apps/my-app/bundle/screenshots/01-main.png
curl -s 127.0.0.1:8141/quit
tools/octo check ~/apps/my-app/bundle                    # hub stamp + hub check

# 6. Publish: print the checklist and follow docs/PUBLISHING.md
tools/octo package-help
```

预期结果：

- `new` 输出 `created …` 和 `bundle stamped`。
- `run --detach` 在 `card-host` 输出
  `card-host: my-notes 0.1.0 admitted — capabilities {"storage"}, …`、远程桥已在你的 `--port` 上监听、
  并且第一帧完整画出（`ready: first frame drawn`）之后才返回；之后可以立即点击或 `shot`。
  如果端口已被占用，它以状态 1 退出，指出占用端口的应用，并给出停止它的 `curl -s 127.0.0.1:<port>/quit`。脚本错误会出现在
  `<app>/.local-state/card-host.log` 中 `[SPLASH] eval:` 之后。
- 对刚复制出来的模板执行 `check`，会被**有意拒绝**：
  `[refused] listing: screenshots/01-main.png is named by the listing but is not in the bundle`。
  有了真实截图后才会通过（`my-notes 0.1.0 — PASSED`，外加未签名警告）。绝不要放一张假图。
  `check` 还会提示 `listing.json` 中模板留下的发布者占位文本，必须由人替换。

完整流程及每一步经过验证的输出见 [docs/QUICKSTART.md](docs/QUICKSTART.md)。

## `tools/octo`

需要 Python 3.9+，无第三方依赖。用 `tools/octo <command> -h` 查看参数。

| 命令 | 作用 |
| --- | --- |
| `doctor` | 检查 Python，查找 `hub` 与 `card-host`（排除 GitHub 那个同名的 `hub` CLI），检查模板，并输出缺失项的修复方法。 |
| `new <dir> [--id ID] [--name NAME] [--system]` | 复制 `templates/script-app`（`bundle/`、`AGENTS.md`、`.gitignore`），设置 id、名称和版本 `0.1.0`，并 stamp 应用包。id 格式为 `[a-z0-9.-]{1,64}`；`os.*` 需要 `--system`。 |
| `run <bundle> [--port N] [--hidden] [--detach] [--system] [--no-stamp] [--app-data DIR] [--static PREFIX=DIR]` | 以 `MAKEPAD_REMOTE=<port>`（默认 8141）运行 `card-host --bundle … --app-data … --allow-unsigned --stamp`。端口已被占用时拒绝运行。`--detach` 在应用通过准入、远程桥开始监听并画出第一帧后返回。应用的 jail 在 `<app>/.local-state/<id>/`。 |
| `shot <port> <out.png> [--settle S]` | 等应用的控件出现、且连续两帧相同（最多 `--settle`，默认 2 秒）后，保存运行中窗口的 PNG（`GET /g?raw=1`）。 |
| `check <bundle> [hub check flags]` | 先 `hub stamp`，再 `hub check --allow-unsigned`；被拒绝时以非零状态退出。不会对已签名的 manifest 重新 stamp。 |
| `package-help` | 输出发布检查清单。 |

二进制的查找顺序：`$OCTO_HUB` / `$OCTO_CARD_HOST`，然后
`$OCTOSENSE_APP_HUB/target/release`、`$CARGO_TARGET_DIR/release`、
`$OCTOSENSE_APP_HUB/../target/release`、`../OctoSense-App-Hub/target/release`、
`../target/release`，最后是 `PATH`。

## 设计流程

一个设计流程把一种输入变成 OctoSense 能运行的东西。每个 `FLOW.md` 先给出前置检查，然后是
编号步骤，每一步都有命令和通过条件，并标明需要人把关的节点。

| 流程 | 起点 | 产出 | 步骤清单 |
| --- | --- | --- | --- |
| script-app | 一段文字需求：应用做什么、有哪些界面、数据、状态和要访问的主机 | 一个隔离运行的脚本应用包（`manifest.json`、`listing.json`、`main.splash`、`assets/`、真实截图），能通过准入检查 | [flows/script-app/FLOW.md](flows/script-app/FLOW.md) |
| image-to-card | 一张生成的 UX 图：一个服务流程 8–12 个界面的合图（atlas），或单个界面 | 原生 L0 卡片（`page.card`、`page.data.json`、`kit/`）、拆分出的服务卡片、一个卡片应用包，可选 WASM | [flows/image-to-card/FLOW.md](flows/image-to-card/FLOW.md) |
| kits/sketch | 一套有授权的 Sketch 设计套件 | 一个**主题套件**（原生 L0 组件与主题），不是应用；供其他流程使用 | [flows/kits/sketch/FLOW.md](flows/kits/sketch/FLOW.md) |

文字需求请用 script-app：这是 `tools/octo` 从头到尾自动化的唯一路径。图像和 Sketch 流程
需要 macOS、Python 3.12、各自的虚拟环境，原生截图还需要 Makepad Studio；各自的 FLOW.md
列出了前置条件。所有应用类流程的交接环节相同（stamp、检查、在 `card-host` 中运行、截图、
签名、提交），详见 [flows/README.md](flows/README.zh-CN.md#每个流程都遵循同一份约定)。

## 应用是什么

OctoSense 应用是一个小巧、隔离运行的应用包。只有 `bundle/` 会被提交；应用仓库里的其他
内容都不放进去。

```text
my-app/                     the app's own git repository
  AGENTS.md  .gitignore     copied by tools/octo new; not submitted
  BRIEF.md  build/          your brief, hub scan's review packet; not submitted
  .local-state/             card-host's jail and log; not submitted
  bundle/                   THE SUBMISSION
    manifest.json           id, name, version, capabilities, hosts, integrity
    listing.json            what the store shows
    main.splash             the program (a card app has page.card + kit/ instead)
    assets/icon.svg         the icon the listing names
    screenshots/01-main.png real captures, 1 to 8, named by the listing
```

**`manifest.json`**：`schema`、`id`、`name`、`version`（每次发布都要新版本）、
`capabilities`（申请的权限）、`network.hosts`（纯主机名，需配合 `net`），以及由
`hub stamp` 写入的 `integrity.bundle_blake3`（`hub sign-manifest` 之后还有签名）。可选的
申请项（`storage.max_bytes`、`compute.*`、`agent`）会被限制在宿主的上限以内；
`hub check` 输出的 `grants:` 行就是实际授予的结果。`storage` 还可以声明应用是否按账户
保存数据、它的 Agent 能读什么（`storage.accounts`、`storage.agent_workspace`）。应用 id
不能是、也不能以宿主保留的名字结尾（`terminal`、`rinx`、`system`、`toolbox` 等）。

**Capabilities（权限）** 是 App Hub 定义的封闭列表：`storage`、`net`、`images`、`web`、
`camera`、`microphone`、`library`、`location`、`mail`、`llm`、`news`、`glance`、`model`、`research`、`crawl`、`prompt`、`ledger.read`、
`clipboard`，另有 49 个精确的宿主服务名（设备助手的 4 个 `octos.*`，Rinx 的 45 个 `matrix.*`）。未申请即不授予；安装前商店会为每项权限向用户显示一行通俗说明。只申请应用真正
需要的。每项权限解锁什么、哪些目前还没有可用路径（`prompt`、`ledger.read`、`clipboard`）、
哪些只有系统应用能用（`llm`、`news`，以及暂时的 `research` 和 `crawl`）：[docs/CAPABILITIES.md](docs/CAPABILITIES.md)。
助手相关权限和应用自己的 Agent 目前在 OctoSense 中能做什么：
[docs/AI-SERVICES.zh-CN.md](docs/AI-SERVICES.zh-CN.md)。

**`listing.json`**：副标题、描述、类别、关键词、图标、截图、实际测试过的平台、年龄分级，
以及发布者信息（名称、支持方式、https 隐私政策 URL）。合法取值见
[docs/PUBLISHING.md §3.2](docs/PUBLISHING.md#32-finalize-the-listing)。

**`main.splash`**：程序本身，由 Makepad Script 在 Splash 隔离环境中求值，
无需 Rust 编译；它与 Octoscript L0（`page.card`）的解析路径不同。顶层是
`let` 状态和 `fn`，然后是一个根组件；由于 `ui` 在主体执行后才注入，请用
`start_timeout(0.05, || boot())` 启动逻辑。源码中的 `{{assets}}` 会被替换为提供应用包内容
的本地回环地址（`http_resource("{{assets}}/thumbs/a.jpg")`）。应用可以调用的全部内容，
以及最费时间的坑：[docs/SCRIPT-API.md](docs/SCRIPT-API.md)。

## 隔离规则

每个应用运行在自己的隔离环境中，只拥有 manifest 申请的授权。大部分规则由准入检查
（`hub check`，与 hub 运行的是同一份代码）强制执行；全部检查项见
[docs/PUBLISHING.md §2](docs/PUBLISHING.md#2-the-rules-the-gate-enforces)。

- **应用中不得有密钥或密码。** 不得有密码、PIN 或一次性验证码输入框，不得有登录表单，
  应用包中不得有 API key 或 token。准入检查会拒绝 `is_password: true` 以及密码、验证码
  类型的输入，运行时也会让这类输入框失效。登录在宿主自有面板上完成。
- **声明每一个主机。** `.splash` 文件只能访问 `network.hosts` 中列出的 `https://` 主机
  （除非应用获得了 `images` 或 `web` 权限）。`http://`、`file://` 和 `../` 一律拒绝。
- **只放应用包文件。** 允许的扩展名为
  `.card .json .l0 .octoscript .splash .svg .png .jpg .jpeg .webp .ttf .otf .txt .md`；
  不得有脚本、压缩包、二进制或符号链接；总大小不超过 8 MB。
- **特权操作交给宿主服务。** 应用调用 `host.request("<family>.<method>", args, fn(r){…})`，
  其中 family 必须是已授予的权限。Mail 是完整示例（`mail.accounts`、`mail.add_account`、
  `mail.list`、`mail.send` 等）：服务弹出自己的面板收集密码，并把密码存进平台的密钥存储，
  位于任何应用的 jail 之外。`<family>.sheet.*` 方法只接受来自面板的调用。新增宿主服务是对
  Shell 的修改，而不是对应用包的修改：[docs/HOST-SERVICES.md](docs/HOST-SERVICES.md)。
- **商店应用与系统应用。** `os.` 开头的 id 保留给系统应用：准入检查会拒绝，任何商店也不会
  安装。系统应用（[OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps)
  中的 News、Photos、Maps、Camera、Mail、AI providers）应用包结构相同，随 Shell 一起发布，上限更高
  （例如存储为 64 MiB 而不是 16 MiB）。`tools/octo new --system` 和
  `tools/octo run --system` 用于开发系统应用。其余都是商店应用，只通过签名的 App Hub 目录分发。

## 应用中的 AI

OctoSense 每个 Shell 运行一个 octos Agent 内核，由用户在系统应用 AI providers 中配置；
密钥永远不会到达应用。内核上运行着**系统 Agent**（Shell 自己的助手，用户在系统对话中与它交谈），
以及每个声明了 Agent 的应用各自的**应用 Agent**，每个都在宿主持有的独立 peer 上。
截至 2026-10-01，在 OctoSense `main` 上（细节与出处见
[docs/AI-SERVICES.zh-CN.md](docs/AI-SERVICES.zh-CN.md)）：

| 应用可以 | 方式 | 在 `card-host` 中 |
| --- | --- | --- |
| 进行一次性、按 schema 校验的模型调用 | `model` 权限，`host.request("model.complete", …)`，受每日预算限制 | `no service answers "model"` |
| 在自己的界面上与助手对话 | 4 个 `octos.*` 权限，用户在首次使用的确认页上允许该应用的 Agent 之后 | `no service answers "octos"` |
| 拥有自己的 Agent：用户可以直接与它对话（Shell 为每个有 Agent 的应用绘制的“Ask <app>”面板、卡片内对话、应用自己的界面），系统 Agent 也可以把任务交给它 | `agent` 块（`"tools": ["ask_user_question"]`），可选 `tools.json`；该 Agent 可以读取应用的账户文件夹（`accounts/device/`） | 只能用 `hub check` 检查 |
| 向 glance 屏幕发布卡片，卡片内可与应用 Agent 对话，模型写的文字标为 AI 撰写 | `glance` 权限，`glance.publish`（L0 `sys.chat`、`model-copy`） | `no service answers "glance"`；本仓库锁定的开发运行时尚不支持 `sys.chat` 与 `ChatEntry` |

仍在**规划中**：商店应用自己的 `tools.json` 工具真正运行（目前只有系统应用的 host-service
工具能运行）、宿主根据 `needs` 为 Agent 选择模型、触发器与后台运行、安装 `AGENT.md` 和
skills，以及面向商店应用的系统工具箱。`llm` 是只供系统应用使用的模型提供方管理服务。
请把应用做成不依赖 AI 也完整可用；添加 AI 功能之前先读
[docs/AI-SERVICES.zh-CN.md](docs/AI-SERVICES.zh-CN.md)：准确的名称、一个经过验证并处理
“不可用”状态的调用、用户看到什么、错误信息，以及规划中的内容。

## 运行应用

**独立运行：在 `card-host` 中**（开发循环）。`card-host` 是 App Hub 为单个应用包提供的参考
隔离宿主。`tools/octo run` 启动它时会在本地端口开启 Makepad 的远程控制桥，人或 Agent 可以
通过 HTTP 操作真实窗口（均为 GET，坐标为窗口点，y 轴向下）：

| 路由 | 作用 |
| --- | --- |
| `/snap`（`?q=` 过滤） | 组件及其矩形和文本 |
| `/d` | 整棵组件树的文本形式 |
| `/click?x=&y=&wait=1` | 一次真实点击 |
| `/t?t=TEXT&wait=1` | 向获得焦点的输入框输入文字 |
| `/k?k=down&c=ReturnKey` | 一个按键事件 |
| `/log?n=50` | 最近的日志行 |
| `/g?raw=1` | 窗口的 PNG（即 `tools/octo shot` 保存的内容） |
| `/quit`（或 `/gq`） | 退出；最后一定要调用 |

`on_render` 生成的控件与其他控件一样出现在 `/snap` 和 `/d` 中（自 makepad `d0a9def5` 起）；应用稍后才添加的内容（来自定时器或响应）在绘制后才出现，请轮询 `/snap?q=` 等待它。`card-host`
**不**注册任何宿主服务，所以类似 Mail 的应用在其中会得到
`no service answers "mail" on this device`。当前的 `card-host` 还会拒绝已签名的 manifest：
请在签名之前截图。

**在 Shell 中。** OctoSense 桌面端 Shell 和手机 Home 通过 App Hub 的 Card runner
（App Hub `crates/appstore` 中的 `card` 模块）运行应用，而不是 `card-host` 本身；它执行同一套
manifest 策略。系统应用从 OctoSense 的 `apps/` 打包进 Shell 构建；商店应用从 App Hub 商店、
依据签名目录安装。想在发布前在桌面 Shell 中试用自己的应用：用一次性信任锚把它发布到本地目录，再把
桌面端 Shell 的 `OCTOSENSE_HUB` / `OCTOSENSE_HUB_ANCHOR` 指向该目录；其 App Hub
即可安装并打开该应用（已在 macOS 上验证，
[PUBLISHING §4](docs/PUBLISHING.md#4-rehearse-the-store-path-locally)）。

**目前在手机上**（[QUICKSTART §9](docs/QUICKSTART.md#9-run-it-on-an-octosense-phone)）：

- 无法把任意应用包侧载到普通 OctoSense 手机上。手机商店读取内置的 hub，只信任编译进构建的
  信任锚；`OCTOSENSE_HUB` / `OCTOSENSE_HUB_ANCHOR` 是环境变量，Android 启动器不会设置。
  在设备上从本地目录安装不受支持，也未经验证。
- 最接近的已验证路径在桌面端：用一次性信任锚发布到本地目录，再用 App Hub 的独立
  `appstore` 安装（[PUBLISHING §4](docs/PUBLISHING.md#4-rehearse-the-store-path-locally)）。
  独立商店不能打开应用；把桌面端 Shell 指向同一目录即可安装并打开。
- `card-host` 的远程控制桥在 Android 上被编译移除；手机测试使用 Shell 自己的测试工具，
  而不是 `tools/octo`。
- 发布之后，应用会通过签名目录出现在每台手机的商店中。

## 无头测试：同时测多个应用，不占屏幕

Makepad 有无头（headless）模式：应用运行时窗口**从不显示、也不抢焦点**，而远程控制桥
（`/snap`、`/click`、`/t`、`/g` 截图）照常工作。凡是由 Agent 或脚本操作应用，都应使用它：
不会占用你的屏幕和键盘，还能同时测试多个应用，或同一应用的多个副本，彼此不争抢显示器。

```sh
tools/octo run apps/tip-split/bundle      --port 8161 --hidden --detach
tools/octo run apps/unit-converter/bundle --port 8162 --hidden --detach
curl -s "127.0.0.1:8161/snap?q=Button"        # 每个应用在自己的端口上响应
tools/octo shot 8161 tip.png && tools/octo shot 8162 conv.png
curl -s 127.0.0.1:8161/quit; curl -s 127.0.0.1:8162/quit
```

- `--hidden` 会设置 `MAKEPAD_HIDE_WINDOWS=1`；所有 Makepad 应用都支持它，包括 OctoSense 的 Shell。
- 每个应用用自己的 `--port`（端口已被占用时 `run` 会拒绝运行）；同一个应用包运行两份时，每份用自己的 `--app-data`。
- 截图由应用自身渲染，即使屏幕上什么都没有，截图也是完整的。
- **脚本化 UI 测试：** makepad 的 [`makepad_test`](https://github.com/OctoSense-org/makepad/tree/main/libs/makepad_test)
  测试框架会以隐藏窗口启动应用、通过同一个控制桥操作它，并在测试失败时保存截图、组件树和日志；
  设置 `MAKEPAD_TEST_PARALLEL=1` 可并发运行多个测试（每个测试一个隐藏应用）。
  配置方法和 `card-host` 示例见 [QUICKSTART §4a](docs/QUICKSTART.md#4a-headless-test-without-the-screen-several-apps-at-once)（英文）。

2026-09-27 在 macOS（Apple silicon）上验证：两个应用以隐藏窗口并行运行，同时发给两者的点击各自改变了对应应用的状态，
两张截图都正确；`makepad_test` 示例测试通过。

## 发布

分步流程见 [docs/PUBLISHING.md](docs/PUBLISHING.md)；`tools/octo package-help` 会输出
其检查清单。契约本身属于 App Hub（见其
[PUBLISHING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md)）。
简要步骤：

1. 定稿 `manifest.json`（新版本号、最少权限、列全主机）和 `listing.json`（没有占位文本；
   发布者字段由发布者本人填写）。
2. 用 `tools/octo shot` 截取真实截图，并逐张查看。
3. 反复执行 `tools/octo check <bundle>`，直到输出 `— PASSED` 且只剩未签名警告。可加
   `--catalog <App Hub catalog.json>` 以发现重复版本号或发布者密钥变化。
4. `hub scan <bundle> --packet build/review.json`，书面回答其中七个审核问题。
5. **由人完成：** `hub keygen`（只需一次，放在任何仓库之外）、
   `hub sign-manifest <bundle> --key … --key-id <publisher-id>`，然后
   `hub check <bundle> --publisher-key <id>=<hex>`。签名后任何修改都需要重新 stamp 并签名。
6. **由人完成：** 在应用的公开仓库中为该提交打 tag，并在
   [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub/issues) 开一个
   标题为 `Submit <app id> <version>` 的 issue，附上仓库、tag、提交、应用包路径、发布者公钥、
   `hub check` 输出和扫描问题的回答。

维护者会在完全相同的字节上重新运行准入检查和扫描，再执行 `hub publish`：把应用包复制进 hub
并签署新的目录。

限制，如实说明：

- issue 途径即 App Hub `main` 所描述的途径（见[现状](#现状)）；其中提到的索引仓库和
  `octosense-org/publish-app` action 尚不存在。提交前请重新阅读 App Hub 的 "Submitting" 一节。
- 绝不要开编辑 App Hub `catalog.json`、`index/` 或 `artifacts/` 的 pull request：只有持有
  hub 密钥的 `hub publish` 能写入它们。
- 首次提交一定会等待人工处理。老发布者自动合并尚在计划中，未实现。
- 准入检查不评判截图、listing 文本或隐私政策；这些由审核人负责。

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | 给编码 Agent 的规则、完成标准和汇报方式 |
| [flows/](flows/README.zh-CN.md) | 设计流程：[script-app](flows/script-app/FLOW.md)、[image-to-card](flows/image-to-card/FLOW.md)、[kits/sketch](flows/kits/sketch/FLOW.md)；共享代码在 [core/](flows/core/README.md)（策略、审核、修复、准入；[NATIVE-INSTRUMENT.md](flows/core/NATIVE-INSTRUMENT.md) 是原生测试手册）和 [image-lib/](flows/image-lib/README.md) |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | 唯一路径：构建工具、创建、运行、修改、检查、手机、发布 |
| [docs/SCRIPT-API.md](docs/SCRIPT-API.md) | Splash 语言及隔离应用可调用的全部 API |
| [docs/CAPABILITIES.md](docs/CAPABILITIES.md) | 每项权限：解锁什么、用户看到什么、规则 |
| [docs/HOST-SERVICES.md](docs/HOST-SERVICES.md) | `host.request`、面板、“密钥归宿主所有”、新增宿主服务 |
| [docs/AI-SERVICES.zh-CN.md](docs/AI-SERVICES.zh-CN.md)（[English](docs/AI-SERVICES.md)） | OctoSense 的助手（octos）：系统 Agent 与应用 Agent、应用目前能用什么、经过验证的示例、应用自己的 Agent 及其工具、系统工具箱、glance 卡片、`sys.digest`、AI 撰写的文字与卡片内对话（`sys.chat`），附带日期的状态表 |
| [docs/PUBLISHING.md](docs/PUBLISHING.md) | 发布到 App Hub，附经过验证的输出和检查清单 |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | 每个术语只有一个含义 |
| [docs/NATIVE-WORKSPACE.md](docs/NATIVE-WORKSPACE.md)、[docs/l0/](docs/l0/) | 原生运行时的兄弟仓库配置；L0 卡片示例 |
| [templates/script-app/](templates/script-app/README.zh-CN.md) | `tools/octo new` 复制的可运行模板（“My Notes”） |
| [templates/card-app/](templates/card-app/README.zh-CN.md) | 指向卡片应用路径的说明 |
| [examples/](examples/README.zh-CN.md) | image-to-card 完整示例项目 |
| [tools/octo](tools/octo) | 上文介绍的命令行工具 |
| `tools/setup-native.py` | 在本仓库旁准备锁定版本的 Octoscript-Makepad 运行时（[native-runtime.lock.json](native-runtime.lock.json)） |
| `tools/image-to-appcard-flow.sh`、`tools/beauty-pipeline.sh`、`tools/beauty-studio.sh` | image-to-card 与套件流水线的入口 |
| `tools/check-links.py` | 检查 Markdown 相对链接能否解析（CI 中运行） |

## 示例

用 image-to-card 流程构建的参考流程。每个示例自带设计源文件、审核过的卡片场景、服务代码和测试。

| 示例 | 形态 | 内容 |
| --- | --- | --- |
| [Aircon](examples/aircon/README.zh-CN.md) | 原生卡片 / WASM | 从购买到安装的完整流程：12 个界面状态，14 个服务卡片变体 |
| [School](examples/school/README.zh-CN.md) | 原生卡片 / WASM | 学校通知、日历与缴费 |
| [Health](examples/health/README.zh-CN.md) | 原生卡片 / WASM | 虚构的体检预约 |
| [Reunion](examples/reunion/README.zh-CN.md) | 原生卡片 / WASM | 聚会筹划、回复与付款 |
| [Calendar](examples/calendar/README.zh-CN.md) | 原生卡片 / 浏览器预览 + 同步服务器 | 两台设备共用一份日历，附基于 SQLite 的同步服务器 |

脚本应用的完整示例是 [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps)
中的第一方应用包（`apps/<name>/bundle/`），以及 [templates/script-app](templates/script-app/README.zh-CN.md)。

## 参与贡献

- 从 `main` 建分支并提 pull request；CI 必须通过。
- CI 运行 `python tools/check-links.py`（受版本管理的 Markdown 中的相对链接必须能解析），并在
  macOS 上用 `tools/setup-native.py` 准备原生运行时，运行 flow、core、Sketch 和维护相关的单元测试
  （见 [.github/workflows/ci.yml](.github/workflows/ci.yml)）。
- 保持文档真实：文档中的每条命令都实际运行过，没运行过的标注 **unverified**。运行时或 `hub`
  与文档不一致时，修正文档，或附上复现步骤报告问题。
- 对运行时、准入检查、Shell 或系统应用的修改属于各自的仓库（见下），不在这里。
- 不要提交购买的设计素材、密钥、`.local-state/` 或本地日志。

## 相关仓库

| 仓库 | 作用 |
| --- | --- |
| [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) | 签名目录、准入检查、`hub`、`card-host`、商店与 Card runner |
| [OctoSense](https://github.com/OctoSense-org/OctoSense) | Shell 及其内置的一切：桌面端 Shell（`desktop/`）、手机 Shell Home（`phone/`，可作为 Home 应用安装，也可放进由 `rom/` 构建的 ROM 镜像），以及第一方应用和它们的宿主服务（`apps/`）。原为 OctoSense-Desktop、OctoSense-ROM 和 OctoSense-System-Apps 三个仓库。 |
| [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps) | 第一方应用（News、Photos、Maps、Camera、Mail、AI providers）及其宿主服务（`mail`、`llm`） |
| [OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard) | AppCard 助手（`octos-app`，在 Shell 中需 `--features app-appcard` 才启用）；L0 解析器/检查器位于 Octoscript，Makepad 转换/渲染层位于 Octoscript-Makepad；Splash 隔离环境和组件位于 makepad |
| [OctoSense-org/makepad](https://github.com/OctoSense-org/makepad)、[Octoscript](https://github.com/OctoSense-org/OctoScript)、[Octoscript-Makepad](https://github.com/OctoSense-org/OctoScript-Makepad) | 应用运行所依赖的框架与语言 |

## 许可证

Apache-2.0；见 [LICENSE](LICENSE) 和 [NOTICE](NOTICE)。
