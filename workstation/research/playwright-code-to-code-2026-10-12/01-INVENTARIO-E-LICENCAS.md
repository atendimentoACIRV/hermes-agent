# 01 — Inventário, licença e proveniência exata

**DATA DA LEITURA:** 2026-10-12. **REVISÃO:** código-fonte local inalterado, sem .git no diretório Playwright; não existe SHA de commit comprovado desse snapshot.
**VERSÃO DECLARADA PELO package.json:** 1.65.0-next. **LICENÇA RAIZ:** Apache-2.0; preservar copyright/NOTICE/termos e atribuições de código derivado.
**ALVO HERMES:** branch de auditoria documental derivada de c39739a1872e57c2033502b03314c781ab64ee12. Hashes de arquivo são SHA-256 **de bytes locais**, não hashes Git de commit.

## Playwright — origem absoluta C:\Github\hermes-agent\referências\02-Browser-Automacao-Web\playwright-main

| Caminho do snapshot | Linhas | SHA-256 integral |
|---|---:|---|
| packages/playwright-core/src/client/locator.ts | 532 | ab68bf2169e2a689f6e62f308b2364327b24b787828c158401a585bce5ff7130 |
| packages/playwright-core/src/server/frames.ts | 1929 | 49a0ccff949247199a835eb845434998bf71b62d4ca290c3c9a19a922163c972 |
| packages/playwright-core/src/server/progress.ts | 209 | 0770a2b225b77df82f0aefea8ca89b699ebb3e58eb4274771d5e0c0cf43aed01 |
| packages/playwright-core/src/server/selectors.ts | 96 | beaf4c3338e980fe1157bea0ff883f4192ac30ca042e7b4830dc48fdef117e2f |
| packages/playwright-core/src/server/chromium/crPage.ts | 1293 | 3a00461606c09088ebf5dbb9879fbca17f31cf532d2c0b9a678b6c93a9d394f6 |
| packages/playwright-core/src/server/trace/recorder/tracing.ts | 933 | fd458b39d81aa78f954cd24d98a05cafff871abf341684cb6b07e0ae4c7925d0 |
| packages/playwright-core/src/server/trace/recorder/snapshotter.ts | 182 | 39f30f20c404f344078d1ccc626023861a941fe9f1523917871c17636da95a1c |
| packages/playwright-core/src/server/trace/recorder/snapshotterInjected.ts | 690 | 5b636b83b0f3cdf327d0c68872d9fe9f84577330d256404159eec236531c052b |
| packages/playwright-core/src/server/har/harRecorder.ts | 162 | 767d5fd51cd457fdc11a2b754ca2834b2e82bea1eb6a4a8843a00fb7d92b4173 |
| packages/playwright-core/src/server/recorder.ts | 587 | c68e57a3fcce352c3ca62fafef26e5c5c99ed2adbef43bd7b14ef9eb59b709a4 |
| packages/playwright-core/src/tools/backend/snapshot.ts | 237 | 38bd014274aaff8270976f42d914b7d0c0ad8a98bb5c25dbcccca1c20346ac1c |
| packages/playwright-core/src/server/dom.ts | 1067 | 439313fa7be8a8b5837d34b391b8475ec0d159d697d3836f6ec0f79e641a35a6 |
| packages/injected/src/injectedScript.ts | 1942 | 599824b60d41b48e07eee4f83d00786e5fb956c8c2f260fd20d5dea424c63816 |
| packages/injected/src/roleSelectorEngine.ts | 222 | f5ac36e7cd00993740ba8cb48d29680dd4fd53298358ca88eb9efb87d4bd8268 |
| tests/electron/electron-webcontentsview.spec.ts | 33 | db7a1a4af2aa6abf43c6f8f290587f9221539497d31ee83b07697b4b8fa8a2c5 |
| tests/electron/electron-tracing.spec.ts | 68 | 52c43f58718ce64ff0e13a96f3f8958e91210b10787193f07bc8220266d545b1 |
| tests/electron/playwright.config.ts | 81 | a84bf23446e21cbc01c3da6ef96900aefd9e9023fd0e238b4b35c046f9524d44 |
| tests/electron/electronTest.ts | 127 | 5ba0127ab1788549e2c55528094fc3539ebf31bb2eb3a38895abe51ec692358b |
| packages/injected/src/selectorGenerator.ts | 564 | df20cc0274020d7594c6e336599728ad0c345cb929ad7be25d66974c1a58dd15 |
| tests/electron/electron-webcontentsview-app.js | 16 | 7121abf20f3c716e5c2033d9658413bc1c89279b271908a0aa3f9f05e4a32571 |
| LICENSE | 202 | 45873d00a0dd243596deb4aa23b2493b3d1f0671921bf2538ea431d7380220eb |
| NOTICE | 5 | 6d602191187b35b9b01d2cffa01c8469c2c8d9de8a96f1bf868e0f264f51c81d |
| package.json | 170 | d0c32e637cb53bd869e77a0fad6626e1f510bafd2066cb4813d988651150b2bf |

## Hermes — baseline auditado (worktree pai)

| Caminho da integração Hermes | Linhas | SHA-256 integral |
|---|---:|---|
| apps/desktop/electron/workstation-browser-runtime.ts | 4805 | bda6c925dc167ba282bb7220b6efae586dd449b119897505091b9da4b7771089 |
| apps/desktop/electron/workstation-browser-snapshot.ts | 237 | fbc61b7b26975f174c39b04d7161af6cb0271d35764949ed6a5171e2955777a4 |
| apps/desktop/electron/workstation-browser-batch.ts | 208 | 21cae4a38480528b5c38c0a1f739158955236a9318662fae5540f2e559906064 |
| apps/desktop/electron/workstation-browser-batch-proof.ts | 97 | 6a61c8b30e74c572ed4239830b8437af01675ce2c9d8b1e3f08adc6fd1f42b44 |
| apps/desktop/electron/workstation-browser-task.ts | 652 | 3cb9702defdbc676e5eab9f14aeaa86cb2fcd0215c1e1a6db44a1810806c8c99 |
| apps/desktop/electron/workstation-browser-extract-cache.ts | 170 | 1d33c7c2f67643bbcc979a63fd6f1a840b35639fa8acda4a7022c728548c1a7b |
| apps/desktop/electron/workstation-browser-snapshot-diff.ts | 122 | c4a8b9b07adeb9629ad64e36f805a7325726465b0d7c292e15932a75880c0c6c |
| apps/desktop/electron/workstation-browser-session-state.ts | 608 | 37052b2ec428941881fe708ee09d4115a97746a70c7170e02ecef0614b46cc2c |
| tools/browser_workstation.py | 948 | 55c528bb38912fc9e1ba2e85e3a1b1ae4e70e252a66cf527107e588c27048d41 |
| workstation/telemetry/browser_observation.py | 126 | 82d9895ffee0c7570afb5e40aa1a01a3e2f85908082bc3fa879db8bd06efd0a8 |
| workstation/operational_kernel.py | 1066 | 7e29bd5c822d6bb61abde38538d673ef541fbaac18b2c4f680910a5b717d7b3b |
| workstation/control_plane/verification.py | 420 | 6faefa84c3019c4fbbff819b92559727d31daa1b8fe9433aaf012a79c43da89a |
| workstation/browser_transaction.py | 59 | b649c25b73400950c50d2b9b6a97066f4ad1e70ee20886d10fb7ffe7c79932b5 |
| workstation/experience_compiler/progressive.py | 23 | d0276db86a991926f259b7c2d72d1eca9d2a418c110d33bd8b7145eb95acb94d |
| apps/desktop/electron/workstation-browser-runtime-task.test.ts | 1328 | ab2ab36ab4020807d588273e4836108aff86022ff5622ea49719b781fbb0d865 |
| apps/desktop/electron/workstation-browser-runtime-batch.test.ts | 545 | 456826db987080ca726df55d126efd9f1f7f9c654fd6d122a4332ee663c40397 |
| apps/desktop/electron/workstation-browser-snapshot.test.ts | 225 | 959cd61f174b8c171ef4334e46bf3e64246aa0bafab4e10abebabf31bff7d117 |

## Referências adjacentes e política de cópia

| Referência | Evidência local | Postura |
|---|---|---|
| browserbase--stagehand/LICENSE | SHA-256 74605fd9afe71584f0105826f2228694988b3593c876ed6c724adf67638725d6; 21 linhas | Stagehand local: MIT no LICENSE atual; relatório histórico da mesma árvore alega Apache-2.0 — conflito documental, usar arquivo atual |
| browserclaw-main/LICENSE | SHA-256 802291ad73ea5aaa400af23abf3fe0f45516ecd2b97329935e0df5c6e99678a5; 22 linhas | BrowserClaw: MIT; priorizar batch/authority semantics, não clonar seu runtime |
| vercel-labs--agent-browser/LICENSE | SHA-256 b93a9ab54e653b0640f7cc6d69b419334add5e3e1de83d08d79e4115abdc8358; 201 linhas | Agent Browser local: Apache-2.0; Rust snapshot e daemon incompatíveis como owner do Electron |
| browseros-ai--BrowserOS/LICENSE | SHA-256 6f1e622c82a380075843bb084a7ec3b1f1d12a4a02526d75e78b0924a860aa75; 661 linhas | BrowserOS: inspecionar licença exata; tratar código AGPL como fonte de ideias, não transplantar |

## Regras operacionais de licenciamento e reprodução
- **COPY permitido em tese:** pequenos fixtures e padrões de teste Playwright que possam ser transpostos para arquivo próprio com copyright/licença/NOTICE e dependências revisados. Nenhuma cópia literal foi efetuada nesta auditoria.
- **ADAPT:** reprojetar behavior/actionability, wait e mutation-revision nos owners Hermes; não extrair código Playwright com imports privados sem análise do grafo de dependências.
- **INSPIRE:** streaming de snapshots e tracing só como algoritmos sem raw DOM, cookies, HAR ou credentials; evitar cópia de instrumentação intrusiva de DOM.
- **REJECT:** Playwright/BrowserOS/daemon Rust como proprietário novo de sessão/browser; qualquer log de recursos/HTML/traces crus em telemetria regular.
- **Sem commit upstream:** snapshot Playwright sem .git; hashes na tabela são a proveniência reproduzível. Não atribuir a um hash/versão de GitHub não comprovado.

## Baseline / qualificação
- Leitura isolada, sem alterar Playwright, sem executar sites, sem browser alternativo.
- Pin ancestral do Hermes registrado nas auditorias anteriores: 66605471e9f0b0832abbefaf625ce08e948ca540, com upstream main observado 835c3dd038d903182a66ecc45e34bf5e0de65f00; upstream-first, H-079, native-E2E e exact-head CI continuam abertos.
- As diferenças são contra o **snapshot da branch c39739a187**, não equivalem a alegação universal sobre HEAD remoto durante esta execução.
