# 05 — Plano sequenciado de implementação (handoff, não execução)

**Audit-only:** esta execução não altera runtime, não faz push/merge e não qualifica release. As alterações abaixo dependem de autorização/ciclo posterior e do gate upstream-first.

## Gate 0 — requisito obrigatório

1. Inspecionar HEAD de `main`, `upstream/main`, pin selecionado, merge-base, ahead/behind, hooks, seam manifest e exact-head CI. A baseline documental desta auditoria é `c39739a187`; ela **não** equivale a baseline de release.
2. Executar `workstation/context/UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md`: Stage A separado, pin fixo, baseline qualificada, seam reconciliation. Bloquear feature se CI vermelho e não houver exceção formal.
3. Criar branch/worktree a partir do baseline qualificado. Preservar alterações não commitadas de outros agentes em Browser Hub/right rail.
4. Usar hashes SHA-256 do [inventário](01-INVENTARIO-E-LICENCAS.md), nunca inventar Git SHA do Playwright local.
5. Não adicionar novo browser, SessionDB, scheduler, dispatcher, BrowserTask owner ou agente. Toda mutação continua no TaskRun/BrowserTask/lease/CertifiedDispatcher.

## Cinco patch-kits em ordem recomendada

### PK-02 — E2E real de WebContentsView primeiro

Origem Playwright: `tests/electron/electron-webcontentsview.spec.ts:19–33`, `electronTest.ts:18–121`. Destino Hermes: harness novo em `apps/desktop/electron/*test*`, fixtures locais e H013 existentes. Criar aplicativo de teste do **Hermes** com userDataDir temporário, observar processo principal e WebContentsView anexado, exercitar snapshot, mouse, takeover, crash/restart, iframe, ocultação e renderização. Playwright somente driver de teste, não owner em produção. Red/Green e rollback detalhados em [04](04-TESTES-E-BENCHMARKS.md).

### PK-01 — Actionability antes do clique

Origem: `server/dom.ts:330–399,435–479` + `packages/injected/src/injectedScript.ts:699–759,1037–1205`. Destino: `workstation-browser-runtime.ts::resolvePoint/clickRef/typeRef`, com helper de precondition observável e testes. Retornar `READY/WAIT_SAFE/REJECT_STALE/REJECT_INTERCEPTED/REJECT_DISABLED`. Estabilidade por requestAnimationFrame, enabled/non-inert, scroll e hit-test. Após qualquer await revalidar `409 USER_CONTROL_ACTIVE`, runId, documentEpoch, tab owner. **Retry de check read-only, nunca de mutação incerta.** Flag experimental; rollback mantém fail-closed.

### PK-03 — Frescor do cache de SPAs

Origem: `snapshotterInjected.ts:76–156,367–433`. Destino: `workstation-browser-extract-cache.ts` e `workstation-browser-runtime.ts::extractItemsForEntry`. Introduzir revision monotônica por MutationObserver (childList, characterData, attributes, escopo/Shadow DOM possível) e reset por document epoch. Incluir revision no cache key e invalidar no mismatch; fallback bypass se observer não instalado/indisponível. Provar com mesma URL/title/childElementCount e texto interno modificado. Evitar persistir o conteúdo observado. Feature flag/bypass em rollback.

### PK-04 — Frame identity + espera cancelável

Origem: `server/chromium/crPage.ts:442–468,635–665`; `server/frames.ts:839–882,1143–1195`; `server/progress.ts:37–143`. Destino: `workstation-browser-snapshot.ts`, `workstation-browser-runtime.ts` e estruturas existentes do BrowserTask. Criar read-only binding de frameId/document identity/context/loaderId sem duplicar PageManager. Cancelar polls ao trocar frame, tomar controle humano ou destruir WebContentsView. Garantir que ref antiga não resolva silenciosamente para nova página. Risco alto; E2E obrigatório.

### PK-05 — Telemetria orientada a evidência + AXTree benchmark

Origem: `server/trace/recorder/tracing.ts:509–529` (fases), `snapshotterInjected.ts:414–430` (delta). Destino: `workstation/telemetry/browser_observation.py`, `workstation-browser-snapshot.ts`. Enriquecer apenas fases estruturais precondition/dispatch/ack/local-readback/external-verification com lineage, não HAR nem DOM cru. p50/p95, CDP calls, bytes model-facing, CPU/RSS por processo e outcome real do verifier. AXTree atrás de flag, DOM fallback e paridade. Comprovante externo nunca inferido do resultado local.

## P0 fora da cópia Playwright: durable exactly-once

O mecanismo de retry Playwright não é journal de efeitos externos. Projetar `admission → dispatch → receipt → readback → reconciliation` no **dono canônico** CertifiedDispatcher/TaskRun/BrowserTask. Testar lost receipt, crash após server write, múltiplas operações e replay de ação antiga não mais presente como lastReceipt. Nenhuma emissão da telemetria cria idempotência. Ciclo P0 separado com upstream-first e testes de falha.

## Sequência de gates

`Stage A upstream baseline → E2E fixture → PK-01 actionability → PK-03 SPA → PK-04 frame/cancel → PK-05 telemetry/perf → durable journal próprio → UX reconciliada → target qualification → exact-head CI → drift final snapshot → promoção explícita`.

Após cada kit: commit separado, RED antes de GREEN, testes negativos, revisão de licença/dependências se houve cópia, snapshots dos arquivos SHA, medida de mudança com denominadores e rollback. **H-079 e CI exatos permanecem abertos nesta auditoria**.

## UX de Browser Hub e right rail

Checkout principal possui modificações não commitadas em `apps/desktop/src/app/browser/index.tsx`, `native-view-occlusion.ts` e `workstation-browser-pane.tsx`. Não tocar nessa região até obter HEAD reconciliado/owner da trilha. Em seguida executar regressão de occlusion, resizing, takeover e background WebContentsView.

## Critérios de aceitação do conjunto

- Zero input despachado após `409 USER_CONTROL_ACTIVE`; zero replays automáticos após efeito incerto.
- Sem browser paralelo ou registro duplicate de TaskRun/BrowserTask.
- AX DOM parity e no stale cache em cenários SPA/iframe.
- Dados estruturais apenas na telemetry; zero canários de cookie/HTML/form/secret.
- E2E Windows real com app Hermes e exact-head CI verde documentados, não apenas mocks.
- Sem economia percentual afirmada sem benchmark de baseline/candidato comparável.
