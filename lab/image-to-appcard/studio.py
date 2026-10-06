#!/usr/bin/env python3
"""One persistent Studio bridge; RunItem is the only UI build/run path."""
import argparse,hashlib,json,os,shutil,time,uuid,urllib.request
from pathlib import Path
from PIL import Image
from catalogue import HERE
from compile import ROOT,compile_page,digest,repository

BRIDGE=os.environ.get('BEAUTY_BRIDGE','http://127.0.0.1:8168')
RUN_ITEM='octos-ux-image-studio'
MOUNT=os.environ.get('BEAUTY_STUDIO_MOUNT','splashref')

def request(kind,body,response=None,timeout=30):
    raw=json.dumps({'request':{kind:body},'response':response,'timeout':timeout}).encode()
    with urllib.request.urlopen(urllib.request.Request(BRIDGE,data=raw,headers={'Content-Type':'application/json'}),timeout=timeout+5) as r:data=json.load(r)
    if data.get('error'):raise RuntimeError(f'{kind}: {data["error"]}')
    return data

def write(path,data):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.new')
    tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(path)

def save_viewport_screenshot(shot,target,width=406,height=776,dpi=2.0):
    """Keep the native backing image and crop its measured viewport, never scale."""
    target=Path(target);source=Path(shot['path'])
    raw=target.with_name(target.stem+'-raw.png');shutil.copy2(source,raw)
    viewport=(round(width*dpi),round(height*dpi))
    with Image.open(raw) as pixels:
        if pixels.size!=(shot['width'],shot['height']):raise RuntimeError('Screenshot metadata differs from actual backing pixels')
        if pixels.width<viewport[0] or pixels.height<viewport[1]:raise RuntimeError('Native backing texture is smaller than the requested viewport')
        pixels.crop((0,0,*viewport)).save(target)
    receipt={'schema_version':1,'source':raw.name,'source_sha256':digest(raw.read_bytes()),
             'target':target.name,'target_sha256':digest(target.read_bytes()),
             'build_id':shot['build_id'],'native_backing_px':[shot['width'],shot['height']],
             'viewport_logical':[width,height],'dpi':dpi,'crop_xywh':[0,0,*viewport],
             'resampled':False,'basis':'Actual Studio RunViewResize viewport at origin of backing texture'}
    write(target.with_suffix('.crop.json'),receipt)
    return receipt

def await_semantic_change(read_state,id,before,expected,paint=False):
    deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        current=read_state()['elements'].get(id,{})
        changed=(current!=before and 'before' in current and
                 current['before']!=current.get('after') and current.get('after')==expected)
        # A paint update for the previous probe also changes the state object.
        # Wait for the requested value AND its paint before saving/restoring it.
        painted=(not paint or all(type(current.get(key)) in (int,float) and
                 abs(current[key]-expected)<=1e-6 for key in ('value','painted_value')))
        if changed and painted:return current
        time.sleep(.1)
    raise RuntimeError('Native semantic state/paint did not settle for '+id)

def launch():
    # A restarted host must never write into the previous immutable QA round.
    current=HERE/'current-request.json'
    if current.exists():
        seed=json.loads(current.read_text());startup=HERE/'qa-work/startup'/uuid.uuid4().hex
        startup.mkdir(parents=True)
        for key,name in [('result','native.json'),('layout','layout.json'),('actions','actions.json'),
                         ('semantic_result','semantic-state.json'),('semantic_probe','semantic-probe.json')]:
            seed[key]=str(startup/name)
        seed['nonce']='startup-'+uuid.uuid4().hex
        write(current,seed)
    builds=request('ListBuilds',[],'Builds')['builds']
    for b in builds:
        if b.get('package')==RUN_ITEM:request('ClearBuild',{'build_id':b['build_id']})
    run=request('RunItem',{'mount':MOUNT,'name':RUN_ITEM},'BuildStarted',20)
    write(HERE/'studio-run.json',dict(run,run_item=RUN_ITEM,bridge=BRIDGE,launched_at=time.time()))
    print(json.dumps(run),flush=True)
    return run['build_id']

def capture(id,build):
    directory=HERE/id
    compile_page(directory)
    rounds=directory/'rounds';rounds.mkdir(exist_ok=True)
    round_dir=rounds/f'{1+max((int(p.name) for p in rounds.iterdir() if p.is_dir() and p.name.isdigit()),default=0):03d}';round_dir.mkdir()
    for name in ['page.card','page.data.json','page.design.splash','mapping.json','contract.json']:
        shutil.copy2(directory/name,round_dir/name)
    for name in ['observations.json','annotations.json','generation.json','image-prompt.md','text-annotations.json','ocr-classifications.json','font-fit.json','font-decisions.json','semantic-map.json','semantic-preflight.json']:
        if (directory/name).exists():shutil.copy2(directory/name,round_dir/name)
    shutil.copytree(directory/'kit',round_dir/'kit')
    shutil.copytree(directory/'assets',round_dir/'assets')
    if (directory/'mapped.json').exists():shutil.copy2(directory/'mapped.json',round_dir/'mapped.json')
    shutil.copy2(HERE/'mapping-rules.json',round_dir/'mapping-rules.json')
    for entry in json.loads((directory/'semantic-map.json').read_text())['elements']:
        for key in ('asset','data'):
            relative=entry.get(key,{}).get('path')
            if relative:
                target=round_dir/relative;target.parent.mkdir(parents=True,exist_ok=True)
                if not target.exists():shutil.copy2(directory/relative,target)
    nonce=uuid.uuid4().hex
    r={'card':str(round_dir/'page.card'),'data':str(round_dir/'page.data.json'),'format':'l0-kit',
       'kit_dir':str(round_dir/'kit'),'width':406,'height':776,'result':str(round_dir/'native.json'),
       'layout':str(round_dir/'layout.json'),'actions':str(round_dir/'actions.json'),'nonce':nonce}
    r.update(semantic=str(round_dir/'semantic-map.json'),semantic_result=str(round_dir/'semantic-state.json'),
             semantic_probe=str(round_dir/'semantic-probe.json'),build_id=build)
    write(round_dir/'request.json',r);write(HERE/'current-request.json',r)
    deadline=time.monotonic()+240;resize_at=0
    while time.monotonic()<deadline:
        if time.monotonic()>resize_at:
            request('RunViewResize',{'build_id':build,'window_id':0,'width':406,'height':776,'dpi':2.0});resize_at=time.monotonic()+2
        path=round_dir/'layout.json'
        if path.exists() and json.loads(path.read_text()).get('nonce')==nonce:break
        time.sleep(.25)
    else:
        pending=round_dir/'layout.json.pending.json'
        raise RuntimeError('No settled native layout: '+(pending.read_text() if pending.exists() else 'see Studio logs'))
    native=json.loads((round_dir/'native.json').read_text())
    if native['request']['nonce']!=nonce:raise RuntimeError('Stale host manifest')
    shutil.copy2(round_dir/'semantic-state.json',round_dir/'semantic-baseline.json')
    for kind,name in [('WidgetTreeDump','tree.json'),('WidgetSnapshot','snapshot.json')]:
        reply=request(kind,{'build_id':build},kind)
        if reply.get('build_id')!=build:raise RuntimeError('Stale Studio build in '+kind)
        write(round_dir/name,reply)
    queries={}
    for element in native['elements']:
        query='id:'+element['id'];reply=request('WidgetQuery',{'build_id':build,'query':query},'WidgetQuery')
        if reply.get('build_id')!=build or reply.get('query')!=query:raise RuntimeError('Mismatched widget query')
        queries[element['id']]=reply
    write(round_dir/'queries.json',queries)
    shot=request('Screenshot',{'build_id':build,'kind_id':0},'Screenshot')
    if shot.get('build_id')!=build:raise RuntimeError('Stale screenshot build')
    path=Path(shot['path']);save_viewport_screenshot(shot,round_dir/'native.png');write(round_dir/'screenshot.json',shot)
    # The temporary screenshot belongs to this specific request only.
    if path.parent==Path('/tmp/makepad_studio_hub') and path.name.startswith('build-'):path.unlink(missing_ok=True)
    write(round_dir/'provenance.json',{'build_id':build,'run_item':RUN_ITEM,'nonce':nonce,
        'reference_sha256':digest((directory/'reference.png').read_bytes()) if (directory/'reference.png').exists() else None,
        'files':{str(p.relative_to(round_dir)):digest(p.read_bytes()) for p in round_dir.rglob('*') if p.is_file()},
        'pipeline_sources':{name:digest((HERE/name).read_bytes()) for name in ('semantics.py','mapping-rules.json','compile.py','gate.py','studio.py','../core/policy.py')},
        'runtime_sources':{str(p.relative_to(repository('splash-makepad'))):digest(p.read_bytes()) for base in ['apps/kit-host/src','crates/splash-makepad/src','crates/splash-widgets/src','crates/octoscript-makepad/src','crates/octoscript-widgets/src','crates/makepad-plot/src'] for p in (repository('splash-makepad')/base).rglob('*.rs')}})
    # Publish only after the interaction probes and their receipt are complete.
    print(json.dumps({'id':id,'round':round_dir.name,'build_id':build,'nodes':native['nodes']}),flush=True)
    return round_dir

def click_controls(directory,build):
    directory=Path(directory)
    if (directory/'gate.json').exists():raise ValueError('A gated round is immutable; capture a new round before interaction probes')
    mapping=json.loads((directory/'mapping.json').read_text())['elements']
    manifest=json.loads((directory/'semantic-map.json').read_text())
    bindings={e['id']:e for e in manifest['elements'] if e.get('behavior')}
    actions=directory/'actions.json';results=[];semantic_results=[]
    def state():return json.loads((directory/'semantic-state.json').read_text())
    def evidence(id,suffix):
        request('WidgetSnapshot',{'build_id':build},'WidgetSnapshot')
        shot=request('Screenshot',{'build_id':build,'kind_id':0},'Screenshot')
        path=Path(shot['path']);target=directory/(id+'-'+suffix+'.png');save_viewport_screenshot(shot,target)
        write(directory/(id+'-'+suffix+'.json'),state())
        if path.parent==Path('/tmp/makepad_studio_hub') and path.name.startswith('build-'):path.unlink(missing_ok=True)
        return target.name
    controls=[n for n in mapping if n['kind']=='button']
    # Exercise alternate ranges first; the default selection must also change state.
    controls.sort(key=lambda n:1 if bindings.get(n['source_id'],{}).get('behavior',{}).get('value')==[0,1] else 0)
    for node in controls:
        id=node['source_id'];binding=bindings.get(id)
        x,y,w,h=node['bounds'];before=len(json.loads(actions.read_text()))
        semantic_before=state()['elements'].get(id,{}) if binding else None
        request('Click',{'build_id':build,'x':round(x+w/2),'y':round(y+h/2)})
        if node.get('enabled') is not None and not bool(node['enabled']):
            # Disabled controls are an intentional state (for example, a
            # conflicting appointment). A real click must not activate them.
            deadline=time.monotonic()+.6;found=[]
            while time.monotonic()<deadline:
                events=json.loads(actions.read_text())
                found=[a for a in events[before:] if a.get('action',{}).get('kind')=='activated']
                if found:break
                time.sleep(.1)
            query=request('WidgetQuery',{'build_id':build,'query':'id:'+node['native_id']},'WidgetQuery')
            write(directory/(id+'-disabled-query.json'),query)
            snapshot=request('WidgetSnapshot',{'build_id':build},'WidgetSnapshot')
            write(directory/(id+'-disabled-snapshot.json'),snapshot)
            widgets=[w for w in snapshot.get('widgets',[]) if w.get('id')==node['native_id']]
            disabled=(snapshot.get('build_id')==build and len(widgets)==1 and widgets[0].get('enabled') is False)
            results.append({'id':id,'pass':disabled and not found,'enabled':False,'events':found,
                            'query_evidence':id+'-disabled-query.json',
                            'snapshot_evidence':id+'-disabled-snapshot.json',
                            'scope':'native disabled Button ignores actual Studio click'})
            continue
        if binding:
            current=await_semantic_change(state,id,semantic_before,binding['behavior']['value'])
            passed=current!=semantic_before and current.get('event')=='click' and current.get('after')==binding['behavior']['value']
            semantic_results.append({'id':id,'pass':passed,'state':current,'screenshot':evidence(id,'changed')})
            results.append({'id':id,'pass':passed,'scope':'native Button click changes actual LinePlot viewport'})
            continue
        deadline=time.monotonic()+3;found=[]
        while time.monotonic()<deadline:
            events=json.loads(actions.read_text())
            found=[a for a in events[before:] if a.get('action',{}).get('kind')=='activated']
            if found:break
            time.sleep(.1)
        parent=next(n for n in mapping if n['source_id']==node['parent'])
        passed=any(a.get('id')==parent['native_id'] for a in found)
        results.append({'id':id,'expected_action_owner':parent['native_id'],'pass':passed,'events':found,
                        'scope':'native KitButton activation; no production navigation or data feeds'})
    for id,entry in bindings.items():
        binding=entry['behavior']
        if binding['event']!='value_change':continue
        before=state()['elements'].get(id,{})
        write(directory/'semantic-probe.json',{'id':id,'value':binding['probe_value'],'nonce':uuid.uuid4().hex})
        changed=await_semantic_change(state,id,before,binding['probe_value'],paint=True);shot=evidence(id,'changed')
        passed=changed!=before and changed.get('after')==binding['probe_value']
        write(directory/'semantic-probe.json',{'id':id,'value':binding['value'],'nonce':uuid.uuid4().hex})
        restored=await_semantic_change(state,id,changed,binding['value'],paint=True)
        semantic_results.append({'id':id,'pass':passed and restored.get('after')==binding['value'],
                                 'changed':changed,'restored':restored,'screenshot':shot})
    write(directory/'semantic-interactions.json',{'pass':all(r['pass'] for r in semantic_results),'controls':semantic_results})
    write(directory/'interactions.json',{'pass':all(r['pass'] for r in results+semantic_results),'controls':results})
    proof=json.loads((directory/'provenance.json').read_text())
    proof['files']={str(p.relative_to(directory)):digest(p.read_bytes()) for p in directory.rglob('*') if p.is_file() and p.name!='provenance.json'}
    write(directory/'provenance.json',proof)
    write(directory.parent.parent/'latest.json',{'round':directory.name,'build_id':build,'nonce':proof['nonce']})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('design',nargs='*');p.add_argument('--launch',action='store_true');p.add_argument('--all',action='store_true');a=p.parse_args()
    ids=[d['id'] for d in json.loads((HERE/'catalogue.json').read_text())] if a.all else a.design
    if not ids:raise SystemExit('Provide a design or --all')
    # Seed before RunItem startup so the host can mount on its first frame.
    first=HERE/ids[0];compile_page(first)
    write(HERE/'current-request.json',{'card':str(first/'page.card'),'data':str(first/'page.data.json'),'format':'l0-kit',
        'kit_dir':str(first/'kit'),'width':406,'height':776,'nonce':'startup-'+uuid.uuid4().hex})
    build=launch() if a.launch else json.loads((HERE/'studio-run.json').read_text())['build_id']
    for id in ids:
        directory=capture(id,build);click_controls(directory,build)
