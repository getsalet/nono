#!/usr/bin/env python3
"""Read only: observe native editing contract, never click a save/new-post action."""
import json,os,re
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/rozblog-image-repair';OUT.mkdir(parents=True,exist_ok=True)
def observed_edit_url(links,panel,pid):
 parent=urlsplit(panel).path.rsplit('/',1)[0]+'/'
 options=[]
 for link in links:
  url=link.get('href','');p=urlsplit(url);q=parse_qs(p.query)
  if p.scheme!='https'or p.hostname!='www.rozblog.com'or not p.path.startswith(parent):continue
  # A native edit route must be observed, not synthesized from a guessed endpoint.
  editing=bool(re.search(r'edit|update',p.path+' '+link.get('label',''),re.I))or'ویرایش'in link.get('label','')
  identity=any(str(pid)in values for name,values in q.items()if name.lower()in('id','pid','postid','post_id','edit','update','idpost'))or bool(re.search(r'(?:/|=)'+str(pid)+r'(?:/|$)',p.path))
  if editing and identity and set(q)<={'id','pid','postid','post_id','edit','update','idpost'}:options.append(url)
 if len(set(options))!=1:raise RuntimeError('Unique observed native edit route required')
 return options[0]
def main():
 import publish_rozblog_posts as native
 from playwright.sync_api import sync_playwright
 q=json.loads((ROOT/'data/rozblog/backlink-queue.json').read_text());rows={x['key']:x for x in q['items']}
 plan=json.loads((ROOT/'data/rozblog-image-repair-plan.json').read_text());report={'mode':'inspect-only','post_submissions':0,'items':[],'editor_contract':None}
 with sync_playwright()as pw:
  browser=pw.chromium.launch(args=['--no-sandbox']);context=browser.new_context(locale='fa-IR');page=context.new_page()
  try:
   posts,_=native.login(page);existing=native.scan(page,posts)
   for selection in plan['items']:
    item=rows[selection['key']];pid=selection['pid'];title=selection['title']
    if not item.get('published')or item.get('post_id')not in(None,pid):raise RuntimeError('Selection is not the expected existing publication')
    if existing.get(title,{}).get('pid')!=pid:raise RuntimeError('Native title and ID do not match the selected post')
    # Scan is paginated; find the actual row page, following only observed pages.
    pending=[posts];seen=set();edit=None
    while pending and not edit:
     listing=pending.pop(0)
     if listing in seen:continue
     seen.add(listing);page.goto(listing,wait_until='domcontentloaded');row=page.locator('#tr_'+str(pid))
     if row.count():
      links=row.locator('a[href]').evaluate_all("a=>a.map(x=>({href:x.href,label:(x.innerText+' '+(x.title||'')+' '+(x.getAttribute('aria-label')||'')).trim()}))")
      try:edit=observed_edit_url(links,posts,pid)
      except RuntimeError:
       report['items'].append({'key':selection['key'],'pid':pid,'edit_route_found':False,'link_labels':[x['label']for x in links]});raise
     for u in page.locator('a[href]').evaluate_all('a=>a.map(x=>x.href)'):
      if u.startswith(posts+'?')and re.search(r'[?&](page|p)=\d+',u)and u not in seen:pending.append(u)
     if len(seen)>100:raise RuntimeError('No partial native post scan')
    if not edit:raise RuntimeError('Selected native post row not found')
    report['items'].append({'key':selection['key'],'pid':pid,'edit_url':edit})
    if report['editor_contract']is None:
     report['stage']='open_observed_edit_route'
     page.goto(edit,wait_until='domcontentloaded')
     report['editor_contract']={'page_path':urlsplit(page.url).path,'title':page.title(),
       'controls':page.locator('input,textarea,select,button').evaluate_all("a=>a.filter(x=>x.type!=='hidden'&&x.type!=='password').map(x=>({tag:x.tagName,id:x.id,name:x.name,type:x.type,button_text:x.tagName==='BUTTON'?x.innerText:((x.type==='submit'||x.type==='button')?x.value:'')}))"),
       'frames':[{'path':urlsplit(f.url).path,'host':urlsplit(f.url).hostname}for f in page.frames]}
     report['stage']='wait_for_native_title'
     page.wait_for_selector('#mtitle',timeout=20000)
     report['title_matches']=page.locator('#mtitle').input_value()==title
     if not report['title_matches']:raise RuntimeError('Native edit title changed; no writes allowed')
     report['stage']='wait_for_editors'
     page.wait_for_function('()=>window.tinymce&&tinymce.get("mtex")?.initialized',timeout=20000)
     report['editor_contract']['editor_ids']=page.evaluate('()=>tinymce.editors.map(x=>x.id)')
     report['editor_contract']['body_image_counts']=page.evaluate('()=>["mtex","mtex2"].map(id=>({id,count:(tinymce.get(id)?.getContent()||"").match(/<img\\b/gi)?.length||0}))')
     report['stage']='editor_observed'

  except Exception as exc:
   report['error_type']=type(exc).__name__
   raise
  finally:
   (OUT/'editor-discovery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));browser.close()
 print('Read-only image editor discovery completed; inspected existing posts:',len(report['items']))
if __name__=='__main__':main()
