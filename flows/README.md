# Flows

English | [简体中文](README.zh-CN.md)

A flow turns one kind of input into something OctoSense can run. Pick the flow
by what you have. Run every command from the repository root.

| You have | Flow | Output | Runtime |
| --- | --- | --- | --- |
| A text brief (what the app does, its screens and data) | [script-app](script-app/FLOW.md) | A contained script app bundle (`manifest.json`, `main.splash`, assets) | App Hub `card-host`, then the OctoSense shell |
| A generated UX image, or a single screen | [image-to-card](image-to-card/FLOW.md) | Native L0 cards (`page.card`, `page.data.json`, `kit/`), extracted service cards, a card bundle, optionally WASM | App Hub `card-host` after packaging; Studio or `beauty-host` while iterating |
| A licensed Sketch design kit | [kits/sketch](kits/sketch/FLOW.md) | A **theme kit** (native L0 components and themes). Not an app | Consumed by the other flows and by Octoscript-Makepad |
| An existing app in this repository | its `examples/<name>/README.md`; see [examples/](../examples/README.md) | Whatever that example records | As recorded per example |

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

1. **Prerequisites first.** Each FLOW.md has one check command. Run it before
   step 1. If it fails, fix what it names; do not start the flow.
2. **Each step is a command and a pass check.** Run the command exactly, then
   the pass check. Stop on the first failure and report the failing step, the
   command, its exit code and the log path. Do not skip a step, retry a failed
   step into a pass, or edit recorded evidence to make a check pass.
3. **Human checkpoints.** A step marked **HUMAN** is where an agent stops,
   reports what is ready, and waits for a person. The checkpoints are:
   - **Image generation with a paid generator.** A person runs the generator
     (or explicitly authorizes the spend) and supplies the original output
     and the exact prompt.
   - **Semantic and visual review.** A person (or a reviewer they name)
     checks the mapping against the source image and approves screenshots.
     A passing script is not a visual approval.
   - **Signing with private keys.** Only the key holder runs `hub keygen` or
     `hub sign-manifest`. Keys never enter the repository, the bundle, a
     prompt or a log.
   - **Submission.** Opening the `Submit <app id> <version>` issue on
     OctoSense-App-Hub ([PUBLISHING §3.8](../docs/PUBLISHING.md#38-submit--human))
     is a person's decision.
   - Flow-specific checkpoints (for example, buying Sketch or a design kit)
     are listed in that flow's steps table.
4. **Common hand-off.** Every app flow ends the same way:

   | # | Step | Command | Pass when |
   | --- | --- | --- | --- |
   | 1 | Package as an App Hub bundle | per flow; see its FLOW.md "Hand-off" | `bundle/` holds `manifest.json`, `listing.json`, the program (`page.card` + `kit/`, or `main.splash`) and `assets/` |
   | 2 | Stamp | `"$HUB_BIN" stamp bundle` | prints the digest |
   | 3 | Check | `"$HUB_BIN" check bundle --allow-unsigned` | only the expected screenshot refusal and unsigned warning remain |
   | 4 | Run in `card-host` | `"$CARD_HOST_BIN" --bundle "$PWD/bundle" --app-data "$PWD/.local-state" --allow-unsigned --remote` (from the App Hub checkout) | the log shows the remote endpoint and no `refused` line |
   | 5 | Screenshot | `curl --fail -sS "$APP_ENDPOINT/g?raw=1" -o bundle/screenshots/01-main.png`, then `curl -sS "$APP_ENDPOINT/quit"` | the PNG shows the app, not an error frame (**HUMAN** review) |
   | 6 | Restamp and check | `"$HUB_BIN" stamp bundle && "$HUB_BIN" check bundle --allow-unsigned` | only the unsigned warning remains |
   | 7 | Sign (**HUMAN**) | `"$HUB_BIN" sign-manifest bundle --key "$APP_SIGNING_KEY" --key-id "$APP_PUBLISHER_ID"` | `"$HUB_BIN" check bundle --publisher-key "$APP_PUBLISHER_ID=$APP_PUBLISHER_PUBLIC_KEY"` passes, where `APP_PUBLISHER_PUBLIC_KEY="$("$HUB_BIN" pubkey "$APP_SIGNING_KEY")"` |
   | 8 | Submit (**HUMAN**) | open a `Submit <app id> <version>` issue on OctoSense-App-Hub ([PUBLISHING §3.8](../docs/PUBLISHING.md#38-submit--human)) | a maintainer re-runs the gate on the exact bytes |

   `HUB_BIN` and `CARD_HOST_BIN` are the `hub` and `card-host` binaries built
   from [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)
   (`cargo build --release -p octosense-app-hub --bin hub` and
   `cargo build --release -p octosense-card-host --bin card-host`). The
   current `card-host` refuses signed manifests, so take screenshots before
   signing. This repository's [docs/PUBLISHING.md](../docs/PUBLISHING.md)
   walks the hand-off for script apps; the contract itself is App Hub's
   [docs/PUBLISHING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md).

## Storage

```sh
python3 flows/maintain.py inventory            # read-only storage inventory
python3 flows/maintain.py clean --exports      # preview cache cleanup
python3 flows/maintain.py clean --exports --apply
```

The cleaner removes only Python bytecode, Finder metadata and, with
`--exports`, Sketch export caches that can be rebuilt. Sources, final assets,
screenshots, review rounds and environments are outside its scope. Do not
share purchased assets or local logs as generic examples.
