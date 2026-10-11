# OPT-07 / OPT-11 — Classificação de backends Python e diagnóstico de drift

**Status:** DIAGNOSED / NO RUNTIME CHANGE (docs-only)
**Data:** 2026-10-11
**Branch:** `feat/workstation-browser-optimization-c2c`
**Autoridade:** `BROWSER_CODE_TO_CODE_DECISIONS_2026-10-10.md` (OPT-07 = DIAGNOSE ONLY, OPT-11 = CLASSIFY FIRST), Gate 8 do plano.

---

## 1. Decisão de engenharia

**Nenhum arquivo Python foi removido, fundido ou teve comportamento alterado.**

A auditoria externa sugeriu redundância aparente entre arquivos `browser*.py`.
A verificação confirma: contagem de arquivos não equivale a concorrência de
runtimes. Existem **2 runtimes sempre presentes**, ambos com owners distintos e
legítimos, mais drivers opcionais sob demanda, roteadores, fachadas de
ferramentas, guardas de política e suporte. Remover ou fundir qualquer um
deles sem prova de equivalência violaria D-BROW-01 (preserve os proprietários
canônicos) e quebraria fallbacks necessários.

Da mesma forma, o tratamento de drift (OPT-07) já possui fronteiras de
quarentena fail-closed. Nenhum reparo automático foi adicionado e nenhuma
operação antes bloqueada foi promovida. Diagnóstico cosmético vs. estrutural
abaixo (§4); quarentena existente preservada (§5).

Rollback: reverter este documento. Nenhum runtime, registro, schema ou teste
foi tocado por este item.

---

## 2. OPT-11 — Classificação dos 32 arquivos `browser*.py`

Metodologia: leitura de docstring, imports, classes/funções de topo e chamadas
de registro de cada arquivo; verificação pontual de delegação
(`browser_workstation.py`, `browser_extension_router.py`,
`browser_tool_lightpanda_fallback.py`, `operational_capabilities.py`).

Buckets: `RUNTIME_OWNER` (detém sessão/tab/task viva ou processo de browser),
`ROUTER` (despacha entre owners), `TOOL_FACADE` (registro/schema fino),
`BACKEND_DRIVER` (backend alternativo sob demanda), `POLICY_GUARD`
(política/consentimento/origem, sem execução), `SUPPORT` (estado, readiness,
projeção, supervisão, install, segredos).

| Arquivo | Linhas | Bucket | Delega para | Responsabilidade |
|---|---|---|---|---|
| `tools/browser_tool.py` | 1585 | RUNTIME_OWNER | próprio (daemons agent-browser) | Runtime local agent-browser + tabelas de sessão; prefere rota Workstation |
| `tools/browser_tool_session.py` | 942 | RUNTIME_OWNER | próprio (mesmo runtime) | Mesmo runtime, arquivo-irmão: spawn de daemon, create/exec por backend |
| `tools/browser_tool_lifecycle.py` | 773 | SUPPORT | tabela de `tools.browser_tool` | Zelador do mesmo runtime: reap por inatividade, órfãos, teardown, atexit |
| `tools/browser_workstation.py` | 907 | ROUTER | `WorkstationBrowserController` → legacy `browser_tool` | Rota do browser interno: prefere loopback Electron, bind de task fail-closed; registra `browser_batch_actions` (OPT-01) |
| `tools/browser_use_cli.py` | 840 | BACKEND_DRIVER | harness próprio; CDP resolvido | Backend Browser-Use: ferramenta `browser_exec`, daemons do harness |
| `tools/browser_vault_tool.py` | 770 | TOOL_FACADE | socket `SUPERVISOR_REGISTRY` + vault local | Autofill de segredos (list/fill/save); origin-match, segredos invisíveis ao modelo |
| `tools/browser_camofox.py` | 601 | BACKEND_DRIVER | servidor Camofox (REST :9377) | Backend Firefox anti-detect via REST; sessões por task |
| `tools/browser_supervisor.py` | 567 | SUPPORT | endpoint CDP resolvido | Supervisor CDP persistente por task (diálogos + frames); alimenta snapshot/diálogos |
| `tools/browser_cdp_tool.py` | 410 | TOOL_FACADE | socket do supervisor / CDP resolvido | Registro `browser_cdp`; passthrough CDP com redação + roteamento de frames |
| `tools/browser_tool_real_profile.py` | 344 | BACKEND_DRIVER | binário Chrome local + attach do daemon | Lane real-profile: cópia snapshot do perfil, lança Chrome, anexa daemon |
| `tools/browser_lightpanda.py` | 340 | BACKEND_DRIVER | próprio (`lightpanda serve`) | Engine Lightpanda: um processo serve por sessão, URL CDP, helpers ready/terminate |
| `tools/browser_supervisor_dialogs.py` | 307 | SUPPORT | `CDPSupervisor` | Mixin de diálogos: captura nativa + bridge Fetch, fila `PendingDialog` |
| `tools/browser_tool_cloud.py` | 268 | BACKEND_DRIVER | providers de plugin | Lane cloud: resolve/cache de provider, seleção backend/engine/headed |
| `tools/browser_tool_lightpanda_fallback.py` | 200 | ROUTER | `tools.browser_tool` (Chrome) | Roteador de fallback: retenta no Chrome comandos que o LP não serve |
| `tools/browser_tool_install.py` | 185 | SUPPORT | PM + PATH | Descoberta/aquisição de agent-browser/Chromium, checks de readiness |
| `tools/browser_extension_router.py` | 174 | ROUTER | `gateway.browser_control_broker` → legacy | Despacho extensão-vs-legacy; lane de identidade vinculada, fail-closed |
| `tools/browser_tool_eval_policy.py` | 167 | POLICY_GUARD | — (guarda exec de sessão) | Política `browser_console`: guarda SSRF, sondas de URL privada, denylist |
| `tools/browser_supervisor_frames.py` | 166 | SUPPORT | `CDPSupervisor` | Mixin de frames: tracking OOPIF/Target, payload `frame_tree` limitado |
| `tools/browser_supervisor_capture.py` | 161 | SUPPORT | `SUPERVISOR_REGISTRY` | `CapturedCDP`: handle WS fixo para plugins in-process; invalida em reconnect |
| `tools/browser_tool_vision.py` | 144 | SUPPORT | exec de `tools.browser_tool` | Helpers de visão: pré-rota de screenshot LP→Chrome, análise LLM auxiliar |
| `tools/browser_tool_cdp.py` | 134 | SUPPORT | URL CDP do usuário; `SUPERVISOR_REGISTRY` | Resolução de override CDP (`/json/version`) + ciclo de vida do supervisor por task |
| `tools/browser_tool_snapshot.py` | 125 | SUPPORT | `tools.browser_tool` | Pós-processamento de snapshot: truncate-store, redação de segredos, recover de screenshot |
| `tools/browser_dialog_tool.py` | 109 | TOOL_FACADE | registro `tools/browser_supervisor` | Registro `browser_dialog`: responde diálogos JS capturados pelo supervisor |
| `tools/browser_tool_origin.py` | 87 | SUPPORT | `tools.browser_tool` | Proxy lazy do módulo de origem: irmãos leem estado da fachada sem ciclo |
| `tools/browser_camofox_state.py` | 27 | SUPPORT | `tools/browser_camofox` | Identidade Camofox: dir de estado por perfil, userId/sessionKey determinísticos |
| `workstation/browser_session.py` | 332 | RUNTIME_OWNER | `WorkstationBrowserController` / Electron | Sessão Workstation + leases de takeover humano (Chromium/Preview/Lightpanda) |
| `workstation/browser_supervisor.py` | 302 | SUPPORT | controller (loopback) | Supervisor do controller Electron: heartbeat, descritores stale, backoff/breaker |
| `workstation/browser_readiness.py` | 173 | SUPPORT | qualquer owner via `evaluate_fn` | Probes semânticas de readiness (seletor/texto/assentamento); substitui sleep |
| `workstation/browser_projection.py` | 167 | SUPPORT | rota genérica via broker | Projeta extrações em WorkItems/artefatos duráveis + forma compacta |
| `workstation/browser_bridge.py` | 121 | SUPPORT | `evaluate_fn` do chamador | Extração DOM/JS → workspace/ArtifactStore sem round-trip de chat/base64 |
| `workstation/browser_transaction.py` | 59 | POLICY_GUARD | contratos das ferramentas owner | Admissão de transação UI: fases por contrato + força de evidência semântica |
| `workstation/browser_runtime.py` | 34 | SUPPORT | — (impl em `apps/desktop`) | Contrato abstrato `BrowserRuntime`: kinds + interface de capability/health |

### Veredito OPT-11

- **Runtimes sempre presentes (2):** (1) runtime local agent-browser
  (`browser_tool.py` + irmãos `session`/`lifecycle` = **um** runtime em três
  arquivos, não três runtimes); (2) runtime Workstation Electron (processo do
  Desktop; lado Python = roteador `tools/browser_workstation.py` + leases em
  `workstation/browser_session.py` + `workstation/browser_supervisor.py` +
  controller em `workstation/integrations/hermes/browser_controller.py`).
- **Drivers opcionais sob demanda** (só mantêm estado vivo se configurados):
  Camofox, `lightpanda serve`, Chrome real-profile, sessões cloud, harness
  Browser-Use. Revisados um a um; nenhum fallback necessário foi removido.
- **Roteadores/fachadas (não runtimes):** `browser_workstation`,
  `browser_extension_router`, `browser_tool_lightpanda_fallback`,
  `browser_cdp_tool`, `browser_dialog_tool`, `browser_vault_tool`.
- **Nada é removível com segurança:** splits/mixins (`origin`, `snapshot`,
  `vision`, `capture`, `frames`, `dialogs`, `runtime`) são pequenos e
  load-bearing; os dois núcleos de runtime, ambos os roteadores, o supervisor
  Electron + fencing de lease e as três fronteiras de política/segredo
  (`eval_policy`, `transaction`, `vault` + redação de snapshot) devem ser
  preservados.

---

## 3. OPT-07 — Inventário do tratamento de drift existente

| Mecanismo | Local | Papel verificado |
|---|---|---|
| Registro versionado + `record_drift` / quarentena | `workstation/operational_capabilities.py` L297 `register`, L403 `promote`, L418 `record_drift` | Capabilities com ciclo de vida; drift registra e quarentena sem autopromoção |
| Gate de saúde no roteamento | `workstation/control_plane/router.py` (checks `drift_state != "healthy"`), `dispatcher.py` (invalida certificado em drift) | Pré-voo revalida; drift invalida certificado |
| Deriva de verificador | `workstation/control_plane/verification.py` (`verifier_fingerprint_drift`, `STALE`) | Fingerprint esperado vs. atual; divergência = STALE, não sucesso |
| Composição/métricas | `workstation/control_plane/composition.py`, `metrics.py` (`verifier_quarantines`, `stale_task_run_count`) | Quarentenas e runs stale contabilizados |
| Drift de DOM em readiness | `workstation/browser_readiness.py` (códigos `dom_drift`/`DOM_DRIFT`) | Mudança de interface classificada durante probes |
| Descritores stale do supervisor | `workstation/browser_supervisor.py` (`DESCRIPTOR_STALE`, limpeza de PIDs mortos) | Limpeza de descritores de processo morto |
| Supersessão de autoridade | `workstation/authority_supersession.py` (`stale_task_run`) | Run stale supersedido com checkpoint, sem retomar mutação insegura |
| Transação UI | `workstation/browser_transaction.py` | Admissão por contrato; evidência semântica, sem auto-reparo |

---

## 4. Diagnóstico cosmético vs. estrutural (OPT-07)

- **Cosmético (observar, não reparar):** mudança de texto/ordem de elementos sem
  alterar alvo de ação; `snapshot-delta` (OPT-04) já trata como projeção de
  view; `browser_readiness` re-sonda em vez de falhar.
- **Estrutural (fail-closed):** troca de documento/aba/perfil, auth wall,
  challenge, revisão de mutação — invalidam cache (OPT-03), delta (OPT-04) e
  certificados de dispatch; `409 USER_CONTROL_ACTIVE` e leases preservados;
  nenhuma operação antes bloqueada foi autorizada automaticamente.
- **Lacuna concreta? Não demonstrada.** Por isso nenhum watchdog paralelo,
  nenhum polling adicional e nenhum reparo automático foi instalado, conforme
  Gate 6/8. Primeiro reproduzir defeito com teste RED; depois a menor correção.

---

## 5. Critérios de aceite OPT-07/11

- [x] Cada um dos 32 arquivos classificado por responsabilidade (tabela §2).
- [x] Rotas de delegação dos dois roteadores principais verificadas no código.
- [x] Mecanismos de drift/quarentena inventariados sem alteração (§3).
- [x] Diagnóstico cosmético vs. estrutural registrado sem autopromoção (§4).
- [x] Zero arquivos Python removidos/fundidos; zero mudança de comportamento.
- [x] Segredos/cookies/tokens fora de traces, relatórios e caches (inalterado).
- [x] Rollback = reverter este documento.

---

## 6. Pendências (ciclos futuros, fora deste item)

1. Reavaliação na próxima sincronia upstream (seams novos exigem
   classificação; proibido criar seams não classificados).
2. OPT-05 permanece HOLD (ver `OPT_05_CHROME_IMPORT_SECURITY_EVALUATION.md`).
3. Qualificação exact-head CI / E2E Windows nativo antes de qualquer merge na
   `main` (BROW-QUAL); sem merge automático.
