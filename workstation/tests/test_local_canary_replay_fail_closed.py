"""Regression tests: product canary must never certify ignored steps."""

import time

from workstation.artifacts import ArtifactStore
from workstation.experience_compiler.lifecycle import create_local_canary_validation_provider
from workstation.tests.test_local_product_validation_provider import make_file_candidate


def _runner(tmp_path, candidate):
    provider = create_local_canary_validation_provider(
        artifacts=ArtifactStore(tmp_path / "artifacts"),
        sandbox_base=tmp_path / "sandbox",
    )
    return provider.replay_runner_factory(candidate, provider.safe_env_factory(candidate))


def test_replay_rejects_unimplemented_primitive_even_when_followed_by_write(tmp_path):
    candidate = make_file_candidate()
    candidate.implementation["steps"].insert(0, {
        "id": "step_unknown", "primitive": "unimplemented_primitive", "args": {},
    })
    result = _runner(tmp_path, candidate)(candidate.implementation["steps"], time.monotonic() + 10)
    assert result["passed"] is False
    assert result["failure"] == "unsupported_primitive"


def test_verifier_rejects_unsupported_read_before_positive_probe(tmp_path):
    from workstation.control_plane.verification import VerificationContract
    candidate = make_file_candidate()
    candidate.implementation["steps"] = [{
        "id": "step_read", "primitive": "read_file", "args": {"path": "input.txt"},
    }]
    provider = create_local_canary_validation_provider(
        artifacts=ArtifactStore(tmp_path / "artifacts"),
        sandbox_base=tmp_path / "sandbox",
    )
    positive, negative = provider.verifier_evaluator(
        candidate, VerificationContract.from_dict(candidate.verifier_contract), "task-local-1", "run-1"
    )
    assert positive is None and negative is None


def test_replay_rejects_unimplemented_read_without_silently_certifying(tmp_path):
    candidate = make_file_candidate()
    candidate.implementation["steps"] = [{
        "id": "step_read", "primitive": "read_file", "args": {"path": "missing.txt"},
    }]
    result = _runner(tmp_path, candidate)(candidate.implementation["steps"], time.monotonic() + 10)
    assert result["passed"] is False
    assert result["failure"] in {"unsupported_primitive", "readback_unavailable"}


def test_positive_verifier_must_replay_candidate_and_reject_traversal(tmp_path):
    from workstation.control_plane.verification import VerificationContract
    candidate = make_file_candidate()
    candidate.learning_metadata["bindings"] = [{"path": "../../escape.txt", "content": "ESCAPE"}]
    provider = create_local_canary_validation_provider(
        artifacts=ArtifactStore(tmp_path / "artifacts"),
        sandbox_base=tmp_path / "sandbox",
    )
    positive, negative = provider.verifier_evaluator(
        candidate, VerificationContract.from_dict(candidate.verifier_contract), "task-local-1", "run-1"
    )
    assert positive is None and negative is None
    assert not (tmp_path / "escape.txt").exists()


def test_positive_verifier_evidence_must_bind_candidate_result(tmp_path):
    from workstation.control_plane.verification import VerificationContract
    candidate = make_file_candidate()
    artifacts = ArtifactStore(tmp_path / "artifacts")
    provider = create_local_canary_validation_provider(artifacts=artifacts, sandbox_base=tmp_path / "sandbox")
    positive, negative = provider.verifier_evaluator(
        candidate, VerificationContract.from_dict(candidate.verifier_contract), "task-local-1", "run-1"
    )
    assert positive is not None and negative is not None
    evidence = artifacts.read_json(positive["evidence_ref"])
    assert evidence["candidate_id"] == candidate.id
    assert evidence["target_count"] == 1
    assert evidence["observed_digests"] == evidence["expected_digests"]
    assert "CANARY_TEST_CONTENT" not in str(evidence)
