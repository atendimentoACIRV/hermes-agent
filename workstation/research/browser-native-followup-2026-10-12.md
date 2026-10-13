# Browser nativo — investigação code-to-code e correções isoladas (2026-10-12)

**Classificação:** EXPERIMENTO LOCAL / CODE CHANGES TESTED / NÃO QUALIFICADO PARA RELEASE.
**Repositório:** `kevynlucasprofissional-stack/hermes-agent`.
**Base exata:** `main@a2b56db1bc9e0b5acf48d94fa86a9844a1005842`.
**Worktree / branch:** `.worktrees/browser-native-evidence-20261012` / `audit/browser-native-evidence-20261012`.
**Upstream:** `main` possui ancestral `66605471e9f0b0832abbefaf625ce08e948ca540`, mas upstream observado `835c3dd038d903182a66ecc45e34bf5e0de65f00` avançou. Não executar novo merge dentro desta correção.
**Controle de alterações:** checkout original `fix/hermes-oneclick-lock-startup-20261011` tem alterações de outras trilhas; não foi alterado. Sem push, PR ou merge desta branch nesta missão.

## Fontes verificadas

- Referências locais: `referências/02-Browser-Automacao-Web/` (23 diretórios físicos na data; a auditoria de 10/10 declarou 25 projetos avaliados, incluindo escopo adicional).
- Auditoria detalhada preexistente: `workstation/research/browser-code-to-code-2026-10-10/` (afirma 49 sessões analisadas).
- Conciliação canônica: `workstation/context/BROWSER_CODE_TO_CODE_DECISIONS_2026-10-10.md`.
- Implementações já entregues em `main`: histórico de merge `c474b4ed93` e `workstation/context/browser-optimization-kit/IMPLEMENTATION_PLAN.md`. Não recriar OPT-01 batch, OPT-02 AXTree, OPT-03 cache/extract, OPT-04 delta, resiliência nem UX já implementados.
- BrowserClaw `src/actions/batch.ts` e licença `LICENSE`: MIT, mas baseado em Playwright Page; **ADAPT**, não colar literalmente no controlador Electron.
- Stagehand `LICENSE`: **MIT no checkout inspecionado**. A classificação Apache-2.0 no relatório antigo não bate com esta licença. Conferir arquivos/dependências e avisos antes de copiar.
- BrowserOS `LICENSE`: AGPL-3.0. **Não copiar código diretamente** para base MIT; apenas padrão arquitetural reimplementado independentemente.
- Agent Browser `cli/src/native/snapshot.rs`: referência para robustez de identificação do documento e CDP, não substituir owner do Browser.
- `browser-use/desktop` importação de cookies Chrome: HOLD por risco de credenciais e ausência de threat model/consentimento explícito.

## Alterações implementadas nesta branch

### AX-01 — Libertar objetos CDP após captura

**Arquivo:** `apps/desktop/electron/workstation-browser-snapshot.ts`.

Problema observado no código: cada `DOM.resolveNode` cria um objeto remoto, e o caminho AXTree não emitia `Runtime.releaseObjectGroup`. Em capturas repetidas, objetos remotos poderiam permanecer referenciados até limpeza pelo runtime.

Mudança: `objectGroup` único por captura; `DOM.resolveNode({backendNodeId,objectGroup})`; liberação via `Runtime.releaseObjectGroup` em `finally`; falha na limpeza não interrompe fallback. Não altera o owner de CDP, navegador, schema de ferramentas nem a flag `HERMES_BROWSER_AXTREE_ENABLED` (padrão OFF).

**Evidência RED:** 2 testes novos falharam inicialmente por ausência do grupo/liberação.
**Evidência GREEN:** testes de ciclo de vida e fallback passaram após patch.

### AX-02 — Não reaproveitar referências de elementos entre snapshots SPA

**Arquivo:** mesmo módulo.

Problema reproduzido: o contador local começava em `@e1` a cada captura AX. Se um elemento novo surgisse no mesmo URL, poderia herdar uma referência ainda armazenada no mapa persistente `window.__hermesWorkstationRefs.byRef`. Isso podia apontar uma `@e` para o nó errado.

Mudança: atribuir nova referência monotônica via `state.counter + 1` apenas a nós inéditos; preservar ref existente via `byElement`; retirar argumento `@eN` derivado de contador volátil.

**Evidência RED:** caso A→B→A demonstrou novo elemento recebendo `@e1` já alocado.
**Evidência GREEN:** o mesmo cenário manteve `@e1/@e2` no mapa original e deu nova ref ao novo nó.

### Provas e limitações

- Arquivo novo: `apps/desktop/electron/workstation-browser-snapshot-object-lifetime.test.ts`, três testes (remote handles: sucesso/falha; refs em DOM dinâmico).
- Runner focal independente das dependências Vite UI: `apps/desktop/vitest.browser-native-audit.config.mjs`.
- `node ../../node_modules/vitest/vitest.mjs run --config vitest.browser-native-audit.config.mjs` executado a partir de `apps/desktop`: **16 arquivos, 139 testes aprovados, 0 falhas**; mede contratos simulados, NÃO prova Electron nativo E2E.
- `git diff --check` sem erros antes da preparação documental; repetir antes do commit.
- Typecheck `node ../../node_modules/typescript/bin/tsc --project tsconfig.electron.json --noEmit`: **FAILED/AMBIENTE**, múltiplos `TS2307 Cannot find module 'electron'` e erros de tipagem preexistentes fora dos arquivos alterados. O worktree utilizou junction para `node_modules` já presentes no checkout; não instalou dependências. Não declarar typecheck aprovado.
- Não há check GitHub Actions para `main@a2b56db1` (consulta por SHA retornou zero runs/check-runs). H-079/exact-head, Windows native E2E, H004/H013, verificação de memória/latência e release estão **PENDENTES**. Os ganhos de 17x/80–98% da auditoria antiga **não foram medidos nesta missão**.

## Risco de prioridade máxima ainda não corrigido: batch ACK ≠ VERIFIED

**Fonte:** `apps/desktop/electron/workstation-browser-runtime.ts`, caso `browser_batch_actions` (`verifyAfter`, perto das linhas 2635–2670 no baseline).

**Constatação estática:** `verified: Boolean(receiptRef)` é atribuído quando `recordReceipt` retorna identificador, sem readback independente do estado externo. `workstation-browser-runtime-batch.test.ts` espera `verified` contra `FakeWebContents`, sem demonstrar mutação persistida. Um receipt prova registro de uma ação, não seu efeito no aplicativo web.

**Próximo experimento (P0):** criar teste RED que simula ACK + receipt + ausência de delta/efeito; deve resultar `UNCERTAIN`, interromper o lote, e bloquear despacho seguinte. Reutilizar as autoridades existentes de `BrowserTask`, `TaskRun`, `CertifiedDispatcher` e `VerificationContract`; contratos `operationId/runId/taskId/tabId/revision`. Verificar por pós-condições específicas: valores de formulário, estado/DOM de toggle, persistência externa quando aplicável. Cliques genéricos e submits não podem virar VERIFIED só porque um receipt foi gravado. Não dar retry automático em efeitos incertos. Não trocar `409 USER_CONTROL_ACTIVE`, não alterar rotas/fallbacks silenciosamente.

## Próximas melhorias por benefício e risco

| Ordem | Família | Código externo | Onde evoluir | Condição de entrada |
|---|---|---|---|---|
| P0 | Verificação de efeitos batch | BrowserClaw + ownership atual | `workstation-browser-runtime.ts`, BatchAdapter, contratos de verify | RED com receipt sem efeito e E2E |
| P0 | Snapshot AX correctness/perf | Agent Browser, BrowserOS como referência conceptual | `workstation-browser-snapshot.ts` | medir CDP por nó; documento/iframe/Shadow DOM; memory soak |
| P1 | UX Browser nativo | BrowserOS, browser-use desktop | `src/app/browser/` e painel chat | reconciliar mudanças NÃO COMMITADAS de outra trilha antes de tocar |
| P1 | Extract robusto/cache | Stagehand MIT + código local | `extractItemsForEntry`, `BoundedExtractCache` | testes A→B→A, auth wall, digest revision |
| P1 | Navegação SPA | BrowserClaw | `snapshotForEntry`, `did-navigate` | instrumentar waits/retries, evitar polling duplicado |
| P2 | Diagnóstico de drift | Driftlock MIT | `operational_kernel.py` | diagnóstico sem auto-reparo sem readback |
| HOLD | Cookies do Chrome | browser-use desktop MIT | **NÃO implementar** | privacy review + opt-in por perfil/origem |

## Reprodução da regressão na branch

```powershell
cd C:\Github\hermes-agent\.worktrees\browser-native-evidence-20261012\apps\desktop
node ..\..\node_modules\vitest\vitest.mjs run --config vitest.browser-native-audit.config.mjs
cd ..\..
git diff --check
git status --short --branch
```

**Interpretação final:** correções locais para recursos e identidade AXTree verificadas por testes simulados; Browser nativo em produção **NÃO QUALIFICADO** nesta missão. Manter a branch isolada até H-079/release CI e E2E Electron reais.
