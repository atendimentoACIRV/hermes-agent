"""Bridge canonically accepted readbacks into active learning; no effect authority."""

from __future__ import annotations

from typing import Any


def notify_canonical_acceptance(
    corpus: Any, accepted_ref: str | None, task_id: str, run_id: str
) -> bool:
    """Publish an actual VERIFIED_SUCCESS sample, never synthesize verification.

    Absent provenance/ref is fail-closed. This is a notification only: it
    does not promote, dispatch, re-open a completed task, or force DIRECT.
    """
    if not accepted_ref or not task_id or not run_id:
        return False
    samples = corpus.query(
        task_id=str(task_id), run_id=str(run_id), outcome="verified_success"
    )
    matching = [s for s in samples if s.provenance.sample_ref == accepted_ref]
    if len(matching) != 1:
        return False
    sample = matching[0]
    if str(sample.provenance.operation_id or "") == "":
        return False
    if not getattr(sample.verification, "evidence_refs", None):
        return False
    from workstation.experience_compiler.compilability_monitor import (
        notify_online_compilability,
    )

    return bool(
        notify_online_compilability(
            ref=accepted_ref,
            task_id=task_id,
            run_id=str(run_id),
            operation_id=sample.provenance.operation_id,
            primitive=sample.operation.primitive,
            route=sample.operation.canonical_route,
            outcome="verified_success",
            event_kind="verified_transition",
            evidence_refs=tuple(sample.verification.evidence_refs),
            operation_family=sample.operation.operation_family,
            target_family=sample.operation.target_family,
        )
    )
