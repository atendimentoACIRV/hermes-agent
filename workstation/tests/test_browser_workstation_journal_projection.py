"""Privacy-preserving native controller projection into the canonical ExecutionJournal."""
import tempfile
import unittest
from pathlib import Path

from workstation.contracts import ExecutionEventKind
from workstation.journal import ExecutionJournal
from tools import browser_workstation as bw


class BrowserJournalProjectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hermes-browser-journal-")
        self.addCleanup(self.temp.cleanup)

    def journal(self, task="task-a", session="session-a"):
        return ExecutionJournal(task, session, file_path=Path(self.temp.name) / "events.jsonl")

    def test_ack_is_causal_and_never_external_verification(self):
        journal = self.journal()
        bw._record_browser_controller_outcome(
            action="browser_type", task_id="task-a", session_id="session-a",
            run_id="run-a", operation_id="op-a",
            result={"success": True, "receipt": {"operationId": "op-a"}, "text": "PRIVATE_CANARY_DO_NOT_STORE"},
            journal=journal,
        )
        events = journal.read_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].kind, ExecutionEventKind.TOOL_CALL)
        self.assertEqual(events[0].metadata["status"], "ACKNOWLEDGED")
        self.assertEqual(events[0].metadata["run_id"], "run-a")
        self.assertEqual(events[0].metadata["operation_id"], "op-a")
        self.assertIs(events[0].metadata["externally_verified"], False)
        self.assertNotIn("PRIVATE_CANARY_DO_NOT_STORE", (Path(self.temp.name) / "events.jsonl").read_text())

    def test_reconciliation_is_never_misclassified_as_ack(self):
        journal = self.journal()
        bw._record_browser_controller_outcome(
            action="browser_click", task_id="task-a", session_id="session-a",
            run_id="run-b", operation_id="op-b",
            result={"status": "reconciliation_required", "blocked_operation_id": "op-a"},
            journal=journal,
        )
        event = journal.read_events()[-1]
        self.assertEqual(event.metadata["status"], "RECONCILIATION_REQUIRED")
        self.assertIs(event.metadata["externally_verified"], False)
        self.assertEqual(event.metadata["blocked_operation_id"], "op-a")

    def test_read_only_snapshot_is_not_mutation(self):
        journal = self.journal()
        bw._record_browser_controller_outcome(
            action="browser_snapshot", task_id="task-a", session_id="session-a",
            run_id="run-c", operation_id="op-c", result={"success": True, "text": "private"},
            journal=journal,
        )
        self.assertEqual(journal.read_events(), [])

    def test_controller_verified_claim_cannot_promote_without_independent_verifier(self):
        journal = self.journal()
        bw._record_browser_controller_outcome(
            action="browser_click", task_id="task-a", session_id="session-a",
            run_id="run-d", operation_id="op-d",
            result={"status": "verified", "externally_verified": True},
            journal=journal,
        )
        record = journal.read_events()[-1]
        self.assertEqual(record.metadata["status"], "ACKNOWLEDGED")
        self.assertIs(record.metadata["externally_verified"], False)

    def test_unknown_controller_outcome_remains_uncertain(self):
        journal = self.journal()
        bw._record_browser_controller_outcome(
            action="browser_navigate", task_id="task-a", session_id="session-a",
            run_id="run-e", operation_id="op-e",
            result={"status": "uncertain", "html": "<input value='SECRET'>"},
            journal=journal,
        )
        record = journal.read_events()[-1]
        self.assertEqual(record.metadata["status"], "UNCERTAIN")
        self.assertIs(record.metadata["externally_verified"], False)
        self.assertNotIn("SECRET", (Path(self.temp.name) / "events.jsonl").read_text())


if __name__ == "__main__":
    unittest.main()
