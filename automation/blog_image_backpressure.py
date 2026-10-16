"""Shared, bounded image-provider cooldown. Does not disable ready-post publication."""
import json,os,subprocess,time
from pathlib import Path
STATE='data/blog-image-provider-backpressure.json'
LOCAL_STATE='artifacts/blog-image-runtime/provider-cooldown.json'
class ImageProviderBusy(RuntimeError):
 def __init__(self,retry_at):
  self.set_retry(retry_at)
 def set_retry(self,stamp):
  self.retry_at=float(stamp)
  self.args=('Image provider queue full; generation deferred until '+time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(self.retry_at)),)
def states(root):
 root=Path(root);values=[]
 for name in(STATE,LOCAL_STATE):
  path=root/name
  if path.exists():
   try:values.append(json.loads(path.read_text()))
   except (OSError,ValueError):raise RuntimeError('Image-provider cooldown unreadable; no API request')from None
 # prepare() already fetched current origin/main for the immutable-asset check.
 if os.getenv('GITHUB_ACTIONS')=='true'and(root/'.git').exists():
  p=subprocess.run(['git','show','origin/main:'+STATE],cwd=root,capture_output=True)
  if p.returncode==0:
   try:values.append(json.loads(p.stdout))
   except ValueError:raise RuntimeError('Remote image-provider cooldown unreadable; no API request')from None
 return values
def retry_at(root):
 stamps=[]
 for value in states(root):
  stamp=value.get('retry_at_epoch')if isinstance(value,dict)else None
  if isinstance(stamp,bool)or not isinstance(stamp,(float,int))or not 0<=stamp<4102444800:raise RuntimeError('Invalid image-provider cooldown; no API request')
  stamps.append(stamp)
 return max(stamps,default=0)
def require_open(root,current=None):
 stamp=retry_at(root)
 if stamp>(time.time()if current is None else current):raise ImageProviderBusy(stamp)
def latest_failure(root):
 values=states(root)
 for value in values:
  if not isinstance(value,dict):raise RuntimeError('Invalid provider state')
  count=value.get('consecutive_queue_full',0);stamp=value.get('last_failure_epoch',0)
  if isinstance(count,bool)or not isinstance(count,int)or not 0<=count<=16 or isinstance(stamp,bool)or not isinstance(stamp,(int,float))or not 0<=stamp<4102444800:raise RuntimeError('Invalid provider backoff state')
 return max(values,key=lambda v:v.get('last_failure_epoch',0),default={})
def write_state(root,value,checkpoint):
 root=Path(root);raw=json.dumps(value,indent=2).encode();path=root/LOCAL_STATE;path.parent.mkdir(parents=True,exist_ok=True)
 # Runtime cache only: never dirty tracked shared state in a live checkout.
 tmp=path.with_suffix('.tmp');tmp.write_bytes(raw);tmp.replace(path)
 checkpoint(STATE,raw,root)
def defer(root,stamp,checkpoint):
 root=Path(root);clock=time.time();prior=latest_failure(root)
 consecutive=min(4,prior.get('consecutive_queue_full',0)+1)if clock-prior.get('last_failure_epoch',0)<3600 else 1
 delay=min(1800,300*2**(consecutive-1))
 stamp=max(retry_at(root),float(stamp),clock+delay)
 value={'reason':'image_queue_full','retry_at_epoch':stamp,'retry_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(stamp)),'consecutive_queue_full':consecutive,'last_failure_epoch':clock,'backoff_seconds':delay,'scope':'new image generation only; ready posts may still publish','post_submissions':0}
 write_state(root,value,checkpoint)
 return stamp
def mark_success(root,checkpoint):
 # Called only under the global image mutex after a real generated response.
 prior=latest_failure(root)
 if not prior.get('consecutive_queue_full'):return
 write_state(root,{'reason':'provider_recovered','retry_at_epoch':0,'retry_at':None,'consecutive_queue_full':0,'last_failure_epoch':time.time(),'scope':'new image generation only; ready posts may still publish','post_submissions':0},checkpoint)
