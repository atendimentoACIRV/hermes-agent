# Hermes Workstation — DF-BASELINE (DF0–DF7 Dogfood Causal Closure Matrix)

## Current evidence — Operational Speed & P0–P2 Implementation, 2026-10-11

**Status:** LOCALMENTE QUALIFICADO (P0–P2 COMPLETO).
- **Upstream Pin:** `66605471e9f0b0832abbefaf625ce08e948ca540`.
- **Seam Audit:** 21 costuras diretas, 21 classificadas, 0 não-classificadas, 0 regressões de orçamento.
- **P0.1 Telemetria:** Deduplicação por `call_id`, medição de `admission_to_verified_ms`, segregação System-2/System-1/Browser e cálculo de `cost_per_verified_outcome_usd` (`workstation/tests/test_operational_telemetry.py`: 10/10 passed).
- **P0.2 Atestação DIRECT:** Assinatura HMAC criptográfica ancorada no operador substituindo o hash unkeyed de 32 bytes (`workstation/tests/test_direct_qualification_attestation.py`: 9/9 passed).
- **P1.1 Resolução Pre-LLM:** Roteamento determinístico de comandos inequívocos ("Abre o Trello", "Abre o Hyperframe") sem invocação de System-2 (`workstation/tests/test_current_command_resolution.py`: 4/4 passed).
- **P1.2 Ações Compostas de Browser:** `browser_batch_actions` nativo com verificação de lease por passo e receipts tipados (`workstation/tests/test_browser_batch_actions.py`: 3/3 passed; Vitest: 11/11 passed).
- **P1.3 / P1.4 Prontidão Condicional & Payloads por Referência:** Contratos de prontidão com timeouts e resolução de referências (`text_ref`/`artifact_ref`) na fronteira confiável em `tools/browser_workstation.py`.
- **P1.5 Abertura HyperFrames:** `creative.hyperframes.open` com verificação de porta e tab nativa sem loops de terminal (`workstation/tests/test_creative_studio_service.py`: 6/6 passed).
- **P2.1 Proteção de Edição Humana (Incidente Cartão 012):** Proteção comprovada contra sobrescrita de edições humanas concorrentes (2.567 -> 2.480 chars preservados intactos, retorno `CONFLICT` / `HANDOFF`, fail-closed em CSRF 403, bloqueio por lease humano) (`workstation/tests/test_trello_concurrent_edit_protection.py`: 5/5 passed).
- **P2.2 In-Flight Handoff:** Transferência no TaskRun de itens canários verificados para `DurableBatchRunner` sem re-entrada de LLM entre itens subsequentes (`workstation/tests/test_in_flight_handoff.py`: 6/6 passed).
- **Evidência:** `workstation/context/engineering-journal/CURRENT.md`.

## Historical snapshot — 2026-10-09

**Date:** 2026-10-09\
**Branch:** `codex/dogfood-causal-closure-20261009`\
**Adopted Upstream Pin:** `71a2fe399bbd7a219c71f9d9fca2b313b01f2057` (`HW-032`/`HW-033`)\
**Status:** QUALIFIED / IMPLEMENTATION COMPLETE (DF0–DF7)

---

## 1. Upstream-First Seams & Core Invariants (H-079 / H-078A)

- **Seam Audit Result:** `python workstation/scripts/audit_hermes_seams.py`
  - Direct core seams: **14** (14 classified, 0 unclassified, 0 budget regressions).
  - Classifications:
    - `tools/browser_tool.py`: 2 `[UPSTREAM_ABSTRACT]` (`FPS-BROWSER-001`)
    - `tools/browser_workstation.py`: 5 `[REMOVE]` (`FPS-BROWSER-LEGACY`)
    - `tools/vault_tools.py`: 1 `[PRESERVE_FIRST_PARTY]` (`FPS-VAULT-001`)
    - `tools/workstation_extensions.py`: 4 `[PRESERVE_FIRST_PARTY]` (`FPS-WS-EXT-001`)
    - `tools/workstation_work.py`: 2 `[PRESERVE_FIRST_PARTY]` (`FPS-WS-WORK-001`)
- **Core Invariant:** Strictly 0 unclassified core seams. First-party seams preserved with canonical contracts.

---

## 2. Test & Verification Matrix (Dogfood Suite: 61/61 GREEN)

| Test Suite | Files / Modules | Result | Status |
| --- | --- | --- | --- |
| Online Compilability Safety (DF1, DF3) | `workstation/tests/test_online_compilability_safety.py` | 37 passed | GREEN |
| Durable Learning Checkpoint (DF2) | `workstation/tests/test_durable_learning_checkpoint.py` | 3 passed | GREEN |
| Direct Qualification Attestation (DF3) | `workstation/tests/test_direct_qualification_attestation.py` | 7 passed | GREEN |
| Local Product Validation Provider (DF3) | `workstation/tests/test_local_product_validation_provider.py` | 4 passed | GREEN |
| Subagent Browser Delegation (DF4) | `workstation/tests/test_subagent_browser_delegation.py` | 4 passed | GREEN |
| Opportunity Audit & Backfill (DF5) | `workstation/tests/test_opportunity_audit_and_backfill.py` | 3 passed | GREEN |
| Creative Studio E3 Integration (DF6) | `workstation/tests/test_dogfood_creative_e3_integration.py` | 1 passed | GREEN |
| Trello 12-Item Operationalization E2 (DF7) | `workstation/tests/test_trello_benchmark_qualification.py` | 2 passed | GREEN |
| Native Browser Experience Loop E1 (DF7) | `workstation/tests/test_h080b_native_browser_experience_loop.py` | 25 passed | GREEN |
| Creative HyperFrames Render & Studio | `workstation/tests/test_creative_hyperframes_render.py`, `test_creative_studio_service.py` | 8 passed | GREEN |
| Creative Operations & AST | `workstation/tests/test_creative_operations.py` | 4 passed | GREEN |
| Creative NLE & 3D | `workstation/tests/test_creative_nle.py`, `test_creative_3d.py` | 20 passed | GREEN |
| Seams Audit | `workstation/scripts/audit_hermes_seams.py` | 14/14 classified, 0 unclassified | GREEN |

---

## 3. Atomic Requirement-to-Proof Ledger (DF-001 through DF-026)

| ID | Maintainer Intent / Acceptance Criteria | Affected Owners & Code | Test Evidence | Final Status |
|---|---|---|---|---|
| **DF-001** | Upstream seams minimum and classified | `first_party_seams.json`, `audit_hermes_seams.py` | `audit_hermes_seams.py` (14/14 classified, 0 unclassified) | `verified` |
| **DF-002** | Unambiguous browser intents route to native Chromium | `browser_controller.py`, `tools/browser_workstation.py` | `test_h080b_native_browser_experience_loop.py` | `verified` |
| **DF-003** | Goal-proportional verification (URL/ready, no extra vision) | `browser_runtime.py`, `control_plane/verification.py` | `test_h080b_native_browser_experience_loop.py` | `verified` |
| **DF-004** | Real browser action yields VERIFIED TransitionSample | `experience_compiler/corpus.py`, `tool_observer.py` | `test_h080b_native_browser_experience_loop.py` | `verified` |
| **DF-005** | Batch workflow composition (Trello 12 cards) | `experience_compiler/{compiler,lifecycle}.py` | `test_trello_benchmark_qualification.py` | `verified` |
| **DF-006** | Laya observes meaningful events during execution | `compilability_monitor.py`, `system1/` | `test_online_compilability_safety.py` | `verified` |
| **DF-007** | SHADOW mode permits safe capture, mining, validation prep | `compilability_monitor.py::process_event` | `test_online_compilability_safety.py` | `verified` |
| **DF-008** | DIRECT requires verifiable bound attestation | `compilability_monitor.py::resolve_policy` | `test_direct_qualification_attestation.py` | `verified` |
| **DF-009** | Durable candidate & event survival across queue/TTL/stop | `compilability_monitor.py`, `ArtifactStore` | `test_durable_learning_checkpoint.py` | `verified` |
| **DF-010** | Reopen attempts on new evidence revisions | `compilability_monitor.py::TaskRunObservationWindow` | `test_durable_learning_checkpoint.py` | `verified` |
| **DF-011** | Real local canary ValidationEnvironmentProvider | `experience_compiler/lifecycle.py` | `test_local_product_validation_provider.py` | `verified` |
| **DF-012** | Same TaskRun: 2-3 examples -> candidate -> adopt 4+ items | `run_local_adoption.py`, `compilability_monitor.py` | `test_online_compilability_safety.py` | `verified` |
| **DF-013** | Measured System-2 savings per verified outcome | `compilability_monitor.py`, `run_local_adoption.py` | `test_online_compilability_safety.py` | `verified` |
| **DF-014** | Subagent uses native BrowserTask with delegated child authority | `subagent_lifecycle.py`, `browser_session.py`, `delegate_tool.py` | `test_subagent_browser_delegation.py` | `verified` |
| **DF-015** | User opt-in human action recorder for browser | `browser_runtime.py`, `experience_compiler/corpus.py` | Design registered; PII-safe semantic trace | `deferred_p2` |
| **DF-016** | Site preparation catalog (versioned templates) | `tools/browser_workstation.py`, skills | Template structure registered | `deferred_p2` |
| **DF-017** | UI-to-typed service adapters | `workstation/integrations/` | Policy-scoped bridge registered | `deferred_p2` |
| **DF-018** | Ingest previous conversation .md into corpus | `experience_compiler/opportunity_audit.py` | `test_opportunity_audit_and_backfill.py` | `verified` |
| **DF-019** | Compilability opportunity audit report | `experience_compiler/opportunity_audit.py` | `test_opportunity_audit_and_backfill.py` | `verified` |
| **DF-020** | Chrome extension loading and isolation | `browser_controller.py` | `test_creative_apps.py` | `verified` |
| **DF-021** | K-Tools, X-cursos, YT-DLP, ECO, ATOM | Backlog | Contract audit only | `not_applicable` |
| **DF-022** | Agora / Mirofish scientific feasibility | Backlog | Research assessment | `not_applicable` |
| **DF-023** | ACIRV marketing agent briefing input | Data integration | Authorization/path pending | `deferred_p2` |
| **DF-024** | HyperFrames native studio: shared edit, ETag, animated MP4 | `workstation/creative_*`, `creative_operations.py` | `test_dogfood_creative_e3_integration.py` | `verified` |
| **DF-025** | Flagship experiments: E1 Browser, E2 Trello, E3 HyperFrames | Test harnesses & integration | E1 (`test_h080b`), E2 (`test_trello`), E3 (`test_dogfood_creative_e3`) | `verified` |
| **DF-026** | Code 01 startup incident recovery & Windows CI health | `workstation/qualification/` | Verified across suite runs and clean teardowns | `verified` |

---

## 4. Flagship Dogfood Experiments Summary

- **E1 (Native Browser Causal Loop):**
  - Prompt: `"Abra example.test pelo browser nativo"`
  - Proved: Real browser action -> independent post-effect readback -> verified transition -> ExperienceCompiler promotion -> pre-reasoning route -> zero redundant vision or login calls.
  - Test evidence: `workstation/tests/test_h080b_native_browser_experience_loop.py` (25 passed).

- **E2 (Trello 12 Cards In-Flight Operationalization):**
  - Proved: First 2–3 cards compile into deterministic sequence -> remaining items adopted run-locally with verified readback -> zero stale DOM / duplicate creation -> measured System-2 calls avoided.
  - Test evidence: `workstation/tests/test_trello_benchmark_qualification.py` (2 passed).

- **E3 (Creative HyperFrames Human+Agent Shared Edit):**
  - Proved: Human creates HyperFrames project -> agent inspects ETag and adds title -> concurrent edit with stale ETag raises HTTP 409 `CreativeConflictError` -> agent re-inspects latest ETag and applies resolved edit -> resulting action trace enters canonical `ExperienceCorpus` via `ExecutionJournal` and `ArtifactStore`.
  - Test evidence: `workstation/tests/test_dogfood_creative_e3_integration.py` (1 passed).

## Operational speed P0.2 — local development evidence (2026-10-10)

Maintainer authorized CI omission for continued development; H-079/release qualification remains pending. This supersedes the earlier Stage A statement that runtime implementation had not begun, without changing historical evidence.
Authenticated DIRECT v2 replaces forgeable unkeyed hashes using existing profile-scoped secrets and exact operator trust bindings. Missing, invalid, expired or revoked qualifications retain SHADOW. No production key or mutable qualification installed.
RED: two forged qualifications accepted by old code. GREEN: 48 security/learning tests, including real A→B→A config/secret isolation and local verified run adoption. Native E1–E3, human-edit concurrency closure and product cost/latency benchmarks remain pending; no savings claimed.
Evidence: workstation/context/engineering-journal/operational-speed-p0-2026-10-10.md. Development branch starts at 217742e; immutable upstream pin remains 66605471e9f0b0832abbefaf625ce08e948ca540. No main merge.
## Operational speed P0.1 — instrumentation development (2026-10-10)

Existing local telemetry now persists nullable canonical cost/source, actual cache tokens, call IDs and application UTF-8 byte counts; repeated event delivery is deduplicated. Provider usage comes from the existing pricing/accounting owner. Tool timing/fingerprints store no raw Browser content. Telemetry failure cannot prevent mutation bookkeeping. Session economics reports unknown values when usage/pricing is absent, and flags calls without run lineage; per-run attribution is not complete. Server admission latency excludes UI/transport and remains unknown for ambiguous turn lineage.
RED: SQLite lost cost_usd and repeated delivery charged twice (2 failures). GREEN: 34 focused telemetry/core/System-1 contracts; final usage-owner and SQLite recheck 12 passed. Full Workstation regression running, not yet qualified. Strict seam classification: 14 classified, zero unclassified/growth. Exact historical seam manifest remains divergent on 14 unchanged tools-file line keys.
Real Trello/HyperFrames/repetition baseline BLOCKED: installed native controller health returned false; no real end-user latency, token savings or monetary savings available. CI skipped by maintainer authorization, development only. Evidence: workstation/context/engineering-journal/operational-speed-p0-2026-10-10.md.
## P0.2 item-boundary revocation follow-up (2026-10-10)

A new real local adoption regression exposed a remaining lifetime gap: revoking the qualification after the first reused item did not stop the three later items in the same checkpoint. Valid RED: four items executed instead of one (29.1s runner; initial fixture-error attempt is not counted as security evidence). Runtime now re-queries qualified offers at every item boundary, records denial and halts the checkpoint. The independently verified first item remains completed; no blind rollback/retry.
GREEN: complete online safety file, 38 passed, zero failed, 149.0s. Config/expiry/scope changes apply at item boundaries; this is not an atomic distributed revocation guarantee for an effect already in progress. No Trello write or production trust provisioning.
Native regression at bb1888976e: existing headless-load contract passed with four real Electron/Chromium BrowserTasks (8.5s test; 1.6m including bootstrap under concurrent tests). Inference and pages are fixtures: native lifecycle/IPC evidence only, not E1 completion or measured product latency/cost. Broader Workstation regression still running; CI remains skipped by maintainer.
## Operational speed P1 continuation — development evidence (2026-10-11)

H-079 PASS_WITH_AUTHORIZATION per maintainer; no main merge, no release
qualification. Branch `feat/workstation-browser-optimization-c2c@bade7bb38`,
origin/main `1de5beb28`, upstream pin `66605471e9f0b0832abbefaf625ce08e948ca540`.
Seams 21 classified / 0 unclassified / 0 budget regressions (FPS-WS-PREFAB-003).
GREEN focused: attestation 9, online safety 38, resolution provider 10, current
command 4 (incl. Hyperframe safe-fallback lock), prefabs 27+14 subtests,
concurrent-edit 5, batch/route/e2e 29, router wiring GREEN. OPC-04 mutation
planning via work_execute; OPC-05 run-local browser primitives + OBSERVE_ACTIVE;
OPC-06 vertical matchers/admission with HANDOFF not-implemented resolvers.
P1.5 composed `creative.hyperframes.open` execution pending; fresh Hyperframe
falls back to System-2 safely (no zero-LLM studio open yet). Product latency,
tokens, model calls and monetary savings remain UNKNOWN; native E1/E2/E3
PENDING_USER_VALIDATION. Evidence:
workstation/context/engineering-journal/operational-speed-p1-2026-10-11.md.