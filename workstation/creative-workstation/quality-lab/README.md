# Creative Quality & Capability Lab — CQL-001

Independent qualification lane for Hermes Creative Workstation. Does not own CreativeDocument, TaskRun, canonical IPC, HyperFrames, EffectCraft, or the production renderer.

## Verified entry points

Run from repository root on Windows; use an existing Python environment with required dependencies. The export verifier itself needs only Python stdlib plus FFmpeg/FFprobe on PATH.

```powershell
py -3.14 -m unittest discover -s workstation/creative-workstation/quality-lab/tests -p 'test_*.py' -v
py -3.14 workstation/creative-workstation/quality-lab/scripts/verify_native_export.py 'C:\Temp\hcw-hybrid01-native-smoke\effectcraft-enrichment\hermes-hybrid-native.mp4' --source 'C:\Temp\hcw-hybrid01-native-smoke\effectcraft-enrichment\05-blur20.ecproj' --expected-frames 60 --expected-width 640 --expected-height 360
```

The latter example needs the actual native artifacts produced by PR #81 at that path. The report records source bytes and video integrity, **not** EffectCraft reopen or Electron UI qualification.

## HyperFrames RGBA source proof

```powershell
& 'C:\Github\hermes-agent-p0-kanban-effects\.venv\Scripts\python.exe' workstation/creative-workstation/quality-lab/scripts/verify_png_sequence.py 'C:\Temp\hcw-hybrid01-native-smoke\hf-official-motion' --expected-frames 60
```

This independently decodes source PNG pixels, compares frame hashes and checks compositable alpha. Pillow is required; 11 decoder/PNG regression tests passed.

## Three.js GLB raster experiment

The reproducible GLB input is generated using the existing `workstation.creative_3d.create_minimal_valid_glb` helper; it contains a real triangle mesh. `prove_threejs_glb.cjs` uses *installed* Three.js GLTFLoader and Playwright Chromium, requests real WebGL pixels, writes three PNGs at different rotations/light settings, and fails on missing meshes, blank pixels or identical frames.

```powershell
$env:CQL_NODE_MODULES='C:\Github\hermes-agent\node_modules'
node workstation/creative-workstation/quality-lab/scripts/prove_threejs_glb.cjs workstation/creative-workstation/quality-lab/fixtures/reference-3d/cql-triangle.glb workstation/creative-workstation/quality-lab/evidence/threejs-native
```

This is a bounded **3D-engine proof**, not a claim that the production Hermes compositor already supports 3D or preserves a full animated 3D timeline.

## Native hybrid 2-layer EffectCraft composition + text and blur

Run from repository root, using a **new empty** output directory, real prebuilt CLI and the 60 official HF native frames:

```powershell
& 'C:\Github\hermes-agent-p0-kanban-effects\.venv\Scripts\python.exe' workstation/creative-workstation/quality-lab/scripts/prove_effectcraft_hybrid.py --cli 'C:\Temp\hcw-hybrid01-effectcraft-target\debug\effectcraft-cli.exe' --hyperframes 'C:\Temp\hcw-hybrid01-native-smoke\hf-official-motion' --threejs workstation/creative-workstation/quality-lab/evidence/threejs-native --out 'C:\Temp\cql-001-reproduction-NEW'
```

Real EffectCraft `file.import` preserves editable project files; `info` reopens them, seek and extra layer change pixels, and `layer.newText` + `effect.apply` Gaussian Blur 20 produce three distinct RGB hashes. See `evidence/effectcraft-hybrid-native/`. Not an authenticated Electron TaskRun UI test and no claim of arbitrary-device project portability.

## Evidence contract

- `PASS_NATIVE` requires execution of native renderer/decoder and independently inspected artifacts.
- `PASS_UNIT` covers test-only or programmatic contracts.
- `BLOCKED_EXTERNAL_DEPENDENCY` never counts as pass.
- Native source existence and SHA do not prove native source reopen.
- Synthetic FFmpeg color/testsrc is a **test fixture**, not evidence of HyperFrames rendering.
- Evidence PNG/JSON may be kept in the branch when small and non-sensitive; large local files must have reproducible commands and hashes.
- Every report distinguishes the producer's claims from independent checks.

Read `CQL_STATE.md`, `CQL_ACCEPTANCE_MATRIX.md` and `CQL_HANDOFF.md` before continuing.