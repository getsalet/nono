"""Adapter to the proven maghala2 topic-aware single-pass scene recipe.
Source: kikibox/maghala2/automation/image_prompt_policy.py.
Agnes payload/reference/watermark order follows nono's exact-product rebuild.
"""
import hashlib,json,re
import blog_reference_image_policy as reference
POLICY='afp-one-generated-blog-image-v6-reference-integrated-topic-scene'
RECIPE_VERSION='maghala2-exact-recipe-image-connection-parity-v1'
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
 a=article(item);kind=role(item)
 return {'article_title':a['title'],'role':kind,'crop':reference.named_crop(a),'botany':reference.crop_identity_spec(a),'visual_brief':reference.visual_brief(a),'evidence':reference.topic_visual_anchor(a),'visual_template':reference.visual_template(a,kind),'recipe':'maghala2/image_prompt_policy.py'}

def prompt(item,blog):
 # Use the actual upstream function, including title, summary, topic anchors,
 # role, scale, botany and QA correction. Never replace it with a homemade scene.
 a=article(item);a['slug']=str(a['slug'])+'-'+blog
 return reference.image_prompt(a,role(item))
def references(item):return reference.reference_images(role(item),article(item))
def topic_hash(item):
 data=article(item);data.pop('_image_qa_feedback',None)
 return hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
