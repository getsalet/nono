import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import parsiblog_matrix as matrix
import parsiblog_policy as policy
import parsiblog_native as native
from parsiblog_links import render_contextual_links
from bs4 import BeautifulSoup
import parsiblog_pipeline as pipeline
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.inventory=matrix.build();cls.item=copy.deepcopy(next(x for x in cls.inventory['items']if not x['evidence']));cls.item['image_url']='https://navar-abyari.ir/wp-content/uploads/afp-drip-tape-roll-transparent.webp'
 def setUp(self):
  mock=patch('parsiblog_images.validate_record',return_value=[]);mock.start();self.addCleanup(mock.stop)
 def fixture(self):
  item=copy.deepcopy(self.item);links=policy.links_for(item)
  para='<p>'+('بررسی مشخصات محصول پیش از سفارش و ثبت اطلاعات زمین برای انتخاب آگاهانه ضروری است. '*43)+'</p>'
  body='<p><img src="'+item['image_url']+'" alt="نمای محصول آبیاری AFP"></p><h2>ثبت نیاز زمین</h2>'+para+'<h2>انتخاب مشخصات</h2><ul><li>ثبت نیاز واقعی زمین</li></ul><h2>جمع‌بندی</h2>'
  for x in links:body+='<p>برای بررسی دقیق‌تر <a href="'+x['url']+'">'+x['anchor']+'</a> را بخوانید.</p>'
  body+='<h2>پرسش‌های متداول</h2>'+''.join('<h3>چه اطلاعاتی لازم است؟</h3><p>نیاز زمین و مشخصات همان مدل باید بررسی شود.</p>'for _ in range(3))
  post={'title':item['assigned_title'],'slug':'parsiblog-city-choice','meta_description':'راهنمای انتخاب تجهیزات آبیاری و بررسی مشخصات محصول با توجه به اطلاعات واقعی زمین، پرسش‌های فنی و نکات ضروری پیش از ثبت سفارش.','tags':['آبیاری','راهنمای انتخاب'],'html':body};item['editorial_review']={'policy':'parsiblog-evidence-review-v2','passed':True,'post_sha256':policy.post_digest(post)};return item,post
 def text_fixture(self):
  x,p=self.fixture();soup=BeautifulSoup(p['html'],'html.parser')
  for image in soup.find_all('img'):image.parent.decompose()
  p['html']=str(soup);return x,p
 def test_renderer_fills_missing_home_link(self):
  x,p=self.text_fixture();soup=BeautifulSoup(p['html'],'html.parser');soup.find('a',href=policy.links_for(x)[0]['url']).unwrap();p['html']=str(soup)
  e,r=render_contextual_links(x,p);self.assertEqual(e,[]);self.assertEqual(r['link_count'],3);self.assertEqual(policy.qa(x,p,require_image=False,originality=False)[0],[])
 def test_renderer_owns_all_three_links_without_model_anchors(self):
  x,p=self.text_fixture();soup=BeautifulSoup(p['html'],'html.parser')
  for a in soup.find_all('a'):a.unwrap()
  p['html']=str(soup);e,r=render_contextual_links(x,p);self.assertEqual(e,[]);self.assertEqual(r['link_count'],3);self.assertEqual(len({v['paragraph_index']for v in r['placements']}),3)
  self.assertEqual(policy.qa(x,p,require_image=False,originality=False)[0],[])
 def test_renderer_fallback_when_anchor_phrases_absent(self):
  x,p=self.text_fixture();soup=BeautifulSoup(p['html'],'html.parser')
  for a in soup.find_all('a'):a.replace_with('مشخصات محصول')
  p['html']=str(soup);e,r=render_contextual_links(x,p);self.assertEqual(e,[]);self.assertTrue(all(z['placement']=='contextual reading sentence'for z in r['placements']));self.assertEqual(policy.qa(x,p,require_image=False,originality=False)[0],[])
 def test_renderer_idempotent(self):
  x,p=self.text_fixture();self.assertEqual(render_contextual_links(x,p)[0],[]);before=p['html'];self.assertEqual(render_contextual_links(x,p)[0],[]);self.assertEqual(before,p['html'])
 def test_renderer_does_not_hide_unknown_destination(self):
  x,p=self.text_fixture();p['html']+='<p><a href="https://example.invalid/">لینک نامعتبر</a></p>';self.assertTrue(render_contextual_links(x,p)[0]);self.assertIn('https://example.invalid/',p['html'])
 def test_renderer_deduplicates_only_approved_destinations(self):
  x,p=self.text_fixture();p['html']=p['html'].replace('<h2>جمع‌بندی</h2>','<p><a href="'+policy.links_for(x)[0]['url']+'">راهنمای بیشتر</a></p><h2>جمع‌بندی</h2>');self.assertEqual(render_contextual_links(x,p)[0],[]);self.assertEqual(policy.qa(x,p,require_image=False,originality=False)[0],[])
 def test_renderer_never_links_in_faq(self):
  x,p=self.text_fixture();self.assertEqual(render_contextual_links(x,p)[0],[]);faq=p['html'].split('<h2>پرسش‌های متداول</h2>')[1];self.assertNotIn('<a ',faq)
 def test_renderer_requires_real_body(self):
  self.assertTrue(render_contextual_links(self.item,{'html':'<h2>پرسش‌های متداول</h2><p>پاسخ</p>'})[0])
 def test_invalid_model_json_is_a_repairable_error(self):
  for p in (None,[],{}, {'title':[],'html':None}):self.assertTrue(policy.qa(self.item,p,require_image=False,originality=False)[0])
 def test_explicit_preflight_recovery_preserves_audit(self):
  s={'items':{'k':{'status':'failed','reason':'Text SEO preflight rejected: missing link'}},'published':[]};self.assertTrue(pipeline.recover_explicit_preflight(s,'k',True));self.assertNotIn('k',s['items']);self.assertEqual(len(s['reviewed_pre_submit_failures']),1)
 def test_recovery_never_resets_ambiguous_or_published_state(self):
  for status in ('submitting_publish','submitting_draft','published'):
   s={'items':{'k':{'status':status,'id':'42'}}};self.assertFalse(pipeline.recover_explicit_preflight(s,'k',True));self.assertEqual(s['items']['k']['status'],status)
  with self.assertRaises(RuntimeError):pipeline.recover_explicit_preflight({'items':{'k':{'status':'failed','id':'42','reason':'Text SEO preflight rejected: x'}}},'k',True)
 def test_fresh_run_report_is_not_prior_receipt(self):
  import tempfile
  with tempfile.TemporaryDirectory()as d,patch.object(pipeline,'ART',Path(d)):
   pipeline.RUN.clear();pipeline.run_report(run_id='new-run',status='failed',native_write_attempted=False)
   r=json.loads((Path(d)/'run-report.json').read_text());self.assertEqual(r['run_id'],'new-run');self.assertEqual(r['status'],'failed');self.assertNotIn('receipt',r)
 def test_public_read_retry_never_repeats_native_write(self):
  with patch.object(native,'_verify_public_once',side_effect=[native.NativeError('not visible yet'),'http://afp.parsiblog.com/Posts/2/'])as read,patch.object(native.time,'sleep'),patch.object(native,'save_post')as write:
   self.assertEqual(native.verify_public(None,{},'42'),'http://afp.parsiblog.com/Posts/2/');self.assertEqual(read.call_count,2);write.assert_not_called()
 def test_public_read_retry_is_bounded(self):
  with patch.object(native,'_verify_public_once',side_effect=native.NativeError('not visible'))as read,patch.object(native.time,'sleep')as wait,self.assertRaises(native.NativeError):native.verify_public(None,{},'42')
  self.assertEqual(read.call_count,5);self.assertEqual([x.args[0]for x in wait.call_args_list],[5,15,30,60])
 def test_inventory(self):
  rows=self.inventory['items'];self.assertEqual(len(rows),1000);self.assertEqual(len({x['assigned_title']for x in rows}),1000);self.assertTrue(all(12<=len(x['assigned_title'])<=65 for x in rows));self.assertEqual(self.inventory['crop_title_count'],8)
  self.assertTrue(all(not policy.title_errors(x,x['assigned_title'],matrix.ROOT)for x in rows))
 def test_three_links_and_native_faq(self):
  x,p=self.fixture();e,r=policy.qa(x,p,originality=False);self.assertEqual(e,[]);self.assertEqual(r['link_count'],3)
 def test_link_tokens_resolve_before_strict_qa(self):
  x,p=self.fixture()
  for i,link in enumerate(policy.links_for(x),1):p['html']=p['html'].replace('href="'+link['url']+'"','href="AFP_LINK_'+str(i)+'"')
  self.assertEqual(policy.qa(x,p,originality=False)[0],[])
 def test_hash_link_tokens_resolve(self):
  x,p=self.fixture()
  for i,link in enumerate(policy.links_for(x),1):p['html']=p['html'].replace('href="'+link['url']+'"','href="#AFP_LINK_'+str(i)+'"')
  self.assertEqual(policy.qa(x,p,originality=False)[0],[])
 def test_factual_prescriptions_rejected(self):
  for claim in ('ضخامت ۲۰۰ میکرون مناسب است','نوار را 2 سانتی متر بالای خاک بگذارید','شستشو با اسید ملایم','خاک لومی و رسی','یکی از مناطق مهم کشت است','نوار فاقد قطره چکان است','دشت این شهرستان دارای شوری بالا است'):
   self.assertTrue(policy.factual_errors(claim),claim)
 def test_irrigation_word_is_not_a_local_water_assertion(self):
  self.assertEqual(policy.factual_errors('انتخاب نوار آبیاری مناسب برای زمین‌های کشت سیر در شهرستان هوراند، نیازمند یک فرایند تصمیم‌گیری ساختاریافته است.'),[])
  self.assertTrue(policy.factual_errors('آب این شهرستان دارای شوری بالا است.'))
  self.assertTrue(policy.factual_errors('خاک این شهرستان دارای سختی بالا است.'))
 def test_conditional_checklist_not_fabricated_local_fact(self):
  self.assertEqual(policy.factual_errors('پیش از انتخاب محصول برای این شهرستان باید کیفیت آب و خاک همان زمین بررسی شود. برگه فنی همان مدل را بخوانید.'),[])
 def test_current_editorial_review_bound_to_body(self):
  x,p=self.fixture();self.assertEqual(policy.review_errors(x,p),[]);p['html']+='<p>تغییر متن</p>';self.assertTrue(policy.review_errors(x,p))
 def test_unknown_hash_token_rejected(self):
  x,p=self.fixture();p['html']=p['html'].replace(policy.links_for(x)[0]['url'],'#AFP_LINK_4');self.assertTrue(policy.qa(x,p,originality=False)[0])
 def test_empty_hash_exact_assigned_anchors_only(self):
  x,p=self.fixture()
  for link in policy.links_for(x):p['html']=p['html'].replace('href="'+link['url']+'"','href="#"')
  self.assertEqual(policy.qa(x,p,originality=False)[0],[])
  p['html']+='<p><a href="#">نشانی ناشناخته</a></p>'
  self.assertTrue(policy.qa(x,p,originality=False)[0])
 def test_mixed_language_rejected(self):
  for claim in ('بررسی que محصول','با对照 اطلاعات زمین'):
   self.assertTrue(policy.factual_errors(claim))
 def test_document_availability_not_invented(self):
  self.assertTrue(policy.factual_errors('برگه فنی هر محصول در صفحه همان مدل منتشر می شود و قابل مشاهده و دانلود است'))
  self.assertEqual(policy.factual_errors('برگه فنی همان مدل را از تولیدکننده درخواست کنید'),[])
 def test_review_calibrates_checklists_not_local_soil_assertions(self):
  x,p=self.fixture();brief=policy.review_prompt(x,p)
  self.assertIn('جمع‌آوری داده است',brief);self.assertIn('خاک این شهرستان رسی است',brief)
 def test_unknown_link_token_rejected(self):
  x,p=self.fixture();p['html']=p['html'].replace(policy.links_for(x)[0]['url'],'AFP_LINK_4');self.assertTrue(policy.qa(x,p,originality=False)[0])
 def test_fourth_link_rejected(self):
  x,p=self.fixture();p['html']+='<p><a href="https://navar-abyari.ir/shop/">فروشگاه</a></p>';self.assertTrue(policy.qa(x,p,originality=False)[0])
 def test_links_in_faq_rejected(self):
  x,p=self.fixture();p['html']=p['html'].replace('<h3>چه اطلاعاتی لازم است؟','<a href="https://navar-abyari.ir/">پیوند</a><h3>چه اطلاعاتی لازم است؟',1);self.assertTrue(policy.qa(x,p,originality=False)[0])
 def test_stripped_faq_format_rejected(self):
  x,p=self.fixture();p['html']=p['html'].replace('<h3>چه اطلاعاتی لازم است؟</h3>','<details><summary>پرسش</summary></details>',1);self.assertTrue(policy.qa(x,p,originality=False)[0])
 def test_readback_changed_text_rejected(self):
  x,p=self.fixture();self.assertEqual(native.persisted_errors(x,p,p),[]);q=copy.deepcopy(p);q['html']=q['html'].replace('اطلاعات واقعی زمین','متن عوض شده');q['html']+='<p>بخش تازه</p>';self.assertTrue(native.persisted_errors(x,p,q))
 def test_native_title_only_known_zwnj_normalization(self):
  self.assertTrue(native.title_matches('گوجه‌فرنگی در شهرستان ارومیه','گوجهفرنگي در شهرستان اروميه'))
  self.assertTrue(native.title_matches('گوجه‌فرنگی در شهرستان ارومیه','گوجه فرنگی در شهرستان ارومیه'))
  self.assertFalse(native.title_matches('گوجه‌فرنگی در شهرستان ارومیه','گوجهفرنگی در شهرستان دیگری'))
 def test_readback_only_observed_fullwidth_comma_canonicalization(self):
  x,p=self.fixture();p['html']=p['html'].replace('بررسی مشخصات','بررسی، مشخصات，',1);actual=copy.deepcopy(p);actual['html']=actual['html'].replace('，',',')
  self.assertEqual(native.persisted_errors(x,p,actual),[])
  actual['html']=actual['html'].replace('بررسی، مشخصات','حذف مشخصات',1);self.assertTrue(native.persisted_errors(x,p,actual))
 def test_readback_digit_glyphs_preserve_values(self):
  x,p=self.fixture();p['html']+='<table><tr><td>۱</td><td>۲</td><td>۳</td></tr></table><p>مدل ۲۰، مقدار ۱٫۵ و شناسه ۰۰۷</p>'
  actual=copy.deepcopy(p);actual['html']=actual['html'].translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹','0123456789'))
  self.assertEqual(native.persisted_errors(x,p,actual),[])
  self.assertEqual(native.normalized_body('۰۱۲۳۴۵۶۷۸۹'),'0123456789')
 def test_readback_numeric_value_change_still_rejected(self):
  x,p=self.fixture();p['html']+='<p>ردیف ۱۲، مقدار ۱٫۵</p>'
  for changed in ('ردیف 13، مقدار 1٫5','ردیف 12، مقدار 15','ردیف 12، مقدار 1.5','ردیف ، مقدار 1٫5'):
   actual=copy.deepcopy(p);actual['html']=actual['html'].replace('ردیف ۱۲، مقدار ۱٫۵',changed)
   self.assertIn('Saved article text differs from approved draft',native.persisted_errors(x,p,actual))
 def test_readback_digit_normalization_does_not_change_destinations(self):
  x,p=self.fixture();p['html']=p['html'].replace(x['image_url'],x['image_url']+'?id=۱۲');x['image_url']+='?id=۱۲'
  actual=copy.deepcopy(p);actual['html']=actual['html'].replace('?id=۱۲','?id=12')
  self.assertIn('Saved image missing or changed',native.persisted_errors(x,p,actual))
 def test_readback_normalizes_letters(self):
  x,p=self.fixture();q=copy.deepcopy(p);q['html']=q['html'].replace('ی','ي').replace('ک','ك');q['title']=q['title'].replace('ی','ي');self.assertEqual(native.persisted_errors(x,p,q),[])
 def test_budget(self):
  self.assertEqual(pipeline.budget({'published':[]}),2);self.assertEqual(pipeline.budget({'published':[{'at':pipeline.stamp()}]}),1);self.assertEqual(pipeline.budget({'published':[{'at':pipeline.stamp()},{'at':pipeline.stamp()}]}),0)
 def test_missing_image_review_rejected(self):
  x,p=self.fixture()
  with patch('parsiblog_images.validate_record',return_value=['Current family-aware image review missing']):self.assertTrue(policy.qa(x,p,originality=False)[0])
 def test_unverified_crop_body_rejected(self):
  x,p=self.fixture();p['html']=p['html'].replace('<h2>ثبت نیاز زمین</h2>','<h2>ثبت نیاز زمین</h2><p>کشت '+json.loads((matrix.ROOT/'data/blog-city-title-matrix.json').read_text())['row_crops'][0]+' در این شهر</p>');self.assertTrue(policy.qa(x,p,originality=False)[0])
 def test_canary_seed_not_automatically_approved(self):
  seed=json.loads((matrix.ROOT/'data/parsiblog/canary-seed.json').read_text());self.assertFalse(seed['approved']);self.assertTrue(seed['requires_full_qa_and_editorial_review']);self.assertTrue(policy.review_errors({},seed['post']))
 def test_native_editor_opens_post_view_before_initialization(self):
  class StopBeforeAnyWrite(Exception):pass
  class P:
   url=native.NOTES
   def goto(self,url,**kw):self.url=url
   def wait_for_function(self,*a,**kw):
    if self.url!=native.NOTES+'?Post':raise AssertionError('Editor was not opened')
    raise StopBeforeAnyWrite()
  page=P()
  with patch.object(native,'guard'),self.assertRaises(StopBeforeAnyWrite):native.save_post(page,{},pid='8027686')
  self.assertEqual(page.url,native.NOTES+'?Post')
 def test_public_local_id_is_not_native_database_id(self):
  item,post=self.fixture();item['post']=post
  class Title:
   def count(self):return 1
   def inner_text(self):return post['title']
  class Card:
   def locator(self,selector):
    if selector!='.post-title':raise AssertionError('Guessed native ID used for public selector')
    return Title()
  class Cards:
   def count(self):return 1
   def nth(self,i):return Card()
  class Page:
   def locator(self,selector):
    if selector!='.post-card':raise AssertionError('Guessed native ID used for public selector')
    return Cards()
  self.assertIsInstance(native.find_public_article(Page(),item),Card)
 def test_account_guard(self):
  class P:
   url='http://www.parsiblog.com/Notes.aspx'
   def wait_for_selector(self,*a,**k):pass
   def evaluate(self,*a,**k):return 'someoneelse'
  with self.assertRaises(native.NativeError):native.guard(P())
 def test_native_readback_parse(self):
  class P:
   def evaluate(self,*a):return 'native-edit-payload'
  with patch.object(native,'guard'),patch.object(native,'native_request',return_value='OK$#PBFalse$#PBعنوان$#PB<p>متن</p>$#PB12$#PBFalse$#PBTrue$#PBSub=آبیاری'):
   actual=native.read_post(P(),'12');self.assertEqual(actual['id'],'12');self.assertFalse(actual['published']);self.assertEqual(actual['title'],'عنوان')
class RealPhotoTests(unittest.TestCase):
 def setUp(self):
  import tempfile,hashlib
  import parsiblog_images as images
  self.images=images;self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  (self.root/'data').mkdir();(self.root/'data/blog-generated-image-control.json').write_text(json.dumps({'pause_image_production':False,'enabled_families':['tape20'],'cancelled_families':['hose']}))
  self.raw=b'actual-verified-image-fixture';self.item={'family':'tape20','key':'pb-test'}
  self.good={'pass':True,'score':96,'observed_family':'tape20',**{k:True for k in images.TRUE_FLAGS},**{k:False for k in images.FALSE_FLAGS}}
  m=patch.object(images.shared,'fetch',return_value=(self.raw,(386,382),'WEBP'));m.start();self.addCleanup(m.stop)
 def prepare(self):
  with patch.object(self.images,'vision',return_value=(self.good,self.images.common.BASE.AGNES_MODEL))as review:
   self.item['image_url']=self.images.prepare_image(self.item,self.root)
  return review
 def test_real_photo_requires_actual_scoped_vision(self):
  review=self.prepare();review.assert_called_once();self.assertEqual(self.images.validate_record(self.item,self.root),[])
  self.assertEqual(self.item['image_review']['scope'],'real-product-photo')
 def test_real_photo_rejects_unknown_or_low_scores(self):
  for score in (True,89,101,float('nan'),'95',None):
   v=dict(self.good,score=score);self.assertTrue(self.images.verdict_errors(v,'tape20'))
 def test_real_photo_rejects_every_missing_safety_flag(self):
  for flag in self.images.TRUE_FLAGS+self.images.FALSE_FLAGS:
   v=dict(self.good);del v[flag];self.assertTrue(self.images.verdict_errors(v,'tape20'),flag)
  self.assertTrue(self.images.verdict_errors(dict(self.good,observed_family='hose'),'tape20'))
 def test_shared_rejected_cache_never_counts_as_scoped_approval(self):
  (self.root/'artifacts/blog-image-reviews').mkdir(parents=True);(self.root/'artifacts/blog-image-reviews/old.json').write_text(json.dumps({'pass':True}))
  self.prepare().assert_called_once()
 def test_real_photo_changed_bytes_invalidates_approval(self):
  self.prepare()
  with patch.object(self.images.shared,'fetch',return_value=(b'changed-image',(386,382),'WEBP')):self.assertTrue(self.images.validate_record(self.item,self.root))
 def test_real_photo_persisted_verdict_required(self):
  self.prepare();record=self.item['image_review'];record['scope']='generated-field-scene';self.assertTrue(self.images.validate_record(self.item,self.root))
 def test_real_photo_manual_rejection_blocks_cached_approval(self):
  self.prepare()
  with patch.object(self.images.shared,'visual_override_rejected',return_value=True):
   self.assertTrue(self.images.validate_record(self.item,self.root))
   with self.assertRaises(RuntimeError):self.images.prepare_image(self.item,self.root)
 def test_global_stop_and_held_family_block_before_network(self):
  with patch.object(self.images.shared,'fetch')as network:
   for item in ({'family':'hose'},):
    with self.assertRaises(RuntimeError):self.images.prepare_image(item,self.root)
   (self.root/'data/blog-generated-image-control.json').write_text(json.dumps({'pause_image_production':True,'enabled_families':['tape20']}))
   with self.assertRaises(RuntimeError):self.images.prepare_image(self.item,self.root)
   network.assert_not_called()
 def test_no_approval_from_url_or_filename(self):
  with patch.object(self.images,'vision',return_value=(dict(self.good,**{'pass':False}),self.images.common.BASE.AGNES_MODEL))as vision:
   with self.assertRaises(RuntimeError):self.images.prepare_image(self.item,self.root)
   vision.assert_called_once()
 def test_timestamp_bound_report_permits_explicit_prewrite_recovery(self):
  at='2026-10-21T01:28:15.014888Z';state={'items':{'k':{'status':'failed','at':at,'reason':'RuntimeError'}}}
  report={'key':'k','status':'failed','native_write_attempted':False,'started_at':'2026-10-21T01:25:31Z','completed_at':'2026-10-21T01:28:15.014912Z'}
  self.assertTrue(pipeline.recover_explicit_preflight(state,'k',True,report))
 def test_unrelated_report_cannot_reset_generic_failure(self):
  for extra in ({'key':'other'},{'native_write_attempted':True},{'completed_at':'2026-10-21T03:00:00Z'},{'completed_at':'bad'}):
   state={'items':{'k':{'status':'failed','at':'2026-10-21T01:28:15Z','reason':'RuntimeError'}}};r=dict(key='k',status='failed',native_write_attempted=False,started_at='2026-10-21T01:25:31Z',completed_at='2026-10-21T01:28:15Z');r.update(extra)
   with self.assertRaises(RuntimeError):pipeline.recover_explicit_preflight(state,'k',True,r)
class UnicodeAndRepairTests(unittest.TestCase):
 def test_foreign_scripts_and_single_letters_rejected(self):
  from parsiblog_text import language_errors
  for token in ('для','α','対照','偏离','X','tape20','hose','AFPfoo','الفБ'):
   self.assertTrue(language_errors('مدل '+token+' برای زمین'),token)
 def test_persian_text_and_afp_mark_allowed(self):
  from parsiblog_text import language_errors
  self.assertEqual(language_errors('مدل نوار تیپ AFP برای زمین؛ بررسی کیفیت آب و خاک.'),[])
 def test_replacement_character_corruption_rejected(self):
  from parsiblog_text import language_errors
  for text in ('مدل ??? برای زمین','مدل � زمین'):self.assertTrue(language_errors(text))
 def test_slug_and_hrefs_not_misclassified_as_visible_prose(self):
  from parsiblog_text import post_language_errors
  p={'title':'عنوان فارسی','slug':'navar-tip-city','meta_description':'توضیح فارسی','tags':['آبیاری'],'html':'<p><a href="https://example.com/tape20/">نوار تیپ AFP</a></p>'}
  self.assertEqual(post_language_errors(p),[])
  for field in ('title','meta_description','tags','html'):
   q=copy.deepcopy(p);q[field]=['для']if field=='tags'else'برای برای для';self.assertTrue(post_language_errors(q),field)
 def test_model_source_has_no_internal_family_code(self):
  from parsiblog_text import source_context
  x=source_context({'family':'tape20','city_fa':'بابکان'});text=json.dumps(x,ensure_ascii=False)
  self.assertNotIn('tape20',text);self.assertNotIn('locality_label',text);self.assertIn('نوار آبیاری قطره‌ای',text)
 def repair_fixture(self):
  import parsiblog_repair as r
  fixture=Tests();fixture.item=Tests.item;item,post=fixture.fixture();item.update(key='pb-guard-fixture',post=post);post['html']=post['html'].replace('بررسی مشخصات','بررسی مشخصات для',1)
  actual={'id':'42','published':True,'title':post['title'],'html':post['html'].replace('для','???',1)};target=copy.deepcopy(post);target['html']=target['html'].replace('для','برای',1)
  m={'policy':r.POLICY,'authorized':True,'key':item['key'],'native_id':'42','source_post_sha256':policy.post_digest(post),'observed_native_sha256':r.snapshot_digest(actual),'target_post_sha256':policy.post_digest(target),'old_text':'для','new_text':'برای'}
  state={'id':'42','status':'submitting_publish','native_phase':'acknowledged'};return r,item,state,actual,m
 def test_repair_requires_exact_remote_snapshot_and_same_id(self):
  r,item,state,actual,m=self.repair_fixture();candidate,write=r.repair_candidate(item,state,actual,m)
  self.assertTrue(write);self.assertIn('برای',candidate['post']['html']);self.assertNotIn('для',candidate['post']['html']);self.assertIn('для',item['post']['html'])
 def test_repair_never_overwrites_unknown_remote_changes(self):
  r,item,state,actual,m=self.repair_fixture()
  for change in ({'id':'99'},{'published':False},{'title':'عنوان عوض شده'},{'html':actual['html']+'<p>تغییر تازه</p>'}):
   q=dict(actual,**change)
   with self.assertRaises(native.NativeError):r.repair_candidate(item,state,q,m)
 def test_repair_never_accepts_changed_local_or_target_digest(self):
  r,item,state,actual,m=self.repair_fixture()
  for change in ({'authorized':False},{'target_post_sha256':'bad'},{'source_post_sha256':'bad'},{'native_id':'43'},{'key':'other'}):
   with self.assertRaises(native.NativeError):r.repair_candidate(item,state,actual,dict(m,**change))
 def test_completed_repair_reconciles_without_second_write(self):
  r,item,state,actual,m=self.repair_fixture();candidate,_=r.repair_candidate(item,state,actual,m);actual['html']=candidate['post']['html'];state['status']='published'
  same,write=r.repair_candidate(candidate,state,actual,m);self.assertFalse(write)
 def test_repair_does_not_accept_unacknowledged_write(self):
  r,item,state,actual,m=self.repair_fixture();state['native_phase']='request_pending'
  with self.assertRaises(native.NativeError):r.repair_candidate(item,state,actual,m)
if __name__=='__main__':unittest.main()
