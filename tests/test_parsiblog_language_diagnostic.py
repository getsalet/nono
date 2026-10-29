import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from validate_parsiblog_language import validate
class LanguageDiagnosticTests(unittest.TestCase):
 def test_diagnostic_cannot_save_ready_or_call_publication(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);key='pb-'+'1'*20
   files={'artifacts/parsiblog-backlink-queue/rejected/'+key+'.json':{'key':key,'passed':False,'errors':['Unexpected foreign-language text in Persian article'],'post':{'title':'عنوان','html':'<p>متن برای بررسی برای مزرعه دیگر برای تصمیم نیست для این مورد.</p>'}},'data/parsiblog/title-matrix.json':{'items':[{'key':key}]}}
   for p,x in files.items():f=root/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(x))
   before={str(p.relative_to(root)):p.read_bytes()for p in root.rglob('*.json')}
   with patch('parsiblog_policy.qa',return_value=([],{})):
    r=validate(key,root,lambda prompt:{'edits':[{'field':'body','old':'для','new':'برای'}]})
   self.assertEqual(r['status'],'validated_language_not_published');self.assertFalse(r['native_write_attempted']);self.assertFalse(r['state_changed']);self.assertFalse(r['ready_post_saved'])
   self.assertEqual(before,{str(p.relative_to(root)):p.read_bytes()for p in root.rglob('*.json')})
 def test_untrusted_target_is_rejected_before_model_or_file_access(self):
  for key in ['../escape','pb-x','pb-'+'1'*20+'; echo unsafe']:
   with self.assertRaises(ValueError):validate(key,Path('/no-such-dir'),lambda x: self.fail('no model'))
if __name__=='__main__':unittest.main()
