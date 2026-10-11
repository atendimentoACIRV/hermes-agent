"""Rail 3: an unclaimed canonical run has an actionable, fail-closed fence."""
import json
from types import SimpleNamespace

import pytest

from hermes_cli import kanban_db, kanban_db_connect
from tools.registry import registry
from workstation.artifacts import ArtifactStore
from workstation.batch_detection import prepare_mutation, call_key
from workstation.authority_supersession import resume_superseded_work


@pytest.fixture
def fenced(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    conn = kanban_db_connect.connect()
    task = kanban_db.create_task(conn, title="fence-recovery", session_id="test-session")
    old = kanban_db.claim_task(conn, task, claimer="old-worker")
    assert old.current_run_id == 1
    agent = SimpleNamespace(
        valid_tool_names={"work_execute"},
        session_id="test-session",
        _canonical_work_task_id=task,
        _canonical_work_run_id="1",
        _conversation_root_id=lambda: "test-session",
    )
    yield conn, task, agent, tmp_path
    conn.close()


def test_unclaimed_canonical_run_has_typed_recovery_and_checkpoint(fenced):
    from workstation.authority_supersession import MutationAuthorityFenceError
    conn, task, agent, home = fenced
    conn.execute("UPDATE tasks SET current_run_id=NULL WHERE id=?", (task,))
    conn.commit()
    args = {"path": "unexecuted.txt", "content": "do-not-write"}
    with pytest.raises(MutationAuthorityFenceError) as caught:
        prepare_mutation(agent, "write_file", args)
    error = caught.value
    assert error.code == "CANONICAL_RUN_UNCLAIMED"
    assert error.current_run_id is None
    assert error.continuation_allowed is False
    assert error.recovery_action == "claim_new_canonical_run_and_replan"
    assert error.pending_items_ref and error.checkpoint_ref
    pending = ArtifactStore().read_json(error.pending_items_ref)
    assert pending["pending_items"][0]["operation_id"] == call_key("write_file", args)
    assert pending["pending_items"][0]["status"] == "not_dispatched"
    assert not (home / "unexecuted.txt").exists()


def test_valid_successor_is_named_but_old_run_stays_fenced(fenced):
    from workstation.authority_supersession import MutationAuthorityFenceError
    conn, task, agent, home = fenced
    assert kanban_db.reclaim_task(conn, task)
    next_run = kanban_db.claim_task(conn, task, claimer="new-worker")
    assert next_run.current_run_id == 2
    with pytest.raises(MutationAuthorityFenceError) as caught:
        prepare_mutation(agent, "write_file", {"path": "no.txt", "content": "no"})
    error = caught.value
    assert error.code == "AUTHORITY_SUPERSEDED"
    assert error.current_run_id == "2"
    assert error.continuation_allowed is True
    assert error.recovery_action == "resume_in_canonical_run"
    assert error.pending_items_ref
    from workstation.authority_supersession import AuthoritySuperseded
    resume = resume_superseded_work(AuthoritySuperseded(
        task_id=task, stale_run_id="1", current_run_id="2", continuation_allowed=True,
        checkpoint_ref=error.checkpoint_ref, pending_items_ref=error.pending_items_ref,
    ), "2", artifact_store=ArtifactStore())
    assert len(resume["resumed_items"]) == 1
    assert resume["resumed_items"][0]["claimed_run_id"] == "2"
    assert resume["resumed_items"][0]["status"] == "not_dispatched"
    assert not (home / "no.txt").exists()
