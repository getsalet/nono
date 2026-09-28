import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))

import upload_new_city_batches_ftps as uploader
import write_new_batch_signal as signal_writer


class NewBatchUploadTests(unittest.TestCase):
    def test_signal_is_stable_when_no_new_batch_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            state = root / "state.json"
            signal = root / ".new-batch-signal"
            manifest.write_text(
                json.dumps({"packages": [{"batch": "batch-001-posts-0001-0050"}]}),
                encoding="utf-8",
            )
            state.write_text(
                json.dumps({"files": {"batch-001-posts-0001-0050.zip": {}}}),
                encoding="utf-8",
            )
            signal.write_text("batch-001-posts-0001-0050.zip\n", encoding="utf-8")
            with (
                patch.object(signal_writer, "MANIFEST", manifest),
                patch.object(signal_writer, "STATE", state),
                patch.object(signal_writer, "SIGNAL", signal),
            ):
                self.assertEqual(signal_writer.main(), 0)
            self.assertEqual(
                signal.read_text(encoding="utf-8"),
                "batch-001-posts-0001-0050.zip\n",
            )

    def test_uploader_selects_only_names_from_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packages = root / "packages"
            packages.mkdir()
            first = packages / "batch-001.zip"
            second = packages / "batch-002.zip"
            first.write_bytes(b"one")
            second.write_bytes(b"two")
            signal = root / ".new-batch-signal"
            signal.write_text("batch-002.zip\n", encoding="utf-8")
            with (
                patch.object(uploader, "PACKAGES", packages),
                patch.object(uploader, "SIGNAL_PATH", signal),
            ):
                self.assertEqual(uploader.signaled_packages(), [second])


if __name__ == "__main__":
    unittest.main()