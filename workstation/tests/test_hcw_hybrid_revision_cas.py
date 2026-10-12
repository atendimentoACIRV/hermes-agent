"""H-C4 opt-in durable head CAS: concurrency and replay must fail closed."""
import pytest

from hermes_constants import set_hermes_home_override, reset_hermes_home_override
from workstation.creative_document import create_empty_project
from workstation.creative_project_store import CreativeConflictError
from workstation.creative_revision_cas import (
    publish_creative_document_cas, load_creative_head,
)


def test_human_agent_same_parent_cannot_publish_sibling_revisions(tmp_path):
    token = set_hermes_home_override(tmp_path / "profile")
    try:
        doc = create_empty_project(name="HCW shared")
        root = publish_creative_document_cas(doc, operation_id="a" * 32)
        assert load_creative_head(doc.project_id) == root
        doc.name = "human change"
        human = publish_creative_document_cas(
            doc, expected_head_revision=root.revision_id,
            expected_etag=root.etag, operation_id="b" * 32,
        )
        assert load_creative_head(doc.project_id) == human
        doc.name = "agent stale change"
        with pytest.raises(CreativeConflictError, match="409 Conflict"):
            publish_creative_document_cas(
                doc, expected_head_revision=root.revision_id,
                expected_etag=root.etag, operation_id="c" * 32,
            )
        assert load_creative_head(doc.project_id) == human
        assert not any(p.is_dir() and p.name not in {root.revision_id, human.revision_id}
                       for p in (human.manifest_path.parent.parent).iterdir())
    finally:
        reset_hermes_home_override(token)


def test_replay_same_operation_and_conflicting_payload(tmp_path):
    token = set_hermes_home_override(tmp_path / "profile")
    try:
        doc = create_empty_project(name="Idempotency")
        first = publish_creative_document_cas(doc, operation_id="1" * 32)
        doc.name = "Edited"
        edited = publish_creative_document_cas(
            doc, expected_head_revision=first.revision_id,
            expected_etag=first.etag, operation_id="2" * 32,
        )
        replay = publish_creative_document_cas(
            doc, expected_head_revision=first.revision_id,
            expected_etag=first.etag, operation_id="2" * 32,
        )
        assert replay == edited
        doc.name = "Different with same id"
        with pytest.raises(CreativeConflictError, match="409 Conflict"):
            publish_creative_document_cas(
                doc, expected_head_revision=first.revision_id,
                expected_etag=first.etag, operation_id="2" * 32,
            )
        assert load_creative_head(doc.project_id) == edited
    finally:
        reset_hermes_home_override(token)


def test_requires_expected_head_and_operation_id(tmp_path):
    token = set_hermes_home_override(tmp_path / "profile")
    try:
        doc = create_empty_project(name="Must use revision CAS")
        first = publish_creative_document_cas(doc, operation_id="1" * 32)
        with pytest.raises(CreativeConflictError, match="409 Conflict"):
            publish_creative_document_cas(doc, operation_id="3" * 32)
        with pytest.raises(ValueError, match="operation"):
            publish_creative_document_cas(
                doc, expected_head_revision=first.revision_id,
                expected_etag=first.etag, operation_id="bad-id",
            )
        assert load_creative_head(doc.project_id) == first
    finally:
        reset_hermes_home_override(token)


def test_concurrent_human_agent_race_commits_one_head(tmp_path):
    """Two simultaneously admitted editors cannot fork one canonical HEAD."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from workstation.creative_project_store import load_creative_document

    profile = tmp_path / "profile"
    token = set_hermes_home_override(profile)
    try:
        initial_doc = create_empty_project(name="Before race")
        first = publish_creative_document_cas(initial_doc, operation_id="a" * 32)
        barrier = Barrier(2)

        def editor(actor: str, operation_id: str):
            own = set_hermes_home_override(profile)
            try:
                copy = load_creative_document(first.project_id, first.revision_id)
                copy.name = actor
                barrier.wait(timeout=10)
                try:
                    return publish_creative_document_cas(
                        copy, expected_head_revision=first.revision_id,
                        expected_etag=first.etag, operation_id=operation_id,
                    )
                except CreativeConflictError as exc:
                    return str(exc)
            finally:
                reset_hermes_home_override(own)

        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(editor, "human", "b" * 32)
            b = pool.submit(editor, "agent", "c" * 32)
            results = [a.result(timeout=20), b.result(timeout=20)]
        assert sum(isinstance(item, str) and "409 Conflict" in item
                   for item in results) == 1, results
        successful = next(item for item in results if not isinstance(item, str))
        assert load_creative_head(first.project_id) == successful
        assert len(list((successful.manifest_path.parent.parent).glob("*/manifest.json"))) == 2
    finally:
        reset_hermes_home_override(token)


def test_canonical_command_bus_publishes_human_then_agent_with_one_revision_chain(tmp_path):
    from workstation.creative_revision_cas import publish_creative_command_batch_cas
    from workstation.creative_commands import Actor, CreativeCommand
    from workstation.creative_transactions import CreativeTransaction
    from workstation.creative_project_store import load_creative_document

    token = set_hermes_home_override(tmp_path / "profile")
    try:
        doc = create_empty_project(name="Human agent joint")
        root = publish_creative_document_cas(doc, operation_id="a" * 32)
        comp = doc.compositions[0].composition_id
        layer_id = "e" * 32
        human_tx = CreativeTransaction(
            transaction_id="b" * 32,
            commands=[CreativeCommand(
                command_id="layer.create",
                params={"composition_id": comp, "layer_id": layer_id,
                        "name": "Shared", "kind": "vector_svg"},
                actor=Actor("human", "human_mouse"), idempotency_key="human-layer",
            )],
        )
        human = publish_creative_command_batch_cas(
            doc.project_id, human_tx, expected_head_revision=root.revision_id,
            expected_etag=root.etag,
        )
        assert human.parent_revision == root.revision_id
        assert len(load_creative_document(doc.project_id, human.revision_id).compositions[0].layers) == 1
        replay = publish_creative_command_batch_cas(
            doc.project_id, human_tx, expected_head_revision=root.revision_id,
            expected_etag=root.etag,
        )
        assert replay == human
        agent_tx = CreativeTransaction(
            transaction_id="c" * 32,
            commands=[CreativeCommand(
                command_id="layer.setProperty",
                params={"composition_id": comp, "layer_id": layer_id,
                        "property_path": "declared_parameters.brandColor",
                        "value": "#8b1e4f"},
                actor=Actor("hermes", "hermes_agent"),
                idempotency_key="agent-color",
            )],
        )
        agent = publish_creative_command_batch_cas(
            doc.project_id, agent_tx,
            expected_head_revision=human.revision_id, expected_etag=human.etag,
        )
        reopened = load_creative_document(doc.project_id, agent.revision_id)
        assert reopened.compositions[0].layers[0].declared_parameters["brandColor"] == "#8b1e4f"
        assert load_creative_head(doc.project_id) == agent
        with pytest.raises(CreativeConflictError, match="409 Conflict"):
            publish_creative_command_batch_cas(
                doc.project_id, agent_tx,
                expected_head_revision=root.revision_id, expected_etag=root.etag,
            )
    finally:
        reset_hermes_home_override(token)


def test_faulty_four_step_batch_never_advances_durable_head(tmp_path):
    from workstation.creative_revision_cas import publish_creative_command_batch_cas
    from workstation.creative_commands import Actor, CreativeCommand
    from workstation.creative_transactions import CreativeTransaction, TransactionExecutionError

    token = set_hermes_home_override(tmp_path / "profile")
    try:
        doc = create_empty_project(name="Atomic batch")
        root = publish_creative_document_cas(doc, operation_id="a" * 32)
        comp = doc.compositions[0].composition_id
        actor = Actor("hermes", "hermes_agent")
        ops = [
            ("track.add", {"composition_id": comp, "track_id": "1" * 32}),
            ("layer.create", {"composition_id": comp, "layer_id": "2" * 32}),
            ("clip.add", {"composition_id": comp, "track_id": "missing",
                          "clip_id": "3" * 32, "asset_id": "4" * 32}),
            ("layer.create", {"composition_id": comp, "layer_id": "5" * 32}),
        ]
        tx = CreativeTransaction(
            transaction_id="b" * 32,
            commands=[CreativeCommand(id, params, actor, f"batch-{i}")
                      for i, (id, params) in enumerate(ops)],
        )
        with pytest.raises(TransactionExecutionError):
            publish_creative_command_batch_cas(
                doc.project_id, tx, expected_head_revision=root.revision_id,
                expected_etag=root.etag,
            )
        assert load_creative_head(doc.project_id) == root
        assert len(list(root.manifest_path.parent.parent.glob("*/manifest.json"))) == 1
    finally:
        reset_hermes_home_override(token)


def test_legacy_or_orphan_revision_without_head_not_silently_promoted(tmp_path):
    """Completed manifest without HEAD may be an orphan after a crashed commit."""
    from workstation.creative_project_store import save_creative_document
    token = set_hermes_home_override(tmp_path / "profile")
    try:
        doc = create_empty_project(name="Unmarked legacy or crash orphan")
        orphan = save_creative_document(doc, operation_id="a" * 32)
        assert orphan.manifest_path.is_file()
        with pytest.raises(CreativeConflictError, match="409 Conflict"):
            load_creative_head(doc.project_id)
        with pytest.raises(CreativeConflictError, match="409 Conflict"):
            publish_creative_document_cas(
                doc, expected_head_revision=orphan.revision_id,
                expected_etag=orphan.etag, operation_id="b" * 32,
            )
        assert not (orphan.manifest_path.parent.parent.parent / "head.json").exists()
    finally:
        reset_hermes_home_override(token)


def test_idempotency_receipt_survives_intervening_agent_commit_and_restart(tmp_path):
    """Retry of a completed human batch cannot become a second edit after an agent edit."""
    from workstation.creative_revision_cas import publish_creative_command_batch_cas
    from workstation.creative_commands import Actor, CreativeCommand
    from workstation.creative_transactions import CreativeTransaction
    from workstation.creative_project_store import load_creative_document

    token = set_hermes_home_override(tmp_path / "profile")
    try:
        doc = create_empty_project(name="Durable replay after another editor")
        first = publish_creative_document_cas(doc, operation_id="a" * 32)
        comp = doc.compositions[0].composition_id

        def tx(op, ident, actor):
            return CreativeTransaction(transaction_id=op, commands=[
                CreativeCommand(
                    "layer.create", {
                        "composition_id": comp, "layer_id": ident, "name": actor,
                    }, Actor(actor, "hermes_agent" if actor == "agent" else "human_mouse"),
                    f"same-key-{ident}",
                ),
            ])

        original = tx("b" * 32, "1" * 32, "human")
        second = publish_creative_command_batch_cas(
            doc.project_id, original, expected_head_revision=first.revision_id,
            expected_etag=first.etag,
        )
        next_tx = tx("c" * 32, "2" * 32, "agent")
        third = publish_creative_command_batch_cas(
            doc.project_id, next_tx, expected_head_revision=second.revision_id,
            expected_etag=second.etag,
        )
        # Process restart-equivalent: import the module again and use disk HEAD.
        retry = publish_creative_command_batch_cas(
            doc.project_id, original, expected_head_revision=first.revision_id,
            expected_etag=first.etag,
        )
        assert retry == second
        assert load_creative_head(doc.project_id) == third
        assert len(load_creative_document(doc.project_id, third.revision_id)
                   .compositions[0].layers) == 2

        altered = tx("b" * 32, "3" * 32, "human")
        with pytest.raises(CreativeConflictError, match="409 Conflict"):
            publish_creative_command_batch_cas(
                doc.project_id, altered,
                expected_head_revision=first.revision_id, expected_etag=first.etag,
            )
        assert load_creative_head(doc.project_id) == third
    finally:
        reset_hermes_home_override(token)
