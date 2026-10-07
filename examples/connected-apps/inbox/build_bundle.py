#!/usr/bin/env python3
"""Keep the app and Glance workspace behavior identical; no recursive embedding."""
import json
from pathlib import Path
root = Path(__file__).resolve().parent
source = (root / 'src/workspace.splash').read_text()
import re
card = source
for name, replacement in [('FIXTURE', 'let fixture = []'), ('LOGIN', ''), ('INBOX', 'inbox := View{visible:false rows := View{}}')]:
    card, count = re.subn(r'// CARD-' + name + r'-START.*?// CARD-' + name + r'-END', replacement, card, flags=re.S)
    assert count == 1, name
card = '\n'.join(line.strip() for line in card.splitlines()) + '\n'
if len(card.encode()) > 14 * 1024:
    raise SystemExit('Workspace must leave room for a compact binding in the 16 KiB Glance budget')
(root / 'bundle/main.splash').write_text('let initial = nil\nlet card_source = ' + json.dumps(card, ensure_ascii=False) + '\n' + source)
manifest = json.loads((root / 'bundle/manifest.json').read_text())
manifest['capabilities'] = ['storage', 'auth', 'gmail', 'model', 'glance', 'octos.session.open', 'octos.turn.start']
manifest['storage'] = {'accounts': True}
manifest['agent'] = {'profile':'read-only','tools':['ask_user_question'],'model':{'needs':['tool_calling']},'instructions':'AGENT.md','skills':['incoming-mail-triage'],'background':True,'triggers':{'events':['inbox.new_message']}}
(root / 'bundle/glance-workspace.splash').write_text(card)
manifest.pop('network', None)
(root / 'bundle/manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
