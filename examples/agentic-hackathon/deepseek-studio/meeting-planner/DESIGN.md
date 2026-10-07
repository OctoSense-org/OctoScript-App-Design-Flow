# Meeting Planner — interactive card design (Stage 3)

`demo.deepseek-meeting` / bundle id `dev.studio.meeting-planner`. Fictional
calendar only; nothing is booked for real and no invitation is sent. Native
Splash (`main.splash`) in the storage-only Studio preview.

## Family and palette

Same family as Email Action and the L0 glances: warm pale background, dark ink,
one blue accent, generous rhythm.

- Background `#xfaf5ec`; panels `#xffffff`; soft fills `#xefe8db`; ink
  `#x1b1b1f`; secondary `#x6f6a63`; accent `#x2f5bff`; receipt green
  `#x1f7a4d`; refusal `#xb3261e`.
- Type 13–22 pt. Header 22 pt bold, headline 22 pt bold, supporting lines lower
  weight.
- `Primary`/`Ghost` are bound once as `ButtonFlat` and instantiated, so every
  control is full width (`width: Fill`) and 48 logical px high (≥ 44). Verified
  in pixels: full-width blue primaries.

## Structure

- Header row: "Meeting Planner" + `Demo data` marker.
- **Home (scroll):** a panel with "Design review", `Mon 5 Oct 2026 · 30 min ·
  UTC`, `Alex, Maya, Jordan`; an offline suggestion line + **Suggest first free
  slot (offline)**; a heading and four tappable candidate rows
  (`GestureView`); a notice line; **Review this slot**; a review panel (exact
  time/timezone + attendees) that contains **Confirm booking**; the local
  receipt; then **New 14:00 conflict**, **All busy**, **Undo this booking**,
  **Open full view**.
- **Full view:** availability summary (each candidate free/busy), busy-event
  list, agent status, a question field + **Ask agent**, **Stop**, the agent
  answer line, the local booking receipt, **Undo**, and **Back to the card**.

## Correctness choices

1. **Overlap math.** `free` iff no busy event satisfies
   `candidate.start < event.end AND event.start < candidate.end`. Initial data:
   Maya 600-630, Alex 660-690, Jordan 780-810; candidates 600-630, 660-690,
   840-870, 930-960 → 10:00 and 11:00 busy, 14:00 and 15:30 free. Busy slots
   cannot be booked (`review()` refuses them).
2. **Deterministic offline calc.** **Suggest first free slot** runs
   `first_free()` — a fixed calculation, clearly labelled "… (a fixed
   calculation, no AI)." No model is involved.
3. **Review gates booking.** `review()` freezes `rv_start/rv_end/rv_time` and
   sets `rv_valid`; Confirm lives only inside the review panel. Changing the
   selection (`pick`) or the availability (`add_conflict`/`all_busy`) clears the
   review.
4. **Recheck at confirmation.** `confirm()` re-runs `is_free` on the frozen
   slot; if a conflict appeared after review it **refuses**, clears the review
   and reports the blocking event. A conflict added after review therefore
   cannot be booked.
5. **One immutable receipt.** A successful booking stores
   `bookings[start] = {date, time, tz, attendees}` under the local demo
   calendar; a duplicate at the same slot is rejected ("already booked"). Undo
   removes only that booking and keeps the busy fixtures.
6. **Persistence.** `calendar.json` (events + candidates) and `state.json`
   (bookings + selection) are written under `accounts/device/` after every
   relevant change, so the receipt survives the process.
7. **Grounded, safe agent prompt.** `prompt_for` embeds the fake events,
   candidates and their free/busy flags, points at `calendar.json`/`state.json`,
   treats calendar content as data, restricts recommendations to a currently
   free listed slot, forbids invented availability and forbids claiming a
   booking. AI output is prose only — never evaluated, never auto-booked.
8. **Honest availability states.** `host.has("octos…")` decides agent
   availability; the storage-only preview shows an explicit unavailable state.
   No arbitrary short AI timeout; the busy state is shown while the request is
   outstanding and Stop (calling `octos.turn.interrupt`) is on the same screen.
   Blank questions are rejected.

## Files

- `bundle/main.splash`, `bundle/manifest.json` (schema 1, `[storage]`),
  `bundle/assets/icon.svg`.
- `agent-manifest.json` (outside the bundle): id `demo.deepseek-meeting`,
  capabilities `[storage, octos.turn.start, octos.turn.interrupt]`, agent
  profile read-only with `ask_user_question`. No forged integrity; no publish,
  sign or install.
