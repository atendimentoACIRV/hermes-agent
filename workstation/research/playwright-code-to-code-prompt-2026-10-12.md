# EXECUTE PLAYWRIGHT-C2C-01 — Auditoria de código fonte Playwright × Hermes Work Browser Nativo

Você é o engenheiro principal de auditoria comparativa code-to-code do Hermes Workstation. **Execute a investigação diretamente, usando Remote Desktop Commander, GitHub, Superpowers e community-agent-workflows.** Não faça auditoria superficial baseada em README nem implemente mudanças sem evidência e gates. Não pergunte por confirmação para ler código ou realizar experimentos seguros, somente para operações destrutivas, remotas ou de promoção quando for obrigatório.

## 0. Fontes e isolamento

- Repositório real: `C:\Github\hermes-agent`.
- **Nova referência local**: `C:\Github\hermes-agent\referências\02-Browser-Automacao-Web\playwright-main`. O pacote raiz se identifica como **Playwright 1.65.0-next** (snapshot local em 12/10/2026). `LICENSE` e `NOTICE`: Apache-2.0, incluindo avisos sobre derivações de Puppeteer. **O diretório não apresenta .git**; calcule SHA-256 dos arquivos relevantes e NÃO invente commit/pin de upstream. Verifique direitos, notices, dependências e patch provenance antes de propor `COPY`.
- Worktree isolado anterior: `C:\Github\hermes-agent\.worktrees\browser-native-evidence-20261012`; branch `audit/browser-native-evidence-20261012`. Valide HEAD/status/branches atuais; use outro worktree se necessário, **preservando as edições não commitadas de outros agentes no checkout principal**.
- Contexto canônico: `workstation/AGENTS.md`, `workstation/context/README.md`, `workstation/context/UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md`, `workstation/context/BROWSER_CODE_TO_CODE_DECISIONS_2026-10-10.md`, `workstation/research/browser-native-followup-2026-10-12.md`, `workstation/research/browser-native-next-2026-10-12.md`, `workstation/research/hermes-native-browser-telemetry-2026-10-12.md`. Reutilize a auditoria anterior em `workstation/research/browser-code-to-code-2026-10-10/` sem repeti-la.
- Owners Hermes: `apps/desktop/electron/workstation-browser-runtime.ts`, `workstation-browser-snapshot.ts`, `workstation-browser-batch.ts`, `workstation-browser-batch-proof.ts`, `workstation-browser-task.ts`, `workstation-browser-extract-cache.ts`, `workstation-browser-snapshot-diff.ts`; ponte `tools/browser_workstation.py`; kernel/verifier/TaskRun/authority; `workstation/telemetry/browser_observation.py`.

## 1. Auditoria profunda (fonte → símbolo → destino)

Inspecione primeiro estes arquivos reais do checkout Playwright; recupere seus símbolos/linhas exatos e dependências:
1. `packages/playwright-core/src/client/locator.ts`: `Locator`, `FrameLocator`, selectors semânticos, strictness, retries, auto-wait e composição de ações.
2. `packages/playwright-core/src/server/frames.ts`: `FrameManager`, `Frame`, `waitForSelector`, `retryWithProgressAndTimeouts`, navegação, frames aninhados, same-URL SPA, document changes, actionability.
3. `packages/playwright-core/src/server/progress.ts`: `ProgressController`, timeouts/cancelamento, deadlines e diagnóstico; comparar com lease/timeout/cancelamento canônico do Hermes.
4. `packages/playwright-core/src/server/selectors.ts` + localização REAL dos injected scripts: resolução DOM/Shadow DOM/iframe e staleness; não assumir caminho antigo de arquivo.
5. `packages/playwright-core/src/server/chromium/crPage.ts`: lifecycle/ CDP, page/frame identity, target attach/detach, crash e recuperação.
6. `packages/playwright-core/src/server/trace/recorder/tracing.ts`, `snapshotter.ts`, `snapshotterInjected.ts`, `har/harRecorder.ts`: captura eficiente e diferencial, provas e telemetria não invasiva, autoria de traces, CPU/memória/tempo se disponíveis.
7. `packages/playwright-core/src/server/recorder.ts`, `tools/backend/snapshot.ts`: action recording, replay seguro, geração de procedures e integração com Experience Compiler sem conceder autoridade.
8. `tests/electron/electron-webcontentsview.spec.ts`, `electron-tracing.spec.ts` e `tests/electron/playwright.config.ts`: padrões executáveis para Browser Nativo/Workstation e E2E local com mock sites.
9. Procure também timeouts, polling, CPU savings, message serialization, screenshot/performance, test isolation, DOM snapshot e APIs de `expect` realmente implementadas.

## 2. Problemas Hermes a confrontar, em ordem

- **P0:** reentrada/exactly-once durable (testes de retry, crash, idempotência, receipt perdido e ação executada sem readback). Não confunda actionability/ACK do Playwright com VERIFICAÇÃO DE EFEITO EXTERNO.
- **P0:** precisão de ações em SPA/Shadow DOM/iframes/document replacement, coordenadas obsoletas, click interception, disabled/visible/stable, ARIA/locator. Inspecione equivalência sem reintroduzir browser-process paralelo.
- **P0:** E2E Electron nativo em Windows. Reaproveite padrões/fixtures/test harness do próprio Playwright com o `WebContentsView` **pertencente ao Hermes**, não com um browser próprio do Playwright. Preservar sessão autenticada e profile isolation.
- **P1:** custo de AXTree (`DOM.resolveNode` + `Runtime.callFunctionOn` por nó), compensação cache/selectors, ref IDs persistentes, observação via injected world, fallback DOM; validar benefícios por benchmark.
- **P1:** cache de extração que envelhece em SPA com mesmo childElementCount, Shadow DOM, editors, MutationObserver e document epochs; read-after-write.
- **P1:** waits/synchronization: substituir polling redundante e sleeps fixos por readiness baseada em evidência, timeouts e cancelamento; comparar código real, não slogans.
- **P1:** tracing/telemetria p50/p95, CPU/RSS **por processo identificado**, chamadas CDP, caracteres de snapshot/delta, bytes efetivamente model-facing, duração até efeito *realmente verificado*, custo provider+tool por TaskRun. Reutilize `TelemetryEventV1`/SQLite reconstruível. **Nenhum dado bruto** de URL/query, DOM, prompt, token, cookie, formulário, dados pessoais.
- **P1 UX:** Browser Hub/right rail com logs, progress, intervenção humana, ownership e recuperação; arquivos UI principais possuem alterações não commitadas de outros agentes; faça reconciliação, não sobrescreva.

## 3. Para CADA oportunidade

Entregue uma ficha com **repositório/caminho/símbolo/linhas e SHA-256**, comportamento encontrado e teste upstream que o demonstra; equivalente Hermes atual (caminho/símbolo/linhas); discrepância objetiva e problema real/hipótese; decisão **COPY / ADAPT / INSPIRE / KEEP / REJECT / HOLD**; grau de dependência, licença/NOTICE/atribuição, mudanças mínimas e testes RED→GREEN; impacto esperado separado de medição e risco de regressão; se o código pode coexistir com Electron e `BrowserTask`; rollback. Use diff por contrato e chamadas, nunca apenas comparação de nomes.

Priorize reaproveitamento **de algoritmos e testes**, não arquiteturas que criem Browser separado, segundo dispatcher, outra árvore de sessões, credenciais compartilhadas ou novo owner de autoridade. Preserve `409 USER_CONTROL_ACTIVE`, política, TaskRun/runId e revisão/document identity, fail-closed, `OperationalKernel` e `ExperienceCompiler`. Playwright Apache 2.0 não isenta revisão de third-party notices, dependências e LICENSE dos arquivos.

## 4. Provas e ranking

- Crie uma matriz comparativa completa com evidências dos dois códigos. As 10 melhores melhorias deverão ser ordenadas por **correção de falha real > segurança/authority > latência/custo verificável > esforço > risco de manutenção/licença**.
- Para até cinco candidatos, monte **patch-kits reversíveis e planos de teste**, sem transplantar código ainda. Incluir benchmark reproduzível de antes/depois com mocks e E2E futuro, métricas p50/p95 e denominadores. Não inventar ganhos.
- Auditar `tests/electron` e dizer quais fixtures e técnicas podem ser copiadas/adaptadas para exercitar **o mesmo Electron já presente no Hermes**, sem bloquear as runs do usuário nem modificar sites reais.
- Identificar explicitamente quando `Playwright` oferece algo melhor que `Stagehand`, `BrowserClaw`, `Agent Browser` ou o código Hermes e quando **não** oferece.
- Use GitHub somente para comparar SHA/source quando possível; a fonte da auditoria é este snapshot local, não uma versão remota presumida.
- Não declarar o gate H-079/CI/E2E fechado se estiver pendente. `BrowserOS` permanece AGPL: padrão/inspiração apenas, não copiar código.

## 5. Saída obrigatória

Gerar em `workstation/research/playwright-code-to-code-YYYY-MM-DD/`: `00-RESUMO-EXECUTIVO.md`, `01-INVENTARIO-E-LICENCAS.md`, `02-MATRIZ-SIMBOLO-A-SIMBOLO.md`, `03-RANKING-ROI-RISCO.md`, `04-TESTES-E-BENCHMARKS.md`, `05-PLANO-IMPLEMENTACAO.md`, `06-PROMPT-IMPLEMENTADOR.md` e patch-kits estritamente necessários. Atualize ROADMAP/engineering journal/Intelligence somente se as descobertas forem suportadas por código.

Ao final, entregue: top 10 priorizado, **3 ações com maior ROI agora**, o que é seguro copiar literalmente (com avisos/licença), o que exige adaptação, o que rejeitar, arquivos específicos Hermes que mudariam, gates abertos e prompt de implementação pronto. **Missão de auditoria**, não de merge/instalação: não alterar código runtime ou main sem qualificação/ordem posterior.
