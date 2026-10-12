# Findings — CQL-001

## F-001 — Baseline video decodes and contains motion (verified)
- Input: `C:\Temp\hcw-hybrid01-native-smoke\effectcraft-enrichment\hermes-hybrid-native.mp4`.
- Paired native source: `05-blur20.ecproj`.
- Independent command: `scripts/verify_native_export.py` with 60 frames, 640x360.
- Observed: H.264; decoded 60 frames; 19 distinct RGB hashes; no all-zero RGB frame; status `PASS_NATIVE`.
- Evidence: `reports/HCW81_NATIVE_BASELINE.json`.
- Scope limit: confirms decodability and source byte SHA, NOT EffectCraft source reopen or H-C2 authority.

## F-002 — Tests of false-success paths (verified)
- Native FFmpeg fixture tests reject corrupt media, missing editable sources, frame-count mismatch, incorrect width, and static video when motion is required.
- Synthetic FFmpeg testsrc is explicitly not the native HyperFrames producer.
- Six tests passed; originally warned about open decoder pipes, corrected in local lab source.
- Action: rerun after corrective pipe cleanup.

## F-003 — Python 3.14 global env missing dependency (confirmed environment-only)
- Global `py -3.14` attempted to import `workstation.creative_3d`; required `ruamel.yaml` not installed.
- Existing `C:\Github\hermes-agent-p0-kanban-effects\.venv\Scripts\python.exe` has ruamel and can generate valid GLB via the production `create_minimal_valid_glb`.
- Do not change shared Python installation or call this a Creative runtime regression.

## F-004 — GLB raster verified; production composition remains unqualified
- Baseline `ThreeJsSceneAdapter` / DOM helpers have prior audit findings that scene metadata is not proof of pixels.
- Real WebGL via `scripts/prove_threejs_glb.cjs` loaded Hermes-generated 876-byte triangle GLB with Three.js GLTFLoader; 1 actual mesh, 6062 non-background pixels, 3 distinct 256x256 PNGs after rotation/light changes; out-of-order replay added to harness.
- GLB animation metadata has one named **empty** animation; motion is from deterministic script rotation, not a GLB keyframe-track proof.
- Evidence: `evidence/threejs-native/`. This proves GLB raster in Chromium, **NOT** production Hermes hybrid multi-layer composition.

## F-005 — Native shared human/agent E2E external dependency
- PR #81 HEAD last verified `acb518e5ba227ae1fbabff7f88f0842533851ca6` on 2026-10-12.
- H-C2 sender/TaskRun attestation is owned by agent A. No reproduction by bypassing denied authority.
- Status `BLOCKED_EXTERNAL_DEPENDENCY` until production-Electron direct proof eligible.
