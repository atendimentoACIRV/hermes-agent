"""H-C3: strict offline HyperFrames declared-variable admission.

The native producer receives a JSON file created only from declared variables.
No source HTML rewriting or arbitrary command-line argument injection.
"""
import pytest

from workstation.creative_hyperframes_variables import (
    HyperframesVariableError, validated_hyperframes_overrides,
)


HTML = b"""<html data-composition-variables='[
 {"id":"title","type":"string","default":"Hello"},
 {"id":"bgColor","type":"color","default":"#000000"},
 {"id":"n","type":"number","default":1},
 {"id":"visible","type":"boolean","default":true}
]'><body></body></html>"""


def test_sorted_valid_declared_overrides_preserve_types():
    result = validated_hyperframes_overrides(
        HTML, {"visible": False, "bgColor": "#8b1e4f", "title": "Hermes", "n": 3.25}
    )
    assert result == b'{"bgColor":"#8b1e4f","n":3.25,"title":"Hermes","visible":false}'


@pytest.mark.parametrize("updates,match", [
    ({"undeclared": "x"}, "undeclared"),
    ({"n": True}, "number"),
    ({"visible": 1}, "boolean"),
    ({"bgColor": "red;url(javascript:1)"}, "color"),
    ({"title": "z" * 2000}, "string"),
    ({"n": float("nan")}, "number"),
])
def test_invalid_override_fail_closed(updates, match):
    with pytest.raises(HyperframesVariableError, match=match):
        validated_hyperframes_overrides(HTML, updates)


def test_duplicate_or_missing_declarations_are_rejected():
    with pytest.raises(HyperframesVariableError, match="duplicate"):
        validated_hyperframes_overrides(
            b'<html data-composition-variables=\'[{"id":"x","type":"string"},'
            b'{"id":"x","type":"string"}]\'>', {"x": "a"},
        )
    with pytest.raises(HyperframesVariableError, match="missing"):
        validated_hyperframes_overrides(b"<html></html>", {"x": "a"})


def test_read_only_source_html_is_never_modified():
    before = bytes(HTML)
    _ = validated_hyperframes_overrides(HTML, {"title": "Edited"})
    assert HTML == before
