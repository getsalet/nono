"""Recover a format-only blocked brief from original verified evidence, no model calls."""
import hashlib
from .queue import DATA,OUT,load_json,atomic_json,get_topic,utcnow,age_hours
from .research import build_brief,source_host

def publication_slug(topic,raw):
 import re
 if isinstance(raw,str) and len(raw)<=100 and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',raw):return raw
 # Stable per-topic URL, not an invented translation or a model repair request.
 if not re.fullmatch(r'agri-[a-f0-9]{12}',topic['id']):raise ValueError('Invalid topic ID')
 return topic['id']

def repair_brief(ident,inventory,data=DATA,out=OUT):
 sp=out/'research'/f'{ident}.json';old=load_json(sp)
 if old.get('reason')!='invalid_research_slug' or old.get('status')!='needs_review':raise ValueError('Not a format-only blocked brief')
 if not 0<=age_hours(inventory['source_generated_at'])<5/60:raise ValueError('Fresh inventory required')
 topic=get_topic('new',ident,data);base=out/'research-evidence'/ident
 docs=load_json(base/'sources.json')['documents']
 for d in docs:
  source_host(d['url'])
  if not 0<=age_hours(d['fetched_at'])<24 or hashlib.sha256(d['text'].encode()).hexdigest()!=d['sha256']:raise ValueError('Original source evidence expired or changed')
 from .research import resolve_evidence,evidence_catalog
 raw=load_json(base/'candidate-raw.json');candidate=resolve_evidence(raw,evidence_catalog(docs))
 candidate['slug']=publication_slug(topic,raw.get('slug'))
 review=load_json(base/'review.json')['review']
 brief=build_brief(topic,docs,candidate,review,inventory)
 bp=data/'briefs'/f'{ident}.json'
 if bp.exists():raise ValueError('Do not overwrite existing brief')
 receipt={'topic_id':ident,'status':'format_revalidated','at':utcnow(),'previous_state':old,'old_slug':raw.get('slug'),'new_slug':candidate['slug'],'model_calls':0,'original_evidence_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (base/'sources.json',base/'candidate-raw.json',base/'review.json')}}
 atomic_json(out/'format-repairs'/ident/'receipt.json',receipt)
 atomic_json(bp,brief)
 atomic_json(sp,dict(old,status='brief_ready',reason='slug_format_revalidated',format_repaired_at=receipt['at']))
 return {'status':'brief_ready','topic_id':ident}
