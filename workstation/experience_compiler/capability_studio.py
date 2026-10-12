"""Human-facing projection and inert draft revisions of learned capabilities.

This module deliberately has NO dispatch, promotion, or storage entry point.
Only OperationalCapabilityRegistry and the existing verifier/policy owners may
later admit a newly reviewed candidate.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from workstation.operational_capabilities import (
    CapabilityLifecycle,
    OperationalCapability,
)

_UNSUPPORTED_GRAPH_FIELDS = frozenset({
    "loop",
    "while",
    "foreach",
    "branch",
    "branches",
    "trigger",
    "expression",
    "script",
    "code",
    "on_error",
    "conditions",
    "subflow",
})
_SENSITIVE_KEYS = (
    "token",
    "secret",
    "password",
    "credential",
    "authorization",
    "api_key",
    "cookie",
)


def _steps(cap: OperationalCapability) -> list[dict[str, Any]]:
    steps = (
        cap.implementation.get("steps", [])
        if isinstance(cap.implementation, dict)
        else []
    )
    if not isinstance(steps, list):
        raise ValueError("capability_steps_not_a_list")
    if any(not isinstance(step, dict) for step in steps):
        raise ValueError("capability_step_not_object")
    return steps


def _revision_editable(cap: OperationalCapability) -> list[dict[str, Any]]:
    steps = _steps(cap)
    seen: set[str] = set()
    for step in steps:
        if any(k in step for k in _UNSUPPORTED_GRAPH_FIELDS):
            raise ValueError("unsupported_control_flow")
        name = str(step.get("id") or "")
        if not name or name in seen:
            raise ValueError("steps_need_unique_ids")
        seen.add(name)
        if not isinstance(step.get("args", {}), dict):
            raise ValueError("step_arguments_must_be_objects")
    return steps


def project_capability(cap: OperationalCapability) -> dict[str, Any]:
    """Lossless topology for linear steps; show unsupported semantics as read-only."""
    steps = _steps(cap)
    nodes: list[dict[str, Any]] = []
    for i, step in enumerate(steps):
        fields = step.get("args", {})
        nodes.append({
            "id": str(step.get("id") or f"step-{i}"),
            "kind": "operation",
            "primitive": str(step.get("primitive") or step.get("tool") or "unknown"),
            "argument_names": [
                key
                for key in fields
                if not any(s in str(key).lower() for s in _SENSITIVE_KEYS)
            ]
            if isinstance(fields, dict)
            else [],
            "editable": not any(k in step for k in _UNSUPPORTED_GRAPH_FIELDS),
        })
    edges = [
        {"source": nodes[i]["id"], "target": nodes[i + 1]["id"]}
        for i in range(len(nodes) - 1)
    ]
    return {
        "id": cap.id,
        "name": cap.name,
        "version": cap.version,
        "lifecycle": cap.lifecycle.value,
        "route": cap.route,
        "effect": cap.effect,
        "drift_state": cap.drift_state,
        "preconditions": list(cap.preconditions),
        "postconditions": list(cap.postconditions),
        "verifier_present": bool(cap.verifier_contract),
        "nodes": nodes,
        "edges": edges,
        "editable": bool(nodes) and all(node["editable"] for node in nodes),
        "requires_revalidation": cap.lifecycle != CapabilityLifecycle.PROMOTED,
    }


def draft_revision(
    cap: OperationalCapability,
    *,
    step_arguments: Mapping[str, Mapping[str, Any]] | None = None,
    preconditions: Sequence[str] | None = None,
    postconditions: Sequence[str] | None = None,
) -> OperationalCapability:
    """Return an unregistered new version; changes never inherit promotion proofs."""
    steps = _revision_editable(cap)
    patches = step_arguments or {}
    by_id = {str(step["id"]): step for step in steps}
    for step_id, args in patches.items():
        if step_id not in by_id:
            raise ValueError("unknown_step_id")
        if not isinstance(args, Mapping):
            raise ValueError("invalid_step_patch")
        existing = by_id[step_id].get("args", {})
        if any(
            k not in existing or any(word in str(k).lower() for word in _SENSITIVE_KEYS)
            for k in args
        ):
            raise ValueError("undeclared_or_sensitive_argument")
        if any(
            not isinstance(v, (str, int, float, bool, type(None)))
            for v in args.values()
        ):
            raise ValueError("only_json_scalar_arguments_supported")
    for conditions in (preconditions, postconditions):
        if conditions is not None and (
            isinstance(conditions, (str, bytes))
            or not all(
                isinstance(item, str) and 0 < len(item) <= 512 for item in conditions
            )
        ):
            raise ValueError("invalid_conditions")
    try:
        major, minor, patch = [int(p) for p in cap.version.split(".")]
    except (ValueError, TypeError) as exc:
        raise ValueError("revision_requires_semantic_version") from exc

    revision = deepcopy(cap)
    revision.version = f"{major}.{minor}.{patch + 1}"
    for step in _steps(revision):
        step["args"].update(patches.get(str(step["id"]), {}))
    if preconditions is not None:
        revision.preconditions = list(preconditions)
    if postconditions is not None:
        revision.postconditions = list(postconditions)

    revision.lifecycle = CapabilityLifecycle.DISCOVERED
    revision.semantic_fingerprint = ""
    revision.compatibility_fingerprint = ""
    revision.verifier_contract = {}
    revision.validation_evidence = []
    revision.success_count = 0
    revision.failure_count = 0
    revision.causal_grade = 0
    revision.promotion_policy_version = ""
    revision.drift_state = "healthy"
    revision.savings = {}
    revision.source_trace_refs = []
    revision.formal_contract = None
    revision.provenance = {
        "source": "human_draft_revision",
        "parent_capability": f"{cap.id}@{cap.version}",
        "requires_independent_validation": True,
    }
    revision.learning_metadata = {"requires_independent_validation": True}
    return revision


def compose_preview(
    capabilities: Sequence[OperationalCapability],
    *,
    links: Sequence[tuple[str, str]],
) -> dict[str, Any]:
    """Project a DAG for human review. NOT a runnable composite capability."""
    nodes = [
        {"id": c.id, "name": c.name, "lifecycle": c.lifecycle.value}
        for c in capabilities
    ]
    ids = {n["id"] for n in nodes}
    if len(ids) != len(nodes):
        raise ValueError("duplicate_capability_id")
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in ids}
    indegree = {node_id: 0 for node_id in ids}
    edges = []
    for a, b in links:
        if a not in ids or b not in ids or (b in adjacency[a]):
            raise ValueError("invalid_composition_link")
        adjacency[a].append(b)
        indegree[b] += 1
        edges.append({"source": a, "target": b})
    ready = [k for k, deg in indegree.items() if deg == 0]
    visited = 0
    while ready:
        current = ready.pop()
        visited += 1
        for neighbor in adjacency[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                ready.append(neighbor)
    if visited != len(nodes):
        raise ValueError("composition_cycle")
    return {
        "nodes": nodes,
        "edges": edges,
        "runnable": False,
        "requires_validation": True,
    }
