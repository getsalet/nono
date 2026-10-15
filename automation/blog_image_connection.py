"""Public image-request settings shared with the reference workflows.
Private IMAGE_API_KEY is read only by the caller and never appears here.
"""
import hashlib,json,os
from urllib.parse import urlsplit
TIMEOUT=600

def settings(default_base):
 endpoint=os.getenv('IMAGE_ENDPOINT')or default_base.rstrip('/')+'/images/generations'
 parsed=urlsplit(endpoint)
 if parsed.scheme!='https'or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
  raise RuntimeError('Image endpoint must be a credential-free HTTPS endpoint')
 model=os.getenv('IMAGE_MODEL')or os.getenv('AGNES_IMAGE_MODEL')or'agnes-image-2.5-flash'
 return {'endpoint':endpoint,'model':model,'size':'1024x768','timeout_seconds':TIMEOUT}

def fingerprint(default_base):
 return hashlib.sha256(json.dumps(settings(default_base),sort_keys=True).encode()).hexdigest()[:16]
