# 手机工作区说明文字与导航修正

[English](README.md) | 简体中文

2026-10-05，在 OnePlus 6 的 Glance 工作区验收中发现，DeepSeek 照片、
YouTube 和新闻卡片的离线数据说明被截断。Android 上的 DeepSeek v4 flash 使用
`view_image` 读取真实手机截图，把六类模板的说明设置为 `width: .fill`。
操作员提供反馈并原样复制模型输出，没有修改生成源码。

六个 `.glance.card` 文件替代[第 12 轮](../turn-12/README.zh-CN.md)中对应的
`glance.card`；六个 `.main.splash` 替代各类型的 `bundle/main.splash`。
输入数据和其余安装包文件不变。[来源记录](provenance.json)保存成功的模型修改
以及原文件、输出文件的 SHA-256，不包含凭据或私有推理。

深色 Paper 宿主还暴露出六个 Splash 程序的导航按钮截断。DeepSeek 看真实截图后
给出第一次字体修改，操作员复查发现 States 仍被截断，遂把新截图退回模型。
第二次 Android 输出把 `NavBtn` 改为明确的 11 点字体、6 点内边距，保留 44 点
高度，四个按钮已在 OnePlus 6 完整显示。两次连续修改都保留并可重放；第一次
未达标的输出不计为通过。

导航证据：[原始](screenshots/navigation-before.png)、
[第一次修正](screenshots/navigation-first-attempt.png)、最终
[邮件](screenshots/mail-navigation-after.png)、
[日历](screenshots/calendar-navigation-after.png)、
[新闻](screenshots/news-navigation-after.png)、
[财经](screenshots/finance-navigation-after.png)、
[照片](screenshots/photo-navigation-after.png)、
[YouTube](screenshots/youtube-navigation-after.png)。

复测截图显示，点击收藏、稍后观看或保存后，完整说明可以换行显示。收起并重新打开
仍保留本地选项，宿主 Chat 输入框在 Android 键盘弹出后仍可操作。卡片继续
使用虚构数据，不能加载媒体或执行外部操作。本次修正不代表重新给出整体 UX 分数。

| 卡片 | 修正前 | 修正后 |
| --- | --- | --- |
| 照片 | [文字被截断](screenshots/photo-before.png) | [完整换行](screenshots/photo-after.png) |
| YouTube | [文字被截断](screenshots/youtube-before.png) | [完整换行](screenshots/youtube-after.png) |
| 新闻 | [文字被截断](screenshots/news-before.png) | [完整换行](screenshots/news-after.png) |

邮件、日历和财经具有同样的说明宽度问题，DeepSeek 也做了相同的最小修改，
与新闻一起复测本地操作和收起恢复。最后一轮请求曾因锁屏后的后台网络限制失败，
恢复前台后 Android 模型成功修改；失败请求没有产生导入源码。

验证使用 OctoSense 独立 Android 验收包：照片／视频说明文字为 `2026100503`，
其余说明和导航为 `2026100504`，基于
`a2a0524d` 加工作区验收修改。在本目录已执行以下来源验证命令：

```sh
python3 verify.py
```

验证器对不可变原文件重放记录的一次替换，并检查两端哈希；不代表新一轮
App Hub/商店验收，也不代表真实邮件发送、视频播放或照片接入通过。
