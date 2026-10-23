"""Public-read reconciliation only: no login, AI, form fill or native submission."""
import json
from playwright.sync_api import sync_playwright
import niloblog_pipeline as n

def main():
 if not n.allowed():raise SystemExit('User/global control blocks reconciliation')
 s=n.read(n.STATE)
 if not s.get('intent'):print('No pending intent; no generation or native write');return
 if s['intent'].get('operation')!='create_public_post':raise n.PipelineStop('Unsupported intent retained')
 with sync_playwright()as pw:
  browser=pw.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox'])
  try:
   context=browser.new_context();page=context.new_page()
   receipt=n.reconcile_public_intent(page,s)
   n.save(n.A/'public-reconciliation.json',{'at':n.now().isoformat(),'new_public_write_performed':False,'provider_requests':0,'receipt':receipt})
  finally:browser.close()
if __name__=='__main__':main()
