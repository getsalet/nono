#!/usr/bin/env python3
"""Add only the observed Search Console property token to the live native theme.
Never replaces a theme, removes other verification tokens, exports sessions,
logs native responses, generates articles, or submits a post.
"""
import contextlib,io,json,os,re,sys,time,hashlib
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent.parent
BLOGS={'roya':'https://afp.royablog.ir/','farsiblog':'https://afp.farsiblog.com/','rozblog':'https://afp-pipe.rozblog.com/','loxblog':'https://afp.lxb.ir/'}

def patched(source,token):
 if not re.fullmatch(r'[A-Za-z0-9_-]{30,100}',token):raise ValueError('Invalid public verification token')
 if not re.search(r'<head(?:\s|>)',source,re.I) or not re.search(r'</head\s*>',source,re.I):raise ValueError('Expected native HTML head missing')
 if 'navar-abyari.ir'not in source:raise ValueError('Expected AFP theme identity missing')
 if token in source:return source
 tag='<meta name="google-site-verification" content="'+token+'" />\n'
 return re.sub(r'</head\s*>',lambda m:tag+m[0],source,count=1,flags=re.I)

def run(key):
 from playwright.sync_api import sync_playwright
 token=json.loads((ROOT/'data/gsc/verification-tags.json').read_text())[key]
 result={'blog':BLOGS[key],'at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'changed':False,'verified_live':False}
 with sync_playwright()as pw:
  browser=pw.chromium.launch(headless=True)
  try:
   page=browser.new_page()
   # Native helpers may print panel details. Deliberately discard that output.
   with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
    if key=='loxblog':
     import loxblog_native as native
     native.login(page);page.goto(native.PANEL+'/adminnew.php?page=themeedit',wait_until='domcontentloaded',timeout=60000);native.assert_management(page)
     page.get_by_role('tab',name=re.compile('قالب هدر')).click()
    elif key=='roya':
     import publish_roya_posts as native
     native.login(page)
    elif key=='farsiblog':
     import publish_farsiblog_posts as native
     native.login(page)
    else:
     import publish_rozblog_posts as native
     native.login(page)
   if key!='loxblog':
    options=page.locator('a[href]').evaluate_all("es=>es.map(e=>({text:(e.innerText||'').trim(),href:e.href}))")
    def norm(s):return re.sub(r'\s+',' ',s.replace('ي','ی').replace('ك','ک')).strip()
    candidates=[x for x in options if norm(x['text'])==('ویرایش قالب سایت'if key=='rozblog'else'ویرایش ساختار قالب فعلی') and urlsplit(x['href']).hostname==urlsplit(page.url).hostname]
    urls=list(dict.fromkeys(x['href']for x in candidates))
    if len(urls)!=1:
     result['editor_candidates']=[{'label':norm(x['text'])[:80],'path':urlsplit(x['href']).path}for x in options if 'قالب'in norm(x['text'])][:20]
     raise ValueError('Unique observed native theme-editor link required')
    page.goto(urls[0],wait_until='domcontentloaded',timeout=60000)
   page.locator('textarea').first.wait_for(state='attached',timeout=30000)
   candidates=[]
   for field in page.locator('textarea').all():
    source=field.input_value()
    if key=='loxblog'and field.get_attribute('name')!='themeheader':continue
    if re.search(r'<head(?:\s|>)',source,re.I)and 'navar-abyari.ir'in source:candidates.append((field,source))
   if len(candidates)!=1:raise ValueError('Unique loaded AFP native theme required')
   field,source=candidates[0];new=patched(source,token)
   result['before_sha256']=hashlib.sha256(source.encode()).hexdigest()
   if new!=source:
    field.evaluate("""(el,value)=>{for(const n of document.querySelectorAll('.CodeMirror')){if(n.CodeMirror?.getTextArea?.()===el){n.CodeMirror.setValue(value);n.CodeMirror.save()}}el.value=value;el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));}""",new)
    form=field.locator('xpath=ancestor::form[1]')
    if form.count()!=1:raise ValueError('Native theme form missing')
    actions=[]
    for el in form.locator('button,input[type=submit],input[type=button]').all():
     text=(el.get_attribute('value')or el.inner_text()).strip()
     if re.search(r'ذخیره|ثبت|save|update',text,re.I)and el.is_visible()and el.is_enabled():actions.append(el)
    if len(actions)!=1:
     result['save_actions']=[{'tag':x.evaluate('e=>e.tagName'),'label':(x.get_attribute('value')or x.inner_text())[:90]}for x in form.locator('button,input[type=submit],input[type=button]').all()if x.is_visible()]
     raise ValueError('Unique observed native save action required')
    # One save only. If acknowledgement is uncertain, verify without resubmitting.
    actions[0].click(timeout=30000);result['changed']=True
   public=browser.new_page()
   try:
    for attempt in range(4):
     response=public.goto(BLOGS[key],wait_until='domcontentloaded',timeout=60000)
     values=public.locator('head meta[name="google-site-verification"]').evaluate_all('es=>es.map(e=>e.content)')
     if response and response.status==200 and token in values:
      result['verified_live']=True;result['verification_tag_count']=len(values);break
     time.sleep(3)
    if not result['verified_live']:raise ValueError('Property token not yet present in live head')
   finally:public.close()
  except Exception as exc:
   # Error strings from third-party libraries may include sensitive response data.
   result['error_type']=type(exc).__name__
   safe={'Unique observed native theme-editor link required','Unique loaded AFP native theme required','Native theme form missing','Unique observed native save action required','Property token not yet present in live head'}
   if str(exc)in safe:result['reason']=str(exc)
  finally:browser.close()
 path=ROOT/'data/gsc/results'/f'{key}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps({'blog':BLOGS[key],'changed':result['changed'],'verified_live':result['verified_live'],'error_type':result.get('error_type')},ensure_ascii=False))
 return 0 if result['verified_live']else 1
if __name__=='__main__':sys.exit(run(sys.argv[1]))
