# 06 — PROMPT IMPLEMENTADOR: PLAYWRIGHT-C2C PATCH-KITS (usar em missão posterior)

**Preflight real de 12/10/2026: BLOCKED.** Não iniciar os kits sem concluir o [Stage A corretivo](08-REMEDIACAO-STAGE-A.md), conforme [registro do gate](07-GATE-0-BLOCKED-2026-10-12.md). Nenhuma dispensa do gate está presumida.

**INSTRUÇÃO PARA O IMPLEMENTADOR:** assumir implementação técnica APÓS satisfazer os gates. Este documento NÃO autoriza alterar o runtime na missão de auditoria. Você possui acesso ao checkout local Hermes e à referência Playwright.

## Contexto congelado

- Repositório: `C:\Github\hermes-agent`.
- Referência: `C:\Github\hermes-agent\referências\02-Browser-Automacao-Web\playwright-main`. Version declarada `1.65.0-next`, Apache-2.0, snapshot sem metadados Git; usar hashes SHA-256 de `01-INVENTARIO-E-LICENCAS.md`.
- Auditoria completa: `workstation/research/playwright-code-to-code-2026-10-12/00..06`.
- Baseline da auditoria: `audit/browser-native-evidence-20261012@c39739a187`; **não é baseline de release qualificada**.
- Código já existente: `apps/desktop/electron/workstation-browser-runtime.ts`, `workstation-browser-snapshot.ts`, `workstation-browser-batch.ts`, `workstation-browser-batch-proof.ts`, `workstation-browser-task.ts`, `workstation-browser-extract-cache.ts`, `workstation-browser-snapshot-diff.ts`; `tools/browser_workstation.py`; `workstation/telemetry/browser_observation.py`; `workstation/operational_kernel.py`.
- As modificações não commitadas do checkout principal em Browser Hub/right rail pertencem a outros agentes: preserve-as.

## Passo ZERO — autoridade, baseline e execução permissível

1. Ler `AGENTS.md`, `workstation/AGENTS.md`, `workstation/context/README.md`, `UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md`, `H079_2_UPSTREAM_DOGFOOD_CLOSURE_2026-09-20.md` e a matriz `02` deste pacote.
2. Registrar `DOWNSTREAM_MAIN_SHA`, `UPSTREAM_MAIN_SHA_OBSERVED`, `CURRENT_PIN_SHA`, `git merge-base`, ahead/behind, CI required, seams afetadas e estado de main; não pressupor que c39739a187 é verde.
3. Fazer Stage A upstream-first em branch isolada com pin único e baseline qualificada. Se gate RED ou falta autorização/exceção, **NÃO codar runtime**; registrar BLOCKED e produzir plano de remediação, sem inventar green.
4. Criar worktree separado do checkout principal e não sobrescrever mudanças de terceiros. Não push, PR ou merge main sem ordem/qualificação.

## Owner e invariantes inegociáveis

O único owner do Chromium é `WorkstationBrowserRuntime` com `Electron WebContentsView`. TaskRun/BrowserTask/lease/CertifiedDispatcher/OperationalKernel/ExperienceCompiler permanecem como implementados. Não criar outro browser, daemon, dispatcher, estado de sessão, persistência de autoridade, LLM agent ou roteador. `409 USER_CONTROL_ACTIVE` é fail-closed. Validação de efeito local não prova efeito remoto. Zero retry cego de mutações após timeout/ACK incerto. Reuse H013/H-079, receipts e existing verifier. Não copiar BrowserOS AGPL.

## Implementar na ordem exata (somente depois do gate)

### C2C-I01 — Test harness Electron Nativo (PW-05, primeiro)

Ler Playwright `tests/electron/electron-webcontentsview.spec.ts:17–33`, `electron-tracing.spec.ts:23–53`, `electronTest.ts:18–121` e `tests/electron/playwright.config.ts`.

Criar fixture local/offline do Electron **do Hermes**, perfil temporário próprio e verificação da view anexada. Playwright atua como test client, jamais backend de browser no produto. Escrever RED para descoberta WebContentsView/Tab, takeover, crash/restart, iframe, snapshot e readback em objeto real, verificar PID e isolamento. Não enviar ações a sites reais. Copiar apenas fragmentos pequenos de teste se realmente necessário, com copyright Apache-2.0/NOTICE e revisão de dependências. GREEN exigido com Electron real, não FakeWebContents.

### C2C-I02 — Actionability independente (PW-01/PW-02)

Ler `packages/playwright-core/src/server/dom.ts:330–399,402–479`, `packages/injected/src/injectedScript.ts:699–759,1037–1205`, `client/locator.ts:48–98`, `roleSelectorEngine.ts:26–95`.

Introduzir helper read-only de target, validando `isConnected`, visible/enabled/non-inert, stable across animation frames, scroll/viewport e que hit-test não aponte para overlay estranho. Aceitar role/name/testid apenas sob escopo autorizado e strictness: 0 match = stale, 2 matches = ambíguo, nunca selecionar primeiro implicitamente. Revalidar lease, task/run, tab, epoch e document identity após cada await. Encaminhar input apenas pela função existente de click/type. Nunca promover ACK ou hit-test a VERIFIED. RED ACT-01..05 e GREEN. Flag default-off, fallback fail-closed.

### C2C-I03 — Invalidação SPA estruturada (PW-06)

Ler `snapshotterInjected.ts:76–156,367–433` e `workstation-browser-runtime.ts::extractItemsForEntry`.

Instrumentar MutationObserver estrutural scoped, monotonic revision, reset por navigation/documentEpoch, listener cleanup por destroy/restart. Chave de cache incorpora revision além de schema/query/tab. Se observer falhar: bypass cache, nunca devolver stale data. Não salvar mutations, DOM ou texto. RED SPA-01..03 demonstrando mudança de texto/atributo sem alteração de childElementCount. GREEN. Testar Shadow DOM ou documentar coverage parcial com bypass.

### C2C-I04 — Frame identity e cancelamento (PW-03/PW-04)

Ler `server/chromium/crPage.ts:442–468,635–665`, `server/frames.ts:839–882,1143–1195`, `server/progress.ts:37–143`.

Amarrar ref a tab/TaskRun/frameId/document/context/loader evidence, mantendo BrowserTask proprietário. Tratar attach/detach/navigatedWithinDocument/contextDestroyed/OOPIF/rendererGone. Waits com deadline monotônico e cancelamento no takeover, stale run e renderer detached; retries permitidos **somente antes de qualquer efeito**, jamais após ação incerta. RED FRM-01/02, LAT-01, crash/recovery, navegação de iframe com URL parent inalterada. GREEN.

### C2C-I05 — Observabilidade e benchmark (PW-08/PW-09)

Ler `server/trace/recorder/tracing.ts:509–529`, `snapshotterInjected.ts:414–430`, `workstation/telemetry/browser_observation.py`.

Acrescentar fases estruturais e diagnósticos semânticos correlacionados `session_id/task_id/run_id/operation_id`. Medir latência stage, CDP por método/nó, DOM/AX source, snapshots/delta model-facing, cache hit/miss, process.cpuUsage/RSS distinguindo MAIN de renderer com PID, custos e tokens do provider usage-owner. Nenhum HAR, cookies, screenshot, DOM HTML, URLs com query/fragment, password, prompt ou dados de usuário. Canary tests devem validar bytes dos SQLite/WAL e capturas de debug. Testar AX feature flag e DOM fallback, parity de target/correção, before/after comparável. Não converter bytes em tokens ou ACK em outcome verificado.

### C2C-I06 — Durable exactly-once (P0, trabalho distinto do Playwright)

**Não implementar simplesmente retry Playwright.** No dono canônico `CertifiedDispatcher + TaskRun + BrowserTask`, identificar journal persistente existente e estendê-lo sem novo dispatcher ou store de autoridade. Registrar admission intent/idempotency key, dispatch uncertainty, confirmed receipt/readback/outcome, collision run/tab/document e reconciliação. RED de lost receipt, crash after write, operações intercaladas, restart/replay antigo e takeover. Executar em isolamento e só declarar GREEN com prova causal/external verifier apropriado. Telemetry é observador, não journal.

## Testes, rollback e critérios obrigatórios

- Cada passo: RED→GREEN em teste com expectativa legítima de falha anterior, commits pequenos, lint/typecheck, regressões Browser, privacy canaries e E2E real no app.
- Build baseline + target mesmo upstream pin e ambiente; registrar n, p50/p95, variance, CDP count, CPU+RSS por processo, correção, uncertain rate e tokens reais (se conhecidos).
- Rollback por flags feature-off e cache bypass; nunca fallback externo, retry automático ou degradação de consentimento/authority.
- Atualizar ``ROADMAP`, journal, Intelligence e source matrix com hashes, resultados e falsificações, não com “implemented” sem exato teste.
- Qualificação final inclui CI exact-head, Windows native-E2E, H013/H-079, seam audit e upstream drift apenas observado (pin fixo), sem merge nem push sem autorização.

## Entrega final do implementador

Entregue para cada kit `ANTES`, `DEPOIS`, alteração exata, fonte Playwright/licença, resultados RED/GREEN, regression, E2E, benchmark com denominadores, privacy audit, riscos, rollback, commits locais e gates restantes. Se algum E2E estiver indisponível, estado `NOT_RELEASE_QUALIFIED` e razão explícita. Não invente resultados ou economias.
