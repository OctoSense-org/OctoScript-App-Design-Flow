# Discover and use host APIs

English | [简体中文](HOST-API-V1.zh-CN.md)

Host API v1 lets an app discover and call the Rust services compiled into its
host, and lets the app's agent call Splash functions that the app declares as
tools. It loads no custom Rust library or JIT code, and it does not expose
every OS API. To run your own Rust code, compile it to WebAssembly and use the
`wasm` capability ([Run your own Rust code](RUST.md)).

App Hub contract 1.6 or later, published on crates.io, defines the
declarations on this page. Each build treats an app that declares them as
follows:

| Build | Host API v1 |
| --- | --- |
| OctoSense `main` (in no release yet) | Implements every API on this page, within the platform limits each section gives. |
| `desktop-v0.1.0-beta.2` | Refuses the app: its contract, 1.5, knows none of the `requires` markers below. For what beta.2 serves, see [Host services](HOST-SERVICES.md). |
| `card-host`, which `tools/octo run` starts | Refuses the app ([Before publishing](#before-publishing)). For an app that requests `runtime` without the markers, it answers `runtime.list` and `runtime.describe`. |

**Unverified:** a physical permission approval, camera capture, the Android
runtime, Linux and Windows device services, consent to the app's agent, and
live-model runs.

For a runnable example, see OctoSense's
[Host API Lab](https://github.com/OctoSense-org/OctoSense/blob/main/tools/fixtures/host-api-lab/README.md),
a development fixture whose README gives the build and run commands. On macOS
it passed these checks: signed installation, an app-owned Splash tool, a real
OS permission-status call (`camera.permission.status`), live UI updates and
permission refusals. It is not a published App Hub app, and it tests neither a
live model nor consent to the app's agent.

## 1. Declare what the app needs

This **manifest fragment** is not a complete manifest:

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

| Field or marker | Meaning |
| --- | --- |
| `host-api-v1` | Enables the `host_api` block and the device-consent policy in [§3](#3-request-device-access-in-the-foreground). The host must implement `app_policy.device_consent@1`. |
| `host_api.required` | The host must implement each method at exactly this ABI major version on this platform, or installation or launch fails. Version 2 does not satisfy version 1. |
| `host_api.optional` | The app installs even if the host lacks these methods; the app must provide a fallback. |
| `script-tools-v1` | Enables `implemented_by: "app"` tools ([§5](#5-implement-a-declared-app-tool)). The host must implement the `app_tools.dispatch@1` runtime ABI. |
| `backend-api-v1` | Enables the `backend` block ([§4](#4-connect-the-apps-backend)). The host must implement `auth.backend.request@1`. |

Markers (the values in `requires`) and ABI versions grant no capability. The
usual rules for identity, capabilities, accounts, network access, signing and
publication still apply. An ABI version describes a method's contract, not an
OctoSense release number.

## 2. Discover before offering an optional feature

With the `runtime` capability, ask whether the host implements a method before
you offer the feature that uses it:

```splash
host.request("runtime.describe", {method: "location.get"}, fn(r){
    if r.is_ok && r.data.supported {
        ui.status.set_text("Location API available; permission still needed")
    } else {
        ui.status.set_text("Enter the location manually")
    }
})
```

`runtime.list` takes `{}` and returns `schema`, `platform`, `methods` and
`runtime_features`. A service method description includes its schemas,
capability, ABI version, platforms and `agent_access` policy. `runtime.describe`
takes `{method: "…"}`; service responses include `implemented`, `supported`,
`configured: null` and `authorization: "checked-on-call"`.

**Available, configured and permitted are separate.** Use the service's account
or status methods to check setup. A discovered API can still refuse a call for
missing configuration, account, app consent or OS permission. Some older
services have no descriptor, so discovery does not list every method a host
serves.

`app_tools.dispatch` is a runtime ABI, not a callable service. Its description
has `kind: "runtime-abi"` and `callable_via_host_request: false`. Use the hook
in [§5](#5-implement-a-declared-app-tool); do not send
`host.request("app_tools.dispatch", …)`.

## 3. Request device access in the foreground

`camera.permission.*`, `microphone.permission.*` and `location.permission.*`
provide `status`, `request` and `revoke`, each with `{}` arguments, on Android
and macOS. These methods require `host-api-v1` and the corresponding capability.

A permission request first asks the person to consent for this app on a native
sheet, then asks the OS for its permission if needed. Consent covers one app
across its accounts. The app cannot approve its own sheet. A request from an
agent or a background card fails with
`<method> is unavailable to agents/background surfaces`. A request still
waiting when the shell goes to the background fails with
`authorization_required`, as does `location.get` until the person grants the
app location access. An agent can
read status, revoke the app's consent and read the location once the app is
authorized, but it cannot approve consent.

A response reports three states separately: `app_policy_granted` (the
manifest grants the capability), `app_consent` (the person consented for this
app) and `os_permission` (the OS grant to the shell). Revoking the app's
consent changes neither the shell's OS grant nor other apps' consent.

In an app that declares `host-api-v1`, the same consent check covers
`CameraPreview`, `sys.request_location`, `sys.gps` and GPS reads by map
widgets. After the shell starts, the host refuses each of these until the app
calls that capability's permission method, which loads the app's saved
consent for it. When the app opens, call `camera.permission.status` before
you start `CameraPreview`, and `location.permission.status` before you read
GPS. `sys.request_location` can prompt, so call it
only in the foreground; background code can use `sys.gps`, which never
prompts, or `location.get` once the app is authorized.

`location.get` currently works only on Android. It returns `latitude`,
`longitude`, `accuracy_m`, `source: "last_known"`, `timestamp: null` and
`freshness: "unknown"`. It does not guarantee a fresh fix or background
location. The permission methods add no capture, picker or calendar API; call
only methods the host registers. On Windows, Linux and iOS, the host does not
advertise these device methods: `status` reports
`os_permission: "unsupported"`, and the other methods fail with
`unsupported_platform`.

## 4. Connect the app's backend

Describe the backend in the manifest's `backend` block. A manifest with that
block must also request `auth`, set `storage.accounts: true` and list
`backend-api-v1` in `requires`. This fragment also declares a `host_api`
block, so it lists `host-api-v1` too:

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

The backend must implement public-client PKCE authorization, token exchange,
an identity endpoint and logout. People register and sign in on the backend's
own website; the app never collects a password. Endpoints share one HTTPS
origin on port 443. Named operations fix the method, path and permitted query
keys. The host supplies app identity and keeps tokens in its vault.

Call `auth.connect` with `{provider: "backend", scopes: ["app.session"]}`.
Then pass the connection it returns to `auth.backend.request`:

```splash
host.request("auth.backend.request", {
    connection: connection,
    operation: "notes.list",
    query: {page: "1"}
}, fn(r){
    // Success: r.data is the backend's JSON result directly.
    // Failure: r.error explains the refusal or service error.
})
```

`body` is optional JSON for declared writes. The app cannot supply an
arbitrary URL, method, Authorization header or another app's connection. A GET
operation may run in the background. A write runs only in the foreground,
after the host shows the exact, unchangeable request on a native sheet and the
person approves it with a physical press; synthetic input cannot approve it.
Cancelling before approval sends nothing; after approval, closing the sheet
cannot undo the request.

The host rechecks the admitted declaration. Changing or removing the
declaration, or withdrawing the app, invalidates access; a rollback does not
revive revoked connections. Installing, updating or removing the app revokes
its backend handles, so the app must call `auth.connect` again after every
update, even one that keeps the declaration. On macOS and Android 9 or later,
the host shows the backend's sign-in page in a web view it owns; device
acceptance is still pending. On Windows and Linux, the host opens the system
browser instead (unverified).

## 5. Implement a declared app tool

List `script-tools-v1` in `requires`, and declare each tool in `tools.json`
with its input and output schemas. A tool's namespace is the last segment of
the app's id, `notebook` for `dev.example.notebook`; it cannot be a reserved
name such as `notes`, which belongs to a native app. This declaration adds one
tool that reads the app's current state:

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

In the app's signed Splash source:

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
// The UI reads and edits current_text in this same VM.
```

`request` contains `args` and host-stamped
`context: {app, account, caller, call_id}`. For asynchronous work,
`mod.app_tools.active(call_id)` checks whether a result is still wanted.
`complete` checks the result against `output_schema`; `fail` returns an error
string. This hook is Splash code; a purely declarative L0 card cannot define
it.

The host checks the caller and its permissions, then runs the hook on the UI
thread, in the VM of the full app that owns the tool, so the hook shares the
UI's state and the app's storage jail. Only the full app owns its tools: a
Glance card does not, and the host refuses a second owner. A call while the
app is closed answers `app_not_running`; the host never starts the app to
answer it.

A call runs within these limits:

| Limit | Value |
| --- | --- |
| Input and result | 1 MiB each |
| Pending calls | 16 per app, 128 per process |
| Time | 60 seconds per call |
| VM | The app's instruction and memory limits |

Closing the app, switching accounts or cancelling the call discards the reply,
but cancelling cannot undo a host request the hook already sent. A tool call
cannot show a consent sheet. For a tool with consequences, keep the default
`confirm: "host"`; this ABI refuses `confirm: "app"`.
`implemented_by: "host-service"` tools still call their Rust service.

## Before publishing

`card-host` implements none of the runtime APIs that these markers require, so
`tools/octo run` cannot run an app whose `requires` lists `host-api-v1`,
`backend-api-v1` or `script-tools-v1`. `run` still prints `admitted` and
`ready: first frame drawn`, but the window shows a refusal instead of the app,
and `/snap` lists its labels. For an app that requires only `script-tools-v1`:

```text
card-host refused this bundle
app dev.example.notebook needs a host implementing
app_tools.dispatch@1
```

The reason names the API the host lacks; for `host-api-v1` it is
`app_policy.device_consent@1`. If `host_api.required` lists a method the host
lacks, the reason is
`this host does not implement required APIs: <method>@<version>` instead.
Test such an app this way:

1. Check the final signed bundle with `hub` built from App Hub `main`:
   `hub check <bundle> --publisher-key <publisher-id>=<hex public key>`
   prints a line that ends in `— PASSED`.
2. Install it from a local mirror in an OctoSense desktop shell built from
   `main`, as [PUBLISHING §4](PUBLISHING.md#4-rehearse-the-store-path-locally)
   shows.
3. Exercise discovery and the fallback for a missing API, account changes,
   permission denial and revocation, a tool call while the app is closed, and
   the native review of a backend write.
4. In `listing.json`, list only the platforms you tested.

See [ADR 0012](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0012-app-host-api-discovery.md),
[the script tool implementation](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/crates/appstore/src/script_tools.rs),
[OAuth services](https://github.com/OctoSense-org/OctoSense/blob/main/crates/oauth-service/README.md)
and [device consent](https://github.com/OctoSense-org/OctoSense/blob/main/crates/shell/src/platform_services/README.md).
