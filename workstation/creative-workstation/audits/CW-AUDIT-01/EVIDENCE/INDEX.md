# Evidence Index (CW-AUDIT-01)

**HEAD Hermes:** `80e3a0724b1c939bfbcbb4801434fb31661eea70` · **Pin D-043:** `f21e803b` · Sem binários/segredos/dados pessoais. SHAs externos em `01`.

## Hermes (FACT — lidos)
- `workstation/creative_document.py`, `creative_time.py`, `creative_timeline.py`, `creative_nle.py`, `creative_commands.py`, `creative_transactions.py`, `creative_operations.py`, `creative_edit_plan.py`, `creative_project_store.py` (dup L69/L114), `creative_project_runtime.py`, `creative_render.py`, `creative_render_adapters.py`, `creative_scene_adapters.py`, `creative_media.py`, `creative_export.py`, `creative_video.py`, `creative_video_metadata.py`, `creative_video_process.py`, `creative_3d.py`, `creative_hyperframes_render.py`, `creative_apps.py`, `creative_process.py`, `creative_runtime.py`, `creative_studio_service.py`, `operational_kernel.py` (L1-120), `operational_capabilities.py` (L1-120), `capabilities.py`, `artifacts.py`
- `apps/desktop/electron/workstation-creative-frame.ts` (189 linhas)
- `workstation/tests/test_creative*.py` (22 suites / 98 `def test_`)
- `workstation/creative-workstation/{ENGINE_NEUTRAL_ARCHITECTURE_2026-10-10.md,ENGINE_NEUTRAL_IMPLEMENTER_HANDOFF_2026-10-10.md,CWN_BASELINE.md,README.md,AGENTS.md}`, `workstation/{AGENTS.md,ARCHITECTURE.md,SOURCE_MATRIX.md,ROADMAP.md}`, `workstation/context/{README.md,CURRENT_STATE.md,DECISIONS.md,REFERENCE_CODE_TO_CODE_AUDIT_2026-09-23.md}`
- Comandos: `git rev-parse HEAD`, `git branch --show-current`, `git status --porcelain`, `git worktree list`, `Get-ChildItem workstation/creative*.py`, `Test-Path .git` por referência

## EffectCraft (FACT — snapshot sem .git, ws 0.7.0)
- `Cargo.toml:1-10,14-46,72-93` (members, deps, filmcraft pin `2c5ba7a`)
- `docs/architecture.md:1-102,163-200` (L0-L6, Tick, document, rendering, §6a interchange)
- `docs/agents.md:1-652` (MCP/CLI/control, tools, cookbook, pitfalls #257/#261)
- `docs/control-protocol.md:1-50`, `docs/mcp.md:1-72`, `docs/web.md:1-482`, `docs/gaps.md:11-42`, `docs/parity.md:13-33`, `docs/effects.md:6-12`, `AGENTS.md §1-2`, `LICENSE-MIT`, `LICENSE-APACHE`, `NOTICE`, `ATTRIBUTION.md:1-122`
- `crates/engine/src/{lib.rs:351-686,commands/mod.rs:93-359,commands/batch.rs:1-118,history.rs:1-346,prefs.rs:1059,offload.rs,remote.rs}`
- `crates/{time/src/lib.rs:16-500,keyframe/src/lib.rs:21-560,value.rs,project/src/lib.rs:835-845,effects/src/lib.rs:415-1127,render/src/{lib.rs:286-1580,cache.rs,disk_cache.rs},gpu/,ui-egui/src/panels/graph.rs (626),script/src/runtime.rs,automation/src/tools.rs,host/src/lib.rs:82-96}`

## FilmCraft/PhotoCraft/OpenReel/Natron (FACT — snapshots)
- filmcraft: `Cargo.toml:1-58`, `docs/architecture.md:15-200`, `project/src/lib.rs:269-1033`, `edit/src/lib.rs:95-1003`, `interchange/src/{fcp7,fcpxml,otio,edl,aaf,omf,comp,common}.rs`, `engine/src/{lib.rs:252-469,commands.rs:324-2460,keyboard.rs:251}`, `ui-egui/src/panels/timeline.rs:1262`
- photocraft: `doc/src/lib.rs:52-1315`, `adjust.rs:133`, `raster/src/lib.rs:38-547`, `cms/{lib,pipeline,clut,curve,math,builtin,gamut}.rs`, `paint/{brush:135-508,lib,dynamics,render}.rs`, `psd/{header,compression,tagged,file,builder}.rs`, `engine/src/*_cmds.rs`, `automation/src/{server,headless}.rs`, `README:182-219,413`
- openreel: `packages/core/src/actions/action-executor.ts:74-1364`, `packages/agent/src/{host.ts:228-308,loop.ts:91-278,registry.ts,tool-router.ts:70}`, `AGENT-GUIDE.md:11,60-71`, `LICENSE`, `package.json:40`
- natron: `README.md:1-141`, `LICENSE.txt:1-60`, `Engine/Node.h:370-748`, `AppManager.h:208-570`, `HostSupport/Ofx*.h`, `Renderer/NatronRenderer_main.cpp`

## 20 repos (FACT — git SHAs em 01; arquivos-chave nos relatórios de campo)
- Penpot `mcp/packages/common/src/index.ts` + `backend/src/app/rpc/` + AI Kit `skills/penpot-*/SKILL.md` + `skills.json/lock`
- Remotion `core/src/Composition.tsx` + `{cli,studio,renderer}/src/index.ts` + `mcp/` + skills `remotion-{create,studio,render}/SKILL.md`
- Three.js `src/scenes/Scene.js` + `src/renderers/WebGLRenderer.js` + `editor/js/{Editor,History,Command}.js`
- FFmpeg `fftools/ffmpeg.c:main` + `libavcodec/avcodec.h` · Blender `scripts/modules/bpy/` · GIMP `libgimp/gimp.h+pdb/` · Krita `libs/pigment+image/` + `plugins/paintops/` · Graphite `node-graph/nodes/*` + `document/graph-storage` · Replicad `packages/replicad/src/sketches` · PartMode `src/{mcp.ts,headless/kernel-host.ts}` · Tone.js `Tone/instrument/Synth.ts` · n8n `packages/workflow/src/Workflow.ts`

## Lacunas de evidência (NV, não ausência)
Conteúdo React `creative-workspace/` (só existência), exact-head CI nesta branch, benchmarks B-01..B-10 (NOT_RUN), BrowserOS código (só docs públicas), remotes/upstream dos 5 snapshots, `control_plane/` além `contract.py`.
