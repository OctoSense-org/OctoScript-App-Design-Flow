//! The example components, built with plain cargo for wasm32-wasip2, loaded
//! in Wasmtime 49 with WASI 0.2 the way OctoSense's `wasm` service loads them
//! (ADR 0014): their exports, their WIT signatures and their results.
//!
//! Each test builds its component first (`cargo build --release --target
//! wasm32-wasip2` into `target/e2e-wasm`, which does nothing when it is up to
//! date), or for markdown-tools takes the file `OCTOSENSE_COMPONENT_WASM`
//! names.

use std::path::{Path, PathBuf};
use std::process::Command;

use wasmtime::component::types::{ComponentItem, Type};
use wasmtime::component::{Component, Func, Instance, Linker, ResourceTable, Val};
use wasmtime::{Config, Engine, Store};
use wasmtime_wasi::p2::pipe::MemoryOutputPipe;
use wasmtime_wasi::{FsPerms, WasiCtx, WasiCtxBuilder, WasiCtxView, WasiView};

struct State {
    wasi: WasiCtx,
    table: ResourceTable,
}

impl WasiView for State {
    fn ctx(&mut self) -> WasiCtxView<'_> {
        WasiCtxView {
            ctx: &mut self.wasi,
            table: &mut self.table,
        }
    }
}

fn workspace() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .to_path_buf()
}

/// An example component (`package`, whose file is `file`), built now, in a
/// target directory of its own so the outer `cargo test` lock is not
/// contended. `OCTOSENSE_COMPONENT_WASM` overrides markdown-tools' file.
fn component_bytes(package: &str, file: &str) -> Vec<u8> {
    if package == "markdown-tools" {
        if let Ok(path) = std::env::var("OCTOSENSE_COMPONENT_WASM") {
            return std::fs::read(&path).unwrap_or_else(|e| panic!("{path}: {e}"));
        }
    }
    let target_dir = workspace().join("target/e2e-wasm");
    let status = Command::new(std::env::var("CARGO").unwrap_or_else(|_| "cargo".into()))
        .current_dir(workspace())
        .args([
            "build",
            "--locked",
            "--release",
            "--target",
            "wasm32-wasip2",
            "-p",
            package,
            "--target-dir",
        ])
        .arg(&target_dir)
        .status()
        .expect("cargo runs");
    assert!(
        status.success(),
        "building {package} for wasm32-wasip2 failed (rustup target add wasm32-wasip2)"
    );
    std::fs::read(target_dir.join("wasm32-wasip2/release").join(file)).unwrap()
}

struct Loaded {
    store: Store<State>,
    instance: Instance,
    component: Component,
    engine: Engine,
    stderr: MemoryOutputPipe,
}

fn load(storage: &Path) -> Loaded {
    load_component(storage, "markdown-tools", "markdown_tools.wasm")
}

fn load_component(storage: &Path, package: &str, file: &str) -> Loaded {
    let mut config = Config::new();
    config.wasm_component_model(true);
    let engine = Engine::new(&config).unwrap();
    let bytes = component_bytes(package, file);
    assert_eq!(
        &bytes[4..8],
        &[0x0d, 0x00, 0x01, 0x00],
        "a component, not a core module"
    );
    let component = Component::new(&engine, &bytes).unwrap();
    let stderr = MemoryOutputPipe::new(64 << 10);
    let mut wasi = WasiCtxBuilder::new();
    wasi.stderr(stderr.clone())
        .allow_tcp(false)
        .allow_udp(false)
        .allow_ip_name_lookup(false);
    wasi.preopened_dir(storage, "/", FsPerms::ReadWrite)
        .unwrap();
    let mut store = Store::new(
        &engine,
        State {
            wasi: wasi.build(),
            table: ResourceTable::new(),
        },
    );
    let mut linker = Linker::new(&engine);
    wasmtime_wasi::p2::add_to_linker_sync(&mut linker).unwrap();
    let instance = linker.instantiate(&mut store, &component).unwrap();
    Loaded {
        store,
        instance,
        component,
        engine,
        stderr,
    }
}

fn call(loaded: &mut Loaded, name: &str, args: &[Val]) -> Val {
    let func: Func = loaded
        .instance
        .get_func(&mut loaded.store, name)
        .unwrap_or_else(|| panic!("no export {name}"));
    let mut results = vec![Val::Bool(false)];
    func.call(&mut loaded.store, args, &mut results).unwrap();
    results.remove(0)
}

/// A fresh folder standing in for the app's storage, one per test.
fn storage() -> PathBuf {
    static NEXT: std::sync::atomic::AtomicU32 = std::sync::atomic::AtomicU32::new(0);
    let dir = std::env::temp_dir().join(format!(
        "octosense-component-e2e-{}-{}",
        std::process::id(),
        NEXT.fetch_add(1, std::sync::atomic::Ordering::Relaxed)
    ));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
    dir
}

#[test]
fn ordinary_rust_becomes_typed_exports_with_kebab_names() {
    let dir = storage();
    let loaded = load(&dir);
    let mut exports: Vec<(String, Vec<String>, Vec<String>)> = Vec::new();
    for (name, ext) in loaded.component.component_type().exports(&loaded.engine) {
        if let ComponentItem::ComponentFunc(func) = ext.ty {
            let params = func.params().map(|(n, _)| n.to_string()).collect();
            let results = func
                .results()
                .map(|t| match t {
                    Type::Record(r) => format!(
                        "record {}",
                        r.fields().map(|f| f.name).collect::<Vec<_>>().join(",")
                    ),
                    Type::Enum(e) => format!("enum {}", e.names().collect::<Vec<_>>().join(",")),
                    Type::Result(_) => "result".into(),
                    Type::String => "string".into(),
                    Type::U64 => "u64".into(),
                    other => format!("{other:?}"),
                })
                .collect();
            exports.push((name.to_string(), params, results));
        }
    }
    exports.sort();
    assert_eq!(
        exports,
        [
            (
                "analyze".into(),
                vec!["markdown".into()],
                vec!["record words,lines,headings".into()]
            ),
            (
                "measure".into(),
                vec!["markdown".into()],
                vec!["enum short,medium,long".into()]
            ),
            ("now-ms".into(), vec![], vec!["u64".into()]),
            (
                "save-html".into(),
                vec!["markdown".into(), "path".into()],
                vec!["result".into()]
            ),
            (
                "to-html".into(),
                vec!["markdown".into()],
                vec!["string".into()]
            ),
        ]
    );
    let _ = std::fs::remove_dir_all(dir);
}

#[test]
fn the_exports_run_with_an_unmodified_crate_files_and_a_clock() {
    let dir = storage();
    let mut loaded = load(&dir);
    assert_eq!(
        call(
            &mut loaded,
            "to-html",
            &[Val::String("# Hi\n\nThere *you*".into())]
        ),
        Val::String("<h1>Hi</h1>\n<p>There <em>you</em></p>\n".into())
    );
    let Val::Record(fields) = call(
        &mut loaded,
        "analyze",
        &[Val::String("# Title\n## Part\nsome words".into())],
    ) else {
        panic!("a record")
    };
    assert_eq!(
        fields,
        vec![
            ("words".to_string(), Val::U32(6)),
            ("lines".to_string(), Val::U32(3)),
            (
                "headings".to_string(),
                Val::List(vec![
                    Val::String("Title".into()),
                    Val::String("Part".into())
                ])
            ),
        ]
    );
    assert_eq!(
        call(&mut loaded, "measure", &[Val::String("two words".into())]),
        Val::Enum("short".into())
    );
    assert_eq!(
        call(
            &mut loaded,
            "save-html",
            &[
                Val::String("# Saved".into()),
                Val::String("out.html".into())
            ]
        ),
        Val::Result(Ok(Some(Box::new(Val::U64(15)))))
    );
    assert_eq!(
        std::fs::read_to_string(dir.join("out.html")).unwrap(),
        "<h1>Saved</h1>\n"
    );
    let Val::Result(Err(Some(error))) = call(
        &mut loaded,
        "save-html",
        &[
            Val::String("x".into()),
            Val::String("missing/dir/x.html".into()),
        ],
    ) else {
        panic!("an error result")
    };
    assert!(matches!(*error, Val::String(_)));
    let Val::U64(now) = call(&mut loaded, "now-ms", &[]) else {
        panic!("a number")
    };
    assert!(now > 1_700_000_000_000, "{now}");
    let log = String::from_utf8_lossy(&loaded.stderr.contents()).into_owned();
    assert!(log.contains("saved 15 bytes to out.html"), "{log}");
    let _ = std::fs::remove_dir_all(dir);
}

#[test]
fn the_template_octo_wasm_new_writes_runs_as_a_component() {
    let dir = storage();
    let mut c = load_component(&dir, "component-template", "component_template.wasm");
    assert_eq!(call(&mut c, "greet", &[s("Ada")]), s("Hello, Ada!"));
    assert_eq!(
        call(&mut c, "count", &[s("one two\nthree")]),
        Val::Record(vec![
            ("words".into(), Val::U32(3)),
            ("lines".into(), Val::U32(2))
        ])
    );
    assert_eq!(
        call(&mut c, "parse-number", &[s(" 2.5 ")]),
        Val::Result(Ok(Some(Box::new(Val::Float64(2.5)))))
    );
    assert_eq!(
        call(&mut c, "parse-number", &[s("two")]),
        Val::Result(Err(Some(Box::new(s("\"two\" is not a number")))))
    );
    let _ = std::fs::remove_dir_all(dir);
}

fn s(text: &str) -> Val {
    Val::String(text.into())
}

fn point(x: i32, y: i32, label: Option<&str>) -> Val {
    Val::Record(vec![
        ("x".into(), Val::S32(x)),
        ("y".into(), Val::S32(y)),
        ("label".into(), Val::Option(label.map(|l| Box::new(s(l))))),
    ])
}

#[test]
fn every_type_mapping_crosses_both_ways() {
    let dir = storage();
    let mut c = load_component(&dir, "type-tour", "type_tour.wasm");
    // A record in and out, with an option inside.
    assert_eq!(
        call(&mut c, "mirror", &[point(3, -4, Some("ab"))]),
        point(-3, 4, Some("ba"))
    );
    // Variants with a number, a record and nothing; and back out.
    assert_eq!(
        call(
            &mut c,
            "area",
            &[Val::Variant(
                "rect".into(),
                Some(Box::new(point(2, 5, None)))
            )]
        ),
        Val::Float64(10.0)
    );
    assert_eq!(
        call(&mut c, "area", &[Val::Variant("nothing".into(), None)]),
        Val::Float64(0.0)
    );
    assert_eq!(
        call(
            &mut c,
            "grow",
            &[Val::Variant(
                "circle".into(),
                Some(Box::new(Val::Float64(1.5)))
            )]
        ),
        Val::Variant("circle".into(), Some(Box::new(Val::Float64(3.0))))
    );
    // An enum argument.
    assert_eq!(
        call(
            &mut c,
            "convert",
            &[Val::Float64(10.0), Val::Enum("metric".into())]
        ),
        Val::Float64(25.4)
    );
    // Bytes in (&[u8] and Vec<u8>), a tuple and bytes out.
    let bytes = Val::List(vec![Val::U8(1), Val::U8(2), Val::U8(250)]);
    assert_eq!(
        call(&mut c, "checksum", std::slice::from_ref(&bytes)),
        Val::Tuple(vec![Val::U32(3), Val::U64(253)])
    );
    assert_eq!(
        call(&mut c, "reverse-bytes", &[bytes]),
        Val::List(vec![Val::U8(250), Val::U8(2), Val::U8(1)])
    );
    // Option out, both ways.
    assert_eq!(
        call(&mut c, "first-word", &[s("  hello world")]),
        Val::Option(Some(Box::new(s("hello"))))
    );
    assert_eq!(call(&mut c, "first-word", &[s("   ")]), Val::Option(None));
    // Result<(), String>.
    assert_eq!(
        call(&mut c, "check", &[Val::Bool(true)]),
        Val::Result(Ok(None))
    );
    assert_eq!(
        call(&mut c, "check", &[Val::Bool(false)]),
        Val::Result(Err(Some(Box::new(s("not ok")))))
    );
    // Small numbers, char and bool in a tuple.
    assert_eq!(
        call(
            &mut c,
            "widen",
            &[
                Val::U8(200),
                Val::S8(-100),
                Val::Char('é'),
                Val::Bool(false)
            ]
        ),
        Val::Tuple(vec![
            Val::U16(400),
            Val::S16(-200),
            Val::U32('é' as u32),
            Val::Bool(true)
        ])
    );
    // Random numbers through getrandom.
    let random = |c: &mut Loaded| match call(c, "random-u64", &[]) {
        Val::Result(Ok(Some(value))) => *value,
        other => panic!("{other:?}"),
    };
    assert_ne!(random(&mut c), random(&mut c));
    // State kept in the instance between calls.
    assert_eq!(call(&mut c, "tally", &[Val::U64(2)]), Val::U64(2));
    assert_eq!(call(&mut c, "tally", &[Val::U64(3)]), Val::U64(5));
    // A list of records in, a list of strings out.
    assert_eq!(
        call(
            &mut c,
            "labels",
            &[Val::List(vec![
                point(0, 0, Some("a")),
                point(1, 1, None),
                point(2, 2, Some("c"))
            ])]
        ),
        Val::List(vec![s("a"), s("c")])
    );
    let _ = std::fs::remove_dir_all(dir);
}
