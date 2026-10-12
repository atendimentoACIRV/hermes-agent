# KANBAN-04 — atomic human handoff transitions (2026-10-12)

Scope: only Session/TaskRun-safe human review under the existing `workstation/runtime.py::HumanHandoffManager` JSON owner. Draft PR #83 `fix/p0-kanban-browser-authority-20261012`; worktree `C:\Github\hermes-agent-kanban-browser-authority-20261012`. No merge, no real user Kanban/handoff changes. The separate root checkout has 34 unrelated user edits and was not touched.

## Reproduced RED defect

Two independent `HumanHandoffManager` instances loading the same JSON before mutation each retained a stale snapshot. The first wrote review A, the second wrote B from its old snapshot. B overwrote A. For identical `task_id/session_id/reason/scope`, two stale instances minted **two** different handoff IDs; another manager could also consume from stale status and rewrite another worker's progress.

Added tests in `workstation/tests/test_p0_handoff_concurrent_owner.py`. Original implementation **2 failed / 0 passed** for stale-manager distinct-scope loss and duplicate-scope identity. No special timing or artificial injection required.

## Scoped fix

The canonical JSON owner remains unchanged; there is no parallel approval database or alternative state machine.

In `workstation/runtime.py::HumanHandoffManager`, each `request/resume/consume` now holds the existing Hermes cross-platform OS lock `hermes_cli.active_sessions._FileLock` on the JSON's sibling `.lock` file, reloads the latest ledger, checks the transition, then atomically replaces the JSON. A manager keeps object references for existing returned reviews while refreshing their mutable status. The writer temp filename is process- and thread-scoped to avoid cross-process collision; malformed or unreadable ledgers fail closed without overwriting the original bytes. `get` also reloads recent committed state.

Invariants: one human review per exact operation/scope even under independent processes; `resume` only from waiting; `consume` only from ready; consumed never implies persisted remote mutation; unrelated session scopes do not lose each other's handoffs. A failed I/O or corrupt ledger cannot be rewritten as an empty valid state.

## Deterministic integration evidence

- `test_p0_handoff_concurrent_owner.py` covers stale manager identity, distinct records, synchronized *independent Windows process* handoff requests, and corrupt-ledger fail closed. 3 Windows-process/concurrent tests passed before adding corruption test; rerun full file after final edit.
- `test_p0_uncertain_mutation_readback.py` operates on a local HTTP server and isolated `HERMES_HOME`: the simulated external POST commits once and its response exceeds the client deadline; `prepare_mutation` has persisted a pending uncertain effect before I/O. A newly loaded agent receives REQUIRE_HUMAN; the same operation returns one stable handoff. Read tools and a second session remain unblocked. Human resume/consume is once; an independent HTTP GET confirms the effect once; the same original mutation remains blocked from automatic replay. **1 PASS** in isolated local test.
- NOTE: this is a **Python admission/ledger + deterministic network integration** test, NOT the Electron native Browser readback/approval E2E. It is deliberately fail-closed and does not claim automatic work-item continuation. The real provider verifier and exact effect-to-readback cryptographic/semantic proof are not yet implemented.
- Preserve earlier PR #83 gates: native BrowserTasks/cold restart/409 and UI click **3 PASS**, Electron runtime **58 PASS**, prior Python **50 PASS**, none of which directly qualifies native KANBAN-04.

## Remaining, ordered

1. **KANBAN-04 native E2E:** use built Electron and deterministic loopback state page; exercise actual Browser mutation with real timeout after side effect, human UI handoff, independent controller Browser snapshot, approval consumed once, no popup loop, no mutation redispatch, same session/run authority across restart. Begin in `apps/desktop/e2e/workstation-headless-load.spec.ts` and `workstation/integrations/hermes/tool_batch_admission.py::workstation_tool_batch_admission`. Do not claim this Python integration fulfills native E2E.
2. Implement or qualify a typed owner-approved `uncertain -> verified` reconciliation path only on verifiable persisted semantic readback. A human click alone must never clear uncertainty. Keep unchanged `409 USER_CONTROL_ACTIVE` and stale run fences.
3. KANBAN-01 corpus of deidentified actual intents (FP/FN); KANBAN-02 worker restart/completed task; KANBAN-03 per-effect acceptance; KANBAN-05 blocked/orphan isolation; KANBAN-06 historical review in dry-run only (106 deleted tasks, 55 orphan handoffs); KANBAN-07 packaged native Windows application E2E, dependency PR chain, exact-head CI and H-079 release qualification.
4. Never merge to main without separate gates and authorization. Every incomplete implementing assistant must deliver a copy/paste updated resume prompt containing actual branch/SHA/test outcomes.



### KANBAN-04 execution evidence — 2026-10-12 (handoff atomicity + active human lease)

- RED stale-manager reproducer: two independent cached `HumanHandoffManager` objects previously overwrote unrelated JSON reviews and minted separate handoff IDs for the identical task/session/reason/scope (**2 RED / 0 GREEN** before correction).
- Owner `workstation/runtime.py::HumanHandoffManager` corrected: uses existing cross-process `hermes_cli.active_sessions._FileLock` around canonical JSON reload, request/resume/consume and atomic persist; fresh `get` reads disk; bad JSON fails closed, no mass historical review rewrite.
- Windows independent-process synchronized requests now converge on one handoff; new corruption and stale-object tests verify no lost updates and consumption exactly once.
- Added isolated deterministic HTTP timeout mutation/readback integration proof in `workstation/tests/test_p0_uncertain_mutation_readback.py`: external POST commits once before response timeout, freshly reconstructed agent gets REQUIRE_HUMAN, handoff ID stable, human resume+consume once, independent GET confirms effect, original mutation remains refused rather than dispatched again, other session read unaffected. Not a native Electron tool→approval UI→provider readback E2E and not a qualified automatic reconciliation path.
- **Canonical Windows runner:** 9 Python suites, **64 PASSED / 0 FAILED** (124.7s wall, 8 workers), covering runtime, handoffs, Browser session isolation, TaskCompiler, admission/claim multiprocess, completion proof. See exact selected paths in `P0_KANBAN04_HANDOFF_ATOMICITY_2026-10-12.md`.
- Extended native P0 restart E2E to also cover a **second restart with active human control**: before shutdown Browser operation is refused with exact 409 USER_CONTROL_ACTIVE; upon restart, the prior process' human lease is not resurrected as new-process authority; persisted sessionHost is recovered and new navigation/readback succeeds. **1 native Electron E2E PASSED (194.53s)**, source-built isolated worktree. No production Browser takeover/release semantics were relaxed.
- Three native P0 scenario combined re-run started after extended test; final count must be recorded after execution. No packaged MSI/EXE validation and no exact HEAD GitHub Actions proof yet. Never merge into main solely on these local tests.
- Historical 106 deleted tasks and 55 orphan handoffs remain read-only; root user's 34 uncommitted files preserved.


### Final scoped P0 gates after active-human-lease E2E — 2026-10-12

- Windows source-built **real Electron/Chromium P0 combined**: `$env:HERMES_DESKTOP_PYTHON='C:\Github\hermes-agent-p0-kanban-effects\.venv\Scripts\python.exe'; cd apps/desktop; ..\..\node_modules\.bin\playwright.cmd test workstation-headless-load --grep 'P0:' --reporter=line --timeout=360000` → **3 PASSED, 0 FAILED, 0 SKIPPED (141.67s)**. The cold restart case exercises *two successive Electron restarts*: released human lease then active human lease, with 409 before shutdown and no unauthorized stale-lease inheritance. Run from isolated PR worktree; not packaged installer.
- **Canonical Python runner:** 9 files **64 PASSED / 0 FAILED** in 124.7s with 8 workers: `test_p0_handoff_concurrent_owner.py`, `test_p0_uncertain_mutation_readback.py`, `test_denied_mutation_handoff_recovery.py`, `test_runtime.py`, `test_task_compiler.py`, `test_p0_multiprocess_task_admission.py`, `test_p0_concurrent_task_admission.py`, `test_browser_session_run_isolation_p0.py`, `test_p0_completion_proof_boundary.py`.
- `tsc -p apps/desktop/tsconfig.e2e.json --noEmit`: EXIT 0. Scoped `ruff check`: all passed.
- **No native effect-timeout→human approval UI→provider readback certification yet**, no typed verified-status transition or actual work-item resume; keep KANBAN-04 PARTIAL. Production installer test and exact-HEAD CI remain release gates.
