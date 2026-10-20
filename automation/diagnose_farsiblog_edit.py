"""Read-only form diagnostics. Never outputs credentials, values, or script bodies."""
import json,copy
from pathlib import Path
import publish_farsiblog_posts as p
from reconcile_known_blog_posts import entry_and_item,matches
from farsiblog_pressure_wording import normalize
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];entry,item=entry_and_item(p.native,'farsiblog');links=p.generator.links_for(item);corrected=copy.deepcopy(item);corrected['post']=normalize(item['post'])
report={'read_only':True,'new_articles':0}
with sync_playwright()as pw:
 b=pw.chromium.launch(headless=True)
 try:
  page=b.new_page();p.login(page);page.goto(p.native.PANEL+'/User/EditPosts/146',wait_until='domcontentloaded',timeout=60000);p.active_blog(page)
  if page.locator('#ptitle').input_value()!=item['post']['title']:raise RuntimeError('Exact title identity mismatch')
  page.wait_for_function("()=>['pshort','pfull'].every(id=>window.tinymce?.get(id)?.initialized)",timeout=45000)
  body=page.evaluate("()=>tinymce.get('pshort').getContent()+tinymce.get('pfull').getContent()")
  report['native_original_matches']=matches(item,body,links);report['native_corrected_matches']=matches(corrected,body,links)
  report['form']=page.locator('#ptitle').evaluate('''e=>{const f=e.form;return {action:f.action,method:f.method,cls:f.className,controls:[...f.elements].map(x=>({tag:x.tagName,id:x.id,name:x.name,type:x.type,disabled:x.disabled,valid:x.checkValidity()})),scripts:[...document.scripts].map(x=>x.src).filter(u=>u.startsWith(location.origin)),submitEndpoints:[...f.querySelectorAll('button,input[type=submit]')].map(x=>({tag:x.tagName,id:x.id,name:x.name,kind:x.type})),events:window.jQuery?Object.keys(jQuery._data(f,'events')||{}):[]}}''')
 finally:b.close()
p=root/'artifacts/farsiblog-edit-form-diagnosis.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
