# GitHub Notes

An independently installed App Hub app (`org.octosense.samples.githubnotes`)
for writing Markdown and saving a reviewed version to an existing GitHub
repository. This reuses the host's `MarkdownEditor`, backed by Rinx v1.1.0
`article-core` and `article-makepad`; it does not embed Rinx's Matrix account or
publication controller.

## Journey

1. Open a local draft immediately in the Rinx article writer layout. Edit exact
   Markdown or read the preview; wide windows also offer split view. The writer
   uses the original icon toolbar and phone bottom formatting bar. Rich block
   editing and undo/redo remain available through the style panel. Remote images
   are not fetched by this sample, and image binary upload is not implemented.
2. Connect GitHub through the OctoSense OAuth sheet. Passwords and device codes
   never enter the app's UI or storage. Choose public-repository access or the
   broader private-repository scope explicitly in that host consent screen.
3. Select a repository, branch and Markdown file from a directory listing, or
   provide a new `.md` path. Keep the current local draft before changing files;
   require an explicit replacement confirmation when the draft differs.
4. Load the remote file and its content SHA. On save, show the frozen content,
   repository, branch, path and commit message in the host review sheet. Only
   its approval performs the remote commit. A returned commit SHA establishes
   success. A click alone does not.
5. A remote conflict keeps the draft, offers loading the latest remote version
   separately, and never automatically retries or overwrites it. Cancel and
   service-unavailable failures leave editing usable. Restart restores the
   exact unsaved draft and its GitHub binding.

## Screens and data

- Editor: Rinx article writer header and formatting icons, with Source/Split/Preview
  on desktop and Source/Preview plus bottom formatting on phones. The back/file
  icon opens repository settings; the publish icon opens GitHub save review.
  A compact local-save status and document caption replace the extra Notes
  title, text button rows and destination row. Editing uses the whole viewport.
- Repository drawer: connection status, connection/revocation actions,
  repositories, branch, directory/file selection, path and commit message.
- Replace confirmation: describes the incoming file and offers Keep draft or
  Replace; preserved drafts remain recoverable locally.
- Empty/offline: a new local note, with a clear optional connection action.
- Error: specific service error with the draft retained, not a fake success.
- Local state: current source, original loaded content, content SHA, selected
  repo/branch/path, opaque app-bound connection handle, and one recovery draft.
  These are private app data and never part of the submitted bundle.

## Capabilities and host contract

- `storage`: private local drafts and restart recovery.
- `auth`: GitHub consent, account handles and disconnect.
- `github`: repositories, files, Markdown read and host-reviewed commit.
- No `net`, token, account identifier, fixed repository, AI-provider key or
  direct endpoint appears in the app. No AI feature is required for editing.

Runtime changes live in OctoSense. The normal standalone `card-host` currently
lacks this host-installed editor vocabulary and live provider services; native
local widget testing uses OctoSense's `editor-host` with no account and no writes.
The signed installed `connected-app-host` acceptance additionally exercises the
real host APIs with an explicitly synthetic provider transport and vault.
Installed-shell authentication and remote commits need a configured OAuth app
and explicit human review. Tests must distinguish that path from local UI.

## Acceptance

Author: Codex. Test driver/reviewer: Codex native Makepad instrument, hidden
owned process with synthetic notes; real account consent remains with the user.
Compare original native Rinx writer captures at the same narrow and wide sizes.
Exercise source → rich → preview → source without losing Markdown; edit a
second block, undo/redo, long-document scrolling, narrow viewport, restart,
missing service and failed load. Test actual repository read/commit/conflict in
a disposable repository once host OAuth registration is available. Never claim
Android, Windows, Linux, Glance/chat or live publication passed from macOS UI
fixtures. No autonomous model generation or numeric UX grade is asserted.
