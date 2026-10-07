# Native App Card testing with Makepad's built-in instrument

Use the app's built-in HTTP instrument for new native UI inspection and interaction tests. Build a release executable and launch it directly with `--remote`. Automated tests can hide its native window with `MAKEPAD_HIDE_WINDOWS=1`. Studio, RunItem and the Studio bridge are not required for this workflow.

Use it for image-to-appcard projects. The intake, semantic-mapping, L0 compilation, service-reducer, bundle and visual-review steps don't change. Studio capture commands use Studio; see [Existing capture/gate compatibility](#existing-capturegate-compatibility).

For a model that generates and repairs the app, pair this runbook with
[model-driven validation](../../docs/MODEL-VALIDATION.md). That guide covers startup
failures, language confusion, clipping, stale state and source-bound feedback,
plus the separate Android capture and input paths.

## Build and launch an owned instance

Follow Makepad's agent runbook (`AGENTS.md`) and app remote reference (`docs/agents/app-remote.md`) in the `makepad` checkout that `python3 tools/setup-native.py` prepares beside this repository (`$OCTOSENSE_WORKSPACE/makepad`). Read the running binary's `GET /` response for its actual protocol. Use a fresh release build after runtime changes, and record the source revisions and local adapter patches.

From this repository's root, for the existing `beauty-host` L0 adapter:

```sh
APP_PIPELINE_ROOT="$PWD"
APP_NATIVE_REQUEST="/absolute/path/to/app/runtime/current-request.json"
APP_NATIVE_LOG="$(mktemp -t appcard-native)"
OCTOSENSE_WORKSPACE="${OCTOSENSE_WORKSPACE:-$(dirname "$PWD")}"
cd "$OCTOSENSE_WORKSPACE/octoscript-makepad"
RUSTFLAGS='' CARGO_PROFILE_RELEASE_LTO=false cargo build --release -p kit-host --bin beauty-host
MAKEPAD_HIDE_WINDOWS=1 BEAUTY_REQUEST="$APP_NATIVE_REQUEST" \
  ./target/release/beauty-host --remote > "$APP_NATIVE_LOG" 2>&1 &
APP_NATIVE_PID=$!
```

The request file must already be authored by the app/controller. It identifies the compiled `.card`, data JSON, kit directory, dimensions, unique request `nonce`, output paths for native/layout/action evidence and a unique launch identity. The current host also accepts that standalone identity in its historical `build_id` field; it is not a Studio build ID. Mount one request at a time. Do not let two controllers share a request or action file.

Run the executable from its owning workspace so resources resolve correctly. Start a loopback artwork server only when compiled assets require one. Set the app's own credential/configuration path separately; never place credentials in the request or launch arguments.

The startup log contains the instrument endpoint and owned process:

```text
[makepad-remote] listening on 127.0.0.1:PORT pid=PID app=beauty-host grabs=...
```

Retain that PID and endpoint. Do not discover or take over an unrelated running app. For a visible hand-off, omit `MAKEPAD_HIDE_WINDOWS`; do not activate the window unless the user asks.

**Headless here means a hidden native window.** The tested macOS route retains Metal, native controls and platform WebViews. It still needs a native macOS session. **Unverified:** the separate `cfg(headless)` software renderer, a display-free Linux runner, iOS and WebAssembly.

## Inspect and inject real input

Set `APP_NATIVE_ENDPOINT` to the endpoint printed by that launch:

```sh
APP_NATIVE_ENDPOINT="http://127.0.0.1:PORT"   # from the [makepad-remote] log line
curl --fail --silent --show-error "$APP_NATIVE_ENDPOINT/"
curl --fail --silent --show-error "$APP_NATIVE_ENDPOINT/s"
curl --fail --silent --show-error --get "$APP_NATIVE_ENDPOINT/snap" \
  --data-urlencode 'q=TextInput' --data 'all=1'
```

`/snap` returns `s` entries with these fields:

| Field | Meaning |
| --- | --- |
| `i` | native widget ID |
| `ty` | type |
| `w` | window |
| `r` | `[x, y, width, height]` in window-local logical points |
| `t`, `val` | text, value |

Resolve source IDs through the compiled `mapping.json`, then select the exact native ID. A substring query may also match descendants. `all=1` includes otherwise omitted widgets; it does not prove they are visible or clickable.

**Rectangles are window-local logical points.** Do not add the OS window position or multiply by DPI. Fetch fresh bounds after a mount, scroll or resize. Click within the current visible rectangle:

```sh
# X and Y come from the latest native /snap rectangle.
curl --fail --silent --show-error --get "$APP_NATIVE_ENDPOINT/click" \
  --data "x=$APP_CLICK_X" --data "y=$APP_CLICK_Y" --data 'wait=1'
curl --fail --silent --show-error --get "$APP_NATIVE_ENDPOINT/k" \
  --data 'k=press' --data 'c=KeyA' --data 'cmd=1' --data 'wait=1'
curl --fail --silent --show-error --get "$APP_NATIVE_ENDPOINT/t" \
  --data-urlencode 't=pop.example.com' --data 'wait=1'
curl --fail --silent --show-error --get "$APP_NATIVE_ENDPOINT/m" \
  --data 'k=scroll' --data 'x=200' --data 'y=450' --data 'dy=600' --data 'wait=1'
```

`wait=1` waits for the resulting native frame. Also wait for the app's controller/reducer and request nonce to settle before asserting an asynchronous change. Acceptance tests must observe real native actions and resulting state; directly calling a reducer is a unit test, not an input test. Cover disabled controls, validation, retry, stale responses, selection/focus across redraws and scroll restoration where relevant.

Use `/d` for the native tree and `/log?n=50` for app logs. Assert geometry and clipping from the host's measured layout where `/snap` reports only the clipped rectangle. Do not substitute rendered text or an entire screenshot for a native control.

## Capture, provenance and cleanup

Use `/g` to capture the app's own drawable. It returns a `png` path; `/g?raw=1` returns PNG bytes. A screenshot is evidence for visual inspection, not automatic visual approval. Platform overlays such as WKWebView may require the app's existing WebKit inspection/snapshot hook; do not claim a Metal capture includes them. Do not substitute an OS/window/display screenshot for this app-owned rendering evidence. Platform integration captures have a separate scope, described below.

Record at least:

- Native executable and relevant source/artifact hashes, launch identity, PID, hidden/visible mode and request nonce.
- The instrument protocol response, native snapshots/tree, observed action/result evidence and app-owned captures needed by the change.
- Fixture versus real-service checks, passed/failed assertions and unrun visual, browser or platform checks.
- Cleanup result for each temporary test process.

Keep personal mail, credentials and real-account captures under private ignored storage. Publish fictional fixtures and counts-only live-service receipts.

A masked TextInput can still expose its underlying value through inspection or action logging. Use a secure platform credential dialog with a private controller pipe, or an explicitly protected credential channel. Do not type real passwords through `/t`, put them in URLs, or copy them into card data, snapshots, prompts or logs.

Finish every temporary test instance with:

```sh
curl --fail --silent --show-error "$APP_NATIVE_ENDPOINT/gq"
wait "$APP_NATIVE_PID"
```

`/gq` returns `png` as an **array of paths** and `quit: 1`; `/g` returns one path. Copy any required evidence and confirm the process exited. If capture is unavailable, use `/quit`. If `/gq` already closed the process, a failed second request is not a reason to relaunch. Preserve an instance only when handing the app to the user as requested. A human-closed window is not a crash to auto-restart.

## Working examples

- [`flows/image-to-card/compare_screens.py`](../image-to-card/compare_screens.py)
  launches one fresh `beauty-host --remote` per compiled scene, grabs `/g`,
  probes every text widget's `/snap` rectangle for ink and writes side-by-side
  evidence. Its rules are in [VISUAL-CHECKS.md](../image-to-card/VISUAL-CHECKS.md).
  Run it with the image library's Python, which has numpy, as
  [FLOW.md](../image-to-card/FLOW.md) does:

  ```sh
  OCTOSENSE_WORKSPACE="${OCTOSENSE_WORKSPACE:-$(dirname "$PWD")}"
  BEAUTY_PYTHON="$PWD/flows/image-lib/.venv/bin/python"
  "$BEAUTY_PYTHON" flows/image-to-card/compare_screens.py \
    --project examples/calendar --pages <page-images> \
    --out examples/calendar/evidence/screenshots \
    --host "$OCTOSENSE_WORKSPACE/octoscript-makepad/target/release/beauty-host"
  ```

  `<page-images>` is a directory of `page-NN.png` references.
- The reference journeys in [examples/](../../examples/README.md) record their
  native evidence per project. Their older verifiers (for example
  `examples/aircon/scripts/verify_standalone_cards.py`) are Studio-backed; see
  the compatibility boundary below.
- A packaged OctoSense app runs in App Hub's `card-host`, which exposes the
  same instrument: launch it with `--remote`, inspect with `/snap` and `/d`,
  drive it with `/click`, `/k` and `/t`, capture with `/g` and close with `/gq`.
  `card-host` serves no host services; a call to one fails with
  `no service answers "…" on this device`. [QUICKSTART.md](../../docs/QUICKSTART.md)
  shows how to run and capture an app.

## Other platforms

The pinned Makepad release compiles its HTTP `--remote` instrument out on
Android. Desktop HTTP or desktop Studio results do not establish an Android or
OpenHarmony pass. Android's in-shell Studio tools are a separate implementation:
the reviewed OctoSense build opens visible contained apps, injects Makepad events
and captures their textures. Its L0 render tool returns a PNG without an
interactive instance. Record the actual platform, runtime and capture route;
see the [test-surface matrix](../../docs/MODEL-VALIDATION.md#choose-the-test-surface).

Keep Android OS screenshots as separately labelled **platform integration
evidence** when testing the real keyboard, system notifications or an authorized
other APK. They do not replace app-texture captures or establish native widget
geometry. Android offers MediaProjection and accessibility screenshot APIs, but
the reviewed Studio tools do not expose arbitrary cross-APK capture or a fully
hidden phone session. The [Android capture guide](../../docs/MODEL-VALIDATION.md#capture-another-android-apk)
records consent, protected-content and input-control boundaries. Supporting a new
capture service belongs in the runtime, not in this flow's evidence adapters.

## Existing capture/gate compatibility

`flows/image-lib/studio.py` and the flow runner's `capture --launch` stage are Studio-backed capture adapters. They don't use the direct HTTP instrument. Their saved-round gates expect their existing evidence schema. Preserve prior evidence; do not invent Studio IDs or relabel a direct snapshot as a legacy gate pass.

For new direct-instrument app work, run the shared authoring/compile/service stages explicitly, then the project's owned native verifier:

```sh
bash tools/image-to-appcard-flow.sh run \
  --project "$FLOW_PROJECT" --manifest "$FLOW_PROJECT/image-to-appcard-flow.json" \
  --stages semantic,compile,bundle,service-test
```

Do not select legacy `capture --launch` for a request to test without Studio. Keep direct-instrument results alongside the project's evidence with explicit provenance. **Not yet:** the shared capture and gate stages don't read direct-instrument results; report them as unrun. Semantic correctness, native interaction, source-image fidelity, visual review and browser/platform acceptance remain separate decisions.


## Shared runtime

All flows select the root `native-runtime.lock.json`; its OctoScript-Makepad
release owns the underlying `runtime.json`. Prepare the sibling sources with
`python3 tools/setup-native.py` and verify them with
`python3 tools/setup-native.py --check`. WASM does not apply private framework
patches. Preserve existing edits before updating a checkout. See
[NATIVE-WORKSPACE.md](../../docs/NATIVE-WORKSPACE.md).
