# 设计流程

[English](README.md) | 简体中文

一个设计流程把一种输入变成 OctoSense 能运行的东西。按你手上已有的东西选择流程。所有命令都在仓库根目录下运行。

| 你手上有 | 流程 | 产出 | 运行环境 |
| --- | --- | --- | --- |
| 一份文字需求（应用做什么、有哪些页面和数据） | [script-app](script-app/FLOW.md) | 一个隔离运行的脚本应用 bundle（`manifest.json`、`main.splash`、资源文件） | App Hub `card-host`，之后是 OctoSense Shell |
| 一张生成的 UX 图，或单个页面 | [image-to-card](image-to-card/FLOW.md) | 原生 L0 卡片（`page.card`、`page.data.json`、`kit/`）、抽取出的服务卡片、一个卡片 bundle，可选 WASM | 打包后在 App Hub `card-host` 中运行；迭代期间用 Studio 或 `beauty-host` |
| 一套已获授权的 Sketch 设计套件 | [kits/sketch](kits/sketch/FLOW.md) | 一个**主题套件**（原生 L0 组件和主题）。不是应用 | 供其他流程和 Octoscript-Makepad 使用 |
| 本仓库中已有的应用 | 它的 `examples/<name>/README.md`；见 [examples/](../examples/README.zh-CN.md) | 该示例所记录的内容 | 以各示例的记录为准 |

以下是支撑代码，不是流程：

- [core/](core/README.md)：所有流程共用的策略、评审包、修复、Studio 桥接、组合与检查门；
  [REPRODUCE.md](core/REPRODUCE.md) 是环境搭建说明，
  [NATIVE-INSTRUMENT.md](core/NATIVE-INSTRUMENT.md) 是原生测试手册。
- [image-lib/](image-lib/README.md)：image-to-card 流程调用的图像库，附带按设计归档的证据语料。
- [STRUCTURE.md](STRUCTURE.md)：目录归属与保留规则；
  [LLM-COMPOSITION.md](LLM-COMPOSITION.md)：组合约定。
- `maintain.py` 和 `tests/`：存储清单与缓存清理。

## 每个流程都遵循同一份约定

1. **先检查前置条件。** 每个 FLOW.md 都有一条检查命令。在第 1 步之前运行它。
   如果失败，修复它指出的问题；不要开始流程。
2. **每一步都是一条命令加一项通过检查。** 原样运行命令，然后运行通过检查。
   遇到第一个失败就停止，并报告失败的步骤、命令、退出码和日志路径。不要跳过步骤，
   不要把失败的步骤重试到通过，也不要为了让检查通过而修改已记录的证据。
3. **人工检查点。** 标记为 **HUMAN** 的步骤是 agent 必须停下的地方：报告已准备好的内容，
   然后等待人来处理。检查点包括：
   - **使用付费生成器生成图像。** 由人运行生成器（或明确授权这笔花费），
     并提供原始输出和确切的提示词。
   - **语义与视觉评审。** 由人（或其指定的评审者）对照源图检查映射，并批准截图。
     脚本通过不等于视觉批准。
   - **用私钥签名。** 只有密钥持有人运行 `hub keygen` 或 `hub sign-manifest`。
     密钥永远不进入仓库、bundle、提示词或日志。
   - **提交。** 在 OctoSense-App-Hub 开 `Submit <app id> <version>` issue
     （[PUBLISHING §3.8](../docs/PUBLISHING.md#38-submit--human)）由人决定。
   - 各流程特有的检查点（例如购买 Sketch 或设计套件）列在该流程的步骤表中。
4. **统一的交接。** 每个应用流程都以相同的方式结束：

   | # | 步骤 | 命令 | 通过条件 |
   | --- | --- | --- | --- |
   | 1 | 打包为 App Hub bundle | 因流程而异；见其 FLOW.md 的 "Hand-off" | `bundle/` 包含 `manifest.json`、`listing.json`、程序（`page.card` + `kit/`，或 `main.splash`）以及 `assets/` |
   | 2 | 盖章（stamp） | `"$HUB_BIN" stamp bundle` | 打印出摘要 |
   | 3 | 检查 | `"$HUB_BIN" check bundle --allow-unsigned` | 只剩下预期中的截图拒绝和未签名警告 |
   | 4 | 在 `card-host` 中运行 | `"$CARD_HOST_BIN" --bundle "$PWD/bundle" --app-data "$PWD/.local-state" --allow-unsigned --remote`（在 App Hub checkout 中运行） | 日志显示远程端点，且没有 `refused` 行 |
   | 5 | 截图 | `curl --fail -sS "$APP_ENDPOINT/g?raw=1" -o bundle/screenshots/01-main.png`，然后 `curl -sS "$APP_ENDPOINT/quit"` | PNG 显示的是应用，而不是错误画面（**HUMAN** 评审） |
   | 6 | 重新盖章并检查 | `"$HUB_BIN" stamp bundle && "$HUB_BIN" check bundle --allow-unsigned` | 只剩下未签名警告 |
   | 7 | 签名（**HUMAN**） | `"$HUB_BIN" sign-manifest bundle --key "$APP_SIGNING_KEY" --key-id "$APP_PUBLISHER_ID"` | `"$HUB_BIN" check bundle --publisher-key "$APP_PUBLISHER_ID=$APP_PUBLISHER_PUBLIC_KEY"` 通过，其中 `APP_PUBLISHER_PUBLIC_KEY="$("$HUB_BIN" pubkey "$APP_SIGNING_KEY")"` |
   | 8 | 提交（**HUMAN**） | 在 OctoSense-App-Hub 开 `Submit <app id> <version>` issue（[PUBLISHING §3.8](../docs/PUBLISHING.md#38-submit--human)） | 维护者对完全相同的字节重新运行检查门 |

   `HUB_BIN` 和 `CARD_HOST_BIN` 是从
   [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)
   构建的 `hub` 和 `card-host` 二进制文件
   （`cargo build --release -p octosense-app-hub --bin hub` 和
   `cargo build --release -p octosense-card-host --bin card-host`）。当前的
   `card-host` 拒绝运行已签名的 manifest，所以要在签名之前截图。本仓库的
   [docs/PUBLISHING.md](../docs/PUBLISHING.md) 针对脚本应用讲解交接流程；
   约定本身以 App Hub 的
   [docs/PUBLISHING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md) 为准。

## 存储

```sh
python3 flows/maintain.py inventory            # read-only storage inventory
python3 flows/maintain.py clean --exports      # preview cache cleanup
python3 flows/maintain.py clean --exports --apply
```

清理器只删除 Python 字节码、Finder 元数据，以及在使用 `--exports` 时可重建的
Sketch 导出缓存。源文件、最终资源、截图、评审轮次和环境都不在其范围内。
不要把购买的资源或本地日志当作通用示例分享。
