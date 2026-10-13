"""Read-only P0.5 Kanban reconciliation with a consistent SQLite snapshot.

The source databases and handoff ledger are never modified. Backup-only task
IDs are intentionally retained as deleted pending explicit human authorization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


def open_readonly(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise FileNotFoundError(path)
    conn = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    conn.execute("PRAGMA query_only=ON")
    result = conn.execute("PRAGMA quick_check").fetchone()
    if result != ("ok",):
        conn.close()
        raise ValueError("SQLite integrity check failed")
    return conn


def sqlite_snapshot(source: Path, destination: Path) -> None:
    """Capture a WAL-consistent backup using the SQLite backup API."""
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    conn = open_readonly(source)
    try:
        with sqlite3.connect(destination) as target:
            conn.backup(target)
    finally:
        conn.close()
    with open_readonly(destination):
        pass


def _tables(conn: sqlite3.Connection) -> set[str]:
    return {str(x[0]) for x in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}


def _ids(conn: sqlite3.Connection, table: str) -> set[str]:
    if table not in _tables(conn):
        return set()
    return {str(row[0]) for row in conn.execute(f"SELECT id FROM {table}")}


def _rows(conn: sqlite3.Connection, table: str, fields: str) -> list[tuple[Any, ...]]:
    if table not in _tables(conn):
        return []
    return list(conn.execute(f"SELECT {fields} FROM {table}"))


def analyze(current: sqlite3.Connection, previous: sqlite3.Connection,
            handoffs: list[dict[str, Any]]) -> dict[str, Any]:
    current_ids, historical_ids = _ids(current, "tasks"), _ids(previous, "tasks")
    proposals: list[dict[str, str]] = []
    for task_id in sorted(current_ids):
        proposals.append({"type": "task", "id": task_id, "action": "PRESERVE",
                          "reason": "present_in_canonical_database"})
    for task_id in sorted(historical_ids - current_ids):
        proposals.append({"type": "task", "id": task_id, "action": "RETAIN_DELETED",
                          "reason": "backup_only_deletion_intent_not_proven"})
    run_orphans: set[str] = set()
    for run_id, task_id in _rows(current, "task_runs", "id, task_id"):
        if str(task_id) not in current_ids:
            run_orphans.add(str(run_id))
            proposals.append({"type": "task_run", "id": str(run_id),
                              "action": "MARK_FOR_HUMAN_REVIEW",
                              "reason": "run_references_missing_current_task"})
    orphan_handoffs = 0
    for i, item in enumerate(handoffs):
        if not isinstance(item, dict):
            raise ValueError("Malformed handoff ledger item")
        task_id = str(item.get("task_id") or "")
        if not task_id or task_id not in current_ids:
            orphan_handoffs += 1
            proposals.append({
                "type": "handoff", "id": str(item.get("handoff_id") or f"index-{i}"),
                "action": "MARK_FOR_HUMAN_REVIEW",
                "reason": "handoff_has_no_current_task",
            })
    return {
        "schema_version": 1,
        "mode": "DRY_RUN_NO_MUTATIONS",
        "counts": {
            "current_tasks": len(current_ids),
            "backup_tasks": len(historical_ids),
            "intersection": len(current_ids & historical_ids),
            "current_only": len(current_ids - historical_ids),
            "backup_only_retained_deleted": len(historical_ids - current_ids),
            "current_task_runs": len(_ids(current, "task_runs")),
            "backup_task_runs": len(_ids(previous, "task_runs")),
            "current_work_plans": len(_ids(current, "work_plans")),
            "backup_work_plans": len(_ids(previous, "work_plans")),
            "current_work_items": len(_ids(current, "work_items")),
            "backup_work_items": len(_ids(previous, "work_items")),
            "orphan_task_runs": len(run_orphans),
            "handoffs": len(handoffs),
            "orphan_handoffs": orphan_handoffs,
        },
        "proposals": proposals,
        "warnings": [
            "Backup-only tasks may have been intentionally deleted; never restore automatically.",
            "Missing handoff targets require review; do not regrant execution authority.",
            "No task, run, handoff, WorkPlan or WorkItem was changed.",
        ],
    }


def read_handoffs(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("handoffs"), list):
        raise ValueError("Invalid handoff ledger schema")
    return value["handoffs"]


def create_manifest(source: Path, historical: Path, handoff_file: Path,
                    output_dir: Path) -> Path:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError("Reconciliation output directory must be empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = output_dir / "canonical-snapshot.db"
    sqlite_snapshot(source, snapshot)
    with open_readonly(snapshot) as now, open_readonly(historical) as past:
        manifest = analyze(now, past, read_handoffs(handoff_file))
    manifest["source_snapshot_sha256"] = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    manifest["historic_backup_sha256"] = hashlib.sha256(historical.read_bytes()).hexdigest()
    result = output_dir / "reconciliation-dry-run.json"
    result.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only P0.5 reconciliation")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--handoffs", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = create_manifest(args.source, args.previous, args.handoffs, args.output_dir)
    print("DRY RUN completed; no source records modified")
    print(result)


if __name__ == "__main__":
    main()
