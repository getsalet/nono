"""Source-bound pending-row overlay. Never edits state, past titles or permissions."""
import copy,re

def apply_source_queue(matrix,state,queue,protected_keys=()):
 if queue.get('schema')!='niloblog-source-bound-queue-v1' or queue.get('publication_permission_granted')is not False or queue.get('retry_permission_granted')is not False:raise ValueError('Invalid source queue policy')
 topics=queue.get('topics')
 if not isinstance(topics,list)or not 1<=len(topics)<=12:raise ValueError('Invalid source queue size')
 result=copy.deepcopy(matrix);result['source_queue_required']=True
 protected=set(protected_keys)|set(state.get('held',{}))|{p['key']for p in state.get('published',[])}
 protected.update(k for k in [state.get('current'),(state.get('intent')or{}).get('key')]if k)
 used={row['angle_ref']for row in matrix['titles']if row['id']in set(protected_keys)|{p['key']for p in state.get('published',[])}}
 seen=set();changed=[];topic_audit=[]
 for priority,topic in enumerate(topics):
  ref=topic.get('angle_ref');refs=topic.get('research_refs',[]);evidence=topic.get('evidence',[])
  if ref not in result['angles']or ref in seen:raise ValueError('Invalid source queue angle')
  seen.add(ref)
  if not isinstance(topic.get('reader_question'),str)or len(topic['reader_question'])<20 or not isinstance(topic.get('seo_short_label'),str):raise ValueError('Invalid source queue question')
  if len(refs)!=2 or len(set(refs))!=2 or not isinstance(evidence,list)or not 2<=len(evidence)<=6:raise ValueError('Invalid source queue evidence')
  if not 3<=len(topic.get('sections',[]))<=5 or not topic.get('forbidden_inferences'):raise ValueError('Invalid source queue scope')
  if any(not isinstance(e,dict)or e.get('source_ref')not in refs or not isinstance(e.get('quote'),str)or len(e['quote'])<30 for e in evidence):raise ValueError('Invalid source queue quotation')
  retired=any(h.get('editorial_source_contract_id')==topic['id']and h.get('failure_policy',{}).get('category')in ('evidence_or_topic','editorial_or_duplicate')for h in state.get('held',{}).values())
  if ref in used or retired:
   topic_audit.append({'id':topic['id'],'pending_rows':0,'reason':'angle_already_used'if ref in used else'contract_requires_editorial_review'});continue
  before=len(changed)
  angle=result['angles'][ref];angle.update(brief=topic['reader_question'],seo_short_label=topic['seo_short_label'])
  for row in result['titles']:
   if row['angle_ref']!=ref or row['id']in protected or row.get('review_state')!='editorial_review_required':continue
   row['legacy_planning_title']=row.get('legacy_planning_title',row['title'])
   row['editorial_source_contract']=copy.deepcopy(topic);row['editorial_priority']=priority
   from niloblog_titles import instructional_title
   row.update(title=instructional_title(row,result),title_policy_version=2);changed.append(row['id'])
  topic_audit.append({'id':topic['id'],'pending_rows':len(changed)-before,'reason':'ready_for_independent_review'if len(changed)>before else'all_rows_protected'})
 from validate_niloblog_matrix import normalize
 if len({normalize(row['title'])for row in result['titles']})!=len(result['titles']):raise ValueError('Source queue would duplicate titles')
 return result,{'version':queue.get('version'),'topics':topic_audit,'eligible_pending_rows':len(changed),'changed_keys':changed,'protected_count':len(protected),'state_changed':False,'publication_permission_granted':False,'retry_permission_granted':False}

def verify_source_contract(contract,technical,canon):
 refs=contract['research_refs'];required=[]
 if [source.get('research_ref')for source in technical]!=refs:raise ValueError('Source queue provenance changed')
 for position,evidence in enumerate(contract['evidence']):
  index=refs.index(evidence['source_ref']);source=technical[index];quote=canon(evidence['quote'])
  if source['url'].rstrip('/')!=evidence['source_url'].rstrip('/')or quote not in canon(source['text']):raise ValueError('Source queue method quote changed')
  required.append({'excerpt_id':f's{index+2}-contract{position}','source_index':index+2,'scope':'technical_general','quote':quote})
 return required
