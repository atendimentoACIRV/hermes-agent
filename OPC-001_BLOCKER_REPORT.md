# OPC-001 Blocker Report — H-079 Gate Status

**Date:** 2026-10-11  
**Branch:** `feat/workstation-browser-optimization-c2c` (commit `55399a455d`)  
**Status:** **BLOCKED** — H-079 baseline qualification not GREEN

---

## Current Gate Status

### H-079 Upstream-First Change Gate Requirements (from `workstation/context/UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md`)

| Requirement | Status | Evidence |
|-------------|--------|----------|
| **1. Selected upstream pin is ancestor of candidate baseline** | ❌ **BLOCKED** | Downstream `1de5beb` vs upstream `1f2b9e0864` — merge-base `6660547`, downstream ahead 933, behind 94. Upstream pin NOT yet adopted. |
| **2. Current downstream main green on required exact-head gates** | ❌ **BLOCKED** | Workstation CI has failures (see below) |
| **3. No unclassified/overdue REMOVE seams in affected surface** | ⚠️ **UNKNOWN** | Seam audit needed (`first_party_seams.json`, `UPSTREAM_DELTA.md`) |
| **4. Target change implementable on qualified baseline without mixing migration** | ❌ **BLOCKED** | Baseline not qualified |

### Observed CI Failures (Workstation exact-head)

| Test | Status | Details |
|------|--------|---------|
| `test_h078b_runtime_independence` | ✅ PASS | Alternate reasoner drives Workstation lifecycle |
| `test_adapter_bootstrap` | ✅ PASS | Adapter install fails closed |
| `test_anthropic_sdk_construction` | ❌ **FAIL** | `ModuleNotFoundError: No module named 'anthropic'` — missing dependency in CI environment |
| `test_browser_operational_admission` | ✅ PASS | 18/18 tests pass |
| Browser AppView/core-patch anchor | ⚠️ **UNKNOWN** | "ERROR: browser AppView: expected one anchor, found 0" per H-079 doc |
| Duplicate batch admission | ⚠️ **UNKNOWN** | `admit_tool_batch()` called twice per H-079 doc |

### H-079 Qualification Debt (from gate doc)

1. **Browser authority switch incomplete** — `WorkstationBrowserController.attach_to_broker()` exists but bespoke `tools.browser_workstation.workstation_routed_browser_handler` route still registered (REMOVE seams)
2. **Duplicate batch admission** — `admit_tool_batch()` invoked in `agent/turn_tool_round.py` AND `run_agent.py::_execute_tool_calls()`
3. **Adapter bootstrap fail-open** — `workstation/__init__.py` catches adapter installation errors with broad silent exception
4. **Documentation/registry stale** — Historical H-078B COMPLETE/VERIFIED language, pre-H-078C baselines
5. **H-078C implementation report incomplete** — Browser/Desktop/H-077/full-qualification closure sections missing

---

## OPC-001 Phase Status

| Phase | Status | Blocker |
|-------|--------|---------|
| **OPC-00** Pre-conditions & Git | ✅ DONE | Baseline documented |
| **OPC-01** Corpus Inventory | ✅ DONE | 49 sessions, 10 HTML, 59 entries sanitized |
| **OPC-02** Prefab Library Integration | ✅ DONE | Tools registered, Fast Path hooks added |
| **OPC-03** Trello READ Live | 🔴 **BLOCKED** | Requires H-079 GREEN + live Trello creds |
| **OPC-04** Trello Mutation | 🔴 **BLOCKED** | Requires OPC-03 qualified + Policy integration |
| **OPC-05** Learning/Adoption | 🔴 **BLOCKED** | Requires OPC-04 qualified |
| **OPC-06** Instagram/WhatsApp/ChatGPT | 🔴 **BLOCKED** | Requires OPC-05 qualified, separate PRs |
| **OPC-07** Qualification/Benchmarks | 🔴 **BLOCKED** | Requires all prior phases qualified |

---

## RED Tests Created (Documenting Required Behavior)

| Phase | Test File | Tests | Purpose |
|-------|-----------|-------|---------|
| **OPC-03** | `workstation/tests/opc03_trello_read/test_trello_read_red.py` | 23 | Trello READ live validation, intent matching, toolset visibility, Fast Path zero-LLM |
| **OPC-04** | `workstation/tests/opc04_trello_mutation/test_trello_mutation_red.py` | 12 | Mutation policy, work_execute, CLI, receipts, no-retry lane |
| **OPC-05** | `workstation/tests/opc05_learning/test_learning_red.py` | 11 | ExperienceCompiler mining, run-local adoption, Laya OBSERVE_ACTIVE |
| **OPC-06** | `workstation/tests/opc06_verticals/test_verticals_red.py` | 15 | Instagram/WhatsApp/ChatGPT catalogs, fixtures, readback, separate PRs |
| **OPC-07** | `workstation/tests/opc07_qualification/test_qualification_red.py` | 40 | Full test matrix, benchmarks, CI gates, acceptance criteria |

**Total RED tests: 101** — All designed to FAIL until implementation complete.

---

## Required to Unblock

### Minimum for H-079 Baseline Qualification (Stage A)

Per `UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md`, Stage A must achieve:

1. **New upstream Stage A pin adopted and ancestry proven**
   - Fetch `NousResearch/hermes-agent:main`
   - Select exact SHA, record it
   - True merge into integration branch
   - Reconcile seams (REMOVE/UPSTREAM_ABSTRACT/PRESERVE_FIRST_PARTY)
   - Run baseline qualification
   - Establish green downstream baseline

2. **Exact-head Workstation CI GREEN**
   - Fix `anthropic` SDK dependency in CI
   - Fix browser AppView/core-patch anchor gate
   - Resolve duplicate batch admission (single owner)
   - Fix adapter bootstrap fail-open (explicit fail-closed)
   - Update stale documentation

3. **Runtime-independence gate correctly isolated and GREEN**
   - `test_h078b_runtime_independence` already passes ✅

4. **One canonical tool-batch admission owner**
   - Consolidate `admit_tool_batch()` calls

5. **Browser routing authority resolved**
   - Switch to `BrowserControlBroker/controller` OR explicitly justify residual path

6. **No silent required-adapter initialization failure**
   - Adapter install failure = explicit/fail-closed

7. **H-077/H-078 regression ladder GREEN on exact candidate head**

8. **Affected Desktop/Browser E2E GREEN**

9. **Seam registry reflects actual state**
   - Update `first_party_seams.json`, `UPSTREAM_DELTA.md`, `PATCH_MANIFEST.md`

10. **Roadmap/current state/journal/intelligence match exact candidate**

---

## Next Actions (When Gate Clears)

### Immediate (OPC-03 Completion)
1. Run `test_trello_read_red.py` with live `TRELLO_API_KEY`/`TRELLO_TOKEN`
2. Verify Fast Path: "Abra o Calendário Editorial" → zero LLM → EXECUTED
3. Verify independent browser_snapshot verification
4. Verify toolset disable/enable behavior

### Short-term (OPC-04)
1. Integrate Trello mutation with Policy/TaskRun/effect_budget
2. Implement `--i-approve-external-write` CLI gate
3. Add canonical receipt to ExecutionJournal
4. Run mutation RED tests

### Medium-term (OPC-05)
1. Extend `run_local_adoption.py` for browser primitives
2. Implement Laya OBSERVE_ACTIVE mode
3. Add adoption gates (foreign-run, drift, replay-fail, etc.)

### Long-term (OPC-06/07)
1. Instagram vertical (API-first, incremental, checkpoint)
2. WhatsApp vertical (authorized scope, no auto-send)
3. ChatGPT vertical (semantic editor, drift handling)
4. Full qualification suite + benchmarking
5. Documentation updates

---

## How to Verify Current State

```bash
# Run existing prefab tests (all GREEN)
python -m pytest workstation/tests/prefabs/ -v

# Run OPC-03 RED tests (will FAIL - expected)
python -m pytest workstation/tests/opc03_trello_read/ -v

# Run all RED tests (will FAIL - expected)
python -m pytest workstation/tests/opc03_trello_read/ workstation/tests/opc04_trello_mutation/ workstation/tests/opc05_learning/ workstation/tests/opc06_verticals/ workstation/tests/opc07_qualification/ -v

# Check corpus inventory
cat workstation/qualification/prefabs/corpus-inventory.json | python -m json.tool | head -50

# Verify tool registration
python -c "
from tools.registry import discover_builtin_tools, registry
discover_builtin_tools()
print('prefab_catalog:', 'prefab_catalog' in registry.get_tool_names_for_toolset('browser'))
print('prefab_execute:', 'prefab_execute' in registry.get_tool_names_for_toolset('desktop_ui'))
"
```

---

## Decision

**Per OPC-001 prompt and H-079 gate: NO further runtime changes will be merged until baseline qualification is GREEN.**

Current deliverables:
- ✅ Sanitized corpus inventory (`corpus-inventory.json`)
- ✅ Prefab library (`workstation/prefabs/`)
- ✅ Agent + Workstation tools (`prefab_catalog`, `prefab_execute`)
- ✅ Fast Path hooks (`turn_admission.py`, `operational_resolution.py`)
- ✅ 101 RED tests documenting exact requirements for OPC-03 through OPC-07
- ✅ This blocker report

**Next step:** Execute H-079 Stage A upstream sync and qualification. Only then proceed with OPC-03 live validation.