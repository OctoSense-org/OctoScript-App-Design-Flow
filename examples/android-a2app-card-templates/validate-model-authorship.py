#!/usr/bin/env python3
"""Replay archived successful Android mutations in memory; never edit model source.

Replays complete successful writes, unique exact edits and the verified Android
kernel's first-forward exact patch subset. See pinned-apply-patch-semantics.json
for source/binary linkage. No provider profile, device or original transcript is needed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def targets(call):
    args = call['arguments']
    if call['name'] in ('write_file', 'edit_file'):
        return [args.get('path')]
    return re.findall(r'^\*\*\* (?:Update|Add|Delete) File: (.+)$', args.get('patch', ''), re.M)


def safe_source_path(path):
    return (isinstance(path, str) and path.startswith('card-templates/')
            and all(part not in ('', '.', '..') for part in path.split('/'))
            and '\\' not in path and '\x00' not in path)


def parse_exact_patch(patch):
    """Only Update File blocks with bare @@ hunks; reject all extended syntax."""
    if not isinstance(patch, str) or '\r' in patch:
        raise ValueError('patch must use literal LF lines')
    lines = patch.split('\n')
    if lines[-1] == '':
        lines.pop()
    if not lines or lines[0] != '*** Begin Patch' or lines[-1] != '*** End Patch':
        raise ValueError('unsupported patch envelope')
    files = {}
    index = 1
    while index < len(lines) - 1:
        if not lines[index].startswith('*** Update File: '):
            raise ValueError('only Update File is supported; no add/delete/move commands')
        path = lines[index][len('*** Update File: '):]
        if not safe_source_path(path) or path in files:
            raise ValueError('unsafe or duplicate patch path')
        index += 1
        hunks = []
        while index < len(lines) - 1 and not lines[index].startswith('*** Update File: '):
            if lines[index] != '@@':
                raise ValueError('only bare @@ exact-context hunks are supported')
            index += 1
            old, new = [], []
            while index < len(lines) - 1 and lines[index] != '@@' and not lines[index].startswith('*** '):
                line = lines[index]
                if not line or line[0] not in ' +-':
                    raise ValueError('every hunk line needs an explicit context/add/remove prefix')
                if line[0] in ' -':
                    old.append(line[1:] + '\n')
                if line[0] in ' +':
                    new.append(line[1:] + '\n')
                index += 1
            if not old:
                raise ValueError('hunk requires nonempty exact old context')
            hunks.append((old, new))
        if not hunks:
            raise ValueError('empty update block')
        files[path] = hunks
    if not files:
        raise ValueError('empty patch')
    return files


def apply_exact_patch(content, patch, path):
    """Replay the verified Android kernel's first-forward exact-match subset.

    See pinned-apply-patch-semantics.json: binary/APK/build linkage identifies
    kernel056173e. Its first trim_end match wins. We reject that choice unless
    every old line is byte-exact; never backtrack to a later exact occurrence.
    Context-only hunks advance the same cursor without changing source bytes.
    """
    files = parse_exact_patch(patch)
    if path not in files:
        raise ValueError('patch does not target this file')
    if not content.endswith('\n') or '\r' in content:
        raise ValueError('exact patch subset requires LF source with final newline')
    hunks = files[path]
    if len(hunks) > 128:
        raise ValueError('exact patch replay exceeds supported hunk limit')
    lines = [line + '\n' for line in content.split('\n')[:-1]]
    # Rust str::trim_end uses Unicode White_Space. Used solely to locate the
    # runtime's first candidate; a non-exact candidate is rejected, not applied.
    whitespace = ' \t\n\r\v\f\x85\xa0\u1680' + ''.join(chr(c) for c in range(0x2000, 0x200b)) + '\u2028\u2029\u202f\u205f\u3000'
    cursor = 0
    for old, new in hunks:
        canonical = next((pos for pos in range(cursor, len(lines) - len(old) + 1)
                          if all(a.rstrip(whitespace) == b.rstrip(whitespace)
                                 for a, b in zip(lines[pos:pos + len(old)], old))), None)
        if canonical is None:
            raise ValueError('missing exact context or out-of-order hunks; no fuzzy matching')
        if lines[canonical:canonical + len(old)] != old:
            raise ValueError('pinned first-forward choice is not byte-exact; no fuzzy matching or later-match fallback')
        lines = lines[:canonical] + new + lines[canonical + len(old):]
        cursor = canonical + len(new)
    return ''.join(lines) if lines else '\n'


def validate(root, case_dirs=None):
    result = {'method': 'last successful write plus unique exact edits/pinned first-forward exact patch replay; UTF-8 byte comparison',
              'scope': 'Archived model mutations only; no absence-of-intervention claim', 'cases': {}}
    root = root.resolve()
    folders = [root / path for path in case_dirs] if case_dirs else [root / 'attempts' / name for name in ('deepseek-r3', 'minimax-r3')]
    for folder in folders:
        if not folder.resolve().is_relative_to(root):
            raise ValueError('case directory must stay inside the archive root')
        if any(p.is_symlink() for p in [folder, *folder.parents] if p.is_relative_to(root)):
            raise ValueError('case directories must not be symlinks')
        if any(p.is_symlink() for p in folder.rglob('*')):
            raise ValueError('archived inputs must not contain symlinks')
        name = folder.name if sum(f.name == folder.name for f in folders) == 1 else str(folder.relative_to(root))
        calls = json.loads((folder / 'model-mutations.json').read_text())['calls']
        for call in calls:
            if call.get('success') is True and any(not safe_source_path(path) for path in targets(call)):
                raise ValueError('mutation path must stay inside card-templates')
        receipt = json.loads((folder / 'source-receipt.json').read_text())
        if not receipt:
            raise ValueError('source receipt must contain at least one file')
        recorded = {entry['path'] for entry in receipt}
        actual = {str(f.relative_to(folder)) for f in (folder / 'card-templates').rglob('*') if f.is_file()}
        if len(recorded) != len(receipt) or recorded != actual:
            raise ValueError('source receipt has duplicate, missing or extra files')
        rows = []
        for entry in receipt:
            path = entry['path']
            relative = Path(path)
            if relative.is_absolute() or '..' in relative.parts or relative.parts[0] != 'card-templates':
                raise ValueError('receipt path must stay inside the archived attempt')
            ops = [c for c in calls if c.get('success') is True and path in targets(c)]
            writes = [i for i, c in enumerate(ops) if c['name'] == 'write_file']
            row = {'path': path, 'status': 'unverified'}
            rows.append(row)
            if not writes:
                row['reason'] = 'no successful base write'
                continue
            tail = ops[writes[-1]:]
            if any(call.get('input_complete') is not True for call in tail):
                row['reason'] = 'contributing mutation arguments are not recorded complete'
                continue
            content = tail[0]['arguments'].get('content')
            if not isinstance(content, str):
                row['reason'] = 'base write content is incomplete'
                continue
            for call in tail[1:]:
                args = call['arguments']
                if call['name'] == 'apply_patch':
                    try:
                        content = apply_exact_patch(content, args.get('patch'), path)
                    except ValueError as error:
                        row['reason'] = str(error)
                        break
                else:
                    old, new = args.get('old_string'), args.get('new_string')
                    if (call['name'] != 'edit_file' or not isinstance(old, str) or not old
                            or not isinstance(new, str) or content.count(old) != 1):
                        row['reason'] = 'ambiguous/incomplete edit; no guessing'
                        break
                    content = content.replace(old, new, 1)
            if 'reason' in row:
                continue
            actual = (folder / relative).read_bytes()
            replay = content.encode('utf-8')
            row.update(sha256=hashlib.sha256(actual).hexdigest(), bytes=len(actual),
                       mutations=[c['tool_call_id'] for c in tail])
            if re.search(r'\[[^\]\n]*redact[^\]\n]*\]', content, re.I):
                row['reason'] = 'redacted argument cannot prove original bytes'
            elif actual == replay and row['sha256'] == entry['sha256'] and len(actual) == entry['bytes']:
                row['status'] = 'exact_match'
                if path.endswith('manifest.json'):
                    value = json.loads(content).get('integrity', {}).get('bundle_blake3')
                    row.update(integrity_placeholder=value == '0' * 64,
                               real_bundle_integrity_verified=False, publisher_signing_verified=False)
            else:
                row.update(status='mismatch', reason='no newline/whitespace normalization allowed')
        result['cases'][name] = rows
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--case-dir', action='append', type=Path, help='Relative case directory with model-mutations.json and source-receipt.json; repeat for multiple cases')
    args = parser.parse_args()
    result = validate(args.root, args.case_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if all(r['status'] == 'exact_match' for rows in result['cases'].values() for r in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())
