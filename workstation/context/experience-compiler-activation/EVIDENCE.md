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
