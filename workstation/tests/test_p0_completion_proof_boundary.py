"""Regression: completion admission requires proof-bound canonical receipts."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from workstation.integrations.hermes import completion_admission as admission


class _Connection:
    def close(self):
        pass


class _Bridge:
    candidate: object = None

    def get_connection(self):
        return _Connection()

    def finalize_turn_candidate(self, **kwargs):
        return self.candidate


@pytest.fixture
def admission_bridge(monkeypatch):
    instance = _Bridge()
    monkeypatch.setattr(admission, "WorkstationKanbanBridge", lambda: instance)
    from hermes_cli import kanban_db
    monkeypatch.setattr(
        kanban_db, "get_task",
        lambda conn, task_id: SimpleNamespace(session_id="session-1"),
    )
    return instance


def _admit():
    return admission.workstation_completion_admission(
        "task-1", "101", {"session_id": "session-1", "turn_result": {"completed": True}}
    )


@pytest.mark.parametrize("candidate", [
    {"task_id": "task-1", "status": "verified_completed", "acceptance_approved": False},
    {"task_id": "task-1", "status": "uncertain", "acceptance_approved": True},
    {"task_id": "task-1", "status": "verified_completed", "acceptance_approved": True, "run_id": "99"},
    {"task_id": "other-task", "status": "verified_completed", "acceptance_approved": True},
    {"task_id": "task-1", "status": "queued_unstarted", "acceptance_approved": False},
    {"task_id": "task-1", "status": "unrecognized_state", "acceptance_approved": False},
    {},
    None,
])
def test_unverified_candidate_never_admits(admission_bridge, candidate):
    admission_bridge.candidate = candidate
    assert _admit().admitted is False


def test_matching_verified_candidate_admits(admission_bridge):
    admission_bridge.candidate = {
        "task_id": "task-1", "status": "verified_completed", "acceptance_approved": True,
    }
    assert _admit().admitted is True


def test_unexpected_candidate_type_denied(admission_bridge):
    admission_bridge.candidate = "ok"
    assert _admit().admitted is False


def test_legacy_verified_candidate_requires_canonical_identity(admission_bridge):
    admission_bridge.candidate = SimpleNamespace(verified=True, run_id="99", pending_items=[])
    assert _admit().admitted is False
