# EXECUTE BROW-NATIVE-NEXT — Hermes Workstation Browser Nativo

Você é o implementador principal no Windows do repositório `C:\Github\hermes-agent`. Sua missão é **EXECUTAR CÓDIGO**, não apenas auditar ou sugerir. Use os plugins Remote Desktop Commander, GitHub, Superpowers e community-agent-workflows. Aplique investigação code-to-code, plano/TEST FIRST/RED→GREEN/revisão/qualificação, preservando a autoridade canônica do runtime Electron.

## Contexto operacional confirmado em 12/10/2026

- O trabalho prévio de auditoria está em `workstation/research/browser-code-to-code-2026-10-10/`.
- Conciliação e política: `workstation/context/BROWSER_CODE_TO_CODE_DECISIONS_2026-10-10.md`, `workstation/context/UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md`, `workstation/AGENTS.md`.
- Relatório deste ciclo: `workstation/research/browser-native-followup-2026-10-12.md` na branch local `audit/browser-native-evidence-20261012` em `C:\Github\hermes-agent\.worktrees\browser-native-evidence-20261012`. Essa branch foi criada a partir de `main@a2b56db1bc9e0b5acf48d94fa86a9844a1005842`; confira HEADs atuais antes de agir.
- O checkout principal estava em `fix/hermes-oneclick-lock-startup-20261011` com alterações locais de outros agentes — NUNCA descartar, sobrescrever, resetar ou misturar essas modificações.
- `main` já integrou OPT-01 batch, OPT-02 AXTree experimental, OPT-03 extraction/cache, OPT-04 delta, OPT-06/09/12 resilience e UX via merge `c474b4ed93`. NÃO duplicar ferramentas, admission owners ou navegadores.
- Nesta branch foram corrigidos: (a) liberação de `DOM.resolveNode` handles via `Runtime.releaseObjectGroup` em `finally`; (b) refs `@e` alocados monotonicamente entre snapshots SPA. Os testes demonstraram RED antes e GREEN depois.
- Evidência local: Vitest Browser/Electron, 16 arquivos / 139 testes aprovados. `tsc` completo BLOQUEADO por dependência `electron` ausente no `node_modules` reutilizado; não afirmar typecheck verde. Não há exact-main-HEAD CI comprovado e o E2E nativo não foi executado.
- `BrowserOS` é AGPL-3.0: só padrões/reimplementação independente, nenhuma cópia de código. `browserclaw-main` e `browserbase--stagehand` têm LICENSE MIT no snapshot local; qualquer reutilização de trechos requer verificar licença, copyright, dependências e SHA/versão específica.
- Importação de cookies/credenciais do Chrome permanece HOLD por privacidade/segurança.

## Execução obrigatória, em ordem

### BROW-N0 — Isolamento, gate e estado

1. Confirme `git status`, `git worktree list`, `main`, `origin/main`, `upstream/main`, pin upstream, merge-base, as alterações já existentes e o escopo real de `AGENTS.md`. Confira journal H-079 `PASS_WITH_AUTHORIZATION` e limites. Caso o gate de release esteja vermelho, continue apenas em branch isolada, com feature flag OFF e marque `NOT_RELEASE_QUALIFIED`.
2. Leia integralmente os dois módulos alterados nesta branch, seu diff e testes; rode a suíte Browser focal e faça revisão independente. Concilie com eventuais novas alterações da `main` antes de portar qualquer código.
3. Não faça merge/push na main; não instale dependências sem necessidade; não automatize escrita em Trello/Instagram/WhatsApp reais como benchmark.

### BROW-N1 — P0: Corrigir falso VERIFIED em browser_batch_actions

1. Leia `apps/desktop/electron/workstation-browser-runtime.ts` (`executeControlRequest`, `verifyAfter` do lote), `workstation-browser-batch.ts`, `workstation-browser-task.ts`, `tools/browser_workstation.py`, `workstation/operational_kernel.py`, `CertifiedDispatcher` e verificadores existentes.
2. Escreva teste RED reproduzindo `perform()` com ACK e `BrowserOwnerReceipt` gravado, porém sem alteração real/sem readback. Hoje `verified: Boolean(receiptRef)` permite falso positivo; o teste deve exigir `UNCERTAIN` e interrupção do restante, sem retentativa cega.
3. Implemente readback independente e pós-condições explícitas por tipo de ação. Para inputs, comparar estado esperado reobservado com o DOM e documento/revision corretos; para click/press/scroll, não declarar VERIFIED sem evidência suficiente; quando a pós-condição não puder ser comprovada, estado `UNCERTAIN`. Preserve `ACKNOWLEDGED` distinto de `VERIFIED`. Verifique antes de cada step lease, owner, tab, run, policy, URL/document epoch, foreground ownership; `409 USER_CONTROL_ACTIVE` sempre vence.
4. Adicione testes de navegação durante batch, DOM que muda entre ação e readback, takeover no passo 2, crash em checkpoint, perda de receipt e reentrada com operation ID. Nunca gerar `verified` fictício para manter testes antigos verdes.
5. Faça um PR pequeno por contrato/owner, não misture com otimização estética.

### BROW-N2 — P0/P1: Qualificar AXTree sob carga e identidade

1. Amplie testes reais para Shadow DOM, iframe cross-origin, SPAs com DOM recriado em mesmo URL, contenteditable, canvas e páginas volumosas, incluindo troca de documentos em iframe (comparar testes de `vercel-labs--agent-browser/cli/src/native/snapshot.rs`).
2. Valide `objectGroup` e `Runtime.releaseObjectGroup` em sucesso, exceções e debugger detach; preserve fallback para `inventoryScript` e feature flag default-off.
3. Meça p50/p95 de latência, RAM do renderer, CPU, CDP roundtrips, bytes/tokens observados e taxa de identificação correta de alvo; contabilize as duas chamadas por elemento (`DOM.resolveNode`, `Runtime.callFunctionOn`) e a chamada final de release. Se não provar melhora, NÃO ativar a flag em produção.
4. Detecte referências obsoletas, ausência de documento e diferenças de `documentEpoch`; previna reuso entre aba/task/frame/session.
5. Use as referências somente conforme licença; não criar outro navegador ou service broker.

### BROW-N3 — P1: Custos, extração e espera em páginas dinâmicas

1. Compare `browser_extract_items` e `workstation-browser-extract-cache.ts` com Stagehand; validar mutações assíncronas, cache A→B→A, papéis de origem, token-redaction, auth walls e schemas; não criar `browser_extract` concorrente.
2. Benchmark das políticas de auto-snapshot, delta e compactação model-facing; reconcilie com a trilha existente `tools/browser_workstation.py::project_model_browser_payload`, sem sobrescrever ajustes não commitados de outros agentes.
3. Substitua delays fixos por espera baseada em sinais/document readiness somente com teste RED e prova de melhoria; não adicionar polling paralelo.

### BROW-N4 — P1/P2: UX nativa humana + agente

1. Faça diff e reconciliação do Browser Hub e right rail: `apps/desktop/src/app/browser/index.tsx`, `native-view-occlusion.ts`, `workstation-browser-pane.tsx`, `TaskJournalDrawer`, `WebContentsView` ownership. Esses arquivos estavam sujos no checkout principal: preserve mudanças e não inicie refactor em cima de patch alheio.
2. Qualifique indicadores de alvo/progresso, takeover, foreground, tarefa em segundo plano, recuperação pós-restart, troca de abas sem foreground theft, modal/overlay de oclusão e indisponibilidade sem UX ilusória.
3. Estados de interface sempre projeções dos owners TaskRun/BrowserTask; UX jamais decide autoridade. Inspire-se nos padrões BrowserOS sem copiar AGPL.

### BROW-N5 — Qualificação final e entrega

- Rodar RED→GREEN para cada mudança; suítes Browser/Electron/Python, `git diff --check`, typecheck com dependências qualificadas, lint, Windows native E2E, takeover, recovery, benchmark de p50/p95, memory-soak e CI exact-head.
- Registrar testes por SHA, comandos e saída, environment blockers, cobertura, licença de cada trecho transferido, flags e rollback. Não repetir números de ganho da auditoria como resultado medido.
- Atualizar `workstation/ROADMAP.md`, `workstation/context/engineering-journal/CURRENT.md`, `workstation/context/HERMES_WORKSTATION_INTELLIGENCE.md` e o relatório deste ciclo **somente** conforme o estado real; evitar sobrescrever edições concorrentes.
- Preparar commits e PRs pequenos em branches isoladas; sem merge em main sem gates verdes e autoridade correta.
- Entregar matriz `COPY/ADAPT/REIMPLEMENT/KEEP/REJECT/HOLD` com origem e destino por símbolo; problemas reproduzidos; diffs, commits, tests RED/GREEN, E2E, p50/p95, custo real ou NV, riscos residuais e próximo trabalho por ROI.

**Regra absoluta:** não duplicar OPTs já presentes, não confundir receipt com prova de efeito, não usar fallback para navegador/perfil diferente após binding e não declarar DONE/release verde enquanto faltarem E2E ou exact-head CI. Prossiga automaticamente pelas fases seguras; qualquer gate bloqueado deve virar evidência e deixar código atrás de flag, não um atalho.
