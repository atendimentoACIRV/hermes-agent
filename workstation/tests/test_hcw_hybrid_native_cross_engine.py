"""Opt-in real HyperFrames->EffectCraft source E2E: no mock engines.

Supply HYPERFRAMES_MOTION_FRAMES from the pinned official HyperFrames CLI render,
and EFFECTCRAFT_CLI from a trusted compiled EffectCraft executable.
Both run on the user's authorized machine; temporary project files remain isolated.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest
from PIL import Image

from workstation.creative_hybrid_footage import (
    validate_rgba_footage, effectcraft_import_invocation,
)


def _run(executable: Path, *argv: str) -> str:
    result = subprocess.run(
        [str(executable), *argv], capture_output=True, text=True,
        encoding="utf-8", errors="replace", shell=False, timeout=90,
        check=False,
    )
    assert result.returncode == 0, (
        f"Native engine returned {result.returncode}; "
        f"argv={argv!r}; stdout={result.stdout[-1200:]}; stderr={result.stderr[-1200:]}"
    )
    return result.stdout


def test_official_hyperframes_moving_rgba_imports_and_seeks_in_effectcraft(tmp_path: Path):
    """Pin observed frame hashes, validate alpha/motion, import, reopen, decode seeks."""
    ec = os.environ.get("EFFECTCRAFT_CLI")
    hf = os.environ.get("HYPERFRAMES_MOTION_FRAMES")
    if not ec or not hf:
        pytest.skip("Real cross-engine run requires explicit engine and producer paths")
    executable = Path(ec)
    source = Path(hf)
    if not executable.is_file() or not source.is_dir():
        pytest.fail("Configured native engine or HyperFrames output missing")

    workspace_sequence = tmp_path / "producer-frames"
    workspace_sequence.mkdir()
    originals = sorted(source.glob("*.png"))
    assert len(originals) == 60
    for image in originals:
        assert not image.is_symlink()
        shutil.copyfile(image, workspace_sequence / image.name)

    footage = validate_rgba_footage(
        workspace_sequence, frame_count=60, width=640, height=360,
    )
    assert footage.has_alpha and footage.has_motion
    assert len(set(footage.frame_hashes)) > 1

    source_project = tmp_path / "before-import.ecproj"
    destination = tmp_path / "after-import.ecproj"
    new_comp = json.dumps({
        "name": "HyperFramesAnimatedOverlay", "width": 640, "height": 360,
        "frameRate": 30, "duration": 2,
    }, separators=(",", ":"))
    _run(executable, "--empty", "--save-as", str(source_project),
         "exec", "comp.new", "--params", new_comp, "--json")
    assert source_project.is_file()

    invocation = effectcraft_import_invocation(
        footage, fps=30, project_path=source_project, output_path=destination,
        executable_path=executable, workspace_root=tmp_path,
    )
    invocation.validate()
    _run(executable, *invocation.argv[1:])
    assert destination.is_file()
    reopened = json.loads(_run(executable, "--project", str(destination), "info", "--json"))
    comps = [item for item in reopened["project"]["items"]
             if item.get("type") == "Composition"]
    assert any(item.get("layers", 0) > 0 for item in comps)

    screenshots = []
    for i in (0, 30, 45):
        frame = tmp_path / f"effectcraft_{i:02d}.png"
        _run(executable, "--project", str(destination), "render-frame",
             "--frame", str(i), "--out", str(frame))
        with Image.open(frame) as pixels:
            assert pixels.format == "PNG" and pixels.size == (640, 360)
            rgba = pixels.convert("RGBA")
            screenshots.append(hashlib.sha256(rgba.tobytes()).hexdigest())
    assert len(set(screenshots)) > 1, "EffectCraft did not advance HyperFrames native footage"

    proof = {
        "hf_frame_count": footage.frame_count,
        "hf_unique_hash_count": len(set(footage.frame_hashes)),
        "hf_first_sha256": footage.frame_hashes[0],
        "ec_native_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "ec_render_pixel_sha256": screenshots,
    }
    (tmp_path / "native-cross-engine-proof.json").write_text(
        json.dumps(proof, indent=2), encoding="utf-8"
    )

    # Second engine-native edit: new EffectCraft title and a non-default Gaussian
    # Blur on the imported HyperFrames footage. Compare ACTUAL decoded frames.
    titled = tmp_path / "with-text.ecproj"
    effected = tmp_path / "effect-default.ecproj"
    blurred = tmp_path / "effect-blur20.ecproj"
    heading = json.dumps({"text": "HERMES WORK", "size": 42, "fill": "#ffffff"},
                         separators=(",", ":"))
    _run(executable, "--project", str(destination), "--save-as", str(titled),
         "exec", "layer.newText", "--params", heading, "--json")
    titled_info = json.loads(_run(executable, "--project", str(titled), "info", "--json"))
    layers = titled_info["activeComp"]["layers"]
    assert any(layer["type"] == "Text" and layer["name"] == "HERMES WORK"
               for layer in layers)
    footage_layer = next(layer for layer in layers if layer["type"] == "Footage")
    blur_spec = json.dumps({"layer": footage_layer["id"], "effect": "Gaussian Blur"},
                           separators=(",", ":"))
    _run(executable, "--project", str(titled), "--save-as", str(effected),
         "exec", "effect.apply", "--params", blur_spec, "--json")
    _run(executable, "--project", str(effected), "--save-as", str(blurred),
         "set", "-", str(footage_layer["id"]), "effects/#1/blurriness",
         "20", "--json")
    changed = json.loads(_run(executable, "--project", str(blurred), "props",
                              "-", str(footage_layer["id"]), "--flat", "--json"))
    assert any(prop["path"] == "effects/#1/blurriness" and prop["value"] == 20
               for prop in changed["properties"])

    decorated_pixel_hashes = []
    for project in (destination, titled, blurred):
        output = tmp_path / f"decorated-{len(decorated_pixel_hashes)}.png"
        _run(executable, "--project", str(project), "render-frame", "--time",
             "1.05", "--out", str(output))
        with Image.open(output) as image:
            assert image.size == (640, 360)
            decorated_pixel_hashes.append(
                hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()
            )
    assert len(set(decorated_pixel_hashes)) == 3, (
        "Either typography or actual blurred footage did not affect rendered pixels"
    )
    assert blurred.read_bytes() != titled.read_bytes()


def test_real_effectcraft_import_via_canonical_process_supervisor(tmp_path: Path):
    """Executes native import under real policy, session and ProcessRegistry.

    Uses no mocked approvals. Production TaskRun admission remains a separate
    runtime gate; this test verifies the Hermes native process seam itself.
    """
    ec = os.environ.get("EFFECTCRAFT_CLI")
    hf = os.environ.get("HYPERFRAMES_MOTION_FRAMES")
    if not ec or not hf:
        pytest.skip("Supervisor E2E requires native engine and moving footage")
    from hermes_constants import reset_hermes_home_override, set_hermes_home_override
    from tools.approval_context import reset_current_session_key, set_current_session_key
    from tools.process_registry import ProcessRegistry
    from workstation.config import WorkstationConfig
    from workstation.creative_process import (
        CreativeExecutionScope, start_creative_process, wait_creative_process,
    )

    profile = tmp_path / "hermes-profile"
    workspace = profile / "workstation" / "creative" / "native-qualification"
    sequence = workspace / "motion"
    sequence.mkdir(parents=True)
    for original in sorted(Path(hf).glob("*.png")):
        assert not original.is_symlink()
        shutil.copyfile(original, sequence / original.name)
    footage = validate_rgba_footage(sequence, frame_count=60, width=640, height=360)
    assert footage.has_alpha and footage.has_motion

    cli = Path(ec)
    project = workspace / "base.ecproj"
    imported = workspace / "supervised-import.ecproj"
    _run(cli, "--empty", "--save-as", str(project), "exec", "comp.new",
         "--params", json.dumps({
             "name": "TaskOwnedNative", "width": 640, "height": 360,
             "frameRate": 30, "duration": 2,
         }), "--json")
    scope = CreativeExecutionScope(
        str(profile), "native-e2e-session", "native-e2e-task", str(workspace),
    )
    invocation = effectcraft_import_invocation(
        footage, fps=30, project_path=project, output_path=imported,
        executable_path=cli, workspace_root=workspace,
    )
    home_token = set_hermes_home_override(profile)
    session_token = set_current_session_key("native-e2e-session")
    registry = ProcessRegistry()
    try:
        child = start_creative_process(
            WorkstationConfig({"creative": {"enabled": True}}),
            scope, invocation, registry=registry,
        )
        assert child.owner_task_id == scope.task_id
        assert child.session_key == scope.session_key
        result = wait_creative_process(scope, child.id, timeout=60, registry=registry)
        assert result.get("status") == "exited" and result.get("exit_code") == 0, result
        assert imported.is_file()
        inspected = json.loads(_run(cli, "--project", str(imported), "info", "--json"))
        assert any(layer["type"] == "Footage"
                   for layer in inspected["activeComp"]["layers"])
    finally:
        registry.kill_all()
        reset_current_session_key(session_token)
        reset_hermes_home_override(home_token)


def test_real_native_sources_saved_in_canonical_creative_document(tmp_path: Path):
    """Real engine-native bytes, not mocked placeholder files, survive revisions."""
    ecdir = os.environ.get("EFFECTCRAFT_ENRICHMENT_DIR")
    hfsource = os.environ.get("HYPERFRAMES_SOURCE_HTML")
    if not ecdir or not hfsource:
        pytest.skip("Real source revision requires native output and official HTML")
    base = Path(ecdir) / "02-hyperframes.ecproj"
    altered = Path(ecdir) / "05-blur20.ecproj"
    html_file = Path(hfsource)
    if not all(p.is_file() for p in (base, altered, html_file)):
        pytest.fail("Canonical E2E input missing")

    from hermes_constants import reset_hermes_home_override, set_hermes_home_override
    from workstation.creative_document import create_empty_project
    from workstation.creative_project_store import (
        CreativeConflictError, load_creative_document, load_creative_revision,
        save_creative_document,
    )

    profile_token = set_hermes_home_override(tmp_path / "canonical-profile")
    try:
        native = {
            "compositions/effectcraft.ecproj": base.read_bytes(),
            "procedural/hyperframes/index.html": html_file.read_bytes(),
            "procedural/hyperframes/hyperframes.json": (
                b'{"width":640,"height":360,"fps":30}'
            ),
        }
        ids = ("a" * 32, "b" * 32)
        specs = [
            {
                "id": ids[0], "engine": "effectcraft",
                "source_ref": "compositions/effectcraft.ecproj",
                "source_sha256": hashlib.sha256(
                    native["compositions/effectcraft.ecproj"]).hexdigest(),
            },
            {
                "id": ids[1], "engine": "hyperframes",
                "source_ref": "procedural/hyperframes/index.html",
                "source_sha256": hashlib.sha256(
                    native["procedural/hyperframes/index.html"]).hexdigest(),
            },
        ]
        doc = create_empty_project(name="Hermes Hybrid Native Verified")
        doc.metadata.update({
            "native_compositions": specs,
            "native_dependencies": [{"parent": ids[0], "child": ids[1]}],
        })
        before = save_creative_document(doc, native_files=native)
        reopened = load_creative_document(before.project_id, before.revision_id)
        assert reopened.project_id == doc.project_id
        assert reopened.metadata["native_compositions"] == specs
        assert (before.manifest_path.parent /
                "compositions/effectcraft.ecproj").read_bytes() == base.read_bytes()
        assert (before.manifest_path.parent /
                "procedural/hyperframes/index.html").read_bytes() == html_file.read_bytes()

        native_after = dict(native)
        native_after["compositions/effectcraft.ecproj"] = altered.read_bytes()
        doc.metadata["native_compositions"][0]["source_sha256"] = (
            hashlib.sha256(altered.read_bytes()).hexdigest()
        )
        after = save_creative_document(
            doc, native_files=native_after,
            parent_revision=before.revision_id, if_match=before.etag,
        )
        assert after.parent_revision == before.revision_id
        assert load_creative_revision(after.project_id, after.revision_id) == after
        assert (before.manifest_path.parent /
                "compositions/effectcraft.ecproj").read_bytes() == base.read_bytes()
        assert (after.manifest_path.parent /
                "compositions/effectcraft.ecproj").read_bytes() == altered.read_bytes()
        with pytest.raises(CreativeConflictError, match="409 Conflict"):
            save_creative_document(
                doc, native_files=native_after, parent_revision=after.revision_id,
                if_match=before.etag,
            )
    finally:
        reset_hermes_home_override(profile_token)


def test_pinned_hyperframes_cli_generates_real_motion_consumed_by_effectcraft(tmp_path: Path):
    """Full engine producer->consumer tracer using source pinned to upstream SHA.

    Runs only on explicitly configured native infrastructure; normal offline
    unit CI skips. No synthetic frames, no backend black-frame fallback.
    """
    root = os.environ.get("HYPERFRAMES_OFFICIAL_CHECKOUT")
    ec = os.environ.get("EFFECTCRAFT_CLI")
    node = os.environ.get("HYPERFRAMES_NODE")
    if not root or not ec or not node:
        pytest.skip("Native full producer->consumer CLI test requires three opt-ins")
    checkout = Path(root)
    node_executable = Path(node)
    executable = Path(ec)
    cli_entry = checkout / "packages" / "cli" / "bin" / "hyperframes.mjs"
    fixture = checkout / "packages" / "producer" / "tests" / "distributed" / "png-sequence" / "src"
    assert node_executable.is_file() and cli_entry.is_file() and fixture.is_dir()
    git = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        check=False, capture_output=True, text=True, timeout=15,
    )
    assert git.returncode == 0
    assert git.stdout.strip() == "6ae1af7470133db72de6d9bbceeaf80e85695c68"

    producer_dir = tmp_path / "hyperframes-native-png"
    env = {**os.environ, "HYPERFRAMES_TELEMETRY": "0",
           "HYPERFRAMES_SKIP_SKILLS": "1"}
    result = subprocess.run(
        [str(node_executable), str(cli_entry), "render", str(fixture),
         "--format", "png-sequence", "--output", str(producer_dir),
         "--fps", "30", "--workers", "1", "--strict", "--no-best-effort"],
        cwd=checkout, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", timeout=240,
        check=False,
    )
    assert result.returncode == 0, result.stdout[-4000:]
    footage = validate_rgba_footage(
        producer_dir, frame_count=60, width=640, height=360,
    )
    assert footage.has_alpha and footage.has_motion
    assert len(set(footage.frame_hashes)) >= 2

    project = tmp_path / "effectcraft-base.ecproj"
    imported = tmp_path / "effectcraft-imported.ecproj"
    spec = json.dumps({
        "name": "HFtoECReal", "width": 640, "height": 360,
        "frameRate": 30, "duration": 2,
    }, separators=(",", ":"))
    _run(executable, "--empty", "--save-as", str(project),
         "exec", "comp.new", "--params", spec, "--json")
    invocation = effectcraft_import_invocation(
        footage, fps=30, project_path=project, output_path=imported,
        executable_path=executable, workspace_root=tmp_path,
    )
    invocation.validate()
    _run(executable, *invocation.argv[1:])
    assert imported.is_file()

    rendered_pixel_hashes = set()
    for moment in (0, 31, 45):
        png = tmp_path / f"composited-{moment:02d}.png"
        _run(executable, "--project", str(imported),
             "render-frame", "--frame", str(moment), "--out", str(png))
        with Image.open(png) as image:
            assert image.format == "PNG" and image.size == (640, 360)
            rendered_pixel_hashes.add(
                hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()
            )
    assert len(rendered_pixel_hashes) > 1


def test_native_hybrid_mp4_export_decodes_and_contains_motion(tmp_path: Path):
    """Re-encode the genuinely composited .ecproj; independently validate video."""
    ecdir = os.environ.get("EFFECTCRAFT_ENRICHMENT_DIR")
    ec = os.environ.get("EFFECTCRAFT_CLI")
    if not ecdir or not ec:
        pytest.skip("Explicit trusted native hybrid source and EffectCraft CLI required")
    source = Path(ecdir) / "05-blur20.ecproj"
    if not source.is_file():
        pytest.fail("Real hybrid source unavailable")
    ffprobe = shutil.which("ffprobe")
    ffmpeg = shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        pytest.skip("Video export qualification requires ffprobe and ffmpeg")
    video = tmp_path / "verified-hybrid.mp4"
    _run(Path(ec), "--project", str(source), "render",
         "--out", str(video), "--format", "h264",
         "--start", "0", "--end", "2", "--fps", "30", "--quality", "draft")
    assert video.is_file() and video.stat().st_size > 1000
    probe = subprocess.run(
        [ffprobe, "-v", "error", "-count_frames", "-select_streams", "v:0",
         "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration",
         "-of", "json", str(video)],
        capture_output=True, text=True, check=False, timeout=30,
    )
    assert probe.returncode == 0, probe.stderr
    stream = json.loads(probe.stdout)["streams"][0]
    assert stream["codec_name"] == "h264"
    assert (stream["width"], stream["height"]) == (640, 360)
    assert stream["r_frame_rate"] == "30/1"
    assert int(stream["nb_read_frames"]) == 60
    assert abs(float(stream["duration"]) - 2) < 0.01

    decoded = []
    for second in ("0", "1.05"):
        png = tmp_path / f"decoded-{second}.png"
        ffmpeg_result = subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
             "-ss", second, "-i", str(video), "-frames:v", "1", str(png)],
            capture_output=True, check=False, timeout=30,
        )
        assert ffmpeg_result.returncode == 0, ffmpeg_result.stderr
        with Image.open(png) as image:
            assert image.size == (640, 360)
            decoded.append(hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest())
    assert decoded[0] != decoded[1], "Exported H.264 video lacks moving source content"
