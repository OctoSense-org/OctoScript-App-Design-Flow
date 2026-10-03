# Android Mail comparison: evidence draft

English | [简体中文](COMPARISON.zh-CN.md)

**Frozen comparison: DeepSeek round 3 versus MiniMax final round 3. Neither is
an accepted template; no winner is declared here.** MiniMax completed its third
turn. The incoming DeepSeek round 4 repair is excluded from this comparison.
Calendar, News, Finance, Photos and YouTube are outside these Mail test results.

The frozen [provenance record](comparison-provenance.json) contains the collection
time, source/reference hashes, build receipts and tool counts. The archive includes
selected unmodified captures, native reports and successful model source mutations.
Original operator inventory paths in the record are provenance identifiers, not
promises that every original file is included. See [reproduction](README.md#reproduction)
for the parameterized review harness. No provider settings or private reasoning
are included.

## Runtime and copied bytes

Both local build receipts name clean OctoSense commit
`ccf8013f2bd7adbb6c20d5f52f47bcfbcbb55313`, version `2026100306`, standalone
mode, development signing and enabled dev mode. Framework revision is
`2cc5ef37d7d6a3d2992673389ce74488f7bb2d87`; its engine pins are Makepad
`c155f61d0e1600d2ec474209374444a38a09a470` and Octoscript
`5991dfae9344589e732b2605b530f788e8bbcd11`. The build receipts also record
Makepad's applied patch stack; the pins alone are not the complete build.
The shared prebuilt kernel hash is
`4bcfa4f5c60f7e8cad526b49481d40bf0556ce4853aad9c72f853ad866ded1e6`.

| Attempt package | Local APK SHA-256 |
| --- | --- |
| DeepSeek: `dev.makepad.octosense.studio` | `d1dbebdf602f01ee427d68109c500e607b7a5c50fc3f387d5a7c46a1f7b4f882` |
| MiniMax: `dev.makepad.octosense.studio.minimax` | `219a81645c60d315f1d7638e1efa15ab5ff4aa88f06fe0495edf44dbf4c2f34b` |

The collector recomputed both APK hashes and matched the build receipts. A later
independent [installed APK readback](collection/installed-builds-verified.json)
confirmed both installed packages match those receipts. Runtime feature details
not captured by a receipt remain unverified.

All five model files in each of [`attempts/minimax-r3/`](attempts/minimax-r3/source-receipt.json) and
[`attempts/deepseek-r3/`](attempts/deepseek-r3/source-receipt.json) match their original `source-receipt.json` byte lengths
and SHA-256 values. The [independent replay result](model-authorship-validation.json) and the rerun
of the [portable replay helper](validate-model-authorship.py) establish exact
UTF-8 byte matches for all ten files: each file starts from its last successful
Android model write, followed by unique exact edits. Earlier patches were
superseded by later writes; no applicable patch, fuzzy edit or normalization was
inferred. This proves reproducibility from the recorded model arguments, not the
absence of every possible unrecorded historical intervention. All 11 entries in
`reference-index.json` match the available local sources. The index records the
framework, catalog, design-system, Mail/Calendar/News/Finance/YouTube cards,
Photos source and script API documentation supplied as references.

## Native tests

| Saved suite | Passed steps / attempted steps | Tool calls | What the evidence establishes |
| --- | --- | --- | --- |
| MiniMax Mail final round 3 | 7 / 10 raw assertions | 20 | Read/unread, archive/undo and second-message identity work. One failure is changed archive copy, not broken archiving. Full-app view still clips its composer subject label; Send remains unreachable. |
| DeepSeek Mail round 3, keyboard route | 3 / 16 | 10 | Glance, expansion and blank-send validation pass; typing reaches clipped UI and subsequent targets are unavailable. Later failures are a cascade, not 12 independently reproduced defects. |
| DeepSeek Mail round 3, no-keyboard route | 11 / 12 | 26 | Archive/undo and folder filtering work; the second message shows the correct subject but the wrong sender and generic body. Native input targets include a 40-point button and a partially visible 18-point rectangle. |

The MiniMax archive assertion expected “Nothing selected”, but the model now shows
“Message archived”; the inbox count and Undo demonstrate the action. Preserve
that raw failure without treating it as a functional regression.

The generation conditions also differ. DeepSeek's first turn could not use
Studio tools because the developer grant's canonical workspace path did not
match; MiniMax had Studio access in its first turn. DeepSeek continued the prior
Task Planner/Mail conversation, while MiniMax started a fresh conversation. Each
had three prompt turns, but feedback, writes, revisions and tool-call counts
differed. This was not an equal-budget or equal-context comparison.

These are different action sequences and fixtures; raw percentages are not a
controlled model benchmark. The MiniMax suite has no text-input step, so that
report does not establish a typing-triggered keyboard defect. All captures retain
`settled:false`. Geometry checks and observed input behavior do not replace
visual review. Neither suite establishes an A− quality result or full persistence
and error-state coverage.

## Generation counts and timing

Operator-attributed models are DeepSeek V4 Flash and MiniMax M3.1 Flash Preview.
The sanitized transcripts do not independently identify the provider's returned
model ID; this collector does not read provider profiles.

| Completed turn | Recorded tool calls | Successful / failed | Recorded elapsed seconds |
| --- | --- | --- | --- |
| DeepSeek initial design | 20 | 19 / 1 | Not recorded |
| DeepSeek review | 25 | 25 / 0 | Not recorded |
| DeepSeek revision | 29 | 29 / 0 | Not recorded |
| MiniMax initial design | 57 | 52 / 5 | 618.869 |
| MiniMax review | 35 | 30 / 5 | 380.260 |
| MiniMax final review | 45 | 43 / 2 | 263.388 |

A separate DeepSeek background attempt records a turn error and zero tool calls.
Elapsed times above come from the operator polling loop, not provider inference
latency; do not calculate model speed or token cost from these numbers. Eight
DeepSeek and six MiniMax `view_image` completions in the listed completed turns
are explicitly marked `reported_shown_to_model`; that confirms reported image
delivery, not that the model noticed every issue.

MiniMax’s final turn used 45 tool calls despite a requested 24-call limit and
acknowledged the remaining Send blocker. This is recorded alongside its useful
repairs, not omitted from the comparison.

## Admission and acceptance

Both saved source revisions passed **local Studio developer admission** with
`storage` as their sole capability, `publisher_signed:false` and
`source_modified:false`. MiniMax final round 3's admitted digest is
`22d5350a9afcf20bc2c17bb5391e5af0dcb0dec8bc62be598035a30fecaf401f`;
DeepSeek round 3's is
`9281aaec32391be5a274a3ba54764ebf528f653e7d4f3464f41a618c52d90f67`.
These BLAKE3 bundle digests differ from per-file SHA-256 hashes. Both original
manifests contain a literal 64-zero integrity placeholder, preserved in the
recorded model arguments and imported bytes. Exact authorship replay of that
placeholder does not validate real bundle integrity or publisher signing; the
actual local admission digests above come from Studio's separately staged copy.

Local admission does not establish App Hub `hub check`, catalog/store scan,
publisher signing, store approval or publication. All remain unverified here.
Known failing attempts stay review evidence; do not import them as accepted
reusable templates. The phone model must author any design/source corrections.

## Independent artifact scores

The independent reviewer scored only these unfinished Mail artifacts, not the
models' general ability. The criteria below are the reviewer's artifact rubric;
they differ from the blank reusable review form.

| Artifact | Visual | Presentation depths | Interactions | A2App reference use | Verification honesty | Overall / 5 |
| --- | --- | --- | --- | --- | --- | --- |
| DeepSeek round 3 | 3.5 | 3.5 | 3.0 | 3.5 | 3.5 | **3.4** |
| MiniMax final round 3 | 3.5 | 3.0 | 3.5 | 2.5 | 4.0 | **3.3** |

Neither meets the 4.5/5 A− target. A 0.1-point difference between these two
unfinished attempts is not a general model ranking or a declaration of a winner.
The [score record](independent-review.json) preserves scope and attribution.
