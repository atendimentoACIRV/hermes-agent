"""Typed fail-closed HyperFrames variable overrides from immutable native source.

This module validates a declared parameter payload. It does not mutate HTML,
launch a renderer, authorize a TaskRun, or publish a CreativeDocument revision.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
import math
import re
from typing import Mapping, Any


class HyperframesVariableError(ValueError):
    """A rendered variable request violates the source declaration."""


_ID = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_.-]{0,63}$")
_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


class _DeclarationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "html":
            return
        for name, value in attrs:
            if name.lower() == "data-composition-variables" and value is not None:
                self.values.append(value)


def _validate_type(kind: str, value: Any) -> bool:
    if kind == "string":
        return isinstance(value, str) and len(value) <= 1024
    if kind == "color":
        return isinstance(value, str) and bool(_COLOR.fullmatch(value))
    if kind == "number":
        return type(value) in {int, float} and math.isfinite(value)
    if kind == "boolean":
        return type(value) is bool
    return False


def validated_hyperframes_overrides(source_html: bytes, updates: Mapping[str, Any]) -> bytes:
    """Return strict canonical JSON for HyperFrames --variables-file.

    The native HTML is parsed but never edited. The caller must execute its
    renderer via an authorized process supervisor and persist immutable
    source bytes and the returned JSON under the Hermes canonical revision.
    """
    if not isinstance(source_html, bytes) or len(source_html) > 262_144:
        raise HyperframesVariableError("Invalid source HTML size")
    if not isinstance(updates, Mapping) or len(updates) > 64:
        raise HyperframesVariableError("Invalid variable overrides")
    try:
        html = source_html.decode("utf-8", "strict")
        parser = _DeclarationParser()
        parser.feed(html)
        if len(parser.values) != 1:
            raise HyperframesVariableError("missing or duplicate variable declarations")
        declarations = json.loads(parser.values[0])
    except (UnicodeError, ValueError, TypeError) as exc:
        if isinstance(exc, HyperframesVariableError):
            raise
        raise HyperframesVariableError("Invalid HyperFrames declaration JSON") from exc
    if not isinstance(declarations, list) or len(declarations) > 64:
        raise HyperframesVariableError("Invalid declared variable list")
    kinds: dict[str, str] = {}
    for item in declarations:
        if not isinstance(item, dict):
            raise HyperframesVariableError("Invalid variable declaration entry")
        key, kind = item.get("id"), item.get("type")
        if not isinstance(key, str) or not _ID.fullmatch(key) or not isinstance(kind, str):
            raise HyperframesVariableError("Invalid variable ID or type")
        if key in kinds:
            raise HyperframesVariableError("duplicate variable declaration")
        if kind not in {"string", "color", "number", "boolean"}:
            raise HyperframesVariableError("Unsupported variable type")
        if "default" in item and not _validate_type(kind, item["default"]):
            raise HyperframesVariableError("Invalid default variable type")
        kinds[key] = kind
    for key, value in updates.items():
        if not isinstance(key, str) or key not in kinds:
            raise HyperframesVariableError(f"undeclared HyperFrames variable: {key}")
        if not _validate_type(kinds[key], value):
            raise HyperframesVariableError(f"Invalid {kinds[key]} value for {key}")
    try:
        encoded = json.dumps(dict(updates), ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError) as exc:
        raise HyperframesVariableError("Invalid variable JSON payload") from exc
    if len(encoded) > 8192:
        raise HyperframesVariableError("Variable payload exceeds safe bound")
    return encoded
