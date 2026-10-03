# Flow: script app from a text brief

Turn a written description of an app into a contained script app
(`main.splash`) that runs in `card-host`, passes the App Hub gate, and is
ready for the human publishing steps.

## Use when

- The input is text: what the app does, its screens, its data, who it is for.
- The app's behavior fits a contained isolate: its own storage, requests to
  declared hosts, and existing host services ([HOST-SERVICES](../../docs/HOST-SERVICES.md)).

Use another flow when the input is a design image or atlas
([image-to-card](../image-to-card/FLOW.md)), a Sketch file
([kits/sketch](../kits/sketch/FLOW.md)), or when the app needs new native code
or a new host service (that is a shell change, not a bundle). All flows:
[flows/README.md](../README.md).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| Brief | yes | Purpose, screens, actions, data sources, what is stored, error and empty states. |
| App id and name | yes | id `[a-z0-9.-]{1,64}`, not `os.*`. |
| Hosts the app will call | if any | Exact host names; each becomes `network.hosts`. |
| Publisher details | for publishing | Name, support contact, privacy-policy URL: **human** supplies them. |

## Prerequisites

```sh
tools/octo doctor        # pass: "[ok]" for python, hub and card-host, then "ready: …"
```

If it fails, follow its printed fix, or [QUICKSTART §1–2](../../docs/QUICKSTART.md#1-prerequisites).
A graphical session is required for step 5 onward.

For model-assisted work, use the [development and validation loop](../../docs/MODEL-VALIDATION.md)
with steps 4–9 below. Start with one populated screen and one working action;
after each repair, check initialization, inject real input and inspect the
resulting pixels. Keep original failures and bind the final evidence to the
tested source. That guide also distinguishes desktop hidden-window tests,
OctoSense App Studio on Android and separately authorized Android platform captures.

## Steps

`A=<app dir>`, `B=$A/bundle`, `P=<port>` (for example 8141), `HUB=<the hub path tools/octo doctor prints>`.

| # | Do (exact command or action) | Pass when | Human? |
| --- | --- | --- | --- |
| 1 | Write the brief into `$A/BRIEF.md` (outside `bundle/`): screens, actions, data, states, hosts, capabilities you think it needs and why. | Every screen and action has a line; every capability has a reason. | Confirm the brief with the requester if it was ambiguous. |
| 2 | `tools/octo new $A --id <id> --name "<Name>"` | Prints `created …` and `bundle stamped`. | no |
| 3 | Edit `$B/manifest.json`: capabilities and `network.hosts` from the brief, nothing more ([CAPABILITIES](../../docs/CAPABILITIES.md)). | Every capability maps to a line of the brief. | no |
| 4 | Write `$B/main.splash` using only APIs in [SCRIPT-API](../../docs/SCRIPT-API.md) or found in the runtime source; start from the template's structure (state `let`s, `fn`s, `start_timeout(0.05, …)` loader, one root view). | File saved; no API used that you could not cite. | no |
| 5 | `tools/octo run $B --port $P --hidden --detach` (exits 1 if `$P` is taken: quit the old instance with the `curl … /quit` it prints) | Prints the `admitted` and `ready: first frame drawn` lines; `grep -nE '\[E\]\|splash:[0-9]+:\|refused\|on_render closure failed\|callback error' $A/.local-state/card-host.log` prints nothing after `[SPLASH] eval:` (do not grep for "error": healthy runs log Metal's `MTLCompilerError` in `[ui-hang]` lines). | no |
| 6 | `tools/octo shot $P /tmp/first.png` (right away is fine: `run --detach` returns once the UI is drawn, and `shot` waits for a settled frame), then open it. | The first screen is visibly drawn and its expected initial fields are populated after loading; an admitted but partly initialized shell does not pass. | no |
| 7 | Drive every action in the brief: `curl -s "127.0.0.1:$P/click?x=&y=&wait=1"`, `curl -s "127.0.0.1:$P/t?t=…&wait=1"`, `/k?k=down&c=ReturnKey`; after each, a screenshot or `/snap?q=…` or the jail file under `$A/.local-state/<id>/`. Click a `TextInput` again before each `/t` (a button click takes its focus); screenshot pixels / 2 = click points on a Retina Mac. | Each action's effect is observed and recorded (command + what changed). | no |
| 8 | Test states: empty, error (e.g. network off or bad input), restart persistence (`curl -s 127.0.0.1:$P/quit`, rerun step 5). | Each state renders sensibly; stored data survives restart when the brief says so. | no |
| 9 | Return the reproduction, source revision, PNG and native state/log findings to the author; make a focused fix and repeat 4–8. Preserve failed runs separately. | Required paths pass against the final source; behavior assertions and direct visual review both pass. Earlier screenshots cannot verify later edits. | no |
| 10 | Edit `$B/listing.json`: subtitle, description (what it does, truthfully), category, keywords, platforms tested, release notes. Leave publisher fields for the human if unknown. Replace `$B/assets/icon.svg`. | Listing parses (step 12) and says only what the app does. | Publisher name/support/privacy URL: **human**. |
| 11 | Drive the app to its best real state; `tools/octo shot $P $B/screenshots/01-main.png` (add `02-…png` for more screens, max 8, list them in `listing.json`); open each; `curl -s 127.0.0.1:$P/quit`. | Each PNG is a real capture you looked at. | no |
| 12 | `tools/octo check $B` | `<id> <version> — PASSED`, only the unsigned warning; no placeholder note (or placeholders are waiting on the human). | no |
| 13 | `"$HUB" scan $B --packet $A/build/review.json`, then write answers to its 7 questions into `$A/build/REVIEW-ANSWERS.md`. | Packet written; every question answered honestly. | no |
| 14 | Report (see [AGENTS.md](../../AGENTS.md#reporting)): commands run and their results, screenshots, what was not verified. **Stop.** | Report delivered. | Hand-off to a human. |

## Outputs

- `$A/bundle/` — `manifest.json` (stamped), `listing.json`, `main.splash`,
  `assets/icon.svg`, `screenshots/*.png`: the submission candidate.
- `$A/BRIEF.md`, `$A/build/review.json`, `$A/build/REVIEW-ANSWERS.md`,
  `$A/AGENTS.md`: outside the bundle, not submitted.
- The `tools/octo check` output, verbatim.

## Hand-off

Continue with [docs/PUBLISHING.md](../../docs/PUBLISHING.md) from
§3.6: the publisher key, signing and the submission are **human** steps. An
agent drafts the submission text; a person signs and submits.
