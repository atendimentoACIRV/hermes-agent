"""Rail 2: synthetics must not poison mutable ledgers or mint endless handoffs."""
import json
from pathlib import Path
from types import SimpleNamespace

from tools.effects import ToolEffect
from workstation.batch_detection import call_key, record_mutation
from workstation.execution_policy import CompilationDecision, decisions_for_calls
from workstation.runtime import HumanHandoffManager


def _agent():
    return SimpleNamespace(
        session_id="session-p0-rail2",
        valid_tool_names={"work_execute"},
        _conversation_root_id=lambda: "session-p0-rail2",
    )


def _call(name, args=None, ident="a"):
    return SimpleNamespace(id=ident, function=SimpleNamespace(name=name, arguments=json.dumps(args or {})))


def test_refusal_before_dispatch_never_creates_mutation_uncertainty():
    agent = _agent()
    record_mutation(agent, "write_file", {"path": "x.txt", "content": "x"},
                    {"status": "handoff_requested", "error": "policy refused"}, dispatched=False)
    assert not hasattr(agent, "_work_mutation_evidence")
    assert decisions_for_calls(agent, [_call("browser_snapshot")]) == [CompilationDecision.ALLOW_ADAPTIVE]


def test_old_mutation_receipt_does_not_block_current_pure_read():
    agent = _agent()
    key = call_key("browser_snapshot", {})
    agent._work_mutation_evidence = {key: {"status": "uncertain"}}
    assert decisions_for_calls(agent, [_call("browser_snapshot")]) == [CompilationDecision.ALLOW_ADAPTIVE]


def test_request_is_stable_by_task_session_reason_scope(tmp_path):
    path = tmp_path / "human_handoffs.json"
    mgr = HumanHandoffManager(path)
    a = mgr.request(task_id="t_test", session_id="s_test", reason="uncertain_mutation_requires_review",
                    scope={"operation_key": "identity-1"})
    b = HumanHandoffManager(path).request(
        task_id="t_test", session_id="s_test", reason="uncertain_mutation_requires_review",
        scope={"operation_key": "identity-1"})
    assert a.handoff_id == b.handoff_id
    assert mgr.resume(a.handoff_id, returned_by="human") is True
    loaded = HumanHandoffManager(path)
    assert loaded.consume(a.handoff_id) is True
    assert loaded.consume(a.handoff_id) is False
    after = HumanHandoffManager(path).request(
        task_id="t_test", session_id="s_test", reason="uncertain_mutation_requires_review",
        scope={"operation_key": "identity-1"})
    assert after.handoff_id == a.handoff_id
    assert len(loaded._handoffs) == 1


def test_one_handoff_per_mutation_even_after_resume(tmp_path, monkeypatch):
    from workstation.integrations.hermes import tool_batch_admission as admission

    monkeypatch.setattr(admission, "get_hermes_home", lambda: tmp_path)
    agent = _agent()
    name, args = "write_file", {"path": "x.txt", "content": "value"}
    agent._work_mutation_evidence = {call_key(name, args): {"status": "uncertain"}}
    first = admission.workstation_tool_batch_admission(agent, [_call(name, args, "call-A")])
    second = admission.workstation_tool_batch_admission(agent, [_call(name, args, "call-B")])
    assert first is not None and second is not None
    a = json.loads(first.decisions[0].synthetic_result)
    b = json.loads(second.decisions[0].synthetic_result)
    assert a["handoff_id"] == b["handoff_id"]
    path = tmp_path / "workstation" / "human_handoffs.json"
    mgr = HumanHandoffManager(path)
    assert len(mgr._handoffs) == 1
    assert mgr.resume(a["handoff_id"], returned_by="human")
    third = admission.workstation_tool_batch_admission(agent, [_call(name, args, "call-C")])
    receipt = json.loads(third.decisions[0].synthetic_result)
    assert receipt["status"] == "human_review_completed"
    assert receipt["code"] == "uncertain_effect_requires_readback"
    assert HumanHandoffManager(path).get(a["handoff_id"]).status == "consumed"
    fourth = admission.workstation_tool_batch_admission(agent, [_call(name, args, "call-D")])
    assert json.loads(fourth.decisions[0].synthetic_result)["handoff_id"] == a["handoff_id"]
    assert len(HumanHandoffManager(path)._handoffs) == 1


def test_uncertain_handoff_never_reuses_approval_from_superseded_run(tmp_path, monkeypatch):
    """A previous TaskRun's consumed human review is not a fresh run's grant."""
    from workstation.integrations.hermes import tool_batch_admission as admission

    monkeypatch.setattr(admission, "get_hermes_home", lambda: tmp_path)
    args = {"ref": "@e17", "button": "left"}
    name = "browser_click"
    operation_key = call_key(name, args)
    agent = _agent()
    agent._canonical_work_task_id = "same-canonical-task"
    agent._canonical_work_run_id = "run-old"
    agent._work_mutation_evidence = {operation_key: {"status": "uncertain"}}
    call = _call(name, args, "first-review")
    prior = admission.workstation_tool_batch_admission(agent, [call])
    old_id = json.loads(prior.decisions[0].synthetic_result)["handoff_id"]
    path = tmp_path / "workstation" / "human_handoffs.json"
    mgr = HumanHandoffManager(path)
    assert mgr.resume(old_id, returned_by="human")
    admission.workstation_tool_batch_admission(agent, [call])
    assert HumanHandoffManager(path).get(old_id).status == "consumed"

    agent._canonical_work_run_id = "run-new"
    current = admission.workstation_tool_batch_admission(agent, [_call(name, args, "new-run")])
    current_body = json.loads(current.decisions[0].synthetic_result)
    assert current_body["handoff_id"] != old_id
    assert current_body["status"] == "handoff_requested"
    current_ledger = HumanHandoffManager(path)
    assert current_ledger.get(old_id).status == "consumed"
    assert current_ledger.get(current_body["handoff_id"]).status == "waiting-for-human"
    assert len(current_ledger._handoffs) == 2


def test_consumed_review_returns_readback_guidance_without_another_handoff(tmp_path, monkeypatch):
    from agent.tool_batch_admission import BatchAdmissionAction
    from workstation.integrations.hermes import tool_batch_admission as admission

    monkeypatch.setattr(admission, "get_hermes_home", lambda: tmp_path)
    agent = _agent()
    agent._canonical_work_task_id = "task-p0"
    agent._canonical_work_run_id = "run-p0"
    name, args = "browser_click", {"ref": "@e24"}
    agent._work_mutation_evidence = {call_key(name, args): {"status": "uncertain"}}
    operation = _call(name, args)
    initial = admission.workstation_tool_batch_admission(agent, [operation])
    assert initial.decisions[0].action == BatchAdmissionAction.HANDOFF
    handoff = json.loads(initial.decisions[0].synthetic_result)
    manager = HumanHandoffManager(tmp_path / "workstation" / "human_handoffs.json")
    assert manager.resume(handoff["handoff_id"], returned_by="human")

    completed = admission.workstation_tool_batch_admission(agent, [operation])
    repeated = admission.workstation_tool_batch_admission(agent, [operation])
    for result in (completed, repeated):
        assert result.decisions[0].action == BatchAdmissionAction.SYNTHETIC_RESULT
        message = json.loads(result.decisions[0].synthetic_result)
        assert message["code"] == "uncertain_effect_requires_readback"
        assert message["handoff_id"] == handoff["handoff_id"]

    # The original mutating operation has not been authorized by review alone.
    assert decisions_for_calls(agent, [operation]) == [CompilationDecision.REQUIRE_HUMAN]
    final = HumanHandoffManager(manager.path)
    assert final.get(handoff["handoff_id"]).status == "consumed"
    assert len(final._handoffs) == 1
