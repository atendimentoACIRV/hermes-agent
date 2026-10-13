"""P0 concurrent Kanban admission across independent OS processes.

All storage is under tmp_path. No real Hermes cards or sessions are opened.
"""
import os
from pathlib import Path
import subprocess
import sys
import time

from workstation.kanban import WorkstationKanbanBridge


CHILD = r"""
import os
from pathlib import Path
import time
from workstation.contracts import IntentAuthority, MessageEnvelope, MessageOrigin
from workstation.kanban import WorkstationKanbanBridge
root = Path(os.environ["P0_TEST_READY_DIR"])
idx = os.environ["P0_TEST_WORKER"]
(root / ("ready-" + idx)).write_text("ready", encoding="ascii")
deadline = time.monotonic() + 12
while not (root / "go").exists():
    if time.monotonic() > deadline:
        raise RuntimeError("P0 cross-process barrier expired")
    time.sleep(0.02)
body = "First collect reports then verify and save the results"
envelope = MessageEnvelope(
    MessageOrigin.HUMAN, IntentAuthority.CREATE_WORK,
    "shared-session", body, correlation_id="different-turn-" + idx,
)
task = WorkstationKanbanBridge().promote_request_if_multistep(
    body, session_id="shared-session", envelope=envelope, defer_execution=True,
)
print(task, flush=True)
"""


def test_two_os_processes_admit_single_task(tmp_path, monkeypatch):
    home = tmp_path / "hermes-home"
    monkeypatch.setenv("HERMES_HOME", str(home))
    # Initialize schema before racing admissions; target transaction not setup.
    with WorkstationKanbanBridge().get_connection() as conn:
        assert conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0

    env = os.environ.copy()
    env["HERMES_HOME"] = str(home)
    env["P0_TEST_READY_DIR"] = str(tmp_path)
    processes = []
    for idx in range(2):
        child_env = {**env, "P0_TEST_WORKER": str(idx)}
        processes.append(subprocess.Popen(
            [sys.executable, "-c", CHILD],
            cwd=str(Path(__file__).resolve().parents[2]),
            env=child_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ))
    try:
        deadline = time.monotonic() + 14
        while not all((tmp_path / f"ready-{idx}").exists() for idx in range(2)):
            assert time.monotonic() < deadline, "child processes did not reach barrier"
            time.sleep(0.025)
        (tmp_path / "go").write_text("go", encoding="ascii")
        results = [process.communicate(timeout=25) for process in processes]
        for proc, (_, errors) in zip(processes, results):
            assert proc.returncode == 0, errors
        task_ids = [stdout.strip() for stdout, _ in results]
        assert len(set(task_ids)) == 1, task_ids
        with WorkstationKanbanBridge().get_connection() as conn:
            assert conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 1
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.communicate()


CLAIM_CHILD = r"""
import os
import time
from pathlib import Path
from hermes_cli import kanban_db
from workstation.kanban import WorkstationKanbanBridge
root = Path(os.environ["P0_TEST_READY_DIR"])
worker = os.environ["P0_TEST_WORKER"]
(root / ("claim-ready-" + worker)).write_text("ready", encoding="ascii")
deadline = time.monotonic() + 12
while not (root / "claim-go").exists():
    if time.monotonic() > deadline:
        raise RuntimeError("claim concurrency barrier timeout")
    time.sleep(0.02)
with WorkstationKanbanBridge().get_connection() as conn:
    result = kanban_db.claim_task(
        conn, os.environ["P0_TEST_TASK_ID"], claimer="worker-" + worker
    )
    print(str(result.current_run_id) if result else "NOT_CLAIMED", flush=True)
"""


def test_two_os_processes_cannot_claim_one_task_twice(tmp_path, monkeypatch):
    """Two independent workers must never receive simultaneous TaskRun leases."""
    from hermes_cli import kanban_db

    home = tmp_path / "hermes-home"
    monkeypatch.setenv("HERMES_HOME", str(home))
    with WorkstationKanbanBridge().get_connection() as conn:
        task_id = kanban_db.create_task(
            conn, title="Race", body="Execute verified mutation", session_id="chat-1",
            created_by="workstation", triage=True,
        )
        assert kanban_db.specify_triage_task(conn, task_id)
        assert kanban_db.get_task(conn, task_id).status == "ready"
    env = {
        **os.environ,
        "HERMES_HOME": str(home),
        "P0_TEST_READY_DIR": str(tmp_path),
        "P0_TEST_TASK_ID": task_id,
    }
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", CLAIM_CHILD],
            cwd=str(Path(__file__).resolve().parents[2]),
            env={**env, "P0_TEST_WORKER": str(idx)},
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        ) for idx in range(2)
    ]
    try:
        deadline = time.monotonic() + 14
        while not all((tmp_path / f"claim-ready-{idx}").exists() for idx in range(2)):
            assert time.monotonic() < deadline, "workers failed to reach race barrier"
            time.sleep(0.025)
        (tmp_path / "claim-go").write_text("go", encoding="ascii")
        results = [worker.communicate(timeout=25) for worker in processes]
        for worker, (_, errors) in zip(processes, results):
            assert worker.returncode == 0, errors
        claims = [stdout.strip() for stdout, _ in results]
        assert claims.count("NOT_CLAIMED") == 1, claims
        run_id = next(value for value in claims if value != "NOT_CLAIMED")
        with WorkstationKanbanBridge().get_connection() as conn:
            task = kanban_db.get_task(conn, task_id)
            assert task.status == "running"
            assert str(task.current_run_id) == run_id
            assert conn.execute(
                "SELECT COUNT(*) FROM task_runs WHERE task_id=?", (task_id,)
            ).fetchone()[0] == 1
    finally:
        for worker in processes:
            if worker.poll() is None:
                worker.kill()
                worker.communicate()
