"""PNG sequence verifier regressions: real decoded PNG pixels and fail-closed cases."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

try:
    from PIL import Image
except ImportError:
    Image = None

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_png_sequence.py"


@unittest.skipIf(Image is None, "Pillow is not installed in this interpreter")
class RGBASequenceAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("cql_png_verifier", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        for i in range(2):
            picture = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
            picture.putpixel((i + 4, 5), (255, 70, 20, 255))
            picture.save(self.folder / f"frame_{i:06d}.png")

    def test_real_rgba_and_motion(self):
        result = self.module.inspect(self.folder, 2)
        self.assertEqual(result["status"], "PASS_NATIVE")
        self.assertEqual(result["unique_pixel_frames"], 2)
        self.assertEqual(result["alpha_min"], 0)
        self.assertEqual(result["alpha_max"], 255)

    def test_rejects_wrong_count(self):
        with self.assertRaisesRegex(ValueError, "frame count mismatch"):
            self.module.inspect(self.folder, 3)

    def test_rejects_static(self):
        (self.folder / "frame_000001.png").write_bytes((self.folder / "frame_000000.png").read_bytes())
        with self.assertRaisesRegex(ValueError, "no source motion"):
            self.module.inspect(self.folder, 2)

    def test_rejects_opaque(self):
        for file in self.folder.glob("*.png"):
            Image.new("RGBA", (20, 20), (255, 0, 0, 255)).save(file)
        with self.assertRaisesRegex(ValueError, "alpha not compositable"):
            self.module.inspect(self.folder, 2)

    def test_rejects_dimensions(self):
        Image.new("RGBA", (10, 10), (0, 0, 0, 0)).save(self.folder / "frame_000001.png")
        with self.assertRaisesRegex(ValueError, "inconsistent dimensions"):
            self.module.inspect(self.folder, 2)


if __name__ == "__main__":
    unittest.main()
