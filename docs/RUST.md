# Run your own Rust code

English | [简体中文](RUST.zh-CN.md)

A store app's bundle holds no native code, but it can carry your Rust code as
**Wasm functions**: Rust functions that a WebAssembly module (a `.wasm` file
in the bundle's `fns/` folder) exports by name. OctoSense's `wasm` service runs
each function in a sandbox where it sees only its input. Every standard
desktop and Home build of OctoSense `main` includes the service on macOS,
Linux and Android, with limited support; no release includes it yet. For the
device, the network, files or native code, use another route.

Every command on this page was run on macOS (Apple silicon) unless it is
marked **unverified**. No shell that runs functions was built for this guide.

## Choose a route

| You need | Route | Read |
| --- | --- | --- |
| Pure computation: parsing, scoring, crypto, image processing | A Wasm function | [Write a function](#write-a-function) |
| The camera, the microphone or the location | Host APIs: the `camera`, `microphone` and `location` capabilities, their permission methods and `location.get` | [HOST-API-V1 §3](HOST-API-V1.md#3-request-device-access-in-the-foreground) |
| The network | Splash's `net`, to the hosts in `network.hosts`. A function cannot reach the network: fetch the data in Splash, then pass it to the function. | [SCRIPT-API § Network](SCRIPT-API.md#network) |
| Files | The app's own storage, through `fs.*` in Splash. Pass the contents to the function: text as a string, other data as JSON. | [SCRIPT-API § Storage](SCRIPT-API.md#storage-fs) |
| A native library, threads or OS calls | Not available to a store app. App Hub's gate refuses native libraries, and native code ships only inside a shell release. | App Hub's [delivery paths](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/DEVELOPMENT.md#choose-a-delivery-path) |

## Where functions run

The shell's `wasm` host service runs the functions. OctoSense's
[ADR 0011](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0011-apps-own-functions-in-webassembly.md)
accepts the service with limited support: `wasm-functions`, an OctoSense
Cargo feature that is on by default, includes it in every standard desktop
and Home build on macOS, Linux and Android. `wasm-lab` is the feature's
former name and stays as an alias. Builds for Windows (not yet checked), iOS
(no code generation for apps) and OpenHarmony (policy unknown) leave the
runtime out.

| Build | Accepts an app that requests `wasm` | Runs its functions |
| --- | --- | --- |
| `desktop-v0.1.0-beta.2` | No. Its app contract, 1.5, refuses the capability: `app <id> requests unknown capability "wasm"`. | No |
| OctoSense `main` (in no release yet), default build for macOS, Linux or Android: feature `wasm-functions`, formerly `wasm-lab` | Yes | Yes |
| OctoSense `main` (in no release yet), build for Windows, iOS or OpenHarmony | Yes | No. Every call answers `no service answers "wasm" on this device`. |
| `card-host`, built from App Hub `main` | Yes | No. Every call answers `no service answers "wasm" on this device`. |

No release includes the service yet: `desktop-v0.1.0-beta.2`, desktop RC1
and `home-v0.1.0-beta.1` leave it out. The first desktop and Home releases
built from `main` after OctoSense
[#400](https://github.com/OctoSense-org/OctoSense/pull/400) will include it.

App Hub's gate (`hub check`) admits the `wasm` capability from app contract
1.7, with at most 8 modules per bundle ([Build it](#build-it)).

**Unverified:** no store-installed app has run its functions yet. Only Wasm
Lab, a system app, has run functions on a device.

## How a call runs

1. The app's script calls `host.request("wasm.<function>", args, fn(r){…})`,
   or the app's agent calls a tool mapped to `wasm.<function>`.
2. On the app's first call, the `wasm` service loads every module in the
   app's own bundle (`fns/*.wasm`), never another app's. Wasmtime, the
   shell's WebAssembly runtime, compiles each module with its Cranelift
   compiler, or takes the compiled code from the shell's cache on disk.
3. The service passes the arguments to the function as bytes. The function
   runs on the app's own worker thread, so a slow function holds up only its
   own app. One app's calls run one at a time, in order. The worker exits
   after 5 idle seconds; the app's next call starts a new one, which loads
   the modules again.
4. The script's callback gets the output in `r.data`, or an error in
   `r.error`.

Every call gets a fresh **instance**: a running copy of the module with its
own memory. Nothing survives from one call to the next: a `static`, a cache
in memory or anything else written to the module's linear memory is gone at
the next call. Only the compiled code is reused. Keep state in the script,
and pass the function what it needs with each call. A **trap** aborts the
function on a panic, a stack overflow or memory over the 256 MiB cap. A trap
or the 2 s deadline ends the call with an error; the shell keeps running.

After an app update, a changed grant or a signed withdrawal, the service
discards the compiled code and the answer of a call that was running. That
call answers `wasm app admission changed; retry from the current app`, and
the next call loads the new modules, with no restart of the shell.

## Write a function

### The guest crate

`octosense-guest` is a helper crate for the guest, the Rust code inside the
module. It implements [the ABI](#the-abi) for you. It is not on crates.io.
Copy it from
[`apps/wasmlab/guest/octosense-guest`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/wasmlab/guest/octosense-guest)
in the OctoSense repository. It is licensed under Apache-2.0 and depends only
on `serde_json`.

| Item | What it does |
| --- | --- |
| `octosense_guest::abi!()` | Exports `octo_alloc` and `octo_free`. Invoke it once per crate. |
| `octosense_guest::export!(f)` | Exports `fn f(&[u8]) -> Result<Vec<u8>, String>` as `f`: bytes in, bytes out. |
| `octosense_guest::export_json!(f)` | Exports `fn f(In) -> Result<Out, String>` as `f`, where `In: Deserialize` and `Out: Serialize`. It parses the input as JSON into `In` and writes `Out` as JSON. Input that does not parse fails with `the input is not what f takes: <reason>`. |
| `octosense_guest::log(line)` | Writes `line` to the shell's log, as `wasm <app id>: <line>`. A native build prints it to stderr. |
| A panic hook, which `export!` and `export_json!` install | Logs the panic's message, as a `panic: …` line, before the call traps. |

### A minimal example

These steps add functions to an app that `tools/octo new` made in
`~/apps/my-app` ([QUICKSTART §3](QUICKSTART.md#3-create-an-app)); the
examples give it the id `dev.example.texttools`. Keep the Rust crate beside
`bundle/`. Only the built module goes into the bundle:

```text
~/apps/my-app/
  bundle/
    fns/my_functions.wasm   the built module
  functions/                your Rust crate; not in the bundle
    Cargo.toml
    src/lib.rs
  octosense-guest/          copied from OctoSense; not in the bundle
```

1. Clone OctoSense into `<workspace>` as
   [PUBLISHING §4.2](PUBLISHING.md#42-install-and-open-the-app-in-the-desktop-shell)
   shows, then copy the guest crate:

   ```sh
   cp -R <workspace>/OctoSense/apps/wasmlab/guest/octosense-guest ~/apps/my-app/
   ```

2. Write `functions/Cargo.toml`. `cdylib` produces the `.wasm` file, and
   `rlib` lets other Rust code, such as integration tests, link the same
   functions natively. The release profile is Wasm Lab's
   ([Build it](#build-it)).

   ```toml
   [package]
   name = "my-functions"
   version = "0.1.0"
   edition = "2021"
   publish = false

   [lib]
   crate-type = ["cdylib", "rlib"]

   [dependencies]
   octosense-guest = { path = "../octosense-guest" }
   serde = { version = "1", features = ["derive"] }
   pulldown-cmark = { version = "0.13", default-features = false, features = ["html"] }

   [profile.release]
   opt-level = 3
   lto = true
   codegen-units = 1
   panic = "abort"
   strip = true
   ```

3. Write `functions/src/lib.rs`. It adapts two of Wasm Lab's functions:
   `md_to_html` takes text and returns text, and `rank` takes and returns
   JSON.

   ```rust
   //! The app's own functions, built for wasm32-unknown-unknown.
   use serde::{Deserialize, Serialize};

   // Exports octo_alloc and octo_free. Invoke it once per crate.
   octosense_guest::abi!();

   /// Text in, text out: CommonMark to HTML.
   pub fn md_to_html(input: &[u8]) -> Result<Vec<u8>, String> {
       let text = std::str::from_utf8(input).map_err(|_| "the text is not UTF-8".to_string())?;
       let mut html = String::new();
       pulldown_cmark::html::push_html(&mut html, pulldown_cmark::Parser::new(text));
       Ok(html.into_bytes())
   }
   octosense_guest::export!(md_to_html);

   /// JSON in, JSON out: the items that contain the query, earliest match first.
   #[derive(Deserialize)]
   pub struct RankRequest {
       pub query: String,
       pub items: Vec<String>,
       #[serde(default = "ten")]
       pub limit: usize,
   }

   #[derive(Serialize)]
   pub struct Ranking {
       pub ranked: Vec<String>,
   }

   fn ten() -> usize {
       10
   }

   pub fn rank(req: RankRequest) -> Result<Ranking, String> {
       let query = req.query.to_lowercase();
       if query.is_empty() {
           return Err("the query is empty".into());
       }
       let mut hits: Vec<(usize, &String)> = req
           .items
           .iter()
           .filter_map(|item| item.to_lowercase().find(&query).map(|at| (at, item)))
           .collect();
       hits.sort();
       let ranked = hits.into_iter().take(req.limit).map(|(_, item)| item.clone()).collect();
       Ok(Ranking { ranked })
   }
   octosense_guest::export_json!(rank);

   #[cfg(test)]
   mod tests {
       use super::*;

       #[test]
       fn the_earliest_match_comes_first() {
           let req = RankRequest {
               query: "cal".into(),
               items: vec!["Local calls".into(), "Calendar".into(), "Mail".into()],
               limit: 10,
           };
           assert_eq!(rank(req).unwrap().ranked, ["Calendar", "Local calls"]);
       }
   }
   ```

4. Test the logic natively, from `~/apps/my-app`:

   ```sh
   cargo test --manifest-path functions/Cargo.toml
   ```

   The output includes `test tests::the_earliest_match_comes_first ... ok`.

### What the sandbox forbids

A function reaches nothing but its own memory and `octo.log`. Rust's
standard library still compiles for `wasm32-unknown-unknown`, but the calls
below fail or do nothing:

| Your code | What happens | Instead |
| --- | --- | --- |
| Reads the clock: `Instant::now()`, `SystemTime::now()` | Panics with `time not implemented on this platform`, so the call traps. | Pass the time in the input. Splash has `time_now()`. |
| Gets random bytes from `getrandom`, directly or through a crate such as `rand` with its default features | `getrandom` does not build for `wasm32-unknown-unknown`. With its JavaScript backend enabled, it imports `wasm-bindgen` functions, so the module does not load. | Pass a seed in the input. Splash has `random_u32()`. |
| Opens a file with `std::fs` | Returns `operation not supported on this platform`. | Read the file in Splash and pass its contents in. |
| Opens a socket with `std::net` | Returns `operation not supported on this platform`. | Fetch with `net` in Splash and pass the data in. |
| Starts a thread with `std::thread::spawn` | Panics, so the call traps. `thread::Builder::spawn` returns `operation not supported on this platform`. | Compute on one thread. |
| Reads an environment variable | `std::env::var` returns `Err(NotPresent)`. | Pass settings in the input. |
| Prints with `println!` or `eprintln!` | Writes nothing. | Call `octosense_guest::log`. |
| Imports a host function, such as WASI's or `wasm-bindgen`'s | The module does not load: `the module imports <name>; only octo.log is provided`. | Build for `wasm32-unknown-unknown` and drop the dependency that adds the import. |

### Limits

| Limit | Value | When a function exceeds it |
| --- | --- | --- |
| Time per call | 2 s of wall-clock time, checked every 10 ms | `the call ran past its deadline` |
| Memory per instance | 256 MiB | `the function trapped: memory over its cap (…)` |
| Wasm stack per call | 512 KiB | `the function trapped: wasm trap: call stack exhausted` |
| Input and output of a call | 16 MiB each | `<n> bytes is over the input/output limit` |
| Module size | 8 MiB | `<file>: the module is <n> bytes, over the limit` |
| Log | 64 lines per call, each cut to 1,024 bytes | Further lines are dropped. |

The `wasm` service adds its own limits to every request:

| Limit | Value | When a request exceeds it |
| --- | --- | --- |
| Serialized input | 1 MiB per request | `wasm input exceeds 1 MiB` |
| Queued requests | 4 per app | `wasm app queue is full; try again later` |
| Apps running functions at once | 4 | `wasm workers are busy; try again later` |
| Buffered input, all apps together | 16 MiB | `wasm input queue is full; try again later` |
| One request, including queueing and loading | 10 s, the service's timeout (App Hub's default is 60 s) | `the host service timed out` |

A full queue or no free worker fails the request at once instead of making
it wait. An app's calls run one at a time, in order, on its own worker
thread, and a worker exits after 5 idle seconds.

App Hub's general limits on host-service requests still apply too, but the
`wasm` service's own are stricter. A call from a script meets these caps
before the runtime's 16 MiB ones:

| Limit | Value | When a call exceeds it |
| --- | --- | --- |
| A script's arguments | 1 MiB of JSON | `the request's arguments exceed 1 MiB` |
| The answer | 4 MiB of JSON | `the service's answer exceeds 4 MiB` |
| Calls waiting per app | 32 | `too many host requests are waiting; try again when some have answered` |

Source: `Limits::default()` in OctoSense's `crates/wasm-host/src/lib.rs`,
which the `wasm` service uses, the constants in OctoSense's
`crates/shell/src/wasm_service.rs`, and `crates/appstore/src/services.rs` in
App Hub.

### The ABI

The guest crate implements this ABI. Read it to write a module without the
crate, or to debug one. A module is a WebAssembly core module, not a
component. It has these exports and at most one import:

| Name | Kind | Type | Role |
| --- | --- | --- | --- |
| `memory` | Export | Memory | The module's linear memory. |
| `octo_alloc` | Export | `(len: i32) -> i32` | Allocates `len` bytes for the input and returns their address. |
| `octo_free` | Export | `(ptr: i32, len: i32)` | Frees a buffer that `octo_alloc` returned or that holds an output. |
| Each function | Export | `(ptr: i32, len: i32) -> i64` | Reads `len` input bytes at `ptr` and returns `(out_ptr << 32) \| out_len`: the address and length of an output buffer it allocated, which starts with a status byte (step 4 below). |
| `octo.log` | Import, optional | `(ptr: i32, len: i32)` | Writes one line to the shell's log. |

The shell makes each call in four steps:

1. It calls `octo_alloc(len)` and writes the input at the returned address.
2. It calls the function with that address and length, then frees the input
   with `octo_free`.
3. It copies the output buffer and frees it with `octo_free`.
4. It reads the buffer's first byte, the status: `0` means the rest is the
   output, and `1` means the rest is the error text in UTF-8. Any other
   value, or an empty buffer, is a trap.

Every export of type `(i32, i32) -> i64` is a function the app can call. The
shell ignores exports of other types. A module that lacks `memory`,
`octo_alloc` or `octo_free`, or imports anything besides `octo.log`, does not
load.

## Build it

Run these commands from `~/apps/my-app`.

1. Check that Rust has the WebAssembly target:

   ```sh
   rustup target list --installed
   ```

   The list includes `wasm32-unknown-unknown`. If it does not, add it
   (**unverified**):

   ```sh
   rustup target add wasm32-unknown-unknown
   ```

2. Build the module:

   ```sh
   cargo build --manifest-path functions/Cargo.toml --release --target wasm32-unknown-unknown
   ```

   A successful build ends with ``Finished `release` profile [optimized] target(s) in …``.
   If it fails while compiling `getrandom`, a dependency needs OS randomness:
   drop that dependency, or turn off the feature that pulls in `getrandom`
   ([What the sandbox forbids](#what-the-sandbox-forbids)).

3. Copy the module into the bundle. Cargo names the file after the package,
   with `-` turned into `_`:

   ```sh
   mkdir -p bundle/fns
   cp functions/target/wasm32-unknown-unknown/release/my_functions.wasm bundle/fns/
   ```

The gate holds the bundle to these rules:

| Rule | Value |
| --- | --- |
| Path | `fns/<name>.wasm`, directly in `fns/` |
| Name | 1 to 64 characters of `[a-z0-9_-]` |
| Header | The first 8 bytes: a WebAssembly core module, version 1 |
| Modules | At most 8 per bundle |
| Bundle size | 8 MiB (8,388,608 bytes) of files, not counting `manifest.json` |

The gate does not read a module's imports or exports. The shell checks them
when it loads the module, so a module that passes the gate can still fail to
load ([Errors the app sees](#errors-the-app-sees)). Each function name must
also be unique across the app's modules: the `wasm` service refuses to load
two modules that export the same name.

The example uses Wasm Lab's release profile:

| Setting | Effect |
| --- | --- |
| `opt-level = 3` | Optimizes for speed. |
| `lto = true`, `codegen-units = 1` | Optimizes across crates as one unit. |
| `panic = "abort"` | A panic traps at once, with no unwinding code. |
| `strip = true` | Drops symbols and debug information. |

Built with Rust 1.97, the example's module is 372,358 bytes with these
settings, and 430,973 bytes with Cargo's default release profile.

`target/` is in the `.gitignore` that `tools/octo new` writes, so the build
output stays out of Git. Commit `bundle/fns/my_functions.wasm` with
`functions/` and the copied `octosense-guest/`, which the crate needs to
build.

## Declare and call it

### Declare the capability

1. Request `wasm` in `bundle/manifest.json`:

   ```json
   "capabilities": ["wasm"]
   ```

   `wasm` needs no `requires` marker; it is an ordinary capability. The
   store shows the person "Run its own sandboxed functions on this device".

2. Stamp and check the bundle, from your App Flow checkout:

   ```sh
   tools/octo check ~/apps/my-app/bundle
   ```

   With the rest of the bundle complete
   ([QUICKSTART §8](QUICKSTART.md#8-check-it)), it passes with only the
   unsigned warning, and the `grants:` line lists `wasm`. For the app
   `dev.example.texttools`, the output is:

   ```text
   dev.example.texttools 0.1.0 — PASSED
     [warning] publisher-signature: unsigned: accountability rests on the hub alone
     grants: capabilities {"wasm"}, hosts {}, storage none, agent none
   ```

   If the gate refuses the module, fix what the finding names:

   | Finding | Fix |
   | --- | --- |
   | `[refused] functions: the bundle carries 1 WebAssembly module(s) but does not declare the wasm capability` | Request `wasm` (step 1). |
   | `[refused] functions: the bundle carries 9 WebAssembly modules, over the 8 it may` | Put the functions in 8 modules or fewer. |
   | `[refused] contents-invalid (fns/MyFunctions.wasm): a function module is named fns/<name>.wasm, the name [a-z0-9_-] and at most 64 characters` | Rename the file, and keep it directly in `fns/`. |
   | `[refused] contents-invalid (lib/x.wasm): a WebAssembly module belongs in fns/, as fns/<name>.wasm` | Move the file into `fns/`. |
   | `[refused] contents-invalid (fns/x.wasm): not a WebAssembly core module (magic and version 1)` | Ship a core module built for `wasm32-unknown-unknown`, not a component. |
   | `[warning] functions: the bundle declares the wasm capability but carries no fns/*.wasm` | Copy the module into `bundle/fns/` ([Build it](#build-it), step 3). |
   | `hub: the bundle exceeds the size limit` | Bring the bundle's files under 8 MiB. |

### Call it from Splash

Call `wasm.<function>`, where `<function>` is the exported name:

```splash
host.request("wasm.rank", {query: "cal" items: ["Local calls" "Calendar" "Mail"]}, fn(r){
    if r.is_ok { ranked = r.data.ranked } else { note = r.error }
})

host.request("wasm.md_to_html", "# Hello", fn(r){
    if r.is_ok { html = r.data.text } else { note = r.error }
})
```

Here `r.data.ranked` is `["Calendar", "Local calls"]`, and `r.data.text`
is `<h1>Hello</h1>` followed by a newline. The service converts the
arguments and the output like this:

| The script passes | The function receives |
| --- | --- |
| A string | Its text, as UTF-8 bytes. Implement the function with `export!`. |
| Anything else: an object, a list, a number or a boolean | Its JSON. Implement the function with `export_json!`. |

| The function returns | `r.data` is |
| --- | --- |
| Valid JSON | That value |
| Anything else | `{text: <the output as UTF-8>}` |

To pass binary data, such as an image that `fs.read_bytes` returns, pass the
byte list. It arrives as a JSON array of numbers, which `export_json!` reads
into a `Vec<u8>`. Each byte takes up to 4 characters, so the 1 MiB argument
limit holds at least 256 KiB of binary data (**unverified**).

### Call it from an agent tool

Shipping `tools.json` gives the app its own agent, so declare the `agent`
block as well
([AI-SERVICES § An app's own agent](AI-SERVICES.md#an-apps-own-agent)). Add
this entry to the `tools` array of `bundle/tools.json`. Its `host_method`
maps the tool to the `rank` function:

```json
{
  "name": "texttools.rank",
  "description": "Rank names against a query, earliest match first. Computes only.",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "maxLength": 200 },
      "items": { "type": "array", "items": { "type": "string" }, "maxItems": 1000 },
      "limit": { "type": "integer", "minimum": 1, "maximum": 100 }
    },
    "required": ["query", "items"],
    "additionalProperties": false
  },
  "output_schema": {
    "type": "object",
    "properties": { "ranked": { "type": "array", "items": { "type": "string" } } },
    "required": ["ranked"]
  },
  "risk": "read",
  "background": true,
  "shareable": true,
  "implemented_by": "host-service",
  "host_method": "wasm.rank"
}
```

The tool's name starts with the app's namespace, the last segment of its
id: `texttools` for `dev.example.texttools`. App Hub's
[`tools.json` rules](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#toolsjson-the-apps-tools)
apply. Four of them differ for `wasm.<function>`:

| Rule | Other `host_method` tools | `wasm.<function>` |
| --- | --- | --- |
| Method | One in App Hub's reviewed list | Any function the app exports: one segment after `wasm.`, of `[a-z0-9_]` |
| Minimum `risk` | Set per method | None; `read` fits a function that only computes |
| `private_data` | Must be `true` | Not required: the function sees only its arguments |
| Capability | The method's family | `wasm` |

A tool's arguments are a JSON object, so implement the function with
`export_json!`. Return an object as well, and declare an object
`output_schema`, because octos, OctoSense's agent kernel, accepts only
object schemas. That is why `rank` returns `{"ranked": […]}` rather than a
bare list. The agent receives `{"ok": true, "data": <output>}`, or
`{"ok": false, "error": {"kind": "app_error", "message": <error>}}`.

The gate's refusal names the rule it applies, such as
`[refused] tools: texttools.rank: host_method "wasm.rank" requires the declared "wasm" service capability`.

### Check what loaded

Call `wasm.functions` with `{}` to learn whether the host runs functions,
and which ones loaded. Where no `wasm` service runs, the call fails with
`no service answers "wasm" on this device`. `runtime.list` and
`runtime.describe` do not list the `wasm` methods. `wasm.functions` answers
with:

| Field | Holds |
| --- | --- |
| `functions` | The names of the app's functions. |
| `modules` | One entry per module file: `file`, `bytes`, `load_ms`, `from_cache` (whether the compiled code came from the cache), `memory_bytes` (the most memory a call has used: a high-water mark only), `invocations` (the calls so far), `renewed` (`invocations - 1`: every call after the first got a fresh instance) and `instance_policy` (`"fresh-per-call"`). |
| `stats` | One entry per function called so far: `calls`, `errors`, `mean_us` and `max_us`. |

The counts start when the app's worker starts. A worker exits after 5 idle
seconds, and the counts start again with the next one.

Do not name a function `functions`: `wasm.functions` never calls it.

### Errors the app sees

| `r.error` | Cause | Fix |
| --- | --- | --- |
| `this app was not granted "wasm", which "wasm.rank" needs` | The manifest does not request `wasm`. | Add `wasm` to `capabilities`. |
| `no service answers "wasm" on this device` | The host has no `wasm` service: `card-host`, a release, or an OctoSense build for Windows, iOS or OpenHarmony. | Test in a desktop shell built from OctoSense `main` on macOS or Linux ([Test it](#test-it)). |
| `<app id> has no function "rank"` | No module exports that name. | Compare the name with what `wasm.functions` lists. |
| `<app id>'s bundle has no fns directory` | The app requests `wasm` but ships no module. | Add `fns/<name>.wasm`. |
| `<file>: the module imports <name>; only octo.log is provided` | A dependency imports WASI or `wasm-bindgen` functions. | Build for `wasm32-unknown-unknown`, and drop that dependency. |
| `<file>: the module does not export <name>` | The crate does not invoke `octosense_guest::abi!()`. | Add it once. |
| `<file>: <function> is exported by another module too` | Two modules export the same name. | Rename one of the functions. |
| `the input is not what rank takes: <reason>` | The arguments do not match the function's input type. | Fix the arguments or the type. |
| The function's own text, such as `the query is empty` | The function returned `Err`. | Handle it in the script. |
| `the call ran past its deadline`, `the function trapped: …` | The call broke a [limit](#limits) or [the sandbox](#what-the-sandbox-forbids). | For a panic, read the `panic: …` line in the shell's log. For the deadline, do less work per call. |
| `wasm input exceeds 1 MiB` | The request's serialized input is over 1 MiB. | Pass less input per call. |
| `wasm app queue is full; try again later` | The app already has 4 requests queued. | Send fewer requests at once, for example each one from the previous one's callback. |
| `wasm workers are busy; try again later` | 4 other apps have a worker; a worker exits only after 5 idle seconds. | Try again later. |
| `wasm input queue is full; try again later` | The requests of all apps already buffer 16 MiB of input. | Try again later. |
| `wasm app admission changed; retry from the current app` | The app was updated, its grant changed or it was withdrawn while the call ran. | Call again. After an update, the next call loads the new modules. |
| `the host service timed out` | The request took more than 10 s, including queueing and loading. | Do less work per call, and queue fewer calls. |

The service loads an app's modules together. While any module fails to load,
every call answers that module's error. The service tries again on the next
call.

## Test it

Steps 3 to 9 test the functions in a shell that runs them, so they are
**unverified**.

1. Run the app in `card-host` with `tools/octo run`
   ([QUICKSTART §4](QUICKSTART.md#4-run-it-on-the-desktop)). `card-host`
   admits the bundle but has no `wasm` service, so every call answers
   `no service answers "wasm" on this device`. Use it to check the layout
   and what the app shows without its functions.
2. Set up the OctoSense clone from [A minimal example](#a-minimal-example),
   step 1, as
   [PUBLISHING §4.2](PUBLISHING.md#42-install-and-open-the-app-in-the-desktop-shell)
   shows.
3. Build and start the desktop shell with
   `desktop/system-apps-wasm-lab.json`, which lists the default system apps
   plus Wasm Lab. The default build includes the `wasm` service on macOS and
   Linux, so it needs no `--features wasm-lab`:

   ```sh
   cd <workspace>/OctoSense
   OCTOSENSE_SYSTEM_APPS="$PWD/desktop/system-apps-wasm-lab.json" \
     cargo run --release -p octosense
   ```

   OctoSense checked its plain default build with
   `OCTOSENSE_SYSTEM_APPS=$PWD/desktop/system-apps-wasm-lab.json cargo build --locked -p octosense`,
   then ran Wasm Lab with `--test-action launch-wasmlab`
   ([WebAssembly in OctoSense § Wasm Lab](https://github.com/OctoSense-org/OctoSense/blob/main/docs/wasm.md#wasm-lab)).

4. Open **Wasm Lab** from the dock or the **Apps** menu. Each card calls one
   function and shows the result and the round trip. When a module loads,
   the shell's log shows a line such as
   `wasm os.wasmlab: wasmlab.wasm (433 KiB) compiled in … ms: find_slots, fuzzy_rank, md_to_html, rogue, text_diff`.
   Wasm Lab sends five requests when it opens, one more than the service
   queues for an app, so on a cold start its Markdown card shows
   `wasm app queue is full; try again later`.
5. Under **Misbehave**, click each button. A loop, endless allocation, a
   panic and runaway recursion each end in an error, and the next call still
   answers.
6. Publish your own app to a local mirror, as
   [PUBLISHING §4.1](PUBLISHING.md#41-publish-into-a-local-mirror) shows.
7. Quit the shell, and start it again with the command in
   [PUBLISHING §4.2](PUBLISHING.md#42-install-and-open-the-app-in-the-desktop-shell).
8. Install and open your app from **App Hub** in the dock.
9. Install a new version while the shell runs, then call a function again:
   the next call loads the new modules, with no restart. A call that runs
   during the update answers
   `wasm app admission changed; retry from the current app`.

Agent tools, Wasm Lab's or your app's, also need the octos kernel, staged
as the
[desktop README](https://github.com/OctoSense-org/OctoSense/blob/main/desktop/README.md#build-and-run)
describes, and an AI provider. Home, the phone shell, runs the service on
Android in its default build and has a `phone/system-apps-wasm-lab.json`
file; build it as OctoSense's
[phone README](https://github.com/OctoSense-org/OctoSense/blob/main/phone/README.md)
describes (**unverified**).

## Open items

OctoSense's [ADR 0011](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0011-apps-own-functions-in-webassembly.md)
records the design. These items are open:

| Item | Status |
| --- | --- |
| A CPU budget per app | Not yet. The limits apply per call, so an app can keep one core busy with back-to-back calls. |
| Compiling modules ahead of time for phones | Not yet. The first call compiles each module: ADR 0011 measured 27–33 ms on a desktop and 378–421 ms on a mid-range Android phone, and 5–11 ms for later loads from the cache on that phone. |
| Agent tools with a live model | Unverified. OctoSense's tests call Wasm Lab's tools through the shell's tool executor, without a model. |
| Windows | Not yet. Builds for Windows leave the runtime out until it has been checked there. |
| iOS | Not yet. Builds for iOS leave the runtime out. iOS allows no JIT for apps, so Wasmtime would have to use its Pulley interpreter, about 17 times slower than Cranelift. iOS also allows no downloaded native code, so a store app's functions cannot be compiled ahead of time there either. |
| OpenHarmony | Not yet. Its JIT policy is unknown, so builds for OpenHarmony leave the runtime out. |
| Typed interfaces (the component model and WIT), host imports such as a clock or randomness, and deterministic limits (fuel) | Not yet decided. Any host import beyond `octo.log` would be a new capability. |

## See also

- OctoSense's [WebAssembly in OctoSense](https://github.com/OctoSense-org/OctoSense/blob/main/docs/wasm.md):
  how the `wasm` service works on `main`, with its limits, platforms and
  tests.
- [HOST-API-V1](HOST-API-V1.md): device permissions and `location.get`.
- [CAPABILITIES § Host services](CAPABILITIES.md#host-services): `wasm`
  beside the other host services.
- App Hub's [PUBLISHING § Findings](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#findings)
  and [§ Map a tool to a shared service](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#map-a-tool-to-a-shared-service-host_method):
  the gate's rules for `fns/` and `wasm.<function>`.
- App Hub's [SUBMITTING § What the Hub cannot do yet](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#what-the-hub-cannot-do-yet):
  what a store app cannot do yet, native Rust code included.
- [Wasm Lab](https://github.com/OctoSense-org/OctoSense/tree/main/apps/wasmlab):
  the reference app, its guest crate and its `build.sh`.
