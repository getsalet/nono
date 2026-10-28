// Optional browser regression: node tests/status_priorities.browser.cjs
// Requires Playwright and Chromium; all remote responses are controlled fixtures.
const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const D=require('../docs/status/data.js'),root=path.resolve(__dirname,'../docs/status');
(async()=>{
 const server=http.createServer((req,res)=>{const name=req.url.split('?')[0].replace(/^\/status\/?/,'')||'index.html';if(!['index.html','app.js','data.js','styles.css','fonts/vazir.css','fonts/OFL.txt'].includes(name)){res.writeHead(404);res.end();return;}res.setHeader('Content-Type',name.endsWith('.js')?'application/javascript':name.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(path.join(root,name)));});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,headless:true,args:['--no-sandbox']});
 try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const now=Date.now(),iso=ms=>new Date(ms).toISOString();let sha='a'.repeat(40);
 let failReceipt=false,failQueue=false,delayQueues=true;
 const counts=new Map();
 const fulfill=(route,data,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(data)});
 await page.route('https://api.github.com/**',route=>{
   if(route.request().url().includes('/commits?'))return fulfill(route,[{sha,commit:{message:'fixture',committer:{date:iso(now)}},html_url:'https://github.com/getsalet/nono/commit/'+sha}]);
   return fulfill(route,{workflow_runs:D.CONFIG.map((c,i)=>({id:i+1,path:'.github/workflows/'+c.workflow,status:'in_progress',created_at:iso(now),updated_at:iso(now),html_url:'https://github.com/getsalet/nono/actions/runs/'+(i+1)}))});
 });
 await page.route('https://raw.githubusercontent.com/**',async route=>{
   const file=route.request().url().split('/'+sha+'/')[1];counts.set(file,(counts.get(file)||0)+1);
   const c=D.CONFIG.find(c=>c.state===file||c.queue===file);
   if(c&&file===c.state){if(failReceipt&&c.id==='blogsky')return fulfill(route,{},503);return fulfill(route,{published:[{key:c.id+'-item',url:c.url+'post/1',at:iso(now-(c.id==='blogsky'?3*86400000:3600000)),...(c.id==='roya'?{recovered_existing:true}:{})}]});}
   if(c&&file===c.queue){if(delayQueues)await new Promise(resolve=>setTimeout(resolve,350));if(failQueue&&c.id==='farsiblog')return fulfill(route,{},503);return fulfill(route,{items:[{key:c.id+'-item',assigned_title:'عنوان اختصاصی '+c.id,status:'published'}]});}
   if(file?.endsWith('.yml'))return route.fulfill({status:200,contentType:'text/plain',body:"schedule:\n - cron: '*/15 * * * *'"});
   if(file==='data/blog-generated-image-control.json')return fulfill(route,{pause_image_production:false});
   if(file==='data/blog-automation-control.json')return fulfill(route,{enabled:{}});
   return fulfill(route,{},404);
 });
 const base='http://127.0.0.1:'+server.address().port+'/status/';
 await page.goto(base+'#publications');
 await page.getByText('در حال تکمیل عنوان‌ها',{exact:false}).waitFor();
 await page.getByText('عنوان همه رسیدهای موجود بارگذاری شد.',{exact:true}).waitFor();
 await page.evaluate(()=>document.fonts.ready);assert(await page.evaluate(()=>document.fonts.check('600 16px Vazir','سلام ۱۲۳')));assert((await page.locator('body').evaluate(el=>getComputedStyle(el).fontFamily)).includes('Vazir'));
 if(process.env.AFP_PREVIEW_HTML){const rendered=await page.content();fs.writeFileSync(process.env.AFP_PREVIEW_HTML,rendered.replace(/<script[\s\S]*?<\/script>/g,'').replace(/<link[^>]*rel="stylesheet"[^>]*>/g,'')+'<style>'+fs.readFileSync(path.join(root,'fonts/vazir.css'),'utf8')+fs.readFileSync(path.join(root,'styles.css'),'utf8')+'</style>');}
 assert(D.CONFIG.every(c=>counts.get(c.queue)===1),'all title queues automatically loaded once');
 const search=page.getByRole('searchbox',{name:'جست‌وجو در انتشارها',exact:true});
 await search.fill('  عنوان اختصاصی blogsky  ');
 assert.equal(await page.locator('.post-table tbody tr').count(),1);
 await page.getByRole('link',{name:'عنوان اختصاصی blogsky ↗',exact:true}).waitFor();
 const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'دریافت CSV'}).click();const dl=await downloadPromise;const stream=await dl.createReadStream();let csv='';for await(const chunk of stream)csv+=chunk.toString();assert(csv.includes('عنوان اختصاصی blogsky'));assert(!csv.includes('عنوان اختصاصی roya'));
 await search.fill('');
 if(process.env.AFP_SCREENSHOT_DIR){fs.mkdirSync(process.env.AFP_SCREENSHOT_DIR,{recursive:true});await page.screenshot({path:path.join(process.env.AFP_SCREENSHOT_DIR,'publications.png')});}
 await page.locator('nav a[href="#overview"]').click();await page.locator('.blog-table').waitFor();
 const blogRow=page.locator('.blog-table tbody tr').filter({hasText:'afp-pipe.blogsky.com'});
 assert((await blogRow.innerText()).includes('بیش از ۲۴ ساعت بدون انتشار ثبت‌شده'));assert((await blogRow.innerText()).includes('در حال اجرا'));
 await page.locator('.followups a[href="#blogsky"]').first().waitFor();
 assert((await page.locator('main').innerText()).includes('۱ رسید بدون زمان معتبر'));
 await page.locator('nav a[href="#blogsky"]').click();await page.locator('.status-dimensions').waitFor();
 assert.equal(await page.locator('.status-dimensions .fact').count(),3);
 failReceipt=true;failQueue=true;delayQueues=false;sha='b'.repeat(40);
 await page.getByRole('button',{name:'به‌روزرسانی',exact:true}).click();
 await page.getByRole('button',{name:'به‌روزرسانی',exact:true}).waitFor({state:'visible'});
 await page.waitForFunction(()=>!document.querySelector('#refresh').disabled);
 assert((await page.locator('.status-dimensions').innerText()).includes('داده قدیمی'));
 await page.locator('nav a[href="#overview"]').click();await page.waitForFunction(()=>document.querySelector('.stats')?.innerText.includes('شامل داده قدیمیِ ۱ وبلاگ')); 
 await page.locator('nav a[href="#publications"]').click();await page.waitForFunction(()=>document.querySelector('#titleIndexStatus')?.innerText.includes('ناموفق'));
 await page.setViewportSize({width:390,height:844});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'no viewport horizontal overflow');
 if(process.env.AFP_SCREENSHOT_DIR)await page.screenshot({path:path.join(process.env.AFP_SCREENSHOT_DIR,'mobile.png')});
 assert.deepEqual(errors,[]);console.log('PASS: eager title index, initial loading notice, trimmed search/CSV parity, independent running/overdue dimensions, follow-up inclusion, temporal coverage, stale refresh aggregates, failed title index warning, mobile overflow, no page errors.');
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exit(1)});
