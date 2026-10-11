# 02 — Hermes Current State (CW-AUDIT-01)

**HEAD auditado:** `80e3a0724b1c939bfbcbb4801434fb31661eea70` (`feat/workstation-browser-optimization-c2c`) · **Pin D-043:** `f21e803b` · **Data:** 2026-10-11
**Método:** leitura direta `workstation/creative_*.py` + `workstation/tests/test_creative*.py` (22 suites, 98 testes `def test_`) + `apps/desktop/electron/workstation-creative-frame.ts` + D-043 docs. Vocabulário: FACT / PARTIAL / NOT_VERIFIED. Runtime NÃO modificado.

## Resumo executivo do estado
Hermes CW já possui fundação D-043 CWN-00..06 **IMPLEMENTADA E TESTADA localmente** (~260 KB python + 22 suites), mas com **duplicação crítica de owners** (timeline ×2, commands ×2, MP4 ×2, RenderContext ×2, sanitize ×3) e lacunas CWN-02/04/06/07. Nada está QUALIFIED em exact-head CI nesta branch (CI red histórica documentada em CWN_BASELINE.md). Electron creative-frame é escopo mínimo (SVG rect/circle/text → PNG).

## 2.1 Documento / tempo / timeline / NLE

| Módulo | Símbolos-chave | Status | Provas / lacunas |
|---|---|---|---|
| `workstation/creative_document.py` (15.7 KB) | `CreativeDocument,Composition,Track,Clip,Layer,Keyframe,Asset,Marker,create_empty_project,document_to_dict,load_document_from_dict` | IMPLEMENTADO_VERIFICADO | FACT: IDs 32-hex validados (`_ID_REGEX`), `schema_version=1` rejeita `>1` sem migração, `Clip.linked_clip_ids`, `Track.locked/muted/solo`, `Asset.sha256` obrigatório, rejeita inline base64. Lacuna D-043: sem masks/nested/effects-graph/parent-child/speed-ramps, sem `layer.move`, sem `preserve unknowns`, revisão fora do documento (`CreativeHistory.current_revision`) |
| `workstation/creative_time.py` (8.7 KB) | `RationalFps,CanonicalTime(Fraction),TimeRange,MediaTimeMap,format/parse_timecode` | IMPLEMENTADO_VERIFICADO | FACT: racional exato `Fraction`, `RationalFps(30000,1001)`, drop-frame SMPTE `HH:MM:SS:FF/;FF`, half-open `[start,end)`, rejeita NaN/Inf/negativo, `timeline_to_source` com speed ±/freeze. Lacuna: `source_duration/source_out` usam `float()` — deriva CWN-01 |
| `workstation/creative_timeline.py` (12.3 KB) | `split/trim/ripple_delete/slip/slide/roll/set_clip_speed_op` | IMPLEMENTADO_VERIFICADO | FACT: cobre 7 primitivas, `track.locked` fiscalizado, linked A/V simétrico em split/trim/slip/slide + ripple multitrack. Lacuna: `roll` não propaga linked, `set_speed(0→freeze)` não ajusta linked nem overlaps/transições, sem audio-mix |
| `workstation/creative_nle.py` (18.6 KB) | `Clip,Track,Timeline(float),add/trim/split/delete/reorder/transition/set_clip_audio/sanitize_svg` | IMPLEMENTADO_VERIFICADO mas LEGADO/DIVERGENTE | FACT: tempo `float`, sem `CanonicalTime/linked/speed`, `locked` não fiscalizado em trim/split/delete, ripple intra-track. Usado só por `creative_operations.py` (stack HyperFrames-DOM). **Duplicação: dois owners de timeline** |

## 2.2 Commands / transactions / operations / edit-plan (CWN-02/04)

| Módulo | Símbolos | Status | Provas / lacunas |
|---|---|---|---|
| `creative_commands.py` (24.8 KB) | `Actor,CreativeCommand,CommandResult,CommandRegistry,execute_command` — **19 comandos**: track.add/remove, clip.add/remove, layer.create/remove/setProperty, keyframe.set/remove, asset.import/remove, clip.split/trim/rippleDelete/slip/slide/roll/setSpeed (7), timeline.restoreTracks | IMPLEMENTADO_VERIFICADO | FACT: `actor_type human_mouse/hermes_agent/headless`, `idempotency_key`, `inverse_command` (NLE via snapshot grosso `restoreTracks`). Lacuna CWN-02: sem JSON schemas (`params["x"]` direto), sem `expectedRevision/scope` no comando (só na Transaction), sem `project.open/save,layer.move,history.undo/redo,render.*`, sem capabilities+denial reasons |
| `creative_transactions.py` (5.2 KB) | `CreativeTransaction{commands,expected_revision},CreativeHistory{current_revision,undo/redo,seen_idempotency}` | IMPLEMENTADO_VERIFICADO | FACT: atomic copy-on-write (`document_to_dict/load`), commit 409 em `expected_revision` mismatch, idempotência no-op, undo/redo via inverses. Lacuna: sem preview (está no edit-plan), sem branching, sem verifier receipts |
| `creative_operations.py` (33.7 KB) | `CreativeOperation{kind,project_id,parent_revision_id,params,operation_id,if_match},apply_creative_operation` — **18 kinds** HyperFrames-DOM | IMPLEMENTADO_VERIFICADO mas STACK PARALELA | FACT: opera `index.html+hyperframes.json` + `save_creative_revision(engine=hyperframes)` + ETag/if_match + ScopedPolicy + ArtifactStore+Journal. **Não usa CommandRegistry/CreativeDocument**; usa `creative_nle.Timeline` float. Duplica sanitize SVG/typo |
| `creative_edit_plan.py` (6.3 KB) | `SemanticEditPlan{plan_id,base_revision,intent,target_ids,commands,read/write_set,predicted_diff,state,preview_document,diagnostics,provenance},Manager` | IMPLEMENTADO_VERIFICADO | FACT: estados D-043 completos PROPOSED→PREVIEWED→VALIDATED→APPLIED/REJECTED/BLOCKED/PARTIAL/ROLLED_BACK, preview em clone isolado, subset→PARTIAL, rebase check. Lacuna: `predictedDiff={count,verbs,targets}` pobre, sem preconditions/validation estruturada, sem previewRevision persistida |

## 2.3 Store / runtime / render / scene / media / export / video / 3D / hyperframes (CWN-01/05/06)

| Módulo | Status | Notas FACT |
|---|---|---|
| `creative_project_store.py` (13.1 KB) `CreativeProjectRevision{etag},save/load_creative_revision,save/load_creative_document` | PARCIAL (bug estrutural) | FACT: `~/workstation/creative/projects/<id>/revisions/<rev>/{manifest,source.creative.json,native_files}`, sha256, ETag `rev-source`, `CreativeConflictError`. **DEFEITO: `load_creative_revision` definido 2× (L69 e L114), segunda sobrescreve; código morto**. Sem migração schema |
| `creative_project_runtime.py` (7.4 KB) `CreativeRunContext,save/publish_project_revision` | IMPLEMENTADO_VERIFICADO | FACT: fencing `creative_enabled+home+session+TaskRun running+claim_lock+workspace⊂profile`, ArtifactStore `creative.project-revision.v1`+Journal, erro incerto sem retry cego |
| `creative_render.py` (7.4 KB) `render_project_for_run` | IMPLEMENTADO_VERIFICADO (escopo antigo) | FACT: só PNG/SVG via `dispatch_workstation_browser_authoritative` + recibo browser-session.json + `inspect_creative_png`. Não conhece Document/CWN-06 seek/render/cancel |
| `creative_render_adapters.py` (13.3 KB) `RenderAdapter{prepare/seek/ready/snapshot/render/cancel/dispose}×5 engines` | PARCIAL | FACT: contrato + capabilities + `select_best` verificados; `Electron/FFmpeg.render` delegam a `creative_export` (real); `seek/snapshot` vazios; `HyperFramesAdapter.render success=False Not fully implemented`. **Duplicação: `RenderContext{fps:float}` vs `scene_adapters.RenderContext{fps:RationalFps}`** |
| `creative_scene_adapters.py` (10.2 KB) `SvgVector/CanvasEffect/ThreeJs/AudioVisualMediaAdapter,CompositeScene{from_composition,seek}` | IMPLEMENTADO_VERIFICADO | FACT: `render_at(t,frame)` determinístico, seed=`random+frame`, lerp keyframes, MediaTimeMap, fence traversal. CWN-05 seek/declared-vs-opaque provado. Sem mix áudio, sem masks/effects |
| `creative_media.py` (1.3 KB) `inspect_creative_png` | IMPLEMENTADO_VERIFICADO | FACT: Pillow, budgets 4096px/8MP/32MB, hash+dimensões; nunca certifica execução |
| `creative_export.py` (7.6 KB) `export_composition_to_video,cancel_active_render` | IMPLEMENTADO_VERIFICADO | FACT: FFmpeg real scale/pad/yuv420p+libx264, fallback lavfi testsrc, Popen timeout 30s, `_decode_frame_hash` 4 amostras, receipt verified, cancel via terminate. Lacuna: sem áudio, sem parity player-vs-export, `float(fps/duration)` |
| `creative_video*.py` (8.4+3.2+5.7 KB) `encode_still_video,inspect_video_probe/preview,CreativeVideoEngines` | IMPLEMENTADO_VERIFICADO | FACT: still→H.264 bounded 1-30s fps∈{15,24,25,30,60} ≤1800 frames faststart + ffprobe nb_frames==nb_read + mean_error≤6 + manifests pinados+sha + exige libx264 sem nonfree. **Duplicação: dois pipelines MP4 (video still vs export composition) sem owner único** |
| `creative_3d.py` (15.5 KB) `inspect_glb_bytes,create_minimal_valid_glb,generate_threejs_canvas_dom` | IMPLEMENTADO_VERIFICADO | FACT: parser GLB 2.0 real (magic/chunks JSON+BIN), budgets 16MB/1000nodes/500meshes, bloqueia http/file/../javascript/data, Blender opcional. Sem WebGPU real |
| `creative_hyperframes_render.py` (9.8 KB) `render_hyperframes_video` | IMPLEMENTADO_VERIFICADO | FACT: `node cli render -o`, approval guards, ProcessRegistry adopt+wait 180s, ffprobe, ArtifactStore `creative.hyperframes-video.v1`. **DEFEITO: `CreativeStudioError` referenciado sem import/definição — NameError em path timeout (verificar)** |
| `creative_apps.py`/`creative_process.py`/`creative_runtime.py`/`creative_studio_service.py` | IMPLEMENTADO_VERIFICADO | FACT: manifests engine+sha256+probe CLI; env sanitizado, absoluto sem .cmd/.bat/.ps1/.sh, adopt/kill sem órfãos; discovery passivo `locate_command` sem executar; studio `127.0.0.1:3032-3099` token 24B, readiness `/__hyperframes_config`. Sob D-043 studio é adapter |

## 2.4 Kernel / Electron / D-043
- `operational_kernel.py` (58 KB): PARTIAL/NOT_VERIFIED além L120 — nenhum verbo creative observado; creative usa ScopedPolicyEngine+TaskRun, não OperationalCapability registry. Único acoplamento: `capabilities.py:RuntimeCapabilityRegistry.inspect_creative → creative_runtime.inspect_creative_engines` (descoberta passiva).
- `apps/desktop/electron/workstation-creative-frame.ts` (189 linhas): IMPLEMENTADO_VERIFICADO mas MÍNIMO — só rect/circle/text→SVG→data URL→PNG + sha/dimensões. Sem Document/timeline/hf-seek/CWN-02..09.
- `apps/desktop/src/app/creative-workspace/` (9 ficheiros: Page/Context/Switcher/Timeline/Preview/Inspector/Toolbar/GraphEditor/css + teste): NOT_VERIFIED conteúdo (existência FACT via glob).
- D-043 `ENGINE_NEUTRAL_ARCHITECTURE_2026-10-10.md` (91 linhas): DESIGN_ONLY vigente — invariante mesmo documento + mesmos comandos; fases CWN-00..09.

## 2.5 Testes (22 suites / 98 testes)
`test_creative_time 9` (racional/SMPTE/map 2x/reverse/freeze) · `timeline 7` (split+linked, 2x, lock, ripple, slip/slide, roll, undo) · `document 4` · `commands 4` (mouse≡agent, falha passo3 sem mutação, undo byte-eq, revision+idempotência) · `edit_plan 4` · `scene_adapters 3` · `render_adapters 14` · `export 2` · `nle 10` · `operations 4` · `3d 10` · `project_store 3` · `project_runtime 2` · `process 2` · `apps/runtime 2+2` · `render/media/video_* 2+2+2+2` · `hyperframes_render 2` · `studio_service 6`. Todos afirmam PASS local em CWN_BASELINE.md; re-verificação exact-head CI nesta branch PENDENTE (fora do escopo read-only desta auditoria).

## Classificação por estado (para §12 roadmap)
- Implementado e verificado (local): document/time/timeline/commands/transactions/edit_plan/scene_adapters/export/video/3d/apps/process/runtime/studio.
- Implementado parcialmente: project_store (bug dup), render_adapters (stubs seek/snapshot, HyperFrames stub), operational acoplamento.
- Duplicado/divergente (pagar dívida antes de features): `creative_timeline ↔ creative_nle`, `creative_commands ↔ creative_operations`, `RenderContext ×2`, `sanitize_svg ×3`, `MP4 ×2`.
- Documentado mas não implementado: CWN-07 Graph Editor UI completa, CWN-08 Experience Compiler creative, CWN-09 effects avançados.
- Não verificado: conteúdo `creative-workspace/` React, exact-head CI nesta branch, perf p50/p95.
