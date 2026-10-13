"""Experience Compiler API is a projection; mutation stores only invalidated drafts."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hermes_cli.web_routers import experience_compiler as api
from workstation.operational_capabilities import (
    OperationalCapability,
    CapabilityLifecycle,
)


class ExperienceApiTests(unittest.TestCase):
    def setUp(self):
        self.cap = OperationalCapability(
            id="example",
            name="Example",
            route="filesystem",
            effect="state_mutation",
            version="1.2.0",
            lifecycle=CapabilityLifecycle.PROMOTED,
            implementation={
                "steps": [
                    {
                        "id": "s1",
                        "primitive": "write_file",
                        "args": {"path": "$inputs.path", "content": "one"},
                    }
                ]
            },
        )
        self.registry = SimpleNamespace(
            list_capabilities=lambda: [self.cap],
            get=lambda cap_id, version=None: (
                self.cap if version in (None, "1.2.0") else None
            ),
            register=lambda cap, **kw: cap,
        )
        self.patcher = patch.object(api, "_registry", return_value=self.registry)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        app = FastAPI()
        app.include_router(api.router)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_catalog_and_page_are_read_only(self):
        response = self.client.get("/api/workstation/experience/capabilities")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["capabilities"][0]["nodes"][0]["id"], "s1")
        page = self.client.get("/experience-compiler")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Experience Compiler", page.text)

    def test_preview_does_not_persist_or_inherit_promoted(self):
        before = self.cap.to_dict()
        result = self.client.post(
            "/api/workstation/experience/revisions/preview",
            json={
                "capability_id": "example",
                "version": "1.2.0",
                "step_arguments": {"s1": {"content": "two"}},
            },
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["draft"]["lifecycle"], "discovered")
        self.assertEqual(self.cap.to_dict(), before)

    def test_save_draft_explicitly_requires_version_not_already_used(self):
        result = self.client.post(
            "/api/workstation/experience/revisions/save-draft",
            json={
                "capability_id": "example",
                "version": "1.2.0",
                "step_arguments": {"s1": {"content": "two"}},
            },
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["draft"]["version"], "1.2.1")
        self.assertEqual(self.cap.lifecycle, CapabilityLifecycle.PROMOTED)

    def test_save_composite_delegates_to_hierarchical_compiler(self):
        other = OperationalCapability(
            id="second", name="Second", lifecycle=CapabilityLifecycle.PROMOTED
        )
        previous = self.registry.get
        self.registry.get = lambda cid, version=None: (
            other if cid == "second" else previous(cid, version)
        )
        with patch(
            "workstation.experience_compiler.hierarchical.HierarchicalExperienceCompiler.propose_composite",
            return_value=OperationalCapability(
                id="comp", name="Composed", route="composite"
            ),
        ) as propose:
            response = self.client.post(
                "/api/workstation/experience/compositions/save-draft",
                json={
                    "capability_ids": ["example", "second"],
                    "links": [["example", "second"]],
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["runnable"])
        self.assertTrue(propose.call_args.kwargs["if_absent"])

    def test_graph_composition_refuses_loop(self):
        result = self.client.post(
            "/api/workstation/experience/compositions/preview",
            json={"capability_ids": ["example"], "links": [["example", "example"]]},
        )
        self.assertEqual(result.status_code, 422)


if __name__ == "__main__":
    unittest.main()
