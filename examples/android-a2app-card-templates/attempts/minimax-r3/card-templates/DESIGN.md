# App-Card Template Collection — DESIGN

Author: MiniMax (design + code owner) · Host: Android OnePlus6, Studio offline host
Scope: reusable card templates for **Mail, Calendar, News, Finance, Photo, YouTube**
built on the existing A2App app-card templates (`apps/appcard/a2app-l0/*`).

**Presentation depths (UI), not parser levels.** The user confirmed L0/L1/L2 as
*presentation* depth. A declarative `.card` file still declares the L0 language
level in its header (`# level:   L0`); L1/L2 never appear in a `.card` header.

```
L0  compact glance        one glance-width card, no interaction beyond open
L1  expanded card         actionable: the primary action(s) + one secondary
L2  full app view         the real screen the card would open into
```

---

## 1. Provenance — what was read, and what was decided

Read verbatim from `card-template-references/` (hashes/index in its `index.json`):

| Reference | Origin | What I took from it |
|---|---|---|
| `framework-l0.md` | `apps/appcard/a2app-l0/framework/l0.md` | declaration order (`source/state/event/copy/component/view`), source lifecycle `.pending/.ready/.stale/.failed`, `copy.*` must be declared, closed icon vocabulary, "no headline/bylines a card can't fetch" |
| `catalog.md` | `apps/appcard/a2app-l0/framework/catalog.md` | the **only** legal roles (`Col, Row, Surface, TextTitle/TextRow/TextBody/TextCaption/TextEyebrow, Tile, Chip, Field, Rule, Icon, Band, Avatar…`) and the `sys.*` field vocabulary; it is generated, so a role not listed here is refused |
| `news.card` | `apps/appcard/a2app-l0/apps/news/exemplar.card` | the `# level/profile/model` header block, two-source-not-one-sliced rule, `copy` vocabulary/model-copy split, no fabricated content |
| `finance.card` | `apps/appcard/a2app-l0/apps/stock/exemplar.card` | value + unit handling (`TextValue`/`Tile` with `unit`, `format`), numeric-first hierarchy |
| `youtube.card` | `apps/appcard/a2app-l0/apps/youtube/exemplar.card` | title/channel/duration row shape, single-source list discipline |
| `mail-request.card` | `crates/shell/resources/glance/mail-request.card` | Mail's own mode-state machine (`brief/reply/ask/sent/done`), `Field` for draft editing, "Send only moves the card to Sent (demo)" |
| `calendar-event.card`, `calendar-agenda.card` | `apps/calendar/host-service/resources/*.card` | `sys.dataset` record shape, two-`Tile` metric row, `Icon(name:.location)` subtitle row |
| `photos.splash` | `apps/photos/bundle/main.splash` | the **native** Splash idioms this collection is built on: `let Chip = ButtonFlat{…}` component widgets, `ScrollYView{on_render: \|\| {…}}` lists, `GestureView` rows, `show_bg/draw_bg.color`, `draw_bg.border_radius`, `start_timeout(0.05, \|\| boot())` |
| `SCRIPT-API.md` | `OctoScript-App-Design-Flow/docs/SCRIPT-API.md` | `ui.<id>` accessors, event handler signatures, string/array methods (no `sort/map/filter/join/index_of`), `fs.*`, limits (200k instr / 64 ms per handler), hex-colour gotcha |
| `a2app-design-system.md` | `apps/appcard/a2app/widgets/design-system.md` | **deliberately not adopted as layout truth** — it carries desktop/fixed-height assumptions; only its semantic hierarchy (eyebrow → title → body → caption) and token intent are reused, re-expressed for this phone's width |

No reference file was modified.

### Honest capability boundary (this host)
Offline Studio: no network, no host services, no accounts, no `{{assets}}` routes,
no in-screen `http_resource`. So:

* `Photo`/`YouTube` rows carry **declared media slots** — a frame with the slot's
  aspect ratio, a caption, and an explicit "media not loaded" state. Nothing is
  fetched and no playback is faked.
* `Finance` shows a value + change as text. No `StockPlot` sparkline is drawn
  where it would need fetched series data; the plot role is documented in the
  card, not faked with random numbers.
* `Mail`/`Calendar` content is **synthetic demo data**, labelled as such in the
  UI. No mailbox, no account, no send.

---

## 2. Shared visual rules (the family)

Semantic hierarchy, adapted from the L0 role set into native widget styling.
Widths are *Fill-based and fluid*; heights are `Fit` or fixed minimums, never
desktop-fixed.

| Token | Value | Use |
|---|---|---|
| `ground` | `#xf2f2f7` | app background, separates cards |
| `surface` | `#xffffff` | card / row panel |
| `ink` | `#x1c1c1e` | titles, sender names |
| `ink2` | `#x3c3c43` | body, preview lines |
| `muted` | `#x8e8e93` | captions, timestamps, placeholders |
| `accent` | `#x007aff` | interactive text, unread dot, selected segment |
| `positive` | `#x248a3d` | gain / resolved state |
| `danger` | `#xd70015` | destructive action (delete, decline) |
| `demo` | `#x8a0b00` on `#xfff3cd` | the DEMO badge, one per screen |

Type scale (native `draw_text.text_style.font_size`):

```
21 bold   screen title / card title      (TextTitle)
16 bold   row title, sender             (TextTitle)
14        body, preview line 1–2        (TextRow)
12        captions, timestamps, chips   (TextCaption)
11 bold   eyebrow / section label, letterspaced look via uppercase copy
```

Rules:

1. **Eyebrow → Title → Body → Caption**, in that order, max 4 text levels per
   card. Never more than one 21pt item on screen.
2. **Wrapping**: every long line is a `Fill`-width Label inside a `Fit` view, so
   text wraps instead of clipping. No `width: Fit` on a long sentence.
3. **Touch targets ≥ 44 logical px.** Buttons `height: 44`; row hit areas are
   `GestureView` with `height: Fit` + `padding` to reach 44.
4. **No hidden actions.** Every action is visible in the view that owns it; the
   depth bar is always on screen, never inside a menu.
5. **Demo honesty**: any synthetic record carries the DEMO badge; a demo
   mutation says so in its own confirmation ("Sent (demo) — nothing left this
   device").
6. **Reversible first**: an action that changes the local list must offer Undo
   in the same bar, not only in a toast.
7. Empty / loading / error are *designed*, not implied — see §5.

---

## 3. The three depths, per family

Every family ships: a declarative L0 card (glance), an L1 expanded layout, an
L2 full view. L1/L2 live in the family's native bundle with explicit view
names (`l0_glance`, `l1_expanded`, `l2_full`).

### MAIL — authored this turn (`card-templates/mail/`)
* **L0 glance** — envelope family icon/word, `UNREAD · DEMO` eyebrow, sender,
  subject, one preview line, timestamp, unread dot. The shape of
  `mail-request.card`'s brief mode, minus `sys.chat` (no agent on this host).
* **L1 expanded** — full preview body, `Reply (demo)` / `Archive` / `Mark read`
  actions, metadata row (folder · attachment flag · demo label), Undo affordance
  for the destructive one.
* **L2 full** — inbox list + selected thread + composer. The composer is the
  `Field`/draft pattern from `mail-request.card`: text in, nothing sent.
* **Local demo interaction (reversible)**: `Archive` removes the message from
  the inbox and pushes it to a shadow list; `Undo` pops it back, in the same
  always-visible bar. Secondary reversible toggle: `Mark read` / `Mark unread`
  flips a flag, state survives depth changes.

### CALENDAR
* **L0** — next event only: date tile + time + title + place, per
  `calendar-event.card`'s two-`Tile` row.
* **L1** — the event with a one-line location note, attendee count, and
  `Add (demo)` / `Dismiss` actions; agenda preview of what follows.
* **L2** — day agenda list + a week strip; selecting a slot swaps the detail
  pane. Empty day gets a designed "nothing scheduled (demo)" state.

### NEWS
* **L0** — lead story: source eyebrow, headline, points/comments captions. No
  byline unless fetched, no invented headline (see `news.card`).
* **L1** — lead + three follow rows, `Save`/`Remove` chips (the reading-list
  pattern, identity-only), topic chips.
* **L2** — feed with search, saved list tab, story detail. Loading uses
  `.pending` copy; failure uses `.failed` copy and a Retry action.

### FINANCE
* **L0** — symbol, last value, signed change, as-of caption. Numbers first.
* **L1** — value tile + day range caption + a `Plot` **slot** (a framed region
  with a stated "series not available offline" state — never random data).
* **L2** — watchlist + detail with range chips; an unfetched range degrades to
  the last value with an explicit caption.

### PHOTO
* **L0** — one framed 4:3 media slot + caption + date.
* **L1** — media slot + title/people row + `Add to (demo album)` / `Remove`.
* **L2** — grid of media slots grouped by moment, with a filter row.
  **All frames are visibly "media slot" placeholders on this host** — a caption
  and a diagonal-free flat frame, never a fake photograph.

### YOUTUBE
* **L0** — 16:9 media slot, title, channel, duration caption.
* **L1** — slot + description snippet + `Watch later (demo)` / `Remove` chips.
* **L2** — list + search; selecting a row shows the slot large with an explicit
  "playback unavailable offline" state.

---

## 4. Reusable structure

* **Family name + DEMO badge** is always the first line — one place to find out
  what app you are looking at and that the data is synthetic.
* **Depth bar** — persistent, 44px, three segments, current depth stated in
  words next to it (not only by colour, so it survives a screenshot).
* **Action bar** — 44px, always visible at the bottom of L0/L1/L2, with Undo
  adjacent to any list-mutating action.
* **Card + row components** are declared once as `let` widget templates
  (`let MailRow = View{…}`) and instantiated with `{…}`, exactly as
  `photos.splash` does, so a family tweak lands in one place.

---

## 5. Empty · loading · error (specified, not implied)

The declarative language has source lifecycles; the native views get the same
three states as *designed* placeholders inside the same component, at the same
size as content, so nothing reflows when data lands.

| State | L0 glance | L1 / L2 |
|---|---|---|
| **Loading** | DEMO eyebrow + a 2-line shimmer block: `Masthead` sized label, `Rule`, two muted lines | a 44px `LoadingSpinner` beside `Loading demo messages…`; actions disabled-looking (muted text, no destructive tone) |
| **Empty** | `No demo messages` + `Archive one to see this` (actionable, not a shrug) | empty inbox with a `Restore all (demo)` action |
| **Error** | `Can't load demo messages` + `Retry` chip | `Retry` + the reason text; the list keeps its last good rows, dimmed, with a `Showing last good data (demo)` caption |
| **Stale** | `as_of` caption in `muted` | `Refresh (demo)` action next to the caption |

Per the L0 rules: `copy.loading`/`copy.offline` are **declared copy**, never
inline strings compared against sentinel values; `$state` is branched, never a
`-9999` test.

---

## 6. What this turn delivers

* `card-templates/DESIGN.md` — this document.
* `card-templates/mail/bundle/main.splash` + `manifest.json` — a real native
  interactive preview with all three depths, Archive/Undo and mark-read toggles.
* `card-templates/mail/glance.card` + `glance.data.json` — the reusable
  declarative L0 source and its fixture, in the A2App exemplar shape.

Remaining families (Calendar, News, Finance, Photo, YouTube) follow only after
the reviewer signs off on the Mail starting point.
