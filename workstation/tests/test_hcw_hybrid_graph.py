"""H-C3/H-C7/H-C9: declared graph, typed bindings and cache-content signatures."""
import hashlib
import pytest

from workstation.creative_hybrid_graph import (
    HybridGraphError, hybrid_render_key, plan_hybrid_dependencies,
    validate_hybrid_bindings,
)


A, B, C = "a" * 32, "b" * 32, "c" * 32


def test_nested_order_and_cycle_detection():
    assert plan_hybrid_dependencies([A, B, C], [(A, B), (B, C)]) == [C, B, A]
    with pytest.raises(HybridGraphError, match="cycle"):
        plan_hybrid_dependencies([A, B, C], [(A, B), (B, C), (C, A)])
    with pytest.raises(HybridGraphError, match="unknown"):
        plan_hybrid_dependencies([A], [(A, B)])
    with pytest.raises(HybridGraphError, match="Duplicate"):
        plan_hybrid_dependencies([A, A], [])


def test_declared_shared_binding_validation():
    bindings = [
        {"parameter": "headline.text", "composition_id": A, "property_path": "text/source"},
        {"parameter": "headline.text", "composition_id": B, "property_path": "params/headline"},
    ]
    assert validate_hybrid_bindings({A, B}, {"headline.text": {"type": "string", "value": "Hello"}}, bindings) == bindings
    with pytest.raises(HybridGraphError, match="unknown"):
        validate_hybrid_bindings({A}, {"headline.text": {"type": "string", "value": "Hello"}}, bindings)
    with pytest.raises(HybridGraphError, match="Duplicate"):
        validate_hybrid_bindings({A, B}, {"headline.text": {"type": "string", "value": "Hello"}}, bindings + [bindings[0]])


def test_cache_signature_binds_all_source_inputs_and_frame():
    items = {A: "1" * 64, B: "2" * 64}
    params = {"brand.primaryColor": "#ff7d3b"}
    one = hybrid_render_key(items, params, 40, "effectcraft:0.7/hyperframes:0.8", width=640, height=360, fps=(30, 1))
    assert one == hybrid_render_key(items, params, 40, "effectcraft:0.7/hyperframes:0.8", width=640, height=360, fps=(30, 1))
    assert one != hybrid_render_key(items, params, 41, "effectcraft:0.7/hyperframes:0.8", width=640, height=360, fps=(30, 1))
    assert one != hybrid_render_key(items, {"brand.primaryColor": "#129cdf"}, 40, "effectcraft:0.7/hyperframes:0.8", width=640, height=360, fps=(30, 1))
    assert one != hybrid_render_key({A: "3" * 64, B: "2" * 64}, params, 40, "effectcraft:0.7/hyperframes:0.8", width=640, height=360, fps=(30, 1))
    assert len(one) == 64 and bytes.fromhex(one)


def test_cache_refuses_nondeterministic_or_invalid_sources():
    with pytest.raises(HybridGraphError):
        hybrid_render_key({A: "wrong"}, {}, 1, "engine:a", width=640, height=360, fps=(30, 1))
    with pytest.raises(HybridGraphError):
        hybrid_render_key({A: "1" * 64}, {}, -1, "engine:a", width=640, height=360, fps=(30, 1))


def test_render_key_changes_when_external_media_or_color_profile_changes():
    base = {A: "1" * 64}
    params = {"color": "#ff7d3b"}
    common = dict(width=640, height=360, fps=(30000, 1001))
    one = hybrid_render_key(base, params, 12, "effectcraft=0.7/hyperframes=0.8",
                            asset_hashes={"asset1": "2" * 64}, color_profile="srgb", **common)
    other = hybrid_render_key(base, params, 12, "effectcraft=0.7/hyperframes=0.8",
                              asset_hashes={"asset1": "3" * 64}, color_profile="srgb", **common)
    wide = hybrid_render_key(base, params, 12, "effectcraft=0.7/hyperframes=0.8",
                             asset_hashes={"asset1": "2" * 64}, color_profile="display-p3", **common)
    assert one != other != wide != one
    with pytest.raises(HybridGraphError):
        hybrid_render_key(base, params, 12, "effectcraft=0.7",
                          asset_hashes={"asset1": "invalid"}, color_profile="srgb", **common)
