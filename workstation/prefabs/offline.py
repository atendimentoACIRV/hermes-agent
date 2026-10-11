"""Offline, no-network, no-JS inspection of supplied saved HTMLs and Hermes logs."""
from __future__ import annotations

import collections
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


class _AuditHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.counts: collections.Counter = collections.Counter()
        self.testids: collections.Counter = collections.Counter()
        self.list_ids: set[str] = set()
        self.card_links: set[str] = set()
        self.input_labels: set[str] = set()
        self._max_elements = 750_000
        self._seen = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._seen += 1
        if self._seen > self._max_elements:
            raise ValueError("HTML element count exceeds safety limit")
        self.counts[tag] += 1
        a = dict(attrs)
        if a.get("data-testid"):
            self.testids[str(a["data-testid"])] += 1
        if a.get("data-list-id"):
            self.list_ids.add(str(a["data-list-id"]))
        href = a.get("href") or ""
        if href.startswith("/c/") and len(href) < 300:
            self.card_links.add(href)
        aria = a.get("aria-label") or ""
        if aria and len(aria) < 100 and len(self.input_labels) < 100:
            self.input_labels.add(aria)


def html_fingerprint(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file() or p.stat().st_size > 30_000_000:
        raise ValueError("HTML file missing or larger than 30 MB")
    raw = p.read_bytes()
    parser = _AuditHTMLParser()
    parser.feed(raw.decode("utf-8", errors="replace"))
    # Never persist raw HTML, cookies, embedded tokens or page contents.
    return {"file": p.name, "sha256": hashlib.sha256(raw).hexdigest(),
            "size_bytes": len(raw), "tags": dict(parser.counts.most_common(15)),
            "testids": dict(parser.testids.most_common(35)),
            "list_count": len(parser.list_ids), "trello_card_link_count": len(parser.card_links),
            "form_control_labels_sample": sorted(parser.input_labels)[:25]}


def session_fingerprint(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file() or p.stat().st_size > 30_000_000:
        raise ValueError("Session missing or exceeds 30 MB")
    raw = p.read_bytes()
    body = json.loads(raw)
    if not isinstance(body, dict) or not isinstance(body.get("messages"), list):
        raise ValueError("Not a Hermes session export")
    tool_counts: collections.Counter = collections.Counter()
    calls = 0
    for m in body["messages"]:
        if not isinstance(m, dict):
            continue
        for call in m.get("tool_calls") or []:
            if not isinstance(call, dict):
                continue
            name = (call.get("function") or {}).get("name") or ""
            if name:
                tool_counts[str(name)] += 1
                calls += 1
    # No prompts, messages, browser results or internal reasoning in report.
    return {"file": p.name, "sha256": hashlib.sha256(raw).hexdigest(),
            "session_id": body.get("session_id"), "tool_calls": calls,
            "browser_tool_calls": sum(n for k,n in tool_counts.items() if k.startswith("browser_")),
            "top_tools": dict(tool_counts.most_common(12))}