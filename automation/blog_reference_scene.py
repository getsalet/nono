"""Adapter to the proven maghala2 topic-aware single-pass scene recipe.
Source: kikibox/maghala2/automation/image_prompt_policy.py.
Agnes payload/reference/watermark order follows nono's exact-product rebuild.
"""
import hashlib,json,re
import blog_reference_image_policy as reference
POLICY='afp-one-generated-blog-image-v6-reference-integrated-topic-scene'
RECIPE_VERSION='maghala2-reference-v3-concise-topic-scene'
# Separate from the reference/model recipe: binds candidates and reviews to this
# corrected topic/physical-role contract without rewriting old acceptance records.
SCENE_CONTRACT='off-axis-carton-soil-island-v3'
SOURCES=['https://github.com/kikibox/maghala2/blob/main/automation/image_prompt_policy.py','https://github.com/getsalet/nono/blob/main/automation/rebuild_city_images_preserve_posts.py','https://github.com/getsalet/nono/blob/main/.github/workflows/city-content-queue.yml']
# Add missing crop identities as data, without rewriting the upstream generation recipe.
reference.CROPS.update({'آفتابگردان':'sunflower','آفتاب گردان':'sunflower','بامیه':'okra','پیاز':'onion','گوجه فرنگی':'tomato','گوجه‌فرنگی':'tomato','هندوانه':'watermelon','سیب زمینی':'potato','سیب‌زمینی':'potato'})
reference.CROP_VISUALS.update({'آفتابگردان':'sunflower plants with upright stems and broad rough serrated heart-shaped leaves; at flowering, recognizable yellow ray petals around a dark central disk','آفتاب گردان':'sunflower plants with upright stems and broad rough serrated heart-shaped leaves; at flowering, recognizable yellow ray petals around a dark central disk','بامیه':'okra with broad connected palmately lobed leaves, upright ridged tapered green pods, and pale creamy-yellow flowers with a dark maroon throat','پیاز':'onion rows with upright tubular hollow blue-green leaves','گوجه فرنگی':'tomato plants with compound serrated leaves and attached tomato clusters','گوجه‌فرنگی':'tomato plants with compound serrated leaves and attached tomato clusters','هندوانه':'watermelon vines with deeply lobed leaves and restrained attached striped fruit','سیب زمینی':'potato rows with compound oval leaflets and low bushy canopies','سیب‌زمینی':'potato rows with compound oval leaflets and low bushy canopies'})
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
 if any(term in text for term in ('بغل دوخت','پلاکدار','پلاک دار')):
  intent='tape_construction';evidence='a close technical view of two short unbranded thin flattened drip-tape sample sections lying parallel on bare soil: one with a visible welded edge seam, the other with a discreet integrated emitter; a continuous thin installed drip-tape lateral remains visible nearby. These are small tape samples, not additional commercial rolls or packages; no invented labels or dimensions'
 elif 'اتصال' in text:
  intent='connection';evidence='one closed ribbed compression union installed inline between two continuous black irrigation pipes; the joined ends and seal are visible, no open pipe end'
 elif 'فشار' in text:
  intent='pressure';evidence='one small pressure gauge on a short normal threaded port of a continuous irrigation header, and a separate thin flattened drip-tape lateral connected by a normal small take-off fitting; gauge face angled away so no readable scale or pressure rating is invented'
 elif 'فیلتر' in text:
  intent='filtration';evidence='one compact irrigation filter installed with closed connections in a continuous irrigation header, and a thin flattened drip-tape lateral connected downstream by a normal small take-off fitting'
 elif any(k in text for k in ('گرفتگی','تخلیه')):
  intent='flushing';evidence='the closed flush end of a thin flattened installed drip-tape lateral beside the root zone, with an identifiable normal flush end closure, not a rigid oversized pipe'
 elif any(k in text for k in ('مراقبت','نگهداری','پایش')):
  intent='monitoring';evidence='continuous thin flattened installed drip tape beside crop roots, with a clearly visible continuous dark wet-soil strip along the root zone, strongly contrasting with lighter dry soil outside the strip'
 elif any(k in text for k in ('فاصله','کاشت','بذر')):
  intent='spacing';evidence='parallel planted rows and continuous installed drip lines with evenly spaced emitters and a few plain unmarked spacing stakes'
 elif any(k in text for k in ('عملکرد','برداشت')):
  intent='crop';evidence='uniform healthy crop canopy and visible continuous irrigation lines near the roots'
 else:
  intent='agronomy';evidence=('crop-specific leaves, 'if _crop_key(a)else'neutral small seedlings, ')+'continuous thin flattened installed drip-tape laterals and localized root-zone wetting'
 cameras=['close side view','high oblique close view','medium three-quarter technical view']
 camera=cameras[int(hashlib.sha256((a['slug']+'|'+blog).encode()).hexdigest()[:6],16)%len(cameras)]
 return {'article_title':a['title'],'scene_contract':SCENE_CONTRACT,'setting':_setting(a),'role':3 if intent in('connection','pressure','filtration','flushing')else 2,'crop':reference.named_crop(a),'botany':reference.crop_identity_spec(a),'visual_brief':reference.visual_brief(a),'evidence':evidence,'intent':intent,'camera':camera,'recipe':RECIPE_VERSION}

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
 crop=('Crop identity: '+plan['botany']+'. Show unmistakable attached crop leaves and growth habit in an adjacent bed, also in technical close views'
  if _crop_key(a) else 'A few neutral small seedlings beside the irrigation bed; no invented named crop')
 technical_priority=('The RIGHT half must clearly show dark moist soil directly alongside the installed tape and plant roots, bordered by lighter dry soil. Only the separate carton island is dry; do not make the entire irrigated root zone dry. 'if plan['intent']=='monitoring'else'')
 brief=(f"One continuous photorealistic agricultural photograph, {plan['camera']}, soft natural daylight. "
  +f"Setting: {plan['setting']}. Main subject: {plan['evidence']}. {technical_priority}{crop}. Tight equipment-and-soil framing with no skyline. "
  +f"Place the complete commercial package in the LOWER-LEFT quarter on a dedicated dry-soil island. Keep ALL installed irrigation lines in the RIGHT half, at least one carton diameter away from the package footprint. No line behind the carton, no collinear line disappearing under its front rim and reappearing behind it. No loose coil, no spare roll, no tape emerging from the carton; all installed tape remains straight along the planted rows. Show a broad uninterrupted dry-soil gap all around the base. The off-axis package is a standalone commercial package on soil, visibly separated from all pipes and fittings, never on the irrigation route: {product}. A visible strip of bare soil separates the entire carton base from every pipe; never balance or rest the carton on plumbing. No white ribbon, strap or printed strip emerges from the carton; installed drip tape is a separate thin black flattened lateral. Keep the required technical fitting unobstructed in the foreground. No pipe passes through its central hole; the carton is never a coupling, sleeve, filter, valve or installed hardware. Connect only the separate thin flattened drip tape, never its package, to the header. The reference is an identity guide, not a flat layer to paste. Reconstruct it in the same perspective and light, with ground contact and realistic shadows. "
  +'Keep each product fully inside the frame with clear margins; preserve authentic shape, material and package print. Equipment and plants are the story, products are secondary. Empty scene, no people. Single photograph, no inset, pasted panel, extra product or added writing. '
  +f"Article context, not on-image text: {a['title']}. {a['summary'][:360]}")
 feedback=str(a.get('_image_qa_feedback')or'').strip()
 if feedback:brief+=' Correction for this attempt: '+_feedback_direction(a,plan,feedback)
 # End with the actual photographed arrangement, not article prose that can
 # pull the model back into a stock product-on-pipe field composition.
 brief+=(' Final scene layout: LEFT foreground is one fully enclosed AFP package standing directly on an empty soil patch; its complete base is surrounded by bare soil. RIGHT foreground is the installed irrigation evidence: '+plan['evidence']+'. A broad empty soil corridor, at least one carton diameter wide, separates these two areas. The package is a sealed display object with a clean silhouette; the operating tape belongs only to the crop bed.')
 return brief
def references(item):
 from blog_image_gate import family
 if family(item)!='hose':
  # Preserve the accepted tape reference bytes; topic contract versions the cache.
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
 data['scene_contract']=SCENE_CONTRACT
 return hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def _setting(a):
 # Use headline/description and the introduction, not incidental comparison tables.
 text=_lexical_text(' '.join((a['title'],a.get('meta_description',''),a.get('summary','')[:360])))
 if 'گلخانه' in text or re.search(r'\bgreenhouse\b',text,re.I):
  return 'inside a greenhouse growing area with a visible softly blurred greenhouse frame, crop beds and a soil walkway; do not invent a specific hydroponic apparatus'
 return 'a non-geolocated agricultural crop bed with soil; no invented location or climate'

def _feedback_direction(a,plan,feedback):
 # Remove stale generic species demands created by the former no-crop fallback.
 if not _crop_key(a):
  feedback=re.sub(r'Keep the named crop botanically unmistakable:[^.]*\.\s*','',feedback)
  feedback=feedback.replace('Match the crop, setting and installed evidence of this article.','Match the setting and installed evidence of this article.')
  feedback=feedback.replace('Show this exact installed evidence: crop-specific leaves, continuous installed irrigation lines and localized root-zone wetting.','Show this exact installed evidence: '+plan['evidence']+'.')
 flags={
  'crop_contradiction':'Keep the named crop botanically unmistakable: '+plan['botany']+'.',
  'topic_match':'Match the crop, setting and installed evidence of this article.',
  'technical_evidence_match':'Show this exact installed evidence: '+plan['evidence']+'.',
  'packaging_not_used_as_hardware':'The single AFP carton stands separately on soil; no pipe through it.',
  'product_role_plausible':'Separate the commercial carton from all installed plumbing.',
  'package_soil_gap_visible':'Move the carton to the lower-left dry-soil island; all lines stay one carton diameter to its right, never under or behind it.',
  'irrigation_geometry_plausible':'Use normal connected header fittings and a thin flattened drip-tape lateral.',
  'product_count_match':'Show exactly one commercial AFP carton, no duplicate.',
  'product_fully_in_frame':'Keep the complete carton inside clear soil margins.',
 }
 found=[direction for flag,direction in flags.items()if flag in feedback]
 return ' '.join(found) if found else feedback[:700]

def rejection_feedback(item,digest,root,fallback):
 """Use saved structured rejection flags instead of a truncated exception tail.
 Free-form vision reasons remain in the diagnostic record, not as instructions.
 """
 from pathlib import Path
 from blog_image_gate import family
 expected=family(item)
 path=Path(root)/'artifacts/blog-image-reviews'/f'{expected}-{digest}.json'
 try:record=json.loads(path.read_text())
 except (OSError,ValueError):return fallback
 if record.get('sha256')!=digest or record.get('family')!=expected:return fallback
 v=record.get('verdict')
 if not isinstance(v,dict):return fallback
 bad=[k for k in ('topic_match','technical_evidence_match','packaging_not_used_as_hardware','product_role_plausible','package_soil_gap_visible','irrigation_geometry_plausible','product_count_match','product_fully_in_frame')if v.get(k)is False]
 if v.get('crop_contradiction')is True:bad.insert(0,'crop_contradiction')
 if not bad:return fallback
 return _feedback_direction(article(item),scene_plan(item,'review'), ' '.join(bad))

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
 return f'{key} ({reference.CROPS[key]})'if key else'none; neutral seedlings allowed, no named crop required'
def _crop_identity(a):
 key=_crop_key(a)
 return reference.CROP_VISUALS.get(key,f'{key} ({reference.CROPS[key]}) with botanically accurate leaves, stems, growth habit and harvest stage')if key else'neutral small seedlings; no species-specific crop requirement'
reference.named_crop=_named_crop
reference.crop_identity_spec=_crop_identity
