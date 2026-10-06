"""Drive only the Finance process endpoint explicitly passed by its owner."""
import json,time,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def get(base,route,**params):
 u=base+'/'+route+'?'+urllib.parse.urlencode(params)
 with urllib.request.urlopen(u,timeout=30) as response:return json.load(response)
def state():
 for _ in range(20):
  try:return json.loads((ROOT/'runtime/instrument/state.json').read_text())
  except (ValueError,FileNotFoundError):time.sleep(.05)
 raise RuntimeError('missing state')
def rect(base,name):
 ident=state()['mapping'][name]
 return next(v['r'] for v in get(base,'snap',q=ident,all=1)['s'] if v['i']==ident)
def click(base,name):
 x,y,w,h=rect(base,name)
 get(base,'click',x=x+w/2,y=y+h/2,wait=1)
 time.sleep(.25)
 return state()
if __name__=='__main__':
 import sys
 base=sys.argv[1]
 for name in sys.argv[2:]:
  s=click(base,name);print(name,{k:s[k] for k in ['screen','selected','range','inspection']})
