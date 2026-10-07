# Set up the native runtime workspace

Every native app and card built here uses the release of
[OctoScript-Makepad](https://github.com/OctoSense-org/OctoScript-Makepad)
selected by `native-runtime.lock.json`. That framework owns `runtime.json`,
which fixes the underlying Makepad and OctoScript commits. Applications do not
carry alternate Makepad branches or compatibility patches.

```text
<workspace>/                  # this repository's parent, or $OCTOSENSE_WORKSPACE
  OctoScript-App-Design-Flow/ # this repository
    native-runtime.lock.json
    flows/  examples/  tools/
  octoscript-makepad/         # shared UI framework; runtime.json owns engine pins
  octoscript/                 # VM packages at the framework's revision
  makepad/                    # native platform at the framework's revision
```

1. From this repository's root, prepare the sibling repositories:

   ```sh
   python3 tools/setup-native.py
   ```

   The command keeps dirty source trees and custom Cargo configuration, and
   refuses a workspace inside this repository.

2. Verify the prepared set without changing it:

   ```sh
   python3 tools/setup-native.py --check
   ```

   On success it prints a JSON receipt of the verified sources. If a sibling
   does not match the lock, it stops with a `RuntimeError`, for example
   `<workspace>/makepad differs from the unified runtime source lock`
   (**✓ run** on a workspace whose `makepad` carries local patches). Revert
   the local changes, or prepare a clean workspace with `--root`.

| Option or variable | What it does |
| --- | --- |
| `--update` | Moves clean checkouts to a new release |
| `--cargo-manifest <Cargo.toml>` | Also checks that a Cargo workspace resolves one Makepad VM, platform, draw and widgets source, for example `--cargo-manifest examples/calendar/native/Cargo.toml` |
| `--root <dir>` or `OCTOSENSE_WORKSPACE` | Uses another workspace; the default is this repository's parent directory |
| `OCTOS_APPCARD_NATIVE_ROOT` | Sets where `flows/core/native_paths.py` looks for the prepared checkouts |

The WASM builder (`flows/image-to-card/wasm/build.py`) uses this release in
both its `existing` and `isolated` modes and applies no application-specific
runtime patches. To move to a new release, update the framework first, verify
its native and browser behavior, then update `native-runtime.lock.json` here.

Native UI checks use standalone release binaries, Makepad's built-in HTTP
instrument and hidden Metal windows. They do not need Makepad Studio. Close
each test instance you started with `/gq` (capture every window, then quit)
and check that it exited. See [the instrument runbook](../flows/core/NATIVE-INSTRUMENT.md).
