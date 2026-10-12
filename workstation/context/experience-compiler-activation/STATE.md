# Current state — 2026-10-12 (activation session)
## Source of truth / checkout
- GitHub: kevynlucasprofissional-stack/hermes-agent; PR #82 open, DRAFT, unmerged as verified this session.
- Branch: feat/experience-compiler-real-reuse-20261011; worktree C:\Github\hermes-agent\.worktrees\experience-compiler-p0-p2-20261011.
- Original HEAD: ec739ce8a6ed1f746299db992342cb879738d93d. **Run git rev-parse HEAD to obtain newer HEAD after this ledger commits; do not trust the old value.**
- Downstream main / GitHub main SHA: a2b56db1bc9e0b5acf48d94fa86a9844a1005842.
- Pin 66605471e9f0b0832abbefaf625ce08e948ca540 is ancestor of main; local upstream/main observed 835c3dd038d903182a66ecc45e34bf5e0de65f00, main...upstream/main 963 ahead / 245 behind (not refreshed, explicitly historic local ref).
- Main checkout C:\Github\hermes-agent on fix/hermes-oneclick-lock-startup-20261011 HEAD 9fffa7f3ffcc; has many existing modified Electron files and local dogfood; intentionally untouched.
- H-079 PASS_WITH_AUTHORIZATION appears at engineering-journal/CURRENT.md:5678 but was scoped to an operational-speed lane; does **not** certify baseline CI, prevent gate checks or authorize merge.
- No PR #82 workflow run found by GitHub tool at original SHA; final exact-HEAD gates NOT QUALIFIED.

## Work executed in this session
- EC-00: preflight git/PR/local state/gate reading completed for safe isolation; release baseline H-079/H-081/H-082 remains unqualified.
- EC-01: historical failure reproduced at HEAD: H-080B test [True] returns NEEDS_REASONING and makes 3 forbidden provider calls. Not yet resolved. The fresh-command test fixture has host example.test versus learned trello.com. A temporary diagnostic correction to trello.com STILL failed (no_certifiable_capability_found); the diagnostic-only test modification was subsequently reverted, preserving the original test. Detailed investigation observed PROMOTED/healthy cap, reload registry count=1, goal coverage=True, effect containment=True, verifier sufficiency=True and empty preconditions. Next trace the actual TaskCompiler/router candidate rejection and trusted scope at runtime. Existing browser tool requirements missing in test environment are also logged.
- EC-02: fail-closed canary patch in workstation/experience_compiler/lifecycle.py plus new negative regressions workstation/tests/test_local_canary_replay_fail_closed.py. Original RED: ignored primitive and read_file falsely returned replay passed; verifier accepted path traversal and positive evidence was not bound to candidate. Patch now rejects unsupported primitives, requires replay, independently readbacks candidate target(s), binds digests/IDs/contract and executes a candidate-bound divergent-state negative. Unit focus 9 passed. Broader regression **60 passed, 1 skipped in 157.28s**. This is partial EC-02, not product qualification.
- EC-03..EC-14: pending, except EC-13 conditional HOLD.
- H-080B test log .ec_h080b_red.log and regression log .ec_canary_regression.log are local scratch; never commit them.

## Next exact action
1. Read final output of current full relevant pytest run (process PID recorded in session/EVIDENCE.md; PID is ephemeral). Inspect .ec_canary_regression.log if process ended.
2. Review candidate-specific canary patch for step schema, target/run binding and adversarial cases; add RED tests then fix any real misses.
3. Investigate H-080B operation intent/host and owner/browser-route effects rather than weakening semantic admission. Add matched-host/mismatched-host tests; narrow minimal correction where justified.
4. Continue EC-03+ without duplicating validated work. Commit/push only if tests and gate documentation support, keep PR #82 draft.

## Permanent handoff
Before ending update these files, git status, exact commit SHA, test outputs and NEXT_PROMPT.md. Return a ready-to-copy new prompt with next action. Each new session inherits this contract.

## Remaining release debt
- Native lefthook pre-commit failed on 32 pre-existing modernization UP findings in lifecycle.py; no hook/CI pass claim. Exact-HEAD CI and H-079/H-081/H-082 remain HOLD.

## Post-hook corrective update
- The original 32-error lefthook failure was addressed with scoped Ruff safe modernizations to lifecycle.py. A fresh F,UP lint PASS and narrow 9-test PASS were observed. Final broad regression: 60 passed, 1 skipped in 109.59s, exit 0. Second native lefthook attempt still pending at this ledger update. Release gates remain HOLD regardless.

## UPDATE — EC-01 new-task routing fixed in feature branch (2026-10-12)
- The older EC-01 failed-status narrative above is SUPERSEDED for the isolated H-080B targeted E2E: both scenarios NOW PASS after editing workstation/work_intent.py (not router/effect policy) to project allowlisted native site commands to host/page_family/recovery_state exact goal and effect footprint, without unsolicited url capability input.
- Tests: TDD RED 1 on old URL vs learned host representation, then route reached execution but RED `unexpected learned capability parameter`, then TDD RED for unsolicited url, then GREEN: 6/6 command-intent tests and H-080B both [False,True] PASS (2 passed, 24 deselected in 24.88s).
- H-080B [True] failure mechanism confirmed by temporary CapabilityRouter forensic instrumentation (subsequently removed): incoming operation originally goal EQ(url,https://trello.com/) and effect SET(url,..); learned promoted capability required host=trello.com, page_family=/, recovery_state=live. Original goal_coverage=False, effect_containment=False, authority=True, verifier VALIDATED. With schema-aligned goal route certifies; dropping undeclared url makes compiled zero-input capability execute.
- New tests: workstation/tests/test_current_command_native_intent_contract.py; updated existing test_current_command_resolution.py fixture to reflect real native/browser state contract and preserve strict authority gate.
- **Not production-qualified**: EC-01 adjacent full regression running (see EVIDENCE); CI exact-head, Laya DIRECT and native Electron UI dogfood still unqualified. EC-02 candidate-specific canary remains partial, future negative tests needed.
- Next: finish EC-01 regression, commit + push, then EC-03 production owner verification, EC-04 real mid-run samples, EC-05 Laya DIRECT, and EC-07 EvidenceRef telemetry.

## Continuation result — EC-01 regression confirmed
- EC-01 intent IR adaptation in work_intent.py with target/contract-matched allowlist is ready for draft review. Full four-file regression 42 passed in 175.32s, lint F,UP passed. Exact-head CI/H-079/H-082 remains unqualified, no production certification.
- Next engineering target EC-03 and EC-07: exercise production factory readback/lease and fix EvidenceRef JSON serialization at telemetry sink with RED->GREEN tests. EC-02 committed under e81d23a812, with safety gaps preserved as future negative-test work.
