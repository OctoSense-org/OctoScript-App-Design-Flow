#!/usr/bin/env python3
"""Stage a complete frozen Android-model snapshot; no device access or source edits.

Requires all six families and exact successful mutation replay. Evidence and
acceptance are reviewed separately; import never awards a quality score.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('authorship', ROOT / 'validate-model-authorship.py')
authorship = importlib.util.module_from_spec(spec)
spec.loader.exec_module(authorship)
FAMILIES = ('mail', 'calendar', 'news', 'finance', 'photo', 'youtube')
EXPECTED = {'card-templates/DESIGN.md'} | {
    f'card-templates/{family}/{name}' for family in FAMILIES
    for name in ('glance.card', 'glance.data.json', 'bundle/main.splash', 'bundle/manifest.json')}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def complete_replay(result):
    return all(row['status'] == 'exact_match' for rows in result['cases'].values() for row in rows)


def import_snapshot(source, base_case, turn_dirs, model, round_number, archive_root=ROOT, dry_run=True):
    archive_root = archive_root.resolve()
    base_case = Path(base_case)
    if model not in ('deepseek', 'minimax') or round_number < 1:
        raise ValueError('model and positive round number required')
    permitted_bases = {Path('collection')} if model == 'deepseek' else set()
    permitted_bases.add(Path('attempts') / f'{model}-r3')
    if base_case not in permitted_bases and base_case.parts[:2] != ('continuations', model):
        raise ValueError('base case must belong to the same model; never borrow another model history')
    base = archive_root / base_case
    if not complete_replay(authorship.validate(archive_root, [base_case])):
        raise ValueError('base case must replay exactly before continuation')
    if source.is_symlink() or any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('source must not contain symlinks')
    receipt = read_json(source / 'source-receipt.json')
    paths = [entry['path'] for entry in receipt]
    actual = {str(p.relative_to(source)) for p in (source / 'card-templates').rglob('*') if p.is_file()}
    if len(paths) != 25 or set(paths) != EXPECTED or actual != EXPECTED:
        raise ValueError('freeze all 25 expected files; keep incomplete snapshots outside the archive')
    for entry in receipt:
        path = source / entry['path']
        if sha(path) != entry['sha256'] or path.stat().st_size != entry['bytes']:
            raise ValueError('source bytes differ from source receipt')
    calls = read_json(base / 'model-mutations.json')['calls'][:]
    identities = {(c['turn'], c['tool_call_id']) for c in calls}
    known_turns = {c['turn'] for c in calls}
    records = []
    interruptions = {}
    for turn_dir in turn_dirs:
        turn = turn_dir.name
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', turn) or not turn.startswith(model + '-') or turn in known_turns:
            raise ValueError('turn names must be distinct portable labels in chronological order')
        known_turns.add(turn)
        transcript = turn_dir / 'transcript.json'
        data = read_json(transcript)
        for call in data['tool_calls']:
            if call.get('success') is not True or call['name'] not in ('write_file', 'edit_file', 'apply_patch'):
                continue
            args = call['arguments']
            allowed = {'write_file': {'path', 'content'}, 'edit_file': {'path', 'old_string', 'new_string'}, 'apply_patch': {'patch'}}[call['name']]
            if call.get('input_complete') is not True or set(args) != allowed:
                raise ValueError('mutation arguments must be complete and use the reviewed schema')
            filtered = dict(turn=turn, tool_call_id=call['tool_call_id'], name=call['name'],
                            arguments=args, input_complete=True, success=True)
            targets = authorship.targets(filtered)
            if not targets or any(path not in EXPECTED for path in targets):
                raise ValueError('mutation outside six-family source; review before archiving')
            identity = (turn, call['tool_call_id'])
            if identity in identities:
                raise ValueError('duplicate mutation identity')
            identities.add(identity)
            calls.append(filtered)
        timing = turn_dir / 'timing.json'
        records.append(dict(turn=turn, transcript_sha256=sha(transcript),
                            tool_calls=len(data['tool_calls']),
                            successful_tool_calls=sum(c.get('success') is True for c in data['tool_calls']),
                            failed_tool_calls=sum(c.get('success') is False for c in data['tool_calls']),
                            elapsed_seconds=read_json(timing).get('elapsed_seconds') if timing.exists() else None,
                            assistant_finals=len(data.get('assistant_finals', [])),
                            turn_errors=len(data.get('turn_errors', []))))
        interruption = turn_dir / 'operator-interruption.json'
        record = records[-1]
        record['completion'] = 'assistant_final_observed' if record['assistant_finals'] else 'no_assistant_final_recorded'
        if interruption.exists():
            if interruption.is_symlink() or interruption.stat().st_size > 65536:
                raise ValueError('interruption receipt must be a bounded regular file')
            observed = read_json(interruption)
            if (observed.get('operator_interrupted') is not True
                    or observed.get('recorded_tool_calls') != record['tool_calls']
                    or observed.get('assistant_finals') != record['assistant_finals']):
                raise ValueError('interruption receipt counts must match the recorded transcript')
            for field in ('timestamp_utc', 'reason', 'method'):
                if not isinstance(observed.get(field), str) or not observed[field]:
                    raise ValueError('interruption receipt needs timestamp, reason and method')
            if re.search(r'/Users/|/private/|/tmp/|/data/(?:data|user)/|(?i:bearer\s+\S+|sk-[a-z0-9]{20,})', interruption.read_text()):
                raise ValueError('interruption receipt requires privacy review')
            relative = f'turn-evidence/{turn}/operator-interruption.json'
            interruptions[relative] = interruption
            record.update(completion='operator_interrupted', operator_interruption=relative,
                          operator_interruption_sha256=sha(interruption))
    mutations = {'scope': 'Successful recorded Android model file mutations only; no reasoning or tool outputs', 'calls': calls}
    # Refuse obvious private paths/credentials; an operator must still review all
    # retained source arguments. This is a guard, not a general secret detector.
    if re.search(r'/Users/|/private/|/tmp/|/data/(?:data|user)/|(?i:bearer\s+\S+|sk-[a-z0-9]{20,})', json.dumps(mutations)):
        raise ValueError('mutation archive requires privacy review; never redact source to force replay')
    destination = archive_root / 'continuations' / model / f'turn-{round_number}'
    if destination.exists():
        raise FileExistsError('snapshot exists; choose a new immutable revision')
    if not destination.resolve().is_relative_to(archive_root) or any(p.is_symlink() for p in destination.parents if p.is_relative_to(archive_root)):
        raise ValueError('destination must remain inside archive without symlinks')
    with tempfile.TemporaryDirectory(prefix='model-snapshot-') as temporary:
        stage = Path(temporary) / 'snapshot'
        stage.mkdir()
        for entry in receipt:
            target = stage / entry['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / entry['path'], target)
        shutil.copyfile(source / 'source-receipt.json', stage / 'source-receipt.json')
        write_json(stage / 'model-mutations.json', mutations)
        result = authorship.validate(Path(temporary), [Path('snapshot')])
        if not complete_replay(result):
            raise ValueError('continued mutation history does not exactly reproduce frozen source')
        write_json(stage / 'model-authorship-validation.json', result)
        for relative, original in interruptions.items():
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, target)
        write_json(stage / 'generation-record.json', {
            'status': 'source_replayed_native_and_visual_review_pending',
            'model': model, 'model_identity_scope': 'operator attribution, not provider attestation',
            'phase': 'six-family continuation; not an equal-budget benchmark',
            'base_case': str(base.relative_to(archive_root)),
            'base_receipt_sha256': sha(base / 'source-receipt.json'),
            'base_mutations_sha256': sha(base / 'model-mutations.json'),
            'source_receipt_sha256': sha(stage / 'source-receipt.json'),
            'files': 25, 'source_modified_on_import': False,
            'new_turns': records,
            'timing_scope': 'operator polling interval; not inference latency; null means unrecorded'})
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(stage, destination)
    return {'mode': 'validated_only' if dry_run else 'imported_for_review',
            'case': str(destination.relative_to(archive_root)), 'exact_files': 25,
            'native_and_visual_review': 'pending; no score awarded'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True, help='Operator-frozen source with source-receipt.json')
    parser.add_argument('--base-case', type=Path, required=True, help='Existing archive-relative snapshot with full mutation history')
    parser.add_argument('--turn-dir', type=Path, action='append', required=True, help='New sanitized transcript directory, repeat chronologically')
    parser.add_argument('--model', choices=('deepseek', 'minimax'), required=True)
    parser.add_argument('--round', type=int, required=True)
    parser.add_argument('--frozen-source', action='store_true', required=True, help='Operator confirms source is frozen, not an active partial turn')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        result = import_snapshot(args.source_root, args.base_case, args.turn_dir, args.model, args.round, dry_run=args.dry_run)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'Import refused: {error}\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
