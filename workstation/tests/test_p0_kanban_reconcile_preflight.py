"""P0.5 dry-run reconciliation never mutates canonical task data."""
from __future__ import annotations

import hashlib
import json
import sqlite3

import pytest

from workstation.kanban_reconcile_preflight import (
    analyze, create_manifest, open_readonly, read_handoffs, sqlite_snapshot,
)


def _database(path, task_ids, runs=()):
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE tasks(id TEXT PRIMARY KEY, status TEXT)")
        db.execute("CREATE TABLE task_runs(id TEXT PRIMARY KEY, task_id TEXT)")
        db.execute("CREATE TABLE work_plans(id TEXT PRIMARY KEY)")
        db.execute("CREATE TABLE work_items(id TEXT PRIMARY KEY)")
        db.executemany("INSERT INTO tasks VALUES (?, 'blocked')", [(i,) for i in task_ids])
        db.executemany("INSERT INTO task_runs VALUES (?,?)", runs)


def test_manifest_preserves_intentional_deletions_and_orphan_handoffs(tmp_path):
    current, previous = tmp_path / "now.db", tmp_path / "previous.db"
    _database(current, ["new", "shared"], [("run-ok", "new"), ("run-orphan", "old")])
    _database(previous, ["old", "shared", "older"])
    handoffs = tmp_path / "handoffs.json"
    handoffs.write_text(json.dumps({"handoffs": [
        {"handoff_id": "h1", "task_id": "new", "status": "waiting-for-human"},
        {"handoff_id": "h2", "task_id": "old", "status": "waiting-for-human"},
    ]}))
    before = hashlib.sha256(current.read_bytes()).hexdigest()
    result_path = create_manifest(current, previous, handoffs, tmp_path / "output")
    report = json.loads(result_path.read_text(encoding="utf-8"))
    assert hashlib.sha256(current.read_bytes()).hexdigest() == before
    assert report["mode"] == "DRY_RUN_NO_MUTATIONS"
    assert report["counts"]["current_tasks"] == 2
    assert report["counts"]["backup_only_retained_deleted"] == 2
    assert report["counts"]["intersection"] == 1
    assert report["counts"]["orphan_task_runs"] == 1
    assert report["counts"]["orphan_handoffs"] == 1
    assert {p["action"] for p in report["proposals"]} == {
        "PRESERVE", "RETAIN_DELETED", "MARK_FOR_HUMAN_REVIEW",
    }
    assert not any(p["action"] in ("RESTORE", "DELETE", "DONE") for p in report["proposals"])
    assert (tmp_path / "output" / "canonical-snapshot.db").exists()
    with pytest.raises(FileExistsError):
        create_manifest(current, previous, handoffs, tmp_path / "output")


def test_sqlite_snapshot_consistent_and_non_destructive(tmp_path):
    source = tmp_path / "source.db"
    _database(source, ["t1"])
    dest = tmp_path / "snapshot.db"
    sqlite_snapshot(source, dest)
    with open_readonly(dest) as db:
        assert db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 1
    with pytest.raises(FileExistsError):
        sqlite_snapshot(source, dest)
    with open_readonly(source) as db:
        assert db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 1


def test_corrupt_sqlite_and_invalid_handoffs_are_rejected(tmp_path):
    corrupt = tmp_path / "corrupt.db"
    corrupt.write_bytes(b"not a SQLite database")
    with pytest.raises((sqlite3.DatabaseError, ValueError)):
        with open_readonly(corrupt):
            pass
    bad = tmp_path / "handoffs.json"
    bad.write_text('{"handoffs": {"unexpected": "mapping"}}')
    with pytest.raises(ValueError, match="schema"):
        read_handoffs(bad)


def test_injected_bad_handoff_is_not_silently_ignored(tmp_path):
    current, previous = tmp_path / "current.db", tmp_path / "old.db"
    _database(current, ["t1"])
    _database(previous, ["t1"])
    with open_readonly(current) as now, open_readonly(previous) as old:
        with pytest.raises(ValueError, match="Malformed"):
            analyze(now, old, [None])
