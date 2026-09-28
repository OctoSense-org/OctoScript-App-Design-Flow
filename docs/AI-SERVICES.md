# AI in your app: OctoSense's assistant

English | [简体中文](AI-SERVICES.zh-CN.md)

How a script app built here can use the assistant inside OctoSense (the octos
agent kernel the shell runs), what works today, and what is planned. State as
of 2026-09-27: App Hub `main` `e8601b8`, OctoSense `main` `405139f` (which
pins App Hub `46d67e51` and octos `a6ea8505`).

> **Building an app needs no AI.** Nothing in this repository calls a model
> or needs an API key, and you may use any coding agent (Codex, Claude Code,
> Cursor, Gemini CLI, GitHub Copilot, …) or none. This page is only about the
> assistant your *finished app* may ask for on the device.

The deep version, for shell and native-module developers:
[OctoSense `docs/ai-services.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.md).

## Contents

- [The short answer](#the-short-answer)
- [How the assistant is built](#how-the-assistant-is-built)
- [The assistant capabilities](#the-assistant-capabilities)
- [A minimal call, and handling "unavailable"](#a-minimal-call-and-handling-unavailable)
- [What the person sees](#what-the-person-sees)
- [Errors](#errors)
- [Test it](#test-it)
- [Coming: one-shot model calls (`model`)](#coming-one-shot-model-calls-model)
- [Not available yet, and the planned route](#not-available-yet-and-the-planned-route)

## The short answer

**Today a store app cannot ask a model or the assistant anything on an
OctoSense device.** No OctoSense shell serves assistant requests to contained
apps, and `card-host` serves no host services at all. Build your app so it is
complete without AI.

| You try | What happens today |
| --- | --- |
| Declare `octos.turn.start` (and friends) and call it | The gate accepts the name. The call answers `no service answers "octos" on this device`, in `card-host` and in the OctoSense shells alike (verified in `card-host`, below). |
| Declare `model` and call `model.complete` | The gate accepts it (App Hub [#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24), merged): a one-shot model call is **coming**. The OctoSense `model` service is not written yet, so the call answers `no service answers "model" on this device` (verified in `card-host`). See [Coming: one-shot model calls](#coming-one-shot-model-calls-model). |
| Declare `llm` | The gate accepts it, but the `llm` service manages the device's AI providers (it has no prompt method) and answers only `os.*` system apps: `llm is for OctoSense's own apps.` Do not request it. |
| Declare an `agent` in `manifest.json` | Admitted and clamped by the gate; **nothing runs it**. |
| Ship `tools.json`, `AGENT.md`, `skills/` | Admitted by App Hub `main`; **no shell loads them yet**, and the shells' older App Hub refuses a manifest with the new `agent` fields (see [below](#not-available-yet-and-the-planned-route)). |
| Put a provider API key in the bundle | Never. No keys, tokens or passwords in an app ([AGENTS.md](../AGENTS.md#rules-for-every-app)). |

A plain HTTPS API your app declares under `net` is just a web request, even
if a model runs behind it. The usual rules hold: no key or token in the
bundle, the host is listed, and your privacy text says what leaves the
device. It is not the device's assistant and uses none of the person's AI
providers.

## How the assistant is built

- **One octos kernel per shell.** The OctoSense desktop and Home (the phone
  shell) each run one kernel, started on first use. Android bundles it,
  OpenHarmony runs it in process, a desktop runs the binary named by
  `OCTOS_APP_CORE_BIN`, iOS has none.
- **AI providers** (a system app) is where the person picks models and types
  keys, on host-owned sheets. Keys stay in the platform's secret store; no
  app ever sees one.
- **App peers.** An app the host grants the assistant gets its own octos peer:
  private conversation contexts, workspace and memory
  (`app/<app>/acct-<hash>`), owned by the shell's system agent. The app gets a
  scoped service, never the kernel, a provider or a key.
- **Approvals are the person's, in the app that asked.** The system agent
  never approves for an app.

Today only **native modules** the shell trusts get a peer (Rinx, the Matrix
client). Script apps get one in the plan below.

## The assistant capabilities

Four exact names, each its own consent (`KNOWN_CAPABILITIES`,
`crates/app-policy/src/services.rs` in App Hub). A prefix grants nothing:
`octos.` or `octos.admin` is refused by the gate.

| Capability | Call | Args | Answer (`r.data`) | The store says |
| --- | --- | --- | --- | --- |
| `octos.session.open` | `octos.session.open` | `{}` | `{open: true, model: {lane, provider, model} or nil}` | Open its own conversation with the assistant |
| `octos.session.history` | `octos.session.history` | `{}` | the conversation, `{session_id, messages: [...], …}` | Read its own conversations with the assistant |
| `octos.turn.start` | `octos.turn.start` | `{text}` (1 byte to 32 KiB) | `{turn_id, text}`, the reply, once the turn ends | Ask the assistant to work for it, using the device's AI settings |
| `octos.turn.interrupt` | `octos.turn.interrupt` | `{}` | stops the running turn | Stop assistant work it started |

The argument and answer shapes are those of the one host that serves these
names today, Rinx's mini-app host (`src/host/octos.rs` in
[hagency-org/Rinx](https://github.com/hagency-org/Rinx), over OctoSense's
`crates/app-peers`). Other arguments are refused (`Unsupported Octos
arguments`): an app supplies text, never a session, profile, provider, model
or approval decision. One turn runs at a time per app instance, and a turn
gives up after 180 s.

## A minimal call, and handling "unavailable"

`manifest.json` (only what a screen uses):

```json
"capabilities": ["octos.session.open", "octos.turn.start"]
```

`main.splash`:

```splash
fn ask(){
    ui.answer.set_text("Waiting for the assistant…")
    host.request("octos.session.open", {}, fn(s){
        if !s.is_ok {
            ui.answer.set_text("Assistant unavailable: " + s.error)
            return
        }
        host.request("octos.turn.start", {text: ui.prompt.text()}, fn(r){
            if r.is_ok { ui.answer.set_text(r.data.text) }
            else { ui.answer.set_text("Assistant unavailable: " + r.error) }
        })
    })
}
```

with `prompt := TextInput{…}`, `answer := Label{…}` and
`Button{text: "Ask the assistant" on_click: || ask()}` in the body.

- `host.has("octos.turn.start")` says whether the capability was **granted**,
  not whether any service answers it. Always handle `r.is_ok == false`.
- Treat "unavailable" as a normal state: no kernel on this device (iOS, a
  desktop without one), no provider configured, not granted, signed out.
  Show it in a sentence and keep every other screen working.
- Never ask the person for a key or a provider. The host's AI providers app
  owns that.

Verified on 2026-09-27 with `tools/octo run … --hidden` (App Hub `362d832`,
runtime `65d30a09`), clicking the button over the remote bridge:

| Manifest | The label read |
| --- | --- |
| `["octos.session.open", "octos.turn.start"]` | `Assistant unavailable: no service answers "octos" on this device` |
| `["storage"]` | `Assistant unavailable: this app was not granted "octos", which "octos.session.open" needs` |

The OctoSense shells run the same App Hub dispatch and register no `octos`
service either (they register `mail`, `llm`, `news` and `glance`), so a store
app hears the same `no service answers` there.

**Should you ship this today?** Only if the app is complete without it. A
reviewer asks about grants nothing on screen needs (`hub scan`), and every
`octos.*` line appears on the store's permission list. If you keep the call,
say in your listing and your report that it does nothing on today's devices.

## What the person sees

- **Before install**, one permission line per capability (the table above),
  and in the privacy summary: "Asks the device's assistant to work for it;
  the assistant's keys stay with the device." (with `octos.turn.start`), or
  "Opens or reads its own conversations with the device's assistant, but
  cannot ask it to work." (open or history only).
- **Keys and providers** only in AI providers, on host sheets: Start →
  Settings → AI providers on the desktop, OctoSense Settings → Accounts → AI
  providers on a phone.
- **Tool approvals** the assistant raises go to the person, in the app that
  asked, on the host's own controls (today that host is Rinx); the system
  agent never answers them. A script app cannot approve anything: no
  argument carries a decision.

## Errors

| `r.error` | Meaning | What your app does |
| --- | --- | --- |
| `this app was not granted "octos", which "<service>" needs` | The manifest does not list that exact name | Add it to `capabilities`, or remove the call |
| `no service answers "octos" on this device` | This host does not serve the assistant to apps (today: every OctoSense shell and `card-host`) | Show "unavailable" and carry on |
| `no service answers "model" on this device` | No `model` service on this host (today: every OctoSense shell and `card-host`) | The same |
| `Unsupported Octos arguments` | An argument other than `text` (turn start) or anything at all (the others) | Send only `{text}` or `{}` |
| `Provide text (at most 32 KiB)` | Empty or oversized prompt | Check before sending |
| `This app already has an assistant turn running` | One turn at a time | Disable the button while waiting, or interrupt first |
| `No assistant turn is running` | `octos.turn.interrupt` with nothing running | Nothing to do |
| Anything else (no provider configured, the provider failed, quota, signed out, revoked) | The host's text, passed through | Show it; never retry in a loop |

There is no per-app quota API. Budgets are the host's (planned, below).

## Test it

- **In the harness:** `tools/octo run <bundle> --hidden --port 8141`, drive
  the button over the remote bridge, read the label with `/snap`. Expect the
  `no service answers` state; screenshot it as your app's "unavailable"
  state.
- **In the OctoSense desktop:** rehearse the store path
  ([PUBLISHING §4](PUBLISHING.md#4-rehearse-the-store-path-locally)). To give
  the shell a kernel and a provider, see OctoSense
  [`docs/ai-services.md` § Run and test locally](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.md#run-and-test-locally);
  your app still hears `no service answers "octos"` there today.
- **The one host that answers today** is Rinx's mini-app host, for bundles a
  person imports into Rinx after review (a Matrix sign-in, Rinx's own
  assistant peer): [Rinx `examples/miniapps`](https://github.com/hagency-org/Rinx/tree/main/examples/miniapps).
  It is not the App Hub install path, and it refuses a bundle that declares
  an `agent`. Not re-run for this page.

## Coming: one-shot model calls (`model`)

App Hub `main` admits a second, narrower path
([App-Hub#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24),
merged): the `model` capability, for the shell's `model` host service. As
App Hub describes it (the OctoSense service is a pull request still to come,
so none of this runs yet):

- `host.request("model.complete", {task, input, schema, class}, fn(r){…})`,
  with `class` `fast` or `strong`. The host picks the model from the
  person's own AI providers; the app never sees the provider, model id or
  key.
- One shot: no tools, no memory, no history beyond `input`. The reply must
  validate against the app's JSON Schema (size-capped); URLs in the reply
  are refused unless the app asks for them. A per-app daily rate and token
  budget, kept by the host.
- The store says "Send what you give it to the AI provider you configured,
  within a daily budget"; the privacy summary says "Sends what you give it to
  the AI provider you configured, for one-off answers within a daily budget;
  it never sees your API keys."

Today the gate passes it (`grants: capabilities {"model"}`) and every call
answers `no service answers "model" on this device` (run in `card-host` at
App Hub `e8601b8`). The shells' pinned App Hub (`46d67e51`) does not know the
name, so today's shells refuse a manifest that requests it. The exact answer
shape and error texts come with the OctoSense service; do not rely on more
than the fields above until then.

## Not available yet, and the planned route

| Not available | Planned route | Status |
| --- | --- | --- |
| Assistant requests from a contained app in OctoSense | The shell gives the app a peer and serves it, as it does for native modules | Planned: OctoSense [ADR 0002](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0002-event-driven-app-agents.md) (Proposed), first for News ([#61](https://github.com/OctoSense-org/OctoSense/issues/61)) |
| Direct kernel access, choosing a provider or model | Never: the app states model **requirements** (`agent.model`: needs, tier, `local_only`), the host picks from the person's providers | Admitted by App Hub ([App-Hub#18](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/18)); not run |
| The app's own agent and tools | `tools.json` (typed tools named `<app>.<tool>`, `risk` read/act/destructive, `confirm` host/app), `AGENT.md`, data-only `skills/`, `background` and `triggers` in the manifest, admitted and pinned by App Hub | App Hub `main` checks them ([PUBLISHING § The app's agent and tools](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-apps-agent-and-tools)). The kernel side ([octos#2567](https://github.com/octos-org/octos/pull/2567)) is open, and no shell registers or runs them. |
| A one-shot model call | `model.complete` with the `model` capability | Capability merged in App Hub ([#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24)); the OctoSense service is still to come |
| Cards on the glance screen | `glance.publish` with the `glance` capability | The service is merged in OctoSense ([#72](https://github.com/OctoSense-org/OctoSense/pull/72)) but serves only `os.*` apps; the capability is on App Hub `main` ([App-Hub#22](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/22)) and the shell side is in progress ([#86](https://github.com/OctoSense-org/OctoSense/pull/86)) |

**Version skew to know about.** `tools/octo check` runs the App Hub checkout
beside this repository (`main`). The OctoSense shells still pin App Hub
`46d67e51`, which predates the `glance`, `news` and `model` capabilities and the new
`agent` fields (`model`, `background`, `triggers`, `instructions`, `skills`).
Manifests refuse unknown fields, so a bundle that uses any of them passes
`octo check` but is refused by today's shells. Leave them out of a bundle you
want to open in OctoSense now. Whether the shells' older App Hub admits a
bundle that carries `tools.json`, `AGENT.md` or `skills/` was not tested, and
nothing would use them there.

If you want to prepare, draft `tools.json` and `AGENT.md` outside `bundle/`,
from App Hub's News example
([`crates/app-policy/tests/fixtures/news-agent`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/crates/app-policy/tests/fixtures/news-agent)).
