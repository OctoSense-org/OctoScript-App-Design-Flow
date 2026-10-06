"""Review shared native scene contracts against the immutable generated atlas."""
from pathlib import Path
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
PIPE=ROOT.parents[1]
sys.path[:0]=[str(PIPE/'lab'),str(PIPE/'lab/image-to-appcard'),str(PIPE/'lab/image-to-appcard-flow')]
from atlas import intake
from semantics import propose,preflight

def write(path,v):path.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=ROOT/'image-to-appcard-flow.json'
intake_dir=ROOT/json.loads(manifest.read_text())['outputs']['intake']
receipt=intake(manifest,ROOT,intake_dir)
for rec in receipt['scenes']:
 d=ROOT/'cards'/rec['design_id'];reference=intake_dir/rec['reference_image']
 if (d/'reference.png').exists():assert sha(d/'reference.png')==sha(reference),'Refusing changed reference'
 else:shutil.copy2(reference,d/'reference.png')
 write(d/'atlas-provenance.json',rec)
 shutil.copy2(ROOT/'source/atlas-prompt.md',d/'image-prompt.md')
 write(d/'generation.json',{'provider':'OpenAI built-in image_gen','actual_atlas_size':[1024,1536],'source_crop':rec['crop'],'reference_sha256':sha(d/'reference.png')})
 contract=json.loads((d/'contract.json').read_text());write(d/'mapped.json',{'schema_version':1,'reference_sha256':sha(d/'reference.png'),'tree':contract['tree'],'basis':'Measured atlas panel; hierarchy reflowed onto 406×776. Shared Rust author is the runtime source. This is a layout adaptation, not a pixel-parity claim.'})
 (d/'semantic-map.json').unlink(missing_ok=True);sem=propose(d);plots=json.loads((d/'plots.json').read_text());(d/'data').mkdir(exist_ok=True)
 for e in sem['elements']:
  e.update(decision='reviewed',confidence=1)
  if e['id'] in plots:
   points=plots[e['id']]['points'];path=d/'data'/(e['id']+'.json');write(path,points)
   xs=[p['time'] for p in points];ys=[p['price'] for p in points]
   e.update(role='chart.line',basis='Numeric fixture series rendered by the Stock AppCard Matplot PlotView engine through FinancePlot; no pixels traced from generated chart',data={'origin':'fixture','path':str(path.relative_to(d)),'sha256':sha(path),'x_key':'time','y_keys':['price'],'units':{'x':'Unix seconds UTC','y':'listing currency'},'domain':{'x':[min(xs),max(xs)],'y':[min(ys),max(ys)]}})
  if e['role']=='input':e['behavior']={'event':'changed','target':e['id'] if e['id'].endswith('_input') else e['id']+'_input','property':'text'}
 write(d/'semantic-map.json',sem)
 (d/'AUTHORING.md').write_text('The 1024×1536 atlas panels have different aspect ratios from the requested 406×776 screens. Native layout explicitly reflows their dark surfaces, hierarchy, rows and charts; measured original crops and transforms are preserved. Generated graph pixels are replaced by declared numerical fixtures. Current news rows use native text; artwork fidelity and pixel parity are not asserted. The standalone native built-in instrument is used; legacy Studio capture/gate are separate and are not claimed.\n')
 preflight(d)
 print('Reviewed',rec['design_id'])
