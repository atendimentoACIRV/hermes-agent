# 05 — OpenReel + Natron Deep-Dive (CW-AUDIT-01)

Snapshots sem `.git` (SHA NOT_VERIFIED). Read-only, sem execução.

## 5.1 OpenReel (`openreel-video-main`, MIT 2024-2026 Augustus Otu)

Stack FACT: React+TS+Zustand+MediaBunny+WebCodecs/WebGPU/WebAudio/Three.js, pnpm, `apps/web,apps/desktop`, `packages/core,ui,agent,agent-runner,creation-*,fxpkg,image-core` (`README:113-124`).

**`packages/core/src/actions/action-executor.ts` (FACT):** `ActionExecutor{validator,history:ActionHistory,inverseGenerator,lastAddedIds}` · `execute:162 validate→snapshot JSON→inverse→apply→push` · `executeMany` stop-on-error · `undo:223 undoGroup+resolveSpecialMarkers` · `redo:262` · `applyAction:319 getActionHandler(type) ?? fallback project/media/track/clip/effect/transform/keyframe/transition/audio/subtitle/marker` + `recalculateTimelineDuration` + `markProjectModified(Date.now())`.
Clip: `add:800,remove:880,restore:889,move:899,trim{in,out}:933,split{time}:958 (out=in+offset),merge:991,rippleDelete:1015,rippleRestore:1102,slip{delta}:1124,slide{delta,prev,next}:1145,roll{left,right,delta}:1178,trimToPlayhead:1208,closeGapBefore:1241,consolidate:1280`. Track: `add/duplicate/remove/restore/reorder/lock/hide/rename/mute/solo` + owned `text/shape/svg/sticker/adjustment/motionInstances:74-127`. Sync `nestedInstances` manual só move/trim/slip/playhead (`1339-1364`).

**`packages/agent/src/host.ts` (FACT):** `EditingHost{getProject,applyAction,beginTransaction,commitTransaction,rollbackTransaction,runJob(exportVideo|Audio|Frame),capabilities(),multicam?,requireOpenProject(),createProject?/openProject?/listProjects?/saveProject?/importMediaFromUrl?...}` (`host.ts:228-308`). **Bug-class FACT:** `text/shape/sticker/svg create/update/remove` raw só appendam `project.textClips` e nunca chegam ao TitleEngine — renderizam nada (`287-307`); host contorna com `createTextOverlay…fix engine-aware`.

**`packages/agent/src/loop.ts` (FACT):** `runTurn{host,llm,tools,system,messages,confirmGate,onEvent,limits:{maxSteps:12,maxToolCalls:64,maxTokens},dryRun,turnLabel="AI edit"}` · `beginTransaction` up-front · `isDestructive/isExpensive→confirmGate approve_for_turn|approve|reject (201-223)` · `dryRun→"[dry-run] would call X"` · `maxToolCalls→MAX_TOOL_CALLS transcript` · `maxTokens` entre steps · commit em end/budget/max, rollback em catch:267 · eventos `text_delta/tool_call/awaiting_confirmation/tool_result/turn_complete/error` + `usage{input,output}` · `Stop`=rollback parcial, `Undo this turn`=reverte turno.

**Riscos verificados (NÃO copiar sem validar):**
1. Same-track ripple — `rippleDelete:1022-1036` shifta só `track.id==clip.trackId` e `startTime>deletedStart`; sem sync-lock/patch/target. Hermes `creative_timeline.py` JÁ é superior (multitrack + locks). **KEEP_HERMES.**
2. Rate mapping float — `seconds:number`, `duration=in-out`, `add:829-833` fallback imagem=5s mágico, `speed/reversed` soltos, `playbackRate=speed` sem resample. Drift 23.976/29.97DF inevitável. Hermes `CanonicalTime` superior. **KEEP_HERMES.**
3. História fragmentada — snapshot `JSON.parse(stringify(project))` por execute (caro, perde Blob), inverso per-action + `__LAST_ADDED__` resolvido no push (`304`) — frágil em executeMany; `track/duplicate` structuredClone+randomUUID sem `Sequence::check`. Hermes transactions atômicas + 409 superiores. **KEEP_HERMES.**
4. Registry gigante — `registry.ts` ~15k linhas, `AGENT-GUIDE.md:11` 228 tools + `execute_action/batch_actions`; `tool-router.ts:70` filtra por turno mas follow-ups acumulam. Hermes deve expor bounded (`filter/enabled_only`), nunca 300 tools.
5. IDs `Date.now()` (`media/import:442`, `marker/add:750`) + `randomUUID` sem seed — não determinístico. Hermes IDs 32-hex + revision superiores.

**Veredito contrato:** EffectCraft/FilmCraft > OpenReel para bus compartilhado (dispatch único, `enabled()->reason`, undo Arc 200 + journal replay, Tick). OpenReel bom como **referência TS web imediata** (Zustand/MediaBunny/WebCodecs) + `EditingHost` seam + `runTurn` budget/confirm/dry-run (ADAPT_CONTRACT). Executor/registry: REFERENCE_ONLY, REJECT COPY_DIRECT.

Comparação NLE vs `creative_nle.py/timeline.py/commands.py/edit_plan.py`: Hermes já cobre split/trim/ripple/slip/slide/roll/speed + linked + locks + atomic + preview — OpenReel adiciona `merge/consolidate/closeGap/trimToPlayhead/multicam` como ideias, não código.

## 5.2 Natron (`Natron-RB-2.6`, GPLv2 — ATENÇÃO COPYLEFT)

Confirma fork: `README.md:1-7` Natron free GPLv2 similar AE/Nuke/Fusion, `Engine/,Gui/,HostSupport/,Renderer/,libs/,PythonBin/,Tests/,tools/`, snapshot RB-2.6. `LICENSE.txt:1-60` GPLv2 FSF + `LICENSE_SHORT.txt:5-8` GPLv2 or later. **Nunca COPY_DIRECT/ADAPT_CODE — só REFERENCE_ONLY ou EXTERNAL_PROCESS (processo separado + CLI/IPC).**

- Node graph/DAG: `Engine/Node.h:370 getInput,521 getOutputs,565 connectInput,577 disconnectInput,546 eCanConnectInput_graphCycles,445 auto-connection,722 deactivate,748 destroyNode` + `NodeGraphI.h,NodeGroup.h,GroupInput/Output.h,Dot.h,Backdrop.h,EffectInstance.h` — guarda ciclo, grupos como Python scripts.
- OpenFX host v1.4: `OfxHost.h,OfxImageEffectInstance.h,OfxClipInstance.h,OfxParamInstance.h,OfxOverlayInteract.h,OfxMemory.h,HostSupport/` + bundles `openfx-io/misc/gmic/arena` + comerciais RevisionFX/Sapphire/Furnace (`README:35-43`).
- Cache: `AppManager.h:208 getImage_diskCache,221 getCachesTotal/Disk` + `AppManagerPrivate.h:100-104 ofxHost/nodeCache/diskCache/viewerCache:Cache<Image>/Cache<FrameEntry>` + `Cache.h,TileCacheFile,FrameEntry.h,Image.h` — RAM/Disk/Viewer LRU tiled + proxy + `saveCaches/restoreCaches`. Realtime após render (`README:50`).
- Background: `Engine/BlockingBackgroundRender.h:38`, `AppInstance.h:439 onBackgroundRenderFinished`, `README:46` multi-graph + headless, `Renderer/NatronRenderer_main.cpp` CLI batch/farm sem GUI (crash render ≠ crash main).
- GPU: `GPUContextPool.h,GLShader.h`, OpenGL 2.0+ (`README:69-86`), fallback `LIBGL_ALWAYS_SOFTWARE=1`. Pipeline 32-bit linear OpenColorIO, formatos OpenImageIO+FFmpeg, Python expressions/PySide/callbacks, Curve+Dope, roto/rotpaint/tracking, multiview, projeto XML editável (`README:30-64`).

**EffectCraft vs Natron vs Graphite vs Hermes:**
- Natron nodal: DAG arbitrário + EXR multi-layer + OFX + cache tiled + farm — superior VFX pesada/keying/roto/CG. Custo: GPL + C++/Qt + processo pesado.
- EffectCraft layer-based: motion temporal + precomps + expressões + agente por comandos — superior MoGraph.
- Graphite procedural: vetor+raster node-based MIT — superior design interativo.
- Hermes: documento + comandos + TaskRun/authority — superior integração humano+IA (nenhum dos três tem).
- Temporal graph (keyframes) ≠ node graph (dependências): Hermes precisa AMBOS (CWN-07 Graph + CWN-09 nodal via Graphite-concept, nunca Natron embed).

**Classificação:** REFERENCE_ONLY (DAG guard, `FrameKey/ImageKey`, OCIO linear, OFX host API) + EXTERNAL_PROCESS (NatronRenderer CLI / farm). REJECT COPY.
