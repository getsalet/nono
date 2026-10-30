"""Regression for a real preflight false positive, not a chemical-QA waiver."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'automation'))
from parsiblog_policy import factual_errors

CHEMICAL_ERROR = 'Chemical cleaning requires a reviewed model-specific procedure; omit it'

class ChemicalBoundariesTests(unittest.TestCase):
    def test_observed_identification_word_is_not_acid(self):
        text = ('این فرآیند به شما کمک می‌کند تا نقاط آسیب‌پذیر را بهتر بشناسید '
                'و تصمیم‌گیری را بر اساس مستندات انجام دهید، نه بر اساس حدس و گمان.')
        self.assertEqual(factual_errors(text), [])

    def test_safe_identification_in_different_positions(self):
        for text in ('بشناسید', 'نیاز زمین را بشناسید.', '«بشناسید»', 'بشناسید؛ سپس بررسی کنید.'):
            with self.subTest(text=text):
                self.assertNotIn(CHEMICAL_ERROR, factual_errors(text))

    def test_real_chemical_terms_and_inflections_still_rejected(self):
        for term in ('اسید', 'اسیدی', 'اسیدشویی', 'اسیدها', 'اسیدهاى',
                     'اسیدشویی‌ها', 'اسید‌شویی', 'جوهر نمک', 'جوهرنمک', 'جوهر‌نمک'):
            for text in (term, 'شستشو با ' + term, 'شستشو:«' + term + '»'):
                with self.subTest(text=text):
                    self.assertIn(CHEMICAL_ERROR, factual_errors(text))

    def test_safe_word_never_masks_separate_chemical_recommendation(self):
        for text in ('زمین را بشناسید؛ شستشو با اسید ملایم.',
                     'جوهر نمک استفاده کنید؛ زمین را بشناسید.'):
            with self.subTest(text=text):
                self.assertIn(CHEMICAL_ERROR, factual_errors(text))

if __name__ == '__main__':
    unittest.main()
