from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
import pathlib
from typing import Any

import pytest

from rebar_harness.benchmarks import load_manifest
from tests.benchmarks.benchmark_anchor_support_test_helpers import (
    _synthetic_case,
    _synthetic_manifest_loader,
    _synthetic_workload,
    _synthetic_workload_is_included,
    _synthetic_workload_signature,
    anchor_support_cache_guard,
)
from tests.benchmarks import benchmark_test_support as benchmark_support
from tests.benchmarks import source_tree_benchmark_anchor_support as anchor_support
from tests.benchmarks import standard_benchmark_anchor_support as support
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    assert_anchored_workload_case_result_parity,
    assert_benchmark_workload_matches_expected_result,
)
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
        benchmark_support,
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
        benchmark_support,
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


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    support._standard_benchmark_manifest_params(),
)
def test_standard_benchmark_manifest_keeps_expected_workloads_in_scope(
    definition: support.StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    workloads = load_manifest(manifest_path).workloads
    assert {
        workload.workload_id
        for workload in workloads
        if workload.workload_id in definition.expected_excluded_workload_ids
    } == definition.expected_excluded_workload_ids
    assert {
        workload.workload_id
        for workload in workloads
        if workload.workload_id in definition.expected_legacy_workload_ids
    } == definition.expected_legacy_workload_ids
    assert tuple(
        workload.workload_id
        for workload in workloads
        if definition.includes_workload(workload)
    ) == support._expected_workload_ids(definition, manifest_path)


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    support._standard_benchmark_manifest_params(),
)
def test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases(
    definition: support.StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    assert support._unanchored_case_ids(definition, manifest_path) == ()


@pytest.mark.parametrize(
    "definition",
    support.STANDARD_BENCHMARK_DEFINITIONS,
    ids=support._standard_benchmark_definition_id,
)
def test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids(
    definition: support.StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert support._anchored_case_ids(definition) == definition.expected_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    support._standard_benchmark_definition_params(
        include_definition=support._has_standard_benchmark_special_unanchored_workloads
    ),
)
def test_standard_benchmark_special_unanchored_workloads_stay_explicit(
    definition: support.StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert tuple(
        workload_id
        for manifest_path in definition.manifest_paths
        for workload_id in support._unanchored_case_ids(
            definition,
            manifest_path,
            include_special_unanchored=True,
        )
    ) == definition.expected_special_unanchored_workload_ids


@pytest.mark.parametrize(
    "definition",
    support._standard_benchmark_definition_params(
        include_definition=(
            support._has_standard_benchmark_special_unanchored_direct_parity_cases
        )
    ),
)
def test_standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases(
    definition: support.StandardBenchmarkAnchorContractDefinition,
) -> None:
    workloads_by_id = support._definition_workloads_by_id(definition)
    direct_parity_case_ids = support._direct_parity_case_ids_by_signature(
        definition.direct_parity_supplemental_cases
    )
    uncovered_workload_ids: list[str] = []

    for workload_id in definition.expected_special_unanchored_workload_ids:
        workload = workloads_by_id[workload_id]
        if workload.text_model != "bytes":
            continue
        if workload.operation not in {"module.search", "pattern.fullmatch"}:
            raise AssertionError(
                "expected bytes special-unanchored workload to stay on a direct-parity "
                f"search/fullmatch path, got {workload.operation!r}"
            )

        signature = (
            workload.operation,
            workload.pattern_payload(),
            workload.haystack_payload(),
        )
        case_ids = direct_parity_case_ids.get(signature)
        if case_ids is None:
            uncovered_workload_ids.append(workload_id)
            continue

        assert len(case_ids) == 1

    assert uncovered_workload_ids == []


@pytest.mark.parametrize(
    "definition",
    support._standard_benchmark_definition_params(
        include_definition=support._has_standard_benchmark_legacy_workloads
    ),
)
def test_standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids(
    definition: support.StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert {
        key: case_ids
        for key, case_ids in support._anchored_case_ids(definition).items()
        if key[1] in definition.expected_legacy_workload_ids
    } == support._expected_legacy_anchor_case_ids(definition)


@pytest.mark.parametrize(
    "definition",
    support._standard_benchmark_definition_params(
        include_definition=support._runs_standard_benchmark_callback_result_parity
    ),
)
def test_standard_benchmark_workload_callbacks_match_anchor_case_results(
    definition: support.StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert_anchored_workload_case_result_parity(
        support._expected_anchored_pairs(
            definition,
            expected_anchor_case_ids=support._expected_callback_anchor_case_ids(
                definition
            ),
        )
    )


@pytest.mark.parametrize(
    ("definition", "workload_id"),
    support._standard_benchmark_special_unanchored_result_parity_params(),
)
def test_standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch(
    definition: support.StandardBenchmarkAnchorContractDefinition,
    workload_id: str,
) -> None:
    workload = support._definition_workloads_by_id(definition)[workload_id]
    assert_benchmark_workload_matches_expected_result(
        workload,
        support._manual_expected_result(workload),
    )
