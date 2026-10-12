# CONTINUAR HWH-001 — HERMES WORKSTATION HUB
**ORDEM DE IMPLEMENTAÇÃO DIRETA. NÃO RECOMECE A AUDITORIA. NÃO REIMPLEMENTE PROVAS APROVADAS. NÃO FAÇA MERGE NA MAIN.**

## 1. Estado publicado e fontes canônicas
Repositório: `kevynlucasprofissional-stack/hermes-agent`.
Branch de feature: `feat/workstation-hub-creative-session-handoff-20261012`.
Worktree da feature: `C:\Github\hermes-agent\.worktrees\workstation-hub-creative-session-20261012`.
Original `origin/main` / base da feature: `a2b56db1bc9e0b5acf48d94fa86a9844a1005842`.
Branch de integração H-079: `integration/hwh-upstream-20261012-53df274`.
Worktree H-079: `C:\Github\hermes-agent\.worktrees\hwh-upstream-baseline-20261012`.
Upstream pin observado: `53df274b08f2bbbe82bb67bb50c7571952e95809`; merge-base anterior: `66605471e9f0b0832abbefaf625ce08e948ca540`.
Os checkpoints estão em `workstation/context/workstation-hub-mvp/{PLAN,STATE,EVIDENCE,DECISIONS,NEXT_PROMPT}.md` nesta branch GitHub. O HEAD na publicação do NEXT_PROMPT é posterior a `d4fea064a9b040579a653778c6a566ddc49c37d7`; confirme o SHA real via GitHub ou `git fetch origin; git rev-parse origin/feat/workstation-hub-creative-session-handoff-20261012`.
PR HWH: ainda não aberto à época do checkpoint. Não alegue PR sem consultar.
Checkout primário: `C:\Github\hermes-agent` em `fix/hermes-oneclick-lock-startup-20261011`, último observado `9fffa7f3ffcc2c50774654c271fe25e92ce459e8`, DIRTY. **NUNCA TOCAR/RESETAR/STASH/OVERWRITE.**
PRs relevantes #77, #81, #83, #85: observados OPEN, DRAFT, não merged em 12/10/2026. Revalidar se alteraram.

## 2. Missão — não reduzir
**HWH-01:** “Abra o Creative Workstation” e variantes devem disparar operação conhecida no Hermes Agent para abrir/focar interface interna React Creative, SEM buscas de arquivos ou abrir loopback HyperFrames. O `browser_creative_studio_open` existente serve outro propósito. Capability tipada agent↔Desktop e confirmação real.
**HWH-02:** Sidebar Browser→Workstation preservando `/browser`; botão “Abrir Creative Workstation”; Creative como aba React interna do Browser Hub, provider correto, WebContentsView nativas preservadas, viewport/occlusion sem cliques bloqueados.
**HWH-03:** Botão “Levar para sessão” na aba manual; criar sessão verdadeira via `session.create` no Gateway/perfil certo; adotar a MESMA aba e `WebContentsView` em BrowserTask persistente (sem nova tab/loadURL); apresentar chat com pane; lease humano obrigatório e 409 durante controle, liberação explícita para agente. Rejeitar sessão estrangeira, stale run, conflitos, dupla admissão; rollback/reconciliação seguro.

TDD RED→GREEN, testes reais em Electron (E2E-A Agent→Creative, E2E-B Web↔Creative, E2E-C Manual Web→Session→Agent), regressões, exata autoridade. Não duplicar stores/sessões/tasks, não implementar editor criativo avançado, automação aprendida, múltiplas sessões ou replay de histórico humano. Não declarar estado JavaScript volátil recuperável após crash do Electron.

## 3. Status factual
HWH-00 = IN_PROGRESS / prerequisite H-079 Stage A merge; HWH-01/02/03/04/05 = NOT_STARTED. **Nenhuma alteração de código HWH implementada; não há evidência de Electron E2E.** Os quatro arquivos canônicos PLAN/STATE/EVIDENCE/DECISIONS publicados no GitHub são a entrega documental atual.
O `origin/main` não tem checks retornados para a2b56db1; ausência de checks NÃO é CI verde.
O H-079 exige baseline upstream qualificado antes de novas alterações de runtime. A exceção PASS_WITH_AUTHORIZATION histórica registrada no engineering journal é para outro trabalho; não extrapolar para este. Sem Stage A green, marque qualquer trabalho como release BLOCKED, nunca MVP_QUALIFIED.

## 4. PRIMEIRA AÇÃO EXATA — concluir Stage A separado
Abra o worktree `C:\Github\hermes-agent\.worktrees\hwh-upstream-baseline-20261012`.
Rode `git status`, `git ls-files -u`, `git diff --name-only --diff-filter=U`. O merge `git merge --no-commit --no-ff upstream/main` foi iniciado e está em progresso. Não rode um segundo merge, não aborte sem preservar o trabalho.
Cinco conflitos encontrados: `agent/chat_completion_helpers.py`; `apps/desktop/electron/updater/checkout-source.test.ts`; `pyproject.toml`; `tools/tool_search.py`; `uv.lock`.
O script temporário `C:\Temp\hwh_stagea_resolve.py` foi EXECUTADO uma vez e modificou o working tree para remover os marcadores. Os cinco caminhos ainda não foram `git add`ados, portanto o index continua com U; NÃO execute o script novamente sem verificar conteúdo.
Revisão específica necessária:
- agent/helpers: manter `_current_provider_usage` e upstream `carrier_record`, validar indentação/comportamento.
- tool_search: manter `register_tool_search_projection` e upstream `_record_search_metric`, validar ambos.
- updater test: candidata preserva downstream wrapper `_fixture_original_build_opener`, comparar contra upstream `_hermes_loopback` e garantir idempotência com teste.
- pyproject: candidata preserva downstream `exclude-newer = "14 days"` e muitas exceções; upstream usa 3 dias. Resolver explicitamente a política sem downgrade silencioso.
- uv.lock: opções e extras downstream preservados, mas consistência do lock **não comprovada**.
`uv lock --check --offline` falhou por falta de Git cache de `misaki@f03fd2be`. Uma chamada de `python -m pytest` foi bloqueada pela política da ferramenta remota; NÃO contá-la como teste e não contornar bloqueio de segurança. Procure meios autorizados de validação. Também foi tentado `python -m py_compile` sem erro emitido, mas código de saída não isolado.
Depois de revisão, somente se seguro: `git add` dos cinco, `git diff --cached --check`, execuções de pytest focado, testes Electron updater, lock, seam reconciliation, baseline exato e CI; apenas então criar commit Stage A e PR isolado, rebase/branch feature a partir da base qualificada, sem alterar main. Se Stage A não qualificar, registre o blocker e pare antes de implementar runtime.
O upstream novo afetou `apps/desktop/src/app/contrib/surfaces.tsx`; procure provider/policy de Creative após merge.

## 5. Implementação, somente após baseline admissível
HWH-01: escrever primeiro teste RED para operação agent→Desktop de abertura interna; usar registro de ferramentas existente e IPC tipado autenticado, foco idempotente, indisponibilidade erro. Aproveitar PR #77 apenas onde pertinente.
HWH-02: teste RED de sidebar/aba Creative/occlusion, alterar `apps/desktop/src/app/browser/index.tsx`, `chat/sidebar/index.tsx`, `contrib/surfaces.tsx`/provider e testes. Preservar Chromium e rota legada.
HWH-03: teste RED de adoção de aba com `tabId`/WebContentsView constantes, sem reload; gateway `session.create`, trusted sender/session, `workstation-browser-task.ts`, runtime maps `taskTabs`, IPC mínimo/preload, chat pane, human lease. Testar concorrência/falhas/foreign session.
HWH-04: executar 3 E2Es no Electron real, regressões/segurança, typecheck/build, CI exact-head, sem mocks como única evidência.
HWH-05: commits incrementais, push, PR DRAFT se parcial, documentação + evidência; sem merge main. Concluir apenas se 3 jornadas E2E passaram e todos os critérios do PLAN.md comprovados.

## 6. Handoff recursivo obrigatório
Não dependa deste chat. Em CADA sessão incompleta: atualize `STATE.md`, `EVIDENCE.md`, `DECISIONS.md`, `NEXT_PROMPT.md` na branch de feature com branch/SHA completos, worktree, PR, arquivos modificados, testes EXATOS com PASS/FAIL/SKIP/exit code, bloqueios reais, status por HWH, próxima função/arquivo/teste e commit pretendido.
Entregue na resposta **UM ÚNICO PROMPT COMPLETO PARA COPIAR/COLAR** contendo missão, identidade exata, estado factual, próxima ação exata, regras de segurança/H-079/TDD/20-80, critérios de aceite e ESTE MESMO DEVER DE GERAR OUTRO HANDOFF quando a sessão seguinte terminar incompleta.
Nunca fingir E2E, CI, green, implementação, push ou conclusão. Não fazer merge na main. Continue trabalhando sem repetir auditorias concluídas; se houver blocker, registre, execute atividades independentes realmente seguras e pare com checkpoint real.
