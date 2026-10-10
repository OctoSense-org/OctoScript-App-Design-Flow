# GitHub Notes 示例

[English](README.md) | 简体中文

普通 App Hub 应用包 `org.octosense.samples.githubnotes` 提供本地 Markdown 草稿和经宿主确认的 GitHub 提交。它只申请 `storage`、`auth` 和 `github`，从不接收提供商令牌，也不直接联网。连接 GitHub 不会创建 OctoSense 云账户。

0.1.1 版已从 [ymote/octosense-github-notes](https://github.com/ymote/octosense-github-notes) 发布到 App Hub，它声明了 0.1.0 中缺少的可选 Agent。本目录是 0.1.1 的未签名开发副本，Agent 和 [AGENT.md](bundle/AGENT.md) 都与发布版相同。它的 `listing.json` 中发布者字段是占位内容，`manifest.json` 没有签名；其余文件都与发布版一致。[参考应用指南](../README.zh-CN.md)说明了应用的构成，以及复用前需要修改什么。

编辑器采用 Rinx 的布局。Rinx 是 OctoSense 自带的文章编辑器：顶部是纯图标的标题栏和格式按钮，桌面端提供原文/分栏/预览，手机端在底部显示格式工具栏。样式面板还能打开富文本块编辑。编辑器基于 Rinx v1.1.0 组件，保留精确的 Markdown、富文本选择、撤销/重做、代码、表格和公式渲染，以及本地恢复。它不包含 Rinx 的 Matrix 发布功能，也不包含图片选择和上传。远程图片 URL 保留为 Markdown，本示例不下载图片。

[Rinx 编辑器验收](VALIDATION.md#rinx-writer-layout)提供原始参考对比、更新后的安装流程和 OnePlus 6 截图。此前的截图和持续测试记录对应旧版编辑器布局。

## 运行

1. 使用 OctoSense desktop-v0.1.0-beta.2 或更新版本，其中包含连接账户服务和 `MarkdownEditor` 控件。
2. 为宿主提供 GitHub 注册信息。beta.2 的下载包里没有：请按[宿主配置指南](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/crates/oauth-service/README.zh-CN.md)，在宿主的 `<apps root>/.host/oauth/clients.json` 中添加启用设备授权流程的 GitHub OAuth 客户端 ID。缺少它时，连接会失败并提示 `OAuth is not configured`。如果宿主构建时已编入分发者的注册信息，就不需要这个文件。不要把客户端密钥或令牌放进应用包或应用数据。
3. 从 App Hub 安装已发布的 GitHub Notes，或通过本地测试目录安装本副本（[PUBLISHING 第 4 节](../../../docs/PUBLISHING.zh-CN.md#4-在本地演练商店流程)）。授予界面列出的能力。
4. 先写笔记，再点击左上角的返回/文件图标打开 **Repository & file**。选择应用可访问的范围（**Public repositories**，或会授予 GitHub 范围更广的 `repo` 权限的 **Public and private repositories**），然后点 **Connect GitHub**，在宿主面板和浏览器中完成授权。
5. 账户卡片随后显示已连接的账户及其访问范围，并加载仓库。选择仓库、分支和文件。新笔记可以填写新的 Markdown 路径，再选择 **Use as new path**。已有文件会连同 blob SHA 一起加载；如果远端文件已经改变，GitHub 会拒绝提交，应用保留你的草稿。
6. 设置提交说明，回到笔记，点击纸飞机图标。在宿主面板中核对确切内容和目标位置，然后选择 **Approve & Save**。只有 GitHub 返回提交 SHA 后，应用才报告提交成功。

## 草稿与账户

未发送的编辑以交替保存、读回校验的快照形式存放在应用的私有存储中。主动打开另一个文件时，当前草稿会保留为恢复副本。远程保存失败或取消时，本地草稿保留不变。网络超时会让远端结果不明；重试前请先到 GitHub 查看。**Disconnect** 经确认后会移除本应用的 OAuth 连接，但保留本地笔记。**Use another account** 可切换或添加账户。

清单声明了 `storage.accounts: true`。启动时读取 `auth.active`，选择账户时调用 `auth.select`，让宿主和应用对当前账户保持一致。浏览使用当前选中的账户。已打开的草稿保留原来的账户和仓库；切换账户不会悄悄改变它下一次提交的目标。要提交这样的草稿，请选回原账户，或选择新的目标。

Rinx 解析的文章上限为 512 KiB。无法加载的已保存草稿会留在恢复/仓库界面中受到保护，在空白编辑器里输入也无法覆盖它。主动用有效文件替换它时，会保留原文的完整恢复副本。

## 应用 Agent 与只读工具

本副本的清单声明了一个可选的应用 Agent，在前台为用户读取笔记：

```json
"agent": {
  "background": false,
  "instructions": "AGENT.md",
  "model": {
    "local_only": false,
    "needs": [
      "tool_calling"
    ]
  },
  "profile": "read-only",
  "tools": []
}
```

用户通过 **Ask GitHub Notes** 使用它。安装应用或连接 GitHub 都不等于允许这个 Agent，宿主会另行询问。用户允许之后，提问、对话内容以及允许读取的结果都可能发送给宿主配置的模型。[AGENT.md](bundle/AGENT.md) 把 Agent 限定为只读：它没有编辑、提交、删除或批准工具，把仓库内容当作不可信的数据，提出的修改也只是对话中的建议。它读到的是远端已保存的文件，不是编辑器中未保存的草稿。编写和保存笔记都不需要模型。

应用包声明了 `githubnotes.repositories`、`githubnotes.files` 和 `githubnotes.read`。宿主用本应用自己的连接和 `github` 权限，把它们映射到对应的 GitHub 读取 API。每个工具都设为 `private_data: true`、`background: false` 和 `shareable: false`。应用包没有导出任何写入、批准或凭据工具；保存仍要在宿主确认面板上核对确切内容。准入检查接受这个 Agent（`hub check` 的授权为 `agent read-only`），但还没有真实模型运行过它，独立编辑器测试也不检查应用 Agent 的工具调用。

0.1.0 版附带同样的工具，却没有 `agent` 块，OctoSense 仍然为它提供了 **Ask GitHub Notes**。不要照搬这种做法，见[没有 agent 块的工具](../README.zh-CN.md#没有-agent-块的工具)。

## 当前验证范围

独立的 App Hub `card-host` 会准入所声明的能力，但没有 `MarkdownEditor`，因此无法单独运行本示例。不要把它显示的“first frame drawn”当作编辑器可用。OctoSense 的 `editor-host` 测试宿主由测试启动和关闭，无需账户即可运行真实控件和本应用包的确切源码。集成的 `connected-app-host` 还验证普通应用包准入、真实的宿主授权、缺少注册信息时的错误、取消操作，以及本地草稿的精确保留。

0.1.0 发布前，安装后的验收流程也已通过：使用真实的 Store、`prepare_launch`、编辑器、宿主 API 和确认面板，只把 GitHub 传输和凭据库换成仅在编译期启用的模拟实现和内存实现。覆盖范围包括仓库分页、空仓库、第二个文件、未保存草稿的保护、确切内容的确认与取消、已有文件和新文件的提交、SHA 冲突、响应丢失时不自动重试，以及离线重启。原始原生截图及记录了源码哈希的回执见 [VALIDATION.md](VALIDATION.md#signed-installed-provider-acceptance)。[最终宿主回归](VALIDATION.md#final-modal-and-cancellation-regression)在修复模态输入和取消问题后，重新跑完了两条流程。要复现，请在本仓库旁边的 OctoSense 检出目录中运行：

```sh
cargo build --locked --release -p octosense-shell \
  --features mobile-apps,acceptance-fixtures \
  --example connected-app-host --example connected-install
python3 tools/connected-e2e/notes.py \
  --bundle ../OctoSense-App-Flow/examples/connected-apps/github-notes/bundle
```

驱动脚本最后输出 `PASS: installed Notes flow with synthetic provider; native pixel review pending`。`acceptance-fixtures` 特性在普通构建中关闭，并拒绝未标记的配置目录和真实的提供商注册信息。测试只使用虚构数据。示例应用本身只使用普通宿主 API，没有测试开关。

[macOS 持续测试记录](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/tools/connected-e2e/evidence/notes-soak-20261006/README.zh-CN.md)包含 156 轮，其中有一次 10 分钟的连续运行，验证了精确的草稿恢复和取消确认。运行期间内存有所增长，长期内存稳定性未经验证。独立的 OnePlus 6 `OctoSenseNotesTest` APK 在修复 Android 输入法组合末词丢失的问题后，通过了本地编辑、软键盘和硬件 Enter，以及精确的冷启动恢复。[手机配置](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/tools/connected-e2e/android-notes.zh-CN.md)使用签名私有目录，不使用提供商凭据。手机上没有配置 GitHub 连接，因此这不是真实仓库验收。

**未验证：** 真实 GitHub OAuth、读取、提交和冲突；Android 后台生命周期；Windows 和 Linux 界面；应用 Agent 的工具调用；亲手点按批准保存。在 desktop-v0.1.0-beta.2 上，宿主的 GitHub 确认面板不检查是否为亲手点按；[OctoSense 桌面版 0.1.0-rc.1](../../../README.zh-CN.md#下载兼容-shell) 在 macOS 上要求在原生审阅界面上亲手点按，在 Windows 和 Linux 上则不允许保存。真实验收需要启用设备授权流程的客户端 ID、用户亲自授权，以及一个可丢弃的仓库、分支和路径；不复用 GitHub CLI 凭据。本副本和已发布应用都没有实现 Rinx 的全部功能。任务约定见 [BRIEF.md](BRIEF.md)。
