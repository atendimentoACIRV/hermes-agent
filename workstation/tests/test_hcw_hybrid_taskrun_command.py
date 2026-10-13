"""Actual claimed TaskRun must gate canonical human/AI command publication."""
from dataclasses import replace

import pytest

from gateway.session_context import scoped_current_session_id
from hermes_constants import set_hermes_home_override, reset_hermes_home_override
from hermes_cli import kanban_db
from hermes_cli.kanban_db_connect import connect_closing
from tools.approval_context import set_current_session_key, reset_current_session_key
from workstation.config import WorkstationConfig
from workstation.creative_commands import Actor, CreativeCommand
from workstation.creative_document import create_empty_project
from workstation.creative_transactions import CreativeTransaction
from workstation.creative_revision_cas import (
    publish_creative_document_cas, load_creative_head,
)
from workstation.creative_project_runtime import (
    CreativeRunContext, publish_creative_command_batch_for_run,
)


def _claimed_scope(home):
    workspace = home / "workstation" / "creative" / "projects"
    workspace.mkdir(parents=True)
    with connect_closing() as db:
        task_id = kanban_db.create_task(
            db, title="Hermes canonical editing", session_id="session-one",
            workspace_kind="dir", workspace_path=str(workspace),
        )
        task = kanban_db.claim_task(db, task_id, ttl_seconds=300)
    assert task is not None
    return CreativeRunContext(
        str(home), "session-key", "session-one",
        task_id, task.current_run_id,
    )


def test_live_taskrun_publishes_canonical_command_and_fences_other_session(tmp_path, monkeypatch):
    home = tmp_path / "profile"
    monkeypatch.setenv("HERMES_KANBAN_DB", str(home / "kanban.db"))
    ht = set_hermes_home_override(home)
    st = set_current_session_key("session-key")
    try:
        with scoped_current_session_id("session-one"):
            ctx = _claimed_scope(home)
            config = WorkstationConfig({"creative": {"enabled": True}})
            doc = create_empty_project(name="Live TaskRun")
            old = publish_creative_document_cas(doc, operation_id="a" * 32)
            command = CreativeCommand(
                "layer.create", {
                    "composition_id": doc.compositions[0].composition_id,
                    "layer_id": "d" * 32, "name": "Shared",
                }, Actor("human-id", "human_mouse"), "request-1",
            )
            tx = CreativeTransaction(commands=[command], transaction_id="b" * 32)
            result = publish_creative_command_batch_for_run(
                config, ctx, project_id=doc.project_id, transaction=tx,
                expected_head_revision=old.revision_id, expected_etag=old.etag,
            )
            assert result["operation_id"] == "b" * 32
            assert result["task_id"] == ctx.task_id
            assert result["run_id"] == ctx.run_id
            head = load_creative_head(doc.project_id)
            assert head is not None and head.revision_id == result["revision_id"]
            assert head.parent_revision == old.revision_id
            with pytest.raises(PermissionError):
                publish_creative_command_batch_for_run(
                    config, replace(ctx, session_id="other-session"),
                    project_id=doc.project_id, transaction=tx,
                    expected_head_revision=old.revision_id, expected_etag=old.etag,
                )
            assert load_creative_head(doc.project_id) == head
            with connect_closing() as db:
                db.execute("UPDATE tasks SET status='done' WHERE id=?", (ctx.task_id,))
                db.commit()
            with pytest.raises(PermissionError):
                publish_creative_command_batch_for_run(
                    config, ctx, project_id=doc.project_id, transaction=tx,
                    expected_head_revision=old.revision_id, expected_etag=old.etag,
                )
            assert load_creative_head(doc.project_id) == head
    finally:
        reset_current_session_key(st)
        reset_hermes_home_override(ht)


def test_live_taskrun_preserves_hybrid_natives_during_canonical_command(tmp_path, monkeypatch):
    """An ordinary layer edit cannot silently drop EffectCraft/HyperFrames sources."""
    import hashlib
    from workstation.creative_project_store import load_creative_revision

    home = tmp_path / "profile"
    monkeypatch.setenv("HERMES_KANBAN_DB", str(home / "kanban.db"))
    ht = set_hermes_home_override(home)
    st = set_current_session_key("session-key")
    try:
        with scoped_current_session_id("session-one"):
            ctx = _claimed_scope(home)
            config = WorkstationConfig({"creative": {"enabled": True}})
            doc = create_empty_project(name="Retain hybrid natives")
            native = {
                "compositions/main.ecproj": b"trusted-effectcraft-native-source",
                "procedural/main/index.html": b"<!doctype html><html><body>source</body></html>",
                "procedural/main/hyperframes.json": b'{"fps":30}',
            }
            doc.metadata["native_compositions"] = [
                {"id": "a" * 32, "engine": "effectcraft",
                 "source_ref": "compositions/main.ecproj",
                 "source_sha256": hashlib.sha256(native["compositions/main.ecproj"]).hexdigest()},
                {"id": "b" * 32, "engine": "hyperframes",
                 "source_ref": "procedural/main/index.html",
                 "source_sha256": hashlib.sha256(native["procedural/main/index.html"]).hexdigest()},
            ]
            first = publish_creative_document_cas(
                doc, native_files=native, operation_id="a" * 32,
            )
            command = CreativeCommand(
                "layer.create", {
                    "composition_id": doc.compositions[0].composition_id,
                    "layer_id": "c" * 32, "name": "Canonical overlay",
                }, Actor("human-id", "human_mouse"), "save-layer",
            )
            tx = CreativeTransaction(commands=[command], transaction_id="b" * 32)
            result = publish_creative_command_batch_for_run(
                config, ctx, project_id=doc.project_id, transaction=tx,
                expected_head_revision=first.revision_id, expected_etag=first.etag,
            )
            second = load_creative_revision(doc.project_id, result["revision_id"])
            assert second.native_files == first.native_files
            for name, expected_bytes in native.items():
                assert (second.manifest_path.parent / name).read_bytes() == expected_bytes
            assert load_creative_head(doc.project_id) == second
    finally:
        reset_current_session_key(st)
        reset_hermes_home_override(ht)


def test_cli_apply_batch_uses_existing_canonical_taskrun_contract(tmp_path, monkeypatch):
    """A command file routes through the one admitted TaskRun+CAS backend."""
    import json
    from types import SimpleNamespace
    from workstation.creative import _execute
    from workstation.creative_project_store import load_creative_document

    home = tmp_path / "profile"
    monkeypatch.setenv("HERMES_KANBAN_DB", str(home / "kanban.db"))
    ht = set_hermes_home_override(home)
    st = set_current_session_key("session-key")
    try:
        with scoped_current_session_id("session-one"):
            ctx = _claimed_scope(home)
            config = WorkstationConfig({"creative": {"enabled": True}})
            doc = create_empty_project(name="CLI actor shared")
            first = publish_creative_document_cas(doc, operation_id="a" * 32)
            workspace = ctx.validate(config)
            request = workspace / "commands.json"
            request.write_text(json.dumps({
                "transaction_id": "b" * 32,
                "commands": [{
                    "command_id": "layer.create",
                    "params": {
                        "composition_id": doc.compositions[0].composition_id,
                        "layer_id": "c" * 32,
                        "name": "UI-created-layer",
                    },
                    "actor": {"actor_id": "human-ui", "actor_type": "human_mouse"},
                    "idempotency_key": "create-ui-layer",
                }],
            }), encoding="utf-8")
            args = SimpleNamespace(
                command="apply-batch", commands_file=request,
                project_id=doc.project_id,
                expected_revision_id=first.revision_id, if_match=first.etag,
            )
            result = _execute(args, config, ctx, workspace)
            assert result["operation_id"] == "b" * 32
            second = load_creative_head(doc.project_id)
            assert second is not None and second.parent_revision == first.revision_id
            edited = load_creative_document(doc.project_id, second.revision_id)
            assert edited.compositions[0].layers[0].name == "UI-created-layer"
            outside = tmp_path / "outside.json"
            outside.write_bytes(request.read_bytes())
            with pytest.raises(PermissionError):
                _execute(SimpleNamespace(
                    command="apply-batch", commands_file=outside,
                    project_id=doc.project_id,
                    expected_revision_id=first.revision_id,
                    if_match=first.etag,
                ), config, ctx, workspace)
            assert load_creative_head(doc.project_id) == second
    finally:
        reset_current_session_key(st)
        reset_hermes_home_override(ht)


def test_cli_canonical_create_open_then_batch_single_owner(tmp_path, monkeypatch):
    """Complete Python CLI dispatcher read/create/edit cycle over one HEAD."""
    import json
    from types import SimpleNamespace
    from workstation.creative import _execute
    from workstation.creative_document import document_to_dict

    home = tmp_path / "profile"
    monkeypatch.setenv("HERMES_KANBAN_DB", str(home / "kanban.db"))
    ht = set_hermes_home_override(home)
    st = set_current_session_key("session-key")
    try:
        with scoped_current_session_id("session-one"):
            ctx = _claimed_scope(home)
            config = WorkstationConfig({"creative": {"enabled": True}})
            workspace = ctx.validate(config)
            doc = create_empty_project(name="Canonical CLI roundtrip")
            document_path = workspace / "creative-document.json"
            document_path.write_text(json.dumps(document_to_dict(doc)), encoding="utf-8")
            created = _execute(SimpleNamespace(
                command="canonical-create", source=document_path,
            ), config, ctx, workspace)
            assert created["project_id"] == doc.project_id
            assert load_creative_head(doc.project_id).revision_id == created["revision_id"]
            loaded = _execute(SimpleNamespace(
                command="canonical-open", project_id=doc.project_id,
            ), config, ctx, workspace)
            assert loaded["revision_id"] == created["revision_id"]
            assert loaded["source"] == document_to_dict(doc)
            assert loaded["etag"] == created["etag"]
            path = workspace / "commands.json"
            path.write_text(json.dumps({
                "transaction_id": "b" * 32,
                "commands": [{
                    "command_id": "layer.create",
                    "params": {"composition_id": doc.compositions[0].composition_id,
                               "layer_id": "d" * 32, "name": "Shared canonical layer"},
                    "actor": {"actor_id": "hermes", "actor_type": "hermes_agent"},
                    "idempotency_key": "add-layer",
                }],
            }), encoding="utf-8")
            edited = _execute(SimpleNamespace(
                command="apply-batch", commands_file=path,
                project_id=doc.project_id, expected_revision_id=created["revision_id"],
                if_match=created["etag"],
            ), config, ctx, workspace)
            reopened = _execute(SimpleNamespace(
                command="canonical-open", project_id=doc.project_id,
            ), config, ctx, workspace)
            assert reopened["revision_id"] == edited["revision_id"]
            assert reopened["source"]["compositions"][0]["layers"][0]["name"] == "Shared canonical layer"
            assert reopened["etag"] != loaded["etag"]
    finally:
        reset_current_session_key(st)
        reset_hermes_home_override(ht)
