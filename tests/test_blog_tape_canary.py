import copy,datetime,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import run_blog_tape_canary as c
class TapeCanaryTests(unittest.TestCase):
 def fixture(self):
  req={'request_id':'a'*32,'blog':'farsiblog','family':'tape20','count':1,'publish':True,'target':'saved'}
  control={'enabled':True,'pause_image_production':False,'enabled_families':['tape20'],'cancelled_families':['hose'],'blogs':['farsiblog']}
  item={'key':'saved','family':'tape20','status':'failed','failure_stage':'image','next_retry_at':'2020-01-01T00:00:00Z'}
  record={**item,'post':{'title':'نوار تیپ','slug':'saved-draft','html':'<p>متن ذخیره شده</p>'}}
  return req,control,[item],record
 def test_existing_tape_image_draft_is_selected_without_mutation(self):
  values=self.fixture();before=copy.deepcopy(values)
  self.assertEqual(c.validate(*values)['key'],'saved');self.assertEqual(values,before)
 def test_hose_scope_pause_and_higher_article_count_are_blocked(self):
  for target,key,value in [(0,'family','hose'),(0,'count',2),(1,'pause_image_production',True),(1,'enabled_families',['tape20','hose']),(1,'cancelled_families',[])]:
   values=list(self.fixture());values[target][key]=value
   with self.assertRaises(RuntimeError):c.validate(*values)
 def test_published_future_due_or_mismatched_draft_blocked(self):
  for target,key,value in [(2,'published',True),(2,'next_retry_at','2099-01-01T00:00:00Z'),(3,'key','other'),(3,'post',None),(2,'failure_stage','validation')]:
   values=list(self.fixture());row=values[target][0]if target==2 else values[target];row[key]=value
   with self.assertRaises(RuntimeError):c.validate(*values)
 def test_recorded_request_is_never_dispatched_again(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);(root/'data').mkdir();req=self.fixture()[0];(root/'data/blog-tape-live-canary-request.json').write_text(json.dumps(req))
   ledger=root/'artifacts/blog-tape-live-canary'/('a'*32+'.json');ledger.parent.mkdir(parents=True);ledger.write_text('{"status":"dispatching"}')
   with patch.object(c,'ROOT',root),patch.object(c.urllib.request,'urlopen')as network:
    self.assertEqual(c.main(),0);network.assert_not_called()
 def test_controller_workflow_has_no_image_credentials_or_direct_generator(self):
  source=(Path(__file__).resolve().parents[1]/'.github/workflows/blog-tape-live-canary.yml').read_text()
  self.assertNotIn('secrets.',source);self.assertNotIn('backlink_queue.py',source);self.assertIn('run_blog_tape_canary.py',source)

class NamedPublicationTests(unittest.TestCase):
 def test_named_target_does_not_drain_other_approved_drafts(self):
  import publish_farsiblog_posts as p
  entries=[{'key':'other'},{'key':'saved'}]
  self.assertEqual(p.selected_entries(entries,'saved'),[entries[1]])
  self.assertEqual(p.selected_entries(entries,'missing'),[])
  self.assertEqual(p.selected_entries(entries,''),entries)
 def test_named_canary_is_capped_to_one_at_native_handoff(self):
  import publish_farsiblog_posts as p
  entries=[{'key':'other'},{'key':'saved'}]
  saved={'key':'saved','kind':'fixture','post':{}}
  with patch('blog_image_runtime_control.publication_paused',return_value=False),patch('city_backlink_policy.matrix_ready',return_value=True),patch.dict('os.environ',{'FARSIBLOG_TARGET':'saved'}),patch.object(p.native,'DO_PUBLISH',False),patch.object(p.native,'LIMIT',3),patch.object(p.native,'load',side_effect=[{'items':entries},saved])as load,patch.object(p.native,'main',return_value=0)as native,patch.object(p.generator,'qa',return_value=([],{})),patch.object(p.generator,'links_for',return_value=[]),patch.object(p.generator,'save')as save:
   self.assertEqual(p.main(),0);self.assertEqual(p.native.LIMIT,1);native.assert_called_once()
   self.assertEqual(save.call_args.args[1]['items'],[entries[1]])
   self.assertEqual(load.call_count,2)
