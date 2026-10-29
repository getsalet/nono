import copy,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import niloblog_pipeline as n
class BoundedTextRepairTests(unittest.TestCase):
 def setUp(self):
  # This fixture exercises the legacy transport/media contract, not live rollout.
  from unittest.mock import patch
  legacy=patch('blog_image_restore.enabled',return_value=False);legacy.start();self.addCleanup(legacy.stop)
 def run_case(self,reason,*,second_failure=False,blocked=False,review_rejected=False):
  quote='این نقل دقیق و مستند درباره محصول شهرستان است'
  bundle={'local':{'text':quote},'article':{'text':quote+' راهنمای فنی'},'technical':[],'links':[]}
  plan={'blocked':False,'facts':[{'excerpt_id':'s0-e0','claim':'گزارش محدود'},{'excerpt_id':'s1-e0','claim':'روش عمومی'}]}
  review={'approved':not review_rejected,'grounded':True,'locally_distinct':True,'semantic_duplicate':False,'unsupported_claims':[],'local_evidence_id':'s0-e0'}
  article={'title':'عنوان','html':'<p>انتخaب و ادعای ردشده</p>'};fixed={'blocked':True}if blocked else{'title':'عنوان','html':'<p>انتخاب مستند</p>'}
  outputs=[article,fixed,review]
  # A rejected independent review gets its original bounded second chance, then still fails.
  if review_rejected:outputs += [copy.deepcopy(fixed),copy.deepcopy(review)]
  validations=[n.PipelineStop(reason),n.PipelineStop(reason)if second_failure else 600]
  if review_rejected:validations.append(600)
  with tempfile.TemporaryDirectory()as tmp,patch.object(n,'A',Path(tmp)),patch.object(n,'source_bundle',return_value=bundle),patch.object(n,'all_history',return_value=[]),patch.object(n,'plan_article',return_value={'outline':[]}),patch.object(n,'validate_article',side_effect=validations)as validate,patch('roya_backlink_queue.agnes',side_effect=outputs)as ai,patch.object(n,'reserve',return_value=({}, {'image_id':'img','video_id':None}))as reserve,patch.object(n,'checkpoint'):
   args=({'id':'test','title':'عنوان','angle_ref':'angle'},{'angles':{'angle':{}}},{},{'assets':[{'id':'img','url':'https://x/a.webp','alt':'محصول','width':100,'height':100}]},{})
   if second_failure or blocked or review_rejected or reason=='Cross-blog content reuse':
    with self.assertRaises(n.PipelineStop):n.generate(*args)
    reserve.assert_not_called()
   else:
    result=n.generate(*args);self.assertIn('انتخاب مستند',result['post']['html']);self.assertIsNone(result['selection']['video_id']);self.assertEqual(validate.call_count,2);self.assertEqual(ai.call_count,3)
   if reason!='Cross-blog content reuse':self.assertIn('invalid_visible_tokens',ai.call_args_list[1].args[0])
 def test_mixed_script_repaired_then_revalidated_and_reviewed(self):self.run_case('Mixed-script word requires editorial correction')
 def test_unsupported_claim_repaired_then_revalidated_and_reviewed(self):self.run_case('Unsupported commercial claim')
 def test_second_validation_failure_does_not_reserve_media(self):self.run_case('Unsupported commercial claim',second_failure=True)
 def test_blocked_repair_stays_held(self):self.run_case('Unsupported commercial claim',blocked=True)
 def test_independent_reviewer_can_still_reject_repaired_text(self):self.run_case('Unsupported commercial claim',review_rejected=True)
 def test_cross_blog_reuse_is_not_silently_retried(self):self.run_case('Cross-blog content reuse')
if __name__=='__main__':unittest.main()
