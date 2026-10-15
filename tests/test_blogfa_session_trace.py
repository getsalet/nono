import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automation"))
from blogfa_session_trace import cookie_delta, cookie_response_metadata, SessionTrace


class SessionTraceTests(unittest.TestCase):
    def test_cookie_values_and_hashes_never_reported(self):
        out = cookie_delta({"ten": "OLD_PRIVATE"}, {"ten": "NEW_PRIVATE", "ph": "SECRET"})
        self.assertEqual(out["changed"], ["ten"])
        self.assertEqual(out["added"], ["ph"])
        for secret in ("OLD_PRIVATE", "NEW_PRIVATE", "SECRET"):
            self.assertNotIn(secret, json.dumps(out))

    def test_response_cookie_redaction(self):
        out = cookie_response_metadata(
            ["ten=PRIVATE_TOKEN; Path=/; HttpOnly; SameSite=Lax"])
        self.assertNotIn("PRIVATE_TOKEN", json.dumps(out))
        self.assertEqual(out[0]["name"], "ten")
        self.assertTrue(out[0]["http_only"])

    def test_publication_and_autosave_always_blocked(self):
        class Page:
            def route(self, *args): pass
            def on(self, *args): pass
        trace = SessionTrace(Page())
        for path in ("Post.aspx", "autosave.aspx"):
            calls = []
            route = SimpleNamespace(
                request=SimpleNamespace(
                    method="POST", url="https://www.blogfa.com/Desktop/" + path),
                abort=lambda reason: calls.append("abort"),
                continue_=lambda: calls.append("forward"))
            trace._route(route)
            self.assertEqual(calls, ["abort"])
        self.assertTrue(all(not x["forwarded_to_server"] for x in trace.events))

    def test_archive_search_is_allowed(self):
        class Page:
            def route(self, *args): pass
            def on(self, *args): pass
        trace = SessionTrace(Page())
        calls = []
        route = SimpleNamespace(
            request=SimpleNamespace(
                method="POST", url="https://www.blogfa.com/Desktop/Archive.aspx"),
            abort=lambda reason: calls.append("abort"),
            continue_=lambda: calls.append("forward"))
        trace._route(route)
        self.assertEqual(calls, ["forward"])
    def test_final_audit_also_works_when_login_fails_early(self):
        import ast
        source=(Path(__file__).resolve().parents[1]/"automation/blogfa_native.py").read_text()
        main=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=="main")
        self.assertFalse(any(isinstance(n,ast.Import) and any(x.name=="json" for x in n.names) for n in ast.walk(main)))

    def test_stabilization_is_single_bounded_wait_and_no_submission(self):
        from blogfa_native import wait_submit_ready
        calls=[]
        url="https://www.blogfa.com/Desktop/Post.aspx?action=new&t=PRIVATE_TOKEN"
        button=SimpleNamespace(count=lambda:1,is_enabled=lambda:True,evaluate=lambda js:url)
        page=SimpleNamespace(url=url,locator=lambda selector:button,
          context=SimpleNamespace(cookies=lambda origin:[{"name":"ten","value":"PRIVATE_TOKEN"}]),
          wait_for_timeout=lambda ms:calls.append(ms))
        wait_submit_ready(page)
        self.assertEqual(calls,[30000])

    def test_stabilization_refuses_changed_session_before_wait(self):
        from blogfa_native import wait_submit_ready
        url="https://www.blogfa.com/Desktop/Post.aspx?action=new&t=PRIVATE_TOKEN"
        button=SimpleNamespace(count=lambda:1,is_enabled=lambda:True,evaluate=lambda js:url)
        page=SimpleNamespace(url=url,locator=lambda selector:button,
          context=SimpleNamespace(cookies=lambda origin:[{"name":"ten","value":"OTHER_TOKEN"}]),
          wait_for_timeout=lambda ms:self.fail("Must not wait or send with a mismatched session"))
        with self.assertRaisesRegex(RuntimeError,"mismatch"):wait_submit_ready(page)

    def test_stabilization_precedes_journal_and_single_real_submit(self):
        source=(Path(__file__).resolve().parents[1]/"automation/publish_blogfa_posts.py").read_text()
        self.assertIn("wait_submit_ready(page);begin(e)",source)
        self.assertEqual(source.count("page.locator('#btnPublish').click()"),1)
