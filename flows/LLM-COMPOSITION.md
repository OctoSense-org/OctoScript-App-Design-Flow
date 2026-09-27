# Lab purpose: context-driven composition through L0

The lab produces a discoverable library of styles, native components and
functional app-card compositions that an LLM can select and combine at runtime.
Selection uses the current request, stored user preferences, local time and
other supplied context. Both Sketch and generated-image pipelines contribute
to this same library.

A validated source-screen reproduction is one input to this process. The
deliverable also needs reusable interfaces, data/event bindings, compatibility
metadata and an LLM-facing description. Screenshot acceptance alone does not
establish that an arbitrary combination works as a live app.

## What the LLM needs to discover

| Capability | Interface to expose |
|---|---|
| Themes and style axes | Stable IDs, descriptive tags, available variants, typography, density, shape, surface and contrast constraints; supported overrides |
| Components | Named constructors, typed parameters, slots, supported data, events and state ownership; compatible theme overrides |
| App cards and page recipes | App capability, named layout, replaceable regions, required sources, state/events, viewport support and working examples |
| Assets and numerical graphics | Asset IDs and allowed regions; numerical chart adapters with data/units/domains, kept distinct from artwork |
| Validation status | Source provenance, tested renderer/viewports/interactions, review evidence, version and unsupported combinations |

Every available style and reusable card function should be discoverable. A
compact catalog can describe the whole library, with detailed signatures and
examples retrieved for the relevant candidates. Raw source paint fragments
need semantic wrappers before they become useful app-level functions. Keep
unadapted designs visible with their actual status instead of presenting them
as callable, validated components.

## Runtime selection contract

The host supplies a structured context snapshot: request, explicit appearance
preferences, app-specific preferences, local time and timezone, viewport and
available capabilities. Unknown context remains unknown. The LLM selects
registered IDs and supported overrides; the host validates and composes them.

Selection policy:

1. Enforce device/capability and accessibility constraints.
2. Honor the user's current explicit choices, then saved preferences.
3. Use supplied context such as time of day for unspecified choices.
4. Resolve missing or incompatible choices to a registered compatible default
   and record the reason. Do not silently substitute an unregistered style.

The selection is an inspectable data object, separate from application state.
For example, the proposed contract could select:

```json
{
  "app": "weather",
  "page_recipe": "forecast",
  "theme": "atro_light",
  "axes": {"density": "airy"},
  "component_overrides": {},
  "basis": ["saved preference: light", "request: hourly forecast"]
}
```

This is a proposed host/LLM contract, not an existing callable API. Actual
constructor names and admissible axes must come from the runtime registry.
Theme, layout and component choices should be independently selectable where
their contracts permit it. Combining one kit's typography, another kit's
component and a third card layout needs explicit token/slot compatibility;
source-screen parity does not validate that combination.

The same weather app could therefore use an airy forecast layout in the
morning and a compact dark dashboard at night when preferences allow it.
News and stock can choose their own compositions. Live data bindings, events,
selection, entered text and navigation state survive appearance changes.
Context changes must not interrupt an ongoing interaction or erase state.

## Verified current state — 2026-09-08

The native client this table inspected (`app/`, `a2app-l0/`) has since moved to
[OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard).
Links to it point at the last revision of this repository that contained it.

| Area | Present implementation | Exposure gap |
|---|---|---|
| Themes | Six base moods and five imported variants in [`l0_card.rs`](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/app/app/src/app/l0_card.rs): Atro dark/light, Camo dark/light and Taskplan light | [`l0.md`](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/a2app-l0/framework/l0.md) lists only Atro among imported packs and restricts style choice to explicit requests |
| Component adaptation | [`app-recipes.json`](https://github.com/OctoSense-org/Octoscript-Makepad/blob/main/components/l0/native/app-recipes.json) and [`l0_kit_components.rs`](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/app/app/src/app/l0_kit_components.rs) adapt supported weather/news/stock structures to source-backed kit components | Selection is coupled to the card's theme and recognized app/tree patterns; independent per-component kit selection is not established |
| Page recipes | [`l0_page_recipes.rs`](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/app/app/src/app/l0_page_recipes.rs) has weather dashboard/forecast, stock tiles/chart, news magazine/compact | The apply call is reached from `bundled_l0_source`'s review selector, not a general LLM composition interface |
| Prompt | [`main.rs`](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/cbbda4da0a9d0fbf13497335dd3342b71f35e71f/app/app/src/main.rs) assembles framework, constructor catalog and app exemplars through `l0_prompt_all` / `l0_prompt_for` | These functions take intent text; no explicit structured appearance-context parameter or complete style/recipe registry is supplied there |
| Import/export | [`export_app_recipes.py`](kits/sketch/export_app_recipes.py) exports selected semantic component roles from five imported variants | It does not expose every imported compound or image-derived design as an independently selectable live app function |
| Validation | Studio captures, semantic/state gates and visual receipts cover the tested designs | Arbitrary mixed styles, context selection and state-preserving runtime recomposition need separate evidence |

This audit covers the local L0 prompt and composition path. Server-side session
memory may contain other context; it is not a substitute for an explicit,
testable appearance-context contract in this path.

## Structure guided by this purpose

The next organization should make the flow easy to follow:

```text
Sketch / generated-image adapters
  → extracted styles, assets and semantic components
  → reusable app-card recipes with data/event contracts
  → native validation and evidence
  → versioned capability registry + LLM descriptions
  → context-based selection
  → validated L0 composition and native rendering
```

Logical owners for the next migration:

- `beauty/ingest/`: Sketch and image adapters, source identity and measurement.
- `beauty/library/`: styles, components, app-card recipes and compatibility data.
- `beauty/export/`: generate the machine-readable registry and LLM descriptions
  from the same definitions accepted by L0; check for missing/stale exports.
- `beauty/context/`: selection schema, preference precedence and scenario fixtures.
- `beauty/validation/`: current structural/semantic/visual gates plus composition
  and context scenarios. Shared transport, review and repair remain reusable.
- An explicit artifact root: source material, captures and immutable evidence.

These are responsibilities for migration, not directories already implemented.
The application owns live context and runtime state. Lab tools build, export
and validate capabilities consumed by that application. Preserve current paths
until their consumers and capture provenance have a tested migration.

## Interactive image-flow delivery

[image-to-appcard-flow](image-to-card/README.md) implements the delivery
extension for an authored 8–12-screen service journey: one atlas, source-bound
native mapping, explicit service ownership, subtree extraction, reducer tests,
WASM packaging and native-input browser checks. Applications still supply their
own service model and state bindings. This does not claim the broader automatic
context selection or capability-registry completion described above.

## Completion criteria

Both import pipelines register every reusable capability or explain why it is
not runtime-ready. Registry entries and LLM descriptions agree with accepted
L0 syntax and bundled native implementations. The normal app generation path
can select styles, layouts and supported component overrides from supplied
context. Explicit preferences win over time-based defaults. Invalid or
incompatible choices fail validation or use a documented compatible default.

Scenario tests cover weather, news and stock across preferences, day/night,
missing context and device constraints. Interaction tests demonstrate that
theme/layout changes preserve data, events and user state. Studio and visual
QA validate representative combinations at their declared viewport sizes.
Passing the existing source-artboard corpus alone does not satisfy this goal.
