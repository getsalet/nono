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
    const issues=[];
    for(const x of records.values()){
      const key=String(x.key||x.id||'');if(published.has(key)||x.published===true||x.status==='published')continue;
      const s=String(x.status||x.phase||'');
      if(['ready','approved','completed','generated','draft_saved'].includes(s))counts.ready++;
      if(s==='pending')counts.pending++;
      if(s==='failed'||s==='held'||s==='deferred')counts.failed++;
      if(/^(submitting|unconfirmed|uncertain|request_pending)/.test(s)){counts.ambiguous++;issues.push({key,reason:'ارسال قبلی هنوز نیاز به تطبیق رسید دارد.'});}
    }
    const failures=new Map(Object.entries(state?.failed||{}).filter(([key])=>!published.has(key)));
    for(const [key,v]of Object.entries(state?.held||{}))if(!published.has(key))failures.set(key,v?.reason||v);
    for(const [key,v]of failures)issues.push({key,reason:typeof v==='string'?v:String(v?.last_error||v?.reason||'کنترل کیفیت نیاز به بررسی دارد.')});
    if(state?.intent){counts.ambiguous++;issues.unshift({key:state.intent.key||'',reason:'یک قصد ارسال ثبت‌شده در انتظار تطبیق است؛ ارسال دوباره نکنید.'});}
    for(const [key,x]of Object.entries(journal?.items||journal?.attempts||{}))if(/^(submitting|unconfirmed|uncertain)$/.test(x?.phase||'')){counts.ambiguous++;issues.unshift({key,reason:'دفتر ارسال، رسید حل‌نشده دارد.'});}
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
  function build(c,input={},now=Date.now()) {
    const {state,queue,control,globalControl,automationControl,journal,generation,yaml,runs=[]}=input;
    const pub=publications(c,state,queue,now),q=queueSummary(c,state,queue,journal);
    const relevant=runs.filter(x=>[c.workflow,c.generationWorkflow].filter(Boolean).some(w=>String(x.path||'').split('@')[0].endsWith('/'+w))).sort((a,b)=>(dateMs(b.created_at)||0)-(dateMs(a.created_at)||0));
    const latest=relevant[0]||null,last=pub.rows.find(x=>x.publishedAt!==null)||null;
    const paused=globalControl?.pause_image_production===true || control?.enabled===false || automationControl?.enabled?.[c.id]===false;
    let status={label:'بدون خطای اجرای تازه',tone:'good',message:'در آخرین اجرای مشاهده‌شده خطایی ثبت نشده است؛ انتشارها را جداگانه ببینید.'};
    if(!state)status={label:'داده ناقص',tone:'neutral',message:'فایل رسیدها خوانده نشد؛ صفر پست یا سلامت سیستم فرض نمی‌شود.'};
    else if(paused)status={label:'توقف تنظیم‌شده',tone:'neutral',message:'انتشار طبق تنظیمات متوقف است؛ این توقف لزوماً خطا نیست.'};
    else if(q.ambiguous)status={label:'رسید در انتظار تطبیق',tone:'warn',message:'ارسال قبلی باید با صفحه عمومی تطبیق داده شود؛ ارسال مجدد خودکار راه‌حل نیست.'};
    else if(runState(latest).tone==='bad')status={label:'نیازمند بررسی اجرا',tone:'bad',message:'آخرین اجرای مشاهده‌شده ناموفق بوده است. جزئیات اجرا را باز کنید.'};
    else if(latest?.status==='in_progress'||latest?.status==='queued')status={label:runState(latest).label,tone:'info',message:'اجرا هنوز تمام نشده است؛ نتیجه انتشار پس از ثبت رسید مشخص می‌شود.'};
    else if(!last)status={label:'زمان انتشار نامشخص',tone:'neutral',message:'رسید زمان‌دار معتبری برای آخرین انتشار نداریم؛ این یعنی نبود مدرک، نه نبود پست.'};
    else if(now-last.publishedAt>86400000)status={label:'بدون انتشار تازه',tone:'warn',message:'بیش از ۲۴ ساعت از آخرین انتشار ثبت‌شده می‌گذرد. صف و آخرین اجرا را بررسی کنید؛ این به‌تنهایی اثبات خرابی نیست.'};
    else if(!latest)status={label:'وضعیت اجرا نامشخص',tone:'neutral',message:'رسید انتشار خوانده شد، اما اجرای مرتبط در نمونه API موجود نیست یا API در دسترس نیست.'};
    return {...c,input,pub,q,last,latest,runs:relevant,status,paused,generation,schedules:schedule(yaml),model:String(yaml||'').match(/AGNES_MODEL:\s*['"]?([^\s'"\n]+)/)?.[1]||null,
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
  return {REPO,CONFIG,dateMs,safeUrl,canonicalUrl,publications,queueSummary,schedule,cronDescription,runState,build,relative};
});
