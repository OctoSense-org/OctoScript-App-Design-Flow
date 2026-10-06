#!/usr/bin/env python3
"""Signed installed Calendar UI + real host services + explicit synthetic provider.

Requires connected-app-host built with the non-default acceptance-fixtures
feature. No real Google account, network request or physical approval is used.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request

APP = Path(__file__).resolve().parents[1]
APP_ID = 'org.octosense.samples.googlecalendar'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=APP / '.local-state/installed-evidence')
    args = parser.parse_args()
    host = args.host.resolve()
    run = args.out / ('run-' + str(time.time_ns()))
    run.mkdir(parents=True)
    receipt = {'result': 'running', 'scope': 'signed installed app + real services + synthetic provider',
               'provider': 'compile-gated local fixture; no Google OAuth or traffic',
               'approval': 'native host sheet driven by Makepad instrument; not physical acceptance',
               'binary_sha256': digest(host), 'source_sha256': digest(APP / 'bundle/main.splash'),
               'steps': [], 'not_verified': ['Live Google OAuth/read/write', 'Full shell Glance routing',
                                           'Actual agent conversations', 'Android, Linux, Windows']}
    child, log, endpoint = None, None, None
    with tempfile.TemporaryDirectory(prefix='calendar-installed-') as temporary:
        profile = Path(temporary) / 'profile'
        state_file = profile / '.host/acceptance-calendar/provider.json'

        def request(route, **query):
            suffix = '?' + urllib.parse.urlencode(query) if query else ''
            with urllib.request.urlopen(endpoint + route + suffix, timeout=15) as response:
                result = json.load(response)
            if result.get('err'):
                raise RuntimeError(result['err'])
            return result

        def widgets():
            return [row for row in request('/snap')['s'] if row['ty'] != 'Splash'
                    and row['r'][2] > 0 and row['r'][3] > 0]

        def wait(predicate, timeout=15):
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                value = predicate()
                if value:
                    return value
                time.sleep(.08)
            raise AssertionError('Native Calendar state did not settle')

        def row_text(text, kind=None):
            return next((row for row in widgets() if row.get('t') == text
                         and (kind is None or row['ty'] == kind)), None)

        def click(text, kind='Button'):
            row = wait(lambda: row_text(text, kind))
            x, y, width, height = row['r']
            request('/click', x=x + width / 2, y=y + height / 2, wait=1)
            receipt['steps'].append('click ' + text)

        def field(identifier, text):
            request('/m', k='scroll', x=200, y=450, dy=-10000, wait=1)
            for _ in range(15):
                row = next((row for row in widgets() if row.get('i') == identifier
                            and row['ty'] == 'TextInput' and row['r'][3] >= 40), None)
                if row:
                    x, y, width, height = row['r']
                    request('/click', x=x + width / 2, y=y + min(20, height / 2), wait=1)
                    request('/k', k='press', c='KeyA', cmd=1, wait=1)
                    request('/t', t=text, wait=1)
                    wait(lambda: any(row.get('i') == identifier and (row.get('val') == text or row.get('t') == text)
                                     for row in widgets()))
                    return
                request('/m', k='scroll', x=200, y=450, dy=170, wait=1)
            raise AssertionError('Unreachable input ' + identifier)

        def snapshot(name):
            rows = widgets()
            (run / (name + '.snapshot.json')).write_text(json.dumps(rows, indent=2) + '\n')
            capture = Path(request('/g')['png'])
            shutil.copyfile(capture, run / (name + '.png'))
            return '\n'.join(row.get('t', '') for row in rows)

        def state():
            return json.loads(state_file.read_text())

        def update_state(value):
            temporary_file = state_file.with_suffix('.edit.tmp')
            temporary_file.write_text(json.dumps(value))
            temporary_file.replace(state_file)

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
                child.kill()
                child.wait()
            log.close()
            child, log, endpoint = None, None, None

        def launch(first):
            nonlocal child, log, endpoint
            label = 'first' if first else 'restart'
            log_path = run / (label + '.log')
            log = log_path.open('w+')
            entry = '--install-bundle=' + str(APP / 'bundle') if first else '--installed-app=' + APP_ID
            child = subprocess.Popen([str(host), entry, '--app-data=' + str(profile),
                                      '--provider-fixture=calendar', '--remote'],
                                     stdout=log, stderr=log, env={**os.environ, 'MAKEPAD_HIDE_WINDOWS': '1'})
            def started():
                if child.poll() is not None:
                    raise AssertionError('Installed host exited: ' + log_path.read_text()[-2000:])
                return re.search(r'listening on (127\.0\.0\.1:\d+)', log_path.read_text())
            match = wait(started, 30)
            endpoint = 'http://' + match[1]
            wait(lambda: 'CONNECTED_INSTALLED' in log_path.read_text())
            assert '"signed":true' in log_path.read_text()

        def review_snapshot(name, title):
            click('Review & Save')
            wait(lambda: row_text(title, 'Label'))
            return snapshot(name)

        try:
            launch(True)
            click('Synthetic acceptance calendar · owner')
            wait(lambda: row_text('Synthetic planning session', 'Label'))
            snapshot('01-installed-agenda')
            click('+ Event')
            title = 'Synthetic appointment — installed acceptance'
            field('e_title', title)
            field('e_date', '2026-10-10')
            field('e_time', '09:45')
            field('e_end_date', '2026-10-10')
            field('e_end_time', '10:30')
            field('e_zone', 'America/Los_Angeles')
            field('e_place', 'Synthetic review room')
            field('e_notes', 'Synthetic notes only.\nReview this exact event.')
            text = review_snapshot('02-host-create-review', 'Create Google Calendar event')
            for expected in [title, '2026-10-10T09:45:00-07:00', 'Synthetic review room', 'Review this exact event.']:
                assert expected in text, ('Missing reviewed content', expected)
            click('Back to editing')
            assert not [call for call in state()['calls'] if call['method'] in ('POST', 'PATCH')]
            review_snapshot('03-review-after-cancel', 'Create Google Calendar event')
            click('Approve & Save')
            wait(lambda: len(state()['events']) == 3)
            wait(lambda: not any(row.get('i') == 'connector_review_status' for row in widgets()))
            wait(lambda: row_text(title, 'Label'))
            saved = next(event for event in state()['events'] if event['summary'] == title)
            assert saved['start']['dateTime'] == '2026-10-10T09:45:00-07:00'
            assert saved['description'] == 'Synthetic notes only.\nReview this exact event.'
            assert saved['location'] == 'Synthetic review room'
            receipt['saved_event'] = saved
            click(title, 'Label')
            snapshot('04-reopened-saved-event')
            click('Edit')
            field('e_title', title + ' edited')
            review_snapshot('05-host-edit-review', 'Update Google Calendar event')
            click('Approve & Save')
            wait(lambda: any(event['summary'] == title + ' edited' for event in state()['events']))
            wait(lambda: not any(row.get('i') == 'connector_review_status' for row in widgets()))
            wait(lambda: row_text(title + ' edited', 'Label'))
            click(title + ' edited', 'Label')
            click('Edit')
            field('e_title', 'Retained local conflicting draft')
            external = state()
            event = next(event for event in external['events'] if event['id'] == saved['id'])
            event['summary'] = 'Synthetic external edit'
            event['etag'] = '"synthetic-external-revision"'
            external['revision'] += 1
            update_state(external)
            review_snapshot('06-host-conflict-review', 'Update Google Calendar event')
            writes_before = len([call for call in state()['calls'] if call['method'] == 'PATCH'])
            click('Approve & Save')
            wait(lambda: any(row.get('i') == 'connector_review_status' and 'remote content changed' in row.get('t', '') for row in widgets()))
            wait(lambda: row_text('Back to editing', 'Button') and not row_text('Approve & Save', 'Button'))
            snapshot('07-visible-conflict-error')
            assert len([call for call in state()['calls'] if call['method'] == 'PATCH']) == writes_before + 1
            assert next(event for event in state()['events'] if event['id'] == saved['id'])['summary'] == 'Synthetic external edit'
            click('Back to editing')
            assert any(row.get('i') == 'e_title' and (row.get('val') == 'Retained local conflicting draft' or row.get('t') == 'Retained local conflicting draft') for row in widgets())
            click('Keep draft')
            quit()
            offline = state()
            offline['offline'] = True
            update_state(offline)
            launch(False)
            wait(lambda: row_text(title + ' edited', 'Label'))
            wait(lambda: any('Synthetic provider is offline' in row.get('t', '') for row in widgets()))
            snapshot('08-offline-restart-cached-agenda')
            click('Resume draft')
            assert any(row.get('i') == 'e_title' and (row.get('val') == 'Retained local conflicting draft' or row.get('t') == 'Retained local conflicting draft') for row in widgets())
            snapshot('09-restarted-conflicting-draft')
            receipt['cases'] = ['signed install and verified reopen', 'provider-backed populated agenda (synthetic)',
                                'exact immutable host review and cancel', 'create and reopen', 'edit with ETag',
                                'conflict without retry and draft retained', 'offline cached agenda after restart',
                                'draft retained after restart']
            receipt['provider_final'] = state()
            receipt['result'] = 'pass'
        except BaseException as error:
            receipt['result'], receipt['error'] = 'fail', str(error)
            if endpoint and child and child.poll() is None:
                try:
                    snapshot('failure')
                except Exception as capture_error:
                    receipt['capture_error'] = str(capture_error)
            raise
        finally:
            quit()
            receipt['captures'] = {path.name: digest(path) for path in run.glob('*.png')}
            receipt['cleanup'] = 'owned native process stopped; synthetic temporary profile removed'
            (run / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print(json.dumps({'result': receipt['result'], 'evidence': str(run)}, indent=2))


if __name__ == '__main__':
    main()
