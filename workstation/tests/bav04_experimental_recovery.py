"""BAV04 **TEST-ONLY** crash-window fencing contract using canonical Hermes stores.

Not a product adapter and not an authority source: admission/readback callbacks are
fixture inputs. No task or Browser owner is created here. Production use requires
qualified H-079 Stage A and independently authenticated admission/readback.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from workstation.artifacts import ArtifactStore
from workstation.contracts import ExecutionEventKind
from workstation.journal import ExecutionJournal
from workstation.memory import WebProcedure
from workstation.routines import procedure_fingerprint


class UnsafeReplay(ValueError):
    """Mutation cannot be resumed without a compatible independent proof."""


class RecoveryFence:
    """A thin experimental pre-dispatch fence; DeterministicRoutineRunner still executes."""

    def __init__(
        self, *, journal: ExecutionJournal, artifacts: ArtifactStore,
        procedure: WebProcedure, task_id: str, session_id: str, run_id: str,
    ) -> None:
        self.journal = journal
        self.artifacts = artifacts
        self.procedure = procedure
        self.task_id = task_id
        self.session_id = session_id
        self.run_id = run_id

    def _events(self):
        state = self.journal.integrity()
        if state["status"] != "verified" and state["events"] != 0:
            raise UnsafeReplay("unverified or damaged journal cannot authorize replay")
        return self.journal.read_events()

    def _unresolved(self) -> dict[str, Any] | None:
        pending: dict[str, Any] | None = None
        for event in self._events():
            meta = event.metadata
            if meta.get("bav04_phase") == "pending":
                if pending is not None:
                    raise UnsafeReplay("multiple unresolved mutations")
                pending = meta
            if meta.get("bav04_phase") == "independently_verified" and pending:
                if pending["operation_id"] != meta.get("operation_id"):
                    raise UnsafeReplay("journal operation lineage mismatch")
                pending = None
        return pending

    def unresolved_step(self) -> int | None:
        current = self._unresolved()
        return current["step_index"] if current else None

    def mark_dispatched(self, *, step_index: int, operation_id: str, baseline_effects: int = 0) -> None:
        if self.procedure.lifecycle.value != "promoted":
            raise UnsafeReplay("procedure is not promoted")
        if self._unresolved() is not None:
            raise UnsafeReplay("uncertain prior mutation prevents new dispatch")
        if not operation_id or not 0 <= step_index < len(self.procedure.steps) or not isinstance(baseline_effects, int) or baseline_effects < 0:
            raise UnsafeReplay("invalid mutation operation")
        if self.procedure.steps[step_index].action not in {"click", "type", "press"}:
            raise UnsafeReplay("operation must be a bounded effectful step")
        self.journal.record(ExecutionEventKind.ACTION,
            "BAV04 experimental mutation pending before controller dispatch",
            metadata={
                "bav04_phase": "pending",
                "boundary": "acceptance",  # fsync before the external effect
                "operation_id": operation_id,
                "baseline_effects": baseline_effects,
                "step_index": step_index,
                "procedure_id": self.procedure.id,
                "version": self.procedure.version,
                "fingerprint": procedure_fingerprint(self.procedure),
                "task_id": self.task_id,
                "session_id": self.session_id,
                "run_id": self.run_id,
                "scope": self.procedure.scope,
            })

    def reconcile_for_resume(
        self, *, admission: dict[str, Any],
        independent_readback: Callable[[], dict[str, Any] | None],
    ) -> str:
        pending = self._unresolved()
        if pending is None:
            raise UnsafeReplay("no uncertain mutation to reconcile")
        exact = {
            "task_id": self.task_id,
            "session_id": self.session_id,
            "run_id": self.run_id,
            "scope": self.procedure.scope,
        }
        if not isinstance(admission, dict):
            raise UnsafeReplay("current authenticated admission required")
        if any(admission.get(key) != value for key, value in exact.items()):
            raise UnsafeReplay("recovery authority or scope mismatch")
        if admission.get("lease_valid") is not True:
            raise UnsafeReplay("lease revoked or not attested")
        if admission.get("host") != "127.0.0.1" or admission["host"] not in self.procedure.scope.get("allowed_hosts", []):
            raise UnsafeReplay("recovery host mismatch")
        if any(pending.get(k) != v for k, v in {
            **exact,
            "procedure_id": self.procedure.id,
            "version": self.procedure.version,
            "fingerprint": procedure_fingerprint(self.procedure),
        }.items()):
            raise UnsafeReplay("saved checkpoint is from a different procedure, version or owner")
        result = independent_readback()
        if not isinstance(result, dict) or result.get("verified") is not True or (
            result.get("fault_domain") != "fixture-server"
        ) or result.get("effect_count") != pending.get("baseline_effects", 0) + 1:
            raise UnsafeReplay("uncertain mutation requires independent fixture-server readback")

        self.journal.record(
            ExecutionEventKind.ACTION, "BAV04 independently reconciled test-only effect",
            metadata={
                "bav04_phase": "independently_verified",
                "operation_id": pending["operation_id"], "boundary": "acceptance",
                "step_index": pending["step_index"], "fault_domain": "fixture-server",
            },
        )
        # Reuse existing canonical ArtifactStore checkpoint shape and Runner.resume_ref.
        return self.artifacts.store_json(
            {
                "safe_to_resume": True,
                "context": {
                    "procedure_id": self.procedure.id,
                    "version": self.procedure.version,
                    "fingerprint": procedure_fingerprint(self.procedure),
                    "completed_steps": pending["step_index"] + 1,
                },
            },
            task_id=self.task_id, name="bav04_verified_resume.json",
        )
