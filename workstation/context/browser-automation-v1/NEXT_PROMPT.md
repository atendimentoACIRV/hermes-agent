# CONTINUE HERMES BROWSER AUTOMATION V1 — BAV-05 → BAV-12
**ORDEM DE EXECUÇÃO. NÃO REINICIE AUDITORIA. NÃO REFAÇA BAV01/BAV03 OU O GREEN BAV05. NÃO FAÇA MERGE NA MAIN.**
Use GitHub, Remote Desktop Commander, Superpowers e Community Agent Workflows quando disponíveis. Execute o máximo possível por sessão com RED→GREEN, evidências reais, documentação e o próximo prompt obrigatório.

## Localização e proteção
- Repositório: C:\Github\hermes-agent (checkout principal sujo com modificações paralelas; nunca editar/resetar/limpar).
- Worktree: C:\Github\hermes-agent\.worktrees\browser-automation-v1-20261012
- Branch: feat/hermes-browser-automation-v1-20261012
- Base original: a2b56db1bc9e0b5acf48d94fa86a9844a1005842 (origin/main). **Execute git rev-parse HEAD e git status -sb para descobrir o HEAD atual; nunca assuma o SHA base após os commits.**
- PR #82 Experience Compiler, independente, DRAFT; outra worktree Playwright C2C também independente. Não mover suas alterações.
- Gate H-079 Stage A upstream-first / CI exact-head / H-081/H-082 permanecem HOLD. Nenhum código produtivo BAV autorizado ou certificado neste checkpoint. A autorização de local-dev da outra branch não se transfere. Revise gate antes de mudar runtime e não declare qualificação sem evidência.

## Fonte da verdade
Leia primeiro AGENTS.md, workstation/AGENTS.md, workstation/context/README.md, workstation/context/UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md, e os arquivos PLAN.md, STATE.md, EVIDENCE.md, DECISIONS.md, METRICS.md, REFERENCE_MATRIX.md, NEXT_PROMPT.md desta pasta. Depois ROADMAP.md, engineering-journal/CURRENT.md e os arquivos de implementação selecionados.
Princípio: **automação funcional → procedimento persistente → aprendizado → otimização**. Nenhum segundo BrowserRuntime, owner, scheduler, registry, engine ou bypass CDP. Playwright connectOverCDP BAV01 só é compatibilidade experimental.

## O que já foi demonstrado (não repetir)
- BAV01: Playwright connectOverCDP em WebContentsView de perfil descartável; 1 efeito. Não há permissão para Playwright externo na produção.
- BAV03: singleton real getWorkstationBrowserRuntime + controller bearer-auth; mesmo procedimento Alpha/Beta, duas mutações verificadas, 12 chamadas ao controller e 0 LLM no harness.
- BAV05 anterior: ref stale recuperada por data-testid na fixture. JSON versão 1 inicialmente DISCOVERED.
- BAV05 desta continuação: teste RED de persistência falhou porque runner emitia só BAV03. Novo worker Python JSON-lines test-only exercita **ProceduralMemory.persist/load**, **RoutinePromotionService.validate/promote fixture-only** e **DeterministicRoutineRunner.run_matching**, usando apenas o controller autenticado existente. Em Electron real isolado: Alpha seed + Beta replay + Gamma replay, efeitos independentes 3/3; dois processos Python distintos recarregaram memória persistente. GREEN do node --test electron/workstation-browser-bav1-persistence.contract.test.cjs: 1 passed em ~42s; 0 chamadas ao modelo dentro do harness.
- Segurança demonstrada: ao inventar run_id 'bav-test-seed-Alpha', controller recusou 'BrowserTask run mismatch' HTTP 400 CAPABILITY_MISSING. Preservar 'bav-run' do fixture. Não tratar o teste como cross-TaskRun ou como validação de promoção produtiva.
- Laya em worker emite aviso de provenance por apontar para a vendorização no checkout principal; não tratar como runtime Laya qualificado.
- Arquivos test-only: apps/desktop/electron/workstation-browser-bav1-controller.runner.cjs (extensão), workstation-browser-bav1-memory.worker.py, workstation-browser-bav1-persistence.contract.test.cjs, os demais BAV01 e JSON fixture existentes.
- Logs .bav*.log ficam locais e jamais são commitados.

## Próxima ação obrigatória
1. Verificar git status/HEAD e H-079 Stage A real. Se continuar NÃO QUALIFICADO, permanecer em testes experimentais e documentação, sem alterar runtime produtivo; documentar bloqueio. Qualifique Stage A em lane própria se viável, sem misturar com BAV.
2. Primeiro RED: novo BrowserTask/TaskRun **realmente admitido**, em vez de trocar run_id arbitrariamente; depois selecionar ProceduralMemory promovida via run_matching com parâmetros distintos, autoridade válida, escopo e readback independente. Provar que browser lease revogado, drift, TaskRun antigo, cross-scope, restart e falta de prova falham fechados; especialmente evitar duplicação quando mutação é UNCERTAIN.
3. BAV04: checkpoint persistente e restauração pós-crash SEM repetir mutações de resultado incerto. Reutilizar DurableTaskStore/ExecutionJournal/reasoning_handoff; não criar segunda store. BAV05 ampliar somente após segurança.
4. BAV06: gravação opt-in redigida; BAV07 recuperação limitada por âncora sem bypass; BAV08 conectar PR #82 sem recriar compiler; BAV09 Trello somente em quadro de teste com autorização específica, leitura primeiro; BAV10 UI Electron; BAV11 benchmarks pareados medidos (latência/tokens/chamadas/efeito), BAV12 gates exact-head. BAV02 CDP nativo opcional, se necessário.

## Comandos confiáveis no Windows
Use PowerShell:
$w='C:\Github\hermes-agent\.worktrees\browser-automation-v1-20261012'
Set-Location $w
git status -sb; git rev-parse HEAD; git log -5 --oneline
$env:NODE_PATH='C:\Github\hermes-agent\node_modules;C:\Github\hermes-agent\apps\desktop\node_modules'
Set-Location "$w\apps\desktop"
node --test electron/workstation-browser-bav1-persistence.contract.test.cjs
node electron/workstation-browser-bav1-controller.runner.cjs
Set-Location $w
$env:PYTHONPATH='C:\Github\hermes-agent\.venv\Lib\site-packages;' + $w
uvx --offline pytest -q -o addopts='' workstation/tests/test_routines.py --tb=short

## Checkpoint obrigatório, recursivo
Atualize PLAN/STATE/EVIDENCE/DECISIONS/METRICS/NEXT_PROMPT e ROADMAP/journal de engenharia. Termine com testes realmente executados (PASS/FAIL/SKIP), HEAD completo verificado, branch/worktree/remote/PR, diff/dirty, gates H-079/H-081/H-082, próxima etapa/RED e incertezas. Faça commits pequenos sem segredos/logs/artefatos gerados. Push apenas na branch experimental apropriada, nunca main, e sem alegar release aprovado.
**OBRIGATORIAMENTE entregue ao usuário um NOVO PROMPT COMPLETO PRONTO PARA COPIAR/COLAR em toda interrupção. Cada prompt deverá incluir todas estas regras e obrigar a próxima sessão a gerar outro prompt, até BAV-12 integralmente qualificado.**
