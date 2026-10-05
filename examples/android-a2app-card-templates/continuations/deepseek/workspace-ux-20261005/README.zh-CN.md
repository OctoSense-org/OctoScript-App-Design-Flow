# 手机工作区说明文字修正

[English](README.md) | 简体中文

2026-10-05，在 OnePlus 6 的 Glance 工作区验收中发现，DeepSeek 照片和
YouTube 卡片的离线数据说明被截断。Android 上的 DeepSeek v4 flash 使用
`view_image` 读取两张真实手机截图，把对应说明设置为 `width: .fill`。
操作员提供反馈并原样复制模型输出，没有修改生成源码。

这两个文件只替代[第 12 轮](../turn-12/README.zh-CN.md)中对应的
`glance.card`；数据和 Splash 应用不变。[来源记录](provenance.json)保存两次
成功的模型修改以及原文件、输出文件的 SHA-256，不包含凭据或私有推理。

复测截图显示，点击收藏或稍后观看后，完整说明可以换行显示。收起并重新打开
仍保留本地选项，宿主 Chat 输入框在 Android 键盘弹出后仍可操作。卡片继续
使用虚构数据，不能加载媒体或执行外部操作。本次修正不代表重新给出整体 UX 分数。

| 卡片 | 修正前 | 修正后 |
| --- | --- | --- |
| 照片 | [文字被截断](screenshots/photo-before.png) | [完整换行](screenshots/photo-after.png) |
| YouTube | [文字被截断](screenshots/youtube-before.png) | [完整换行](screenshots/youtube-after.png) |

验证使用 OctoSense 独立 Android 验收包，版本 `2026100503`，基于
`a2a0524d` 加工作区验收修改。在本目录已执行以下来源验证命令：

```sh
python3 verify.py
```

验证器对不可变原文件重放记录的一次替换，并检查两端哈希；不代表新一轮
App Hub/商店验收，也不代表真实邮件发送、视频播放或照片接入通过。
