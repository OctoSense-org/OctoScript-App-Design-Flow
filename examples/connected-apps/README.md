# Connected App Hub samples

English | [简体中文](README.zh-CN.md)

Three ordinary App Hub apps demonstrate shared provider login and host services.
They use their own app identities and private storage, without requiring the
bundled Mail or Calendar interface. **No OctoSense cloud account is introduced.**
The person authorizes GitHub or Google; the host gives each app an opaque,
account-bound handle and keeps provider credentials outside its bundle.

These are development samples. Local UI and connector tests are recorded below;
they are not published apps or accepted live-provider demonstrations.

| Sample | Exact app ID | Implemented path and evidence |
| --- | --- | --- |
| [GitHub Notes](github-notes/README.md) | `org.octosense.samples.githubnotes` | Rinx-backed Markdown editor, repository/file selection and reviewed commits. [Native editor evidence](github-notes/VALIDATION.md). |
| [Inbox Assistant](inbox/README.md) | `org.octosense.samples.inbox` | Gmail reads, one editable reply shared with its app peer, native send review, important-mail event decisions and interactive Glance template. [Fixture receipts and limits](inbox/evidence/README.md). |
| [Google Calendar](google-calendar/README.md) | `org.octosense.samples.googlecalendar` | Calendar selection, paginated sync, event editing and reviewed saves, Glance publication/reopening. [Native UI and connector evidence](google-calendar/ACCEPTANCE.md). |

## Matching host and tooling

The samples require the companion OctoSense `feat/app-hub-connected-samples`
implementation with the `app-hub` feature, shared `auth`/provider services,
account isolation and host review surfaces. GitHub Notes additionally requires
its native `MarkdownEditor`, extracted from Rinx v1.1.0. The Inbox peer needs
admitted tool mappings, app-agent consent, a model configuration and the shell's
incoming-event collector. Glance templates and routes need the integrated shell.

Use the matching App Hub policy at commit
`eaaffffd695caf7ebf6205c455377c1f8567b906` or the compatible revision pinned by
OctoSense. Rebuild **both** `hub` and `card-host` after changing that policy; an
older binary rejects the new provider capabilities or `host_method` mappings.
An admission result says what the host may allow; it does not install those
services or verify a provider connection.

The standalone `card-host` runs the Inbox and Calendar local fixtures. It has no
real OAuth/model/provider services and no Rinx `MarkdownEditor`. GitHub Notes
requires the OctoSense editor fixture or integrated host, not an empty first
frame from standalone `card-host`. Each sample's README gives its actual runner
and verification commands. Follow the Design Flow's native workspace setup
before running `tools/octo doctor`.

## Provider setup and live acceptance

The host administrator supplies registered GitHub/Google OAuth clients in the
host's private `oauth/clients.json`. Client registration belongs to the host;
it is not an OctoSense account and must not be embedded in a submitted app.
The person reviews app/provider/scopes in the host sheet and completes consent
with the provider. GitHub device authorization must be enabled for its client.
Google desktop authorization uses the browser and PKCE loopback flow, with
provider API/consent/testing settings configured for the intended users.

**Google authorization on Android is currently unsupported in this shared
service until the native adapter is implemented.** The desktop loopback flow is
not a phone workaround. Windows and Linux credential adapters are implemented
in source but have not been executed on those platforms for these samples.

Use a clean development profile and the App Hub local/test-catalog workflow for
integration testing. A complete live test still needs provider sign-in, actual
read/write receipts, cancellation/revocation/conflicts and the exact installed
bundle. Inbox additionally needs agent consent and a completed forward-mail
baseline before sending a new test email. Its fictional inbox is never evidence
that real Gmail or an agent ran.

A deterministic `connected-install` check has installed all three actual
bundles through a fresh signed private catalog and signed bundles, reopened
the stored policy, and rejected tampering/another app’s staging. Source files
were unchanged and temporary data was removed. This validates the Store
installation boundary, not the installed UI or provider/model execution; see
the per-app evidence and the host’s local `target/connected-install/receipt.json`.
It was rebuilt and rerun against Hub
`eaaffffd695caf7ebf6205c455377c1f8567b906`; the
[portable signed-install receipt](evidence/signed-install-eaaffffd.json) records
all three bundle digests and the exact source, lockfile and binary hashes.

Not yet verified for these samples: live OAuth, real brokered peer/model
processing, integrated shell Glance expansion/routing, remote write effects,
or the OnePlus 6 keyboard/background lifecycle. Source implementation and local
fixture success must not be presented as those results. ADR 0010 in the
companion OctoSense repository tracks the architecture and remaining acceptance.

## Reproducible checks and data boundary

The work has executed `tools/octo doctor`, native Makepad input/capture journeys,
App Hub admission checks and deterministic connector tests. See the per-app
records above for exact source/binary/capture hashes, commands, failures and
which checks must be rerun after a change. Inbox also preserves machine-readable
[interaction](inbox/evidence/run-receipt.json) and
[restart](inbox/evidence/restart-receipt.json) receipts. These are scoped local
results, not a numeric UX or release score.

Codex authored these samples and drove the native fixtures. The examples do not
claim DeepSeek/MiniMax authorship or model validation. All supplied email,
calendar and repository contents are fictional. Never commit provider tokens,
client secrets, personal mailbox/calendar exports, private repository contents,
real-account screenshots, or `.local-state/`. App-agent consent controls model
processing separately from provider login. A model cannot approve protected
writes; the app must show the actual saved content in the host review surface.

Bundles remain unsigned and unpublished. Publisher/support/privacy placeholders
must be replaced by the actual publisher before release, and publishing requires
the normal Design Flow/App Hub checks. This directory is not a production
catalog or a claim that every platform can already install and run all three.
