# Operator answers to the seven scan questions

Applies to [Email scan](email-action-scan.json) and [Meeting scan](meeting-planner-scan.json).
This is an operator assessment, not a fabricated human approval or external reviewer verdict.

1. **Claims:** Both implement the listed fake-data workflows. Email's `confirm`
   saves the reviewed `to`, `subject` and `body` in `outbox`; the screen says
   “Delivered to the local demo outbox (no email sent).” Meeting's `confirm`
   rechecks availability and saves a local booking; the screen says “No invitation
   was sent.” The optional AI and labeled offline paths match the descriptions.
2. **Platforms/category:** Productivity fits. The listings conservatively name
   macOS, validated with native Metal. The adjacent record additionally verifies
   Android on one OnePlus 6; it is not a broad Android compatibility claim.
3. **Capabilities/hosts:** `storage` supports fixtures, drafts and receipts;
   `octos.turn.start` supports visible Ask controls; `octos.turn.interrupt`
   supports Stop. The read-only app peer is scoped to its account workspace and
   may ask a question through `ask_user_question`. Neither app requests network
   hosts or a real mail/calendar service. The configured host provider still
   contacts its remote model endpoint; an empty app host list does not mean
   model inference is offline. No unused app capability was identified.
4. **Deception:** Both display Demo data and explicitly label local effects.
   No login, payment sheet or impersonated system prompt is drawn by these apps.
   The actual host draws separate installation and agent consent screens.
5. **Assistant instructions:** Source contains intentional `prompt_for`/`qprompt`
   instructions used for explicit app-agent requests, including treating fixture
   content as data and avoiding real sends/bookings. This is expected integration,
   not hidden prose in fake mail asking the reviewer to ignore checks. Model
   notes and this evidence directory are outside installable bundles.
6. **Abuse:** None found. Named people are fictional participants; email addresses
   use `example.invalid` and there is no abusive or targeted content.
7. **Route:** Suitable for a private hackathon reference with documented UX
   limitations. **Human review before public submission:** replace publisher,
   support and privacy placeholders; review platform claims and polish the raw
   Markdown answer/editor behavior. This does not block the authorized local
   rehearsal, and it is not a public-release approval.
