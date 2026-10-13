"""H-C1 preflight contract for a genuine, numbered transparent video source."""
from pathlib import Path

import pytest
from PIL import Image

from workstation.creative_hybrid_footage import (
    HybridFootageError, validate_rgba_footage, effectcraft_import_command,
)


def _frames(folder: Path, *, moving: bool = True, opaque: bool = False):
    folder.mkdir()
    for index in range(3):
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0 if not opaque else 255))
        if index or not moving:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.rectangle((index * 2 if moving else 0, 4, 10, 15),
                           fill=(255, 126, 59, 255))
        img.save(folder / f"shot_{index:04d}.png")
    return folder


def test_real_png_sequence_is_verified_and_import_command_retains_30_fps(tmp_path):
    folder = _frames(tmp_path / "frames")
    inspected = validate_rgba_footage(folder, frame_count=3, width=32, height=32)
    assert inspected.frame_count == 3
    assert inspected.has_alpha and inspected.has_motion
    cmd = effectcraft_import_command(inspected, fps=30)
    assert cmd["command"] == "file.import"
    assert cmd["params"]["sequence"] is True
    assert cmd["params"]["frameRate"] == 30
    assert cmd["params"]["addToComp"] is True
    assert cmd["params"]["paths"] == [str(folder / "shot_0000.png")]


@pytest.mark.parametrize("problem", ["missing", "opaque", "duplicate", "rgb", "symlink"])
def test_footage_failure_cannot_be_promoted(tmp_path, problem):
    folder = _frames(tmp_path / "frames", moving=problem != "duplicate", opaque=problem == "opaque")
    if problem == "missing":
        (folder / "shot_0001.png").unlink()
    if problem == "rgb":
        Image.new("RGB", (32, 32), "red").save(folder / "shot_0002.png")
    if problem == "symlink":
        link = folder / "shot_0001.png"
        link.unlink()
        try:
            link.symlink_to(folder / "shot_0000.png")
        except OSError:
            pytest.skip("Symlink creation not available in test environment")
    with pytest.raises(HybridFootageError):
        validate_rgba_footage(folder, frame_count=3, width=32, height=32)


def test_native_import_invocation_cannot_escape_workspace(tmp_path):
    from workstation.creative_hybrid_footage import effectcraft_import_invocation
    folder = _frames(tmp_path / "frames")
    inspected = validate_rgba_footage(folder, frame_count=3, width=32, height=32)
    project = tmp_path / "safe.ecproj"
    project.write_bytes(b"source")
    exe = tmp_path / "effectcraft-cli.exe"
    exe.write_bytes(b"native-test-executable")
    expected = tmp_path / "output.ecproj"
    argv = effectcraft_import_invocation(
        inspected, fps=30, project_path=project, output_path=expected,
        executable_path=exe, workspace_root=tmp_path,
    )
    assert argv.argv[0] == str(exe)
    assert argv.argv[argv.argv.index("--params") + 1]
    argv.validate()
    with pytest.raises(HybridFootageError, match="escapes"):
        effectcraft_import_invocation(
            inspected, fps=30, project_path=project,
            output_path=tmp_path.parent / "escaped.ecproj",
            executable_path=exe, workspace_root=tmp_path,
        )
    exe.write_bytes(b"binary-drift")
    with pytest.raises(PermissionError, match="fingerprint drift"):
        argv.validate()


def test_native_import_refuses_overwrite(tmp_path):
    from workstation.creative_hybrid_footage import effectcraft_import_invocation
    folder = _frames(tmp_path / "frames")
    inspected = validate_rgba_footage(folder, frame_count=3, width=32, height=32)
    project = tmp_path / "safe.ecproj"
    project.write_bytes(b"source")
    exe = tmp_path / "effectcraft-cli.exe"
    exe.write_bytes(b"native-test-executable")
    with pytest.raises(HybridFootageError, match="new, absent"):
        effectcraft_import_invocation(
            inspected, fps=30, project_path=project, output_path=project,
            executable_path=exe, workspace_root=tmp_path,
        )
