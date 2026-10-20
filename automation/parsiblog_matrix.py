"""Deterministic 1000-title inventory; never infer a crop from a city name."""
import hashlib,json,re,collections
from pathlib import Path
from blog_city_editorial import approved_crop_records,title_errors
ROOT=Path(__file__).resolve().parents[1]
TAPE=['راهنمای انتخاب نوار تیپ در {city}؛ از نیاز تا سفارش','نوار آبیاری در {city}؛ کدام مشخصات را بررسی کنیم؟','چک‌لیست خرید نوار تیپ برای کشاورزان {city}','پیش از سفارش نوار تیپ در {city} این پرسش‌ها را بپرسید','نوار تیپ در {city}؛ خطاهای رایج انتخاب و نصب','برگه فنی نوار تیپ در {city} را چگونه بخوانیم؟','از سفارش تا تحویل نوار آبیاری در {city}','نوار تیپ در {city}؛ ثبت اطلاعات زمین پیش از خرید','بازبینی مسیر نوار آبیاری در {city} پیش از اجرا','نوار تیپ در {city}؛ نگهداری و بررسی دوره‌ای']
HOSE=['انتخاب لوله نخی و تاشو در {city}؛ راهنمای عملی','لوله انتقال آب در {city}؛ چک‌لیست بررسی اتصالات','پیش از خرید لوله نخی در {city} چه اطلاعاتی لازم است؟','لوله تاشو در {city}؛ از بررسی مسیر تا سفارش','خطاهای انتخاب لوله انتقال آب در {city}','مقایسه پیشنهادهای لوله نخی و تاشو در {city}','لوله انتقال آب در {city}؛ بازبینی و نگهداری','مشخصات لوله نخی در {city} را چگونه بررسی کنیم؟','لوله تاشو در {city}؛ پرسش‌های مهم هنگام تحویل','برنامه بازدید مسیر انتقال آب در {city}']
def build(root=ROOT):
 root=Path(root);src=json.loads((root/'data/roya/backlink-queue.json').read_text())['items'];eligible=[];seen=set()
 for x in src:
  if x.get('family') not in ('tape20','hose') or not x.get('city_fa') or x.get('target_url')==x.get('hub_url'):continue
  if x['target_url'] in seen:continue
  seen.add(x['target_url']);eligible.append(x)
 def evidence(x):return approved_crop_records(x,root)
 # Verified crop rows first, then deterministic cross-city coverage, then second families.
 eligible.sort(key=lambda x:(not bool(evidence(x)),hashlib.sha256(x['target_url'].encode()).hexdigest()))
 places=set();first=[];second=[]
 for x in eligible:
  place=(x.get('hub_url'),x['city_fa'])
  if place not in places:first.append(x);places.add(place)
  else:second.append(x)
 chosen=first+second;used=set();items=[]
 for x in chosen:
  records=evidence(x);city=x['city_fa'];key='pb-'+hashlib.sha256(x['target_url'].encode()).hexdigest()[:20]
  pool=[]
  if records:
   row=records[0];place=('شهرستان '+row['county_fa']) if row['scope']=='county' else city
   pool=[('نوار تیپ' if x['family']=='tape20' else 'انتقال آب')+' برای '+row['crop']+' در '+place+'؛ نکات انتخاب']
  pool +=[t.format(city=city) for t in (TAPE if x['family']=='tape20' else HOSE)]
  offset=int(key[-4:],16)%len(pool)
  if not records:pool=pool[offset:]+pool[:offset]
  title=next((t for t in pool if 12<=len(t)<=65 and t not in used and not title_errors(x,t,root)),None)
  if not title:continue
  used.add(title)
  item={k:x.get(k,'') for k in ('city_fa','province_fa','family','target_url','hub_url','site_title')}
  matched=[r for r in records if r['crop'] in title]
  item.update(key=key,kind='city',assigned_title=title,angle=title.split('؛')[-1],evidence=matched,status='pending',source_key=x['key'])
  items.append(item)
  if len(items)==1000:break
 if len(items)!=1000:raise RuntimeError('Insufficient unique evidence-safe city titles')
 return {'version':'parsiblog-city-1000-v1','approved':True,'approval_note':'User explicitly requested a 1000-title city/crop inventory and generator setup; crop claims remain evidence-bound.','link_count':3,'count':1000,'crop_title_count':sum(bool(x['evidence']) for x in items),'cities':len({(x['hub_url'],x['city_fa'])for x in items}),'items':items}
def main():
 p=ROOT/'data/parsiblog/title-matrix.json';p.parent.mkdir(parents=True,exist_ok=True);obj=build();p.write_text(json.dumps(obj,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in obj.items() if k!='items'},ensure_ascii=False))
if __name__=='__main__':main()
