# CONTINUAR HERMES EXPERIENCE COMPILER — EC-04 PRODUÇÃO → EC-14

**MISSÃO DE IMPLEMENTAÇÃO DIRETA, NÃO AUDITORIA OU PLANO.** Use GitHub, Remote Desktop Commander, Superpowers e Community Agent Workflows. Continue automaticamente as tarefas elegíveis, priorize segurança/autoridade, TDD RED→GREEN, verificação independente, commits pequenos e hooks nativos.

## Estado, repositório e isolamento
- Repo GitHub: kevynlucasprofissional-stack/hermes-agent.
- PR #82: https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/82 (DRAFT, OPEN, NÃO MESCLADO no último preflight).
- Worktree: C:\Github\hermes-agent\.worktrees\experience-compiler-p0-p2-20261011.
- Branch: feat/experience-compiler-real-reuse-20261011.
- Base antes desta continuação: 7d85ffdf627eeb0f5e352bcffd203007607e6916. NOVO COMMIT DE CÓDIGO confirmado: d3c171c3ef78efb2c3c025af00938bdd6694ddc9. A documentação pode ter commit posterior: VERIFIQUE git rev-parse HEAD e PR head em tempo real.
- Checkout principal C:\Github\hermes-agent SUJO por outros trabalhos: NÃO tocar, resetar ou limpar. Preserve logs .ec*.log UNTRACKED e jamais faça git add -A nem commit de logs/privados.
- H-079 upstream-first, H-081 real Laya DIRECT, H-082 native Browser e CI exact-head permanecem HOLD; não mesclar ou alegar release.

## Fontes canônicas — ler antes de qualquer outra ação
1. workstation/context/experience-compiler-activation/PLAN.md
2. workstation/context/experience-compiler-activation/STATE.md
3. workstation/context/experience-compiler-activation/EVIDENCE.md
4. workstation/context/experience-compiler-activation/DECISIONS.md
5. workstation/context/experience-compiler-activation/NEXT_PROMPT.md
6. AGENTS.md; workstation/AGENTS.md; workstation/context/README.md; workstation/context/UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md
7. workstation/ROADMAP.md; workstation/context/engineering-journal/CURRENT.md; workstation/context/EXPERIENCE_COMPILER_STUDIO_IMPL_2026-10-11.md.
Auditoria C2C anterior sob workstation/context/audits/C2C-HARNESS-EXPERIENCE-2026-10-11: NÃO repetir.

## O que mudou nesta continuação (EC-04)
1. OperationalKernel.observe_semantics() no filesystem e composite foi corrigido para usar _resolve_path(path, base_dir), evitando falsos estados ao ler no CWD.
2. Na execução do MESMO OperationalKernel com DurableTaskStore REAL, uma escrita fs_write single-step, dentro de base_dir autorizado, após primitive_admission, persiste workstation.operational_prestate_readback.v1 **antes** do checkpoint de dispatch. A prova tem task_id/run_id/operation_id, resource, observer, read_before_write, estado semanticamente abstraído. Exige plano running, item pending/running, identidade correspondente e escopo; pós-captura revalida owner/plan/item antes de executar. Não é um segundo executor nem lease autônomo.
3. Verificador builtin fs_hash/hash_file/fs_stat/stat grava independentemente apenas hash/metadados, nunca conteúdo bruto de fs_read, sob workstation.operational_filesystem_readback.v1. Vincula recurso real observado, task/run/operation, READ-AFTER-WRITE e URI ao VerificationEvidence. Canonical proof passa a apontar esse readback. O ExperienceCorpus captura VERIFIED_SUCCESS com antes/depois/delta comprovados, mesmo que outro WorkItem permaneça PENDING.
4. Progressive capture rejeita prestate de recurso A com readback posterior de recurso B mesmo quando task/run/operation coincidem. Mantém todas as exigências E2+, trusted runtime, canonical verifier, readback independently persisted.
5. Testes RED da sessão: precondition errada, ausência de prestate, falta de admissão, revogação após prestate, hash VERIFIED que não alimentava corpus, e mix A/B. Testes de segurança para cross-run, plan cancel, escape, restart incerto, composite, ordenação prestate/write.
6. NOTA: resultou uma prova local do owner e do corpus, NÃO uma qualificação completa de offer/reuse com Laya real, nem PROMOTED global nem VERFIED_REUSE. O estudo de parâmetros tipados reexecutáveis e validade de source scopes é a próxima prioridade.

## PRÓXIMA AÇÃO TÉCNICA PRIORITÁRIA — EC-04
Rever código:
- workstation/operational_kernel.py::execute_capability/observe_semantics
- workstation/experience_compiler/progressive.py::capture_progressive
- workstation/tests/test_ec04_production_prestate.py
- workstation/experience_compiler/compilability_monitor.py / compiler.py / corpus.py
- workstation/run_adoption.py / integrations/hermes/run_local_adoption.py

Testar RED e implementar vínculo **tipado e reproduzível** de argumentos de operações com provas do owner real e do item durável, sem expor content/secret e sem inventar parâmetros de replay. Definir explícita política que não torne uma constante de texto privada reutilizável. Provar, em TaskRun ainda aberta com diversos itens:
1) read-before-write e read-after-write com recurso exato, status/lease e scope válidos;
2) ExperienceCorpus registra VERIFIED_SUCCESS com operação, propriedades, prestate e delta efetivamente comprovados;
3) Laya REAL com checkpoint pinned decide (não usar fake Laya como prova);
4) miner gera candidata, validador canário faz replay positivo/negativo candidate-bound, offer é emitido em modo formalmente autorizado;
5) RunLocalAdopter reutiliza apenas item equivalente, revalida lease/scope/uncertainty e verifica readback;
6) VERIFIED_REUSE e economia de provider somente se medidos.
Negativos obrigatórios: injeção de parâmetros, mismatch path/basedir, false postreadback, cross-run, restart, missing proof, revoked lease, SHADOW, drift.

Depois EC-05 LIVE Laya v0.3.23 pinned/source SHA 4aa6761be8173de4ce6d92c31b3e40b6eaf59a7c, sem instalar globalmente; EC-06 ranked pre-System2 authorized discovery; EC-07 honest telemetry; EC-08 restart; EC-09 score/revisions; EC-10 real paired benchmarks; EC-11 Electron authenticated read-only inspector; EC-12 typed editor; EC-13 HOLD until justified; EC-14 exact-head H079/H081/H082, CI, dogfood. NÃO MERGE.

## Comandos iniciais Windows
```powershell
$w='C:\Github\hermes-agent\.worktrees\experience-compiler-p0-p2-20261011'
Set-Location $w
git status -sb
git rev-parse HEAD
git log -6 --oneline
$env:PYTHONPATH='C:\Github\hermes-agent\.venv\Lib\site-packages;'+$w
uvx --offline pytest -q -o addopts='' workstation/tests/test_ec04_production_prestate.py workstation/tests/test_progressive_verified_gate.py workstation/tests/test_operational_capabilities.py --tb=short
uvx --offline pytest -q -o addopts='' workstation/tests/test_online_compilability_safety.py workstation/tests/test_run_local_browser_effect_authority.py --tb=short
```

## Encerramento obrigatório — propagação recursiva
Execute o máximo possível neste turno. Ao encerrar, registre: HEAD local e remoto completos, status/PR/draft, arquivos alterados/não commitados, testes + resultados exatos, gates e falhas, próximo RED com arquivo/função, critério de conclusão. Atualize PLAN.md, STATE.md, EVIDENCE.md, DECISIONS.md, NEXT_PROMPT.md, ROADMAP.md, engineering-journal/CURRENT.md. Commit/push só na branch existente com Lefthook; nunca main. **ENTREGUE SEMPRE UM NOVO PROMPT COMPLETO, AUTOSSUFICIENTE, PRONTO PARA COPIAR E COLAR, contendo esta mesma obrigação para a sessão seguinte.** NÃO entregue apenas resumo.

COMECE PELA VERIFICAÇÃO DO HEAD REAL E PELO TESTE RED DOS ARGUMENTOS REEXECUTÁVEIS COM PROVA DO OWNER.
