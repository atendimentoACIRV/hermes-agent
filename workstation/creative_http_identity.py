"""Authenticated HTTP principal -> canonical session/TaskRun discovery (NO authority grant).

This is deliberately read-only. The FastAPI OAuth/session gate owns actor
authentication. A session selector is never an authority claim, and this
projection must NEVER be used as the TrustedCreativeOwner of a mutation.
"""
from __future__ import annotations

from pathlib import Path
from time import time

from hermes_constants import get_hermes_home
from hermes_state import SessionDB
from hermes_cli import kanban_db
from hermes_cli.dashboard_auth.base import Session
from hermes_cli.kanban_db_connect import connect_closing
from workstation.authority_supersession import classify_run_authority


class CreativeHttpIdentityDenied(PermissionError):
    """The HTTP identity cannot be joined to exactly one canonical live run."""


def resolve_creative_http_identity(request, session_id: str) -> dict:
    """Verify existing OAuth principal, SessionDB owner and Kanban claim.

    This cannot establish live gateway ContextVars, human-control authority,
    Electron sender ownership or an authenticated canonical mutation RPC.
    """
    principal = getattr(request.state, "session", None)
    if (getattr(request.app.state, "auth_required", False) is not True
            or getattr(request.state, "token_authenticated", False)
            or not isinstance(principal, Session)
            or not principal.user_id or principal.expires_at <= int(time())
            or not isinstance(session_id, str) or not session_id
            or len(session_id) > 256):
        raise CreativeHttpIdentityDenied("creative_verified_interactive_principal_required")

    home = Path(get_hermes_home()).resolve()
    try:
        # Read ONLY the current server's profile store. Neither profile paths
        # nor a session->database route are accepted from a browser or client.
        with SessionDB(db_path=home / "state.db", read_only=True) as sessions:
            record = sessions.get_session(session_id)
        if (not record or record.get("id") != session_id
                or record.get("user_id") != principal.user_id
                or not record.get("session_key")
                or record.get("ended_at") is not None
                or record.get("archived")):
            raise CreativeHttpIdentityDenied("creative_session_not_owned")

        db_path = kanban_db.kanban_db_path().resolve()
        if not db_path.is_file() or not db_path.is_relative_to(home):
            raise CreativeHttpIdentityDenied("creative_profile_claim_store_unavailable")
        with connect_closing(db_path) as connection:
            candidates = kanban_db.list_tasks(connection, status="running", session_id=session_id)
            claimed = [task for task in candidates if task.current_run_id is not None]
            if len(claimed) != 1:
                raise CreativeHttpIdentityDenied("creative_claim_ambiguous")
            task = claimed[0]
            run = kanban_db.get_run(connection, task.current_run_id)
            if (run is None or run.task_id != task.id
                    or classify_run_authority(task, str(task.current_run_id), connection=connection) is not None
                    or run.status != "running" or run.ended_at is not None
                    or not task.claim_lock or task.claim_lock != run.claim_lock
                    or not task.claim_expires or not run.claim_expires):
                raise CreativeHttpIdentityDenied("creative_claim_not_live")
            expires = min(int(task.claim_expires), int(run.claim_expires))
            if expires <= time():
                raise CreativeHttpIdentityDenied("creative_claim_expired")
            # Read-only workspace containment check. Actual write operations
            # still require CreativeRunContext and the native policy engine.
            root = home / "workstation" / "creative"
            workspace = Path(task.workspace_path or "").resolve(strict=True)
            if (not workspace.is_dir() or workspace == root
                    or not workspace.is_relative_to(root)):
                raise CreativeHttpIdentityDenied("creative_claim_workspace_invalid")
    except (OSError, ValueError) as exc:
        raise CreativeHttpIdentityDenied("creative_canonical_owner_unavailable") from exc

    return {
        "sessionId": session_id,
        "taskId": task.id,
        "runId": task.current_run_id,
        "expiresAt": expires * 1000,
        "authorityGranted": False,
    }
