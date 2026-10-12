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
