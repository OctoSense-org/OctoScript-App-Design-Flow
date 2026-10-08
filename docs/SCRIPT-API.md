# Script API for contained apps

What a script app's `main.splash` can use when it runs in a policed isolate:
App Hub's `card-host` and the shells' Card runner. Everything here was read in
the source of the runtime this repository pins (OctoSense-org/makepad
`32d6415f`) and of App Hub. Behavior marked **✓ run** was observed in
`card-host` on macOS. Idioms come from the system apps (OctoSense
`apps/<name>/bundle/main.splash`), which are working code.

If something is not on this page, check the runtime source before using it.
If it is not there either, it does not exist for apps.

Paths below: `MP` is the makepad checkout, `HUB` is OctoSense-App-Hub `crates/`.

## Shape of a program

```splash
let notes = []                       // state: top-level let, persists for the session

fn load(){                           // functions may use ui.* (they run after the body)
    if fs.exists("notes.json") {
        let v = fs.read("notes.json").parse_json()
        if v != nil { notes = v }
    }
    ui.list.render()
}

start_timeout(0.05, || load())       // ui is injected AFTER the body evaluates

SolidView{width: Fill height: Fill flow: Down padding: 16 draw_bg.color: #xffffff
    list := ScrollYView{width: Fill height: Fill flow: Down on_render: || {
        if notes.len() == 0 { Label{text: "No notes yet." draw_text.color: #x8e8e93} }
        for i in notes.len() { Label{text: notes[i] draw_text.color: #x1c1c1e} }
    }}
}
```

- Declarations (`let`, `fn`) first, then one root widget. The host prepends
  `use mod.prelude.widgets.*`, `let fs = mod.fs`, `let host = mod.host` (and
  `use mod.net` when the app may use the network), then continues an open
  `View{height: Fit, …}` with your body (`MP/widgets/src/splash.rs`).
- `ui` is injected after the body is evaluated (`splash.rs`). It works
  inside every `fn` and handler, but not in top-level statements during the
  first evaluation. Start work with `start_timeout(0.05, || boot())`, as every
  system app does (**✓ run**).
- `name := Widget{…}` makes a widget addressable as `ui.name`. A `:=` id is a
  field of its direct parent only; name every wrapper you need to reach through.
- `{{assets}}` in the source is replaced by the loopback origin serving the
  bundle (`HUB/app-contract/src/entry.rs`), and that origin is on the app's host
  list: `Image{src: http_resource("{{assets}}/thumbs/a.jpg")}`, or
  `let assets = "{{assets}}"` then `http_resource(assets + "/" + name)`
  (Photos).

## `ui.<id>`: reading and changing widgets

Lookup searches the handler's subtree, then the whole app; `ui.root` is the
root. A miss is an error `widget '<id>' not found in tree`; an unknown method
is `widget method <m> not found for uid <uid>` (`MP/widgets/src/widget_async.rs`).

| Call | On | Notes |
| --- | --- | --- |
| `ui.x.text()` / `ui.x.set_text(s)` | any widget (`widget.rs`); Label, LinkLabel, TextInput, buttons | `set_text` converts numbers and booleans: `set_text(42)` shows `42` (**✓ run**) |
| `ui.x.set_visible(b)` / `ui.x.visible()` | any widget (`widget.rs`) | Views take a bool only (`view.rs`) (**✓ run**) |
| `ui.x.render()` | View, SolidView, RoundedView, ScrollYView, ScrollXView | re-runs the view's `on_render` (**✓ run**) |
| `ui.x.set_src(http_resource(url))` / `set_src(nil)` | Image (`image.rs`) | the URL must pass the media rule (see Network) |
| `ui.x.load_image_from_data_async(bytes)` | Image (`image.rs`) | for example `fs.read_bytes("DCIM/IMG_1.jpg")` (Camera) |
| `ui.x.value()` / `set_value(n)` | Slider (`slider.rs`) | no script callback |
| `ui.x.checked()` | CheckBox (`check_box.rs`) | no setter |
| `ui.x.on_click()` | Button family (`button.rs`) | fires the handler |
| `open() close() toggle() is_open()` | SlidePanel (`slide_panel.rs`) | – |

## Events

| Handler | Widget | Arguments | Example |
| --- | --- | --- | --- |
| `on_click: \|\| …` | Button, ButtonFlat, ButtonFlatter | none | `ButtonFlat{text: "Add" on_click: \|\| add()}` (**✓ run**) |
| `on_click: \|active\| …` | CheckBox | `active` | |
| `on_change: \|text\| …` | TextInput | current text | News search. `text` is the new text; `ui.<its id>.text()` returns the same (**✓ run**) |
| `on_return: \|text\| …` | TextInput | current text | Maps search |
| `on_tap: \|x, y\| …` | GestureView | point in the view | `GestureView{on_tap: \|x, y\| remove(i) …}` (**✓ run**) |
| `on_double_tap: \|x, y\|`, `on_long_press: \|x, y\|` | GestureView | | News long-press |
| `on_swipe: \|dx, dy\|` | GestureView | one axis is 0 | Photos |
| `on_pan: \|dx, dy, phase\|` | GestureView | phase 0 begin, 1 move, 2 end | |
| `on_pinch: \|scale, x, y, phase\|` | GestureView | | Photos |
| `on_detent: \|d\|` | SheetView | 0 peek, 1 half, 2 full | |
| `on_render: \|\| { children }` | View family | none; the closure's widgets become the children | the template's list (**✓ run**) |
| `on_capture`, `on_error`, `on_zoom: \|z\|` | CameraPreview | | Camera |
| `on_error` | WebReader | none | News |

GestureView thresholds: tap slop 10 points, swipe at least 60 points within
0.45 s, double tap within 0.3 s (`gesture_view.rs`).

## Timers and time

These timer functions are global (`MP/platform/src/script/timer.rs`):

| Call | Returns |
| --- | --- |
| `start_timeout(secs, fn)` | timer id (**✓ run**) |
| `start_interval(secs, fn)` | timer id |
| `stop_timer(id)` | – |
| `time_now()` | Unix seconds, as a float (**✓ run**) |
| `local_time(epoch?)` | `{year month day hour minute second weekday}` (weekday 0 = Sunday). `card-host` sets no UTC offset, so it is **UTC** there (**✓ run**) |
| `random()` / `random_u32()` / `random_seed()` | 0..1 / u32 / reseed (**✓ run**) |

```splash
let rec_timer = nil
fn start_rec(){ rec_timer = start_interval(0.5, || tick_rec()) }
fn stop_rec(){ stop_timer(rec_timer) }
```

A body containing `fn tick(` gets an implicit 1 Hz interval calling `tick`
(`splash.rs`). Name your function something else unless you want that.

Math functions are global too: `floor ceil round abs min max clamp pow sqrt sin cos …`
(`floor(2.7)` = 2, **✓ run**).

## Storage: `fs.*`

The app's jail (`<app-data>/<id>/`; in `card-host` `<app>/.local-state/<id>/`).
Paths are relative to it; a leading `/` means the jail root; `..` above the
root is an error; symlinks are refused (`MP/widgets/src/splash_storage.rs`).
Only an app granted `storage` has a jail. Without it every call below errors
with `storage not available in this context` (see
[CAPABILITIES](CAPABILITIES.md)).

| Call | Returns | Verified |
| --- | --- | --- |
| `fs.read(path)` | string | **✓ run** |
| `fs.read_bytes(path)` | u8 array | |
| `fs.write(path, text)` | nil | **✓ run** |
| `fs.append(path, text)` | nil | **✓ run** |
| `fs.exists(path)` | bool | **✓ run** |
| `fs.list(dir)` | sorted names, directories end in `/` (`["b/"]`) | **✓ run** |
| `fs.mkdir(path)` | nil, recursive | **✓ run** |
| `fs.remove(path)` | nil; a file or an empty directory | **✓ run** |

No rename, stat or binary write. Limits: 1 MiB per file, the manifest's
`storage.max_bytes` for the whole jail (ceiling 16 MiB installed, 64 MiB
system), 256 entries, depth 16, 128-byte names.

A failed call logs an error and stops the handler: the statements after it
do not run (**✓ run**: `[E] splash:…:6:21 - file not found`). Check with
`fs.exists` before you read. The messages include `file not found`,
`path escapes the app's storage`, `file too large`, `app storage is full`,
`too many files`, `data must be a string`, `not a directory`.

## Network

`net` exists only when the app has `net` **and** at least one host in
`network.hosts`; otherwise it is not defined at all
(`variable net not found in scope …`, **✓ run**).

```splash
fn fetch(url){
    let p = promise()
    net.http_request(net.HttpRequest{url: url method: net.HttpMethod.GET headers: {"User-Agent": "MyApp/1.0"}}) do net.HttpEvents{
        on_response: |res| p.resolve(res)
        on_error: |_err| p.resolve(nil)
    }
    p
}
fn refresh(){
    let res = fetch("https://api.example.com/today").await()
    if res == nil || res.status_code >= 400 { ui.status.set_text("Offline") return }
    let data = res.body.to_string().parse_json()
    …
}
```

- Request: `net.HttpRequest{url method headers body …}`; methods
  `net.HttpMethod.GET HEAD POST PUT DELETE PATCH …`
  (`MP/platform/network/src/types.rs`).
- Events: `net.HttpEvents{on_response on_error on_stream on_complete}`;
  `res.status_code`, `res.headers`, `res.body` (bytes; `.to_string()`);
  `err.message`. Default response cap 16 MiB (`MP/platform/script/std/src/net.rs`).
- `promise()`, `p.resolve(v)`, `p.await()` (News).
- A URL outside the rules is refused **without** calling `on_error`: the call
  logs `this app may not reach <url>` and the rest of the handler does not
  run (**✓ run**).
- `Image{src: http_resource(url)}` loads a picture; refused:
  `this app may not load <url>` and the log line
  `Script resource refused by the host's allowlist: <url>`.

The rules (`MP/widgets/src/splash_policy.rs`): requests reach exactly the hosts
in `network.hosts` (lowercase, exact, no wildcard). Pictures (`http_resource`)
may also come from any public `https://` host when the app has `images`; web
pages (WebReader) when it has `web`. Private, internal and non-https addresses
are refused (`only https:// URLs are allowed`, `host not permitted (private/internal): <h>`).
The gate additionally refuses a bundle whose source names an undeclared https
host ([PUBLISHING §2](PUBLISHING.md#2-the-rules-the-gate-enforces)).

`net.web_socket` is held to the host list like `net.http_request`
(`this app may not reach <url>`). `net.socket_stream` and `net.http_server`
are refused in a store app, whatever it was granted (`this app may not open a
raw socket`, `this app may not open a listening server`; `MP/platform/script/std/src/net.rs`).

## Host services: `host.request`

```splash
host.request("mail.list", {account: account.id folder: folder.id offset: 0 limit: 100}, fn(r){
    if r.is_ok { messages = r.data.messages ui.inbox.render() }
    else { ui.status.set_text(r.error) }
})
```

- `host.request(service, args, fn(r))` returns a request id. `r.is_ok`
  (bool; `ok` is a keyword), `r.data` (parsed JSON or nil), `r.error`
  (string or nil) (`MP/widgets/src/splash_host.rs`).
- Service `a.b` needs capability `a` (or exactly `a.b`). Without it the
  callback runs immediately with `is_ok` false and
  `r.error` = `this app was not granted "mail", which "mail.accounts" needs`;
  the log shows `splash host: refused "mail.accounts": this app was not granted "mail", which "mail.accounts" needs` (**✓ run**).
- No service for the family on this host: the callback gets
  `no service answers "<family>" on this device` at once. `card-host` has no
  services, so every call there answers this (**✓ run**).
- Every request answers once (`HUB/appstore/src/services.rs`):

  | Situation | `r.error` |
  | --- | --- |
  | The call waits longer than its service allows: 60 s unless the service asks for more; the clock stops while the service's sheet is up | `the host service timed out` |
  | The app already has 32 calls waiting | `too many host requests are waiting; try again when some have answered` |
  | The call comes from a Glance card or an agent's tool, and the service needs its sheet | The service's own sentence, such as `this surface cannot raise a prompt; open the app to continue` |

  The limits in full: App Hub
  [PUBLISHING § Host services and sheets](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#host-services-and-sheets).
- `host.capabilities()` returns the granted list, such as `["storage"]` (**✓ run**);
  `host.has("net")` returns a bool (**✓ run**). `host.has` says only that the
  capability was granted, not that any service answers it. There is no
  `host.prompt`.
- Which shell serves which service, sheets and the Mail methods:
  [HOST-SERVICES](HOST-SERVICES.md).

## Data and strings

| Kind | Available | Notes |
| --- | --- | --- |
| JSON | `s.parse_json()`, `v.to_json()` | `parse_json` never raises. Invalid JSON does **not** reliably give nil (`"{nope".parse_json() == nil` was false, **✓ run**): check the fields you need. `to_json` stops at depth 24. |
| Feeds | `s.parse_feed(style)` | → `[{title link source published summary image}]` or nil (`mod_feed.rs`); News |
| Strings | `len trim split(p) search(p) replace(p, r) strip_prefix strip_suffix url_encode url_decode to_f64 match_str match_all` | `to_f64` gives NaN (not nil) for `""`, non-numbers and untrimmed text (`" 12.5 "`); NaN compares false with everything, so guard with `if v >= 0` (**✓ run**). `search` → index or -1. `"a-b-c".replace("-", "+")` = `a+b-c`: **first occurrence only** (**✓ run**); replace all with `regex("-", "g")`. |
| Regex | `regex(pattern, flags)` with `.test(s)`, `.exec(s)` | case-insensitive contains: `regex("word", "i").test(s)` (News) |
| Missing | `to_lower to_upper contains starts_with ends_with` | use `search(p) == 0`, `search(p) >= 0`, or a regex |
| Arrays | `push pop clear len remove(i) retain(fn)` | no `sort map filter join insert index_of slice` |
| Objects | `o.k`, `o[k]`, `delete`, `extend`, `o += {k: v}` | |
| Numbers → text | `"" + n` | |
| Loops | `for i in n` (0..n-1), `for v in array`, `for i v in array`, `for k v in object`, `a..b` ranges, `loop {}`, `while` | there is **no `range()`** (**✓ run**: `for i in 3` sums to 3; `for k v in {a:1 b:2}` gives `ab`) |

## Widgets available to an app

Every name in the widgets prelude resolves in the isolate
(`MP/widgets/src/lib.rs`). None is gated to exist; checks apply when a
widget acts.

| Widget | Use | Needs |
| --- | --- | --- |
| `View`, `SolidView`, `RoundedView` | containers; `SolidView`/`RoundedView` for a filled background | – |
| `ScrollYView`, `ScrollXView`, `ScrollXYView` | scrolling containers, often with `on_render` | – |
| `Label`, `LinkLabel` | text (default text color is white: set `draw_text.color`) | – |
| `TextInput` | text entry; give it a numeric `height`, because a `Fill` height inside a `Fit` parent collapses to zero | password and one-time-code fields are refused (see Gotchas) |
| `Button`, `ButtonFlat`, `ButtonFlatter` | buttons with `text:` and `on_click` | – |
| `Image` | `src: http_resource(url)`, `fit: ImageFit.CropToFill` | media rule (see Network) |
| `Html`, `Markdown` | rich text | – |
| `GestureView`, `SheetView` | taps, swipes, pinches; bottom sheet with detents | – |
| `Hr`, `Vr`, `Icon`, `LoadingSpinner`, `Slider`, `CheckBox`, `Toggle`, `RadioButton`, `DropDown` | controls | – |
| `HostedView` | `full:` / `tile:` faces for the home screen (News, Photos) | – |
| `WebReader` | `open(url)→bool close() is_open() error() url()` | a URL on the host list, or any public https page with `web`; refused: `refused <url>: not on this app's host list, and no \`web\` grant` |
| `CameraPreview` | `start() stop() switch() capture() record_start() record_stop() set_zoom(n) set_flash(s) focus(x,y) last() error() …`; captures land in the jail at `DCIM/` | `camera`; refused: `this app was not granted the camera`. `microphone` adds sound, `library` copies to the photo library |
| `MapView` | map with `set_nav_polyline` etc. (Maps) | tile hosts must be declared; follow camera needs `location` |
| `glass.*` | Liquid-glass kit (`glass.Card`, `glass.GlassButton`, …) | – |

Registration lines are in the source (`view_ui.rs`, `label.rs`, `button.rs`,
`image.rs`, `gesture_view.rs`, `web_reader.rs`, `camera_preview.rs`,
`map/view.rs`, `glass_panel.rs`, …). `MapView` needs the host built with the
`maps` feature (`card-host` is).

`card-host` registers `sys.*` (weather, stock, geocode, route, gps, …) with
`register_agent_module`. Unverified: the OctoSense shells. Every fetch it
makes is held to `network.hosts`, `sys.gps` reads "no fix" without
`location`, and profile-backed helpers (`link`, `prefs`, watchlists) return
empty because no app can hold `profile`. Prefer `net.http_request` to hosts
you declare.

## Limits and what you see when you hit them

| Limit | Value | Message |
| --- | --- | --- |
| One handler, timer, callback or the body | 200,000 instructions and 64 ms | `script instruction limit exceeded` (**✓ run**: an endless `loop` in a timer; the app kept running) / `script time budget exceeded` |
| Cumulative instructions per session | manifest `compute.instruction_budget`, ceiling 20,000,000 (system 4,000,000,000); charged for the body, host callbacks and `tick` | `splash: <label> is stopped: its instruction budget is spent`; afterwards requests, network and media are refused |
| Heap | `compute.memory_bytes`, ceiling 64 MiB (system 128 MiB) | `script heap allocation limit exceeded while <op>: requested <n> bytes, <m> remaining` |
| Storage | see Storage | `app storage is full`, `file too large`, `too many files` |
| HTTP response | 16 MiB by default (`MP/platform/script/std/src/net.rs`) | – |

## Gotchas

- **Comments depend on the language:** native Splash uses `//` and `/* … */`.
  `#` starts color tokenization; it is not a prose-comment prefix. Copying
  `.card`-style `#` comments into a Splash function can interrupt initialization
  after some fields have already been filled.
- **Container boundaries:** `View{width: Fill height: Fit}` is already closed.
  Indented widgets on following lines do not become its children. Keep the
  container open through its intended children, and check for an extra closing
  brace left after a layout edit. Open success alone does not prove a complete
  root or startup callback; follow the [validation loop](MODEL-VALIDATION.md#run-a-complete-review-loop).
- **Hex colors:** write `#x` before any hex color with an `e` next to a digit
  (`#x1e1e2e`, `#x2ecc71`); `#x` is always safe. Otherwise the tokenizer reads
  an exponent.
- **`on_render` empty state:** write `if list.len() == 0 { Empty } for i in list.len() { Row }`.
  Do not write `if … {…} else for …`: the empty branch draws nothing and stale
  rows stay on screen (**✓ run**).
- **Backgrounds:** `View{show_bg: true draw_bg.color: …}` draws no background
  in `card-host`, whether always visible or shown later with
  `set_visible(true)` (**✓ run**); `SolidView{draw_bg.color: …}` does. Use
  `SolidView` or `RoundedView` for filled panels.
- **Default button look:** a `ButtonFlat` with only `text:` draws white text
  on a light outline, invisible on a white app (**✓ run**). Style it as the
  template does (`draw_bg +: {color: … color_hover: … color_down: …}` and
  `draw_text +: {color: … color_hover: … color_down: …}`). To reuse a style,
  bind it once and instantiate it: `let Chip = ButtonFlat{height: 40 draw_bg +: {…} draw_text +: {…}}`,
  then `Chip{text: "10%" on_click: || set_tip(10)}` (**✓ run**).
- **A `TextInput` inside its own `on_change`:** reading the input itself
  (`ui.<its id>.text()`) there returns the edited text (**✓ run**). If you see
  `widget has no uid` and then `not found in tree`, your runtime is older than
  the pin: run `python3 tools/setup-native.py --update`. Passing the handler's
  `text` argument on (`on_change: |text| set_query(text)`, as News and Photos
  do) is the simplest form.
- **`ButtonFlat` holds no children:** a `Label` inside a `ButtonFlat` is not
  drawn and the button's own text disappears (**✓ run**). Use `text:`; for a
  rich tappable row use `GestureView{on_tap: |x, y| …}` around the content.
- **Password fields are refused** in a policed isolate: `is_password: true` or
  `content_type: TextInputContentType.Password | NewPassword | OneTimeCode`
  renders an inert field reading `Apps can't ask for passwords` (**✓ run**),
  with no log line, and the gate refuses the bundle.
- **Missing fields and names are errors,** not nil:
  `property missing_field not found in prototype chain. Did you mean: …` and
  `variable no_such_thing not found in scope. Did you mean: …` (**✓ run**).
  Guard optional fields with checks on data you control.
- **Shadowing builtins:** a top-level `let`/`fn` that reuses a prelude name
  (`tick`, `floor`, a widget name) opens a child scope rather than replacing it,
  and `fn tick(` starts an implicit timer. Pick distinct names.
- **Reserved words** cannot be variable names: `me scope self nil true false ok
  let var mut fn if elif else for in while loop match return break continue and
  or is do try use`.

## Errors and the log

`card-host` prints to stdout (`tools/octo run --detach` writes
`<app>/.local-state/card-host.log`).

- Runtime errors in handlers, timers and callbacks:
  `[E] splash:<n>:<line>:<col> - <message> (<runtime file>:<line>)`.
  `<line>` is the `main.splash` line **plus 3** (plus 4 when `net` is granted),
  because of the prelude. An error on `main.splash` line 2 prints as
  `[E] splash:35135094784:5:26 - property missing_field not found …` (**✓ run**).
- A body that fails to evaluate logs
  `splash: splash:<n>:<line0>:<col0>: <message>` with 0-based positions
  (subtract 2, or 3 with `net`). Non-fatal errors during a successful body
  evaluation are not printed.
- Other lines worth grepping: `card-host: … admitted`, `card-host: refused:`,
  `[SPLASH] eval:`, `on_render closure failed; discarding its output:`,
  `splash host: refused`, `splash host callback error:`,
  `contained a mini-app isolate panic`.
