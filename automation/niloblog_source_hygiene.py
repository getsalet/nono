"""Quarantine observed source defects, never silently repair or invent facts.

Raw fetched documents stay unchanged. Model views and source excerpts exclude
whole defective sentences; all admitted quotes still verify against raw text.
This is a narrow deterministic regression barrier, not semantic fact checking.
"""
import copy,re
RULES=(
 ('double_prevention_negation',r'از جلوگیری از افت کارایی[^.؟!\n]{0,80}جلوگیری می کند'),
 ('cleanliness_causes_wear',r'(?:تمیزی|پاکسازی|پاک سازی|تمیز نگه)[^.؟!\n]{0,180}به سایش[^.؟!\n]{0,80}کمک می کند'),
 ('ambiguous_clogging_assurance',r'از مسدود شدن قطره چکان ها و حفظ جریان آب اطمینان حاصل'),
 ('malformed_animal_hazard',r'حیوانات خردکننده'),
 ('malformed_cost_term',r'سرهنگ کردن'),
)
def normalize(text):return re.sub(r'\s+',' ',str(text).replace('ي','ی').replace('ك','ک').replace('\u200c',' ')).strip()
def sentence_quality(text):
 value=normalize(text)
 return [name for name,pattern in RULES if re.search(pattern,value)]
def partition_source(text):
 # Never stitch across a removed sentence inside an evidentiary quotation.
 value=normalize(text);safe=[];excluded=[]
 for segment in re.split(r'(?<=[.!؟])\s+|\n+',value):
  reasons=sentence_quality(segment)
  if reasons:excluded.append({'text':segment,'reasons':reasons})
  elif segment.strip():safe.append(segment)
 return safe,excluded

def clean_catalog(bundle):
 catalog=[]
 for index,source in enumerate([bundle.get('local'),bundle['article']]+bundle.get('technical',[])):
  if source is None:continue
  safe,_=partition_source(source['text'])
  for position,segment in enumerate(safe):
   words=segment.split(' ')
   for start in range(0,len(words),45):
    quote=' '.join(words[start:start+60])
    if len(quote)>=20:catalog.append({'excerpt_id':f's{index}-q{position}-{start//45}','source_index':index,'scope':'technical_general','quote':quote})
 required=copy.deepcopy(bundle.get('required_evidence',[]))
 if any(sentence_quality(e['quote'])for e in required):raise ValueError('Source contract quote quarantined')
 catalog.extend(required)
 return catalog

def model_source_view(bundle):
 result=copy.deepcopy(bundle)
 for source in [result.get('local'),result['article']]+result.get('technical',[]):
  if source is None:continue
  safe,excluded=partition_source(source['text'])
  source['text']='\n'.join(safe)
  source['source_quality']={'excluded_sentence_count':len(excluded),'excluded_sentences_must_not_be_reconstructed':True}
 return result

def source_quality_audit(bundle):
 sources=[]
 for i,source in enumerate([bundle.get('local'),bundle['article']]+bundle.get('technical',[])):
  if source is None:continue
  safe,excluded=partition_source(source['text'])
  sources.append({'source_index':i,'url':source['url'],'sha256':source.get('sha256'),'checked_at':source.get('checked_at'),'admitted_sentence_count':len(safe),'excluded_sentences':excluded})
 return {'policy_version':1,'raw_sources_modified':False,'rewritten_factual_claims':False,'publication_authorized':False,'sources':sources}

def draft_quality_feedback(markup):
 from bs4 import BeautifulSoup
 _,excluded=partition_source(BeautifulSoup(markup,'html.parser').get_text(' ',strip=True))
 return {'unsafe_sentences':excluded,'action':'Remove the ambiguous/defective sentence. Do not guess or invert its intended meaning. Any replacement claim must have separate clean evidence; rerun full validation and independent review.'}
