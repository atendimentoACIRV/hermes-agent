# Dossiê P0 — diagnósticos e Known Issues rastreáveis (2026-10-12)

**Índice autoritativo de status:** [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md), IDs KI-028–KI-043. Este dossiê é **evidência e critérios de retomada**, não uma segunda máquina de estados. O conjunto foi pausado por estratégia; isso não altera o status técnico.

## Matriz KANBAN-01 → KANBAN-07
| Gate | Última prova do histórico/#83 | Não comprovado e critério de encerramento |
|---|---|---|
| KANBAN-01: intent/admission | #75 D-045 triage, #79 force-work e #83 9 testes de intent; concorrência 2/2 processo | Corpus anonimizado com falsos positivos/negativos; sem cartões ao pedir explicações |
| KANBAN-02: task/run/concurrency/restart | 2 workers disputam Task/claim canônicos; Electron BrowserTask cold restart em 3/3 e 4/4 P0 nativos | Matriz kill/restart/supersession/repetição legítima + packaged app |
| KANBAN-03: conclusão/verificação | #79 proof-bound status+acceptance; #83 teste typed readback negativo | AcceptanceContract por tipo de efeito e prova end-to-end, sem receipt autoautenticado |
| KANBAN-04: handoff humano | #73 dedupe, #83 JSON lock, lease 409, cross-TaskRun guard, lost-ACK 1 vez | **Ciclo real HANDOFF→UI→approve/consume→readback via evaluate_verification→resume sem replay**, reinício, 2 sessões, erro inconclusivo |
| KANBAN-05: isolamento e órfãos | #83 sessão Browser isolada, stale-run fail-closed | Matriz de cartões bloqueados, sessões paralelas, run superseded, órfãos sem contaminação |
| KANBAN-06: histórico | #80 preflight SQLite consistente e inventário privado | **Somente propostas**; nenhuma restauração automática, revisão humana/rollback caso autorizado |
| KANBAN-07: release | 34 Python + 58 Electron unit/Vitest + 4 native source-built E2E; Ruff/tsc scoped | packaged Windows One-Click, CI HEAD exato, H-079 e cadeia PR #76→#79→#80→#83 |

## Defeitos, fundamentos e pontos de entrada
**KI-028 — sessão empresta execução antiga:** `tools/browser_workstation.py::_dispatch` anteriormente escolhia a única task não done de outra operação ou variáveis process-level. #83 passou a exigir identidade de card/run explicitamente vinculada à sessão e a recusar `STALE_RUN` para run não-running/estrangeira. Outro `HERMES_OPERATION_ID` global podia provocar idempotency false-hit; #83 impede vazamento. Abrir reprodução com duas sessões e 1 task bloqueada; nenhuma mutação deve usar run alheia. Status: PARTIALLY_FIXED.

**KI-029 — admissão semântica indevida:** `workstation/kanban.py::is_multistep_request`, `workstation/work_intent.py::prepare_turn_work` e `workstation/task_compiler.py::batch_intent`. Palavras workflow/pipeline e perguntas cognitivas geravam cards; imperativos multi-op com pergunta ou "escreva" escapavam. #75 e #83 corrigiram exemplos; falta benchmark representativo e monitor de regressão. Status: QUALIFICATION_PENDING.

**KI-030 — efeitos classificáveis incorretamente:** `tools/kanban_tools.py` e `tools/effects.py`, Browser/console/todo previews. PR #71/read, #72/BOA-001, interações `INTERACTIVE`; console com expression e todo_list com escrita continuam `MUTATION`; fallback unknown fechado. Status: FIXED_UNVERIFIED em produto.

**KI-031 — recusa envenena ledger e reabre aprovação:** `workstation/batch_detection.py` / `workstation/execution_policy.py` / `workstation/runtime.py::HumanHandoffManager`. Uma recusa pré-dispatch não é efeito incerto, mas timeout após dispatch pode ser; dedupe de handoff deve ser por task/session/run/op/scope, e consumed não gera novo popup. #73 e #83 testes locais. Status: PARTIALLY_FIXED; UI ponta a ponta faltante.

**KI-032 — supersession sem continuação:** `workstation/authority_supersession.py` / `workstation/task_compiler.py`; erro genérico `SUPERSEDED` podia perder pendências. #74 retorna `AUTHORITY_SUPERSEDED` ou `CANONICAL_RUN_UNCLAIMED`, grava operação não executada e exige nova reivindicação canônica. Status: QUALIFICATION_PENDING no orchestrator/E2E.

**KI-033 — conclusão falsa por receipt:** `workstation/integrations/hermes/completion_admission.py`, `workstation/work_intent.py`, `workstation/verifier.py`. #79 exige task/run compatíveis, `verified_completed` e `acceptance_approved=True`. Generic `AcceptanceContract` para efeitos heterogêneos segue insuficiente. Não equivaler execução com verificação independente. Status: PARTIALLY_FIXED.

**KI-034 — aprovação UI não conectada:** primeiro ponto exato de retomada `workstation/integrations/hermes/tool_batch_admission.py::workstation_tool_batch_admission()`, `BatchAdmissionAction.HANDOFF`, `agent/turn_tool_round.py`, `run_agent.py` e ponte real IPC/renderer; usar `VerificationContract/evaluate_verification()`, observer read-only real e identidade completa. Testar 1 mutação externa recebida com ACK perdido, UI humana e retomada sem repetir. Status: OPEN / P0.

**KI-035 — lost-ACK do Browser:** a prova nativa #83 fez POST uma vez após clique, descartou recibo e confirmou via GET/snapshot sem segundo clique. O E2E local NÃO percorre a interface de aprovação e continuação da TaskRun. Status: QUALIFICATION_PENDING.

**KI-036 — concorrência do handoff ledger:** `workstation/runtime.py::HumanHandoffManager` JSON mantinha snapshots em memória e perdia atualizações entre processos. #83 utiliza lock `hermes_cli.active_sessions._FileLock`, reload e atomic replace; falha fechado em corrupção. RED→GREEN com dois processos Windows. Status: FIXED_UNVERIFIED em produto final.

**KI-037 — histórico Kanban e órfãos:** #80 `workstation/kanban_reconcile_preflight.py`: snapshot backup SQLite consistente/WAL, quick_check, manifesto privado sem write em origem; 19 tarefas atuais, 106 históricas sem overlap, 55 handoffs sem tarefa vinculada; 19 PRESERVE / 106 RETAIN_DELETED / 55 MARK_FOR_HUMAN_REVIEW. Valores são snapshot local datado e devem ser revalidados. Status: BLOCKED quanto a qualquer reparo real até autorização.

**KI-038 — UI travada/leases:** Teste #2 mostrou reaprovações e `SUPERSEDED`; há também problemas independentes de oclusão de superfície nativa e botões. #83 comprovou cliques reais Take/Release, 409 e cold restart, mas sem afirmar solução universal. Status: PARTIALLY_FIXED.

**KI-039 — CI e release:** H-079 `PASS_WITH_AUTHORIZATION` aprova desenvolvimento excepcional, não substitui Actions exact-head/instalador empacotado. No PR #83 statuses/workflow_runs vazios. Status: QUALIFICATION_PENDING.

**KI-040 — One-Click:** #70 reporta lock corrigido e fingerprint para evitar `npm ci` redundante; não demonstrou packaged/offline/warm real + HyperFrames ausente. Status: QUALIFICATION_PENDING.

**KI-041 — Creative:** D-043 oferece backend/editor React estrutural; #77 cria renderer-local JSON/SVG e #81 apresenta IPC CAS com `resolveTrustedOwner: () => null` (DENY-ALL). Falta identidade TaskRun atestada, projeto único humano/IA, MP4 decodificado, GLB 3D. Status: PARTIALLY_FIXED.

**KI-042 — Browser custo:** batch, AXTree, cache, diff e projeção de payload reduzem estruturas em fixtures; relatos de 70–85% ou custo total não possuem benchmark p50/p95 + tokens pareados com equivalência de resultado. Status: OPEN (medição).

**KI-043 — Prefabs/Experience Compiler:** OPC-00–06 e #82 criam catálogo/reuse em trilhas próprias, mas live Trello, P3 triggers, proof exato/CI e comportamento de produção não demonstrados; nunca autopromover nem criar segundo executor/owner. Status: QUALIFICATION_PENDING.

## Critérios transversais de segurança
- Uma recusa antes do dispatch não vira `uncertain`. Efeito possivelmente aplicado sem recibo exige **readback independente**, não retry cego.
- Aprovação humana não é certificado de efeito; revisão consumida não pode ser usada por outra TaskRun.
- Controle humano ativo retorna 409; uma sessão não assume a BrowserTask ou lease de outra.
- Persistência canônica deve continuar no SQLite/JSON owner existente; não criar TaskDB/SessionDB/HandoffDB paralelo.
- Toda alteração de release precisa de E2E real, CI SHA exato, reconciliação upstream H-079 e cadeia stacked resolvida.
- Não fazer cleanup destrutivo de 106 cards/55 handoffs; só dry-run histórico privado e review sob autorização.

## Fontes e qualificação
Export original: SHA-256 `f429972fb70f97af5131bb81df274edbfb9614a89d050f077224ea5aa4f0251b`, fonte privada. [Manifesto](HERMES_WORK_SOURCE_EVIDENCE_MANIFEST_2026-10-12.md); [PRs](HERMES_WORK_PR_RECONCILIATION_2026-10-12.md); documentos P0 **no ref #83**, não em main: `P0_KANBAN_BROWSER_AUTHORITY_HANDOFF_2026-10-12.md`, `P0_KANBAN04_HANDOFF_ATOMICITY_2026-10-12.md`, `P0_PROOF_RECONCILIATION_2026-10-11.md`. Novos testes citados são evidência de runs históricas/PR, não foram reexecutados por esta missão documental.
