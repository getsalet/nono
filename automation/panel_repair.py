"""Authenticated, exact-item repairs. Never submits a new blog post."""
import datetime as dt, hashlib, json, os, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class Blocked(Exception): pass

def load(root, path):
    return json.loads((root / path).read_text())

def plan(root, blog, target):
    if blog not in ('parsiblog', 'loxblog'): raise Blocked('unsupported_blog')
    pattern = r'pb-[0-9a-f]{20}' if blog == 'parsiblog' else r'(?:city|article)-[0-9a-f]{16}'
    if not re.fullmatch(pattern, target): raise Blocked('invalid_target')
    control = load(root, 'data/blog-generated-image-control.json')
    if control.get('pause_image_production') is not False or blog in control.get('retired_blogs', []): raise Blocked('paused')
    state_path = 'state/parsiblog-progress.json' if blog == 'parsiblog' else 'state/loxblog-backlink-progress.json'
    state = load(root, state_path)
    if any(x.get('key') == target for x in state.get('published', [])): raise Blocked('already_published')
    if blog == 'parsiblog':
        row = state.get('items', {}).get(target, {})
        if row.get('status') != 'failed' or row.get('id') or row.get('native_phase'): raise Blocked('not_pre_submit_failure')
        if not str(row.get('reason', '')).startswith('Text SEO preflight rejected:'): raise Blocked('unsupported_failure')
        matrix = load(root, 'data/parsiblog/title-matrix.json')
        matches = [x for x in matrix.get('items', []) if x.get('key') == target]
        if matrix.get('approved') is not True or len(matches) != 1: raise Blocked('unapproved_target')
        family = matches[0].get('family')
        if family not in control.get('enabled_families', []) or family in control.get('held_families', {}) or family in control.get('cancelled_families', []): raise Blocked('family_held')
        saved = root / ('artifacts/parsiblog-backlink-queue/items/' + target + '.json')
        if saved.exists():
            item = json.loads(saved.read_text())
            if item.get('native_id') or item.get('published') or item.get('qa', {}).get('passed'): raise Blocked('saved_item_needs_review')
        operation = 'rewrite_and_validate_draft'
    else:
        journal = load(root, 'artifacts/loxblog-backlink-queue/submission-attempts.json')
        row = journal.get(target, {})
        if row.get('phase') not in ('submitting', 'unconfirmed', 'reconciled_absent'): raise Blocked('not_uncertain_submission')
        item = load(root, 'artifacts/loxblog-backlink-queue/items/' + target + '.json')
        if item.get('key') != target or item.get('qa', {}).get('passed') is not True or not item.get('post', {}).get('html'): raise Blocked('approved_body_missing')
        family = item.get('family')
        if family not in control.get('enabled_families', []) or family in control.get('held_families', {}) or family in control.get('cancelled_families', []): raise Blocked('family_held')
        operation = 'verify_existing_and_recover_receipt'
    fingerprint = hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()
    marker = root / f'artifacts/panel-repairs/{blog}/{target}.json'
    if marker.exists() and json.loads(marker.read_text()).get('fingerprint') == fingerprint: raise Blocked('same_failure_already_attempted')
    return dict(blog=blog, target=target, operation=operation, fingerprint=fingerprint)

def perform(root, request):
    if request['blog'] == 'parsiblog':
        import parsiblog_pipeline as pipeline
        key = request['target']
        previous = load(root, 'state/parsiblog-progress.json')['items'][key]
        try:
            pipeline.main(['--mode', 'generate', '--target', key, '--retry-pre-submit'])
        except Exception:
            # Keep a fresh, non-secret failed report; no native path is entered.
            current = load(root, 'state/parsiblog-progress.json')
            current.setdefault('items', {})[key] = previous
            pipeline.save(root / 'state/parsiblog-progress.json', current)
            pipeline.run_report(status='failed', completed_at=pipeline.stamp(), reason='Panel draft repair did not pass all gates')
            raise
        state = load(root, 'state/parsiblog-progress.json')
        item = load(root, f'artifacts/parsiblog-backlink-queue/items/{key}.json')
        if state.get('items', {}).get(key, {}).get('status') != 'ready' or item.get('qa', {}).get('passed') is not True or item.get('editorial_review', {}).get('passed') is not True or pipeline.RUN.get('native_write_attempted') is not False:
            raise Blocked('repair_not_verified')
        return 'repaired_draft'
    import recover_existing_blog_receipt as recovery
    recovery.TARGETS = {'loxblog': request['target']}
    result = recovery.recover('loxblog')
    if result.get('passed') is not True or result.get('result') != 'verified_existing' or result.get('new_submissions') != 0: raise Blocked('existing_post_not_verified')
    state = load(root, 'state/loxblog-backlink-progress.json')
    if not any(x.get('key') == request['target'] and x.get('recovered_existing') is True for x in state.get('published', [])): raise Blocked('receipt_missing')
    return 'reconciled_receipt'

def main():
    blog = os.environ.get('REPAIR_BLOG', '')
    target = os.environ.get('REPAIR_TARGET', '')
    mode = os.environ.get('REPAIR_MODE', 'inspect')
    if os.environ.get('GITHUB_REF') != 'refs/heads/main' or os.environ.get('GITHUB_EVENT_NAME') != 'workflow_dispatch': raise SystemExit('Only authenticated main dispatch is allowed')
    report = dict(schema='panel-repair-v1', blog=blog, target=target, run_id=os.environ['GITHUB_RUN_ID'], at=dt.datetime.now(dt.timezone.utc).isoformat(), native_submissions=0, outcome='blocked', mode=mode)
    exit_code = 0
    try:
        if mode not in ('inspect', 'repair'): raise Blocked('invalid_mode')
        request = plan(ROOT, blog, target)
        report.update(request)
        if mode == 'repair':
            if os.environ.get('REPAIR_CONFIRM') != 'REPAIR': raise Blocked('confirmation_required')
            report['outcome'] = 'failed'
            report['outcome'] = perform(ROOT, request)
        else: report['outcome'] = 'eligible_not_executed'
    except Blocked as e:
        report['reason_code'] = str(e); exit_code = 1
    except Exception:
        report['reason_code'] = 'repair_failed_inspect_artifact'; exit_code = 1
    finally:
        # Only allowlisted identifiers and application-authored codes, never raw exceptions.
        if blog in ('parsiblog', 'loxblog') and re.fullmatch(r'(?:pb-[0-9a-f]{20}|(?:city|article)-[0-9a-f]{16})', target):
            folder = ROOT / f'artifacts/panel-repairs/{blog}'; folder.mkdir(parents=True, exist_ok=True)
            (folder / 'latest.json').write_text(json.dumps(report, indent=2) + '\n')
            # Inspection/blocked requests must not consume a repair attempt.
            if mode == 'repair' and report['outcome'] in ('failed', 'repaired_draft', 'reconciled_receipt'):
                (folder / (target + '.json')).write_text(json.dumps(report, indent=2) + '\n')
        if os.environ.get('GITHUB_STEP_SUMMARY'):
            labels = {'repaired_draft': 'پیش‌نویس اصلاح شد و از کنترل کیفیت گذشت؛ منتشر نشده است.', 'reconciled_receipt': 'مطلب موجود تأیید و رسید بازیابی شد؛ پست تازه‌ای ارسال نشد.', 'eligible_not_executed': 'بررسی انجام شد؛ تعمیر اجرا نشده است.', 'blocked': 'تعمیر مسدود شد؛ علت را در reason_code ببینید.', 'failed': 'تعمیر تأیید نشد؛ کنترل کیفیت دور زده نشده است.'}
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as out: out.write('## نتیجه تعمیر\n\n' + labels[report['outcome']] + '\n\n```json\n' + json.dumps(report, ensure_ascii=False, indent=2) + '\n```\n\nنتیجه ماندگار فقط پس از موفقیت مرحله ذخیره معتبر است.\n')
    raise SystemExit(exit_code)
if __name__ == '__main__': main()
