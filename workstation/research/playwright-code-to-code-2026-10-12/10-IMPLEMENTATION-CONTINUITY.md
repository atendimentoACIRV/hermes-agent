# 10 — IMPLEMENTATION CONTINUITY — HERMES BROWSER C2C-P0–P2

**Date:** 2026-10-12. **Release:** NOT_RELEASE_QUALIFIED.
**Stage A:** PENDING_WITH_MAINTAINER_AUTHORIZATION. Upstream refresh, next pin, seams explicitly deferred only for local development; no push or merge.

## Confirmed identity
- Original repository (do not touch dirty UI): `C:\Github\hermes-agent`.
- Isolated worktree: `C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012`.
- Branch: `feat/playwright-c2c-kits-20261012`.
- Base HEAD before this session: `7b590bd35ed9f43701cf152de884b4851c9d9e8e`.
- **Latest verified code HEAD before this documentary checkpoint:** `81a16ed00b78b7f741c331ee90a3bf06b003942f` — `fix(browser): persist mutation admissions and block uncertain operation replay`.
- The exact latest HEAD after documentation commits MUST be obtained by `git rev-parse HEAD`, never inferred from the self-modifying markdown.
- GitHub does not have this local code commit (earlier fetch for 7b590bd got 422). No push, PR or merge performed.

## Implementation executed this session (P0-01/P0-02 PARTIAL, local GREEN)

Reused EXISTING `BrowserSessionStateFilePersistence` as the owner of a synchronous persistent mutation admission fence. Before dispatch, persist the operation ID and structural task/session/run/tab/action identity plus a SHA-256 digest of parameters; no raw page text, HTML, passwords, form contents or screenshots. An old operation ID must not redispatch after intervening receipts or restart; conflicting identity/digest throws `operation_identity_collision`. State corrupted or fsync impossible fails closed. Windows `fsyncSync` requires `r+` descriptor. The previous lastReceipt ACK is not declared remote VERIFIED. Existing browser batch replay response remains `prior_batch_effect_requires_reconciliation`; normal replay yields `status:'uncertain'`.

Files changed: `apps/desktop/electron/workstation-browser-session-state.ts`; `workstation-browser-runtime.ts`; `workstation-browser-admission.test.ts`; `workstation-browser-runtime-task.test.ts`; `workstation-browser-runtime-resilience.test.ts`; `apps/desktop/vitest.browser-native-audit.config.mjs`; `apps/desktop/vitest.browser-native-audit.setup.ts`.

Vitest now sets `HERMES_WORKSTATION_HOME` to a UNIQUE synthetic temporary directory per test, then deletes only that newly created temporary directory. Previously tests isolated HERMES_HOME only; the Workstation on Windows uses LOCALAPPDATA or HERMES_WORKSTATION_HOME. That defect caused replay tests from separate runs to collide and may have written synthetic state to the user's normal HermesWorkstation runtime folder. **DO NOT delete or overwrite any user state there without separately verifying provenance and authorization.**

### RED/GREEN evidence
- RED: four tests in `workstation-browser-admission.test.ts` failed because admission method absent.
- RED: `CRASH-02 runtime` A→B→A reexecuted A, `status` missing.
- RED platform: `fsyncSync` on read-only Windows file descriptor returned EPERM; changed to `r+` and retested.
- RED regression: two existing replay tests required adapted uncertain semantics; repaired.
- RED infrastructure: batch tests collided through the shared default Workstation state. Isolated per test and reran.
- GREEN final: `cd apps/desktop; node ../../node_modules/vitest/vitest.mjs run --config vitest.browser-native-audit.config.mjs --reporter=default` => **19/19 files, 164/164 PASS, exit 0**.
- GREEN native: `cd apps/desktop; node electron/workstation-browser-playwright-native.runner.cjs` => **NATIVE_E2E_PASS, exit 0** (single Electron process, offline).
- `git diff --check` and commit Lefthook => PASS.
- Full Electron TS typecheck => FAIL known unrelated `electron/git-review-ops.test.ts(124,5) TS2349 simple-git not callable`. Only observed diagnostic. Fix/qualify separately.
- Python telemetry 7/7 PASS was rerun this session with isolated unittest runner `C:\Users\Kevyn Lucas\AppData\Local\Temp\run_workstation_playwright_telemetry_unittest.py`; 7 tests OK, exit 0, without private Browser profile.

### Limitations: never claim exactly-once externally
- Admission is durable local replay fencing, not proof a remote website committed an effect.
- No cross-process OS writer lock, no semantic remote reconciler, no durable VERIFIED terminal per operation; Python CertifiedDispatcher and ExecutionJournal still require cross-layer binding.
- Bounded 4096 records fail closed when full; current whole-state rewrite+fsync per operation may cost p95 latency. No compaction or benchmark.
- Coverage: navigate/click/type/scroll/back/press/batch. Creative and extension paths NOT yet guarded. Without caller operation_id, local random ID cannot ensure dedupe on retries.
- Real crash between two Electron processes, renderer fault injection and durable receipt-loss remain unverified; no CI exact-head; Stage A pending for release.

## Phase states
| Phase | Status | Next |
|---|---|---|
| P0-01 crash cases CRASH-01..08 | PARTIAL | real Electron process A kill after effect before receipt, process B restore, A→B→A, forked concurrent collision |
| P0-02 canonical journal | PARTIAL | align CertifiedDispatcher, ExecutionJournal, TaskRun/BrowserTask terminal evidence; use no second store |
| P0-03 actionability/CDP | PARTIAL from prior session | rAF stability, stop pointScript focus/scroll before inspection, input partial safety |
| P0-04 OOPIF/frames/cancel | PARTIAL from prior | frame/loader/context ref binding; cancellation takeover/renderer gone |
| P1-01 causal telemetry | PARTIAL from prior | provider usage attribution, PID window, SQLite/WAL privacy |
| P1-02 benchmark | NOT_STARTED | offline fixed pin baseline, n/p50/p95/CDP/CPU/RSS/tokens/correction |
| P1-03 AXTree/CDP/cache | NOT_STARTED | benchmark-gated, no stale results |
| P1-04 locators/rich editors | NOT_STARTED | strict semantic locators and Electron fixtures |
| P1-05 Experience Compiler | NOT_STARTED | evidence gate, no global promotion |
| QUAL-01 | PARTIAL/BLOCKED | typecheck known TS2349; CI exact-head and native crossprocess unavailable |
| QUAL-02 docs | IN_PROGRESS | update this checkpoint and canonical docs |
| QUAL-03 release | PENDING_WITH_MAINTAINER_AUTHORIZATION | Stage A not permitted yet; no push/main merge |

## NEXT_SESSION_ENTRYPOINT
1. Confirm `git status --short --branch` and `git rev-parse HEAD` in the isolated worktree. Preserve any new work by other agents.
2. **Next exact operation:** extend `apps/desktop/electron/workstation-browser-playwright-native.e2e.cjs` and `workstation-browser-playwright-native.runner.cjs` for two truly separate Electron processes using the same temporary synthetic profile. Process A admits mutation, performs a loopback fixture effect, crashes before receipt; process B restores and replays identical ID; must return UNCERTAIN without second effect. Verify actual loopback side-effect counter, PID and exit codes.
3. First RED/next test: `CRASH-01/07 real cross-process renderer fault`. Present harness only tests same-process E2E.
4. P0-02 next: add admission to creative/extension mutators under existing owner (no new dispatcher), durable reconciliation linked to `workstation/control_plane/dispatcher.py`, `workstation/journal.py`, `workstation/operational_kernel.py`; test crash-after-effect, A→B→A, hash mismatch, concurrent process and fsync failure.
5. Rerun full 164+ Vitest, native Electron, isolated Python telemetry and `tsc -p tsconfig.electron.json --noEmit` (known unrelated simple-git TS2349).
6. Continue P0-03→P0-04→P1-01..P1-05 and docs. Do not synchronize Stage A now.
7. On every interruption update this file and deliver **a new complete copy/paste prompt**, containing exact HEAD/working tree, latest verified tests, next function/first command, all constraints and recursive handoff instruction.

**Guards:** WorkstationBrowserRuntime sole Chromium owner; BrowserTask/TaskRun/CertifiedDispatcher/OperationalKernel/ExperienceCompiler preserved; 409 USER_CONTROL_ACTIVE fail closed; no blind mutation retry; no public sites; no second authority DB; don't delete user's file; no upstream sync now, push/PR/main merge not authorized.
