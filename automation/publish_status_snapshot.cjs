#!/usr/bin/env node
// Writes only the public snapshot file on the dedicated status-data branch.
const fs=require('node:fs');
(async()=>{
 const token=process.env.STATUS_SNAPSHOT_TOKEN;if(!token)throw new Error('Snapshot publisher token is required');
 const repo='getsalet/nono',branch='status-data',file='status-snapshot.json',base='https://api.github.com/repos/'+repo;
 const headers={Accept:'application/vnd.github+json',Authorization:'Bearer '+token,'Content-Type':'application/json'};
 const request=(url,options={})=>fetch(url,{...options,headers,signal:AbortSignal.timeout(18000)});
 const source=fs.readFileSync(process.argv[2],'utf8');const value=JSON.parse(source);
 if(value.schema!=='afp-status-snapshot-v1')throw new Error('Invalid snapshot schema');
 const previous=await request(base+'/contents/'+file+'?ref='+branch);
 if(previous.status!==404&&!previous.ok)throw new Error('Cannot read snapshot destination: '+previous.status);
 const current=previous.ok?await previous.json():null;
 // A serialized workflow owns this destination; a conflict fails rather than force-overwriting.
 const result=await request(base+'/contents/'+file,{method:'PUT',body:JSON.stringify({branch,message:'data(status): refresh public title and workflow snapshot',content:Buffer.from(source).toString('base64'),...(current?{sha:current.sha}:{})})});
 if(!result.ok)throw new Error('Cannot publish snapshot: '+result.status);
 console.log('Updated '+branch+'/'+file);
})().catch(e=>{console.error(e.message);process.exit(1)});
