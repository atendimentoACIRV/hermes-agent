# CQL-001 — handoff and copy-ready continuation

## Exact ownership and identity
Repo `kevynlucasprofissional-stack/hermes-agent`.
Worktree `C:\Github\hermes-agent-creative-quality-lab`; branch `feat/creative-quality-capability-lab-20261012`; clean baseline `origin/main@a2b56db1bc9e0b5acf48d94fa86a9844a1005842`.
First own commit `03703b22a49fea0ca6626182615924a0b4e527bb`. Always run `git rev-parse HEAD`, `git status --short`, `git ls-remote origin refs/heads/feat/creative-quality-capability-lab-20261012` to recover post-handoff HEADs.
Other owner: [PR #81](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/81), last verified `acb518e5ba227ae1fbabff7f88f0842533851ca6`; verify live HEAD anew before its tests. Root checkout had unrelated dirty changes and must be left intact.

## Completed with real outputs
- CQL-00 isolated worktree, quality-lab structure, contract tests.
- CQL-01: FFprobe + real FFmpeg decoded 60/60 H.264 frames, 19 distinct; 60 real HyperFrames RGBA frames, 7 distinct, alpha 0..255. Negative cases fail closed.
- CQL-02A: real Three.js GLB triangle loaded/rendered by Chromium WebGL, 3 different screenshot hashes and replay seek; 6062 non-background pixels.
- CQL-02B: official HF frames and GLB-rendered PNGs imported into *real* EffectCraft CLI in native editable 2-layer project; native CLI reopen, two distinct seeks and layer visual differences proved.
- CQL-02C: native title + Gaussian Blur 20, three distinct decoded visual variants and project source SHA proved.
- Python suite `13 passed / 0 failed`; native scripts exit 0; pre-commit lint GREEN. CQL-05 bounded independent 60-frame decode benchmark: 5 samples, p50 470.12 ms, p95 937.25 ms; **not product latency**. No claims of global CI/Windows Electron E2E.
- Tests and fixtures under `workstation/creative-workstation/quality-lab`; evidence under `reports/` and `evidence/`.

## Key executable commands
Run in our worktree:
```powershell
& 'C:\Github\hermes-agent-p0-kanban-effects\.venv\Scripts\python.exe' -m unittest discover -s 'workstation/creative-workstation/quality-lab/tests' -p 'test_*.py' -v
$env:CQL_NODE_MODULES='C:\Github\hermes-agent\node_modules'
node 'workstation/creative-workstation/quality-lab/scripts/prove_threejs_glb.cjs' 'workstation/creative-workstation/quality-lab/fixtures/reference-3d/cql-triangle.glb' 'workstation/creative-workstation/quality-lab/evidence/threejs-native'
& 'C:\Github\hermes-agent-p0-kanban-effects\.venv\Scripts\python.exe' 'workstation/creative-workstation/quality-lab/scripts/prove_effectcraft_hybrid.py' --cli 'C:\Temp\hcw-hybrid01-effectcraft-target\debug\effectcraft-cli.exe' --hyperframes 'C:\Temp\hcw-hybrid01-native-smoke\hf-official-motion' --threejs 'workstation/creative-workstation/quality-lab/evidence/threejs-native' --out 'C:\Temp\cql-001-hybrid-replay-NEW'
```
Use a **new empty output directory** for every native CLI rerun; never overwrite immutable evidence.

## Next action exact
1. Confirm repository branch and PR published; if not, publish dedicated branch and open draft PR; do not merge.
2. Reuse the now-created `quality-lab/scenarios/CQL_EDITOR_UX_ACCEPTANCE.md`: turn feasible cases into automated read-only UI assertions or real Electron E2E tests. Preserve H-C2 cases as BLOCKED until authentic owner is available, and do not treat mock UI as native.
3. Add an independent measured startup/preview-seek benchmark when possible and a typed regression reporter for PR #81; do not create another editable project store.
4. Add `quality-lab/benchmarks/` measured repeated native fixture scenario p50/p95 and resource stats; do not estimate improvements without baseline.
5. Recheck latest PR #81, and only when authentic backend TaskRun owner is bound, run exact-head Electron↔Python real human+agent CAS E2E; do not patch authority yourself.
6. Consolidate CQL-06, all statuses, real screenshots and reports, and checkpoint/continuation.

## Hard constraints
Never edit root dirty checkout or main. Never write to PR #81 or counterfeit auth. Never create another CreativeDocument/TaskRun/compositor/editor. Never equate mock results with native proofs. Track missing/blocked explicitly and keep preserving output SHA, native files and source provenance. No destructive operations.

## Full continuation request template

EXECUTAR CQL-001 — RETOMADA (NÃO REINICIAR AUDITORIA).
Você é implementador do Creative Quality & Capability Lab no repo `kevynlucasprofissional-stack/hermes-agent`. Worktree `C:\Github\hermes-agent-creative-quality-lab`, branch `feat/creative-quality-capability-lab-20261012`, base `origin/main@a2b56db1bc9e0b5acf48d94fa86a9844a1005842`. Primeiro commit `03703b22a49fea0ca6626182615924a0b4e527bb`; obtenha HEAD local e remoto reais via Git. PR #81 é outra branch, último SHA verificado `acb518e5ba227ae1fbabff7f88f0842533851ca6`, verifique seu SHA atual e permaneça read-only.
Leia `workstation/creative-workstation/quality-lab/CQL_STATE.md`, `CQL_ACCEPTANCE_MATRIX.md`, `CQL_FINDINGS.md`, `CQL_HANDOFF.md` e somente os contratos relevantes. Laboratório de decodificação/alpha, GLB WebGL e composição nativa EffectCraft de HF + 3D + texto + GaussianBlur foram implementados e testados com evidências reais, 13 testes Python passaram. Não reexecute builds desnecessariamente nem volte aos motores.
Próximo passo: utilizar `quality-lab/scenarios/CQL_EDITOR_UX_ACCEPTANCE.md` já criado, transformar casos elegíveis em testes reais da UI, medir desempenho do produto (já existe baseline p50/p95 apenas do decodificador), depois qualificar independentemente PR #81 quando H-C2 autenticado estiver disponível. Não implemente H-C2; não escreva em PR #81/main ou em arquivos de produção do outro agente. Continue pelas fases CQL-03, CQL-04, CQL-05 e CQL-06; salve, valide, faça commits incrementais, publique nossa branch draft PR, atualize checkpoints. Se sessão interromper, produza prompt integral, autossuficiente, com HEADs, mudanças, testes, bloqueios, próxima alteração/arquivo/comando/critérios e fases restantes.
