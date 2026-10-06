# GitHub Notes development validation

2026-10-06. Source authored, native input injected and original PNGs reviewed
by Codex. Data is fictional; there was no account login, provider key, GitHub
commit or physical phone interaction. This is scoped development evidence, not
release approval or a numerical UX score.

## Receipt

OctoSense base `4081c30e` plus the uncommitted connected-services/editor changes;
Rinx `4b89097d8791a7190d01de1c576979c93df0013d` (v1.1.0);
Makepad `c155f61d0e1600d2ec474209374444a38a09a470` with the workspace's existing
runtime patch stack. Owned hidden macOS native `editor-host`, 430 × 850 logical
points, 860 × 1700 captured pixels, light fixture theme. Final fixture launch
used `--remote=8158`; it was shut down with `/quit`.

| Artifact | SHA-256 |
| --- | --- |
| main.splash | `ccb24a97a5135107784087468ee74f952a5cae2db97314f8711e00984bc78001` |
| Markdown editor lib.rs | `5081d03ecedff31ffef1f1a71c9d545a1803b086dd638383504990cd1cd544a4` |
| editor-host source | `2e907bec62489ce3deab70e1f33d74f196de87bcbfba48803b52da69b3803762` |
| editor-host binary | `69e55124510fc2020e62b0c7745970007005ffb267c00f80d96632aadf9fe6c8` |
| 01-preview.png | `3ca56a8d0888667c7ef1a8c07f0b1a2250d956c114c28f858f102e1674454491` |
| 02-connection-unavailable.png | `4ae30ba375d24ef8b2d697d352df6fdbe0d90df481f80e38d1f1e78cd0b9b03a` |

The sample ID was subsequently normalized to
`org.octosense.samples.githubnotes` for the tool namespace grammar, and a
read-only `tools.json` was added. The original UI captures above predate that
metadata-only rename and those declarations; the recorded fixture source and
binary hashes identify the actual captured build. Native brokered tool execution
was not part of that capture.

## Checks and observations

- `tools/octo doctor`: passed with the rebuilt adjacent Hub tools.
- `cargo check --locked -p octosense-markdown-editor --all-targets`: passed.
- `cargo test --locked -p octosense-markdown-editor --lib`: 2 passed.
- Release build of `editor-host`: passed. Existing upstream Makepad dead-code
  and workspace duplicate-bin/lib warnings remain; no editor warning added.
- Native source input included Chinese, accented text, headings, bold, lists,
  table and a Rust code fence. Source → Write → Preview → Source preserved the
  exact Markdown string. Original pixels were opened and inspected.
- Rinx cross-block native selection/replacement changed the authoritative
  Markdown. Undo restored the full original, Redo restored the replacement,
  and another Undo restored the source used in the final screenshot.
- Quit/relaunch read the alternating snapshot and restored the exact note.
- Default fixture `auth.connect` returned unavailable. The error appeared in
  both native text inspection and pixels; the note remained editable.
- Read-only provider fixture selected `sample-writer/notes` and the second file,
  `second-note.md`. Confirmation protected the dirty note, the displayed file
  matched the choice, and Recover previous draft restored the original.
- The fixture refused `github.review_save` with an explicit simulated conflict.
  Local source stayed intact. This tests error handling, not a real SHA conflict
  or host approval.
- Repository scrolling reached the commit message and recovery action. The
  editor toolbar scrolled to Undo/Redo. No measured scrolling benchmark, phone
  IME test or accessibility audit was performed.

The final captures are [preview](bundle/screenshots/01-preview.png) and
[unavailable connection](bundle/screenshots/02-connection-unavailable.png).
They are original native captures from the exact source above. The latter
clearly states that this is an offline editor test host.

## Failures found and repaired

1. Generic `card-host` admitted the app but lacked `MarkdownEditor`, so boot
   reported `widget editor not found`. The limitation remains explicit; this
   sample needs the integrated OctoSense host. It is not silently replaced by a
   TextInput. No generic card-host functional pass is claimed.
2. The new host widget initially was not copied into Makepad's public prelude;
   exporting the composite fixed its availability in a fresh isolate.
3. Rinx style application during draw initially read the outer heap. Entering
   the widget's owner isolate for native draw/input removed that crash.
4. The composite's internal status ID shadowed the app's status ID. Namespacing
   it fixed status updates. Final PNGs show the correct distinct messages.
5. The fixture's service reply needed an explicit redraw/signal after replying
   so asynchronous widget updates were presented. This is in the fixture host;
   it is not a per-frame redraw loop or an app-side visibility toggle.

## Admission and unfinished release work

`tools/octo check` prints:

```text
org.octosense.samples.githubnotes 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
```

The normalized identity and all three `host_method` read aliases passed the
rebuilt Hub gate. The bundle BLAKE3 at that point was:
`be32e021bf4d87f3b8226e8372dfc18193574eb718b4e08e274e7093dd74030d`.
This is manifest/alias admission, not brokered provider execution.

## Integrated consent and account selection regression

The subsequent bundle adds `storage.accounts: true`, reads the selected host
account through `auth.active`, and switches it through `auth.select`. Browsing
uses that account; an open note keeps its original account/repository/file
binding. Saving to a different account requires an explicit new destination.
These behavior changes postdate the editor-only screenshots above.

`OctoSense/tools/check-connected-oauth.py` uses the real integrated native host,
ordinary bundle admission and a fresh disposable profile. It records source
and binary hashes, native snapshots, original PNGs, logs, and a separate run
directory on every attempt, including failure. It never uses a real provider
registration or copies credentials. Account switching uses two synthetic
metadata records with no scopes or tokens; provider reads stop at missing host
configuration.

The current checks cover public-repository consent, missing host configuration,
cancelling before and after Continue, exact Unicode draft retention, loading
host account A and selecting/persisting account B without rebinding the note.
Static consent ink is compared from decoded native PNGs; functional text
matches alone are not visual acceptance.

A first driver version matched the underlying app's error label behind the
opaque consent sheet before the sheet's next half-second status poll. Original
pixels therefore still said “Preparing secure sign-in…”. The host deliberately
settles the original app request on an authorization error; that callback and
the sheet's next poll have separate valid destinations. Code review and the
delayed failure snapshot show the error eventually in the sheet itself, with
no reproduced cross-isolate widget lookup leak.
The receipt in local run
`target/connected-oauth-native/run-20261006T182306Z-1791310986537236000`
therefore has a separate `manual-review.json` marking sheet-error evidence
incomplete despite its initial functional pass. The hardened driver targets
the namespaced `oauth_status`, and preserved its pre-rename failure in
`run-20261006T182356Z-1791311036066174000`.

The earlier run, `run-20261006T182638Z-1791311198445340000`, passed after rebuilding
the integrated host with namespaced sheet selectors and production-equivalent
modal input routing. Every original native frame was inspected individually;
the [missing-registration frame](evidence/connected-host/02-missing-registration.png)
now shows the error inside the host sheet itself. The
[selected-account frame](evidence/connected-host/05-selected-host-account.png)
and [retained note](evidence/connected-host/06-account-selection-retains-draft.png)
show the completed account scenario. The portable
[source-bound receipt](evidence/connected-host/receipt.json) and separate
[visual review](evidence/connected-host/manual-review.json) retain exact source,
binary and PNG hashes without absolute local paths, credentials or profile
files. This is acceptance of that scoped development scenario only.

| Integrated artifact | SHA-256 |
| --- | --- |
| main.splash | `274385b0970581978b3dcfa8380b54c6b2c1ac354c6e16e39c33ad9bb72bcfef` |
| manifest.json | `5c2b847a03e11fa8dfd718aa07fa17de862a1f5bd5bccc95814fa4514ac6fa47` |
| connected-app-host source | `e91ac8d89c0aaa9ea0a443781583d5b99beff9de310b372e0378471a6207e40b` |
| connected-app-host binary | `17e414f258ea820f4e167d316598678518de6fe2bdfe6afc8898a74a97bc1303` |
| native regression driver | `691a1e257bae1eb85e5fc5ac39b64d738373587f8554c7da7be23aa31babfea8` |

That release build, Python syntax check, bundle gate and `git diff --check`
passed. The owned native process exited normally; no test instance was left
running. The failed startup-race and premature-status-match runs remain under
the ignored local test-output directory rather than being overwritten.

The final Hub revision `eaaffffd695caf7ebf6205c455377c1f8567b906` retires a host
sheet's isolate before replacement and rejects requests already queued by the
retired sheet. After rebuilding the native host against that pin, run
`run-20261006T184328Z-1791312208067398000` passed the same complete consent,
cancel/reopen and metadata-only account-selection journey. All six original
frames were individually inspected; the process exited normally. The
[new receipt](evidence/connected-host-eaaffffd/receipt.json),
[visual review](evidence/connected-host-eaaffffd/manual-review.json),
[sheet error](evidence/connected-host-eaaffffd/02-missing-registration.png) and
[retained draft](evidence/connected-host-eaaffffd/06-account-selection-retains-draft.png)
are additional evidence; the earlier artifacts above remain unchanged.

This final native binary has SHA-256
`07120a62ca518ed820bc4cea58f3725f4dd8e54690c02739422bced931ce975b`;
its `Cargo.lock` hash is
`076b4bf53fff10c08a540ba6c58c231f452248a2ebf4869aebb89872569b24d9`.
The driver and host example source hashes are unchanged from the preceding
table. The native journey tests normal teardown/reopen behavior. The Hub's
separate actual Splash/pump regression tests cross-family replacement,
discarding stale close/mutation requests, late replies and prior sheet state;
all 19 appstore library tests passed for that change.

The signed-install example was also rebuilt against this final Hub revision
and passed for the exact GitHub Notes, Inbox and Google Calendar bundles. It
used an ephemeral private signed catalog and bundles, reopened the installed
policy, refused unsigned/untrusted catalogs and source/cross-app tampering,
and verified cleanup and unchanged source bundles. The
[portable installation receipt](../evidence/signed-install-eaaffffd.json)
records the binary and source hashes. This checks Store installation, not
installed UI execution or a real provider connection.

No Makepad renderer patch is claimed: the static consent title and description
retained exactly 5,542 and 17,199 dark pixels before and after the asynchronous
callback. Earlier suspected general label loss did not reproduce under
individual PNG and RGB inspection. Historical Inbox missing-control captures
remain separate evidence and are not declared fixed by this work.

The tool also reports the publisher template placeholders. These remain for
human publisher identity, support and privacy-policy review. A scan packet and
seven review answers were generated under ignored `build/`; route is
**human-review**, not published/approved.

Not verified: real OAuth/device authorization, installed App Hub permission
flow, live GitHub read/commit/conflict, exact host review with a real provider,
remote image loading/upload, Android/iOS/Windows/Linux, Glance/chat, model
execution and physical sending. Rinx's full Matrix publication and image-picker
feature set is not reproduced by this component. These limits must remain in
handoff and store claims.


## Signed installed provider acceptance

The later run `run-1791313763946328000` passes the installed Notes journey with
bundle BLAKE3 `c254ddb25658e9243e2313cf7edcc953452cf15c5afe96ba4227ad0482c65016`.
It uses real signed private-catalog Store installation, `prepare_launch` and
verified installed source, the Rinx editor, normal account selection, host
GitHub API adapter and immutable host review. A non-default
`acceptance-fixtures` build injects only a synthetic GitHub HTTPS transport and
in-memory vault for an explicitly marked disposable profile. No real provider
registration, account token or repository was used. This supersedes the earlier
“installed UI execution not verified” limit for this scoped macOS test only.

The [source-bound receipt](evidence/installed-synthetic-provider/receipt.json)
records binary, driver, service, editor and bundle hashes, every native action,
and a sanitized method/path/status provider journal. The binary SHA-256 is
`f0f6448a42a5a6fbdf3180e633fd82d44eb4d5bfdbb051a3226853e3471a5842`.
All nine published original PNGs were opened individually at 860 × 1700 pixels;
[visual review](evidence/installed-synthetic-provider/manual-review.json) is
separate from the automated assertions. No profiles, private keys, account
metadata, raw tokens or private logs are included in these artifacts.

The journey proves:

- Signed installation and reopen preserve an exact unsent Unicode note.
- Empty repository pages retain **Previous**; an empty repository explains how
  to choose a new file. The directory list opens the selected second file.
- Refusing dirty-note replacement keeps the original; accepting replacement
  stores a recovery copy and loads the intended remote Markdown.
- [Host review](evidence/installed-synthetic-provider/02-exact-host-review.png)
  shows the exact repository, branch, file, commit message and changed time.
  Cancel sends no provider write and retains the exact edited content.
- A [successful synthetic commit](evidence/installed-synthetic-provider/04-synthetic-commit-confirmed.png)
  returns a commit SHA and clears dirty state only for the reviewed content.
- A [409 conflict](evidence/installed-synthetic-provider/05-provider-conflict.png)
  retains the draft; the consumed approval action is removed, with a visible
  return to editing. There is no overwrite or automatic retry.
- An explicit new `.md` path is created through the same host review/API path.
- The [lost-response case](evidence/installed-synthetic-provider/07-uncertain-save-response.png)
  models a provider storing the commit before the connection fails. Local state
  stays dirty, approval cannot be reused, and no duplicate request is issued.
- [Offline installed restart](evidence/installed-synthetic-provider/08-offline-restart-retains-note.png)
  preserves the exact unsent text and destination and displays the provider error.

The provider journal contains four explicit PUT attempts: successful existing
file, conflict, successful new file, and uncertain response. All normal
app/account/scope/review gates remain in the path. Synthetic instrument clicks
on this isolated fixture are not evidence of physical human approval.

Failures retained under ignored `target/connected-notes-e2e` include an invalid
64-hex fixture revision correctly refused by production validation, a driver
that queried the selected Markdown tab by its inactive label, an overstrict
footer margin, an offscreen label selector, and input attempted while the review
sheet was still closing. The hardened driver waits for actual modal retirement
before editing again. Two real sample defects were fixed: **Previous** was
missing on an empty repository page, and a delayed local-save timer could hide
an immediate host save error. No validation rule was relaxed to pass the tests.

A separate [current three-app install receipt](evidence/signed-install-current.json)
records successful signed installation/reopen plus unsigned catalog, untrusted
anchor, source tamper and cross-app staging rejection for the three current
bundles. Private signing keys existed only in memory; temporary install data was
removed and the source bundles remained unchanged.

Reproduction commands are in [README.md](README.md) and OctoSense's
`tools/connected-e2e/README.md`. Real GitHub device authorization and network
read/write remain outstanding: they require a registered OAuth client with
device flow enabled, human consent and an explicit disposable repository,
branch and file. This small host does not run the production agent kernel,
peer tool broker or Glance. Android, Windows/Linux UI, live GitHub delivery,
physical approval and public catalog publication remain unverified.

## Final modal and cancellation regression

After the host modal-input and sheet-lifecycle fixes, both complete native
journeys were rebuilt and rerun against Hub
`5c7a13f92fa25d36ba1fe7fb99dc9fb1b235f8d3`. Notes run
`run-1791315334124061000` passed all ten installed/provider-fixture checks;
consent run `run-20261006T193534Z-1791315334138335000` passed missing registration,
cancellation before/after Continue, account selection and retained Unicode text.
Both used host binary SHA-256
`ef8b5e4c7fcb01b52b6c71fbec2980b87d0b69e7b1a106e8658159fb06e6ff9d`.

The new [installed receipt](evidence/installed-synthetic-provider-5c7a13f9/receipt.json)
and [visual review](evidence/installed-synthetic-provider-5c7a13f9/manual-review.json)
record the final sources and nine individually inspected original frames. The
new [consent receipt](evidence/connected-host-5c7a13f9/receipt.json) and
[visual review](evidence/connected-host-5c7a13f9/manual-review.json) contain six
individually inspected frames. Earlier successes and failures remain separate.
No credentials, private profiles or raw runtime logs were copied into evidence.

This build routes pointer, keyboard and text input only to the visible host
sheet, captures host widget references before app evaluation, and cancels the
exact pending review when its host surface is dismissed. The focused native
Glance policy test and Gmail sheet-close gate test passed separately; Notes is
not being claimed as a Glance or physical-send test.

The [final three-app signed-install receipt](evidence/signed-install-5c7a13f9.json)
passed installation, reopen and tamper refusal for the current Notes, Inbox and
Calendar bundle digests. Provider transport remains synthetic in the installed
journey. Live GitHub OAuth/read/write still requires a registered device-flow
client, human consent and a chosen disposable repository/branch/path.
