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

def test_verified_intermediate_sample_preserves_owner_known_families_without_promoting(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    receipt = store.store("task-verified", "owned_write.json", {
        "task_id": "task-verified", "run_id": "run-1", "operation_id": "op-1",
        "path": "out/report.txt", "matched": True,
    }, schema="workstation.run_local_readback.v1").ref
    ref = capture_progressive(
        store, task_id="task-verified", run_id="run-1", operation_id="op-1",
        primitive="write_file", route="filesystem", outcome="verified_success",
        operation_family="filesystem.write", target_family="local_file",
        effect_class="state_mutation", scope={"root": "out"},
        state={"exists": True},
        verification=Verification(
            status="VERIFIED", evidence_refs=[receipt],
            evidence_strength=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
            trust_class="trusted_runtime", observer="workstation.readback",
            verifier_fingerprint="verified-fingerprint",
        ),
    )
    assert ref is not None
    sample = ExperienceCorpus(store, discover=True).query(
        task_id="task-verified", run_id="run-1", outcome="verified_success"
    )[0]
    assert sample.operation.operation_family == "filesystem.write"
    assert sample.operation.target_family == "local_file"
    assert sample.operation.effect_class == "state_mutation"
    assert sample.operation.scope == {"root": "out"}
    assert sample.operation.parameters == {}

def test_verified_intermediate_progressive_state_delta_is_reconstructible(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    before_ref = store.store("task-verified", "owner_prestate.json", {
        "task_id": "task-verified", "run_id": "run-1", "operation_id": "op-1",
        "observer": "workstation.operational_prestate",
        "read_before_write": True, "state": {"exists": False},
    }, schema="workstation.operational_prestate_readback.v1").ref
    receipt = store.store("task-verified", "state_transition_readback.json", {
        "task_id": "task-verified", "run_id": "run-1", "operation_id": "op-1",
        "matched": True,
    }, schema="workstation.run_local_readback.v1").ref
    ref = capture_progressive(
        store, task_id="task-verified", run_id="run-1", operation_id="op-1",
        primitive="write_file", route="filesystem", outcome="verified_success",
        state_before={"exists": False}, state_before_ref=before_ref, state={"exists": True},
        verification=Verification(
            status="VERIFIED", evidence_refs=[receipt],
            evidence_strength=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
            trust_class="trusted_runtime", observer="workstation.readback",
            verifier_fingerprint="verified-fingerprint",
        ),
    )
    assert ref is not None
    sample = ExperienceCorpus(store, discover=True).query(outcome="verified_success")[0]
    assert sample.state_before.semantic_predicates["exists"] is False
    assert sample.state_after.semantic_predicates["exists"] is True
    assert sample.delta.changed == {"exists": [False, True]}


def test_verified_poststate_without_owner_prestate_does_not_invent_a_delta(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    proof = store.store("task-verified", "post_only.json", {
        "task_id": "task-verified", "run_id": "run-1",
        "operation_id": "op-1", "matched": True,
    }, schema="workstation.run_local_readback.v1").ref
    sample_ref = _capture(store, Verification(
        status="VERIFIED", evidence_refs=[proof],
        evidence_strength=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
        trust_class="trusted_runtime", observer="workstation.readback",
        verifier_fingerprint="verified-fingerprint",
    ))
    assert sample_ref
    sample = ExperienceCorpus(store, discover=True).query(outcome="verified_success")[0]
    assert sample.state_after.semantic_predicates["exists"] is True
    assert not sample.delta.added and not sample.delta.changed


def test_caller_supplied_unwitnessed_prestate_cannot_create_a_causal_effect(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    receipt = store.store("task-verified", "unwitnessed_prestate_after.json", {
        "task_id": "task-verified", "run_id": "run-1", "operation_id": "op-1",
        "matched": True,
    }, schema="workstation.run_local_readback.v1").ref
    ref = capture_progressive(
        store, task_id="task-verified", run_id="run-1", operation_id="op-1",
        primitive="write_file", route="filesystem", outcome="verified_success",
        state_before={"exists": False}, state={"exists": True},
        verification=Verification(
            status="VERIFIED", evidence_refs=[receipt],
            evidence_strength=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
            trust_class="trusted_runtime", observer="workstation.readback",
            verifier_fingerprint="verified-fingerprint",
        ),
    )
    assert ref is not None
    sample = ExperienceCorpus(store, discover=True).query(outcome="verified_success")[0]
    assert sample.delta.changed == {}
    assert sample.delta.added == {}


def test_prestate_proof_wrong_run_wrong_value_or_missing_before_read_is_denied(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    after = store.store("task-verified", "after_verified.json", {
        "task_id": "task-verified", "run_id": "run-1",
        "operation_id": "op-1", "matched": True,
    }, schema="workstation.run_local_readback.v1").ref
    scenarios = {
        "foreign": {"run_id": "run-OTHER"},
        "contradicts": {"state": {"exists": True}},
        "not_witnessed": {"read_before_write": False},
    }
    for name, changes in scenarios.items():
        before = {
            "task_id": "task-verified", "run_id": "run-1",
            "operation_id": "op-1", "observer": "workstation.operational_prestate",
            "read_before_write": True, "state": {"exists": False},
        }
        before.update(changes)
        before_ref = store.store(
            "task-verified", f"before_{name}.json", before,
            schema="workstation.operational_prestate_readback.v1",
        ).ref
        assert capture_progressive(
            store, task_id="task-verified", run_id="run-1", operation_id="op-1",
            primitive="write_file", route="filesystem", outcome="verified_success",
            state={"exists": True}, state_before={"exists": False},
            state_before_ref=before_ref,
            verification=Verification(
                status="VERIFIED", evidence_refs=[after],
                evidence_strength=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
                trust_class="trusted_runtime", observer="workstation.readback",
                verifier_fingerprint="verified-fingerprint",
            ),
        ) is None
    assert ExperienceCorpus(store, discover=True).query(outcome="verified_success") == []


def test_progressive_rejects_prestate_and_post_readback_for_different_resources(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    before_ref = store.store("task-verified", "resource_a_before.json", {
        "task_id": "task-verified", "run_id": "run-1", "operation_id": "op-1",
        "observer": "workstation.operational_prestate", "read_before_write": True,
        "resource": str(tmp_path / "A.txt"), "state": {"exists": False},
    }, schema="workstation.operational_prestate_readback.v1").ref
    post_ref = store.store("task-verified", "resource_b_after.json", {
        "task_id": "task-verified", "run_id": "run-1", "operation_id": "op-1",
        "observer": "fs_hash", "read_after_write": True,
        "resource": str(tmp_path / "B.txt"), "value": "dummy-hash",
    }, schema="workstation.operational_filesystem_readback.v1").ref
    canonical_ref = store.store("task-verified", "canonical_cross_resource.json", {
        "task_id": "task-verified", "run_id": "run-1", "operation_id": "op-1",
        "result": {"status": "VERIFIED", "accepted": True, "evidence_refs": [post_ref]},
    }, schema="hermes.canonical_verification.v1").ref
    assert capture_progressive(
        store, task_id="task-verified", run_id="run-1", operation_id="op-1",
        primitive="write_file", route="filesystem", outcome="verified_success",
        state={"exists": True}, state_before={"exists": False}, state_before_ref=before_ref,
        verification=Verification(
            status="VERIFIED", evidence_refs=[canonical_ref],
            evidence_strength=EvidenceStrength.SEMANTIC_PERSISTED_READBACK,
            trust_class="trusted_runtime", observer="fs_hash",
            verifier_fingerprint="canonical-verifier",
        ),
    ) is None
    assert ExperienceCorpus(store, discover=True).query(outcome="verified_success") == []
