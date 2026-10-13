"""HCW P0A: project canonical TaskRun facts from already-authenticated backend context.

NOT a route, login, token issuer, or renderer authority. The caller MUST derive
session_record from its canonical authenticated SessionDB, authenticated_user_id
from an already-verified request principal, and lease_is_clear from the native
authority owner. No caller may forward renderer-supplied values as those facts.
"""
from __future__ import annotations

from collections.abc import Mapping
from time import time

from gateway.session_context import get_bound_session_env
from hermes_constants import get_hermes_home
from hermes_cli import kanban_db
from hermes_cli.kanban_db_connect import connect_closing
from tools.approval_context import get_current_session_key
from workstation.config import WorkstationConfig
from workstation.creative_project_runtime import CreativeRunContext


class CreativeAttestationDenied(PermissionError):
    """No proven authenticated owner of exactly one live canonical TaskRun."""


def attest_creative_taskrun(
    config: WorkstationConfig, *, authenticated_user_id: str,
    session_id: str, session_record: Mapping | None,
    lease_is_clear: bool = False,
) -> dict:
    """Attest only an already-bound gateway context, never a web form's identity.

    This function is intentionally unusable from a normal detached HTTP request:
    a web server must not invent HERMES_SESSION_KEY/HERMES_SESSION_ID, substitute
    user-provided session identities or treat a login as a TaskRun claim.
    """
    if (not isinstance(authenticated_user_id, str) or not authenticated_user_id.strip()
            or not isinstance(session_id, str) or not session_id.strip()
            or not isinstance(session_record, Mapping)
            or session_record.get("id") != session_id
            or session_record.get("user_id") != authenticated_user_id
            or lease_is_clear is not True):
        raise CreativeAttestationDenied("creative_authenticated_owner_required")

    key = get_bound_session_env("HERMES_SESSION_KEY")
    if (not key or key != get_current_session_key(default="")
            or get_bound_session_env("HERMES_SESSION_ID") != session_id):
        raise CreativeAttestationDenied("creative_live_gateway_context_required")

    try:
        home = get_hermes_home()
        with connect_closing(kanban_db.kanban_db_path()) as db:
            candidates = kanban_db.list_tasks(db, status="running", session_id=session_id)
            claimed = [task for task in candidates if task.current_run_id is not None]
            # Never infer ownership from "the first running task": competing
            # TaskRuns in the same session MUST be disambiguated by a trusted owner.
            if len(claimed) != 1:
                raise CreativeAttestationDenied("creative_taskrun_not_unique")
            task = claimed[0]
            context = CreativeRunContext(str(home), key, session_id, task.id, task.current_run_id)
            context.validate(config)
            run = kanban_db.get_run(db, task.current_run_id)
            if (run is None or not task.claim_expires or not run.claim_expires):
                raise CreativeAttestationDenied("creative_claim_expiry_missing")
            expiry = min(int(task.claim_expires), int(run.claim_expires)) * 1000
    except (OSError, ValueError, PermissionError) as error:
        raise CreativeAttestationDenied("creative_taskrun_not_attested") from error

    now_ms = int(time() * 1000)
    if expiry <= now_ms:
        raise CreativeAttestationDenied("creative_claim_expired")
    return {
        "taskId": task.id, "runId": task.current_run_id,
        "sessionId": session_id, "sessionKey": key,
        "profileHome": str(home), "actorId": authenticated_user_id,
        "authorized": True, "humanControlActive": False,
        "expiresAt": min(now_ms + 15_000, expiry),
    }
