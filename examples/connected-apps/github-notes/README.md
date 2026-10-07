# GitHub Notes sample

English | [简体中文](README.zh-CN.md)

An ordinary App Hub bundle (`org.octosense.samples.githubnotes`) with local
Markdown drafts and host-reviewed GitHub commits. It requests `storage`, `auth`
and `github`, never a provider token or direct network access. Connecting does
not create an OctoSense cloud account.

Version 0.1.1 is published in App Hub from
[ymote/octosense-github-notes](https://github.com/ymote/octosense-github-notes).
It declares the app's optional agent, which 0.1.0 left out. This directory is
the unsigned development copy of 0.1.1, with the same agent and
[AGENT.md](bundle/AGENT.md). Its `listing.json` has placeholder publisher
fields, and its `manifest.json` has no signature; every other file matches the
published release. The [reference app guide](../README.md) explains how the
app is built and what to change before you reuse it.

The editor uses the layout of Rinx, the article writer that ships with
OctoSense: icon-only header and formatting controls, desktop
Source/Split/Preview, and a bottom formatting bar on phones. The style palette
also opens rich block editing. The editor keeps exact Markdown, rich selection,
undo/redo, code, table and math rendering, and local recovery, using the Rinx
v1.1.0 components. It leaves out Rinx's Matrix publishing and its image picker
and upload. Remote image URLs stay Markdown; this sample doesn't fetch their
pixels.

See the [Rinx writer validation](VALIDATION.md#rinx-writer-layout) for the
original reference comparisons, the revised installed workflow and the
OnePlus 6 captures. Earlier screenshots and soak receipts describe the previous
editor layout.

## Run

1. Use OctoSense desktop-v0.1.0-beta.2 or later; it includes the connected
   services and the `MarkdownEditor` widget.
2. Give the host a GitHub registration. The beta.2 download has none: add a
   GitHub OAuth client ID with device flow enabled to the host's
   `<apps root>/.host/oauth/clients.json`, as the
   [host setup guide](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/crates/oauth-service/README.md)
   describes. Without it, connecting fails with `OAuth is not configured`. A
   host built with its distributor's registration needs no file. Never put a
   client secret or token in this bundle or its app data.
3. Install the published GitHub Notes from App Hub, or install this copy from a
   local test catalog
   ([PUBLISHING §4](../../../docs/PUBLISHING.md#4-rehearse-the-store-path-locally)).
   Grant the displayed capabilities.
4. Write a note, then click the top-left back/file icon to open
   **Repository & file**. Choose public or private access, and complete GitHub
   consent in the host sheet and the browser. Private access grants GitHub's
   broader `repo` scope.
5. Select the account, repository, branch and file. For a new note, enter a new
   Markdown path and choose **Use as new path**. An existing file loads with its
   blob SHA; if the remote file has changed, GitHub refuses the commit and the
   app keeps your draft.
6. Set the commit message, return to the note and click the paper-plane icon.
   Check the exact content and destination in the host sheet, then choose
   **Approve & Save**. The app reports the commit only after GitHub returns its
   SHA.

## Drafts and accounts

Unsent edits are saved as alternating verified snapshots in the app's private
storage. Opening a different file explicitly keeps the current draft as a
recovery copy. A failed or cancelled remote save keeps the local draft. A
network timeout leaves the remote result unknown; check GitHub before you
retry. **Disconnect selected account** removes this app's OAuth connection and
keeps its local note.

The manifest declares `storage.accounts: true`. Startup reads `auth.active`, and
account choice calls `auth.select`, so the host and the app agree on the active
account. Browsing uses that selection. An open draft keeps its original account
and repository; switching accounts can't silently retarget its next commit. To
commit such a draft, select its original account or choose a new destination.

Rinx limits a parsed article to 512 KiB. A saved draft that fails to load stays
protected in the recovery/repository screen; typing into a blank editor can't
overwrite it. Explicitly replacing it with a valid file preserves its exact
recovery copy.

## Agent and read tools

This copy's manifest declares an optional agent that reads notes for the
person in the foreground:

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

The person reaches it through **Ask GitHub Notes**. Installing the app or
connecting GitHub doesn't allow the agent; the host asks for that separately.
Once the person allows it, their questions, the conversation and the results
of permitted reads can reach the model the host is configured with.
[AGENT.md](bundle/AGENT.md) keeps the agent to reading. It has no edit,
commit, delete or approval tool, it treats repository content as untrusted
data, and a change it suggests stays a proposal in the chat. Its reads
return the saved remote file, never the editor's unsaved draft. Writing and
saving notes needs no model.

The bundle declares `githubnotes.repositories`, `githubnotes.files` and
`githubnotes.read`. The host maps them to the matching GitHub read API under
this app's own connection and `github` grant. Each sets `private_data: true`,
`background: false` and `shareable: false`. The bundle exports no write,
approval or credential tool; saving still goes through the host review sheet.
The gate admits the agent (`hub check` grants `agent read-only`), but no live
model has run it, and the standalone editor fixture doesn't test the agent's
tool calls.

Version 0.1.0 shipped the same tools without the `agent` block, and OctoSense
offered **Ask GitHub Notes** for it anyway. Don't copy that pattern; see
[Tools without an agent block](../README.md#tools-without-an-agent-block).

## Current validation boundary

The standalone App Hub `card-host` admits the declared capabilities but has no
`MarkdownEditor`, so it can't run this sample by itself. Don't read its "first
frame drawn" as a working editor. OctoSense's `editor-host` fixture, which the
test starts and stops, exercises the real widget and the exact bundle source
without an account. The integrated `connected-app-host` also validates ordinary
bundle admission, real host consent, missing-registration errors, cancellation
and exact local draft retention.

Before the 0.1.0 release, the installed acceptance journey also passed with the
real Store, `prepare_launch`, the editor, the host APIs and the review sheets,
using a compile-only synthetic GitHub transport and an in-memory vault. It
covered repository pagination, empty repositories, a second file, dirty-note
protection, exact review and cancel, existing and new-file commits, a SHA
conflict, a lost response without automatic retry, and offline restart. The
original native PNGs and their receipts, which record the source hashes, are in
[VALIDATION.md](VALIDATION.md#signed-installed-provider-acceptance). The
[final host regression](VALIDATION.md#final-modal-and-cancellation-regression)
reran both journeys after the modal-input and cancellation fixes. To reproduce,
run these commands in an OctoSense checkout next to this repository:

```sh
cargo build --locked --release -p octosense-shell \
  --features mobile-apps,acceptance-fixtures \
  --example connected-app-host --example connected-install
python3 tools/connected-e2e/notes.py \
  --bundle ../OctoScript-App-Design-Flow/examples/connected-apps/github-notes/bundle
```

The driver ends with
`PASS: installed Notes flow with synthetic provider; native pixel review pending`.
The `acceptance-fixtures` feature is off in normal builds and refuses unmarked
profiles and real provider registrations. Only synthetic fixture data goes into
this test. The sample itself uses normal host APIs and has no fixture switch.

The [macOS soak report](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/tools/connected-e2e/evidence/notes-soak-20261006/README.md)
records 156 cycles, including a 10-minute run, exact draft recovery and review
cancellation. Memory grew during the runs; long-term memory stability is
unverified. The separate OnePlus 6 `OctoSenseNotesTest` APK passed local
editing, soft and hardware Enter, and exact cold-restart recovery after an
Android composing-word fix. The [phone setup](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/tools/connected-e2e/android-notes.md)
uses a signed private catalog and no provider credentials. The phone has no
GitHub connection configured, so this is not live repository acceptance.

**Unverified:** live GitHub OAuth, read, commit and conflict; Android
background lifecycle; Windows and Linux UI; the app agent's tool calls; a
physical save approval. On desktop-v0.1.0-beta.2, the host's GitHub review
sheet doesn't check for a physical press. OctoSense `main` requires one on its
native review (not in any release yet). Live acceptance
needs a device-flow client ID, human consent, and a disposable repository,
branch and path; no GitHub CLI credential is reused. Neither this copy nor the
published app has full Rinx feature parity. See [BRIEF.md](BRIEF.md) for the
task contract.
