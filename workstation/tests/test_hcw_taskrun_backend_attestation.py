"""P0A: backend attestation must derive TaskRun from canonical Kanban, not renderer IDs."""
from contextlib import contextmanager
from time import time

import pytest

from gateway.session_context import scoped_current_session_id, set_session_vars, clear_session_vars
from hermes_constants import set_hermes_home_override, reset_hermes_home_override
from hermes_cli import kanban_db
from hermes_cli.kanban_db_connect import connect_closing
from tools.approval_context import set_current_session_key, reset_current_session_key
from workstation.config import WorkstationConfig
from workstation.creative_taskrun_attestation import attest_creative_taskrun


@contextmanager
def live_scope(tmp_path, monkeypatch, *, bind_gateway=True):
    home = tmp_path / "profile"
    home.mkdir()
    workspace = home / "workstation" / "creative" / "projects"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("HERMES_KANBAN_DB", str(home / "kanban.db"))
    token = set_hermes_home_override(home)
    session = set_current_session_key("trusted-gateway-session-key")
    gateway_tokens = (set_session_vars(session_id="session-1", session_key="trusted-gateway-session-key")
                      if bind_gateway else None)
    try:
        with scoped_current_session_id("session-1"):
            with connect_closing() as db:
                task_id = kanban_db.create_task(db, title="Creative run", session_id="session-1",
                                                workspace_kind="dir", workspace_path=str(workspace))
                task = kanban_db.claim_task(db, task_id, ttl_seconds=300)
            assert task is not None
            yield home, task_id, task.current_run_id
    finally:
        if gateway_tokens is not None:
            clear_session_vars(gateway_tokens)
        reset_current_session_key(session)
        reset_hermes_home_override(token)


def proof(_home, **kwargs):
    inputs = {
        "authenticated_user_id": "account-1", "session_id": "session-1",
        "session_record": {"id": "session-1", "user_id": "account-1"},
        "lease_is_clear": True,
    }
    inputs.update(kwargs)
    return attest_creative_taskrun(WorkstationConfig({"creative": {"enabled": True}}), **inputs)


def test_live_authenticated_owner_is_derived_from_canonical_taskrun(tmp_path, monkeypatch):
    with live_scope(tmp_path, monkeypatch) as (home, task_id, run_id):
        result = proof(home)
        assert result["taskId"] == task_id
        assert result["runId"] == run_id
        assert result["actorId"] == "account-1"
        assert result["sessionKey"] == "trusted-gateway-session-key"
        assert result["authorized"] is True


@pytest.mark.parametrize("changes", [
    {"authenticated_user_id": ""},
    {"authenticated_user_id": "forged-account"},
    {"session_id": "forged-session"},
    {"session_record": {"id": "other-session", "user_id": "account-1"}},
    {"session_record": {"id": "session-1", "user_id": "other-account"}},
    {"lease_is_clear": False},
    {"lease_is_clear": None},
])
def test_untrusted_identity_or_human_control_fails_closed(tmp_path, monkeypatch, changes):
    with live_scope(tmp_path, monkeypatch):
        with pytest.raises(PermissionError):
            proof(None, **changes)


def test_finished_or_superseded_taskrun_is_not_attested(tmp_path, monkeypatch):
    with live_scope(tmp_path, monkeypatch) as (_, task_id, _run_id):
        with connect_closing() as db:
            db.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
            db.commit()
        with pytest.raises(PermissionError):
            proof(None)


def test_competing_claimed_task_in_same_session_fails_closed(tmp_path, monkeypatch):
    with live_scope(tmp_path, monkeypatch) as (home, _, _run_id):
        with connect_closing() as db:
            other = kanban_db.create_task(
                db, title="Concurrent run", session_id="session-1",
                workspace_kind="dir", workspace_path=str(home / "workstation" / "creative" / "projects"))
            assert kanban_db.claim_task(db, other, ttl_seconds=300)
        with pytest.raises(PermissionError):
            proof(None)


def test_missing_gateway_session_key_denies_even_live_task(tmp_path, monkeypatch):
    with live_scope(tmp_path, monkeypatch):
        set_session_vars(session_id="session-1", session_key="")
        with pytest.raises(PermissionError):
            proof(None)

def test_approval_context_without_gateway_bound_key_does_not_grant_authority(tmp_path, monkeypatch):
    # A caller (including a detached HTTP handler) must not reuse an ambient
    # HERMES_SESSION_ID or an approval-only key to impersonate a live turn.
    with live_scope(tmp_path, monkeypatch, bind_gateway=False):
        with pytest.raises(PermissionError):
            proof(None)

def test_proof_never_outlives_canonical_taskrun_claim(tmp_path, monkeypatch):
    with live_scope(tmp_path, monkeypatch) as (_, task_id, run_id):
        claim_end = int(time()) + 5
        with connect_closing() as db:
            db.execute("UPDATE tasks SET claim_expires=? WHERE id=?", (claim_end, task_id))
            db.execute("UPDATE task_runs SET claim_expires=? WHERE id=?", (claim_end, run_id))
            db.commit()
        attested = proof(None)
        assert attested["expiresAt"] <= claim_end * 1000
