const test=require('node:test'),assert=require('node:assert/strict');
const D=require('../docs/status/data.js');
const now=Date.parse('2026-10-28T09:00:00Z'),c=D.CONFIG.find(c=>c.id==='blogsky');
const old={key:'old',url:'https://afp-pipe.blogsky.com/post/1',at:'2026-10-25T09:00:00Z'};
const fresh={key:'new',url:'https://afp-pipe.blogsky.com/post/2',at:'2026-10-28T08:00:00Z'};
const run={path:'.github/workflows/'+c.workflow,status:'in_progress',created_at:'2026-10-28T08:00:00Z'};
const build=extra=>D.build(c,{state:{published:[fresh]},sourceAt:now,...extra},now);
test('running workflow never hides overdue publication dimension or attention',()=>{
 const r=build({state:{published:[old]},runs:[run]});
 assert.equal(r.status.code,'running');assert.equal(r.publication.code,'overdue');assert.equal(D.needsAttention(r),true);
});
test('paused workflow preserves independent publication freshness and quality',()=>{
 const r=build({state:{published:[old]},control:{enabled:false}});
 assert.equal(r.status.code,'paused');assert.equal(r.publication.code,'overdue');assert.equal(r.quality.code,'current');
});
test('unknown timestamp is not no publication; it needs attention even when running',()=>{
 const r=build({state:{published:[{...fresh,at:'bad'}]},runs:[run]});
 assert.equal(r.publication.code,'unknown');assert.equal(D.needsAttention(r),true);
});
test('missing or malformed receipt data never gets a current quality label',()=>{
 for(const state of [null,{}, {published:'not-an-array'}])assert.equal(build({state}).quality.code,'missing');
 assert.equal(build({state:{published:[]}}).quality.code,'current');
});
test('stale data retains last successful read without claiming current data',()=>{
 const r=build({stale:true,sourceAt:now-3600000});assert.equal(r.quality.code,'stale');assert.equal(r.quality.sourceAt,now-3600000);assert(D.needsAttention(r));
});
test('aggregates explicitly count missing and stale contributors, including stale zero',()=>{
 const rows=[build({}),build({stale:true,state:{published:[]}}),build({state:null})];
 for(const field of ['publications','today','week'])assert.deepEqual(D.aggregate(rows,field),{value:1,missing:1,stale:1});
 assert.deepEqual(D.aggregate([build({state:null})],'publications'),{value:null,missing:1,stale:0});
});
test('temporal coverage reconciles deduped total with unknown recovery and invalid timestamps',()=>{
 const r=build({state:{published:[fresh,fresh,{...old,recovered_existing:true},{key:'bad',url:'https://afp-pipe.blogsky.com/post/3',at:'bad'}]}});
 assert.deepEqual(D.timeCoverage([r]),{total:3,timed:1,unknown:2,missing:0,stale:0});assert.equal(r.today,1);
 assert.deepEqual(D.timeCoverage([r,build({state:null}),build({stale:true,state:{published:[]}})]),{total:3,timed:1,unknown:2,missing:1,stale:1});
});
test('genuine title metadata distinguished from ordinal fallback',()=>{
 assert.equal(D.publications(c,{published:[fresh]},null,now).rows[0].titleKnown,false);
 const p=D.publications(c,{published:[fresh]},{items:[{key:'new',assigned_title:'عنوان واقعی'}]},now).rows[0];
 assert.equal(p.title,'عنوان واقعی');assert.equal(p.titleKnown,true);
});
test('search and CSV use identical trimmed case-insensitive filter semantics',()=>{
 const posts=[{blogId:'blogsky',title:'عنوان واقعی',key:'a',url:'https://example.test',blog:'الف'}];
 assert.equal(D.filterPublications(posts,{blog:'all',query:'  عنوان واقعی  '}).length,1);
 assert.equal(D.filterPublications(posts,{blog:'all',query:' EXAMPLE.TEST '}).length,1);
 assert.equal(D.filterPublications(posts,{blog:'roya',query:''}).length,0);
});
test('independent recent receipt dimension does not conceal runtime failure',()=>{
 const r=build({runs:[{...run,status:'completed',conclusion:'failure'}]});assert.equal(r.publication.code,'recent');assert.equal(r.status.code,'run_failed');assert(D.needsAttention(r));
});
