# AI in your app: OctoSense's assistant

English | [简体中文](AI-SERVICES.zh-CN.md)

How a script app built here can use the assistant inside OctoSense (the octos
agent kernel the shell runs), what works today, and what is planned. State as
of 2026-09-30: App Hub `main` `0f33211`, OctoSense `main` `7082ff5` (which
pins App Hub `0f332112`). Since this page was first written (2026-09-27) the
shells gained the `model` service, the `octos` service for contained apps
behind first-use consent, `glance` for any app granted it, and an agent (a
peer and an "Ask <app>" panel) for every app that declares one. OctoSense's
[`docs/ai-services.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.md)
and [`docs/architecture.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/architecture.md)
describe the shell side.

The later sections cover what is being built on top: an app's own agent
declared in its bundle, the tools it exposes, the system toolbox, publishing
to the glance screen, `sys.digest` cards, and News end to end. Each feature
there is marked **available** (merged on `main` of the repository named, and
usable as described) or **coming** (in an open pull request, named, or only
in an ADR: the shape shown may change before it lands, so do not build a
submission on it yet). Commands marked **✓ run** were run for this page on
2026-09-27 (macOS, Apple silicon); every other command is quoted from the
named source and marked not run. The 2026-09-30 updates are quoted from the
named pull requests and code, not run.

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
- [One-shot model calls (`model`)](#one-shot-model-calls-model)
- [Status at a glance](#status-at-a-glance)
- [An app's own agent](#an-apps-own-agent)
- [The app's tools and peer tools](#the-apps-tools-and-peer-tools)
- [The system toolbox](#the-system-toolbox)
- [Publishing to the glance screen](#publishing-to-the-glance-screen)
- [Cards bound to findings: `sys.digest`](#cards-bound-to-findings-sysdigest)
- [Card levels and render-and-critique](#card-levels-and-render-and-critique)
- [End to end: News](#end-to-end-news)
- [Testing without a provider](#testing-without-a-provider)
- [Sources](#sources)

## The short answer

**On an OctoSense device a store app can make one-shot model calls
(`model`), and can talk to the assistant (`octos.*`) once the person allows
its agent.** App Hub's `card-host`, which `tools/octo run` uses, serves no
host services at all, so both answer `no service answers "…" on this device`
there. Build your app so it is complete without AI either way: the person may
decline, and a device may have no kernel (iOS) or no provider.

| You try | What happens today |
| --- | --- |
| Declare `octos.turn.start` (and friends) and call it | The gate accepts the name. In `card-host` the call answers `no service answers "octos" on this device` (verified, below). In an OctoSense shell that hosts a kernel, the first call waits for the person to allow the app's agent (`Waiting for the person to allow this app's agent (OctoSense asks the first time)`); after that the app talks to its own peer ([OctoSense#106](https://github.com/OctoSense-org/OctoSense/pull/106), [#120](https://github.com/OctoSense-org/OctoSense/pull/120), [#184](https://github.com/OctoSense-org/OctoSense/pull/184)). |
| Declare `model` and call `model.complete` | The gate accepts it (App Hub [#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24)), and the OctoSense shells serve it ([OctoSense#95](https://github.com/OctoSense-org/OctoSense/pull/95), merged): a one-shot, schema-checked call answered from the person's own AI providers. `card-host` answers `no service answers "model" on this device`. See [One-shot model calls](#one-shot-model-calls-model). |
| Declare `llm` | The gate accepts it, but the `llm` service manages the device's AI providers (it has no prompt method) and answers only `os.*` system apps: `llm is for OctoSense's own apps.` Do not request it. |
| Declare an `agent` in `manifest.json` | Admitted and clamped by the gate. Once the person allows it, the shell gives the app its own peer, and the person can talk to it in the shell's "Ask <app>" panel ([OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)). Model choice from `needs`, triggers and background runs are still **coming** ([An app's own agent](#an-apps-own-agent)). |
| Ship `tools.json`, `AGENT.md`, `skills/` | Admitted by the gate. The shell registers the bundle's tools with the app's peer and relays their calls ([OctoSense#145](https://github.com/OctoSense-org/OctoSense/pull/145), [#184](https://github.com/OctoSense-org/OctoSense/pull/184)); `AGENT.md` and skills are not installed into the peer yet. |
| Call `glance.publish` | Answered for any contained app granted the `glance` capability ([OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)) ([Publishing to the glance screen](#publishing-to-the-glance-screen)). |
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

**Native modules** the shell's host policy grants get a peer (the shipped
policy grants Rinx, the Matrix client: `Policy::shipped()` in OctoSense
`crates/ai-host/src/lib.rs`), and Rinx's mini-app host serves the `octos.*`
names to the mini-apps a person imports into Rinx. A **contained script app**
gets its own peer too (`card.<app id>`), through the shell's `octos` host
service ([OctoSense#106](https://github.com/OctoSense-org/OctoSense/pull/106)), once the person allows its agent at first
use ([#120](https://github.com/OctoSense-org/OctoSense/pull/120), [#184](https://github.com/OctoSense-org/OctoSense/pull/184)). `OCTOSENSE_CONTAINED_APPS=1` skips the
question for every app (a developer override) and `0` turns it off.

## The assistant capabilities

Four exact names, each its own consent (`KNOWN_CAPABILITIES` in App Hub
`crates/app-policy/src/manifest.rs`; the names and their store lines in
`crates/app-policy/src/services.rs`). A prefix grants nothing:
`octos.` or `octos.admin` is refused by the gate.

| Capability | Call | Args | Answer (`r.data`) | The store says |
| --- | --- | --- | --- | --- |
| `octos.session.open` | `octos.session.open` | `{}` | `{open: true, model: {lane, provider, model} or nil}` | Open its own conversation with the assistant |
| `octos.session.history` | `octos.session.history` | `{}` | the conversation, `{session_id, messages: [...], …}` | Read its own conversations with the assistant |
| `octos.turn.start` | `octos.turn.start` | `{text}` (1 byte to 32 KiB) | `{turn_id, text}`, the reply, once the turn ends | Ask the assistant to work for it, using the device's AI settings |
| `octos.turn.interrupt` | `octos.turn.interrupt` | `{}` | stops the running turn | Stop assistant work it started |

The argument and answer shapes are those of the two hosts that serve these
names, both over OctoSense's `crates/app-peers`: the OctoSense shells' `octos`
service for contained apps (`crates/ai-host/src/contained.rs`) and Rinx's
mini-app host (`src/host/octos.rs` in
[hagency-org/Rinx](https://github.com/hagency-org/Rinx)). Other arguments are
refused (`Unsupported Octos arguments`): an app supplies text (in the
OctoSense shells, also `trigger`, one of `person`, `app` or `incoming`, and
`from`, saying what started the turn), never a session, profile, provider,
model or approval decision. One turn runs at a time per app instance, and a turn
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

An OctoSense shell that hosts a kernel answers differently: the first call
asks the person to allow the app's agent, and then the app talks to its own
peer ([OctoSense#106](https://github.com/OctoSense-org/OctoSense/pull/106), [#184](https://github.com/OctoSense-org/OctoSense/pull/184); not run for this page). See
[Errors](#errors) for what each refusal says.

**Should you ship this today?** Only if the app is complete without it: the
person may decline, the device may have no kernel or no provider, and
`tools/octo run` never answers. A reviewer asks about grants nothing on screen
needs (`hub scan`), and every `octos.*` line appears on the store's permission
list.

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
  asked, on the host's own controls (the OctoSense shells' approval sheets,
  [OctoSense#120](https://github.com/OctoSense-org/OctoSense/pull/120) and
  [#145](https://github.com/OctoSense-org/OctoSense/pull/145); Rinx's own for its mini-apps); the system
  agent never answers them. A script app cannot approve anything: no
  argument carries a decision.

## Errors

| `r.error` | Meaning | What your app does |
| --- | --- | --- |
| `this app was not granted "octos", which "<service>" needs` | The manifest does not list that exact name | Add it to `capabilities`, or remove the call |
| `no service answers "octos" on this device` | This host does not serve the assistant to apps (`card-host`, or a shell built without a kernel) | Show "unavailable" and carry on |
| `Waiting for the person to allow this app's agent (OctoSense asks the first time)` | The person has not allowed the app's agent yet; the shell is asking | Show it; the person's answer decides the next call |
| `The assistant is turned off for apps on this device` | The device turned the assistant off for apps (`OCTOSENSE_CONTAINED_APPS=0`) | Show "unavailable" and carry on |
| `The assistant is not available on this device` | The shell could not start the app's peer | The same |
| `no service answers "model" on this device` | No `model` service on this host (`card-host`) | The same |
| `<code>: <sentence>` from `model.complete`, `<code>` one of `capability`, `no_provider`, `rate`, `budget`, `bad_request`, `invalid_output`, `too_large`, `provider` | The `model` service refused the call ([details](#the-model-service)) | Show the sentence; keep the app usable without the model |
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
  [`docs/ai-services.md` § Run and test locally](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.md#run-and-test-locally).
  There your app's first `octos.*` call asks the person to allow its agent.
- **Rinx's mini-app host** also answers `octos.*`, for bundles a person
  imports into Rinx after review (a Matrix sign-in, Rinx's own assistant
  peer): [Rinx `examples/miniapps`](https://github.com/hagency-org/Rinx/tree/main/examples/miniapps).
  It is not the App Hub install path, and it refuses a bundle that declares
  an `agent`. Not re-run for this page.

## One-shot model calls (`model`)

App Hub `main` admits a second, narrower path
([App-Hub#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24),
merged): the `model` capability, served by the OctoSense shells' `model` host
service ([OctoSense#95](https://github.com/OctoSense-org/OctoSense/pull/95), merged 2026-09-28):

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

The gate passes it (`grants: capabilities {"model"}`), and the shells' App
Hub pin knows the name. `card-host` has no `model` service: a call there
answers `no service answers "model" on this device` (run in `card-host` at
App Hub `e8601b8`).

### The `model` service

The service (`apps/ai-providers/host-service/src/complete/`, crate
`octosense-llm-service`, registered by `crates/ai-host` next to `llm`;
[OctoSense#95](https://github.com/OctoSense-org/OctoSense/pull/95)) has this shape. #95 also added ADR 0002 §14, "Direct
one-shot model calls", which keeps an app's own agent (below) the main path
for anything with tools, research, memory or approvals.

| Method | Args | Answer (`r.data`) |
| --- | --- | --- |
| `model.complete` | `{task, input, schema, class?, allow_urls?}` | `{output, meta: {class, requested, attempts, usage: {input_tokens, output_tokens, estimated}, budget}}` |
| `model.budget` | – | the caller's `budget` alone |

- **`task`** (at most 4 KiB) says what to do; **`input`** (any JSON, at most
  32 KiB) is what to do it on, sent as data the model is told not to obey.
- **`class`**: `"fast"` (the default) or `"strong"`. The host tries the
  person's providers in their own order, those of that class first, and
  passes over one that fails. `meta.class` says which class answered. The
  app never sees the provider, the model id or the key.
- **`schema` is required** (a bounded JSON Schema subset, at most 8 KiB);
  `output` always validates against it. A reply that is not JSON, fails the
  schema, carries a URL or is over 16 KiB is retried once, then refused.
- **No URLs by default**: a reply with `http://`, `https://` or `www.` in it
  is refused, because replies end up as card data. Pass `allow_urls: true`
  only when the app extracts links.
- **A per-app budget**, kept by the host outside the app's jail: by default
  6 calls a minute, and 100 calls and 100,000 tokens a UTC day. `meta.budget`
  and `model.budget` report `{calls_today, calls_per_day, tokens_today,
  tokens_per_day, tokens_left, per_minute, resets_at}`.
- **Refusals** are `"<code>: <sentence>"`, with `code` one of `capability`,
  `no_provider`, `rate`, `budget`, `bad_request`, `invalid_output`,
  `too_large` or `provider`. The sentence may be shown to the person.
- The service also checks the app's own manifest for `model`, behind the
  Card runner's gate.

A call (not run for this page; the literal
syntax follows the Photos bundle, space-separated lists and maps):

```splash
host.request("model.complete", {
    task: "Give the note a short title and up to three tags."
    input: {note: note_text}
    schema: {type: "object" required: ["title" "tags"] additionalProperties: false
             properties: {title: {type: "string" maxLength: 40}
                          tags: {type: "array" maxItems: 3 items: {type: "string"}}}}
    class: "fast"
}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) return }   // "budget: …", "no_provider: …"
    show_title(r.data.output.title)
})
```

## Status at a glance

As of 30 Sep 2026. **available** means merged on `main` of the repository
named; **coming** means an open pull request (named) or only an ADR.

| Feature | Status | Pull requests, source |
| --- | --- | --- |
| Apps reach AI only through host services and the app-peer broker, never the kernel, a provider or a key | **available** (the rule) | OctoSense [`AGENTS.md`](https://github.com/OctoSense-org/OctoSense/blob/main/AGENTS.md) rules 3 and 4, [`crates/app-peers`](https://github.com/OctoSense-org/OctoSense/tree/main/crates/app-peers) |
| `octos.*` for native modules the host policy grants (Rinx), and through Rinx's mini-app host for bundles imported into Rinx | **available** | OctoSense `crates/ai-host` (`Policy::shipped()`); [Rinx](https://github.com/hagency-org/Rinx) `src/host/octos.rs` |
| `octos.*` for a contained script app in OctoSense | **available** where the shell hosts a kernel (not iOS), once the person allows the app's agent at first use | OctoSense [#106](https://github.com/OctoSense-org/OctoSense/pull/106), [#120](https://github.com/OctoSense-org/OctoSense/pull/120), [#184](https://github.com/OctoSense-org/OctoSense/pull/184) |
| `llm`: the person's AI providers, masked keys, host sheets | **available**, system apps (`os.*`) only; no prompt method | OctoSense [`apps/ai-providers/host-service`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/ai-providers/host-service) |
| `model.complete`: one-shot, schema-checked model call | **available**: the capability ([App-Hub#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24)) and the service ([OctoSense#95](https://github.com/OctoSense-org/OctoSense/pull/95)), in the shells' App Hub pin | [above](#one-shot-model-calls-model) |
| An app's own agent in the bundle: `agent` (profile, model needs, triggers, skills), `tools.json`, `AGENT.md`, `skills/` | **available** in the App Hub gate ([App-Hub#18](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/18)) and the shells: a peer and the "Ask <app>" panel once the person allows it ([OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)); `AGENT.md` and skills are not installed into the peer yet | [An app's own agent](#an-apps-own-agent) |
| The host picking the model from `needs` and `tier`; triggers and `background` firing | **coming** (ADR 0002 step 2, M3) | [The manifest's `agent`](#the-manifests-agent) |
| App tools registered with the app's peer (`peer/tools/register`, `peer/tool/call`) | **available**: the kernel side ([octos#2567](https://github.com/octos-org/octos/pull/2567)) and the shell registering the bundle's tools and relaying their calls ([OctoSense#145](https://github.com/OctoSense-org/OctoSense/pull/145), [#184](https://github.com/OctoSense-org/OctoSense/pull/184)) | [The app's tools and peer tools](#the-apps-tools-and-peer-tools) |
| In-app conversation with the app's agent, run-time approvals, app memory | Conversation **available** in the shell's "Ask <app>" panel ([OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)); approvals on the shell's sheets ([#120](https://github.com/OctoSense-org/OctoSense/pull/120), [#145](https://github.com/OctoSense-org/OctoSense/pull/145)); app memory **coming** (ADR 0002 §9, M7) | [What is enforced where](#what-is-enforced-where) |
| System toolbox: templates, `workflow.run`, `workflow.fork`, the `research` module | Templates **available** ([OctoSense#82](https://github.com/OctoSense-org/OctoSense/pull/82), `crates/toolbox`) and the `research` and `crawl` capabilities in App Hub ([App-Hub#26](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/26)); granting the toolbox to app agents is **coming** ([OctoSense#64](https://github.com/OctoSense-org/OctoSense/issues/64); the `toolbox-peers` build feature is off in the shipped shells) | [The system toolbox](#the-system-toolbox) |
| `news` host service (a data service, no model) | **available**, system apps (`os.*`) only | OctoSense [`apps/news/host-service`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/news/host-service) |
| `glance.publish`, `glance.withdraw`, `glance.list` (the service) | **available** ([OctoSense#72](https://github.com/OctoSense-org/OctoSense/pull/72)) to any contained app granted `glance` ([OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)) | [Publishing to the glance screen](#publishing-to-the-glance-screen) |
| The `glance` capability | **available** in App Hub ([App-Hub#22](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/22)) and the shells ([OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)) | [Who may publish](#who-may-publish) |
| `sys.digest(app:, id:, fields:)` L0 source | **coming**: [OctoScript#40](https://github.com/OctoSense-org/OctoScript/pull/40), [OctoScript-Makepad#50](https://github.com/OctoSense-org/OctoScript-Makepad/pull/50), [OctoSense#87](https://github.com/OctoSense-org/OctoSense/pull/87) | [Cards bound to findings](#cards-bound-to-findings-sysdigest) |
| Render and critique a card: `card-studio`, `card-host --remote` | **available** (App Hub `main`, [App-Hub#19](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/19)); run by an app's agent **coming** (M6) | [Card levels and render-and-critique](#card-levels-and-render-and-critique) |

In one line: a store app can call `model.complete`, publish glance cards
when granted `glance`, and, once the person allows its agent, talk to the
assistant through its own peer, whose tools the shell registers; model choice
from `needs`, triggers, background runs, app memory and the system toolbox
for app agents are still coming.

What an app author can do today:

- Build the app's own screens so they are complete without AI, and show
  "unavailable" as a normal state.
- Declare an agent (`agent`, `tools.json`, `AGENT.md`, skills) that passes
  `hub check`, knowing the shells give it a peer and register its tools but
  do not yet install `AGENT.md` or skills, choose its model or fire its
  triggers.
- Write and render L0 cards with `card-studio`, and design them around
  `sys.digest` once OctoScript#40 lands.

**Version skew to know about.** `tools/octo check` runs the App Hub checkout
beside this repository (`main`). The OctoSense shells pin an App Hub commit of
their own (`0f332112` on 2026-09-30, in OctoSense's `native-apps.json`), which
can lag App Hub `main`. Manifests refuse unknown fields, so a field newer than
the shells' pin passes `octo check` but is refused by the shells until their
pin moves.

If you want to prepare, draft `tools.json` and `AGENT.md` outside `bundle/`,
from App Hub's News example
([`crates/app-policy/tests/fixtures/news-agent`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/crates/app-policy/tests/fixtures/news-agent)).

## An app's own agent

**available** in the App Hub gate since
[App-Hub#18](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/18)
(merged 2026-09-27), and in the shells' App Hub pin. Since
[OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184) (2026-09-30) the shell gives an app that declares an
agent (or `octos.*`, or ships `tools.json`) its own peer once the person
allows it, registers the bundle's tools with it, and lets the person talk to
it in the "Ask <app>" panel. No shell installs `AGENT.md` or skills into the
peer, selects a model or fires a trigger yet (ADR 0002, Implementation step
2).

The contract is App Hub's
[PUBLISHING § The app's agent and tools](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-apps-agent-and-tools);
the complete worked example is App Hub's
[`crates/app-policy/tests/fixtures/news-agent`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/crates/app-policy/tests/fixtures/news-agent).

### The design (ADR 0002)

What OctoSense
[ADR 0002](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0002-event-driven-app-agents.md)
(Proposed) decides for AI in apps, in brief:

| § | Decision |
| --- | --- |
| 1 | Each app that asks gets its own agent (its app peer); the system agent supervises and never writes app agents' prompts. |
| 2 | Triggers belong to the app: a schedule, a data event from its host service, or the person in the app. |
| 3 | The app ships its agent: `AGENT.md`, skills, and model **requirements**; the host picks the model from the person's providers. |
| 4 | The app exposes typed tools (`tools.json`) with a risk level and a confirmation owner; the host registers them with the app's peer. |
| 5 | Collection is code (a data service, no model); judgement is the model's. |
| 6 | Searching, research and crawling are a system toolbox the host runs, granted per app with a scope. |
| 7 | Cards are L0, bound to host-resolved sources, rendered and critiqued before `glance.publish`. |
| 8 | The glance screen is curated by the system agent. |
| 9 | Memory is private to the app unless a rule or the person promotes it. |
| 10 | The person talks to the app's agent inside the app; approvals happen there. |
| 11 | The system agent tunes app agents with a versioned overlay; it never edits the pinned `AGENT.md`. |
| 12 | Script apps and native modules follow one model; only where rules are enforced differs. |
| 13 | Least privilege: tools, network, files, memory, secrets, risk, model, budgets, output, control. |
| 14 | A narrow, direct, one-shot model call for bounded jobs (`model.complete`, [above](#one-shot-model-calls-model)); added in OctoSense#95 (merged). |

### The bundle

```text
bundle/
  manifest.json      "agent": { … } (below)
  tools.json         the app's own tools (next section)
  AGENT.md           named by agent.instructions
  skills/<name>/     SKILL.md + manifest.json, each named in agent.skills
  main.splash, listing.json, assets/, screenshots/  as for any app
```

Every file is under the bundle digest, so the agent that runs is the one that
was reviewed. Agent files without an `agent` in the manifest, and undeclared
`AGENT.md` or skill directories, are refused (App Hub
`crates/app-policy/src/agent.rs`).

### The manifest's `agent`

A store app's agent that passes the gate. **✓ run**: `tools/octo new --id
dev.example.brief <dir>`, then this `agent`, the `tools.json` of the next
section (plus a `brief.topics.get` read tool), `AGENT.md` and the skill
below, then `hub stamp <bundle>` and `hub check <bundle> --allow-unsigned`
with a `hub` built from App Hub `crates/` as on `main` `a72989f`:

```json
"capabilities": ["storage", "glance"],
"agent": {
  "profile": "read-only",
  "tools": [],
  "max_iterations": 6,
  "token_budget": 60000,
  "model": {
    "needs": ["tool_calling", "multilingual"],
    "tier": "standard",
    "local_only": false,
    "per_task": { "summary": { "needs": ["tool_calling", "reasoning"], "tier": "strong" } }
  },
  "background": true,
  "triggers": { "schedule": ["30 7 * * *"] },
  "instructions": "AGENT.md",
  "skills": ["morning-brief"]
}
```

```text
$ hub check <bundle> --allow-unsigned
  grants: capabilities {"glance", "storage"}, hosts {}, storage 16777216 bytes, agent read-only
```

(The only refusal was the template's missing screenshot, which a real capture
fixes.)

| Field | Rule (App Hub `manifest.rs`, `policy.rs`) | Enforced today |
| --- | --- | --- |
| `profile` | `read-only`, `workspace-write` or `workspace-write-never-ask`; there is no full access | gate |
| `tools` | generic host tools only: `ledger.read ledger.write net.fetch storage.read storage.write card.render`; anything else is refused | gate |
| `max_iterations`, `token_budget` | clamped to 8 and 200 000 | gate (`grants:` line) |
| `model.needs` | from `tool_calling vision long_context reasoning structured_output multilingual` | gate; the gate warns when an app has tools but no `tool_calling` |
| `model.tier` | `fast`, `standard` (default) or `strong` | gate |
| `model.local_only` | app-wide; data must not leave the person's devices | gate (shareable tools must say `private_data: false`) |
| `model.per_task` | named tasks `[a-z_]{1,32}`, at most 8, that `AGENT.md` refers to | gate |
| no provider or model name | an unknown key is refused: ``hub: manifest is not valid: unknown field `provider`, expected one of `needs`, `tier`, `local_only`, `per_task` `` (**✓ run**) | gate |
| `background` | a request to run while the app is closed; the person grants it per app; requires `triggers` | gate; the grant and the wake are **coming** |
| `triggers.schedule` | five-field cron, local time, at most 16 triggers | gate; firing is **coming** (ADR 0002 M3) |
| `triggers.events` | the app's own host-service events, in its namespace (`news.items.new`) | gate; delivery is **coming** (M3). A store app has no host service, so it has no events to name |
| `instructions`, `skills` | `AGENT.md` (text, 32 KB, no HTML scripts, no `#!`); skill names `[a-z0-9_-]{1,64}`, at most 16 | gate |

**The host picks the model**, from the person's providers, to meet `needs`
and `tier` (ADR 0002 §3, octos `peer/model/set`); policy may lower the tier
or force local models; the person may override per app. That selection is
**coming** (ADR 0002 step 2). How ties are broken is an open question in the
ADR.

### `AGENT.md` and skills

`AGENT.md` is the agent's role: what to do on each trigger, what matters in
the app's data, the rubric its output must meet, and its memory rules. A
skill is data only: `skills/<name>/SKILL.md` plus a `manifest.json` with
`name` (the directory), `version`, `description`, `uses` (each one of the
app's tools or in `agent.tools`; anything else is refused, **✓ run**) and
optionally `prompts.include`; `.md`, `.json` and `.txt` files only;
executable fields (`tools`, `binaries`, `mcp_servers`, `hooks`, …) are
refused.

```json
{
  "name": "morning-brief",
  "version": "1.0.0",
  "description": "Write the short morning note from the followed topics.",
  "uses": ["brief.topics.get", "brief.note.save"]
}
```

### Approvals: `risk` and `confirm`

Declared per tool in `tools.json` (next section). Whether a call needs the
person comes from `risk`; whose surface asks comes from `confirm` (App Hub
PUBLISHING):

| `risk` | Runs |
| --- | --- |
| `read` (looks), `act` (changes the app's own state) | unattended |
| `destructive` (sends, posts, shares, buys, deletes) | only after the person approves |

| `risk: "destructive"` with | Person present | Person absent |
| --- | --- | --- |
| `confirm: "host"` (default) | the host's approval path asks | an approval request in the app's conversation |
| `confirm: "app"` | the app's own confirmation sheet is the only confirmation | an approval request in the app's conversation |

`confirm: "app"` is allowed only for a tool with `implemented_by: "app"` (or a
native module's tool). The gate warns on every destructive tool; making the
example's `brief.note.save` destructive gives (**✓ run**):

```text
  [warning] tools: brief.note.save is destructive and marked background: in a background run it only becomes an approval request, and runs after the person approves
  [warning] agent: a background agent with destructive tools: each destructive call waits as an approval request until the person answers
  [warning] tools: brief.note.save is destructive: every call waits for the host's approval
```

The store shows the person one line per consequence, derived from the
manifest and `tools.json`, for example "Its assistant may work while the app
is closed, on a schedule; only if you allow it, and you can turn it off." and
"Can ask to mail.send: nothing of this runs until you approve it."

### What is enforced where

| Part | Status |
| --- | --- |
| Declarations (fields, sizes, names, schemas, risk, confirm) | **available**: the App Hub gate refuses or warns |
| The approval gate at run time (kernel); approve, edit or decline | **available**: the kernel side ([octos#2567](https://github.com/octos-org/octos/pull/2567)) and the shell's approval sheets ([OctoSense#120](https://github.com/OctoSense-org/OctoSense/pull/120), [#145](https://github.com/OctoSense-org/OctoSense/pull/145)); approvals stay on those sheets, not in the app's conversation ([#184](https://github.com/OctoSense-org/OctoSense/pull/184)) |
| In-app conversation with the app's agent | **available** in the shell's "Ask <app>" panel ([OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)) |
| Memory in `app/<app>/…`, promotion by rule | **coming**: ADR 0002 §9, M7. There is no manifest field; memory rules are prose in `AGENT.md` |
| Overlays by the system agent | **coming**: ADR 0002 §11, M8 |

## The app's tools and peer tools

What the app writes is **available** now: `tools.json` in the bundle, checked
by the App Hub gate (`crates/app-policy/src/agent.rs`):

```json
{
  "schema": 1,
  "tools": [
    {
      "name": "brief.note.save",
      "description": "Save the morning note the app shows on its first screen.",
      "input_schema": {
        "type": "object",
        "properties": { "text": { "type": "string", "maxLength": 600 } },
        "required": ["text"],
        "additionalProperties": false
      },
      "output_schema": { "type": "object", "properties": { "saved": { "type": "boolean" } } },
      "risk": "act",
      "background": true,
      "implemented_by": "app"
    }
  ]
}
```

- `name` is `<namespace>.<tool>`; the namespace is the **last segment of the
  app id** (`dev.example.brief` → `brief`, `os.news` → `news`).
- `input_schema` and `output_schema` are both required (a tool without
  `output_schema` is refused: ``tools.json is not valid: missing field
  `output_schema` ``, **✓ run**). They use a JSON Schema subset (`type title
  description properties required items enum const default minimum maximum
  minLength maxLength minItems maxItems additionalProperties format
  pattern`); the input is an object. At most 64 tools, 1024-character
  descriptions.
- `implemented_by`: `host-service` (native code that holds data, network or
  secrets) or `app` (the app's script, for tools that only reshape its own
  data). The shell runs a `host-service` tool on the host service of its
  namespace, with the app's identity, as the app's own `host.request` would;
  it refuses an `app` tool for now (`<tool> runs in the app's own script;
  open the app to use it`; OctoSense `crates/shell/src/host_tools/script_apps.rs`).
- `background`, `shareable`, `private_data`, `confirm`: see
  [An app's own agent](#approvals-risk-and-confirm).

The shell hands them to the app's peer: the kernel side is
[octos#2567](https://github.com/octos-org/octos/pull/2567) ("host-registered
tools per app peer with tool-list and risk enforcement", UPCR-2026-035,
merged 2026-09-29), and the shell registers an app's `tools.json` for its
peer and relays the calls ([OctoSense#145](https://github.com/OctoSense-org/OctoSense/pull/145), [#184](https://github.com/OctoSense-org/OctoSense/pull/184)). Per
#2567:

| Method | Direction | Shape |
| --- | --- | --- |
| `peer/tools/register` | host → kernel | `{session_id, peer, host_token, tools: [{name, description, input_schema, output_schema?, risk, background?, outward?, confirm?, shareable?}], generic_tools?, if_version?, call_timeout_ms?, approval_ttl_secs?, max_result_bytes?}` → `{…, version, tools: [{name, model_name, risk, background, outward, confirm}], applies: "next_turn"}`. The whole set replaces the previous one. |
| `peer/tool/call` | kernel → host | `{peer, session_id, context_id, turn_id, call_id, tool_call_id, args_digest, name, args, risk, confirm_required, timeout_ms, tools_version}` |
| `peer/tool/result` | host → kernel | `{session_id, peer, host_token, call_id, ok?, data?, error?, status?: "awaiting_confirmation"}` |
| `peer/tool/cancel` | kernel → host | `{call_id, reason: timeout \| cancelled}` |

The model sees `news.list` as `news_list`. Defaults: 30 s per call, results
at most 256 KiB, approvals expire after an hour. A gated call (destructive,
or outward) with `confirm: host` waits for a kernel approval; with
`confirm: app` and the person present it goes to the host with
`confirm_required: true`. The app never calls these methods: the shell
(`crates/ai-host`) does, for the app's peer (ADR 0002 §12).

## The system toolbox

The templates are **available** ([OctoSense#82](https://github.com/OctoSense-org/OctoSense/pull/82), merged:
`crates/toolbox`, crate `octosense-toolbox`), and App Hub has the `research`
and `crawl` capabilities ([App-Hub#26](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/26)).
Granting the toolbox to an app's agent is **coming**
([OctoSense#64](https://github.com/OctoSense-org/OctoSense/issues/64)): the
shells' `toolbox-peers` build feature is off in the shipped builds, and
`crawl` / `deep_crawl` is not implemented (the toolbox's one module is
`research`).

An app's agent never searches, crawls or drives a browser itself. It is
granted toolbox tools, and the host runs them outside the app, under the
app's scope and budget (ADR 0002 §6).

### Templates

Fixed, bounded OctoScript procedures with a manifest (parameters, the host
modules they call, a budget and an output schema), from #82's
`templates/*/template.json`:

| Template | Required params | Optional (default) | Budget: calls / model calls / pages |
| --- | --- | --- | --- |
| `news-digest` | `topic`, `language` | `search_language` ("en"), `translate_query` (false), `limit` (3, 1–5), `max_age_hours` (72) | 8 / 2 / 7 |
| `topic-brief` | `topic`, `language`, `languages` (1–4 of `{language, translate}`) | `per_language` (3), `read_top` (4), `max_age_hours` (72) | 20 / 5 / 10 |
| `market-brief` | `symbols` (1–3 of `{symbol, name}`), `language` | `search_language`, `per_symbol` (2), `max_age_hours` (72) | 13 / 1 / 12 |
| `weather-plan` | `location`, `language` | `activity`, `days` (3), `search_language`, `limit` (2), `max_age_hours` (48) | 7 / 1 / 6 |
| `briefing` | `topics` (1–4), `language` | `search_language`, `per_topic` (2), `max_age_hours` (24) | 17 / 1 / 16 |
| `compare` | `subjects` (exactly 2), `aspect`, `language` | `search_language`, `per_subject` (2), `max_age_hours` (72) | 9 / 1 / 8 |

No template may exceed 64 calls, 8 model calls, 32 pages or 300 s; a run's
budget is further narrowed by the app's budget and its scope's `max_pages`.

### The tools

Per #82's `src/api.rs`, a call is tagged by tool name:

```json
{ "tool": "workflow.run",
  "arguments": { "id": "news-digest",
                 "params": { "topic": "electric cars", "language": "en" },
                 "run_id": "glance" } }
```

| Tool | Arguments | Answer |
| --- | --- | --- |
| `workflow.list` | – | `{templates, refused?}` (the library plus the app's forks) |
| `workflow.run` | `{id, params, run_id?}` (`run_id` `[A-Za-z0-9_-]{1,64}`) | `{run_id, app_id, template: {id, version, digest}, status: ready \| partial \| failed, data, provenance, diagnostics, stats, trace, started_at, result_path?}` |
| `workflow.fork` | `{id, new_id?}` | `{template, path: "toolbox/templates/<id>"}`; the fork records its parent and may not add modules, raise a budget or turn provenance off |
| `workflow.evaluate` | `{a, b, cases}` (1–32 cases) | a comparison of two templates on the same inputs |

Errors are `{"error": {kind, message}}`, `kind` one of `manifest check
widening pin not_found not_granted params runtime io`. The agent reaches
these as peer tools ([previous section](#the-apps-tools-and-peer-tools)), not
through `host.request`.

### Scope, budgets, provenance

- **Scope** (`host.rs`): `languages, regions, allowed_domains,
  denied_domains, max_depth, max_pages, recency_hours`; the host refuses a
  call outside it. (`max_depth` is declared but unused in #82.)
- **The `research` module**: `query`, `search` (structured items), `article`
  (only ids found in this run; one page each; the text is hashed as
  evidence) and `digest` (a summary of at most 1200 characters and up to 12
  cited points).
- **Provenance is the host's**, never the model's: each source carries `id,
  url, title, source, language, published_at, retrieved_at, evidence_sha256,
  via`. A URL in the output that the host did not retrieve fails the run.
- **Results** are written to `<app folder>/toolbox/runs/<template>/<run_id>.json`.
- **One budget per app**: with `toolbox-peers`, the toolbox's model client
  goes through the `model` service's `ModelHost::complete`
  (`crates/ai-host/src/toolbox_peers.rs`), so template calls and direct
  `model.complete` calls draw on the same budget.

## Publishing to the glance screen

### `glance.publish`, `glance.withdraw`, `glance.list`

The service is **available** on OctoSense `main`
([#72](https://github.com/OctoSense-org/OctoSense/pull/72),
`crates/shell/src/glance.rs`):

| Method | Args | Answer |
| --- | --- | --- |
| `glance.publish` | `{card_id, source, data?, title, priority?, expires?, open?: {app, route?}}` | `{card_id, replaced, expires_at}` |
| `glance.withdraw` | `{card_id}` | `{withdrawn}` |
| `glance.list` | – | `[{card_id, title, priority, published_at, expires_at}]`, the caller's own cards only |

- `source` is an **L0 card** (L1 if its header declares it; L2 refused),
  realized against `data` (a map from the card's source names to values) and
  lowered through the Card runner's pipeline before it is stored.
- **Limits:** `card_id` 1–64 of `[A-Za-z0-9._-]`; `title` at most 80
  characters; `source` at most 16 KiB; `data` at most 32 KiB as JSON;
  `priority` 0–100 (default 50); `expires` 60 s to 7 days (default 24 h); 6
  publishes per minute per app (a replace, and a card the L0 check refuses,
  both count); 4 cards per app; 32 in the store; 6 shown.
- **Identity:** the publisher is the caller, never an argument; publishing
  the same `card_id` replaces the card; `open.app` must be the caller's own
  app. A tap opens that app. `open.route` is stored but not used yet.
- A tile runs in its own isolate, under its publishing app's policy (a
  native module's tile gets none), and cannot raise a sheet.

### Who may publish

- **Any contained app granted `glance`** may publish, list and withdraw its
  own cards ([OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86), merged; the capability is
  [App-Hub#22](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/22), in
  the shells' App Hub pin). System apps get no exemption. Refusal:
  `<app> was not granted the glance capability`.
- Native modules and the shell's demo (`OCTOSENSE_GLANCE_DEMO=1`) publish too.

A call from an app looks like this (the shape is `glance.rs`'s; not run,
since `card-host` registers no host services):

```splash
host.request("glance.publish", {
    card_id: "morning"
    title: "Morning brief"
    source: card_source
    data: {}
    expires: 43200
}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) }
})
```

Request `glance` only if the app publishes cards; the store shows "Show cards
on your glance screen".

## Cards bound to findings: `sys.digest`

**coming**: [OctoScript#40](https://github.com/OctoSense-org/OctoScript/pull/40)
(the L0 source), [OctoScript-Makepad#50](https://github.com/OctoSense-org/OctoScript-Makepad/pull/50)
(repin), [OctoSense#87](https://github.com/OctoSense-org/OctoSense/pull/87)
(the shell resolves it, `crates/shell/src/glance_digest.rs`).

L0's no-facts rule forbids a card from stating findings as its own text, so
the findings become a source the host resolves:

```text
source brief sys.digest(app: "os.news", id: "glance",
                        fields: [topic, summary, points, sources, id, text, cite, n, title, source])
```

- `app` is a literal and must be the publishing app; the host refuses a card
  naming another. `id` is a literal (`[A-Za-z0-9_-]{1,64}`, the toolbox's
  run-id charset) or a path into state.
- The record: `status` (`ready partial failed missing expired`), `topic`,
  `language`, `summary`, `retrieved_at`, `count`, `points` (`{id, text, label,
  cite, citations}`) and `sources` (`{id, n, title, source, url,
  published_at}`).
- **Links come only from `sources`**, which the host retrieved; text with a
  URL is dropped. A missing, expired or malformed digest resolves to an empty
  record with `$state` `.failed`, never an error, so the card shows its own
  "nothing yet" copy.
- In #87 the host reads the newest `toolbox/runs/<template>/<id>.json` for the
  app (under the host's directory, outside the app's jail), keeps only
  sources in the run's host-kept provenance, caps text (summary 800, 8 points
  of 400, 8 sources) and expires a digest 48 h after its run started; the
  card's expiry is at most the digest's.

The worked example is #87's `crates/shell/resources/glance/news-brief.card`:

```text
# ledger news.brief@1.0.0
# level:   L0
# profile: ui/l0

source brief sys.digest(app: "os.news", id: "glance",
                        fields: [topic, summary, points, sources,
                                 id, text, cite, n, title, source])

copy label   { class: vocabulary, en: "NEWS DIGEST", zh: "新闻摘要" }
copy nothing { class: vocabulary, en: "No digest yet. News will brief you after its next read.", zh: "暂无摘要。新闻读完下一批后会为你汇总。" }
copy sources { class: vocabulary, en: "SOURCES", zh: "来源" }

view root  Surface(pad: .page) {
             Col(gap: 6) {
               Row(gap: 8) {
                 TextCaption(text: copy.label, width: .fill)
                 TextCaption(text: brief.topic)
               }
               when brief.$state == .failed { TextBody(text: copy.nothing, width: .fill) }
               when brief.$state == .ready {
                 Col(gap: 6) {
                   TextBody(text: brief.summary, width: .fill)
                   for p in brief.points key p.id {
                     Row(gap: 8) {
                       TextRow(text: p.text, width: .fill)
                       TextCaption(text: p.cite)
                     }
                   }
                   TextCaption(text: copy.sources)
                   for s in brief.sources key s.id {
                     Row(gap: 8) {
                       TextCaption(text: s.n)
                       TextCaption(text: s.source)
                       TextCaption(text: s.title, width: .fill)
                     }
                   }
                 }
               }
             }
           }
```

(Its header comment is shortened here.) Until OctoScript#40 lands, the L0
checker does not know `sys.digest`, so a card using it is refused.

## Card levels and render-and-critique

The levels are defined in OctoScript's
[`docs/ui-profile-l0.md`](https://github.com/OctoSense-org/OctoScript/blob/main/docs/ui-profile-l0.md):

| Level | What it admits | For AI output |
| --- | --- | --- |
| **L0** | UI declarations only: data from catalogued `sys.*` sources the host resolves, no expressions, no calls | the default for generated and glance cards |
| **L1** | L0 plus arithmetic expressions, declared with a `# level: L1` header | only where arithmetic is needed |
| **L2** | imperative Splash (`ui.<id>.set_*`) | refused for generated cards; this is what a script app's `main.splash` is |

L0 card examples in this repository: [docs/l0/](l0/).

**Render and critique** (**available**, App Hub `main`, `crates/card-studio`;
the octos skill `skills/card-studio`, tools `card_render` and
`card_critique_payload`): render a card in a hidden `card-host --remote` at
the target sizes, run the measured checks (truncated text, does not fit,
failed source, lint, lowering), then build a vision-critique request against
a rubric. From App Hub's
[DEVELOPMENT.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/DEVELOPMENT.md#inspecting-a-card-before-publishing-card-studio)
(not run for this page):

```sh
cargo build --release -p octosense-card-host -p octosense-card-studio
export CARD_STUDIO_KIT=../octoscript-makepad/components/l0
target/release/card-studio render --card news.card --data digest.json \
    --size glance --size phone --size desktop --out out/
target/release/card-studio critique --report out/report.json --rubric AGENT-rubric.md --inline > request.json
```

By hand, the same instrument: `card-host … --remote` (or
`MAKEPAD_REMOTE=<port>`), then `/snap` for widget text and rectangles, `/g`
for a frame grab (`/g?raw=1` for the PNG bytes), `/d` for the tree, `/log`,
and `/quit`. `tools/octo run --hidden` and `tools/octo shot` wrap this for a
bundle (README, [Headless testing](../README.md#headless-testing-many-apps-no-screen)).

Running the loop from an app's agent (ADR 0002 M6) is **coming**.

## End to end: News

News is ADR 0002's first slice. Each step, with where it stands:

| # | Step | Status | Where (OctoSense unless named) |
| --- | --- | --- | --- |
| 1 | **The data service collects**, no model: HN, TechMeme, Google News, RSS, followed topics (Google News, GDELT), a seen-items ledger, every 15 minutes | **available** (M1) | `apps/news/host-service`: `news.list`, `news.read`, `news.topics.get`, `news.topics.set`, `news.refresh`, `news.sources`, `news.feeds.import`; `os.*` only |
| 2 | **The bundle reads from it**: `host.has("news")`, then `news.list {feed, current: true, limit: 30}` | **available**: News's manifest requests `news` and uses the service when `host.has("news")` | `apps/news/bundle/main.splash` |
| 3 | **A trigger wakes the agent**: the service's fetch report ("N new items") as `news.items.new`, or a schedule (`0 7 * * *`) | **coming** (M3): the service's `on_fetch` hook only logs today | `crates/shell/src/apps.rs` `register_news` |
| 4 | **News's agent runs**, with its `AGENT.md`, skills and tools declared in the bundle | declarations **available** in App Hub (#18); a peer for `os.news` with its `tools.json` tools, once the person allows it, **available** ([OctoSense#184](https://github.com/OctoSense-org/OctoSense/pull/184)); `AGENT.md` and skills in the peer **coming** | `apps/news/bundle`, `crates/shell/src/agents.rs` |
| 5 | **It runs the `news-digest` template**: `workflow.run {id: "news-digest", params: {topic, language}, run_id: "glance"}` | template **available** (#82); run by the app's agent **coming** (M5, #64) | `crates/toolbox` |
| 6 | **The result is stored** by the host, with provenance: `toolbox/runs/news-digest/glance.json` | **available** in the toolbox runner (#82); from the agent **coming** (#64) | `crates/toolbox/src/runner.rs` |
| 7 | **A card binds to it**: `news-brief.card`, `source brief sys.digest(app: "os.news", id: "glance", …)` | **coming** (OctoScript#40, OctoScript-Makepad#50, #87) | `crates/shell/src/glance_digest.rs` |
| 8 | **Render and critique** the card at glance, phone and desktop sizes | tool **available** (`card-studio`); run by the agent **coming** (M6) | App Hub `crates/card-studio` |
| 9 | **`glance.publish`** the card (`card_id` "brief", `data: {}`; the host fills `brief`) | **available**, from a contained app granted `glance` (#86) | `crates/shell/src/glance.rs` |
| 10 | **The person taps it and News opens** | **available** (the desktop panel and the phone's glance page open the publishing app) | `glance_panel.rs`, `mobile_pages.rs` |

To see steps 9–10 today, run the desktop shell's own check, which publishes a
sample card as `os.news` at startup (`OCTOSENSE_GLANCE_DEMO=1`) and opens News
from it, hidden and driven over the remote instrument (from an OctoSense
checkout; not run for this page):

```sh
cargo build --release -p octosense && desktop/scripts/glance_remote.sh
```

## Testing without a provider

- **Run the app headless**, never with OS screenshots, as in
  [Test it](#test-it) and [QUICKSTART §4a](QUICKSTART.md#4a-headless-test-without-the-screen-several-apps-at-once).
  `card-host` registers no host services, so by the rule verified above for
  `octos` and `model`, a granted `glance.*` call there answers `no service
  answers "glance" on this device` and an ungranted one `this app was not
  granted "glance", which "glance.publish" needs` (not run for `glance`).
  Make every such call's error path visible in the UI, and exercise it.
- **Check the agent declarations** with the gate: `tools/octo check <bundle>`
  (`hub check`) validates `agent`, `tools.json`, `AGENT.md` and skills
  offline; no model is involved ([An app's own agent](#an-apps-own-agent),
  **✓ run** with `hub check`).
- **Cards:** render with `card-studio render --card … --data <fixture>.json`
  ([above](#card-levels-and-render-and-critique)): the data is a fixture, so
  no model or network is needed. For a `sys.digest` card, #87 ships a run
  fixture, `crates/shell/resources/glance/fixtures/news-digest-run.json`, and
  `OCTOSENSE_GLANCE_DEMO=digest` (**coming**).
- **Fakes in the platform's own tests**, for when you change a service or the
  toolbox (in OctoSense, not in an app bundle; the commands were not run for
  this page):

  | Piece | Fake | Status |
  | --- | --- | --- |
  | `model` service | a fake transport, `cargo test --locked -p octosense-llm-service --test complete` | **available** (#95) |
  | Toolbox templates | `fixture::FakeModel` (deterministic, extractive; can inject a bad URL or citation) and `FixtureBackend`, with recorded cases in `templates/*/fixtures/`; `cargo test --locked -p octosense-toolbox` | **available** (#82) |
  | `news` service | a fixture `Fetcher` and a moved clock; `cargo test -p octosense-news-service` ("fixtures, no network") | **available** |
  | `llm` service | a local fake provider endpoint (`fake_provider`), `FakeScanner`, `FakePicker`; `OCTOSENSE_LLM_VAULT=file` keeps keys out of the Keychain | **available** |
  | App peers | `tests/fixtures/mock_llm.py` (an OpenAI-compatible server that answers `ECHO: <text>`), a profile with `model_id: "mock-model"`; real-kernel tests run only with `OCTOS_APP_PEERS_TEST_KERNEL=<octos>` | **available** |
  | Kernel | `crates/kernel/tests/fixtures/fake_kernel.py` | **available** |

  An app bundle cannot swap in any of these; they are the platform's.

## Sources

- OctoSense `main` (`405139f`, re-checked at `89787ba`): `AGENTS.md`;
  `docs/adr/0002-event-driven-app-agents.md`;
  `docs/adr/home/0004-system-apps-are-contained-script-apps.md`;
  `crates/app-peers/README.md`; `crates/ai-host/src/lib.rs`;
  `apps/ai-providers/host-service/src/lib.rs`; `apps/news/host-service`;
  `apps/news/bundle/main.splash`; `crates/shell/src/glance.rs`,
  `crates/shell/src/apps.rs`. Pull requests #70, #82, #86, #87, #95
  (`apps/ai-providers/host-service/src/complete/`), and, for the 2026-09-30
  update, #106, #120, #145 and #184 (`crates/ai-host/src/contained.rs`,
  `crates/shell/src/agents.rs`, `crates/shell/src/host_tools/script_apps.rs`),
  at `main` `7082ff5`.
- OctoSense-App-Hub `main` (`a72989f`; `0f33211` for the 2026-09-30 update): `crates/app-policy/src/manifest.rs`,
  `services.rs`, `agent.rs`, `policy.rs`, `listing.rs`; `docs/PUBLISHING.md`;
  `docs/DEVELOPMENT.md`.
- OctoScript pull request #40: `docs/ui-profile-l0.md` §5.14.
- octos pull request #2567:
  `docs/OCTOS_UI_PROTOCOL_CHANGE_REQUEST_UPCR_2026_035_PEER_HOST_TOOLS.md`.
- Rinx: `src/host/octos.rs`.
