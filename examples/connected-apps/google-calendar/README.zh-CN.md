# Google Calendar 示例

[English](README.md) | 简体中文

这是一个普通 App Hub 应用（`org.octosense.samples.googlecalendar`），使用 OctoSense 的共享 OAuth 与 Google Calendar 服务，不依赖内置的邮件或日历界面。

0.1.1 版已从 [ymote/octosense-google-calendar](https://github.com/ymote/octosense-google-calendar) 发布到 App Hub。本目录是与 `v0.1.1` 同步的未签名开发副本，已包含日期范围状态。清单版本为 `0.1.1`，仅有开发摘要、没有签名；商店发布者字段仍是占位内容。[参考应用指南](../README.zh-CN.md)说明了保留的差异和复用步骤。现有验收证据仍对应记录时的源码。

应用提供账户与日历选择、同步日程、日程详情、定时和全天日程编辑、草稿保留，以及保存前的宿主确认。应用界面为英文。可选的聊天用于讨论当前日程，**不会**修改日程，也不会声称已保存建议的修改。**Glance** 操作把日程发布为速览卡片，卡内有 **Open Calendar** 操作和独立会话。之后同步成功时，应用会更新已变化的卡片，并撤下日程已不在同步结果中的卡片。

在所有版本上，宿主缓存都会：

- 分页失败时保留上一次完整的结果；
- 编辑时使用 ETag；
- 按应用、连接和日历分别存放数据。

同步覆盖的范围因版本而异：

- **desktop-v0.1.0-beta.2：** 整个日历。宿主只在最后一页之后才推进 Google 同步令牌，遇到 HTTP 410 时重新完整同步。
- **OctoSense `main`（尚未进入任何发布版本）：** 一个固定窗口，按 UTC 日界，从今天之前 30 天到之后 366 天。每次刷新都重新获取整个窗口，宿主不保存同步令牌。

编辑器使用日期、24 小时制时间和 IANA 时区；宿主会拒绝夏令时切换时不存在或重复的本地时间。全天日程的结束日期指最后包含的那一天。应用不能编辑重复日程。在 desktop-v0.1.0-beta.2 上，重复系列只出现一次，并标明原始起点。OctoSense `main` 会把窗口内的每个系列展开为单次日程，应用仍把每一次都标为重复系列。日程从最早的开始列出，所以在 beta.2 上打开时显示的是日历历史的开头。不要照搬这种同步策略，见[同步整个日历](../README.zh-CN.md#同步整个日历)。

## 在本地检查界面

在 App Flow 根目录运行（已在 macOS 上验证）：

```sh
tools/octo doctor
python3 examples/connected-apps/google-calendar/scripts/verify-native.py
python3 examples/connected-apps/google-calendar/scripts/verify-glance.py
tools/octo check examples/connected-apps/google-calendar/bundle
```

每个验证器都会输出 JSON 回执：`verify-native.py` 报告 `"passed": 5`，`verify-glance.py` 报告 `"result": "template and render pass"`。`tools/octo check` 最后输出 `— PASSED`，附带 `unsigned` 警告和一条关于商店信息占位内容的提示。

原生验证器在 8164 端口启动隐藏的 `card-host`，结束后自行关闭；可用 `--port` 选择其他空闲端口。它输入虚构的日程信息，滚动到多行备注，检查已保存的草稿，验证未连接账户时的确认提示，并重启以检查内容保留。临时文件和回执位于 `.local-state/`，不使用真实 Google 账户。独立的 `card-host` 会如实提示缺少 OAuth 服务。

[ACCEPTANCE.md](ACCEPTANCE.md) 记录了确切范围和最初的失败。独立的 Glance 验证器在 8165 端口用虚构数据渲染内嵌的 L0 卡片源码，不模拟 Shell 路由或聊天回复。应用包内的四张截图都是这些本地状态的原生截图，不是 Google API 的结果。

## 运行签名安装后的集成验收

先构建相邻 OctoSense 仓库中的测试宿主，再从 App Flow 根目录运行验证器：

```sh
# 在 ../OctoSense 中：
cargo build --locked --release -p octosense-shell \
  --features mobile-apps,acceptance-fixtures \
  --example connected-app-host --example connected-inbox-e2e --example connected-install
# 在 App Flow 根目录：
python3 examples/connected-apps/google-calendar/scripts/verify-installed.py \
  --host ../OctoSense/target/release/examples/connected-app-host
python3 examples/connected-apps/google-calendar/scripts/verify-shell.py \
  --shell ../OctoSense/target/release/examples/connected-inbox-e2e \
  --installer ../OctoSense/target/release/examples/connected-install
```

0.1.0 发布前，这些验证全部通过：应用经临时签名目录安装，并使用真实的应用与宿主服务；只有日历传输和凭据库是模拟实现。

| 验证器 | 结果 |
| --- | --- |
| `verify-installed.py` | 在宿主最终的取消和模态输入修改（App Hub `5c7a13f9`）之后重跑，通过 8 项：日程列表、确切内容的确认与取消、创建与重新打开、ETag 编辑与冲突、草稿保留、离线缓存重启 |
| `verify-shell.py` | 使用实际的速览栏和已安装的应用启动器，通过 6 项：热启动和冷启动都准确回到对应日程、同一日程的聊天输入、未经应用 Agent 授权也能恢复卡片且不刷新过期时间 |
| `verify-shell.py --model-profile <model-profile.json> --kernel <octos-binary>` | 真实 DeepSeek v4 Flash：Calendar 的应用 Agent 调用已声明的 `googlecalendar.event` 只读工具，回答了所选虚构日程的信息，没有任何提供商写入 |

冲突时显示错误和 **Back**；已用过的批准不能再次使用。这些检查不会登录 Google、不会发送邀请，也不能证明亲手点按批准。修正后的授权面板和实际回答见 [ACCEPTANCE.md](ACCEPTANCE.md)。两个验证器都会清理自己启动的隐藏进程和临时配置，并把绑定源码与可执行文件哈希的回执保存在 `.local-state/` 下。

如需持续运行原生界面测试，执行：

```sh
python3 examples/connected-apps/google-calendar/scripts/soak.py \
  --host ../OctoSense/target/release/examples/connected-app-host
```

这次 macOS 运行在 620 秒内通过 36 轮：编辑、滚动、确认与取消，其中包括三次保存后读回核对、三次版本冲突和四次冷重启。每个进程的常驻内存（RSS）都有增长，因此这只说明功能测试通过，不能声称没有内存泄漏。[验收记录](ACCEPTANCE.md#sustained-macos-ux-soak)包含原始截图、计时方法的限制和内存变化。

## 连接真实 Google Calendar

此流程已在源码中实现，但**真实账户验证只有一次手动测试**。OctoSense 记录了这次在 macOS 上用开发构建进行的测试：已安装的 0.1.0 连接了一个专用的 Google 测试账户，列出了它的日历，并保存了一个日程，**Refresh** 后日程仍在；没有通过 API 独立读回核对（[回执](https://github.com/OctoSense-org/OctoSense/blob/main/tools/connected-e2e/evidence/calendar-login-20261007.json)）。需要 OctoSense desktop-v0.1.0-beta.2 或更新版本，它包含共享 OAuth 服务，并准入 `auth` 和 `gcalendar` 能力。beta.2 没有内置的提供商注册信息，所以宿主管理员需要按[宿主配置指南](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/crates/oauth-service/README.zh-CN.md)在应用包外配置 Google OAuth 客户端；宿主构建时已编入分发者注册信息的，不需要这一步。你在宿主界面上完成提供商授权。**尚未支持：** Android 上的 Google 登录，它需要原生的授权适配器。

1. 从 App Hub 安装 Google Calendar。已发布的 0.1.1 由 `ymote` 签名。
2. 选择 **Account → Connect Google**，完成宿主和提供商授权，再选择账户与日历。**Refresh** 会调用真实的 Google API。
3. 选择一个日程后选择 **Edit**，或选择 **+ Event** 新建。**Keep draft** 保留未提交的修改，**Review & Save** 打开宿主确认面板，显示确切内容。
4. 核对账户、日历、标题、时间和备注后再批准。收到提供商回执后会重新同步；出错时保留草稿。版本冲突不会覆盖日程，请在最新版本上修改。
5. 要发布卡片，请在日程详情中选择 **Glance**。卡片保留 24 小时，不发送通知。卡片中的 **Open Calendar** 通过宿主绑定应用的路由，回到同一账户、日历和日程。

## 服务与隐私边界

能力、存储、工具和 Agent 的说明，见参考应用指南中的 [Google Calendar](../README.zh-CN.md#google-calendar)。

**未验证：** 除那次测试之外的真实 Google 登录、读取、创建、编辑、冲突和撤销授权；展开后的卡片工作区；速览卡片的聊天历史；亲手点按批准保存；Android；Linux；Windows。在 desktop-v0.1.0-beta.2 上，宿主的 Calendar 确认面板不检查是否为亲手点按；OctoSense `main` 则要求在原生审阅界面上亲手点按（尚未进入任何发布版本）。
