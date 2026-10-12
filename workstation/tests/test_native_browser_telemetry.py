"""Native-browser telemetry contracts: structural only, no new authority."""
import json
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

from workstation.telemetry import set_telemetry_sink
from workstation.telemetry.sqlite_sink import SQLiteTelemetrySink, TelemetryQuery
from workstation.telemetry.browser_observation import emit_native_browser_observation, strip_private_browser_telemetry


class NativeBrowserObservationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.db = Path(self.tmp.name) / "telemetry.sqlite"
        set_telemetry_sink(SQLiteTelemetrySink(self.db))

    def tearDown(self):
        set_telemetry_sink(None)
        self.tmp.cleanup()

    def emit(self, action, result, **opts):
        return emit_native_browser_observation(
            action=action, result=result, session_id="session-A", task_id="task-A",
            run_id="run-A", operation_id="operation-A", duration_ms=54.3,
            request_bytes=200, response_bytes=900, **opts)

    def test_ack_receipt_is_not_verified(self):
        self.emit("browser_click", {"success": True, "receipt": {"operationId": "operation-A"}})
        self.emit("browser_batch_actions", {"status": "verified", "verified_steps": 1, "completed_steps": 1},
                  operation_id_override="batch-B")
        rows = TelemetryQuery(self.db).events()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].status, "ACKNOWLEDGED")
        self.assertEqual(rows[1].status, "LOCAL_VERIFIED")
        self.assertEqual(rows[0].route, "native_browser")
        self.assertEqual(rows[1].run_id, "run-A")

    def test_snapshot_metrics_are_numeric_and_never_store_user_content(self):
        marker = "PRIVATE_FORM_SECRET_NEVER_PERSIST"
        self.emit("browser_snapshot", {
            "snapshot": marker,
            "__telemetry": {
                "snapshot_source": "ax",
                "cdp_calls": 19, "duration_ms": 120.2,
                "snapshot_chars": 6600, "delta_chars": 1300,
                "renderer_memory_bytes": 10_000,
                "password": marker,
            }
        })
        row = TelemetryQuery(self.db).events()[0]
        self.assertEqual(row.payload["snapshot_source"], "ax")
        self.assertEqual(row.payload["cdp_calls"], 19)
        self.assertEqual(row.payload["snapshot_chars"], 6600)
        self.assertNotIn("password", row.payload)
        self.assertNotIn(marker.encode(), self.db.read_bytes())

    def test_unverified_batch_and_failed_native_call_remain_uncertain(self):
        self.emit("browser_batch_actions", {"status": "uncertain", "completed_steps": 1,
                                           "verified_steps": 0, "reason": "input_value_mismatch"})
        self.emit("browser_type", None, error_code="CONTROLLER_DOWN",
                  operation_id_override="operation-B")
        rows = TelemetryQuery(self.db).events()
        self.assertEqual([row.status for row in rows], ["UNCERTAIN", "ERROR"])
        self.assertEqual(rows[0].payload["completed_steps"], 1)
        self.assertEqual(rows[0].payload["verified_steps"], 0)
        self.assertEqual(rows[1].reason_code, "CONTROLLER_DOWN")

    def test_attempt_and_terminal_events_detect_unresolved_mutations(self):
        from workstation.telemetry.projectors import project_native_browser_profile
        self.emit('browser_batch_actions', None, stage='attempt', operation_id_override='once-1')
        self.emit('browser_batch_actions', {'status': 'uncertain', 'completed_steps': 1},
                  operation_id_override='once-1')
        self.emit('browser_type', None, stage='attempt', operation_id_override='once-2')
        summary = project_native_browser_profile(TelemetryQuery(self.db).events())
        self.assertEqual(summary['attempts'], 2)
        self.assertEqual(summary['terminal_observations'], 1)
        self.assertEqual(summary['unresolved_attempts'], 1)
        self.assertEqual(summary['uncertain_batches'], 1)
        self.assertEqual(summary['latency_ms_p50'], 54.3)
        self.assertIsNone(summary['verified_external_outcomes'])

    def test_private_metrics_are_removed_before_model_response(self):
        marker = 'RAW_PRIVATE_DOM_NEVER_MODEL'
        raw = {'snapshot': 'public', '__telemetry': {'snapshot_source': 'dom', 'secret': marker}}
        public = strip_private_browser_telemetry(raw)
        self.assertEqual(public, {'snapshot': 'public'})
        self.assertIn('__telemetry', raw, 'no mutation of canonical raw observation')

    def test_real_bridge_dispatch_emits_attempt_and_result_without_model_metric_leak(self):
        import ast
        import os
        import time
        import types
        import uuid
        import typing
        import sys
        from tools import __path__ as tools_path

        source = (Path(tools_path[0]) / 'browser_workstation.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_dispatch')
        bridge = {}
        code = compile('from __future__ import annotations' + chr(10) + ast.unparse(fn), '<actual_browser_dispatch>', 'exec')
        events = []
        mock_batch = types.ModuleType('workstation.batch_detection')
        mock_batch.call_key = lambda action, args: 'test-call-key'
        bridge.update(os=os, time=time, uuid=uuid, json=json,
                      _DEFAULT_TIMEOUT_SECONDS=8.0,
                      _task_key=lambda task_id, session_id: 'test-task',
                      _force_redact=lambda value: value,
                      _bind=lambda key: events.append('bound'),
                      _request_json=lambda *a, **kw: {'result': {
                          'snapshot': 'VISIBLE_TO_MODEL', '__telemetry': {
                              'snapshot_source': 'dom', 'cdp_calls': 0,
                              'password': 'PRIVATE_NOT_MODEL'}}},
                      Dict=typing.Dict, Any=typing.Any, Optional=typing.Optional)
        with patch.dict(sys.modules, {'workstation.batch_detection': mock_batch}):
            exec(code, bridge)
            with patch.dict(os.environ, {}, clear=True):
                output = bridge['_dispatch']('browser_snapshot', {}, session_id='session-A',
                                             operation_id='bridge-op')
        public = json.loads(output)
        self.assertNotIn('__telemetry', public)
        self.assertEqual(public['snapshot'], 'VISIBLE_TO_MODEL')
        rows = TelemetryQuery(self.db).events()
        self.assertEqual([e.status for e in rows], ['REQUEST_ATTEMPTED', 'OBSERVED'])
        self.assertEqual(rows[1].payload['snapshot_source'], 'dom')
        self.assertEqual(events, ['bound'])
        self.assertNotIn(b'PRIVATE_NOT_MODEL', self.db.read_bytes())

    def test_telemetry_failure_does_not_change_control_result(self):
        class Broken:
            def emit(self, e):
                raise OSError("telemetry_is_unavailable")
        set_telemetry_sink(Broken())
        self.emit("browser_snapshot", {"success": True})


if __name__ == "__main__":
    unittest.main()
