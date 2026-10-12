"""P0 Browser authority: a session action cannot borrow an unrelated Kanban run."""
import pytest

from tools import browser_workstation as bw
from hermes_cli import kanban_db
from workstation.kanban import WorkstationKanbanBridge


@pytest.fixture
def dispatch(monkeypatch):
    observed = []
    monkeypatch.setattr(bw, "_request_json",
                        lambda method, route, payload, **kwargs:
                        observed.append(payload) or {"success": True, "result": {"success": True}})
    return observed


def test_unrelated_blocked_kanban_task_does_not_bind_browser_session(tmp_path, monkeypatch, dispatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    with WorkstationKanbanBridge().get_connection() as conn:
        task_id = kanban_db.create_task(conn, title="Old work", body="Broken task",
                                        session_id="chat-1", created_by="workstation",
                                        initial_status="running")
        conn.execute("UPDATE tasks SET status='blocked' WHERE id=?", (task_id,))
        conn.commit()
    bw._dispatch("browser_navigate", {"url": "https://example.com"}, session_id="chat-1")
    assert dispatch[0]["task_id"] == "chat-1"
    assert "kanban_card_id" not in dispatch[0]
    assert "run_id" not in dispatch[0]


def test_session_only_browser_command_does_not_borrow_process_env_run(monkeypatch, dispatch):
    monkeypatch.setenv("HERMES_KANBAN_TASK", "another-session-card")
    monkeypatch.setenv("HERMES_KANBAN_RUN_ID", "another-session-run")
    bw._dispatch("browser_snapshot", {}, session_id="current-chat")
    assert dispatch[0]["task_id"] == "current-chat"
    assert "kanban_card_id" not in dispatch[0]
    assert "run_id" not in dispatch[0]


def test_explicit_canonical_identity_is_preserved(tmp_path, monkeypatch, dispatch):
    task_id, run_id = _claimed_task(tmp_path, monkeypatch)
    bw._dispatch(
        "browser_snapshot", {}, task_id="browser-task", session_id="chat-a",
        kanban_card_id=task_id, run_id=run_id,
    )
    assert dispatch[0]["task_id"] == "browser-task"
    assert dispatch[0]["kanban_card_id"] == task_id
    assert dispatch[0]["run_id"] == run_id


def _claimed_task(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    with WorkstationKanbanBridge().get_connection() as conn:
        task_id = kanban_db.create_task(
            conn, title="Owned task", body="Actual work",
            session_id="chat-a", created_by="workstation",
            triage=True,
        )
        assert kanban_db.specify_triage_task(conn, task_id)
        claimed = kanban_db.claim_task(conn, task_id, claimer="test-worker")
        assert claimed and claimed.current_run_id
        return task_id, str(claimed.current_run_id)


def test_blocked_task_cannot_reuse_explicit_run_for_browser(tmp_path, monkeypatch, dispatch):
    task_id, run_id = _claimed_task(tmp_path, monkeypatch)
    with WorkstationKanbanBridge().get_connection() as conn:
        conn.execute("UPDATE tasks SET status='blocked' WHERE id=?", (task_id,))
        conn.commit()
    with pytest.raises(bw.WorkstationBrowserError) as err:
        bw._dispatch("browser_navigate", {"url": "https://example.com"},
                     session_id="chat-a", kanban_card_id=task_id, run_id=run_id)
    assert err.value.error_code == "STALE_RUN"
    assert dispatch == []


def test_task_run_from_foreign_session_cannot_control_browser(tmp_path, monkeypatch, dispatch):
    task_id, run_id = _claimed_task(tmp_path, monkeypatch)
    with pytest.raises(bw.WorkstationBrowserError) as err:
        bw._dispatch("browser_snapshot", {}, session_id="chat-b",
                     kanban_card_id=task_id, run_id=run_id)
    assert err.value.error_code == "STALE_RUN"
    assert dispatch == []


def test_new_session_browser_operation_does_not_replay_prior_global_operation_id(monkeypatch, dispatch):
    monkeypatch.setenv("HERMES_OPERATION_ID", "op_old_chat_1234")
    bw._dispatch("browser_navigate", {"url": "https://example.com"}, session_id="new-chat")
    assert dispatch[0]["operation_id"] != "op_old_chat_1234"
    assert dispatch[0]["operation_id"].startswith("op_browser_navigate_")


@pytest.mark.parametrize("card_id, run_id", [
    ("missing-card", "12345"),
    ("missing-card", None),
    (None, "12345"),
])
def test_nonexistent_or_incomplete_explicit_binding_fails_closed(
    tmp_path, monkeypatch, dispatch, card_id, run_id,
):
    """Unverifiable explicit run/card binding must not reach Electron."""
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    with pytest.raises(bw.WorkstationBrowserError) as err:
        bw._dispatch(
            "browser_snapshot", {}, session_id="chat-a",
            kanban_card_id=card_id, run_id=run_id,
        )
    assert err.value.error_code == "STALE_RUN"
    assert dispatch == []
