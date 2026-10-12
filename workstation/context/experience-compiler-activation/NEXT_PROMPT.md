# PROMPT DE CONTINUAÇÃO — COPIAR E COLAR

MISSÃO: CONTINUAR HERMES EXPERIENCE COMPILER — EXECUÇÃO INTEGRAL.

Você é a IA implementadora. NÃO repita a auditoria code-to-code e NÃO produza outro plano genérico. Use imediatamente GitHub, Remote Desktop Commander, Superpowers e Community Agent Workflows para continuar as entregas EC-03 a EC-14.

## Repositório e isolamento
- Repositório GitHub: kevynlucasprofissional-stack/hermes-agent
- PR #82: https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/82 (DRAFT, ainda não autorizado merge)
- Branch: feat/experience-compiler-real-reuse-20261011
- Worktree Windows: C:\Github\hermes-agent\.worktrees\experience-compiler-p0-p2-20261011
- Checkout principal: C:\Github\hermes-agent (alterações independentes; NÃO editar, resetar ou limpar).
- Último commit de CÓDIGO EC-04 confirmado: 3b9f18ac51528da329fb1fdfdaba5f98893b4e2a (precedido por EC-03 065acd189b). A documentação pode ser commitada após esse SHA: VERIFIQUE git rev-parse HEAD e GitHub PR head antes de qualquer edição.
- Logs locais .ec*.log não rastreados não devem ser adicionados ao Git.
- Não faça merge na main; não afirme CI verde sem execução exata no HEAD.

## Leia primeiro
- workstation/context/experience-compiler-activation/PLAN.md
- workstation/context/experience-compiler-activation/STATE.md
- workstation/context/experience-compiler-activation/EVIDENCE.md
- workstation/context/experience-compiler-activation/DECISIONS.md
- workstation/context/experience-compiler-activation/NEXT_PROMPT.md
- AGENTS.md, workstation/AGENTS.md, workstation/context/README.md
- workstation/context/UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md
- workstation/context/EXPERIENCE_COMPILER_STUDIO_IMPL_2026-10-11.md
- workstation/ROADMAP.md, workstation/context/engineering-journal/CURRENT.md
- Auditoria anterior: workstation/context/audits/C2C-HARNESS-EXPERIENCE-2026-10-11

## Estado do código confirmado
EC-00: preflight parcial, H-079/H-081/H-082/CI release HOLD.
EC-01: novo comando Browser conhece contrato host/page_family/recovery_state, H080B regressão 2 PASS, sem novo System-2 indevido quando capacidade formal é compatível.
EC-02: canário filesystem candidate-bound fail-closed com contraprovas; regressão histórica 60 PASS / 1 SKIPPED; ainda não release-qualified.
EC-03: run_local_adoption.py valida TaskRun no dispatch/readback mesmo depois do cache; run_adoption.py mapeia browser_navigate para CALL(browser.navigate,host) com HTTPS exato e efeito/readback obrigatório. RunLocalAdopter revalida lease/authority/uncertain mutations/effect budget no começo do item e antes de cada passo. Testes RED provaram execução indevida após cancelamento; GREEN incluiu 3 casos focados, depois 51 pytest PASS e 7 unittest PASS. ALTERAÇÃO: fixture safety passa a identificar explicitamente o owner já validado com _bound_task_run. PENDENTE: E2E native Browser H-082 e migração de budgets de navegação onde intent/capability ainda usa apenas SET sem CALL.
EC-04: progressive.py rejeita VERIFIED_SUCCESS sem proveniência de owner, força E2+ e receipt persistido com run/task/operation correspondentes, valida cadeia de recibo canônico e evita laundering de provas de outro run ou readback falho. operational_kernel.py agora apresenta proof_ref canônico na amostra. 51 regressões passaram incluindo casos novos. PENDENTE: prova integral antes do fechamento do TaskRun com owner real, Laya, mine, validate, offer, RunLocalAdopter e VERIFIED_REUSE. O observador genérico continua OBSERVED/UNCERTAIN, nunca transforma tool ACK em sucesso.
EC-05: import do Laya vendorizado v0.3.23 de workstation/third_party/laya sem instalar globalmente, verify_laya_provenance PASS; SHA fonte e pin 4aa6761be8173de4ce6d92c31b3e40b6eaf59a7c; telemetria System-1 focada 2 PASS. Checkpoint live e DIRECT produtivo ainda não testados/qualificados.
EC-06: descoberta pré-System-2, decisão por utilidade pós-admissão, integração explícita do CALL budget do navegador: PENDENTE.
EC-07: EvidenceRef -> URI-only telemetry corrigido anteriormente. Funil E2E e métricas ainda pendentes.
EC-08 a EC-12: pendentes. EC-13 somente se qualificado pelos casos de uso e Kernel. EC-14 release CI + Windows/Electron + H-079/H-081/H-082: HOLD.

## PRIMEIRA AÇÃO TÉCNICA (NÃO REPETIR AUDITORIA)
1. Obtenha git status -sb, HEAD, PR status e resultados exatos do CI. Preserve logs.
2. Prossiga em EC-03: teste primeiro que native browser_navigate em DIRECT receba orçamento explícito CALL(browser.navigate,host) sem autorização mais ampla, preservando goal host/page_family/recovery_state e readback do Browser owner. O atual CALL em effects_for_step é intencional: não reverta para read_only nem alargue budgets silenciosamente. Arquivos: workstation/work_intent.py, workstation/run_adoption.py, workstation/integrations/hermes/run_local_adoption.py, workstation/control_plane e H080B. RED: operação navegacional não consegue obter budget/autoridade correto, wrong-host rejeitado, lease perdido em restart não executa. GREEN: readback nativo e ação qualificada.
3. EC-04: use a prova canônica intermediária real, inacabada, dentro de DurableTaskStore/OperationalKernel, e confirme que o ExperienceCorpus e OnlineCompilabilityMonitor recebem apenas VERIFIED_SUCCESS com evidência E2+, task/run/operation iguais, durante a TaskRun ainda com itens pendentes. Monte cenário com vários arquivos temporários e progressão mine→validate→offer→adopt→readback→VERIFIED_REUSE. Teste negativas: tool ACK, wrong-run, sem lease, restart, drift, uncertainty. Nunca promover automaticamente.
4. EC-05: qualifique Laya pinned com provinência e checkpoint real em ambiente isolado; não confunda import de código com inferência do checkpoint. Use instruções em workstation/scripts/qualify_laya_system1.py, avaliando flags --live/--full conforme impacto. Não modifique a venv do checkout principal sem cuidado.
5. Continue EC-06..EC-14 sem parar em auditorias. Registre benchmarks reais de latência, tokens/calls/custo por resultado verificado, integre o Studio ao Electron somente após gates P0.

## Comandos de retomada (PowerShell)
$w = 'C:\Github\hermes-agent\.worktrees\experience-compiler-p0-p2-20261011'
Set-Location $w
git status -sb
git rev-parse HEAD
git log -5 --oneline
$env:PYTHONPATH = 'C:\Github\hermes-agent\.venv\Lib\site-packages;' + (Get-Location).Path
& 'C:\Github\hermes-agent\.venv\Scripts\python.exe' -m unittest -q workstation.tests.test_run_local_owner_factory
uvx --offline pytest -q -o addopts='' workstation/tests/test_online_compilability_safety.py workstation/tests/test_progressive_verified_gate.py workstation/tests/test_progressive_experience_capture.py workstation/tests/test_run_local_browser_effect_authority.py --tb=short

## Regras transitivas
Cada tarefa deve seguir teste RED → código mínimo → GREEN → regressão → segurança → commit com lefthook → push apenas na branch draft. Nunca sobreponha trabalho do usuário, não faça git reset/clean, não copie sessões privadas, não contorne autorização humana e não confunda SHADOW com DIRECT. H-079/H-081/H-082/CI exato permanecem HOLD até qualificados.

Ao terminar uma sessão ainda com itens pendentes:
- Atualize PLAN.md, STATE.md, EVIDENCE.md, DECISIONS.md, NEXT_PROMPT.md, ROADMAP.md e Engineering Journal.
- Registre SHA exato, branch, PR, arquivos modificados, alterações não commitadas, testes executados, falhas, bloqueios, próximo teste RED e critério de conclusão.
- Entregue obrigatoriamente um NOVO PROMPT DE CONTINUAÇÃO pronto para copiar e colar, autossuficiente e com esta mesma obrigação replicada; prossiga até EC-14 em sessões subsequentes sem recomeçar.

COMECE AGORA PELA VERIFICAÇÃO DO HEAD E DE EC-03/EC-04. EXECUTE.
