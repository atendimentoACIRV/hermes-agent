"""A missing turn correlation is not proof of an existing TaskRun's lineage.

This regression covers the authenticated-user ingress path, whose
TurnIngress.correlation_id is optional and may be None.
"""
from types import SimpleNamespace

import pytest

from hermes_cli import kanban_db
from workstation.contracts import IntentAuthority, MessageEnvelope, MessageOrigin
from workstation.kanban import WorkstationKanbanBridge
from workstation.work_intent import prepare_turn_work


@pytest.fixture
def claimed_task(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))

    def make_task(objective):
        with WorkstationKanbanBridge().get_connection() as conn:
            task_id = kanban_db.create_task(
                conn, title="Previously active work", body=objective,
                session_id="chat-a", created_by="workstation", triage=True,
            )
            assert kanban_db.specify_triage_task(conn, task_id)
            claimed = kanban_db.claim_task(conn, task_id, claimer="previous-turn")
            assert claimed and claimed.current_run_id
            return task_id, str(claimed.current_run_id)

    return make_task


def _agent(task_id, run_id):
    return SimpleNamespace(
        session_id="chat-a",
        _conversation_root_id=lambda: "chat-a",
        _canonical_work_task_id=task_id,
        _canonical_work_run_id=run_id,
        _canonical_work_turn_id=None,
    )


def _envelope(objective):
    return MessageEnvelope(
        MessageOrigin.HUMAN, IntentAuthority.CREATE_WORK,
        "chat-a", objective, correlation_id=None,
    )


def test_new_point_action_with_no_correlation_does_not_adopt_old_running_run(claimed_task):
    objective = "Abre o Trello"
    task_id, run_id = claimed_task(objective)
    agent = _agent(task_id, run_id)

    result = prepare_turn_work(agent, objective, envelope=_envelope(objective))

    assert result.admission_kind == "point_action"
    assert agent._canonical_work_task_id is None
    assert agent._canonical_work_run_id is None


def test_new_durable_turn_without_correlation_cannot_reuse_previous_run(claimed_task):
    objective = "Implemente a API e depois escreva testes."
    task_id, run_id = claimed_task(objective)
    agent = _agent(task_id, run_id)

    result = prepare_turn_work(agent, objective, envelope=_envelope(objective))

    assert result.requires_task
    assert agent._canonical_work_run_id is None
    assert agent._work_blocked_task_id == task_id


def test_matching_nonempty_turn_correlation_preserves_owned_active_run(claimed_task):
    objective = "Implemente a API e depois escreva testes."
    task_id, run_id = claimed_task(objective)
    agent = _agent(task_id, run_id)
    agent._canonical_work_turn_id = "turn-verified"

    envelope = MessageEnvelope(
        MessageOrigin.HUMAN, IntentAuthority.CREATE_WORK,
        "chat-a", objective, correlation_id="turn-verified",
    )
    result = prepare_turn_work(agent, objective, envelope=envelope)

    assert result.requires_task
    assert agent._canonical_work_task_id == task_id
    assert str(agent._canonical_work_run_id) == run_id
    assert agent._work_blocked_task_id is None
