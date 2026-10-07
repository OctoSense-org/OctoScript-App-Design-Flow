#!/usr/bin/env python3
"""Launch a new private full-shell acceptance profile; Gmail is synthetic.

Requires the companion OctoSense acceptance-fixtures examples and the pinned
kernel. Copies only the explicitly selected model configuration, never app or
conversation data. Normal app-agent consent is still answered in the host UI.
"""
import argparse
import hashlib
import json
import os
import socket
import subprocess
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--octosense', type=Path, required=True)
p.add_argument('--profile-root', type=Path, required=True)
p.add_argument('--model-profile', type=Path)
p.add_argument('--restart', action='store_true', help='Reopen this marked fixture without replacing its account, consent or draft')
p.add_argument('--kernel', type=Path, required=True)
p.add_argument('--port', type=int, default=8195)
a = p.parse_args()
repo = a.octosense.resolve()
root = a.profile_root.resolve()
for binary in (repo / 'target/release/examples/connected-install', repo / 'target/release/examples/connected-inbox-e2e', a.kernel):
    assert binary.is_file(), f'Missing built binary: {binary.name}'
with socket.socket() as probe:
    assert probe.connect_ex(('127.0.0.1', a.port)) != 0, 'The selected instrument port already belongs to another process'
config = root / 'home/octos-home/.octos/profiles/_main.json'
apps = root / 'apps'
if a.restart:
    assert root.is_dir() and config.is_file()
    assert json.loads((apps / '.connected-e2e.json').read_text())['fixture'] == 'connected-e2e'
    assert json.loads((apps / '.host/acceptance-inbox.json').read_text())['synthetic_gmail']
else:
    assert not root.exists(), 'Choose a new isolated root, never a personal profile'
    assert a.model_profile, 'Choose the authorized model profile explicitly'
    source = json.loads(a.model_profile.read_text())
    profile = {k: source[k] for k in ('id', 'name', 'enabled', 'created_at', 'updated_at')}
    profile['name'] = 'Isolated connected Inbox acceptance'
    profile['config'] = {k: source['config'][k] for k in ('llm', 'env_vars')}
    root.mkdir(mode=0o700, parents=True)
    config.parent.mkdir(parents=True)
    with open(config, 'x', opener=lambda path, flags: os.open(path, flags, 0o600)) as f:
        json.dump(profile, f)
    bundle = Path(__file__).resolve().parent / 'bundle'
    subprocess.run([str(repo / 'target/release/examples/connected-install'), '--keep-profile=' + str(apps), str(bundle)], check=True, stdout=subprocess.DEVNULL)
meta = json.loads((apps / '.connected-e2e.json').read_text())
env = os.environ.copy()
env.update(OCTOSENSE_HOME=str(root / 'home'), OCTOSENSE_APP_DATA=str(apps), OCTOSENSE_HUB_ANCHOR=meta['anchor'], OCTOS_APP_CORE_BIN=str(a.kernel.resolve()), OCTOS_APP_CORE_DIR=str(config.parent.parent), MAKEPAD_HIDE_WINDOWS='1', RINX_DATA_DIR=str(root / 'rinx'))
binary = repo / 'target/release/examples/connected-inbox-e2e'
binary_hash = hashlib.sha256(binary.read_bytes()).hexdigest()
if not a.restart:
    (root / 'binary-at-model-run.sha256').write_text(binary_hash)
(root / 'active-binary.sha256').write_text(binary_hash)
command = [str(binary), '--remote=' + str(a.port), '--test-action', 'launch-hub:org.octosense.samples.inbox']
with (root / ('shell-restart.log' if a.restart else 'shell.log')).open('wb') as log:
    child = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
(root / 'pid').write_text(str(child.pid))
print(f'Started owned hidden shell PID {child.pid}, Makepad port {a.port}. Gmail is synthetic; model inference is real. Normal agent consent remains required. Stop only this instance using /quit.')
