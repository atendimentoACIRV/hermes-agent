"""Regressions for deterministic named-site intents and native-browser contracts."""

from workstation.contracts import IntentAuthority, MessageEnvelope, MessageOrigin
from workstation.control_plane.intent import OperationIntent
from workstation.control_plane.ir import AND, EQ, SET, entails, effect_contained
from workstation.work_intent import current_command_objective


def test_named_trello_navigation_projects_native_browser_state_contract():
    envelope = MessageEnvelope(MessageOrigin.HUMAN, IntentAuthority.CREATE_WORK, "session-a", "Abre o Trello.")
    result = current_command_objective(envelope, "task-a", "run-a")
    assert result is not None
    intent = OperationIntent.from_dict(result["operation_intent"])
    assert intent.target == "native_browser"
    # Fixed allowlisted navigation binds destination in the contract, not as
    # an unsolicited parameter to a compiled zero-input capability.
    assert result["inputs"] == {}
    postconditions = [EQ("host", "trello.com"), EQ("page_family", "/"), EQ("recovery_state", "live")]
    effect_footprint = [SET("host", "trello.com"), SET("page_family", "/"), SET("recovery_state", "live")]
    assert entails(AND(*postconditions), intent.goal)
    assert all(effect_contained(e, intent.effect_budget) for e in effect_footprint)
    assert not entails(AND(EQ("host", "wrong.test")), intent.goal)
    assert SET("host", "wrong.test") not in intent.effect_budget
    # General SET effect containment is path-based, so the exact hostname
    # must remain an independently proven goal (never inferred from budget).


def test_unrecognized_or_untrusted_command_cannot_produce_native_intent():
    for content in ("Abra um site qualquer.", "Não abre o Trello.", "Abra o Trello e apague tudo."):
        envelope = MessageEnvelope(MessageOrigin.HUMAN, IntentAuthority.CREATE_WORK, "session-a", content)
        assert current_command_objective(envelope, "task", "run") is None
    envelope = MessageEnvelope(MessageOrigin.RUNTIME, IntentAuthority.OBSERVATION_ONLY, "session-a", "Abre o Trello.")
    assert current_command_objective(envelope, "task", "run") is None
