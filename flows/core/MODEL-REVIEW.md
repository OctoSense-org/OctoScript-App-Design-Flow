# Image reading and reviewer portability

For app authorship and iterative native testing, also follow
[model-driven development and validation](../../docs/MODEL-VALIDATION.md).
It separates the author's tool use, operator tests and independent visual
judgment, and gives source-backed recovery steps for observed model failures.
The image-to-card review contract below continues to apply to its saved rounds.

The generated-image pipeline has no Astra-specific API, SDK, endpoint or image
reader. A generator supplies a PNG; a separate reviewer interprets it. The
successful reference conversions in this workspace used the coding assistant's
visual reasoning for semantic decisions, artwork choices and final screenshot
QA. Those judgments are recorded as mappings and review receipts, not hidden
inside a model service. Equivalent quality from another reviewer has not been
established by a comparative benchmark.

| Step | Implementation | Reviewer requirement |
|---|---|---|
| Image generation | External tool; original prompt/PNG and declared provenance | Any suitable generator; no built-in provider call |
| OCR | Apple Vision via Swift | No language-model dependency |
| Edges, surfaces, glyph metrics | OpenCV, NumPy, Pillow, fontTools | Proposals and measurements need ambiguity resolution |
| Semantic mapping | Authored contract plus `semantic-map.json` | Human or capable vision model reads the actual image |
| Artwork/data choice | Explicit policy, crop provenance and numerical adapters | Decide chart vs artwork; inspect crop/SVG quality |
| Compilation and inspection | L0 runtime and Makepad Studio | No vision model |
| Measured gates | Local Python plus Studio state/paint evidence | Cannot be overridden by a visual score |
| Visual QA | Frozen source/native PNG pair and explicit receipt | Human or capable vision model compares the images |

The generator and reviewer can be different tools. Provider/model fields in
`generation.json` describe the actual generation; they do not configure an API
or choose a reviewer. Use the actual model name when exposed and leave it
unrecorded otherwise. A requested font in a generation prompt is intent, not
proof that the generator rendered that exact face.

## Handoff to another reviewer

Give the reviewer the original image, submitted prompt, contract, observed
OCR/bounds, source IDs, mapping rules and available widget/data/asset contracts.
For final QA, use `review.py prepare` and provide its frozen PNG pair. The
reviewer needs the ability to inspect images; a text-only model cannot perform
the visual stages merely by reading OCR.

Use this provider-neutral instruction for semantic conversion:

> Inspect the entire original UI image and the supplied measurements. Keep
> requested intent separate from observed pixels. Classify every element and
> anonymous numerical region. Map text and controls to native widgets, charts
> to numerical widgets with explicit data/units/domains, and artwork to a
> source-backed SVG or isolated asset. Do not infer business data from a curve
> without declaring it approximate. Preserve source IDs, hierarchy and control
> state. Report ambiguity as needs_review. Produce concrete mapping/annotation
> changes and reasons; do not claim acceptance before Studio evidence exists.

Use this instruction for screenshot review:

> Inspect both images in the frozen pair. Compare typography, colors, imagery
> and effects; record remaining differences and whether they are acceptable
> for the specified artboard. Read measured/semantic findings separately.
> Complete the supplied decision JSON with your reviewer identity, explicit
> verdict, written basis and all four criteria. For Sketch, provide the 1–10
> design-match score. Do not approve an image you did not inspect. A visual
> verdict cannot waive structural, semantic, state, clipping or freshness gates.

`review.py submit` validates hashes and receipt completeness. It never makes
the judgment itself. Using another reviewer changes the judgment source, not
the gate tolerances or required native evidence. New inputs still need repair
and review; the scripts are not an unattended universal image-to-app converter.
