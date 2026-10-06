# Lab: styles and app-card composition for LLMs

The lab's purpose is to expose themes, native component functions and reusable
app-card layouts to an LLM so it can compose an app using the request, user
preferences, time of day and other supplied context. Sketch and generated-image
conversion build this library; native validation makes its capabilities
reviewable. See [the composition contract and current gaps](LLM-COMPOSITION.md).

For a complete agentic application journey, start with
[image-to-appcard-flow](image-to-appcard-flow/README.md): one 8–12-screen atlas,
reviewed native scenes, independently owned service cards, click-driven state,
Makepad WASM and verified Astro integration. Run `tools/image-to-appcard-flow.sh`.

New native tests use [the built-in Makepad HTTP instrument](core/NATIVE-INSTRUMENT.md)
with a standalone release binary and optional hidden window. Studio is not required
for this path; older capture/gate adapters remain explicitly documented as legacy.

For individual beauty-card work, start with
[the generic reproduction guide](core/REPRODUCE.md). Both Sketch and
generated-image inputs produce native Makepad widgets and require native
inspection, semantic checks and explicit visual review. The entry point is
`tools/beauty-pipeline.sh` at the workspace root.

| Area | Status | Contents / entry point |
|---|---|---|
| [core](core/README.md) | Current shared infrastructure | Mapping policy, repair engine, review packets, Studio bridge, reproducible setup |
| [sketch-to-appcard](sketch-to-appcard/README.md) | Current Sketch adapter | Import, native/L0 composition, kit promotion, capture and gates; `run_kit.py` |
| [image-to-appcard](image-to-appcard/README.md) | Current image adapter | Prompt/contract intake, OCR and measurements, widget mapping, capture and gates; `run.py` |
| [image-to-appcard-flow](image-to-appcard-flow/README.md) | Service-flow extension of the image adapter | Single-atlas intake, native subtree export, service checks, WASM packaging and web integration; `flow.py` |
| `tests/` | Maintenance tests | Cache-cleanup safety checks |

Use [STRUCTURE.md](STRUCTURE.md) for directory ownership, retained dependencies,
storage rules and the remaining migration work. The next organization follows
ingest → library → export → context selection → validated composition.
Historical findings describe
their own runs; they do not establish the current implementation's quality.

```sh
# Read-only storage inventory; commands run from the workspace root.
python3 lab/maintain.py inventory

# Preview recognized bytecode/Finder caches. Export caches require opt-in.
python3 lab/maintain.py clean --exports
# Stop Sketch import jobs before applying; future imports may need re-export.
python3 lab/maintain.py clean --exports --apply
```

Sources, final assets, screenshots, review rounds and environments are outside
the cleaner's scope. Inspection history stays available for acceptance and
repair. Local environments, QA scratch space and transient image capture
outputs are ignored by Git; ignoring files does not remove existing tracked
history. Do not share purchased assets or local logs as generic examples.
