# Sketch kit ingest: Sketch → native widgets → inspection → repair

English | [简体中文](README.zh-CN.md)

This produces **theme kits** from licensed Sketch design kits. It is not an
app flow. For the step-by-step contract see `FLOW.md`.

Entry point: `tools/beauty-pipeline.sh` from the repository root. The recommended
first renderer for a purchased design kit is **splash-makepad through release
Makepad Studio**. The older theme/LLM L0 and desktop/device rails remain in
`run_kit.py` for existing kit configurations; they are not documented or
maintained here, and the desktop rail's client now lives in
[OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard).

For a new installation, use [the generic reproduction guide](../../core/REPRODUCE.md)
and [example kit configuration](../../core/examples/sketch-kit.json).
These replace personal archive paths and device settings with local inputs.
The default native loop records explicit external visual reviews; it does not
require a provider account or invoke a model CLI. See
[the reviewer contract](../../core/MODEL-REVIEW.md).

For an AI-generated UX image, use the [image-to-widget branch](../../image-lib/README.md):
`tools/beauty-pipeline.sh --ux-image --design weather-01`. It saves explicit font
and layout prompts, measures the actual generated image, mounts native L0 kits,
and joins Studio inspection and screenshot differences into each repair round.
The initial review collection has 10 Weather, 10 News and 10 Stocks layouts.
The image branch's [explicit mapping rules](../../image-lib/MAPPING-RULES.md) require
native data-bound charts and documented artwork assets before compilation.
Its semantic audit is separate from the legacy Sketch vector-geometry route.

## What gets composed

The `input_format: "design"` route imports source-measured `.splash` trees and
uses `octoscript_makepad::design` to generate native Makepad widgets. It preserves
Sketch group hierarchy and source IDs. It is a fixed-layout visual port;
it does not establish reusable L0–L3 composition,
responsive behavior, or a complete application.

| Sketch element | Native composition |
|---|---|
| Group | Nested `View` with explicit dimensions and absolute position |
| Text / rich text | `Label` / `DesignText` containing individually inspected labels |
| Editable field | `DesignInput`, derived from `TextInput` |
| Button | Native `Button` inside the source `View`, retaining inspectable labels and graphics |
| Selection pill | Native `CheckBox` with an independently inspected `Label` |
| Slider / range | Native `Slider`, including two independently draggable handles |
| Legacy Taskplan tab | `DesignButton`, a custom `View` retaining its source children |
| Toggle / checkbox | Native `Toggle` / `CheckBox`, styled for the kit |
| Radio | Native `RadioButton` for Camo; legacy Taskplan uses `DesignRadio` |
| Simple shape, background, border | Native `View` surface properties |
| Rounded glass | Native `GaussRoundedView` with source tint and blur |
| Glass tooltip silhouette | Native `Svg` with a Gauss backdrop texture; labels and icons stay widgets |
| Graphic-only Overlay blend | Native `Svg` sampling the backdrop, with source tint composition |
| Rotated text | Native `DrawRotatedText`; source labels remain inspectable |
| Icon, decorative path, supported effect | Native `Svg` tessellation with the original canvas |
| Quantitative chart, waveform, progress | Native numerical widget and reviewed data binding; never static SVG/Image paint |
| Photo or unsupported graphic feature | `Image`, with a per-element fallback reason |

**Use Makepad native widgets first unless the source feature cannot be represented.**
Set `native_widgets_first: true` for new kits (see `atro-native-all.json`).
Existing Taskplan templates predate this policy and contain many layer Images,
including button backgrounds. New composition uses native surfaces, text and
controls, then native SVG for supported vector geometry. A bitmap fallback must
identify the source photo or unsupported mask/filter feature; it cannot silently
replace text, controls, or a full screen. Control recognition depends on the
kit's source symbols; unknown variants need an explicit mapping and verification.
Full-screen reference screenshots and text must not become implementation assets.
Compound paths may remain a single graphic, retaining their source ancestry.
Quantitative regions are the exception: both intake branches now share
`flows/core/policy.py` and the same mapping rules. Sketch composition
acceptance requires `native/semantics/<screen>.json` for every artboard, with a
complete `source_review` bound to the source hierarchy and reference hash.
Nominated chart/progress regions require individual decisions. These retain source
IDs, exact paint owners, units, domains and data provenance. Named candidates
are a review aid; anonymous data regions must be annotated explicitly.
`semantic_lowering.py` lowers line, area, donut, bar, radar, scatter, waveform
and progress regions into native numerical adapters while retaining text and
controls as widgets. Source masks become native clipping containers around
the numerical paint. Gradients, bar widths, bubble radii, arc geometry and
radar axes have explicit source-derived styles and values.
Unsupported chart types fail pending an adapter. `curve.py` can measure a
single reviewed SVG curve into approximate normalized samples; those samples
are not recovered business values. Studio must report the actual arrays.
Unmigrated legacy kits need semantic migration before their earlier visual
acceptances can satisfy this stronger gate. Taskplan, Atro and Camo completed
that migration; see [old-kit migration](../../core/OLD-KIT-MIGRATION.md)
for the source-review, import, L0 promotion and fresh Studio validation steps.

For the persistent Studio bridge, tall-artboard allocation, declarative repairs
and restart protocol, see [the shared loop guide](../../core/README.md).
Glass overlays belong to the component that owns them; a tooltip must not move
the artboard background out of the scene capture. Covering glass materials retain
their source tint provenance when nested surfaces share Makepad's backdrop texture.
An artboard-sized glass background retains its preceding photo in the scene
capture; later content and overlapping controls draw above the glass. Source
button hit-area padding must not put its label behind its glass background.
Normal glass tints compose before an Overlay blend. Checkbox cutouts retain
transparency, so their marks reveal the actual backdrop instead of a fixed color.
Glass coverage is evaluated inside the artboard clip, including keyboards whose
source backgrounds extend beyond its edge. Blur radii remain logical points;
native sampling accounts for texture DPI and the Gauss reconstruction kernel.
SVG glass uses the same fractional mip reconstruction as rounded surfaces.
Coverage from the source alpha mask proves whether a compound glass shape
actually covers another material; a bounding box alone cannot prove this.
Any graphic deferred above glass also defers later overlapping paint, including
labels outside the original glass bounds but inside an exported shadow canvas.
Fixed-height text boxes keep the full native text and clip its drawing to the
source box. Rotated graphics use their transformed bounds for visibility checks.
Group rotations and reflections propagate to child geometry and mask chains.
Sketch reflections apply in the rotated parent's axes. An unpainted mask outline
retains its native layout container without inventing drawable SVG geometry.
An isolated mask's own paint still obeys its ancestor masks.
Alpha masks retain their fills and gradients for descendant coverage and do not
paint an independent black surface. Outline masks contribute only their shape.
Atro uses the exact Montserrat styles embedded in the Sketch document; their
versions and hashes are saved in `native-fonts.json`. Mixed emoji baselines do
not imply an extra text row. Trailing paragraph breaks that Sketch does not draw
remain in source provenance without creating empty native layout rows.
Explicit paragraph heights include Sketch's centered leading; vertically aligned
text also keeps its offset inside the source frame. The importer adds offsets
missing from SVG and detects baselines that already include line compression,
avoiding a second upward shift on short fixed line boxes.

Camo's `camo-native-all.json` covers 246 mobile screens, including both light
and dark pages with identical Sketch page names. Page IDs and explicit artboard
names prevent one theme from overwriting the other. Archive DM Sans fonts are
installed and bundled byte-for-byte; platform fonts use local file resources.
CoreText must resolve the exact font name and file before Sketch detaches symbols
or exports references. Font hashes and registration evidence invalidate the
source cache when they change. SVG text inherits `fill-opacity` once while group
opacity composes. Password circles map to editable masked TextInput glyphs with
measured ink and spacing. Outer button shadows can pass through transparent
full-size wrappers to their opaque background without flattening their labels.
Completed imports resume only when source, importer, kit and every generated
asset hash still match. Camo controls and screenshots require the same Studio
inspection, interaction and visual gates as other native templates.
Apple Color Emoji uses measured CoreText optical sizes and bitmap baseline
offsets in native Labels. Emoji shadows remain native: CachedView renders a
Label's alpha for a Gaussian shadow, with a separately inspected foreground.
SVG fill rules reach native tessellation, including nonzero overlap and
opposite-winding holes. Ancestor Multiply/Soft Light effects that require an
unsupported backdrop become individual graphic fallbacks with source context;
that path rejects text or controls inside the paint region.
Use repeated `sketch_native.py --screen <exact-name>` arguments for an exact
repair set; `--only` continues to select by substring. Zero-alpha source exports
retain their hash evidence and native layout bounds, including compound operand
Views. They do not create empty SVG paint nodes that can never return drawn bounds.
Opaque group foreground tints propagate to native text without rasterizing it.
Linear gradients are reconstructed from Sketch's original point-space values
when its exported SVG endpoints disagree with the raster reference. Coordinates
retain scientific notation, including near-zero gradient endpoints. Native SVG
renders dashed strokes with source caps, joins, offset and odd-length patterns.
Axis-aligned rectangle shadows use Makepad's rounded-rectangle blur renderer.
Unsupported backdrop blending uses only the affected graphic's coverage, with
its source backdrop needed to compute the blend. Holes and padding stay
transparent. The exporter rejects any such fallback that intersects source text.
The report records the limitation, contributing source IDs and coverage hash.
This includes individual effects over a foreground photo excluded from Window
Gauss's shared scene texture. The photo remains an Image widget and foreground
text and controls remain native; the fallback covers only the affected graphic.
Overlay shadows and unsupported SVG pattern paints retain that backdrop context
instead of silently turning an isolated layer export into ordinary alpha blending.

`composition.json` records the route, layout limits, per-screen generated node
counts and manifest hashes. Counts are widget instances, not unique assets or
screen coverage. Its presence alone is not an acceptance gate. The separate
`composition-gate.json` audits the generated paint widgets against source owners,
backend decisions and asset names. It rejects unowned Images/SVGs, missing bitmap
reasons, a claimed source photo without a bitmap reference, flattened artboards,
paint containing source text/controls, and text/controls replaced by containers.
An artboard-sized source photograph is allowed when its labels and controls
remain separate native widgets. Per-screen `.composition.json` reports list
the asset decisions and source/widget IDs for each failure. This policy audit
does not determine by itself whether an unsupported renderer feature could be
implemented; the fallback reason still needs a source-backed review.

## One cycle

The native designs can now be promoted to reusable L0 kits for **Taskplan,
Atro and Camo**. Run `python3 promote_l0.py --kit camo-native-all` (or
`atro-native-all` / `taskplan-native-all`) after native import. This writes the
theme's measured tokens, typed primitive and compound components under
`Octoscript-Makepad/components/l0/native/`, and `.card`, `.data.json`, and
`.l0map.json` screen instances under `work/<family>/native/l0/`.

Validate the resulting `camo-l0-all`, `atro-l0-all` or `taskplan-l0-all` kit with
the same Studio loop. `gate_kit.py` additionally checks the shared definitions,
cross-screen reuse, complete Sketch ownership, and native-tree equivalence.
`semantic_widgets.py` recognizes complete buttons, fields, navigation, project
cards and music rows. Shared definitions own their layers and take one instance
ID plus named content/state parameters; host part bindings retain Sketch IDs.
The runtime mounts `KitButton`, `KitFormField`, `KitTabBar`,
`KitBottomNavigation`, `TaskplanProjectCard` and `CamoTrackRow` from
`octoscript-widgets::kit`. Public defaults are in `roles.l0` / `semantic_roles`.
The gate requires these actual Studio widget types for every promoted boundary;
a generic View with the same name does not pass. Explicitly mapped transparent
native controls fill passive Atro tab and card/row action gaps while the offline
audit still requires every original source property and child to match.
`semantic_interactions.py` checks every component's initial enabled/selection
state against its native controls, then exercises all navigation items and representative
button/field/card/row actions and setters per screen, records the observations
in `.semantic-interactions.json`, and restores source state. These findings join
the repair handoff, and failed/missing semantic evidence fails the kit gate.
Navigation probes also sample selected/unselected backgrounds and underlines with a
3/255 per-channel tolerance; a changed state flag with stale paint fails. They
use the initial screenshot's source-state palette to account for composited
modal scrims. Inconsistent palette samples fail rather than hiding occlusion.
If another native control receives a click at the same measured position, the
probe records that occlusion and chooses an exposed button. Component probe
failures are collected across the remaining screens, then fail the run together.
Click points also exclude later native controls inside the measured clipped
rectangle, so a floating action button cannot intercept a radio probe. Fully
covered controls are recorded without claiming click coverage.
Missing/host-only inspection still fails the structural gate. Per-element kit
failures join structural and visual findings in the repair report.

The native widget implementations are reusable registrations in
`octoscript-widgets::design` and `octoscript-widgets::kit`, separate from the beauty host. Standard L0 text roles
also receive the imported source fonts and measured sizes. The source screen
templates retain fixed-artboard placement; responsive layout and complete app
workflows require their own evidence.

`inherit_visual.py --kit <family>-l0-all` can carry an existing visual verdict
forward only when the full target/capture/prompt hash is identical. It never
reuses structural inspection, assigns a new score, or accepts changed pixels.
Changed pairs require fresh screenshot review. See
[the native L0 kit contract](https://github.com/OctoSense-org/Octoscript-Makepad/blob/main/docs/native-l0-kits.md).

1. **Import the source.** Verify the archive and source document; resolve symbols
   and overrides in a copy. Export the original Sketch artboards as references.
   Preserve source IDs, hierarchy, frames, fonts, text, masks and control states.
2. **Compose widgets.** Generate checked Splash trees and map nodes to native
   widgets. Prefer built-in widgets and native properties; preserve text and editable controls.
   Use native SVG for remaining supported vectors. Export fallback graphics individually,
   accounting for painted bounds, masks and shadows. Unsupported mappings fail
   and require a source-backed implementation.
   Keep the semantic component boundary: a button owns its hit target, label,
   icon, background and state, even when those draw through separate widgets.
   Count its low-level paint nodes separately from its reusable component status.
3. **Render in Studio.** Launch the release RunItem, set the artboard viewport,
   mount the generated tree, and wait for fonts, layout and decoded image textures.
   Save a native screenshot and reject blank, incomplete or wrong-size captures.
   Confirm the embedded viewport after Studio's initial tab layout and repeat
   the resize if that layout replaced the requested artboard dimensions.
   Do not save a layout nonce while the root is still clipped to Studio's
   initial viewport; wait for the full artboard's drawn area.
   Consume only temporary screenshots returned to this bridge, after copying
   evidence successfully; failed copies retain their Studio source for recovery.
4. **Inspect structure and controls.** Use WidgetTreeDump, exact WidgetQuery for
   every generated ID, and WidgetSnapshot. Join back to Sketch IDs and compare
   hierarchy, bounds, visibility, text, clipping and control state. Exercise native
   input typing/restoration, password masking, focus, checkbox/toggle clicking
   and both slider handles with restoration where present.
   Run the native composition gate on the same source and generated manifests;
   declaring `native_widgets_first` without native widget mappings cannot pass.
5. **Review screenshots.** Compare original Sketch and native output for
   typography, colors, imagery and effects. Require a current `accept` verdict
   and score of at least 9/10 (unless the kit explicitly configures its threshold).
   Review copies use the native pixel dimensions and white window backdrop for
   transparent export pixels; original Sketch exports remain unchanged.
   Both review inputs are frozen under their content hash before the reviewer
   reads them. Partial reviews preserve verdicts for other screens.
   Independent frozen pairs are reviewed in bounded batches (`--workers`,
   default 3), with one verdict writer. A failed request preserves the other
   completed reviews in its batch. A file lock also serializes separate review
   invocations so a focused repair cannot overwrite a full run's newer rows.
   A disputed visual finding can receive an evidence-informed follow-up using
   `visual_evidence.py`. It saves measured regions and native bounds, preserves
   the original verdict, and asks for a fresh review of the complete pair.
   The gate verifies all evidence hashes and retains the same score threshold;
   neither measurements alone nor a follow-up can override structural failures.
6. **Repair and recapture.** Read `repair-feedback.json` and per-element reports,
   fix the responsible importer, widget, renderer or asset-export code, regenerate
   and repeat. The importer records prior findings in `.repair-input.json`; it
   does not automatically invent code fixes. The legacy L0 author can consume
   findings in an LLM repair round. Do not loosen tolerances to pass a defect.
   Composition failures join the per-screen repair queue even when structure
   and screenshot review pass. Keep the unfinished component, layout and workflow
   work in `acceptance.json` visible as the next composition round.

`beauty` runs one import/author + native capture/inspection/review cycle. Rerun it
after a repair. For shared widget or renderer fixes, revalidate the whole kit;
a small successful probe does not pass untested screens.

## From a visual template to reusable pages

The existing design importer completes the fixed-artboard reproduction cycle.
The next composition round has separate requirements:

1. Identify repeated source symbols and semantic groups, such as app bars,
   buttons, fields, cards and list rows. Map each instance to a named shared
   component with source IDs, properties, slots and control state. Repeated
   absolute-position `View` trees do not establish reuse.
2. Compose page sections with native flow containers, Fill/Fit sizing, padding,
   spacing and alignment. Use scrolling where content can exceed the viewport.
   Keep absolute positioning for intentional overlays and internal artwork.
3. Render the reference viewport and at least two additional configured widths.
   Inspect bounds, wrapping, clipping and missing content at each size; include
   long text and overflow cases. Compare screenshot styling at every size, using
   source references where available and explicit layout expectations elsewhere.
4. Exercise navigation, submission, selection and scrolling against expected
   state transitions. Include focus, disabled and error states. A native Button
   hit target does not establish that its application action is connected.
5. Repair the shared component and revalidate its consumers. Preserve each
   viewport's screenshots, Studio inspection, state transitions and source map.

`acceptance.json` explicitly reports `scope: "fixed_artboard_parity"`. Promoted
L0 kits establish shared component reuse through `gate_kit.py`, including native
semantic types and component behavior. Responsive layout and application
workflows remain `not_established`, with their required evidence and next repair
actions. Component events do not establish complete application workflows;
counts, a screenshot score or a configuration flag cannot promote them to passed.

## Set up and run

Use `../core/examples/sketch-kit.json` as the shareable configuration example. Set a separate
output directory for each kit, `source_archive`, `pages`, exact `screens`,
`input_format: "design"`, `native_widgets_first: true`, `reference_renderer: "Sketch"`,
`rails: ["splash-makepad"]`, `studio_embedded: true`, and the correct
`design_scale`. Keep archives and generated templates/assets under ignored
`work/`; do not publish purchased kit content.

Install the Python dependencies in `flows/kits/sketch/.venv` from `requirements.txt`.
Set `SKETCHTOOL` to Sketch.app's native CLI and `CARGO_MAKEPAD` to the patched
release Studio bridge. The bridge must forward WidgetSnapshot. Use the dev
Studio viewport-persistence and backing-allocation fixes recorded in the
[Taskplan report](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/docs/reviews/taskplan-native-parity-2026-09-05.md).

Prepare the shared runtime with `python3 tools/setup-native.py` (see
[NATIVE-WORKSPACE.md](../../../docs/NATIVE-WORKSPACE.md)). Start Studio with a
`splashref` mount pointing to the prepared `octoscript-makepad` checkout, which
sits beside this repository by default:

```sh
bash tools/beauty-studio.sh /path/to/makepad/target/release/makepad-studio --remote \
  --mounts="splashref:$(cd .. && pwd)/octoscript-makepad" \
  --bind=127.0.0.1:8001
export CARGO_MAKEPAD=/path/to/makepad/target/release/cargo-makepad
export SKETCHTOOL=/path/to/Sketch.app/Contents/MacOS/sketchtool
```

Then, from the repository root:

```sh
# One full cycle, including saved findings from a previous native round.
tools/beauty-pipeline.sh --kit atro-native-all --stages beauty

# Rerender existing templates after a native runtime change.
tools/beauty-pipeline.sh --kit atro-native-all --stages splash-makepad

# Rerun all acceptance gates against saved evidence; no Studio build or new judge call.
# Missing/stale evidence or any gate failure exits nonzero and saves repair findings.
tools/beauty-pipeline.sh --kit atro-native-all --stages audit

# Refresh the composition/feedback/gallery from saved evidence; no GPU or judge call.
tools/beauty-pipeline.sh --kit atro-native-all --stages report
```

`author` separately imports native designs, while `validate` runs checked
assembly without a UI. `doctor` checks configured dependencies and gate tests;
run it once the kit inputs have been imported. UI builds and runs happen only
through Studio RunItem; clear the previous build before validating a change.
`--rounds` controls the legacy author stage, not automatic native code repair.

## Acceptance and saved evidence

Structure, native composition policy and visual review must pass for every
configured source-mapped design screen. Legacy L0 cards have no source-mapped
composition audit and are explicitly marked `not_applicable` for that gate.
Design kits imported before the native-first policy must be migrated and
reimported before passing it; missing or disabled policy settings fail.
Host-only inspection, missing elements, missing query responses, wrong text or
state, unavailable textures, excess clipping, and stale evidence fail acceptance.
A screenshot score cannot override a structural failure. Fill analysis remains
an additional diagnostic, not a substitute for either gate.

| Structural measurement | Default tolerance (logical points) |
|---|---|
| Position, alignment, spacing | 4 |
| Width and height | 6 |
| Clipping / unexpected text overflow | 2 |
| Agreement among inspection APIs | 1 |

The effective `structure_tolerances` are saved in each structural report.
Reference/capture/review hashes bind evidence to the source, resources, binary,
inspection data and review prompt. Saved PNGs or old high scores alone do not pass.

Beside each capture are `.portable.json`, `.native.json`, `.widgets.json`,
`.queries.json`, `.snapshot.json`, `.layout.json`, `.structure.json`,
`.capture.json`, and interaction evidence where applicable. The directory also
contains `visual-gate.json`, `composition.json`, `composition-gate.json`,
`acceptance.json`, `pipeline-run.json`,
`repair-feedback.json` and `gallery.html`. The gallery shows Sketch and Makepad
side by side, with links to structural differences, native state and composition.
Renderer or judge failures still produce the repair/gallery handoff, and the
native stage exits nonzero. `report` refreshes artifacts; it does not repair a
failed pipeline run or manufacture a new screenshot verdict.
`audit` records `operation: "audit_saved_evidence"` in the latest run receipt;
it rechecks existing captures and reviews, and never claims a new rendering.

The importer, native renderer and screenshot reviewer accept repeated `--only`
screen-name substrings for a focused repair. Run the full native stage after
shared changes; focused evidence does not establish whole-kit acceptance.

## Results and limits

Camo's 246 mobile templates passed the native structure, composition and visual
gates on 2026-09-06. Studio build 63 inspected 29,929 nodes; all screenshot pairs
score 9–10/10. The [Camo report](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/docs/reviews/camo-native-parity-2026-09-05.md)
links the full comparison gallery, repair evidence and fixed-artboard scope.

Atro's 150-artboard native run passed its configured fixed-layout structural
and visual gates: 3,009 text nodes, 279 Buttons, 48 Inputs, 3,935 SVG widgets and
919 Image instances, alongside native surfaces and selection controls. Its
saved templates also pass the native composition audit. See the
[Atro report](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/docs/reviews/atro-native-parity-2026-09-05.md) and the current
generated `acceptance.json` for scope and freshness.

Taskplan's 79-artboard run passed its configured native structural and visual
gates: 1,952 text nodes, 97 inputs, seven toggles, 4,012 image nodes and 8,672
container nodes. Containers include composed controls. See the
[full report](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/docs/reviews/taskplan-native-parity-2026-09-05.md).
That historical result predates the enforced native-first composition gate and
subsequent shared runtime changes; it is not a current acceptance result.

Those historical results validate fixed artboard reproduction. The generated
L0 kits now add shared native components, component actions and selection state;
their current evidence is in the L0 comparison index (`work/l0-themes/index.html`)
and each `l0-captures/acceptance.json`. Responsive rearrangement and complete
application workflows require separate implementation and tests. The earlier
five-screen L0 Taskplan run remains a
failed baseline, documented in [TASKPLAN-VALIDATION.md](TASKPLAN-VALIDATION.md).

### Using kit components in existing Octos apps

Promotion now also exports `Octoscript-Makepad/components/l0/native/app-recipes.json`
through `export_app_recipes.py`. These compact recipes retain source component
IDs, source screen names, kit hashes and native part styles. Run the exporter
with `--check` to detect stale recipes. The first app adapters compose Weather
with Atro controls, Stocks with Camo rows/tabs, and News with Taskplan cards.
They share the native kit class implementation with the Sketch host and bind
existing L0 values/actions to real Button, Label and TextInput children.

App adaptation has its own gate: source-linked native components and child
bindings must be present in Studio, control state and interactions must work,
and the measured scroll canvas must contain the resulting composition. Flowing
app layouts are intentional adaptations and do not inherit an artboard parity
pass. Before/after captures, per-element differences, source mappings and the
validation script are in [`docs/reviews/theme-phone-evidence/components/`](https://github.com/OctoSense-org/OctoSense-App-Flow/tree/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/docs/reviews/theme-phone-evidence/components) (removed here; kept in history).

Page structure is a separate adaptation step. Six authored L0 recipes now live
in `Octoscript-Makepad/components/l0/pages/`: Weather dashboard/forecast, Stocks
tiles/chart, and News magazine/compact. They replace named views while keeping
the app's source/state/event declarations. The bundled selector can choose
`weather@atro_light/dashboard`, for example. Each adapted page must pass native
component inspection plus topology checks (section order, column bounds, item
counts, scrolling, and actions); a color-only change cannot satisfy this gate.
The phone comparison and per-element repair evidence are in
[`docs/reviews/theme-phone-evidence/structures/`](https://github.com/OctoSense-org/OctoSense-App-Flow/tree/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/docs/reviews/theme-phone-evidence/structures) (removed here; kept in history). This is an explicit authored
recipe layer, not automatic page generation for every ported theme.
