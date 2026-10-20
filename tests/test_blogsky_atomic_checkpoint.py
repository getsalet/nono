import os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
from checkpoint_blogsky_native import persist
class AtomicCheckpointTests(unittest.TestCase):
 def git(self,root,*args):
  r=subprocess.run(['git',*args],cwd=root,capture_output=True,check=True);return r.stdout.decode().strip()
 def setup_repo(self,d):
  base=Path(d);remote=base/'remote.git';self.git(base,'init','--bare',str(remote));root=base/'work';self.git(base,'clone',str(remote),str(root));self.git(root,'config','user.name','test');self.git(root,'config','user.email','test@example.invalid');self.git(root,'checkout','-b','main')
  p=root/'state/blogsky-backlink-progress.json';p.parent.mkdir();p.write_text('old');(root/'unrelated.txt').write_text('base');self.git(root,'add','.');self.git(root,'commit','-m','base');self.git(root,'push','origin','main');return base,root,remote
 def test_atomic_overlay_preserves_unrelated_remote_and_worktree_edits(self):
  with tempfile.TemporaryDirectory() as d:
   base,root,remote=self.setup_repo(d);other=base/'other';self.git(base,'clone','--branch','main',str(remote),str(other));self.git(other,'config','user.name','test');self.git(other,'config','user.email','test@example.invalid');(other/'unrelated.txt').write_text('remote change');self.git(other,'commit','-am','concurrent');self.git(other,'push','origin','main')
   (root/'unrelated.txt').write_text('uncommitted local change');(root/'state/blogsky-backlink-progress.json').write_text('verified');commit=persist(root)
   self.assertEqual(self.git(root,'show',commit+':unrelated.txt'),'remote change');self.assertEqual((root/'unrelated.txt').read_text(),'uncommitted local change');self.assertEqual(self.git(root,'show',commit+':state/blogsky-backlink-progress.json'),'verified')
 def test_concurrent_target_edit_is_not_overwritten(self):
  with tempfile.TemporaryDirectory() as d:
   base,root,remote=self.setup_repo(d);other=base/'other';self.git(base,'clone','--branch','main',str(remote),str(other));self.git(other,'config','user.name','test');self.git(other,'config','user.email','test@example.invalid');(other/'state/blogsky-backlink-progress.json').write_text('concurrent state');self.git(other,'commit','-am','concurrent');self.git(other,'push','origin','main');(root/'state/blogsky-backlink-progress.json').write_text('local state')
   with self.assertRaises(RuntimeError):persist(root)
   self.assertEqual(self.git(root,'show','origin/main:state/blogsky-backlink-progress.json'),'concurrent state')
 def test_second_checkpoint_advances_own_intent_without_reset(self):
  with tempfile.TemporaryDirectory() as d:
   base,root,remote=self.setup_repo(d);p=root/'artifacts/blogsky-backlink-queue/native-publications/key.json';p.parent.mkdir(parents=True);p.write_text('intent');persist(root,[str(p.relative_to(root))]);p.write_text('verified');commit=persist(root)
   self.assertEqual(self.git(root,'show',commit+':'+str(p.relative_to(root))),'verified');self.assertEqual(self.git(root,'log','-1','--format=%s','HEAD'),'base')
 def test_unrelated_explicit_path_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   base,root,remote=self.setup_repo(d)
   with self.assertRaises(RuntimeError):persist(root,['unrelated.txt'])
if __name__=='__main__':unittest.main()
