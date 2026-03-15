from __future__ import annotations

import re

import pytest

from rebar_harness.descriptor_values import materialize_descriptor_value


CALLBACK_MODULE_NAME = "tests.descriptor_value_helpers"


@pytest.mark.parametrize(
    ("descriptor", "text_model", "pattern", "text", "expected_qualname", "expected_result"),
    (
        pytest.param(
            {
                "type": "callable_match_group",
                "group": "word",
                "prefix": "<",
                "suffix": ">",
            },
            "str",
            r"(?P<word>abc)",
            "zzabczz",
            "callable_match_group",
            "<abc>",
            id="str-callable-match-group",
        ),
        pytest.param(
            {
                "type": "callable_constant",
                "value": {
                    "type": "bytes",
                    "value": "CONST",
                    "encoding": "ascii",
                },
            },
            "bytes",
            rb"(abc)",
            b"zzabczz",
            "callable_constant",
            b"CONST",
            id="bytes-callable-constant",
        ),
    ),
)
def test_materialize_descriptor_value_builds_tagged_callable_descriptors(
    descriptor: dict[str, object],
    text_model: str,
    pattern: str | bytes,
    text: str | bytes,
    expected_qualname: str,
    expected_result: str | bytes,
) -> None:
    replacement = materialize_descriptor_value(
        descriptor,
        text_model=text_model,
        callback_module_name=CALLBACK_MODULE_NAME,
    )

    assert callable(replacement)
    assert replacement.__module__ == CALLBACK_MODULE_NAME
    assert replacement.__name__ == expected_qualname
    assert replacement.__qualname__ == expected_qualname

    match = re.search(pattern, text)
    assert match is not None
    assert replacement(match) == expected_result


def test_materialize_descriptor_value_recursively_converts_nested_bytes_values() -> None:
    descriptor = {
        "literal": "abc",
        "explicit_bytes": {
            "type": "bytes",
            "value": "XYZ",
            "encoding": "ascii",
        },
        "sequence": [
            "inner",
            {"nested": "value"},
            {
                "type": "callable_constant",
                "value": "CONST",
            },
        ],
    }

    materialized = materialize_descriptor_value(
        descriptor,
        text_model="bytes",
        callback_module_name=CALLBACK_MODULE_NAME,
    )

    assert materialized["literal"] == b"abc"
    assert materialized["explicit_bytes"] == b"XYZ"
    assert materialized["sequence"][0] == b"inner"
    assert materialized["sequence"][1] == {"nested": b"value"}

    constant_replacement = materialized["sequence"][2]
    assert callable(constant_replacement)
    assert constant_replacement.__module__ == CALLBACK_MODULE_NAME
    assert constant_replacement.__qualname__ == "callable_constant"

    descriptor["literal"] = "mutated"
    descriptor["sequence"][0] = "changed"
    descriptor["sequence"][1]["nested"] = "changed"
    descriptor["sequence"][2]["value"] = "changed"

    match = re.search(rb"(abc)", b"abc")
    assert match is not None
    assert constant_replacement(match) == b"CONST"
    assert materialized["literal"] == b"abc"
    assert materialized["sequence"][0] == b"inner"
    assert materialized["sequence"][1] == {"nested": b"value"}


def test_materialize_descriptor_value_rejects_unsupported_text_model_for_strings() -> None:
    with pytest.raises(ValueError, match=r"unsupported text model 'utf-16'"):
        materialize_descriptor_value("abc", text_model="utf-16")
