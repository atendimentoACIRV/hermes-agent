"""Acceptance tests for the independent decoder. Uses real FFmpeg output, not mocks."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_native_export.py"
spec = importlib.util.spec_from_file_location("cql_video_verifier", SCRIPT)
verifier = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(verifier)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "native FFmpeg unavailable")
class NativeDecoderAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.video = self.root / "motion.mp4"
        result = subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
            "-i", "testsrc2=size=128x72:rate=12:duration=1",
            "-an", "-c:v", "mpeg4", "-q:v", "4", "-y", str(self.video)
        ], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))

    def test_native_motion_and_source_integrity(self):
        source = self.root / "source.ecproj"
        source.write_text('{"native":"fixture-only"}', encoding="utf-8")
        receipt = verifier.verify_video(self.video, source=source, expected_frames=12,
                                         expected_width=128, expected_height=72)
        self.assertEqual(receipt["status"], "PASS_NATIVE")
        self.assertEqual(receipt["decoded_frames"], 12)
        self.assertGreaterEqual(receipt["unique_frame_hashes"], 2)
        self.assertEqual(len(receipt["source_sha256"]), 64)
        self.assertIn("not native project reopen", receipt["scope"])

    def test_rejects_incorrect_frame_count(self):
        with self.assertRaisesRegex(verifier.VerificationError, "decoded frames mismatch"):
            verifier.verify_video(self.video, expected_frames=13)

    def test_rejects_missing_editable_source(self):
        with self.assertRaisesRegex(verifier.VerificationError, "editable source missing"):
            verifier.verify_video(self.video, source=self.root / "missing.ecproj")

    def test_rejects_invalid_video_even_if_file_exists(self):
        fake = self.root / "fake.mp4"
        fake.write_bytes(b"X" * 300)
        with self.assertRaisesRegex(verifier.VerificationError, "ffprobe failed"):
            verifier.verify_video(fake)

    def test_rejects_mismatched_width(self):
        with self.assertRaisesRegex(verifier.VerificationError, "width mismatch"):
            verifier.verify_video(self.video, expected_width=256)

    def test_rejects_static_when_motion_required(self):
        still = self.root / "still.mp4"
        result = subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
            "-i", "color=c=red:size=128x72:rate=12:duration=1",
            "-an", "-c:v", "mpeg4", "-q:v", "4", "-y", str(still)
        ], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0)
        with self.assertRaisesRegex(verifier.VerificationError, "no decoded motion"):
            verifier.verify_video(still)


if __name__ == "__main__":
    unittest.main()
