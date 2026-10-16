"""Shared, bounded image-provider cooldown. Does not disable ready-post publication."""
import json,os,subprocess,time
from pathlib import Path
STATE='data/blog-image-provider-backpressure.json'
class ImageProviderBusy(RuntimeError):
 def __init__(self,retry_at):
  self.retry_at=float(retry_at)
  super().__init__('Image provider queue full; generation deferred until '+time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(self.retry_at)))
def retry_at(root):
 root=Path(root);values=[];path=root/STATE
 if path.exists():
  try:values.append(json.loads(path.read_text()))
  except (OSError,ValueError):raise RuntimeError('Image-provider cooldown unreadable; no API request')from None
 # prepare() already fetched current origin/main for the immutable-asset check.
 if os.getenv('GITHUB_ACTIONS')=='true'and(root/'.git').exists():
  p=subprocess.run(['git','show','origin/main:'+STATE],cwd=root,capture_output=True)
  if p.returncode==0:
   try:values.append(json.loads(p.stdout))
   except ValueError:raise RuntimeError('Remote image-provider cooldown unreadable; no API request')from None
 stamps=[]
 for value in values:
  stamp=value.get('retry_at_epoch')if isinstance(value,dict)else None
  if isinstance(stamp,bool)or not isinstance(stamp,(float,int))or not 0<=stamp<4102444800:raise RuntimeError('Invalid image-provider cooldown; no API request')
  stamps.append(stamp)
 return max(stamps,default=0)
def require_open(root,current=None):
 stamp=retry_at(root)
 if stamp>(time.time()if current is None else current):raise ImageProviderBusy(stamp)
def defer(root,stamp,checkpoint):
 root=Path(root);stamp=max(retry_at(root),float(stamp))
 value={'reason':'image_queue_full','retry_at_epoch':stamp,'retry_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(stamp)),'scope':'new image generation only; ready posts may still publish','post_submissions':0}
 raw=json.dumps(value,indent=2).encode();path=root/STATE;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
 checkpoint(STATE,raw,root)
 return stamp
