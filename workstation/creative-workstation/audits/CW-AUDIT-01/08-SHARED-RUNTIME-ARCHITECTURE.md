# 08 — Shared Runtime Architecture HW+HCW (CW-AUDIT-01)

**Invariante:** mesma identidade operacional, mesmas regras de autorização, mesmos mecanismos de proveniência — sem 2º agente/TaskRun/control-plane. Compartilhar semanticamente contratos e autoridade; mesmo processo físico NÃO é requisito.

## 8.1 O que já é comum (FACT)
Owners únicos reutilizados pelo creative: TaskRun (kanban) + claim_lock + workspace⊂profile (`creative_project_runtime.py`), ScopedPolicyEngine (`creative_operations.py:345`, `creative_studio_service.py:275`), ArtifactStore+Journal (todos os fluxos), ProcessRegistry/AppResolver (`creative_apps/process/runtime.py`), BrowserTask/session (render PNG via `dispatch_workstation_browser_authoritative`), Experience Compiler (ainda NÃO ligado a creative — CWN-08). `operational_kernel.py`/`operational_capabilities.py` NÃO executam creative (único acoplamento: `capabilities.py inspect_creative` passivo). Sem 2º SessionDB/Kanban/Memory — conforme AGENTS.

Duplicações a eliminar (não novos owners): timeline×2, commands×2, MP4×2, RenderContext×2, sanitize×3.

## 8.2 BrowserOS — princípios transferíveis (INFERENCE de docs públicas, código Chromium NÃO auditado)
BrowserOS combina navegador + plataforma de agentes no mesmo produto/repo, mas NÃO é literalmente 1 processo: há fronteiras concretas (broker, sessão persistente, ownership, recibos, isolamento origem). Princípios aplicáveis ao Hermes (todos já parcialmente presentes):
1. Um broker autoritativo por recurso (BrowserControlBroker / CreativeRunContext) — nunca dois executores de mutação.
2. Recibo do owner como prova causal (`BrowserOwnerReceipt` H-080B ↔ `CreativeProjectRevision{etag}` + render receipts) — não metadata decorativa.
3. Superfície visual ≠ motor de automação (Chromium é preview; comandos tipados são o caminho curto; clicks fallback).
4. Sessão persistente com ownership/recovery/handoff (BrowserTask ↔ CreativeRunContext + autosave checkpoints).
5. Descoberta bounded de capabilities (nunca prompt gigante).
Hermes NÃO deve forkar Chromium nem trocar Electron sem justificativa medida.

## 8.3 Comparação A–F

| Arquitetura | Latência | Memória/CPU/GPU | Complexidade | Segurança | Testab. | Extens. | Win | Editab. | Recovery | Acopl. upstream | Esforço |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A Externas (CLI/MCP/API por editor) | alta (spawn+IPC) | isolado, pico por render | baixa | máxima (processo) | alta (contrato) | alta | alta | média (via adapter) | crash isolado | mínimo | S |
| B Embutidas (editores no Electron) | média | compartilha renderer, risco leak | alta (bridges) | baixa (origens) | média | média | média | alta | crash leva UI | alto | L |
| C Shared Engine (headless + comandos + estado canônico) | baixa-média | 1 engine por job, cache compartilhado | média | alta (sandbox+policy) | alta | alta | alta | máxima | job isolado | baixo | M |
| D Shared Native (Rust/WASM/N-API/FFI) | mínima | zero-copy potencial, risco ABI | alta (build/toolchain) | média (unsafe/ABI) | baixa-média | baixa | média (toolchain) | média | crash pode levar host | médio-alto | L |
| E Hybrid Creative Kernel (RECOMENDADA) | baixa | adapters isolados, cache partilhado | média-baixa | alta | alta | máxima | alta | máxima | por-domínio | mínimo | M |
| F Alternativa | — | — | — | — | — | — | — | — | — | — | — |

**E = documento+comandos+política+histórico compartilhados (Hermes owners); renderers/engines isolados por necessidade (FFmpeg/Remotion/Three/WASM/Natron-CLI).** É o D-043 vigente; esta auditoria a CONFIRMA com refinamentos (não substitui silenciosamente).

## 8.4 Respostas engenharia §11.3 (resumo)
1. Fronteira real: TaskRun/Policy/ArtifactStore/Journal (HW) vs Document/Commands/Adapters (HCW) — mesma autoridade, domínios distintos. 2. Mesmo runtime: Python Workstation + Electron preview + workers owned; engines externos só via adapters. 3. Adaptadores: render/scene/apps/process/studio são adapters, não owners. 4-5. Serialização redundante: SIM — `document_to_dict/load` por comando + `JSON stringify` snapshots + `RenderContext×2` + HTML DOM paralelo; unificar tipos elimina 2-3 cópias por operação. 6. Mesmos comandos humano↔agente? SIM no path novo (`creative_commands.py` actor human_mouse/hermes_agent), NÃO no legado (`operations.py` DOM). 7. Acesso direto timeline? SIM via `CommandRegistry` + `get_layer`-like introspecção read-only (adicionar). 8. HCW→HW sem outro agente? SIM — `CreativeRunContext` dentro do TaskRun existente. 9. Memória/GPU compartilhada? Só via cache content-keyed + device broker; zero-copy só com prova. 10. Ownership concorrente? `expectedRevision` 409 + `linked_selection` + track locks + `merge_key`; faltam `scope` no comando + denial reasons. 11. Undo humano↔IA? Um `CreativeHistory` + branching (RC-03) + dirty segue undo. 12-13. Autorização: ScopedPolicy `creative_edit` + actor + ETag/if_match; editor externo nunca escreve fora do adapter (File sandbox + allowlist paths). 14. Recovery: job isolado + autosave checkpoints + `cancel_active_render` sem órfãos; estender a todos adapters. 15. Observabilidade: TelemetryEventV1 não-autoritativa + receipts verificáveis. 16. Circulares: adapters só dependem para baixo (xtask layers pattern). 17. Descoberta sem 300 tools: `list_commands{filter,enabled_only}` + `capabilities()` manifesto (RC-01). 18. Experience Compiler: só transições tipadas verificadas + testes +/- reais (CWN-08). 19. Rust: só via CLI/MCP/subprocess pinado, nunca link (exceto WASM isolado). 20. Ganho profunda vs externa: -2-3 serializações, -1 processo por preview, undo unificado, 1 fonte editável; custo: disciplina de owners (já paga).

## 8.5 Recomendação
**Adotar E (Hybrid Creative Kernel = D-043) com correções:** (a) unificar timeline/commands/RenderContext/sanitize/MP4 antes de features; (b) RC-01/02/10 primeiro (contratos); (c) engines sempre `EXTERNAL_PROCESS` (FFmpeg/Blender/GIMP/Natron/Remotion) ou `WASM_MODULE` (Replicad) ou `WRAP_ENGINE` (Penpot MCP, Three.js lib MIT); (d) nenhum link GPL/AGPL/proprietário; (e) mesma TaskRun/authority/proveniência, caches partilhados, recovery por job.
