import tempfile,shutil,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from automation.agri_v2 import practical_finalize as f,image_quality as q
from automation.agri_v2.queue import DATA,OUT,load_json,atomic_json,get_topic
from automation.agri_v2.client import ModelClient
class FinalizeTests(unittest.TestCase):
 def test_existing_real_72_has_all_critical_checks_but_score_unchanged(self):
  path=OUT/'practical-rechecks/pinto-illustration-recheck-v1/fresh-image-2.quality.json';row=load_json(path)
  self.assertEqual(row['verdict']['score'],72);self.assertFalse(row['verdict']['passed']);self.assertTrue(q.verdict(row['verdict'])['passed'])
 def test_zero_call_request_cannot_gain_paid_budget(self):
  req=load_json(DATA/'practical-finalize-request.json');f.validate(req);req['max_visual_reviews']=1
  with self.assertRaises(ValueError):f.validate(req)
 def exercise(self,bad=False):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);data=root/'data';out=root/'out';folder=out/'new'/f.TOPIC;folder.mkdir(parents=True);(data/'briefs').mkdir(parents=True)
   source=OUT/'new'/f.TOPIC
   for name in ['article.json','image-1.webp','image-1.quality.json','image-2.webp','image-2.quality.json','cycle-attempts.json']:shutil.copyfile(source/name,folder/name)
   shutil.copyfile(OUT/'practical-finalizations'/f.ID/'prior-image-2.quality.json',folder/'image-2.quality.json')
   for name in ['config.json','practical-finalize-request.json']:shutil.copyfile(DATA/name,data/name)
   shutil.copyfile(DATA/'briefs'/f'{f.TOPIC}.json',data/'briefs'/f'{f.TOPIC}.json')
   relative=Path('practical-rechecks/pinto-illustration-recheck-v1/fresh-image-2.quality.json');fresh=out/relative;fresh.parent.mkdir(parents=True);shutil.copyfile(OUT/relative,fresh)
   old=(folder/'image-2.quality.json').read_bytes();images=[(folder/f'image-{i}.webp').read_bytes() for i in (1,2)]
   if bad:
    row=load_json(fresh);row['verdict']['checks']['single_product']=False;atomic_json(fresh,row);req=load_json(data/'practical-finalize-request.json');req['fresh_quality_sha256']=f.sha(fresh);atomic_json(data/'practical-finalize-request.json',req)
   wp=Mock();wp.publish.return_value={'public_verified':True,'url':'https://navar-abyari.ir/fixture/'}
   with patch.object(f,'DATA',data),patch.object(f,'OUT',out),patch.object(f,'authorized',return_value=True),patch('automation.agri_v2.wordpress.WordPress',return_value=wp),patch.object(ModelClient,'request',side_effect=AssertionError('No model calls')) as provider:
    if bad:
     with self.assertRaises(q.ImageQualityError):f.run()
     wp.publish.assert_not_called();self.assertEqual((folder/'image-2.quality.json').read_bytes(),old)
    else:
     result=f.run();self.assertEqual(result['status'],'publication_verified');self.assertEqual(result['model_calls'],0);wp.publish.assert_called_once()
     self.assertEqual((folder/'image-2.quality.json').read_bytes(),fresh.read_bytes());self.assertEqual(load_json(folder/'image-2.quality.json')['verdict']['score'],72)
     record=q.valid_record(folder/'image-2.webp',get_topic('new',f.TOPIC),2,load_json(folder/'article.json'));self.assertTrue(record['verdict']['passed']);self.assertFalse(record['new_visual_review_claimed'])
     self.assertIsNone(f.run());self.assertEqual(wp.publish.call_count,1)
    provider.assert_not_called();self.assertEqual(images,[(folder/f'image-{i}.webp').read_bytes() for i in (1,2)])
 def test_publish_from_unchanged_real_evidence_without_any_model_call(self):self.exercise()
 def test_even_owner_policy_never_waives_a_critical_failure(self):self.exercise(True)
