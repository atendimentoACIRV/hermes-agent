"""Verified acceptance is the only bridge from canonical completion into Laya learning."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from workstation.experience_compiler import accepted_observer


class AcceptedObserverTests(unittest.TestCase):
    def test_verified_acceptance_notifies_model_with_owner_provenance(self):
        sample = SimpleNamespace(
            provenance=SimpleNamespace(
                sample_ref="artifact://verified", operation_id="op"
            ),
            operation=SimpleNamespace(
                primitive="write_file",
                canonical_route="filesystem",
                operation_family="make_report",
                target_family="file",
            ),
            verification=SimpleNamespace(evidence_refs=["artifact://readback"]),
        )
        corpus = SimpleNamespace(query=lambda **kw: [sample])
        with patch(
            "workstation.experience_compiler.compilability_monitor.notify_online_compilability",
            return_value=True,
        ) as send:
            self.assertTrue(
                accepted_observer.notify_canonical_acceptance(
                    corpus, "artifact://verified", "task", "run"
                )
            )
        self.assertEqual(send.call_args.kwargs["outcome"], "verified_success")
        self.assertEqual(
            send.call_args.kwargs["evidence_refs"], ("artifact://readback",)
        )

    def test_missing_or_unlinked_ref_does_not_issue_verified_event(self):
        corpus = SimpleNamespace(query=lambda **kw: [])
        with patch(
            "workstation.experience_compiler.compilability_monitor.notify_online_compilability"
        ) as send:
            self.assertFalse(
                accepted_observer.notify_canonical_acceptance(
                    corpus, "artifact://fake", "task", "run"
                )
            )
            self.assertFalse(
                accepted_observer.notify_canonical_acceptance(
                    corpus, None, "task", "run"
                )
            )
            send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
