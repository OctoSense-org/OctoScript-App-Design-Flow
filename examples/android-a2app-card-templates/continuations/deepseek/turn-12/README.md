# DeepSeek turn 12: reviewed offline prototypes

English | [简体中文](README.zh-CN.md)

This continuation contains DeepSeek's six Android-authored families: Mail,
Calendar, News, Finance, Photos and YouTube. Independent agent [review](visual-review.json) scores the
**offline prototype 4.5/5 overall and 4.4/5 for visuals**. No functional blocker
was observed in the exercised paths. These are artifact scores, not a general
model ranking, store approval or a claim that every visual check passed.

All 25 model files are unchanged on import. The [receipt](source-receipt.json),
[strict replay](model-authorship-validation.json) and
[generation record](generation-record.json) connect the prior ten-turn collection
to turns 11 and 12. Tests compared all 25 source files before and after every
native run group; their receipts match this snapshot. No app code was hand-patched.
The earlier [collection](../../../collection/README.md) and three-turn Mail
comparison remain separate historical evidence.

The preserved model `DESIGN.md` predates final operator checks. Any pending or
self-reported verification in it is that historical checkpoint; the later
source-bound reports below establish the observed results. Review scores are
editorial judgments by a separate agent, not human approval or store acceptance.

## Observed behavior and retained failures

| Run group | Behavior / steps | Raw passes / steps | Interpretation |
| --- | --- | --- | --- |
| [Initial native suites](evidence/deepseek-r12-validation/summary.json) | 87/99 | 79/99 | Twelve operator target failures: four domain suites tried Empty/Error/Ready before opening States |
| [States follow-up](evidence/deepseek-r12-preview-followup/summary.json) | 35/35 | 35/35 | Mail and four domain families open States, exercise Loading/Empty/Error/Ready, then close it |
| [Last-item suites](evidence/deepseek-r12-last-item/summary.json) | 25/27 | 23/27 | Finance/Photos used two wrong expected empty-label strings; YouTube passes all nine steps |
| [Copy-corrected follow-up](evidence/deepseek-r12-last-item-copy-corrected/summary.json) | 18/18 | 16/18 | Finance passes 9/9 behavior and 7/9 raw; Photos passes 9/9 both |

Runs stay separate: the archive retains original failed reports and input suites,
alongside the corrected operator inputs. No model source changed between them.
`behavior_pass` covers actual assertions; raw `pass` additionally includes native
geometry and enabled-button target checks. Remaining raw findings include scroll
viewport/keyboard clipping; they are not erased or counted as an all-bounds pass.

Mail's 12-step app suite and 9-step keyboard suite pass all behavior assertions:
blank-send validation, archive/undo, message identity, typing, reachable local-demo
Send and draft retention. Calendar passes all 22 behavior steps, including
independent per-event RSVP and last-event detail opening at its heading. Domain
suites exercise reversible per-item state, second-item identity and filters;
follow-ups verify disclosed preview states and last-row detail navigation.
Finance's third item needs native scrolling, and the last Finance/Photos/YouTube
detail captures show their headings at the top.

The six [exported glance renders](evidence/glances/report.json) pass and settle,
with exact card/fixture hashes. Their source is unchanged from turn 11: these are
fresh verification, not evidence of further glance improvement in turn 12.
Rendering proves neither exported-card interactions nor shell publication or
44-point input targets. Native app snapshots continue to report `settled:false`;
that flag is retained separately from their observed behavior and geometry checks.

## Selected original captures

| Family | Exported glance | Expanded/native interaction | Full-app route |
| --- | --- | --- | --- |
| Mail | [Glance](evidence/glances/mail.png) | [Actual Android keyboard and Send](evidence/deepseek-r12-validation/mail-keyboard/05-send-reachable-with-keyboard-android.png) | [Inbox](evidence/deepseek-r12-validation/mail/08-full-app.png) |
| Calendar | [Glance](evidence/glances/calendar.png) | [Expanded](evidence/deepseek-r12-validation/calendar/01-expanded.png) | [Last-event detail](evidence/deepseek-r12-validation/calendar/12-last-event-detail.png) |
| News | [Glance](evidence/glances/news.png) | [Expanded](evidence/deepseek-r12-validation/news/03-expanded.png) | [Collection](evidence/deepseek-r12-validation/news/04-full-app.png) |
| Finance | [Glance](evidence/glances/finance.png) | [Expanded](evidence/deepseek-r12-validation/finance/03-expanded.png) | [Last instrument](evidence/deepseek-r12-last-item-copy-corrected/finance/03-last-detail-top.png) |
| Photos | [Glance](evidence/glances/photo.png) | [Expanded](evidence/deepseek-r12-validation/photo/03-expanded.png) | [Last item](evidence/deepseek-r12-last-item-copy-corrected/photo/03-last-detail-top.png) |
| YouTube | [Glance](evidence/glances/youtube.png) | [Expanded](evidence/deepseek-r12-validation/youtube/03-expanded.png) | [Last item](evidence/deepseek-r12-last-item/youtube/03-last-detail-top.png) |

The [evidence index](evidence/index.json) identifies all 18 original PNGs and their
matching native snapshots, plus every raw report, complete operator tool-call
record and actual input suite. Other capture names in reports refer to operator
originals omitted from this compact archive. Only the marked Android screen
capture includes the system keyboard; ordinary app textures do not.

## Review limits and reproduction

The five [review criteria](review-status.json) score hierarchy/compactness 4.2,
depth navigation 4.6, state/keyboard 4.6, coherence/honesty 4.5 and source-bound
evidence 4.6. The overall 4.5 reaches the A− prototype target; visual quality alone
is 4.4. Mail/Calendar retain large gaps, and Finance has a stray `0` in gallery
status. Component quality and whole-screen/gallery limitations remain distinct.

These are offline session-state demonstrations. Mail does not send real mail;
RSVP/save/watch changes are not durable service records. Photos and YouTube mark
media unavailable. No App Hub gate, signing, publishing or production integration
is established. The [current cleanup receipt](../../cleanup.json) confirms both test packages'
temporary provider/grant files were removed, the packages stopped and the original
60-second screen timeout restored. Earlier cleanup remains historical evidence.

From this `turn-12/` directory, with archived source already provisioned in the
authorized test package and current developer grants, use explicit operator values:

```sh
python3 ../../../reproduce.py --runtime-root /path/to/OctoSense \
  --serial DEVICE_SERIAL --package dev.makepad.octosense.studio \
  --workspace /data/user/0/dev.makepad.octosense.studio/files/TRUSTED_WORKSPACE \
  --suite evidence/deepseek-r12-validation/calendar/suite.json \
  --output /path/to/new-calendar-evidence
python3 ../../../validate-model-authorship.py --case-dir continuations/deepseek/turn-12
```

The first command uses the device and preserves raw failures in its exit status;
the replay command is local only. Each run summary records the executed helper
hash. The [continuation workflow](../../README.md) covers immutable imports,
source binding and separate model histories.
