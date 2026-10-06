# Google Calendar App Hub sample

English | [简体中文](README.zh-CN.md)

An ordinary App Hub app (`org.octosense.samples.googlecalendar`) that uses
OctoSense's shared OAuth and Google Calendar services. It does not require the
built-in Mail or Calendar interface. This is a development sample, not an
accepted live-provider release.

The app has account/calendar selection, a synced agenda, event details,
timed/all-day editing, retained drafts and a host review before saving. Optional
chat discusses the selected event; it does **not** edit events or claim to save
suggested changes. The Glance action publishes the event with an in-card
**Open Calendar** action and its own conversation. A successful later sync
refreshes changed publications and withdraws removed events.

The host cache keeps the last complete result when a page fails. It advances the
Google sync token only after the final page, starts a full sync after HTTP 410,
uses ETags for edits and partitions data by app, connection and calendar. The
editor uses dates, 24-hour times and an IANA timezone; the host rejects missing
or repeated local times at daylight-saving transitions. An all-day end means
the last included day. Recurring series are labelled with their original start;
this version does not expand or edit individual occurrences/series.

## Run the checked local UI

From the App Design Flow root, these commands were run on macOS:

```sh
tools/octo doctor
python3 examples/connected-apps/google-calendar/scripts/verify-native.py
python3 examples/connected-apps/google-calendar/scripts/verify-glance.py
tools/octo check examples/connected-apps/google-calendar/bundle
```

The native verifier launches and closes its own hidden `card-host` on port 8164.
Use `--port` to select another unused port. It types synthetic event details,
scrolls to the multiline notes field, verifies the saved draft, exercises the
missing-account review state and restarts to verify retention. Its private
working files and receipts are in `.local-state/`; no real Google account is
used. Standalone `card-host` correctly reports that the OAuth service is absent.

[Acceptance evidence](ACCEPTANCE.md) records the exact scope and original
failures. The separate Glance verifier renders the exact embedded L0 template with explicit
synthetic data on port 8165. It does not simulate shell routing or chat replies.
The bundle's four screenshots are native captures of these local states, not
Google API results.

## Connect real Google Calendar

This path is implemented in source but **not live-validated for this sample**.
It requires an OctoSense build containing the shared OAuth service and the App
Hub `auth`/`gcalendar` capabilities. A host administrator configures a Google
OAuth client outside the bundle; the person completes provider consent on the
host screen. Android needs its native Google authorization adapter and cannot
reuse a desktop loopback login flow.

1. Install the unsigned development bundle through the host's developer path.
   A production publication still needs publisher identity, privacy details and
   signing. The repository does not publish or sign this sample automatically.
2. Select **Account → Connect Google**, complete host/provider consent, then
   choose the account and calendar. **Refresh** reads the real Google API.
3. Choose an event and **Edit**, or select **+ Event**. **Keep draft** retains
   unsent changes. **Review & Save** opens the host's exact-content review.
4. Approve only after checking the account/calendar, title, time and notes.
   A provider receipt is followed by a refresh; errors retain the draft.
   A revision conflict must be resolved against the latest event, not overwritten.
5. From event details, **Glance** publishes the event for 24 hours without a
   notification. **Open Calendar** uses the host's app-bound route handoff to
   return to that same account/calendar/event. Glance, real chat and this route
   still require integrated-shell validation.

## Service and privacy boundary

| Capability | App calls and purpose |
| --- | --- |
| `auth` | `accounts`, `active`, `select`, `connect`, `disconnect`; opaque app-bound connection handles |
| `gcalendar` | `calendars`, `cached`, `refresh`, `prepare`, `review_save`; Google events and exact host-reviewed writes |
| `storage` | Selected handle/calendar, unsent draft and published-event route bindings |
| `glance` | `publish`, `withdraw`, `take_open`; explicit cards and app-bound reopening |
| `octos.session.open`, `octos.turn.start` | Optional advice about the event the person selects |

Google scope aliases (`calendar.list`, `calendar.events`) are expanded by the
host. `storage.accounts: true` binds the app's peer to the selected OAuth account.
The bundle has no network capability or provider credentials. Its agent
has no workspace-file access (`agent_workspace: "none"`); event context is
provided only for a requested conversation. Four declared read tools
(`googlecalendar.calendars`, `.cached`, `.refresh`, `.event`) map explicitly to
the granted `gcalendar` service; they are private and not shareable. The host's own model configuration
and consent govern where that context is processed. Chat is advisory in this
version; no cross-app event-writing tool is declared or fabricated.

Remaining acceptance: live sign-in/read/create/edit/conflict/revocation,
provider-backed populated UI, host approval, Glance expansion/reopening/chat,
Android keyboard/lifecycle, Linux and Windows. Current source and local checks
must not be presented as those results. Publisher placeholders deliberately
remain in `listing.json` until the publisher supplies their real information.
