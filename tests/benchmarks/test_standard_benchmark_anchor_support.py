from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
import pathlib
from typing import Any

import pytest

from tests.benchmarks.benchmark_anchor_support_test_helpers import (
    _synthetic_case,
    _synthetic_manifest_loader,
    _synthetic_workload,
    _synthetic_workload_is_included,
    _synthetic_workload_signature,
    anchor_support_cache_guard,
)
from tests.benchmarks import source_tree_benchmark_anchor_support as anchor_support
from tests.benchmarks import standard_benchmark_anchor_support as support
from tests.conftest import records_by_string_id


def _synthetic_case_signature(case: Any) -> tuple[Any, ...] | None:
    return case.signature


def _allow_all_workloads(_: Any) -> bool:
    return True


@dataclass(frozen=True, slots=True)
class _SyntheticStandardBenchmarkDefinition:
    manifest_paths: tuple[pathlib.Path, ...]
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    correctness_case_signature: Callable[[Any], tuple[Any, ...] | None]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    include_workload: Callable[[Any], bool]
    callback_anchor_workload_ids: frozenset[str] = frozenset()
    expected_legacy_workload_ids: frozenset[str] = frozenset()
    expected_special_unanchored_workload_ids: tuple[str, ...] = ()

    def includes_workload(self, workload: Any) -> bool:
        return (
            workload.workload_id not in self.expected_special_unanchored_workload_ids
            and self.include_workload(workload)
        )


def test_standard_benchmark_anchor_contract_definition_filters_excluded_workloads() -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    definition = support.StandardBenchmarkAnchorContractDefinition(
        name="synthetic",
        manifest_paths=(manifest_path,),
        expected_anchor_case_ids={},
        include_workload=_allow_all_workloads,
        correctness_case_signature=_synthetic_case_signature,
        workload_signature=_synthetic_workload_signature,
        expected_excluded_workload_ids=frozenset({"excluded"}),
        expected_special_unanchored_workload_ids=("special-unanchored",),
    )

    assert definition.includes_workload(_synthetic_workload("ordinary", ("shared",)))
    assert not definition.includes_workload(_synthetic_workload("excluded", ("shared",)))
    assert not definition.includes_workload(
        _synthetic_workload("special-unanchored", ("shared",))
    )


def test_definition_anchor_expectations_expand_manifest_name() -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")

    assert support._definition_anchor_expectations(
        manifest_path,
        {
            "workload-a": ("case-1", "case-2"),
            "workload-b": ("case-3",),
        },
    ) == {
        ("synthetic_boundary.py", "workload-a"): ("case-1", "case-2"),
        ("synthetic_boundary.py", "workload-b"): ("case-3",),
    }


def test_workload_case_pair_helpers_preserve_tuple_order() -> None:
    workload_case_pairs = (
        ("workload-a", "case-1"),
        ("workload-b", "case-2"),
        ("workload-c", "case-3"),
    )

    assert support._workload_case_pairs_workload_ids(workload_case_pairs) == (
        "workload-a",
        "workload-b",
        "workload-c",
    )
    assert support._workload_case_pairs_case_ids(workload_case_pairs) == (
        "case-1",
        "case-2",
        "case-3",
    )


def test_workload_case_pair_anchor_expectations_wrap_each_case_id() -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workload_case_pairs = (
        ("workload-a", "case-1"),
        ("workload-b", "case-2"),
    )

    assert support._workload_case_pair_anchor_expectations(
        manifest_path,
        workload_case_pairs,
    ) == {
        ("synthetic_boundary.py", "workload-a"): ("case-1",),
        ("synthetic_boundary.py", "workload-b"): ("case-2",),
    }


def test_expected_workload_ids_filter_to_manifest_name() -> None:
    first_manifest = pathlib.Path("first_boundary.py")
    second_manifest = pathlib.Path("second_boundary.py")
    definition = _SyntheticStandardBenchmarkDefinition(
        manifest_paths=(first_manifest, second_manifest),
        expected_anchor_case_ids={
            ("first_boundary.py", "first-a"): ("case-1",),
            ("second_boundary.py", "second-a"): ("case-2",),
            ("first_boundary.py", "first-b"): ("case-3",),
        },
        correctness_case_signature=_synthetic_case_signature,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
    )

    assert support._expected_workload_ids(definition, first_manifest) == (
        "first-a",
        "first-b",
    )
    assert support._expected_anchor_case_ids_for_manifest(definition, second_manifest) == {
        ("second_boundary.py", "second-a"): ("case-2",),
    }


def test_callback_and_legacy_anchor_subsets_select_expected_workloads() -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    definition = _SyntheticStandardBenchmarkDefinition(
        manifest_paths=(manifest_path,),
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "callback"): ("case-callback",),
            ("synthetic_boundary.py", "legacy"): ("case-legacy",),
            ("synthetic_boundary.py", "ordinary"): ("case-ordinary",),
        },
        correctness_case_signature=_synthetic_case_signature,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
        callback_anchor_workload_ids=frozenset({"callback"}),
        expected_legacy_workload_ids=frozenset({"legacy"}),
    )

    assert support._expected_callback_anchor_case_ids(definition) == {
        ("synthetic_boundary.py", "callback"): ("case-callback",),
    }
    assert support._expected_legacy_anchor_case_ids(definition) == {
        ("synthetic_boundary.py", "legacy"): ("case-legacy",),
    }


def test_anchor_helpers_resolve_anchored_and_unanchored_workloads(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",)),
        _synthetic_workload("excluded", ("shared",), include=False),
        _synthetic_workload("special-unanchored", ("missing",)),
    )
    definition = _SyntheticStandardBenchmarkDefinition(
        manifest_paths=(manifest_path,),
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
        },
        correctness_case_signature=_synthetic_case_signature,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
        expected_special_unanchored_workload_ids=("special-unanchored",),
    )

    monkeypatch.setattr(
        anchor_support,
        "load_manifest",
        partial(_synthetic_manifest_loader, workloads=workloads),
    )
    monkeypatch.setattr(
        support,
        "published_case_ids_by_signature",
        lambda _: {("shared",): ("case-1",)},
    )

    assert support._anchored_case_ids(definition) == {
        ("synthetic_boundary.py", "anchored"): ("case-1",),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert support._unanchored_case_ids(definition, manifest_path) == ("unanchored",)
    assert support._unanchored_case_ids(
        definition,
        manifest_path,
        include_special_unanchored=True,
    ) == (
        "unanchored",
        "special-unanchored",
    )


def test_expected_anchored_pairs_materialize_matching_workload_and_case_objects(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workload = _synthetic_workload("anchored", ("shared",))
    case = _synthetic_case("case-1", ("shared",))
    definition = _SyntheticStandardBenchmarkDefinition(
        manifest_paths=(manifest_path,),
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
            ("other_boundary.py", "ignored"): ("case-2",),
        },
        correctness_case_signature=_synthetic_case_signature,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
    )

    monkeypatch.setattr(
        anchor_support,
        "load_manifest",
        partial(_synthetic_manifest_loader, workloads=(workload,)),
    )
    monkeypatch.setattr(
        anchor_support,
        "published_cases_by_id",
        partial(records_by_string_id, (case,), id_attr="case_id"),
    )

    anchored_pairs = support._expected_anchored_pairs(definition)

    assert len(anchored_pairs) == 1
    anchored_pair = anchored_pairs[0]
    assert anchored_pair.manifest_name == "synthetic_boundary.py"
    assert anchored_pair.workload_id == "anchored"
    assert anchored_pair.case_id == "case-1"
    assert anchored_pair.workload is workload
    assert anchored_pair.case is case
