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

1. Edit `bundle/main.splash`.
2. Run `$OCTO run bundle --port 8141 --hidden --detach`. It prints
   `ready: first frame drawn`; on a failure it prints the log tail and stops the
   `card-host` it started.
3. Drive the app (`/click`, `/t`, `/snap`), then run `$OCTO shot 8141 out.png`
   and open the PNG. Without a host service, the agenda is empty and shows
   `Google sign-in unavailable: no service answers "auth" on this device`.
4. Run `curl -s 127.0.0.1:8141/quit`.
5. From the App Flow root, run
   `python3 examples/connected-apps/google-calendar/scripts/verify-native.py`.
   It prints a JSON summary with `"passed": 5`.
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
- Restamp after every edit (`$OCTO check` does it). Never edit a sealed
  release: a change needs a new version and tag, and the release workflow
  attests it.
- Keep keys, `.local-state/`, `build/` and review packets out of `bundle/` and
  Git.
- Stop at human steps: publisher details, workflow review, platform claims,
  tag, submission.

## This sample

- Version 0.1.0 is published from
  [ymote/octosense-google-calendar](https://github.com/ymote/octosense-google-calendar).
  This directory is the unsigned development copy; its `listing.json` keeps
  publisher placeholders.
- Don't submit this copy. Its ID and version are already in the App Hub
  catalog, so the gate refuses it with `version` and `continuity` findings. A
  new app needs its own ID, tool namespace and `main.splash` app references;
  follow [Start your own app from one](../README.md#start-your-own-app-from-one).
- Follow [BRIEF.md](BRIEF.md) and OctoSense's
  [oauth-service README](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/crates/oauth-service/README.md).
  The `id` is an ordinary store ID, never `os.calendar`. Host credentials stay
  outside the bundle.
- `scripts/verify-native.py` starts its own hidden process and uses a synthetic
  local draft. Don't label it Google API or Android validation. Record runtime
  failures and their fixes in [ACCEPTANCE.md](ACCEPTANCE.md).
- Keep the local draft as one state object for editing and host review. Write
  dynamic object keys as strings, as JSON does; the saved-file checks catch a
  key stored once as an identifier and once as a string.
- Chat is advisory until an executable, approved tool path is added. An agent's
  statement can't count as a Calendar write receipt.
- Keep the original event identity, ETag, timezone and exclusive provider end
  date. Never make a recurring series look like one editable occurrence.
- Read the cache and prepare behavior in OctoSense's
  `crates/oauth-service/src/calendar_cache.rs` and the connector dispatch in
  `host_api.rs` before changing method names or shapes.
- Integrated acceptance uses `scripts/verify-installed.py` and
  `scripts/verify-shell.py` against the companion OctoSense examples built with
  the non-default `acceptance-fixtures` feature. They sign temporary copies and
  install through the real Store; only the Calendar transport and vault are
  synthetic. Keep the source, executable and capture hashes, and don't present
  this as Google OAuth, physical approval, phone tests or real model calls.
- Never put model profiles, OAuth configuration, keys or private run
  directories in public evidence. An optional real-model run uses
  caller-supplied private profile and kernel paths, copies only the needed
  model settings into an isolated temporary home, and exposes only synthetic
  event data.
