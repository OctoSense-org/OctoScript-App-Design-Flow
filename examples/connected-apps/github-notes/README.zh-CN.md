# GitHub Notes 示例

[English](README.md)

普通 App Hub 应用 `org.octosense.samples.githubnotes` 提供本地 Markdown 草稿
和经宿主审核的 GitHub 提交。它只申请 `storage`、`auth`、`github`，不接收
访问令牌，也不直接联网。连接 GitHub 不需要另建 OctoSense 云账号。

编辑器采用 Rinx 文章编辑器布局：顶部图标操作、桌面端原文/分栏/预览，
手机端底部格式工具栏。样式面板保留富文本块编辑入口。继续复用 Rinx v1.1.0
通用文章组件，支持原始 Markdown、原生富文本选择、撤销/重做、代码/表格/公式
渲染与本地恢复。
不包含 Rinx 的 Matrix 发布流程和图片文件选择/上传；图片 URL 保留为
Markdown，不会自动下载图片。

[Rinx 编辑器验收](VALIDATION.md#rinx-writer-layout)提供原生参考对比、更新后的安装
流程与 OnePlus 6 截图。此前的截图和浸泡测试记录对应旧版编辑器布局。

在包含共享 OAuth 和编辑器组件的 OctoSense 中构建 `app-hub`，为宿主配置
启用设备授权流程的 GitHub OAuth 客户端，然后通过测试目录或本地安装此
bundle。不要把客户端密钥或访问令牌放进应用包或应用数据。

先编辑本地笔记，再通过左上角返回/文件图标打开 **Repository & file**。选择公开仓库或更广泛的私有仓库
权限，在宿主审核界面和外部浏览器完成 GitHub 授权。选账号、仓库、分支、文件；
新笔记可以填写新 Markdown 路径并选择 **Use as new path**。设置提交说明，
返回笔记并点纸飞机图标，在宿主页面核对确切内容和目标。只有收到 commit SHA
才会显示提交成功；旧文件 SHA 不匹配时不会自动覆盖。

草稿在应用私有目录交替保存并读回校验，切换文件时可保留恢复副本。失败或取消
不会删除草稿；超时结果不明时应先查看 GitHub，再决定是否重试。断开授权仍保留
本地笔记。
应用声明 `storage.accounts: true`，启动通过 `auth.active` 读取宿主当前账号，
选择账号调用 `auth.select`。浏览使用当前账号，已打开的草稿保留原账号和仓库
绑定；切换账号不会悄悄更改提交目标。保存前需要选回原账号或明确选择新目标。

应用声明三个只读工具：`githubnotes.repositories`、`githubnotes.files` 和
`githubnotes.read`。宿主根据本应用的连接和 `github` 权限调用对应 API。工具
标记为私有数据、仅前台、不可共享；不导出写入、审批或凭据工具。保存仍需审核
确切内容。代理调用及跨应用访问继续受宿主授权约束，独立编辑器测试未验证此路径。

目前独立 `card-host` 可以准入这些能力，但没有注册 `MarkdownEditor`，因此
不能单独运行此示例。OctoSense 的 `editor-host` 可以在没有真实账号的情况下
对真实组件和源码进行原生 UI 测试。集成 `connected-app-host` 还验证普通应用
准入、真实宿主授权页、缺少 OAuth 配置时的错误、取消及本地草稿完整保留。
记录见 [VALIDATION.md](VALIDATION.md)。
安装后的原生流程也已通过：使用真实 Store、`prepare_launch`、编辑器、宿主 API
和审核页，仅通过非默认编译功能替换 GitHub 传输和内存凭据库。覆盖仓库分页、空仓库、
第二个文件、脏草稿保护、确切内容审核/取消、已有及新文件提交、SHA 冲突、响应丢失时
不自动重试、离线重启恢复。原始原生截图和绑定源码的记录见
[VALIDATION.md](VALIDATION.md#signed-installed-provider-acceptance)，失败的本地记录单独保留。
在 OctoSense 工作目录执行：

```sh
cargo build --locked --release -p octosense-shell \
  --features mobile-apps,acceptance-fixtures \
  --example connected-app-host --example connected-install
python3 tools/connected-e2e/notes.py \
  --bundle ../OctoScript-App-Design-Flow/examples/connected-apps/github-notes/bundle
```

[最终宿主回归](VALIDATION.md#final-modal-and-cancellation-regression)已在模态输入与取消生命周期修复后
重新通过完整安装和授权界面流程；新增回执保留确切源码、二进制摘要及逐张检查的原始截图。

普通构建不启用该测试功能；测试拒绝未标记的用户目录或真实 OAuth 客户端配置。
测试目录只存放虚构数据，示例应用本身只使用正常宿主 API，没有测试切换开关。

[Mac 浸泡记录](https://github.com/OctoSense-org/OctoSense/blob/feat/app-hub-connected-samples/tools/connected-e2e/evidence/notes-soak-20261006/README.zh-CN.md)
包含 156 轮，其中一次持续十分钟，验证精确草稿恢复及审核取消。内存有所增长，
长期稳定性仍待分析。独立的 OnePlus 6 **OctoSenseNotesTest** APK 在修复 Android
组合末词丢失后，通过本地编辑、软键盘／硬件 Enter 和精确冷启动恢复。
[手机配置及边界](https://github.com/OctoSense-org/OctoSense/blob/feat/app-hub-connected-samples/tools/connected-e2e/android-notes.zh-CN.md)
使用签名私有目录，不复制提供商凭据；手机尚未配置 GitHub 连接，不能据此声称真实仓库验收通过。

真实 GitHub OAuth/读取/提交/冲突、人工物理审批、Android 后台生命周期、Windows/Linux
界面仍未验证。真实验收需要在宿主 `<apps root>/.host/oauth/clients.json` 配置启用
设备流程的 GitHub OAuth 客户端 ID，由用户完成 GitHub 授权，并明确指定可删除的
测试仓库、分支和文件路径；不复用 GitHub CLI 凭据。该小型宿主不验证代理工具调用或
Glance。发布者身份和隐私政策仍保留显式占位符，等待人工审核；这不是已发布应用，
也不声称已实现 Rinx 的全部功能。

Rinx 文章解析上限为 512 KiB。无法加载的已保存草稿会停留在仓库/恢复界面，
不会出现可覆盖原文的空编辑器。明确选择有效文件替换时，会保留原文的完整恢复副本。

清单显式声明可选的 **Ask GitHub Notes** 前台只读代理及 [AGENT.md](bundle/AGENT.md)。
安装或连接 GitHub 不等于代理授权。启用后，问题、对话上下文及允许读取的仓库／文件
结果可能发送给宿主配置的模型。三个现有工具仍为私有、不可共享、仅前台读取，
没有代理写入或审批工具。远端读取不等于读取编辑器未保存草稿；手动编辑无需模型。
声明修正与 gate 检查不是新的真实模型执行证据。
