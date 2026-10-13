"""P0: handoff JSON must remain canonical across independently loaded managers.

Every test uses tmp_path; no user review state is read or changed.
"""
from workstation.runtime import HumanHandoffManager


def test_stale_managers_do_not_lose_distinct_handoffs(tmp_path):
    path = tmp_path / "human_handoffs.json"
    first = HumanHandoffManager(path)
    second = HumanHandoffManager(path)
    a = first.request(task_id="task-a", session_id="session-a", reason="review",
                      scope={"operation_key": "a"})
    b = second.request(task_id="task-b", session_id="session-b", reason="review",
                       scope={"operation_key": "b"})
    reloaded = HumanHandoffManager(path)
    assert reloaded.get(a.handoff_id) is not None
    assert reloaded.get(b.handoff_id) is not None


def test_stale_managers_share_identity_and_single_consume(tmp_path):
    path = tmp_path / "human_handoffs.json"
    first = HumanHandoffManager(path)
    second = HumanHandoffManager(path)
    scope = {"operation_key": "same-effect"}
    a = first.request(task_id="task", session_id="session", reason="uncertain",
                      scope=scope)
    b = second.request(task_id="task", session_id="session", reason="uncertain",
                       scope=scope)
    assert a.handoff_id == b.handoff_id
    assert first.resume(a.handoff_id, returned_by="human") is True
    assert second.consume(a.handoff_id) is True
    assert first.consume(a.handoff_id) is False
    final = HumanHandoffManager(path)
    assert len(final._handoffs) == 1
    assert final.get(a.handoff_id).status == "consumed"


# Independent Windows processes race the exact same operation scope.
HANDOFF_WORKER = r"""
import os
from pathlib import Path
import time
from workstation.runtime import HumanHandoffManager
root = Path(os.environ["P0_HANDOFF_ROOT"])
worker = os.environ["P0_HANDOFF_WORKER"]
(root / ("ready-" + worker)).write_text("ready", encoding="ascii")
limit = time.monotonic() + 14
while not (root / "go").exists():
    if time.monotonic() > limit:
        raise RuntimeError("handoff process barrier timeout")
    time.sleep(0.015)
manager = HumanHandoffManager(root / "shared.json")
result = manager.request(
    task_id="task", session_id="session", reason="uncertain_mutation_requires_review",
    scope={"operation_key": "external-operation-1"},
)
print(result.handoff_id, flush=True)
"""


def test_two_windows_processes_admit_one_handoff(tmp_path):
    import os
    from pathlib import Path
    import subprocess
    import sys
    import time

    env = {**os.environ, "P0_HANDOFF_ROOT": str(tmp_path)}
    procs = [
        subprocess.Popen(
            [sys.executable, "-c", HANDOFF_WORKER],
            cwd=str(Path(__file__).resolve().parents[2]),
            env={**env, "P0_HANDOFF_WORKER": str(worker)},
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        ) for worker in range(2)
    ]
    try:
        deadline = time.monotonic() + 15
        while not all((tmp_path / f"ready-{worker}").exists() for worker in range(2)):
            assert time.monotonic() < deadline, "process barrier not reached"
            time.sleep(0.02)
        (tmp_path / "go").write_text("go", encoding="ascii")
        results = [process.communicate(timeout=25) for process in procs]
        for process, (_, errors) in zip(procs, results):
            assert process.returncode == 0, errors
        ids = [output.strip() for output, _ in results]
        assert len(set(ids)) == 1, ids
        final = HumanHandoffManager(tmp_path / "shared.json")
        assert len(final._handoffs) == 1
        assert final.get(ids[0]).status == "waiting-for-human"
    finally:
        for process in procs:
            if process.poll() is None:
                process.kill()
                process.communicate()



def test_corrupt_handoff_ledger_fails_closed_without_overwrite(tmp_path):
    import pytest

    path = tmp_path / "human_handoffs.json"
    keeper = HumanHandoffManager(path)
    keeper.request(task_id="task", session_id="session", reason="review",
                   scope={"operation_key": "before-corruption"})
    path.write_text('{"handoffs": [{"handoff_id": "incomplete"}', encoding="utf-8")
    corrupt_bytes = path.read_bytes()
    with pytest.raises(RuntimeError, match="handoff ledger unreadable"):
        keeper.request(task_id="another", session_id="session", reason="review",
                       scope={"operation_key": "other"})
    assert path.read_bytes() == corrupt_bytes
