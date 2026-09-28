# Using octos AI in an OctoScript app

How an OctoSense app gets AI: which paths exist today, which are still being
built, and what an app declares for each. octos is the agent kernel inside
OctoSense; an app never talks to it directly.

Every API, method, manifest field and command below was read in source (the
file is named with each). Each feature is marked:

- **available**: merged on `main` of the repository named, and usable as
  described;
- **coming**: in an open pull request (named) or only in an ADR; the shape
  shown is what that pull request or ADR says, and it may change before it
  lands. Do not build a submission on it yet.

Commands marked **✓ run** were run for this guide on 2026-09-27 (macOS, Apple
silicon). The others are quoted from the named source and were not re-run
here.

## Status at a glance (2026-09-27)

| Feature | Status | Where |
| --- | --- | --- |
| Apps reach AI only through host services and the app-peer broker, never the kernel | **available** (rule) | OctoSense [`AGENTS.md`](https://github.com/OctoSense-org/OctoSense/blob/main/AGENTS.md) rules 3 and 4, [`crates/app-peers`](https://github.com/OctoSense-org/OctoSense/tree/main/crates/app-peers) |
| `llm` host service: the person's AI providers, masked keys, host sheets | **available**, system apps (`os.*`) only | OctoSense [`apps/ai-providers`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/ai-providers) |
| `model.complete`: a direct, one-shot, schema-checked model call from a script app (not a chat; no tools) | **coming**: the service is in [OctoSense#95](https://github.com/OctoSense-org/OctoSense/pull/95) (draft); the `model` capability is in App Hub ([#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24)) but not yet in the shells' App Hub pin ([OctoSense#70](https://github.com/OctoSense-org/OctoSense/pull/70)) | [§2](#2-direct-model-calls-model-coming-and-llm) |
| `octos.*` assistant services (open a conversation, start a turn) | **available** to native modules only (the shipped policy grants Rinx); no path for script apps | OctoSense `crates/app-peers`, `crates/ai-host/src/lib.rs` `Policy::shipped` |
| An app's own agent declared in its bundle: `agent` (model needs, triggers, skills), `tools.json`, `AGENT.md`, `skills/` | **available** in the App Hub gate ([OctoSense-App-Hub#18](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/18)); **coming** in the shells (they pin an App Hub before #18; [OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86) moves the pin); nothing runs the agent yet (ADR 0002 M2, M3) | App Hub `crates/app-policy/src/{manifest,agent,policy}.rs` |
| App tools registered with the app's peer (`peer/tools/register`, `peer/tool/call`) | **coming**: [octos-org/octos#2567](https://github.com/octos-org/octos/pull/2567), draft, changes requested | octos UPCR-2026-035 |
| In-app conversation with the app's agent; approvals; app memory | **coming**: ADR 0002 §9–10 (milestone M7); only the approval rules are in the gate today | OctoSense ADR 0002 |
| System toolbox: workflow templates, `workflow.run`, `workflow.fork`, `research` module | **coming**: [OctoSense#82](https://github.com/OctoSense-org/OctoSense/pull/82), draft; the `research` capability is not in App Hub yet; `crawl` is not implemented | OctoSense `crates/toolbox` (#82) |
| `news` host service (a data service, no model) | **available**, system apps only; News uses it once the shells' App Hub pin knows the `news` capability (#86) | OctoSense [`apps/news/host-service`](https://github.com/OctoSense-org/OctoSense/tree/main/apps/news/host-service) |
| `glance.publish`, `glance.withdraw`, `glance.list` (the service) | **available** ([OctoSense#72](https://github.com/OctoSense-org/OctoSense/pull/72)) | OctoSense `crates/shell/src/glance.rs` |
| The `glance` capability | **available** in App Hub ([#22](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/22)); **coming** in the shells ([OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)). Until then no contained app can publish ([§6](#6-publishing-results-the-glance-screen)) | App Hub `KNOWN_CAPABILITIES`; OctoSense `glance.rs` |
| `sys.digest(app:, id:, fields:)` L0 source | **coming**: [OctoScript#40](https://github.com/OctoSense-org/OctoScript/pull/40), [OctoScript-Makepad#50](https://github.com/OctoSense-org/OctoScript-Makepad/pull/50), [OctoSense#87](https://github.com/OctoSense-org/OctoSense/pull/87) | OctoScript `docs/ui-profile-l0.md` §5.14 (#40) |
| Render and critique a card: `card-studio`, `card-host --remote` | **available** (App Hub `main`) | App Hub [`docs/DEVELOPMENT.md`](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/DEVELOPMENT.md) |

In one line: today a store app can **declare** an agent that passes the gate,
but nothing in a shell runs it, calls its tools or lets it publish; the pieces
that do are the open pull requests above.

## Contents

1. [The model: apps never talk to the kernel](#1-the-model-apps-never-talk-to-the-kernel)
2. [Direct model calls: `model` (coming) and `llm`](#2-direct-model-calls-model-coming-and-llm)
3. [An app's own agent](#3-an-apps-own-agent)
4. [App tools for the agent: host-registered peer tools](#4-app-tools-for-the-agent-host-registered-peer-tools)
5. [The system toolbox: research and workflow templates](#5-the-system-toolbox-research-and-workflow-templates)
6. [Publishing results: the glance screen](#6-publishing-results-the-glance-screen)
7. [Card levels and the render-and-critique loop](#7-card-levels-and-the-render-and-critique-loop)
8. [Capabilities an AI app declares](#8-capabilities-an-ai-app-declares)
9. [End to end: News](#9-end-to-end-news)
10. [Testing without a real provider](#10-testing-without-a-real-provider)

## 1. The model: apps never talk to the kernel

**available** (the rules); the event-driven agent design is ADR 0002 (status
Proposed).

- **One kernel per shell.** The shell starts one octos kernel on the first
  consumer and shares it; "consumers never spawn their own. Apps reach the
  assistant only through `crates/app-peers`, never through the raw kernel
  protocol" (OctoSense `AGENTS.md`, rule 4).
- **Secrets are the host's.** "No script app collects a password, PIN, key or
  one-time code … Apps see masked status, never the secret" (rule 3). An AI
  provider's key is typed only on the `llm` service's sheet.
- **App peers.** For each app whose declared `octos.*` services host policy
  grants, the shell's system agent session (`_main:api:octosense#system`) owns
  ONE octos peer, with its own workspace, history and memory namespace
  `app/<app>/acct-<hash>`. The app gets a scoped service handle; it "never
  sees raw kernel protocol, provider settings or credentials, and it never
  starts a kernel" (`crates/app-peers/README.md`).
- **System apps are contained script apps** (Home ADR 0004): News, Mail, AI
  providers and the rest are ordinary bundles in their own isolate under their
  manifest's policy. Privileged work (a socket to a mail server, a provider
  key, a device) is a **host service** the app calls with `host.request`.
- **Today a contained script app cannot reach its peer at all** (ADR 0002,
  Context). App peers are opened only by a running native module, and the
  shipped policy grants the `octos.*` services to one module, Rinx
  (`Policy::shipped()` in `crates/ai-host/src/lib.rs`).

What ADR 0002 decides for AI in apps (its sections 1–13), in brief:

| § | Decision |
| --- | --- |
| 1 | Each app that asks gets its own agent (its app peer); the system agent supervises and never writes app agents' prompts. |
| 2 | Triggers belong to the app: a schedule, a data event from its host service, or the person in the app. |
| 3 | The app ships its agent: `AGENT.md`, skills, and model **requirements**; the host picks the model from the person's providers. |
| 4 | The app exposes typed tools (`tools.json`) with a risk level and a confirmation owner; the host registers them with the app's peer. |
| 5 | Collection is code (a data service, no model); judgement is the model's. |
| 6 | Searching, research and crawling are a system toolbox the host runs, granted per app with a scope. |
| 7 | Cards are L0, bound to host-resolved sources, rendered and critiqued before `glance.publish`. |
| 8 | The glance screen is curated by the system agent. |
| 9 | Memory is private to the app unless a rule or the person promotes it. |
| 10 | The person talks to the app's agent inside the app; approvals happen there. |
| 11 | The system agent tunes app agents with a versioned overlay; it never edits the pinned `AGENT.md`. |
| 12 | Script apps and native modules follow one model; only where rules are enforced differs. |
| 13 | Least privilege: tools, network, files, memory, secrets, risk, model, budgets, output, control. |

Sources: OctoSense [`docs/adr/0002-event-driven-app-agents.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/0002-event-driven-app-agents.md),
[`docs/adr/home/0004-system-apps-are-contained-script-apps.md`](https://github.com/OctoSense-org/OctoSense/blob/main/docs/adr/home/0004-system-apps-are-contained-script-apps.md),
[`crates/app-peers/README.md`](https://github.com/OctoSense-org/OctoSense/blob/main/crates/app-peers/README.md).

## 2. Direct model calls: `model` (coming) and `llm`

**Today there is no host method that runs a model for an app.** A script app
gets model output only through an agent (sections 3–5), which is **coming**.

### `model.complete` (**coming**)

OctoSense ADR 0002 §14 (added in [OctoSense#95](https://github.com/OctoSense-org/OctoSense/pull/95),
draft) adds a narrow, direct, **one-shot** call for bounded jobs: title this
note, classify this item, pull these fields out of this text. An app's agent
stays the main path for anything with tools, research, memory or approvals.
The call needs the `model` capability, which App Hub admits
([OctoSense-App-Hub#24](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/24),
merged). The shells get it only when their App Hub pin moves
([OctoSense#70](https://github.com/OctoSense-org/OctoSense/pull/70)). Until
then no shell grants it, and the service itself is not merged. The shape
below is #95's and may change: do not ship a submission that depends on it
yet.

```splash
host.request("model.complete", {
    task: "Give the note a short title and up to three tags."
    input: {note: note_text}
    schema: {type: "object" required: ["title" "tags"] additionalProperties: false
             properties: {title: {type: "string" maxLength: 40}
                          tags: {type: "array" maxItems: 3 items: {type: "string"}}}}
    class: "fast"
}, fn(r){
    if !r.is_ok { status(r.error) return }   // "budget: …", "no_provider: …"
    show_title(r.data.output.title)
})
```

This call was not run for this guide, because no shell serves `model` yet.
The literal syntax follows the Photos bundle (space-separated lists and maps);
the fields come from #95's service and its tests (a fake provider, and a live
DeepSeek check).

- **You name a class, not a model:** `"fast"` (default) or `"strong"`. The
  host picks from the person's providers in their own order and never tells
  the app the provider, the model id or the key. `r.data.meta.class` says
  which class answered.
- **One shot:** no tools, memory, browsing or history. The model sees the
  host's instructions, your `task`, your `schema` and your `input`, nothing
  else.
- **`schema` is required** (a bounded JSON Schema subset, at most 8 KiB).
  `r.data.output` always validates against it. A bad reply is retried once,
  then comes back as an error.
- **No URLs by default.** A reply with `http://`, `https://` or `www.` in any
  string is refused, because output ends up in card data. Pass
  `allow_urls: true` only if you extract links.
- **A daily budget per app:** by default 6 calls a minute, and 100 calls and
  100,000 tokens a day. `r.data.meta.budget` and `model.budget` show what is
  left.
- **Errors are `"<code>: <sentence>"`**, with `code` one of `capability`,
  `no_provider`, `rate`, `budget`, `bad_request`, `invalid_output`,
  `too_large` or `provider`. Show the sentence, and keep the app usable
  without the model.
- **Privacy:** the store tells the person: "Sends what you give it to the AI
  provider you configured, for one-off answers within a daily budget; it
  never sees your API keys."

### `llm` (**available**, system apps only)

No `llm.complete`, `llm.chat` or similar exists in the `llm` service.

What `llm` is (**available**, system apps only): the AI providers system app's
service for the person's provider list. Source:
`apps/ai-providers/host-service/src/lib.rs` in OctoSense (crate
`octosense-llm-service`, linked by `crates/ai-host` with its `llm` feature).

- **Who may call.** "Only `os.` apps are served"; any other caller gets
  `llm is for OctoSense's own apps.`, even when its manifest holds `llm`. A
  store app gains nothing from requesting it; the store would still show the
  person "Manage the assistant's AI providers, whose keys stay with the
  device".
- **Methods** (`host.request("llm.<method>", …)`):

  | Method | Args | Answer (`r.data`) |
  | --- | --- | --- |
  | `llm.providers` | – | `{primary, fallbacks, scanner, image_picker, store}`; each provider `{id, family, label, model, model_label, custom_model, route, route_label, context, price, tier, base_url, api_type, key}`, `key` being `"set ••••1234"`, `"missing"`, `"not needed"` or `"keychain locked"` |
  | `llm.families` | `{query?}` | the catalog families with their models |
  | `llm.models` | `{family, query?}` | one family's catalog models and routes |
  | `llm.add_provider`, `llm.edit_provider` | –, `{id}` | `{id, label}` once the person saves on the host's sheet |
  | `llm.set_model` | `{id, model}` | `{id}` |
  | `llm.move` | `{id, to}` | `{}`; `to` 0 is the primary |
  | `llm.set_primary`, `llm.remove` | `{id}` | `{}` |
  | `llm.test` | `{id}` | `{ok, ms, error?}` after one tiny request |
  | `llm.export_qr`, `llm.import_qr` | `{ids?}`, – | a QR shown or scanned on the host's sheet |
  | `llm.sheet.*` | – | the sheet's own calls; refused from an app |

- **How the person's provider is chosen.** The list is the kernel's profile,
  `<core_dir>/profiles/_main.json`, `config.llm`: the first entry is the
  **primary**, the rest are **fallbacks in order** (`llm.move`,
  `llm.set_primary`). Every change restarts the shell's kernel, which reads
  the profile at start. An app never names a provider or a model.
- **Secrets stay on host sheets.** Keys are typed, shown as a QR or scanned
  only on the service's sheets (`llm.sheet.submit`, `llm.sheet.import`, …),
  which "`dispatch` refuses … from anyone else". They are kept in the
  Keychain on macOS, an owner-only `secrets/` file on Linux, or the owner-only
  profile (`vault.rs`). The app sees only the masked `key` status.

The calling convention, as the AI providers app uses it
(`apps/ai-providers/bundle/main.splash`, `load()`):

```splash
host.request("llm.providers", {}, fn(r){
    if !r.is_ok { status(r.error) return }
    let list = []
    if r.data.primary != nil { list.push(r.data.primary) }
    for f in r.data.fallbacks { list.push(f) }
    // …
})
```

The same shape serves every host service: `r.is_ok`, `r.data`, `r.error`;
map literals have no commas (`{id: p.id to: 0}`); `host.has("<family>")`
tells whether the family is granted ([SCRIPT-API](SCRIPT-API.md#host-services-hostrequest),
[HOST-SERVICES](HOST-SERVICES.md)).

## 3. An app's own agent

**available** in the App Hub gate since
[OctoSense-App-Hub#18](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/18)
(merged 2026-09-27); **coming** everywhere else: OctoSense's shells pin an App
Hub revision from before #18, so their Card runner refuses these manifest
fields as unknown until the pin moves (OctoSense#86 moves it), and no shell
code installs `AGENT.md` or skills into a peer, selects a model or fires a
trigger yet (ADR 0002 Implementation, step 2).

The contract is App Hub's
[PUBLISHING § The app's agent and tools](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-apps-agent-and-tools);
the complete worked example is App Hub's
[`crates/app-policy/tests/fixtures/news-agent`](https://github.com/OctoSense-org/OctoSense-App-Hub/tree/main/crates/app-policy/tests/fixtures/news-agent).

### The bundle

```text
bundle/
  manifest.json      "agent": { … } (below)
  tools.json         the app's own tools (section 4)
  AGENT.md           named by agent.instructions
  skills/<name>/     SKILL.md + manifest.json, each named in agent.skills
  main.splash, listing.json, assets/, screenshots/  as for any app
```

Every file is under the bundle digest, so the agent that runs is the one that
was reviewed. Agent files without an `agent` in the manifest, and undeclared
`AGENT.md` or skill directories, are refused (`crates/app-policy/src/agent.rs`).

### The manifest's `agent`

A store app's agent that passes the gate (**✓ run**, `hub check` from App Hub
`main` `362d832`, in a copy of the template made with `tools/octo new --id dev.example.brief`):

```json
"capabilities": ["storage", "glance"],
"agent": {
  "profile": "read-only",
  "tools": [],
  "max_iterations": 6,
  "token_budget": 60000,
  "model": {
    "needs": ["tool_calling", "multilingual"],
    "tier": "standard",
    "local_only": false,
    "per_task": { "summary": { "needs": ["tool_calling", "reasoning"], "tier": "strong" } }
  },
  "background": true,
  "triggers": { "schedule": ["30 7 * * *"] },
  "instructions": "AGENT.md",
  "skills": ["morning-brief"]
}
```

```text
$ hub check <bundle> --allow-unsigned
  grants: capabilities {"glance", "storage"}, hosts {}, storage 16777216 bytes, agent read-only
```

(The only refusal was the template's missing screenshot, which a real capture
fixes.)

| Field | Rule (App Hub `manifest.rs`, `policy.rs`) | Enforced today |
| --- | --- | --- |
| `profile` | `read-only`, `workspace-write` or `workspace-write-never-ask`; there is no full access | gate |
| `tools` | generic host tools only: `ledger.read ledger.write net.fetch storage.read storage.write card.render`; anything else is refused | gate |
| `max_iterations`, `token_budget` | clamped to 8 and 200 000 | gate (`grants:` line) |
| `model.needs` | from `tool_calling vision long_context reasoning structured_output multilingual` | gate; the gate warns when an app has tools but no `tool_calling` |
| `model.tier` | `fast`, `standard` (default) or `strong` | gate |
| `model.local_only` | app-wide; data must not leave the person's devices | gate (shareable tools must say `private_data: false`) |
| `model.per_task` | named tasks `[a-z_]{1,32}`, at most 8, that `AGENT.md` refers to | gate |
| no provider or model name | an unknown key is refused: `hub: manifest is not valid: unknown field \`provider\`, expected one of \`needs\`, \`tier\`, \`local_only\`, \`per_task\`` (**✓ run**) | gate |
| `background` | a request to run while the app is closed; the person grants it per app; requires `triggers` | gate; the grant and the wake are **coming** |
| `triggers.schedule` | five-field cron, local time, at most 16 triggers | gate; firing is **coming** (ADR 0002 M3) |
| `triggers.events` | the app's own host-service events, in its namespace (`news.items.new`) | gate; delivery is **coming** (M3). A store app has no host service, so it has no events to name |
| `instructions`, `skills` | `AGENT.md` (text, 32 KB, no HTML scripts, no `#!`); skill names `[a-z0-9_-]{1,64}`, at most 16 | gate |

**The host picks the model**, from the person's providers, to meet `needs`
and `tier` (ADR 0002 §3, octos `peer/model/set`); policy may lower the tier
or force local models; the person may override per app. That selection is
**coming** (ADR 0002 step 2). How ties are broken is an open question in the
ADR.

### `AGENT.md` and skills

`AGENT.md` is the agent's role: what to do on each trigger, what matters in
the app's data, the rubric its output must meet, and its memory rules. A
skill is data only: `skills/<name>/SKILL.md` plus a `manifest.json` with
`name` (the directory), `version`, `description`, `uses` (each one of the
app's tools or in `agent.tools`) and optionally `prompts.include`; `.md`,
`.json` and `.txt` files only; executable fields (`tools`, `binaries`,
`mcp_servers`, `hooks`, …) are refused.

```json
{
  "name": "morning-brief",
  "version": "1.0.0",
  "description": "Write the short morning note from the followed topics.",
  "uses": ["brief.topics.get", "brief.note.save"]
}
```

### Approvals: `risk` and `confirm`

Declared per tool in `tools.json` (section 4). Whether a call needs the
person comes from `risk`; whose surface asks comes from `confirm`
(App Hub PUBLISHING):

| `risk` | Runs |
| --- | --- |
| `read` (looks), `act` (changes the app's own state) | unattended |
| `destructive` (sends, posts, shares, buys, deletes) | only after the person approves |

| `risk: "destructive"` with | Person present | Person absent |
| --- | --- | --- |
| `confirm: "host"` (default) | the host's approval path asks | an approval request in the app's conversation |
| `confirm: "app"` | the app's own confirmation sheet is the only confirmation | an approval request in the app's conversation |

`confirm: "app"` is allowed only for a tool with `implemented_by: "app"` (or a
native module's tool). The gate warns on every destructive tool; making the
example's `brief.note.save` destructive gives (**✓ run**):

```text
  [warning] tools: brief.note.save is destructive and marked background: in a background run it only becomes an approval request, and runs after the person approves
  [warning] agent: a background agent with destructive tools: each destructive call waits as an approval request until the person answers
  [warning] tools: brief.note.save is destructive: every call waits for the host's approval
```

The store shows the person one line per consequence, derived from the
manifest and `tools.json`, for example "Its assistant may work while the app
is closed, on a schedule; only if you allow it, and you can turn it off." and
"Can ask to mail.send: nothing of this runs until you approve it."

**What is enforced where, today:**

| Part | Status |
| --- | --- |
| Declarations (fields, sizes, names, schemas, risk, confirm) | **available**: the App Hub gate refuses or warns |
| The approval gate at run time (kernel), approve, edit or decline in the app's conversation | **coming**: octos#2567 (kernel side), ADR 0002 §10 / M7 (the shell's conversation) |
| In-app conversation with the app's agent | **coming**: ADR 0002 §10, M7; no pull request yet |
| Memory in `app/<app>/…`, promotion by rule | **coming**: ADR 0002 §9, M7. There is no manifest field; memory rules are prose in `AGENT.md` |
| Overlays by the system agent | **coming**: ADR 0002 §11, M8 |

## 4. App tools for the agent: host-registered peer tools

**coming**: [octos-org/octos#2567](https://github.com/octos-org/octos/pull/2567)
("host-registered tools per app peer with tool-list and risk enforcement",
UPCR-2026-035), draft, **changes requested** by the reviewer (the open point
is whether credential binding, octos #2556, must land first). The OctoSense
side (the shell registering an app's `tools.json` for its peer) has no pull
request yet.

What the app writes is **available** now: `tools.json` in the bundle, checked
by the App Hub gate (`crates/app-policy/src/agent.rs`):

```json
{
  "schema": 1,
  "tools": [
    {
      "name": "brief.note.save",
      "description": "Save the morning note the app shows on its first screen.",
      "input_schema": {
        "type": "object",
        "properties": { "text": { "type": "string", "maxLength": 600 } },
        "required": ["text"],
        "additionalProperties": false
      },
      "output_schema": { "type": "object", "properties": { "saved": { "type": "boolean" } } },
      "risk": "act",
      "background": true,
      "implemented_by": "app"
    }
  ]
}
```

- `name` is `<namespace>.<tool>`; the namespace is the **last segment of the
  app id** (`dev.example.brief` → `brief`, `os.news` → `news`).
- Schemas use a JSON Schema subset (`type title description properties
  required items enum const default minimum maximum minLength maxLength
  minItems maxItems additionalProperties format pattern`); the input is an
  object. At most 64 tools, 1024-character descriptions.
- `implemented_by`: `host-service` (native code that holds data, network or
  secrets) or `app` (the app's script, for tools that only reshape its own
  data). How a call reaches a script app's own implementation is not
  specified yet.
- `background`, `shareable`, `private_data`, `confirm`: see section 3.

How the shell will register them, per #2567 (not merged; names may change):

| Method | Direction | Shape |
| --- | --- | --- |
| `peer/tools/register` | host → kernel | `{session_id, peer, host_token, tools: [{name, description, input_schema, output_schema?, risk, background?, outward?, confirm?, shareable?}], generic_tools?, if_version?, call_timeout_ms?, approval_ttl_secs?, max_result_bytes?}` → `{…, version, tools: [{name, model_name, risk, background, outward, confirm}], applies: "next_turn"}`. The whole set replaces the previous one. |
| `peer/tool/call` | kernel → host | `{peer, session_id, context_id, turn_id, call_id, tool_call_id, args_digest, name, args, risk, confirm_required, timeout_ms, tools_version}` |
| `peer/tool/result` | host → kernel | `{session_id, peer, host_token, call_id, ok?, data?, error?, status?: "awaiting_confirmation"}` |
| `peer/tool/cancel` | kernel → host | `{call_id, reason: timeout \| cancelled}` |

The model sees `news.list` as `news_list`. Defaults: 30 s per call, results
at most 256 KiB, approvals expire after an hour. A gated call (destructive,
or outward) with `confirm: host` waits for a kernel approval; with
`confirm: app` and the person present it goes to the host with
`confirm_required: true`. The app never calls these methods: the shell
(`crates/ai-host`) does, for the app's peer (ADR 0002 §12).

## 5. The system toolbox: research and workflow templates

**coming**: [OctoSense#82](https://github.com/OctoSense-org/OctoSense/pull/82)
(draft, `crates/toolbox`, crate `octosense-toolbox`). "The shells do not link
it yet." The App Hub `research` and `crawl` capabilities do not exist yet
(the gate refuses them: `policy: app dev.example.brief requests unknown
capability "research"`, **✓ run**), and `crawl` / `deep_crawl` is not
implemented.

An app's agent never searches, crawls or drives a browser itself. It is
granted toolbox tools, and the host runs them outside the app, under the
app's scope and budget (ADR 0002 §6).

### Templates

Fixed, bounded OctoScript procedures with a manifest (parameters, the host
modules they call, a budget and an output schema), from #82's
`templates/*/template.json`:

| Template | Required params | Optional (default) | Budget: calls / model calls / pages |
| --- | --- | --- | --- |
| `news-digest` | `topic`, `language` | `search_language` ("en"), `translate_query` (false), `limit` (3, 1–5), `max_age_hours` (72) | 8 / 2 / 7 |
| `topic-brief` | `topic`, `language`, `languages` (1–4 of `{language, translate}`) | `per_language` (3), `read_top` (4), `max_age_hours` (72) | 20 / 5 / 10 |
| `market-brief` | `symbols` (1–3 of `{symbol, name}`), `language` | `search_language`, `per_symbol` (2), `max_age_hours` (72) | 13 / 1 / 12 |
| `weather-plan` | `location`, `language` | `activity`, `days` (3), `search_language`, `limit` (2), `max_age_hours` (48) | 7 / 1 / 6 |
| `briefing` | `topics` (1–4), `language` | `search_language`, `per_topic` (2), `max_age_hours` (24) | 17 / 1 / 16 |
| `compare` | `subjects` (exactly 2), `aspect`, `language` | `search_language`, `per_subject` (2), `max_age_hours` (72) | 9 / 1 / 8 |

No template may exceed 64 calls, 8 model calls, 32 pages or 300 s; a run's
budget is further narrowed by the app's budget and its scope's `max_pages`.

### The tools

Per #82's `src/api.rs`, a call is tagged by tool name:

```json
{ "tool": "workflow.run",
  "arguments": { "id": "news-digest",
                 "params": { "topic": "electric cars", "language": "en" },
                 "run_id": "glance" } }
```

| Tool | Arguments | Answer |
| --- | --- | --- |
| `workflow.list` | – | `{templates, refused?}` (the library plus the app's forks) |
| `workflow.run` | `{id, params, run_id?}` (`run_id` `[A-Za-z0-9_-]{1,64}`) | `{run_id, app_id, template: {id, version, digest}, status: ready \| partial \| failed, data, provenance, diagnostics, stats, trace, started_at, result_path?}` |
| `workflow.fork` | `{id, new_id?}` | `{template, path: "toolbox/templates/<id>"}`; the fork records its parent and may not add modules, raise a budget or turn provenance off |
| `workflow.evaluate` | `{a, b, cases}` (1–32 cases) | a comparison of two templates on the same inputs |

Errors are `{"error": {kind, message}}`, `kind` one of `manifest check
widening pin not_found not_granted params runtime io`. The agent reaches
these as peer tools (section 4), not through `host.request`.

### Scope, budgets, provenance

- **Scope** (`host.rs`): `languages, regions, allowed_domains,
  denied_domains, max_depth, max_pages, recency_hours`; the host refuses a
  call outside it. (`max_depth` is declared but unused in #82.)
- **The `research` module**: `query`, `search` (structured items), `article`
  (only ids found in this run; one page each; the text is hashed as
  evidence) and `digest` (a summary of at most 1200 characters and up to 12
  cited points).
- **Provenance is the host's**, never the model's: each source carries `id,
  url, title, source, language, published_at, retrieved_at, evidence_sha256,
  via`. A URL in the output that the host did not retrieve fails the run.
- **Results** are written to `<app folder>/toolbox/runs/<template>/<run_id>.json`.

## 6. Publishing results: the glance screen

### `glance.publish`, `glance.withdraw`, `glance.list`

The service is **available** on OctoSense `main`
([#72](https://github.com/OctoSense-org/OctoSense/pull/72),
`crates/shell/src/glance.rs`):

| Method | Args | Answer |
| --- | --- | --- |
| `glance.publish` | `{card_id, source, data?, title, priority?, expires?, open?: {app, route?}}` | `{card_id, replaced, expires_at}` |
| `glance.withdraw` | `{card_id}` | `{withdrawn}` |
| `glance.list` | – | `[{card_id, title, priority, published_at, expires_at}]`, the caller's own cards only |

- `source` is an **L0 card** (L1 if its header declares it; L2 refused),
  realized against `data` (a map from the card's source names to values) and
  lowered through the Card runner's pipeline before it is stored.
- **Limits:** `card_id` 1–64 of `[A-Za-z0-9._-]`; `title` at most 80
  characters; `source` at most 16 KiB; `data` at most 32 KiB as JSON;
  `priority` 0–100 (default 50); `expires` 60 s to 7 days (default 24 h); 6
  publishes per minute per app (a replace, and a card the L0 check refuses,
  both count); 4 cards per app; 32 in the store; 6 shown.
- **Identity:** the publisher is the caller, never an argument; publishing
  the same `card_id` replaces the card; `open.app` must be the caller's own
  app. A tap opens that app. `open.route` is stored but not used yet.
- A tile runs in its own isolate with no capabilities and no hosts.

### Who may publish

- **On OctoSense `main` today: no contained app can.** The service code admits
  only `os.*` contained callers, but the isolate refuses `glance.*` for any
  app whose manifest does not grant `glance`, and the App Hub revision the
  shells pin has no `glance` capability to grant. Only native modules (and
  the shell's demo, `OCTOSENSE_GLANCE_DEMO=1`) publish.
- **With [OctoSense#86](https://github.com/OctoSense-org/OctoSense/pull/86)
  (coming):** the shells pin App Hub with `glance` (merged there as
  [#22](https://github.com/OctoSense-org/OctoSense-App-Hub/pull/22)), and any
  contained app **granted `glance`** may publish, list and withdraw its own
  cards; system apps get no exemption. Refusal:
  `<app> was not granted the glance capability`.

Once #86 lands, a call from an app looks like this (the shape is `glance.rs`'s;
not run, since `card-host` registers no host services):

```splash
host.request("glance.publish", {
    card_id: "morning"
    title: "Morning brief"
    source: card_source
    data: {}
    expires: 43200
}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) }
})
```

### `sys.digest`: a card bound to what the agent found

**coming**: [OctoScript#40](https://github.com/OctoSense-org/OctoScript/pull/40)
(the L0 source), [OctoScript-Makepad#50](https://github.com/OctoSense-org/OctoScript-Makepad/pull/50)
(repin), [OctoSense#87](https://github.com/OctoSense-org/OctoSense/pull/87)
(the shell resolves it, `crates/shell/src/glance_digest.rs`).

L0's no-facts rule forbids a card from stating findings as its own text, so
the findings become a source the host resolves:

```text
source brief sys.digest(app: "os.news", id: "glance",
                        fields: [topic, summary, points, sources, id, text, cite, n, title, source])
```

- `app` is a literal and must be the publishing app; the host refuses a card
  naming another. `id` is a literal (`[A-Za-z0-9_-]{1,64}`, the toolbox's
  run-id charset) or a path into state.
- The record: `status` (`ready partial failed missing expired`), `topic`,
  `language`, `summary`, `retrieved_at`, `count`, `points` (`{id, text, label,
  cite, citations}`) and `sources` (`{id, n, title, source, url,
  published_at}`).
- **Links come only from `sources`**, which the host retrieved; text with a
  URL is dropped. A missing, expired or malformed digest resolves to an empty
  record with `$state` `.failed`, never an error, so the card shows its own
  "nothing yet" copy.
- In #87 the host reads the newest `toolbox/runs/<template>/<id>.json` for the
  app (under the host's directory, outside the app's jail), keeps only
  sources in the run's host-kept provenance, caps text (summary 800, 8 points
  of 400, 8 sources) and expires a digest 48 h after its run started; the
  card's expiry is at most the digest's.

The worked example is #87's `crates/shell/resources/glance/news-brief.card`:

```text
# ledger news.brief@1.0.0
# level:   L0
# profile: ui/l0

source brief sys.digest(app: "os.news", id: "glance",
                        fields: [topic, summary, points, sources,
                                 id, text, cite, n, title, source])

copy label   { class: vocabulary, en: "NEWS DIGEST", zh: "新闻摘要" }
copy nothing { class: vocabulary, en: "No digest yet. News will brief you after its next read.", zh: "暂无摘要。新闻读完下一批后会为你汇总。" }
copy sources { class: vocabulary, en: "SOURCES", zh: "来源" }

view root  Surface(pad: .page) {
             Col(gap: 6) {
               Row(gap: 8) {
                 TextCaption(text: copy.label, width: .fill)
                 TextCaption(text: brief.topic)
               }
               when brief.$state == .failed { TextBody(text: copy.nothing, width: .fill) }
               when brief.$state == .ready {
                 Col(gap: 6) {
                   TextBody(text: brief.summary, width: .fill)
                   for p in brief.points key p.id {
                     Row(gap: 8) {
                       TextRow(text: p.text, width: .fill)
                       TextCaption(text: p.cite)
                     }
                   }
                   TextCaption(text: copy.sources)
                   for s in brief.sources key s.id {
                     Row(gap: 8) {
                       TextCaption(text: s.n)
                       TextCaption(text: s.source)
                       TextCaption(text: s.title, width: .fill)
                     }
                   }
                 }
               }
             }
           }
```

(Its header comment is shortened here.) Until OctoScript#40 lands, the L0
checker does not know `sys.digest`, so a card using it is refused.

## 7. Card levels and the render-and-critique loop

The levels are defined in OctoScript's
[`docs/ui-profile-l0.md`](https://github.com/OctoSense-org/OctoScript/blob/main/docs/ui-profile-l0.md):

| Level | What it admits | For AI output |
| --- | --- | --- |
| **L0** | UI declarations only: data from catalogued `sys.*` sources the host resolves, no expressions, no calls | the default for generated and glance cards |
| **L1** | L0 plus arithmetic expressions, declared with a `# level: L1` header | only where arithmetic is needed |
| **L2** | imperative Splash (`ui.<id>.set_*`) | refused for generated cards; this is what a script app's `main.splash` is |

L0 card examples in this repository: [docs/l0/](l0/).

**Render and critique** (**available**, App Hub `main`, `crates/card-studio`;
the octos skill `skills/card-studio`, tools `card_render` and
`card_critique_payload`): render a card in a hidden `card-host --remote` at
the target sizes, run the measured checks (truncated text, does not fit,
failed source, lint, lowering), then build a vision-critique request against
a rubric. From App Hub's
[DEVELOPMENT.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/DEVELOPMENT.md#inspecting-a-card-before-publishing-card-studio):

```sh
cargo build --release -p octosense-card-host -p octosense-card-studio
export CARD_STUDIO_KIT=../octoscript-makepad/components/l0
target/release/card-studio render --card news.card --data digest.json \
    --size glance --size phone --size desktop --out out/
target/release/card-studio critique --report out/report.json --rubric AGENT-rubric.md --inline > request.json
```

By hand, the same instrument: `card-host … --remote` (or
`MAKEPAD_REMOTE=<port>`), then `/snap` for widget text and rectangles, `/g`
for a frame grab (`/g?raw=1` for the PNG bytes), `/d` for the tree, `/log`,
and `/quit`. `tools/octo run --hidden` and `tools/octo shot` wrap this for a
bundle (README, [Headless testing](../README.md#headless-testing-many-apps-no-screen)).

Running the loop from an app's agent (ADR 0002 M6) is **coming**.

## 8. Capabilities an AI app declares

The list is closed (`KNOWN_CAPABILITIES`, App Hub
`crates/app-policy/src/manifest.rs`, `main`). Ask for the least the app
needs; each line below is what the store shows the person before install.

| Capability | For | Store line | Status |
| --- | --- | --- | --- |
| `glance` | `glance.publish`, `withdraw`, `list` for the app's own cards | "Show cards on your glance screen" | App Hub: **available**; shells: **coming** (#86) |
| `news` | the `news` host service (collected stories) | "Read news the device collects from its feeds and topics" | App Hub: **available**; the service answers `os.*` only |
| `model` | `model.complete`: one-shot, schema-checked calls to the person's AI provider, within a daily budget | "Send what you give it to the AI provider you configured, within a daily budget" | App Hub: **available** (#24); shells: **coming** (OctoSense#70, #95) |
| `llm` | managing the person's AI providers | "Manage the assistant's AI providers, whose keys stay with the device" | `os.*` only; do not request it in a store app |
| `octos.session.open`, `octos.session.history`, `octos.turn.start`, `octos.turn.interrupt` | the app's own conversation and turns with the assistant, each name its own consent | "Open its own conversation with the assistant", …, "Ask the assistant to work for it, using the device's AI settings" | admitted by the gate; served only to native modules the host policy grants (Rinx); no script-app path |
| `research`, `crawl` | system toolbox tools, with a scope | – | **coming**; the gate refuses them today |
| the manifest's `agent` | an assistant limited to the app's own data | "Run an assistant for this app (…), inside this app's own data only" | App Hub: **available**; shells: **coming** |

Rules of thumb:

- Request `glance` only if the app publishes cards.
- `network.hosts` stays the app's own hosts, for the agent too; wider
  information comes only through granted toolbox tools within the app's
  declared scope (ADR 0002 §13), fetched by the host, not by the app.
- A `local_only` model is app-wide; a shareable tool then must say
  `private_data: false`.
- Declaring a host service's family in a store app does not make a service
  exist: `card-host` registers none, and the shells register only `mail`,
  `llm`, `news` and `glance` (OctoSense `crates/shell/src/apps.rs`,
  `crates/ai-host`).

More: [CAPABILITIES](CAPABILITIES.md), [PUBLISHING](PUBLISHING.md), App Hub
[PUBLISHING § The manifest](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-manifest).

## 9. End to end: News

News is ADR 0002's first slice. Each step, with where it stands:

| # | Step | Status | Where |
| --- | --- | --- | --- |
| 1 | **The data service collects**, no model: HN, TechMeme, Google News, RSS, followed topics (Google News, GDELT), a seen-items ledger, every 15 minutes | **available** (M1) | `apps/news/host-service`: `news.list`, `news.read`, `news.topics.get`, `news.topics.set`, `news.refresh`, `news.sources`, `news.feeds.import`, `os.*` only |
| 2 | **The bundle reads from it**: `host.has("news")`, then `news.list {feed, current: true, limit: 30}` | **coming**: News's manifest cannot request `news` until the shells' App Hub pin has it (#86); until then News fetches in its script | `apps/news/bundle/main.splash` |
| 3 | **A trigger wakes the agent**: the service's fetch report ("N new items") as `news.items.new`, or a schedule (`0 7 * * *`) | **coming** (M3): the service's `on_fetch` hook only logs today | `crates/shell/src/apps.rs` `register_news` |
| 4 | **News's agent runs**, with its `AGENT.md`, skills and tools declared in the bundle | declarations **available** in App Hub (#18); a peer for `os.news` and tool routing **coming** (M2, octos#2567) | App Hub `fixtures/news-agent` |
| 5 | **It runs the `news-digest` template**: `workflow.run {id: "news-digest", params: {topic, language}, run_id: "glance"}` | **coming** (M5, OctoSense#82) | `crates/toolbox` |
| 6 | **The result is stored** by the host, with provenance: `toolbox/runs/news-digest/glance.json` | **coming** (#82) | `crates/toolbox/src/runner.rs` |
| 7 | **A card binds to it**: `news-brief.card`, `source brief sys.digest(app: "os.news", id: "glance", …)` | **coming** (OctoScript#40, OctoScript-Makepad#50, OctoSense#87) | `crates/shell/src/glance_digest.rs` |
| 8 | **Render and critique** the card at glance, phone and desktop sizes | tool **available** (`card-studio`); run by the agent **coming** (M6) | App Hub `crates/card-studio` |
| 9 | **`glance.publish`** the card (`card_id` "brief", `data: {}`; the host fills `brief`) | service **available**; from a contained app **coming** (#86) | `crates/shell/src/glance.rs` |
| 10 | **The person taps it and News opens** | **available** (desktop panel and the phone's glance page open the publishing app) | `glance_panel.rs`, `mobile_pages.rs` |

To see steps 9–10 today, run the desktop shell's own check, which publishes a
sample card as `os.news` at startup (`OCTOSENSE_GLANCE_DEMO=1`) and opens News
from it, hidden and driven over the remote instrument (from an OctoSense
checkout; not run for this guide):

```sh
cargo build --release -p octosense && desktop/scripts/glance_remote.sh
```

## 10. Testing without a real provider

- **Run the app headless**, never with OS screenshots:
  `tools/octo run <bundle> --port 8141 --hidden --detach`, then
  `curl -s "127.0.0.1:8141/snap?q=…"`, `tools/octo shot`, and
  `curl -s 127.0.0.1:8141/quit` ([QUICKSTART §4a](QUICKSTART.md#4a-headless-test-without-the-screen-several-apps-at-once)).
  `card-host` registers no host services. By the rule
  [HOST-SERVICES](HOST-SERVICES.md) verified for `mail`, a granted
  `glance.*` call there answers `no service answers "glance" on this device`,
  and an ungranted one `this app was not granted "glance", which
  "glance.publish" needs` (not run for `glance` here). Make every such call's
  error path visible in the UI, and exercise it.
- **Check the agent declarations** with the gate: `tools/octo check <bundle>`
  (`hub check`) validates `agent`, `tools.json`, `AGENT.md` and skills
  offline; no model is involved.
- **Cards:** render with `card-studio render --card … --data <fixture>.json`
  (section 7): the data is a fixture, so no model or network is needed. For a
  `sys.digest` card, #87 ships a run fixture,
  `crates/shell/resources/glance/fixtures/news-digest-run.json`, and
  `OCTOSENSE_GLANCE_DEMO=digest` (**coming**).
- **Fakes in the platform's own tests**, for when you change a service or the
  toolbox (in OctoSense, not in an app bundle):

  | Piece | Fake | Status |
  | --- | --- | --- |
  | Toolbox templates | `fixture::FakeModel` (deterministic, extractive; can inject a bad URL or citation) and `FixtureBackend`, with recorded cases in `templates/*/fixtures/`; `cargo test --locked -p octosense-toolbox` | **coming** (#82) |
  | `news` service | a fixture `Fetcher` and a moved clock; `cargo test -p octosense-news-service` ("fixtures, no network") | **available** |
  | `llm` service | a local fake provider endpoint (`fake_provider`), `FakeScanner`, `FakePicker`; `OCTOSENSE_LLM_VAULT=file` keeps keys out of the Keychain | **available** |
  | App peers | `tests/fixtures/mock_llm.py` (an OpenAI-compatible server that answers `ECHO: <text>`), a profile with `model_id: "mock-model"`; real-kernel tests run only with `OCTOS_APP_PEERS_TEST_KERNEL=<octos>` | **available** |
  | Kernel | `crates/kernel/tests/fixtures/fake_kernel.py` | **available** |

  An app bundle cannot swap in any of these; they are the platform's.

## What an app author can do today

- Declare an agent (`agent`, `tools.json`, `AGENT.md`, skills) that passes
  `hub check` on App Hub `main`, knowing no shell runs it yet.
- Write and render L0 cards with `card-studio`, and design them around
  `sys.digest` once OctoScript#40 lands.
- Build the app's own screens as today; do not depend on a model at run time.

What an app author cannot do yet: call a model (`model.complete` is **coming**, §2), reach the app's peer from a
script app, publish to the glance screen from a contained app, request
`research` or `crawl`, or have a trigger fire.

## Sources

- OctoSense: `AGENTS.md`; `docs/adr/0002-event-driven-app-agents.md`;
  `docs/adr/home/0004-system-apps-are-contained-script-apps.md`;
  `crates/app-peers/README.md`; `crates/ai-host/src/lib.rs`;
  `apps/ai-providers/host-service/src/lib.rs`, `vault.rs`;
  `apps/ai-providers/bundle/main.splash`; `apps/news/host-service/README.md`;
  `apps/news/bundle/main.splash`; `crates/shell/src/glance.rs`,
  `crates/shell/src/apps.rs` (all `main` at `405139f`); pull requests #82,
  #86 and #87.
- OctoSense-App-Hub (`main` at `362d832`): `crates/app-policy/src/manifest.rs`,
  `agent.rs`, `policy.rs`, `listing.rs`; `crates/app-hub/src/index.rs`;
  `docs/PUBLISHING.md`; `docs/DEVELOPMENT.md`.
- OctoScript pull request #40: `docs/ui-profile-l0.md` §5.14.
- octos pull request #2567: `docs/OCTOS_UI_PROTOCOL_CHANGE_REQUEST_UPCR_2026_035_PEER_HOST_TOOLS.md`.
