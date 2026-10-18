"""Stdlib-only wake-up gate for an existing ready image and saved article.
Does not approve content, change queues, use a provider or submit a post.
"""
import hashlib,json,os,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path,default=None):
 return json.loads(path.read_text())if path.exists()else default
def select(blog,root=ROOT):
 if blog!='rozblog':raise ValueError('Only the explicitly enabled Rozblog handoff is supported')
 from check_blog_pipeline_control import decision
 if not decision(blog,root)['proceed']:return None
 root=Path(root);queue=read(root/'data'/blog/'backlink-queue.json',{'items':[]});selected=[]
 for path in (root/'data/blog-image-stock/requests').glob('*.json'):
  row=read(path,{})
  if row.get('status')!='ready'or row.get('blog')!=blog:continue
  asset=row.get('asset_id','');key=row.get('key','');digest=row.get('review_sha256','')
  if not re.fullmatch('[a-f0-9]{32}',asset)or not re.fullmatch('[A-Za-z0-9_-]+',key)or not re.fullmatch('[a-f0-9]{64}',digest):continue
  if path.name!=asset+'.json':continue
  matches=[x for x in queue['items']if x.get('key')==key]
  if len(matches)!=1:continue
  source=matches[0]
  if source.get('published')or source.get('status')not in('failed','pending')or source.get('_image_stock_request')!=asset:continue
  if source.get('family')!='tape20':continue
  record=read(root/f'artifacts/{blog}-backlink-queue/items/{key}.json',{})
  if record.get('status')!='failed'or record.get('failure_stage')!='image':continue
  post=record.get('post');context=row.get('item',{}).get('_image_article_context')
  if not isinstance(post,dict)or not all(isinstance(post.get(k),str)and post[k].strip()for k in ('title','slug','html')):continue
  plain=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',post['html'])).strip()
  actual={'title':post['title'],'meta_description':post.get('meta_description',''),'summary':plain[:1200]}
  if actual!=context or source.get('_image_article_context')!=context:continue
  image=root/f'assets/blog-generated/{blog}/{asset}.webp'
  if not image.exists()or hashlib.sha256(image.read_bytes()).hexdigest()!=digest:continue
  selected.append((row.get('ready_at',0),key))
 return min(selected)[1]if selected else None

def handoff(event,blog,root=ROOT):
 if event not in('push','workflow_run'):return {'proceed':True,'cached_only':False,'target':''}
 target=select(blog,root)
 return {'proceed':bool(target),'cached_only':True,'target':target or ''}
def main():
 result=handoff(os.getenv('GITHUB_EVENT_NAME',''),sys.argv[1]);print(json.dumps(result))
 if os.getenv('GITHUB_OUTPUT'):
  with open(os.environ['GITHUB_OUTPUT'],'a')as out:
   out.write('proceed='+('1'if result['proceed']else'0')+'\ncached_only='+('1'if result['cached_only']else'0')+'\ntarget='+result['target']+'\n')
 return 0
if __name__=='__main__':raise SystemExit(main())
