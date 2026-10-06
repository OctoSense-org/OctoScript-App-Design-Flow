#!/usr/bin/env python3
"""Measure immutable AI references with Vision OCR, retaining uncertainty.

OCR is evidence about text pixels, not proof of font identity or full hierarchy.
Non-text bounds require annotations; unannotated graphics cannot silently pass.
"""
import argparse,copy,difflib,functools,json,math,re,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from catalogue import HERE,walk
from compile import ROOT,digest,repository

def norm(s):
    return re.sub(r'\s+',' ',s.replace('•','·').replace('’',"'").replace('“','"').replace('”','"')).strip().casefold()

def light_foreground(node,nodes):
    parents={c['id']:n for n in nodes for c in n.get('c',[])}
    parent=parents.get(node['id']);background=0xffffffff
    while parent:
        surface=next((c for c in parent.get('c',[]) if 'bg' in c),None) if parent.get('kit') else None
        if surface:background=surface['bg'];break
        if 'bg' in parent:background=parent['bg'];break
        parent=parents.get(parent['id'])
    return sum((node['color']>>s)&255 for s in (16,8,0))>sum((background>>s)&255 for s in (16,8,0))

def ocr(path):
    path=Path(path);dest=path.with_suffix('.ocr.json');sha=digest(path.read_bytes())
    if dest.exists():
        old=json.loads(dest.read_text())
        if old.get('image_sha256')==sha:return old
    value=json.loads(subprocess.check_output(['swift','-O',str(HERE/'ocr.swift'),str(path)]))
    value.update(image_sha256=sha,engine='Apple Vision VNRecognizeTextRequest accurate, zh-Hans and en-US')
    dest.write_text(json.dumps(value,indent=2)+'\n');return value


def ocr_label(path,bounds,logical=(406,776)):
    """Disambiguate crowded labels using their independently inspected bounds.

    This is an OCR analysis crop, never a rendered UI asset. The full screenshot
    and WidgetSnapshot still supply independent image/text evidence.
    """
    path=Path(path)
    with Image.open(path) as im:
        sx,sy=im.width/logical[0],im.height/logical[1];x,y,w,h=bounds
        left=max(0,math.floor(x*sx));top=max(0,math.floor(y*sy))
        right=min(im.width,math.ceil((x+w)*sx));bottom=min(im.height,math.ceil((y+h)*sy))
        if right<=left or bottom<=top:return []
        key=digest([digest(path.read_bytes()),bounds]);out=path.parent/'.ocr-labels';out.mkdir(exist_ok=True)
        crop=out/(key+'.png')
        if not crop.exists():im.crop((left,top,right,bottom)).save(crop)
    rows=[]
    for row in ocr(crop)['observations']:
        a,b,c,d=row['bounds'];rows.append(dict(row,bounds=[a+left,b+top,c,d]))
    return rows

def match_text(nodes,observations,scale_x,scale_y):
    pairs=[]
    for node in nodes:
        if node['t']!='text':continue
        for i,obs in enumerate(observations):
            score=difflib.SequenceMatcher(None,norm(node['text']),norm(obs['text'])).ratio()
            if score<.8:continue
            x,y,w,h=obs['bounds'];distance=abs(x/scale_x-node['x'])+abs(y/scale_y-node['y'])
            pairs.append((-(score*1000-distance),node['id'],i,score))
    used=set();matched={}
    for _,id,i,score in sorted(pairs):
        if id in matched or i in used:continue
        matched[id]=(i,score);used.add(i)
    return matched,used

def ink_box(pixels,bounds,logical,light=False,clip=None,min_component_height=None):
    height,width=pixels.shape[:2];sx=width/logical[0];sy=height/logical[1]
    x,y,w,h=bounds;x0=max(0,int(x)-2);y0=max(0,int(y)-2);x1=min(width,math.ceil(x+w)+2);y1=min(height,math.ceil(y+h)+2)
    if clip is not None:
        cx,cy,cw,ch=clip
        x0=max(x0,int(cx*sx));y0=max(y0,int(cy*sy));x1=min(x1,math.ceil((cx+cw)*sx));y1=min(y1,math.ceil((cy+ch)*sy))
    if x1<=x0 or y1<=y0:return [x/sx,y/sy,w/sx,h/sy],None
    crop=pixels[y0:y1,x0:x1,:3].astype(float);lum=crop.mean(axis=2)
    lo,hi=np.percentile(lum,[10,90]);cut=lo+.38*(hi-lo) if not light else lo+.62*(hi-lo)
    mask=lum<cut if not light else lum>cut
    # A loose OCR box may also contain a bright adjacent weather symbol.
    # Keep the text's dominant ink cluster rather than absorbing that artwork.
    if mask.any():
        dominant=np.median(crop[mask],axis=0)
        mask &= np.max(np.abs(crop-dominant),axis=2)<45
    if min_component_height is not None and mask.any():
        import sys
        sys.path.insert(0,str(HERE/'.deps'))
        import cv2
        count,labels,stats,_=cv2.connectedComponentsWithStats(mask.astype('uint8'))
        keep=[i for i in range(1,count) if stats[i,cv2.CC_STAT_HEIGHT]>=min_component_height*sy]
        mask=np.isin(labels,keep)
    ys,xs=np.where(mask)
    if not len(xs):return [x/sx,y/sy,w/sx,h/sy],None
    color=np.median(crop[mask],axis=0).round().astype(int).tolist()
    return [(x0+xs.min())/sx,(y0+ys.min())/sy,(xs.max()-xs.min()+1)/sx,(ys.max()-ys.min()+1)/sy],color

@functools.cache
def metrics(path,text):
    font=TTFont(path);glyphs=font.getGlyphSet();cmap=font.getBestCmap();units=font['head'].unitsPerEm
    cursor=0;bounds=[]
    for ch in text:
        name=cmap.get(ord(ch),'.notdef');pen=BoundsPen(glyphs);glyphs[name].draw(pen)
        if pen.bounds:
            x0,y0,x1,y1=pen.bounds;bounds.append((x0+cursor,y0,x1+cursor,y1))
        cursor+=font['hmtx'].metrics[name][0]
    box=[min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds)]
    return [v/units for v in box],cursor/units,font['hhea'].ascent/units,font['hhea'].descent/units

def observe(directory):
    directory=Path(directory);contract=json.loads((directory/'contract.json').read_text());image=directory/'reference.png'
    data=ocr(image);im=Image.open(image);pixels=np.asarray(im.convert('RGB'));w,h=im.size
    nodes=list(walk(contract['tree']))
    part_path=directory/'text-annotations.json'
    parts=json.loads(part_path.read_text()) if part_path.exists() else {'groups':[]}
    if parts.get('reference_sha256',digest(image.read_bytes()))!=digest(image.read_bytes()):raise ValueError('Stale text group annotations')
    manual={p['id']:(group,p) for group in parts['groups'] for p in group['parts']}
    matched,used=match_text([n for n in nodes if n['id'] not in manual],data['observations'],w/406,h/776)
    for group in parts['groups']:
        candidates=[(i,o) for i,o in enumerate(data['observations']) if norm(o['text'])==norm(group['text'])]
        if not candidates:raise ValueError('Reviewed text group has no matching source OCR')
        i,o=min(candidates,key=lambda io:abs(io[1]['bounds'][1]/(h/776)-group['bounds'][1]))
        used.add(i)
    rows=[]
    for n in nodes:
        if n['t']!='text':continue
        if n['id'] in manual:
            group,part=manual[n['id']]
            rows.append({'id':n['id'],'expected_text':n['text'],'status':'observed','ocr_text':group['text'],
                'confidence':1.0,'text_similarity':1.0,'ink_bounds':part['ink_bounds'],'ink_color':part['ink_color'],
                'light_foreground':part['light_foreground'],'measurement':'reviewed glyph region','group_text':group['text'],
                'group_id':group['id'],'requested_bounds':[n[k] for k in ('x','y','w','h')]})
            continue
        match=matched.get(n['id']);row={'id':n['id'],'expected_text':n['text'],'requested_bounds':[n[k] for k in ('x','y','w','h')]}
        if match:
            i,score=match;o=data['observations'][i];light=light_foreground(n,nodes)
            box,ink=ink_box(pixels,o['bounds'],[406,776],light)
            row.update(status='observed',ocr_text=o['text'],confidence=o['confidence'],text_similarity=score,
                       ink_bounds=box,ink_color=ink,light_foreground=light,ocr_bounds=[o['bounds'][j]/(w/406 if j%2==0 else h/776) for j in range(4)])
        else:row.update(status='missing_or_ocr_unresolved')
        rows.append(row)
    alpha_opaque=im.mode!='RGBA' or im.getextrema()[3]==(255,255)
    manual=directory/'annotations.json';annotations=json.loads(manual.read_text()) if manual.exists() else {}
    if annotations and annotations.get('reference_sha256')!=digest(image.read_bytes()):raise ValueError('Stale image annotations')
    classifications_path=directory/'ocr-classifications.json'
    classifications=json.loads(classifications_path.read_text()) if classifications_path.exists() else {'elements':[]}
    nontext_ocr=[]
    if classifications.get('reference_sha256',digest(image.read_bytes()))!=digest(image.read_bytes()):raise ValueError('Stale OCR classifications')
    for decision in classifications['elements']:
        if not decision.get('reviewed') or decision.get('source_id') not in {n['id'] for n in nodes}:raise ValueError('Unreviewed OCR classification')
        candidates=[i for i,o in enumerate(data['observations']) if o['text']==decision['text'] and o['bounds']==decision['bounds']]
        if len(candidates)!=1:raise ValueError('OCR classification no longer identifies one source observation')
        used.add(candidates[0]);nontext_ocr.append(decision)
    observed={'schema_version':1,'reference_sha256':digest(image.read_bytes()),'artboard':[406,776],
              'opaque':alpha_opaque,'aspect_error':abs((w/h)/(406/776)-1),
              'text':rows,'non_text':annotations.get('elements',[]),
              'unmapped_ocr':[o for i,o in enumerate(data['observations']) if i not in used],
              'non_text_ocr':nontext_ocr,
              'limits':['OCR cannot prove font family, hierarchy or control behavior.','Unannotated non-text elements require visual review.']}
    (directory/'observations.json').write_text(json.dumps(observed,indent=2)+'\n')
    return observed

def map_observations(directory):
    directory=Path(directory);observed=observe(directory);doc=json.loads((directory/'contract.json').read_text())
    tree=copy.deepcopy(doc['tree']);nodes={n['id']:n for n in walk(tree)}
    changes=[]
    for row in observed['non_text']:
        if row['id'] not in nodes:raise ValueError('Annotation targets unknown element: '+row['id'])
        n=nodes[row['id']]
        for k,v in zip(('x','y','w','h'),row['bounds']):n[k]=v
        for k in ('bg','radius','border','bordercolor'):
            if k in row:n[k]=row[k]
        changes.append({'id':n['id'],'source':'observed non-text annotation'})
    for row in observed['text']:
        if row['status']!='observed':continue
        n=nodes[row['id']];x,y,w,h=row['ink_bounds']
        font=repository('splash-makepad')/'apps/kit-host'/n['font_src'].removeprefix('self:')
        (x0,y0,x1,y1),advance,asc,desc=metrics(str(font),n['text'])
        size=h/(y1-y0);tracking=(w-(x1-x0)*size)/max(1,len(n['text'])-1)
        # Use real glyph metrics, not a bitmap label or per-character drawing.
        n.update(x=x-x0*size,y=y-2,w=max(w+4,advance*size+tracking*len(n['text'])+2),h=h+4,
                 size=size,tracking=tracking,line_height=h+4,alignx=0,
                 font_asc=y1+2/size-asc,font_desc=(y1*size+2-(h+4))/size-desc)
        if row['ink_color']:
            r,g,b=row['ink_color'];n['color']=(255<<24)+(r<<16)+(g<<8)+b
        changes.append({'id':n['id'],'source':'Vision OCR ink bounds plus bundled font glyph metrics',
                        'font_family_verified_in_reference':False,'tracking_em':tracking/size})
    (directory/'mapped.json').write_text(json.dumps({'schema_version':1,'reference_sha256':observed['reference_sha256'],
        'tree':tree,'changes':changes,'limits':['Measured fixed artboard; not a responsive production application.']},indent=2)+'\n')
    return {'id':directory.name,'texts':len(observed['text']),'matched':sum(r['status']=='observed' for r in observed['text']),
            'extra_ocr':len(observed['unmapped_ocr']),'opaque':observed['opaque']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('design',nargs='+');p.add_argument('--map',action='store_true');a=p.parse_args()
    for id in a.design:print(json.dumps(map_observations(HERE/id) if a.map else observe(HERE/id)))
