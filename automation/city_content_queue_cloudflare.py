#!/usr/bin/env python3
"""Cloudflare/Lucid Origin production adapter for missing-city draft queue."""
import base64,hashlib,io,json,os,time,urllib.error,urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import city_content_queue as q

MODEL=os.getenv('CLOUDFLARE_IMAGE_MODEL','@cf/leonardo/lucid-origin')
TOKEN=os.getenv('CLOUDFLARE_API_TOKEN','').strip(); ACCOUNT=os.getenv('CLOUDFLARE_ACCOUNT_ID','').strip()
IMAGE_COUNT=5
ARTICLE_WORKERS=max(1,int(os.getenv('ARTICLE_WORKERS','4')))
IMAGE_WORKERS=max(1,int(os.getenv('IMAGE_WORKERS','8')))
WATERMARK='AFP | 09134922013'
ALT_TEMPLATES={
 1:'تصویر شاخص راهنمای خرید نوار آبیاری در {city}',
 2:'انتخاب نوار تیپ متناسب با مزرعه {city}',
 3:'فیلتر و تنظیم فشار سیستم آبیاری قطره‌ای در {city}',
 4:'نصب صحیح نوار آبیاری در ردیف‌های کشت {city}',
 5:'بازرسی و نگهداری نوار آبیاری در مزرعه {city}',
}
SCENES={
 1:'wide hero view of healthy crop rows with drip irrigation tape clearly visible, professional editorial composition',
 2:'close view comparing drip irrigation tape thickness and emitter spacing beside crop rows',
 3:'technical yet natural farm scene showing irrigation filter, pressure regulator and clean water connections',
 4:'careful installation of drip irrigation tape along straight crop rows, hands visible but no identifiable face',
 5:'inspection and maintenance of drip irrigation lines, checking emitters and preventing leaks in a clean field',
}

def font(size):
 for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf'):
  if Path(p).exists(): return ImageFont.truetype(p,size)
 return ImageFont.load_default()

def watermark(blob):
 im=Image.open(io.BytesIO(blob)).convert('RGB'); layer=Image.new('RGBA',im.size,(0,0,0,0)); draw=ImageDraw.Draw(layer)
 f=font(max(18,im.width//38)); box=draw.textbbox((0,0),WATERMARK,font=f); tw,th=box[2]-box[0],box[3]-box[1]
 pad=max(10,im.width//80); x=im.width-tw-pad*2; y=im.height-th-pad*2
 draw.rounded_rectangle((x-pad,y-pad,im.width-pad//2,im.height-pad//2),radius=9,fill=(0,0,0,155))
 draw.text((x,y),WATERMARK,font=f,fill=(255,255,255,235))
 out=io.BytesIO(); Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB').save(out,'JPEG',quality=91,optimize=True); return out.getvalue()

def image_prompt(item,kind):
 return (f"Photorealistic editorial agriculture image made specifically for a Persian SEO article about buying and using drip irrigation tape in "
         f"{item['city']}, {item['county']} county, {item['province']} province, Iran. {SCENES[kind]}. "
         "Use plausible agricultural scenery and climate cues only, without famous landmarks or unverifiable local claims. "
         "Natural light, realistic soil and equipment, accurate drip irrigation tape, commercial photography, no generated text, no logo, no watermark, 16:9 composition.")

def generate_image(item,kind):
 if not TOKEN or not ACCOUNT: raise RuntimeError('Cloudflare Actions secrets are missing')
 endpoint='https://'+'api.cloudflare.com/client/v4/accounts/'+ACCOUNT+'/ai/run/'+MODEL
 payload={'prompt':image_prompt(item,kind),'width':768,'height':432,'num_steps':20,'guidance':4.5,'seed':(int(item['source_id'])+kind)%2147483647}
 req=urllib.request.Request(endpoint,data=json.dumps(payload).encode(),method='POST',headers={'Authorization':'Bearer '+TOKEN,'Content-Type':'application/json','Accept':'application/json','User-Agent':'navar-city-content-queue/2.0'})
 try:
  with urllib.request.urlopen(req,timeout=300) as response:data=json.loads(response.read())
 except urllib.error.HTTPError as exc:raise RuntimeError(f"Cloudflare HTTP {exc.code}: {exc.read().decode('utf-8','replace')[:1000]}")
 image=(data.get('result') or {}).get('image')
 if not data.get('success') or not image:raise RuntimeError('Cloudflare image response was unsuccessful')
 blob=watermark(base64.b64decode(image))
 if len(blob)<10000:raise RuntimeError('Generated image is unexpectedly small')
 name=f"{item['source_id']}-{kind}.jpg";(q.IMAGES/name).write_bytes(blob);return name,hashlib.sha256(blob).hexdigest()

def make_content(item,links):
 approved=links[:12]; link_lines='\n'.join(f"- {x['title']} | {x['url']}" for x in approved)
 prompt=f'''برای شهر {item['city']} در شهرستان {item['county']}، استان {item['province']} یک مقاله کاملاً جدید، فارسی، کاربردی و سئوشده درباره انتخاب و خرید نوار آبیاری بنویس. متن باید دست‌کم {q.MIN_WORDS} کلمه باشد و از ادعای ساختگی درباره اقلیم، قیمت، نمایندگی، موجودی یا ارسال محلی خودداری کند. ساختار HTML فقط با h2/h3/p/ul/ol/table/strong/a باشد و H1 نداشته باشد. موضوعات لازم: نیازسنجی مزرعه، انتخاب ضخامت و فاصله قطره‌چکان، فشار و فیلتراسیون، طراحی، نصب، نگهداری، خطاهای رایج، FAQ و جمع‌بندی. حداقل {q.MIN_LINKS} و حداکثر ۷ لینک داخلی فقط از فهرست زیر استفاده کن. برای چهار تصویر داخل متن، نشانگرهای دقیق [[[IMAGE_2]]], [[[IMAGE_3]]], [[[IMAGE_4]]], [[[IMAGE_5]]] را هرکدام دقیقاً یک بار و بلافاصله پس از بخشی مرتبط با موضوع همان تصویر قرار بده. تصویر شماره ۱ شاخص است و نشانگر داخل متن ندارد. JSON معتبر با کلیدهای title, meta_title, meta_description, focus_keyword, excerpt, html برگردان.\nلینک‌های مجاز:\n{link_lines}'''
 for _ in range(4):
  obj=q.agnes(prompt); body=obj.get('html',''); used=q.internal_links(body); allowed={x['url'] for x in approved}
  if q.words(body)>=q.MIN_WORDS and q.MIN_LINKS<=len(used)<=7 and not(used-allowed) and all(body.count(f'[[[IMAGE_{i}]]]')==1 for i in range(2,6)):return obj
  prompt+='\nنسخه قبلی کنترل کیفیت را رد کرد؛ طول متن، لینک‌های مجاز و چهار نشانگر تصویر را دقیق اصلاح کن.'
 raise RuntimeError('Text QA failed after 4 attempts')

def sql_for(item,obj,image_names):
 title=obj['title'];body=obj['html'];urls=[]
 for name in image_names:urls.append(f'{q.SITE}/wp-content/uploads/2026/09/navar-city-generated/{name}')
 for i in range(2,6):
  alt=ALT_TEMPLATES[i].format(city=item['city']);body=body.replace(f'[[[IMAGE_{i}]]]',f'<figure class="wp-block-image size-large"><img src="{urls[i-1]}" alt="{alt}"/><figcaption>{alt}</figcaption></figure>')
 pt=item['post_type'];slug=item['slug'];excerpt=obj.get('excerpt','');marker=str(item.get('source_id',''))
 commands=[q.sql_preamble(),'START TRANSACTION;',f"SET @existing_post=(SELECT ID FROM `{q.TABLE}` WHERE `post_name`='{q.esc(slug)}' AND `post_type`='{q.esc(pt)}' LIMIT 1);",'SET @created_post=IF(@existing_post IS NULL,1,0);',f"INSERT INTO `{q.TABLE}` (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) SELECT 1,NOW(),UTC_TIMESTAMP(),'{q.esc(body)}','{q.esc(title)}','{q.esc(excerpt)}','draft','closed','closed','{q.esc(slug)}',NOW(),UTC_TIMESTAMP(),0,'',0,'{q.esc(pt)}','',0 WHERE @created_post=1;",'SET @post_id=COALESCE(@existing_post,LAST_INSERT_ID());']
 metadata=[('_rank_math_title',obj.get('meta_title','')),('_rank_math_description',obj.get('meta_description','')),('rank_math_focus_keyword',obj.get('focus_keyword','')),('_navar_geo_level','city'),('_navar_city',item['city']),('_navar_county',item['county']),('_navar_province',item['province']),('_navar_city_queue_generated',marker)]
 for key,val in metadata:commands.append(f"INSERT INTO `{q.META}` (`post_id`,`meta_key`,`meta_value`) SELECT @post_id,'{q.esc(key)}','{q.esc(val)}' WHERE @created_post=1 AND NOT EXISTS (SELECT 1 FROM `{q.META}` WHERE post_id=@post_id AND meta_key='{q.esc(key)}');")
 for idx,(name,url) in enumerate(zip(image_names,urls),1):
  alt=ALT_TEMPLATES[idx].format(city=item['city']);media_slug=name.rsplit('.',1)[0];mime='image/webp' if name.lower().endswith('.webp') else ('image/png' if name.lower().endswith('.png') else 'image/jpeg')
  commands += [f"SET @media_{idx}=(SELECT ID FROM `{q.TABLE}` WHERE post_parent=@post_id AND post_type='attachment' AND post_name='{q.esc(media_slug)}' LIMIT 1);",f"INSERT INTO `{q.TABLE}` (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) SELECT 1,NOW(),UTC_TIMESTAMP(),'','{q.esc(alt)}','','inherit','open','closed','{q.esc(media_slug)}',NOW(),UTC_TIMESTAMP(),@post_id,'{q.esc(url)}',0,'attachment','{mime}',0 WHERE @created_post=1 AND @media_{idx} IS NULL;",f"SET @media_{idx}=COALESCE(@media_{idx},LAST_INSERT_ID());",f"INSERT INTO `{q.META}` (`post_id`,`meta_key`,`meta_value`) SELECT @media_{idx},'_wp_attached_file','2026/09/navar-city-generated/{q.esc(name)}' WHERE @created_post=1 AND NOT EXISTS (SELECT 1 FROM `{q.META}` WHERE post_id=@media_{idx} AND meta_key='_wp_attached_file');",f"INSERT INTO `{q.META}` (`post_id`,`meta_key`,`meta_value`) SELECT @media_{idx},'_wp_attachment_image_alt','{q.esc(alt)}' WHERE @created_post=1 AND NOT EXISTS (SELECT 1 FROM `{q.META}` WHERE post_id=@media_{idx} AND meta_key='_wp_attachment_image_alt');"]
 commands += [f"INSERT INTO `{q.META}` (`post_id`,`meta_key`,`meta_value`) SELECT @post_id,'_thumbnail_id',@media_1 WHERE @created_post=1 AND @media_1 IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{q.META}` WHERE post_id=@post_id AND meta_key='_thumbnail_id');",'COMMIT;']
 rollback='\n'.join([q.sql_preamble(),'START TRANSACTION;',f"SET @rollback_post_id=(SELECT p.ID FROM `{q.TABLE}` p JOIN `{q.META}` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='{q.esc(marker)}' WHERE p.post_name='{q.esc(slug)}' AND p.post_type='{q.esc(pt)}' LIMIT 1);",f"DELETE pm FROM `{q.META}` pm JOIN `{q.TABLE}` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';",f"DELETE FROM `{q.TABLE}` WHERE post_parent=@rollback_post_id AND post_type='attachment';",f"DELETE FROM `{q.META}` WHERE post_id=@rollback_post_id;",f"DELETE FROM `{q.TABLE}` WHERE ID=@rollback_post_id;",'COMMIT;'])+'\n'
 return '\n'.join(commands)+'\n',rollback,body

def migrate(queue):
 queue['version']=2; queue['text_model']=q.AGNES_MODEL; queue['image_model']=MODEL; queue['images_per_post']=5
 queue.setdefault('rules',{}).update({'draft_only':True,'minimum_words':q.MIN_WORDS,'minimum_internal_links':q.MIN_LINKS,'featured_images':1,'inline_images':4,'watermark':WATERMARK,'article_workers':ARTICLE_WORKERS,'image_workers':IMAGE_WORKERS})
 for item in queue['items']:
  if item.get('status')=='blocked_image_model':
   item['status']='pending';item['attempts']=0
   for k in ('last_error','failed_at','started_at','image_model_error'):item.pop(k,None)
 queue.pop('image_model_error',None);queue['updated_at']=q.now();q.QUEUE.write_text(json.dumps(queue,ensure_ascii=False,indent=2),encoding='utf-8')

class StageFailure(RuntimeError):
 def __init__(self,stage,error):self.stage=stage;self.original=error;super().__init__(str(error))

def generate_images_parallel(item,pool):
 futures={pool.submit(generate_image,item,kind):kind for kind in range(1,6)};results={}
 for future in as_completed(futures):
  kind=futures[future];results[kind]=future.result()
 return [results[kind] for kind in range(1,6)]

def _produce_item(item,links,image_pool):
 try:obj=make_content(item,links)
 except Exception as exc:raise StageFailure('text',exc) from exc
 try:rows=generate_images_parallel(item,image_pool)
 except Exception as exc:raise StageFailure('image',exc) from exc
 return obj,[row[0] for row in rows],[row[1] for row in rows]

def process(queue):
 batch=[x for x in queue['items'] if x.get('status')=='pending' and x.get('attempts',0)<q.MAX_ATTEMPTS][:q.BATCH]
 if not batch:
  result='complete_with_failures' if any(x.get('status')=='failed' for x in queue['items']) else 'complete'
  q.write_status(queue,result);return
 for item in batch:item.update(status='processing',attempts=item.get('attempts',0)+1,started_at=q.now())
 queue['updated_at']=q.now();q.QUEUE.write_text(json.dumps(queue,ensure_ascii=False,indent=2),encoding='utf-8');q.write_status(queue,'processing')
 failures=[];deferred=[];successes=0;article_workers=min(ARTICLE_WORKERS,len(batch))
 with ThreadPoolExecutor(max_workers=IMAGE_WORKERS,thread_name_prefix='city-image') as image_pool:
  with ThreadPoolExecutor(max_workers=article_workers,thread_name_prefix='city-article') as article_pool:
   future_items={article_pool.submit(_produce_item,item,queue['link_index'],image_pool):item for item in batch}
   for future in as_completed(future_items):
    item=future_items[future];stage='text'
    try:
     obj,names,hashes=future.result();stage='sql'
     insert,rollback,body=sql_for(item,obj,names)
     (q.SQL/f"{item['source_id']}.sql").write_text(insert,encoding='utf-8');(q.ROLLBACK/f"{item['source_id']}.sql").write_text(rollback,encoding='utf-8')
     (q.ITEMS/f"{item['source_id']}.json").write_text(json.dumps({**item,**obj,'html':body,'images':names,'image_sha256':hashes,'image_roles':['featured','inline','inline','inline','inline'],'watermark':WATERMARK},ensure_ascii=False,indent=2),encoding='utf-8')
     item.update(status='completed',completed_at=q.now(),word_count=q.words(body),images=names,last_error='');item.pop('started_at',None);item.pop('failed_at',None)
     successes+=1
    except Exception as exc:
     if isinstance(exc,StageFailure):stage=exc.stage;error=exc.original
     else:error=exc
     msg=str(error)[:1200];qa_retry=stage=='image' and 'image hard gate rejected role' in msg
     if qa_retry:
      # Quarantine a visually impossible item instead of resetting its
      # attempt counter and selecting it forever on every scheduled run.
      item.update(status='failed',last_error=msg,failed_stage='image_qa_deferred',failed_at=q.now())
      item.pop('started_at',None)
      deferred.append(str(item.get('source_id') or ''))
     else:
      item.update(status='failed',failed_at=q.now(),last_error=msg,failed_stage=stage);item.pop('started_at',None)
     failures.append(f"{item['source_id']} ({stage}): {type(error).__name__}: {error}")
    queue['updated_at']=q.now();q.QUEUE.write_text(json.dumps(queue,ensure_ascii=False,indent=2),encoding='utf-8');q.write_status(queue,'processing')
 (q.OUT/'create-all-completed.sql').write_text('\n'.join(['-- Editorially reviewed generated posts.',q.sql_preamble()]+[path.read_text(encoding='utf-8') for path in sorted(q.SQL.glob('*.sql'))]),encoding='utf-8')
 (q.OUT/'rollback-all-completed.sql').write_text('\n'.join([q.sql_preamble()]+[path.read_text(encoding='utf-8') for path in sorted(q.ROLLBACK.glob('*.sql'))]),encoding='utf-8')
 result='ready_with_failures' if any(x.get('status')=='failed' for x in queue['items']) else 'ready';q.write_status(queue,result)
 if failures and not successes and not deferred:raise RuntimeError('All queue items failed: '+' | '.join(failures))
 if deferred:print('deferred_image_qa_items='+','.join(deferred),flush=True)
 if failures:print('partial_success failures='+' | '.join(failures),flush=True)


def main():
 q.IMAGE_MODEL=MODEL
 queue=q.initialize(False);migrate(queue);process(queue)
if __name__=='__main__':main()
