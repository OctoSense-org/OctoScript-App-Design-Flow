# Reproduce the Sketch and generated-image beauty-card pipelines

For **new native UI testing**, follow [the built-in Makepad instrument guide](NATIVE-INSTRUMENT.md):
build a standalone release executable, launch with `--remote`, and use hidden
native windows for automated checks. It requires no Studio process or bridge.
This page retains the older Studio capture/gate setup for explicit historical
reproduction. Its `RunItem` instructions are not the default for direct native tests.

For the full image → service state → interactive native App Cards → WASM website
workflow, see [image-to-appcard-flow](../image-to-appcard-flow/README.md). It reuses
the native setup and visual gates below, adding one-atlas 8–12-screen intake,
service card extraction, portable WASM packaging and browser checks.

This guide uses local tools, relative project paths and example inputs. It
contains no service credentials and requires no particular model provider.
The normal native loop does not call an LLM API or provider CLI. Image
generation and semantic/visual review are explicit external steps.
See [the reviewer contract](MODEL-REVIEW.md) for the division of work.

## Prerequisites

- macOS with Swift/Xcode command-line tools. The current OCR implementation
  uses Apple Vision; the current Sketch exporter uses Sketch's macOS CLI.
- Python 3.11 or 3.12. Use separate environments: the image measurement
  requirements currently use NumPy 1.x, while Sketch uses NumPy 2.x.
- The complete compatible workspace: `lab/`, `tools/`, `makepad/`, `splash/`
  and `Octoscript-Makepad/`. Include this workspace's native widget, chart and
  Studio inspection changes. A bare upstream Makepad checkout is insufficient.
  Record repository/submodule revisions and any local patch with a reproduction.
- For legacy Studio capture only: release Makepad Studio and `cargo-makepad` built from the same compatible
  Makepad source revision. The client/server inspection protocol must match.
- For Sketch input: your source archive, Sketch installation and the exact
  fonts used by the design. The native importer accepts a ZIP containing a
  `.sketch` document; set `sketch_member` if the ZIP contains more than one.
- For generated-image input: an original PNG, its exact submitted prompt,
  an authored contract and fonts/assets you can use. Keep the actual provider
  and model identity when known; never infer them from the output's appearance.

Run commands from the workspace root. Paths with spaces must remain quoted.

```sh
python3.12 -m venv lab/sketch-to-appcard/.venv
lab/sketch-to-appcard/.venv/bin/python -m pip install -r lab/sketch-to-appcard/requirements.txt
python3.12 -m venv lab/image-to-appcard/.venv
lab/image-to-appcard/.venv/bin/python -m pip install -r lab/image-to-appcard/requirements.txt

export BEAUTY_STUDIO_BIN="/path/to/matching/release/makepad-studio"
export CARGO_MAKEPAD="/path/to/matching/release/cargo-makepad"
export SKETCHTOOL="/path/to/Sketch.app/Contents/MacOS/sketchtool"
export BEAUTY_STUDIO="127.0.0.1:8002"
export BEAUTY_BRIDGE="http://127.0.0.1:8169"
```

Start the following long-running commands in separate terminals with the same
environment. `splashref` is the configured mount alias, not a user identity.
UI builds and launches go through Studio's release RunItems in
`Octoscript-Makepad/makepad.splash`.

```sh
bash tools/beauty-studio.sh "$BEAUTY_STUDIO_BIN" --remote \
  --mounts="splashref:$PWD/splash-makepad" --bind="$BEAUTY_STUDIO"

lab/sketch-to-appcard/.venv/bin/python lab/core/studio_bridge.py \
  --binary "$CARGO_MAKEPAD" --studio "$BEAUTY_STUDIO" \
  --port 8169 --log /tmp/beauty-studio.jsonl

# Required for the image branch's local artwork URLs and comparison gallery.
python3.12 -m http.server 8170 --bind 127.0.0.1 \
  --directory docs/reviews/theme-phone-evidence
```

Use available ports. Set `BEAUTY_BRIDGE` in both pipeline terminals if changing
the bridge port. The current image artwork URLs use gallery port 8170; changing
that port also requires updating/recompiling those URLs. The launcher reserves
2048 × 4096 backing pixels; override `BEAUTY_CAPTURE_WIDTH_PX` and
`BEAUTY_CAPTURE_HEIGHT_PX` for larger screenshots. Serialize capture jobs:
each branch uses one request file, and a new RunItem replaces that host.
Keep only one active capture host per branch across Studio instances. A first
capture can fail while Studio is still starting the app (`no app socket`).
After the host is ready, rerun that design's capture/gate stages without
`--launch`; the failed round stays recorded and cannot grant acceptance.

## Sketch input

Copy [the generic kit configuration](examples/sketch-kit.json) to
`lab/core/kits/example-native-all.json`. Edit the archive member, page,
artboard names, scale and fonts for your input. Paths are relative to
`lab/core`; keep each kit's outputs in its own `work/` directory.
`font_files`, when needed, must point to your exact local font files; those
local settings are not part of the shareable example.

```sh
cp lab/core/examples/sketch-kit.json lab/core/kits/example-native-all.json
# Place your archive at lab/core/work/example/source.zip and edit the config.
lab/sketch-to-appcard/.venv/bin/python lab/sketch-to-appcard/sketch_native.py --kit example-native-all

# Repeat for each configured screen. This creates an UNREVIEWED template.
lab/sketch-to-appcard/.venv/bin/python lab/core/review.py prepare-source \
  --kit example-native-all --screen Home --out lab/core/work/example/source-review/Home
```

Inspect the complete source image and tree, including anonymous numerical
regions. Complete the semantic manifest with reviewed roles, source IDs and
paint owners. Charts require native numerical data, units, domains and a
supported adapter. Artwork requires an explicit asset strategy. A screen
without charts still needs a complete whole-source review. Install the
reviewed manifest as `work/example/native/semantics/Home.json`; preserve the
original source tree. Repeat for all screens. The supplied candidate list is
a review aid and does not classify the image for you.

```sh
# Lower the reviewed semantic mappings, then create reusable L0 cards.
lab/sketch-to-appcard/.venv/bin/python lab/sketch-to-appcard/sketch_native.py --kit example-native-all
lab/sketch-to-appcard/.venv/bin/python lab/core/promote_l0.py --kit example-native-all
lab/sketch-to-appcard/.venv/bin/python lab/core/render_splash_makepad.py \
  --kit example-l0-all --studio "$BEAUTY_STUDIO"

# Prepare a fixed source/native pair; inspect its index.html before deciding.
lab/sketch-to-appcard/.venv/bin/python lab/core/review.py prepare \
  --kit example-l0-all --screen Home --out lab/core/work/example/visual-review/Home
```

Copy `decision.template.json` to `decision.json` in that packet. A reviewer
fills the verdict, name, written basis, four visual criteria, remaining
differences and a Sketch `design_match` score from 1 to 10. An unchanged
template cannot be submitted. Then repeat submission for every reviewed screen:

```sh
lab/sketch-to-appcard/.venv/bin/python lab/core/review.py submit \
  --packet lab/core/work/example/visual-review/Home \
  --decision lab/core/work/example/visual-review/Home/decision.json
bash tools/beauty-pipeline.sh --kit example-l0-all --stages audit
```

The audit fails until current structural, semantic, L0 and visual gates pass.
Read per-element `.structure.json`, `.composition.json`, `.kit.json` and
`repair-feedback.json` beside the captures. Repair the importer, mappings,
components or assets; re-import, promote, capture and review changed pixels.
Kit-specific adapters in `migrate_legacy.py` cover the historical Taskplan,
Atro and Camo migrations; they are not a classifier for arbitrary new kits.
The optional `visual_review: "claude_cli"` setting selects the legacy CLI
reviewer. The default `external` path used here has no provider dependency.

## Generated-image input

Create `lab/image-to-appcard/example-01/`. Author `contract.json` with the structure
illustrated in [the contract example](examples/image-contract.json), replacing
its font resource with a real bundled font. Use
[the generation-prompt template](examples/image-prompt.md) to state exact
fonts, text, layout, artwork bounds and numerical intent. The current image
branch validates 406 × 776 logical artboards. Generate the image with your
chosen external tool and save the **exact submitted prompt** as
`image-prompt.md` in the design folder.

```sh
lab/image-to-appcard/.venv/bin/python lab/image-to-appcard/save_reference.py example-01 \
  /path/to/original-generated.png --provider "actual-generator-name" \
  --model "actual-model-identifier"
# Omit --model when it was not exposed. Provider/model are metadata, not auth.
lab/image-to-appcard/.venv/bin/python lab/image-to-appcard/register.py example-01

BEAUTY_PYTHON="$PWD/lab/image-to-appcard/.venv/bin/python" bash tools/beauty-pipeline.sh \
  --ux-image --design example-01 --stages classify,observe,measure,map
```

Review `observations.json`, `annotations.json`, `mapped.json`,
`semantic-map.json` and `conversion-brief.md` against the actual PNG. OCR and
edge measurements do not establish semantic intent or the true font identity.
Resolve missing/extra text, ambiguous bounds, artwork and data regions using
[MAPPING-RULES.md](../image-to-appcard/MAPPING-RULES.md). Keep original intent separate
from observed geometry. The `classify` stage only seeds candidates; existing
study-specific repair scripts are not a general image recognizer.

```sh
BEAUTY_PYTHON="$PWD/lab/image-to-appcard/.venv/bin/python" bash tools/beauty-pipeline.sh \
  --ux-image --design example-01 --stages compile,capture,gate,gallery --launch
# A missing visual review correctly makes this first gate exit nonzero.
lab/image-to-appcard/.venv/bin/python lab/core/review.py prepare \
  --design example-01 --out lab/image-to-appcard/example-01/review-packets/001
# Inspect the pair; complete decision.json explicitly as described above.
lab/image-to-appcard/.venv/bin/python lab/core/review.py submit \
  --packet lab/image-to-appcard/example-01/review-packets/001 \
  --decision lab/image-to-appcard/example-01/review-packets/001/decision.json
BEAUTY_PYTHON="$PWD/lab/image-to-appcard/.venv/bin/python" bash tools/beauty-pipeline.sh \
  --ux-image --design example-01 --stages gate,gallery
```

Repairs change `mapped.json`, reviewed assets/data or a hash-bound repair plan,
then repeat compilation/capture/gates. Do not rerun `map` over manual repairs
unless intentionally deriving a new mapping. Preserve prior `rounds/NNN`
and original source images. Rebuild through `--launch` after native code
changes. A changed capture tool or input can make old proof stale; recapture
instead of changing the recorded hashes. Progress probes wait for both the
requested value and its paint before saving/restoring state.

## Verify and share

```sh
lab/sketch-to-appcard/.venv/bin/python -m unittest discover -s lab/sketch-to-appcard -p 'test_*.py'
lab/image-to-appcard/.venv/bin/python -m unittest discover -s lab/image-to-appcard -p 'test_*.py'
lab/sketch-to-appcard/.venv/bin/python -m unittest discover -s lab/core -p 'test_*.py'
```

Share this guide, code, generic examples and the compatible native source
changes. Supply only assets/fonts you may redistribute. Keep service
authentication outside prompts, configs, receipts and logs. No credentials,
account IDs, signed URLs or personal device serials belong in a reproduction.
Historical `work/`, `rounds/`, `qa-work/`, galleries and local logs contain
machine-specific paths and source material: they are evidence, not a generic
distribution. Do not rewrite hash-bound historical evidence to sanitize it;
create a clean reproduction with permitted inputs instead.

Close only Studio/bridge processes started for the reproduction. Use the
temporary Studio's own remote `/quit` endpoint. Acceptance covers tested
artboards; additional viewport sizes, phone rendering, live data and complete
application workflows require their own evidence.
