"""Read-only queue eligibility, independent of image-provider availability."""
from .queue import DATA,OUT,load_json

def pending_briefs(data=DATA,out=OUT):
 config=load_json(data/'config.json');held=config.get('publication_holds',{});pending=[]
 for p in sorted((data/'briefs').glob('*.json')):
  brief=load_json(p);ident=brief['topic_id']
  if brief.get('publish_authorized') is not True or ident in held:continue
  folder=out/'new'/ident;receipt=folder/'wordpress-receipt.json';attempts=folder/'cycle-attempts.json'
  if receipt.exists() and load_json(receipt).get('public_verified') is True:continue
  if attempts.exists() and load_json(attempts).get('attempts',0)>=2:continue
  pending.append(ident)
 return pending

def buffer_limit(config):
 # A small bounded buffer, never bulk generation while image service is down.
 n=config.get('research_feeder',{}).get('max_buffered_briefs',2)
 return min(2,max(1,n)) if type(n)is int else 2
