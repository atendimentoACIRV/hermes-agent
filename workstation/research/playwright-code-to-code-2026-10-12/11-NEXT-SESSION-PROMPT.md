# PROMPT DE CONTINUIDADE — Hermes Work Browser C2C-P0–P2

EXECUTE, NÃO REAUDITE. Use GitHub, Remote Desktop Commander, Superpowers e Community Agent Workflows quando disponíveis. Assuma o projeto em andamento e faça implementação direta com RED→GREEN, regressões, commits incrementais e checkpoint. Continue por todas as fases seguras, sem ficar apenas planejando.

## Estado de partida conhecido
- Repo: `C:\Github\hermes-agent` (checkout principal DIRTY, trabalho alheio intocável).
- Worktree: `C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012`.
- Branch: `feat/playwright-c2c-kits-20261012`.
- Último SHA de CÓDIGO confirmado: `81a16ed00b78b7f741c331ee90a3bf06b003942f`.
- A documentação pode ter gerado SHA posterior: PRIMEIRO CONFIRME `git rev-parse HEAD` e `git status --short --branch`.
- Stage A: `PENDING_WITH_MAINTAINER_AUTHORIZATION`. NÃO sincronize upstream, selecione novo pin ou reconcilie seams nesta missão local. Gate de release permanece.
- Push/PR/merge main: NENHUM. Não faça sem autorização. NOT_RELEASE_QUALIFIED.

## Implementado (não refazer)
- E2E Electron WebContentsView, actionability basica, cache SPA MutationObserver, telemetria PID/RAM renderer — commits `1997d1cbf4`, `9f8b4740d8`, `93186e4b44`, `e152603402`.
- `81a16ed00b` adicionou admissão persistente no próprio BrowserSessionStateFilePersistence (sem novo dispatcher): operação, task/session/run/tab/action, SHA256 dos argumentos; fsync Windows r+; replay UNCERTAIN; colisão de ID/digest rejeitada; estado corrompido fail-closed. Navegar/clicar/digitar/scroll/back/press/batch cobertos. Creative/extensões ainda não.
- Vitest usa agora um HERMES_WORKSTATION_HOME temporário por teste; NÃO remova nem toque em arquivos do perfil real.
- RED comprovado: replay A→B→A, API de admission ausente e Windows EPERM fsync; GREEN 19 arquivos / 164 testes, `NATIVE_E2E_PASS` Windows em uma inicialização, ambos exit 0.
- Typecheck Electron geral: FAIL conhecido `electron/git-review-ops.test.ts:124` TS2349 simple-git. Python telemetria 7/7 foi reexecutada nesta sessão em runner Python isolado, exit 0; repetir depois de qualquer alteração.

## PRIMEIRO COMANDO
`git -C "C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012" status --short --branch; git -C "C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012" rev-parse HEAD`

## PRÓXIMO TESTE RED: P0-01 CRASH-01 / CRASH-07 entre dois processos Electron
Modificar `apps/desktop/electron/workstation-browser-playwright-native.e2e.cjs` e `workstation-browser-playwright-native.runner.cjs` para usar dois processos Electron independentes A e B, mesmo perfil TEMPORÁRIO isolado. Fixture loopback contabiliza POST real. Processo A admite mutação, despacha efeito real, é terminado ANTES do receipt. Processo B restaura task/run e reenvia o mesmo operation_id; deve receber UNCERTAIN e não produzir segundo POST. Provar PID, exit code, contador antes/depois e lease. Não basta FakeWebContents ou segundo BrowserWindow no mesmo processo.

Depois: completar P0-02 journal/reconciliação entre `workstation/control_plane/dispatcher.py`, `workstation/journal.py`, `workstation/operational_kernel.py` e BrowserTask, sem novo owner; testar CRASH-02..08, concorrência, digest e falhas de disco. NÃO declarar exactly-once externo sem idempotência/verificador do destino.

## Próximas fases obrigatórias
P0-03 actionability: tirar scroll/focus da fase read-only, rAF stability e mousePressed parcial.
P0-04 frameID/context/loader/OOPIF e waits com deadline cancelável.
P1-01 telemetria causal TaskRun/provider, privacy canary SQLite/WAL.
P1-02 benchmark offline n/p50/p95/CPU/RSS/CDP/tokens e paridade.
P1-03 otimização AXTree/CDP/delta/cache com métricas.
P1-04 role/name/testid/rich editor e strictness.
P1-05 Experience Compiler somente com evidência verificada.
QUAL: typecheck, regressões, native real E2E, CI exact-head quando possível, documentação e gate Stage A PARA RELEASE (não fazer agora).

## Guardrails e handoff recursivo
Owner único WorkstationBrowserRuntime/Electron WebContentsView; preserve TaskRun, BrowserTask, leases, CertifiedDispatcher, OperationalKernel, ExperienceCompiler e 409 USER_CONTROL_ACTIVE. Sem retry de mutação incerta. Sem sites públicos, credenciais, DOM bruto, screenshots e dados de usuário em journals. Não toque na main dirty nem faça push/merge.

Checkpoint canônico `workstation/research/playwright-code-to-code-2026-10-12/10-IMPLEMENTATION-CONTINUITY.md`, relatorio `09-MAINTAINER-EXCEPTION-IMPLEMENTATION-2026-10-12.md` e auditoria 00–08.

Em qualquer interrupção: atualize o checkpoint, registre Git status/HEAD EXATOS, comandos/testes e efeitos; commit verificável quando seguro; responda com um NOVO PROMPT DE CONTINUIDADE COMPLETO e autossuficiente pronto para copiar e colar, incluindo próximos arquivos/funções, primeiro comando, primeiro teste RED, pendências e estas mesmas instruções recursivas. NÃO pare só para planejar.
