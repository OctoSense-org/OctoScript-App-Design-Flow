# image-to-appcard-flow

Turn **one generated atlas containing 8–12 related UX screens** into measured
native Makepad scenes, reusable service App Cards, a click-driven service flow,
and a WebAssembly package for the OctoSense Astro website.

This extends the existing [image adapter](../image-to-appcard/README.md).
It reuses that adapter's semantic compiler. New native testing uses
[Makepad's built-in HTTP instrument](../core/NATIVE-INSTRUMENT.md), with a
standalone release executable and hidden windows when needed. It does not
generate a separate image per state or turn screenshots into clickable hotspots.

```text
service scenario + shared state/actions + bilingual copy
  → one high-resolution atlas, exact submitted prompt, actual generation receipt
  → measured crops + reversible reference transforms
  → reviewed semantic map → native L0 + kit + data + source/widget mapping
  → independently owned service card subtrees
  → service reducer + app/desktop bindings + native KitAction inputs
  → built-in native instrument inspection and separate visual review
  → single-threaded Makepad WASM + hashed artwork/font package
  → atomic Astro integration → real native clicks in EN/CN and mobile
```

## Entry point

Commands run from the Octoscript-AppCard repository. Install the image adapter's
[Python environment](../core/REPRODUCE.md) and follow the
[standalone native testing guide](../core/NATIVE-INSTRUMENT.md). Node is needed
for service/browser checks; a Rust WASM target and matching `cargo-makepad` are
needed only when rebuilding native code.

```sh
export BEAUTY_PYTHON="$PWD/lab/image-to-appcard/.venv/bin/python"
export FLOW_PROJECT="/path/to/Octosense-Service-AppCards/apps/aircon"
export FLOW_SITE="/path/to/Octosense-website"

bash tools/image-to-appcard-flow.sh plan \
  --project "$FLOW_PROJECT" --manifest "$FLOW_PROJECT/image-to-appcard-flow.json"

bash tools/image-to-appcard-flow.sh run \
  --project "$FLOW_PROJECT" --manifest "$FLOW_PROJECT/image-to-appcard-flow.json" \
  --stages intake,semantic,compile,bundle,service-test
```

`tools/beauty-pipeline.sh --image-to-appcard-flow` is the equivalent shared entry.
`plan` prints exact argument arrays without running them. `run` stops at the first
failure, retaining logs and a run receipt under `pipeline-output/runs/`. `status`
shows the latest receipt and whether its input fingerprint still matches. A
successful command is not a visual acceptance: every receipt lists unrun stages.
Re-running creates a new receipt; a failed run is never overwritten or silently
retried. `--node /path/to/node` or `SERVICE_NODE` selects an installed Node binary.
Check commands may use `{python}`, `{node}`, `{project}`, `{workspace}` and
`{website}` as complete arguments. They run without shell evaluation. Their
`cwd` is relative to the service project, or exactly `{website}`.

The [aircon manifest](examples/aircon.flow.json) uses the external 12-scene service
project already created for OctoSense. It contains relative paths, source crop
measurements, 14 service surface declarations, and test commands. The original
generated imagery, service implementations, fonts and archived evidence stay in
that separate project; the manifest does not download or fabricate them.

## 1. Author the whole experience before generating

Use the [atlas prompt template](examples/atlas-prompt.md). Describe 8–12 states in
one request, with one palette, typography system, recurring service identity and
fixture. Request the highest supported output size and quality from the selected
generator. Preserve the actual output dimensions separately from requested size;
upscaling is not higher-resolution generation. Save the exact submitted prompt
and original output bytes. Never put credentials in prompts or manifests.

Each scene declares `surface: app` or `surface: desktop`. The application retains
familiar browsing, reading and editing. A desktop App Card belongs to a service:
it announces a concrete update, shows the relevant data and offers scoped actions.
For example, an authorized school sender can update the calendar; the calendar
card then offers acknowledgment and undo. A separate payment card still requires
explicit payment. A generic chat transcript is not the navigation model.

The flow manifest has `schema_version: 1`, `id`, `artboard: [406,776]`,
`locales: ["en","cn"]`, `generation`, `scenes`, `cards`, `artwork`, `outputs`,
`browser_modules`, and `checks`. Each scene supplies a unique string `id`,
`design_id`, relative `directory`, reviewed atlas `crop: [x,y,width,height]`, and
surface. The generator is external: this pipeline records provider/model facts
but does not call an image API or claim automatic visual interpretation.

## 2. Preserve and measure the atlas

Run `--stages intake`. It validates every crop against the decoded atlas, rejects
overlaps and duplicate IDs, and saves exact crops plus letterboxed references at
the native artboard's 2× backing resolution. The receipt carries original hashes,
actual dimensions, scale, padding, forward/inverse transforms and derived hashes.
The original atlas and prompt remain unchanged. Same-input replay is idempotent;
changed or edited intake requires a new output directory.

Review each reference, OCR, artwork boundary, native font metrics and semantic
intent using [the mapping rules](../image-to-appcard/MAPPING-RULES.md). Author
`contract.json`, `mapped.json`, `semantic-map.json` and `service-actions.json` in
the scene directory, with the reference and prompt. Intake does not author an
invented mapping. `native.py` fails clearly if the reviewed files are missing.

For a new flow, `--stages prepare` installs the frozen reference, exact prompt and
generation/crop provenance into each new scene directory. It refuses existing
design directories. Author the native contract using
[the contract example](../core/examples/image-contract.json), then run
`--stages observe,measure,map` for Apple Vision OCR, source surface measurement
and an initial native mapping. Review and resolve semantic decisions and add
service actions before `semantic,compile`. An existing `mapped.json` blocks a fresh
map, and an existing `annotations.json` is retained. Use a new design version for
new source measurements rather than replacing reviewed work.
Keep requested layout separate from observed pixels. Preserve manual repairs;
the flow runner never silently reruns `map` or `catalogue.py`.

## 3. Compile and extract service cards

`semantic,compile` reuse the image adapter. Text is native Label/rich text,
controls are native buttons/inputs, surfaces are Views and icons are native SVG.
Only declared, hash-verified artwork may remain raster. Charts must bind native
numerical widgets. Every source ID remains linked to its actual native widget.

`--stages extract` reads `cards: [{id, scene, root, owner}]`. It extracts each
declared native subtree, translates its origin, filters actions/semantics, carries
artwork provenance, and compiles an independent L0/kit card. Ownership is explicit,
not guessed from a heading. Outputs go to `outputs.cards`; use a new directory for
a changed extraction to preserve reviewed cards. A card reference crop is review
material, never its runtime UI. Independent mounting, input and layout verification
remain required; compiling a subtree does not claim that validation.

## 4. Bind service state and interaction

The application supplies the reducer, state-to-L0 binding, and browser controller
listed in `browser_modules`. The current website integration expects
`wizard/service.mjs`, `wizard/render.mjs`, and `wizard/wizard.mjs`. A new email or
health flow needs its own authored service rules and matching website UI; this
tool does not infer business logic from image pixels.

Use stable service IDs shared by app and desktop views. An event carries unique
ID, actor, action and payload; reject stale state and duplicate side effects.
Provider updates cannot grant user approval. Recheck scheduling conflicts when
confirming; use integer minor currency units. Undo affects its named service
operation: undoing a calendar entry does not cancel a booking; canceling a pending
payment does not refund or cancel a completed installation.

Advance only on a native user action or an explicitly supplied provider update.
An animation may transition between resolved states; it must not schedule the next
business event. Back/Restart restore local demo snapshots and do not claim to
reverse real transactions. Test reducer invariants and all branches in
`checks.service-test`, including disabled actions, duplicate payments, undo/restore,
conflict selection and app/desktop data agreement. The current aircon reducer has
matching Python and browser fixtures; a slideshow index is not its service state.

## 5. Native and visual evidence

Use [the built-in instrument workflow](../core/NATIVE-INSTRUMENT.md) for new
native UI tests: release build, direct `--remote` launch, optional
`MAKEPAD_HIDE_WINDOWS=1`, `/snap` bounds, native `/click`/`/k`/`/t` input,
app-owned `/g` captures, and `/gq` cleanup. Record the launch identity, PID,
request nonce, source hashes and observed service state. The guide includes
the native mail-server settings implementation and its headless checks.

The commands below are **legacy Studio capture/gate replay**, not the direct
instrument path. `native.py` still delegates capture to the Studio adapter;
this documentation does not migrate that implementation or its evidence schema.
When Studio is excluded, run `semantic,compile,bundle,service-test`, then the
project's direct-instrument verifier. Report legacy capture/gate as unrun.

```sh
bash tools/image-to-appcard-flow.sh run \
  --project "$FLOW_PROJECT" --manifest "$FLOW_PROJECT/image-to-appcard-flow.json" \
  --stages capture --launch
# Inspect/review the current screenshots using the existing review packet tools.
bash tools/image-to-appcard-flow.sh run \
  --project "$FLOW_PROJECT" --manifest "$FLOW_PROJECT/image-to-appcard-flow.json" \
  --stages gate
```

For an explicitly requested legacy replay, start the matching Studio/bridge/artwork
servers as described in the reproduction guide and use its release RunItem.
That legacy adapter captures WidgetTreeDump, WidgetQuery, WidgetSnapshot, layout and
clipping, Screenshot and Click results. Bind evidence to build ID, request nonce
and source hashes; disabled controls must not emit activation. Serialize capture
and service watchers. The flow capture lock coordinates flow runner jobs, but
cannot stop an independently started watcher. It only creates temporary design
aliases if absent and never replaces another design's directory.

Native structure, image fidelity, visual review and service correctness remain
distinct. `gate` retains the existing strict image/semantic/native/visual decision
and exits nonzero on failure. A browser test or a runnable prototype does not
upgrade an unaccepted visual comparison. Prior Studio evidence stays immutable.

## 6. Package and integrate WASM

```sh
bash tools/image-to-appcard-flow.sh run \
  --project "$FLOW_PROJECT" --manifest "$FLOW_PROJECT/image-to-appcard-flow.json" \
  --stages bundle,wasm,integrate --website "$FLOW_SITE"

bash tools/image-to-appcard-flow.sh run \
  --project "$FLOW_PROJECT" --manifest "$FLOW_PROJECT/image-to-appcard-flow.json" \
  --stages web-test --website "$FLOW_SITE"
```

`bundle.py` exports native scenes and only their referenced, declared artwork with
hashes. It excludes screen rasters and does not assert visual approval.
[wasm/](wasm/README.md) contains the portable Makepad host, build entry, pinned
dependency/patch receipt and browser transport. Source compatibility changes are
reproduced without silently modifying another checkout. Normal Astro builds use
the completed static package and need no Rust compiler or Studio process.

The renderer is single-threaded WASM and works on ordinary static hosting without
cross-origin isolation. Embed real CJK glyphs and include font/native licenses.
Preserve the native enabled state, image/vector/text readiness checks, same-origin
sender checks, render generation IDs, stale-click rejection and redraw input lock.
The browser checks its exact artwork origin; the native runtime has explicit
OctoSense deployment bases. A different HTTPS host/prefix needs a reviewed rebuild.
Cache-version the iframe, bridge and WASM together. Keep Retry state-preserving,
keyboard focus stable, and phone scaling based on actual native coordinates.

Integration validates package, bundle and artwork hashes before replacing the
website's static directory atomically. A malformed package leaves the prior
working package intact. Integration is a local source update; publishing is a
separate, already established website workflow. This runner does not push or deploy.

## 7. Browser and hosted verification

Browser checks must click real native widget bounds, not call reducer actions
directly or target raster hotspots. Cover the full flow in EN and CN, mobile
scaling, keyboard equivalents, Back/Restart, undo/restore and explicit payments.
Check failed asset loads, native readiness and `application/wasm` MIME on the
deployed origin. Run `--stages hosted-test --website "$FLOW_SITE"` after a website
deployment to execute the manifest's hosted checks and preserve their result.

The aircon prototype passed both full live language flows. Chromium 1243 also
showed intermittent cold-scene/reused-tab rendering stalls; those failures remain
recorded. Use independent browser contexts per locale and expose Retry. Do not
auto-retry tests into a pass or treat timeout as readiness. Production service
connectors, responsive reflow beyond the tested fixed artboard, arbitrary new
flows, and every browser/device require additional implementation and evidence.

## Pipeline maintenance tests

```sh
"$BEAUTY_PYTHON" -m unittest discover -s lab/image-to-appcard-flow -p 'test_*.py'
"$BEAUTY_PYTHON" -m unittest discover -s lab/image-to-appcard-flow/wasm -p 'test_*.py'
```

These verify atlas provenance, crop validation, native subtree extraction,
bundle boundaries and stage/error behavior. They are separate from Studio and
browser acceptance of a particular app.
