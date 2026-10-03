# Six Android-authored app-card families

English | [简体中文](README.zh-CN.md)

DeepSeek on Android authored Mail, Calendar, News, Finance, Photos and YouTube
prototypes from existing A2App references. Each family has an exported declarative
glance card and a Splash app with glance, expanded and full-app presentation.
**These are reviewed prototypes, not an accepted template collection.**
All 25 final model files are imported unchanged, including Calendar's verified
scroll-navigation repair and the shared design document.

The user's authorship rule applies throughout: the phone model writes designs,
source and revisions. Supervising agents provide references, review feedback,
operator tools and evidence. They do not repair generated app code by hand.
The [reference inventory](../reference-index.json) records the A2App material.
L0/L1/L2 here mean presentation depth; they do not escalate the card language or
establish publication to the shell's glance screen.

## What native checks establish

| Family | Independently observed behavior | Full behavior suite: assertions / raw pass |
| --- | --- | --- |
| Mail | Blank-reply validation, archive/undo, folder filtering, correct second-message identity; separate keyboard route types, scrolls to a 44-point Send control and queues a local-demo reply | 12/12 and 12/12; keyboard 7/7 and 5/7 |
| Calendar | Per-event RSVP independence, list/week navigation and last-row detail opening at its heading after the model repair | Final regression 21/21 and 18/21 |
| News | Reversible per-story save, second-story identity, saved collection, empty/error/ready states | 14/14 and 14/14 |
| Finance | Reversible per-instrument watch, second instrument, watched collection, empty/error/ready states; last row and its detail are reachable | 14/14 and 12/14 |
| Photos | Reversible per-item save, second item, saved collection, empty/error/ready states; last row and detail are reachable | 14/14 and 12/14 |
| YouTube | Reversible per-item save, second item, saved collection, empty/error/ready states; last row and detail are reachable; no enabled Play control in the tested views | 14/14 and 12/14 |

The [evidence summary](evidence/summary.json) retains raw counts and admission
results. `behavior_pass` covers observed assertions; raw `pass` additionally
requires native geometry checks and no small enabled buttons. Finance/Photos/
YouTube raw failures include viewport-edge text clipping; keyboard raw failures
include scroll-boundary clipping while the IME is open. These findings remain in
the original reports, even when independent visual review identifies their scope.
No all-bounds pass is claimed. Calendar's two old “You're going” expectations
changed to “Going (demo)”; that copy mismatch is separate from the retained-scroll defect fixed in the final
revision. The final 21-step Calendar run preserves three viewport-edge clipping
findings; all behavior assertions pass.

All six exported glance cards rendered at 968 pixels wide with `settled:true`:
Mail/Calendar 509 pixels high, News 587, Finance 589, Photos/YouTube 573.
[Render evidence](evidence/glances/report.json) binds those captures to exact card
and fixture hashes. This is render-only evidence: no exported-card action or
44-point target claim follows from it. In particular, Mail's secondary Archive
and Calendar's Details actions lack independent 44-point input evidence.

## Selected original captures

| Family | Exported glance | Expanded/native interaction | Full-app branch |
| --- | --- | --- | --- |
| Mail | [Glance](evidence/glances/mail.png) | [Android keyboard and reachable Send](evidence/mail-keyboard-final-suite/03-send-reachable-with-keyboard-android.png) | [Inbox](evidence/mail-release-suite/02-full-app.png) |
| Calendar | [Glance](evidence/glances/calendar.png) | [Expanded](evidence/calendar-scroll-fixed-suite/01-expanded.png) | [Corrected last-event detail](evidence/calendar-scroll-fixed-suite/12-last-event-detail.png) |
| News | [Glance](evidence/glances/news.png) | [Expanded](evidence/news-release-suite/01-expanded.png) | [Collection](evidence/news-release-suite/02-full-app.png) |
| Finance | [Glance](evidence/glances/finance.png) | [Expanded](evidence/finance-release-suite/01-expanded.png) | [Last instrument detail](evidence/finance-release-suite/04-last-item-detail.png) |
| Photos | [Glance](evidence/glances/photo.png) | [Expanded](evidence/photo-release-suite/01-expanded.png) | [Last item detail](evidence/photo-release-suite/04-last-item-detail.png) |
| YouTube | [Glance](evidence/glances/youtube.png) | [Expanded](evidence/youtube-release-suite/01-expanded.png) | [Last item detail](evidence/youtube-release-suite/04-last-item-detail.png) |

PNG files are unchanged originals. App captures have matching full native
snapshots beside them. The Mail keyboard image is an actual Android screen
capture; other app textures do not include the keyboard. Raw reports mention
additional operator captures that were intentionally omitted from this compact
archive. Final selection is limited to 18 images.

## Source, limits and review status

`card-templates/` contains all six model-authored families and the shared
[`DESIGN.md`](card-templates/DESIGN.md). The [final receipt](source-receipt.json),
[ten-turn generation record](generation-record.json) and
[independent authorship replay](model-authorship-validation.json) bind all 25
files to successful recorded Android model mutations. The portable replay also
matches every byte without normalization. This establishes derivation from those
records, not absence of every possible unrecorded intervention. The preserved
[round 9 receipt](revisions/deepseek-round9/source-receipt.json) documents the
pre-fix snapshot separately.

Calendar's model repair recreates a `ScrollYView` subtree through
`stage.on_render` when changing views. Detail remains inside that new scroll
subtree; no invented script scroll-reset API is used. The independent final suite
opened the last event after scrolling, verified its complete title/date/location
at the top and checked that changing its RSVP preserved the first event's Maybe
response. Its newer report supersedes the model's earlier verification checkpoint
without editing `DESIGN.md`.

The other five `main.splash` hashes match the source captured for their full
behavior checks. Later manifests remove unused storage capability; their separate
release suites establish local admission with empty capabilities. Source binding
is recorded in the evidence summary. The examples keep state in memory: saved,
watched, RSVP and queued-reply state are local session demonstrations, not durable
records or external actions. They do not sync mail/calendar, fetch live prices,
load photos or play videos. Photos and YouTube explicitly mark media unavailable.

Unsigned Studio developer admission is separate from App Hub `hub check`, store
scan, publisher signing and publication; those checks were not run here. Manifest
integrity placeholders are not real digest attestations.

The [final independent visual review](visual-review.json) scores the collection
**4.1/5**, below the **4.5/5 A− target**. It assesses rendered components while
excluding explicit gallery test chrome from component scores; whole-screen
spacing and gallery controls remain usability limitations. Tall rows, dominant
primary glance chips and unavailable media keep this a prototype collection.
The [frozen Mail comparison](../COMPARISON.md) remains historical evidence, not
a general model ranking.

## Reproduce checks

[reproduce.py](../reproduce.py) drives native tap/text/scroll, checks forbidden
enabled buttons and reports `behavior_pass` separately from geometry and the
combined result. It rejects enabled buttons below 44 logical points by default;
`--allow-small-targets` reproduces historical comparison scoring only.
[render-glances.py](../render-glances.py) copies exact model card/fixture bytes to
fresh test-package scratch space and invokes the OctoSense AppStudio renderer on
Android. Run the following commands from this `collection/` directory.
The first command validates arguments only; remove `--dry-run` to render.

```sh
python3 ../render-glances.py --runtime-root /path/to/OctoSense \
  --serial DEVICE_SERIAL --package dev.makepad.octosense.studio \
  --workspace /data/user/0/dev.makepad.octosense.studio/files/TRUSTED_WORKSPACE \
  --output /path/to/new-glance-evidence \
  --families mail calendar news finance photo youtube --dry-run
```

Use an unlocked authorized test device, existing developer grants, exact archived
source bytes and a new output directory. Neither helper installs or publishes.
The parameterized helpers also ran on the actual Android test device:
`reproduce.py` drove the final 21-step Calendar regression (21 behavior passes,
18 raw passes; exit 1 retained the three clipping findings), and
`render-glances.py` rendered all six families successfully. Helper hashes are
recorded in [the evidence summary](evidence/summary.json).

From this `collection/` directory, after provisioning the archived source in the
trusted test workspace, rerun the native suite with explicit operator values:

```sh
python3 ../reproduce.py --runtime-root /path/to/OctoSense \
  --serial DEVICE_SERIAL --package dev.makepad.octosense.studio \
  --workspace /data/user/0/dev.makepad.octosense.studio/files/TRUSTED_WORKSPACE \
  --suite evidence/calendar-scroll-fixed-suite/suite.json \
  --output /path/to/new-calendar-evidence
```

No phone or provider is needed for
`python3 ../validate-model-authorship.py --case-dir collection`: strict replay
checks all 25 final files and refuses missing/extra files, ambiguous edits or
unsupported patches. Local runtime/build/APK details are recorded separately in
[runtime provenance](runtime-provenance.json). Independent [installed APK readback](installed-builds-verified.json)
matches both packages to their clean build receipts and the published
[OctoSense runtime commit](https://github.com/OctoSense-org/OctoSense/commit/ccf8013f2bd7adbb6c20d5f52f47bcfbcbb55313).
The [cleanup receipt](final-cleanup.json) records removal of temporary provider
configuration and developer grants, stopped test packages and restored screen
timeout; production Home and the ROM were unchanged.
