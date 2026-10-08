# OctoScript App Design Flow

English | [简体中文](README.zh-CN.md)

The development harness for [OctoSense](https://github.com/OctoSense-org) apps.
It takes you, or a coding agent, from an idea (a text brief, a generated UX
image) to a contained app bundle that passes the
[OctoSense App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) gate
and is ready for a person to sign and submit.

It holds the rules for agents ([AGENTS.md](AGENTS.md)), step-by-step design
flows ([flows/](flows/README.md)), the developer docs ([docs/](docs/)), a
runnable app template ([templates/script-app](templates/script-app/README.md))
and worked examples ([examples/](examples/README.md)). Its CLI, `tools/octo`,
wraps App Hub's `card-host` and `hub` and never decides admission:
`tools/octo check` stamps an unsigned bundle, then passes on `hub check`'s
output and exit status.

It is for hackathon contestants and other developers building an OctoSense
app, and for the coding agents they work with. This repository was formerly
named *OctoScript-AppCard*.

## Contents

- [Hackathon: start here](#hackathon-start-here)
- [Connected apps: GitHub, Gmail and Google Calendar](#connected-apps-github-gmail-and-google-calendar)
- [Agents start here](#agents-start-here)
- [Status](#status)
- [Quick path](#quick-path)
- [`tools/octo`](#toolsocto)
- [Design flows](#design-flows)
- [What an app is](#what-an-app-is)
- [Containment rules](#containment-rules)
- [AI in your app](#ai-in-your-app)
- [Running an app](#running-an-app)
- [Headless testing: many apps, no screen](#headless-testing-many-apps-no-screen)
- [Publishing](#publishing)
- [Repository layout](#repository-layout)
- [Examples](#examples)
- [Contributing](#contributing)
- [Related repositories](#related-repositories)
- [License](#license)

## Hackathon: start here

This repository covers the technical path only. For the event itself
(rules, schedule, judging, how entries are handed in), see the
[Agentic App Hackathon](https://create.gosim.org/agenticapp26/) page and its
organizers. What a contestant needs from here:

| Topic | What to know |
| --- | --- |
| **Start** | The [Quick path](#quick-path) below: every step is a shell command. |
| **Machine** | The complete guide was run on Apple silicon macOS. App Hub's Windows and Linux CI also passes the native tools build and contract, policy, CLI and modal-input tests; native app interaction on those platforms is a separate check. Linux software-rendered frame capture remains unverified. See [platform evidence](docs/QUICKSTART.md#1-prerequisites) and the [Quick path](#quick-path). |
| **What an app can do** | Keep its own storage; make HTTPS requests to hosts it declares; show pictures and web pages; use the camera and the device's location; read and send mail through the host's `mail` service; publish Glance cards; call `model.complete`; and, in `desktop-v0.1.0-beta.2`, use a person's GitHub, Gmail or Google Calendar account through the host. [docs/CAPABILITIES.md](docs/CAPABILITIES.md) lists the capabilities; [docs/SCRIPT-API.md](docs/SCRIPT-API.md) covers the language and every API. |
| **What it cannot do** | Hold a password, API key or token, even in its own storage. Sign people in to its own backend on a released build: only OctoSense `main` has the host-run backend sign-in, with the backend declared in the app's manifest or registered by the host's operator ([CAPABILITIES](docs/CAPABILITIES.md#sign-in-to-your-own-backend), [App Hub#16](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/16)). Use media generation or embeddings on beta.2 or `card-host`: those services require the implementation in [OctoSense #368](https://github.com/OctoSense-org/OctoSense/pull/368), merged into `main`; compatible release pending ([media guide](docs/AI-SERVICES.md#media-and-embeddings-model)). Add a capability or host service (an App Hub and shell change), use the system-app-only `llm`, `news` and `calendar` capabilities or an `os.*` id, or ship native code. |
| **AI in the app** | Building an app needs no AI service, and `card-host` serves none, so make the app complete without one. See [AI in your app](#ai-in-your-app). |
| **Reference apps** | The three published [connected apps](#connected-apps-github-gmail-and-google-calendar). |
| **Demo** | The app in `card-host` (`tools/octo run`, driven over the remote bridge) and real screenshots from `tools/octo shot`. To show it inside OctoSense, with its host services, run the OctoSense desktop shell against a local catalog ([PUBLISHING §4](docs/PUBLISHING.md#4-rehearse-the-store-path-locally)). |
| **Submit to the App Hub** | Prepare the bundle with [docs/PUBLISHING.md](docs/PUBLISHING.md); then a person signs, tags and opens the issue as App Hub's [SUBMITTING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md) describes. A contest entry is not automatically an App Hub submission; the hackathon page says what the event needs. |
| **Test headless** | `tools/octo run … --hidden`: the window never appears, so an agent can test your app (and several apps at once, one `--port` each) without taking over your screen. See [Headless testing](#headless-testing-many-apps-no-screen). |
| **Check what your agent built** | [docs/MODEL-VALIDATION.md](docs/MODEL-VALIDATION.md): drive and capture the app natively, repair failures, and tie the evidence to the final source. |
| **Agentic app references** | [Email Action and Meeting Planner](examples/agentic-hackathon/README.md): fake email/calendar data, real app-agent entry points, a labeled offline fallback, review-before-action and native interaction tests. |
| **Stuck** | [QUICKSTART § Troubleshooting](docs/QUICKSTART.md#troubleshooting), [SCRIPT-API § Gotchas](docs/SCRIPT-API.md#gotchas), then App Hub's [Common refusals and how to fix them](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#common-refusals-and-how-to-fix-them). |

## Connected apps: GitHub, Gmail and Google Calendar

Three apps in the App Hub catalog work with a person's GitHub or Google
account through the host, without an OctoSense account. They are the
reference apps for a submission: each passed the gate and review, and the
catalog offers version 0.1.1 of each.

| App | App id | Source |
| --- | --- | --- |
| GitHub Notes | `org.octosense.samples.githubnotes` | [ymote/octosense-github-notes](https://github.com/ymote/octosense-github-notes) |
| Inbox Assistant | `org.octosense.samples.inbox` | [ymote/octosense-inbox-assistant](https://github.com/ymote/octosense-inbox-assistant) |
| Google Calendar | `org.octosense.samples.googlecalendar` | [ymote/octosense-google-calendar](https://github.com/ymote/octosense-google-calendar) |

Their anatomy (capabilities, tools, agent, Glance cards, protected writes) is
in [examples/connected-apps](examples/connected-apps/README.md); how they were
submitted is in App Hub's
[The three reference apps](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#the-three-reference-apps).

- They run in the OctoSense desktop shell, `desktop-v0.1.0-beta.2` or later
  (OctoSense `main`).
- Signing in needs provider registrations. On `desktop-v0.1.0-beta.2`, the
  host reads them only from `oauth/clients.json`, which its downloads do not
  include, so the host's operator supplies that file. A build from OctoSense
  `main` can compile a distributor's registrations in instead. Live use with
  the real providers is largely unverified
  ([CAPABILITIES § Limits](docs/CAPABILITIES.md#limits)).
- The person confirms every send and save in the host. A Gmail send needs a
  physical press on the host's review screen. On `desktop-v0.1.0-beta.2`, a
  GitHub or Calendar save needs approval on a host **sheet** (a panel the host
  draws over the app), and that sheet does not check for a physical press.
  OctoSense `main` requires a physical press for these saves too, but no
  release has it yet.
- Not yet: Google sign-in on Android, and installing any of them on a phone.
  The `desktop-v0.1.0-beta.1` store and every released phone build refuse the
  `auth` capability.
- `card-host` serves no connected accounts and lacks the native Markdown
  editor that GitHub Notes uses.

## Agents start here

Every step is a shell command or a file edit, so any coding agent, or a
person at a terminal, can follow it. `AGENTS.md` is the one source of truth;
`CLAUDE.md` and `GEMINI.md` only import it for agents that look for those
names.

`tools/octo` is unrelated to octos (the agent kernel inside OctoSense) and needs no AI service or API key.

Read these in order:

1. [AGENTS.md](AGENTS.md): the rules, the definition of done, and every point
   where you stop and ask a person.
2. [flows/README.md](flows/README.md): pick the flow for what you start from,
   then follow that flow's `FLOW.md` step by step.
3. [docs/QUICKSTART.md](docs/QUICKSTART.md) and
   [docs/SCRIPT-API.md](docs/SCRIPT-API.md): build and run the app with
   `tools/octo`; use only documented APIs (or ones you can cite from the
   runtime source or a system app).
4. [docs/PUBLISHING.md](docs/PUBLISHING.md): finalize the bundle, capture
   screenshots and pass the gate. A person then signs and submits it with
   App Hub's [SUBMITTING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md).

The human checkpoints (publisher keys and signing, publisher identity and
privacy text, platform claims, paid image generation, visual approval, the
release tag, submission) are listed in [AGENTS.md](AGENTS.md#how-to-work);
[flows/README.md](flows/README.md#every-flow-follows-the-same-contract)
explains the ones every flow shares. An agent never fabricates an approval,
a review result or a submission.

### App card UX skill

Use [octoscript-app-card-ux](skills/octoscript-app-card-ux/SKILL.md) when designing
or accepting a Glance app card. It adds a complete summary → expanded card →
full-workspace journey, shared Chat/Edit/Review state, keyboard and scrolling
checks, and a repair loop that preserves the designated model's authorship.
Its acceptance matrix distinguishes local behavior, actual agent execution,
external effects and visual approval; historical scores cannot pass a new card.

Any coding agent can read the skill directly alongside the selected flow.
For Codex discovery, copy the whole `skills/octoscript-app-card-ux` directory into
your Codex skills directory, then use it in a session that loads that catalog:
`Use $octoscript-app-card-ux to design and validate this app card.` Refresh the
installed copy when adopting later revisions. The skill does not provision a
phone's system/app agent or replace App Hub publishing gates. It adapts to the
chosen runtime, author and device; DeepSeek, MiniMax and OnePlus 6 are dated
examples, not requirements for every app.

## Status

Use `main` of each repository.

| Piece | State |
| --- | --- |
| The gate (`hub`) | App Hub `main`, app contract 1.7 (the manifest rules `hub` enforces), which admits the connected-account capabilities `auth`, `github`, `gmail` and `gcalendar`, the [Host API v1](docs/HOST-API-V1.md) declarations and the `wasm` capability. |
| `card-host` | App Hub `main`. It runs one bundle and serves no host services except `runtime` discovery. Build it as the [Quick path](#quick-path) shows. |
| The shells | OctoSense `main`; its latest desktop release is `desktop-v0.1.0-beta.2`. The desktop shell and the phone's Home run system and store apps; the desktop also serves connected accounts and app agents' host-service tools. |
| Submission | An issue on OctoSense-App-Hub, as App Hub's [SUBMITTING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md) describes. |
| Installing your own bundle on a phone | Not supported. See [Running an app](#running-an-app). |

[QUICKSTART §1](docs/QUICKSTART.md#1-prerequisites) lists the exact
revisions and the commands that set up the workspace.

## Quick path

Prerequisites ([QUICKSTART §1](docs/QUICKSTART.md#1-prerequisites)):

- Rust (stable, via rustup), with `~/.cargo/bin` on `PATH`.
- Python 3.9 or newer (no third-party packages needed for `tools/octo`;
  macOS's own `/usr/bin/python3` works).
- A graphical session: `card-host` renders a real 412x892-point window, even
  when `--hidden` keeps it off screen.
- One workspace directory holding this repository and its siblings, because
  App Hub's `Cargo.toml` patches Makepad and OctoScript to those paths:

  ```text
  <workspace>/
    OctoScript-App-Design-Flow/   this repository
    OctoSense-App-Hub/            hub, card-host, appstore
    makepad/                      OctoSense-org/makepad
    octoscript-makepad/           OctoSense-org/Octoscript-Makepad
    octoscript/                   OctoSense-org/Octoscript
  ```

Then create the workspace and, from this repository, build and use the tools:

```sh
# 0. The workspace: clone this repository and the App Hub side by side, then
#    let setup-native.py add makepad, octoscript and octoscript-makepad
mkdir octosense-ws && cd octosense-ws
git clone https://github.com/OctoSense-org/OctoScript-App-Design-Flow.git
git clone https://github.com/OctoSense-org/OctoSense-App-Hub.git
cd OctoScript-App-Design-Flow && python3 tools/setup-native.py

# 1. Build the two tools once (in the App Hub checkout)
(cd ../OctoSense-App-Hub && cargo build --release -p octosense-card-host -p octosense-app-hub)
tools/octo doctor                                        # finds hub and card-host; prints fixes if not

# 2. Create an app from the template
tools/octo new ~/apps/my-app --platform macos --id my-notes --name "My Notes"

# 3. Run it in a real window with the remote-control bridge
tools/octo run ~/apps/my-app/bundle --port 8141 --detach
#    Agents and scripts: add --hidden (headless: no window takes your screen,
#    and several apps can run at once, one --port each; QUICKSTART §4a)
curl -s "127.0.0.1:8141/snap?q=Notes"                    # what is on screen

# 4. Iterate: edit bundle/main.splash, then quit and run again
curl -s 127.0.0.1:8141/quit
tools/octo run ~/apps/my-app/bundle --port 8141 --detach

# 5. Capture a real screenshot, then check against the App Hub gate
tools/octo shot 8141 ~/apps/my-app/bundle/screenshots/01-main.png
curl -s 127.0.0.1:8141/quit
tools/octo check ~/apps/my-app/bundle                    # hub stamp + hub check

# 6. Publish: print the checklist, then follow docs/PUBLISHING.md
tools/octo package-help
```

If the build fails with `no variant … TextInputStateQuery`, see [QUICKSTART § The `card-host` build fails on `TextInputStateQuery`](docs/QUICKSTART.md#the-card-host-build-fails-on-textinputstatequery).

On Windows, run each `tools/octo` command as `python tools/octo …`. It finds
`hub.exe` and `card-host.exe` in the same places as on macOS
([QUICKSTART §2](docs/QUICKSTART.md#2-build-hub-and-card-host)). The native
tools build and CLI tests pass on Windows CI; the complete create/run/capture
sequence remains unverified there on the current pins.

What to expect:

- `new` prints `created …`, `bundle stamped` and
  `target platforms: macos; verify each before publishing`. List only the
  platforms you will test on; the listing claims them in the store.
- `run --detach` returns once `card-host` logs
  `card-host: my-notes 0.1.0 admitted — capabilities {"storage"}, …`, its
  remote bridge listens on your `--port`, and the first full frame is drawn
  (`ready: first frame drawn`); you can click or `shot` right away. If the
  port is already taken, it exits 1 and names the app holding it, with the
  `curl -s 127.0.0.1:<port>/quit` that stops it. Script errors appear in
  `<app>/.local-state/card-host.log` after `[SPLASH] eval:`.
- `check` on a fresh copy of the template is **refused** on purpose:
  `[refused] listing: screenshots/01-main.png is named by the listing but is not in the bundle`.
  It passes (`my-notes 0.1.0 — PASSED` plus the unsigned warning) once a real
  capture exists. Never add a placeholder image. `check` also notes the
  template's placeholder publisher text in `listing.json`, which a person must
  replace.

The full walk-through, with real output for every step, is
[docs/QUICKSTART.md](docs/QUICKSTART.md).

## `tools/octo`

Run `tools/octo <command> -h` for flags.

| Command | Does |
| --- | --- |
| `doctor` | Checks Python, looks for the App Hub checkout and cargo, finds `hub` and `card-host` (rejecting GitHub's unrelated `hub` CLI), checks the template, and prints how to fix what is missing. |
| `new <dir> --platform PLATFORM [--id ID] [--name NAME] [--system]` | Copies `templates/script-app` (`bundle/`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.gitignore`), sets id, name and version `0.1.0`, writes the `--platform` values into the listing, and stamps the bundle. `--platform` is required; repeat it for each platform you will test on. Ids are `[a-z0-9.-]{1,64}`; `os.*` needs `--system`. It refuses a reserved id, or one whose last segment is reserved, before it creates any file ([What an app is](#what-an-app-is)). |
| `run <bundle> [--port N] [--hidden] [--detach] [--system] [--no-stamp] [--app-data DIR] [--static PREFIX=DIR]` | Runs `card-host --bundle … --app-data … --allow-unsigned --stamp` with `MAKEPAD_REMOTE=<port>` (default 8141). Refuses a port that is already taken. `--detach` returns once the app is admitted, its bridge listens and the first frame is drawn. The app's jail (its private data directory) is `<app>/.local-state/<id>/`. |
| `shot <port> <out.png> [--settle S]` | Saves a PNG of the running window (`GET /g?raw=1`) once the app's widgets exist and two frames in a row match (at most `--settle`, 2 s by default). |
| `check <bundle> [hub check flags]` | `hub stamp`, then `hub check --allow-unsigned`; exits nonzero on a refusal. Passes other flags, such as `--catalog` or `--publisher-key`, to `hub check`. Does not restamp a signed manifest. A failed stamp returns its status at once and skips the gate. |
| `package-help` | Prints the publish checklist. |

`doctor` prints every place it looks for `hub` and `card-host`;
[QUICKSTART §2](docs/QUICKSTART.md#2-build-hub-and-card-host) lists the
order, including the `.exe` names on Windows.

## Design flows

A flow turns one kind of input into something OctoSense can run. Each
`FLOW.md` has a prerequisite check, then numbered steps, each with a command
and a pass condition, and marks the human checkpoints.

| Flow | You start from | You get | Step list |
| --- | --- | --- | --- |
| script-app | A text brief: what the app does, its screens, data, states and hosts | A contained script app bundle (`manifest.json`, `listing.json`, `main.splash`, `assets/`, real screenshots) that passes the gate | [flows/script-app/FLOW.md](flows/script-app/FLOW.md) |
| image-to-card | A generated UX image: one atlas of 8–12 screens of a service journey, or a single screen | Native L0 cards (`page.card`, `page.data.json`, `kit/`), extracted service cards, a card bundle, optionally WASM | [flows/image-to-card/FLOW.md](flows/image-to-card/FLOW.md) |
| kits/sketch | A licensed Sketch design kit | A **theme kit** (native L0 components and themes), not an app; the other flows consume it | [flows/kits/sketch/FLOW.md](flows/kits/sketch/FLOW.md) |

For a text brief, use script-app: it is the one path `tools/octo` automates
end to end. The image and Sketch flows need macOS, Python 3.12, their own
virtual environments and, for native capture, Makepad Studio; each `FLOW.md`
lists its prerequisites. Every app flow ends in the same hand-off (stamp,
check, run in `card-host`, screenshot, sign, submit), described in
[flows/README.md](flows/README.md#every-flow-follows-the-same-contract).

## What an app is

An OctoSense app is a contained bundle of at most 8 MiB. Only `bundle/` is
submitted; everything else in the app's repository stays out of it.

```text
my-app/                     the app's own Git repository
  AGENTS.md  CLAUDE.md      copied by tools/octo new; not submitted
  GEMINI.md  .gitignore     copied by tools/octo new; not submitted
  .gitattributes            copied by tools/octo new: bundle/** -text, so Git never rewrites the bundle
  BRIEF.md  build/          your brief, hub scan's review packet; not submitted
  .local-state/             card-host's jail and log; not submitted
  bundle/                   THE SUBMISSION
    manifest.json           id, name, version, capabilities, hosts, integrity
    listing.json            what the store shows
    main.splash             the program (a card app has page.card + kit/ instead)
    assets/icon.svg         the icon the listing names
    screenshots/01-main.png real captures, 1 to 8, named by the listing
```

**`manifest.json`** holds:

| Field | Holds |
| --- | --- |
| `schema`, `id`, `name`, `version` | Identity, with a new `version` for each release. The id's last segment, after its final `.`, must not be a name the host reserves (`notes`, `weather`, `terminal`, `rinx`, `system`, …): `com.example.notes` is refused, `my-notes` passes. `tools/octo new` refuses such an id before it creates any file, and the gate refuses it if you change the id later. |
| `capabilities` | The permissions the app asks for. |
| `network.hosts` | Bare host names; needs `net`. |
| `storage`, `compute`, `agent` | Optional requests, clamped to the host's ceilings; `hub check` prints the result as its `grants:` line. `storage.accounts: true` gives each account its own data folder and agent, instead of one shared `device` folder; `storage.agent_workspace` sets what the agent may read: its account's folder (the default) or nothing. |
| `integrity.bundle_blake3` | Written by `hub stamp`; `hub sign-manifest` adds the signature. |

For every field, see App Hub's
[The manifest](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-manifest).

**Capabilities** form a closed list defined by App Hub: 27 families, such as
`storage`, `net`, `images`, `web`, `camera`, `location`, `mail`, `glance`,
`model` and the connected-account `auth`, `github`, `gmail` and `gcalendar`,
plus 78 exact host-service names: 4 `octos.*` for the device's assistant, 45
`matrix.*` for Rinx, and 29 `palpo.*`, which no OctoSense shell serves yet.
Not requested means not granted, and the store shows the person one
plain-language line per capability before install. Ask for the least the app
needs. [docs/CAPABILITIES.md](docs/CAPABILITIES.md) says what each one
unlocks, which have no working path yet (`prompt`, `ledger.read`,
`clipboard`) and which only a system app can use;
[docs/AI-SERVICES.md](docs/AI-SERVICES.md) covers what the assistant
capabilities and an app's own agent do in OctoSense.

**`listing.json`** holds what the store shows: subtitle, description,
category, keywords, icon, screenshots, the platforms you actually tested, age
rating and the publisher (name, support, HTTPS privacy-policy URL). For valid
values, see App Hub's
[The listing](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-listing).

**`main.splash`** holds the program. Makepad Script evaluates it in a Splash
isolate, with no Rust compile step. It is a different language from
OctoScript L0 (`page.card`). A program declares top-level `let` state and
`fn`s, then one root widget. Start work with `start_timeout(0.05, || boot())`,
since `ui` is injected after the body runs. `{{assets}}` in the source is
replaced by the loopback origin that serves the bundle
(`http_resource("{{assets}}/thumbs/a.jpg")`).
[docs/SCRIPT-API.md](docs/SCRIPT-API.md) lists everything an app may call and
the gotchas that cost the most time.

## Containment rules

Each app runs in its own isolate under exactly the grants its manifest asks
for. The gate (`hub check`, the same code App Hub runs on submissions)
enforces most of this; App Hub's
[rules the gate enforces](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#rules-the-gate-enforces)
lists every check.

- **No secrets in apps.** No password, PIN or one-time-code field, no login
  form, and no API key or token in the bundle or the app's storage. The gate
  refuses `is_password: true` and password or one-time-code content types,
  and the runtime makes such a field inert. Sign-in happens on a host-owned
  **sheet**: a surface the host service draws over the app for what only the
  person may type.
- **Declare every host.** A `.splash` file may call only `https://` hosts
  listed in `network.hosts`; `images` and `web` add pictures and pages from
  any public `https://` host, but `net` still reaches only listed hosts.
  `http://`, `file://` and `../` are refused.
- **Only bundle files.** Allowed extensions are
  `.card .json .l0 .octoscript .splash .svg .png .jpg .jpeg .webp .ttf .otf .txt .md`,
  and an app that requests `wasm` may also carry up to 8 WebAssembly modules
  at `fns/<name>.wasm`. Any other file is refused, including macOS
  `.DS_Store`. The gate also refuses other scripts, archives, binaries,
  symlinks. Plain `.txt`/`.md` documentation may contain attribution or
  license URLs; agent guidance and structured resources still undergo their
  normal host/resource checks.
- **Host services for anything privileged.** An app calls
  `host.request("<family>.<method>", args, fn(r){…})`, and the family must be
  a granted capability. Mail is the worked example (`mail.accounts`,
  `mail.add_account`, `mail.list`, `mail.send`, …): the service raises its own
  sheet for the password and keeps it in the platform's secret store, outside
  every app's jail. `<family>.sheet.*` methods are accepted only from the
  sheet. A new service is a shell change, not a bundle:
  [docs/HOST-SERVICES.md](docs/HOST-SERVICES.md).
- **Store apps and system apps.** Ids under `os.` are reserved for system
  apps: the gate refuses them and no store installs one. System apps (News,
  Photos, Maps, Camera, Mail, AI providers in
  [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps))
  have the same bundle shape, ship with the shells and get higher ceilings
  (for example 64 MiB storage instead of 16 MiB). `tools/octo new --system`
  and `tools/octo run --system` exist for developing them; App Hub has no
  submission route for them. Everything else is a store app, distributed only
  through the signed App Hub catalog.

## AI in your app

OctoSense runs one octos agent kernel per shell, configured by the person in
the AI providers system app; an app never sees a key. The kernel runs the
**system agent** (the shell's own assistant, which the person talks to in
the system chat) and one **app agent** for each app that has one. On
`desktop-v0.1.0-beta.2` and OctoSense `main`, an app can do the following:

| An app can | How | In `card-host` |
| --- | --- | --- |
| Make a one-shot, schema-checked model call | `model` capability, `host.request("model.complete", …)`, within a daily budget that `model.budget` reports | `no service answers "model"` |
| Talk to the assistant from its own screens | the 4 `octos.*` capabilities, once the person allows the app's agent on a first-use sheet | `no service answers "octos"` |
| Have its own agent, which the person talks to directly (the shell's `Ask <app>` panel, an in-card chat, the app's own screens) and the system agent can hand work to | an `agent` block and `tools.json`: a tool marked `implemented_by: "host-service"` runs through a `host_method` from App Hub's reviewed list, on `github`, `gcalendar`, `gmail` or `glance`; on OctoSense `main` only, a tool marked `implemented_by: "app"` runs the app's own Splash handler while the app is open ([HOST-API-V1 §5](docs/HOST-API-V1.md#5-implement-a-declared-app-tool)); `AGENT.md` and skills are loaded as per-turn guidance | checked by `hub check` only |
| Publish cards to the Glance screen, with an in-card chat its agent answers and model-written text marked AI-written | `glance` capability, `glance.publish` (L0 `sys.chat`, `model-copy`) | `no service answers "glance"` |
| Run its agent in the background when new mail arrives | `agent.background: true` and `agent.triggers.events: ["<namespace>.new_message"]`, plus `auth` and `gmail`, as Inbox Assistant does | not available |

Image, speech, video and embeddings are implemented in [OctoSense #368](https://github.com/OctoSense-org/OctoSense/pull/368),
merged into `main`; compatible release pending. They are absent from beta.2 and `card-host`;
a compatible shell and an entitled host-configured provider are required.
Live paid-provider and device validation remain **unverified**. See
[media and embeddings](docs/AI-SERVICES.md#media-and-embeddings-model) for discovery,
app-agent aliases and the source-pinned API reference.

Agent tools that run the app's own code work only on OctoSense `main`, in no
release yet: the manifest must declare `requires: ["script-tools-v1"]`, and a
tool runs only while the app is open. `desktop-v0.1.0-beta.2` refuses
`implemented_by: "app"`, and on that build, a host-service tool can only call
an existing host service method. `llm` manages AI providers for system apps
only. A bundle that ships `tools.json` gets an app agent even without an
`agent` block, so say so in the listing. Read
[docs/AI-SERVICES.md](docs/AI-SERVICES.md) before you add an AI feature: it
has a verified call that handles "unavailable".

## Running an app

**Standalone, in `card-host`** (the development loop). `card-host` is App
Hub's reference contained host for one bundle. `tools/octo run` starts it with
Makepad's remote-control bridge on a local port, so a person or an agent can
drive the real window over HTTP (every route is a GET; coordinates are window
points, with y pointing down):

| Route | Does |
| --- | --- |
| `/snap` (`?q=` filters) | Lists widgets with their rects and text |
| `/d` | Prints the whole widget tree as text |
| `/click?x=&y=&wait=1` | Sends a real click |
| `/t?t=TEXT&wait=1` | Types into the focused input |
| `/k?k=down&c=ReturnKey` | Sends a key event |
| `/log?n=50` | Returns the last log lines |
| `/g?raw=1` | Returns a PNG of the window (what `tools/octo shot` saves) |
| `/quit` (or `/gq`, which captures every window, then quits) | Quits; always end with this |

Widgets built by `on_render` are listed in `/snap` and `/d` like any other;
content an app adds later, from a timer or a reply, appears once it is
drawn, so poll `/snap?q=` for it. `card-host` registers **no** host
services, so a Mail-style app gets `no service answers "mail" on this device`
there. `card-host` also refuses signed manifests: take screenshots before
signing.

**In the shells.** The OctoSense desktop shell and the phone's Home run apps
with App Hub's Card runner (the `card` module in App Hub's
`crates/appstore`), not with `card-host`; the Card runner applies the same
manifest policy. System apps are packed into the shell build from
OctoSense's `apps/`; store apps are installed from the App Hub store out of
the signed catalog. To try your own app in the desktop shell before it is
published, publish it into a local catalog with a throwaway trust anchor (a
test root key) and point the desktop shell's `OCTOSENSE_HUB` /
`OCTOSENSE_HUB_ANCHOR` at it; the shell's store installs and opens the app
([PUBLISHING §4](docs/PUBLISHING.md#4-rehearse-the-store-path-locally)).

**On a phone, today** ([QUICKSTART §9](docs/QUICKSTART.md#9-run-it-on-an-octosense-phone)):

- An arbitrary bundle cannot be side-loaded onto a stock OctoSense phone. The
  phone's store reads the catalog at App Hub's built-in address and trusts
  only the anchor compiled into the build; the `OCTOSENSE_HUB` / `OCTOSENSE_HUB_ANCHOR`
  overrides are environment variables the Android launcher does not set.
  Installing from a local catalog on a device is unsupported and unverified.
- The closest verified path is the desktop rehearsal above.
- `card-host`'s remote bridge is compiled out on Android, so phone testing
  does not use `tools/octo`.
- After publication, the app appears in every phone's store from the signed
  catalog, unless it declares `auth`: no released phone build accepts that
  capability.

## Headless testing: many apps, no screen

Makepad has a hidden-window mode, called headless here: the app still needs
the graphical session from the [Quick path](#quick-path), but its window is
**never shown or focused**, while the remote-control bridge (`/snap`,
`/click`, `/t`, `/g` screenshots) keeps working. Use it whenever an agent or a script drives an
app: it never takes over your screen or keyboard, and you can test several
apps, or several copies of one app, at the same time without them competing
for the display.

```sh
tools/octo run ~/apps/my-app/bundle     --port 8161 --hidden --detach
tools/octo run ~/apps/second-app/bundle --port 8162 --hidden --detach
curl -s "127.0.0.1:8161/snap?q=Button"        # each app answers on its own port
tools/octo shot 8161 first.png && tools/octo shot 8162 second.png
curl -s 127.0.0.1:8161/quit; curl -s 127.0.0.1:8162/quit
```

- `--hidden` sets `MAKEPAD_HIDE_WINDOWS=1`; any Makepad app honors it,
  including the OctoSense shells.
- One `--port` per app (`run` refuses a port that is already taken); one
  `--app-data` per copy when you run the same bundle twice.
- Screenshots are rendered by the app itself, so they are complete even with
  nothing on screen.
- **Scripted UI tests:** Makepad's [`makepad_test`](https://github.com/OctoSense-org/makepad/tree/main/libs/makepad_test)
  harness launches the app hidden, drives it through the same bridge, and
  saves a screenshot, the widget tree and the log when a test fails;
  `MAKEPAD_TEST_PARALLEL=1` runs tests (one hidden app each) concurrently.
  [QUICKSTART §4b](docs/QUICKSTART.md#4b-scripted-ui-tests-with-makepad_test)
  has the setup and a `card-host` example.

Verified on macOS (Apple silicon) with two hidden apps clicked at once. The
`makepad_test` example is **unverified** on the current pins; it passed with
an earlier App Hub and Makepad.

## Publishing

Publishing has two halves, owned by two repositories:

1. **Here.** [docs/PUBLISHING.md](docs/PUBLISHING.md) takes a working app to
   a bundle that is ready to sign: the final manifest and listing (no
   placeholders; the publisher fields are the publisher's to write), real
   screenshots from `tools/octo shot`, `tools/octo check` passing with only
   the unsigned warning, and the `hub scan` questions answered in writing.
   There are seven questions, or eight when the bundle ships `tools.json`,
   `AGENT.md` or skills. `tools/octo package-help` prints the checklist.
2. **App Hub.** [SUBMITTING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md)
   is the step-by-step submission a person follows: sign last, commit and
   tag, run `hub check` on a fresh clone of the tag without restamping, and
   open a `Submit <app id> <version>` issue.
   [PUBLISHING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md)
   is the reference for every gate rule and field.

A maintainer re-runs the gate and the scan on the exact bytes of your tag
and runs `hub publish`, which copies the bundle into App Hub and signs a new
catalog.

- Never open a pull request that edits App Hub's `catalog.json`, `index/` or
  `artifacts/`: only `hub publish` with App Hub's catalog key writes them.
- Never move a release tag. To change a published app, release a new version.
- The gate does not judge screenshots, listing text or the privacy policy; a
  reviewer does.

## Repository layout

| Path | What |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Rules, definition of done and reporting for coding agents |
| [flows/](flows/README.md) | The design flows: [script-app](flows/script-app/FLOW.md), [image-to-card](flows/image-to-card/FLOW.md), [kits/sketch](flows/kits/sketch/FLOW.md); shared code in [core/](flows/core/README.md) (policy, review, repair, gates; [NATIVE-INSTRUMENT.md](flows/core/NATIVE-INSTRUMENT.md) is the native test runbook) and [image-lib/](flows/image-lib/README.md) |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | The one path: build tools, create, run, edit, check, phone, publish |
| [docs/SCRIPT-API.md](docs/SCRIPT-API.md) | The Splash language and every API a contained app may call |
| [docs/CAPABILITIES.md](docs/CAPABILITIES.md) | Each capability: what it unlocks, what the person sees, the rules |
| [docs/HOST-SERVICES.md](docs/HOST-SERVICES.md) | `host.request`, sheets, "secrets are the host's", adding a service |
| [docs/RUST.md](docs/RUST.md) ([简体中文](docs/RUST.zh-CN.md)) | An app's own Rust code: Wasm functions, and the routes for device APIs, the network, files and native code |
| [docs/AI-SERVICES.md](docs/AI-SERVICES.md) ([简体中文](docs/AI-SERVICES.zh-CN.md)) | OctoSense's assistant (octos): what an app can use today, app agents and their tools, Glance cards and in-card chat (`sys.chat`) |
| [docs/MODEL-VALIDATION.md](docs/MODEL-VALIDATION.md) ([简体中文](docs/MODEL-VALIDATION.zh-CN.md)) | Checking what a coding agent built: native input and capture, review loops, repair |
| [docs/PUBLISHING.md](docs/PUBLISHING.md) | From a working app to a bundle ready to sign: final manifest and listing, screenshots, the gate, the local store rehearsal and the human checkpoints |
| [docs/CODE-WALKTHROUGH.md](docs/CODE-WALKTHROUGH.md) | How `tools/octo`, App Hub and the OctoSense shell connect, traced through one request |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | One meaning per term |
| [docs/NATIVE-WORKSPACE.md](docs/NATIVE-WORKSPACE.md), [docs/l0/](docs/l0/) | Sibling-source setup for the native runtime; L0 card examples |
| [templates/script-app/](templates/script-app/README.md) | The runnable template `tools/octo new` copies ("My Notes") |
| [templates/card-app/](templates/card-app/README.md) | Pointer to the card-app path |
| [examples/](examples/README.md) | Worked image-to-card projects, and the three connected reference apps in [examples/connected-apps](examples/connected-apps/README.md) |
| [tools/octo](tools/octo) | The CLI above |
| `tools/setup-native.py` | Prepares the pinned OctoScript-Makepad runtime ([native-runtime.lock.json](native-runtime.lock.json)) beside this repository |
| `tools/image-to-appcard-flow.sh`, `tools/beauty-pipeline.sh`, `tools/beauty-studio.sh` | Entry points for the image-to-card and kit pipelines |
| `tools/check-links.py` | Checks that relative Markdown links resolve (run in CI) |

## Examples

These examples are reference journeys built with the image-to-card flow,
contained apps built with the script-app flow, and Android-authored prototype
archives. Each keeps its source, validation evidence and current limits
alongside it.

| Example | Surfaces | What it is |
| --- | --- | --- |
| [Agentic hackathon apps](examples/agentic-hackathon/README.md) | Native Splash / app agents | Email Action and Meeting Planner with fictional data, reviewed local actions and native tests |
| [Aircon](examples/aircon/README.md) | Native cards / WASM | A purchase-to-installation journey: 12 screen states, 14 service-card variants |
| [School](examples/school/README.md) | Native cards / WASM | School notice, calendar and payment |
| [Health](examples/health/README.md) | Native cards / WASM | A fictional health-check booking |
| [Reunion](examples/reunion/README.md) | Native cards / WASM | Reunion planning, RSVP and payment |
| [Calendar](examples/calendar/README.md) | Native cards / browser preview + sync server | One calendar on two devices, with a SQLite-backed sync server |
| [Android-authored card prototypes](examples/android-a2app-card-templates/README.md) | AppStudio on Android; glance / expanded / full app | Two model-authored six-family collections: each 4.5/5 overall offline prototype, 4.4/5 visual; exact source replay and native evidence. |

For a script app, the complete examples are the
[connected apps](#connected-apps-github-gmail-and-google-calendar), the
first-party bundles in
[OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps)
(`apps/<name>/bundle/`), and [templates/script-app](templates/script-app/README.md).

## Contributing

- Branch from `main` and open a pull request; CI must pass.
- CI runs `python tools/check-links.py` (relative links in tracked Markdown
  must resolve), and runs the `tools/test_*.py` tests (the `tools/octo`
  starter, its binary search and the example contracts) on Windows, Linux and
  macOS. On macOS it also prepares the native runtime with
  `tools/setup-native.py` and runs the flow, core, Sketch and maintenance
  unit tests (see [.github/workflows/ci.yml](.github/workflows/ci.yml)).
- Keep the docs honest: every command in them was run, and anything not run
  is marked **unverified**. When the runtime or `hub` disagrees with a doc,
  fix the doc or report the gap with a reproduction.
- Changes to the runtime, the gate, the shells or the system apps belong in
  their own repositories (below), not here.
- Do not commit purchased design assets, keys, `.local-state/` or local logs.

## Related repositories

| Repository | Role |
| --- | --- |
| [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) | The signed catalog, the gate, `hub`, `card-host`, the store, the Card runner and the submission route |
| [OctoSense](https://github.com/OctoSense-org/OctoSense) | The shell and what ships in it: the desktop shell (`desktop/`), the phone shell, Home (`phone/`, as a Home app or in the ROM image built by `rom/`), and the first-party apps with their host services (`apps/`). Formerly OctoSense-Desktop, OctoSense-ROM and OctoSense-System-Apps. |
| [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps) | First-party apps (News, Photos, Maps, Camera, Mail, AI providers) and their host services (`mail`, `llm`) |
| [OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard) | The AppCard assistant (`octos-app`, opt-in in the shells with `--features app-appcard`) |
| [OctoSense-org/makepad](https://github.com/OctoSense-org/makepad), [OctoScript](https://github.com/OctoSense-org/Octoscript), [OctoScript-Makepad](https://github.com/OctoSense-org/Octoscript-Makepad) | Makepad: Splash isolates and widgets. OctoScript: the L0 parser and checker. OctoScript-Makepad: the L0 renderer. |

## License

Apache-2.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE).
