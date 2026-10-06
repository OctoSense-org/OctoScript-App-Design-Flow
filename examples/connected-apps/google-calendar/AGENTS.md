# Developing this OctoSense app

> **Any coding agent, or none.** These instructions work the same for Codex, Claude Code, Cursor, Gemini CLI, GitHub Copilot or a person at a terminal: every step is a shell command or a file edit, and nothing here needs a particular agent, model or vendor. `AGENTS.md` is the one source of truth; `CLAUDE.md` and `GEMINI.md` only import it for agents that look for those names.

This repository is one OctoSense script app. `bundle/` is the app and the only
thing submitted to the App Hub; everything else stays outside it.

Follow the harness, and do not invent requirements or APIs:

- How to build, run and test: [QUICKSTART](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/QUICKSTART.md)
- The language and every API an app may use: [SCRIPT-API](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/SCRIPT-API.md)
- Capabilities: [CAPABILITIES](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/CAPABILITIES.md)
- Publishing, step by step, with the human checkpoints: [PUBLISHING](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/PUBLISHING.md)

The loop, with `OCTO=<path to OctoScript-App-Design-Flow>/tools/octo` (the CLI
lives in the harness repository, not here), run from this directory: edit
`bundle/main.splash` → `$OCTO run bundle --port 8141 --detach` → drive it
(`/click`, `/t`, `/snap`) and `$OCTO shot 8141 out.png` → `curl -s 127.0.0.1:8141/quit`
→ `$OCTO check bundle`.

Rules:

- Ask only for capabilities a screen uses; declare every `https://` host in
  `network.hosts`; never `http://`.
- Never collect a password, PIN or code; accounts go through a host service.
- Screenshots are real captures you looked at. Never a dummy.
- Restamp after every edit (`tools/octo check` does it). After signing, any
  edit needs a new stamp and signature.
- Keys, `.local-state/`, `build/` and review packets never enter `bundle/` or git.
- Stop at human steps: publisher key, publisher details, platform claims, submission.

Add this app's own requirements, data sources and tests below.

## This connected sample

- Follow BRIEF.md and the shared OAuth service contract. The app ID is ordinary,
  never os.calendar. Host credentials remain outside the bundle.
- Run the root-relative native verifier documented in README.md; it uses its
  own hidden process and synthetic local draft. Do not label it Google API or
  Android validation. Preserve runtime failures and resulting repairs.
- Keep the local draft as one state object for editing and host review. Dynamic
  Splash object keys need JSON string-key semantics; exact saved-file checks
  protect against duplicate identifier/string keys.
- Chat is advisory until an executable, approved tool path is added. An agent's
  statement cannot count as a Calendar write receipt.
- Retain original event identity, ETag, timezone and exclusive provider end date.
  Never make recurring series look like one editable occurrence.
- Read cache/prepare behavior in OctoSense crates/oauth-service/src/calendar_cache.rs
  and connector dispatch in host_api.rs before changing method names or shapes.

- Integrated acceptance uses `scripts/verify-installed.py` and
  `scripts/verify-shell.py` against the companion OctoSense examples built with
  the non-default `acceptance-fixtures` feature. They sign temporary copies and
  install through the real Store; only Calendar transport/vault are synthetic.
  Preserve source/executable/capture hashes and distinguish this from Google
  OAuth, physical approval, phone tests and real model calls.
- Never put model profiles, OAuth configuration, keys or private run directories
  in public evidence. An optional real-model run uses caller-supplied private
  profile and kernel paths, copies only the needed model settings into an
  isolated temporary home, and exposes only synthetic event data.
