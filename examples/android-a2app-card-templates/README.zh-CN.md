# Android 模型编写的应用卡片原型

[English](README.md) | 简体中文

[六类集合](collection/README.zh-CN.md)包含 Android 上 DeepSeek 编写并修订的
邮件、日历、新闻、财经、照片和 YouTube 原型。每类都有声明式概览卡片，以及
含概览、展开和完整应用展示的 Splash 应用。25 个最终文件逐字节保留，严格
重放与记录中的 Android 模型修改完全匹配。

**这是经过评审的原型，不是已验收模板集。** 独立视觉评审给集合 **4.1/5**，
低于 **4.5/5 的 A− 目标**。原生测试验证了本地操作、选择和导航；照片与
YouTube 展示诚实的媒体不可用状态，不是实际照片加载或视频播放。状态仅在
本次会话内存中，不连接实时服务。

用户要求手机模型编写设计、源码和修订。监督代理提供参考、反馈、操作工具
及证据，不手动修改应用源码。L0／L1／L2 表示展示深度，不是语言准入等级
或权限授权。

## 查看集合

| 类别 | 导出概览 | 原生行为证据 |
| --- | --- | --- |
| 邮件 | [截图](collection/evidence/glances/mail.png) | 归档／撤销、邮件身份、键盘下可达的本地演示 Send |
| 日历 | [截图](collection/evidence/glances/calendar.png) | RSVP 状态独立，最后一行详情导航已修复 |
| 新闻 | [截图](collection/evidence/glances/news.png) | 保存／取消保存、选中文章及已存集合 |
| 财经 | [截图](collection/evidence/glances/finance.png) | 关注／取消关注、证券身份及最后一行详情 |
| 照片 | [截图](collection/evidence/glances/photo.png) | 本地已存项目及元数据详情；图片不可用 |
| YouTube | [截图](collection/evidence/glances/youtube.png) | 稍后观看状态及元数据详情；播放不可用 |

[集合源码、结果和复现说明](collection/README.zh-CN.md)区分行为断言、原始
几何发现、直接视觉评审及仅渲染的概览证据，并包含真实 Android 键盘整屏图。
不笼统宣称导出概览都满足 44 点触控目标。

[源码来源](collection/source-receipt.json)、
[作者来源重放](collection/model-authorship-validation.json)、
[参考资料哈希](reference-index.json)及[归档哈希清单](artifact-inventory.json)
关联了证据。保留成功的模型写入／编辑，不包含供应商配置、凭据或私有推理。
本地 Studio 开发者准入与未运行的 App Hub／商店检查、发布者签名及发布不同。

## 早期邮件对比

冻结的 [DeepSeek 第 3 轮与 MiniMax 最终第 3 轮对比](COMPARISON.zh-CN.md)
仍是独立历史证据。两份未完成产物分别为 3.4/5 和 3.3/5；工具可用性、对话
历史及反馈不同，不能当作通用模型排名或等预算基准。

| 冻结尝试 | 源码来源 | 代表性原始截图 |
| --- | --- | --- |
| DeepSeek 第 3 轮 | [记录](attempts/deepseek-r3/source-receipt.json) | [详情发件人错误](attempts/deepseek-r3/evidence/deepseek-mail-r3-no-keyboard-suite/10-second-message-detail.png) |
| MiniMax 最终第 3 轮 | [记录](attempts/minimax-r3/source-receipt.json) | [完整应用限制](attempts/minimax-r3/evidence/minimax-mail-r3-suite/06-full-app.png) |

[对比重放](model-authorship-validation.json)匹配十个归档文件。无需手机即可用
`python3 validate-model-authorship.py` 复跑；
`python3 validate-model-authorship.py --case-dir collection` 检查最终集合的
25 个文件。能够从记录修改中复现，不证明历史上绝无任何未记录干预。原始
manifest 完整性占位值保持不变，作者来源不等于签名证明。

后续尝试使用[评审表](REVIEW-TEMPLATE.zh-CN.md)。保留失败证据，将应用源码
修正交回手机模型，并明确未运行的检查。
