import datetime as dt,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import city_backlink_policy as policy
import check_blog_run_budget as budget
import content_originality as originality

class LoxBlogIndependentPipelineTests(unittest.TestCase):
 def test_provider_has_independent_identity(self):
  self.assertEqual(policy.BLOGS['loxblog'],'https://afp.lxb.ir')
  for other in ('blogfa','farsiblog','rozblog'):self.assertFalse(set(policy.ANGLES['loxblog'])&set(policy.ANGLES[other]))
 def test_title_templates_are_not_other_provider_templates(self):
  m=json.loads((ROOT/'data/blog-city-title-matrix.json').read_text())
  for group in ('templates','article_templates'):
   for family in ('tape20','hose'):
    own=set(m[group]['loxblog'][family]);self.assertTrue(own)
    for other in ('blogfa','farsiblog','rozblog'):self.assertFalse(own&set(m[group][other][family]))
 def test_queue_uses_own_paths(self):
  script='import loxblog_backlink_queue as w;import json;print(json.dumps([w.engine.CITY_BLOG,str(w.engine.QUEUE),str(w.engine.ART),str(w.engine.STATE)]))'
  out=subprocess.check_output([sys.executable,'-c',script],env={**os.environ,'PYTHONPATH':str(ROOT/'automation')},text=True)
  values=json.loads(out);self.assertEqual(values[0],'loxblog');self.assertTrue(all('loxblog' in x for x in values))
 def test_rolling_budget_is_per_blog(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'state';p.mkdir();now=dt.datetime(2026,10,15,tzinfo=dt.timezone.utc)
   (p/'loxblog-backlink-progress.json').write_text(json.dumps({'published':[{'at':now.isoformat()}]*3}))
   self.assertFalse(budget.decision('loxblog',Path(d),now)['proceed'])
   self.assertTrue(budget.decision('blogfa',Path(d),now)['proceed'])
 def test_uncertain_submission_stops_new_generation(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'artifacts/loxblog-backlink-queue';p.mkdir(parents=True)
   for phase in ('submitting','unconfirmed','reconciled_absent'):
    (p/'submission-attempts.json').write_text(json.dumps({'x':{'phase':phase}}))
    result=budget.decision('loxblog',Path(d));self.assertFalse(result['proceed']);self.assertEqual(result['reason'],'native_reconciliation_required')
 def test_loxblog_drafts_participate_in_all_blog_originality(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'artifacts/loxblog-backlink-queue/items';p.mkdir(parents=True)
   body='<p>'+' '.join('word'+str(i)for i in range(100))+'</p>'
   (p/'x.json').write_text(json.dumps({'key':'x','qa':{'passed':True},'post':{'html':body}}))
   self.assertTrue(originality.check_corpus(Path(d),'blogfa','other',body))
   self.assertFalse(originality.check_corpus(Path(d),'loxblog','x',body))
 def test_publisher_has_single_submit_and_native_comments_off(self):
  s=(ROOT/'automation/publish_loxblog_posts.py').read_text()
  self.assertEqual(s.count('button.click()'),1)
  self.assertIn("comment_status:'0'",s);self.assertIn("native_split(post['html'])",s)
  self.assertIn("finally:journal(e,'unconfirmed')",s)
  self.assertNotIn('storage_state',s)
 def test_diagnostic_does_not_log_secrets_or_cookie_state(self):
  s=(ROOT/'automation/loxblog_native.py').read_text()
  self.assertNotIn('storage_state',s);self.assertNotIn('post_data',s);self.assertNotIn('print(feedback',s)
  self.assertIn('no automatic credential retry',s)
 def test_controlled_acceptance_recovers_before_one_fresh_article(self):
  s=(ROOT/'.github/workflows/loxblog-deployment-acceptance.yml').read_text()
  self.assertIn('publisher.begin = refuse_new_submission',s)
  self.assertIn('needs: reconcile-existing',s)
  self.assertIn("LOXBLOG_COUNT: '1'",s)
  self.assertIn('if: success() &&',s)
 def test_custom_native_public_slugs_are_not_discarded(self):
  script='from publish_loxblog_posts import public_records;r=public_records([{"url":"https://afp.lxb.ir/native-slug","title":"Exact title"},{"url":"https://afp.lxb.ir/post/7","title":"Alias title"}]);assert r["Exact title"]["pid"]is None;assert r["Alias title"]["pid"]==7;print("PASS")'
  out=subprocess.check_output([sys.executable,'-c',script],env={**os.environ,'PYTHONPATH':str(ROOT/'automation')},text=True)
  self.assertIn('PASS',out)
 def test_existing_native_identity_is_checked_before_any_submit(self):
  s=(ROOT/'automation/publish_loxblog_posts.py').read_text()
  self.assertIn('native=find_native_record(page,title)',s)
  self.assertIn("q.get('editpid'",s)
  self.assertIn("page.locator('#ptitle').input_value()!=title",s)
 def test_image_iri_fits_native_field_without_changing_reserved_escapes(self):
  script='from publish_loxblog_posts import native_image_value;from urllib.parse import quote;u="https://navar-abyari.ir/wp-content/uploads/"+quote("نوار آبیاری"*10)+"%2Fphoto.jpg";v=native_image_value(u);assert len(v)<240;assert "%2Fphoto.jpg" in v;assert quote(v,safe=":/%")==u;print("PASS")'
  out=subprocess.check_output([sys.executable,'-c',script],env={**os.environ,'PYTHONPATH':str(ROOT/'automation')},text=True)
  self.assertIn('PASS',out)
 def test_native_form_identity_and_server_date_are_preserved(self):
  s=(ROOT/'automation/publish_loxblog_posts.py').read_text()
  self.assertIn("form.id=form.id||'afp-native-post'",s)
  self.assertIn("result['future']==native_date",s)
  self.assertNotIn("locator('input[name=publish_at]').fill('')",s)
 def test_native_archive_has_its_own_verified_layout(self):
  s=(ROOT/'automation/publish_loxblog_posts.py').read_text()
  self.assertIn("#content #title a[href]",s)
  self.assertIn("#content #result",s)
  self.assertIn("#navbar a[href]",s)
  self.assertIn("#result a[href]",s)
  self.assertIn("Native public archive fingerprint missing",s)
 def test_versioned_release_is_explicit_and_has_verified_evidence(self):
  d=json.loads((ROOT/'data/loxblog/deployment-control.json').read_text())
  self.assertIsInstance(d['enabled'],bool)
  self.assertGreaterEqual(len(set(d['verified_post_ids'])),2)
  self.assertTrue(d['acceptance_run'].startswith('https://github.com/getsalet/nono/actions/runs/'))
  s=(ROOT/'.github/workflows/loxblog-content.yml').read_text()
  self.assertIn('needs: [tests, deployment-gate]',s)
  self.assertIn("release.get('enabled') is True",s)
 def test_schedule_is_gated_and_checkpoint_is_independent(self):
  s=(ROOT/'.github/workflows/loxblog-content.yml').read_text()
  self.assertIn("steps.release.outputs.proceed == '1'",s)
  self.assertIn("python automation/check_loxblog_release.py",s)
  self.assertIn("RELEASE_REPOSITORY_SWITCH: ${{ vars.LOXBLOG_AUTOMATION_ENABLED }}",s)
  self.assertIn('python automation/check_blog_run_budget.py loxblog',s)
  self.assertIn('data/loxblog/backlink-queue.json',s)
  self.assertIn('state/loxblog-backlink-progress.json',s)
  self.assertIn('LOXBLOG_LOGIN_DIAGNOSTIC',s)
  self.assertNotIn('secrets.BLOGFA_',s)
 def test_native_publisher_refuses_prior_uncertainty_globally(self):
  s=(ROOT/'automation/publish_loxblog_posts.py').read_text()
  self.assertIn("any(r.get('phase')in BLOCKED for r in rows.values())",s)

if __name__=='__main__':unittest.main()
