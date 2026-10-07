#!/usr/bin/env python3
"""Read an isolated signed Inbox acceptance run; never grants consent or sends.

Run after the native journey described in evidence/README.md. Provider data
must be the compile-only synthetic Gmail fixture. Copies only selected original
PNG captures and a field-allowlisted receipt, never profiles or full logs.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

APP = 'org.octosense.samples.inbox'
CLINIC = 'fixtureclinic20261006'
NEWSLETTER = 'fixturenewsletter20261006'
HERE = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--profile-root', type=Path, required=True)
p.add_argument('--binary', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--capture', action='append', default=[], help='Original PNG basename in profile root')
a = p.parse_args()
root = a.profile_root.resolve()
host = root / 'apps/.host'
read = lambda path: json.loads(path.read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
meta = read(root / 'apps/.connected-e2e.json')
assert meta['fixture'] == 'connected-e2e'
installed = next(x for x in meta['apps'] if x['id'] == APP)
assert installed['signed_install'] and installed['prepared_launch_verified']
provider = read(host / 'acceptance-inbox.json')
assert provider['synthetic_gmail'] and provider['released']
assert provider['denied_send_attempts'] == 0
states = [read(x) for x in (host / 'oauth/inbox-events').glob('*/*.json')]
assert len(states) == 1 and not states[0]['pending']
assert set(states[0]['completed']) == {CLINIC, NEWSLETTER}
cards = [x for x in read(host / 'mail-notifications/outbox.json') if x['key'].startswith(APP + '/')]
assert len(cards) == 1 and cards[0]['key'].endswith('/' + CLINIC)
drafts = [d for x in (host / 'oauth/inbox').glob('*/*.json') for d in read(x)['drafts'].values()]
assert len(drafts) == 1
draft = drafts[0]
assert draft['source_message'] == CLINIC and draft['provenance'] == 'model'
assert draft['status'] == 'draft' and draft['revision'] >= 3 and not draft['attempts']
body = draft['reply']['body']
assert '10:30' in body and 'medication list' in body
assert draft['reply']['to'] == 'appointments@example.test'
turns = []
for path in (root / 'apps' / APP).rglob('*.jsonl'):
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    user = next((x for x in rows if x.get('role') == 'user'), None)
    final = next((x for x in reversed(rows) if x.get('role') == 'assistant' and not x.get('tool_calls')), None)
    if not user or not final:
        continue
    tools = [t for row in rows for t in row.get('tool_calls', [])]
    if not tools:
        continue
    decisions = [t['arguments']['decision'] for t in tools if t['name'] == 'inbox_event_decide']
    kind = 'human_draft_change' if any(t['name'] == 'inbox_draft_edit' for t in tools) else ('important_mail' if 'published' in decisions else 'quiet_mail')
    parse_time = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))
    turns.append({'kind': kind, 'elapsed_seconds': round((parse_time(final['timestamp']) - parse_time(user['timestamp'])).total_seconds(), 3), 'tools': [t['name'] for t in tools], 'decisions': decisions, 'tool_errors': [x['content'] for x in rows if x.get('role') == 'tool' and 'failed (host:' in x.get('content', '')]})
assert {t['kind'] for t in turns} == {'important_mail', 'quiet_mail', 'human_draft_change'}
# Check the actual kernel bootstrap log, without reading or exporting credentials.
logs = '\n'.join(x.read_text() for x in (root / 'home/octos-home/.octos/logs').glob('serve*.log'))
assert 'provider=deepseek' in logs and 'model=deepseek-v4-flash' in logs
captures = {}
capture_builds = {}
recorded_builds = read(root / 'capture-builds.json') if (root / 'capture-builds.json').exists() else {}
a.output.mkdir(parents=True, exist_ok=True)
for name in a.capture:
    assert Path(name).name == name and name.endswith('.png')
    source = root / name
    assert source.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    (a.output / name).write_bytes(source.read_bytes())
    captures[name] = sha(source)
    capture_builds[name] = recorded_builds.get(name, (root / 'binary-at-model-run.sha256').read_text().strip())
receipt = {'schema': 1, 'recorded_at': datetime.now(timezone.utc).isoformat(), 'driver': 'Codex using Makepad native instrument; model performs triage and draft tools', 'platform': 'macOS hidden full OctoSense shell', 'data': 'synthetic Gmail dependency; no live OAuth or email', 'model': 'DeepSeek deepseek-v4-flash (real network inference)', 'signed_bundle_digest': installed['bundle_digest'], 'source_sha256': {name: sha(HERE / name) for name in ['src/workspace.splash', 'bundle/main.splash', 'bundle/glance-workspace.splash', 'bundle/manifest.json', 'bundle/tools.json', 'bundle/AGENT.md', 'bundle/skills/incoming-mail-triage/SKILL.md', 'launch_integrated.py', 'collect_integrated.py']}, 'visual_run_binary_sha256': sha(a.binary), 'model_run_binary_sha256': (root / 'binary-at-model-run.sha256').read_text().strip(), 'turns': sorted(turns, key=lambda x: x['kind']), 'durable_events': {'pending': 0, 'completed': [CLINIC, NEWSLETTER]}, 'publication': {'count': 1, 'clinic_only': True, 'title': cards[0]['args']['title'], 'summary': cards[0]['args']['summary']}, 'draft': {'revision': draft['revision'], 'status': draft['status'], 'body': body, 'recipient': draft['reply']['to'], 'submission_attempts': 0}, 'provider_requests': provider['requests'], 'provider_send_attempts': provider['denied_send_attempts'], 'captures_sha256': captures, 'capture_binary_sha256': capture_builds, 'visual_verdict': 'separate original-pixel review required', 'unverified': ['live Google OAuth', 'live Gmail reads or delivery', 'physical native send approval', 'Android keyboard and lifecycle', 'OnePlus 6', 'MiniMax']}
(a.output / 'integrated-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('PASS: signed Inbox install; real model important/quiet decisions; same saved model-edited draft; zero send attempts. Pixel findings are separate.')
