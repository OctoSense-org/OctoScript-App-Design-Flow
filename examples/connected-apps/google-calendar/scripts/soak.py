#!/usr/bin/env python3
"""Sustained native Calendar UX soak with signed install and synthetic provider.

Measures HTTP input-to-frame-submission round trips, not FPS or hardware delay.
No real credentials, Google traffic, model calls or physical approval are used.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request

APP = Path(__file__).resolve().parents[1]
APP_ID = 'org.octosense.samples.googlecalendar'
EVENT = 'event00001'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=Path, required=True)
    parser.add_argument('--cycles', type=int, default=36)
    parser.add_argument('--seconds', type=float, default=620)
    parser.add_argument('--out', type=Path, default=APP / '.local-state/soak-evidence')
    args = parser.parse_args()
    if args.cycles < 30 or args.seconds < 600:
        parser.error('Acceptance requires at least 30 cycles over at least 600 seconds')
    host = args.host.resolve()
    run = args.out / ('run-' + str(time.time_ns()))
    run.mkdir(parents=True)
    receipt = {'result': 'running', 'scope': 'macOS signed installed Calendar; synthetic provider',
               'source_sha256': digest(APP / 'bundle/main.splash'), 'binary_sha256': digest(host),
               'latency_scope': 'Makepad instrument HTTP input through macOS wait=1 applied-frame submission; not FPS, display completion or physical input latency',
               'cycles': [], 'rss': [], 'inputs': [], 'captures': {}, 'restarts': 0,
               'not_verified': ['Live Google', 'Android/iOS/Linux/Windows', 'Physical approval', 'Real model calls', 'Full-shell Glance soak']}
    child = log = endpoint = None
    launched = 0
    started = time.monotonic()

    def request(route, **query):
        before = time.monotonic()
        suffix = '?' + urllib.parse.urlencode(query) if query else ''
        result = json.load(urllib.request.urlopen(endpoint + route + suffix, timeout=15))
        elapsed = (time.monotonic() - before) * 1000
        if result.get('err'):
            raise AssertionError(result['err'])
        if route in ['/click', '/k', '/t', '/m']:
            receipt['inputs'].append({'route': route, 'kind': query.get('k'), 'ms': round(elapsed, 3), 'frame': result.get('f')})
        return result

    def rows():
        return [r for r in request('/snap')['s'] if r['ty'] != 'Splash' and r['r'][2] > 0 and r['r'][3] > 0]

    def wait(predicate, timeout=15):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            value = predicate()
            if value:
                return value
            time.sleep(.08)
        raise AssertionError('Native state did not settle')

    def row(text, kind='Button'):
        return next((r for r in rows() if r.get('t') == text and r['ty'] == kind), None)

    def click(text, kind='Button'):
        r = wait(lambda: row(text, kind)); x, y, w, h = r['r']
        request('/click', x=x + w / 2, y=y + h / 2, wait=1)

    def scroll(amount):
        request('/m', k='scroll', x=200, y=450, dy=amount, wait=1)

    def field(identifier, text):
        scroll(-10000)
        for _ in range(18):
            r = next((r for r in rows() if r.get('i') == identifier and r['ty'] == 'TextInput' and r['r'][3] >= 40), None)
            if r:
                x, y, w, h = r['r']; request('/click', x=x + w / 2, y=y + min(20, h / 2), wait=1)
                request('/k', k='press', c='KeyA', cmd=1, wait=1)
                request('/t', t=text, wait=1)
                wait(lambda: any(r.get('i') == identifier and (r.get('val') == text or r.get('t') == text) for r in rows()))
                return
            scroll(170)
        raise AssertionError('Input not reachable: ' + identifier)

    def shot(name):
        (run / (name + '.snapshot.json')).write_text(json.dumps(rows(), indent=2) + '\n')
        shutil.copyfile(request('/g')['png'], run / (name + '.png'))
        receipt['captures'][name + '.png'] = digest(run / (name + '.png'))

    def quit():
        nonlocal child, log, endpoint
        if child is None:
            return
        if child.poll() is None:
            try:
                request('/quit')
            except Exception:
                child.terminate()
        try:
            child.wait(timeout=12)
        except subprocess.TimeoutExpired:
            child.kill(); child.wait()
        log.close()
        child = log = endpoint = None

    def rss(cycle):
        value = subprocess.check_output(['ps', '-o', 'rss=', '-p', str(child.pid)], text=True).strip()
        receipt['rss'].append({'cycle': cycle, 'process': launched, 'elapsed_s': round(time.monotonic() - started, 3), 'kib': int(value)})

    with tempfile.TemporaryDirectory(prefix='calendar-soak-') as tmp:
        private = Path(tmp)
        profile = private / 'apps'
        provider = profile / '.host/acceptance-calendar/provider.json'
        inherited = {k: v for k, v in os.environ.items() if k not in ['MAKEPAD_APP_CONFIG', 'OCTOS_APP_CORE_DIR', 'OCTOS_APP_CORE_BIN']}
        env = {**inherited, 'MAKEPAD_HIDE_WINDOWS': '1', 'OCTOSENSE_HOME': str(private / 'home'), 'RINX_DATA_DIR': str(private / 'rinx')}

        def launch(first):
            nonlocal child, log, endpoint, launched
            launched += 1
            path = run / ('process-%02d.log' % launched)
            log = path.open('w')
            entry = '--install-bundle=' + str(APP / 'bundle') if first else '--installed-app=' + APP_ID
            child = subprocess.Popen([str(host), entry, '--app-data=' + str(profile), '--provider-fixture=calendar', '--remote'], env=env, stdout=log, stderr=log)
            def ready():
                if child.poll() is not None:
                    raise AssertionError('Owned host exited')
                return re.search(r'listening on (127\.0\.0\.1:\d+)', path.read_text())
            endpoint = 'http://' + wait(ready, 30)[1]
            wait(lambda: '"signed":true' in path.read_text())

        def state():
            return json.loads(provider.read_text())

        def event():
            return next(e for e in state()['events'] if e['id'] == EVENT)

        def writes():
            return sum(call['method'] in ['POST', 'PATCH', 'DELETE'] for call in state()['calls'])

        def draft():
            files = list(profile.rglob('draft.json'))
            assert len(files) == 1, 'Exactly one app draft should exist'
            return json.loads(files[0].read_text())

        def review(title):
            click('Review & Save')
            wait(lambda: row('Update Google Calendar event', 'Label'))
            wait(lambda: any(title in r.get('t', '') for r in rows()))

        def back_from_review():
            click('Back to editing')
            wait(lambda: not any(r.get('i') == 'connector_review_status' for r in rows()))

        def discard():
            scroll(10000)
            click('Discard local draft')
            wait(lambda: row('+ Event'))

        try:
            launch(True)
            click('Synthetic acceptance calendar · owner')
            current = event()['summary']
            wait(lambda: row(current, 'Label'))
            shot('00-initial-agenda')
            rss(0)
            interaction_start = time.monotonic()
            receipt['interaction_start_offset_s'] = round(interaction_start - started, 3)
            for cycle in range(1, args.cycles + 1):
                tick = time.monotonic()
                expected = 'Synthetic soak event %02d' % cycle
                notes = '\n'.join('Synthetic note %02d line %02d — draft retention and scrolling.' % (cycle, i) for i in range(1, 13))
                click(current, 'Label')
                wait(lambda: any(r.get('i') == 'event_title' and r.get('t') == current for r in rows()))
                scroll(180); scroll(-180)
                click('Chat')
                field('chat_entry', 'Unsent synthetic question %02d' % cycle)
                click('‹ Event')
                click('Edit')
                field('e_title', expected)
                field('e_place', 'Synthetic soak room %02d' % cycle)
                field('e_notes', notes)
                wait(lambda: draft().get('summary') == expected and draft().get('description') == notes)
                local = draft()
                assert local['event_id'] == EVENT and local['calendar'] == 'synthetic-calendar'
                assert local['summary'] == expected and local['description'] == notes
                assert local['start_date'] == '2026-10-08' and local['start_time'] == '09:00'
                before = writes()
                review(expected)
                if cycle in [1, 12, 24, args.cycles]:
                    shot('cycle-%02d-exact-review' % cycle)
                back_from_review()
                assert writes() == before and draft() == local, 'Cancel changed provider or draft'
                restarted = False
                if cycle % 9 == 0:
                    click('Keep draft'); quit(); launch(False)
                    wait(lambda: row(current, 'Label'))
                    click('Resume draft')
                    assert draft() == local, 'Cold restart changed draft identity or content'
                    restarted = True; receipt['restarts'] += 1
                outcome = 'cancel/discard'
                if cycle % 12 == 0:
                    remote = state(); changed = next(e for e in remote['events'] if e['id'] == EVENT)
                    changed['summary'] = 'Synthetic remote edit %02d' % cycle
                    changed['etag'] = '"synthetic-external-%02d"' % cycle
                    remote['revision'] += 1
                    temp = provider.with_suffix('.soak.tmp'); temp.write_text(json.dumps(remote)); temp.replace(provider)
                    review(expected); click('Approve & Save')
                    wait(lambda: any(r.get('i') == 'connector_review_status' and 'remote content changed' in r.get('t', '') for r in rows()))
                    assert not row('Approve & Save') and row('Back to editing')
                    assert writes() == before + 1 and event()['summary'] == changed['summary']
                    assert draft() == local
                    shot('cycle-%02d-conflict' % cycle)
                    back_from_review(); discard(); click('Refresh')
                    current = changed['summary']; wait(lambda: row(current, 'Label'))
                    outcome = 'conflict refused; local draft retained then explicitly discarded'
                elif cycle % 6 == 0:
                    prior_etag = event()['etag']
                    review(expected); click('Approve & Save')
                    wait(lambda: event()['summary'] == expected)
                    wait(lambda: not any(r.get('i') == 'connector_review_status' for r in rows()))
                    current = expected; wait(lambda: row(current, 'Label'))
                    stored = event()
                    assert stored['id'] == EVENT and stored['description'] == notes and stored['etag'] != prior_etag
                    assert writes() == before + 1
                    outcome = 'saved and read back exact event'
                else:
                    discard()
                rss(cycle)
                receipt['cycles'].append({'cycle': cycle, 'event_id': EVENT, 'draft_title': expected,
                                          'draft_sha256': hashlib.sha256(json.dumps(local, sort_keys=True).encode()).hexdigest(),
                                          'etag': local['etag'], 'outcome': outcome, 'cold_restart': restarted,
                                          'active_s': round(time.monotonic() - tick, 3)})
                (run / 'progress.json').write_text(json.dumps({'completed': cycle, 'total': args.cycles, 'elapsed_s': round(time.monotonic() - interaction_start, 1), 'latest_rss_kib': receipt['rss'][-1]['kib']}) + '\n')
                print('cycle %d/%d: %s' % (cycle, args.cycles, outcome), flush=True)
                # Keep exercising scroll dispatch during the paced soak rather
                # than leaving the process idle between semantic journeys.
                deadline = interaction_start + args.seconds * cycle / args.cycles
                direction = 1
                while time.monotonic() < deadline:
                    scroll(90 * direction); direction *= -1
                    time.sleep(min(.8, max(0, deadline - time.monotonic())))
            receipt['interaction_duration_s'] = round(time.monotonic() - interaction_start, 3)
            shot('99-final-agenda')
            receipt['provider_final_events'] = state()['events']
            receipt['provider_write_calls'] = [c for c in state()['calls'] if c['method'] in ['POST', 'PATCH', 'DELETE']]
            receipt['result'] = 'pass'
        except BaseException as error:
            receipt['result'] = 'fail'; receipt['error'] = str(error)
            if child and child.poll() is None:
                try:
                    shot('failure')
                except Exception as e:
                    receipt['capture_error'] = str(e)
            raise
        finally:
            quit()
            samples = sorted(item['ms'] for item in receipt['inputs'])
            if samples:
                receipt['input_latency_ms'] = {'count': len(samples), 'median': statistics.median(samples),
                                               'p95': samples[min(len(samples) - 1, int(len(samples) * .95))], 'max': max(samples)}
            receipt['elapsed_s'] = round(time.monotonic() - started, 3)
            receipt['cleanup'] = 'owned host processes stopped; temporary synthetic profile removed'
            (run / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print(json.dumps({'result': receipt['result'], 'evidence': str(run)}, indent=2), flush=True)


if __name__ == '__main__':
    main()
