from __future__ import annotations

from collections import Counter
from types import SimpleNamespace

import pytest

import tests.conftest as test_support
from tests.conftest import (
    duplicate_items,
    duplicate_string_ids,
    manifest_records_by_id,
    records_by_string_id,
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


def test_manifest_records_by_id_returns_original_records_keyed_by_manifest_id() -> None:
    manifest_a = SimpleNamespace(manifest_id="manifest-a", payload="alpha")
    manifest_b = SimpleNamespace(manifest_id="manifest-b", payload="beta")

    manifests_by_id = manifest_records_by_id(iter((manifest_a, manifest_b)))

    assert list(manifests_by_id) == ["manifest-a", "manifest-b"]
    assert manifests_by_id["manifest-a"] is manifest_a
    assert manifests_by_id["manifest-b"] is manifest_b


def test_records_by_string_id_returns_original_records_keyed_by_requested_id_in_input_order(
) -> None:
    case_a = SimpleNamespace(case_id="case-a", payload="alpha")
    case_b = SimpleNamespace(case_id="case-b", payload="beta")

    cases_by_id = records_by_string_id(
        iter((case_a, case_b)),
        id_attr="case_id",
    )

    assert list(cases_by_id) == ["case-a", "case-b"]
    assert cases_by_id["case-a"] is case_a
    assert cases_by_id["case-b"] is case_b


def test_records_by_string_id_rejects_duplicate_ids() -> None:
    duplicate_case_id = "duplicate-case"

    with pytest.raises(
        AssertionError,
        match=rf"duplicate ids: \['{duplicate_case_id}'\]",
    ):
        records_by_string_id(
            (
                SimpleNamespace(case_id=duplicate_case_id, payload="alpha"),
                SimpleNamespace(case_id=duplicate_case_id, payload="beta"),
            ),
            id_attr="case_id",
        )


def test_manifest_records_by_id_rejects_duplicate_manifest_ids() -> None:
    duplicate_manifest_id = "duplicate-manifest"

    with pytest.raises(
        AssertionError,
        match=rf"duplicate ids: \['{duplicate_manifest_id}'\]",
    ):
        manifest_records_by_id(
            (
                SimpleNamespace(manifest_id=duplicate_manifest_id, payload="alpha"),
                SimpleNamespace(manifest_id=duplicate_manifest_id, payload="beta"),
            )
        )


@pytest.mark.parametrize(
    "helper_name",
    (
        "run_harness_cli",
        "completed_process",
        "report_path_from_cli_args",
        "fake_harness_cli_scorecard_result",
        "run_harness_scorecard",
    ),
    ids=(
        "run_harness_cli",
        "completed_process",
        "report_path_from_cli_args",
        "fake_harness_cli_scorecard_result",
        "run_harness_scorecard",
    ),
)
def test_owner_local_harness_helpers_are_not_shared_from_tests_conftest(
    helper_name: str,
) -> None:
    assert not hasattr(test_support, helper_name)
