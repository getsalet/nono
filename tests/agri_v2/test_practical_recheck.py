import tempfile,shutil,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from automation.agri_v2 import practical_recheck as r,image_quality as q
from automation.agri_v2.queue import DATA,OUT,load_json,atomic_json,get_topic
from automation.agri_v2.client import ModelClient
from automation.agri_v2.curated_continuation import BoundedClient,CapabilityError
class PracticalRecheckTests(unittest.TestCase):
 def test_exact_existing_bytes_and_zero_new_images(self):
  req=load_json(DATA/'practical-recheck-request.json');r.validate(req);folder=OUT/'new'/r.TOPIC
  self.assertEqual(req['max_image_calls'],0);self.assertEqual(req['image_2_sha256'],r.sha(folder/'image-2.webp'))
  self.assertEqual(req['prior_quality_sha256'],r.sha(OUT/'practical-rechecks'/r.ID/'prior-image-2.quality.json'))
  req['max_image_calls']=1
  with self.assertRaises(ValueError):r.validate(req)
 def test_zero_image_budget_never_calls_provider(self):
  x=object.__new__(BoundedClient);x.limit=0;x.review_limit=1;x.accounting_path=None;x.reserved={'image':0,'text':0}
  with patch.object(ModelClient,'request') as provider:
   with self.assertRaises(CapabilityError):x.request('image','/',{},1)
   provider.assert_not_called()
 def test_old_62_not_silently_reapproved(self):
  with tempfile.TemporaryDirectory() as tmp:
   source=OUT/'new'/r.TOPIC;p=Path(tmp)/'image-2.webp';shutil.copyfile(source/'image-2.webp',p)
   archive=OUT/'practical-rechecks'/r.ID/'prior-image-2.quality.json';shutil.copyfile(archive,q.review_path(p));before=q.review_path(p).read_bytes()
   self.assertEqual(load_json(archive)['verdict']['score'],62)
   with self.assertRaises(q.ImageQualityError):q.valid_record(p,get_topic('new',r.TOPIC),2,load_json(source/'article.json'))
   self.assertEqual(q.review_path(p).read_bytes(),before)
 def exercise_review(self,passed):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);data=root/'data';out=root/'out';folder=out/'new'/r.TOPIC;folder.mkdir(parents=True);(data/'briefs').mkdir(parents=True)
   source=OUT/'new'/r.TOPIC
   for name in ['article.json','image-1.webp','image-1.quality.json','image-2.webp','image-2.quality.json','cycle-attempts.json']:shutil.copyfile(source/name,folder/name)
   shutil.copyfile(OUT/'practical-rechecks'/r.ID/'prior-image-2.quality.json',folder/'image-2.quality.json')
   for name in ['practical-recheck-request.json','config.json']:shutil.copyfile(DATA/name,data/name)
   shutil.copyfile(DATA/'briefs'/f'{r.TOPIC}.json',data/'briefs'/f'{r.TOPIC}.json');(data/'health').mkdir();shutil.copyfile(DATA/'health/latest.json',data/'health/latest.json')
   old=(folder/'image-2.quality.json').read_bytes();images=[(folder/f'image-{i}.webp').read_bytes() for i in (1,2)]
   client=Mock();checks={k:True for k in q.CHECKS};checks['role_camera_match']=False
   if not passed:checks['product_identity_match']=False
   client.review_image.return_value={'score':90,'checks':checks,'reasons':['Offline fixture only; not an assessment of the real image']}
   wp=Mock();wp.publish.return_value={'public_verified':True,'url':'https://navar-abyari.ir/fixture/'}
   with patch.object(r,'DATA',data),patch.object(r,'OUT',out),patch.object(r,'authorized',return_value=True),patch.object(r,'BoundedClient',return_value=client),patch('automation.agri_v2.wordpress.WordPress',return_value=wp):
    result=r.run();self.assertEqual(result['status'],'publication_verified' if passed else 'stopped_safely')
    client.review_image.assert_called_once();client.image.assert_not_called();client.text.assert_not_called()
    self.assertEqual(images,[(folder/f'image-{i}.webp').read_bytes() for i in (1,2)])
    receipt=out/'practical-rechecks'/r.ID/'receipt.json';self.assertEqual(receipt.with_name('prior-image-2.quality.json').read_bytes(),old)
    if passed:wp.publish.assert_called_once();self.assertEqual(load_json(folder/'image-2.quality.json')['verdict']['score'],90)
    else:wp.publish.assert_not_called();self.assertEqual((folder/'image-2.quality.json').read_bytes(),old)
    r.run();self.assertEqual(client.review_image.call_count,1)
 def test_fresh_pass_preserves_old_verdict_and_image_bytes(self):self.exercise_review(True)
 def test_fresh_failure_never_publishes_or_spends_again(self):self.exercise_review(False)
 def test_reviewer_defines_illustrative_not_documentary_match(self):
  import inspect
  text=inspect.getsource(ModelClient.review_image)
  for phrase in ['NOT documentary proof','Never cascade a cosmetic camera mismatch','not inflate the score']:self.assertIn(phrase,text)
