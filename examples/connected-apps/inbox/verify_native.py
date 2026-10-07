#!/usr/bin/env python3
"""Drive an owned hidden card-host fixture; never approves sending."""
import argparse, hashlib, json, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);p.add_argument('--restart-check',action='store_true');p.add_argument('--binary',type=Path);p.add_argument('--out',type=Path);args=p.parse_args()
root=Path(__file__).resolve().parent
out=args.out or root/'evidence';out.mkdir(parents=True,exist_ok=True)
receipt_path=out/('restart-receipt.json' if args.restart_check else 'run-receipt.json')
binary=args.binary or root.parents[3]/'OctoSense-App-Hub/target/release/card-host'
def sha256(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024), b''):digest.update(chunk)
    return digest.hexdigest()
# Verify prerequisites before touching the fixture; a missing binary is never PASS.
try:
    binary_hash=sha256(binary)
except OSError:
    receipt_path.write_text(json.dumps({'recorded_at':datetime.now(timezone.utc).isoformat(),'checks':'not run','status':'failed','reason':'card-host binary missing or unreadable; supply --binary','restart_check':args.restart_check},indent=2)+'\n')
    p.exit(1,'FAIL: card-host binary missing or unreadable; supply --binary. Failure receipt written.\n')
base=f'http://127.0.0.1:{args.port}/'
def call(route,**params):
    with urlopen(base+route+('?' + urlencode(params) if params else '')) as response: data=json.load(response)
    if 'err' in data:raise RuntimeError(data)
    return data
def snap():return [w for w in call('snap')['s'] if w.get('ty')!='Splash']
def find(text=None,identity=None,index=0):
    until=time.monotonic()+3
    while True:
        matches=[w for w in snap() if (text is None or w.get('t')==text) and (identity is None or w.get('i')==identity)]
        if len(matches)>index:break
        if time.monotonic()>until:raise AssertionError((text,identity,matches))
        time.sleep(0.02)
    return matches[index]
def click(text=None,identity=None,index=0):
    w=find(text,identity,index);x,y,width,height=w['r'];call('click',x=x+width/2,y=y+height/2,wait=1)
def text(identity,value):
    click(identity=identity);call('k',k='down',c='KeyA',cmd=1,wait=1);call('k',k='up',c='KeyA',cmd=1,wait=1);call('t',t=value,wait=1)
def capture(name):
    data=call('g');path=Path(data['png']);(out/name).write_bytes(path.read_bytes())
    (out/(name+'.snapshot.json')).write_text(json.dumps(snap(),indent=2)+'\n')
def contains(text):assert any(text in w.get('t','') for w in snap()),text
expected='Please deliver Thursday at 10:30 AM Pacific.\nRing the bell twice. 谢谢。'
assert find(identity='status')['t']=='Fictional inbox · local editing only'
click(text='Open message',index=1)
contains('Choose your refrigerator delivery window')
click(text='Compose reply')
if args.restart_check:
    assert find(identity='reply_body')['t']==expected
    capture('04-restart.png')
    result='PASS restart: exact multiline Unicode draft and message identity retained'
else:
    text('reply_body',expected)
    click(identity='chat_tab')
    contains("Chat with this account's Inbox agent")
    click(identity='reply_tab')
    assert find(identity='reply_body')['t']==expected
    capture('02-reply.png')
    click(identity='chat_tab')
    text('question','Change the delivery time to Friday at 11 AM Pacific.')
    click(text='Ask')
    contains('Assistant unavailable')
    contains('no service answers "octos"')
    capture('03-chat-unavailable.png')
    click(identity='reply_tab')
    assert find(identity='reply_body')['t']==expected
    click(text='Review & Send')
    contains('Fictional draft saved')
    click(text='Back')
    click(text='Connect Google')
    contains('no service answers "auth"')
    click(text='Important')
    assert len([w for w in snap() if w.get('t')=='Open message'])==2
    click(text='Sent')
    contains('No messages in this folder')
    click(text='Inbox')
    capture('01-inbox.png')
    result='PASS startup, second-message identity, multiline Unicode editing, saved Reply/Chat state, unavailable peer/auth, fictional-send block, important and empty folders'
receipt={'recorded_at':datetime.now(timezone.utc).isoformat(),'binary_sha256':binary_hash,'driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'template_sha256':hashlib.sha256((root/'bundle/glance-workspace.splash').read_bytes()).hexdigest(),'screenshots_sha256':{name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in (['04-restart.png'] if args.restart_check else ['01-inbox.png','02-reply.png','03-chat-unavailable.png'])},'source_sha256':hashlib.sha256((root/'bundle/main.splash').read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256((root/'bundle/manifest.json').read_bytes()).hexdigest(),'driver':'Codex via Makepad native instrument','fixture':'fictional sample data only','platform':'macOS hidden card-host 412x892 logical','restart_check':args.restart_check,'checks':'passed; pixel review reported separately','live_oauth':False,'live_model':False,'gmail_delivery':False,'android':False}
receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
print(result)
