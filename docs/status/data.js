/* Pure public-data model. No credentials, writes, native logins or publications. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.StatusData = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const REPO = 'https://github.com/getsalet/nono';
  const CONFIG = [
    {id:'roya',name:'رویابلاگ',mark:'رو',host:'afp.royablog.ir',url:'https://afp.royablog.ir/',workflow:'roya-backlink-publish.yml',generationWorkflow:'roya-backlink-queue.yml',state:'state/roya-backlink-progress.json',queue:'data/roya/backlink-queue.json'},
    {id:'farsiblog',name:'فارسی‌بلاگ',mark:'فا',host:'afp.farsiblog.com',url:'https://afp.farsiblog.com/',workflow:'farsiblog-content.yml',state:'state/farsiblog-backlink-progress.json',queue:'data/farsiblog/backlink-queue.json'},
    {id:'rozblog',name:'رزبلاگ',mark:'رز',host:'afp-pipe.rozblog.com',url:'https://afp-pipe.rozblog.com/',workflow:'rozblog-content.yml',state:'state/rozblog-backlink-progress.json',queue:'data/rozblog/backlink-queue.json'},
    {id:'loxblog',name:'لوکس‌بلاگ',mark:'لو',host:'afp.lxb.ir',url:'https://afp.lxb.ir/',workflow:'loxblog-content.yml',state:'state/loxblog-backlink-progress.json',queue:'data/loxblog/backlink-queue.json',control:'data/loxblog/deployment-control.json',journal:'artifacts/loxblog-backlink-queue/submission-attempts.json'},
    {id:'blogsky',name:'بلاگ‌اسکای',mark:'بـ',host:'afp-pipe.blogsky.com',url:'https://afp-pipe.blogsky.com/',workflow:'blogsky-auto.yml',state:'state/blogsky-backlink-progress.json',queue:'data/blogsky/backlink-queue.json',control:'data/blogsky/native-publication-control.json'},
    {id:'parsiblog',name:'پارسی‌بلاگ',mark:'پا',host:'afp.parsiblog.com',url:'http://afp.parsiblog.com/',workflow:'parsiblog-content.yml',state:'state/parsiblog-progress.json',queue:'data/parsiblog/title-matrix.json',control:'data/parsiblog/control.json'},
    {id:'niloblog',name:'نیلوبلاگ',mark:'نی',host:'afp.niloblog.com',url:'https://afp.niloblog.com/',workflow:'niloblog-content.yml',state:'data/niloblog/runtime-state.json',queue:'data/niloblog/title-matrix.json',control:'data/niloblog/runtime-control.json'}
  ];
  function dateMs(value) {
    if(typeof value !== 'string' || !/(Z|[+-]\d{2}:\d{2})$/i.test(value)) return null;
    const ms=Date.parse(value); return Number.isFinite(ms) ? ms : null;
  }
  function safeUrl(value, host) {
    try { const u=new URL(value); if(!['https:','http:'].includes(u.protocol)||u.username||u.password||(host&&u.hostname.toLowerCase()!==host))return ''; return u.href; } catch {return '';}
  }
  function canonicalUrl(value) {
    try {const u=new URL(value); let path=u.pathname;try{path=decodeURIComponent(path);}catch{}return u.hostname.toLowerCase()+path.replace(/\/+$/,'');}catch{return '';}
  }
  function values(obj) {return obj && typeof obj === 'object' ? Object.values(obj) : [];}
  function titleFallback(row) {
    try {const u=new URL(row.url);const tail=decodeURIComponent(u.pathname.split('/').filter(Boolean).pop()||'').replace(/[+-]/g,' ');if(/[\u0600-\u06ff]/.test(tail))return tail;}catch{}
    const ordinal=String(row.url||'').match(/\/(?:post[-\/]|Posts\/|p\/)(\d+)/i);
    return 'پست '+(ordinal?.[1]||row.pid||'ثبت‌شده');
  }
  function publications(c,state,queue,now=Date.now()) {
    if(!state || !Array.isArray(state.published))return {rows:[],total:null,invalid:0};
    const titles=new Map(values(queue?.items).map(x=>[String(x.key||x.id),x.title||x.assigned_title||x.matrix_title||'']));
    const groups=[],byKey=new Map(),byUrl=new Map();let invalid=0;
    for(const x of state.published) {
      if(!x || typeof x!=='object'){invalid++;continue;}
      const url=safeUrl(x.url,c.host);if(!url||new URL(url).pathname==='/'){invalid++;continue;}
      const key=String(x.key||''),canon=canonicalUrl(url);
      let group=(key&&byKey.get(key))||byUrl.get(canon);
      if(!group){group={key,url,pid:x.pid||x.id,dates:[],recovered:false,title:'',verifiedAt:null};groups.push(group);}
      if(key)byKey.set(key,group);byUrl.set(canon,group);
      const time=dateMs(x.original_published_at||x.published_at||x.at);
      if(time!==null && time<=now+120000)group.dates.push(time);
      if(x.recovered_existing===true && !x.original_published_at)group.recovered=true;
      const verified=dateMs(x.at);if(verified!==null)group.verifiedAt=Math.max(group.verifiedAt||0,verified);
      group.title=x.title||state.items?.[key]?.title||titles.get(key)||group.title;
    }
    const rows=groups.map(g=>({...g,publishedAt:g.recovered?null:(g.dates.length?Math.min(...g.dates):null),title:g.title||titleFallback(g)}));
    rows.sort((a,b)=>(b.publishedAt??-1)-(a.publishedAt??-1));
    return {rows,total:rows.length,invalid};
  }
  function queueSummary(c,state,queue,journal) {
    const published=new Set((state?.published||[]).map(x=>String(x?.key||'')));
    const items=values(queue?.items);for(const x of items)if(published.has(String(x.key||x.id||''))&&x.source_key)published.add(String(x.source_key));const records=new Map(items.map(x=>[String(x.key||x.id),x]));
    for(const [key,x]of Object.entries(state?.items||{}))records.set(key,{...(records.get(key)||{}),...x,key});
    const counts={ready:0,pending:0,failed:0,ambiguous:0};
    const issues=[],ambiguousKeys=new Set();
    for(const x of records.values()){
      const key=String(x.key||x.id||'');if(published.has(key)||x.published===true||x.status==='published')continue;
      const s=String(x.status||x.phase||'');
      if(['ready','approved','completed','generated','draft_saved'].includes(s))counts.ready++;
      if(s==='pending')counts.pending++;
      if(s==='failed'||s==='held'||s==='deferred')counts.failed++;
      if(/^(submitting|unconfirmed|uncertain|request_pending)/.test(s)){ambiguousKeys.add(key||'record:unknown');issues.push({key,reason:'ارسال قبلی هنوز نیاز به تطبیق رسید دارد.'});}
    }
    const failures=new Map(Object.entries(state?.failed||{}).filter(([key])=>!published.has(key)));
    for(const [key,v]of Object.entries(state?.held||{}))if(!published.has(key))failures.set(key,v?.reason||v);
    for(const [key,v]of failures)issues.push({key,reason:typeof v==='string'?v:String(v?.last_error||v?.reason||'کنترل کیفیت نیاز به بررسی دارد.')});
    if(state?.intent){ambiguousKeys.add(state.intent.key||'intent:unknown');issues.unshift({key:state.intent.key||'',reason:'یک قصد ارسال ثبت‌شده در انتظار تطبیق است؛ ارسال دوباره نکنید.'});}
    for(const [key,x]of Object.entries(journal?.items||journal?.attempts||journal||{}))if(/^(submitting|unconfirmed|uncertain|reconciled_absent)$/.test(x?.phase||'')){ambiguousKeys.add(key||'journal:unknown');issues.unshift({key,reason:'دفتر ارسال، رسید حل‌نشده دارد.'});}
    counts.ambiguous=ambiguousKeys.size;
    counts.failed=Math.max(counts.failed,failures.size);
    return {...counts,loaded:!!queue,total:queue?items.length:null,issues};
  }
  function schedule(yaml) {return [...String(yaml||'').matchAll(/cron:\s*['"]([^'"]+)['"]/g)].map(m=>m[1]);}
  function cronDescription(cron) {
    const p=String(cron).trim().split(/\s+/);if(p.length!==5)return 'برنامه زمان‌بندی سفارشی';
    if(p.slice(1).every(x=>x==='*')){
      const step=p[0].match(/^\*\/(\d+)$/);if(step)return 'هر '+Number(step[1])+' دقیقه';
      const minutes=p[0].split(',').map(Number);
      if(minutes.every(n=>Number.isInteger(n)&&n>=0&&n<60)){
        if(minutes.length===1)return 'هر ساعت، دقیقه '+minutes[0];
        const gaps=minutes.map((n,i)=>(minutes[(i+1)%minutes.length]+(i===minutes.length-1?60:0))-n);
        if(gaps.every(n=>n===gaps[0]))return 'هر '+gaps[0]+' دقیقه';
      }
    }
    return 'برنامه زمان‌بندی سفارشی';
  }
  function runState(run) {
    if(!run)return {label:'اطلاعات اجرا در دسترس نیست',tone:'neutral'};
    if(run.status==='queued')return {label:'در صف اجرا',tone:'info'};
    if(run.status==='in_progress'||run.status==='waiting')return {label:'در حال اجرا',tone:'info'};
    return ({success:{label:'اجرای موفق',tone:'good'},failure:{label:'اجرای ناموفق',tone:'bad'},cancelled:{label:'لغوشده',tone:'neutral'},skipped:{label:'اجرا نشده',tone:'neutral'},timed_out:{label:'پایان مهلت اجرا',tone:'bad'},action_required:{label:'نیازمند اقدام',tone:'warn'}})[run.conclusion]||{label:'وضعیت نامشخص',tone:'neutral'};
  }
  function generationPath(c) {return c.id==='niloblog'?'artifacts/niloblog/run-status.json':c.id==='parsiblog'?'artifacts/parsiblog-backlink-queue/run-report.json':'artifacts/'+c.id+'-backlink-queue/generation-status.json';}
  function runReportPath(c){return 'artifacts/blog-run-reports/'+c.id+'/latest.json';}
  function matchedRunReport(c,input,latest){
    const r=input.runReport;
    return r?.schema==='blog-run-report-v1'&&r.blog===c.id&&latest&&String(r.run_id)===String(latest.id)&&Number(r.run_attempt)===Number(latest.run_attempt||1)&&r.workflow_path===String(latest.path||'').split('@')[0]&&r.workflow_conclusion===latest.conclusion&&dateMs(r.completed_at)!==null&&dateMs(latest.updated_at)!==null&&Math.abs(dateMs(r.completed_at)-dateMs(latest.updated_at))<=120000?r:null;
  }
  function issueAdvice(reason) {
    const text=String(reason||'');
    if(/visual_challenge|captcha|کپچا/i.test(text))return {category:'login',label:'ورود / کپچا',action:'گزارش ورود را بررسی کنید؛ پس از رفع علت، فقط یک آزمون ورود بدون انتشار اجرا کنید.'};
    if(/authentication|credential|login rejected|unauthorized|Missing.*secret/i.test(text))return {category:'login',label:'ورود / دسترسی',action:'اعتبار دسترسی را در تنظیمات امن گیت‌هاب بررسی کنید؛ رمز یا کلید را در پنل وارد نکنید.'};
    if(/unconfirmed|uncertain|reconciliation|تطبیق|قصد ارسال|رسید حل/i.test(text))return {category:'receipt',label:'رسید نامشخص',action:'ابتدا آرشیو بومی و صفحه عمومی را تطبیق دهید؛ تا تعیین نتیجه، مطلب را دوباره ارسال نکنید.'};
    if(/hourly|rolling.*limit|budget|rate.limit|429/i.test(text))return {category:'limit',label:'محدودیت / سهمیه',action:'زمان مجاز تلاش بعدی و نوع محدودیت را بررسی کنید؛ سقف انتشار را دور نزنید.'};
    if(/image|تصویر/i.test(text))return {category:'image',label:'مرحله تصویر',action:'موجودی تصویر و گزارش تأیید تصویر را بررسی کنید؛ تصویر ردشده را بدون تأیید منتشر نکنید.'};
    if(/quality|preflight|editorial|evidence|claim|word count|foreign.language|کنترل کیفیت|Text validation/i.test(text))return {category:'quality',label:'رد کنترل کیفیت',action:'فقط پیش‌نویس و شواهد همان مورد را اصلاح و دوباره ارزیابی کنید؛ کنترل کیفیت را غیرفعال نکنید.'};
    return {category:'unknown',label:'علت فنی نیازمند بررسی',action:'مرحله ناموفق و پیام خطا را در گزارش اجرا بررسی کنید؛ از روی رنگ اجرا علت را حدس نزنید.'};
  }
  function diagnosis(c,input,pub,q,last,latest,paused,now) {
    const result=(code,label,tone,message,action,evidence,source,confidence='ثبت‌شده',observedAt=null)=>({code,label,tone,message,action,evidence,source,confidence,observedAt});
    const file=p=>REPO+'/blob/'+(input.revision||'main')+'/'+p;
    const runUrl=safeUrl(latest?.html_url)||REPO+'/actions/workflows/'+c.workflow;
    const gen=input.generation,at=dateMs(gen?.completed_at||gen?.updated_at||gen?.at),start=dateMs(latest?.run_started_at||latest?.created_at),end=dateMs(latest?.updated_at);
    // A report is not the cause of a later run unless its run ID matches or its
    // timestamp falls inside that run. Old held drafts are background, not outages.
    const sameRun=!!latest && (gen?.run_id?String(gen.run_id)===String(latest.id):at!==null&&start!==null&&end!==null&&at>=start&&at<=end+120000);
    const current=sameRun&&at!==null&&at<=now+120000;
    if(!input.state||input.stale)return result('data_missing',input.stale?'داده قبلی':'داده ناقص','neutral','تازگی فایل رسید تأیید نشده است؛ وضعیت سلامت قابل نتیجه‌گیری نیست.','خواندن منابع را تازه‌سازی کنید؛ در صورت تداوم خطا، منبع رسید را مستقیم باز کنید.',input.stale?'خواندن نسخه فعلی ناموفق؛ داده قبلی حفظ شده است.':'فایل رسید خوانده نشد.',file(c.state),'نامشخص');
    if(paused)return result('paused','توقف تنظیم‌شده','neutral','توقف از تنظیمات خوانده شده؛ خطای جنراتور فرض نمی‌شود.','اگر توقف عمدی است، اقدامی لازم نیست؛ فقط با مجوز، تنظیم توقف را تغییر دهید.','حداقل یک کنترل توقف فعال است.',file(input.control?.enabled===false?c.control:input.automationControl?.enabled?.[c.id]===false?'data/blog-automation-control.json':'data/blog-generated-image-control.json'));
    if(q.ambiguous)return result('receipt','رسید در انتظار تطبیق','warn','برای یک ارسال قبلی هنوز نتیجه قطعی نداریم.',issueAdvice('reconciliation').action,'قصد ارسال یا وضعیت حل‌نشده در دفتر ارسال ثبت شده است.',file(c.journal||c.state));
    if(current && (gen.status==='failed'||gen.reason||gen.error_type) && runState(latest).tone==='bad') {
      const reason=String(gen.reason||(Array.isArray(gen.qa_errors)?gen.qa_errors:[]).join('؛ ')||gen.error_type||'');const a=issueAdvice(reason);
      return result(a.category,a.label,'bad',a.category==='quality'?'این اجرا در کنترل کیفیت متوقف شد؛ این مدرک خرابی کل جنراتور نیست.':'گزارش همین اجرا یک مانع ثبت کرده است.',a.action,reason||'گزارش اجرا ناموفق است.',file(generationPath(c)),'همین اجرا',at);
    }
    const observed=matchedRunReport(c,input,latest);
    if(observed && runState(latest).tone==='bad'){
      const causes={quality:'رد کنترل کیفیت',login:'ورود / دسترسی',receipt:'رسید نامشخص',limit:'محدودیت / سهمیه',image:'مرحله تصویر'};
      const hints={quality:'quality',login:'authentication',receipt:'reconciliation',limit:'budget',image:'image'};
      const stages={generation:'تولید',publication:'انتشار / تأیید بومی',dependencies:'نصب وابستگی‌ها',tests:'آزمون‌ها',checkpoint:'ذخیره رسیدها',admission:'بررسی اجازه اجرا',unknown:'مرحله نامشخص'};
      const cause=Object.hasOwn(causes,observed.reason_code)?observed.reason_code:'unknown';
      return result(cause==='unknown'?'run_failed':cause,causes[cause]||'اجرای ناموفق؛ علت نامشخص','bad','مرحله توقف ثبت‌شده: '+(stages[observed.phase]||'نامشخص')+'؛ '+(cause==='unknown'?'متن لاگ خوانده نشده و علت دقیق مشخص نیست.':'علت از گزارش مرتبط همین اجرا دسته‌بندی شده است.'),issueAdvice(hints[cause]||'').action,'گزارش یکپارچه اجرا '+String(observed.run_id)+'، نوبت '+String(observed.run_attempt)+'؛ نتیجه: '+String(observed.workflow_conclusion),file(runReportPath(c)),cause==='unknown'?'مرحله مشخص؛ علت نامشخص':'همین اجرا',dateMs(observed.completed_at));
    }
    if(runState(latest).tone==='bad')return result('run_failed','نیازمند بررسی اجرا','bad','آخرین اجرای مرتبط ناموفق است؛ علت دقیق از این داده‌ها مشخص نیست.',issueAdvice('').action,'نتیجه workflow: '+String(latest.conclusion),runUrl,'علت نامشخص',dateMs(latest.updated_at));
    if(['queued','in_progress','waiting'].includes(latest?.status))return result('running',runState(latest).label,'info','این اجرا هنوز تمام نشده است؛ انتشار فقط با رسید تأیید می‌شود.','تا پایان اجرا صبر کنید؛ سپس رسید و نتیجه همان اجرا را بررسی کنید.','وضعیت workflow: '+latest.status,runUrl,'ثبت‌شده',dateMs(latest.updated_at));
    const limit=Number(input.control?.rolling_hourly_limit||input.control?.max_verified_posts_per_rolling_hour);
    const recent=pub.rows.filter(x=>x.publishedAt!==null&&x.publishedAt>now-3600000&&x.publishedAt<=now);
    if(Number.isInteger(limit)&&limit>0&&recent.length>=limit){const next=recent.map(x=>x.publishedAt).sort((a,b)=>b-a)[limit-1]+3600000;
      return {...result('budget','سقف ساعتی پر است','info','تعداد رسیدهای یک ساعت اخیر به سقف صریح فایل کنترل رسیده است؛ این خطا نیست.','تا آزادشدن ظرفیت صبر کنید؛ اجرای دستی محدودیت را دور نمی‌زند.','رسیدهای یک ساعت اخیر: '+recent.length+'؛ سقف تنظیم‌شده: '+limit,file(c.control),'محاسبه از رسیدها'),retryAt:next};}
    if(current && ['waiting_image','waiting_provider'].includes(gen?.status))return result('waiting',gen.status==='waiting_image'?'در انتظار تصویر':'در انتظار سرویس تولید','info','آخرین گزارش مرتبط، انتظار را ثبت کرده است؛ انتشار تأیید نشده است.','گزارش سرویس و زمان مجاز تلاش بعدی را بررسی کنید؛ ارسال موازی راه نیندازید.','وضعیت گزارش: '+gen.status,file(generationPath(c)),'همین اجرا',at);
    if(current && gen?.status==='idle')return result('idle','بدون کار آماده','info','گزارش همین اجرا حالت بی‌کاری را ثبت کرده است؛ خالی بودن کل صف هنوز اثبات نمی‌شود.','صف را باز کنید: موضوع در انتظار، پیش‌نویس آماده و موارد ردشده را جداگانه بررسی کنید.','گزارش تولید: idle؛ '+(q.loaded?'جزئیات صف خوانده شده است.':'جزئیات صف هنوز خوانده نشده است.'),file(generationPath(c)),'همین اجرا',at);
    if(q.loaded&&q.total===0)return result('empty_queue','صف موضوع خالی است','info','فایل صف خوانده شده و هیچ موضوعی ندارد.','در صورت نیاز، موضوع‌های مجاز جدید به صف اضافه کنید؛ اجرای مجدد به‌تنهایی کاری تولید نمی‌کند.','تعداد موضوع‌های فایل صف: ۰',file(c.queue));
    if(!last)return result('publication_unknown','زمان انتشار نامشخص','neutral','رسید زمان‌دار معتبر برای آخرین انتشار نداریم.','آرشیو عمومی و رسیدها را تطبیق دهید؛ نبود مدرک را نبود پست فرض نکنید.','رسید زمان‌دار معتبر موجود نیست.',file(c.state),'نامشخص');
    if(now-last.publishedAt>86400000)return result('stale_publication','بدون انتشار تازه','warn','بیش از ۲۴ ساعت از آخرین انتشار ثبت‌شده گذشته است؛ علت هنوز معلوم نیست.','صف و گزارش آخرین اجرا را باز کنید؛ پیش از تشخیص علت، تولید یا ارسال تکراری نکنید.','آخرین زمان انتشار از رسید اتوماسیون خوانده شده است.',file(c.state),'نیازمند بررسی',last.publishedAt);
    if(!latest)return result('run_unknown','وضعیت اجرا نامشخص','neutral','رسید انتشار خوانده شده، اما اجرای مرتبط در نمونه API موجود نیست.','برای نتیجه اجرا، GitHub Actions را مستقیم بررسی کنید.','نمونه اجراهای مرتبط در دسترس نیست.',runUrl,'نامشخص');
    return result('recent_receipt','انتشار تازه ثبت شده','good','رسید انتشار در ۲۴ ساعت اخیر وجود دارد؛ این تضمین سلامت همه اجراها نیست.','فعلاً اقدام فوری لازم نیست؛ روند انتشار و خطاهای بعدی را دنبال کنید.','رسید زمان‌دار انتشار موجود است.',last.url,'رسید انتشار',last.publishedAt);
  }
  function build(c,input={},now=Date.now()) {
    const {state,queue,control,globalControl,automationControl,journal,generation,yaml,runs=[]}=input;
    const pub=publications(c,state,queue,now),q=queueSummary(c,state,queue,journal);
    const relevant=runs.filter(x=>[c.workflow,c.generationWorkflow].filter(Boolean).some(w=>String(x.path||'').split('@')[0].endsWith('/'+w))).sort((a,b)=>(dateMs(b.created_at)||0)-(dateMs(a.created_at)||0));
    const latest=relevant[0]||null,last=pub.rows.find(x=>x.publishedAt!==null)||null;
    const paused=globalControl?.pause_image_production===true || control?.enabled===false || automationControl?.enabled?.[c.id]===false;
    const status=diagnosis(c,input,pub,q,last,latest,paused,now);
    return {...c,input,pub,q,last,latest,runReport:matchedRunReport(c,input,latest),runs:relevant,status,paused,generation,schedules:schedule(yaml),model:String(yaml||'').match(/AGNES_MODEL:\s*['"]?([^\s'"\n]+)/)?.[1]||null,
      today:pub.total===null?null:pub.rows.filter(x=>x.publishedAt!==null&&x.publishedAt>now-86400000&&x.publishedAt<=now).length,
      week:pub.total===null?null:pub.rows.filter(x=>x.publishedAt!==null&&x.publishedAt>now-7*86400000&&x.publishedAt<=now).length};
  }
  function relative(value,now=Date.now()) {
    if(value===null||value===undefined)return 'زمان نامشخص';
    const ms=typeof value==='number'?value:dateMs(value);if(ms===null)return 'زمان نامشخص';
    const s=Math.floor((now-ms)/1000);if(s<0)return s>=-120?'همین حالا':'زمان در آینده';
    if(s<60)return 'کمتر از یک دقیقه پیش';const m=Math.floor(s/60);if(m<60)return m+' دقیقه پیش';
    const h=Math.floor(m/60);if(h<24)return h+' ساعت'+(m%60?' و '+m%60+' دقیقه':'')+' پیش';
    const d=Math.floor(h/24);return d+' روز'+(h%24?' و '+h%24+' ساعت':'')+' پیش';
  }
  return {REPO,CONFIG,generationPath,runReportPath,matchedRunReport,issueAdvice,diagnosis,dateMs,safeUrl,canonicalUrl,publications,queueSummary,schedule,cronDescription,runState,build,relative};
});
