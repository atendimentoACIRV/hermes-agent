"""Provider-free navigator. Invoked only through the OWNER's scoped dispatcher."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import urlsplit

from .catalog import Destination, same_destination


@dataclass(frozen=True)
class NavigationReceipt:
    status: str  # verified | uncertain | refused
    destination: str
    expected_host: str
    observed_url: str = ""
    reason: str = ""
    dispatch_attempted: bool = False

    def safe_dict(self) -> dict:
        return {"status": self.status, "destination": self.destination,
                "expected_host": self.expected_host, "observed_url": self.observed_url,
                "reason": self.reason, "dispatch_attempted": self.dispatch_attempted}


def _as_data(raw: Any) -> Any:
    if isinstance(raw, (dict, list)):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return {"text": raw[:1000]}
    return {}


def _has_error(raw: Any) -> bool:
    d = _as_data(raw)
    if isinstance(d, dict):
        if d.get("is_error") is True or d.get("isError") is True or d.get("success") is False:
            return True
        if d.get("error") or str(d.get("status", "")).lower() in ("error", "failed", "denied", "blocked"):
            return True
    return False


def _extract_known_url(raw: Any) -> str:
    """Only explicit URL fields, never arbitrary text, tool debug, or HTML links."""
    d = _as_data(raw)
    if isinstance(d, dict) and "text" in d and isinstance(d["text"], str):
        # Hermes can wrap native JSON in <untrusted_tool_result>. Parse only
        # the controller-owned metadata before the snapshot/page-text field,
        # never a URL mentioned inside user-controlled page content.
        text = d["text"]
        head = text.split('"snapshot":', 1)[0][:2000]
        if '"snapshot":' in text and '"tab_id":' in head:
            match = re.search(r'"url"\s*:\s*"(https://[^"\\\s]+)"', head)
            if match:
                return match.group(1)
    if isinstance(d, dict):
        for key in ("url", "current_url", "currentUrl", "page_url", "pageUrl", "final_url", "finalUrl"):
            value = d.get(key)
            if isinstance(value, str) and value.startswith("https://"):
                return value
        for key in ("page", "browser", "metadata", "result", "data"):
            v = d.get(key)
            if isinstance(v, dict):
                found = _extract_known_url(v)
                if found:
                    return found
    return ""


def navigate(destination: Destination, dispatch: Callable[[str, dict], Any], *,
             independent_read: Callable[[], Any] | None = None) -> NavigationReceipt:
    """Navigate once; success requires an independent state observation.

    Do NOT treat an acknowledgement from browser_navigate as proof of success.
    Caller owns authoritative TaskRun, guardrails, effects and journaling.
    """
    expected_host = urlsplit(destination.url).hostname or ""
    attempted = False
    try:
        attempted = True
        ack = dispatch("browser_navigate", {"url": destination.url})
        if _has_error(ack):
            return NavigationReceipt("uncertain", destination.key, expected_host,
                                     reason="browser_navigation_returned_error", dispatch_attempted=True)
        # A separate browser_snapshot is needed, never verifying the same acknowledgement.
        observation = independent_read() if independent_read else dispatch("browser_snapshot", {"full": False})
        if _has_error(observation):
            return NavigationReceipt("uncertain", destination.key, expected_host,
                                     reason="browser_state_unavailable", dispatch_attempted=True)
        observed = _extract_known_url(observation)
        if observed and same_destination(observed, destination.url):
            return NavigationReceipt("verified", destination.key, expected_host,
                                     observed_url=observed, dispatch_attempted=True)
        return NavigationReceipt("uncertain", destination.key, expected_host,
                                 reason="browser_url_unverified_or_drifted", dispatch_attempted=True)
    except Exception as exc:
        return NavigationReceipt("uncertain" if attempted else "refused", destination.key, expected_host,
                                 reason=f"dispatch_failure:{type(exc).__name__}", dispatch_attempted=attempted)