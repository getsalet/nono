"""Read one known Actions failure; export only allowlisted diagnostic categories."""
import json,os,re,urllib.request,urllib.error
from pathlib import Path
BASE='https://api.github.com/repos/getsalet/nono/'
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
opener=urllib.request.build_opener(NoRedirect)
def api(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'AFP-bounded-recovery-diagnosis','Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'})
 try:return opener.open(req,timeout=45).read()
 except urllib.error.HTTPError as exc:
  if exc.code!=302:raise
  url=exc.headers['Location']
  if not url.startswith('https://'):raise RuntimeError('Non-HTTPS log redirect refused')
  # Never forward the GitHub credential to the signed blob URL.
  return urllib.request.urlopen(url,timeout=45).read()
rows=[]
for j in json.loads(api('actions/runs/39489558974/jobs?per_page=100'))['jobs']:
 if j['conclusion']!='failure':continue
 raw=api('actions/jobs/'+str(j['id'])+'/logs').decode('utf-8','replace')
 categories=[]
 for known in ['Native login rejected (visual_challenge)','Native login rejected (authentication)','Native edit form action not confirmed','Native title is absent or ambiguous','Native body does not match known draft','Public mismatch is not the diagnosed wording-only change','Edit slug identity mismatch','Edit title identity mismatch','Full corrected-draft QA rejected','Full existing-draft QA rejected']:
  if known in raw:categories.append(known)
 frames=[{'file':a,'line':int(b),'function':c}for a,b,c in re.findall(r'File "[^"\n]*/automation/([A-Za-z0-9_]+\.py)", line (\d+), in ([A-Za-z0-9_<>]+)',raw)]
 timeouts=re.findall(r'([A-Za-z.]+(?:Error|Timeout)): [^\n]{0,140}?Timeout (\d+)ms exceeded',raw)
 waiting=re.findall(r'waiting for (?:locator|selector)\([^\n]{0,140}',raw)
 # Locator names only; do not export caller input values, DOM, tokens or logs.
 waiting=[x for x in waiting if not any(y in x.lower()for y in ('password','passwd','username','usern','loginpass'))]
 rows.append({'job':j['name'],'job_id':j['id'],'categories':categories,'frames':frames[-8:],'timeouts':timeouts,'waiting':waiting[-3:]})
path=Path('artifacts/known-blog-recovery-diagnosis.json');path.parent.mkdir(exist_ok=True);path.write_text(json.dumps({'run':39489558974,'diagnostics':rows},indent=2))
print(json.dumps(rows,indent=2))
