# 07 — Reusable Code Catalog (CW-AUDIT-01)

Cada cartão tem origem/destino exatos, licença verificada e rollback. Só incluir código terceiro com licença verificada. `COPY_DIRECT` só com MIT/Apache/CC-BY e atribuição.

## RC-01 — Command discovery + strict params (P0 QUICK WIN)
- ID: RC-01 · Capacidade: `list_commands{filter,enabled_only,schemas}` + `describe_command` + strict reject unknown (-32602)
- Problema Hermes: `creative_commands.py` sem schemas, typos de agente viram mutação silenciosa ou KeyError tardio
- Origem: effectcraft `crates/engine/src/commands/mod.rs:93-235,339-359` (`CommandSpec`, `find`, `check_params`) + `automation/src/tools.rs` · SHA: NOT_VERIFIED snapshot · Teste upstream: `batch_refs_one_undo_step_and_rollback` + `commands --list --schemas`
- Destino: `workstation/creative_commands.py:CommandRegistry` · Owner: Creative Operations
- Diferença: ~2000 ids com doc+schema+enabled_reason vs 19 cmds com `params["x"]` direto
- Integração: ADAPT_CONTRACT — adicionar `label/menu/shortcut/params_doc/json_schema/enabled_reason` + `execute_checked` + `capabilities()` bounded
- Licença: MIT OR Apache-2.0 · Deps: nenhuma (só serde_json) · Compat: total (Python) · Dificuldade: S · Risco: baixo · Benefício: elimina classe de erros agente · Testes: strict-reject + filter + enabled_only · Rollback: remover campos extras

## RC-02 — Batch atômico $N.key + fold (P0 QUICK WIN)
- Origem: `crates/engine/src/commands/batch.rs:1-118` (`engine.batch`, `reference/substitute`, `NOT_IN_BATCH`, rollback snapshot, `fold()`)
- Destino: `workstation/creative_transactions.py` · Owner: CreativeHistory
- Integração: ADAPT_CONTRACT — refs `$N.key`, fold 1 undo, rollback nomeando step; MANTER 409/idempotência Hermes
- Licença MIT/Apache · Dificuldade S · Testes: falha passo 3 sem mutação (já existe `test_creative_commands 4`, estender com refs)

## RC-03 — Branching history + merge_key + goto (P1 HIGH IMPACT)
- Origem: `crates/engine/src/history.rs:1-346` (`History`, `Branch`, `Arena`, `record/abandon_redo/trim/goto_history`) + `lib.rs:608-686 edit()` + `prefs.rs:1059 undoLevels`
- Destino: `workstation/creative_transactions.py` · ADAPT_ALGORITHM (portar árvore + merge_key drag + níveis; manter revision int)
- Licença MIT/Apache · Dificuldade M · Risco: migração undo linear→árvore (feature-flag) · Testes: goto branch sem perder, merge drag 1 step

## RC-04 — timeBase + snap_nearest + saturating (P1)
- Origem: `crates/time/src/lib.rs:16-500` + `commands/prop.rs:84-117` + `project/src/lib.rs:835-845`
- Destino: `workstation/creative_time.py` + `creative_timeline.py` · ADAPT_CONTRACT/ADAPT_CODE seletivo
- NÃO trocar Fraction por Tick; portar `nonzero/saturating/clamp`, `timeBase layer|comp`, snap + warnings out-of-range
- Licença MIT/Apache · Dificuldade S-M

## RC-05 — NLE edit pura + Sequence::check (P1)
- Origem: filmcraft `crates/edit/src/lib.rs:95-1003` + `project/src/lib.rs:965,1033 Sequence::check`
- Destino: `workstation/creative_timeline.py` · ADAPT_ALGORITHM (ripple_trim_group, lift/extract/insert/overwrite, invariantes never-overlapping)
- Licença MIT/Apache · Dificuldade M · Testes: multitrack sync + locks + 29.97/60 + 2x/reverse

## RC-06 — Interchange único (P1)
- Origem: filmcraft `crates/interchange/src/{fcp7,fcpxml,otio,edl,aaf,omf,comp,common}.rs` · pin `2c5ba7a` (via effectcraft Cargo)
- Destino: CWN-03/06 adapter · ADAPT_CONTRACT (usar crate pinada via subprocess/FFI, nunca reimplementar parser)
- Licença MIT/Apache

## RC-07 — Graph math (P1)
- Origem: effectcraft `crates/keyframe/src/lib.rs:21-560` (ease/bezier/roving/velocity/spatial ARC_N=96)
- Destino: CWN-07 · ADAPT_ALGORITHM math, UI Hermes própria (nunca egui)
- Licença MIT/Apache · Dificuldade M

## RC-08 — LayerCache + disk OPFS (P1)
- Origem: `crates/render/src/cache.rs:1-116` + `disk_cache.rs` (LZ4/atomic/checksum/128-bit/LRU) + `ui-egui/src/frames.rs` (out-of-order-safe)
- Destino: `workstation/creative_render_adapters.py` preview · ADAPT_ALGORITHM
- Licença MIT/Apache

## RC-09 — Adjustment stack + tiles CoW + CMS (P1)
- Origem: photocraft `doc/src/lib.rs:52-1315` + `adjust.rs:133` + `raster/src/lib.rs:38-90` + `cms/` + `paint/brush.rs:135-508`
- Destino: pipeline imagem Hermes · ADAPT_ALGORITHM (não embarcar editor)
- Licença MIT/Apache

## RC-10 — __query vs __exec + beginUndoGroup (P0)
- Origem: effectcraft `script/src/runtime.rs` + `prelude.js:4-5` + `matchnames.rs`
- Destino: capabilities/skills · ADAPT_CONTRACT (leitura snapshot vs escrita journaled)
- Licença MIT/Apache

## RC-11 — Penpot MCP + AI Kit skills (P0 QUICK WIN)
- Origem: `penpot--penpot/mcp/packages/common/src/index.ts` + `backend/src/app/rpc/` + `penpot--penpot-ai-kit/skills/penpot-*/SKILL.md` · SHA `10955f17e279` / `fe4f99e51c71` · Lic MPL-2.0 (WRAP, nunca linkar Clojure) + CC-BY-4.0 (COPY com atribuição)
- Destino: `creative_apps.py` + skills · WRAP_ENGINE + COPY_DIRECT (markdown)
- Dificuldade S · Risco legal baixo com atribuição

## RC-12 — Three.js Scene + Editor.History (P1)
- Origem: `mrdoob--three.js/src/scenes/Scene.js` + `src/renderers/WebGLRenderer.js` + `editor/js/{Editor,History,Command}.js` · SHA `11738a9d55e5` · MIT
- Destino: `creative_scene_adapters.py` + `creative_3d.py` · ADAPT_CODE (copiar grafo + undo-stack, renderer web nativo)
- Dificuldade S-M

## RC-13 — Replicad WASM CAD (P2 STRATEGIC)
- Origem: `sgenoud--replicad/packages/{replicad,replicad-opencascadejs}/` · SHA `e4b05f67dc4e` · MIT
- Destino: 3D CAD paramétrico browser · WASM_MODULE (sem nativo)

## RC-14 — FFmpeg sidecar (P0, KEEP pattern)
- Origem: `FFmpeg--FFmpeg/fftools/ffmpeg.c` + `libav*` · SHA `1f7228e4fcc4` · LGPL/GPL → NUNCA copiar; EXTERNAL_PROCESS `ffmpeg/ffprobe` binário
- Destino: `creative_video_process.py` (já faz) · KEEP_HERMES + documentar flags validadas

## RC-15 — Graphite NodeDefinition (P2)
- Origem: `GraphiteEditor--Graphite/node-graph/nodes/{vector,raster,graphic}` + `document/graph-storage` · SHA `7477cd2fab31` · MIT/Apache
- Destino: `creative_operations.py` · ADAPT_CODE (único procedural permissivo)

## RC-16 — Tone.js Synth (P3)
- Origem: `Tonejs--Tone.js/Tone/instrument/Synth.ts` · SHA `de9df332ca75` · MIT · ADAPT_CODE trilha WebAudio

## REJECTED / REFERENCE_ONLY (não incorporar)
- Natron `Engine/Node.h` etc (GPLv2) — REFERENCE_ONLY + EXTERNAL_PROCESS CLI, REJECT COPY.
- Blender `bpy` (GPL-2.0), GIMP/Krita (GPL-3.0), PartMode (AGPL), Strudel stub (AGPL), p5.js (LGPL — só algoritmo), Scribus (GPL-2.0+), Godot (MIT mas overkill — REFERENCE_ONLY), n8n (Sustainable Use — só intercâmbio), Inkscape stub / Strudel stub (REJECT — sem código).
- OpenReel executor/registry — REJECT COPY (float, ripple parcial, snapshot JSON, 228 tools); ADAPT só `EditingHost` seam + `runTurn`.
- Remotion código — WRAP (`studio/cli/render`), nunca fork (licença proprietária dual).
