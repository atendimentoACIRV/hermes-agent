"""Real EffectCraft smoke test. Opt in by setting EFFECTCRAFT_CLI to a built CLI.

Unlike mock renderer tests, this launches EffectCraft and decodes its output PNG.
No network access and all native files live in pytest tmp_path.
"""
import json
import os
from pathlib import Path
import subprocess

import pytest
from PIL import Image


def _cli() -> str:
    cli = os.getenv("EFFECTCRAFT_CLI")
    if not cli or not Path(cli).is_file():
        pytest.skip("Native EffectCraft binary not explicitly configured")
    return cli


def _run(cli: str, *args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([cli, *args], text=True, capture_output=True, timeout=45, check=False)
    assert result.returncode == 0, (
        f"EffectCraft invocation failed ({result.returncode}): {args!r}\n"
        f"stdout={result.stdout[-2400:]}\nstderr={result.stderr[-2400:]}"
    )
    return result


def test_effectcraft_native_persists_and_renders_real_frame(tmp_path: Path):
    cli = _cli()
    project = tmp_path / "native.ecproj"
    frame = tmp_path / "native.png"

    new_comp = json.dumps({
        "name": "HermesNativeSmoke", "width": 320, "height": 180,
        "frameRate": 30, "duration": 2,
    }, separators=(",", ":"))
    created = _run(cli, "--empty", "--save-as", str(project), "exec", "comp.new",
                   "--params", new_comp, "--json")
    assert project.is_file() and project.stat().st_size > 64, created.stdout

    reopened = _run(cli, "--project", str(project), "info", "--json")
    saved = json.loads(reopened.stdout)
    assert any(item.get("name") == "HermesNativeSmoke"
               for item in saved["project"]["items"])

    _run(cli, "--project", str(project), "render-frame",
         "--time", "0", "--out", str(frame))
    assert frame.is_file() and frame.stat().st_size > 100
    with Image.open(frame) as image:
        assert image.format == "PNG"
        assert image.size == (320, 180)
        image.load()


def test_effectcraft_native_imports_rgba_sequence_and_composites_pixels(tmp_path: Path):
    """Real file.import + save/reopen + seek, not an inspection-only mocked import."""
    cli = _cli()
    project = tmp_path / "base.ecproj"
    imported = tmp_path / "imported.ecproj"
    frame_a, frame_b = tmp_path / "a.png", tmp_path / "b.png"
    sequence = tmp_path / "sequence"
    sequence.mkdir()
    from PIL import ImageDraw

    for idx in range(3):
        canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((idx * 12, 4, idx * 12 + 15, 24), fill=(255, 125, 59, 255))
        canvas.save(sequence / f"clip_{idx:04d}.png")

    comp = json.dumps({
        "name": "HermesFootage", "width": 64, "height": 64, "frameRate": 30,
        "duration": 1,
    }, separators=(",", ":"))
    _run(cli, "--empty", "--save-as", str(project), "exec", "comp.new",
         "--params", comp, "--json")
    footage = json.dumps({
        "paths": [str(sequence / "clip_0000.png")], "sequence": True,
        "frameRate": 30, "addToComp": True,
    }, separators=(",", ":"))
    from workstation.creative_hybrid_footage import (
        validate_rgba_footage, effectcraft_import_invocation,
    )
    inspected = validate_rgba_footage(sequence, frame_count=3, width=64, height=64)
    native = effectcraft_import_invocation(
        inspected, fps=30, project_path=project, output_path=imported,
        executable_path=Path(cli), workspace_root=tmp_path,
    )
    assert native.engine == "effectcraft"
    assert native.executable_sha256
    assert json.loads(native.argv[native.argv.index("--params") + 1]) == json.loads(footage)
    _run(cli, *native.argv[1:])
    assert imported.is_file() and imported.stat().st_size > 64

    reopened = json.loads(_run(cli, "--project", str(imported), "info", "--json").stdout)
    comps = [x for x in reopened["project"]["items"] if x.get("type") == "Composition"]
    assert any(x.get("layers", 0) >= 1 for x in comps), reopened
    _run(cli, "--project", str(imported), "render-frame",
         "--time", "0", "--out", str(frame_a))
    _run(cli, "--project", str(imported), "render-frame",
         "--time", "0.066667", "--out", str(frame_b))
    with Image.open(frame_a) as im_a, Image.open(frame_b) as im_b:
        assert im_a.size == im_b.size == (64, 64)
        assert im_a.convert("RGBA").tobytes() != im_b.convert("RGBA").tobytes()
