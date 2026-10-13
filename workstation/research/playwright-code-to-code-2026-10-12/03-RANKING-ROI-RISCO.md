# 03 — Ranking por impacto, ROI investigável e risco

**Não existe estimativa comprovada de economia percentual, tokens ou velocidade.** “Impacto” é prioridade de engenharia baseada em lacuna reprodutível/gravidade; não é benefício quantificado. Escala: A (P0 / segurança ou validade), B (alta), C (diagnóstico/otimização). Esforço é qualitativo; todas as ações de runtime aguardam upstream-first/baseline e não foram implementadas nesta missão.

| Ordem | ID | Veredito | Impacto | Esforço | Risco | Motivo / dependência e entrega |
|---:|---|---|---|---|---|---|
| 1 | PW-01 | ADAPT | **A** | M | Médio | Actionability, rAF-stable e hit-target evitam clique errado e falha silenciosa; preservar lease, epoch, no-retry de mutações incertas |
| 2 | PW-05 | COPY-test/ADAPT | **A** | M | Baixo-médio | Playwright fornece fixture Electron/WebContentsView real para provar propriedade que 156 mocks não podem demonstrar |
| 3 | PW-06 | ADAPT | **A/B** | M | Médio | Invalidação de cache SPA por MutationObserver, cobrindo mudanças sem alteração de childElementCount |
| 4 | PW-03 | ADAPT | **A** | L | Alto | Frame/OOPIF/document identity, evitar execução em alvo errado; precisa lifecycle e E2E |
| 5 | PW-04 | ADAPT | **A/B** | M | Médio | Deadline monotônico, cancelamento, espera interrompível em lease/detach; sem retry após possível efeito |
| 6 | PW-13 | KEEP owner Hermes | **A** | L | Alto | Durable exactly-once do CertifiedDispatcher e BrowserTask, **não resolvido por Playwright**; exigir journal canônico e fault injection |
| 7 | PW-02 / PW-16 | ADAPT | **B** | L | Médio-alto | Semantic locators/strictness e escopo de frame com ambiguidades explicitamente recusadas |
| 8 | PW-09 | ADAPT sob flag | **B** | M/L | Alto | Reduzir custo AX per-node, apenas quando métrica CDP/paridade mostrar vantagem real |
| 9 | PW-08 | ADAPT | **B** | S/M | Baixo | Fases estruturais BEFORE/AFTER na telemetria, sem DOM bruto; cruzar ao verificador |
| 10 | PW-07 | INSPIRE/KEEP | **B** | M | Médio | Delta do Hermes já implementado; possível ganho em reutilizar árvores, mas risco de refs de histórico obsoletas |
| 11 | PW-10 | INSPIRE | **C** | M | Alto | Recorder pode fornecer sinais para Experience, mas actions do usuário não são recibos verificados |
| 12 | PW-11 | KEEP | **C** | S | Baixo | Aperfeiçoar contrato de schema e targetLocator já existente; não criar novo stack de ferramentas |
| 13 | PW-14 | HOLD | **C** | M | Alto | Browser Hub/right rail possui alterações não commitadas; depender de reconciliação, jamais sobrescrever |
| 14 | PW-12 | HOLD/REJECT | — | L | **Alto privacidade** | HAR/traces crus capturam material sensível; não usar como observabilidade default |
| 15 | PW-15 | REJECT | — | Muito alto | **Crítico** | Browser separado/segunda autoridade causa colisão de estado, cookie, leases e ownership |

## As três melhores ações após liberação do gate

1. **PW-01 — Proof-bound actionability:** antes do primeiro evento de input, conferir snapshot/elemento vivo, estabilidade por quadros, enabled, non-inert e que hit-test aponta para o target; abortar sob troca de documento/takeover. O verificador Hermes continua único responsável por marcar efeito.
2. **PW-05 — Native Electron E2E:** primeiro provar no app real, com dados e páginas sintéticas e perfil isolado, que 0 cliques são produzidos sob overlay/takeover e que recovery preserva BrowserTask. Playwright pode ser **instrumento de teste**, não browser de produção.
3. **PW-06 — SPA cache freshness:** usar contador de mutações/scope invalidation e fallback conservador. Validar com mesmo URL, mesmo childElementCount, atributo/texto alterado; sem caching de segredos.

Essas três são imediatamente *planejáveis/testáveis*; **não iniciar patch runtime** enquanto baseline upstream-first/exact-head estiver bloqueada.

## Cinco patch-kits priorizados — objetivos observáveis

| Kit | Contrato a implementar posteriormente | Arquivos Hermes | Regressão principal | Condição de rollback |
|---|---|---|---|---|
| PK-01 | Check de actionability e target identity read-only antes de click/type; guardas antes/apos await e no mutable replay | `workstation-browser-runtime.ts`; nova função puro-testável se estritamente necessário; `...-runtime-task.test.ts` | overlay, disabled, stable, takeover, typed effect | se ref semântica substituir ownership, desligar feature flag e manter path atual fail-closed |
| PK-02 | Test harness Electron externo instrumentando **a view da instância Hermes** em perfil temporário | `apps/desktop/electron/*test*`, config E2E, scripts H013 existentes | view é real, usuário assume controle, restart mantém identity | harness falha/usa browser paralelo -> não aceitar prova |
| PK-03 | Cache invalidation por MutationObserver + epoch com reset em reload/iframe, TTL/bypass seguro | `workstation-browser-runtime.ts`; `workstation-browser-extract-cache.ts` e testes | texto atributo muda com childElementCount fixo | bypass cache no mismatch em vez de servir resposta stale |
| PK-04 | Frame/document epoch específico para iframe/OOPIF; invalidar refs em attach/detach/navigate | `workstation-browser-snapshot.ts`; `...-runtime.ts`; `...-task.ts` (sem nova fonte da verdade) | clique no iframe antigo bloqueado | fallback DOM, estado UNCERTAIN sem retry |
| PK-05 | Cancelamento de espera e trace de fases estruturais ligados ao operationId | `workstation-browser-runtime.ts`; `workstation/telemetry/browser_observation.py`; testes | stop imediato durante takeover/renderer-gone | desabilitar otimização, manter fencing + telemetria não-autoritativa |

## Playwright versus as outras referências locais

| Referência | Código efetivamente localizado | Vantagem específica | Limitação para Hermes |
|---|---|---|---|
| **Playwright** | `client/locator.ts`; `server/dom.ts`; `server/frames.ts`; `injected/src/injectedScript.ts` | Semântica de actionability, hit-target, state machine de frame/cancelamento, suites Electron | Não contém owner de TaskRun/lease nem atestado de efeito de serviço externo |
| **Stagehand** | `packages/sdk-ts/src/stagehand.ts:133–164,232–269`; `packages/sdk-ts/src/batch.ts:36–76` | API declarativa `act/observe/extract` e batch de alto nível já voltados a planejamento por intenção | Não é substituto da verificação nativa mais baixa de target nem do BrowserTask. **LICENSE local atual é MIT**, divergindo de relatório histórico que afirmava Apache |
| **BrowserClaw** | `src/actions/batch.ts:30–96,350–356` e `src/ref-resolver.ts:143–146` | Batch serial e timeouts de interação explícitos em API; base já estudada para otimização Hermes | Não resolveu no Hermes a distinção ACK vs efeito; a proteção mais forte é a do owner Hermes/verified readback |
| **Agent Browser** | `cli/src/native/snapshot.rs:183,324+`; `cli/src/native/daemon.rs`; `cli/src/native/actions.rs` | Snapshot e CLI/daemon otimizados para automação desacoplada | Rust daemon seria um **segundo processo/browser backend** sem guarantees do Electron humano/agente; usar ideias de formato/benchmark, não clonar runtime |
| **Hermes** | `workstation-browser-task.ts`, `workstation-browser-batch-proof.ts`, `operational_kernel.py`, `telemetry/browser_observation.py` | Autoridade humana, TaskRun, receipts, effect proof, fail-stop e Experience Compiler são superiores para os invariantes do produto | Lacunas em actionability, iframe, SPA cache e native E2E dependem de evidência |

**Licença ao reutilizar:** fonte exata e copyright no inventário; nunca copiar código AGPL do BrowserOS. Apache-2.0/MIT não dispensam registro de NOTICE, fonte e dependências. Não foi incorporada uma linha de implementação Playwright neste audit.

## Critérios de decisão quantitativa que faltam medir

- Resultado correto primeiro: taxa de clique no alvo correto, operações bloqueadas no takeover, mutações incertas, readback cruzado.
- Depois desempenho: p50/p95 end-to-end por etapa e por run, CDP calls per snapshot, snapshot bytes/tokens, CPU/RSS de **processos identificados**.
- Eficiência econômica: custo real de provider só quando há `run_id` e usage ligado ao owner; em eventos passados 3.189/3.189 chamadas provider estão sem runId.
- Não comparar medianas de backends misturados nem declarar 70–85% de ganho sem amostra reproduzível e confidence interval.
