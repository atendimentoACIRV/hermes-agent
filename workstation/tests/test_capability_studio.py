"""Contract tests for inspection and safe revisions of operational capabilities."""

import unittest
from workstation.operational_capabilities import (
    OperationalCapability,
    CapabilityLifecycle,
)
from workstation.experience_compiler import capability_studio


class CapabilityStudioTests(unittest.TestCase):
    def setUp(self):
        self.cap = OperationalCapability(
            id="hello",
            name="Write greeting",
            version="1.1.0",
            route="filesystem",
            effect="state_mutation",
            input_schema={
                "type": "object",
                "properties": {"target": {"type": "string"}},
            },
            implementation={
                "steps": [
                    {
                        "id": "write",
                        "primitive": "write_file",
                        "args": {"path": "$inputs.target", "content": "hello"},
                    }
                ]
            },
            preconditions=["target-allowed"],
            postconditions=["file-exists"],
            verifier_contract={"observer": "read_file"},
            semantic_fingerprint="old",
            compatibility_fingerprint="old",
            lifecycle=CapabilityLifecycle.PROMOTED,
        )

    def test_projection_displays_steps_guards_without_execution(self):
        before = self.cap.to_dict()
        graph = capability_studio.project_capability(self.cap)
        self.assertEqual(graph["nodes"][0]["id"], "write")
        self.assertEqual(graph["preconditions"], ["target-allowed"])
        self.assertEqual(graph["postconditions"], ["file-exists"])
        self.assertEqual(self.cap.to_dict(), before)

    def test_draft_revision_invalidates_proofs_and_does_not_modify_original(self):
        edited = capability_studio.draft_revision(
            self.cap,
            step_arguments={"write": {"content": "other"}},
            preconditions=["target-allowed", "size-small"],
        )
        self.assertEqual(edited.version, "1.1.1")
        self.assertEqual(edited.lifecycle, CapabilityLifecycle.DISCOVERED)
        self.assertEqual(edited.implementation["steps"][0]["args"]["content"], "other")
        self.assertEqual(edited.verifier_contract, {})
        self.assertEqual(edited.semantic_fingerprint, "")
        self.assertEqual(
            self.cap.implementation["steps"][0]["args"]["content"], "hello"
        )
        self.assertEqual(self.cap.lifecycle, CapabilityLifecycle.PROMOTED)

    def test_revision_rejects_unknown_steps_and_unsupported_structures(self):
        with self.assertRaises(ValueError):
            capability_studio.draft_revision(
                self.cap, step_arguments={"unknown": {"content": "x"}}
            )
        self.cap.implementation["steps"][0]["loop"] = {"forever": True}
        with self.assertRaises(ValueError):
            capability_studio.draft_revision(
                self.cap, step_arguments={"write": {"content": "x"}}
            )

    def test_human_draft_never_auto_promotes_from_validation_counter(self):
        import tempfile
        from pathlib import Path
        from workstation.artifacts import ArtifactStore
        from workstation.operational_capabilities import OperationalCapabilityRegistry

        with tempfile.TemporaryDirectory() as tmp:
            registry = OperationalCapabilityRegistry(
                ArtifactStore(root_dir=Path(tmp) / "artifacts"),
                root=Path(tmp) / "registry",
            )
            registry.register(capability_studio.draft_revision(self.cap))
            registry.record_validation(
                "hello", {"evidence": "first"}, auto_promote_threshold=2
            )
            validated = registry.record_validation(
                "hello", {"evidence": "second"}, auto_promote_threshold=2
            )
            self.assertNotEqual(validated.lifecycle, CapabilityLifecycle.PROMOTED)

    def test_draft_version_cannot_be_overwritten_by_second_save(self):
        import tempfile
        from pathlib import Path
        from workstation.artifacts import ArtifactStore
        from workstation.operational_capabilities import (
            CapabilityValidationError,
            OperationalCapabilityRegistry,
        )

        with tempfile.TemporaryDirectory() as tmp:
            registry = OperationalCapabilityRegistry(
                ArtifactStore(root_dir=Path(tmp) / "artifacts"),
                root=Path(tmp) / "registry",
            )
            draft = capability_studio.draft_revision(self.cap)
            registry.register(draft, if_absent=True)
            with self.assertRaises(CapabilityValidationError):
                registry.register(draft, if_absent=True)

    def test_composition_preview_refuses_cycles_and_produces_edges(self):
        second = OperationalCapability(
            id="send", name="Send", route="composite", effect="read_only"
        )
        graph = capability_studio.compose_preview(
            [self.cap, second], links=[("hello", "send")]
        )
        self.assertEqual(len(graph["nodes"]), 2)
        self.assertEqual(graph["edges"], [{"source": "hello", "target": "send"}])
        with self.assertRaises(ValueError):
            capability_studio.compose_preview(
                [self.cap, second], links=[("hello", "send"), ("send", "hello")]
            )


if __name__ == "__main__":
    unittest.main()
