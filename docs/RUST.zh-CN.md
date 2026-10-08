# 运行自己的 Rust 代码

[English](RUST.md) | 简体中文

未注明中文版的链接指向英文文档。

商店应用的应用包不能带原生代码，但可以把你的 Rust 代码做成 **Wasm 函数**带上：Rust 函数编译进 WebAssembly 模块（一个 `.wasm` 文件，放在应用包的 `fns/` 文件夹中），由模块按名称导出。启用 `wasm-lab` 特性构建的 OctoSense Shell 会在沙盒中运行每个函数，函数只能看到自己的输入；目前还没有任何发布版本包含这项特性。设备、网络、文件或原生代码，请改用其他途径。

每条命令都在 macOS（Apple 芯片）上运行过，标注为**未验证**的除外。编写本文时没有构建启用 `wasm-lab` 的 Shell。

## 选择途径

| 你需要 | 途径 | 参阅 |
| --- | --- | --- |
| 纯计算：解析、打分、密码学运算、图像处理 | Wasm 函数 | [编写函数](#编写函数) |
| 相机、麦克风或位置 | 宿主 API：`camera`、`microphone` 和 `location` 能力及其权限方法，以及 `location.get` | [HOST-API-V1 §3](HOST-API-V1.zh-CN.md#3-在前台申请设备访问) |
| 网络 | Splash 的 `net`，只能访问 `network.hosts` 中的主机。函数访问不了网络：先在 Splash 中取回数据，再传给函数。 | [SCRIPT-API § Network](SCRIPT-API.md#network) |
| 文件 | 应用自己的存储，在 Splash 中通过 `fs.*` 读写。把内容传给函数：文本作为字符串传，其他数据作为 JSON 传。 | [SCRIPT-API § Storage](SCRIPT-API.md#storage-fs) |
| 原生库、线程或系统调用 | 商店应用无法使用。App Hub 的准入检查会拒绝原生库，原生代码只能随 Shell 的发布版本分发。 | App Hub 的[交付路径](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/DEVELOPMENT.zh-CN.md#选择合适的交付路径) |

## 函数在哪里运行

函数由 Shell 的 `wasm` 宿主服务运行。只有启用了 `wasm-lab` 的构建才包含这项服务；`wasm-lab` 是 OctoSense 的 Cargo 特性，默认关闭。

| 构建 | 是否接受申请 `wasm` 的应用 | 是否运行它的函数 |
| --- | --- | --- |
| `desktop-v0.1.0-beta.2` | 否。它的应用契约是 1.5，会拒绝这项能力：`app <id> requests unknown capability "wasm"`。 | 否 |
| [OctoSense 桌面版 0.1.0-rc.1](../README.zh-CN.md#下载兼容-shell) 及之后的默认构建 | 是 | 否。每次调用都返回 `no service answers "wasm" on this device`。 |
| 启用 `wasm-lab` 构建的 OctoSense `main`（尚未进入任何发布版本） | 是 | 是 |
| 基于 App Hub `main` 构建的 `card-host` | 是 | 否。每次调用都返回 `no service answers "wasm" on this device`。 |

App Hub 的准入检查（`hub check`）从应用契约 1.7 起接受 `wasm` 能力，每个应用包最多带 8 个模块（见[构建](#构建)）。

**未验证**：还没有从商店安装的应用运行过自己的函数。目前只有系统应用 Wasm Lab 在设备上运行过函数。

## 一次调用的过程

1. 应用的脚本调用 `host.request("wasm.<function>", args, fn(r){…})`，或者应用的 Agent 调用映射到 `wasm.<function>` 的工具。
2. 应用第一次调用时，`wasm` 服务从该应用自己的应用包中加载全部模块（`fns/*.wasm`），绝不加载其他应用的模块。Shell 的 WebAssembly 运行时 Wasmtime 用自带的 Cranelift 编译器编译每个模块，或者直接从 Shell 的磁盘缓存中取出编译好的代码。
3. 服务把参数以字节形式传给函数。函数在该应用专属的工作线程上运行，所以一个慢函数只会拖慢它自己的应用。同一个应用的调用按顺序逐个执行。
4. 脚本的回调从 `r.data` 拿到输出，或从 `r.error` 拿到错误。

两次调用之间，每个模块保留一个**实例**，即拥有独立内存的运行副本。因此，存放在 `static` 中的数据（例如缓存）会从一次调用保留到下一次。**陷阱**（trap）指函数因 panic、栈溢出或内存超出 256 MiB 上限而中止。发生陷阱或超过 2 秒截止时间时，只有这次调用以错误结束，Shell 照常运行。随后，服务会在下次调用前为该模块换上一个新实例，`static` 中的数据也随之重置。

## 编写函数

### 客体 crate

`octosense-guest` 是客体（guest，即模块内部的 Rust 代码）一侧的辅助 crate，替你实现 [ABI](#abi)。它不在 crates.io 上，请从 OctoSense 仓库的 [`apps/wasmlab/guest/octosense-guest`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/wasmlab/guest/octosense-guest) 复制。它采用 Apache-2.0 许可，只依赖 `serde_json`。

| 项目 | 作用 |
| --- | --- |
| `octosense_guest::abi!()` | 导出 `octo_alloc` 和 `octo_free`。每个 crate 调用一次。 |
| `octosense_guest::export!(f)` | 以 `f` 为名导出 `fn f(&[u8]) -> Result<Vec<u8>, String>`：字节进，字节出。 |
| `octosense_guest::export_json!(f)` | 以 `f` 为名导出 `fn f(In) -> Result<Out, String>`，其中 `In: Deserialize`、`Out: Serialize`。它把输入按 JSON 解析成 `In`，再把 `Out` 写成 JSON。输入解析失败时返回 `the input is not what f takes: <reason>`。 |
| `octosense_guest::log(line)` | 把 `line` 写进 Shell 的日志，格式为 `wasm <app id>: <line>`。原生构建会把它打印到 stderr。 |
| panic 钩子（由 `export!` 和 `export_json!` 安装） | 在调用因陷阱结束之前，把 panic 信息记为一行 `panic: …`。 |

### 最小示例

下面的步骤为 `tools/octo new` 在 `~/apps/my-app` 中创建的应用添加函数（见 [QUICKSTART §3](QUICKSTART.zh-CN.md#3-创建应用)），示例中应用的 id 是 `dev.example.texttools`。把 Rust crate 放在 `bundle/` 旁边，只有构建出的模块进入应用包：

```text
~/apps/my-app/
  bundle/
    fns/my_functions.wasm   构建出的模块
  functions/                你的 Rust crate；不放进应用包
    Cargo.toml
    src/lib.rs
  octosense-guest/          从 OctoSense 复制而来；不放进应用包
```

1. 按 [PUBLISHING §4.2](PUBLISHING.zh-CN.md#42-在桌面端-shell-中安装并打开应用) 的说明把 OctoSense 克隆到 `<workspace>`，然后复制客体 crate：

   ```sh
   cp -R <workspace>/OctoSense/apps/wasmlab/guest/octosense-guest ~/apps/my-app/
   ```

2. 编写 `functions/Cargo.toml`。`cdylib` 生成 `.wasm` 文件；`rlib` 让其他 Rust 代码（例如集成测试）以原生方式链接同一批函数。release profile 沿用 Wasm Lab 的设置（见[构建](#构建)）。

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

3. 编写 `functions/src/lib.rs`。其中的两个函数改编自 Wasm Lab：`md_to_html` 接收文本、返回文本，`rank` 接收并返回 JSON。

   ```rust
   //! 应用自己的函数，为 wasm32-unknown-unknown 构建。
   use serde::{Deserialize, Serialize};

   // 导出 octo_alloc 和 octo_free。每个 crate 调用一次。
   octosense_guest::abi!();

   /// 文本进，文本出：把 CommonMark 转成 HTML。
   pub fn md_to_html(input: &[u8]) -> Result<Vec<u8>, String> {
       let text = std::str::from_utf8(input).map_err(|_| "the text is not UTF-8".to_string())?;
       let mut html = String::new();
       pulldown_cmark::html::push_html(&mut html, pulldown_cmark::Parser::new(text));
       Ok(html.into_bytes())
   }
   octosense_guest::export!(md_to_html);

   /// JSON 进，JSON 出：找出包含查询词的条目，匹配位置越靠前排得越前。
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

4. 在 `~/apps/my-app` 中以原生方式测试逻辑：

   ```sh
   cargo test --manifest-path functions/Cargo.toml
   ```

   输出中包含 `test tests::the_earliest_match_comes_first ... ok`。

### 沙盒禁止的操作

函数只能接触自己的内存和 `octo.log`。Rust 标准库照样能为 `wasm32-unknown-unknown` 编译，但下列调用会失败，或者什么也不做：

| 你的代码 | 结果 | 替代做法 |
| --- | --- | --- |
| 读取时钟：`Instant::now()`、`SystemTime::now()` | panic，信息为 `time not implemented on this platform`，调用因此触发陷阱。 | 把时间放在输入中传入。Splash 有 `time_now()`。 |
| 直接调用 `getrandom`，或经由启用默认特性的 `rand` 等 crate 获取随机字节 | `getrandom` 无法为 `wasm32-unknown-unknown` 构建。启用它的 JavaScript 后端后，它会导入 `wasm-bindgen` 的函数，模块因此无法加载。 | 把随机种子放在输入中传入。Splash 有 `random_u32()`。 |
| 用 `std::fs` 打开文件 | 返回 `operation not supported on this platform`。 | 在 Splash 中读取文件，再把内容传入函数。 |
| 用 `std::net` 打开套接字 | 返回 `operation not supported on this platform`。 | 在 Splash 中用 `net` 取回数据，再传入函数。 |
| 用 `std::thread::spawn` 启动线程 | panic，调用因此触发陷阱。`thread::Builder::spawn` 返回 `operation not supported on this platform`。 | 在单个线程上完成计算。 |
| 读取环境变量 | `std::env::var` 返回 `Err(NotPresent)`。 | 把设置放在输入中传入。 |
| 用 `println!` 或 `eprintln!` 输出 | 没有任何输出。 | 调用 `octosense_guest::log`。 |
| 导入宿主函数，例如 WASI 或 `wasm-bindgen` 的函数 | 模块无法加载：`the module imports <name>; only octo.log is provided`。 | 为 `wasm32-unknown-unknown` 构建，并去掉带来这个导入的依赖。 |

### 上限

| 上限 | 数值 | 函数超出时 |
| --- | --- | --- |
| 每次调用的时间 | 2 秒（按墙钟时间计），每 10 毫秒检查一次 | `the call ran past its deadline` |
| 每个实例的内存 | 256 MiB | `the function trapped: memory over its cap (…)` |
| 每次调用的 Wasm 栈 | 512 KiB | `the function trapped: wasm trap: call stack exhausted` |
| 每次调用的输入和输出 | 各 16 MiB | `<n> bytes is over the input/output limit` |
| 模块大小 | 8 MiB | `<file>: the module is <n> bytes, over the limit` |
| 日志 | 每次调用 64 行，每行截断到 1,024 字节 | 多出的行会丢弃。 |

App Hub 还为每个宿主服务请求设了上限。来自脚本的调用会先碰到这些上限，然后才轮到 16 MiB 的上限：

| 上限 | 数值 | 调用超出时 |
| --- | --- | --- |
| 脚本请求的参数 | 1 MiB 的 JSON | `the request's arguments exceed 1 MiB` |
| 返回结果 | 4 MiB 的 JSON | `the service's answer exceeds 4 MiB` |
| 等待结果的时间，包括排在本应用先前调用之后的排队时间 | 60 秒 | `the host service timed out` |
| 每个应用同时等待的调用 | 32 个 | `too many host requests are waiting; try again when some have answered` |

来源：OctoSense `crates/wasm-host/src/lib.rs` 中的 `Limits::default()`（`wasm` 服务使用这组上限），以及 App Hub 的 `crates/appstore/src/services.rs`。

### ABI

客体 crate 实现了这套 ABI。不用这个 crate 编写模块，或者排查模块的问题时，需要了解它。模块是 WebAssembly 核心模块，不是组件。它包含下列导出，以及最多一个导入：

| 名称 | 类别 | 类型 | 作用 |
| --- | --- | --- | --- |
| `memory` | 导出 | 内存 | 模块的线性内存。 |
| `octo_alloc` | 导出 | `(len: i32) -> i32` | 为输入分配 `len` 字节，返回其地址。 |
| `octo_free` | 导出 | `(ptr: i32, len: i32)` | 释放 `octo_alloc` 返回的缓冲区，或存放输出的缓冲区。 |
| 每个函数 | 导出 | `(ptr: i32, len: i32) -> i64` | 读取 `ptr` 处的 `len` 字节输入，返回 `(out_ptr << 32) \| out_len`，即输出缓冲区（由函数自行分配）的地址和长度；这个缓冲区以状态字节开头（见下面第 4 步）。 |
| `octo.log` | 导入，可选 | `(ptr: i32, len: i32)` | 向 Shell 的日志写一行。 |

Shell 分四步完成一次调用：

1. 调用 `octo_alloc(len)`，把输入写到返回的地址。
2. 用这个地址和长度调用函数，再用 `octo_free` 释放输入。
3. 复制输出缓冲区，再用 `octo_free` 释放它。
4. 读取缓冲区的第一个字节，即状态字节：`0` 表示其余部分是输出，`1` 表示其余部分是 UTF-8 编码的错误文本。其他值或空缓冲区都按陷阱处理。

类型为 `(i32, i32) -> i64` 的导出都是应用可以调用的函数，其他类型的导出 Shell 一概忽略。模块缺少 `memory`、`octo_alloc` 或 `octo_free`，或者除 `octo.log` 外还有其他导入，都无法加载。

## 构建

在 `~/apps/my-app` 中运行下列命令。

1. 确认 Rust 已安装 WebAssembly 目标平台：

   ```sh
   rustup target list --installed
   ```

   列表中应有 `wasm32-unknown-unknown`。如果没有，添加它（**未验证**）：

   ```sh
   rustup target add wasm32-unknown-unknown
   ```

2. 构建模块：

   ```sh
   cargo build --manifest-path functions/Cargo.toml --release --target wasm32-unknown-unknown
   ```

   构建成功时，最后一行是 ``Finished `release` profile [optimized] target(s) in …``。如果构建在编译 `getrandom` 时失败，说明某个依赖需要系统随机数：去掉这个依赖，或者关闭引入 `getrandom` 的特性（见[沙盒禁止的操作](#沙盒禁止的操作)）。

3. 把模块复制进应用包。Cargo 用包名给文件命名，并把 `-` 换成 `_`：

   ```sh
   mkdir -p bundle/fns
   cp functions/target/wasm32-unknown-unknown/release/my_functions.wasm bundle/fns/
   ```

准入检查要求应用包遵守下列规则：

| 规则 | 要求 |
| --- | --- |
| 路径 | `fns/<name>.wasm`，直接放在 `fns/` 下 |
| 名称 | 1 到 64 个字符，取自 `[a-z0-9_-]` |
| 模块数 | 每个应用包最多 8 个 |
| 应用包大小 | 文件合计 8 MiB（8,388,608 字节），不计 `manifest.json` |

此外，函数名在应用的所有模块中必须唯一：两个模块导出同名函数时，`wasm` 服务会拒绝加载。

示例沿用 Wasm Lab 的 release profile：

| 设置 | 效果 |
| --- | --- |
| `opt-level = 3` | 按速度优化。 |
| `lto = true`、`codegen-units = 1` | 把所有 crate 当作一个整体来优化。 |
| `panic = "abort"` | panic 立即触发陷阱，不生成栈展开代码。 |
| `strip = true` | 去掉符号和调试信息。 |

用 Rust 1.97 构建时，示例模块在这些设置下是 372,358 字节，在 Cargo 默认的 release profile 下是 430,973 字节。

`tools/octo new` 写入的 `.gitignore` 已包含 `target/`，所以构建输出不会进入 Git。把 `bundle/fns/my_functions.wasm` 和 `functions/`、复制来的 `octosense-guest/` 一起 commit，构建 crate 需要它们。

## 声明并调用

### 声明能力

1. 在 `bundle/manifest.json` 中申请 `wasm`：

   ```json
   "capabilities": ["wasm"]
   ```

   `wasm` 不需要 `requires` 标记，它是一项普通能力。商店向用户显示的说明是“Run its own sandboxed functions on this device”。

2. 在你的 App Flow 检出目录中写入摘要并检查应用包：

   ```sh
   tools/octo check ~/apps/my-app/bundle
   ```

   应用包的其余部分齐全时（见 [QUICKSTART §8](QUICKSTART.zh-CN.md#8-检查应用包)），检查会通过，只有未签名的警告，`grants:` 行列出 `wasm`。以 `dev.example.texttools` 应用为例，输出如下：

   ```text
   dev.example.texttools 0.1.0 — PASSED
     [warning] publisher-signature: unsigned: accountability rests on the hub alone
     grants: capabilities {"wasm"}, hosts {}, storage none, agent none
   ```

   如果准入检查拒绝模块，按检查结果指出的问题修复：

   | 检查结果 | 修复方法 |
   | --- | --- |
   | `[refused] functions: the bundle carries 1 WebAssembly module(s) but does not declare the wasm capability` | 申请 `wasm`（第 1 步）。 |
   | `[refused] functions: the bundle carries 9 WebAssembly modules, over the 8 it may` | 把函数合并到 8 个以内的模块中。 |
   | `[refused] contents-invalid (fns/MyFunctions.wasm): a function module is named fns/<name>.wasm, the name [a-z0-9_-] and at most 64 characters` | 给文件改名，并让它直接位于 `fns/` 下。 |
   | `[refused] contents-invalid (lib/x.wasm): a WebAssembly module belongs in fns/, as fns/<name>.wasm` | 把文件移到 `fns/` 中。 |
   | `[refused] contents-invalid (fns/x.wasm): not a WebAssembly core module (magic and version 1)` | 改用针对 `wasm32-unknown-unknown` 构建的核心模块，不要用组件。 |
   | `[warning] functions: the bundle declares the wasm capability but carries no fns/*.wasm` | 把模块复制到 `bundle/fns/`（见[构建](#构建)第 3 步）。 |
   | `hub: the bundle exceeds the size limit` | 把应用包的文件压到 8 MiB 以内。 |

### 从 Splash 调用

调用 `wasm.<function>`，其中 `<function>` 是导出的函数名：

```splash
host.request("wasm.rank", {query: "cal" items: ["Local calls" "Calendar" "Mail"]}, fn(r){
    if r.is_ok { ranked = r.data.ranked } else { note = r.error }
})

host.request("wasm.md_to_html", "# Hello", fn(r){
    if r.is_ok { html = r.data.text } else { note = r.error }
})
```

这里 `r.data.ranked` 是 `["Calendar", "Local calls"]`，`r.data.text` 是 `<h1>Hello</h1>` 加一个换行符。服务按下表转换参数和输出：

| 脚本传入 | 函数收到 |
| --- | --- |
| 字符串 | 字符串的 UTF-8 字节。用 `export!` 实现函数。 |
| 其他值：对象、列表、数字或布尔值 | 该值的 JSON。用 `export_json!` 实现函数。 |

| 函数返回 | `r.data` |
| --- | --- |
| 有效的 JSON | 就是这个值 |
| 其他内容 | `{text: <按 UTF-8 解码的输出>}` |

要传入二进制数据（例如 `fs.read_bytes` 读出的图像），直接传字节列表。它以数字组成的 JSON 数组送到函数，`export_json!` 会把它读成 `Vec<u8>`。每个字节最多占 4 个字符，所以 1 MiB 的参数上限至少能容纳 256 KiB 二进制数据（**未验证**）。

### 从 Agent 工具调用

附带 `tools.json` 的应用会得到自己的 Agent，因此还要声明 `agent` 块（见 [AI-SERVICES § 应用自己的 Agent](AI-SERVICES.zh-CN.md#应用自己的-agent)）。在 `bundle/tools.json` 的 `tools` 数组中加入下面这一项。它的 `host_method` 把工具映射到 `rank` 函数：

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

工具名以应用的命名空间开头，命名空间就是应用 id 的最后一段：`dev.example.texttools` 的命名空间是 `texttools`。App Hub 的 [`tools.json` 规则](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md#toolsjson应用的工具)照常适用，但其中四条对 `wasm.<function>` 另有规定：

| 规则 | 其他 `host_method` 工具 | `wasm.<function>` |
| --- | --- | --- |
| 方法 | App Hub 审核过的列表中的方法 | 应用导出的任何函数：`wasm.` 之后只有一段，由 `[a-z0-9_]` 组成 |
| 最低 `risk` | 每个方法各有规定 | 没有；只做计算的函数用 `read` 即可 |
| `private_data` | 必须为 `true` | 不要求：函数只看得到自己的参数 |
| 能力 | 该方法的能力族 | `wasm` |

工具的参数是 JSON 对象，因此要用 `export_json!` 实现函数。函数也要返回对象，并声明对象类型的 `output_schema`，因为 OctoSense 的 Agent 内核 octos 只接受对象 schema。`rank` 因此返回 `{"ranked": […]}`，而不是单独一个列表。Agent 收到的是 `{"ok": true, "data": <output>}`，或 `{"ok": false, "error": {"kind": "app_error", "message": <error>}}`。

准入检查拒绝时会说明依据的规则，例如 `[refused] tools: texttools.rank: host_method "wasm.rank" requires the declared "wasm" service capability`。

### 查看加载结果

用 `{}` 调用 `wasm.functions`，可以知道宿主能不能运行函数，以及加载了哪些函数。在没有 `wasm` 服务的宿主上，这次调用会返回 `no service answers "wasm" on this device`。`runtime.list` 和 `runtime.describe` 不会列出 `wasm` 的方法。`wasm.functions` 的返回结果包含：

| 字段 | 内容 |
| --- | --- |
| `functions` | 应用的函数名。 |
| `modules` | 每个模块文件一项：`file`、`bytes`、`load_ms`、`from_cache`（编译好的代码是否来自缓存）、`memory_bytes`，以及 `renewed`（陷阱或超时后换上的新实例数）。 |
| `stats` | 每个已调用过的函数一项：`calls`、`errors`、`mean_us` 和 `max_us`。 |

不要把函数命名为 `functions`：`wasm.functions` 永远不会调用它。

### 应用看到的错误

| `r.error` | 原因 | 修复方法 |
| --- | --- | --- |
| `this app was not granted "wasm", which "wasm.rank" needs` | 清单没有申请 `wasm`。 | 在 `capabilities` 中加入 `wasm`。 |
| `no service answers "wasm" on this device` | 宿主没有 `wasm` 服务：`card-host`，或未启用 `wasm-lab` 的 OctoSense 构建。 | 在启用了 `wasm-lab` 的 Shell 中测试（见[测试](#测试)）。 |
| `<app id> has no function "rank"` | 没有模块导出这个名称。 | 与 `wasm.functions` 列出的名称核对。 |
| `<app id>'s bundle has no fns directory` | 应用申请了 `wasm`，却没有带模块。 | 加入 `fns/<name>.wasm`。 |
| `<file>: the module imports <name>; only octo.log is provided` | 某个依赖导入了 WASI 或 `wasm-bindgen` 的函数。 | 为 `wasm32-unknown-unknown` 构建，并去掉这个依赖。 |
| `<file>: the module does not export <name>` | crate 没有调用 `octosense_guest::abi!()`。 | 在 crate 中调用一次。 |
| `<file>: <function> is exported by another module too` | 两个模块导出了同名函数。 | 给其中一个函数改名。 |
| `the input is not what rank takes: <reason>` | 参数与函数的输入类型不符。 | 修正参数或类型。 |
| 函数自己的错误文本，例如 `the query is empty` | 函数返回了 `Err`。 | 在脚本中处理。 |
| `the call ran past its deadline`、`the function trapped: …` | 调用超出了[上限](#上限)，或触犯了[沙盒的限制](#沙盒禁止的操作)。 | 如果是 panic，到 Shell 的日志中查看 `panic: …` 一行；如果超时，减少每次调用的工作量。 |

服务会一并加载一个应用的全部模块。只要有一个模块加载失败，每次调用都返回这个模块的错误；下次调用时，服务会重新加载。

## 测试

第 3 到第 9 步在启用 `wasm-lab` 构建的 Shell 中测试函数，因此都**未验证**。

1. 用 `tools/octo run` 在 `card-host` 中运行应用（见 [QUICKSTART §4](QUICKSTART.zh-CN.md#4-在桌面上运行)）。`card-host` 会接受应用包，但它没有 `wasm` 服务，每次调用都返回 `no service answers "wasm" on this device`。用它检查布局，以及缺少函数时应用显示什么。
2. 按 [PUBLISHING §4.2](PUBLISHING.zh-CN.md#42-在桌面端-shell-中安装并打开应用) 的说明，准备好[最小示例](#最小示例)第 1 步克隆的 OctoSense。
3. 以 `wasm-lab` 特性构建并启动桌面端 Shell，系统应用改用 `desktop/system-apps-wasm-lab.json`，即默认的系统应用加上 Wasm Lab：

   ```sh
   cd <workspace>/OctoSense
   OCTOSENSE_SYSTEM_APPS="$PWD/desktop/system-apps-wasm-lab.json" \
     cargo run --release -p octosense --features wasm-lab
   ```

4. 从 dock 或 **Apps** 菜单打开 **Wasm Lab**。每张卡片调用一个函数，显示结果和往返耗时。模块加载时，Shell 的日志会出现类似这样的一行：`wasm os.wasmlab: wasmlab.wasm (433 KiB) compiled in … ms: find_slots, fuzzy_rank, md_to_html, rogue, text_diff`。
5. 点击 **Misbehave** 下的每个按钮。死循环、无休止的内存分配、panic 和失控递归都以错误结束，下一次调用照常返回结果。
6. 按 [PUBLISHING §4.1](PUBLISHING.zh-CN.md#41-发布到本地镜像) 的说明，把你自己的应用发布到本地镜像。
7. 退出 Shell，再用 [PUBLISHING §4.2](PUBLISHING.zh-CN.md#42-在桌面端-shell-中安装并打开应用) 中的命令加上 `--features wasm-lab` 重新启动它。
8. 从 dock 中的 **App Hub** 安装并打开你的应用。
9. 安装新版本后重启 Shell：正在运行的 Shell 会继续使用应用的旧函数。

Agent 工具（无论是 Wasm Lab 的还是你的应用的）还需要 octos 内核（按[桌面端 README](https://github.com/OctoSense-org/OctoSense/blob/main/desktop/README.zh-CN.md#构建与运行) 的说明部署）和一个 AI 提供商。手机 Shell（即 Home）同样有 `wasm-lab` 特性和 `phone/system-apps-wasm-lab.json` 文件；构建方法见 OctoSense 的[手机端 README](https://github.com/OctoSense-org/OctoSense/blob/main/phone/README.zh-CN.md)（**未验证**）。

## 未决事项

OctoSense 的 [ADR 0011](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0011-apps-own-functions-in-webassembly.zh-CN.md) 记录了这项设计。下列事项尚未解决：

| 事项 | 状态 |
| --- | --- |
| 每个应用的 CPU 和内存预算 | 尚未实现。上限按调用、按实例计算，所以一个应用可以用连续调用占满一个核心，也可以在它的 8 个模块中各用 256 MiB。App Hub 已判定超时的调用，仍会在该应用的工作线程里继续运行。 |
| 为手机预先编译模块 | 尚未实现。第一次调用会编译每个模块：ADR 0011 在桌面上测得 27–33 毫秒，在中端 Android 手机上测得 378–421 毫秒；之后在同一部手机上从缓存加载需要 5–11 毫秒。 |
| 用真实模型调用 Agent 工具 | 未验证。OctoSense 的测试通过 Shell 的工具执行器调用 Wasm Lab 的工具，没有用到模型。 |
| iOS | 尚未实现。iOS 不允许应用使用 JIT，Wasmtime 将只能改用自带的 Pulley 解释器，速度约为 Cranelift 的 1/17。iOS 也不允许应用下载原生代码，因此商店应用的函数在 iOS 上同样无法预先编译。 |
| OpenHarmony | 未验证。它的 JIT 策略未知。 |
| Shell 运行期间更新应用 | 尚未实现。Shell 重启之前，一直使用旧函数。 |
| 带类型的接口（组件模型和 WIT）、时钟或随机数之类的宿主导入，以及确定性的限制（fuel） | 尚未决定。`octo.log` 之外的任何宿主导入都会是一项新能力。 |

## 另请参阅

- [HOST-API-V1](HOST-API-V1.zh-CN.md)：设备权限和 `location.get`。
- [CAPABILITIES § 宿主服务](CAPABILITIES.zh-CN.md#宿主服务)：`wasm` 与其他宿主服务。
- App Hub 的 [PUBLISHING § 检查结果](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md#检查结果)和 [§ 把工具映射到共享服务](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md#把工具映射到共享服务host_method)：准入检查对 `fns/` 和 `wasm.<function>` 的规则。
- App Hub 的 [SUBMITTING § Hub 目前做不到的事](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md#hub-目前做不到的事)：商店应用目前做不到的事，包括附带原生 Rust 代码。
- [Wasm Lab](https://github.com/OctoSense-org/OctoSense/tree/main/apps/wasmlab)：参考应用，含它的客体 crate 和 `build.sh`。
