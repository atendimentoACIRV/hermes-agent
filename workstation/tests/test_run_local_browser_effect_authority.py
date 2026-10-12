"""EC-03: native browser navigation must not be admitted as a read-only adoption."""

from workstation.control_plane.ir import CALL
from workstation.run_adoption import effects_for_step


def test_browser_navigation_requires_effect_and_readback():
    effect = effects_for_step(
        "browser_navigate", {"url": "https://trello.com/"}, {"host": "trello.com"}
    )
    assert effect == [CALL("browser.navigate", "trello.com")]


def test_browser_navigation_rejects_out_of_scope_or_unverifiable_destination():
    assert effects_for_step(
        "browser_navigate", {"url": "https://another.example/"}, {"host": "trello.com"}
    ) is None
    assert effects_for_step(
        "browser_navigate", {"url": "https://trello.com/"}, {}
    ) is None
    assert effects_for_step(
        "browser_navigate", {"url": "javascript:alert(1)"}, {"host": "trello.com"}
    ) is None

from workstation.artifacts import ArtifactStore
from workstation.control_plane.lattice import AuthorityScope, AuthorityLevel
from workstation.run_adoption import (
    AdoptionOffer, CanonicalRunSnapshot, DurableRunAdoptionOwner,
    PendingRunItem, plan_item_adoption,
)


def test_browser_navigation_requires_canonical_owner_readback_before_adoption(tmp_path):
    artifact_store = ArtifactStore(tmp_path / "artifacts")
    owner = DurableRunAdoptionOwner(
        lambda: None, artifact_store,
        authority_for_task=lambda task: AuthorityScope(),
        dispatch_fn=lambda *args: None,
        supported_primitives=("browser_navigate",),
        readback_primitives=(),  # owner does not certify browser state
    )
    offer = AdoptionOffer(
        offer_id="offer", task_id="task", run_id="run", candidate_id="cap",
        proof=None, steps=[{
            "id": "navigate", "primitive": "browser_navigate",
            "args": {"url": "$inputs.url"},
        }],
        input_schema={"type": "object", "properties": {"url": {"type": "string"}},
                      "required": ["url"]},
        relations=[], operation_family="browser.open_site",
        target_family="native_browser", route="native_browser",
        scope={"host": "trello.com"},
    )
    snap = CanonicalRunSnapshot(
        task_id="task", run_id="run", plan_id="plan",
        authority=AuthorityScope(level=AuthorityLevel.EXTERNAL_REVERSIBLE,
                                 allowed_actions={"*"}, allowed_resources={"*"}),
        effect_budget=(CALL("browser.navigate", "trello.com"),),
        lease_valid=True, termination="", uncertain_mutations=(),
        pending_items=(PendingRunItem(
            item_id="item", item_index=0, payload={"url": "https://trello.com/"},
            status="pending", attempts=0, has_checkpoints=False,
            operation_family="browser.open_site", target_family="native_browser",
        ),),
        remaining_items_ref="artifact://tasks/task/pending",
        allowed_targets=frozenset({"native_browser"}),
    )
    plan, reasons = plan_item_adoption(snap, offer, owner)
    assert plan is None
    assert reasons == ["readback_unavailable:browser_navigate"]

    # Once a real independent verifier exists, the canonical lease and the
    # exact effect budget must still be revalidated before any dispatch.
    from dataclasses import replace

    owner._readback = lambda *_: {"ok": True}
    owner._readback_primitives.add("browser_navigate")
    plan, reasons = plan_item_adoption(replace(snap, lease_valid=False), offer, owner)
    assert plan is None and reasons == ["lease_not_valid"]
    plan, reasons = plan_item_adoption(replace(snap, effect_budget=()), offer, owner)
    assert plan is None and reasons == ["effect_budget_missing"]
