# 09 — Respostas ao contrato de qualidade (10 perguntas)

**Nível de prova:** cada resposta separa código existente [S], inferência arquitetural [P] e condição ainda não demonstrada [HOLD]. Todos os arquivos e matrizes em 00–08 fazem parte desta entrega.

1. **O que falta para humano e Hermes editarem exatamente o mesmo projeto?**
[S] Python CreativeDocument/CreativeCommand/CreativeHistory/ProjectStore existem; PR77 usa CreativeProject TS, applyCreativeEdit e undo/useState próprios. [P] Um único command IPC com ProjectStore como dono persistente, schema versionado, actor scope, expectedRevision CAS, history durable, readback e UI subscription. [HOLD] Clique real→mesma mutação que agente→reabrir e desfazer sem divergência.

2. **Qual documento canônico para SVG, Canvas, vídeo, áudio e Three.js?**
[P] Reutilizar workstation/creative_document.py e seu store; registrar camadas e compositor de cena, referências por asset SHA, source nativo preserved, exact rational time, typed properties e opaque executable sandbox. SVG e Three são implementações de node renderer em cima dos mesmos IDs/tempo; clip traz source-time mapping e áudio. [HOLD] codec TS/Python roundtrip, imported native source fidelity e perfil.

3. **Melhor combinação para criar 2D, acrescentar 3D e só depois animar?**
[P] React/Electron com canvas de seleção, vector/SVG renderer para 2D, WebGL Three.js em origem isolada para 3D, shared scene graph+properties+time; frame compositor para PNG; keyframes/Graph+FFmpeg para vídeo. Não exigir migração de projeto a cada modo. Backend-neutral D-043 preservado.

4. **Que partes do EffectCraft dão maior evolução por esforço?**
[S] registry CommandSpec/check_params (commands/mod.rs:94,339), batch $N (batch.rs:16–106), history merge (history.rs:27,193,276), math easing/spatial (keyframe/lib.rs:167–541), graph handles (ui-egui/panels/graph.rs:188,601). [P] primeiro CONTRACT registry/batch; segundo math/keyframe/UI React; depois WRAP de engine efeitos somente se prova. Não copiar egui.

5. **Qual Graph Editor/keyframe e tempo?**
[P] CanonicalTime/RationalFps Hermes como clock; interpoladores temporal/spatial/velocity de EffectCraft; React Graph Editor e inspector emitindo mesmas CreativeCommand IDs. FilmCraft source mapping é referência NLE; não trocar Fraction por Tick sem benchmark. [HOLD] e2e two-actor keys/camera, roving, 29.97, speed graph e decoded MP4 identical evaluator.

6. **Qual pipeline export real PNG e vídeo?**
[S] Hermes possui RenderAdapter + FFmpeg e creative_export.py, mas _decode_frame_hash retorna hash sintético quando decode falha, e o exportador pode renderizar color black fallback. [P] pinned canonical revision, deterministic frame graph (SVG + WebGL + media), RGBA/PNG readback e frames ordenados por RationalFps para supervised FFmpeg; independent ffprobe+decode+pixel/oracle compare; never verified on decode error. [HOLD] vídeo GLB+vector+audio ainda não comprovado.

7. **O que incorporar/adaptar/deixar fora?**
[P] ADAPT_CONTRACT EffectCraft command/schema/batch, FilmCraft edit checks, Penpot semantic design; ADAPT_ALGORITHM EffectCraft keyframes/history, PhotoCraft CoW raster, VectorCraft vector geometry, Three.js scene; WRAP supervised Film/Effect/Remotion/Blender as qualified; KEEP_HERMES authority/document/revision/ffprobe/journal; REFERENCE_ONLY GPL tools and full egui UI. Licenças itemizadas em 01/05/08.

8. **Em que Hermes já é superior?**
[S] TaskRun, ScopedPolicy, human-authority handoff, ArtifactStore, journal, expectedRevision intent, structured source digests e process supervision são owners que referências visuais não substituem. [CAVEAT] CreativeHistory in-memory e fallback de export ainda requerem conserto; não chamar as garantias de documento total já qualificadas.

9. **Como IA opera sem navegar por coordenadas?**
[P] Expor list commands by families, describe schema of selected operations, query(selection, properties, revision), propose semantic edit plan, then execute one atomic typed batch with $N refs; bounded response com new IDs+revision+artifact evidence; clicks apenas para gestos humanos e operations não tipadas. Same RPC invokes same registry. Authority gate sempre valida no commit, não no prompt.

10. **Qual sequência mínima para produto utilizável sem refazer?**
CW02-01/02 schema+bridge; CW02-03 batched editing; CW02-04 asset import; CW02-05 real PNG; CW02-06 fail-closed verifier; CW02-07 GLB+camera; CW02-08 motion+Graph; CW02-09 MP4 decoded; CW02-10+ NLE/effects/prefabs. Cada gate tem testes RED→GREEN, arquivos de destino e rollback em 07. Prioridade real é integração do que já existe, não 306 efeitos novos.

## Cinco condições inegociáveis da primeira versão
- A mesma revisão é a fonte do que usuário vê, do que a IA modifica e do que a exportação usa.
- Projeto não perde layers, 3D sources, keyframes e history ao salvar/reabrir.
- Nenhuma mutação sem authority e nenhum conflito humano/IA é silenciosamente aceito.
- Nenhum PNG/MP4 recebe VERIFIED a partir de hash fabricado, fonte ausente ou frames não decodificados.
- Nenhuma engine especial assume propriedade independente do documento; a escolha de engine é verificável e reversível.

## Transparência
Entrega é **auditoria documental SOURCE_INSPECTED** e roadmap, não implementing PR dos recursos. Inclui fontes localmente inspecionadas e catálogo CW-AUDIT-01 com níveis distintos de confirmação. Não afirma compilar os 26 repositórios, nem fazer packaged Windows E2E, nem medir latência/VRAM/tokens. A qualidade de pesquisa é avaliada pelos paths+símbolos, gaps e testes prescritos; a qualidade do produto precisa provas adicionais.
