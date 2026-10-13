# 08 — Remediação de Stage A para destravar C2C-I01–I06

**Estado do plano: NÃO EXECUTADO.** Pré-requisito obrigatório de `07-GATE-0-BLOCKED-2026-10-12.md`. O diagnóstico local constatou `main@a2b56db1` versus `upstream/main@835c3dd0`, merge-base/pin `66605471`, `963 ahead/245 behind`, com `tools/browser_tool.py` afetado. Ref remoto atual e CI exact-head **não comprovados**.

## Grupo A — Confirmar baseline remoto (sem alterar trabalho principal)

1. Em ambiente com acesso ao origin/upstream permitido pela política, executar `git fetch --no-tags origin main` e `git fetch --no-tags upstream main`. **Não trocar branch ou modificar HEAD em `C:\Github\hermes-agent`; não alterar refs de outros agentes.** Registrar sha de cada ref, commit date e merge-base. Se ferramenta negar rede, registrar bloqueio e **parar** (não forçar espelho/hack).
2. Inspecionar required checks de `main` com a plataforma GitHub Actions, **não apenas combined statuses antigos**. Workflows possíveis observados no checkout: `.github/workflows/workstation-ci.yml`, `workstation-browser-windows.yml`, `ci.yaml`, `e2e-desktop.yml`, `e2e-desktop-core.yml`, `windows-bundle-sdk.yml`. Determinar quais são required atualmente, usar API/check-runs que fornece status por **SHA de HEAD**. Se nenhum recibo => UNVERIFIED; jamais presumir PASS ou FAIL.
3. Auditar original `main` e branch auditada para diferenças semânticas no Browser. Não tomar `audit/browser-native-evidence-20261012@c39739a187` como release verde; alterações de telemetria e verificação serão porta separada depois de Stage A.
4. Selecionar **um pin novo imutável** a partir de upstream fetch; registrar hash e decisão. Exceção por upstream comprovadamente quebrado somente por decisão escrita do maintainer em CURRENT_STATE/journal e política H-079; uma autorização geral anterior não é exceção de release.

## Grupo B — Criar Stage A independente e re-adotar upstream verdadeiramente

1. Criar worktree novo de integração **do estado efetivamente escolhido de `main`**, e branch `integration/upstream-20261012-<pin-short>`. Não usar `git checkout main` no checkout sujo.
2. Executar true-history merge com `git merge --no-ff <pin>` apenas **dentro da branch de integração**. Nunca `git cherry-pick` em massa nem cópia de snapshots como substituto de ancestry.
3. Resolver conflitos semanticamente. Analisar `963 ahead/245 behind` no corte local: ao menos `tools/browser_tool.py` mudou upstream, e os owners canônicos de agent/tool/runtime requerem comparação atualizada. Projetar o menor seam possível; não usar `-X ours` ou `-X theirs` em conflitos sem revisão de lógica.
4. Reconciliar `workstation/first_party_seams.json`, `workstation/UPSTREAM_DELTA.md`, `workstation/PATCH_MANIFEST.md` e contratos de runtime. Dar atenção a `FPS-BROWSER-001`, `FPS-BROWSER-LEGACY`, `FPS-MODEL-001`, `FPS-RUN-001`, `FPS-DESKTOP-MAIN/PRELOAD`.
5. Disposição de `REMOVE` não é sinônimo de removido; verificar owner do route real, controller, adapter bootstrap, batch admission único e authority/lease sem ruptura.
6. Trazer semanticamente (quando ainda necessário) os reparos da H-079.2 em installer `pipless venv`, H-077 negative actual_delta, plataforma Windows e integração opcional Anthropic. Fonte histórica na doc H079_2; **revalidar no novo HEAD**, não cherry-pick sem contraste.

## Grupo C — Qualification ladder de Stage A

| Passo | Prova requerida | Evidência a anexar |
|---|---|---|
| C1 | SHA de pin é ancestral do HEAD integração; `merge-base HEAD <pin> == <pin>` | log de commit/ancestry e merge 2 parents |
| C2 | Seam auditoria no novo HEAD | lista de REMOVE cumpridos/devedores, 0 seam sem classificação, parity por contrato |
| C3 | Installer no Windows incluindo existing pipless venv com/sem uv | testes offline isolados e logs legíveis |
| C4 | Owner router único, fake ACK não produz verified, takeover fail-stop | RED→GREEN reais, resultados da Workstation suite |
| C5 | Typecheck Electron/desktop com dependencies válidas; browser mocks + E2E | logs de sucesso e comando executado |
| C6 | Windows Browser native real + H013/occlusion/ownership | duração/PID/tab leases, fixture web local, sem dados pessoais |
| C7 | Core patch dry-run, Python CI, dependências e regressões negativas | exit codes/logs + SHA |
| C8 | Required checks GitHub no exato candidate HEAD | workflow/run/check IDs com SHA igual ao HEAD; sem reutilizar CI de outro commit |
| C9 | Upstream drift final, sem trocar pin | ref final observado, classificação delta para próximo ciclo, decisão formal |

Nenhuma linha do checklist é provada pelo simples sucesso `156/156` do Vitest mock e `7/7` da telemetria isolada anteriores.

## Grupo D — Só então implementar C2C-I01..I06

1. Criar branch/feature worktree baseada **exatamente na integração Stage A verde** e declarar `BASELINE_QUALIFIED_SHA`. Deixar integração e feature como commits distintos.
2. Seguir `06-PROMPT-IMPLEMENTADOR.md`: `I01` harness Electron nativo → `I02` actionability → `I03` cache SPA → `I04` frame/cancelamento → `I05` telemetria/bench → `I06` journal durable exactly-once.
3. RED antes de GREEN por cenário, benchmark paritário no mesmo pin, commits pequenos sem push, canário de privacidade, flag defaults conservadoras.
4. Ao final exigir CI exact-head da branch, Windows native E2E e revisão do maintainer para autorizar PR/merge. Sem resultados completos permanecer `NOT_RELEASE_QUALIFIED`.

## Sequência de comandos — exemplos NÃO executados

Execute somente quando o acesso remoto e a política H-079 permitirem:

```powershell
git -C C:\Github\hermes-agent fetch --no-tags origin main
git -C C:\Github\hermes-agent fetch --no-tags upstream main
git -C C:\Github\hermes-agent rev-parse main
git -C C:\Github\hermes-agent rev-parse upstream/main
git -C C:\Github\hermes-agent merge-base main upstream/main
git -C C:\Github\hermes-agent rev-list --left-right --count main...upstream/main
# Escolher pin exato aqui, sem assumir que ref remoto é o mesmo da análise
git -C C:\Github\hermes-agent worktree add -b integration/upstream-20261012-PIN C:\Temp\hermes-playwright-stage-a MAIN_SHA
git -C C:\Temp\hermes-playwright-stage-a merge --no-ff PIN_SHA
# NÃO executar target runtime sem C1..C9 qualificados
```

**Regra final:** se baseline CI não comprovar GREEN, manter C2C-I01..I06 BLOQUEADOS; jamais ocultar FAIL com SKIP, nem declarar release por evidência documental.
