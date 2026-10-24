"""Repository-wide admission for production image requests; no credential rotation on image errors."""
import contextlib,hashlib,json,os,subprocess,time
from .queue import ROOT
from automation.blog_image_queue import Queue,Client as LeaseClient
class AdmissionBlocked(ValueError):pass
def shared_guard(slot):
 # Read latest public routing/cooldown evidence; never read secret values from Git.
 subprocess.run(['git','fetch','--quiet','origin','main:refs/remotes/origin/main'],cwd=ROOT,check=True,capture_output=True)
 for path in ['data/blog-image-provider-backpressure.json','data/blog-image-key-pool-state.json']:
  p=subprocess.run(['git','show','origin/main:'+path],cwd=ROOT,check=True,capture_output=True)
  try:d=json.loads(p.stdout)
  except ValueError:raise AdmissionBlocked('Unreadable shared provider evidence') from None
  if d.get('shared_block')=='billing_required':raise AdmissionBlocked('Shared billing hold; no provider request')
  deadline=max(d.get('retry_at_epoch',0),d.get('shared_retry_at_epoch',0),d.get('keys',{}).get(slot,{}).get('retry_at_epoch',0))
  if not isinstance(deadline,(int,float)) or deadline>time.time():raise AdmissionBlocked('Shared cooldown active; no provider request')
  if d.get('keys',{}).get(slot,{}).get('status') in ('authentication_rejected','image_scope_denied'):raise AdmissionBlocked('Credential unavailable for image scope')

class TokenClient(LeaseClient):
 def __init__(self,token):
  if not token:raise AdmissionBlocked('GitHub image lease unavailable; no provider request')
  self.token=token
@contextlib.contextmanager
def admission(slot,payload,env):
 if env.get('GITHUB_ACTIONS')!='true':yield;return
 token=env.get('BLOG_IMAGE_QUEUE_TOKEN') or env.get('GITHUB_TOKEN')
 shared_guard(slot)
 ident=hashlib.sha256(payload['prompt'].encode()).hexdigest()[:32]
 with Queue(client=TokenClient(token)).slot('agri-v2',ident):
  shared_guard(slot)
  yield
