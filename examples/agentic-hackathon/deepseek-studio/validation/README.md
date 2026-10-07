# Generated-card validation

This is the operator's acceptance record for the final generated files, tested
on 3 October 2026 local time. [Provenance](provenance.json) records the model,
runtime revisions and source hashes. It supersedes intermediate model self-reviews.

| Layer | Executed checks | Evidence |
| --- | --- | --- |
| Model authoring on OnePlus 6 | Skill/reference reads; source writes and repairs; L0 render; native preview admission/open/inspect/input; image viewing | [Sanitized calls and tool receipts](model-tools.json), [operator brief](operator-briefs/BRIEF.md) |
| Independent L0 measurement | Both cards fit 350×160 logical pixels; zero errors and warnings | [Email report](glance/email-action/report.json), [Meeting report](glance/meeting-planner/report.json) |
| Independent desktop behavior | **33/33 assertions passed**, native input and persisted state, both process restarts | [Results and inputs](desktop-native.json), [reproducible driver](../verify_native.py) |
| Normal phone integration | Both installed via App Hub; separate agent consent; real DeepSeek replies; reviewed local actions; receipts after restart; source byte equality | [Phone record](phone.json), [Email peer](phone/email-agent.json), [Meeting peer](phone/meeting-agent.json) |
| Bundle gate | Both PASSED, only unsigned publisher warning in the source examples | [Email gate](email-action-gate.txt), [Meeting gate](meeting-planner-gate.txt), [review answers](REVIEW-ANSWERS.md) |

The retained authoring ledger includes 41 `studio_input`, 45 `studio_inspect`,
22 `view_image` and 4 `studio_render` calls. These are observed calls, not
assertions that every attempted operation passed. Earlier streaming failures
and initial bad dataset fields required retries; the record is not a complete
provider transcript. No reasoning trace or credential is included.

## Source identity

| App | `main.splash` SHA-256 |
| --- | --- |
| Email Action DS | `a462937ca76d59daad215a60aa477aeb8488dd370c0f66dc6f614988eb2d4b49` |
| Meeting Planner DS | `5f020068fbb8b56dba9e91e9f857a840f050a5838d6ef9e39b032ccba31c66c9` |

The generated workspace, repository bundle and phone-installed source match
byte for byte. Studio's storage-only manifests and normal host agent manifests
are different and retained separately. Signing happened only on private copies.
The private catalog advanced from sequence 2 to 4 and verified with four entries;
the two original references remained installed. Nothing was publicly published.

## What the tests establish

Desktop tests cover populated startup, blank input, edits invalidating review,
exact recipient/body storage, immutable receipts, duplicate prevention, selection
by message identity, targeted Undo, explicit agent-unavailable errors, busy slots,
a new conflict after review, all-busy fallback, reset and restart persistence.
The driver obtains current native widget bounds, scrolls to controls, injects
real input and checks saved state; it does not invoke action handlers directly.

Independent review caught Email Undo showing success while retaining the entry:
the generated `delete o[k]` was ineffective in this isolate. DeepSeek repaired
it by rebuilding the object without the key. A later native rerun verified
targeted deletion and preserved drafts. Calendar's one-booking invariant and
late-conflict refusal were also repaired by the model and retested.

Some failed operator runs were harness errors: selecting an incomplete text
label, sending empty text without deleting, or clicking stale geometry after
visibility changes. The final driver replaces text explicitly and waits for a
fresh rendered frame. Earlier local failure artifacts remain outside the bundle;
they were not relabeled as passes. The final report contains only the final run.

On the phone, Email's model draft was marked **AI-written**, reviewed and saved
unchanged to Maya's fictional outbox entry. Meeting's peer actually read
`calendar.json` and `state.json`, explained the busy candidates and recommended
14:00 UTC. There was no booking until the operator selected, reviewed and
confirmed it. The host was then force-stopped and both apps reopened through
App Hub: their receipts and state remained. Developer mode was used only for
system-agent authoring and removed before these normal-host tests.

## Real captures and visual limits

- Phone: [Email main](phone/email-main.png), [review](phone/email-review.png),
  [after restart](phone/email-restarted.png); [Meeting main](phone/meeting-main.png),
  [answer](phone/meeting-answer.png), [review](phone/meeting-review.png),
  [after restart](phone/meeting-restarted.png).
- L0: [phone Email](phone/email-glance.png), [phone Meeting](phone/meeting-glance.png),
  [desktop Email](glance/email-action/glance.png), [desktop Meeting](glance/meeting-planner/glance.png).
- The operator opened and inspected the native captures. Contrast and hierarchy
  are readable; the initial Meeting Review action fits. Empty Email status
  regions were removed by DeepSeek. This is a visual judgment, not an automated
  aesthetic score.
- Email's long draft lines scroll horizontally in its editor; the full review
  wraps. Calendar's free-form answer currently displays raw Markdown and can be
  verbose. These remain UX limitations, so this record makes no production-polish
  or A-grade claim. A follow-up model repair should constrain answer formatting
  and revalidate an actual long provider response.

Phone Stop/late-response races, real mail/calendar delivery, background peer
delegation, live glance publication, notifications, and other platforms were
not verified in this run. Standalone `card-host` checks do not prove provider
delivery. No public publisher approval is claimed; listing identity and privacy
links are placeholders for a contestant to replace before public submission.
