"""Force cannot turn a point action into durable work without explicit authority."""
from workstation.contracts import IntentAuthority, MessageEnvelope, MessageOrigin
from workstation.kanban import WorkstationKanbanBridge


def test_force_does_not_bypass_point_action_without_explicit_delegation(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    request = "Abre o Trello"
    envelope = MessageEnvelope(MessageOrigin.HUMAN, IntentAuthority.CREATE_WORK,
                               "session", request)
    assert WorkstationKanbanBridge().promote_request_if_multistep(
        request, session_id="session", envelope=envelope, force=True, defer_execution=True
    ) is None


def test_force_allows_explicit_trusted_durable_delegation(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    request = "Abre o Trello"
    envelope = MessageEnvelope(MessageOrigin.HUMAN, IntentAuthority.CREATE_WORK,
                               "session", request, metadata={"explicit_force_work": True})
    task_id = WorkstationKanbanBridge().promote_request_if_multistep(
        request, session_id="session", envelope=envelope, force=True, defer_execution=True
    )
    assert task_id

def test_force_with_invalid_ingress_metadata_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    request = "Abre o Trello"
    envelope = MessageEnvelope(MessageOrigin.HUMAN, IntentAuthority.CREATE_WORK,
                               "session", request, metadata=None)
    assert WorkstationKanbanBridge().promote_request_if_multistep(
        request, session_id="session", envelope=envelope, force=True, defer_execution=True
    ) is None
