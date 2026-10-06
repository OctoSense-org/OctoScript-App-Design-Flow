# GitHub Notes sample

[简体中文](README.zh-CN.md)

An ordinary App Hub bundle (`org.octosense.samples.githubnotes`) with local
Markdown drafts and host-reviewed GitHub commits. It requests `storage`, `auth`
and `github`, never a provider token or direct network access. Connecting does
not create an OctoSense cloud account.

The editor is the host's Rinx-backed `MarkdownEditor`: Write, exact Markdown,
Preview, formatting, rich selection, undo/redo, code/table/math rendering and
local recovery. It shares the existing Rinx v1.1.0 component revision. The Rinx
Matrix publication flow and binary image picker/upload are not included. Remote
image URLs remain Markdown; this sample does not fetch their pixels.

## Run

1. Build OctoSense with the connected-services change and `app-hub`. Configure
   the host's GitHub OAuth client registration, with device flow enabled. Never
   put a client secret or token in this bundle or its app data.
2. Install this bundle through App Hub using a test catalog/local bundle. Grant
   the displayed capabilities. It uses its own ordinary identity, not `os.mail`
   or an installed Rinx account.
3. Write a note before connecting. Open **Repository**, choose public or private
   repository access, and complete GitHub consent in the OctoSense sheet and
   external browser. Private access uses GitHub's broader `repo` scope; review
   that choice carefully in the host sheet.
4. Select the account, repository, branch and file. For a new note, enter a new
   Markdown path and choose **Use as new path**. Existing files load their blob
   SHA; a conflicting remote version cannot be silently overwritten.
5. Set the commit message, return to the note and choose **Save**. Review the
   exact content and destination in the host sheet. A returned commit SHA is
   required before the app reports a committed result.

Unsent edits use alternating verified snapshots in the app's private jail.
Opening a different file explicitly preserves the current draft as a recovery
copy. A failed or cancelled remote save retains the local draft. A network
timeout may have an unknown remote outcome: inspect GitHub before trying again.
Disconnect removes this app's OAuth connection, while retaining its local note.
The manifest declares `storage.accounts: true`. Startup reads `auth.active`, and
account choice calls `auth.select` so the host and app agree on the active
account. Browsing uses that selection. An open draft retains its original
account/repository identity; switching accounts cannot silently retarget its
next commit. Select the original account or explicitly choose a new destination.

## Agent read tools

The bundle declares `githubnotes.repositories`, `githubnotes.files` and
`githubnotes.read`. The host maps them to the corresponding GitHub read API
under this app’s own connection and `github` grant. Each is private-data,
foreground-only and non-shareable. No write, approval or credential tool is
exported; saving still goes through the exact host review sheet. Brokered
execution and cross-app access remain subject to the host’s authorization; the
standalone editor fixture does not validate that route.

## Current validation boundary

The standalone App Hub `card-host` admits the declared capabilities but does not
install OctoSense's `MarkdownEditor`; it cannot run this sample by itself yet.
Do not interpret its “first frame drawn” as a functioning editor. The owned
OctoSense `editor-host` fixture exercises the real widget and exact bundle source
without an account. The integrated `connected-app-host` additionally validates
ordinary bundle admission, real host consent, missing-registration errors,
cancellation and exact local draft retention; see [VALIDATION.md](VALIDATION.md).

Live OAuth, host-approved GitHub commits, remote conflicts, clean installed-app
execution, phone keyboard/lifecycle, Windows and Linux are not yet validated.
The listing retains explicit publisher placeholders pending human identity and
privacy-policy review. This is a development sample, not a published app or a
claim of full Rinx feature parity. See [BRIEF.md](BRIEF.md) for the task contract.
