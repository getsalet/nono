"""User-authorized generator removal and bounded fixes; no provider or blog I/O."""
import ast,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def edit(path,old,new):
 p=ROOT/path;s=p.read_text()
 if old in new and new in s:return
 if old in s:p.write_text(s.replace(old,new))
 elif new not in s:raise RuntimeError('Patch context changed: '+path)
def main():
 tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines();removed=[]
 exact={'.github/workflows/retire-blogfa.yml','automation/publish_blogfa_posts.py','state/blogfa-backlink-progress.json'}
 prefixes=('automation/blogfa_','tests/test_blogfa_','data/blogfa/','artifacts/blogfa-backlink-queue/','artifacts/blog-run-reports/blogfa/','templates/blogfa/','design-system/afp-blogfa/')
 for path in tracked:
  p=ROOT/path
  if path in exact or path.startswith(prefixes)or(path.startswith('.github/workflows/blogfa-')and path.endswith('.yml'))or(path.startswith('data/blog-image-stock/requests/')and p.exists()and json.loads(p.read_text()).get('blog')=='blogfa'):
   if p.exists():p.unlink()
   removed.append(path)
 # Published asset URLs and Git history are intentionally retained. No native account access.
 p=ROOT/'data/blog-city-title-matrix.json';obj=json.loads(p.read_text())
 def clean(v):
  if isinstance(v,dict):return {k:clean(x)for k,x in v.items()if k!='blogfa'and not k.startswith('blogfa_')}
  if isinstance(v,list):return [clean(x)for x in v if not(isinstance(x,dict)and x.get('blog')=='blogfa')]
  return v
 p.write_text(json.dumps(clean(obj),ensure_ascii=False,indent=2)+'\n')
 # Remove active routing, retaining explicit deny guards for obsolete callers.
 for path in ('automation/city_backlink_policy.py','automation/blog_generated_image.py','automation/blog_generation_status.py'):
  p=ROOT/path;s=p.read_text()
  if path.endswith('city_backlink_policy.py'):
   lines=s.splitlines(True)
   for i,line in enumerate(lines):
    if line.startswith(('BLOGS=','ANGLES=')):
     name,value=line.split('=',1);d=ast.literal_eval(value.strip());d.pop('blogfa',None);lines[i]=name+'='+repr(d)+'\n'
   s=''.join(lines).replace(' + Blogfa','')
  elif path.endswith('blog_generated_image.py'):s=s.replace("'rozblog','blogfa','loxblog'","'rozblog','loxblog'")
  else:s=s.replace("'blogfa':'بلاگفا',",'')
  p.write_text(s)
 edit('automation/content_originality.py',"for blog in ('roya','farsiblog','rozblog','blogfa','loxblog','blogsky'):","for blog in ('roya','farsiblog','rozblog','loxblog','blogsky'):")
 edit('automation/check_blog_run_budget.py',"('farsiblog','rozblog','blogfa','loxblog','blogsky')","('farsiblog','rozblog','loxblog','blogsky')")
 edit('automation/check_blog_run_budget.py',"if blog in ('blogfa','loxblog'):","if blog == 'loxblog':")
 edit('automation/check_blog_pipeline_control.py',"BLOGS=('roya','farsiblog','rozblog','blogfa','loxblog','blogsky')","BLOGS=('roya','farsiblog','rozblog','loxblog','blogsky')")
 edit('automation/check_blog_pipeline_control.py'," if blog not in BLOGS:raise ValueError('Unsupported blog')"," if blog=='blogfa':return {'blog':blog,'proceed':False,'reason':'blog_removed_by_user','publication_attempted':False}\n if blog not in BLOGS:raise ValueError('Unsupported blog')")
 edit('automation/check_blog_pipeline_control.py',"any(b not in BLOGS for b in retired)","any(b not in (*BLOGS,'blogfa') for b in retired)")
 for path in ('.github/workflows/niloblog-content.yml','.github/workflows/niloblog-validation.yml'):
  p=ROOT/path;p.write_text(''.join(line for line in p.read_text().splitlines(True)if 'artifacts/blogfa-backlink-queue/items'not in line))
 edit('.github/workflows/blog-generator-control-audit.yml','roya farsiblog rozblog blogfa loxblog','roya farsiblog rozblog loxblog')
 edit('.github/workflows/stop-rejected-image-runs.yml',"'blogfa-content.yml',",'')
 # Fix exactly the known model placeholder markup, not arbitrary unsupported tags.
 edit('automation/parsiblog_text.py'," if isinstance(body,str)and _CITY_TOKEN_RE.search(body):",''' if isinstance(body,str):
  # Empty exact placeholder tags represent a matrix locality, not an HTML element.
  # Attributed/nonempty/unknown elements remain untouched and fail normal HTML QA.
  empty=re.compile(r'<AFP_CITY\\s*>\\s*</AFP_CITY\\s*>|<AFP_CITY\\s*/>',re.I)
  body,n=empty.subn(lambda m:__import__('html').escape(city),body);count+=n
  if not re.search(r'</AFP_CITY\\s*>',body,re.I):
   body,n=re.subn(r'<AFP_CITY\\s*>',lambda m:__import__('html').escape(city),body,flags=re.I);count+=n
  post['html']=body
 if isinstance(body,str)and any(_CITY_TOKEN_RE.search(part)for part in re.split(r'(<[^>]*>)',body)[::2]):''')
 # Supply precise feedback rather than teaching the model to add unsupported tags.
 edit('automation/parsiblog_pipeline.py',"request=base\n", "request=base+'\\nتوکن شهر AFP_CITY فقط متن ساده است؛ آن را داخل <> یا تگ HTML ننویس. <AFP_CITY> ممنوع است.'\n")
 # HTTP 429 is not malformed JSON: propagate it without changing key or rewriting prose.
 for path in ('automation/agnes_json_client.py','automation/roya_backlink_queue.py'):
  edit(path,'   last=exc\n'if path.endswith('agnes_json_client.py')else'            last = exc\n',('   'if path.endswith('agnes_json_client.py')else'            ')+"if getattr(exc,'http_status',None)==429 or getattr(exc,'code',None)==429:raise\n"+('   last=exc\n'if path.endswith('agnes_json_client.py')else'            last = exc\n'))
 edit('automation/farsiblog_backlink_queue.py',"        except (TimeoutError,urllib.error.URLError,RuntimeError) as exc:\n", "        except (TimeoutError,urllib.error.URLError,RuntimeError) as exc:\n            if getattr(exc,'http_status',None)==429 or getattr(exc,'code',None)==429:raise\n")
 edit('automation/roya_backlink_queue.py',"                errors = ['agnes error: ' + str(exc)[:200]]", "                text_rate_limited=getattr(exc,'http_status',None)==429 or getattr(exc,'code',None)==429\n                errors = ['agnes error: ' + str(exc)[:200]]")
 edit('automation/roya_backlink_queue.py',"                if stage=='image':break", "                if stage=='image' or text_rate_limited:break")
 edit('automation/roya_backlink_queue.py',"        if shared_image_deferred and not stock_pending:break", "        if errors and any('Agnes/provider HTTP 429;'in error for error in errors):break\n        if shared_image_deferred and not stock_pending:break")
 edit('automation/farsiblog_backlink_queue.py',"        if provider_busy and not isinstance(exc_pending,ImagePending):break", "        if text_rate_limited:break\n        if provider_busy and not isinstance(exc_pending,ImagePending):break")
 edit('automation/farsiblog_backlink_queue.py',"        provider_busy=False;exc_pending=None", "        provider_busy=False;exc_pending=None;text_rate_limited=False")
 edit('automation/farsiblog_backlink_queue.py',"            provider_busy=isinstance(exc,(ImageProviderBusy,ImageQueueBusy));exc_pending=exc if isinstance(exc,ImagePending)else None", "            text_rate_limited=getattr(exc,'http_status',None)==429 or getattr(exc,'code',None)==429\n            provider_busy=isinstance(exc,(ImageProviderBusy,ImageQueueBusy));exc_pending=exc if isinstance(exc,ImagePending)else None")
 for path in ('tests/test_blog_image_stock.py','tests/test_blog_stock_capacity_preflight.py'):
  p=ROOT/path;p.write_text(p.read_text().replace("'roya','farsiblog','rozblog','blogfa'","'roya','farsiblog','rozblog','blogsky'"))
 # Tests that formerly exercised a positive Blogfa path now use an active adapter.
 for path in ('tests/test_blog_budget_preflight_pipeline.py',):
  p=ROOT/path;p.write_text(p.read_text().replace('blogfa','loxblog'))
 p=ROOT/'tests/test_loxblog_pipeline.py';s=p.read_text().replace("('blogfa','farsiblog','rozblog')","('farsiblog','rozblog')").replace("budget.decision('blogfa'","budget.decision('farsiblog'");p.write_text(s)
 for path in ('tests/test_blog_pipeline_stop.py','tests/test_blog_key10_activation.py','tests/test_blog_image_queue.py','tests/test_blog_image_key_router.py','tests/test_blog_hose_diagnostic_scope.py'):
  p=ROOT/path;s=p.read_text().replace("'publish_blogfa_posts',",'').replace("('blogfa-content','blogfa'),",'').replace("'blogfa-content.yml',",'').replace("'blogfa-content',",'');p.write_text(s)
 edit('tests/test_blog_image_backpressure.py',"('roya','farsiblog','rozblog','blogfa','loxblog')","('roya','farsiblog','rozblog','loxblog')")
 report={'policy':'remove-blogfa-runtime-v1','removed_paths':removed,'removed_count':len(removed),'preserved':['published immutable image assets','Git history','explicit deny tombstones'],'native_account_contacted':False,'live_generation_triggered':False}
 (ROOT/'docs/generator-removal-repair-2026-10-30.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('Removal plan applied:',len(removed),'tracked paths; published assets retained; no network requests.')
if __name__=='__main__':main()
