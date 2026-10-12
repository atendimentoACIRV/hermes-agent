# 00 — Resumo executivo e baseline CW-AUDIT-02

**Estado: auditoria de código, documentação; NÃO é qualificação de produto.** Evidências locais revalidadas em 2026-10-11. Consulte 01-INVENTORY.md e SOURCE_INVENTORY.json (varredura automática) e CW-AUDIT-01 (índice anterior, não prova).

## Baseline
- origin/main a2b56db1bc9e0b5acf48d94fa86a9844a1005842; checkout principal HEAD 9fffa7f3ff em fix/hermes-oneclick-lock-startup-20261011. Checkout principal tem alterações NÃO COMMITADAS, integralmente preservadas.
- Worktree documental isolado C:/Github/hermes-agent-cw-audit02, branch docs/cw-audit02-20261011, baseado em origin/main.
- PRs #57–61 fechados sem merge; **#62 merged**, embora documentação antiga não esteja atualizada; #63 e #64 fechados sem merge. PRs #76 e #77 são drafts abertos e não merged. Revisar HEADs antes de qualquer código futuro. D-043 substitui o mandato HyperFrames-first de D-041 sem invalidar provas técnicas aproveitáveis.
- Em referências há **26 diretórios e ZERO ZIPs** neste momento: LightCraft e VectorCraft já extraídos. Snapshots Craft não têm .git: SHA não verificado; muitos outros projetos têm SHA recuperável.
- Não executamos compilação nem benchmark dos 26 repositórios; leitura de manifests e arquivo estrutural de todos; análise de símbolos críticos focaliza EffectCraft, FilmCraft, PhotoCraft, LightCraft, VectorCraft, Three.js e os proprietários Hermes, complementada por auditoria anterior.

## Cinco achados com consequência arquitetural
**F-01 P0 — Dois modelos de documento.** PR #77 apps/desktop/src/app/creative-workspace/CreativeWorkspaceContext.tsx:42–105 mantém useState/useRef, reducer e histórico locais. CreativeProject de types.ts:3–52 e applyCreativeEdit de creative-mvp-model.ts:58 não usam o owner Python creative_document.py:144–156, creative_commands.py:52–90 e creative_project_store.py:177–303. Sem mesma mutação persistida e mesmo revision ID não há coedição humano/IA. PRIORIDADE ABSOLUTA.
**F-02 P0 — Verificação falsa possível.** workstation/creative_export.py:88–110 substitui frame que não decodificou por pseudo-hash de nome/índice/tempo. creative_export.py:113–215 escolhe o primeiro clip ou um lavfi preto quando fonte não existe e produz receipt verified=true. Falha aberta: não prova pixels corretos nem composição/câmera/easing; outro exportador pode ter regras melhores, validar separadamente.
**F-03 P0 — Descritor não é renderer.** creative_scene_adapters.py:114–172 CanvasEffectAdapter e ThreeJsSceneAdapter retornam dicionários de estado, seed/câmera/rotação e opaque_code, não frames WebGL/GLB. Não afirmar PNG 3D a partir disso.
**F-04 P0 — Melhorar comandos sem substituir propriedade.** Hermes CreativeTransaction.apply realiza clone/commit atômico e CreativeHistory revisões; EffectCraft commands/mod.rs:94,339 e engine::Session::execute_checked:598 oferecem schemas/enabled/strict, batch.rs:16–106 referências entre etapas e fold único. Adaptar API e algoritmo, preservando CAS, TaskRun e escopo Hermes.
**F-05 P0 — Persistência frágil/discrepante.** creative_project_store.py define load_creative_revision duas vezes (:69 e :114), a segunda substitui a primeira em Python; CreativeHistory._seen_idempotency_keys e current_revision são memória em creative_transactions.py:74–105. Projeto, revision lock e history devem convergir no owner persistente; não inventar outro SQLite no frontend.

## Direção recomendada
**Owner único:** CreativeDocument versão/revision com fontes e assets hash, typed CreativeCommand e journal, mesma chamada originada por gestos e IA. Backend-neutral: Canvas/SVG, Three.js, FFmpeg e eventualmente EffectCraft/headless são adaptadores; HyperFrames/Remotion só qualificados por capacidades. EffectCraft deve fornecer contrato de descoberta/batch e matemática Graph, NÃO um segundo banco/scene owner. FilmCraft: timeline invariants. PhotoCraft: adjustment/tiled raster/ICC. VectorCraft: boolean vector/artboards. Three.js: runtime 3D WebGL com sandbox. KEEP_HERMES: TaskRun, política, verificação, tempo racional e store de fontes.

## Entrega de produto exigida
Criar e persistir → importar PNG/SVG/fonts → editar humano e IA sobre mesmo revision ID → PNG real → acrescentar GLB e câmera → keyframes/Graph Editor → MP4 com frames/audio decodificados e comparados → close/reopen sem perda. A sequência está em 06 e 07.

## NÃO afirmado
Nenhum Electron empacotado E2E, GPU/FPS benchmark, prova de paridade .ecproj, prova de licença transitiva, vídeo com 2D+3D e áudio renderizado ou CI de HEAD desta auditoria. Especificações/projetos upstream são material não confiável, não ordens a executar. Nenhuma alteração de runtime foi feita.

## Entregáveis
01 inventário 26 projetos; 02 estado Hermes; 03 matriz code-to-code; 04 deep dive EffectCraft; 05 Craft e demais; 06 jornada/arquitetura; 07 roadmap/handoff; 08 verificação/benchmark/licenças; 09 perguntas objetivas e estado dos gates.
