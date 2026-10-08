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
   (the submission issue, release provenance and Hub review). Opening the
   issue is the request to publish; a tag/release is not automatic submission.
3. Follow the flow's steps **in order and exactly**. Each step has a pass
   condition; do not start the next step until it holds.
4. **Stop at every human checkpoint** (steps marked **HUMAN**, or rows whose
   "Human?" column says yes): GitHub release workflow, publisher identity
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
  sign-in. OctoSense `main` (in no release yet) signs the person in to the
  app's own backend: the bundle declares it in a signed `backend` block, or
  the host's operator registers it
  ([the backend guide](docs/HOST-API-V1.md#4-connect-the-apps-backend)).
- **Declare every host.** List in `network.hosts` every `https://` host that
  `main.splash` contacts, and request `net`. `images` and `web` add pictures
  and pages from any public `https://` host; they do not widen `net`. Never
  use `http://`.
- **Every AI feature is optional.** Make the app complete without one:
  `card-host` (and so `tools/octo run`) serves no AI service, and every call
  there answers `no service answers "…" on this device`. On an OctoSense
  device a store app can call `model.complete`, and `octos.*` once the person
  allows its agent. Released hosts offer `model.complete` and `model.budget`.
  Image, speech, video and embedding methods are implemented in
  [OctoSense #368](https://github.com/OctoSense-org/OctoSense/pull/368), merged into `main`; compatible release pending; neither beta.2 nor
  `card-host` provides them. Follow the [media guide](docs/AI-SERVICES.md#media-and-embeddings-model)
  and its source-pinned API reference. A configured chat provider is not
  proof of media entitlement; live paid providers and device execution remain
  unverified. `llm` is for system apps only. Never put a model key in an app. Read
  [docs/AI-SERVICES.md](docs/AI-SERVICES.md) before adding an AI feature, and
  report each one as unverified until exercised on its actual host.
- **Connected accounts and host-service tools need `desktop-v0.1.0-beta.2`
  or a build from OctoSense `main`.**
  App Hub's contract 1.5 admits `auth`, `github`, `gmail` and `gcalendar`.
  OctoSense serves them from `desktop-v0.1.0-beta.2` on. On that build:
  - the host runs the OAuth sign-in and gives the app a connection handle,
    never a token. Beta.2 has no built-in provider registrations, so the
    host's operator supplies them in `oauth/clients.json`;
  - a store app's `tools.json` tools run only with
    `implemented_by: "host-service"` and a `host_method` from App Hub's
    reviewed list: reads of `github`, `gcalendar` and `gmail`, Gmail drafts
    and events, and `glance`. A tool without `host_method` calls the service
    named after the app's namespace (`summary` for `dev.example.summary`); no
    capability grants that service, so the call answers `not_granted`. The
    shell refuses
    `implemented_by: "app"`, so no tool runs the app's own code. The
    capability, risk, private-data and account checks still apply;
  - admitted `AGENT.md` and skill text is per-turn guidance, not an
    executable kernel skill.

  OctoSense `main` (in no release yet) also runs `implemented_by: "app"`
  tools. The manifest must declare `requires: ["script-tools-v1"]`, and the
  shell calls the app's `app_tool` handler while the full app is open; a call
  to a closed app answers `app_not_running`
  ([docs/HOST-API-V1.md](docs/HOST-API-V1.md#5-implement-a-declared-app-tool)).
  `card-host` refuses an app that requires `host-api-v1`, `backend-api-v1` or
  `script-tools-v1`; test such an app in a shell built from OctoSense `main`.

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
- **Restamp editable source after every edit.** `tools/octo check` and
  `tools/octo run` stamp unsigned source for you. Never restamp or strip the
  proof from a sealed GitHub-attested or legacy signed release.
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
  which a bundle may not hold`. Delete it, then stamp. Plain `.txt`/`.md`
  documentation may contain license/attribution URLs; keep required font
  notices in the bundle. Agent guidance and structured resources retain
  their normal host/resource checks.
- **Name a card's own font with a bundle-relative path.** Put the `.ttf` or
  `.otf` file in the bundle and set `font_src` to its path, such as
  `"font_src": "assets/Body.ttf"`; `card-host` loads it from the bundle's
  asset server. A bundled font counts toward the 8 MiB limit, so bundle a
  subset of a large CJK font. Text the font lacks, such as Chinese, falls
  back to LXGW WenKai, Makepad's built-in Chinese font. A kit may name
  exactly `Inter.ttf`, `LXGWWenKaiRegular.ttf` or `LXGWWenKaiBold.ttf` under
  `makepad_widgets:resources/`. A single `$token` reference resolving to a
  supported string is accepted; arbitrary objects, nested token references
  and other crate paths remain refused. Rebuild older gates from App Hub
  #146 or later.
  `desktop-v0.1.0-beta.2` predates this font loading: it installs an app
  with a bundled font, but its cards do not load the font. For Chinese text
  there, build the card from the plain L0 role kit and set no `font_src`;
  LXGW WenKai draws it.
  A script app may bundle a font and load it with
  `FontMember{res: http_resource("{{assets}}/fonts/X.ttf")}`. Check text with
  `MAKEPAD_SYSTEM_FONTS=0`, so a system font cannot hide a missing glyph.
  Font loading in a shell built from OctoSense `main` is unverified.
- **Keep the bytes exact.** The digest covers every byte of every file, so a
  line-ending conversion breaks it. Commit the `.gitattributes` that
  `tools/octo new` writes (`bundle/** -text`), so that a Windows checkout
  with `core.autocrlf=true` leaves the bundle alone. In a repository that
  `tools/octo new` did not create, add one that unsets `text` for the bundle.
  Confirm it with
  `git check-attr text -- <path to bundle>/manifest.json`, which prints a
  line ending in `text: unset` ([QUICKSTART §3](docs/QUICKSTART.md#3-create-an-app)).
- **Use GitHub publishing for a new app.** `tools/octo publish-github <app>`
  installs the tag workflow; `new` also copies it. No developer signing key
  or signing secret is required. Review the workflow and test unsigned source
  before release. Manual Ed25519 signing is optional compatibility only.
- **Never move a tag.** Commit tested editable source and the workflow, then
  use `v` plus the manifest's version (`v0.1.0`). The workflow prepares,
  attests, verifies and packs the release; do not commit its sealed output
  back over the editable source. Every later release needs a new version/tag.
- **Verify the release artifact separately.** A source gate pass is not
  publisher-proof verification. The workflow must pass `publisher-verify`
  and `publisher-pack`; no restamping after attestation. `card-host` refuses
  sealed releases. Contract 1.8.0 / `publisher-github-v1` support and a
  compatible host are required. Real GitHub publishing and native Store
  install/update checks passed with an isolated test catalog; shipped-shell
  and phone installation remain unverified, and a compatible release is pending.
  See [PUBLISHING §3.6](docs/PUBLISHING.md#36-publisher-key--human).
- **An issue requests publication.** Include repository, version/commit,
  screenshots and permissions; it may precede the release. Attach the
  successful workflow and exact release pack when ready. The Hub checks it,
  an administrator approves, and the authenticated catalog publishes it.
  Never claim that pushing a tag automatically submits or approves an app.
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
   For an app that `card-host` refuses, use a shell built from OctoSense
   `main` ([docs/HOST-API-V1.md](docs/HOST-API-V1.md#before-publishing)).
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
