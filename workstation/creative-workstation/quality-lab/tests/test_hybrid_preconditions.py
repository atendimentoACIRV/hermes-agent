"""Fail-closed hybrid CLI preconditions. Native success is independently exercised by run script."""
from pathlib import Path
import importlib.util
import tempfile
import unittest

try:
    import PIL
except ImportError:
    PIL = None

FILE = Path(__file__).resolve().parents[1] / "scripts" / "prove_effectcraft_hybrid.py"


@unittest.skipIf(PIL is None, "Pillow needed for native CLI experiment")
class NativeHybridPreconditions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("cql_hybrid", FILE)
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def test_missing_native_cli_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(FileNotFoundError, "CLI unavailable"):
                self.mod.prove(root / "absent.exe", root, root, root / "output")
            self.assertFalse((root / "output").exists())

    def test_existing_output_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cli = root / "cli.exe"
            cli.write_bytes(b"stub-not-executed")
            destination = root / "output"
            destination.mkdir()
            (destination / "valuable-project.ecproj").write_text("do-not-delete")
            with self.assertRaisesRegex(ValueError, "must be empty"):
                self.mod.prove(cli,root,root,destination)
            self.assertEqual((destination/"valuable-project.ecproj").read_text(),"do-not-delete")


if __name__=="__main__":
    unittest.main()
