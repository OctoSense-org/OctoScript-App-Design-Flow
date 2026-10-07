# Inbox Assistant sample

English | [简体中文](README.zh-CN.md)

An ordinary App Hub app, `org.octosense.samples.inbox`, with an optional Gmail
connection and one saved reply shared by the Email, Reply and Chat tabs and the
host's send review. It does not require the bundled `os.mail` app or borrow its
identity.

The initial inbox is explicitly fictional. It exercises local editing without
an account and cannot send email. On a configured OctoSense host, **Connect
Google** opens the shared OAuth service; the app receives an account-bound
handle, never a password, authorization code, access token or refresh token.

Version 0.1.1 is published in App Hub from
[ymote/octosense-inbox-assistant](https://github.com/ymote/octosense-inbox-assistant).
Its `inbox.notify` tool accepts only the bundled Glance template, and its
`AGENT.md` and triage skill say so. This directory is the unsigned development
copy and has the same tool, `AGENT.md` and skill. Its `manifest.json` still
says version 0.1.0 and has no signature, and its `listing.json` has
placeholder publisher fields and its own subtitle, description and release
notes. The other files match the published 0.1.1. The
[reference app guide](../README.md) explains how the app is built and what to
change before you reuse it.

## What is implemented

- Gmail Inbox, Important and Sent folder reads through `gmail.messages` and
  `gmail.message`; no direct app-side network or provider credential access.
- Plain-text replies to one recipient. The host stores the sender, the original
  message and thread headers, a monotonic revision, the pending review and the
  send receipt.
- Switching between Reply and Chat saves edits first. Chat opens this account's
  app agent through `octos.session.open` and `octos.turn.start`. Its admitted
  Inbox tools read and edit the same saved draft, then the UI reads the stored
  result. Version checks and local typing guards prevent silent stale
  overwrites.
- The declared `inbox.new_message` event routes new Gmail IDs to the consented
  app agent and its bundled triage skill. The first connection sets a forward
  history baseline; it doesn't notify for the whole old mailbox. An event
  counts as processed only after the agent records a quiet decision or the host
  confirms a published card. Failed processing retries the same stable ID. No
  event can authorize sending.
- **AI sort** checks the selected message for personal relevance. Healthcare,
  shipping, schedules, school or work, and family activity are the default
  examples; ordinary newsletters and marketing stay quiet. Relevant results can
  publish a Glance card and a notification. **Pin** is a manual, quiet action.
- A published card loads the admitted `glance-workspace.splash` template,
  shares the app's controller, keeps its original connection and message, and
  reads full message contents through the host. The model supplies relevance
  and a summary; the host supplies the admitted interactive UI and the account
  binding.
- **Review & Send** asks the host to show the complete immutable message. Only
  a physical press on the native control can authorize sending. A script, a
  model, a `from_sheet` flag, an instrument click or developer mode can't
  approve it.
- Accepted submissions retire their Glance card. Gmail acceptance is recorded
  separately from recipient delivery. Unknown outcomes block automatic retries.

One tool declaration here is not safe to copy: `inbox.draft_edit` runs in the
background and can change a reply's `to` address. Version 0.1.0 had a second
one. Its `inbox.notify` also accepted `script`, `source` and `data`, so a
prompt-injected background turn could publish arbitrary Splash code on
desktop-v0.1.0-beta.2. In 0.1.1 and this copy, `inbox.notify` requires the
admitted `glance-workspace.splash` template, `initial.message`, `card_id`,
`title`, `summary` and `notify`, and its closed schema has no `script`,
`source` or `data`. OctoSense `main` also refuses `script` from any agent tool
(not in any release yet). See
[What to copy, what not to copy](../README.md#what-to-copy-what-not-to-copy).

## Runtime requirements and limits

This sample needs the shared OAuth and Gmail services of OctoSense
desktop-v0.1.0-beta.2 or later (`crates/oauth-service`). It uses these host
operations:

| Service | Operations |
| --- | --- |
| `auth` | `connect`, `active`, `disconnect` |
| `gmail` | `messages`, `message`, `draft.open`, `draft.get`, `draft.edit`, `draft.review`; `event.status` and `event.decide`, the agent's triage record for one message; `events.status`, the read-only check that the new-mail baseline is ready |

The `inbox.*` tools map to these host methods; none exposes send approval.
`mail.read` and `mail.send` in the OAuth request are host aliases for the
matching Google scopes.

Beta.2 has no built-in provider registration, so the host's administrator
supplies a registered OAuth client, as the
[host setup guide](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/crates/oauth-service/README.md)
describes; a host built with its distributor's registration needs none. A
person completes Google consent in the host and the browser. Gmail
API access and the OAuth consent and testing restrictions are configured with
Google. The standard standalone `card-host` registers no provider or model
services and correctly reports their absence. Google authorization on Android
is not implemented yet, so no phone can complete this journey.

The shell's mail collector checks the active, consented account every 5
minutes while background execution is allowed. An unsuccessful turn or a
missing durable decision can be retried later; Android can defer quiet jobs.
The collector and the agent's tool route are part of OctoSense
desktop-v0.1.0-beta.2. Before the 0.1.0 release, the macOS acceptance run
exercised that production route with real DeepSeek inference and a
compile-only synthetic Gmail provider. Live Google OAuth and real Gmail
delivery remain unverified. The
[integrated evidence](evidence/integrated/README.md) records the source hashes.

**Not yet:** cross-app calendar booking, chat-to-system-memory promotion,
pagination beyond the first 30 messages, attachments, Reply All, HTML replies,
and retry or reconciliation UI. **Unverified:** Android, Windows and Linux.

### Test new-mail notifications

1. Connect an account and allow the app agent.
2. Keep the inbox list open until it shows **New-mail baseline ready**. The
   status refreshes every 3 seconds; **Refresh** checks at once.
3. Send a new test email to the connected account. The collector checks every
   5 minutes; the agent then triages the message, and relevant mail publishes a
   Glance card. Older mail never triggers notifications.
4. If nothing arrives, check the host's agent setting. The readiness row
   records a completed baseline, not that agent consent is still on.

## Development and validation

From the App Design Flow root, run:

```sh
tools/octo doctor
python3 examples/connected-apps/inbox/build_bundle.py
tools/octo run examples/connected-apps/inbox/bundle --port 8194 --hidden --detach
python3 examples/connected-apps/inbox/verify_native.py --port 8194
```

The verifier prints a line that starts `PASS startup, second-message identity`.
It uses the actual Makepad HTTP instrument on fictional data and checks
startup, the second item's identity, multiline Unicode editing, the saved Reply
and Chat state, unavailable auth and agent services, the fixture's sending
block, and the folders' empty and filter states. It captures real PNGs and
records source and manifest hashes, overwriting the files in `evidence/`.

To check restart recovery:

1. Quit with `curl -s 127.0.0.1:8194/quit`.
2. Run the same `tools/octo run` command again.
3. Run
   `python3 examples/connected-apps/inbox/verify_native.py --port 8194 --restart-check`.
   It prints
   `PASS restart: exact multiline Unicode draft and message identity retained`.
4. Quit with the same `curl` command.

The core tests live in OctoSense's `crates/oauth-service/src/inbox.rs` and
`inbox_events.rs`:

- The review tests cover injected and mixed-provenance rejection, revision
  conflicts, expired, cancelled and cross-app reviews, persist-before-transport,
  replay protection, uncertain results, MIME and header validation, and a fake
  Gmail request that checks the thread, the exact body and a single submission.
- The event tests cover pagination, cursor expiry, durable decisions, replay,
  retry, account isolation and bounded queue recovery.

Success on the fake transport doesn't establish live Gmail delivery.

See [evidence](evidence/README.md) for the executed checks and the remaining
visual and runtime gaps. The standalone fixtures use no model. The separate
installed full-shell run used real DeepSeek with synthetic Gmail; it used no
live Google account or real email. The
[macOS soak report](evidence/soak/README.md) adds 33 native cycles over 610
seconds and cold restoration. It separates two remaining instrument
frame-submission errors from the passing draft and state checks, and records
the finite RSS trend.

All of this evidence predates the narrower `inbox.notify` of 0.1.1 and this
copy, and records the earlier bundle's hashes. The change has passed the gate,
`tools/test_connected_contracts.py` and App Hub's 0.1.1 admission, which
checked signed store install, upgrade from 0.1.0 and agent-file loading. It
has had no new native or model run.

## Privacy

The app receives readable email contents only after its host connection is
authorized. Enabling its background agent lets the account's app agent and the
configured model read new mail for triage. Foreground Chat and **AI sort** also
use that model. Agent consent is separate from Google sign-in; disable the app
agent to stop model triage. Ordinary manual reading and editing work without a
model. Host credentials stay outside app storage.

Fictional drafts and the opaque selected connection handle are stored in the
app's private storage. Real reply drafts and submission records are kept by the
host, keyed by app and connection. Signing out revokes further use of that
connection; it doesn't erase the historical host draft or send receipt. A Glance
publication stores a compact account and message binding and a workspace
program; the full message contents are loaded through the authorized service.
Don't commit private app data, OAuth configuration, real email captures or
tokens to this repository. All supplied screenshots and fixtures must stay
fictional.
