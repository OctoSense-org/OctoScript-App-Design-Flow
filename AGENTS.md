# Instructions for coding agents

> **Any coding agent, or none.** These instructions work the same for Codex, Claude Code, Cursor, Gemini CLI, GitHub Copilot or a person at a terminal: every step is a shell command or a file edit, and nothing here needs a particular agent, model or vendor. `AGENTS.md` is the one source of truth; `CLAUDE.md` and `GEMINI.md` only import it for agents that look for those names.

You are in **OctoScript App Design Flow**: the harness for building an
OctoSense app and taking it to the OctoSense App Hub. Read this file first,
then the one flow you are following. For repository architecture/documentation
work, read [docs/CODE-WALKTHROUGH.md](docs/CODE-WALKTHROUGH.md): trace code and
check links and commands.
The screenshot, gate and publishing checklist below applies when delivering
an app bundle, not when reviewing this repository's documentation.

## What this repository is, and is not

| It is | It is not (go there instead) |
| --- | --- |
| Flows (`flows/*/FLOW.md`): step-by-step procedures from an input to a checked bundle | The runtime: [OctoSense-org/makepad](https://github.com/OctoSense-org/makepad) (Splash isolate, widgets) and [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) (the Card runner); the AppCard assistant: [OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard); the L0 parser/checker: [Octoscript](https://github.com/OctoSense-org/Octoscript), and its Makepad lowering/renderer: [Octoscript-Makepad](https://github.com/OctoSense-org/OctoScript-Makepad) |
| Developer docs (`docs/`): quickstart, script API, capabilities, host services, AI services, publishing, glossary | System apps (News, Photos, Maps, Camera, Mail, AI providers): [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps) |
| `tools/octo`: doctor, new, run, shot, check around the real `card-host` and `hub` | The store, gate, catalog, `hub` and `card-host` source: [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) |
| Templates (`templates/script-app/`) and worked examples (`examples/`) | The shells that run apps: [OctoSense](https://github.com/OctoSense-org/OctoSense) `phone/` (Home, the phone launcher) and `desktop/` (the desktop shell) |

If a task needs a change in one of those repositories, say so and stop; do not
patch around it here.

## How to work

1. Set up the workspace once ([QUICKSTART §1–2](docs/QUICKSTART.md#1-prerequisites):
   clone this repository and OctoSense-App-Hub side by side, run
   `python3 tools/setup-native.py`, build `hub` and `card-host`), then run
   `tools/octo doctor`. Fix what it reports before anything else.
   `tools/octo` is this repository's own Python CLI around App Hub's `hub` and `card-host`. It is unrelated to octos (the agent kernel inside OctoSense) and needs no AI service or API key. `doctor` checks Python, cargo, the App Hub checkout and the `hub` / `card-host` binaries.
2. Pick the flow from [flows/README.md](flows/README.md). For a text brief it
   is [flows/script-app/FLOW.md](flows/script-app/FLOW.md). Publishing is
   [docs/PUBLISHING.md](docs/PUBLISHING.md) for every flow.
3. Follow the flow's steps **in order and exactly**. Each step has a pass
   condition; do not start the next step until it holds.
4. **Stop at every human checkpoint** (marked **HUMAN** or "Human?" = yes):
   publisher keys, publisher identity and privacy text, platform claims,
   submission, approval. Report and wait. Never fabricate an approval, a
   review result, a submission or a person's answer.
5. **Never invent an API.** Use only what [docs/SCRIPT-API.md](docs/SCRIPT-API.md)
   documents, or what you found in the runtime source (makepad
   `widgets/src/splash*.rs`, `platform/script/src/`) or a working System App
   (`apps/*/bundle/main.splash`) and can cite. If neither has it, the app
   cannot use it: say so.
6. **Validate model output against the final source.** Follow
   [docs/MODEL-VALIDATION.md](docs/MODEL-VALIDATION.md) for native input, visual
   review and focused repair. Check populated startup state, not just admission
   or open success. Keep behavior, geometry and visual judgments separate;
   preserve failures and distinguish operator-run checks from model-run checks.

## Rules for every app

- **No secrets in apps.** No password, PIN or one-time-code field, no login
  form, no API key or token in the bundle. Accounts go through a host service's
  sheet ([docs/HOST-SERVICES.md](docs/HOST-SERVICES.md)).
- **Declare every host.** Every `https://` host in `main.splash` is in
  `network.hosts` (with `net`), unless the app legitimately needs `images` or
  `web`. Never `http://`.
- **Every AI feature is optional.** On an OctoSense device a store app can
  call `model.complete`, and `octos.*` once the person allows its agent, but
  `card-host` (and so `tools/octo run`) serves neither: every call there
  answers `no service answers "…" on this device`. `llm` is for system apps
  only. Never put a model key in an app. Read
  [docs/AI-SERVICES.md](docs/AI-SERVICES.md) before adding one, and report
  such a feature as not verified on a device. An app's own agent
  (`"agent": {…, "tools": ["ask_user_question"]}`) is checked here only by
  `hub check`. In the shells the person talks to it directly in the
  "Ask <app>" panel the shell draws for every app with an agent, so the app
  need not draw a chat of its own (desktop; the phone has no entry to the
  panel yet). A store app's `tools.json` tools do not run in any shell yet,
  so no screen may depend on its agent calling them. L0 cards that use
  `sys.chat`, `sys.digest` or `model-copy` text need a newer runtime than
  this repository pins: report them as not verified here.
- **Only needed capabilities.** Each capability maps to something a screen
  does ([docs/CAPABILITIES.md](docs/CAPABILITIES.md)). Remove what is unused.
- **No dummy screenshots.** Screenshots are captures of the real app in a real
  state (`tools/octo shot`), opened and looked at. Never draw, generate, crop
  from another app, or copy one to make the gate pass.
- **Restamp after every edit.** `tools/octo check` and `tools/octo run` stamp
  for you; after signing, any edit needs stamp and sign again (human).
- **Keep the bundle clean.** Only `manifest.json`, `listing.json`, the entry,
  artwork and screenshots go in `bundle/` (plus `tools.json`, `AGENT.md` and
  `skills/` for an app that declares its own agent; the shells give it a peer,
  `ask_user_question` and read access to its account folder, and register
  its tools (which run only for system apps today), but do not install
  `AGENT.md` or skills yet:
  [docs/AI-SERVICES.md](docs/AI-SERVICES.md#an-apps-own-agent)). Notes, keys, logs, review packets
  and `.local-state/` stay out.
- **Run headless.** Start apps with `tools/octo run … --hidden` (Makepad's
  headless mode: the window is never shown or focused, the remote bridge and
  screenshots work as usual), so you never take over the person's screen.
  Several apps can be tested at once: one `--port` each, and `--app-data` per
  copy when you run the same bundle twice. For scripted regression tests use
  makepad's `makepad_test` harness ([QUICKSTART §4a](docs/QUICKSTART.md#4a-headless-test-without-the-screen-several-apps-at-once)).
- **Clean up what you launch.** End every `card-host` you start with
  `curl -s 127.0.0.1:<port>/quit` (or `/gq`); do not `pkill` other windows.
  `tools/octo run` refuses a port that is still taken and prints the `/quit`
  command for whatever holds it. With `--detach` it returns once the app is
  drawn, so you can click, type or `shot` immediately; without `--detach`
  it waits for the child process to exit.

## Definition of done (before hand-off to a human)

All of:

1. `tools/octo check <bundle>` prints `— PASSED` with only the unsigned warning.
2. Real screenshots in `bundle/screenshots/`, named in `listing.json`, each looked at.
3. Every interaction in the brief was driven natively in `card-host` (click,
   type, tap through the remote bridge) and its effect observed.
4. Empty, error and restart states were exercised.
5. `hub scan` packet written outside the bundle and its seven questions answered.
6. The [PUBLISHING checklist](docs/PUBLISHING.md#6-checklist-copy-then-run-top-to-bottom)
   is complete up to the first **HUMAN** line.

## Reporting

End with a report a person can check without rerunning anything:

- **Verified**: each command you ran and its result, quoted (gate output
  verbatim), with the screenshots' paths.
- **Not verified**: anything you did not run (a platform, a host service that
  `card-host` does not provide, a phone), stated as not verified, never as
  "should work".
- **Waiting on a human**: the checkpoints reached, and exactly what the person
  must do next.
- **Gaps found**: runtime or tool behavior that contradicted the docs, with the
  smallest reproduction you have.

## Architecture claims and documentation changes

- Keep Splash/Makepad Script and Octoscript L0 distinct; the project name
  does not make `.splash` and `.card` interchangeable languages.
- Separate validation, grants, registration and executable handlers. A
  `tools.json` entry or `AGENT.md` accepted by the gate is not proof the
  runtime executes or installs it. Default App Hub admission also checks
  `agent.tools` against `HostLimits::offered_tools`; shell relay support
  alone does not make an arbitrary cross-app tool request admissible.
- Distinguish an account workspace from the entire app jail and host
  service storage. Agent access is bounded; do not promise automatic access
  to data written elsewhere by the UI.
- Explain routing terms through one request and show pipeline inputs and
  outputs before enumerating stages. Keep worked examples explicit about
  required files, consent and runtime support.
- Keep English/Chinese README summaries aligned, preserve dated evidence,
  run `python3 tools/check-links.py`, and also check links in new untracked
  Markdown files. Report unrun native, provider and device paths explicitly.
- Runtime locks belong to each consumer. Do not update shared sibling
  checkouts or pins merely to make a documentation command pass.

## Syntax reminders for `main.splash`

Splash comments use `//` or `/* … */`, never `.card`-style `#` prose. Keep a
container open until after its children; indentation does not reopen it.
`#x` for hex colors containing `e` (`#x1e1e2e`); `for i in n`, no `range()`;
`name := Widget{}` to address a widget as `ui.name`; `draw_bg +: {…}` merges;
separate `if` and `for` in `on_render` (no `else for`). The full list is in
[docs/SCRIPT-API.md](docs/SCRIPT-API.md#gotchas).
