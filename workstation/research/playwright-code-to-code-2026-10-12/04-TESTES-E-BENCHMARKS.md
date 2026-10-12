# 04 — Testes, falsificação e benchmarks

**Status: PROPOSTA, NÃO EXECUTADO E2E WINDOWS.** A baseline auditada já tinha 156 testes mock Browser/Electron e 7 testes isolados de telemetria, mas esses testes não substituem o Chromium real. Nenhuma economia percentual ou nova latência Playwright foi medida.

## Harness Playwright que realmente existe

- `tests/electron/electron-webcontentsview.spec.ts:19–33` usa `launchElectronApp`, `firstWindow`, `expect.poll` e verifica 3 WebContentsViews; o teste requer Electron >=30.
- `tests/electron/electron-tracing.spec.ts:23–53` executa navegação/clique e confere traces; não copiar traces com HTML/cookies para telemetria Hermes.
- `tests/electron/electronTest.ts:18–121` cria `userDataDir` separado, limpa cookies e encerra aplicativos.
- Adaptar esses padrões para a instância **do Hermes** em perfil temporário, não instalar Playwright como backend de browser.

## Testes RED→GREEN por oportunidade

| ID | Cenário real/sintético | RED no comportamento não protegido | GREEN necessário | Owner |
|---|---|---|---|---|
| ACT-01 | Botão visível mas disabled/inert | click enviado | nenhum dispatch; `TARGET_NOT_ACTIONABLE` | Browser runtime |
| ACT-02 | Retângulo do alvo se move entre rAFs | clique na coordenada antiga | espera bounded ou recusa sem input | runtime/Electron |
| ACT-03 | Overlay intercepta hit-test | overlay recebe click | `REJECT_INTERCEPTED`, nenhum input no overlay | runtime/Electron |
| ACT-04 | humano assume enquanto aguarda | interação após takeover | `409 USER_CONTROL_ACTIVE`, 0 efeitos | authority/TaskRun |
| ACT-05 | ACK em botão sem toggle | falso VERIFIED | UNCERTAIN até verificador independente | batch proof |
| FRM-01 | iframe troca documento mas URL parent é igual | referência antiga aceita | STALE_REF, novo snapshot deliberado | frame/session |
| FRM-02 | OOPIF detach/re-attach/crash | handles antigos seguem | erro tipado e recuperação sem reroute | Electron |
| SPA-01 | texto muda sem mudar childElementCount | cache stale hit | revision invalida cache | extract cache |
| SPA-02 | attributes/text/Shadow DOM mudam assincronamente | projeção antiga | reobservação ou bypass conservador | extract cache |
| SPA-03 | observador não disponível ou desconectado | cache “válido” sem prova | desabilita cache e mantém sucesso correto | extract cache |
| LAT-01 | renderer fechado durante wait | espera vence timeout arbitrário | cancela imediatamente; 0 replay | progress owner |
| TRACE-01 | fases attempt/dispatch/ack/readback por operation | eventos sem join | correlaciona TaskRun sem falsificar outcome | telemetry |
| TRACE-02 | cookie/form/HTML/query secret em fixture | segredo persistido | canário ausente nos bytes SQLite/arquivos | privacy |
| REPLAY-01 | crash após efeito e antes de receipt | write duplicado | journal owner bloqueia replay incerto | CertifiedDispatcher |
| REPLAY-02 | operação A deixa de ser lastReceipt após B | replay A permitido | journal identifica A e recusa | BrowserTask |
| E2E-01 | Electron Hermes real, 2 views, restart, takeover | mocks não provam | PID/view/owner corretos e sem browser extra | E2E native |

**Exactly-once:** a retry logic do Playwright não fecha a janela entre efeito externo e receipt persistido. Exigir fault injection depois de dispatch, antes do recibo, com decisão de reconciliação explícita. Nenhum teste de playwright actionability substitui owner verifier.

## Medição controlada após liberação do gate

A/B com baseline e target do **mesmo upstream pin qualificado**, mesma GPU/CPU, Electron, rede loopback, datasets sintéticos e número de tabs. Propor no mínimo 30 repetições independentes por cenário para exploração e escolher tamanho amostral formal antes de afirmar melhora. Gravar build SHA e versão.

| Medida | Fonte exata | Proibição |
|---|---|---|
| latência p50/p95 por action e stage | boundary Python + Electron + owner verification | não chamar controller latency de end-user latency |
| chamadas CDP por método/nó | instrumentação de `this.cdp` | não extrapolar custos em tokens |
| CPU/RAM MAIN | `process.cpuUsage` / RSS main PID | não atribuir a renderer |
| CPU/RAM renderer | processo Electron renderer identificado pelo PID | não inventar se ausente |
| caracteres e bytes snapshot/delta | serialização model-facing | bytes não são tokens |
| token input/output/custo | provider usage owner com `run_id` e preço verificado | desconhecido não é zero |
| cache hit/miss e stale hit | `cached:true/false` + revision de documento | hit sem validade não é sucesso |
| effect truth | receipt + semantically independent verifier | ACK/local DOM não prova servidor remoto |

Histórico observado antes da implantação desta coleta: 5.108 eventos, 84 ferramentas browser, p50~49,6 ms e p95~8065 ms (BACKENDS MISTURADOS), 3.189 provider calls sem runId. Não usar como performance baseline nativa.

## Comandos e evidências exigidos

Na worktree qualificada: `cd apps/desktop && node ../../node_modules/vitest/vitest.mjs run --config vitest.browser-native-audit.config.mjs`; TypeScript Electron com dependencies reais; Python suites e privacy canaries; E2E Windows Electron; H013/H-079; CI exact-head. Registrar SHA, logs, sucesso e falha por caso, número de samples, incerteza e reversão. Sem qualificação não promover.

## Rollback

Desligar flags experimentais e degradar para leitura segura, fallback DOM e cache bypass. Nunca trocar silenciosamente para outro navegador, retentar mutação incerta ou diminuir autoridade.
