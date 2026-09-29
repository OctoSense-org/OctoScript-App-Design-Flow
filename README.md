# OctoScript App Design Flow

English | [简体中文](README.zh-CN.md)

The development harness for [OctoSense](https://github.com/OctoSense-org) apps.
It takes you, or a coding agent, from an idea (a text brief, a generated UX
image) to a contained app bundle that passes the
[OctoSense App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) gate
and is ready for a person to sign and submit.

It holds the rules for agents ([AGENTS.md](AGENTS.md)), step-by-step design
flows ([flows/](flows/README.md)), the developer docs ([docs/](docs/)), a
runnable app template ([templates/script-app](templates/script-app/README.md)),
worked examples ([examples/](examples/README.md)) and `tools/octo`, a small CLI
over the App Hub's real `card-host` and `hub` binaries. It never decides
admission itself: `tools/octo check` prints exactly what `hub check` prints.

Who it is for: hackathon contestants and other developers building an
OctoSense app, and the coding agents they work with.

Formerly *Octoscript-AppCard*. The AppCard assistant runtime and
the first-party apps moved to OctoSense-System-Apps and, since 2026-09-27,
live in [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps)
(OctoSense-System-Apps is archived and no longer public).

## Contents

- [Hackathon: start here](#hackathon-start-here)
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

## Hackathon: start here

This repository covers the technical path only. For the event itself
(rules, schedule, judging, how entries are handed in), see the
[Agentic App Hackathon](https://create.gosim.org/agenticapp26/) page and its
organizers; none of that is decided here. What a contestant needs from here:

| | |
| --- | --- |
| **Start** | The [Quick path](#quick-path) below: on 2026-09-26 a new app went from an empty directory to `— PASSED` in about 10 minutes (clones 1.5 min, setup 20 s, first build 1 min on an Apple silicon Mac), most of it writing the app. Every step is a shell command, so any coding agent (or none) can run it. |
| **Machine** | macOS on Apple silicon is the verified platform. Windows and Linux are unverified. Rust stable (rustup), Python 3.9+ (macOS's own `/usr/bin/python3` works), git, a graphical session, about 3 GB free (the clones take about 1.9 GB, 1.3 GB of it this repository, where `--depth 1` is fine; the build about 1 GB), and network access for the first build. |
| **What an app can do** | Its own storage, HTTPS requests to hosts it declares, pictures and web pages, camera, location, and Mail through a host service: [CAPABILITIES](docs/CAPABILITIES.md). The language and every API: [SCRIPT-API](docs/SCRIPT-API.md). Complete examples: the [System Apps](https://github.com/OctoSense-org/OctoSense/tree/main/apps) (News, Photos, Maps, Camera, Mail) and the [template](templates/script-app/README.md). |
| **What it cannot do** | Hold a password, key or token; invent a capability or a host service (those are App Hub and shell changes); use `llm` or an `os.*` id (system apps only); be side-loaded onto a phone. `card-host` provides no host services, so a Mail-style app shows `no service answers` there. |
| **AI in the app** | Building needs none, with any coding agent or none. On the device, a store app cannot ask the assistant or a model yet: the `octos.*` capabilities pass the gate, but no OctoSense shell serves them to apps (`no service answers "octos"`). What works, what is planned, and a verified example that handles "unavailable": [docs/AI-SERVICES.md](docs/AI-SERVICES.md). |
| **Demo** | The app in `card-host` (`tools/octo run`, driven over the remote bridge) and real screenshots from `tools/octo shot`. To show it inside OctoSense, run the OctoSense desktop shell against a local catalog ([PUBLISHING §4](docs/PUBLISHING.md#4-rehearse-the-store-path-locally)). |
| **Submit to the App Hub** | [Publishing](#publishing): `tools/octo check` passes, `hub scan` answered, then a person signs and opens a `Submit <app id> <version>` issue on [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub/issues). A contest entry is not automatically an App Hub submission; ask the organizers what they need. |
| **Test headless** | `tools/octo run … --hidden`: the window never appears, so an agent can test your app (and several apps at once, one `--port` each) without taking over your screen. [Headless testing](#headless-testing-many-apps-no-screen). |
| **Stuck** | [QUICKSTART § Troubleshooting](docs/QUICKSTART.md#troubleshooting), then [SCRIPT-API § Gotchas](docs/SCRIPT-API.md#gotchas). |

## Agents start here

> **Any coding agent, or none.** These instructions work the same for Codex, Claude Code, Cursor, Gemini CLI, GitHub Copilot or a person at a terminal: every step is a shell command or a file edit, and nothing here needs a particular agent, model or vendor. `AGENTS.md` is the one source of truth; `CLAUDE.md` and `GEMINI.md` only import it for agents that look for those names.

`tools/octo` is this repository's own Python CLI around App Hub's `hub` and `card-host`. It is unrelated to octos (the agent kernel inside OctoSense) and needs no AI service or API key.

Read these in order (the same order the
[OctoSense org profile](https://github.com/OctoSense-org) gives):

1. [AGENTS.md](AGENTS.md): the rules, the definition of done, and every point
   where you stop and ask a person.
2. [flows/README.md](flows/README.md): pick the flow for what you start from,
   then follow that flow's `FLOW.md` step by step.
3. [docs/QUICKSTART.md](docs/QUICKSTART.md) and
   [docs/SCRIPT-API.md](docs/SCRIPT-API.md): build and run the app with
   `tools/octo`; use only documented APIs (or ones you can cite from the
   runtime source or a System App).
4. [docs/PUBLISHING.md](docs/PUBLISHING.md), with the App Hub's
   [publishing contract](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md):
   stamp, screenshot, check, sign and submit.

The human checkpoints (publisher keys and signing, publisher identity and
privacy text, platform claims, paid image generation, visual approval,
submission) are listed in [AGENTS.md](AGENTS.md) and
[flows/README.md](flows/README.md#every-flow-follows-the-same-contract). An
agent never fabricates an approval, a review result or a submission.

## Status

The work script apps depend on merged on 2026-09-26; use `main` of each
repository.

| Piece | State |
| --- | --- |
| Script-app gate, scan and `os.` id check in `hub` | On App Hub `main` ([OctoSense-App-Hub#4](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/4), merged as `0d36f50b`). The docs here were verified against its pre-merge commit `79a2c4f` and re-run end to end on `main` on 2026-09-26. |
| Contained script apps and host services in the runtime | On makepad `main` ([OctoSense-org/makepad#30](https://github.com/OctoSense-org/makepad/pull/30), merged as `cd812acd`; now at `3afef545`), selected by Octoscript-Makepad `a7693615`, the release `native-runtime.lock.json` pins. Verified before the merge at `d94e5e6`. |
| System and store apps in the shells | On `main` of [OctoSense](https://github.com/OctoSense-org/OctoSense), in the desktop shell and the phone's Home (landed as OctoSense-Desktop [#36](https://github.com/OctoSense-org/OctoSense/pull/36) and OctoSense-ROM #18, before the repositories merged). |
| Submission route | An issue on OctoSense-App-Hub (below), as App Hub's [PUBLISHING § Submitting](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#submitting) describes. The index repository and release action it mentions do not exist yet. |
| Installing your own bundle on a phone | Not supported. See [Running an app](#running-an-app). |

[docs/QUICKSTART.md §1](docs/QUICKSTART.md#1-prerequisites) lists the exact
revisions and the commands that set up the workspace.

## Quick path

Prerequisites ([QUICKSTART §1](docs/QUICKSTART.md#1-prerequisites)):

- Rust (stable, via rustup), with `~/.cargo/bin` on `PATH`.
- Python 3.9 or newer (no packages needed for `tools/octo`; macOS's own
  `/usr/bin/python3` 3.9 works).
- A graphical session: `card-host` opens a real 412x892-point window, even
  when an agent drives it.
- One workspace directory holding this repository and its siblings, because
  the App Hub's `Cargo.toml` patches Makepad and Octoscript to those paths:

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
tools/octo new ~/apps/my-app --id my-notes --name "My Notes"

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

# 6. Publish: print the checklist and follow docs/PUBLISHING.md
tools/octo package-help
```

What to expect:

- `new` prints `created …` and `bundle stamped`.
- `run --detach` returns once `card-host` logs
  `card-host: my-notes 0.1.0 admitted — capabilities {"storage"}, …`, its
  remote bridge listens on your `--port`, and the first full frame is drawn
  (`ready: first frame drawn`); you can click or `shot` right away. If the
  port is already taken it exits 1 and names the app holding it, with the
  `curl -s 127.0.0.1:<port>/quit` to stop it. Script
  errors appear in `<app>/.local-state/card-host.log` after `[SPLASH] eval:`.
- `check` on a fresh copy of the template is **refused** on purpose:
  `[refused] listing: screenshots/01-main.png is named by the listing but is not in the bundle`.
  It passes (`my-notes 0.1.0 — PASSED` plus the unsigned warning) once a real
  capture exists. Never add a dummy image. `check` also notes the template's
  placeholder publisher text in `listing.json`, which a person must replace.

The full walk-through, with verified output for every step, is
[docs/QUICKSTART.md](docs/QUICKSTART.md).

## `tools/octo`

Python 3.9+, no third-party packages. Run `tools/octo <command> -h` for flags.

| Command | Does |
| --- | --- |
| `doctor` | Checks Python, finds `hub` and `card-host` (rejecting GitHub's unrelated `hub` CLI), checks the template, and prints how to fix what is missing. |
| `new <dir> [--id ID] [--name NAME] [--system]` | Copies `templates/script-app` (`bundle/`, `AGENTS.md`, `.gitignore`), sets id, name and version `0.1.0`, and stamps the bundle. Ids are `[a-z0-9.-]{1,64}`; `os.*` needs `--system`. |
| `run <bundle> [--port N] [--hidden] [--detach] [--system] [--no-stamp] [--app-data DIR] [--static PREFIX=DIR]` | Runs `card-host --bundle … --app-data … --allow-unsigned --stamp` with `MAKEPAD_REMOTE=<port>` (default 8141). Refuses a port that is already taken. `--detach` returns once the app is admitted, its bridge listens and the first frame is drawn. The app's jail is `<app>/.local-state/<id>/`. |
| `shot <port> <out.png> [--settle S]` | Saves a PNG of the running window (`GET /g?raw=1`) once the app's widgets exist and two frames in a row match (at most `--settle`, 2 s). |
| `check <bundle> [hub check flags]` | `hub stamp`, then `hub check --allow-unsigned`; exits nonzero on a refusal. Does not restamp a signed manifest. |
| `package-help` | Prints the publish checklist. |

Binaries are found in `$OCTO_HUB` / `$OCTO_CARD_HOST`, then
`$OCTOSENSE_APP_HUB/target/release`, `$CARGO_TARGET_DIR/release`,
`$OCTOSENSE_APP_HUB/../target/release`, `../OctoSense-App-Hub/target/release`,
`../target/release`, then `PATH`.

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
virtual environments and, for native capture, Makepad Studio; each FLOW.md
lists its prerequisites. Every app flow ends in the same hand-off (stamp,
check, run in `card-host`, screenshot, sign, submit), described in
[flows/README.md](flows/README.md#every-flow-follows-the-same-contract).

## What an app is

An OctoSense app is a small, contained bundle. Only `bundle/` is submitted;
everything else in the app's repository stays out of it.

```text
my-app/                     the app's own git repository
  AGENTS.md  .gitignore     copied by tools/octo new; not submitted
  BRIEF.md  build/          your brief, hub scan's review packet; not submitted
  .local-state/             card-host's jail and log; not submitted
  bundle/                   THE SUBMISSION
    manifest.json           id, name, version, capabilities, hosts, integrity
    listing.json            what the store shows
    main.splash             the program (a card app has page.card + kit/ instead)
    assets/icon.svg         the icon the listing names
    screenshots/01-main.png real captures, 1 to 8, named by the listing
```

**`manifest.json`**: `schema`, `id`, `name`, `version` (new for every
release), `capabilities` (the permissions it asks for), `network.hosts`
(bare host names, with `net`), and `integrity.bundle_blake3`, written by
`hub stamp` (plus a signature after `hub sign-manifest`). Optional requests
(`storage.max_bytes`, `compute.*`, `agent`) are clamped to the host's
ceilings; `hub check` prints the resulting `grants:` line.

**Capabilities** form a closed list defined by the App Hub: `storage`, `net`,
`images`, `web`, `camera`, `microphone`, `library`, `location`, `mail`,
`llm`, `news`, `glance`, `model`, `prompt`, `ledger.read`, `clipboard`, plus 49 exact
host-service names (four `octos.*` for the device's assistant, 45 `matrix.*`
for Rinx). Not requested means not granted,
and the store shows the person one plain-language line per capability before
install. Ask for the least the app needs. What each unlocks, which have no
working path yet (`prompt`, `ledger.read`, `clipboard`) and which only a
system app can use (`llm`): [docs/CAPABILITIES.md](docs/CAPABILITIES.md).
What the assistant capabilities do today (nothing yet, in OctoSense):
[docs/AI-SERVICES.md](docs/AI-SERVICES.md).

**`listing.json`**: subtitle, description, category, keywords, icon,
screenshots, the platforms you actually tested, age rating and the publisher
(name, support, https privacy-policy URL). Valid values:
[docs/PUBLISHING.md §3.2](docs/PUBLISHING.md#32-finalize-the-listing).

**`main.splash`**: the program, in Splash (OctoScript), interpreted with no
compile step. Top-level `let` state and `fn`s, then one root widget; start
work with `start_timeout(0.05, || boot())`, since `ui` is injected after the
body runs. `{{assets}}` in the source is replaced by the loopback origin that
serves the bundle (`http_resource("{{assets}}/thumbs/a.jpg")`). Everything an
app may call, and the gotchas that cost the most time:
[docs/SCRIPT-API.md](docs/SCRIPT-API.md).

## Containment rules

Each app runs in its own isolate under exactly the grants its manifest asks
for. The gate (`hub check`, the same code the hub runs) enforces most of this;
[docs/PUBLISHING.md §2](docs/PUBLISHING.md#2-the-rules-the-gate-enforces)
lists every check.

- **No secrets in apps.** No password, PIN or one-time-code field, no login
  form, no API key or token in the bundle. The gate refuses
  `is_password: true` and password or one-time-code content types, and the
  runtime makes such a field inert. Sign-in happens on a host-owned **sheet**.
- **Declare every host.** A `.splash` file may reach only `https://` hosts
  listed in `network.hosts` (unless the app is granted `images` or `web`).
  `http://`, `file://` and `../` are refused.
- **Only bundle files.** Allowed extensions are
  `.card .json .l0 .octoscript .splash .svg .png .jpg .jpeg .webp .ttf .otf .txt .md`;
  no scripts, archives, binaries or symlinks; 8 MB at most.
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
  and `tools/octo run --system` exist for developing them. Everything else is
  a store app, distributed only through the signed App Hub catalog.

## AI in your app

OctoSense runs one octos agent kernel per shell, configured by the person in
the AI providers system app; keys never reach an app. **A contained app
cannot use it yet**: the gate accepts the four `octos.*` capabilities, but no
OctoSense shell serves them to apps, and `card-host` serves no host services.
`llm` is provider management for system apps only, and the one-shot `model`
capability (App Hub #24) has no service in any shell yet. An app's own agent
(`tools.json`, `AGENT.md`, skills, triggers) is admitted by App Hub `main` and
planned in OctoSense's ADR 0002, but nothing runs it yet. Build apps that are
complete without AI, and read [docs/AI-SERVICES.md](docs/AI-SERVICES.md)
before adding an AI feature: the exact names, a verified call that handles
"unavailable", what the person sees, the errors, and the planned route.

## Running an app

**Standalone, in `card-host`** (the development loop). `card-host` is App
Hub's reference contained host for one bundle. `tools/octo run` starts it with
Makepad's remote-control bridge on a local port, so a person or an agent can
drive the real window over HTTP (all GET, window points, y down):

| Route | Does |
| --- | --- |
| `/snap` (`?q=` filters) | Widgets with rects and text |
| `/d` | The whole widget tree as text |
| `/click?x=&y=&wait=1` | A real click |
| `/t?t=TEXT&wait=1` | Types into the focused input |
| `/k?k=down&c=ReturnKey` | A key event |
| `/log?n=50` | The last log lines |
| `/g?raw=1` | A PNG of the window (what `tools/octo shot` saves) |
| `/quit` (or `/gq`) | Quits; always end with this |

Widgets built by `on_render` are listed in `/snap` and `/d` like any other
(since makepad `d0a9def5`); content an app adds later, from a timer or a
reply, appears once it is drawn, so poll `/snap?q=` for it. `card-host`
registers **no** host services, so a Mail-style app gets `no service answers "mail" on this device` there. The
current `card-host` also refuses signed manifests: take screenshots before
signing.

**In the shells.** The OctoSense desktop shell and the phone's Home run apps with
App Hub's Card runner (the `card` module in App Hub's `crates/appstore`), not
with `card-host` itself; it applies the same manifest policy. System apps are
packed into the shell build from OctoSense's `apps/`; store apps are
installed from the App Hub store out of the signed catalog. To try your own
app in the desktop shell before it is published, publish it into a local
catalog with a throwaway anchor and point the desktop shell's
`OCTOSENSE_HUB` / `OCTOSENSE_HUB_ANCHOR` at it; its App Hub installs and
opens the app (verified on macOS,
[PUBLISHING §4](docs/PUBLISHING.md#4-rehearse-the-store-path-locally)).

**On a phone, today** ([QUICKSTART §9](docs/QUICKSTART.md#9-run-it-on-an-octosense-phone)):

- An arbitrary bundle cannot be side-loaded onto a stock OctoSense phone. The
  phone's store reads the built-in hub and trusts only the anchor compiled
  into the build; the `OCTOSENSE_HUB` / `OCTOSENSE_HUB_ANCHOR` overrides are
  environment variables the Android launcher does not set. Installing from a
  local catalog on a device is unsupported and unverified.
- The closest verified path is on the desktop: publish into a local catalog
  with a throwaway anchor and install it with App Hub's standalone `appstore`
  ([PUBLISHING §4](docs/PUBLISHING.md#4-rehearse-the-store-path-locally)).
  The standalone store does not open apps; the desktop shell pointed at the
  same catalog installs and opens it.
- `card-host`'s remote bridge is compiled out on Android; phone testing goes
  through the shell's own instrument, not `tools/octo`.
- After publication, the app appears in every phone's store from the signed
  catalog.

## Headless testing: many apps, no screen

Makepad has a headless mode: an app runs with its window **never shown or
focused**, while the remote-control bridge (`/snap`, `/click`, `/t`, `/g`
screenshots) keeps working. Use it whenever an agent or a script drives an
app: it never takes over your screen or keyboard, and you can test several
apps, or several copies of one app, at the same time without them competing
for the display.

```sh
tools/octo run apps/tip-split/bundle      --port 8161 --hidden --detach
tools/octo run apps/unit-converter/bundle --port 8162 --hidden --detach
curl -s "127.0.0.1:8161/snap?q=Button"        # each app answers on its own port
tools/octo shot 8161 tip.png && tools/octo shot 8162 conv.png
curl -s 127.0.0.1:8161/quit; curl -s 127.0.0.1:8162/quit
```

- `--hidden` sets `MAKEPAD_HIDE_WINDOWS=1`; any Makepad app honours it,
  including the OctoSense shells.
- One `--port` per app (`run` refuses a port that is already taken); one `--app-data` per copy when you run the same
  bundle twice.
- Screenshots are rendered by the app itself, so they are complete even with
  nothing on screen.
- **Scripted UI tests:** makepad's [`makepad_test`](https://github.com/OctoSense-org/makepad/tree/main/libs/makepad_test)
  harness launches the app hidden, drives it through the same bridge, and
  saves a screenshot, the widget tree and the log when a test fails;
  `MAKEPAD_TEST_PARALLEL=1` runs tests (one hidden app each) concurrently.
  Setup and a `card-host` example: [QUICKSTART §4a](docs/QUICKSTART.md#4a-headless-test-without-the-screen-several-apps-at-once).

Verified 2026-09-27 on macOS (Apple silicon): two apps ran hidden side by
side, clicks sent to both at once changed each app's own state, and both
screenshots were correct; the `makepad_test` example passed.

## Publishing

[docs/PUBLISHING.md](docs/PUBLISHING.md) is the step-by-step path;
`tools/octo package-help` prints its checklist. The contract itself belongs to
the App Hub ([its PUBLISHING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md)).
In short:

1. Finalize `manifest.json` (new version, minimal capabilities, every host)
   and `listing.json` (no placeholders; the publisher fields are the
   publisher's to write).
2. Capture real screenshots with `tools/octo shot` and look at each one.
3. `tools/octo check <bundle>` until it prints `— PASSED` with only the
   unsigned warning. Optionally add `--catalog <App Hub catalog.json>` to catch
   a reused version or a publisher-key change.
4. `hub scan <bundle> --packet build/review.json` and answer its seven
   reviewer questions in writing.
5. **HUMAN:** `hub keygen` (once, outside every repository),
   `hub sign-manifest <bundle> --key … --key-id <publisher-id>`, then
   `hub check <bundle> --publisher-key <id>=<hex>`. Any edit after signing
   needs stamp and sign again.
6. **HUMAN:** tag the commit in the app's public repository and open an issue
   titled `Submit <app id> <version>` on
   [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub/issues)
   with the repository, tag, commit, bundle path, publisher key, `hub check`
   output and the scan answers.

A maintainer re-runs the gate and the scan on the exact bytes and runs
`hub publish`, which copies the bundle into the hub and signs a new catalog.

Limits, stated plainly:

- The issue route is the one App Hub's `main` documents (see [Status](#status));
  the index repository and the `octosense-org/publish-app` action it mentions
  do not exist yet. Re-read App Hub's "Submitting" section before you submit.
- Never open a pull request that edits the App Hub's `catalog.json`, `index/`
  or `artifacts/`: only `hub publish` with the hub's key writes them.
- A first submission always waits for a person. Automatic merging for
  returning publishers is planned, not built.
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
| [docs/AI-SERVICES.md](docs/AI-SERVICES.md) ([简体中文](docs/AI-SERVICES.zh-CN.md)) | OctoSense's assistant (octos): what an app can use today, a verified example, what is planned (an app's own agent, its tools, the system toolbox, glance cards, `sys.digest`), with a dated status table |
| [docs/PUBLISHING.md](docs/PUBLISHING.md) | Publishing to the App Hub, with verified outputs and the checklist |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | One meaning per term |
| [docs/NATIVE-WORKSPACE.md](docs/NATIVE-WORKSPACE.md), [docs/l0/](docs/l0/) | Sibling-source setup for the native runtime; L0 card examples |
| [templates/script-app/](templates/script-app/README.md) | The runnable template `tools/octo new` copies ("My Notes") |
| [templates/card-app/](templates/card-app/README.md) | Pointer to the card-app path |
| [examples/](examples/README.md) | Worked image-to-card projects |
| [tools/octo](tools/octo) | The CLI above |
| `tools/setup-native.py` | Prepares the pinned Octoscript-Makepad runtime ([native-runtime.lock.json](native-runtime.lock.json)) beside this repository |
| `tools/image-to-appcard-flow.sh`, `tools/beauty-pipeline.sh`, `tools/beauty-studio.sh` | Entry points for the image-to-card and kit pipelines |
| `tools/check-links.py` | Checks that relative Markdown links resolve (run in CI) |

## Examples

Reference journeys built with the image-to-card flow. Each owns its design
source, reviewed card scenes, service code and tests.

| Example | Surfaces | What it is |
| --- | --- | --- |
| [Aircon](examples/aircon/README.md) | Native cards / WASM | A purchase-to-installation journey: 12 screen states, 14 service-card variants |
| [School](examples/school/README.md) | Native cards / WASM | School notice, calendar and payment |
| [Health](examples/health/README.md) | Native cards / WASM | A fictional health-check booking |
| [Reunion](examples/reunion/README.md) | Native cards / WASM | Reunion planning, RSVP and payment |
| [Calendar](examples/calendar/README.md) | Native cards / browser preview + sync server | One calendar on two devices, with a SQLite-backed sync server |

For a script app, the complete examples are the first-party bundles in
[OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps)
(`apps/<name>/bundle/`), plus [templates/script-app](templates/script-app/README.md).

## Contributing

- Branch from `main` and open a pull request; CI must pass.
- CI runs `python tools/check-links.py` (relative links in tracked Markdown
  must resolve) and, on macOS, prepares the native runtime with
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
| [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) | The signed catalog, the gate, `hub`, `card-host`, the store and the Card runner |
| [OctoSense](https://github.com/OctoSense-org/OctoSense) | The shell and what ships in it: the desktop shell (`desktop/`), the phone shell Home (`phone/`, as a Home app or in the ROM image built by `rom/`), and the first-party apps with their host services (`apps/`). Formerly OctoSense-Desktop, OctoSense-ROM and OctoSense-System-Apps. |
| [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps) | First-party apps (News, Photos, Maps, Camera, Mail, AI providers) and their host services (`mail`, `llm`) |
| [OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard) | The AppCard assistant (`octos-app`, opt-in in the shells with `--features app-appcard`) and the L0 card language; the Splash isolate and widgets themselves are in makepad |
| [OctoSense-org/makepad](https://github.com/OctoSense-org/makepad), [Octoscript](https://github.com/OctoSense-org/OctoScript), [Octoscript-Makepad](https://github.com/OctoSense-org/OctoScript-Makepad) | The framework and language the apps run on |

## License

Apache-2.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE).
