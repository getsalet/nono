"""Shared editorial city scheduling; never rewrites titles, identities or progress."""
import json,re,unicodedata
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
CONFIG='data/blog-city-priority.json'
POLICY='major-cities-first-v1'
def normalize(value):
 value=unicodedata.normalize('NFKC',str(value or '')).translate(str.maketrans({'ي':'ی','ك':'ک','ى':'ی','\u200c':' ','ـ':''}))
 return re.sub(r'\s+','',value)
def config(root=None):
 path=Path(root or ROOT)/CONFIG
 if not path.exists():return None # Legacy/offline fixtures retain their prior order.
 value=json.loads(path.read_text())
 if value.get('enabled')is not True:return None
 if value.get('policy')!=POLICY:raise RuntimeError('Unknown city priority policy')
 for name in ('major_cities','provincial_capitals','important_county_cities','province_order'):
  rows=value.get(name)
  if not isinstance(rows,list)or not rows or any(not isinstance(x,str)or not normalize(x)for x in rows)or len(set(map(normalize,rows)))!=len(rows):raise RuntimeError('Invalid city priority list: '+name)
 if not isinstance(value.get('county_named_cities'),dict):raise RuntimeError('County city evidence required')
 return value

def enabled(root=None):return config(root)is not None

def _rank(item,cfg):
 city=normalize(item.get('city_fa'));kind=item.get('kind');family=item.get('family')
 if not city or kind=='article'or family=='hub':return (4,0,0,'')
 for tier,name in enumerate(('major_cities','provincial_capitals')):
  names=list(map(normalize,cfg[name]))
  if city in names:return (tier,names.index(city),0,'')
 province=item.get('province')or urlsplit(item.get('hub_url')or'').path.strip('/').split('/')[0]
 provinces=cfg['province_order'];prov_rank=provinces.index(province)if province in provinces else len(provinces)
 important=list(map(normalize,cfg['important_county_cities']))
 county_names=set(map(normalize,cfg['county_named_cities'].get(province,[])))
 if city in important:return (2,important.index(city),prov_rank,city)
 if city in county_names:return (2,len(important),prov_rank,city)
 return (3,0,prov_rank,city)

def ordered(items,root=None):
 cfg=config(root)
 return sorted(items,key=lambda x:_rank(x,cfg))if cfg else list(items)

def fresh(item):
 return (not item.get('published') and item.get('status','pending')in('pending','failed','needs_title_review')
         and not item.get('generated_at') and not item.get('_image_stock_request')
         and not item.get('_image_article_context') and not item.get('pid') and not item.get('published_url'))

def prioritize_queue(queue,root=None):
 """Only swap future-work slots. Frozen/published records stay at their index."""
 cfg=config(root)
 if not cfg:return queue
 rows=queue.get('items',[]);slots=[i for i,x in enumerate(rows)if fresh(x)]
 pending=sorted((rows[i]for i in slots),key=lambda x:_rank(x,cfg))
 for index,item in zip(slots,pending):rows[index]=item
 queue['city_priority_policy']=POLICY
 return queue
