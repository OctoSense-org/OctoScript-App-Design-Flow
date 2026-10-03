# MiniMax 第 14 轮：经过评审的离线原型

[English](README.md) | 简体中文

MiniMax 在 Android 上从自己的早期邮件工作继续编写邮件、日历、新闻、财经、
照片和 YouTube。[独立代理评审](visual-review.json)给出 **离线原型整体 4.5/5、
视觉 4.4/5**，整个展示界面为 4.3/5。最终已执行路径中未观察到功能阻塞。
整体达到 A− 原型目标，视觉打磨仍低于该目标。这不证明实时服务已完成，
也不表示模型普遍优于其他模型。

25 个文件原字节导入，[精确重放](model-authorship-validation.json)关联前三轮
冻结基线及第 4–14 轮记录。[源码清单](source-receipt.json)和
[生成记录](generation-record.json)保留这条来源链。操作人员没有手改应用、
卡片或设计源码。

保留的模型 `DESIGN.md` 写于最终操作检查之前。其中待验证或自报验证的
措辞属于当时检查点；下面较新的源码绑定报告说明实际观察结果。评分是另一
代理的编辑评审判断，不是人工批准或商店验收。

## 原生结果，包括失败路径

| 运行 | 行为通过／步骤 | 原始通过／步骤 | 含义 |
| --- | --- | --- | --- |
| [最终六类套件](evidence/minimax-r14-validation/summary.json) | 114/115 | 113/115 | 邮件最后一项选择前漏了必要滚动，原始失败保留 |
| [邮件滚动补测](evidence/minimax-r14-mail-last-followup/summary.json) | 4/4 | 4/4 | 原生滚动显示 Northwind，完整 Invoice 2291 标题及金额在详情顶部 |

两组运行前后均比较全部 25 个文件，与此快照一致。补测不把原运行改写为
115/115。日历、新闻、财经、照片和 YouTube 各自二十步行为及原始检查全通过。
邮件初次套件行为 14/15、原始 13/15。

邮件覆盖已读／未读、归档／撤销、邮件身份、空白回复拒绝，以及真实 Android
键盘下输入和本地排队。输入帧中可见 Queue reply 目标为 129 × 22 逻辑点；
下一次滚动将它展开，排队成功。该原始发现仍保留，不笼统宣称所有目标达到
44 点。日历覆盖逐项独立 RSVP 和全部拒绝状态。其余四类覆盖第二／最后一项
身份、可逆状态、筛选列表、展开操作和从选中项目返回当前概览主项。

六张[导出概览](evidence/glances/report.json)渲染通过且 `settled:true`，卡片、
数据及 PNG 哈希精确匹配。原生检查帧仍保留 `settled:false`，与已观察行为
和几何检查区分。概览渲染不证明导出卡片目标／事件或 shell 发布。
L0／L1／L2 仍表示展示深度，不是权限等级。

## 精选原始截图

| 类别 | 导出概览 | 展开 | 完整应用详情 |
| --- | --- | --- | --- |
| 邮件 | [概览](evidence/glances/mail.png) | [展开](evidence/minimax-r14-validation/mail/01-expanded.png) | [滚动后 Northwind](evidence/minimax-r14-mail-last-followup/03-northwind-detail.png) |
| 日历 | [概览](evidence/glances/calendar.png) | [展开](evidence/minimax-r14-validation/calendar/01-expanded.png) | [最后事件](evidence/minimax-r14-validation/calendar/05-last-detail.png) |
| 新闻 | [概览](evidence/glances/news.png) | [展开](evidence/minimax-r14-validation/news/01-expanded.png) | [最后文章](evidence/minimax-r14-validation/news/10-last-item-detail.png) |
| 财经 | [概览](evidence/glances/finance.png) | [展开](evidence/minimax-r14-validation/finance/01-expanded.png) | [最后证券](evidence/minimax-r14-validation/finance/10-last-item-detail.png) |
| 照片 | [概览](evidence/glances/photo.png) | [展开](evidence/minimax-r14-validation/photo/01-expanded.png) | [最后项目](evidence/minimax-r14-validation/photo/10-last-item-detail.png) |
| YouTube | [概览](evidence/glances/youtube.png) | [展开](evidence/minimax-r14-validation/youtube/01-expanded.png) | [最后项目](evidence/minimax-r14-validation/youtube/10-last-item-detail.png) |

[真实键盘整屏图](evidence/minimax-r14-validation/mail/11-send-scroll-keyboard-android.png)
展示展开后的 Queue 控件。[财经第二证券](evidence/minimax-r14-validation/finance/03-second-item-detail.png)
显示完整红色 −0.38 及正确身份。[索引](evidence/index.json)列出二十张原始 PNG、
对应原生快照、全部七份原始报告及完整工具调用记录。输入步骤未改，只将
操作源码路径元数据改为相对形式，保留原哈希。报告／评审中的其他截图名称
指向这里未复制的操作原件。

## 限制与保留的历史

五项评分为：层级／紧凑度 4.3、深度导航 4.6、状态／键盘 4.6、统一性／真实
限制 4.4、源码绑定证据 4.6。原生邮件行及一些详情仍有较大空隙；强操作按钮、
红色 DEMO 标记和技术性深度标签与内容争夺注意。组件表面为 4.4，整套展示
界面为 4.3，两者分开。状态仅在本次会话内，不真正发送邮件、取实时价格、
加载照片或播放视频；不可用媒体有明确标识。

[历史索引](history/index.json)保留第 4 轮操作授权错误、第 8 轮主动中断、
第 9 轮收集器恢复及模型只读选择、绑定哈希的中途诊断，以及最终第 12 轮
新闻准入成功后打开失败。后续修复不抹去失败检查点。
[源码比较](source-binding.json)确认第 14 轮只改变六条真正的主题声明及
`DESIGN.md`，是七个文件，不是模型自称的九个。原生脚本／manifest 和数据
与第 13 轮一致。工具计数取自转录，不用模型自报值。补丁重放依据
[已验证 Android 内核约定](../../../pinned-apply-patch-semantics.json)。

[当前清理记录](../../cleanup.json)确认两个测试包临时供应商／授权文件已移除、
包已停止、原来六十秒屏幕超时已恢复。本地开发者准入不同于未执行的
App Hub 检查、签名、发布和生产集成。

## 复现

将归档源码和开发者授权准备到已获准测试包后，从本 `turn-14/` 目录使用
明确操作参数：

```sh
python3 ../../../reproduce.py --runtime-root /path/to/OctoSense \
  --serial DEVICE_SERIAL --package dev.makepad.octosense.studio.minimax \
  --workspace /data/user/0/dev.makepad.octosense.studio.minimax/files/TRUSTED_WORKSPACE \
  --suite evidence/minimax-r14-mail-last-followup/suite.json \
  --output /path/to/new-mail-followup
python3 ../../../validate-model-authorship.py --case-dir continuations/minimax/turn-14
```

第一条操作设备，第二条仅在本地重放来源记录。运行摘要记录实际工具哈希。
[后续评审](../../REVIEW.zh-CN.md)比较产物证据，并保留上下文及反馈不相同的事实。
