# Quickstart: build, run and ship an OctoSense script app

One path, from nothing to a bundle the App Hub gate admits. Every command was
run on macOS (Apple silicon) unless marked **unverified**: first on 2026-09-25,
then again end to end from fresh clones of `main` on 2026-09-26 (a new app
built from this page and [SCRIPT-API](SCRIPT-API.md) alone, through
`tools/octo check`, `hub scan`, a local publish and an install in
OctoSense-Desktop).

```text
1 prerequisites → 2 build hub + card-host → 3 octo new → 4 octo run → 5 edit loop
→ 6 capabilities → 7 test and capture → 8 octo check → 9 on a phone → 10 publish
```

## 1. Prerequisites

- **Rust** (stable, via rustup). `cargo` lives in `~/.cargo/bin`; put it on
  `PATH` (`export PATH=$HOME/.cargo/bin:$PATH`).
- **Python 3.9+** for `tools/octo` (no packages needed).
- **A graphical session** for `card-host` (it opens a real window, 412x892
  points, even when an agent drives it).
- **The App Hub and its sibling sources** in one workspace directory:

  ```text
  <workspace>/
    OctoScript-App-Design-Flow/   this repository
    OctoSense-App-Hub/            hub, card-host, appstore
    makepad/                      OctoSense-org/makepad
    octoscript-makepad/           OctoSense-org/Octoscript-Makepad
    octoscript/                   OctoSense-org/Octoscript
  ```

  The App Hub's `Cargo.toml` patches its Makepad and Octoscript dependencies to
  exactly those sibling paths (`../makepad`, `../octoscript-makepad`,
  `../octoscript`). Create the workspace with these commands; `setup-native.py`
  clones the three runtime siblings (lower-case directory names, as above) at
  the revisions [native-runtime.lock.json](../native-runtime.lock.json) selects
  ([NATIVE-WORKSPACE](NATIVE-WORKSPACE.md) has its options):

  ```sh
  mkdir octosense-ws && cd octosense-ws
  git clone https://github.com/OctoSense-org/OctoScript-App-Design-Flow.git
  git clone https://github.com/OctoSense-org/OctoSense-App-Hub.git
  cd OctoScript-App-Design-Flow
  python3 tools/setup-native.py           # makepad, octoscript, octoscript-makepad beside it
  python3 tools/setup-native.py --check   # pass: exits 0 and prints the pinned revisions
  ```

  Verified 2026-09-26: the two clones took about 1.5 minutes (this repository
  is about 1 GB, mostly design evidence; `--depth 1` is fine for building
  apps), `setup-native.py` about 30 seconds.

  Use `main` of App Hub and of this repository. The runtime is Octoscript-Makepad
  `463e3da8`, which pins makepad `cd812acd` (OctoSense-org/makepad#30, merged)
  and octoscript `68f6a9df`; App Hub `main` includes OctoSense-App-Hub#4
  (merged as `0d36f50b`). The 2026-09-26 re-run used App Hub `6c075d0`.

## 2. Build `hub` and `card-host`

```sh
cd <workspace>/OctoSense-App-Hub
cargo build --release -p octosense-card-host -p octosense-app-hub
```

Verified (`Finished release profile … in 1m 43s` with dependencies cached).
The binaries land in `target/release/` (or `$CARGO_TARGET_DIR/release/`).

Then, from this repository:

```sh
export OCTOSENSE_APP_HUB=<workspace>/OctoSense-App-Hub   # optional when it is a sibling
tools/octo doctor
```

`doctor` finds `hub` and `card-host` in `$OCTO_HUB`/`$OCTO_CARD_HOST`, then
`$OCTOSENSE_APP_HUB/target/release`, `$CARGO_TARGET_DIR/release`,
`$OCTOSENSE_APP_HUB/../target/release`, the sibling
`../OctoSense-App-Hub/target/release`, then `PATH`. It rejects GitHub's
unrelated `hub` CLI. Verified output ends with
`ready: tools/octo new <dir> && tools/octo run <dir>/bundle`; when something is
missing it prints `[fail]` lines, where it looked, and the fix.

## 3. Create an app

```sh
tools/octo new ~/apps/my-app --id my-notes --name "My Notes"
```

Copies [templates/script-app](../templates/script-app/README.md) (`bundle/`,
`AGENTS.md` with its `CLAUDE.md`/`GEMINI.md` shims, `.gitignore`), sets `id` and `name` in the manifest and the
title label in `main.splash`, and stamps the bundle. Verified output (run
with `--id my-test-notes --name "Test Notes"`):

```text
created …/my-app
  id my-test-notes, name 'Test Notes', version 0.1.0, bundle stamped
```

Ids are `[a-z0-9.-]{1,64}`, not starting with `.`; `os.` is reserved for
system apps. Make `~/apps/my-app` its own git repository.

## 4. Run it on the desktop

```sh
tools/octo run ~/apps/my-app/bundle --port 8141            # foreground; Ctrl-C quits
tools/octo run ~/apps/my-app/bundle --port 8141 --detach   # background; returns when admitted
```

This is `card-host --bundle <bundle> --app-data <app>/.local-state
--allow-unsigned --stamp` with `MAKEPAD_REMOTE=8141`, started from the App Hub
directory. Verified `--detach` output:

```text
[makepad-remote] listening on 127.0.0.1:8141 pid=18656 app=card-host grabs=/var/folders/…
[I] crates/card-host/src/main.rs:189:9 - card-host: my-test-notes 0.1.0 admitted — capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
pid 18656  log …/my-app/.local-state/card-host.log
```

- `--stamp` rewrites the manifest digest on every start, so edits run without
  a separate `hub stamp`. Without it (`--no-stamp`) card-host refuses a
  bundle whose bytes changed.
- `--system` admits an `os.*` system app under system ceilings.
- The app's files live in its jail: `<app>/.local-state/<id>/`.
- Look in the log for `admitted` **and** for errors after
  `[SPLASH] eval:` (script errors print there, see
  [SCRIPT-API](SCRIPT-API.md#errors-and-the-log)). Search for the error
  forms, not the word "error": Makepad's `[ui-hang]` diagnostics mention
  Metal's `MTLCompilerError` in healthy runs.

  ```sh
  grep -nE '\[E\]|splash:[0-9]+:|refused|on_render closure failed|callback error' <app>/.local-state/card-host.log
  ```

Drive it over HTTP (all GET; coordinates are window points, y down):

| Route | Does |
| --- | --- |
| `curl -s 127.0.0.1:8141/snap` | widgets with rects and text: `{"s":[{"i":id,"ty":type,"r":[x,y,w,h],"t":text}]}`; `?q=` filters |
| `curl -s 127.0.0.1:8141/d` | the whole widget tree as text |
| `curl -s "127.0.0.1:8141/click?x=150&y=140&wait=1"` | a real click (`wait=1`: answer after the next frame) |
| `curl -s "127.0.0.1:8141/t?t=Buy%20milk&wait=1"` | type text into the focused input |
| `curl -s "127.0.0.1:8141/k?k=down&c=ReturnKey"` | a key event |
| `curl -s "127.0.0.1:8141/log?n=50"` | the last log lines |
| `tools/octo shot 8141 out.png` | PNG of the window (`/g?raw=1`) |
| `curl -s 127.0.0.1:8141/quit` | quit; always end with this (or `/gq`) |

Driving tips (verified 2026-09-26):

- `/t` types into whatever has focus. Clicking a button takes focus away from
  a `TextInput`, so click the input again before the next `/t`. To clear it,
  send `/k?k=down&c=Backspace` once per character.
- `?q=` also matches the `Splash` widget itself, whose text is your whole
  `main.splash`; filter the result by type (`"ty":"Label"`) or read the rects.
- A `shot` taken the moment `run --detach` returns can catch a frame before
  text is drawn (shapes but no labels). Wait a second, or send any input with
  `wait=1`, before the first capture, and look at every PNG.
- The window is 412x892 points and `/g?raw=1` is at 2x on a Retina Mac:
  divide screenshot pixels by 2 to get click coordinates. The capture
  includes `card-host`'s 32-point caption bar at the top.

Verified: `/snap` showed the title label `"t":"Test Notes"`; clicking the
input, `/t?t=Buy%20milk`, then clicking **Add** wrote `["Buy milk"]` to
`.local-state/my-test-notes/notes.json` and drew the row; tapping the row
removed it; a restart reloaded stored notes. Rows built by `on_render` do not
always appear in `/snap` or `/d`: confirm them with a screenshot or the jail
file, and click them by coordinates from the screenshot (pixels / 2 on a
Retina Mac).

## 5. The edit loop

1. Edit `bundle/main.splash` (the language: [SCRIPT-API](SCRIPT-API.md)).
2. `curl -s 127.0.0.1:8141/quit`, then `tools/octo run … --detach` again
   (a restart re-reads the bundle and restamps it).
3. `tools/octo shot 8141 /tmp/now.png` and look at it; read the log for errors.

Keep the app's state in `.local-state/` between runs; delete it to test a
first launch.

## 6. Add capabilities

Add only what a screen uses, in `bundle/manifest.json`:

```json
"capabilities": ["storage", "net"],
"network": { "hosts": ["api.open-meteo.com"] }
```

Every `https://` host your `main.splash` names must be listed (unless you
request `images` or `web`); plain `http://` is never allowed. What each
capability unlocks and what the person sees: [CAPABILITIES](CAPABILITIES.md).
Services such as mail: [HOST-SERVICES](HOST-SERVICES.md).

## 7. Gotchas that cost the most time

Full list in [SCRIPT-API](SCRIPT-API.md#gotchas).

- Hex colors with an `e` next to a digit need `#x`: `#x1e1e2e`. Using `#x` everywhere is safe.
- Iterate with `for i in n` (0..n-1); there is no `range()`.
- In `on_render`, write `if list.len() == 0 { EmptyLabel } for i in list.len() { Row }`,
  **not** `if … {…} else for …`: with `else for`, the empty branch drew nothing and the
  list kept showing stale rows (observed with this template on makepad `d94e5e6`).
- A hidden view does not draw its background; use `SolidView` for a filled panel.
- `ButtonFlat` cannot hold `Label` children; for a tappable row use `GestureView{on_tap: |x, y| …}`.
- Password and one-time-code fields are refused. Secrets belong to a host service's sheet.

## 8. Check it

```sh
tools/octo shot 8141 ~/apps/my-app/bundle/screenshots/01-main.png   # after driving the app to a real state
curl -s 127.0.0.1:8141/quit
tools/octo check ~/apps/my-app/bundle
```

`check` runs `hub stamp` then `hub check --allow-unsigned` and exits nonzero
on a refusal. Verified: without the screenshot, `REFUSED … [refused] listing:
screenshots/01-main.png is named by the listing but is not in the bundle`
(the template names a screenshot on purpose: never add a dummy one); with a
real capture, `my-test-notes 0.1.0 — PASSED` plus the expected unsigned
warning. `octo check` also notes template placeholders left in `listing.json`.

## 9. Run it on an OctoSense phone

What exists today, stated plainly:

- **An arbitrary bundle cannot yet be side-loaded onto a stock OctoSense
  phone.** The phone's store reads the built-in hub
  (`DEFAULT_HUB`, `raw.githubusercontent.com/OctoSense-org/OctoSense-App-Hub/main/`)
  and trusts only the anchor compiled into the build. `OCTOSENSE_HUB` and
  `OCTOSENSE_HUB_ANCHOR` (a mirror directory or URL, and its anchor) are
  environment variables, which the Android launcher does not set; no
  on-device setting for them was found. **Unverified on a device.**
- **Closest real path, verified on the desktop:** publish into a local
  catalog with your own throwaway anchor and install it with the App Hub's
  store, which is the same install code a phone runs:
  [PUBLISHING § 4](PUBLISHING.md#4-rehearse-the-store-path-locally). The
  same local catalog also works in the desktop shell: OctoSense-Desktop reads
  `OCTOSENSE_HUB` and `OCTOSENSE_HUB_ANCHOR`, and its App Hub installs and
  opens your app in the shell's Card runner (verified on macOS, see
  PUBLISHING § 4).
- **First-party apps** reach a phone as system apps: a bundle in
  [OctoSense-System-Apps](https://github.com/OctoSense-org/OctoSense-System-Apps),
  listed in the ROM's `home/system-apps.json` and packed by
  `home/apps/app-hub/build.rs`, then a ROM or Home build. That path is for
  `os.*` apps maintained by OctoSense, not for store apps.
- **After publication** your app appears in every phone's store from the
  signed catalog.

`card-host`'s remote bridge is compiled out on Android, so phone testing is
through the shell's own instrument, not `tools/octo`.

## 10. Publish

Follow [PUBLISHING](PUBLISHING.md) top to bottom: final manifest and listing,
real screenshots, `tools/octo check`, `hub scan`, then the **human** steps
(publisher key, signing, and the submission issue).
`tools/octo package-help` prints the checklist.
