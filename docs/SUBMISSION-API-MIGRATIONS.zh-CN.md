# 将已提交应用迁移到当前宿主 API

[English](SUBMISSION-API-MIGRATIONS.md) | 简体中文

能力名称合法，不代表具体方法已实现；闸门通过，也不代表服务调用成功。
本指南修正提交中实际存在的契约差异，不修改参赛者仓库，也不复制其界面。
示例是维护中的开发夹具，不是替代原作品的新上架应用。

先运行 [API Migration Lab](../examples/api-migration-lab/README.zh-CN.md)，
验证本地编辑与服务不可用状态；再运行
[Script Tool State](../examples/script-tool-state/README.zh-CN.md)，
验证应用工具与界面共用持久化状态。数据均为虚构，不需要账号或模型密钥。

## 1. 同时修正授权、请求与结果

Qianxian 提交的 [manifest](https://github.com/kkkkikun/qianxian-guardian/blob/9c7c32291a3a2fdfaed2c34152040cd1239d1834/app/qianxian/bundle/manifest.json)
仅请求 `storage`、`octos.turn.start`，但其
[模型请求](https://github.com/kkkkikun/qianxian-guardian/blob/9c7c32291a3a2fdfaed2c34152040cd1239d1834/app/qianxian/bundle/main.splash#L1537)
以 `prompt` 和普通字段表调用 `model.complete`。如果保留此功能，应声明
`model`，发送 `task`、`input` 和 JSON Schema，并读取 `r.data.output`：

```splash
host.request("model.complete", {
    task: "Summarize the note in one short sentence."
    input: {note: note}
    schema: {type: "object"
        properties: {summary: {type: "string" maxLength: 160}}
        required: ["summary"] additionalProperties: false}
    class: "fast"
}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) return }
    ui.summary.set_text(r.data.output.summary)
})
```

[可运行实现](../examples/api-migration-lab/bundle/main.splash)还保存本地修改，
并在服务拒绝后保留草稿。不能读取提供商专用的 `content` 或 `choices`。
`model` 与 `octos` 是不同能力，允许应用助手运行不会自动授权直接模型调用。
`octos.turn.start({text})` 本身有效，不强制先调用 `session.open`。
不要在应用里增加模型密钥输入框或把令牌存入应用存储。
预算、错误和结果限制见[模型服务](AI-SERVICES.zh-CN.md#模型服务)。

## 2. 使用稳定卡片身份与真实呈现内容

Qianxian 的 `level/title/body`、OctoStudio 的
[`glance.publish({data: ...})`](https://github.com/aios-pub/OctoStudio/blob/bc58cb3/bundle/main.splash#L1508)
都没有提供可呈现的程序。声明 `glance`，提供 `card_id`、`title`，并只选一种：

| 呈现方式 | 请求字段 | 宿主执行内容 |
| --- | --- | --- |
| 已准入模板 | `template: "brief.splash", initial: {summary: ...}` | 当前应用包根目录的 `.splash` 文件，加上宿主绑定的初始数据 |
| L0 源码 | `source: card_source, data: {}` | 经检查的 `.card` 语言，不是 Splash |
| 应用直接提供脚本 | `script: splash_source` | 应用编写的 Splash；代理工具不能提供此字段 |

Lab 采用模板：

```splash
host.request("glance.publish", {
    card_id: "brief" title: "My reviewed brief" summary: summary
    template: "brief.splash" initial: {summary: summary}
    notify: false expires: 3600
}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) return }
    card_id = r.data.card_id
})
host.request("glance.withdraw", {card_id: card_id}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) }
})
```

OctoStudio 还需把返回值 `id` 和撤回参数 `{id}` 改为 `card_id`。
相同 ID 替换同一卡片；不同邮件或新闻应使用不同 ID，同一摘要更新不应制造重复项。
可选的 `open.app` 必须是发布应用自己的 ID。

L0 使用 `source: card_source` 和 `data`，参考
[宿主契约](AI-SERVICES.md#glancepublish-glancewithdraw-glancelist)，
并用选定的 L0 运行时检查真实源码。`level: "L0"` 不会把任意 JSON 转换成卡片。
代理发布模板使用 `template` 与 `initial`，不能混入 `script`、`source`、`data`；
不要在代理工具的输入 schema 中暴露可执行 Splash。

## 3. 将旧回调迁移到当前应用工具 ABI

DailyFlow 提交的[处理器](https://github.com/KumaYuriPool/DailyFlow/blob/dfb69ea9130fd5c0b2778ebf647ea900a7537713/bundle/main.splash#L871)
仍使用旧回调。通用执行器已经存在，应同时更新以下内容：

| 旧写法 | 当前契约 |
| --- | --- |
| 缺少运行时要求 | manifest 加入 `requires: ["script-tools-v1"]` |
| `on_agent_tool(token, name, args_json)` | `app_tool(name, call_id)` |
| 解析回调传入的 JSON 字符串 | `mod.app_tools.request(call_id).args` |
| `mod.app_tools.resolve` / `reject` | `mod.app_tools.complete` / `fail` |

[状态示例](../examples/script-tool-state/bundle/main.splash)让编辑器和工具调用同一更新函数，
先持久化，再 `complete`，返回精确保存的主题与修订号。不另建脚本 VM、聊天会话或文档副本。
工具声称“已更新”不算证据，应检查返回状态与编辑器实际内容。

`request.context` 中的应用、账号、调用者、调用 ID 由宿主填写，不能用
`request.args` 中的身份替代。异步任务完成前可用 `mod.app_tools.active(call_id)`
确认请求仍有效。宿主校验输入、输出 schema。应用关闭时返回 `app_not_running`；
此 ABI 不会自动启动应用，也不等于通用后台任务服务。

## 4. 给助手声明真正的偏好工具

TrendyHear 最新 [v0.4.4 源码](https://github.com/shaokaiyuan0513-dotcom/TrendyHear/tree/25d25960baee624d6360a4b8f48b8c0cd599e49a/bundle)
有偏好流程，但没有 `tools.json`。现在缺少的不是 `implemented_by: "app"`
执行能力，而是应用接入：

1. 声明 `requires: ["script-tools-v1"]`，如实填写 `agent`。
2. 添加 `tools.json`，指定 `implemented_by: "app"`、有界输入输出 schema、真实风险和私有数据属性。
3. 在完整应用中实现 `app_tool`，复用已有偏好存储。
4. 指导助手先读取保存值，仅按明确要求修改，并引用返回状态，不假定成功。

可参考示例 [manifest](../examples/script-tool-state/bundle/manifest.json)、
[工具声明](../examples/script-tool-state/bundle/tools.json)、
[代理指导](../examples/script-tool-state/bundle/AGENT.md)。改用实际应用命名空间：
`skystream.trendyhear` 对应 `trendyhear.*`，不要保留 `toolstate.*`。
声明工具意味着提供助手，用户仍须同意运行。原生验收调用者有意绕过模型与 peer
分发，因此结果不证明代理授权流程或模型推理。

## 5. 在正确宿主上验证

- `card-host` 可验证本地 UI、存储与真实服务不可用响应，不提供模型和 Glance 服务。
- `card-host` 拒绝 `script-tools-v1`，不能删掉标记后宣称代理工具通过。
  状态示例使用 README 中的原生验收程序，验证签名准入和实际 ABI 调用。
- 成功的模型请求、Glance 发布、代理同意和 peer 路由仍需兼容 shell。
  检查具体发行版与平台，最新源码不等于用户已经安装更新。
- **待完成：** 第三方通用 Mail 草稿/审阅/发送、原生日历写入和公共 Matrix 路由
  是独立的宿主任务。示例不调用它们，也不声称文档解决了这些缺口。
  `auth`/`gmail`/`gcalendar` 是另一组连接器，不是 `mail.*`、`calendar.*` 的别名。

保留失败记录。原生像素、本地文件、准入通过、外部真实操作分别证明不同事实，
应明确记录已发生的检查，其余标为未验证。
