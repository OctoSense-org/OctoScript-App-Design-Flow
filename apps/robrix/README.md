# Robrix for OctoSense

Source preservation checkpoint (2026-10-06): this is the historical native-module
integration. The current live Mail/Calendar demo ships in the unified
[OctoSense repository](https://github.com/OctoSense-org/OctoSense). Historical
`evidence/` captures stay local and are excluded from this source commit; run the
provided verifiers for new evidence. Device/provider and full native builds were
not rerun for this preservation checkpoint.

Robrix2's Matrix client is a native application at `apps/robrix`, alongside
Mail and the other applications. Both OctoSense and OctoSense-mobile link its
`octosense-robrix` crate as an `AppModule`. The imported client retains its
login, rooms, timeline, search, media, account settings and Matrix encryption
code. This is a Matrix client, not a Signal protocol implementation.

The source import is recorded in [upstream.json](upstream.json):
`Project-Robius-China/robrix2` at `7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8`.
The original local checkout is separate. Imported code retains its
[MIT notice](LICENSE-MIT); bundled font notices are in
[native/resources/licenses](native/resources/licenses/README.md).

## Shared runtime and build

Keep these repositories beside one another under `octosense-org/`:

```text
OctoSense/
OctoSense-mobile/
Octosense-Service-AppCards/apps/robrix/
octoscript-makepad/
makepad/
octoscript/
```

All consumers select Octoscript-Makepad `b1596d9c2cee6e80cca9d27b1b0c2d57b9d28dd8`
through their `native-runtime.lock.json`. That release selects Makepad
`d4502ef1e4d196d2829a07aa137740cb0581e9b4` and Octoscript
`5430518683462eebb65b56b9b5d0e620006f04f4`. Robrix has no private Makepad fork.
Root Cargo path patches must resolve to those sibling checkouts.

The AppCard engine and `octos-core` use rusqlite 0.37, matching the Matrix SDK's
libsqlite3-sys 0.35. Both launchers patch the legacy AppCard Git dependencies
to this repository's `app/app` and `octos/crates/octos-core`. The `octos` submodule needs the committed [SQLite compatibility patch](octos-sqlite.patch), which preserves its upstream commit pin. From the repository root:

```sh
git submodule update --init octos
git -C octos apply --check ../apps/robrix/octos-sqlite.patch
git -C octos apply ../apps/robrix/octos-sqlite.patch
```

Apply it once to a clean submodule; on an already prepared checkout, verify with
`git -C octos apply --reverse --check ../apps/robrix/octos-sqlite.patch` instead.

From either launcher repository:

```sh
python3 tools/setup-native.py --check --cargo-manifest Cargo.toml
cargo run --release -- --test-action launch-robrix
```

For the phone shell on macOS, add `--features mobile-apps,mobile-only` before
`--`. Robrix is linked by default and opens as one module instance; reopening
focuses the existing client. Other desktop modules retain their hosting policy.
For a standalone desktop client, run `cargo run --release` from `native/`.
The `standalone` feature owns the independent entry point; hosts disable it so
Android has only the launcher's Java/JNI application entry.

For Android, use the existing SDK and the locked Makepad build tool from
OctoSense-mobile:

```sh
cargo build --release --manifest-path ../makepad/tools/cargo_makepad/Cargo.toml
../makepad/target/release/cargo-makepad makepad android \
  --sdk-path=/path/to/existing/android_sdk \
  --package-name=dev.makepad.octosense.robrixpreview --app-label='OctoSense Robrix' \
  build -p octosense --release
```

The preview uses a separate Android package. It does not require changing the
phone's Home role. Robrix connects directly from the phone to the homeserver;
no Mac proxy or service is part of its Matrix transport. The launchers configure
the locked AWS-LC CC builder to use the existing Android arm64 NDK Clang.
No extra CMake installation is needed for this target. Enter account details
in the app. Port tests use fictional text, never a real password through the
instrument. iOS device deployment is outside the current verification.

## Application and card boundaries

`native/src/app.rs` separates the windowless `RobrixContent` from the standalone
window. `native/src/module.rs` registers those widgets in the host's isolate,
forwards events with Robrix's application state, and releases runtime and UI
references on close. The host forwards foreground changes. Window DPI and
updater controls remain host-owned. The responsive widget cache belongs to
Robrix and is cleared before freeing its isolate. Account files use an OctoSense Robrix data
directory, separate from the original Robrix installation.

The shared AppCard route is:

```text
Matrix org.octos.appcard data
  → installed service-cards recipe + host-owned kit
  → Octoscript L0 realization
  → Octoscript-Makepad lowering
  → native RobrixAppCard widget inside a timeline message
```

Version 1 supports the read-only `robrix.message-summary` recipe. Its
[fixture](service-cards/message-summary/fixture.json) defines the message data.
Each text field is limited to 8 KiB. Unknown versions, recipes or invalid data
fall back to the Matrix message's ordinary text. A payload cannot replace the
installed recipe or kit. Existing upstream `org.octos.splash_card` rendering
remains a separate legacy path.

The host also accepts validated module arguments in `MAKEPAD_APP_CONFIG`:

```json
{"module_open":{"robrix":{"card_preview":true}}}
```

Launch Robrix with that config to render the fictional AppCard without creating
a Matrix client. Normal launches omit `card_preview`. This allows pipeline
native-render checks independently of account login. The imported Robrix design
is the design source for this port; no new image atlas or image-parity approval
is claimed. New image-derived cards belong in this app's `service-cards/` and
use the shared pipeline's native validation requirements.

## Verification

Use [Makepad's built-in instrument](../../lab/core/NATIVE-INSTRUMENT.md), release
builds and `MAKEPAD_HIDE_WINDOWS=1`; the hidden native window still uses Metal.
Capture the app drawable and finish owned runs with `/gq`. Android does not
expose that HTTP instrument at this pinned revision; use its existing app-owned
GPU readback hook and real device input. Allow at least twelve seconds after
input for its two timer stages. The hook requests redraw, so it does not
measure spontaneous repaint latency.

From the AppCards repository, reproduce a hidden native check with:

```sh
python3 apps/robrix/scripts/verify_native.py \
  --host ../OctoSense-mobile --output apps/robrix/runtime/mobile-check --reopen
# Use a different output directory and --card-preview to test the L0 fixture.
```

Each run owns a fresh `OCTOSENSE_HOME` and `OCTOSENSE_ROBRIX_DATA_DIR`, uses only
fictional input, records executable hashes and captures, and closes via `/gq`.
The output directory must be new. Android installation and opening use:

```sh
python3 apps/robrix/scripts/open_android.py \
  --adb /path/to/existing/platform-tools/adb --serial YOUR_DEVICE_SERIAL \
  --apk /path/to/built.apk --capture
# --card-preview selects the fictional L0 card without a Matrix client.
```

Choose your own Matrix-compatible integration server; `https://matrix.example.org` is a placeholder.
Probe its password-login capabilities without credentials with:

```sh
python3 apps/robrix/scripts/verify_native.py \
  --host ../OctoSense --output apps/robrix/runtime/palpo-check \
  --homeserver https://matrix.example.org
```

See [verification.md](verification.md) for the checks and remaining service
validation. Build logs and private runtime state are not part of the source
import.
