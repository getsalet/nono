#!/usr/bin/env python3
"""Bounded same-key/same-model differential diagnosis; zero publication or acceptance edits."""
import base64,copy,hashlib,io,json,os,re,subprocess,time,urllib.request,urllib.error
from pathlib import Path
from PIL import Image
import blog_reference_scene as scene
import blog_generated_image as generated
from blog_image_connection import settings
ROOT=Path(__file__).resolve().parents[1]
OUT='artifacts/blog-hose-provider-diagnosis'
def error_summary(raw,headers):
 # Derive fixed vocabulary only; never persist response bodies, messages or keys.
 try:d=json.loads(raw);e=d.get('error',d)
 except (ValueError,TypeError):e={}
 text=json.dumps(e,ensure_ascii=False).lower()
 categories={
  'quota_or_credit':r'quota|insufficient.credit|balance|billing',
  'rate_or_concurrency':r'rate.limit|too.many|concurren|rpm|busy|overload',
  'upstream_capacity':r'upstream|no.available|no.healthy|capacity|channel|temporar|unavailable',
  'media_validation':r'unsupported|invalid|decode|base64|image.format|image.size|dimension',
  'safety_filter':r'safety|moderation|content.policy|blocked|prohibited',
  'authentication':r'unauthorized|authentication|permission|api.key',
  'timeout':r'timeout|timed.out',
 }
 result={'body_format':'json'if e else'non_json_or_empty','categories':[name for name,pattern in categories.items()if re.search(pattern,text)]}
 from agnes_key_pool import AgnesProviderError
 err=AgnesProviderError(503,raw)
 result.update(provider_code=err.provider_code,provider_type=err.provider_type)
 if headers:
  result['content_type']=str(headers.get_content_type())
  retry=headers.get('Retry-After')
  if retry and re.fullmatch(r'\d{1,6}',retry):result['retry_after_seconds']=min(int(retry),180)
 return result

def png_refs(refs):
 result=[]
 for ref in refs:
  raw=base64.b64decode(ref.split(',',1)[1]);image=Image.open(io.BytesIO(raw)).convert('RGB')
  out=io.BytesIO();image.save(out,'PNG',optimize=True)
  result.append('data:image/png;base64,'+base64.b64encode(out.getvalue()).decode())
 return result

def decode(data):
 row=(data.get('data')or[{}])[0]
 if row.get('b64_json'):raw=base64.b64decode(row['b64_json'],validate=True)
 elif isinstance(row.get('url'),str)and row['url'].startswith('https://'):
  with urllib.request.urlopen(row['url'],timeout=300)as response:raw=response.read(12*1024*1024+1)
 else:raise ValueError('No image data')
 if len(raw)>12*1024*1024:raise ValueError('Oversized response')
 im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert('RGB')
 if min(im.size)<512 or max(im.size)>10000:raise ValueError('Unexpected dimensions')
 size=list(im.size);im.thumbnail((1600,1600))
 from blog_image_watermark import apply
 im=apply(im);out=io.BytesIO();im.save(out,'WEBP',quality=90,method=6)
 return out.getvalue(),size

def main():
 from blog_generated_image import family_cancelled
 if family_cancelled({'family':'hose'},ROOT):
  print('Hose image generation cancelled by user; zero provider requests.');return 0
 cfg=settings(generated.roya.BASE.AGNES_BASE);key=os.getenv('IMAGE_API_KEY','').strip();run=os.getenv('GITHUB_RUN_ID','local')
 if not re.fullmatch(r'[A-Za-z0-9_-]+',run):raise ValueError('Bad run identifier')
 report={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'workflow_run_id':run,'post_submissions':0,'production_approval':False,'max_requests':4,'same_credential_all_cases':True,'connection':cfg,'cases':[]}
 try:
  if not key:raise RuntimeError('Missing image credential')
  queue=json.loads((ROOT/'data/loxblog/backlink-queue.json').read_text())
  item=next(copy.deepcopy(x)for x in queue['items']if x.get('family')=='hose'and x.get('published')and x.get('kind')in('city','article'))
  post=ROOT/'artifacts/loxblog-backlink-queue/items'/(re.sub(r'[^A-Za-z0-9._-]+','_',item['key'])+'.json')
  item['_image_article_context']=scene.context_from_post(json.loads(post.read_text())['post'])
  prompt=scene.prompt(item,'loxblog');refs=scene.references(item)
  report.update(article_key=item['key'],article_context=item['_image_article_context'],prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest())
  base={'model':cfg['model'],'prompt':prompt,'size':'1024x768'}
  cases=[('same-prompt-text-control',dict(base,return_base64=True)),
         ('official-img2img-fields',dict(base,extra_body={'response_format':'b64_json','image':refs})),
         ('official-tier-and-ratio',dict(base,size='1K',ratio='16:9',extra_body={'response_format':'b64_json','image':refs})),
         ('tier-and-lossless-png-refs',dict(base,size='1K',ratio='16:9',extra_body={'response_format':'b64_json','image':png_refs(refs)}))]
  for i,(name,payload)in enumerate(cases):
   if i:time.sleep(35)
   body=json.dumps(payload,ensure_ascii=False).encode()
   r={'name':name,'size':payload['size'],'ratio':payload.get('ratio'),'reference_count':len(payload.get('extra_body',{}).get('image',[])),'request_bytes':len(body),'image_received':False}
   report['cases'].append(r);start=time.monotonic()
   try:
    req=urllib.request.Request(cfg['endpoint'],data=body,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','Accept':'application/json','User-Agent':'AFP-image-differential-diagnosis/1.0'})
    with urllib.request.urlopen(req,timeout=360)as response:data=json.load(response)
    r['http_status']=200
    raw,size=decode(data);path=OUT+'/'+run+'-'+name+'.webp'
    r.update(image_received=True,provider_size=size,sha256=hashlib.sha256(raw).hexdigest(),candidate_url=generated.checkpoint_asset(path,raw,ROOT),candidate_path=path)
   except urllib.error.HTTPError as exc:
    r.update(http_status=exc.code,error_summary=error_summary(exc.read(16384),exc.headers));exc.close()
   except Exception as exc:r['error_type']=type(exc).__name__
   r['elapsed_seconds']=round(time.monotonic()-start,2)
   print(json.dumps({k:r[k]for k in('name','http_status','image_received','elapsed_seconds','error_summary')if k in r}),flush=True)
   generated.checkpoint_asset(OUT+'/'+run+'.json',json.dumps(report,ensure_ascii=False,indent=2).encode(),ROOT)
   # Do not spend more calls after a reference-conditioned request succeeds.
   if r['image_received']and i>0:break
   if r.get('http_status')in(401,402,403,429):break
 except Exception as exc:report['preflight_error_type']=type(exc).__name__
 finally:generated.checkpoint_asset(OUT+'/'+run+'.json',json.dumps(report,ensure_ascii=False,indent=2).encode(),ROOT)
 return 0
if __name__=='__main__':raise SystemExit(main())
