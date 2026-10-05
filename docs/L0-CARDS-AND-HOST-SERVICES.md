# L0 cards and host services

A script app calls a service itself — `host.request("mail.accounts", {}, fn(r){ … })`
([HOST-SERVICES](HOST-SERVICES.md#calling-a-service-from-an-app)). An **L0 card**
(`page.card`) has no statements, so it asks the same way in a different form: a
sibling `bindings.json` declares the calls, and the host makes them when the card
opens or when an event the card names arrives.

## Who runs the bindings

`bindings.json` is Rinx's L0 path. Rinx's bundle guide documents the **shape** of
the file — the `{service, args, target}` call, `on_open` and `events`, the
`{"is_ok": …, "data" | "error": …}` written to the target, the `$state` /
`$data` / `$value` argument references, and "declare each service in the
manifest's `capabilities`" — in
[`examples/miniapps/README.md`](https://github.com/hagency-org/Rinx/blob/main/examples/miniapps/README.md).

An OctoSense shell runs an app through the App Hub `CardModule` and its own
registered Rust services, and `card-host` registers none: a bundle carrying
`bindings.json` is admitted and drawn there as usual, and the calls simply do
not happen. So everything below is about the host that **does** run them, and it
is why a card that uses a service is worth running in Rinx before you call it
done.

## The three rules that fail closed

All three were found by running real bundles against the host, and each one
fails the **whole card** — or the **whole app** — rather than the one line that
reads the service. None of them is visible to `hub check`, because none of them
is in the manifest.

### 1. A name the card reads must already be seeded in `page.data.json`

A card is lowered before any call answers. A path the card evaluates that lands
on a name which does not exist fails the entire card:

```
unresolved or unsupported kit property
```

So `state reply { shape: text }` with `text: reply.data.text` is not enough by
itself: `page.data.json` must carry an initial `reply`, and the host's write
replaces it when the call answers.

The rule is about the names the card **reads**, not about every target. A target
the card never reads — a session handle opened only to establish the assistant's
context, say — needs no seed, because an unread name is never resolved. Both
directions verify the same way: seed nothing and leave the target unread, and the
card lowers; read it once, and the card fails until it is seeded.

### 2. A failed call fails the card, so every read needs a guard

When a call fails, the host writes `{"is_ok": false, "error": "…"}` to the
target — there is **no `data`**. A line that reads `X.data.text` then has nothing
to resolve, and the whole card fails to lower rather than the one line. The form
that survives is a bare boolean guard around the read:

```
when read.is_ok { Note(instance: "row_ai", text: read.data.text) }
```

The line the card always draws must sit outside the guard, so the card still
reads as a card when the service answers nothing. Which failures this covers: a
missing provider, a refused permission, a network error, and — on `card-host` —
every call, since no service answers there at all.

### 3. `on_open` failing keeps the app from opening

Every `service` in `bindings.json` must also be in the manifest's
`capabilities`, or the call is refused before anything is queued. And a failure
in any `on_open` call leaves the app **not opening**: it stops with no error
shown. Since `on_open` runs on the way in, a binding that can fail — anything
reaching an assistant, a model or the network — belongs in `events`, or behind a
line the card can still draw without it.

## A worked example

From a card that asks the on-device assistant one question and prints the answer:

```json
// bindings.json
{
  "on_open": [
    { "service": "octos.session.open", "target": "session" },
    { "service": "octos.turn.start", "target": "read",
      "args": { "text": "…what two things does this message still leave out?" } }
  ]
}
```

```json
// page.data.json — `read` is seeded; `session` is a target the card never reads,
// so it needs no seed. The seed is what the card draws if the turn never answers.
{ "$kit": { "theme": "light", "placements": { … } },
  "read": { "is_ok": false, "error": "assistant has not answered yet" } }
```

```
# page.card — the guard is the whole of the wiring on the card's side
when read.is_ok { Note(instance: "row_ai", text: read.data.text) }
```

`octos.session.open` and `octos.turn.start` are in the manifest's
`capabilities`; without them the calls are refused, and with the turn in
`on_open` a host that cannot answer leaves the app unopened (rule 3).

## Checking a bundle before a host runs it

[`tools/l0-bindings-lint.py`](../tools/l0-bindings-lint.py) implements the three
rules over the files — no L0 parser, no dependencies, and it writes nothing:

```sh
python3 tools/l0-bindings-lint.py ./bundle
```

```
  ok   page.card: "read" is seeded and guarded
  warn events[open]: target "session" is neither referenced by page.card nor seeded
  ERR  page.card reads "reply" (a binding target) with no `when reply.is_ok { … }` guard
  ...
l0-bindings-lint: 2 ok, 1 warn, 1 error
```

Exit 0 when the card will lower, 1 when it will not. It is not a gate and does
not replace `hub check`: it catches what `hub check` admits, which is exactly the
class of fault this page is about.
