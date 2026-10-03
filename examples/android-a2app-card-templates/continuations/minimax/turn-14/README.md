# MiniMax turn 14: reviewed offline prototypes

English | [简体中文](README.zh-CN.md)

MiniMax on Android authored Mail, Calendar, News, Finance, Photos and YouTube
from its own earlier Mail work. Independent agent [review](visual-review.json) scores
these **offline prototypes 4.5/5 overall and 4.4/5 visually**; the whole gallery
scores 4.3/5. No functional blocker was observed in the exercised final paths.
The overall grade reaches the A− prototype target; visual polish remains below it.
These scores do not establish live-service completion or general model superiority.

All 25 model files are unchanged on import and [replay exactly](model-authorship-validation.json)
from the frozen three-turn base plus recorded turns 4–14. The
[source receipt](source-receipt.json) and [generation record](generation-record.json)
retain that chain. Operators never hand-patched app, card or design source.

The preserved model `DESIGN.md` predates final operator checks. Any pending or
self-reported verification in it is that historical checkpoint; the later
source-bound reports below establish the observed results. Review scores are
editorial judgments by a separate agent, not human approval or store acceptance.

## Native results, including the failed route

| Run | Behavior / steps | Raw passes / steps | Meaning |
| --- | --- | --- | --- |
| [Final six-family suites](evidence/minimax-r14-validation/summary.json) | 114/115 | 113/115 | Mail's last-item selector missed the needed scroll; the original failure remains |
| [Mail scroll follow-up](evidence/minimax-r14-mail-last-followup/summary.json) | 4/4 | 4/4 | Native scrolling reveals Northwind; its full Invoice 2291 title and amount appear at the top |

Both run groups compare all 25 source files before and after, matching this
snapshot. The follow-up does not rewrite the original run as 115/115. Calendar,
News, Finance, Photos and YouTube each pass all 20 behavior and raw steps. Mail
passes 14/15 behavior and 13/15 raw in its initial suite.

Mail covers read/unread, archive/undo, message identity, blank-reply rejection,
typing and local queuing with the actual Android keyboard. In the typing frame,
the visible Queue reply target is 129 × 22 logical points; the next scroll reveals
it and queuing succeeds. That raw finding stays recorded: there is no blanket
44-point claim. Calendar covers independent RSVP and all-declined state. The four
other families cover second/last-item identity, reversible state, filtered lists,
expanded actions and returning from a selected item to the displayed lead.

All six [exported glances](evidence/glances/report.json) render and report
`settled:true`, with exact card, fixture and PNG hashes. Native inspect frames
retain `settled:false`; this differs from observed behavior and geometry checks.
Glance rendering proves neither exported-card input targets/events nor shell
publication. L0/L1/L2 here remain presentation depths, not permission levels.

## Selected original captures

| Family | Exported glance | Expanded | Full-app detail |
| --- | --- | --- | --- |
| Mail | [Glance](evidence/glances/mail.png) | [Expanded](evidence/minimax-r14-validation/mail/01-expanded.png) | [Northwind after scroll](evidence/minimax-r14-mail-last-followup/03-northwind-detail.png) |
| Calendar | [Glance](evidence/glances/calendar.png) | [Expanded](evidence/minimax-r14-validation/calendar/01-expanded.png) | [Last event](evidence/minimax-r14-validation/calendar/05-last-detail.png) |
| News | [Glance](evidence/glances/news.png) | [Expanded](evidence/minimax-r14-validation/news/01-expanded.png) | [Last story](evidence/minimax-r14-validation/news/10-last-item-detail.png) |
| Finance | [Glance](evidence/glances/finance.png) | [Expanded](evidence/minimax-r14-validation/finance/01-expanded.png) | [Last instrument](evidence/minimax-r14-validation/finance/10-last-item-detail.png) |
| Photos | [Glance](evidence/glances/photo.png) | [Expanded](evidence/minimax-r14-validation/photo/01-expanded.png) | [Last item](evidence/minimax-r14-validation/photo/10-last-item-detail.png) |
| YouTube | [Glance](evidence/glances/youtube.png) | [Expanded](evidence/minimax-r14-validation/youtube/01-expanded.png) | [Last item](evidence/minimax-r14-validation/youtube/10-last-item-detail.png) |

The [actual keyboard capture](evidence/minimax-r14-validation/mail/11-send-scroll-keyboard-android.png)
shows the revealed Queue control. [Finance's second instrument](evidence/minimax-r14-validation/finance/03-second-item-detail.png)
shows the complete red −0.38 and correct identity. The [index](evidence/index.json)
lists 20 original PNGs, matching native snapshots, all seven raw reports and
complete tool-call records. Input steps are unchanged; only absolute operator
source-path metadata was made relative, with original hashes retained. Other
capture names in raw reports/review refer to operator originals omitted here.

## Limits and retained history

The reviewer scores hierarchy/compactness 4.3, depth navigation 4.6, state/keyboard
4.6, coherence/honesty 4.4 and source-bound evidence 4.6. Native Mail rows and some
details retain large gaps; strong actions, red DEMO badges and technical depth
labels compete with content. Component surfaces score 4.4, distinct from the
whole gallery's 4.3. State is local to the session, with no real mail delivery,
live prices, photo loading or video playback; unavailable media is labelled.

The [history index](history/index.json) preserves turn 4's operator grant error,
turn 8's deliberate interruption, turn 9's collector recovery and read-only model
choice, hash-bound intermediate diagnostics, and final-turn-12 News admission
success followed by open failure. Later repairs do not erase failed checkpoints.
The [source comparison](source-binding.json) confirms turn 14 changed only six
bare theme declarations and `DESIGN.md`—seven files, not the model's claimed nine.
Native scripts/manifests and fixtures are unchanged from turn 13. Actual tool
counts come from transcripts, not model self-reports. Patch replay uses the
[verified Android kernel contract](../../../pinned-apply-patch-semantics.json).

The [current cleanup receipt](../../cleanup.json) confirms both test packages'
temporary provider/grant files were removed, the packages stopped and the original
60-second screen timeout restored. Local developer admission is distinct from
unrun App Hub checks, signing, publishing and production integration.

## Reproduce

From this `turn-14/` directory, after provisioning archived source and developer
grants in an authorized test package, use explicit operator values:

```sh
python3 ../../../reproduce.py --runtime-root /path/to/OctoSense \
  --serial DEVICE_SERIAL --package dev.makepad.octosense.studio.minimax \
  --workspace /data/user/0/dev.makepad.octosense.studio.minimax/files/TRUSTED_WORKSPACE \
  --suite evidence/minimax-r14-mail-last-followup/suite.json \
  --output /path/to/new-mail-followup
python3 ../../../validate-model-authorship.py --case-dir continuations/minimax/turn-14
```

The first command uses the device; the second replays local provenance only.
Run summaries record the actual helper hash. The [continuation review](../../REVIEW.md)
compares artifact evidence while preserving unequal histories and feedback.
