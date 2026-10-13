# 09 — Exceção do mantenedor e execução local Playwright C2C

Data: 2026-10-12. **PASS_WITH_AUTHORIZATION somente para implementação local / NOT_RELEASE_QUALIFIED.**

## Exceção Stage A registrada como pendência

O mantenedor autorizou expressamente adiar o refresh upstream, a escolha de novo pin e a reconciliação das first-party seams **somente neste ciclo de desenvolvimento local**. NÃO autorizou promover a main sem H-079.2, CI exact-head, E2E e fechamento Stage A.

Base observada: downstream main `a2b56db1`, upstream local `835c3dd0`, pin ancestral `66605471`, 963 ahead/245 behind. Checkout principal com alterações UI de outros agentes preservado. Worktree isolado `C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012`, branch `feat/playwright-c2c-kits-20261012`, base `dbf3c44f1e`. Nenhum push ou merge.

## Entregas e lacunas honestas

| Kit | Estado | Implementação e evidências | Ainda falta |
|---|---|---|---|
| I01 — Electron harness | **PARTIAL / Native E2E PASS** | `workstation-browser-playwright-native.e2e.cjs` e `...runner.cjs` executam Chromium Electron 40 real do Hermes em perfil efêmero. Verificam WebContentsView único ligado a BrowserTask, DOM readback, overlay, disabled, anchor ambígua, takeover, SPA cache, renderer PID/RAM; executor externo limpa Windows profile após saída. | Restart em outro processo, navegação iframe/OOPIF, controller externo e Playwright como test client (não instalado). |
| I02 — Actionability | **PARTIAL / Native RED→GREEN** | `pointScript` recusa disabled/inert/ARIA-disabled, invisibilidade, pointer-events, fora da viewport, overlay/hit target e anchors com múltiplos resultados; `clickRef` e `typeRef` revalidam lease/epoch/URL após await. RED antes da correção de overlay e takeover, GREEN depois. | Estabilidade por rAF, semantic locators completos, deadlines canceláveis e feature flag avançada; guardas conservadoras atualmente ativas. |
| I03 — SPA cache | **IMPLEMENTADO LOCAL / GREEN** | `workstation-browser-dom-revision.ts` instala MutationObserver no isolated world 999, revision/generation, grava contadores apenas. Cache confere revisão antes/depois e a cada hit; falta de observer, iframes, open Shadow DOM ou DOM grande produzem bypass. Native Electron demonstrou cache miss em mudança de texto sem alterar childElementCount; 3 testes unitários PASS. | Medir overhead p50/p95, cobrir alterações dinâmicas em shadow/frames com política apropriada. |
| I04 — Frames/cancel | **PARTIAL** | Fence de epoch/URL/lease após resolução assíncrona. | FrameId/OOPIF/loaderId, waits com prazo monotônico e cancelamento completo, testes FRM. |
| I05 — Telemetria | **PARTIAL / GREEN** | `getOSProcessId` + `app.getAppMetrics` geram renderer PID e working-set bytes, separados de main CPU/RSS; whitelist `browser_observation.py` com canário de privacidade. Native RED de campo ausente e GREEN após implementação; Python 7/7 PASS. | CPU renderer por janela, verificador externo, tokens/custo por run, benchmark comparativo. |
| I06 — Durable exactly-once | **NOT STARTED** | Nenhuma nova fonte de autoridade ou store paralelo criada. | Journal canônico admission/effect/reconciliation, crash/replay failpoints, verificação externa. |

## Testes de engenharia observados

- Native Windows Electron: `cd apps/desktop && node electron/workstation-browser-playwright-native.runner.cjs` => `NATIVE_E2E_PASS`, exit code 0. Perfil temporário, dados sintéticos offline.
- Vitest Browser: `cd apps/desktop && node ../../node_modules/vitest/vitest.mjs run --config vitest.browser-native-audit.config.mjs --reporter=default` => 18 files / 159 tests PASS. Rodar novamente sobre HEAD final.
- Telemetry Python 7/7 em isolated unittest runner temporário, sem perfis reais.
- Helper TypeScript `workstation-browser-dom-revision.ts` compilou isoladamente. Typecheck full Electron deve ser registrado separadamente, não inferido dos testes.
- No productivity benchmark, no p50/p95 savings, no CI exact-head, no H-079 closure.

## Regras para próximo agente

1. Stage A upstream **PENDENTE AUTORIZADO**, não removido. Fechar antes de release, conforme `08-REMEDIACAO-STAGE-A.md`.
2. P0: I06 exactly-once owner journal, I04 iframe/OOPIF cancellation, I01 restart cross-process nativo.
3. P1: I02 stable rAF + semantic locator strictness e feature controls, I05 benchmark e verifier lineage.
4. Em todos os casos, preservar `409 USER_CONTROL_ACTIVE`, TaskRun/BrowserTask owner, zero retry cego e privacidade estrutural.
5. Não dizer `DONE` para I04/I05/I06; manter `NOT_RELEASE_QUALIFIED` até gates reais.

## Commits locais

- `396c96a1d4` — deferir Stage A com autorização expressa.
- `1997d1cbf4` — harness Windows Electron real, perfil temporário.
- `9f8b4740d8` — actionability e lease/document fencing.
- `93186e4b44` — invalidation SPA por MutationObserver.
- `e152603402` — renderer telemetry e extensão dos testes nativos.
