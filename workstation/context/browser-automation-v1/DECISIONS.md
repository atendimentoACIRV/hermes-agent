# Decisions
1. Canonical runtime must remain the existing getWorkstationBrowserRuntime() singleton. A second WorkstationBrowserRuntime gave false ACK without effect in the wrong instance; never duplicate.
2. Playwright connectOverCDP is technically feasible in an isolated 127.0.0.1 test profile. Do NOT expose a real user Chromium session or treat this external connection as authorized production actor; require BrowserTask lease/owner mediation before product use.
3. Native authenticated controller already completes two parameterized local-page transactions with independent snapshot/server readback and zero model calls in the harness. Prioritize binding to existing DeterministicRoutineRunner/ProceduralMemory, not inventing a new engine.
4. Browser owner ACK/receipt is not proof of remote effect. Require readback; uncertain mutations must not be retried blindly.
5. Missing ephemeral refs can be safely re-acquired from stable data-testid anchors in the same authorized task; no arbitrary cross-site selector fallback.
6. H-079 upstream-qualified Stage A not completed for this new branch. Earlier authorization in a separate local C2C branch does not grant production promotion here. Only isolated tests and documentation in this checkpoint.
7. Playwright C2C parallel worktree contains unreleased native crash replay work. Reuse tested concepts, not wholesale code without deliberate integration and gates.

8. Persistence is proven by reloading ProceduralMemory across Python processes against the exact existing fixture BrowserTask; fabricated run IDs are rejected with BrowserTask run mismatch, not silently translated. Cross-TaskRun execution requires a truly admitted new BrowserTask.
9. Test-only procedure lifecycle promotion is backed only by disposable fixture server effect + snapshot readback and strictly scoped 'test_only' loopback; never interpret it as production validation/promotion authority. Do not reuse this JSON-lines test bridge as production API.

10. BAV04 adds only **test-owned crash/reconciliation contract** under workstation/tests and disposable Electron runners; canonical ExecutionJournal (append with acceptance fsync), ArtifactStore and DeterministicRoutineRunner.resume_ref are reused. Production runtime and canonical owners untouched while H-079 unqualified.
11. A worker-constructed admission dict is synthetic fixture metadata, not proof of production lease, new TaskRun, human/agent authority or restart recovery. Treat such proof as test-only and require real authenticated owner on next stage.
12. Lost response after externally completed effect is UNCERTAIN. Never re-dispatch until independent snapshot + server-effect delta match persisted pre-effect baseline. A successful owner ACK alone is insufficient.
