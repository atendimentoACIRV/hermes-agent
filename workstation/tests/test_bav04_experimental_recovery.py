"""BAV04 test-only recovery contract; not an approved production replay implementation."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from workstation.artifacts import ArtifactStore
from workstation.journal import ExecutionJournal
from workstation.memory import ProceduralMemory, ProcedureStep
from workstation.routines import (
    DeterministicRoutineRunner, RoutineExecutionStatus, RoutinePromotionService,
)
from workstation.tests.bav04_experimental_recovery import RecoveryFence, UnsafeReplay


@pytest.fixture
def scenario(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes-home"))
    memory_path = tmp_path / "procedures.json"
    memory = ProceduralMemory(memory_path)
    proc = memory.record_success("127.0.0.1", "test fixture write",
        [ProcedureStep(action="navigate"), ProcedureStep(action="click"),
         ProcedureStep(action="wait")])
    proc.capability_fingerprint = "bav04-test-only"
    proc.scope = {"allowed_hosts": ["127.0.0.1"], "test_only": True}
    memory.update_procedure(proc)
    promotion = RoutinePromotionService(memory)
    promotion.validate(proc.id, evidence=[{"kind": "fixture-only", "ref": "local-test"}])
    promotion.promote(proc.id)
    journal_path = tmp_path / "journal.jsonl"
    effect_path = tmp_path / "effects.json"
    effect_path.write_text("[]", encoding="utf-8")
    return {
        "memory_path": memory_path, "journal_path": journal_path,
        "effect_path": effect_path, "task_id": "bav-task",
        "session_id": "bav-session", "run_id": "bav-run",
        "procedure_id": proc.id,
    }


def make_fence(s, *, run_id=None):
    return RecoveryFence(
        journal=ExecutionJournal(s["task_id"], s["session_id"],
            file_path=s["journal_path"], environment="test"),
        artifacts=ArtifactStore(), procedure=ProceduralMemory(s["memory_path"]).get_procedure(s["procedure_id"]),
        task_id=s["task_id"], session_id=s["session_id"], run_id=run_id or s["run_id"],
    )


def admitted(s, **changes):
    return {
        "task_id": s["task_id"], "session_id": s["session_id"],
        "run_id": s["run_id"], "lease_valid": True,
        "host": "127.0.0.1", "scope": {"allowed_hosts": ["127.0.0.1"], "test_only": True},
        **changes,
    }


def effects(s):
    return json.loads(s["effect_path"].read_text(encoding="utf-8"))


def crash_after_effect(s):
    """Separate Python worker persists the pending operation then exits with no receipt."""
    script = """
import json, os, pathlib, sys
from workstation.artifacts import ArtifactStore
from workstation.journal import ExecutionJournal
from workstation.memory import ProceduralMemory
from workstation.tests.bav04_experimental_recovery import RecoveryFence
root, procpath, journalpath, effectpath, procid = sys.argv[1:]
p = ProceduralMemory(pathlib.Path(procpath)).get_procedure(procid)
j = ExecutionJournal('bav-task','bav-session',file_path=pathlib.Path(journalpath),environment='test')
f = RecoveryFence(journal=j,artifacts=ArtifactStore(),procedure=p,task_id='bav-task',session_id='bav-session',run_id='bav-run')
f.mark_dispatched(step_index=1, operation_id='op-click-one')
path = pathlib.Path(effectpath)
existing = json.loads(path.read_text(encoding='utf-8'))
path.write_text(json.dumps(existing + ['effect-1']), encoding='utf-8')
os._exit(37)
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2]) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run([sys.executable, "-c", script, "test-only",
        str(s["memory_path"]), str(s["journal_path"]), str(s["effect_path"]), s["procedure_id"]],
        env=env, capture_output=True, text=True, timeout=20)
    assert proc.returncode == 37, proc.stderr


def test_bav04_crash_keeps_pending_and_blocks_blind_replay(scenario):
    crash_after_effect(scenario)
    assert effects(scenario) == ["effect-1"]
    fence = make_fence(scenario)  # Fresh Journal and ProceduralMemory instances.
    assert fence.unresolved_step() == 1
    with pytest.raises(UnsafeReplay, match="uncertain"):
        fence.reconcile_for_resume(admission=admitted(scenario),
            independent_readback=lambda: None)
    assert effects(scenario) == ["effect-1"]


def test_bav04_independent_reconciliation_skips_effect_step(scenario):
    crash_after_effect(scenario)
    fence = make_fence(scenario)
    resume_ref = fence.reconcile_for_resume(
        admission=admitted(scenario),
        independent_readback=lambda: {"verified": effects(scenario) == ["effect-1"],
                                     "fault_domain": "fixture-server", "effect_count": 1},
    )
    ctx = {"elements": [], "continuation_calls": []}
    runner = DeterministicRoutineRunner(ProceduralMemory(scenario["memory_path"]))
    def execute(step, target, context):
        context["continuation_calls"].append(step.action)
        if step.action == "click":
            scenario["effect_path"].write_text(json.dumps(effects(scenario) + ["duplicate"]), encoding="utf-8")
    result = runner.run(scenario["procedure_id"], ctx, execute, resume_ref=resume_ref)
    assert result.status == RoutineExecutionStatus.COMPLETED
    assert ctx["continuation_calls"] == ["wait"]
    assert effects(scenario) == ["effect-1"]


@pytest.mark.parametrize("override", [
    {"run_id": "other-run"}, {"task_id": "other-task"},
    {"session_id": "other-session"}, {"lease_valid": False},
    {"host": "evil.example"}, {"scope": {"allowed_hosts": ["other"], "test_only": True}},
])
def test_bav04_fail_closed_on_authority_scope_drift(scenario, override):
    crash_after_effect(scenario)
    with pytest.raises(UnsafeReplay):
        make_fence(scenario).reconcile_for_resume(
            admission=admitted(scenario, **override),
            independent_readback=lambda: {"verified": True, "fault_domain": "fixture-server", "effect_count": 1})
    assert effects(scenario) == ["effect-1"]


def test_bav04_fails_closed_after_procedure_revision_change(scenario):
    crash_after_effect(scenario)
    memory = ProceduralMemory(scenario["memory_path"])
    proc = memory.get_procedure(scenario["procedure_id"])
    proc.version += 1
    memory.update_procedure(proc)
    with pytest.raises(UnsafeReplay):
        make_fence(scenario).reconcile_for_resume(
            admission=admitted(scenario),
            independent_readback=lambda: {"verified": True, "fault_domain": "fixture-server", "effect_count": 1})


def test_bav04_corrupt_journal_is_not_admissible(scenario):
    crash_after_effect(scenario)
    with scenario["journal_path"].open("a", encoding="utf-8") as handle:
        handle.write('{"invalid":true}\n')
    with pytest.raises(Exception):
        make_fence(scenario).reconcile_for_resume(
            admission=admitted(scenario),
            independent_readback=lambda: {"verified": True, "fault_domain": "fixture-server", "effect_count": 1})

def test_bav04_server_readback_must_match_persisted_baseline(scenario):
    fence = make_fence(scenario)
    fence.mark_dispatched(step_index=1, operation_id="op-increment", baseline_effects=5)
    with pytest.raises(UnsafeReplay):
        make_fence(scenario).reconcile_for_resume(
            admission=admitted(scenario),
            independent_readback=lambda: {
                "verified": True, "fault_domain": "fixture-server", "effect_count": 1,
            },
        )
    ref = make_fence(scenario).reconcile_for_resume(
        admission=admitted(scenario),
        independent_readback=lambda: {
            "verified": True, "fault_domain": "fixture-server", "effect_count": 6,
        },
    )
    assert ArtifactStore().read_json(ref)["context"]["completed_steps"] == 2
