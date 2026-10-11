"""Hermes Workstation built-in tool for prefabricated operations (toolset=desktop_ui).

READ-ONLY. All mutation tools must continue through existing Workstation work_execute
with authority and verifier controls, or through explicit human-operated CLI.
"""
from __future__ import annotations

import json
from tools.registry import registry


def _available() -> bool:
    try:
        from workstation.config import load_workstation_config
        return bool(load_workstation_config().enabled)
    except Exception:
        return False


def _handler(args, **_kwargs):
    from workstation.prefabs.catalog import DESTINATIONS
    from workstation.prefabs.trello import TrelloClient
    try:
        action = (args or {}).get("action", "catalog")
        if action == "catalog":
            payload = {"status": "ok", "targets": [{"id": d.key, "title": d.title, "url": d.url}
                                                    for d in DESTINATIONS],
                       "trello_actions": ["board_lists", "board_cards", "card", "prepare_description"]}
        elif action in {"board_lists", "board_cards", "card", "prepare_description"}:
            client = TrelloClient()
            if action == "board_lists":
                payload = client.board_lists(args["board"])
            elif action == "board_cards":
                payload = client.board_cards(args["board"], search=str(args.get("search") or ""),
                                             limit=min(100, max(1, int(args.get("limit", 50)))))
            elif action == "card":
                payload = client.card(args["card_id"], include_description=False)
            else:
                payload = client.prepare_description(args["card_id"], args["description"])
        else:
            raise ValueError("Unknown read-only prefab action")
        return json.dumps({"ok": True, "data": payload}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error_code": type(exc).__name__,
                           "error": str(exc) if type(exc).__name__ in ("ValueError", "TrelloAccessError")
                           else "Capability unavailable or missing authorization"}, ensure_ascii=False)


registry.register(
    name="prefab_execute", toolset="desktop_ui", handler=_handler, check_fn=_available,
    schema={"name": "prefab_execute",
            "description": ("Read-only precompiled Hermes Workstation operations. No reasoning loops, "
                            "script execution, browser console, or external mutations. "
                            "action=catalog lists targets. Trello actions use supported official REST API, "
                            "requiring TRELLO_API_KEY and TRELLO_TOKEN configured in the Hermes runtime. "
                            "prepare_description returns a hash-only proposed update, not a write."),
            "parameters": {"type": "object", "properties": {
                "action": {"type": "string", "enum": ["catalog", "board_lists", "board_cards", "card", "prepare_description"]},
                "board": {"type": "string", "description": "editorial, scrum, or Trello board ID"},
                "card_id": {"type": "string"},
                "search": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "description": {"type": "string", "description": "Desired text (hash comparison only, no write)"}},
                "required": ["action"], "additionalProperties": False}}
)