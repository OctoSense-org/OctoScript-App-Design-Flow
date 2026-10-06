#!/usr/bin/env python3
"""Signed Calendar -> shared Glance -> exact event, including cold shell restart.

The provider/vault are compile-gated synthetic fixtures. The signed Store,
Calendar app, OAuth host methods, Glance and launcher are real shell code.
This test runs its own hidden desktop window; it does not test Google or a phone.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.parse
import urllib.error
import urllib.request

APP = Path(__file__).resolve().parents[1]
APP_ID = 'org.octosense.samples.googlecalendar'
TITLE = 'Synthetic planning session'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--shell', type=Path, required=True)
    parser.add_argument('--installer', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8294)
    parser.add_argument('--model-profile', type=Path, help='Optional private Octos profile; never written to evidence')
    parser.add_argument('--kernel', type=Path, help='Real octos executable for optional advisory chat')
    parser.add_argument('--out', type=Path, default=APP / '.local-state/shell-evidence')
    args = parser.parse_args()
    shell, installer = args.shell.resolve(), args.installer.resolve()
    if bool(args.model_profile) != bool(args.kernel):
        parser.error('--model-profile and --kernel must be supplied together')
    with socket.socket() as check:
        if check.connect_ex(('127.0.0.1', args.port)) == 0:
            raise RuntimeError('Requested instrument port is already serving another process')
    run = args.out / ('run-' + str(time.time_ns()))
    run.mkdir(parents=True)
    receipt = {'result': 'running', 'scope': 'signed installed Calendar in real desktop shell',
               'provider': 'synthetic compile-gated Calendar transport and vault',
               'source_sha256': digest(APP / 'bundle/main.splash'),
               'binary_sha256': digest(shell), 'steps': [],
               'not_verified': ['Google OAuth/live provider', 'Real model conversations',
                                'Phone keyboard/lifecycle', 'Linux and Windows']}
    child, log = None, None
    endpoint = 'http://127.0.0.1:' + str(args.port)

    def request(route, **query):
        suffix = '?' + urllib.parse.urlencode(query) if query else ''
        try:
            result = json.load(urllib.request.urlopen(endpoint + route + suffix, timeout=15))
        except urllib.error.HTTPError as error:
            raise RuntimeError(error.read().decode('utf-8', errors='replace')) from error
        if result.get('err'):
            raise AssertionError(result['err'])
        return result

    def rows():
        return [r for r in request('/snap')['s'] if r['ty'] != 'Splash'
                and r['r'][2] > 0 and r['r'][3] > 0]

    def wait(predicate, timeout=20):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            value = predicate()
            if value:
                return value
            time.sleep(.1)
        raise AssertionError('Calendar shell state did not settle')

    def text_row(text, kind='Button'):
        return next((r for r in rows() if r.get('t') == text and r['ty'] == kind), None)

    def click(text, kind='Button'):
        r = wait(lambda: text_row(text, kind))
        x, y, w, h = r['r']
        request('/click', x=x + w / 2, y=y + h / 2, wait=1)
        receipt['steps'].append('click ' + text)

    def event_selected(title):
        return any(r.get('i') == 'event_title' and r.get('t') == title for r in rows())

    def capture(name):
        (run / (name + '.snapshot.json')).write_text(json.dumps(rows(), indent=2) + '\n')
        shutil.copyfile(request('/g')['png'], run / (name + '.png'))

    def glance(visible=True):
        transitions = re.findall(r'wm: glance panel (open|closed)', Path(log.name).read_text())
        is_open = bool(transitions and transitions[-1] == 'open')
        if is_open != visible:
            request('/k', k='down', c='F9', wait=1)
            request('/k', k='up', c='F9', wait=1)
        # Custom-drawn Glance controls do not appear in /snap. Wait for the
        # panel slide, then use its inspected 1400x900 desktop coordinates.
        time.sleep(.5)

    def quit():
        nonlocal child, log
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
        child, log = None, None

    with tempfile.TemporaryDirectory(prefix='calendar-shell-') as temporary:
        root = Path(temporary)
        profile, home = root / 'apps', root / 'home'
        home.mkdir()
        core = home / 'octos-home/.octos'
        if args.model_profile:
            original = json.loads(args.model_profile.read_text())
            private = {k: original[k] for k in ['id', 'name', 'enabled', 'created_at', 'updated_at']}
            private['name'] = 'Calendar synthetic-event acceptance'
            private['config'] = {k: original['config'][k] for k in ['llm', 'env_vars']}
            profiles = core / 'profiles'
            profiles.mkdir(parents=True, mode=0o700)
            path = profiles / '_main.json'
            with path.open('w') as out:
                os.chmod(path, 0o600)
                json.dump(private, out)
            receipt['model'] = {'provider': private['config']['llm'].get('primary', {}).get('family_id'),
                                'model': private['config']['llm'].get('primary', {}).get('model_id'),
                                'kernel_sha256': digest(args.kernel.resolve())}
        installed = subprocess.run([str(installer), '--keep-profile=' + str(profile),
                                    str(APP / 'bundle')], text=True, capture_output=True)
        if installed.returncode:
            raise AssertionError(installed.stderr + installed.stdout)
        marker = json.loads((profile / '.connected-e2e.json').read_text())
        assert any(app['id'] == APP_ID and app['signed_install'] and app['prepared_launch_verified'] for app in marker['apps'])
        outbox = profile / '.host/mail-notifications/outbox.json'
        inherited = {k: v for k, v in os.environ.items() if k not in
                     ['MAKEPAD_APP_CONFIG', 'OCTOS_APP_CORE_DIR', 'OCTOS_APP_CORE_BIN']}
        env = {**inherited, 'MAKEPAD_HIDE_WINDOWS': '1', 'MAKEPAD_REMOTE': str(args.port),
               'OCTOSENSE_HOME': str(home), 'OCTOSENSE_APP_DATA': str(profile),
               'RINX_DATA_DIR': str(root / 'rinx'),
               'OCTOSENSE_HUB_ANCHOR': marker['anchor']}
        if args.kernel:
            env.update({'OCTOS_APP_CORE_DIR': str(core), 'OCTOS_APP_CORE_BIN': str(args.kernel.resolve())})

        def launch(first):
            nonlocal child, log
            log_path = run / ('first.log' if first else 'restart.log')
            log = log_path.open('w')
            command = [str(shell), '--provider-fixture=calendar']
            if first:
                command += ['--test-action', 'launch-hub:' + APP_ID]
            child = subprocess.Popen(command, stdout=log, stderr=log, env=env)
            def ready():
                if child.poll() is not None:
                    raise AssertionError('Shell exited: ' + log_path.read_text()[-2000:])
                try:
                    status = request('/s')
                    return status if status.get('w') else None
                except (OSError, ValueError):
                    return None
            window = wait(ready, 45)['w'][0]
            assert window['sz'][0] == 1400 and 898 <= window['sz'][1] <= 900, window

        try:
            launch(True)
            click('Synthetic acceptance calendar · owner')
            click(TITLE, 'Label')
            wait(lambda: event_selected(TITLE))
            click('Glance')
            wait(lambda: text_row('Shown in Glance for 24 hours.', 'Label'))
            saved = json.loads(outbox.read_text())
            assert len(saved) == 1 and saved[0]['args']['title'] == TITLE
            assert saved[0]['args']['notify'] is False
            receipt['publication'] = {'key': saved[0]['key'], 'published': saved[0]['published'],
                                      'expires': saved[0]['expires']}
            # A newly published desktop card opens Glance automatically.
            time.sleep(.5)
            capture('00-new-publication-opens-glance')
            glance(False)
            click('‹ Agenda')
            click('Different synthetic event', 'Label')
            wait(lambda: event_selected('Different synthetic event'))
            glance()
            capture('01-glance-with-other-event-selected')
            request('/click', x=1136, y=278, wait=1)
            wait(lambda: event_selected(TITLE))
            capture('02-warm-exact-event-route')
            click('Chat')
            wait(lambda: any(r.get('i') == 'chat_title' and r.get('t') == TITLE for r in rows()))
            assert any(r.get('i') == 'chat_entry' for r in rows())
            capture('03-chat-bound-to-selected-event')
            quit()
            # No app launch action on restart: the retained card must restore
            # by itself, and its button must launch the installed app cold.
            launch(False)
            time.sleep(1.5)
            assert not event_selected(TITLE)
            glance()
            capture('04-restored-glance-without-open-app')
            request('/click', x=1136, y=278, wait=1)
            wait(lambda: event_selected(TITLE))
            capture('05-cold-exact-event-route')
            restored = json.loads(outbox.read_text())
            assert len(restored) == 1
            assert restored[0]['published'] == saved[0]['published']
            assert restored[0]['expires'] == saved[0]['expires']
            assert not (home / 'approvals/consent.json').exists(), 'Agent consent was not part of this foreground journey'
            receipt['cases'] = ['signed installed app publishes real shared Glance card',
                                'warm Open Calendar selects exact event from another event',
                                'app Chat opens with same event and input',
                                'card restores without agent consent or app open',
                                'cold Open Calendar launches exact installed event',
                                'restart preserves original publication and expiry']
            if args.model_profile:
                click('Chat')
                entry = wait(lambda: next((r for r in rows() if r.get('i') == 'chat_entry'), None))
                x, y, w, h = entry['r']
                request('/click', x=x + w / 2, y=y + h / 2, wait=1)
                question = 'Verify this event with your googlecalendar.event tool. What is its exact title, local start time, timezone and location? Answer briefly. Do not change or save anything.'
                request('/t', t=question, wait=1)
                click('Send')
                # Agent permission is reviewed in the real host sheet. Only
                # synthetic event data is provided, and no write tool is granted.
                wait(lambda: any('Allow' in r.get('t', '') or 'Assistant' in r.get('t', '') for r in rows()))
                capture('06-agent-consent')
                allow = next((r for r in rows() if r['ty'] == 'Button' and r.get('t', '').startswith('Allow')), None)
                if allow:
                    x, y, w, h = allow['r']
                    request('/click', x=x + w / 2, y=y + h / 2, wait=1)
                else:
                    # The current shell consent overlay is custom drawn, so it
                    # is absent from /snap. These are its visually reviewed
                    # Allow coordinates at this fixed desktop viewport.
                    assert any('Waiting for the person to allow' in r.get('t', '') for r in rows())
                    request('/click', x=446, y=570, wait=1)
                wait(lambda: (home / 'approvals/consent.json').exists())
                consent = json.loads((home / 'approvals/consent.json').read_text())
                assert consent['apps'][APP_ID]['allowed'] is True
                # The first request returns a visible error while prompting;
                # deliberately resend the unchanged question after consent.
                entry = next(r for r in rows() if r.get('i') == 'chat_entry')
                x, y, w, h = entry['r']
                request('/click', x=x + w / 2, y=y + h / 2, wait=1)
                request('/t', t=question, wait=1)
                click('Send')
                last_scroll = [0.0]
                def answered():
                    if time.monotonic() - last_scroll[0] > 1:
                        request('/m', k='scroll', x=800, y=550, dy=900, wait=1)
                        last_scroll[0] = time.monotonic()
                    return any('Fixture room' in r.get('t', '') for r in rows())
                wait(answered, 120)
                capture('07-real-advisory-model-answer')
                text = '\n'.join(r.get('t', '') for r in rows())
                assert TITLE in text and 'Fixture room' in text and ('09:00' in text or '9:00' in text)
                receipt['advisory_answer'] = text
                peers = list((core / 'profiles/_main/data/peers').glob('org-octosense-samples-googlecalendar-*'))
                assert len(peers) == 1
                receipt['model_result'] = (peers[0] / 'result.md').read_text()
                receipt['tool_audit'] = [json.loads(line) for line in (peers[0] / 'tool_audit.jsonl').read_text().splitlines()]
                assert 'googlecalendar.event' in json.dumps(receipt['tool_audit'])
                provider_state = json.loads((profile / '.host/acceptance-calendar/provider.json').read_text())
                assert not any(call['method'] in ['POST', 'PATCH', 'DELETE'] for call in provider_state['calls'])
                receipt['advisory_writes'] = 0
                receipt['cases'].append('real configured model answers about selected synthetic event')
                receipt['not_verified'].remove('Real model conversations')
                receipt['not_verified'].append('Glance-card/app shared conversation continuity')
            receipt['result'] = 'pass'
        except BaseException as error:
            receipt['result'], receipt['error'] = 'fail', str(error)
            if child and child.poll() is None:
                try:
                    capture('failure')
                except Exception as capture_error:
                    receipt['capture_error'] = str(capture_error)
            raise
        finally:
            quit()
            receipt['captures'] = {p.name: digest(p) for p in run.glob('*.png')}
            receipt['cleanup'] = 'owned shell stopped; synthetic profile and home removed'
            (run / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print(json.dumps({'result': receipt['result'], 'evidence': str(run)}, indent=2))


if __name__ == '__main__':
    main()
