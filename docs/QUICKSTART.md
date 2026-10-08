# Quickstart: build, run and ship an OctoSense script app

English | [简体中文](QUICKSTART.zh-CN.md)

Follow one path from an empty directory to a bundle that the App Hub gate
admits. Every command was run on macOS (Apple silicon) unless it is marked
**unverified**.
Quoted output is real, with local paths and process ids shortened to `…`.

```text
1 prerequisites → 2 build hub + card-host → 3 octo new → 4 octo run → 5 edit loop
→ 6 capabilities → 7 gotchas → 8 octo check → 9 on a phone → 10 publish
```

## 1. Prerequisites

| Platform | State |
| --- | --- |
| macOS on Apple silicon | Verified: every command on this page. |
| Windows | Unverified on current `main` ([App Hub#41](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/41) tracks it), except the `tools/test_*.py` tests that CI runs there. Run `tools/octo` through Python (§2), and keep Git away from the bundle's line endings (§3). |
| Linux | Unverified, except the `tools/test_*.py` tests that CI runs there. Frame capture (`/g`, `tools/octo shot`) is reported to time out under software rendering (llvmpipe, WSL). |

You need:

- **Rust** (stable, via rustup). `cargo` lives in `~/.cargo/bin`; put it on
  `PATH` (`export PATH=$HOME/.cargo/bin:$PATH`).
- **Python 3.9+** for `tools/octo` and `setup-native.py`, with no
  third-party packages. macOS's own `/usr/bin/python3` works.
- **Git.**
- **About 3 GB of disk:** 2 GB for the clones (1.5 GB of it this
  repository, mostly design evidence; `git clone --depth 1` is enough to
  build apps) and 1 GB for the build. Trying the desktop shell
  ([PUBLISHING §4](PUBLISHING.md#4-rehearse-the-store-path-locally)) takes
  about 1 GB more, plus its own build.
- **A graphical session** for `card-host`. It renders a real 412x892-point
  window, even when `--hidden` keeps the window off screen (§4a).
- **The App Hub and its sibling sources** in one workspace directory:

  ```text
  <workspace>/
    OctoScript-App-Design-Flow/   this repository
    OctoSense-App-Hub/            hub, card-host, appstore
    makepad/                      OctoSense-org/makepad
    octoscript-makepad/           OctoSense-org/Octoscript-Makepad
    octoscript/                   OctoSense-org/Octoscript
  ```

  App Hub's `Cargo.toml` patches its Makepad and OctoScript dependencies to
  exactly those sibling paths (`../makepad`, `../octoscript-makepad`,
  `../octoscript`). `setup-native.py` clones the three runtime siblings
  (lowercase directory names, as above) at the revisions
  [native-runtime.lock.json](../native-runtime.lock.json) selects
  ([NATIVE-WORKSPACE](NATIVE-WORKSPACE.md) has its options).

Create the workspace:

```sh
mkdir octosense-ws && cd octosense-ws
git clone https://github.com/OctoSense-org/OctoScript-App-Design-Flow.git
git clone https://github.com/OctoSense-org/OctoSense-App-Hub.git
cd OctoScript-App-Design-Flow
python3 tools/setup-native.py           # makepad, octoscript, octoscript-makepad beside it
python3 tools/setup-native.py --check   # pass: exits 0 and prints the pinned revisions
```

`setup-native.py` takes 20 to 30 seconds. If `--check` fails later, run
`python3 tools/setup-native.py --update` to move clean sibling checkouts to
the locked revisions.

Use `main` of App Hub and of this repository. The runtime is
OctoScript-Makepad `33dea2f1`, which pins Makepad `32d6415f` and OctoScript
`2e37d9e6`.

## 2. Build `hub` and `card-host`

```sh
cd <workspace>/OctoSense-App-Hub
cargo build --release -p octosense-card-host -p octosense-app-hub
```

A successful build ends with `Finished release profile …`. The binaries land
in `target/release/` (or `$CARGO_TARGET_DIR/release/`): `hub` (the gate) and
`card-host` (the host that runs one bundle). On Windows they are `hub.exe` and
`card-host.exe`.

If the build fails with `no variant … TextInputStateQuery`, see [The `card-host` build fails on `TextInputStateQuery`](#the-card-host-build-fails-on-textinputstatequery).

Then, from this repository:

```sh
export OCTOSENSE_APP_HUB=<workspace>/OctoSense-App-Hub   # optional when it is a sibling
tools/octo doctor
```

`doctor` looks for `hub` and `card-host` in `$OCTO_HUB` and `$OCTO_CARD_HOST`,
then `$OCTOSENSE_APP_HUB/target/release`, `$CARGO_TARGET_DIR/release`,
`$OCTOSENSE_APP_HUB/../target/release`, the sibling
`../OctoSense-App-Hub/target/release`, `../target/release`, then `PATH`. It
rejects GitHub's unrelated `hub` CLI. When it finds both, it ends with:

```text
ready: tools/octo new <dir> --platform <target> && tools/octo run <dir>/bundle
```

When something is missing, it prints a `[fail]` line, every place it looked,
and the commands that fix it.

**Windows (unverified).** Windows does not run the script by its shebang, so
run every `tools/octo` command through Python. In each directory above,
`tools/octo` looks for `hub.exe` and `card-host.exe` before the names without
`.exe`:

```powershell
python tools/octo doctor
```

If the binaries live elsewhere, set `$env:OCTO_HUB` and
`$env:OCTO_CARD_HOST` to their full paths. CI tests this search on Windows;
the commands themselves are unverified there. An open issue,
[App Hub#41](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/41),
reports a native Windows 11 build (Rust and MSVC, no WSL) at an earlier
revision: `hub` and `card-host` built, `hub stamp` and `hub check` ran, and
`card-host --remote` served `/g` captures. The maintainers have not verified
it on current `main`.

## 3. Create an app

```sh
tools/octo new ~/apps/my-app --platform macos --id my-notes --name "My Notes"
```

`new` copies [templates/script-app](../templates/script-app/README.md)
(`bundle/`, `AGENTS.md` with its `CLAUDE.md` and `GEMINI.md` shims,
`.gitignore`), sets `id` and `name` in the manifest and the title label in
`main.splash`, writes the `--platform` values into the listing, and stamps
the bundle:

```text
created …/my-app
  id my-notes, name 'My Notes', version 0.1.0, bundle stamped
  target platforms: macos; verify each before publishing
```

`--platform` is required. Give it once for each platform you will run the
app on: `macos`, `windows`, `linux`, `android`, `ios`, `openharmony` or
`web`. A `card-host` run on a Mac tests `macos`. The listing claims these
platforms in the store, so before you publish, keep only the ones you
tested, and have a person confirm the claim. Without the option, `new` stops
with `tools/octo new: error: the following arguments are required: --platform`.

Pick the id with care:

- It is 1 to 64 characters of `[a-z0-9.-]`, does not start with `.` and has
  no `..`. `new` checks this.
- It does not start with `os.`, which is reserved for system apps. `new`
  refuses it unless you pass `--system`.
- Neither the id nor its last segment is a name the host reserves, such as
  `notes`, `weather`, `calculator`, `browser`, `terminal` or `system`. `new`
  refuses such an id before it creates any file:
  `octo: id 'com.example.notes' uses reserved native/host namespace 'notes'; choose an app-specific name`.
  If you change the id later, the gate refuses it (§8). App Hub's
  [rules the gate enforces](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#rules-the-gate-enforces)
  list every reserved name.

Make `~/apps/my-app` its own Git repository, and stop Git from rewriting the
bundle's bytes. The bundle's digest covers every byte, so a checkout that
converts line endings (Git on Windows with `core.autocrlf=true`) breaks it:

```sh
cd ~/apps/my-app
git init
printf 'bundle/** -text\n' >> .gitattributes
git check-attr text -- bundle/manifest.json
```

Success prints `bundle/manifest.json: text: unset`. `>>` appends, so an
existing `.gitattributes` keeps its rules.

If the app sits inside a larger repository, `bundle/**` in the root's
`.gitattributes` does not cover its bundle. Write the bundle's path from the
root, such as `apps/my-app/bundle/** -text`, or `**/bundle/** -text` for a
`bundle/` folder at any depth. Then check the real manifest path from the
root: `git check-attr text -- apps/my-app/bundle/manifest.json`. A check of
`bundle/manifest.json` there proves nothing: `git check-attr` prints `unset`
for any path that matches the pattern, even one that does not exist.

## 4. Run it on the desktop

```sh
tools/octo run ~/apps/my-app/bundle --port 8141            # foreground; Ctrl-C quits
tools/octo run ~/apps/my-app/bundle --port 8141 --detach   # background; returns when admitted and drawn
```

`run` starts `card-host --bundle <bundle> --app-data <app>/.local-state
--allow-unsigned --stamp` with `MAKEPAD_REMOTE=8141`, from the App Hub
directory. `--detach` prints:

```text
[makepad-remote] listening on 127.0.0.1:8141 pid=… app=card-host …
… card-host: my-notes 0.1.0 admitted — capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
ready: first frame drawn
pid …  log …/my-app/.local-state/card-host.log
drive it:  curl -s 127.0.0.1:8141/snap   |   tools/octo shot 8141 <out.png>   |   curl -s 127.0.0.1:8141/quit
```

- `run` first checks that the port is free. If something already answers
  there, it stops with exit status 1 and
  `port 8141 is already taken by card-host pid …`, plus the command that
  quits that instance (`curl -s 127.0.0.1:8141/quit`).
- `--detach` returns once the app's widgets are laid out (`/snap` lists them,
  with text) and one full frame has been drawn after that. A `shot`, click or
  `/t` sent right after it lands on the finished UI.
- `run` passes `--stamp`, so `card-host` rewrites the manifest digest on every
  start and your edits run without a separate `hub stamp`.
  `tools/octo run --no-stamp` leaves the flag out; `card-host` then refuses a
  bundle whose bytes changed. `--no-stamp` is a `tools/octo` flag, not a
  `card-host` one (`card-host --help` lists its own).
- `--system` admits an `os.*` system app under system ceilings.
- The app's files live in its jail, the private data directory
  `<app>/.local-state/<id>/`.
- Look in the log for `admitted`, and for errors after `[SPLASH] eval:`
  (script errors print there; see
  [SCRIPT-API](SCRIPT-API.md#errors-and-the-log)). Search for the error
  forms, not the word "error": Makepad's `[ui-hang]` diagnostics mention
  Metal's `MTLCompilerError` in healthy runs.

  ```sh
  grep -nE '\[E\]|splash:[0-9]+:|refused|on_render closure failed|callback error' <app>/.local-state/card-host.log
  ```

Drive the app over HTTP. Every route is a GET; coordinates are window points,
with y pointing down:

| Command | Does |
| --- | --- |
| `curl -s 127.0.0.1:8141/snap` | Lists widgets with their rects and text: `{"s":[{"i":id,"ty":type,"r":[x,y,w,h],"t":text}]}`; `?q=` filters |
| `curl -s 127.0.0.1:8141/d` | Prints the whole widget tree as text |
| `curl -s "127.0.0.1:8141/click?x=150&y=140&wait=1"` | Sends a real click (`wait=1`: answers after the next frame) |
| `curl -s "127.0.0.1:8141/t?t=Buy%20milk&wait=1"` | Types text into the focused input |
| `curl -s "127.0.0.1:8141/k?k=down&c=ReturnKey"` | Sends a key event |
| `curl -s "127.0.0.1:8141/log?n=50"` | Returns the last log lines |
| `curl -s 127.0.0.1:8141/s` | Returns the bridge's status, including the app's name and pid |
| `tools/octo shot 8141 out.png` | Saves a PNG of the window (`/g?raw=1`) |
| `curl -s 127.0.0.1:8141/quit` | Quits; always end with this (or `/gq`, which captures every window, then quits) |

Driving tips:

- `/t` types into whatever has focus. Clicking a button takes focus away from
  a `TextInput`, so click the input again before the next `/t`. To clear it,
  send `/k?k=down&c=Backspace` once per character.
- `?q=` also matches the `Splash` widget itself, whose text is your whole
  `main.splash`; filter the result by type (`"ty":"Label"`) or read the rects.
- `tools/octo shot` waits for the app's widgets, then grabs until two frames
  in a row are identical (at most `--settle`, 2 s by default), so it never saves a
  half-drawn first frame. Still look at every PNG.
- The window is 412x892 points, and `/g?raw=1` captures at 2x on a Retina
  Mac: divide screenshot pixels by 2 to get click coordinates. The capture
  includes `card-host`'s caption bar at the top (32 points on macOS). The
  caption bar is a widget in the same window, so click coordinates count
  from the same top edge: do not subtract it.

On the template app, `/snap` shows the title label `"t":"My Notes"`. Drive
it through a full cycle:

1. Click the input and send `/t?t=Buy%20milk`.
2. Click **Add**. The app writes `["Buy milk"]` to
   `.local-state/my-notes/notes.json` and draws the row.
3. Click the row. The app removes it.
4. Restart the app. The stored notes reload.

Widgets built by `on_render` appear in `/snap` and `/d` like any other, so
click them by the rects `/snap` gives. What an app builds later, from
`start_timeout` or a network reply, appears once it is drawn: poll
`/snap?q=` for it rather than reading `/snap` once.

### 4a. Headless: test without the screen, several apps at once

Makepad has a hidden-window mode, called headless here. The app still needs
the graphical session from §1, but its window is **never shown or
focused**, and the remote bridge above (`/snap`, `/click`, `/t`, `/g`
screenshots) works exactly the same. Use it for every automated check: a
coding agent then never takes over your screen or keyboard focus, and you can
test several apps, or several copies of one app, side by side.

```sh
tools/octo run ~/apps/my-app/bundle     --port 8161 --hidden --detach
tools/octo run ~/apps/second-app/bundle --port 8162 --hidden --detach
curl -s "127.0.0.1:8161/snap?q=Button"             # each app answers on its own port
curl -s "127.0.0.1:8162/click?x=X&y=Y&wait=1"      # X, Y: center of a rect from /snap
tools/octo shot 8161 first.png && tools/octo shot 8162 second.png
curl -s 127.0.0.1:8161/quit; curl -s 127.0.0.1:8162/quit
```

`--hidden` sets `MAKEPAD_HIDE_WINDOWS=1` for `card-host`; any Makepad app
honors it, including the OctoSense shells. Rules for running several at
once:

- **One port per app.** Give every instance its own `--port`; `run` refuses
  a port that is already taken and names the app holding it.
- **One `--app-data` per copy.** Two different bundles already get separate
  jails (`<app>/.local-state`). Two copies of the *same* bundle need
  `--app-data` to keep their storage and logs apart.
- **Screenshots work hidden.** The app renders them itself, so they are
  complete even though nothing is on screen. Look at each one.

Verified on macOS: two hidden apps, clicked at the same time, each kept its
own state, and both screenshots were correct.

### 4b. Scripted UI tests with `makepad_test`

For repeatable regression tests, the pinned Makepad ships a Rust test
harness, `libs/makepad_test`
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

The example tests a tip-splitting app with a `20%` button and a `tip_line`
label; change the selectors to match your app. Run it with
`cargo test --release --test ui`. Set `MAKEPAD_TEST_PARALLEL=1`
to run the tests (one hidden app each) concurrently, or
`MAKEPAD_TEST_VISIBLE=1` to watch them. Target widgets you declared in the
page (`name := …` for `Selector::id`, or a button's text); widgets built
inside `on_render` are in the harness's snapshot too.

**Unverified on the current pins:** this example passed on macOS, alongside a
second app in parallel, with an earlier App Hub and Makepad. Its API matches
the current Makepad pin.

## 5. The edit loop

1. Edit `bundle/main.splash`. [SCRIPT-API](SCRIPT-API.md) describes the
   language.
2. Run `curl -s 127.0.0.1:8141/quit`, then `tools/octo run … --detach`
   again. The restart re-reads the bundle and restamps it.
3. Run `tools/octo shot 8141 /tmp/now.png` and open the PNG.
4. If the screen is wrong, grep the log (§4) and fix the first error.

`.local-state/` keeps the app's data between runs; delete it to test a first
launch.

## 6. Add capabilities

Add only what a screen uses, in `bundle/manifest.json`:

```json
"capabilities": ["storage", "net"],
"network": { "hosts": ["api.open-meteo.com"] }
```

List in `network.hosts` every `https://` host that your `main.splash` names.
With `images` or `web`, the gate accepts any `https://` host, but at runtime
an unlisted host serves only pictures (`images`) or pages in the web view
(`web`); `net` still reaches only the listed hosts. Plain `http://` is never
allowed. Without
`storage`, the app gets no storage at all: the gate's `grants:` line says
`storage none`. [CAPABILITIES](CAPABILITIES.md) says what each capability
unlocks and what the person sees; [HOST-SERVICES](HOST-SERVICES.md) covers
services such as mail.

**Connected accounts.** To work with a person's GitHub or Google account,
declare `auth` plus the provider family (`github`, `gmail` or `gcalendar`),
and `storage.accounts: true`, as the reference apps do; to identify the
person without reading their data, `auth` alone is enough. The host runs the
sign-in and gives the app a connection handle, never a token. These services
run only in OctoSense desktop `desktop-v0.1.0-beta.2` or later. Sign-in also
needs provider registrations: beta.2 has none built in, so the host's
operator supplies them in `oauth/clients.json`
([CAPABILITIES § Limits](CAPABILITIES.md#limits)). `card-host` answers
`no service answers "…" on this device`.
[examples/connected-apps](../examples/connected-apps/README.md) has worked
examples.

**AI.** In the OctoSense shells a contained app can call `model.complete`,
and the 4 `octos.*` methods once the person allows its agent; in
`card-host` every such call answers `no service answers "…" on this device`.
Build the app to be complete without them. [AI-SERVICES](AI-SERVICES.md)
lists what exists and what is planned, with a verified call that handles
"unavailable".

## 7. Gotchas that cost the most time

### In `main.splash`

[SCRIPT-API](SCRIPT-API.md#gotchas) has the full list.

- Hex colors with an `e` next to a digit need `#x`: `#x1e1e2e`. Using `#x`
  everywhere is safe.
- Iterate with `for i in n` (0..n-1); there is no `range()`.
- In `on_render`, write `if list.len() == 0 { EmptyLabel } for i in list.len() { Row }`,
  **not** `if … {…} else for …`. When this template was tested with
  `else for`, the empty branch drew nothing and stale rows stayed on screen.
- A `View` with `show_bg: true` draws no background in `card-host`, whether
  visible from the start or shown later; use `SolidView` or `RoundedView` for
  a filled panel.
- `ButtonFlat` cannot hold `Label` children; for a tappable row use
  `GestureView{on_tap: |x, y| …}`.
- Password and one-time-code fields are refused. Secrets belong to a host
  service's sheet.

### In the bundle and in Git

- **Reserved ids.** `tools/octo new` checks only the id it creates. If you
  later change the id to `com.example.notes`, the gate refuses it, because
  its last segment, `notes`, is reserved (§3).
- **`.DS_Store`.** Finder writes it into folders you open, and the gate
  refuses any file whose extension it does not know. Delete it before you
  check: `find ~/apps/my-app/bundle -name .DS_Store -delete`.
- **Line endings.** A Git checkout that converts line endings changes the
  bytes and breaks the digest. Commit the `.gitattributes` from §3.
- **Fonts in a card.** Write CJK text with the plain L0 role kit (`Surface`,
  `TextTitle`, `TextBody`, …) and no `font_src`: it draws Chinese with the
  built-in LXGW WenKai, and the gate passes it. A kit's `font_src` may name
  only one built-in font, `makepad_widgets:resources/Inter.ttf`, which has no
  CJK glyphs. A bundled font file in `font_src` also passes the gate, but it
  does not load in `card-host` today, so do not ship one for a card
  ([App Hub#75](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/75)).
- **Fonts in a script app.** Bundle the file, such as `bundle/fonts/X.ttf`,
  and load it in `main.splash` as a member of a `TextStyle`'s `FontFamily`:
  `FontMember{res: http_resource("{{assets}}/fonts/X.ttf")}`. Keep the font's
  license outside `bundle/`: the gate refuses a URL inside a bundled `.txt` or
  `.md` file.
- **Missing glyphs.** Test the app with `MAKEPAD_SYSTEM_FONTS=0`
  (`MAKEPAD_SYSTEM_FONTS=0 tools/octo run …`). Without it, a macOS system font
  fills in the glyphs your fonts lack and hides the problem. **Unverified:**
  that the same text shows boxes on Linux without a CJK system font, and how
  fonts behave in the OctoSense shells.
- **Size.** The bundle must stay within 8 MiB (8,388,608 bytes).

## 8. Check it

```sh
tools/octo shot 8141 ~/apps/my-app/bundle/screenshots/01-main.png   # after driving the app to a real state
curl -s 127.0.0.1:8141/quit
tools/octo check ~/apps/my-app/bundle
```

`check` runs `hub stamp`, then `hub check --allow-unsigned`, and exits
nonzero on a refusal. If you run `check` before the `shot`, as on a fresh
copy of the template, the gate refuses the bundle, because the template's
listing names `screenshots/01-main.png` on purpose:

```text
octo: hub stamp -> 32363ac4…
octo: …/hub check …/my-app/bundle --allow-unsigned
my-notes 0.1.0 — REFUSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  [refused] listing: screenshots/01-main.png is named by the listing but is not in the bundle
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
hub: the bundle was refused
octo: note: listing.json still holds template placeholders (example.com, Replace with, Replace this); the gate accepts them, a reviewer will not.
```

With the capture from the first command, it passes (never substitute a
placeholder image):

```text
my-notes 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
```

The unsigned warning is expected until a person signs the bundle. The
placeholder note stays until a person writes the publisher fields.

To catch a version that is already published, add App Hub's catalog:
`tools/octo check <bundle> --catalog <workspace>/OctoSense-App-Hub/catalog.json`.
A reused version is refused with
`[refused] version: version 0.1.0 of <id> is already published; publish a new version`.

`check` restamps an unsigned bundle first. If you edit the bundle after your
last `check` and commit without running it again, the committed digest is
stale, and a reviewer's plain `hub check` refuses it with `[refused] digest`.
Run `tools/octo check` as the last step before every commit; before you
submit, run plain `hub check` on a fresh clone of your release tag
([SUBMITTING §6](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#6-freeze-and-verify-the-release)).

## 9. Run it on an OctoSense phone

What exists today:

- **An arbitrary bundle cannot be side-loaded onto a stock OctoSense phone.**
  The phone's store reads the built-in hub
  (`DEFAULT_HUB`, `raw.githubusercontent.com/OctoSense-org/OctoSense-App-Hub/main/`)
  and trusts only the trust anchor (App Hub's root public key) compiled into
  the build. `OCTOSENSE_HUB` and
  `OCTOSENSE_HUB_ANCHOR` (a mirror directory or URL, and its anchor) are
  environment variables, which the Android launcher does not set; no
  on-device setting for them was found. **Unverified on a device.**
- **The closest real path is on the desktop:** publish into a local catalog
  with your own throwaway anchor and install it with App Hub's store,
  which runs the same install code as a phone
  ([PUBLISHING §4](PUBLISHING.md#4-rehearse-the-store-path-locally)). The
  OctoSense desktop shell reads `OCTOSENSE_HUB` and `OCTOSENSE_HUB_ANCHOR`
  too; its store installs your app from that catalog and opens it in the
  shell's Card runner.
- **First-party apps** reach a phone as system apps: a bundle in
  [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps),
  listed in the shell's `system-apps.json` (OctoSense `phone/system-apps.json`
  on a phone) and packed by App Hub's `crates/app-hub-app/build.rs`, then a
  Home or ROM build. That path is for `os.*` apps that OctoSense maintains,
  not for store apps.
- **Connected-account apps** (`auth`) cannot be installed on a phone: no
  released phone build accepts the `auth` capability.
- **After publication** your app appears in every phone's store from the
  signed catalog.

`card-host`'s remote bridge is compiled out on Android. On a phone, drive the
app with the App Studio tools of an OctoSense test build
([MODEL-VALIDATION](MODEL-VALIDATION.md#choose-the-test-surface)), not
`tools/octo`.

## 10. Publish

[PUBLISHING](PUBLISHING.md) takes the bundle from here to ready-to-sign:
final manifest and listing, real screenshots, a passing gate, the review
questions, and a local rehearsal of the store path. A person then signs,
tags and submits it, following App Hub's
[Submit an app to the App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md).
`tools/octo package-help` prints the checklist.

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| The build stops in `octosense-appstore` with `no variant … TextInputStateQuery` | See [The `card-host` build fails on `TextInputStateQuery`](#the-card-host-build-fails-on-textinputstatequery). |
| `cargo` not found | `export PATH=$HOME/.cargo/bin:$PATH` (rustup puts it there). |
| The build fails on a `path = "../makepad/..."` dependency | The siblings are missing or at other revisions: run `python3 tools/setup-native.py` from this repository, then `--check`. |
| `doctor`: `[fail] hub` or `card-host` | Build them (§2). If `hub` resolves to GitHub's `hub` CLI, `doctor` says so; set `OCTO_HUB` / `OCTO_CARD_HOST` or `CARGO_TARGET_DIR`. |
| Windows: `tools/octo` does not start | Run it as `python tools/octo …` (§2). |
| Windows: `doctor` cannot find `hub.exe` | Build it (§2). If it lives outside the directories `doctor` lists, set `OCTO_HUB` and `OCTO_CARD_HOST` to the `.exe` paths. |
| `new`: `the following arguments are required: --platform` | Pass `--platform macos`, or each platform you will test on (§3). |
| `new`: `id '…' uses reserved native/host namespace '…'` | Choose an id whose last segment is not reserved (§3). |
| `run`: `port 8141 is already taken by card-host pid …` | An earlier instance still holds the port. Run the `curl -s 127.0.0.1:8141/quit` the message prints, or pick another `--port`. |
| Clicks, typing or edits seem to have no effect | A handler failed (grep the log, §4), or you started the app some other way than `tools/octo run` and are driving an older instance on that port (`curl -s 127.0.0.1:8141/s` shows its pid). |
| `shot` says `still changing after 2s` | The app animates continuously; the PNG is the last frame. Look at it, or pass a longer `--settle`. |
| `shot` or `/g?raw=1` times out on Linux | Frame capture is reported to time out under software rendering (llvmpipe, WSL). Capture on macOS, the verified path. On Linux (**unverified** here), start the app with `MAKEPAD_WRITE_FRAMEBUFFER_PNG=<file>` set (`MAKEPAD_WRITE_FRAMEBUFFER_PNG=<file> tools/octo run …`); Makepad's Linux OpenGL backend then writes every frame it draws to the window into `<file>`, replacing the previous one. Never redraw a screenshot from `/snap`. |
| Under WSL, Chinese typed through an input method never reaches `card-host` | Reported, **unverified**. Test text input on macOS. |
| CJK text in a card shows boxes, or `NO GLYPH` | The kit's `font_src` names `Inter.ttf`, which has no CJK glyphs, or a bundled font, which does not load. Use the plain L0 role kit with no `font_src` (§7). |
| A button shows no label | `ButtonFlat`'s default text is white for a dark theme; set `draw_text +: {color: …}` ([SCRIPT-API § Gotchas](SCRIPT-API.md#gotchas)). |
| A number shows `NaN` | `"".to_f64()` and non-numeric text give NaN, not nil; guard with `if v >= 0` ([SCRIPT-API § Data and strings](SCRIPT-API.md#data-and-strings)). |
| `widget has no uid` / `widget '<id>' not found in tree` after typing | A runtime older than Makepad `d0a9def5`, where a `TextInput`'s `on_change` could not read that same input through `ui`: run `python3 tools/setup-native.py --update` and rebuild `card-host`. |
| `variable net not found in scope` | The manifest lacks `net` or has no `network.hosts` (§6). |
| `this app may not reach <url>` | The host is not in `network.hosts` (exact, lowercase). |
| `no service answers "…" on this device` | Expected in `card-host`, which has no host services; try the app in an OctoSense shell ([HOST-SERVICES](HOST-SERVICES.md)). |
| `check`: `screenshots/01-main.png is named by the listing but is not in the bundle` | Capture a real screenshot (§8); never a placeholder. |
| `check`: `[refused] listing: listing names no platforms` | The listing's `platforms` is empty, as in the raw template. List the platforms you tested in `listing.json`, or create the app with `tools/octo new … --platform …` (§3). |
| `check`: `[refused] identity: app id "…" ends in "…", which is reserved: …` | Change the id's last segment (§3). The same finding repeats under `policy`. |
| `check`: `[refused] contents: .DS_Store has extension "", which a bundle may not hold` | Delete the file: `find <bundle> -name .DS_Store -delete`. Any other file without a known extension must leave `bundle/` too. |
| `check`: `[refused] digest: the bundle hashes to …, the manifest claims …` | The bytes changed after the last stamp. Unsigned: run `tools/octo check` again. Signed: a person stamps and signs again. On a fresh clone only: the checkout converted line endings (commit the `.gitattributes` from §3), or the commit holds a stale digest (§8). |
| `check`: `[refused] assets: … contains https://…` in a `.txt` or `.md` file | Bundled text may not hold URLs; remove them, or keep the file outside `bundle/`. |
| `check`: `[refused] resource-invalid (…/font_src): not a portable bundle path: "makepad_widgets:resources/…"` | A kit's `font_src` may name only the built-in `Inter.ttf`. For CJK text, use the plain L0 role kit with no `font_src`; a bundled font file passes the gate but does not load in a card (§7). |
| `hub: the bundle exceeds the size limit`, with no report | The bundle is over 8 MiB. Shrink or drop images and fonts. |
| `check` or `hub scan` on a signed bundle: `publisher key "…" is not registered with this hub` | Pass the publisher's public key: `tools/octo check <bundle> --publisher-key <publisher-id>=<hex public key>` (the same flag works for `hub scan`). |
| `card-host: refused: no signature verifier is installed` | `card-host` does not run signed bundles; test the unsigned copy and sign last. |
| `hub scan … --packet build/review.json` prints `hub: build/review.json: No such file or directory (os error 2)` | `hub` does not create the packet's directory. Run `mkdir -p build` first. |
| `hub check --help` prints `hub: No such file or directory (os error 2)` | Your `hub` predates App Hub's current `main`, where `--help` prints the usage. Rebuild it (§2), or run `hub` with no arguments. |
| Any other gate refusal | App Hub's [Common refusals and how to fix them](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#common-refusals-and-how-to-fix-them). |

### The `card-host` build fails on `TextInputStateQuery`

`cargo build --release -p octosense-card-host -p octosense-app-hub` stops
with:

```text
error[E0599]: no variant, associated function, or constant named `TextInputStateQuery` found for enum `makepad_widgets::Event` in the current scope
   --> crates/appstore/src/services.rs:393:18
error: could not compile `octosense-appstore` (lib) due to 1 previous error
```

The same error stops the `appstore` build in
[PUBLISHING §4](PUBLISHING.md#4-rehearse-the-store-path-locally). `hub` does
not use Makepad and still builds on its own:
`cargo build --release -p octosense-app-hub`.

Update App Hub and build again with exactly the two packages from §2:

```sh
cd <workspace>/OctoSense-App-Hub
git pull
cargo build --release -p octosense-card-host -p octosense-app-hub
```

App Hub `main` builds `card-host` with the `appstore` feature
`text-input-state-query` turned off, so it builds against plain Makepad. The error
remains if your App Hub checkout predates that change, or if you build any
other App Hub package or the whole workspace: those keep the feature on and
need OctoSense's patched Makepad. The `octosense-appstore-app` build in
[PUBLISHING §4](PUBLISHING.md#4-rehearse-the-store-path-locally) is one of
those packages; build it as that section describes.
