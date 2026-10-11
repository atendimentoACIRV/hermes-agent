"""Regression: Kanban queries must not poison mutation/approval ledgers."""
from types import SimpleNamespace

import pytest

from tools import kanban_tools  # registers the canonical tool metadata
from tools.effects import ToolEffect, tool_effect
from workstation.batch_detection import prepare_mutation, record_mutation


READ_ONLY = {"kanban_show", "kanban_list", "kanban_attachments"}


@pytest.mark.parametrize("name", [item[0] for item in kanban_tools._TOOLS])
def test_kanban_effects_are_explicit_and_conservative(name):
    expected = ToolEffect.PURE_READ if name in READ_ONLY else ToolEffect.MUTATION
    assert tool_effect(name) is expected


@pytest.mark.parametrize("name", sorted(READ_ONLY))
def test_kanban_read_never_enters_mutation_ledger(name, monkeypatch):
    # This is the real registration and the real Workstation dispatcher
    # classification; no per-name allowlist may be added to tools.effects.
    monkeypatch.setattr("workstation.procedure_trace.record_trace", lambda *a, **kw: None)
    monkeypatch.setattr("tools.effects.observe_capability", lambda *a, **kw: None)
    agent = SimpleNamespace(
        valid_tool_names={"work_execute"},
        session_id="kanban-read-regression",
        _conversation_root_id=lambda: "kanban-read-regression",
    )
    args = {"task_id": "t_example"} if name != "kanban_list" else {"limit": 5}
    record_mutation(agent, name, args, '{"success":false,"error":"timeout"}', dispatched=True)
    assert getattr(agent, "_work_mutation_evidence", {}) == {}
    assert getattr(agent, "_work_completed_mutations", {}) == {}
    prepare_mutation(agent, name, args)
    assert getattr(agent, "_work_mutation_evidence", {}) == {}
