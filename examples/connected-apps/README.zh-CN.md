# 可独立安装的 App Hub 示例

[English](README.md) | 简体中文

三个普通 App Hub 应用展示共享提供商登录及主机服务。它们使用独立的应用身份
和私有存储，不依赖内置 Mail 或 Calendar 界面。**不新增 OctoSense 云账户。**
用户授权 GitHub 或 Google，主机向应用提供绑定账户的不透明句柄，并把提供商
凭据保存在应用包之外。

这些是开发示例。下方记录了本地界面和连接器测试；它们尚未发布，也不代表
真实提供商流程已经通过验收。

| 示例 | 准确应用 ID | 已实现路径及证据 |
| --- | --- | --- |
| [GitHub Notes](github-notes/README.zh-CN.md) | `org.octosense.samples.githubnotes` | Rinx Markdown 编辑器、仓库／文件选择及审核后提交。[原生编辑器证据](github-notes/VALIDATION.md)。 |
| [Inbox Assistant](inbox/README.zh-CN.md) | `org.octosense.samples.inbox` | Gmail 读取、与应用代理共享的一份回复草稿、原生发送审核、重要邮件事件决定及交互式 Glance 模板。[测试回执和限制](inbox/evidence/README.md)。 |
| [Google Calendar](google-calendar/README.zh-CN.md) | `org.octosense.samples.googlecalendar` | 日历选择、分页同步、日程编辑与审核保存、Glance 发布及返回原日程。[原生界面和连接器证据](google-calendar/ACCEPTANCE.md)。 |

## 匹配的主机与工具

示例需要配套 OctoSense `feat/app-hub-connected-samples` 实现，并启用 `app-hub`
功能、共享 `auth`／提供商服务、账户隔离和主机审核界面。GitHub Notes 还需要
从 Rinx v1.1.0 提取的原生 `MarkdownEditor`。Inbox 代理需要已接纳的工具映射、
应用代理同意、模型配置及主机新邮件收集器。Glance 模板和路由需要集成主机。

使用 App Hub 策略提交 `5c7a13f92fa25d36ba1fe7fb99dc9fb1b235f8d3`，或 OctoSense
固定的兼容版本。策略变化后必须同时重新构建 **hub 和 card-host**；旧二进制
会拒绝新增的提供商能力或 `host_method` 映射。准入通过只说明主机允许哪些
能力，不会安装这些服务，也不能证明提供商连接成功。

独立 `card-host` 可运行 Inbox 和 Calendar 的本地测试，但没有真实 OAuth、
模型、提供商服务，也没有 Rinx `MarkdownEditor`。GitHub Notes 必须使用
OctoSense 编辑器测试主机或集成主机；独立运行器绘制了空白首帧不等于编辑器
可用。每个示例 README 提供实际运行和验证命令。先按 Design Flow 配置原生
工作区，再执行 `tools/octo doctor`。

## 提供商配置与真实验收

主机管理员在私有 `oauth/clients.json` 中配置已注册的 GitHub／Google OAuth
客户端。客户端注册属于主机，不是 OctoSense 用户账户，不能打包进提交应用。
用户在主机界面审查应用、提供商和权限，再到提供商完成同意。GitHub 客户端
需要启用设备授权；Google 桌面流程使用浏览器、PKCE 和本地回环地址，并需要
为目标用户配置提供商 API、同意界面及测试用户限制。

**在原生适配器完成前，此共享服务目前不支持 Android Google 授权。** 不能把
桌面回环登录当成手机替代方案。Windows 和 Linux 凭据适配器已有源码。Linux
构建主机已通过协议测试及主机编译；原生凭据库测试被未解锁／不可用的 Secret Service
拒绝。Windows 交叉编译因 Mac 缺少 Windows SDK，在到达本 crate 前停止。
这些结果不能证明相应平台的原生界面或真实提供商登录。

集成测试使用干净的开发配置和 App Hub 本地／测试目录安装流程。完整真实
测试仍需提供商登录、实际读写回执、取消／撤销／冲突及准确的已安装应用包。
Inbox 还需要允许应用代理，并等待后续新邮件基线建立后再发送测试邮件。
虚构收件箱不能证明真实 Gmail 或代理已经运行。

确定性的 `connected-install` 检查已通过新的签名私有目录和分别签名的应用包
安装这三个实际示例，重新打开保存的策略，并拒绝篡改或其他应用的暂存目录。
输入源码保持不变，临时数据已删除。原始运行只验证 Store 安装边界；之后的
已安装界面及模型运行另行记录。详见各应用证据和主机本地
`target/connected-install/receipt.json`。
已针对 Hub `eaaffffd695caf7ebf6205c455377c1f8567b906` 重新构建并运行；
[可移植签名安装回执](evidence/signed-install-eaaffffd.json) 记录三个应用包的摘要，
以及准确的源码、锁文件和二进制哈希。

之后的签名安装流程使用真实主机服务和原生审核界面、合成提供商网络：Notes
验证编辑／保存／冲突／离线重启；Calendar 验证创建／修改／ETag／缓存和
Glance 热启动、冷启动跳转。真实 DeepSeek peer 还处理了两封合成 Inbox 邮件，
静默处理通讯简报、发布诊所卡片，并通过 Chat 修改同一份持久化回复。各应用证据
区分这些结果和剩余项目。真实 OAuth、远程写入结果、物理发送批准，以及
OnePlus 6 键盘和后台生命周期仍未验证。配套 OctoSense 的 ADR 0010 记录架构及待验收项目。

## 可复现检查与数据边界

已执行的工作包括 `tools/octo doctor`、原生 Makepad 输入／截图流程、App Hub
准入检查和确定性连接器测试。上方各应用证据记录给出准确源码、二进制、截图
摘要、命令、失败及修改后应重跑的项目。Inbox 另有机器可读的
[交互回执](inbox/evidence/run-receipt.json)和
[重启回执](inbox/evidence/restart-receipt.json)。这些仅是限定范围的本地结果，
不是 UX 数字评分或发布认可。

示例由 Codex 编写并驱动原生测试，没有宣称 DeepSeek／MiniMax 编写。已记录的
DeepSeek 工具回合使用应用准入指令和合成内容；这些新示例尚未进行 MiniMax 验收。
提供的邮件、日历、仓库内容全部虚构。不得提交提供商令牌、客户端密钥、私人
邮箱／日历导出、私人仓库内容、真实账户截图或 `.local-state/`。应用代理同意
与提供商登录分开控制模型处理。模型不能批准受保护的写入；应用必须在主机
审核界面展示实际已保存的内容。

应用包尚未签名和发布。发布前应由实际发布者替换发布者／支持／隐私占位信息，
并通过正常 Design Flow／App Hub 检查。本目录不是生产应用目录，也没有宣称
所有平台都已能安装并正常运行这三个应用。

[最终三个应用的安装复验](evidence/signed-install-5c7a13f9.json)使用 Hub
`5c7a13f92fa25d36ba1fe7fb99dc9fb1b235f8d3` 和当前应用包摘要，再次通过签名安装、
重新打开以及目录、源码、跨应用暂存篡改拒绝检查。历史回执保持不变；该证明不代表真实
OAuth 或供应商投递已经验证。
