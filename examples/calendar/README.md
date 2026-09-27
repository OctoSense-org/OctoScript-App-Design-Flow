# Calendar — one calendar, two devices

English | [简体中文](README.zh-CN.md)

An iOS-style Calendar built with the [image-to-appcard flow](../../flows/image-to-card/README.md),
backed by a real sync service: one SQLite database, one ordered operation log,
one reducer that every client replays. "Alex · Phone" (the app screens) and
"Sam · Desktop" (the desktop service cards) submit operations to the same
server and converge on the same state; conflicts are refused by the server,
undo names the exact step it reverses, and a change made on one device is
*offered* to the other — never pushed onto its screen.

## What is here

| Part | Files | What it does |
| --- | --- | --- |
| Storyboard | `scripts/design.py`, `source/storyboard.html`, `source/atlas.png`, `source/prompt.txt` | One logical layout (406 × 776) for 10 scenes. The atlas is a deterministic Chromium render of it at 2× (`source/render_atlas.mjs`), recorded as the provider — no image model was used. |
| Pipeline | `image-to-appcard-flow.json`, `scripts/author_calendar.py`, `scripts/build_calendar.py`, `cards/calendar-01..10`, `artwork/`, `wizard/card-bundle/` | Intake freezes the atlas; the author script writes contracts, reviewed semantic maps and service actions from the same spec; compile emits the L0 scenes; extract produces 4 standalone service cards; bundle exports the browser package. |
| Calendar core | `service/calendar_core.py`, `wizard/core.mjs`, `service/fixtures/ops.json` | The domain reducer, twice: Python for the server and native runtimes, JS for the browser. A shared two-device fixture pins both to the same verdicts and the same state digest. |
| Sync server | `server/calendar_server.py`, `service/sync_client.py` | Standard-library HTTP + SQLite (WAL). `POST /v1/ops` applies an operation and logs the verdict; `GET /v1/ops?since=N&wait=S` long-polls the log; `GET /v1/stream` is the same as server-sent events; `GET /v1/state` is the snapshot with its digest. Bearer token, explicit CORS origins. |
| Session | `wizard/service.mjs`, `wizard/sync.mjs`, `wizard/copy.mjs`, `route_test.json` | The wizard session (`createSession`, `getView`, `activateControl`, `nextUpdate`, `goBack`, `restart`) plus `applyRecords`/`adoptSnapshot` for the server, and the fetch/long-poll transport. |
| Preview | `wizard/preview/`, `scripts/demo.sh` | An HTML rendering of the storyboard driven by the real session, sync client and server, so two browser tabs can be watched syncing. It is not the native renderer. |
| **Native app** | `native/` (crate `octosense-calendar`) | The Calendar as an in-process OctoSense AppModule. Every screen is a scene built at runtime from the calendar state (any month, any events), compiled to L0 and mounted as native Makepad Kit widgets — the same lowering the reviewed storyboard cards use. Ships its own replica of the service log (`model.rs`, the third twin of the reducer) and a sync link (`sync.rs`). Runs in the OctoSense shell on macOS and Android. |

Scenes: 01 month · 02 day · 03 event · 04 new event · 05 desktop *Calendar · Synced* ·
06 desktop *Invitation from Sam* · 07 time picker with a conflict · 08 calendars ·
09 desktop *Sync · Up to date* · 10 desktop *Calendar · Removed*. Cards extracted:
`calendar-synced-05`, `calendar-invite-06`, `calendar-removed-10` (owner `calendar`)
and `calendar-sync-status-09` (owner `sync`). 64 native controls, bilingual EN/CN.

## Service rules

- An operation is `{id, actor, action, payload}`; actions: `event.create`, `event.update`,
  `event.delete`, `event.restore`, `invite.respond`, `calendar.set_visible`, `device.sync`.
- The server applies operations in arrival order and records every verdict. Replaying an
  identical operation id is a no-op; reusing an id with different content is refused.
- One owner, one timeline: an event overlapping any live event is refused (`conflict:<id>`),
  on create, update and restore. The time picker disables such slots before the server does.
- Undo is the named inverse: undoing a create deletes that event; undoing a delete restores
  the same event, with its original content. Nothing else is touched.
- Accepting an invitation adds one event and answers Sam; a second acceptance never
  duplicates; declining removes only our copy, Sam's invitation is untouched.
- Hiding a calendar changes visibility only. `device.sync` records a sync; it changes nothing.
- A remote change never moves the screen. The session offers it as `view.nextUpdate`
  ("Show 1 change from Alex · Phone") and shows the synced card when the user asks.
  A server rejection of this device's own operation rolls the optimistic change back and
  leaves a notice.

## Run it

```sh
export BEAUTY_PYTHON="$PWD/flows/image-lib/.venv/bin/python"   # from the repository root
bash tools/image-to-appcard-flow.sh run \
  --project "$PWD/examples/calendar" --manifest "$PWD/examples/calendar/image-to-appcard-flow.json" \
  --stages intake,semantic,compile,bundle,service-test --node /path/to/node
```

Rebuild from the spec (new atlas → new intake; delete `cards/`, `artwork/`, `pipeline-output/`
first, the intake refuses a changed atlas in an existing output directory):

```sh
cd examples/calendar
"$BEAUTY_PYTHON" scripts/design.py                         # → source/storyboard.html
node source/render_atlas.mjs source/storyboard.html source/atlas.png 3488 4950
"$BEAUTY_PYTHON" scripts/author_calendar.py                # intake, prepare, contracts, compile
"$BEAUTY_PYTHON" scripts/build_calendar.py                 # extract cards, export the bundle
```

Two devices syncing, in the browser:

```sh
cd examples/calendar && PYTHON="$BEAUTY_PYTHON" bash scripts/demo.sh
# prints the phone tab (?device=alex-phone) and desktop tab (?device=sam-desktop) URLs
```

Tests (also what `checks.service-test` runs):

```sh
"$BEAUTY_PYTHON" -m unittest discover -s service -p 'test_*.py'   # reducer + fixture (9)
"$BEAUTY_PYTHON" -m unittest discover -s server  -p 'test_*.py'   # live server: convergence, verdicts, restart, auth, SSE (7)
node --test wizard/service.test.mjs wizard/core.test.mjs          # routes × 2 locales, invariants, rollback (24)
BEAUTY_PYTHON=… node --test wizard/sync.test.mjs                  # two JS sessions against a spawned Python server (2)
node wizard/preview/smoke.mjs                                     # two Chromium tabs against a live server, screenshots
```

## The native app

`native/` is a Rust `AppModule` written for the earlier native OctoSense shell
(feature `app-calendar`). That shell is archived and the native client now lives in
[OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard); this module
is kept as a reference implementation and is not built by this repository's CI. Screens: month (any month, dots
per calendar, today/selection rings, the selected day's list), day timeline
(hour rows, overlapping events share the width, now line), event detail, editor
(title/location/notes fields, all-day, start/end pickers with conflicting slots
disabled, calendar chooser, alert), calendars (show/hide, EN/中文), inbox
(invitations with Accept/Maybe/Decline, changes from the other device), sync
status. Ops go through the same reducer as the server; conflicts are refused
before they are sent; a rejection from the server rolls the change back and is
listed on the Sync screen.

Configuration (environment on desktop; `--es makepad.APP_CONFIG` keys
`calendar_server`, `calendar_token`, `calendar_device`, `calendar_locale` on Android):
`CALENDAR_SERVER`, `CALENDAR_TOKEN` (for example `$(cat examples/calendar/runtime/calendar.token)`),
`CALENDAR_DEVICE`, `CALENDAR_LOCALE`. `native/desktop-apps.json` is the module
list the shell's `--apps` option read.

Without `CALENDAR_SERVER` the app runs on-device with the demo fixture laid
around the real today. Unit tests: `cargo test --manifest-path examples/calendar/native/Cargo.toml`
(reducer fixture parity with the Python/JS twins, scene lowering through the
shared L0 pipeline, every screen renders, server records confirm/roll back).

## Status and limits

- Pipeline stages run and passing: intake, prepare, semantic, compile, extract, bundle,
  service-test (receipts under `pipeline-output/runs/`). Not run: capture, gate, wasm,
  integrate, web-test, hosted-test — there is no native capture or visual acceptance yet,
  and the WASM package for the website has not been built.
- The atlas is authored, not generated: contracts and reference agree by construction,
  which is why intake measurement is a consistency check rather than OCR of an unknown image.
- The server is a local, single-process service with a shared bearer token: fine for a
  household and for tests, not multi-tenant. Actor identity is the device id the client
  declares; a production deployment authenticates devices before trusting `actor`.
- The browser preview draws the storyboard HTML; the native app mounts real Kit widgets. The
  native scenes are built at runtime rather than from the reviewed storyboard cards, so the
  pipeline's capture/gate stages do not cover them yet.
