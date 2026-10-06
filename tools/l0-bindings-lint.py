#!/usr/bin/env python3
"""Catch the L0 card faults that fail the whole card before a host runs it.

An L0 card reaches a host service through a sibling `bindings.json`. Four
things about that wiring fail closed, and none of them is visible to `hub check`,
because none of them is in the manifest. All were found by running real bundles
against the host that runs the bindings; see docs/L0-CARDS-AND-HOST-SERVICES.md.

  0. A name the card **reads** must be declared — a `source`, `state`, `copy`,
     a `for` binder or a component param. `check_ui_l0` refuses any other root
     ("… is not a declared name") and App Hub admission rejects the bundle on
     that refusal, before any host runs. A binding target does NOT declare a
     name: a card that reads one must declare it too (`state X { shape: record }`).
     This is the one rule here that is a hard ERR on BOTH lowering paths, and it
     is exactly what a card whose only wiring is a `bindings.json` is most likely
     to get wrong.

  1. On the native-Kit path, a declared name the card reads must also be
     **resolvable on the first frame** — seeded in `page.data.json`, declared with
     a `state … { initial: … }`, or answered by a `source`. The card is lowered
     before any reply arrives, and a path landing on a name with no value fails
     the WHOLE card ("unresolved or unsupported kit property"), not the one line.
     A target the card never reads needs no seed: an unread name is never
     resolved.

  2. A failed call writes `{"is_ok": false, "error": "…"}` — no `data` — so a
     read of `X.data.*` must sit inside a guard on `X` (`when X.is_ok { … }`,
     `when X.$state == .ready { … }`). On the native-Kit path, without it one
     failure lowers the whole card.

  3. Every `service` must be declared in `manifest.capabilities`: an undeclared
     service aborts the whole import, so the app never opens. A failure in any
     `on_open` call also keeps the app from opening, with the reason shown in the
     panel's notice line. Two `on_open` calls that share a target are refused:
     the dispatch rejects the second as "already running", which fails `run()`.

Rules 1 and 2 are about the **native-Kit** lowering path — a card whose realized
tree contains a `Kit` node, which Rinx lowers through `kit_pack::lower`. A card
built from semantic components only (TextBody, Chip, Field, …) lowers through
the makepad `kit::lower` instead, where a name that is not seeded, or an
unguarded read after a failed call, renders as an em dash "—" and the card keeps
drawing. The tool branches on which path the card takes, so on the semantic path
those two findings are a WARN, not an ERR. Rule 0 is an ERR either way.

Usage:
    python3 tools/l0-bindings-lint.py <bundle_dir>

Exit codes: 0 when the card will lower (warnings allowed), 1 when it will not,
2 for a usage error or a missing bundle file.
Read-only, standard library only, and everything outside JSON is scanned as
plain text — no L0 parser is required. The card scan is string-aware and
comment-aware; it does not build a parse tree, so a construct a lexical scan
cannot see exactly (a name produced by an expression, say) may be missed. It
errs toward WARN there, never toward a false ERR.
"""
import json
import os
import re
import sys
from collections import Counter

MAX_BINDINGS = {"on_open": 8, "events": 64}
# Rinx's `Call` is #[serde(deny_unknown_fields)]; these are its only keys, and a
# typo'd key is refused at admission.
CALL_KEYS = {"service", "args", "target"}
# A top-level data name: Rinx admission is byte-wise ASCII alphanumeric + `_`
# (`package.rs`, target charset). `\Z` is the end of the whole string, so a
# target passed with a trailing newline (`"target": "read\n"`) is rejected the
# way the host rejects it — `$` would have matched before that newline.
TARGET_RE = re.compile(r"^[A-Za-z0-9_]+\Z")
# L0 identifiers: `is_ident_start` is `is_alphabetic() || '_'`, `is_ident_continue`
# is `is_alphanumeric() || '_'` (octoscript-ui-l0 `lib.rs`) — so a non-ASCII name
# like `réponse` is a legal name and must be scanned like any other.
IDENT = r"(?![0-9])\w+"
# A keyword is an Ident token equal to the word, so `state` in `state X {` is
# only a declaration when the word is not the argument name of `state:`.
KEYWORDS = frozenset(
    "view component state source copy event for when into slot key theme "
    "shape initial true false".split())
# A dotted read: head captured, so `X.data` and `X.data.text` are ONE read of `X`
# (`X.data[0].text`, `read . data . x` for spacing). `read`/`copy`/`rows[0]` are
# heads.
PATH_RE = re.compile(
    r"(?<![.\w])(" + IDENT + r")\s*(?:\[[^\]]*\])?\s*\.\s*(" + IDENT + r")")
# A guard on a result name: `when X.is_ok { … }` and the source form
# `when X.$state == .ready { … }`. The name must be a `state`/`source`/target.
GUARD_OK_RE = re.compile(r"(?<![.\w])when\s+(" + IDENT + r")\s*\.\s*is_ok\b")
GUARD_STATE_RE = re.compile(
    r"(?<![.\w])when\s+(" + IDENT + r")\s*\.\s*\$state\s*==\s*\.\s*(?:ready|done|settled)\b")
# `state X { … }` — a declaration, and whether it carries an `initial:`.
STATE_RE = re.compile(r"(?<![.\w])state\s+(" + IDENT + r")\s*\{")
SOURCE_RE = re.compile(r"(?<![.\w])source\s+(" + IDENT + r")\b")
COPY_RE = re.compile(r"(?<![.\w])copy\s+(" + IDENT + r")\s*\{")
# The two other shapes that declare a readable name: a `for` binder and a
# component parameter. Both go into `Scope::roots` beside sources, states and
# `copy`, so a read of either is a declared name and does not need a seed.
FOR_BINDER_RE = re.compile(r"(?<![.\w])for\s+(" + IDENT + r")\s+in\b")
COMPONENT_PARAM_RE = re.compile(r"(?<![.\w])component\s+" + IDENT + r"\s*\(([^)]*)\)")
PARAM_NAME_RE = re.compile(r"(" + IDENT + r")\s*:")
# Any `Kit(` call — argument order is free (`kit_pack` reads Kit args by name),
# so keying on `Kit(component:` misses `Kit(instance: …, component: …)` and
# classifies a native-Kit card as semantic, the wrong side of the exit code.
KIT_ANY_RE = re.compile(r"(?<![.\w])Kit\s*\(")
# `view [<name>] <Constructor>(…)` — the root view's constructor decides the
# path. `view root <Name>` may name a card-declared component
# (`component Page(...) { view Kit(…) }`), which realizes to a Kit root, so the
# constructor is resolved through the card's own components before the path is
# chosen — the way `complete_root()` does. The constructor is the identifier
# right before the `(`; the view name, when present, is optional.
ROOT_RE = re.compile(
    r"(?<![.\w])view\s+(?:(" + IDENT + r")\s+)?(" + IDENT + r")\s*[({]")
COMPONENT_DEF_RE = re.compile(
    r"(?<![.\w])component\s+(" + IDENT + r")\s*\([^)]*\)\s*\{")
# `component Kit(…) { … }` — a card-declared component named `Kit` shadows the
# built-in constructor, so the realized tree is whatever that component lowers to.
SHADOW_RE = re.compile(r"(?<![.\w])component\s+Kit\s*\(")


class BundleError(Exception):
    """A bundle file that is missing, unreadable, or not valid JSON."""


def strip_comments(card):
    """Drop `#` and `//` comments, keeping every other byte — and every byte of
    a string literal, where `#` and `//` are content (the L0 lexer scans a
    string as one token). Comment bytes become spaces so offsets are preserved."""
    out = []
    i, n = 0, len(card)
    while i < n:
        c = card[i]
        if c == '"':
            out.append(c)
            i += 1
            while i < n:
                if card[i] == "\\" and i + 1 < n:
                    out.append(card[i])
                    out.append(card[i + 1])
                    i += 2
                    continue
                out.append(card[i])
                if card[i] == '"':
                    i += 1
                    break
                if card[i] == "\n":
                    i += 1
                    break
                i += 1
            continue
        if c == "#" or (c == "/" and i + 1 < n and card[i + 1] == "/"):
            while i < n and card[i] != "\n":
                out.append(" ")
                i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def block_end(code, start):
    """Index just past the block whose `{` is at/after `start`, or -1."""
    i = code.find("{", start)
    if i < 0:
        return -1
    depth = 0
    while i < len(code):
        c = code[i]
        if c == '"':
            i += 1
            while i < len(code):
                if code[i] == "\\":
                    i += 2
                    continue
                if code[i] == '"':
                    i += 1
                    break
                if code[i] == "\n":
                    break
                i += 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def guarded_spans(code):
    """Spans `(start, end, name)` of guard blocks, so a read *inside* the block
    is guarded and a read elsewhere of the same name is not — the guard is on a
    read, not on a name for the whole card."""
    spans = []
    for rx in (GUARD_OK_RE, GUARD_STATE_RE):
        for m in rx.finditer(code):
            end = block_end(code, m.end())
            if end > 0:
                spans.append((m.start(), end, m.group(1)))
    return spans


def read_json(path):
    """Parse a bundle JSON file, reporting duplicate keys (which Python silently
    collapses to the last while serde refuses the field)."""
    dups = []

    def hook(pairs):
        seen = set()
        for k, _v in pairs:
            if k in seen:
                dups.append(k)
            seen.add(k)
        return dict(pairs)

    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh, object_pairs_hook=hook), dups
    except json.JSONDecodeError as exc:
        raise BundleError("%s is not valid JSON: %s" % (os.path.basename(path), exc))
    except (OSError, UnicodeDecodeError) as exc:
        raise BundleError("%s cannot be read: %s" % (os.path.basename(path), exc))


def report(oks, warns, errors):
    for message in oks:
        print("  ok   %s" % message)
    for message in warns:
        print("  warn %s" % message)
    for message in errors:
        print("  ERR  %s" % message)
    print()
    print("l0-bindings-lint: %d ok, %d warn, %d error" % (len(oks), len(warns), len(errors)))


def pointer_ok(pointer, data):
    """JSON Pointer (/a/b) into a JSON object — the shape `$data` takes."""
    if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
        return False
    node = data
    for token in pointer.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict) and token in node:
            node = node[token]
        elif isinstance(node, list) and token.isdigit() and int(token) < len(node):
            node = node[int(token)]
        else:
            return False
    return True


def check_args(where, target, args, data, declared_states, errors):
    """The two `$`-reference shapes Rinx resolves at import time, both of which
    fail closed: a `$data` pointer into nothing ("Missing binding data") and a
    `$state` name no store cell answers ("Missing binding state").

    `$state` resolves against the calling instance's store cell first, then card
    state (`arguments` in `package.rs`: `state.get(key, …).or_else(|| state.get(
    CARD_STATE_KEY, …))`). The tool cannot know an instance's own cells, so it
    accepts any `state` the card declares anywhere — card-level or
    component-local — plus the call's own target, and errors on anything else."""
    for key, template in args.items():
        if not isinstance(template, dict) or len(template) != 1:
            continue
        if "$data" in template:
            ptr = template["$data"]
            if not pointer_ok(ptr, data):
                errors.append(
                    "%s: args.%s: $data %r resolves to nothing — Rinx refuses with "
                    "`Missing binding data`, and for an on_open call the app does not "
                    "open" % (where, key, ptr))
        elif "$state" in template:
            name = template["$state"]
            if not isinstance(name, str) or (name not in declared_states and name != target):
                errors.append(
                    "%s: args.%s: $state %r is neither a declared state nor the call's "
                    "own target %r — Rinx refuses with `Missing binding state`"
                    % (where, key, name, target))


def path_reads(code):
    """Every `(head, position)` of a dotted read, once per head occurrence.

    `X.data` and `X.data.text` are ONE read of `X`, not two: the scan keeps the
    head and skips a match whose head is itself a continuation of a longer path
    (`data.text` inside `read.data.text`, or `<spaced> data . x`). `copy.<name>`
    is a copy lookup, not a host-service read, and is left to `check_ui_l0`."""
    out, seen = [], set()
    for m in PATH_RE.finditer(code):
        name, pos = m.group(1), m.start()
        if name == "copy" or name in KEYWORDS:
            continue
        before = code[:pos].rstrip()
        if before.endswith(".") or before.endswith("["):
            continue
        if (name, pos) in seen:
            continue
        seen.add((name, pos))
        out.append((name, pos))
    return out


def component_bodies(code):
    """`{component name: its `view …` body}` for the card's own components, so
    the root constructor can be resolved one hop (`view root Page(…)` →
    `component Page { view Kit(…) }`) the way `complete_root()` does."""
    out = {}
    for m in COMPONENT_DEF_RE.finditer(code):
        start = code.find("{", m.end() - 1)
        end = block_end(code, start)
        if start < 0 or end < 0:
            continue
        body = ROOT_RE.search(code, start, end)
        if body:
            out[m.group(1)] = code[body.start():end]
    return out


def main(argv):
    if len(argv) != 2:
        print("usage: python3 tools/l0-bindings-lint.py <bundle_dir>")
        return 2

    root = argv[1]
    errors, warns, oks = [], [], []

    card_path = os.path.join(root, "page.card")
    data_path = os.path.join(root, "page.data.json")
    bind_path = os.path.join(root, "bindings.json")
    manifest_path = os.path.join(root, "manifest.json")

    # `page.card` and `manifest.json` are what a bundle is checked on; both Rinx
    # and hub admission treat `page.data.json` as optional (`package.rs`,
    # `admission.rs`: absent ⇒ `{}`).
    for path in (card_path, manifest_path):
        if not os.path.isfile(path):
            print("not an L0 card bundle: missing %s" % os.path.basename(path))
            return 2

    try:
        with open(card_path, encoding="utf-8") as fh:
            card = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        errors.append("page.card cannot be read as UTF-8: %s" % exc)
        report(oks, warns, errors)
        return 1

    if os.path.isfile(data_path):
        try:
            data, data_dups = read_json(data_path)
        except BundleError as exc:
            errors.append(str(exc))
            report(oks, warns, errors)
            return 1
    else:
        data, data_dups = {}, []
        oks.append("no page.data.json — optional, and a card with no seeded read needs none")

    try:
        manifest, _ = read_json(manifest_path)
    except BundleError as exc:
        errors.append(str(exc))
        report(oks, warns, errors)
        return 1

    if not isinstance(data, dict):
        errors.append("page.data.json must be a JSON object")
        data = {}
    for key in sorted(set(data_dups)):
        errors.append("page.data.json: duplicate key %r — Python keeps the last, serde "
                      "refuses the field" % key)

    capabilities = manifest.get("capabilities", []) if isinstance(manifest, dict) else []
    capabilities = capabilities or []

    # Scan real syntax only: comments are stripped (string-aware), so prose
    # mentioning "page.data.json" in a banner is not read as a read of it.
    code = strip_comments(card)

    # Rule 0 is about `page.card` alone — `check_ui_l0` never reads bindings.json
    # — so a static card (no bindings) is still checked for it. Only the
    # bindings-side rules (3, and the `$`-reference checks) need the file.
    have_bindings = os.path.isfile(bind_path)
    if have_bindings:
        try:
            bindings, bind_dups = read_json(bind_path)
        except BundleError as exc:
            errors.append(str(exc))
            report(oks, warns, errors)
            return 1
        if not isinstance(bindings, dict):
            errors.append("bindings.json must be a JSON object")
            report(oks, warns, errors)
            return 1
        for key in sorted(set(bind_dups)):
            errors.append("bindings.json: duplicate key %r — Python keeps the last, serde "
                          "refuses the field" % key)
    else:
        bindings, bind_dups = {}, []
        oks.append("no bindings.json — a static card, nothing to wire")

    unknown = set(bindings) - set(MAX_BINDINGS)
    if unknown:
        errors.append("bindings.json has unknown keys: %s" % ", ".join(sorted(unknown)))

    calls = []
    on_open_targets = []
    malformed_section = False
    for name, limit in MAX_BINDINGS.items():
        # An absent section is not a malformed one: Rinx defaults `on_open` to
        # an empty list and `events` to an empty map, so an events-only bundle
        # is a fully valid shape.
        section = bindings.get(name, [] if name == "on_open" else {})
        if name == "on_open":
            if not isinstance(section, list):
                errors.append("bindings.json: on_open must be an array")
                malformed_section = True
                continue
            items = [(name, i, call) for i, call in enumerate(section)]
            on_open_targets = [
                call["target"]
                for call in section
                if isinstance(call, dict) and isinstance(call.get("target"), str)
            ]
        else:
            if not isinstance(section, dict):
                errors.append("bindings.json: events must be an object")
                malformed_section = True
                continue
            items = [(name, key, call) for key, call in section.items()]
        if len(items) > limit:
            errors.append("bindings.json: %s has %d entries, the limit is %d"
                          % (name, len(items), limit))
        calls.extend(items)

    # "present but empty" is about a well-shaped file with nothing wired. A
    # section that failed its shape check already said so, and saying "empty"
    # beside it contradicts the error — and a card with no bindings.json at all
    # already said so above.
    if have_bindings and not malformed_section and not calls:
        warns.append("bindings.json is present but empty")

    dupes = sorted(t for t, n in Counter(on_open_targets).items() if n > 1)
    if dupes:
        errors.append(
            "bindings.json: on_open repeats target(s) %s — Rinx's dispatch refuses the "
            "second call as already running, which fails run() and keeps the app from "
            "opening" % ", ".join(dupes))

    targets = []
    # Names a `$state` reference may resolve against: every `source`, every
    # `state` and every binding target, gathered before the calls are checked so
    # a reference to a later call's target is not read as missing.
    all_names = set(SOURCE_RE.findall(code)) | set(STATE_RE.findall(code))
    for _s, _k, _call in calls:
        if isinstance(_call, dict) and isinstance(_call.get("target"), str):
            all_names.add(_call["target"])
    for section, key, call in calls:
        where = "%s[%s]" % (section, key)
        if not isinstance(call, dict):
            errors.append("%s must be an object" % where)
            continue
        extra = set(call) - CALL_KEYS
        if extra:
            errors.append("%s: unknown key(s) %s — Rinx's Call denies unknown fields and "
                          "refuses the bundle" % (where, ", ".join(sorted(extra))))
        service = call.get("service")
        target = call.get("target")
        args = call.get("args")

        if not isinstance(service, str) or not service:
            errors.append("%s: service must be a non-empty string" % where)
        elif service not in capabilities:
            errors.append("%s: service %r is not declared in manifest.capabilities — an "
                          "undeclared service aborts the whole import" % (where, service))
        else:
            oks.append("%s: service %r is granted" % (where, service))

        if not isinstance(target, str) or not TARGET_RE.match(target or ""):
            errors.append("%s: target must be a top-level data name [A-Za-z0-9_]" % where)
        else:
            targets.append((where, target))
            all_names.add(target)

        # `"args": null` is refused by serde (`#[serde(default)]` defaults only an
        # absent key, and `!args.is_object()` then fails); `call.get("args")`
        # cannot tell null from absence, so test the key directly.
        if "args" in call and args is not None and not isinstance(args, dict):
            errors.append("%s: args must be an object" % where)
        elif "args" in call and args is None:
            errors.append("%s: args is null — Rinx defaults only an absent key and refuses "
                          "a null argument object" % where)
        elif isinstance(args, dict):
            check_args(where, target if isinstance(target, str) else "", args, data,
                       all_names, errors)

    # Rules 1 and 2, over the names the card actually reads. They fail the whole
    # card only on the native-Kit path; on the semantic path the same fault
    # renders as an em dash and the card keeps drawing, so it is a warning.
    # Which lowering path the card takes. `complete_root()` resolves the root
    # view through the card's own components, so `view root Page(...)` where
    # `component Page` lowers to `Kit(...)` IS a Kit root — resolve one hop at a
    # time, the same way, before deciding.
    root_m = ROOT_RE.search(code)
    root_ctor = root_m.group(2) if root_m else ""
    bodies = component_bodies(code)
    for _ in range(4):
        body = bodies.get(root_ctor)
        if body is None:
            break
        inner = ROOT_RE.search(body)
        if not inner or inner.group(2) == root_ctor:
            break
        root_ctor = inner.group(2)
    has_kit = bool(KIT_ANY_RE.search(code))
    shadowed = bool(SHADOW_RE.search(code))
    if shadowed:
        # The card declares its own `Kit` component, which shadows the built-in
        # constructor; the realized tree is semantic.
        kit_path = False
        oks.append("card declares a `Kit` component — the built-in constructor is "
                   "shadowed, so the realized tree is on the semantic path")
    elif root_ctor == "Kit":
        kit_path = True
    elif has_kit:
        # A Kit node under a non-Kit root always fails: `tree()`'s visit requires
        # the root itself to be a Kit.
        kit_path = True
        errors.append("page.card roots at %r but contains a `Kit(` node — on the "
                      "native-Kit path `tree()` requires the ROOT to be a Kit, so the "
                      "card always fails to lower" % (root_ctor or "?"))
    else:
        kit_path = False

    if kit_path:
        missing_effect = ("a path into an absent name fails the WHOLE card "
                          "('unresolved or unsupported kit property')")
        unguarded_effect = "the whole card fails to lower instead of the one line"
    else:
        missing_effect = "an absent name renders as an em dash and the card keeps drawing"
        unguarded_effect = "an unguarded read of the failed result renders as an em dash"

    declared_states = set(STATE_RE.findall(code))
    states_with_initial = set()
    for m in STATE_RE.finditer(code):
        end = block_end(code, m.end() - 1)
        body = code[m.end() - 1:end if end > 0 else len(code)]
        if re.search(r"(?<![.\w])initial\s*:", body):
            states_with_initial.add(m.group(1))
    sources = set(SOURCE_RE.findall(code))
    copies = set(COPY_RE.findall(code))
    # Names the card DECLARES, as `check_ui_l0` counts them: sources, states,
    # copies, `for` binders and component params. A binding target is NOT among
    # them, so a card that reads one must declare it separately — the doc's
    # matrix-octos declares `state answer`/`state profile` for exactly this.
    declared = (
        declared_states | sources | copies
        | set(FOR_BINDER_RE.findall(code))
        | {p for group in COMPONENT_PARAM_RE.findall(code)
           for p in PARAM_NAME_RE.findall(group)}
    )
    # Names a read can land on and still lower: a declaration with no seed draws
    # an em dash (semantic path) or fails the whole card (kit path).
    resolvable = set(data) | sources | states_with_initial

    spans = guarded_spans(code)
    target_names = {target for _, target in targets}
    reads = path_reads(code)

    def guarded(name, pos):
        return any(n == name and s <= pos < e for s, e, n in spans)

    def undeclared_finding(name):
        return (
            "page.card reads %r but the card never declares it — a name a card "
            "reads must be a `source`, `state` or `copy` (%r is not a declared "
            "name), so `check_ui_l0` refuses and App Hub admission rejects the "
            "bundle. A binding target does not declare one: add `state %s { shape: "
            "record }`." % (name, name, name))

    def unseeded_finding(name):
        return (
            "page.card reads %r but nothing resolves it on the first frame — the "
            "card is lowered before any reply, and %s. Seed it in page.data.json, "
            "or declare `state %s { initial: … }`."
            % (name, missing_effect, name))

    def unguarded_target(name):
        return (
            "page.card reads %r (a binding target) with no guard on that read — a "
            "failed call writes {is_ok:false,error:…} with no `data`, and %s. Wrap "
            "it in `when %s.is_ok { … }` (or `when %s.$state == .ready { … }`)."
            % (name, unguarded_effect, name, name))

    rule_findings = set()
    # `check_ui_l0` refuses an undeclared root on EITHER path, before any host
    # runs, so that one is an ERR even for a semantic card. Report it once per
    # NAME: `read` in `when read.is_ok { … read.data … }` is two reads plus the
    # guard, and one undeclared name is one `check_ui_l0` refusal, not three.
    undeclared = set()
    for name, pos in reads:
        if name not in declared:
            undeclared.add(name)
        elif name not in resolvable:
            rule_findings.add(unseeded_finding(name))
        elif name in target_names and not guarded(name, pos):
            rule_findings.add(unguarded_target(name))
    for _start, _end, name in spans:
        if name not in declared:
            undeclared.add(name)
    for name in sorted(undeclared):
        errors.append(undeclared_finding(name))

    # Names page.card actually reads (or guards). Deliberately WITHOUT the
    # binding targets: a target the card never reads is the case the "neither
    # referenced nor seeded" warning below is for, and folding targets in here
    # made that branch unreachable.
    referenced = ({name for name, _pos in reads}
                  | {name for _s, _e, name in spans})

    for name in sorted(referenced):
        # A name already reported as undeclared gets no "is seeded, guarded" line:
        # the ERR above is the finding, and a green line beside it contradicts it.
        if name in resolvable and name not in undeclared:
            how = []
            if name in declared_states:
                how.append("declared")
            if name in data:
                how.append("seeded")
            if name in states_with_initial:
                how.append("with initial")
            if any(n == name for _s, _e, n in spans):
                how.append("guarded")
            oks.append("page.card: %r is %s" % (name, ", ".join(how) or "referenced"))

    rule_findings = sorted(set(rule_findings))
    if rule_findings:
        # Spell out the path only when rules 1-2 actually fire, so a clean card's
        # output is unchanged and the severity below is self-explanatory.
        oks.append("rules 1-2 %s on this card's path (%s)"
                   % ("fail the whole card" if kit_path else "render as an em dash",
                      "root is Kit" if kit_path else "semantic root %r" % (root_ctor or "?")))
        (errors if kit_path else warns).extend(rule_findings)

    # A target the card never reads is harmless unseeded, but fragile.
    for where, target in targets:
        if target not in referenced and target not in data:
            warns.append(
                "%s: target %r is neither referenced by page.card nor seeded — harmless "
                "today, since an unread name is never resolved, but seed it so a later "
                "reference cannot fail the whole card." % (where, target))
        elif target in data and isinstance(data[target], dict) and data[target].get("is_ok") is False:
            warns.append(
                "%s: target %r is seeded as is_ok:false — fine while every read of it is "
                "guarded, otherwise the card shows nothing for it" % (where, target))

    report(oks, warns, errors)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
