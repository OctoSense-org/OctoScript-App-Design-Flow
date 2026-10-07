# Flows structure and cleanup policy

Organize `flows/` around [LLM-driven style and app card composition](LLM-COMPOSITION.md):
ingest designs, extract reusable styles and components, publish a registry,
select from context, and validate the native composition. That contract
separates what the runtime supports today from the registry and
context-selection work still to do.

## Who owns what

| Directory | Owns |
| --- | --- |
| `core/` | Policy, review, repair, the Studio bridge, composition, gates and the native renderer, shared by every flow |
| `kits/sketch/` | Sketch document import and theme-kit promotion: the Sketch → theme kit adapter |
| `image-lib/` | Image observation and mapping: the image → app card adapter |
| `image-to-card/` | Multi-screen service state, independent cards and WASM/web delivery on top of `image-lib`; it reuses the core gates and is not a third adapter |
| `script-app/` | No code: a procedure over `tools/octo` and App Hub's `hub` and `card-host` |

Keep shared rules in `core/` and source-specific conversion in its adapter.
Put a new experiment in a named study directory with a README that states its
purpose, inputs, entry point and status. Remove an obsolete study only after
you check its callers and record the decision.

## Current directory boundaries

```text
flows/
  README.md                 flow index and the shared flow contract
  STRUCTURE.md              ownership and retention rules
  LLM-COMPOSITION.md        composition contract and gaps
  maintain.py               inventory and narrowly scoped cache cleanup
  tests/                    maintenance safety tests
  script-app/FLOW.md        the text-brief flow: tools/octo steps to a gate-passing bundle
  core/                     shared by all flows: mapping policy, review packets,
                            repair engine, Studio bridge, composition and gates,
                            the native renderer, kit configuration, native paths
    kits/                   kit configuration
    work/<kit>/             source copies, final assets and capture evidence (ignored)
    examples/               generic, redistributable input templates
    qa-work/                local verification evidence (ignored)
  image-to-card/            the image design flow (FLOW.md): atlas intake, native
                            subtree export, provenance-aware bundle, WASM templates;
                            application sources/evidence live in examples/<name>/
  image-lib/                generated-image library the flow calls: intake,
                            measurement, mapping; run.py, its regression tests
    <design-id>/            prompt, reference, contract and reviewed mapping
      rounds/<round>/       immutable capture evidence (ignored)
    published/              local review gallery served on :8170 (ignored)
    .venv/                  local environment (ignored)
  kits/sketch/              Sketch theme-kit ingest (FLOW.md): import, native
                            composition, kit promotion; run_kit.py, tests, fonts
    .venv/                  local environment (ignored)
```

Code, durable input descriptions and generic examples belong in Git. New
scratch outputs go under an adapter's `work/` or `qa-work/`; never add more
`out2`, `frozen3` or `shots_final_final` siblings to a source directory.
Preserve explicit source IDs, run IDs and hash-bound review records.

## Safe cleanup

Deleting local caches frees disk space. Changing Git tracking or history is a
different problem: it needs a dataset and retention migration.

`maintain.py clean` selects only Python bytecode directories (`__pycache__`)
and Finder metadata (`.DS_Store`). `--exports` also selects the Sketch
`graphic-export-cache` directories under `core/work/<kit>/native*/`, but only
where `source.sketch`, `resolved.sketch` and `source-cache.json` remain beside
them. These caches are intermediate CLI exports that `sketch_assets.py` copies
into final assets, and a cache miss triggers a re-export. They are outside the
native capture fingerprint. The next import that needs them takes longer and
requires the original, compatible Sketch tool.

Cleanup previews by default and validates every candidate before it deletes
anything. It refuses tracked files and symlinks and skips installed
environments. Stop import jobs first: the tool does not coordinate with an
active importer. There is no broad `purge`, and failed review rounds are never
removed automatically.

The local, Git-ignored records `core/qa-work/structure/validation.json` and
`core/qa-work/structure/archive-removal.json` describe the last cleanup and
its test results.

## Files that are old but still required

| Path | Verified consumer / reason to retain |
| --- | --- |
| `core/cards2/`, the `atro` kit's legacy `cards_dir` (local, not tracked) | Read through `core/kitconf.py` by `gallery.py`, `gate_kit.py`, `judge_shots.py` and `promote_l0.py` for the `atro` kit; not interchangeable with current native cards |
| `image-lib/weather-v1/` | Original image pilot and its provenance, referenced by the adapter README |
| `image-lib/.deps/` | Still used by `observe.py`, `measure_surfaces.py` and `repair_reference.py`; the portable guide uses dedicated environments |
| Captures, repair rounds, import receipts, source trees and manifests | Acceptance, replay, migration provenance and regression evidence |

## Further structural migration

The next layout should group the beauty pipelines (`tools/beauty-pipeline.sh`,
`tools/beauty-studio.sh`) by `ingest`, `library`, `export`, `context` and
`validation`, with shared infrastructure, research, application fixtures and
an explicit artifact root. A registry/export layer would then expose styles,
component functions and app card recipes to the LLM. This needs a
compatibility migration, not filesystem moves alone:

1. Introduce configuration for code, design, dataset and artifact roots;
   replace `HERE.parent`, absolute paths and runtime resource URLs at their
   actual consumers. Keep existing CLI paths working during the transition.
2. Move app-consumed baselines and corpora with all imports and `include_str!`
   references. Split reusable gates from one-off study runners, and adapters
   from their tests and data. Retire legacy scripts only after their callers
   and regression inputs are migrated.
3. Export large historical datasets/evidence with manifests, checksums,
   restoration commands and a stated retention policy. Keep current source,
   accepted runs and referenced repair history available. Git LFS or artifact
   storage is a storage choice, not permission to discard evidence.
4. Revalidate affected captures and browser links after changing paths.
   Sketch capture fingerprints currently include absolute input paths; image
   proof also names source paths. Moving an active tree can invalidate saved
   evidence even when file bytes are unchanged. Never edit proof hashes to
   make a moved tree appear current.
