# HCW-HYBRID-01 — Development-only integration evidence (2026-10-11)

## Scope and status

The user selected the EffectCraft + HyperFrames hybrid-composition approach as an extension of D-043; it does NOT replace D-043's engine-neutral project ownership.

**Not qualified for main.** The H-079 upstream-first Stage A/exact-head CI gate remains open, and neither external engine has been demonstrated running as an integrated pair. This branch contains bounded, test-first source-storage, rational-time and export-verifier improvements only.

## Reproducible baseline

- Worktree: `C:\Github\hermes-agent\.worktrees\hcw-hybrid-01`
- Branch: `feat/hcw-hybrid-01-20261011`
- Base: `origin/main@a2b56db1bc9e0b5acf48d94fa86a9844a1005842`
- Main checkout: `C:\Github\hermes-agent`; 34 existing dirty entries preserved and untouched.
- Upstream accepted pin is an ancestor: `66605471e9f0b0832abbefaf625ce08e948ca540`. A fresh `git fetch upstream main` observed `835c3dd038d903182a66ecc45e34bf5e0de65f00`, 245 upstream-only commits and 963 downstream-only commits versus the baseline. No upstream merge or seam reconciliation was performed.
- GitHub exact-head CI status: not proven green (connector returned no workflow runs/statuses for baseline).

## H-C0 and H-C1 engine-probe results

- Local EffectCraft snapshot: `referências/01-Criacao-Visual-Video-3D/effectcraft-main`; Rust 1.98.1.
- Command run: `cargo build --offline --locked -p effectcraft-cli` with isolated `CARGO_TARGET_DIR=C:\Temp\hcw-hybrid01-effectcraft-target`. **Exit 1**: pinned Git dependency `filmcraft-color` at FilmCraft revision `2c5ba7a...` is not available for offline checkout.
- No packaged CLI executable found at the checked default `C:\Program Files\EffectCraft\effectcraft-cli.exe`, in the local snapshot target, or on PATH.
- HyperFrames resolver candidates from `creative_studio_service.py` were checked: no package found under the standard Antigravity scratch runner, root node_modules, or global npm. A `~/.hyperframes` configuration directory alone does not establish a valid installed CLI.
- No PNG sequence was rendered by a real HyperFrames execution and no EffectCraft footage import/export was executed. **H-C1: BLOCKED; no E2E or media-composition claim.**

## Implementation truth

| Requirement | Status | Actual proof |
|---|---|---|
| H-C0 local isolation | SOURCE_PRESENT | dedicated clean worktree, safe baseline, cargo/Node/FFmpeg discovery |
| H-C1 actual RGBA footage into EffectCraft | BLOCKED | both external engine execution paths remain unqualified |
| H-C2 preserve native projects in one Hermes revision | UNIT_TESTED | `save_hybrid_project_revision` saves `.ecproj`, HTML and JSON; canonical `save_creative_document` accepts native files with declared references; hashes, IDs and ETag checks |
| H-C3 one canonical clock | UNIT_TESTED (partial) | pure `HybridTimeMapping` uses `CanonicalTime` and `RationalFps`; seeks, offsets, reverse, freeze, 30000/1001 |
| H-C3 cross-engine parameter bindings | NOT_IMPLEMENTED | no real EffectCraft/HyperFrames command adapters |
| H-C4 coordinated human/AI operations | NOT_IMPLEMENTED | no cross-engine atomic publish/Electron authority E2E |
| H-C5-H-C9 | NOT_IMPLEMENTED | advanced editor, masks, caching, on-demand render and nesting not exercised |
| Export fail-closed decoder | UNIT_TESTED | `_decode_frame_hash` raises instead of synthesizing SHA on failed decode; verifies decoded RGB byte dimensions |
| Export missing visual source | UNIT_TESTED | errors instead of silently exporting a synthetic black video |

## Security and known gaps

- Existing export pipeline `creative_export.py` is still a **single primary-source FFmpeg path**, not a true multilayer composition renderer. A successful FFmpeg decode alone does not prove overlay, cuts, text or 3D content parity. H-C1 PNG/MP4 acceptance remains BLOCKED.
- Existing `CreativeProjectStore` permits history forks and checks ETag against the selected parent. This is not an atomic global-head CAS/lock across concurrent editor sessions. Cross-engine atomic commit is NOT implemented.
- `CreativeProjectStore` has a duplicate shadowed `load_creative_revision` definition from the baseline; not addressed in this bounded change.
- Native files are persisted as bytes within existing per-file 16 MiB policy and loaded after integrity validation. No renderer evaluates untrusted scripts in an Electron privileged origin.
- The new native project fixtures are intentionally sample bytes, not an `.ecproj` parsed by EffectCraft. **No native format validity is inferred from storage tests.**
- `test_creative_runtime.py` previously reported a yaml dependency collection error in the audited Python environment; only actual new test command output should be used for qualification here.

## Next unblock steps (no claims of completion)

1. Qualify H-079 Stage A baseline on an independent branch, or obtain an explicit recorded development exception with scope; do not merge this lane while Stage A is unresolved.
2. Obtain/build pinned EffectCraft CLI with verified FilmCraft dependency provenance and verify real `file.import` of numbered RGBA footage.
3. Locate/admit HyperFrames producer installation; generate alpha-preserving 30 fps frames using real `hf-seek`/CLI.
4. Run the H-C1 test with a real edited EffectCraft project, a visibly modified effect and decoded PNG/MP4; compare frames/source files.
5. Connect persisted subproject refs to TaskRun-admitted typed commands and a real Electron UI before declaring H-C2/H-C3 product-complete.


## Continuation — local source-only infrastructure, H-C1 renderer still BLOCKED

- HyperFrames official repository cloned in isolated `C:\Temp\hcw-hybrid01-hyperframes-src` and checked out at **exact SHA `6ae1af7470133db72de6d9bbceeaf80e85695c68`**; `bun install --frozen-lockfile --ignore-scripts` completed with exit 0 and 1,457 packages in the isolated reference directory. No build/run of its real frame producer is yet proven; attempted direct source CLI execution was refused by connector security and was not bypassed.
- EffectCraft Rust `cargo build --locked -p effectcraft-cli` resolved the earlier FilmCraft pinned Git dependency and compiled multiple workspace crates; final executable status must be checked separately. This is toolchain progress, **not** an imported/composited media proof.
- `creative_hybrid_footage.py`: validates real consecutive RGBA PNGs, actual transparency, visible compositable pixels, motion, dimensions, file hashes, and constructs an EffectCraft `file.import` command with explicit fps and `addToComp`. This neither invokes HyperFrames nor EffectCraft nor proves provenance of frames; H-C1 remains BLOCKED.
- `creative_hybrid_graph.py`: source dependency topological planning and cycle rejection, explicit typed parameter bindings, content-based render key binding composition SHA, external asset SHA, output time/fps/dimensions, engine version and color profile; these validations are admitted into `save_hybrid_project_revision` before source storage. No runtime cache, native binding application or actual nested compositor has been built. **H-C3/H-C7/H-C9 partial UNIT_TESTED only.**
- Local RED: unsupported APIs for graph/footage, invalid graph persisted on old store, missing asset/profile key; GREEN: 19 passing and 1 environment-permission skip across 3 new test files. Full scoped regression is to be re-run on exact pushed head and appended to PR; do not extrapolate this subset into CI qualification.


## Full scoped regression (post-continuation source)

Windows isolated `PYTHONPATH=<worktree>` and `HERMES_HOME=C:\Temp\hcw-hybrid01-home` with test runner `C:\Github\hermes-agent-p0-kanban-effects\.venv\Scripts\python.exe`: 26 test files (21 legacy `test_creative_*.py` excluding existing `test_creative_runtime.py` collection/environment issue, plus 5 `test_hcw_hybrid_*.py` files), **121 passed, 1 skipped**, 100.62 seconds, exit code 0. The one skip is a Windows symlink-creation test that could not acquire permission. The test ran on the complete source worktree before the corresponding documentation receipt commit; rerun exact-head qualification before promotion. This is not native engine E2E or Workstation full CI.


### Native engine evidence, 2026-10-12 (development-only)

EffectCraft 0.7.0 CLI executable completed --help and --demo render-frame on Windows, produced real 320x180 PNG. Real native integration pytest creates, saves and reopens .ecproj, imports three generated RGBA PNG frames with file.import, reopens and decodes distinguishable frames at t0 and t0.066667. Python's fixture creates the source RGBA pixels; this is NOT HyperFrames origin proof. Native argv is now generated through effectcraft_import_invocation with executable SHA and confined input/output; execution authority remains in start_creative_process. RED->GREEN seen for missing invocation function. Preliminary 9 passed / 1 platform symlink skip in focused tests, broader exact-head results to follow.

HyperFrames source build: core/parsers/lint/studio-server/producer succeeded; CLI version 0.8.143 exit 0. Full cli build:copy initially failed without studio/dist; separate studio build attempted. Actual CLI render --format png-sequence --strict reached Chrome/lint and aborted with missing_gsap_script, and warnings about id/subcomposition. No HF frames were generated, no joint HF+EC composition, no production promotion. Security-filtered HTML patch was not retried through alternate paths. For checkpoint and exact next tasks see ../HCW_HYBRID_EXECUTION_STATE.md.


### Subsequent native HyperFrames successful transparent fixture

The pinned official HyperFrames 0.8.143 CLI completed full build with exit 0.
Real CLI rendered its existing static transparency-regression source with
--format png-sequence --fps 30 --workers 1 --strict --no-best-effort.
Rendered 30 frames to C:\Temp\hcw-hybrid01-native-smoke\hf-official-alpha,
exit 0. Independent Pillow verification of original PNGs:
mode RGBA, 200x200, alpha min=0 max=255, corner fully transparent,
center opaque red, unique file SHA count=1 because fixture was intentionally
STATIC. No claim of 2s moving HyperFrames animation, EffectCraft composite,
or H-C1 graduation. Full scoped regression newly run: 125 PASSED,
1 Windows symlink SKIPPED, exit 0 in 107.51s over 27 files;
historical YAML-dependent creative_runtime tests remain excluded.


### 2026-10-12 — H-C1 actual pinned producer → native EffectCraft, 60-frame motion, H.264

- Pin: HyperFrames 6ae1af7470133db72de6d9bbceeaf80e85695c68; official unmodified producer/tests/distributed/png-sequence/src/index.html. HyperFrames CLI --strict --no-best-effort: exit 0, 60 PNG RGBA, 640x360, min/max alpha 0..255, seven distinct frame SHA256s, at 30 fps. Validated with workstation.creative_hybrid_footage.validate_rgba_footage.
- Real EffectCraft 0.7.0 CLI: import from those HF frames via typed CreativeInvocation and file.import; saved/reopened .ecproj; decoded seeks show actual different pixels. Additional native edits created "HERMES WORK" text and Gaussian Blur, changed blur scalar 0 to 20; original/text/effect outputs have distinct decoded SHA. Empty blur default was explicitly NOT accepted as proof of a rendered effect.
- Real Hermes CreativeExecutionScope + start_creative_process + ProcessRegistry owner/task/session accepted the import, without monkeypatching approval in this opt-in test; live TaskRun admission outside test is still unproved.
- Actual CreativeDocument native revisions contain real .ecproj + HyperFrames HTML + JSON, ETag-stale edit returns 409; this is not a complete atomic two-engine mutable transaction or Electron shared-editor test.
- Native EffectCraft CLI export produced 640x360 H.264 MP4 at 30 fps / 2.0 s / 60 decoded frames; FFprobe exit 0, FFmpeg extracted both first and later frame exit 0, decoded pixels differ. Native output MP4 SHA256 9d9a264b256fba16a93faa9152c69a50470a18fe74eed7e299ebf3d0b4634c82.
- Tests added: workstation/tests/test_hcw_hybrid_native_cross_engine.py, including real opt-in pinned CLI producer->consumer and independent MP4 validation.
- Scoped 28-file regression 128 PASSED / 1 symlink SKIPPED in 104.86s, exit 0; pinned producer 1 PASSED separately in 49.03s. See HCW_HYBRID_EXECUTION_STATE.md for exact paths and remaining gates.
- **DEVELOPMENT_ONLY**: independent HF native source edit in same project, final TaskRun/Edit UI E2E, 1920x1080 10s demo, full H-079 and CI gates NOT MET. Blocked HTML edit denial was respected; no bypass.


**Final scoped qualification update** (same date): all 28 selected Creative
test files re-executed on final source, with pinned native producer and
FFmpeg verification enabled: **130 passed / 1 skipped / exit 0, 128.07s**.
Not equivalent to full Workstation CI or a complete H-C0 through H-C9 gate.


### 2026-10-12 — canonical multi-revision and live TaskRun command admission

- Two authentic HyperFrames CLI strict 1920x1080 RGBA variants were rendered
  without touching source HTML, driven via JSON parameter files for title,
  subtitle, bgColor. Byte SHA256 of first PNG:
  base 11eec824ec5df58ee7ba135bcef09752a92d6e1300b23b747ac03f5ad0f782d0;
  edited 64d000103394e95d7b477d37bb85b2c9f6714fe012824d1ca64c6b29b834783b.
  Difference bbox (523,397,1400,660), actual visual change.
- Real EffectCraft imported both variants, rendered different pixels,
  then new native text independently changed output. SAME canonical
  CreativeDocument project got three immutable revisions with native
  .ecproj, official unchanged HTML, JSON variable overrides and
  silence.wav (288078 bytes), reopening each, stale ETag rejected.
- Strict declare-only variable validator covered by 9 passing tests,
  rejects unknown/wrong typed/bad colors/non-finite or excessive data.
- New canonical HEAD CAS (opt-in) protects parallel human/agent edits
  under OS lock and durable etag, one winner on race, fault in 3rd command
  of 4 leaves HEAD unchanged; stale and orphan cases fail closed.
  Native files inherited and hash verified when a command changes only
  document metadata/layers.
- Real Kanban TaskRun harness proved live owner, session policy and
  terminal run fence for canonical create/open/apply-batch, with
  real project artifacts and operation receipt. Not a real Electron
  UI round-trip nor verified human actor identity attribution.
- Previous scoped 31-file tests completed 146 passed / 1 skipped.
  A fresh 32-file scoped regression was started under Remote Desktop
  PID 19584; inspect its final status before promoting any test claim.
- No main merge. NOT full H-C0–H-C9 qualification; Electron H-C5,
  distributed native H-C4, 1920x1080 10-second delivery, H-079,
  exact-head CI and full Workstation test suite remain open.

Final verification of this checkpoint: 32 selected Creative pytest files,
151 passed / 1 skipped / 0 failures / 175.02 seconds / exit 0, native
engines enabled. Python Ruff targeted ALL CHECKS PASSED; compileall exit 0.
Release gates (global CI, native UI Editor, H-079) remain open.

### Additional replay correctness receipt

Test RED reproduced an old human command resubmitted after another
agent's canonical revision; prior code refused it as stale. New
per-operation durable receipt index verifies source revision and
published ancestry, replays original receipt only when transaction
digest and expected parent match; mismatched payload and orphan index
fail closed. CAS focused suite 8 passed, exit 0. Global scoped
native pytest PID 75136 pending. No claim of full native
distributed idempotency or Electron authority.

Historical operation replay final qualification: 32-file Creative suite,
152 passed / 1 symlink skip / exit 0 / 158.95s with native engine opt-ins.
Historical human transaction replay after agent commit now returns its
original receipt and does not advance canonical HEAD; altered payload
using same ID returns 409. Native/Electron product gates remain open.


### 2026-10-12 — H-C2 frontend mount and canonical read-model contract (not Electron E2E)

- Previously /creative direct route had no CreativeWorkspaceProvider although
  page used useCreativeWorkspace (runtime error). Route-level Vitest now
  confirms welcome UI mounts with provider; 9 focused UI tests passed.
- Removed duplicate writable local React project state and independent
  $creativeProject nanostore; display state is now accepted ONLY from
  a validated canonical HEAD projection containing revisionId and ETag.
  Selection/playhead remain UI-local, intentionally.
- New pure TS projection maps Python CreativeDocument snake_case to UI
  camelCase and rejects bad project ID/ETag/schema/ranges. Actual Python
  CreativeProjectRevision.etag is quoted 16hex-16hex, found by RED test
  against real serialized Python output. Rational CanonicalTime strings
  are also supported after separate RED test.
- Canonical Python snapshot under temp/isolated profile, tested via Node:
  4 passed, 0 failed, exit 0. UI context/route focused Vitest:
  9 passed, 0 failed, exit 0. Full Electron IPC and UI interaction
  with TaskRun are NOT implemented.
- The upstream npm lock/overrides conflict required isolated
  --legacy-peer-deps/--ignore-scripts install to run UI tests locally.
  No global release qualification is implied.

Final frontend exact-source verification: 9 focused Vitest passed;
4 pure Node/real-Python-schema tests passed; renderer TypeScript
full-project tsconfig --noEmit exit 0; targeted ESLint exit 0;
`git diff --check` exit 0. No Electron IPC binding qualified.

### 2026-10-12 H-C2 Electron fail-closed boundary

New typed IPC handler, restricted preload and React canonical
open/apply display integration. Renderer cannot self-assign TaskRun
session, actor or profile; main rejects all until independently
verified TaskRun binding. Existing 4-file targeted Vitest confirmed
11 passed, exit 0. UI test used synthetic IPC responses; NOT a real
mouse edit/agent edit, native browser session or Electron E2E.
Electron global TypeScript compilation remains blocked by unrelated
existing simple-git type error at git-review-ops.test.ts:124.
H-079 and CI unqualified.

Final targeted verification: 4 Electron/React Vitest files,
11 passed, 0 failed, exit 0; ESLint changed files exit 0.
This verifies typed transport and presentation only. Real manual
editing remains intentionally blocked by null server-trusted owner.
