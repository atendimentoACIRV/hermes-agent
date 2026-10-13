# Strategic Handoff — Hermes Work Kanban / Browser Authority (2026-10-12)

**DECISÃO:** `PAUSED_BY_STRATEGY` — suspensão deliberada dos esforços de implementação nesta frente, sem supor que suas pendências foram resolvidas. **Não executar o prompt de retomada agora.** Nenhum runtime, DB, sessão, handoff, PR de implementação ou merge foi alterado por esta intervenção documental.

## A. Estado factual na suspensão
- `main` verificada neste snapshot: `a2b56db1bc9e0b5acf48d94fa86a9844a1005842`; documentação geral da main anterior à sequência #70–#83.
- O mais recente checkpoint publicado da frente é [PR #83](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/83), branch `fix/p0-kanban-browser-authority-20261012`, commit `22498a09db0802c06125f5a5ec4cb5039da9b98f`, base `fix/p0-proof-bound-completion-20261011` (PR #80). O PR continua DRAFT/OPEN/UNMERGED na última consulta. É **stacked** sobre #80 → #79 → #76, que agrega #70–#75; não é fatia pronta para merge direto na main.
- Código relatado/testado no PR #83: Browser sessão não empresta run/operation_id de processo ou cartão bloqueado; task/run/sessão precisam casar; criação de tasks ingressa em triage; 2 processos competem sem duplicar TaskRun; `HumanHandoffManager` segura JSON com lock interprocesso e atomic replace; aprovação/revisão isolada por TaskRun; UI Take/Release + 409 humano; Electron cold restart; readback nativo após clique HTTP POST com ACK descartado, sem novo clique.
- Evidências da execução mais recente: 34 Python PASS, 58 Electron/Vitest PASS, 4 Electron/Chromium E2E PASS em 193,29s; TypeScript E2E scoped, Ruff e git whitespace PASS, **como reportado no histórico/docs do branch**. GitHub #83 HEAD: `statuses=[]` e `workflow_runs=[]`; não implica CI GREEN.
- **NÃO QUALIFICADO:** o fluxo real inteiro `BatchAdmissionAction.HANDOFF → UI aprovação → consume once → observer read-only → VerificationContract/evaluate_verification() → TaskRun resume sem replay`; aplicativo Windows empacotado/One-Click; exact-head CI H-079; classificação de intent com corpus representativo. KANBAN-04 permanece `PARTIALLY_FIXED`.
- Estado root remoto Windows observado: `C:\Github\hermes-agent` na branch `fix/hermes-oneclick-lock-startup-20261011`, HEAD local `9fffa7f3ff` com várias alterações não commitadas, inclusive componentes UI/browser e dados de dogfood. **Preservar.** Worktree #83 isolado: `C:\Github\hermes-agent-kanban-browser-authority-20261012`. Não alterar nenhum deles nesta documentação.

## B. Por que suspender
Mudança deliberada de direção e alocação de esforço, **sem abandonar aprendizagem**. A próxima estratégia de produto NÃO foi definida neste artefato. Backlog permanece existente e tecnicamente aberto; pausa não concede status RESOLVED nem baixa severidade.

## C. Não perder
1. Falha central não era apenas lentidão: tarefas auto-promovidas e borrowing de run causavam bloqueios em conversa, revisões repetidas, `SUPERSEDED` e UI confusa.
2. `Session ≠ Task ≠ TaskRun` (D-045); triage é compromisso sem permissão de mutação, execução precisa claim tipado/canônico.
3. `PURE_READ` não é `MUTATION`; operações browser são `INTERACTIVE` quando aplicável, mantendo guarda nativa; `browser_console(expression)` continua operação potencialmente mutante.
4. Não transformar sucesso do dispatch, snapshot próprio ou aprovação humana em prova de efeito. Um timeout após dispatch é indeterminação real: readback externo antes de possível retry.
5. Handoff `request/resume/consume` deve ser atômico entre processos e limitado à operação/TaskRun. Revisão consumed não deve criar novo prompt nem autorizar outra run.
6. Navegação de uma sessão não absorve `HERMES_OPERATION_ID` global ou `HERMES_KANBAN_RUN_ID` de outra sessão.
7. 106 tarefas antigas / 55 handoffs órfãos: **somente inventário/dry-run local**. Nada de restauração ou eliminação sem aprovação humana e plano de rollback.
8. #77 Creative renderer e #81 Creative CAS IPC continuam sem edição humano+agente end-to-end; #82 Experience Compiler sem prova ampla. A arquitetura das frentes permanece aproveitável.
9. Hipóteses de redução 70–85% de custos/latência não foram validadas com benchmark de tarefas equivalentes e mesma verificação. Instrumentar antes de reivindicar economia.
10. Não duplicar owners (Kanban, SessionDB, TaskRun, browser, aprovação, CreativeDocument, OperationalCapability). Guardrails H-079/D-042 continuam vigentes.

## D. Artefatos e grafo de implementação
Documento canônico: [Known Issues](KNOWN_ISSUES.md) com detalhamento [P0](HERMES_WORK_P0_ISSUES_DETAIL_2026-10-12.md). [PR snapshot](HERMES_WORK_PR_RECONCILIATION_2026-10-12.md). [Manifesto](HERMES_WORK_SOURCE_EVIDENCE_MANIFEST_2026-10-12.md). [Decisões](HERMES_WORK_DECISION_RATIONALE_2026-10-12.md).

**Na branch do PR #83 (não na main no momento da consulta):**
- `workstation/context/P0_KANBAN_BROWSER_AUTHORITY_HANDOFF_2026-10-12.md`
- `workstation/context/P0_KANBAN04_HANDOFF_ATOMICITY_2026-10-12.md`
- `workstation/context/P0_PROOF_RECONCILIATION_2026-10-11.md`
- `workstation/context/P0_INTEGRATION_2026-10-11.md`

**Principais seams:** `workstation/integrations/hermes/tool_batch_admission.py`, `agent/turn_tool_round.py`, `run_agent.py`, `workstation/runtime.py::HumanHandoffManager`, `tools/browser_workstation.py::_dispatch`, `workstation/task_compiler.py`, `workstation/kanban.py`, `workstation/integrations/hermes/completion_admission.py`.

**Testes relevantes do histórico:** `test_denied_mutation_handoff_recovery.py`, `test_p0_uncertain_mutation_readback.py`, `test_p0_handoff_concurrent_owner.py`, `test_p0_multiprocess_task_admission.py`, `test_p0_concurrent_task_admission.py`, `test_browser_session_run_isolation_p0.py`, `test_p0_completion_proof_boundary.py`; suite Electron `workstation-headless-load` com filtro `P0:`.

## E. Matriz de retomada, por ordem de dependência (NÃO EXECUTAR)
**KANBAN-04**: Primeiro conectar `BatchAdmissionAction.HANDOFF` do owner Python ao transporte e UI nativos com identificadores de task/run/session/op/resource/scope. Após aprovação, consumir uma vez, observar por leitura real, avaliar contrato tipado, prosseguir sem repetir o efeito. Manter `BLOCKED` quando indeterminado, detectar divergência. Cobrir 2 sessões + cold restart + lease 409. Não criar novo sistema de aprovação.

**KANBAN-01**: Corpus de intenção e falsos positivos/negativos.
**KANBAN-02**: Worker death/restart, concorrência, ownership, claim/supersession, repetição legítima.
**KANBAN-03**: AcceptanceContract por tipo (texto, leitura, artefato, Browser, efeito remoto), verificação independente.
**KANBAN-05**: Isolamento bloqueios e órfãos, sem contaminação de novas conversas.
**KANBAN-06**: reconciliação só preflight; decisão humana necessária para qualquer modificação real.
**KANBAN-07**: review de PR chain, CI exato, upstream H-079, packaged Windows e One-Click.

## F. Primeiro ponto exato para futuro agente
Arquivo/função: `workstation/integrations/hermes/tool_batch_admission.py::workstation_tool_batch_admission()`. Acompanhar o resultado `BatchAdmissionAction.HANDOFF` por `agent/turn_tool_round.py` / `run_agent.py` até o renderer/IPC; ligar esse mesmo handoff à interface de revisão e ao `VerificationContract/evaluate_verification()`. **Teste RED obrigatório proposto:** `P0: uncertain native Browser mutation requires single human handoff, independent readback and safe resume`. A implementação real exige inspeção do HEAD atual e TDD; **não** é parte desta missão documental.

## G. Impacto noutras frentes
- **Creative:** precisa autoridade TaskRun/IPC e revisão CAS sem segundo estado, aproveita a segurança de handoff e verificação tipada.
- **Browser:** UI que perde controle/receipt e leases entram no mesmo modelo causal; batch, diff/cache devem provar payload/custo empiricamente.
- **Experience Compiler:** reutilização só com execuções realmente verificadas e owner único, nunca compilar falsa conclusão nem autopromover.
- **One-Click:** fixture Electron de restart não substitui validação de aplicativo empacotado nem startup offline.
- **Produto:** priorizar resultado efetivamente utilizável e comprovado, não só infraestrutura/autotestes.

## Instruções de recuperação
1. Fetch/remotes e árvore limpa em worktree dedicado; não tocar root com alterações não commitadas.
2. Conferir [PRs](HERMES_WORK_PR_RECONCILIATION_2026-10-12.md), commits, bases, diffs, CI e documentação do branch.
3. Verificar se parte do gate já avançou em outro PR. Não reimplementar.
4. Atualizar Known Issues/Jornal/Roadmap após execução e gerar outro prompt se interrompida.
5. O [prompt pronto](HERMES_WORK_RESUME_PROMPT_2026-10-12.md) fica arquivado e **não foi executado**.
