# CQL Acceptance Matrix

| ID | Capability | Input / expected | Verification | Result | State |
|---|---|---|---|---|---|
| CQL-00-A | Isolation | own worktree from a2b56db1bc, not #81 | `git worktree list`, status | Dedicated `feat/creative-quality-capability-lab-20261012` | PASS_UNIT |
| CQL-01-A | Decoder safety | sample native MP4, 640x360, 30fps, 60 frames | real ffprobe and full FFmpeg RGB decode | H.264, 60 decoded, 19 distinct, 0 all-black, SHA256 in HCW81_NATIVE_BASELINE.json | PASS_NATIVE |
| CQL-01-B | Invalid-source handling | missing source / corrupt MP4 / invalid frame count | 6 native/unittest cases | 6 passed on Windows Python 3.14 | PASS_UNIT |
| CQL-01-C | Reopen native editable source | `05-blur20.ecproj` must successfully reopen in EffectCraft | native CLI reopen + native frame extraction | Artifact SHA verified only; reopen is not yet repeated by this lab | NOT_RUN |
| CQL-01-D | RGBA HyperFrames source | pinned source 60 RGBA PNG frames, alpha and motion | Pillow native RGBA pixels and source image hashes | 60 frames 640x360, 7 unique, alpha 0..255; `reports/HCW81_RGBA_SOURCE_BASELINE.json`; native decoder tests 11/11 | PASS_NATIVE |
| CQL-02-A | GLB raster pixels | Hermes triangle GLB, 3 orientations/light settings, repeat seek | Three.js GLTFLoader + Chromium WebGL readPixels + PNG hashes | 1 mesh, 6062 changed pixels, 3 distinct PNGs (repeat seek replay test), manifest `evidence/threejs-native/threejs-glb-receipt.json` | PASS_NATIVE |
| CQL-02-B | Hybrid 2D+3D+HyperFrames+EffectCraft | coherent composition with shared time | independent decoded frames / preserved native inputs | Not yet executed | NOT_RUN |
| CQL-03-A | Human editing UX | timeline, Inspector, preview, undo/redo | real UI dogfood and measured interactions | Not yet executed | NOT_RUN |
| CQL-04-A | Canonical human+agent TaskRun cycle | auth from backend, same project revision, CAS conflict | native Electron independent UI+backend E2E | Owned by PR #81; cannot bypass DENY-ALL | BLOCKED_EXTERNAL_DEPENDENCY |
| CQL-05-A | Latency and memory baseline | equivalent exact fixture repeated | p50/p95, memory/process observation | Not yet executed | NOT_RUN |

Status names: `PASS_NATIVE`, `PASS_UNIT`, `PASS_INTEGRATION`, `FAIL`, `BLOCKED_EXTERNAL_DEPENDENCY`, `NOT_RUN`, `NOT_APPLICABLE`. Scope of each proof is binding.