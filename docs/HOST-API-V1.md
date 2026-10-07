# Discover and use host APIs

English | [简体中文](HOST-API-V1.zh-CN.md)

An app can call Rust services compiled into its host, plus its own declared
Splash functions through the script-tool ABI. Host API v1 does not load custom
Rust libraries, Wasm or JIT code, and it does not expose every OS API.

App Hub contract 1.6.0, published on crates.io, defines the declarations on
this page. What each build does with an app that declares them:

| Build | Host API v1 |
| --- | --- |
| OctoSense `main` (in no release yet) | Implements every API on this page, within the platform limits each section gives. |
| OctoSense desktop 0.1.0-beta.2 | Refuses the app: its contract, 1.5, knows none of the markers. For what beta.2 serves, see [Host services](HOST-SERVICES.md). |
| `card-host`, which `tools/octo run` starts | Refuses the app ([Before publishing](#before-publishing)). For an app that requests `runtime` without the markers, it answers `runtime.list` and `runtime.describe`. |

**Unverified:** a physical permission approval, camera capture, the Android
runtime, Linux and Windows device services, consent to the app's agent, and
live-model runs.

## 1. Declare what the app needs

The following is a **manifest fragment**, not a complete publishable bundle:

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
| `host-api-v1` | Enables `host_api` requirements and the new device-consent policy; requires `app_policy.device_consent@1`. |
| `host_api.required` | Every entry must exist with this exact ABI major on this platform, or installation/launch fails. Version 2 does not satisfy version 1. |
| `host_api.optional` | Missing entries permit installation; the app must provide a fallback. |
| `script-tools-v1` | Requires the `app_tools.dispatch@1` runtime ABI for `implemented_by: "app"` tools. |
| `backend-api-v1` | Enables signed backend registration and requires `auth.backend.request@1`. |

Markers and ABI versions do not grant capabilities. Keep the existing app
identity, capabilities, account, network, signing and publication requirements.
An ABI version describes a method's contract, not an OctoSense release number.

## 2. Discover before offering an optional feature

With the `runtime` capability:

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
services have no descriptor; discovery is not an exhaustive historical list.

`app_tools.dispatch` is a runtime ABI, not a callable service. Its description
has `kind: "runtime-abi"` and `callable_via_host_request: false`. Use the hook in
section 5; do not send `host.request("app_tools.dispatch", ...)`.

## 3. Request device access in the foreground

`camera.permission.*`, `microphone.permission.*` and `location.permission.*`
provide `status`, `request` and `revoke`, each with `{}` arguments, on Android
and macOS. These methods require `host-api-v1` and the corresponding capability.

A permission request first obtains this app's native consent, then the OS grant
if needed. Consent covers one app across its accounts. The app cannot approve
its own sheet. A request from the background or from an agent fails with
`authorization_required`: an agent can read status, revoke the app's consent
and read an authorized location, but cannot approve consent.
Responses distinguish `app_policy_granted`, `app_consent` and `os_permission`.
Revoking app consent does not revoke the OS package's grant or other apps'
consent.

In an app that declares `host-api-v1`, the same consent gate covers
`CameraPreview`, `sys.request_location`, `sys.gps` and the map's GPS reads.
After a restart, the gate refuses access until the app calls a permission
method, which loads its saved consent. Call `<family>.permission.status` when
the app opens, before you start `CameraPreview` or read GPS.
`sys.request_location` can prompt, so call it only in the foreground;
background code can use `sys.gps`, which never prompts, or `location.get`
once the app is authorized.

`location.get` currently works only on Android. It returns `latitude`,
`longitude`, `accuracy_m`, `source: "last_known"`, `timestamp: null` and
`freshness: "unknown"`. It does not guarantee a fresh fix or background location.
A permission API is not a new capture, picker or calendar API; use only methods
actually registered by the host. The adapter does not advertise these device
methods for Windows, Linux or iOS: there `status` reports
`os_permission: "unsupported"`, and the other methods fail with
`unsupported_platform`.

## 4. Connect the app's backend

Add `auth`, `storage.accounts: true`, `backend-api-v1` and `host-api-v1` to the
manifest, plus a signed `backend` declaration. For example, this is a fragment:

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

The backend implements public-client PKCE authorization, token exchange,
identity and logout. Its website owns registration/login; the app does not
collect passwords. Endpoints share one HTTPS origin on port 443. Named
operations fix the method, path and permitted query keys. The host supplies
app identity and keeps tokens in its vault.

Call `auth.connect` with `{provider: "backend", scopes: ["app.session"]}`.
Use the returned app-owned connection with:

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

`body` is optional JSON for declared writes. The app cannot supply an arbitrary
URL, method, Authorization header or another app's connection. GET operations
may run in the background. Mutations require foreground native review of the
exact immutable request and a physical approval; synthetic input cannot approve.
Cancelling before approval sends nothing. Once approved, a network operation
cannot be undone by cancelling the UI.

The host rechecks the admitted declaration. Changing/removing it or withdrawing
the app invalidates access; a rollback does not revive revoked connections.
Installation, update and removal notifications revoke existing backend handles;
even an update that keeps the same declaration requires reconnecting.
Embedded backend login is implemented for macOS/Android, with device acceptance
still pending. Windows/Linux retain a separate external-browser authentication
path; embedded `WebReader` is unsupported there, and its `open` returns `false`
([CAPABILITIES § Network](CAPABILITIES.md#network)). Google Android
sign-in remains unsupported. Google/GitHub also need provider registrations in
the host; ordinary app users do not register a developer client themselves.

## 5. Implement a declared app tool

Use `script-tools-v1`. Declare the tool in signed `tools.json`, including JSON
input/result schemas. This minimal declaration returns state from the app's
existing UI VM. For an app with manifest ID `dev.example.notebook`, the tool
prefix is `notebook`, its final ID segment. `notes` is reserved for a native app
and cannot be an installed app's tool namespace:

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
// The UI reads/edits current_text in this same VM.
```

`request` contains `args` and host-stamped
`context: {app, account, caller, call_id}`. For asynchronous work,
`mod.app_tools.active(call_id)` checks whether a result is still wanted.
`complete` validates the result schema; `fail` returns an error string.
This hook is Splash code; a purely declarative L0 card cannot define it.

The tool relay authenticates callers and permissions, then queues the hook for
the owning full-app VM on the UI thread. Tokio tasks wait for its result; they
do not own or move the VM. The hook shares UI state and the app's storage jail.
Glance creates no second tool owner; multiple owners are rejected. A closed app
returns `app_not_running`, with no hidden background or cold start.

Calls have 1 MiB input/result limits, at most 16 pending per app and 128 per
process, at most 60 seconds, and VM instruction/memory limits. Closing the app,
changing accounts or cancelling invalidates replies; cancellation cannot undo
an already-emitted host request. Tool turns cannot prompt for consent. Use host
confirmation for consequential tools; this ABI does not implement
`confirm: "app"` proof. Existing `implemented_by: "host-service"` tools continue
using their registered Rust service.

## Before publishing

`card-host` implements none of these APIs, so `tools/octo run` cannot run an
app whose `requires` lists `host-api-v1`, `backend-api-v1` or
`script-tools-v1`. `run` still prints `admitted` and
`ready: first frame drawn`, but the window shows a refusal instead of the
app, and `/snap` lists its text:

```text
card-host refused this bundle
app dev.example.notebook needs a host implementing app_tools.dispatch@1
```

The reason names the API the host lacks; for `host-api-v1` it is
`app_policy.device_consent@1`. Test such an app this way instead:

1. Check the final signed bundle with `hub` built from App Hub `main`.
2. Install it from a local mirror in an OctoSense desktop shell built from
   `main`, as [PUBLISHING §4](PUBLISHING.md#4-rehearse-the-store-path-locally)
   shows.
3. Exercise discovery and the fallback for a missing API, account changes,
   permission denial and revocation, a tool call while the app is closed, and
   the native review of a backend write.
4. Publish only the platforms you exercised.

Source checks and VM unit tests are not a device or live-model pass.

See [ADR 0012](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0012-app-host-api-discovery.md),
[the script tool implementation](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/crates/appstore/src/script_tools.rs),
[OAuth services](https://github.com/OctoSense-org/OctoSense/blob/main/crates/oauth-service/README.md)
and [device consent](https://github.com/OctoSense-org/OctoSense/blob/main/crates/shell/src/platform_services/README.md).
