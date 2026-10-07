# 发现并使用宿主 API

[English](HOST-API-V1.md) | 简体中文

**本文是实现指南，不代表已发布宿主已经支持。** 这些改动面向 App Hub 1.6 契约及
配套的 OctoSense、运行器和 Makepad 构建。契约 1.6.0 已发布；兼容宿主发布和手机验收仍待完成。
旧宿主必须拒绝要求这些特性的应用。此前发布版本的行为见[宿主服务](HOST-SERVICES.zh-CN.md)。

应用可调用宿主已编译的 Rust 服务，也可通过脚本工具 ABI 调用自己声明的 Splash
函数。此工作不加载自定义 Rust 动态库、Wasm 或 JIT 代码，也不暴露所有系统 API。

## 1. 声明应用的要求

下面是**清单片段**，不是完整的可发布应用包：

```json
{
  "requires": ["host-api-v1", "script-tools-v1"],
  "capabilities": ["runtime", "storage", "location"],
  "host_api": {
    "required": {"app_tools.dispatch": 1},
    "optional": {"location.get": 1}
  }
}
```

| 字段或标记 | 含义 |
| --- | --- |
| `host-api-v1` | 启用 `host_api` 要求及新的设备授权策略；要求 `app_policy.device_consent@1`。 |
| `host_api.required` | 当前平台必须提供每个条目的精确 ABI 主版本，否则拒绝安装/启动。版本 2 不满足版本 1。 |
| `host_api.optional` | 缺失时仍允许安装；应用必须提供降级路径。 |
| `script-tools-v1` | 要求 `app_tools.dispatch@1` 运行时 ABI，以执行 `implemented_by: "app"` 工具。 |
| `backend-api-v1` | 启用签名后端注册，并要求 `auth.backend.request@1`。 |

标记与 ABI 版本不授予能力。应用身份、能力、账户、网络、签名和发布要求仍然
有效。ABI 版本描述方法契约，不是 OctoSense 的发布版本号。

## 2. 提供可选功能前先查询

获得 `runtime` 能力后：

```splash
host.request("runtime.describe", {method: "location.get"}, fn(r){
    if r.is_ok && r.data.supported {
        ui.status.set_text("位置 API 可用；仍需申请权限")
    } else {
        ui.status.set_text("请手动输入位置")
    }
})
```

`runtime.list` 接收 `{}`，返回 `schema`、`platform`、`methods` 和
`runtime_features`。服务方法描述包含 schema、能力、ABI 版本、平台和
`agent_access` 策略。`runtime.describe` 接收 `{method: "…"}`；服务响应包含
`implemented`、`supported`、`configured: null` 和 `authorization: "checked-on-call"`。

**可用、已配置和已授权是不同状态。** 用具体服务的账户或状态方法检查配置。
发现 API 后，仍可能因为缺少配置、账户、应用授权或系统权限而被拒绝。部分旧
服务没有描述符；发现结果不是全部历史方法的完整清单。

`app_tools.dispatch` 是运行时 ABI，不是可调用服务。它的描述带有
`kind: "runtime-abi"` 和 `callable_via_host_request: false`。请使用第 5 节的
钩子，不要发送 `host.request("app_tools.dispatch", ...)`。

## 3. 在前台申请设备访问

`camera.permission.*`、`microphone.permission.*` 和 `location.permission.*`
在 Android/macOS 提供 `status`、`request`、`revoke`，参数均为 `{}`。
这些方法要求 `host-api-v1` 和相应能力。

申请权限先取得用户在原生界面中对本应用的授权，再按需申请系统权限。应用不能
批准自己的授权页。Agent 可以读取状态，但不能批准授权，也不能把后台请求变成
前台请求。响应区分 `app_policy_granted`、`app_consent` 和 `os_permission`。
撤销应用授权不撤销系统对安装包的授权，也不影响其他应用授权。启用新策略的
应用，其设备控件和 GPS 辅助接口也遵循这套检查。

`location.get` 目前仅支持 Android，返回 `latitude`、`longitude`、`accuracy_m`、
`source: "last_known"`、`timestamp: null`、`freshness: "unknown"`。
不保证新鲜位置，也不提供后台定位。权限接口不等于新的拍摄、文件选择或日历
API；只调用宿主实际注册的方法。此适配器不宣称 Windows、Linux 或 iOS 支持
这些设备方法。

## 4. 连接应用自己的后端

清单添加 `auth`、`storage.accounts: true`、`backend-api-v1` 和 `host-api-v1`，
并提供签名 `backend` 声明。下面仍是片段：

```json
{
  "requires": ["host-api-v1", "backend-api-v1"],
  "capabilities": ["auth"],
  "storage": {"accounts": true},
  "host_api": {"required": {"auth.backend.request": 1}},
  "backend": {
    "id": "notes",
    "client_id": "public-client",
    "authorization_url": "https://backend.example/authorize",
    "token_url": "https://backend.example/token",
    "me_url": "https://backend.example/me",
    "logout_url": "https://backend.example/logout",
    "scopes": ["app.session"],
    "operations": {
      "notes.list": {"method": "GET", "path": "/api/notes", "query_keys": ["page"]},
      "notes.create": {"method": "POST", "path": "/api/notes"}
    }
  }
}
```

后端实现公共客户端 PKCE 授权、令牌交换、身份和退出。注册/登录页面属于后端
网站；应用不收集密码。端点共享同一个 HTTPS 源，使用 443 端口。命名操作固定
方法、路径和允许的查询键。宿主填写应用身份，把令牌保留在凭据库中。

调用 `auth.connect`，参数为 `{provider: "backend", scopes: ["app.session"]}`。
使用返回的本应用连接：

```splash
host.request("auth.backend.request", {
    connection: connection,
    operation: "notes.list",
    query: {page: "1"}
}, fn(r){
    // 成功时，r.data 直接是后端返回的 JSON。
    // 失败时，r.error 说明拒绝原因或服务错误。
})
```

写操作可选用 JSON `body`。应用不能任意指定 URL、方法、Authorization 请求头
或其他应用的连接。GET 可在后台运行。修改操作必须在前台原生界面审阅精确且
不可变的请求，并由用户真实物理输入批准；合成输入不能批准。批准前取消不会
发送请求；批准后已经进行的网络操作不能靠关闭界面撤销。

宿主重新检查已准入声明。声明变更/移除或应用撤回会使访问失效；回滚不会恢复
已撤销的连接。安装、更新与卸载通知会撤销现有后端句柄；即使更新保留相同
声明，也需要重新连接。macOS/Android 实现嵌入式后端登录，设备验收仍待完成。
Windows/Linux 保留独立的外部浏览器认证路径；嵌入式 `WebReader` 不受支持，
必须明确报错。Google Android 登录仍不受支持。Google/GitHub 还需要宿主的提供商
注册信息；普通应用用户不需要自行注册开发者客户端。

## 5. 实现声明的应用工具

使用 `script-tools-v1`。在签名 `tools.json` 中声明工具，包括 JSON 输入/结果
schema。以下最小声明返回当前应用 UI VM 中的状态。假设清单 ID 是
`dev.example.notebook`，工具前缀必须是其最后一段 `notebook`。
`notes` 是原生应用的保留名称，不能用作商店应用的工具命名空间：

```json
{
  "schema": 1,
  "tools": [{
    "name": "notebook.current",
    "description": "Read the text currently open in Notes",
    "implemented_by": "app",
    "risk": "read",
    "input_schema": {"type": "object", "additionalProperties": false},
    "output_schema": {
      "type": "object",
      "properties": {"text": {"type": "string"}},
      "required": ["text"],
      "additionalProperties": false
    }
  }]
}
```

在应用已签名的 Splash 源码中：

```splash
let current_text = "Draft note"
fn app_tool(name, call_id) {
    let request = mod.app_tools.request(call_id)
    if name == "notebook.current" {
        mod.app_tools.complete(call_id, {text: current_text})
    } else {
        mod.app_tools.fail(call_id, "Unknown tool")
    }
}
// UI 在同一个 VM 中读取和编辑 current_text。
```

`request` 包含 `args` 和宿主填写的
`context: {app, account, caller, call_id}`。异步工作可用
`mod.app_tools.active(call_id)` 检查是否仍需要结果。`complete` 检查结果 schema，
`fail` 返回错误字符串。此钩子是 Splash 代码；纯声明式 L0 卡片不能定义它。

工具中继验证调用者和权限，然后把钩子加入 UI 线程中完整应用 VM 的队列。
Tokio 任务等待结果，不拥有或移动 VM。钩子共享 UI 状态和应用存储沙箱。
Glance 不创建第二个工具所有者；多个所有者会被拒绝。关闭的应用返回
`app_not_running`，不会偷偷在后台或冷启动。

输入/结果各限 1 MiB，每个应用最多 16 个待处理调用，进程最多 128 个，最多
60 秒，并受 VM 指令/内存限制。应用关闭、账户切换和取消使回复失效；取消
不能撤销已发出的宿主请求。工具轮次不能弹出授权页。需要确认的工具应使用
宿主确认；此 ABI 不实现 `confirm: "app"` 的证明。既有
`implemented_by: "host-service"` 工具仍调用已注册的 Rust 服务。

## 发布前

用兼容 App Hub 工具检查最终签名包，再在实际支持的 OctoSense 版本上测试：
发现、缺少服务时降级、账户切换、权限拒绝/撤销、应用关闭时调用工具及原生写入
审阅。`card-host` 能渲染应用，并不意味着它拥有 OctoSense 的服务。只发布实际
测试过的平台。源码检查和 VM 单元测试不等于 OnePlus 6 或真实模型验收通过。

参见 [ADR 0012](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0012-app-host-api-discovery.zh-CN.md)、
[脚本工具实现](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/crates/appstore/src/script_tools.rs)、
[OAuth 服务](https://github.com/OctoSense-org/OctoSense/blob/main/crates/oauth-service/README.zh-CN.md)
和[设备授权](https://github.com/OctoSense-org/OctoSense/blob/main/crates/shell/src/platform_services/README.zh-CN.md)。
