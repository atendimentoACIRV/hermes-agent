# HCW-HYBRID-FINAL — Plan review after IPC boundary work

Date: 2026-10-12, development-only. This is a priority and qualification review,
not a new code-to-code audit or an authorization to merge. Source: PR #81
and in-tree HCW execution ledger/evidence; earlier audit CW-AUDIT-02 remains applicable.

## Verified progression since the previous checkpoint

- Real HyperFrames and EffectCraft native engines, source-preserving three-revision
  workflow, 2s moving PNG/MP4 and parameter edit tracer were proven on Windows
  in earlier session; historical scoped Creative pytest result: 152 passed /
  1 skipped in 158.95s. Do not present it as exact-new-HEAD CI.
- Canonical CreativeDocument store, HEAD CAS, interprocess lock, idempotent
  receipts, fail-closed concurrent edits and TaskRun-scoped Python CLI
  canonical-create/open/apply-batch implemented.
- React CreativeWorkspaceContext projects canonical revision/ETag and submits
  bounded typed edits via preload; no second authoritative writable project.
- This session corrected Electron IPC trust boundary: owner resolution now
  takes the exact invoking IPC sender rather than a global active window,
  reattests after async action/readback, rechecks renderer admission across
  async boundaries, and requires a typed canonical commit receipt whose revision
  matches the subsequently loaded authoritative HEAD.
- Targeted Electron Vitest: 11 passed across creative-canonical-ipc.test.ts
  and preload-creative-canonical.test.ts. ESLint targeted exit 0.
  Full electron typecheck currently blocked by unrelated existing
  electron/git-review-ops.test.ts:124 simple-git callable type error;
  no claim of globally clean TypeScript compilation.
- main.ts currently registers registerCreativeCanonicalHandlers with
  resolveTrustedOwner: () => null, open/apply that reject. This deliberate
  fail-closed configuration is the remaining CRITICAL H-C2 runtime gate.
  There is no proven main-owned, backend-attested TaskRun identity for the
  renderer's active window. Do not substitute renderer taskId/runId,
  renderer-provided sessionId/profile or ambient profile guesses.

## Architectural priorities (reordered to remove false progress)

### P0A — Authenticated TaskRun identity source (blocks live H-C2)

Define a backend attestation backed by the owning gateway's live session,
active Kanban task/current run, correct profile and connection. The Electron
main process must bind it to a specific admitted webContents/mainFrame,
not to a process-global active window. Attestation must expire/revoke on
navigation, window destruction, profile/connection switch, TaskRun finish,
human-control lease or authority supersession. Main->backend interaction
must use existing authenticated transport and backend policy; NEVER accept
an arbitrary executable path, shell command, user-selected task ID or
actor identity from renderer as trust evidence.

Acceptance: wrong/closed window, forged task/run/session/profile, competing
connection, stale lease, cancelled TaskRun, user-control-active and
unauthenticated actor all fail closed BEFORE project mutation.

### P0B — Real authorized IPC->TaskRun->CAS round trip (blocks H-C2)

Wire the main-process injected owner resolver and bounded open/apply backend
adapters to the existing Python canonical command surface using authenticated
transport, not spawned arbitrary renderer commands. Keep the current strict
IPC parser and verified commit/readback. Test actual Electron UI mouse edit,
followed by Hermes agent edit of same layer/project, successive revision
IDs and ETags, source hashes and browser restart/reopen. 409 must refresh
without optimistic UI mutation. Include concurrent second-window case.
Only this demonstrates H-C2 manual/agent integration; mocks are insufficient.

### P0C — Complete authority identity and native transaction (H-C4)

Bind actor identity to authenticated main/backend principal, not to an
actor_type string in command JSON. Add safe staging and commit/rollback for
actual EffectCraft/HyperFrames native mutations, recovery after interrupted
two-engine edit, and durable undo/redo. Confirm CAS receipt cannot be replayed
across a superseded TaskRun even if valid as historical project data.
TaskRun check and policy must cover all mutating entry points, including
legacy writers or an explicit migration gate.

### P1 — EffectCraft Web manual editor in isolated Electron view (H-C5)

Verify legal/license compatibility and source integrity first. Isolate
WebContentsView and IPC, enforce least privilege and authority leases.
Use canonical typed commands instead of parallel project snapshots.
Do not deploy Web UI integration ahead of P0A/P0B; it would create an
attractive but unauthoritative editor.

### P2 — Shared parameters/time and compositor (H-C3/H-C6)

Wire rational frame timestamps, parameter bindings and effects to actual
engines and shared project, including seeks, colors, keyframes, masks/mattes,
sound and alpha. Reuse EffectCraft where native capability exists.

### P3 — Cache / on-demand render (H-C7/H-C8)

Introduce bounded source-fingerprinted frame cache, selective invalidation,
full parity checks against the already-verified PNG sequence path, explicit
timeouts and process budget. Then qualify native on-demand frame rendering.

### P4 — Nested composition and final demonstration (H-C9)

Dependency DAG, true nested timelines, loop rejection, source-preserving
restart, 1920x1080 30fps 10-second editable project and independently
decoded PNG/MP4 proof. End with full native/Electron E2E + H-079 reconciliation
and exact-HEAD CI. No merge into main without explicit authorization.

## Current milestone evidence levels

| Milestone | Level | Remaining gating proof |
|---|---|---|
| H-C0 | NATIVE_PARTIAL | H-079/upstream and full native release gates |
| H-C1 | NATIVE_E2E_PARTIAL | Integrated live manual edit and 10s final project |
| H-C2 | BACKEND_AND_UI_CONTRACT_TESTED | Backend-attested sender owner, live Electron human+agent test |
| H-C3 | NATIVE_VARIABLES_PARTIAL | Runtime two-way binding/seek tests |
| H-C4 | BACKEND_CAS_PARTIAL | Attested actor; native dual-engine atomicity, durable undo |
| H-C5 | NOT_INTEGRATED | Secure EffectCraft Web/Electron manual project |
| H-C6 | NATIVE_EFFECT_PARTIAL | Masks/mattes/keying and shared editor |
| H-C7 | CONTRACT_ONLY | Runtime bounded cache + invalidation |
| H-C8 | NOT_INTEGRATED | On-demand hybrid frame parity |
| H-C9 | DAG_UNIT_TESTED | Nested native 10s 1080p demo and release qualification |

## Stop and reporting rules

1. Do not mark P0A or H-C2 complete until the main-process resolver is genuinely
   backed by a validated live TaskRun; current null resolver must remain denied.
2. Keep exact command/log/exit receipts; distinguish test mocks from native/Electron E2E.
3. Preserve the protected main checkout, draft PR, pinned native sources and
   saved immutable source revisions.
4. Update HCW_HYBRID_EXECUTION_STATE.md and publish only verified scoped commits.
5. If incomplete, end every work session with a full, self-contained copyable
   continuation prompt, updating exact local and remote HEADs and the first
   executable action.

## P0A checkpoint — 2026-10-12

Verified first contract-only increment: main-side attestation verifier 14 new tests / 25 creative Electron tests GREEN; no authenticated backend attestor or trustworthy main per-window lifecycle registry wired. Production IPC remains deny-all. This does not satisfy P0A or enable P0B. First remaining action: implement genuinely authenticated backend TaskRun+principal+lease attestation, bind it to main-owned window connection/profile/session and reverify on navigation/rehome/cancellation; only then wire canonical-open/apply-batch to the existing main bridge.


## P0A backend continuation — 2026-10-12

The missing backend-bound admission helper was implemented with TDD: user/session record equality, unique live Kanban claim, CreativeRunContext.validate, ContextVar-only gateway key and TTL bounded by task/run leases. 25 focused Python backend/CAS tests passed; three meaningful RED failures recorded. **Remaining blocker:** an authenticated HTTP principal is not automatically the TaskRun gateway principal and cannot legitimately conjure its session key; `main.ts` still has no verified sender-scoped window/session/connection binding. No server RPC wired, no real Electron manual/agent E2E, no H-C2 promotion. Immediate next action is to prove authenticated request-to-TaskRun binding using native gateway transport, implement narrowly scoped canonical RPC and only then connect `creative-taskrun-attestation.ts` to the main handler. Keep deny-all when binding fails.

### P0A: verified HTTP session–TaskRun *discovery*, without mutation grant

2026-10-12 continuation after 85b0448fa: Added workstation/creative_http_identity.py and GET /api/workstation/creative/owner-readiness in hermes_cli/web_server.py. Read-only authenticated interactive-principal → canonical SessionDB (user_id/session_key) → unique live Kanban TaskRun lookup with workspace, profile, expiry, lock and supersession fences. OAuth/native-session request.state.session is required; loopback token and service token are not considered interactive actor authentication. TDD RED module absent (exit 1), route not registered (1 failed exit 1), GREEN 38 passed, 0 failed in 47.06s, 1 Starlette/httpx deprecation warning, command python -m pytest workstation/tests/test_hcw_http_principal_owner.py workstation/tests/test_hcw_taskrun_backend_attestation.py workstation/tests/test_hcw_hybrid_taskrun_command.py workstation/tests/test_hcw_hybrid_revision_cas.py -q. No sessionKey or claimLock returned; authorityGranted=false. Not an authenticated mutation RPC or live gateway authority proof. main.ts remains resolveTrustedOwner: () => null; P0A PARTIAL, P0B BLOCKED; H-C2 no promotion, H-079 and exact-head CI unverified.
