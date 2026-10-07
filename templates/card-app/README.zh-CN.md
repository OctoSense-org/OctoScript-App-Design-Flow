# 卡片应用模板（指引）

[English](README.md) | 简体中文

未注明中文版的链接指向英文文档。

**卡片应用**是用 L0（声明式卡片语言）编写的 `page.card`，加上它的 `page.data.json` 和 `kit/`，由宿主转换为控件。它是生成出来的，不是手写的：使用 [image-to-card 流程](../../flows/image-to-card/FLOW.md)（或者用 [Sketch 套件流程](../../flows/kits/sketch/FLOW.md)生成套件），然后按 [flows/README.zh-CN.md](../../flows/README.zh-CN.md#每个流程都遵循同一份约定) 中的统一交接步骤完成；应用包中放的是 `page.card` 和 `kit/`，而不是 `main.splash`。

App Hub 的 [`templates/app/`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/templates/app) 是卡片应用包的元数据脚手架：清单、商店信息、图标和 Agent 说明。它没有入口文件（`page.card`），也没有截图，即使先运行 `hub stamp`，准入检查仍会报 `entry` 和 `listing` 两项拒绝。请加入流程生成的 `page.card`、`kit/` 和一张真实截图，并把占位的 `platforms` 换成你测试过的平台。

套件的 `font_src` 只能引用一个内置字体：`makepad_widgets:resources/Inter.ttf`。其他字体（包括中日韩字体）都要以 `.ttf` 或 `.otf` 文件的形式放进应用包，应用包总大小不超过 8 MiB（内置中日韩字体的进展见 [App Hub#75](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/75)）。

如果应用有自己的逻辑、状态和请求，请改用[脚本应用模板](../script-app/README.zh-CN.md)。
