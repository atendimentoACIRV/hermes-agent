"""Five real AIAgent turn admissions sharing one native Browser controller.

Model decisions and controller transport are deterministic local fakes; the
conversation loop, agent tool middleware, and Workstation turn admission
remain real. No external service or user Kanban database is touched.
"""
from __future__ import annotations

import json

import pytest
from types import SimpleNamespace
from unittest.mock import patch

from workstation.kanban import WorkstationKanbanBridge
from tools import browser_workstation as bw


def _tool(name: str, arguments: dict, index: int):
    return SimpleNamespace(
        id=f"turn-call-{index}", type="function",
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


def _response(content=None, tool_calls=None):
    return SimpleNamespace(
        choices=[SimpleNamespace(
            message=SimpleNamespace(content=content, tool_calls=tool_calls),
            finish_reason="tool_calls" if tool_calls else "stop",
        )],
        model="test/model", usage=None,
    )


@pytest.mark.parametrize("inject_lost_ack", [False, True])
def test_five_consecutive_agent_turns_cannot_poison_independent_tools(tmp_path, monkeypatch, inject_lost_ack):
    from run_agent import AIAgent
    from agent.tool_guardrails import ToolCallGuardrailConfig, ToolCallGuardrailController
    from gateway.session_context import set_session_vars, clear_session_vars
    import workstation

    home = tmp_path / "hermes"
    home.mkdir(exist_ok=True)
    browser_home = tmp_path / "desktop"
    browser_home.mkdir(exist_ok=True)
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setenv("HERMES_WORKSTATION_HOME", str(browser_home))
    monkeypatch.setattr("hermes_constants.get_hermes_home", lambda: home)
    monkeypatch.setenv("HERMES_WORKSTATION_BROWSER", "1")
    monkeypatch.setenv("HERMES_WORKSTATION_BROWSER_ROUTING", "0")
    control = browser_home / "browser-control.json"
    control.write_text(json.dumps({
        "version": 1, "url": "http://127.0.0.1:49152", "token": "test-token",
    }))
    monkeypatch.setenv("HERMES_WORKSTATION_BROWSER_CONTROL_FILE", str(control))
    bw._LAST_HEALTH_AT, bw._LAST_HEALTH_VALUE = 0.0, False
    actions = []
    observed_url = {"value": "about:blank"}

    def physical(method, path, payload=None, **_kw):
        if method == "GET":
            return {"success": True, "ready": True}
        assert path == "/v1/action"
        action = payload["action"]
        actions.append(action)
        if action == "browser_navigate":
            observed_url["value"] = payload["arguments"]["url"]
            if inject_lost_ack and observed_url["value"] == "https://www.youtube.com":
                # External effect applied; the response to Hermes was lost.
                raise TimeoutError("controlled post-dispatch lost ACK")
        return {"success": True, "result": {
            "success": True, "runtime": "electron-chromium",
            "action": action, "url": observed_url["value"], "readiness": "stable",
            "operation_id": payload.get("operation_id"),
        }}

    monkeypatch.setattr(bw, "_request_json", physical)
    workstation.bootstrap_workstation_adapter("required")
    with (patch("model_tools.check_toolset_requirements", return_value={}),
          patch("agent.process_bootstrap.OpenAI")):
        agent = AIAgent(api_key="test-key-1234567890", base_url="https://test.api",
                        quiet_mode=True, skip_context_files=True, skip_memory=True)

    agent.session_id = "five-turn-chat"
    agent._conversation_root_id = lambda: "five-turn-chat"
    agent.provider = "moa"
    agent._tool_guardrails = ToolCallGuardrailController(
        ToolCallGuardrailConfig.from_mapping({}, platform="cli"))
    agent._work_capabilities = {}
    agent._work_user_constraints = {}
    agent._workstation_event_bus = None
    agent._interrupt_requested = False
    # Prevent independent background skill-review worker from creating work
    # in this diagnostic fixture or contacting auxiliary providers.
    agent.skip_background_review = True
    agent.valid_tool_names = set(agent.valid_tool_names or ()) | {
        "browser_navigate", "browser_snapshot", "terminal", "work_execute",
    }

    turns = [
        ("Abra o Google.", "browser_navigate", {"url": "https://www.google.com"}),
        ("Mostre a página atual.", "browser_snapshot", {}),
        ("Abra o YouTube.", "browser_navigate", {"url": "https://www.youtube.com"}),
        ("Mostre novamente a página.", "browser_snapshot", {}),
        ("Execute o comando de terminal de verificação.", "terminal", {"command": "echo agent-independent"}),
    ]
    provider_results = []
    for i, (_, name, args) in enumerate(turns):
        provider_results.extend([_response(tool_calls=[_tool(name, args, i)]),
                                 _response(content=f"Turn {i} complete")])

    def provider(*_a, **_kw):
        assert provider_results, "Unexpected provider call (agent loop)"
        return provider_results.pop(0)

    agent.client = SimpleNamespace(chat=SimpleNamespace(
        completions=SimpleNamespace(create=provider)))
    dispatched = []

    def route(name, args, task_id, **_kw):
        dispatched.append(name)
        if name == "terminal":
            return "agent-independent"
        assert name in {"browser_navigate", "browser_snapshot"}
        return bw.workstation_routed_browser_handler(
            name, args, task_id=task_id, session_id=agent.session_id,
            fallback=lambda: (_ for _ in ()).throw(AssertionError("legacy browser fallback")),
        )

    session_tokens = set_session_vars(
        platform="desktop", source="desktop", session_id="five-turn-chat",
        browser_control_principal="workstation",
        browser_control_transport_family="workstation_native",
    )
    try:
        with patch("model_tools.handle_function_call", side_effect=route):
            for text, _, _ in turns:
                result = agent.run_conversation(user_message=text)
                assert result["completed"] is True, result
                tool_receipts = [m.get("content", "") for m in result.get("messages", [])
                                 if isinstance(m, dict) and m.get("role") == "tool"]
                assert not any("SUPERSEDED" in str(value) for value in tool_receipts)
                assert getattr(agent, "_canonical_work_run_id", None) is None
    finally:
        clear_session_vars(session_tokens)

    assert not provider_results
    assert dispatched == [row[1] for row in turns]
    assert actions == [row[1] for row in turns if row[1].startswith("browser_")]
    assert actions.count("browser_navigate") == 2  # no blind replay after timeout
    assert observed_url["value"] == "https://www.youtube.com"
    with WorkstationKanbanBridge().get_connection() as conn:
        cards = conn.execute("SELECT body, status FROM tasks").fetchall()
        assert not cards, [tuple(row) for row in cards]
