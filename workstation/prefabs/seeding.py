"""Optionally register audited candidates in the EXISTING capability registry.

'Prefabricated' is a source label, not a forged VERIFIED or PROMOTED status.
"""
from __future__ import annotations

from .catalog import DESTINATIONS


def seed_discovered(registry=None) -> list[str]:
    from workstation.operational_capabilities import (
        CapabilityLifecycle, OperationalCapability, OperationalCapabilityRegistry)
    reg = registry or OperationalCapabilityRegistry()
    added: list[str] = []
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
    return added