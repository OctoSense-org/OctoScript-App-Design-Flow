# Android-authored app-card prototypes

English | [简体中文](README.zh-CN.md)

DeepSeek and MiniMax each authored a six-family collection on Android: Mail,
Calendar, News, Finance, Photos and YouTube. Each family has a declarative glance
card and a native Splash app with glance, expanded and full-app views. The current
snapshots preserve **50 model-authored files byte for byte**, with source replay,
original device captures and recorded native interactions.

A separate reviewing agent gave the archived **offline prototypes 4.5/5 overall and
4.4/5 visually**. The overall A− target is met; visual polish alone remains below
it. These are editorial artifact reviews, not human/store approval or a general
model ranking. Local state demonstrations do not send real mail, fetch live
prices, load photos or play videos.

The later [OnePlus 6 workspace review](continuations/deepseek/workspace-ux-20261005/README.md)
found clipped Photo/YouTube/News explanations and overflowing full-app navigation.
Android DeepSeek corrected them after viewing the phone captures. Android
[MiniMax also corrected Mail's L1 Reply route](continuations/minimax/workspace-ux-20261005/README.md).
Exact replacement sources and before/after evidence are preserved separately.
The historical score above is not acceptance of the
current integrated workspace and is not a new 9/10 rating.

## Current collections

| Model snapshot | Source and evidence | Overall / visual |
| --- | --- | --- |
| DeepSeek turn 12 | [Six families, native results and captures](continuations/deepseek/turn-12/README.md) | 4.5 / 4.4 |
| MiniMax turn 14 | [Six families, native results and captures](continuations/minimax/turn-14/README.md) | 4.5 / 4.4 |

The [continuation review](continuations/REVIEW.md) separates each original failed
run from its corrected operator follow-up. It also explains different contexts,
feedback, interruptions and turn counts; this is not an equal-budget benchmark.
MiniMax's whole gallery scores 4.3, separately from its 4.4 component surfaces.

Here L0 means a short glance, L1 an expanded view with local actions, and L2 the
app's list/detail views. These presentation depths do not escalate language or
permissions: declarative `.card` and native `.splash` remain different paths.
The [reference inventory](reference-index.json) records the A2App source material.
Exported-card renders verify pixels, not shell publication or input target sizes.

## Authorship and reproduction

The user required Android models to write designs, source and revisions.
Operators supplied references, feedback, test tools and provenance; they did not
hand-patch apps. Each snapshot carries its exact source receipt, successful model
mutation history and replay report. Model design documents preserve their earlier
checkpoints; later operator reports establish actual verification.

From this directory, check both current source histories without a phone:

```sh
python3 validate-model-authorship.py \
  --case-dir continuations/deepseek/turn-12 \
  --case-dir continuations/minimax/turn-14
```

Each collection documents native reproduction using [reproduce.py](reproduce.py).
[render-glances.py](render-glances.py) renders unchanged card/fixture bytes;
[the workflow](continuations/README.md) explains immutable imports and the
[verified patch semantics](pinned-apply-patch-semantics.json). The
[hash inventory](artifact-inventory.json) covers archived artifacts. Source replay
proves derivation from recorded mutations, not publisher signing or absence of
every possible unrecorded intervention. App Hub/store checks were not run.

The [current cleanup receipt](continuations/cleanup.json) records removed temporary
provider/grant files, stopped test packages and restored screen timeout. No
provider profiles, credentials, device serial or private reasoning are archived.

## Preserved earlier phases

The [three-turn Mail comparison](COMPARISON.md) remains frozen: DeepSeek round 3
scored 3.4 and MiniMax round 3 scored 3.3 for those unfinished artifacts. The
[ten-turn DeepSeek collection](collection/README.md) retains its original 4.1 score
and evidence. Neither historical result is relabelled as the current collection.
Future reviews can use the [review template](REVIEW-TEMPLATE.md); app fixes return
to the phone model, and unrun checks remain explicit.
