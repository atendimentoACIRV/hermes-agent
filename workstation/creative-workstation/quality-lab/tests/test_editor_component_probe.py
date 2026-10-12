"""Checks CQL Chromium component receipt integrity and cross-head fail-closed boundary.

The artifact itself was produced by real Chromium + React from PR #81, not these
unit tests. These checks do not rerun browser E2E or assert that H-C2 works.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "evidence" / "pr81-chromium-85b0448" / "CQL_CHROMIUM_UI_OBSERVATIONS.json"
PROBE = ROOT / "scripts" / "probe_editor_components.cjs"


class CqlChromiumEvidence(unittest.TestCase):
    def test_receipt_has_source_binding_and_separate_component_qualification(self):
        data = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(data["head"], "85b0448fa01261bf425764f188edf443d8194b8b")
        self.assertIn("no native Electron/TaskRun authority", data["scope"])
        self.assertEqual(data["pass"], 5)
        self.assertEqual(data["fail"], 4)
        self.assertEqual(len(data["observations"]), 9)
        for checksum in data["candidateSourceSha256"].values():
            self.assertRegex(checksum, r"^[0-9a-f]{64}$")

    def test_reproduced_failures_are_not_masked_as_success(self):
        data = json.loads(REPORT.read_text(encoding="utf-8"))
        observed = {o["id"]: o["status"] for o in data["observations"]}
        self.assertEqual(observed["UX-GRAPH-HOOKS"], "FAIL")
        self.assertEqual(observed["UX-RATIONAL-FPS"], "FAIL")
        self.assertEqual(observed["UX-PREVIEW-PLAY"], "FAIL")
        self.assertEqual(observed["UX-INSPECTOR-SPEED"], "FAIL")
        self.assertTrue(any("Rendered more hooks" in e for e in data["graphErrors"]))
        benchmark = data["seekBenchmark"]
        self.assertEqual(benchmark["count"], 12)
        self.assertEqual(len(benchmark["ms"]), 12)
        self.assertIn("NOT pixel render or Electron", benchmark["scope"])

    @unittest.skipUnless(shutil.which("node") and shutil.which("git"), "node and git required")
    def test_mismatched_candidate_head_fails_before_any_browser_or_evidence_write(self):
        with tempfile.TemporaryDirectory() as folder:
            # Own CQL worktree is safe: test only candidate HEAD rejection, no write.
            checkout = ROOT.parents[2]
            env = dict(os.environ, CQL_TARGET_HEAD="0" * 40,
                       CQL_PR81_CHECKOUT=str(checkout),
                       CQL_NODE_MODULES=str(checkout / "node_modules"),
                       CQL_UI_REPORT_DIR=str(Path(folder) / "never-create"))
            result = subprocess.run(["node", str(PROBE)], env=env,
                                    text=True, capture_output=True, timeout=10, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Refusing to test changed candidate HEAD", result.stderr)
            self.assertFalse((Path(folder) / "never-create").exists())


if __name__ == "__main__":
    unittest.main()
