# CQL Acceptance Matrix

| ID | Capability | Input / expected | Verification | Result | State |
|---|---|---|---|---|---|
| CQL-00-A | Isolation | own worktree from a2b56db1bc, not #81 | `git worktree list`, status | Dedicated `feat/creative-quality-capability-lab-20261012` | PASS_UNIT |
| CQL-01-A | Decoder safety | sample native MP4, 640x360, 30fps, 60 frames | real ffprobe and full FFmpeg RGB decode | H.264, 60 decoded, 19 distinct, 0 all-black, SHA256 in HCW81_NATIVE_BASELINE.json | PASS_NATIVE |
| CQL-01-B | Invalid-source handling | missing source / corrupt MP4 / invalid frame count | 6 native/unittest cases | 6 passed on Windows Python 3.14 | PASS_UNIT |
| CQL-01-C | Reopen native editable source | `05-blur20.ecproj` must successfully reopen in EffectCraft | native CLI reopen + native frame extraction | Artifact SHA verified only; reopen is not yet repeated by this lab | NOT_RUN |
| CQL-01-D | RGBA HyperFrames source | pinned source 60 RGBA PNG frames, alpha and motion | Pillow native RGBA pixels and source image hashes | 60 frames 640x360, 7 unique, alpha 0..255; `reports/HCW81_RGBA_SOURCE_BASELINE.json`; native decoder tests 11/11 | PASS_NATIVE |
| CQL-02-A | GLB raster pixels | Hermes triangle GLB, 3 orientations/light settings, repeat seek | Three.js GLTFLoader + Chromium WebGL readPixels + PNG hashes | 1 mesh, 6062 changed pixels, 3 distinct PNGs (repeat seek replay test), manifest `evidence/threejs-native/threejs-glb-receipt.json` | PASS_NATIVE |
| CQL-02-B | Hybrid 2D+3D+HyperFrames+EffectCraft | 60 real HF frames + 3 real Three.js GLB-raster PNGs | Native EffectCraft file.import, saved/reopened .ecproj, 2 layers, decoded PNG and seek comparison | Source preserved, 2 native layers, differences against HF-only and across seeks; `evidence/effectcraft-hybrid-native/` | PASS_NATIVE |
| CQL-02-C | Native title and blur | `layer.newText` + Gaussian Blur blurriness=20 | Native CLI saved/reopened and 3 independent RGB hashes | 3 visual states distinct at frame 0.033333, `05-hybrid-blur20.ecproj` persisted | PASS_NATIVE |
| CQL-03-A | Human editing UX | timeline, Inspector, preview, undo/redo | real UI dogfood and measured interactions | Not yet executed | NOT_RUN |
| CQL-04-A | Canonical human+agent TaskRun cycle | auth from backend, same project revision, CAS conflict | native Electron independent UI+backend E2E | Owned by PR #81; cannot bypass DENY-ALL | BLOCKED_EXTERNAL_DEPENDENCY |
| CQL-05-A | Product latency and memory baseline | equivalent exact fixture repeated | product edit/p50/p95/memory | Not yet executed; benchmark below is verifier-only | NOT_RUN |
| CQL-05-B | Independent decode verifier latency | H.264 60 frames, five repeats | wall-clock p50/p95; source SHA stable | p50 470.12ms, p95 937.25ms (nearest rank), 5 measured samples; `reports/CQL_VIDEO_DECODE_BENCHMARK.json` | PASS_NATIVE |

Status names: `PASS_NATIVE`, `PASS_UNIT`, `PASS_INTEGRATION`, `FAIL`, `BLOCKED_EXTERNAL_DEPENDENCY`, `NOT_RUN`, `NOT_APPLICABLE`. Scope of each proof is binding.

## 2026-10-12 scoped CQL-03 results — not native Electron qualification

| ID | Target | Evidence & observed result | Classification |
|---|---|---|---|
| CQL-03-EMPTY | Project hidden before HEAD | Real Chromium React empty view | PASS_UNIT |
| CQL-03-HEAD | Only accepted canonical revision | React projected supplied schema-valid fixture HEAD | PASS_UNIT |
| CQL-03-TRACK | Track click selects Inspector | Inspector rendered Video A | PASS_UNIT |
| CQL-03-CLIP | Clip click selects Inspector | Inspector rendered Visual Clip | PASS_UNIT |
| CQL-03-SEEK | Timeline ruler click syncs Preview local time | 1.530s display and unchanged acknowledged revision | PASS_UNIT |
| CQL-03-PREVIEW-PLAY | Preview button should start playback | isPlaying remained false after actual click | FAIL |
| CQL-03-INSPECTOR-SPEED | Speed edit should submit authorized mutation | field handler logs; no new canonical projection | FAIL (component wiring only) |
| CQL-03-GRAPH | Select keyed layer after graph empty | React crashed with Rendered more hooks than during previous render | FAIL |
| CQL-03-RATIONAL-FPS | Click one Step Forward with canonical fps 30000/1001 | Actual delta 0.03333333333333344s vs required 1001/30000s | FAIL |
| CQL-03-ELECTRON | Native app human+agent CAS and readback | main.ts DENY-ALL without owner | BLOCKED_EXTERNAL_DEPENDENCY |
| CQL-05-LOCAL-UX | Local ruler-click to Preview text only, 12 tries | p50 17.80595ms, p95 38.5327ms in browser receipt, not decoded video or Electron | PASS_UNIT (scoped benchmark) |

Source SHA and precise results in evidence/pr81-chromium-85b0448/CQL_CHROMIUM_UI_OBSERVATIONS.json. Reports are intentionally immutable per target SHA. Overall UX experience and native application gates remain UNQUALIFIED.
