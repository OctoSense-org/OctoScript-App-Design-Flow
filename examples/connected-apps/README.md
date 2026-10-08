# Connected reference apps

English | [简体中文](README.zh-CN.md)

These three App Hub apps sign in to a provider, GitHub or Google, through the
OctoSense host. An app never sees a password or token. It receives an opaque
connection handle bound to one account, and the host makes every provider
call. No OctoSense account is involved.

All three are published, and App Hub's
[submission guide](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#the-three-reference-apps)
uses them as its worked examples. Study them to see how a connected app is
built, which of their patterns to copy, and which to avoid.

## The three apps

| App | App ID | Published source | Study it for |
| --- | --- | --- | --- |
| [GitHub Notes](github-notes/README.md) | `org.octosense.samples.githubnotes` | [ymote/octosense-github-notes](https://github.com/ymote/octosense-github-notes) | A GitHub commit that the host reviews before it runs |
| [Inbox Assistant](inbox/README.md) | `org.octosense.samples.inbox` | [ymote/octosense-inbox-assistant](https://github.com/ymote/octosense-inbox-assistant) | Gmail reads, a background app agent, a Glance template card, and a send that needs a physical press |
| [Google Calendar](google-calendar/README.md) | `org.octosense.samples.googlecalendar` | [ymote/octosense-google-calendar](https://github.com/ymote/octosense-google-calendar) | A cached calendar sync, reviewed event saves, a Glance card that reopens the app, and an advisory agent |

App Hub catalog sequence 10 lists each app twice, as 0.1.0 and 0.1.1, both
published by `ymote` with state `offered`. The store shows the newest, 0.1.1.
Each version was published from the matching tag of its repository (`v0.1.0`,
`v0.1.1`). Version 0.1.1 addresses three problems in 0.1.0 that this guide
teaches from ([Don't copy these patterns](#dont-copy-these-patterns)).

The directories here are unsigned development copies of the published 0.1.1.
Every file matches the release byte for byte except two:

- `listing.json`: the publisher name, support URL and privacy-policy URL are
  placeholders for you to replace. The rest of the listing matches the
  release.
- `manifest.json`: it has no signature, and its digest differs because the
  listing does. The published manifests also spell out the defaults that
  `hub sign-manifest` writes, such as `"network": {"hosts": []}` and
  `"tier": "standard"`. GitHub Notes' copy instead spells out the default
  `"background": false`, which its published manifest omits. Each copy
  declares the same version, capabilities, storage and agent as the release.

## Run the apps

### What you need

| Requirement | Why |
| --- | --- |
| [OctoSense desktop-v0.1.0-beta.2](https://github.com/OctoSense-org/OctoSense/releases/tag/desktop-v0.1.0-beta.2) on macOS (Apple silicon) | The first release whose App Hub contract (1.5) admits `auth`, `github`, `gmail` and `gcalendar`, and whose shell serves them. It also has the `MarkdownEditor` widget that GitHub Notes uses. |
| Provider registrations in the host's `<apps root>/.host/oauth/clients.json` | The host, not the app, owns the OAuth clients. Beta.2 reads them only from this file, and its downloads contain none. [OctoSense desktop 0.1.0-rc.1](../../README.md#compatible-shell-download) (RC1) and later builds can compile them in instead; the public RC1 packages include none. |
| A GitHub OAuth app with device flow enabled | GitHub Notes signs in with it. |
| A Google desktop OAuth client with the Gmail and Calendar APIs enabled, and its consent screen and test users configured | Inbox Assistant and Google Calendar sign in with it. |

The OctoSense [host setup guide](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/crates/oauth-service/README.md)
shows the `clients.json` format and how to register each provider.

Known limits:

- Earlier releases list the apps but never offer to install them:
  desktop-v0.1.0-beta.1 and home-v0.1.0-beta.1 refuse each one with
  `unknown capability "auth"`.
- Without `clients.json`, connecting an account fails with
  `OAuth is not configured. Add provider registrations in the host's oauth/clients.json`.
- **Not yet:** Google sign-in on Android. The host answers
  `Google authorization needs the Android host adapter; desktop login is not supported on this device`.
  No released phone build can install these apps.
- **Unverified:** most reads and writes against real GitHub and Google
  accounts. Every run recorded here used a synthetic provider; OctoSense
  records two live macOS checks, listed in
  [CAPABILITIES § Limits](../../docs/CAPABILITIES.md#limits).

### Install the published apps

1. Install OctoSense desktop-v0.1.0-beta.2 and add your provider registrations
   to `clients.json`.
2. In OctoSense, open App Hub, find the app, review the permissions it asks
   for, and install it. If the app is listed but can't be installed, your shell
   is older than beta.2; install beta.2.
3. Open the app and connect your account. The host shows its own consent sheet
   and opens the browser for the provider's step. The app receives only the
   connection handle. If connecting fails with `OAuth is not configured`, the
   host can't find your registrations; check the path and the provider entries
   in `clients.json`.

### Run the development copies

App Hub's `card-host` runs these bundles without any host service. Build it as
described in [QUICKSTART](../../docs/QUICKSTART.md), then start an app from the
repository root:

```sh
tools/octo run examples/connected-apps/inbox/bundle --port 8141 --hidden --detach
```

Each app behaves like this:

- Inbox Assistant opens its fictional inbox. Google Calendar opens an empty
  agenda where you can still write a local draft. Every connected call fails,
  and the app shows the error, for example
  `Google sign-in unavailable: no service answers "auth" on this device`.
- GitHub Notes doesn't render its editor. `card-host` has no `MarkdownEditor`,
  and the log shows `widget 'editor' not found in tree`.

For which shell serves which service, see [HOST-SERVICES](../../docs/HOST-SERVICES.md).
Each app's README lists its local checks and its signed-install acceptance run,
which uses OctoSense's test hosts with a synthetic provider.

## How each app is built

| | GitHub Notes | Inbox Assistant | Google Calendar |
| --- | --- | --- | --- |
| Capabilities | `storage`, `auth`, `github` | `storage`, `auth`, `gmail`, `model`, `glance`, `octos.session.open`, `octos.turn.start` | `storage`, `auth`, `gcalendar`, `glance`, `octos.session.open`, `octos.turn.start` |
| Storage | Per account, 4 MiB | Per account, 16 MiB (default) | Per account, 1 MiB, agent reads no files |
| `agent` block | Foreground, read-only (none in 0.1.0) | Background, started by `inbox.new_message`, one skill | Foreground only, advisory |
| `tools.json` | 3 read tools | 9 tools: 4 read, 5 act | 4 read tools |
| Glance | None | Template file `glance-workspace.splash` | [L0](../../docs/GLOSSARY.md) card source inside `main.splash` |
| Protected write | GitHub commit through `github.review_save` | Gmail send through `gmail.draft.review` | Event save through `gcalendar.review_save` |
| Host review checks for a physical press, desktop-v0.1.0-beta.2 | No | Yes | No |
| Host review checks for a physical press, RC1 on macOS | Yes | Yes | Yes |

All three follow the same rules:

- **Connect with scope aliases.** The app calls `auth.connect` with a provider
  and short scope names, and keeps only the handle that comes back.
- **Keep data per account.** `storage.accounts: true` gives each connected
  account its own data folder and its own agent.
- **Map tools to reviewed host methods.** Every tool is
  `implemented_by: "host-service"` with a `host_method` from App Hub's reviewed
  list, `private_data: true` and `shareable: false`. The list and its risk
  floors are in App Hub's [PUBLISHING](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#map-a-tool-to-a-shared-service-host_method).
- **Leave protected writes out of reach.** `github.review_save`,
  `gcalendar.review_save` and `gmail.draft.review` are not on that list, and a
  `host_method` can't name a host sheet. No agent tool can commit, save an
  event or send mail.

### GitHub Notes

A Markdown editor that commits a note to a GitHub repository.

| Capability | Calls | Used for |
| --- | --- | --- |
| `auth` | `auth.connect`, `auth.accounts`, `auth.active`, `auth.select`, `auth.disconnect` | GitHub consent, account choice, sign-out |
| `github` | `github.repositories`, `github.files`, `github.read`, `github.review_save` | Browsing, loading a note with its blob SHA, committing after review |
| `storage` | `fs.read`/`fs.write` of `recovery.json` | The unsent draft and one recovery copy |

The person picks public or private access before connecting. Public access
requests `read:user` and `public_repo`; private access requests `read:user`
and `repo`.

**Storage.** From `bundle/manifest.json`:

```json
"storage": {
  "accounts": true,
  "max_bytes": 4194304
}
```

**Agent.** Version 0.1.0 shipped `tools.json` without an `agent` block, so
the shell gave the app an agent anyway; see
[Tools without an agent block](#tools-without-an-agent-block). Version 0.1.1
and this copy declare that agent. From `bundle/manifest.json`:

```json
"agent": {
  "background": false,
  "instructions": "AGENT.md",
  "model": {
    "local_only": false,
    "needs": [
      "tool_calling"
    ]
  },
  "profile": "read-only",
  "tools": []
}
```

The agent runs only when the person asks, through **Ask GitHub Notes**, and
only after the person allows it; installing the app or connecting GitHub
never starts it. `AGENT.md` treats repository content as untrusted, keeps the agent to
the three read tools, and sends the person to the editor and the host review
for any save.

**Tools.** Three read tools map to the GitHub service. From `bundle/tools.json`,
without its input schema:

```json
{
  "name": "githubnotes.read",
  "description": "Read a UTF-8 note from the selected repository branch, including its current blob SHA.",
  "risk": "read",
  "background": false,
  "shareable": false,
  "private_data": true,
  "implemented_by": "host-service",
  "host_method": "github.read"
}
```

`githubnotes.repositories` and `githubnotes.files` map to
`github.repositories` and `github.files` the same way.

**Glance.** None.

**Protected write.** The paper-plane button freezes the draft and asks the host
to review it:

```text
host.request("github.review_save", {connection: frozen.connection, file: {owner: frozen.owner, repo: frozen.repo, branch: frozen.branch, path: frozen.path, sha: frozen.sha, content: frozen.content, message: frozen.message}}, fn(r){ … })
```

The host opens its own sheet with the exact repository, branch, path, commit
message and content. GitHub receives the commit only after the person presses
**Approve & Save** in that sheet. The app reports success only when the reply
carries a `commit_sha`. The blob `sha` makes a stale save fail with a conflict
instead of overwriting a newer file.

The host raises the sheet only over an app in the foreground; a background tile
or an agent's tool call gets `Open the app to review this change`. The review
expires after 10 minutes. How the host accepts approval depends on the build:

- **desktop-v0.1.0-beta.2:** only from its own sheet, but it doesn't check
  that the press was physical.
- **RC1 on macOS:** only from a physical press on the native
  **Approve & Save** control, the same kind of review that guards a Gmail
  send. Like that review, it checks Makepad's `trusted_user_input()` on both
  the press and the click, and an approval works once. A script or agent
  request gets
  `Saving requires a physical activation of the native host review. Script and agent requests cannot approve it.`
  On Windows and Linux, RC1 refuses the save: protected writes fail closed.

### Inbox Assistant

A Gmail client with one saved reply per message and an app agent that triages
new mail.

| Capability | Calls | Used for |
| --- | --- | --- |
| `auth` | `auth.connect`, `auth.active`, `auth.disconnect` | Google consent with `openid`, `email`, `profile`, `mail.read`, `mail.send` |
| `gmail` | `gmail.messages`, `gmail.message`, `gmail.draft.open`, `gmail.draft.get`, `gmail.draft.edit`, `gmail.draft.review`, `gmail.events.status` | Reading mail, keeping one reply draft on the host, requesting the send review, showing new-mail monitoring status |
| `model` | `model.complete` | The foreground **AI sort** button |
| `octos.session.open`, `octos.turn.start` | `octos.session.open`, `octos.turn.start` | Opening the agent's session and sending a turn from the Chat tab |
| `glance` | `glance.publish`, `glance.withdraw` | Publishing a message card and withdrawing it after the send |
| `storage` | `fs.read`/`fs.write` of `inbox-local.json` | Fictional drafts and the selected handle |

The app's source is `src/workspace.splash`. `build_bundle.py` generates
`bundle/main.splash` and the Glance template from it, so edit the source and
rerun the script.

**Storage.** `"storage": {"accounts": true}` sets no `max_bytes`, so the gate
(`hub check`) grants the default 16 MiB. Real reply drafts and send receipts
live with the host, keyed by app and connection. The app's own folder holds
only the fictional drafts and the handle.

**Agent.** From `bundle/manifest.json`:

```json
"agent": {
  "background": true,
  "instructions": "AGENT.md",
  "model": {
    "needs": [
      "tool_calling"
    ]
  },
  "profile": "read-only",
  "skills": [
    "incoming-mail-triage"
  ],
  "tools": [
    "ask_user_question"
  ],
  "triggers": {
    "events": [
      "inbox.new_message"
    ]
  }
}
```

- `background` and `triggers` let the host start a turn when new mail arrives.
  The event name is the app's namespace (the last segment of its ID, `inbox`)
  plus `.new_message`.
- The shell loads `AGENT.md` and the skill's `SKILL.md` as guidance for each
  turn. Both treat email text as untrusted data.
- `profile: "read-only"` is the file profile of OctoSense's agent kernel: every
  file write asks the person first. It doesn't stop tools with risk `act`.
- `ask_user_question` is the one kernel tool an app agent may keep.

**Tools.** All nine run on host services with `background: true`,
`private_data: true` and `shareable: false`. None can send.

| Tool | `host_method` | Risk |
| --- | --- | --- |
| `inbox.messages` | `gmail.messages` | `read` |
| `inbox.message` | `gmail.message` | `read` |
| `inbox.draft_open` | `gmail.draft.open` | `act` |
| `inbox.draft_get` | `gmail.draft.get` | `read` |
| `inbox.draft_edit` | `gmail.draft.edit` | `act` |
| `inbox.event_status` | `gmail.event.status` | `read` |
| `inbox.event_decide` | `gmail.event.decide` | `act` |
| `inbox.notify` | `glance.publish` | `act` |
| `inbox.withdraw` | `glance.withdraw` | `act` |

`inbox.event_status` and `inbox.event_decide` read and record the agent's
triage decision for one incoming message. The app's own `gmail.events.status`
call is different: it only reports whether the new-mail baseline is ready.

**Glance.** The card is a bundle file, `glance-workspace.splash`, built from
the same source as the app. To publish it, the app names the template and
passes initial values. From `bundle/main.splash`:

```text
if demo {args["script"]="let initial = "+{connection:connection demo:demo message:card_message}.to_json()+"\nlet card_source = \"\"\n"+card_source}
else {args["template"]="glance-workspace.splash" args["initial"]={message:card_message}}
```

For a real account, the host reads the template from the installed,
digest-checked bundle and binds the card to the app's active account. It
refuses `source`, `script` or `data` next to a template. The card runs under
the app's own policy, so its Reply and Chat tabs work on the same host draft.
Only the fictional demo publishes a `script` card.

**Protected write.** **Review & Send** calls `gmail.draft.review` with the
draft and its revision. The host shows the complete saved message in a native
review and sends only after a physical press on its approve button. It checks
Makepad's `trusted_user_input()` on both the press and the click. macOS pointer
input and Android touch qualify. On other platforms, and for remote-control or
synthetic input, the send fails closed. An app or agent that tries to approve
gets
`Apps and agents cannot approve sending. Request draft.review and physically activate the native host control.`

### Google Calendar

A calendar client with a cached agenda, reviewed edits, event cards in Glance
and an advisory agent.

| Capability | Calls | Used for |
| --- | --- | --- |
| `auth` | `auth.connect`, `auth.accounts`, `auth.active`, `auth.select`, `auth.disconnect` | Google consent with `openid`, `email`, `calendar.list`, `calendar.events` |
| `gcalendar` | `gcalendar.calendars`, `gcalendar.cached`, `gcalendar.refresh`, `gcalendar.prepare`, `gcalendar.review_save` | Calendar list, cached agenda, sync, date and timezone checks, reviewed saves |
| `glance` | `glance.publish`, `glance.withdraw`, `glance.take_open` | Publishing an event card, withdrawing it, reopening the event from the card |
| `octos.session.open`, `octos.turn.start` | `octos.session.open`, `octos.turn.start` | Opening the agent's session to chat about the selected event |
| `storage` | `fs` calls on `draft.json`, `selection.json`, `publications.json` | The unsent draft, the chosen account and calendar, published cards |

**Storage.** From `bundle/manifest.json`:

```json
"storage": {
  "accounts": true,
  "agent_workspace": "none",
  "max_bytes": 1048576
}
```

`agent_workspace: "none"` gives the agent no files; it sees only what its tools
return. The host caches events outside the app's folder, one cache per app,
connection and calendar.

**Agent.** From `bundle/manifest.json`:

```json
"agent": {
  "instructions": "AGENT.md",
  "model": {
    "needs": [
      "tool_calling"
    ]
  },
  "profile": "read-only",
  "tools": []
}
```

There is no `background` flag and no trigger, so the agent runs only when the
person asks. `AGENT.md` treats event text as untrusted and sends the person to
**Edit** and the host review to change anything.

**Tools.** Four read tools with `background: false`:
`googlecalendar.calendars`, `googlecalendar.cached` and
`googlecalendar.refresh` map to the `gcalendar` methods of the same name, and
`googlecalendar.event` maps to `gcalendar.get`.

**Glance.** The card is an L0 source string in `bundle/main.splash`
(`let glance_source = …`). For each event, the app gives the card its own chat
thread and publishes it with data and a route back into the app:

```text
host.request("glance.publish", {card_id: event.card_id title: event.card_title summary: event.card_summary source: card data: {ev: {…}} open: {app: "org.octosense.samples.googlecalendar" route: route} expires: 86400 notify: false}, fn(r){ … })
```

**Open Calendar** in the card launches the app. The app collects the route with
`glance.take_open` and opens the same account, calendar and event. After each
sync, it republishes cards whose event changed and withdraws cards whose event
is no longer in the synced agenda.

**Protected write.** A save takes two host calls. `gcalendar.prepare` checks
the dates, times and IANA timezone. It refuses a local time that a daylight
saving change skips or repeats. `gcalendar.review_save` then opens the host
sheet with the exact event. An edit carries the event's ETag, so if the event
changed remotely, the save fails with HTTP 412 instead of overwriting it.
Approval works as it does for GitHub Notes: desktop-v0.1.0-beta.2's sheet
doesn't check for a physical press, and RC1 requires one.

## What to copy, what not to copy

### Copy these patterns

Besides the four rules all three apps share:

- Send every provider write through the host review, and report success only
  from the provider's receipt: a commit SHA, a refreshed event, a Gmail status.
- Give each tool the lowest risk that fits.
- Set `agent_workspace: "none"` when the agent needs only its tools.
- Tell the agent in `AGENT.md` that provider content is data, not
  instructions.
- Publish Glance cards from a bundled template that the host binds to the
  account.
- List only the platforms you tested. All three set `"platforms": ["macos"]`
  in `listing.json`.

### Don't copy these patterns

These four patterns passed App Hub review, but each carries a risk or a
surprise. Version 0.1.1 fixes the first two and shows the date range for the
third; the fourth is still in Inbox Assistant. The host's side depends on the
build, so the first three lessons cover both desktop-v0.1.0-beta.2 and
RC1.

#### Glance tools that accept `script`

In Inbox Assistant 0.1.0, the `inbox.notify` tool, which maps to
`glance.publish` and runs in the background, accepted a whole Splash program
next to `template` and `source`. From its `bundle/tools.json`:

```json
"script": {
  "type": "string",
  "maxLength": 16384
},
```

A `script` card is a Splash program that runs in the Glance panel under the
app's policy and grants. The agent's background turns start from incoming
email, so text in one email could steer a turn into publishing a program of the
sender's choosing.

- **What 0.1.1 changes:** `inbox.notify` drops `script`, `source` and
  `data`, and requires `template`, `initial`, `card_id`, `title`, `summary`
  and `notify`. Its description says
  `Executable card source is not accepted.` This repository's copy matches.
- **RC1:** the host refuses `script` from any agent tool that maps
  to `glance.publish`:
  `Agents cannot publish executable Splash; choose an admitted template with initial data, or L0 source`.
  A template card needs a template name and an `initial` object, and an
  agent's `source` must be valid L0. An app's own script can still publish a
  `script` card.
- **desktop-v0.1.0-beta.2:** the host has no such check, so an agent tool that
  accepts `script`, as 0.1.0's did, can still publish one.

**Do this instead:** give a card-publishing tool only `template` and
`initial`, or an L0 `source` with `data`. Never accept `script`. Restrict
`template` to your bundled file and give `initial` a strict schema:

```json
"template": {
  "type": "string",
  "enum": [
    "glance-workspace.splash"
  ]
},
```

Version 0.1.1 and this repository's copy do this, and set
`additionalProperties: false`.

#### Tools without an agent block

GitHub Notes 0.1.0 declared no `agent` block but shipped a `tools.json`.
`hub check` reports `agent none`. App Hub still admits the tools as an agent
bundle, and OctoSense treats any app that ships admitted tools as an agent app:
the shell offered **Ask GitHub Notes**, while the store said
`Runs no assistant.` The privacy policy was amended after the 0.1.0 tag to
disclose that agent.

- **What 0.1.1 changes:** the manifest declares the foreground,
  read-only agent and its `AGENT.md`, and the listing description discloses
  **Ask GitHub Notes**. The three read tools are unchanged.
- **RC1 and desktop-v0.1.0-beta.2:** both still give a
  `tools.json` app an agent, but their stores describe it differently:

| Store text | desktop-v0.1.0-beta.2 | RC1 |
| --- | --- | --- |
| Privacy summary, 0.1.0 | `Runs no assistant.` | `Offers the host's Ask assistant for its admitted tools, only after you consent. Your conversation and tool results may be sent to your configured AI provider.` and `No app-declared background assistant or automatic triggers.` |
| Privacy summary, 0.1.1 | `Runs an assistant limited to this app's own data.` | The same |
| Permission lines, 0.1.1 | `Run an assistant for this app (no tools), inside this app's own data only` | `Run an assistant for this app, only after you allow it` and `Its assistant can use these app tools: githubnotes.repositories, githubnotes.files, githubnotes.read` |

The store lists only the newest version, so a person now sees the 0.1.1 lines.
The beta.2 store prints `(no tools)` because it counts only the tools in
`agent.tools`, which is empty; the agent can still call the three read tools.

**Do this instead:** if you ship tools, declare the `agent` block and describe
the agent in your listing and privacy policy. If you want no agent, don't ship
`tools.json`.

#### Whole-calendar sync

Google Calendar refreshes through `gcalendar.refresh`. On
desktop-v0.1.0-beta.2, that syncs the entire calendar: the host asks Google for
every event, with no start date, and sorts the snapshot oldest first. The app
shows the first 100 events, so a calendar with years of history opens on its
oldest entries. Large calendars fail when they reach the host's limits: 100
pages, 25,000 events, a 16 MiB cache or 35 seconds per refresh. The
`googlecalendar.cached` and `googlecalendar.refresh` tools hand that whole
snapshot to the model. Version 0.1.0 didn't tell the person which dates the
agenda covered.

- **What 0.1.1 changes:** the status line shows
  `past 30 days / next 366 days` when the host reports its sync window, and
  `date range unavailable` when it doesn't. When the selected event drops out
  of a sync, the app says it may be outside the displayed date range, not that
  it left the calendar. This repository's copy has the same change.
- **RC1:** the host syncs a fixed window, from 30 days before
  today to 366 days after on UTC day boundaries, with recurring events expanded
  into single occurrences. The same limits apply.
- **desktop-v0.1.0-beta.2:** the host still syncs the whole calendar, oldest
  first, and reports no window, so 0.1.1 shows `date range unavailable`.

**Do this instead:** window what you show and what the agent reads. Start the
agenda at today by filtering on each event's start, page forward from there,
and give the agent single-event tools such as `googlecalendar.event` rather
than whole-calendar reads.

#### Background tools that rewrite drafts

Inbox Assistant's `inbox.draft_edit` has `background: true` and takes `to`,
`subject` and `body`. A turn started by an incoming email can rewrite any open reply,
recipient included. Only the physical send review stands between that edit and
a send.

**Do this instead:** keep background tools to reads and to writes the person
reviews. Mark draft-editing tools `background: false`. OctoSense's agent kernel
then refuses them unless the person is in the app:
`may only run while the person is in the app (the app did not mark it background)`.

## Start your own app from one

Don't submit a copy unchanged. The gate compares the ID and version with the
catalog, and these IDs belong to `ymote`. An unchanged copy of GitHub Notes,
checked with the `hub` you built in [QUICKSTART](../../docs/QUICKSTART.md):

```console
$ hub check bundle --allow-unsigned --catalog <App Hub checkout>/catalog.json
org.octosense.samples.githubnotes 0.1.1 — REFUSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  [refused] version: version 0.1.1 of org.octosense.samples.githubnotes is already published; publish a new version
  [refused] continuity: org.octosense.samples.githubnotes is already published by "ymote"; an update must carry that key
  grants: capabilities {"auth", "github", "storage"}, hosts {}, storage 4194304 bytes, agent read-only
hub: the bundle was refused
```

A new version number doesn't help: `continuity` still demands `ymote`'s key.
Give the copy its own ID.

1. From this repository's root, copy the app's `bundle/` into your new app's
   directory. For Inbox Assistant, copy `src/` and `build_bundle.py` too.

   ```sh
   mkdir -p ~/apps/my-notes
   cp -R examples/connected-apps/github-notes/bundle ~/apps/my-notes/bundle
   cd ~/apps/my-notes
   ```

2. Set a new `id` in `bundle/manifest.json`, for example `com.example.mynotes`.
   Its last segment becomes the
   namespace of your tools and events, and it can't be a reserved name such as
   `notes` or `weather`. App Hub's [PUBLISHING](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#ids-and-reserved-names)
   lists the reserved names.
3. Rename the old namespace everywhere it appears:

   | App | Files that name the namespace or the ID |
   | --- | --- |
   | GitHub Notes | `tools.json`, `AGENT.md` |
   | Inbox Assistant | `tools.json`, `AGENT.md`, `skills/incoming-mail-triage/manifest.json`, `skills/incoming-mail-triage/SKILL.md`, the chat prompt in `src/workspace.splash`, and the `inbox.new_message` trigger, which `build_bundle.py` writes into `manifest.json` |
   | Google Calendar | `tools.json`, `AGENT.md`, and `main.splash`: the `sys.chat(app: …)` line in `glance_source`, the `app://` link and `open.app` in the publish call |

4. Replace the placeholders in `listing.json`, the icon and the screenshots.
   Capture new screenshots of your app as described in
   [QUICKSTART](../../docs/QUICKSTART.md).
5. Update the bundle digest with `hub stamp`, then check the bundle against the
   catalog:

   ```sh
   hub stamp bundle
   hub check bundle --allow-unsigned --catalog <App Hub checkout>/catalog.json
   ```

   `hub stamp` writes the bundle's 64-character BLAKE3 digest into
   `integrity.bundle_blake3` and prints it. The check passes with only the
   unsigned warning:

   ```text
   com.example.mynotes 0.1.1 — PASSED
     [warning] publisher-signature: unsigned: accountability rests on the hub alone
     grants: capabilities {"auth", "github", "storage"}, hosts {}, storage 4194304 bytes, agent read-only
   ```

   If it fails:

   | Refusal | Fix |
   | --- | --- |
   | `tools: tool "githubnotes.repositories" is outside the app's namespace "mynotes"` | Rename the tools to the new namespace (step 3). |
   | `identity: app id "com.example.notes" ends in "notes", which is reserved` | Choose another last segment (step 2). |
   | `version` or `continuity` | Set an ID that isn't published yet (step 2). |

## How the reference apps were submitted

Each published repository is a complete submission you can copy. It holds
`bundle/`, which is all the gate reads, plus `publisher.json` with the public
key, `PRIVACY.md` and `review/`. The support URL is the repository's issue
tracker; GitHub Notes also ships `SUPPORT.md`. In `review/`, `GATE.json` is the
`hub check` report on the signed bundle and `ANSWERS.md` answers the `hub scan`
questions.
Each version has its own tag (`v0.1.0`, `v0.1.1`) and GitHub release, which
freeze its bytes.

Follow the [submission guide](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#the-three-reference-apps)
for the steps, from the repository layout to the issue. App Hub's
[PUBLISHING](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md)
is the reference for every gate rule.

## Development evidence

The records here describe the development copies before the 0.1.0 release.
Each describes the code at the time of its run, not the current code, and all
of them used synthetic providers.

| App | Record | Covers |
| --- | --- | --- |
| GitHub Notes | [VALIDATION.md](github-notes/VALIDATION.md) | The Rinx writer layout, host consent and account selection, and the signed installed journey |
| Inbox Assistant | [evidence/README.md](inbox/evidence/README.md) | The fixture checks, the integrated run with a real model, and the macOS soak |
| Google Calendar | [ACCEPTANCE.md](google-calendar/ACCEPTANCE.md) | The fixture checks, the installed journey, Glance routes, advisory chat, and the macOS soak |
| All three | [signed-install-5c7a13f9.json](evidence/signed-install-5c7a13f9.json) | Signed install and reopen, and refusal of tampered catalogs, sources and staging |

**Unverified:** live OAuth and provider writes, apart from the two macOS
checks that OctoSense records
([CAPABILITIES § Limits](../../docs/CAPABILITIES.md#limits)); Gmail delivery;
a physical send or save approval on a real device; Android background
behavior; and Windows and Linux. App Hub's
[0.1.1 admission record](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/admissions/connected-apps-0.1.1/README.md)
verified signed store install, upgrade from 0.1.0 and agent-file loading, not
native UI, live providers or physical approval.

## Data rules

- Keep every fixture, screenshot and recorded message fictional.
- Never commit provider tokens, OAuth client IDs or secrets, mailbox or
  calendar exports, private repository contents, real-account screenshots or
  `.local-state/`.
- Agent consent and provider sign-in are separate. Allowing an app's agent lets
  the configured model read what the agent's tools return.
- A model can't approve a protected write. The host review shows the saved
  content, and only the person approves it.
