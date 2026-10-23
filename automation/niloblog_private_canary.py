"""Exactly-one private corrected-article canary. Durable intent, no blind retry."""
import copy,datetime,json,sys,traceback
from pathlib import Path
from urllib.parse import parse_qs
from playwright.sync_api import sync_playwright
import niloblog_pipeline as n
report={'at':n.now().isoformat(),'mode':'private_canary_only','public_submission':False}
s=n.read(n.STATE);item=n.read(n.A/'items'/'nilo-7d32c1dc781cd9a1.json')
if any(x['key']==item['key'] for x in s.get('published',[])):raise SystemExit('Canary already published and reconciled; no private mutation')
test=copy.deepcopy(item);test['post']['title']='پیش‌نویس داخلی بررسی AFP: پرونده آبیاری گوجه‌فرنگی تاکستان'
try:
 if not n.allowed():raise n.PipelineStop('Global/user control blocks native write')
 if s.get('intent'):raise n.PipelineStop('Pending intent requires reconciliation; no automatic retry')
 with sync_playwright() as pw:
  browser=pw.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox']);page=browser.new_page();n.login(page)
  found=n.scan(page,test['post']['title'])
  if not found:
   f=n.navigate(page,'ارسال مطلب جدید');n.fill_form(f,test,True)
   report['prepared_body']=n.verify_stored_body(test,f.evaluate('()=>CKEDITOR.instances.mtex.getData()'))
   s['intent']={'key':item['key'],'operation':'private_canary_repair','at':n.now().isoformat(),'public_submission':False};n.checkpoint(s)
   if not n.allowed():raise n.PipelineStop('Control changed before private save')
   def inspect(request):
    if request.method=='POST' and '/desktop.php' in request.url:
     data=parse_qs(request.post_data or '',keep_blank_values=True)
     report['request']={'content_type':request.headers.get('content-type'),'names':sorted(data),'pcm':data.get('pcm'),'draft':data.get('cdraft'),'body_length':len(data.get('mtex',[''])[0]),'body_has_linebreaks':any(x in data.get('mtex',[''])[0] for x in '\r\n\t'),'duplicate_fields':[k for k,v in data.items() if len(v)>1]}
   page.on('request',inspect)
   n.submit_once(f);page.remove_listener('request',inspect)
   text=f.locator('body').inner_text()
   report['response']={'pcomment_integer_error':"Incorrect integer value: '' for column 'pcomment'" in text,'generic_operation_error':'مشکلی در اجرای عملیات پیش آمد' in text,'success_text':'موفقیت' in text}
   found=n.scan(page,test['post']['title'])
   if not found:
    report['private_post_found']=False
    # Only reconcile a determinate rejection followed by a fresh empty native lookup.
    if report['response']['pcomment_integer_error'] or report['response']['generic_operation_error']:
     s['intent']=None;s['private_repair_rejected_at']=n.now().isoformat()
    raise n.PipelineStop('Private native save rejected; no corrected draft persisted')
  f,proof=n.native_readback(page,test)
  native_id=f.locator('input[name=id]').input_value()
  report.update(private_post_found=True,native_id=native_id,proof=proof,private_draft=True)
  item['private_canary']={'native_id':native_id,'private_title':test['post']['title'],'legacy_draft_native_id':'1','verified_at':n.now().isoformat(),'proof':proof}
  item['status']='private_canary_verified';n.save(n.A/'items'/f"{item['key']}.json",item)
  s['intent']=None;s['draft_canary_verified_at']=n.now().isoformat();s.pop('blocked',None)
  browser.close()
except BaseException as e:
 report['error_type']=type(e).__name__
 if isinstance(e,n.PipelineStop):report['safe_error']=str(e)
 report['frames']=[{'function':x.name,'line':x.lineno,'file':Path(x.filename).name} for x in traceback.extract_tb(e.__traceback__)][-6:]
finally:
 n.save(n.A/'private-canary-diagnostic.json',report)
 n.checkpoint(s)
 print('Private canary complete; verified:',bool(report.get('proof')),'public submitted: false')
