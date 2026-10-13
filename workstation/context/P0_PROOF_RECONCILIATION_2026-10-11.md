# P0.3 completion proof + P0.5 safe historical reconciliation — 2026-10-11

**Branch:** `fix/p0-proof-bound-completion-20261011` (based on integrated P0 branch; NOT main).
**Status:** code and focused regressions implemented/tested locally, not native Electron or production-qualified.
**H-079:** PASS_WITH_AUTHORIZATION allows isolated engineering, not promotion.

## Scope, ownership, and decision

This change intentionally addresses only the two defensible vertical seams below. It does **not** silently complete all 14 roadmap fronts and does **not** alter the user's live Kanban, Browser, permissions, sessions or data.

### P0.3 — Completion admission must fail closed

Source: `workstation/integrations/hermes/completion_admission.py`.

Before: the Python adapter admitted a dictionary if either `status == "verified_completed"` OR `acceptance_approved == True`, admitted unrecognized statuses and missing payloads by fallback, and admitted legacy object proofs even with a mismatched run identity.

After: an admitted dict requires `task_id` match, an optional matching `run_id`, `status == "verified_completed"` **AND** `acceptance_approved is True`. Missing, conflicting, incomplete or unknown receipts are rejected. Legacy object admission requires verified boolean **and** canonical matching run. Non-Kanban owned task behavior is unchanged, as it belongs to another completion policy. No proof is synthesized.

**RED:** 9 failing and 2 passing in new `test_p0_completion_proof_boundary.py` before correction. **GREEN:** 11 passed after. Wider completion/smart-task/continuity regression: 78 passed / 0 failed over four suites on the modified worktree.

**Remaining P0.3:** selecting a semantically correct `AcceptanceContract` by trusted outcome/effect type, mapping artifact readback and publication receipts, and full user-facing E2E; generic `AcceptanceContract()` remains in `work_intent.py`. Thus P0.3 is **PARTIAL**, not qualified.

### P0.5 — Historical reconciliation with zero source mutation

New: `workstation/kanban_reconcile_preflight.py`.

- Requires explicit paths for canonical DB, historical backup DB, handoff ledger and output directory.
- Opens both sources with read-only SQLite connections; validates `quick_check`.
- Creates a consistent copy via the SQLite backup API (handles WAL) into a new output directory, refuses overwrites.
- Emits a local JSON dry-run manifest: task intersections, current/backup-only task IDs, TaskRuns, WorkPlans, WorkItems, orphan runs and handoffs.
- Every current task is `PRESERVE`. Every backup-only task is `RETAIN_DELETED` pending explicit confirmation of restoration. Orphan handoffs/runs are `MARK_FOR_HUMAN_REVIEW`; never resumed or deleted automatically.
- Snapshot and historic backup SHA-256 included in the **local** report. Keep per-record proposals out of public GitHub.
- Does not restore, mark DONE, remove handoffs, grant leases or write to source databases.

**Windows real-data DRY RUN** (read-only, snapshot in private `%TEMP%\hermes-p0-reconcile-*`):
- Canonical DB: **19 tasks**, **19 runs**, zero WorkPlans, zero WorkItems.
- Historical backup: **106 tasks**, **40 runs**, **31 WorkPlans**, **152 WorkItems**.
- **Zero overlapping task IDs; 19 current-only; 106 backup-only** retained as deleted.
- **57 handoffs total; 55 have no corresponding canonical task.**
- Proposals: `PRESERVE=19`, `RETAIN_DELETED=106`, `MARK_FOR_HUMAN_REVIEW=55`. None applied.
- Generated canonical snapshot: 409,600 bytes. No user data included in this document.

Four targeted tests cover read-only snapshot, corrupt DB/schema validation, deletion preservation, orphan handoff/run classification and overwrite refusal. **4 passed**.

**Remaining P0.5:** reconcile richer historical provenance, user-facing review UX, explicit user-approved restore decisions, a transactional apply engine and rollback rehearsal. Do not build an apply path by copying all 106 old rows: the user previously asked to delete boards/cards. Restore only upon explicit scoped authorization.

## Evidence gates

| Gate | Status |
|---|---|
| Isolated worktree | yes; based on PR #76 integration |
| P0.3 reproducer RED → GREEN | 9 RED, 11 GREEN |
| Cross-suite P0.3 regression | 78 passed, 0 failed |
| P0.5 isolated SQLite tests | 4 passed, 0 failed |
| P0.5 real-data dry run | completed, no source mutation |
| Ruff + git whitespace | passed on scoped paths |
| Exact-head CI | unverified |
| Windows packaged Electron | not run |
| Real historical data mutation | **not authorized; not performed** |
| Full P0.1–P0.5 qualification | **not achieved** |
| Full nine product priorities | **not achieved** |

Next sequence: typed acceptance contracts + proof binding per effect, deterministic worker contention / idempotent triage, durable handoff reconciliation, packaged Electron replay and native Browser/One-Click, then shared CreativeDocument bridge and true PNG/MP4/3D exports.

### P0.2 — Explicit authorization required for forced task creation

The existing `WorkstationKanbanBridge.promote_request_if_multistep(force=True)` bypassed intent classification for any `CREATE_WORK` human envelope, including point actions. This bypass was exercised by H080B test fixtures but is not a normal production ingress route.

Added a guard: `force=True` requires an existing trusted `MessageEnvelope.can_create_work` **and** an explicit typed ingress marker `metadata["explicit_force_work"] is True`. Without that marker, the method returns `None`, even if a caller supplies `force=True`. Normal durable work admission is unchanged. Intentional H080B test setup now marks its synthetic forced work explicitly, instead of relying on an unqualified bypass.

**RED:** unauthorized `force=True` turned a one-shot `Abre o Trello` into a Kanban task; 1 failed, 1 passed before fix. **GREEN / REGRESSION:** `test_p0_force_task_authority.py`, `test_smart_task_admission.py` and canonical work loop rerun on updated code. This does not yet qualify cross-process idempotency or full semantic task admission.
