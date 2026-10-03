# A2App Card Template Collection — Design & Status

Reusable app-card templates for **MAIL, CALENDAR, NEWS, FINANCE, PHOTO, YOUTUBE**,
authored on this Android phone (OnePlus 6, portrait) for the offline Studio host.
Each family ships a native preview bundle plus an exported declarative L0 glance.

This is the single current document (it replaces earlier drafts; there is no
stale section beneath it).

## 0 · Honesty scope

- All six bundles are **offline**. No network, no accounts, no host services, no
  agent. There is **no** live mail delivery, mailbox access, news feed, quote
  feed, trading, media retrieval or media playback anywhere in this collection.
- All content (subjects, events, headlines, prices, photo/video items) is
  **synthetic demo data**. Titles, names, numbers and metadata are fictional.
- Only the **local controls** are functional: reversible local toggles (archive,
  RSVP, save, watch, favorite, watch-later) and local view navigation.
- **Native app state is in-memory and resets when the preview is reopened.** It
  is not persisted (no storage calls are made; no `storage` capability is
  declared). Reopening a disposable preview returns to the initial demo state.
- Scores referenced by the operator are **external manual review**, currently
  ~4.1/5 excluding gallery controls — not an acceptance or production rating.

## 1 · Presentation depths are UI depths, not parser levels

| depth | name | what it is |
|---|---|---|
| **L0** | compact glance | a short card on the glance surface: identity row, title, one line, one primary action. Declarative `.card` source. |
| **L1** | expanded actionable | the same item opened in place: metadata, action chips, one reversible local action. |
| **L2** | full app view | the app's own screen: collection + tabs + item detail. Native Splash only. |

Every declarative `.card` keeps `# level: L0` **regardless** of which UI depth it
renders into; the parser level is always L0. L0/L1/L2 are presentation depths.

**Native vs exported (explicit difference):**
- Native bundles draw their own accent colors (see §2). The exported `.card`
  glances render with the runtime theme's tint, which **differs** from the
  native accent.
- The exported ready-fixture glances have rendered successfully, but shell
  publication/notification wiring and the exported cards' **event interactions**
  are **not** validated by those renders.
- L1 body text in the native apps is **fixed fixture copy authored during
  generation** — it is not a live AI-generated summary.

## 2 · Shared visual rules

- Canvas `#xf4f6f8`-family light neutrals; surface `#xffffff`; hairline `#xe2e7ec`.
- Text `#x1c2430` primary, `#x5b6672` secondary, `#x9aa4b0` faint.
- Type scale (px): eyebrow 11, caption 13, body 14–15, row-title 16, title 18–20,
  screen 24–30.
- Radius: pills 12, cards 16. Spacing 12–16 between sections, 6–8 within a group.
- **One accent per family**, used only for the primary action / active state:
  MAIL `#x2f6fed` · CALENDAR `#xe0642f` · NEWS `#xd6342b` · FINANCE `#x1f9d55` ·
  PHOTO `#x8a4fff` · YOUTUBE `#xe22b2b`.
- Active/selected state is **persistent after the press** (not hover-only): the
  selected tab/element renders as a filled accent control. Reversible toggles
  also carry a word badge (`✓`, `Archived`, `Going (demo)`, …) so emphasis is
  never colour alone.
- **Touch targets ≥ 44 logical px** in both dimensions; rows are `Fit` with padding.
- Text wraps; the phone width is fixed by the frame, not a hard-coded 1080.
- Empty / loading / error are declared states in the `.card` sources and reachable
  demo states in the native bundles (§5).
- Known non-blocking finding: tall L2 collections report `text_clipped` on the
  **scroll-edge partial third row**. The controls visible there are ≥44 px;
  whether scrolling actually reaches the **final** list item is **awaiting the
  operator's final scroll check** and is not asserted here.

## 3 · Family layouts (all authored & native-verified)

- **MAIL.** glance = sender + subject + snippet + one `Reply`. expanded = header +
  sender + **draft `TextInput`** + `Send (demo)` (blank-guarded) + `Archive`
  (or `Undo`) + a short summary, with bottom nav pinned at the top so it stays
  reachable when the Android keyboard shrinks the viewport. app = `Inbox`/`Archived`
  tabs (pure view state) + rows + `Open ›` → per-message detail (sender/title/body
  keyed to the selected id) + `‹ Back to list`. Reversible: **Archive ↔ Undo**.
- **CALENDAR.** glance = next event (time · place, title) + `RSVP`. expanded =
  when/where + attendees + **reversible RSVP `Going`/`Maybe`** + description.
  app = `Today`/`Week` tabs + agenda rows + `Open ›` → event detail + `‹ Back`.
  **Fix (this turn):** the L2 collection list is its own internal `ScrollYView`
  inside the stage's `on_render`, so opening an event renders the detail as a
  **fresh pane** — the detail starts at its header instead of inheriting the
  list's scroll offset. No new API is used (`View.render()` re-runs the stage's
  `on_render`, recreating the enclosing scroll subtree).
  **RSVP is per event** (independent state per event id); the unset label is the
  neutral **"No response"**. Selected RSVP renders as the filled accent control.
- **NEWS.** glance = lead story (title + source line) + one `Save`. expanded =
  source line + summary + `Save`/`Remove` + link line. app = `Feed`/`Saved` tabs +
  story rows + `Open ›` → detail + `‹ Back`; a saved record is **a link only**
  (no article is downloaded). Reversible: **Save ↔ Remove**.
- **FINANCE.** glance = price hero + change + one `Watch`. expanded = price +
  day range + a **static fixture bar strip** (plain `SolidView` blocks — no chart
  API is used) + `Watch`. app = `All`/`Watching` tabs + instrument rows (name +
  price stacked so both stay readable) + `Open ›` → detail + `‹ Back`. Reversible:
  **Watch ↔ Unwatch**, per instrument. Deltas use green-up / red-down with a sign.
- **PHOTO.** glance = concise `IMAGE UNAVAILABLE` panel + title/place + one
  `Favorite`. expanded = larger panel + metadata/tags + `Favorite`. app =
  `All`/`Favorites` tabs + rows + `Open ›` → detail + `‹ Back`. Reversible:
  **Favorite ↔ Unfavorite**, per item. Media is honestly unavailable.
- **YOUTUBE.** glance = concise `VIDEO UNAVAILABLE` panel + title/views + one
  `Watch later`. expanded = larger panel + metadata + description + `Watch later`.
  app = `Feed`/`Watch later` tabs + rows + `Open ›` → detail + `‹ Back`.
  Reversible: **Watch later ↔ Remove**, per item. **There is no `Play` button at
  any depth** — no playback is implied. Media is honestly unavailable.

Shared styling: same canvas/surface/hairline, type scale and identity-row →
title → meta → actions rhythm; only the family accent differs.

## 4 · Data ownership & capabilities

- Each manifest declares **no capabilities** (in-memory demo state only; not even
  `storage` is used or declared). `integrity.bundle_blake3` stays a
  zero placeholder — this is **local developer admission**, not signing/publishing.
- L0 cards read only catalogued capabilities (`sys.dataset`); a fixture that is
  only a link never becomes a fetched article.

## 5 · Empty / loading / error

The `.card` sources declare `copy.loading`, `copy.offline`, `copy.empty` and
branch on `source.$state` (`.pending`/`.ready`/`.failed`). The native bundles
expose reachable `Ready / Loading / Empty / Error` demo buttons for the compact
and expanded depths. These were authored and are reachable in the native previews.

## 6 · Reference provenance (what was actually read across these turns)

**Read during generation:** `index.json`; `framework-l0.md` ←
`apps/appcard/a2app-l0/framework/l0.md` (L0 syntax, `$state` lifecycle,
`sys.chat`); `catalog.md` ← `apps/appcard/a2app-l0/framework/catalog.md` (roles +
capability `answers`, in part); `mail-request.card` ←
`crates/shell/resources/glance/mail-request.card` (brief/compose/chat modes,
model-copy); `news.card` ← `apps/appcard/a2app-l0/apps/news/exemplar.card` (in
part); `a2app-design-system.md` ← `apps/appcard/a2app/widgets/design-system.md`
(in part; desktop tokens, adapted to phone widths).

**Domain references read in a post-generation review** (read *after* the families
were authored; they did **not** guide the earlier generation — the mapping below
is a retrospective comparison): `finance.card` ←
`apps/appcard/a2app-l0/apps/stock/exemplar.card`; `youtube.card` ←
`apps/appcard/a2app-l0/apps/youtube/exemplar.card`; `calendar-event.card`,
`calendar-agenda.card` ← `apps/calendar/host-service/resources/*.card`;
`photos.splash` ← `apps/photos/bundle/main.splash`.

**Available but not read:** `SCRIPT-API.md`.

### 6b · Domain-reference mapping (original concept → generated family)

| Original (kind) | Concept retained / adapted | Cannot run in this offline Studio slice |
|---|---|---|
| `finance.card` — **A2App declarative exemplar** (`stock`) | list↔detail switch; quote header; per-instrument **Watch ↔ Unwatch** with a word badge; range state; stat tiles | `sys.movers` / `sys.quote` / `sys.watchlist` / `sys.prefs` / `sys.symbol_search` sources; live prices; the `PriceChart` (drawn here as **static fixture bars**, no chart API) |
| `youtube.card` — **A2App declarative exemplar** | search-driven list; **Watch later** toggle; player is host-owned | `sys.video` search; `sys.link` **player overlay** and playback; `embed` urls. The generated family has **no Play button** at any depth |
| `calendar-event.card`, `calendar-agenda.card` — **A2App declarative exemplars** | `sys.dataset` single-record shape; day/time tiles; place + notes; next-events agenda | `os.calendar` service fill; `Tile` metric rows (adapted to plain text here) |
| `photos.splash` — **native Splash reference** (NOT a declarative exemplar) | library of photo records (`id/title/date/location/people/tags/moment`); grid + viewer; a favorite-style local action | its `catalog` fixture **image files** and any local-image / `http_resource` / asset routes; actual photo rendering. Media is honestly unavailable here |

**Kind distinction:** `photos.splash` is a **native Splash app**; `finance.card`,
`youtube.card`, `calendar-event.card` and `calendar-agenda.card` are declarative
**L0 `.card`** exemplars. No network, asset or media API was copied from any
reference.

The earlier `task-planner/` project is untouched. Work lives only in `card-templates/`.

## 7 · Verification status

**My own Studio checks:** all six `studio_bundle_check` admissions (capabilities
`[]`); all six exported `glance.card` files render via `studio_render`
(`settled:true`); and, driving the native previews myself, per-item reversible
toggles, second-item identity, collection filters, persistent tab selected-state,
and per-message / per-event detail navigation.

**Calendar navigation fix (my verification, this turn):** on the checked revision,
opening an event now shows the **detail starting at its header** (title/date/place
visible) instead of inheriting the list's scroll offset. Verified for two events
(Design review, 1:1 with Sam) with **per-event RSVP independence** intact (Sam set
Going → Design review still "No response"). The operator has **not** yet rerun on
the fixed source; their final replay of the Week → third-event scroll path is
**pending**.

**Operator checks (independent — performed by the operator, not by me):** Mail
12/12 raw steps; News 14/14; Finance, Photo and YouTube each 14/14 behavior
assertions; Calendar per-event RSVP independence (set review Maybe → Sam shows No
response → set Sam Going → review stays Maybe); YouTube has no enabled `Play` at
any tested depth; and the Mail keyboard suite (typed a draft, scrolled to a 44 pt
`Send`, got the local-demo queued confirmation, retained the draft across
Glance/Expand — no mail sent). Two old assertions expecting "You're going" vs the
current copy "Going (demo)" are **test-copy mismatches, not state failures**. The
operator's final scroll-to-last-item check is still **pending** (see §2).

**Not verified by those renders:** shell publication/notification wiring and
exported `.card` event interactions; they are not covered by initial renders.

**Out of scope / not done:** no install, signing, publishing, or host-service
integration.
