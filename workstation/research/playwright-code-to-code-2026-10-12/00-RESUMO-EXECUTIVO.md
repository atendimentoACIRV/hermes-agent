# 00 — RESUMO EXECUTIVO — PLAYWRIGHT-C2C-01

**GATE 0 EXECUTADO EM 12/10:** **BLOCKED / NOT_RELEASE_QUALIFIED**; não foi iniciada implementação C2C-I01..I06 por ausência de baseline upstream-first e exact-head CI comprovados. Ver [07-GATE-0-BLOCKED-2026-10-12.md](07-GATE-0-BLOCKED-2026-10-12.md) e [08-REMEDIACAO-STAGE-A.md](08-REMEDIACAO-STAGE-A.md).

**Data:** 12/10/2026. **Missão:** auditoria comparativa de código-fonte, documentação técnica e handoff de implementação, **sem modificação de runtime, sem push e sem merge**.

**Origem:** `C:\Github\hermes-agent\referências\02-Browser-Automacao-Web\playwright-main`. O `package.json` diz **1.65.0-next**, `LICENSE` informa **Apache-2.0** e `NOTICE` inclui código derivado de Puppeteer. A cópia local não contém `.git`; os hashes SHA-256 integrais por arquivo estão em `01-INVENTARIO-E-LICENCAS.md`. **Nunca declarar SHA upstream para este snapshot local.**

**Destino:** Hermes Work Browser Nativo em `audit/browser-native-evidence-20261012@c39739a187`, inspecionado sem tocar no checkout principal com trabalho UI de outros agentes. Esta baseline é **NOT_RELEASE_QUALIFIED**; H-079/upstream-first, E2E Electron Windows e exact-head CI permanecem pendentes. Uma conferência pontual do `workstation-browser-runtime.ts` com GitHub main foi realizada, mas não substitui freeze/qualification do main atual.

## Veredito comparativo

**Playwright demonstra vantagem localizada** em checks de ação (visibilidade, estabilidade por rAF, enabled, hit-target), strict locators/ARIA, frame/OOPIF lifecycle, timeout/cancelamento não-trivial e fixtures Electron/WebContentsView. **Hermes demonstra contratos distintos que NÃO devem ser substituídos:** TaskRun e BrowserTask canônicos, `409 USER_CONTROL_ACTIVE`, owner receipts, readback fail-stop, prevenção parcial de replay, `OperationalKernel` e `ExperienceCompiler`. Playwright não traz exactly-once de efeitos externos.

Foram documentadas **16 oportunidades** (PW-01..PW-16): 9 ADAPT centrais, 1 COPY restrito ao test harness, 2 INSPIRE, 3 KEEP/REJECT e HOLDs para HAR/UI/novos runtimes, com casos de teste e arquivo de destino. Classificações podem se sobrepor conforme a granularidade e não devem ser somadas como subtotais exclusivos. As cinco melhores propostas possuem patch-kits/rollback descritos nos arquivos 03–05.

## Três ações de maior impacto, em ordem

1. **PW-01 — Actionability segura antes de ações.** Usar `server/dom.ts:330–399,435–479` e `packages/injected/src/injectedScript.ts:699–759,1037–1205` como referência de semântica, adaptando para `workstation-browser-runtime.ts::resolvePoint/clickRef/typeRef`. Não reexecutar mutações após resultado desconhecido; preservar lease, runId e documentEpoch.
2. **PW-05 — E2E real em Electron/WebContentsView.** Adaptar `tests/electron/electron-webcontentsview.spec.ts:19–33` e `electronTest.ts:18–121` para testar o app Hermes e o WebContentsView real no Windows, com perfil isolado e websites sintéticos. Playwright é **driver de teste, não browser substituto**.
3. **PW-06 — Cache SPA mutation-aware.** Adaptar `server/trace/recorder/snapshotterInjected.ts:76–156,367–433` para invalidar `workstation-browser-extract-cache.ts` quando mudar texto/atributo sem modificar URL nem childElementCount. Cache sem observação segura faz bypass.

**P0 paralelo e indispensável, mas não reaproveitamento Playwright:** exactly-once durável precisa de journal/admission/reconciliation no owner Hermes, além do fencing atual baseado no último receipt. Não é solucionado por retry de locator.

## Copy × Adapt × Inspire × Reject

| Veredito | Candidato concreto | Regra |
|---|---|---|
| **COPY restrito** | Trechos pequenos de fixtures, `expect.poll` e setup/teardown de teste Electron (Apache-2.0) | Só após revisão de LICENSE/NOTICE/imports e no **harness**. Zero código Playwright copiado nesta auditoria |
| **ADAPT** | actionability, locator strictness, frame lifecycle, cancelable wait, SPA revision e tracing semântico | Reescrever para API/autoridade Hermes, com testes e licenciamento conferidos |
| **INSPIRE** | snapshot históricos/delta e recorder do Playwright | Extrair mecanismo; não guardar DOM/HTML cru e não tratar ações gravadas como outcomes verificados |
| **KEEP** | BrowserTask/TaskRun/lease/receipt/readback, snapshot diff e tools Browser do Hermes | Evitar implementação duplicada |
| **HOLD** | HAR, traces completos, controle de Browser Hub/right rail ainda em andamento | Privacy review ou reconciliação de owner e testes nativos |
| **REJECT** | Browser alternativo Playwright, novo daemon/broker, timeout->retry de escrita desconhecida, cópia de BrowserOS AGPL | Quebrariam autoridade/sessão/consentimento ou obrigações de licença |

## Comparação com três referências adjacentes

- **Stagehand:** `packages/sdk-ts/src/stagehand.ts:133–164` e `batch.ts` apresentam `act/observe/extract` e batch declarativo; mais aplicável à interação de alto nível baseada em intenção que à mecânica de hit-target. O `LICENSE` **atual local é MIT**, diverge de um relatório anterior que chamava Apache-2.0: foi priorizada a licença lida agora.
- **BrowserClaw:** `src/actions/batch.ts` e `src/ref-resolver.ts` mostram batch e timeout; Hermes já tem batch serial mais truth of effect, enquanto Playwright é referência mais específica para actionability/cancelamento.
- **Agent Browser:** `cli/src/native/snapshot.rs` e `daemon.rs` têm estratégias de snapshot/CLI, mas clonar o daemon Rust introduziria backend separado incompatível com o dono Electron. O LICENSE local é Apache-2.0.

## Índice de entregas

| Documento | Conteúdo |
|---|---|
| [01-INVENTARIO-E-LICENCAS.md](01-INVENTARIO-E-LICENCAS.md) | Fontes, versões, hashes SHA-256 integrais, NOTICE e decisão de direitos |
| [02-MATRIZ-SIMBOLO-A-SIMBOLO.md](02-MATRIZ-SIMBOLO-A-SIMBOLO.md) | 16 evidências Playwright→Hermes com símbolo/linhas, classificação, risco e teste |
| [03-RANKING-ROI-RISCO.md](03-RANKING-ROI-RISCO.md) | 15 itens ranqueados, top 3, cinco patch-kits, comparação de outras referências |
| [04-TESTES-E-BENCHMARKS.md](04-TESTES-E-BENCHMARKS.md) | RED/GREEN, E2E real, benchmarks por owner, privacidade e rollback |
| [05-PLANO-IMPLEMENTACAO.md](05-PLANO-IMPLEMENTACAO.md) | Stage A, sequência por gate, cinco patch-kits, tradeoffs |
| [06-PROMPT-IMPLEMENTADOR.md](06-PROMPT-IMPLEMENTADOR.md) | Ordem detalhada para próxima IA implementar quando os gates permitirem |

## O que NÃO foi comprovado

Nenhum patch de runtime nem aplicação Playwright sobre o Hermes foi realizado; nenhuma medição de ganho p50/p95/CPU/tokens no Chromium real, nenhum native E2E Windows, nenhuma CI exact-head ou demonstração de exactly-once durável. A auditoria compara **código e testes disponíveis**, não certifica qualidade em produção. Sem baseline qualificado, o resultado correto é **AUDITORIA ENTREGUE / IMPLEMENTAÇÃO BLOQUEADA POR GATES**, não READY_FOR_MAIN.
