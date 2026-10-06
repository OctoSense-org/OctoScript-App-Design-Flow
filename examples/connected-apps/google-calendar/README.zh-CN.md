# Google Calendar 应用中心示例

[English](README.md) | 简体中文

这是一个普通 App Hub 应用（`org.octosense.samples.googlecalendar`），使用
OctoSense 共享 OAuth 与 Google Calendar 服务，不依赖内置邮件或日历界面。
目前是开发示例，尚未完成真实提供商的端到端验收。

应用提供账号与日历选择、同步日程、事件详情、定时／全天事件编辑、草稿保留和
保存前的宿主审核。可选聊天用于讨论当前事件，**不会**修改事件，也不会声称
已保存建议。Glance 操作发布对应事件卡片，卡内包含**打开日历**及独立会话。
后续成功同步时会更新已变化的卡片，并撤下已删除事件的卡片。

宿主缓存仅在全部分页成功后提交新数据及 Google 同步令牌；分页失败时保留上次
完整结果，HTTP 410 后重新完整同步。编辑使用 ETag 防止覆盖其他修改，缓存按
应用、连接和日历隔离。表单输入日期、24 小时时间及 IANA 时区；宿主会拒绝夏令时
切换导致不存在或重复的本地时间。全天事件的结束日期包含当天。重复事件会标为
系列并显示原始起点；本版不展开或编辑系列／单次重复事件。

## 运行已验证的本地界面

以下命令已在 macOS 的 App Design Flow 根目录运行：

```sh
tools/octo doctor
python3 examples/connected-apps/google-calendar/scripts/verify-native.py
python3 examples/connected-apps/google-calendar/scripts/verify-glance.py
tools/octo check examples/connected-apps/google-calendar/bundle
```

原生验证器在 8164 端口启动并关闭自己拥有的隐藏 `card-host`；可用 `--port`
选择其他空闲端口。它输入虚构事件，滚动到多行备注，检查实际草稿文件，验证未连接
账号时的审核提示，并重启检查内容保留。临时文件与记录位于 `.local-state/`，
不使用真实 Google 账号。独立 `card-host` 会如实提示缺少 OAuth 宿主服务。

[验收记录](ACCEPTANCE.md)说明精确范围和修复前失败。独立 Glance 验证器在 8165
端口使用明确的虚构数据渲染原封不动的内嵌 L0 模板，不模拟宿主路由或聊天回答。
应用包内四张截图均为这些本地状态的原生截图，不是 Google API 结果。

## 运行签名安装后的集成验收

先构建相邻 OctoSense 仓库的测试宿主，再从本 Flow 仓库执行：

```sh
# 在 ../OctoSense：
cargo build --locked --release -p octosense-shell \
  --features mobile-apps,acceptance-fixtures \
  --example connected-app-host --example connected-inbox-e2e --example connected-install
# 在本仓库：
python3 examples/connected-apps/google-calendar/scripts/verify-installed.py \
  --host ../OctoSense/target/release/examples/connected-app-host
python3 examples/connected-apps/google-calendar/scripts/verify-shell.py \
  --shell ../OctoSense/target/release/examples/connected-inbox-e2e \
  --installer ../OctoSense/target/release/examples/connected-install
```

最终宿主取消审核及模态输入修复后（App Hub `5c7a13f9`），安装验收再次通过八项：经临时签名目录安装、实际事件列表、精确审核与取消、创建与
重新打开、ETag 编辑和冲突、草稿保留及离线重启缓存。冲突时保留错误与返回操作，
已经使用的批准按钮不会继续显示。应用、安装验证及宿主服务是真实代码，只有
日历提供商传输与令牌保险库采用明确的虚构测试实现；这些结果不代表已登录
Google、发送邀请或验证物理点击。独立完整 Shell 验证器通过六项检查，使用实际 Glance 面板
与已安装应用启动器，验证热／冷启动准确返回事件、相同事件的聊天输入，以及
首次代理授权前恢复原卡片、保留原过期时间。可选参数 `--model-profile /private/path/profile.json` 与
`--kernel /path/to/octos` 可加入真实模型检查。本次使用真实 DeepSeek v4 Flash
通过验收：Calendar 代理调用已声明的 `googlecalendar.event` 只读工具，准确回答
虚构事件信息，提供商写入次数为零。正确的授权说明及实际回答截图见
[验收记录](ACCEPTANCE.md)。

两者均清理自己启动的隐藏进程与临时配置，并把绑定源文件
及执行文件哈希的记录保存在 `.local-state/`。

## 连接真实 Google Calendar

此流程已接入源代码，但**尚未对本示例进行真实账号验证**。需要包含共享 OAuth
服务及 App Hub `auth`／`gcalendar` 能力的 OctoSense 构建。Google OAuth 客户端
由宿主管理员在应用包外配置，使用者在宿主／提供商界面完成授权。Android 需要
原生 Google 授权适配器，不能复用桌面的回环登录流程。

1. 通过 App Hub 安装已签名、审核的应用包。上述测试目录仅用于私有验收，不代表
   已公开发布；正式发布仍需要真实发布者身份、隐私资料、签名及目录接纳。
2. 点击 **Account → Connect Google**，完成授权，选择账号与日历；**Refresh**
   调用真实 Google API。
3. 选择事件后点击 **Edit**，或用 **+ Event** 新建。**Keep draft** 保留未提交修改，
   **Review & Save** 打开宿主的精确内容审核。
4. 检查账号、日历、标题、时间与备注后再批准。提供商确认后重新同步；失败会保留
   草稿。遇到版本冲突应对照最新事件处理，不能强制覆盖。
5. 事件详情中的 **Glance** 会发布 24 小时卡片，不发送通知。卡内 **Open Calendar**
   通过绑定应用的路由回到相同账号、日历与事件。完整 Shell 验证器单独验证
   Glance 与路由；真实 Google 与模型会话仍需要各自的验收证据。

## 服务与隐私边界

| 能力 | 调用及用途 |
| --- | --- |
| `auth` | `accounts`、`active`、`select`、`connect`、`disconnect`：仅获取绑定本应用的不透明连接句柄 |
| `gcalendar` | `calendars`、`cached`、`refresh`、`prepare`、`review_save`：读取事件、同步和审核后写入 |
| `storage` | 所选连接／日历、未发送草稿和已发布事件的路由绑定 |
| `glance` | `publish`、`withdraw`、`take_open`：发布卡片及返回对应应用 |
| `octos.session.open`、`octos.turn.start` | 按用户请求讨论选定事件 |

Google 权限别名 `calendar.list`、`calendar.events` 由宿主转换。
`storage.accounts: true` 使应用代理绑定当前所选 OAuth 账号。本应用不申请网络
能力，也不保存提供商凭据。代理不读取工作区文件（`agent_workspace: "none"`）；
仅在请求会话时提供对应事件上下文，由宿主模型配置和授权决定如何处理。四个已声明
只读工具 `googlecalendar.calendars`、`.cached`、`.refresh`、`.event` 显式映射到
已授权的 `gcalendar` 服务，均标为私有且不可共享。本版聊天
只提供建议，没有虚构跨应用写入日程工具。

尚待验收：真实 Google 登录／读取／创建／编辑／冲突／撤销授权、物理批准、
展开卡片工作区、Glance 卡片聊天及与应用会话共享历史、Android 键盘与生命周期、Linux 和 Windows。不可将当前
源码与本地检查描述成这些项目已通过。`listing.json` 暂保留发布者占位信息，等待
发布者提供真实内容。当前应用界面以英文为主。
