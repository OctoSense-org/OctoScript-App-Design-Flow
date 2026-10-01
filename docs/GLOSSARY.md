# Glossary

One meaning per word. When another document uses one of these words, it means
this.

| Term | Meaning |
| --- | --- |
| **OctoSense app** | Anything a person installs or opens on an OctoSense device as an app. Two kinds ship through the App Hub: a script app and a card app. |
| **Script app** | An app whose bundle holds `main.splash`, a Splash program with its own state, handlers, storage and requests. The host evaluates it as it is in a policed isolate. The default kind, and the one this repository's [QUICKSTART](QUICKSTART.md) builds. |
| **Card app** | An app whose bundle holds `page.card` (L0), optional `page.data.json` and a `kit/`. The host lowers the card to widgets: presentation, no program. Produced by the [image-to-card flow](../flows/image-to-card/FLOW.md). |
| **System app** | A script app that ships inside a shell build rather than from the store (News, Photos, Maps, Camera, Mail, AI providers). Its id starts with `os.`, an id prefix no store may install. Lives in [OctoSense `apps/`](https://github.com/OctoSense-org/OctoSense/tree/main/apps). |
| **Bundle** | The directory that is the app: `manifest.json`, `listing.json`, the entry (`main.splash` or `page.card`), artwork and screenshots. The only thing submitted. Its bytes are hashed into the manifest by `hub stamp`. |
| **Manifest** | `bundle/manifest.json`: id, version, name, integrity digest (and signature), capabilities, network hosts, storage and compute requests, optional agent. The only thing an app may say about its own limits; unknown fields are refused. Schema: `crates/app-policy/src/manifest.rs` in OctoSense-App-Hub. |
| **Listing** | `bundle/listing.json`: what the store shows before install (subtitle, description, category, keywords, screenshots, icon, platforms, publisher, release notes, age rating, license). Reviewed with the bundle. Schema: `crates/app-policy/src/listing.rs`. |
| **Capability** | One named permission from the closed list `KNOWN_CAPABILITIES` (`storage`, `net`, `prompt`, `ledger.read`, `location`, `camera`, `clipboard`, `images`, `web`, `microphone`, `library`, `mail`, `llm`, `news`, `glance`, `model`, and 49 exact host-service names: four `octos.*`, 45 `matrix.*`). Not requested means not granted. See [CAPABILITIES](CAPABILITIES.md). |
| **Host service** | Work the shell does for an app, in Rust, with things the app must never hold (a socket, a credential, a device). The app calls `host.request("<family>.<method>", args, fn(r){…})`; the capability `<family>` must be granted. See [HOST-SERVICES](HOST-SERVICES.md). |
| **octos** | The agent kernel inside OctoSense ([octos-org/octos](https://github.com/octos-org/octos)): one per shell, configured by AI providers. Not `tools/octo`, which is this repository's CLI. See [AI-SERVICES](AI-SERVICES.md). |
| **AI providers** | The system app (`os.ai-providers`) where the person chooses the assistant's models and types keys, on host sheets. Its `llm` host service answers only system apps. |
| **App peer** | The octos peer the shell gives one app the assistant is granted to: private contexts, workspace and memory (`app/<app>/acct-<hash>`), owned by the system agent. Today only native modules (Rinx) get one. |
| **System agent** | The shell's own assistant session (`_main:api:octosense#system`), owner of every app peer. It holds no app's tools and cannot approve for an app. |
| **Agent files** | `tools.json`, `AGENT.md` and `skills/` beside `manifest.json`, plus the manifest's `agent` fields: an app's own agent (OctoSense ADR 0002). The App Hub gate admits them; once the person allows the app's agent, the OctoSense shells give it a peer with its `tools.json` tools, but do not install `AGENT.md` or skills yet. |
| **Sheet** | A host-owned surface a host service draws over an app, in its own isolate under no app's policy, for things only the person may type (a password). Only the sheet may call `<family>.sheet.*` methods. |
| **Card runner** | The part of an OctoSense shell (App Hub's `appstore` crate, `card` module) that runs one installed or system app: admit, resolve policy, jail, evaluate, pump host services. |
| **card-host** | App Hub's reference contained host for one bundle on the desktop (`crates/card-host`). The development runner: `card-host --bundle <dir> --allow-unsigned`. Same policy code as the Card runner. |
| **App Hub** | [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub): the publication contract, the gate, the scan, the signed catalog, the `hub` command, the store (`appstore`) and `card-host`. |
| **hub** | The App Hub's command-line tool (`crates/app-hub/src/bin/hub.rs`): `keygen`, `pubkey`, `certify`, `stamp`, `sign-manifest`, `check`, `scan`, `publish`, `withdraw`, `remove`, `verify`. Not GitHub's `hub` CLI. |
| **Gate** | `hub check`: the deterministic admission rules (file types, digest, assets, secrets, listing, policy, version and publisher continuity). The same code runs on the developer's machine and the hub. |
| **Scan** | `hub scan`: the review packet (the app's source, listing, grants, screenshots and seven questions) a reviewer, human or model, answers after the gate passes. |
| **Catalog** | `catalog.json`: the signed list of admitted app versions a store reads, with a copy of each bundle under `artifacts/`. Verified against a trust anchor before anything is shown. |
| **Isolate** | One Splash VM with its own heap, jail directory, storage quota, capability list, host allowlist, instruction budget and heap ceiling. Every app runs in its own. |
| **Splash** | Makepad's runtime script and widget language (`Splash` widget, `widgets/src/splash*.rs` in OctoSense-org/makepad). A script app's `main.splash` is Splash source. |
| **OctoScript** | The OctoSense layer above Makepad: the Octoscript VM packages, Octoscript-Makepad (the UI framework, kits and L0 lowering), and the name of this design flow. Not a separate language an app author writes. |
| **L0** | The declarative card language a card app's `page.card` is written in: data, state, events and views, lowered to widgets by a kit. Examples in [docs/l0/](l0/). |
| **Kit** | A named set of widgets and styles a card is lowered with (`kit/` in a card bundle); the [sketch kit flow](../flows/kits/sketch/FLOW.md) builds one. |
| **Flow** | A documented, step-by-step procedure in [flows/](../flows/README.md) (`FLOW.md`) that a person or agent follows from an input to a checked bundle. |
| **Stamp** | Writing the bundle's blake3 digest into `manifest.json` (`hub stamp <bundle>`). Every byte change needs a restamp; a signature covers the stamped digest. |
| **Publisher key** | The ed25519 key a publisher signs manifests with (`hub keygen`, `hub sign-manifest`). Private, outside every repository. Once on record, every later version must carry it. |
