# Google Calendar sample brief

Build `org.octosense.samples.googlecalendar`, an independently installable
App Hub app. Use the shared OctoSense OAuth and Google Calendar host services;
never use `os.calendar`, collect credentials, or pretend a local event was
saved to Google.

## Journey

1. Connect Google through the host, see connected accounts, choose an account
   and one of its calendars. Explain service-unavailable and cancelled consent.
2. Read a retained agenda; refresh completes every provider page before replacing
   the cache. Show whether data came from the last successful sync. Failed refresh
   keeps the previous agenda. After a change of account or calendar, the screen
   names the active account and calendar.
3. Open an event. Summary, date, timezone, location and notes precede actions.
   Edit or create a timed or all-day event with one scrollable form and a
   compact footer. Date and time are separate fields; the host resolves the
   timezone and daylight saving time. An all-day end field means the last
   included day.
4. Retain unsaved input across navigation and process restart. Review the exact
   draft on the host sheet; save to Google only after approval. Keep the draft
   when review is cancelled or the network fails. An ETag conflict does not
   overwrite a newer remote event. Refresh verifies a confirmed write.
5. Publish the selected real event as an optional Glance card. The summary and
   full view retain event identity; an in-card **Open Calendar** action returns
   to this installed sample. Chat is optional and uses the declared app agent;
   unavailable AI must not prevent viewing or editing. Chat advice does not
   itself claim to change or save an event.

## Scope and states

Support ordinary timed and all-day events; show recurring records as series,
without pretending their original start is the next occurrence. Editing a
recurring series is disabled until an explicit series/occurrence workflow exists.
Leave out deletion, attendee invitations, hidden background polling and
billing.

Design these states:

- connection: disconnected, authorizing, calendar selection
- data: loading, empty, cached, sync failure
- editing: detail, editor, restored draft, invalid date or time, DST gap or
  repeated hour
- saving: review pending, review cancelled, ETag conflict
- optional services: unavailable assistant, unavailable Glance

Public native captures and tests use synthetic fixtures only. Real accounts and
credentials stay in private host storage.

## Capabilities and data

- `auth`: consent, list app-bound connections, disconnect.
- `gcalendar`: selected calendar read/sync/cache and host-reviewed writes.
- `storage`: local account/calendar selection and unsaved draft, not tokens.
- `glance`: only the explicit **Glance** action.
- `octos.session.open`, `octos.turn.start`: optional contextual advice.

No direct network host is needed: OAuth and Google API traffic belongs to the
host. Persist the selected opaque connection handle and calendar ID privately.
The host caches events, partitioned by app, connection and calendar.

## Acceptance

Use the [script-app flow](../../../flows/script-app/FLOW.md):

1. Run a hidden `card-host` that the test starts and stops.
2. Exercise the real unavailable-service states and the synthetic form and
   draft fixtures.
3. Inspect the native screenshots.
4. Test keyboard editing and restart.

These are local UI checks, not OAuth, Google or phone acceptance. A live
provider round trip, a Glance transition and agent execution need the
integrated shell and consent; record them separately. Do not fabricate
publisher identity or publish this copy; the published 0.1.0 comes from
[ymote/octosense-google-calendar](https://github.com/ymote/octosense-google-calendar).
