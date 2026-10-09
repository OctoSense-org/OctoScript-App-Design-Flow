# Script Tool State

English | [简体中文](README.zh-CN.md)

This example migrates old `on_agent_tool` callbacks to the current
`app_tool(name, call_id)` contract. Its editor and declared tools share one
saved topic preference and revision. The assistant can read that state or
change it when explicitly requested; it has no mail, calendar, network or
Glance permission. See [the migration guide](../../docs/SUBMISSION-API-MIGRATIONS.md).

The manifest declares `script-tools-v1`; `tools.json` declares bounded
`toolstate.preferences` and `toolstate.set_preferences` tools implemented by
the app. The handler obtains host-stamped arguments through `request`, writes
state before `complete`, and rejects unknown names with `fail`.

## Native acceptance

**Do not remove `script-tools-v1` to run this in `card-host`.** That host
refuses the required runtime ABI. Build the `app-tool-acceptance` example in
the companion OctoSense change, then run from App Flow:

```sh
python3 examples/script-tool-state/verify-native.py \
  --host /path/to/app-tool-acceptance --hub /path/to/hub \
  --output /tmp/script-tool-state-evidence
```

The output directory must not exist. The driver first captures a real preview
for the copied bundle's listing, then stamps that copy. The native runner
verifies ephemeral signed admission, binds the actual script tools, and waits
until the instrument has observed the loaded UI before dispatching. It checks
the exact result and visible state, edits through real input, restarts and
reads the retained value through the tool. It also requires wrong-account,
undeclared-tool, invalid-input and unregistered-owner refusals.

All signing keys live only in memory; no public publisher identity is
created. All app state is synthetic and isolated. Native calls enter after
the production peer/consent relay: they do not prove model reasoning, human
consent to the agent, public Store installation, external effects or phone
execution. The driver records failures and stops only its own hidden native
processes. See `result.json` in the chosen evidence directory; screenshots
must still be inspected.

**Validated on macOS:** the release runner at OctoSense `77b7c6b5` passed the
signed gate, actual tool dispatch, exact state/output, manual Unicode edit,
restart persistence and all four refusal checks. All four native Metal
screenshots were inspected; content and controls are fully rendered with
system fonts disabled. See [validation.json](validation.json).

Two private mutations also failed as required: renaming the hook to
`on_agent_tool` returned `app_handler_missing`; removing `script-tools-v1`
was rejected when binding the tools. No contestant repository was modified.
This remains a development example, not a published app or a model/phone test.
