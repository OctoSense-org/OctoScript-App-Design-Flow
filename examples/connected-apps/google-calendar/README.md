# Google Calendar sample

English | [简体中文](README.zh-CN.md)

An ordinary App Hub app (`org.octosense.samples.googlecalendar`) that uses
OctoSense's shared OAuth and Google Calendar services. It does not require the
built-in Mail or Calendar interface.

Version 0.1.1 is published in App Hub from
[ymote/octosense-google-calendar](https://github.com/ymote/octosense-google-calendar).
This directory is the unsigned development copy, and it still holds the 0.1.0
code. Its `main.splash` lacks 0.1.1's date-range status, `manifest.json` says
version 0.1.0 and lacks the signature, and `listing.json` has placeholder
publisher fields and its own subtitle, description and release notes. The
other files match the published 0.1.1. The [reference app guide](../README.md)
explains how the app is built and what to change before you reuse it.

The app has account and calendar selection, a synced agenda, event details,
timed and all-day editing, retained drafts and a host review before saving. Its
interface is in English. Optional chat discusses the selected event; it does
**not** edit events or claim to save suggested changes. The **Glance** action
publishes the event with an in-card **Open Calendar** action and its own
conversation. A later successful sync refreshes changed cards and withdraws the
cards of events no longer in the synced agenda.

The host cache, on every build:

- keeps the last complete result when a page fails;
- uses ETags for edits;
- partitions data by app, connection and calendar.

What a sync covers depends on the build:

- **desktop-v0.1.0-beta.2:** the whole calendar. The host advances Google's
  sync token only after the final page and starts a full sync after HTTP 410.
- **OctoSense `main` (not in any release yet):** a fixed window, from 30
  days before today to 366 days after on UTC day boundaries. Each refresh
  fetches the whole window again; the host keeps no sync token.

The editor uses dates, 24-hour times and an IANA timezone; the host rejects
missing or repeated local times at daylight-saving transitions. An all-day end
means the last included day. The app can't edit a recurring event. On
desktop-v0.1.0-beta.2, a recurring series appears once, labeled with its
original start. OctoSense `main` expands each series into its occurrences in
the window; the app still labels each one as a recurring series. The agenda
lists the oldest events first, so on beta.2 it opens on the start of the
calendar's history. Don't copy this sync strategy; see
[Whole-calendar sync](../README.md#whole-calendar-sync).

## Check the UI locally

From the App Design Flow root, run (verified on macOS):

```sh
tools/octo doctor
python3 examples/connected-apps/google-calendar/scripts/verify-native.py
python3 examples/connected-apps/google-calendar/scripts/verify-glance.py
tools/octo check examples/connected-apps/google-calendar/bundle
```

Each verifier prints a JSON receipt: `verify-native.py` reports `"passed": 5`,
and `verify-glance.py` reports `"result": "template and render pass"`.
`tools/octo check` ends `— PASSED` with the `unsigned` warning and a note about
the listing placeholders.

The native verifier starts its own hidden `card-host` on port 8164 and closes
it afterward; use `--port` to pick another free port. It types synthetic event
details, scrolls to the multiline notes field, checks the saved draft, exercises
the missing-account review state and restarts to check retention. Its private
working files and receipts are in `.local-state/`; no real Google account is
used. Standalone `card-host` correctly reports that the OAuth service is absent.

[ACCEPTANCE.md](ACCEPTANCE.md) records the exact scope and the original
failures. The separate Glance verifier renders the embedded L0 card source
with synthetic data on port 8165. It doesn't simulate shell routing or chat
replies. The bundle's four screenshots are native captures of these local
states, not Google API results.

## Run signed integration acceptance

Build the companion OctoSense fixture host, then run the verifiers from the App
Design Flow root:

```sh
# In ../OctoSense:
cargo build --locked --release -p octosense-shell \
  --features mobile-apps,acceptance-fixtures \
  --example connected-app-host --example connected-inbox-e2e --example connected-install
# From the App Design Flow root:
python3 examples/connected-apps/google-calendar/scripts/verify-installed.py \
  --host ../OctoSense/target/release/examples/connected-app-host
python3 examples/connected-apps/google-calendar/scripts/verify-shell.py \
  --shell ../OctoSense/target/release/examples/connected-inbox-e2e \
  --installer ../OctoSense/target/release/examples/connected-install
```

Before the 0.1.0 release, these runs passed. They installed the app from a
temporary signed catalog and used the real app and host services; only the
Calendar transport and vault were synthetic.

| Verifier | Result |
| --- | --- |
| `verify-installed.py` | 8 cases, rerun after the final host cancellation and modal-input changes (App Hub `5c7a13f9`): populated agenda, exact review and cancel, create and reopen, ETag edit and conflict, retained draft, offline cached restart |
| `verify-shell.py` | 6 cases with the actual Glance panel and installed launcher: warm and cold routes to the exact event, chat input for the same event, restoration without agent consent or a renewed expiry |
| `verify-shell.py --model-profile <model-profile.json> --kernel <octos-binary>` | Real DeepSeek v4 Flash: the Calendar agent called its declared `googlecalendar.event` read tool and answered about the selected synthetic event, with no provider writes |

The conflict state shows an error and **Back**; a consumed approval can't be
retried. These checks don't sign in to Google, send invitations or prove
physical-input approval. The corrected consent sheet and the actual answer are
in [ACCEPTANCE.md](ACCEPTANCE.md). Both verifiers clean up their own hidden
processes and temporary profiles, and save receipts bound to the source and
executable hashes under `.local-state/`.

For sustained native UX checks, run:

```sh
python3 examples/connected-apps/google-calendar/scripts/soak.py \
  --host ../OctoSense/target/release/examples/connected-app-host
```

The macOS run passed 36 cycles over 620 seconds: editing, scrolling, review and
cancel, three saved-event readbacks, three revision conflicts and four cold
restarts. Resident memory (RSS) grew within each process; this is a
functional pass, not a leak-free claim. [The acceptance record](ACCEPTANCE.md#sustained-macos-ux-soak)
contains original captures, timing limits and measured memory trends.

## Connect real Google Calendar

This path is implemented in source, but its **live validation is one manual
session**. OctoSense records it on macOS with a development build: the
installed 0.1.0 connected a dedicated test Google account, listed its
calendars and saved an event that remained after **Refresh**, with no
independent API readback ([receipt](https://github.com/OctoSense-org/OctoSense/blob/main/tools/connected-e2e/evidence/calendar-login-20261007.json)).
It requires OctoSense desktop-v0.1.0-beta.2 or later, which includes the shared
OAuth service and admits the `auth` and `gcalendar` capabilities. Beta.2 has no
built-in provider registration, so a host administrator configures a Google
OAuth client outside the bundle, as the
[host setup guide](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/crates/oauth-service/README.md)
describes; a host built with its distributor's registration needs none. You
complete provider consent on the host screen. **Not yet:**
Google sign-in on Android, which needs a native authorization adapter.

1. Install Google Calendar from App Hub. The published 0.1.1 is signed by
   `ymote`.
2. Select **Account → Connect Google**, complete the host and provider consent,
   then choose the account and calendar. **Refresh** reads the real Google API.
3. Choose an event and select **Edit**, or select **+ Event**. **Keep draft** keeps
   unsent changes. **Review & Save** opens the host's exact-content review.
4. Approve only after checking the account, calendar, title, time and notes. A
   provider receipt is followed by a refresh; errors keep the draft. A revision
   conflict never overwrites the event; edit the latest version instead.
5. To publish a card, select **Glance** in the event details. The card lasts
   24 hours and sends no notification. **Open Calendar** in the card uses the
   host's app-bound route to return to the same account, calendar and event.

## Service and privacy boundary

For capabilities, storage, tools and the agent, see
[Google Calendar](../README.md#google-calendar) in the reference app guide.

**Unverified:** beyond that one session, live Google sign-in, read, create,
edit, conflict and revocation; the expanded-card workspace; Glance-card chat
history; a physical save approval; Android; Linux; Windows. On
desktop-v0.1.0-beta.2, the host's Calendar review sheet doesn't check for a
physical press. OctoSense `main` requires one on its native review (not
in any release yet).
