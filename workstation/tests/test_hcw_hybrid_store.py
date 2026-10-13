"""H-C2: source-true, immutable hybrid EffectCraft/HyperFrames project revisions."""
import hashlib
import json

import pytest

from hermes_constants import reset_hermes_home_override, set_hermes_home_override
from workstation.creative_project_store import (
    CreativeConflictError, load_creative_revision, save_hybrid_project_revision,
)


def _sources():
    ec = b'{"version":1,"composition":"motion"}'
    html = b"<!DOCTYPE html><html><body>Animated source</body></html>"
    config = b'{"width":640,"height":360,"fps":30}'
    native = {"compositions/main.ecproj": ec, "procedural/hero/index.html": html,
              "procedural/hero/hyperframes.json": config}
    specs = [{"id": "a" * 32, "engine": "effectcraft", "source_ref": "compositions/main.ecproj",
              "source_sha256": hashlib.sha256(ec).hexdigest()},
             {"id": "b" * 32, "engine": "hyperframes", "source_ref": "procedural/hero/index.html",
              "source_sha256": hashlib.sha256(html).hexdigest()}]
    source = {"project": "Hybrid Test", "metadata": {"native_compositions": specs}}
    return source, native


def test_hybrid_revision_round_trip_preserves_both_natives_and_reopen(tmp_path):
    token = set_hermes_home_override(tmp_path / "profile")
    try:
        source, native = _sources()
        one = save_hybrid_project_revision(source, native_files=native)
        again = load_creative_revision(one.project_id, one.revision_id)
        assert again == one
        assert again.engine == "creative-document"
        assert len(again.native_files) == 3
        assert json.loads(again.source_path.read_text()) == source
        assert (again.manifest_path.parent / "compositions/main.ecproj").read_bytes() == native["compositions/main.ecproj"]
        assert (again.manifest_path.parent / "procedural/hero/index.html").read_bytes() == native["procedural/hero/index.html"]
        changed = dict(native)
        changed["procedural/hero/index.html"] = b"<!DOCTYPE html>updated"
        altered = dict(source)
        altered["metadata"] = dict(source["metadata"])
        specs = [dict(i) for i in source["metadata"]["native_compositions"]]
        specs[1]["source_sha256"] = hashlib.sha256(changed["procedural/hero/index.html"]).hexdigest()
        altered["metadata"]["native_compositions"] = specs
        two = save_hybrid_project_revision(altered, native_files=changed, project_id=one.project_id,
                                         parent_revision=one.revision_id, if_match=one.etag)
        assert one.source_path.read_bytes() != two.source_path.read_bytes()
        assert (one.manifest_path.parent / "procedural/hero/index.html").read_bytes() == native["procedural/hero/index.html"]
        with pytest.raises(CreativeConflictError, match="409 Conflict"):
            save_hybrid_project_revision(altered, native_files=changed, project_id=two.project_id,
                                         parent_revision=two.revision_id, if_match=one.etag)
    finally:
        reset_hermes_home_override(token)


@pytest.mark.parametrize("case", ["missing", "tamperedhash", "badengine", "escape", "duplicate"])
def test_hybrid_invalid_sources_fail_before_persistence(tmp_path, case):
    token = set_hermes_home_override(tmp_path / "profile")
    try:
        source, native = _sources()
        if case == "missing":
            del native["compositions/main.ecproj"]
        elif case == "tamperedhash":
            source["metadata"]["native_compositions"][0]["source_sha256"] = "f" * 64
        elif case == "badengine":
            source["metadata"]["native_compositions"][0]["engine"] = "unknown"
        elif case == "escape":
            source["metadata"]["native_compositions"][0]["source_ref"] = "../secret"
        else:
            source["metadata"]["native_compositions"][1]["id"] = "a" * 32
        with pytest.raises(ValueError):
            save_hybrid_project_revision(source, native_files=native)
        root = tmp_path / "profile" / "workstation" / "creative" / "projects"
        assert not root.exists() or not list(root.iterdir())
    finally:
        reset_hermes_home_override(token)


def test_canonical_creative_document_save_reopens_hybrid_native_sources(tmp_path):
    from workstation.creative_document import create_empty_project
    from workstation.creative_project_store import save_creative_document, load_creative_document
    token = set_hermes_home_override(tmp_path / "profile")
    try:
        source, natives = _sources()
        doc = create_empty_project(name="Joint composition")
        doc.metadata.update(source["metadata"])
        revision = save_creative_document(doc, native_files=natives)
        reopened = load_creative_document(revision.project_id, revision.revision_id)
        assert reopened.project_id == doc.project_id
        assert reopened.metadata["native_compositions"] == source["metadata"]["native_compositions"]
        assert len(revision.native_files) == 3
    finally:
        reset_hermes_home_override(token)


def test_hybrid_dependency_cycle_rejected_before_persistence(tmp_path):
    token = set_hermes_home_override(tmp_path / "profile")
    try:
        source, native = _sources()
        source["metadata"]["native_dependencies"] = [
            {"parent": "a" * 32, "child": "b" * 32},
            {"parent": "b" * 32, "child": "a" * 32},
        ]
        with pytest.raises(ValueError, match="cycle"):
            save_hybrid_project_revision(source, native_files=native)
        root = tmp_path / "profile" / "workstation" / "creative" / "projects"
        assert not root.exists() or not list(root.iterdir())
    finally:
        reset_hermes_home_override(token)


def test_declared_parameter_bindings_are_validated_on_hybrid_commit(tmp_path):
    token = set_hermes_home_override(tmp_path / "profile")
    try:
        source, native = _sources()
        source["metadata"]["native_parameters"] = {"title": {"type": "string", "value": "Hello"}}
        source["metadata"]["native_bindings"] = [
            {"parameter": "title", "composition_id": "a" * 32, "property_path": "text/source"},
            {"parameter": "title", "composition_id": "b" * 32, "property_path": "params/title"},
        ]
        saved = save_hybrid_project_revision(source, native_files=native)
        assert load_creative_revision(saved.project_id, saved.revision_id) == saved
        source["metadata"]["native_bindings"][1]["composition_id"] = "c" * 32
        with pytest.raises(ValueError, match="unknown"):
            save_hybrid_project_revision(source, native_files=native)
    finally:
        reset_hermes_home_override(token)
