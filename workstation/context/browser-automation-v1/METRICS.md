# Metrics — only test evidence
| Test | Iterations | Owner/controller calls | Independently confirmed effects | Model calls within harness | Scope |
|---|---:|---:|---:|---:|---|
| BAV01 external Playwright CDP disposable tab | 1 | not instrumented | 1 | 0 | FEASIBILITY ONLY |
| BAV03 native singleton bearer controller | 2 | 12 | 2 | 0 | LOCAL TEST ONLY |
| BAV05 invalid-ref semantic recovery | 2 | 12 | 2 | 0 | LOCAL TEST ONLY |
No controlled baseline using adaptive LLM and no full token/cost instrumentation. No measured provider savings or p50/p95 claim. Process wall time includes Electron startup/teardown; not an application performance comparison.

| BAV05 persisted canonical replay (Alpha seed; Beta/Gamma fresh Python processes) | 3 | unmeasured (fixture test) | 3 | 0 | LOCAL SAME-TASK TEST ONLY; fresh-process reloads 2 |
Comparison with LLM not performed. Do not claim a production reliability, cost, or latency gain.
