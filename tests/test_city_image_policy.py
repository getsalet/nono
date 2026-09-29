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

    def test_city_pipeline_matches_three_image_article_contract(self):
        backend = (ROOT / "automation" / "city_content_queue_cloudflare.py").read_text(encoding="utf-8")
        launcher = (ROOT / "automation" / "run_agnes_city_queue_seo.py").read_text(encoding="utf-8")
        rebuild = (ROOT / "automation" / "rebuild_city_images_preserve_posts.py").read_text(encoding="utf-8")
        self.assertIn("IMAGE_COUNT=3", backend)
        self.assertIn("range(1,4)", backend)
        self.assertIn("install_set_manager(base,backend,3)", launcher)
        self.assertIn("range(1, 4)", rebuild)
        self.assertNotIn("range(1, 6)", rebuild)

    def test_layflat_references_are_scale_conditioned(self):
        refs = image_prompt_policy.reference_images(
            1, {"source_id": "city-layflat", "title": "لوله نخی"}
        )
        self.assertEqual(len(refs), 1)
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
        self.assertIn("HEADWORKS DETAIL", prompts[2])
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
            }, 1,
        )
        self.assertTrue(ok)
        self.assertEqual(issues, [])
        ok, issues = image_quality_gate._metric_check(
            "tape20",
            {
                "product_width_percent": 16,
                "product_height_percent": 31,
                "product_x_center_percent": 50,
            }, 1,
        )
        self.assertTrue(ok)
        self.assertEqual(issues, [])
        ok, issues = image_quality_gate._metric_check(
            "layflat",
            {
                "product_width_percent": 33,
                "product_height_percent": 35,
                "product_x_center_percent": 50,
            }, 3,
        )
        self.assertTrue(ok)
        self.assertEqual(issues, [])
        ok, issues = image_quality_gate._metric_check(
            "layflat",
            {
                "product_width_percent": 60,
                "product_height_percent": 44,
                "product_x_center_percent": 50,
            }, 3,
        )
        self.assertTrue(ok)
        self.assertEqual(issues, [])
        ok, issues = image_quality_gate._metric_check(
            "layflat",
            {
                "product_width_percent": 66,
                "product_height_percent": 35,
                "product_x_center_percent": 50,
            }, 3,
        )
        self.assertFalse(ok)
        self.assertTrue(any("8-65%" in issue for issue in issues))
        queue_source = (ROOT / "automation" / "city_content_queue_cloudflare.py").read_text(encoding="utf-8")
        self.assertIn("layflat[:q.BATCH-len(selected)]", queue_source)
        ok, issues = image_quality_gate._metric_check(
            "tape20",
            {
                "product_width_percent": 11,
                "product_height_percent": 43,
                "product_x_center_percent": 50,
            }, 1,
        )
        self.assertFalse(ok)
        self.assertTrue(any("Enlarge" in issue for issue in issues))
        self.assertTrue(any("at most 35%" in issue for issue in issues))

    def test_headworks_prompt_is_an_unoccupied_equipment_still_life(self):
        item = {"source_id": "city-tape20", "topic": "tape20", "city": "گوهران"}
        prompt = image_prompt_policy.image_prompt(item, 3)
        self.assertIn("equipment-only still life", prompt)
        self.assertIn("no farm activity or living subject", prompt)
        self.assertIn("neutral empty equipment pad", prompt)
        self.assertNotIn("suitable for گوهران", prompt)

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

    def test_individually_approved_roles_survive_one_role_failure(self):
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

            def fake_generate(item, kind):
                image_dir = Path(item["_image_output_dir"])
                review_dir = Path(item["_image_review_dir"])
                name = f"city-{kind}.webp"
                if kind == 3:
                    raise RuntimeError("role 3 exhausted")
                image_dir.joinpath(name).write_bytes((f"approved-{kind}" * 2000).encode())
                review_dir.joinpath(f"city-{kind}.json").write_text(
                    '{"policy":"%s","history":[{"pass":true}]}' % image_quality_gate.REVIEW_POLICY,
                    encoding="utf-8",
                )
                return name, f"hash-{kind}"

            backend = SimpleNamespace(generate_image=fake_generate)
            manager = image_quality_gate.install_set_manager(base, backend, 5)
            with ThreadPoolExecutor(max_workers=5) as pool:
                with self.assertRaises(RuntimeError):
                    manager({"source_id": "city"}, pool)
            checkpoint = base.OUT / ".image-role-checkpoints" / "city"
            self.assertTrue(checkpoint.exists())
            for kind in (1, 2, 4, 5):
                self.assertTrue((checkpoint / "images" / f"city-{kind}.webp").exists())
                self.assertTrue((checkpoint / "image-reviews" / f"city-{kind}.json").exists())
            self.assertFalse((base.IMAGES / "city-1.webp").exists())

    def test_failed_checkpoint_feedback_is_reused_on_next_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image_dir = root / "images"
            review_dir = root / "reviews"
            image_dir.mkdir(); review_dir.mkdir()
            review_dir.joinpath("city-2.json").write_text(
                '{"policy":"%s","history":[{"pass":false,"reasons":["too large"],"correction_prompt":"move camera farther away"}]}' % image_quality_gate.REVIEW_POLICY,
                encoding="utf-8",
            )
            seen = []
            def seo_image_name(item, kind):
                return f"city-{kind}.webp"
            def raw_generator(item, kind):
                seen.append(item.get("_image_qa_feedback"))
                path = Path(item["_image_output_dir"]) / f"city-{kind}.webp"
                path.write_bytes(b"x" * 12000)
                return path.name, "hash"
            base = SimpleNamespace(OUT=root, IMAGES=image_dir)
            backend = SimpleNamespace(seo_image_name=seo_image_name)
            guarded = image_quality_gate.install(base, backend, raw_generator)
            passed = {"pass": True, "score": 90, "reasons": [], "correction_prompt": "", "product_width_percent": 20, "product_height_percent": 20, "product_x_center_percent": 30}
            item = {"source_id": "city", "_image_output_dir": str(image_dir), "_image_review_dir": str(review_dir)}
            with patch.object(image_quality_gate, "_vision_review", return_value=passed):
                guarded(item, 2)
            self.assertEqual(seen, ["move camera farther away"])

    def test_layflat_selection_role_has_no_conflicting_scene_objects(self):
        item = {"source_id": "city-layflat", "topic": "layflat", "city": "پلدشت"}
        prompt = image_prompt_policy.image_prompt(item, 2)
        self.assertIn("elevated technical view", prompt)
        self.assertIn("no horizon, building, crop rows, person", prompt)
        self.assertIn("occupying approximately 12 to 15 percent of frame width", prompt)

    def test_tape_maintenance_role_is_isolated_from_people_and_vehicles(self):
        item = {"source_id": "city-tape20", "topic": "tape20", "city": "لاجان"}
        prompt = image_prompt_policy.image_prompt(item, 5)
        self.assertIn("elevated close documentary view", prompt)
        self.assertIn("Crop all horizon, sky, buildings, people, animals", prompt)
        self.assertIn("exactly one carton visible at roughly 20 to 23 percent of frame width", prompt)
        self.assertIn("connector/emitter/flush-point", prompt)

    def test_set_qa_targets_only_named_roles_and_defaults_to_role_three(self):
        verdict = {
            "duplicate_roles": [],
            "reasons": ["Image 1 and Role 2 repeat the same layout"],
            "correction_prompt": "replace panel 2",
        }
        self.assertEqual(image_quality_gate._target_set_roles(verdict, 3), {1, 2})
        self.assertEqual(
            image_quality_gate._target_set_roles(
                {"duplicate_roles": [], "reasons": ["generic composition"]}, 3
            ),
            {3},
        )

    def test_final_diversity_only_failure_can_soft_pass_but_safety_cannot(self):
        diversity = {
            "score": 55,
            "reasons": ["Images 1 and 2 use similar camera angles"],
        }
        unsafe = {
            "score": 80,
            "reasons": ["A person is visible in panel 2"],
        }
        self.assertTrue(image_quality_gate._soft_set_accept(diversity, 3, 3))
        self.assertFalse(image_quality_gate._soft_set_accept(unsafe, 3, 3))
        self.assertFalse(image_quality_gate._soft_set_accept(diversity, 2, 3))


if __name__ == "__main__":
    unittest.main()
