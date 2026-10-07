#!/usr/bin/env python3
"""Native Mac Inbox soak in an already-owned, signed synthetic Gmail profile.

Start launch_integrated.py and accept normal agent consent first. This driver
uses pointer/key/text input, never writes a host draft or approves a send. Raw
receipts and captures remain under the explicitly supplied private profile.
"""
import argparse, hashlib, json, math, socket, statistics, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError

HERE = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--profile-root', type=Path, required=True)
p.add_argument('--octosense', type=Path, required=True)
p.add_argument('--kernel', type=Path, required=True)
p.add_argument('--port', type=int, default=8395)
p.add_argument('--cycles', type=int, default=33)
p.add_argument('--run-name', default='soak')
p.add_argument('--reuse-model-case', action='store_true', help='Reuse this same isolated profile’s completed real model edit; no new model turn')
p.add_argument('--duration-seconds', type=float, default=610)
a = p.parse_args()
assert a.cycles >= 1 and a.duration_seconds >= 0
assert a.run_name and a.run_name.replace('-', '').replace('_', '').isalnum()
root=a.profile_root.resolve(); host=root/'apps/.host'; out=root/a.run_name
assert not out.exists(), 'Choose a fresh --run-name; failed evidence is never overwritten'
out.mkdir()
assert json.loads((root/'apps/.connected-e2e.json').read_text())['fixture']=='connected-e2e'
assert json.loads((host/'acceptance-inbox.json').read_text())['synthetic_gmail']
base=f'http://127.0.0.1:{a.port}/'; timings=[]; cycles=[]; captures={}; input_errors=[]; owned=int((root/'pid').read_text())
driver_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
started=time.monotonic(); baseline=None; result={'status':'running','visual_status':'requires_original_pixel_review','scope':'macOS full Shell; real DeepSeek, synthetic Gmail; no real OAuth or send'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(name,value): (out/name).write_text(json.dumps(value,indent=2)+'\n')
def call(route,**params):
    start=time.perf_counter()
    try:
        with urlopen(base+route+('?' + urlencode(params) if params else ''),timeout=15) as r: value=json.load(r)
        request_ms=(time.perf_counter()-start)*1000
    except HTTPError as error:
        # remote.rs poll_with_present applies Cmd::Input BEFORE trying present.
        # Its explicit submission error thus cannot authorize replaying input.
        # Record failed acknowledgement, recover read-only pixels, and require
        # the unchanged downstream exact-state assertions to pass.
        body=error.read().decode('utf-8',errors='replace')
        request_ms=(time.perf_counter()-start)*1000
        detail={'route':route,'parameters':params,'status':error.code,'body':body,'milliseconds':round(request_ms,3)}
        input_errors.append(detail);write('input-errors.json',input_errors)
        known={'{"err":"timeout (app busy or not running its event loop)"}', '{"err":"requested input frame could not be submitted; retry"}'}
        if route not in ('click','m','k','t') or body not in known:
            raise RuntimeError('Native instrument HTTP error: '+json.dumps(detail)) from error
        value={'frame_wait_error':True}
        print(json.dumps({'stage':'native_frame_error','detail':detail}),flush=True)
        capture(f'input-error-{len(input_errors):02d}.png')
        assert call('s')['pid']==owned
    if 'err' in value: raise RuntimeError(value['err'])
    if route in ('click','m','k','t'):
        timings.append({'route':route,'milliseconds':request_ms,'frame':value.get('f'),'frame_wait_error':value.get('frame_wait_error',False)})
    return value

def wait_for(predicate,label,seconds=15):
    deadline=time.monotonic()+seconds
    while True:
        value=predicate()
        if value:return value
        if time.monotonic()>deadline:raise AssertionError('Timeout: '+label)
        time.sleep(.04)

def draft():
    values=[d for f in (host/'oauth/inbox').glob('*/*.json') for d in json.loads(f.read_text())['drafts'].values()]
    return values[0] if values else None

def click(x,y): call('click',x=x,y=y,wait=1)
def replace(x,y,value):
    click(x,y);call('k',k='down',c='KeyA',cmd=1,wait=1);call('k',k='up',c='KeyA',cmd=1,wait=1)
    if value:call('t',t=value,wait=1)
    else:call('k',k='down',c='Backspace',wait=1);call('k',k='up',c='Backspace',wait=1)
def scroll(x,y,dy):call('m',k='scroll',x=x,y=y,dy=dy,dx=0,precise=1,wait=1)
def capture(name):
    for attempt in range(3):
        try:g=call('g');break
        except Exception:
            if attempt==2:raise
            time.sleep(.1)
    data=Path(g['png']).read_bytes();assert data.startswith(b'\x89PNG\r\n\x1a\n');(out/name).write_bytes(data)
    captures[name]={'sha256':sha(data),'native_pixels':g['sz'],'binary_sha256':(root/'active-binary.sha256').read_text().strip()}
    write('captures.json',captures)
def rss_kib():return int(subprocess.check_output(['ps','-o','rss=','-p',str(owned)],text=True).strip())
def provider_clean():
    state=json.loads((host/'acceptance-inbox.json').read_text());assert state['denied_send_attempts']==0
    d=draft();assert d and not d['attempts'];return state

def await_status(status):return wait_for(lambda:draft() if draft() and draft()['status']==status else None,status)
def open_review():
    click(845,791);await_status('awaiting_approval')
def cancel_review():
    click(549,792);await_status('draft')
def reopen():
    click(1243,16);click(1190,150)
def stop():
    global owned
    try:
        if call('s')['pid']==owned:call('quit')
    except Exception:pass
    for _ in range(100):
        with socket.socket() as s:
            if s.connect_ex(('127.0.0.1',a.port))!=0:return
        time.sleep(.05)
    raise AssertionError('Owned shell did not close its port')
try:
    def ready_window():
        try:
            info=call('s')
            return info if info['pid']==owned and info.get('w') else None
        except Exception:return None
    info=wait_for(ready_window,'owned native window ready',30)
    size=info['w'][0]['sz'];assert size[0]==1400 and 898<=size[1]<=900,size
    wait_for(lambda: json.loads((host/'inbox-e2e-receipt.json').read_text())['result'].get('phase')=='events_processed','incoming model triage',180)
    kernel_logs='\n'.join(f.read_text() for f in (root/'home/octos-home/.octos/logs').glob('serve*.log'))
    assert 'provider=deepseek' in kernel_logs and 'model=deepseek-v4-flash' in kernel_logs, 'This recorded DeepSeek soak needs an actual matching kernel trace'
    state=next(json.loads(f.read_text()) for f in (host/'oauth/inbox-events').glob('*/*.json'))
    assert not state['pending'] and set(state['completed'])=={'fixtureclinic20261006','fixturenewsletter20261006'}
    cards=json.loads((host/'mail-notifications/outbox.json').read_text());assert len(cards)==1 and cards[0]['key'].endswith('/fixtureclinic20261006')
    wait_for(lambda:'New-mail baseline ready' in json.dumps(call('snap')),'visible baseline status refresh',10)
    result['monitoring_status_refreshed_without_manual_refresh']=True
    capture('01-summary.png');click(1190,150);wait_for(draft,'Glance draft creation')
    # Read actual peer tools, never synthesize or overwrite a model turn.
    def completed_model_body():
        for f in (root/'apps/org.octosense.samples.inbox').rglob('*.jsonl'):
            rows=[json.loads(line) for line in f.read_text().splitlines()]
            edits=[t for row in rows for t in row.get('tool_calls',[]) if t.get('name')=='inbox_draft_edit']
            if edits and rows[-1].get('role')=='assistant' and not rows[-1].get('tool_calls'):
                return edits[-1]['arguments']['body']
        return None
    if a.reuse_model_case:
        baseline=completed_model_body()
        assert baseline and draft()['reply']['body'].startswith(baseline)
        click(669,267)
    else:
        click(481,791)
        replace(650,570,'Thank you. I confirm Tuesday, October 13 at 9:00 AM Pacific.\nI will bring my medication list.')
        click(669,267);wait_for(lambda:draft()['revision']==2,'human draft save')
        replace(650,762,'Please change my reply to ask for 10:30 AM Pacific instead of 9:00 AM on Tuesday, October 13. Keep the sentence about bringing my medication list. Do not send.')
        click(964,792);wait_for(lambda:draft()['revision']>=3 and '10:30' in draft()['reply']['body'],'real model draft edit',120)
        baseline=wait_for(completed_model_body,'actual peer terminal response',120)
        assert draft()['reply']['body']==baseline
    capture('02-model-chat.png');click(593,267);assert 'medication list' in baseline and '10:30' in baseline
    initial_revision=draft()['revision'];initial_model_body_hash=sha(baseline.encode());timings.clear();soak_started=time.monotonic();initial_rss=rss_kib()
    print(json.dumps({'stage':'soak_started','cycles':a.cycles,'minimum_duration_seconds':a.duration_seconds,'initial_revision':initial_revision,'rss_kib':initial_rss}),flush=True)
    for number in range(1,a.cycles+1):
        cycle_start=time.monotonic();rev=draft()['revision'];prior_calls=len(timings)
        expected=baseline+'\n'+('\n'.join(f'Soak {number:02d}, line {i:02d}: test note — café, 谢谢。' for i in range(1,25)) if number%2==0 else f'Soak {number:02d}: native edit — café, 谢谢。')
        click(593,267);replace(650,570,expected);scroll(650,600,380);scroll(650,600,-380);click(549,792)
        wait_for(lambda:draft()['revision']==rev+1 and draft()['reply']['body']==expected,'exact native edit saved')
        click(669,267);replace(650,762,f'Unsent composer probe {number:02d}');scroll(650,620,420);scroll(650,620,-420)
        click(514,267);scroll(650,600,350);scroll(650,600,-350);click(669,267);replace(650,762,'');click(593,267)
        click(650,570);open_review();scroll(650,600,500)
        call('t',t='MODAL_INPUT_MUST_NOT_REACH_DRAFT',wait=1);click(669,267)
        if number in (1,a.cycles) or number%10==0:
            click(845,792);capture(f'cycle-{number:02d}-review.png')
        cancel_review();click(549,792)
        assert draft()['revision']==rev+1 and draft()['reply']['body']==expected
        if number%5==0:
            open_review();click(990,109);await_status('draft')
        else:click(990,109)
        reopen();click(593,267)
        assert draft()['revision']==rev+1 and draft()['reply']['body']==expected
        provider_clean()
        if number in (1,a.cycles) or number%10==0:capture(f'cycle-{number:02d}-reply.png')
        active=time.monotonic()-cycle_start;target=soak_started+number*a.duration_seconds/a.cycles;idle=max(0,target-time.monotonic())
        time.sleep(idle)
        assert draft()['revision']==rev+1 and draft()['reply']['body']==expected
        row={'cycle':number,'revision':rev+1,'body_sha256':sha(expected.encode()),'characters':len(expected),'active_seconds':round(active,3),'idle_seconds':round(idle,3),'elapsed_seconds':round(time.monotonic()-soak_started,3),'native_inputs':len(timings)-prior_calls,'rss_kib':rss_kib(),'passed':True}
        cycles.append(row);write('cycles.json',cycles);print(json.dumps(row),flush=True)
    final_body=draft()['reply']['body'];final_revision=draft()['revision'];capture('03-before-restart.png');stop()
    subprocess.run(['python3',str(HERE/'launch_integrated.py'),'--restart','--octosense',str(a.octosense),'--profile-root',str(root),'--kernel',str(a.kernel),'--port',str(a.port)],check=True)
    owned=int((root/'pid').read_text())
    def new_shell():
        try:return call('s')['pid']==owned
        except Exception:return False
    wait_for(new_shell,'cold shell startup',30);wait_for(lambda:draft()['status']=='draft','cold saved draft')
    time.sleep(1);capture('04-cold-summary.png');click(1190,150);time.sleep(.5);click(593,267);capture('05-cold-reply.png')
    assert draft()['revision']==final_revision and draft()['reply']['body']==final_body
    open_review();scroll(650,600,500);capture('06-cold-review.png');cancel_review();assert draft()['revision']==final_revision
    provider=provider_clean();result.update(status='functional_checks_passed',cycles=len(cycles),sustained_seconds=round(cycles[-1]['elapsed_seconds'],3),model='real DeepSeek deepseek-v4-flash',model_case='prior completed edit in this same profile' if a.reuse_model_case else 'one fresh chat edit before native soak',initial_model_body_sha256=initial_model_body_hash,final_revision=final_revision,final_body_sha256=sha(final_body.encode()),restart_exact_body=True,provider_send_attempts=provider['denied_send_attempts'],first_failure=None)
except BaseException as error:
    result.update(status='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',error=str(error),completed_cycles=len(cycles))
    try:capture('FIRST-FAILURE.png')
    except Exception:pass
    raise
finally:
    values=sorted(x['milliseconds'] for x in timings)
    if values:result['native_frame_wait_rtt_ms']={'count':len(values),'p50':round(statistics.median(values),3),'p95':round(values[max(0,math.ceil(len(values)*.95)-1)],3),'max':round(max(values),3),'meaning':'HTTP native input with wait=1; not FPS or display latency'}
    if cycles:result['rss_kib']={'start':initial_rss,'end':cycles[-1]['rss_kib'],'min':min(x['rss_kib'] for x in cycles),'max':max(x['rss_kib'] for x in cycles),'meaning':'process RSS, includes full Shell, renderer and capture caches; finite-run trend is not a leak verdict'}
    result['instrument_errors']=input_errors
    result['zero_instrument_timeouts']=not input_errors
    result['performance_context']='Concurrent other native soaks and Android compilation; not an idle benchmark'
    if input_errors:result['responsiveness_status']='failed: observed native instrument errors'
    else:result['responsiveness_status']='no instrument error observed in this run'
    result.update(recorded_at=datetime.now(timezone.utc).isoformat(),driver_sha256=driver_hash,binary_sha256=(root/'active-binary.sha256').read_text().strip(),model_run_binary_sha256=(root/'binary-at-model-run.sha256').read_text().strip(),glance_card_source_sha256=sha((a.octosense/'crates/shell/src/glance_card.rs').read_bytes()),instrument_source_sha256=sha((a.octosense/'.sources/makepad/platform/src/remote.rs').read_bytes()),app_source_sha256=sha((HERE/'bundle/main.splash').read_bytes()),bundle_digest=next(x['bundle_digest'] for x in json.loads((root/'apps/.connected-e2e.json').read_text())['apps'] if x['id']=='org.octosense.samples.inbox'),captures=captures,live_google_oauth=False,physical_approval=False,real_delivery=False,android=False)
    write('soak-receipt.json',result);write('native-input-timings.json',timings)
    stop()
