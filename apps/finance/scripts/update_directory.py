"""Refresh public instrument names/codes; this does not grant quote entitlement."""
import csv,hashlib,io,json,re,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=[];sources=[]
for market,gid in [('US','583033325'),('HK','1134034911'),('CN','1702052913')]:
 url=f'https://docs.google.com/spreadsheets/d/1avkeR1heZSj6gXIkDeBt8X3nv4EzJetw4yFuKjSDYtA/export?format=csv&gid={gid}'
 raw=urllib.request.urlopen(url,timeout=30).read()
 for row in csv.reader(io.StringIO(raw.decode('utf8'))):
  if len(row)<2:continue
  code,name=row[0].strip(),row[1].strip()
  if not re.fullmatch(r'[A-Z0-9.-]+\.(US|HK|SH|SZ)',code) or not name:continue
  # Benchmark indices have their own product class; do not present them as stocks.
  if market=='CN' and (code.startswith('399') or code in ('000001.SH','000300.SH')):continue
  rows.append([code,name,market])
 sources.append({'market':market,'url':url,'sha256':hashlib.sha256(raw).hexdigest()})
rows=list({row[0]:row for row in rows}.values())
target=ROOT/'service/data/directory.json';target.parent.mkdir(exist_ok=True)
target.write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':'))+'\n')
(ROOT/'source/directory-provenance.json').write_text(json.dumps({'fetched_at':datetime.now(timezone.utc).isoformat(),'records':len(rows),'sources':sources,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'scope':'Public provider instrument directory; US venue and security class not supplied. Membership is not subscription entitlement.'},indent=2)+'\n')
print(len(rows),'public instrument records')
