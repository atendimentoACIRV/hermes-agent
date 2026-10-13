# Targeted reference-to-Hermes matrix
| Reference | Existing Hermes solution | Decision |
|---|---|---|
| XCursos browser-session.mjs connectOverCDP | WebContentsView, BrowserTask | Test adapter feasibility; BAV01 PASS, product authority not integrated |
| XCursos navigation-planner.mjs | deterministic routines + known URL | Adapt route planning later, no second navigator |
| XCursos lesson-scheduler.mjs | TaskRun/DurableTaskStore | Reuse owners, no second scheduler |
| XCursos adaptive-locator.mjs | @e refs + semantic_anchor | Adapt fallback testid; BAV05 PASS in fixture |
| BrowserClaw snapshot refs | Workstation native snapshot | Keep existing, avoid parallel ref registry |
| Stagehand observe/act/extract | Native inventory/controller | Use conceptual fallback only |
| BrowserOS session replay | Native WebContentsView/BrowserTask | Evaluate license; do not import unreviewed code |
| Browser Harness controller persistence | Native bearer-auth loopback | Use existing |
| Hermes workstation/routines.py | DeterministicRoutineRunner | Next product integration |
| Hermes workstation/memory.py | WebProcedure/ProceduralMemory | Next persistent procedure catalog |
| Hermes workstation-browser-batch.ts | executeAuthorizedBatch | Reuse owner, but ACK not independent proof |
| Parallel feat/playwright-c2c-kits-20261012 | Native crash/lease tests | Preserve; release Stage A HOLD |

| Hermes ExecutionJournal | Durable append with integrity chain and acceptance-boundary fsync | BAV04 test-only mutation-pending record before effect; production approval pending H-079 |
| Hermes ArtifactStore + DeterministicRoutineRunner.resume_ref | Canonical artifact checkpoint + skip previously verified steps | BAV04 green in disposable fixture, no new persistence engine |
| Hermes native BrowserTask bearer controller | Existing singleton owner, 400 on unauthorized run mismatch | BAV04 used same genuinely admitted fixture BrowserTask; different-run qualification pending |
