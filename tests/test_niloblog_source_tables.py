import copy,sys,unittest
from pathlib import Path
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from niloblog_source_tables import extract_tables,admitted_tables
from niloblog_source_hygiene import model_source_view
class SourceTableTests(unittest.TestCase):
 def setUp(self):
  self.html='<table><tr><th>Indication</th><th>Possible problem</th></tr><tr><td>Gradual pressure increase at filter outlet</td><td>Dripper plugging</td></tr><tr><td>Sudden pressure increase at filter outlet</td><td>Stuck control valve or other flow restrictions</td></tr></table>'
  self.tables=extract_tables(BeautifulSoup(self.html,'html.parser'));self.text=self.tables[0]['text']
 def test_adjacent_diagnostic_rows_keep_their_own_causes(self):
  self.assertEqual(self.tables[0]['rows'][1],['Gradual pressure increase at filter outlet','Dripper plugging'])
  self.assertEqual(self.tables[0]['rows'][2],['Sudden pressure increase at filter outlet','Stuck control valve or other flow restrictions'])
  self.assertFalse(self.tables[0]['inferences_added'])
 def test_unadmitted_chemical_table_never_leaks_into_model(self):
  extra=extract_tables(BeautifulSoup('<table><tr><th>Brand</th><th>Chemical</th></tr><tr><td>Excluded brand</td><td>Excluded chemical</td></tr></table>','html.parser'))
  text=self.text+' '+extra[0]['text'];source={'url':'https://example.org/','text':text,'tables':self.tables+extra,'sha256':'raw'}
  b={'local':None,'article':{'url':'https://a.org','text':'This text is outside the admitted table contract.'},'technical':[source],'required_evidence':[{'excerpt_id':'s2-contract0','source_index':2,'scope':'technical_general','quote':self.text}]};before=copy.deepcopy(b)
  view=model_source_view(b);self.assertEqual(b,before);self.assertEqual(view['technical'][0]['tables'],self.tables);self.assertNotIn('Excluded chemical',str(view));self.assertEqual(view['technical'][0]['sha256'],'raw')
 def test_partial_table_quote_does_not_admit_extra_rows(self):
  self.assertEqual(admitted_tables({'text':self.text,'tables':self.tables},['Gradual pressure increase at filter outlet Dripper plugging']),[])
 def test_tampered_table_rejected(self):
  tables=copy.deepcopy(self.tables);tables[0]['rows'][1][1]='Invented diagnosis'
  with self.assertRaisesRegex(ValueError,'not verifiable'):admitted_tables({'text':self.text,'tables':tables},[self.text])
 def test_nested_spanned_irregular_and_captioned_tables_are_not_guessed(self):
  for h in ['<table><tr><td colspan="2">x</td></tr><tr><td>a</td><td>b</td></tr></table>','<table><tr><td>a</td><td>b</td></tr><tr><td>c</td></tr></table>','<table><caption>Extra</caption><tr><td>a</td><td>b</td></tr><tr><td>c</td><td>d</td></tr></table>']:
   self.assertEqual(extract_tables(BeautifulSoup(h,'html.parser')),[])
if __name__=='__main__':unittest.main()
