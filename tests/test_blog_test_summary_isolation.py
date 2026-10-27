"""Offline fixtures must never be presented as real pipeline results."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ('farsiblog-content.yml', 'rozblog-content.yml', 'loxblog-content.yml',
             'blogsky-content.yml', 'blog-image-stock.yml')

class BlogTestSummaryIsolation(unittest.TestCase):
    def test_full_suite_workflows_unset_only_summary_for_tests(self):
        for name in WORKFLOWS:
            with self.subTest(workflow=name):
                text = (ROOT / '.github/workflows' / name).read_text()
                commands = [line for line in text.splitlines() if 'unittest discover -s tests' in line]
                self.assertTrue(commands)
                for command in commands:
                    self.assertIn('env -u GITHUB_STEP_SUMMARY python -m unittest', command)
                self.assertNotIn('continue-on-error: true', '\n'.join(commands))

    def test_fixture_cannot_append_to_inherited_production_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = root / 'real-job-summary.md'
            summary.write_text('Production results only\n')
            fixture = root / 'fixture'
            fixture.mkdir()
            code = ("import sys; from pathlib import Path; "
                    "sys.path.insert(0, sys.argv[1]); "
                    "import blog_generation_status as status; "
                    "status.write(Path(sys.argv[2]), 'loxblog', ['synthetic-fixture'], [])")
            result = subprocess.run(
                ['env', '-u', 'GITHUB_STEP_SUMMARY', sys.executable, '-c', code,
                 str(ROOT / 'automation'), str(fixture)],
                env={**os.environ, 'GITHUB_STEP_SUMMARY': str(summary)},
                text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(summary.read_text(), 'Production results only\n')
            self.assertTrue((fixture / 'artifacts/loxblog-backlink-queue/generation-status.json').exists())

if __name__ == '__main__':
    unittest.main()
