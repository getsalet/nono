import tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from automation.agri_v2 import multilingual as m
from automation.agri_v2.queue import atomic_json,load_json
from automation.agri_v2.pipeline import digest

def article():
 return {'title':'عنوان فارسی','excerpt':'توضیح فارسی برای بررسی ترجمه','content_html':'<h2>تیتر</h2><p>متن <a href="https://extension.msu.edu/source">منبع</a> <a href="https://navar-abyari.ir/fa-post/">مطلب فارسی</a></p><table><tr><td>داده</td></tr></table>','faq':[{'question':'سؤال','answer':'پاسخ'} for _ in range(3)]}
def response(a,lang='en-US'):
 _,values=m.source_segments(a)
 token={'en-US':'Faithful agricultural translation with preserved meaning. ','ru-RU':'Точный перевод сельскохозяйственного текста без новых фактов. ','tg-TJ':'Тарҷумаи дақиқи кишоварзӣ бо ҳифзи маъно ва маҳдудиятҳо. ','ar-IQ':'ترجمة زراعية دقيقة تحفظ المعنى والقيود دون معلومات جديدة. '}[lang]
 return {'translations':[{'id':i,'text':token*3} for i in range(len(values))]}
class MultilingualTests(unittest.TestCase):
 def test_all_four_languages_from_same_final_persian(self):
  a=article()
  for lang in m.LANGUAGES:
   row=m.render_translation(a,response(a,lang),lang)
   self.assertEqual(row['source_article_sha256'],digest(a));self.assertNotIn('/fa-post/',row['content_html']);self.assertIn('https://extension.msu.edu/source',row['content_html']);self.assertIn('<table>',row['content_html']);self.assertEqual(len(row['faq']),3)
 def test_numbers_cannot_change(self):
  a=article();a['title']='عنوان 20';r=response(a)
  with self.assertRaisesRegex(ValueError,'numbers'):m.render_translation(a,r,'en-US')
 def test_missing_duplicate_and_injected_ids_are_blocked(self):
  for kind in ('missing','duplicate','html'):
   a=article();r=response(a)
   if kind=='missing':r['translations'].pop()
   if kind=='duplicate':r['translations'][-1]['id']=0
   if kind=='html':r['translations'][0]['text']='<script>bad</script>'
   with self.assertRaises(ValueError):m.render_translation(a,r,'en-US')
 def test_tajik_is_cyrillic_not_persian(self):
  a=article()
  with self.assertRaises(ValueError):m.render_translation(a,response(a,'ar-IQ'),'tg-TJ')
 def test_shared_images_and_localized_links_only(self):
  a=article();row=m.render_translation(a,response(a),'en-US');media=[{'id':11,'url':'https://navar-abyari.ir/uploads/image1.webp'},{'id':12,'url':'https://navar-abyari.ir/uploads/image2.webp'}]
  policy={'en-US':[{'anchor':'drip tape','url':'https://navar-abyari.ir/en/'}]}
  fetch=lambda u:(u,'<html lang="en-US">',200)
  body=m.localized_body(row,media,policy,fetch)
  self.assertIn(media[1]['url'],body);self.assertNotIn(media[0]['url'],body);self.assertIn('href="https://navar-abyari.ir/en/"',body);self.assertNotIn('/fa-post/',body)
 def test_cross_language_redirect_or_lang_never_allowed(self):
  for fetch in (lambda u:('https://navar-abyari.ir/','<html lang="fa-IR">',200),lambda u:(u,'<html lang="fa-IR">',200)):
   with self.assertRaises(ValueError):m.verify_target('https://navar-abyari.ir/en/','en-US',fetch)
 def test_missing_bridge_never_posts_or_uploads_media(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';folder=Path(d)/'out';atomic_json(data/'config.json',{'multilingual':{'enabled':True}})
   wp=Mock();wp.call.return_value=({'schema':{'properties':{}}},{})
   with patch.object(m,'DATA',data):r=m.publish_family(wp,folder,{}, {'post_id':123})
   self.assertEqual(r['translations_status'],'pending_wordpress_language_bridge');wp.call.assert_called_once_with('posts',method='OPTIONS')
 def test_completed_translation_reuses_bytes_without_paid_call(self):
  with tempfile.TemporaryDirectory() as d:
   a=article();folder=Path(d);atomic_json(folder/'translations'/'en-US.json',m.render_translation(a,response(a),'en-US'));client=Mock()
   m.translate_one(a,'en-US',folder,{},client);client.assert_not_called()
 def test_translation_calls_do_not_rotate_after_failure(self):
  client=object.__new__(m.TranslationClient)
  with patch.object(m.ModelClient,'request',return_value={}) as request:
   client.request('text','/chat/completions',{},120)
   self.assertEqual(request.call_args.kwargs['attempts'],1)
 def test_translation_failure_reservation_is_not_reset(self):
  with tempfile.TemporaryDirectory() as d:
   a=article();folder=Path(d);factory=Mock();factory.return_value.text.side_effect=RuntimeError('provider')
   for _ in range(2):
    with self.assertRaises(Exception):m.translate_one(a,'en-US',folder,{},factory)
   factory.assert_called_once()
 def test_translations_overlap_with_maximum_two_workers(self):
  import threading
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';folder=Path(d)/'out';atomic_json(data/'config.json',{'multilingual':{'enabled':True}});barrier=threading.Barrier(2);calls=[]
   def translated(a,lang,*rest):calls.append(lang);barrier.wait(timeout=3);return {}
   with patch.object(m,'DATA',data),patch.object(m,'translate_one',side_effect=translated):
    job=m.start(article(),folder,{});self.assertIsNotNone(job);m.finish(job,folder)
   self.assertEqual(set(calls),set(m.LANGUAGES));self.assertEqual(set(load_json(folder/'translations/status.json')['languages'].values()),{'validated'})

class FamilyPublishingTests(unittest.TestCase):
 def test_four_posts_reuse_two_media_and_reconcile_without_duplicates(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';folder=Path(d)/'out';a=article();media=[{'index':1,'id':11,'url':'https://navar-abyari.ir/uploads/a.webp'},{'index':2,'id':12,'url':'https://navar-abyari.ir/uploads/b.webp'}]
   atomic_json(data/'config.json',{'multilingual':{'enabled':True}});atomic_json(data/'internal-links.json',{'related':[]})
   atomic_json(data/'internal-links-i18n.json',{'languages':{lang:[{'anchor':'equipment','url':'https://navar-abyari.ir/'+lang+'/'}] for lang in m.LANGUAGES}})
   atomic_json(folder/'article.json',a);atomic_json(folder/'wordpress-draft-payload.json',{'slug':'source-post'});atomic_json(folder/'wordpress-receipt.json',{'media':media})
   for lang in m.LANGUAGES:atomic_json(folder/'translations'/f'{lang}.json',m.render_translation(a,response(a,lang),lang))
   class WP:
    user_id=7
    def __init__(self):self.posts={};self.requests=[]
    def call(self,path,method='GET',data=None):
     self.requests.append((path,method,data))
     if method=='OPTIONS':return {'schema':{'properties':{'afp_language':{},'afp_source_post_id':{}}}},{}
     if path.startswith('posts?'):
      import urllib.parse
      q=urllib.parse.parse_qs(urllib.parse.urlsplit(path).query)
      return [p for p in self.posts.values() if p['slug']==q['slug'][0] and p['status']==q['status'][0]],{}
     if path=='posts':
      ident=100+len(self.posts);p=dict(data,id=ident,author=7,title={'rendered':data['title']},content={'raw':data['content'],'rendered':data['content']},link='https://navar-abyari.ir/'+data['slug']+'/');self.posts[ident]=p;return p,{}
     ident=int(path.split('/')[1].split('?')[0]);p=self.posts[ident]
     if method=='POST':p.update(data)
     return p,{}
   wp=WP()
   with patch.object(m,'DATA',data),patch.object(m,'verify_target',return_value=True):
    for _ in range(2):result=m.publish_family(wp,folder,{'id':'agri-fixture'},{'post_id':500})
   self.assertEqual(len(wp.posts),4);self.assertEqual(len(result['translations']),4)
   self.assertFalse(any(path.startswith('media') for path,method,data in wp.requests))
   self.assertEqual({p['featured_media'] for p in wp.posts.values()},{11})
   for post in wp.posts.values():self.assertEqual(post['status'],'publish');self.assertEqual(post['afp_source_post_id'],500);self.assertEqual(post['content']['rendered'].count(media[1]['url']),1)
