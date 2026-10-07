# Six-family continuation workflow

English | [简体中文](README.zh-CN.md)

The [current review](REVIEW.md) covers DeepSeek turn 12 and MiniMax turn 14,
each with 25 exactly replayed source files, native evidence and six settled
exported glances. Independent agent review scores each offline prototype 4.5/5
overall and 4.4/5 visually. Failed runs and corrected follow-ups remain separate;
[current cleanup](cleanup.json) is complete. Only the phone models may change
app designs, source and fixtures; operators prepare references, feedback, test
harnesses and provenance.

The [three-turn Mail comparison](../COMPARISON.md) stays frozen. The existing
[DeepSeek ten-turn collection](../collection/README.md) remains a separate reviewed
snapshot with its original 4.1/5 visual assessment. Later family coverage and
revision counts are not an equal-budget benchmark or a general model ranking.
Each model continues its own source history; one model's apps are not the other's
starting point.

## Freeze and import source

Use separate immutable destinations: `deepseek/turn-N/` and `minimax/turn-N/`.
Keep incomplete turns outside this repository. After the operator freezes all
25 files (six families × four files plus shared `DESIGN.md`), run from the parent
`android-a2app-card-templates/` directory:

```sh
python3 import-snapshot.py --source-root /path/to/frozen-source \
  --base-case collection --model deepseek --round 11 \
  --turn-dir /path/to/deepseek-11-collection-completion \
  --frozen-source --dry-run
```

For MiniMax, start with `--base-case attempts/minimax-r3 --model minimax`, supply
its final round number and repeat `--turn-dir` for every subsequent turn in
chronological order. A later import may use that model's previous continuation
snapshot as its base. Remove `--dry-run` only when the input is frozen and the
retained mutation arguments have been reviewed for private data.

The importer carries forward successful mutations, copies exact source bytes,
checks the receipt and replays later edits in memory. It refuses missing/extra
files, symlinks, duplicate turns, changed receipts, existing destinations and
unreproducible edits. Only mutation arguments and aggregate turn counts/hashes are
retained; reasoning, assistant responses and unrelated tool outputs are excluded.
The private-path guard is not a general secret detector. Never redact source
arguments to manufacture a successful replay. Record unresolved proof gaps and
keep that snapshot outside the completed archive.

Patch replay follows the verified Android kernel's **first matching block at or
after the forward cursor**, including context-only `@@` hunks that advance that
cursor. Repeated blocks therefore have a deterministic meaning; global uniqueness
is not the kernel contract. The [semantics receipt](../pinned-apply-patch-semantics.json)
links the source revision to the cross-built binary, both archived APKs and their
installed-hash receipts. This is build evidence, not reproducible-build attestation.

Only the exact subset is accepted: the earliest candidate under the runtime's
trailing-whitespace comparison must also match byte for byte. An earlier fuzzy
candidate causes refusal, even if a later exact match exists. No backtracking or
whitespace normalization is allowed. Bare `@@` Update File hunks, LF source and a
final newline are required; add/delete/move commands, extended markers and
unanchored insertions remain unsupported. Failed calls are excluded; a failed
validation patch is atomic in this pinned runtime. Complete successful mutation
arguments and exact final source hashes are still required. The recorded patch
is retained without inventing a replacement write. A different runtime needs its
own verified tool contract before this replay can support an authorship claim.

Include interrupted turns in chronological history. When a turn directory has
`operator-interruption.json`, the importer checks its tool/final counts against
the transcript and preserves the receipt unchanged under `turn-evidence/`.
Generation records label that turn `operator_interrupted`; zero assistant finals
must never be presented as a completed model response. Keep operator environment
or guidance errors distinct from model-quality findings.

The import status is **source replayed; native and visual review pending**.
Authorship replay proves derivation from recorded mutations, not absence of every
possible unrecorded intervention, real bundle integrity or publisher signing.

## Bind tests and review to each snapshot

Before recording results, hash the exact `main.splash`, manifest, card and fixture
used by that run. Keep local developer admission digests separate from source
SHA-256. If a later manifest differs, rerun admission and record that change;
a matching script hash alone does not establish the same admitted bundle.

Keep each snapshot's original reports, selected PNGs and corresponding native
snapshots together. Record the runtime commit/build/APK, actual helper hash,
turn history, tool counts and available timing. Preserve raw geometry findings
separately from behavioral assertions. Operator-supplied tests earn no evidence
credit until the behavior is actually observed. Rendered exported glances prove
neither shell publication nor interaction target size.

Use the same five review criteria for both models: visual hierarchy/compactness;
reachable L0/L1/L2 navigation; correct reversible per-item state including keyboard
flows; coherent family styling and honest offline limits; source-bound native
and visual evidence. Report component and whole-screen/gallery scores separately.
The target is at least 4.5/5 overall with no functional blockers; a passing import
or supplied test suite does not establish that result.

Local checks need neither a phone nor provider:

```sh
python3 test-import-snapshot.py
python3 validate-model-authorship.py --case-dir collection
```

After a continuation is imported, pass its archive-relative directory to
`--case-dir`; repeat the option to check both model histories independently.
