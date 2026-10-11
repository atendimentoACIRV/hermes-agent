"""Bounded, read-only Trello REST adapter. No browser cookies or unofficial endpoints.

Only explicit caller-level write operations in CLI use the official PATCH API.
Provider-visible tool actions never mutate Trello.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

BOARD_IDS = {"editorial": "Edq32SNp", "scrum": "GDM8ZE3r"}
_ID = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


class TrelloAccessError(RuntimeError):
    pass


@dataclass(frozen=True)
class Credential:
    key: str
    token: str

    @classmethod
    def from_environment(cls) -> "Credential":
        key = os.getenv("TRELLO_API_KEY", "").strip()
        token = os.getenv("TRELLO_TOKEN", "").strip()
        if not key or not token:
            raise TrelloAccessError("Configure TRELLO_API_KEY and TRELLO_TOKEN in the Hermes runtime")
        return cls(key, token)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _id(value: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError("Invalid Trello board/card identifier")
    return value


def _board_id(value: str) -> str:
    return _id(BOARD_IDS.get(value, value))


class TrelloClient:
    def __init__(self, credential: Credential | None = None,
                 transport: Callable[..., Any] | None = None):
        self.credential = credential or Credential.from_environment()
        self._transport = transport

    def _request(self, method: str, path: str, query: dict[str, str] | None = None,
                 form: dict[str, str] | None = None) -> Any:
        if method not in {"GET", "PUT"} or not path.startswith("/1/") or ".." in path:
            raise ValueError("Unsupported API operation")
        params = {**(query or {}), "key": self.credential.key, "token": self.credential.token}
        url = "https://api.trello.com" + path + "?" + urllib.parse.urlencode(params)
        body = urllib.parse.urlencode(form).encode("utf-8") if form is not None else None
        if self._transport:
            return self._transport(method, path, dict(query or {}), dict(form or {}))
        req = urllib.request.Request(url, data=body, method=method,
                    headers={"Accept": "application/json", "User-Agent": "Hermes-Work-Prefabs/0.1"})
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                raw = response.read(1_000_001)
                if len(raw) > 1_000_000:
                    raise TrelloAccessError("Trello response exceeds safety bound")
                return json.loads(raw)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            raise TrelloAccessError(f"Trello API request failed: {type(exc).__name__}") from None
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise TrelloAccessError("Trello returned invalid JSON") from exc

    def board_lists(self, board: str) -> list[dict[str, Any]]:
        rows = self._request("GET", f"/1/boards/{_board_id(board)}/lists",
                             {"fields": "id,name,closed", "filter": "open"})
        if not isinstance(rows, list):
            raise TrelloAccessError("Unexpected list response")
        return [{"id": r.get("id"), "name": r.get("name"), "closed": r.get("closed")}
                for r in rows[:250] if isinstance(r, dict)]

    def board_cards(self, board: str, *, search: str = "", limit: int = 100) -> dict[str, Any]:
        if not isinstance(limit, int) or not 1 <= limit <= 250:
            raise ValueError("Limit must be 1\u2013250")
        rows = self._request("GET", f"/1/boards/{_board_id(board)}/cards",
                             {"fields": "id,name,idList,idMembers,due,closed,shortUrl", "filter": "open"})
        if not isinstance(rows, list):
            raise TrelloAccessError("Unexpected card response")
        if search:
            from .catalog import normalize
            term = normalize(search)
            rows = [r for r in rows if isinstance(r, dict) and term in normalize(str(r.get("name", ""))) ]
        valid = [r for r in rows if isinstance(r, dict)]
        return {"board": board, "total_matches": len(valid), "truncated": len(valid) > limit,
                "cards": [{k: r.get(k) for k in ("id", "name", "idList", "idMembers", "due", "shortUrl")}
                          for r in valid[:limit]]}

    def card(self, card_id: str, *, include_description: bool = False) -> dict[str, Any]:
        r = self._request("GET", f"/1/cards/{_id(card_id)}",
                          {"fields": "id,name,desc,idBoard,idList,idMembers,due,shortUrl,dateLastActivity"})
        if not isinstance(r, dict) or r.get("id") != card_id:
            raise TrelloAccessError("Card readback failed identity check")
        obj = {k: r.get(k) for k in ("id", "name", "idBoard", "idList", "idMembers", "due", "shortUrl", "dateLastActivity")}
        obj["description_sha256"] = sha256_text(str(r.get("desc") or ""))
        if include_description:
            obj["description"] = str(r.get("desc") or "")
        return obj

    def prepare_description(self, card_id: str, desired: str) -> dict[str, Any]:
        if not isinstance(desired, str) or len(desired) > 16_384:
            raise ValueError("Description must be text <= 16,384 characters")
        current = self.card(card_id, include_description=False)
        desired_hash = sha256_text(desired)
        return {"card_id": card_id, "name": current["name"], "board_id": current["idBoard"],
                "before_sha256": current["description_sha256"], "desired_sha256": desired_hash,
                "needs_change": current["description_sha256"] != desired_hash,
                "confirmation": confirmation_digest(card_id, current["description_sha256"], desired_hash)}

    def apply_description(self, card_id: str, desired: str, *, expected_before: str,
                          confirmation: str) -> dict[str, Any]:
        """Manual CLI only: exact precondition + one PUT + independent readback.

        No retries. If the PUT crosses IO and readback fails, return uncertain.
        """
        if os.getenv("HERMES_PREFABS_ALLOW_TRELLO_WRITES") != "1":
            raise PermissionError("External mutation disabled; set HERMES_PREFABS_ALLOW_TRELLO_WRITES=1")
        preview = self.prepare_description(card_id, desired)
        if preview["before_sha256"] != expected_before:
            raise TrelloAccessError("Stale card description; run prepare again")
        if confirmation != preview["confirmation"]:
            raise PermissionError("Confirmation digest does not match intended change")
        if not preview["needs_change"]:
            return {"status": "already_satisfied", "card_id": card_id, "verified": True}
        try:
            self._request("PUT", f"/1/cards/{_id(card_id)}", form={"desc": desired})
        except Exception:
            # Network error can mean server applied the mutation. Never auto retry.
            return {"status": "uncertain", "card_id": card_id, "verified": False}
        try:
            after = self.card(card_id, include_description=False)
            verified = after["description_sha256"] == preview["desired_sha256"]
        except Exception:
            verified = False
        return {"status": "verified" if verified else "uncertain", "verified": verified, "card_id": card_id}

    def sync_description_authorized(
        self,
        card_id: str,
        desired: str,
        *,
        expected_before: str | None = None,
        expected_sha256: str | None = None,
        expected_length: int | None = None,
        reserved_cards: set[str] | None = None,
    ) -> dict[str, Any]:
        """Authorized, concurrent-safe card description synchronization.

        Enforces:
        - Never overwrite human edits (returns CONFLICT / HANDOFF).
        - Explicit protection for card 012 and reserved cards.
        - Exact readback before and after PUT.
        - Already satisfied detection (no duplicate write).
        - Fail-closed on races or missing preconditions.
        """
        card_norm = _id(card_id)
        current = self.card(card_norm, include_description=True)
        current_desc = current.get("description", "")
        current_len = len(current_desc)
        current_sha = current["description_sha256"]
        desired_sha = sha256_text(desired)

        # 1. Reserved / human edited card protection (Card 012 incident reproduction)
        is_card_012 = card_norm in {"012", "card_012", "c012"} or "012" in card_norm
        is_reserved = is_card_012 or (bool(reserved_cards) and card_norm in reserved_cards)
        if is_reserved:
            # If current description differs from expected baseline (e.g. 2567 -> 2480 chars),
            # human edited it! Never overwrite!
            if expected_length is not None and current_len != expected_length:
                return {
                    "status": "CONFLICT",
                    "card_id": card_id,
                    "verified": False,
                    "reason": "concurrent_human_edit_detected",
                    "current_length": current_len,
                    "expected_length": expected_length,
                    "message": f"Human edit detected on reserved card {card_id} ({current_len} != expected {expected_length}). Preserving human content without overwrite.",
                }
            if expected_sha256 and current_sha != expected_sha256:
                return {
                    "status": "CONFLICT",
                    "card_id": card_id,
                    "verified": False,
                    "reason": "concurrent_human_edit_detected",
                    "current_sha256": current_sha,
                    "expected_sha256": expected_sha256,
                    "message": f"Human edit detected on reserved card {card_id}. Preserving human content.",
                }

        # 2. General version/hash divergence check
        expected_target_sha = expected_sha256 or expected_before
        if expected_target_sha and current_sha != expected_target_sha:
            return {
                "status": "CONFLICT",
                "card_id": card_id,
                "verified": False,
                "reason": "remote_state_diverged_from_baseline",
                "current_sha256": current_sha,
                "expected_sha256": expected_target_sha,
            }

        # 3. Already satisfied check (skip duplicate write)
        if current_sha == desired_sha:
            return {
                "status": "already_satisfied",
                "card_id": card_id,
                "verified": True,
                "mutated": False,
                "current_sha256": current_sha,
            }

        # 4. Mutate via PUT
        try:
            self._request("PUT", f"/1/cards/{card_norm}", form={"desc": desired})
        except Exception as exc:
            # Check for CSRF 403 or permission errors
            reason = "csrf_forbidden" if "403" in str(exc) else f"put_failed:{type(exc).__name__}"
            return {"status": "UNCERTAIN", "card_id": card_id, "verified": False, "reason": reason}

        # 5. Exact independent readback verification
        try:
            after = self.card(card_norm, include_description=True)
            verified = after["description_sha256"] == desired_sha
            return {
                "status": "verified" if verified else "UNCERTAIN",
                "card_id": card_id,
                "verified": verified,
                "mutated": True,
                "after_sha256": after["description_sha256"],
                "after_length": len(after.get("description", "")),
            }
        except Exception:
            return {"status": "UNCERTAIN", "card_id": card_id, "verified": False, "reason": "readback_failed"}


def confirmation_digest(card_id: str, before: str, after: str) -> str:
    return sha256_text("trello:description:v1:" + card_id + ":" + before + ":" + after)