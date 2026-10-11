# OPC-001 Implementation Summary

**Branch:** `feat/workstation-browser-optimization-c2c` (commit 55399a455d)
**Date:** 2026-10-11
**Status:** Foundation complete (OPC-00, OPC-01, OPC-02), OPC-03 partially implemented

## What Was Implemented

### OPC-00: Pre-conditions and Git Strategy
- Verified current HEAD: `1de5beb2890772261fff2a26608b03c416efb949`
- Upstream main: `1f2b9e0864` (94 commits ahead)
- Merge base: `66605471e9f0b0832abbefaf625ce08e948ca540`
- Downstream ahead: 933 commits, behind: 94 commits
- **Known Blocker:** H-079 baseline qualification debt - exact-head Workstation CI is red (runtime-independence test failure, browser AppView anchor gate failure)

### OPC-01: Corpus Inventory
**File:** `workstation/qualification/prefabs/inventory_corpus.py`
**Output:** `workstation/qualification/prefabs/corpus-inventory.json`

- **49 unique sessions** (SHA-256 deduplicated)
- **10 unique HTML snapshots** (SHA-256 deduplicated)
- **59 total entries** in sanitized inventory
- **Family breakdown:**
  - unknown: 23
  - instagram: 16
  - trello: 13
  - whatsapp: 4
  - chatgpt: 3
- **Operation types:** generic_browser (28), instagram_navigation (10), html_snapshot (10), chatgpt_interaction (3), whatsapp_conversation (3), trello_navigation (2), trello_console_extraction (2), instagram_scroll_collection (1)
- **Result categories:** OBSERVED (38), UNCERTAIN (21)
- No raw session/HTML content committed - only sanitized metadata

### OPC-02: Prefab Library Integration

#### New Package: `workstation/prefabs/`
| File | Purpose |
|------|---------|
| `catalog.py` | Fixed navigation destinations + closed-vocabulary intent matchers (`match_navigation`, `match_trello_read`) |
| `engine.py` | Provider-free navigator with independent browser snapshot verification (`navigate`) |
| `integration.py` | Turn admission helpers (`prepare_user_navigation`, `prepare_user_trello_read`) + Fast Path resolver (`maybe_resolve_navigation`) |
| `trello.py` | Bounded read-only Trello REST adapter (`TrelloClient`) with hash-based description diffing |
| `offline.py` | HTML/session fingerprinting without raw content persistence |
| `seeding.py` | Register discovered candidates in `OperationalCapabilityRegistry` as `DISCOVERED` |

#### New Tools
| Tool | Toolset | Purpose |
|------|---------|---------|
| `prefab_catalog` | `browser` | Agent capability discovery: `catalog`, `match_navigation`, `match_trello_read`, `get_destination` |
| `prefab_execute` | `desktop_ui` | Workstation read-only operations: `catalog`, `board_lists`, `board_cards`, `card`, `prepare_description` |

#### Fast Path Integration
- **`turn_admission.py`**: Extracts exact-match navigation/Trello read intents from authenticated human turns (`CREATE_WORK`/`UPDATE_WORK` authority only)
- **`operational_resolution.py`**: Calls `maybe_resolve_navigation()` before durable task lookup for zero-LLM known destinations

### OPC-03: Trello READ Vertical (Partial)
- ✅ Navigation intents: `open_trello`, `open_editorial`, `open_scrum`
- ✅ Read intents: `board_lists`, `board_cards`, `find_card`, `card`
- ✅ Description diffing: `prepare_description` (hash-only, no write)
- ✅ Official Trello REST API with credential validation
- ✅ Cache-friendly design with stable IDs
- ⏳ Live validation with real credentials pending
- ⏳ User-facing test: "Abra o Calendário Editorial" (zero System-2 on exact match)

### OPC-04: Trello Mutation (Gated)
- ✅ `prepare_description` returns hash comparison + confirmation digest
- ✅ `apply_description` gated behind `HERMES_PREFABS_ALLOW_TRELLO_WRITES=1`
- ✅ Precondition: stale description blocks write
- ✅ Single PUT + independent readback, no auto-retry on uncertain
- ⏳ Full Policy/TaskRun/effect_budget integration pending OPC-05

## Test Results
All 70 new/existing tests pass:
- 24 prefab tests (intent matching, browser verification, Trello client, offline fingerprinting, integration)
- 39 registry tests
- 7 model_tools handle_function_call tests

## Known Blockers (H-079)
Per `workstation/context/UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md`:
1. **Runtime-independence gate failure** - `run_agent` already in `sys.modules` during test
2. **Browser AppView/core-patch anchor gate failure** - "expected one anchor, found 0"
3. **Duplicate batch admission** - `admit_tool_batch()` called twice
4. **Adapter bootstrap fail-open** - silent exception catching in `workstation/__init__.py`
5. **Stale documentation/registry** - pre-H-078C baselines

**Decision:** As per OPC-001 prompt: "Se PR1 estiver bloqueado por H-079/CI, produza docs, auditoria de corpus sanitizada e testes RED, reportando razão específica, sem mesclar alterações de runtime."

## Files Added/Modified
### Added (12 files)
- `tools/hermes_prefab_catalog.py`
- `tools/workstation_prefabs.py`
- `workstation/prefabs/__init__.py`
- `workstation/prefabs/catalog.py`
- `workstation/prefabs/engine.py`
- `workstation/prefabs/integration.py`
- `workstation/prefabs/trello.py`
- `workstation/prefabs/offline.py`
- `workstation/prefabs/seeding.py`
- `workstation/qualification/prefabs/inventory_corpus.py`
- `workstation/qualification/prefabs/corpus-inventory.json`
- `workstation/tests/prefabs/test_prefabs.py`

### Modified (2 files)
- `workstation/integrations/hermes/turn_admission.py` (+13 lines: prefab intent extraction)
- `workstation/integrations/hermes/operational_resolution.py` (+7 lines: Fast Path resolver call)

## Next Steps (When Gates Clear)
1. **OPC-03 Completion:** Live validation of Trello READ with real credentials, user-facing test
2. **OPC-04:** Full mutation path with Policy/TaskRun/effect_budget integration
3. **OPC-05:** Browser run-local adoption extension, Laya OBSERVE_ACTIVE mode
4. **OPC-06:** Instagram/WhatsApp/ChatGPT verticals
5. **OPC-07:** Full qualification suite, benchmarking, documentation updates

## How to Test
```bash
# Run prefab tests
python -m pytest workstation/tests/prefabs/ -v

# Test prefab_catalog tool (browser toolset)
python -c "
from tools.registry import discover_builtin_tools, registry
discover_builtin_tools()
result = registry.get_entry('prefab_catalog').handler({'action': 'catalog'})
print(result)
"

# Test prefab_execute tool (desktop_ui toolset)
python -c "
from tools.registry import discover_builtin_tools, registry
discover_builtin_tools()
result = registry.get_entry('prefab_execute').handler({'action': 'catalog'})
print(result)
"

# Regenerate corpus inventory
python workstation/qualification/prefabs/inventory_corpus.py
```