"""Adapter to the proven maghala2 topic-aware single-pass scene recipe.
Source: kikibox/maghala2/automation/image_prompt_policy.py.
Agnes payload/reference/watermark order follows nono's exact-product rebuild.
"""
import hashlib,json,re
import blog_reference_image_policy as reference
POLICY='afp-one-generated-blog-image-v6-reference-integrated-topic-scene'
RECIPE_VERSION='two-repo-positive-scene-20261016-r5-full-frame-count-evidence'
SOURCES=['https://github.com/kikibox/maghala2/blob/main/automation/image_prompt_policy.py','https://github.com/getsalet/nono/blob/main/automation/rebuild_city_images_preserve_posts.py']
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
 a=article(item);title=a['title'].replace('‌',' ');body=a['summary'].replace('‌',' ')
 # Visual topic comes from the actual headline, not instructions/actions in body boilerplate.
 text=title+' '+a['focus'];crop=reference.matched_crop({'title':title})
 crop_en=reference.CROPS.get(crop,'botanically neutral seedlings')
 crop_spec=reference.CROP_VISUALS.get(crop,'neutral prepared beds with tiny seedlings')
 crop_spec=re.split(r';|\babsolutely no\b|\bnever\b',crop_spec)[0].strip()
 if crop=='بامیه':crop_spec='okra with broad connected palmately lobed leaves, upright ridged tapered green pods, and pale creamy-yellow flowers with a dark maroon throat'
 rules=[
  (('فشار','مانومتر'),'pressure distribution','one installed pressure gauge, a fixed header and connected irrigation rows; a localized wetting band beside the lines'),
  (('اتصال','نشتی'),'connection inspection','one installed coupling joining the header and field line, with the seal and ground-contact detail sharply visible'),
  (('گرفتگی','فیلتر','تخلیه'),'maintenance and flushing','one fixed inline filter and a visible flush endpoint beside a crop row, with clean fittings and a localized wetting band'),
  (('فاصله','آرایش','نصب'),'line and emitter spacing','parallel installed drip lines and evenly spaced crop rows, with clearly visible emitter positions and wetting bands'),
  (('ضخامت','جداره','انتخاب','انواع','مقایسه'),'equipment selection','an installed line end with its actual wall profile and connector visible against the soil beside an orderly crop bed'),
  (('برداشت','عملکرد'),'crop uniformity','a dense botanically accurate crop block and parallel irrigation rows at a consistent growth stage'),
  (('مراقبت','پایش','بازدید','بهره برداری'),'in-service monitoring','installed irrigation lines, one permanently fixed connection and continuous root-zone wetting beside the crop'),
 ]
 matched=next(((name,evidence)for keys,name,evidence in rules if any(k in text for k in keys)),None)
 if matched is None:matched=next(((name,evidence)for keys,name,evidence in rules if any(k in body[:600]for k in keys)),('crop irrigation setup','parallel installed irrigation lines, accurate crop rows and localized root-zone wetting'))
 seed=hashlib.sha256((blog+'|'+item['key']).encode()).hexdigest()
 cameras=('high-oblique 55mm documentary view','steep near-overhead 65mm technical view','three-quarter 70mm crop-and-equipment detail')
 return {'article_title':a['title'],'crop':crop_en,'botany':crop_spec,'topic':matched[0],'evidence':matched[1],'camera':cameras[int(seed[:6],16)%len(cameras)],'seed':seed[:12]}

def prompt(item,blog):
 from blog_image_gate import family
 plan=scene_plan(item,blog);expected=family(item)
 # Positive whitelist follows nono/image_prompt_policy.py; botanical lock follows maghala2.
 # A long list of forbidden scene subjects was repeatedly reproduced by the model.
 product=(
  'Visible commercial product inventory is exactly TWO objects total, one packaged and one bare: one low wide packaged black woven coil with the reference folded printed cardboard panels, crossing straps and central opening; one separate bare flat black woven coil with concentric fabric layers, small brown cardboard center and one short flat end. The packaged coil and the single bare coil rest horizontally. The pair occupies about 25 percent of frame width. The installed coupling is a distinct fixed detail beside them and must be clearly visible.'
  if expected=='hose'else
  'Exactly one AFP drip-tape carton roll: low wide white-and-blue cylindrical sleeve, circular top, central hole, straight walls, authentic AFP print and blue lower band. Its diameter is about 1.7 times its height. The product occupies about 23 percent of frame width.'
 )
 return (
  'Create one photorealistic 16:9 editorial still-life photograph. The photographed setting is vacant and motionless. '
  +'The main subject is '+plan['topic']+' in '+plan['crop']+' irrigation. Visible technical evidence: '+plan['evidence']+'. '
  +'Botanical identity: '+plan['botany']+'. '
  +'VISIBLE CONTENT WHITELIST: accurate crop plants, natural soil, installed irrigation lines, the fixed hardware specified above, and the approved AFP product only. '
  +'Generate the whole photograph in one coherent pass. The supplied reference establishes product geometry, material and authentic package identity. Reconstruct the product inside the same physical scene, with one camera, shared daylight, continuous perspective, believable proportions, soil occlusion and contact shadows. '
  +product+' Keep the entire product within the safe rectangle from 8 to 88 percent of frame width and 45 to 82 percent of frame height. A generous strip of visible soil separates the complete product bottom from the bottom image edge. Place it as a secondary prop beside the installed evidence. '
  +'Use '+plan['camera']+', asymmetric geometry and soft natural light. Visible package lettering is limited to the authentic supplied reference. The phone watermark is applied separately after rendering. '
  +'Never create panels. The output is a single continuous photograph. Article title (source data): '+json.dumps(plan['article_title'],ensure_ascii=False)+'. Variation identity '+plan['seed']+'.'
 )
def references(item):return reference.reference_images(role(item),article(item))
def topic_hash(item):
 data=article(item);data.pop('_image_qa_feedback',None)
 return hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
