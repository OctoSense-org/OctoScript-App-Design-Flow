# Instructions for coding agents

`CLAUDE.md` and `GEMINI.md` only import this file, so every coding agent reads
the same rules.

You are in **OctoScript App Design Flow**: the harness for building an
OctoSense app and taking it to the OctoSense App Hub. Read this file first,
then the one flow you are following. For architecture or documentation work
on this repository, read [docs/CODE-WALKTHROUGH.md](docs/CODE-WALKTHROUGH.md),
then trace the code and check links and commands. The app rules, admission
rules and definition of done below apply when you deliver an app bundle, not
when you review this repository's documentation.

## What this repository is, and is not

This repository holds the flows (`flows/*/FLOW.md`), the developer docs
(`docs/`), `tools/octo`, the template (`templates/script-app/`) and the
worked examples (`examples/`). Change anything else where it lives:

| To change | Go to |
| --- | --- |
| The Splash isolate or widgets | [OctoSense-org/makepad](https://github.com/OctoSense-org/makepad) |
| The gate, `hub`, `card-host`, the store, the catalog, the Card runner or the submission route | [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) |
| The L0 parser or checker | [OctoScript](https://github.com/OctoSense-org/Octoscript) |
| The L0 Makepad renderer | [OctoScript-Makepad](https://github.com/OctoSense-org/Octoscript-Makepad) |
| The AppCard assistant, a system app or a shell | [OctoSense](https://github.com/OctoSense-org/OctoSense): `apps/appcard`, `apps/`, `phone/` (Home) and `desktop/` |

If a task needs a change in one of those repositories, say so and stop; do not
patch around it here.

## How to work

`tools/octo` is this repository's own Python CLI around App Hub's `hub` and
`card-host`. It is unrelated to octos (the agent kernel inside OctoSense) and
needs no AI service or API key.

1. Set up the workspace once, as [QUICKSTART §1–2](docs/QUICKSTART.md#1-prerequisites)
   shows, and build `hub` and `card-host` from current App Hub `main`. Then
   run `tools/octo doctor` and fix everything it reports.
2. Pick the flow from [flows/README.md](flows/README.md). For a text brief it
   is [flows/script-app/FLOW.md](flows/script-app/FLOW.md). Every app flow
   ends with [docs/PUBLISHING.md](docs/PUBLISHING.md) (final bundle,
   screenshots, human checkpoints), then App Hub's
   [SUBMITTING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md)
   (signing, tag and issue, done by a person).
3. Follow the flow's steps **in order and exactly**. Each step has a pass
   condition; do not start the next step until it holds.
4. **Stop at every human checkpoint** (steps marked **HUMAN**, or rows whose
   "Human?" column says yes): publisher keys and signing, publisher identity
   and privacy text, platform claims, paid image generation, visual approval,
   the release tag, submission. Report and wait. Never fabricate an approval,
   a review result, a submission or a person's answer.
5. **Never invent an API.** Use only what [docs/SCRIPT-API.md](docs/SCRIPT-API.md)
   documents, or what you found in the runtime source (Makepad
   `widgets/src/splash*.rs`, `platform/script/src/`) or a working system app
   (`apps/*/bundle/main.splash`) and can cite. If none of these sources has
   it, the app cannot use it: say so.
6. **Check the app you built against its final source.** Follow
   [docs/MODEL-VALIDATION.md](docs/MODEL-VALIDATION.md) for native input,
   visual review and focused repair. Check that the app starts with its data
   loaded, not only that it opens. Judge behavior, layout and appearance
   separately. Keep the evidence of every failure, and say which checks a
   person ran and which you ran.
   For new Glance cards or card UX acceptance, also use
   [the app-card UX skill](skills/octoscript-app-card-ux/SKILL.md): summary-to-workspace
   transitions, shared editing state, keyboard/scrolling checks and source-bound
   acceptance. This is a development workflow, not runtime app-agent provisioning.

## Rules for every app

- **No secrets in apps.** No password, PIN or one-time-code field, no login
  form, and no API key or token in the bundle or in the app's storage. The
  gate refuses only password and one-time-code fields; a key kept anywhere
  else is still a secret the app holds. Accounts go through a host service's
  sheet ([docs/HOST-SERVICES.md](docs/HOST-SERVICES.md)). Beta.2 has no backend
  sign-in. Earlier OctoSense source builds use operator-managed backend
  registrations; compatible Host API v1 source builds also accept public
  registration metadata from an admitted signed bundle's `backend` block.
  Contract 1.6.0 is published, but a compatible host release is pending.
  Follow [the backend guide](docs/HOST-API-V1.md#4-connect-the-apps-backend);
  operator configuration remains available when the bundle has no declaration.
- **Declare every host.** List in `network.hosts` every `https://` host that
  `main.splash` contacts, and request `net`. `images` and `web` add pictures
  and pages from any public `https://` host; they do not widen `net`. Never
  use `http://`.
- **Every AI feature is optional.** Make the app complete without one:
  `card-host` (and so `tools/octo run`) serves no AI service, and every call
  there answers `no service answers "…" on this device`. On an OctoSense
  device a store app can call `model.complete`, and `octos.*` once the person
  allows its agent. `model` offers
  `model.complete` and `model.budget` only; `model.image`, `model.audio`,
  `model.video` and `model.embeddings` do not exist. `llm` is for system apps
  only. Never put a model key in an app. Read
  [docs/AI-SERVICES.md](docs/AI-SERVICES.md) before adding an AI feature, and
  report each one as unverified until exercised on its actual host.
- **Connected accounts and app tools need OctoSense `desktop-v0.1.0-beta.2`.**
  App Hub's contract 1.5 admits `auth`, `github`, `gmail` and `gcalendar`.
  OctoSense serves them from `desktop-v0.1.0-beta.2` on. On that build:
  - the host runs the OAuth sign-in and gives the app a connection handle,
    never a token. Beta.2 has no built-in provider registrations, so the
    host's operator supplies them in `oauth/clients.json`;
  - `tools.json` tools run only with `implemented_by: "host-service"`,
    directly or through an allowlisted `host_method`. The capability, risk,
    private-data and account checks still apply, and the shell refuses
    `implemented_by: "app"`;
  - admitted `AGENT.md` and skill text is per-turn guidance, not an
    executable kernel skill.

  `card-host`, beta.1 builds and older shells provide none of this, and a
  gate pass does not prove a provider connection. The three published
  reference apps show the pattern
  ([examples/connected-apps](examples/connected-apps/README.md)): keep a
  manual path and a clear missing-service state, as they do.
- **Only needed capabilities.** Map each capability to something a screen
  does ([docs/CAPABILITIES.md](docs/CAPABILITIES.md)), and remove the rest.
- **No placeholder screenshots.** Capture the real app in a real state with
  `tools/octo shot`, then open each PNG and look at it. Never draw, generate,
  redraw from `/snap`, crop from another app, or copy a screenshot to make
  the gate pass.
- **Restamp after every edit.** `tools/octo check` and `tools/octo run` stamp
  for you.
- **Keep the bundle clean.** Only `manifest.json`, `listing.json`, the entry
  file (`main.splash`, or `page.card` with `kit/`), artwork and screenshots go
  in `bundle/`. An app with its own agent adds `tools.json`, `AGENT.md`,
  `skills/` and the `.splash` Glance templates its tools publish
  ([An app's own agent](docs/AI-SERVICES.md#an-apps-own-agent)). Notes, keys,
  logs, review packets and `.local-state/` stay out.
- **Run headless.** Start apps with `tools/octo run … --hidden`, so you never
  take over the person's screen. This is Makepad's hidden-window mode: the app
  still needs a graphical session, but its window is never shown or focused,
  and the remote bridge and screenshots work as usual.
  You can test several apps at once: give each its own `--port`, and each
  copy of the same bundle its own `--app-data`. For scripted regression tests,
  use Makepad's `makepad_test` harness ([QUICKSTART §4b](docs/QUICKSTART.md#4b-scripted-ui-tests-with-makepad_test)).
- **Clean up what you launch.** End every `card-host` you start with
  `curl -s 127.0.0.1:<port>/quit` (or `/gq`); do not `pkill` other windows.
  `tools/octo run` refuses a port that is still taken and prints the `/quit`
  command for whatever holds it.

## Rules that keep a submission admissible

The gate checks some of these; reviewers and the shells hold you to the rest.

- **Keep the id's last segment off the reserved names.** The gate refuses an
  id whose last segment, after its final `.`, is the name of a native app or
  of the host (`notes`, `weather`, `calculator`, `browser`, `terminal`,
  `rinx`, `system` and others): `com.example.notes` gets
  `[refused] identity: app id "com.example.notes" ends in "notes", which is reserved: …`,
  while `my-notes` passes. `tools/octo new` refuses such an id before it
  creates any file; the gate catches one you change later. The full list is
  in App Hub's [rules the gate enforces](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#rules-the-gate-enforces).
- **Only known file types in `bundle/`.** The gate refuses a file whose
  extension it does not know, including macOS `.DS_Store` and any file
  without an extension: `[refused] contents: .DS_Store has extension "",
  which a bundle may not hold`. Delete it, then stamp. It also refuses a URL
  inside a bundled `.txt` or `.md` file, such as a font license.
- **Only one built-in font.** A card kit's `font_src` may name only
  `makepad_widgets:resources/Inter.ttf`. Ship any other font as a file in the
  bundle ([App Hub#75](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/75)).
- **Keep the bytes exact.** The digest covers every byte of every file, so a
  line-ending conversion breaks it. Commit a `.gitattributes` holding
  `bundle/** -text`, so that a Windows checkout with `core.autocrlf=true`
  leaves the bundle alone.
- **Sign last, and never edit after signing.** Capture screenshots and run
  `card-host` on the unsigned bundle; `card-host` refuses a signed one. Only
  a person signs. Any edit after signing needs a new stamp and a new
  signature.
- **Never move a tag.** Tag the commit that holds the final signed bundle,
  `v` plus the manifest's `version` (`v0.1.0`). To change anything after
  that, release a new version under a new tag.
- **Run the final check from a fresh clone.** `tools/octo check` restamps an
  unsigned bundle, so it passes a working copy whose committed digest is
  stale. Clone the tag into a new directory and run `hub check` there without
  restamping, as a reviewer does
  ([SUBMITTING §6](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#6-freeze-and-verify-the-release)).
- **No `script` in a Glance tool.** An agent tool that publishes Glance
  cards accepts `template` with `initial`, or L0 `source` with `data`, and
  never `script`. OctoSense runs a script card under the app's own policy.
  On `desktop-v0.1.0-beta.2`, an agent tool can publish one, so a
  prompt-injected turn could publish arbitrary Splash code. OctoSense `main`
  refuses `script` from agent tools, but no release has that check yet.
- **Shipping `tools.json` gives the app an agent.** With or without an
  `agent` block, App Hub admits the tools as the app's agent and OctoSense
  offers an `Ask <app>` panel for it. Declare the `agent` block and say so in
  the listing and the privacy text. For an app without an agent, ship no
  `tools.json`.

## Definition of done (before hand-off to a person)

Hand off only when all of these hold:

1. `tools/octo check <bundle>` prints `— PASSED` with only the unsigned
   warning.
2. `bundle/screenshots/` holds real screenshots, each named in
   `listing.json` and inspected.
3. You have driven every interaction in the brief natively in `card-host`
   (click, type and tap through the remote bridge) and observed its effect.
4. You have exercised the empty, error and restart states.
5. The `hub scan` packet is written outside the bundle and its questions are
   answered: seven, or eight when the bundle ships `tools.json`, `AGENT.md`
   or skills.
6. The [PUBLISHING checklist](docs/PUBLISHING.md#6-checklist-copy-then-run-top-to-bottom)
   is complete up to the first **HUMAN** line.

## Reporting

End with a report a person can check without rerunning anything:

- **Verified**: each command you ran and its result, quoted (gate output
  verbatim), with the screenshots' paths.
- **Not verified**: anything you did not run (a platform, a host service that
  `card-host` does not provide, a phone), stated as not verified, never as
  "should work".
- **Waiting on a person**: the checkpoints reached, and exactly what the
  person must do next.
- **Gaps found**: runtime or tool behavior that contradicted the docs, with the
  smallest reproduction you have.

## Architecture claims and documentation changes

- Keep Splash/Makepad Script and OctoScript L0 distinct: `.splash` and
  `.card` are different languages, whatever this repository's name suggests.
- For each feature, say separately whether the gate validates it, the host
  grants it, the shell registers it and a handler runs it. A `tools.json`
  entry or `AGENT.md` accepted by the gate is not proof that a given runtime
  executes or loads it. Default App Hub admission also checks `agent.tools`
  against `HostLimits::offered_tools`, so a shell's ability to relay a call to
  another app's tool does not make that call admissible.
- An app's agent reads only its account workspace (`storage.agent_workspace`).
  Never promise that it sees data the UI wrote elsewhere.
- Check each L0 feature against the runtime that renders it, and record what
  you ran.
- Explain routing by tracing one request, and show a pipeline's inputs and
  outputs before you list its stages. In worked examples, name the required
  files, the consent the person gives and the runtime that supports each
  step.
- Keep each `X.md` and its `X.zh-CN.md` saying the same thing, and never
  rewrite dated evidence.
- Run `python3 tools/check-links.py`. It reads `git ls-files`, so `git add`
  new Markdown files first.
- Name every native, provider and device path you did not run.
- Runtime locks belong to each consumer. Do not update shared sibling
  checkouts or pins merely to make a documentation command pass.

## Syntax reminders for `main.splash`

The full list is in [docs/SCRIPT-API.md](docs/SCRIPT-API.md#gotchas).

- Write comments as `//` or `/* … */`, never `.card`-style `#` prose.
- Close a container after its children; indentation does not reopen it.
- Prefix a hex color with `#x` when an `e` sits next to a digit
  (`#x1e1e2e`); `#x` is always safe.
- Loop with `for i in n`; there is no `range()`.
- Write `name := Widget{}` to address a widget as `ui.name`.
- `draw_bg +: {…}` merges your fields into the existing `draw_bg`.
- In `on_render`, keep `if` and `for` separate (no `else for`).
