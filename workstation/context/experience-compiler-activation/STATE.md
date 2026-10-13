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

## UPDATE — EC-03/EC-07 incremental (2026-10-12)
- EC-01 committed: 38dc4b52a1 (native intent IR routing); 42 passed in four-file regression; targeted H080B [False,True] passed. PR #82 remains draft.
- EC-03: fail-closed cache binding patched in run_local_adoption.py and RED->GREEN owner factory test (5 PASS). Broader owner/lease/browser/restart E2E pending.
- EC-07: EvidenceRef typed object caused SQLite telemetry warning. emit_event projects URI only, no summary; RED->GREEN regression, 11 telemetry PASS + 13 focused pytest PASS, Ruff F,UP PASS. Full System-1 telemetry suite has independent Laya import blocker.
- NEXT priority: EC-03 owner lease/restart negative tests and EC-04 live intermediate VERIFIED samples; assess Laya installation provenance before EC-05. Preserve EC-02 candidate-specific validation and release gates as partial.
- This worktree remains isolated; do not merge main. Refresh git HEAD, GitHub PR and CI, since this ledger is written before next commit/push.

## Handoff checkpoint after publish / EC-04 seam discovery
- Last tested/pushed code commit f710a6b46b034ac37c953869877f795b8672a9b1; GitHub PR #82 draft, unmerged, no workflow runs at this SHA (NOT green). Current doc-only commit may advance HEAD; always git rev-parse HEAD.
- H080B rerun on published code: 2 passed / 24 deselected in 37.92s, verifying no regression in native reused capability routing after EC-03 cache fix.
- EC-04 NEXT RED: exercise a real intermediate owner-verification event in an unfinished TaskRun; assert neither observed nor uncertain tool result becomes VERIFIED_SUCCESS, and that independently verified operation sample/provenance is offered to monitor before TaskRun completion. Inspect run_adoption.py:_execute_item and operational_kernel.py:capture, corpus.py and compilability_monitor.py:notify_online_compilability, plus current Kanban completion hook. Do not grant authority through observer notifications.
- EC-05: environment must install qualified pinned Laya 0.3.23 and provenance subtree in isolated runtime; no fake DIRECT. EC-03 browser lease/restart and full authority negative E2E pending.

## 2026-10-12 — EC-03/EC-04 continued after b113652ed0
- Isolated branch feat/experience-compiler-real-reuse-20261011; PR #82 draft, no main merge. Use git rev-parse HEAD after further commits; root checkout remains untouched.
- EC-03: run_adoption.py maps browser_navigate to HTTPS host/path-scoped external CALL effect, requiring readback, effect budget and authority; run_local_adoption.py denies stale owner dispatch/readback after canonical task/run changes. Additional two cancellation-window tests show owner rechecks canonical lease/authority/uncertainty at item start and before each step, without widening grants.
- EC-04: progressive.py now rejects VERIFIED_SUCCESS without persisted independent owner evidence bound to task/run/operation; operational_kernel.py persists canonical verification proof and supplies its ref for progressive capture. Negative tests covered forged/missing proof, wrong run, canonical unlinked and failed downstream readbacks.
- EC-03/04 tests: 7 owner factory PASS; 3 browser effect tests PASS; 10 progressive/browser PASS; previous full safety 49 PASS; H080B pair 2 PASS. Additional full regression after time-of-check/use race fix in .ec04_final_full_suite.log is not yet recorded here.
- EC-05: vendored Laya 0.3.23 import and verify_laya_provenance PASS; 2 System-1 telemetry tests PASS when vendored source is on PYTHONPATH; locked source SHA 4aa6761be8173de4ce6d92c31b3e40b6eaf59a7c. Live checkpoint and DIRECT NOT QUALIFIED.
- EC-03 production Browser lease/restart/readback H-082 and EC-04 actual early owner verification -> Laya -> offer -> reuse E2E remain open. EC-06 native effect budgets may need explicit authorized CALL migration before direct Browser adoption.
- All release H-079/H-081/H-082 and exact-head CI remain HOLD; EC-13 conditional HOLD. Logs .ec*.log remain local and untracked, never stage.

## Final regression gate for this implementation
- Latest full targeted security+learning regression after both lease race fixes: 51 passed in 115.40s, exit 0, .ec04_final_full_suite.log (local only).
- Latest owner factory regression: 7 unittest PASS. Ruff configured rules for 9 edited code/test files PASS; diff check PASS. H080B pair 2 PASS.
- Next step after commit: explicit CALL effect authority budgeting and independent native Browser lease/readback E2E; then actual active-run owner-verified Laya adoption cycle. Release CI/gates HOLD.

## Commit checkpoint — EC-03/04 code published to local branch
- EC-03 code commit 065acd189b (exact full SHA via git rev-parse); native Lefthook lint PASS.
- EC-04 code commit 3b9f18ac51528da329fb1fdfdaba5f98893b4e2a; native Lefthook lint PASS.
- Both commits were authored on isolated feature worktree. Confirm remote push/PR HEAD after documentation commit; no merge was performed.
- Latest full Python regression: 51 PASS, H080B pair 2 PASS, owner 7 PASS, System1 local Laya 2 PASS. Native qualified production/release HOLD.

## 2026-10-12 — scoped Browser CALL and witnessed progressive state (continuation)
- Local commit 40f8f82a66 follows f37208a4: fixes current_command_objective to budget exact CALL(browser.navigate,trello.com); native Lefthook PASS. PR #82 is still draft.
- EC-03 intent tests: 10 PASS / Ruff PASS; H-080B pair after CALL 2 PASS (39.35s) and after progressive metadata 2 PASS (42.04s). No external authorization broadened to arbitrary sites.
- EC-04: existing progressive sample stored only bare primitive and after-state; added formal-contract family/effect/scope, runtime tag and optional verified prestate delta. A merely caller-supplied prestate produced false causal delta (RED); now a distinct owner-persisted prestate receipt with matching task/run/operation is mandatory. Tests 24 PASS for progressive + OperationalKernel (before last negative scenarios), 3 targeted negative/positive proofs PASS. Replay arguments remain intentionally absent until bound to owner-issued evidence; no false mining claim.
- In new EC-04 proof schema workstation.operational_prestate_readback.v1, check source observer/workstation.operational_prestate, state, read_before_write and identity; currently NOT a proven production producer, so EC-04 is not qualified end-to-end.
- EC-05 source-locked Laya v0.3.23 tests (vendor provenance, real contract, routing): 10 PASS 1 SKIPPED. Real checkpoint/DIRECT/CI HOLD.
- Final full safety suite after prestate gate pending local log .ec04_prestate_final_safety.log. Keep all .ec*.log untracked; checkout principal still dirty and untouched.

## Final code checkpoint — EC-03/04 witnessed evidence (2026-10-12)
- EC-03 exact host CALL native budget code committed: 40f8f82a663152bcbade0fea809352973edd1dc7 (hooks PASS). EC-04 family/delta witnessed prestate code committed: c3f87a84860615f2086f17191921605068c6932c (hooks PASS).
- **Fresh full safety regression after prestate proof**: 56 passed in 221.83 seconds, exit 0. Log .ec04_prestate_final_safety.log (intentionally untracked). H080B after proof change 2 passed/24 deselected in 73.59 sec, exit 0. Owner tests 7 passed; Laya pinned 10 passed 1 skipped. Ruff PASS.
- All substantive local changes are staged for publication through code commits. Final documentation commit may follow. PR #82 remains DRAFT and must NOT be merged.
- No qualification of native Electron live effects, DIRECT real model checkpoint, full early-capture producer/verified same-run adoption, or exact-head CI. EC-13/14 HOLD.

## 2026-10-12 — EC-04 partial real producer and verified intermediate sample
- Base HEAD 7d85ffdf627eeb0f5e352bcffd203007607e6916 on isolated feat/experience-compiler-real-reuse-20261011. PR #82 DRAFT, no merge. Refresh HEAD after local commits.
- Filesystem observer now uses _resolve_path(path, base_dir) for filesystem/composite. A real DurableTaskStore (SQLite) test reproduces the original wrong-path precondition and its correction.
- Single-step scoped fs_write on the existing OperationalKernel, with callable primitive_admission and matching durable plan/item, persists workstation.operational_prestate_readback.v1 before effects. Rechecks admission + durable plan/item after prestate. Cross-run, cancelled plan, missing owner admission, path escape, and restart with uncertain dispatch marker must fail closed.
- For fs_hash/fs_stat only, independent owner readback is persisted without raw content and referenced by canonical verifier. A real filesystem hash verifier produces VERIFIED_SUCCESS in rehydrated ExperienceCorpus while second durable work item remains PENDING. Cross-resource prestate/poststate chains rejected.
- Important limitation: proof producer is currently scoped to one fs_write step and a supplied existing primitive_admission callback; no proof of native Browser/Electron authority and no end-to-end live Laya or verified reuse. Do NOT declare EC-04 globally complete.
- Local scratch .ec*.log files remain untracked. Original checkout untouched. H-079/H-081/H-082 exact-head gates hold.

## Final focused qualification on 2026-10-12
- Full combined owner/EC-03/EC-04 regression after resource-binding fix: **68 PASS in 207.98s**, exit 0, .ec04_prod_full_safety_final.log local untracked. H080B native pair **2 PASS, 24 deselected in 27.19s**, exit 0, .ec04_prod_h080b_final.log. Owner factory 7 PASS. Ruff default PASS, git diff --check PASS.
- Complete live Laya and DIRECT offer/adopt/VERIFIED_REUSE remain NOT RUN/HOLD. PR #82 draft, no merge.

## Código EC-04 publicado localmente
- Novo commit de código d3c171c3ef78efb2c3c025af00938bdd6694ddc9, hook Lefthook PASS; primeiro hook recusou 36 avisos RUF059 de unpacked vars em teste novo, corrigidos com Ruff fix restrito ao arquivo novo; replay focused 23 PASS (16.42s), hook segundo PASS sem bypass. O próximo commit documental e GitHub PR head devem ser verificados.
