# Manifesto de fontes e fronteiras de evidência — 2026-10-12

**Tipo:** controle documental público, sem cópia de sessões privadas. **Estado:** inventário de 1 export integral (4.458 linhas), referências de anexos e confronto com GitHub em 2026-10-12. **Congelamento:** somente documentação, sem execução de runtime.

## Fonte primária lida integralmente como histórico
- `ChatGPT-Branch · Plano Hermes e Workstation-20261012-1602(1).md` — export de 207.227 caracteres / 4.458 linhas; SHA-256 `f429972fb70f97af5131bb81df274edbfb9614a89d050f077224ea5aa4f0251b`; período de 11/10/2026 16:58 até 12/10/2026 02:58 no export. **READ**. A fonte está anexa à conversa, mas **não é incorporada** ao GitHub público.
- 17 prompts e suas respostas/continuações, cobrindo: 16:58 inventário de nove anexos/cinco logs; 17:36 correção Kanban; 17:59 BOA-001/Rail 2/Rail 3; 19:13–20:43 decisão arquitetural D-045; 21:49 planos de implementação; 22:53 admissão; 00:20–00:30 retomadas; 01:00–02:58 refinamentos progressivos do PR #83.
- Os nove anexos citados no primeiro prompt (históricos, três runs e relatórios) e três runs posteriores são **REFERENCE_ONLY** neste manifesto: seus nomes e conclusões citadas foram examinados no export; os bytes originais de cada anexo não constituem leitura independente nesta missão. Não publicar dados privados dessas runs.
- Há notícia histórica de um controle privado `HERMES_WORK_CONTROLE_E_PLANO_2026-10-11.md` e manifesto privado `HERMES_EVIDENCE_MANIFEST_2026-10-11.json` em /Hermes Work/Controle de Contexto/. **REFERENCE_ONLY**; existência e conteúdo presente não foram validados aqui.

## Matriz de leitura do repositório
| Fonte | Classe | Leitura/verificação | Uso |
|---|---|---|---|
| `workstation/AGENTS.md` | Instruções | READ via GitHub main | H-079, isolamento, ordem de leitura |
| `workstation/ROADMAP.md` | Roadmap | READ (índice + seções pertinentes) | Estados históricos; adendo de congelamento |
| `workstation/context/README.md` | Índice | READ | Source of truth e navegação |
| `workstation/context/KNOWN_ISSUES.md` | Issue register canônico | READ (inventário + seções pertinentes) | Reutilizado, não substituído |
| `workstation/context/DECISIONS.md` | ADR canônico | READ (inventário + seções pertinentes) | Decisão D-045 e decisões preservadas |
| `workstation/context/HERMES_WORKSTATION_INTELLIGENCE.md` | Inteligência | READ (índice + trechos pertinentes) | Síntese transversal |
| `workstation/context/engineering-journal/CURRENT.md` | Jornal | READ (índice + trechos pertinentes) | Entrada append-only |
| `workstation/context/P0_KANBAN_BROWSER_AUTHORITY_HANDOFF_2026-10-12.md` | Documento P0 | READ na branch #83; NOT_FOUND em main | Evidência e próximo seam |
| `workstation/context/P0_KANBAN04_HANDOFF_ATOMICITY_2026-10-12.md` | Documento P0 | READ na branch #83; NOT_FOUND em main | Persistência, concorrência |
| `workstation/context/P0_PROOF_RECONCILIATION_2026-10-11.md` | Documento P0 | READ na branch #83; NOT_FOUND em main | Readback e dry-run |
| `workstation/context/P0_INTEGRATION_2026-10-11.md` | Documento P0 | READ na branch #83; NOT_FOUND em main | Integração 70–75 |
| GitHub PRs #70–#77, #79–#83 | Metadados de PR | READ, consulta explícita em 2026-10-12 | Branch, base, HEAD, draft/merge |
| PR #83 exact-HEAD `22498a09db` | CI | READ: statuses=[]; PR-triggered workflow_runs=[] | **Nenhuma qualificação CI demonstrada**, não equivale a CI vermelho |

## Cronologia compacta da descoberta
1. **11/10 16:58–17:36:** análise de runs observou handoffs repetidos/SUPERSEDED, tarefa simples que se torna investigação longa, bloqueios de UI e falta de prova de efeitos; a Creative UI existia mas ainda não era fluxo profissional completo.
2. **11/10 17:36–19:13:** #71 classificou leituras Kanban como PURE_READ; #72 BOA-001 segregou leitura/interação/mutação; #73 deduplicou/consumiu revisão por operação sem tratar aprovação como readback; #74 tipou fence e pendências de runs superseded.
3. **11/10 19:13–22:53:** problema de tasks foi identificado como confusão entre intenção, Task durável, TaskRun e Session; opção C progressiva com contenção B escolhida para D-045; #75 entregou triage e claim sob execução; #76 convergiu #70–#75 corrigindo owner injetado no TaskCompiler; #77 editor criativo local sem CAS backend.
4. **11/10 22:53–12/10 00:30:** foram separados P0.1–P0.5, corrigidos force-work e prova de conclusão (#79), executada reconciliação histórica SOMENTE dry-run (#80), e iniciada #83 com isolamento Browser/Session.
5. **12/10 01:00–02:58:** #83 avançou por testes de admissão concorrente, reinício nativo, UI de takeover/lease, handoffs atômicos entre processos, fence de revisão por TaskRun e prova nativa de efeito único após ACK perdido. Último HEAD do export: `22498a09db...`. Pendente: E2E ligado ponta a ponta de HANDOFF real na UI → readback tipado → continuação.
6. **Verificação posterior ao export, 12/10:** GitHub mantém #83 open/draft/unmerged com aquele SHA e docs P0 apenas na branch; contexto da main ainda não integra essas decisões recentes.

## Níveis obrigatórios de afirmação
`HISTORICAL_CLAIM` = alegado em texto; `LOCAL_TESTED` = execução de teste reportada no histórico/PR; `BRANCH_CODE` = existente em branch consultada; `PUBLISHED_PR` = HEAD remoto; `MAIN_MERGED` = demonstrado em main; `PRODUCT_QUALIFIED` = E2E produto + exigências de release comprovadas.

Neste snapshot #70–#83 listados estão **PUBLISHED_PR / OPEN, unmerged**, alguns com `LOCAL_TESTED`. Isso não concede `MAIN_MERGED` nem `PRODUCT_QUALIFIED`. Documentos desta missão são uma projeção de conhecimento e não novos owners de estado.

## Limites e recuperação
Os documentos de P0 permanecem acessíveis em `fix/p0-kanban-browser-authority-20261012` até o merge; não copiá-los como se estivessem na main. Revalidar os links/ref ao retomar. Ver [mapa dos PRs](HERMES_WORK_PR_RECONCILIATION_2026-10-12.md), [Known Issues](KNOWN_ISSUES.md), [handoff](HERMES_WORK_STRATEGIC_HANDOFF_2026-10-12.md).
