# Main consolidation audit — 2026-10-12

**Status: IN_PROGRESS — Stage A is not qualified.** Repository: `kevynlucasprofissional-stack/hermes-agent`.

## Baseline and gates

- Downstream baseline: `main@a2b56db1bc9e0b5acf48d94fa86a9844a1005842`; upstream pin `3b63…` must be recorded in full. Stage A is separate; partial state `53df…` is not qualified.
- Required order: qualify exact Stage A head → semantic target integration → target/regression gates → normal PR/push/merge → local main fast-forward → full audit. One pin per cycle; later upstream movement is next-cycle drift.
- At initial inspection, PR API had an empty `statusCheckRollup` and an explicit dispatch returned HTTP 422 while Actions was disabled. After the owner reactivated Actions and authorized cost containment, settings-only changes marked 11 inherited workflows `disabled_manually`; fork-owned Workstation CI and Browser Windows remained active. Their owned workflow sources were later narrowed; Windows is manual-only and retains its complete aggregate, but neither lane was dispatched by this audit. See [CI cost-control record](../CI_COST_CONTROL.md) for IDs and trigger scopes. Workflow source/configuration is not exact-head evidence. The current Stage A tree has no exact candidate SHA or exact-head receipt; qualification remains PENDING, never green. The earlier baseline runner stopped at missing `acp` imports; isolated test-environment setup was later authorized, but no qualifying exact-head result is recorded here.
- Five Stage A decisions: chat usage + carrier; tools projection + internal payload/metrics/call; updater idempotence + main Git semantics; three-day dependency policy without exceptions, preserving Laya extras/source; regenerate `uv.lock` through repository PM.
- Current Stage A worktree snapshot: `HEAD=a2b56db1bc9e0b5acf48d94fa86a9844a1005842`, `MERGE_HEAD=3b63f7b0a4c7beb9eadbce2f15b9da75d01f5065`; `uv.lock` is the sole unresolved merge path. Stage A remains IN_PROGRESS.

## Stage A validation receipts (2026-10-12)

- BOM regression: `scripts/run_tests.sh workstation/tests/test_browser_workstation_route.py -q` first reproduced both failures (controller availability returned `False` for a BOM-prefixed valid descriptor; public route binding returned `False` for a BOM-prefixed valid BrowserTask projection), with 16 existing tests passing. After both reads used BOM-tolerant UTF-8, the canonical runner passed **18/18**.
- POSIX scratch-path scanner: the added synthetic scan test first failed because both vendored Laya documentation and archived dogfood conversation data were reported; the maintained first-party control remained expected. After narrowly pruning `workstation/third_party/laya` and `workstation/dogfood/dados`, `scripts/run_tests.sh tests/scripts/test_check_no_tmp_literals.py -q` passed **24/24**. Ruff’s only baseline Laya findings were PLW1514; the vendored path now ignores only PLW1514, leaving other Ruff rules active.
- `python scripts/check --only footguns,no-tmp,agents-md`: **3 checks, ok**. `python workstation/scripts/audit_hermes_seams.py`: **21 direct seams, all 21 classified, 0 unclassified, 0 budget regressions**. `git diff --check HEAD`: clean after removal of the trailing blank line in `tools/connectors/gateway/bridge.py`.
- Full `scripts/check` remains unverified: the local host provides Ruff 0.17.0 while this checkout pins 0.15.10, and no install was performed. Desktop typecheck/build remain unrun because this worktree has no `node_modules`. No dependency installation or external setup occurred.
- Current workflow source has since changed: Ubuntu stays the automatic fork-owned lane; Windows is manual-only with its complete gate aggregate. Neither lane has been dispatched, so source changes are not qualification evidence. The Ubuntu lane's explicit `workstation/tests` collection includes 72 unconditional OPC RED specification placeholders (and two credential-gated navigation stubs); they are known debt, not passing tests. Keep OPC NOT QUALIFIED and do not alter real credential-backed tests while deciding the separate non-collected home for the spec text. See [CI cost-control record](../CI_COST_CONTROL.md).

## Open PR inventory

Every PR reports CLEAN/MERGEABLE but has empty status checks. #70 alone is non-draft; #71–#88 are drafts.

| # | Draft | Base | Head branch @ SHA | Scope / disposition |
|---:|:---:|---|---|---|
|70|no|main|`fix/hermes-oneclick-lock-startup-20261011` @ `7c24c09`|One-Click startup; reassess after Stage A.|
|71|yes|main|`fix/p0-kanban-read-effects-20261011` @ `ae14d0a`|Keep Kanban reads out of mutation admission.|
|72|yes|main|`fix/boa001-effect-classification-20261011` @ `8ca9297`|Browser interaction/read classification; one mutation authority.|
|73|yes|main|`fix/p0-denied-mutation-receipts-20261011` @ `a491a8f`|Operation-scoped human review receipts.|
|74|yes|main|`fix/p0-run-supersession-recovery-20261011` @ `bf8227a`|Stale-run fence and durable continuation.|
|75|yes|main|`fix/p0-smart-task-admission-20261011` @ `e4f9daa`|Deferred TaskRun admission; exactly-once dispatch.|
|76|yes|main|`integration/p0-authority-browser-20261011` @ `4e6884d`|Converges #70–75; contains `9fffa7f3`.|
|77|yes|main|`feat/p0-creative-mvp-20261011` @ `1692d50`|Renderer-only Creative editor MVP.|
|78|yes|main|`docs/cw-audit02-20261011` @ `22a0e85`|Creative source comparison/shared document/export verifier docs.|
|79|yes|#76 branch|`fix/p0-admission-proof-core-20261011` @ `7d5c4df`|Force-work authorization/proof-bound completion; stacked.|
|80|yes|#79 branch|`fix/p0-proof-bound-completion-20261011` @ `0e7fd07`|Kanban backup/read-only history; stacked.|
|81|yes|main|`feat/hcw-hybrid-01-20261011` @ `940a038`|Native source persistence, rational time, safe export.|
|82|yes|main|`feat/experience-compiler-real-reuse-20261011` @ `f552c96`|Learning funnel, verified readback, Experience Compiler Studio.|
|83|yes|#80 branch|`fix/p0-kanban-browser-authority-20261012` @ `22498a0`|Kanban intent/native Browser authority; stacked.|
|84|yes|main|`docs/hermes-work-knowledge-freeze-20261012` @ `1aaa13a`|Knowledge/strategic docs; reconcile canonical context.|
|85|yes|main|`feat/hermes-browser-automation-v1-20261012` @ `80c7acc`|Test-only Browser persistence/crash recovery; require native proof.|
|86|yes|main|`feat/creative-quality-capability-lab-20261012` @ `90f74a9`|GLB/HyperFrames/EffectCraft lab; Creative overlap.|
|87|yes|main|`feat/workstation-hub-creative-session-handoff-20261012` @ `001d8f1`|HWH-001 preflight/checkpoint; blocked/conflicted.|
|88|yes|#83 branch|`fix/mvp-kanban-browser-superseded-20261012` @ `682a15e`|Deepest P0 child; package smoke 5/6, one boot failure unconfirmed.|

P0 chain: #70–75 → #76 → #79 → #80 → #83 → #88; review as one semantic stack. #77–78/#81–82/#84–87 are separate lanes. Creative overlaps #77/#78/#81/#86; choose canonical owners, preserve reusable semantics. #85 is test-only; #87 remains blocked. `9fffa7f3` is already in #76/descendants, not exclusive.

## Preserved local work

- Original checkout has 17 dirty Desktop files for native-view occlusion/visibility (helper, pane gating, overlay annotations, regressions), absent from #70–#88. Preserve as a separate post-Stage-A slice, not One-Click.
- Obsidian state and private session/conversation exports are local user data; never publish or copy into runtime.
- No-PR chain `audit/browser-native-evidence-20261012` → `audit/playwright-c2c-20261012` → `feat/playwright-c2c-kits-20261012`: native Browser evidence, replay/admission, pointer recovery, TaskRun journal, cross-process serialization and gates. Preserve final head.
- No-PR Creative chain `codex/creative-stage-a-20261008` → `cw02` → `cw03a` → `cw03b` → `cw03c`/`creative-native-capture-20261008`: docs/gates, native views, export, Remotion. Preserve latest; compare D-043/#77/#81/#86.
- `codex/creative-cw01-refresh-20261008`: docs/evidence, preserve. `integration/hwh-upstream-20261012-53df274` was observed at `a2b56…`; linked #87 worktree is conflicted, so no integration is proven.

| Stash | Label | Patch ID | Handling |
|---:|---|---|---|
|@0|`wip-dogfood-20261008`|`c8724c617003205dc2366879553d95f032073f40`|Obsidian/day-note local state.|
|@1|`readonly preflight qualification follow-up`|`9491980240473aeed2d833b13f46ac47f2f9c86d`|Runner/qualification; compare current.|
|@2|`preserved workstation WIP before main sync; not merged`|`bee48f2b4d535abf132f4e3959882d965f59dbf8`|Same diff as @3.|
|@3|`preserved workstation WIP excluded from main pending canonical-owner review`|`bee48f2b4d535abf132f4e3959882d965f59dbf8`|Duplicate of @2; preserve refs, one logical candidate.|
|@4|`wip-human-card-delegation-bridge`|`a02e4a4e11865722f047d1f5814cad05d8441484`|Overlap-review.|
|@5|`codex workstation audit before main sync`|`69ec36f0d0bba990d719ae3bc66d5ab38d351c6a`|Browser/Kanban/compaction; compare.|
|@6|`backup-plugin-api`|`f938ff3d4d1ae0d5ebbc8ae40481a91d2da35ddf`|Compare canonical owner.|
|@7|`backup-pre-hardening`|`2be34f1d9c03247d6730fae4d6e7e644b50615c3`|Vault/ArtifactStore/browser daemon; distinct from @2.|
|@8|`pre-hybrid-kanban-intelligence-2026-09-14`|`2f3066f781591e73b641c7f441b9c37b7ebeec58`|Intelligence docs.|
|@9|`pre-hybrid-kanban-vault-docs-2026-09-14`|`e76dc53b736d2227b46dabd40d41101b09eb82e4`|ROADMAP/intelligence/journal; includes @8 material but differs.|
|@10|`pre-main-sync-2026-09-14-local-intelligence`|`2c0c6414d9baea812f7f9ec1d4e077954f784c1a`|Larger earlier doc version.|
|@11|`pre-main-sync-2026-09-14-local-tracked`|`485ffa9159c20e8247c8be1244e227330baf5a85`|Older 17-file startup/Browser patch, distinct.|

Patch IDs came from stash patch content; no stash applied/dropped. Different IDs do not prove obsolescence. Follow root AGENTS, Workstation README, upstream-first/seam policies, TESTING, UPSTREAM_DELTA and PATCH_MANIFEST. #88 boot cause is unconfirmed; do not execute red-team payloads.
