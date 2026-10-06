"""Release/native-GPU acceptance through the app's built-in instrument, no Studio."""
import argparse,hashlib,json,re,shutil,subprocess,time,urllib.request
from pathlib import Path
from drive import ROOT,get,state,rect,click
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'evidence/native');args=p.parse_args()
out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
profile=ROOT/'runtime'/('acceptance-'+str(time.time_ns()));profile.mkdir(parents=True)
proof=ROOT/'runtime/instrument';proof.mkdir(parents=True,exist_ok=True)
import os
env={**os.environ,'MAKEPAD_HIDE_WINDOWS':'1','OCTOS_FINANCE_PREVIEW':'1','OCTOS_FINANCE_DATA_DIR':str(profile),'OCTOS_FINANCE_EVIDENCE_DIR':str(proof)}
binary=ROOT/'target/release/octosense-finance';report={'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'mode':'hidden native macOS window / Metal / built-in HTTP instrument','fixture':True,'live_provider_validation':False,'checks':[],'captures':[],'cleanup':[]}
base=None;proc=None;log=None

def start():
 global base,proc,log
 log=open(out/'runtime.log','ab');proc=subprocess.Popen([str(binary),'--remote'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 deadline=time.monotonic()+15
 while time.monotonic()<deadline:
  raw=(out/'runtime.log').read_text(errors='replace');matches=re.findall(r'listening on (127\.0\.0\.1:\d+) pid=(\d+)',raw)
  match=next((m for m in reversed(matches) if int(m[1])==proc.pid),None)
  if match:
   base='http://'+match[0]
   try:
    if get(base,'snap',q='KitButton')['s']:return
   except Exception:pass
  if proc.poll() is not None:raise RuntimeError('native process exited')
  time.sleep(.05)
 raise RuntimeError('native startup timed out')
def capture(name):
 shot=get(base,'g');target=out/(name+'.png');shutil.copy2(shot['png'],target);report['captures'].append({'name':name,'file':target.name,'capture_ms':shot['capture_ms']})
def check(name,ok,**detail):
 report['checks'].append({'name':name,'passed':bool(ok),**detail});assert ok,name
def stop():
 global proc,base,log
 if proc and proc.poll() is None:
  result=get(base,'gq');proc.wait(timeout=15);report['cleanup'].append({'pid':proc.pid,'gq':result.get('quit'),'exit_code':proc.returncode})
 if log:log.close()
 proc=None;base=None
try:
 start();capture('01-watchlist')
 click(base,'stock_0');capture('05-stock-detail');uid=state()['chart_widget_uid'];click(base,'range_2');check('range preserves chart widget',state()['range']=='1M' and state()['chart_widget_uid']==uid)
 x,y,w,h=state()['chart_data_rect'];get(base,'m',k='down',x=x+w*.5,y=y+h/2,wait=1);get(base,'m',k='move',x=x+w*2/3,y=y+h/2,wait=1);get(base,'m',k='up',x=x+w*2/3,y=y+h/2,wait=1)
 check('chart inspection uses fixture sample',state()['inspection']==6 and state()['points'][6]['price']==211,point=state()['points'][6]);capture('06-chart-inspection')
 click(base,'tab_markets');capture('02-markets');click(base,'tab_watchlist');click(base,'search_open');capture('03-search')
 x,y,w,h=rect(base,'search_input');get(base,'click',x=x+35,y=y+h/2,wait=1)
 for char in 'Tencent':get(base,'t',t=char,wait=1);time.sleep(.22)
 inp=get(base,'snap',q='TextInput',all=1)['s'];check('typing retains focus',any(n.get('val')=='Tencent' for n in inp))
 click(base,'tab_watchlist');click(base,'edit');before=state()['watchlist'];click(base,'up_2');check('watchlist reorder',state()['watchlist'][1]==before[2]);capture('04-edit-watchlist');click(base,'done')
 click(base,'search_open');get(base,'m',k='scroll',x=270,y=580,dy=2400,wait=1);time.sleep(.5)
 mapping=state()['mapping'];check('long directory virtualizes rows', 'stock_0' not in mapping and len(mapping)<500,widgets=len(mapping));capture('search-scrolled')
 click(base,'tab_news');capture('08-business-news');click(base,'save_0');saved=state()['saved'];check('bookmark saved',bool(saved));click(base,'tab_saved');capture('10-saved-news');click(base,'story_0');capture('09-reader-chrome');time.sleep(.6)
 get(base,'event',data=json.dumps({'action':'finance.inspect_web','scroll_y':100000}));time.sleep(.8);web=json.loads((proof/'web.json').read_text());check('native WebView full article scroll',web['readyState']=='complete' and web['scrollY']>500 and web['scrollHeight']>web['viewportHeight'],scroll_y=web['scrollY'],content_height=web['scrollHeight'],viewport_height=web['viewportHeight']);shutil.copy2(proof/'web.png',out/'09-reader-webkit.png');shutil.copy2(proof/'web.json',out/'09-reader-webkit.json')
 click(base,'tab_watchlist');click(base,'stock_0');get(base,'m',k='scroll',x=280,y=590,dy=500,wait=1);time.sleep(.3);click(base,'company_news');capture('07-company-news')
 click(base,'tab_settings');capture('11-settings');click(base,'theme');capture('light-theme');click(base,'language');capture('chinese-settings');click(base,'theme');click(base,'language');click(base,'preview');get(base,'m',k='scroll',x=280,y=580,dy=500,wait=1);time.sleep(.3);click(base,'provider_refresh');check('missing provider keys are explicit',all(k in state()['errors'] for k in ['finnhub','tushare']));capture('12-unconfigured-providers')
 # Restore preview, then verify the user's saved preferences survive a new process.
 get(base,'m',k='scroll',x=280,y=300,dy=-1000,wait=1);time.sleep(.3);click(base,'preview');stop();start();check('bookmarks survive restart',state()['saved']==saved);check('watchlist survives restart',state()['watchlist'][1]==before[2]);capture('restart-watchlist');stop();report['passed']=True
except Exception as error:
 report['passed']=False;report['error']=str(error)
 raise
finally:
 try:stop()
 finally:(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'output':str(out)}))
