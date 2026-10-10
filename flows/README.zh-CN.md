# 设计流程

[English](README.md) | 简体中文

未注明中文版的链接指向英文文档。

每个流程把一种输入转换成 OctoSense 能运行的产物。按手头已有的输入选择流程。除非某一步另有说明，所有命令都在仓库根目录下运行。

| 你手上有 | 流程 | 产出 | 运行环境 |
| --- | --- | --- | --- |
| 一份文字需求（应用做什么、有哪些界面和数据） | [script-app](script-app/FLOW.md) | 一个隔离运行的脚本应用包（`manifest.json`、`main.splash`、资源文件） | App Hub `card-host`，之后是 OctoSense Shell |
| 一张生成的 UX 图，或单个界面 | [image-to-card](image-to-card/FLOW.md) | 用 L0（声明式卡片语言）编写的原生卡片（`page.card`、`page.data.json`、`kit/`）、抽取出的服务卡片、一个卡片应用包，可选 WASM | 打包后在 App Hub `card-host` 中运行；迭代期间用 Makepad Studio 或 `beauty-host`（见该流程） |
| 一套已获授权的 Sketch 设计套件 | [kits/sketch](kits/sketch/FLOW.md) | 一个**主题套件**（原生 L0 组件和主题），不是应用 | 供其他流程和 OctoScript-Makepad 使用 |
| 本仓库中已有的应用 | 它的 `examples/<name>/README.md`；见 [examples/](../examples/README.zh-CN.md) | 该示例所记录的内容 | 以各示例的记录为准 |

速览卡片还应配合 [AppCard UX 技能](../skills/octoscript-app-card-ux/SKILL.md)，检查各层展示、宿主工作区/Chat 集成，并凭实际证据验收。该技能补充所选流程，不替代发布检查。

以下是支撑代码，不是流程：

- [core/](core/README.md)：所有流程共用的策略、评审包、修复、Studio 桥接、组合与检查；[REPRODUCE.md](core/REPRODUCE.md) 是环境搭建说明，[NATIVE-INSTRUMENT.md](core/NATIVE-INSTRUMENT.md) 是原生测试手册。
- [image-lib/](image-lib/README.md)：image-to-card 流程调用的图像库，附带按设计归档的证据语料。
- [STRUCTURE.md](STRUCTURE.md)：目录归属与保留规则；[LLM-COMPOSITION.md](LLM-COMPOSITION.md)：组合约定。
- `maintain.py` 和 `tests/`：存储盘点与缓存清理。

## 每个流程都遵循同一份约定

1. **先检查前置条件。** 每个 `FLOW.md` 都有一条检查命令。在第 1 步之前运行它。如果失败，修复它指出的问题；不要开始流程。
2. **每一步都是一条命令加一个通过条件。** 原样运行命令，再检查通过条件。遇到第一个失败就停止，并报告失败的步骤、命令、退出码和日志路径。不要跳过步骤，不要反复重试失败的步骤直到它碰巧通过，也不要为了让检查通过而修改已记录的证据。
3. **人工检查点。** 标记为 **HUMAN** 的步骤是 Agent 必须停下的地方：报告已准备好的内容，然后等待人来处理。检查点包括：
   - **使用付费生成器生成图像。** 由人运行生成器（或明确授权这笔花费），并提供原始输出和确切的提示词。
   - **语义与视觉评审。** 由人（或其指定的评审人）对照源图检查映射，并批准截图。脚本通过不等于视觉批准。
   - **发布者身份与 Release 工作流。** 发布前审阅 GitHub 仓库、工作流和 tag。App Hub 只接受带 GitHub 证明的 Release，不涉及任何发布者密钥：不要创建发布者密钥、为清单签名，或为了发布而传入 `--publisher-key`。
   - **Release 与提交。** 为 Release 打 tag，以及在 OctoSense-App-Hub 开 `Submit <app id> <version>` issue（[SUBMITTING §7](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md#7-开提交-issue)），都由人决定。
   - 各流程特有的检查点（例如购买 Sketch 或设计套件）列在该流程的步骤表中。
4. **统一的交接。** 每个应用流程都以相同的方式结束。先设置这些变量：

   - `HUB_BIN` 和 `CARD_HOST_BIN`：`hub` 和 `card-host` 程序的路径。在 [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) 中用 `cargo build --release -p octosense-card-host -p octosense-app-hub` 构建（[QUICKSTART §2](../docs/QUICKSTART.zh-CN.md#2-构建-hub-和-card-host)）。
   - `APP_REPO`：应用仓库的绝对路径，`bundle/` 就在其中。

   如果构建失败并提示 `no variant … TextInputStateQuery`，请看 [构建 `card-host` 时报 `TextInputStateQuery` 错误](../docs/QUICKSTART.zh-CN.md#构建-card-host-时报-textinputstatequery-错误)。

   | # | 步骤 | 命令 | 通过条件 |
   | --- | --- | --- | --- |
   | 1 | 打包为 App Hub 应用包 | 因流程而异；见其 `FLOW.md` 的“Hand-off”一节 | `bundle/` 包含 `manifest.json`、`listing.json`、程序（`page.card` + `kit/`，或 `main.splash`）以及 `assets/`，且没有其他类型的文件（例如 `.DS_Store`） |
   | 2 | 写入摘要（stamp） | `"$HUB_BIN" stamp "$APP_REPO/bundle"` | 打印出摘要 |
   | 3 | 检查 | `"$HUB_BIN" check "$APP_REPO/bundle" --allow-unsigned` | 只剩下预期中的截图拒绝和未签名警告 |
   | 4 | 在 `card-host` 中运行 | 在 App Hub 仓库目录中运行：`"$CARD_HOST_BIN" --bundle "$APP_REPO/bundle" --app-data "$APP_REPO/.local-state" --allow-unsigned --remote 8141` | 日志显示 `[makepad-remote] listening on 127.0.0.1:8141`，且没有 `refused` 行 |
   | 5 | 截图 | 在另一个终端中、在本仓库目录下：`tools/octo shot 8141 "$APP_REPO/bundle/screenshots/01-main.png"`，然后 `curl -sS 127.0.0.1:8141/quit`。`shot` 会等应用的控件出现、画面稳定后再截图。 | PNG 显示的是应用，而不是错误画面（**HUMAN** 评审） |
   | 6 | 重新写入摘要并检查 | `"$HUB_BIN" stamp "$APP_REPO/bundle" && "$HUB_BIN" check "$APP_REPO/bundle" --allow-unsigned` | 只剩下未签名警告 |
   | 7 | 审核问题 | `mkdir -p "$APP_REPO/build" && "$HUB_BIN" scan "$APP_REPO/bundle" --packet "$APP_REPO/build/review.json"` | 已生成审核包，问题都已书面回答：七个；应用包附带 `tools.json`、`AGENT.md` 或 skills 时为八个 |
   | 8 | 请求发布（**HUMAN**，可以提前） | 在 App Hub 开 `Submit <app id> <version>`，附仓库/版本/commit、截图和权限 | issue 记录发布意图；之后可补充 Release 产物 |
   | 9 | 准备 Release（公开操作需 **HUMAN** 授权） | `tools/octo publish-github "$APP_REPO"`；审阅并 commit 已测试源码和工作流，再推送新的 `v<manifest.version>` tag | GitHub 的 `publisher-verify` 和 `publisher-pack` 成功；把 Release、pack 和摘要补充到 issue |
   | 10 | Hub 审核 | Hub 检查确切的候选版本，管理员审核并批准 | 经过认证的签名目录完成发布；GitHub Release 本身不代表批准 |

   `card-host` 拒绝已封存的 Release，所以先测试可编辑源码并截图。Release 工作流需要契约 1.8.0 / `publisher-github-v1`；安装 Release 需要兼容宿主，例如 macOS 上的 OctoSense 桌面版 0.1.0-rc.1。上表列出的是通过条件，不是测试结果。本仓库的 [docs/PUBLISHING.zh-CN.md](../docs/PUBLISHING.zh-CN.md) 讲解完整流程。App Hub 的 [SUBMITTING.zh-CN.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md) 讲解提交 issue 和审核，它的 [PUBLISHING.zh-CN.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md) 是每条准入规则的参考。
5. **购买的素材不外传。** 不要把购买的设计素材或本地日志当作通用示例分享。

## 清理本地存储

```sh
python3 flows/maintain.py inventory            # 只读的存储盘点
python3 flows/maintain.py clean --exports      # 预览缓存清理
python3 flows/maintain.py clean --exports --apply
```

清理器只删除 Python 字节码和 Finder 元数据；加上 `--exports` 时，还会删除可重建的 Sketch 导出缓存。源文件、最终资源、截图、评审轮次和环境都不在其范围内。
