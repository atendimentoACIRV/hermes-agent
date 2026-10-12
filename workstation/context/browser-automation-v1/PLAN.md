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
