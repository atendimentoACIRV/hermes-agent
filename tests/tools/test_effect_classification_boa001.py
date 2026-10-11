"""BOA-001: effect contracts must match the actually dispatched operation."""
import pytest

from tools import (annotate_preview_tool, browser_tool, browser_vault_tool,
                   drive_preview_tool, feishu_doc_tool, feishu_drive_tool,
                   preview_tool, todo_tool, vault_tools, workstation_extensions,
                   x_search_tool, yuanbao_tools)
from tools.effects import ToolEffect, tool_effect
from workstation.batch_detection import mutation_identity


@pytest.mark.parametrize("name", [
    "annotate_preview", "browser_navigate", "browser_click", "browser_type",
    "browser_press", "browser_scroll", "browser_back", "browser_batch_actions",
    "desktop_preview",
])
def test_interaction_not_classified_as_destructive_mutation(name):
    assert tool_effect(name) == ToolEffect.INTERACTIVE


@pytest.mark.parametrize("name", [
    "browser_extension_list", "browser_vault_list", "feishu_doc_read",
    "feishu_drive_list_comment_replies", "feishu_drive_list_comments",
    "vault_read", "vault_search", "x_search", "yb_query_group_info",
    "yb_query_group_members", "yb_search_sticker",
])
def test_discovery_and_read_tools_do_not_generate_write_effects(name):
    assert tool_effect(name) == ToolEffect.PURE_READ


@pytest.mark.parametrize(("name", "args", "expected"), [
    ("browser_console", {}, ToolEffect.PURE_READ),
    ("browser_console", {"clear": False}, ToolEffect.PURE_READ),
    ("browser_console", {"clear": True}, ToolEffect.INTERACTIVE),
    ("browser_console", {"expression": "document.title"}, ToolEffect.MUTATION),
    ("browser_console", {"expression": ""}, ToolEffect.MUTATION),
    ("todo_list", {}, ToolEffect.PURE_READ),
    ("todo_list", {"todos": None}, ToolEffect.PURE_READ),
    ("todo_list", {"todos": []}, ToolEffect.MUTATION),
    ("desktop_preview", {"action": "read"}, ToolEffect.PURE_READ),
    ("desktop_preview", {"action": "open"}, ToolEffect.INTERACTIVE),
    ("drive_preview", {"action": "elements"}, ToolEffect.DISCOVERY),
    ("drive_preview", {"action": "click"}, ToolEffect.INTERACTIVE),
    ("browser_read_http", {"method": "GET"}, ToolEffect.PURE_READ),
    ("browser_read_http", {"method": "POST"}, ToolEffect.MUTATION),
])
def test_argument_sensitive_effects(name, args, expected):
    assert tool_effect(name, args=args) == expected


@pytest.mark.parametrize("name", [
    "browser_vault_unlock", "vault_write", "feishu_drive_add_comment",
    "yb_send_sticker", "browser_extension_install",
])
def test_mutations_stay_conservative(name):
    assert tool_effect(name) == ToolEffect.MUTATION


def test_a2a_reads_are_declared_to_plugin_registry():
    from plugins.platforms.a2a import tools as a2a

    class Capture:
        def __init__(self):
            self.schemas = {}

        def register_tool(self, **kwargs):
            self.schemas[kwargs["name"]] = kwargs["schema"]

    capture = Capture()
    a2a.register_tools(capture)
    assert capture.schemas["a2a_list"]["effect"] == "PURE_READ"
    assert capture.schemas["a2a_history"]["effect"] == "PURE_READ"
    assert capture.schemas["a2a_call"]["effect"] == "MUTATION"
