import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from city_backlink_policy import resolve_editorial_link_tokens,prompt
import farsiblog_backlink_queue as f
class EditorialTokenTests(unittest.TestCase):
 def setUp(self):self.links=[{'url':'https://navar-abyari.ir/article/','anchor':'راهنمای انتخاب نوار تیپ','role':'article'}]
 def test_exact_token_binds_owned_url_and_anchor(self):
  obj={'html':'<p><a href="AFP_LINK_1">لنگر اشتباه</a></p>'};resolve_editorial_link_tokens(obj,self.links)
  self.assertEqual(obj['html'],'<p><a href="https://navar-abyari.ir/article/">راهنمای انتخاب نوار تیپ</a></p>')
 def test_unknown_missing_foreign_and_visible_tokens_are_not_hidden(self):
  for body in ('<p>AFP_LINK_1</p>','<a href="AFP_LINK_99">بد</a>','<a href="https://wrong.example/">بد</a>','<p>بدون لینک</p>'):
   obj={'html':body};resolve_editorial_link_tokens(obj,self.links);self.assertEqual(obj['html'],body)
 def test_duplicates_remain_for_strict_qa(self):
  obj={'html':'<a href="AFP_LINK_1">الف</a>'*2};resolve_editorial_link_tokens(obj,self.links);self.assertEqual(obj['html'].count(self.links[0]['url']),2)
 def test_prompt_uses_tokens_without_long_destinations(self):
  item={'site_title':'نوار تیپ','angle':'انتخاب','family':'tape20','assigned_title':'راهنمای انتخاب نوار تیپ','key':'x','kind':'article'}
  with patch('city_backlink_policy.matrix_title',return_value=item['assigned_title']):text=prompt(item,self.links,'مرجع','farsiblog')
  self.assertIn('AFP_LINK_1',text);self.assertNotIn(self.links[0]['url'],text);self.assertIn('بدون span',text)
 def test_safe_transient_provider_errors_retry_but_auth_does_not(self):
  with patch.object(f.time,'sleep'),patch('builtins.print'):
   with patch.object(f,'source_text',side_effect=[RuntimeError('Agnes/provider HTTP 503; raw response withheld'),'ok'])as op:self.assertEqual(f.retry_transient(op),'ok');self.assertEqual(op.call_count,2)
   with patch.object(f,'source_text',side_effect=RuntimeError('Agnes/provider HTTP 403; raw response withheld'))as op,self.assertRaises(RuntimeError):f.retry_transient(op)
   self.assertEqual(op.call_count,1)
if __name__=='__main__':unittest.main()
