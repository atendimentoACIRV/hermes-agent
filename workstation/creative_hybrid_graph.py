"""Validated source dependency graph, declared bindings, and cache fingerprints.

Pure control-plane helpers. No script evaluation, secondary project database,
or claims that this module itself executes EffectCraft/HyperFrames renderers.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class HybridGraphError(ValueError):
    """Invalid hybrid source graph, binding or render fingerprint."""


_ID = re.compile(r"^[a-f0-9]{32}$")
_SHA = re.compile(r"^[a-f0-9]{64}$")
_PATH = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-/]*$")


def plan_hybrid_dependencies(
    composition_ids: list[str], dependencies: list[tuple[str, str]], *, max_depth: int = 32
) -> list[str]:
    """Topological order: a (parent, child) edge renders child before parent."""
    if len(set(composition_ids)) != len(composition_ids):
        raise HybridGraphError("Duplicate hybrid composition")
    if not composition_ids or len(composition_ids) > 256 or max_depth < 1:
        raise HybridGraphError("Invalid hybrid graph size")
    if any(not isinstance(value, str) or not _ID.fullmatch(value) for value in composition_ids):
        raise HybridGraphError("Invalid composition identifier")
    source_ids = set(composition_ids)
    graph: dict[str, set[str]] = {comp: set() for comp in composition_ids}
    for parent, child in dependencies:
        if parent not in source_ids or child not in source_ids:
            raise HybridGraphError("Dependency references unknown composition")
        graph[parent].add(child)
    visiting: set[str] = set()
    complete: set[str] = set()
    order: list[str] = []

    def visit(node: str, depth: int) -> None:
        if node in visiting:
            raise HybridGraphError("Hybrid dependency cycle")
        if depth > max_depth:
            raise HybridGraphError("Hybrid dependency graph exceeds maximum depth")
        if node in complete:
            return
        visiting.add(node)
        for child in sorted(graph[node]):
            visit(child, depth + 1)
        visiting.remove(node)
        complete.add(node)
        order.append(node)

    for node in sorted(composition_ids):
        visit(node, 1)
    return order


def validate_hybrid_bindings(
    composition_ids: set[str], parameters: dict[str, dict[str, Any]],
    bindings: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Validate declared typed external targets; never infer from arbitrary JS."""
    if not isinstance(parameters, dict) or not isinstance(bindings, list):
        raise HybridGraphError("Invalid parameter/binding declarations")
    allowed_types = {"string", "number", "boolean", "color"}
    for name, definition in parameters.items():
        if not isinstance(name, str) or not _PATH.fullmatch(name):
            raise HybridGraphError("Invalid parameter name")
        if not isinstance(definition, dict) or definition.get("type") not in allowed_types:
            raise HybridGraphError("Invalid parameter type")
        value = definition.get("value")
        kind = definition["type"]
        if (kind in {"string", "color"} and not isinstance(value, str)) or (
            kind == "boolean" and type(value) is not bool
        ) or (kind == "number" and (type(value) not in {int, float} or not -1e12 <= value <= 1e12)):
            raise HybridGraphError("Invalid parameter value")
    seen: set[tuple[str, str, str]] = set()
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {"parameter", "composition_id", "property_path"}:
            raise HybridGraphError("Invalid hybrid binding")
        name = binding["parameter"]
        cid = binding["composition_id"]
        path = binding["property_path"]
        if name not in parameters or cid not in composition_ids:
            raise HybridGraphError("Binding references unknown parameter or composition")
        if not isinstance(path, str) or not _PATH.fullmatch(path):
            raise HybridGraphError("Invalid bound property path")
        key = name, cid, path
        if key in seen:
            raise HybridGraphError("Duplicate bound property")
        seen.add(key)
    return bindings


def hybrid_render_key(
    composition_sources: dict[str, str], parameters: dict[str, Any],
    frame_index: int, engine_version: str, *, width: int, height: int, fps: tuple[int, int],
    asset_hashes: dict[str, str] | None = None, color_profile: str = "srgb",
) -> str:
    """Stable content signature for a single frame, NOT proof of pixel parity.

    Callers must include every transitive asset/version/profile input in the source
    digest or invalidate the cache conservatively. Never cache by pathname alone.
    """
    if not composition_sources or any(
        not isinstance(k, str) or not _ID.fullmatch(k) or not isinstance(v, str) or not _SHA.fullmatch(v)
        for k, v in composition_sources.items()
    ):
        raise HybridGraphError("Invalid input composition source digest")
    if (type(frame_index) is not int or frame_index < 0 or type(width) is not int or width <= 0
            or type(height) is not int or height <= 0
            or len(fps) != 2 or any(type(part) is not int or part <= 0 for part in fps)
            or not isinstance(engine_version, str) or not engine_version.strip()):
        raise HybridGraphError("Invalid render frame specification")
    asset_hashes = asset_hashes or {}
    if (not isinstance(asset_hashes, dict)
            or any(not isinstance(k, str) or not k or not isinstance(v, str)
                   or not _SHA.fullmatch(v) for k, v in asset_hashes.items())
            or not isinstance(color_profile, str) or not color_profile):
        raise HybridGraphError("Invalid asset fingerprints or color profile")
    payload = {
        "sources": composition_sources, "assets": asset_hashes,
        "parameters": parameters, "frame": frame_index,
        "engine_version": engine_version, "width": width, "height": height, "fps": fps,
        "color_profile": color_profile,
    }
    try:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError) as exc:
        raise HybridGraphError("Invalid render parameters") from exc
    return hashlib.sha256(encoded).hexdigest()
