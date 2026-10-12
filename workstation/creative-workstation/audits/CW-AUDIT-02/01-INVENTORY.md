# CW-AUDIT-02 — Inventário revalidado das referências

**Método:** leitura de manifests/licenças de raiz e amostragem estrutural de código; NÃO demonstra teste funcional, licença transitiva nem benchmark.

**Diretórios presentes:** 26. **ZIPs presentes:** 0.

| Projeto | Licença preliminar e fonte | Revisão | Marcadores raiz |
|---|---|---|---|
| blender--blender | GPL [COPYING] | aed2b5972fc25ca8 | pyproject.toml, COPYING, README.md |
| BOMWiki--partmode | AGPL-3.0-only [package.json] | fe88558a34c8d7a3 | package.json, LICENSE, README.md |
| effectcraft-main | MIT OR Apache-2.0 [Cargo.toml] | snapshot / SHA not verified | Cargo.toml, NOTICE, ATTRIBUTION.md, README.md |
| FFmpeg--FFmpeg | GPL [LICENSE.md] | 1f7228e4fcc49230 | LICENSE.md, README.md |
| filmcraft-main | MIT OR Apache-2.0 [Cargo.toml] | snapshot / SHA not verified | Cargo.toml, NOTICE, ATTRIBUTION.md, README.md |
| GNOME--gimp | GPL [LICENSE] | 0774955bfe1c5318 | LICENSE, COPYING |
| godotengine--godot | UNRESOLVED [LICENSE.txt] | 232e6b14abf6e590 | pyproject.toml, LICENSE.txt, README.md |
| GraphiteEditor--Graphite | MIT OR Apache-2.0 [Cargo.toml] | 7477cd2fab315494 | Cargo.toml, README.md |
| inkscape--inkscape | UNVERIFIED (root license not identified) | 1232eac68aff1297 | README.md |
| KDE--krita | GPL [COPYING] | 3ee2270d8ead3696 | COPYING, README.md |
| lightcraft-main | MIT OR Apache-2.0 [Cargo.toml] | snapshot / SHA not verified | Cargo.toml, NOTICE, README.md |
| mrdoob--three.js | MIT [package.json] | 11738a9d55e502fb | package.json, LICENSE, README.md |
| Natron-RB-2.6 | GPL [LICENSE.txt] | snapshot / SHA not verified | LICENSE.txt, README.md |
| openreel-video-main | MIT [package.json] | snapshot / SHA not verified | package.json, pnpm-workspace.yaml, LICENSE, README.md |
| penpot--penpot | MPL-2.0 [package.json] | 10955f17e2794342 | package.json, pnpm-workspace.yaml, LICENSE, README.md |
| penpot--penpot-ai-kit | CC-BY-4.0 [package.json] | fe4f99e51c714951 | package.json, LICENSE, README.md |
| photocraft-main | MIT OR Apache-2.0 [Cargo.toml] | snapshot / SHA not verified | Cargo.toml, NOTICE, ATTRIBUTION.md, README.md |
| pixijs--pixijs | MIT [package.json] | 65552017d23255c1 | package.json, LICENSE, README.md |
| processing--p5.js | LGPL-2.1 [package.json] | 8ae967b59c491509 | package.json, LICENSE.txt, README.md |
| remotion-dev--remotion | SEE LICENSE IN LICENSE.md [package.json] | 32af7e8f8ac67493 | package.json, LICENSE.md, README.md |
| remotion-dev--skills | UNVERIFIED (root license not identified) | 32b241b97f4e0e4a | package.json, README.md |
| scribusproject--scribus | GPL [COPYING] | 969c3fe4bedbd394 | COPYING, README.md |
| sgenoud--replicad | MIT [package.json] | e4b05f67dc4e2393 | package.json, LICENSE, README.md |
| tidalcycles--strudel | AGPL [LICENSE] | 8a8ae9ac9659509a | LICENSE, README.md |
| Tonejs--Tone.js | MIT [package.json] | de9df332ca7573b9 | package.json, LICENSE.md, README.md |
| vectorcraft-main | MIT OR Apache-2.0 [Cargo.toml] | snapshot / SHA not verified | Cargo.toml, NOTICE, README.md |

## Superfícies candidatas observadas por projeto

### blender--blender
- Revisão: aed2b5972fc25ca8; licença preliminar: GPL [COPYING]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: pyproject.toml, COPYING, README.md.
- Candidatos: doc/blender_file_format/BlendFileDnaExporter_25.py, doc/python_api/examples/bpy.types.bpy_struct.keyframe_insert.0.py, doc/python_api/examples/bpy.types.bpy_struct.keyframe_insert.1.py, doc/python_api/examples/bpy.types.Depsgraph.1.py, doc/python_api/examples/bpy.types.Depsgraph.2.py, doc/python_api/examples/bpy.types.Depsgraph.3.py, doc/python_api/examples/bpy.types.Depsgraph.4.py, doc/python_api/examples/bpy.types.Depsgraph.5.py, doc/python_api/examples/bpy.types.Depsgraph.6.py, doc/python_api/examples/bpy.types.Depsgraph.7.py.

### BOMWiki--partmode
- Revisão: fe88558a34c8d7a3; licença preliminar: AGPL-3.0-only [package.json]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: package.json, LICENSE, README.md.
- Candidatos: scripts/step-export-determinism-smoke.ts, scripts/studio-assembly-features-document-smoke.ts, scripts/studio-document-history-smoke.ts, scripts/studio-offset-feature-history-smoke.ts, scripts/studio-pattern-feature-history-smoke.ts, scripts/studio-profile-feature-history-smoke.ts, scripts/studio-project-bundle-smoke.ts, scripts/studio-scene-settings-smoke.ts, scripts/studio-sketch-constraint-editor-smoke.ts, scripts/studio-thread-document-smoke.ts.

### effectcraft-main
- Revisão: snapshot / SHA not verified; licença preliminar: MIT OR Apache-2.0 [Cargo.toml]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: Cargo.toml, NOTICE, ATTRIBUTION.md, README.md.
- Candidatos: crates/engine/scripts/Render Queue Batch.jsx, crates/engine/src/history.rs, crates/engine/src/render_queue.rs, crates/engine/src/tests_frame_export.rs, crates/engine/src/tests_history.rs, crates/engine/src/tests_project_items.rs, crates/engine/src/tests_timeline.rs, crates/engine/src/tests_timeline_interchange.rs, crates/engine/src/xml_project.rs, crates/engine/src/commands/align.rs.

### FFmpeg--FFmpeg
- Revisão: 1f7228e4fcc49230; licença preliminar: GPL [LICENSE.md]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: LICENSE.md, README.md.
- Candidatos: fftools/ffplay_renderer.c, fftools/ffplay_renderer.h, fftools/graph/graphprint.c, fftools/graph/graphprint.h, libavcodec/brenderpix.c, libavcodec/bsfgraph.c, libavcodec/cdgraphics.c, libavcodec/mobiclip.c, libavfilter/af_apsyclip.c, libavfilter/af_asoftclip.c.

### filmcraft-main
- Revisão: snapshot / SHA not verified; licença preliminar: MIT OR Apache-2.0 [Cargo.toml]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: Cargo.toml, NOTICE, ATTRIBUTION.md, README.md.
- Candidatos: apps/filmcraft/src/graphics.rs, crates/engine/src/clip_ops.rs, crates/engine/src/clip_ops_tests.rs, crates/engine/src/commands.rs, crates/engine/src/export_tests.rs, crates/engine/src/export_tools.rs, crates/engine/src/frame_export_tests.rs, crates/engine/src/graphics.rs, crates/engine/src/graphics_tests.rs, crates/engine/src/graphic_templates.rs.

### GNOME--gimp
- Revisão: 0774955bfe1c5318; licença preliminar: GPL [LICENSE]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: LICENSE, COPYING.
- Candidatos: app/actions/brush-editor-actions.c, app/actions/brush-editor-actions.h, app/actions/buffers-commands.c, app/actions/buffers-commands.h, app/actions/channels-commands.c, app/actions/channels-commands.h, app/actions/colormap-commands.c, app/actions/colormap-commands.h, app/actions/context-commands.c, app/actions/context-commands.h.

### godotengine--godot
- Revisão: 232e6b14abf6e590; licença preliminar: UNRESOLVED [LICENSE.txt]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: pyproject.toml, LICENSE.txt, README.md.
- Candidatos: core/config/project_settings.cpp, core/config/project_settings.h, core/math/projection.cpp, core/math/projection.h, core/object/editor_language.h, core/string/node_path.cpp, core/string/node_path.h, core/templates/command_queue_mt.h, drivers/apple_embedded/godot_renderer.h, drivers/apple_embedded/godot_view_renderer.h.

### GraphiteEditor--Graphite
- Revisão: 7477cd2fab315494; licença preliminar: MIT OR Apache-2.0 [Cargo.toml]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: Cargo.toml, README.md.
- Candidatos: desktop/src/render.rs, desktop/src/render/state.rs, desktop/ui/src/internal/render_handler.rs, desktop/ui/src/internal/render_process_app.rs, desktop/ui/src/internal/render_process_handler.rs, desktop/ui/src/internal/render_process_v8_handler.rs, desktop/wrapper/src/intercept_editor_message.rs, document/container/src/archive.rs, document/container/src/backends.rs, document/container/src/lib.rs.

### inkscape--inkscape
- Revisão: 1232eac68aff1297; licença preliminar: UNVERIFIED (root license not identified). Licenças transitivas e de assets ainda não verificadas.
- Marcadores: README.md.
- Candidatos: nenhum na amostragem limitada.

### KDE--krita
- Revisão: 3ee2270d8ead3696; licença preliminar: GPL [COPYING]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: COPYING, README.md.
- Candidatos: benchmarks/KisAnimationRenderingBenchmark.cpp, benchmarks/KisAnimationRenderingBenchmark.h, benchmarks/kis_projection_benchmark.cpp, benchmarks/kis_projection_benchmark.h, libs/command/KisChangeValueCommand.h, libs/command/KisCumulativeUndoData.cpp, libs/command/KisCumulativeUndoData.h, libs/command/kis_command_ids.h, libs/command/kis_command_utils.cpp, libs/command/kis_command_utils.h.

### lightcraft-main
- Revisão: snapshot / SHA not verified; licença preliminar: MIT OR Apache-2.0 [Cargo.toml]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: Cargo.toml, NOTICE, README.md.
- Candidatos: apps/lightcraft/src/editors.rs, crates/engine/examples/render_bench.rs, crates/engine/src/export.rs, crates/engine/src/tests_export.rs, crates/engine/src/tests_filesystem_history.rs, crates/engine/src/cmd/export.rs, crates/faces/src/graph.rs, crates/faces/src/graph/tests.rs, crates/geom/src/homography.rs, crates/gpu/src/render.rs.

### mrdoob--three.js
- Revisão: 11738a9d55e502fb; licença preliminar: MIT [package.json]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: package.json, LICENSE, README.md.
- Candidatos: editor/sw.js, editor/js/Animation.js, editor/js/AnimationResizer.js, editor/js/Command.js, editor/js/Config.js, editor/js/Editor.js, editor/js/EditorControls.js, editor/js/GLTFImportDialog.js, editor/js/History.js, editor/js/Loader.js.

### Natron-RB-2.6
- Revisão: snapshot / SHA not verified; licença preliminar: GPL [LICENSE.txt]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: LICENSE.txt, README.md.
- Candidatos: Documentation/source/conf.py, Documentation/source/devel/conf.py, Documentation/source/devel/init.py, Documentation/source/devel/initGui.py, Documentation/source/guide/conf.py, Documentation/source/guide/_static/dropdown.js, Documentation/templates/group-foot.c, Documentation/templates/group-head.c, Documentation/templates/groupitem-foot.c, Documentation/templates/groupitem-head.c.

### openreel-video-main
- Revisão: snapshot / SHA not verified; licença preliminar: MIT [package.json]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: package.json, pnpm-workspace.yaml, LICENSE, README.md.
- Candidatos: apps/desktop/src/aurora-host/native-renderer.ts, apps/desktop/src/aurora-host/render-preview.ts, apps/desktop/src/main/ipc/export.ts, apps/desktop/src/main/mcp/renderer-bridge.ts, apps/desktop/src/main/sidecar/export-job.ts, apps/desktop/test/aurora-render-preview.test.ts, apps/desktop/test/export-integration.test.ts, apps/image/src/components/editor/EditorInterface.tsx, apps/image/src/components/editor/ExportDialog.tsx, apps/image/src/components/editor/KeyboardShortcutsPanel.tsx.

### penpot--penpot
- Revisão: 10955f17e2794342; licença preliminar: MPL-2.0 [package.json]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: package.json, pnpm-workspace.yaml, LICENSE, README.md.
- Candidatos: .clj-kondo/hooks/export.clj, backend/resources/app/assets/swagger-ui-4.18.3.js, backend/src/app/graph/arrow.clj, backend/src/app/graph/debug.clj, backend/src/app/graph/ingest.clj, backend/src/app/graph/ladybug.clj, backend/src/app/graph/meta.clj, backend/src/app/graph/report.clj, backend/src/app/graph/schema.clj, backend/src/app/graph/stats.clj.

### penpot--penpot-ai-kit
- Revisão: fe4f99e51c714951; licença preliminar: CC-BY-4.0 [package.json]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: package.json, LICENSE, README.md.
- Candidatos: skills/penpot-design-to-code-review/scripts/exportForCompare.js, skills/penpot-document-handoff/scripts/addTooltipCallout.js, skills/penpot-document-handoff/scripts/buildContextCard.js, skills/penpot-document-handoff/scripts/finalizeHandoff.js, skills/penpot-document-handoff/scripts/placePinAndNote.js, skills/penpot-document-handoff/scripts/setupAnnotationKit.js.

### photocraft-main
- Revisão: snapshot / SHA not verified; licença preliminar: MIT OR Apache-2.0 [Cargo.toml]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: Cargo.toml, NOTICE, ATTRIBUTION.md, README.md.
- Candidatos: crates/algo/src/render.rs, crates/algo/src/render2.rs, crates/engine/examples/bench_command_lookup.rs, crates/engine/src/channel_clip.rs, crates/engine/src/commands.rs, crates/engine/src/document_preset_cmds.rs, crates/engine/src/history_cmds.rs, crates/engine/src/render_cmds.rs, crates/engine/src/timeline_cmds.rs, crates/engine/src/channel_clip/tests.rs.

### pixijs--pixijs
- Revisão: 65552017d23255c1; licença preliminar: MIT [package.json]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: package.json, LICENSE, README.md.
- Candidatos: examples/assets_async.ts, examples/assets_background-loading.ts, examples/assets_manifest_bundles.ts, examples/assets_multi-loading.ts, examples/assets_promises.ts, examples/graphics_basic_shapes.ts, examples/graphics_curves_arcs_holes_textures.ts, examples/graphics_dynamic.ts, examples/graphics_fill_stroke_gradient.ts, examples/graphics_mask_animation.ts.

### processing--p5.js
- Revisão: 8ae967b59c491509; licença preliminar: LGPL-2.1 [package.json]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: package.json, LICENSE.txt, README.md.
- Candidatos: src/app.node.js, src/core/p5.Graphics.js, src/core/p5.Renderer.js, src/core/p5.Renderer2D.js, src/core/p5.Renderer3D.js, src/core/rendering.js, src/image/filterRenderer2D.js, src/shape/svg/svg_export.js, src/strands/strands_node.js, src/webgl/p5.RenderBuffer.js.

### remotion-dev--remotion
- Revisão: 32af7e8f8ac67493; licença preliminar: SEE LICENSE IN LICENSE.md [package.json]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: package.json, LICENSE.md, README.md.
- Candidatos: packages/.monorepo/validate-exports.ts, packages/brand/src/BasicsLeftTrimScene.tsx, packages/brand/src/BasicsPlaybackRateScene.tsx, packages/brand/src/BasicsSeriesTrimScene.tsx, packages/brand/src/BasicsSourceOnlyTrimScene.tsx, packages/brand/src/BasicsVirtualizedTimelineComposition.tsx, packages/brand/src/BasicsVirtualizedTimelineScene.tsx, packages/brand/src/BasicsVolumeKeyframesComposition.tsx, packages/brand/src/BasicsVolumeKeyframesScene.tsx, packages/brand/src/KeyframeMove.tsx.

### remotion-dev--skills
- Revisão: 32b241b97f4e0e4a; licença preliminar: UNVERIFIED (root license not identified). Licenças transitivas e de assets ainda não verificadas.
- Marcadores: package.json, README.md.
- Candidatos: skills/remotion-best-practices/remotion-maps/techniques/cesium/assets/CesiumFlythrough.tsx, skills/remotion-best-practices/remotion-maps/techniques/cesium/assets/example-Root.tsx, skills/remotion-best-practices/remotion-maps/techniques/cesium/assets/flight-path.ts, skills/remotion-best-practices/remotion-maps/techniques/maptiler/assets/CountryLabel.tsx, skills/remotion-best-practices/remotion-maps/techniques/maptiler/assets/example-Root.tsx, skills/remotion-best-practices/remotion-maps/techniques/maptiler/assets/MapTilerVectorElement.ts, skills/remotion-best-practices/remotion-maps/techniques/maptiler/assets/RiverReveal.tsx, skills/remotion-best-practices/remotion-maps/techniques/maptiler/assets/tokens.ts, skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/assets/CesiumFlythrough.tsx, skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/assets/example-Root.tsx.

### scribusproject--scribus
- Revisão: 969c3fe4bedbd394; licença preliminar: GPL [COPYING]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: COPYING, README.md.
- Candidatos: resources/editorconfig/helperscripts/latexicons.py, scribus/canvasmode_drawcalligraphic.cpp, scribus/canvasmode_drawcalligraphic.h, scribus/canvasmode_nodeedit.cpp, scribus/canvasmode_nodeedit.h, scribus/documentbuilder.cpp, scribus/documentbuilder.h, scribus/documentchecker.cpp, scribus/documentchecker.h, scribus/documentinformation.cpp.

### sgenoud--replicad
- Revisão: e4b05f67dc4e2393; licença preliminar: MIT [package.json]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: package.json, LICENSE, README.md.
- Candidatos: packages/replicad/src/export/assemblyExporter.ts, packages/replicad/src/projection/index.ts, packages/replicad/src/projection/makeProjectedEdges.ts, packages/replicad/src/projection/ProjectionCamera.ts, packages/replicad/src/shapeFunctions/export.ts, packages/replicad/__tests__/shape-export.test.ts, packages/replicad/__tests__/drawing/projection-arcs.test.ts, packages/replicad-cli/src/projectSvg.ts, packages/replicad-docs/examples/projections.js, packages/replicad-evaluator/src/export.ts.

### tidalcycles--strudel
- Revisão: 8a8ae9ac9659509a; licença preliminar: AGPL [LICENSE]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: LICENSE, README.md.
- Candidatos: nenhum na amostragem limitada.

### Tonejs--Tone.js
- Revisão: de9df332ca7573b9; licença preliminar: MIT [package.json]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: package.json, LICENSE.md, README.md.
- Candidatos: test/helper/compare/OfflineRender.ts, Tone/core/context/ToneAudioNode.test.ts, Tone/core/context/ToneAudioNode.ts, Tone/core/util/IntervalTimeline.test.ts, Tone/core/util/IntervalTimeline.ts, Tone/core/util/StateTimeline.test.ts, Tone/core/util/StateTimeline.ts, Tone/core/util/Timeline.test.ts, Tone/core/util/Timeline.ts, Tone/core/util/TimelineValue.test.ts.

### vectorcraft-main
- Revisão: snapshot / SHA not verified; licença preliminar: MIT OR Apache-2.0 [Cargo.toml]. Licenças transitivas e de assets ainda não verificadas.
- Marcadores: Cargo.toml, NOTICE, README.md.
- Candidatos: apps/vectorcraft/src/clipboard.rs, apps/vectorcraft/src/open_documents.rs, crates/cad/src/scene.rs, crates/doc/src/assets.rs, crates/doc/src/clipnest.rs, crates/doc/src/graph.rs, crates/doc/src/node.rs, crates/doc/src/placed_document.rs, crates/effects/src/clip.rs, crates/engine/src/tests_assets.rs.

## Regra de evidência
O arquivo comprova apenas presença de fonte/manifest. Compatibilidade e licenças de distribuições têm de ser verificadas antes de COPY_ALLOWED.
