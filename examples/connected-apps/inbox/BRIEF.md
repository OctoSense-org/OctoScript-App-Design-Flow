# Inbox Assistant

An ordinary App Hub app (`org.octosense.samples.inbox`) with no `os.*` identity.
It connects a Gmail account through the host OAuth service, reads Gmail labels
and messages, and keeps each reply as one revisioned host draft shared by the
editor, optional app-peer chat, and native exact-message review.

## Journey and screens

1. Open a clearly labelled fictional inbox immediately. Select a second item,
   read it, compose a reply, switch between Email and Chat, and restore edits
   after restart. Fictional data never sends email or claims an AI classification.
2. Connect Google using the host OAuth sheet. The app receives only its opaque
   connection handle. The inbox lists Gmail messages from a chosen label, with
   loading, empty, revoked, missing-provider and network failure states.
3. Open a message and compose a plain-text reply to one reviewed recipient.
   Save changes before switching to Chat or asking for host review. A model
   answer may update the same saved revision only if it has not changed while
   the model was running. Stale output leaves newer edits intact.
4. Optional AI sorting checks personal relevance (healthcare, shipping,
   appointments, school/work and family activities); marketing and generic
   newsletters should stay quiet. The user can read all messages regardless.
   Classification is advice, never authority to send or book an appointment.
5. Publish an important message as a Glance card under this app's identity.
   Expansion offers Email / Chat, retains the exact connection/message, and
   operates on the same host draft. Retire the card after confirmed provider
   acceptance, without deleting the draft or sending receipt.
6. Review opens the native host-owned view of the exact sender, recipient,
   subject and complete saved body. Only trusted physical input authorizes one
   submission. Cancellation, replay, account revocation, stale revisions and
   ambiguous network results never become automatic retries.

## Data and capabilities

- `storage`: fictional draft state and preferences in the app's private jail.
- `auth`: host-owned Google login, connected handles, revocation. No passwords,
  OAuth tokens, one-time codes, email addresses or personal fixtures ship.
- `gmail`: label/message reads and host-owned revisioned reply drafts/review.
- `model`: optional bounded foreground classification with host providers.
- `octos.session.open` / `octos.turn.start`: the account-bound Inbox peer, using
  admitted `inbox.*` host-method aliases and versioned draft tools.
- `glance`: publish and retire user-relevant cards from the app.

Native OAuth and sending integrations live in OctoSense. The standalone runner
has no host services and must clearly report their absence. Attachments,
Reply All, rich outbound HTML, transport retries and delegated calendar writes
are not implemented by this sample. An attachment notice prevents silently
suggesting that omitted attachment contents were read.

## Validation

Codex authors/drives/reviews a hidden Makepad instance with fictional fixtures.
Check populated startup, second-message identity, manual edit, Email/Chat state,
long content scrolling, narrow viewport, service failure, and restart retention.
Unit tests separately verify native send provenance and durable claim/receipt
behavior with a fake transport. These do not establish live sign-in, real AI,
Glance shell transitions, Android keyboard or actual Gmail delivery.

The shell collector and mapped Inbox tools form the incoming-event path. It
requires active OAuth account selection, app-agent consent and the declared
`inbox.new_message` trigger. A durable quiet decision or verified publication
acknowledges work; foreground refresh alone never does. Live provider/model
validation remains a separate gate.
