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
