#!/usr/bin/env python3
"""Atomic path-scoped Blogsky checkpoint; preserve concurrent other-blog commits.
Never reset/stash the worktree, stage unrelated files, or overwrite a concurrent
edit to a target path. One Git tree contains all verification/queue/state changes.
"""
import json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCOPES=('artifacts/blogsky-backlink-queue','artifacts/content-originality/blogsky','data/blogsky/backlink-queue.json','state/blogsky-backlink-progress.json','data/blogsky/native-recovery-control.json')
REF='refs/afp/blogsky-native-checkpoint'
def git(args,root,env=None,data=None,check=True):
 r=subprocess.run(['git',*args],cwd=root,env=env,input=data,capture_output=True,timeout=90)
 if check and r.returncode:raise RuntimeError('Blogsky atomic checkpoint failed at '+args[0]+'; recovery evidence retained')
 return r

def allowed(path):
 return any(path==s or path.startswith(s+'/') for s in SCOPES) and '..' not in Path(path).parts

def tree_entries(root,ref,paths):
 out=git(['ls-tree','-r','-z',ref,'--',*paths],root).stdout
 values={}
 for entry in out.split(b'\0'):
  if entry:
   meta,name=entry.split(b'\t',1);values[name.decode()]=meta.split()[2].decode()
 return values

def changed_paths(root):
 paths=set()
 for args in [['diff','--name-only','-z','HEAD','--',*SCOPES],['ls-files','-z','--others','--exclude-standard','--',*SCOPES],['ls-files','-z','--others','--ignored','--exclude-standard','--',*SCOPES]]:
  paths.update(x.decode() for x in git(args,root).stdout.split(b'\0') if x)
 return sorted(paths)

def persist(root=ROOT,paths=None,message='Checkpoint verified Blogsky native outcome [skip ci]'):
 root=Path(root);paths=changed_paths(root) if paths is None else list(paths)
 if not paths:return None
 if any(not allowed(p) or not (root/p).is_file() or (root/p).is_symlink() for p in paths):raise RuntimeError('Only existing scoped Blogsky checkpoint files may be persisted')
 baseline=REF if git(['rev-parse','--verify',REF],root,check=False).returncode==0 else 'HEAD'
 before=tree_entries(root,baseline,paths)
 desired={p:git(['hash-object','-w','--stdin'],root,data=(root/p).read_bytes()).stdout.decode().strip() for p in paths}
 with tempfile.TemporaryDirectory(prefix='afp-blogsky-index-') as tmp:
  env=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'),GIT_AUTHOR_NAME='github-actions[bot]',GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',GIT_COMMITTER_NAME='github-actions[bot]',GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com')
  for attempt in range(3):
   git(['fetch','--quiet','origin','main'],root)
   parent=git(['rev-parse','origin/main'],root).stdout.decode().strip();remote=tree_entries(root,parent,paths)
   if any(remote.get(p) not in (before.get(p),desired[p]) for p in paths):raise RuntimeError('Concurrent edit to Blogsky checkpoint path; no overwrite allowed')
   if all(remote.get(p)==desired[p] for p in paths):git(['update-ref',REF,parent],root);return parent
   git(['read-tree',parent],root,env)
   for p,blob in desired.items():git(['update-index','--add','--cacheinfo','100644,'+blob+','+p],root,env)
   tree=git(['write-tree'],root,env).stdout.decode().strip()
   commit=git(['commit-tree',tree,'-p',parent],root,env,(message+'\n').encode()).stdout.decode().strip()
   if git(['push','--quiet','origin',commit+':refs/heads/main'],root,check=False).returncode==0:
    git(['update-ref',REF,commit],root);return commit
 raise RuntimeError('Blogsky atomic checkpoint push exhausted; blocking intent and artifact retained')

def main():
 import sys
 if '--consume-recovery' in sys.argv:
  p=ROOT/'data/blogsky/native-recovery-control.json';value=json.loads(p.read_text());value.update(enabled=False,consumed_by_run=os.getenv('GITHUB_RUN_ID',''));p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
 commit=persist();print('Atomic scoped Blogsky checkpoint: '+str(commit or 'no changes'))
if __name__=='__main__':main()
