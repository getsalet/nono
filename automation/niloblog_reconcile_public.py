"""Reconcile a pending publication by reading public evidence. Never submits."""
from pathlib import Path
import traceback
from playwright.sync_api import sync_playwright
import niloblog_pipeline as n
s=n.read(n.STATE);key='nilo-7d32c1dc781cd9a1'
if any(x['key']==key for x in s.get('published',[])):raise SystemExit('Public receipt already reconciled; no native write')
if not s.get('intent') or s['intent'].get('key')!=key or s['intent'].get('operation')!='create_public_post':raise SystemExit('Expected pending public intent missing; no native write')
item=n.read(n.A/'items'/f'{key}.json')
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox']);context=browser.new_context();page=context.new_page()
  receipt=n.verify_public(page,item);browser.close()
 s['media']=n.acknowledge(n.read(n.D/'media-catalog.json'),s['media'],key,receipt['url'],public_receipt_verified=True)
 s.setdefault('published',[]).append({'key':key,'url':receipt['url'],'at':receipt['at']})
 item.update(status='published',receipt=receipt);n.save(n.A/'items'/f'{key}.json',item);n.save(n.A/'receipts'/f'{key}.json',receipt)
 s.setdefault('intent_reconciliation_history',[]).append(s.get('intent_reconciliation',{}))
 s['intent_reconciliation']={'at':n.now().isoformat(),'operation':'create_public_post','result':'Existing native public article independently verified. No resubmission.','url':receipt['url']}
 s['intent']=None;s['current']=None;s['public_canary_verified_at']=receipt['at']
 n.save(n.A/'last-error.json',{'at':receipt['at'],'resolved':True,'reason':None,'verified_public_receipt':receipt['url']})
 n.save(n.A/'public-reconciliation.json',{'at':receipt['at'],'new_public_write_performed':False,'receipt':receipt})
 n.checkpoint(s);print('Existing native public article reconciled; no duplicate post:',receipt['url'])
except BaseException as e:
 n.save(n.A/'public-reconciliation-error.json',{'at':n.now().isoformat(),'error_type':type(e).__name__,'reason':str(e) if isinstance(e,n.PipelineStop) else 'private error details withheld','frames':[{'file':Path(x.filename).name,'function':x.name,'line':x.lineno} for x in traceback.extract_tb(e.__traceback__)][-8:]})
 n.checkpoint(s);raise SystemExit('Reconciliation stopped; pending intent retained, no native write')
