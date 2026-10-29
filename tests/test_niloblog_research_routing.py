import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import niloblog_pipeline as n
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads((ROOT/'data/niloblog/title-matrix.json').read_text());cls.targets={x['key']:x for x in json.loads((ROOT/'data/niloblog/article-targets.json').read_text())['targets']}
 def row(self,cluster):return next(r for r in self.m['titles']if self.m['angles'][r['angle_ref']]['cluster']==cluster)
 def test_every_route_is_approved_and_bounded(self):
  for row in self.m['titles']:
   refs=n.research_refs(row,self.m,self.targets);self.assertEqual(len(refs),2);self.assertEqual(len(set(refs)),2)
 def test_repair_question_uses_maintenance_not_rotating_specs(self):
  row=self.row('نشتی و آسیب');self.assertEqual(n.research_refs(row,self.m,self.targets),['site-post-900','site-post-939'])
 def test_monitoring_uses_inspection_and_pressure(self):
  row=self.row('پایش حین بهره‌برداری');self.assertEqual(n.research_refs(row,self.m,self.targets),['site-post-1002','site-post-34967'])
 def test_backlink_contract_unchanged(self):
  before=copy.deepcopy(self.m)
  for row in self.m['titles']:n.research_refs(row,self.m,self.targets)
  self.assertEqual(before,self.m)
 def test_unapproved_or_redirected_source_fails_closed(self):
  row=self.row('نشتی و آسیب')
  for field,value in [('target_url','https://example.org/fake'),('family','hose'),('kind','product')]:
   targets=copy.deepcopy(self.targets);targets['site-post-900'][field]=value
   with self.assertRaises(n.PipelineStop):n.research_refs(row,self.m,targets)
if __name__=='__main__':unittest.main()
