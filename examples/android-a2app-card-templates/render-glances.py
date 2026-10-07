#!/usr/bin/env python3
"""Render unchanged model L0 cards through the Android Studio test action.

Copies source bytes into fresh test-package scratch directories, captures actual
renderer output, and records hashes. Never writes the model source, provider
configuration or production package. The parameterized helper rendered all six
archived families on the Android test device; see collection/evidence/.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import time
import uuid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-root', type=Path, required=True)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--package', required=True)
    parser.add_argument('--workspace', required=True, help='Existing authoring workspace inside the test package files directory')
    parser.add_argument('--output', type=Path, required=True, help='New evidence directory')
    parser.add_argument('--families', nargs='+', choices=['mail', 'calendar', 'news', 'finance', 'photo', 'youtube'], required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('studio_probe', args.runtime_root / 'tools/studio-device-probe.py')
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    try:
        probe.test_package(args.package)
        if not args.workspace.startswith((f'/data/user/0/{args.package}/files/', f'/data/data/{args.package}/files/')):
            raise ValueError('workspace must belong to the dedicated test package')
        if any(part in ('', '.', '..') for part in args.workspace.lstrip('/').split('/')) or '\\' in args.workspace:
            raise ValueError('invalid workspace components')
    except (ValueError, argparse.ArgumentTypeError) as error:
        parser.error(str(error))
    if args.dry_run:
        print(json.dumps({'families': args.families, 'mode': 'validation only; no phone access'}))
        return 0
    args.output.mkdir(parents=True, exist_ok=False)
    device = probe.Device('adb', args.serial, args.package)
    report = []
    try:
        for family in args.families:
            remote = args.workspace + '/review-render-' + str(uuid.uuid4())
            record = {'family': family, 'source_sha256': {}}
            try:
                device.stop()
                device.private('umask 077; mkdir -p ' + shlex.quote(remote))
                for name, limit in [('glance.card', 16384), ('glance.data.json', 32768)]:
                    raw = device.read(args.workspace + '/card-templates/' + family + '/' + name, limit + 1)
                    if raw is None or len(raw) > limit:
                        raise RuntimeError(f'missing or oversized {family}/{name}')
                    record['source_sha256'][name] = hashlib.sha256(raw).hexdigest()
                    device.write(remote + '/' + name, raw)
                request = {'workspace': remote, 'source_path': 'glance.card', 'data_path': 'glance.data.json'}
                device.write(remote + '/spec.json', json.dumps(request).encode())
                # The authorized operator unlocks and foregrounds the test device.
                device.launch(remote + '/spec.json')
                result = None
                started = time.monotonic()
                while time.monotonic() - started < 35:
                    raw = device.read(remote + '/studio-result.json', 1048576)
                    if raw:
                        try:
                            result = json.loads(raw)
                            break
                        except json.JSONDecodeError:
                            pass
                    time.sleep(.2)
                record['reply'] = result
                if not isinstance(result, dict) or result.get('ok') is not True:
                    raise RuntimeError('render failed or timed out; see reply')
                data = result['data']
                name = data.get('path', '')
                if '/' in name or '\\' in name or not name.endswith('.png'):
                    raise RuntimeError('unexpected render path')
                png = device.read(remote + '/' + name, 5242880)
                if png is None:
                    raise RuntimeError('render output missing')
                metadata = probe.png_metadata(png)
                if (metadata['width'], metadata['height']) != (data['width'], data['height']):
                    raise RuntimeError('PNG dimensions differ from reply')
                (args.output / (family + '.png')).write_bytes(png)
                record.update(png=family + '.png', png_sha256=hashlib.sha256(png).hexdigest(), pass_render=True)
            except Exception as error:
                record.update(pass_render=False, error=str(error))
            report.append(record)
            (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(record), flush=True)
    finally:
        device.stop()
    return 0 if all(r['pass_render'] for r in report) else 1


if __name__ == '__main__':
    raise SystemExit(main())
