# 日历：一份日历，两台设备

[English](README.md) | 简体中文

一个 iOS 风格的日历，用 [image-to-appcard 流程](../../flows/image-to-card/README.zh-CN.md) 构建，
背后是一个真实的同步服务：一个 SQLite 数据库、一份有序的操作日志、
一个每个客户端都会重放的 reducer。“Alex · Phone”（应用画面）和
“Sam · Desktop”（桌面服务卡片）向同一台服务器提交操作，并收敛到相同的状态；
冲突由服务器拒绝，撤销会指明它回退的确切步骤，一台设备上的改动会被*提供*给另一台设备，
而绝不会直接推到它的屏幕上。

## 这里有什么

| 部分 | 文件 | 作用 |
| --- | --- | --- |
| 故事板 | `scripts/design.py`、`source/storyboard.html`、`source/atlas.png`、`source/prompt.txt` | 10 个场景共用一个逻辑布局（406 × 776）。atlas 是它在 2× 下的确定性 Chromium 渲染（`source/render_atlas.mjs`），并作为 provider 记录；没有使用任何图像模型。 |
| 流水线 | `image-to-appcard-flow.json`、`scripts/author_calendar.py`、`scripts/build_calendar.py`、`cards/calendar-01..10`、`artwork/`、`wizard/card-bundle/` | intake 冻结 atlas；author 脚本从同一份规格写出 contract、经评审的语义映射和服务动作；compile 产出 L0 场景；extract 产出 4 个独立服务卡片；bundle 导出浏览器包。 |
| 日历核心 | `service/calendar_core.py`、`wizard/core.mjs`、`service/fixtures/ops.json` | 领域 reducer 写了两份：Python 版供服务器和原生运行时使用，JS 版供浏览器使用。一个共享的双设备 fixture 把两者固定在相同的判定和相同的状态摘要上。 |
| 同步服务器 | `server/calendar_server.py`、`service/sync_client.py` | 仅用标准库的 HTTP + SQLite（WAL）。`POST /v1/ops` 应用一个操作并记录判定；`GET /v1/ops?since=N&wait=S` 长轮询日志；`GET /v1/stream` 以 server-sent events 提供同样内容；`GET /v1/state` 是带摘要的快照。使用 Bearer token，CORS 来源显式列出。 |
| 会话 | `wizard/service.mjs`、`wizard/sync.mjs`、`wizard/copy.mjs`、`route_test.json` | 向导会话（`createSession`、`getView`、`activateControl`、`nextUpdate`、`goBack`、`restart`），加上面向服务器的 `applyRecords`/`adoptSnapshot`，以及 fetch / 长轮询传输层。 |
| 预览 | `wizard/preview/`、`scripts/demo.sh` | 由真实会话、同步客户端和服务器驱动的故事板 HTML 渲染，可以同时观察两个浏览器标签页同步。它不是原生渲染器。 |
| **原生应用** | `native/`（crate `octosense-calendar`） | 作为进程内 OctoSense AppModule 的日历。每个画面都是运行时根据日历状态（任意月份、任意事件）构建的场景，编译为 L0 并挂载为原生 Makepad Kit 控件，与经评审的故事板卡片使用相同的 lowering。自带服务日志的副本（`model.rs`，reducer 的第三个孪生实现）和同步链路（`sync.rs`）。在 macOS 和 Android 上的 OctoSense Shell 中运行。 |

场景：01 月视图 · 02 日视图 · 03 事件 · 04 新建事件 · 05 桌面 *Calendar · Synced* ·
06 桌面 *Invitation from Sam* · 07 带冲突的时间选择器 · 08 日历列表 ·
09 桌面 *Sync · Up to date* · 10 桌面 *Calendar · Removed*。提取出的卡片：
`calendar-synced-05`、`calendar-invite-06`、`calendar-removed-10`（归属 `calendar`）
以及 `calendar-sync-status-09`（归属 `sync`）。共 64 个原生控件，中英双语。

## 服务规则

- 一个操作是 `{id, actor, action, payload}`；动作包括：`event.create`、`event.update`、
  `event.delete`、`event.restore`、`invite.respond`、`calendar.set_visible`、`device.sync`。
- 服务器按到达顺序应用操作，并记录每个判定。重放完全相同的操作 id 不产生效果；
  用同一个 id 提交不同内容会被拒绝。
- 一个所有者，一条时间线：与任何现存事件重叠的事件会被拒绝（`conflict:<id>`），
  创建、更新和恢复时都如此。时间选择器会在服务器拒绝之前先禁用这些时段。
- 撤销就是具名的逆操作：撤销一次创建会删除该事件；撤销一次删除会以原内容恢复同一个事件。
  其他任何东西都不会被触动。
- 接受邀请会添加一个事件并回复 Sam；第二次接受永远不会产生重复；
  拒绝只移除我们这边的副本，Sam 的邀请不受影响。
- 隐藏日历只改变可见性。`device.sync` 记录一次同步，不改变任何内容。
- 远端改动绝不会移动画面。会话把它作为 `view.nextUpdate` 提供
  （“Show 1 change from Alex · Phone”），用户请求时才显示已同步卡片。
  如果服务器拒绝了本设备自己的操作，乐观更新会被回滚，并留下提示。

## 运行

```sh
export BEAUTY_PYTHON="$PWD/flows/image-lib/.venv/bin/python"   # from the repository root
bash tools/image-to-appcard-flow.sh run \
  --project "$PWD/examples/calendar" --manifest "$PWD/examples/calendar/image-to-appcard-flow.json" \
  --stages intake,semantic,compile,bundle,service-test --node /path/to/node
```

从规格重新构建（新的 atlas → 新的 intake；请先删除 `cards/`、`artwork/`、`pipeline-output/`，
因为 intake 会拒绝在已有输出目录中出现变更过的 atlas）：

```sh
cd examples/calendar
"$BEAUTY_PYTHON" scripts/design.py                         # → source/storyboard.html
node source/render_atlas.mjs source/storyboard.html source/atlas.png 3488 4950
"$BEAUTY_PYTHON" scripts/author_calendar.py                # intake, prepare, contracts, compile
"$BEAUTY_PYTHON" scripts/build_calendar.py                 # extract cards, export the bundle
```

在浏览器中观察两台设备同步：

```sh
cd examples/calendar && PYTHON="$BEAUTY_PYTHON" bash scripts/demo.sh
# prints the phone tab (?device=alex-phone) and desktop tab (?device=sam-desktop) URLs
```

测试（也是 `checks.service-test` 运行的内容）：

```sh
"$BEAUTY_PYTHON" -m unittest discover -s service -p 'test_*.py'   # reducer + fixture (9)
"$BEAUTY_PYTHON" -m unittest discover -s server  -p 'test_*.py'   # live server: convergence, verdicts, restart, auth, SSE (7)
node --test wizard/service.test.mjs wizard/core.test.mjs          # routes × 2 locales, invariants, rollback (24)
BEAUTY_PYTHON=… node --test wizard/sync.test.mjs                  # two JS sessions against a spawned Python server (2)
node wizard/preview/smoke.mjs                                     # two Chromium tabs against a live server, screenshots
```

## 原生应用

`native/` 是为早期原生 OctoSense Shell 编写的 Rust `AppModule`
（feature `app-calendar`）。该 Shell 已归档，原生客户端现在位于
[OctoSense `apps/appcard`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/appcard)；本模块
作为参考实现保留，不由本仓库的 CI 构建。画面包括：月视图（任意月份、按日历区分的圆点、
今天 / 选中的圆环、选中日的列表）、日时间线（按小时分行，重叠事件平分宽度，当前时间线）、
事件详情、编辑器（标题 / 地点 / 备注字段、全天、开始 / 结束选择器并禁用冲突时段、
日历选择、提醒）、日历列表（显示 / 隐藏，EN/中文）、收件箱
（带 Accept/Maybe/Decline 的邀请，来自另一台设备的改动）、同步状态。
操作经过与服务器相同的 reducer；冲突在发送之前就被拒绝；服务器的拒绝会回滚改动，
并列在 Sync 画面上。

配置（桌面上用环境变量；Android 上用 `--es makepad.APP_CONFIG`，键为
`calendar_server`、`calendar_token`、`calendar_device`、`calendar_locale`）：
`CALENDAR_SERVER`、`CALENDAR_TOKEN`（例如 `$(cat examples/calendar/runtime/calendar.token)`）、
`CALENDAR_DEVICE`、`CALENDAR_LOCALE`。`native/desktop-apps.json` 是该 Shell 的
`--apps` 选项读取的模块列表。

没有 `CALENDAR_SERVER` 时，应用在设备本地运行，使用围绕真实“今天”排布的演示 fixture。
单元测试：`cargo test --manifest-path examples/calendar/native/Cargo.toml`
（reducer fixture 与 Python/JS 孪生实现一致、通过共享 L0 流水线的场景 lowering、
每个画面都能渲染、服务器记录的确认 / 回滚）。

## 状态与局限

- 已运行并通过的流水线阶段：intake、prepare、semantic、compile、extract、bundle、
  service-test（回执位于 `pipeline-output/runs/`）。未运行：capture、gate、wasm、
  integrate、web-test、hosted-test；目前还没有原生抓取或视觉验收，
  网站所需的 WASM 包也尚未构建。
- atlas 是编写出来的，而不是生成的：contract 与参考图在构造上就一致，
  因此 intake 测量是一致性检查，而不是对未知图像做 OCR。
- 服务器是本地单进程服务，使用共享的 Bearer token：适合一个家庭和测试使用，
  不支持多租户。actor 身份是客户端自己声明的设备 id；生产部署需要先认证设备，
  再信任 `actor`。
- 浏览器预览绘制的是故事板 HTML；原生应用挂载的是真实的 Kit 控件。原生场景在运行时构建，
  而不是来自经评审的故事板卡片，因此流水线的 capture/gate 阶段目前还未覆盖它们。
