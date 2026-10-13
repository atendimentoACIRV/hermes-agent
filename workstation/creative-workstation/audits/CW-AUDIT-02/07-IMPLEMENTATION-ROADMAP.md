# 07 — Plano de implementação executável, prioridade e handoff

**Princípio:** não implementar motor/produto novo antes do caminho compartilhado humano↔IA. Nenhuma task abaixo está implementada por este PR documental. Estado DESIGN/INSPECTED. Todas alterações futuras em worktrees/PRs pequenos com H-079 upstream-first, testes RED→GREEN, rollback e exact-head CI.

## Gates transversais
- Não alterar main nem dados do usuário; verificar PRs #57–64, #76–77 e HEAD atual.
- Reutilizar Workstation TaskRun, approvals, ArtifactStore, journal, Executor ProcessRegistry, CreativeDocument e ProjectStore existentes; não criar dono paralelo.
- Sem source hash, scoped auth ou readback: FAIL CLOSED. Renderer React não executa JS do agente em origem privilegiada.
- Um PR por vertical verificável, não por nome de engine. Qualquer patch que altere source schema inclui migração explícita e modo somente leitura seguro.

| ID/prioridade | Problema e solução; referências | Arquivos existentes de destino | Dependências, RED→GREEN / DoD e rollback |
|---|---|---|---|
| CW02-00 / P0 | Baseline/owners/evidências; PR #77 não merged; #62 merged; fonte local 26 dirs | AGENTS.md, workstation/ROADMAP.md, creative-workstation/VERIFICATION_MATRIX.md | Inventário preservado; não adotar patch histórico sem CI; rollback docs isolados |
| CW02-01 / P0 | CONVERGIR schemas: python doc e TS CreativeProject divergem; KEEP_HERMES doc | workstation/creative_document.py, creative_project_store.py, creative_transactions.py, apps/desktop/src/app/creative-workspace/types.ts | RED: import PR77 JSON perde IDs/attrs/3D; GREEN: strict codec migração/reopen; revision etag, unknown future reject; rollback leitura somente do velho |
| CW02-02 / P0 | 1 command registry compartilhado, strict schemas e enabled(reason); EffectCraft commands/mod.rs:94,339 | workstation/creative_commands.py, creative_transactions.py, creative_project_runtime.py, Electron preload/IPC, CreativeWorkspaceContext.tsx | RED mouse vs IA tem stores diferentes; GREEN gesto e agent retornam MESMO commandId/projectRevision/receipt. Undo após restart, 409 concorrente; rollback feature flag editor local read-only |
| CW02-03 / P0 | Batches $N.key e one undo; EffectCraft batch.rs:16,42,54,97 | creative_commands.py, creative_transactions.py, creative_edit_plan.py, typed gateway | RED step3 falha e ainda muda state; GREEN 4 etapas atômicas com refs e history único, no blind retries; rollback apagar novo contract sem alterar formato antigo |
| CW02-04 / P0 | Assets reais imagem/logo/font/SVG com source hash, sem flatten | creative_project_store.py, creative_document.py, creative_media.py, creative_scene_adapters.py, CreativeWorkspacePage.tsx | RED arquivo inexistente silently color; GREEN import hashes, traversal denied, readback after restart; rollback projeto preservado, imports inertes |
| CW02-05 / P0 | PNG REAL, não SVG file nem metadata; THREE depois; render preview + export | creative_render_adapters.py, creative_scene_adapters.py, creative_render.py, creative_project_runtime.py, UI canvas | RED missing font/GPU or wrong pixel marks verified; GREEN decoded PNG, dims, transparent pixel, sourceRevision and SHA, frame seek; rollback adapter disabled no false receipt |
| CW02-06 / P0 | Corrigir verificador: fake frame SHA e black source fallback em creative_export.py:88–215 | creative_export.py, creative_video_process.py, creative_render_adapters.py, workstation/tests/test_creative_export*.py | RED mock decoder fails but verified=true; RED missing clip generates black; GREEN deterministic error, independent decoded frame match source; no partial done; rollback behind stricter gate (never reenable unsafe) |
| CW02-07 / P0 | 3D no MESMO documento com GLB + câmera editáveis; Three.js scene graph e canvas | creative_3d.py, creative_scene_adapters.py, creative_document.py, Electron creative view/isolated renderer, CreativePreview.tsx | RED metadata-only render; GREEN real pixels GLB + SVG title in 1 PNG, camera property edit via UI+AI, frame and reimport; rollback mark 3D unavailable but preserve layer |
| CW02-08 / P0 | Motion 2D/3D keys + Graph; EffectCraft keyframe.rs + graph.rs adapted | creative_time.py, creative_commands.py, creative_scene_adapters.py, CreativeGraphEditor.tsx, CreativeInspector.tsx | RED TS vs Python easing mismatch, key movement lost; GREEN value/speed/Bezier/tangents/roving, drag 1 undo, 29.97/60 and out-of-order seek; rollback view basic curves without state loss |
| CW02-09 / P0 | MP4 composto a partir de frames renderer da rev R e audio; FFmpeg supervised | creative_export.py, creative_video_process.py, creative_render_adapters.py, creative_media.py | Depends 05/06/07/08; RED first clip only or lavfi black; GREEN 10s video distinct decoded frames, frame count, codec, A/V sync, cancel/process cleanup, readback; rollback no video UI until proof |
| CW02-10 / P1 | Semantic Edit Plan visually reversible, selective commit/cancel | creative_edit_plan.py, creative_transactions.py, agent tool gateway, PR77 UI | RED preview changes user doc; GREEN stage R' renders actual canvas, subset dependency valid, human R→R+1 conflict prevented; rollback refuse apply |
| CW02-11 / P1 | NLE media and audio link correctness; FilmCraft Sequence.check/edit | creative_timeline.py, creative_commands.py, creative_time.py, UI timeline | RED split/trim/ripple drift with reverse/2x and locked tracks; GREEN linked AV sample-aware and undo; rollback disable unsafe ops |
| CW02-12 / P1 | Better vector + raster editing; VectorCraft, PhotoCraft, Graphite | creative_document.py, creative_operations.py, creative_scene_adapters.py, renderer | RED Boolean loses path/source; GREEN paths, masks, adjustments, CMS, editable after reopen; legal gate |
| CW02-13 / P1 | Perf and bounded agent tools; EffectCraft command discovery + cache refs | command registry/tool gateway, creative_render_adapters.py, experience_compiler | RED large command menu injected per turn; GREEN correct operation fewer tokens/latency benchmark, pixel parity cached vs uncached; rollback cache and narrowed discovery by flags |
| CW02-14 / P2 | Specialty engines EffectCraft/FilmCraft/LightCraft/Remotion/Blender | creative_apps.py, creative_process.py, creative_runtime.py, adapters | each adapter separate licensing/proc/security/format test; never project owner |
| CW02-15 / P2 | Verified creative prefabs/operations | workstation/experience_compiler/, creative typed command journal | zero LLM only when existing compiler admits proven deterministic sequence; drift quarantine and TaskRun scope; rollback promotion |

## Vertical acceptance by increment
Milestone A: CW02-01,02,03,04,05,06 → functional editable 2D + imported assets + real PNG, same document between human and agent. No 3D claim.
Milestone B: CW02-07 → 2D/3D same scene, editable camera, PNG.
Milestone C: CW02-08,10 → human+agent keyframes/Graph + reversible preview.
Milestone D: CW02-09,11 → real multi-layer MP4+audio with decoded independent verifier.
Milestone E: CW02-12–15 → pro effects/interchange/cache/prefabs only when benchmarks demonstrate advantage.

## Implementation handoff: exact first task
START CW02-01/02 as ONE tiny vertical and a separate export verifier RED test:
1. Create isolated development worktree from a mutually admitted baseline; do NOT reuse dirty root checkout or merge PR77 blindly.
2. Inspect workstation/creative_document.py:29–360, creative_commands.py:26–560, creative_transactions.py:21–138, creative_project_store.py:65–303, PR77 types.ts:3–105, creative-mvp-model.ts:4–160, CreativeWorkspaceContext.tsx:42–110, Electron IPC. Record source schema differences.
3. Write failing test: human edit through renderer command serializer and agent edit through Python produce identical post-edit source SHA, revision, journal and undo; repeat after restart. Negative expectedRevision stale, duplicate idempotency across process, untrusted actor, undefined parameter, locked layer, cancellation.
4. Implement typed JSON contract at current canonical CreativeCommand boundary, narrow Electron IPC/proxy owner; make React reducer a view/event adapter only. Persist source and history CAS before UI claims success. Existing file-based JSON import is migration adapter, not authoritative storage.
5. Run focused RED→GREEN and Electron real UI E2E, verify project reopen and selection; document exact SHA, performance counters, failure. No fake tests of mock WebContentsView.
6. Independently write failing tests for creative_export pseudo-hash+missing-source fallback and make fail-closed before any video promotion.
7. Publish small draft PR with rationale/test report and rollback flag. Do not start 3D before accepted single-document bridge.
The next implementer should begin with these exact paths, not repeat this research.

## DoD hierarchy
NOT_IMPLEMENTED → SOURCE_PRESENT → UNIT_TESTED → INTEGRATED_NATIVE_E2E → EXACT_HEAD_CI → QUALIFIED. Each milestone records which level has been achieved; no green badge for unit-only runtime. No user-data mutation during audit.
