"""Two concurrent durable admissions must converge on one canonical task."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from hermes_cli import kanban_db
from workstation.contracts import IntentAuthority, MessageEnvelope, MessageOrigin
from workstation.kanban import WorkstationKanbanBridge


def _human(content: str, correlation_id: str) -> MessageEnvelope:
    return MessageEnvelope(MessageOrigin.HUMAN, IntentAuthority.CREATE_WORK,
                           "shared-session", content, correlation_id=correlation_id)


def test_simultaneous_work_requests_deduplicate_across_turn_ids(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    text = "First collect reports then verify and save the results"
    barrier = Barrier(2)
    def admit(i):
        barrier.wait(timeout=10)
        return WorkstationKanbanBridge().promote_request_if_multistep(
            text, session_id="shared-session", envelope=_human(text, f"turn-{i}"),
            defer_execution=True,
        )
    with ThreadPoolExecutor(max_workers=2) as executor:
        a, b = list(executor.map(admit, (1, 2)))
    assert a == b
    with WorkstationKanbanBridge().get_connection() as conn:
        assert conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM task_runs").fetchone()[0] == 0


def test_completed_work_does_not_prevent_explicit_new_request(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    text = "First collect reports then verify and save the results"
    bridge = WorkstationKanbanBridge()
    first = bridge.promote_request_if_multistep(
        text, session_id="shared-session", envelope=_human(text, "turn-A"), defer_execution=True,
    )
    with bridge.get_connection() as conn:
        conn.execute("UPDATE tasks SET status='done' WHERE id=?", (first,))
        conn.commit()
    second = bridge.promote_request_if_multistep(
        text, session_id="shared-session", envelope=_human(text, "turn-B"), defer_execution=True,
    )
    assert second != first


def test_existing_blocked_work_is_not_duplicated(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    text = "First collect reports then verify and save the results"
    bridge = WorkstationKanbanBridge()
    first = bridge.promote_request_if_multistep(
        text, session_id="shared-session", envelope=_human(text, "turn-A"), defer_execution=True,
    )
    with bridge.get_connection() as conn:
        conn.execute("UPDATE tasks SET status='blocked' WHERE id=?", (first,))
        conn.commit()
    second = bridge.promote_request_if_multistep(
        text, session_id="shared-session", envelope=_human(text, "turn-B"), defer_execution=True,
    )
    assert second == first
