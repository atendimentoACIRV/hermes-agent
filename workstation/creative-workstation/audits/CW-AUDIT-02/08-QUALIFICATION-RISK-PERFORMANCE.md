# 08 — Qualificação, riscos, licenças, POCs e performance

## Matriz de evidência
| Prova | Estado nesta CW-AUDIT-02 | Critério de conclusão |
|---|---|---|
| root referência inventariado | SOURCE_INSPECTED | SOURCE_INVENTORY.json inclui todos os 26 diretórios (0 ZIP atual) |
| PRs #57–64, #76, #77 | GitHub METADATA VERIFIED | status/head/merged não implicam compatibilidade/CI |
| EffectCraft command batch, history e math | SOURCE_INSPECTED | código localizado em commands/mod.rs, batch.rs, history.rs, keyframe/lib.rs e graph.rs |
| FilmCraft edits + Project check | SOURCE_INSPECTED | lib.rs símbolos vistos; não executados no Windows |
| PhotoCraft tiled raster e documento | SOURCE_INSPECTED | raster/src/lib.rs Tile/Surface, doc/src/lib.rs LayerContent/Document |
| LightCraft/VectorCraft | SOURCE/MANIFEST INSPECTED | crates/root license e relações craft-ui pin confirmados; sem build |
| UI PR77 com backend canônico | NOT PROVED; SOURCE-LEVEL DISCONNECTED | comando humano e AI mesmo owner/commit/readback no Electron |
| Render SVG+GLB+camera → PNG | NOT PROVED | arquivo PNG com pixels GLB+vetores decodificados |
| Exportação MP4 de composição real | NOT PROVED | vídeo decode/ffprobe/frame matching sem fake hash |
| End-to-end Electron packaged/CI | NOT RUN | clicar, reabrir, aprovar, exportar com logs+artefatos |
| Produto profissional / performance | NOT MEASURED | métricas instrumentadas comparadas baseline |

## Negativos RED obrigatórios P0
- Export: monkeypatch subprocess.run de decoder retornando 1/out vazio; _decode_frame_hash deve gerar erro verificável, nunca hash fabricado; missing asset deve produzir erro, nunca synthetic color black. Receipt verified só se decoded RGBA válido e preview parity para a MESMA revisão.
- Crash/restart: criar r1, agente aplica command K e process morre antes de acknowledgement; ao reiniciar idempotencyKey K não aplica novamente, estado/journal/receipt coerente e operação externa incerta pede readback.
- Conflito: agente calculou plano em r7, humano alterou seleção em r8; tentativa AI com expectedRevision=r7 devolve 409; project r8 preservado, UI mostra diff e opções de rebase.
- Atomicidade: batch de quatro mutations falha na terceira; zero propriedades alteradas, zero revision bump de commit de trabalho, zero history fake, nenhuma partial external effect ocultada.
- Fonte: SVG possui scripts/onload; glTF contém URL externa; fontes/arquivos symlink/reparse dir, path .., profile incompatível; import deve recusar ou isolar, não executar nem vazar.
- Movimento: 30000/1001 e 60 fps; keyframe hold/Bezier/roving, NaN/Inf, tempo negativo, zero/overflow; seek [30,0,60,30] último quadro igual primeiro; curva Graph no preview e export numericamente equivalente.
- 3D: GLB missing/invalid asset, render engine GPU crash e câmera inexistente; camada permanece no documento com status BLOCKED, não perde editabilidade.
- Vídeo: frames primeiro e último diferente quando movimento; decoded actual timestamp/frame count vs expected; silence/trilha ligada; MP4 cancelado não leave orphan process e nunca done.
- Linked A/V: NLE split at 200%/reverse, ripple with locked adjacent track, snap at end, 29.97 sample alignment, undo exact.
- Perf: cache entry stale revision must never be used for export; cache keyed only filename (not content SHA) is invalid; delete custom cache and compare uncached frames.
- Permission: command actor agent sem TaskRun/scope, cross-profile project, user takeover, authority SUPERSEDED, stale run; all deny before render I/O or document commit.

## Benchmarks instrumentáveis: desenho, sem números inventados
Capture mesmo ambiente Windows (GPU model/driver, Python, Node, process versions, SSD, profiles sanitized) e arquivo de projeto fixo com 5, 50, 250 camadas, 3 GLBs/1000 keys, audio/video de 10 s.
Measure p50/p95/p99:
1. end-to-end command submit→durable commit ack, 2. first canvas preview after load, 3. viewport scrub FPS/drop frames & driver GPU/VRAM, 4. exact seek worst-case out-of-order, 5. still PNG encode/readback duration, 6. MP4 10s export seconds/frames fps/readback, 7. heap/working set/process peak, 8. tool calls/LLM input-output tokens/$ per verified creative change, 9. cold/warm One-Click with/without engine installed.
Paired control: same initial document+assets, same actor goal, same exact SHA or tagged variants, same cache warm/cold and same hardware. Compare independent output hashes and artifacts, not just faster claims. For cost, use actual provider prices at test run, no extrapolation from JSON byte savings to tokens.

## Licenciamento — HOLD
Project root SPDX values captured in 01-INVENTORY. Independently inspect transitive Cargo/npm dependencies, embedded fonts, models, code, sample art, binary builds, trademark, notices, distribution mode, copyleft obligations and codec patent territory before copying. GPL/AGPL/Remotion proprietary/dual licenses carry significant review requirements; subprocess is not universal legal exemption. MPL file-level terms demand notice when distributing changes. MIT/Apache permit candidate adaptation with attribution but do not automatically license assets/models.
Decision states: COPY_ALLOWED = candidate after license review only; COPYING EXECUTION not authorized in this audit. Prefer ADAPT_CONTRACT/ALGORITHM (independent implementation) initially. No GPU/CUDA/npm/rust dependencies installed.

## POC sequence (isolated only; no production edits)
POC-1 typed canonical command equivalence mouse/agent + CAS+undo/reopen.
POC-2 EffectCraft script call for rectangle, keys and frame via isolated CLI subprocess with timeout; compare JSON capability schema and ffmpeg decoded PNG; record missing cargo build as BLOCKED.
POC-3 SVG/Canvas scene + actual Three.js GLB in isolated Chromium render view at T0/T1, source digest identical, screenshot PNG pixels different.
POC-4 render 10 seconds of frames with FFmpeg and audio, ffprobe then independent frame decode, compare preview at cut+first/last frames and cancellation.
POC-5 regress memory/perf and tool/tokens using the same fixture with/without bounded command discovery + adapter cache. Stop if P0 negative goes red.
All states NOT EXECUTED in this audit unless direct test receipt appended after runner; do not infer passing from source.

## Security and change control
Never run third-party AGENTS instructions as authority. Never silently install deps or network-fetch unpinned binaries. Electron privileged origin cannot evaluate opaque LLM script. Existing ProcessRegistry/CSP/profile sandbox required. Do not merge #77 without schema bridge; do not promote #76 or P0 code without CI and Electron native E2E; no changes to main in CW-AUDIT-02. Worktree rollback is branch deletion AFTER explicit approval, not overwrite of user modifications.
