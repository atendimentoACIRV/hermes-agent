# CWN renderer-first MVP: first editable visual workspace (2026-10-11)

**Status: DEVELOPMENT_ONLY / isolated draft.** Source `origin/main@a2b56db1bc9e0b5acf48d94fa86a9844a1005842`; H-079 `PASS_WITH_AUTHORIZATION` permits isolated work, not production promotion. Related architectural authority D-043; this patch does **not** replace the Python `creative_document`, `creative_commands`, `creative_project_store`, `creative_3d`, `creative_export` owners and does not claim that renderer-local edits are synchronized with the native durable project.

## Verified implementation surface
- `CreativeWorkspacePage` now mounts its own `CreativeWorkspaceProvider`; previously `useCreativeWorkspace` had no parent provider in the installed route.
- Open explicit JSON project from file or create a new vector project in the existing renderer context. Validate IDs, coordinates, dimensions, FPS and layer/keyframe content. Reject media, unknown script/3D owners and malformed projects instead of silently losing content.
- An explicit renderer-local typed `CreativeEdit` reducer creates text and rectangle layers, changes text/color/position/dimensions/opacity, inserts and edits keyframes, renames a project and deletes a layer. The existing context keeps bounded undo/redo snapshot stacks (not a new persistent state owner).
- SVG vector preview interpolates property keyframes; ruler, preview playback, mode switch, Inspector and Graph Editor controls are connected. Clicking a shape or text selects the layer. Save an editable JSON file and export the **current SVG frame** through an explicit browser download.
- Rendering escape tests cover HTML/XML text payloads, finite frame values, invalid opaque code/media, and historical immutability. Source routes remain unchanged except provider installation in the existing page.
- Windows Vitest targeted model/context/page specs passed; renderer `tsc -p apps/desktop/tsconfig.json --noEmit` passed. The full Electron typecheck is blocked on known `simple-git` baseline lock mismatch addressed in separate PR #70 (this branch based on origin/main).

## NOT delivered / promotion gates
1. **No shared native Creative Document edits.** Renderer-local undo, open and download are an initial interactive standalone layer; AI/tool-driven native commands and `expectedRevision` 409/CAS must be wired through the existing Python/Electron authority and journal before production.
2. **No MP4/exported motion video.** SVG is one current frame, not animation encoding or verified FFmpeg. A real frame-by-frame export with distinct decoded frames and source-revision binding must pass H-079/D-043 gates.
3. **No GLB/Three.js compositing yet.** Existing Python `creative_3d.py` is separate; importing untrusted `three_js_scene` into the renderer MVP is refused rather than faked or flattened. Maintain source editability.
4. No packaged Electron cold-start/restart and shared human/agent editing E2E, no native WebContentsView/handoff ownership proof, no exact-HEAD CI, no user project/data migration.
5. Full EffectCraft/HyperFrames/Remotion/OpenReel/Natron/Graph Editor parity is deferred. In particular, `CreativeGraphEditor` currently edits typed keyframe value and easing; interactive tangent manipulation and Bezier curve preview are not claimed.

## Next minimal executable slice
CWN command bridge: connect human layer commands to the existing canonical `CreativeCommand` Python reducer and `creative_project_store` via a narrow typed Electron IPC provider; same `expectedRevision`, actor/scope and versioned schema for human and agent. Qualify file source fidelity, conflict, cancellation, undo, persistence on restart, and zero execution of unknown source code. Then frame-rendered PNG/MP4 with independent ffprobe, and finally native Three.js GLB scene overlay with provenance. Do not merge this isolated draft without these proofs.
