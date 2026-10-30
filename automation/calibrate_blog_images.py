#!/usr/bin/env python3
"""Six bounded image-only comparisons; never edits queues, posts or acceptance."""
import copy,hashlib,io,json,os,re,subprocess,time
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import blog_reference_scene as scene
import blog_generated_image as generated
import blog_image_gate as gate
import blog_image_restore as restore
from blog_image_art_direction import closed_package_prompt,VERSION
ROOT=Path(__file__).resolve().parents[1]
BLOG='roya'
SOURCE_KEYS=('article-f216134c2b97ce6d','article-4231236eacb8613e','article-98433db6d9a59096')
CASES=((1,'baseline',0),(1,'baseline',1),(2,'candidate',0),(2,'candidate',1),(3,'holdout',2),(3,'repeat',0))

def load_items(root=ROOT):
    q=json.loads((root/'data/roya/backlink-queue.json').read_text())
    rows={x['key']:x for x in q['items']}
    result=[]
    for key in SOURCE_KEYS:
        item=copy.deepcopy(rows[key])
        if item.get('family')!='tape20' or not item.get('published'):raise ValueError('Published tape source required')
        post=json.loads((root/'artifacts/roya-backlink-queue/items'/(key+'.json')).read_text())['post']
        item['_image_article_context']=scene.context_from_post(post)
        result.append(item)
    return result

def cases(items):
    result=[]
    for i,(stage,variant,index)in enumerate(CASES,1):
        item=copy.deepcopy(items[index])
        source=item['key'];item['key']='image-calibration-'+os.getenv('GITHUB_RUN_ID','offline')+'-'+str(i)
        item.pop('_image_qa_feedback',None)
        result.append((item,{'case':i,'stage':stage,'variant':variant,'source_key':source,'source_index':index}))
    return result

def encode(raw):
    from blog_image_watermark import apply
    image=Image.open(io.BytesIO(raw)).convert('RGB')
    out=io.BytesIO();apply(image).save(out,'WEBP',quality=92,method=6)
    return out.getvalue()

def main():
    run=os.environ['GITHUB_RUN_ID']
    out=ROOT/'artifacts/blog-image-calibration'/run;out.mkdir(parents=True,exist_ok=True)
    report={'run_id':run,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'candidate_version':VERSION,
        'post_submissions':0,'article_state_changes':0,'production_activation':False,'manual_visual_approval':False,
        'model':os.getenv('IMAGE_MODEL','agnes-image-2.5-flash'),'maximum_candidates':6,'cases':[]}
    def save():
        data=json.dumps(report,ensure_ascii=False,indent=2).encode();(out/'report.json').write_bytes(data)
        generated.checkpoint_asset(str((out/'report.json').relative_to(ROOT)),data,ROOT)
    try:
        control=json.loads((ROOT/'data/blog-generated-image-control.json').read_text())
        if control.get('pause_image_production')is not False or not generated.family_enabled({'family':'tape20'},ROOT):raise RuntimeError('Existing image hold remains active')
        slots=restore.evidence(BLOG,ROOT)
        report['assigned_image_slots']=slots
        inputs=load_items();save()
        for item,row in cases(inputs):
            report['cases'].append(row)
            plan=scene.scene_plan(item,BLOG);a=scene.article(item)
            prompt=scene.prompt(item,BLOG)if row['variant']=='baseline'else closed_package_prompt(a,plan)
            row.update(title=a['title'],scene=plan,prompt=prompt,prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                reference_sha256=[hashlib.sha256(x.encode()).hexdigest()for x in scene.references(item)])
            try:
                # Preserve hosted FIFO admission, cooldown and the owner's image pair.
                with patch.object(scene,'prompt',return_value=prompt):raw=generated.generate(item,BLOG,slots=slots,max_attempts=1)
                candidate=encode(raw);filename=f"case-{row['case']}-{row['variant']}.webp";path=out/filename;path.write_bytes(candidate)
                row.update(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(candidate).hexdigest(),dimensions=list(Image.open(io.BytesIO(candidate)).size))
                generated.checkpoint_asset(row['path'],candidate,ROOT)
                try:
                    review=gate.review(item,'generated://roya/'+item['key'],root=ROOT,_candidate=candidate)
                    row['primary_review']=review['verdict'];row['primary_passed']=True
                except Exception as exc:
                    row['primary_passed']=False;row['primary_error_type']=type(exc).__name__
                    records=list((ROOT/'artifacts/blog-image-reviews').glob('tape20-'+row['sha256']+'.json'))
                    if records:row['primary_review']=json.loads(records[0].read_text()).get('verdict')
                key=generated.roya.BASE.next_agnes_key()
                row['independent_physical_review']=gate.focused_physical_check(candidate,'WEBP',os.getenv('IMAGE_REVIEW_MODEL','agnes-3.0-flash'),key)
                row['no_strip_confirmed']=row['independent_physical_review'].get('package_has_protruding_strip')is False
                row['candidate_passed']=row['primary_passed'] and row['no_strip_confirmed']
            except Exception as exc:
                row.update(error_type=type(exc).__name__,candidate_passed=False)
                if hasattr(exc,'retry_at'):row['retry_at']=exc.retry_at
            row['provider_attempts']=item.get('_image_provider_attempts',[])
            save()
            print(json.dumps({k:row.get(k)for k in ('case','variant','candidate_passed','no_strip_confirmed','error_type')},ensure_ascii=False),flush=True)
            # Never blindly retry a busy provider in this run.
            if row.get('retry_at'):report['stopped_for_provider_backpressure']=True;break
    except Exception as exc:report['preflight_error_type']=type(exc).__name__
    finally:
        report['finished_at']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());save()
    return 0
if __name__=='__main__':raise SystemExit(main())
