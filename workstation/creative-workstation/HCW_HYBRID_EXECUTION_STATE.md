# HCW-HYBRID-FINAL — Persistent Execution Ledger

Status: DEVELOPMENT_ONLY / NOT QUALIFIED. Last updated 2026-10-12, America/Sao_Paulo.
Source of mission: HCW-HYBRID-FINAL implementation spec, milestones H-C0 through H-C9.
D-043: Hermes CreativeDocument/TaskRun/revisions/authority are canonical.
EffectCraft and HyperFrames retain editable native source files. Never merge to main without authorization.

## Source control and environment

Repo: kevynlucasprofissional-stack/hermes-agent
Device: DESKTOP-3NA47UH (fdf43006-f9bb-4933-98bc-6c6c76e9f2c4)
Worktree: C:\Github\hermes-agent\.worktrees\hcw-hybrid-01
Branch: feat/hcw-hybrid-01-20261011
Starting HEAD: 456f62f583aef8c1ac2afe8a64b62d987ac521bf
PR: https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/81 (draft, unmerged at session start)
Main checkout C:\Github\hermes-agent on fix/hermes-oneclick-lock-startup-20261011 at 9fffa7f3ffcc2c50774654c271fe25e92ce459e8 with 34 local dirty changes. PRESERVE ALL.
Recheck remote/local SHAs, dirty files and ongoing processes on each resume.
Two documentation files in this worktree were dirty BEFORE this session:
workstation/context/engineering-journal/CURRENT.md and
workstation/creative-workstation/evidence/HCW-HYBRID-01.md.
These are previous-session evidence, not unrelated user edits.

## Newly verified in this session

- EffectCraft executable: C:\Temp\hcw-hybrid01-effectcraft-target\debug\effectcraft-cli.exe.
  Real binary, 100561920 bytes observed. CLI --help and --demo info returned exit 0.
  Native demo render-frame produced actual 320x180 PNG under
  C:\Temp\hcw-hybrid01-native-smoke\demo-frame.png.
- Added workstation/tests/test_hcw_hybrid_native_effectcraft.py.
  With EFFECTCRAFT_CLI configured, created an actual .ecproj via comp.new,
  saved and reopened it, rendered and decoded a real PNG.
  A separate test imported a THREE-FRAME Pillow-made RGBA test fixture using
  the EffectCraft file.import sequence command, reopened the new .ecproj,
  decoded frame 0 and frame 2, and verified unequal pixels. This is actual
  EffectCraft engine behavior; the footage is NOT HyperFrames output.
- Added effectcraft_import_invocation to workstation/creative_hybrid_footage.py.
  Builds the exact typed, fingerprint-pinned CreativeInvocation for the EXISTING
  workstation.creative_process.start_creative_process supervisor. Checks path
  containment, source project presence, destination not-existing and .ecproj types.
  TDD red: missing method; green: native test executes its argv successfully.
- Native + footage tests on this source: 9 PASSED, 1 Windows symlink permission
  SKIPPED; exit code 0. Environment: EFFECTCRAFT_CLI set to the binary above;
  HERMES_HOME=C:\Temp\hcw-hybrid01-home and PYTHONPATH=worktree.
- HyperFrames official pinned checkout:
  C:\Temp\hcw-hybrid01-hyperframes-src at
  6ae1af7470133db72de6d9bbceeaf80e85695c68.
  Prior bun install --frozen-lockfile --ignore-scripts installed 1457 packages.
  This session built packages/core, packages/parsers, packages/lint,
  packages/studio-server and packages/producer with exit 0.
  packages/cli dist built but full build:copy failed because packages/studio/dist
  was missing. packages/studio subsequently finished with exit 0 (DTS generation succeeded).
  The full packages/cli build was retried afterward; verify its final exit code before qualification.
  The official built CLI returned version 0.8.143 and exit 0.
- First HyperFrames png-sequence render attempted from isolated temp fixture
  C:\Temp\hcw-hybrid01-native-smoke\hyperframes\index.html.
  CLI found Chrome, but --strict correctly failed with missing_gsap_script
  (error), plus studio_missing_editable_id and
  nested_structure_needs_subcomposition (warnings). Exit 1. ZERO HF frames
  produced or imported. The bundled GSAP distribution was copied from pinned
  node_modules to temporary project's assets, SHA-256
  92bb9a96476f983d212a2bc4f54c889039c1696dd4461d40a736860938570fbb.
  A remote edit_block attempt to change the source HTML was denied by platform
  security: do NOT evade the block. Use an already valid independent source
  fixture if duly authorized, or request explicit assistance with that blocker.
- Expanded Creative scoped regression with real EffectCraft opt-in on this
  session's new source: 27 test files, 125 PASSED, 1 SKIPPED (symlink),
  107.51s, exit 0. Existing test_creative_runtime.py was intentionally excluded
  due to the preexisting YAML collection/environment defect. This is not full CI.

## Milestone status (not product completion)

H-C0: BLOCKED/PARTIAL NATIVE — EC runs with PNG and .ecproj; HF CLI runs but no HF-frame proof.
H-C1: UNIT_TESTED/PARTIAL ENGINE — actual EC import validated, no HF->EC complete.
H-C2: UNIT_TESTED — linked natives persist, UI/IA canonical bridge absent.
H-C3: UNIT_TESTED — rational time and typed bindings; native engine sync absent.
H-C4: NOT_IMPLEMENTED — atomic cross-engine human+AI durable command history.
H-C5: NOT_IMPLEMENTED — EffectCraft Web in Electron and authoritative bridge.
H-C6: UNIT_TESTED partial — RGBA contract and EC import; effects/mattes E2E absent.
H-C7: UNIT_TESTED — content fingerprints, no cache/invalidation in runtime.
H-C8: NOT_IMPLEMENTED — hybrid on-demand frame renderer.
H-C9: UNIT_TESTED — DAG checks, no native nested rendering and final suite.

## Next execution priority

1. Packages/studio build exited 0. A new packages/cli build was started
   after Studio became available; read the process log and exact exit code.
2. Reconcile the HyperFrames --strict lint blocker by approved modifications or
   a preexisting valid reference sample without evading a tool security denial.
   Run official png-sequence producer, validate 60 frames with real alpha/motion.
3. Feed that genuine HF footage to EffectCraft using
   effectcraft_import_invocation and the existing TaskRun-owned process supervisor.
   Save and reopen real .ecproj; prove both EC edit and HF source edit produce
   changed composited output. Keep engine-native originals. H-C1 not yet done.
4. Independently start canonical human/AI document + command bridge from PR #77.
   No second authoritative React store, no blind PR merge.
5. Implement multi-layer verified export, bindings, cache, WebContentsView and
   nested comp after native vertical proof.
6. Run scoped regressions, exact-head CI, H-079 gate; preserve main and PR draft.

## Mandatory recursive handoff

Before ending an incomplete session: recheck git status, exact local/remote SHA,
processes, tests and artifacts; update this ledger and evidence, commit safely,
push to draft PR, and give the user an AUTONOMOUS, READY-TO-COPY PROMPT carrying
the state above, first executable action, constraints, dependencies and a rule
to generate an updated continuation prompt if H-C0–H-C9 remain incomplete.


## Addendum — later proof from this same session

- Studio build ultimately returned STUDIO_BUILD_EXIT=0 (Vite and DTS).
- Full HyperFrames CLI build retried and returned HF_CLI_BUILD_EXIT=0.
  Its build-copy phase warned that optional skills/gsap and player bundles were
  not present; this did not change the zero exit code.
- Official existing HyperFrames fixture, with no remote CDN:
  packages/producer/tests/transparency-regression/src/index.html
  was rendered by the real HyperFrames CLI as:
  node packages/cli/bin/hyperframes.mjs render <fixture>
    --format png-sequence --output C:\Temp\hcw-hybrid01-native-smoke\hf-official-alpha
    --fps 30 --workers 1 --strict --no-best-effort
  This completed with HF_OFFICIAL_FIXTURE_EXIT=0 and 30 PNG frames.
  Independent Pillow verifier at
  C:\Temp\hcw-hybrid01-native-smoke\verify_hf_frames.py returned exit 0:
  PNG RGBA, (200,200), alpha extrema (0,255), corner (0,0,0,0),
  center (255,0,0,255); FRAME_COUNT=30; UNIQUE_FILE_SHA=1.
  IMPORTANT: the fixture is STATIC, not animated. This is native HF render
  and alpha proof, not proof of motion or end-to-end EffectCraft composition.
- Native EffectCraft/Python regressions on this session source: 27 test files,
  125 passed / 1 skipped, 107.51 seconds, exit 0.
- Next H-C1 blocker: obtain a valid authorized 2s 30fps actual-moving
  transparent HyperFrames project (do not circumvent the HTML editing denial),
  then pass it through validate_rgba_footage and native EffectCraft importer.


## 2026-10-12 continuation — actual native HyperFrames -> EffectCraft tracer

Status remains DEVELOPMENT_ONLY; do not promote H-C0 through H-C9 as a whole.
Starting local/remote HEAD was fe8d5a7c5f02529e7ca2055c7abb05497c1b7dea.
Starting worktree was clean; main checkout had 34 local dirty changes and was NOT modified.

New reproducible test file:
workstation/tests/test_hcw_hybrid_native_cross_engine.py

An **unchanged**, already-authorized official fixture at
C:\Temp\hcw-hybrid01-hyperframes-src\packages\producer\tests\distributed\png-sequence\src\index.html
was rendered by the pinned HyperFrames 0.8.143 CLI (SHA 6ae1af7470133db72de6d9bbceeaf80e85695c68)
with --format png-sequence --fps 30 --workers 1 --strict --no-best-effort.
Exit 0, 60 PNG RGBA frames at 640x360, alpha 0..255, 7 distinct frame SHA256 hashes;
validate_rgba_footage confirmed real alpha, visible content and frame motion.
Native output under C:\Temp\hcw-hybrid01-native-smoke\hf-official-motion.
Frame samples (source PNG bytes):
frame 0: 7c0beac5c1c48a2e56...;
frame 29: 9076ddeb6edd96fcfe...;
frame 30: 25da3f1f6b1ceabb00...;
frame 45: a9d24afea6070801e6...
Full hashes can be recalculated from surviving files; these prefixes are not substitutes.

The verified native EffectCraft .exe imported the 60 real HyperFrames PNGs using
effectcraft_import_invocation, saved/reopened a real .ecproj, and rendered different
pixels when seeking frames 0, 30 and 45; explicit opt-in pytest passed.
A standalone pinned producer->consumer test recreated the actual render from the
official untouched HTML and immediately imported into EffectCraft: 1 passed in 49.03s,
zero failure. No synthetic/mocked renderer.

EffectCraft source edits using engine commands created an actual Text layer with
"HERMES WORK", applied "Gaussian Blur" to the imported footage, then changed
effects/#1/blurriness from 0 (same pixels) to 20 (distinct pixels). All .ecproj
variants saved and reopened. Actual RGBA pixels differed between original, text,
and blurred compositions. Scripts/results under
C:\Temp\hcw-hybrid01-native-smoke\effectcraft-enrichment,
not the Hermes repo. source .ecproj SHA256 for final blurred project:
98e9664f8c84c2f31ee0ead8175c343c58fdfe8b3916a206d13a491c51bede48.

Real supervisor test exercised start_creative_process with matching
CreativeExecutionScope, ScopedPolicyEngine, command guards and ProcessRegistry,
without mocking approval, verifying owner_task_id/session_key and native import.
Two supervised+cross-engine tests: 2 passed in 27.86s.
This is proof of the task-scoped PROCESS seam, not full live TaskRun admission.
Canonical CreativeDocument E2E with actual native .ecproj and unchanged real
HyperFrames HTML saved/reopened immutable revisions, changed EC native via
parent ETag and rejected stale ETag (409). Three native tests: 3 passed in 19.71s.

EffectCraft's real CLI rendered the composited final .ecproj to H.264 MP4:
C:\Temp\hcw-hybrid01-native-smoke\effectcraft-enrichment\hermes-hybrid-native.mp4
CLI exit 0. FFprobe independent exit 0: codec h264, 640x360, yuv420p,
30/1 FPS, 2.000000 seconds, 60 decoded frames, 49570 bytes.
MP4 SHA256: 9d9a264b256fba16a93faa9152c69a50470a18fe74eed7e299ebf3d0b4634c82.
FFmpeg independently decoded first and later frames, exit 0 both times;
pixels differ (separate decoded SHA 9f4212e8... and fe07a645...);
verified 2s video contains actual visible motion. Repeatable opt-in
native ffprobe/ffmpeg regression has also been added.

Fresh SCOPED 28-file Creative regression (collected before the opt-in producer
and video tests were appended): 128 passed, 1 symlink skip, 104.86s, exit 0.
Additional pinned producer 1 passed separately.
No complete Workstation CI run and no H-079 Stage A qualification.
test_creative_runtime.py historically excluded due to missing YAML in this venv.

**Do NOT overclaim H-C1 as fully qualified:** independent change to the
HyperFrames source in the SAME bound composition and live Electron human/AI
round-trip are still absent. Previous remote HTML edit_block was denied by
platform security and must not be circumvented. Reuse authorized source, or
qualify a supported declared-variable edit instead; mark exactly what that
does and does not prove.

Current milestone updates:
H-C0 PARTIAL: both real engine binaries and real output verified; H-079 missing.
H-C1 NATIVE_VERTICAL_PROVEN / BLOCKED_FOR_PROMOTION: real moving HF frames ->
EC import/edit/frame/MP4; no HF source mutation in same project, no live TaskRun E2E.
H-C2 PARTIAL INTEGRATION TESTED: real native sources in canonical document
revisions, stale ETag; no full human/AI interface bridge or global atomic CAS.
H-C3 UNIT_TESTED: rational times/typed bindings; no native two-way binding.
H-C4 NOT_IMPLEMENTED: durable multi-engine atomic command.
H-C5 NOT_IMPLEMENTED: EffectCraft Web in Electron.
H-C6 PARTIAL NATIVE: text and real non-default blur; full mattes/keying unproved.
H-C7 UNIT_TESTED fingerprints only; bounded runtime cache missing.
H-C8 NOT_IMPLEMENTED: native on-demand composite renderer.
H-C9 UNIT_TESTED graph planning; native nested render and 1920x1080 10s demo missing.

Next: check exact latest HEAD/status, verify fresh tests on final head; update this
ledger for every continuation. Resolve real independent HF source edit through an
authorized mechanism, then TaskRun admission and Electron shared editing/CAS;
do not merge main, respect H-079 and CI, and leave a recursive handoff prompt
whenever incomplete.


### Final exact-source local regression — 2026-10-12

After appending the last opt-in native MP4/export test and native pinned
producer->consumer test, the full scoped suite of 28 files was re-executed
with EFFECTCRAFT_CLI, HYPERFRAMES_MOTION_FRAMES,
HYPERFRAMES_OFFICIAL_CHECKOUT, HYPERFRAMES_NODE,
EFFECTCRAFT_ENRICHMENT_DIR, HYPERFRAMES_SOURCE_HTML, PYTHONPATH and isolated
HERMES_HOME configured. **130 passed / 1 skipped / 0 failed in 128.07s,
FINAL_SCOPED_EXIT=0**, pytest process exit 0.
The skipped test requires Windows symlink privilege. This is scoped Creative
regression, not global Workstation CI. test_creative_runtime.py remains
intentionally omitted due pre-existing missing YAML dependency in this venv.
User's main checkout remained outside this worktree and was not edited.


## 2026-10-12 resumed implementation — canonical create/open/apply-batch and durable CAS

Started from PR #81 HEAD 5638aeee6610cd038c80c2febbe3b56a10c7d896,
isolated worktree feat/hcw-hybrid-01-20261011. Main checkout remained
at 9fffa7f3ffcc2c50774654c271fe25e92ce459e8 with 34 dirty
entries and was NOT modified. GitHub PR #81 remains OPEN/DRAFT.

Previously UNCOMMITTED changes in this worktree at session resumption:
workstation/creative.py; creative_project_runtime.py; new
creative_hyperframes_variables.py; creative_revision_cas.py; and
test_hcw_hybrid_native_variables_roundtrip.py,
test_hcw_hybrid_revision_cas.py,
test_hcw_hybrid_taskrun_command.py,
test_hcw_hybrid_variables.py. Preserve and publish after verification.

This checkpoint's completed behavior:
- Official HyperFrames variables-prod template with title, subtitle and
  bgColor declared parameters; strict --variables-file CLI overrides leave
  original HTML immutable. Two actual producer captures: 6 RGBA PNG frames
  each at 1920x1080, comparison bbox (523,397,1400,660), true byte
  difference. First frame SHA256:
  base 11eec824ec5df58ee7ba135bcef09752a92d6e1300b23b747ac03f5ad0f782d0
  edited 64d000103394e95d7b477d37bb85b2c9f6714fe012824d1ca64c6b29b834783b.
- workstation.creative_hyperframes_variables.validated_hyperframes_overrides
  implements declared-variable allowlist, simple type checks, strict
  canonical JSON, payload budgets; native source never rewritten.
- Native opt-in test imports both genuine HF producer variants into real
  EffectCraft, confirms differing render pixels, adds independent
  EffectCraft text, saves and reopens three revisions of SAME project
  with true native .ecproj, HTML, JSON variable override and silence.wav.
  Real 288078-byte silence.wav native dependency was added after RED
  FileNotFoundError and passed GREEN; no synthetic source. H-C1
  engine+canonical multi-revision edit evidenced, but NOT Electron UI.
- New independent workstation.creative_revision_cas supports
  HEAD pointer under project, OS interprocess lock, expected HEAD and
  ETag, transaction idempotent replay with payload fingerprint, refusal
  of stale and simultaneous siblings; fail closed on orphan/legacy
  revision lineage without a HEAD marker. This is a NEW opted-in
  publication path, not a retrofit of all existing legacy writers.
  Test concurrency confirmed one success and one 409; TDD RED/GREEN.
- publish_creative_command_batch_cas applies existing CreativeTransaction
  atomically in cloned CreativeDocument, stores digest receipt and
  then updates HEAD. Fault in third of four commands leaves prior HEAD.
  Human and agent actors sequentially update one revision chain. Actor
  labels are CLIENT-SUPPLIED metadata, not yet identity-attested.
- publish_creative_command_batch_for_run validates ACTUAL live Kanban
  TaskRun and workspace, canonical policy and owner journal before
  publishing. Failure after committing revision raises
  CreativeEffectUncertain. If editing hybrid document, it carries
  forward hashed native files from previous revision, preserving
  EffectCraft, HF HTML/JSON, other assets, with test.
- CLI workstation.creative now has canonical-create, canonical-open
  and apply-batch behind --task-id and --run-id, operating on bounded
  workspace-confined documents/command files; source and commands
  are not independent authority. Integration test proved
  create -> open -> command batch -> open, with negative outside
  workspace, wrong session, terminated task and immutable history.
- Baseline targeted followup: 4 passed in 18.62s on real TaskRun
  command tests. Other CAS 7 green; source/native additional tests green.
  FULL CURRENT scoped regression was STARTED in separate Remote Desktop
  process PID 19584 across 32 Creative test files including native opt-in
  engines; READ ITS FINAL EXIT AND COUNTS BEFORE CLAIMING FINAL STATUS.
  Test creative_runtime.py remains excluded for the preexisting
  missing YAML dependency in this venv.

Current H-C:
H-C0 PARTIAL (native CLIs proven, H-079 gating missing).
H-C1 NATIVE_ENGINE_AND_CANONICAL_REVISION_PROVEN (real HF declared
parameters and EC native text update each change rendered pixels; no
Electron human manual editor E2E; no overall qualification).
H-C2 BACKEND CANONICAL CLI_INTEGRATED (one project, CAS HEAD,
immutable revisions, TaskRun input; React still has local owner state).
H-C3 PARAMETER_NATIVE_INTEGRATED_PARTIAL (strict declared HF override;
no full two-way property binding/time editor).
H-C4 BACKEND_CAS_BATCH_INTEGRATED_PARTIAL (cross-process HEAD CAS,
idempotent commands, TaskRun admission and batch rollback; no
distributed native dual-engine transaction/undo or editor identity).
H-C5 NOT_IMPLEMENTED (EffectCraft Web / Electron).
H-C6 PARTIAL NATIVE (text and blur real; mattes/keying pending).
H-C7 UNIT_TESTED fingerprints; no runtime cache.
H-C8 NOT_IMPLEMENTED on-demand hybrid compositor.
H-C9 UNIT_TESTED DAG; nested runtime and 1920x1080/10s final demo pending.

Critical gates: D-043 Hermes is ONLY project authority; native EC and HF
sources editable; preserve no-placeholder verification. H-079 and
exact-head CI required before qualification. PR stays draft, NO MERGE.

Next executable priorities:
1. Read PID 19584 final pytest output; debug any regressions.
2. Finish cross-platform security review, check git diff --check/lints.
3. Commit only scoped changes and this ledger in isolated worktree,
   push branch, confirm SHA and GitHub draft PR.
4. Start H-C2 UI convergence using React PR #77 types / provider and
   canonical backend RPC, without creating competing authoritative state;
   next tracer test: actual Electron UI human edit -> existing live
   TaskRun canonical-create/open/apply-batch -> Hermes agent edit same
   revision -> renderer refresh via canonical-open, test restart.
5. H-C4: durable undo/redo and genuinely atomic engine native staging;
   concurrent process CAS stress test; close actor identity attribution.
6. H-C5 onward as in roadmap, H-079/CI before main promotion.
7. At every incomplete session, produce another SELF-CONTAINED copyable
   continuation prompt with verified SHA, test receipts, process state,
   blockers and first exact executable step.

### Final scoped test and code quality receipt (same source, 2026-10-12)

All 32 selected Creative test modules (native HyperFrames and EffectCraft
opt-ins enabled) completed: **151 passed, 1 Windows symlink skip, 0 failed**,
175.02 s, FINAL_SCOPE_EXIT=0. This is scoped pytest, NOT full product CI,
Electron E2E or H-079 approval. The prior CLI TaskRun-only suite was
4 passed in 18.62 s. Python compileall exit 0, Ruff 0.15.10 targeted
8 Python files ALL CHECKS PASSED, git diff --check exit 0.
No main worktree mutation or merge. The new APIs are opt-in, NOT yet
wired to a real Electron manual editor. No claim of verified actor ID;
actor_type is trace metadata, subject to future trustworthy identity binding.

### Same-date continuation — historical operation replay durability

After commit 886d50918f632e58bc5ec434afe996a0f603b1f0, an additional
H-C4 failure mode was reproduced RED: a completed human batch replayed
after an intervening agent edit returned 409, instead of its prior
receipt. New test in test_hcw_hybrid_revision_cas.py confirmed RED.
The canonical CAS now stores immutable operation-id keyed receipt files
in the project's operations directory before swapping HEAD. An operation
receipt is only eligible for idempotent replay if its verified revision
belongs to the current published HEAD lineage; interrupted/orphan
records are refused. Exact command digest and original parent revision
must match. Fresh publications check receipts by direct filename lookup
(O(1), ancestry traversal only on replay). This fixes historical replay
without duplicate new revisions or spoofed payload acceptance.
8 tests in test_hcw_hybrid_revision_cas.py PASSED, 0 failed, exit 0.
A full 32-file native Creative scoped suite was started with
Remote Desktop PID 75136 and MUST be read for final exit and result.
No UI/Electron live co-editing, global CI, H-079 or 10s 1080p
qualification claimed.

### Verified subsequent historical CAS replay regression, 2026-10-12

Final scoped pytest re-executed with real EffectCraft/HyperFrames opt-ins,
32 Creative test modules: **152 passed, 1 Windows symlink skip, zero failures**,
158.95s, CAS_FINAL_TEST_EXIT=0. New historical operation replay test passed
and older 8 CAS tests green. Ruff and Python compileall for modified CAS
and tests also passed, git diff --check exited 0. Still missing full CI,
H-079, Electron manual UI and user identity proof. Commit/push this
post-886d50918f correctness fix separately.


## 2026-10-12 frontend H-C2 continuation — read-only canonical HEAD projection

Started with confirmed PR #81 draft HEAD
62dc14f66f9c3e3770c1feab75499af5c84d4e93,
isolated worktree clean; checkout C:\Github\hermes-agent at
9fffa7f3ffcc2c50774654c271fe25e92ce459e8
with 34 unrelated dirty entries preserved.

NEW FRONTEND OBSERVATIONS AND CHANGES:
- /creative route in apps/desktop/src/app/contrib/surfaces.tsx mounted
  CreativeWorkspacePage with NO CreativeWorkspaceProvider. The use hook
  requires this provider and would throw. Fixed Page to mount provider
  before rendering CreativeWorkspaceBody. Existing route test extended;
  focused UI Vitest 9 passed / 0 failed, exit 0.
- The React context had TWO local project copies (useState plus
  $creativeProject nanostore) plus unrestricted setProject, with neither
  tied to an acknowledged backend CreativeDocument. Removed both writable
  local-project controls. Added acceptCanonicalHead(unknown) which validates
  the backend HEAD and only projects it for display, exposing immutable
  revision ID/ETag; clearCanonicalHead discards display state.
  Selection/playhead/workspace panel state remains local UI state.
- Added apps/desktop/src/app/creative-workspace/canonical-creative-projection.ts
  and a standalone Node test suite plus Vitest context tests. Strict
  input/schema/project ownership/range validation, projected React
  camelCase shapes from authentic Python snake_case schema. A direct
  Node runtime test proved RED missing module then GREEN.
- An additional RED regression established that fractional CanonicalTime
  strings such as 1001/30000 were wrongly rejected. Renderer projection
  now accepts bounded rational-seconds strings and preserves fps 30000/1001.
- A REAL backend CreativeProjectRevision was generated in an isolated
  HERMES_HOME using workstation.creative_revision_cas and
  workstation.creative_document; live JSON snapshot at
  C:\Temp\hcw-hybrid01-native-smoke\canonical_real_head.json
  (test script canonical_real_head_smoke.py). This revealed another RED:
  actual strong ETag is QUOTED "revision_id[:16]-source_sha256[:16]",
  NOT a 64-digit SHA. Fixed projection validator to match the
  real Python CreativeProjectRevision.etag contract.
  The actual Python-backed Node smoke suite: 4 passed, exit 0.
- Isolated Windows Node dependencies were missing @rolldown/plugin-babel.
  npm ci failed due package-lock/overrides mismatch; a normal isolated
  install failed on upstream React/Ink peer conflicts. Installed 1541
  packages into this WORKTREE only using npm install --legacy-peer-deps
  --ignore-scripts --no-save --package-lock=false --no-audit --no-fund,
  exit 0. This is a local testing accommodation, NOT qualification of
  dependency lock or release reproducibility. Main checkout untouched.
  No package lock update in git status.
- Last UI Vitest targeted: 9 passed / 0 failed, exit 0;
  TypeScript renderer tsc is being rerun on final source in Remote
  Desktop process PID 62912; inspect final output before claiming final
  typecheck. ESLint fixes were applied to changed frontend source and
  rerun in focused scope; final ESLint run exited 0.

**HIGH-PRIORITY UNFINISHED CONTRACT:** No actual Electron main/preload
CreativeDocument IPC and no valid backend gateway API creative route
were found during focused inspection. No renderer UI element invokes
canonical-open, apply-batch or TaskRun admission yet; page may still
show empty state because no canonical snapshot is loaded from backend.
The context's acceptCanonicalHead is ONLY a display adapter; values
supplied by JS are NOT server authority. Do not claim manual/agent E2E.
The real backend TaskRun CAS/CLI implemented before this session is
unchanged and remains available. Do NOT create shell/terminal IPC allowing
arbitrary commands or trust renderer-supplied actor identity.

Updated milestone labels:
H-C0 PARTIAL, H-079 / CI absent.
H-C1 INTEGRATED_NATIVE_E2E+CANONICAL_REVISIONS_PARTIAL, no Electron UI.
H-C2 FRONTEND_READ_MODEL_TESTED + TASKRUN_BACKEND_TESTED, actual IPC
and combined human/agent UI round trip NOT implemented.
H-C3 PARTIAL: true rational time display + HF typed native variables,
two-way native binding not complete.
H-C4 BACKEND_CAS_TESTED, no Electron manual editor / trusted actor identity,
no native distributed atomicity / undo-redo fully done.
H-C5 NOT_IMPLEMENTED Electron EffectCraft WebContentsView.
H-C6 PARTIAL native typography+blur; mattes/keying not qualified.
H-C7 UNIT_TESTED fingerprint, runtime cache missing.
H-C8 NOT_IMPLEMENTED frame-on-demand hybrid engine.
H-C9 UNIT_TESTED graph; 1920x1080 10s final delivery not qualified.

Next executable steps:
1. Finish final UI tsc verification PID 62912, rerun scoped tests
   if source changed after it; check git diff --check.
2. Commit just scoped frontend changes and documentation to isolated
   feat/hcw-hybrid-01-20261011, push and verify remote SHA, keep PR draft.
3. Implement the MISSING SECURE IPC or existing gateway API route. First
   trace main-process session ownership and actual TaskRun identity;
   do not accept renderer-provided session key/actor identity or
   command paths. Write RED tests for actual Electron main -> real
   Python canonical-open/apply-batch and fixed authorized owner before
   registering any channel. Reuse existing authority/policy. No
   arbitrary subprocess/shell API to untrusted renderer.
4. Call this new safe IPC from the React CreativeWorkspaceProvider,
   require acknowledged HEAD and ETag for EVERY edit, and read back
   authoritative HEAD after edits/restart. Remove any optimistic local
   project changes. Test human click then agent command then refresh.
5. Continue H-C4 identity/transactions, H-C5+ other milestones,
   full Electron E2E, H-079, exact-head CI, then eventual authorized merge.
6. On EVERY incomplete ending, produce a complete self-contained,
   ready-to-copy continuation prompt with exact SHA, tests, blockers
   and this same recursive obligation.

Final H-C2 frontend validation receipt: targeted ui vitest **9 passed**,
2 test files, UI_FINAL_VITEST_EXIT=0 (lazy route tests printed existing
React act warnings but no test failure). Python-generated genuine
CreativeProjectRevision HEAD fed to Node native .ts ESM test suite:
**4 passed**, NODE_REAL_HEAD_FINAL_EXIT=0; source schema, ratio seconds,
real quoted ETag and negative cases covered. Scoped frontend TypeScript
`tsc -p tsconfig.json --noEmit` **UI_FINAL_TYPECHECK_EXIT=0**
(118.34s). Targeted ESLint --fix completed UI_FINAL_ESLINT_EXIT=0;
`git diff --check` exit 0. Main checkout and lockfile untouched.

## Continuation 2026-10-12 — Electron H-C2 typed bridge (NOT live manual edit)

Starting HEAD PR #81: 4af6c1177b0420063dbb84bc6f1ee67005369ac4.
Isolated creative worktree was clean. Root C:\Github\hermes-agent at
9fffa7f3ffcc2c50774654c271fe25e92ce459e8 and 34 dirty user changes
was not edited.

New Electron creative-canonical-ipc.ts: allowlist of two typed
CreativeCommands (layer.create, layer.setProperty), exact envelope/param
keys, bounded strings/IDs, no arbitrarily executable shell/FS access.
Rejects injected renderer actor/session/task/owner metadata, untrusted
renderer WebContents, missing trusted owner and backend 409 conflicts.
Checks Python project_id/revision_id/source and strong quoted ETag
before returning a post-command canonical HEAD; renderer receives no
optimistic success without backend readback. TDD RED/GREEN verified.

preload.ts exposes ONLY creativeCanonical.open/apply. main.ts registers
two IPC channels but deliberately resolves main-attested TaskRun owner
to null, as a secure connection between THIS renderer and live TaskRun
has not yet been qualified. Consequently current real app refuses every
creative mutation with creative_owner_unavailable. This is security
intent, NOT a working manual editing E2E.

React CreativeWorkspaceContext now provides openCanonicalProject and
submitCanonicalCommand; both project by projectFromCanonicalHead only
after backend result, with crypto.randomUUID transaction IDs and no
local mutation of the canonical CreativeDocument. Context test with
simulated trusted IPC readbacks confirmed revision changes in view.
No real server/agent/editor E2E was run; do not promote H-C2.

TDD baseline RED: nonexistent bridge, preload field, React method,
response field naming mismatch and unregistered sender gate. Final
selected Vitest 4 files, 11 passed / 0 failed / exit 0.
Renderer tsc -p tsconfig.json --noEmit exit 0 (before final lint fixes).
Electron global tsc -p tsconfig.electron.json --noEmit exit 2 due
PREEXISTING unrelated git-review-ops.test.ts:124 simple-git module
typing; no new Creative source error was emitted.
ESLint scoped autofixes applied to new files; final lint receipt to
be rechecked after last scoped fixes. No H-079, CI, app E2E, or main merge.

H-C0 partial; H-C1 integrated native/canonical revision tests, not
end-user app; H-C2 READBACK_UI+IPC_TRUST_CONTRACT_TESTED / LIVE_OWNER_BLOCKED;
H-C3 partially native variables and rational time; H-C4 backend
CAS/TaskRun exists, Electron authenticated actor not wired and native
cross-engine distributed atomicity missing; H-C5 NOT_IMPLEMENTED;
H-C6 partial native; H-C7 fingerprint only; H-C8 missing on-demand
renderer; H-C9 no native nested/1920x1080 10s end-to-end final demo.

First next executable action: bind Electron renderer to a verified
server-owned TaskRun without accepting renderer-supplied session,
actor_id, task_id or profile data. Add real backend typed
canonical-open/apply gateway route under existing dashboard auth and
TaskRun authority. Inject authenticated owner resolver in main only
after independent E2E verification; then run true mouse->CAS->agent
same document->reload->restart/human lease negatives. Keep current
fail-closed resolver until qualification. No arbitrary shell IPC.

Every incomplete session must produce a self-contained ready-to-copy
continuation prompt with HEAD, tests, pending blockers, first exact
step and this same recursive obligation until H-C0-H-C9 are qualified.

### Final scoped H-C2 IPC validation receipt — 2026-10-12

4 targeted Electron/React Vitest files: 11 passed, 0 failed,
HCW_UI_FINAL_VITEST_EXIT=0. Selected changed-file ESLint:
HCW_UI_FINAL_LINT_EXIT=0. Renderer tsc verified earlier exit 0.
Global Electron tsc fails only on previously present unrelated
simple-git type mismatch in git-review-ops.test.ts:124, exit 2.
No trusted TaskRun owner binding, no genuine main-to-backend canonical
RPC and no user/agent Electron E2E. The new main bridge is fail-closed.
No full app CI or H-079 release qualification performed.


## 2026-10-12 14:38+ continuation — Electron IPC sender attestation hardening

Observed PR #81 remote HEAD 4af6c1177b0420063dbb84bc6f1ee67005369ac4
at session start, but LOCAL clean worktree on
2c58391db5cd085f138d0f0de4f82a49d5966c6f,
one already-committed change ahead of remote. This local commit introduced
creative-canonical-ipc.ts and renderer/preload readback transport. Preserve it;
do not rewrite old head, and push normally after checks.

New TDD test cases in apps/desktop/electron/creative-canonical-ipc.test.ts:
- Main resolves TrustedCreativeOwner per IPC sender, not global last window.
- Reattest TaskRun owner after asynchronous commit/read and refuse head if
  sender's owner changes midflight.
- Never confirm a canonical edit merely because a syntactically valid head
  was readable; require typed commit receipt project_id/revision_id and
  exact matching canonical HEAD revision, refusing stale/no-op receipts.
- Admission of sender rechecked at every asynchronous owner resolution:
  navigation/close during commit fails acknowledgement before readback.
All critical defects were first observed with RED failing tests; GREEN targeted
Vitest creative-canonical-ipc and preload: 11 passed, 0 failed, exit 0.
Targeted ESLint exit 0 after scoped formatting.
Electron TypeScript-wide noEmit still has unrelated pre-existing
electron/git-review-ops.test.ts:124 simple-git callable type error;
do not claim full TypeScript typecheck pass.

CRITICAL: apps/desktop/electron/main.ts registers canonical IPC with
resolveTrustedOwner: () => null. This remains intentionally DENY ALL:
no backend-authenticated TaskRun owner bound to admitted individual
Electron webContents has been identified/implemented. Thus NO real Electron
mouse -> TaskRun -> canonical CAS end-to-end has passed. Do NOT change
this to TaskRun/session IDs supplied by renderer, ambient profile guesses or
an arbitrary subprocess/CLI path. This security prerequisite is explicitly
P0A of the plan review saved in:
workstation/creative-workstation/HCW_HYBRID_PLAN_REVIEW_2026-10-12.md.
P0B real UI + Hermes agent sequential writes remains immediately next.
H-C2 is BACKEND+UI_CONTRACT_TESTED, NOT LIVE_E2E/QUALIFIED.
No other H-C0-H-C9 promotion from this scoped IPC work.

Protected main checkout C:\Github\hermes-agent remains at
9fffa7f3ffcc2c50774654c271fe25e92ce459e8 with 34 dirty changes
as observed at session start. No main merge authorized.

Next session first executable actions: verify exact local+remote heads after
push, preserve root dirt, locate/implement **backend-attested** TaskRun owner
per main-owned sender+profile/connection/session, add RED tests for forged
and stale authority, then wire bounded main IPC to existing authenticated
canonical-open/apply-batch. Verify manual UI edit -> agent edit same HEAD and
restart before marking H-C2 complete. No global UI state or shell path accepted.
Recursive self-contained copy-paste continuation prompt required if incomplete.

## 2026-10-12 P0A continuation — attestation verifier, NOT live authority

Starting local/remote HEAD a3527baa7a960db7ac712c9c726fb8ef176e3678; isolated worktree clean, draft PR #81 open, main untouched. Added apps/desktop/electron/creative-taskrun-attestation.ts and corresponding .test.ts. TDD RED missing module (Vitest exit 1); GREEN 14 new tests and 11 creative IPC/preload regression tests: 25 passed, exit 0. Validates per-window main-owned webContentsId, navigation epoch, connection, profile and session against an authenticated-backend attestation; rejects ended/revoked run, human control lease, missing actor principal, bad expiry and async scope drift. This verifier does NOT mint authority. Production main.ts resolveTrustedOwner: () => null remains DENY-ALL. Real backend attestor + main scope registry + Electron UI/CAS E2E remain missing. No H-C0–H-C9 promotion. Next: implement authenticated gateway TaskRun/actor/lease attestation; bind main per-window sender; use verifier without renderer-derived identities. H-079/CI pending.


## 2026-10-12 P0A continuation after acb518e5ba — backend-bound admission only

- Starting exact local+remote HEAD `acb518e5ba227ae1fbabff7f88f0842533851ca6`, clean isolated worktree, PR #81 draft/open/unmerged. Main checkout preserved; do not alter its dirty changes.
- TDD RED #1: `python -m pytest workstation/tests/test_hcw_taskrun_backend_attestation.py -q` collection failed exit 1 with missing `workstation.creative_taskrun_attestation`.
- Added `workstation/creative_taskrun_attestation.py`: derives EXACTLY ONE running, claimed TaskRun from existing Kanban DB and verifies via canonical `CreativeRunContext.validate`. It also requires verified account matching a canonical SessionDB record, a bound gateway session key/id and a trusted clear authority lease assertion. No renderer identifiers or arbitrary task IDs are accepted by this function.
- Security TDD RED #2: approval-only/ambient context incorrectly passed the original check; negative test failed 1, demonstrating forged detached call. Added `gateway.session_context.get_bound_session_env` (ContextVar-only, no process env fallback). The attestor now requires an actual gateway-bound key and session id and refuses ambient HTTP/process identity.
- Security TDD RED #3: proof lifetime exceeded TaskRun `claim_expires`; verified test failure exit 1. Proof lifetime now capped by the shortest canonical task/run lease or 15 seconds.
- Focused backend regression: `python -m pytest workstation/tests/test_hcw_taskrun_backend_attestation.py workstation/tests/test_hcw_hybrid_taskrun_command.py workstation/tests/test_hcw_hybrid_revision_cas.py -q` **25 passed, 0 failed, exit 0**. Native Electron E2E not performed. Ruff unavailable in system Python (No module named ruff); do not report Ruff GREEN.
- **Ruling (safety):** These are backend admission primitives, not a production HTTP RPC. An independently authenticated HTTP request does not inherit a live gateway SessionKey. The renderer/connection/session mapping in Electron is not yet main-owned and attested. Therefore DO NOT wire `main.ts` to these functions or change `resolveTrustedOwner: () => null`. No P0A/H-C2 promotion. P0B remains blocked. P0C, H-C3-H-C9 unchanged; H-079 and exact-head CI pending.
- Next exact action: bind an authenticated backend session principal (e.g. verified OAuth request.state.session) to the stored SessionDB owner and the live gateway TaskRun without fabricating ContextVars, then create a strictly bounded authenticated canonical RPC and a main-owned window/session/connection registry. Follow with native UI+agent CAS E2E. Never expose `sessionKey` via arbitrary public API.

## HCW-P0A next checkpoint — read-only authenticated HTTP identity binding

2026-10-12 continuation after 85b0448fa: Added workstation/creative_http_identity.py and GET /api/workstation/creative/owner-readiness in hermes_cli/web_server.py. Read-only authenticated interactive-principal → canonical SessionDB (user_id/session_key) → unique live Kanban TaskRun lookup with workspace, profile, expiry, lock and supersession fences. OAuth/native-session request.state.session is required; loopback token and service token are not considered interactive actor authentication. TDD RED module absent (exit 1), route not registered (1 failed exit 1), GREEN 38 passed, 0 failed in 47.06s, 1 Starlette/httpx deprecation warning, command python -m pytest workstation/tests/test_hcw_http_principal_owner.py workstation/tests/test_hcw_taskrun_backend_attestation.py workstation/tests/test_hcw_hybrid_taskrun_command.py workstation/tests/test_hcw_hybrid_revision_cas.py -q. No sessionKey or claimLock returned; authorityGranted=false. Not an authenticated mutation RPC or live gateway authority proof. main.ts remains resolveTrustedOwner: () => null; P0A PARTIAL, P0B BLOCKED; H-C2 no promotion, H-079 and exact-head CI unverified.

Next: establish provable HTTP principal ↔ live gateway lease and main-owned Electron sender/window/session/connection scope, then add privileged RPC using existing CreativeRunContext CAS. Never treat readiness response as a grant.
