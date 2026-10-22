"""System-owned metadata/neutral CTA repairs; never relaxes article QA or adds links."""
import hashlib,html,re
ACTIVE=('farsiblog','rozblog','loxblog','blogsky')
CTA='<p>برای بررسی مشخصات همان مدل، به وب‌سایت اصلی AFP مراجعه کنید.</p>'
def normalize(item,obj,blog):
 if blog not in ACTIVE or not isinstance(obj,dict)or not isinstance(obj.get('html'),str):return []
 changes=[]
 if not re.fullmatch(r'[a-z0-9][a-z0-9-]{2,59}',str(obj.get('slug',''))):
  key=str(item.get('key',''))
  if key:
   product='navar-tip'if item.get('family')=='tape20'else'irrigation-guide'
   obj['slug']=product+'-'+hashlib.sha256((blog+':'+key).encode()).hexdigest()[:20]
   changes.append('invalid_slug_replaced_with_stable_system_slug')
 body=obj['html'];faq=body.find('<details')
 if faq<0:return changes
 before=body[:faq]
 endings=list(re.finditer(r'<h[23]\b[^>]*>\s*(?:جمع[\s‌-]*بندی|نتیجه[\s‌-]*گیری)[^<]*</h[23]\s*>',before,re.I))
 if not endings:return changes
 end=endings[-1].end();segment=before[end:]
 if re.search(r'<h[23]\b',segment,re.I):return changes
 text=re.sub(r'<[^>]*>',' ',html.unescape(segment))
 # Do not manufacture a missing/short conclusion. Its 30-word topic-specific
 # summary, factual checks, originality and every link still require full QA.
 if len(re.findall(r'[\u0600-\u06ff]+',text))<30:return changes
 site=bool(re.search(r'(?:وب[\s‌-]*سایت|سایت\s+اصلی|AFP)',text))
 action=bool(re.search(r'بررسی|مشاهده|مراجعه|مطالعه|مقایسه',text))
 if not(site and action):
  obj['html']=body[:faq]+CTA+'\n'+body[faq:]
  changes.append('neutral_unlinked_main_site_next_step_added')
 return changes
