# Migrate submitted apps to the current host API

English | [简体中文](SUBMISSION-API-MIGRATIONS.zh-CN.md)

A known capability name is not proof that a method exists, and a gate pass is
not a successful service call. This guide repairs concrete submission contracts
without editing a contestant's repository or copying their UI. The examples are
maintained development fixtures, not published replacement apps.

Start with the [API Migration Lab](../examples/api-migration-lab/README.md)
for real local editing and unavailable-service behavior, then
[Script Tool State](../examples/script-tool-state/README.md) for an app-owned
handler sharing the UI's saved state. Both use synthetic data. Neither requires
an account or model key.

## 1. Match the grant, request and result together

Qianxian's submitted [manifest](https://github.com/kkkkikun/qianxian-guardian/blob/9c7c32291a3a2fdfaed2c34152040cd1239d1834/app/qianxian/bundle/manifest.json)
requests `storage` and `octos.turn.start`, but its
[model request](https://github.com/kkkkikun/qianxian-guardian/blob/9c7c32291a3a2fdfaed2c34152040cd1239d1834/app/qianxian/bundle/main.splash#L1537)
uses `model.complete` with `prompt` and a plain field map. Add `model` only if
that feature remains, send `task`, `input` and a JSON Schema, and read
`r.data.output`, not a provider-style `content` or `choices` field:

```splash
host.request("model.complete", {
    task: "Summarize the note in one short sentence."
    input: {note: note}
    schema: {type: "object"
        properties: {summary: {type: "string" maxLength: 160}}
        required: ["summary"] additionalProperties: false}
    class: "fast"
}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) return }
    ui.summary.set_text(r.data.output.summary)
})
```

The runnable [implementation](../examples/api-migration-lab/bundle/main.splash)
also saves local edits and retains them after refusal. `model` and `octos` are
separate capabilities: a grant to the app agent does not grant direct model
calls. `octos.turn.start({text})` is valid without a separate `session.open`
call. Do not add a direct provider-key field or keep a token in app storage.
See [AI services](AI-SERVICES.md#the-model-service) for budgets, errors and
response limits.

## 2. Publish a real presentation with a stable card identity

Qianxian's `level/title/body` object and OctoStudio's
[`glance.publish({data: ...})`](https://github.com/aios-pub/OctoStudio/blob/bc58cb3/bundle/main.splash#L1508)
do not supply a presentation. Request `glance` and provide `card_id`, `title`
and exactly one presentation:

| Presentation | Request fields | What the host runs |
| --- | --- | --- |
| Admitted template | `template: "brief.splash", initial: {summary: ...}` | A `.splash` file at the root of this admitted bundle, with host-bound initial data |
| L0 source | `source: card_source, data: {}` | Checked `.card` language, not Splash |
| Direct app script | `script: splash_source` | App-authored Splash; agent tools cannot supply this |

The Lab uses the first form:

```splash
host.request("glance.publish", {
    card_id: "brief" title: "My reviewed brief" summary: summary
    template: "brief.splash" initial: {summary: summary}
    notify: false expires: 3600
}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) return }
    card_id = r.data.card_id
})
host.request("glance.withdraw", {card_id: card_id}, fn(r){
    if !r.is_ok { ui.status.set_text(r.error) }
})
```

OctoStudio must also change its returned `id` and withdrawal `{id}` to
`card_id`. Reusing the same ID replaces the same card. A different email or
news item needs its own ID; a summary refresh should not create duplicates.
The optional `open.app` must be the publishing app's own ID.

For L0, use `source: card_source` with `data`, as in the
[host reference](AI-SERVICES.md#glancepublish-glancewithdraw-glancelist), and
validate the actual source with the selected L0 runtime. `level: "L0"` does
not convert arbitrary JSON into a card. Agent-published templates use
`template` plus `initial`; do not combine these with `script`, `source` or
`data`, and never expose executable Splash in an agent tool's schema.

## 3. Move old callbacks to the current app-tool ABI

DailyFlow's submitted [handler](https://github.com/KumaYuriPool/DailyFlow/blob/dfb69ea9130fd5c0b2778ebf647ea900a7537713/bundle/main.splash#L871)
uses an older callback contract. The generic executor already exists; update
all three parts together:

| Older submission | Current contract |
| --- | --- |
| Missing runtime requirement | Manifest `requires: ["script-tools-v1"]` |
| `on_agent_tool(token, name, args_json)` | `app_tool(name, call_id)` |
| Parse the callback's JSON argument string | `mod.app_tools.request(call_id).args` |
| `mod.app_tools.resolve` / `reject` | `mod.app_tools.complete` / `fail` |

The [state fixture](../examples/script-tool-state/bundle/main.splash) has one
shared update function for its editor and tool. It persists the result before
calling `complete`, and returns the exact saved topics and revision. The
handler does not create another script VM, another chat session or a second
copy of the document. A tool saying “updated” is not evidence of an update;
read the returned state and inspect the editor.

`request.context` is stamped by the host with app, account, caller and call ID.
Do not replace it with an identity from `request.args`. For asynchronous work,
check `mod.app_tools.active(call_id)` before completing an expired call. Input
and output schemas are enforced. A closed app returns `app_not_running`;
this ABI does not launch it or create a general background worker.

## 4. Give the assistant an actual declared preference tool

TrendyHear's latest [v0.4.4 source](https://github.com/shaokaiyuan0513-dotcom/TrendyHear/tree/25d25960baee624d6360a4b8f48b8c0cd599e49a/bundle)
has a preference flow but no `tools.json`. Asking for `implemented_by: "app"`
support is no longer the missing step. Add:

1. `requires: ["script-tools-v1"]` and an honest `agent` declaration.
2. `tools.json` entries with `implemented_by: "app"`, bounded input/output
   schemas, truthful risk and private-data declarations.
3. The `app_tool` hook in the full app, using its existing preference store.
4. Guidance to read the saved preference before answering, change it only on
   request, and report the returned state rather than assume success.

Copy the pattern from the fixture's [manifest](../examples/script-tool-state/bundle/manifest.json),
[tools](../examples/script-tool-state/bundle/tools.json) and
[guidance](../examples/script-tool-state/bundle/AGENT.md). Use the real app's
namespace (`trendyhear.*` for `skystream.trendyhear`), not `toolstate.*`.
Declaring a tool offers an assistant; the person must still consent to it.
The native acceptance caller deliberately bypasses model/peer dispatch, so
its receipt does not certify that consent flow or model reasoning.

## 5. Validate on the right host

- `card-host` can exercise local UI, storage and real unavailable-service
  responses. It serves no model or Glance service.
- `card-host` refuses `script-tools-v1`; do not remove the marker to claim
  that agent tools passed. The state fixture uses the native runner linked
  from its README, which checks signed admission and calls the actual ABI.
- A current compatible shell is still needed for successful model calls,
  Glance publication, app-agent consent and peer routing. Test the exact
  release and platform; current source is not an installed update.
- **Pending:** generic third-party Mail draft/review/send, native calendar
  writes and public Matrix routing are separate host work. These examples
  do not call them or claim that documentation closes those gaps. The
  separate `auth`/`gmail`/`gcalendar` connectors have different contracts;
  they are not aliases for `mail.*` or `calendar.*`.

Keep failed receipts. A native pixel capture, a saved-file check, an admission
pass and a successful external operation establish different things. Record
which happened and leave the rest unverified.
