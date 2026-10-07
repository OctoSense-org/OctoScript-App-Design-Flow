# 宿主服务

[English](HOST-SERVICES.md) | 简体中文

未注明中文版的链接指向英文文档。

应用不能与邮件服务器建立 socket 连接，不能持有密码，也不能与设备通信。它改为调用**宿主服务**。宿主服务是 Shell 中的 Rust 代码，用 Shell 持有的资源完成工作，只把结果返回给应用。

分发器属于 App Hub（[OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) 中的 `crates/appstore/src/services.rs`）。服务属于 OctoSense：[OctoSense](https://github.com/OctoSense-org/OctoSense) 中的 `crates/shell`、`crates/ai-host`、`crates/oauth-service` 和 `apps/*/host-service`。下文未加标注的路径都在 OctoSense 中。

正在实现的宿主 API 方案见 [Host API v1](HOST-API-V1.zh-CN.md)：版本要求、发现、
签名后端操作、设备授权和脚本工具。该指南需要配套发布版本；不改变下文记录的
此前发布版本限制。

## 哪个 Shell 提供哪项服务

OctoSense 有两个 Shell：桌面端（`desktop/`）和手机 Shell，即 Home（`phone/`）。两者的标准构建都注册了下表中的全部服务。`crates/shell/src/apps.rs` 中的 `register_host_services` 注册面向应用的服务；`crates/ai-host/src/lib.rs` 注册 `llm`、`model` 和 `octos`。App Hub 的 `card-host` 不注册任何服务。

| 能力族 | 谁可以调用 | 服务代码 |
| --- | --- | --- |
| `mail` | 任何获得 `mail` 授权的应用 | `apps/mail/host-service` |
| `auth` | 任何获得 `auth` 授权的应用。申请数据权限时，还需要对应的能力族（`github`、`gcalendar` 或 `gmail`）；身份权限，以及 OctoSense `main` 上的后端登录，只需要 `auth`。 | `crates/oauth-service/src/host.rs`、`host_backend.rs` |
| `github`、`gcalendar` | 获得相应能力族授权的应用，通过 `auth` 建立的连接调用。在 OctoSense `main` 上，保存前的审阅界面与 `gmail` 一样由 Shell 提供。 | `crates/oauth-service/src/host_api.rs`；在 `main` 上还有 `crates/shell/src/connected_review.rs` |
| `gmail` | 获得 `gmail` 授权的应用，通过 `auth` 建立的连接调用。发信前的审阅界面由 Shell 提供。 | `crates/oauth-service/src/host_inbox.rs`、`crates/shell/src/connected_review.rs` |
| `glance` | 任何获得 `glance` 授权的应用 | `crates/shell/src/glance.rs` |
| `model` | 任何获得 `model` 授权的应用，受每个应用各自的每日预算限制 | `apps/ai-providers/host-service/src/complete/` |
| `octos` | 获得对应的精确 `octos.*` 名称授权的应用；用户允许该应用的 Agent 之后才能调用，且仅限托管 octos 内核的 Shell | `crates/ai-host/src/contained.rs` |
| `llm` | 仅限系统应用 | `apps/ai-providers/host-service` |
| `news` | 仅限系统应用 | `apps/news/host-service` |
| `calendar` | 仅限 Calendar（`os.calendar`） | `apps/calendar/host-service` |
| `photos`、`youtube` | 仅限对应系统应用的 `notify` | `crates/shell/src/glance_notice.rs` |

对于没有自己服务的其他系统应用，例如 Maps 和 Camera，`glance_notice.rs` 也会响应它们的 `<namespace>.notify`。

没有任何 OctoSense Shell 向已安装的应用提供 `prompt`、`ledger.read`、`clipboard`、`matrix.*` 或 `palpo.*`。Rinx 是 OctoSense 作为原生应用随附的 Matrix 客户端。用户可以把应用包作为迷你应用导入 Rinx，Rinx 只向这样导入的应用包提供 `matrix.*` 和 `octos.*`；这种导入方式不属于 App Hub 的安装途径。`research` 和 `crawl` 为应用的 Agent 授予工具箱中的工具，它们不是 `host.request` 的能力族（[AI-SERVICES § 系统工具箱](AI-SERVICES.zh-CN.md#系统工具箱)）。

有些服务要先完成配置才能使用，而且并非每个构建都有：

| 服务 | 前提 | 可用的构建 |
| --- | --- | --- |
| `auth`、`github`、`gcalendar`、`gmail` | GitHub 和 Google 的提供商注册信息。beta.2 只从 `<apps root>/.host/oauth/clients.json` 读取注册信息，这个文件由宿主的运维人员提供；用 OctoSense `main` 构建时，可以把注册信息编译进去（[CAPABILITIES § 限制](CAPABILITIES.zh-CN.md#限制)）。 | 用 OctoSense `main` 构建的版本，以及 desktop-v0.1.0-beta.2 发布版（macOS，Apple 芯片）。尚不支持：在 Android 上登录 Google。 |
| 使用 `backend` 提供商的 `auth` | 宿主的运维人员在 `<apps root>/.host/oauth/backends.json` 中注册的应用后端（[CAPABILITIES](CAPABILITIES.zh-CN.md#登录应用自己的后端)）。 | 仅限用 OctoSense `main` 构建的版本：macOS 和 Android 9 及以上版本使用宿主的 WebView，Windows 和 Linux 使用系统浏览器。iOS 不支持。 |
| `octos`、`model` | 用户在 AI providers 应用中添加的 AI 提供商。 | 所有标准构建；`octos` 仅限托管内核的 Shell。 |
| `mail` | 用户在 Mail 的面板上登录的账户。 | 所有标准构建。 |

**未验证**：在真实的 GitHub 和 Google 上使用已连接账户服务的大部分场景，以及在手机上登录 GitHub。[CAPABILITIES § 限制](CAPABILITIES.zh-CN.md#限制) 列出了实际运行过的内容；OctoSense 的 [`crates/oauth-service/README.zh-CN.md`](https://github.com/OctoSense-org/OctoSense/blob/main/crates/oauth-service/README.zh-CN.md#当前交付边界) 给出各平台的状态，包括凭据的存储方式。

如果没有服务能满足应用的需要，请为 Shell [新增宿主服务](#新增宿主服务)，不要在应用包里自行变通。商店应用申请了无人为它提供服务的能力时会得到什么，见 [CAPABILITIES](CAPABILITIES.zh-CN.md#商店应用用不上的能力)。

## 在应用中调用服务

```splash
host.request("mail.accounts", {}, fn(r){
    if r.is_ok && r.data.len() > 0 {
        ui.address.set_text(r.data[0].address)
    } else {
        ui.note.set_text(r.error)
    }
})
```

- 服务名的形式是 `<family>.<method>`。其中的能力族（family）本身就是一项能力，清单必须授予它（`"capabilities": ["mail"]`）。否则，隔离环境会直接拒绝这次调用，不把任何请求放入队列：回调立即运行，`r.is_ok` 为 false，`r.error` 为 `this app was not granted "mail", which "mail.accounts" needs`。
- `args` 可以是任何能序列化为 JSON 的值；服务以 JSON 形式接收它。
- 回调稍后在 UI 线程上运行，并收到 `r.is_ok`、`r.data`（服务返回的 JSON）和 `r.error`（失败时为字符串）。
- 如果当前 Shell 上没有服务响应这个能力族，回调会立即收到 `no service answers "<family>" on this device`。在 `card-host` 中，每次调用收到的都是这条消息。

参数格式、时间限制和拒绝情况，见 [SCRIPT-API § Host services](SCRIPT-API.md#host-services-hostrequest)。每项能力为脚本提供什么，见 [CAPABILITIES](CAPABILITIES.zh-CN.md#宿主服务)。

## 面板

有些输入只能由用户本人给出：密码、账户授权、发送确认。服务为此弹出一个**面板**。面板是一段 Splash 程序，由 Shell 绘制在应用之上，在独立的隔离环境中运行，不受任何应用的策略约束。应用不能打开面板，只有服务能打开（`ServiceHost::open_sheet`）。

面板调用的是同一个 `host.request`，它发出的调用到达时带有 `from_sheet` 标记。应用发出的任何 `<family>.sheet.*` 调用，分发器都会在服务收到之前拒绝。在 `card-host` 中（**✓ 已运行**）：

```text
mail.sheet.submit is for the host's sheet, not an app
```

因此，服务只从自己的面板接收密码。每次打开面板都会启动一个全新的程序，所以在已取消的登录中输入的密码不会保留下来。

面板只出现在前台应用之上。来自信息流中速览卡片或 Agent 工具的调用无法弹出面板，所以服务会拒绝这类调用，并用一句话提示用户打开应用，例如 Mail 会返回 `Signing in needs Mail open: open Mail to add an account.` 这句话。

带 `from_sheet` 标记的调用只能证明它出自面板中的程序，不能证明用户按下了什么。所以，必须由用户本人发起的发送或保存要经过原生控件：它在按下和点击时都检查 Makepad 的 `trusted_user_input()`。Gmail 的发送审阅界面在所有版本上都这样做；GitHub 和 Calendar 的保存在 OctoSense `main`（尚未进入任何发布版本）上也这样做，那里的 `sheet.save` 调用会得到 `Saving requires a physical activation of the native host review. Script and agent requests cannot approve it.` 这句话。在 desktop-v0.1.0-beta.2 上，GitHub 和 Calendar 的服务仍接受来自面板的 `sheet.save`，不做这项检查。

## 密钥归宿主所有

应用绝不收集密码、PIN 或一次性验证码，哪怕只是代为转交。以下三条规则保证了这一点：

- 在受策略约束的隔离环境中，运行时会让密码输入框失效（[SCRIPT-API § Gotchas](SCRIPT-API.md#gotchas)）。
- 准入检查会拒绝声明了密码或一次性验证码输入框的应用包（[PUBLISHING](PUBLISHING.zh-CN.md#2-准入检查的规则) 中的 `secrets` 检查）。
- 需要凭据的服务在自己的面板上索取凭据，并把它存进平台的密钥存储；这些存储都在所有应用的 jail（私有数据目录）之外。

Mail 在 macOS 和 iOS 上把密码存进钥匙串。在 Android 和其他平台上，它在宿主的密钥文件夹 `<home>/secrets/os.mail/` 中为每个账户保存一个文件：文件在 Android 上用 Android Keystore 密钥加密，在各平台上都仅限所有者访问（`apps/mail/host-service/src/vault.rs`）。已连接账户服务在 macOS、iOS 和 Android 上把提供商令牌存进 Mail 的存储，但使用自己的命名空间。在 Windows 和 Linux 上，它们使用系统凭据服务（Windows Credential Manager、Secret Service），绝不退回到文件存储（`crates/oauth-service/src/host.rs`）。

应用的 Agent 同样接触不到这些密钥：它在应用的账户文件夹中工作（[AI-SERVICES](AI-SERVICES.zh-CN.md#agent-在哪里工作storage)）。

如果应用需要某个服务上的账户，它需要的是对接该服务的宿主服务，而不是登录表单。GitHub 和 Google 已有现成的宿主服务（[CAPABILITIES § 使用已连接账户](CAPABILITIES.zh-CN.md#使用已连接账户)）。有自己账户体系的应用可以使用宿主的后端登录，但仅限 OctoSense `main`，并且要由宿主的运维人员注册该后端（[CAPABILITIES § 登录应用自己的后端](CAPABILITIES.zh-CN.md#登录应用自己的后端)）。应用包目前还不能自行注册后端（[App Hub#16](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/16)）。

## 完整示例：Mail

系统应用 Mail（`apps/mail/bundle/main.splash`）使用 `mail` 能力族，也就是 `mail` 能力授予的这组方法：

| 方法 | 参数 | 返回（`r.data`） |
| --- | --- | --- |
| `mail.accounts` | – | `[{id, address}]`，本应用可以使用的账户 |
| `mail.add_account` | – | 用户在 Mail 的面板上登录后返回 `{id, address}`。从速览卡片或工具调用时失败，返回 `Signing in needs Mail open: open Mail to add an account.` |
| `mail.remove_account` | `{account}` | `{}` |
| `mail.folders` | `{account}` | `[{id, name, role}]`，收件箱排在最前 |
| `mail.sync` | `{account, folder?}` | `{new, total}` |
| `mail.list` | `{account, folder?, offset?, limit?}` | `{folder, total, messages: [{id, sender, address, subject, preview, time, unread}]}` |
| `mail.message` | `{account, folder?, message}` | `{id, sender, address, subject, body, html, attachments, date, time}` |
| `mail.mark_read` | `{account, folder?, message}` | `{}` |
| `mail.review_send` | `{account, to, subject, body, compose_id?, expected_revision?, folder?, message?}` | `{review_required: true, compose_id, draft_id, revision}`。宿主打开自己的审阅界面；用户在那里批准之前，什么都不会发出。需要 Mail 处于前台。 |
| `mail.send` | – | 一律拒绝：`approval_required: use mail.review_send with Mail open, or open the reply card, then use the host's Approve & Send control. mail.send cannot authorize delivery.` |
| `mail.notify` | `{title, body, card_id?, priority?}`（title 1–80 个字符，body 1–600 个字符） | Mail 的通知卡片出现在速览栏上并发出通知后，返回 `{card_id, replaced, expires_at}`。Mail 的 Agent 以工具的形式调用它。 |
| `mail.sheet.submit` | 登录字段 | 仅限面板 |
| `mail.sheet.cancel` | – | 仅限面板 |

Mail 的 Agent 在同一个服务上还有自己的工具（`peek`、`draft`、`propose_reply`、`skip_event`、`publish_card` 等），完整列表见 `apps/mail/bundle/tools.json`。

`mail.add_account` 的工作过程：

1. 应用调用 `mail.add_account` 并等待。
2. 服务弹出登录面板。
3. 用户在面板中输入，面板调用 `mail.sheet.submit`。
4. 服务检查账户能否连接，把密码存进平台的密钥存储，再把不含密码的账户信息存进 `<host_dir>/mail/accounts.json`。
5. 服务关闭面板（`close_sheet_later`），并用 `{id, address}` 应答应用最初的请求。

只有登录过某个账户的应用才能使用这个账户。

## 新增宿主服务

新服务要修改的是 Shell 和 App Hub，而不是应用包。以下四项修改要一起完成：

1. **添加能力。** 在 `KNOWN_CAPABILITIES`（App Hub 的 `crates/app-contract/src/manifest.rs`，即应用契约）中为新服务的能力族添加一项能力，并在 `crates/app-policy/src/listing.rs`（`privacy_summary`）中加上一行隐私说明，在 `crates/app-hub/src/index.rs`（`permissions_summary`）中加上一行权限说明。能力缺少通俗说明时，`crates/app-hub/src/index.rs` 中的一个测试会失败。这个列表是有意封闭的；新增一个名称，就是一次需要评审的 App Hub 修改。
2. **编写服务。** 服务是一个实现 `HostService`（`octosense_appstore::services`）的 Rust crate。下面的示意代码未经编译；完整且经过测试的参考是 Mail 的 `lib.rs`：

   ```rust
   use octosense_appstore::services::{HostService, Replier, ServiceCall, ServiceHost};

   struct Weather;
   impl HostService for Weather {
       fn family(&self) -> &'static str { "weather" }
       fn call(&mut self, call: ServiceCall, reply: Replier, host: &mut dyn ServiceHost) {
           match call.method() {
               "today" => reply.send(Ok(serde_json::json!({"temp": 21}))),
               other => reply.send(Err(format!("weather has no method {other:?}"))),
           }
       }
   }
   ```

   | 名称 | 作用 |
   | --- | --- |
   | `call.app_id` | 调用方应用的清单 id。请按应用隔离所有状态。 |
   | `call.host_dir` | 只有宿主能访问的目录，位于所有 jail 之外：在 Shell 中是 `<apps root>/.host`，在 `card-host` 中是 `<app data>/.host`。 |
   | `call.may_prompt` | 在不能弹出面板的场合为 `false`：信息流中的速览卡片、Agent 的工具调用。此时请用一句话应答，提示用户打开应用；App Hub 在这些场合本来也会拒绝弹出面板。 |
   | `reply` | 可以移到工作线程，稍后再 `send`。超时之后的 `send` 会直接丢弃。 |
   | `host.open_sheet(source)`、`host.close_sheet()` | 弹出和关闭面板。在工作线程中改用 `close_sheet_later(app_id)`。凡是接收密钥的方法，都放在 `sheet.` 之下。 |
   | `HostService::timeout` | 默认 60 秒；面板显示期间暂停计时。慢服务可以覆盖它：`model` 允许 2 × 120 秒 + 30 秒。 |

   服务方法也可以是应用 Agent 的工具。`tools.json` 中 `implemented_by: "host-service"` 的工具会以来自该应用的普通 `ServiceCall` 到达服务，且 `may_prompt` 为 false。这样，应用的界面和它的 Agent 可以共用同一个方法（[AI-SERVICES § 应用的工具](AI-SERVICES.zh-CN.md#应用的工具与-peer-工具)）。
3. **在 Shell 中注册。** 在 `crates/shell/src/apps.rs` 的 `register_host_services` 中调用 `octosense_appstore::services::register_host_service(Box::new(Weather))`。之后，Card runner 会驱动这个服务（`services::pump`）。Mail 的 crate 把这个调用封装在 `octosense_mail_service::register()` 中，再由 `apps.rs` 调用它。
4. **在服务 crate 中测试。** Mail 的测试在 OctoSense 检出目录中执行（未运行）：

   ```sh
   cargo test -p octosense-mail-service
   ```

之后，应用声明这项能力，即可调用 `host.request("weather.today", …)`。
