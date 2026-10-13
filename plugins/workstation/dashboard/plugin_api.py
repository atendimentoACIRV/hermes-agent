from __future__ import annotations

import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/resources")
async def get_workstation_resources():
    """Project the Electron Workstation resources for Dashboard clients."""
    from workstation.client import get_workstation_resources as read_resources
    return await asyncio.to_thread(read_resources)


@router.get("/events")
async def get_workstation_events(task_id: Optional[str] = None, limit: int = 200):
    """Project bounded canonical Workstation journal events for clients."""
    from workstation.client import get_workstation_events as read_events
    return await asyncio.to_thread(read_events, task_id=task_id, limit=limit)


@router.get("/tasks/{task_id}/cockpit")
async def get_workstation_task_cockpit(task_id: str, request: Request, board: Optional[str] = None):
    def read():
        from hermes_cli import kanban_db_connect
        from workstation.cockpit import task_cockpit
        conn = kanban_db_connect.connect(board=board)
        try:
            return task_cockpit(conn, task_id)
        finally:
            conn.close()
    try:
        return await asyncio.to_thread(read)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# Canonical human review projection for the native Workstation Browser.
# Reads/writes only HumanHandoffManager; never grants mutation or verification.
async def list_native_handoff_reviews(*, session_id: str) -> dict:
    from hermes_constants import get_hermes_home
    from workstation.runtime import HumanHandoffManager

    if not session_id or len(session_id) > 256:
        raise HTTPException(status_code=400, detail="valid session_id required")

    def read() -> dict:
        ledger = HumanHandoffManager(get_hermes_home() / "workstation" / "human_handoffs.json")
        reviews = [
            {
                "handoff_id": review.handoff_id,
                "task_id": review.task_id,
                "session_id": review.session_id,
                "run_id": review.scope.get("run_id", ""),
                "status": review.status,
                "reason": review.reason,
                "requested_at": review.requested_at,
            }
            for review in ledger._handoffs.values()
            if review.session_id == session_id
            and review.reason == "uncertain_mutation_requires_review"
            and review.status == "waiting-for-human"
        ]
        reviews.sort(key=lambda item: (item["requested_at"], item["handoff_id"]))
        return {"handoffs": reviews[:32]}

    return await asyncio.to_thread(read)


async def resume_native_handoff_review(
    handoff_id: str, *, session_id: str, run_id: str,
) -> dict:
    from hermes_constants import get_hermes_home
    from workstation.runtime import HumanHandoffManager

    if not handoff_id.startswith("handoff-") or len(handoff_id) > 128:
        raise HTTPException(status_code=400, detail="invalid handoff_id")
    if not session_id or len(session_id) > 256 or len(run_id) > 256:
        raise HTTPException(status_code=400, detail="invalid review identity")

    def resume() -> dict:
        ledger = HumanHandoffManager(get_hermes_home() / "workstation" / "human_handoffs.json")
        review = ledger.get(handoff_id)
        if review is None or review.session_id != session_id:
            raise HTTPException(status_code=404, detail="review not found")
        if review.scope.get("run_id", "") != run_id:
            raise HTTPException(status_code=409, detail="TaskRun authority mismatch")
        if review.reason != "uncertain_mutation_requires_review" or review.status != "waiting-for-human":
            raise HTTPException(status_code=409, detail="review is no longer pending")
        if not ledger.resume(handoff_id, returned_by="desktop-human"):
            raise HTTPException(status_code=409, detail="review was already handled")
        return {"handoff_id": handoff_id, "status": "ready",
                "readback_required": True, "mutation_authorized": False}

    return await asyncio.to_thread(resume)
