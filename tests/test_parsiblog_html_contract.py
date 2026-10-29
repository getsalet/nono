import json,unittest
from pathlib import Path
import parsiblog_policy as policy
from city_backlink_policy import Inspect
ROOT=Path(__file__).resolve().parents[1]
class NativeHTMLContract(unittest.TestCase):
 def test_writer_explicitly_forbids_observed_merged_table_cells(self):
  row=json.loads((ROOT/'data/parsiblog/title-matrix.json').read_text())['items'][0]
  text=policy.prompt(row,'{}')
  for fragment in ['هیچ ویژگی (attribute)','colspan و rowspan ممنوع','تعداد یکسانی سلول','یک پاراگراف بیرون جدول']:self.assertIn(fragment,text)
 def test_observed_colspan_is_still_rejected_without_mutation(self):
  html='<table><tr><td colspan="3">در انتظار بررسی</td></tr></table>'
  p=Inspect();p.feed(html);self.assertIn('unsupported attribute',p.errors)
 def test_active_attributes_remain_rejected(self):
  for attribute in ['rowspan="2"','onclick="alert(1)"','style="color:red"','data-test="1"']:
   p=Inspect();p.feed('<p '+attribute+'>متن</p>');self.assertIn('unsupported attribute',p.errors)
 def test_simple_table_remains_allowed(self):
  p=Inspect();p.feed('<table><tr><th>مورد</th><th>وضعیت</th></tr><tr><td>برگه فنی</td><td>در انتظار بررسی</td></tr></table>');self.assertEqual(p.errors,[])
