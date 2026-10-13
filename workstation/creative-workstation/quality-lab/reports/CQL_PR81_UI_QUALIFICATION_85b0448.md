# CQL-03 — independent PR #81 React/Chromium qualification

Target PR #81 HEAD: 85b0448fa01261bf425764f188edf443d8194b8b (unchanged during probe).
Lab PR #86 runs a separate exact-head guarded script, scripts/probe_editor_components.cjs. It bundles the actual unmodified React components with one React package instance, loads them into headless Google Chrome, and exercises DOM mouse interactions. Fixture: schema-valid *synthetic* canonical HEAD, validated by the actual CreativeWorkspaceContext. This is component testing, not authenticated Electron/TaskRun/backend E2E. Browser errors and source SHA-256s are persisted.

Evidence: evidence/pr81-chromium-85b0448/CQL_CHROMIUM_UI_OBSERVATIONS.json and creative-chromium-component.png.

## Observed: five PASS_UNIT

- UX-EMPTY: no editable timeline is shown before canonical HEAD.
- UX-HEAD: accepting canonical HEAD displays only its revision dddddddd…; no optimistic source mutation.
- UX-TRACK: clicking actual track displays Track: Video A in Inspector.
- UX-CLIP: clicking actual clip displays Clip: Visual Clip in Inspector.
- UX-SEEK: clicking timeline ruler at x=153px updates local playhead and Preview label to 1.530s; canonical revision remains unchanged.

## Observed: four FAIL (component scope)

### F-008 — Graph Editor React Hooks order violation (P0 motion editing)

Reproduce: mount CreativeGraphEditor with empty selection, accept a canonical projection containing two keyframes, select their layer. Chromium logs "React has detected a change in the order of Hooks called by CreativeGraphEditor" and "Rendered more hooks than during the previous render." Graph is not visible.

Root cause: CreativeGraphEditor.tsx conditionally returns before subsequent useMemo and useCallback hooks; selection changes hook call count.

Recommendation to PR #81 owner: ensure every hook executes in the same order unconditionally; move early return below hooks and handle null layer within memo callbacks. Regression must exercise empty → selected keyed layer → deselected → selected again.

### F-009 — Preview Play button is inert (P1)

Reproduce: click the real Preview Play button after loading a canonical fixture. The context isPlaying remains false.

Root cause: CreativePreview.tsx handlePlayPause only logs to console, unlike CreativeToolbar which calls setIsPlaying. Recommendation: connect Preview to the shared playback authority/state and qualify real preview playback separately.

### F-010 — Inspector Speed editor does not submit a command (P1)

Reproduce: select real clip, fill the Speed number input with 1.5. No new acknowledged revision is received. CreativeInspector.tsx onChange logs to console. This is missing UI wiring, not proof of a defective backend.

Recommendation: after H-C2 is truly authenticated, use typed canonical command with CAS/ETag readback, stale rejection, and persisted reopen; no ad hoc JS actor/session authority.

### F-012 — Rational FPS frame stepping mismatch (P1 precision)

Reproduce: accept canonical fixture at 30000/1001fps, click actual CreativeToolbar Step Forward. Observed playhead delta 0.03333333333333344s (1/30), expected exactly 1001/30000s. Real Chromium component FAIL, although rendered frame timing has not yet been compared. Source: CreativeToolbar.tsx fixed 1/30 step and formatting; CreativeTimeline.tsx also formats frames as fixed 30. Owner should use canonical RationalFps and test long seeks without drift.

## Additional NOT_RUN or BLOCKED

- Toolbar Undo, Redo, Save and Export render buttons without onClick handlers in current source. Native workflows remain NOT_RUN.
- Preview draws a placeholder colored rectangle for video clips, rather than decoded source frames. Actual preview/export fidelity remains NOT_RUN.
- Rational frame step is FAIL in Chromium as detailed above; precise export/preview drift remains NOT_RUN.
- Electron main.ts still registers resolveTrustedOwner: () => null and open/apply throw creative_owner_unavailable. H-C2 native human↔agent round trip remains BLOCKED_EXTERNAL_DEPENDENCY; a unit-tested TaskRun resolver is not itself product integration.

## CQL-05 scoped performance

12 measurements of Chromium ruler-click-to-updated-Preview-label recorded in the JSON. The timings are Playwright+local React interaction only; they do NOT measure decoded preview pixels, native Electron, TaskRun IPC, video rendering, GPU, or agent cost. No baseline comparison or claimed performance gain.

## Exact reproduction

Run in C:\Github\hermes-agent-creative-quality-lab:

    $env:CQL_TARGET_HEAD='85b0448fa01261bf425764f188edf443d8194b8b'
    $env:CQL_PR81_CHECKOUT='C:\Github\hermes-agent\.worktrees\hcw-hybrid-01'
    $env:CQL_NODE_MODULES='C:\Github\hermes-agent\node_modules'
    $env:CQL_UI_REPORT_DIR='C:\Temp\cql-ui-next-clean-dir'
    node workstation/creative-workstation/quality-lab/scripts/probe_editor_components.cjs

The script refuses an incorrect checkout SHA before launching Chromium or writing results. First attempt exposed duplicate React packages inside the harness itself; it was fixed by forcing a single React module resolver. No PR #81 code was edited. Do not treat harness setup errors as product defects.

Next: hand these findings to PR #81 integrator; add feasible negative UI contract coverage without touching their branch; requalify only after change on a newly pinned SHA. CQL-04 remains blocked until a real authenticated TaskRun boundary exists.
