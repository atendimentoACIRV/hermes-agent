"""EC-04: native filesystem owner evidence, before the first durable mutation."""
import json
import sqlite3

from workstation.artifacts import ArtifactStore
from workstation.durable_tasks import DurableTaskStore, WorkItemStatus
from workstation.operational_capabilities import CapabilityLifecycle, OperationalCapability
from workstation.operational_kernel import OperationalKernel


def _harness(tmp_path):
    base = tmp_path / "scoped"
    base.mkdir()
    (base / "report.txt").write_text("old", encoding="utf-8")
    artifact_store = ArtifactStore(tmp_path / "artifacts")
    db = sqlite3.connect(str(tmp_path / "durable.sqlite"), check_same_thread=False)
    tasks = DurableTaskStore(conn=db)
    plan = tasks.create_plan(
        "ec04-task", "Two independent files", [{"path": "report.txt"}, {"path": "later.txt"}],
        run_id="ec04-run",
    )
    first, second = tasks.get_work_items(plan.id)
    recorded = []
    original_store = artifact_store.store

    def witness(*args, **kwargs):
        ref = original_store(*args, **kwargs)
        if kwargs.get("schema") == "workstation.operational_prestate_readback.v1":
            recorded.append(ref.ref)
        return ref

    artifact_store.store = witness
    kernel = OperationalKernel(artifacts=artifact_store)
    cap = OperationalCapability(
        id="ec04_probe", name="Filesystem scoped owner", route="filesystem",
        lifecycle=CapabilityLifecycle.PROMOTED,
        effect="state_mutation",
        scope={"base_dir": str(base)},
        provenance={"source": "experience_compiler"},
        preconditions=[json.dumps({"type": "semantic_predicate", "key": "exists", "expected": True})],
        implementation={"steps": [{"primitive": "fs_write",
                                   "args": {"path": "report.txt", "content": "new", "base_dir": str(base)}}]},
    )
    context = {
        "learning_replay": True, "task_id": plan.task_id, "run_id": plan.run_id,
        "operation_id": first.operation_id, "durable_store": tasks,
        "durable_item_id": first.id,
        "primitive_admission": lambda route, mutating: None,
    }
    return base, tasks, plan, first, second, recorded, artifact_store, kernel, cap, context


def test_fs_observer_resolves_scoped_base_dir_before_writing(tmp_path):
    base, tasks, _plan, _first, second, _recorded, _artifacts, kernel, cap, context = _harness(tmp_path)
    result = kernel.execute_capability(cap, {}, context=context)
    assert result["success"] is True
    assert (base / "report.txt").read_text(encoding="utf-8") == "new"
    assert tasks.get_item(second.id).status is WorkItemStatus.PENDING
    tasks.close()


def test_durable_owner_persists_prestate_before_mutation(tmp_path):
    _base, tasks, plan, first, second, recorded, artifacts, kernel, cap, context = _harness(tmp_path)
    kernel.execute_capability(cap, {}, context=context)
    assert recorded, "real owner must persist operation-bound witnessed PRESTATE before dispatch"
    receipt = artifacts.resolve_structured(recorded[0])
    proof = receipt["content"]
    assert receipt["schema"] == "workstation.operational_prestate_readback.v1"
    assert proof["task_id"] == plan.task_id
    assert proof["run_id"] == plan.run_id
    assert proof["operation_id"] == first.operation_id
    assert proof["read_before_write"] is True
    assert proof["state"]["exists"] is True
    assert proof["state"]["basename"] == "report.txt"
    assert tasks.get_item(second.id).status is WorkItemStatus.PENDING
    tasks.close()


def test_missing_owner_admission_denies_durable_learned_mutation(tmp_path):
    import pytest
    from workstation.operational_capabilities import CapabilityDriftError

    base, tasks, _plan, _first, _second, recorded, _artifacts, kernel, cap, context = _harness(tmp_path)
    context.pop("primitive_admission")
    with pytest.raises(CapabilityDriftError, match="admission"):
        kernel.execute_capability(cap, {}, context=context)
    assert (base / "report.txt").read_text(encoding="utf-8") == "old"
    assert not recorded
    tasks.close()


def test_revoked_plan_before_effect_refuses_prestate_and_dispatch(tmp_path):
    import pytest
    from workstation.operational_capabilities import CapabilityDriftError

    base, tasks, plan, _first, _second, recorded, _artifacts, kernel, cap, context = _harness(tmp_path)
    def revoke_at_admission(_route, _mutating):
        conn = tasks.get_connection()
        conn.execute("UPDATE work_plans SET status='cancelled' WHERE id=?", (plan.id,))
        conn.commit()
    context["primitive_admission"] = revoke_at_admission
    with pytest.raises(CapabilityDriftError, match="canonical durable item"):
        kernel.execute_capability(cap, {}, context=context)
    assert (base / "report.txt").read_text(encoding="utf-8") == "old"
    assert not recorded
    tasks.close()


def test_wrong_run_identity_cannot_produce_owner_prestate(tmp_path):
    import pytest
    from workstation.operational_capabilities import CapabilityDriftError

    base, tasks, _plan, _first, _second, recorded, _artifacts, kernel, cap, context = _harness(tmp_path)
    context["run_id"] = "run-other"
    with pytest.raises(CapabilityDriftError, match="canonical durable item"):
        kernel.execute_capability(cap, {}, context=context)
    assert (base / "report.txt").read_text(encoding="utf-8") == "old"
    assert not recorded
    tasks.close()


def test_prestate_observation_precedes_actual_write(tmp_path):
    base, tasks, _plan, _first, _second, recorded, artifacts, kernel, cap, context = _harness(tmp_path)
    real_write = kernel.fs_write

    def inspect_write(*args, **kwargs):
        assert recorded
        proof = artifacts.resolve_structured(recorded[0])["content"]
        assert proof["state"]["exists"] is True
        assert (base / "report.txt").read_text(encoding="utf-8") == "old"
        return real_write(*args, **kwargs)

    kernel.fs_write = inspect_write
    result = kernel.execute_capability(cap, {}, context=context)
    assert result["success"] is True
    tasks.close()


def test_scoped_composite_observer_resolves_step_base_dir(tmp_path):
    base, tasks, _plan, _first, _second, _recorded, _artifacts, kernel, cap, context = _harness(tmp_path)
    cap.route = "composite"
    cap.scope = {"backends": {"filesystem": {"base_dir": str(base)}}}
    context.pop("durable_store")
    context.pop("durable_item_id")
    result = kernel.execute_capability(cap, {}, context=context)
    assert result["success"] is True
    assert (base / "report.txt").read_text(encoding="utf-8") == "new"
    tasks.close()


def test_prestate_never_captured_for_filesystem_scope_escape(tmp_path):
    import pytest
    from workstation.operational_capabilities import CapabilityDriftError

    base, tasks, _plan, _first, _second, recorded, _artifacts, kernel, cap, context = _harness(tmp_path)
    cap.preconditions = []
    cap.implementation["steps"][0]["args"]["path"] = "../escaped.txt"
    with pytest.raises(CapabilityDriftError, match="scope"):
        kernel.execute_capability(cap, {}, context=context)
    assert not (base.parent / "escaped.txt").exists()
    assert not recorded
    tasks.close()


def test_restart_dispatch_checkpoint_blocks_new_prestate_or_duplicate_effect(tmp_path):
    import pytest
    from workstation.operational_capabilities import CapabilityDriftError

    base, tasks, _plan, first, _second, recorded, _artifacts, kernel, cap, context = _harness(tmp_path)
    tasks.update_item_checkpoint(first.id, "ec04_probe@1.0.0_step_0_dispatch")
    with pytest.raises(CapabilityDriftError, match="uncertain mutation"):
        kernel.execute_capability(cap, {}, context=context)
    assert (base / "report.txt").read_text(encoding="utf-8") == "old"
    assert not recorded
    tasks.close()


def test_lease_revoked_after_prestate_before_dispatch_denies_effect(tmp_path):
    import pytest
    from workstation.operational_capabilities import CapabilityDriftError

    base, tasks, plan, _first, second, _recorded, _artifacts, kernel, cap, context = _harness(tmp_path)
    count = 0

    def revoke_between_prestate_and_dispatch(_route, _mutating):
        nonlocal count
        count += 1
        if count == 2:
            connection = tasks.get_connection()
            connection.execute("UPDATE work_plans SET status='cancelled' WHERE id=?", (plan.id,))
            connection.commit()

    context["primitive_admission"] = revoke_between_prestate_and_dispatch
    with pytest.raises(CapabilityDriftError, match="canonical durable item"):
        kernel.execute_capability(cap, {}, context=context)
    assert count >= 2
    assert (base / "report.txt").read_text(encoding="utf-8") == "old"
    assert tasks.get_item(second.id).status is WorkItemStatus.PENDING
    tasks.close()


def test_real_fs_hash_readback_feeds_verified_progressive_corpus_before_run_closure(tmp_path):
    import hashlib

    from workstation.control_plane.verification import VerificationContract, VerificationLifecycle
    from workstation.execution_policy import EvidenceStrength
    from workstation.experience_compiler.corpus import ExperienceCorpus

    base, tasks, plan, _first, second, _recorded, artifacts, kernel, cap, context = _harness(tmp_path)
    digest = hashlib.sha256(b"new").hexdigest()
    cap.verifier_contract = VerificationContract(
        observer="fs_hash", source_kind="filesystem",
        minimum_evidence=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
        allowed_trust=("trusted_runtime",),
        require_read_after_write=True, transition_claim=True,
        lifecycle=VerificationLifecycle.VALIDATED,
    ).to_dict()
    context.update(
        observer_args={"path": "report.txt", "base_dir": str(base)},
        verification_expected=digest,
        expected_task_id=plan.task_id,
        expected_run_id=plan.run_id,
    )
    result = kernel.execute_capability(cap, {}, context=context)
    assert result["verification_result"]["status"] == "VERIFIED"
    samples = ExperienceCorpus(artifacts, discover=True).query(
        task_id=plan.task_id, run_id=plan.run_id, outcome="verified_success"
    )
    assert len(samples) == 1, "verified owned intermediate work must enter corpus before run closes"
    assert samples[0].delta.changed["hash"] == [
        hashlib.sha256(b"old").hexdigest(), digest
    ]
    assert tasks.get_item(second.id).status is WorkItemStatus.PENDING
    tasks.close()
