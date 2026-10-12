# Hermes Experience Compiler Activation — execution ledger
Source of truth: user master mission (EC-00..EC-14), the previously completed C2C audit under workstation/context/audits/C2C-HARNESS-EXPERIENCE-2026-10-11, and PR #82 implementation.
No workstream may bypass formal owner/readback/effect authority or declare production qualification without evidence.

| ID | Dependency and acceptance |
|---|---|
| EC-00 | Verify exact upstream pin, downstream HEAD, PR #82, local dirty files, required H-079/H-081/H-082 gates; preserve isolated worktree |
| EC-01 | Correctly route semantically compatible PROMOTED capability in a new TaskRun before System-2, with real Browser readback, no false match |
| EC-02 | Verify candidate-specific real filesystem steps and counterexamples; reject unknown steps, mismatched predicates, missing/revoked evidence, path escapes |
| EC-03 | Production DurableRunAdoptionOwner factory E2E for readback/lease/drift/task binding, no duplicate effects |
| EC-04 | Intermediate owner-verified capture during active TaskRun, candidate/offer/reuse before full TaskRun closure |
| EC-05 | Real Laya -> compile -> validation -> DIRECT-qualified reuse E2E; SHADOW never grants effects |
| EC-06 | Discover admissible promoted capabilities pre-System-2 and rank utility only AFTER authorization checks |
| EC-07 | Instrument causal funnel, fix EvidenceRef serialization, persist honest provider/token metrics |
| EC-08 | Checkpoint rehydration, monotonic uncertainty, evidence-revision backoff, bounded storage |
| EC-09 | Reuse/success ranking, failure explanations and fresh DISCOVERED revisions with verifier downgrade |
| EC-10 | Paired filesystem/native Browser/Trello benchmarks measuring VERIFIED completions, p50/p95, actual calls/tokens/cost |
| EC-11 | Native Electron/React explorer and runtime timeline, authenticated and read-only |
| EC-12 | Typed revisions, lossless roundtrips, immutable versioned drafts, graph and verifier safety |
| EC-13 | HOLD unless concrete use cases, licensed source, typed IR, kernel semantics, owner and E2E justify loops/triggers |
| EC-14 | Exact-head CI, Windows/Electron/dogfood gates, upstream drift and journal/roadmap update; no automatic merge |

Protocol: advance automatically through eligible independent tasks, test RED -> GREEN -> regress, commit isolated patches, update STATE/EVIDENCE/DECISIONS/NEXT_PROMPT at each handoff. Use true git HEAD instead of trusting cached SHA. Preserve checkout C:\Github\hermes-agent modifications.
