# 快速入门：构建、运行并发布 OctoSense 脚本应用

[English](QUICKSTART.md) | 简体中文

未注明中文版的链接指向英文文档。

从一个空目录出发，沿一条路径走到一个能通过 App Hub 准入检查的应用包。每条命令都在 macOS（Apple 芯片）上运行过，标注为**未验证**的除外。引用的输出均为真实输出，其中的本地路径和进程号省略为 `…`。

```text
1 前置条件 → 2 构建 hub + card-host → 3 octo new → 4 octo run → 5 迭代修改
→ 6 能力 → 7 常见的坑 → 8 octo check → 9 在手机上运行 → 10 发布
```

## 1. 前置条件

| 平台 | 状态 |
| --- | --- |
| Apple 芯片上的 macOS | 已验证：本页所有命令都在这个平台上运行过。 |
| Windows | 在当前 `main` 上未验证（由 [App Hub#41](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/41) 跟踪），CI 在该平台上运行的 `tools/test_*.py` 测试除外。通过 Python 运行 `tools/octo`（§2），并且不要让 Git 改动应用包的换行符（§3）。 |
| Linux | 未验证，CI 在该平台上运行的 `tools/test_*.py` 测试除外。有报告称，在软件渲染（llvmpipe、WSL）下截帧（`/g`、`tools/octo shot`）会超时。 |

你需要：

- **Rust**（stable，通过 rustup 安装）。`cargo` 位于 `~/.cargo/bin`，请把这个目录加入 `PATH`（`export PATH=$HOME/.cargo/bin:$PATH`）。
- **Python 3.9+**，供 `tools/octo` 和 `setup-native.py` 使用，不需要任何第三方包。macOS 自带的 `/usr/bin/python3` 即可。
- **Git。**
- **约 3 GB 磁盘空间：** 克隆占 2 GB（其中 1.5 GB 是本仓库，大部分是设计证据；只构建应用的话，`git clone --depth 1` 就够了），构建占 1 GB。试用桌面端 Shell（[PUBLISHING §4](PUBLISHING.zh-CN.md#4-在本地演练商店流程)）还要再多约 1 GB，另加它自身构建所占的空间。
- **图形会话**，供 `card-host` 使用。即使 `--hidden` 让窗口不出现在屏幕上，`card-host` 也会渲染一个真实的 412x892 点窗口（§4a）。
- **App Hub 及其同级源码**，放在同一个工作区目录中：

  ```text
  <workspace>/
    OctoScript-App-Design-Flow/   本仓库
    OctoSense-App-Hub/            hub、card-host、appstore
    makepad/                      OctoSense-org/makepad
    octoscript-makepad/           OctoSense-org/Octoscript-Makepad
    octoscript/                   OctoSense-org/Octoscript
  ```

  App Hub 的 `Cargo.toml` 把它的 Makepad 和 OctoScript 依赖固定指向这几个同级路径（`../makepad`、`../octoscript-makepad`、`../octoscript`）。`setup-native.py` 按 [native-runtime.lock.json](../native-runtime.lock.json) 选定的版本，克隆这三个运行时同级仓库（目录名为小写，如上所示）。它的选项见 [NATIVE-WORKSPACE](NATIVE-WORKSPACE.md)。

创建工作区：

```sh
mkdir octosense-ws && cd octosense-ws
git clone https://github.com/OctoSense-org/OctoScript-App-Design-Flow.git
git clone https://github.com/OctoSense-org/OctoSense-App-Hub.git
cd OctoScript-App-Design-Flow
python3 tools/setup-native.py           # 在本仓库旁克隆 makepad、octoscript 和 octoscript-makepad
python3 tools/setup-native.py --check   # 通过时以退出码 0 退出，并输出锁定的版本
```

`setup-native.py` 需要运行 20 到 30 秒。如果之后 `--check` 失败，运行 `python3 tools/setup-native.py --update`，把没有本地改动的同级仓库切换到锁定的版本。

App Hub 和本仓库都请使用 `main`。运行时为 OctoScript-Makepad `aa80f72c`，它锁定了 Makepad `68d1f4ec` 和 OctoScript `2e37d9e6`。

## 2. 构建 `hub` 和 `card-host`

```sh
cd <workspace>/OctoSense-App-Hub
cargo build --release -p octosense-card-host -p octosense-app-hub
```

构建成功时，输出以 `Finished release profile …` 结尾。生成的程序位于 `target/release/`（或 `$CARGO_TARGET_DIR/release/`）：`hub`（准入检查）和 `card-host`（运行单个应用包的宿主）。在 Windows 上，文件名是 `hub.exe` 和 `card-host.exe`。

如果构建失败并提示 `no variant … TextInputStateQuery`，请看[构建 `card-host` 时报 `TextInputStateQuery` 错误](#构建-card-host-时报-textinputstatequery-错误)。

然后在本仓库中运行：

```sh
export OCTOSENSE_APP_HUB=<workspace>/OctoSense-App-Hub   # App Hub 位于同级目录时可省略
tools/octo doctor
```

`doctor` 依次在以下位置查找 `hub` 和 `card-host`：`$OCTO_HUB` 和 `$OCTO_CARD_HOST`；然后是 `$OCTOSENSE_APP_HUB/target/release`、`$CARGO_TARGET_DIR/release`、`$OCTOSENSE_APP_HUB/../target/release`、同级的 `../OctoSense-App-Hub/target/release`、`../target/release`；最后是 `PATH`。它会排除 GitHub 那个同名但无关的 `hub` CLI。两个程序都找到时，最后输出：

```text
ready: tools/octo new <dir> --platform <target> && tools/octo run <dir>/bundle
```

有缺失项时，它输出一行 `[fail]`、查找过的每个位置，以及修复用的命令。

**Windows（未验证）。** Windows 不会按 shebang 运行这个脚本，所以每条 `tools/octo` 命令都要通过 Python 运行。在上面列出的每个目录中，`tools/octo` 都先查找 `hub.exe` 和 `card-host.exe`，再查找不带 `.exe` 的文件名：

```powershell
python tools/octo doctor
```

如果程序在别的位置，把 `$env:OCTO_HUB` 和 `$env:OCTO_CARD_HOST` 设为它们的完整路径。CI 会在 Windows 上测试这套查找逻辑；命令本身在 Windows 上未验证。

## 3. 创建应用

```sh
tools/octo new ~/apps/my-app --platform macos --id my-notes --name "My Notes"
```

`new` 复制 [templates/script-app](../templates/script-app/README.zh-CN.md)（`bundle/`、`AGENTS.md` 及导入它的 `CLAUDE.md` 和 `GEMINI.md`、`.gitignore`），设置清单中的 `id` 和 `name` 以及 `main.splash` 中的标题标签，把 `--platform` 的值写入商店信息，并为应用包写入摘要：

```text
created …/my-app
  id my-notes, name 'My Notes', version 0.1.0, bundle stamped
  target platforms: macos; verify each before publishing
```

`--platform` 是必填项，你要在哪些平台上运行应用，就为每个平台写一次：`macos`、`windows`、`linux`、`android`、`ios`、`openharmony` 或 `web`。在 Mac 上用 `card-host` 运行，测试的是 `macos`。商店信息会在商店中声明这些平台，所以发布之前，只保留你实际测试过的平台，并由人确认这一声明。不加这个选项时，`new` 会停止，并输出 `tools/octo new: error: the following arguments are required: --platform`。

请慎重选择 id：

- 长度为 1 到 64 个字符，只能用 `[a-z0-9.-]`，不能以 `.` 开头，也不能包含 `..`。`new` 会检查这一点。
- 不能以 `os.` 开头，这个前缀保留给系统应用。除非传入 `--system`，否则 `new` 会拒绝这样的 id。
- id 本身及其最后一段都不能是宿主保留的名字，例如 `notes`、`weather`、`calculator`、`browser`、`terminal` 或 `system`。`new` 在创建任何文件之前就会拒绝这样的 id：`octo: id 'com.example.notes' uses reserved native/host namespace 'notes'; choose an app-specific name`。如果之后把 id 改成这样的名字，准入检查会拒绝它（§8）。全部保留名见 App Hub 的 [准入检查的规则](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.zh-CN.md#准入检查的规则)。

把 `~/apps/my-app` 建成独立的 Git 仓库，并禁止 Git 改写应用包的字节。应用包的摘要覆盖每一个字节，如果检出时转换了换行符（Windows 上设置了 `core.autocrlf=true` 的 Git 就会这样），摘要就会失效：

```sh
cd ~/apps/my-app
git init
printf 'bundle/** -text\n' > .gitattributes
```

## 4. 在桌面上运行

```sh
tools/octo run ~/apps/my-app/bundle --port 8141            # 前台运行；按 Ctrl-C 退出
tools/octo run ~/apps/my-app/bundle --port 8141 --detach   # 后台运行；应用已准入并完成绘制后返回
```

`run` 在 App Hub 目录中启动 `card-host --bundle <bundle> --app-data <app>/.local-state --allow-unsigned --stamp`，并设置 `MAKEPAD_REMOTE=8141`。`--detach` 会输出：

```text
[makepad-remote] listening on 127.0.0.1:8141 pid=… app=card-host …
… card-host: my-notes 0.1.0 admitted — capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
ready: first frame drawn
pid …  log …/my-app/.local-state/card-host.log
drive it:  curl -s 127.0.0.1:8141/snap   |   tools/octo shot 8141 <out.png>   |   curl -s 127.0.0.1:8141/quit
```

- `run` 先检查端口是否空闲。如果该端口上已有程序在响应，它以退出码 1 退出，输出 `port 8141 is already taken by card-host pid …`，并给出退出那个实例的命令（`curl -s 127.0.0.1:8141/quit`）。
- `--detach` 在两件事都完成后才返回：应用的控件已完成布局（`/snap` 能列出它们及其文本），并且此后已完整画出一帧。紧接着发送的 `shot`、点击或 `/t` 都会作用在已完成的界面上。
- `run` 会传入 `--stamp`，所以 `card-host` 每次启动都会重写清单中的摘要，改动不用另外执行 `hub stamp` 就能运行。`tools/octo run --no-stamp` 不传这个参数，此时 `card-host` 会拒绝字节有变化的应用包。`--no-stamp` 是 `tools/octo` 的参数，不是 `card-host` 的参数（`card-host --help` 会列出它自己的参数）。
- `--system` 按系统应用的上限准入 `os.*` 系统应用。
- 应用的文件存放在它的 jail 中，即私有数据目录 `<app>/.local-state/<id>/`。
- 在日志中查找 `admitted`，以及 `[SPLASH] eval:` 之后的错误（脚本错误会输出在这里；见 [SCRIPT-API](SCRIPT-API.md#errors-and-the-log)）。按下面这些错误格式搜索，不要搜索“error”这个词：即使运行正常，Makepad 的 `[ui-hang]` 诊断信息也会提到 Metal 的 `MTLCompilerError`。

  ```sh
  grep -nE '\[E\]|splash:[0-9]+:|refused|on_render closure failed|callback error' <app>/.local-state/card-host.log
  ```

通过 HTTP 操作应用。所有路由都是 GET；坐标为窗口点，y 轴向下：

| 命令 | 作用 |
| --- | --- |
| `curl -s 127.0.0.1:8141/snap` | 列出控件及其矩形和文本：`{"s":[{"i":id,"ty":type,"r":[x,y,w,h],"t":text}]}`；用 `?q=` 过滤 |
| `curl -s 127.0.0.1:8141/d` | 以文本形式输出整棵控件树 |
| `curl -s "127.0.0.1:8141/click?x=150&y=140&wait=1"` | 发送一次真实点击（`wait=1`：画完下一帧后再响应） |
| `curl -s "127.0.0.1:8141/t?t=Buy%20milk&wait=1"` | 向获得焦点的输入框输入文字 |
| `curl -s "127.0.0.1:8141/k?k=down&c=ReturnKey"` | 发送一个按键事件 |
| `curl -s "127.0.0.1:8141/log?n=50"` | 返回最近的日志行 |
| `curl -s 127.0.0.1:8141/s` | 返回远程控制桥的状态，包括应用名称和进程号 |
| `tools/octo shot 8141 out.png` | 把窗口保存为 PNG（`/g?raw=1`） |
| `curl -s 127.0.0.1:8141/quit` | 退出；最后一定要调用它（或调用 `/gq`：截下所有窗口后退出） |

操作技巧：

- `/t` 向当前获得焦点的控件输入文字。点击按钮会让 `TextInput` 失去焦点，所以发送下一个 `/t` 之前，要再点一下输入框。要清空输入框，每个字符发送一次 `/k?k=down&c=Backspace`。
- `?q=` 也会匹配 `Splash` 控件本身，它的文本就是你的整个 `main.splash`；请按类型过滤结果（`"ty":"Label"`），或根据矩形判断。
- `tools/octo shot` 先等应用的控件出现，再反复截帧，直到相邻两帧完全相同（最多等待 `--settle` 指定的时长，默认 2 秒），所以不会保存画了一半的首帧。即便如此，仍要逐张查看 PNG。
- 窗口大小为 412x892 点；在 Retina 屏幕的 Mac 上，`/g?raw=1` 按 2 倍分辨率截图：把截图的像素坐标除以 2，就得到点击坐标。截图顶部包含 `card-host` 的标题栏（macOS 上为 32 点）。标题栏是同一窗口中的控件，所以点击坐标也从同一个顶边算起：不要减去标题栏的高度。

在模板应用中，`/snap` 会显示标题标签 `"t":"My Notes"`。按下面的步骤完整操作一遍：

1. 点击输入框，然后发送 `/t?t=Buy%20milk`。
2. 点击 **Add**。应用把 `["Buy milk"]` 写入 `.local-state/my-notes/notes.json`，并画出这一行。
3. 点击这一行。应用会删除它。
4. 重启应用。已保存的笔记会重新加载。

`on_render` 生成的控件与其他控件一样出现在 `/snap` 和 `/d` 中，所以按 `/snap` 给出的矩形点击即可。应用稍后才生成的内容（来自 `start_timeout` 或网络响应）要等绘制之后才会出现：请轮询 `/snap?q=` 等待它，不要只读一次 `/snap`。

### 4a. 无头模式：不占屏幕，同时测试多个应用

Makepad 有隐藏窗口模式，这里称为无头（headless）模式。应用仍然需要 §1 中的图形会话，但窗口**从不显示、也不抢焦点**，上面介绍的远程控制桥（`/snap`、`/click`、`/t`、`/g` 截图）也完全照常工作。所有自动化检查都应使用这种模式：编码 Agent 不会占用你的屏幕或键盘焦点，你还可以同时测试多个应用，或同一应用的多个副本。

```sh
tools/octo run ~/apps/my-app/bundle     --port 8161 --hidden --detach
tools/octo run ~/apps/second-app/bundle --port 8162 --hidden --detach
curl -s "127.0.0.1:8161/snap?q=Button"             # 每个应用在自己的端口上响应
curl -s "127.0.0.1:8162/click?x=X&y=Y&wait=1"      # X、Y：/snap 给出的某个矩形的中心点
tools/octo shot 8161 first.png && tools/octo shot 8162 second.png
curl -s 127.0.0.1:8161/quit; curl -s 127.0.0.1:8162/quit
```

`--hidden` 会为 `card-host` 设置 `MAKEPAD_HIDE_WINDOWS=1`；所有 Makepad 应用都支持这个变量，包括 OctoSense 的 Shell。同时运行多个应用时，遵守以下规则：

- **每个应用一个端口。** 为每个实例指定自己的 `--port`；端口已有程序占用时，`run` 会拒绝运行，并指出占用端口的应用。
- **每个副本一个 `--app-data`。** 两个不同的应用包本来就有各自的 jail（`<app>/.local-state`）。同一个应用包运行两份时，需要用 `--app-data` 把它们的存储和日志分开。
- **隐藏时也能截图。** 截图由应用自己渲染，即使屏幕上什么都没有，截图也是完整的。每张都要查看。

已在 macOS 上验证：两个隐藏窗口的应用同时接受点击，各自保持了自己的状态，两张截图也都正确。

### 4b. 用 `makepad_test` 编写脚本化 UI 测试

要做可重复的回归测试，锁定版本的 Makepad 自带一个 Rust 测试框架：`libs/makepad_test`（[README](https://github.com/OctoSense-org/makepad/blob/main/libs/makepad_test/README.md)、[GUIDE](https://github.com/OctoSense-org/makepad/blob/main/libs/makepad_test/GUIDE.md)）。它会自己构建并启动应用（默认隐藏窗口），通过同一个远程控制桥操作应用，并在测试失败时保存截图、控件树和日志。要测试应用包，让它指向 App Hub 的 `card-host`，并把应用包作为应用参数传入：

```rust
// tests/ui.rs，所在的小 crate 声明了
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

这个示例测试的是一个分摊小费的应用，它有一个 `20%` 按钮和一个 `tip_line` 标签；请按你的应用修改选择器。用 `cargo test --release --test ui` 运行。设置 `MAKEPAD_TEST_PARALLEL=1` 可以并发运行测试（每个测试一个隐藏应用），设置 `MAKEPAD_TEST_VISIBLE=1` 则可以观看测试过程。用你在页面中声明的控件作为目标（`Selector::id` 对应 `name := …`，也可以用按钮文字）；`on_render` 中生成的控件同样在测试框架的快照里。

**在当前锁定的版本上未验证：** 这个示例曾在 macOS 上与另一个应用并行运行并通过，当时用的是较早的 App Hub 和 Makepad。它的 API 与当前锁定的 Makepad 版本一致。

## 5. 迭代修改

1. 修改 `bundle/main.splash`。语言说明见 [SCRIPT-API](SCRIPT-API.md)。
2. 运行 `curl -s 127.0.0.1:8141/quit`，再重新运行 `tools/octo run … --detach`。重启时会重新读取应用包，并重新写入摘要。
3. 运行 `tools/octo shot 8141 /tmp/now.png`，然后打开这张 PNG。
4. 如果画面不对，用 grep 搜索日志（§4），并修复第一个错误。

`.local-state/` 会在多次运行之间保留应用数据；要测试首次启动，删除这个目录即可。

## 6. 添加能力

在 `bundle/manifest.json` 中只添加界面实际用到的能力：

```json
"capabilities": ["storage", "net"],
"network": { "hosts": ["api.open-meteo.com"] }
```

`main.splash` 中提到的每个 `https://` 主机都要列入 `network.hosts`。声明了 `images` 或 `web` 时，准入检查接受任何 `https://` 主机，但在运行时，未列出的主机只能提供图片（`images`）或网页视图中的页面（`web`）；`net` 仍然只能访问列出的主机。纯 `http://` 一律不允许。没有 `storage`，应用就完全没有存储：准入检查的 `grants:` 行会显示 `storage none`。[CAPABILITIES](CAPABILITIES.zh-CN.md) 说明每项能力解锁什么、用户会看到什么；[HOST-SERVICES](HOST-SERVICES.zh-CN.md) 介绍 Mail 等服务。

**已连接账户。** 要使用用户的 GitHub 或 Google 账户，像参考应用那样声明 `auth`、对应提供商的能力族（`github`、`gmail` 或 `gcalendar`）和 `storage.accounts: true`；如果只需识别用户身份、不读取其数据，只声明 `auth` 就够了。登录由宿主完成，宿主给应用的是连接句柄，绝不是令牌。这些服务只在 OctoSense 桌面端 `desktop-v0.1.0-beta.2` 或更新版本中运行。登录还需要提供商注册信息：beta.2 没有内置任何注册信息，所以由宿主的运维人员在 `oauth/clients.json` 中提供（[CAPABILITIES § 限制](CAPABILITIES.zh-CN.md#限制)）。`card-host` 会返回 `no service answers "…" on this device`。完整示例见 [examples/connected-apps](../examples/connected-apps/README.zh-CN.md)。

**AI。** 在 OctoSense 的 Shell 中，隔离运行的应用可以调用 `model.complete`；用户允许该应用的 Agent 之后，还可以调用 4 个 `octos.*` 方法。在 `card-host` 中，这类调用一律返回 `no service answers "…" on this device`。请让应用在没有这些服务时也完整可用。[AI-SERVICES](AI-SERVICES.zh-CN.md) 列出了已有和计划中的功能，并给出一个经过验证、能处理“不可用”状态的调用。

## 7. 最费时间的坑

### `main.splash` 方面

完整列表见 [SCRIPT-API](SCRIPT-API.md#gotchas)。

- 十六进制颜色中只要有 `e` 紧挨着数字，就要写成 `#x` 形式，如 `#x1e1e2e`。所有颜色都写成 `#x` 形式也没有问题。
- 用 `for i in n` 循环（0..n-1）；没有 `range()`。
- 在 `on_render` 中，写成 `if list.len() == 0 { EmptyLabel } for i in list.len() { Row }`，**不要**写成 `if … {…} else for …`。用 `else for` 测试这个模板时，空分支什么都没画，屏幕上还残留着旧的行。
- 在 `card-host` 中，带 `show_bg: true` 的 `View` 不绘制背景，无论它一开始就可见还是之后才显示；需要填充背景的容器时，请用 `SolidView` 或 `RoundedView`。
- `ButtonFlat` 不能包含 `Label` 子控件；可点击的行请用 `GestureView{on_tap: |x, y| …}`。
- 准入检查会拒绝密码和一次性验证码输入框。机密信息只在宿主服务的面板中输入。

### 应用包与 Git 方面

- **保留 id。** `tools/octo new` 只检查它创建时用的 id。如果之后把 id 改成 `com.example.notes`，准入检查会拒绝它，因为最后一段 `notes` 是保留名（§3）。
- **`.DS_Store`。** Finder 会把它写进你打开过的文件夹，而准入检查会拒绝任何扩展名未知的文件。检查之前先删除它：`find ~/apps/my-app/bundle -name .DS_Store -delete`。
- **换行符。** 如果 Git 检出时转换了换行符，字节就会改变，摘要随之失效。请 commit §3 中的 `.gitattributes`。
- **字体。** 卡片套件的 `font_src` 只能引用一种内置字体：`makepad_widgets:resources/Inter.ttf`；其他字体都要作为文件放进应用包（[App Hub#75](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/75)）。应用包内 `.txt` 或 `.md` 文件（例如字体许可证）中的 URL，准入检查同样会拒绝。
- **大小。** 应用包不能超过 8 MiB（8,388,608 字节）。

## 8. 检查应用包

```sh
tools/octo shot 8141 ~/apps/my-app/bundle/screenshots/01-main.png   # 先把应用操作到真实状态
curl -s 127.0.0.1:8141/quit
tools/octo check ~/apps/my-app/bundle
```

`check` 先运行 `hub stamp`，再运行 `hub check --allow-unsigned`，检查不通过时返回非零退出码。如果在 `shot` 之前运行 `check`（例如对刚复制出来的模板），准入检查会拒绝这个应用包，因为模板的商店信息有意引用了 `screenshots/01-main.png`：

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

有了第一条命令截取的截图，检查就会通过（绝不要用占位图片代替）：

```text
my-notes 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
```

在人工为应用包签名之前，出现未签名警告是正常的。在人工填写发布者字段之前，占位提示会一直存在。

要检查版本是否已经发布过，加上 App Hub 的签名目录：`tools/octo check <bundle> --catalog <workspace>/OctoSense-App-Hub/catalog.json`。如果版本号已经用过，准入检查会拒绝并输出 `[refused] version: version 0.1.0 of <id> is already published; publish a new version`。

`check` 会先为未签名的应用包重新写入摘要。如果你在最后一次 `check` 之后又修改了应用包，却没有重新运行就 commit，commit 中的摘要就是过期的：审核人员直接运行 `hub check` 时，会以 `[refused] digest` 拒绝它。每次 commit 之前，都把 `tools/octo check` 作为最后一步；提交之前，在发布 tag 的全新克隆上直接运行 `hub check`（[SUBMITTING §6](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md#6-冻结并验证发布)）。

## 9. 在 OctoSense 手机上运行

目前的情况：

- **无法把任意应用包侧载到普通 OctoSense 手机上。** 手机商店读取内置的 Hub 地址（`DEFAULT_HUB`，即 `raw.githubusercontent.com/OctoSense-org/OctoSense-App-Hub/main/`），并且只信任编译进构建的信任锚（App Hub 的根公钥）。`OCTOSENSE_HUB` 和 `OCTOSENSE_HUB_ANCHOR`（镜像目录或 URL，及其信任锚）是环境变量，Android 启动器不会设置它们；也没有找到在设备上设置它们的选项。**在设备上未验证。**
- **最接近真实情况的路径在桌面端：** 用你自己的一次性信任锚把应用发布到本地签名目录，再用 App Hub 的商店安装；这个商店运行的安装代码与手机上的相同（[PUBLISHING §4](PUBLISHING.zh-CN.md#4-在本地演练商店流程)）。OctoSense 桌面端 Shell 同样读取 `OCTOSENSE_HUB` 和 `OCTOSENSE_HUB_ANCHOR`；它的商店会从这个签名目录安装你的应用，并在 Shell 的 Card runner 中打开。
- **第一方应用**作为系统应用进入手机：应用包位于 [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps)，列在 Shell 的 `system-apps.json` 中（手机上是 OctoSense 的 `phone/system-apps.json`），由 App Hub 的 `crates/app-hub-app/build.rs` 打包，再经过 Home 或 ROM 构建。这条路径用于 OctoSense 维护的 `os.*` 应用，不用于商店应用。
- **连接账户的应用**（`auth`）无法安装到手机上：目前没有任何已发布的手机版本接受 `auth` 能力。
- **发布之后**，你的应用会通过签名目录出现在每台手机的商店中。

Android 版 `card-host` 不编译远程控制桥。在手机上，请用 OctoSense 测试构建中的 App Studio 工具操作应用（[MODEL-VALIDATION](MODEL-VALIDATION.zh-CN.md#选择测试方式)），而不是 `tools/octo`。

## 10. 发布

[PUBLISHING](PUBLISHING.zh-CN.md) 介绍如何把应用包从这里推进到待签名状态：定稿清单和商店信息、截取真实截图、通过准入检查、回答审核问题，以及本地商店演练。之后由人工按照[向 App Hub 提交应用](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md)签名、打 tag 并提交。`tools/octo package-help` 会输出检查表。

## 故障排查

| 现象 | 原因与修复 |
| --- | --- |
| 构建停在 `octosense-appstore`，并提示 `no variant … TextInputStateQuery` | 见[构建 `card-host` 时报 `TextInputStateQuery` 错误](#构建-card-host-时报-textinputstatequery-错误)。 |
| 找不到 `cargo` | `export PATH=$HOME/.cargo/bin:$PATH`（rustup 把它安装在这里）。 |
| 构建在 `path = "../makepad/..."` 依赖处失败 | 同级仓库缺失或版本不对：在本仓库中运行 `python3 tools/setup-native.py`，然后用 `--check` 检查。 |
| `doctor`：`[fail] hub` 或 `card-host` | 构建它们（§2）。如果 `hub` 指向的是 GitHub 的 `hub` CLI，`doctor` 会指出来；请设置 `OCTO_HUB` / `OCTO_CARD_HOST` 或 `CARGO_TARGET_DIR`。 |
| Windows：`tools/octo` 无法启动 | 以 `python tools/octo …` 的形式运行（§2）。 |
| Windows：`doctor` 找不到 `hub.exe` | 先构建（§2）。如果它不在 `doctor` 列出的目录中，把 `OCTO_HUB` 和 `OCTO_CARD_HOST` 设为对应 `.exe` 的路径。 |
| `new`：`the following arguments are required: --platform` | 传入 `--platform macos`，或你要测试的每个平台（§3）。 |
| `new`：`id '…' uses reserved native/host namespace '…'` | 换一个最后一段不是保留名的 id（§3）。 |
| `run`：`port 8141 is already taken by card-host pid …` | 之前的实例仍占用着该端口。运行消息中给出的 `curl -s 127.0.0.1:8141/quit`，或换一个 `--port`。 |
| 点击、输入或修改似乎都不起作用 | 某个处理函数失败了（搜索日志，见 §4）；或者你没有用 `tools/octo run` 启动应用，操作的是该端口上一个较旧的实例（`curl -s 127.0.0.1:8141/s` 会显示它的进程号）。 |
| `shot` 提示 `still changing after 2s` | 应用在持续播放动画；PNG 是最后一帧。查看这张图，或传入更长的 `--settle`。 |
| 在 Linux 上 `shot` 或 `/g?raw=1` 超时 | 有报告称，在软件渲染（llvmpipe、WSL）下截帧会超时。Linux 未验证；请在 macOS 上截图。绝不要根据 `/snap` 重画截图。 |
| 按钮上不显示文字 | `ButtonFlat` 的默认文字是为深色主题准备的白色；请设置 `draw_text +: {color: …}`（[SCRIPT-API § Gotchas](SCRIPT-API.md#gotchas)）。 |
| 数字显示为 `NaN` | `"".to_f64()` 和非数字文本得到的是 NaN，而不是 nil；请用 `if v >= 0` 判断（[SCRIPT-API § Data and strings](SCRIPT-API.md#data-and-strings)）。 |
| 输入文字后出现 `widget has no uid` / `widget '<id>' not found in tree` | 运行时早于 Makepad `d0a9def5`：在这些版本中，`TextInput` 的 `on_change` 无法通过 `ui` 读取同一个输入框。运行 `python3 tools/setup-native.py --update`，然后重新构建 `card-host`。 |
| `variable net not found in scope` | 清单缺少 `net`，或没有 `network.hosts`（§6）。 |
| `this app may not reach <url>` | 该主机不在 `network.hosts` 中（须完全一致，且为小写）。 |
| `no service answers "…" on this device` | `card-host` 没有宿主服务，出现这条消息是正常的；请在 OctoSense Shell 中试用应用（[HOST-SERVICES](HOST-SERVICES.zh-CN.md)）。 |
| `check`：`screenshots/01-main.png is named by the listing but is not in the bundle` | 截取真实截图（§8）；绝不要用占位图片。 |
| `check`：`[refused] listing: listing names no platforms` | 商店信息的 `platforms` 为空，原始模板就是这样。在 `listing.json` 中列出你测试过的平台，或用 `tools/octo new … --platform …` 创建应用（§3）。 |
| `check`：`[refused] identity: app id "…" ends in "…", which is reserved: …` | 修改 id 的最后一段（§3）。同样的检查结果还会在 `policy` 下再出现一次。 |
| `check`：`[refused] contents: .DS_Store has extension "", which a bundle may not hold` | 删除这个文件：`find <bundle> -name .DS_Store -delete`。其他扩展名未知的文件也必须移出 `bundle/`。 |
| `check`：`[refused] digest: the bundle hashes to …, the manifest claims …` | 上次写入摘要之后，字节发生了变化。未签名的应用包：再运行一次 `tools/octo check`。已签名的应用包：由人工重新写入摘要并签名。只在全新克隆上出现时：检出时转换了换行符（commit §3 中的 `.gitattributes`），或者 commit 中的摘要已过期（§8）。 |
| `check`：`[refused] assets: … contains https://…`（`.txt` 或 `.md` 文件） | 应用包中的文本文件不能包含 URL；删掉这些 URL，或把文件放在 `bundle/` 之外。 |
| `check`：`[refused] resource-invalid (…/font_src): not a portable bundle path: "makepad_widgets:resources/…"` | 内置字体只能用 `Inter.ttf`；把字体文件放进应用包（§7）。 |
| `hub: the bundle exceeds the size limit`，没有报告 | 应用包超过了 8 MiB。压缩或删除图片和字体。 |
| 对已签名的应用包运行 `check` 或 `hub scan`：`publisher key "…" is not registered with this hub` | 传入发布者公钥：`tools/octo check <bundle> --publisher-key <publisher-id>=<hex public key>`（`hub scan` 也可以用同一个参数）。 |
| `card-host: refused: no signature verifier is installed` | `card-host` 不运行已签名的应用包；请用未签名的副本测试，最后再签名。 |
| `hub scan … --packet build/review.json` 输出 `hub: build/review.json: No such file or directory (os error 2)` | `hub` 不会创建审核包所在的目录。先运行 `mkdir -p build`。 |
| `hub check --help` 输出 `hub: No such file or directory (os error 2)` | 你的 `hub` 比 App Hub 当前的 `main` 旧；在当前 `main` 中，`--help` 会输出用法。重新构建（§2），或不带参数运行 `hub`。 |
| 准入检查的其他拒绝 | 见 App Hub 的[常见拒绝原因及修复](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.zh-CN.md#常见拒绝原因及修复)。 |

### 构建 `card-host` 时报 `TextInputStateQuery` 错误

`cargo build --release -p octosense-card-host -p octosense-app-hub` 报错中止：

```text
error[E0599]: no variant, associated function, or constant named `TextInputStateQuery` found for enum `makepad_widgets::Event` in the current scope
   --> crates/appstore/src/services.rs:393:18
error: could not compile `octosense-appstore` (lib) due to 1 previous error
```

同一个错误也会让 [PUBLISHING §4](PUBLISHING.zh-CN.md#4-在本地演练商店流程) 中的 `appstore` 构建中止。`hub` 不使用 Makepad，单独构建仍能成功：`cargo build --release -p octosense-app-hub`。

更新 App Hub，然后严格按照 §2 只构建这两个包：

```sh
cd <workspace>/OctoSense-App-Hub
git pull
cargo build --release -p octosense-card-host -p octosense-app-hub
```

App Hub `main` 构建 `card-host` 时关闭了 `appstore` 的 `text-input-state-query` 特性，因此可以基于未打补丁的 Makepad 构建。如果你本地的 App Hub 早于这项改动，或者你构建的是 App Hub 的其他包或整个工作区，错误仍会出现：这些构建会开启该特性，需要 OctoSense 打过补丁的 Makepad。[PUBLISHING §4](PUBLISHING.zh-CN.md#4-在本地演练商店流程) 中的 `octosense-appstore-app` 构建就属于这一类；请按该节的说明构建。
