# Review of the two six-family continuations

English | [简体中文](REVIEW.zh-CN.md)

DeepSeek turn 12 and MiniMax turn 14 each provide six Android-authored offline
prototype families. A separate reviewing agent inspected original device captures
and operator reports. Both receive **4.5/5 overall and 4.4/5 visually**. These are
editorial artifact judgments, not human/store approval or a general model ranking.
The overall prototype target is met; visual polish alone remains below 4.5.

| Frozen continuation | Source proof | Overall / visual | Scope |
| --- | --- | --- | --- |
| [DeepSeek turn 12](deepseek/turn-12/README.md) | 25/25 exact files | 4.5 / 4.4 | Six offline families; local actions, identity, navigation, keyboard and preview-state routes |
| [MiniMax turn 14](minimax/turn-14/README.md) | 25/25 exact files | 4.5 / 4.4 | Six offline families; local actions, identity, navigation, keyboard and last-item routes |

MiniMax component surfaces score 4.4 and its whole gallery 4.3; DeepSeek has no
separate numeric whole-gallery score. Gallery controls and spacing remain part of
the practical limitations, even when a component score excludes explicit test
chrome. Each detailed review retains its own rubric and remaining polish items.

## What the evidence establishes

DeepSeek's initial suites report 87/99 behavior and 79/99 raw passes. The operator
had omitted States disclosure before twelve state-control attempts; the separate
35-step follow-up passes all behavior/raw checks. Last-item runs retain 25/27
behavior and 23/27 raw, followed by 18/18 behavior and 16/18 raw after correcting
two expected-label strings. Those are separate runs on unchanged source.

MiniMax's final suite reports 114/115 behavior and 113/115 raw passes. The operator
omitted the scroll needed to reveal Mail's last item; a separate four-step native
scroll follow-up passes both measures. Mail's partially visible Queue target in
the typing frame remains a raw finding; the later scroll and queue action pass.
The other five families each pass all 20 behavior/raw steps.

Both final collections have six settled exported glance renders, tied to exact
source/fixture hashes. Native inspect frames retain their reported `settled:false`;
render settling, observed behavior and geometry are separate evidence. Rendering
an exported glance does not validate its input targets or publish it to the shell.
All final native run groups compare 25 source files before and after. Every app,
card, fixture and shared design file came from recorded Android model mutations;
operators wrote test/provenance tools and feedback, not app repairs.

These remain session-state demos. They do not establish live mail/calendar access,
market-data fetching, photo loading, video playback or durable service changes.
Local Studio developer admission is not App Hub validation, signing or publishing.
The model design documents are preserved as written before final operator checks;
later evidence supplies verification without rewriting those historical claims.

## Why this is not an equal-budget comparison

The [three-turn Mail comparison](../COMPARISON.md) stays frozen, as does the prior
[ten-turn DeepSeek collection](../collection/README.md). The later collections
have different turn counts, prior conversation context, feedback and repairs.
DeepSeek already had a six-family base; MiniMax extended its own Mail prototype.
Neither model borrowed the other's generated application source.

MiniMax's history additionally preserves the turn-4 grant-path environment error,
the deliberately interrupted turn 8, the turn-9 collector recovery/read-only
model choice, and hash-bound failed checkpoints. Recorded tool counts supersede
incorrect model self-counts; missing timing remains unknown. These conditions do
not support claims about equal cost, speed, a general winner or provider quality.

The [current cleanup receipt](cleanup.json) confirms removal of temporary provider
and developer-grant files, stopped isolated test packages, restored screen timeout
and unprivileged adb. Historical archives and their earlier receipts stay intact.
