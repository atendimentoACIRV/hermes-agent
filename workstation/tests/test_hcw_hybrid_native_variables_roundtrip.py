"""Opt-in real H-C1/H-C2/H-C3 variable-to-EffectCraft canonical revisions."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest
from PIL import Image

from workstation.creative_hyperframes_variables import validated_hyperframes_overrides


def _run(executable: Path, *args: str) -> str:
    r = subprocess.run([str(executable), *map(str, args)], shell=False,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=180, check=False)
    assert r.returncode == 0, (
        f"Nonzero exit={r.returncode}, argv={args!r}; "
        f"stdout={r.stdout[-2000:]}; stderr={r.stderr[-2000:]}"
    )
    return r.stdout


def _pixel_hash(path: Path) -> str:
    with Image.open(path) as image:
        assert image.format == "PNG"
        return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()


def test_two_declared_hyperframes_edits_and_effectcraft_edit_share_revisions(tmp_path: Path):
    """Two independent native engines alter same canonical project's three revisions.

    Files are real engine artifacts. The source is never rewritten. Runtime
    TaskRun approval/Electron editing remain separate acceptance criteria.
    """
    root = os.getenv("HYPERFRAMES_OFFICIAL_CHECKOUT")
    node = os.getenv("HYPERFRAMES_NODE")
    ec = os.getenv("EFFECTCRAFT_CLI")
    if not root or not node or not ec:
        pytest.skip("Explicit native source/Node/EffectCraft opt-in required")
    root_path = Path(root)
    source = root_path / "packages/producer/tests/variables-prod/src"
    html_path = source / "index.html"
    cli = root_path / "packages/cli/bin/hyperframes.mjs"
    node_exe, ec_exe = Path(node), Path(ec)
    assert html_path.is_file() and cli.is_file()
    assert node_exe.is_file() and ec_exe.is_file()
    original_html = html_path.read_bytes()
    assert b"data-composition-variables" in original_html

    profiles = (
        {"title": "HCW BASE", "subtitle": "Original procedural parameter", "bgColor": "#0a3d62"},
        {"title": "HCW EDITED", "subtitle": "Independent procedural change", "bgColor": "#8b1e4f"},
    )
    source_outputs: list[tuple[Path, bytes, Path, str]] = []
    for index, variables in enumerate(profiles):
        native_config = validated_hyperframes_overrides(original_html, variables)
        variable_path = tmp_path / f"variables_{index}.json"
        variable_path.write_bytes(native_config)
        output = tmp_path / f"hf_render_{index}"
        args = (
            "render", str(source), "--format", "png-sequence",
            "--output", str(output), "--fps", "2", "--workers", "1",
            "--strict", "--strict-variables", "--no-best-effort",
            "--variables-file", str(variable_path),
        )
        _run(node_exe, str(cli), *args)
        frames = sorted(output.glob("frame_*.png"))
        assert len(frames) == 6
        with Image.open(frames[0]) as image:
            assert image.size == (1920, 1080)
            assert image.mode == "RGBA"
        source_outputs.append((output, native_config, frames[0], _pixel_hash(frames[0])))

    assert source_outputs[0][-1] != source_outputs[1][-1]
    assert html_path.read_bytes() == original_html

    comp = json.dumps({
        "name": "ParameterVersioned", "width": 1920, "height": 1080,
        "frameRate": 2, "duration": 3,
    }, separators=(",", ":"))
    initial = tmp_path / "unmodified.ecproj"
    _run(ec_exe, "--empty", "--save-as", str(initial),
         "exec", "comp.new", "--params", comp, "--json")

    projects: list[Path] = []
    output_hashes: list[str] = []
    for index, (_, _, first_frame, _) in enumerate(source_outputs):
        target = tmp_path / f"native-{index}.ecproj"
        import_params = json.dumps({
            "paths": [str(first_frame)], "sequence": True,
            "frameRate": 2, "addToComp": True,
        }, separators=(",", ":"))
        _run(ec_exe, "--project", str(initial), "--save-as", str(target),
             "exec", "file.import", "--params", import_params, "--json")
        assert target.is_file()
        check = tmp_path / f"native-output-{index}.png"
        _run(ec_exe, "--project", str(target), "render-frame",
             "--time", "0", "--out", str(check))
        output_hashes.append(_pixel_hash(check))
        projects.append(target)
    assert output_hashes[0] != output_hashes[1], (
        "EffectCraft did not reflect changed HyperFrames parameter output"
    )

    text_target = tmp_path / "native-effectcraft-text.ecproj"
    _run(ec_exe, "--project", str(projects[1]), "--save-as", str(text_target),
         "exec", "layer.newText",
         "--params", json.dumps({"text": "EFFECTCRAFT NATIVE", "size": 72,
                                 "fill": "#ffffff"}, separators=(",", ":")),
         "--json")
    final_frame = tmp_path / "native-effectcraft-text.png"
    _run(ec_exe, "--project", str(text_target),
         "render-frame", "--time", "0", "--out", str(final_frame))
    assert _pixel_hash(final_frame) != output_hashes[1]

    # Store both native sources in the SAME immutable canonical project.
    from hermes_constants import set_hermes_home_override, reset_hermes_home_override
    from workstation.creative_document import create_empty_project
    from workstation.creative_project_store import (
        CreativeConflictError, load_creative_revision, load_creative_document,
    )
    from workstation.creative_revision_cas import (
        publish_creative_document_cas, load_creative_head,
    )

    home = tmp_path / "isolated-hermes-profile"
    token = set_hermes_home_override(home)
    try:
        doc = create_empty_project(name="Dual-Engine Param Revision")
        ids = ("a" * 32, "b" * 32)
        references = [
            {"id": ids[0], "engine": "effectcraft",
             "source_ref": "compositions/main.ecproj", "source_sha256": ""},
            {"id": ids[1], "engine": "hyperframes",
             "source_ref": "procedural/hero/index.html",
             "source_sha256": hashlib.sha256(original_html).hexdigest()},
        ]
        doc.metadata["native_compositions"] = references
        doc.metadata["native_dependencies"] = [{"parent": ids[0], "child": ids[1]}]
        previous = None
        revisions = []
        for index, (project, (_, config, _, _)) in enumerate(
            zip((projects[0], projects[1], text_target),
                (source_outputs[0], source_outputs[1], source_outputs[1]))
        ):
            natives = {
                "compositions/main.ecproj": project.read_bytes(),
                "procedural/hero/index.html": original_html,
                "procedural/hero/hyperframes.json": config,
                "procedural/hero/silence.wav": (source / "silence.wav").read_bytes(),
            }
            references[0]["source_sha256"] = hashlib.sha256(
                natives["compositions/main.ecproj"]).hexdigest()
            doc.metadata["native_parameters"] = {
                "title": {"type": "string", "value": json.loads(config)["title"]},
                "bgColor": {"type": "color", "value": json.loads(config)["bgColor"]},
            }
            rev = publish_creative_document_cas(
                doc, native_files=natives,
                expected_head_revision=previous.revision_id if previous else None,
                expected_etag=previous.etag if previous else None,
                operation_id=f"{index + 1:032x}",
            )
            assert load_creative_revision(rev.project_id, rev.revision_id) == rev
            reopened = load_creative_document(rev.project_id, rev.revision_id)
            assert reopened.metadata["native_parameters"] == doc.metadata["native_parameters"]
            assert (rev.manifest_path.parent /
                    "procedural/hero/index.html").read_bytes() == original_html
            assert (rev.manifest_path.parent /
                    "procedural/hero/silence.wav").read_bytes() == (
                        source / "silence.wav").read_bytes()
            revisions.append(rev)
            previous = rev
        assert len({x.project_id for x in revisions}) == 1
        assert len({x.revision_id for x in revisions}) == 3
        assert load_creative_head(doc.project_id) == revisions[-1]
        assert revisions[0].source_sha256 != revisions[1].source_sha256
        assert revisions[1].source_sha256 != revisions[2].source_sha256
        assert (revisions[0].manifest_path.parent /
                "procedural/hero/hyperframes.json").read_bytes() != (
                    revisions[1].manifest_path.parent /
                    "procedural/hero/hyperframes.json").read_bytes()
        with pytest.raises(CreativeConflictError, match="409 Conflict"):
            publish_creative_document_cas(
                doc, native_files=natives,
                expected_head_revision=revisions[-1].revision_id,
                expected_etag=revisions[0].etag,
                operation_id="f" * 32,
            )
    finally:
        reset_hermes_home_override(token)
