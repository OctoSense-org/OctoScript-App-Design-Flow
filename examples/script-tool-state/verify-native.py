#!/usr/bin/env python3
"""Verify the real app_tool ABI, native UI and restart using an isolated host."""
import argparse, hashlib, json, os, shutil, socket, subprocess, time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host',type=Path,required=True,help='OctoSense app-tool-acceptance release example')
    parser.add_argument('--hub',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    root=args.output.resolve();root.mkdir(parents=True,exist_ok=False,mode=0o700)
    report={'result':'failed','verified':[],'not_verified':['real model','agent consent and peer relay','public catalog installation','phone','other operating systems']}
    child=None
    try:
        host,hub=args.host.resolve(),args.hub.resolve()
        if not host.is_file() or not hub.is_file():raise RuntimeError('Build app-tool-acceptance and hub first')
        bundle=root/'bundle';shutil.copytree(HERE/'bundle',bundle)
        report.update(binary_sha256=sha(host),source_sha256=sha(bundle/'main.splash'),driver_sha256=sha(__file__))
        env=dict(os.environ,MAKEPAD_HIDE_WINDOWS='1',MAKEPAD_SYSTEM_FONTS='0',RINX_DATA_DIR=str(root/'private-rinx'),OCTOSENSE_HOME=str(root/'private-shell'),OCTOS_APP_CORE_DIR=str(root/'private-kernel'),OCTOSENSE_APP_DATA=str(root/'private-apps'))
        env.pop('MAKEPAD_FORCE_FOCUS',None);env.pop('OCTOSENSE_HUB_ANCHOR',None);env.pop('OCTOSENSE_HUB_CATALOG',None)
        tool_topics='Space weather and community science'
        manual_topics='Community gardens and music. 社区。'
        def call(route,**params):
            with urlopen(base+route+('?' + urlencode(params) if params else ''),timeout=5) as response:value=json.load(response)
            if 'err' in value:raise RuntimeError(value)
            return value
        def find(identity,text=None):
            until=time.monotonic()+8
            while time.monotonic()<until:
                for w in call('snap')['s']:
                    if w.get('i')==identity and (text is None or w.get('t')==text):return w
                time.sleep(.04)
            raise AssertionError((identity,text))
        def click(identity):
            x,y,w,h=find(identity)['r'];call('click',x=x+w/2,y=y+h/2,wait=1)
        def edit(identity,value):
            click(identity);call('k',k='down',c='KeyA',cmd=1,wait=1);call('k',k='up',c='KeyA',cmd=1,wait=1)
            call('t',t=value,wait=1)
        def capture(name):
            previous=None
            for _ in range(6):
                time.sleep(.08)
                with urlopen(base+'g?raw=1',timeout=10) as response:png=response.read()
                if not png.startswith(b'\x89PNG'):raise AssertionError('No native PNG')
                if png==previous:break
                previous=png
            (root/name).write_bytes(png);(root/(name+'.json')).write_text(json.dumps(call('snap'),indent=2)+'\n')
        def stamp():
            r=subprocess.run([str(hub),'stamp',str(bundle)],text=True,capture_output=True)
            if r.returncode:raise RuntimeError(r.stdout+r.stderr)
        stamp()
        for phase in ['preview','tool','restart']:
            with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
            base=f'http://127.0.0.1:{port}/';env['MAKEPAD_REMOTE']=str(port)
            read=phase=='restart'
            expected={'topics':manual_topics if read else tool_topics,'revision':2 if read else 1}
            receipt=root/(phase+'-native.json');trigger=root/(phase+'-trigger')
            command=[str(host),'--bundle='+str(bundle),'--app-data='+str(root/('preview-profile' if phase=='preview' else 'profile')),
                     '--receipt='+str(receipt),'--trigger-file='+str(trigger),
                     '--tool=toolstate.'+('preferences' if read else 'set_preferences'),
                     '--args='+json.dumps({} if read else {'topics':tool_topics}),
                     '--invalid-args='+json.dumps({'unexpected':True}),
                     '--expected='+json.dumps(expected)]
            if phase=='preview':command.append('--preview')
            with (root/(phase+'.log')).open('w') as log:child=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT)
            until=time.monotonic()+50
            while time.monotonic()<until:
                if child.poll() is not None:raise RuntimeError('Host exited; inspect '+phase+'.log')
                try:find('status','Ready; local preferences loaded.');break
                except (OSError,AssertionError,ValueError):time.sleep(.1)
            else:raise AssertionError('Timed out waiting for app load')
            if phase=='preview':
                capture('01-preview.png')
                (bundle/'screenshots').mkdir(exist_ok=True)
                shutil.copyfile(root/'01-preview.png',bundle/'screenshots/01-main.png')
            else:
                if read:find('topics',manual_topics);find('revision','Saved revision: 2')
                trigger.write_text('invoke after native UI loaded\n')
                until=time.monotonic()+20
                while not receipt.exists() and time.monotonic()<until:
                    if child.poll() is not None:raise RuntimeError('Host exited before receipt')
                    time.sleep(.05)
                native=json.loads(receipt.read_text())
                if native['result']!='pass':raise AssertionError(native)
                report[phase]=native
                find('topics',expected['topics']);find('revision','Saved revision: '+str(expected['revision']))
                capture('02-tool.png' if not read else '04-restart.png')
                if not read:
                    edit('topics',manual_topics);click('keep')
                    find('topics',manual_topics);find('revision','Saved revision: 2')
                    capture('03-manual.png')
            call('quit');child.wait(timeout=10);child=None
            if phase=='preview':stamp()
        report['verified']=['real signed admission','actual app_tool request/complete dispatch','exact structured result','tool mutation visible in native UI','manual UI edit shares same state','process restart retains exact Unicode state','invalid input refused','wrong account refused','undeclared tool refused','closed app endpoint refused']
        report['result']='pass'
        report['screenshots_sha256']={p.name:sha(p) for p in root.glob('*.png')}
    except Exception as exc:report['error']=str(exc)
    finally:
        if child is not None:
            try:call('quit');child.wait(timeout=5)
            except Exception:
                child.terminate()
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5)
        (root/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
    return 0 if report['result']=='pass' else 1
if __name__=='__main__':raise SystemExit(main())
