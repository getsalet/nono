import unittest
from unittest.mock import patch,Mock
from automation.agri_v2 import curated_continuation as c
from automation.agri_v2.queue import DATA,OUT,load_json
from automation.agri_v2.client import ModelClient
class DashboardContinuationTests(unittest.TestCase):
 def test_remaining_request_is_exactly_two_roles_not_new_three_image_budget(self):
  r=load_json(DATA/'curated-continuation-request.json');c.validate(r);self.assertEqual(r['request_id'],c.REMAINING_ID);self.assertEqual(r['max_image_calls'],2)
  self.assertEqual(c.sha(OUT/'new'/c.TOPIC/'image-1.webp'),r['accepted_image_1_sha256']);self.assertEqual(c.sha(OUT/'curated-continuations'/c.ID/'receipt.json'),r['prior_continuation_sha256'])
  r['max_image_calls']=3
  with self.assertRaises(ValueError):c.validate(r)
 def test_per_kind_budget_never_sends_third_request(self):
  x=object.__new__(c.BoundedClient);x.limit=2;x.accounting_path=None;x.reserved={'image':0,'text':0}
  with patch.object(ModelClient,'request',return_value={}) as request:
   x.request('image','/images/generations',{},1);x.request('image','/images/generations',{},1)
   with self.assertRaises(c.CapabilityError):x.request('image','/images/generations',{},1)
   self.assertEqual(request.call_count,2)
 def test_article_generation_requests_native_json(self):
  x=object.__new__(ModelClient);x.request=Mock(return_value={'choices':[{'message':{'content':'{"title":"fixture"}'}}]})
  x.text('fixture');self.assertEqual(x.request.call_args.args[2]['response_format'],{'type':'json_object'})
