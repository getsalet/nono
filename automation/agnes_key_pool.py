"""Secret-name-only credential routing. Never persist credentials or fingerprints."""
import datetime as dt,json,os,re,threading,urllib.error,urllib.request
from pathlib import Path
NAMES=('AGNES_API_KEY',*(f'AGNES_API_KEY{i}' for i in range(2,26)))
DEFAULT_BASE='https://apihub.agnes-ai.com/v1'

class AgnesKeyPool:
 def __init__(self,environ=None,report_path=None,now=None,base=None):
  env=os.environ if environ is None else environ
  self.base=(base or env.get('AGNES_API_BASE')or env.get('AGNES_BASE')or DEFAULT_BASE).rstrip('/')
  self._lock=threading.RLock();self._disabled=set();self._cursor=0;self.slots={}
  entries=[]
  for name in NAMES:
   value=env.get(name,'').strip()
   if value and not re.search(r'[,\s]',value):entries.append((name,value));self.slots.setdefault(value,name)
  for i,value in enumerate(re.split(r'[,\s]+',env.get('AGNES_API_KEYS',''))):
   if value:entries.append((f'AGNES_API_KEYS[{i+1}]',value));self.slots.setdefault(value,f'AGNES_API_KEYS[{i+1}]')
  blocked=set();healthy_names=None
  try:
   path=Path(report_path)if report_path else Path(__file__).resolve().parents[1]/'data/agnes-key-health/latest.json'
   report=json.loads(path.read_text());tested=dt.datetime.fromisoformat(report['tested_at']);age=((now or dt.datetime.now(dt.timezone.utc))-tested).total_seconds()
   if report.get('complete') is True and report.get('endpoint')==self.base+'/chat/completions':
    healthy_names={r['secret_name']for r in report.get('keys',[])if r.get('status')=='healthy'and r.get('http_status')==200}
   if healthy_names is not None and 0<=age<=21600:
    names={r['secret_name']for r in report.get('keys',[])if r.get('status')=='authentication_rejected'and r.get('http_status')==401}
    blocked={v for n,v in entries if n in names}
  except (OSError,ValueError,TypeError,KeyError):pass
  if env.get('AGNES_HEALTHY_SLOTS_ONLY')=='1':
   if healthy_names is None:raise RuntimeError('Complete matching Agnes health audit required before healthy-only routing')
   allowed={v for n,v in entries if n in healthy_names}
   entries=[(n,v)for n,v in entries if v in allowed]
  preferred=[n for n in re.split(r'[,\s]+',env.get('AGNES_PREFERRED_KEY_SLOTS',''))if n]
  if any(n not in NAMES for n in preferred):raise RuntimeError('Unknown preferred Agnes secret slot name')
  entries=sorted(enumerate(entries),key=lambda row:(preferred.index(row[1][0])if row[1][0]in preferred else len(preferred),row[0]))
  self.keys=list(dict.fromkeys(v for _,(_,v)in entries if v not in blocked))
  if env.get('AGNES_HEALTHY_SLOTS_ONLY')=='1'and not self.keys:raise RuntimeError('No configured credential passed the latest Agnes text audit')
 def next(self):
  with self._lock:
   active=[k for k in self.keys if k not in self._disabled]
   if not active:raise RuntimeError('No active Agnes credentials; replace rejected repository secrets and rerun health audit')
   key=active[self._cursor%len(active)];self._cursor+=1;return key
 def disable(self,key,status):
  # 403 can be a model/scope denial; 429/503 must never blacklist credentials.
  if status!=401 or key not in self.keys:return False
  with self._lock:self._disabled.add(key)
  return True
 def fetch_json(self,url,headers=None,payload=None,timeout=180):
  headers=dict(headers or {});key=next((v[7:]for n,v in headers.items()if n.lower()=='authorization'and v.startswith('Bearer ')),None)
  managed=url.startswith(self.base+'/')and key in self.keys
  for _ in range(len(self.keys)+1 if managed else 1):
   req=urllib.request.Request(url,data=json.dumps(payload,ensure_ascii=False).encode()if payload is not None else None,headers=headers)
   try:
    with urllib.request.urlopen(req,timeout=timeout)as response:return json.load(response)
   except urllib.error.HTTPError as exc:
    status=exc.code;exc.close()
    if managed and status==401:
     self.disable(key,status);key=self.next();headers={n:v for n,v in headers.items()if n.lower()!='authorization'};headers['Authorization']='Bearer '+key;continue
    raise RuntimeError(f'Agnes/provider HTTP {status}; raw response withheld')from None
   except urllib.error.URLError:
    raise RuntimeError('Agnes/provider transport failure; private details withheld')from None
  raise RuntimeError('Agnes authentication fallback exhausted')
