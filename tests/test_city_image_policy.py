import os
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))

import image_prompt_policy
import image_quality_gate


class CityImagePolicyTests(unittest.TestCase):
    def test_visual_brief_and_roles_are_grounded_and_distinct(self):
        item = {
            "source_id": 101,
            "city": "نقده",
            "province": "آذربایجان غربی",
            "title": "راهنمای انتخاب نوار تیپ در نقده",
            "excerpt": "مقایسه فشار، فیلتراسیون و فاصله قطره‌چکان",
        }
        brief = image_prompt_policy.visual_brief(item)
        self.assertIn("نقده", brief)
        self.assertIn("فیلتراسیون", brief)
        prompts = [image_prompt_policy.image_prompt(item, kind) for kind in range(1, 6)]
        self.assertEqual(len(set(prompts)), 5)
        self.assertTrue(all("Article visual brief extracted from the post" in prompt for prompt in prompts))
        self.assertTrue(all("People must not appear" in prompt for prompt in prompts))
        self.assertIn("HEADWORKS STORY", prompts[2])
        self.assertIn("MAINTENANCE DETAIL", prompts[4])

    def test_metric_feedback_is_directional_without_noisy_center_rejection(self):
        ok, issues = image_quality_gate._metric_check(
            "tape20",
            {
                "product_width_percent": 22,
                "product_height_percent": 26,
                "product_x_center_percent": 50,
            },
        )
        self.assertTrue(ok)
        self.assertEqual(issues, [])
        ok, issues = image_quality_gate._metric_check(
            "tape20",
            {
                "product_width_percent": 16,
                "product_height_percent": 31,
                "product_x_center_percent": 50,
            },
        )
        self.assertFalse(ok)
        self.assertTrue(any("Enlarge" in issue for issue in issues))
        self.assertTrue(any("at most 28%" in issue for issue in issues))

    def test_rejected_five_image_set_keeps_published_files_untouched(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"IMAGE_SET_QA_ATTEMPTS": "1"}
        ):
            root = Path(tmp)
            base = SimpleNamespace(
                OUT=root / "artifacts",
                IMAGES=root / "artifacts" / "images",
                AGNES_MODEL="test",
                AGNES_BASE="https://example.invalid",
                AGNES_KEY="test",
            )
            base.IMAGES.mkdir(parents=True)
            originals = {}
            for kind in range(1, 6):
                name = f"city-{kind}.webp"
                originals[name] = f"published-{kind}".encode()
                (base.IMAGES / name).write_bytes(originals[name])

            def fake_generate(item, kind):
                name = f"city-{kind}.webp"
                output = Path(item["_image_output_dir"]) / name
                output.write_bytes(f"rejected-{kind}".encode())
                return name, f"hash-{kind}"

            backend = SimpleNamespace(generate_image=fake_generate)
            rejected = {
                "pass": False,
                "score": 20,
                "duplicate_roles": [1, 2, 3, 4, 5],
                "reasons": ["duplicate generic farm scenes"],
                "correction_prompt": "use distinct role-specific scenes",
            }
            manager = image_quality_gate.install_set_manager(base, backend, 5)
            with patch.object(image_quality_gate, "review_image_set", return_value=rejected):
                with ThreadPoolExecutor(max_workers=5) as pool:
                    with self.assertRaises(RuntimeError):
                        manager({"source_id": "city"}, pool)
            for name, expected in originals.items():
                self.assertEqual((base.IMAGES / name).read_bytes(), expected)
            self.assertFalse(any(base.OUT.glob(".image-staging-*")))


if __name__ == "__main__":
    unittest.main()