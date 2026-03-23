from __future__ import annotations

from collections import Counter
from types import ModuleType

from tests.conftest import (
    declared_string_constants_by_suffix,
    duplicate_items,
    duplicate_string_ids,
)


def test_duplicate_items_returns_sorted_duplicate_keys_once() -> None:
    duplicates = duplicate_items(Counter({"beta": 2, "alpha": 3, "gamma": 1, "delta": 4}))

    assert duplicates == ["alpha", "beta", "delta"]


def test_duplicate_string_ids_accepts_one_shot_iterators() -> None:
    case_ids = iter(
        (
            "module-search-shared",
            "pattern-fullmatch-shared",
            "module-search-shared",
            "compile-shared",
            "compile-shared",
        )
    )

    assert duplicate_string_ids(case_ids) == (
        "compile-shared",
        "module-search-shared",
    )


def test_declared_string_constants_by_suffix_filters_only_matching_strings_in_order() -> None:
    module = ModuleType("selector_contract_module")
    module.PUBLIC_SURFACE_FIXTURE_SELECTOR = "public-surface"
    module.RELATED_FLAG = "ignored"
    module.PARSER_FIXTURE_SELECTOR = "parser"
    module.BENCHMARK_MANIFEST_SELECTOR = 7
    module.NON_STRING_SELECTOR = ["still-ignored"]
    module.PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR = "published-full-suite"

    declared = declared_string_constants_by_suffix(
        module,
        name_suffix="_FIXTURE_SELECTOR",
    )

    assert tuple(declared.items()) == (
        ("PUBLIC_SURFACE_FIXTURE_SELECTOR", "public-surface"),
        ("PARSER_FIXTURE_SELECTOR", "parser"),
        ("PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR", "published-full-suite"),
    )


def test_declared_string_constants_by_suffix_returns_empty_dict_without_matching_strings() -> None:
    module = ModuleType("empty_selector_contract_module")
    module.UNRELATED = "value"
    module.NON_STRING_SELECTOR = 3

    assert declared_string_constants_by_suffix(module, name_suffix="_SELECTOR") == {}
