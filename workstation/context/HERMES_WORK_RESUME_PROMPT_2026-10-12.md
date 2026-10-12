# PROMPT DE RETOMADA — P0 Kanban / Browser / Autoridade (ARQUIVADO, NÃO EXECUTAR AGORA)

> Copie o conteúdo deste documento para outra conversa **somente quando o maintainer decidir reabrir a frente**. Estado histórico de referência em 2026-10-12; sempre reconfirme a árvore, os PRs e a documentação antes de editar.

## OBJETIVO
Execute a continuação segura do P0 Kanban e Browser nativo no `kevynlucasprofissional-stack/hermes-agent`, sem reiniciar auditorias já concluídas, sem reimplementar as provas aprovadas, sem tocar banco real e sem merge automático.

## FASE 0 — READ FIRST E RECONCILIAR
Leia `workstation/AGENTS.md` e `workstation/context/README.md`; depois:
- `workstation/context/HERMES_WORK_STRATEGIC_HANDOFF_2026-10-12.md`
- `workstation/context/HERMES_WORK_P0_ISSUES_DETAIL_2026-10-12.md`
- `workstation/context/HERMES_WORK_PR_RECONCILIATION_2026-10-12.md`
- `workstation/context/HERMES_WORK_DECISION_RATIONALE_2026-10-12.md`
- `workstation/context/KNOWN_ISSUES.md`, `DECISIONS.md`, `ROADMAP.md`, `HERMES_WORKSTATION_INTELLIGENCE.md`, `engineering-journal/CURRENT.md`.
Na branch do PR #83, leia `P0_KANBAN_BROWSER_AUTHORITY_HANDOFF_2026-10-12.md`, `P0_KANBAN04_HANDOFF_ATOMICITY_2026-10-12.md`, `P0_PROOF_RECONCILIATION_2026-10-11.md`, `P0_INTEGRATION_2026-10-11.md`.

Confronte GitHub #70–#77/#79–#83 (e trabalhos posteriores), HEADs/base/CI/exact-head, com o checkout remoto, incluindo dirty status. **Não use SHA histórico como estado corrente sem confirmação.** Crie worktree isolado. Não resetar nem limpar `C:\Github\hermes-agent`, não alterar PRs de implementação involuntariamente.

Snapshot histórico:
- worktree `C:\Github\hermes-agent-kanban-browser-authority-20261012`
- PR #83: `https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/83`
- branch `fix/p0-kanban-browser-authority-20261012`
- HEAD `22498a09db0802c06125f5a5ec4cb5039da9b98f`
- base `fix/p0-proof-bound-completion-20261011` (#80), stacked em #79→#76.
- evidência local final reportada: Python 34 pass / Electron Vitest 58 pass / Electron Chromium native 4 pass; GitHub Actions/status checks **não confirmados**.

## FASE 1 — NÃO REFAZER O QUE ESTÁ VERDE
#83 já inclui isolamento por sessão de Browser e TaskRun, proteções stale-run, correção do id global, intent de Kanban, concorrência de triage+claim e de JSON handoff, lease humano 409, restart BrowserTask e E2E de efeito aplicado com ACK perdido seguido de readback único. O teste nativo de clique/POST/GET NÃO cobriu UI handoff real. Não marque KANBAN-04 como QUALIFIED com base nele.

## FASE 2 — PRIMEIRO GATE PENDENTE (TDD)
A partir de `workstation/integrations/hermes/tool_batch_admission.py::workstation_tool_batch_admission()`, rastreie `BatchAdmissionAction.HANDOFF` através de `agent/turn_tool_round.py` e `run_agent.py` até o IPC/renderer e UI real. Use o `HumanHandoffManager` existente, identidade `task/run/session/operation/resource/scope`, política de leases e `409 USER_CONTROL_ACTIVE`. Não forje grants nem reabra handoff consumed.

Crie RED antes de GREEN para cenário nomeado:
`P0: uncertain native Browser mutation requires single human handoff, independent readback and safe resume`.

Prove E2E com mutação Browser real aplicada uma vez (ACK perdido), estado incerto enviado à UI, aprovação do usuário exatamente uma vez, observação read-only independente, `VerificationContract` validado por `evaluate_verification()`, evidência vinculada à task/run/op/recurso, continuação somente de trabalho pendente sem repetir a mutação; segundo chat permanece livre. Falta de prova ⇒ permanece BLOCKED. Divergência ⇒ não declarar sucesso. Restart entre handoff e readback ⇒ nenhuma revisão/efeito duplicado. Falhar fechado em IDs ou leases incompatíveis.

## FASE 3 — OUTROS GATES
KANBAN-01 corpus/semântica; 02 restart e concorrência end-to-end; 03 contratos de aceitação tipados por tipo de efeito; 05 isolamento dos bloqueados/órfãos; 06 preflight privado de 106 tarefas e 55 handoffs **sem restaurar nada automaticamente**; 07 CI exact-head, qualificação Windows packaged e PR chain H-079.

Não misture worktrees concorrentes; não faça merge main; não altere sessões/cartões/handoffs reais; não publique dados privados em GitHub.

## FASE 4 — ACEITE E STOP PROTOCOL
Mostre RED/GREEN por teste, comandos, versão exata do código, resultados de nativo/CI e limites. Atualize os registros canônicos e PR com fatos (não promessas), faça commit/push só após validação apropriada. Ao interromper, gere **outro prompt completo de retomada** com commit remoto exato, branch/worktree, primeiro teste pendente, o que foi modificado, evidências, blockers, restrições, e mesma exigência recursiva de novo handoff. Nunca alegar progresso que não foi comprovado.

**NÃO execute esta missão enquanto o trabalho permanecer em pausa estratégica.**
