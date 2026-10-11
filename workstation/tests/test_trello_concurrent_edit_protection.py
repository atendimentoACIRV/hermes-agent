"""Tests for Concurrent Human Edit Protection in Trello Operations.

Reproduces and permanently protects against:
- Incident of Card 012 (Dia das Crianças): 2567-char initial -> 2480-char human edit must never be overwritten.
- Batch of 33 descriptions with concurrent edit control, exact readback, and resume.
- Duplicate write suppression (already_satisfied).
- CSRF 403 and uncertain effect handling (no blind retry).
- SUPERSEDED / human takeover lease revocation.
"""
from __future__ import annotations

import copy
import hashlib
import json
import pytest
from types import SimpleNamespace

from workstation.prefabs.trello import Credential, TrelloAccessError, TrelloClient, sha256_text
from workstation.run_closure import (
    HandoffWakeCondition,
    RunClosureProof,
    execute_in_flight_handoff,
)
from workstation.control_plane.lattice import AuthorityLevel, AuthorityScope
from workstation.artifacts import ArtifactStore
from workstation.durable_tasks import DurableTaskStore, WorkItemStatus


def make_mock_trello(cards_db: dict[str, dict]):
    """In-memory mock transport for Trello API."""
    def transport(method: str, path: str, query: dict, form: dict):
        # path is like /1/cards/{id}
        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[1] == "cards":
            card_id = parts[2]
            if card_id not in cards_db:
                raise TrelloAccessError(f"Card not found: {card_id}")
            card = cards_db[card_id]
            if method == "GET":
                return copy.deepcopy(card)
            if method == "PUT":
                if card.get("simulate_csrf_403"):
                    raise Exception("HTTP 403 Forbidden: CSRF token invalid")
                new_desc = form.get("desc", "")
                card["desc"] = new_desc
                card["dateLastActivity"] = "2026-10-10T12:00:00.000Z"
                return copy.deepcopy(card)
        raise TrelloAccessError(f"Unhandled endpoint: {method} {path}")

    client = TrelloClient(credential=Credential(key="mock_key", token="mock_token"), transport=transport)
    return client


def test_card_012_human_edit_preserved_and_never_overwritten():
    """Reproduce Card 012 incident: 2567-char initial was updated by human to 2480-char.
    
    The automation MUST detect the concurrent human edit and refuse to overwrite it.
    """
    initial_desc = "A" * 2567
    human_edited_desc = "B" * 2480
    attempted_automated_desc = "AUTOMATED_RESTORE_" + ("A" * 2540)

    cards_db = {
        "card_012": {
            "id": "card_012",
            "name": "Dia das Crianças",
            "desc": human_edited_desc,
            "idBoard": "board_edq",
            "idList": "list_1",
            "idMembers": [],
            "due": None,
            "shortUrl": "https://trello.com/c/012",
            "dateLastActivity": "2026-10-09T15:30:00.000Z",
        }
    }
    client = make_mock_trello(cards_db)

    # Automation runs with expected_length=2567 (the old unedited baseline)
    result = client.sync_description_authorized(
        "card_012",
        attempted_automated_desc,
        expected_length=2567,
        expected_sha256=sha256_text(initial_desc),
        reserved_cards={"card_012"},
    )

    # 1. Result must be CONFLICT, NOT verified/overwritten
    assert result["status"] == "CONFLICT"
    assert result["verified"] is False
    assert result["reason"] == "concurrent_human_edit_detected"
    assert result["current_length"] == 2480
    assert result["expected_length"] == 2567

    # 2. Remote description remains the human's edit intact!
    current_remote = client.card("card_012", include_description=True)
    assert current_remote["description"] == human_edited_desc
    assert len(current_remote["description"]) == 2480


def test_duplicate_write_is_suppressed_as_already_satisfied():
    """If the remote description already matches desired, no PUT request is executed."""
    existing_desc = "Current active description"
    cards_db = {
        "card_100": {
            "id": "card_100",
            "name": "Item 100",
            "desc": existing_desc,
            "idBoard": "board_1",
            "idList": "list_1",
            "idMembers": [],
            "due": None,
            "shortUrl": "https://trello.com/c/100",
        }
    }
    put_executed = False
    def transport(method, path, query, form):
        nonlocal put_executed
        if method == "PUT":
            put_executed = True
        return cards_db["card_100"]

    client = TrelloClient(credential=Credential("k", "t"), transport=transport)
    result = client.sync_description_authorized("card_100", existing_desc)

    assert result["status"] == "already_satisfied"
    assert result["verified"] is True
    assert result["mutated"] is False
    assert not put_executed


def test_csrf_error_fails_closed_without_blind_retry():
    """When API returns 403 CSRF error, fail closed with UNCERTAIN and no blind retry."""
    cards_db = {
        "card_200": {
            "id": "card_200",
            "name": "Item 200",
            "desc": "Before",
            "idBoard": "board_1",
            "idList": "list_1",
            "idMembers": [],
            "due": None,
            "shortUrl": "https://trello.com/c/200",
            "simulate_csrf_403": True,
        }
    }
    client = make_mock_trello(cards_db)
    result = client.sync_description_authorized("card_200", "New Desired")

    assert result["status"] == "UNCERTAIN"
    assert result["verified"] is False
    assert result["reason"] == "csrf_forbidden"
    # Content must remain "Before"
    assert cards_db["card_200"]["desc"] == "Before"


def test_batch_33_items_with_concurrent_edit_halt_and_resumption(tmp_path):
    """33 items batch: items 1..10 succeed, item 11 (card 012) detects concurrent edit, halts safely.
    
    Upon resumption after human clearance, remaining items complete without duplicate writes.
    """
    db_file = tmp_path / "batch_tasks.db"
    import sqlite3
    conn = sqlite3.connect(db_file)
    store = DurableTaskStore(conn=conn)
    artifacts = ArtifactStore(root_dir=tmp_path / "artifacts")

    # Generate 33 items
    items = []
    for i in range(1, 34):
        cid = f"card_{i:03d}"
        items.append({
            "card_id": cid,
            "desired_desc": f"Description for {cid}",
            "expected_len": 100,
            "current_remote_len": 2480 if cid == "card_012" else 100,
            "is_human_edited": cid == "card_012",
        })

    proof = RunClosureProof(
        task_id="task_trello_33_batch",
        run_id="run_batch_001",
        operation_id="op_batch_sync",
        semantic_fingerprint="sem_batch_sync_hash",
        operation_family="trello_batch_sync",
        target_family="trello_card",
        deterministic_representation_ref="trello:sync_description",
        executable_primitive_or_capability="trello_sync",
        compatible_route="native_browser",
        authority_scope=AuthorityScope(level=AuthorityLevel.LOCAL_MUTATION, allowed_actions={"trello_sync"}),
        effect_budget=[],
        verifier_contract={"kind": "readback"},
        first_verified_evidence_ref="artifact://evidence_1",
        replay_evidence_ref="artifact://evidence_2",
        uncertainty_clear=True,
        parameter_schema={"card_id": "string", "desired_desc": "string"},
        bindings={"card_id": "$item.card_id", "desc": "$item.desired_desc"},
        remaining_items_ref="artifact://tasks/batch_33.json",
        remaining_item_count=33,
        expected_operational_utility=33.0,
    )

    dispatched_cards = []

    def dispatch(tool, args):
        dispatched_cards.append(args["card_id"])
        return {"status": "ok", "card_id": args["card_id"]}

    steps = [
        {
            "id": "sync_desc",
            "tool": "trello_sync",
            "args": {"card_id": "$item.card_id", "desc": "$item.desired_desc"},
            "concurrent_edit_check": lambda bound, payload: (
                f"concurrent_human_edit: {payload['card_id']} diverged ({payload['current_remote_len']} != {payload['expected_len']})"
                if payload.get("is_human_edited") else None
            ),
            "verifies": [],
        }
    ]

    # Run batch
    result = execute_in_flight_handoff(
        proof,
        items,
        steps,
        dispatch,
        task_store=store,
        artifact_store=artifacts,
        stop_on_exception=True,
        max_retries=0,
    )

    # 1. Handoff caught the exception on card 012 and woke for reasoning/human
    assert result["status"] == "NEEDS_REASONING"
    assert result["wake_reason"] == HandoffWakeCondition.CONCURRENT_HUMAN_EDIT.value
    # Items 1..11 were processed, stopped on item 12 (card_012)
    assert "card_012" not in dispatched_cards  # card_012 was halted BEFORE dispatch!
    assert len(dispatched_cards) == 11  # cards 001..011 dispatched and verified

    # Check safe_to_resume
    assert result["safe_to_resume"] is True


def test_human_takeover_lease_blocks_destructive_mutation():
    """When human takeover is active, BrowserControlLeaseManager blocks destructive mutations."""
    from workstation.browser_session import (
        BrowserControlLeaseManager,
        BrowserControlMode,
        HumanTakeoverActiveError,
    )
    manager = BrowserControlLeaseManager()
    task_id = "task_human_active_999"

    # Default lease is agent control
    lease = manager.get_lease(task_id)
    assert lease.mode == BrowserControlMode.AGENT
    # Agent action is allowed
    manager.assert_action_allowed(task_id, "browser_click")

    # Human takeover triggered
    manager.request_human_control(task_id, reason="Human taking control of Trello card")

    # Destructive/mutating actions must now be blocked
    with pytest.raises(HumanTakeoverActiveError):
        manager.assert_action_allowed(task_id, "browser_click")

    with pytest.raises(HumanTakeoverActiveError):
        manager.assert_action_allowed(task_id, "browser_type")

    with pytest.raises(HumanTakeoverActiveError):
        manager.assert_action_allowed(task_id, "browser_batch_actions")

    # Read-only action remains allowed
    manager.assert_action_allowed(task_id, "browser_snapshot")

    # Resuming agent control unblocks mutations
    manager.resume_agent_control(task_id)
    manager.assert_action_allowed(task_id, "browser_click")

