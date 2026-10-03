#!/usr/bin/env python3
"""Replay archived successful Android mutations in memory; never edit model source.

Uses the independent operator check's last-write/exact-edit method against the
portable mutation archive. The original operator result retains transcript IDs
and hashes; this helper needs no provider profile, device or original transcript.
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


def validate(root, case_dirs=None):
    result = {'method': 'last successful write plus unique exact edits; UTF-8 byte comparison',
              'scope': 'Archived model mutations only; no absence-of-intervention claim', 'cases': {}}
    folders = [root / path for path in case_dirs] if case_dirs else [root / 'attempts' / name for name in ('deepseek-r3', 'minimax-r3')]
    for folder in folders:
        name = folder.name
        calls = json.loads((folder / 'model-mutations.json').read_text())['calls']
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
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('receipt path must stay inside the archived attempt')
            ops = [c for c in calls if c.get('success') is True and path in targets(c)]
            writes = [i for i, c in enumerate(ops) if c['name'] == 'write_file']
            row = {'path': path, 'status': 'unverified'}
            rows.append(row)
            if not writes:
                row['reason'] = 'no successful base write'
                continue
            tail = ops[writes[-1]:]
            content = tail[0]['arguments'].get('content')
            if not isinstance(content, str):
                row['reason'] = 'base write content is incomplete'
                continue
            for call in tail[1:]:
                args = call['arguments']
                old, new = args.get('old_string'), args.get('new_string')
                if (call['name'] != 'edit_file' or not isinstance(old, str) or not old
                        or not isinstance(new, str) or content.count(old) != 1):
                    row['reason'] = 'applicable patch or ambiguous/incomplete edit; no guessing'
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
