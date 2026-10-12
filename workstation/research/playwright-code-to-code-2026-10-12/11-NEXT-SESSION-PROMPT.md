# CONTINUE HERMES BROWSER C2C — P0-02 → P1 (IMPLEMENTAÇÃO E HANDOFF RECURSIVO)

**IMPLEMENTAÇÃO DIRETA, NÃO REAUDITORIA.** Use Remote Desktop Commander, GitHub, Superpowers e Community Agent Workflows conforme disponíveis; TDD RED→GREEN, commits pequenos, regressões, E2E Windows e checkpoint. Execute o máximo possível e prossiga por todas as fases seguras, sem perguntar a cada passo.

## ESTADO EXATO CONHECIDO — RECONFIRMAR PRIMEIRO
- Repositório: `C:\Github\hermes-agent` — checkout principal DIRTY em UI Browser Hub/right rail por outros agentes: **NÃO TOCAR**.
- Worktree: `C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012`.
- Branch: `feat/playwright-c2c-kits-20261012`.
- Último HEAD de código confirmado: `da3ca495690bc56b26088fb40d8a2c594348d30a`. Um commit documental posterior pode mudar o HEAD: verificar `git rev-parse HEAD` e `git status --short --branch` ANTES de agir.
- Stage A upstream refresh/pin/seams: `PENDING_WITH_MAINTAINER_AUTHORIZATION`. **PULAR a Stage A DURANTE DESENVOLVIMENTO LOCAL**; ela continua gate de merge/release. Nenhum push/PR/merge autorizado; `NOT_RELEASE_QUALIFIED`.
- Auditoria canônica: `workstation/research/playwright-code-to-code-2026-10-12/00..09`; checkpoint atualizado: `10-IMPLEMENTATION-CONTINUITY.md`.

## NÃO REPETIR — PATCHES E EVIDÊNCIAS
- Commits anteriores `81a16ed00b` (admissão persistida + hash); `7623bfbfcb` (crash/restart real dois Electron); `246477e4c0` (actionability pré-scroll).
- NOVO `20acf1d2e9`: CRASH-03 provou duas admissões simultâneas (RED), corrigiu com lock create-only interprocessos sem segundo store, preserva ledger em session saves stale; Node runner concorrente PASS (1 admitted / 1 rejected).
- NOVO `da3ca49569`: impediu replay ANTES de criar WebContentsView, corrigiu duplicação de GET provocada por lazy restore; navegação pendente sem receipt recupera aba com `about:blank`, snapshot real funciona; operações com receipt mantêm recuperação normal; generated op ID de admissão e receipt é o mesmo.
- **Evidências finais dos patches:** `cd apps/desktop && node ../../node_modules/vitest/vitest.mjs run --config vitest.browser-native-audit.config.mjs --reporter=default`: **168 testes / 19 arquivos PASS**. `node electron/workstation-browser-crash-replay-native.runner.cjs`: dois PIDs reais, 1 HTTP effect, replay e read-only snapshot seguros, PASS. `node electron/workstation-browser-admission-concurrency.runner.cjs`: PASS. `node electron/workstation-browser-playwright-native.runner.cjs`: PASS.
- Typecheck completo ainda `FAIL` apenas erro anterior `electron/git-review-ops.test.ts(124,5) TS2349 simple-git not callable` (outro subsistema). Python telemetry 7/7 passou na sessão anterior, reexecutar caso relevante.
- Teste GET com efeito foi adversarial **em loopback**, não é certificação de POST clique nem exatamente-uma-vez externo.

## PRIMEIRO COMANDO
`git -C "C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012" status --short --branch`
`git -C "C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012" rev-parse HEAD`
`git -C "C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012" log -6 --oneline`

## PRÓXIMO RED (P0-02) E IMPLEMENTAÇÃO
Falta journal canônico terminal **POR OPERAÇÃO** e verificação causal. Uma operação A pode ficar UNCERTAIN após crash, mas NOVO operation_id B talvez ainda dispare no mesmo TaskRun/tab. Escreva primeiro fixture RED entre dois processos Electron usando contador de efeitos de loopback:
- processo A admite e produz efeito, crash antes de receipt;
- B tenta uma NOVA mutação no mesmo TaskRun/tab com ID diferente; deve receber `RECONCILIATION_REQUIRED`, sem segundo efeito. Não bloquear indevidamente operação cujo efeito foi comprovadamente terminal.
- Testar também A→B→A, lost receipt, colisão entre processos, lock de crash órfão sem auto-delete, takeover 409, renderer gone, truncated/corrupted ledger, e falhas de fsync.
- Estender APENAS owners existentes `workstation/control_plane/dispatcher.py` (CertifiedDispatcher), `workstation/journal.py` (ExecutionJournal), `workstation/operational_kernel.py`, `apps/desktop/electron/workstation-browser-task.ts`, `workstation-browser-session-state.ts` e `workstation-browser-runtime.ts`. Admit/dispatch/ACK/readback/EXTERNALLY_VERIFIED devem ser estados distintos. Sem novo dispatcher, sem store paralelo, sem autopromoção de receipt local a VERIFIED.
- Testar extensão/creative mutators pelo proprietário correto sem criar BrowserTask falso. Retention cap 4096 + whole-file fsync necessitam benchmark/compaction antes de release.

## RESTANTE DA MISSÃO (NÃO PARAR APÓS UM PATCH)
P0-03 rAF stability, hit target, scroll/focus e mousePressed parcial; P0-04 frameId/loader/context/OOPIF e cancelamento monotônico; P1-01 causal telemetry/canários SQLite/WAL; P1-02 benchmark offline n/p50/p95/CDP/CPU/RSS/tokens reais; P1-03 otimizar AXTree/cache/snapshots só com paridade; P1-04 semantic locators/rich editor; P1-05 ExperienceCompiler evidence-gated; QUAL testes/tsc/CI exact-head/rollback/docs. Stage A ainda não deve ser executada, só preparada para release.

## PROIBIÇÕES E HANDOFF OBRIGATÓRIO
WebContentsView Electron/WorkstationBrowserRuntime owner único. Preservar BrowserTask/TaskRun/CertifiedDispatcher/OperationalKernel/ExperienceCompiler e `409 USER_CONTROL_ACTIVE`; zero retry cego, zero navegação pública de teste, zero credenciais/DOM/URLs privadas em logs, zero overwrite de UI de outros agentes; zero push/merge main. Ao interromper: conferir Git HEAD/status, registrar cada teste RED/GREEN e commit local, atualizar `10-IMPLEMENTATION-CONTINUITY.md` + ROADMAP/CURRENT_STATE/journal/Intelligence/source matrix. **RETORNAR NOVO PROMPT COMPLETO PRONTO PARA COPIAR/COLAR** com HEAD real, branch, worktree, primeiro comando, próximo teste RED, arquivos/funções, testes, gates e restrições; instruir a IA seguinte a repetir recursivamente essa regra até completar o plano. Não entregar só um resumo e não alegar release sem upstream/CI.
