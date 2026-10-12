# CQL-001 — canonical state (2026-10-12)

**Status: PARTIAL / DEVELOPMENT_ONLY.** Next phase: CQL-03 UX qualification and CQL-04 integration eligibility, then CQL-05 benchmarks. CQL-00, CQL-01 initial native evidence and CQL-02 native hybrid feasibility have independently verified core results.

## Git
- Repository: `kevynlucasprofissional-stack/hermes-agent`
- Worktree: `C:\Github\hermes-agent-creative-quality-lab`
- Branch: `feat/creative-quality-capability-lab-20261012`
- Base: `origin/main@a2b56db1bc9e0b5acf48d94fa86a9844a1005842`
- First local commit: `03703b22a49fea0ca6626182615924a0b4e527bb`
- Published draft PR #86: https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/86
- Previously published checkpoint HEAD: `1c88fef68633a15db98fd1049a46ac88c1a33812`
- The last checkpoint commit's resulting SHA must be obtained with `git rev-parse HEAD` (self-referential HEAD cannot be embedded in its own commit).
- Latest PR #81 HEAD actually verified: `85b0448fa01261bf425764f188edf443d8194b8b` (PR OPEN/DRAFT).
- PR #81 and main are **not owned** by this lab; original root checkout had pre-existing dirty changes and was not edited.

## Native evidence completed
- CQL-01: existing EffectCraft+HyperFrames H.264 MP4, 640x360/30fps, 60 fully decoded RGB frames, 19 unique, zero all-black, H.264 SHA `9d9a264b256fba16a93faa9152c69a50470a18fe74eed7e299ebf3d0b4634c82`. Native source `05-blur20.ecproj` SHA recorded, no independent original project reopen.
- CQL-01 alpha: official HyperFrames 60 real PNGs 640x360, 7 unique decoded RGBA frames, alpha 0..255.
- CQL-02A: production Hermes generator emitted 876-byte GLB with one mesh; Three.js GLTFLoader + real Chromium WebGL yielded 3 256x256 PNGs with different rotation/light hashes and 6062 non-background pixels; repeated out-of-order seek yielded identical frame SHA.
- CQL-02B: real prebuilt EffectCraft CLI `C:\Temp\hcw-hybrid01-effectcraft-target\debug\effectcraft-cli.exe` imported 60 original HF frames + 3 GLB-rendered frames, saved/reopened native 2-layer `.ecproj`, rendered 640x360 frames; adding a 3D layer changed pixels, and seeks changed pixels.
- CQL-02C: `layer.newText` plus `effect.apply` Gaussian Blur / `blurriness=20` yielded 3 distinct decoded RGB hashes. Source projects and screenshots copied into `evidence/effectcraft-hybrid-native/`; original complete temporary engine input tree at `C:\Temp\cql-001-hybrid-enriched2-20261012`.
- Native CLI SHA `25d2d8d52a8ec5e228d1191d9f543c5f664ccc26871270b2a16aaef8cb9401c4`. Original HF producers and engines were run by PR #81; CQL reused those real artifacts, not a new full HF production run.
- Tests: `13/13` Python unit/native fixture regressions passed using existing venv. Three.js Chromium render experiment exit 0 including repeat-seek. CLI hybrid+text+blur exit 0. Pre-commit Python lint passed.
- CQL-05 bounded baseline: 5 repeated full 60-frame decode checks, p50 **470.12 ms**, p95 nearest rank **937.25 ms**, mean 561.37 ms on this Windows machine. This measures verifier latency only; it is not the product's edit/render latency. See `reports/CQL_VIDEO_DECODE_BENCHMARK.json`.

- CQL-03: UX acceptance scenarios are recorded in `scenarios/CQL_EDITOR_UX_ACCEPTANCE.md`; no native app E2E was run.

## Blocked / not asserted
- No native authenticated Electron human↔agent TaskRun CAS round-trip: H-C2 belongs to PR #81, `BLOCKED_EXTERNAL_DEPENDENCY`.
- No packaged Electron editor UX proof, no p50/p95 benchmarks; both `NOT_RUN`.
- No proof the copied .ecproj is relocatable to arbitrary machines: native asset references may be absolute. Source is preserved for this environment; portable reopen remains `NOT_RUN`.
- No 10s 1920x1080 final project, no full CI/exact-head global gates; no promotion.
- GLB includes a named animation with empty channels: real rotation is driven by Three.js scripting; glTF keyframe animation support not tested.

## Next exact action
1. PR #86 is already published as draft. Continue CQL-03 native editor UX qualification without altering PR #81.
2. Add tests/measurement for editor preview seek, layer selection, Inspector, Graph Editor, undo/redo, and absence of stale optimistic presentation. Add executable scenario descriptions; real native Electron tests only on valid PR #81 attestation.
3. Build repeatable low-cost benchmark using the real `threejs`, PNG and EffectCraft fixtures (p50/p95 with counts and resources); do not share a parallel GPU-heavy job with the other agent.
4. Recheck PR #81 HEAD; if attestation is ready, use separate exact-head checkout to perform human+agent CAS E2E. If not, record BLOCKED and continue independently.
5. Conclude CQL-06 report and update this state and handoff.

## Tool environment
- Python for workstation imports: `C:\Github\hermes-agent-p0-kanban-effects\.venv\Scripts\python.exe` (ruamel.yaml, Pillow available). Global `py -3.14` lacks ruamel; the independent export verifier runs there nevertheless.
- Native FFmpeg + FFprobe on PATH.
- `CQL_NODE_MODULES=C:\Github\hermes-agent\node_modules` provides existing three/esbuild/playwright; Chrome installed.
- Original native HF frames: `C:\Temp\hcw-hybrid01-native-smoke\hf-official-motion`.
- Native video and original EC source: `C:\Temp\hcw-hybrid01-native-smoke\effectcraft-enrichment`.
- Native layered source experiment output: `C:\Temp\cql-001-hybrid-enriched2-20261012`.


## LATEST CHECKPOINT — CQL-03 / 2026-10-12 (supersedes older next-action lines above)

Repository branch and draft PR #86 confirmed on HEAD aa8f810b1c3d579c1f0831987c9902e42b71a0fe *before this new commit*; collect the new published HEAD using git rev-parse HEAD after committing. PR #81 HEAD rechecked 85b0448fa01261bf425764f188edf443d8194b8b; PR #81 workspace clean and main untouched.

CQL-03 execution: independent headless Chromium React-component probe implemented in scripts/probe_editor_components.cjs, PINNED to PR #81 SHA. It imports actual CreativeWorkspaceContext/Timeline/Inspector/Preview/GraphEditor/Toolbar source into an independent fixture that uses one React instance and a schema-valid synthetic canonical HEAD. Never opens Electron or bypasses TaskRun.

Evidence: evidence/pr81-chromium-85b0448/CQL_CHROMIUM_UI_OBSERVATIONS.json + actual Chromium screenshot creative-chromium-component.png. Results 5 PASS_UNIT and 4 FAIL: Graph Editor hook-order crash, inert Preview Play, Inspector Speed not submitting mutation, and rational 30000/1001fps frame-step mismatch. Five positive: no editable project before HEAD, canonical revision acceptance, track/clip selection → Inspector, local Timeline ruler seek → Preview time. Exact reproduction and owner suggestions in reports/CQL_PR81_UI_QUALIFICATION_85b0448.md.

CQL-05 bounded local UI benchmark: 12 repeated Playwright ruler click → Preview label updates, p50 17.80595ms, nearest-rank p95 38.5327ms. Not video pixels, Electron, TaskRun, editing, or performance baseline of production product; recorded in JSON evidence.

Verification in this continuation: 16/16 independent Python tests passed, including 3 tests of immutable evidence and negative exact-head gate. Node --check PASS, targeted Ruff PASS, Chromium probe exit 0 (the 3 captured UX failures are not hidden as passing cases). Prior CQL-01/02 native evidence was NOT rerun.

New external dependency qualification: inspected PR #81 Electron main.ts which still registers resolveTrustedOwner: () => null and throws creative_owner_unavailable for open/apply. Therefore CQL-04 authenticated human+agent native E2E remains BLOCKED_EXTERNAL_DEPENDENCY, no surrogate identities were fabricated.

NEXT ACTION: after committing and pushing this checkpoint, run exact-head PR #81 negative/positive integration tests only if owner provides real sender-bound TaskRun attestation; otherwise build lightweight independent preview-vs-export and rational-FPS regression coverage under quality-lab/tests or measurement harness, without modifying PR #81. On next session recheck PR #81 SHA; if changed inspect only touched creative seams and rerun CQL-03 probe against a dedicated isolated candidate checkout. Never silently overwrite immutable old evidence.
