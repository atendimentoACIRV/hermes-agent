# EVIDENCE — Subagente Engine Auditor Report (CW-AUDIT-01)

**Fonte:** Subagente `fbd8362a-f38d-4905-b22e-7376b61176a1` (EffectCraft Engine Deep-Dive Auditor)  
**Status:** COMPLETE — relatório recebido via mensagem  
**Data:** 2026-10-11T03:34:00Z  

Este arquivo preserva o relatório completo do subagente para rastreabilidade.  
O relatório foi incorporado nos documentos principais da auditoria.

---

## Seções principais do relatório

### Command Registry (FACT)
- `CommandSpec{id,label,menu,shortcut,params,enabled:Enabled,run:Run,journal:bool}` (mod.rs:93-107)
- Macros `cmd!` e `query!` (mod.rs:110,116) — queries sem journaling, enabled sempre
- `command_specs()` via `OnceLock` — inicialização estática, ~2.000 IDs
- `find(id)` via `OnceLock<HashMap>` — resolução O(1)
- Mesmo `Session::execute` serve UI + CLI + Control TCP + MCP (lib.rs:571-594)

### Batch (FACT)
- `engine.batch{steps, label?, atomic?=true}`
- `reference/substitute` para `$N.key.path` intra-lote (batch.rs:L15-52)
- Rollback: snapshot `(project, history, state)` antes do batch, restaura em falha
- `fold()` colapsa todos os passos em 1 undo step (batch.rs:L96-104)
- `NOT_IN_BATCH = ["engine.batch", "file.runScript", "script.run"]` — sem nesting

### History (FACT)
- `History{undo:Vec<(label,Arc<Project>)>, redo, merge_key, branches:Vec<Branch>}`
- `abandon_redo(&before)` drena redo e arquiva como `Branch` — NÃO descarta
- `Arena` mantém toda a árvore consultável via `edit.history.list` (`history_tree()`)
- `goto_history(id)` pula para qualquer estado em qualquer branch

### Time Model (FACT)
- `TICKS_PER_SECOND = 254_016_000_000` = LCM de todas as taxas broadcast + áudio
- Fatoração: 2^10 × 3^4 × 5^6 × 7^1 — cobre 24/25/30/48/50/60/120fps + NTSC fracionário + áudio 44.1k/48k/192k
- `Tick(i64)` + aritmética saturada + intermediários em i128
- `from_seconds_f64` limitado a `[i64::MIN/4, i64::MAX/4]` para segurança

### Keyframes (FACT)
- `solve_u`: Newton-Raphson (8 iter) + bisseção (60 iter) + caso cbrt degenerado
- `SpatialSeg`: arc-length 96 amostras, lookup + interpolação linear
- `retime_roving`: velocidade constante em trajetórias
- Teste contra AE 26.3x87 real via AEsync 2.0.4: 8 casos, 168 amostras, erro máximo < 3e-11

### Tabela de comparação final (do subagente)

| Área | EffectCraft | Hermes | Superioridade |
|---|---|---|---|
| Command Registry | 5.0/5 | 3.5/5 | EffectCraft (~2000 vs 19 comandos) |
| Batch + Atomicidade | 4.8/5 | 3.0/5 | EffectCraft ($N refs) |
| Undo/Branching | 5.0/5 | 3.0/5 | EffectCraft (árvore vs pilha linear) |
| Modelo de Tempo | 5.0/5 | 4.0/5 | EffectCraft (i64 zero-alloc vs Fraction) |
| Keyframes/Curves | 5.0/5 | 2.0/5 | EffectCraft (solvers completos) |
| NLE Track Primitives | 3.5/5 | 4.5/5 | **Hermes** (split/ripple/slip/slide/roll) |
| MCP + Agent Control | 5.0/5 | 3.5/5 | EffectCraft (unified dispatch) |
| Governança/Concorrência | — | 5.0/5 | **Hermes** (ETag/409/TaskRun/verifier) |
