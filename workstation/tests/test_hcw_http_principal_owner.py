"""P0A HTTP admission: a verified login is only a selector, never mutation authority."""
from contextlib import contextmanager
from types import SimpleNamespace
from time import time

import pytest
from hermes_constants import set_hermes_home_override, reset_hermes_home_override
from hermes_state import SessionDB
from hermes_cli import kanban_db
from hermes_cli.dashboard_auth.base import Session, TokenPrincipal
from hermes_cli.kanban_db_connect import connect_closing
from workstation.creative_http_identity import resolve_creative_http_identity


@contextmanager
def store(tmp_path, monkeypatch, *, session_user="account-1", session_key="server-bound-key"):
    home = tmp_path / "profile"
    home.mkdir()
    target = home / "workstation" / "creative" / "projects"
    target.mkdir(parents=True)
    monkeypatch.setenv("HERMES_KANBAN_DB", str(home / "kanban.db"))
    token = set_hermes_home_override(home)
    try:
        with SessionDB(db_path=home / "state.db") as db:
            db.create_session("session-1", source="desktop", user_id=session_user,
                              session_key=session_key, profile_name="test")
        with connect_closing() as conn:
            task = kanban_db.create_task(conn, title="Creative", session_id="session-1",
                                        workspace_kind="dir", workspace_path=str(target))
            claimed = kanban_db.claim_task(conn, task, ttl_seconds=300)
            assert claimed
        yield home, task, claimed.current_run_id
    finally:
        reset_hermes_home_override(token)


def request(*, user="account-1", gated=True, identity=True):
    principal = (Session(user_id=user, email="e@e.test", display_name="Test", org_id="",
                         provider="test", expires_at=int(time()) + 300,
                         access_token="access", refresh_token="refresh")
                 if identity else None)
    return SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(auth_required=gated)),
        state=SimpleNamespace(session=principal))


def test_http_principal_is_matched_to_stored_session_and_live_claim(tmp_path, monkeypatch):
    with store(tmp_path, monkeypatch) as (_, task, run):
        result = resolve_creative_http_identity(request(), "session-1")
        assert result["sessionId"] == "session-1"
        assert result["taskId"] == task
        assert result["runId"] == run
        assert result["authorityGranted"] is False
        assert "sessionKey" not in result
        assert "profileHome" not in result
        assert "claimLock" not in result


@pytest.mark.parametrize("kwargs", [
    {"user": "forged-user"}, {"gated": False}, {"identity": False},
])
def test_unverified_http_identity_denied(tmp_path, monkeypatch, kwargs):
    with store(tmp_path, monkeypatch):
        with pytest.raises(PermissionError):
            resolve_creative_http_identity(request(**kwargs), "session-1")


@pytest.mark.parametrize("session_user,session_key", [
    ("another-user", "server-bound-key"),
    ("", "server-bound-key"),
    ("account-1", ""),
])
def test_unowned_or_unkeyed_session_denied(tmp_path, monkeypatch, session_user, session_key):
    with store(tmp_path, monkeypatch, session_user=session_user, session_key=session_key):
        with pytest.raises(PermissionError):
            resolve_creative_http_identity(request(), "session-1")


def test_wrong_session_selector_cannot_claim_other_run(tmp_path, monkeypatch):
    with store(tmp_path, monkeypatch):
        with pytest.raises(PermissionError):
            resolve_creative_http_identity(request(), "session-2")


def test_closed_and_superseded_runs_denied(tmp_path, monkeypatch):
    with store(tmp_path, monkeypatch) as (_, task, _):
        with connect_closing() as db:
            db.execute("UPDATE tasks SET status = 'done' WHERE id = ?", (task,))
            db.commit()
        with pytest.raises(PermissionError):
            resolve_creative_http_identity(request(), "session-1")


def test_two_claimed_runs_in_one_session_are_ambiguous(tmp_path, monkeypatch):
    with store(tmp_path, monkeypatch) as (home, _, __):
        with connect_closing() as db:
            second = kanban_db.create_task(db, title="Other", session_id="session-1",
                workspace_kind="dir", workspace_path=str(home / "workstation" / "creative" / "projects"))
            assert kanban_db.claim_task(db, second, ttl_seconds=300)
        with pytest.raises(PermissionError):
            resolve_creative_http_identity(request(), "session-1")


def test_service_principal_is_not_implicitly_interactive_actor(tmp_path, monkeypatch):
    with store(tmp_path, monkeypatch):
        req = request(identity=False)
        req.state.token_authenticated = True
        req.state.token_principal = TokenPrincipal(principal="account-1", provider="service")
        with pytest.raises(PermissionError):
            resolve_creative_http_identity(req, "session-1")

def test_real_web_server_registers_readonly_owner_endpoint():
    from hermes_cli.web_server import app
    matched = [r for r in app.routes if getattr(r, "path", "") ==
               "/api/workstation/creative/owner-readiness"]
    assert len(matched) == 1
    assert matched[0].methods == {"GET"}


def test_real_http_anonymous_cannot_discover_an_owners_run():
    from fastapi.testclient import TestClient
    from hermes_cli.web_server import app
    with TestClient(app) as client:
        response = client.get("/api/workstation/creative/owner-readiness",
                              params={"session_id": "session-1"})
    assert response.status_code in {401, 403}
    assert "sessionKey" not in response.text
