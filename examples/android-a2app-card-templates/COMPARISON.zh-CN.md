# Android 邮件模板对比：证据草稿

[English](COMPARISON.md) | 简体中文

**已冻结对比：DeepSeek 第 3 轮与 MiniMax 最终第 3 轮。两者都不是已验收模板，
本文不宣布优胜者。** MiniMax 第三轮已完成；正在进行的 DeepSeek 第 4 轮修复
不纳入本次对比。
日历、新闻、财经、照片和 YouTube 不在本次邮件测试结果范围内。

冻结的[来源记录](comparison-provenance.json)包含收集时间、源码／参考资料哈希、
构建信息和工具计数。归档包括精选的原始截图、原生测试报告及成功的模型源码
修改记录。来源记录中的原始操作路径是证据标识，不意味着所有原文件均在仓库
中。参数化评审工具见[复现说明](README.zh-CN.md#复现)。未导入供应商配置或
私有推理。

## 运行时与复制字节

两份本地构建记录都来自干净的 OctoSense 提交
`ccf8013f2bd7adbb6c20d5f52f47bcfbcbb55313`，版本 `2026100306`，采用
standalone 模式、开发签名并启用 dev mode。框架提交为
`2cc5ef37d7d6a3d2992673389ce74488f7bb2d87`，对应 Makepad
`c155f61d0e1600d2ec474209374444a38a09a470` 和 Octoscript
`5991dfae9344589e732b2605b530f788e8bbcd11`。构建记录还包含 Makepad 补丁栈，
不能只用上游提交描述完整构建。共用的预构建内核哈希为
`4bcfa4f5c60f7e8cad526b49481d40bf0556ce4853aad9c72f853ad866ded1e6`。

| 测试包 | 本地 APK SHA-256 |
| --- | --- |
| DeepSeek：`dev.makepad.octosense.studio` | `d1dbebdf602f01ee427d68109c500e607b7a5c50fc3f387d5a7c46a1f7b4f882` |
| MiniMax：`dev.makepad.octosense.studio.minimax` | `219a81645c60d315f1d7638e1efa15ab5ff4aa88f06fe0495edf44dbf4c2f34b` |

重新计算的两份 APK 哈希均与构建记录一致；后续独立的
[已安装 APK 读回校验](collection/installed-builds-verified.json)也确认两个测试包
与对应记录相符。构建记录未覆盖的功能开关仍为未验证。

[`attempts/minimax-r3/`](attempts/minimax-r3/source-receipt.json) 和 [`attempts/deepseek-r3/`](attempts/deepseek-r3/source-receipt.json) 各有五个模型文件，
其字节长度及 SHA-256 均与原始 `source-receipt.json` 一致。[独立重放结果](model-authorship-validation.json)及
[便携重放工具](validate-model-authorship.py)的复跑确认十个文件均逐字节匹配：
从该文件最后一次成功的 Android 模型写入开始，应用后续唯一精确匹配的编辑，
再比较 UTF-8 字节。较早补丁已被后续写入覆盖；未猜测补丁、模糊编辑或格式
归一化。这证明冻结字节可以从记录中的模型参数复现，不证明历史上绝无任何
未记录干预。
`reference-index.json` 的 11 项均与现有本地源码匹配，涵盖框架、构造器目录、
设计系统、邮件／日历／新闻／财经／YouTube 卡片、照片源码和脚本 API 文档。

## 原生测试

| 保存的测试套件 | 通过步骤／尝试步骤 | 工具调用 | 证据支持的结论 |
| --- | --- | --- | --- |
| MiniMax 邮件最终第 3 轮 | 原始断言 7 / 10 | 20 | 已读切换、归档／撤销及第二封邮件身份正确；一个失败来自归档文案变化。完整应用的撰写区主题标签仍裁切，发送控件仍不可达。 |
| DeepSeek 邮件第 3 轮，键盘路线 | 3 / 16 | 10 | 概览、展开及空白发送校验通过；输入后界面裁切，后续目标不可用。后续失败是连锁结果，不是独立复现的 12 个缺陷。 |
| DeepSeek 邮件第 3 轮，无键盘路线 | 11 / 12 | 26 | 归档／撤销及文件夹筛选可用；第二封邮件主题正确，但发件人错误、正文仍为通用内容。原生输入目标包含 40 点高按钮和仅部分可见的 18 点高矩形。 |

MiniMax 归档断言期待“Nothing selected”，实际文案已改为“Message archived”；
收件箱数量变化和撤销证明归档操作有效。保留原始失败记录，但不能将其算作
功能退步。

生成条件也不同。DeepSeek 第一轮因开发者授权的规范工作区路径不匹配，无法
使用 Studio 工具；MiniMax 第一轮即可使用。DeepSeek 延续了此前 Task Planner／
邮件对话，MiniMax 使用新对话。两者各有三轮提示，但反馈、写入、修订及工具
调用次数不同。这不是等预算、等上下文的对比。

三套操作序列和测试数据不同，不能用通过百分比直接比较模型能力。MiniMax
套件没有文本输入步骤，不能据此认定是输入触发了键盘缺陷。所有截图均保留
`settled:false`。几何检查和输入结果不能代替视觉评审；这些套件都不足以证明
达到 A−，也没有完整验证持久化及错误状态。

## 生成计数与耗时

操作者标注的模型为 DeepSeek V4 Flash 和 MiniMax M3.1 Flash Preview。
脱敏记录未独立提供供应商返回的模型 ID，本工具不读取供应商配置。

| 已完成轮次 | 工具调用数 | 成功／失败 | 已记录耗时（秒） |
| --- | --- | --- | --- |
| DeepSeek 初稿 | 20 | 19 / 1 | 未记录 |
| DeepSeek 评审 | 25 | 25 / 0 | 未记录 |
| DeepSeek 修订 | 29 | 29 / 0 | 未记录 |
| MiniMax 初稿 | 57 | 52 / 5 | 618.869 |
| MiniMax 评审 | 35 | 30 / 5 | 380.260 |
| MiniMax 最终评审 | 45 | 43 / 2 | 263.388 |

另一次 DeepSeek 后台尝试记录了轮次错误，工具调用为零。耗时来自操作者轮询
循环，不是供应商推理耗时，不能据此计算模型速度或 token 成本。上述已完成
轮次中，DeepSeek 的八次、MiniMax 的六次 `view_image` 完成记录明确标为
`reported_shown_to_model`；这证明工具报告图片已交付，不能证明模型发现了
所有问题。

MiniMax 最终轮次使用了 45 次工具调用，超过要求的 24 次，并承认发送控件仍有
阻碍。这与有效修复一起记录，不能从对比中省略。

## 准入与验收

两份保存的源码版本都通过了 **Studio 本地开发者准入**，唯一能力为 `storage`，
返回 `publisher_signed:false` 和 `source_modified:false`。MiniMax 最终第 3 轮
bundle 摘要为
`22d5350a9afcf20bc2c17bb5391e5af0dcb0dec8bc62be598035a30fecaf401f`；
DeepSeek 第 3 轮为
`9281aaec32391be5a274a3ba54764ebf528f653e7d4f3464f41a618c52d90f67`。
这些是 BLAKE3 bundle 摘要，与逐文件 SHA-256 不同。两份原始 manifest 都保留
了 64 个零的完整性占位值，模型参数和导入字节完全一致。占位值的作者来源
重放匹配，不代表真实 bundle 完整性或发布者签名有效；上述实际本地准入摘要
来自 Studio 另外暂存的副本。

本地准入不代表 App Hub `hub check`、目录／商店扫描、发布者签名、商店批准
或发布完成，本文均未验证这些项目。已知失败尝试应保留为评审证据，不能作为
已验收复用模板导入。设计和源码修正必须继续由手机模型完成。

## 独立产物评分

独立评审只评价这两份未完成的邮件产物，不代表模型的通用能力。以下维度来自
评审者针对本次产物的尺度，与空白复用评审表的维度不同。

| 产物 | 视觉 | 展示深度 | 交互 | A2App 参考应用 | 验证诚实度 | 总分／5 |
| --- | --- | --- | --- | --- | --- | --- |
| DeepSeek 第 3 轮 | 3.5 | 3.5 | 3.0 | 3.5 | 3.5 | **3.4** |
| MiniMax 最终第 3 轮 | 3.5 | 3.0 | 3.5 | 2.5 | 4.0 | **3.3** |

两者都未达到 4.5/5 的 A− 目标。两份未完成产物相差 0.1 分，不能作为通用模型
排名，也不代表已经选定优胜者。[评分记录](independent-review.json)保留范围和
评审归属。
