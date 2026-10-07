# GitHub Notes development validation

These are development records from before the 0.1.0 release. Each section
describes the code at the time of its run, not the current code. Versions
0.1.0 and 0.1.1 were later published from
[ymote/octosense-github-notes](https://github.com/ymote/octosense-github-notes);
the [README](README.md) gives the current status.

## Rinx writer layout

The Notes editor used the article writer's icon header, Source/Split/Preview on
wide windows, a bottom formatting bar on narrow ones, the style palette, the
native table picker and the paper preview. The extra Notes title, the
Repository/Save text-button row and the mode-label rows were removed.
Repository setup and exact GitHub review remained separate surfaces. The
document caption identified the file; it did not rewrite a heading.

The [native reference report](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/tools/connected-e2e/evidence/rinx-writer-20261006/README.md)
contains the original Rinx writer captures, the diagnostic entry hook, source
hashes and the Notes component captures at matching window sizes. Both the
narrow and the wide native interaction suites passed Unicode retention,
selection formatting, undo/redo, mode switching, rich input and table
insertion. The layout was adapted from the Rinx source with GitHub semantics;
it doesn't reproduce every Rinx feature.

The [installed receipt](evidence/rinx-writer-installed/receipt.json) and
[visual review](evidence/rinx-writer-installed/manual-review.json) validated
the signed sample, including exact host review and cancel, synthetic existing
and new commits, a conflict, an uncertain response and an offline restart. All
ten original PNGs were inspected. The first run exposed an offscreen
repository-status row; the corrected layout passed the same assertions. The
earlier receipts below describe the previous text-button UI.

The final review also reproduced a rejected-load hazard: an oversized saved note
left an editable blank document. The corrected app kept that draft closed until
the person explicitly chose a valid file or recovery copy, so typing could not
mark the rejected draft ready. The
[native recovery regression](evidence/rejected-draft-recovery/receipt.json) and
[original frames](evidence/rejected-draft-recovery/manual-review.json) passed.
The full ten-case installed flow passed again afterward, with byte-identical UI
captures. The prior receipt stays alongside the final one for comparison.

The [revised writer soak](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/tools/connected-e2e/evidence/notes-rinx-soak-20261006/README.md)
records 36 cycles over ten minutes before the recovery guard and a 12-cycle
regression after it. Both preserved exact drafts, rich-edit undo and cancelled
review without provider writes. The report notes finite memory growth and
doesn't treat the runs as proof of leak-free operation.

The [OnePlus 6 report](https://github.com/OctoSense-org/OctoSense/blob/desktop-v0.1.0-beta.2/tools/connected-e2e/evidence/notes-rinx-phone-20261006/README.md)
records the separate test APK, the retained draft, real soft Enter and text
input, keyboard open and dismiss, an exact cold restart and the preview. The
floating shell navigation hid while the IME was visible and returned to its
previous dock afterward. No normal Home profile or provider account was copied,
and no live GitHub save ran.

Data was fictional; there was no account login, provider key, GitHub commit or
physical phone interaction. This is scoped development evidence, not release
approval or a numeric UX score.

## Initial editor run

OctoSense base `4081c30e` plus the uncommitted connected-services/editor changes;
Rinx `4b89097d8791a7190d01de1c576979c93df0013d` (v1.1.0);
Makepad `c155f61d0e1600d2ec474209374444a38a09a470` with the workspace's existing
runtime patch stack. The test started a hidden macOS `editor-host` at
430 × 850 logical points (860 × 1700 captured pixels) with the light fixture
theme. The final fixture launch used `--remote=8158` and was shut down with
`/quit`.

| Artifact | SHA-256 |
| --- | --- |
| main.splash | `ccb24a97a5135107784087468ee74f952a5cae2db97314f8711e00984bc78001` |
| Markdown editor lib.rs | `5081d03ecedff31ffef1f1a71c9d545a1803b086dd638383504990cd1cd544a4` |
| editor-host source | `2e907bec62489ce3deab70e1f33d74f196de87bcbfba48803b52da69b3803762` |
| editor-host binary | `69e55124510fc2020e62b0c7745970007005ffb267c00f80d96632aadf9fe6c8` |
| 01-preview.png | `3ca56a8d0888667c7ef1a8c07f0b1a2250d956c114c28f858f102e1674454491` |
| 02-connection-unavailable.png | `4ae30ba375d24ef8b2d697d352df6fdbe0d90df481f80e38d1f1e78cd0b9b03a` |

The sample ID was later normalized to `org.octosense.samples.githubnotes` for
the tool namespace grammar, and a read-only `tools.json` was added. The UI
captures above predate that metadata-only rename and those declarations; the
recorded fixture source and binary hashes identify the build that was captured.
Native brokered tool execution was not part of that capture.

## Checks and observations

- `tools/octo doctor`: passed with the rebuilt adjacent Hub tools.
- `cargo check --locked -p octosense-markdown-editor --all-targets`: passed.
- `cargo test --locked -p octosense-markdown-editor --lib`: 2 passed.
- Release build of `editor-host`: passed. The existing upstream Makepad
  dead-code and workspace duplicate-bin/lib warnings remained; the editor added
  none.
- Native source input included Chinese, accented text, headings, bold, lists, a
  table and a Rust code fence. Source → Write → Preview → Source preserved the
  exact Markdown string. The original pixels were opened and inspected.
- Rinx cross-block native selection and replacement changed the authoritative
  Markdown. Undo restored the full original, Redo restored the replacement, and
  another Undo restored the source used in the final screenshot.
- Quit and relaunch read the alternating snapshot and restored the exact note.
- The default fixture's `auth.connect` returned unavailable. The error appeared
  in both native text inspection and pixels; the note remained editable.
- The read-only provider fixture selected `sample-writer/notes` and the second
  file, `second-note.md`. Confirmation protected the dirty note, the displayed
  file matched the choice, and **Recover previous draft** restored the original.
- The fixture refused `github.review_save` with an explicit simulated conflict.
  The local source stayed intact. This tested error handling, not a real SHA
  conflict or host approval.
- Repository scrolling reached the commit message and the recovery action. The
  editor toolbar scrolled to Undo/Redo. No scrolling benchmark, phone IME test
  or accessibility audit was run.

The historical captures are [preview](evidence/initial-editor/01-preview.png)
and [unavailable connection](evidence/initial-editor/02-connection-unavailable.png).
Both are original native captures from the exact source above; the second one
states that it comes from an offline editor test host.

## Failures found and repaired

1. Generic `card-host` admitted the app but lacked `MarkdownEditor`, so boot
   reported `widget 'editor' not found in tree`. The sample needs the integrated
   OctoSense host; the editor was not silently replaced by a `TextInput`, and no
   generic `card-host` functional pass is claimed.
2. The new host widget was initially missing from Makepad's public prelude;
   exporting the composite made it available in a fresh isolate.
3. Rinx style application during draw initially read the outer heap. Entering
   the widget's owner isolate for native draw and input removed that crash.
4. The composite's internal status ID shadowed the app's status ID. Namespacing
   it fixed status updates; the final PNGs show the distinct messages.
5. The fixture's service reply needed an explicit redraw signal after replying,
   so that asynchronous widget updates were presented. The fix was in the
   fixture host; it is not a per-frame redraw loop or an app-side visibility
   toggle.

## Admission before release

`tools/octo check` printed:

```text
org.octosense.samples.githubnotes 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
```

The normalized identity and all three `host_method` read aliases passed the
rebuilt Hub gate. The bundle BLAKE3 at that point was
`be32e021bf4d87f3b8226e8372dfc18193574eb718b4e08e274e7093dd74030d`. This
checked manifest and alias admission, not brokered provider execution.

`tools/octo check` also reported the publisher placeholders, left for the
publisher to fill in. A scan packet and seven answers were written under the
ignored `build/`, the count recorded at that time; the route was
**human-review**. A bundle that ships `tools.json`, `AGENT.md` or skills gets
an eighth question; the published 0.1.0 answers all eight in its repository's
`review/ANSWERS.md`.

## Integrated consent and account selection regression

The next bundle added `storage.accounts: true`, read the selected host account
through `auth.active`, and switched it through `auth.select`. Browsing used that
account; an open note kept its original account, repository and file binding.
Saving to a different account required an explicit new destination. These
changes postdate the editor-only screenshots above.

OctoSense's `tools/check-connected-oauth.py` used the real integrated native
host, ordinary bundle admission and a fresh disposable profile. It recorded
source and binary hashes, native snapshots, original PNGs, logs and a separate
run directory on every attempt, including failures. It never used a real
provider registration or copied credentials. Account switching used two
synthetic metadata records with no scopes or tokens; provider reads stopped at
the missing host configuration.

The checks covered public-repository consent, missing host configuration,
cancelling before and after **Continue**, exact Unicode draft retention, and
loading host account A, then selecting and persisting account B without
rebinding the note. Static consent ink was compared in decoded native PNGs,
because functional text matches alone are not visual acceptance.

A first driver version matched the underlying app's error label behind the
opaque consent sheet before the sheet's next half-second status poll, so the
original pixels still said `Preparing secure sign-in…`.

The host deliberately settled the original app request on an authorization
error; that callback and the sheet's next poll had separate valid destinations.
Code review and the delayed failure snapshot showed the error eventually in the
sheet itself, with no reproduced cross-isolate widget lookup leak.

The receipt of run `run-20261006T182306Z-1791310986537236000` therefore has a
separate `manual-review.json` that marks the sheet-error evidence incomplete
despite its initial functional pass. The hardened driver targeted the
namespaced `oauth_status` and kept its pre-rename failure as run
`run-20261006T182356Z-1791311036066174000`.

The next run, `run-20261006T182638Z-1791311198445340000`, passed after the
integrated host was rebuilt with namespaced sheet selectors and
production-equivalent modal input routing. Every original native frame was
inspected individually. The
[missing-registration frame](evidence/connected-host/02-missing-registration.png)
showed the error inside the host sheet itself, and the
[selected-account frame](evidence/connected-host/05-selected-host-account.png)
and [retained note](evidence/connected-host/06-account-selection-retains-draft.png)
showed the completed account scenario. The portable
[receipt](evidence/connected-host/receipt.json), which records the source
hashes, and the separate
[visual review](evidence/connected-host/manual-review.json) keep exact source,
binary and PNG hashes without absolute local paths, credentials or profile
files. This accepts that scoped development scenario only.

| Integrated artifact | SHA-256 |
| --- | --- |
| main.splash | `274385b0970581978b3dcfa8380b54c6b2c1ac354c6e16e39c33ad9bb72bcfef` |
| manifest.json | `5c2b847a03e11fa8dfd718aa07fa17de862a1f5bd5bccc95814fa4514ac6fa47` |
| connected-app-host source | `e91ac8d89c0aaa9ea0a443781583d5b99beff9de310b372e0378471a6207e40b` |
| connected-app-host binary | `17e414f258ea820f4e167d316598678518de6fe2bdfe6afc8898a74a97bc1303` |
| native regression driver | `691a1e257bae1eb85e5fc5ac39b64d738373587f8554c7da7be23aa31babfea8` |

That release build, a Python syntax check, the bundle gate and
`git diff --check` passed. The native process the test started exited
normally, and no test instance was left running. The failed startup-race and
premature-status-match runs were kept locally, not overwritten.

Hub revision `eaaffffd695caf7ebf6205c455377c1f8567b906` made a host sheet's
isolate retire before replacement and rejected requests the retired sheet had
already queued. After the native host was rebuilt against that pin, run
`run-20261006T184328Z-1791312208067398000` passed the same complete consent,
cancel/reopen and metadata-only account-selection journey. All six original
frames were inspected individually, and the process exited normally. The
[new receipt](evidence/connected-host-eaaffffd/receipt.json),
[visual review](evidence/connected-host-eaaffffd/manual-review.json),
[sheet error](evidence/connected-host-eaaffffd/02-missing-registration.png) and
[retained draft](evidence/connected-host-eaaffffd/06-account-selection-retains-draft.png)
are additional evidence; the earlier artifacts above are unchanged.

This native binary has SHA-256
`07120a62ca518ed820bc4cea58f3725f4dd8e54690c02739422bced931ce975b`;
its `Cargo.lock` hash is
`076b4bf53fff10c08a540ba6c58c231f452248a2ebf4869aebb89872569b24d9`.
The driver and host example source hashes are unchanged from the preceding
table. The native journey tested normal teardown and reopen. The Hub's separate
Splash/pump regression tested cross-family replacement, discarding stale close
and mutation requests, late replies and prior sheet state; all 19 appstore
library tests passed for that change.

The signed-install example was also rebuilt against this Hub revision and
passed for the exact GitHub Notes, Inbox and Google Calendar bundles. It used an
ephemeral private signed catalog and bundles, reopened the installed policy,
refused unsigned and untrusted catalogs and source or cross-app tampering, and
verified cleanup and unchanged source bundles. The
[portable installation receipt](../evidence/signed-install-eaaffffd.json)
records the binary and source hashes. This checked Store installation, not
installed UI execution or a real provider connection.

No Makepad renderer patch is claimed: the static consent title and description
kept exactly 5,542 and 17,199 dark pixels before and after the asynchronous
callback. The earlier suspected general label loss did not reproduce under
individual PNG and RGB inspection. The historical Inbox missing-control
captures are separate evidence, and this work does not declare them fixed.

Not verified at that point: real OAuth and device authorization, the installed
App Hub permission flow, live GitHub read/commit/conflict, exact host review
with a real provider, remote image loading and upload, Android, iOS, Windows,
Linux, Glance and chat, model execution and physical sending. The component
doesn't reproduce Rinx's full Matrix publication and image-picker features.

## Signed installed provider acceptance

The later run `run-1791313763946328000` passed the installed Notes journey with
bundle BLAKE3 `c254ddb25658e9243e2313cf7edcc953452cf15c5afe96ba4227ad0482c65016`.
It used real signed private-catalog Store installation, `prepare_launch` and
verified installed source, the Rinx editor, normal account selection, the host
GitHub API adapter and immutable host review. A non-default
`acceptance-fixtures` build injected only a synthetic GitHub HTTPS transport and
an in-memory vault, for an explicitly marked disposable profile. No real
provider registration, account token or repository was used. This lifted the
earlier `installed UI execution not verified` limit for this scoped macOS test
only.

The [receipt](evidence/installed-synthetic-provider/receipt.json) records the
binary, driver, service, editor and bundle hashes, every native action, and a
sanitized method/path/status provider journal. The binary SHA-256 is
`f0f6448a42a5a6fbdf3180e633fd82d44eb4d5bfdbb051a3226853e3471a5842`.
All nine published original PNGs were opened individually at 860 × 1700 pixels;
the [visual review](evidence/installed-synthetic-provider/manual-review.json) is
separate from the automated assertions. These artifacts include no profiles,
private keys, account metadata, raw tokens or private logs.

The journey showed:

- Signed installation and reopen preserved an exact unsent Unicode note.
- Empty repository pages kept **Previous**, and an empty repository explained
  how to choose a new file. The directory list opened the selected second file.
- Refusing dirty-note replacement kept the original; accepting replacement
  stored a recovery copy and loaded the intended remote Markdown.
- [Host review](evidence/installed-synthetic-provider/02-exact-host-review.png)
  showed the exact repository, branch, file, commit message and changed time.
  Cancel sent no provider write and kept the exact edited content.
- A [successful synthetic commit](evidence/installed-synthetic-provider/04-synthetic-commit-confirmed.png)
  returned a commit SHA and cleared the dirty state only for the reviewed
  content.
- A [409 conflict](evidence/installed-synthetic-provider/05-provider-conflict.png)
  kept the draft and removed the consumed approval action, with a visible
  return to editing. There was no overwrite or automatic retry.
- An explicit new `.md` path was created through the same host review and API
  path.
- The [lost-response case](evidence/installed-synthetic-provider/07-uncertain-save-response.png)
  modelled a provider that stored the commit before the connection failed.
  Local state stayed dirty, approval could not be reused, and no duplicate
  request was sent.
- [Offline installed restart](evidence/installed-synthetic-provider/08-offline-restart-retains-note.png)
  preserved the exact unsent text and destination and displayed the provider
  error.

The provider journal contains four explicit PUT attempts: a successful existing
file, a conflict, a successful new file and an uncertain response. All normal
app, account, scope and review gates stayed in the path. Synthetic instrument
clicks on this isolated fixture are not evidence of physical human approval.

The failures kept locally included:

- an invalid 64-hex fixture revision, which production validation correctly
  refused;
- a driver that queried the selected Markdown tab by its inactive label;
- an overstrict footer margin;
- an offscreen label selector;
- input sent while the review sheet was still closing.

The hardened driver waited for the modal to retire before editing again. Two real sample defects were fixed: **Previous**
was missing on an empty repository page, and a delayed local-save timer could
hide an immediate host save error. No validation rule was relaxed to pass the
tests.

A separate [three-app install receipt](evidence/signed-install-current.json)
records successful signed installation and reopen, plus rejection of an
unsigned catalog, an untrusted anchor, source tampering and cross-app staging,
for the three bundles of that time. Private signing keys existed only in
memory; temporary install data was removed, and the source bundles stayed
unchanged.

Reproduction commands are in [README.md](README.md) and OctoSense's
`tools/connected-e2e/README.md`. Real GitHub device authorization and network
reads and writes were outstanding: they need a registered OAuth client with
device flow enabled, human consent and an explicit disposable repository,
branch and file. This small host doesn't run the production agent kernel, the
peer tool broker or Glance. Android, Windows and Linux UI, live GitHub
delivery, physical approval and public catalog publication were still
unverified.

## Final modal and cancellation regression

After the host's modal-input and sheet-lifecycle fixes, both complete native
journeys were rebuilt and rerun against Hub
`5c7a13f92fa25d36ba1fe7fb99dc9fb1b235f8d3`. Notes run
`run-1791315334124061000` passed all ten installed and provider-fixture checks;
consent run `run-20261006T193534Z-1791315334138335000` passed missing
registration, cancellation before and after **Continue**, account selection and
retained Unicode text. Both used host binary SHA-256
`ef8b5e4c7fcb01b52b6c71fbec2980b87d0b69e7b1a106e8658159fb06e6ff9d`.

The new [installed receipt](evidence/installed-synthetic-provider-5c7a13f9/receipt.json)
and [visual review](evidence/installed-synthetic-provider-5c7a13f9/manual-review.json)
record the final sources and nine individually inspected original frames. The
new [consent receipt](evidence/connected-host-5c7a13f9/receipt.json) and
[visual review](evidence/connected-host-5c7a13f9/manual-review.json) contain six
individually inspected frames. Earlier successes and failures were kept
separately. No credentials, private profiles or raw runtime logs were copied
into the evidence.

That build routed pointer, keyboard and text input only to the visible host
sheet, captured host widget references before app evaluation, and cancelled the
exact pending review when its host surface was dismissed. The focused native
Glance policy test and the Gmail sheet-close gate test passed separately; these
Notes runs are not a Glance or physical-send test.

The [final three-app signed-install receipt](evidence/signed-install-5c7a13f9.json)
passed installation, reopen and tamper refusal for the Notes, Inbox and
Calendar bundle digests of that time. The installed journey's provider
transport was synthetic. Live GitHub OAuth, reads and writes still need a
registered device-flow client, human consent and a chosen disposable
repository, branch and path.
