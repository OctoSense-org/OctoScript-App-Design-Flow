#!/usr/bin/env python3
"""Render the exact embedded L0 template with explicitly synthetic data.

This tests template realization and native pixels, not shell routing or chat.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import urllib.request

APP = Path(__file__).resolve().parents[1]
REPO = APP.parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8165)
    args = parser.parse_args()
    root = APP / '.local-state/glance-fixture'
    bundle = root / 'bundle'
    bundle.mkdir(parents=True, exist_ok=True)
    source = (APP / 'bundle/main.splash').read_text()
    card = json.loads(re.search(r'^let glance_source = (".*")$', source, re.M)[1])
    app_id = json.loads((APP / 'bundle/manifest.json').read_text())['id']
    (bundle / 'manifest.json').write_text(json.dumps({
        'schema': 1, 'id': app_id, 'name': 'Calendar card fixture',
        'version': '0.1.0', 'capabilities': [],
    }, indent=2) + '\n')
    (bundle / 'page.card').write_text(card)
    (bundle / 'page.data.json').write_text(json.dumps({
        'ev': {
            'title': 'Synthetic appointment', 'metric1_value': '2026-10-08',
            'metric2_value': '09:30', 'as_of': 'America/Los_Angeles',
            'subtitle': 'Fixture Studio',
            'summary': 'Synthetic capture only; no Google event was created.',
            'url1': f'app://{app_id}/event/fixture',
            'evidence_body': json.dumps({'connection': 'fixture-only', 'calendar': 'fixture', 'event': 'fixture'}),
        },
        'conversation': {'entries': []},
    }, indent=2) + '\n')
    shutil.copytree(REPO.parent / 'octoscript-makepad/components/l0', bundle / 'kit', dirs_exist_ok=True)
    endpoint = f'http://127.0.0.1:{args.port}/'
    running = False
    try:
        output = subprocess.check_output([
            str(REPO / 'tools/octo'), 'run', str(bundle), '--port', str(args.port),
            '--hidden', '--detach',
        ], text=True)
        assert 'ready: first frame drawn' in output
        running = True
        with urllib.request.urlopen(endpoint + 'snap', timeout=12) as response:
            snapshot = json.load(response)
        text = ' '.join(item.get('t', '') for item in snapshot['s'] if item['ty'] != 'Splash')
        for expected in ['Synthetic appointment', 'Open Calendar', 'America/Los_Angeles']:
            assert expected in text, expected
        with urllib.request.urlopen(endpoint + 'g?raw=1', timeout=12) as response:
            capture = response.read()
        assert capture.startswith(b'\x89PNG\r\n\x1a\n')
        (root / 'card.png').write_bytes(capture)
        log = (root / '.local-state/card-host.log').read_text()
        assert '"level":"L0","valid":true' in log
        assert '[E]' not in log and 'on_render closure failed' not in log
        receipt = {
            'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'template_sha256': hashlib.sha256(card.encode()).hexdigest(),
            'capture_sha256': hashlib.sha256(capture).hexdigest(),
            'surface': 'hidden native card-host, 412x860 logical app viewport',
            'data': 'explicit synthetic fixture', 'result': 'template and render pass',
            'not_verified': ['shell Glance route', 'live event binding', 'chat replies', 'phone keyboard'],
        }
        (root / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps(receipt, indent=2))
    finally:
        if running:
            with urllib.request.urlopen(endpoint + 'quit', timeout=12) as response:
                response.read()


if __name__ == '__main__':
    main()
