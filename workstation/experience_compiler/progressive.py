"""Progressive artifact capture; observation never implies promotion."""
import logging

from workstation.execution_policy import EvidenceStrength

from .models import TransitionSample, TransitionOutcome, Operation, Provenance, Verification
from .corpus import ExperienceCorpus
from .state_abstraction import abstract_state

logger = logging.getLogger(__name__)


def capture_progressive(artifacts, *, task_id, run_id, operation_id, primitive, route, outcome,
                        state=None, evidence_refs=(), verification=None):
    if not task_id or not run_id or not operation_id:
        return None
    if outcome == TransitionOutcome.VERIFIED_SUCCESS.value:
        # An observation with a caller-supplied "VERIFIED" flag is not enough.
        # Only a persisted, operation-bound owner readback may enter the corpus
        # as VERIFIED_SUCCESS. Later promotion remains independently gated.
        if (verification is None
                or verification.status != "VERIFIED"
                or verification.trust_class != "trusted_runtime"
                or verification.evidence_strength < EvidenceStrength.SEMANTIC_PERSISTED_READBACK
                or not verification.observer
                or not verification.verifier_fingerprint
                or not verification.evidence_refs):
            return None
        for ref in verification.evidence_refs:
            if not isinstance(ref, str) or not ref.startswith("artifact://tasks/"):
                return None
            try:
                evidence = artifacts.resolve_structured(ref)
            except (OSError, ValueError, KeyError):
                return None
            body = evidence.get("content")
            if (not isinstance(body, dict)
                    or body.get("task_id") != task_id
                    or str(body.get("run_id")) != str(run_id)
                    or body.get("operation_id") != operation_id):
                return None
            schema = evidence.get("schema")
            if schema == "workstation.run_local_readback.v1":
                if body.get("matched") is not True:
                    return None
            elif schema == "hermes.browser_local_readback.v1":
                if body.get("read_after_write") is not True or body.get("recovery_state") != "live":
                    return None
            elif schema == "hermes.canonical_verification.v1":
                result = body.get("result") or {}
                if (result.get("status") != "VERIFIED"
                        or result.get("accepted") is not True
                        or not result.get("evidence_refs")):
                    return None
                # The canonical verifier receipt must link to independently
                # persisted evidence, not just self-assert a terminal status.
                for proof_ref in result["evidence_refs"]:
                    if not isinstance(proof_ref, str):
                        return None
                    if not proof_ref.startswith(f"artifact://tasks/{task_id}/"):
                        return None
                    try:
                        underlying = artifacts.resolve_structured(proof_ref)
                    except (OSError, ValueError, KeyError):
                        return None
                    payload = underlying.get("content")
                    if underlying.get("content_omitted") or not underlying.get("schema"):
                        return None
                    if isinstance(payload, dict):
                        if (payload.get("task_id", task_id) != task_id
                                or str(payload.get("run_id", run_id)) != str(run_id)
                                or payload.get("operation_id", operation_id) != operation_id):
                            return None
                        if (underlying.get("schema") == "workstation.run_local_readback.v1"
                                and payload.get("matched") is not True):
                            return None
            else:
                return None
    sample = TransitionSample(operation=Operation(primitive=primitive, canonical_route=route),
        state_after=abstract_state(route, state or {}),
        outcome=TransitionOutcome(outcome), provenance=Provenance(task_id=task_id, run_id=str(run_id),
            operation_id=operation_id, source="progressive_owner", trust_class="trusted_runtime"),
        verification=verification or Verification(evidence_refs=list(evidence_refs)))
    try:
        return ExperienceCorpus(artifacts).capture(sample)
    except (OSError, ValueError):
        logger.warning("Progressive learning capture failed", exc_info=True)
        return None
