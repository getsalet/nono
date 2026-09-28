#!/usr/bin/env python3
"""Fast image QA with hard rejection for product identity and physics failures."""
import base64,json,os,re,urllib.error,urllib.request,shutil,time
from concurrent.futures import as_completed
from pathlib import Path
import image_prompt_policy
REVIEW_POLICY='article-parity-v13-no-human-no-container-scale-topic-role-reviewed'
MAX_IMAGE_ATTEMPTS=max(1,int(os.getenv('IMAGE_QA_ATTEMPTS','6')))
MIN_IMAGE_SCORE=int(os.getenv('IMAGE_QA_MIN_SCORE','70'))
FAST_MODE=os.getenv('IMAGE_QA_FAST_MODE','1')!='0'
REVIEW_KINDS={int(x) for x in os.getenv('IMAGE_QA_REVIEW_KINDS','1,2,3,4,5').split(',') if x.strip().isdigit()}
REVIEW_REQUEST_ATTEMPTS=max(1,int(os.getenv('IMAGE_QA_REVIEW_ATTEMPTS','4')))

def _extract_json(text):
 text=(text or '').strip();text=re.sub(r'^```(?:json)?\s*|\s*```$','',text,flags=re.I|re.S).strip()
 try:return json.loads(text)
 except Exception:
  a=text.find('{');b=text.rfind('}')
  if a>=0 and b>a:return json.loads(text[a:b+1])
 return {'pass':False,'score':0,'reasons':['visual reviewer returned invalid JSON'],'correction_prompt':'Regenerate and submit a clean image for strict review.'}

def _quick_file_check(path):
 if (not path.exists()) or path.stat().st_size<10000:
  return {'pass':False,'score':0,'reasons':['image file missing or too small'],'correction_prompt':'Regenerate a valid photorealistic farm irrigation image.'}
 return None


def _metric_check(family,verdict):
 try:
  width=float(verdict.get('product_width_percent'))
  height=float(verdict.get('product_height_percent'))
  x_center=float(verdict.get('product_x_center_percent'))
 except (TypeError,ValueError):
  return False,['Return numeric product_width_percent, product_height_percent and product_x_center_percent.']
 # Keep impossible/giant products out, but do not starve the queue because a
 # noisy vision estimate misses an editorial target by a few points.
 min_width,max_width=(9,20) if family=='layflat' else (13,27)
 issues=[]
 if width<min_width:
  issues.append(f'Enlarge the product group from {width:g}% to {min_width}-{max_width}% of frame width.')
 elif width>max_width:
  issues.append(f'Reduce the product group from {width:g}% to {min_width}-{max_width}% of frame width.')
 if height>32:
  issues.append(f'Reduce product height from {height:g}% to at most 32% of frame height.')
 return not issues,issues

def _vision_review(base,path,item,kind):
 quick=_quick_file_check(path)
 if quick:return quick
 family=__import__('image_prompt_policy').product_family(item)
 brief=image_prompt_policy.visual_brief(item)
 if FAST_MODE and kind not in REVIEW_KINDS:
  return {'pass':True,'score':90,'reasons':['fast mode: trusted prompt for non-key image'],'correction_prompt':''}
 encoded=base64.b64encode(path.read_bytes()).decode('ascii')
 if family=='layflat':
  criteria='The image must show the approved layflat pair: one packaged AFP coil and one bare black woven coil. The complete pair should occupy about 12 to 15 percent of frame width; accept reviewer-estimation noise only from 9 to 20 percent when both objects remain recognizable, fully visible, separate and physically plausible. Lower-third and off-center placement are editorial preferences, not standalone hard rejects. The image must contain zero people and zero human body parts.'
  reject='Hard reject any person, farmer, worker, face, hand, arm, leg, body part or human silhouette, even distant. Hard reject a pair wider than 20 percent of the frame, a third commercial package or third coil, bottle, jar, canister, bucket, invented package, fake label, impossible intersection, object passing through a coil, floating or merged product, or severely distorted dimensions. A distant unattended tractor, ordinary farm building, installed hose segment, connector, fixed pump, gauge or manifold is allowed when relevant to the requested role and must not be treated as a third commercial product.'
 else:
  criteria='The image must show exactly one AFP white-and-blue wide low cylindrical drip-tape carton roll. The preferred width is 20 to 23 percent of frame width; accept reviewer-estimation noise only from 13 to 27 percent and height up to 32 percent when the object remains physically plausible. Lower-third and off-center placement are editorial preferences, not standalone hard rejects. The image must contain zero people and zero human body parts. The background should match the article brief and selected image role.'
  reject='Hard reject any person, farmer, worker, face, hand, arm, leg, body part or human silhouette, even distant. Hard reject a roll wider than 27 percent of the frame, taller than 32 percent, bottle, jar, canister, bucket, fertilizer or pesticide container, second commercial package, second roll, layflat hose, pipe through the roll, fake headline, caption, gibberish writing, impossible geometry or severely distorted dimensions. A distant unattended tractor, ordinary farm building and fixed irrigation hardware are allowed when contextually relevant.'
 prompt=f'''Fast practical QA for city {item.get('city','')}, family {family}, image role {kind}. {criteria}
{reject}
Article visual brief: {brief}. Mandatory role: {image_prompt_policy.role_directive(family,kind)}.
The exact bottom-right watermark "AFP | 09134922013" is REQUIRED and must never be rejected or requested for removal. Fixed pumps, filters, gauges, manifolds, relevant connectors and distant unattended farm equipment are infrastructure, not extra commercial products. Never pass any visible human or bottle/container. Estimate the product bounding box from image pixels. Report product_width_percent, product_height_percent and product_x_center_percent as numeric percentages of the full image. If pass is true, correction_prompt must be empty. Do not reject only for centered placement, ordinary soil texture, a horizon, farm building, distant crop rows or unattended equipment. Return only JSON: {{"pass":true|false,"score":0-100,"product_width_percent":0,"product_height_percent":0,"product_x_center_percent":0,"reasons":["..."],"correction_prompt":"short regeneration instruction"}}. Pass at score {MIN_IMAGE_SCORE} or higher.'''
 payload={'model':base.AGNES_MODEL,'messages':[{'role':'user','content':[{'type':'text','text':prompt},{'type':'image_url','image_url':{'url':'data:image/webp;base64,'+encoded}}]}],'temperature':0,'response_format':{'type':'json_object'}}
 req=urllib.request.Request(base.AGNES_BASE+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':f"Bearer {base.next_agnes_key() if hasattr(base,'next_agnes_key') else base.AGNES_KEY}",'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=60) as response:raw=json.loads(response.read())
 content=raw['choices'][0]['message']['content']
 if isinstance(content,list):content=''.join(str(x.get('text','')) for x in content if isinstance(x,dict))
 verdict=_extract_json(content)
 metric_ok,metric_issues=_metric_check(family,verdict)
 verdict['pass']=bool(verdict.get('pass')) and int(verdict.get('score',0))>=MIN_IMAGE_SCORE and metric_ok
 if not metric_ok:
  verdict.setdefault('reasons',[]).append('machine-enforced bounding-box check failed: '+'; '.join(metric_issues))
  model_correction=str(verdict.get('correction_prompt') or '').strip()
  verdict['correction_prompt']=' '.join(x for x in [model_correction,' '.join(metric_issues)] if x)
 return verdict


def _vision_review_with_retry(base,path,item,kind):
 last_error=None
 for review_attempt in range(1,REVIEW_REQUEST_ATTEMPTS+1):
  try:
   return _vision_review(base,path,item,kind)
  except (TimeoutError,urllib.error.HTTPError,urllib.error.URLError,ConnectionError,OSError) as exc:
   last_error=exc
   print(
    f"image_visual_review_retry source_id={item.get('source_id')} kind={kind} "
    f"attempt={review_attempt}/{REVIEW_REQUEST_ATTEMPTS} error={type(exc).__name__}",
    flush=True,
   )
   if review_attempt<REVIEW_REQUEST_ATTEMPTS:
    time.sleep(min(12,2**review_attempt))
 raise RuntimeError(
  f"visual reviewer unavailable after {REVIEW_REQUEST_ATTEMPTS} retries: "
  f"{type(last_error).__name__ if last_error else 'unknown error'}"
 )

def install(base,backend,raw_generator):
 def guarded(item,kind):
  feedback='';history=[];family=image_prompt_policy.product_family(item)
  reviews=Path(item.get('_image_review_dir') or (base.OUT/'image-reviews'));reviews.mkdir(parents=True,exist_ok=True)
  image_dir=Path(item.get('_image_output_dir') or base.IMAGES);image_dir.mkdir(parents=True,exist_ok=True)
  review_path=reviews/f"{item['source_id']}-{kind}.json"
  try:
   if review_path.exists():
    prior=json.loads(review_path.read_text(encoding='utf-8'))
    path=image_dir/backend.seo_image_name(item,kind)
    prior_history=prior.get('history') or []
    if prior.get('policy')==REVIEW_POLICY and prior_history and prior_history[-1].get('pass') and path.exists() and path.stat().st_size>10000:
     blob=path.read_bytes();return path.name,__import__('hashlib').sha256(blob).hexdigest()
    # If only the reviewer was unavailable, review the preserved candidate
    # again instead of spending another image-generation attempt.
    if (prior.get('policy')==REVIEW_POLICY and prior_history
        and prior_history[-1].get('review_unavailable')
        and path.exists() and path.stat().st_size>10000):
     try:
      verdict=_vision_review_with_retry(base,path,item,kind)
     except RuntimeError:
      raise RuntimeError('visual reviewer unavailable after retries; candidate checkpoint preserved')
     verdict['attempt']='checkpoint-review'
     history=list(prior_history[-19:])+[verdict]
     review_path.write_text(json.dumps({'source_id':item['source_id'],'family':family,'kind':kind,'policy':REVIEW_POLICY,'fast_mode':FAST_MODE,'history':history[-20:]},ensure_ascii=False,indent=2),encoding='utf-8')
     print(f"image_quality_review_checkpoint source_id={item['source_id']} topic={item.get('topic')} kind={kind} pass={verdict['pass']} score={verdict.get('score',0)} reasons={verdict.get('reasons',[])}",flush=True)
     if verdict['pass']:
      blob=path.read_bytes();return path.name,__import__('hashlib').sha256(blob).hexdigest()
     path.unlink(missing_ok=True)
     feedback=str(verdict.get('correction_prompt') or '; '.join(verdict.get('reasons',[])))
    # A checkpointed failed role must resume with its last directional QA
    # feedback instead of repeating the same six blind attempts every hour.
    if prior.get('policy')==REVIEW_POLICY and prior_history:
     history=list(prior_history[-20:])
     last=prior_history[-1]
     feedback=str(last.get('correction_prompt') or '; '.join(last.get('reasons') or [])).strip()
  except Exception:
   pass
  for attempt in range(1,MAX_IMAGE_ATTEMPTS+1):
    candidate_item=dict(item)
    if feedback:candidate_item['_image_qa_feedback']=feedback
    name,digest=raw_generator(candidate_item,kind);path=image_dir/name
    try:
     verdict=_vision_review_with_retry(base,path,item,kind)
    except RuntimeError as exc:
     verdict={'pass':False,'score':0,'review_unavailable':True,'reasons':[str(exc)],'correction_prompt':'Retry visual review of the preserved candidate without regenerating it.'}
    verdict['attempt']=attempt;history.append(verdict)
    print(f"image_quality_review_fast source_id={item['source_id']} topic={item.get('topic')} kind={kind} attempt={attempt} pass={verdict['pass']} score={verdict.get('score',0)} reasons={verdict.get('reasons',[])}",flush=True)
    review_path.write_text(json.dumps({'source_id':item['source_id'],'family':family,'kind':kind,'policy':REVIEW_POLICY,'fast_mode':FAST_MODE,'history':history[-20:]},ensure_ascii=False,indent=2),encoding='utf-8')
    if verdict['pass']:return name,digest
    if verdict.get('review_unavailable'):
     raise RuntimeError('visual reviewer unavailable after retries; candidate checkpoint preserved')
    path.unlink(missing_ok=True);feedback=str(verdict.get('correction_prompt') or '; '.join(verdict.get('reasons',[])))
  raise RuntimeError(f'image hard gate rejected role {kind} after {MAX_IMAGE_ATTEMPTS} attempt')
 return guarded


def review_image(base,path,item,kind):
 return _vision_review(base,path,item,kind)


def _review_image_panel(base,paths,item,role_numbers):
 encoded=[base64.b64encode(Path(path).read_bytes()).decode('ascii') for path in paths]
 brief=image_prompt_policy.visual_brief(item)
 family=image_prompt_policy.product_family(item)
 roles='; '.join(f'{kind}: {image_prompt_policy.role_directive(family,kind)}' for kind in role_numbers)
 prompt=f'''Review this overlapping panel from a five-image city-article editorial set.
Panel role numbers: {role_numbers}. Article visual brief: {brief}. Required roles: {roles}.
The same AFP product is expected in every image, so product identity itself is not duplication. Pass only when the shown roles are visibly distinct in camera height/angle, environment structure and technical narrative, and every background is relevant to the article brief. Reject repeated layouts, generic farms, role-3/role-5 hardware duplication, any person, any bottle/container, oversized product, or images that only move the product. The exact bottom-right watermark "AFP | 09134922013" is required and must never be treated as duplication, obstruction, added caption or a rejection reason. Return duplicate_roles using the original role numbers from {role_numbers}. Return only JSON: {{"pass":true|false,"score":0-100,"duplicate_roles":{role_numbers},"reasons":["..."],"correction_prompt":"one concise replacement instruction"}}.'''
 content=[{'type':'text','text':prompt}]
 content.extend({'type':'image_url','image_url':{'url':'data:image/webp;base64,'+blob}} for blob in encoded)
 payload={'model':base.AGNES_MODEL,'messages':[{'role':'user','content':content}],'temperature':0,'response_format':{'type':'json_object'}}
 req=urllib.request.Request(base.AGNES_BASE+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':f"Bearer {base.next_agnes_key() if hasattr(base,'next_agnes_key') else base.AGNES_KEY}",'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=120) as response:raw=json.loads(response.read())
 body=raw['choices'][0]['message']['content']
 if isinstance(body,list):body=''.join(str(x.get('text','')) for x in body if isinstance(x,dict))
 verdict=_extract_json(body);roles_out=[]
 for value in verdict.get('duplicate_roles',[]):
  try:value=int(value)
  except (TypeError,ValueError):continue
  if value in role_numbers and value not in roles_out:roles_out.append(value)
 verdict['duplicate_roles']=roles_out
 verdict['pass']=bool(verdict.get('pass')) and int(verdict.get('score',0))>=75 and not roles_out
 return verdict


def review_image_set(base,paths,item):
 # Agnes vision is reliable with up to four attachments. Review two overlapping
 # panels instead of sending all five and then accepting an unverified fallback.
 panels=([(paths,[1,2,3])] if len(paths)==3 else [(paths[:4],[1,2,3,4]),(paths[1:],[2,3,4,5])])
 verdicts=[_review_image_panel(base,panel,item,roles) for panel,roles in panels]
 duplicate_roles=[];reasons=[];corrections=[]
 for verdict in verdicts:
  for role in verdict.get('duplicate_roles',[]):
   if role not in duplicate_roles:duplicate_roles.append(role)
  for reason in verdict.get('reasons',[]):
   reason=str(reason)
   if reason not in reasons:reasons.append(reason)
  correction=str(verdict.get('correction_prompt') or '').strip()
  if correction and correction not in corrections:corrections.append(correction)
 return {
  'pass':all(v.get('pass') for v in verdicts) and not duplicate_roles,
  'score':min(int(v.get('score',0)) for v in verdicts),
  'duplicate_roles':duplicate_roles,
  'reasons':reasons,
  'correction_prompt':' '.join(corrections),
  'panel_scores':[int(v.get('score',0)) for v in verdicts],
 }


def install_set_manager(base,backend,image_count=5):
 def manager(item,pool):
  review_id=str(item.get('source_id') or 'unknown')
  base.OUT.mkdir(parents=True,exist_ok=True)
  # Preserve individually approved roles between scheduled runs. Publication
  # stays atomic: checkpointed files move to base.IMAGES only after set approval.
  staging_root=base.OUT/'.image-role-checkpoints'/review_id
  staging_images=staging_root/'images';staging_reviews=staging_root/'image-reviews'
  staging_images.mkdir(parents=True,exist_ok=True);staging_reviews.mkdir(parents=True,exist_ok=True)
  results,feedback={},{};pending=set(range(1,image_count+1));history=[]
  completed=False
  set_review=base.OUT/'image-reviews'/f'{review_id}-set.json'
  try:
   rounds=max(1,int(os.getenv('IMAGE_SET_QA_ATTEMPTS','3')))
   for set_attempt in range(1,rounds+1):
    futures={}
    for kind in sorted(pending):
     candidate=dict(item);candidate['_image_output_dir']=str(staging_images);candidate['_image_review_dir']=str(staging_reviews)
     if feedback.get(kind):candidate['_image_qa_feedback']=feedback[kind]
     futures[pool.submit(backend.generate_image,candidate,kind)]=kind
    for future in as_completed(futures):
     kind=futures[future];results[kind]=future.result()
    paths=[staging_images/results[kind][0] for kind in range(1,image_count+1)]
    verdict=review_image_set(base,paths,item);verdict['set_attempt']=set_attempt;history.append(verdict)
    set_review.parent.mkdir(parents=True,exist_ok=True)
    set_review.write_text(json.dumps({'source_id':review_id,'policy':REVIEW_POLICY,'history':history[-20:]},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"city_image_set_qa source_id={review_id} attempt={set_attempt} pass={verdict.get('pass')} score={verdict.get('score')} duplicate_roles={verdict.get('duplicate_roles',[])} reasons={verdict.get('reasons',[])}",flush=True)
    if verdict.get('pass'):
     base.IMAGES.mkdir(parents=True,exist_ok=True);final_reviews=base.OUT/'image-reviews';final_reviews.mkdir(parents=True,exist_ok=True)
     for kind in range(1,image_count+1):
      staged=staging_images/results[kind][0]
      if not staged.exists():raise RuntimeError(f'Approved staged image is missing for role {kind}')
      os.replace(staged,base.IMAGES/staged.name)
      role_review=staging_reviews/f'{review_id}-{kind}.json'
      if role_review.exists():os.replace(role_review,final_reviews/role_review.name)
     completed=True
     return [results[kind] for kind in range(1,image_count+1)]
    pending=set(verdict.get('duplicate_roles') or range(1,image_count+1))
    correction=str(verdict.get('correction_prompt') or '; '.join(verdict.get('reasons',[])))
    for kind in pending:
     feedback[kind]=correction+f' Create a new role-{kind} scene clearly unlike the other four.'
     if kind in results:
      (staging_images/results[kind][0]).unlink(missing_ok=True);results.pop(kind,None)
     (staging_reviews/f'{review_id}-{kind}.json').unlink(missing_ok=True)
   raise RuntimeError(f'Image-set diversity gate rejected the five-image editorial set after {rounds} rounds')
  finally:
   if completed:
    shutil.rmtree(staging_root,ignore_errors=True)
   else:
    # Keep approved role images/reviews for the next run. Empty checkpoints
    # (for example, an all-role diversity rejection) are safe to remove.
    try:
     if not any(staging_images.iterdir()) and not any(staging_reviews.iterdir()):
      shutil.rmtree(staging_root,ignore_errors=True)
    except OSError:
     pass
 return manager
