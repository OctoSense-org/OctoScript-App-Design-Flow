# API Migration Lab

[English](README.md) | 简体中文

用于[迁移指南](../../docs/SUBMISSION-API-MIGRATIONS.zh-CN.md)的小型开发示例。
编辑笔记，手写或请求摘要，保存，然后发布/撤回固定身份的 Glance 卡片。
服务失败不会丢弃本地草稿。

`model.complete` 使用 `task`、`input`、有界 JSON Schema 和 `r.data.output`。
Glance 使用准入包中的 `brief.splash` 模板、`initial`，发布和撤回都用 `card_id`。
manifest 仅声明 `storage`、`model`、`glance`；示例没有应用代理，不编造聊天页或登录表单。

## 运行与验证

在 App Flow 根目录执行，预先构建 `hub` 与 `card-host`：

```sh
tools/octo doctor
tools/octo run examples/api-migration-lab/bundle --hidden --detach --port 8197
tools/octo shot 8197 /tmp/api-migration-lab.png
curl -s http://127.0.0.1:8197/quit
tools/octo check examples/api-migration-lab/bundle
```

自动原生输入与重启验证（替换构建产物路径；输出目录必须不存在）：

```sh
python3 examples/api-migration-lab/verify-native.py \
  --card-host /path/to/card-host --hub /path/to/hub \
  --output /tmp/api-migration-lab-evidence
```

驱动程序复制应用包到隔离目录，在隐藏原生窗口中输入中英多行文本，测试空输入、
保存、真实服务缺失、进程重启；记录二进制/源码/驱动哈希、真实截图、控件快照和日志。
只停止自己启动的进程，失败也写 `result.json`。不调用模型，不读取日常应用资料。

## 证据与限制

macOS 原生行为检查已通过：启动内容、空输入拒绝、编辑、保存、两种服务错误和
精确重启恢复；缓存 `card-host` 的身份见 [validation.json](validation.json)。
提交的[截图](bundle/screenshots/01-main.png)是实际重启后捕获，关闭系统字体后已目视检查。
该旧宿主更早的截图存在重绘不完整帧，不作为视觉验收证据。
本记录不声明长时间 UX 测试或性能评分。

`card-host` 真实返回没有 `model`、`glance` 服务。成功推理、实际 Glance 发布/撤回、
摘要展开、公开发行与手机平台均**未验证**，应在配置好的兼容 OctoSense shell 中另测。
这是未签名示例，不是 App Hub 上架申请，也不隐含人的发布或视觉批准。
