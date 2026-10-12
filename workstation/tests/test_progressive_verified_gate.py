"""EC-04: only owner-readback-backed transitions enter verified experience."""
from workstation.artifacts import ArtifactStore
from workstation.execution_policy import EvidenceStrength
from workstation.experience_compiler.corpus import ExperienceCorpus
from workstation.experience_compiler.models import Verification
from workstation.experience_compiler.progressive import capture_progressive


def _capture(store, verification):
    return capture_progressive(
        store, task_id="task-verified", run_id="run-1",
        operation_id="op-1", primitive="write_file", route="filesystem",
        outcome="verified_success", state={"exists": True},
        verification=verification,
    )


def test_missing_or_unpersisted_readback_cannot_forge_verified_success(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    assert _capture(store, None) is None
    assert _capture(store, Verification(
        status="VERIFIED", evidence_refs=["artifact://tasks/task-verified/nonexistent.json"],
        evidence_strength=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
        trust_class="trusted_runtime", observer="workstation.readback",
        verifier_fingerprint="verified-fingerprint",
    )) is None
    assert ExperienceCorpus(store, discover=True).query(outcome="verified_success") == []


def test_cross_taskrun_readback_cannot_certify_current_run(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    alien = store.store("task-verified", "alien.json", {
        "task_id": "task-verified", "run_id": "run-OTHER", "operation_id": "op-1",
        "matched": True,
    }, schema="workstation.run_local_readback.v1").ref
    assert _capture(store, Verification(
        status="VERIFIED", evidence_refs=[alien],
        evidence_strength=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
        trust_class="trusted_runtime", observer="workstation.readback",
        verifier_fingerprint="verified-fingerprint",
    )) is None


def test_persisted_owner_readback_allows_intermediate_sample_without_closing_run(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    ref = store.store("task-verified", "readback.json", {
        "task_id": "task-verified", "run_id": "run-1", "operation_id": "op-1",
        "matched": True,
    }, schema="workstation.run_local_readback.v1").ref
    sample_ref = _capture(store, Verification(
        status="VERIFIED", evidence_refs=[ref],
        evidence_strength=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
        trust_class="trusted_runtime", observer="workstation.readback",
        verifier_fingerprint="verified-fingerprint",
    ))
    assert isinstance(sample_ref, str) and sample_ref.startswith("artifact://tasks/task-verified/")
    samples = ExperienceCorpus(store, discover=True).query(
        task_id="task-verified", run_id="run-1", outcome="verified_success",
    )
    assert len(samples) == 1
    assert samples[0].verification.evidence_refs == [ref]


def test_canonical_verification_receipt_requires_original_verifier_evidence(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    forged = store.store("task-verified", "forged_verifier.json", {
        "task_id": "task-verified", "run_id": "run-1", "operation_id": "op-1",
        "result": {"status": "VERIFIED", "evidence_refs": []},
    }, schema="hermes.canonical_verification.v1").ref
    assert _capture(store, Verification(
        status="VERIFIED", evidence_refs=[forged],
        evidence_strength=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
        trust_class="trusted_runtime", observer="workstation.readback",
        verifier_fingerprint="verified-fingerprint",
    )) is None


def test_canonical_kernel_receipt_can_prove_an_unfinished_taskrun_step(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    raw = store.store("task-verified", "owner_verified.json", {
        "task_id": "task-verified", "run_id": "run-1",
        "operation_id": "op-1", "matched": True,
    }, schema="workstation.run_local_readback.v1").ref
    proof = store.store("task-verified", "canonical_verified.json", {
        "task_id": "task-verified", "run_id": "run-1", "operation_id": "op-1",
        "result": {"status": "VERIFIED", "accepted": True, "evidence_refs": [raw]},
    }, schema="hermes.canonical_verification.v1").ref
    sample_ref = _capture(store, Verification(
        status="VERIFIED", evidence_refs=[proof],
        evidence_strength=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
        trust_class="trusted_runtime", observer="workstation.canonical_verifier",
        verifier_fingerprint="fp",
    ))
    assert sample_ref is not None
    assert ExperienceCorpus(store, discover=True).query(outcome="verified_success")


def test_canonical_verifier_cannot_launder_cross_run_or_failed_readback(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    for name, run, matched in (("alien", "other-run", True), ("failed", "run-1", False)):
        subordinate = store.store("task-verified", f"{name}.json", {
            "task_id": "task-verified", "run_id": run,
            "operation_id": "op-1", "matched": matched,
        }, schema="workstation.run_local_readback.v1").ref
        certificate = store.store("task-verified", f"certificate_{name}.json", {
            "task_id": "task-verified", "run_id": "run-1", "operation_id": "op-1",
            "result": {"status": "VERIFIED", "accepted": True,
                       "evidence_refs": [subordinate]},
        }, schema="hermes.canonical_verification.v1").ref
        assert _capture(store, Verification(
            status="VERIFIED", evidence_refs=[certificate],
            evidence_strength=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
            trust_class="trusted_runtime", observer="workstation.canonical_verifier",
            verifier_fingerprint="fp",
        )) is None
