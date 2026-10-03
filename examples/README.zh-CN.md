# 示例

[English](README.md) | 简体中文

这里包括 [image-to-card 流程](../flows/image-to-card/FLOW.md) 的参考旅程，
以及在手机上生成和评审的 Android 原型。image-to-card 示例各自拥有服务代码、
已评审的卡片场景、设计源文件、启动器、测试和 fixture 证据。
运行时状态和个人数据均被忽略，不入库。重构之前它们位于 `apps/<name>/`。

| 示例 | 呈现方式 | 说明 |
| --- | --- | --- |
| [Aircon](aircon/README.zh-CN.md) | 原生卡片 / WASM | 一条从购买到安装的旅程，含 12 个画面状态和 14 个提取出的服务卡片变体。 |
| [School](school/README.zh-CN.md) | 原生卡片 / WASM | 学校通知、日历与缴费旅程。 |
| [Health](health/README.zh-CN.md) | 原生卡片 / WASM | 虚构的体检预约旅程。 |
| [Reunion](reunion/README.zh-CN.md) | 原生卡片 / WASM | 同学聚会的筹划、回复（RSVP）与付款旅程。 |
| [Calendar](calendar/README.zh-CN.md) | 原生卡片 / 浏览器预览 + 同步服务器 | 双设备日历：10 个画面、4 个服务卡片，以及一个基于 SQLite 的操作日志服务器，每个客户端都重放同一份日志。 |
| [Android 模型编写的卡片原型](android-a2app-card-templates/README.zh-CN.md) | Android 上的 AppStudio；概览／展开／完整应用 | 两份模型编写的六类集合：各自离线原型整体 4.5/5、视觉 4.4/5；源码精确重放及原生证据。 |

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
