# CONTINUAR HERMES EXPERIENCE COMPILER — PR #82 — IMPLEMENTAÇÃO DIRETA

**EXECUÇÃO, NÃO PLANEJAMENTO. NÃO REFAÇA A AUDITORIA.** Esta missão retoma as etapas EC-03 a EC-14 com teste RED→GREEN, owners de produção, qualificação independente e publicação apenas na branch existente.

Use GitHub, Remote Desktop Commander, Superpowers e Community Agent Workflows. Leia primeiro os arquivos canônicos, depois execute. Não mexa no checkout principal.

## 1. Estado do repositório e do PR

- GitHub: kevynlucasprofissional-stack/hermes-agent
- PR: https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/82
- Estado pretendido/último confirmado: **OPEN, DRAFT, NÃO MESCLADO**; verificar novamente em tempo real.
- Branch: feat/experience-compiler-real-reuse-20261011
- Worktree: C:\Github\hermes-agent\.worktrees\experience-compiler-p0-p2-20261011
- Checkout principal: C:\Github\hermes-agent — **sujo por trabalho independente, preserve tudo; não executar reset/clean**.
- Último commit de CÓDIGO executado neste checkpoint: **c3f87a84860615f2086f17191921605068c6932c**. A documentação/handoff pode adicionar commit posterior: obtenha o SHA atual exato no Git e confira se o GitHub PR head corresponde.
- Commits imediatamente anteriores: 40f8f82a663152bcbade0fea809352973edd1dc7 (intenção formal de navegação CALL), f37208a4e8dbe10e7387ecbb5774d93bf97454df (documentação), 3b9f18ac51528da329fb1fdfdaba5f98893b4e2a (EC-04 provas), 065acd189b (EC-03 lease/owner).
- Preserve todos os logs locais `.ec*.log`. Nunca inclua esses logs em commits; não publicar dogfood, dados privados ou segredos. Hooks nativos Lefthook passaram nos commits de código. Um `index.lock` órfão no diretório .git/worktrees da worktree foi liberado SOMENTE após verificar >148 segundos e zero processos git.exe; não voltar a apagar locks sem prova de orfandade.

## 2. Fontes canônicas — leia primeiro, nessa ordem

1. workstation/context/experience-compiler-activation/PLAN.md
2. workstation/context/experience-compiler-activation/STATE.md
3. workstation/context/experience-compiler-activation/EVIDENCE.md
4. workstation/context/experience-compiler-activation/DECISIONS.md
5. workstation/context/experience-compiler-activation/NEXT_PROMPT.md
6. AGENTS.md / workstation/AGENTS.md / workstation/context/README.md
7. workstation/context/UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md
8. workstation/context/EXPERIENCE_COMPILER_STUDIO_IMPL_2026-10-11.md
9. workstation/ROADMAP.md / workstation/context/engineering-journal/CURRENT.md

A auditoria antiga fica em workstation/context/audits/C2C-HARNESS-EXPERIENCE-2026-10-11. NÃO reiniciar.

## 3. Execução concluída neste checkpoint — não refazer

**EC-03 / Browser e autoridade:**
- `workstation/run_adoption.py`: `browser_navigate` deixou de ser read-only e exige `CALL("browser.navigate", host)`, host HTTPS comprovado, eventual path_family, efeito concedido, readback independente, lease e autorização. Em `RunLocalAdopter`, snapshot e orçamento/uncertainty são reavaliados no item-boundary e antes de passos.
- `workstation/integrations/hermes/run_local_adoption.py`: factory e chamadas `dispatch/readback` falham se owner já pertence a TaskRun antigo.
- `workstation/work_intent.py`: comando reconhecido "Abra o Trello" declara explicitamente CALL("browser.navigate", "trello.com") no seu orçamento ao lado dos SET dos predicados host/page_family/recovery_state, **sem permitir outros hosts**. Regressão original: 10 PASS; H-080B após CALL: 2 PASS. Commit `40f8f82a66`, Lefthook PASS.

**EC-04 / aprendizagem intermediária:**
- `workstation/experience_compiler/progressive.py`: `verified_success` exige E2+ e prova persistida/integral de readback ou recibo canônico vinculado a task_id, run_id, operation_id. Captura recebe agora `operation_family`, `target_family`, `effect_class`, `scope` fornecidos pelo contrato admitido. Não inventa `parameters` e NÃO generaliza argumentos sem prova.
- `workstation/operational_kernel.py`: repassa família/target/escopo de `cap.formal_contract` e `cap.effect`, inclui essas dimensões no evento para OnlineCompilabilityMonitor; envia `proof_ref` canônico para a amostra.
- Um defeito RED adicional: `state_before` arbitrário informado no contexto criava delta causal falso apesar do readback só provar o estado POSTERIOR. Corrigido: **delta somente quando existe `state_before_ref` comprovado, com artefato `workstation.operational_prestate_readback.v1` contendo `task_id/run_id/operation_id`, `observer=workstation.operational_prestate`, `read_before_write=true` e predicados iguais**; sem isso o delta fica vazio. Prova inválida falha fechada. Testes negativos incluem wrong run, wrong prestate, falta de read_before_write.
- IMPORTANTE: o parser/validador do novo `state_before_ref` existe, mas **o produtor real dessa prova anterior ainda não foi qualificado**. Sem produtor e sem parâmetros de passos atestados, `ExperienceCompiler.mine` ainda pode não conseguir gerar capacidade operacional a partir das transições progressivas. NÃO declarar EC-04 end-to-end concluído.
- Novo commit EC-04: `c3f87a84860615f2086f17191921605068c6932c`, Lefthook PASS.

**EC-05 / Laya:**
- O Laya vendorizado em `workstation/third_party/laya` informa v0.3.23; SHA fonte e lock são `4aa6761be8173de4ce6d92c31b3e40b6eaf59a7c`. `verify_laya_provenance()` PASS; focused `test_laya_vendor_provenance.py + test_laya_real_contract.py + test_system1_capability_routing.py`: **10 PASS, 1 SKIPPED**. Live checkpoint não executado; DIRECT/Electron release não qualificados.

**Testes já realizados:**
- Full `test_online_compilability_safety.py + test_progressive_verified_gate.py + test_progressive_experience_capture.py + test_run_local_browser_effect_authority.py`: 54 PASS após adição da captura metadata, **ANTES** da última exigência de `state_before_ref`; consulte o log `.ec04_prestate_final_safety.log` para o resultado do teste completo final.
- Focused progressive + Kernel: 24 PASS; teste prestate positivo + negativos: 3 PASS; H080B em HEAD com último código: 2 PASS/24 deselected; owner factory 7 PASS. Ruff PASS.
- Um `LayaDecisionProvider: No module named laya` aparece quando a venv do checkout principal é usada sem PYTHONPATH vendorizado. Não tratar isso como prova do runtime real nem instalar dependências globalmente.

## 4. PRÓXIMA AÇÃO TÉCNICA OBRIGATÓRIA — EC-04 (prioridade máxima)

**Não reinicie auditorias. Crie primeiro os testes RED e então implemente:**

A. Um owner real de operação (filesystem primeiro) captura PRESTATE **antes** de um efeito e persiste um recibo sob `workstation.operational_prestate_readback.v1`, vinculando a prova de leitura independente ao mesmo `task_id/run_id/operation_id` e recurso. No restart, drift, escopo alterado, lease revogado, prova ausente ou contraditória, nada promove, nada executa e nenhum delta é inferido. Arquivos principais: `workstation/operational_kernel.py`, `workstation/run_adoption.py`, `workstation/integrations/hermes/run_local_adoption.py`, `workstation/experience_compiler/progressive.py`. NÃO crie segundo executor; use owner/Kernal já existentes.

B. A execução real vinculada ao dono da operação persiste os ARGUMENTOS GENERALIZÁVEIS estritamente autorizados e verificados (path/target e outros parâmetros tipados admitidos), não dumps de tool output, não texto de página e não secrets. Garanta correspondência com item durável e readback, sem aceitar `parameters` fabricados pelo observador genérico. A amostra de corpus deve conter estado antes/depois/delta e operação reexecutável, mas só se provas forem positivas.

C. Prove `TaskRun` REAL ainda com itens PENDING: primeiro item real tem leitura anterior e posterior atestadas; `capture_progressive` persiste; `ExperienceCorpus` vê VERIFIED_SUCCESS; `OnlineCompilabilityMonitor` descobre, Laya decide, miner valida, replay controlado vinculado à candidata, oferece, `RunLocalAdopter` adota próximo item equivalente; novo readback independente gera VERIFIED_REUSE; nenhuma mutação repetida, SHADOW nunca executa. Não usar mocks para reivindicar Laya/DIRECT real. Use os fixtures reais `test_online_compilability_safety.py` como ponto de partida, mas substitua a injeção manual de amostras por capture real verificado.

**Primeiro teste RED esperado:** execução de 2+ itens com owner real grava recibo PRESTATE e POSTSTATE da mesma operação antes do fechamento do plano; corpus reidratado mostra delta só para o item atestado, e outro item permanece PENDING. Ausência de prestate/lease/escopo/autoridade impede efeitos e aprendizado.

## 5. EC-03, EC-05 e etapas posteriores

EC-03: completar H-082 nativo Electron com lease, restart, drift, scope, readback negativo e budget CALL( browser.navigate, host), sem ampliar grants. Testes com ações realmente mediadas pelo owner, não só produção de intent.

EC-05: executar `workstation/scripts/qualify_laya_system1.py` com runtime Python isolado, PYTHONPATH para vendored Laya v0.3.23, checkpoint real quando operacionalmente possível; documentar proveniência/checkpoint, inferência, decisão e verificador. Sem download destrutivo e sem alterar o checkout principal.

EC-06: descoberta e ranking de capacidades promovidas pré-System-2 com autorização e utilidade provadas.
EC-07: funil verificável, latência, tokens/calls e Savings realmente medidos; EvidenceRef serialization já corrigida.
EC-08: restart/checkpoints monotônicos, regressão de evidence revision.
EC-09: score e revisões versionadas seguras.
EC-10: benchmarks comparáveis de filesystem/native Browser/Trello, p50/p95 e custo por VERIFICADO.
EC-11: explorer nativo Electron, autenticado, leitura única.
EC-12: edição tipada, preservação de contrato/verificador e versionamento imutável.
EC-13: HOLD para workflows/triggers/loops sem caso de uso e owner qualificados; nunca importar n8n/Activepieces engine.
EC-14: H-079/H-081/H-082, upstream pin, CI exato no SHA publicado e dogfood Windows/Electron. **Não mesclar na main**.

## 6. Comandos iniciais

```powershell
$w='C:\Github\hermes-agent\.worktrees\experience-compiler-p0-p2-20261011'
Set-Location $w
git status -sb
git rev-parse HEAD
git log -5 --oneline
$env:PYTHONPATH='C:\Github\hermes-agent\.venv\Lib\site-packages;'+(Get-Location).Path
& 'C:\Github\hermes-agent\.venv\Scripts\python.exe' -m unittest -q workstation.tests.test_run_local_owner_factory
uvx --offline pytest -q -o addopts='' workstation/tests/test_online_compilability_safety.py workstation/tests/test_progressive_verified_gate.py workstation/tests/test_progressive_experience_capture.py workstation/tests/test_run_local_browser_effect_authority.py --tb=short
```

Para Laya vendorizado, prefixar PYTHONPATH também com `$w\workstation\third_party\laya;`. Os logs .ec*.log NÃO podem entrar no stage.

## 7. Regras e protocolo de encerramento obrigatório

- Código de produção somente após RED→GREEN, regressões, revisão de segurança e hooks nativos, com commits pequenos.
- Nunca fazer reset/clean, merge na main, alteração em checkout principal, migração de efeito sem autorização explícita ou qualquer execução em SHADOW.
- Nem proveniência do Laya nem testes instrumentados são prova de DIRECT com checkpoint real. Nenhuma redução de System-2 pode ser alegada sem medição.
- Atualizar PLAN.md, STATE.md, EVIDENCE.md, DECISIONS.md, NEXT_PROMPT.md, ROADMAP.md e Engineering Journal.
- No final, reportar: SHA exato, branch/worktree/PR, mudanças não commitadas, testes, falhas/gates, próxima ação exata, funções a alterar, primeiro RED e critério de conclusão.
- **OBRIGATORIAMENTE ENTREGAR UM NOVO PROMPT DE CONTINUAÇÃO PRONTO PARA COPIAR/COLAR**, autossuficiente, repetindo esta mesma obrigação para a sessão seguinte. Não entregar apenas resumo.

COMECE PELO HEAD REAL E IMPLEMENTE EC-04/EC-03, NÃO REFAÇA A AUDITORIA.
