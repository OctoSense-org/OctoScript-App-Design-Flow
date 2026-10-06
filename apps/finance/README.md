# Finance

Source preservation checkpoint (2026-10-06): this is the historical native-module
integration. The current live Mail/Calendar demo ships in the unified
[OctoSense repository](https://github.com/OctoSense-org/OctoSense). Historical
`evidence/` captures stay local and are excluded from this source commit; run the
provided verifiers for new evidence. Device/provider and full native builds were
not rerun for this preservation checkpoint.

A native iOS Stocks-style Finance app in `Octosense-Service-AppCards/apps/finance/`, shared by OctoSense and OctoSense-mobile. The generated design atlas, native scene definitions, provider adapters, service cards and tests belong to this application.

**Status: native MVP; the A2App Yahoo chart path is verified on macOS; authenticated AllTick/Finnhub/Tushare acceptance remains pending. The installed Android preview predates this update.** No paid-provider subscription or API key is included. The native app starts with the A2App StockPlot market-data binding (Yahoo Finance, no API key). Fictional prices and stories are available only when Preview data is explicitly enabled. News providers still need their own keys.

## Run

Use the sibling Makepad and Octoscript-Makepad revisions in `native-runtime.lock.json`. The host-series API needed by this historical app is preserved in [makepad-stockplot.patch](runtime-patches/makepad-stockplot.patch). From the repository root, apply it once to the clean pinned Makepad checkout:

```sh
APPCARD_STOCK_PATCH="$PWD/apps/finance/runtime-patches/makepad-stockplot.patch"
git -C ../makepad apply --check "$APPCARD_STOCK_PATCH"
git -C ../makepad apply "$APPCARD_STOCK_PATCH"
```

The runtime setup uses a sibling `../makepad/`; adjust that checkout path if your configured native workspace is elsewhere. On an already patched checkout use `git apply --reverse --check` instead. Then, from this Finance directory:

```sh
cargo build --release -p octosense-finance --features standalone
./target/release/octosense-finance
```

Both host catalogs register `finance`, using `octosense_finance::FINANCE_MODULE`. It is enabled by `app-finance`, included in the default and `mobile-apps` feature sets, and uses module hosting by default. From either host checkout:

```sh
cargo build --release --no-default-features --features app-finance
```

The module accepts optional `symbol` (the canonical listing ID, e.g. `XHKG:00700`) and `card` (`finance.quote`, `finance.watchlist`, `finance.related-news`, `finance.market-brief`) open arguments. Module shutdown and foreground changes close its native WebView and cancel pending requests.

## Implemented

- Mixed US/HK/mainland watchlist, regional filters, add/remove/reorder, persistent order, and bilingual ticker/company search.
- Public provider directory: 10,926 imported records plus curated canonical entries, preserving HK leading zeros and distinct mainland exchanges. US venue is explicitly unspecified when absent from the directory. Directory membership does not imply feed access or confirm instrument classification.
- Windowed stock/news lists render at most 24 rows at once. The scroll extent covers all available records; scrolling mounts later rows. Provider news is bounded to 1,500 cached stories.
- Quote/details, native numeric sparklines and charts, five ranges, sample inspection, OHLC/previous close when available. Day change is separate from selected-range return. Fixture range changes keep the chart widget's identity.
- Company-related and regional news, deduplication, persistent saved stories, share/copy link, and continuous publisher reading in the platform WebView. A feed item without a canonical URL is read as attributed feed text; the app does not invent a publisher URL.
- Settings for dark/light appearance, English/Chinese interface labels, rising-price color and preview/live mode. Provider-key fields keep keys **only in memory for that session**.
- Native HTTPS requests, conservative queued request cadence, timeout/cancellation, separate provider errors, and cached live quotes/history/news across restarts. These requests run on the device; there is no Mac companion server.
- Escape/Android Back navigation, native text entry/focus restoration, touch-drag scrolling and WebView foreground lifecycle handling.

## Data providers and present limits

The adapters use documented interfaces:

| Provider | Role | Contract |
| --- | --- | --- |
| Yahoo Finance | Default A2App StockPlot chart and daily quote data | Shared `StockPlot { symbol, range }` request/cache |
| AllTick | Optional alternative quotes, daily statistics, history | `trade-tick`, `batch-kline`, `kline`; [official HTTP API](https://github.com/AllTick-Official/alltick-realtime-forex-crypto-stock-tick-finance-websocket-api/tree/main/http_interface) |
| Finnhub | English general/company news | `news`, `company-news`; [official client](https://github.com/Finnhub-Stock-API/finnhub-python) |
| Tushare | Chinese news | `news`; [official news interface](https://tushare.pro/document/2?doc_id=143) |

Quotes and charts load automatically through the same symbol/range binding as the A2App stock card. Open Settings to enable the explicit preview or configure optional AllTick/Finnhub/Tushare keys; use Connect & refresh to request fresh data. Optional authenticated provider requests use a ten-second queue interval to accommodate restrictive plans; the default StockPlot path shares the A2App request cache. Prices are not synthesized when access is absent. The AllTick free demo universe does not provide arbitrary mainland stocks. Its stock-history pagination and adjustment options are limited; available history depends on entitlement. Feed timestamps are retained; unreported delay is labeled unknown. Daily bars are matched using the exchange timezone, including US daylight saving time.

Market overview currently shows regional context and **watchlist movers**, not a full-market ranking or live benchmark index dashboard. Exchange holiday calendars and definitive open/closed indicators are not implemented. Automatic StockPlot chart ticks use the provider's exchange-local offset; the selected-point readout explicitly uses UTC. External preview/AllTick series use UTC ticks. Public-directory names are primarily Chinese outside the curated seed set. Full interface translation, news-language filtering, automatic refresh scheduling, encrypted key persistence, live chart latency acceptance, corporate-action validation and paid-provider coverage verification remain release work. Article images from feeds are not yet shown in native list rows.

Do not enter real keys into a process being inspected or captured by the development instrument: native password fields can still expose underlying values through developer inspection. Production use should use a private credential channel/platform secure storage or an owned authenticated backend. This version has no trade execution, portfolio accounting or investment advice.

## Image-to-AppCard pipeline

[The atlas](source/finance-atlas.png) contains twelve states of **one app**. Its original output is **1024×1536**, smaller than requested. The exact prompt, original bytes, hashes, measured crops and transforms are retained. Native scenes deliberately reflow this layout to 406×776; neither atlas pixel parity nor artwork fidelity is claimed.

`service/src/scenes.rs` is the shared scene author. Its CLI exports contracts for the image pipeline; the native runtime lowers the same scene tree through L0 Kit composition and Octoscript-Makepad. `service/src/frame.rs` adapts Mail's L0 Kit compiler. The stock card's list/detail/range/stat hierarchy and Matplot PlotView engine are reused, with multi-market identities replacing its US-only ticker assumptions. News remains source-attributed. Charts use declared numeric data, never generated chart pixels or SVG traces.

The following stages passed: **intake, semantic, compile, extract, bundle, service-test**. `service-cards/` contains the four extracted native subtrees. `service/src/cards.rs` selects those same subtrees against current application data for module/card consumers. Legacy Studio capture/gate, WASM publication and strict visual parity were not run.

To reproduce scene authoring and the existing output stages:

```sh
cargo build --release -p octosense-finance-service
./target/release/octosense-finance-service .
../../lab/image-to-appcard/.venv/bin/python scripts/author.py
BEAUTY_PYTHON="$PWD/../../lab/image-to-appcard/.venv/bin/python" \
  bash ../../tools/image-to-appcard-flow.sh run \
  --project "$PWD" --manifest "$PWD/image-to-appcard-flow.json" \
  --stages intake,semantic,compile,bundle,service-test
```

Extraction is immutable: its first output is `pipeline-output/service-cards`; choose a new output location in the manifest when reviewing a later extraction. The current Matplot revision uses `pipeline-output/intake-matplot` and `pipeline-output/service-cards-matplot`; the curated extracted cards are retained under `service-cards/`. The bundle adapter now distinguishes typed inline-HTML WebViews from image assets and retains the existing artwork provenance checks.

## Verification

```sh
cargo test --release -p octosense-finance-service
cargo build --release -p octosense-finance --features standalone
python3 scripts/verify_native.py
```

Native evidence (`evidence/native/report.json`, retained locally) records the binary hash, owned process IDs, app-owned Metal captures, WebKit document/scroll evidence and `/gq` cleanup. The fixture tests explicitly set `OCTOS_FINANCE_PREVIEW=1`; a normal fresh profile uses market data. The tests use Makepad's **built-in HTTP instrument**, a release executable and hidden native macOS windows. They do not use Studio or a software-rendered screenshot.

Checks cover chart range/inspection values and stable fixture widget identity, continuous typing, long-directory virtualization, watchlist reorder, bookmark/restart persistence, native WebView full-article scrolling, missing-key states, light/dark and Chinese settings. Service tests also exercise listing identity, quote parsing, daily returns, source attribution, empty reusable cards and preview/live isolation. Bundle regression tests cover typed inline HTML without weakening image provenance.

Both OctoSense hosts compiled with `--no-default-features --features app-finance` on macOS before the visual polish. The polished standalone native build passes the ten built-in instrument checks and thirteen service tests. A release arm64 APK is installed on the user-selected OnePlus 6 (Android 15); app-owned Adreno GPU captures verify the native Matplot detail screen. The Android build uses the previously validated mobile host plus Finance integration and the clean locked framework revisions, isolated from concurrent launcher/platform work. It has existing framework/build-tool warnings. See `evidence/android/report.json` for device scope and hashes. No iOS-device acceptance or authenticated AllTick/Finnhub/Tushare verification is claimed.

## Native stock rendering

Both the watchlist sparklines and the detail chart instantiate Makepad's built-in `makepad_widgets::matplot::stock_plot::StockPlot`, the same widget used by the original Stock AppCard in `app/app/src/app/plan/stock.rs`. Finance's `native/src/plot.rs` only binds data and appearance; it defines no widget and draws no chart primitives. The normal path sets only the market symbol and selected range for data binding, letting StockPlot fetch the full series. Quote statistics and range summaries read the same response cache, with day-change statistics taken only from the daily response. The widget's `set_series` API is used only in explicit preview mode or when an AllTick key selects the alternative provider. Its native line/area rendering, latest-price marker, grid, price/time ticks and selected-sample marker are used directly. Inspection follows StockPlot's sample-index spacing across exchange closures. There are no app-authored Y-axis or time-label rows around the widget, matching `a2app/apps/stock/app.md`. The widget's default symbol/range fetch behavior remains available to other apps.

The generic design compiler initially lowered `stockplot` to a minimal `makepad-plot::LinePlot`. The Finance native adapter now maps those declared numeric plot nodes to `mod.widgets.StockPlot`; native evidence records the concrete widget type and actual data rectangle. Range changes preserve the widget and refresh its selected chip color. The native header, compact rows, region segments and four icon tabs follow the generated reference hierarchy. Settings is in the header; Inter 400/600/700 and the bundled Noto Sans SC provide consistent Latin/Chinese typography. The mobile host's available height controls the scrolling region and bottom bar, without leaving a blank strip beside the app.

The pipeline compiler resolves `self:` fonts against an external application's `native/` directory and framework fonts against the pinned Makepad widgets resources, checking their exact bytes. This avoids validating a similarly named font from an unrelated gallery host.

## Android preview

Finance is linked into OctoSense-mobile as an AppModule. Build from a host checkout whose sibling Makepad and Octoscript-Makepad sources match the locked revisions; keep unrelated framework experiments out of that validation build. Use the existing Android SDK and the matching Makepad build tool:

```sh
# From OctoSense-mobile; SDK is the existing Makepad Android toolchain folder.
MAKEPAD_FORCE_DEBUGGABLE=1 ../makepad/target/release/cargo-makepad makepad android \
  --sdk-path="$SDK" --abi=aarch64 \
  --package-name=dev.makepad.octosense.financepreview \
  --app-label='OctoSense Finance' build -p octosense --release

# From this Finance application directory; select the intended phone explicitly.
python3 scripts/open_android.py --adb "$SDK/platform-tools/adb" \
  --serial YOUR_DEVICE_SERIAL --apk /absolute/path/to/octo_sensefinance.apk --capture --symbol XNAS:AAPL
```

The separate preview package opens Finance directly inside the mobile launcher. It does not change the default Home role. The user selected OnePlus 6 (`YOUR_DEVICE_SERIAL`) for this Finance run; the prior Robrix preference was OnePlus 6T (`YOUR_DEVICE_SERIAL`). An explicit serial is required. The open script refuses to replace a running Finance preview session.

The pinned Android backend does not expose the macOS HTTP instrument. For device visual checks, the launcher's existing capture hook reads back Finance's own GPU texture, without Studio or an OS screenshot. Allow at least twelve seconds after an interaction, then read the app-private capture:

```sh
"$SDK/platform-tools/adb" -s YOUR_DEVICE_SERIAL exec-out run-as \
  dev.makepad.octosense.financepreview cat files/finance-capture.png > finance-android.png
```

This timer-driven capture forces a redraw and does not establish spontaneous repaint latency. The capture APK is debuggable solely for reading this app-owned artifact; use fictional preview data during inspection. For a normal handoff, close the owned capture session and reopen without `--capture`. Android installation, visible rendering and interaction results must be recorded separately from APK compilation.

## Files and dependencies

- `source/`, `cards/`: generated design, references, semantic maps and compiled scenes.
- `service/`: data models, provider contracts, state, scene author and reusable card selection.
- `native/`: Makepad view/controller, native network/WebView adapters and AppModule.
- `service-cards/`: four extracted native L0 panels.
- `scripts/`, `evidence/`: directory refresh, authoring and direct-instrument checks.
- `runtime/`, `target/`, `pipeline-output/`: ignored local data/build/session output.

Locked framework revisions: Octoscript-Makepad `b1596d9c2cee6e80cca9d27b1b0c2d57b9d28dd8`, Makepad `d4502ef1e4d196d2829a07aa137740cb0581e9b4`, Octoscript `5430518683462eebb65b56b9b5d0e620006f04f4`. The workspace patch unifies Octoscript's transitive node-model dependency with the selected sibling Octoscript-Makepad checkout. The standalone workspace patches `makepad-widgets` and `makepad-app-module` to the sibling Makepad checkout, matching the hosts. That checkout adds host-supplied series, selected-sample and shared chart-URL APIs to the StockPlot widget; keep this framework change together with the Finance integration. Earlier Android evidence predates this direct StockPlot integration.

Code is Apache-2.0 under the repository license. Inter and Noto Sans SC remain under their included SIL Open Font Licenses. Provider terms govern use and redistribution of their data independently of this code license.
