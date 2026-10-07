# Email Action — review log (Stage 2, post native-review repair)

Interactive card, bundle `dev.studio.email-action`. Source:
`generated/email-action/bundle/main.splash`. This revision applies the
independent native-test findings in `EMAIL-NATIVE-REVIEW.md`.

## Repairs made

| Finding | Fix |
| --- | --- |
| **Undo says "removed" but `outbox.m1` stays** | Added `without(o, k)` — rebuild an object excluding one key via supported iteration — and `undo()` now does `outbox = without(outbox, id)`. `delete o[k]` is no longer used. |
| Blank full-view question shows error only in hidden home | Added `qnotice`, rendered in the **full view** next to the input; `ask_question` sets it. |
| Full inbox list fixed-height, one huge row, blank space | Inbox is now one `ScrollYView`; each row is compact (subject bold, sender, due) and the whole view scrolls. |
| Busy guard must cover draft + Q&A | `ask_agent` clears `qstate`; `ask_question` clears `agent`; both bump `gen` with `pick`/`stop`, so a stale result can't leave a phantom busy flag. |
| Prompt should use peer-workspace basenames | `qprompt` now says read `inbox.json` / `state.json` (not `accounts/device/...`). |
| Selecting a message left the inbox open with no route to the card | `pick(i)` now sets `screen = HOME`, so a tap returns to the **expanded action card** for the chosen message; added `selmark(i)` (`"> "` prefix) so the selected inbox row is marked. Draft and busy invalidation preserved (`gen` bump, flags cleared). |

Review/confirmation behaviour is preserved: Review freezes the exact reply,
Confirm is inside the review-only panel, and any draft edit clears `rv_valid`.

## Executed calls (Email)

`studio.bundle_check` pass (`local_developer`, `source_modified:false`).
`studio.open` → instance `7f964349-5620-441b-a638-057465867411`,
`ready:true`. `studio.inspect` `checks.pass:true`, `error_count:0` throughout.

| Step | Action | Result | Capture |
| --- | --- | --- | --- |
| 1 | inspect | card renders; `Demo data` marker; unavailable state | `.studio-0b15f28d…` |
| 2 | tap `samplebtn@0` | draft = sample; `prov@0` "Reply source: Offline sample" | (in `.studio-02b2dddf…`) |
| 3 | scroll +700 then +600 | review controls reached | `.studio-36c6a7d3…` |
| 4 | tap `reviewbtn@0` | `reviewbox@0`, `rvto@0`/`rvsubj@0`/`rvbody@0`, `confirmbtn@0` | `.studio-02b2dddf…` |
| 5 | tap `confirmbtn@0` | receipt `rcptto@0`/`rcptsubj@0`/`rcptbody@0` = reviewed payload; notice "Delivered… No email sent." | `.studio-9f937c39…` |
| 6 | **tap `undobtn@0`** | **receipt labels gone; notice "Removed only this message's outbox entry; the reply draft is kept."; `prov@0`/draft preserved** | `.studio-ae92f5aa…` |

### Navigation fix (focused 6-call check)

`studio.open` → instance `0e7cdfe7-e40f-494a-88d7-e2605afdf18b`. Then: scroll
``home@0` +1200 → tap `openbtn@0` → inspect (inbox) → tap Jordan row (`2@1`) →
inspect.

- Inbox inspect `.studio-2f6df457…`: row 1 marker renders `"> Permission slip
  for Friday"` (selmark works); Jordan's row is GestureView `2@1`.
- After tapping Jordan, capture `.studio-d43d06bf…`: `home@0` is visible and
  `inbox@0` is gone; `hsubj@0` = "Design review - 30 minutes on 5 Oct 2026",
  `hbody@0` = Jordan's body, `hdue@0` = "no time confirmed". **Selecting Jordan
  now opens its action card** as required. `checks.pass:true`, `error_count:0`.

**Undo is VERIFIED for Email:** after the tap the receipt fields (`rcpthead`,
`rcptto`, `rcptsubj`, `rcptbody`) are absent from the inspected tree, the notice
confirms removal, and the draft + provenance (`Reply source: Offline sample`)
are kept — the reviewer's "state still contains outbox.m1" failure is fixed.

## Not verified (Email)

- **Live agent path / real normal host** — storage-only preview makes no
  provider call; the operator runs the real host.
- **Restart persistence** — preview storage is disposable.
- The persisted `state.json` bytes were not read back with Studio tools
  (instructed not to mutate/read storage); the fix was validated by observable
  widget state and the `without()` rebuild, not by inspecting the file.
