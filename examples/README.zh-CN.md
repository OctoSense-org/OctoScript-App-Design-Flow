# 示例

[English](README.md) | 简体中文

用 [image-to-card 流程](../flows/image-to-card/FLOW.md) 构建的参考旅程，以及用
[script-app 流程](../flows/script-app/FLOW.md) 构建的受控应用。
每个示例把源码、操作说明和验证证据放在一起；卡片旅程还包含服务代码和已评审场景。
运行时状态和个人数据均被忽略，不入库。旧的旅程示例在重构之前位于 `apps/<name>/`。

| 示例 | 呈现方式 | 说明 |
| --- | --- | --- |
| [黑客松 Agent 应用](agentic-hackathon/README.zh-CN.md) | 原生 Splash 应用 / 应用 Agent 集成 | Email Action 和 Meeting Planner：虚构数据、真实 Agent 入口、明确标注的离线路径、确认、回执及原生回归测试。 |
| [Aircon](aircon/README.zh-CN.md) | 原生卡片 / WASM | 一条从购买到安装的旅程，含 12 个画面状态和 14 个提取出的服务卡片变体。 |
| [School](school/README.zh-CN.md) | 原生卡片 / WASM | 学校通知、日历与缴费旅程。 |
| [Health](health/README.zh-CN.md) | 原生卡片 / WASM | 虚构的体检预约旅程。 |
| [Reunion](reunion/README.zh-CN.md) | 原生卡片 / WASM | 同学聚会的筹划、回复（RSVP）与付款旅程。 |
| [Calendar](calendar/README.zh-CN.md) | 原生卡片 / 浏览器预览 + 同步服务器 | 双设备日历：10 个画面、4 个服务卡片，以及一个基于 SQLite 的操作日志服务器，每个客户端都重放同一份日志。 |

[shared/](shared/README.zh-CN.md) 存放通用的浏览器适配器和历史上的跨应用验证产物，它不是一个应用。

系统脚本应用（News、Photos、Maps、Camera、Mail）以及个人数据技能已迁移到
[OctoSense-org/OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps)。
原生客户端和运行时已迁移到
[OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard)。
Makepad 和 OctoScript 位于独立的
[原生工作区](../docs/NATIVE-WORKSPACE.md)。

## 单个示例的目录结构

在一个示例中，`cards/` 存放完整的画面状态。例如
`aircon/cards/aircon-01` 到 `aircon-12` 是**同一个 Aircon 应用**的十二个画面，
而不是十二个应用。`service-cards/` 存放从这些画面中提取出的较小交互面板
（订单、安装预约、日历更新、支付面板），各自带有数据和操作。它们的归属名
标识的是旅程中的服务，而不是额外的项目。

每个示例把设计源文件、场景、服务代码和 `image-to-appcard-flow.json` 放在一起。
从仓库根目录运行流程，并显式选择一个示例：

```sh
bash tools/image-to-appcard-flow.sh plan \
  --project "$PWD/examples/aircon" \
  --manifest "$PWD/examples/aircon/image-to-appcard-flow.json"
```

`plan` 打印每个阶段将要运行的命令，manifest 有效时以 0 退出；它不实际运行任何东西。
要开始一个新项目，复制
[`flows/image-to-card/examples/flow.template.json`](../flows/image-to-card/examples/flow.template.json)。

原生 UI 测试请使用 [Makepad 的内置 instrument](../flows/core/NATIVE-INSTRUMENT.md)，
并隐藏窗口。旧的 Studio 脚本和回执属于历史资料；搬移它们并不等于重新完成了原生或图像一致性验收。

## 已记录的证据保留原始路径

回执和证据记录于重构之前，仍然引用 `lab/...`、`apps/...`、`pipeline/...`
或仓库以前的名字（`Octosense-Service-AppCards`、`Octoscript-AppCard`）。
它们是与哈希绑定的运行记录，因此不做改写：

- `*/cards/*/rounds/`、`*/evidence/`、`aircon/wizard/wasm-host/smoke-evidence/`
- `aircon/runtime/infrastructure.json` 以及它所哈希的 `*.patch` 文件
- `shared/verification.json`、`shared/layout-validation.json`、`shared/flows-history.md`
- `*/wizard/card-bundle/cards.provenance.json`
- `calendar/source/storyboard.html`（保留原始字体 URL 的设计源文件）

`aircon/scripts/verify_native_flow.py` 和 `verify_standalone_cards.py` 在重新哈希源文件时，
会把记录中的 `lab/` 和 `apps/` 前缀映射到 `flows/` 和 `examples/`。
