#!/usr/bin/env python3
"""Apply already-live verified editorial corrections to existing records only."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p,default):return json.loads(p.read_text())if p.exists()else default
def save(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def normalized(s):return s.replace('ي','ی').replace('ك','ک').strip()
def reconcile(root=ROOT):
 manifest=load(root/'data/farsiblog/editorial-fixes-20261014.json',{})
 if not manifest:return 0
 revision=manifest['revision'];qpath=root/'data/farsiblog/backlink-queue.json';spath=root/'state/farsiblog-backlink-progress.json'
 queue=load(qpath,{'items':[]});state=load(spath,{});count=0;art=root/'artifacts/farsiblog-backlink-queue'
 for fix in manifest['updates']:
  matches=[x for x in queue['items']if x.get('key')==fix['key']]
  if len(matches)!=1:raise RuntimeError('Editorial record is missing or ambiguous')
  item=matches[0]
  if item.get('editorial_revision')==revision:continue
  if not fix.get('live_verified')or item.get('pid')!=fix['pid']or not item.get('published'):raise RuntimeError('Cannot apply an editorial correction to an unpublished or different post')
  if normalized(item.get('title',''))not in (normalized(fix['previous_title']),normalized(fix['title'])):raise RuntimeError('Post changed after review; do not overwrite a newer edit')
  if hashlib.sha256(fix['html'].encode()).hexdigest()!=fix['body_sha256']:raise RuntimeError('Editorial body checksum mismatch')
  p=art/'items'/(item['key']+'.json');record=load(p,None)
  if record is None or record.get('pid')!=fix['pid']:raise RuntimeError('Published item artifact identity missing')
  item.update(title=fix['title'],assigned_title=fix['title'],editorial_revision=revision)
  record.update(title=fix['title'],assigned_title=fix['title'],matrix_title=fix['title'],editorial_revision=revision)
  record['post'].update(title=fix['title'],html=fix['html'])
  if 'meta_title'in record['post']:record['post']['meta_title']=fix['title']
  # Keep original publication time/URL: this is an edit, not another publication.
  for row in state.get('published',[]):
   if row.get('key')==fix['key']:row['title']=fix['title'];row['editorial_revision']=revision
  save(p,record);count+=1
 save(qpath,queue);save(spath,state)
 if count:save(art/'verified-editorial-updates.json',manifest)
 print('Verified existing editorial records reconciled:',count)
 return count
if __name__=='__main__':reconcile()
