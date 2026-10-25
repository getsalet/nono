"""Complete one already published Persian family; zero media/model-image operations."""
from .queue import DATA,OUT,load_json,get_topic,atomic_json,utcnow
from .multilingual import start,finish,publish_family,LANGUAGES
from .progress import update
from .runtime_health import ensure_fresh
from .wordpress import WordPress
TOPIC='agri-a4f1fee1e3ee'
def run(req):
 if req.get('multilingual_source_topic')!=TOPIC or req.get('max_translation_calls')!=4 or req.get('max_new_source_posts')!=0 or req.get('max_new_image_calls')!=0:raise ValueError('Exact existing-source four-translation request required')
 from .safe_activation import authorized
 if not authorized(DATA):raise ValueError('Owner activation required')
 if ensure_fresh()['status'] not in {'health_current','health_refreshed_from_actual_evidence'}:raise ValueError('Current health required')
 folder=OUT/'new'/TOPIC;receipt=load_json(folder/'wordpress-receipt.json')
 if receipt.get('post_id')!=524170 or receipt.get('public_verified') is not True:raise ValueError('Exact public Persian source required')
 wp=WordPress();wp.preflight();schema,_=wp.call('posts',method='OPTIONS')
 if not {'afp_language','afp_source_post_id'}<=schema.get('schema',{}).get('properties',{}).keys():raise ValueError('Language bridge not installed')
 source,_=wp.call('posts/524170')
 if source.get('status')!='publish' or source.get('afp_language')!='fa-IR':raise ValueError('Persian source no longer public')
 topic=get_topic('new',TOPIC)
 update('ترجمهٔ چهار زبان از فارسی؛ دو تصویر مشترک و بدون ساخت تصویر تازه',20,TOPIC,topic['title'])
 finish(start(load_json(folder/'article.json'),folder,load_json(DATA/'health/latest.json')),folder)
 result=publish_family(wp,folder,topic,receipt)
 state=load_json(folder/'translations/publication-status.json')
 if state.get('status')=='complete':update('چهار ترجمه با تصاویر مشترک و لینک‌های هم‌زبان منتشر و تأیید شد',100,TOPIC,topic['title'],status='success')
 else:update('ترجمه‌های موجود پردازش شدند؛ وضعیت هر زبان در رسید ثبت است',70,TOPIC,topic['title'],status='awaiting_review')
 return result
