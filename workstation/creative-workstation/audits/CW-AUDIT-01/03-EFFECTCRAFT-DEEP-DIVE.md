# 03 — EffectCraft Deep-Dive (CW-AUDIT-01)

**Alvo:** `referências/01-Criacao-Visual-Video-3D\effectcraft-main` — snapshot sem `.git` (SHA NOT_VERIFIED) · workspace `0.7.0`, edition 2024, rust 1.95 (`Cargo.toml:1-10`) · licença `MIT OR Apache-2.0` (`Cargo.toml:9`) + NOTICE + ATTRIBUTION.md
**Docs lidos:** `docs/architecture.md` (§1-§6a), `docs/agents.md` (652 linhas), `docs/control-protocol.md`, `docs/mcp.md`, `docs/web.md`, `docs/gaps.md`, `docs/parity.md`, `AGENTS.md`
**Método:** read-only, sem build, sem execução. Símbolos Rust citados com paths.

## 3.1 Arquitetura de crates (FACT — IMPLEMENTADO)

`Cargo.toml:1-4` `members=["crates/*","apps/*","xtask"]`. `docs/architecture.md:1-52` tabela L0-L6 + `cargo xtask layers` (proíbe L<5 depender de egui/eframe/winit/rfd/cpal/muda) + `cargo xtask wasm` (L0-L4+ui-egui+web → wasm32).

| Layer | Crates | Papel |
|---|---|---|
| L0 | `time, geom, color, vp9enc, opusenc, hevcenc, av1enc` | Tick 254016000000, transform, 38 blends, codecs próprios (VP9/Opus/HEVC/AV1 de spec) |
| L1 | `raster, keyframe, segment, psd, path` | imagem float premult + rayon, animated values, MobileSAM/MediaPipe registry, PSD 8/16/32-bit, Bezier ops |
| L2 | `project, text, effects, svg, pdf, model, track` | documento `.ecproj`, shaping, **registry 306 efeitos** (241 na tabela stale arquitetura), SVG/PDF/AI/EPS, glTF/OBJ, tracking NCC+Lucas-Kanade |
| L3 | `render, media, expr, export, gpu, interchange, lottie, plugin` | `Renderer::comp_frame`, FilmCraft codecs, boa JS AE-model, H.264/HEVC/AV1/ProRes/WebM/PNG/GIF/WAV, wgpu, FCP7/FCPXML/OTIO/EDL/AAF/OMF via filmcraft-interchange pinado, Lottie, wasmi sandbox |
| L4 | `engine, script, host` | `Session`, boa ScriptUI AE-matchnames, sessão wired (media+expr+script+plugins+exporter) |
| L5 | `ui-egui, automation` | desktop docking/viewer/timeline/graph, MCP headless/bridge |
| L6 | `apps/effectcraft, effectcraft-cli, effectcraft-web` | desktop, CLI headless, browser wasm |

Same-layer edges permitidas: `path→keyframe,raster`, `text→path`, `pdf→svg,text`, `effects→project,text,path,track`, `media/expr/export/gpu→render`, `export→media`, `lottie→format`, `host→engine,script`, `script→engine`.
**Divergência FACT:** `architecture.md:30` diz 241 efeitos; `effects.md:6` + `parity.md:21` dizem 306/280 GPU — doc arquitetura stale.

Fluxo real confirmado (hipótese da missão §6.1 CONFIRMADA com refinamento):
```
humano/agente → descoberta (list_commands/describe + enabled) → validação strict (check_params -32602)
→ Session::execute(id,params) → guard::guarded + journal 10k → mutação Project (Arc) → history.record/merge
→ persistência .ecproj atômica (to_file_json read-back) / autosave → render (comp_frame + caches) → UI/MCP/CLI reply
```

## 3.2 Command Registry — prioridade máxima (FACT — IMPLEMENTADO, superior ao Hermes em 4 pontos)

- `crates/engine/src/commands/` ~70 ficheiros: `mod.rs,batch.rs,prop.rs,layer.rs,comp.rs,effect.rs,time.rs,track.rs,warp_cmds.rs,camera_cmds.rs,roto_cmds.rs,paint.rs,puppet.rs,mask*.rs,keys_more.rs,key_transform.rs,essential.rs,render_queue.rs,lottie.rs,viewer_cmds.rs,frontend.rs,query.rs,scripts.rs,settings.rs`.
- `commands/mod.rs:93-107` `CommandSpec{id,label,menu,shortcut,params,enabled:Enabled,run:Run,journal:bool}` + macros `cmd!/query!` + `command_specs() OnceLock` agregando ~50 `*_::specs()`. `mod.rs:224-235,339-359` `find(id)` índice ~2000 ids, `check_params` rejeita unknown com accepted-list, `ALWAYS_OK=[comp,merge]`.
- `engine/src/lib.rs:351,572-606` `Session{project:Arc<Project>,history,revision,...}` + `execute → find+enabled(+bypass explícito layer/layers/prop/keys/item/comp)+guarded+journal` ; `execute_checked = check_params+execute`; `is_enabled`.
- `commands/batch.rs:1-118` `engine.batch{steps,label?,atomic?=true}` + `$N.key` via `reference/substitute` + `NOT_IN_BATCH=[engine.batch,file.runScript,script.run]` + rollback snapshot project/history/state + `fold()` 1 undo. Teste `batch_refs_one_undo_step_and_rollback`.
- Despacho único VERIFICADO: UI + CLI (`exec/get/set/run/render-frame/script`) + control TCP JSON-lines (`engine.execute`, `ui.menu.invoke`) + MCP (`command_run/command_batch/execute_command/batch`) → todos `Session::execute`. `automation/src/tools.rs:1-3`, `host/src/lib.rs:82-96`.
- Widgets com automation-id (`ui-egui`, `control.rs:250`, `timeline.prop.<uid>.*`) permitem click além de comando — clicks NÃO são mecanismo obrigatório de edição (responde §6.6 missão: API tipada é o caminho curto; clicks para semântica ausente).

Respostas §6.2 (1-10):
1. Mais completo? SIM em quantidade (~2000 ids vs 19 Hermes) mas Hermes cobre NLE/documento com owner TaskRun que EffectCraft não tem. 2. Descoberta? SIM — `list_commands{filter,enabled_only,schemas}` + `describe_command` + `enabled/why` > Hermes (sem schemas). 3. Equivalência gesto↔agente? SIM — mesmo id + automation-ids + `keys.move{merge}` = 1 drag. 4. Validação tipada? SIM — params doc + JSON Schema + strict reject. 5-8. Atomicidade/batch/undo/consistência? SIM — `engine.batch` atômico + fold + rollback nomeando step; `edit(label,merge,f)` same-content→sem step, merge→fold, senão record; `bump` segue saved (dirty segue undo). **Atenção:** atomicidade é snapshot-rollback, não journal transacional com 409 como Hermes — complementar, não substituto. 9-10. Módulos portáveis? `CommandSpec+check_params+schema` (ADAPT_CONTRACT), `batch $N.key+fold` (ADAPT_CONTRACT), `enabled→Result reason` (ADAPT_CONTRACT). Proposta §3.9 abaixo.

## 3.3 Session / history / transações (FACT)

- `engine/src/history.rs:1-346` `History{undo:Vec<(label,Arc<Project>)>,redo,merge_key,branches:Vec<Branch>}` + `HistoryNode{index,id,label,parent,depth,current}` + `Arena::build` + `record/abandon_redo/trim/prune/clear/tree` + `Session::history_tree/goto_history` (resto vira branch, `sanitize+bump`). Branching real, não linear.
- `lib.rs:608-686` `edit(label,merge,f)`; níveis `prefs.rs:1059 general.undoLevels 1..99 default 32` (teste `undo_levels_are_honoured`); comandos no-op não gravam step; `get_state.dirty` segue undo.
- `.ecproj` JSON `savedBy+schema` + `.ecprojx` XML; `Project::to_file_json` read-back antes de escrever (JSON sem NaN/inf) + escrita atômica; schema 2 migração effect-space shape/text (§architecture.md:85-102, `upgrade_effects`); unknown future → warning + drop se salvar (old recusa abrir novo — nunca render errado).
- Comparação: Hermes `CreativeHistory` tem 409 + idempotência + inverses cirúrgicos (superior em concorrência); EffectCraft tem branching + merge_key + níveis (superior em UX). **Recomendação: ADAPT_ALGORITHM branching+merge para Hermes, KEEP_HERMES 409/idempotência.**

## 3.4 Tempo e keyframes (FACT)

- `crates/time/src/lib.rs` (~790 linhas): `TICKS_PER_SECOND=254_016_000_000` (LCM broadcast×1001 + áudio) · `Tick(i64)` + `from_seconds_f64/from_units/from_rational/saturating/clamp/nonzero` · `FrameRate{num,den}` + 11 COMMON + 23.976..120 · `frame_duration/frame_at/tick_of/snap/snap_nearest` · `TimeDisplay{Timecode,Frames,Feet16/35,AudioSamples,Seconds}` + drop-frame `df_params/format_timecode/parse_timecode`.
- `project/src/lib.rs:835-845` `layer_time=(comp-start)/stretch`, Time Remap override; `architecture.md:56-60` snap a whole frames como AE; `prop.rs:84-117` `timeBase:layer|comp` + snap_nearest; `agents.md` cookbook layer-vs-comp pitfall #257 documentado.
- `crates/keyframe/src/lib.rs:21-160,220-560` `Interp{Linear,Bezier,Hold}` + `Ease{speed,influence}` + `EASY={0,1/3}` + `Keyframe{time:Tick,value,in/out_interp,in/out_ease,continuous,auto_bezier,spatial_in/out,spatial_auto,spatial_continuous,roving,label}` + `ease_progress/solve_u/bez`, `SpatialSeg ARC_N=96` arc-length, `spatial_tangents/retime_roving/velocity/speed`. `value.rs` ShapePath/Gradient/TextDoc (SourceText hold).
- **Conclusão tempo:** Hermes `CanonicalTime(Fraction)` já é racional e suficiente; Tick EffectCraft NÃO deve substituir por preferência (missão §6.3). Benefício real: `snap_nearest` + `timeBase` + `nonzero/saturating` + NTSC/drop-frame display separado de sample rate. **ADAPT_CODE ~790 linhas sem deps para cron/scheduler se drift provado; senão ADAPT_CONTRACT.**

## 3.5 Graph Editor (FACT — IMPLEMENTADO, melhor referência para CWN-07)

- `crates/ui-egui/src/panels/graph.rs` (626 linhas): value/speed graph, drag time/value, handles, `keys.set/setEase/select`; `graph_tools.rs`, `state.rs:371-395 graph_editor/mode value|speed`, `menus.rs:57 Shift+F3`, `control.rs:250 ui.set timeline.graphEditor`.
- Curvas: temporal Bezier (ease speed/influence) + espacial Bezier arc-length + roving + hold + velocity (`keys.velocity{outSpeed,outInfluence}`, `keys.select/toggle/move{merge}/transform{merge,fromStart}/copy/paste`, `selectEqual/Previous/Following`, `time.nextKey/previousKey` com `visible:[{layer,prop}]`).
- Seleção/manipulação paridade humano↔agente: mesmos comandos `keys.*` + `prop.set/addKey{timeBase}` + undo + viewer RAM preview sem freeze (newest completed enquanto exact renderiza; out-of-order nunca regressa).
- Respostas A-E missão §6.4: A) reaproveitar algoritmos SIM (easing/spatial/velocity — ADAPT_ALGORITHM); B) portar para React/Canvas/SVG/WebGL SIM mas esforço médio (626 linhas egui → reescrever interação, manter math); C) reusar motor Rust com UI própria SIM via `Session::execute` headless + render_frame (menor esforço, recomendado); D) embutir editor existente NÃO — egui não drop-in React sem bridge pesada; E) combinar math EffectCraft + UI timeline Hermes/OpenReel SIM (melhor custo/benefício).
- **Recomendação fundamentada:** C+E — motor `keyframe` + comandos `keys.*` como contrato, UI Hermes própria em `creative-workspace/GraphEditor`, math portada, nenhuma dependência egui.

## 3.6 Efeitos e composição (FACT — CPU maduro, GPU parcial com fallbacks)

- Registry: `effects/src/lib.rs:415-529` `EffectSpec{id,name,category,params,render:RenderFn,gpu,float}` + `registry()` agregando 20+ famílias + `find/all/categories` + `GPU_EFFECTS` + `TIME_DEPENDENT` + teste anti-drift. `effects.md:6-12` 306 efeitos/3014 params/280 GPU/306 32bpc/0 parcial (gerado de catalog.rs).
- Pipeline `render/src/lib.rs:286-330` `Renderer::comp_frame` bottom→top source→masks→effects→styles→transform(+motion blur)→matte→blend; effect-space (`effect_bounds/Buf::rebase`, shape/text comps-sized centrados), adjustment sobre accumulator, Classic 3D per-pixel + Advanced 3D meshes PBR (glTF/OBJ, GGX, IBL, PCF shadows, 2×2 SS + reversed-Z), Collapse Transformations, Continuously Rasterize, Preserve frame/nested rate.
- Cache: `render/src/cache.rs` LayerCache content-hash sem transform + `set_gate` (deferred não cacheia) + disk LZ4/atomic/checksum/128-bit/LRU + RAM preview content-keyed + viewer out-of-order-safe. Efeitos clock-dependentes declarados.
- Tracking/IA: `track` NCC+Lucas-Kanade + `warp_stab` Subspace Warp + `camtrack` SfM bundle-adjustment + `roto` graph-cut/GrabCut + MobileSAM/MediaPipe registry SHA-256 + Content-Aware Fill PatchMatch multi-escala — tudo via comandos `track.*/warp.*/camera.*/roto.*` com `wait:true` headless.
- Maturidade honesta: `gaps.md` breadth ~95%+ mas behavior 60-80% não medido, `.aep 0%`, perf desconhecido vs AE, HEVC/AV1 sem B-frames, AI ~50%. `parity.md` 99% ponderado auto-avaliado — NÃO usar como benchmark.
- Para Hermes: **WRAP_ENGINE / REFERENCE_ONLY** — nunca reimplementar 306 efeitos; chamar `effectcraft-cli render-frame/exec` headless ou MCP `render_frame`; usar `GPU_EFFECTS/TIME_DEPENDENT` como referência de plugin design (wasmi API v1).

## 3.7 Automação e agentes (FACT)

- Três entradas (§agents.md:3-5): MCP (`mcp [--demo|--project|--gpu|--bridge|--autosave]`, JSON-RPC stdio, tools `list_commands/describe/execute/get_state/run_script/get_project/get_comp/get_layer/get_property/set_property/add_keyframe/list_effects/add_effect/render_frame/open/save/undo/redo/history/script_ui/batch` + `command_list/run/batch/doc_inspect/render_preview`), CLI (`info/commands/exec/props/set/get/run/render-frame/script`, `--json`, exit 1 erro/2 uso), control TCP `127.0.0.1` JSON-lines 60s/16conns (`engine.execute/engine.commands/ui.menu.invoke|list/render.frame`).
- Script: `script/src/runtime.rs __exec/__query/__print/__undo/__task/__file` + `ACTIVE thread-local` + `prelude.js app.project` (lê via `__query` snapshot JSON, edita só via `__exec` → undoable) + `matchnames.rs ADBE*` + `beginUndoGroup/endUndoGroup` + File sandbox (só pasta projeto, sem rede sem pref).
- Comparação ciclo Hermes: EffectCraft `intento→execute→edit→history→render_frame→artifact` é 2 hops; Hermes `Agent→TaskRun/Policy→Commands→Engine→Verified→ArtifactStore→Experience Compiler` é 6 hops com authority/verifier que EffectCraft NÃO tem. **Caminho mais curto: ADAPT_CONTRACT `__query vs __exec` + `execute_checked` + `batch` para dentro do TaskRun/Policy Hermes, sem criar segundo TaskRun.**
- `script_ui{list/get/click/set/close}` + `ui_*` bridge permitem operar janelas ScriptUI — útil para ops sem semântica, mas NÃO mecanismo obrigatório (responde §6.6).

## 3.8 WASM/web (FACT — IMPLEMENTADO com gaps)

- `web.md`: `apps/effectcraft-web` mesmo engine+egui em wasm32 via `cargo xtask web/wasm`, eframe WebGPU (WebGL2 fallback), ~58MB→17/10MB gzip/Brotli, flags `?empty/demo/home/storage/memory/noworkers/frameworkers/nogpuworkers/nosw`.
- Sem SharedArrayBuffer: job workers (`engine/src/offload.rs WorkerRequest{project,footage,job}`) + frame workers (`engine/src/remote.rs diff/patch`) cada um com próprio WebGPU device; `render::passes in_passes` + `Accelerator::settle`, 24 passes→CPU; `?nogpuworkers`=CPU.
- Disk OPFS `effectcraft-cache/v1` LZ4+checksum + `DiskIndex` + `PrefetchStore`; persistência mirror OPFS→IndexedDB→memory; `window.effectcraft.request/execute/commands/inspect/renderFrame/screenshot/addFile/.../workerFrameCheck`.
- Comparação 7 arquiteturas §6.7: (1) app externa — isolamento máximo, latência IPC alta; (2) web embutida Electron — REJEITAR (egui em webview ≠ React, 58MB, dois runtimes); (3) engine Rust + frontend Hermes — RECOMENDADO via CLI/MCP headless; (4) WASM+API tipada — VIÁVEL para preview isolado, não para authority; (5) Rust nativo + protocolo local — VIÁVEL via control TCP/MCP bridge, N-API desnecessário; (6) reimplementação seletiva — RECOMENDADO só para math/time/keyframe (~2k linhas), nunca renderer; (7) híbrida módulos — RECOMENDADO (filmcraft time/media/interchange + effectcraft keyframe/effects-contract + Hermes TaskRun/authority).

## 3.9 Proposta obrigatória: Command Registry criativo compartilhado (ADAPT_CONTRACT, owners Hermes preservados)

Mapeamento EffectCraft → Hermes (não substituir owners):

| EffectCraft | Hermes destino | Owner | Ação |
|---|---|---|---|
| `CommandSpec{id,label,menu,shortcut,params,enabled,run,journal}` + `find/check_params/schema` | `workstation/creative_commands.py:CommandRegistry` | Creative Operations | ADAPT: adicionar `label/menu/shortcut/params_doc/json_schema/enabled_reason`; `execute_checked` strict reject unknown (-32602); `capabilities+denial` |
| `engine.batch{atomic,$N.key,fold,NOT_IN_BATCH}` | `workstation/creative_transactions.py` | CreativeHistory | ADAPT: `$N.key` refs + `fold()` 1 undo + rollback nomeando step; MANTER 409/idempotência Hermes |
| `History{branches,merge_key,goto,levels}` | `workstation/creative_transactions.py` | CreativeHistory | ADAPT_ALGORITHM: branching + merge_key (drag) + `history{goto}`; MANTER revision(int) Hermes |
| `prop.set/addKey/keys.*{timeBase layer|comp,snap_nearest}` | `workstation/creative_timeline.py` + `creative_time.py` | Timeline/Time | ADAPT: `timeBase` explícito + snap a frame + warnings out-of-range |
| `list_commands/describe/get_state` | `workstation/creative_apps.py` + gateway MCP | AppResolver/Router | ADAPT: descoberta bounded (`filter/enabled_only`), nunca 300 tools no prompt |
| `__query vs __exec + beginUndoGroup` | `workstation/operational_capabilities.py` + skills | Capability Router | ADAPT_CONTRACT: leitura snapshot vs escrita só via comando journaled |
| `Time Tick + FrameRate + drop-frame display` | `workstation/creative_time.py` | Time | ADAPT_CODE seletivo (`saturating/nonzero`, display vs sample); NÃO trocar Fraction por Tick sem prova |
| `keyframe math (ease/spatial/roving/velocity)` | CWN-07 Graph Editor | Timeline | ADAPT_ALGORITHM math, UI Hermes própria |

**Não portar:** renderer/306 efeitos/GPU/egui (WRAP ou REFERENCE_ONLY); nunca segundo TaskRun/authority/verifier.
