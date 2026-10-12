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
