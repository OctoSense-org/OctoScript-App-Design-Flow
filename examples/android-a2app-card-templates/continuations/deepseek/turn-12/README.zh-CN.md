# DeepSeek 第 12 轮：经过评审的离线原型

[English](README.md) | 简体中文

此快照包含 DeepSeek 在 Android 上编写的邮件、日历、新闻、财经、照片和
YouTube 六类原型。[独立代理评审](visual-review.json)给出 **离线原型整体 4.5/5、视觉 4.4/5**。
已执行路径中未观察到功能阻塞。这是产物评分，不是通用模型排名、商店批准，
也不代表所有视觉检查通过。

25 个模型文件在导入时保持原字节。[来源清单](source-receipt.json)、
[严格重放](model-authorship-validation.json)及[生成记录](generation-record.json)
关联了原先十轮集合和第 11、12 轮。每组原生运行前后均比较了全部 25 个文件，
其清单与此快照一致。没有手工修改应用源码。之前的
[集合](../../../collection/README.zh-CN.md)及三轮邮件对比仍是独立历史证据。

保留的模型 `DESIGN.md` 写于最终操作检查之前。其中待验证或自报验证的
措辞属于当时检查点；下面较新的源码绑定报告说明实际观察结果。评分是另一
代理的编辑评审判断，不是人工批准或商店验收。

## 已观察行为及保留的失败

| 运行组 | 行为通过／步骤 | 原始通过／步骤 | 解释 |
| --- | --- | --- | --- |
| [初次原生套件](evidence/deepseek-r12-validation/summary.json) | 87/99 | 79/99 | 四类套件未先打开 States 就寻找 Empty／Error／Ready，出现十二次操作目标失败 |
| [States 补测](evidence/deepseek-r12-preview-followup/summary.json) | 35/35 | 35/35 | 邮件和四类领域应用打开 States，执行 Loading／Empty／Error／Ready 后关闭 |
| [最后一项套件](evidence/deepseek-r12-last-item/summary.json) | 25/27 | 23/27 | 财经／照片用了两条错误的空状态期望文案；YouTube 九步全通过 |
| [修正文案后补测](evidence/deepseek-r12-last-item-copy-corrected/summary.json) | 18/18 | 16/18 | 财经行为 9/9、原始 7/9；照片两者均 9/9 |

各次运行分开保留：原始失败报告和输入套件，与修正后的操作输入并列归档。
期间模型源码没有改变。`behavior_pass` 表示实际行为断言；原始 `pass` 还包括
原生几何和可用按钮目标检查。剩余原始发现包括滚动视口／键盘裁切，不删除
这些记录，也不宣称全部边界检查通过。

邮件十二步应用套件和九步键盘套件的行为断言全部通过：空白发送校验、归档／
撤销、邮件身份、输入、可达的本地演示 Send 及草稿保留。日历二十二步行为
全通过，包括逐事件独立 RSVP，以及最后事件详情从标题开始显示。领域套件
验证逐项可逆状态、第二项身份及筛选；补测覆盖展开的预览状态和最后一行
详情导航。财经第三项需要原生滚动；财经／照片／YouTube 最后详情截图的
标题都从顶部显示。

六张[导出概览](evidence/glances/report.json)渲染通过且稳定，卡片／数据哈希
匹配。源码与第 11 轮相同；这是重新验证，不计为第 12 轮概览改进。渲染不
证明导出卡片交互、shell 发布或 44 点触控目标。原生应用快照仍报告
`settled:false`；此标记与已观察行为、几何检查分别保留。

## 精选原始截图

| 类别 | 导出概览 | 展开／原生交互 | 完整应用路径 |
| --- | --- | --- | --- |
| 邮件 | [概览](evidence/glances/mail.png) | [真实 Android 键盘及 Send](evidence/deepseek-r12-validation/mail-keyboard/05-send-reachable-with-keyboard-android.png) | [收件箱](evidence/deepseek-r12-validation/mail/08-full-app.png) |
| 日历 | [概览](evidence/glances/calendar.png) | [展开](evidence/deepseek-r12-validation/calendar/01-expanded.png) | [最后事件详情](evidence/deepseek-r12-validation/calendar/12-last-event-detail.png) |
| 新闻 | [概览](evidence/glances/news.png) | [展开](evidence/deepseek-r12-validation/news/03-expanded.png) | [集合](evidence/deepseek-r12-validation/news/04-full-app.png) |
| 财经 | [概览](evidence/glances/finance.png) | [展开](evidence/deepseek-r12-validation/finance/03-expanded.png) | [最后证券](evidence/deepseek-r12-last-item-copy-corrected/finance/03-last-detail-top.png) |
| 照片 | [概览](evidence/glances/photo.png) | [展开](evidence/deepseek-r12-validation/photo/03-expanded.png) | [最后项目](evidence/deepseek-r12-last-item-copy-corrected/photo/03-last-detail-top.png) |
| YouTube | [概览](evidence/glances/youtube.png) | [展开](evidence/deepseek-r12-validation/youtube/03-expanded.png) | [最后项目](evidence/deepseek-r12-last-item/youtube/03-last-detail-top.png) |

[证据索引](evidence/index.json)列出十八张原始 PNG、对应原生快照，以及每份
原始报告、完整操作工具调用记录和实际输入套件。报告中其他截图名称指向
未复制进此精简归档的操作原件。只有标明的 Android 整屏图包含系统键盘，
普通应用纹理截图不包含键盘。

## 评审限制与复现

五项[评审标准](review-status.json)分别为：层级／紧凑度 4.2、深度导航 4.6、
状态／键盘 4.6、统一性／真实限制 4.5、源码绑定证据 4.6。整体 4.5 达到
A− 原型目标，单独视觉为 4.4。邮件／日历仍有较大空隙，财经展示工具状态
残留一个 `0`。组件质量与整屏／展示工具界面的限制分开记录。

这些是离线会话状态演示。邮件不真正发送；RSVP／保存／关注不形成持久服务
记录。照片和 YouTube 明确显示媒体不可用。这里不证明 App Hub 准入、签名、
发布或生产集成。[当前清理记录](../../cleanup.json)确认两个测试包的临时供应商／授权文件
已移除、包已停止、原来六十秒屏幕超时已恢复。旧清理记录仍只属历史证据。

将归档源码放入已授权测试包、准备当前开发者授权后，从本 `turn-12/` 目录
使用明确操作参数：

```sh
python3 ../../../reproduce.py --runtime-root /path/to/OctoSense \
  --serial DEVICE_SERIAL --package dev.makepad.octosense.studio \
  --workspace /data/user/0/dev.makepad.octosense.studio/files/TRUSTED_WORKSPACE \
  --suite evidence/deepseek-r12-validation/calendar/suite.json \
  --output /path/to/new-calendar-evidence
python3 ../../../validate-model-authorship.py --case-dir continuations/deepseek/turn-12
```

第一条命令操作设备，退出状态保留原始检查失败；重放命令仅在本地执行。
各组摘要记录实际工具哈希。[后续流程](../../README.zh-CN.md)说明不可覆盖
导入、源码绑定及两个模型的独立历史。
