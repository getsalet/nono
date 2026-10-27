"""Keep the full-suite job usable without silently skipping dependencies."""
import unittest
from pathlib import Path

class ImageStockTestDependencies(unittest.TestCase):
    def test_full_suite_installs_import_dependencies(self):
        text = (Path(__file__).resolve().parents[1] / '.github/workflows/blog-image-stock.yml').read_text()
        tests = text.split('  tests:', 1)[1].split('  replenish:', 1)[0]
        install = next(line for line in tests.splitlines() if 'pip install' in line)
        for package in ('Pillow', 'beautifulsoup4', 'playwright'):
            self.assertIn(package, install)
        self.assertIn("python -m unittest discover -s tests -p 'test_*.py' -v", tests)
        self.assertNotIn('continue-on-error', tests)

if __name__ == '__main__':
    unittest.main()
