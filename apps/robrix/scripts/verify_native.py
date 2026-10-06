#!/usr/bin/env python3
"""Verify an owned release launcher with Makepad's native HTTP instrument."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from urllib.parse import urlencode
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--card-preview', action='store_true')
    parser.add_argument('--reopen', action='store_true')
    parser.add_argument('--homeserver', help='Probe a password-only Matrix server; never submits credentials')
    args = parser.parse_args()
    if args.card_preview and args.homeserver:
        parser.error('--homeserver requires the login view')
    host = args.host.resolve()
    binary = host / 'target/release/octosense'
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env.update(MAKEPAD_HIDE_WINDOWS='1', OCTOSENSE_HOME=str(output / 'shell'),
               OCTOSENSE_ROBRIX_DATA_DIR=str(output / 'account'))
    config = {'module_open': {'robrix': {'card_preview': args.card_preview}}}
    env['MAKEPAD_APP_CONFIG'] = json.dumps(config)
    command = [str(binary), '--remote', '--test-action', 'launch-robrix']
    if args.reopen:
        command += ['--test-action', 'close', '--test-action', 'launch-robrix']
    endpoint = None
    proof = {'fixture_only': True, 'command': command, 'host': str(host),
             'executable_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
             'hidden': True, 'card_preview': args.card_preview, 'reopen': args.reopen}
    log_path = output / 'native.log'
    with log_path.open('w') as log:
        child = subprocess.Popen(command, cwd=host, env=env, stdout=log, stderr=subprocess.STDOUT)
        proof['pid'] = child.pid
        try:
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                if child.poll() is not None:
                    raise RuntimeError('launcher exited before instrument was ready')
                text = log_path.read_text(errors='replace')
                match = re.search(r'listening on (127\.0\.0\.1:\d+) pid=(\d+)', text)
                if match:
                    assert int(match[2]) == child.pid
                    endpoint = 'http://' + match[1]
                    break
                time.sleep(.2)
            if endpoint is None:
                raise RuntimeError('owned instrument endpoint not found')

            def get(route, **params):
                with urlopen(endpoint + route + ('?' + urlencode(params) if params else ''), timeout=30) as response:
                    raw = response.read()
                    return json.loads(raw) if route != '/' else raw.decode()

            (output / 'protocol.txt').write_text(get('/'))
            deadline = time.monotonic() + 25
            while time.monotonic() < deadline:
                proof['status'] = get('/s')
                if proof['status']['w']:
                    break
                time.sleep(.2)
            assert len(proof['status']['w']) == 1, 'expected one host native window'
            time.sleep(2)  # Let the phone viewport and launch animation settle.
            proof['status'] = get('/s')
            query = 'OctoSense chat' if args.card_preview else 'user_id_input'
            deadline = time.monotonic() + 25
            while time.monotonic() < deadline:
                snap = get('/snap', q=query)
                visible = [node for node in snap.get('s', []) if node['r'][2] > 0 and node['r'][3] > 0]
                if visible:
                    break
                time.sleep(.3)
            assert visible, 'expected native widget did not appear'
            proof['snapshot'] = snap
            if not args.card_preview:
                node = visible[0]
                x, y, width, height = node['r']
                get('/click', x=x + width / 2, y=y + height / 2, wait=1)
                get('/t', t='@fixture:example.org', wait=1)
                proof['input'] = get('/snap', q='user_id_input')
                assert any(n.get('val') == '@fixture:example.org' for n in proof['input']['s']), 'native input was not applied'
            if args.homeserver:
                def click_widget(query):
                    nodes = get('/snap', q=query).get('s', [])
                    nodes = [n for n in nodes if n['r'][2] > 0 and n['r'][3] > 0]
                    assert len(nodes) == 1, 'expected one ' + query
                    x, y, w, h = nodes[0]['r']
                    get('/click', x=x+w/2, y=y+h/2, wait=1)
                click_widget('homeserver_input')
                get('/t', t=args.homeserver, wait=1)
                proof['homeserver_input'] = get('/snap', q='homeserver_input')
                assert any(n.get('val') == args.homeserver for n in proof['homeserver_input']['s'])
                # The first click probes capabilities before checking credentials.
                assert get('/snap', q='sso_view').get('s'), 'expected unresolved SSO controls before probe'
                click_widget('login_button')
                deadline = time.monotonic() + 35
                while time.monotonic() < deadline:
                    after = get('/snap', q='sso_view')
                    if not after.get('s'):
                        break
                    time.sleep(.3)
                assert not after.get('s'), 'password-only homeserver discovery did not hide SSO controls'
                proof['password_server_discovered'] = True
                proof['authentication_attempted'] = False
                proof['homeserver'] = args.homeserver
            time.sleep(2)
            capture = get('/gseq', n=3, every_ms=100)
            shutil.copy2(capture['png'][-1], output / 'native.png')
            proof['capture'] = capture
            proof['pass'] = True
        finally:
            if endpoint and child.poll() is None:
                try:
                    with urlopen(endpoint + '/gq', timeout=30) as response:
                        proof['cleanup'] = json.load(response)
                except Exception as error:
                    proof['cleanup_error'] = str(error)
                    try:
                        urlopen(endpoint + '/quit', timeout=10).close()
                    except Exception:
                        pass
            if child.poll() is None:
                try:
                    child.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    child.terminate()
                    child.wait(timeout=10)
                    proof['forced_cleanup'] = True
            proof['exit_code'] = child.returncode
            log.flush()
            runtime_errors = [line for line in log_path.read_text(errors='replace').splitlines()
                              if re.search(r'\[E\]|panicked at|ScriptError|Shader compilation failed', line)]
            proof['runtime_errors'] = runtime_errors
            proof['pass'] = proof.get('pass', False) and child.returncode == 0 and not proof.get('forced_cleanup') and not runtime_errors
            (output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({'output': str(output), 'pass': proof.get('pass', False), 'exit_code': proof['exit_code']}))
    if not proof.get('pass'):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
