# MVP Kanban + Browser SUPERSEDED — execution checkpoint

Date: 2026-10-12. **State: MVP PARTIALLY QUALIFIED / all product gates still unverified.** This record is a factual handoff, not proof of integration. Work remains.

## Identity and isolation

- Repository: `kevynlucasprofissional-stack/hermes-agent`.
- Source PR: [#83](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/83), draft, head `22498a09db0802c06125f5a5ec4cb5039da9b98f`, stacked on `fix/p0-proof-bound-completion-20261011`.
- New branch: `fix/mvp-kanban-browser-superseded-20261012`, created from **the exact #83 head**.
- New draft PR: [#88](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/88); base `fix/p0-kanban-browser-authority-20261012`, not `main`.
- First test commit: `0cdfe4b6b7815b34355b1ceadf32dfff3dc7d1b5`.
- Production fix commit: `2336e15b2cd121bf6438407075a27773c08a7596`.
- Fixture initialization follow-up: `04a7a7de50b702c6841b38b9d1f31109954e9e06`.
- The commit adding **this checkpoint** is newer: use `git rev-parse HEAD` and compare `origin/fix/mvp-kanban-browser-superseded-20261012` after fetch. Do not quote the earlier SHA as final HEAD.
- No Windows worktree was created or modified in this session. Historical #83 worktree: `C:\Github\hermes-agent-kanban-browser-authority-20261012` (do not touch without checking). Root checkout `C:\Github\hermes-agent` has historically been dirty; present status remains **unverified**.
- No merge to main, no user Kanban/database changes.

## Change made and proof level

1. `workstation/tests/test_browser_session_run_isolation_p0.py`:
   - Existing fake explicit-bind happy path replaced with a **real claimed canonical task/run fixture**.
   - Regression for nonexistent explicit card/run pair, card-only binding and run-only binding.
   - Test initializes isolated HERMES_HOME database.
2. `tools/browser_workstation.py::_dispatch`:
   - Rejects partial card/run binding with `STALE_RUN` **before dispatch**.
   - Rejects missing canonical card instead of accepting `get_task(...) is None`.
   - Existing checks for current run, running status and owning session remain.
   - No-card/no-run chat Browser session continues on its legitimate session-only path.
3. This prevents a specific identifiable authority-validation gap. **It does not prove resolution of the persistent cross-tool SUPERSEDED symptom**.

**Test qualification: NONE in this session.** Remote Desktop Commander device DESKTOP-3NA47UH (`fdf43006-f9bb-4933-98bc-6c6c76e9f2c4`) was listed online, but `start_process` and even `ping` timed out without a device response. No test logs, RED proof, GREEN proof, CI, native Windows Electron or packaged dogfood run exist for this new branch. GitHub combined statuses and PR-associated workflow runs for fix SHA `2336e15...` were empty. Do not report PASS. The original PR #83 has historical tests, but those are **not** test runs for our changes.

## Original goals and invariants

- Upstream Kanban remains canonical SQLite execution coordinator (CAS/BEGIN IMMEDIATE); human Kanban columns are separate from machine execution status.
- Conversation, point action and durable task are distinct. One-shot Browser commands create no speculative Kanban TaskRun; durable tasks enter triage and are claimed before executable dispatch.
- Session, Kanban Task, TaskRun, BrowserTask and operation are distinct identities. Never borrow prior run/global operation ID across chats.
- Keep `SUPERSEDED` and `409 USER_CONTROL_ACTIVE` safety fences. A stale owner cannot mutate, but an independent legitimate new turn must not be poisoned.
- After lost-ACK, use independent typed readback before considering any resumption; no blind retry, no repeated handoff popup.
- No automatic restoration/deletion of historical Kanban or actual user data.

## P0 status / 8 product acceptance gates

- P0-1 intent/TaskRun separation: historical work exists in #75/#79/#83. **Our additional missing/partial binding patch is published; test verification pending**.
- P0-2 persistent SUPERSEDED: **OPEN, exact authority invalidator/emitting call site unknown**.
- P0-3 handoff-to-UI, consumed approval, independent readback, no replay: **OPEN, not end-to-end qualified**.
- P0-4 real Windows integration: **BLOCKED by remote desktop responsiveness**, no dogfood evidence.

All eight MVP acceptance items are **UNVERIFIED** against this new exact HEAD:
1. 10 simple commands → no phantom cards.
2. One durable request → single task and legitimate CAS run claim.
3. Five Browser prompts including close/reopen → no persistent SUPERSEDED.
4. Two chats → separate run/operation/controller authority.
5. Lost-ACK → one external effect verified by independent readback, no replay.
6. Take Control → 409; Release → new authorized work.
7. Restart → no stale lease revival, clean new work.
8. Exact-head Python/TS/Electron native regression, CI and Windows dogfood.

## Directed source trace (GitHub-only, not runtime proof)

Current branch `workstation/batch_detection.py::prepare_mutation` checks **every non-compiled mutable tool** (not only Browser tools) against the agent's `_canonical_work_task_id` and `_canonical_work_run_id`. If a task remains pinned from a superseded turn, `classify_run_authority` can fence unrelated `terminal` / `write_file` operations before I/O. This is a concrete path consistent with the incident's cross-tool symptoms, **not proof that it was entered in the reported session**.

The turn admission path `agent/turn_tool_round.py` admits whole batches and uses `scoped_execution` from `agent/scoped_execution.py`. Separately, `run_agent.py::_execute_tool_calls` can admit intervention decisions. Need inspect the actual Workstation registration and invocation of `workstation/work_intent.py::prepare_turn_work`, including turn boundary and the clearing of obsolete agent fields; instrument **which fence produced the user-visible SUPERSEDED** before patching. There is no evidence yet that `agent/scoped_execution.py` itself is responsible.

## Immediate next step — do this before writing more code

1. Restore responsiveness of authorized Desktop Commander computer; `list_devices` saying Online is not enough. Confirm with `ping`, then run a read-only `git status --short`, `git rev-parse HEAD`, and `git worktree list --porcelain` in `C:\Github\hermes-agent`.
2. Create a new isolated Windows worktree for `origin/fix/mvp-kanban-browser-superseded-20261012` (or inspect an existing exact-branch worktree first); keep the root and #83 worktree untouched. Read root `AGENTS.md`, `workstation/AGENTS.md` and `workstation/context/README.md`; execute required upstream-first gate as feasible and record any blocked qualification.
3. Reproduce RED on the earlier test-only commit `0cdfe4b6...` in a temporary worktree (the test includes an isolated temp Kanban DB), then GREEN on latest branch via `pytest -q workstation/tests/test_browser_session_run_isolation_p0.py`. If test fails due fixture/schema issues, repair with minimal test/production changes; run adjacent PR #83 suites. No unverified retroactive TDD claim.
4. Reproduce the **actual** five-turn Google/search/YouTube Browser session, including timeout-after-dispatch, Browser close/reopen, two chat sessions, and a nonbrowser tool. Trace session/turn/epoch, task/run/browser ID, operation ID, fence emitter, first invalidation and controller lifecycle, excluding secrets. Prior incident `abrir-google-20261012.json` may be available in dogfood records. The observed error also affected terminal and write_file, therefore test agent-level cancellation/fencing, not Browser alone.
5. Write a failing test at the first **confirmed** authority ownership divergence, fix minimal cause, and prove RED→GREEN plus legitimate stale owner denial.
6. Complete minimal handoff→UI→single approval consumption→independent readback→TaskRun continuation without replay. Preserve legacy contracts, no new orchestration engine.
7. Run real isolated Windows Electron Chromium, 409 Take/Release, cold restart and 8 MVP gates. Confirm CI for the exact SHA; do not claim qualified for earlier SHA or mere mocks.
8. Update this checkpoint, `workstation/ROADMAP.md`, Known Issues / decisions and engineering journal only as warranted by verified changes. Push incremental commits to PR #88 and maintain its stacked base without merging main.

## Next-session mandatory handoff

If all eight gates are not proven, send one **standalone, user-copyable continuation prompt in Portuguese** with exact latest worktree/branch/HEAD/PR, changed paths, tests with actual counts, confirmed vs hypothetical root cause, exact next failing test and source symbol, ordered remaining steps, authority invariants, no merge without approval, and the same recursive handoff requirement. Never say to 'continue from the previous conversation'. Do not promise future background work.
