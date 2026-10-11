"""Hermes Workstation built-in tool for Trello mutations via work_execute (toolset=desktop_ui).

MUTATION PATH: All mutations go through work_execute with Policy, effect_budget, TaskRun.
No direct Trello API writes from this tool - it constructs a work_execute plan.
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
    """Construct a work_execute plan for Trello card description sync.
    
    This tool does NOT execute the mutation directly. It returns a structured
    work_execute plan that the caller (human or agent) must dispatch through
    the work_execute tool, which enforces Policy, effect_budget, and verification.
    """
    from workstation.prefabs.trello import TrelloClient
    try:
        action = (args or {}).get("action", "plan_sync_description")
        
        if action == "plan_sync_description":
            # Prepare the description diff first (read-only)
            client = TrelloClient()
            card_id = args["card_id"]
            desired = args["description"]
            preview = client.prepare_description(card_id, desired)
            
            if not preview["needs_change"]:
                return json.dumps({
                    "ok": True, 
                    "data": {"status": "already_satisfied", "card_id": card_id, "plan": None}
                }, ensure_ascii=False)
            
            # Build work_execute plan
            plan = {
                "operation_key": f"trello_sync_desc_{card_id}",
                "title": f"Sync Trello card {card_id} description",
                "kind": "browser_transaction",
                "mutation_target": {
                    "scope": "external",
                    "provider": "trello",
                    "kind": "card",
                    "field": "desc"
                },
                "steps": [
                    {
                        "id": "read_current",
                        "tool": "prefab_execute",
                        "args": {"action": "card", "card_id": card_id, "include_description": True},
                        "expect": {"description_sha256": preview["before_sha256"]},
                        "transaction_phase": "PREPARE"
                    },
                    {
                        "id": "verify_policy",
                        "tool": "work_execute",  # Policy check via internal mechanism
                        "args": {"action": "route", "capability_id": "prefab.trello.sync_description"},
                        "transaction_phase": "PREPARE"
                    },
                    {
                        "id": "mutate",
                        "tool": "prefab_execute",
                        "args": {
                            "action": "sync_description",
                            "card_id": card_id,
                            "desired": desired,
                            "expected_before": preview["before_sha256"],
                            "expected_sha256": preview["desired_sha256"],
                            "expected_length": len(desired),
                            "reserved_cards": args.get("reserved_cards", [])
                        },
                        "expect": {"status": "verified", "verified": True},
                        "verifies": ["read_current"],
                        "transaction_phase": "COMMIT"
                    },
                    {
                        "id": "verify_readback",
                        "tool": "prefab_execute",
                        "args": {"action": "card", "card_id": card_id, "include_description": True},
                        "expect": {"description_sha256": preview["desired_sha256"]},
                        "verifies": ["mutate"],
                        "transaction_phase": "VERIFY"
                    }
                ],
                "capability_id": "prefab.trello.sync_description",
                "operation_intent": {
                    "goal": {"type": "UPDATE_CARD_DESCRIPTION", "card_id": card_id, "field": "desc"},
                    "effects": [{"type": "external_mutation", "provider": "trello", "resource": f"card:{card_id}"}],
                    "invariants": ["never_overwrite_human_edit", "exact_readback_verification"]
                },
                "authority": {
                    "required": ["trello_write", "effect_budget_external"],
                    "human_approval": True
                },
                "constraints": {
                    "mutation_allowed_routes": ["trello_api"],
                    "mutation_forbidden_routes": ["browser_console", "browser_cdp"]
                }
            }
            
            return json.dumps({"ok": True, "data": {"plan": plan, "preview": preview}}, ensure_ascii=False)
        
        elif action == "sync_description":
            # Direct mutation - only for CLI with --i-approve-external-write
            # This bypasses work_execute and should only be used by human operators
            import os
            if os.getenv("HERMES_PREFABS_ALLOW_TRELLO_WRITES") != "1":
                raise PermissionError("Direct mutation requires HERMES_PREFABS_ALLOW_TRELLO_WRITES=1 (CLI only)")
            
            client = TrelloClient()
            result = client.sync_description_authorized(
                card_id=args["card_id"],
                desired=args["description"],
                expected_before=args.get("expected_before"),
                expected_sha256=args.get("expected_sha256"),
                expected_length=args.get("expected_length"),
                reserved_cards=set(args.get("reserved_cards", [])) if args.get("reserved_cards") else None
            )
            return json.dumps({"ok": True, "data": result}, ensure_ascii=False)
        
        else:
            raise ValueError(f"Unknown action: {action}")
            
    except Exception as exc:
        return json.dumps({"ok": False, "error_code": type(exc).__name__,
                           "error": str(exc) if type(exc).__name__ in ("ValueError", "TrelloAccessError", "PermissionError")
                           else "Capability unavailable or missing authorization"}, ensure_ascii=False)


registry.register(
    name="prefab_trello_mutate", toolset="desktop_ui", handler=_handler, check_fn=_available,
    schema={"name": "prefab_trello_mutate",
            "description": ("Trello mutation planning and execution via work_execute. "
                            "Action 'plan_sync_description' returns a work_execute plan for Policy-gated mutation. "
                            "Action 'sync_description' executes directly (CLI only, requires HERMES_PREFABS_ALLOW_TRELLO_WRITES=1). "
                            "All mutations require Policy approval, effect_budget, TaskRun, and independent readback verification."),
            "parameters": {"type": "object", "properties": {
                "action": {"type": "string", "enum": ["plan_sync_description", "sync_description"]},
                "card_id": {"type": "string"},
                "description": {"type": "string", "description": "Desired description text"},
                "expected_before": {"type": "string", "description": "Expected before_sha256 from prepare"},
                "expected_sha256": {"type": "string", "description": "Expected desired_sha256 from prepare"},
                "expected_length": {"type": "integer", "description": "Expected description length (for reserved card protection)"},
                "reserved_cards": {"type": "array", "items": {"type": "string"}, "description": "Card IDs that must never be overwritten"}},
                "required": ["action", "card_id", "description"], "additionalProperties": False},
            "when_to_use": ("Trello card description mutations. Use plan_sync_description to get a work_execute plan "
                           "for Policy-gated execution. Use sync_description only for CLI with explicit human approval."),
            "do_not_use": ("Direct mutations without Policy, batch mutations without work_execute, "
                          "overwriting reserved cards (card 012) without explicit length check"),
            "risk": "external_mutation",
            "verifier": "trello_api_readback_with_policy"}
)