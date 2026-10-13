# BAV-00..12 — Hermes Browser Automation V1
2026-10-12. Principle: execute → reuse → learn → optimize. Never develop a second Browser owner.
| Phase | Verified state | Next |
|---|---|---|
| BAV-00 | Worktree created from origin/main a2b56db1bc; release H-079 HOLD | preserve parallel branches |
| BAV-01 | FEASIBILITY PASS: Playwright connects via loopback CDP to Hermes WebContentsView in disposable test profile; 1 effect | production authority-mediated adapter not done |
| BAV-02 | OPTIONAL: existing native CDP/controller fallback | no duplicate BrowserRuntime |
| BAV-03 | TEST HARNESS PASS: native authenticated controller, 2 parameterized executions, independent readback | bridge to DeterministicRoutineRunner |
| BAV-04 | NOT STARTED | durable restart, reconcile uncertain effects |
| BAV-05 | PARTIAL: versioned WebProcedure-compatible fixture JSON, recovered missing refs by testid | persist/promote with ProceduralMemory |
| BAV-06 | NOT STARTED | opt-in redacted recording |
| BAV-07 | PARTIAL test: testid re-acquisition | bounded adaptive recovery |
| BAV-08 | HOLD | integrate with existing Experience Compiler PR #82 |
| BAV-09 | HOLD | authorized Trello test board, read-only then approved mutation |
| BAV-10 | HOLD | React/Electron UI after runtime |
| BAV-11 | LOCAL EVIDENCE | controller 12 calls for 2 fixture runs, 0 model calls in test; no comparative savings |
| BAV-12 | HOLD | H-079, CI exact-head, Electron real release qualification |
Next RED: execute a promoted, parametrized ProceduralMemory.WebProcedure via DeterministicRoutineRunner and the existing authenticated BrowserTask controller with independently verified postconditions and restart; current harness still hardcodes orchestration. Respect H-079 upstream gate before any downstream product change.

## BAV-05 continuation, 2026-10-12
Test-only persistent replay contract now GREEN. Canonical ProceduralMemory persists a fixture-scoped promoted WebProcedure after test-server effect verification; two fresh Python worker processes load it and call DeterministicRoutineRunner.run_matching with Alpha(seed)/Beta/Gamma (replay). Existing Electron singleton + authorized loopback controller handles every web action; no runtime product code changed. This is **within one fixture BrowserTask/run**, not a cross-TaskRun proof. Release H-079 remains HOLD. Next RED: genuinely admitted distinct BrowserTask/TaskRun replay and uncertainty/restart without mutation replay, under qualified baseline.

## BAV-04 checkpoint 2026-10-12 (test-only GREEN)
- RED: no BAV04 recovery-fence contract; initial Python collection errored ModuleNotFoundError. New native Electron contract RED showed only BAV03 result; revised baseline-effect binding had independent RED TypeError.
- GREEN Python: 11 tests including a true separate Python process os._exit(37) immediately after a persisted external file effect, durable ExecutionJournal pending boundary, independent fixture readback, authority/lease/host/scope/version mismatch negatives, corrupt journal. Uses existing ArtifactStore + DeterministicRoutineRunner.resume_ref; no second engine/store.
- GREEN Electron: disposable WebContentsView/Bearer native controller fixture; initial Alpha seed, Beta click effect, worker os._exit(37), fresh worker readback + journal reconciliation, no second click, effect counter 2. **Same existing BrowserTask; no new production lease/admission or Electron main crash.**
- BAV04 is PARTIAL/EXPERIMENTAL, not RELEASE. Qualified Stage A baseline H-079 is HOLD (live upstream main 9f63a6fe5cfe39adc7a8f1936fbdcffffbec1d74, origin/main a2b56db1bc; exact-head CI not established). Next RED must exercise authentic new BrowserTask/TaskRun admission after restart, lease revocation and real authority source without synthetic admitted dict. No runtime promotion before gate.
