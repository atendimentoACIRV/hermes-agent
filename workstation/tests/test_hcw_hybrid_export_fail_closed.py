"""Regression: exporting must never claim decoded frames that do not exist."""
import subprocess
from unittest.mock import patch

import pytest

from workstation.creative_document import create_empty_project
from workstation.creative_export import ExportEngineError, VideoExportRequest, _decode_frame_hash, export_composition_to_video
from workstation.creative_time import RationalFps, CanonicalTime


def test_decoder_failure_cannot_generate_synthetic_hash(tmp_path):
    failed = subprocess.CompletedProcess(["ffmpeg"], 1, stdout=b"", stderr=b"bad media")
    with patch("workstation.creative_export.subprocess.run", return_value=failed):
        with pytest.raises(ExportEngineError, match="decod"):
            _decode_frame_hash(tmp_path / "missing.mp4", 3, RationalFps(30, 1))


def test_missing_visual_source_does_not_export_black_fallback(tmp_path):
    doc = create_empty_project(width=64, height=64, duration_seconds=2)
    comp = doc.compositions[0]
    req = VideoExportRequest(project_id=doc.project_id, composition_id=comp.composition_id,
        output_path=tmp_path / "output.mp4", width=64, height=64,
        fps=RationalFps(30, 1), duration=CanonicalTime.from_seconds(2))
    with patch("workstation.creative_export.subprocess.Popen") as spawn:
        with pytest.raises(ExportEngineError, match="visual source|rendered composition"):
            export_composition_to_video(doc, req, workspace_root=tmp_path)
    spawn.assert_not_called()
    assert not req.output_path.exists()
