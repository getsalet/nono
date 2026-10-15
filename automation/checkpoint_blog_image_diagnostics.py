"""Persist only safe diagnostic report/images using an isolated Git index.
Never rebase a dirty generator checkout or include browser sessions/credentials.
"""
import json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def checkpoint():
 report=ROOT/'data/blog-generated-image-acceptance.json'
 if not report.exists():return 0
 data=json.loads(report.read_text());files={'data/blog-generated-image-acceptance.json'}
 if data.get('post_submissions')!=0:raise RuntimeError('Diagnostic scope invalid')
 for row in data.get('families',[]):
  for path in row.get('candidate_paths',[]):
   p=Path(path)
   if p.is_absolute()or '..'in p.parts or not path.startswith('artifacts/blog-image-acceptance/')or p.suffix!='.webp':raise RuntimeError('Invalid diagnostic image path')
   if (ROOT/p).is_file()and(ROOT/p).stat().st_size<8*1024*1024:files.add(path)
 # Reviews contain only non-secret visual decisions and public/local candidate identifiers.
 for p in (ROOT/'artifacts/blog-image-reviews').glob('*.json'):
  if p.stat().st_size<100000:files.add(str(p.relative_to(ROOT)))
 def git(args,env=None,input=None,check=True):
  r=subprocess.run(['git',*args],cwd=ROOT,env=env,input=input,capture_output=True)
  if check and r.returncode:raise RuntimeError('Diagnostic repository operation failed: '+args[0])
  return r
 with tempfile.TemporaryDirectory()as tmp:
  env=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'),GIT_AUTHOR_NAME='github-actions[bot]',GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',GIT_COMMITTER_NAME='github-actions[bot]',GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com')
  for attempt in range(3):
   git(['fetch','--quiet','origin','main']);parent=git(['rev-parse','origin/main']).stdout.decode().strip()
   git(['read-tree',parent],env);git(['add','--sparse','-f','--',*sorted(files)],env)
   tree=git(['write-tree'],env).stdout.decode().strip()
   if tree==git(['rev-parse',parent+'^{tree}']).stdout.decode().strip():return 0
   commit=git(['commit-tree',tree,'-p',parent],env,b'Preserve bounded image QA diagnostics without post publication\n').stdout.decode().strip()
   if git(['push','--quiet','origin',commit+':refs/heads/main'],check=False).returncode==0:
    print('Safe image diagnostics checkpointed:',len(files));return 0
 raise RuntimeError('Diagnostic checkpoint push failed')
if __name__=='__main__':
 try:raise SystemExit(checkpoint())
 except RuntimeError as exc:
  print('::error::'+str(exc));raise SystemExit(1)
