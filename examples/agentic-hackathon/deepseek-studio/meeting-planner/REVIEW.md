# Meeting Planner — review log (Stage 3, post source-review repair)

Interactive card, bundle `dev.studio.meeting-planner`. Source:
`generated/meeting-planner/bundle/main.splash`. This revision applies
`MEETING-OPERATOR-REVIEW.md`.

## Repairs made

| Finding | Fix |
| --- | --- |
| **`delete bookings[key]` not trusted** | Added `without(o, k)` (rebuild excluding one key). `undo()` uses `bookings = without(bookings, key)`. |
| **Two bookings for the same meeting (14:00 AND 15:30)** | `confirm()` now blocks any second booking while one exists: "One Design review is already booked. Undo it before booking another slot." One booking until explicit Undo. |
| Blank question shown only in home | `qnotice` rendered in the **full view** next to the input. |
| Full view fixed, will overflow | Full view converted to a single `ScrollYView`; long answers, keyboard and receipt scroll; Stop/Back stay reachable below. |
| Prompt basenames | `prompt_for` now says read `calendar.json` / `state.json` (not `accounts/device/...`). |
| Repeat the All-busy scenario without injection | Added labeled **Reset demo** restoring the fake fixture and clearing the local booking and added conflicts; bumps `gen` to invalidate any in-flight response. |
| Late-conflict recheck preserved | `confirm()` still re-runs `is_free` on the frozen slot and refuses with the blocking event; `add_conflict`/`all_busy` clear the review. |

Review/confirmation behaviour is preserved.

## Executed calls (Meeting)

`studio.bundle_check` pass (`local_developer`, `source_modified:false`).
`studio.open` → instance `70c59b72-8e21-4c89-81a0-2114d957d2b3`,
`ready:true`. Every `studio.inspect` `checks.pass:true`, `error_count:0`.

| Step | Action | Result | Capture |
| --- | --- | --- | --- |
| 1 | tap `suggestbtn@0` | "Deterministic first free slot: 14:00-14:30 UTC (a fixed calculation, no AI)."; 14:00 selected | `.studio-652d66b3…` |
| 2 | tap `reviewbtn@0` | `reviewbox@0`, `rvwhen@0` "…14:00-14:30 UTC" | `.studio-652d66b3…` |
| 3 | tap `confirmbtn@0` | receipt `rcptbody@0` "Mon 5 Oct 2026 · 14:00-14:30 UTC · Alex, Maya, Jordan"; notice "Booked … No invitation was sent." | `.studio-c15bcdf2…` |
| 4 | tap `undobtn@0` | **FAILED (host: `studio_widget_missing_or_ambiguous`)** — Undo had scrolled off the viewport | – |

## What is verified vs NOT

- **VERIFIED:** booking creation and the exact receipt (`Mon 5 Oct 2026 ·
  14:00-14:30 UTC · Alex, Maya, Jordan`); the review panel; the deterministic
  offline suggestion; busy/free candidate math (10:00 and 11:00 busy, 14:00 and
  15:30 free) rendered with reasons; error-free render on every inspect.
- **NOT VERIFIED this turn (budget spent):** the Meeting **Undo** tap, the
  **single-booking** refusal, **Reset demo**, and the **late-conflict confirm
  refusal**. The budget (24 Studio calls) was fully used by Email's verified
  sequence plus Meeting's booking flow, and the Meeting Undo tap landed on a
  scrolled-off control.
- **Source-level mitigation for Undo:** Meeting's `undo()` uses the same
  `without()` pattern whose effect was *observably verified in Email* this turn
  (receipt fields disappeared). That is corroborating, not a Meeting
  verification, and is recorded as such.
- **Still unverified across both apps:** live agent path, restart persistence,
  real normal-host geometry. Operator runs these.

## Honest remaining gaps

1. Meeting Undo / single-booking / Reset / late-conflict refusal: source
   changed but **not exercised**; next turn should run them (undo after
   booking; then attempt a second slot's Confirm to see the single-booking
   refusal; then Reset).
2. Meeting Undo target was hard to hit because the home card is long; a future
   pass could move Undo/Reset nearer the receipt or shorten the card.
