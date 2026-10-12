# CQL-03 — Native editor UX acceptance (prepared, NOT product-E2E qualified)

These are **reproducible product scenarios**, not claims that UI works. Test on a Windows Electron build pinned to the exact head of PR #81 only after authenticated H-C2 becomes operational. Human feedback is distinct from code proof.

## Entry and basic editing

| ID | User interaction | Required independent oracle | Current status |
|---|---|---|---|
| UX-01 | Open `/creative` in Electron | Editor mounts without hook/provider errors; TaskRun owns project | BLOCKED_EXTERNAL_DEPENDENCY |
| UX-02 | New 640×360/30fps project, add text and shape | Python canonical HEAD new revision + exactly one created source | BLOCKED_EXTERNAL_DEPENDENCY |
| UX-03 | Select/deselect layer | Inspector selection reflects canonical element ID; no content revision for selection-only | NOT_RUN |
| UX-04 | Change position, opacity, scale in Inspector | Canonical CAS revision; seek at same time changes decoded preview pixels | BLOCKED_EXTERNAL_DEPENDENCY |
| UX-05 | Add 0s/1s/2s keyframes and graph easing | Canonical rational timestamps + out-of-order frame comparison | BLOCKED_EXTERNAL_DEPENDENCY |
| UX-06 | Play/pause and scrub to frame 30 | Playhead, preview, and exported frame 30 agree; no accumulated clock drift | NOT_RUN |
| UX-07 | Undo last edit and redo it | Same source revision lineage, real pixel output returns to prior/next state | BLOCKED_EXTERNAL_DEPENDENCY |
| UX-08 | Save/close/reopen project | Native source SHA and canonical metadata restored; app does not fabricate local editor copy | BLOCKED_EXTERNAL_DEPENDENCY |
| UX-09 | Human edit followed by agent edit | Distinct canonical revisions with correct actor authorization and CAS | BLOCKED_EXTERNAL_DEPENDENCY |
| UX-10 | Agent edit then stale human edit | 409 typed conflict, no source overwrite or optimistic success | BLOCKED_EXTERNAL_DEPENDENCY |
| UX-11 | Cancel pending render | No leaked child process, no false verified receipt | NOT_RUN |
| UX-12 | Invalid property value / missing native source | Typed error in Inspector, no black fallback and no UI freeze | NOT_RUN |
| UX-13 | Three.js GLB + HyperFrames + native title and blur | Real pixels and preserved EffectCraft source; native CLI source reference baseline already proven by CQL-02 | PASS_NATIVE (CLI only) |
| UX-14 | Export 2s/60frame H.264 and reopen | FFprobe+decode independently verifies exact frames, alpha source separately | PASS_NATIVE (CLI only) |

## Qualification procedure

1. Install or open a native Windows Electron build pinned to a SHA and record it; do not run unverified fixture impersonation as an authenticated session.
2. Use a temporary Hermes profile and TaskRun, with real backend-attested owner and physical/machine UI interaction.
3. Capture pre/post revision ID, ETag, actor, time, screenshot/video and native output/decoder hashes.
4. For each case, retain failing reproduction steps and actual UI/state logs; never classify a JSX unit test as a native E2E.
5. Test one negative security path per mutation (revoked owner, stale CAS, wrong sender/session) without enabling broad unsafe permissions.
6. Only mark PASS_INTEGRATION when app/UI event, backend canonical readback, and independent file/pixel verification all agree.

## UX metrics (PENDING)

Record startup, preview seek, inspector edit→pixel, playhead drift, source reopen, undo/redo correctness, keystroke counts and p50/p95 across comparable runs. Do not assert percentages without a baseline. Evaluate human perceptual quality explicitly as `PENDING_HUMAN_VALIDATION`.

**No production UI code changes are authorized in CQL-001; send validated defect reports to the PR #81 owner.**
