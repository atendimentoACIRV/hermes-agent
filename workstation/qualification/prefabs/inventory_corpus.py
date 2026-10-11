#!/usr/bin/env python3
"""OPC-01: Inventory sessions and HTML snapshots for prefab capability mining.

Enumerates all sessions (*.json) and HTML snapshots (*.html) recursively,
deduplicates by SHA-256, and produces a sanitized corpus-inventory.json.
No raw session/HTML content is committed.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


SESSIONS_ROOT = Path(r"C:\Github\hermes-agent\workstation\dogfood\dados\Sessões Hermes")
HTML_ROOT = Path(r"C:\Github\hermes-agent\workstation\dogfood\dados\Páginas de sites")
OUTPUT_PATH = Path(r"C:\Github\hermes-agent\workstation\qualification\prefabs\corpus-inventory.json")


@dataclass
class FileEntry:
    hash: str
    file: str
    size_bytes: int
    modified_iso: str
    family: str = ""
    operation_type: str = ""
    tool_sequence: list[str] = None
    result_category: str = "UNCERTAIN"  # VERIFIED/OBSERVED/FAILED/UNCERTAIN/HYPOTHESIS
    frequency: int = 1
    savings_potential: str = ""
    evidence_notes: str = ""
    correlation_status: str = "UNMATCHED"  # MATCHED/HYPOTHESIS/UNMATCHED

    def __post_init__(self):
        if self.tool_sequence is None:
            self.tool_sequence = []


def sha256_file(path: Path) -> str:
    """Compute SHA-256 of file contents."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sanitize_session(session_data: dict) -> dict:
    """Extract only safe metadata from a Hermes session export."""
    if not isinstance(session_data, dict):
        return {}
    
    messages = session_data.get("messages", [])
    tool_counts = Counter()
    browser_tool_calls = 0
    tool_sequence = []
    urls_seen: list[str] = []
    
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        
        # Check tool calls
        for call in msg.get("tool_calls") or []:
            if not isinstance(call, dict):
                continue
            name = (call.get("function") or {}).get("name") or ""
            if name:
                tool_counts[str(name)] += 1
                tool_sequence.append(str(name))
                if str(name).startswith("browser_"):
                    browser_tool_calls += 1
        
        # Check tool results (role=tool messages) for URLs in content
        if msg.get("role") == "tool":
            content = msg.get("content", "")
            if isinstance(content, str):
                # Extract URLs from tool result content
                found_urls = re.findall(r'https?://[^\s<>"\']+', content)
                urls_seen.extend(found_urls)
        
        # Also check assistant messages for URLs in content
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            if isinstance(content, str):
                found_urls = re.findall(r'https?://[^\s<>"\']+', content)
                urls_seen.extend(found_urls)
    
    # Determine primary site family from URLs
    family = "unknown"
    family_scores = Counter()
    for url in urls_seen:
        if "trello.com" in url:
            family_scores["trello"] += 1
        elif "instagram.com" in url:
            family_scores["instagram"] += 1
        elif "web.whatsapp.com" in url or "whatsapp.com" in url:
            family_scores["whatsapp"] += 1
        elif "chatgpt.com" in url or "chat.openai.com" in url:
            family_scores["chatgpt"] += 1
    if family_scores:
        family = family_scores.most_common(1)[0][0]
    
    # Categorize result based on tool patterns
    result_category = "OBSERVED"
    if browser_tool_calls == 0:
        result_category = "UNCERTAIN"
    elif any("error" in str(t).lower() or "failed" in str(t).lower() for t in tool_sequence):
        result_category = "FAILED"
    
    # Calculate savings potential
    savings = "low"
    if browser_tool_calls > 20:
        savings = "high"
    elif browser_tool_calls > 5:
        savings = "medium"
    
    return {
        "session_id": session_data.get("session_id", ""),
        "total_tool_calls": sum(tool_counts.values()),
        "browser_tool_calls": browser_tool_calls,
        "top_tools": dict(tool_counts.most_common(10)),
        "tool_sequence": tool_sequence[:50],  # Limit sequence length
        "family": family,
        "result_category": result_category,
        "savings_potential": savings,
        "urls_sample": urls_seen[:5],
    }


def sanitize_html(html_path: Path) -> dict:
    """Extract only structural fingerprints from HTML, no content."""
    try:
        raw = html_path.read_bytes()
        if len(raw) > 30_000_000:
            return {"error": "file_too_large"}
        
        # Simple tag counting without full parser for speed
        text = raw.decode("utf-8", errors="replace")
        
        # Count data-testid attributes (common in Trello/React apps)
        testids = Counter(re.findall(r'data-testid=["\']([^"\']+)["\']', text))
        
        # Count data-list-id (Trello specific)
        list_ids = set(re.findall(r'data-list-id=["\']([^"\']+)["\']', text))
        
        # Count card links
        card_links = set(re.findall(r'href=["\'](/c/[^"\']+)["\']', text))
        
        # Detect site family
        family = "unknown"
        text_lower = text.lower()
        if "trello.com" in text_lower:
            family = "trello"
        elif "instagram.com" in text_lower:
            family = "instagram"
        elif "web.whatsapp.com" in text_lower or ("whatsapp" in text_lower and "web" in text_lower):
            family = "whatsapp"
        elif "chatgpt.com" in text_lower or "chat.openai.com" in text_lower:
            family = "chatgpt"
        
        return {
            "tags_sample": dict(Counter(re.findall(r"<(\w+)[\s>]", text)).most_common(15)),
            "testids": dict(testids.most_common(35)),
            "list_count": len(list_ids),
            "trello_card_link_count": len(card_links),
            "family": family,
            "size_bytes": len(raw),
        }
    except Exception as e:
        return {"error": str(e)}


def infer_operation_type(tool_sequence: list[str], family: str) -> str:
    """Infer the type of operation from tool sequence."""
    seq_str = " ".join(tool_sequence)
    
    if family == "trello":
        if "browser_navigate" in tool_sequence and "browser_snapshot" in tool_sequence:
            if "browser_click" in tool_sequence:
                return "trello_board_interaction"
            return "trello_navigation"
        if "browser_console" in tool_sequence:
            return "trello_console_extraction"
    elif family == "instagram":
        if "browser_scroll" in tool_sequence:
            return "instagram_scroll_collection"
        return "instagram_navigation"
    elif family == "whatsapp":
        return "whatsapp_conversation"
    elif family == "chatgpt":
        return "chatgpt_interaction"
    
    return "generic_browser"


def main():
    print("Starting OPC-01 corpus inventory...")
    
    # Track seen hashes for deduplication
    seen_session_hashes = set()
    seen_html_hashes = set()
    
    entries: list[FileEntry] = []
    
    # Process sessions
    print(f"Scanning sessions in {SESSIONS_ROOT}")
    session_files = list(SESSIONS_ROOT.rglob("*.json"))
    print(f"Found {len(session_files)} session files")
    
    for session_path in session_files:
        try:
            file_hash = sha256_file(session_path)
            if file_hash in seen_session_hashes:
                print(f"  Duplicate session (SKIP): {session_path.name}")
                continue
            seen_session_hashes.add(file_hash)
            
            raw = session_path.read_bytes()
            session_data = json.loads(raw)
            
            sanitized = sanitize_session(session_data)
            
            stat = session_path.stat()
            entry = FileEntry(
                hash=file_hash,
                file=str(session_path.relative_to(SESSIONS_ROOT)),
                size_bytes=len(raw),
                modified_iso=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                family=sanitized.get("family", "unknown"),
                operation_type=infer_operation_type(sanitized.get("tool_sequence", []), sanitized.get("family", "unknown")),
                tool_sequence=sanitized.get("tool_sequence", []),
                result_category=sanitized.get("result_category", "UNCERTAIN"),
                frequency=1,
                savings_potential=sanitized.get("savings_potential", "low"),
                evidence_notes=f"session_id={sanitized.get('session_id', '')}; browser_calls={sanitized.get('browser_tool_calls', 0)}; top_tools={list(sanitized.get('top_tools', {}).keys())[:5]}; urls={sanitized.get('urls_sample', [])}",
            )
            entries.append(entry)
            print(f"  Session: {session_path.name} -> {entry.family} / {entry.operation_type} / {entry.result_category}")
            
        except Exception as e:
            print(f"  ERROR processing {session_path.name}: {e}")
    
    # Process HTML files
    print(f"\nScanning HTML in {HTML_ROOT}")
    html_files = list(HTML_ROOT.rglob("*.html"))
    print(f"Found {len(html_files)} HTML files")
    
    for html_path in html_files:
        try:
            file_hash = sha256_file(html_path)
            if file_hash in seen_html_hashes:
                print(f"  Duplicate HTML (SKIP): {html_path.name}")
                continue
            seen_html_hashes.add(file_hash)
            
            sanitized = sanitize_html(html_path)
            
            stat = html_path.stat()
            family = sanitized.get("family", "unknown")
            
            entry = FileEntry(
                hash=file_hash,
                file=str(html_path.relative_to(HTML_ROOT)),
                size_bytes=len(html_path.read_bytes()),
                modified_iso=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                family=family,
                operation_type="html_snapshot",
                tool_sequence=[],
                result_category="OBSERVED",
                frequency=1,
                savings_potential="reference",
                evidence_notes=f"size={sanitized.get('size_bytes', 0)}; testids={len(sanitized.get('testids', {}))}; lists={sanitized.get('list_count', 0)}; cards={sanitized.get('trello_card_link_count', 0)}",
                correlation_status="HYPOTHESIS",  # HTML alone can't verify session correlation
            )
            entries.append(entry)
            print(f"  HTML: {html_path.name} -> {entry.family} / {entry.evidence_notes}")
            
        except Exception as e:
            print(f"  ERROR processing {html_path.name}: {e}")
    
    # Correlate sessions with HTML by family
    print("\nCorrelating sessions with HTML snapshots...")
    html_by_family = {}
    for e in entries:
        if e.operation_type == "html_snapshot":
            html_by_family.setdefault(e.family, []).append(e)
    
    for entry in entries:
        if entry.operation_type != "html_snapshot" and entry.family in html_by_family:
            entry.correlation_status = "HYPOTHESIS"
            entry.evidence_notes += f"; correlated_html_count={len(html_by_family[entry.family])}"
    
    # Count frequencies by family+operation
    freq_counter = Counter((e.family, e.operation_type) for e in entries if e.operation_type != "html_snapshot")
    for entry in entries:
        if entry.operation_type != "html_snapshot":
            entry.frequency = freq_counter[(entry.family, entry.operation_type)]
    
    # Write output
    output = {
        "generated_at": datetime.now().isoformat(),
        "sessions_root": str(SESSIONS_ROOT),
        "html_root": str(HTML_ROOT),
        "total_entries": len(entries),
        "unique_sessions": len(seen_session_hashes),
        "unique_html": len(seen_html_hashes),
        "entries": [asdict(e) for e in entries],
    }
    
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nInventory written to {OUTPUT_PATH}")
    print(f"Total entries: {len(entries)}")
    print(f"Unique sessions: {len(seen_session_hashes)}")
    print(f"Unique HTML: {len(seen_html_hashes)}")
    
    # Summary by family
    family_summary = Counter(e.family for e in entries)
    print("\nFamily summary:")
    for fam, count in family_summary.most_common():
        print(f"  {fam}: {count}")


if __name__ == "__main__":
    main()