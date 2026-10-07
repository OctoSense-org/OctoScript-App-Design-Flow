# Google Calendar sample acceptance

This is a development record from before the 0.1.0 release. Each section
describes the code at the time of its run, not the current code. Versions
0.1.0 and 0.1.1 were later published from
[ymote/octosense-google-calendar](https://github.com/ymote/octosense-google-calendar);
the [README](README.md) gives the current status.

Scope: an ordinary App Hub app written in Splash, with an embedded L0 Glance
card. A later advisory-chat run used real DeepSeek v4 Flash with synthetic
Calendar data; Google Calendar stayed a local fixture.

Final native-tested `main.splash` SHA-256:
`7292894f1576d2283726eeafdb79742bd6fe6fb9a651cb1646462bbde4185ff0`.
The verifier wrote binary, runtime, manifest-contract and screenshot hashes to
a local receipt in `.local-state/`; it is not a provider account export. All
public captures contain synthetic data.

`storage.accounts` was enabled, so the app agent and the host's OAuth
connection selection used the same account. The native journeys were rerun after
this manifest correction; the receipt includes its final manifest contract
hash.

## Checks executed

`python3 examples/connected-apps/google-calendar/scripts/verify-native.py`,
run from the App Design Flow root, ran five native journeys through the Makepad
instrument on a hidden macOS `card-host` that it started and stopped. Final
result: **5 passed**.

| Journey | Observed result |
| --- | --- |
| Fresh startup | Complete empty agenda; actual missing OAuth service reported |
| Timed-event editor | Title, both dates/times, timezone, location and multiline notes typed natively; exact values written to local draft |
| Review without account | Visible actionable error; exact draft retained |
| Restart | Exact edited values and all-day choice restored; notes reachable by scrolling |
| Account and calendar navigation | Real unavailable-service callback displayed; return navigation works |

The verifier confirmed that each control it clicked had at least 40 logical
points of visible height; the authored action buttons were 44 points. Screens
were reviewed at a 412 × 860 logical-point app viewport (824 × 1784 capture
including the host caption). The editor kept the compact action row outside its
scroller. The native desktop check did not simulate a phone soft keyboard.

Public original captures, inspected after the final code changes:

- `bundle/screenshots/01-local-draft.png`: retained all-day draft after restart.
- `bundle/screenshots/02-notes.png`: multiline notes and reachable actions.
- `bundle/screenshots/03-host-required.png`: real missing OAuth host service.
- `bundle/screenshots/04-glance-template.png`: the embedded L0 card source with
  synthetic event data; this is not a shell route or agent-chat result.

`python3 examples/connected-apps/google-calendar/scripts/verify-glance.py`
extracted the embedded L0 card source without rewriting it, supplied explicit
fixture data and rendered it through the native instrument. Final result: **L0
lint and render passed**, 10 realized nodes; **Open Calendar**, the timezone
and the chat input were visible. The local receipt recorded the source, card
and capture hashes.

`cargo test --locked -p octosense-oauth-service calendar_cache --lib` in the
companion OctoSense checkout: **8 passed**. These fixture tests covered:

- atomic page commit
- failed-page preservation
- a full reset after HTTP 410
- removal of cancelled events
- identity separation
- rejection of page loops and incomplete results
- rejection of a DST gap and a repeated hour
- all-day inclusive editor dates
- timezone handling
- bounded Glance metadata

They don't call Google.

`tools/octo check examples/connected-apps/google-calendar/bundle`:

```text
org.octosense.samples.googlecalendar 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"auth", "gcalendar", "glance", "octos.session.open", "octos.turn.start", "storage"}, hosts {}, storage 1048576 bytes, agent read-only
```

The wrapper also reported the listing's publisher placeholders; admission is
not publication readiness. `hub scan` wrote `build/review.json`; the scanner
asked **eight** questions, answered in `build/REVIEW-ANSWERS.md`.

The companion OctoSense `connected-install` example also passed against all
three actual connected sample bundles. It used ephemeral publisher, working
and anchor keys to sign temporary copies, admitted a private signed catalog,
installed through `Store::install_staged`, reopened through `Store::may_run` and
checked the exact capabilities and account-scoped storage. Modified installed
source, cross-app staging, unsigned catalogs and an untrusted anchor were
refused. Input bundles stayed unchanged; temporary fixture removal was checked.
This proved the signed installation boundary, not public catalog acceptance or
live services.

## Signed installed app and provider-boundary acceptance

The additional installed-app journey used the real signed App Hub Store,
`prepare_launch`, contained app identity, the shared OAuth and Calendar
services, immutable host review, native widgets, the cache and restart. A
non-default `acceptance-fixtures` build substituted only the provider transport
and token vault inside a marked temporary profile. Its synthetic account is not Google
OAuth; its native instrument approvals are not physical-input acceptance.

From the companion OctoSense checkout:

```sh
cargo build --locked --release -p octosense-shell \
  --features mobile-apps,acceptance-fixtures \
  --example connected-app-host --example connected-inbox-e2e --example connected-install
```

From the App Design Flow root:

```sh
python3 examples/connected-apps/google-calendar/scripts/verify-installed.py \
  --host ../OctoSense/target/release/examples/connected-app-host
```

Final result: **8 cases passed**, rerun after the final host cancellation and
modal-input changes against App Hub
`5c7a13f92fa25d36ba1fe7fb99dc9fb1b235f8d3`. The replacement review,
conflict and offline screenshots were inspected. The local receipt bound the
source and actual executable hashes to the screenshots and the final synthetic
provider state. The verifier created its own ephemeral signed installation; it
never enabled unsigned developer mode or used real credentials.

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
also **passed**. It exercised the stateful synthetic provider through the
actual API and cache, including saved and reopened values, an ETag conflict
without retry, connection restart, stable card identity and cross-app cache
isolation.

## Shared Glance and installed app routing

```sh
python3 examples/connected-apps/google-calendar/scripts/verify-shell.py \
  --shell ../OctoSense/target/release/examples/connected-inbox-e2e \
  --installer ../OctoSense/target/release/examples/connected-install
```

Result: **6 cases passed** in a hidden macOS desktop shell. The signed
Calendar app published its actual L0 card. Selecting a different event and
clicking the card's in-body **Open Calendar** returned to the original event.
The app's **Chat** page showed that event and a reachable input. After the
shell was quit and restarted without opening the app, the card was restored
before any agent consent; **Open Calendar** launched the installed app and
selected the same event. The original publication time and expiry did not
change.

- [Restored card before the app opens](evidence/04-restored-glance-without-open-app.png)
- [Cold route opens the original event](evidence/05-cold-exact-event-route.png)
- [Portable source, executable and capture hashes](evidence/acceptance.json)

The desktop Glance panel opened automatically when a new card appeared. Its
custom-drawn controls were not included in `/snap`, so the driver used visually
reviewed coordinates at its checked 1400 × 898–900 logical viewport and
recorded original captures. Earlier driver runs exposed startup timing, window
rounding and panel-dismiss sequencing assumptions; these failures were kept
locally and are not reported as product failures. One later instrument capture
returned HTTP 404; its failure receipt was kept locally, and an unchanged rerun
passed (see [Real DeepSeek advisory chat](#real-deepseek-advisory-chat)).

The restored-publication regression
`foreground_cards_restore_before_agent_consent_without_bypassing_revocation`
passed in `octosense-shell`: explicit denial and a missing capability still
blocked restoration, while an ordinary foreground publication did not require
first agent use. Account and signed-out checks stayed part of the real restore
path.

## Real DeepSeek advisory chat

The full-shell verifier was rerun with `--model-profile <model-profile.json>`
and `--kernel <octos-binary>`, using the operator's existing DeepSeek
configuration in an isolated temporary home. The actual model was
**DeepSeek v4 Flash**. No profile, credential or real account data entered the
bundle or public evidence.

Result: **7 cases passed**, including the six shell journeys above. The final
first-use sheet named **Google Calendar** and described **No files: only what
its tools return**. After consent and an explicit resend, the app's advisory
conversation called `googlecalendar.event` through its ordinary contained peer
and the real host tool mapping. The audit recorded `risk: read`, `decision:
allowed`, `outcome: ok`. The tool returned the selected synthetic event, and
DeepSeek answered its title, 09:00 Pacific start and Fixture room location.
The synthetic provider recorded **zero POST, PATCH or DELETE calls**.

- [Corrected actual consent sheet](evidence/06-agent-consent.png)
- [Actual model answer in the Calendar app](evidence/07-real-advisory-model-answer.png)

The portable receipt records separate executable hashes for installed review,
Glance routing and this later real-model run. The native conversation was
scrollable, and the driver scrolled to inspect the answer; this is not an
auto-scroll or phone-keyboard claim. First-use consent returned an error to the
original request, so the person had to resend after allowing the agent.
The Glance card's own chat thread and the full app conversation have not been
shown to share history.

## Sustained macOS UX soak

```sh
python3 examples/connected-apps/google-calendar/scripts/soak.py \
  --host ../OctoSense/target/release/examples/connected-app-host
```

The signed installed app passed **36 cycles over 620.010 seconds** with the
synthetic Calendar provider. Each cycle opened `event00001`, visited its Chat
input without sending, edited title/location/twelve-line notes, scrolled,
reviewed the exact draft and cancelled with zero provider writes. Three cycles
then saved and read back the exact event; three forced stale-ETag saves returned
412 without overwriting the newer provider state. Four cold restarts preserved
the exact draft. Every conflict exposed **Back** and removed the consumed
approval.
No crashes or blocked controls occurred. The test's processes and temporary
profile were removed after the run.

The 1,743 instrument input requests had a **1.127 ms median, 2.228 ms p95 and
6.023 ms maximum** HTTP round trip through macOS `wait=1` applied-frame
submission. These are not FPS, display completion or physical-input latency.
The run overlapped an Android cross-compile with four jobs and the other app
soaks on an arm64 Mac; it was not an idle-machine benchmark.

RSS increased within each process: **301.4→333.7, 283.8→329.1,
299.3→333.0 and 284.3→310.3 MiB** across the four longer process lifetimes.
The final restart measured 322.5 MiB. The restarts ruled out a steady-state
or leak-free conclusion; uninterrupted memory profiling was still open. The
always-visible **Resume draft** action on a fresh agenda was a remaining polish
issue; when clicked, it explained that no draft existed.

The first driver attempt read the retained draft before the input's 300 ms
debounce had flushed. The fixed driver waited for the persisted values; the
failed receipt was kept locally. No product source was changed for this soak.
It did not extend Google, phone, real-model or full-shell Glance coverage.

- [Portable soak receipt, identities, timings and RSS samples](evidence/soak.json)
- [Exact review during sustained use](evidence/09-soak-exact-review.png)
- [Final conflict with reachable Back action](evidence/10-soak-conflict.png)
- [Final agenda after refresh](evidence/11-soak-final-agenda.png)

## Failures retained and repaired

1. The first editor layout wasted vertical space on an unrelated global service
   status; the final editor hid that row and placed dates and times side by
   side.
2. A restart check failed with `no getter for field kind on type nan` because
   object `+=` did not merge parsed JSON in this runtime. The fix used explicit
   key assignment.
3. Real typing exposed duplicate JSON keys when a string key updated an object
   initially created with identifier keys. The fix normalized draft and default
   state through JSON before dynamic writes. The exact saved-content and restart
   tests caught the issue and passed after the repair.
4. The initial notes input was tall but single-line. The fix declared
   `is_multiline: true`; the final test entered and verified a newline.
5. The initial L0 card source used arbitrary `sys.dataset` field names, which
   the runtime rejected. The fix mapped the published event fields onto the
   allowed vocabulary. Its separate native fixture also needed the real runtime
   L0 kit.
6. Integrated offline restart exposed that loading the calendar list gated
   loading cached events. The fix made the app load its selected calendar cache
   immediately and fetch the list independently; both installed restart tests
   passed.
7. Full-shell restart hid foreground-published cards until agent consent
   existed. Restoration was changed to accept an ordinary installed app's
   existing Glance grant before first agent use, while keeping the explicit
   denial, current-account, sign-out and capability checks. The legacy Mail
   consent rule stayed intact.
8. A failed single-use host save kept a visible inert **Approve** button. The
   host fix hid the consumed approval and returned **Back** after a failure; the
   final native test verified that exact error state.
9. The first actual agent request used a native-module consent description,
   showing the app ID and device-file access. The contained-app gate was changed
   to read the admitted app name and storage contract. Its regression test
   verified “Google Calendar,” no workspace files, account-scoped alternatives
   and unchanged denial behavior.

## Remaining acceptance

**Unverified:** real OAuth consent, Google read/create/edit, physical host approval,
expanded-card workspace, Glance-card chat and card/app shared conversation history,
Android keyboard and lifecycle, Linux or Windows execution. No numeric UX grade or production sign-off is
claimed while those core paths remain unverified. Recurrence expansion/editing,
attendee invitations and agent-driven event mutation are outside this sample's
implemented scope. Every native test instance was closed after its run.
