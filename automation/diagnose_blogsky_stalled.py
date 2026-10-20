#!/usr/bin/env python3
"""Inspect one known failed native run and archive; never submit a post."""
import json,os,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KEY='city-66afad426708678b'
JOB=118400363092
REPORT=ROOT/'artifacts/blogsky-backlink-queue/diagnostics/stalled-native.json'

def main():
    report={'target_key':KEY,'failed_job':JOB,'native_submissions':0,'queue_modified':False,'controls_modified':False}
    record=json.loads((ROOT/f'artifacts/blogsky-backlink-queue/items/{KEY}.json').read_text())
    post=record['post']
    report['title']=post['title'];report['slug']=post['slug']
    # Provider/browser raw messages are never copied. Only the publisher's own
    # fixed, secret-free error categories are recognized from the old job log.
    categories={
      'Published post not uniquely confirmed in public archive':'public_archive_discovery_missing_or_ambiguous',
      'Durable automatic intent checkpoint failed':'durable_intent_checkpoint_failed',
      'Automatic admission changed before submit':'admission_changed_before_submit',
      'Native editor serialization failed current QA':'native_serialization_qa_failed',
      'TimeoutError':'browser_timeout',
      'Matching native post exists':'matching_native_post_exists',
      'Native Blogsky authentication rejected':'authentication_rejected'}
    try:
        headers={'Accept':'application/vnd.github+json','Authorization':'Bearer '+os.environ['GH_TOKEN'],'User-Agent':'AFP-read-only-native-diagnostic'}
        request=urllib.request.Request('https://api.github.com/repos/getsalet/nono/actions/jobs/'+str(JOB)+'/logs',headers=headers)
        with urllib.request.urlopen(request,timeout=60) as response:raw=response.read(8*1024*1024).decode('utf-8','replace')
        lines=[line for line in raw.splitlines() if 'Blogsky native operation stopped:' in line]
        report['publisher_error_categories']=sorted({category for line in lines for needle,category in categories.items() if needle in line})
        report['publisher_error_line_found']=bool(lines)
    except Exception as exc:report['logs_read_error_type']=type(exc).__name__
    try:
        from playwright.sync_api import sync_playwright
        import blogsky_native as native
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            try:
                context=browser.new_context();page=context.new_page();native.login(page)
                report['native_login_verified']=True
                body=(ROOT/'templates/blogsky/afp-single-post.html').read_text().replace('{{ARTICLE_HTML}}',post['html'])
                report['editor_state']=page.evaluate("""()=>({getHTML:HTMLArea.prototype.getHTML.toString(),setHTML:HTMLArea.prototype.setHTML.toString(),submit:document.querySelector('#post-form').onsubmit.toString(),registry:Object.keys(HTMLArea).filter(k=>/editor|instance/i.test(k)),frames:[...document.querySelectorAll('.htmlarea iframe')].map(f=>({ready:f.contentDocument?.readyState,hasBody:!!f.contentDocument?.body}))})""")
                page.wait_for_timeout(3000)
                report['stage']='fill' 
                native.fill(page,post,body)
                report['stage']='validation'
                report['native_form_preflight']=page.evaluate('''()=>{const f=document.querySelector('#post-form');let jqValid=null,errors=[];try{if(window.jQuery&&jQuery.fn.valid){jqValid=jQuery(f).valid();errors=(jQuery(f).validate().errorList||[]).map(e=>({field:e.element.id,message:e.message}))}}catch(e){errors=[{field:'validator',message:e.message}]}return {htmlValid:f.checkValidity(),jqueryValid:jqValid,errors,visibleErrors:[...document.querySelectorAll('.field-validation-error,.validation-summary-errors,.token-invalid')].map(x=>x.textContent.trim()).filter(Boolean),fields:['post-title','post-address','post-tag','post-content'].map(id=>{const x=document.getElementById(id);return {id,name:x?.name,length:x?.value?.length,validation:x?[...x.attributes].filter(a=>a.name.startsWith('data-val')||['maxlength','pattern','required'].includes(a.name)).map(a=>({name:a.name,value:a.value})):[]}})}}''')
                report['stage']='archive'
                page.goto(native.ARCHIVE,wait_until='domcontentloaded',timeout=60000)
                if page.url!=native.ARCHIVE:raise RuntimeError('Unexpected archive')
                report['native_archive']=page.locator('a[href]').evaluate_all('''(aa,p)=>({matches:aa.filter(a=>a.textContent.trim()===p.title || a.href.includes(p.slug)).map(a=>({label:a.textContent.trim(),href:a.href,rowText:(a.closest('tr')||a.closest('li')||a.parentElement).innerText.slice(0,700)})),editorLinks:aa.filter(a=>a.href.includes('/afp-pipe/post/edit/')).slice(0,15).map(a=>({label:a.textContent.trim(),href:a.href,rowText:(a.closest('tr')||a.closest('li')||a.parentElement).innerText.slice(0,500)}))})''',post)
                page.goto(native.BLOG+'/posts',wait_until='domcontentloaded',timeout=60000)
                report['public_archive_matches']=page.locator('a[href]').evaluate_all('(aa,p)=>aa.filter(a=>a.textContent.trim()===p.title || a.href.includes(p.slug)).map(a=>({title:a.textContent.trim(),href:a.href}))',post)
            finally:browser.close()
    except Exception as exc:
        report['native_diagnostic_error_type']=type(exc).__name__
        message=str(exc).split('Call log:')[0].split('\n')[0]
        for secret in [os.getenv('BLOGSKY_USERNAME',''),os.getenv('BLOGSKY_PASSWORD',''),os.getenv('GH_TOKEN','')]:
            if secret:message=message.replace(secret,'[redacted]')
        report['error_summary']=message[:350]
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
    from blog_generated_image import checkpoint_asset
    checkpoint_asset(str(REPORT.relative_to(ROOT)),REPORT.read_bytes(),ROOT)

if __name__=='__main__':main()
