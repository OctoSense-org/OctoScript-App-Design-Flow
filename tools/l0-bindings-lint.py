#!/usr/bin/env python3
"""Catch the L0 card faults that fail the whole card before a host runs it.

An L0 card reaches a host service through a sibling `bindings.json`. Three
things about that wiring fail closed, and none of them is visible to
`hub check`, because none of them is in the manifest. All three were found by
running real bundles against the host that runs the bindings; see
docs/L0-CARDS-AND-HOST-SERVICES.md.

  1. A name the card **reads** must already be seeded in `page.data.json`. The
     card is lowered before any reply arrives, and a path landing on a name
     that does not exist fails the WHOLE card
     ("unresolved or unsupported kit property"), not the one line. A target
     the card never reads needs no seed: an unread name is never resolved.

  2. A failed call writes `{"is_ok": false, "error": "…"}` — no `data` — so a
     read of `X.data.*` must sit inside a bare boolean guard
     (`when X.is_ok { … }`). Without it, one failure lowers the whole card.

  3. Every `service` must be declared in `manifest.capabilities`, and a failure
     in any `on_open` call keeps the app from opening at all.

Usage:
    python3 tools/l0-bindings-lint.py <bundle_dir>

Exit code: 0 when the card will lower (warnings allowed), 1 when it will not.
Read-only, standard library only, and everything outside JSON is scanned as
plain text — no L0 parser is required.
"""
import json
import os
import re
import sys

MAX_BINDINGS = {"on_open": 8, "events": 64}
TARGET_RE = re.compile(r"^[A-Za-z0-9_]+$")
# `X.data.<field>` / `X.data[` — a read of a service result
DATA_READ_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\.data\b")
# `when X.is_ok { … }` — the bare boolean guard L0 predicates allow
GUARD_RE = re.compile(r"\bwhen\s+([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*is_ok\b")
# `state X { … }` — a declaration
STATE_RE = re.compile(r"\bstate\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{")


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def report(oks, warns, errors):
    for message in oks:
        print("  ok   %s" % message)
    for message in warns:
        print("  warn %s" % message)
    for message in errors:
        print("  ERR  %s" % message)
    print()
    print("l0-bindings-lint: %d ok, %d warn, %d error" % (len(oks), len(warns), len(errors)))


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

    for path in (card_path, data_path, manifest_path):
        if not os.path.isfile(path):
            print("not an L0 card bundle: missing %s" % os.path.basename(path))
            return 2

    card = open(card_path, encoding="utf-8").read()
    data = read_json(data_path)
    capabilities = read_json(manifest_path).get("capabilities", []) or []

    # Scan real syntax only: drop `#` comments, so prose mentioning
    # "page.data.json" in a banner is not read as a read of `page.data`.
    card_code = "\n".join(line.split("#", 1)[0] for line in card.splitlines())

    if not isinstance(data, dict):
        errors.append("page.data.json must be a JSON object")
        data = {}

    if not os.path.isfile(bind_path):
        oks.append("no bindings.json — a static card, nothing to wire")
        report(oks, warns, errors)
        return 0

    bindings = read_json(bind_path)
    if not isinstance(bindings, dict):
        errors.append("bindings.json must be a JSON object")
        report(oks, warns, errors)
        return 1

    unknown = set(bindings) - set(MAX_BINDINGS)
    if unknown:
        errors.append("bindings.json has unknown keys: %s" % ", ".join(sorted(unknown)))

    calls = []
    for name, limit in MAX_BINDINGS.items():
        section = bindings.get(name, {})
        if name == "on_open":
            if not isinstance(section, list):
                errors.append("bindings.json: on_open must be an array")
                continue
            items = [(name, i, call) for i, call in enumerate(section)]
        else:
            if not isinstance(section, dict):
                errors.append("bindings.json: events must be an object")
                continue
            items = [(name, key, call) for key, call in section.items()]
        if len(items) > limit:
            errors.append("bindings.json: %s has %d entries, the limit is %d"
                          % (name, len(items), limit))
        calls.extend(items)

    if not calls:
        warns.append("bindings.json is present but empty")

    targets = []
    for section, key, call in calls:
        where = "%s[%s]" % (section, key)
        if not isinstance(call, dict):
            errors.append("%s must be an object" % where)
            continue
        service = call.get("service")
        target = call.get("target")
        args = call.get("args")

        if not isinstance(service, str) or not service:
            errors.append("%s: service must be a non-empty string" % where)
        elif service not in capabilities:
            errors.append("%s: service %r is not declared in manifest.capabilities"
                          % (where, service))
        else:
            oks.append("%s: service %r is granted" % (where, service))

        if not isinstance(target, str) or not TARGET_RE.match(target or ""):
            errors.append("%s: target must be a top-level data name [A-Za-z0-9_]" % where)
        else:
            targets.append((where, target))

        if args is not None and not isinstance(args, dict):
            errors.append("%s: args must be an object" % where)

    # Rules 1 and 2, over the names the card actually reads.
    declared_states = set(STATE_RE.findall(card_code))
    read_names = set(DATA_READ_RE.findall(card_code))
    guarded = set(GUARD_RE.findall(card_code))
    target_names = {target for _, target in targets}
    referenced = read_names | guarded

    for name in sorted(referenced):
        if name not in data:
            errors.append(
                "page.card references %r but page.data.json has no such key — the first "
                "frame lowers before any reply, and a path into an absent name fails the "
                "WHOLE card ('unresolved or unsupported kit property'). Seed %r in "
                "page.data.json." % (name, name))
            continue
        if name in target_names and name not in guarded:
            errors.append(
                "page.card reads %r (a binding target) with no `when %s.is_ok { … }` guard — "
                "a failed call writes {is_ok:false,error:…} with no `data`, and the whole "
                "card fails to lower instead of the one line." % (name, name))
            continue
        if name in declared_states:
            oks.append("page.card: %r is declared, seeded%s"
                       % (name, " and guarded" if name in guarded else ""))
        else:
            oks.append("page.card: %r is seeded%s"
                       % (name, " and guarded" if name in guarded else ""))

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
