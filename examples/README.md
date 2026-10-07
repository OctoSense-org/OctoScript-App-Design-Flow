# Examples

English | [简体中文](README.zh-CN.md)

The examples in the table are reference journeys, complete multi-screen apps
built with the [image-to-card flow](../flows/image-to-card/FLOW.md),
contained apps built with the [script-app flow](../flows/script-app/FLOW.md), and
Android-authored prototype archives with historical phone review evidence.
Each keeps its source, walkthrough and validation evidence together; the card
journeys also own their service code, reviewed card scenes, design source,
launcher and tests. Git ignores runtime state and personal data.

| Example | Runs as | Description |
| --- | --- | --- |
| [Agentic hackathon apps](agentic-hackathon/README.md) | Native Splash apps / app-agent integration | Email Action and Meeting Planner: fictional data, real-agent entry points, labeled offline fallbacks, confirmation, receipts and native regression tests. |
| [Aircon](aircon/README.md) | Native cards / WASM | One purchase-to-installation journey with 12 screen states and 14 extracted service-card variants. |
| [School](school/README.md) | Native cards / WASM | School notice, calendar and payment journey. |
| [Health](health/README.md) | Native cards / WASM | Fictional health-check booking journey. |
| [Reunion](reunion/README.md) | Native cards / WASM | Reunion planning, RSVP and payment journey. |
| [Calendar](calendar/README.md) | Native cards / browser preview + sync server | Calendar for two devices: 10 screen states, 4 service cards and a SQLite-backed server whose operation log every client replays. |
| [Android-authored card prototypes](android-a2app-card-templates/README.md) | AppStudio on Android; glance / expanded / full app | Two model-authored six-family collections: each 4.5/5 overall offline prototype, 4.4/5 visual; exact source replay and native evidence. |

[shared/](shared/README.md) contains common browser adapters and historical
cross-app verification artifacts; it is not an app.

[connected-apps/](connected-apps/README.md) holds the development copies of
the three script apps published in App Hub: GitHub Notes, Inbox Assistant and
Google Calendar. They sign in to GitHub or Google through the OctoSense host.
The [connected-apps README](connected-apps/README.md) shows how each app is
built and submitted, and which patterns to copy or avoid.

System script apps (News, Photos, Maps, Camera, Mail) and the personal-data
skill live in
[OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps).
The native client and runtime live in
[OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard).
Makepad and OctoScript live in the separate
[native workspace](../docs/NATIVE-WORKSPACE.md).

## Layout of one example

In each example, `cards/` holds full screen states: `aircon/cards/aircon-01`
through `aircon-12` are 12 screen states of **one Aircon app**, not 12 apps.
`service-cards/` holds smaller interactive panels extracted from those screens
(an order, an installation appointment, a calendar update, a payment panel),
each with its own data and actions. Service cards are grouped by the
`owner_app` field in `service-cards/catalogue.json`. In Aircon the owners are
`shopping`, `logistics`, `installation`, `calendar` and `payment`. Each owner is
a service in the journey, not a separate project.

Each example has its own flow manifest, `image-to-appcard-flow.json`. Run the
flow from the repository root, choosing an example explicitly:

```sh
bash tools/image-to-appcard-flow.sh plan \
  --project "$PWD/examples/aircon" \
  --manifest "$PWD/examples/aircon/image-to-appcard-flow.json"
```

`plan` prints the commands each stage would run and exits 0 when the manifest
is valid; it runs nothing. To start a new project, copy
[`flows/image-to-card/examples/flow.template.json`](../flows/image-to-card/examples/flow.template.json)
into its directory as `image-to-appcard-flow.json`.

For native UI tests, use [Makepad's built-in instrument](../flows/core/NATIVE-INSTRUMENT.md)
with hidden windows. Older Makepad Studio scripts and receipts record past runs
only. Their native and image-parity results predate the move.

## Recorded evidence keeps its original paths

Receipts and evidence were recorded before the restructure and still name
`lab/...`, `apps/...`, `pipeline/...` or the repository's former names
(`Octosense-Service-AppCards`, `Octoscript-AppCard`). They are hash-bound
records of what ran. Don't rewrite these paths:

- `*/cards/*/rounds/`, `*/evidence/`, `aircon/wizard/wasm-host/smoke-evidence/`
- `aircon/runtime/infrastructure.json` and the `*.patch` files it hashes
- `shared/verification.json`, `shared/layout-validation.json`, `shared/flows-history.md`
- `*/wizard/card-bundle/cards.provenance.json`

`aircon/scripts/verify_native_flow.py` and
`aircon/scripts/verify_standalone_cards.py` map the recorded `lab/` and
`apps/` prefixes to `flows/` and `examples/` when they re-hash sources.
