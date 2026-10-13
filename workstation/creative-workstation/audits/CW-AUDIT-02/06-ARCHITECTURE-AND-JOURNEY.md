# 06 — Arquitetura de experiência integrada e jornada de aceitação

## Produto e owner
UM CreativeDocument persistente; Design, Motion, 3D, Montage e Export são VISÕES do mesmo projeto. Renderer não substitui owner de projeto; engines externos recebem snapshot versionado e devolvem frame/audio/receipts. Humano e IA são produtores dos mesmos comandos tipados.

Fluxo:
Human pointer/keyboard OR Hermes agent typed call
 → shared selection + bounded capability discovery (READ)
 → CreativeCommand {projectId, baseRevision, actor, scope, idempotencyKey, targetIds, params}
 → existing Workstation policy/owner/revision CAS
 → CreativeTransaction stage clone, validate, atomic persist+journal/history
 → project revision + independent readback
 → React canvas/timeline/Inspector/Graph view
 → render adapters SVG/Canvas, Three.js, media/FFmpeg, qualified specialized engines
 → pinned revision and canonical frame seek, fonts/media/GPU readiness
 → PNG/ordered-frame MP4 with decoded readback and immutable receipt.

## Documento canônico
Extend EXISTING workstation/creative_document.py; do not clone schema as sovereign renderer state. Document {schemaVersion, projectId, revision/etag, compositions, assets, sourceRefs, metadata}; Composition {compositionId, dimensions, fps rational, timeline, layer graph, camera, audio}; Layer {stable id, kind, parentId, transforms, properties, keyframes, effect refs, sourceId}; Clip {timelineRange, sourceRange, linked AV, speed/reverse}; Asset {hash, mime, original editable source, metadata, sourceURI, provenance/license}. External SVG, PSD, .ecproj, GLB retained as linked native source when parsing cannot preserve editability. Unknown future schema must refuse unsafe write, never flatten silently. Use CanonicalTime and RationalFps from Hermes.
UI gesture and agent tool must call one registry, get same command result and one journal. 409 revision conflict explicit. Undo/redo tracks exact committed doc revision; one drag is one undo; disabled layer errors include reason.
Asset generation/render are external effects with receipts, not reversible editor transaction.
Agent receives READ-ONLY selection projection {projectId, revision, compositionId, selected layer/keyframe IDs, property paths, playhead, viewport, fps}; no click needed where typed API exists. Actor scope and TaskRun remain owned by workstation, never minted by scene/motor.

## Minimal UI
Left assets/layers+scene outline; center true preview/canvas direct selection and 3D gizmo; right Inspector; bottom Timeline/Graph; top mode switch Save/Export with revision and dirty marker; contextual agent bar uses selected IDs. Pinned panes persist as view metadata, not duplicate project data.

## Semantic Edit Plan
AI proposes batch → stage isolated copy-on-write document → preview through REAL render from candidate revision → accept subset/reject with dependency checks → CAS against latest human revision → commit once with actor provenance → readback and updated view. Manual change between proposal and commit => 409/rebase, not overwrite. Unknown source, failed render or partial external effect not DONE.

## Vertical 17-step acceptance matrix
| Step | Scenario | Observable evidence |
|---|---|---|
| 1 | Electron opens editor | packaged UI, buttons/direct manipulation respond |
| 2 | Create persisted project | canonical revision + digest survives app restart |
| 3 | Import image, logo, font | source hashes, font loading/permission and provenance |
| 4 | AI creates 2D design | bounded typed commands and no pixel-click fallback |
| 5 | Human changes text/position/color | same canonical registry and revision change |
| 6 | AI moves existing selected object | expectedRevision/targetId; 409 if human edited later |
| 7 | Insert GLB/3D | visual GLB WebGL layer saved within SAME document |
| 8 | Edit object/camera | commands reflect controls and source model |
| 9 | Export actual PNG | frame decoded with expected pixels/size/hash |
| 10 | Continue editing same project | export is derivative, editor remains live |
| 11 | Keyframe 2D, 3D, camera | property IDs + rational canonical times |
| 12 | Agent edits selected easing | same evaluator and command schema |
| 13 | Human edits Graph handles | merge drag+1 undo, value/speed visual parity |
| 14 | Playback | out-of-order seeks, seed/readiness, time stable |
| 15 | Export MP4 | canonical frame graph, ordered audio+video job |
| 16 | Independently decode | ffprobe count/fps/dims/duration, decoded frames differ and match preview |
| 17 | Close/reopen | source IDs, assets, 3D, keyframes, camera, history recover |

## Delivery steps without false success
V0: single source/typed bridge for 2D, asset import and real PNG.
V1: GLB, camera and true WebGL frame in same project; PNG with depth and transparency.
V2: keyframe math, Graph Editor, 2D/3D seek parity.
V3: ordered frames to ffmpeg/ffprobe with audio, provenance, cancellation.
V4: NLE/effects/native specialty engines and performance after measured bottlenecks.

## Real render contract
Each node consumes pinned revision R and canonical time T and yields premultiplied RGBA in declared color space or audio samples, not a state dict. Explicit z/composition/depth/camera policy; await media/font/GPU barriers; seeded deterministic procedural nodes; isolate JS under CSP restricted origin; never embed untrusted code in privileged Electron. PNG produces decoded frame at T; MP4 consumes frames T=i/fps, with provenance R and assets. Viewer may render lower-resolution preview but export must not silently degrade or substitute black. If GLB unsupported, preserve asset and show BLOCKED, do not flatten. Cache keys include revision/frame/dimensions/engine/font/profile/source hashes; prove cached vs uncached parity before optimizing.

## Engines as adapters, never independent project owners
EffectCraft property/keyframe/effect adapter; FilmCraft NLE checks; PhotoCraft raster adjustments; VectorCraft geometry; Penpot interoperability; Three.js WebGL real scene; FFmpeg supervised codecs; HyperFrames/Remotion optional backends with capability and license checks. None can bypass authority, journal, source provenance or verifiers.
