"""Optionally register audited candidates in the EXISTING capability registry.

'Prefabricated' is a source label, not a forged VERIFIED or PROMOTED status.
"""
from __future__ import annotations

from .catalog import DESTINATIONS


TRELLO_READ_CAPABILITIES = [
    {
        "id": "prefab.trello.board_lists",
        "name": "List Trello Board Lists",
        "route": "trello_api", "effect": "read_only",
        "input_schema": {"type": "object", "properties": {"board": {"type": "string"}}, "required": ["board"]},
        "output_schema": {"type": "object", "properties": {"lists": {"type": "array"}}},
        "scope": {"host": "api.trello.com", "path_family": "/1/boards/*/lists"},
        "preconditions": ["trello_api_credentials_configured", "board_accessible"],
        "postconditions": ["lists_retrieved_via_official_api"],
        "implementation": {"steps": [{"primitive": "trello_api_get", "inputs": {"endpoint": "/1/boards/{board}/lists"}}]},
        "verifier_contract": {"kind": "trello_api_response", "expected_fields": ["id", "name"]},
    },
    {
        "id": "prefab.trello.board_cards",
        "name": "List Trello Board Cards",
        "route": "trello_api", "effect": "read_only",
        "input_schema": {"type": "object", "properties": {"board": {"type": "string"}, "search": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["board"]},
        "output_schema": {"type": "object", "properties": {"cards": {"type": "array"}, "total_matches": {"type": "integer"}}},
        "scope": {"host": "api.trello.com", "path_family": "/1/boards/*/cards"},
        "preconditions": ["trello_api_credentials_configured", "board_accessible"],
        "postconditions": ["cards_retrieved_via_official_api"],
        "implementation": {"steps": [{"primitive": "trello_api_get", "inputs": {"endpoint": "/1/boards/{board}/cards"}}]},
        "verifier_contract": {"kind": "trello_api_response", "expected_fields": ["id", "name", "shortUrl"]},
    },
    {
        "id": "prefab.trello.card",
        "name": "Read Trello Card",
        "route": "trello_api", "effect": "read_only",
        "input_schema": {"type": "object", "properties": {"card_id": {"type": "string"}, "include_description": {"type": "boolean"}}, "required": ["card_id"]},
        "output_schema": {"type": "object", "properties": {"id": {"type": "string"}, "name": {"type": "string"}, "description_sha256": {"type": "string"}}},
        "scope": {"host": "api.trello.com", "path_family": "/1/cards/*"},
        "preconditions": ["trello_api_credentials_configured", "card_accessible"],
        "postconditions": ["card_retrieved_via_official_api"],
        "implementation": {"steps": [{"primitive": "trello_api_get", "inputs": {"endpoint": "/1/cards/{card_id}"}}]},
        "verifier_contract": {"kind": "trello_api_response", "expected_fields": ["id", "name", "description_sha256"]},
    },
    {
        "id": "prefab.trello.prepare_description",
        "name": "Prepare Trello Card Description Diff",
        "route": "trello_api", "effect": "read_only",
        "input_schema": {"type": "object", "properties": {"card_id": {"type": "string"}, "desired": {"type": "string"}}, "required": ["card_id", "desired"]},
        "output_schema": {"type": "object", "properties": {"before_sha256": {"type": "string"}, "desired_sha256": {"type": "string"}, "needs_change": {"type": "boolean"}, "confirmation": {"type": "string"}}},
        "scope": {"host": "api.trello.com", "path_family": "/1/cards/*"},
        "preconditions": ["trello_api_credentials_configured", "card_accessible"],
        "postconditions": ["diff_computed_hash_only"],
        "implementation": {"steps": [{"primitive": "trello_api_get", "inputs": {"endpoint": "/1/cards/{card_id}"}}, {"primitive": "trello_api_compare", "inputs": {"field": "desc"}}]},
        "verifier_contract": {"kind": "trello_hash_compare", "expected_fields": ["before_sha256", "desired_sha256", "confirmation"]},
    },
]


TRELLO_MUTATION_CAPABILITIES = [
    {
        "id": "prefab.trello.sync_description",
        "name": "Sync Trello Card Description (Authorized)",
        "route": "trello_api", "effect": "external_mutation",
        "input_schema": {"type": "object", "properties": {
            "card_id": {"type": "string"},
            "desired": {"type": "string"},
            "expected_before": {"type": "string"},
            "expected_sha256": {"type": "string"},
            "expected_length": {"type": "integer"},
            "reserved_cards": {"type": "array", "items": {"type": "string"}}
        }, "required": ["card_id", "desired"]},
        "output_schema": {"type": "object", "properties": {"status": {"type": "string"}, "verified": {"type": "boolean"}, "card_id": {"type": "string"}}},
        "scope": {"host": "api.trello.com", "path_family": "/1/cards/*"},
        "preconditions": [
            "trello_api_credentials_configured",
            "card_accessible",
            "policy_approval_granted",
            "effect_budget_available",
            "taskrun_bound",
            "human_approval_for_reserved_cards"
        ],
        "postconditions": ["description_synced_verified_readback", "execution_journal_recorded"],
        "implementation": {"steps": [
            {"primitive": "trello_api_get", "inputs": {"endpoint": "/1/cards/{card_id}", "include_description": True}},
            {"primitive": "policy_check", "inputs": {"action": "trello_sync_description", "target": "{card_id}"}},
            {"primitive": "trello_api_put", "inputs": {"endpoint": "/1/cards/{card_id}", "field": "desc", "value": "{desired}"}},
            {"primitive": "trello_api_get", "inputs": {"endpoint": "/1/cards/{card_id}"}},
            {"primitive": "verifier_check", "inputs": {"expected_sha256": "{expected_sha256}"}}
        ]},
        "verifier_contract": {"kind": "trello_api_readback", "expected_fields": ["description_sha256"]},
    },
]


def seed_discovered(registry=None) -> list[str]:
    from workstation.operational_capabilities import (
        CapabilityLifecycle, OperationalCapability, OperationalCapabilityRegistry)
    reg = registry or OperationalCapabilityRegistry()
    added: list[str] = []

    # Browser navigation capabilities
    for target in DESTINATIONS:
        capability_id = "prefab.browser.open." + target.key
        previous = reg.get(capability_id)
        if previous:
            continue
        obj = OperationalCapability(
            id=capability_id,
            name="Open " + target.title,
            route="native_browser", effect="read_only",
            input_schema={"type": "object", "properties": {}, "additionalProperties": False},
            output_schema={"type": "object", "required": ["url_verified"]},
            scope={"host": target.url.split("/")[2], "path_family": target.url},
            preconditions=["authenticated_user_requested_exact_destination"],
            postconditions=["independent_browser_snapshot_url_verified"],
            implementation={"steps": [{"primitive": "browser_navigate", "inputs": {"url": target.url}},
                                      {"primitive": "browser_snapshot", "inputs": {"full": False}}]},
            verifier_contract={"kind": "independent_browser_url_snapshot", "expected_url": target.url},
            lifecycle=CapabilityLifecycle.DISCOVERED,
            provenance={"source": "prefabricated_candidate", "site": target.key},
        )
        reg.register(obj)
        added.append(capability_id)

    # Trello READ capabilities
    for cap_def in TRELLO_READ_CAPABILITIES:
        previous = reg.get(cap_def["id"])
        if previous:
            continue
        obj = OperationalCapability(
            id=cap_def["id"],
            name=cap_def["name"],
            route=cap_def["route"],
            effect=cap_def["effect"],
            input_schema=cap_def["input_schema"],
            output_schema=cap_def["output_schema"],
            scope=cap_def["scope"],
            preconditions=cap_def["preconditions"],
            postconditions=cap_def["postconditions"],
            implementation=cap_def["implementation"],
            verifier_contract=cap_def["verifier_contract"],
            lifecycle=CapabilityLifecycle.DISCOVERED,
            provenance={"source": "prefabricated_candidate", "site": "trello", "type": "read"},
        )
        reg.register(obj)
        added.append(cap_def["id"])

    # Trello MUTATION capabilities (HELD until Policy authorizes)
    for cap_def in TRELLO_MUTATION_CAPABILITIES:
        previous = reg.get(cap_def["id"])
        if previous:
            continue
        obj = OperationalCapability(
            id=cap_def["id"],
            name=cap_def["name"],
            route=cap_def["route"],
            effect=cap_def["effect"],
            input_schema=cap_def["input_schema"],
            output_schema=cap_def["output_schema"],
            scope=cap_def["scope"],
            preconditions=cap_def["preconditions"],
            postconditions=cap_def["postconditions"],
            implementation=cap_def["implementation"],
            verifier_contract=cap_def["verifier_contract"],
            lifecycle=CapabilityLifecycle.HELD,  # HELD until Policy authorizes
            provenance={"source": "prefabricated_candidate", "site": "trello", "type": "mutation"},
        )
        reg.register(obj)
        added.append(cap_def["id"])

    return added