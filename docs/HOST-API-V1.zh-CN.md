# 发现并使用宿主 API

[English](HOST-API-V1.md) | 简体中文

未注明中文版的链接指向英文文档。

应用可以调用编译进宿主的 Rust 服务，也可以通过脚本工具 ABI 调用自己声明的 Splash 函数。Host API v1 不加载自定义的 Rust 库、Wasm 或 JIT 代码，也不开放所有系统 API。

本页的各项声明由 App Hub 契约 1.6.0 定义，该版本已发布到 crates.io。各个构建如何对待声明了这些内容的应用：

| 构建 | Host API v1 |
| --- | --- |
| OctoSense `main`（尚未进入任何发布版本） | 实现本页的全部 API，平台限制见各节。 |
| OctoSense 桌面版 0.1.0-beta.2 | 拒绝该应用：它的契约是 1.5，不认识这些标记。beta.2 提供哪些服务，见[宿主服务](HOST-SERVICES.zh-CN.md)。 |
| `tools/octo run` 启动的 `card-host` | 拒绝该应用（见[发布前](#发布前)）。应用申请了 `runtime` 但没有声明这些标记时，它会响应 `runtime.list` 和 `runtime.describe`。 |

**未验证**：亲手点按批准权限、相机拍摄、Android 运行时、Linux 和 Windows 上的设备服务、对应用 Agent 的授权，以及真实模型运行。

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
| `host-api-v1` | 启用 `host_api` 要求和新的设备授权策略；要求 `app_policy.device_consent@1`。 |
| `host_api.required` | 当前平台必须以完全相同的 ABI 主版本提供其中每一项，否则安装或启动失败。版本 2 不满足版本 1。 |
| `host_api.optional` | 缺少其中的条目时仍可安装；应用必须提供降级方案。 |
| `script-tools-v1` | 要求 `app_tools.dispatch@1` 运行时 ABI，用于执行 `implemented_by: "app"` 的工具。 |
| `backend-api-v1` | 启用签名的后端注册，并要求 `auth.backend.request@1`。 |

标记和 ABI 版本不授予任何能力。应用身份、能力、账户、网络、签名和发布方面的要求照旧有效。ABI 版本描述的是方法的契约，不是 OctoSense 的发布版本号。

## 2. 提供可选功能前先查询

申请了 `runtime` 能力后：

```splash
host.request("runtime.describe", {method: "location.get"}, fn(r){
    if r.is_ok && r.data.supported {
        ui.status.set_text("Location API available; permission still needed")
    } else {
        ui.status.set_text("Enter the location manually")
    }
})
```

`runtime.list` 接收 `{}`，返回 `schema`、`platform`、`methods` 和 `runtime_features`。服务方法的描述包含 schema、能力、ABI 版本、平台和 `agent_access` 策略。`runtime.describe` 接收 `{method: "…"}`；对服务方法，响应包含 `implemented`、`supported`、`configured: null` 和 `authorization: "checked-on-call"`。

**可用、已配置和已授权是三回事。** 用服务自己的账户或状态方法检查配置。已发现的 API 仍可能因缺少配置、账户、应用授权或系统权限而拒绝调用。部分旧服务没有描述，发现结果不是全部历史方法的完整列表。

`app_tools.dispatch` 是运行时 ABI，不是可以调用的服务。它的描述带有 `kind: "runtime-abi"` 和 `callable_via_host_request: false`。请使用第 5 节的钩子，不要发送 `host.request("app_tools.dispatch", ...)`。

## 3. 在前台申请设备访问

`camera.permission.*`、`microphone.permission.*` 和 `location.permission.*` 在 Android 和 macOS 上提供 `status`、`request` 和 `revoke`，参数都是 `{}`。这些方法要求 `host-api-v1` 和相应的能力。

申请权限时，宿主先在原生界面上取得用户对本应用的授权，需要时再申请系统权限。授权针对单个应用，覆盖它的所有账户。应用无法替自己批准授权面板。从后台或由 Agent 发起的申请会失败，返回 `authorization_required`：Agent 可以读取状态、撤销应用的授权，也可以读取已获授权的位置，但不能批准授权。响应分别给出 `app_policy_granted`、`app_consent` 和 `os_permission`。撤销应用授权，不会撤销系统授予安装包的权限，也不影响其他应用的授权。

在声明了 `host-api-v1` 的应用中，`CameraPreview`、`sys.request_location`、`sys.gps` 和地图的 GPS 读取同样要通过这道授权关口。应用重启后，这道关口会一直拒绝访问，直到应用调用某个权限方法、加载已保存的授权。请在应用打开时先调用 `<family>.permission.status`，再启动 `CameraPreview` 或读取 GPS。`sys.request_location` 可能弹出提示，所以只在前台调用；后台代码可以用从不弹出提示的 `sys.gps`，或在应用获得授权后用 `location.get`。

`location.get` 目前只支持 Android，返回 `latitude`、`longitude`、`accuracy_m`、`source: "last_known"`、`timestamp: null` 和 `freshness: "unknown"`。它不保证位置是最新的，也不提供后台定位。权限接口并不等于新的拍摄、文件选择或日历 API；只调用宿主实际注册的方法。这个适配器不为 Windows、Linux 或 iOS 声明这些设备方法：在这些平台上，`status` 返回 `os_permission: "unsupported"`，其他方法以 `unsupported_platform` 失败。

## 4. 连接应用自己的后端

在清单中加入 `auth`、`storage.accounts: true`、`backend-api-v1` 和 `host-api-v1`，再加上签名的 `backend` 声明。下面同样是片段：

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

后端实现公共客户端的 PKCE 授权、令牌交换、身份查询和退出登录。注册和登录页面属于后端自己的网站，应用不收集密码。所有端点共用同一个 HTTPS 源，使用 443 端口。具名操作固定了方法、路径和允许的查询键。宿主提供应用身份，并把令牌保存在自己的凭据库中。

调用 `auth.connect`，参数为 `{provider: "backend", scopes: ["app.session"]}`。然后用返回的、属于本应用的连接发起请求：

```splash
host.request("auth.backend.request", {
    connection: connection,
    operation: "notes.list",
    query: {page: "1"}
}, fn(r){
    // 成功时，r.data 直接就是后端返回的 JSON。
    // 失败时，r.error 说明拒绝原因或服务错误。
})
```

`body` 是可选的 JSON，用于已声明的写操作。应用不能自行指定 URL、方法或 Authorization 请求头，也不能使用其他应用的连接。GET 操作可以在后台运行。修改操作必须在前台的原生界面上审阅确切且不可更改的请求，并由用户亲手点按批准；合成输入不能批准。批准之前取消，什么都不会发送；批准之后，关闭界面也撤销不了已经发出的网络操作。

宿主会重新检查已准入的声明。修改或删除声明、撤回应用，都会使访问失效；回滚不会恢复已撤销的连接。安装、更新和卸载通知会撤销现有的后端句柄；即使更新保留了相同的声明，也要重新连接。macOS 和 Android 上已实现嵌入式后端登录，设备验收尚未完成。Windows 和 Linux 保留独立的外部浏览器认证方式；这两个平台不支持嵌入式 `WebReader`，它的 `open` 返回 `false`（[CAPABILITIES § 网络](CAPABILITIES.zh-CN.md#网络)）。Android 上的 Google 登录仍不支持。Google 和 GitHub 还需要宿主中的提供商注册信息；普通用户不需要自己注册开发者客户端。

## 5. 实现声明的应用工具

使用 `script-tools-v1`。在签名的 `tools.json` 中声明工具，包括 JSON 输入和结果 schema。下面这个最小声明返回应用现有 UI VM 中的状态。对清单 ID 为 `dev.example.notebook` 的应用，工具前缀是 ID 的最后一段 `notebook`。`notes` 保留给原生应用，不能用作已安装应用的工具命名空间：

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

`request` 包含 `args` 和宿主填写的 `context: {app, account, caller, call_id}`。处理异步工作时，用 `mod.app_tools.active(call_id)` 检查是否仍需要结果。`complete` 会按 schema 检查结果；`fail` 返回一条错误信息。这个钩子是 Splash 代码，纯声明式的 L0 卡片无法定义它。

工具中继先验证调用方和权限，再把钩子排进 UI 线程上、拥有该工具的完整应用 VM 的队列。Tokio 任务只等待结果，不拥有也不移动 VM。钩子与 UI 共享状态和应用的存储沙箱。Glance 不会成为第二个工具所有者；出现多个所有者时，宿主会拒绝。应用关闭时返回 `app_not_running`，宿主不会在后台悄悄运行它，也不会冷启动它。

每次调用的输入和结果各限 1 MiB，每个应用最多 16 个待处理调用，整个进程最多 128 个，每次最长 60 秒，并受 VM 指令和内存上限约束。关闭应用、切换账户或取消调用都会让回复失效；取消无法撤回已经发出的宿主请求。工具轮次不能弹出授权面板。会产生后果的工具请使用宿主确认；这个 ABI 不实现 `confirm: "app"` 的证明。已有的 `implemented_by: "host-service"` 工具继续调用已注册的 Rust 服务。

## 发布前

`card-host` 不实现这些 API，所以 `tools/octo run` 无法运行 `requires` 中列有 `host-api-v1`、`backend-api-v1` 或 `script-tools-v1` 的应用。`run` 仍会输出 `admitted` 和 `ready: first frame drawn`，但窗口显示的是拒绝信息而不是应用，`/snap` 会列出这些文字：

```text
card-host refused this bundle
app dev.example.notebook needs a host implementing app_tools.dispatch@1
```

拒绝原因会写出宿主缺少的 API；对 `host-api-v1` 来说是 `app_policy.device_consent@1`。请改用以下方式测试这类应用：

1. 用 App Hub `main` 构建的 `hub` 检查最终签名的应用包。
2. 按 [PUBLISHING §4](PUBLISHING.zh-CN.md#4-在本地演练商店流程) 的步骤，从本地镜像把它安装到用 `main` 构建的 OctoSense 桌面端 Shell 中。
3. 逐项测试：API 发现与缺少 API 时的降级、账户切换、拒绝和撤销权限、应用关闭时调用工具，以及后端写操作的原生审阅。
4. 只发布实际测试过的平台。

源码检查和 VM 单元测试不等于通过了设备验收或真实模型验收。

参见 [ADR 0012](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0012-app-host-api-discovery.zh-CN.md)、[脚本工具实现](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/crates/appstore/src/script_tools.rs)、[OAuth 服务](https://github.com/OctoSense-org/OctoSense/blob/main/crates/oauth-service/README.zh-CN.md)和[设备授权](https://github.com/OctoSense-org/OctoSense/blob/main/crates/shell/src/platform_services/README.zh-CN.md)。
