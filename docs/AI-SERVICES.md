# AI in your app: OctoSense's assistant

English | [简体中文](AI-SERVICES.zh-CN.md)

A script app built here can use AI on an OctoSense device in three ways:
host model calls (`model`), a conversation with the device's assistant
(`octos.*`), and an agent of its own, declared in its bundle. The status labels
below distinguish **available** (on the named repository's `main`, as
described), **implemented in a PR** (pending integration/release), and **not yet**.

Commands marked **✓ run** were run on macOS (Apple silicon) with `hub` and
`card-host` built from App Hub `main`. Everything else was read in the code;
nothing here was run in an OctoSense shell. How the shell builds all this:
OctoSense's [`docs/ai-services.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.md)
and [`docs/architecture.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/architecture.md).

> **Building an app needs no AI.** Building and checking a script app calls
> no model and needs no API key, and you may use any coding agent (Codex,
> Claude Code, Cursor, Gemini CLI, GitHub Copilot, …) or none. Only the
> Sketch design-kit flow runs a model, and only if you opt in to its legacy
> visual reviewer, which calls the `claude` CLI (`flows/core/llm.py`). This page is only about the assistant
> your *finished app* may ask for on the device.

## Contents

- [The short answer](#the-short-answer)
- [How the assistant is built](#how-the-assistant-is-built)
- [The system agent and app agents](#the-system-agent-and-app-agents)
- [The assistant capabilities](#the-assistant-capabilities)
- [A minimal call, and handling "unavailable"](#a-minimal-call-and-handling-unavailable)
- [What the person sees](#what-the-person-sees)
- [Errors](#errors)
- [Test it](#test-it)
- [One-shot model calls (`model`)](#one-shot-model-calls-model)
- [Media and embeddings (`model`)](#media-and-embeddings-model)
- [An app's own agent](#an-apps-own-agent)
- [The app's tools and peer tools](#the-apps-tools-and-peer-tools)
- [The system toolbox](#the-system-toolbox)
- [Publishing to the Glance screen](#publishing-to-the-glance-screen)
- [Cards bound to findings: `sys.digest`](#cards-bound-to-findings-sysdigest)
- [AI-written text and in-card chat: `model-copy`, `sys.chat`](#ai-written-text-and-in-card-chat-model-copy-syschat)
- [Card levels and render-and-critique](#card-levels-and-render-and-critique)
- [Sources](#sources)

<a id="status-at-a-glance"></a>

## The short answer

**On an OctoSense device a store app can make one-shot model calls
(`model`), and can talk to the assistant (`octos.*`) once the person allows
its agent.** App Hub's `card-host`, which `tools/octo run` uses, serves no
host services except `runtime` discovery, so both answer
`no service answers "…" on this device` there.
Build your app so it is complete without AI either way: the person may
decline, and a device may have no kernel (iOS) or no provider.

| You want to | What happens today | More |
| --- | --- | --- |
| Make one-shot model calls (`model`) | **available** in the OctoSense shells: a schema-checked call answered by the person's own AI providers, within a daily budget. `card-host` answers `no service answers "model" on this device` (**✓ run**). | [One-shot model calls](#one-shot-model-calls-model) |
| Generate images, speech, video or embeddings (`model`) | **Implemented in [OctoSense #368](https://github.com/OctoSense-org/OctoSense/pull/368)**, pending integration/release. Requires a compatible shell and an entitled configured provider; absent from beta.2 and `card-host`. Live paid-provider/device use is **unverified**. | [Media and embeddings](#media-and-embeddings-model) |
| Talk to the assistant from your screens (`octos.*`) | **available** where the shell hosts a kernel (not iOS). The first call is refused with `Waiting for the person to allow this app's agent (OctoSense asks the first time)` while the shell asks; after that, the app talks to its own peer. `card-host` answers `no service answers "octos" on this device` (**✓ run**). | [A minimal call](#a-minimal-call-and-handling-unavailable) |
| Give the app its own agent (`agent`, `tools.json`, `AGENT.md`, `skills/`) | **available**: once the person allows it, the agent gets a peer, an "Ask &lt;app&gt;" panel, `ask_user_question`, read tools over the account folder (Unix only), its granted host-service tools, and `AGENT.md` and skills as guidance for each turn. A `tools.json` without an `agent` block also gives the app an agent. | [An app's own agent](#an-apps-own-agent) |
| Run a tool the app's script implements (`implemented_by: "app"`) | **not yet in a release**: on OctoSense `main`, the tool runs in the open app when the manifest declares `requires: ["script-tools-v1"]`, and a call to a closed app answers `app_not_running`. `desktop-v0.1.0-beta.2` refuses it. | [The app's tools](#the-apps-tools-and-peer-tools), [HOST-API-V1 §5](HOST-API-V1.md#5-implement-a-declared-app-tool) |
| Wake the agent on an event | **available** for the Gmail service's `<namespace>.new_message`; **not yet** for other events. | [The manifest's agent](#the-manifests-agent) |
| Wake the agent on a schedule, or choose its model from `needs` | **not yet** | [The manifest's agent](#the-manifests-agent) |
| Publish Glance cards (`glance`) | **available**: L0, script and template cards, with notifications. On OctoSense `main` (not in any release yet), an agent's tools may publish only template and L0 cards. | [Publishing to the Glance screen](#publishing-to-the-glance-screen) |
| Chat with the agent inside a card, or show model-written text (`sys.chat`, `model-copy`) | **available** in the shells; this repository's runtime checks both. | [AI-written text](#ai-written-text-and-in-card-chat-model-copy-syschat) |
| Bind a card to research findings (`sys.digest`) | **available** for system apps; **not yet** for store apps, which have no research runs to bind. | [Cards bound to findings](#cards-bound-to-findings-sysdigest) |
| Search and crawl through the system toolbox (`research`, `crawl`) | **not yet** for store apps ([OctoSense#64](https://github.com/OctoSense-org/OctoSense/issues/64)). | [The system toolbox](#the-system-toolbox) |
| Use the person's GitHub or Google account (`auth` with `github`, `gcalendar` or `gmail`) | **available** in OctoSense desktop-v0.1.0-beta.2; most live use of the real providers is unverified. | [CAPABILITIES](CAPABILITIES.md#use-a-connected-account) |
| Manage the device's AI providers (`llm`) | System apps only: `llm is for OctoSense's own apps.` Do not request it. | – |
| Render and critique a card (`card-studio`) | **available** in App Hub; an agent that runs this loop itself: **not yet**. | [Card levels](#card-levels-and-render-and-critique) |
| Ship a provider API key | Never. No keys, tokens or passwords in an app ([AGENTS.md](../AGENTS.md#rules-for-every-app)). | – |

To ship today: make every screen work without AI, keep the data the agent
should read under `accounts/device/`, and pass `hub check` with your agent
files.

A plain HTTPS API your app declares under `net` is just a web request, even
if a model runs behind it. The usual rules hold: no key or token in the
bundle, the host is listed, and your privacy text says what leaves the
device. It is not the device's assistant and uses none of the person's AI
providers.

## How the assistant is built

- **One octos kernel per shell.** The OctoSense desktop and Home (the phone
  shell) each run one kernel, started on first use. Android bundles it,
  OpenHarmony runs it in process, iOS has none. A desktop runs the binary
  named by `OCTOS_APP_CORE_BIN`, else the packaged `octos-kernel` beside the
  shell.
- **AI providers** (a system app) is where the person picks models and enters
  API keys, on host-owned sheets. Keys stay with the host: in the Keychain on
  macOS, and in owner-only host files elsewhere. No app ever sees one.
- **Apps reach AI only through host services and the app-peer broker**, never
  the kernel, a provider or a key (OctoSense
  [`AGENTS.md`](https://github.com/OctoSense-org/OctoSense/blob/main/AGENTS.md)
  rules 3 and 4).
- **App peers.** An app the host grants the assistant gets its own octos peer
  for each account it keeps (one `device` account unless the manifest says
  `storage.accounts: true`): private conversation contexts, a workspace (the
  account's folder, `apps/<app>/accounts/<account hash>/`) and memory
  (`app/<app>/acct-<hash>`), owned by the shell's system agent
  (`crates/app-peers`).
- **Approvals are the person's, in the app that asked.** The system agent
  never approves for an app.

**Native apps** are compiled Rust apps the shell links from OctoSense's
`native-apps.json`. Most run inside the shell's process as **native
modules**; on the desktop, Terminal and Task run as separate **process
apps**. The native apps the shell's host policy grants get a peer:
`Policy::shipped()` in OctoSense `crates/ai-host/src/lib.rs` grants those
listed in `native_agents.rs` (Rinx, a Matrix client, and Terminal, App Hub,
Calculator, Clock, Notes, Reminders and Weather). Rinx's mini-app host serves
the `octos.*` names to the mini-apps a person imports into Rinx. A
**contained script app** gets its own peer too (`card.<app id>`), through the
shell's `octos` host service, once the person allows its agent at first use.
`OCTOSENSE_CONTAINED_APPS=1` skips the question for every app (a developer
override), and `0` turns the assistant off for every app.

## The system agent and app agents

- **Which apps have an agent.** A script app whose manifest declares an
  `agent` block or any `octos.*` name, or whose bundle ships `tools.json`;
  a native app whose shell entry grants `octos.*` (the native apps above).
  Setup › Assistant › Approvals lists each one, and the person can turn it
  off there. Among the
  system apps, News, Mail, Calendar, Photos, Maps and YouTube have one, and
  Camera on the phone. None of them declares an `octos.*` name, so the shell
  drives their agents and the apps never call `host.request("octos…")`.
- **First use.** The person allows an app's agent on a first-use sheet,
  raised by the app's own first `octos.*` call, by its "Ask &lt;app&gt;" panel
  (the bar's "Ask &lt;app&gt;" or Shift+F8 on the desktop), or by the system
  agent's `agents.ask`. From then on the shell prepares the peer at startup
  and registers its tools, whether or not the app is open. A script app's
  peer is `card.<app id>` (so `card.os.mail`); no native app's peer id
  starts with `card.`.
- **The system agent** is the shell's own session
  (`_main:api:octosense#system`), which the person talks to in the system
  chat (the assistant pane; F8 on the desktop). It sees every prepared app
  peer with `peer_list`,
  hands one work with `peer_send_input`, reads what it wrote with
  `peer_gather`, and asks the shell with `agents.list` / `agents.ask` about
  apps whose agent the person has not allowed yet. At the person's request it
  configures Mail's agent with `agents.provision` (instructions, skill text
  and incoming-mail processing) and reads its state with `agents.status`. It
  holds no app's tools, never approves for an app and cannot close an app's
  peer.
- **Questions.** An agent that keeps `ask_user_question` may ask the person
  something. A question from a turn the person or the app started is shown
  in the app's conversation; one from a turn the system agent started goes
  to the system chat. The shell declines a question nobody answers within
  10 minutes.
- **Example** (not run): the person asks the system agent for a calendar
  card; it hands the request to Calendar's agent with `peer_send_input`
  (Calendar's first-use sheet appears if the person has not allowed it
  yet); Calendar's agent calls one of its own tools (`calendar.notify`,
  `calendar.agenda`), whose host service fills a fixed L0 card it ships and
  publishes it to the Glance screen as Calendar. The model never writes the
  card's code.
- **Lifecycle.** A peer keeps its memory across launches. Signing out of an
  account suspends that account's agent; removing the account or
  uninstalling the app erases it (octos `peer/purge`), so a reinstall starts
  a new agent.

### The person talks to an app's agent directly

An app's agent is not only reachable through the system agent: the person
can talk to it directly, in three places. Each place has a **person's lane**
of its own, beside the system agent's lane. Nothing runs until the person
has allowed the app's agent on its first-use sheet.

| Where | What the person does | What the app author writes |
| --- | --- | --- |
| The shell's **"Ask &lt;app&gt;" panel** | Opens it for the focused app's agent from the bar's "Ask &lt;app&gt;" button, Shift+F8, or Setup › Assistant › "Ask this app's agent" (desktop). Its turns run in the person's lane; its Stop button stops only that lane. Questions the app's agent asks in the person's lane are answered here. | Nothing: the shell draws the panel for **every** app that has an agent, whether or not the app has a chat screen of its own. |
| An **in-card chat** on the Glance screen | Types into a card the app published; the app's own agent answers in the card. | An L0 card with `sys.chat` and `ChatEntry`, published with `glance` ([below](#ai-written-text-and-in-card-chat-model-copy-syschat)). |
| The **app's own screens** | Uses whatever chat or "ask" control the app draws. | `host.request("octos.session.open" / "octos.turn.start" / "octos.session.history" / "octos.turn.interrupt", …)` on the `octos` service, with those names in `capabilities` ([A minimal call](#a-minimal-call-and-handling-unavailable)). |

- **One conversation, two lanes.** The system agent's lane is the peer's
  own session (`_main:api:octosense#peer-…`); a person's lane is a request
  context opened with shared history (`…#peerctx-…`). Each lane sees the
  other's recent messages, read only. Turns are labeled by speaker, and the
  events and `octos.session.history` rows carry `lane` (`person` or
  `system_agent`) and `speaker`.
- **Each place keeps its own person's lane.** OctoSense keys a person's lane
  by account and client instance. The panel's instance is `shell-ask`, an
  in-card chat's is `card-chat`, and the app's own `octos.*` calls use
  `<peer>-g<generation>`. So `octos.session.history` returns the app's own
  conversation, never what the person asked in the panel or in a card.
- A turn from the panel or the system chat is the person's own
  (`TurnTrigger::Person`).
- **Stop on the shell's approval surface** for an app's agent (the button
  under its pending approvals and questions, `approvals::stop_agent`)
  declines what that agent is waiting on and stops its running turns in
  **both** lanes: the person owns the device.
- **On the phone** the panel is built as a full-screen sheet, but on `main`
  no touch control opens it (the phone's Assistant tile opens the system
  chat); not run on a device. An app's own screens and its Glance cards
  work there as on the desktop.
- Native modules and process apps open a person's lane their own way
  (`open_conversation` on the injected service, or the peer link); a script
  app uses the `octos.*` names above.

## The assistant capabilities

There are four exact names, each its own consent (`KNOWN_CAPABILITIES` in
App Hub `crates/app-contract/src/manifest.rs`). A prefix grants nothing: the
gate refuses `octos.` and `octos.admin`. For the store's words for each, see
App Hub [PUBLISHING § The manifest](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-manifest).

| Capability and call | Args | Answer (`r.data`) |
| --- | --- | --- |
| `octos.session.open` | `{}` | `{open: true, conversation, shared_history, model: {lane, provider, model} or nil}` |
| `octos.session.history` | `{}` | the app's own conversation, `{session_id, messages: [...], …}`: its lane and the system agent's, merged by time, each message with its `lane` and speaker. It never includes the "Ask &lt;app&gt;" panel's turns. |
| `octos.turn.start` | `{text}` (1 byte to 32 KiB) | `{turn_id, text, speaker, lane}`: the reply, once the turn ends |
| `octos.turn.interrupt` | `{}` | `{interrupted, turns}`: in the OctoSense shells it stops the running turns in both lanes, the system agent's included |

Two hosts serve these names, with the shapes of OctoSense's
`crates/app-peers`: the OctoSense shells' `octos` service for contained apps
(`crates/ai-host/src/contained.rs`) and Rinx's mini-app host
(`src/host/octos.rs` in [hagency-org/Rinx](https://github.com/hagency-org/Rinx)).

- Send `text` to `octos.turn.start`, and nothing to the other three calls.
  The OctoSense shells also accept two optional arguments with `text`:
  `trigger` (`person`, `app`, `incoming`, `schedule` or `background`) and
  `from`, which say what started the turn; without them the turn counts as
  unknown. Any other argument gets `Unsupported Octos arguments`: an app
  never names a session, profile, provider, model or approval decision.
- One turn runs at a time per app instance, and a turn times out after 180 s.
- A script app gets no pushed events. Poll `octos.session.history`, which
  includes the system agent's turns.

`trigger: "person"` from an app labels the turn as the person's in the
transcript, but the approval rules treat it as the app's own run: a standing
rule such as "when I start it" never answers it. Only the shell's own
composers (the "Ask &lt;app&gt;" panel, the system chat) vouch for the person.

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

**✓ run** in `card-host` with `tools/octo run … --hidden`, with `ask()`
called once the app started:

| Manifest | The label read |
| --- | --- |
| `["octos.session.open", "octos.turn.start"]` | `Assistant unavailable: no service answers "octos" on this device` |
| `["storage"]` | `Assistant unavailable: this app was not granted "octos", which "octos.session.open" needs` |

An OctoSense shell that hosts a kernel answers differently: the first call
is refused with `Waiting for the person to allow this app's agent (OctoSense
asks the first time)` while the shell asks the person, and once they allow
it, the next call reaches the app's own peer (not run). See
[Errors](#errors) for what each refusal says.

**Should you ship this today?** Only if the app is complete without it: the
person may decline, the device may have no kernel or no provider, and
`tools/octo run` never answers. A reviewer asks about grants nothing on screen
needs (`hub scan`), and every `octos.*` line appears on the store's permission
list.

## What the person sees

- **Before install**, the store shows one permission line per capability,
  and in the privacy summary: "Asks the device's assistant to work for it; the assistant's keys
  stay with the device." (with `octos.turn.start`), or "Opens or reads its
  own conversations with the device's assistant, but cannot ask it to work."
  (open or history only).
- **For an app with an `agent` block**, the store adds permission lines for
  the assistant, and they differ by build. The `desktop-v0.1.0-beta.2` store
  shows "Run an assistant for this app (&lt;tools&gt;), inside this app's own data
  only", where `<tools>` lists the `agent.tools` entries that are not kernel
  tools, or says `no tools`; it leaves out the `tools.json` tools. The store
  in OctoSense `main` (not in any release yet) shows "Run an assistant for
  this app, only after you allow it", then "Its assistant can use these app
  tools: …" with the `tools.json` names, and "Its assistant requests these
  additional tools: …" with the same non-kernel `agent.tools` entries.
- **Keys and providers** are set only in the AI providers app, on host
  sheets.
- **Tool approvals** the assistant raises go to the person, in the app that
  asked, on the host's own controls (the OctoSense shells' approval sheets;
  Rinx's own for its mini-apps); the system agent never answers them. A
  script app cannot approve anything: no argument carries a decision. The
  sheet shows every argument in full (hidden and control characters as their
  code points, a command one line per row), and its approve buttons stay
  disabled until the person has scrolled through all of them.
- **A first-use sheet** for the app's agent, listing what it may read (its
  own memory, and its account folder or, with
  `storage.agent_workspace: "none"`, "No files: only what its tools
  return"), what it may use ("Ask you questions" for an agent that keeps
  `ask_user_question`) and where the model runs
  (`crates/shell/src/approvals/consent.rs`). Setup › Assistant › Approvals
  turns it off again.

## Errors

| `r.error` | Meaning | What your app does |
| --- | --- | --- |
| `this app was not granted "octos", which "<service>" needs` | The manifest does not list that exact name | Add it to `capabilities`, or remove the call |
| `no service answers "octos" on this device` | This host does not serve the assistant to apps (`card-host`, or a shell built without a kernel) | Show "unavailable" and carry on |
| `Waiting for the person to allow this app's agent (OctoSense asks the first time)` | The person has not allowed the app's agent yet; the shell is asking | Show it; call again after the person answers |
| `The assistant is turned off for apps on this device` | The device turned the assistant off for apps (`OCTOSENSE_CONTAINED_APPS=0`) | Show "unavailable" and carry on |
| `The assistant is not available on this device` | The shell could not start the app's peer | Show "unavailable" and carry on |
| `Add an account in the app before using its assistant` | The app keeps accounts (`storage.accounts: true`) and has none yet | Offer the app's own way to add an account |
| `This app's manifest does not declare that assistant service` | The shell's own check behind the isolate's: the manifest lists no `octos.*` name, or not this one | Declare it, or remove the call |
| `no service answers "model" on this device` | No `model` service on this host (`card-host`) | Show "unavailable" and carry on |
| `<code>: <sentence>` from `model.complete`, `<code>` one of `capability`, `no_provider`, `rate`, `budget`, `bad_request`, `invalid_output`, `too_large`, `provider` | The `model` service refused the call ([details](#the-model-service)) | Show the sentence; keep the app usable without the model |
| `Unsupported Octos arguments` | An argument other than `text`, `trigger` or `from` to `octos.turn.start`, or any argument to the other calls | Send only those |
| `Provide text (at most 32 KiB)` | Empty or oversized prompt | Check before sending |
| `This app already has an assistant turn running` | One turn at a time | Disable the button while waiting, or interrupt first |
| `Nothing is running in this conversation` | `octos.turn.interrupt` with nothing running (Rinx's mini-app host says `No assistant turn is running`) | Nothing to do |
| Anything else (no provider configured, the provider failed, quota, signed out, revoked) | The host's text, passed through | Show it; never retry in a loop |

The `model` service keeps a per-app daily budget, which `model.budget`
reports ([below](#the-model-service)).

## Test it

- **In the harness:** `tools/octo run <bundle> --hidden --port 8141`, drive
  the app over the remote bridge and read its labels with `/snap`, never with
  OS screenshots ([QUICKSTART §4a](QUICKSTART.md#4a-headless-test-without-the-screen-several-apps-at-once)).
  `card-host` registers no host services, so expect `no service answers`
  from every assistant, model and Glance call; screenshot that as your app's
  "unavailable" state. A granted `glance.publish` there answers
  `no service answers "glance" on this device` (**✓ run**).
- **The agent declarations:** `tools/octo check <bundle>` (`hub check`)
  checks `agent`, `tools.json`, `AGENT.md` and skills offline, with no model
  ([The manifest's `agent`](#the-manifests-agent), **✓ run**).
- **Cards:** render them with `card-studio render --card … --data <fixture>.json`
  ([below](#card-levels-and-render-and-critique)); the data is a fixture, so
  no model or network is needed. A `sys.chat` card needs no model either:
  without an agent the host answers with a `host` notice.
- **In the OctoSense desktop:** rehearse the store path
  ([PUBLISHING §4](PUBLISHING.md#4-rehearse-the-store-path-locally)). To give
  the shell a kernel and a provider, see OctoSense
  [`docs/ai-services.md` § Run and test locally](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.md#run-and-test-locally).
  There your app's first `octos.*` call asks the person to allow its agent.
  The desktop can also publish sample Glance cards at startup
  ([OctoSense `desktop/README.md` § Flags and environment](https://github.com/OctoSense-org/OctoSense/blob/main/desktop/README.md#flags-and-environment)).
- **Rinx's mini-app host** also answers `octos.*`, for bundles a person
  imports into Rinx after review (a Matrix sign-in, Rinx's own assistant
  peer): [Rinx `examples/miniapps`](https://github.com/hagency-org/Rinx/tree/main/examples/miniapps).
  It is not the App Hub install path, and it refuses a bundle that declares
  an `agent`. Not run.

Two version differences matter when you test:

- `tools/octo check` runs the App Hub checkout beside this repository
  (`main`). The OctoSense shells pin an App Hub commit of their own (in
  OctoSense's `Cargo.toml` and `native-apps.json`), which can lag App Hub
  `main`. Both take the manifest rules from one crate,
  `octosense-app-contract` ([ADR 0005](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0005-app-contract.md)),
  which App Hub requires at version 1.7, published on crates.io.
  OctoSense `main` resolves 1.6.0 from crates.io; Host API v1 needs 1.6 or
  later.
  A manifest at the default `schema_minor` (0) still refuses unknown fields
  (**✓ run**: ``hub: manifest is not valid: unknown field `future_field`, expected one of `schema`, `id`, … `requires`, `schema_minor` ``),
  so do not use a field the shells' pin does not know.
- The `card-host` and `card-studio` you build for this repository (both
  App Hub tools) use the runtime that
  [`native-runtime.lock.json`](../native-runtime.lock.json) pins:
  OctoScript-Makepad `33dea2f1`, which pins OctoScript `2e37d9e6`. That
  runtime checks `sys.digest`, `model-copy` in text slots, `sys.chat` and
  `ChatEntry`. The shells use the same OctoScript, but
  `desktop-v0.1.0-beta.2` pins the older OctoScript-Makepad `aa80f72c`,
  which does not load a bundled card font.

OctoSense's own tests use fakes for the model, the toolbox, the app peers and
the kernel; see its
[architecture walkthrough § Tests](https://github.com/OctoSense-org/OctoSense/blob/main/docs/architecture-walkthrough.md#11-tests).
An app bundle cannot swap them in.

## One-shot model calls (`model`)

App Hub admits a second, narrower path: the `model` capability, served by the
OctoSense shells' `model` host service.

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

The gate admits it, and the shells' App Hub pin knows the name. `card-host`
has no `model` service: a call there answers
`no service answers "model" on this device` (**✓ run**).

### The `model` service

The service (`apps/ai-providers/host-service/src/complete/`, crate
`octosense-llm-service`, registered by `crates/ai-host` next to `llm`) has
this shape. ADR 0002 §14, "Direct one-shot model calls", keeps an app's own
agent (below) the main path for anything with tools, research, memory or
approvals.

| Method | Args | Answer (`r.data`) |
| --- | --- | --- |
| `model.complete` | `{task, input, schema, class?, allow_urls?}` | `{output, meta: {class, requested, attempts, usage: {input_tokens, output_tokens, estimated}, budget}}` |
| `model.budget` | – | the caller's `budget` alone |

- **`task`** (at most 4 KiB) says what to do; **`input`** (any JSON, at most
  32 KiB) is what to do it on, sent as data the model is told not to obey.
- **`class`:** `"fast"` (the default) or `"strong"`. The host tries the
  person's providers in their own order, those of that class first, and
  passes over one that fails. `meta.class` says which class answered.
- **`schema` is required** (a bounded JSON Schema subset, at most 8 KiB);
  `output` always validates against it. A reply that is not JSON, fails the
  schema, carries a URL or is over 16 KiB is retried once, then refused.
- **No URLs by default:** a reply with `http://`, `https://` or `www.` in it
  is refused, because replies end up as card data. Pass `allow_urls: true`
  only when the app extracts links.
- **A per-app budget**, kept by the host outside the app's jail: by default
  6 calls a minute, and 100 calls and 100,000 tokens a UTC day. `meta.budget`
  and `model.budget` report `{calls_today, calls_per_day, tokens_today,
  tokens_per_day, tokens_left, per_minute, resets_at}`.
- **Refusals** are `"<code>: <sentence>"`, with `code` one of `capability`,
  `no_provider`, `rate`, `budget`, `bad_request`, `invalid_output`,
  `too_large` or `provider`. The sentence may be shown to the person.
- The service also checks the app's own manifest for `model`, after the Card
  runner's capability check.

A call (not run; the literal syntax follows the Photos bundle,
space-separated lists and maps):

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

## Media and embeddings (`model`)

**Implemented in [OctoSense #368](https://github.com/OctoSense-org/OctoSense/pull/368), pending integration and release.**
This section describes source revision `95155ec0`; it does not claim these
methods exist in beta.2, `card-host`, or a released package. The owning
[media API reference](https://github.com/OctoSense-org/OctoSense/blob/95155ec035bd13c20de671689dc9e1aea0c8c698/apps/ai-providers/host-service/MEDIA.md) defines exact arguments, outputs, provider
routes, quotas and job lifetime; use it rather than inventing provider parameters.

- Grant `model`, declare the needed API versions and `host-api-v1` as shown
  in that reference, and use `runtime.describe` to check optional methods.
  `model.capabilities` reports configured route availability. An implemented
  method, a configured route and provider account entitlement are three
  separate checks; `host.has` proves only the app's capability grant.
- `model.image`, `model.audio` and `model.embeddings` return bounded image,
  MP3 or vector data. `model.video` starts a scoped asynchronous job;
  `model.video.status` polls it and `model.video.cancel` requests cancellation.
  Video handles belong to the app/account and current host process; a running
  remote job may refuse cancellation. Show that result honestly and do not
  blindly retry a possibly billable submission. Apps still need their own
  rendering/playback UI and handling for unavailable service or quota errors.
- Providers and credentials remain host-owned. Current adapters use OpenAI
  for images, speech and embeddings, and MiniMax for images, speech and H3
  video. A DeepSeek chat configuration or MiniMax M Plan subscription does
  not establish media API entitlement. Never collect a key in the app.
- [App Hub #147](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/147)
  admits the seven media aliases in `tools.json`. The owning app still needs
  `model` and `private_data: true`; generation, embeddings and cancellation
  require at least `act` risk, while capabilities and status are `read`.
  An admitted alias needs the matching host implementation before it runs.
- **Validation boundary:** the service has synthetic provider-protocol tests
  and a loopback HTTP transport test. Live paid providers, generated-media
  UX and phone execution remain **unverified**. A passing gate or configured
  chat account is not end-to-end media acceptance.

## An app's own agent

**available** in the App Hub gate and in the shells. The shell gives an app
that declares an agent (or `octos.*`, or ships `tools.json`) its own peer
once the person allows it, registers the bundle's tools with it, loads its
`AGENT.md` and skills as guidance for each turn, and lets the person talk to
it in the "Ask &lt;app&gt;" panel; the system agent can hand it work
([The system agent and app agents](#the-system-agent-and-app-agents)). The
shell delivers one event to store apps' agents ([below](#the-manifests-agent)).
Not yet: other events, schedules, and model selection from the manifest's
needs.

If you ship `tools.json`, declare the `agent` block and say so in the
listing and privacy text. If you want no assistant, do not ship
`tools.json`.

The contract is App Hub's
[PUBLISHING § The app's agent and tools](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-apps-agent-and-tools);
the complete worked example is App Hub's
[`crates/app-policy/tests/fixtures/news-agent`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/crates/app-policy/tests/fixtures/news-agent),
and the [connected reference apps](../examples/connected-apps/README.md)
show store apps' agents. The design behind it is OctoSense
[ADR 0002](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0002-event-driven-app-agents.md)
(Proposed; partly implemented), whose
[first slice](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0002-event-driven-app-agents.md#first-slice-news)
is News.

### What an app's agent gets today

What the shell registers on a script app's peer (`card.<app id>`), from
OctoSense `crates/shell/src/host_tools/`:

| Tool | Where it comes from | A store app | A system app (`os.*`) |
| --- | --- | --- | --- |
| `ask_user_question` (octos kernel tool) | `agent.tools: ["ask_user_question"]` | **yes** | **yes** (every system app with an agent) |
| `files.list`, `files.read`, `files.search` (read, no approval) | every peer whose agent has a workspace, on Unix platforms | **yes**: its account folder only, 128 KiB per read, 500 entries per listing, 100 matches per search | **yes** |
| Its own `tools.json` tools, `implemented_by: "host-service"` | run on the host service of the tool's `host_method` family, or of its namespace, with the app's identity, as its own `host.request` would; the family must be granted, or be the system app's own namespace | **yes**, through a `host_method` on a granted `github`, `gcalendar`, `gmail` or `glance`. Without `host_method`, a tool calls its namespace's service, which no capability grants: `summary.list` in `dev.example.summary` answers `not_granted`, `dev.example.summary was not granted the summary service`. A `github`, `gcalendar` or `gmail` call also needs an active connection: `Connect this app account first` | **yes**: News (`news.list`, `news.read`, `news.notify`), Mail (12 tools, such as `mail.peek` and `mail.propose_reply`), Calendar (`calendar.events`, `add_event`, `update_event`, `remove_event`, `notify`, `agenda`), and `photos.notify`, `maps.notify`, `youtube.notify`, `camera.notify` |
| Its own `tools.json` tools, `implemented_by: "app"` | the app's `app_tool` handler, in its open full app | on OctoSense `main` only, with `requires: ["script-tools-v1"]`; a call to a closed app answers `app_not_running`. `desktop-v0.1.0-beta.2` refuses them (`app_tool_unavailable`): `<tool> declares a script implementation, but this host does not support script tool dispatch` | the same |
| The generic host tools `ledger.read`, `ledger.write`, `net.fetch`, `storage.read`, `storage.write`, `card.render` | `agent.tools` | admitted by the gate, but no shell implements them | the same |
| Other apps' shareable tools (`mail.send`) | a dotted name in `agent.tools` | refused by the gate (`hub check`): `app <id> requests tool "mail.send", which this host does not offer contained apps` (**✓ run**) | granted by the shell's own policy; for example, Mail keeps `calendar.events`, `calendar.add_event` and `calendar.notify` |
| System toolbox tools | the `research` / `crawl` capabilities | **not yet** | with `toolbox-peers` ([below](#the-system-toolbox)); no system app declares `research` |
| `dev.run` (a shell command) | developer mode, for the apps it covers | development builds, and release builds launched with `--dev-grant-all`; never a store build | the same |

The relay caps every agent at 32 tool calls a turn and 1000 a day by default
(`crates/shell/src/host_tools/relay.rs`).

### Where the agent works: `storage`

App Hub's `storage` block (ADR 0004 §11) says what the agent sees:

| Field | Meaning |
| --- | --- |
| `storage.accounts` | `true`: data and one agent per account (Mail). Omitted or `false`: one `device` folder and one agent |
| `storage.agent_workspace` | `"account"` (the default): the agent's workspace is the account's folder, which its conversation reads through octos `read_parent`. `"none"`: no files, only what its tools return |
| `storage.cache_max_bytes` | the ceiling for the jail's `cache/` |

The account folder is `accounts/<account hash>/` inside the app's own
storage (`accounts/device/` for an app without accounts). The system apps
keep their data there (`let DATA = "accounts/device/"` in News, YouTube,
Photos, Maps and Camera) and refetchable caches in `cache/`, so their agents
can read it; data written at the top of the jail stays out of the agent's
reach. A store app following the same layout (`fs` paths under
`accounts/device/`) gets the same, by the same code. Unverified: a store
app's agent reading that folder was not run in a shell. `storage.external` is
for native apps and is refused in a script manifest. In-card chat
transcripts are kept in the same folder, under `chat/`
([below](#ai-written-text-and-in-card-chat-model-copy-syschat)).

The gate admits `"storage": {"accounts": false, "agent_workspace": "account"}`
(**✓ run**).

### The bundle

```text
bundle/
  manifest.json        "agent": { … } (below)
  tools.json           the app's own tools (next section)
  AGENT.md             named by agent.instructions
  skills/<name>/       SKILL.md + manifest.json, each named in agent.skills
  summary-card.splash  a glance card template its tool publishes
  main.splash, listing.json, assets/, screenshots/  as for any app
```

Every file is under the bundle digest, so the agent that runs is the one that
was reviewed. An undeclared `AGENT.md` or skill directory is refused (App Hub
`crates/app-policy/src/agent.rs`). A `tools.json` alone, without an `agent`
block, is admitted and still gives the app an agent, even though `hub check`
reports `agent none` (**✓ run**). The store in OctoSense `main` (not in any
release yet) discloses it: its privacy summary says the app offers the host's
Ask assistant after the person consents. The `desktop-v0.1.0-beta.2` store
says `Runs no assistant.`

### The manifest's `agent`

A store app's agent that passes the gate (**✓ run**):

1. Run `tools/octo new <dir> --platform macos --id dev.example.summary`.
2. Add this `agent` block, the next section's `tools.json` and template, an
   `AGENT.md` and the skill below.
3. Run `hub stamp <bundle>`, then `hub check <bundle> --allow-unsigned`:

```json
"capabilities": ["storage", "glance"],
"agent": {
  "profile": "read-only",
  "tools": ["ask_user_question"],
  "max_iterations": 6,
  "token_budget": 60000,
  "model": {
    "needs": ["tool_calling", "multilingual"],
    "tier": "standard",
    "local_only": false,
    "per_task": { "summary": { "needs": ["tool_calling", "reasoning"], "tier": "strong" } }
  },
  "instructions": "AGENT.md",
  "skills": ["daily-summary"]
}
```

```text
$ hub check <bundle> --allow-unsigned
  grants: capabilities {"glance", "storage"}, hosts {}, storage 16777216 bytes, agent read-only
```

The only refusal was the template's missing screenshot, which a real capture
fixes. The system apps News, Photos, Maps, YouTube and Camera declare a
smaller agent:

```json
"agent": { "profile": "read-only", "tools": ["ask_user_question"], "model": { "needs": ["tool_calling"] } }
```

Calendar adds `"instructions": "AGENT.md"`. Mail adds other apps' tools,
`AGENT.md`, skills, `background` and `triggers.events: ["mail.messages.new"]`.
With `"capabilities": ["storage", "glance"]` the smaller agent gives the same
`grants:` line (**✓ run**).

| Field | Rule (App Hub `crates/app-contract/src/manifest.rs`, `crates/app-policy/src/policy.rs`) | Enforced today |
| --- | --- | --- |
| `profile` | `read-only`, `workspace-write` or `workspace-write-never-ask`; there is no full access | gate; the shell does not read it (the peer's limits come from its workspace and its registered tools) |
| `tools` | the generic host tools `ledger.read ledger.write net.fetch storage.read storage.write card.render` (admitted, not implemented by any shell), and of the octos kernel's own tools only `ask_user_question`; anything else is refused. **✓ run**: `web_search` gives `[refused] agent: agent.tools names the octos kernel tool "web_search"; a contained app's agent may keep only ask_user_question` | gate; the shells hand `ask_user_question` to the peer |
| `max_iterations`, `token_budget` | model turns and tokens per request, clamped to 8 and 200,000 | gate (the `grants:` line shows only the profile) |
| `model.needs` | from `tool_calling vision long_context reasoning structured_output multilingual` | gate; the gate warns when an app has tools but no `tool_calling`. Not yet: the shell does not choose a model from it |
| `model.tier` | `fast`, `standard` (default) or `strong` | gate |
| `model.local_only` | app-wide; data must not leave the person's devices | gate (shareable tools must say `private_data: false`) |
| `model.per_task` | named tasks `[a-z_]{1,32}`, at most 8, that `AGENT.md` refers to | gate |
| no provider or model name | an unknown key is refused: ``hub: manifest is not valid: unknown field `provider`, expected one of `needs`, `tier`, `local_only`, `per_task` `` (**✓ run**) | gate |
| `background` | a request to run while the app is closed; requires `triggers` | gate; the shells wake a store app's agent for the Gmail event below |
| `triggers.schedule` | five-field cron, local time, at most 16 triggers | gate; not yet: no shell fires schedules |
| `triggers.events` | the app's own host-service events, in its namespace (`news.items.new`) | gate; the shells deliver the Gmail service's `<namespace>.new_message` and Mail's own `mail.messages.new`; other events not yet |
| `instructions`, `skills` | `AGENT.md` (text, 32 KiB, no HTML scripts, no `#!`); skill names `[a-z0-9_-]{1,64}`, at most 16 | gate; the shell loads both as guidance for each turn |

**The Gmail event.** An app granted `auth` and `gmail`, with
`background: true` and `triggers.events: ["<namespace>.new_message"]`
(`inbox.new_message` for an id ending in `.inbox`), gets one turn per new
message on its active account. The shell polls every 300 s while it runs in
the foreground or holds an Android background job, and only once the person
has allowed the app's agent. The first sync sets a baseline, so older mail
wakes nothing. The turn tells the agent the mail is untrusted input; the
agent reads the message with its own tool and records a decision, or
publishes a card. An event counts as handled only after a completed turn and
a recorded decision or publication; otherwise it stays pending. Sending
always needs the person's review on the host (`crates/shell/src/connected_events.rs`;
not run).

**Not yet: model choice.** ADR 0002 §3 has the host pick a model from the
person's providers that meets `needs` and `tier`; no shell does this yet.

### `AGENT.md` and skills

`AGENT.md` is the agent's role: what to do on each trigger, what matters in
the app's data, the rubric its output must meet, and its memory rules. A
skill is data only: `skills/<name>/SKILL.md` plus a `manifest.json` with
`name` (the directory), `version`, `description`, `uses` (each one of the
app's tools or in `agent.tools`) and optionally `prompts.include`; `.md`,
`.json` and `.txt` files only; executable fields (`tools`, `binaries`,
`mcp_servers`, `hooks`, …) are refused.

```json
{
  "name": "daily-summary",
  "version": "1.0.0",
  "description": "Write the short daily summary and put it on the glance screen.",
  "uses": ["summary.card.publish"]
}
```

A `uses` entry that is neither is refused (**✓ run**):
`[refused] skills: skill daily-summary uses summary.note.save, which is neither one of the app's tools nor in agent.tools`.

The shell loads the admitted, digest-checked `AGENT.md` and skill text as
guidance for each turn of the app's agent. They are not installed as kernel
skills and grant no tools.

## The app's tools and peer tools

What the app writes is **available**: `tools.json` in the bundle, checked by
the App Hub gate (`crates/app-policy/src/agent.rs`). This one publishes the
app's own card template through the shared `glance.publish` method:

```json
{
  "schema": 1,
  "tools": [
    {
      "name": "summary.card.publish",
      "description": "Put today's summary on the glance screen, using the app's own card template.",
      "input_schema": {
        "type": "object",
        "properties": {
          "card_id": { "type": "string", "pattern": "^[a-z0-9-]{1,32}$" },
          "title": { "type": "string", "maxLength": 80 },
          "template": { "type": "string", "enum": ["summary-card.splash"] },
          "initial": { "type": "object" }
        },
        "required": ["card_id", "title", "template", "initial"],
        "additionalProperties": false
      },
      "output_schema": { "type": "object", "properties": { "card_id": { "type": "string" } } },
      "risk": "act",
      "private_data": true,
      "implemented_by": "host-service",
      "host_method": "glance.publish"
    }
  ]
}
```

- `name` is `<namespace>.<tool>`; the namespace is the **last segment of the
  app id** (`dev.example.summary` → `summary`, `os.news` → `news`).
- `input_schema` and `output_schema` are both required (a tool without
  `output_schema` is refused: ``tools.json is not valid: missing field
  `output_schema` ``, **✓ run**). They use a JSON Schema subset (`type title
  description properties required items enum const default minimum maximum
  minLength maxLength minItems maxItems additionalProperties format
  pattern`); the input is an object. At most 64 tools, 1024-character
  descriptions.
- `implemented_by`: `host-service` (native code that holds data, network or
  secrets) or `app` (the app's script). The shell runs a `host-service` tool
  on a host service with the app's identity, as the app's own `host.request`
  would, never from a sheet (`may_prompt: false`). The service is the one its
  `host_method` names, or else its namespace's (`news.list` → `news`). The
  family must be granted, or be a system app's own namespace (`os.calendar`
  → `calendar`); otherwise the call answers
  `<app> was not granted the <family> service`. A store app's namespace,
  such as `summary`, is not a capability, so its host-service tools run only
  through `host_method`. The gate admits an `app` tool.
  `desktop-v0.1.0-beta.2` refuses every call to it:
  `<tool> declares a script implementation, but this host does not support script tool dispatch`.
  OctoSense `main` runs it in the open full app, for a manifest that declares
  `requires: ["script-tools-v1"]`
  ([HOST-API-V1 §5](HOST-API-V1.md#5-implement-a-declared-app-tool);
  OctoSense `crates/shell/src/host_tools/script_apps.rs`).
- `host_method` maps an ordinary app's tool to a reviewed shared-service
  method, as `summary.card.publish` → `glance.publish` above. App Hub admits
  only the methods in `SHARED_HOST_METHODS`
  (`crates/app-policy/src/agent.rs`): reads of `github`, `gcalendar` and
  `gmail`, `gmail.draft.open`, `gmail.draft.edit`, `gmail.event.decide`, and
  `glance.publish`, `glance.withdraw` and `glance.list`. The tool must
  request the method's capability, declare `private_data: true` and at least
  the method's risk. No provider write, review approval or account change is
  an alias. For `github`, `gcalendar` and `gmail` the shell adds the app's
  active connection to the arguments.
- An agent tool that publishes Glance cards should take only `template` +
  `initial`, as above, or an L0 `source` + `data`, never `script`: a script
  card runs under the app's own policy, so a turn misled by its input could
  publish arbitrary code. `desktop-v0.1.0-beta.2` publishes whatever the tool
  accepts; OctoSense `main` refuses `script` from agent tools
  ([Who may publish](#who-may-publish)).
- `background`, `shareable`, `private_data`, `confirm`, `outward`,
  `auto_approvable`: see
  [Approvals: `risk` and `confirm`](#approvals-risk-and-confirm).
- The shell's relay checks each call's arguments against `input_schema` (at
  most 64 KiB) and its result against `output_schema` (at most 256 KiB).
  octos needs an object `output_schema`, so a tool that answers a bare array
  cannot be offered as is.

The shell registers these tools with the app's peer over the octos
peer-tools protocol; your app never calls it. The model sees
`summary.card.publish` as `summary_card_publish`, and a call times out
after 30 s by default. To trace a call through the shell, see OctoSense's
[architecture walkthrough § Trace a tool to Rust code](https://github.com/OctoSense-org/OctoSense/blob/main/docs/architecture-walkthrough.md#7-trace-a-tool-to-rust-code).

### Approvals: `risk` and `confirm`

Whether a call needs the person comes from `risk` and `outward`; whose
surface asks comes from `confirm`; whether a standing rule may answer comes
from `auto_approvable` (App Hub PUBLISHING):

| `risk` | Runs |
| --- | --- |
| `read` (looks), `act` (changes the app's own state) | unattended |
| `destructive` (sends, posts, shares, buys, deletes) | only after the person approves |
| `act` with `outward: true` (reaches outside the device) | only after the person approves, like a destructive tool |

- `outward: true` on a `read` tool is refused (**✓ run**):
  `[refused] tools: summary.card.share is outward but its risk is read: a call that reaches outside the device is at least act`.
  On an `act` tool the gate warns:
  `[warning] tools: summary.card.share is outward: every call waits for the host's approval`.
- The gate warns on every destructive tool (**✓ run**):
  `[warning] tools: summary.card.publish is destructive: every call waits for the host's approval`.
- `auto_approvable: false` (default `true`): no standing rule ("allow for an
  hour") may approve it, so every call needs the person live. Use it for
  permanent deletion, payments, sharing outside the device, account and
  security changes. The shell takes whichever is stricter, its own rule or
  the tool's declaration.

| `risk: "destructive"` with | Person present | Person absent |
| --- | --- | --- |
| `confirm: "host"` (default) | the shell's approval sheet asks | the call waits as an approval request on the shell's sheet |
| `confirm: "app"` | the app's own confirmation sheet is the only confirmation | the call waits as an approval request on the shell's sheet |

Not yet for store apps: `confirm: "app"`. The gate allows it only on a tool
with `implemented_by: "app"` (or a native module's tool).
`desktop-v0.1.0-beta.2` refuses those tools, and OctoSense `main` refuses a
script tool call that needs the app's own confirmation:
`Script tools require host confirmation; confirm: app is not supported by this ABI`.
On a host-service tool the gate refuses it (**✓ run**):
`[refused] tools: summary.card.publish says confirm "app" but is implemented by the host service: …`.

Keep background tools to reads, and to writes the person reviews before
anything leaves the device: a background turn acts on untrusted input, such
as incoming mail.

The store shows the person one line per consequence, derived from the
manifest and `tools.json`, for example "Its assistant may work while the app
is closed, on a schedule; only if you allow it, and you can turn it off." and
"Can ask to mail.send: nothing of this runs until you approve it."

### What is enforced where

| Part | Status |
| --- | --- |
| Declarations (fields, sizes, names, schemas, risk, confirm) | **available**: the App Hub gate refuses or warns |
| Run-time approval (kernel): approve or deny | **available**: the kernel side and the shell's approval sheets, which offer Once, Always and Deny; approvals stay on those sheets, not in the app's conversation |
| The shell's approval router (`crates/shell/src/approvals/`) | **available**: developer mode, then `confirm: "app"` (the owning app's sheet), then `auto_approvable: false` (always the person), then the person's standing rules, then the live sheet. A rule's conditions fail closed on arguments it cannot read; the approve buttons wait until every argument row was on screen |
| An audit of every tool call | **available**: each call when it arrives and when it ends, with the caller, the owning app, the tool and a SHA-256 of the arguments (never the arguments), in `logs/tool-calls.jsonl` under the shell's home |
| In-app conversation with the app's agent | **available** in the shell's "Ask &lt;app&gt;" panel and in a Glance card's `sys.chat` |
| Memory in `app/<app>/acct-<hash>`, kept per account and erased with it | **available**; promotion by rule **not yet** (ADR 0002 §9). There is no manifest field; memory rules are prose in `AGENT.md` |
| Overlays by the system agent | **not yet** (ADR 0002 §11) |

## The system toolbox

The toolbox lets an app's agent search and read the web through the host,
inside the scope of the manifest's top-level `research` object. `research`
gives `workflow.run`, `workflow.fork`, `toolbox.search` and
`toolbox.web_read`; `crawl`, with `max_depth` and `max_pages` above 0 in the
scope, gives `toolbox.deep_crawl`. The agent never fetches a page itself:
the host runs each call within the app's scope and budget, keeps the
provenance, and writes results where the app cannot forge them.

- **Not yet for store apps.** The shells grant the toolbox only to system
  apps (`os.*`) that declare it, and only in builds with the
  `toolbox-peers` feature (the phone's default, not the desktop's)
  ([OctoSense#64](https://github.com/OctoSense-org/OctoSense/issues/64)). No
  system app declares `research`.
- A store app that declares `research` must still carry the top-level
  `research` scope object, or the gate refuses it (**✓ run**):
  `[refused] policy: app dev.example.summary requests research but declares no research scope; add a top-level "research" object (octos's scope; {} means no limits)`.

The scope's fields: App Hub
[PUBLISHING § The research scope](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-research-scope).
Templates and tools: OctoSense
[`docs/ai-services.md` § The system toolbox](https://github.com/OctoSense-org/OctoSense/blob/main/docs/ai-services.md#the-system-toolbox).

## Publishing to the Glance screen

### `glance.publish`, `glance.withdraw`, `glance.list`

The Glance screen is the desktop's Glance panel and the phone's feed. Its
service is **available** on OctoSense `main` (`crates/shell/src/glance.rs`):

| Method | Args | Answer |
| --- | --- | --- |
| `glance.publish` | `{card_id, source \| script \| template, data?, initial?, title, summary?, priority?, expires?, open?: {app, route?}, notify?, viewport?}` | `{card_id, replaced, expires_at}` |
| `glance.withdraw` | `{card_id}` | `{withdrawn}` |
| `glance.list` | – | `[{card_id, title, priority, published_at, expires_at}]`, the caller's own cards only |
| `glance.take_open` | – | `{route}`: the `open.route` of the card the person last opened for this app, once. Only for the app in the foreground |

- Give exactly one of:
  - `source`, an **L0 card** (L1 if its header declares it; L2 refused),
    realized against `data` (a map from the card's source names to values)
    and lowered through the Card runner's pipeline before it is stored. A
    `sys.chat` source must name the publishing app
    ([in-card chat](#ai-written-text-and-in-card-chat-model-copy-syschat)).
  - `script`, a **Splash program**, the same thing a script app's
    `main.splash` is (its own state, handlers, `host.request` calls and
    storage), with no `data`: the interactive card (a reply box, a form).
  - `template`, the name of a `.splash` file at the root of the app's own
    admitted bundle (`[A-Za-z0-9._-]`, at most 96 characters), with
    `initial`, the JSON object it starts from (at most 32 KiB). The host sets
    `initial.connection` to the app's active account (`device` for an app
    without accounts) and stores the card as an interactive script card, so
    the template and `initial` together must fit the 16 KiB `script` limit.
- Script and template cards run under the publishing app's own policy.
- `notify: true` also posts a notification (the phone's shade, the desktop's
  toast); `summary` (at most 200 characters) is its second line. On a
  desktop, clicking the toast opens that card in a card window; a new card
  also opens the Glance panel.
- **Limits:** `card_id` 1–64 of `[A-Za-z0-9._-]`; `title` at most 80
  characters; `source` (or `script`) at most 16 KiB; `data` at most 32 KiB as
  JSON; `priority` 0–100 (default 50); `expires` 60 s to 7 days (default
  24 h); 6 publishes per minute per app (a replace, and a card the L0 check
  refuses, both count). Cards are kept within a byte budget, 8 MiB per app
  and 32 MiB in all; when space runs short, older lower-priority cards
  retire first. The panel and the phone's feed scroll every retained card.
- **Identity:** the publisher is the caller, never an argument; publishing
  the same `card_id` replaces the card; `open.app` must be the caller's own
  app. Tapping a card opens it in a card window (on the phone, an expanded
  workspace). The desktop panel's open button, or a `sys.link` in the card,
  opens the app, which reads the card's `open.route` with
  `glance.take_open`.
- A card in the feed runs in its own isolate, under its publishing app's
  policy (a native app's card gets no app policy). It is a background
  surface: a host service it calls cannot raise a sheet there
  (`may_prompt: false`), and the host cancels its waiting requests when the
  card goes. A card opened in the foreground may raise host sheets, as the app
  itself may.

### Who may publish

- **Any contained app granted `glance`** may publish, list and withdraw its
  own cards. System apps get no exemption. Refusal:
  `<app> was not granted the glance capability`.
- A store app publishes from its script, or from an agent tool mapped to
  `glance.publish` with `host_method`; either way it needs the `glance`
  grant.
- **What an agent may publish depends on the build.** On
  `desktop-v0.1.0-beta.2`, an agent tool can publish all three kinds of card.
  OctoSense `main` (not in any release yet) checks every agent call that
  resolves to `glance.publish` before it runs. It refuses `script` with
  `Agents cannot publish executable Splash; choose an admitted template with initial data, or L0 source`.
  A template card needs a template name and an `initial` object, without
  `source` or `data`, and `source` must be valid L0, without executable code
  or L1 expressions. The app's own script can still publish all three kinds.
- Native modules publish too, and system apps' host services publish for
  their app's agent. Calendar's `calendar.notify` and `calendar.agenda` fill
  a fixed L0 card the service ships, and every other system app's
  `<namespace>.notify`, Mail's and News's included, fills the shell's notice
  card (`crates/shell/src/glance_notice.rs`). Mail's `mail.publish_card`
  publishes model-written cards, limited to L0.

A call from an app looks like this (the shape is `glance.rs`'s; not run,
since `card-host` registers no host services):

```splash
host.request("glance.publish", {
    card_id: "morning"
    title: "Morning summary"
    source: card_source
    data: {}
    expires: 43200
}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) }
})
```

Request `glance` only if the app publishes cards; the store shows
"Show cards on your glance screen".

## Cards bound to findings: `sys.digest`

The L0 source is **available**: the shells' runtime and this repository's
pin (OctoScript `2e37d9e6`) check it, and the shell resolves it when a card
is published (`crates/shell/src/glance_digest.rs`). A digest's `summary` and
its points' `text` and `label` are model text, shown marked AI-written
([below](#ai-written-text-and-in-card-chat-model-copy-syschat)).

Not yet for store apps: the host fills a digest only from the app's own
research runs, and store apps have no toolbox ([above](#the-system-toolbox)),
so a store app's digest always resolves to the empty record.

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
- The host reads the newest `toolbox/runs/<template>/<id>.json` for the
  app (under the host's directory, outside the app's jail), keeps only
  sources in the run's host-kept provenance, caps text (a summary of 800
  characters, 8 points of 400 characters, 8 sources) and expires a digest 48 h after its run started; the
  card's expiry is at most the digest's.

A complete card is OctoSense's
[`crates/shell/resources/glance/news-brief.card`](https://github.com/OctoSense-org/OctoSense/blob/main/crates/shell/resources/glance/news-brief.card).

## AI-written text and in-card chat: `model-copy`, `sys.chat`

**available** in the OctoSense shells: the L0 rules in OctoScript's
[`docs/ui-profile-l0.md`](https://github.com/OctoSense-org/OctoScript/blob/main/docs/ui-profile-l0.md)
§4.2 and §5.15, the kit's mark in OctoScript-Makepad, and the host side in
OctoSense (`crates/l0-chat`, `crates/shell/src/glance_chat.rs`). This
repository's pinned runtime has the same checker and mark
([Test it](#test-it)).

L0 has two rules for model text: one for words and one for actions.

**Words: model text may fill a text slot, and is drawn marked AI-written.**
Model text is a `copy` declared `class: model-copy`
(`copy gist { class: model-copy, en: "Rates held." }`), a model-written
field of a host source (`sys.digest`'s `summary` and a point's
`text`/`label`, a `sys.chat` entry's `text`, `sys.mail_draft`'s `to`,
`subject`, `body` and `suggestion_body`), or a `text` state such text was
written into (a draft: `event use { draft: set(copy.suggestion) }`). A text
slot is the `text` argument of `TextHero`, `TextTitle`, `TextBody`,
`TextRow`, `TextEyebrow`, `TextCaption`, `Band`, `Bubble`, `ChatEntry` and
`Field`; chip, tile and tab labels, avatars, glyphs and placeholders are
not. The kit draws a small sparkle and an `AI` eyebrow above the words, in
their own ink; the words stay plain text (no Markdown, HTML or links).

**Actions: model text never decides what runs.** It may not be an action's
payload or target, a source argument, a guard, a loop key, a control's
label, a component prop, a state initial or a value written to a host store.
The checker denies by default: every position but a text slot refuses it.

**In-card chat with the app's agent.** From OctoScript's `chat.card`
fixture:

```text
source convo sys.chat(app: "os.news", thread: "main", fields: [entries, id, role, text])

state draft { shape: text, initial: "" }

copy title { class: vocabulary, en: "ASK THE NEWS AGENT", zh: "问新闻助手" }
copy ask   { class: vocabulary, en: "Ask about today's news", zh: "问问今天的新闻" }

event send { convo: append($value), draft: clear }

view root  Surface(pad: .page) {
             Col(gap: 8) {
               TextEyebrow(text: copy.title)
               for m in convo.entries key m.id {
                 ChatEntry(text: m.text, role: m.role)
               }
               Field(text: draft, placeholder: copy.ask, on_commit: send, width: .fill)
             }
           }
```

- `app` is a literal and must be the **publishing app**: the shell refuses
  to publish a card that names another app, and such a card reads an
  `unavailable` transcript and writes nothing. `thread` is
  `[A-Za-z0-9_-]{1,64}` or a path into state.
- The source answers `status`, `count` and `entries`, rows
  `{id, role, text, at}`; `role` is `user`, `model` or `host` (a notice).
  `ChatEntry(text: m.text, role: m.role)` draws a bubble on the role's side;
  both arguments must come from the same row, and only `model` entries are
  marked AI-written.
- **The transcript is the host's.** Whatever the card's `data` puts under
  the source's name is replaced by the host's own transcript. A card's one
  write is `append`, accepted only with what the person typed in a `Field`
  and recorded as a `user` entry; the host then runs a turn in the app's
  conversation (the person's lane) and appends the reply as a `model` entry,
  or a `host` notice (`<app> has no agent to answer here yet.`) when the
  app has no agent or the person has not allowed it. A card can never write
  a `model` entry.
- **Limits** (`crates/l0-chat/src/lib.rs`): 4 KiB a message after trimming,
  one message per thread every 2 s and none while the agent is answering,
  the last 200 entries kept, a reply cut at 16 KiB.
- **Storage:** one owner-only file per thread in the app's account folder,
  `apps/<app>/accounts/<account hash>/chat/<thread>.json`, which is also the
  agent's workspace, so the agent can read the transcripts it is part of.
- **Where it is answered:** one live-card path answers in the desktop's card
  window (the one a card's toast opens; `glance_sheet.rs`), in the desktop
  panel's live cards and in the phone's expanded workspace; the phone's feed
  shows summaries only. AppCard, an opt-in native app that generates live
  cards, answers in its L0 cards with a `host` notice. App
  Hub's Card runner does not answer `sys.chat`, so a card app's own
  `page.card` cannot use it yet (not found in App Hub `crates/`).

A store app that wants this publishes such a card with `glance.publish`
(`source`), naming its own id, and declares an agent so the person can allow
it.

## Card levels and render-and-critique

The levels are defined in OctoScript's
[`docs/ui-profile-l0.md`](https://github.com/OctoSense-org/OctoScript/blob/main/docs/ui-profile-l0.md):

| Level | What it admits | For AI output |
| --- | --- | --- |
| **L0** | UI declarations only: data from cataloged `sys.*` sources the host resolves, no expressions, no calls | the default for generated and Glance cards |
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
(not run):

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

Not yet: an app's agent running this loop itself.

## Sources

- OctoSense `main`: `AGENTS.md`; `docs/ai-services.md`;
  `docs/adr/0002-event-driven-app-agents.md`, ADR 0004, ADR 0005 and
  `docs/adr/home/0004-system-apps-are-contained-script-apps.md`;
  `crates/app-peers` (`README.md`, `src/broker.rs`); `crates/ai-host/src/`
  (`lib.rs`, `contained.rs`, `native_agents.rs`, `toolbox_peers.rs`);
  `crates/shell/src/` (`agents.rs`, `apps.rs`, `agent_events.rs`,
  `connected_events.rs`, `questions/`, `approvals/`, `app_chat/`,
  `host_tools/` with `script_apps.rs`, `files.rs` and `relay.rs`,
  `glance.rs`, `glance_card.rs`, `glance_chat.rs`, `glance_digest.rs`,
  `glance_notice.rs`, `glance_routes.rs`); `crates/l0-chat`;
  `crates/toolbox`; `apps/ai-providers/host-service`, `apps/news/host-service`,
  `apps/mail/host-service`, `apps/calendar/host-service`; `apps/*/bundle/`.
- OctoSense-App-Hub `main`: `crates/app-contract/src/manifest.rs` and
  `policy.rs`; `crates/app-policy/src/services.rs`, `agent.rs`, `policy.rs`,
  `listing.rs`; `crates/appstore/src/services.rs`; `docs/PUBLISHING.md`;
  `docs/DEVELOPMENT.md`.
- OctoScript at the shells' pin: `docs/ui-profile-l0.md` §4.2, §5.14 and
  §5.15; `crates/octoscript-ui-l0/tests/fixtures/chat.card`.
- octos at the OctoSense pin:
  `docs/OCTOS_UI_PROTOCOL_CHANGE_REQUEST_UPCR_2026_035_PEER_HOST_TOOLS.md`.
- Rinx: `src/host/octos.rs`.
