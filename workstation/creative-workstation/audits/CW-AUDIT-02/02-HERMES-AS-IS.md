# 02 — Hermes atual: owners, funcionamento e lacunas

Base: origin/main a2b56db1bc, não confundir com PR #77. SOURCE_PRESENT não implica WIRED, REAL_E2E nem QUALIFIED. Arquivos e símbolos abaixo inspecionados no Windows.

| Subsistema | Símbolos verificados | Código oferece | Gaps reais |
|---|---|---|---|
| Documento | workstation/creative_document.py:29 Keyframe, :41 Layer, :58 Clip, :78 Track, :93 Asset, :124 Composition, :144 CreativeDocument, :252 document_to_dict, :322 load_document_from_dict | objeto e serialização Python | UI+agente no mesmo revision persistente não demonstrado |
| Tempo | creative_time.py e creative_timeline.py | RationalFps/CanonicalTime e fonte/timeline | testar source mapping e taxas mistas no render |
| Commands | creative_commands.py:32 CreativeCommand, :52 CommandRegistry, :62 execute, :227 layer, :275 property, :310 keyframe, :456–541 NLE | handlers e inverses | schemas descobertos/enabled(reason), ponte React e contexto do agente |
| Transações | creative_transactions.py:32 CreativeTransaction.apply, :74 CreativeHistory, :89 commit, :115 undo | clone e commit após sucesso, expected_revision | keys de idempotência e revision em RAM, CAS persistente concorrente não provado |
| Fonte/versões | creative_project_store.py:69 e :114 load_creative_revision, :177 save_creative_revision, :284 save document, :299 load document | digest de fontes, revision e perfil | LOAD DUPLICADO, histórico/revision no store e no objeto ainda não convergentes |
| Planos IA | creative_edit_plan.py:40 SemanticEditPlan, :58 Manager, :94 preview_plan, :107 validate, :126 apply_plan | clone preview e conflito por número | preview_document não é frame visual; read/write sets heurísticos |
| Cena | creative_scene_adapters.py:86 SvgVectorAdapter, :114 CanvasEffectAdapter, :133 ThreeJsSceneAdapter, :155 media, :187 CompositeScene | propriedades/descritores por tempo | Canvas/Three só retornam DICIONÁRIOS, não geram pixels |
| GLB | creative_3d.py:42 GLBAssetMetadata, :137 inspect_glb_bytes, :363 generate_threejs_canvas_dom | guardrails GLB/DOM | objeto+câmera não integrados ao projeto do renderer |
| Export | creative_export.py:88–110 _decode_frame_hash, :113 export_composition_to_video | MP4 via FFmpeg primeira fonte/fallback color | pseudo-hash e black fallback; recibo verified=true sem garantir composição |
| Motores | creative_render_adapters.py:76 RenderAdapter, :121 ElectronChromiumAdapter, :207 HyperFramesAdapter, :272 FFmpegWebCodecsAdapter | adapters/capabilities | provar mesmo revision/frame; cancelamento readback |
| Supervisão | creative_video_process.py:20 manifests, :45 executable, :90 ffmpeg/ffprobe | executor sob fingerprints | evitar spawn duplicado no export |
| Autoridade | Browser/TaskRun/ArtifactStore/policy existentes | escopo/journal/verificação | REUSAR, não criar store de permissão da UI |

## PR #77: editor visual real, owner separado
- CreativeWorkspacePage.tsx monta o provider, new/open JSON (branch feat/p0-creative-mvp-20261011).
- apps/desktop/src/app/creative-workspace/types.ts:3–52 descreve CreativeProject e Layer com text/shape/three_js_scene, mas declaração de tipo não prova render para todos os kinds.
- creative-mvp-model.ts:4–155 contém CreativeEdit, newCreativeProject, assertCreativeProject, applyCreativeEdit, sampledTransform e renderCreativeSvg.
- CreativeWorkspaceContext.tsx:42–105 usa useState/useRef, undoHistory/redoHistory e $creativeProject. Não há invocação da transação Python persistida nesses caminhos. O renderer possui uma segunda história e segunda mutação.
- Salvar JSON portátil é diferente de salvar revisão canônica. Frame SVG é diferente de PNG e MP4 decodificados. Não afirmar coedição do agente nem E2E Electron.
- São modelos TypeScript/Python diferentes; não permitir migração que perca native source, ids, mídia, layer metadata ou histórico.

## Código técnico que já precisa saneamento
1. creative_project_store.py:69,114: a segunda definição Python de load_creative_revision sombreia a primeira; unificar mantendo check completo de symlink, digest, schema, native files.
2. creative_scene_adapters.py:71 e creative_render_adapters.py:41 definem ambos RenderContext, contextos diferentes; normalizar ownership/nomes.
3. creative_scene_adapters.py:37 sanitize_svg_text + SVG escaping merece teste de double escape e de atributos untrusted.
4. creative_export.py:88–110 deve falhar ao não decodificar; arquivo faltante deve falhar (nunca lavfi black silencioso). Confirmar frames reais, duração/frame count, dimensões, A/V.
5. CreativeHistory armazena current_revision e idempotency_keys em memória; reconciliar com revision ID durável e command receipt.
6. Se a IA tenta r4 após ajuste humano em r5, responder conflito 409 + diffs, sem sobrescrever.
7. Fonte SVG/.ecproj nativa deve seguir editável/linked; recusar flatten ou unknown properties em perda.

## Estado e requisito para alegar produto
Falta comprovar um único percurso: gesto de mouse OU comando agente → mesma operação tipada → scoped authority → expectedRevision sob CAS → commit persistido/journal → preview da revisão → PNG/MP4 do mesmo snapshot → undo/redo coerente → reabertura equivalente.

CWN-02 typed Electron IPC e CWN-01 store/history convergidos devem vir antes de expansão de motores; P0 export verificador real. Testes negativos: concorrência humano vs IA, crash/restart, cancelamento e fonte ausente.
