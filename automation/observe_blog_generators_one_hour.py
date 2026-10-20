#!/usr/bin/env python3
"""Finite read-only observation of five repository generators; report writes only.
No workflow dispatch/rerun, provider probe, login, native submission or control edit.
"""
import base64
from collections import Counter
import datetime as dt
import json
import os
from pathlib import Path
import re
import time
from monitor_blog_generators_one_hour import api, public_check
ROOT=Path(__file__).resolve().parents[1]
DURATION=3600
INTERVAL=300
BLOGS={
    'roya':{'url':'https://afp.royablog.ir/','workflows':['roya-backlink-queue.yml','roya-backlink-publish.yml']},
    'farsiblog':{'url':'https://afp.farsiblog.com/','workflows':['farsiblog-content.yml']},
    'rozblog':{'url':'https://afp-pipe.rozblog.com/','workflows':['rozblog-content.yml']},
    'loxblog':{'url':'https://afp.lxb.ir/','workflows':['loxblog-content.yml']},
    'blogsky':{'url':'https://afp-pipe.blogsky.com/','workflows':['blogsky-auto.yml','blogsky-content.yml']}}

def utc():return dt.datetime.now(dt.timezone.utc).isoformat()

def repo_json(path,ref):
    if not re.fullmatch(r'[a-f0-9]{40}',ref):raise ValueError('Exact repository commit required')
    value=api('/contents/'+path+'?ref='+ref)
    if not value.get('content'):
        sha=value.get('sha','')
        if not re.fullmatch(r'[a-f0-9]{40}',sha):raise RuntimeError('Verified JSON blob identifier required')
        value=api('/git/blobs/'+sha)
    if value.get('encoding')!='base64' or not value.get('content'):raise RuntimeError('JSON content unavailable')
    return json.loads(base64.b64decode(value['content']))

def snapshot():
    ref=api('/commits/main')['sha']
    sample={'at':utc(),'repository_ref':ref,'blogs':{}}
    for blog,cfg in BLOGS.items():
        row={'workflows':{}}
        sample['blogs'][blog]=row
        for workflow in cfg['workflows']:
            try:
                data=api('/actions/workflows/'+workflow+'/runs?per_page=3')
                runs=[{k:r.get(k) for k in ('id','status','conclusion','event','created_at','updated_at','html_url')}for r in data.get('workflow_runs',[])]
                item={'runs':runs};row['workflows'][workflow]=item
                if runs:
                    jobs=api('/actions/runs/'+str(runs[0]['id'])+'/jobs?per_page=100').get('jobs',[])
                    item['latest_jobs']=[{'name':j.get('name'),'status':j.get('status'),'conclusion':j.get('conclusion'),'failed_steps':[s.get('name') for s in j.get('steps',[]) if s.get('conclusion')=='failure']}for j in jobs]
            except Exception as exc:row['workflows'][workflow]={'read_error_type':type(exc).__name__}
        try:
            rows=repo_json('data/'+blog+'/backlink-queue.json',ref).get('items',[])
            keys=[x['key'] for x in rows]
            if len(keys)!=len(set(keys)):raise RuntimeError('Duplicate queue keys; observation invalid')
            row['queue_status_counts']=dict(Counter(str(x.get('status','unknown')) for x in rows))
            row['queue_items']=len(rows)
            row['generated_keys']=[x['key'] for x in rows if x.get('generated_at')]
            row['published_keys']=[x['key'] for x in rows if x.get('published')]
            row['ready_count']=sum(x.get('status') in ('completed','ready') and not x.get('published') for x in rows)
            row['published_flag_count']=len(row['published_keys'])
        except Exception as exc:row['queue_read_error_type']=type(exc).__name__
        try:
            state=repo_json('state/'+blog+'-backlink-progress.json',ref)
            row['publication_history_count']=len(state.get('published',[]))
            row['latest_publication_records']=state.get('published',[])[-3:]
        except Exception as exc:row['history_read_error_type']=type(exc).__name__
        row['public_availability']=public_check(cfg['url'])
    for label,path in [('release_control','data/blog-generated-image-control.json'),('provider_backpressure','data/blog-image-provider-backpressure.json'),('blogsky_publication_control','data/blogsky/native-publication-control.json')]:
        try:sample[label]=repo_json(path,ref)
        except Exception as exc:sample[label+'_read_error_type']=type(exc).__name__
    return sample

def summary(samples):
    result={}
    for blog in BLOGS:
        first=samples[0].get('blogs',{}).get(blog,{}) if samples else {}
        last=samples[-1].get('blogs',{}).get(blog,{}) if samples else {}
        complete=all('published_keys' in row and 'generated_keys' in row for row in (first,last))
        def failures(row):
            return {str(run['id']) for wf in row.get('workflows',{}).values() for run in wf.get('runs',[]) if run.get('conclusion')=='failure'}
        seen_failures=set().union(*(failures(sample.get('blogs',{}).get(blog,{})) for sample in samples)) if samples else set()
        baseline_workflows_ok=bool(first.get('workflows')) and all('read_error_type' not in wf for wf in first['workflows'].values())
        result[blog]={'new_failed_run_ids':sorted(seen_failures-failures(first)) if baseline_workflows_ok else None,'baseline_and_final_queue_available':complete,'new_generated_checkpoint_keys':len(set(last['generated_keys'])-set(first['generated_keys'])) if complete else None,'new_published_queue_flags':len(set(last['published_keys'])-set(first['published_keys'])) if complete else None,'latest_ready_count':last.get('ready_count'),'new_public_posts_independently_verified_by_monitor':False}
    return result

def observe(read=None,persist=None,clock=None,sleep=None,duration=DURATION,interval=INTERVAL):
    if not 1<=duration<=DURATION or not 1<=interval<=INTERVAL:raise ValueError('Finite observation window required')
    read=read or snapshot;clock=clock or time.monotonic;sleep=sleep or time.sleep
    run=os.getenv('GITHUB_RUN_ID','local')
    if not re.fullmatch(r'[A-Za-z0-9_-]+',run):raise ValueError('Invalid run identifier')
    started=clock();deadline=started+duration
    report={'workflow_run_id':run,'workflow_url':'https://github.com/getsalet/nono/actions/runs/'+run,'status':'monitoring','started_at':utc(),'requested_duration_seconds':duration,'sample_interval_seconds':interval,'scope':list(BLOGS),'retired_blogfa_excluded':True,'observation_only':True,'provider_requests':0,'workflow_dispatches':0,'native_submissions':0,'production_controls_modified':False,'publication_caveat':'Queue flags and green runs are not independent public content verification; HTTP failures are unverified availability observations, not proof of outage.','samples':[]}
    if persist is None:
        from blog_generated_image import checkpoint_asset
        path='artifacts/blog-readonly-one-hour/'+run+'.json'
        def persist(value):
            raw=json.dumps(value,ensure_ascii=False,indent=2).encode()
            dest=ROOT/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
            checkpoint_asset(path,raw,ROOT)
    def checkpoint():
        report['elapsed_seconds']=round(clock()-started,1)
        report['summary']=summary(report['samples'])
        persist(report)
    checkpoint()
    try:
        while True:
            try:sample=read()
            except Exception as exc:sample={'at':utc(),'blogs':{},'read_error_type':type(exc).__name__}
            report['samples'].append(sample);checkpoint()
            print(json.dumps({'status':report['status'],'elapsed_seconds':report['elapsed_seconds'],'samples':len(report['samples'])}),flush=True)
            left=deadline-clock()
            if left<=0:break
            sleep(min(interval,left))
        report.update(status='completed',finished_at=utc())
    except BaseException as exc:
        report.update(status='interrupted',finished_at=utc(),error_type=type(exc).__name__)
        raise
    finally:checkpoint()
    if os.getenv('GITHUB_STEP_SUMMARY'):
        Path(os.environ['GITHUB_STEP_SUMMARY']).write_text('## One-hour read-only generator observation\n\nObserved seconds: '+str(report['elapsed_seconds'])+'; snapshots: '+str(len(report['samples']))+'.\n\nNo dispatch, provider request, login, publication, or production-control change.\n\n```json\n'+json.dumps(report['summary'],ensure_ascii=False,indent=2)+'\n```\n\nQueue publication changes are self-reported checkpoints, not new independently verified public articles.\n')
    return report

if __name__=='__main__':observe()
