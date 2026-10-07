#!/usr/bin/env python3
"""Operator-owned native regression driver for the DeepSeek-authored examples."""
from pathlib import Path
import hashlib, importlib.util, json, time

REPO=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('sample_driver',REPO/'examples/agentic-hackathon/scripts/verify_native.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
OUT=REPO/'build/deepseek-studio'/time.strftime('%Y%m%d-%H%M%S')
OUT.mkdir(parents=True,exist_ok=True)

def check(condition,label):
    d.check(condition,label); print('PASS',label,flush=True)

class App(d.App):
    def request(self,path,**params):
        result=super().request(path,**params)
        if path in ('/click','/m','/k','/t'):
            time.sleep(.18)
            super().request('/g',raw=1)
        return result
    def nodes(self):
        super().request('/g',raw=1)
        return super().nodes()
    def fill(self,identity,value):
        self.tap(identity=identity)
        self.request('/k',k='press',c='KeyA',cmd=1,wait=1)
        self.request('/k',k='press',c='Backspace',wait=1)
        if value:self.request('/t',t=value,wait=1)
        self.inputs.append({'action':'replace_text','id':identity,'value':value})
    def expect(self,text,label):
        for n in range(24):
            if text in self.text():check(True,self.name+': '+label);return
            self.request('/m',k='scroll',x=210,y=430,dy=180 if n<12 else -180,wait=1)
        self.shot('failure')
        raise AssertionError(label+': missing '+text+'; visible '+self.text())
    def shot(self,label):
        p=OUT/self.name.split('/')[-1]/(label+'.png');p.parent.mkdir(exist_ok=True)
        p.write_bytes(self.request('/g',raw=1));return p
    def anytap(self,identity=None,text=None):
        for attempt in range(26):
            hits=[n for n in self.nodes() if (n.get('i')==identity if identity else n.get('t')==text) and n.get('r',[0]*4)[3]>15]
            if hits:
                n=hits[0];x,y,w,h=n['r'];self.request('/click',x=x+w/2,y=y+h/2,wait=1)
                self.inputs.append({'action':'click','id':n.get('i'),'text':n.get('t'),'rect':n['r']});return
            self.request('/m',k='scroll',x=200,y=350,dy=-180 if attempt<13 else 180,wait=1)
        raise AssertionError('cannot reach '+str(identity or text))
    def restart(self):
        self.request('/quit');self.launch()
    def closed(self):
        self.request('/quit')

def email(a):
    a.expect('Maya Chen','Email populated sender');check(a.state()['outbox']=={},'Email starts with empty outbox');a.shot('01-main')
    a.tap(identity='samplebtn');a.fill('reply','');a.tap(identity='reviewbtn')
    a.expect('Add a reply before reviewing.','Email rejects blank draft');check(a.state()['outbox']=={},'Blank draft creates no delivery')
    a.fill('reply','First draft, Alex.');a.tap(identity='reviewbtn');a.fill('reply','Final reviewed reply, Alex.')
    check(not any(n.get('i')=='confirmbtn' and n.get('r',[0]*4)[3]>0 for n in a.nodes()),'Edit invalidates Email confirmation')
    check(a.state()['drafts']['m1']=='Final reviewed reply, Alex.','Email edits persist before navigating')
    a.tap(identity='reviewbtn');a.shot('02-review');a.tap(identity='confirmbtn')
    delivery=a.state()['outbox']['m1'];check(delivery['body']=='Final reviewed reply, Alex.' and 'maya@example.invalid' in delivery['to'],'Email delivers exact reviewed body to correct recipient');a.shot('03-receipt')
    a.tap(identity='samplebtn');a.tap(identity='reviewbtn');a.tap(identity='confirmbtn')
    check(a.state()['outbox']=={'m1':delivery},'Email duplicate prevention preserves immutable receipt')
    a.tap(identity='openbtn');a.tap(identity='askqbtn');a.expect('Type a question first.','Email blank question visible in full view')
    a.anytap(text='Jordan  <jordan@example.invalid>');check(a.state()['sel']==1,'Selecting Jordan changes stable message identity')
    a.expect('jordan@example.invalid','Jordan action card opened');a.tap(identity='samplebtn');a.tap(identity='reviewbtn');a.tap(identity='confirmbtn')
    check(set(a.state()['outbox'])=={'m1','m2'},'Two reviewed messages have separate deliveries')
    a.tap(identity='undobtn');check(a.state()['outbox']=={'m1':delivery},'Undo removes only Jordan delivery');check(bool(a.state()['drafts']['m2']),'Undo preserves Jordan draft')
    a.tap(identity='askbtn');a.expect('no service answers','Email unavailable fallback is explicit');a.shot('04-unavailable')
    a.restart();check(a.state()['outbox']=={'m1':delivery} and bool(a.state()['drafts']['m2']),'Email receipt and edited drafts survive process restart');a.shot('05-restarted')

def meeting(a):
    a.expect('Design review','Meeting populated initial view');a.shot('01-main')
    a.anytap(identity='cand0');a.tap(identity='reviewbtn');a.expect('busy','Busy slot refused');check(a.state()['bookings']=={},'Busy slot creates no booking')
    a.tap(identity='suggestbtn');check(a.state()['sel']==2,'Offline suggestion chooses first free14:00')
    a.tap(identity='reviewbtn');a.tap(identity='conflictbtn')
    if any(n.get('i')=='confirmbtn' and n.get('r',[0]*4)[3]>0 for n in a.nodes()):a.tap(identity='confirmbtn')
    else:
        a.tap(identity='reviewbtn');a.expect('busy','Changed availability prevents a new review')
    check(a.state()['bookings']=={},'Late conflict rejects stale reviewed slot');a.shot('02-conflict')
    a.anytap(identity='cand3');a.tap(identity='reviewbtn');a.shot('03-review');a.tap(identity='confirmbtn')
    booking=a.state()['bookings'];check(len(booking)==1 and '15:30' in next(iter(booking.values()))['time'],'Meeting stores one15:30 booking');a.shot('04-receipt')
    a.restart();check(a.state()['bookings']==booking,'Meeting booking survives process restart')
    a.tap(identity='reviewbtn')
    if any(n.get('i')=='confirmbtn' and n.get('r',[0]*4)[3]>0 for n in a.nodes()):a.tap(identity='confirmbtn')
    check(a.state()['bookings']==booking,'Meeting duplicate confirmation preserves one booking')
    a.tap(identity='undobtn');check(a.state()['bookings']=={},'Meeting Undo removes saved booking')
    calendar=json.loads((a.state_root/a.app_id/'accounts/device/calendar.json').read_text());check(len(calendar['events'])==4,'Undo preserves original and late-conflict events')
    a.tap(identity='allbusybtn');a.tap(identity='suggestbtn');a.expect('No free candidate slot','No-free-time state visible');check(a.state()['bookings']=={},'All-busy fallback cannot book')
    a.tap(identity='openbtn');a.tap(identity='askqbtn');a.expect('Type a question first.','Meeting blank question visible')
    a.tap(identity='resetbtn');check(a.state()['bookings']=={},'Reset clears demo booking')
    calendar=json.loads((a.state_root/a.app_id/'accounts/device/calendar.json').read_text());check(len(calendar['events'])==3,'Reset restores three fake busy events')
    a.fill('qinput','Which listed free slot works for everyone?');a.tap(identity='askqbtn');a.expect('no service answers','Meeting provider absence explicit');a.shot('05-full-view')

if __name__=='__main__':
    import sys
    records=[]
    try:
        for name,run in [('email-action',email),('meeting-planner',meeting)]:
            if len(sys.argv)>1 and name not in sys.argv[1:]:continue
            a=App('deepseek-studio/'+name,OUT/'state');a.launch()
            try:run(a)
            except Exception:
                a.shot('failure');raise
            finally:
                records.append({'app':name,'source_sha256':hashlib.sha256((a.bundle/'main.splash').read_bytes()).hexdigest(),'inputs':a.inputs})
                a.closed()
    finally:
        (OUT/'checks.json').write_text(json.dumps({'checks':d.CHECKS,'runs':records},indent=2))
