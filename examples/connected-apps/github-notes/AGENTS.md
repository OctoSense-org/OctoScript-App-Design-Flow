# Developing this OctoSense app

> Every step is a shell command or a file edit, so a coding agent or a person at a terminal can follow it. `AGENTS.md` is the one source of truth; `CLAUDE.md` and `GEMINI.md` only import it for agents that look for those names.

This directory is one OctoSense script app. `bundle/` is the app and the only
thing submitted to the App Hub; everything else stays outside it.

Follow the App Flow docs (the harness), and do not invent requirements or
APIs:

- Build, run and test: [QUICKSTART](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/main/docs/QUICKSTART.md)
- The language and every API an app may use: [SCRIPT-API](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/main/docs/SCRIPT-API.md)
- Capabilities: [CAPABILITIES](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/main/docs/CAPABILITIES.md)
- Final bundle, screenshots and human checkpoints: [PUBLISHING](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/main/docs/PUBLISHING.md)
- Signing and the submission issue: App Hub's [SUBMITTING](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md)

`card-host` has no `MarkdownEditor`, so it can't show this app's editor. Run
this edit-and-check loop with OctoSense's test host instead, with
`OCTO=<path to OctoSense-App-Flow>/tools/octo`:

1. Edit `bundle/main.splash`.
2. In an OctoSense checkout next to the App Flow repository, build the
   test hosts once:

   ```sh
   cargo build --locked --release -p octosense-shell \
     --features mobile-apps,acceptance-fixtures \
     --example connected-app-host --example connected-install
   ```

3. From that checkout, run the installed journey:

   ```sh
   python3 tools/connected-e2e/notes.py \
     --bundle ../OctoSense-App-Flow/examples/connected-apps/github-notes/bundle
   ```

   It ends with
   `PASS: installed Notes flow with synthetic provider; native pixel review pending`.
   On a failure it raises an assertion error and still writes its receipt and
   a `failure` capture to the evidence directory it prints.
4. From this directory, run `$OCTO check bundle`.
   It prints `— PASSED` with the `unsigned` warning and a note about the
   listing placeholders. Fix each `[refused]` finding and rerun.

Rules:

- Ask only for capabilities a screen uses; declare every `https://` host in
  `network.hosts`; never `http://`.
- Never collect or store a password, PIN, one-time code, API key or token;
  accounts go through a host service.
- Keep the ID's last segment off App Hub's reserved names (`notes`, `weather`,
  `terminal` and others); the gate refuses them.
- Put only files the gate accepts in `bundle/`: no `.DS_Store`, no file
  without an extension, no URL in a bundled `.txt` or `.md` file; keep the
  whole bundle within 8 MiB.
- Capture screenshots from the unsigned bundle, look at each one, and never use
  a placeholder.
- Restamp after every edit (`$OCTO check` does it). Sign last; any edit
  after signing needs a new stamp and a new signature.
- Keep keys, `.local-state/`, `build/` and review packets out of `bundle/` and
  Git.
- Stop at human steps: publisher key, publisher details, platform claims, tag,
  submission.

## This sample

- Version 0.1.0 is published from
  [ymote/octosense-github-notes](https://github.com/ymote/octosense-github-notes).
  This directory is the unsigned development copy; its `listing.json` keeps
  publisher placeholders.
- Don't submit this copy. Its ID and version are already in the App Hub
  catalog, so the gate refuses it with `version` and `continuity` findings. A
  new app needs its own ID and tool namespace; follow
  [Start your own app from one](../README.md#start-your-own-app-from-one).
- The manifest declares the optional foreground, read-only agent that
  `tools.json` implies, with `AGENT.md`; the published 0.1.0 ships the tools
  without the `agent` block. Keep the agent read-only, with no write, commit
  or approval tool, and keep the listing and privacy text in step with it.
