#!/usr/bin/env python3
"""Three bounded differential probes; no blog submission and no raw API logs."""
import base64,copy,hashlib,io,json,os,re,subprocess,tempfile,time,urllib.request,urllib.error
from pathlib import Path
from PIL import Image
from blog_image_connection import settings
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/blog-image-transport-probe'
TEXT_CONTROL='Photograph exactly one smooth bright red sphere resting on a plain cyan studio tabletop, against a seamless cyan background. Close-up studio product photography. The entire image contains ONLY the red sphere and cyan surface. No people, no farm, no plants, no soil, no vehicles, no packaging, no letters, no logos. This is a studio scene, not agriculture.'
def cases():
 import blog_reference_scene as scene
 queue=json.loads((ROOT/'data/loxblog/backlink-queue.json').read_text())
 item=next(copy.deepcopy(x)for x in queue['items']if x.get('family')=='hose'and x.get('published')and x.get('kind')in('city','article'))
 path=ROOT/'artifacts/loxblog-backlink-queue/items'/(re.sub(r'[^A-Za-z0-9._-]+','_',item['key'])+'.json')
 item['_image_article_context']=scene.context_from_post(json.loads(path.read_text())['post'])
 prompt=scene.prompt(item,'loxblog');refs=scene.references(item)
 return [('text-control',{'prompt':TEXT_CONTROL,'response_format':'b64_json'}),('nested-reference',{'prompt':prompt,'extra_body':{'response_format':'b64_json','image':refs}}),('flat-reference',{'prompt':prompt,'response_format':'b64_json','image':refs})]
def decode(data):
 row=(data.get('data')or[{}])[0]
 if row.get('b64_json'):raw=base64.b64decode(row['b64_json'],validate=True)
 elif isinstance(row.get('url'),str)and row['url'].startswith('https://'):
  with urllib.request.urlopen(row['url'],timeout=120)as r:raw=r.read(12*1024*1024+1)
 else:raise ValueError('No image')
 if len(raw)>12*1024*1024:raise ValueError('Oversized image')
 im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert('RGB');im.thumbnail((1200,1200))
 out=io.BytesIO();im.save(out,'WEBP',quality=90);return out.getvalue(),list(im.size)
def checkpoint():
 files=[str(p.relative_to(ROOT))for p in OUT.glob('*')if p.suffix in('.json','.webp')and p.stat().st_size<8*1024*1024]
 def git(args,env=None,data=None,check=True):
  p=subprocess.run(['git',*args],cwd=ROOT,env=env,input=data,capture_output=True)
  if check and p.returncode:raise RuntimeError('Probe checkpoint failed')
  return p
 with tempfile.TemporaryDirectory()as d:
  env=dict(os.environ,GIT_INDEX_FILE=d+'/index',GIT_AUTHOR_NAME='github-actions[bot]',GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',GIT_COMMITTER_NAME='github-actions[bot]',GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com')
  for _ in range(3):
   git(['fetch','--quiet','origin','main']);parent=git(['rev-parse','origin/main']).stdout.decode().strip();git(['read-tree',parent],env);git(['add','--sparse','-f','--',*files],env);tree=git(['write-tree'],env).stdout.decode().strip();commit=git(['commit-tree',tree,'-p',parent],env,b'Persist bounded image transport probes; no publication\n').stdout.decode().strip()
   if git(['push','--quiet','origin',commit+':refs/heads/main'],check=False).returncode==0:return
  raise RuntimeError('Probe checkpoint failed')
def main():
 OUT.mkdir(parents=True,exist_ok=True);cfg=settings('https://apihub.agnes-ai.com/v1');key=os.getenv('IMAGE_API_KEY','').strip()
 report={'workflow_run_id':os.getenv('GITHUB_RUN_ID'),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'connection':cfg,'post_submissions':0,'manual_visual_acceptance':False,'cases':[]}
 try:
  if not key:raise RuntimeError('Image credential missing')
  for name,body in cases():
   payload=dict(model=cfg['model'],size=cfg['size'],return_base64=True,**body);row={'name':name,'prompt_sha256':hashlib.sha256(body['prompt'].encode()).hexdigest(),'attempts':[]};report['cases'].append(row)
   for attempt in range(2):
    req=urllib.request.Request(cfg['endpoint'],data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','Accept':'application/json'})
    try:
     with urllib.request.urlopen(req,timeout=120)as response:data=json.load(response)
     raw,size=decode(data);path=OUT/(name+'.webp');path.write_bytes(raw);row.update(http_status=200,sha256=hashlib.sha256(raw).hexdigest(),size=size,path=str(path.relative_to(ROOT)));break
    except urllib.error.HTTPError as exc:
     code=exc.code;exc.close();row['attempts'].append({'http_status':code});row['http_status']=code
     if code in(429,500,502,503,504)and attempt==0:time.sleep(15);continue
     break
    except Exception as exc:row['error_type']=type(exc).__name__;break
   print(json.dumps({'name':name,'http_status':row.get('http_status'),'image_received':bool(row.get('path'))}),flush=True)
 except Exception as exc:report['preflight_error_type']=type(exc).__name__
 finally:
  (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));checkpoint()
 return 0
if __name__=='__main__':raise SystemExit(main())
