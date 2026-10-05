# 手机工作区回复跳转修正

[English](README.md) | 简体中文

2026-10-05，操作员在 OnePlus 6 点击邮件 L1 的 Reply，界面仍停在阅读视图。
Android `MiniMax-M3.1-Flash-Preview` 看过截图并阅读原源码后确认：`do_reply`
只修改了 `route`，但编辑器父视图只在 depth 2 显示。模型自行在函数中添加
`depth = 2`，保留草稿与其他应用行为。操作员原样复制输出字节。

[`mail.main.splash`](mail.main.splash) 仅替代
[`turn-14/card-templates/mail/bundle/main.splash`](../turn-14/card-templates/mail/bundle/main.splash)。
[来源记录](provenance.json)包含成功修改及两端哈希。在本目录已执行：

```sh
python3 verify.py
```

手机测试包 `2026100504` 已验证从 L1 打开编辑器、弹出键盘输入，以及收起键盘、
收起工作区并重新打开后保留文字。宿主的内部滚动修复与模型的路由修复分别记录。
截图：[修正前](screenshots/reply-before.png)、[打开编辑器](screenshots/reply-after.png)、
[键盘](screenshots/keyboard.png)、[保留草稿](screenshots/retained.png)。

固定头部和底部仍使键盘上的编辑区域偏小，审核控件可能需要滚动或收起键盘；
这不是 9/10 视觉签收。没有点击演示 Queue reply 或执行真实 SMTP 发送，
也没有安装新的 App Hub 应用包或连接邮箱。
