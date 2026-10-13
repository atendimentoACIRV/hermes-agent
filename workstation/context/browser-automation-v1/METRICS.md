# Metrics — only test evidence
| Test | Iterations | Owner/controller calls | Independently confirmed effects | Model calls within harness | Scope |
|---|---:|---:|---:|---:|---|
| BAV01 external Playwright CDP disposable tab | 1 | not instrumented | 1 | 0 | FEASIBILITY ONLY |
| BAV03 native singleton bearer controller | 2 | 12 | 2 | 0 | LOCAL TEST ONLY |
| BAV05 invalid-ref semantic recovery | 2 | 12 | 2 | 0 | LOCAL TEST ONLY |
No controlled baseline using adaptive LLM and no full token/cost instrumentation. No measured provider savings or p50/p95 claim. Process wall time includes Electron startup/teardown; not an application performance comparison.

| BAV05 persisted canonical replay (Alpha seed; Beta/Gamma fresh Python processes) | 3 | unmeasured (fixture test) | 3 | 0 | LOCAL SAME-TASK TEST ONLY; fresh-process reloads 2 |
Comparison with LLM not performed. Do not claim a production reliability, cost, or latency gain.

| BAV04 crash/reconcile disposable Electron native BrowserTask | 2 effects (Alpha seed + Beta before worker exit) | fixture controller only | 2; no duplicate after recovery | 0 | os._exit(37) Python worker, fresh Python recovery, same BrowserTask, **not** Electron main crash nor new authorized TaskRun |
Selected automated regressions: 11 BAV04 Python; combined Python 13; additional memory/journal/artifacts 16; combined Electron 2. These are distinct command runs, not 42 independent functionality metrics. No comparative baseline, token savings, cost claim or p95.
