#!/usr/bin/env python3
"""Strictly audit recent live city images before selective atomic replacement."""
from __future__ import annotations
import base64,datetime as dt,json,os,re,urllib.request
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import city_content_queue as base
import image_prompt_policy
OUT=Path(__file__).resolve().parents[1]/'artifacts'/'city-content-queue';MARKER=OUT/'recent-image-audit-v1.json'
SINCE=os.getenv('RECENT_IMAGE_AUDIT_SINCE','2026-09-29T10:54:12+00:00');LIMIT=max(1,int(os.getenv('RECENT_IMAGE_AUDIT_LIMIT','24')));WORKERS=max(1,int(os.getenv('RECENT_IMAGE_AUDIT_WORKERS','4')));POLICY='reference-matched-natural-scene-audit-v1'
def now():return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
def extract_json(text):
 text=re.sub(r'^```(?:json)?\s*|\s*```$','',str(text or '').strip(),flags=re.I|re.S).strip()
 try:return json.loads(text)
 except Exception:
  a=text.find('{');b=text.rfind('}')
  if a>=0 and b>a:return json.loads(text[a:b+1])
  return {'pass':False,'score':0,'reasons':['reviewer returned invalid JSON'],'correction_prompt':'Regenerate the scene.'}
def content_url(path):return 'data:image/webp;base64,'+base64.b64encode(path.read_bytes()).decode('ascii')
def review_request(item,kind,path):
 family=image_prompt_policy.product_family(item);refs=image_prompt_policy.reference_images(kind,item)
 criteria=('The candidate must show exactly one approved AFP white-and-blue drip-tape carton roll matching the reference.' if family=='tape20' else 'The candidate must show the approved pair only: one packaged AFP layflat coil and one separate bare black woven layflat coil, both matching the references.')
 prompt=f"""Strict forensic review of an already-published city article image. Product family: {family}; role: {kind}; city: {item.get('city','')}. {criteria}
Compare the candidate against every attached approved reference. Reject if product identity, count, geometry, packaging, proportions, color or AFP branding is invented or belongs to the other family. Reject any person/body part, bottle/container, third commercial product, impossible intersection, floating object, distorted coil/carton, or product clipped by the frame.
Critically inspect photographic integration: reject pasted/cutout/collage appearance, white or razor edge halo, mismatched sharpness/noise/resolution, inconsistent camera angle or perspective, missing or wrong-direction contact shadow, inconsistent sun or color temperature, no soil contact, or a product superimposed on a separately generated background. The farm background must be relevant and the product must sit naturally in it. The required bottom-right AFP | 09134922013 watermark is allowed.
Return JSON only: {{"pass":true|false,"score":0-100,"reasons":["specific evidence"],"correction_prompt":"one concise integrated-rerender instruction"}}. Pass only at 85+ with no defect."""
 content=[{'type':'text','text':prompt},{'type':'image_url','image_url':{'url':content_url(path)}}]+[{'type':'image_url','image_url':{'url':url}} for url in refs]
 payload={'model':base.AGNES_MODEL,'messages':[{'role':'user','content':content}],'temperature':0,'response_format':{'type':'json_object'}};last=None
 for attempt in range(1,4):
  try:
   req=urllib.request.Request(base.AGNES_BASE+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+base.next_agnes_key(),'Content-Type':'application/json'})
   with urllib.request.urlopen(req,timeout=120) as response:data=json.loads(response.read())
   body=data['choices'][0]['message']['content']
   if isinstance(body,list):body=''.join(str(x.get('text','')) for x in body if isinstance(x,dict))
   verdict=extract_json(body);verdict['score']=int(verdict.get('score',0));verdict['pass']=bool(verdict.get('pass')) and verdict['score']>=85;return verdict
  except Exception as exc:last=exc
 return {'pass':False,'score':0,'review_unavailable':True,'reasons':[f'{type(last).__name__}: reviewer unavailable after retries'],'correction_prompt':'Retry audit without deleting or rebuilding.'}
def audit_one(row):
 item,path,data=row;merged={**item,**data};sid=str(item['source_id']);raw=data.get('images') or item.get('images') or [];names=[Path(x.get('name') if isinstance(x,dict) else str(x)).name for x in raw][:3]
 if len(names)!=3:return sid,{'pass':False,'reasons':['expected exactly three current images'],'roles':[]}
 verdicts=[]
 for kind,name in enumerate(names,1):
  image=base.IMAGES/name
  verdict=({'pass':False,'score':0,'reasons':['current image missing or too small'],'correction_prompt':'Regenerate missing image.'} if not image.exists() or image.stat().st_size<10000 else review_request(merged,kind,image));verdicts.append({'kind':kind,'name':name,**verdict})
  if verdict.get('review_unavailable'):return sid,{'pass':None,'reasons':['review temporarily unavailable'],'roles':verdicts}
 passed=all(v.get('pass') for v in verdicts);reasons=[]
 for v in verdicts:
  if not v.get('pass'):reasons.extend(f"role {v['kind']}: {r}" for r in v.get('reasons',[]))
 return sid,{'pass':passed,'reasons':reasons,'roles':verdicts}
def main():
 state=json.loads(base.QUEUE.read_text(encoding='utf-8'));prior={}
 if MARKER.exists():
  try:prior=json.loads(MARKER.read_text(encoding='utf-8'))
  except Exception:prior={}
 audited=dict(prior.get('audited') or {}) if prior.get('policy')==POLICY and prior.get('since')==SINCE else {};candidates=[]
 for item in state.get('items',[]):
  if item.get('status')!='completed' or str(item.get('completed_at') or '')<SINCE:continue
  sid=str(item.get('source_id') or '');path=base.ITEMS/f'{sid}.json'
  if sid and path.exists():candidates.append((item,path,json.loads(path.read_text(encoding='utf-8'))))
 candidates.sort(key=lambda row:str(row[0].get('completed_at') or ''));pending=[row for row in candidates if str(row[0]['source_id']) not in audited][:LIMIT]
 with ThreadPoolExecutor(max_workers=min(WORKERS,len(pending) or 1)) as pool:
  futures={pool.submit(audit_one,row):row for row in pending}
  for future in as_completed(futures):
   sid,result=future.result()
   if result.get('pass') is not None:audited[sid]=result
 failed=sorted(sid for sid,row in audited.items() if row.get('pass') is False);passed=sum(1 for row in audited.values() if row.get('pass') is True);remaining=max(0,len(candidates)-len(audited))
 marker={'policy':POLICY,'since':SINCE,'updated_at':now(),'completed':remaining==0,'total_candidates':len(candidates),'audited_count':len(audited),'passed_count':passed,'failed_count':len(failed),'remaining_candidates':remaining,'failed_source_ids':failed,'audited':audited};MARKER.write_text(json.dumps(marker,ensure_ascii=False,indent=2),encoding='utf-8')
 print(f"recent_image_audit total={len(candidates)} audited={len(audited)} passed={passed} failed={len(failed)} remaining={remaining}",flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
