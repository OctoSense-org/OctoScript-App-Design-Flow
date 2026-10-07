#!/usr/bin/env python3
"""Exercise real Makepad widgets; requires the flow's hub/card-host environment.

Owns its instances and state. No model/provider calls succeed in card-host;
those checks assert the unavailable path, not live agent delivery.
"""
import argparse
from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import time
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OCTO = REPO / 'tools/octo'
CHECKS = []


def check(condition, description):
    CHECKS.append({'check': description, 'passed': bool(condition)})
    if not condition:
        raise AssertionError(description)


class App:
    def __init__(self, name, state_root):
        self.name = name
        self.bundle = ROOT / name / 'bundle'
        self.state_root = state_root / name
        self.app_id = json.loads((self.bundle / 'manifest.json').read_text())['id']
        self.port = None
        self.pid = None
        self.inputs = []

    def launch(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            self.port = sock.getsockname()[1]
        result = subprocess.run([str(OCTO), 'run', str(self.bundle), '--hidden', '--detach',
                                 '--port', str(self.port), '--app-data', str(self.state_root)],
                                check=True, capture_output=True, text=True)
        (self.state_root / 'launch.txt').write_text(result.stdout + result.stderr)
        self.pid = self.request('/s')['pid']
        return self

    def request(self, path, **params):
        suffix = '?' + urlencode(params) if params else ''
        with urlopen(f'http://127.0.0.1:{self.port}{path}{suffix}', timeout=15) as response:
            data = response.read()
        if path == '/g' and params.get('raw') == 1:
            return data
        value = json.loads(data)
        if isinstance(value, dict) and value.get('err'):
            raise RuntimeError(value['err'])
        return value

    def nodes(self):
        return [n for n in self.request('/snap')['s'] if n.get('ty') != 'Splash']

    def text(self):
        return '\n'.join(n.get('t', '') for n in self.nodes())

    def tap(self, identity=None, text=None):
        # Scroll clipped or offscreen controls into view before injecting input.
        for attempt in range(24):
            nodes = self.nodes()
            matches = [n for n in nodes if n.get('ty') in ('Button', 'TextInput')
                       and (n.get('i') == identity if identity else n.get('t') == text)]
            if matches and matches[0]['r'][3] >= 44 and matches[0].get('enabled', True):
                node = matches[0]
                x, y, width, height = node['r']
                self.request('/click', x=x + width / 2, y=y + height / 2, wait=1)
                self.inputs.append({'action': 'click', 'id': node.get('i'), 'text': node.get('t'), 'rect': node['r']})
                return
            direction = 250 if attempt < 12 else -250
            self.request('/m', k='scroll', x=210, y=560, dy=direction, wait=1)
        raise AssertionError(f'{self.name}: no fully visible target {identity or text}; {self.text()}')

    def fill(self, identity, value):
        self.tap(identity=identity)
        self.request('/k', k='press', c='KeyA', cmd=1, wait=1)
        self.request('/t', t=value, wait=1)
        self.inputs.append({'action': 'text', 'id': identity, 'value': value})

    def expect(self, text, description):
        deadline = time.monotonic() + 5
        while text not in self.text() and time.monotonic() < deadline:
            self.request('/g', raw=1)
            time.sleep(0.05)
        check(text in self.text(), self.name + ': ' + description)

    def state(self):
        return json.loads((self.state_root / self.app_id / 'accounts/device/state.json').read_text())

    def capture(self, name):
        path = self.bundle / 'screenshots' / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(self.request('/g', raw=1))

    def clean_logs(self):
        log = (self.state_root / 'card-host.log').read_text()
        bad = [line for line in log.splitlines() if '[E]' in line or 'callback error' in line or 'on_render closure failed' in line]
        check(not bad, self.name + ': no script/runtime errors: ' + '\n'.join(bad))

    def close(self):
        if self.port is not None:
            self.request('/quit')
            self.port = None
            time.sleep(0.15)


def email(app):
    app.expect('Permission slip for Friday', 'populated inbox')
    app.capture('01-main.png')
    app.tap(text='Open / Maya Chen')
    app.tap('review_reply')
    app.expect('Write a reply before reviewing it.', 'empty draft refused')
    app.tap('sample_reply')
    app.fill('draft', 'Hi Maya, Sam can attend. Please confirm the return time. Alex')
    app.tap('review_reply')
    app.expect('maya@example.invalid', 'review binds exact recipient')
    app.expect('Please confirm the return time.', 'review uses edited draft')
    app.capture('02-review.png')
    app.tap('confirm_reply')
    first = app.state()
    check(len(first['outbox']) == 1 and first['outbox'][0]['message_id'] == 'school-101', 'email: one reply to selected message')
    check('Please confirm the return time.' in first['outbox'][0]['body'], 'email: edited draft committed')
    app.capture('03-receipt.png')
    app.tap('card_tab')
    app.fill('draft', 'A later unsent edit')
    app.tap('review_reply')
    app.tap('confirm_reply')
    app.expect('No duplicate was added.', 'repeat confirmation refused')
    check(app.state()['outbox'] == first['outbox'], 'email: original delivery unchanged by duplicate')
    app.tap('card_tab')
    app.tap('receipt')
    app.expect('Please confirm the return time.', 'receipt shows delivered body, not edited draft')
    app.tap('undo_delivery')
    check(not app.state()['outbox'] and not app.state()['done'][0], 'email: targeted undo')
    app.tap('inbox_tab')
    app.tap(text='Open / Jordan Lee')
    app.tap('sample_reply')
    app.tap('review_reply')
    app.expect('jordan@example.invalid', 'second record has its own recipient')
    app.tap('confirm_reply')
    check(app.state()['outbox'][0]['message_id'] == 'meeting-202', 'email: second message committed independently')
    app.tap('inbox_tab')
    app.tap(text='Open / Maya Chen')
    app.tap('done')
    app.tap('inbox_tab')
    app.expect("You're all caught up", 'empty needs-action filter')
    app.expect('0 requests need attention.', 'inbox count reflects handled requests')
    app.tap('filter')
    app.tap(text='Open / Weekly Studio')
    app.expect('Newsletter / no action', 'newsletter accessible outside action filter')
    app.tap('agent_tab')
    app.fill('question', '   ')
    app.tap('ask_agent')
    app.expect('Enter a question first.', 'empty agent question refused')
    app.fill('question', 'Does this newsletter need a reply?')
    app.tap('ask_agent')
    app.expect('Agent unavailable:', 'honest standalone host error')
    app.expect('Does this newsletter need a reply?', 'submitted question survives host error')
    app.capture('04-agent-unavailable.png')
    before = app.state()
    app.clean_logs(); app.close(); app.launch()
    check(app.state() == before, 'email: state survives restart')
    app.tap('card_tab')
    app.expect('A later unsent edit', 'edited draft survives restart')
    app.tap('draft_live')
    app.expect('Agent unavailable:', 'draft request reports unavailable host')
    app.expect('Draft a reply to Maya Chen', 'draft request identifies selected sender')
    check(app.state()['drafts'][0] == 'A later unsent edit', 'email: failed agent draft preserves human edit')
    app.tap('inbox_tab')
    app.tap('reset_demo')
    app.expect('2 requests need attention.', 'reset restores actionable inbox')
    check(not app.state()['outbox'] and app.state()['drafts'] == ['', '', ''], 'email: reset clears only demo actions')
    app.clean_logs()


def meeting(app):
    app.expect('Monday, 5 October 2026', 'populated calendar')
    app.capture('01-main.png')
    app.tap('review_invite')
    app.expect('Choose an available time first.', 'selection required')
    app.tap(text='10:00–10:30 UTC')
    app.expect('Cannot choose this time: Maya', 'known conflict blocked')
    app.tap('suggest_time')
    app.expect('14:00–14:30 UTC is the first shared slot.', 'offline calculation finds shared free slot')
    app.tap('review_invite')
    app.expect('maya@example.invalid', 'review lists attendees')
    app.capture('02-review.png')
    app.tap('change_before_confirm')
    app.tap('confirm_invite')
    app.expect('Nothing was booked.', 'late calendar conflict rechecked')
    check(app.state()['booking'] is None, 'meeting: stale proposal causes no mutation')
    app.tap('suggest_time')
    app.expect('15:30–16:00 UTC is the first shared slot.', 'recalculation skips new conflict')
    app.tap('review_invite')
    app.tap('confirm_invite')
    check(app.state()['booking']['slot_id'] == 'slot-1530', 'meeting: chosen valid slot committed')
    app.capture('03-receipt.png')
    app.tap('plan_tab')
    app.tap('review_invite')
    app.expect('A demo booking already exists.', 'repeat booking refused')
    before = app.state()
    app.clean_logs(); app.close(); app.launch()
    check(app.state() == before, 'meeting: booking survives restart')
    app.tap('receipt_tab')
    app.expect('15:30–16:00 UTC', 'persisted receipt renders correct time')
    app.tap('undo_booking')
    check(app.state()['booking'] is None, 'meeting: booking undo')
    calendar = json.loads((app.state_root / app.app_id / 'accounts/device/calendar.json').read_text())
    check(len(calendar['events']) == 3, 'meeting: original busy events preserved')
    app.tap('plan_tab')
    app.tap('busy_day')
    app.tap('suggest_time')
    app.expect('No shared slot is available.', 'fully booked day has no invented slot')
    app.tap('agent_tab')
    app.fill('question', '   ')
    app.tap('ask_agent')
    app.expect('Enter a question first.', 'empty agent question refused')
    app.fill('question', 'Is there any shared time available?')
    app.tap('ask_agent')
    app.expect('Agent unavailable:', 'honest standalone host error')
    app.expect('Is there any shared time available?', 'submitted question survives host error')
    app.capture('04-agent-unavailable.png')
    app.tap('plan_tab')
    app.tap('reset_demo')
    app.expect('Fictional calendars restored.', 'reset confirms fixture restoration')
    check(app.state() == {'version': 1, 'extra_conflict': False, 'all_busy': False,
                          'booking': None, 'activity': []}, 'meeting: reset clears simulated conflicts and booking')
    app.clean_logs()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'build'/time.strftime('%Y%m%d-%H%M%S')/'native-results.json')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Preserve state and logs for inspection, including failed runs.
    with nullcontext(tempfile.mkdtemp(prefix='state-', dir=args.output.parent)) as tmp:
        apps = [App(name, Path(tmp)) for name in ('email-action', 'meeting-planner')]
        try:
            email(apps[0].launch())
            meeting(apps[1].launch())
            for app in apps:
                app.close()
                gate = subprocess.run([str(OCTO), 'check', str(app.bundle)], capture_output=True, text=True)
                (args.output.parent / (app.name + '-gate.txt')).write_text(gate.stdout + gate.stderr)
                check(gate.returncode == 0, app.name + ': final App Hub gate')
        except Exception as exc:
            CHECKS.append({'check': 'execution completed', 'passed': False, 'error': str(exc)})
            raise
        finally:
            for app in apps:
                if app.port is not None:
                    app.close()
            artifacts = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for app in apps for p in sorted(app.bundle.rglob('*')) if p.is_file()}
            args.output.write_text(json.dumps({'scope': 'desktop native / offline and agent-unavailable only',
                'checks': CHECKS, 'inputs': {app.name: app.inputs for app in apps}, 'sha256': artifacts}, indent=2)+'\n')
    print(f'{sum(c["passed"] for c in CHECKS)}/{len(CHECKS)} checks passed; {args.output}')


if __name__ == '__main__':
    main()
