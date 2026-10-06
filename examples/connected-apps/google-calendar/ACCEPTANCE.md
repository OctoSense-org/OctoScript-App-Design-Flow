# Calendar sample acceptance — 2026-10-06

Scope: ordinary App Hub sample, Splash full app plus an embedded L0 Glance
publication. Source authored, native inputs driven and screenshots reviewed by
Codex's Calendar sub-agent. No DeepSeek/MiniMax authorship or live model result
is claimed.

Final native-tested `main.splash` SHA-256:
`189c2666cd05ac92c3665f66cb890bf9e4acf421378d67ed95520fb4697e6797`.
The verifier writes binary, runtime, manifest-contract and screenshot hashes to
`.local-state/native-evidence/receipt.json`. That file is local evidence, not a
provider account export. All public captures contain synthetic data.

`storage.accounts` is enabled so peer identity and host OAuth connection
selection use the same account. The native journeys were rerun after this
manifest correction; the receipt includes its final manifest contract hash.

## Checks executed

`python3 examples/connected-apps/google-calendar/scripts/verify-native.py`
(from the flow root) executed five native journeys through the Makepad instrument on an owned hidden macOS card-host.
The equivalent root-relative command is in README. Final result: **5 passed**.

| Journey | Observed result |
| --- | --- |
| Fresh startup | Complete empty agenda; actual missing OAuth service reported |
| Timed-event editor | Title, both dates/times, timezone, location and multiline notes typed natively; exact values written to local draft |
| Review without account | Visible actionable error; exact draft retained |
| Restart | Exact edited values and all-day choice restored; notes reachable by scrolling |
| Account and calendar navigation | Real unavailable-service callback displayed; return navigation works |

The verifier confirms relevant controls have at least 40 logical points of
visible height before clicking; authored action buttons are 44 points. Screens
were reviewed at a 412 × 860 logical-point app viewport (824 × 1784 capture
including host caption). The editor keeps the compact action row outside its
scroller. The native desktop check does not simulate a phone soft keyboard.

Public original captures, inspected after the final code changes:

- `bundle/screenshots/01-local-draft.png`: retained all-day draft after restart.
- `bundle/screenshots/02-notes.png`: multiline notes and reachable actions.
- `bundle/screenshots/03-host-required.png`: real missing OAuth host service.
- `bundle/screenshots/04-glance-template.png`: exact embedded L0 template with
  synthetic event data; this is not a shell route or agent-chat result.

`python3 examples/connected-apps/google-calendar/scripts/verify-glance.py`
extracts the embedded template without rewriting it, supplies explicit fixture
data and renders it through the native instrument. Final result: **L0 lint and
render passed**, 10 realized nodes; Open Calendar, timezone and chat input are
visible. The local receipt records source/template/capture hashes.

`cargo test --locked -p octosense-oauth-service calendar_cache --lib` in the
companion OctoSense checkout: **8 passed**. These fixture tests verify atomic
page commit, failed-page preservation, HTTP 410 full reset, cancelled-event
removal, identity separation, page-loop/incomplete-result rejection, DST gap
and repeated-hour rejection, all-day inclusive editor dates, timezone handling
and bounded Glance metadata. They do not call Google.

`tools/octo check examples/connected-apps/google-calendar/bundle`:

```text
org.octosense.samples.googlecalendar 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"auth", "gcalendar", "glance", "octos.session.open", "octos.turn.start", "storage"}, hosts {}, storage 1048576 bytes, agent read-only
```

The wrapper also reports listing publisher placeholders; admission is not
publication readiness. `hub scan` wrote `build/review.json`; the current scanner
asks **eight** questions, answered in `build/REVIEW-ANSWERS.md`.

The companion OctoSense `connected-install` example also passed against all
three actual connected sample bundles. It uses ephemeral publisher, working
and anchor keys to sign temporary copies, admits a private signed catalog,
installs through `Store::install_staged`, reopens through `Store::may_run` and
checks the exact capabilities and account-scoped storage. Modified installed
source, cross-app staging, unsigned catalogs and an untrusted anchor were
refused. Input bundles stayed unchanged; temporary fixture removal was checked.
The local receipt is `OctoSense/target/connected-install/receipt.json`. This proves
the signed installation boundary, not public catalog acceptance or live services.

## Failures retained and repaired

1. The first editor layout wasted vertical space on an unrelated global service
   status; the final editor hides that row and places dates/times side by side.
2. A restart check failed with `no getter for field kind on type nan` because
   object `+=` did not merge parsed JSON in this runtime. Replaced it with explicit
   key assignment. The failed screenshot remains under `.local-state/`.
3. Real typing exposed duplicate JSON keys when a string key updated an object
   initially created with identifier keys. Draft/default state is now normalized
   through JSON before dynamic writes. The exact saved-content and restart tests
   caught the issue and pass after repair.
4. The initial notes input was tall but single-line. It now declares
   `is_multiline: true`; the final test enters and verifies a newline.
5. The initial L0 template used arbitrary `sys.dataset` field names, which the
   runtime rejects. The published payload now maps event fields onto the allowed
   vocabulary. Its separate native fixture also needs the real runtime L0 kit.

## Remaining acceptance

Not verified: real OAuth consent, Google read/create/edit, host approval,
ETag-conflict UI, provider-backed populated agenda/detail, integrated Glance
expansion and same-event route, card/app agent conversations, Android keyboard and lifecycle,
Linux or Windows execution. No numeric UX grade or production sign-off is
claimed while those core paths remain unverified. Recurrence expansion/editing,
attendee invitations and agent-driven event mutation are outside this sample's
implemented scope. Owned native test instances were quit after their runs.
