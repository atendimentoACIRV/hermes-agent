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


## P0 KANBAN-04 — cross-TaskRun handoff fencing + readback guidance + native lost-ACK proof (2026-10-12)

Starting from clean published PR #83 HEAD `dd708241177ec7bfb2ef9dd5fc7f4992b7a11330` on isolated worktree `C:\Github\hermes-agent-kanban-browser-authority-20261012`. Checkout root: 34 unrelated dirty paths, never changed. No real user data or historical state altered. PR remains draft; no main merge.

### Reproduced RED and fixes

1. `workstation/tests/test_denied_mutation_handoff_recovery.py::test_uncertain_handoff_never_reuses_approval_from_superseded_run`: consumed human review from `run-old` was reused under a different `run-new` for the same task/session/operation; **RED 1/1**, before fix. Canonical `workstation_tool_batch_admission` now adds a non-null `_canonical_work_run_id` to `HumanHandoffManager.request(...scope)`. An old consumed review cannot grant the new run's readback disposition; an uncertain new run gets a new waiting review. The existing no-TaskRun workflow remains session/task scoped.
2. `test_consumed_review_returns_readback_guidance_without_another_handoff`: repeated admission of an *already consumed* review returned `BatchAdmissionAction.HANDOFF`, risking another UI popup. **RED 1/1**, before fix. It now returns `SYNTHETIC_RESULT` for consumed reviews with code `uncertain_effect_requires_readback`, while pending reviews remain `HANDOFF`. The originally uncertain write is still blocked by `decisions_for_calls`; a human review is not an independent persisted-state proof. No new state machine.
3. The message was tightened: independent readback is required; human review alone cannot authorize uncertain-effect replay. The 11-test scoped admission/HTTP/ledger suite PASSED, and the canonical 7-suite Python regression run was launched. Record exact final result separately.

### Native Electron/Chromium uncertainty gate

Added `P0: native Browser mutation remains observable after lost controller acknowledgment` in `apps/desktop/e2e/workstation-headless-load.spec.ts`.

The existing isolated loopback page server now exposes a deterministic `/p0-uncertain-native` button and read-only `/p0-native-effect-state` endpoint. Real native controller browser_click dispatches a Chromium click to commit a single POST; the client aborts its controller HTTP response **only after the server confirms the side effect was recorded** (a controlled lost-ack simulation, not proof that production agent timeouts themselves are wired to the handoff). A new controller `browser_snapshot` and independent read-only loopback GET prove that the effect was applied once, without resending the browser_click. A second session remains navigable.

Isolated native scenario: **1 PASS, 0 FAIL**, about 1.9 minutes on worktree-built Electron/Chromium. E2E TS typecheck PASS. The combined 4-test P0 native suite is being rerun; do not record its outcome without observing the terminal result. Previous 3 native P0 scenarios already qualified takeover→409→release, UI clicks, cold restart and active human lease isolation in earlier PR #83 commits.

### Remaining release blockers (still OPEN)

- **Actual UI review and causal continuation**: no verified mapping from Python `HumanHandoffManager` state through the native Electron renderer review controls and back to a trusted readback verifier was established. Do not label this implementation KANBAN-04 fully qualified. Begin at `workstation/integrations/hermes/tool_batch_admission.py::workstation_tool_batch_admission`, trace emitted `BatchAdmissionAction.HANDOFF` through `agent/turn_tool_round.py` / `run_agent.py` to the real UI transport; build only the canonical owner seam, then RED native E2E `P0: uncertain native Browser mutation requires single human handoff, independent readback and safe resume`.
- **Trusted typed readback**: reuse `workstation/control_plane/verification.py::evaluate_verification` with validated `VerificationContract`, required predicates, observer trust/failure domains and exact task/run/operation/resource lineage. Human assent or `verified=True` alone must not mark a mutation verified. Never turn a once-uncertain write into an automatic replay when its readback confirms success; use a non-mutating checkpoint/continuation path.
- KANBAN-01 intent corpus with measured FP/FN; KANBAN-02 crash/restart contention; KANBAN-03 effect-typed acceptance; KANBAN-05 independent blocked tasks and orphan handoffs; KANBAN-06 dry-run only for 106 historic deleted tasks and 55 orphan handoffs; KANBAN-07 native packaged app, exact-HEAD GitHub CI and H-079 upstream-first/stacked PR qualification.
- No merge to main until required gates and authorization. Any agent stopping now MUST emit an updated copy-paste RESUME PROMPT with verified HEAD, results, exact next symbol/test, state protection.


### KANBAN-04 follow-up: scoped authority + native lost-ACK RED/GREEN (2026-10-12)

- Starting Git HEAD: `dd708241177ec7bfb2ef9dd5fc7f4992b7a11330`, PR #83 draft and no main merge. Root checkout has 34 pre-existing uncommitted changes; those and all real sessions/cards/handoffs are untouched.
- **RED 1:** `test_uncertain_handoff_never_reuses_approval_from_superseded_run` demonstrated a consumed handoff from `run-old` reappearing as the same `handoff_id` under `run-new`. Fixed `workstation/integrations/hermes/tool_batch_admission.py::workstation_tool_batch_admission` by adding the canonical non-null TaskRun ID to the existing operation-scoped human review identity, without replacing the canonical JSON owner. Existing session-only operations retain their identity.
- **RED 2:** `test_consumed_review_returns_readback_guidance_without_another_handoff` showed a consumed review emitting `BatchAdmissionAction.HANDOFF` again, potentially requesting another popup. Fixed to emit `SYNTHETIC_RESULT` with `uncertain_effect_requires_readback` for consumed reviews; `HANDOFF` still applies to waiting review. Original uncertain external write remains blocked. Human approval is NEVER a retry grant or semantic proof.
- **Native Electron/Chromium:** added `P0: native Browser mutation remains observable after lost controller acknowledgment` in `apps/desktop/e2e/workstation-headless-load.spec.ts`. A real native BrowserTask clicks a button in Chromium; deterministic local server commits one POST; authenticated controller response is canceled *after* the effect but before acknowledgment; independent controller snapshot and local GET prove side effect count=1, with no repeated click. An unrelated session still works. This is a **controlled lost-ACK test**, not an automatic Hermes agent timeout→human UI review integration test. Native isolated test 1 PASS.
- **Combined native fixture RED→GREEN:** initial 4-test P0 suite had 3 PASS / 1 FAIL because prior cold-restart test had closed the shared Electron fixture before the new native effect scenario; `ECONNREFUSED` on controller. Moved native effect scenario **before** the deliberate cold restart in the same E2E file; full combined native P0 suite then **4 PASS / 0 FAIL / 0 SKIP in 193.29s**. No production controller/lease code weakened.
- **Canonical typed verifier proof test:** added `test_canonical_typed_readback_requires_matching_operation_run_and_persisted_source` to `test_p0_uncertain_mutation_readback.py`. Uses existing `workstation/control_plane/verification.py::evaluate_verification`, verifies a validated trusted independent persisted readback contract with correct lineage and rejects foreign run/operation, weak evidence, stale read-before-write, and mismatched state. This is contract qualification only; no automatic provider readback claim.
- Python scoped admission + handoff tests **11 PASS**; selected canonical Python regression **33 PASS** before the additional typed test; a full re-run after the added typed test is pending terminal result. Electron/Vitest native owner regression **58 PASS**. E2E TypeScript check and Ruff passed, git diff whitespace passed. Record canonical final Python outcome separately.
- **Still OPEN:** actual Hermes native UI human review control wired to `HumanHandoffManager` via owner-approved transport, single consumption and verified typed readback, work-item checkpoint continuation without repeating the uncertain mutation; deidentified task-admission corpus, supersession/crash recovery, type-specific acceptance, historical dry-run only, native packaged binary, exact-head CI/H-079 and stacked PR chain qualification. KANBAN-04 remains PARTIAL. Do not represent synthetic result or local server test as native human approval E2E.
- Next test name: `P0: uncertain native Browser mutation requires single human handoff, independent readback and safe resume`. Next code seam: `workstation/integrations/hermes/tool_batch_admission.py::workstation_tool_batch_admission`, tracing `BatchAdmissionAction.HANDOFF` through `agent/turn_tool_round.py` and `run_agent.py` into the actual Desktop renderer/IPC. Reuse `evaluate_verification` with a real trusted read-only observer and exact task/run/operation/resource evidence. No fresh permission after readback, no uncertain replay. Implement TDD, native E2E, complete release gates.

### Exact-worktree final gate results — KANBAN-04 follow-up

- Canonical Windows `scripts/run_tests.sh` with 7 selected suites: **34 PASS / 0 FAIL** in 19.9s (7 workers), including added TaskRun review fence, consumed-review popup suppression and typed proof negative controls.
- Source-built Windows real Electron/Chromium `playwright test workstation-headless-load --grep 'P0:'`: **4 PASS / 0 FAIL / 0 SKIP** in 193.29s, including native lost-ACK and prior takeover, UI click, and cold restart/active human lease scenarios. One pre-fix combined attempt: **3 PASS / 1 FAIL**, stale shared fixture after the deliberate cold restart; reordered tests to keep destructive restart last, then GREEN.
- Electron/Vitest targeted regressions: **58 PASS / 0 FAIL**. TypeScript E2E `tsc -p tsconfig.e2e.json --noEmit`: exit 0. Scoped Ruff and git whitespace validation: PASS.
- The linked native UI approval→typed readback→work-item continuation and packaged Windows installer/CI have **NOT** been qualified. No merge or real user data mutation authorized.


## 2026-10-12 — KANBAN-04 native human review transport (partial gate)

Previous verified published HEAD: 22498a09db0802c06125f5a5ec4cb5039da9b98f; isolated worktree C:\Github\hermes-agent-kanban-browser-authority-20261012; PR #83 draft; 34 unrelated root-checkout edits preserved.

### Canonical boundary discovered

The agent's `BatchAdmissionAction.HANDOFF` is projected as a tool result via `agent/turn_tool_round.py::run_tool_round` (and `run_agent.py` direct-call path) but there was no React-native review UI/API integrated with `HumanHandoffManager`. It did NOT connect typed `evaluate_verification` readback automatically. Do not represent that tool response as an authorized human approval.

### Implemented, scoped

- `plugins/workstation/dashboard/plugin_api.py`: asynchronous, session-filtered read of *waiting* `HumanHandoffManager` entries using existing canonical JSON owner, bounded to 32; projects IDs/status/reason only, no operation payload. A review acknowledgment performs identity/status/run fences and delegates to `HumanHandoffManager.resume` (atomic one-time transition); output explicitly reports `readback_required=True, mutation_authorized=False`.
- `hermes_cli/web_server.py`: thin token-protected routes `GET /api/workstation/handoffs?session_id=...` and `POST /api/workstation/handoffs/{handoff_id}/review`; no direct mutation/replay, no second state store.
- `apps/desktop/src/app/chat/right-rail/workstation-browser-pane.tsx`: polls authenticated *local* backend only when pane/session active, scopes review to current session, shows warning and human acknowledgment button; success removes the request without granting tool permission and displays explicit readback-needed notice.
- Tests: new `test_p0_native_handoff_review_api.py` intentionally RED 2/2 (API missing), then GREEN with other handoff regressions **12 PASS / 0 FAIL**; `workstation-browser-pane.test.tsx` new UI test RED missing button, then GREEN **2 PASS / 0 FAIL**, verifying real React handler bound to expected session/run and no direct Browser mutation; app and E2E TypeScript check exited 0; scoped Ruff and git diff --check passed.
- New source-built Electron E2E `P0: native UI acknowledges canonical uncertain Browser handoff without replay` in `apps/desktop/e2e/workstation-headless-load.spec.ts` uses a seed of canonical JSON in disposable `HERMES_HOME`, not actual agent admission. This tests only native UI/transport and read-only Browser continuation; it cannot qualify automatic agent handoff→typed readback→work-item completion. First isolated attempt failed **before entering test body**: fixture onboarding/reconnecting overlay obstructed composer after 120s (`waitForAppReady`). A combined 2-test run starts with already qualified Browser UI takeover first; final verdict must be recorded separately.
- No real user Kanban, sessions, Browser leases or historical handoffs mutated. No main merge.

### Remaining highest-priority gate

1. Native UI transport E2E green on own-head Electron; investigate fixture failures separately from application logic. If already passes, implement **real agent admission** path (not seeded ledger) emitting HANDOFF to renderer and resume signal to agent, including proof binding.
2. Trusted provider readback under `workstation/control_plane/verification.py::evaluate_verification`: validated owner contract, independent persistence proof, task/run/operation/resource/effect identity, read-after-write, wrong-run and stale negative controls. Never accept renderer supplied boolean as proof. Never redispatch uncertain external mutation.
3. Non-mutating work-item checkpoint continuation and restart E2E, isolation across two sessions.
4. Other KANBAN-01/02/03/05/06/07 gates; KANBAN-06 dry-run only (106 deleted tasks and 55 orphan handoffs), release app packaged + exact-HEAD CI/H-079 + stacked PR dependencies. PR draft no auto merge.

Mandatory: any incomplete agent must return another independently executable resume prompt with exact verified HEAD, branch, worktree, tests and next functions.


### Native Browser Hub → Chat preview routing RED→GREEN (2026-10-12)

Native source-built E2E `P0: native UI acknowledges canonical uncertain Browser handoff without replay` initially failed before test body when an isolated first launch was blocked by onboarding/reconnect overlay. A paired run with the Browser UI readiness scenario passed the first test but failed to display the review after transfer.

**Root cause confirmed by source and E2E DOM snapshot:** `apps/desktop/src/app/browser/index.tsx::transferToChat` called `openWorkstationBrowserPreview()` before navigating away from `/browser`; `apps/desktop/src/store/preview.ts::openWorkstationBrowserPreview` intentionally rejected all calls while the Browser Hub route was active. The explicit transfer therefore returned home with the right-rail preview not opened. The E2E had also not explicitly selected the newly persisted chat, leaving `New session` in focus, so session-scoped reviews were not visible.

**Fix:** explicit `openWorkstationBrowserPreview({ fromHub: true })` bypasses the route guard only for the human transfer, while automatic opens still respect the guard; the E2E selects its persisted conversation with `openStoredSessionByTitle`. New `src/store/preview-tabs-restart.test.ts` test reproduces the failed transfer RED, then GREEN after the fix. `workstation-browser-pane.test.tsx` UI button/REST test also GREEN. Joint UI run: **4 passed, 0 failed**; an unrelated initial UI baseline import was slow and timed out with default 15s on overloaded Windows (later 30s rerun GREEN); no production timeout increased. Paired native E2E rerun is underway and must have its actual outcome recorded before declaring qualification.

The UI human action acknowledges uncertainty once; it **never** clears mutation uncertainty, confers Browser lease, marks a Kanban card done, or repeats the external effect. The actual agent execution chain → typed verifier → WorkItem continuation gate remains open.

### P0 native UI review continuation — 2026-10-12 13:03 local, uncommitted
- Verified published remote PR #83 HEAD remains `22498a09db0802c06125f5a5ec4cb5039da9b98f`; draft. Isolated worktree already had 13 uncommitted paths when this continuation began (existing API, UI, Browser Hub routing and tests). Main checkout had 34 unrelated dirty paths, not touched.
- Inspected existing work-in-progress implementation instead of overwriting it. Python `test_p0_native_handoff_review_api.py` + `test_denied_mutation_handoff_recovery.py`: **8 PASS**, scoped, isolated ledger; React `workstation-browser-pane.test.tsx` + `preview-tabs-restart.test.ts`: **4 PASS**.
- E2E attempted `playwright test workstation-headless-load --grep 'P0: (Browser UI Take Control|native UI acknowledges canonical)'`: **1 PASS (real Browser UI takeover) / 1 FAIL (native UI review)**, consistently reproduces `getByRole('button', { name: 'Acknowledge uncertain Browser operation' }).toBeVisible()` timed out after 25s, while the E2E previously proved the authenticated API returned seeded canonical review. Source-built Chromium fixture logs confirm selected persisted chat, Browser preview mounted, but review action missing from DOM. E2E thus remains RED; do not claim completion.
- Scoped attempt in `workstation-browser-pane.tsx`: read only canonical conversation aliases of selected session, deduplicate handoff IDs, use exact review.session_id in POST, tolerate partial failure with `Promise.allSettled`, and use non-passive authenticated local API. These are not yet proven to resolve the E2E. Pending changes are deliberately uncommitted; **do not overwrite existing concurrently authored work or stage/push a failing gate as qualified**.
- Next exact diagnostic: instrument **only the isolated E2E** to inspect the React pane's actual selectedStoredSessionId, activeSessionId and derived `activeSessionAliases` (without exposing IDs to logs), and check `window.hermesDesktop.api({ path: '/api/workstation/handoffs?session_id=...', connectionId:'local' })` from the same mounted component. Differentiate missing selected-session key, per-alias backend rejection, effect repeatedly reset, and renderer right-rail mount/visibility. Do not increase the 25s assertion timeout as a substitute for fixing the actual cause.
- Once RED reason is proven and fixed, rerun Python UI API and React unit suites, full native E2E, then typed `evaluate_verification` provenance/WorkItem continuation. No actual agent admission→UI approval→readback→non-mutating TaskRun checkpoint E2E exists; preserve `409 USER_CONTROL_ACTIVE` and uncertainty blocked until trusted independent observation.
