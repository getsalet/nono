"""Bounded parallel source I/O; cache is fetched evidence, never model output."""
import hashlib
from concurrent.futures import ThreadPoolExecutor
from .queue import load_json,atomic_json,age_hours

TTL_HOURS=6
MAX_WORKERS=3

def valid_document(doc,url,source_host):
 try:
  source_host(url)
  return (doc['url']==url and isinstance(doc['text'],str) and 500<=len(doc['text'])<=24000
   and doc['sha256']==hashlib.sha256(doc['text'].encode()).hexdigest()
   and 0<=age_hours(doc['fetched_at'])<TTL_HOURS)
 except (KeyError,TypeError,ValueError):return False

def load_documents(urls,fetcher,out,source_host):
 # No model calls in workers. Unique URLs and input order keep evidence IDs stable.
 urls=list(dict.fromkeys(u for u in urls if isinstance(u,str)))[:6]
 def one(url):
  path=out/'source-cache'/(hashlib.sha256(url.encode()).hexdigest()+'.json')
  try:
   source_host(url)
   try:cached=load_json(path)
   except (OSError,ValueError):cached=None
   if isinstance(cached,dict) and valid_document(cached,url,source_host):return cached
   doc=fetcher(url) # original fetcher still enforces public DNS, no redirects and size limit
   if valid_document(doc,url,source_host):atomic_json(path,doc)
   return doc
  except Exception:return None # no negative caching or extra retries
 with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
  return [d for d in pool.map(one,urls) if d is not None]
