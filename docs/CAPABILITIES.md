# Capabilities

A capability is a permission an app asks for in `manifest.json`:

```json
"capabilities": ["storage", "net"],
"network": { "hosts": ["api.open-meteo.com"] }
```

The list is closed (`KNOWN_CAPABILITIES` in OctoSense-App-Hub
`crates/app-contract/src/manifest.rs`, the app contract every host and app
links since App Hub #46; `crates/app-policy` re-exports it). A name not on it is refused by the gate
(`policy: app <id> requests unknown capability "<name>"`). Not requested means
not granted. Before install the store shows two things derived from the
manifest, never from the listing: one **permission** line per capability
(`permissions_summary`, `crates/app-hub/src/index.rs`; an app with none shows
"Draw its screens, and nothing else") and the **privacy** summary
(`privacy_summary`, `crates/app-policy/src/listing.rs`). Both are quoted
below as of App Hub `79a2c4f`; the `research`, `crawl`, `prompt` and `agent` rows were rechecked at `41bc959` (2026-10-01).

Ask for the least the app needs; the scan asks the reviewer to "name any grant
nothing on screen needs".

## The list

| Capability | Unlocks | The person sees (store) | Rules and runtime behavior |
| --- | --- | --- | --- |
| `storage` | The app's own jail: `fs.*`, camera captures, and the local files a widget reads, such as a map archive (quota: `storage.max_bytes`, ceiling 16 MiB; system apps 64 MiB). | Permission: "Keep its own data on this device". Privacy: "Keeps its own data on this device, in a space only it can read." Without it: "Stores nothing." | The jail is one directory per app id. Without `storage` the app has no jail: every `fs.*` call errors (`storage not available in this context`), a capture saves nothing, and a widget reads no local file. `hub check` warns when a script calls `fs` or the app requests `camera` without `storage`, and its `grants:` line says `storage none`. `card-host` enforces this from App Hub `6a639e3a`; the OctoSense shells do once they pin that App Hub or later. |
| `net` | `net.http_request` (and `net.*`) to exactly the hosts in `network.hosts`. | Permission: "Reach only: *hosts*". Privacy: "Contacts only: *hosts*." Without it (or with no hosts): "Never contacts the network." | Hosts are bare, exact, lowercase names: no scheme, path, port, wildcard (`policy: host "https://x" must be a bare host name…`). Hosts without `net` are refused (`lists hosts but does not request the net capability`). `net` with an empty list reaches nothing and `net` is not even defined in the script. Requests to other hosts: `this app may not reach <url>`. The gate refuses a `.splash` naming an undeclared `https://` host, and any `http://`. |
| `images` | Pictures (`Image{src: http_resource(url)}`) from **any public `https://` host**, beyond `network.hosts`. For a feed reader's thumbnails. | Permission: "Show pictures from any website". Privacy: "Shows pictures from any website its content links to." | Only public https hosts; private and internal addresses are refused (`host not permitted (private/internal): <h>`). Does not widen `net.http_request`. With `images` the gate stops checking `https://` hosts in the source. |
| `web` | Opening **any public `https://` page** in `WebReader` (the system web view), which has no way back into the app. | Permission: "Open web pages in a browser view". Privacy: "Opens web pages, which cannot reach back into the app." | Without `web`, `WebReader.open` works only for listed hosts and refuses others: `refused <url>: not on this app's host list, and no \`web\` grant`. With `web` the gate stops checking `https://` hosts in the source. |
| `camera` | `CameraPreview`: preview, photo and video capture into the jail (`DCIM/IMG_<ms>.jpg`, `DCIM/VID_<ms>.mp4`). | Permission: "Use the camera". Privacy: "Uses the camera." | Without it `CameraPreview` refuses: `this app was not granted the camera`. The OS permission prompt still applies. A capture is saved in the jail, so it needs `storage` too; without it the preview shows and a capture saves nothing. |
| `microphone` | Sound in camera videos. | Permission: "Use the microphone". Privacy: "Records sound with videos." | Only meaningful with `camera`. |
| `library` | Copying captures to the system photo library, where other apps can see them. | Permission: "Save to your photo library, where other apps can see it". Privacy: "Saves photos and videos to your photo library." | Without it captures stay in the app's jail. |
| `location` | The device position: `sys.gps(...)`, MapView's follow camera. | Permission: "Use your location". Privacy: "Uses your location." | Without it `sys.gps("ok")` reads 0 (no fix). OS permission still applies. |
| `mail` | The `mail` host service: `host.request("mail.<method>", …)` for accounts the person adds on the host's sheet. | Permission: "Read and send mail from accounts you sign in to on the device". Privacy: "Reads and sends mail from accounts you add; it never sees your password." | See [HOST-SERVICES](HOST-SERVICES.md). Needs a shell that registers the Mail service (card-host does not). |
| `llm` | The `llm` host service of the AI providers system app: its model providers with masked key status, and host sheets for typing, showing and scanning a provider key. | Permission: "Manage the assistant's AI providers, whose keys stay with the device". Privacy: "Manages the assistant's AI providers; it never sees your API keys." | Added in App Hub `c5cdb17` (#11). The service answers only `os.*` apps (`apps/ai-providers/host-service/src/lib.rs` in OctoSense), so a store app gains nothing from it: do not request it. |
| `news` | The `news` host service: stories the device collects on a schedule from its feeds and topic feeds (`news.list`, `news.read`, …). | Permission: "Read news the device collects from its feeds and topics". Privacy: "Reads news the device collects from its feeds and topics." | On App Hub `main` (#18) and in the shells' App Hub pin. The service in OctoSense (`apps/news/host-service`) answers only `os.*` apps, so a store app gains nothing from it: do not request it. |
| `glance` | The `glance` host service: publishing L0 cards to the glance screen (`glance.publish`, `glance.withdraw`, `glance.list`). | Permission: "Show cards on your glance screen". Privacy: "Shows short cards on your glance screen; each opens only this app." | On App Hub `main` (#22) and in the shells' App Hub pin. The OctoSense service (`crates/shell/src/glance.rs`) serves any contained app granted `glance` ([OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)); `card-host` does not. See [AI-SERVICES](AI-SERVICES.md#publishing-to-the-glance-screen). |
| `model` | The `model` host service: one-shot model calls (`model.complete` with `{task, input, schema, class}`, `class` `fast` or `strong`); the host picks the model from the person's providers, checks the reply against the schema and keeps a daily budget. | Permission: "Send what you give it to the AI provider you configured, within a daily budget". Privacy: "Sends what you give it to the AI provider you configured, for one-off answers within a daily budget; it never sees your API keys." | On App Hub `main` (#24). The OctoSense shells serve it ([OctoSense#95](https://github.com/OctoSense-org/OctoSense/pull/95)); in `card-host` a call answers `no service answers "model" on this device`. See [AI-SERVICES](AI-SERVICES.md#one-shot-model-calls-model). |
| `prompt` | The app asking the person questions of its own. A service's sheet (Mail's sign-in, AI providers' key sheet) does not need it. | Permission: "Ask you questions". Privacy: "May ask you questions." | Resolves to `AppPolicy::may_prompt`, which no host reads, and there is no app-side prompt API (`host.prompt` does not exist), so **no current service uses it**; do not request it. An app's **agent** asks the person questions through the kernel's `ask_user_question` instead, declared in `agent.tools`, not here (the store shows the same words, "Ask you questions"; [AI-SERVICES](AI-SERVICES.md#what-an-apps-agent-gets-today)). Whether a service may raise its sheet is the surface's call, not this capability's: the app in the foreground may, a home-screen tile or an assistant's tool call may not (each request's `may_prompt`, [App Hub#38](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/38); the OctoSense shells set it false for glance tiles and tool calls since [OctoSense#204](https://github.com/OctoSense-org/OctoSense/pull/204), merged 2026-10-01). |
| `research` | Searching through the system toolbox for the app's **agent** (`toolbox.search`, `toolbox.web_read`, `workflow.run`, `workflow.fork`), within the manifest's top-level `research` scope (languages, regions, domains, recency, results per search). The host runs every search; the app never fetches the sites. | Permission: "Search …" with the scope in words. Privacy: "Searches …; the device runs each search, within these limits." | Added in App Hub #26. Needs the `research` object (`{}` means no limits) or the gate refuses: `requests research but declares no research scope` (**✓ run 2026-10-01**). The OctoSense shells grant it to system apps (`os.*`) only for now, where built with `toolbox-peers` ([AI-SERVICES](AI-SERVICES.md#the-system-toolbox)); a store app gains nothing yet. |
| `crawl` | Crawling a site through the system toolbox (`toolbox.deep_crawl`), up to the scope's `max_depth` and `max_pages`, inside its domain lists. More reach than `research`; neither implies the other. | Permission: "Crawl websites, …, which reaches more than searching". Privacy: "Crawls websites, …: this reaches more of the web than searching." | Same scope object and the same system-apps-only rule as `research`. |
| `ledger.read` | Reading the shared ledger through a `ledger` host service. | Permission: "Read your shared data". Privacy: "Reads your shared data." | Grants `ledger.read` only; `ledger.write` is a different name. **No shell registering a `ledger` service was found**; unverified. |
| `clipboard` | Clipboard access. | Permission: "Use the clipboard". Privacy: "Uses the clipboard." | **No script API gated by `clipboard` was found** in this runtime revision; unverified. |

Every `host.request("<family>.<method>")` needs the capability `<family>` (or
the exact service name). Refused calls answer at once with `r.is_ok` false and
`r.error` = `this app was not granted "<family>", which "<service>" needs`.

## Host services by exact name: `octos.*` and `matrix.*`

Besides the families above, `KNOWN_CAPABILITIES` holds 49 exact service names
(`crates/app-policy/src/services.rs`, since App Hub #14): four for the
device's assistant and 45 for the person's Matrix account. Each is its own
consent; a prefix (`octos.`, `matrix.`) or any other name is refused.

| Names | The person sees (store) | Who serves them today |
| --- | --- | --- |
| `octos.session.open`, `octos.session.history`, `octos.turn.start`, `octos.turn.interrupt` | "Open its own conversation with the assistant", "Read its own conversations with the assistant", "Ask the assistant to work for it, using the device's AI settings", "Stop assistant work it started"; privacy: "Asks the device's assistant to work for it; the assistant's keys stay with the device." | An OctoSense shell that hosts a kernel (not iOS) serves them once the person allows the app's agent at first use ([OctoSense#106](https://github.com/OctoSense-org/OctoSense/pull/106), [#184](https://github.com/OctoSense-org/OctoSense/pull/184)); until then a call answers `Waiting for the person to allow this app's agent (OctoSense asks the first time)`. `card-host` does not: a call answers `no service answers "octos" on this device`. Rinx's mini-app host serves them too. Details and a verified example: [AI-SERVICES](AI-SERVICES.md). |
| `matrix.*` (45 names, e.g. `matrix.profile`, `matrix.read_messages`, `matrix.send_message`) | One plain line per name, e.g. "Read messages in rooms you allow" | Only Rinx's mini-app host. |

## Other manifest requests

| Field | Meaning | Ceiling (installed / system) |
| --- | --- | --- |
| `storage.max_bytes` | Whole-jail quota | 16 MiB / 64 MiB |
| `compute.instruction_budget` | Script instructions per session, cumulative | 20 000 000 / 4 000 000 000 |
| `compute.memory_bytes` | Isolate heap | 64 MiB / 128 MiB |
| `agent` | The app's own agent: `profile` one of `read-only`, `workspace-write`, `workspace-write-never-ask`; `tools` from `ledger.read ledger.write net.fetch storage.read storage.write card.render` and the kernel's `ask_user_question` (no other kernel tool); iterations ≤ 8, tokens ≤ 200 000; `model` needs and tier, `background`, `triggers`, `instructions` (`AGENT.md`) and `skills`. The person sees "Runs an assistant limited to this app's own data…" (or "Runs no assistant."). The OctoSense shells give a declared agent its own peer once the person allows it, with `ask_user_question` and read tools over its account folder; they do not yet choose its model, fire its triggers, install `AGENT.md` or skills, or implement the generic host tools. See [AI-SERVICES](AI-SERVICES.md#an-apps-own-agent). | – |
| `storage.accounts` | `true`: data and one agent per account; default one `device` folder | – |
| `storage.agent_workspace` | `"account"` (default): the agent reads its account's folder; `"none"`: no files | – |
| `storage.cache_max_bytes` | Ceiling for the jail's `cache/` | – |
| `research` (top-level object) | The scope of `research` and `crawl`; required with either, refused without both | – |

Values above the ceiling are clamped, not refused; an absent value gets the
ceiling. The `grants:` line of `hub check` shows the result.

## Reserved and absent names

- **Reserved names** (`RESERVED_NAMES` in `crates/app-contract/src/manifest.rs`):
  no app id may be, or end in, `agents apphub appcard card dev octos os
  reference rinx sheets shell system terminal toolbox workflow`, because a
  host keys an app's folders, tools and consent by its id and its tools by
  the id's last segment. **✓ run 2026-10-01**: `[refused] identity: app id
  "dev.example.terminal" ends in "terminal", which is reserved: its tools
  would be terminal.*, a native app's or the host's`.
- **`os.*` ids** (not a capability, an id prefix) are reserved for system apps.
  The gate refuses them (`[refused] identity: <id> is under os., which is
  reserved for system apps that ship with the device`), no store installs one
  (`<id> names a system app, which no store may install`), and
  `card-host --system` runs one under system ceilings for development.
- **`profile`** and **`agent`** appear as runtime gates for profile-backed
  `sys.*` helpers and `agent.notify`, but are **not** in `KNOWN_CAPABILITIES`:
  no store app can hold them.
- **Adding a capability** is an App Hub change (the list, the privacy line,
  and the service or runtime path that enforces it, together). An app cannot
  invent one.
