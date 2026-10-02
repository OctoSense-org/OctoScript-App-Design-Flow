# Host services

A contained app cannot open a socket to a mail server, hold a password or talk
to a device. When it needs that, it asks the shell: a **host service** does
the work in Rust, with what it holds, and hands back data, never the means.

Sources: `crates/appstore/src/services.rs` in
[OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub),
`widgets/src/splash_host.rs` and `splash_policy.rs` in OctoSense-org/makepad,
and the Mail service in
[OctoSense `apps/mail/host-service`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/mail/host-service).

## The services that exist

| Family | Service (source) | Who may call it | Shells that register it |
| --- | --- | --- | --- |
| `mail` | Mail ([`apps/mail/host-service`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/mail/host-service)) | Any app granted `mail` | OctoSense desktop (`desktop/`) and Home (`phone/`) |
| `llm` | AI providers ([`apps/ai-providers/host-service`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/ai-providers/host-service)) | Only `os.*` system apps (the AI providers app); it refuses store apps even when granted `llm` (`llm is for OctoSense's own apps.`). It manages the assistant's providers; it has no prompt method | OctoSense desktop (`desktop/`) and Home (`phone/`) |
| `news` | News's data service ([`apps/news/host-service`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/news/host-service)) | Only `os.*` system apps (`The news service serves system apps only.`) | OctoSense desktop and Home |
| `glance` | The glance screen ([`crates/shell/src/glance.rs`](https://github.com/OctoSense-org/OctoSense/blob/main/crates/shell/src/glance.rs)) | Any contained app granted `glance` (OctoSense [#86](https://github.com/OctoSense-org/OctoSense/pull/86)), and native modules ([AI-SERVICES](AI-SERVICES.md#publishing-to-the-glance-screen)) | OctoSense desktop and Home |
| `model` | One-shot model calls, `model.complete` ([`apps/ai-providers/host-service/src/complete`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/ai-providers/host-service/src/complete), OctoSense [#95](https://github.com/OctoSense-org/OctoSense/pull/95)) | Any app granted `model`, within a per-app budget ([AI-SERVICES](AI-SERVICES.md#one-shot-model-calls-model)) | OctoSense desktop and Home |
| `calendar` | Calendar's events and its glance cards ([`apps/calendar/host-service`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/calendar/host-service), OctoSense [#267](https://github.com/OctoSense-org/OctoSense/pull/267)) | Only Calendar (`os.calendar`), and in practice only its agent's tools: App Hub has no `calendar` capability, so no app can be granted it, and the shell runs a system app's own namespace without a grant ([AI-SERVICES](AI-SERVICES.md#what-an-apps-agent-gets-today)) | OctoSense desktop (Calendar is not packed on the phone) |
| `octos` | The assistant for contained apps ([`crates/ai-host/src/contained.rs`](https://github.com/OctoSense-org/OctoSense/blob/main/crates/ai-host/src/contained.rs), OctoSense [#106](https://github.com/OctoSense-org/OctoSense/pull/106), [#184](https://github.com/OctoSense-org/OctoSense/pull/184)) | Any app granted the `octos.*` name it calls, once the person allows its agent (asked at first use). Rinx's mini-app host also serves them, to bundles imported into Rinx | OctoSense desktop and Home, where the shell hosts a kernel (not iOS) |

`card-host` registers none of these. The device's assistant and what an app
can and cannot do with it: [AI-SERVICES](AI-SERVICES.md). A store app that needs something else needs a
new service in the shells (below), not a workaround in the bundle.

## Calling a service from an app

```splash
host.request("mail.accounts", {}, fn(r){
    if r.is_ok && r.data.len() > 0 {
        ui.address.set_text(r.data[0].address)
    } else {
        ui.note.set_text(r.error)
    }
})
```

- The service name is `<family>.<method>`. The family is a capability: the
  app's manifest must grant it (`"capabilities": ["mail"]`), or the isolate
  refuses the call before anything is queued: the callback runs at once with
  `r.is_ok` false and `r.error` = `this app was not granted "mail", which "mail.accounts" needs`
  (verified in `card-host`; the log shows `splash host: refused "mail.accounts": …`).
- `args` is any JSON-able value; it reaches the service as JSON.
- The callback runs later, on the UI thread, with `r.is_ok`, `r.data` (the
  service's JSON answer) and `r.error` (a string, when not ok). Exact shapes
  and refusal texts: [SCRIPT-API](SCRIPT-API.md#host-services-hostrequest).
- No service registered for the family on this shell: the callback gets
  `r.error` = `no service answers "<family>" on this device` rather than
  waiting forever.
- `card-host` registers **no** services (it has no dependency on Mail). A
  Mail-style app run in `card-host` gets that "no service answers" error
  (verified: `no service answers "mail" on this device`); the service is
  linked by the shell (OctoSense `desktop/` and `phone/`).

## The sheet

Some input only the person may give: a password, an account approval. A
service raises a **sheet** for it: a Splash program the shell draws over the
app, in an isolate of its own, under no app's policy. The app cannot open a
sheet; only a service can (`ServiceHost::open_sheet`).

The sheet calls the same `host.request`, and its calls arrive marked
`from_sheet`. The rule, enforced in `services::dispatch` before any service
sees the call:

> A method under `<family>.sheet.` is accepted **only from the sheet**. From
> an app it is refused with `<family>.sheet.<method> is for the host's sheet, not an app`
> (verified in `card-host`: `mail.sheet.submit is for the host's sheet, not an app`).

So a service takes a password only from its own sheet. Each opening starts a
fresh program (a password typed into a cancelled sign-in does not survive).

## Secrets are the host's

An app never collects a password, a PIN or a one-time code, not even to pass
it on:

- the runtime makes a password field inert in a policed isolate (see
  [SCRIPT-API](SCRIPT-API.md#gotchas));
- the gate refuses a bundle that declares one (`secrets` check in
  [PUBLISHING](PUBLISHING.md#2-the-rules-the-gate-enforces));
- the service that needs a credential asks for it on its sheet and keeps it
  in the platform's secret store (Mail: the keychain on Apple platforms, an
  Android Keystore key on Android), under the host's own directory, outside
  every app's jail (in the OctoSense shells, the owner-only
  `secrets/os.mail/` folder since
  [OctoSense#223](https://github.com/OctoSense-org/OctoSense/pull/223), not under `apps/`).
  An app's agent never reaches it either: the agent works in the app's
  account folder ([AI-SERVICES](AI-SERVICES.md#where-the-agent-works-storage)).

If your app needs an account on some service, it needs a host service for it.
It does not get a login form.

## Mail, the worked example

The `mail` family (capability `mail`) as the Mail system app uses it
(`apps/mail/bundle/main.splash`):

| Method | Args | Answer (`r.data`) |
| --- | --- | --- |
| `mail.accounts` | – | `[{id, address}]` this app may use |
| `mail.add_account` | – | `{id, address}` once the person signs in on the host's sheet |
| `mail.remove_account` | `{account}` | `{}` |
| `mail.folders` | `{account}` | `[{id, name, role}]`, the inbox first |
| `mail.sync` | `{account, folder?}` | `{new, total}` |
| `mail.list` | `{account, folder?, offset?, limit?}` | `{folder, total, messages: [{id, sender, address, subject, preview, time, unread}]}` |
| `mail.message` | `{account, folder?, message}` | `{id, sender, address, subject, body, html, attachments, date, time}` |
| `mail.mark_read` | `{account, folder?, message}` | `{}` |
| `mail.send` | `{account, to, subject, body}` | `{accepted}` |
| `mail.notify` | `{title, body, card_id?, priority?}` (title ≤ 80, body ≤ 600 characters) | `{card_id, replaced, expires_at}` once Mail's fixed notice card is on the glance screen, with a notification. Mail's agent's tool ([OctoSense#267](https://github.com/OctoSense-org/OctoSense/pull/267)); answers `This device shows no glance cards.` where no shell publishes them |
| `mail.sheet.submit` | sign-in fields | sheet only |
| `mail.sheet.cancel` | – | sheet only |

The flow of `mail.add_account`: the app calls it and waits; the service
raises its sign-in sheet; the person types into the sheet; the sheet calls
`mail.sheet.submit`; the service tests the account, stores the password in
the vault and the account (without password) in `<host_dir>/mail/accounts.json`,
closes the sheet (`close_sheet_later`) and answers the app's original request
with `{id, address}`. Each account is granted to the apps that added it.

## Adding a new host service

A new service is a change to a shell, not to an app bundle. It needs, together:

1. **A capability** for its family in `KNOWN_CAPABILITIES`
   (`crates/app-contract/src/manifest.rs`, a reviewed change to the app
   contract), with its privacy line in
   `app-policy/src/listing.rs::privacy_summary` and its permission line in
   `app-hub/src/index.rs::permissions_summary` (a test there fails when a
   capability has no plain-words line). The list is closed on purpose; adding a
   name is a reviewed App Hub change.
2. **The service**, a Rust crate implementing `HostService`
   (`octosense_appstore::services`). A sketch (not compiled here; Mail's
   `lib.rs` is the complete, tested reference):

   ```rust
   use octosense_appstore::services::{HostService, Replier, ServiceCall, ServiceHost};

   struct Weather;
   impl HostService for Weather {
       fn family(&self) -> &'static str { "weather" }
       fn call(&mut self, call: ServiceCall, reply: Replier, host: &mut dyn ServiceHost) {
           match call.method() {
               "today" => reply.send(Ok(serde_json::json!({"temp": 21}))),
               other => reply.send(Err(format!("weather has no method {other:?}"))),
           }
       }
   }
   ```

   `call.app_id` is the calling app's manifest id (scope any state per app);
   `call.host_dir` is a directory only the host can reach (`<app data>/.host`
   in `card-host`, outside every jail); `reply` may be
   moved to a worker thread and `send` later; `host.open_sheet(splash_source)`
   / `host.close_sheet()` raise and drop the sheet (`close_sheet_later(app_id)`
   from a worker). Put anything that takes a secret under `sheet.`.
   `call.may_prompt` is false where no sheet may appear (a home-screen tile,
   an assistant's tool call): answer with a sentence that tells the person to
   open the app, because App Hub refuses the sheet there anyway. A request
   that waits longer than `HostService::timeout` (60 s by default; override it
   for a slow service, and the clock stops while the sheet is up) answers
   `the host service timed out`, and a late `send` is dropped ([App Hub#38](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/38), in
   the OctoSense shells since [OctoSense#243](https://github.com/OctoSense-org/OctoSense/pull/243)). The shells set `call.may_prompt`
   false for glance tiles and for an agent's tool calls since
   [OctoSense#204](https://github.com/OctoSense-org/OctoSense/pull/204) (merged 2026-10-01): Mail's `add_account` and AI providers'
   sheets refuse there, and a cancelled tool call stops waiting. The `model`
   service waits out every attempt on a provider (2 × 120 s + 30 s); the
   other services keep the 60 s default.
   **A service's method can also be an app agent's tool.** A system app's
   `tools.json` tool with `implemented_by: "host-service"` reaches the
   service as a normal `ServiceCall` from that app (`may_prompt: false`), so
   one method serves the app's screen and its agent: Mail's `mail.notify`
   and Calendar's `calendar.*` are written that way
   ([AI-SERVICES](AI-SERVICES.md#the-apps-tools-and-peer-tools)).
3. **Registration in the shell**: `register_host_service(Box::new(Weather))`
   at startup, where the shell's Card runner pumps `services::pump`. Mail's
   crate exposes `octosense_mail_service::register()`.
4. **Tests** in the service crate (Mail's run from a shell workspace that links
   it: in the ROM, `cd home && cargo test -p octosense-mail-service`).

Apps then declare the capability and call `host.request("weather.today", …)`.
