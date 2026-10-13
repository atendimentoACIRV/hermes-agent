"""Isolated Playwright child: genuine Hermes AIAgent turns through native Electron HTTP.

Only the inference model is scripted; browser _request_json talks to a real
Electron controller started by workstation-headless-load.spec.ts. All URLs are
loopback test pages, all session IDs are generated in the isolated renderer.
"""
from __future__ import annotations

import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

from gateway.session_context import clear_session_vars, set_session_vars
from tools import browser_workstation as bw
from workstation.kanban import WorkstationKanbanBridge


def _tool(name, args, number):
    return SimpleNamespace(
        id=f"native-agent-{number}", type="function",
        function=SimpleNamespace(name=name, arguments=json.dumps(args)),
    )


def _response(*, content=None, call=None):
    return SimpleNamespace(
        choices=[SimpleNamespace(
            message=SimpleNamespace(content=content, tool_calls=[call] if call else None),
            finish_reason="tool_calls" if call else "stop",
        )], model="test/model", usage=None,
    )


def _agent(session_id, provider_responses):
    from run_agent import AIAgent
    from agent.tool_guardrails import ToolCallGuardrailConfig, ToolCallGuardrailController
    import workstation

    workstation.bootstrap_workstation_adapter("required")
    with (patch("model_tools.check_toolset_requirements", return_value={}),
          patch("agent.process_bootstrap.OpenAI")):
        agent = AIAgent(
            api_key="test-key-1234567890", base_url="https://test.api",
            quiet_mode=True, skip_context_files=True, skip_memory=True,
        )
    agent.session_id = session_id
    agent._conversation_root_id = lambda: session_id
    agent.provider = "moa"
    agent.skip_background_review = True
    agent._tool_guardrails = ToolCallGuardrailController(
        ToolCallGuardrailConfig.from_mapping({}, platform="cli"),
    )
    agent._work_capabilities = {}
    agent._work_user_constraints = {}
    agent._workstation_event_bus = None
    agent._interrupt_requested = False
    agent.valid_tool_names = set(agent.valid_tool_names or ()) | {
        "browser_navigate", "browser_snapshot", "terminal", "work_execute",
    }

    def provider(*_args, **_kwargs):
        assert provider_responses, "Unplanned provider call"
        return provider_responses.pop(0)

    agent.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=provider)),
    )
    return agent


def main():
    if len(sys.argv) != 5:
        raise SystemExit("expected: sessionA sessionB localBaseUrl controllerFile")
    session_a, session_b, base_url, control_file = sys.argv[1:]
    assert base_url.startswith("http://127.0.0.1:"), "only local test pages"
    assert os.environ.get("HERMES_HOME") and os.environ.get("HERMES_WORKSTATION_HOME")
    assert os.path.isfile(control_file), "real Electron controller descriptor missing"
    os.environ["HERMES_WORKSTATION_BROWSER_CONTROL_FILE"] = control_file
    os.environ["HERMES_WORKSTATION_BROWSER"] = "1"
    os.environ["HERMES_WORKSTATION_BROWSER_ROUTING"] = "0"
    bw._LAST_HEALTH_AT, bw._LAST_HEALTH_VALUE = 0.0, False

    # Call the genuine loopback controller. Simulate transport losing exactly
    # one ACK AFTER controller dispatch returns (the effect is already applied).
    physical = bw._request_json
    actions = []
    lost_acks = [0]

    def proxy(method, endpoint, payload=None, **kwargs):
        result = physical(method, endpoint, payload, **kwargs)
        if endpoint == "/v1/action" and payload:
            actions.append((payload.get("session_id"), payload["action"],
                            payload.get("operation_id"), payload.get("task_id")))
            if (payload["action"] == "browser_navigate" and
                    payload.get("arguments", {}).get("url") == base_url + "/p0-agent-youtube" and
                    lost_acks[0] == 0):
                lost_acks[0] += 1
                raise TimeoutError("test: ACK lost after actual Electron navigation")
        return result

    bw._request_json = proxy

    turns_a = [
        ("Abra o site Google local.", "browser_navigate", {"url": base_url + "/p0-agent-google"}),
        ("Descreva a página.", "browser_snapshot", {}),
        ("Abra o site YouTube local.", "browser_navigate", {"url": base_url + "/p0-agent-youtube"}),
        ("Verifique novamente a página.", "browser_snapshot", {}),
        ("Verifique o terminal independente.", "terminal", {"command": "echo agent-isolated"}),
    ]

    responses_a = []
    for index, (_, name, args) in enumerate(turns_a):
        responses_a.extend([
            _response(call=_tool(name, args, index)),
            _response(content=f"Completed turn {index + 1}"),
        ])
    a = _agent(session_a, responses_a)
    dispatched = []

    def route(name, args, task_id, **kwargs):
        dispatched.append((a.session_id, name))
        if name == "terminal":
            return "agent-isolated"
        assert name in {"browser_navigate", "browser_snapshot"}
        return bw.workstation_routed_browser_handler(
            name, args, task_id=task_id, session_id=a.session_id,
            fallback=lambda: (_ for _ in ()).throw(AssertionError("legacy browser fallback")),
        )

    tokens = set_session_vars(
        platform="desktop", source="desktop", session_id=session_a,
        browser_control_principal="workstation",
        browser_control_transport_family="workstation_native",
    )
    try:
        with patch("model_tools.handle_function_call", side_effect=route):
            for prompt, _, _ in turns_a:
                result = a.run_conversation(user_message=prompt)
                assert result["completed"] is True, f"turn failed: {prompt}"
                assert getattr(a, "_canonical_work_run_id", None) is None
        assert not responses_a
    finally:
        clear_session_vars(tokens)

    # Another legitimate session must have its own BrowserTask owner.
    responses_b = [
        _response(call=_tool("browser_navigate", {"url": base_url + "/p0-agent-other-chat"}, 51)),
        _response(content="Other chat complete"),
    ]
    b = _agent(session_b, responses_b)
    tokens_b = set_session_vars(
        platform="desktop", source="desktop", session_id=session_b,
        browser_control_principal="workstation",
        browser_control_transport_family="workstation_native",
    )
    try:
        with patch("model_tools.handle_function_call", side_effect=lambda name, args, task_id, **kw:
                   bw.workstation_routed_browser_handler(
                       name, args, task_id=task_id, session_id=b.session_id,
                       fallback=lambda: (_ for _ in ()).throw(AssertionError("legacy fallback")))):
            result_b = b.run_conversation(user_message="Abra outro site local.")
            assert result_b["completed"] is True
    finally:
        clear_session_vars(tokens_b)
        bw._request_json = physical

    with WorkstationKanbanBridge().get_connection() as conn:
        cards = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

    assert cards == 0, f"point actions created {cards} cards"
    assert lost_acks[0] == 1, f"unexpected ACK count {lost_acks}"
    assert [entry[1] for entry in dispatched] == [entry[1] for entry in turns_a]
    assert len([action for action in actions if action[1] == "browser_navigate"]) == 3

    # Never print the loopback auth token or user payloads; TS verifies physical
    # owner and readback through its own authenticated controller.
    print(json.dumps({
        "accepted": True, "agent_turns": len(turns_a), "distinct_sessions": 2,
        "native_actions": len(actions), "lost_acks": lost_acks[0],
        "terminal_after_lost_ack": True, "kanban_cards": cards,
        "task_ids_a": sorted({str(row[3]) for row in actions if row[0] == session_a}),
        "task_ids_b": sorted({str(row[3]) for row in actions if row[0] == session_b}),
    }))


if __name__ == "__main__":
    main()
