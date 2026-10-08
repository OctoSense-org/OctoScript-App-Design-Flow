# Inbox Assistant 示例

[English](README.md) | 简体中文

这是普通 App Hub 应用 `org.octosense.samples.inbox`。它可选择连接 Gmail，并让 Email、Reply、Chat 三个标签页和宿主的发送确认共用同一份已保存的回复。它不依赖内置的 `os.mail` 应用，也不借用其身份。

首次启动显示明确标注为虚构的收件箱，无需账户即可编辑，但不能发送邮件。在配置好的 OctoSense 宿主上，**Connect Google** 会打开共享 OAuth 服务；应用只获得绑定账户的句柄，不获得密码、授权码、访问令牌或刷新令牌。

0.1.1 版已从 [ymote/octosense-inbox-assistant](https://github.com/ymote/octosense-inbox-assistant) 发布到 App Hub。它的 `inbox.notify` 工具只接受应用包内的速览卡片模板，`AGENT.md` 和分拣技能也写明了这一点。本目录是 0.1.1 的未签名开发副本：`listing.json` 中发布者字段是占位内容，`manifest.json` 没有签名；其余文件都与发布版一致。[参考应用指南](../README.zh-CN.md)说明了应用的构成，以及复用前需要修改什么。

## 已实现的功能

- 通过 `gmail.messages` 和 `gmail.message` 读取收件箱、重要邮件和已发送文件夹；应用不直接联网，也不接触提供商凭据。
- 向一位收件人回复纯文本。宿主保存发件人、原始邮件与会话头、递增的版本号、待处理的发送确认和发送回执。
- 在 Reply 和 Chat 之间切换时，应用会先保存编辑。Chat 通过 `octos.session.open` 和 `octos.turn.start` 打开此账户的应用 Agent。它的 Inbox 工具已经准入，读写同一份已保存的草稿，界面随后读取实际保存的结果。版本检查和本地输入保护防止过时的结果悄悄覆盖新内容。
- 声明的 `inbox.new_message` 事件把新的 Gmail 邮件 ID 交给已获授权的应用 Agent 及其附带的分拣技能。首次连接只把当前位置记为基线，之后到达的邮件才会触发，不会为整个旧邮箱发通知。只有应用 Agent 记录了静默决定，或宿主确认卡片已发布，事件才算处理完成。处理失败时按同一个 ID 重试。任何事件都不能批准发送。
- **AI sort** 判断所选邮件是否与用户本人相关。默认关注医疗、配送、日程、学习或工作，以及家庭活动；普通订阅邮件和营销邮件不发通知。相关的结果可以发布速览卡片和通知。**Pin** 是手动、不发通知的操作。
- 已发布的卡片加载已准入的 `glance-workspace.splash` 模板，与应用共用控制逻辑，保持原来的连接和邮件，并通过宿主读取完整的邮件内容。模型提供相关性判断和概要；宿主提供已准入的交互界面和账户绑定。
- **Review & Send** 请宿主显示完整、不可修改的邮件。只有在原生控件上亲手点按才能批准发送。脚本、模型、`from_sheet` 标志、自动化点击或开发者模式都不能批准。
- Gmail 接受提交后，对应的速览卡片会撤下。Gmail 接受与收件人送达分开记录。结果不明时禁止自动重试。

这里有一个工具声明不宜照搬：`inbox.draft_edit` 在后台运行，可以改掉回复的 `to` 地址。0.1.0 版还有第二个：它的 `inbox.notify` 还接受 `script`、`source` 和 `data`，因此在 desktop-v0.1.0-beta.2 上，一轮遭到提示注入的后台对话可以发布任意 Splash 代码。在 0.1.1 和本副本中，`inbox.notify` 必须提供已准入的 `glance-workspace.splash` 模板、`initial.message`、`card_id`、`title`、`summary` 和 `notify`，它的封闭 schema 中没有 `script`、`source` 或 `data`。OctoSense `main` 也会拒绝任何 Agent 工具中的 `script`（尚未进入任何发布版本）。见[哪些可以照搬，哪些不要照搬](../README.zh-CN.md#哪些可以照搬哪些不要照搬)。

## 运行要求与限制

本示例需要 OctoSense desktop-v0.1.0-beta.2 或更新版本中的共享 OAuth 和 Gmail 服务（`crates/oauth-service`）。它使用以下宿主操作：

| 服务 | 操作 |
| --- | --- |
| `auth` | `connect`、`active`、`disconnect` |
| `gmail` | `messages`、`message`、`draft.open`、`draft.get`、`draft.edit`、`draft.review`；`event.status` 和 `event.decide`，即应用 Agent 对单封邮件的分拣记录；`events.status`，即检查新邮件基线是否就绪的只读操作 |

`inbox.*` 工具映射到这些宿主方法，没有一个能批准发送。OAuth 请求中的 `mail.read` 和 `mail.send` 是宿主为对应 Google 权限定义的别名。

beta.2 没有内置的提供商注册信息，所以宿主管理员需要按[宿主配置指南](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/crates/oauth-service/README.zh-CN.md)配置已注册的 OAuth 客户端；宿主构建时已编入分发者注册信息的，不需要这一步。用户在宿主和浏览器中完成 Google 授权。Gmail API 访问，以及 OAuth 同意界面和测试用户限制，需要在 Google 一侧配置。普通的独立 `card-host` 不注册提供商或模型服务，会如实报告它们不可用。Android 上的 Google 授权尚未实现，因此目前没有手机能走完这个流程。

允许后台执行时，Shell 的邮件收集器每 5 分钟检查一次当前已授权的账户。失败的对话或缺少持久化决定的邮件，之后可以重试；Android 可能推迟静默任务。收集器和应用 Agent 的工具路由已包含在 OctoSense desktop-v0.1.0-beta.2 中。0.1.0 发布前，macOS 验收跑通了这条生产流程：推理使用真实 DeepSeek，Gmail 使用仅测试构建可用的模拟实现。真实 Google OAuth 和真实 Gmail 送达仍未验证。[集成证据](evidence/integrated/README.md)记录了源码哈希。

**尚未支持：** 跨应用预约日程、把聊天内容提升到系统记忆、超过前 30 封邮件的翻页、附件、全部回复、HTML 回复，以及重试和结果核对界面。**未验证：** Android、Windows 和 Linux。

### 测试新邮件通知

1. 连接账户，并允许应用 Agent 运行。
2. 保持收件箱列表打开，直到显示 **New-mail baseline ready**。该状态每 3 秒刷新一次；点 **Refresh** 会立即检查。
3. 向已连接账户发送一封新的测试邮件。收集器每 5 分钟检查一次；随后应用 Agent 分拣这封邮件，相关邮件会发布速览卡片。旧邮件不会触发通知。
4. 如果没有收到通知，请检查宿主的应用 Agent 设置。就绪状态只说明基线已经建立，不代表应用 Agent 的授权仍然开启。

## 开发与验证

在 App Flow 根目录运行：

```sh
tools/octo doctor
python3 examples/connected-apps/inbox/build_bundle.py
tools/octo run examples/connected-apps/inbox/bundle --port 8194 --hidden --detach
python3 examples/connected-apps/inbox/verify_native.py --port 8194
```

验证器会输出一行以 `PASS startup, second-message identity` 开头的结果。它通过真实的 Makepad HTTP instrument 操作虚构数据，检查启动、第二封邮件的身份、多行 Unicode 编辑、Reply 和 Chat 共享的保存状态、不可用的授权和应用 Agent 服务、测试数据禁止发送，以及文件夹的空状态和筛选状态。它会截取真实的 PNG，并记录源码和清单的哈希，覆盖 `evidence/` 中的文件。

检查重启后的恢复：

1. 用 `curl -s 127.0.0.1:8194/quit` 退出。
2. 再运行一次同样的 `tools/octo run` 命令。
3. 运行 `python3 examples/connected-apps/inbox/verify_native.py --port 8194 --restart-check`。它输出 `PASS restart: exact multiline Unicode draft and message identity retained`。
4. 用同一条 `curl` 命令退出。

核心测试位于 OctoSense 的 `crates/oauth-service/src/inbox.rs` 和 `inbox_events.rs`：

- 发送确认测试覆盖拒绝注入或混合来源的输入、版本冲突、过期、取消和跨应用的发送确认、先持久化再传输、重放保护、结果不明、MIME 和邮件头校验，以及一个模拟 Gmail 请求，用于检查会话、确切正文和单次提交。
- 事件测试覆盖分页、游标过期、持久化决定、重放、重试、账户隔离和有界队列恢复。

模拟传输成功不代表真实 Gmail 已送达。

已执行的检查和尚存的视觉、运行问题见[证据记录](evidence/README.md)。独立的测试数据不使用模型。另一次已安装的完整 Shell 运行使用真实 DeepSeek 和模拟 Gmail，没有使用真实 Google 账户或真实邮件。[macOS 持续测试报告](evidence/soak/README.md)增加了 610 秒内的 33 轮原生交互和冷启动恢复。它把两个尚未解决的 instrument 帧提交错误，与通过的草稿和状态检查分开记录，并记录了有界的 RSS 增长。

这些证据都早于 0.1.1 和本副本收窄 `inbox.notify` 的改动，记录的是旧应用包的哈希。这项改动通过了准入检查、`tools/test_connected_contracts.py` 和 App Hub 对 0.1.1 的准入；后者检查了签名商店安装、从 0.1.0 升级和 Agent 文件加载。它还没有经过新的原生运行或模型运行。

## 隐私

只有在宿主连接获得授权后，应用才能读取邮件内容。启用后台 Agent 后，该账户的应用 Agent 和配置的模型会读取新邮件以进行分拣。前台的 Chat 和 **AI sort** 也使用这个模型。Agent 授权与 Google 登录相互独立；关闭应用 Agent 即可停止模型分拣。手动阅读和编辑不需要模型。宿主凭据始终位于应用存储之外。

虚构草稿和所选的不透明连接句柄存放在应用的私有存储中。真实的回复草稿和提交记录由宿主保存，按应用和连接区分。退出登录会撤销对该连接的后续使用，但不会删除历史草稿或发送回执。速览卡片的发布记录只保存精简的账户和邮件绑定，以及一个工作区程序；完整的邮件内容通过已授权的服务加载。不要把应用私有数据、OAuth 配置、真实邮件截图或令牌提交到本仓库。所有附带的截图和测试数据都必须保持虚构。
