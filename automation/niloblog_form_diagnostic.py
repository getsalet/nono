"""Read-only native form diagnostic. Never serializes credentials or private URLs."""
import json,sys,datetime,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
from niloblog_pipeline import login,navigate,allowed
ROOT=Path(__file__).resolve().parents[1]
if not allowed():raise SystemExit('Global/user control blocks diagnostic')
report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'read_only_no_submit'}
with sync_playwright() as pw:
 browser=pw.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox']);page=browser.new_page();login(page)
 f=navigate(page,'ارسال مطلب جدید');f.locator('#mtitle').wait_for()
 report['form']=f.evaluate('''()=>({method:document.forms[0].method,onsubmit:document.forms[0].getAttribute('onsubmit'),controls:[...document.forms[0].elements].map(e=>({tag:e.tagName,type:e.type,name:e.name,id:e.id,disabled:e.disabled,checked:e.checked,options:e.tagName==='SELECT'?[...e.options].map(o=>({value:o.value,text:o.textContent,selected:o.selected})):undefined,value:e.type==='checkbox'?e.value:undefined})),scripts:[...document.scripts].filter(e=>!e.src).map(e=>e.textContent).filter(t=>t.includes('pars20_go')||t.includes('CKEDITOR.replace'))})''')
 for sel in ['select[name=pcm]']:
  f.locator(sel).select_option('7')
 report['after_moderation']=f.evaluate('''()=>[...new FormData(document.forms[0]).entries()].map(([k,v])=>({name:k,length:v.length,value:['pcm','pcomment','cdraft','cmail','sabet','a_member'].includes(k)?v:undefined}))''')
 report['form_control_duplicates']=f.evaluate('''()=>{let d={};for(let e of document.forms[0].elements)if(e.name)d[e.name]=(d[e.name]||0)+1;return d}''')
 browser.close()
p=ROOT/'artifacts/niloblog/form-diagnostic.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Safe read-only form diagnostic complete; no native submission.')
