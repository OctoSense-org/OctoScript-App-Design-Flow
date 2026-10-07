# Inbox Assistant sample

English | [简体中文](README.zh-CN.md)

A normal App Hub app, `org.octosense.samples.inbox`, with an optional Gmail
connection and one saved reply shared by Email, Reply, Chat and native review.
It does not require the bundled `os.mail` app or borrow its identity.

The initial inbox is explicitly fictional. It exercises local editing without
an account and cannot send email. On a configured OctoSense host, **Connect
Google** opens the shared OAuth service; the app receives an account-bound
handle, never a password, authorization code, access token or refresh token.

## What is implemented

- Gmail Inbox, Important and Sent folder reads through `gmail.messages` and
  `gmail.message`; no direct app-side network or provider credential access.
- Plain-text replies to one recipient. The host stores the sender, original
  message/thread headers, monotonic revision, pending review and send receipt.
- Reply / Chat switching saves edits first. Chat opens this account’s real app
  peer through `octos.session.open` / `octos.turn.start`. Its admitted Inbox
  tools read and edit the same saved draft, then the UI reads the stored result.
  Version checks and local typing guards prevent silent stale overwrites.
- The declared `inbox.new_message` event routes new Gmail IDs to the consented
  app peer and its bundled triage skill. Initial connection sets a forward
  history baseline; it does not notify for the entire old mailbox. Processing
  requires a durable quiet decision or a host-verified published card. Failed
  processing retries the same stable ID. No event can authorize sending.
- **AI sort** checks the selected message for personal relevance. Healthcare,
  shipping, schedules, school/work and family activity are the default examples;
  ordinary newsletters and marketing should remain quiet. Relevant results can
  publish a Glance workspace and notification. **Pin** is a manual, quiet action.
- A published workspace loads the admitted `glance-workspace.splash` template,
  shares the app’s controller, retains its original connection/message, and
  reads full message contents through the host. The model supplies relevance
  and summary; the host supplies the admitted interactive UI and account binding.
- **Review & Send** asks the host to show the complete immutable message. Only
  physical activation of the native control may authorize sending. A script,
  model, `from_sheet` flag, instrument click or developer mode cannot approve it.
- Accepted submissions retire their Glance card. Gmail acceptance is recorded
  separately from recipient delivery. Unknown outcomes block automatic retries.

## Runtime requirements and limits

This sample targets the new shared OAuth/Gmail implementation in OctoSense's
`crates/oauth-service`. Its host operations are `auth.connect`, `auth.active`,
`auth.select`, `auth.disconnect`,
`gmail.messages`, `gmail.message`, `gmail.draft.open`, `gmail.draft.get`,
`gmail.draft.edit`, `gmail.draft.review`, `gmail.event.status` and
`gmail.event.decide` and the read-only `gmail.events.status` readiness check.
The `inbox.*` tools map to these host methods; none exposes
send approval. `mail.read` and `mail.send` in the
OAuth request are host aliases for the corresponding Google scopes.

The host administrator must supply a registered OAuth client; a person completes
Google consent in the host/browser. Gmail API access and OAuth consent/testing
restrictions are configured with Google. The standard standalone `card-host`
registers no provider/model services and correctly reports their absence.
Google's Android authorization adapter and physical send review must be present
in the actual installed shell before a phone can complete this journey.

The shell collector checks the active, consented account approximately every
five minutes while background execution is allowed. An unsuccessful turn or
missing durable decision is eligible for a later retry; Android can defer quiet
jobs. The host collector and peer/tool route are implemented in this change,
and the macOS acceptance run exercised that production route with real DeepSeek
inference and a compile-only synthetic Gmail provider. Live Google OAuth and
real Gmail delivery remain unverified. See the source-bound
[integrated evidence](evidence/integrated/README.md).
After connecting and allowing the app agent, keep the inbox list open until it
shows **New-mail baseline ready**. Local status refreshes every three seconds;
**Refresh** also checks immediately. Only then send a new test email. Older mail
remains readable but is deliberately not backfilled into notifications. The
readiness row records a completed baseline, not proof that agent consent is
currently enabled; check the host agent setting as well.

**Not complete:** cross-app calendar booking, chat-to-system-memory promotion,
pagination UI beyond the first 30 messages, attachments, Reply All, HTML replies,
retry/reconciliation UI, or verified Android/Windows/Linux behavior. **AI sort**
is a foreground model helper, distinct from the incoming-event peer workflow.
No model output can authorize a send in this sample.

## Development and validation

Run from the App Design Flow checkout; these commands were executed locally:

```sh
tools/octo doctor
python3 examples/connected-apps/inbox/build_bundle.py
tools/octo run examples/connected-apps/inbox/bundle --port 8194 --hidden --detach
python3 examples/connected-apps/inbox/verify_native.py --port 8194
```

The verifier uses the actual Makepad HTTP instrument on fictional data. It checks
startup, the second item's identity, multiline Unicode editing, saved Reply/Chat
state, unavailable auth/peer services, the fixture sending block and folder
empty/filter states. It captures real PNGs and records source/manifest hashes.
Run the runner again after closing it, then use `--restart-check` to compare the
exact saved text. End owned instances with `/gq` or `/quit`.

Core tests live in OctoSense’s `inbox.rs` and `inbox_events.rs`: injected/mixed-provenance rejection,
revision conflict, expired/cancelled/cross-app reviews, persist-before-transport,
replay protection, uncertain results, MIME/header validation, and a fake Gmail
request verifying the thread, exact body and single submission. Event tests cover
pagination, cursor expiry, durable decisions, replay, retry, account isolation
and bounded queue recovery. Fake transport
success does not establish live Gmail delivery.

See [evidence](evidence/README.md) for current executed checks and remaining
visual/runtime gaps. The standalone fixtures use no model. The separate installed full-shell run
uses real DeepSeek with synthetic Gmail; no live Google account, MiniMax run or
real email was used. The bundle is unsigned and unpublished; publisher
identity, support/privacy details and release approval remain human checkpoints.

## Privacy

The app receives readable email contents only after its host connection is
authorized. Enabling its background agent allows new-mail content to be read by
the account’s app peer and configured model for triage. Foreground Chat and AI
sort also use that model. Agent consent is separate from Google login; disable
the app agent to stop model triage. Ordinary manual reading and editing work
without a model. Host credentials remain outside app storage.

Fictional drafts and the opaque selected connection handle are stored in the
app's private jail. Real reply drafts and submission records are kept by the
host, keyed by app and connection. Signing out revokes further use of that
connection; it does not erase the historical host draft or send receipt. Glance
publication stores a compact account/message binding and a workspace program;
full real message contents are loaded through the authorized service. Do not
check private app data, OAuth configuration, real email captures or tokens into
this repository. All supplied screenshots/fixtures must remain fictional.

The [macOS soak report](evidence/soak/README.md) adds 33 native cycles over 610 seconds and cold restoration. It separates two remaining instrument frame-submission errors from passing draft/state checks and records the finite RSS trend.
