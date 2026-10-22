"""Explicit digest-bound repair of ONE observed acknowledged native post.
Never resets pending state or guesses which remote changes can be overwritten.
"""
import copy,hashlib,json,re
from pathlib import Path
from bs4 import BeautifulSoup
from parsiblog_policy import post_digest,qa,review_prompt
from parsiblog_native import persisted_errors,normalized_body,NativeError,title_matches
from farsiblog_backlink_queue import save
POLICY='parsiblog-explicit-same-id-repair-v1'
def snapshot_digest(post):
 from city_backlink_policy import Inspect
 p=Inspect();p.feed(post['html'])
 data={'title':normalized_body(post['title']),'text':normalized_body(' '.join(p.plain)),'links':p.links,'images':[i.get('src')for i in p.images],'h2':p.tags.count('h2'),'h3':p.tags.count('h3')}
 return hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def repair_candidate(item,saved,actual,manifest):
 if manifest.get('policy')!=POLICY or manifest.get('key')!=item.get('key')or manifest.get('authorized')is not True:raise NativeError('Repair manifest missing or not explicitly authorized')
 if str(saved.get('id'))!=str(manifest.get('native_id'))or str(actual.get('id'))!=str(manifest.get('native_id')):raise NativeError('Repair native ID changed; no write allowed')
 if actual.get('published')is not True:raise NativeError('Repair expects the observed already-public post')
 if not title_matches(item['post']['title'],actual['title']):raise NativeError('Repair title changed; no write allowed')
 digest=post_digest(item['post'])
 if digest==manifest.get('target_post_sha256')and not persisted_errors(item,item['post'],actual):return copy.deepcopy(item),False
 if saved.get('status')!='submitting_publish'or saved.get('native_phase')!='acknowledged':raise NativeError('Repair requires the known acknowledged checkpoint')
 if digest not in(manifest.get('source_post_sha256'),manifest.get('target_post_sha256')):raise NativeError('Repair local source changed')
 if snapshot_digest(actual)!=manifest.get('observed_native_sha256'):raise NativeError('Repair remote content changed after inspection; no write allowed')
 if persisted_errors(item,item['post'],actual)!=['Saved article text differs from approved draft']:raise NativeError('Repair would hide an unrelated native change')
 candidate=copy.deepcopy(item)
 if digest==manifest.get('source_post_sha256'):
  old=manifest.get('old_text');new=manifest.get('new_text')
  if not isinstance(old,str)or not old or not isinstance(new,str)or not new or candidate['post']['html'].count(old)!=1:raise NativeError('Repair exact one-occurrence replacement missing')
  candidate['post']['html']=candidate['post']['html'].replace(old,new,1)
 if post_digest(candidate['post'])!=manifest.get('target_post_sha256'):raise NativeError('Repair target digest mismatch')
 return candidate,True
def prepare_repair(item,saved,actual,root,now):
 from roya_backlink_queue import agnes
 from parsiblog_images import validate_record
 root=Path(root);path=root/'data/parsiblog/repairs'/(item['key']+'.json')
 if not path.exists():raise NativeError('Explicit same-ID repair manifest required')
 manifest=json.loads(path.read_text());candidate,write=repair_candidate(item,saved,actual,manifest)
 if not write:return candidate,False
 # Full deterministic text, originality, image and independent editorial QA.
 text=copy.deepcopy(candidate['post']);soup=BeautifulSoup(text['html'],'html.parser')
 for img in list(soup.find_all('img')):img.decompose()
 text['html']=str(soup);errors,report=qa(candidate,text,root,require_image=False);errors+=validate_record(candidate,root)
 if errors:raise NativeError('Repair preflight rejected: '+','.join(errors[:5]))
 review=agnes(review_prompt(candidate,candidate['post'],root),temperature=.05)
 if not isinstance(review,dict)or review.get('passed')is not True or review.get('errors')!=[]:
  # Persist the non-secret reviewer findings before aborting; never publish a rejection.
  save(root/'artifacts/parsiblog-backlink-queue/repairs'/(item['key']+'-rejected.json'),{'at':now(),'native_id':str(saved['id']),'review':review,'candidate_post_sha256':post_digest(candidate['post']),'native_write_attempted':False})
  raise NativeError('Independent repair editorial review did not approve; see persisted rejected review')
 candidate['editorial_review']={'policy':'parsiblog-evidence-review-v2','passed':True,'post_sha256':post_digest(candidate['post']),'at':now(),'reviewer':'agnes independent repair review','errors':[]}
 errors,report=qa(candidate,candidate['post'],root)
 if errors:raise NativeError('Repair final preflight rejected: '+','.join(errors[:5]))
 candidate['qa']=dict(report,passed=True);candidate['repair_manifest']=dict(policy=POLICY,native_id=str(saved['id']),source_post_sha256=manifest['source_post_sha256'],target_post_sha256=manifest['target_post_sha256'],reviewed_at=now())
 save(root/'artifacts/parsiblog-backlink-queue/repairs'/(item['key']+'.json'),{'at':now(),'native_id':str(saved['id']),'manifest':manifest,'original_post':item['post'],'observed_native_sha256':snapshot_digest(actual),'review':review,'new_post_sha256':post_digest(candidate['post']),'new_native_post_allowed':False})
 return candidate,True
