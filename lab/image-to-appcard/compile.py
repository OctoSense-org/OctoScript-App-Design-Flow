#!/usr/bin/env python3
"""Compile a declarative design fixture into native L0 Kit components.

The same L0+JSON loader mounts every page. Artwork may use verified region crops;
UI controls, text and charts require their semantic native renderer. Source
contracts and observed-image annotations stay separate.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from catalogue import HERE, walk
from semantics import preflight
from core.native_paths import repository

ROOT=HERE.parents[1]
GALLERY=ROOT/'docs/reviews/theme-phone-evidence/ux-images'
LAYOUT={'x','y','w','h','src','image_width','image_height'}
PROPS={'text':'text','enabled':'enabled','placeholder':'placeholder','selected':'selected'}

def digest(value):
    return hashlib.sha256(value if isinstance(value,bytes) else json.dumps(value,sort_keys=True).encode()).hexdigest()
def literal(value):
    if isinstance(value,dict):return '{'+','.join(k+':'+literal(v) for k,v in value.items())+'}'
    if isinstance(value,list):return '['+','.join(literal(v) for v in value)+']'
    return json.dumps(value,ensure_ascii=False)

# Historical generated SVGs are retained in per-design assets and capture rounds.
# New compilations consume only explicitly mapped, verified artwork assets.

def compile_page(directory, font_root=None):
    directory=Path(directory).resolve();contract=json.loads((directory/'contract.json').read_text())
    overrides=directory/'mapped.json'
    tree=json.loads(overrides.read_text())['tree'] if overrides.exists() else contract['tree']
    ids=[n['id'] for n in walk(tree)]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate semantic element IDs; repair the source before Studio capture')
    preflight(directory)
    decisions={e['id']:e for e in json.loads((directory/'semantic-map.json').read_text())['elements']}
    assets=directory/'assets';assets.mkdir(exist_ok=True)
    for n in walk(tree):
        if n['t'] not in ('svg','image'):continue
        id=n['id'];asset=directory/decisions[id]['asset']['path']
        content=asset.read_bytes()
        filename=id+'-'+digest(content)[:12]+asset.suffix.lower()
        (assets/filename).write_bytes(content)
        n['src']=f'http://127.0.0.1:8170/ux-images/{contract["id"]}/assets/{filename}'
    pack={'schema_version':1,'theme':'light','tokens':{},'components':{}}
    placements={};copies=[];states=[];definitions={};mapping=[];fonts={}
    def emit(node,depth=0,parent=None,path='beauty_0'):
        id=node['id'];style={k:v for k,v in node.items() if k not in LAYOUT|PROPS.keys()|{'id','c'}}
        role={'stack':'Surface' if 'bg' in node else 'Group','text':'Text','svg':'Vector','button':'NativeButton'}.get(node['t'],node['t'].title())
        if 'kit' in node:role=json.loads(node['kit'])['widget']
        rawstyle=dict(style)
        for k,v in list(style.items()):
            if k in ('color','bg','radius','size','weight','font_src','line_height','font_asc','font_desc','tracking'):
                token=k+'_'+digest(v)[:12];pack['tokens'][token]={'value':v,'property':k};style[k]={'$token':token}
        props={PROPS[k]:k for k in node if k in PROPS}
        component=role+digest([style,props,'c' in node])[:12]
        entry={'style':style,'props':props,'slot':'c' in node}
        pack['components'][component]=entry
        placements[id]={'component':component,'layout':{k:v for k,v in node.items() if k in LAYOUT}}
        params=['instance: text'];args=['component: '+json.dumps(component),'instance: instance'];use=['instance: '+json.dumps(id)]
        for prop,key in props.items():
            typ='bool' if prop in ('enabled','selected') else 'text';params.append(f'{prop}: {typ}');args.append(f'{prop}: {prop}')
            ident=id+'_'+prop
            if typ=='bool':
                states.append(f'state {ident} {{ shape: bool, initial: {str(bool(node[key])).lower()} }}');use.append(f'{prop}: {ident}')
            else:
                copies.append(f'copy {ident} {{ class: user-copy, en: {json.dumps(node[key],ensure_ascii=False)} }}');use.append(f'{prop}: copy.{ident}')
        definitions[component]=f'component {component}('+', '.join(params)+') {\n  view Kit('+', '.join(args)+')'+(' { slot }' if 'c' in node else '')+'\n}\n'
        mapping.append({'source_id':id,'native_id':path,'parent':parent,'kind':node['t'],'component':component,
                        'semantic_role':decisions[id]['role'],
                        'bounds':[node.get(k,0) for k in ('x','y','w','h')],
                        'text':node.get('text'),'enabled':node.get('enabled'),
                        'font':rawstyle.get('font_src'),'size':rawstyle.get('size')})
        if node.get('font_src'):
            src=node['font_src']
            if src.startswith('makepad_widgets:'):
                font=repository('makepad')/'widgets'/src.removeprefix('makepad_widgets:')
            elif src.startswith('self:'):
                base=Path(font_root) if font_root is not None else repository('splash-makepad')/'apps/kit-host'
                font=base/src.removeprefix('self:')
            else:
                raise ValueError(f'Unsupported exact font resource: {src}')
            if not font.is_file():raise ValueError(f'Missing exact font: {font}')
            fonts[node['font_src']]=digest(font.read_bytes())
        result='  '*depth+component+'('+', '.join(use)+')'
        if 'c' in node:result+=' {\n'+'\n'.join(emit(c,depth+1,id,path+'_'+str(i)) for i,c in enumerate(node['c']))+'\n'+'  '*depth+'}'
        return result
    body=emit(tree)
    source=f'# ledger {contract["id"]}@1.0.0\n# level: L0\n# profile: ui/l0\n# Static design fixture, runtime native Kit composition.\ntheme light\n'
    source+='\n'.join(copies+states)+'\n'+''.join(definitions.values())+'\nview root '+body+'\n'
    native=directory/'kit/native/light';native.mkdir(parents=True,exist_ok=True)
    (native/'kit.json').write_text(json.dumps(pack,indent=2)+'\n')
    (native/'components.l0').write_text(''.join(definitions.values()))
    (directory/'page.card').write_text(source)
    runtime=[e for e in decisions.values() if e.get('data') or e.get('behavior')]
    (directory/'page.data.json').write_text(json.dumps({'$kit':{'theme':'light','placements':placements,'bindings':runtime}},indent=2)+'\n')
    (directory/'page.design.splash').write_text(literal(tree)+'\n')
    (directory/'mapping.json').write_text(json.dumps({'schema_version':1,'elements':mapping,'fonts':fonts,
        'contract_sha256':digest((directory/'contract.json').read_bytes()),
        'mapping_basis':'mapped.json' if overrides.exists() else 'requested contract; image measurements gated separately'},indent=2)+'\n')
    publish=GALLERY/contract['id'];publish.mkdir(parents=True,exist_ok=True)
    shutil.copytree(assets,publish/'assets',dirs_exist_ok=True)
    return {'id':contract['id'],'nodes':len(mapping),'native_controls':sum(n['kind']=='button' for n in mapping),'components':len(pack['components'])}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('design',nargs='*');a=p.parse_args()
    for id in a.design or [d['id'] for d in json.loads((HERE/'catalogue.json').read_text())]:print(json.dumps(compile_page(HERE/id)))
