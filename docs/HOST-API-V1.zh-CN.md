# 发现并使用宿主 API

[English](HOST-API-V1.md) | 简体中文

未注明中文版的链接指向英文文档。

Host API v1 让应用发现并调用编译进宿主的 Rust 服务，也让应用的 Agent 调用应用声明为工具的 Splash 函数。它不加载自定义的 Rust 库、Wasm 或 JIT 代码，也不会开放全部系统 API。

本页的各项声明由 App Hub 契约 1.6.0 定义，该版本已发布到 crates.io。声明了这些内容的应用在各个构建中的结果如下：

| 构建 | Host API v1 |
| --- | --- |
| OctoSense `main`（尚未进入任何发布版本） | 实现本页的全部 API，平台限制见各节。 |
| `desktop-v0.1.0-beta.2` | 拒绝该应用：它的契约是 1.5，不认识下文 `requires` 中的任何标记。beta.2 提供哪些服务，见[宿主服务](HOST-SERVICES.zh-CN.md)。 |
| `tools/octo run` 启动的 `card-host` | 拒绝该应用（见[发布前](#发布前)）。应用申请了 `runtime` 但没有声明这些标记时，它会响应 `runtime.list` 和 `runtime.describe`。 |

**未验证**：亲手点按批准权限、相机拍摄、Android 运行时、Linux 和 Windows 上的设备服务、对应用 Agent 的授权，以及真实模型运行。

## 1. 声明应用的要求

下面是**清单片段**，不是完整的清单：

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
| `host-api-v1` | 启用 `host_api` 块和[第 3 节](#3-在前台申请设备访问)的设备授权策略；宿主必须实现 `app_policy.device_consent@1`。 |
| `host_api.required` | 宿主必须在当前平台上以完全相同的 ABI 主版本实现其中每个方法，否则安装或启动失败。版本 2 不满足版本 1。 |
| `host_api.optional` | 宿主缺少其中的方法时，应用仍可安装，但必须提供降级方案。 |
| `script-tools-v1` | 启用 `implemented_by: "app"` 的工具（[第 5 节](#5-实现声明的应用工具)）；宿主必须实现 `app_tools.dispatch@1` 运行时 ABI。 |
| `backend-api-v1` | 启用 `backend` 块（[第 4 节](#4-连接应用自己的后端)）；宿主必须实现 `auth.backend.request@1`。 |

标记（即 `requires` 中的取值）和 ABI 版本不授予任何能力。应用身份、能力、账户、网络访问、签名和发布方面的要求照旧有效。ABI 版本描述的是方法的契约，不是 OctoSense 的发布版本号。

## 2. 提供可选功能前先查询

申请了 `runtime` 能力后，先查询宿主是否实现了某个方法，再提供用到它的功能：

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

**可用、已配置和已授权是三回事。** 用服务自己的账户或状态方法检查配置。已发现的 API 仍可能因缺少配置、账户、应用授权或系统权限而拒绝调用。部分旧服务没有描述，所以发现结果不会列出宿主提供的全部方法。

`app_tools.dispatch` 是运行时 ABI，不是可以调用的服务。它的描述带有 `kind: "runtime-abi"` 和 `callable_via_host_request: false`。请使用[第 5 节](#5-实现声明的应用工具)的钩子，不要发送 `host.request("app_tools.dispatch", …)`。

## 3. 在前台申请设备访问

`camera.permission.*`、`microphone.permission.*` 和 `location.permission.*` 在 Android 和 macOS 上提供 `status`、`request` 和 `revoke`，参数都是 `{}`。这些方法要求 `host-api-v1` 和相应的能力。

申请权限时，宿主先在原生面板上请用户为本应用授权，需要时再向系统申请权限。授权针对单个应用，覆盖它的所有账户。应用无法在授权面板上替用户批准。从后台或由 Agent 发起的申请会失败，返回 `authorization_required`。Agent 可以读取状态、撤销应用的授权，也可以在应用获得授权后读取位置，但不能批准授权。

响应分别报告三种状态：`app_policy_granted`（清单授予了该能力）、`app_consent`（用户已为本应用授权）和 `os_permission`（系统授予 Shell 的权限）。撤销应用的授权，不会撤销系统授予 Shell 的权限，也不影响其他应用的授权。

在声明了 `host-api-v1` 的应用中，`CameraPreview`、`sys.request_location`、`sys.gps` 和地图控件的 GPS 读取同样要通过这道授权关口。Shell 每次启动后，这道关口会一直拒绝访问，直到应用调用某个权限方法；这次调用会加载应用已保存的授权。请在应用打开时先调用 `<family>.permission.status`，再启动 `CameraPreview` 或读取 GPS。`sys.request_location` 可能弹出提示，所以只在前台调用；后台代码可以用从不弹出提示的 `sys.gps`，或在应用获得授权后用 `location.get`。

`location.get` 目前只支持 Android，返回 `latitude`、`longitude`、`accuracy_m`、`source: "last_known"`、`timestamp: null` 和 `freshness: "unknown"`。它不保证位置是最新的，也不提供后台定位。这些权限方法不提供新的拍摄、文件选择或日历 API；只调用宿主注册了的方法。在 Windows、Linux 和 iOS 上，宿主不声明这些设备方法：`status` 返回 `os_permission: "unsupported"`，其他方法以 `unsupported_platform` 失败。

## 4. 连接应用自己的后端

在清单中申请 `auth`，设置 `storage.accounts: true`，在 `requires` 中列出 `backend-api-v1` 和 `host-api-v1`，并在 `backend` 块中描述后端。下面的片段列出了这些字段：

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

后端必须实现公共客户端的 PKCE 授权、令牌交换、身份查询和退出登录。用户在后端自己的网站上注册和登录，应用从不收集密码。所有端点共用同一个 HTTPS 源，使用 443 端口。具名操作固定了方法、路径和允许的查询键。宿主提供应用身份，并把令牌保存在自己的凭据库中。

调用 `auth.connect`，参数为 `{provider: "backend", scopes: ["app.session"]}`。然后把返回的连接传给 `auth.backend.request`：

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

`body` 是可选的 JSON，用于已声明的写操作。应用不能自行指定 URL、方法或 Authorization 请求头，也不能使用其他应用的连接。GET 操作可以在后台运行。写操作只能在前台执行：宿主先在原生面板上展示确切且不可更改的请求，用户亲手点按批准后才会发送；合成输入不能代替批准。批准之前取消，什么都不会发送；批准之后，关闭面板也撤销不了已经发出的请求。

宿主会重新检查已准入的声明。修改或删除声明、撤回应用，都会使访问失效；回滚不会恢复已撤销的连接。应用安装、更新或卸载时，宿主会撤销它的后端句柄，所以每次更新后应用都要重新调用 `auth.connect`，即使更新保留了相同的声明。在 macOS 和 Android 9 及以上版本上，宿主在自己的 WebView 中显示后端的登录页，设备验收尚未完成；在 Windows 和 Linux 上，宿主打开系统浏览器。

## 5. 实现声明的应用工具

在 `requires` 中列出 `script-tools-v1`，并在 `tools.json` 中声明每个工具及其输入和输出 schema。工具的命名空间是应用 id 的最后一段，例如 `dev.example.notebook` 的命名空间是 `notebook`；它不能是 `notes` 这样的保留名，`notes` 属于原生应用。下面的声明添加一个读取应用当前状态的工具：

```json
{
  "schema": 1,
  "tools": [{
    "name": "notebook.current",
    "description": "Read the text currently open in the notebook",
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

`request` 包含 `args` 和宿主填写的 `context: {app, account, caller, call_id}`。处理异步工作时，用 `mod.app_tools.active(call_id)` 检查是否仍需要结果。`complete` 会按 `output_schema` 检查结果；`fail` 返回一条错误信息。这个钩子是 Splash 代码，纯声明式的 L0 卡片无法定义它。

宿主先检查调用方及其权限，再在 UI 线程上运行钩子，运行环境是拥有该工具的完整应用的 VM，因此钩子与 UI 共享状态和应用的存储 jail。工具只属于完整应用：速览卡片不拥有工具，宿主也会拒绝第二个所有者。应用关闭时，调用返回 `app_not_running`，宿主不会为此启动应用。

每次调用都受以下限制：

| 限制 | 值 |
| --- | --- |
| 输入和结果 | 各 1 MiB |
| 待处理调用 | 每个应用 16 个，整个进程 128 个 |
| 时长 | 每次调用 60 秒 |
| VM | 应用的指令和内存上限 |

关闭应用、切换账户或取消调用都会让回复作废，但取消撤回不了钩子已经发出的宿主请求。工具调用中不能弹出授权面板。会产生后果的工具请保留默认的 `confirm: "host"`：这个 ABI 会拒绝 `confirm: "app"`。`implemented_by: "host-service"` 工具仍调用各自的 Rust 服务。

## 发布前

`card-host` 没有实现这三个标记所要求的运行时 API，所以 `tools/octo run` 无法运行 `requires` 中列有 `host-api-v1`、`backend-api-v1` 或 `script-tools-v1` 的应用。`run` 仍会输出 `admitted` 和 `ready: first frame drawn`，但窗口显示的是拒绝信息而不是应用，`/snap` 会列出这些标签。以只要求 `script-tools-v1` 的应用为例：

```text
card-host refused this bundle
app dev.example.notebook needs a host implementing
app_tools.dispatch@1
```

拒绝原因会写出宿主缺少的 API；对 `host-api-v1` 来说是 `app_policy.device_consent@1`。如果 `host_api.required` 列出了宿主缺少的方法，原因则是 `this host does not implement required APIs: <method>@<version>`。请改用以下方式测试这类应用：

1. 用 App Hub `main` 构建的 `hub` 检查最终签名的应用包：`hub check <bundle> --publisher-key <publisher-id>=<hex public key>` 应输出一行以 `— PASSED` 结尾的结果。
2. 按 [PUBLISHING §4](PUBLISHING.zh-CN.md#4-在本地演练商店流程) 的步骤，从本地镜像把它安装到用 `main` 构建的 OctoSense 桌面端 Shell 中。
3. 逐项测试：API 发现与缺少 API 时的降级、账户切换、拒绝和撤销权限、应用关闭时调用工具，以及后端写操作的原生审阅。
4. 在 `listing.json` 中只列出实际测试过的平台。

参见 [ADR 0012](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0012-app-host-api-discovery.zh-CN.md)、[脚本工具实现](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/crates/appstore/src/script_tools.rs)、[OAuth 服务](https://github.com/OctoSense-org/OctoSense/blob/main/crates/oauth-service/README.zh-CN.md)和[设备授权](https://github.com/OctoSense-org/OctoSense/blob/main/crates/shell/src/platform_services/README.zh-CN.md)。
