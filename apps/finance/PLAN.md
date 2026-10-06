Implementation status: see [README.md](README.md) for the working native MVP, passed checks and remaining release work. The original feature plan follows.

# Finance app feature plan

Draft, 2026-09-16. Planning only: no generated atlas, implementation, provider
subscription or device deployment has been started. The user selected US,
Hong Kong and mainland China stocks for version 1. Retain ETF support where
the selected feeds cover it; do not reduce the first release to US-only.

Build an iOS Stocks-style application for following securities and reading the
news about them, hosted in OctoSense and OctoSense-mobile. The product name can
remain Finance while the main screen is titled Stocks. Use the shared locked
Octoscript-Makepad runtime and the existing AppCard pipeline.

## Version 1 experience

| Surface | Features and behavior |
| --- | --- |
| Watchlist | All / US / HK / CN filters, large title, persistent search, symbol/company name, latest price, signed daily change and native sparkline. Add, remove and reorder symbols; switch percentage/absolute change. Persist the list locally. Virtualize long lists. Business News appears below the watchlist with an action to open the complete feed. |
| Markets | US / HK / CN overview with market-session status, supported benchmark indices and movers. State the ranked universe explicitly: a watchlist or subscribed basket must not be labeled a market-wide ranking. Show unavailable index/market coverage honestly. |
| Search | Search by ticker and English/Chinese company or fund name; show exchange, currency and instrument type to distinguish listings. Debounce requests, cancel stale responses, and add/remove a result without losing the query. |
| Stock details | Expandable detail sheet/page with quote, session status, currency and quote timestamp. Native interactive line/area chart with 1D, 1W, 1M, 6M, YTD, 1Y and MAX where the selected feed supports them. Touch-and-drag inspection of time/price; unsupported history is explained. Scroll through open, previous close, high/low, volume, 52-week range, market cap and P/E where applicable and available. Company-related stories follow the statistics. |
| Relevant news | Separate views for a selected company, the watchlist and general business news. Show publisher, publication time, headline, permitted excerpt and thumbnail when supplied. Match provider security IDs/tags first, deduplicate syndicated stories, and offer Latest/Relevance sorting. Incrementally load older stories with an explicit end state when history is exhausted. Preserve scroll position. |
| Article reader | Open the publisher's original article in the platform WebView, with continuous scrolling, back navigation, share/open-in-browser and saved links. Preserve publisher login/paywall behavior. Provider excerpts do not imply that full article text is available to rehost. |
| Saved news | A reachable list of bookmarked stories, with publisher, saved/publication time, search, remove and reopen actions. Save links and permitted metadata; do not promise offline full articles. |
| Settings and resilience | System/light/dark appearance, English/Chinese interface, gain/loss color convention (including regional defaults), data source and refresh settings, timestamps and delay labels. Cached watchlists, quotes and permitted news metadata remain readable offline with a stale indicator. Loading, empty, partial, quota, retry and unavailable-data states are first-class UI. |

Apple's documented Stocks interaction model includes watchlists, interactive
charts and symbol-related stories; these are the behavioral reference, with an
original OctoSense visual implementation. Apple News/News+ distribution is not
part of this app. [Apple Stocks guide](https://support.apple.com/en-ph/guide/iphone/iph1ac0b1bc/ios),
[Apple business-news guide](https://support.apple.com/en-gb/guide/iphone/iph013530e8d/26/ios/26).

Version 2 candidates: multiple watchlists, price alerts, earnings/dividend
calendar, comparisons and a manual portfolio. Background alerts require a
separate reliable scheduling/push design. Brokerage login, trading, options,
full technical-analysis tooling and generated investment recommendations are
outside version 1. News summarization can be considered later, with source
links and a clear distinction between source facts and generated text.

## What we can reuse

- [Existing stock L0 card](../../docs/l0/stock.card): quote header, movers,
  selected-security/range contract, statistics and StockPlot composition.
- [Stock plan lowerer](../../app/app/src/app/plan/stock.rs): structured stock
  sections and runtime-owned values. Its current implementation explicitly
  emits a single view; it is not yet the proposed navigable Finance app.
- [Stock design prototype](../../lab/image-to-appcard/stock-05/page.card):
  measured image-to-native layout and chart mapping. Its digitized chart
  samples are design fixtures, not current or recovered market data.
- [News/market composition](../../tools/splash-research/templates/composition/news-market.card):
  source attribution, article links and host-bound news/quote sections.
- Shared native chart and list primitives, AppModule lifecycle, and the
  platform-reader pattern used by Mail.

Work required beyond reuse: persistent navigation/watchlist state, virtualized
lists, native chart scrubbing and stable range updates, provider-independent
numeric chart input, and company/watchlist news aggregation. The existing
Makepad StockPlot builds Yahoo URLs internally. Reuse its chart behavior or the
shared numeric plot primitives, but route new app data through a provider
adapter rather than embedding Yahoo fetching in every widget. Preserve chart
and list identity while applying data/range changes; an old state-template path
rebuilds the card and can lose scroll/focus.

Cross-market requirements are part of version 1: USD/HKD/CNY display,
exchange-local session status and holiday calendars, US daylight-saving changes,
HK/mainland lunch breaks, numeric symbols with leading zeros, and issuer-linked
but distinct A/H/US listings. Match stories through issuer identities and
verified English/Chinese aliases; do not merge prices for separate listings.
Include Shanghai, Shenzhen and Beijing in the coverage checklist. Missing
exchanges, ST stocks or other excluded securities must be disclosed in the
provider capability matrix, not silently presented as complete China coverage.

Create four reusable service-card recipes owned by this application:
`finance.quote`, `finance.watchlist`, `finance.related-news`, and
`finance.market-brief`. Each has typed data, source/as-of fields and scoped
actions such as open security, change range, add to watchlist or read story.
These are compact components of the same Finance application.

## Yahoo and alternative data sources

Yahoo's current public developer catalog does not list a supported Finance
market-data API. This is a finding from its published catalog, not a claim
that every Yahoo Finance endpoint is inaccessible.
[Yahoo API catalog](https://developer.yahoo.com/api/).

The current stock implementation uses Yahoo's web-facing `v8/finance/chart`
endpoint, with search and screener calls elsewhere in the shared runtime.
These are not a supported integration contract. The yfinance project says it
is unaffiliated with Yahoo and intended for research/education and personal
use. Yahoo Finance's own help page states that its supplied/displayed
information must not be redistributed.
[yfinance README](https://github.com/ranaroussi/yfinance/blob/main/README.md),
[Yahoo data-provider notice](https://help.yahoo.com/kb/finance/data-real-time-yahoo-finance-sln2310.html).

For all three selected markets, evaluate quote/history and news providers
separately. The user is comfortable with a practical free or paid API for the
first version; an enterprise feed is not a prerequisite. The working prototype
choice is AllTick for quotes/charts, with Finnhub and Tushare evaluated for
English and Chinese news respectively. No subscription has been purchased,
and live coverage has not yet been accepted.

As checked on 2026-09-16, AllTick lists Basic at 99 USDT/month for 100 selected
products, 60 requests/minute and one WebSocket connection. This fits an initial
watchlist, not arbitrary market-wide quote access. Its free tier has ten fixed
demo products; the China examples are indices rather than individual A-share
stocks. Free is sufficient for adapter/UI experiments, not the required
three-market stock acceptance. Stock historical data is described as the latest
500 K-lines, so range availability must follow the actual response.
The same pricing page prohibits redistribution by default; buying Basic does
not establish public-app display rights. This working choice is for personal
testing unless separate display terms are obtained.
[AllTick current pricing and usage notice](https://alltick.co/pricing).

| Candidate | Role and verified limits |
| --- | --- |
| AllTick | Candidate for a common quote/history adapter: official documentation describes US/HK/A-share REST and WebSocket data. Its A-share plan describes Shanghai/Shenzhen and explicitly excludes ST/*ST securities; Beijing coverage and public-display rights remain to be verified. The published free tier is a small demo universe, not full market coverage. |
| Twelve Data | Candidate for symbol/reference data and historical series. Its China exchange page lists Shanghai/Shenzhen as end-of-day data. This does not meet an intraday A-share requirement by itself. HK timing/entitlements also need confirmation. |
| Finnhub | Documented company/general-news and quote APIs; evaluate for US/English coverage. Chinese-language company-news coverage across HK/A-shares has not been established. |
| Tushare | Candidate for Chinese news and regional metadata/history. The news-flash endpoint requires separately enabled access. Its documented response has time, title, content and optional categories, without a canonical article URL or security-ID field. Company matching and publisher links therefore require additional sourcing; check publisher display rights and HK coverage. |

Sources: [AllTick plan guide](https://alltick.co/blog/how-to-choose-the-right-alltick-plan),
[Twelve Data China coverage](https://twelvedata.com/exchanges?country=China),
[Finnhub official client](https://github.com/Finnhub-Stock-API/finnhub-python),
[Tushare news documentation](https://tushare.pro/document/2?doc_id=143).

The recommended architecture uses exchange-specific provider routing behind one
application data model. The implementation evaluation should test representative
securities in all three regions, Chinese/English company-news matching, symbol
exclusions and quote timestamps before selecting paid plans. Real-time,
15-minute-delayed and end-of-day feeds are distinct product capabilities; never
label an end-of-day China feed as a delayed intraday feed.
For a news flash without a verified article URL, show the permitted attributed
text and omit the article action. Full-story browsing requires a source that
supplies canonical publisher links; do not invent links or ticker associations.

Alpha Vantage is another documented option. Its standard free allowance is
25 requests/day; it also advertises an exception for verified open-source or
educational projects. This exception requires verification and is not an
assumed entitlement for this app. Its support page places real-time and
15-minute-delayed US data in premium offerings.
[Alpha Vantage support](https://www.alphavantage.co/support/).

Keep Yahoo as an optional personal research adapter only if the chosen use is
permitted; it is not the proposed public-release data source. Use clearly
labeled fixtures for design and deterministic tests. No subscriptions or API
keys are required to review this feature plan or the later design images.

## Data and application architecture

`Provider adapters → normalized market/news records → Finance state/cache →
L0 recipes + native kit bindings → Octoscript-Makepad → AppModule hosts`.

- Normalize securities by exchange and instrument ID, not ticker alone.
  Existing short-uppercase ticker validation must be expanded for HK and
  mainland symbols in this first release. Do not confuse an ETF with its benchmark index.
- Quote records carry currency, trading session, exchange timezone, observation
  time and delay status. Daily change uses the preceding session's close;
  selected-range return is a distinct value. Keep split-adjustment semantics
  consistent between displayed history and calculations. Missing values render
  as unavailable rather than zero. Prices and direction never come from the
  image generator or an LLM.
- Use asynchronous, deduplicated requests, bounded caches, request cancellation
  and backoff. Quote cadence follows provider limits and market sessions; avoid
  background polling while the app is suspended. Request historical series
  when symbol/range changes, and refresh news less often than quotes.
- The phone connects over the internet independently of a Mac. A personal
  deployment can use a user-owned provider key stored in platform secure
  storage. A distributed app should keep shared provider secrets in an owned
  backend, with client authentication and caching; this does not imply a Mac
  tether or that a provider permits redistribution.
- Separate quote, chart and news errors. A news outage must not blank the
  watchlist. Local watchlist/order and saved links survive process restarts.

All application files belong under `Octosense-Service-AppCards/apps/finance/`:
`source/`, `cards/`, `service-cards/`, `service/`, `native/`, `tests/` and
`image-to-appcard-flow.json` when implementation starts. Framework checkouts
remain siblings under `octosense-org/`. Do not add the draft to the runnable
app catalog until there is an executable module.

## Image-to-app delivery sequence

Ten reference screens cover the core MVP. The proposed atlas is expanded to
twelve states to make market discovery and saved-news retrieval reviewable.
These states belong to one dynamic app; they do not cap the number of stocks,
stories, list items or navigable data records. US/HK/CN reuse the same page
templates with different data, calendar, currency and localization bindings.

| Scene | Reference state | Main coverage |
| --- | --- | --- |
| 01 | Mixed-market watchlist | Followed stocks, regional filters, quote rows and sparklines. |
| 02 | Markets overview | Regional sessions, available benchmarks and honestly scoped movers. |
| 03 | Bilingual search | English/Chinese names, numeric symbols and distinct exchange listings. |
| 04 | Edit watchlist | Add/remove/reorder and persistence feedback. |
| 05 | Stock details | Quote, intraday chart, statistics and related-news entry. |
| 06 | Chart inspection | A different range and a selected time/price; state of scene 05. |
| 07 | Company news | Entity-linked stories and attributed sources. |
| 08 | Watchlist/business news | Broader feed, region/language filtering and incremental loading. |
| 09 | Article reader | Full-height platform WebView, back, bookmark and share controls. |
| 10 | Saved news | Retrieve, reopen and remove previously saved stories. |
| 11 | Settings/data sources | Appearance, language, colors, provider access and refresh preferences. |
| 12 | Offline/partial data | Cached quotes, explicit timestamps and retry; state of a primary page. |

The atlas is a visual review set, not the complete behavior test suite. Each
applicable surface also needs loading, empty, error and recovery states. In
particular, verify invalid/unsupported symbols, provider quotas, absent company
news, unavailable chart ranges, publisher loading failures and first launch
without configured data access. Test both light/dark themes and both locales
through native variants without treating each as another independent app page.

1. Use the confirmed US/HK/mainland scope and settle this feature plan. Define shared state/actions,
   bilingual strings, numeric fixtures from all three markets and provider contracts.
2. Generate one coherent 12-state atlas using the scene table above.
   Use iOS-style hierarchy, typography, restrained
   separators, native search and sheet interactions. Establish light/dark
   tokens; keep the first atlas visually consistent.
3. Preserve the exact prompt, original bytes, actual resolution and generation
   receipt. Measure crops and create per-scene semantic maps. Map charts to
   numeric native plots and controls to working actions. Screenshots and SVG
   traces cannot serve as interactive stock charts. Article artwork alone may
   use image assets.
4. Run intake, semantic review, compile, bundle and service checks through the
   [shared pipeline](../../lab/image-to-appcard-flow/README.md). Extract the
   four reusable service cards and connect them to Finance state/data.
5. Integrate both launchers against the same locked runtime. Test the native
   release application with Makepad's built-in instrument, hidden native GPU
   windows, real input, chart-state evidence and `/gq` cleanup. Use the existing
   app-owned GPU capture path for Android if the pinned backend still lacks
   the HTTP instrument; report its capture latency/limitations explicitly.
   Legacy Studio capture/gate stages are not claimed as run by direct testing.
6. Complete visual review against the measured atlas and live-provider checks
   independently. A fixture render is not a live-market pass. Website/WASM
   packaging can follow once the native app is accepted; no publication is
   included in this planning step.

Acceptance covers long watchlists/news feeds, correct ticker-to-news matching,
range/inspection values against known samples, selection and scroll retention,
restart persistence, all three currencies and exchange/session labels,
leading-zero ticker lookup, linked listings, Chinese headlines, missing-market
coverage, accurate movers-universe labels, bookmark retrieval/removal,
delayed/stale states, provider
quota failures, keyboard/back navigation, long headlines and both locales.
The article reader must scroll the complete publisher page. Loading a chart
must not block input, and range changes must not recreate the whole screen.

Confirmed scope: US, Hong Kong and mainland China stocks. Open decisions before
live integration: personal versus distributed use, acceptable quote delay in
each market, and data subscription budget. Use documented provider adapters
and show exact coverage and freshness in the application.
