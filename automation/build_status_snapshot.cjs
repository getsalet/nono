#!/usr/bin/env node
// Public read-only projection. Never include queue bodies, prompts, credentials or logs.
const fs=require('node:fs'),path=require('node:path');
const D=require('../docs/status/data.js');
const workflows=[...new Set(D.CONFIG.flatMap(c=>[c.workflow,c.generationWorkflow].filter(Boolean)))];
function loadJson(root,name){return JSON.parse(fs.readFileSync(path.join(root,name),'utf8'))}
function buildPublications(root,now=Date.now()){
 const blogs={};
 for(const c of D.CONFIG){
  const state=loadJson(root,c.state);if(!Array.isArray(state?.published))throw new Error('Invalid receipt source: '+c.state);
  const queue=loadJson(root,c.queue),items=queue?.items??(c.id==='niloblog'?queue?.titles:null);if(!items||typeof items!=='object')throw new Error('Invalid title source: '+c.queue);
  const pub=D.publications(c,state,queue,now);
  blogs[c.id]=pub.rows.map(p=>({key:p.key,url:p.url,title:p.titleKnown?String(p.title):null,published_at:p.publishedAt===null?null:new Date(p.publishedAt).toISOString()}));
 }
 return blogs;
}
function projectRun(run,workflow){
 if(!run)return null;
 if(String(run.path||'').split('@')[0]!=='.github/workflows/'+workflow||run.head_branch!=='main'||!Number.isSafeInteger(run.id)||!D.safeUrl(run.html_url)||run.html_url!=='https://github.com/getsalet/nono/actions/runs/'+run.id||D.dateMs(run.created_at)===null||D.dateMs(run.updated_at)===null)throw new Error('Invalid run for '+workflow);
 const clean={...run,path:'.github/workflows/'+workflow};
 return Object.fromEntries(['id','run_attempt','name','display_title','path','head_branch','status','conclusion','created_at','updated_at','run_started_at','html_url','event'].filter(k=>clean[k]!==undefined).map(k=>[k,clean[k]]));
}
async function collectRuns(fetcher,now=Date.now()){
 const result={};
 for(const workflow of workflows){
  try{const response=await fetcher('https://api.github.com/repos/getsalet/nono/actions/workflows/'+encodeURIComponent(workflow)+'/runs?branch=main&per_page=1');if(!response.ok)throw new Error('HTTP '+response.status);const data=await response.json();if(!Array.isArray(data.workflow_runs))throw new Error('Malformed API response');result[workflow]={ok:true,observed_at:new Date(now).toISOString(),run:projectRun(data.workflow_runs[0],workflow)};}
  catch(e){result[workflow]={ok:false,observed_at:new Date(now).toISOString(),error:'unavailable'};}
 }
 return result;
}
async function buildSnapshot(root,revision,fetcher,now=Date.now()){
 if(!/^[a-f0-9]{40}$/.test(revision))throw new Error('Expected immutable source revision');
 return {schema:'afp-status-snapshot-v1',source_revision:revision,generated_at:new Date(now).toISOString(),blogs:buildPublications(root,now),workflows:await collectRuns(fetcher,now)};
}
async function main(){
 const args=process.argv.slice(2),option=(name,fallback)=>{const i=args.indexOf(name);return i<0?fallback:args[i+1]};
 const token=process.env.STATUS_SNAPSHOT_TOKEN;
 const fetcher=url=>fetch(url,{headers:{Accept:'application/vnd.github+json',...(token?{Authorization:'Bearer '+token}:{})},signal:AbortSignal.timeout(18000)});
 const snapshot=await buildSnapshot(option('--root','.'),option('--revision',''),fetcher);
 fs.writeFileSync(option('--output','status-snapshot.json'),JSON.stringify(snapshot)+'\n');
 console.log('Snapshot created; workflow sources unavailable: '+Object.values(snapshot.workflows).filter(x=>!x.ok).length);
}
module.exports={buildPublications,projectRun,collectRuns,buildSnapshot,workflows};
if(require.main===module)main().catch(e=>{console.error(e.message);process.exit(1)});
