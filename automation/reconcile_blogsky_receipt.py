#!/usr/bin/env python3
"""Reconcile ONLY a durable, already publicly verified receipt. Never submit/login."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def reconcile(key,root=ROOT):
 from publish_blogsky_posts import KEY,read,save
 from blogsky_native import verify
 from city_backlink_policy import links_for,qa
 if not KEY.fullmatch(key):raise RuntimeError('Exact key required')
 receipt=read(root/f'artifacts/blogsky-backlink-queue/native-publications/{key}.json',{})
 record=read(root/f'artifacts/blogsky-backlink-queue/items/{key}.json',{})
 url=receipt.get('publicUrl','');cache=read(root/('artifacts/content-originality/blogsky/'+hashlib.sha256(url.encode()).hexdigest()+'.json'),{})
 if receipt.get('phase')!='verified' or receipt.get('native_publication_verified')is not True or record.get('published')is not True or record.get('published_url')!=url or cache.get('url')!=url or cache.get('key')!=key:raise RuntimeError('Complete verified receipt, record and public snapshot required')
 if hashlib.sha256(cache.get('html','').encode()).hexdigest()!=receipt.get('publicArticleSha256'):raise RuntimeError('Public snapshot digest mismatch')
 result={**receipt['verification'],'html':cache['html']};verify(result,record['post'],links_for(record),record.get('image_url'))
 qpath=root/'data/blogsky/backlink-queue.json';q=read(qpath,{'items':[]});rows=[x for x in q['items']if x['key']==key]
 if len(rows)!=1 or rows[0].get('target_url')!=record.get('target_url'):raise RuntimeError('Queue binding mismatch')
 if rows[0].get('published'):
  if rows[0].get('published_url')!=url:raise RuntimeError('Conflicting public checkpoint')
  return False
 errors,_=qa(record,record['post'],links_for(record),'blogsky',root)
 if errors:raise RuntimeError('Verified record failed current content QA')
 q['items']=[{k:v for k,v in record.items()if k not in ('post','blog','qa')}if x['key']==key else x for x in q['items']];save(qpath,q);return True
if __name__=='__main__':
 print('Verified receipt reconciled:',reconcile(sys.argv[1]))
