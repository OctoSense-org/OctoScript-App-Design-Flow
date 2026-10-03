"""Drive model-authored apps through Android's real Studio instrument.

This operator harness writes requests and evidence only, never app source or
application data. A suite specifies native inputs and observable assertions.
"""
import importlib.util
import json
import sys
import time
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--runtime-root', type=Path, required=True, help='OctoSense checkout with Studio operator tools')
parser.add_argument('--serial', required=True)
parser.add_argument('--package', required=True, help='Dedicated Studio test package; production package refused')
parser.add_argument('--workspace', required=True, help='Absolute existing authoring workspace inside the test package files directory')
parser.add_argument('--suite', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True, help='New evidence directory')
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--allow-small-targets', action='store_true', help='Historical comparison mode: report small controls without failing the step')
args = parser.parse_args()
ROOT = args.runtime_root.resolve()

spec = importlib.util.spec_from_file_location('flow', ROOT / 'tools/studio-flow-device-test.py')
flow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flow)
# Imports define helpers only; no adb operation before the dry-run exit.
try:
    flow._probe.test_package(args.package)
    flow.safe_relative(args.workspace.lstrip('/'))
    allowed = (f'/data/data/{args.package}/files/', f'/data/user/0/{args.package}/files/')
    if not args.workspace.startswith(allowed):
        raise ValueError('workspace must belong to the dedicated test package')
except (ValueError, argparse.ArgumentTypeError, flow.ProbeError) as error:
    parser.error(str(error))
suite_path = args.suite
suite = json.loads(suite_path.read_text())
out = args.output
if args.dry_run:
    print(json.dumps({'family': suite['family'], 'steps': len(suite['steps']),
                     'mode': 'validation only; no phone access or source writes'}))
    sys.exit(0)
d = flow.Device('adb', args.serial, args.package)
out.mkdir(parents=True, exist_ok=False)
studio = flow.Studio(d, args.workspace, out, 35)
report = {'family': suite['family'], 'steps': []}
snapshot = {}

def capture(index, label):
    global snapshot
    compact = studio.call('studio.inspect', {'instance_id': studio.instance})
    full = flow.full_inspection(d, studio.workspace, studio.instance, compact)
    snapshot = full['snapshot']
    stem = f'{index:02d}-{label}'
    (out / (stem + '.json')).write_text(json.dumps(full, indent=2))
    (out / (stem + '.png')).write_bytes(d.read(studio.workspace + '/' + full['path'], 5*1024*1024))
    return {'png': stem + '.png', 'checks': snapshot.get('checks'), 'settled': full.get('settled')}

try:
    # The operator unlocks the test device before running this helper.
    studio.start()
    report['admission'] = studio.call('studio.bundle_check', {'bundle_path': 'card-templates/' + suite['family'] + '/bundle'})
    studio.open(bundle_path='card-templates/' + suite['family'] + '/bundle')
    for index, step in enumerate(suite['steps']):
        result = {'label': step['label'], 'input': step}
        try:
            if step.get('action') in ('tap', 'text', 'scroll'):
                candidates = [n for n in flow.widgets(snapshot) if n.get('enabled') and
                    (flow.node_text(n) == step['target'] or n.get('id') == step['target'] or n.get('selector') == step['target'])]
                if 'occurrence' in step:
                    node = candidates[step['occurrence']]
                elif len(candidates) == 1:
                    node = candidates[0]
                else:
                    raise RuntimeError(f"Target {step['target']!r} matches {len(candidates)} enabled nodes")
                result['target_rect'] = node.get('rect')
                result['target_selector'] = node.get('selector')
                if step['action'] == 'scroll':
                    studio.call('studio.input', {'instance_id': studio.instance,
                        'widget_id': node.get('selector', node['id']),
                        'action': 'scroll', 'delta_y': step['delta_y']})
                else:
                    studio.input(node, step['action'], step.get('text'))
            if step.get('delay_ms'):
                time.sleep(step['delay_ms']/1000)
            result.update(capture(index, step['label']))
            if step.get('capture_android'):
                android_name = f'{index:02d}-{step["label"]}-android.png'
                (out / android_name).write_bytes(d.call('exec-out', 'screencap', '-p').stdout)
                result['android_screenshot'] = android_name
            result['small_button_targets'] = [
                {'selector': n.get('selector'), 'text': flow.node_text(n), 'rect': n.get('rect')}
                for n in flow.widgets(snapshot)
                if n.get('enabled') and 'Button' in str(n.get('type'))
                and isinstance(n.get('rect'), list) and min(n['rect'][2:]) < 44
            ]
            texts = [flow.node_text(n) for n in flow.widgets(snapshot)]
            assertions = []
            for expected in step.get('contains', []):
                assertions.append({'contains': expected, 'pass': any(expected in text for text in texts)})
            for excluded in step.get('excludes', []):
                assertions.append({'excludes': excluded, 'pass': all(excluded not in text for text in texts)})
            for forbidden in step.get('no_enabled_button_text', []):
                matches = [n for n in flow.widgets(snapshot) if n.get('enabled') and 'Button' in str(n.get('type')) and forbidden in flow.node_text(n)]
                assertions.append({'no_enabled_button_text': forbidden, 'pass': not matches})
            if 'input_value' in step:
                values = [n.get('value') for n in flow.widgets(snapshot) if 'TextInput' in str(n.get('type'))]
                assertions.append({'input_value': step['input_value'], 'pass': step['input_value'] in values})
            result['assertions'] = assertions
            result['behavior_pass'] = all(a['pass'] for a in assertions)
            result['pass'] = all(a['pass'] for a in assertions) and result.get('checks', {}).get('pass') is True and (args.allow_small_targets or not result['small_button_targets'])
        except Exception as error:
            result['pass'] = False
            result['error'] = str(error)
        report['steps'].append(result)
        (out / 'report.json').write_text(json.dumps(report, indent=2))
        print(json.dumps(result), flush=True)
finally:
    try:
        studio.close()
        report['closed'] = True
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2))

# Final collection checks reject sub-44 targets. Opt in to historical comparison semantics explicitly.
sys.exit(0 if all(step.get('pass') is True for step in report['steps']) else 1)
