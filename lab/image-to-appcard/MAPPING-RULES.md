# Image → Makepad mapping rules

The converter must identify each region's **function before choosing its renderer**.
Use the matching reusable kit component first, a built-in native widget next,
and a reusable custom native widget when behavior is missing. Artwork has its own
SVG/image path. Native inspection of a generic SVG does not establish a chart.

The executable policy is [mapping-rules.json](mapping-rules.json). Every design
has a `semantic-map.json`, an implementation `conversion-brief.md`, and a
`semantic-audit.json` with per-element failures and repair instructions.

## Mapping table

| Region / recognition evidence | Mapping | Required evidence / prohibited shortcuts |
|---|---|---|
| Heading, caption, price, body copy | `Label` / native rich text | Exact text, bundled font family and weight, size, baseline, wrapping, overflow. Never text baked into artwork. |
| Button, input, toggle, tabs | Matching kit control or native `Button`, `TextInput`, `CheckBox`, `RadioButton` | Enabled/selected/value state and declared action. A drawn background plus text alone is insufficient. |
| Time ranges such as 1D / 1W / 1M | Native selection controls bound to a chart | Record initial selection, event, target property and observed before/after data change. Static labels fail. |
| Rows, cards, navigation and repeated content | Existing kit component; otherwise named reusable native composition | Preserve text/control children; declare item data, scrolling and responsive constraints. Avoid screen-specific Rust branches. |
| Trend line / sparkline / filled time series | `LineChart`, `AreaChart` or `makepad-plot::LinePlot` | Explicit samples, units, domains, series colors and interpolation. No hand-authored SVG trend or cropped chart. |
| Candles, allocation donut, other quantitative plots | Matching native chart | OHLC or category values, legend and scale; retain numerical meaning. Resolve unsupported adapters before compiling. |
| Radar-like image | Determine whether it is a weather map, radial chart or decoration | Ambiguous intent blocks automatic mapping. Do not pick a radial plot merely because circles are present. |
| Audio waveform / progress | Reusable native component bound to samples/value | Inspect current data/value and relevant interaction. A static vector does not prove functional behavior. |
| Simple icon / geometric illustration | Existing kit icon or reference-derived SVG | Record exact asset, provenance, shapes/layers/colors, fit and clipping; compare the rendered result. Generic artwork is not a match. |
| Complex illustration / photo / textured banner | Original asset, exact source crop or separately generated asset in `Image` | Record source, crop, hash, fit and clipping. Keep surrounding UI text and controls native. |
| Unknown or low-confidence region | Explicit review and supported decision | Never silently fall back to `View`, `Svg` or a screenshot. The converter can resolve routine ambiguity from evidence; user approval is not required for each element. |

## Guided conversion sequence

1. **Specify intent before image generation.** Keep a machine-readable manifest
   alongside the prompt: hierarchy, roles, exact text, local font files/family/
   weights, dimensions, spacing, colors, control states and bindings. For charts,
   include the same explicit samples, units and domains that the native widget
   will consume. Request complex artwork separately or inside an artwork-only
   rectangle with no text or controls overlaid.
2. **Measure the generated image.** OCR and image inspection determine actual
   text, bounds, geometry and artwork. Requested coordinates are not ground truth.
   Preserve the submitted prompt and original image unchanged.
3. **Classify and decide.** `classify` seeds `semantic-map.json` from authored
   intent; name-based candidates remain `needs_review`. It is not an automatic
   vision classifier. Resolve unknown roles, record evidence, and select the
   native component/data or asset strategy. Do not downgrade a declared chart to
   an icon to satisfy the gate. A genuine scope change needs a new contract.
4. **Preflight before compilation.** The semantic manifest must cover every
   source node, match the contract/reference hashes and satisfy role constraints.
   Missing adapters, missing data, unrecorded artwork and inappropriate renderer
   types block compilation. No native build begins while preflight is blocked.
5. **Compose and inspect.** Compile L0 + kit + data; use a standalone release
   executable with [Makepad's built-in instrument](../core/NATIVE-INSTRUMENT.md).
   Hidden windows support automated tests. Capture `/d`, `/snap`, measured layout,
   app-owned `/g` frames and real input/result evidence. Map source IDs to native
   widget IDs. Existing Studio capture/gate adapters remain a separate legacy path.
6. **Gate and repair.** Check semantic mapping, native geometry and image geometry
   separately. Feed role-specific findings into repair, then recapture. Typography,
   colors, imagery and effects still need screenshot review. Acceptance requires
   all gates; geometry alone is never a visual or functional pass.

For typography, compare the glyphs and word spaces, not only the bounding box.
Choose a closer bundled face before adding large positive or negative tracking.
Mixed-size values (number + degree, number + unit) use separate native Labels
inside a measured text group, retaining the original OCR string. A local font
repair must preserve unrelated nodes and earlier Studio feedback. Inspect the
fresh screenshot after every font change. Current screenshot review findings
are copied into `repair.json` alongside structural and semantic differences.

## Semantic manifest

Each entry records `id`, `role`, `basis`, `confidence` (0–1), and `decision`
(`declared`, `reviewed` or `needs_review`). Confidence below 0.9 and unresolved
decisions block preflight. Confidence describes classification, not visual parity.
Known intent comes from the authored brief; a screenshot alone does not reveal
the original implementation technology.

Additional fields are conditional on the role:

- **Data graphic:** `data.path`, `sha256`, `origin` (`fixture`, `measured_image`,
  `live_snapshot`), `x_key`, `y_keys`, `units: {x,y}` and increasing `domain: {x,y}`.
  The data file contains finite numeric samples, e.g. an array of `{time,price}`.
  Image-derived values must declare `approximate: true`; never present them as
  recovered market truth. Use numeric timestamps or declared category indices.
- **Stateful control:** `behavior: {event,target,property}` identifies the event
  and target source ID/property. Runtime evidence must show the before/after
  state change. Button activation alone does not establish navigation or a feed.
- **Artwork:** `asset: {method,path,sha256,fit,clip,...}`. Methods are
  `reference_svg`, `source_crop`, `original_asset`, `kit_asset`, `generated_asset`.
  File paths are local to the design. `fit` is `contain`, `cover` or `stretch`;
  `clip` is a boolean. Original/kit/generated assets require a source reference.
  Reference-derived SVGs require the reference hash. Review their geometry and
  effects; a valid SVG does not prove fidelity. UI text and embedded raster UI
  are disallowed inside SVG artwork.

A cropped illustration additionally records:

```json
{
  "method": "source_crop",
  "path": "assets/banner.png",
  "sha256": "<asset SHA-256>",
  "reference_sha256": "<original reference SHA-256>",
  "crop_pixels": [98, 316, 710, 295],
  "contains_ui": false,
  "fit": "contain",
  "clip": true
}
```

Coordinates are `[x,y,width,height]` in original image pixels, not logical layout
pixels. Keep the crop lossless and at original resolution. The gate compares its
decoded pixels to the source rectangle and rejects full-screen crops. Confirm
that the rectangle contains only artwork; `contains_ui: false` is a recorded
review decision, not an automated text/interaction detector. If UI overlays the
artwork, obtain a separate artwork asset and retain that UI as native children.

## Inspection and tolerances

- Native bounds and clipping: **1 logical pixel**.
- Reference position/dimensions and text ink: **3 logical pixels**.
- Text color: **16 per RGB channel**; detailed visual review remains required.
- Widget role/type, text/state, reference/data/asset hashes: **exact match**.
- Source crop: **exact decoded pixels**, with no tolerance or resampling.
- Data graphics: current widget ID, bound data hash and expected series; do not
  require each plotted point to be a separate widget. Native plot internals can
  render their own geometry while remaining a real data-driven component.

`WidgetSnapshot` does not automatically expose arbitrary chart series or data
bindings. A chart adapter must export `semantic-state.json` into the capture:
`build_id`, `nonce`, and `elements` keyed by source ID, each containing
`native_id`, `data_sha256` and, for behavior, `event`, `target`, `property`,
`before`, `after`. Include the file in the capture's provenance hashes. Missing or
stale state evidence fails; no synthetic receipt may be used to manufacture a pass.

The compiler implements stack/text/button/SVG/image, numeric `LinePlot` and
`DonutChart`, amplitude waveforms, and `DesignProgressBar`. `$kit.bindings` is the
runtime data/event input. The host exports the actual plot series, slice values,
progress values, selected range and before/after changes. SHA checks alone are
insufficient: the gate also compares exported numeric values, and measures
progress fill widths in baseline and changed screenshots. Other chart/control
families listed by the policy still require their own adapters.
The current image emitter stretches to its rectangle. `contain`/`cover` therefore
require matching asset/rectangle aspect ratios, an explicitly fitted child inside
a clipping container, or a native fitting adapter. Preflight rejects an unsupported
fit instead of silently stretching the artwork.

## Commands and existing evidence

```sh
# Classify and audit all existing screenshots; preserve saved rendering rounds.
tools/beauty-pipeline.sh --ux-image --all --stages classify,semantic,gallery

# After resolving the mapping, compile and capture a new round through Studio.
tools/beauty-pipeline.sh --ux-image --design stock-04 --stages compile,capture,gate,gallery
```

An audit writes `semantic-audit.json` and `semantic-repair.json` beside the old
rounds. It does not rewrite old prompts, widget trees or native screenshots.
The gallery displays both the original geometry results and current semantic
results. A failed semantic audit prevents acceptance and returns a nonzero exit.
The current per-design gate and hash-bound visual receipt determine acceptance;
implementation of these rules alone does not constitute a visual pass.
