# Flows

English | [简体中文](README.zh-CN.md)

A flow turns one kind of input into something OctoSense can run. Pick the flow
by what you have. Run every command from the repository root unless a step
says otherwise.

| You have | Flow | Output | Runtime |
| --- | --- | --- | --- |
| A text brief (what the app does, its screens and data) | [script-app](script-app/FLOW.md) | A contained script app bundle (`manifest.json`, `main.splash`, assets) | App Hub `card-host`, then the OctoSense shell |
| A generated UX image, or a single screen | [image-to-card](image-to-card/FLOW.md) | Native cards in L0, the declarative card language (`page.card`, `page.data.json`, `kit/`), extracted service cards, a card bundle, optionally WASM | App Hub `card-host` after packaging; Makepad Studio or `beauty-host` (see the flow) while iterating |
| A licensed Sketch design kit | [kits/sketch](kits/sketch/FLOW.md) | A **theme kit** (native L0 components and themes), not an app | Consumed by the other flows and by OctoScript-Makepad |
| An existing app in this repository | Its `examples/<name>/README.md`; see [examples/](../examples/README.md) | Whatever that example records | As recorded per example |

For Glance app cards, pair the chosen flow with the
[app-card UX skill](../skills/octoscript-app-card-ux/SKILL.md). It covers usable
presentation depths, host workspace/Chat integration and evidence-based UX
acceptance. It supplements the flow; it does not replace its publishing gates.

Supporting code, not flows:

- [core/](core/README.md): policy, review packets, repair, Studio bridge,
  composition and gates shared by every flow;
  [REPRODUCE.md](core/REPRODUCE.md) is the environment setup and
  [NATIVE-INSTRUMENT.md](core/NATIVE-INSTRUMENT.md) the native test runbook.
- [image-lib/](image-lib/README.md): the image library the image-to-card flow
  calls, with its per-design evidence corpus.
- [STRUCTURE.md](STRUCTURE.md): directory ownership and retention rules;
  [LLM-COMPOSITION.md](LLM-COMPOSITION.md): the composition contract.
- `maintain.py` and `tests/`: storage inventory and cache cleanup.

## Every flow follows the same contract

1. **Prerequisites first.** Each `FLOW.md` has one check command. Run it
   before step 1. If it fails, fix what it names; do not start the flow.
2. **Each step is a command and a pass check.** Run the command exactly, then
   the pass check. Stop on the first failure and report the failing step, the
   command, its exit code and the log path. Do not skip a step, retry a failed
   step until it happens to pass, or edit recorded evidence to make a check
   pass.
3. **Human checkpoints.** A step marked **HUMAN** is where an agent stops,
   reports what is ready, and waits for a person. The checkpoints are:
   - **Image generation with a paid generator.** A person runs the generator
     (or explicitly authorizes the spend) and supplies the original output
     and the exact prompt.
   - **Semantic and visual review.** A person (or a reviewer they name)
     checks the mapping against the source image and approves screenshots.
     A passing script is not a visual approval.
   - **Publisher identity and release workflow.** Review the GitHub repository,
     workflow and release tag before publication. App Hub accepts only
     GitHub-attested releases, so no publisher key is involved: never create
     one, sign a manifest or pass `--publisher-key` to publish.
   - **Release and submission.** Tagging the release and opening the
     `Submit <app id> <version>` issue on OctoSense-App-Hub
     ([SUBMITTING §7](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#7-open-the-submission-issue))
     are a person's decisions.
   - Flow-specific checkpoints (for example, buying Sketch or a design kit)
     are listed in that flow's steps table.
4. **Common hand-off.** Every app flow ends the same way. Set these first:

   - `HUB_BIN` and `CARD_HOST_BIN`: the paths of the `hub` and `card-host`
     binaries, built in [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)
     with `cargo build --release -p octosense-card-host -p octosense-app-hub`
     ([QUICKSTART §2](../docs/QUICKSTART.md#2-build-hub-and-card-host)).
   - `APP_REPO`: the absolute path of the app's repository, which holds
     `bundle/`.

   If the build fails with `no variant … TextInputStateQuery`, see [The `card-host` build fails on `TextInputStateQuery`](../docs/QUICKSTART.md#the-card-host-build-fails-on-textinputstatequery).

   | # | Step | Command | Pass when |
   | --- | --- | --- | --- |
   | 1 | Package as an App Hub bundle | per flow; see its `FLOW.md` "Hand-off" | `bundle/` holds `manifest.json`, `listing.json`, the program (`page.card` + `kit/`, or `main.splash`) and `assets/`, and no file of another type (such as `.DS_Store`) |
   | 2 | Stamp | `"$HUB_BIN" stamp "$APP_REPO/bundle"` | prints the digest |
   | 3 | Check | `"$HUB_BIN" check "$APP_REPO/bundle" --allow-unsigned` | only the expected screenshot refusal and unsigned warning remain |
   | 4 | Run in `card-host` | from the App Hub checkout: `"$CARD_HOST_BIN" --bundle "$APP_REPO/bundle" --app-data "$APP_REPO/.local-state" --allow-unsigned --remote 8141` | the log shows `[makepad-remote] listening on 127.0.0.1:8141` and no `refused` line |
   | 5 | Screenshot | in a second terminal, from this repository: `tools/octo shot 8141 "$APP_REPO/bundle/screenshots/01-main.png"`, then `curl -sS 127.0.0.1:8141/quit`. `shot` waits for the app's widgets and a settled frame. | the PNG shows the app, not an error frame (**HUMAN** review) |
   | 6 | Restamp and check | `"$HUB_BIN" stamp "$APP_REPO/bundle" && "$HUB_BIN" check "$APP_REPO/bundle" --allow-unsigned` | only the unsigned warning remains |
   | 7 | Review questions | `mkdir -p "$APP_REPO/build" && "$HUB_BIN" scan "$APP_REPO/bundle" --packet "$APP_REPO/build/review.json"` | the packet is written and its questions are answered in writing: seven, or eight when the bundle ships `tools.json`, `AGENT.md` or skills |
   | 8 | Request publication (**HUMAN**, may happen earlier) | Open `Submit <app id> <version>` on App Hub with repo/version/commit, screenshots and permissions | The issue records the request; missing release artifacts can be added later |
   | 9 | Prepare release (**HUMAN** for public actions) | `tools/octo publish-github "$APP_REPO"`; review/commit tested source and workflow, then push a new `v<manifest.version>` tag | GitHub `publisher-verify` and `publisher-pack` succeed; attach release/pack/digest to the issue |
   | 10 | Hub review | Hub checks the exact candidate; administrator reviews and approves it | Authenticated catalog publication completes; a GitHub release alone is not approval |

   `card-host` refuses sealed releases, so test and capture the editable source
   first. The release workflow needs contract 1.8.0 / `publisher-github-v1`, and
   installing a release needs a compatible host, such as OctoSense desktop
   0.1.0-rc.1 on macOS. The table lists pass conditions, not test results.
   This repository's [docs/PUBLISHING.md](../docs/PUBLISHING.md) covers the flow. App Hub's
   [SUBMITTING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md)
   covers the submission issue and review, and its
   [PUBLISHING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md)
   is the reference for every gate rule.
5. **Purchased assets stay private.** Never share purchased design assets or
   local logs as generic examples.

## Clean up local storage

```sh
python3 flows/maintain.py inventory            # read-only storage inventory
python3 flows/maintain.py clean --exports      # preview cache cleanup
python3 flows/maintain.py clean --exports --apply
```

The cleaner removes only Python bytecode, Finder metadata and, with
`--exports`, Sketch export caches that can be rebuilt. Sources, final assets,
screenshots, review rounds and environments are outside its scope.
