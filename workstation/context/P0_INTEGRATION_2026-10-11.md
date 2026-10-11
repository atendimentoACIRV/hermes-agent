# P0 convergence: authority → Browser → One-Click (2026-10-11)

**Status: DEVELOPMENT_ONLY, draft integration.** No main merge or user data mutation. Baseline `origin/main@a2b56db1bc9e0b5acf48d94fa86a9844a1005842`, upstream pin `66605471` included and later upstream `9e827685` observed; H-079 `PASS_WITH_AUTHORIZATION` is a development exception, not CI green.

## Changes included from separate PR heads
- **#70 One-Click:** deterministic lock consistency, installed-dependency fingerprint gate, Python start/doctor fixes and Browser payload model projection. HyperFrames local-server independence still needs native offline dogfood.
- **#71:** read-only Kanban tools do not go through mutation admission.
- **#72:** BOA-001 classified 17+ browser/read and interactive tool effects, preserving conservative unknown effect behavior.
- **#73:** denied write review scope is operation-based; consumed once, blocked without new approval minting or unsafe redispatch.
- **#74:** stale-run typed authority error and pending checkpoint; no auto-claim or bypass of cancelled/revoked run.
- **#75:** Session≠Task≠TaskRun: real durable work admitted in triage, Run claimed at execution, one-shot Browser commands don't create cards, blocked tasks don't lend leases.

**New integration correction:** `TaskCompiler.execute` previously looked up an explicitly bound canonical Task in `WorkstationKanbanBridge`'s default SQLite database even when a `DurableTaskStore` had been constructed with an injected canonical SQLite connection. This broke 9/10 supersession E2E tests in the combined branch with `canonical_task_session_mismatch`. Now the TaskCompiler consults and claims from **the same underlying injected Kanban owner** when present, and only falls back to Workstation's configured Kanban owner otherwise. No extra store, no authority downgrade, no blind replay. After fix: focused 25/25 PASS (Task admission 15 + supersession 10), expanded P0 116/116 PASS across eight suites (read effect, Browser payload, handoff, cancellation/authority and policy).

## Definitive priority lanes, truth and remaining DoD

| Rank | Front | Current evidence | Release gate |
|---|---|---|---|
| 1 | UI, authority, handoff | Drafts #71–#75 integrated; Browser pane renderer's 4 local tests passed from **uncommitted user worktree**, not part of this branch | Packaged Electron actual buttons/navigation, UI review completion→consumption→readback, no loops, exact-head tests |
| 2 | Browser correctness, idempotency | 116/116 integrated regression tests including readbacks, stale-run and mutation effect projection; legacy uncertain writes remain fail-closed | Real timeout→independent readback→resume without duplicate; H080B fresh-command `no_certifiable_capability_found` baseline red remains |
| 3 | Creative Workspace MVP | Separate `feat/p0-creative-mvp-20261011` patch: project/vector/keyframe UI and JSON/SVG file MVP | Native human/AI shared `CreativeDocument` backend, saved source, verified animated export |
| 4 | One-Click and Studio | PR #70 merged here for test integration; deterministic lock/skip-dependencies checks reported on #70 | Clean, offline/warm Windows packaged launch, disabled HyperFrames server, actual native Studio fallback |
| 5 | Composited 3D | Existing `creative_3d.py` GLB/Three.js contracts (not native qualified) | Editable GLB object in same composition and exported frames plus negative ownership/asset tests |
| 6 | Payload and duplicate reasoning | Browser model projection test asserts projected payload below 65% of raw JSON on synthetic 60-element snapshot; not a token measurement | Real dogfood paired tokens/tool calls/p50/p95 latency and identical addressability |
| 7 | Graph Editor | Renderer draft edits numeric keys/easing; legacy graph visual | Tangent/Bezier editor, AI/human equivalence, exact timing, undo/redo and visual negative tests |
| 8 | Prefabs, Experience Compiler | Existing compilation pipeline and independent PRs; no repeat-LLM authority granted | Separate verified capability proof, drift detection, deterministic execution no LLM only when admitted |
| 9 | Motion/video/effects engines | Engines and reference audits are source catalog only | Backend-neutral render/source fidelity, video decoding proof, license/dependency gates and native E2E |

## Release hold (non-negotiable)
- No packaged native Windows UI test from combined branch, no exact-head GitHub Actions runs verified; product behavior not automatically qualified by unit tests.
- No merge of PRs #70–#75 into main; this integration branch is a review surface for compatibility. The local root checkout contains extensive user/uncommitted renderer changes and was never reset/staged/committed here.
- No user data/old Kanban cards were altered. Release is held on definitive approvals/readback, Electron One-Click offline and Creative backend parity.
