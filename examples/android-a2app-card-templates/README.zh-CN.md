# Android 模型编写的应用卡片原型

[English](README.md) | 简体中文

DeepSeek 和 MiniMax 各自在 Android 上编写了邮件、日历、新闻、财经、照片
和 YouTube 六类集合。每类都有声明式概览卡片，以及含概览、展开、完整应用
视图的原生 Splash 应用。当前快照逐字节保留 **五十个模型文件**，附源码重放、
原始设备截图和原生交互记录。

另一评审代理给每份 **离线原型整体 4.5/5、视觉 4.4/5**。整体达到 A− 目标，
单独视觉仍低于该目标。这是产物编辑评审，不是人工／商店批准或通用模型
排名。本地状态演示不真正发送邮件、获取实时价格、加载照片或播放视频。

## 当前集合

| 模型快照 | 源码与证据 | 整体／视觉 |
| --- | --- | --- |
| DeepSeek 第 12 轮 | [六类原型、原生结果和截图](continuations/deepseek/turn-12/README.zh-CN.md) | 4.5／4.4 |
| MiniMax 第 14 轮 | [六类原型、原生结果和截图](continuations/minimax/turn-14/README.zh-CN.md) | 4.5／4.4 |

[后续评审](continuations/REVIEW.zh-CN.md)将各次原始失败与修正后的操作补测
分开，并说明不同上下文、反馈、中断和轮数；这不是等预算基准。MiniMax
整个展示界面为 4.3，组件表面为 4.4，分别记录。

这里 L0 是简短概览，L1 是带本地操作的展开视图，L2 是应用列表／详情。
展示深度不提升语言等级或权限；声明式 `.card` 与原生 `.splash` 仍是不同
路径。[参考清单](reference-index.json)记录 A2App 源材料。导出卡片渲染验证
像素，不证明 shell 发布或触控目标大小。

## 作者来源与复现

用户要求 Android 模型编写设计、源码和修订。操作人员提供参考、反馈、测试
工具和来源记录，没有手改应用。每个快照都有准确源码清单、成功模型修改
历史和重放报告。模型设计文档保留原来的检查点，较新的操作报告说明实际验证。

从本目录无需手机即可检查两份当前源码历史：

```sh
python3 validate-model-authorship.py \
  --case-dir continuations/deepseek/turn-12 \
  --case-dir continuations/minimax/turn-14
```

各集合说明如何用 [reproduce.py](reproduce.py) 复跑原生测试。
[render-glances.py](render-glances.py) 渲染原字节卡片／数据；
[流程](continuations/README.zh-CN.md)说明不可覆盖导入及
[已验证补丁语义](pinned-apply-patch-semantics.json)。[哈希清单](artifact-inventory.json)
覆盖归档产物。重放证明可从记录修改复现，不代表发布者签名或绝无未记录
干预；未运行 App Hub／商店检查。

[当前清理记录](continuations/cleanup.json)记录临时供应商／授权文件移除、
测试包停止及屏幕超时恢复。归档不含供应商配置、凭据、设备序列号或私有推理。

## 保留的早期阶段

[前三轮邮件对比](COMPARISON.zh-CN.md)保持冻结：当时未完成的 DeepSeek 第 3 轮
和 MiniMax 第 3 轮产物分别为 3.4 和 3.3。
[DeepSeek 十轮集合](collection/README.zh-CN.md)保留原来 4.1 的分数和证据，
不会把历史结果改称当前集合。后续可用[评审表](REVIEW-TEMPLATE.zh-CN.md)，
应用修复交回手机模型，未执行检查明确保留。
