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
