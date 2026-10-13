"""P0 deterministic external-effect timeout and human handoff, isolated.

This is an admission/ledger integration test with local HTTP I/O, NOT an
Electron Browser native E2E or a production provider verification.
"""
import json
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

from workstation.batch_detection import prepare_mutation
from workstation.integrations.hermes.tool_batch_admission import workstation_tool_batch_admission
from workstation.runtime import HumanHandoffManager
from workstation.execution_policy import CompilationDecision, decisions_for_calls


class EffectServer(BaseHTTPRequestHandler):
    calls = 0
    lock = threading.Lock()
    applied = threading.Event()

    def do_POST(self):
        with self.lock:
            type(self).calls += 1
        type(self).applied.set()
        time.sleep(0.12)
        try:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(str(type(self).calls).encode())

    def log_message(self, *_args):
        pass


def _agent(session):
    return SimpleNamespace(
        session_id=session,
        valid_tool_names={"work_execute"},
        _conversation_root_id=lambda: session,
    )


def _call(name, args):
    return SimpleNamespace(id="tool", function=SimpleNamespace(
        name=name, arguments=json.dumps(args)))


def test_uncertain_external_effect_requires_review_and_independent_readback(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    EffectServer.calls = 0
    EffectServer.applied.clear()
    server = ThreadingHTTPServer(("127.0.0.1", 0), EffectServer)
    server.timeout = 2
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        agent = _agent("session-a")
        args = {"ref": "@e17", "button": "left"}
        call = _call("browser_click", args)
        # Persist the pre-effect uncertainty before crossing remote I/O.
        prepare_mutation(agent, "browser_click", args)
        url = f"http://127.0.0.1:{server.server_port}"
        try:
            urllib.request.urlopen(urllib.request.Request(
                url + "/mutate", method="POST"), timeout=0.025)
        except (TimeoutError, urllib.error.URLError):
            pass
        assert EffectServer.applied.wait(2)
        assert EffectServer.calls == 1

        # A fresh agent/session recovers durable uncertainty rather than resending.
        reloaded = _agent("session-a")
        assert decisions_for_calls(reloaded, [call]) == [CompilationDecision.REQUIRE_HUMAN]
        first = workstation_tool_batch_admission(reloaded, [call])
        second = workstation_tool_batch_admission(reloaded, [call])
        a = json.loads(first.decisions[0].synthetic_result)
        b = json.loads(second.decisions[0].synthetic_result)
        assert a["handoff_id"] == b["handoff_id"]
        assert a["code"] == "uncertain_mutation_requires_review"

        # Independent read is allowed before and after explicit human review.
        read = _call("browser_snapshot", {})
        assert decisions_for_calls(reloaded, [read]) == [CompilationDecision.ALLOW_ADAPTIVE]
        with urllib.request.urlopen(url + "/readback", timeout=2) as response:
            assert response.read() == b"1"

        # A human review acknowledges uncertainty, NOT proof or replay authority.
        ledger = HumanHandoffManager(tmp_path / "workstation" / "human_handoffs.json")
        assert ledger.resume(a["handoff_id"], returned_by="human")
        third = workstation_tool_batch_admission(reloaded, [call])
        review = json.loads(third.decisions[0].synthetic_result)
        assert review["code"] == "uncertain_effect_requires_readback"
        assert HumanHandoffManager(ledger.path).get(a["handoff_id"]).status == "consumed"
        assert workstation_tool_batch_admission(reloaded, [call]).decisions[0].action is not None
        assert decisions_for_calls(reloaded, [call]) == [CompilationDecision.REQUIRE_HUMAN]
        assert EffectServer.calls == 1
        assert len(HumanHandoffManager(ledger.path)._handoffs) == 1

        # Other chats remain able to read despite this session's effect uncertainty.
        other = _agent("session-b")
        assert decisions_for_calls(other, [read]) == [CompilationDecision.ALLOW_ADAPTIVE]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)



def test_canonical_typed_readback_requires_matching_operation_run_and_persisted_source():
    """The existing typed verifier is strict; this does not publish a UI approval."""
    from dataclasses import replace
    from datetime import UTC, datetime
    from workstation.control_plane.verification import (
        VerificationContract, VerificationEvidence, VerificationLifecycle,
        VerificationStatus, evaluate_verification,
    )
    from workstation.execution_policy import EvidenceStrength

    contract = VerificationContract(
        observer="local_source_of_record_get",
        source_kind="source_of_record",
        covered_predicates=("external_effect_count",),
        effect_classes=("external_mutation",),
        resource_binding={"resource_id": "p0-loopback-effect"},
        minimum_evidence=EvidenceStrength.INDEPENDENT_PERSISTED_READBACK,
        allowed_trust=("trusted_owner",),
        require_read_after_write=True,
        transition_claim=True,
        lifecycle=VerificationLifecycle.VALIDATED,
    )
    evidence = VerificationEvidence(
        evidence_id="readback-after-timeout",
        observer="local_source_of_record_get",
        source_kind="source_of_record",
        value=1,
        evidence_strength=EvidenceStrength.INDEPENDENT_PERSISTED_READBACK,
        trust_class="trusted_owner",
        read_after_write=True,
        observed_at=datetime.now(UTC).isoformat(),
        covered_predicates=("external_effect_count",),
        resource_id="p0-loopback-effect",
        task_id="t-source",
        run_id="run-source",
        operation_id="op-source",
    )
    context = dict(
        mutation_failure_domains={"native_mutation_http"},
        expected_task_id="t-source",
        expected_run_id="run-source",
        expected_operation_id="op-source",
    )

    valid = evaluate_verification(contract, 1, [evidence], **context)
    assert valid.status == VerificationStatus.VERIFIED
    assert valid.transition_proven

    wrong_run = evaluate_verification(contract, 1, [replace(evidence, run_id="run-stale")], **context)
    assert wrong_run.status == VerificationStatus.INCONCLUSIVE
    assert wrong_run.reason == "run_id_mismatch"

    wrong_op = evaluate_verification(contract, 1, [replace(evidence, operation_id="op-foreign")], **context)
    assert wrong_op.status == VerificationStatus.INCONCLUSIVE
    assert "operation_id_mismatch" in wrong_op.reason

    too_weak = evaluate_verification(
        contract, 1, [replace(evidence, evidence_strength=EvidenceStrength.TOOL_ACK_ONLY)], **context)
    assert too_weak.status == VerificationStatus.INCONCLUSIVE

    stale = evaluate_verification(contract, 1, [replace(evidence, read_after_write=False)], **context)
    assert stale.status == VerificationStatus.STALE

    wrong_state = evaluate_verification(contract, 2, [evidence], **context)
    assert wrong_state.status == VerificationStatus.FAILED
