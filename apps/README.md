# Apps

Runnable apps built with the image-to-appcard pipeline live in `apps/<name>/`.
Each app owns its service code, reviewed card scenes, design source, launcher,
tests and fixture evidence. App runtime state and personal data stay ignored.

| App | Platform | Description |
| --- | --- | --- |
| [Aircon](aircon/README.md) | Native cards / WASM | One purchase-to-installation journey with 12 screen states and 14 extracted service-card variants. |
| [Finance](finance/README.md) | macOS / Android / shared launcher module | US, Hong Kong and mainland stock watchlists, Matplot charts, news and platform HTML reader. |
| [Robrix](robrix/README.md) | macOS / Android launcher module | Matrix client imported from Robrix2, with native L0 AppCards in messages. |
| [Mail](mail/README.md) | macOS, iOS-style UI | Gmail POP3 inbox, SMTP sending, IMAP folders/flags, native HTML reader and attachments. |
| [School](school/README.md) | Native cards / WASM | School notice, calendar and payment journey. |
| [Health](health/README.md) | Native cards / WASM | Fictional health-check booking journey. |
| [Reunion](reunion/README.md) | Native cards / WASM | Reunion planning, RSVP and payment journey. |

All seven projects are siblings here. The repository root is
`Octosense-Service-AppCards/`; there is no nested `pipeline/` checkout.
Makepad and Octoscript live in the separate [native workspace](../docs/NATIVE-WORKSPACE.md).
[shared/](shared/README.md) contains common browser adapters and historical
cross-app verification artifacts, not another application.

Within an app, `cards/` holds full screen states. For example,
`aircon/cards/aircon-01` through `aircon-12` are twelve screens of **one Aircon
app**, not twelve apps. `service-cards/` holds smaller interactive panels
extracted from those screens—an order, installation appointment, calendar update
or payment panel—with their own data and actions. Their owner names identify
services within the journey, not additional app projects.

Image-authored apps keep their design source, scenes, service code and
`image-to-appcard-flow.json` together. Robrix preserves its imported native
design and documents the shared message-card renderer in its app README. Run the shared pipeline from the repository
root, choosing an app explicitly:

```sh
bash tools/image-to-appcard-flow.sh plan \
  --project "$PWD/apps/aircon" \
  --manifest "$PWD/apps/aircon/image-to-appcard-flow.json"
```

For native UI tests, use [Makepad's built-in instrument](../lab/core/NATIVE-INSTRUMENT.md)
and hidden windows. Older Studio scripts and receipts are historical material;
moving them does not constitute a fresh native or image-parity acceptance.

`app/` remains the shared Android client. `a2app/apps/` and `a2app-l0/apps/`
contain agent specifications. Shared authoring and conversion tools remain in
`lab/`; app implementations belong here.
