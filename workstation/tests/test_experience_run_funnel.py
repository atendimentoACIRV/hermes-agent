"""Per-TaskRun learning funnel: cumulative, separated from global counters."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from workstation.artifacts import ArtifactStore
from workstation.experience_compiler.compilability_monitor import (
    CompilabilityEvent,
    OnlineCompilabilityMonitor,
    SHADOW,
)


class TaskRunFunnelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.artifacts = ArtifactStore(root_dir=Path(self.tmp.name) / "art")
        self.monitor = OnlineCompilabilityMonitor(
            artifacts=self.artifacts, mode=SHADOW, cooldown_seconds=0
        )
        self.addCleanup(self.monitor.stop)
        self.monitor._query_system1_compilability = lambda *args: {
            "stage": "keep_collecting",
            "confidence": 0.1,
        }

    def test_verified_capture_is_counted_only_for_this_run(self):
        event = CompilabilityEvent(
            event_kind="verified_transition",
            sample_ref="ref-real",
            task_id="task-1",
            run_id="run-1",
            operation_id="op-1",
            primitive="write_file",
            route="filesystem",
            outcome="verified_success",
        )
        self.monitor.process_event(event)
        result = self.monitor.task_run_funnel("task-1", "run-1")
        self.assertEqual(result["verified_evidence"], 1)
        self.assertEqual(result["processed_events"], 1)
        self.assertEqual(result["mode"], SHADOW)
        self.assertEqual(
            self.monitor.task_run_funnel("task-1", "other")["processed_events"], 0
        )

    def test_denials_are_not_counted_as_verified_reuse(self):
        self.monitor.record_adoption(
            "task-2",
            "run-1",
            {"kind": "denied", "reasons": ["readback_unavailable:write_file"]},
        )
        status = self.monitor.task_run_funnel("task-2", "run-1")
        self.assertEqual(status["adoption_denied"], 1)
        self.assertEqual(status["verified_reuse"], 0)
        self.assertEqual(status["denial_reasons"]["readback_unavailable:write_file"], 1)

    def test_unknown_run_query_does_not_create_artifacts(self):
        path = self.artifacts.root / "never-seen-task"
        self.assertFalse(path.exists())
        result = self.monitor.task_run_funnel("never-seen-task", "run-x")
        self.assertEqual(result["status"], "not_observed")
        self.assertFalse(path.exists())

    def test_checkpoint_round_trip_retains_cumulative_counts(self):
        event = CompilabilityEvent(
            event_kind="verified_transition",
            sample_ref="ref-a",
            task_id="task-persist",
            run_id="run-a",
            operation_id="op-a",
            primitive="read_file",
            route="filesystem",
            outcome="verified_success",
        )
        self.monitor.process_event(event)
        self.monitor.stop()
        another = OnlineCompilabilityMonitor(artifacts=self.artifacts, mode=SHADOW)
        self.addCleanup(another.stop)
        status = another.task_run_funnel("task-persist", "run-a")
        self.assertEqual(status["verified_evidence"], 1)
        self.assertEqual(status["processed_events"], 1)


if __name__ == "__main__":
    unittest.main()
