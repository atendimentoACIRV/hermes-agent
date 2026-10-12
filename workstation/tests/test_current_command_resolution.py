"""Fresh commands reach the existing router without a historical objective."""
from types import SimpleNamespace

from agent.operational_resolution import OperationalOutcome, OperationalResolutionContext
from workstation.contracts import IntentAuthority, MessageEnvelope, MessageOrigin
from workstation.control_plane.contract import CapabilityFormalContract
from workstation.control_plane.ir import EQ, SET
from workstation.control_plane.lattice import AuthorityLevel, AuthorityScope
from workstation.durable_tasks import DurableTaskStore
from workstation.integrations.hermes.operational_resolution import workstation_operational_resolution
from workstation.operational_capabilities import (
    CapabilityLifecycle, OperationalCapability, OperationalCapabilityRegistry,
)
from workstation.work_intent import prepare_turn_work


def admit(text, authority=IntentAuthority.CREATE_WORK):
    agent = SimpleNamespace(session_id="fresh-command", _conversation_root_id=lambda: "fresh-command",
        _interrupt_requested=False, _tool_guardrails=None, _work_capabilities={},
        _work_user_constraints={}, _current_provider_usage=None, _work_completed_mutations={},
        _work_mutation_evidence={}, _workstation_event_bus=None, valid_tool_names=set())
    envelope = MessageEnvelope(MessageOrigin.HUMAN, authority, agent.session_id, text)
    return agent, prepare_turn_work(agent, text, envelope)


def consult(agent):
    return workstation_operational_resolution(OperationalResolutionContext(
        agent=agent, session_id=agent.session_id,
        task_id=str(getattr(agent, "_canonical_work_task_id", "") or ""), turn_id="fresh-turn",
        user_message=agent._message_envelope.content, messages=[], api_call_count=0, iteration=0))


def test_fresh_trello_command_reaches_authority_router_without_prior_objective():
    agent, work = admit("Abre o Trello.")
    assert work.requires_task and work.requires_browser
    assert agent._canonical_work_task_id
    store = DurableTaskStore()
    try:
        assert store.get_connection().execute("SELECT COUNT(*) FROM work_plans").fetchone()[0] == 0
    finally:
        store.close()
    # A real registered candidate requires authority human ingress cannot grant.
    # The existing router must refuse it; recognition must never elevate permission.
    OperationalCapabilityRegistry().register(OperationalCapability(
        id="test.open_trello", name="open Trello", version="1",
        lifecycle=CapabilityLifecycle.PROMOTED,
        formal_contract=CapabilityFormalContract(
            operation_family="browser.open_site", target_family="native_browser",
            typed_postconditions=[EQ("host", "trello.com"), EQ("page_family", "/"), EQ("recovery_state", "live")],
            effect_footprint=[SET("host", "trello.com"), SET("page_family", "/"), SET("recovery_state", "live")],
            authority_required=AuthorityScope(level=AuthorityLevel.EXTERNAL_REVERSIBLE,
                allowed_actions={"navigate"}, allowed_resources={"native_browser"}),
            verifier={"kind": "value", "evidence_strength": "E2"})))
    resolution = consult(agent)
    assert resolution is not None and resolution.outcome is OperationalOutcome.HANDOFF
    assert resolution.reason == "ASK_HUMAN"


def test_ambiguous_observed_uninstalled_and_cancelled_commands_do_not_dispatch():
    for text in ("Abre o Trello ou o Hyperframe.", "Não abre o Trello.",
                 "Como abre o Trello?", "Abre o Trello e apaga tudo."):
        agent, work = admit(text)
        assert not work.requires_task
        assert consult(agent) is None
    observed, work = admit("Abre o Trello.", IntentAuthority.OBSERVATION_ONLY)
    assert not work.requires_task and consult(observed) is None
    fresh, work = admit("Abre o Trello.")
    assert work.requires_task
    assert consult(fresh) is None, "missing installed capability falls back to reasoning"
    fresh._interrupt_requested = True
    assert consult(fresh) is None


def test_dispatch_failure_returns_wait_safely(monkeypatch):
    """When dispatch raises an exception, operational resolution returns WAIT and does not retry blindly."""
    agent, work = admit("Abre o Trello.")
    assert work.requires_task

    from unittest.mock import patch
    with patch("workstation.integrations.hermes.operational_resolution._dispatch_intent", side_effect=RuntimeError("Controller connection lost")):
        with patch("workstation.work_intent.current_command_objective", return_value={"operation_id": "op_test", "operation_intent": {}, "inputs": {}}):
            resolution = consult(agent)
            assert resolution is not None
            assert resolution.outcome is OperationalOutcome.WAIT
            assert "Controller connection lost" in resolution.final_response or "RuntimeError" in resolution.final_response
            assert "dispatch_failed:RuntimeError" in resolution.reason


def test_fresh_hyperframe_command_falls_back_safely_without_studio_capability():
    """P1.5 RED lock: 'Abre o Hyperframe.' must not dispatch terminal/skill search.

    No creative capability is installed in this context, so resolution must fall
    back to reasoning (None) — never EXECUTED, never a terminal/skill-search
    side effect from the pre-reasoning path.
    """
    agent, work = admit("Abre o Hyperframe.")
    assert work.requires_task
    # No creative capability is installed: the router must refuse without
    # effects and the boundary must fall back to reasoning (None) — never
    # EXECUTED from the pre-reasoning path without owner-certified readback.
    resolution = consult(agent)
    assert resolution is None
    # Ambiguous Hyperframe variants stay reasoning work.
    for text in ("Abre o Hyperframe ou o Trello.", "Como abre o Hyperframe?",
                 "Abre o Hyperframe e apaga tudo."):
        ambiguous, ambiguous_work = admit(text)
        assert not ambiguous_work.requires_task
        assert consult(ambiguous) is None

