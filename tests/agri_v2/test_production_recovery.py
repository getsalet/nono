import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import production_recovery as recovery,cycle
from automation.agri_v2.queue import atomic_json,load_json,utcnow
from automation.agri_v2.queue_planner import pending_briefs
from automation.agri_v2.client import ImageProviderError

class RecoveryTests(unittest.TestCase):
 def put(self,root,kind='image_provider',category='provider_unavailable'):
  folder=Path(root)/'new'/'agri-111111111111'
  atomic_json(folder/'state.json',{'status':'incomplete','failure':{'kind':kind,'category':category}})
  atomic_json(folder/'article.json',{'title':'preserved'})
  atomic_json(folder/'cycle-attempts.json',{'attempts':2})
  return folder
 def test_four_lifetime_reservations_preserve_attempts_and_article(self):
  with tempfile.TemporaryDirectory() as d:
   f=self.put(d);original={p.name:p.read_bytes() for p in f.glob('*.json')}
   for n in range(4):
    self.assertTrue(recovery.eligible(f));self.assertEqual(recovery.reserve(f)['cycles_started'],n+1)
    recovery.finish(f,'provider_deferred',{'kind':'image_provider'})
   self.assertFalse(recovery.eligible(f))
   with self.assertRaises(ValueError):recovery.reserve(f)
   for name,blob in original.items():self.assertEqual((f/name).read_bytes(),blob)
   self.assertEqual(len(load_json(f/'production-recovery.json')['history']),4)
 def test_quality_validation_auth_and_quota_failures_are_not_reopened(self):
  for kind,category in [('image_quality','unspecified'),('validation','unexpected_mixed_language'),('image_provider','invalid_auth'),('image_provider','quota_limited'),('text_provider','forbidden')]:
   with self.subTest(kind=kind,category=category),tempfile.TemporaryDirectory() as d:self.assertFalse(recovery.eligible(self.put(d,kind,category)))
 def test_missing_article_never_gets_extra_text_generation_budget(self):
  with tempfile.TemporaryDirectory() as d:
   f=self.put(d);(f/'article.json').unlink();self.assertFalse(recovery.eligible(f))
 def test_published_and_fully_staged_states_are_not_provider_recovery(self):
  with tempfile.TemporaryDirectory() as d:
   f=self.put(d);state=load_json(f/'state.json')
   for status in ['published','draft_created']:
    atomic_json(f/'state.json',dict(state,status=status));self.assertFalse(recovery.eligible(f))
 def test_pending_buffer_counts_recoverable_work_but_not_exhausted(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';f=self.put(out)
   atomic_json(data/'config.json',{});atomic_json(data/'briefs'/f'{f.name}.json',{'topic_id':f.name,'publish_authorized':True})
   self.assertEqual(pending_briefs(data,out),[f.name])
   for n in range(4):recovery.reserve(f)
   self.assertEqual(pending_briefs(data,out),[])
 def test_published_receipt_and_holds_always_win(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';f=self.put(out)
   atomic_json(data/'briefs'/f'{f.name}.json',{'topic_id':f.name,'publish_authorized':True})
   atomic_json(data/'config.json',{'publication_holds':{f.name:'owner hold'}});self.assertEqual(pending_briefs(data,out),[])
   atomic_json(data/'config.json',{});atomic_json(f/'wordpress-receipt.json',{'public_verified':True});self.assertEqual(pending_briefs(data,out),[])
 def setup_cycle(self,d):
  data=Path(d)/'data';out=Path(d)/'out';f=self.put(out);ident=f.name
  atomic_json(data/'config.json',{'publication_enabled':True,'automatic_generation':True})
  atomic_json(data/'health/latest.json',{'checked_at':utcnow()})
  brief={'topic_id':ident,'publish_authorized':True};atomic_json(data/'briefs'/f'{ident}.json',brief)
  return data,out,f,{'id':ident,'title':'موضوع'}
 def test_cooldown_never_reserves_or_spends_recovery(self):
  with tempfile.TemporaryDirectory() as d:
   data,out,f,topic=self.setup_cycle(d)
   with patch.object(cycle,'DATA',data),patch.object(cycle,'OUT',out),patch.object(cycle,'get_topic',return_value=topic),patch.object(cycle,'check_brief'),patch.object(cycle,'update'),patch('automation.agri_v2.recovery.circuit_open',return_value=True),patch.object(cycle,'draft') as draft:
    self.assertEqual(cycle.run(scheduled=True)['status'],'provider_cooldown');draft.assert_not_called()
   self.assertFalse((f/'production-recovery.json').exists());self.assertEqual(load_json(f/'cycle-attempts.json')['attempts'],2)
 def test_transient_recovery_returns_deferred_and_preserves_two_original_attempts(self):
  with tempfile.TemporaryDirectory() as d:
   data,out,f,topic=self.setup_cycle(d)
   with patch.object(cycle,'DATA',data),patch.object(cycle,'OUT',out),patch.object(cycle,'get_topic',return_value=topic),patch.object(cycle,'check_brief'),patch.object(cycle,'update'),patch('automation.agri_v2.recovery.circuit_open',return_value=False),patch.object(cycle,'handle_generation_failure'),patch.object(cycle,'WordPress') as wp,patch.object(cycle,'draft',side_effect=ImageProviderError(503,'image_queue_full','provider_unavailable')):
    wp.return_value.inventory.return_value={'records':[{'id':1}]}
    result=cycle.run(scheduled=True);self.assertEqual(result['status'],'provider_deferred');wp.return_value.publish.assert_not_called()
   self.assertEqual(load_json(f/'production-recovery.json')['cycles_started'],1);self.assertEqual(load_json(f/'cycle-attempts.json')['attempts'],2)
   self.assertTrue((out/'latest-cycle-deferred.json').exists())
 def test_recovery_can_publish_without_resetting_original_budget(self):
  with tempfile.TemporaryDirectory() as d:
   data,out,f,topic=self.setup_cycle(d)
   with patch.object(cycle,'DATA',data),patch.object(cycle,'OUT',out),patch.object(cycle,'get_topic',return_value=topic),patch.object(cycle,'check_brief'),patch.object(cycle,'update'),patch('automation.agri_v2.recovery.circuit_open',return_value=False),patch.object(cycle,'validate_for_publication'),patch.object(cycle,'WordPress') as wp,patch.object(cycle,'draft') as draft:
    wp.return_value.preflight.return_value={'can_publish':True};wp.return_value.inventory.return_value={'records':[{'id':1}]};wp.return_value.publish.return_value={'public_verified':True}
    self.assertTrue(cycle.run(scheduled=True)['public_verified']);draft.assert_called_once();wp.return_value.publish.assert_called_once()
   self.assertEqual(load_json(f/'production-recovery.json')['status'],'publication_verified');self.assertEqual(load_json(f/'cycle-attempts.json')['attempts'],2)
