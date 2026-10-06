# Robrix port verification

The port is implemented in `apps/robrix/native` and linked into both OctoSense
launchers. The original Robrix checkout is unchanged. The port adds no
changes to the shared framework repositories. This record covers the imported Matrix client and
the installed L0 message-summary card; it does not certify Signal support.

## Dependency and build checks

- Runtime verification passed for OctoSense, OctoSense-mobile and the standalone
  Robrix manifest. Each graph resolves one Makepad widgets crate from
  Octoscript-Makepad's locked runtime; there is no Robrix-specific Makepad fork.
- macOS release builds passed for both launchers. The standalone native client
  also built and opened with the native Metal renderer during the port.
- Android arm64 release APK packaging passed using the existing SDK/NDK and
  AWS-LC's supported CC builder. No CMake installation was required.
- The two AppCard payload tests passed: installed recipe rendering, unknown
  recipe/version rejection, text escaping, kit ownership and size limits.
- All three existing mobile launcher catalog tests passed, including creating
  and tearing down the six registered application modules.
- The existing module pointer-routing test passed in the isolated mobile
  worktree.
- All 28 existing SQLite ledger tests passed after aligning rusqlite to 0.37
  and libsqlite3-sys to 0.35 for the Matrix SDK and AppCard engine.

Builds still report existing AppCard dead-code/deprecation warnings, optional
unused Cargo patches and an Android launcher-icon warning. They are not
zero-warning builds. Optional upstream `tsp` and `agent_chat` feature builds,
iOS device execution and WebAssembly are outside this port's verification.

## Native execution

The reproducible desktop check is `scripts/verify_native.py`. It starts its own
release process with `MAKEPAD_HIDE_WINDOWS=1`, verifies the built-in HTTP
instrument's PID, exercises native text input or the L0 card, captures three
GPU frames with `/gseq`, and closes with `/gq`. It records executable hashes,
requires exit code zero, and fails on shader/script errors or panic markers.
Closing and reopening the module exercises its isolate and Matrix-runtime
cleanup. No Makepad Studio or CPU-rendered screenshot is used.

Android uses a separate `dev.makepad.octosense.robrixpreview` package and
`scripts/open_android.py`. The pinned Android backend has no HTTP instrument;
captures come from the launcher's app-owned GPU texture readback, with real
ADB input. These images exclude Android system UI and the keyboard. The
existing Mail package and the phone's Home role are not changed.

Desktop and the macOS phone shell both passed login input, module close/reopen
and native AppCard rendering, with no shader/script errors and clean exit.
Both also passed an in-app capability probe of the selected Palpo server:
entering its URL and clicking sign-in hid unsupported SSO controls. No password
was entered and no account credentials were submitted.

The selected physical device is **OnePlus 6T / ONEPLUS A6013**, serial
`YOUR_DEVICE_SERIAL`, running Android 11. Always pass `--serial YOUR_DEVICE_SERIAL` when testing
with both phones attached. The earlier OnePlus 6 exploration is not the target
acceptance record and further Robrix testing uses only the 6T.

The Android capture hook requests a GPU readback and consumes its result on
the next five-second timer tick. Allow at least twelve seconds after input
before pulling the PNG. The hook also requests a redraw, so these captures
verify rendered state, not spontaneous repaint latency. An early observation
used an older captured frame; the speculative host redraw workaround was
removed. Neither launcher's phone event routing is changed by this port.

Final mobile acceptance uses an isolated worktree with clean locked Makepad
and Octoscript-Makepad sources. This avoids unrelated Android integration
changes being developed concurrently in the shared workspace. Those changes
were preserved; they are not part of the Robrix port. The isolated APK is the
mobile acceptance artifact. The desktop's final shared-workspace build includes
those unrelated framework edits, recorded in `evidence/framework-worktree.json`.

The final Android APK passed fixture text input, an in-app Palpo capability
probe and the installed L0 card preview on the 6T. No shader/script error or
panic markers were found in those process logs. The preview fixture is local;
receiving an AppCard over Matrix still requires authenticated testing.
The test process was stopped after capture; the APK remains installed.

The evidence index is evidence/index.json (`evidence/index.json`, retained locally). Final phone
records are oneplus6t-acceptance.json (`evidence/oneplus6t-acceptance.json`, retained locally),
Palpo login (`evidence/oneplus6t-acceptance-palpo.png`, retained locally) and
native AppCard (`evidence/oneplus6t-acceptance-card.png`, retained locally). The final isolated
macOS phone-shell records are mobile-acceptance.json (`evidence/mobile-acceptance.json`, retained locally)
and mobile-card-acceptance.json (`evidence/mobile-card-acceptance.json`, retained locally).

## Palpo service check

The selected endpoint is `https://matrix.example.org`, which resolves to
`69.194.3.128`. On 2026-09-16, HTTPS requests from this Mac passed normal
certificate validation and returned:

| Endpoint | Result |
| --- | --- |
| `/_matrix/client/versions` | HTTP 200; Palpo 0.4.0; Matrix versions through v1.12 |
| `/_matrix/client/v3/login` | HTTP 200; password and application-service login |
| `/.well-known/matrix/client` | HTTP 200; homeserver URL points to this endpoint |

The server advertises both `org.matrix.msc3575` and
`org.matrix.simplified_msc3575`, plus cross-signing support. This is a suitable
candidate for the imported Matrix SDK. Advertised capabilities alone do not
prove authenticated synchronization or E2EE operation.

The local SSH alias `mini3` points to another address, `69.194.3.249`, whose
checked Matrix ports refused connections. Use the supplied HTTPS endpoint,
not that SSH alias, for this app's test configuration. No server was installed,
started or reconfigured.

The OnePlus 6T also fetched all three endpoints directly over Wi-Fi with
normal HTTPS certificate validation, without a Mac proxy. The application also completed its own capability probe and correctly hid SSO
providers unsupported by this Palpo server. No Matrix account was
supplied or used in these checks. Real login, Sliding Sync, message/media
exchange, session restoration and device verification/E2EE remain unverified
until a test account is entered in the application. The narrow phone login
footer still truncates its final informational label; authenticated room
layouts have not yet had device acceptance coverage.

## Reproduction notes

The local isolated workspace is `.appcard-native/robrix/workspace/` under
`octosense-org/`. `mobile-port.patch` beside it records the Robrix-only mobile
changes against `45dbbfb`. This is a temporary test checkout of the same
repositories, not another application or framework fork. The source changes
also remain in the normal application repositories.

Keep runtime directories and credentials outside the source import. The native
test script uses a fresh `OCTOSENSE_ROBRIX_DATA_DIR`; Android uses only the
separate preview package. Never put login passwords in instrument commands,
source files or committed evidence.

The inherited font build step materializes ignored `system_*` resources.
macOS uses local system-font symlinks; Android/iOS uses distributable font
files, including the shared Makepad RobotoFlex face. Complete Mac builds and
their UI checks before building/packaging Android from the same checkout, or
use separate checkouts. Concurrent cross-platform builds would race on those
generated resource filenames.

When publishing the port, include the nested `octos` submodule's rusqlite
change and update its parent gitlink along with the AppCards and launcher
changes. A local path-only edit in an uncommitted submodule is insufficient
for a fresh checkout.
