"""Hermes Agent built-in tool for prefabricated capability discovery (toolset=browser).

READ-ONLY. Provides catalog listing and intent matching without side effects.
No browser automation, no mutations, no external calls.
"""
from __future__ import annotations

import json
from tools.registry import registry


def _handler(args, **_kwargs):
    from workstation.prefabs.catalog import DESTINATIONS, match_navigation, match_trello_read, get_destination
    try:
        action = (args or {}).get("action", "catalog")
        if action == "catalog":
            payload = {"status": "ok", "targets": [{"id": d.key, "title": d.title, "url": d.url, "aliases": list(d.aliases)}
                                                    for d in DESTINATIONS]}
        elif action == "match_navigation":
            text = str(args.get("text") or "")
            dest = match_navigation(text)
            if dest:
                payload = {"status": "matched", "target": {"id": dest.key, "title": dest.title, "url": dest.url}}
            else:
                payload = {"status": "no_match", "target": None}
        elif action == "match_trello_read":
            text = str(args.get("text") or "")
            intent = match_trello_read(text)
            if intent:
                payload = {"status": "matched", "board": intent.board, "search": intent.search}
            else:
                payload = {"status": "no_match", "board": None, "search": None}
        elif action == "get_destination":
            key = str(args.get("key") or "")
            dest = get_destination(key)
            payload = {"status": "ok", "target": {"id": dest.key, "title": dest.title, "url": dest.url, "aliases": list(dest.aliases)}}
        else:
            raise ValueError(f"Unknown action: {action}")
        return json.dumps({"ok": True, "data": payload}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error_code": type(exc).__name__,
                           "error": str(exc) if type(exc).__name__ in ("ValueError",)
                           else "Capability unavailable"}, ensure_ascii=False)


def _available() -> bool:
    """Always available when browser toolset is enabled; no external deps."""
    try:
        from workstation.config import load_workstation_config
        return bool(load_workstation_config().enabled)
    except Exception:
        return True  # Available in Agent context when browser toolset is active


registry.register(
    name="prefab_catalog", toolset="browser", handler=_handler, check_fn=_available,
    schema={"name": "prefab_catalog",
            "description": ("Read-only catalog of prefabricated Hermes Workstation operational capabilities. "
                            "Action 'catalog' lists all known destinations. "
                            "Action 'match_navigation' tests if a human command matches a known destination. "
                            "Action 'match_trello_read' tests if a command matches a known Trello board read. "
                            "Action 'get_destination' returns full details for a destination key. "
                            "No browser automation, no mutations, no external calls."),
            "parameters": {"type": "object", "properties": {
                "action": {"type": "string", "enum": ["catalog", "match_navigation", "match_trello_read", "get_destination"]},
                "text": {"type": "string", "description": "Human command text to match (for match_navigation/match_trello_read)"},
                "key": {"type": "string", "description": "Destination key (for get_destination)"}},
                "required": ["action"], "additionalProperties": False}},
    description="Prefabricated capability catalog and intent matcher",
    emoji="📦",
)