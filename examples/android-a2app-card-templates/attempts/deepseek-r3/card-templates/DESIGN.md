# A2App Card Template Collection — Design

Reusable app-card templates for **MAIL, CALENDAR, NEWS, FINANCE, PHOTO, YOUTUBE**,
authored for this Android phone (OnePlus 6, portrait) on the offline Studio host.
This document is the shared spec; each family ships its own bundle + L0 glance.

## 1 · Presentation depths are UI depths, not parser levels

| depth | name | what it is |
|---|---|---|
| **L0** | compact glance | a short card on the glance surface: identity row, title, one line, one primary action. Declarative `.card` source. |
| **L1** | expanded actionable | the same item opened in place: full body, AI-written summary, action chips, a reversible local action. |
| **L2** | full app view | the app's own screen: list + tabs + reader. Native Splash only. |

Every declarative `.card` file keeps `# level: L0` **regardless** of which UI
depth it *renders* into. "L0/L1/L2" here never change the card language — the
parser level is always L0; these are presentation depths.

## 2 · Shared visual rules (all families)

Tokens (adapted from the desktop design system to phone widths; the desktop file
had fixed-height/1080-wide assumptions we do not copy):

- Canvas `bg / base` `#xf4f6f8` (light warm-neutral).
- Surface `#xffffff`; hairline `#xe2e7ec`.
- Text `primary` `#x1c2430`, `secondary` `#x5b6672`, `faint` `#x9aa4b0`.
- Type scale (px): eyebrow 11, caption 13, body 15, row-title 16, title 22, screen 24, hero 34.
- Radius: pills 12, cards/sheets 16. Spacing: 12–16 between sections, 6–8 within a group.
- One accent per family, used only for the primary action + active state:
  MAIL `#x2f6fed` · CALENDAR `#xe0642f` · NEWS `#xd6342b` · FINANCE `#x1f9d55` · PHOTO `#x8a4fff` · YOUTUBE `#xe22b2b`.
- Emphasis is **never colour alone**: active = accent text **plus** a 2px accent
  underline; done/archived = a word badge (`✓ Done`, `Archived`) plus a tint.
- Directional values (FINANCE deltas) use positive-green up / negative-red down, always with a sign.
- **Touch targets ≥ 44 logical px**; rows are `Fit` height with padding, never clipped.
- Text wraps; the phone width is fixed by the frame, not by a hard-coded 1080.
- Empty / loading / error are real, declared states (see §5), never a blank pane.

## 3 · Family layouts

- **MAIL** (authored this turn): glance = sender+subject+snippet+Reply; expanded =
  summary (AI-written) + draft field + Send/Archive + Undo; app = Inbox/Archived
  tabs + message rows + reader. Reversible demo action: **Archive ↔ Undo**, plus a
  draft field and a "Send (demo)" that only marks state locally.
- **CALENDAR**: glance = next event (time, title, place) + Join; expanded = agenda
  of the day + RSVP/Maybe; app = month strip + agenda + event detail.
- **NEWS**: glance = lead story + Save; expanded = summary + Read/Restore; app =
  feed + reading list + topics (mirrors `news.card`).
- **FINANCE**: glance = symbol + price + delta; expanded = range + stat tiles;
  app = watchlist + detail with a `StockPlot` tile.
- **PHOTO**: glance = a `Thumb` + caption + Share; expanded = larger `Photo`
  slot + info; app = grid + viewer. Honest **media slot**: with no asset route on
  this host, draw a labelled "photo slot" placeholder — never a fake photo or a
  pretend playback.
- **YOUTUBE**: glance = channel + video title + duration; expanded = description
  + Watch later; app = subscriptions + player slot (a labelled placeholder, no
  real playback).

Shared family styling: same canvas/surface/hairline, same type scale, same
identity-row → title → meta → actions rhythm, per-family accent only.

## 4 · Data ownership & honesty

- L0 cards read **catalogued capabilities only** (`sys.dataset`, `sys.news`,
  `sys.locale`, …). A fabricated headline/message is worse than a missing one, so
  fixtures are explicitly demo data.
- Native bundles here are **offline**: no network, no host services, no accounts,
  no agent, no `http_resource`/`{{assets}}`. Capability is `storage` only, and
  only where used.
- All content is labelled demo. No template claims real mail delivery, real
  mailbox access, real media playback or fetched photos.

## 5 · Empty / loading / error (design spec; implementation status noted per family)

**MAIL implemented:** the native bundle exposes reachable `Ready / Loading /
Empty / Error` demo buttons for the glance and expanded depths; the L0
`glance.card` declares `copy.loading/offline/empty` and branches on `msg.$state`
but is **spec + declared copy, not yet executed** (pending a `studio_render`
pass). Other families below are **design spec only** until authored.

Each L0 glance declares `copy.loading`, `copy.offline`, `copy.empty` and branches
on `source.$state` (`.pending/.ready/.failed`). Each native bundle renders the
analogous states: `loading` = a muted "Loading…" row; `empty` = a short centred
message ("No messages"); `error` = a red line ("Couldn't load — demo") — all
designed, not left blank. This first turn implements MAIL's states; the others
inherit the same three.

## 6 · Reference provenance (factual)

Superset present in `card-template-references/` (copied from the A2App sources in
`index.json`); references were **not modified**. Split by what was actually read
in this session vs merely available:

**Actually read this session:**
- `index.json` — the reference manifest (paths + hashes).
- `framework-l0.md` ← `apps/appcard/a2app-l0/framework/l0.md` — L0 syntax (`source`/`state`/`event`/`copy`/`view`, `$state` lifecycle, `sys.chat`).
- `catalog.md` ← `apps/appcard/a2app-l0/framework/catalog.md` — roles + capability `answers` (read in part).
- `mail-request.card` ← `crates/shell/resources/glance/mail-request.card` — shell Mail L0 (brief/compose/chat modes, model-copy).
- `news.card` ← `apps/appcard/a2app-l0/apps/news/exemplar.card` — L0 exemplar (read in part).
- `a2app-design-system.md` ← `apps/appcard/a2app/widgets/design-system.md` — desktop tokens (read in part; adapted).

**Available but NOT yet read this session** (so nothing here is claimed from them):
- `finance.card` ← `apps/appcard/a2app-l0/apps/stock/exemplar.card`.
- `youtube.card` ← `apps/appcard/a2app-l0/apps/youtube/exemplar.card`.
- `calendar-event.card`, `calendar-agenda.card` ← `apps/calendar/host-service/resources/*.card`
  (grep-skimmed only, for `sys.dataset` field names).
- `photos.splash` ← `apps/photos/bundle/main.splash`.
- `SCRIPT-API.md` ← `OctoScript-App-Design-Flow/docs/SCRIPT-API.md` — current Splash API.

The earlier `task-planner/` project is untouched. Work lives only in `card-templates/`.

## 7 · This turn's scope

Author MAIL only (`card-templates/mail/`): `bundle/main.splash` +
`bundle/manifest.json` (native interactive, all three depths), and the reusable
`glance.card` + `glance.data.json`. The reviewer inspects the rendered starting
point before the other five families are expanded.
