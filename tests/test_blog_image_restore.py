import copy,datetime,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import blog_image_restore as restore
from blog_image_connection import settings
class RestoreTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.cfg=json.loads((restore.ROOT/restore.CONFIG).read_text());self.cfg['enabled']=True;self.save()
 def save(self):
  p=self.root/restore.CONFIG;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(self.cfg))
 def proof(self,slots):
  p=self.root/restore.EVIDENCE;p.parent.mkdir(parents=True,exist_ok=True)
  v={'policy':restore.POLICY,'status':'completed','connection':settings('https://apihub.agnes-ai.com/v1'),'post_submissions':0,'key_pairs':self.cfg['key_pairs'],'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'keys':[{'secret_name':n,'image':{'status':'image_healthy','http_status':200,'width':1024,'height':768,'image_sha256':'a'*64}}for n in slots]}
  p.write_text(json.dumps(v));return p,v
 def test_fourteen_disjoint_named_bindings_and_text_kept(self):
  c=restore.load(self.root);names=[n for p in c['key_pairs'].values()for n in p]
  self.assertEqual(len(set(names)),14);self.assertEqual(c['key_pairs']['parsiblog'],['AGNES_API_KEY26','AGNES_API_KEY27']);self.assertFalse(set(names)&{'AGNES_API_KEY14','AGNES_API_KEY15'})
 def test_retired_blog_never_enabled_or_assigned(self):
  self.assertFalse(restore.enabled('blogfa',self.root))
  with self.assertRaises(RuntimeError):restore.assigned('blogfa',self.root)
 def test_cross_blog_assignment_rejected(self):
  self.cfg['key_pairs']['parsiblog'][0]=self.cfg['key_pairs']['roya'][0];self.save()
  with self.assertRaises(RuntimeError):restore.load(self.root)
 def test_missing_pair_rejected(self):
  del self.cfg['key_pairs']['niloblog'];self.save()
  with self.assertRaises(RuntimeError):restore.load(self.root)
 def test_text_slot_not_reassigned(self):
  self.cfg['key_pairs']['niloblog'][0]='AGNES_API_KEY14';self.save()
  with self.assertRaises(RuntimeError):restore.load(self.root)
 def test_one_to_two_default_one(self):
  self.assertEqual(restore.load(self.root)['default_images_per_post'],1)
  for field,value in [('minimum_images_per_post',0),('maximum_images_per_post',3),('default_images_per_post',True)]:
   bad=copy.deepcopy(self.cfg);bad[field]=value
   with patch('json.loads',return_value=bad),self.assertRaises(RuntimeError):restore.load(self.root)
 def test_staged_configuration_does_not_enable_production(self):
  self.cfg['enabled']=False;self.save()
  self.assertFalse(restore.enabled('niloblog',self.root));self.assertEqual(restore.reserved(self.root),set())
 def test_image_pool_ignores_text_health_but_not_assignment(self):
  env={'AGNES_API_KEY12':'fake-nilo','AGNES_API_KEY26':'fake-parsi','AGNES_API_KEY27':'fake-parsi-b','AGNES_API_KEY14':'fake-text','AGNES_API_KEYS':'fake-outside','AGNES_HEALTHY_SLOTS_ONLY':'1'}
  p=restore.pool(self.root,env);self.assertEqual(set(p.keys),{'fake-nilo','fake-parsi','fake-parsi-b'})
 def test_pair_evidence_never_borrows_other_blog_key(self):
  self.proof(self.cfg['key_pairs']['roya'])
  self.assertEqual(restore.evidence('roya',self.root),self.cfg['key_pairs']['roya'])
  with self.assertRaises(RuntimeError):restore.evidence('parsiblog',self.root)
 def test_bytes_dimensions_and_timestamp_required(self):
  p,v=self.proof(self.cfg['key_pairs']['roya']);v['keys'][0]['image']['image_sha256']='missing';v['keys'][1]['image']['width']=False;p.write_text(json.dumps(v))
  with self.assertRaises(RuntimeError):restore.evidence('roya',self.root)
  p,v=self.proof(self.cfg['key_pairs']['roya']);v['finished_at']='2000-01-01T00:00:00+00:00';p.write_text(json.dumps(v))
  with self.assertRaises(RuntimeError):restore.evidence('roya',self.root)
 def test_real_runtime_success_keeps_live_key_eligible_without_paid_reaudits(self):
  import blog_image_key_router as router,time
  p,v=self.proof(self.cfg['key_pairs']['roya']);v['finished_at']='2000-01-01T00:00:00+00:00';p.write_text(json.dumps(v))
  key=self.cfg['key_pairs']['roya'][0]
  q=self.root/router.STATE;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps({'policy':router.POLICY,'keys':{key:{'last_success_at_epoch':time.time(),'status':'image_healthy'}},'updated_at_epoch':time.time()}))
  self.assertEqual(restore.evidence('roya',self.root),[key])
 def test_duplicate_binding_not_eligible(self):
  p,v=self.proof(self.cfg['key_pairs']['roya']);v['keys'][0]['duplicate_of']='AGNES_API_KEY14';v['keys'][1]['duplicate_of']='AGNES_API_KEY14';p.write_text(json.dumps(v))
  with self.assertRaises(RuntimeError):restore.evidence('roya',self.root)
 def test_held_family_remains_rejected_before_provider(self):
  with patch('blog_generated_image.rollout_enabled',return_value=True),patch('blog_generated_image.prepare_now')as generate,self.assertRaisesRegex(RuntimeError,'held'):
   restore.prepare({'family':'hose'},{'title':'x','html':'x'},'roya',self.root)
  generate.assert_not_called()
 def test_reference_pipeline_only_after_actual_article_context(self):
  item={'key':'example','family':'tape20'};post={'title':'عنوان آموزشی','html':'<p>'+('متن واقعی مقاله '*20)+'</p>'}
  with patch('blog_generated_image.rollout_enabled',return_value=True),patch('blog_generated_image.prepare_now',return_value='https://example.invalid/image.webp')as generate:
   url=restore.prepare(item,post,'niloblog',self.root)
  self.assertEqual(item['image_url'],url);self.assertEqual(item['_image_article_context']['title'],post['title']);generate.assert_called_once_with(item,'niloblog',self.root,max_rounds=2)
 def test_text_pool_cannot_recover_image_slot_through_alias(self):
  from agnes_key_pool import AgnesKeyPool
  env={'AGNES_API_KEY12':'fake-image','AGNES_API_KEY14':'fake-text','AGNES_API_KEYS':'fake-image,fake-alias'}
  with patch.object(restore,'reserved',return_value={'AGNES_API_KEY12'}):
   p=AgnesKeyPool(env,report_path='/absent')
  self.assertEqual(set(p.keys),{'fake-text','fake-alias'})
 def test_enabled_pair_router_never_falls_back_to_legacy_pool(self):
  import blog_image_key_router as router
  self.proof(self.cfg['key_pairs']['roya'])
  self.assertEqual(router.evidence(self.root,'roya'),self.cfg['key_pairs']['roya'])
  with self.assertRaises(RuntimeError):router.evidence(self.root,'parsiblog')
 def test_new_blog_asset_urls_require_immutable_owner(self):
  from blog_image_gate import approved_url
  for blog in ('niloblog','parsiblog','blogsky'):
   url='https://raw.githubusercontent.com/getsalet/nono/'+'a'*40+'/assets/blog-generated/'+blog+'/'+'b'*32+'.webp'
   self.assertTrue(approved_url(url));self.assertFalse(approved_url(url.replace('a'*40,'main')))
if __name__=='__main__':unittest.main()

class FailureDetailsTests(unittest.TestCase):
 def test_private_error_text_never_enters_report(self):
  result=restore.failure_details({'_generation_stage':'generation_api'},RuntimeError('Authorization: fake-secret provider payload'))
  self.assertEqual(result['code'],'image_pipeline_failed');self.assertNotIn('fake-secret',json.dumps(result))
 def test_quality_flags_use_saved_matching_digest_only(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);digest='a'*64;p=root/'artifacts/blog-image-reviews'/('tape20-'+digest+'.json');p.parent.mkdir(parents=True)
   p.write_text(json.dumps({'sha256':digest,'verdict':{'score':97,'packaging_not_used_as_hardware':False,'reasons':'private model output'}}))
   result=restore.failure_details({'_generation_stage':'local_vision_qa','_image_rejections':[{'sha256':digest}]},RuntimeError('Product image rejected: private output'),root)
   self.assertEqual(result['failed_review_flags'],['packaging_not_used_as_hardware']);self.assertEqual(result['review_score'],97);self.assertNotIn('private',json.dumps(result))
 def test_queue_misconfiguration_has_explicit_safe_code(self):
  self.assertEqual(restore.failure_details({},RuntimeError('Hosted image queue not configured; no provider request'))['code'],'image_queue_not_configured')

class CorrectiveCandidateTests(unittest.TestCase):
 def fixture(self,root):
  cfg=json.loads((restore.ROOT/restore.CONFIG).read_text());cfg['enabled']=True
  p=root/restore.CONFIG;p.parent.mkdir(parents=True);p.write_text(json.dumps(cfg))
  item={'key':'bounded-fixture','family':'tape20','site_title':'نوار تیپ'}
  post={'title':'پایش آبیاری با نوار تیپ','html':'<p>'+('متن آموزشی درباره پایش رطوبت و نوار تیپ '*15)+'</p>'}
  return item,post
 def test_restored_entry_point_has_two_candidate_ceiling_and_no_asset_on_rejection(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);item,post=self.fixture(root)
   with patch('blog_generated_image.rollout_enabled',return_value=True),patch('blog_generated_image.family_enabled',return_value=True),patch('blog_generated_image.existing_asset',return_value=None),patch('blog_generated_image.reconsider_candidate',return_value=None),patch('blog_image_backpressure.require_open'),patch('blog_generated_image.generate',return_value=b'fixture')as generate,patch('blog_image_gate.review',side_effect=RuntimeError('Product image rejected: fixture')),patch('blog_generated_image.checkpoint_asset')as checkpoint:
    with self.assertRaisesRegex(RuntimeError,'Product image rejected:'):restore.prepare(item,post,'roya',root)
   self.assertEqual(generate.call_count,2);checkpoint.assert_not_called();self.assertNotIn('image_url',item)
 def test_provider_failure_is_never_retried_as_visual_rejection(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);item,post=self.fixture(root)
   with patch('blog_generated_image.rollout_enabled',return_value=True),patch('blog_generated_image.family_enabled',return_value=True),patch('blog_generated_image.existing_asset',return_value=None),patch('blog_generated_image.reconsider_candidate',return_value=None),patch('blog_image_backpressure.require_open'),patch('blog_generated_image.generate',side_effect=RuntimeError('Image provider HTTP 429; raw response withheld'))as generate,patch('blog_generated_image.checkpoint_asset')as checkpoint:
    with self.assertRaisesRegex(RuntimeError,'HTTP 429'):restore.prepare(item,post,'roya',root)
   self.assertEqual(generate.call_count,1);checkpoint.assert_not_called()
