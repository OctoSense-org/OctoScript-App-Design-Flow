# Developing this OctoSense app

`CLAUDE.md` and `GEMINI.md` only import this file, so every coding agent reads
the same rules.

This repository is one OctoSense script app. `bundle/` is the app and the only
thing submitted to the App Hub; everything else stays outside it.

Follow the docs of OctoScript App Design Flow, the harness this app came from,
and do not invent requirements or APIs:

- Build, run and test: [QUICKSTART](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/QUICKSTART.md)
- The language and every API an app may use: [SCRIPT-API](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/SCRIPT-API.md)
- Capabilities: [CAPABILITIES](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/CAPABILITIES.md)
- Final bundle, screenshots and human checkpoints: [PUBLISHING](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/PUBLISHING.md)
- Signing and the submission issue: App Hub's [SUBMITTING](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md)

Set `OCTO=<path to OctoScript-App-Design-Flow>/tools/octo`, then run this loop
from this directory. The CLI lives in the harness repository, not here; on
Windows, run it as `python $OCTO`.

1. Edit `bundle/main.splash`.
2. Run `$OCTO run bundle --port 8141 --hidden --detach`. It returns after
   `ready: first frame drawn`. If it exits 1, the port is taken: run the
   `curl … /quit` it prints, then try again.
3. Drive the app (`/click`, `/t`, `/snap`), then run `$OCTO shot 8141 out.png`
   and open the PNG.
4. Run `curl -s 127.0.0.1:8141/quit`.
5. Run `$OCTO check bundle`. Expect `— PASSED` with only the unsigned
   warning. Until `bundle/screenshots/01-main.png` exists
   (`$OCTO shot 8141 bundle/screenshots/01-main.png` in step 3), the gate
   refuses the listing; fix every other `[refused]` line before you go on.

Follow these rules:

- Ask only for capabilities a screen uses; declare every `https://` host in
  `network.hosts`; never use `http://`.
- Never collect or store a password, PIN, one-time code, API key or token;
  accounts go through a host service.
- Keep the id's last segment, after its final `.`, off App Hub's reserved
  names (`notes`, `weather`, `terminal` and others); the gate refuses them.
- Put only files the gate accepts in `bundle/`: no `.DS_Store`, no file
  without an extension, 8 MiB at most. Plain `.txt`/`.md` license and
  attribution URLs are allowed; keep required notices. Agent guidance and
  structured resources retain their host/resource checks.
- Capture screenshots from the unsigned bundle with `$OCTO shot`, and look at
  each one; never use a placeholder.
- Restamp after every edit (`$OCTO check` does it). Sign last; any edit
  after signing needs a new stamp and a new signature.
- Keys, `.local-state/`, `build/` and review packets never enter `bundle/` or Git.
- Keep `.gitattributes` (`bundle/** -text`) committed: the digest covers every
  byte, and a line-ending conversion breaks it.
- Stop at human steps: publisher key, publisher details, platform claims, tag,
  submission.

Add this app's own requirements, data sources and tests below.
