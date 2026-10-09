#!/usr/bin/env python3
"""Exercise real hidden card-host input, error fallback and restart; no model."""
import argparse, hashlib, json, os, shutil, socket, subprocess, time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    hosts=p.add_mutually_exclusive_group(required=True)
    hosts.add_argument('--card-host', type=Path)
    hosts.add_argument('--host', type=Path, help='Current OctoSense app-tool-acceptance preview runner')
    p.add_argument('--hub', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False, mode=0o700)
    result = {'result': 'failed', 'verified': [], 'not_verified': ['model/provider calls', 'Glance publication and expansion', 'phone', 'agent tools']}
    child = None
    try:
        host, hub = (a.card_host or a.host).resolve(), a.hub.resolve()
        if not host.is_file() or not hub.is_file():
            raise RuntimeError('Supply existing native card-host and hub binaries')
        bundle = a.output / 'bundle'
        shutil.copytree(HERE / 'bundle', bundle)
        result['runner'] = 'card-host' if a.card_host else 'app-tool-acceptance preview (real SDK; no live services)'
        result['binary_sha256'] = sha(host)
        result['source_sha256'] = sha(bundle / 'main.splash')
        result['driver_sha256'] = sha(__file__)
        expected_note = 'Plan a quiet afternoon.\n社区散步，不发送邮件。'
        expected_summary = 'A quiet walk at 16:30 — bring water. 社区。'
        env = dict(os.environ, MAKEPAD_HIDE_WINDOWS='1', MAKEPAD_SYSTEM_FONTS='0',
                   OCTOSENSE_HOME=str(a.output/'private-shell'), RINX_DATA_DIR=str(a.output/'private-rinx'),
                   OCTOS_APP_CORE_DIR=str(a.output/'private-kernel'), OCTOSENSE_APP_DATA=str(a.output/'private-apps'))
        env.pop('MAKEPAD_FORCE_FOCUS', None)
        env.pop('OCTOSENSE_HUB_ANCHOR', None)
        env.pop('OCTOSENSE_HUB_CATALOG', None)
        def call(route, **params):
            with urlopen(base+route+('?' + urlencode(params) if params else ''), timeout=5) as response:
                value = json.load(response)
            if 'err' in value: raise RuntimeError(value)
            return value
        def find(identity=None, text=None):
            until = time.monotonic()+8
            while time.monotonic()<until:
                for w in call('snap')['s']:
                    if (identity is None or w.get('i')==identity) and (text is None or w.get('t')==text): return w
                time.sleep(.03)
            raise AssertionError((identity, text))
        def click(identity):
            x,y,w,h=find(identity=identity)['r']; call('click',x=x+w/2,y=y+h/2,wait=1)
        def edit(identity, text):
            click(identity); call('k',k='down',c='KeyA',cmd=1,wait=1); call('k',k='up',c='KeyA',cmd=1,wait=1)
            call('k',k='down',c='Backspace',wait=1); call('k',k='up',c='Backspace',wait=1)
            if text: call('t',t=text,wait=1)
        def status(fragment):
            until=time.monotonic()+8
            while time.monotonic()<until:
                if fragment in find(identity='status').get('t',''): return
                time.sleep(.03)
            raise AssertionError((fragment, find(identity='status')))
        def capture(name):
            previous=None
            for _ in range(6):
                time.sleep(.08)
                with urlopen(base+'g?raw=1',timeout=10) as response:data=response.read()
                if not data.startswith(b'\x89PNG'):raise AssertionError('Not a native PNG')
                if data==previous:break
                previous=data
            (a.output/name).write_bytes(data)
            (a.output/(name+'.json')).write_text(json.dumps(call('snap'),indent=2)+'\n')
        for phase in ['first','restart']:
            with socket.socket() as sock: sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
            base=f'http://127.0.0.1:{port}/'; env['MAKEPAD_REMOTE']=str(port)
            if a.card_host:
                command=[str(host),'--bundle',str(bundle),'--app-data',str(a.output/'state'),'--allow-unsigned','--stamp']
            else:
                subprocess.run([str(hub),'stamp',str(bundle)],check=True,capture_output=True)
                command=[str(host),'--preview','--bundle='+str(bundle),'--app-data='+str(a.output/'state'),
                         '--receipt='+str(a.output/(phase+'-native.json')),'--trigger-file='+str(a.output/(phase+'-trigger'))]
            with (a.output/(phase+'.log')).open('w') as log:
                child=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT)
            until=time.monotonic()+45
            while time.monotonic()<until:
                if child.poll() is not None: raise RuntimeError('Native host exited; inspect '+phase+'.log')
                try:
                    find(identity='note'); break
                except (OSError, ValueError, AssertionError): time.sleep(.1)
            else: raise AssertionError('Native startup timeout')
            if phase=='first':
                find(identity='note', text='Plan a quiet afternoon walk.')
                edit('note','');click('generate');status('Write a note first.')
                edit('note',expected_note);click('publish');status('Add a summary before publishing.')
                edit('summary',expected_summary);click('keep');status('Saved locally')
                capture('01-editor.png')
                click('generate');status('no service answers "model"')
                find(identity='summary',text=expected_summary)
                click('publish');status('no service answers "glance"')
                find(identity='summary',text=expected_summary)
                click('withdraw');status('Cannot withdraw:')
                capture('02-unavailable.png')
                result['verified'] += ['populated first frame','empty note and summary refusal','native multiline Unicode editing','local save','real missing-model fallback preserves draft','real missing-Glance fallback preserves draft']
            else:
                find(identity='note',text=expected_note);find(identity='summary',text=expected_summary)
                capture('03-restart.png');result['verified'].append('exact note and summary survive process restart')
            call('quit'); child.wait(timeout=10);child=None
        result['result']='pass'
        result['screenshots_sha256']={p.name:sha(p) for p in a.output.glob('*.png')}
    except Exception as exc:
        result['error']=str(exc)
    finally:
        if child is not None:
            try: call('quit');child.wait(timeout=5)
            except Exception:
                child.terminate()
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5)
        (a.output/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result['result']=='pass' else 1
if __name__=='__main__':raise SystemExit(main())
