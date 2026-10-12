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

## 2026-10-12 continuation — source-confirmed absent-correlation run reuse

**New confirmed code-level vulnerability, NOT confirmed as the emitter of the user-reported SUPERSEDED error:**

1. `agent/turn_ingress.py::TurnIngress.correlation_id` defaults to `None`; `agent/conversation_loop.py` constructs the fallback trusted TurnIngress without specifying a correlation ID.
2. `workstation/integrations/hermes/turn_admission.py::workstation_turn_admission` passes `ingress.correlation_id` into the MessageEnvelope, and invokes `workstation/work_intent.py::prepare_turn_work`.
3. The old `prepare_turn_work` compared `prior_turn_id == envelope.correlation_id` and `pinned_turn == envelope.correlation_id` without requiring a nonempty correlation value. Two unrelated turns with both IDs `None` could satisfy a same-turn authority guard if the old canonical task/run, session and objective remained equal, permitting accidental run reuse.
4. `agent/turn_tool_round.py::run_tool_round` invokes full tool admission and `workstation.integrations.hermes.scoped_execution`; `workstation/integrations/hermes/tool_observer.py::workstation_pre_dispatch_hook` invokes `prepare_mutation` on final authorized args. Its canonical TaskRun fence applies to non-Browser mutating tools too. **This establishes a plausible cross-tool propagation route, not definitive production attribution.**

Changes published to PR #88:

- Test-only precursor `f46454706af6a2fd7e9ef572e8181e8b08291069`: `workstation/tests/test_p0_turn_correlation_authority.py` exercises (a) repeated point action with missing correlation and (b) new durable request with identical text but absent correlation.
- Minimal source patch `a1b75c0bf3780c2e67fd8a96ba336b4ebdc5d7e4`: `workstation/work_intent.py::prepare_turn_work` requires a truthy incoming `envelope.correlation_id` for **both** existing TaskRun continuation guards; a true same-turn nonempty correlation can still match, and a missing one fails closed.
- Regression follow-up `082ee7df08be167679c76f8841fad0b207b3d92b`: verifies a correctly correlated, still-running canonical TaskRun remains reusable. Do not claim any RED or GREEN run; none could execute with Windows offline.

**Execution and qualification remain blocked**. In this follow-up session, Desktop Commander once again listed `DESKTOP-3NA47UH` as Online, but `ping` request `fb75c8c0-574d-4d97-b5f0-46d5cbd13c37` ultimately failed with `Timeout - no response from device`. Direct container `git ls-remote` also failed due missing DNS/network, so local cloning and actual pytest on the new commits were impossible. The repository Windows state/worktrees remain unverified. All eight full MVP acceptance gates remain unverified. Keep PR DRAFT and do not merge.

**First required test command once remote execution is available** (after separate clean worktrees for the commit under test and the latest branch, and repository-approved Python venv setup):
`pytest -q workstation/tests/test_p0_turn_correlation_authority.py workstation/tests/test_browser_session_run_isolation_p0.py`.

Prove RED for the first two absent-correlation tests at `f46454706...` (before source patch), then GREEN for all three at current head. Run adjacent WorkIntent, smart task admission, Kanban concurrent claim and Electron owner regression. Fix only actual failure output; be prepared to revise the source patch if legit callers relied on untracked correlation, using a trusted unique turn ID rather than weakening the guard.

**Next true SUPERSEDED reproduction remains P0-2**: trace full Google/search → timeout after dispatch → new YouTube request → terminal/write_file, distinguishing a cancelled turn owner vs. stale TaskRun vs. native controller. Do not pretend this source-level correction resolves the incident without real evidence.

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


## 2026-10-12 — Windows execution / PR #88 continuation

**This section supersedes the older 'Windows unavailable / zero tests' status for the new PR #88 worktree. Earlier records remain historical.**

### Device, worktree and source state

- Remote Desktop Commander device `DESKTOP-3NA47UH` answered real ping and shell commands.
- Root checkout `C:\Github\hermes-agent` remains on `fix/hermes-oneclick-lock-startup-20261011@9fffa7f3ffcc2c50774654c271fe25e92ce459e8`, with numerous user-owned tracked/untracked changes. **Root not edited.**
- Historical #83 isolated worktree verified at `C:\Github\hermes-agent-kanban-browser-authority-20261012@22498a09db0802c06125f5a5ec4cb5039da9b98f`, untouched.
- Clean isolated PR #88 worktree created: `C:\Github\hermes-agent-mvp-kanban-browser-superseded-20261012`. Branch `fix/mvp-kanban-browser-superseded-20261012`; remote fetched at `c2dc3ef13c8c67d5d23ee5c2bfe8d0de91dbb8eb`.
- Python interpreter with pytest: `C:\Github\hermes-agent-p0-kanban-effects\.venv\Scripts\python.exe` (pytest 9.1.1). Root `.venv` has no pytest.
- Test `HERMES_HOME` directories under `C:\Temp\hermes-mvp-browser88-*`, never actual user home. Ignored local directory junctions from new worktree to preinstalled root/desktop `node_modules`, no source changes.
- Local `git merge-base HEAD upstream/main` originally returned `66605471e9f0b0832abbefaf625ce08e948ca540`. This is not a full current upstream-first qualification; no upstream sync/merge or H079 release certification was performed.

### Verified RED→GREEN and code regression

- **RED genuinely reproduced** on detached temporary worktree `C:\Temp\hermes-pr88-red-f464` at test-only `f46454706af6a2fd7e9ef572e8181e8b08291069`:
  `pytest -q workstation/tests/test_p0_turn_correlation_authority.py` → **2 failed in 4.56s**, both due to reuse of a prior TaskRun when correlation was absent.
- **GREEN at PR #88 code**: `pytest -q workstation/tests/test_p0_turn_correlation_authority.py workstation/tests/test_browser_session_run_isolation_p0.py` → **12 passed in 6.92s**.
- Larger initial Python regression exposed **two pre-existing test-fixture assumptions**, not two reasons to relax the runtime: `test_dispatch_forwards_kanban_and_run_identities` and `test_adaptive_browser_loop_uses_one_task_despite_repeatability` in `test_browser_workstation_route.py` used invented `card-123/run-456` and `card-test/run-test` bindings. Their old expectations now correctly fail closed as STALE_RUN.
- Replaced those test-only bindings with real canonical SQLite task/run claims in isolated temporary HERMES_HOME; preserved tested sessionless legacy env binding and multi-action BrowserTask behavior. Fixed three existing test-file Ruff hook warnings (unused noqa twice and unused server binding).
- New test-only commit **`a942a14dd577619913a66c3f040abb8992a01dff`**, pushed to PR #88. No production authority change in this commit. Pre-commit lint: PASS.
- **Full selected Python regression on code SHA `a942a14dd577`: 88 passed in 21.69s, 0 failed, exit 0.** Files: `test_p0_turn_correlation_authority.py`, `test_browser_session_run_isolation_p0.py`, `test_smart_task_admission.py`, `test_p0_kanban_intent_semantics.py`, `test_p0_concurrent_task_admission.py`, `test_p0_multiprocess_task_admission.py`, `test_p0_force_task_authority.py`, `test_p0_completion_proof_boundary.py`, `test_denied_mutation_handoff_recovery.py`, `test_p0_handoff_concurrent_owner.py`, `test_p0_uncertain_mutation_readback.py`, `test_browser_workstation_route.py`, `test_kanban_journal.py`.

### Real source-built native Electron + Chromium

- In isolated PR #88 worktree, `apps/desktop/node scripts/build.mjs`: **exit 0**, build stamp `a942a14dd577` (source-built, not Windows packaged installer).
- Real Electron + Chromium Playwright P0 suite, with `HERMES_DESKTOP_PYTHON=C:\Github\hermes-agent-p0-kanban-effects\.venv\Scripts\python.exe` and isolated HERMES_HOME:
  `playwright test workstation-headless-load --grep P0: --reporter=line` → **4 passed in 1.4m, exit 0**.
  Covered real two-session native Browser takeover / HTTP 409 / separate B session / release and resumption; actual UI Take Control and Release Control buttons; native mutation readback after lost controller ACK; human lease recovery across cold Electron restart.
- Separate H013 source-built native smoke:
  `playwright test workstation-headless-load --grep keeps.four.native.Browser.tasks --reporter=line` → **1 passed in 23.6s, exit 0**, four BrowserTasks independently aligned across controller and renderer IPC.
- These are **real Electron+Chromium with mock inference and deterministic local pages**. They do NOT certify a packaged Windows installer, five successive real agent prompts, native human approval→typed readback→TaskRun continuation, or failure recovery of the user-reported session.
- PR #88 code SHA `a942a14dd577619913a66c3f040abb8992a01dff` returned **zero combined statuses and zero PR-triggered GitHub workflow runs**. Exact-HEAD CI is missing.

### Evidence from user dogfood incident

Read-only inspection of the local original `workstation/dogfood/dados/Sessões Hermes/abrir-google-20261012.json`, 66 messages (no private data copied to commits), confirms:
- First user-visible `Error executing tool 'browser_exec': SUPERSEDED` at message #23 following a post-dispatch navigation timeout.
- Later `browser_navigate`, `terminal`, `write_file`, and generic `tool_call` return `SUPERSEDED`, while some browser snapshots were earlier recoverable.
- The exported tool results contain only wrapped exception text (e.g., `Error executing tool 'terminal': SUPERSEDED`), **not a Python stack trace, emitting module or ownership-invalidation reason**.
- This narrows focus to shared agent/session/tool execution authority; it does not prove the exact emitter. Do not promote the absent-turn-correlation fix to a fully proven production remedy without live reproduction.
- Temporary privacy-sanitizing diagnostics located at `C:\Temp\mvp88-log-parse.py` and `C:\Temp\mvp88-superceded-context.py`, outside Git.

### Open gates / next exact work

- **P0-1 partially validated**: concrete authority bugs are regression-tested and 88 Python tests pass, but ten real UI prompts/one card CAS acceptance is not proven as product workflow.
- **P0-2 OPEN**: reproduce five successive **real agent** Google/search/YouTube prompts plus timeout, chat switch, Browser open/close and unrelated terminal/write_file. Trace the exact emitting exception owner/class, invalidation event, session/turn correlation, TaskRun and BrowserTask owner. Run a failing deterministic regression **before** further production changes.
- **P0-3 OPEN**: real native human approval via renderer/IPC, one-time handoff consumption, independent *typed* readback and resumed actual TaskRun without repeating a prior mutation. Existing native 409 / lost-ACK tests are components, not this integrated workflow.
- **P0-4 PARTIAL**: source-built native tests PASSED (4+1). Exact-HEAD GitHub CI, packaged Windows qualification and original multi-prompt dogfood remain missing.
- **Eight full MVP product acceptance gates: NONE fully proven yet**. Do not claim MVP QUALIFIED, release, or merge.
- Documentation-only commit containing this section will move HEAD past `a942a14dd577`; next session MUST refresh/confirm actual head and distinguish code SHA from documentation SHA. Re-run exact-HEAD acceptance when qualifying.
- Follow upstream-first H-079 pin/baseline checks; no unjustified upstream merge or auto-restore of historical Kanban. No merged branch or actual user data mutation.

### Mandatory next handoff

Start from the updated PR #88 HEAD, preserve the dirty root/other agents, continue with the exact incident reproduction and native handoff implementation, and return a new standalone recursive Portuguese continuation prompt with explicit tested vs untested gates if interrupted.


## 2026-10-12 — PR #88 follow-up: five AIAgent turns, CI and packaging blockers

**Status: MVP PARTIALLY QUALIFIED; original persistent SUPERSEDED root cause and product acceptance are NOT proven. This section supersedes any previous assertion that the remote device remains unresponsive.**

### Identity / published code

- Working branch and isolated Windows worktree unchanged: `fix/mvp-kanban-browser-superseded-20261012`, `C:\Github\hermes-agent-mvp-kanban-browser-superseded-20261012`; stacked PR #88 over draft PR #83; never merge main without owner approval.
- Code/test commit **`bd4c826460e1219c78d67a64a8c27c69757af9fe`**, pushed successfully to GitHub. Contains only new isolated test `workstation/tests/test_p0_browser_five_turn_authority.py`; **no production runtime modifications**.
- Previous source-built Python 88/88 and native Electron/Chromium 5/5 remain prior evidences from `a942a14dd577`, not fresh exact-head qualifications.
- No root checkout or existing Kanban data touched. All new test DBs are `tmp_path` homes. No uploaded real session content.

### Five-turn real agent lifecycle, deterministic physical Browser mock

- New test drives **real `AIAgent.run_conversation()` five times on a single agent**, Workstation trusted turn admission, conversation loop, tool dispatch middleware, and Browser routing. Inference responses are scripted and `_request_json` is fake local physical controller (NOT a real Chromium browser). `terminal` handler returns a safe fake value, but goes through the agent executor. Calls: open Google, Browser snapshot, open YouTube, Browser snapshot, independent terminal.
- Parametrized cases: (a) all acknowledgments normal; (b) controlled `TimeoutError` raised **after simulated YouTube navigation state changed** (lost ACK). Both ensure exactly two navigation dispatches, no automatic duplicate mutation, independent terminal still runs, no `SUPERSEDED` in tool receipts, and no user-conversation Kanban card.
- `agent.skip_background_review=True` is essential for harness isolation. Before setting it, a prior parametrized invocation launched **an unrelated background skill review** with task body beginning `Review the conversation above and update the skill library`; that task appeared in the next fixture and was initially mistaken as a phantom user Kanban task. **Root cause of the test contamination: background review worker, NOT a proven user Kanban regression.** On isolated invocation with lost ACK alone there was no card. Do not make production changes based on this fixture artifact.
- Final new test, both parameters: **2 passed in 8.19s**, exit 0; lint Ruff PASS.
- Combined focused selection `test_p0_browser_five_turn_authority.py`, `test_p0_turn_correlation_authority.py`, `test_browser_session_run_isolation_p0.py`: **14 passed in 14.56s**, exit 0 (before final strengthened assertions); last two-param post-assertion rerun passed.
- **Limitation:** This rules out some straightforward same-agent contamination under scripted tool/I/O, but it does **not** reproduce the reported literal `SUPERSEDED`, native Electron controller timeout, provider callbacks, chat-switch cancellation or multi-session restart. The error source remains unknown.

### GitHub CI blocker now proven, not just 'no status'

- Read existing `.github/workflows/workstation-ci.yml` and `.github/workflows/workstation-browser-windows.yml`; **both explicitly support `workflow_dispatch`**, and Windows workflow verifies the exact candidate SHA and contains build/packaged GUI, soak and native Browser E2E jobs.
- Attempted `gh workflow run workstation-ci.yml -R kevynlucasprofissional-stack/hermes-agent --ref fix/mvp-kanban-browser-superseded-20261012` and same for `workstation-browser-windows.yml` after pushing `bd4c826460`.
- **Both requests failed HTTP 422: `Actions has been disabled for this repository`.** No CI jobs were started and no results exist. **DO NOT enable Actions or relax repository security settings without explicit owner approval.** Owner must decide whether to enable Actions; remote CI is categorically blocked until then.

### Packaged Windows candidate blocker

- Tried nonpublishing local packaging in isolated worktree: `npm run builder --workspace apps/desktop -- --dir --publish never`.
- **EXIT 1** at `apps/desktop/scripts/prepare-packaging-tools.mjs:26`: installed `app-builder-lib` is not the source lock-pinned package. This branch's `node_modules` are ignored directory junctions to the separately managed dirty root checkout; its dependencies are not a valid pinned install for packaged candidate.
- DO NOT invoke `npm ci` against the shared junctions: doing so could destructively modify the root's installed packages and affect other agents. Resolve in a **new isolated dependency directory** after examining actual Node lock and disk space; alternatively rely on CI once Actions is explicitly authorized. Existing source-built Electron E2E proof is unchanged.

### Remaining exact next engineering steps

1. Continue P0-2: capture **the first actual `SUPERSEDED` stack/emitter and losing authority** from a safe reproducible native Browser/controller + real-agent multi-turn session. The archived 66-message dogfood transcript displays only wrapped `Error executing tool ... SUPERSEDED`, without a stack. Do not infer its emitter from matching names or apply speculative runtime patches.
2. Exercise genuine two-chat conversation switching after a dispatched-but-unacknowledged native navigation, Browser close/reopen and unrelated mutating tool in an isolated profile; compare against passing agent harness; instrument per-boundary identifiers only, no credentials or private payloads.
3. Complete P0-3 human renderer approval consumed once → independent typed readback → continuation on validated TaskRun, with no replay. Existing synthetic and partial native tests are NOT end-to-end integrated proof.
4. Finish 10 on-screen point actions / one durable task CAS, packaged Windows dogfood, and exact-SHA CI **only when available**. All 8 full acceptance criteria remain incompletely proven. P0-4 partly covered by existing local source-built Electron tests.
5. Preserve worktree status, recheck actual branch/remote HEAD, update journal if warranted. If interrupted, return a complete self-contained Portuguese continuation prompt with current SHA, blockers, exact next test, and recursive continuation requirement.
