"""Adapter to the proven maghala2 topic-aware single-pass scene recipe.
Source: kikibox/maghala2/automation/image_prompt_policy.py.
Agnes payload/reference/watermark order follows nono's exact-product rebuild.
"""
import hashlib,json,re
import blog_reference_image_policy as reference
POLICY='afp-one-generated-blog-image-v6-reference-integrated-topic-scene'
RECIPE_VERSION='maghala2-reference-v3-concise-topic-scene'
SOURCES=['https://github.com/kikibox/maghala2/blob/main/automation/image_prompt_policy.py','https://github.com/getsalet/nono/blob/main/automation/rebuild_city_images_preserve_posts.py','https://github.com/getsalet/nono/blob/main/.github/workflows/city-content-queue.yml']
# Add missing crop identities as data, without rewriting the upstream generation recipe.
reference.CROPS.update({'بامیه':'okra','پیاز':'onion','گوجه فرنگی':'tomato','گوجه‌فرنگی':'tomato','هندوانه':'watermelon','سیب زمینی':'potato','سیب‌زمینی':'potato'})
reference.CROP_VISUALS.update({'بامیه':'okra with broad connected palmately lobed leaves, upright ridged tapered green pods, and pale creamy-yellow flowers with a dark maroon throat','پیاز':'onion rows with upright tubular hollow blue-green leaves','گوجه فرنگی':'tomato plants with compound serrated leaves and attached tomato clusters','گوجه‌فرنگی':'tomato plants with compound serrated leaves and attached tomato clusters','هندوانه':'watermelon vines with deeply lobed leaves and restrained attached striped fruit','سیب زمینی':'potato rows with compound oval leaflets and low bushy canopies','سیب‌زمینی':'potato rows with compound oval leaflets and low bushy canopies'})
def context_from_post(post):
 text=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',post.get('html',''))).strip()
 return {'title':post.get('title',''),'meta_description':post.get('meta_description',''),'summary':text[:1200]}
def article(item):
 from blog_image_gate import family
 expected=family(item);context=item.get('_image_article_context')or context_from_post(item.get('post')or{})
 if not context.get('title')or len(context.get('summary',''))<40:raise RuntimeError('Actual post title and body summary required before image generation')
 identity=str(item.get('key',''))
 return {'source_id':hashlib.sha256(identity.encode()).hexdigest()[:16]+('-layflat'if expected=='hose'else'-tape20'),'slug':identity,'title':context['title'],'focus':item.get('angle')or item.get('topic')or item.get('site_title',''),'meta_description':context.get('meta_description',''),'summary':context['summary'],'_image_qa_feedback':item.get('_image_qa_feedback','')}
def role(item):
 a=article(item);text=' '.join((a['title'],a['focus'])).replace('‌',' ')
 # Body boilerplate often mentions pressure/filters: it must not turn every topic into the same hardware scene.
 if any(k in text for k in ('فیلتر','افت فشار','گرفتگی','نگهداری','اتصالات','اتصال','تخلیه')):return 3
 if any(crop in text for crop in reference.CROPS):return 1
 return 2

def scene_plan(item,blog):
 a=article(item);text=_lexical_text(a['title']+' '+a['focus'])
 if 'اتصال' in text:
  intent='connection';evidence='one closed ribbed compression union installed inline between two continuous black irrigation pipes; the joined ends and seal are visible, no open pipe end'
 elif any(k in text for k in ('فشار','فیلتر','گرفتگی','تخلیه')):
  intent='maintenance';evidence='one plausible installed filter and closed flush valve connected to the irrigation header'
 elif any(k in text for k in ('مراقبت','نگهداری','پایش')):
  intent='monitoring';evidence='continuous installed drip tape beside plants, with a clearly visible uniform dark soil wetting band along the root zone'
 elif any(k in text for k in ('فاصله','کاشت','بذر')):
  intent='spacing';evidence='parallel planted rows and continuous installed drip lines with evenly spaced emitters and a few plain unmarked spacing stakes'
 elif any(k in text for k in ('عملکرد','برداشت')):
  intent='crop';evidence='uniform healthy crop canopy and visible continuous irrigation lines near the roots'
 else:
  intent='agronomy';evidence='crop-specific leaves, continuous installed irrigation lines and localized root-zone wetting'
 cameras=['close side view','high oblique close view','medium three-quarter technical view']
 camera=cameras[int(hashlib.sha256((a['slug']+'|'+blog).encode()).hexdigest()[:6],16)%len(cameras)]
 return {'article_title':a['title'],'role':3 if intent in('connection','maintenance')else 2,'crop':reference.named_crop(a),'botany':reference.crop_identity_spec(a),'visual_brief':reference.visual_brief(a),'evidence':evidence,'intent':intent,'camera':camera,'recipe':RECIPE_VERSION}

def recipe_for(item):
 from blog_image_gate import family
 return RECIPE_VERSION+('-hose-native1k-v4-smallguide'if family(item)=='hose'else'')

def prompt(item,blog):
 # Differential live tests showed that the concise nested-reference request can
 # express technical equipment without the generic farmer/panorama response.
 # Retain exact upstream reference conditioning, not its 6k repeated directives.
 from blog_image_gate import family
 a=article(item);plan=scene_plan(item,blog)
 if family(item)=='hose':
  # Explicit reference roles and scene inventory: the third reference repeats
  # the same products, never authorizes an additional coil in the output.
  crop='A few neutral seedlings'if plan['role']==3 else plan['botany']
  text=(f"Create a NEW single photorealistic technical photograph, {plan['camera']}, natural daylight. "
   f"PRIMARY SUBJECT in the central two-thirds: {plan['evidence']}. This installed irrigation evidence is the largest sharp subject. {crop}. "
   'Reference 1 identifies the packaged AFP coil; reference 2 identifies the bare woven coil. Reference 3 repeats those SAME TWO items for layout only. '
   'FINAL PRODUCT INVENTORY: exactly two coils total, one packaged and one bare. Place this pair together as small secondary props in the lower-left soil area, 12 to 15 percent of frame width. '
   'Reconstruct both horizontally with authentic materials and packaging, common perspective, daylight and ground-contact shadows. Keep both complete with ground margins. '
   'One continuous equipment-and-soil photograph, no people, no inset, no added writing.')
  feedback=str(a.get('_image_qa_feedback')or'').strip()
  return text+(' Correct: '+feedback[:160]if feedback else'')
 product='exactly one low wide cylindrical AFP drip-tape carton, white printed sleeve and blue lower band, central top hole, diameter larger than height. It occupies about 20 percent of frame width'
 crop=('Use neutral small seedlings only near the hardware'if plan['role']==3 else'Crop identity: '+plan['botany'])
 brief=(f"One continuous photorealistic agricultural photograph, {plan['camera']}, soft natural daylight. "
  +f"Main subject: {plan['evidence']}. {crop}. Tight equipment-and-soil framing with no skyline. "
  +f"Naturally resting nearby: {product}. The reference is an identity guide, not a flat layer to paste. Reconstruct it in the same perspective and light, with ground contact and realistic shadows. "
  +'Keep each product fully inside the frame with clear margins; preserve authentic shape, material and package print. Equipment and plants are the story, products are secondary. Empty scene, no people. Single photograph, no inset, pasted panel, extra product or added writing. '
  +f"Article context, not on-image text: {a['title']}. {a['summary'][:360]}")
 feedback=str(a.get('_image_qa_feedback')or'').strip()
 if feedback:brief+=' Correct the prior visual rejection: '+feedback[:240]
 return brief
def references(item):
 from blog_image_gate import family
 if family(item)!='hose':
  # Preserve the directly accepted tape request bytes and cache identity.
  return reference.reference_images(role(item),article(item))
 # Pinned nono identity inputs: full originals FIRST,
 # then the 92/68-width guide of its integrated layflat test. Input only, never output paste-up.
 import base64,io
 from PIL import Image
 rows=[('afp-layflat.webp.b64','image/webp',92),('afp-layflat-bare.jpg.b64','image/jpeg',68)]
 refs=[];canvas=Image.new('RGBA',(1200,675),(238,238,235,255));x=96
 for filename,mime,width in rows:
  encoded=(reference.ASSET_DIR/filename).read_text(encoding='ascii').strip()
  raw=base64.b64decode(encoded,validate=True)
  product=Image.open(io.BytesIO(raw)).convert('RGBA')
  refs.append('data:'+mime+';base64,'+encoded)
  product.thumbnail((width,600),Image.Resampling.LANCZOS)
  canvas.alpha_composite(product,(x,610-product.height));x+=product.width+8
 out=io.BytesIO();canvas.convert('RGB').save(out,'WEBP',quality=92,method=6)
 return refs+['data:image/webp;base64,'+base64.b64encode(out.getvalue()).decode('ascii')]

def topic_hash(item):
 data=article(item);data.pop('_image_qa_feedback',None)
 return hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

# Targeted lexical correction around the unmodified upstream recipe. A substring
# such as سیر in مسیر is not a crop mention. Headline evidence wins over body text.
def _lexical_text(value):
 return re.sub(r'\s+',' ',str(value or '').replace('‌',' ').replace('ي','ی').replace('ك','ک')).strip()
def _crop_key(a):
 for field in ('title','focus','meta_description','summary'):
  text=_lexical_text(a.get(field,''))
  for key in sorted(reference.CROPS,key=lambda k:len(_lexical_text(k)),reverse=True):
   if re.search(r'(?<!\w)'+re.escape(_lexical_text(key))+r'(?!\w)',text,re.UNICODE):return key
 return None
def _named_crop(a):
 key=_crop_key(a)
 return f'{key} ({reference.CROPS[key]})'if key else'the exact named crop from the article title'
def _crop_identity(a):
 key=_crop_key(a)
 return reference.CROP_VISUALS.get(key,f'{key} ({reference.CROPS[key]}) with botanically accurate leaves, stems, growth habit and harvest stage')if key else'the exact named crop from the article title with botanically accurate, unmistakable morphology'
reference.named_crop=_named_crop
reference.crop_identity_spec=_crop_identity
