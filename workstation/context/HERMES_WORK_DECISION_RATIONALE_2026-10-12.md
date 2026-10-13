# Preservação de decisões e alternativas — pausa estratégica de 2026-10-12

**Owner de decisões:** [`DECISIONS.md`](DECISIONS.md). Este é um memorial com fundamentos/trade-offs históricos; **não** revoga decisões nem substitui ADRs.

## D-045 — Admissão progressiva e separação Session/Task/TaskRun
**Problema:** conversas e ações pontuais eram promovidas cedo demais a cartões `running` e `TaskRuns`, contaminando outros turnos com `SUPERSEDED` e bloqueios de verificação. Uma pergunta comum não é compromisso durável.

**Opções debatidas:** A desativar toda promoção automática (contém risco, mas perde autonomia); B admitir todas como rascunho (gera ruído); C admissão inteligente e progressiva com triagem sem reivindicar run (decisão escolhida, implantação inicial de contenção B); D preservar a promoção ampla atual (baixa mudança, mantém bug). Houve também alerta de que `force=True` podia contornar YAML e precisava autorização de ingresso tipada.

**Decisão:** Session = contexto conversacional; Task = responsabilidade persistente canônica; TaskRun = tentativa com autoridade. Conversação não cria cartão; ação pontual pode usar prefab/Browser sem TaskRun especulativa; trabalho durável entra `triage` e só é reivindicado por um owner canônico no momento certo. Reinício e repetição devem deduplicar sem reabrir tarefas bloqueadas. PR #75 + #79 + #83 contêm fatias testadas em branches, **não main**.

**Trade-off:** classificadores de intenção precisam de corpus de falso positivo/negativo e mecanismos `force-work` tipados. Não há solução puramente por palavras-chave; pragmática e efeitos importam.

## D-014/D-024 — autoridade de execução e verdade de efeitos
**Problema:** retorno de ferramenta, resposta de UI, handoff humano ou snapshot próprio podem ser confundidos com comprovação do efeito.

**Decisão:** TaskRun canônica delimita tentativa; `VerificationContract` + `evaluate_verification()` e readback independente delimitam conclusão. Depois de ACK perdido, não repetir mutação sem reconciliação; aprovação humana não transforma `uncertain` em `success`. Leases e `409 USER_CONTROL_ACTIVE` preservados; stale run não assume efeito. PRs #73/#74/#79/#83 têm contratos e testes parciais.

**Alternativas rejeitadas:** autorizar retry depois de revisão sem verificar efeito; usar a própria ferramenta mutante como única prova; criar segundo ledger/owner para approvals. **Trade-off:** um bloqueio seguro pode permanecer inconclusivo até observação independente; preferível a mutação duplicada.

## D-007/D-013 e persistência — canonicidade antes de conveniência
**Problema:** estados paralelos de Session/Task/Browser e `HumanHandoffManager` com cache desatualizado causam autoridade cruzada, duplicação e perda de registros.

**Decisão:** usar Kanban SQLite canônico, TaskCompiler/TaskRun e JSON handoff já existentes; locks interprocesso + reload+atomic replace; projections não adquirem autoridade. Nenhum DB novo, nem segundo TaskRun, nem store de UI com permissão executiva.

**Alternativas recusadas:** gravar cada estado de Browser na Task errada, acoplar a sessão ao processo inteiro, ou restaurar históricos automaticamente. **Trade-off:** sincronização/casualidade exigem testes de concorrência, fences e readback.

## D-043 — Kernel criativo engine-neutral (continua relevante durante pausa)
**Problema:** HyperFrames-first restringia o editor; referência EffectCraft/FilmCraft possui comandos com schema, graph math e efeitos, mas portar engines integrais criaria relógios e documentos concorrentes.

**Decisão histórica:** CreativeDocument e CanonicalTime de tempo racional como autoridade única; wrappers/engines via interfaces e importação seletiva de contratos, com autoria humana/IA sobre revisões CAS. EffectCraft: schema `CommandSpec`, graph math ease/bezier; FilmCraft: tempo/cor/media; Three.js/GLB e Penpot via adapters; evitar incorporar egui no Electron, codecs duplicados e violação GPL/AGPL. O CW-AUDIT-01 diferenciou aquilo em que Hermes era superior (controle concorrente, rational time, locks multitrack). PR #77 entrega apenas UI renderer-local; #81 IPC sender-bound ainda DENY-ALL para owner não atestado. Não declarar edição compartilhada qualificada.

## D-042 / D-030 / H-079 — evidência de produto e promoção
**Decisão:** desenvolvimento GREEN local não é release; testes exact-head, Windows Electron empacotado, H-079 upstream/seams e prova end-to-end compõem gate. `PASS_WITH_AUTHORIZATION` é exceção explícita para continuar desenvolvimento, nunca licença para declarar CI GREEN ou merge.

**Alternativas rejeitadas:** usar E2E headless/local-server como substituto de aprovação real em UI, usar smoke tests sintéticos para reivindicar performance/custo, usar PR draft como prova de integração.

## D-044 / OPC / Experience Compiler — economia por comprovação
**Problema:** agentes gastavam tokens/investigação em operações rotineiras (e.g. Abrir ChatGPT/Trello), mas não foi comprovada economia total de sessões.

**Decisão:** primeiro monitorar latência p50/p95, número de chamadas e tokens por resultado verificado. Prefabs passam pela política/owner existente e Experience Compiler só promove capacidade após prova; nenhuma autopromoção de rascunhos nem segundo executor de workflows. Batch/snapshot-diff/cache podem reduzir payload estrutural, mas 70–85% de ganho ou economia de custo total não foi medida em pares reais.

## D-037 / One-Click — não reinstalar em cada startup
Separar bootstrap de runtime; fingerprint de dependências verificado e warm start sem registry quando válido. PR #70 melhora essa fronteira, mas não substitui packaged/offline native dogfood.

## Decisão de 2026-10-12: pausa, não supersessão de ADR
A frente Kanban/authority muda para `PAUSED_BY_STRATEGY`, sem declarar os KI resolvidos, cancelar PRs, excluir dados, alterar `main` ou escolher nova prioridade. Este handoff guarda o conhecimento; próximos esforços serão definidos em outro contexto. Reconsiderar escolhas apenas com nova evidência causal, custo/benefício e atualização consciente do ADR owner.

**Referências:** [dossiê dos defeitos](HERMES_WORK_P0_ISSUES_DETAIL_2026-10-12.md), [PRs](HERMES_WORK_PR_RECONCILIATION_2026-10-12.md), [handoff](HERMES_WORK_STRATEGIC_HANDOFF_2026-10-12.md).
