# 脚本应用模板

[English](README.md) | 简体中文

一个可运行的 OctoSense 脚本应用：**My Notes**（输入一条笔记，保存在应用自己的存储中，
点击即可删除）。`tools/octo new <dir>` 会复制它并设置 id 和名称；用
`tools/octo run <dir>/bundle` 运行。

```text
script-app/
  README.md        this file (not copied)
  AGENTS.md        instructions for an agent working in the new app's repository (copied)
  .gitignore       keeps keys, build output and .local-state out of git (copied)
  bundle/          the app; the only thing ever submitted (copied)
    manifest.json  id my-notes, version 0.1.0, capability storage
    listing.json   store text: EVERY publisher value is a placeholder
    main.splash    the program
    assets/icon.svg
```

它演示的内容（均已在 `card-host` 中验证）：用顶层 `let` 保存状态，用
`start_timeout(0.05, …)` 启动加载函数，在应用的隔离目录中使用 `fs.exists/read/write`，
`parse_json`/`to_json`，`ui.<id>.text()/set_text()/render()`，带空状态的
`on_render` 列表，`ButtonFlat{on_click}`，以及 `GestureView{on_tap}` 行。

它有意不完整，以免复制出来的应用被意外发布：

- `listing.json` 引用了 `screenshots/01-main.png`，但这个文件并不存在。在你截取一张真实截图
  （`tools/octo shot`）之前，检查门会拒绝这个 bundle。不要添加假图片。
- 发布者名称、支持 URL 和隐私政策 URL 都是占位符（`tools/octo check` 会提示）。
  由人来替换它们。
- `platforms` 写的是 `android`；请换成你实际运行过的平台（在 Mac 上用 `card-host` 运行即
  `macos`），并由人确认。

来源：与 OctoSense-App-Hub 同期制作的脚本应用模板草稿（从未提交到那里；App Hub 的
`templates/app/` 是卡片应用起步模板），
只做了一处修正：列表的空状态改为 `for` 之前单独的一个 `if`，因为在 `on_render` 中使用
`if … else for …` 时，空分支什么都不画，还会留下过期的行。下一步：
[docs/QUICKSTART.md](../../docs/QUICKSTART.md)。
