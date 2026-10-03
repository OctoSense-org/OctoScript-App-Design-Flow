# App-Card Template Collection — DESIGN

Author: MiniMax (design + code owner) · Host: Android OnePlus 6, Studio offline
Families: MAIL, CALENDAR, NEWS, FINANCE, PHOTO, YOUTUBE (all six authored)

Offline only. No publication, signing, install, accounts, network, live data,
real mail, live news, live prices, trades, or media loading. Every record is
synthetic demo data, labelled DEMO in the UI and in fixture comments.

## 0. Depths vs language level

`L0 / L1 / L2` are **presentation depths** (UI), not parser levels. Every
exported `.card` stays language `L0` at every depth. Native previews are Splash.

## 1. The lexical lesson that cost a turn — reuse this

`View{… spacing: 8}` **already contains its closing brace.** Children on the
next lines are outside that View; the later `}` is a **second** close, not a
matching one. Same for a header ending `draw_bg.border_radius: 14.0}`. Splash
does **not** reopen a closed container because the next line is indented:
**indentation is not structure, the character is.** A header ending `…14.0`
*without* that character is a different, legal shape — the difference is one
character.

Symptom: evaluation reports `CHILDREN 0` while `RUNNING` is true, or the tree
builds and `set_text` never lands.

**Corollary: `checks.pass: true` is not sufficient.** During an earlier
Calendar regression a build reported `error_count: 0` with only 22 of 32 widgets
present. Count the widgets and read the text values.

## 2. Three self-inflicted regressions in the final polish — do not repeat

All three were **duplicate `status := Label` declarations in one tree**
(News, Calendar, Finance) and all three would have broken `open`. Two were
caught by `grep` before building; one only surfaced as an `open` failure.

**Rule adopted: grep for duplicate bound names and premature-close headers
before every `studio_open`.** This is now mandatory, not optional.

A fourth regression — an excess `}` in the Calendar footer — passed grep and
only appeared on `open`, so the grep is necessary but not sufficient.

## 3. Shared visual system

| Token | Value | Use |
|---|---|---|
| `ground` | `#xf2f2f7` | app background |
| `surface` | `#xffffff` | cards, rows, composer |
| `ink` / `ink2` | `#x1c1c1e` / `#x3c3c43` | titles / body |
| `muted` | `#x8e8e93` | captions, dates, timestamps |
| `accent` | `#x007aff` | interactive text, selected tab |
| `up` / `down` | `#x248a3d` / `#xd70015` | gain / loss only (Finance) |
| `line` | `#xe5e5ea` | hairlines |
| `demo_bg` / `demo_ink` | `#xfff3cd` / `#x8a0b00` | DEMO badge |

Type: 19pt screen title · 15pt item title · 13pt body · 12pt meta · 11pt bold
eyebrow. Every active control is `height: 44`. Spacing 2–8.

Exports all declare `theme taskplan_light` — a registered theme pack — so the
six cards form one coherent set.

## 4. `taskplan_light` — my earlier claim was WRONG, corrected here

**Correction.** I previously reported as a negative result that
`taskplan_light` "applied cleanly and changed no height" and that its
13pt title token "did not take effect on this pinned host." **That was wrong.**
All six exports carried the line `# theme taskplan_light`, and in `.card` a
leading `#` starts a **comment** — so no theme was ever selected. Every prior
export render was therefore **default styling**. The host's failure was mine:
a malformed declaration, not a missing platform capability.

The tell was available to me and I misread it: renders before and after the
"change" were byte-identical (585 / 594 / 594 / 712 / 712 / 770 px). An
identical dimension after a supposedly visual change means the change did
nothing. I should have treated that as evidence about **my own input** before
concluding the platform lacked the lever.

All six files now carry the bare, top-level declaration:

```
theme taskplan_light
```

which is the original registered A2App theme API. No typography arguments and
no density axes were invented.

**Rendering under the theme is unverified.** The operator renders all six exact
final cards independently; until that evidence exists I make **no** claim about
the resulting heights, about whether the 180–230 pt target is now met, or about
how the theme reads visually. The previously measured numbers describe
**default-styled** renders and are kept below only as the pre-correction
baseline, not as a result.

Pre-correction baseline, default styling, all `settled: true`
(968 px wide; ≈2.8125 px per logical point, so ÷2.8125 for points):

| Family | px | ≈pt | note |
|---|---|---|---|
| FINANCE | 585 | 208 | in band |
| PHOTO | 594 | 211 | in band |
| CALENDAR | 594 | 211 | in band |
| NEWS | 712 | 253 | over |
| MAIL | 712 | 253 | over |
| YOUTUBE | 770 | 274 | over |

Still true independently of theming: `TextTitle` accepts only `text` and
`width`, and `density: .compact` is parsed by the language but rejected by this
Studio/Glance host. Shortening the fictional titles to hide overflow is
forbidden, so any remaining oversize is reported rather than hidden.

## 5. Family behaviour

**MAIL** — L2 collection → reader → reply → Back in one bounded `ScrollYView`.
Drafts stored per message id; blank Queue refused; typing clears the stale
error; Queue appends to a local demo list only; archive/Undo and read/unread
independent per message. List rows recomposed to content-above-actions so
subjects such as "Design review moved to Thursday" are not clipped. Persistent
`●` depth marker. **Unchanged in the final polish.**

**CALENDAR** — next event, expanded event with a reversible RSVP whose button
names the *next* state, agenda → detail. Per-event RSVP is independent and
wraps. `open_wrap` hides the Open event action when every event is declined.
Now uses the same `b0/b1/b2` bullet marker as the other families; the
redundant `depth_now` label was removed.

**NEWS** — three stories; `do_toggle_saved()` backs the dynamic Save/Remove
label in L1, detail and every row; All/Saved filter. Article bodies are demo
summaries; no page is fetched or opened.

**FINANCE** — three instruments; `do_toggle_watch()` wired to L1, detail and all
six row buttons; All/Watching filter; no buy, sell or trade affordance. The L0
price/dir/change now has its own row, which is what restored the full
**-0.38** (previously clipped to `-0.3`). All six list rows — including the
three filtered ones — were recomposed to content-above-actions. Sign and colour
agree via paired `up`/`down` Labels; there is no `set_color` in the API.

**PHOTO** — three fictional records; `do_toggle_fav()` behind the dynamic
Favorite/Remove label; All/Favorites filter. **No image is ever shown** — each
record states the photo is not loaded, and there is no media control that
pretends otherwise.

**YOUTUBE** — three fictional videos; `do_toggle_later()` behind the dynamic
Watch later/Remove label; All/Watch later filter. **No thumbnail, no search, no
playback**; no enabled Play control exists. The shipped `youtube.card` searches
a live source and hands a player url to `sys.link`; neither is possible
offline, so this family uses a plain `sys.dataset` record.

For both media families the runtime explanation lives here in DESIGN.md; the UI
carries only a short honest caption.

## 6. Offscreen structural convention (now proven in all six)

* every non-leaf container stays open until after its children;
* L0's action uses `lead_id()` — never a stale `sel` from another route;
* L2 is one `ScrollYView{width: Fill height: Fill}` with `l2_list` and
  `l2_detail` toggled, so the last item is reachable by scroll and its detail
  opens at the top of the region;
* list rows are `flow: Down` with full-width content Labels and a **separate**
  nested `flow: Right` action row — side-by-side content and buttons clipped
  titles mid-word across all four list families;
* the active depth is a `●` bullet in the segment bar, so it survives child
  actions and detail navigation; no separate depth label, no extra container;
* selected tabs are marked with `●` **and** in words, not colour alone.

## 7. Exported cards

All six carry `theme taskplan_light`, use fixture keys equal to their **source
aliases** (`lead`; Calendar uses `next_ev`), and **omit the live dataset id** so
fixture values lower to literals. Every lifecycle-bound read sits inside a
`.$state == .ready` guard; `when` takes no `else`; branches reference named
`view` blocks.

The unused `more`/`agenda` second source was removed from all six after
compacting: with no view reading it, each card failed with
`source "more" is declared and never read`.

## 8. Verification status — exact, no self-awarded score

The operator scores this collection. I assign no grade.

**Correction to earlier reports:** my previous turn's "17 Studio calls" was
stale; the transcript records 120 tool calls including 28 Studio calls for that
turn. The **115 independent behaviour passes belong to the round10/11 sources,
not to this revision.** Nothing in this section is a claim that this revision
has been regression-tested; the operator reruns all six after this polish.

Verified in the final polish with real tool output:

| Check | Result |
|---|---|
| News `open`/`inspect` | `ready: true` (`0aa4565b`), `pass: true`, `error_count: 0`, 29 widgets, `g_title` "Riverside bridge reopens after inspection", `b0@0` "● L0", `close` `{"closed": true}` |
| News startup blocker | excess `}` removed; identical bytes that returned `studio_eval_failed` for the operator now open |
| Finance `open`/`inspect` | `ready: true` (`1580b0b3`), `error_count: 0`; L2 45 widgets with six reshaped rows; image shows **"DLK · Delta Logistics"** and **"17.62  -0.38"** in full; `close` `{"closed": true}` |
| Calendar `open`/`inspect` | `ready: true` (`0335ca5f`), `error_count: 0`, 30 widgets, `b0@0` "● L0", `open_wrap@0` present, `close` `{"closed": true}` |
| six export renders | sequential, all `settled: true`, heights in §4 |
| export PNGs viewed | YOUTUBE, MAIL, NEWS; Finance native list viewed |
| structural grep | no premature-close headers, no duplicate `status`, no `#` prose |

**Not verified:**

* **No native behaviour suite has been run on this revision.** The 115 passes are
  the earlier sources. The operator reruns all six.
* Mail, Photo and YOUTUBE natives were **not re-opened** this turn; they are
  unchanged since their last verified build.
* Filtered (Saved/Watching/Favorites) Finance rows were not individually
  exercised; they share the reshaped layout but were not driven.
* **Exported-card actions cannot be proven here at all:** `studio_render`
  returns only a PNG with no interactive instance. No native-input claim is
  made for any exported card in any family; exported actions are correct by
  source reading only.
* The large empty region in every native L0 remains: L0 is a `height: Fill`
  container with short content, so the gap comes from the container, not from a
  filler view. Removing a 1-px filler does not change it.
* Three of six exported glances remain over the 180–230 pt target (§4), and no
  supported lever remains on this host.
