"""Exact, hash-pinned external research documents, never publication targets."""
import datetime,hashlib,io,re,urllib.request
from urllib.parse import urlsplit
DOCUMENTS={
 'research-access-ttape-handling-i108':{
  'url':'https://www.access-irrigation.co.uk/wp-content/uploads/2018/10/I108-T-Tape-500-2.pdf',
  'sha256':'9e9914b4d18f5d484c63f9030a020b1c262732306be67b0d19facda73c59c3e0',
  'pages':[1], 'source_label':'راهنمای حمل کلاف تی‌تیپ؛ اکسس ایریگیشن، صفحه اول، نسخه ژانویه ۲۰۱۶',
  'scope':'T-Tape reels only; do not generalize proprietary packaging instructions to other products',
 }
}
DOCUMENTS['research-arizona-sdi-maintenance']={
 'url':'https://extension.arizona.edu/publication/seasonal-maintenance-practices-drip-and-sprinkler-irrigation-systems-arizona',
 'format':'html','source_label':'راهنمای نگهداری فصلی سامانه های آبیاری؛ ترویج دانشگاه آریزونا',
 'scope':'Published SDI maintenance guidance; table lists POSSIBLE problems, not conclusive diagnosis or farm-specific prescriptions',
}
DOCUMENTS['research-iran-swri-irrigation-evaluation-128814']={
 'url':'https://wra.areeo.ac.ir/article_128814.html','format':'html',
 'source_label':'پژوهش آب در کشاورزی؛ ارزیابی آبیاری نواری و شیاری؛ شاهین رخسار و اسدی، ۱۳۹۲',
 'scope':'For this question admit only the Persian definition of field irrigation evaluation, not the historical experiment outcomes, savings percentages or extrapolated local conditions',
 'authority_class':'iran_public_research','publisher':'مؤسسه تحقیقات خاک و آب، سازمان تحقیقات آموزش و ترویج کشاورزی',
 'published_date':'2013-05-22','doi':'10.22092/jwra.2013.128814',
 'study_context':{'place':'ایستگاه تحقیقات کشاورزی گرگان','crop':'سویا','study_years_fa':'۱۳۸۵ و ۱۳۸۶','publication_year_fa':'۱۳۹۲','historical_not_current_observation':True},
}
DOCUMENTS['research-arizona-sdi-maintenance'].update(authority_class='international_public_research',publisher='University of Arizona Cooperative Extension',publication_month='2025-08',publication_number='az2155')
MAX_BYTES=2_000_000

def registered(ref):return ref in DOCUMENTS

def verify_pdf(raw,ref,final_url,content_type,extract=None):
 if ref not in DOCUMENTS:raise ValueError('Unapproved research document')
 doc=DOCUMENTS[ref]
 if final_url!=doc['url']or urlsplit(final_url).scheme!='https':raise ValueError('Research document redirected')
 if len(raw)>MAX_BYTES or not raw.startswith(b'%PDF-')or content_type.split(';')[0].strip().lower()!='application/pdf':raise ValueError('Invalid research PDF')
 if hashlib.sha256(raw).hexdigest()!=doc['sha256']:raise ValueError('Research document hash changed')
 if extract is None:
  from pypdf import PdfReader
  reader=PdfReader(io.BytesIO(raw))
  if reader.is_encrypted:raise ValueError('Encrypted research document')
  extract=lambda page:reader.pages[page-1].extract_text()or''
 text=' '.join(extract(p)for p in doc['pages']);text=re.sub(r'\s+',' ',text).strip()
 if len(text)<400 or '\ufffd'in text:raise ValueError('Research document text incomplete')
 return {'url':doc['url'],'text':text,'sha256':doc['sha256'],'text_sha256':hashlib.sha256(text.encode()).hexdigest(),
         'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'research_ref':ref,
         'source_label':doc['source_label'],'document_scope':doc['scope'],'document_pages':doc['pages'],
         'research_only':True,'publication_target':False}

def fetch_document(ref):
 if ref not in DOCUMENTS:raise ValueError('Unapproved research document')
 doc=DOCUMENTS[ref]
 if doc.get('format')=='html':
  # Existing bounded HTTPS host-checked reader; exact contract quotes are
  # independently verified by verify_source_contract on every fresh fetch.
  from niloblog_pipeline import fetch
  source=fetch(doc['url'],urlsplit(doc['url']).hostname)
  return dict(source,research_ref=ref,source_label=doc['source_label'],document_scope=doc['scope'],research_only=True,publication_target=False,research_citation={k:doc[k]for k in ('authority_class','publisher','published_date','publication_month','doi','publication_number','study_context')if k in doc})
 request=urllib.request.Request(DOCUMENTS[ref]['url'],headers={'User-Agent':'AFP-Niloblog-editorial/1.0'})
 with urllib.request.urlopen(request,timeout=45)as response:
  if response.status!=200:raise ValueError('Research document HTTP status changed')
  raw=response.read(MAX_BYTES+1)
  return verify_pdf(raw,ref,response.url,response.headers.get('Content-Type',''))


def required_authority_coverage(bundle):
 # Authority is registered against the exact original URL, never model supplied.
 # A commercial Persian source cannot impersonate an Iranian public institution.
 groups={};sources=[bundle.get('local'),bundle['article']]+bundle.get('technical',[])
 for index,source in enumerate(sources):
  if not source:continue
  ref=source.get('research_ref');doc=DOCUMENTS.get(ref,{})
  role=doc.get('authority_class')
  if role not in ('iran_public_research','international_public_research')or source.get('url')!=doc.get('url'):continue
  admitted=[e for e in bundle.get('required_evidence',[])if e.get('source_index')==index and e.get('quote')]
  if not admitted:continue
  groups.setdefault(role,[]).append({'source_index':index,'research_ref':ref,'url':doc['url'],'publisher':doc['publisher'],'source_label':doc['source_label'],'citation':source.get('research_citation',{}),'fact_ids':[e['excerpt_id']for e in admitted]})
 missing=[k for k in ('iran_public_research','international_public_research')if not groups.get(k)]
 if missing:raise ValueError('Iranian and international research evidence required: '+','.join(missing))
 return {'policy':'iran-public-and-international-research-v1','source_groups':groups,'publication_authorized':False,'historical_studies_are_not_current_local_observations':True,'commercial_sources_do_not_satisfy_public_research_requirement':True}

def review_covers_required_authorities(review,bundle):
 policy=bundle.get('research_policy')
 if policy is None:return True # Legacy fixtures; live general_source_bundle always enforces policy.
 indexes={f.get('source_index')for f in review.get('bound_technical_evidence',[])}
 return all(any(source['source_index']in indexes for source in group)for group in policy['source_groups'].values())
