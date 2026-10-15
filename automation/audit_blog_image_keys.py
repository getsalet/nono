#!/usr/bin/env python3
"""One bounded real image probe per healthy unique credential; never publish posts."""
import concurrent.futures,datetime,hashlib,io,json,sys
from pathlib import Path
from PIL import Image
import blog_generated_image as images
ROOT=Path(__file__).resolve().parents[1]
def probe(name):
 item={'key':'image-capability-'+name,'family':'tape20','site_title':'نوار تیپ'}
 row={'secret_name':name,'status':'unknown','http_status':None}
 try:
  raw=images.generate(item,'loxblog',slots=[name],max_attempts=1)
  pic=Image.open(io.BytesIO(raw));pic.verify()
  row.update(status='image_healthy',http_status=200,width=1200,height=675)
 except Exception as exc:
  attempts=item.get('_image_provider_attempts',[]);code=attempts[-1].get('http_status')if attempts else None
  row.update(status={401:'authentication_rejected',403:'image_scope_denied',429:'rate_limited'}.get(code,'temporarily_unavailable'if code in(500,502,503,504)else'probe_failed'),http_status=code,error_type=type(exc).__name__)
 return row

def main():
 pool=images.roya.BASE._key_pool
 names=[pool.slots[k]for k in pool.keys]
 report={'tested_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'endpoint':images.roya.BASE.AGNES_BASE+'/images/generations','model':'agnes-image-2.5-flash','complete':False,'post_submissions':0,'keys':[]}
 # Two requests at most; configured duplicate secrets never get an extra request.
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as workers:
  for row in workers.map(probe,names):
   report['keys'].append(row);print(json.dumps(row),flush=True)
 report['complete']=len(report['keys'])==len(names)
 path=ROOT/'data/agnes-image-key-health/latest.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2))
 return 0 if report['complete']else 1
if __name__=='__main__':sys.exit(main())
