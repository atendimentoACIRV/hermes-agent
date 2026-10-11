# 10 — Performance and Benchmarks (CW-AUDIT-01)

**Status:** nenhuma medição executada nesta missão (proibido instalar/compilar sem justificativa; Rust toolchain + 285k linhas Craft + Qt/C++ inviáveis). Tudo abaixo é PROCEDIMENTO REPRODUZÍVEL + ESTIMATIVA TÉCNICA, nunca métrica observada. Nada é p50/p95.

## 10.1 Procedimentos (fixtures pequenas, comandos exatos)

| ID | O que mede | Fixture | Comando Hermes | Comando referência | Métrica |
|---|---|---|---|---|---|
| B-01 | init + open project | doc vazio 1 comp 1080p | `python -m workstation.tests.test_creative_document` + time open | `effectcraft-cli info --json` + `exec comp.new` | wall ms |
| B-02 | execução comando único | `clip.split` 2s@30fps | `execute_command clip.split` via `creative_commands.py` | `effectcraft-cli exec comp.new/layer.newSolid/prop.set --json` | ms/op |
| B-03 | batch 4 steps + falha passo 3 | 4 cmds (1 falha) | `CreativeTransaction.apply` (teste `test_creative_commands`) | `batch {steps:[...],atomic:true}` | ms + estado intacto? |
| B-04 | undo/redo | 32 steps | `history.undo/redo` | `undo {}` / `history {goto}` | ms |
| B-05 | seek timeline | 10-15s AV real | `CompositeScene.seek(frame)` | `render_frame {time, max_side:640}` | ms seek |
| B-06 | render frame | 1080p comp 3 layers | `creative_export.export_composition_to_video` | `render-frame --max-side 640 --out f.png --json` | ms/frame + CPU/RAM |
| B-07 | export 10-15s MP4 | still+AV | `encode_still_video` / `export_composition_to_video` | `renderQueue.add/render {wait:true}` | s/export + bytes + ffprobe |
| B-08 | Graph Editor drag | 100 keys | NV (sem UI) | `keys.move {delta,merge}` | ms/drag |
| B-09 | IPC overhead | 100 cmds | MCP `execute_command` loop | `exec --bridge 9877` vs headless | ms/cmd + bytes serializados |
| B-10 | recovery | kill mid-render | `cancel_active_render` + reopen | `mcp --autosave` kill + `open_project checkpoint` | perda (0 ops?) + s/reopen |

Hardware a registrar: CPU/GPU/RAM/OS/build/SHA/input/N/comando. Separar OBSERVADO / ESTIMATIVA / HIPÓTESE. Status atual: todos `NOT_RUN`.

## 10.2 Estimativas técnicas (HIPÓTESE, não fato)
- Hermes Python CoW por transação: O(doc) por batch (~ms para docs KB, s para MB) — Branching Arc Rust O(1) snapshot vence em docs grandes; 409 evita re-trabalho concorrente que Craft não tem.
- `JSON.parse(stringify(project))` OpenReel: O(n) + perde Blob — pior que ambos.
- LayerCache content-hash: static/transform-only 1× — Hermes preview deve copiar (RC-08) antes de otimizar GPU.
- GPU Auto (Craft): só vence em comps pesadas; comps leves ficam no CPU (upload+readback > ganho). Hermes: não investir em GPU antes de B-06/B-07 medidos.
- WASM 58MB→17/10MB gzip/Brotli + workers sem SAB: init ~s, não ms — só para preview isolado, nunca authority.

## 10.3 Oportunidades de desempenho (ordenadas por custo/benefício)
1. Eliminar serializações redundantes (RenderContext×2, dict/load por comando, DOM paralelo) — ganho imediato sem deps. 2. LayerCache content-keyed + LRU (RC-08). 3. Tick/snap inteiro no scheduler (RC-04) — elimina drift, não só velocidade. 4. FFmpeg `-hwaccel` + faststart já usados; medir antes de GPU própria. 5. WASM/Replicad/GPU Craft só após B-06/B-07 com fixtures reais.
