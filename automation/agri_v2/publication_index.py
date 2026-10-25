"""Public links from verified generator receipts only; never inferred from job success."""
import datetime
from urllib.parse import urlsplit
from .queue import OUT,load_json

def verified_publications(out=OUT,limit=10):
 rows=[]
 for p in (out/'new').glob('*/wordpress-receipt.json'):
  try:
   r=load_json(p);url=r.get('url','');u=urlsplit(url)
   if (r.get('public_verified') is not True or r.get('status')!='published' or r.get('public_http_status')!=200
       or type(r.get('post_id'))is not int or r['post_id']<=0 or u.scheme!='https' or u.hostname!='navar-abyari.ir'
       or u.username or u.password or u.port not in (None,443)):continue
   verified=datetime.datetime.fromisoformat(r['verified_at'].replace('Z','+00:00'))
   published=datetime.datetime.fromisoformat(r.get('published_at',r['verified_at']).replace('Z','+00:00'))
   if verified.tzinfo is None or published.tzinfo is None:continue
   article=load_json(p.with_name('article.json'))
   if not isinstance(article.get('title'),str) or not article['title'].strip():continue
   rows.append({'topic_id':p.parent.name,'post_id':r['post_id'],'title':article['title'],'url':url,'published_at':published.isoformat(),'verified_at':verified.isoformat(),'public_verified':True,'_sort':published.timestamp()})
  except (ValueError,KeyError,TypeError,OSError):continue
 rows.sort(key=lambda x:(x['_sort'],x['post_id']),reverse=True)
 result=[];seen=set()
 for row in rows:
  if row['post_id'] in seen:continue
  seen.add(row['post_id']);row.pop('_sort');result.append(row)
  if len(result)>=limit:break
 return result
