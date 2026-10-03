# Examples

English | [简体中文](README.zh-CN.md)

Reference journeys built with the [image-to-card flow](../flows/image-to-card/FLOW.md),
plus Android-authored prototypes reviewed on the phone. The image-to-card
examples own their service code, reviewed card scenes, design source,
launcher, tests and fixture evidence. Runtime state and personal data stay
ignored. They were `apps/<name>/` before the restructure.

| Example | Surfaces | Description |
| --- | --- | --- |
| [Aircon](aircon/README.md) | Native cards / WASM | One purchase-to-installation journey with 12 screen states and 14 extracted service-card variants. |
| [School](school/README.md) | Native cards / WASM | School notice, calendar and payment journey. |
| [Health](health/README.md) | Native cards / WASM | Fictional health-check booking journey. |
| [Reunion](reunion/README.md) | Native cards / WASM | Reunion planning, RSVP and payment journey. |
| [Calendar](calendar/README.md) | Native cards / browser preview + sync server | Calendar for two devices: 10 screens, 4 service cards, and a SQLite-backed operation-log server every client replays. |
| [Android-authored card prototypes](android-a2app-card-templates/README.md) | AppStudio on Android; glance / expanded / full app | Two model-authored six-family collections: each 4.5/5 overall offline prototype, 4.4/5 visual; exact source replay and native evidence. |

[shared/](shared/README.md) contains common browser adapters and historical
cross-app verification artifacts; it is not an app.

System script apps (News, Photos, Maps, Camera, Mail) and the personal-data
skill moved to
[OctoSense-org/OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps).
The native client and runtime moved to
[OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard).
Makepad and Octoscript live in the separate
[native workspace](../docs/NATIVE-WORKSPACE.md).

## Layout of one example

Within an example, `cards/` holds full screen states. For example,
`aircon/cards/aircon-01` through `aircon-12` are twelve screens of **one Aircon
app**, not twelve apps. `service-cards/` holds smaller interactive panels
extracted from those screens (an order, an installation appointment, a calendar
update, a payment panel) with their own data and actions. Their owner names
identify services within the journey, not additional projects.

Each example keeps its design source, scenes, service code and
`image-to-appcard-flow.json` together. Run the flow from the repository root,
choosing an example explicitly:

```sh
bash tools/image-to-appcard-flow.sh plan \
  --project "$PWD/examples/aircon" \
  --manifest "$PWD/examples/aircon/image-to-appcard-flow.json"
```

`plan` prints the commands each stage would run and exits 0 when the manifest
is valid; it runs nothing. To start a new project, copy
[`flows/image-to-card/examples/flow.template.json`](../flows/image-to-card/examples/flow.template.json).

For native UI tests, use [Makepad's built-in instrument](../flows/core/NATIVE-INSTRUMENT.md)
with hidden windows. Older Studio scripts and receipts are historical material;
moving them does not constitute a fresh native or image-parity acceptance.

## Recorded evidence keeps its original paths

Receipts and evidence were recorded before the restructure and still name
`lab/...`, `apps/...`, `pipeline/...` or the repository's former names
(`Octosense-Service-AppCards`, `Octoscript-AppCard`). They are hash-bound
records of what ran, so they are not rewritten:

- `*/cards/*/rounds/`, `*/evidence/`, `aircon/wizard/wasm-host/smoke-evidence/`
- `aircon/runtime/infrastructure.json` and the `*.patch` files it hashes
- `shared/verification.json`, `shared/layout-validation.json`, `shared/flows-history.md`
- `*/wizard/card-bundle/cards.provenance.json`
- `calendar/source/storyboard.html` (design source with its original font URLs)

`aircon/scripts/verify_native_flow.py` and `verify_standalone_cards.py` map the
recorded `lab/` and `apps/` prefixes to `flows/` and `examples/` when they
re-hash sources.
