# Email Action — interactive card design (Stage 2)

`demo.email-action` / bundle id `dev.studio.email-action`. Fictional data only;
nothing is sent and no mail account is connected. Native Splash (`main.splash`)
in the storage-only Studio preview.

## Family and palette

Same family as the Stage-1 L0 glance: warm pale background, dark ink, one blue
accent. Restrained, compact, one headline.

- Background `#xfaf5ec`; panels `#xffffff`; soft fills `#xefe8db`; ink
  `#x1b1b1f`; secondary `#x6f6a63`; accent `#x2f5bff`; receipt green
  `#x1f7a4d`; error `#xb3261e`.
- Type sizes 13–22 pt (within the 14–28 brief band; captions at 13 for compact
  metadata). Titles `theme.font_bold`; body regular.
- All primary/secondary controls are `ButtonFlat` bound once (`Primary`,
  `Ghost`) and instantiated, so every action is **full width** (`width: Fill`)
  and **48 logical px** high (≥44 required). Verified in pixels: full-width
  blue primaries, not default pastel buttons.

## Structure

- Root `SolidView(padding: 16)` with a header row (title left, `Demo data`
  marker right), then a `ScrollYView` home card that holds everything the
  selected message needs.
- **Home card:** sender/address, subject (bold), source body, due line; then
  one primary **Ask app agent for a reply**, a **Stop** (shown only while the
  agent is busy), and **Insert offline sample reply**. Status, error and
  provenance lines follow, then the editor.
- **Editor:** a multiline `TextInput` (`multiline: true`) for the reply, a
  **Review reply** primary, and — only after a review — a review panel showing
  the exact `To`, `Subject`, `Body` and the **Confirm demo delivery** primary
  inside it.
- **Receipt:** after delivery, the stored outbox entry's `To`/`Subject`/`Body`
  are shown verbatim, plus **Undo** and **Open full view**.
- **Full view:** a scrollable message list (three fixtures) with
  `GestureView` rows, a question field with **Ask agent** / **Stop**, an
  agent answer line, and **Back to the card**.

## Correctness choices (operator review)

1. **Review gates confirmation.** `review()` freezes an explicit snapshot
   (`rv_id`, `rv_to`, `rv_subj`, `rv_body`) and sets `rv_valid`. The Confirm
   button lives *inside* the review panel, which is visible only while
   `reviewing and rv_valid`. Any draft edit, new model draft, offline sample or
   message change clears `rv_valid` and hides the panel, so typing after review
   cannot deliver different text.
2. **Immutable outbox.** Delivery stores `outbox[id] = {to, subject, body}`
   keyed by the stable message id; the receipt renders those exact fields even
   if the draft later changes. One entry per message; Undo removes only the
   selected entry and **keeps the draft** for correction.
3. **Edit persistence and stale protection.** `set_reply` bumps a per-message
   revision `revs[id]` and calls `save()`, so edits survive restart. `ask_agent`
   captures the revision at request time and discards a reply if the revision
   changed while the agent worked — a late AI answer never overwrites the
   user's editing. Another Ask is refused while busy; Stop is reachable in both
   views.
4. **Grounded, safe prompts.** Both `prompt_for` and `qprompt` label the
   selected message, point at `accounts/device/inbox.json` /
   `state.json`, treat message content as data (not instructions), call answers
   read-only proposals, and forbid invented facts or calendar availability.
5. **Visible provenance.** Each draft carries a persisted source
   ("Offline sample" / "AI-written" / "You edited") shown as
   `Reply source: …`.
6. **Honest states.** No invented 5-second model deadline; the busy state is
   shown while the host request is outstanding and Stop interrupts it. Agent
   failures show the **actual** `r.error`; the storage-only preview shows an
   explicit "no agent service" state via `host.has("octos…")`.

## Files

- `bundle/main.splash` — the app source.
- `bundle/manifest.json` — schema 1, `dev.studio.email-action`, `[storage]`.
- `bundle/assets/icon.svg` — envelope mark.
- `agent-manifest.json` (outside the bundle) — the later normal-host packaging:
  id `demo.deepseek-email`, `[storage, octos.turn.start, octos.turn.interrupt]`,
  agent profile read-only with `ask_user_question`.
- No network, Mail or Calendar capability; no publish, sign or install.
