# UX image → native Makepad beauty loop

For **8–12 related screens in one agentic application flow**, use
[image-to-appcard-flow](../image-to-appcard-flow/README.md). It generates no
independent per-state images: preserve one complete atlas, measure/crop its
screens, reuse this native mapping loop, then bind service state and package
interactive Makepad WASM. This page remains the individual-design adapter guide.

**Current native testing:** use [Makepad's built-in HTTP instrument](../core/NATIVE-INSTRUMENT.md)
with a standalone release binary and `MAKEPAD_HIDE_WINDOWS=1` for hidden-window
automation. Studio is not needed for that path. The `capture`/`--launch` CLI and
saved-round gate described below remain legacy Studio adapters; they have not
been migrated to consume direct HTTP evidence.

This branch starts with an externally generated UX image and an explicit design brief.
Use [the generic reproduction guide](../core/REPRODUCE.md) for a clean
installation, a new input and the complete command sequence. No Astra-specific
image reader or API is called: see [the reviewer contract](../core/MODEL-REVIEW.md).
Semantic interpretation and final screenshot QA still need a human or capable
vision reviewer. The validation corpus contains 11 Weather, 10 News and 10 Stocks layouts. Every page
has its own prompt, reference, native L0 card and kit pack. Open the comparisons
at `http://127.0.0.1:8170/ux-images/` when the existing review server is running.

Start with the [explicit mapping rules](MAPPING-RULES.md). `semantic-map.json`
declares each region's function, allowed native widgets, data/behavior binding
and artwork strategy. Compilation now fails on SVG charts, static range controls,
unknown roles and missing asset provenance. Existing captures are historical
prototypes; a fresh semantic audit can block them even when geometry passed.

## What the loop does

1. Author a layout contract with semantic element IDs, hierarchy, exact fixture
   text, bundled font family/weights, font sizes, line boxes, colors, dimensions,
   spacing and native control intent. `catalogue.py` contains the 30 briefs.
2. For an independent design, generate one image with your chosen external image
   generation tool. For a complete service journey, generate **one atlas containing
   all 8–12 states** and use the flow adapter's hash-bound crop intake.
   Save the exact submitted prompt in `image-prompt.md`. `generation.json`
   records the original filename, declared provider/model, prompt/image hashes
   and actual dimensions. `save_reference.py --provider` records the actual
   generator; omit `--model` when it was not exposed. These are provenance
   fields, not an API integration. Preserve the same intake for any generator.
3. Measure the **actual image**, separately from the requested contract.
   Apple Vision supplies text observations. Reference edge contours and OCR
   descendants propose card bounds. Inspect `annotations.json`: unresolved
   surfaces and projected graphic extents are explicitly marked. Human source
   annotations must include the reference SHA; stale annotations are rejected.
4. Map text ink bounds through the real bundled font's glyph metrics. Preserve
   native Labels and native Button controls, semantic kit wrappers and hierarchy.
   `mapped.json` is the repairable page model. `page.card`, `page.data.json`,
   `kit/native/light/kit.json` and `components.l0` are the runtime outputs. Colors,
   typography and shapes are kit tokens. Geometry is JSON placement data.
   Run semantic preflight: charts must use native data-bound plot widgets;
   illustrations require a reference-derived SVG or a documented image asset.
   `classify` seeds a conversion brief and decisions; ambiguous roles need review.
5. Build the host in release mode and launch the executable with `--remote`.
   Hide the native window for automated checks, discover the owned endpoint from
   its startup log, and fetch `/` for its protocol. The beauty host mounts L0
   cards/packs through request data; a nonce identifies every replacement.
   Rebuild/relaunch after changing native/runtime code. See the direct instrument guide.
6. Capture **native `/d` and `/snap` inspection, measured layout/clipping,
   app-owned `/g` frames, native input and resulting service actions**.
   The gate joins source IDs to mounted native IDs. Only the host appearing in
   inspection is a failure. Native geometry must agree within 1 logical pixel;
   reference text/annotated geometry has 3-pixel tolerances. Text, visibility,
   hierarchy, enabled state, clipping and control activation are checked.
7. Keep direct-instrument results and provenance alongside each screenshot.
   Legacy captures additionally save `gate.json` and per-element `repair.json`;
   do not report those gates as passed from direct evidence without an adapter.
   Semantic role, binding and asset findings join the repair report. For saved
   captures, `semantic` writes a separate audit without modifying prior rounds.
   Repair the mapped model/assets, capture again, and retain prior rounds.
   Native SVG URLs include content hashes so repaired artwork cannot silently
   reuse a cached old texture. Text/graphics never become a full-screen image.
8. Review typography, colors, illustrations and effects side by side. The RGB
   error is diagnostic, not an automatic visual approval. Unmeasured graphics,
   missing/extra source text and unresolved OCR remain open findings. A native
   structure pass alone never marks image parity or visual acceptance.

## Commands

The `capture`/`--launch` examples in this section reproduce the historical Studio
loop. For current standalone/headless inspection, compile the card first and use
[the direct instrument commands](../core/NATIVE-INSTRUMENT.md).

Use a dedicated Python 3.11/3.12 environment at `lab/image-to-appcard/.venv`, installed
from `requirements.txt`. Keep it separate from Sketch's NumPy 2.x environment;
no private `.deps` setup is needed. The OCR stage requires macOS Vision and Swift.
Set `BEAUTY_PYTHON` when using the shared shell entry point:

```sh
export BEAUTY_PYTHON="$PWD/lab/image-to-appcard/.venv/bin/python"
# Preserve a generated image, without overwriting another reference.
lab/image-to-appcard/.venv/bin/python lab/image-to-appcard/save_reference.py example-01 /path/to/generated.png --provider actual-generator

# Review/re-run one design after its reference is present.
tools/beauty-pipeline.sh --ux-image --design weather-01 --launch

# Audit mappings of existing designs before attempting another native capture.
tools/beauty-pipeline.sh --ux-image --all --stages classify,semantic,gallery

# Run designs through the current Studio host after resolving preflight failures.
tools/beauty-pipeline.sh --ux-image --all

# Compile runtime cards without opening or building a UI.
tools/beauty-pipeline.sh --ux-image --all --stages compile

# Publish review artifacts from existing captures.
tools/beauty-pipeline.sh --ux-image --all --stages gallery

# Explicit gate failure exits nonzero; the gallery is still produced.
lab/image-to-appcard/.venv/bin/python lab/image-to-appcard/gate.py weather-01
lab/image-to-appcard/.venv/bin/python -m unittest discover -s lab/image-to-appcard -p 'test_*.py'
```

Stages: `classify,semantic,observe,measure,map,repair,font,compile,capture,gate,gallery`. A repair round
can use `--stages repair,compile,capture,gate,gallery` to apply bounded text
spacing corrections from Studio residuals before recapturing. An explicitly requested map stage derives
the initial mapping again. The default run preserves an existing mapped model. To retain manual repairs to `mapped.json`, resume
with `--stages compile,capture,gate,gallery`. Do not re-run `catalogue.py` over
a reviewed design: it authors fresh contracts/prompts and does not generate
images. Add a new ID/version when changing a generation brief.

Register a new authored design with `register.py <id>` after saving its
reference, contract, prompt and generation receipt. This preserves existing
catalogue entries. `weather-11` is a fresh generated validation example.
For broader repairs, pass `--repair-plan path/to/plan.json` with
`--stages repair,font,compile,capture,gate,gallery`. The shared plan engine
handles reviewed layout, font, color, asset, hierarchy, semantic and data
changes with exact source/evidence hashes and a restartable write journal.
See [the shared loop guide](../core/README.md). `measure_chart.py`
supports a reviewed single-series image region and explicit numerical domains.
It rejects ambiguous or discontinuous extraction instead of inventing data.

The gate command and pipeline gate stage exit nonzero until visual review
**and** native, image and semantic gates accept the current inputs. An audit
also checks compiled inputs and runtime source hashes. `pipeline-run.json`
records running, failed and interrupted work; the gallery cannot present a
failed current run as accepted. A capture publishes `latest.json` only after
interaction probes and immutable evidence receipts are complete. Startup
outputs use a disposable folder, never the previously accepted round.

## Artifact and acceptance boundaries

Each `weather-01` … `weather-10`, `news-01` … `news-10`, `stock-01` … `stock-10`
folder owns its files. `weather-v1` retains the original Weather pilot. The
failed transparent News attempt remains under `news-02/failed-reference-001`.
`rounds/NNN` retains the exact card, pack, assets, reference measurements, source
hashes, Studio build ID, request nonce and captured evidence for that round.
`latest.json` selects the current comparison. Gallery copies are review outputs;
the files under `lab/image-to-appcard` are the authoring source.

These are **native design prototypes at 406 × 776**. They load through the same
L0/kit runtime without an app-specific Rust layout branch. They are not new
deployments of the existing Octos apps: live feeds, actual page navigation,
responsive reflow and Mate 70 captures are outside this study's validation.
Buttons emit native kit actions; activation does not establish a working
production navigation flow. The repaired host includes numeric `LinePlot`/`DonutChart` adapters and a reusable
value-driven `DesignProgressBar`. Range buttons change the actual plot viewport
and move its native selection indicator. Waveforms consume measured amplitude
samples. Reference-derived series are explicitly approximate design data.
Complex banners use verified artwork-only crops; simple icons use native SVG.
Historical chart SVGs and incomplete artwork still fail semantic mapping.
Keep the reference on the left and the actual native capture on the right.

The gallery can shortlist designs, save notes locally and export review JSON.
That review is a design preference, not an automatic structural pass.

After actual screenshot review, a design may carry `visual-review.json` with
`reference_sha256`, `native_sha256`, `reviewer`, `verdict` (`pass` or `repair`),
`criteria` containing boolean `typography`, `colors`, `imagery`, `effects`, and
written `findings`. The gate accepts a design only when that receipt matches
the exact screenshots, all criteria pass, and both structure gates pass.
`../core/review.py prepare` produces a frozen comparison packet;
`submit` records the reviewer's explicit decision and preserves previous image
reviews. Neither command calls a model or creates an automatic judgment.

The repair/QA outcome and current gallery are recorded in [VISUAL-QA.md](VISUAL-QA.md).
An agent visual QA pass is separate from the user's design preference. It covers
the captured prototype size and allows recorded font-face and subtle texture
approximations; it does not assert pixel identity or complete app behavior.

## Repair evidence

`authoring-contract.json` preserves the submitted design contract. The current
contract records the composition observed in the original reference, including
previously missing chart labels and artwork. `text-annotations.json` records
independently sized number/degree and legend groups; each group retains matching
source OCR. Reviewed OCR false positives live in `ocr-classifications.json`.

`fit_reference_fonts.py` fits bundled font faces to source glyphs without raster
text in the output; `font-decisions.json` records reviewed weight choices.
Targeted fits use `fit(directory, only_ids=...)` to preserve unrelated completed
repairs. `repair_visual_details.py` records this study's reviewed font, mixed-size
text, divider and card-border decisions. It is a repair recipe, not a classifier.
`repair_text.py` consumes actual Studio residuals for bounded spacing and ink-color
corrections. `surface-fit.json` records corner measurements. The study-specific
`repair_reference.py` and `repair_measured_charts.py` preserve region decisions
and approximate numeric measurements; they do not claim general image recognition.

Each capture includes `semantic-baseline.json`, `semantic-state.json`, binding
probes, changed-state screenshots, source hashes and per-element differences.
The gate compares actual exported series with the numeric asset, and checks
progress fill widths in both baseline and changed Studio screenshots. It rejects
a state update that does not repaint the component. The source image and submitted
image-generation prompt stay unchanged throughout repair.

Roboto Condensed is bundled from [Google Fonts](https://github.com/google/fonts/tree/main/ofl/robotocondensed)
with its OFL license; static weights are instanced from the supplied variable font.
The selected face is a visual approximation, not proof of the AI image's font identity.
