#!/usr/bin/env python3
"""Two exact-payload requests with redacted error detail; never publication."""
import base64,copy,json,os,re,subprocess,time,urllib.request,urllib.error
from pathlib import Path
import blog_reference_scene as scene
import blog_generated_image as g
from blog_image_connection import settings
from diagnose_hose_provider import decode
ROOT=Path(__file__).resolve().parents[1]
OUT='artifacts/blog-hose-error-detail'
def redact_error(raw):
 try:d=json.loads(raw)
 except (ValueError,TypeError):return {'format':'non_json','detail':'response withheld'}
 # Only error fields, never successful outputs or arbitrary request echoes.
 e=d.get('error',d.get('detail',d.get('message','')))
 text=e if isinstance(e,str)else json.dumps(e,ensure_ascii=False)
 for name,value in os.environ.items():
  if any(x in name for x in ('KEY','TOKEN','PASSWORD','SECRET'))and len(value)>5:text=text.replace(value,'[redacted]')
 text=re.sub(r'data:image/[^,\s]+,[A-Za-z0-9+/=\s]+','[image withheld]',text)
 text=re.sub(r'(?i)bearer\s+\S+','Bearer [redacted]',text)
 text=re.sub(r'https?://[^\s"<>]+','[URL withheld]',text)
 text=re.sub(r'[A-Za-z0-9_+/=-]{28,}','[identifier withheld]',text)
 text=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','[email withheld]',text)
 return {'format':'json','redacted_error_detail':text[:700]}
def main():
 from blog_generated_image import family_cancelled
 if family_cancelled({'family':'hose'},ROOT):
  print('Hose image generation cancelled by user; zero provider requests.');return 0
 cfg=settings(g.roya.BASE.AGNES_BASE);key=os.getenv('IMAGE_API_KEY','').strip();run=os.getenv('GITHUB_RUN_ID','local')
 if not key or not re.fullmatch(r'[A-Za-z0-9_-]+',run):raise RuntimeError('Diagnostic configuration missing')
 queue=json.loads((ROOT/'data/loxblog/backlink-queue.json').read_text());item=next(copy.deepcopy(x)for x in queue['items']if x.get('family')=='hose'and x.get('published')and x.get('kind')in('city','article'))
 p=ROOT/'artifacts/loxblog-backlink-queue/items'/(re.sub(r'[^A-Za-z0-9._-]+','_',item['key'])+'.json');item['_image_article_context']=scene.context_from_post(json.loads(p.read_text())['post'])
 # Recover the EXACT earlier successful prompt from its pinned source, without
 # executing fetched code: parse and compile only the two pure prompt functions
 # is unnecessary here; the literal matched prompt is stored as a local fixture.
 old_prompt=(ROOT/'automation/hose-matched-success-prompt.txt').read_text().strip()
 report={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'post_submissions':0,'production_approval':False,'max_requests':2,'cases':[]}
 for i,(name,prompt)in enumerate([('current-native-production-headers',scene.prompt(item,'loxblog')),('matched-success-native-production-headers',old_prompt)]):
  if i:time.sleep(40)
  payload={'model':cfg['model'],'prompt':prompt,'size':'1K','ratio':'16:9','extra_body':{'response_format':'b64_json','image':scene.references(item)}}
  row={'name':name,'image_received':False};report['cases'].append(row);start=time.monotonic()
  try:
   req=urllib.request.Request(cfg['endpoint'],data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','Accept':'application/json','User-Agent':'AFP-blog-image-queue/2.0'})
   with urllib.request.urlopen(req,timeout=360)as response:d=json.load(response)
   row['http_status']=200;raw,size=decode(d);path=OUT+'/'+run+'-'+name+'.webp';row.update(image_received=True,provider_size=size,candidate_url=g.checkpoint_asset(path,raw,ROOT))
  except urllib.error.HTTPError as exc:row.update(http_status=exc.code,error=redact_error(exc.read(8192)));exc.close()
  except Exception as exc:row['error_type']=type(exc).__name__
  row['elapsed_seconds']=round(time.monotonic()-start,2)
  g.checkpoint_asset(OUT+'/'+run+'.json',json.dumps(report,ensure_ascii=False,indent=2).encode(),ROOT)
  print(json.dumps(row,ensure_ascii=False),flush=True)
  if row.get('http_status')in(401,402,403,429):break
 return 0
if __name__=='__main__':raise SystemExit(main())
