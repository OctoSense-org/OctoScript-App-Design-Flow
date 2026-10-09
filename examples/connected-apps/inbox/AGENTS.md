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

Run this edit-and-check loop from this directory, with
`OCTO=<path to OctoSense-App-Flow>/tools/octo`. The CLI lives in the
harness repository, not here; on Windows, run it as `python $OCTO`.

1. Edit `src/workspace.splash`, never the generated `bundle/main.splash` or
   `bundle/glance-workspace.splash`.
2. Run `python3 build_bundle.py`. It regenerates both files and rewrites the
   capabilities, storage and agent block in `bundle/manifest.json`, and prints
   nothing. It stops with
   `Workspace must leave room for a compact binding in the 16 KiB Glance budget`
   when the generated Glance workspace grows past 14 KiB.
3. Run `$OCTO run bundle --port 8141 --hidden --detach`. It prints
   `ready: first frame drawn`; on a failure it prints the log tail and stops the
   `card-host` it started.
4. Run `python3 verify_native.py --port 8141`. It prints a line that starts
   `PASS startup, second-message identity`. It overwrites the PNGs and
   `run-receipt.json` in `evidence/`; commit them only as new evidence.
5. Run `curl -s 127.0.0.1:8141/quit`.
6. Run `$OCTO check bundle`.
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
  [ymote/octosense-inbox-assistant](https://github.com/ymote/octosense-inbox-assistant).
  This directory is the unsigned development copy; its `listing.json` keeps
  publisher placeholders.
- Don't submit this copy. Its ID and version are already in the App Hub
  catalog, so the gate refuses it with `version` and `continuity` findings. A
  new app needs its own ID, tool namespace and trigger name; follow
  [Start your own app from one](../README.md#start-your-own-app-from-one).
- `inbox.draft_edit` runs in the background, which is not safe to copy.
  `inbox.notify` accepts only the bundled `glance-workspace.splash` template
  and `initial`; the published 0.1.0 also accepts `script`, `source` and
  `data`. Never add executable card input to an agent's tool. See
  [What to copy, what not to copy](../README.md#what-to-copy-what-not-to-copy).
- `build_bundle.py` generates `main.splash` and `glance-workspace.splash` from
  the same controller in `src/workspace.splash`.
- Chat uses the app agent; `model.complete` is only the explicit **AI sort**
  helper.
- Never depend on the bundled `os.mail` app or borrow its identity, store
  provider tokens, or claim that a simulated click authorizes sending. The
  review and event safety tests live in OctoSense's `oauth-service` crate.
- Keep the English and Chinese READMEs aligned and the evidence fictional. A
  passing UI fixture doesn't prove live OAuth, model quality, Android usability
  or delivery.
