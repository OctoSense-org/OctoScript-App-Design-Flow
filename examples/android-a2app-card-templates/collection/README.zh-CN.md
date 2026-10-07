# 六类 Android 模型编写的应用卡片

[English](README.md) | 简体中文

Android 上的 DeepSeek 参考现有 A2App 资料，编写了邮件、日历、新闻、财经、
照片和 YouTube 原型。每类都有导出的声明式概览卡片，以及含概览、展开和完整
应用展示的 Splash 应用。**这是经过评审的原型，不是已验收模板集。**
25 个最终模型文件均已原样导入，包括已验证的日历滚动导航修复和共享设计文档。

用户的作者要求贯穿整个流程：手机模型编写设计、源码和修订。监督代理提供
参考资料、评审反馈、操作工具和证据，不手动修复生成的应用代码。
[参考清单](../reference-index.json)记录了 A2App 来源。L0／L1／L2 表示展示
深度，不代表卡片语言升级，也不证明已发布到系统概览页。

## 原生检查证明了什么

| 类别 | 独立观察到的行为 | 完整行为套件：断言通过／原始通过 |
| --- | --- | --- |
| 邮件 | 空回复校验、归档／撤销、文件夹筛选及第二封邮件身份正确；独立键盘路线输入、滚动到 44 点高 Send 并得到本地演示排队反馈 | 12/12、12/12；键盘 7/7、5/7 |
| 日历 | 每个事件的 RSVP 相互独立、列表／周视图导航；模型修复后从最后一行打开详情会从标题开始 | 最终回归 21/21、18/21 |
| 新闻 | 各文章可逆保存、第二篇身份、已存集合和空白／错误／就绪状态 | 14/14、14/14 |
| 财经 | 各证券可逆关注、第二项身份、关注集合和空白／错误／就绪状态；最后一行及详情可达 | 14/14、12/14 |
| 照片 | 各项目可逆保存、第二项身份、已存集合和空白／错误／就绪状态；最后一行及详情可达 | 14/14、12/14 |
| YouTube | 各项目可逆保存、第二项身份、已存集合和空白／错误／就绪状态；最后一行及详情可达；所测视图没有可用 Play 按钮 | 14/14、12/14 |

[证据摘要](evidence/summary.json)保留原始计数和准入结果。`behavior_pass` 只
覆盖观察到的断言；原始 `pass` 还要求原生几何检查及小控件检查通过。财经／
照片／YouTube 的原始失败含视口边缘文字裁切；键盘路线含 IME 打开时的滚动
边界裁切。即使独立视觉评审确认了范围，原始发现也不会删除。不宣称所有边界
均通过。日历旧断言期待“You're going”，当前为“Going (demo)”；这种文案
不匹配与最终版本已修复的滚动偏移缺陷分别记录。最终 21 步日历测试保留三项
视口边缘裁切发现，所有行为断言均通过。

六张导出概览卡片均以 968 像素宽、`settled:true` 渲染：邮件／日历高 509，
新闻 587，财经 589，照片／YouTube 573。[渲染证据](evidence/glances/report.json)
绑定准确卡片和数据哈希。这里只证明渲染，不证明导出卡片交互或 44 点触控目标。
尤其是邮件次要 Archive 和日历 Details 操作，没有独立的 44 点输入证据。

## 精选原始截图

| 类别 | 导出概览 | 展开／原生交互 | 完整应用分支 |
| --- | --- | --- | --- |
| 邮件 | [概览](evidence/glances/mail.png) | [Android 键盘及可达 Send](evidence/mail-keyboard-final-suite/03-send-reachable-with-keyboard-android.png) | [收件箱](evidence/mail-release-suite/02-full-app.png) |
| 日历 | [概览](evidence/glances/calendar.png) | [展开](evidence/calendar-scroll-fixed-suite/01-expanded.png) | [已修复的最后事件详情](evidence/calendar-scroll-fixed-suite/12-last-event-detail.png) |
| 新闻 | [概览](evidence/glances/news.png) | [展开](evidence/news-release-suite/01-expanded.png) | [集合](evidence/news-release-suite/02-full-app.png) |
| 财经 | [概览](evidence/glances/finance.png) | [展开](evidence/finance-release-suite/01-expanded.png) | [最后证券详情](evidence/finance-release-suite/04-last-item-detail.png) |
| 照片 | [概览](evidence/glances/photo.png) | [展开](evidence/photo-release-suite/01-expanded.png) | [最后项目详情](evidence/photo-release-suite/04-last-item-detail.png) |
| YouTube | [概览](evidence/glances/youtube.png) | [展开](evidence/youtube-release-suite/01-expanded.png) | [最后项目详情](evidence/youtube-release-suite/04-last-item-detail.png) |

PNG 均为未修改的原始文件，应用截图旁附完整原生快照。邮件键盘图是真实的
Android 整屏截图，其他应用纹理不包含键盘。原始报告中提及的其他操作截图
有意未导入，以保持归档精简；最终精选不超过 18 张。

## 源码、限制和评审状态

`card-templates/` 包含六类模型原文件及共享
[`DESIGN.md`](card-templates/DESIGN.md)。[最终来源记录](source-receipt.json)、
[十轮生成记录](generation-record.json)及
[独立作者来源重放](model-authorship-validation.json)将 25 个文件绑定到成功
记录的 Android 模型修改；便携工具也确认全部字节匹配，未做归一化。这证明
文件可从记录复现，不证明历史上绝无任何未记录干预。保留的
[第 9 轮来源记录](revisions/deepseek-round9/source-receipt.json)单独记录修复前版本。

日历模型修复在视图切换时通过 `stage.on_render` 重建 `ScrollYView` 子树，
详情仍位于新建滚动子树中，没有使用虚构的脚本滚动复位 API。独立最终套件在
滚动后打开最后一个事件，确认标题／日期／地点从顶部完整可见，并验证更改其
RSVP 后第一个事件仍为 Maybe。更新的报告取代模型早期验证检查点，无需修改
`DESIGN.md`。

其余五类的 `main.splash` 哈希，与完整行为测试时保存的源码一致。之后的
manifest 删除了未使用的存储能力；独立 release 套件验证了空能力集合的本地
准入。绑定关系见证据摘要。状态仅在内存中：保存、关注、RSVP 和回复排队
都是本次会话的本地演示，不是持久记录或外部操作。不会同步邮件／日历、获取
实时价格、加载照片或播放视频；照片和 YouTube 明确标注媒体不可用。

未签名 Studio 开发者准入与 App Hub `hub check`、商店扫描、发布者签名及
发布不同，这些检查在此未运行。manifest 完整性占位值不是真实摘要证明。
[最终独立视觉评审](visual-review.json)给集合 **4.1/5**，低于 **4.5/5 的 A−
目标**。评分针对渲染组件，组件分数不包含明确的画廊测试外壳；整屏间距和
画廊控件仍属于可用性限制。较高的列表行、突出的主要概览按钮及不可用媒体
使其仍为原型集合。[冻结邮件对比](../COMPARISON.zh-CN.md)保留为历史证据，
不是通用模型排名。

## 复现检查

[reproduce.py](../reproduce.py)驱动原生点击／文本／滚动、禁止可用按钮断言，
并将 `behavior_pass` 与几何和综合结果区分。默认把小于 44 逻辑点的可用按钮
计为失败；`--allow-small-targets` 仅用于早期对比分数。
[render-glances.py](../render-glances.py)将模型卡片和数据原字节复制到独立测试
包的新临时目录，并调用 Android 上的 OctoSense AppStudio 渲染器。
从本 `collection/` 目录执行以下命令。第一条仅校验参数；去掉 `--dry-run`
才会实际渲染。

```sh
python3 ../render-glances.py --runtime-root /path/to/OctoSense \
  --serial DEVICE_SERIAL --package dev.makepad.octosense.studio \
  --workspace /data/user/0/dev.makepad.octosense.studio/files/TRUSTED_WORKSPACE \
  --output /path/to/new-glance-evidence \
  --families mail calendar news finance photo youtube --dry-run
```

使用已解锁且获授权的测试设备、现有开发者授权、准确归档源码及新输出目录。
工具不安装或发布。参数化工具也已在真实 Android 测试设备执行：`reproduce.py` 驱动最终日历
21 步回归（21 项行为通过、18 项原始通过；退出码 1 保留三项裁切发现），
`render-glances.py` 成功渲染六类卡片。工具哈希见[证据摘要](evidence/summary.json)。

将归档源码放入受信任的测试工作区后，从本 `collection/` 目录用明确的操作
参数复跑原生套件：

```sh
python3 ../reproduce.py --runtime-root /path/to/OctoSense \
  --serial DEVICE_SERIAL --package dev.makepad.octosense.studio \
  --workspace /data/user/0/dev.makepad.octosense.studio/files/TRUSTED_WORKSPACE \
  --suite evidence/calendar-scroll-fixed-suite/suite.json \
  --output /path/to/new-calendar-evidence
```

无需手机或供应商即可执行
`python3 ../validate-model-authorship.py --case-dir collection`，严格重放 25 个
最终文件；缺失／多余文件、歧义编辑或不支持的补丁会拒绝通过。本地运行时／
构建／APK 详情单独记录在[运行时来源](runtime-provenance.json)。独立的
[已安装 APK 读回校验](installed-builds-verified.json)确认两个测试包均匹配干净
构建记录及已发布的 [OctoSense 运行时提交](https://github.com/OctoSense-org/OctoSense/commit/ccf8013f2bd7adbb6c20d5f52f47bcfbcbb55313)。
[清理记录](final-cleanup.json)确认临时供应商配置和开发者授权已移除、测试包
已停止、屏幕超时已恢复；生产 Home 和 ROM 未修改。
