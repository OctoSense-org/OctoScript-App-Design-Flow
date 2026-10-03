# Quickstart: build, run and ship an OctoSense script app

One path, from nothing to a bundle the App Hub gate admits. Every command was
run on macOS (Apple silicon) unless marked **unverified**: first on 2026-09-25,
then again end to end from fresh clones of `main` twice on 2026-09-26 (each
time a new app built from this page and [SCRIPT-API](SCRIPT-API.md) alone,
through `tools/octo check`, `hub scan`, a local publish and an install in
the desktop shell). The second run used this repository at `7a61293b`, App Hub
`3e993d4` and OctoSense-Desktop `cae5cfb` (the repository is now
[OctoSense](https://github.com/OctoSense-org/OctoSense)).

```text
1 prerequisites → 2 build hub + card-host → 3 octo new → 4 octo run → 5 edit loop
→ 6 capabilities → 7 test and capture → 8 octo check → 9 on a phone → 10 publish
```

## 1. Prerequisites

- **Rust** (stable, via rustup). `cargo` lives in `~/.cargo/bin`; put it on
  `PATH` (`export PATH=$HOME/.cargo/bin:$PATH`).
- **Python 3.9+** for `tools/octo` and `setup-native.py` (no packages
  needed; macOS's own `/usr/bin/python3` 3.9.6 ran every step).
- **Disk:** about 3 GB (the workspace about 1.9 GB, the release build about
  1 GB; to also try the desktop shell, add about 1 GB for the OctoSense
  clone and its own framework sources, plus its build).
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
  is about 1.3 GB on disk, mostly design evidence; `--depth 1` is fine for
  building apps), `setup-native.py` 20 to 30 seconds.

  Use `main` of App Hub and of this repository. The runtime is Octoscript-Makepad
  `2cc5ef37`, which pins makepad `c155f61d` and octoscript `5991dfae`; this
  guide was last verified against App Hub `46d67e51`.

## 2. Build `hub` and `card-host`

```sh
cd <workspace>/OctoSense-App-Hub
cargo build --release -p octosense-card-host -p octosense-app-hub
```

Verified: `Finished release profile … in 46.00s` from a cold target on a
16-core Apple silicon Mac (1m 43s on an earlier run with dependencies cached;
a laptop takes longer). The binaries land in `target/release/` (or
`$CARGO_TARGET_DIR/release/`).

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
tools/octo run ~/apps/my-app/bundle --port 8141 --detach   # background; returns when admitted and drawn
```

This is `card-host --bundle <bundle> --app-data <app>/.local-state
--allow-unsigned --stamp` with `MAKEPAD_REMOTE=8141`, started from the App Hub
directory. Verified `--detach` output:

```text
[makepad-remote] listening on 127.0.0.1:8141 pid=18656 app=card-host grabs=/var/folders/…
[I] crates/card-host/src/main.rs:189:9 - card-host: my-test-notes 0.1.0 admitted — capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
ready: first frame drawn
pid 18656  log …/my-app/.local-state/card-host.log
```

- `run` (with or without `--detach`) first checks that the port is free. If something already answers
  there it stops with `port 8141 is already taken by card-host pid …`, the
  command to quit that instance (`curl -s 127.0.0.1:8141/quit`) and exit
  status 1, instead of starting a second app without a bridge. After launch
  `--detach` also requires the `[makepad-remote] listening on 127.0.0.1:8141` line
  with the new pid, and stops the new `card-host` if it is missing.
- `--detach` returns only when the app's widgets are laid out (`/snap` lists them,
  with text) and a full frame has been drawn after that, usually 0.3–0.6 s
  after start. A `shot`, click or `/t` sent right after it lands on the
  finished UI.

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
- You can drive the app the moment `run --detach` returns: it waits until the
  UI is laid out and drawn. `tools/octo shot` also waits for the app's widgets
  and then grabs until two frames in a row are identical (at most `--settle`,
  2 s), so it never saves a half-drawn first frame. Still look at every PNG.
- `/quit` the running app before the next `run` on the same port.
  `run` refuses a port that is still taken (exit 1, naming the app and pid
  that hold it), so you cannot end up driving an old instance by accident.
- The window is 412x892 points and `/g?raw=1` is at 2x on a Retina Mac:
  divide screenshot pixels by 2 to get click coordinates. The capture
  includes `card-host`'s 32-point caption bar at the top.

Verified: `/snap` showed the title label `"t":"Test Notes"`; clicking the
input, `/t?t=Buy%20milk`, then clicking **Add** wrote `["Buy milk"]` to
`.local-state/my-test-notes/notes.json` and drew the row; tapping the row
removed it; a restart reloaded stored notes. Widgets built by `on_render` are
in `/snap` and `/d` like any other, so click them by the rects `/snap` gives
(verified on makepad `d0a9def5` with the unit converter's mode buttons and
history rows). What an app builds later, from `start_timeout` or a network
reply, appears once it is drawn: poll `/snap?q=` for it rather than reading
`/snap` once.

### 4a. Headless: test without the screen, several apps at once

Makepad has a headless mode: the app runs with its window **never shown or
focused**, and the remote bridge above (`/snap`, `/click`, `/t`, `/g`
screenshots) works exactly the same. Use it for every automated check, so a
coding agent never takes over your screen or keyboard focus, and so several
apps (or several copies of one app) can be tested side by side without
competing for the display.

```sh
tools/octo run apps/tip-split/bundle      --port 8161 --hidden --detach
tools/octo run apps/unit-converter/bundle --port 8162 --hidden --detach
curl -s "127.0.0.1:8161/snap?q=Button"                 # each app answers on its own port
curl -s "127.0.0.1:8162/click?x=X&y=Y&wait=1"      # X, Y: centre of a rect from /snap
tools/octo shot 8161 tip.png && tools/octo shot 8162 conv.png
curl -s 127.0.0.1:8161/quit; curl -s 127.0.0.1:8162/quit
```

`--hidden` sets `MAKEPAD_HIDE_WINDOWS=1` for `card-host` (any Makepad app
honours it, including the OctoSense shells). Rules for running several at
once:

- **One port per app.** Give every instance its own `--port`; `run` refuses
  a port that is already taken and names the app holding it.
- **One `--app-data` per copy.** Two different bundles already get separate
  jails (`<app>/.local-state`). Two copies of the *same* bundle need
  `--app-data` to keep their storage and logs apart.
- Screenshots are rendered by the app itself, so they are complete even
  though nothing is on screen. Look at them.

Verified 2026-09-27 on macOS (Apple silicon): two apps ran hidden at the same
time; clicks sent to both at once changed each app's own state ("Tip 20%" in
one, "Celsius to Fahrenheit" in the other) and both screenshots were correct.

**Scripted UI tests: `makepad_test`.** For repeatable regression tests, the
pinned makepad ships a Rust test harness, `libs/makepad_test`
([README](https://github.com/OctoSense-org/makepad/blob/main/libs/makepad_test/README.md),
[GUIDE](https://github.com/OctoSense-org/makepad/blob/main/libs/makepad_test/GUIDE.md)).
It builds and launches the app itself, hidden by default, drives it through
the same bridge, and on failure saves a screenshot, the widget tree and the
log. To test a bundle, point it at App Hub's `card-host` and pass the bundle
as app arguments:

```rust
// tests/ui.rs in a small crate with
// [dev-dependencies] makepad-test = { path = "../makepad/libs/makepad_test" }
use makepad_test::{run_with_config, Selector, TestApp, TestConfig};

fn app(test: &str, bundle: &str) -> TestConfig {
    let card_host = "../OctoSense-App-Hub/crates/card-host";
    let mut c = TestConfig::new(card_host, "octosense-card-host", test).unwrap();
    c.bin_name = Some("card-host".into());
    c.app_args = vec!["--bundle".into(), format!("{bundle}/bundle"),
        "--app-data".into(), format!("{bundle}/.test-state"),
        "--allow-unsigned".into(), "--stamp".into()];
    c
}

#[test]
fn tip_20_percent() {
    run_with_config(app("tip", "/abs/path/apps/tip-split"), |app: TestApp| {
        app.locator(Selector::widget_type("Button").text_exact("20%")).wait_visible().click();
        app.locator(Selector::id("tip_line")).wait_text("Tip 20%: 0.00");
    }).unwrap();
}
```

Run with `cargo test --release --test ui`; set `MAKEPAD_TEST_PARALLEL=1` to
run the tests (one hidden app each) concurrently, or `MAKEPAD_TEST_VISIBLE=1`
to watch them. Target widgets you declared in the page (`name := …` for
`Selector::id`, or a button's text); widgets built inside `on_render` are in
the harness's snapshot too. Verified with the example above (and a second app
in parallel) against makepad `cd812acd` and App Hub `3e993d4c`, and on makepad
`d0a9def5` with App Hub `46d67e51` by a test that clicks the unit converter's
`on_render` mode button `kg → lb` by its text.

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

**AI.** In the OctoSense shells a contained app can call `model.complete`,
and the four `octos.*` capabilities once the person allows its agent; in
`card-host` every such call answers `no service answers "…" on this device`.
Build the app to be complete without it; what exists, a verified call that
handles "unavailable", and the plan: [AI-SERVICES](AI-SERVICES.md).

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
  same local catalog also works in the OctoSense desktop shell, which reads
  `OCTOSENSE_HUB` and `OCTOSENSE_HUB_ANCHOR`, and its App Hub installs and
  opens your app in the shell's Card runner (verified on macOS, see
  PUBLISHING § 4).
- **First-party apps** reach a phone as system apps: a bundle in
  [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps),
  listed in the shell's `system-apps.json` (OctoSense `phone/system-apps.json`
  on a phone) and packed by App Hub's `crates/app-hub-app/build.rs`, then a
  Home or ROM build. That path is for
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

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `doctor`: `[fail] hub` or `card-host` | Build them (§2). If `hub` resolves to GitHub's `hub` CLI, `doctor` says so; set `OCTO_HUB` / `OCTO_CARD_HOST` or `CARGO_TARGET_DIR`. |
| `cargo` not found | `export PATH=$HOME/.cargo/bin:$PATH` (rustup puts it there). |
| Build fails on a `path = "../makepad/..."` dependency | The siblings are missing or at other revisions: run `python3 tools/setup-native.py` from this repository, then `--check`. |
| `run`: `port 8141 is already taken by card-host pid …` | An earlier instance still holds the port. `curl -s 127.0.0.1:8141/quit` (the message prints it), or pick another `--port`. |
| Clicks, typing or edits seem to have no effect | A handler failed (grep the log, §4), or you started the app some other way than `tools/octo run` and are driving an older instance on that port (`curl -s 127.0.0.1:8141/s` shows its pid). |
| `shot` says `still changing after 2s` | The app animates continuously; the PNG is the last frame. Look at it, or pass a longer `--settle`. |
| A button shows no label | `ButtonFlat`'s default text is white for a dark theme; set `draw_text +: {color: …}` ([SCRIPT-API § Gotchas](SCRIPT-API.md#gotchas)). |
| A number shows `NaN` | `"".to_f64()` and non-numeric text give NaN, not nil; guard with `if v >= 0` ([SCRIPT-API § Data and strings](SCRIPT-API.md#data-and-strings)). |
| `widget has no uid` / `widget '<id>' not found in tree` after typing | A runtime older than makepad `d0a9def5`, where a `TextInput`'s `on_change` could not read that same input through `ui` ([OctoScript-Makepad#44](https://github.com/OctoSense-org/OctoScript-Makepad/issues/44), fixed): run `python3 tools/setup-native.py --update` and rebuild `card-host`. |
| `variable net not found in scope` | The manifest lacks `net` or has no `network.hosts` (§6). |
| `this app may not reach <url>` | The host is not in `network.hosts` (exact, lowercase). |
| `no service answers "mail" on this device` | Expected in `card-host`, which has no host services; try it in a shell ([HOST-SERVICES](HOST-SERVICES.md)). |
| `check`: `screenshots/01-main.png is named by the listing but is not in the bundle` | Capture a real screenshot (§8); never a placeholder. |
| `check`: `[refused] digest` | The bundle changed after stamping: `tools/octo check` restamps an unsigned bundle; after signing, stamp and sign again. |
| `card-host: refused: no signature verifier is installed` | `card-host` does not run signed bundles; test the unsigned copy. |
