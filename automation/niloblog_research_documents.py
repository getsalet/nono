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
 request=urllib.request.Request(DOCUMENTS[ref]['url'],headers={'User-Agent':'AFP-Niloblog-editorial/1.0'})
 with urllib.request.urlopen(request,timeout=45)as response:
  if response.status!=200:raise ValueError('Research document HTTP status changed')
  raw=response.read(MAX_BYTES+1)
  return verify_pdf(raw,ref,response.url,response.headers.get('Content-Type',''))
