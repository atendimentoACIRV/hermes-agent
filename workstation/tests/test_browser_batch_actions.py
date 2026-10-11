from __future__ import annotations

import json
from unittest.mock import patch, MagicMock
import pytest

from tools.registry import registry
from tools.browser_tool import browser_batch_actions, _BROWSER_SCHEMA_MAP
from tools.browser_workstation import (
    _WORKSTATION_SCHEMA_TOOLS,
    WorkstationBrowserUnavailable,
    workstation_routed_browser_handler
)
from workstation.routing import NATIVE_BROWSER_TOOLS
from workstation.browser_session import DESTRUCTIVE_ACTIONS
from workstation.run_adoption import _BROWSER_MUTATIONS


def test_browser_batch_actions_registration_and_schema():
    assert "browser_batch_actions" in _WORKSTATION_SCHEMA_TOOLS
    assert "browser_batch_actions" in NATIVE_BROWSER_TOOLS
    assert "browser_batch_actions" in DESTRUCTIVE_ACTIONS
    assert "browser_batch_actions" in _BROWSER_MUTATIONS

    schema = _BROWSER_SCHEMA_MAP.get("browser_batch_actions")
    assert schema is not None
    assert schema["name"] == "browser_batch_actions"
    assert "steps" in schema["parameters"]["properties"]
    assert "required" in schema["parameters"]
    assert "steps" in schema["parameters"]["required"]


def test_browser_batch_actions_dispatches_to_routed_handler():
    steps = [
        {"kind": "click", "ref": "@e1"},
        {"kind": "type", "ref": "@e2", "text": "hello"}
    ]

    with patch("tools.browser_tool.routed_browser_handler") as mock_routed:
        mock_routed.return_value = json.dumps({"success": True, "batch_result": {"status": "verified"}})

        # Invoke tool function directly
        res_str = browser_batch_actions(steps=steps, task_id="test-task")
        assert "verified" in res_str
        assert mock_routed.called
        call_args = mock_routed.call_args
        assert call_args[0][0] == "browser_batch_actions"
        assert call_args[0][1]["steps"] == steps


def test_browser_batch_actions_fails_closed_when_controller_unavailable():
    steps = [{"kind": "click", "ref": "@e1"}]

    with patch("tools.browser_workstation.workstation_browser_enabled", return_value=True), \
         patch("tools.browser_workstation.workstation_controller_available", return_value=False), \
         patch("tools.browser_workstation.workstation_routing_enabled", return_value=False):
        with pytest.raises(WorkstationBrowserUnavailable):
            workstation_routed_browser_handler(
                "browser_batch_actions",
                {"steps": steps},
                fallback=lambda: "fallback",
                task_id="test-task"
            )
