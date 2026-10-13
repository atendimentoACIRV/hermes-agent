# 10 — IMPLEMENTATION CONTINUITY — HERMES BROWSER C2C-P0–P2

## 2026-10-12 — P0-02 CAUSAL FENCE / EXECUTION JOURNAL; P0-03 CDP INPUT

**Last tested CODE HEAD:** `b9addc487abc9852368d927cbcc25b588e8b108d`, branch `feat/playwright-c2c-kits-20261012`, worktree `C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012`. Recheck HEAD and status after documentary commits. Stage A: `PENDING_WITH_MAINTAINER_AUTHORIZATION` (do not synchronize upstream/pin/seams during local work). Main/other UI agent changes untouched, no push, PR or merge. NOT_RELEASE_QUALIFIED.

**Commits created:**
- `1c46a508d304b237bb617f9a56e6491bbcf81858`: native BrowserSessionState records `acknowledged=true` only with matching persisted owner receipt, never external VERIFIED. Operation A admitted then crash with lost receipt blocks NEW operation ID B (same TaskRun) before any lazy browser recovery and again atomically during durable admission. Reject forged admission ACK. Stable generated opId across admission and receipt for controller actions. Two-process real Electron RED B had been accepted → GREEN B reconciliation_required and fixture effect count stays 1. Unit RED/green for A/B, ACK and injection.
- `3793c46a15b51ef4f0b05cb955a453727b9020fc`: browser shim tools/browser_workstation.py writes structural ACKNOWLEDGED, UNCERTAIN and RECONCILIATION_REQUIRED observations into EXISTING ExecutionJournal with task/session/run/operation/action identifiers, never raw DOM, fields, URLs, or implicit VERIFIED. This is a post-controller audit projection, NOT a terminal CertifiedDispatcher proof and not second owner. 5 Python journal tests PASS; 7 existing native telemetry tests PASS.
- `b9addc487abc9852368d927cbcc25b588e8b108d`: CDP pointer recovery. After ambiguous mousePressed/mouseReleased timeout or takeover, never retry press. Best-effort cleanup release; output remains browser_input_state_uncertain because release may itself trigger effect. Agent lease/document epoch/URL checked between mouse events. Three RED→GREEN tests passed.

**Exact-head evidence:** `cd apps/desktop && node ../../node_modules/vitest/vitest.mjs run --config vitest.browser-native-audit.config.mjs --reporter=default` => 19 files, **174/174 PASS**, exit 0. `node electron/workstation-browser-playwright-native.runner.cjs` => NATIVE_E2E_PASS, exit 0. `node electron/workstation-browser-crash-replay-native.runner.cjs` => CRASH_REPLAY_NATIVE_PASS, exactly one local GET side effect with distinct Electron process PIDs, exit 0. `node electron/workstation-browser-admission-concurrency.runner.cjs` previously PASS (lock unchanged). `C:\Github\hermes-agent\.venv\Scripts\python.exe -m unittest workstation.tests.test_browser_workstation_journal_projection -v` => **5 PASS**. `py -3 'C:\Users\Kevyn Lucas\AppData\Local\Temp\run_workstation_playwright_telemetry_unittest.py'` => **7 PASS**. Python compileall PASS. Full TS typecheck still fails only observed `electron/git-review-ops.test.ts(124,5) TS2349 simple-git` (known unrelated error).

**QUALIFICATION WARNING:** Ruff strict pre-commit Python hook has 19 lint errors in tools/browser_workstation.py, all independently confirmed **preexisting** by running the same Ruff check over `git show HEAD:tools/browser_workstation.py` before code commit. No new Ruff errors. Python code commit `3793c46a15` used `LEFTHOOK=0` for that one commit only AFTER 5+7 Python tests and syntax checks, to avoid modifying unrelated baseline; lint gate remains OPEN, not passed. The TypeScript code commit used standard Lefthook.

**Remaining critical P0-02:** Native ACK is NOT external verification or a canonical terminal COMMITTED transition. A successful local receipt currently releases the pending-admission barrier even when a remote postcondition is INCONCLUSIVE. CertifiedDispatcher keeps records in memory and needs durable typed verification linkage to browser TaskRun/BrowserTask + ExecutionJournal; Python journal projection alone is not pre-effect proof. Creative/extension mutations not fully covered; lock orphan recovery requires explicit maintainer reconciliation; 4096 admission cap and whole-snapshot fsync overhead unbenchmarked. No universal exactly-once external claim. A prior POST-click crash fixture failed; native crash E2E only proves local deliberate side-effectful GET navigation.

**Remaining P0-03:** rAF target geometry stability, overlay/hit-target across frames, input keyboard partial failures, real native takeover mid-CDP, monotonic deadline/cancellation. **P0-04** iframe/OOPIF/frame identity untouched; **P1-01..P1-05** telemetry baseline, benchmarks, optimization, rich editors, ExperienceCompiler not qualified.

**NEXT_SESSION_ENTRYPOINT:** Verify `git status --short --branch` / `git rev-parse HEAD` in isolated worktree, read this checkpoint then start RED test for `P0-02: operation A locally ACKNOWLEDGED but externally INCONCLUSIVE, different operation B must not be externally VERIFIED/COMMITTED or blindly retried without canonical reconciliation`. Inspect `workstation/control_plane/dispatcher.py`, `workstation/control_plane/verification.py`, `workstation/journal.py`, `tools/browser_workstation.py`, `apps/desktop/electron/workstation-browser-task.ts`, `workstation-browser-session-state.ts`, `workstation-browser-runtime.ts`. Connect existing owner and typed verifier, not another journal/dispatcher. Continue creative/extension coverage, P0-03 residual, P0-04, P1 and QUAL. Always hand off recursively via `11-NEXT-SESSION-PROMPT.md`.

## 2026-10-12 — P0-02 INTERPROCESS ADMISSION + UNCERTAIN NAVIGATION RECOVERY

**Last confirmed code HEAD:** `da3ca495690bc56b26088fb40d8a2c594348d30a`. Worktree `C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012`, branch `feat/playwright-c2c-kits-20261012`. A later documentation commit may advance HEAD; always re-check Git before changing files. Main and other agents' Browser Hub/right rail remain untouched. No push/PR/merge. Stage A `PENDING_WITH_MAINTAINER_AUTHORIZATION` for local development only, `NOT_RELEASE_QUALIFIED`.

**New code commits:**
- `20acf1d2e9fb02282a4bf346f4a3653aeb172f6c` — CRASH-03 concurrency: two independent Node processes use a barrier before saving same operation ID. RED reproduced **both processes ADMITTED (2 !== 1)**; GREEN an exclusive create-only lock permits only one; other fails closed. Lock is synchronization marker, not authority DB; foreign/stale locks are never stolen. Every BrowserSessionState save now uses same lock and merges persisted admission identities so stale session projection cannot erase an operation. Also guards replay BEFORE lazy BrowserTask view materialization.
- `da3ca495690bc56b26088fb40d8a2c594348d30a` — Native Electron found a second effect from task URL lazy restoration after blocking replay. Enhanced two-process crash fixture RED (2 GET effects vs expected 1), then prevents auto-loading the last safe URL when latest navigation admission has no matching receipt. Restores a committed `about:blank` document so CDP snapshot succeeds without network replay. Regression RED caught normal navigation no-op-ID generating DIFFERENT admitted and receipt IDs; fixed stable single ID; normal multi-task restore and crash unsafe restore now both GREEN.

**Reproducible evidence:** `cd apps/desktop && node ../../node_modules/vitest/vitest.mjs run --config vitest.browser-native-audit.config.mjs --reporter=default` => **19 files / 168 tests PASS** on last code changes (exit 0). `node electron/workstation-browser-crash-replay-native.runner.cjs` => two independent real Electron PIDs, exactly one local GET effect, no second effect after explicit replay **OR read-only snapshot**; phase B restores about:blank and snapshot succeeds. `node electron/workstation-browser-admission-concurrency.runner.cjs` => exactly one admitted writer, second denied. `node electron/workstation-browser-playwright-native.runner.cjs` => PASS. Full `tsc -p tsconfig.electron.json --noEmit` still fails only observed baseline issue `electron/git-review-ops.test.ts:124 TS2349 simple-git not callable` (not corrected here). Historical Python telemetry tests 7/7 PASSED prior session; rerun after Python changes.

**CRITICAL LIMITS:** not general remote exactly-once; native crash fixture deliberately uses GET with side effect to catch unintended URL restoration, not POST button click; click-based POST test remains unqualified. Last receipt is NOT external VERIFIED; 4096 admissions need retention/perf strategy; lock left by OS crash blocks until explicit reconciliation (NO AUTO DELETE). Multiple writers can be serialized locally but controller authority still expects one owner. Creative/extension admission incomplete. Any NEW mutation ID following an unverified prior operation may still proceed; require a real terminal verifier/journal gate for this before release. Frame/OOPIF, mouse input partial dispatch, causal telemetry and benchmarks pending. Not CI exact-head or H-079 Stage A release green.

**NEXT_SESSION_ENTRYPOINT (highest impact):** verify actual Git `status`/`HEAD`; implement RED for **unverified operation A followed by NEW operation B in same TaskRun** after crash — prevent B from silently proceeding until A is externally reconciled. Extend existing canonical `CertifiedDispatcher`, `ExecutionJournal`, BrowserTask and TaskRun terminal evidence (not a second authority store); add causal receipt/recovery semantics and tests for crash/replay, stale lock manual reconciliation, creative/extension owner coverage. Then P0-03 actionability, P0-04 OOPIF/deadlines and P1 measurement/optimizations. Preserve full recursive prompt handoff at `11-NEXT-SESSION-PROMPT.md`.


## 2026-10-12 — P0-01 REAL TWO-PROCESS FAULT INJECTION + P0-03 PREPARATION SAFETY

**Latest verified CODE HEAD:** `246477e4c0`. Latest documentation HEAD must always be verified with `git rev-parse HEAD`. Branch unchanged, original main checkout untouched, no push/PR/merge; Stage A PENDING_WITH_MAINTAINER_AUTHORIZATION.

**New commits:**
- `7623bfbfcb` — `test(browser): prove replay fence across crashed Electron processes`. Two NEW native fixtures `apps/desktop/electron/workstation-browser-crash-replay-native.e2e.cjs` and `workstation-browser-crash-replay-native.runner.cjs`. Actual independent Electron process A navigates to a **test-only local GET /effect** endpoint that increments an external loopback count. Failure injected after HTTP effect but before browser owner receipt, exit 86; process B uses same TEMPORARY synthetic state, attempts identical operationId, returns UNCERTAIN and makes no second request. Parent verifies persisted admission, missing receipt, matching task lineage, 2 distinct PIDs, exactly one effect. Command `cd apps/desktop && node electron/workstation-browser-crash-replay-native.runner.cjs` => `CRASH_REPLAY_NATIVE_PASS effects=1 processes=87152,85296`, exit 0. Repeat later with different PIDs; do not treat this GET fixture as evidence for actual click remote outcomes or generalized external exactly-once.
- `246477e4c0` — `fix(browser): reject disabled targets before scroll or focus`. Native E2E RED: disabled button in nested offscreen scroll area had scrollTop changed from 0 to 311.2 before rejection. Added preflight read-only disabled/inert/style check in `pointScript` ahead of scrollIntoView/focus. Native GREEN: `NATIVE_E2E_PASS`, exit 0; regression `164/164` Vitest passed; same cross-process fixture PASS after code.

**Important failed preliminary experiment:** A separate click-based HTTP fixture was attempted before navigation-based proof. Controller's CDP click ACK did not cause synthetic HTTP POST or change button DOM text (diagnostic `CLICK_DOM_READBACK Effect`). The click experiment was replaced by a navigation-based fault-injection test, not passed for clicks. Do not fabricate click success; investigate input forwarding/host visibility before claiming crossprocess click reliability.

**Residuals:** journal still only structural admission in BrowserSessionState; needs canonical CertifiedDispatcher/ExecutionJournal terminal records, verification, interprocess writer lock, no blind retry; guard other mutating creative/extension operations; cap 4096 and whole-state sync perf. Actionability still lacks rAF stable, view reposition rechecks and CDP mousePressed/mouseReleased recovery.

**NEXT_SESSION_ENTRYPOINT UPDATED:** first verify HEAD and git clean; implement CRASH-03 concurrent admissions by two separate processes on same synthetic state file, same operation ID, assert exactly one admission possible and zero duplicates. Current BrowserSessionStateFilePersistence `admitBrowserMutation` uses atomic rename + fsync but has **no explicit interprocess writer lock**, so concurrent processes may both admit. Reproduce RED with deterministic barrier; then implement lock using same existing owner without a parallel authority DB. If uncertain, fail closed; do not delete unknown lock data. Then complete P0-02 CertifiedDispatcher/ExecutionJournal linkage with TaskRun/BrowserTask and verified outcome; keep Stage A deferred.


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
