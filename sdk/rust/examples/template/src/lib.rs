//! The source `tools/octo wasm new` copies into a new crate,
//! templates/rust-component/src/lib.rs, built as a workspace member so that
//! `cargo test` runs its tests and the end-to-end tests call its functions.

#[path = "../../../../../templates/rust-component/src/lib.rs"]
mod template;
