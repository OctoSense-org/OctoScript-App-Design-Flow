# 示例

[English](README.md) | 简体中文

表中的示例包括参考用户旅程（用 [image-to-card 流程](../flows/image-to-card/FLOW.md)构建的完整多画面应用）、用 [script-app 流程](../flows/script-app/FLOW.md)构建的受控应用，以及保留历史手机评审证据的 Android 模型原型档案。每个示例都把源码、操作说明和验证证据放在一起；卡片旅程还各自拥有服务代码、已评审的卡片场景、设计源文件、启动器和测试。运行时状态和个人数据不入库。

| 示例 | 运行方式 | 说明 |
| --- | --- | --- |
| [黑客松 Agent 应用](agentic-hackathon/README.zh-CN.md) | 原生 Splash 应用 / 应用 Agent 集成 | Email Action 和 Meeting Planner：虚构数据、真实 Agent 入口、明确标注的离线路径、确认、回执及原生回归测试。 |
| [Aircon](aircon/README.zh-CN.md) | 原生卡片 / WASM | 一条从购买到安装的旅程，含 12 个画面状态和 14 个提取出的服务卡片变体。 |
| [School](school/README.zh-CN.md) | 原生卡片 / WASM | 学校通知、日历与缴费旅程。 |
| [Health](health/README.zh-CN.md) | 原生卡片 / WASM | 虚构的体检预约旅程。 |
| [Reunion](reunion/README.zh-CN.md) | 原生卡片 / WASM | 同学聚会的筹划、回复（RSVP）与付款旅程。 |
| [Calendar](calendar/README.zh-CN.md) | 原生卡片 / 浏览器预览 + 同步服务器 | 双设备日历：10 个画面状态、4 个服务卡片，以及一个基于 SQLite 的服务器，每个客户端都重放它的操作日志。 |
| [Android 模型编写的卡片原型](android-a2app-card-templates/README.zh-CN.md) | Android 上的 AppStudio；概览/展开/完整应用 | 两份模型编写的六类集合：各自离线原型整体 4.5/5、视觉 4.4/5；源码精确重放及原生证据。 |

[shared/](shared/README.zh-CN.md) 存放通用的浏览器适配器和以往的跨应用验证产物；它不是应用。

[connected-apps/](connected-apps/README.zh-CN.md) 存放 GitHub Notes、Inbox Assistant 和 Google Calendar 的开发副本。这三个脚本应用已在 App Hub 发布，通过 OctoSense 宿主登录 GitHub 或 Google。[connected-apps 的 README](connected-apps/README.zh-CN.md) 说明每个应用如何构建和提交，以及哪些做法可以照搬、哪些应当避免。

系统脚本应用（News、Photos、Maps、Camera、Mail）以及个人数据技能位于 [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps)。原生客户端和运行时位于 [OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard)。Makepad 和 OctoScript 位于独立的[原生工作区](../docs/NATIVE-WORKSPACE.md)。

## 单个示例的目录结构

在每个示例中，`cards/` 存放完整的画面状态：`aircon/cards/aircon-01` 到 `aircon-12` 是**同一个 Aircon 应用**的 12 个画面状态，而不是 12 个应用。`service-cards/` 存放从这些画面中提取出的较小交互面板（订单、安装预约、日历更新、支付面板），各自带有数据和操作。服务卡片按 `service-cards/catalogue.json` 中的 `owner_app` 字段分组。Aircon 的所属服务为 `shopping`、`logistics`、`installation`、`calendar` 和 `payment`。每个服务都是旅程的一部分，而不是独立的项目。

每个示例都有自己的流程清单 `image-to-appcard-flow.json`。从仓库根目录运行流程，并显式选择一个示例：

```sh
bash tools/image-to-appcard-flow.sh plan \
  --project "$PWD/examples/aircon" \
  --manifest "$PWD/examples/aircon/image-to-appcard-flow.json"
```

`plan` 只打印每个阶段将要运行的命令，不执行它们；清单有效时退出码为 0。要开始一个新项目，把 [`flows/image-to-card/examples/flow.template.json`](../flows/image-to-card/examples/flow.template.json) 复制到项目目录，并命名为 `image-to-appcard-flow.json`。

原生 UI 测试请使用 [Makepad 的内置 instrument](../flows/core/NATIVE-INSTRUMENT.md)，并在隐藏窗口模式下运行。旧的 Makepad Studio 脚本和回执只记录以往的运行；它们记录的原生和图像一致性结果早于迁移。

## 已记录的证据保留原始路径

回执和证据记录于重构之前，仍然引用 `lab/...`、`apps/...`、`pipeline/...` 或仓库以前的名字（`Octosense-Service-AppCards`、`Octoscript-AppCard`）。它们是与哈希绑定的运行记录。不要改写以下路径：

- `*/cards/*/rounds/`、`*/evidence/`、`aircon/wizard/wasm-host/smoke-evidence/`
- `aircon/runtime/infrastructure.json` 以及它所哈希的 `*.patch` 文件
- `shared/verification.json`、`shared/layout-validation.json`、`shared/flows-history.md`
- `*/wizard/card-bundle/cards.provenance.json`

`aircon/scripts/verify_native_flow.py` 和 `aircon/scripts/verify_standalone_cards.py` 在重新哈希源文件时，会把记录中的 `lab/` 和 `apps/` 前缀映射到 `flows/` 和 `examples/`。
