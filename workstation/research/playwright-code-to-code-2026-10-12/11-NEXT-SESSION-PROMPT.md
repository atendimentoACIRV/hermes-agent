# CONTINUE HERMES BROWSER C2C — P0-02 TERMINAL VERIFICATION → P0-04 → P1

**ORDEM DE IMPLEMENTAÇÃO DIRETA. NÃO RECOMECE A AUDITORIA CODE-TO-CODE. NÃO REFAÇA OS PATCHES APROVADOS.**

Retome o Hermes Work Browser Nativo diretamente no Windows com Remote Desktop Commander, GitHub, Superpowers e Community Agent Workflows conforme disponíveis. Use TDD RED→GREEN, regressões, native E2E e commits incrementais. Faça o máximo que puder nesta sessão sem interromper por planejamento; caso pare, gere novo prompt completo e recursivo.

## ESTADO REAL DA ÚLTIMA SESSÃO (REVALIDAR)

- Repositório: `C:\Github\hermes-agent`. Checkout principal **DIRTY por outros agentes**, principalmente Browser Hub e right rail; **não tocar**, não usar como worktree de implementação.
- Worktree isolado: `C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012`.
- Branch local: `feat/playwright-c2c-kits-20261012`.
- **Último commit de CÓDIGO verificado:** `b9addc487abc9852368d927cbcc25b588e8b108d`, mensagem `fix(browser): recover CDP pointer safely after uncertain click and takeover`. Commit documental posterior pode mudar HEAD; confira estado real.
- Stage A: `PENDING_WITH_MAINTAINER_AUTHORIZATION`. Mantenedor autorizou pular upstream sync, pin e seam reconciliation para desenvolvimento local. **NÃO EXECUTE STAGE A AGORA**. Ainda obrigatória para merge/release.
- Nenhum push/PR/merge na main autorizado; branch e commits somente locais. Release `NOT_RELEASE_QUALIFIED`.
- Checkpoint durável: `workstation/research/playwright-code-to-code-2026-10-12/10-IMPLEMENTATION-CONTINUITY.md`. Pesquisa Playwright já registrada 00–09.

### PRIMEIRO COMANDO, ANTES DE QUALQUER EDIÇÃO
`git -C "C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012" status --short --branch`
`git -C "C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012" rev-parse HEAD`
`git -C "C:\Github\hermes-agent\.worktrees\playwright-c2c-impl-20261012" log -8 --oneline`

Se houver novos commits ou dirty files desconhecidos, preservar e conciliar antes de editar; não sobrescrever terceiros.

## IMPLEMENTAÇÕES JÁ CONCLUÍDAS (NÃO REFAZER)

Commits herdados: `81a16ed00b` (admissão e replay), `7623bfbfcb` (Electron 2 processos crash E2E), `246477e4c0` (target disabled pré-scroll), `20acf1d2e9` (lock interprocessos + prevenção stale save), `da3ca49569` (fence before lazy restore, about:blank seguro, ID navegação/receipt), `3fd700a37f` documentação.

Nesta sessão:
1. `1c46a508d304b237bb617f9a56e6491bbcf81858` — P0-02: ACK causal por operação no `BrowserSessionStateFilePersistence`, só marcado quando um receipt de mesmo operation/task/tab/action/run foi persistido. NEW operation ID B no mesmo TaskRun após A perder receipt/crash é recusado `RECONCILIATION_REQUIRED` antes de lazy tab restore e dentro do lock do disco. ACK falso fornecido pelo chamador é recusado; controller mint de ID é estável entre admission e receipt. **Não equiparar ACK a VERIFIED**.
2. `3793c46a15b51ef4f0b05cb955a453727b9020fc` — Python shim `tools/browser_workstation.py` projeta disposições ACKNOWLEDGED/UNCERTAIN/RECONCILIATION_REQUIRED no `ExecutionJournal` EXISTENTE, com action/task/session/run/operation e `externally_verified=false`; sem HTML, conteúdo de formulário, URL, prompt, cookies ou segundo dispatcher. **Só projeção observacional após controller**, não terminal evidence.
3. `b9addc487abc9852368d927cbcc25b588e8b108d` — P0-03: CDP mousePressed timeout/release failure/takeover fail-closed. Um press nunca é automaticamente repetido; best-effort cleanup release, resultado `browser_input_state_uncertain`. Revalida lease humano, documentEpoch e URL entre os comandos. Três testes RED→GREEN.

### EVIDÊNCIA EXATA DO ÚLTIMO CÓDIGO
- `cd apps/desktop && node ../../node_modules/vitest/vitest.mjs run --config vitest.browser-native-audit.config.mjs --reporter=default` → **19 arquivos / 174 testes PASS**, exit 0.
- `cd apps/desktop && node electron/workstation-browser-playwright-native.runner.cjs` → `NATIVE_E2E_PASS`, exit 0.
- `cd apps/desktop && node electron/workstation-browser-crash-replay-native.runner.cjs` → `CRASH_REPLAY_NATIVE_PASS effects=1`, dois processos Electron, exit 0. Usa GET sintético local com efeito observável; NÃO é prova genérica de POST clique ou exactly-once externo.
- `cd apps/desktop && node electron/workstation-browser-admission-concurrency.runner.cjs` → anteriormente PASS, lock não mudou neste incremento.
- `C:\Github\hermes-agent\.venv\Scripts\python.exe -m unittest workstation.tests.test_browser_workstation_journal_projection -v` → **5 PASS**, exit 0 (aviso opcional Laya ausente, sem falha).
- `py -3 'C:\Users\Kevyn Lucas\AppData\Local\Temp\run_workstation_playwright_telemetry_unittest.py'` → **7 PASS**, exit 0.
- `py -3 -m compileall -q tools/browser_workstation.py workstation/tests/test_browser_workstation_journal_projection.py` → PASS.
- `node ../../node_modules/typescript/bin/tsc -p tsconfig.electron.json --noEmit --pretty false` → **FAIL** apenas diagnóstico conhecido `electron/git-review-ops.test.ts(124,5) TS2349 simple-git no call signatures`. Não misturar esse erro com código Browser sem prova comparativa.
- Ruff strict pre-commit do Python: **19 erros PREEXISTENTES** em `tools/browser_workstation.py`, confirmados independentemente com Ruff sobre `git show HEAD:tools/browser_workstation.py` (mesmos 19). Python commit `3793c46a15` foi feito com `LEFTHOOK=0` SOMENTE naquele commit, após testes e compilação; gate lint permanece BLOQUEADO. TypeScript commit usou hook normal. Não reescreva os 19 erros alheios sem tarefa separada, não alegue lint verde.

## PRIORIDADE P0-02 AINDA EM ABERTO — TERMINAL EXTERNAL VERIFICATION

**PRÓXIMO TESTE RED EXATO:** Operação A é localmente ACKNOWLEDGED, mas a pós-condição externa permanece INCONCLUSIVE/UNCERTAIN. O agente inicia operação B, com outro operation_id, no mesmo TaskRun. Hoje o ACK local libera o fence, embora não prove o efeito no destino. Implemente contrato explícito que só permite promover execução segura quando há evidência causal suficiente, sem bloquear leituras e sem auto-retry.

- Inspecione exclusivamente: `workstation/control_plane/dispatcher.py`, `workstation/control_plane/verification.py`, `workstation/journal.py`, `workstation/operational_kernel.py`, `tools/browser_workstation.py`, `apps/desktop/electron/workstation-browser-task.ts`, `workstation-browser-session-state.ts` e `workstation-browser-runtime.ts`.
- Distinga: ADMITTED, DISPATCHED, ACKNOWLEDGED, LOCALLY_OBSERVED, EXTERNALLY_VERIFIED, COMMITTED, UNCERTAIN, RECONCILIATION_REQUIRED. Não crie segundo journal, dispatcher, Browser nem autoridade.
- O `CertifiedDispatcher` Python mantém `DispatchRecord` principalmente em memória; `ExecutionJournal` já persiste eventos. A projeção de status implementada **não é certificação nem durable operation terminal state**. Criar vínculo tipado TaskRun/BrowserTask/opId, verificações independentes e reconciliação fail-closed com testes RED→GREEN e crash de processo.
- Não aceitar `result.success=true`, mero owner receipt ou payload `status:'verified'` do destino como `EXTERNALLY_VERIFIED`. Somente contrato de verificador canônico com evidência independente.
- Permitir explicitamente operação após **reconciliação comprovada**, não exigir intervenção indefinida sem procedimento seguro. Documentar idempotência não suportada por sites remotos.
- Cobrir `browser_creative_render`, `browser_creative_studio_open`, `browser_extension_open_options/load/remove` respeitando seus proprietários e autoridade, sem inventar BrowserTask para extensão.
- Hardening: lock órfão nunca auto-removido, disk write failures, duplicate A→B→A, framed navigation, capability policy, user takeover `409 USER_CONTROL_ACTIVE`, crash after dispatch before receipt.
- Benchmark do limite de 4096 admissions, rewrite+fsync por ação e efeitos p50/p95 antes de otimizar.

## DEPOIS DE P0-02, EXECUTE NA ORDEM

**P0-03 restante:** rAF geometry stability, hit target/overlay, ambiguidade estrita, teclado e clipboard parcial, cancelamento/timeouts e takeover real durante CDP. Os 3 testes recentes usam CDP mockado e não certificam takeover nativo no Windows.

**P0-04:** Frame identity/iframe navigation/OOPIF/context/loader/documentEpoch, fail-closed stale refs, deadlines monotônicos e cancelamento.

**P1-01:** Telemetria causal com TaskRun, sender PID CPU/RSS, CDP calls, snapshot bytes e provider reais; privacy canary SQLite/WAL.

**P1-02:** Benchmarks repetíveis offline, baseline/candidato sobre pin/configuração equivalentes, amostras n, p50/p95, variância, correctness, tokens/custo real.

**P1-03:** AXTree/CDP/cache SPA/delta otimizações SOMENTE com benchmarks de paridade.

**P1-04:** strict role/name/test ID, Shadow DOM, contentEditable/rich editors E2E.

**P1-05:** ExperienceCompiler evidence-gated; não promover globalmente capacidades com outcome incerto.

**QUAL:** regressões, tsc/lint conhecidos, native release E2E, CI exact-head após autorização de publicação, relatório e plano rollback. Stage A continua pulada autorizadamente DURANTE DEV; obrigatória antes de merge/release.

## INVARIANTES, PRIVACIDADE E SEGURANÇA
WorkstationBrowserRuntime único owner Electron WebContentsView; preservados TaskRun/BrowserTask/CertifiedDispatcher/OperationalKernel/ExperienceCompiler e lease humano `409 USER_CONTROL_ACTIVE`. Zero retry cego, segundo dispatcher/journal, segundo Browser de produção, uso de sites reais para testes, dados privados no journal, alterações no checkout principal dirty ou push/merge main. Só fixtures loopback/temporárias; nenhuma limpeza de arquivos de usuário desconhecidos.

## HANDOFF RECURSIVO OBRIGATÓRIO
Ao pausar ou terminar parcialmente, **não diga apenas "continue"**. Atualize `10-IMPLEMENTATION-CONTINUITY.md` e documentos `workstation/ROADMAP.md`, `context/CURRENT_STATE.md`, `context/engineering-journal/CURRENT.md`, `context/HERMES_WORKSTATION_INTELLIGENCE.md`, `workstation/SOURCE_MATRIX.md` com HEAD real, status Git, commits, testes RED/GREEN, gates e última função. **ENTREGUE um NOVO PROMPT COMPLETO pronto para copiar e colar**, com comandos iniciais, árvore/branch/HEAD/status, últimos resultados, primeira função/arquivo/teste, pendências, Stage A e todas as regras; exija que a IA seguinte repita esta regra recursivamente. Não alegar release sem Stage A/CI/qualificação final.

**COMECE AGORA PELO TESTE RED DE EXTERNAL VERIFICATION DO P0-02. SEM AUDITORIA DO ZERO.**
