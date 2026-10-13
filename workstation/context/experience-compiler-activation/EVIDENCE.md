# Evidence — Hermes Experience Compiler activation, 2026-10-12
## Verified baseline
- GitHub PR #82: open, draft, not merged; original head ec739ce8a6ed1f746299db992342cb879738d93d, 17 files at initial inspection.
- Local isolated branch clean before session edits. Main checkout dirty on unrelated files; untouched.
- H-079 selected upstream pin ancestor (git merge-base --is-ancestor exit 0), upstream reference ahead/behind 963/245; exact-head release qualification outstanding.
- GitHub fetch_commit_workflow_runs(head of PR #82) returned empty list, **not evidence of green CI**.

## EC-01 RED
Command (worktree PowerShell): `$env:PYTHONPATH='C:\Github\hermes-agent\.venv\Lib\site-packages;'+(Get-Location).Path; uvx --offline pytest -q -o addopts='' workstation/tests/test_h080b_native_browser_experience_loop.py -k 'test_real_browser_readback_validates_and_promotes_compiled_capability and True' --tb=short`
Result: FAIL, NEEDS_REASONING, provider called 3 times, plus EvidenceRef JSON serialization warnings. Trace: .ec_h080b_red.log untracked. In a temporary diagnostic run with fresh-command goal changed to trello.com (then reverted), H-080B still FAIL with no_certifiable_capability_found / WAKE_LLM. Diagnostic isolated route data: local registry=1, reloaded registry=1, PROMOTED healthy, preconditions=[], goal_coverage=True, effects_contained=True, verifier_sufficiency=(True,()). Exact router runtime rejection still unknown; do not weaken authority. Raw .ec_h080b_checks.log and .ec_h080b_diag.log are scratch, not for commit. No production routing fix claimed.

## EC-02 TDD
- Initial RED: two replay tests FAIL, replay returned passed=True for unknown primitive and for ignored read_file.
- After first fail-closed patch: `uvx --offline pytest -q -o addopts='' workstation/tests/test_local_canary_replay_fail_closed.py workstation/tests/test_local_product_validation_provider.py --tb=short`: 7 PASS.
- Added independent RED: verifier accepted candidate whose path was ../../escape.txt, and positive evidence lacked candidate_id (2 FAIL / 3 PASS).
- After positive replay/binding/semantic readback patch and content-hashed evidence: same focused two-file command 9 PASS in 1.43s.
- Broader regression on files test_online_compilability_safety.py, test_online_compilability_monitor.py, test_hierarchical_causal_promotion.py, test_local_product_validation_provider.py, test_local_canary_replay_fail_closed.py: **60 passed, 1 skipped in 157.28s**, exit 0. Output .ec_canary_regression.log is temporary and must not be committed.
- This does not prove live Laya, DIRECT or full Electron H-082.

Status vocabulary: PASS, FAIL, SKIPPED, NOT RUN, BLOCKED, INCONCLUSIVE. Never infer cost/tokens from role=tool count.

## Commit qualification / lint
- Fresh after import cleanup: two-file canary pytest **9 passed in 3.98s**; `ruff check --select F` on lifecycle + new test PASS; `compileall` PASS; `git diff --check` PASS.
- Native Lefthook pre-commit attempted and FAILED with **32 Ruff modernization UP errors** in the edited legacy lifecycle.py (30 autofixable, 2 unsafe). These checks are **not green**. The unrelated modernization debt is deferred and blocks release qualification; staging isolated security remediation for draft review may require explicit recorded hook bypass. No merge without exact-head CI.

## Follow-up lint cleanup after first failed pre-commit
- Applied Ruff safe automated UP modernization in the already edited lifecycle.py only; removed deprecated/unused imports. This is mechanical typing and datetime.UTC modernization, not a behavior change. `uvx --offline ruff check --select F,UP workstation/experience_compiler/lifecycle.py workstation/tests/test_local_canary_replay_fail_closed.py`: PASS. Fresh narrow pytest: 9 passed in 1.79s (exit 0). Final broad regression `uvx --offline pytest -q -o addopts='' workstation/tests/test_online_compilability_safety.py workstation/tests/test_online_compilability_monitor.py workstation/tests/test_hierarchical_causal_promotion.py workstation/tests/test_local_product_validation_provider.py workstation/tests/test_local_canary_replay_fail_closed.py --tb=short`: **60 passed, 1 skipped in 109.59s** (exit 0), log .ec_canary_regression_final.log (untracked). A second native lefthook commit attempt must still confirm the hook state before describing it as passing.

## EC-01 detailed root cause and test-first sequence (2026-10-12)
- First H-080B original regression FAIL: NEEDS_REASONING, 3 provider calls. The temporary host-matched test still FAIL: no_certifiable_capability_found.
- Temporary spy on live CapabilityRouter.route (reverted before commit) captured promoted healthy cap; actual OperationIntent target native_browser but goal EQ(url,https://trello.com/), footprint SET(url,..) vs promoted formal host/page_family/recovery_state. target=True, pre=True, goal=False, effect=False, auth=True, verifier=(True,()). This is an **intent IR mismatch**, not absence of a registry entry.
- New test contract RED: native operation goal incorrectly used url. Source workstation/work_intent.py adapted to native Browser's postcondition IR; old non-browser creative commands unaffected.
- Initial follow-on targeted E2E: new TaskRun routing passed but dispatcher produced ASK_HUMAN after unexpected learned capability parameter. TaskCompiler._execute_capability forwards request.inputs, and generalization.validate_inputs rejects undeclared url key for fixed zero-input capability.
- Added parameter regression RED; fixed allowlisted native command by omitting extra inputs because exact destination is already bound by typed goal/effects and compiled static step. TDD GREEN: native intent + existing current command tests 6 passed in 24.79s; targeted H-080B [False,True] 2 passed, 24 deselected in 24.88s (exit 0).
- Global `effect_contained` is path-based for SET budgets, even with different values; do NOT casually change this contract. The new intent requires exact host/page/recovery goal coverage (independent of effect containment), and tests enforce wrong-host mismatch. Any broad policy hardening is a separate reviewed scope.
- Broader four-file regression launched (H-080B, current command existing/new, e2e operational resolution); see .ec01_regression.log for final status. Not evidence of actual live Laya/real browser dogfood.

## EC-01 final regression (verified in continuation)
- Worktree `.ec01_regression.log` concludes: `42 passed in 175.32s` for H-080B, current command existing/new and E2E operational resolution. This is integration regression evidence, not live provider/production Laya certification.
- `uvx --offline ruff check --select F,UP workstation/work_intent.py workstation/tests/test_current_command_resolution.py workstation/tests/test_current_command_native_intent_contract.py`: `All checks passed!` (exit 0).
- `git diff --check`: exit 0. Raw scratch log remains untracked and excluded from commit.

## EC-03 and EC-07 continued RED/GREEN — 2026-10-12
- EC-03: test_legacy_cached_owner_without_taskrun_binding_is_not_reused RED (unexpected identical legacy owner); replaced implicit cache fallback with explicit _bound_task_run check. Fresh 5/5 owner factory unittest PASS (0.077s). Production authority/lease/browser restart E2E still unqualified.
- EC-07: EvidenceRef object in emit_event.evidence_refs RED: sqlite sink logged Object of type EvidenceRef is not JSON serializable; regression asserted URI-only storage and no summary leak. Code projects canonical EvidenceRef.uri before event construction; 11/11 telemetry+operational tests PASS; broader owner+telemetry+intent suite 5 unittest PASS + 13 pytest PASS (2.86s). Ruff F,UP PASS; diff check PASS.
- Extended test_system1_telemetry.py has 1 FAIL from ModuleNotFoundError: No module named laya (12 passed, 1 failed); not counted as green. Real Laya, H-079/H-081/H-082, Electron, DIRECT and exact-HEAD CI remain unqualified.

## Final verification after published EC-03/EC-07 (2026-10-12)
- GitHub PR #82 exact code HEAD f710a6b46b034ac37c953869877f795b8672a9b1 verified open/DRAFT/unmerged. Pushed commits 38dc4b52a1 and f710a6b46b with native Lefthook lint hooks PASS. GitHub fetch_commit_workflow_runs at f710a6 returned []: CI NOT QUALIFIED.
- Fresh H080B paired test on current code: 2 passed, 24 deselected in 37.92s, exit 0, log .ec_h080b_final_after_owner.log (UNTRACKED, DO NOT COMMIT).
- Source review for EC-04: tool_observer.py yields observed/uncertain only; operational_kernel.py capture("verified_success", verification) already notifies online monitor; kanban.py accepts final run after completion; run_adoption.py records per-item readback evidence. New mid-run acceptance requires owner-bound proof, not raw tool result; NOT IMPLEMENTED by this review.
- Laya is pinned in pyproject.toml as version 0.3.23; package source at workstation/third_party/laya. Missing import in test runtime still unqualified; do not call full Laya E2E PASS.

## 2026-10-12 — EC-03/04 RED-GREEN / Laya local source
- RED: browser_navigate yielded [] effects and accepted cross-host URL. GREEN: 3 browser effects/admission tests PASS with HTTPS scoped CALL and required owner readback; missing effect budget/lease denied.
- RED: cached owner still dispatched/readback after TaskRun swap. GREEN: 7 unittest factory tests PASS with call-time task/run guard.
- RED: capture_progressive accepted VERIFIED_SUCCESS without persisted proof, wrong run, canonical proof without underlying evidence and canonical laundering of failed/alien readback. GREEN: focused progressive tests 10 PASS, original capture fixture switched to real persisted owner receipt. Kernel carries canonical verification proof reference rather than unbound evidence.
- RED: operator cancellation between snapshot and work item start caused 2 extra tool calls (8 vs 6). GREEN: happy-path adoption plus 2 lease-race windows, 3 tests PASS after live item-boundary and pre-step authority checks.
- Root cause of 6 early no_canonical_snapshot regression failures: injected fixture owner missing _bound_task_run and was correctly rejected by production cache; fixture now binds real task/run explicitly. Isolated happy-path rerun 1 PASS; previous full suite before final race tests 49 PASS in 168.79s, exit 0.
- H080B pair after EC-04 proof hardening: 2 PASS/24 deselected, exit 0, 43.42s.
- Laya source 0.3.23 import PASS; verify_laya_provenance PASS, source_SHA and lock_SHA both 4aa6761be8173de4ce6d92c31b3e40b6eaf59a7c; focused System-1 telemetry 2 PASS (26.29s). This is not live checkpoint qualification.
- Ruff full configured rules on edited files PASS, git diff --check PASS; owner factory 7 PASS. Complete final suite still subject to latest execution result.

## EC-03/EC-04 last fresh qualification
- Command: uvx --offline pytest -q -o addopts='' workstation/tests/test_online_compilability_safety.py workstation/tests/test_progressive_verified_gate.py workstation/tests/test_progressive_experience_capture.py workstation/tests/test_run_local_browser_effect_authority.py --tb=short
- Result: 51 passed in 115.40s, exit 0, log .ec04_final_full_suite.log (untracked).
- Owner: python -m unittest -q workstation.tests.test_run_local_owner_factory: Ran 7, OK, exit 0.
- Ruff default configured rules: All checks passed. git diff --check exit 0.
- Both lease race tests after fix and canonical progress proof checks are included. No exact-head CI, native Browser production, Laya DIRECT, or user dogfood certification.

## Committed artifacts
- EC-03 source+tests: git commit 065acd189b, Lefthook precommit lint PASS. First commit attempt blocked by 2 legacy RUF059 unused unpacked variables in test_online_compilability_safety.py; repaired by naming unused values with underscore and retry succeeded without bypass.
- EC-04 source+tests: git commit 3b9f18ac51528da329fb1fdfdaba5f98893b4e2a, Lefthook precommit lint PASS.
- No destructive git reset/clean. Local .ec*.log scratch excluded from commits.

## 2026-10-12 — Native intent and progressive owner provenance
- RED: new native named-site test found CALL(browser.navigate,trello.com) outside existing SET-only effect budget, failed 1. GREEN: 10 targeted tests PASS in 25.13s; native H-080B pair 2 PASS in 39.35s. Native hook approved local code commit 40f8f82a66.
- RED: progressive source rejected operation_family/target_family labels; GREEN: 21 focused tests PASS (16.18s) after schema mapping.
- RED: capture_progressive had no state_before and no causal delta; GREEN: 25 focused tests PASS (20.56s) after explicit state transition support, but critical review revealed forged prestate risk.
- RED: arbitrary caller state_before without owner witness incorrectly generated changed exists False->True. GREEN: require separately persisted owner pre-readback proof matching task/run/operation and state; 3 targeted positive/negative cases PASS, including wrong-run, wrong-value, missing read_before_write. Independent real production prestate producer NOT yet delivered.
- Updated Laya tests: 10 PASS, 1 SKIPPED, .ec05_vendored_laya_regression.log; real checkpoint not tested.
- Full security suite .ec04_metadata_full_safety.log: 54 PASS (175.57s) before latest prestate witness restriction. Native H080B after metadata 2 PASS, 24 deselected.
- Latest prestate full .ec04_prestate_final_safety.log and native .ec04_prestate_final_h080b.log running; record exact result before release.

## Final verified outputs — 2026-10-12
- `uvx --offline pytest -q -o addopts='' workstation/tests/test_online_compilability_safety.py workstation/tests/test_progressive_verified_gate.py workstation/tests/test_progressive_experience_capture.py workstation/tests/test_run_local_browser_effect_authority.py --tb=short`: **56 passed in 221.83s**, exit 0, scratch log `.ec04_prestate_final_safety.log`.
- H080B paired: `test_real_browser_readback_validates_and_promotes_compiled_capability` **2 passed, 24 deselected in 73.59s**, exit 0, scratch log `.ec04_prestate_final_h080b.log`.
- Owner factory: **7 unit tests PASS**. Laya vendor/real-contract/routing: **10 passed 1 skipped**, source pinned 0.3.23. Ruff current edited files PASS.
- Native hooks: commit 40f8f82a66 PASS; commit c3f87a84860615f2086f17191921605068c6932c PASS. Do not interpret absence of PR-head CI runs as green.

## 2026-10-12 — Owner-created witnessed filesystem proof
- RED: 2 real OperationalKernel/DurableTaskStore failures: filesystem precondition observes wrong path due ignored base_dir, and no prestate receipt emitted. GREEN: both pass, original first green 2 tests and 29 targeted tests covering existing compiler/kernel after authority guard.
- RED: learned durable filesystem effect executes with no primitive_admission (1 failure). GREEN: missing admission is denied, original 6 tests after change pass.
- RED: operator cancels running durable plan after prestate but before dispatch (1 failure). GREEN: second owner admission and canonical plan/item check; 10/10 owner tests PASS.
- RED: real fs_hash verifier VERIFIED but corpus query during still-open two-item TaskRun returns [] (1 failure). GREEN: persist hash-only independent readback artifact linked to verification receipt; direct test PASS.
- RED: prestate resource A plus poststate fs_hash resource B wrongly captures VERIFIED_SUCCESS (1 failure). GREEN: verified post-readback resource must match witnessed prestate resource; 35 focused tests PASS in 38.93s, Ruff PASS.
- Earlier full EC-03/04 safety 65 PASS (169.88s) before later postreadback binding change. New exact final full regression .ec04_prod_full_safety_final.log running (record outcome when complete), H-080B .ec04_prod_h080b_final.log running. Current owner 7 unittest PASS; ruff and git diff --check PASS.
- Important: these prove a real intermediate hash-verified sample before workplan completion but NOT Laya decision, candidate, adoption, DIRECT or VERIFIED_REUSE.

## Final EC-04 producer tests — exact outcomes
- Command: uvx --offline pytest -q -o addopts='' workstation/tests/test_ec04_production_prestate.py workstation/tests/test_online_compilability_safety.py workstation/tests/test_progressive_verified_gate.py workstation/tests/test_progressive_experience_capture.py workstation/tests/test_run_local_browser_effect_authority.py --tb=short.
- Result **68 passed in 207.98s**, exit 0, .ec04_prod_full_safety_final.log. H080B original 2 PASS/24 deselected in 27.19s, .ec04_prod_h080b_final.log. Separate 35 targeted PASS, native owner factory 7 PASS, Ruff PASS.
- No measured provider/token savings, no live Laya checkpoint or DIRECT verification, no exact-head Actions run. Release HOLD.

## Commit qualification
- d3c171c3ef78efb2c3c025af00938bdd6694ddc9: tested/committed code (4 files). Native Lefthook PASS on second attempt, no LEFTHOOK bypass. First hook failed RUF059 36 unused unpackings in new test; fixed only in test_ec04_production_prestate.py by Ruff --select RUF059 --fix --unsafe-fixes, inspected patch, narrow 23 PASS after correction.
