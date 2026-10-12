# BROW-NATIVE-NEXT — Relatório de engenharia (2026-10-12)

**Resultado:** P0 readback e replay fence implementados; AXTree document-fencing implementado; extração schema/cache/redaction corrigida. Trabalho local na branch `audit/browser-native-evidence-20261012`. **NOT_RELEASE_QUALIFIED**: CI exact-head, Electron Windows real/E2E, custos e performance nativos não qualificados. Não fazer merge em `main` a partir deste relatório.

## Proveniência e gate

- Baseline anterior: `dbf51de048bf361015c2f26a1fa79bc69efea63d` (parent `main@a2b56db1bc9e0b5acf48d94fa86a9844a1005842`).
- Upstream pin já ancestral: `66605471e9f0b0832abbefaf625ce08e948ca540`; observado `upstream/main@835c3dd038d903182a66ecc45e34bf5e0de65f00` (245 commits além do pin). Nenhum merge upstream neste ciclo; gate documental de promoção continua aberto.
- Histórico do maintainer no jornal inclui `PASS_WITH_AUTHORIZATION` de continuação de desenvolvimento, não de release. Nenhuma alteração feita no checkout original com mudanças não commitadas de UX; a branch é um worktree isolado.
- Auditorias: `workstation/research/browser-code-to-code-2026-10-10/`, `workstation/context/BROWSER_CODE_TO_CODE_DECISIONS_2026-10-10.md`, `workstation/research/browser-native-followup-2026-10-12.md`.
- Snapshot local de referências: BrowserClaw (`src/actions/batch.ts`, licença MIT), Stagehand (LICENSE MIT), Agent Browser (`cli/src/native/snapshot.rs`, comportamentos de identidade de documento), BrowserOS (LICENSE AGPL-3.0). **Nenhuma fonte AGPL transplantada.**

## Entrega 1 — P0 Batch effect truth

**Commit:** `44de4faa37`, `fix(browser): verify batch effects by readback and fence replay`.

Arquivos: `apps/desktop/electron/workstation-browser-runtime.ts`, `workstation-browser-batch-proof.ts`, `workstation-browser-batch-proof.test.ts`, `workstation-browser-runtime-batch.test.ts`.

- Antes, `verifyAfter()` retornava `verified: Boolean(receiptRef)`: um ACK/receipt sozinho tornava o lote VERIFIED mesmo quando a página não tinha sofrido o efeito.
- Agora o runtime reobserva no próprio `WebContentsView` antes e depois de cada subação, sem devolver dados brutos ao modelo. Valida URL/documentToken (`performance.timeOrigin`), identidade do elemento na mesma página via WeakMap, owner/task/tab/run/documentEpoch e lease de controle humano.
- `type`: comprova o valor local resultante no controle de edição. `click`: só confirma toggles observáveis (`checked`, `aria-pressed`, `aria-expanded`). `scroll`: comprova deslocamento na direção solicitada. `press`: sem verificador semântico específico é `UNCERTAIN`.
- Receipts de ação continuam pertencendo a `BrowserTaskLifecycle`; um receipt sem pós-condição comprovada permanece ACKNOWLEDGED/UNCERTAIN. Primeira incerteza interrompe todos os passos posteriores, sem retry automático. Checkpoint e perda de recibo também deixam o lote incerto.
- Reentrada: `operation_id` com receipt de subação prévia na mesma aba retorna `prior_batch_effect_requires_reconciliation` e não repete a operação. **Limite:** o fencing atual verifica o último receipt recuperável; não é um ledger persistente completo de múltiplas operações concorrentes. Também não recupera efeitos externos cujo receipt tenha falhado antes de persistir.
- **RED reproduzido:** receipt sem readback retornava `verified`; repetição do mesmo `operation_id` adicionava texto novamente. **GREEN:** testes de valor observado, ausência de efeito, takeover, navegação, recibo ausente, checkpoint falho e replay.

**Limite semântico:** observação do DOM verifica efeito local na página, não persistência remota. Operações externas (por exemplo, salvar um cartão em Trello) ainda exigem verificador externo/owner do domínio. Não promover um DOM toggle a conclusão de workflow externo.

## Entrega 2 — AXTree document fencing

**Commit:** `2673fedc6d`, `fix(browser): reject AX snapshots after document replacement`.

Arquivos: `workstation-browser-snapshot.ts`, `workstation-browser-snapshot.test.ts`, `workstation-browser-snapshot-object-lifetime.test.ts`.

- Captura `location.href` e `performance.timeOrigin` antes de adquirir a Accessibility Tree e junto aos metadados finais após resolver referências.
- Se URL ou identidade do documento mudarem durante o mapeamento, devolve `null` e o runtime utiliza `inventoryScript()` como fallback canônico. Preserva flag `HERMES_BROWSER_AXTREE_ENABLED` default-off.
- Mantém correções anteriores `dbf51de048`: `Runtime.releaseObjectGroup` em `finally` e refs `@e` monotônicas de SPA.
- **RED reproduzido:** mapeamento antigo + metadados de nova navegação aceitos como snapshot. **GREEN:** rejeita snapshot cruzado e preserva 12 testes focalizados.
- **Limite:** troca de documento de iframe sem troca do documento pai ainda requer E2E de frame/session/loaderId. AXTree continua experimental.

## Entrega 3 — Extração segura/cache

**Commit:** `7767410643`, `fix(browser): isolate extraction cache schemas and redact nested secrets`.

Arquivos: `workstation-browser-extract-cache.ts`, `workstation-browser-extract-cache.test.ts`.

- `computeQueryDigest()` inclui `schema`. Dois schemas diferentes com mesmo seletor/documento não reutilizam cache de projeção incompatível.
- `normalizeExtractedItem()` redige segredos também em arrays de objetos aninhados e limita profundidade de recursão.
- **RED reproduzido:** colisão do digest entre schemas e exposição de `api_token` dentro de array. **GREEN:** 11 testes focalizados de cache/extraction.
- **Risco residual:** o `documentFingerprint` atual no runtime usa título, URL, readyState, contagem de filhos diretos e `lastModified`. Isso não prova frescor em mutações assíncronas sem troca da contagem (SPA). O cache ainda deve ser tratado como **parcial**, com prioridade de substituir por revisões de MutationObserver/DOM digest revalidado ou bypass conservador antes de habilitar estratégia mais agressiva.

## Qualificação executada

| Verificação | Resultado |
|---|---|
| Vitest Browser/Electron focal expandido | **17 arquivos, 155 testes PASS, 0 FAIL**, última execução `node ../../node_modules/vitest/vitest.mjs run --config vitest.browser-native-audit.config.mjs` |
| RED → GREEN | ACK sem efeito; replay duplicado; AXTree com documento substituído; colisão de schemas; segredo em array |
| Typecheck puro de batch/cache | PASS com `tsc --ignoreConfig --noEmit --skipLibCheck --types node --module esnext --moduleResolution bundler --target es2022` |
| Typecheck Electron completo | **NV/BLOCKED**: `node_modules` local compartilhado do checkout não contém `electron`; falhou com TS2307 em múltiplos arquivos não alterados |
| E2E Chromium/Electron Windows | **NV**, executável/ambiente exato não disponibilizado na dependência local atual |
| GitHub CI exact-head do candidato | **NV**; sem autorização de promoção apenas por suítes locais |
| diff/whitespace e pre-commit hook | `git diff --check` e hooks de commit executados nos commits separados |
| Benchmark p50/p95 nativo, memória, CPU | **NV**; não inventar resultados |
| Custo/tokens efetivamente economizados | **NV**; nenhum fornecedor/modelo comparado neste ciclo |

A análise estática demonstra que o caminho AXTree continua realizando aproximadamente **duas chamadas CDP por nó resolvido** (`DOM.resolveNode` + `Runtime.callFunctionOn`), além de `Accessibility.enable`, `Accessibility.getFullAXTree` e `Runtime.releaseObjectGroup`, com duas leituras JS de documento. O readback de batch acrescenta duas avaliações de página por subação (antes/depois). Isso descreve overhead arquitetural, **não medição de tempo/custo**.

## Matriz code-to-code

| Referência | Mecanismo | Decisão | Estado |
|---|---|---|---|
| BrowserClaw MIT | batch serial | **ADAPT** na autoridade Electron existente | Já integrado; verdade de efeitos corrigida |
| Agent Browser | AXTree/document identity | **ADAPT** padrões de identidade via código Hermes | Parent-document fencing testado; iframe E2E pendente |
| Stagehand MIT | extração/cache | **ADAPT** no `browser_extract_items` existente | Schema e redaction corrigidos; fingerprint ainda parcial |
| BrowserOS AGPL-3.0 | diff/UX | **REIMPLEMENT PATTERN** independente | Delta já existe; sem cópia de código AGPL |
| browser-use Desktop | takeover/recuperação | **KEEP/ADAPT** owners existentes | Testes locais, native E2E pendente |
| Driftlock | drift diagnostics | **DIAGNOSE ONLY** | Sem auto-reparo cego |
| Chrome cookie import | sessão autenticada | **HOLD** | Revisão de segurança e consentimento por perfil/origem |
| Chromium customizado/novo broker | runtime paralelo | **REJECT** | Não implementado |

## UX e conflitos preservados

O checkout ativo `fix/hermes-oneclick-lock-startup-20261011` contém alterações não commitadas em `apps/desktop/src/app/browser/index.tsx`, `native-view-occlusion.ts`, respectivos testes e `workstation-browser-pane.tsx` (occlusion ownership, overlays e visibilidade). Esse trabalho foi **apenas lido**. Não portar/editar simultaneamente essas regiões sem reconciliação de HEAD e owner, para não sobrescrever outra trilha. Nenhuma mudança de UX foi reivindicada neste ciclo.

## Próximas etapas e decisão de release

1. **P0 durable exactly-once:** criar journal persistente de batch admission/steps, correlacionado ao `CertifiedDispatcher`, para cobrir efeitos com receipt perdido, concorrência e replay após outras mutações. Provar por failpoint/restart verdadeiro.
2. **P0 native E2E:** preparar dependência Electron exata e rodar Windows E2E com formulário, checkbox, SPA, takeover, restart, iframe/doc replacement e real readback de postcondições; só então classificar `DONE`.
3. **P1 cache correctness:** substituir fingerprint fraco por estado rastreável sob mutação dinâmica, sem custo inviável em páginas extensas; incluir negative tests de SPA com mesmo childElementCount, shadow DOM e iframe.
4. **P1 performance:** benchmark em fixtures controladas (sem writes em contas reais) comparando AX vs inventory, batch pré/pós, delta vs full, projeção model-facing, p50/p95, memória, CPU, chamadas CDP, bytes/tokens reais e sucesso externo verificado.
5. **P1 UX:** reconciliar mudanças concorrentes de occlusion/right rail antes de qualquer patch visual; E2E de foreground theft e lease.
6. **Release:** H-079/CI exact-head, Windows CI, security/licensing, regressões completas; até lá somente branch/PR sem merge para main.

**Não há ganho percentual de velocidade/custo verificado nesta sessão. Não utilizar os números do relatório de 10/10 como medições atuais.**
