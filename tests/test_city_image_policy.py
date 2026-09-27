import os
import sys
import tempfile
import unittest
import base64
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))

import image_prompt_policy
import image_quality_gate


class CityImagePolicyTests(unittest.TestCase):
    def test_failed_image_qa_is_quarantined_instead_of_starving_queue(self):
        queue_source = (ROOT / "automation" / "city_content_queue_cloudflare.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("image_qa_deferred", queue_source)
        self.assertIn("deferred_image_qa_items", queue_source)
        self.assertNotIn("item['attempts']=max(0,int(item.get('attempts',0))-1)", queue_source)
        rebuild_source = (
            ROOT / "automation" / "rebuild_city_images_preserve_posts.py"
        ).read_text(encoding="utf-8")
        self.assertIn('== "layflat"', rebuild_source)
        retry_source = (
            ROOT / "automation" / "run_agnes_city_queue_fast.py"
        ).read_text(encoding="utf-8")
        self.assertIn("IMAGE_RETRY_POLICY", retry_source)
        self.assertIn("item.get('retry_policy')!=IMAGE_RETRY_POLICY", retry_source)

    def test_layflat_references_are_scale_conditioned(self):
        refs = image_prompt_policy.reference_images(
            1, {"source_id": "city-layflat", "title": "لوله نخی"}
        )
        self.assertEqual(len(refs), 2)
        self.assertTrue(all(ref.startswith("data:image/webp;base64,") for ref in refs))
        for ref in refs:
            image = Image.open(io.BytesIO(base64.b64decode(ref.split(",", 1)[1])))
            self.assertEqual(image.size, (1200, 675))

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
        self.assertTrue(all("NO PEOPLE OR VEHICLES" in prompt for prompt in prompts))
        self.assertTrue(all("tractor, harvester, vehicle or machine cabin" in prompt for prompt in prompts))

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
        self.assertTrue(ok)
        self.assertEqual(issues, [])
        ok, issues = image_quality_gate._metric_check(
            "layflat",
            {
                "product_width_percent": 33,
                "product_height_percent": 35,
                "product_x_center_percent": 50,
            },
        )
        self.assertTrue(ok)
        self.assertEqual(issues, [])
        ok, issues = image_quality_gate._metric_check(
            "tape20",
            {
                "product_width_percent": 11,
                "product_height_percent": 43,
                "product_x_center_percent": 50,
            },
        )
        self.assertFalse(ok)
        self.assertTrue(any("Enlarge" in issue for issue in issues))
        self.assertTrue(any("at most 42%" in issue for issue in issues))

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