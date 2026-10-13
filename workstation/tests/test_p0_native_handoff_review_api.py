"""Native UI review reads the canonical handoff ledger without minting authority."""
import asyncio

import pytest
from fastapi import HTTPException

from workstation.runtime import HumanHandoffManager


def test_native_review_api_scopes_sessions_and_consumes_once(tmp_path, monkeypatch):
    from plugins.workstation.dashboard import plugin_api

    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    ledger = HumanHandoffManager(tmp_path / "workstation" / "human_handoffs.json")
    a = ledger.request(task_id="task-a", session_id="session-a", reason="uncertain_mutation_requires_review",
                       scope={"operation_key": "click-a", "run_id": "run-a"})
    ledger.request(task_id="task-b", session_id="session-b", reason="uncertain_mutation_requires_review",
                   scope={"operation_key": "click-b", "run_id": "run-b"})

    reviews = asyncio.run(plugin_api.list_native_handoff_reviews(session_id="session-a"))
    assert len(reviews["handoffs"]) == 1
    assert reviews["handoffs"][0]["handoff_id"] == a.handoff_id
    assert reviews["handoffs"][0]["run_id"] == "run-a"
    assert "operation_key" not in reviews["handoffs"][0]  # no raw mutation payload in UI

    with pytest.raises(HTTPException) as denied:
        asyncio.run(plugin_api.resume_native_handoff_review(
            a.handoff_id, session_id="session-b", run_id="run-a"))
    assert denied.value.status_code == 404

    with pytest.raises(HTTPException) as denied:
        asyncio.run(plugin_api.resume_native_handoff_review(
            a.handoff_id, session_id="session-a", run_id="run-stale"))
    assert denied.value.status_code == 409

    accepted = asyncio.run(plugin_api.resume_native_handoff_review(
        a.handoff_id, session_id="session-a", run_id="run-a"))
    assert accepted["status"] == "ready"
    with pytest.raises(HTTPException) as duplicate:
        asyncio.run(plugin_api.resume_native_handoff_review(
            a.handoff_id, session_id="session-a", run_id="run-a"))
    assert duplicate.value.status_code == 409
    assert HumanHandoffManager(ledger.path).get(a.handoff_id).status == "ready"


def test_native_review_api_read_does_not_consume_or_reopen(tmp_path, monkeypatch):
    from plugins.workstation.dashboard import plugin_api

    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    ledger = HumanHandoffManager(tmp_path / "workstation" / "human_handoffs.json")
    review = ledger.request(task_id="task", session_id="session", reason="uncertain_mutation_requires_review",
                            scope={"operation_key": "click"})
    assert ledger.resume(review.handoff_id, returned_by="human")
    assert ledger.consume(review.handoff_id)
    assert asyncio.run(plugin_api.list_native_handoff_reviews(session_id="session")) == {"handoffs": []}
    with pytest.raises(HTTPException) as rejected:
        asyncio.run(plugin_api.resume_native_handoff_review(
            review.handoff_id, session_id="session", run_id=""))
    assert rejected.value.status_code == 409
    assert HumanHandoffManager(ledger.path).get(review.handoff_id).status == "consumed"
