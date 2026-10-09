# OctoSense component SDK for Rust

English | [简体中文](README.zh-CN.md)

Write an OctoSense app's own functions in ordinary Rust, and get a
WebAssembly component that the app's script calls as `wasm.<function>`
(OctoSense ADR 0014, proposed in
[OctoSense #436](https://github.com/OctoSense-org/OctoSense/pull/436)). There
is no WIT and no glue code to write. The guide is
[docs/RUST.md](../../docs/RUST.md); `tools/octo wasm new` starts a crate.

```rust
#[octosense_component::export]
pub mod functions {
    pub fn greet(name: &str) -> String {
        format!("Hello, {name}!")
    }
}
```

| Path | What it is |
| --- | --- |
| [octosense-component/](octosense-component/src/lib.rs) | The crate a component depends on. It re-exports the macro and `wit-bindgen` 0.62, and has `log(line)`. |
| [octosense-component-macros/](octosense-component-macros/src/lib.rs) | `#[octosense_component::export]`. It writes the WIT world from the module's `pub fn`s, `pub struct`s and `pub enum`s (names in kebab case), generates the bindings with `wit_bindgen::generate!`, and converts between the module's types and the generated ones. A type it cannot map fails the build with what to use instead. |
| [examples/markdown-tools/](examples/markdown-tools/src/lib.rs) | An unmodified crate (`pulldown-cmark`), a record, an enum, files through `std::fs`, the clock and a log line. |
| [examples/type-tour/](examples/type-tour/src/lib.rs) | Every type mapping both ways, random numbers through `getrandom`, and state kept between calls. |
| [examples/template/](examples/template/src/lib.rs) | [templates/rust-component/src/lib.rs](../../templates/rust-component/src/lib.rs), which `tools/octo wasm new` copies, built as a member here. |
| [e2e/](e2e/tests/components.rs) | Builds the three examples with plain cargo for `wasm32-wasip2`, loads them in Wasmtime 49 with WASI 0.2 as ADR 0014's runtime does, and calls every function. |

Run the tests from this folder; they need the target
(`rustup target add wasm32-wasip2`):

```sh
cargo test --locked --workspace
```

CI's `rust-sdk` job runs them on Ubuntu, with `cargo fmt --all -- --check`.

The SDK is not on crates.io yet. ADR 0014 publishes it there with a
maintainer's approval; until then, a crate depends on it by a git commit of
this repository or by path, and `tools/octo wasm new` writes either. No
OctoSense build runs components yet ([docs/RUST.md](../../docs/RUST.md)).
