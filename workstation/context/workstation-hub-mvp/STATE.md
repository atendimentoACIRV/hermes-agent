# HWH-001 — checkpoint, 2026-10-12

**Release status: BLOCKED / NOT_VERIFIED_NATIVE.** This branch currently contains documentation only; HWH-01/02/03 product code has NOT been implemented or tested.

## Git / worktrees
Repository `kevynlucasprofissional-stack/hermes-agent`
Original `origin/main`: `a2b56db1bc9e0b5acf48d94fa86a9844a1005842`
Original downstream-to-upstream frozen common pin: `66605471e9f0b0832abbefaf625ce08e948ca540`
Observed upstream main after actual fetch: `53df274b08f2bbbe82bb67bb50c7571952e95809`
Divergence from origin/main at check: `963 478` (left/right).
Feature branch: `feat/workstation-hub-creative-session-handoff-20261012`
Feature worktree: `C:\Github\hermes-agent\.worktrees\workstation-hub-creative-session-20261012`; created clean at original origin/main. Remote branch created through GitHub; **fetch it before local commits**.
Stage A branch: `integration/hwh-upstream-20261012-53df274`
Stage A worktree: `C:\Github\hermes-agent\.worktrees\hwh-upstream-baseline-20261012`. It has a **live in-progress, UNCOMMITTED upstream/main merge**, not a clean/qualified integration.
Primary checkout: `C:\Github\hermes-agent`, branch `fix/hermes-oneclick-lock-startup-20261011`, HEAD `9fffa7f3ffcc2c50774654c271fe25e92ce459e8` at inspection, with ~20+ dirty changes of other agents. DO NOT CHANGE.

## Stage A candidate merge
`git merge --no-commit --no-ff upstream/main` produced 5 conflicts:
- `agent/chat_completion_helpers.py`
- `apps/desktop/electron/updater/checkout-source.test.ts`
- `pyproject.toml`
- `tools/tool_search.py`
- `uv.lock`

The conflict hunks were resolved **in local working files only** by `C:\Temp\hwh_stagea_resolve.py`: combined downstream provider usage with upstream reasoning carriers; combined downstream tool projection registry with upstream search metrics; kept downstream idempotent loopback URL interception in updater fixture; kept downstream 14-day exclude-newer policy and package exceptions vs upstream 3-day; kept downstream lock options and extras. **Not staged** at checkpoint: index still showed five U conflicts. These resolutions are candidate decisions, **NOT qualified**. Reinspect behavior and regenerate/check lock; do not blindly finalize.
Offline `uv lock --check --offline` failed because git dependency `NousResearch/misaki@f03fd2be` was not cached. Focused Python pytest tool call was blocked before execution by platform security settings. No PASS claim.

## HWH ledger
| Phase | Status | Next |
|---|---|---|
| HWH-00 | IN_PROGRESS / H-079_BLOCKED | Finish qualified upstream integration and exact-head baseline |
| HWH-01 | NOT_STARTED | RED test of agent internal Creative app dispatch → Desktop |
| HWH-02 | NOT_STARTED | RED test of Hub Creative tab/provider/occlusion |
| HWH-03 | NOT_STARTED | RED test of authenticated adoption of existing tab |
| HWH-04 | NOT_STARTED | Three native Electron E2Es |
| HWH-05 | NOT_STARTED | Feature implementation, commits, PR review; no main merge |

## Related PRs
#77 Creative renderer-local editor/provider; #81 hybrid Creative TaskRun, pending trusted owner; #83 Browser session authority and human leases; #85 Browser automation test-only. All observed OPEN/DRAFT/UNMERGED.
