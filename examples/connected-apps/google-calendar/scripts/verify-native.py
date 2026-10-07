#!/usr/bin/env python3
"""Exercise the exact Calendar bundle through an owned hidden Makepad process.
No OAuth account, fake service reply or Google write is created by this test.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import urllib.parse
import urllib.request

APP = Path(__file__).resolve().parents[1]
REPO = APP.parents[2]
APP_ID = 'org.octosense.samples.googlecalendar'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8164)
    args = parser.parse_args()
    root = APP / '.local-state' / 'native-check'
    evidence = APP / '.local-state' / 'native-evidence'
    evidence.mkdir(parents=True, exist_ok=True)
    root.mkdir(parents=True, exist_ok=True)
    jail = root / APP_ID
    # This is the test's own jail. A repeat run starts from a clean local draft.
    if jail.exists():
        for name in ['draft.json', 'selection.json', 'publications.json']:
            (jail / name).unlink(missing_ok=True)
    endpoint = f'http://127.0.0.1:{args.port}/'
    cases = []
    running = False

    def request(route, **params):
        with urllib.request.urlopen(endpoint + route + '?' + urllib.parse.urlencode(params), timeout=12) as response:
            return json.load(response)

    def launch():
        nonlocal running
        output = subprocess.check_output([str(REPO / 'tools/octo'), 'run', str(APP / 'bundle'), '--port', str(args.port), '--hidden', '--detach', '--app-data', str(root)], text=True)
        assert 'ready: first frame drawn' in output
        running = True
        wait(lambda: any('no service answers' in item.get('t', '') for item in widgets()))

    def wait(predicate):
        deadline = time.monotonic() + 6
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(.05)
        raise AssertionError('Native state did not settle')

    def widgets():
        return [item for item in request('snap')['s'] if item['ty'] != 'Splash' and item['r'][2] > 0 and item['r'][3] > 0]

    def item_by_id(identifier):
        return next((item for item in widgets() if item['i'] == identifier), None)

    def click(item):
        x, y, width, height = item['r']
        assert height >= 40, (item.get('t'), item['r'])
        assert request('click', x=x + width / 2, y=y + height / 2, wait=1).get('ok') == 1

    def button(text):
        item = next(item for item in widgets() if item['ty'] == 'Button' and item.get('t') == text)
        click(item)

    def field(identifier, text):
        for _ in range(12):
            item = item_by_id(identifier)
            if item and item['r'][3] >= 40:
                click(item)
                request('k', k='press', c='KeyA', cmd=1, wait=1)
                request('t', t=text, wait=1)
                wait(lambda: item_by_id(identifier).get('val') == text)
                return
            request('m', k='scroll', x=200, y=500, dy=190, wait=1)
        raise AssertionError(f'{identifier} could not be reached by scrolling')

    def capture(name):
        with urllib.request.urlopen(endpoint + 'g?raw=1', timeout=12) as response:
            png = response.read()
        assert png.startswith(b'\x89PNG\r\n\x1a\n')
        (evidence / name).write_bytes(png)
        return hashlib.sha256(png).hexdigest()

    def quit():
        nonlocal running
        request('quit')
        running = False
        time.sleep(.1)

    try:
        launch()
        cases.append({'case': 'empty and unavailable auth', 'result': 'pass', 'capture': '01-empty.png', 'sha256': capture('01-empty.png')})
        button('+ Event')
        field('e_title', 'Synthetic appointment — design review')
        field('e_date', '2026-10-08')
        field('e_time', '09:30')
        field('e_end_date', '2026-10-08')
        field('e_end_time', '10:15')
        field('e_zone', 'America/Los_Angeles')
        field('e_place', 'Fixture Studio, second floor')
        field('e_notes', 'Synthetic test only.\nBring the annotated calendar draft.')
        wait(lambda: (jail / 'draft.json').exists() and json.loads((jail / 'draft.json').read_text()).get('description') == 'Synthetic test only.\nBring the annotated calendar draft.')
        draft = json.loads((jail / 'draft.json').read_text())
        assert draft['summary'] == 'Synthetic appointment — design review'
        assert draft['start_time'] == '09:30' and draft['end_time'] == '10:15'
        cases.append({'case': 'all editors reachable; durable native input', 'result': 'pass', 'capture': '02-draft-notes.png', 'sha256': capture('02-draft-notes.png')})
        button('Keep draft')
        button('Resume draft')
        button('Review & Save')
        wait(lambda: any('connect Google and choose a calendar' in item.get('t', '') for item in widgets()))
        cases.append({'case': 'review without account retains draft and explains next step', 'result': 'pass', 'capture': '03-review-needs-account.png', 'sha256': capture('03-review-needs-account.png')})
        button('Timed event')
        wait(lambda: json.loads((jail / 'draft.json').read_text())['all_day'])
        assert not item_by_id('e_time')
        button('Keep draft')
        quit()
        launch()
        button('Resume draft')
        assert item_by_id('e_title')['val'] == 'Synthetic appointment — design review'
        assert any(item.get('t') == 'All day ✓' for item in widgets())
        cases.append({'case': 'restart restores exact draft and all-day choice', 'result': 'pass', 'capture': '04-restored-draft.png', 'sha256': capture('04-restored-draft.png')})
        button('Keep draft')
        button('Account')
        button('Connect Google')
        wait(lambda: any('no service answers' in item.get('t', '') for item in widgets()))
        cases.append({'case': 'connect button handles unavailable host', 'result': 'pass', 'capture': '05-unavailable-account.png', 'sha256': capture('05-unavailable-account.png')})
        button('Back to agenda')
        button('Calendars')
        assert any('Connect Google to list' in item.get('t', '') for item in widgets())
        button('Back to agenda')
        log = (APP / '.local-state' / 'card-host.log').read_text()
        assert '[E]' not in log and 'on_render closure failed' not in log and 'callback error' not in log
        source_hash = hashlib.sha256((APP / 'bundle/main.splash').read_bytes()).hexdigest()
        manifest = json.loads((APP / 'bundle/manifest.json').read_text()); manifest.pop('integrity', None)
        hub = REPO.parent / 'OctoSense-App-Hub'
        runtime = REPO.parent / 'makepad'
        receipt = {'source_sha256': source_hash, 'manifest_contract_sha256': hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(), 'card_host_sha256': hashlib.sha256((hub / 'target/release/card-host').read_bytes()).hexdigest(), 'hub_revision': subprocess.check_output(['git','rev-parse','HEAD'],cwd=hub,text=True).strip(), 'makepad_revision': subprocess.check_output(['git','rev-parse','HEAD'],cwd=runtime,text=True).strip(), 'surface': 'hidden card-host native instrument on macOS', 'data': 'synthetic local draft; no provider connection', 'authored_and_driven_by': 'Codex calendar sub-agent', 'cases': cases, 'not_verified': ['Live OAuth', 'Google API read/write', 'Host review approval', 'ETag conflict UI', 'Glance route and chat', 'Android keyboard and lifecycle', 'Windows and Linux'], 'cleanup': 'owned process quit'}
        (evidence / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps({'passed': len(cases), 'source_sha256': source_hash, 'evidence': str(evidence)}, indent=2))
    finally:
        if running:
            quit()


if __name__ == '__main__':
    main()
