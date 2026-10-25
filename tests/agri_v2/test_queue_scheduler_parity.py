import tempfile,time,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from automation.agri_v2 import cycle,recovery,research
from automation.agri_v2.queue import atomic_json,load_json,utcnow
from automation.agri_v2.queue_planner import pending_briefs
T={'id':'agri-111111111111','title':'عنوان تست','crop':'لوبیا'}
class ScopeTests(unittest.TestCase):
 def test_image_wait_does_not_block_text_and_unknown_scope_stays_closed(self):
  with tempfile.TemporaryDirectory() as d,patch.object(recovery,'OUT',Path(d)):
   for row in ({'scope':'image generation only; shared cooldown'},{'request_kind':'text'},{'request_kind':'unspecified'}):
    atomic_json(Path(d)/'provider-circuit.json',dict(row,open=True,retry_at_epoch=time.time()+3600))
    self.assertTrue(recovery.circuit_open())
    if row.get('scope'):self.assertTrue(recovery.circuit_open('image'));self.assertFalse(recovery.circuit_open('text'))
    elif row.get('request_kind')=='text':self.assertFalse(recovery.circuit_open('image'));self.assertTrue(recovery.circuit_open('text'))
    else:self.assertTrue(recovery.circuit_open('text'));self.assertTrue(recovery.circuit_open('image'))
class QueueParityTests(unittest.TestCase):
 def setup_files(self,d,mode):
  data=Path(d)/'data';out=Path(d)/'out';ident=T['id'];folder=out/'new'/ident
  atomic_json(data/'config.json',{'automatic_generation':True,'publication_enabled':True,'research_feeder':{'enabled':True}})
  atomic_json(data/'briefs'/f'{ident}.json',{'topic_id':ident,'publish_authorized':True})
  atomic_json(data/'health/latest.json',{'checked_at':utcnow()})
  if mode=='published':atomic_json(folder/'wordpress-receipt.json',{'public_verified':True})
  if mode=='exhausted':
   atomic_json(folder/'cycle-attempts.json',{'attempts':2});atomic_json(out/'research'/f'{ident}.json',{'attempts':1,'status':'brief_ready','source_catalog_version':2})
  return data,out,folder
 def run_research_path(self,mode):
  with tempfile.TemporaryDirectory() as d:
   data,out,folder=self.setup_files(d,mode)
   with patch.object(cycle,'DATA',data),patch.object(cycle,'OUT',out),patch.object(cycle,'get_topic',return_value=T),patch.object(cycle,'check_brief'),patch.object(cycle,'update'),patch.object(cycle,'WordPress') as wp,patch.object(cycle,'draft') as draft,patch.object(recovery,'circuit_open',side_effect=lambda kind=None:kind!='text'),patch.object(research,'prepare_one',return_value={'status':'research_needs_review','topic_id':'next-topic'}) as prep:
    r=cycle.run(scheduled=True);self.assertEqual(r['topic_id'],'next-topic');prep.assert_called_once();draft.assert_not_called();wp.return_value.preflight.assert_called_once()
   if mode=='exhausted':self.assertEqual(load_json(out/'research'/f"{T['id']}.json")['attempts'],1);self.assertEqual(load_json(folder/'cycle-attempts.json')['attempts'],2)
 def test_published_topic_before_image_wait_no_longer_freezes_research(self):self.run_research_path('published')
 def test_exhausted_topic_before_image_wait_preserves_attempts_and_moves_on(self):self.run_research_path('exhausted')
 def test_waiting_image_can_fill_one_research_buffer_slot(self):self.run_research_path('pending')
 def test_full_two_brief_buffer_makes_zero_model_or_wp_calls(self):
  with tempfile.TemporaryDirectory() as d:
   data,out,folder=self.setup_files(d,'pending');atomic_json(data/'briefs/agri-222222222222.json',{'topic_id':'agri-222222222222','publish_authorized':True})
   with patch.object(cycle,'DATA',data),patch.object(cycle,'OUT',out),patch.object(cycle,'get_topic',return_value=T),patch.object(cycle,'check_brief'),patch.object(cycle,'update'),patch.object(cycle,'WordPress') as wp,patch.object(cycle,'draft') as draft,patch.object(recovery,'circuit_open',side_effect=lambda kind=None:kind!='text'),patch.object(research,'prepare_one') as prep:
    self.assertEqual(cycle.run(scheduled=True)['status'],'provider_cooldown');wp.assert_not_called();draft.assert_not_called();prep.assert_not_called()
 def test_fully_staged_article_publishes_without_model_during_image_wait(self):
  with tempfile.TemporaryDirectory() as d:
   data,out,folder=self.setup_files(d,'pending');atomic_json(folder/'state.json',{'status':'draft_created','brief_sha256':cycle.digest(load_json(data/'briefs'/f"{T['id']}.json"))});atomic_json(folder/'article.json',{});atomic_json(folder/'wordpress-draft-payload.json',{})
   for n in (1,2):(folder/f'image-{n}.webp').write_bytes(b'test')
   with patch.object(cycle,'DATA',data),patch.object(cycle,'OUT',out),patch.object(cycle,'get_topic',return_value=T),patch.object(cycle,'check_brief'),patch.object(cycle,'validate_article'),patch.object(cycle,'validate_for_publication'),patch.object(cycle,'update'),patch.object(cycle,'WordPress') as wp,patch.object(cycle,'draft') as draft,patch.object(recovery,'circuit_open',return_value=True):
    wp.return_value.preflight.return_value={'can_publish':True};wp.return_value.inventory.return_value={'source_generated_at':utcnow(),'scope':'all published','records':[{'id':1}]};wp.return_value.publish.return_value={'status':'published','public_verified':True};self.assertEqual(cycle.run(scheduled=True)['status'],'published');draft.assert_not_called();wp.return_value.publish.assert_called_once()
 def test_pending_selection_is_read_only_and_skips_holds(self):
  with tempfile.TemporaryDirectory() as d:
   data,out,folder=self.setup_files(d,'pending');before=(data/'config.json').read_bytes();self.assertEqual(pending_briefs(data,out),[T['id']]);self.assertEqual((data/'config.json').read_bytes(),before)
