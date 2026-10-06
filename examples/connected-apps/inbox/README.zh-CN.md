# 收件箱助手示例

[English](README.md) | 简体中文

这是普通 App Hub 应用 `org.octosense.samples.inbox`。它通过共享主机服务连接
Gmail，并让邮件、回复编辑、聊天和原生审核使用同一份已保存的回复。它不依赖
内置 `os.mail` 应用，也不借用系统应用身份。

首次启动显示明确标注的虚构收件箱，可离线编辑，不能发送真实邮件。配置好
OctoSense 主机后，**Connect Google** 打开共享 OAuth 授权界面。应用只获得
绑定自身的连接句柄，不获得密码、授权码、访问令牌或刷新令牌。

## 已实现的功能

- 通过 `gmail.messages`、`gmail.message` 读取收件箱、重要邮件和已发送文件夹；
  应用不直接访问网络，也不接触提供商凭据。
- 向一位收件人回复纯文本。主机保存发件人、原始邮件与会话头、递增版本号、
  审核请求和发送回执。
- 在 Reply 与 Chat 之间切换前先保存编辑。聊天通过 `octos.session.open` 和
  `octos.turn.start` 调用此账户的真实应用代理。代理工具读写同一份草稿，界面再
  读取实际保存结果；版本检查和本地输入保护防止迟到结果覆盖新内容。
- `inbox.new_message` 将新的 Gmail 邮件 ID 交给已获同意的应用代理及其筛选技能。
  首次连接只建立后续增量基线，不给整个旧邮箱发通知。处理完成必须留下持久化
  的静默决定或主机确认的已发布卡片；失败后按同一 ID 重试。事件本身不能批准发送。
- **AI sort** 判断当前邮件是否对用户重要。默认关注医疗、配送、日程、学习／
  工作任务和家庭活动，普通促销与通讯保持安静。重要结果可发布 Glance 工作区
  和通知；**Pin** 仅手动固定卡片，不弹通知。
- Glance 使用已接纳的 `glance-workspace.splash` 模板，与应用共用控制逻辑，
  保持原连接及邮件身份，通过主机读取完整内容。模型负责相关性与摘要，主机负责
  已接纳的交互界面及账户绑定。
- **Review & Send** 打开主机绘制的完整、不可变邮件审核界面。只有原生控件上的
  真实物理操作才允许发送。脚本、模型、`from_sheet`、自动化点击或开发者模式
  都不能代替批准。
- Gmail 接受提交后移除对应 Glance 卡片；接受提交不等于收件人已收到邮件。
  结果不确定时禁止自动重发。

## 主机要求与当前限制

示例使用 OctoSense `crates/oauth-service` 中的新 OAuth／Gmail 服务。
调用包括 `auth.connect`、`auth.active`、`auth.select`、`auth.disconnect`、
`gmail.messages`、`gmail.message`、
`gmail.draft.open`、`gmail.draft.get`、`gmail.draft.edit`、`gmail.draft.review`、
`gmail.event.status`、`gmail.event.decide`，以及只读的
`gmail.events.status` 就绪检查。`inbox.*` 工具映射到这些主机方法，
没有工具可以批准发送。
OAuth 请求中的 `mail.read`、`mail.send` 是主机定义的 Google 权限别名。

主机管理员需要配置已注册的 OAuth 客户端，用户在主机／浏览器完成 Google
授权。Gmail API、Google 同意界面及测试用户限制需要在 Google 配置。普通
`card-host` 不注册提供商或模型服务，会如实显示服务不可用。手机运行真实流程
还需要实际安装版本支持 Android Google 授权适配器和物理发送审核。

允许后台执行时，主机大约每五分钟检查当前已授权、已同意代理处理的账户。
代理失败或没有持久化处理决定会在之后重试；Android 可能延迟静默任务。本次
实现了主机收集器、应用代理与工具路由，但本示例尚未完成真实 Gmail → 模型 →
Glance 的端到端验证。连接账户并允许应用代理后，点击 **Refresh**，直到界面显示
**New-mail baseline ready**，再发送新的测试邮件。旧邮件仍可阅读，但不会补发
通知。此状态只说明增量基线已建立，不等于代理同意目前仍然开启；还需检查
主机的应用代理设置。

**尚未完成：** 跨应用日历预约、聊天偏好汇总到系统记忆、超过首批 30 封邮件的
翻页界面、附件、回复全部、HTML 回复、重试／结果核对界面，以及
Android／Windows／Linux 验收。**AI sort** 是前台模型辅助，与新邮件事件代理
流程不同。本示例中的模型不能批准发送。

## 开发与验证

在 App Design Flow 仓库运行，以下命令已执行：

```sh
tools/octo doctor
python3 examples/connected-apps/inbox/build_bundle.py
tools/octo run examples/connected-apps/inbox/bundle --port 8194 --hidden --detach
python3 examples/connected-apps/inbox/verify_native.py --port 8194
```

验证器通过真实 Makepad HTTP instrument 操作虚构数据，检查启动、第二封邮件
身份、多行 Unicode 编辑、Reply／Chat 共享状态、服务不可用、虚构数据禁止发送
及文件夹筛选／空状态，并保存真实 PNG 和源码摘要。关闭并重新运行后，可使用
`--restart-check` 检查保存文本是否完全恢复。自己的测试进程通过 `/gq` 或 `/quit`
退出。

OctoSense `inbox.rs`、`inbox_events.rs` 的测试覆盖注入输入、版本冲突、过期／取消／跨应用审核、
提交前持久化、重复提交、不确定结果、MIME 头校验，以及模拟 Gmail 请求中的
会话、正文和单次提交。事件测试还覆盖分页、历史游标过期、持久化决定、重放、
重试、账户隔离及完整队列恢复。模拟传输成功不代表真实 Gmail 送达。

当前测试与视觉问题见[证据记录](evidence/README.md)。没有使用真实 Google
账户、DeepSeek／MiniMax 推理或真实邮件。应用尚未签名、发布；发布者身份、
支持／隐私信息和发布批准仍是人工检查点。

## 隐私

只有主机授权后应用才可读取邮件。启用后台应用代理后，新邮件可由该账户的代理
及用户配置的模型读取并筛选。前台 Chat 和 AI sort 同样使用模型。代理同意与
Google 登录是两道独立设置；关闭应用代理会停止模型筛选。手动阅读、编辑不
需要模型。凭据保存在应用存储之外。

应用私有目录保存虚构草稿和选中的不透明连接句柄。真实回复及回执由主机按
应用和连接隔离保存。退出授权后不能继续使用该连接，但不会删除历史草稿和
回执。Glance 保存精简邮件绑定和工作区程序，完整邮件通过授权服务加载。
不要提交真实应用数据、OAuth 配置、私人邮件截图或令牌；所有示例及公开截图
必须保持虚构数据。
