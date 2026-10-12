# CONTINUE HERMES BROWSER AUTOMATION V1 — PR #85 / BAV04 HOLD → BAV12

**ORDEN DE EXECUÇÃO DIRETA. NÃO RECOMEÇAR AUDITORIAS NEM BAV01/BAV03/BAV05/BAV04 EXPERIMENTAL. NÃO FAZER MERGE NA MAIN.**
Use GitHub, Remote Desktop Commander, Superpowers e Community Agent Workflows. TDD RED→GREEN, testes reais, gates de autoridade, commits pequenos, push na branch da PR apenas e handoff recursivo.

## Baseline exata e isolamento
- Repo: `kevynlucasprofissional-stack/hermes-agent`; original: `C:\Github\hermes-agent` (checkout principal com trabalho paralelo; NÃO editar, limpar, resetar ou sobrescrever).
- Worktree BAV: `C:\Github\hermes-agent\.worktrees\browser-automation-v1-20261012`
- Branch: `feat/hermes-browser-automation-v1-20261012`
- PR #85: https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/85 — OPEN DRAFT, sem merge.
- Base `origin/main@a2b56db1bc9e0b5acf48d94fa86a9844a1005842`.
- HEAD antes de documentação: `5448f889fe94af43c0534b26a0243364be1a078e`, código test-only de BAV04. **O HEAD desta documentação pode ser posterior: verifique git rev-parse HEAD, status -sb, git log e branch remota ao iniciar**.
- Scratch logs locais `.bav*.log`: preservar, nunca adicionar. Não incluir secrets ou dogfood.
- Paralelas: PR #82 Experience Compiler + C2C Playwright worktree separada. Não cherry-pick indiscriminado, não editar outras worktrees.

## Leia primeiro
`AGENTS.md`, `workstation/AGENTS.md`, `workstation/context/README.md`, `workstation/context/UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md`, e pasta `workstation/context/browser-automation-v1/`: `PLAN.md`, `STATE.md`, `EVIDENCE.md`, `DECISIONS.md`, `REFERENCE_MATRIX.md`, `METRICS.md`, `NEXT_PROMPT.md`. Depois `workstation/ROADMAP.md`, `workstation/context/engineering-journal/CURRENT.md` e `workstation/context/ID_DISAMBIGUATION.md`.

## Evidências aprovadas (não repetir do zero)
BAV01: test-only Playwright CDP ↔ Electron WebContentsView em perfil descartável: 1 efeito; **CDP externo não autorizado na produção**.
BAV03: autenticado controller + singleton native Browser, Alpha/Beta, 12 controller calls, 2 efeitos independentes, 0 chamadas ao modelo pelo harness.
BAV05: Procedure JSON v1, data-testid para ref stale; ProceduralMemory + RoutinePromotionService (somente fixture) + DeterministicRoutineRunner.run_matching, Alpha seed e Beta/Gamma replay com duas recargas de memória por novos processos Python, 3 efeitos, 0 model calls harness.
BAV04 desta sessão: **test-only crash/reconcile GREEN**. RED Python por ausência de recovery fence; RED Node emitia só marcador BAV03; RED de contador baseline recusou argumento. Implementou `workstation/tests/bav04_experimental_recovery.py` (NÃO é código de produção), teste `test_bav04_experimental_recovery.py` e runner Electron `workstation-browser-bav1-recovery.contract.test.cjs`, estendendo worker/runner BAV05 test-only. Usa ExecutionJournal canônico (mutation pending, acceptance/fsync) + ArtifactStore + DeterministicRoutineRunner.resume_ref. No Electron WebContentsView descartável: Alpha seed, Beta click com efeito no servidor, Python `os._exit(37)` antes da persistência de readback, novo worker reconciliou via snapshot + contador de efeitos e prosseguiu sem segundo click. 2 efeitos totais; 0 chamadas LLM dentro do harness.
Verificações: `test_bav04_experimental_recovery.py` 11/11 PASS; `test_bav04... + test_routines.py` 13/13; adicionais test_memory_replay/test_memory/test_kanban_journal/test_artifacts_and_verbosity 16/16; Node recovery+persistence 2/2; Ruff F,UP, pre-commit, Node --check, py_compile, diff check PASS.
**NÃO alegar** Electron main crash; nova TaskRun/admissão/lease produtivos; release CI; economia real, token cost; Laya provada. Admissão de recuperação no fixture é dicionário sintético e mesma BrowserTask original, jamais substitui token autenticado. Não fazer mutação em Trello real sem autorização específica.

## Gate H-079 — bloquear alteração produtiva
`ls-remote upstream refs/heads/main`: `9f63a6fe5cfe39adc7a8f1936fbdcffffbec1d74` observado em 12/10; cached upstream/main estava em `835c3dd038d903182a66ecc45e34bf5e0de65f00`. `ls-remote origin refs/heads/main`: `a2b56db1bc9e0b5acf48d94fa86a9844a1005842`; merge-base cacheado `66605471e9f0b0832abbefaf625ce08e948ca540`. CI main exact-head não demonstrado: GitHub retornou statuses=[] e PR workflow_runs=[] (isto **NÃO é verde**). Status Stage A QUALIFIED não existe nesta branch; HOLD.
Sem baseline H-079 Stage A qualificada, **não modificar runtime produtivo**. Se possível, qualificar Stage A em lane separada e com critérios completos (pin upstream, merge real, seams classificados, CI verde). Documente antes de tocar produção. Não usar permissão local-dev de outras branches como waiver. Não misturar upstream merge e feature.

## Próximo RED prioritário — Autoridade real/restart BAV04
Examinar diretamente as fronteiras de produção:
- `workstation/routines.py::DeterministicRoutineRunner.run` / `resume_ref`
- `workstation/journal.py::ExecutionJournal`
- `workstation/artifacts.py::ArtifactStore`
- `workstation/reasoning_handoff.py`
- `workstation/run_adoption.py` / `workstation/task_compiler.py`
- `apps/desktop/electron/workstation-browser-runtime.ts`
- `apps/desktop/electron/workstation-browser-batch.ts`
- `tools/browser_workstation.py`
- BrowserTask/TaskRun lease/owner supervisor

Primeiro teste RED deve criar **nova BrowserTask/TaskRun real, autenticada e admitida**, não forjar `run_id`, e tentar recuperar uma mutação `UNCERTAIN` após restart. Sem autoridade válida o replay deve ser bloqueado. Com autoridade renovada, prova externa independente e checkpoint íntegro/escopado, retomar sem duplicar efeitos; registrar cada dispatch antes do efeito e confirmar depois por readback. Verificar revogação, outro owner, outro run/session, outro host/scope, versão/fingerprint, drift DOM, arquivo de journal corrompido, falta de verificador, ACK sem efeito, crash Electron main (não somente worker), e retomada sob SHADOW/DIRECT. Reusar os owners e stores existentes; não criar um segundo BrowserRuntime/scheduler/ProcedureDB/engine ou bypass de lease/CDP. Se Stage A continuar bloqueado, faça testes e documentação de contrato, não mudança produtiva.

## Ordem restante
1. BAV04: verdadeiro recovery com autoridade/lease/restart; apenas quando H-079 qualificado.
2. BAV05: promoção canônica, reutilização entre TaskRuns distintas com readback externo e real admissão.
3. BAV06: gravação opt-in com redaction e sem persistir segredos.
4. BAV07: recuperação bounded de âncoras e drift, sem auto-bypass.
5. BAV08: integração à frente existente Experience Compiler PR #82, sem duplicar compilador.
6. BAV09: Trello somente test board expressamente autorizado; leitura primeiro, mutação após aprovação.
7. BAV10: UI Electron visualização, parametrização, revisão e handoff.
8. BAV11: benchmarks pareados com chamadas LLM, tokens, custo e latência por efeito verificado.
9. BAV12: gates H079/H081/H082, regressões, segurança, dogfood, CI exact-head e release.

## Comandos iniciais (PowerShell)
```powershell
$w='C:\Github\hermes-agent\.worktrees\browser-automation-v1-20261012'
Set-Location $w
git status -sb
git rev-parse HEAD
git log -5 --oneline
$env:PYTHONPATH='C:\Github\hermes-agent\.venv\Lib\site-packages;' + $w
uvx --offline pytest -q -o addopts='' workstation/tests/test_bav04_experimental_recovery.py workstation/tests/test_routines.py --tb=short
$env:NODE_PATH='C:\Github\hermes-agent\node_modules;C:\Github\hermes-agent\apps\desktop\node_modules'
Set-Location "$w\apps\desktop"
node --test electron/workstation-browser-bav1-recovery.contract.test.cjs electron/workstation-browser-bav1-persistence.contract.test.cjs
```

## Finalização obrigatória e recursiva
Execute o máximo possível nesta sessão, TDD RED→GREEN, teste nativo e negativo, lint/hooks/CI quando disponível. Mantenha `PLAN/STATE/EVIDENCE/DECISIONS/METRICS/REFERENCE_MATRIX/NEXT_PROMPT`, `ROADMAP.md` e `engineering-journal/CURRENT.md` sincronizados. Commits pequenos e push apenas na branch PR #85 (sem main merge, sem arquivos .bav ou dados sensíveis). Relate HEAD SHA completo efetivamente verificado, remote/PR, files dirty, PASS/FAIL/SKIP/NOT RUN, H079/081/082, próxima função + RED exato, risco remanescente. **AO ENCERRAR SEMPRE DEVOLVA UM NOVO PROMPT COMPLETO, PRONTO PARA COPIAR/COLAR, QUE CONTENHA ESTA MESMA REGRA DE CONTINUIDADE RECURSIVA até BAV12 comprovadamente qualificado.**
