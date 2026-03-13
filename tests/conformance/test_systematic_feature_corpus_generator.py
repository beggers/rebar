from __future__ import annotations

import pathlib
import sys

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


from rebar_harness.systematic_corpus import (
    GENERATOR_ID,
    GENERATOR_VERSION,
    expand_systematic_manifest,
)


def test_expand_systematic_manifest_passes_through_literal_manifests() -> None:
    raw_manifest = {
        "schema_version": 1,
        "manifest_id": "literal-manifest",
        "cases": [{"id": "literal-case", "operation": "compile", "pattern": "abc"}],
    }

    expanded = expand_systematic_manifest(raw_manifest)

    assert expanded == raw_manifest


def test_expand_systematic_manifest_renders_defaults_templates_and_case_metadata() -> None:
    raw_manifest = {
        "schema_version": 1,
        "manifest_id": "systematic-manifest",
        "defaults": {"text_model": "bytes"},
        "generator": {"id": GENERATOR_ID, "version": GENERATOR_VERSION},
        "feature_specs": [
            {
                "id": "feature",
                "family_prefix": "systematic_feature",
                "categories": ["feature-category"],
                "notes": ["feature note"],
                "variants": [
                    {
                        "id": "named",
                        "pattern": "a(?P<word>b)d",
                        "group_name": "word",
                        "categories": ["variant-category"],
                        "notes": ["variant note"],
                    }
                ],
                "expansions": [
                    {
                        "id": "module-search",
                        "operation": "module_call",
                        "family_suffix": "module_search_workflow",
                        "helper": "search",
                        "args": ["{pattern}", "zzabdzz"],
                        "kwargs": {"group_name": "{group_name}", "variant": "{variant_id}"},
                        "categories": ["expansion-category"],
                        "notes": ["expansion note"],
                    },
                    {
                        "id": "pattern-fullmatch",
                        "operation": "pattern_call",
                        "helper": "fullmatch",
                        "args": ["abd"],
                        "text_model": "str",
                        "include_pattern": False,
                    },
                ],
            }
        ],
    }

    expanded = expand_systematic_manifest(raw_manifest)

    assert "cases" in expanded
    assert len(expanded["cases"]) == 2

    module_case, pattern_case = expanded["cases"]

    assert module_case == {
        "id": "systematic-feature-named-module-search-bytes",
        "family": "systematic_feature_named_module_search_workflow",
        "operation": "module_call",
        "helper": "search",
        "args": ["a(?P<word>b)d", "zzabdzz"],
        "kwargs": {"group_name": "word", "variant": "named"},
        "notes": ["feature note", "variant note", "expansion note"],
        "categories": [
            "systematic",
            "feature-category",
            "variant-category",
            "expansion-category",
        ],
        "text_model": "bytes",
    }
    assert pattern_case == {
        "id": "systematic-feature-named-pattern-fullmatch-str",
        "family": "systematic_feature_named_pattern_fullmatch",
        "operation": "pattern_call",
        "helper": "fullmatch",
        "args": ["abd"],
        "notes": ["feature note", "variant note"],
        "categories": ["systematic", "feature-category", "variant-category"],
        "text_model": "str",
    }


@pytest.mark.parametrize(
    ("raw_manifest", "message"),
    [
        (
            {"generator": "systematic_feature_corpus"},
            "fixture manifest generator must be an object",
        ),
        (
            {
                "generator": {"id": "other-generator", "version": GENERATOR_VERSION},
            },
            "unsupported fixture generator 'other-generator'",
        ),
        (
            {
                "generator": {"id": GENERATOR_ID, "version": GENERATOR_VERSION + 1},
            },
            f"unsupported {GENERATOR_ID} generator version {GENERATOR_VERSION + 1!r}; "
            f"expected {GENERATOR_VERSION}",
        ),
        (
            {
                "generator": {"id": GENERATOR_ID, "version": GENERATOR_VERSION},
                "feature_specs": [],
            },
            "systematic corpus manifests require a non-empty feature_specs list",
        ),
        (
            {
                "generator": {"id": GENERATOR_ID, "version": GENERATOR_VERSION},
                "feature_specs": [{"id": "feature", "variants": [], "expansions": []}],
            },
            "feature spec 'feature' requires a non-empty variants list",
        ),
        (
            {
                "generator": {"id": GENERATOR_ID, "version": GENERATOR_VERSION},
                "feature_specs": [
                    {
                        "id": "feature",
                        "variants": [{"id": "variant", "pattern": "abc"}],
                        "expansions": [],
                    }
                ],
            },
            "feature spec 'feature' requires a non-empty expansions list",
        ),
        (
            {
                "generator": {"id": GENERATOR_ID, "version": GENERATOR_VERSION},
                "cases": [{"id": "literal-case"}],
                "feature_specs": [{"id": "feature", "variants": [], "expansions": []}],
            },
            "systematic corpus manifests must not define literal cases",
        ),
        (
            {
                "generator": {"id": GENERATOR_ID, "version": GENERATOR_VERSION},
                "feature_specs": [
                    {
                        "id": "feature",
                        "variants": [{"id": "named", "pattern": "abc"}],
                        "expansions": [
                            {
                                "id": "broken-template",
                                "operation": "module_call",
                                "helper": "{missing_key}",
                            }
                        ],
                    }
                ],
            },
            "missing template key 'missing_key'",
        ),
    ],
)
def test_expand_systematic_manifest_rejects_invalid_specs(
    raw_manifest: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        expand_systematic_manifest(raw_manifest)
