# Calendar sample acceptance — 2026-10-06

Scope: ordinary App Hub sample, Splash full app plus an embedded L0 Glance
publication. Source authored, native inputs driven and screenshots reviewed by
Codex's Calendar sub-agent. No DeepSeek/MiniMax authorship is claimed. A later advisory-chat
acceptance run used real DeepSeek v4 Flash with synthetic Calendar data, as
recorded below; Google Calendar itself remained a local provider fixture.

Final native-tested `main.splash` SHA-256:
`7292894f1576d2283726eeafdb79742bd6fe6fb9a651cb1646462bbde4185ff0`.
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

## Signed installed app and provider-boundary acceptance

The additional installed-app journey uses the real signed App Hub Store,
`prepare_launch`, contained app identity, shared OAuth/Calendar services,
immutable host review, native widgets, cache and restart. A non-default
`acceptance-fixtures` build substitutes only the provider transport and token
vault inside a marked temporary profile. Its synthetic account is not Google
OAuth; its native instrument approvals are not physical-input acceptance.

From the companion OctoSense checkout:

```sh
cargo build --locked --release -p octosense-shell \
  --features mobile-apps,acceptance-fixtures \
  --example connected-app-host --example connected-inbox-e2e --example connected-install
```

From the Flow root:

```sh
python3 examples/connected-apps/google-calendar/scripts/verify-installed.py \
  --host ../OctoSense/target/release/examples/connected-app-host
```

Final result: **8 cases passed**, rerun after the final host cancellation and
modal-input changes against App Hub
`5c7a13f92fa25d36ba1fe7fb99dc9fb1b235f8d3`. The replacement review,
conflict and offline screenshots were inspected. The `.local-state/installed-evidence/` receipt
binds the source and actual executable hashes to screenshots and the final
synthetic provider state. The verifier creates its own ephemeral signed
installation; it never enables unsigned developer mode or uses real credentials.

| Journey | Observed result |
| --- | --- |
| Signed first install and reopen | The running app comes from the verified Store installation |
| Populated agenda | Two synthetic provider events are visible |
| Exact review and cancel | Title, timezone offset, location and notes match the frozen draft; cancel makes zero writes |
| Create and reopen | Provider result and reopened event contain the exact submitted values |
| Edit | PATCH supplies the saved event's ETag |
| Conflict | One stale PATCH returns 412; no retry or remote overwrite; exact draft retained; error exposes Back and no consumed Approve button |
| Offline restart | Saved agenda remains visible when provider and calendar-list retrieval fail |
| Draft restart | The conflicting local title survives restart |

Original native captures, inspected after the final review-button correction:

- [Exact create review](evidence/02-host-create-review.png)
- [Conflict with reachable return action](evidence/07-visible-conflict-error.png)
- [Offline restart with cached agenda](evidence/08-offline-restart-cached-agenda.png)

`cargo test --locked -p octosense-oauth-service
calendar_provider_boundary_create_reopen_edit_conflict_and_restart --lib`
also **passed**. It exercises the stateful synthetic provider through the actual
API and cache, including saved/reopened values, ETag conflict without retry,
connection restart, stable card identity and cross-app cache isolation.

## Shared Glance and installed app routing

```sh
python3 examples/connected-apps/google-calendar/scripts/verify-shell.py \
  --shell ../OctoSense/target/release/examples/connected-inbox-e2e \
  --installer ../OctoSense/target/release/examples/connected-install
```

Result: **6 cases passed** in an owned hidden macOS desktop shell. The signed
Calendar app publishes its actual L0 card. Selecting a different event and
clicking the card's in-body **Open Calendar** returns to the original event.
The app's **Chat** page shows that event and a reachable input. After quitting
and restarting the shell without opening the app, the card restores before any
agent consent; **Open Calendar** launches the installed app and selects the
same event. The original publication time and expiry do not change.

- [Restored card before the app opens](evidence/04-restored-glance-without-open-app.png)
- [Cold route opens the original event](evidence/05-cold-exact-event-route.png)
- [Portable source, executable and capture hashes](evidence/acceptance.json)

The desktop Glance panel opens automatically when a new card appears. Its
custom-drawn controls are not included in `/snap`; the driver uses visually
reviewed coordinates at its checked 1400 × 899–900 logical viewport and records
original captures. Earlier driver runs exposed startup timing, window rounding
and panel-dismiss sequencing assumptions; these failures are retained locally
and are not reported as product failures. One later instrument capture returned
HTTP 404; its failure receipt remains local, and an unchanged rerun completed
all seven model-enabled cases.

The restored-publication regression
`foreground_cards_restore_before_agent_consent_without_bypassing_revocation`
passed in `octosense-shell`: explicit denial and missing capability still block
restoration, while an ordinary foreground publication does not require first
agent use. Account and signed-out checks remain part of the real restore path.

## Real DeepSeek advisory chat

The full-shell verifier was rerun with `--model-profile /private/path/profile.json`
and `--kernel /path/to/octos`, using the person's existing approved DeepSeek
configuration in an isolated temporary home. The actual model was
**DeepSeek v4 Flash**. No profile, credential or real account data enters the
bundle or public evidence.

Result: **7 cases passed**, including the six shell journeys above. The final
first-use sheet names **Google Calendar** and describes **No files: only what
its tools return**. After consent and an explicit resend, the app's advisory
conversation called `googlecalendar.event` through its ordinary contained peer
and the real host tool mapping. The audit records `risk: read`, `decision:
allowed`, `outcome: ok`. The tool returned the selected synthetic event, and
DeepSeek answered its title, 09:00 Pacific start and Fixture room location.
The synthetic provider recorded **zero POST, PATCH or DELETE calls**.

- [Corrected actual consent sheet](evidence/06-agent-consent.png)
- [Actual model answer in the Calendar app](evidence/07-real-advisory-model-answer.png)

The portable receipt records separate executable hashes for installed review,
Glance routing and this later real-model run. The native conversation is
scrollable, and the driver scrolls to inspect the answer; this is not an
auto-scroll or phone-keyboard claim. First-use consent currently returns an
error to the original request, so the person resends after allowing the agent.
The Glance card's own chat thread and the full app conversation have not been
shown to share history.

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

6. Integrated offline restart exposed that loading the calendar list gated loading
   cached events. The app now loads its selected calendar cache immediately and
   fetches the list independently; both installed restart tests pass.
7. Full-shell restart hid foreground-published cards until agent consent existed.
   Restoration now accepts an ordinary installed app's existing Glance grant
   before first agent use, while retaining explicit denial, current-account,
   sign-out and capability checks. The legacy Mail consent rule remains intact.
8. A failed single-use host save kept a visible inert Approve button. The host
   now hides consumed approval and returns Back after failure; the final native
   test verifies that exact error state.

9. The first actual agent request used a native-module consent description,
   showing the app ID and device-file access. The contained-app gate now reads
   the admitted app name and storage contract. Its regression test verifies
   “Google Calendar,” no workspace files, account-scoped alternatives and
   unchanged denial behavior.

## Remaining acceptance

Not verified: real OAuth consent, Google read/create/edit, physical host approval,
expanded-card workspace, Glance-card chat and card/app shared conversation history,
Android keyboard and lifecycle, Linux or Windows execution. No numeric UX grade or production sign-off is
claimed while those core paths remain unverified. Recurrence expansion/editing,
attendee invitations and agent-driven event mutation are outside this sample's
implemented scope. Owned native test instances were quit after their runs.
