from __future__ import annotations

import ast
import importlib
import pathlib
from types import SimpleNamespace
import unittest

import pytest

from rebar_harness import benchmarks
from tests.benchmarks import benchmark_test_support
from tests.benchmarks import (
    collection_replacement_benchmark_anchor_support as collection_support,
)
from tests.benchmarks import (
    pattern_boundary_benchmark_anchor_support as pattern_boundary_support,
)
from tests.benchmarks import source_tree_benchmark_anchor_support as support
from tests.conftest import REPO_ROOT

anchor_support_cache_guard = benchmark_test_support.anchor_support_cache_guard


def _synthetic_report_scorecard(
    *,
    workloads: tuple[dict[str, object], ...],
    artifacts: dict[str, object],
    baseline: dict[str, object],
    phase: str = "synthetic-phase",
    runner_version: str = "synthetic-runner",
    native_module_loaded: bool = False,
) -> dict[str, object]:
    known_gap_statuses = {"known-gap", "unimplemented"}

    def _known_gap_count(rows: list[dict[str, object]]) -> int:
        return sum(
            1
            for row in rows
            if row["status"] in known_gap_statuses
        )

    family_ids = sorted(
        {
            "module",
            "parser",
            *(str(row["family"]) for row in workloads),
        }
    )
    cache_mode_ids = sorted({str(row["cache_mode"]) for row in workloads})
    families: dict[str, dict[str, object]] = {}
    for family_id in family_ids:
        family_rows = [
            row
            for row in workloads
            if row["family"] == family_id
        ]
        families[family_id] = {
            "workload_count": len(family_rows),
            "known_gap_count": _known_gap_count(family_rows),
            "cache_modes": {
                cache_mode: {
                    "workload_count": len(
                        [
                            row
                            for row in family_rows
                            if row["cache_mode"] == cache_mode
                        ]
                    ),
                    "known_gap_count": _known_gap_count(
                        [
                            row
                            for row in family_rows
                            if row["cache_mode"] == cache_mode
                        ]
                    ),
                }
                for cache_mode in sorted(
                    {
                        str(row["cache_mode"])
                        for row in family_rows
                    }
                )
            },
        }
    cache_modes = {
        cache_mode: {
            "workload_count": len(
                [
                    row
                    for row in workloads
                    if row["cache_mode"] == cache_mode
                ]
            ),
            "known_gap_count": _known_gap_count(
                [
                    row
                    for row in workloads
                    if row["cache_mode"] == cache_mode
                ]
            ),
        }
        for cache_mode in cache_mode_ids
    }
    measured_workloads = sum(
        1
        for row in workloads
        if row["status"] == "measured"
    )
    summary: dict[str, object] = {
        "known_gap_count": _known_gap_count(list(workloads)),
        "measured_workloads": measured_workloads,
        "module_workloads": sum(
            1
            for row in workloads
            if row["family"] == "module"
        ),
        "parser_workloads": sum(
            1
            for row in workloads
            if row["family"] == "parser"
        ),
        "regression_workloads": sum(
            1
            for row in workloads
            if row["manifest_id"] == "regression-matrix"
        ),
        "total_workloads": len(workloads),
        "workloads_by_cache_mode": {
            cache_mode: cache_modes[cache_mode]["workload_count"]
            for cache_mode in cache_mode_ids
        },
    }
    if measured_workloads:
        summary.update(
            {
                "baseline_median_ns": 101,
                "baseline_median_ops_per_second": 9.9,
                "implementation_median_ns": 151,
                "implementation_median_ops_per_second": 6.6,
            }
        )

    return {
        "schema_version": "1.0",
        "suite": "benchmarks",
        "phase": phase,
        "baseline": baseline,
        "implementation": {
            "module_name": "rebar",
            "adapter": "source-tree-shim",
            "adapter_mode_requested": "source-tree-shim",
            "adapter_mode_resolved": "source-tree-shim",
            "build_mode": "source-tree-shim",
            "timing_path": "source-tree-shim",
            "native_build_tool": None,
            "native_wheel": None,
            "native_module_loaded": native_module_loaded,
            "native_module_name": "rebar._rebar",
            "native_scaffold_status": (
                "scaffold-only" if native_module_loaded else None
            ),
            "native_target_cpython_series": (
                "3.12.x" if native_module_loaded else None
            ),
            "native_unavailable_reason": (
                "native timing not requested for synthetic contract coverage"
            ),
        },
        "environment": {
            "runner_version": runner_version,
            "execution_model": "single-process in-process adapter comparison",
        },
        "summary": summary,
        "families": families,
        "cache_modes": cache_modes,
        "workloads": list(workloads),
        "artifacts": artifacts,
    }


def _summary_view(scorecard: dict[str, object]) -> dict[str, object]:
    summary = scorecard["summary"]
    assert isinstance(summary, dict)
    return {
        key: summary[key]
        for key in (
            "known_gap_count",
            "measured_workloads",
            "module_workloads",
            "parser_workloads",
            "regression_workloads",
            "total_workloads",
        )
    }


def test_freeze_signature_value_canonicalizes_nested_mappings_and_lists() -> None:
    value = {
        "b": [2, {"d": 4, "c": [5, 6]}],
        "a": {"y": 1, "x": 0},
    }

    assert benchmark_test_support.freeze_signature_value(value) == (
        ("a", (("x", 0), ("y", 1))),
        ("b", (2, (("c", (5, 6)), ("d", 4)))),
    )
    assert not hasattr(support, "freeze_signature_value")


def test_definition_anchor_expectations_expand_manifest_name() -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")

    assert benchmark_test_support._definition_anchor_expectations(
        manifest_path,
        {
            "workload-a": ("case-1", "case-2"),
            "workload-b": ("case-3",),
        },
    ) == {
        ("synthetic_boundary.py", "workload-a"): ("case-1", "case-2"),
        ("synthetic_boundary.py", "workload-b"): ("case-3",),
    }
    assert not hasattr(support, "_definition_anchor_expectations")


def test_workload_case_pair_anchor_expectations_wrap_each_case_id() -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workload_case_pairs = (
        ("workload-a", "case-1"),
        ("workload-b", "case-2"),
    )

    assert benchmark_test_support._workload_case_pair_anchor_expectations(
        manifest_path,
        workload_case_pairs,
    ) == {
        ("synthetic_boundary.py", "workload-a"): ("case-1",),
        ("synthetic_boundary.py", "workload-b"): ("case-2",),
    }
    assert not hasattr(support, "_workload_case_pair_anchor_expectations")


def test_source_tree_combined_representative_workload_ids_prefer_explicit_manifest_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest_id = "synthetic-boundary"
    expected_workload_ids = ("explicit-a", "explicit-b")

    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
        {
            manifest_id: support.SourceTreeCombinedManifestExpectationDefinition(
                representative_measured_workload_ids=expected_workload_ids,
            ),
        },
    )
    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS",
        (
            support.SourceTreeCombinedSliceExpectation(
                manifest_id=manifest_id,
                slice_id="synthetic-slice",
                expected_workload_ids=("slice-row",),
            ),
        ),
    )

    assert (
        support.source_tree_combined_manifest_representative_measured_workload_ids(
            manifest_id
        )
        == expected_workload_ids
    )


def test_source_tree_combined_representative_workload_ids_derive_unique_shape_and_slice_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest_id = "synthetic-boundary"

    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
        {
            manifest_id: support.SourceTreeCombinedManifestExpectationDefinition(
                shape_expectation=support.SourceTreeCombinedManifestShapeExpectation(
                    representative_measured_workload_ids=(
                        "shape-a",
                        "shape-b",
                    ),
                ),
            ),
        },
    )
    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS",
        (
            support.SourceTreeCombinedSliceExpectation(
                manifest_id=manifest_id,
                slice_id="source-tree-slice",
                expected_workload_ids=("shape-b", "source-tree-c"),
            ),
            support.SourceTreeCombinedSliceExpectation(
                manifest_id=manifest_id,
                slice_id="collection-owned-slice",
                expected_workload_ids=("source-tree-c", "collection-d"),
            ),
        ),
    )

    assert (
        support.source_tree_combined_manifest_representative_measured_workload_ids(
            manifest_id
        )
        == ("shape-a", "shape-b", "source-tree-c", "collection-d")
    )


def test_deleted_zero_gap_representative_helpers_are_absent_from_support_module(
) -> None:
    assert not hasattr(support, "assert_zero_gap_bytes_representative_subset")
    assert not hasattr(support, "assert_zero_gap_manifest_representative_promotion")


def test_source_tree_combined_manifest_representative_workload_ids_restore_zero_gap_bytes_subset_public_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest_id = "synthetic-boundary"
    expected_workload_ids = ("bytes-a", "bytes-b")

    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
        {
            manifest_id: support.SourceTreeCombinedManifestExpectationDefinition(
                representative_measured_workload_ids=(
                    "bytes-a",
                    "bytes-b",
                    "other-representative",
                ),
                zero_gap_bytes_representative_subsets=(expected_workload_ids,),
            ),
        },
    )
    manifest_definition = support.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
        manifest_id
    ]

    assert expected_workload_ids in (
        manifest_definition.zero_gap_bytes_representative_subsets
    )
    assert (
        support.source_tree_combined_manifest_representative_measured_workload_ids(
            manifest_id
        )
        == (
            "bytes-a",
            "bytes-b",
            "other-representative",
        )
    )


def test_direct_zero_gap_manifest_assertions_use_selected_counts_from_public_case_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest_id = "synthetic-boundary"
    expected_workload_ids = ("promoted-a", "promoted-b")
    selected_workload_ids = ("row-a", "row-b", "row-c")
    target_manifest_path = pathlib.Path("benchmarks/workloads/synthetic_boundary.py")
    captured_call: dict[str, object] = {}

    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
        {
            manifest_id: support.SourceTreeCombinedManifestExpectationDefinition(
                representative_measured_workload_ids=expected_workload_ids,
            ),
        },
    )
    monkeypatch.setattr(
        support,
        "source_tree_combined_case",
        lambda observed_manifest_id: SimpleNamespace(
            manifest_expectation=support.SourceTreeManifestExpectation(
                known_gap_count=0,
                representative_measured_workload_ids=expected_workload_ids,
                representative_known_gap_workload_ids=(),
            ),
            target_manifest=SimpleNamespace(path=target_manifest_path),
            selected_workload_ids_for_manifest=lambda selected_manifest_id: (
                selected_workload_ids
                if observed_manifest_id == manifest_id
                and selected_manifest_id == manifest_id
                else ()
            ),
        ),
    )
    monkeypatch.setattr(
        benchmark_test_support,
        "assert_zero_gap_manifest_workloads_measured",
        lambda **kwargs: captured_call.update(kwargs),
    )

    manifest_definition = support.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
        manifest_id
    ]
    case = support.source_tree_combined_case(manifest_id)
    manifest_expectation = case.manifest_expectation

    assert manifest_definition.known_gap_workload_ids is None
    assert (manifest_definition.representative_known_gap_workload_ids or ()) == ()
    assert manifest_expectation.known_gap_count == 0
    assert manifest_expectation.representative_known_gap_workload_ids == ()
    assert (
        manifest_definition.representative_measured_workload_ids
        == expected_workload_ids
    )
    assert (
        manifest_expectation.representative_measured_workload_ids
        == expected_workload_ids
    )

    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=case.target_manifest.path,
        manifest_id=manifest_id,
        expected_measured_workload_ids=expected_workload_ids,
        expected_measured_workload_count=len(
            case.selected_workload_ids_for_manifest(manifest_id)
        ),
    )

    assert captured_call == {
        "manifest_path": target_manifest_path,
        "manifest_id": manifest_id,
        "expected_measured_workload_ids": expected_workload_ids,
        "expected_measured_workload_count": len(selected_workload_ids),
    }


def test_select_source_tree_combined_slice_rows_filters_suffix_features_and_categories(
) -> None:
    manifest = SimpleNamespace(
        workloads=(
            SimpleNamespace(
                workload_id="first-keep",
                syntax_features=("feature-a", "feature-b"),
                categories=("cat-a", "cat-b"),
            ),
            SimpleNamespace(
                workload_id="wrong-suffix",
                syntax_features=("feature-a",),
                categories=("cat-a",),
            ),
            SimpleNamespace(
                workload_id="missing-feature-keep",
                syntax_features=("feature-b",),
                categories=("cat-a",),
            ),
            SimpleNamespace(
                workload_id="excluded-feature-keep",
                syntax_features=("feature-a", "feature-x"),
                categories=("cat-a",),
            ),
            SimpleNamespace(
                workload_id="missing-category-keep",
                syntax_features=("feature-a",),
                categories=("cat-b",),
            ),
            SimpleNamespace(
                workload_id="excluded-category-keep",
                syntax_features=("feature-a",),
                categories=("cat-a", "cat-x"),
            ),
            SimpleNamespace(
                workload_id="second-keep",
                syntax_features=("feature-a",),
                categories=("cat-a",),
            ),
        ),
    )
    expectation = support.SourceTreeCombinedSliceExpectation(
        manifest_id="synthetic-boundary",
        slice_id="synthetic-slice",
        required_syntax_features=("feature-a",),
        excluded_syntax_features=("feature-x",),
        required_categories=("cat-a",),
        excluded_categories=("cat-x",),
        required_id_suffix="-keep",
    )

    assert [
        workload.workload_id
        for workload in support.select_source_tree_combined_slice_rows(
            manifest,
            expectation,
        )
    ] == ["first-keep", "second-keep"]


def test_expected_summary_for_manifests_ignores_known_gaps_from_empty_selected_manifests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selected_gap = SimpleNamespace(
        workload_id="module-compile-synthetic-gap",
        family="parser",
    )
    regression_measured = SimpleNamespace(
        workload_id="module-search-regression-measured",
        family="module",
    )
    manifests = [
        SimpleNamespace(
            manifest_id="synthetic-boundary",
            selected_workloads=lambda *, selection_mode: (selected_gap,),
        ),
        SimpleNamespace(
            manifest_id="unselected-boundary",
            selected_workloads=lambda *, selection_mode: (),
        ),
        SimpleNamespace(
            manifest_id="regression-matrix",
            selected_workloads=lambda *, selection_mode: (regression_measured,),
        ),
    ]
    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
        {
            "synthetic-boundary": support.SourceTreeCombinedManifestExpectationDefinition(
                known_gap_workload_ids=("module-compile-synthetic-gap",),
            ),
            "unselected-boundary": (
                support.SourceTreeCombinedManifestExpectationDefinition(
                    known_gap_workload_ids=("module-search-unselected-gap",),
                )
            ),
        },
    )

    assert support.expected_summary_for_manifests(
        manifests,
        selection_mode="smoke",
    ) == {
        "known_gap_count": 1,
        "measured_workloads": 1,
        "module_workloads": 1,
        "parser_workloads": 1,
        "regression_workloads": 1,
        "total_workloads": 2,
    }


def test_source_tree_combined_case_rejects_unknown_target_manifest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        support,
        "published_benchmark_manifests",
        lambda: [
            SimpleNamespace(manifest_id="module-boundary", workloads=()),
            SimpleNamespace(manifest_id="regression-matrix", workloads=()),
        ],
    )

    with pytest.raises(
        AssertionError,
        match="target manifest 'synthetic-boundary' is not in the published full-suite selector",
    ):
        support.source_tree_combined_case("synthetic-boundary")


def test_source_tree_combined_case_requires_regression_manifest_for_non_module_targets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        support,
        "published_benchmark_manifests",
        lambda: [
            SimpleNamespace(manifest_id="module-boundary", workloads=()),
            SimpleNamespace(manifest_id="synthetic-boundary", workloads=()),
        ],
    )

    with pytest.raises(
        AssertionError,
        match="the published full-suite selector is missing the regression-matrix manifest",
    ):
        support.source_tree_combined_case("synthetic-boundary")


@pytest.mark.parametrize(
    ("target_manifest_id", "expected_manifest_ids"),
    (
        pytest.param(
            "module-boundary",
            ("compile-matrix", "module-boundary"),
            id="module-boundary-excludes-regression",
        ),
        pytest.param(
            "synthetic-boundary",
            (
                "compile-matrix",
                "module-boundary",
                "synthetic-boundary",
                "regression-matrix",
            ),
            id="non-module-target-appends-regression",
        ),
    ),
)
def test_source_tree_combined_case_selects_expected_manifest_prefix_for_target(
    monkeypatch: pytest.MonkeyPatch,
    target_manifest_id: str,
    expected_manifest_ids: tuple[str, ...],
) -> None:
    compile_workload = SimpleNamespace(
        workload_id="module-compile-compile-matrix-cold-gap",
        family="parser",
    )
    module_workload = SimpleNamespace(
        workload_id="module-search-module-boundary-warm-str",
        family="module",
    )
    target_workload = SimpleNamespace(
        workload_id="pattern-fullmatch-synthetic-boundary-purged-str",
        family="module",
    )
    regression_workload = SimpleNamespace(
        workload_id="module-search-regression-warm-str",
        family="module",
    )
    manifests = [
        SimpleNamespace(
            manifest_id="compile-matrix",
            workloads=(compile_workload,),
        ),
        SimpleNamespace(
            manifest_id="module-boundary",
            workloads=(module_workload,),
        ),
        SimpleNamespace(
            manifest_id="regression-matrix",
            workloads=(regression_workload,),
        ),
        SimpleNamespace(
            manifest_id="synthetic-boundary",
            workloads=(target_workload,),
        ),
        SimpleNamespace(
            manifest_id="later-boundary",
            workloads=(
                SimpleNamespace(
                    workload_id="module-search-later-boundary-warm-str",
                    family="module",
                ),
            ),
        ),
    ]
    payloads: list[str] = []
    summary_call: dict[str, object] = {}
    manifest_expectation = support.SourceTreeManifestExpectation(
        known_gap_count=1,
        representative_measured_workload_ids=("module-search-module-boundary-warm-str",),
        representative_known_gap_workload_ids=(
            "module-compile-compile-matrix-cold-gap",
        ),
    )

    monkeypatch.setattr(
        support,
        "published_benchmark_manifests",
        lambda: manifests,
    )
    monkeypatch.setattr(
        support,
        "workload_to_payload",
        lambda workload: payloads.append(workload.workload_id) or workload.workload_id,
    )
    monkeypatch.setattr(
        support,
        "determine_phase",
        lambda observed_payloads: f"phase:{','.join(observed_payloads)}",
    )
    monkeypatch.setattr(
        support,
        "determine_runner_version",
        lambda observed_payloads: f"runner:{len(observed_payloads)}",
    )
    monkeypatch.setattr(
        support,
        "expected_summary_for_manifests",
        lambda observed_manifests, *, selection_mode, manifest_known_gap_counts=None: (
            summary_call.update(
                {
                    "manifest_ids": tuple(
                        manifest.manifest_id for manifest in observed_manifests
                    ),
                    "selection_mode": selection_mode,
                    "manifest_known_gap_counts": manifest_known_gap_counts,
                }
            )
            or {
                "known_gap_count": len(observed_manifests),
                "measured_workloads": len(observed_manifests) + 1,
                "module_workloads": sum(
                    len(
                        [
                            workload
                            for workload in manifest.workloads
                            if workload.family == "module"
                        ]
                    )
                    for manifest in observed_manifests
                ),
                "parser_workloads": sum(
                    len(
                        [
                            workload
                            for workload in manifest.workloads
                            if workload.family == "parser"
                        ]
                    )
                    for manifest in observed_manifests
                ),
                "regression_workloads": sum(
                    len(manifest.workloads)
                    for manifest in observed_manifests
                    if manifest.manifest_id == "regression-matrix"
                ),
                "total_workloads": sum(
                    len(manifest.workloads) for manifest in observed_manifests
                ),
            }
        ),
    )
    monkeypatch.setattr(
        support,
        "_public_source_tree_manifest_expectation",
        lambda manifest_id: (
            manifest_expectation if manifest_id == target_manifest_id else None
        ),
    )

    case = support.source_tree_combined_case(target_manifest_id)

    assert tuple(manifest.manifest_id for manifest in case.manifests) == (
        expected_manifest_ids
    )
    assert case.manifest_id == target_manifest_id
    assert case.target_manifest.manifest_id == target_manifest_id
    assert case.manifest_expectation is manifest_expectation
    assert case.expected_adapter == "rebar.module-surface"
    assert case.expected_phase == f"phase:{','.join(payloads)}"
    assert case.expected_runner_version == f"runner:{len(payloads)}"
    assert case.expected_summary == {
        "known_gap_count": len(expected_manifest_ids),
        "measured_workloads": len(expected_manifest_ids) + 1,
        "module_workloads": sum(
            len(
                [
                    workload
                    for workload in manifest.workloads
                    if workload.family == "module"
                ]
            )
            for manifest in case.manifests
        ),
        "parser_workloads": sum(
            len(
                [
                    workload
                    for workload in manifest.workloads
                    if workload.family == "parser"
                ]
            )
            for manifest in case.manifests
        ),
        "regression_workloads": (
            1 if target_manifest_id != "module-boundary" else 0
        ),
        "total_workloads": len(expected_manifest_ids),
    }
    assert summary_call == {
        "manifest_ids": expected_manifest_ids,
        "selection_mode": "full",
        "manifest_known_gap_counts": None,
    }


def test_source_tree_combined_target_manifest_ids_rejects_missing_expectation_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        support,
        "published_benchmark_manifests",
        lambda: [
            SimpleNamespace(manifest_id="module-boundary"),
            SimpleNamespace(manifest_id="synthetic-boundary"),
            SimpleNamespace(manifest_id="regression-matrix"),
        ],
    )
    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
        {
            "module-boundary": support.SourceTreeCombinedManifestExpectationDefinition(),
            "regression-matrix": (
                support.SourceTreeCombinedManifestExpectationDefinition(
                    exclude_from_combined_targets=True,
                )
            ),
        },
    )

    with pytest.raises(
        AssertionError,
        match=(
            "source-tree combined manifest expectations drifted from the "
            "published full-suite selector: missing \\['synthetic-boundary'\\]"
        ),
    ):
        support.source_tree_combined_target_manifest_ids()


def test_source_tree_combined_target_manifest_ids_preserve_order_and_exclusion_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        support,
        "published_benchmark_manifests",
        lambda: [
            SimpleNamespace(manifest_id="compile-matrix"),
            SimpleNamespace(manifest_id="module-boundary"),
            SimpleNamespace(manifest_id="synthetic-boundary"),
            SimpleNamespace(manifest_id="regression-matrix"),
        ],
    )
    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
        {
            "compile-matrix": support.SourceTreeCombinedManifestExpectationDefinition(
                exclude_from_combined_targets=True,
            ),
            "module-boundary": support.SourceTreeCombinedManifestExpectationDefinition(),
            "synthetic-boundary": (
                support.SourceTreeCombinedManifestExpectationDefinition()
            ),
            "regression-matrix": (
                support.SourceTreeCombinedManifestExpectationDefinition(
                    exclude_from_combined_targets=True,
                )
            ),
        },
    )

    assert support.source_tree_combined_target_manifest_ids() == (
        "module-boundary",
        "synthetic-boundary",
    )


def test_deleted_source_tree_wrapper_helpers_are_absent() -> None:
    for attribute_name in (
        "source_tree_combined_manifest_shape_expectation",
        "source_tree_combined_slice_manifest_ids",
        "source_tree_combined_slice_expectations",
    ):
        assert not hasattr(support, attribute_name)


def test_source_tree_combined_slice_manifest_filter_keeps_only_slice_derived_contracts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        support,
        "source_tree_combined_target_manifest_ids",
        lambda: (
            "explicit-boundary",
            "shape-boundary",
            "slice-derived-boundary",
        ),
    )
    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
        {
            "explicit-boundary": (
                support.SourceTreeCombinedManifestExpectationDefinition(
                    representative_measured_workload_ids=("explicit-row",),
                )
            ),
            "shape-boundary": (
                support.SourceTreeCombinedManifestExpectationDefinition(
                    shape_expectation=support.SourceTreeCombinedManifestShapeExpectation(
                        representative_measured_workload_ids=("shape-row",),
                    ),
                )
            ),
            "slice-derived-boundary": (
                support.SourceTreeCombinedManifestExpectationDefinition()
            ),
        },
    )
    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS",
        (
            support.SourceTreeCombinedSliceExpectation(
                manifest_id="explicit-boundary",
                slice_id="explicit-slice",
            ),
            support.SourceTreeCombinedSliceExpectation(
                manifest_id="shape-boundary",
                slice_id="shape-slice",
            ),
            support.SourceTreeCombinedSliceExpectation(
                manifest_id="slice-derived-boundary",
                slice_id="slice-derived-slice",
            ),
        ),
    )

    combined_target_manifest_ids = (
        "explicit-boundary",
        "shape-boundary",
        "slice-derived-boundary",
    )
    manifest_ids_with_slice_expectations = {
        expectation.manifest_id
        for expectation in support.SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS
    }
    assert tuple(
        manifest_id
        for manifest_id in combined_target_manifest_ids
        if manifest_id in manifest_ids_with_slice_expectations
        and support.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            manifest_id
        ].representative_measured_workload_ids
        is None
        and support.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            manifest_id
        ].shape_expectation
        is None
    ) == (
        "slice-derived-boundary",
    )


@pytest.mark.parametrize(
    ("case", "pattern", "expected"),
    (
        pytest.param(
            SimpleNamespace(
                operation="compile",
                helper="",
                flags=None,
                text_model=None,
                serialized_args=lambda: [],
                serialized_kwargs=lambda: {"window": [1, 3]},
            ),
            "a((b))d",
            ("module.compile", "a((b))d", (), (("window", (1, 3)),), 0, "str"),
            id="compile-defaults",
        ),
        pytest.param(
            SimpleNamespace(
                operation="module_call",
                helper="search",
                flags=4,
                text_model="bytes",
                serialized_args=lambda: [b"a((b))d", b"zzabdzz"],
                serialized_kwargs=lambda: {"pos": [1, 4]},
            ),
            b"ignored",
            (
                "module.search",
                None,
                (b"a((b))d", b"zzabdzz"),
                (("pos", (1, 4)),),
                4,
                "bytes",
            ),
            id="module-search",
        ),
        pytest.param(
            SimpleNamespace(
                operation="pattern_call",
                helper="fullmatch",
                flags=2,
                text_model="bytes",
                serialized_args=lambda: [b"abd"],
                serialized_kwargs=lambda: {"endpos": [3]},
            ),
            b"a((b))d",
            (
                "pattern.fullmatch",
                b"a((b))d",
                (b"abd",),
                (("endpos", (3,)),),
                2,
                "bytes",
            ),
            id="pattern-fullmatch",
        ),
        pytest.param(
            SimpleNamespace(
                operation="module_call",
                helper="match",
                flags=None,
                text_model=None,
                serialized_args=lambda: ["zzabdzz"],
                serialized_kwargs=lambda: {},
            ),
            "a((b))d",
            None,
            id="unsupported-operation",
        ),
    ),
)
def test_compile_search_fullmatch_case_signature_routes_shared_operations(
    case: object,
    pattern: str | bytes,
    expected: tuple[object, ...] | None,
) -> None:
    assert support._compile_search_fullmatch_case_signature(
        case,
        pattern=lambda: pattern,
    ) == expected


@pytest.mark.parametrize(
    ("workload", "pattern", "module_search_args", "pattern_fullmatch_args", "expected"),
    (
        pytest.param(
            SimpleNamespace(
                operation="module.compile",
                flags=0,
                text_model="str",
            ),
            "a((b))d",
            ("unused-search",),
            ("unused-fullmatch",),
            ("module.compile", "a((b))d", (), (), 0, "str"),
            id="compile",
        ),
        pytest.param(
            SimpleNamespace(
                operation="module.search",
                flags=4,
                text_model="bytes",
            ),
            b"a((b))d",
            (b"a((b))d", b"zzabdzz"),
            (b"unused-fullmatch",),
            ("module.search", None, (b"a((b))d", b"zzabdzz"), (), 4, "bytes"),
            id="module-search",
        ),
        pytest.param(
            SimpleNamespace(
                operation="pattern.fullmatch",
                flags=2,
                text_model="bytes",
            ),
            b"a((b))d",
            (b"unused-search",),
            (b"abd",),
            ("pattern.fullmatch", b"a((b))d", (b"abd",), (), 2, "bytes"),
            id="pattern-fullmatch",
        ),
    ),
)
def test_compile_search_fullmatch_workload_signature_routes_shared_operations(
    workload: object,
    pattern: str | bytes,
    module_search_args: tuple[object, ...],
    pattern_fullmatch_args: tuple[object, ...],
    expected: tuple[object, ...],
) -> None:
    assert support._compile_search_fullmatch_workload_signature(
        workload,
        pattern=lambda: pattern,
        module_search_args=lambda: module_search_args,
        pattern_fullmatch_args=lambda: pattern_fullmatch_args,
        error_label="synthetic benchmark",
    ) == expected


def test_compile_search_fullmatch_workload_signature_rejects_unsupported_operations(
) -> None:
    workload = SimpleNamespace(
        operation="pattern.search",
        flags=0,
        text_model="str",
    )

    with pytest.raises(
        AssertionError,
        match="unexpected synthetic benchmark workload operation 'pattern.search'",
    ):
        support._compile_search_fullmatch_workload_signature(
            workload,
            pattern=lambda: "a((b))d",
            module_search_args=lambda: ("unused-search",),
            pattern_fullmatch_args=lambda: ("unused-fullmatch",),
            error_label="synthetic benchmark",
        )


@pytest.mark.parametrize(
    ("owner_module", "helper_names"),
    (
        pytest.param(
            collection_support,
            (
                "freeze_signature_value",
                "_workload_case_pair_anchor_expectations",
            ),
            id="collection-replacement",
        ),
    ),
)
def test_former_owner_modules_share_source_tree_helpers_without_local_duplicates(
    owner_module: object,
    helper_names: tuple[str, ...],
) -> None:
    local_definition_names, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            owner_module
        )
    )
    owner_support = owner_module.benchmark_test_support

    assert owner_support is benchmark_test_support

    for helper_name in helper_names:
        assert getattr(owner_support, helper_name) is getattr(
            benchmark_test_support,
            helper_name,
        )
        assert helper_name not in local_definition_names
        assert helper_name not in local_assignment_names
        assert not hasattr(owner_module, helper_name)


def test_source_tree_support_module_exposes_moved_combined_case_surface() -> None:
    module_ast = benchmark_test_support._parsed_module_ast(support)
    _, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            support
        )
    )
    local_class_names = {
        node.name for node in module_ast.body if isinstance(node, ast.ClassDef)
    }
    local_function_names = {
        node.name for node in module_ast.body if isinstance(node, ast.FunctionDef)
    }

    for class_name in (
        "SourceTreeBenchmarkCommonCase",
        "SourceTreeManifestExpectation",
        "SourceTreeDeferredExpectation",
        "SourceTreeScorecardCase",
        "SourceTreeCombinedCase",
        "SourceTreeCombinedPatternGroupExpectation",
        "SourceTreeCombinedManifestShapeExpectation",
        "SourceTreeCombinedFullyMeasuredManifestExpectation",
        "SourceTreeCombinedManifestExpectationDefinition",
        "SourceTreeCombinedSliceExpectation",
    ):
        assert hasattr(support, class_name)
        assert class_name in local_class_names
    for function_name in (
        "source_tree_scorecard_case",
        "source_tree_combined_target_manifest_ids",
        "source_tree_combined_case",
        "expected_summary_for_manifests",
        "select_source_tree_combined_slice_rows",
    ):
        assert hasattr(support, function_name)
        assert function_name in local_function_names
    assert not hasattr(support, "_combined_slice_expectation")
    assert "_combined_slice_expectation" not in local_function_names
    for function_name, owner_type in (
        (
            "compiled_pattern_module_compile_contract_builder_spec",
            benchmark_test_support.CompiledPatternModuleCompileContractCase,
        ),
        (
            "compiled_pattern_module_success_contract_builder_spec",
            support.CompiledPatternModuleSuccessOwnerSpec,
        ),
        (
            "compiled_pattern_module_helper_keyword_contract_builder_spec",
            benchmark_test_support._CompiledPatternModuleHelperKeywordContractSpec,
        ),
    ):
        local_builder = getattr(support, function_name, None)
        owner_builder = getattr(owner_type, "contract_builder_spec", None)

        assert local_builder is None
        assert owner_builder is not None
        assert function_name not in local_function_names
    for constant_name in (
        "SOURCE_TREE_SCORECARD_EXPECTATIONS",
        "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
        "SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS",
    ):
        assert hasattr(support, constant_name)
        assert constant_name in local_assignment_names
    for constant_name in (
        "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
        "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES",
        "_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS",
        "_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
    ):
        if constant_name == "_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS":
            assert constant_name not in local_assignment_names
            assert not hasattr(support, constant_name)
            assert hasattr(benchmark_test_support, constant_name)
            continue
        assert constant_name in local_assignment_names
        assert hasattr(support, constant_name)
        assert not hasattr(benchmark_test_support, constant_name)
    for function_name in (
        "relative_manifest_path",
        "source_tree_scorecard_case_ids",
    ):
        assert function_name not in local_function_names
        assert not hasattr(support, function_name)
    benchmark_test_support.assert_mixed_owner_surface(
        support,
        local_function_names=frozenset(),
        local_assignment_names=frozenset(
            {
                "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
                "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS",
                "_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS",
                "_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS",
                "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES",
            }
        ),
        support_alias_assignment_names=frozenset(),
    )
    for removed_name in (
        "compiled_pattern_contract_expected_build_calls",
        "_compiled_pattern_module_helper_route",
    ):
        assert not hasattr(support, removed_name)
        assert removed_name not in local_assignment_names
    for constant_name in (
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS",
        "_is_collection_replacement_compiled_pattern_keyword_error_workload",
    ):
        assert not hasattr(support, constant_name)
        assert constant_name not in local_function_names
        assert constant_name not in local_assignment_names
        assert hasattr(collection_support, constant_name)
    assert hasattr(
        collection_support,
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS",
    )
    assert hasattr(
        support,
        "_assert_compiled_pattern_module_success_payload_round_trip",
    )
    assert (
        "_assert_compiled_pattern_module_success_payload_round_trip"
        in local_function_names
    )
    assert not hasattr(
        support,
        "_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call",
    )
    assert (
        "_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call"
        not in local_assignment_names
    )
    for constant_name in (
        "CompiledPatternModuleSuccessOwnerSpec",
        "_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS",
    ):
        assert hasattr(support, constant_name)
    assert "CompiledPatternModuleSuccessOwnerSpec" in local_function_names
    for constant_name in (
        "_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS",
    ):
        assert constant_name in local_assignment_names
    for constant_name in (
        "_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload",
        "_is_module_workflow_compiled_pattern_literal_success_workload",
        "_is_module_workflow_compiled_pattern_verbose_bytes_success_workload",
        "SOURCE_TREE_ROUTED_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_NAMES",
        "SOURCE_TREE_ROUTED_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS",
        "SOURCE_TREE_LOCAL_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPEC_NAMES",
    ):
        assert not hasattr(support, constant_name)
        assert constant_name not in local_assignment_names


@pytest.mark.parametrize(
    ("contract_case",),
    tuple(
        pytest.param(contract_case, id=contract_case.case_id)
        for contract_case in (
            support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        )
    ),
)
def test_compiled_pattern_module_compile_contract_builder_surface_builds_expected_spec(
    contract_case: benchmark_test_support.CompiledPatternModuleCompileContractCase,
) -> None:
    excluded_fields = contract_case.manifest_excluded_fields()

    assert contract_case.contract_builder_spec() == benchmark_test_support._SourceTreeContractBuilderSpec(
        manifest_id="module-boundary",
        excluded_fields=excluded_fields,
        manifest_timed_samples=benchmark_test_support._SourceTreeContractBuilderSpec.__dataclass_fields__[
            "manifest_timed_samples"
        ].default,
        timing_scope="module-helper-call",
        notes=(contract_case.note(),),
    )


def test_compiled_pattern_module_compile_standard_definition_surface_moves_to_shared_support(
) -> None:
    definition_names, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            support
        )
    )
    shared_definition_names, shared_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            benchmark_test_support
        )
    )

    assert (
        "_build_compiled_pattern_module_compile_standard_benchmark_definitions"
        not in definition_names
    )
    assert (
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS"
        not in local_assignment_names
    )
    assert {
        "_build_compiled_pattern_module_compile_standard_benchmark_definitions",
    }.issubset(shared_definition_names)
    assert {
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
    }.issubset(shared_assignment_names)
    assert not hasattr(
        support,
        "_build_compiled_pattern_module_compile_standard_benchmark_definitions",
    )
    assert not hasattr(
        support,
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
    )
    assert hasattr(support, "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES")


def test_compiled_pattern_module_compile_standard_benchmark_definitions_are_shared_support_owned(
) -> None:
    expected_definitions = tuple(
        owner_spec.anchor_definition()
        for owner_spec in (
            *support._COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
            *support._COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
        )
    )

    first_export = getattr(
        benchmark_test_support,
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
    )
    second_export = getattr(
        benchmark_test_support,
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
    )

    assert first_export is second_export
    assert (
        benchmark_test_support._build_compiled_pattern_module_compile_standard_benchmark_definitions()
        == first_export
    )
    assert first_export == expected_definitions
    assert first_export is not expected_definitions
    assert tuple(definition.name for definition in first_export) == (
        "module-workflow-compiled-pattern-module-compile-literal-success",
        "module-workflow-compiled-pattern-module-compile-named-group-success",
        "module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword",
        "module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword-named-group",
        "module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword",
        "module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword-named-group",
        "module-workflow-compiled-pattern-module-compile-flags-ignorecase-keyword-rejection",
        "module-workflow-compiled-pattern-module-compile-flags-ignorecase-keyword-rejection-named-group",
    )
    assert (
        vars(benchmark_test_support)[
            "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS"
        ]
        is first_export
    )

    builder_definition = benchmark_test_support._module_function_definition(
        benchmark_test_support,
        "_build_compiled_pattern_module_compile_standard_benchmark_definitions",
    )
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "owner_spec"
        and node.func.attr == "anchor_definition"
        for node in ast.walk(builder_definition)
    )


@pytest.mark.parametrize(
    ("contract_manifest_id", "expected_note_fragment"),
    (
        pytest.param(
            "collection-replacement-boundary",
            "collection/replacement",
            id="collection-replacement-boundary",
        ),
        pytest.param(
            "module-boundary",
            "module-boundary",
            id="module-boundary",
        ),
    ),
)
def test_compiled_pattern_wrong_text_model_contract_specs_track_manifest_family(
    contract_manifest_id: str,
    expected_note_fragment: str,
) -> None:
    spec = support._COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS[
        contract_manifest_id
    ]

    assert spec == benchmark_test_support._SourceTreeContractBuilderSpec(
        manifest_id=contract_manifest_id,
        excluded_fields=(
            benchmark_test_support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
        ),
        manifest_timed_samples=benchmark_test_support._SourceTreeContractBuilderSpec.__dataclass_fields__[
            "manifest_timed_samples"
        ].default,
        timing_scope="module-helper-call",
        notes=spec.notes,
    )
    assert spec.notes
    assert expected_note_fragment in spec.notes[0]
    assert "wrong-text-model" in spec.notes[0]
    assert spec.notes[0].endswith("rows unresolved until helper invocation.")


@pytest.mark.parametrize(
    ("owner_spec",),
    tuple(
        pytest.param(owner_spec, id=owner_spec.case_id)
        for owner_spec in support._COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
    ),
)
def test_compiled_pattern_module_success_contract_builder_spec_uses_owner_metadata(
    owner_spec: object,
) -> None:
    spec = owner_spec.contract_builder_spec()

    assert spec == benchmark_test_support._SourceTreeContractBuilderSpec(
        manifest_id=owner_spec.contract_manifest_id,
        excluded_fields=(
            benchmark_test_support.COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS
        ),
        timing_scope="module-helper-call",
        notes=(
            "Ensures benchmark manifests keep the bounded "
            "compiled-pattern-first-argument successful "
            f"{owner_spec.note_surface} rows unresolved until helper invocation.",
        ),
    )
    assert (
        spec.manifest_timed_samples
        == benchmark_test_support._SourceTreeContractBuilderSpec.__dataclass_fields__[
            "manifest_timed_samples"
        ].default
    )


@pytest.mark.parametrize(
    ("spec", "expected_excluded_fields"),
    (
        pytest.param(
            collection_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC,
            benchmark_test_support.COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS,
            id="preserve-expected-exception",
        ),
        pytest.param(
            collection_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC,
            (
                benchmark_test_support.COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS
                | frozenset({"expected_exception"})
            ),
            id="drop-expected-exception",
        ),
    ),
)
def test_compiled_pattern_module_helper_keyword_contract_builder_spec_handles_exception_field(
    spec: benchmark_test_support._CompiledPatternModuleHelperKeywordContractSpec,
    expected_excluded_fields: frozenset[str],
) -> None:
    built_spec = spec.contract_builder_spec()

    assert built_spec == benchmark_test_support._SourceTreeContractBuilderSpec(
        manifest_id="collection-replacement-boundary",
        excluded_fields=expected_excluded_fields,
        manifest_timed_samples=spec.manifest_timed_samples,
        timing_scope="module-helper-call",
        notes=spec.notes,
    )


@pytest.mark.parametrize(
    ("owner_spec",),
    tuple(
        pytest.param(owner_spec, id=owner_spec.case_id)
        for owner_spec in support._COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
    ),
)
def test_compiled_pattern_module_success_owner_specs_pin_live_source_workload_ids(
    owner_spec: object,
) -> None:
    workload_ids = tuple(
        workload.workload_id
        for workload in owner_spec.source_workloads()
    )

    assert workload_ids == owner_spec.expected_source_workload_ids
    assert len(workload_ids) == len(set(workload_ids))


def test_compiled_pattern_module_success_owner_spec_surface_is_owned_locally() -> None:
    local_definition_names, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            support
        )
    )

    assert {
        "_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS",
    }.issubset(local_definition_names | local_assignment_names)


def test_compiled_pattern_module_success_source_workload_params_follow_owner_specs(
) -> None:
    expected_params = tuple(
        (
            owner_spec.case_id,
            source_workload.workload_id,
            f"{owner_spec.case_id}-{source_workload.workload_id}",
        )
        for owner_spec in support._COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
        for source_workload in owner_spec.source_workloads()
    )
    observed_params = tuple(
        (
            param.values[0].case_id,
            param.values[1].workload_id,
            param.id,
        )
        for param in support._COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS
    )

    assert observed_params == expected_params


def test_source_tree_support_module_exposes_source_tree_report_contract_helper_locally(
) -> None:
    module_ast = benchmark_test_support._parsed_module_ast(support)
    local_function_names = {
        node.name for node in module_ast.body if isinstance(node, ast.FunctionDef)
    }
    shared_module_ast = benchmark_test_support._parsed_module_ast(benchmark_test_support)
    shared_function_names = {
        node.name for node in shared_module_ast.body if isinstance(node, ast.FunctionDef)
    }

    still_shared_function_names = (
        "_assert_benchmark_summary_consistent",
        "_artifact_manifest_record",
        "assert_benchmark_manifest_contract",
        "find_manifest_record",
    )
    for function_name in still_shared_function_names:
        assert hasattr(benchmark_test_support, function_name)
        assert function_name in shared_function_names
        assert not hasattr(support, function_name)
        assert function_name not in local_function_names

    assert hasattr(support, "assert_source_tree_benchmark_contract")
    assert "assert_source_tree_benchmark_contract" in local_function_names
    assert not hasattr(benchmark_test_support, "assert_source_tree_benchmark_contract")
    assert "assert_source_tree_benchmark_contract" not in shared_function_names


def test_source_tree_support_module_exposes_moved_conditional_callable_helpers() -> None:
    source_tree_ast = benchmark_test_support._parsed_module_ast(support)
    source_tree_function_names = {
        node.name for node in source_tree_ast.body if isinstance(node, ast.FunctionDef)
    }
    _, source_tree_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(support)
    )
    collection_ast = benchmark_test_support._parsed_module_ast(collection_support)
    collection_function_names = {
        node.name for node in collection_ast.body if isinstance(node, ast.FunctionDef)
    }
    _, collection_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            collection_support
        )
    )

    for function_name in (
        "_conditional_group_exists_callable_str_slice_workloads",
        "_conditional_group_exists_callable_bytes_slice_workloads",
        "_conditional_group_exists_quantified_callable_str_workloads",
        "_conditional_group_exists_nested_callable_str_workloads",
        "_conditional_group_exists_nested_callable_bytes_workloads",
        "_conditional_group_exists_quantified_callable_bytes_workloads",
        "_conditional_group_exists_alternation_callable_bytes_workloads",
    ):
        assert not hasattr(support, function_name)
        assert function_name not in source_tree_function_names
        assert not hasattr(collection_support, function_name)
        assert function_name not in collection_function_names

    for assignment_name in (
        "_CONDITIONAL_GROUP_EXISTS_TEMPLATE_REPLACEMENT_EXPECTATION",
        "_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTED_SLICE_IDS",
        "_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS",
        "_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_ACTUAL_SLICE_IDS",
        "_CONDITIONAL_GROUP_EXISTS_ALTERNATION_CALLABLE_REPLACEMENT_EXPECTATION",
        "_CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_REPLACEMENT_EXPECTATION",
        "_CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION",
        "_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_REPLACEMENT_EXPECTATION",
        "_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION",
    ):
        assert not hasattr(support, assignment_name)
        assert assignment_name not in source_tree_assignment_names
        assert hasattr(collection_support, assignment_name)
        assert assignment_name in collection_assignment_names


def test_source_tree_support_module_exposes_routed_collection_owner_surface() -> None:
    _, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            support
        )
    )
    assert (
        "_is_collection_replacement_compiled_pattern_success_workload"
        not in local_assignment_names
    )

    collection_module_ast = benchmark_test_support._parsed_module_ast(collection_support)
    _, collection_local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            collection_support
        )
    )
    collection_function_names = {
        node.name for node in collection_module_ast.body if isinstance(node, ast.FunctionDef)
    }
    for function_name in (
        "_conditional_group_exists_callable_str_slice_workloads",
        "_conditional_group_exists_callable_bytes_slice_workloads",
        "_conditional_group_exists_quantified_callable_str_workloads",
        "_conditional_group_exists_nested_callable_str_workloads",
        "_conditional_group_exists_nested_callable_bytes_workloads",
        "_conditional_group_exists_quantified_callable_bytes_workloads",
        "_conditional_group_exists_alternation_callable_bytes_workloads",
    ):
        assert not hasattr(collection_support, function_name)
        assert function_name not in collection_function_names
    for assignment_name in (
        "_CONDITIONAL_GROUP_EXISTS_TEMPLATE_REPLACEMENT_EXPECTATION",
        "_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTED_SLICE_IDS",
        "_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS",
        "_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_ACTUAL_SLICE_IDS",
        "_CONDITIONAL_GROUP_EXISTS_ALTERNATION_CALLABLE_REPLACEMENT_EXPECTATION",
        "_CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_REPLACEMENT_EXPECTATION",
        "_CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION",
        "_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_REPLACEMENT_EXPECTATION",
        "_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION",
    ):
        assert hasattr(collection_support, assignment_name)
        assert assignment_name in collection_local_assignment_names
    assert hasattr(
        collection_support,
        "COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS",
    )
    assert (
        "COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS"
        in collection_local_assignment_names
    )
    assert not hasattr(
        support,
        "COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS",
    )
    assert hasattr(support, "SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS")
    assert "SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS" in local_assignment_names


def test_source_tree_support_module_no_longer_exposes_collection_owned_signature_helpers(
) -> None:
    source_tree_ast = benchmark_test_support._parsed_module_ast(support)
    local_function_names = {
        node.name for node in source_tree_ast.body if isinstance(node, ast.FunctionDef)
    }
    collection_ast = benchmark_test_support._parsed_module_ast(collection_support)
    collection_function_names = {
        node.name for node in collection_ast.body if isinstance(node, ast.FunctionDef)
    }

    for function_name in (
        "_text_model_agnostic_callable_match_group_signature",
        "_conditional_group_exists_nested_callable_correctness_case_signature",
        "_conditional_group_exists_nested_callable_workload_signature",
        "_conditional_group_exists_quantified_callable_correctness_case_signature",
        "_conditional_group_exists_quantified_callable_workload_signature",
    ):
        assert not hasattr(support, function_name)
        assert function_name not in local_function_names
        assert hasattr(collection_support, function_name)
        assert function_name in collection_function_names


def test_source_tree_support_module_exports_combined_slice_owner_group() -> None:
    _, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            support
        )
    )
    assert "SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS" in local_assignment_names
    assert "SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS" in local_assignment_names

    _, collection_local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            collection_support
        )
    )
    assert hasattr(
        collection_support,
        "COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS",
    )
    assert (
        "COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS"
        in collection_local_assignment_names
    )


def test_combined_suite_no_longer_defines_moved_source_tree_case_surface_locally() -> None:
    module_ast = benchmark_test_support._parsed_module_ast(
        support._source_tree_combined_suite()
    )
    local_class_names = {
        node.name for node in module_ast.body if isinstance(node, ast.ClassDef)
    }
    local_function_names = {
        node.name for node in module_ast.body if isinstance(node, ast.FunctionDef)
    }

    for class_name in (
        "_SourceTreeContractBuilderSpec",
        "SourceTreeBenchmarkCommonCase",
        "SourceTreeManifestExpectation",
        "SourceTreeDeferredExpectation",
        "SourceTreeScorecardCase",
        "SourceTreeCombinedCase",
        "SourceTreeCombinedPatternGroupExpectation",
        "SourceTreeCombinedManifestShapeExpectation",
        "SourceTreeCombinedFullyMeasuredManifestExpectation",
        "SourceTreeCombinedManifestExpectationDefinition",
        "SourceTreeCombinedSliceExpectation",
    ):
        assert class_name not in local_class_names
    for function_name in (
        "_source_tree_contract_manifest",
        "_source_tree_contract_workload",
        "source_tree_scorecard_case",
        "source_tree_combined_target_manifest_ids",
        "source_tree_combined_manifest_representative_measured_workload_ids",
        "source_tree_combined_case",
        "expected_summary_for_manifests",
        "select_source_tree_combined_slice_rows",
        "_combined_suite_slice_expectations",
        "_combined_manifest_representative_measured_workload_ids",
    ):
        assert function_name not in local_function_names


def test_combined_suite_class_no_longer_defines_zero_gap_representative_wrappers(
) -> None:
    combined_suite_class = next(
        node
        for node in benchmark_test_support._parsed_module_ast(
            support._source_tree_combined_suite()
        ).body
        if isinstance(node, ast.ClassDef)
        and node.name == "SourceTreeCombinedBoundaryBenchmarkSuiteTest"
    )
    class_method_names = {
        node.name
        for node in combined_suite_class.body
        if isinstance(node, ast.FunctionDef)
    }

    assert "_assert_zero_gap_bytes_representative_subset" not in class_method_names
    assert (
        "_assert_zero_gap_manifest_representative_promotion"
        not in class_method_names
    )
    assert "_assert_source_tree_combined_manifest_slice" not in class_method_names
    assert "_assert_source_tree_combined_pattern_group" not in class_method_names


def test_combined_suite_class_no_longer_defines_scorecard_contract_wrappers() -> None:
    combined_suite_class = next(
        node
        for node in benchmark_test_support._parsed_module_ast(
            support._source_tree_combined_suite()
        ).body
        if isinstance(node, ast.ClassDef) and node.name == "SourceTreeScorecardBenchmarkSuiteTest"
    )
    class_method_names = {
        node.name
        for node in combined_suite_class.body
        if isinstance(node, ast.FunctionDef)
    }

    assert "_assert_manifest_contracts" not in class_method_names
    assert (
        "_assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation"
        not in class_method_names
    )
    assert "_assert_zero_gap_representative_workload_subset" not in class_method_names
    assert "_assert_representative_workloads" not in class_method_names
    assert "_assert_workloads" not in class_method_names


def test_source_tree_support_module_does_not_export_deleted_fully_measured_helpers(
) -> None:
    assert not hasattr(
        support, "source_tree_combined_fully_measured_manifest_ids"
    )
    assert not hasattr(
        support, "source_tree_combined_fully_measured_manifest_expectation"
    )


def test_combined_suite_no_longer_routes_deleted_wrapper_helpers_through_source_tree_support(
) -> None:
    module_ast = benchmark_test_support._parsed_module_ast(
        support._source_tree_combined_suite()
    )
    deleted_wrapper_names = frozenset(
        {
            "assert_zero_gap_bytes_representative_subset",
            "assert_zero_gap_manifest_representative_promotion",
            "relative_manifest_path",
            "source_tree_scorecard_case_ids",
            "source_tree_combined_fully_measured_manifest_ids",
            "source_tree_combined_fully_measured_manifest_expectation",
        }
    )
    source_tree_support_alias_names = benchmark_test_support._module_alias_names(
        module_ast,
        import_from_module="tests.benchmarks",
        import_name="source_tree_benchmark_anchor_support",
        dotted_import_name="tests.benchmarks.source_tree_benchmark_anchor_support",
    )

    assert benchmark_test_support._top_level_import_from_alias_pairs(
        module_ast,
        module_name="tests.benchmarks.source_tree_benchmark_anchor_support",
        imported_names=deleted_wrapper_names,
    ) == frozenset()
    assert frozenset(
        node.attr
        for node in ast.walk(module_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in source_tree_support_alias_names
        and node.attr in deleted_wrapper_names
    ) == frozenset()


def test_combined_suite_no_longer_binds_moved_source_tree_constants_locally(
) -> None:
    combined_suite_ast = benchmark_test_support._parsed_module_ast(
        support._source_tree_combined_suite()
    )
    moved_constant_names = frozenset(
        {
            "SOURCE_TREE_SCORECARD_EXPECTATIONS",
            "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
            "SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS",
        }
    )
    direct_import_names = {
        alias.name
        for node in combined_suite_ast.body
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    local_assignment_names = {
        target.id
        for node in combined_suite_ast.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    } | {
        node.target.id
        for node in combined_suite_ast.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
    }
    local_constant_alias_names = {
        target.id
        for node in combined_suite_ast.body
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Attribute)
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "source_tree_support"
        and node.value.attr in moved_constant_names
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    local_name_loads = {
        node.id
        for node in ast.walk(combined_suite_ast)
        if isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
        and node.id in moved_constant_names
    }

    for constant_name in moved_constant_names:
        assert constant_name not in direct_import_names
        assert constant_name not in local_assignment_names
        assert constant_name not in local_name_loads
    assert local_constant_alias_names == set()


def test_combined_suite_no_longer_binds_centralized_source_tree_manifest_paths_locally(
) -> None:
    combined_suite_ast = benchmark_test_support._parsed_module_ast(
        support._source_tree_combined_suite()
    )
    centralized_manifest_path_names = frozenset(
        {
            "OPTIONAL_GROUP_MANIFEST_PATH",
            "NESTED_GROUP_MANIFEST_PATH",
            "EXACT_REPEAT_MANIFEST_PATH",
            "RANGED_REPEAT_MANIFEST_PATH",
            "GROUPED_ALTERNATION_MANIFEST_PATH",
            "GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH",
            "NESTED_GROUP_REPLACEMENT_MANIFEST_PATH",
            "OPEN_ENDED_MANIFEST_PATH",
        }
    )
    direct_import_names = {
        alias.name
        for node in combined_suite_ast.body
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    local_assignment_names = {
        target.id
        for node in combined_suite_ast.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    } | {
        node.target.id
        for node in combined_suite_ast.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
    }
    local_constant_alias_names: set[str] = set()
    for node in combined_suite_ast.body:
        if isinstance(node, ast.Assign):
            targets = tuple(
                target.id for target in node.targets if isinstance(target, ast.Name)
            )
            value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = (node.target.id,)
            value = node.value
        else:
            continue

        if isinstance(value, ast.Name):
            if value.id in centralized_manifest_path_names:
                local_constant_alias_names.update(targets)
            continue

        if (
            isinstance(value, ast.Attribute)
            and isinstance(value.value, ast.Name)
            and value.value.id
            in {
                "compiled_pattern_module_helper_support",
                "source_tree_support",
            }
            and value.attr in centralized_manifest_path_names
        ):
            local_constant_alias_names.update(targets)

    local_name_loads = {
        node.id
        for node in ast.walk(combined_suite_ast)
        if isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
        and node.id in centralized_manifest_path_names
    }
    direct_compiled_pattern_contract_refs = {
        node.attr
        for node in ast.walk(combined_suite_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "source_tree_owner_support"
        and node.attr
        in {
            "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
            "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES",
            "_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS",
            "_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS",
            "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS",
        }
    }

    for constant_name in centralized_manifest_path_names:
        assert constant_name not in direct_import_names
        assert constant_name not in local_assignment_names
        assert constant_name not in local_name_loads
    assert local_constant_alias_names == set()
    assert direct_compiled_pattern_contract_refs == {
        "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
        "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES",
        "_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS",
    }


def test_combined_suite_no_longer_defines_moved_report_contract_helpers_locally() -> None:
    module_ast = benchmark_test_support._parsed_module_ast(
        support._source_tree_combined_suite()
    )
    local_function_names = {
        node.name for node in module_ast.body if isinstance(node, ast.FunctionDef)
    }

    for function_name in (
        "_assert_benchmark_summary_consistent",
        "_artifact_manifest_record",
        "assert_benchmark_manifest_contract",
        "find_manifest_record",
    ):
        assert function_name not in local_function_names


def test_combined_suite_no_longer_defines_moved_conditional_callable_helpers_locally(
) -> None:
    module_ast = benchmark_test_support._parsed_module_ast(
        support._source_tree_combined_suite()
    )
    local_function_names = {
        node.name for node in module_ast.body if isinstance(node, ast.FunctionDef)
    }

    for function_name in (
        "_conditional_group_exists_callable_str_slice_workloads",
        "_conditional_group_exists_callable_bytes_slice_workloads",
        "_conditional_group_exists_quantified_callable_str_workloads",
        "_conditional_group_exists_nested_callable_str_workloads",
        "_conditional_group_exists_nested_callable_bytes_workloads",
        "_conditional_group_exists_quantified_callable_bytes_workloads",
        "_conditional_group_exists_alternation_callable_bytes_workloads",
    ):
        assert function_name not in local_function_names


def test_combined_suite_imports_source_tree_support_through_owner_module_only() -> None:
    combined_suite_ast = benchmark_test_support._parsed_module_ast(
        support._source_tree_combined_suite()
    )
    direct_owner_imports = [
        node
        for node in combined_suite_ast.body
        if isinstance(node, ast.ImportFrom)
        and node.module == "tests.benchmarks.source_tree_benchmark_anchor_support"
    ]
    owner_module_imports = [
        alias
        for node in combined_suite_ast.body
        if isinstance(node, ast.ImportFrom) and node.module == "tests.benchmarks"
        for alias in node.names
    ]
    local_assignment_names = {
        target.id
        for node in combined_suite_ast.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }

    assert direct_owner_imports == []
    assert any(
        alias.name == "source_tree_benchmark_anchor_support"
        and alias.asname == "source_tree_owner_support"
        for alias in owner_module_imports
    )
    assert "source_tree_support" in local_assignment_names


def test_combined_suite_imports_and_reads_collection_owner_surface_through_package_alias(
) -> None:
    combined_suite_ast = benchmark_test_support._parsed_module_ast(
        support._source_tree_combined_suite()
    )
    package_collection_imports = [
        (alias.name, alias.asname)
        for node in combined_suite_ast.body
        if isinstance(node, ast.ImportFrom) and node.module == "tests.benchmarks"
        for alias in node.names
        if alias.name == "collection_replacement_benchmark_anchor_support"
    ]
    direct_collection_owner_imports = [
        node
        for node in combined_suite_ast.body
        if isinstance(node, ast.ImportFrom)
        and node.module
        == "tests.benchmarks.collection_replacement_benchmark_anchor_support"
    ]
    direct_collection_attribute_reads = {
        node.attr
        for node in ast.walk(combined_suite_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "collection_replacement_support"
    }

    assert package_collection_imports == [
        (
            "collection_replacement_benchmark_anchor_support",
            "collection_replacement_support",
        )
    ]
    assert direct_collection_owner_imports == []
    assert direct_collection_attribute_reads
    assert (
        "COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS"
        not in direct_collection_attribute_reads
    )


def test_source_tree_support_defines_combined_route_helpers_locally() -> None:
    module_ast = benchmark_test_support._parsed_module_ast(support)
    local_function_names = {
        node.name for node in module_ast.body if isinstance(node, ast.FunctionDef)
    }
    _, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            support
        )
    )

    moved_helper_names = {
        "_source_tree_combined_suite",
        "_assert_source_tree_combined_routes_owner_names_through_module_alias",
        "source_tree_combined_manifest_representative_measured_workload_ids",
    }

    assert moved_helper_names.issubset(local_function_names)
    for helper_name in moved_helper_names:
        assert hasattr(support, helper_name)
    assert "SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS" in local_assignment_names


@pytest.mark.parametrize(
    (
        "module_source",
        "import_name",
        "dotted_import_name",
        "expected_alias_names",
    ),
    (
        pytest.param(
            """
from tests.benchmarks import benchmark_test_support as benchmark_support

benchmark_support_alias = benchmark_support
benchmark_support_final: object = benchmark_support_alias
""",
            "benchmark_test_support",
            "tests.benchmarks.benchmark_test_support",
            {
                "benchmark_support",
                "benchmark_support_alias",
                "benchmark_support_final",
            },
            id="benchmark-test-support",
        ),
        pytest.param(
            """
from tests.benchmarks import source_tree_benchmark_anchor_support as source_tree_support

source_tree_support_alias = source_tree_support
source_tree_support_final: object = source_tree_support_alias
""",
            "source_tree_benchmark_anchor_support",
            "tests.benchmarks.source_tree_benchmark_anchor_support",
            {
                "source_tree_support",
                "source_tree_support_alias",
                "source_tree_support_final",
            },
            id="source-tree-support",
        ),
    ),
)
def test_module_alias_names_follow_import_and_assignment_alias_chains(
    module_source: str,
    import_name: str,
    dotted_import_name: str,
    expected_alias_names: set[str],
) -> None:
    assert benchmark_test_support._module_alias_names(
        ast.parse(module_source),
        import_from_module="tests.benchmarks",
        import_name=import_name,
        dotted_import_name=dotted_import_name,
    ) == expected_alias_names


@pytest.mark.parametrize(
    (
        "alias_name",
        "owner_module",
        "routed_names",
        "expected_direct_benchmark_test_support_refs",
    ),
    [
        pytest.param(
            "source_tree_support",
            support,
            (
                "_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS",
                "_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS",
                "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
                "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS",
                "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES",
            ),
            frozenset(),
            id="compiled-pattern-module-compile",
        ),
        pytest.param(
            "source_tree_support",
            support,
            (
                "SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS",
                "source_tree_combined_manifest_representative_measured_workload_ids",
            ),
            frozenset(),
            id="source-tree-combined-route-helpers",
        ),
        pytest.param(
            "source_tree_support",
            support,
            (),
            frozenset(),
            id="compiled-pattern-wrong-text-model",
        ),
        pytest.param(
            "source_tree_support",
            support,
            ("assert_source_tree_benchmark_contract",),
            frozenset(),
            id="source-tree-report-contract-helper",
        ),
        pytest.param(
            "collection_replacement_support",
            collection_support,
            (
                "_CONDITIONAL_GROUP_EXISTS_TEMPLATE_REPLACEMENT_EXPECTATION",
                "_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTED_SLICE_IDS",
                "_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS",
                "_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_ACTUAL_SLICE_IDS",
                "_CONDITIONAL_GROUP_EXISTS_ALTERNATION_CALLABLE_REPLACEMENT_EXPECTATION",
                "_CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_REPLACEMENT_EXPECTATION",
                "_CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION",
                "_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_REPLACEMENT_EXPECTATION",
                "_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION",
            ),
            frozenset(),
            id="conditional-callable-helpers",
        ),
        pytest.param(
            "collection_replacement_support",
            collection_support,
            (
                "_text_model_agnostic_callable_match_group_signature",
                "_conditional_group_exists_nested_callable_correctness_case_signature",
                "_conditional_group_exists_nested_callable_workload_signature",
                "_conditional_group_exists_quantified_callable_correctness_case_signature",
                "_conditional_group_exists_quantified_callable_workload_signature",
            ),
            frozenset(),
            id="conditional-callable-signature-helpers",
        ),
        pytest.param(
            "collection_replacement_support",
            collection_support,
            (
                "COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS",
            ),
            frozenset(),
            id="collection-owner-combined-slice-owner-names",
        ),
    ],
)
def test_combined_suite_routes_moved_support_surfaces_through_benchmark_test_support(
    alias_name: str,
    owner_module: object,
    routed_names: tuple[str, ...],
    expected_direct_benchmark_test_support_refs: frozenset[str],
) -> None:
    support._assert_source_tree_combined_routes_owner_names_through_module_alias(
        alias_name=alias_name,
        owner_module=owner_module,
        owner_names=routed_names,
        expected_direct_benchmark_test_support_refs=(
            expected_direct_benchmark_test_support_refs
        ),
    )


def test_combined_suite_imports_remaining_report_contract_helpers_through_benchmark_test_support(
) -> None:
    module_ast = benchmark_test_support._parsed_module_ast(
        support._source_tree_combined_suite()
    )
    benchmark_support_alias_names = benchmark_test_support._module_alias_names(
        module_ast,
        import_from_module="tests.benchmarks",
        import_name="benchmark_test_support",
        dotted_import_name="tests.benchmarks.benchmark_test_support",
    )
    helper_names = frozenset(
        {
            "assert_benchmark_manifest_contract",
            "find_manifest_record",
        }
    )

    assert benchmark_support_alias_names
    assert benchmark_test_support._top_level_import_from_alias_pairs(
        module_ast,
        module_name="tests.benchmarks.benchmark_test_support",
        imported_names=helper_names,
    ) == frozenset()
    assert frozenset(
        (target_name, attribute_name)
        for target_name, attribute_name in benchmark_test_support._module_attribute_alias_targets(
            module_ast,
            module_alias_names=benchmark_support_alias_names,
        ).items()
        if attribute_name in helper_names
    ) == frozenset()
    assert frozenset(
        node.attr
        for node in ast.walk(module_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in benchmark_support_alias_names
        and node.attr in helper_names
    ) == helper_names


def test_combined_suite_imports_compiled_pattern_module_helper_keyword_surface_through_collection_support(
) -> None:
    module_ast = benchmark_test_support._parsed_module_ast(
        support._source_tree_combined_suite()
    )
    owner_names = frozenset(
        {
            "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS",
            "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC",
            "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
            "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC",
            "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
            "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS",
            "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
            "_is_collection_replacement_compiled_pattern_keyword_error_workload",
        }
    )
    benchmark_support_alias_names = benchmark_test_support._module_alias_names(
        module_ast,
        import_from_module="tests.benchmarks",
        import_name="benchmark_test_support",
        dotted_import_name="tests.benchmarks.benchmark_test_support",
    )
    collection_support_alias_names = benchmark_test_support._module_alias_names(
        module_ast,
        import_from_module="tests.benchmarks",
        import_name="collection_replacement_benchmark_anchor_support",
        dotted_import_name="tests.benchmarks.collection_replacement_benchmark_anchor_support",
    )
    source_tree_support_alias_names = benchmark_test_support._module_alias_names(
        module_ast,
        import_from_module="tests.benchmarks",
        import_name="source_tree_benchmark_anchor_support",
        dotted_import_name="tests.benchmarks.source_tree_benchmark_anchor_support",
    )

    assert benchmark_support_alias_names
    assert collection_support_alias_names
    assert benchmark_test_support._top_level_import_from_alias_pairs(
        module_ast,
        module_name="tests.benchmarks.benchmark_test_support",
        imported_names=owner_names,
    ) == frozenset()
    assert benchmark_test_support._top_level_import_from_alias_pairs(
        module_ast,
        module_name="tests.benchmarks.collection_replacement_benchmark_anchor_support",
        imported_names=owner_names,
    ) == frozenset()
    assert frozenset(
        (target_name, attribute_name)
        for target_name, attribute_name in benchmark_test_support._module_attribute_alias_targets(
            module_ast,
            module_alias_names=benchmark_support_alias_names,
        ).items()
        if attribute_name in owner_names
    ) == frozenset()
    assert frozenset(
        (target_name, attribute_name)
        for target_name, attribute_name in benchmark_test_support._module_attribute_alias_targets(
            module_ast,
            module_alias_names=collection_support_alias_names,
        ).items()
        if attribute_name in owner_names
    ) == frozenset()
    assert frozenset(
        node.attr
        for node in ast.walk(module_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in benchmark_support_alias_names
        and node.attr in owner_names
    ) == frozenset()
    assert frozenset(
        node.attr
        for node in ast.walk(module_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in collection_support_alias_names
        and node.attr in owner_names
    ) == owner_names
    assert frozenset(
        node.attr
        for node in ast.walk(module_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in source_tree_support_alias_names
        and node.attr in owner_names
    ) == frozenset()


def test_source_tree_combined_slice_expectations_keep_collection_owned_block_out_of_source_tree_owner_inventory(
) -> None:
    source_tree_combined_slice_ids = {
        expectation.slice_id
        for expectation in support.SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS
    }
    combined_suite_slice_ids = {
        expectation.slice_id
        for expectation in support.SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS
    }
    collection_owned_slice_ids = {
        expectation.slice_id
        for expectation in (
            collection_support.COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
        )
    }

    assert collection_owned_slice_ids
    assert source_tree_combined_slice_ids.isdisjoint(collection_owned_slice_ids)
    assert collection_owned_slice_ids.issubset(combined_suite_slice_ids)
    assert "former-gap-callable-replacement-rows" in source_tree_combined_slice_ids
    assert "former-gap-callable-replacement-rows" in combined_suite_slice_ids
    assert "minimal-template-replacement-rows" not in source_tree_combined_slice_ids
    assert "minimal-template-replacement-rows" in combined_suite_slice_ids
    assert "nested-callable-replacement-str-rows" not in source_tree_combined_slice_ids
    assert "nested-callable-replacement-str-rows" in combined_suite_slice_ids


def test_source_tree_owner_inventory_constants_are_not_mirrored_back_into_this_test_module(
) -> None:
    module = importlib.import_module(__name__)
    module_ast = benchmark_test_support._parsed_module_ast(module)
    local_definition_names, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            module
        )
    )
    legacy_local_mirror_names = frozenset(
        {
            "_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_LOCAL_FUNCTION_NAMES",
            "_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_ASSIGNMENT_NAMES",
            "_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_DEFINITION_NAMES",
        }
    )
    assert legacy_local_mirror_names.isdisjoint(
        local_definition_names | local_assignment_names
    )


def test_moved_conditional_callable_expectation_helpers_pin_current_slice_ids() -> None:
    expected_callable_slice_ids = (
        "minimal-callable-replacement-rows",
        "minimal-callable-replacement-exception-rows",
        "minimal-callable-replacement-none-count-exception-rows",
        "alternation-heavy-callable-replacement-rows",
    )
    callable_expectations = (
        collection_support._CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
    )

    assert (
        collection_support._CONDITIONAL_GROUP_EXISTS_TEMPLATE_REPLACEMENT_EXPECTATION.slice_id
        == "minimal-template-replacement-rows"
    )
    assert tuple(
        expectation.slice_id for expectation in callable_expectations
    ) == expected_callable_slice_ids
    assert {
        expectation.manifest_id for expectation in callable_expectations
    } == {"conditional-group-exists-boundary"}
    assert (
        collection_support._CONDITIONAL_GROUP_EXISTS_ALTERNATION_CALLABLE_REPLACEMENT_EXPECTATION.slice_id
        == "alternation-heavy-callable-replacement-rows"
    )
    assert (
        collection_support._CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_REPLACEMENT_EXPECTATION.slice_id
        == "nested-callable-replacement-str-rows"
    )
    assert (
        collection_support._CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION.slice_id
        == "nested-callable-replacement-bytes-rows"
    )
    assert (
        collection_support._CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_REPLACEMENT_EXPECTATION.slice_id
        == "quantified-callable-replacement-str-rows"
    )
    assert (
        collection_support._CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION.slice_id
        == "quantified-callable-replacement-bytes-rows"
    )


def test_moved_conditional_callable_workload_loaders_pin_expected_ids() -> None:
    callable_expectations = (
        collection_support._CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
    )
    expected_callable_workload_ids = tuple(
        workload_id
        for expectation in callable_expectations
        for workload_id in expectation.expected_workload_ids
    )
    expected_callable_str_workload_ids = tuple(
        workload_id
        for workload_id in expected_callable_workload_ids
        if not workload_id.endswith("-bytes")
    )
    expected_callable_bytes_workload_ids = tuple(
        workload_id
        for workload_id in expected_callable_workload_ids
        if workload_id.endswith("-bytes")
    )
    manifest_path = (
        benchmarks.BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py"
    )
    callable_str_workloads = benchmark_test_support.live_manifest_workloads(
        manifest_path,
        expected_callable_str_workload_ids,
    )
    callable_bytes_workloads = benchmark_test_support.live_manifest_workloads(
        manifest_path,
        expected_callable_bytes_workload_ids,
    )
    nested_str_workloads = benchmark_test_support.live_manifest_workloads(
        manifest_path,
        collection_support.CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS,
    )
    nested_bytes_workloads = benchmark_test_support.live_manifest_workloads(
        manifest_path,
        collection_support.CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS,
    )
    quantified_str_workloads = benchmark_test_support.live_manifest_workloads(
        manifest_path,
        collection_support.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
    )
    quantified_bytes_workloads = benchmark_test_support.live_manifest_workloads(
        manifest_path,
        collection_support.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
    )
    alternation_bytes_workloads = benchmark_test_support.live_manifest_workloads(
        manifest_path,
        collection_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS,
    )

    assert tuple(
        workload.workload_id for workload in callable_str_workloads
    ) == expected_callable_str_workload_ids
    assert {workload.text_model for workload in callable_str_workloads} == {"str"}
    assert tuple(
        workload.workload_id for workload in callable_bytes_workloads
    ) == expected_callable_bytes_workload_ids
    assert {workload.text_model for workload in callable_bytes_workloads} == {
        "bytes"
    }
    assert tuple(
        workload.workload_id for workload in nested_str_workloads
    ) == collection_support.CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
    assert {workload.text_model for workload in nested_str_workloads} == {"str"}
    assert tuple(
        workload.workload_id for workload in nested_bytes_workloads
    ) == collection_support.CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
    assert {workload.text_model for workload in nested_bytes_workloads} == {"bytes"}
    assert tuple(
        workload.workload_id for workload in quantified_str_workloads
    ) == (
        collection_support.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
    )
    assert {workload.text_model for workload in quantified_str_workloads} == {
        "str"
    }
    assert tuple(
        workload.workload_id for workload in quantified_bytes_workloads
    ) == (
        collection_support.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
    )
    assert {workload.text_model for workload in quantified_bytes_workloads} == {
        "bytes"
    }
    assert tuple(
        workload.workload_id for workload in alternation_bytes_workloads
    ) == (
        collection_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS
    )
    assert {workload.text_model for workload in alternation_bytes_workloads} == {
        "bytes"
    }


def test_moved_conditional_callable_selector_helpers_keep_partition_rules() -> None:
    expected_callable_workload_ids = tuple(
        workload_id
        for expectation in collection_support._CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
        for workload_id in expectation.expected_workload_ids
    )
    synthetic_workloads = (
        benchmark_test_support.synthetic_workload(
            manifest_id="conditional-group-exists-boundary",
            workload_id="callable-negative-count-warm-str",
            operation="module.sub",
            text_model="str",
            categories=["callable", "negative-count", "replacement"],
        ),
        benchmark_test_support.synthetic_workload(
            manifest_id="conditional-group-exists-boundary",
            workload_id="callable-negative-count-warm-bytes",
            operation="module.sub",
            text_model="bytes",
            categories=["callable", "negative-count", "replacement"],
        ),
        benchmark_test_support.synthetic_workload(
            manifest_id="conditional-group-exists-boundary",
            workload_id="callable-negative-none-count-warm-str",
            operation="module.sub",
            text_model="str",
            categories=["callable", "negative-count", "none-count", "replacement"],
        ),
        benchmark_test_support.synthetic_workload(
            manifest_id="conditional-group-exists-boundary",
            workload_id="callable-no-match-warm-str",
            operation="module.sub",
            text_model="str",
            categories=["callable", "no-match", "replacement"],
        ),
    )

    expected_callable_str_workload_ids = tuple(
        workload_id
        for workload_id in expected_callable_workload_ids
        if not workload_id.endswith("-bytes")
    )
    expected_callable_bytes_workload_ids = tuple(
        workload_id
        for workload_id in expected_callable_workload_ids
        if workload_id.endswith("-bytes")
    )
    assert len(expected_callable_workload_ids) == (
        len(expected_callable_str_workload_ids)
        + len(expected_callable_bytes_workload_ids)
    )
    assert all(
        not workload_id.endswith("-bytes")
        for workload_id in expected_callable_str_workload_ids
    )
    assert all(
        workload_id.endswith("-bytes")
        for workload_id in expected_callable_bytes_workload_ids
    )
    assert set(expected_callable_workload_ids) == (
        set(expected_callable_str_workload_ids)
        | set(expected_callable_bytes_workload_ids)
    )
    assert tuple(
        f"{workload_id.removesuffix('-str')}-bytes"
        for workload_id in (
            collection_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
        )
    ) == (
        collection_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS
    )
    assert tuple(
        workload.workload_id
        for workload in synthetic_workloads
        if workload.text_model == "str"
        and "negative-count" in workload.categories
    ) == (
        "callable-negative-count-warm-str",
        "callable-negative-none-count-warm-str",
    )
    assert tuple(
        workload.workload_id
        for workload in synthetic_workloads
        if workload.text_model == "str"
        and "negative-count" in workload.categories
        and "none-count" not in workload.categories
    ) == ("callable-negative-count-warm-str",)
    assert tuple(
        workload.workload_id
        for workload in synthetic_workloads
        if workload.text_model == "bytes"
        and "negative-count" in workload.categories
    ) == ("callable-negative-count-warm-bytes",)
    assert tuple(
        workload.workload_id
        for workload in synthetic_workloads
        if workload.text_model == "str"
        and "no-match" in workload.categories
    ) == ("callable-no-match-warm-str",)


def test_nested_conditional_callable_live_signatures_cover_exception_and_no_match_bytes_routes(
) -> None:
    cases = benchmark_test_support.published_cases_by_id()

    absent_case = cases[
        "pattern-subn-callable-named-conditional-group-exists-nested-absent-bytes"
    ]
    absent_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH,
        "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
    )
    absent_signature = (
        "pattern.subn",
        b"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
        ("callable_match_group", "word", b"", b"x"),
        (b"zzacfzz", 1),
        True,
        False,
        0,
        "bytes",
    )

    assert (
        collection_support._conditional_group_exists_nested_callable_correctness_case_signature(
            absent_case
        )
        == absent_signature
    )
    assert (
        collection_support._conditional_group_exists_nested_callable_workload_signature(
            absent_workload
        )
        == absent_signature
    )

    no_match_case = cases[
        "module-sub-callable-conditional-group-exists-nested-near-miss-present-bytes"
    ]
    no_match_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH,
        "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
    )
    no_match_signature = (
        "module.sub",
        b"a(b)?c(?(1)(?(1)d|e)|f)",
        ("callable_match_group", 1, b"", b"x"),
        (b"zzabcezz",),
        False,
        True,
        0,
        "bytes",
    )

    assert (
        collection_support._conditional_group_exists_nested_callable_correctness_case_signature(
            no_match_case
        )
        == no_match_signature
    )
    assert (
        collection_support._conditional_group_exists_nested_callable_workload_signature(
            no_match_workload
        )
        == no_match_signature
    )


def test_quantified_conditional_callable_live_signatures_cover_none_count_and_no_match_routes(
) -> None:
    cases = benchmark_test_support.published_cases_by_id()

    none_count_case = cases[
        "module-sub-callable-conditional-group-exists-quantified-none-count-present-str"
    ]
    none_count_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH,
        "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-warm-str",
    )
    none_count_signature = (
        "module.sub",
        "a(b)?c(?(1)d|e){2}",
        ("callable_match_group", 1, "", "x"),
        ("zzabcddzz",),
        True,
        False,
        0,
        "str",
    )

    assert (
        collection_support._conditional_group_exists_quantified_callable_correctness_case_signature(
            none_count_case
        )
        == none_count_signature
    )
    assert (
        collection_support._conditional_group_exists_quantified_callable_workload_signature(
            none_count_workload
        )
        == none_count_signature
    )

    no_match_case = cases[
        "pattern-subn-callable-named-conditional-group-exists-quantified-near-miss-absent-bytes"
    ]
    no_match_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH,
        "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
    )
    no_match_signature = (
        "pattern.subn",
        b"a(?P<word>b)?c(?(word)d|e){2}",
        ("callable_match_group", "word", b"", b"x"),
        (b"zzacedzz", 1),
        False,
        True,
        0,
        "bytes",
    )

    assert (
        collection_support._conditional_group_exists_quantified_callable_correctness_case_signature(
            no_match_case
        )
        == no_match_signature
    )
    assert (
        collection_support._conditional_group_exists_quantified_callable_workload_signature(
            no_match_workload
        )
        == no_match_signature
    )


def test_benchmark_summary_consistent_counts_unimplemented_and_regression_rows() -> None:
    scorecard = _synthetic_report_scorecard(
        workloads=(
            {
                "id": "parser-cold-gap",
                "manifest_id": "synthetic-boundary",
                "family": "parser",
                "cache_mode": "cold",
                "status": "known-gap",
            },
            {
                "id": "module-warm-measured",
                "manifest_id": "synthetic-boundary",
                "family": "module",
                "cache_mode": "warm",
                "status": "measured",
            },
            {
                "id": "regression-purged-unimplemented",
                "manifest_id": "regression-matrix",
                "family": "regression",
                "cache_mode": "purged",
                "status": "unimplemented",
            },
        ),
        artifacts={
            "selection_mode": "full",
            "raw_samples": None,
            "manifests": [],
            "manifest": None,
            "manifest_id": "combined-benchmark-suite",
            "manifest_schema_version": 1,
        },
        baseline={
            "python": "synthetic",
            "version_family": "3.12.x",
            "re_module": "re",
        },
    )

    benchmark_test_support._assert_benchmark_summary_consistent(
        unittest.TestCase(),
        scorecard,
        _summary_view(scorecard),
    )


def test_source_tree_report_contract_accepts_single_manifest_native_loaded_scorecard(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
) -> None:
    monkeypatch.setattr(
        benchmark_test_support,
        "build_cpython_baseline",
        lambda version_family: {
            "python": "synthetic",
            "version_family": version_family,
        },
    )
    manifest_path = "benchmarks/workloads/synthetic_boundary.py"
    workloads = (
        SimpleNamespace(
            workload_id="module-search-synthetic-warm-str",
            operation="module.search",
            family="module",
        ),
        SimpleNamespace(
            workload_id="module-compile-synthetic-cold-gap",
            operation="module.compile",
            family="parser",
        ),
    )
    workload_by_id = {workload.workload_id: workload for workload in workloads}
    manifest = SimpleNamespace(
        manifest_id="synthetic-boundary",
        schema_version=7,
        workloads=workloads,
        smoke_workload_ids=lambda: ("module-search-synthetic-warm-str",),
        spec_refs=("docs/spec/synthetic-boundary.md",),
        notes=None,
        selected_workloads=lambda selected_workload_ids=None: (
            workloads
            if selected_workload_ids is None
            else tuple(workload_by_id[workload_id] for workload_id in selected_workload_ids)
        ),
    )
    manifest_record = benchmark_test_support._artifact_manifest_record(
        manifest_path,
        manifest,
    )
    scorecard = _synthetic_report_scorecard(
        workloads=(
            {
                "id": "module-search-synthetic-warm-str",
                "manifest_id": manifest.manifest_id,
                "family": "module",
                "cache_mode": "warm",
                "status": "measured",
            },
            {
                "id": "module-compile-synthetic-cold-gap",
                "manifest_id": manifest.manifest_id,
                "family": "parser",
                "cache_mode": "cold",
                "status": "known-gap",
            },
        ),
        artifacts={
            "selection_mode": "full",
            "raw_samples": None,
            "manifests": [manifest_record],
            "manifest": manifest_record["manifest"],
            "manifest_id": manifest_record["manifest_id"],
            "manifest_schema_version": manifest_record["manifest_schema_version"],
            "workload_count": manifest_record["workload_count"],
            "smoke_workload_ids": manifest_record["smoke_workload_ids"],
            "spec_refs": manifest_record["spec_refs"],
        },
        baseline={
            "python": "synthetic",
            "version_family": "3.12.x",
            "re_module": "re",
        },
        native_module_loaded=True,
    )
    tracked_report_path = tmp_path / "synthetic-benchmark-report.py"
    tracked_report_path.write_text("REPORT = {}\n")

    support.assert_source_tree_benchmark_contract(
        unittest.TestCase(),
        scorecard,
        _summary_view(scorecard),
        expected_phase="synthetic-phase",
        expected_runner_version="synthetic-runner",
        expected_adapter="source-tree-shim",
        expected_manifests=[manifest],
        expected_manifest_paths=[manifest_path],
        expected_selection_mode="full",
        tracked_report_path=tracked_report_path,
    )


def test_source_tree_report_contract_accepts_combined_manifest_scorecard_without_native_load(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        benchmark_test_support,
        "build_cpython_baseline",
        lambda version_family: {
            "python": "synthetic",
            "version_family": version_family,
        },
    )
    manifest_paths = [
        "benchmarks/workloads/first_boundary.py",
        "benchmarks/workloads/second_boundary.py",
    ]
    first_workloads = (
        SimpleNamespace(
            workload_id="module-search-first-warm-str",
            operation="module.search",
            family="module",
        ),
    )
    first_workload_by_id = {
        workload.workload_id: workload for workload in first_workloads
    }
    second_workloads = (
        SimpleNamespace(
            workload_id="module-compile-second-cold-gap",
            operation="module.compile",
            family="parser",
        ),
        SimpleNamespace(
            workload_id="pattern-fullmatch-second-purged-str",
            operation="pattern.fullmatch",
            family="module",
        ),
    )
    second_workload_by_id = {
        workload.workload_id: workload for workload in second_workloads
    }
    manifests = [
        SimpleNamespace(
            manifest_id="first-boundary",
            schema_version=3,
            workloads=first_workloads,
            smoke_workload_ids=lambda: ("module-search-first-warm-str",),
            spec_refs=("docs/spec/first-boundary.md",),
            notes=None,
            selected_workloads=lambda selected_workload_ids=None: (
                first_workloads
                if selected_workload_ids is None
                else tuple(
                    first_workload_by_id[workload_id]
                    for workload_id in selected_workload_ids
                )
            ),
        ),
        SimpleNamespace(
            manifest_id="second-boundary",
            schema_version=5,
            workloads=second_workloads,
            smoke_workload_ids=lambda: ("module-compile-second-cold-gap",),
            spec_refs=("docs/spec/second-boundary.md",),
            notes=None,
            selected_workloads=lambda selected_workload_ids=None: (
                second_workloads
                if selected_workload_ids is None
                else tuple(
                    second_workload_by_id[workload_id]
                    for workload_id in selected_workload_ids
                )
            ),
        ),
    ]
    manifest_records = [
        benchmark_test_support._artifact_manifest_record(manifest_path, manifest)
        for manifest_path, manifest in zip(manifest_paths, manifests, strict=True)
    ]
    scorecard = _synthetic_report_scorecard(
        workloads=(
            {
                "id": "module-search-first-warm-str",
                "manifest_id": "first-boundary",
                "family": "module",
                "cache_mode": "warm",
                "status": "measured",
            },
            {
                "id": "module-compile-second-cold-gap",
                "manifest_id": "second-boundary",
                "family": "parser",
                "cache_mode": "cold",
                "status": "known-gap",
            },
            {
                "id": "pattern-fullmatch-second-purged-str",
                "manifest_id": "second-boundary",
                "family": "module",
                "cache_mode": "purged",
                "status": "measured",
            },
        ),
        artifacts={
            "selection_mode": "smoke",
            "raw_samples": None,
            "manifests": manifest_records,
            "manifest": None,
            "manifest_id": "combined-benchmark-suite",
            "manifest_schema_version": 1,
        },
        baseline={
            "python": "synthetic",
            "version_family": "3.12.x",
            "re_module": "re",
        },
        native_module_loaded=False,
    )

    support.assert_source_tree_benchmark_contract(
        unittest.TestCase(),
        scorecard,
        _summary_view(scorecard),
        expected_phase="synthetic-phase",
        expected_runner_version="synthetic-runner",
        expected_adapter="source-tree-shim",
        expected_manifests=manifests,
        expected_manifest_paths=manifest_paths,
        expected_selection_mode="smoke",
    )


def test_manifest_contract_helpers_validate_selected_workloads_and_lookup() -> None:
    manifest_path = "benchmarks/workloads/synthetic_boundary.py"
    workloads = (
        SimpleNamespace(
            workload_id="module-compile-synthetic-cold",
            operation="module.compile",
            family="parser",
        ),
        SimpleNamespace(
            workload_id="module-search-synthetic-warm",
            operation="module.search",
            family="module",
        ),
        SimpleNamespace(
            workload_id="pattern-fullmatch-synthetic-purged",
            operation="pattern.fullmatch",
            family="module",
        ),
    )
    workload_by_id = {workload.workload_id: workload for workload in workloads}
    manifest = SimpleNamespace(
        manifest_id="synthetic-boundary",
        schema_version=1,
        workloads=workloads,
        smoke_workload_ids=lambda: ("module-compile-synthetic-cold",),
        spec_refs=("docs/spec/synthetic-boundary.md",),
        notes="synthetic manifest notes",
        selected_workloads=lambda selected_workload_ids=None: (
            workloads
            if selected_workload_ids is None
            else tuple(workload_by_id[workload_id] for workload_id in selected_workload_ids)
        ),
    )
    manifest_record = benchmark_test_support._artifact_manifest_record(
        manifest_path,
        manifest,
    )
    manifest_summary = {
        "workload_count": 3,
        "selected_workload_count": 2,
        "measured_workloads": 1,
        "known_gap_count": 1,
        "readiness": "partial",
        "selection_mode": "smoke",
        "available_smoke_workload_count": 1,
        "smoke_workload_ids": manifest.smoke_workload_ids(),
        "families": ["module", "parser"],
        "operations": ["module.compile", "module.search"],
        "spec_refs": manifest.spec_refs,
        "notes": manifest.notes,
    }
    scorecard = {"artifacts": {"manifests": [manifest_record]}}

    benchmark_test_support.assert_benchmark_manifest_contract(
        unittest.TestCase(),
        manifest_summary,
        benchmark_test_support.find_manifest_record(scorecard, manifest.manifest_id),
        manifest=manifest,
        manifest_path=manifest_path,
        known_gap_count=1,
        selection_mode="smoke",
        selected_workload_ids=(
            "module-compile-synthetic-cold",
            "module-search-synthetic-warm",
        ),
    )


def test_find_manifest_record_rejects_missing_manifest_id() -> None:
    with pytest.raises(
        AssertionError,
        match="missing manifest record for 'missing-boundary'",
    ):
        benchmark_test_support.find_manifest_record(
            {
                "artifacts": {
                    "manifests": [
                        {
                            "manifest_id": "synthetic-boundary",
                            "manifest": "benchmarks/workloads/synthetic_boundary.py",
                        }
                    ]
                }
            },
            "missing-boundary",
        )


def test_source_tree_support_module_imports_shared_support_through_tests_benchmarks_package_only(
) -> None:
    module_ast = benchmark_test_support._parsed_module_ast(support)
    package_imports = {
        (alias.name, alias.asname)
        for node in module_ast.body
        if isinstance(node, ast.ImportFrom) and node.module == "tests.benchmarks"
        for alias in node.names
        if alias.name == "benchmark_test_support"
    }

    assert package_imports == {("benchmark_test_support", None)}
    assert not any(
        isinstance(node, ast.ImportFrom)
        and node.module
        in {
            "tests.benchmarks.benchmark_test_support",
        }
        for node in module_ast.body
    )


@pytest.mark.parametrize(
    (
        "module_name",
        "expected_source_tree_names",
        "forbidden_local_names",
        "expected_benchmark_support_names",
        "expected_collection_replacement_names",
        "expected_package_imports",
    ),
    (
        pytest.param(
            "tests.benchmarks.test_pattern_boundary_benchmark_anchor_support",
            frozenset(
                {
                    "_source_tree_contract_manifest",
                    "_source_tree_contract_workload",
                }
            ),
            frozenset(),
            frozenset(),
            frozenset(),
            frozenset(
                {
                    (
                        "collection_replacement_benchmark_anchor_support",
                        "collection_replacement_support",
                    ),
                    ("source_tree_benchmark_anchor_support", "source_tree_support"),
                }
            ),
            id="pattern-boundary",
        ),
        pytest.param(
            "tests.benchmarks.test_collection_replacement_benchmark_anchor_support",
            frozenset(
                {"_source_tree_contract_manifest", "_source_tree_contract_workload"}
            ),
            frozenset(),
            frozenset(),
            frozenset(),
            frozenset(
                {
                    ("collection_replacement_benchmark_anchor_support", "support"),
                    ("source_tree_benchmark_anchor_support", "source_tree_support"),
                }
            ),
            id="collection-replacement",
        ),
        pytest.param(
            "tests.benchmarks.test_benchmark_manifest_validation",
            frozenset(
                {
                    "_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS",
                    "_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS",
                    "_assert_compiled_pattern_module_success_payload_round_trip",
                    "_source_tree_contract_manifest",
                    "_source_tree_contract_workload",
                    "_compiled_pattern_wrong_text_model_specs",
                    "_compiled_pattern_wrong_text_model_source_workloads",
                    "_run_cpython_compiled_pattern_module_helper_workload",
                    "_assert_wrong_text_model_payload_round_trip",
                    "include_live_compiled_pattern_module_success_workload",
                }
            ),
            frozenset(
                {
                    "_compiled_pattern_module_helper_keyword_contract_surface",
                    "_compiled_pattern_module_helper_keyword_contract_spec",
                }
            ),
            frozenset(),
            frozenset(
                {
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
                }
            ),
            frozenset(
                {
                    (
                        "collection_replacement_benchmark_anchor_support",
                        "collection_replacement_support",
                    ),
                    ("source_tree_benchmark_anchor_support", "source_tree_support"),
                }
            ),
            id="manifest-validation",
        ),
        pytest.param(
            "tests.benchmarks.test_source_tree_combined_boundary_benchmarks",
            frozenset(
                {
                    "_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC",
                    "_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC",
                    "_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS",
                    "_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS",
                    "_assert_compiled_pattern_module_success_payload_round_trip",
                    "_source_tree_contract_manifest",
                    "_source_tree_contract_workload",
                    "_compiled_pattern_wrong_text_model_specs",
                    "_compiled_pattern_wrong_text_model_source_workloads",
                    "_assert_wrong_text_model_payload_round_trip",
                }
            ),
            frozenset(
                {
                    "_compiled_pattern_module_contract_case",
                    "_compiled_pattern_module_helper_keyword_contract_spec",
                }
            ),
            frozenset(
                {
                    "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
                    "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS",
                    "_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS",
                    "_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS",
                    "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES",
                }
            ),
            frozenset(
                {
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
                    "_is_collection_replacement_compiled_pattern_keyword_error_workload",
                }
            ),
            frozenset(
                {
                    (
                        "collection_replacement_benchmark_anchor_support",
                        "collection_replacement_support",
                    ),
                    ("source_tree_benchmark_anchor_support", "source_tree_owner_support"),
                }
            ),
            id="source-tree-combined",
        ),
    ),
)
def test_source_tree_contract_builder_consumers_route_owner_surface_through_package_alias(
    module_name: str,
    expected_source_tree_names: frozenset[str],
    forbidden_local_names: frozenset[str],
    expected_benchmark_support_names: frozenset[str],
    expected_collection_replacement_names: frozenset[str],
    expected_package_imports: frozenset[tuple[str, str | None]],
) -> None:
    module = importlib.import_module(module_name)
    module_ast = benchmark_test_support._parsed_module_ast(module)
    local_definition_names, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            module
        )
    )
    local_names = local_definition_names | local_assignment_names
    benchmark_support_alias_names = benchmark_test_support._module_alias_names(
        module_ast,
        import_from_module="tests.benchmarks",
        import_name="benchmark_test_support",
        dotted_import_name="tests.benchmarks.benchmark_test_support",
    )
    collection_replacement_alias_names = benchmark_test_support._module_alias_names(
        module_ast,
        import_from_module="tests.benchmarks",
        import_name="collection_replacement_benchmark_anchor_support",
        dotted_import_name=(
            "tests.benchmarks.collection_replacement_benchmark_anchor_support"
        ),
    )
    package_imports = {
        (alias.name, alias.asname)
        for node in module_ast.body
        if isinstance(node, ast.ImportFrom) and node.module == "tests.benchmarks"
        for alias in node.names
        if alias.name
        in {
            "collection_replacement_benchmark_anchor_support",
            "source_tree_benchmark_anchor_support",
        }
    }
    direct_benchmark_support_imports = benchmark_test_support._top_level_import_from_alias_pairs(
        module_ast,
        module_name="tests.benchmarks.benchmark_test_support",
        imported_names=expected_benchmark_support_names,
    )
    benchmark_support_local_aliases = frozenset(
        (target_name, attribute_name)
        for target_name, attribute_name in benchmark_test_support._module_attribute_alias_targets(
            module_ast,
            module_alias_names=benchmark_support_alias_names,
        ).items()
        if attribute_name in expected_benchmark_support_names
    )

    assert "tests.benchmarks" in benchmark_test_support._module_import_targets(module)
    assert (
        "tests.benchmarks.benchmark_test_support"
        not in benchmark_test_support._module_import_targets(module)
    )
    assert package_imports == expected_package_imports
    assert direct_benchmark_support_imports == frozenset()
    assert benchmark_support_local_aliases == frozenset()
    assert forbidden_local_names.isdisjoint(local_names)
    assert expected_source_tree_names.isdisjoint(local_names)
    assert expected_benchmark_support_names.isdisjoint(local_names)
    assert expected_collection_replacement_names.isdisjoint(local_names)
    assert frozenset(
        node.attr
        for node in ast.walk(module_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "source_tree_support"
        and node.attr in expected_source_tree_names
    ) == expected_source_tree_names
    assert frozenset(
        node.attr
        for node in ast.walk(module_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in benchmark_support_alias_names
        and node.attr in expected_benchmark_support_names
    ) == expected_benchmark_support_names
    assert frozenset(
        node.attr
        for node in ast.walk(module_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in collection_replacement_alias_names
        and node.attr in expected_collection_replacement_names
    ) == expected_collection_replacement_names


@pytest.mark.parametrize(
    ("module_source", "expected_direct_imports", "expected_local_aliases"),
    (
        pytest.param(
            "\n".join(
                (
                    "from tests.benchmarks import benchmark_test_support",
                    (
                        "from tests.benchmarks.source_tree_benchmark_anchor_support import "
                        "_source_tree_contract_manifest"
                    ),
                )
            ),
            frozenset({("_source_tree_contract_manifest", None)}),
            frozenset(),
            id="direct-import",
        ),
        pytest.param(
            "\n".join(
                (
                    "from tests.benchmarks import benchmark_test_support",
                    (
                        "from tests.benchmarks.source_tree_benchmark_anchor_support import "
                        "_source_tree_contract_manifest as contract_manifest"
                    ),
                )
            ),
            frozenset({("_source_tree_contract_manifest", "contract_manifest")}),
            frozenset(),
            id="direct-import-asname",
        ),
            pytest.param(
                "\n".join(
                    (
                        "from tests.benchmarks import benchmark_test_support",
                        "from tests.benchmarks import source_tree_benchmark_anchor_support as source_tree_support",
                        "",
                        (
                            "contract_manifest = "
                            "source_tree_support._source_tree_contract_manifest"
                        ),
                )
            ),
            frozenset(),
            frozenset({("contract_manifest", "_source_tree_contract_manifest")}),
            id="local-alias",
        ),
        pytest.param(
            "\n".join(
                (
                    "from tests.benchmarks import source_tree_benchmark_anchor_support as source_tree_support",
                    "from collections.abc import Callable",
                    "",
                    (
                        "contract_manifest: Callable[..., object] = "
                        "source_tree_support._source_tree_contract_manifest"
                    ),
                )
            ),
            frozenset(),
            frozenset({("contract_manifest", "_source_tree_contract_manifest")}),
            id="annotated-local-alias",
        ),
        pytest.param(
            "\n".join(
                (
                    "from tests.benchmarks import source_tree_benchmark_anchor_support as source_tree_support",
                    "",
                    (
                        "contract_manifest = contract_manifest_alias = "
                        "source_tree_support._source_tree_contract_manifest"
                    ),
                )
            ),
            frozenset(),
            frozenset(
                {
                    ("contract_manifest", "_source_tree_contract_manifest"),
                    ("contract_manifest_alias", "_source_tree_contract_manifest"),
                }
            ),
            id="multi-target-local-alias",
        ),
        pytest.param(
            "\n".join(
                (
                    (
                        "from tests.benchmarks import "
                        "source_tree_benchmark_anchor_support as source_tree_support"
                    ),
                    "",
                    "source_tree_support_final = source_tree_support",
                    (
                        "contract_manifest = "
                        "source_tree_support_final._source_tree_contract_manifest"
                    ),
                    "contract_manifest_alias: object = contract_manifest",
                )
            ),
            frozenset(),
            frozenset(
                {
                    ("contract_manifest", "_source_tree_contract_manifest"),
                    ("contract_manifest_alias", "_source_tree_contract_manifest"),
                }
            ),
            id="chained-package-and-local-alias",
        ),
        pytest.param(
            "\n".join(
                (
                    (
                        "import tests.benchmarks.source_tree_benchmark_anchor_support "
                        "as source_tree_support"
                    ),
                    "",
                    "source_tree_support_final = source_tree_support",
                    (
                        "contract_manifest = "
                        "source_tree_support_final._source_tree_contract_manifest"
                    ),
                    "contract_manifest_alias: object = contract_manifest",
                )
            ),
            frozenset(),
            frozenset(
                {
                    ("contract_manifest", "_source_tree_contract_manifest"),
                    ("contract_manifest_alias", "_source_tree_contract_manifest"),
                }
            ),
            id="dotted-package-and-local-alias",
        ),
    ),
)
def test_source_tree_contract_builder_consumer_guard_detects_direct_imports_and_local_aliases(
    module_source: str,
    expected_direct_imports: frozenset[tuple[str, str | None]],
    expected_local_aliases: frozenset[tuple[str, str]],
) -> None:
    module_ast = ast.parse(module_source)
    source_tree_support_alias_names = benchmark_test_support._module_alias_names(
        module_ast,
        import_from_module="tests.benchmarks",
        import_name="source_tree_benchmark_anchor_support",
        dotted_import_name="tests.benchmarks.source_tree_benchmark_anchor_support",
    )
    contract_builder_names = frozenset(
        {"_source_tree_contract_manifest", "_source_tree_contract_workload"}
    )

    assert benchmark_test_support._top_level_import_from_alias_pairs(
        module_ast,
        module_name="tests.benchmarks.source_tree_benchmark_anchor_support",
        imported_names=contract_builder_names,
    ) == expected_direct_imports
    assert frozenset(
        (target_name, attribute_name)
        for target_name, attribute_name in benchmark_test_support._module_attribute_alias_targets(
            module_ast,
            module_alias_names=source_tree_support_alias_names,
        ).items()
        if attribute_name in contract_builder_names
    ) == expected_local_aliases


def test_source_tree_owner_retires_compiled_pattern_module_compile_surface_to_shared_support(
) -> None:
    source_tree_assignment_names = {
        "_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
        "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS",
        "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES",
    }
    local_definition_names, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            support
        )
    )

    assert source_tree_assignment_names.isdisjoint(local_definition_names)
    assert source_tree_assignment_names.issubset(local_assignment_names)
    for assignment_name in source_tree_assignment_names:
        assert hasattr(support, assignment_name)
        assert not hasattr(benchmark_test_support, assignment_name)


def test_source_tree_owner_no_longer_keeps_contract_builder_spec_local() -> None:
    local_definition_names, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            support
        )
    )

    assert "_SourceTreeContractBuilderSpec" not in local_definition_names | local_assignment_names
    assert not hasattr(support, "_SourceTreeContractBuilderSpec")
    assert hasattr(benchmark_test_support, "_SourceTreeContractBuilderSpec")


def test_combined_suite_single_manifest_representatives_use_combined_suite_slice_expectations(
) -> None:
    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    class_definition = benchmark_test_support._module_class_definition(
        combined_suite,
        "SourceTreeScorecardBenchmarkSuiteTest",
    )
    method_definition = benchmark_test_support._class_method_definition(
        class_definition,
        "test_single_manifest_scorecards_keep_slice_backed_representatives",
    )

    assert frozenset(
        node.attr
        for node in ast.walk(method_definition)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "source_tree_support"
        and node.attr
        in {
            "SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS",
            "SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS",
        }
    ) == frozenset({"SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS"})


def test_source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally(
) -> None:
    owner_definition_names = frozenset(
        {
            "_compiled_pattern_wrong_text_model_specs",
            "_compiled_pattern_wrong_text_model_source_workloads",
            "_run_cpython_compiled_pattern_module_helper_workload",
            "_assert_wrong_text_model_payload_round_trip",
            "_module_workflow_compiled_pattern_correctness_case_signature",
            "_module_workflow_compiled_pattern_workload_signature",
            "_is_module_workflow_compiled_pattern_wrong_text_model_workload",
        }
    )
    owner_assignment_names = frozenset()
    module_ast = benchmark_test_support._parsed_module_ast(support)

    benchmark_test_support.assert_mixed_owner_surface(
        support,
        local_function_names=owner_definition_names,
        local_assignment_names=owner_assignment_names,
        support_alias_assignment_names=frozenset(),
    )
    assert not hasattr(support, "compiled_pattern_contract_expected_build_calls")
    assert not hasattr(support, "_compiled_pattern_module_helper_route")
    for definition_name in owner_definition_names:
        assert not hasattr(benchmark_test_support, definition_name)

    for definition_name in owner_definition_names:
        definition = next(
            node
            for node in benchmark_test_support._parsed_module_ast(support).body
            if isinstance(node, ast.FunctionDef) and node.name == definition_name
        )
        assert isinstance(definition, ast.FunctionDef)

    for assignment_name in owner_assignment_names:
        assignment = benchmark_test_support._module_assignment(
            support,
            assignment_name,
        )
        assert isinstance(assignment, ast.Assign)

    assert {
        node.attr
        for node in ast.walk(module_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "benchmark_test_support"
        and node.attr in owner_definition_names | owner_assignment_names
    } == set()
    assert {
        node.attr
        for node in ast.walk(module_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "benchmark_test_support"
    } >= {
        "_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
        "_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
        "_compiled_pattern_module_helper_route",
        "_is_collection_replacement_wrong_text_model_workload",
        "_is_module_workflow_compiled_pattern_workload",
        "freeze_signature_value",
        "selected_manifest_workloads",
    }


def test_source_tree_owner_manifest_path_constants_point_to_current_workload_files() -> None:
    manifest_paths = (
        support.benchmark_test_support.OPTIONAL_GROUP_MANIFEST_PATH,
        support.benchmark_test_support.NESTED_GROUP_MANIFEST_PATH,
        support.benchmark_test_support.EXACT_REPEAT_MANIFEST_PATH,
        support.benchmark_test_support.RANGED_REPEAT_MANIFEST_PATH,
        support.benchmark_test_support.GROUPED_ALTERNATION_MANIFEST_PATH,
        support.benchmark_test_support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        support.benchmark_test_support.NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,
        support.benchmark_test_support.OPEN_ENDED_MANIFEST_PATH,
    )

    assert support.benchmark_test_support is benchmark_test_support
    assert manifest_paths == (
        REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.py",
        REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py",
        REPO_ROOT
        / "benchmarks"
        / "workloads"
        / "exact_repeat_quantified_group_boundary.py",
        REPO_ROOT
        / "benchmarks"
        / "workloads"
        / "ranged_repeat_quantified_group_boundary.py",
        REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py",
        REPO_ROOT
        / "benchmarks"
        / "workloads"
        / "grouped_alternation_replacement_boundary.py",
        REPO_ROOT / "benchmarks" / "workloads" / "nested_group_replacement_boundary.py",
        REPO_ROOT
        / "benchmarks"
        / "workloads"
        / "open_ended_quantified_group_boundary.py",
    )
    assert all(manifest_path.is_file() for manifest_path in manifest_paths)


@pytest.mark.parametrize(
    ("builder_name", "expected_manifest_path_names"),
    (
        pytest.param(
            "_source_tree_standard_benchmark_definitions",
            (
                ("MODULE_BOUNDARY_MANIFEST_PATH",),
                ("OPTIONAL_GROUP_MANIFEST_PATH",),
                ("NESTED_GROUP_MANIFEST_PATH",),
                ("EXACT_REPEAT_MANIFEST_PATH",),
                ("RANGED_REPEAT_MANIFEST_PATH",),
                ("GROUPED_ALTERNATION_MANIFEST_PATH",),
                ("GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH",),
                ("NESTED_GROUP_REPLACEMENT_MANIFEST_PATH",),
                ("OPEN_ENDED_MANIFEST_PATH",),
            ),
            id="source-tree-standard",
        ),
    ),
)
def test_source_tree_owner_builders_reference_owner_manifest_path_constants(
    builder_name: str,
    expected_manifest_path_names: tuple[tuple[str, ...], ...],
) -> None:
    builder = next(
        node
        for node in benchmark_test_support._parsed_module_ast(support).body
        if isinstance(node, ast.FunctionDef) and node.name == builder_name
    )
    builder_return = next(
        node for node in builder.body if isinstance(node, ast.Return)
    )
    observed_manifest_path_names: list[tuple[str, ...]] = []
    assert isinstance(builder_return.value, ast.Tuple)

    for element in builder_return.value.elts:
        assert isinstance(element, ast.Call)
        manifest_paths_keyword = next(
            keyword for keyword in element.keywords if keyword.arg == "manifest_paths"
        )
        assert isinstance(manifest_paths_keyword.value, ast.Tuple)
        manifest_path_names: list[str] = []
        for manifest_path in manifest_paths_keyword.value.elts:
            assert isinstance(manifest_path, ast.Attribute)
            assert isinstance(manifest_path.value, ast.Name)
            assert manifest_path.value.id == "benchmark_test_support"
            manifest_path_names.append(manifest_path.attr)
        observed_manifest_path_names.append(tuple(manifest_path_names))

    assert tuple(observed_manifest_path_names) == expected_manifest_path_names


def test_source_tree_owner_definition_exports_reuse_owner_manifest_path_constants() -> None:
    manifest_paths = tuple(
        definition.manifest_paths[0]
        for definition in support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS
    )

    assert manifest_paths == (
        benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
        benchmark_test_support.OPTIONAL_GROUP_MANIFEST_PATH,
        benchmark_test_support.NESTED_GROUP_MANIFEST_PATH,
        benchmark_test_support.EXACT_REPEAT_MANIFEST_PATH,
        benchmark_test_support.RANGED_REPEAT_MANIFEST_PATH,
        benchmark_test_support.GROUPED_ALTERNATION_MANIFEST_PATH,
        benchmark_test_support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        benchmark_test_support.NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,
        benchmark_test_support.OPEN_ENDED_MANIFEST_PATH,
    )
    assert all(manifest_path.is_file() for manifest_path in manifest_paths)


def test_source_tree_owner_does_not_export_compiled_pattern_module_helper_keyword_shared_surface(
) -> None:
    definition_names, assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(support)
    )
    local_names = definition_names | assignment_names
    assignment_only_names = (
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS",
    )

    assert all(name not in local_names for name in assignment_only_names)
    assert all(not hasattr(support, name) for name in assignment_only_names)
    assert all(hasattr(collection_support, name) for name in assignment_only_names)
    assert (
        "_is_collection_replacement_compiled_pattern_keyword_error_workload"
        not in local_names
    )
    assert not hasattr(
        support,
        "_is_collection_replacement_compiled_pattern_keyword_error_workload",
    )
    assert hasattr(
        collection_support,
        "_is_collection_replacement_compiled_pattern_keyword_error_workload",
    )


def test_source_tree_compiled_pattern_module_compile_standard_definition_helpers_stay_shared_support_owned(
) -> None:
    definition_names, assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(support)
    )
    shared_definition_names, shared_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            benchmark_test_support
        )
    )

    assert (
        "_build_compiled_pattern_module_compile_standard_benchmark_definitions"
        not in definition_names
    )
    assert (
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS"
        not in assignment_names
    )
    assert "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES" in assignment_names
    assert (
        "_build_compiled_pattern_module_compile_standard_benchmark_definitions"
        in shared_definition_names
    )
    assert (
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS"
        in shared_assignment_names
    )
    assert "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES" not in shared_assignment_names
    assert not hasattr(
        support,
        "_build_compiled_pattern_module_compile_standard_benchmark_definitions",
    )
    assert not hasattr(
        support,
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
    )
    assert hasattr(support, "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES")
    assert hasattr(
        benchmark_test_support,
        "_build_compiled_pattern_module_compile_standard_benchmark_definitions",
    )
    assert hasattr(
        benchmark_test_support,
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
    )
    assert not hasattr(
        benchmark_test_support,
        "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES",
    )


def test_source_tree_owner_keeps_collection_routed_names_off_source_tree_module() -> None:
    _, assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            collection_support
        )
    )
    routed_names = frozenset(
        name
        for name in assignment_names
        if name == "COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS"
        or (
            name.startswith("CONDITIONAL_GROUP_EXISTS_")
            and name.endswith("_WORKLOAD_IDS")
        )
    )

    assert routed_names
    assert (
        "COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS"
        in routed_names
    )
    for routed_name in routed_names:
        assert not hasattr(support, routed_name)
        assert not hasattr(benchmark_test_support, routed_name)
        assert hasattr(collection_support, routed_name)


def test_source_tree_standard_definitions_export_stays_owned_by_source_tree() -> None:
    owner_definitions = support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS
    definition_names = tuple(definition.name for definition in owner_definitions)
    assert definition_names == (
        "module-workflow-compiled-pattern-wrong-text-model",
        "optional-group-conditional",
        "nested-group",
        "exact-repeat",
        "ranged-repeat",
        "grouped-alternation",
        "grouped-alternation-replacement",
        "nested-group-replacement",
        "open-ended-grouped-alternation",
    )
    standard_definitions = (
        *benchmark_test_support.COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS,
        *collection_support.COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS,
        *benchmark_test_support.MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS,
        *benchmark_test_support.COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS,
        *benchmark_test_support.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS,
        *pattern_boundary_support.PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS,
        *support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS,
    )
    start_index = next(
        index
        for index, definition in enumerate(standard_definitions)
        if definition.name == definition_names[0]
    )
    standard_inventory_slice = standard_definitions[
        start_index : start_index + len(owner_definitions)
    ]

    assert tuple(
        definition.name for definition in standard_inventory_slice
    ) == definition_names
    assert standard_inventory_slice == owner_definitions
    assert all(
        standard_definition is owner_definition
        for standard_definition, owner_definition in zip(
            standard_inventory_slice,
            owner_definitions,
            strict=True,
        )
    )


def test_source_tree_wrong_text_model_standard_definition_stays_bound_to_local_module_boundary_contract(
) -> None:
    definition = support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS[0]
    selected_workloads = benchmark_test_support.selected_manifest_workloads(
        benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload=definition.includes_workload,
    )

    assert definition.name == "module-workflow-compiled-pattern-wrong-text-model"
    assert definition.manifest_paths == (
        benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
    )
    assert (
        definition.include_workload
        is support._is_module_workflow_compiled_pattern_wrong_text_model_workload
    )
    assert (
        definition.correctness_case_signature
        is support._module_workflow_compiled_pattern_correctness_case_signature
    )
    assert (
        definition.workload_signature
        is support._module_workflow_compiled_pattern_workload_signature
    )
    assert tuple(workload.workload_id for workload in selected_workloads) == tuple(
        workload_id for _, workload_id in definition.expected_anchor_case_ids
    )


def test_optional_group_conditional_helpers_stay_on_the_search_anchor() -> None:
    cases = benchmark_test_support.published_cases_by_id()
    workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.OPTIONAL_GROUP_MANIFEST_PATH,
        support._OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID,
    )
    non_conditional_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.OPTIONAL_GROUP_MANIFEST_PATH,
        "module-search-named-optional-group-absent-warm-str",
    )

    assert support._is_optional_group_conditional_workload(workload)
    assert not support._is_optional_group_conditional_workload(non_conditional_workload)
    assert support._optional_group_correctness_case_signature(
        cases["optional-group-conditional-module-search-present-str"]
    ) == (
        "module.search",
        None,
        ("a(b)?(?(1)c|d)e", "zzabcezz"),
        (),
        0,
        "str",
    )
    assert support._optional_group_workload_signature(workload) == (
        "module.search",
        None,
        ("a(b)?(?(1)c|d)e", "zzabcezz"),
        (),
        0,
        "str",
    )
    assert (
        support._optional_group_correctness_case_signature(
            benchmark_test_support._module_pattern_case(
                helper="fullmatch",
                operation="pattern_call",
                args=("abce",),
                pattern="a(b)?(?(1)c|d)e",
            )
        )
        is None
    )
    with pytest.raises(
        AssertionError,
        match="unexpected optional-group benchmark workload operation",
    ):
        support._optional_group_workload_signature(
            benchmark_test_support.synthetic_workload(
                manifest_id="optional-group-boundary",
                workload_id="optional-group-compile-unsupported",
                operation="module.compile",
                pattern="a(b)?(?(1)c|d)e",
            )
        )


def test_nested_group_live_signatures_cover_numbered_and_named_routes() -> None:
    cases = benchmark_test_support.published_cases_by_id()

    assert support._nested_group_correctness_case_signature(
        cases["nested-group-compile-metadata-str"]
    ) == ("module.compile", "a((b))d", (), (), 0, "str")
    assert support._nested_group_workload_signature(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.NESTED_GROUP_MANIFEST_PATH,
            "module-compile-nested-group-cold-str",
        )
    ) == ("module.compile", "a((b))d", (), (), 0, "str")

    assert support._nested_group_correctness_case_signature(
        cases["nested-group-module-search-str"]
    ) == (
        "module.search",
        None,
        ("a((b))d", "zzabdzz"),
        (),
        0,
        "str",
    )
    assert support._nested_group_workload_signature(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.NESTED_GROUP_MANIFEST_PATH,
            "module-search-nested-group-warm-str",
        )
    ) == (
        "module.search",
        None,
        ("a((b))d", "zzabdzz"),
        (),
        0,
        "str",
    )

    assert support._nested_group_correctness_case_signature(
        cases["nested-group-pattern-fullmatch-str"]
    ) == (
        "pattern.fullmatch",
        "a((b))d",
        ("abd",),
        (),
        0,
        "str",
    )
    assert support._nested_group_workload_signature(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.NESTED_GROUP_MANIFEST_PATH,
            "pattern-fullmatch-nested-group-purged-str",
        )
    ) == (
        "pattern.fullmatch",
        "a((b))d",
        ("abd",),
        (),
        0,
        "str",
    )

    assert support._nested_group_correctness_case_signature(
        cases["named-nested-group-compile-metadata-str"]
    ) == ("module.compile", "a(?P<outer>(?P<inner>b))d", (), (), 0, "str")
    assert support._nested_group_workload_signature(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.NESTED_GROUP_MANIFEST_PATH,
            "module-compile-named-nested-group-warm-str",
        )
    ) == ("module.compile", "a(?P<outer>(?P<inner>b))d", (), (), 0, "str")

    assert support._nested_group_correctness_case_signature(
        cases["named-nested-group-module-search-str"]
    ) == (
        "module.search",
        None,
        ("a(?P<outer>(?P<inner>b))d", "zzabdzz"),
        (),
        0,
        "str",
    )
    assert support._nested_group_workload_signature(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.NESTED_GROUP_MANIFEST_PATH,
            "module-search-named-nested-group-warm-str",
        )
    ) == (
        "module.search",
        None,
        ("a(?P<outer>(?P<inner>b))d", "zzabdzz"),
        (),
        0,
        "str",
    )

    assert support._nested_group_correctness_case_signature(
        cases["named-nested-group-pattern-fullmatch-str"]
    ) == (
        "pattern.fullmatch",
        "a(?P<outer>(?P<inner>b))d",
        ("abd",),
        (),
        0,
        "str",
    )
    assert support._nested_group_workload_signature(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.NESTED_GROUP_MANIFEST_PATH,
            "pattern-fullmatch-named-nested-group-purged-str",
        )
    ) == (
        "pattern.fullmatch",
        "a(?P<outer>(?P<inner>b))d",
        ("abd",),
        (),
        0,
        "str",
    )


def test_counted_repeat_live_signatures_cover_exact_ranged_and_open_ended_routes() -> None:
    cases = benchmark_test_support.published_cases_by_id()

    assert support._counted_repeat_correctness_case_signature(
        cases["exact-repeat-numbered-group-compile-metadata-str"]
    ) == ("module.compile", "a(bc){2}d", (), (), 0, "str")
    assert support._counted_repeat_workload_signature(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.EXACT_REPEAT_MANIFEST_PATH,
            "module-compile-numbered-exact-repeat-group-cold-str",
        )
    ) == ("module.compile", "a(bc){2}d", (), (), 0, "str")

    assert support._counted_repeat_correctness_case_signature(
        cases["exact-repeat-named-group-module-search-str"]
    ) == (
        "module.search",
        None,
        ("a(?P<word>bc){2}d", "zzabcbcdzz"),
        (),
        0,
        "str",
    )
    assert support._counted_repeat_workload_signature(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.EXACT_REPEAT_MANIFEST_PATH,
            "module-search-named-exact-repeat-group-warm-str",
        )
    ) == (
        "module.search",
        None,
        ("a(?P<word>bc){2}d", "zzabcbcdzz"),
        (),
        0,
        "str",
    )

    assert support._counted_repeat_correctness_case_signature(
        cases["ranged-repeat-numbered-group-module-search-lower-bound-str"]
    ) == (
        "module.search",
        None,
        ("a(bc){1,2}d", "zzabcdzz"),
        (),
        0,
        "str",
    )
    assert support._counted_repeat_workload_signature(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.RANGED_REPEAT_MANIFEST_PATH,
            "module-search-numbered-ranged-repeat-group-lower-bound-warm-str",
        )
    ) == (
        "module.search",
        None,
        ("a(bc){1,2}d", "zzabcdzz"),
        (),
        0,
        "str",
    )

    assert support._counted_repeat_correctness_case_signature(
        cases["ranged-repeat-named-group-pattern-fullmatch-lower-bound-str"]
    ) == (
        "pattern.fullmatch",
        "a(?P<word>bc){1,2}d",
        ("abcd",),
        (),
        0,
        "str",
    )
    assert support._counted_repeat_workload_signature(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.RANGED_REPEAT_MANIFEST_PATH,
            "pattern-fullmatch-named-ranged-repeat-group-lower-bound-purged-str",
        )
    ) == (
        "pattern.fullmatch",
        "a(?P<word>bc){1,2}d",
        ("abcd",),
        (),
        0,
        "str",
    )

    assert support._counted_repeat_correctness_case_signature(
        cases["open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str"]
    ) == (
        "module.search",
        None,
        ("a(bc|de){1,}d", "zzabcdzz"),
        (),
        0,
        "str",
    )
    assert support._counted_repeat_workload_signature(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.OPEN_ENDED_MANIFEST_PATH,
            "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-str",
        )
    ) == (
        "module.search",
        None,
        ("a(bc|de){1,}d", "zzabcdzz"),
        (),
        0,
        "str",
    )

    assert support._counted_repeat_correctness_case_signature(
        cases["open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str"]
    ) == (
        "pattern.fullmatch",
        "a(?P<word>bc|de){1,}d",
        ("adededed",),
        (),
        0,
        "str",
    )
    assert support._counted_repeat_workload_signature(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.OPEN_ENDED_MANIFEST_PATH,
            "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-str",
        )
    ) == (
        "pattern.fullmatch",
        "a(?P<word>bc|de){1,}d",
        ("adededed",),
        (),
        0,
        "str",
    )


def test_non_alternation_counted_repeat_selector_excludes_alternation_workloads() -> None:
    assert support._is_non_alternation_counted_repeat_workload(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.EXACT_REPEAT_MANIFEST_PATH,
            "module-compile-numbered-exact-repeat-group-cold-str",
        )
    )
    assert support._is_non_alternation_counted_repeat_workload(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.RANGED_REPEAT_MANIFEST_PATH,
            "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
        )
    )
    assert not support._is_non_alternation_counted_repeat_workload(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.EXACT_REPEAT_MANIFEST_PATH,
            "module-search-numbered-exact-repeat-group-alternation-bc-bc-warm-str",
        )
    )
    assert not support._is_non_alternation_counted_repeat_workload(
        benchmark_test_support.live_manifest_workload(
            benchmark_test_support.OPEN_ENDED_MANIFEST_PATH,
            "module-search-numbered-open-ended-group-broader-range-cold-gap",
        )
    )


def test_published_case_ids_by_signature_groups_duplicate_case_ids(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest = benchmark_test_support._synthetic_manifest(
        cases=(
            benchmark_test_support._synthetic_case("case-b", ("shared",)),
            benchmark_test_support._synthetic_case("case-a", ("shared",)),
            benchmark_test_support._synthetic_case("case-c", ("unique",)),
            benchmark_test_support._synthetic_case("ignored", None),
        )
    )
    monkeypatch.setattr(
        benchmark_test_support,
        "published_fixture_manifests",
        lambda: (manifest,),
    )

    observed = benchmark_test_support.published_case_ids_by_signature(lambda case: case.signature)

    assert observed == {
        ("shared",): ("case-a", "case-b"),
        ("unique",): ("case-c",),
    }


def test_source_tree_reuses_shared_published_case_helpers_by_identity() -> None:
    assert not hasattr(support, "published_case_ids_by_signature")
    assert not hasattr(support, "published_cases_by_id")


def test_grouped_alternation_live_signatures_cover_non_replacement_routes() -> None:
    cases = benchmark_test_support.published_cases_by_id()

    compile_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.GROUPED_ALTERNATION_MANIFEST_PATH,
        "module-compile-grouped-alternation-cold-str",
    )
    search_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.GROUPED_ALTERNATION_MANIFEST_PATH,
        "module-search-grouped-alternation-warm-str",
    )
    fullmatch_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.GROUPED_ALTERNATION_MANIFEST_PATH,
        "pattern-fullmatch-grouped-alternation-purged-str",
    )
    legacy_module_sub_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.GROUPED_ALTERNATION_MANIFEST_PATH,
        "module-sub-template-nested-grouped-alternation-warm-gap",
    )
    legacy_pattern_subn_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.GROUPED_ALTERNATION_MANIFEST_PATH,
        "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
    )

    assert support._grouped_alternation_correctness_case_signature(
        cases["grouped-alternation-compile-metadata-str"]
    ) == ("module.compile", "a(b|c)d", (), (), 0, "str")
    assert support._grouped_alternation_workload_signature(compile_workload) == (
        "module.compile",
        "a(b|c)d",
        (),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_correctness_case_signature(
        cases["grouped-alternation-module-search-str"]
    ) == (
        "module.search",
        None,
        ("a(b|c)d", "zzacdzz"),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_workload_args(search_workload) == (
        "a(b|c)d",
        "zzacdzz",
    )
    assert support._grouped_alternation_workload_signature(search_workload) == (
        "module.search",
        None,
        ("a(b|c)d", "zzacdzz"),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_correctness_case_signature(
        cases["grouped-alternation-pattern-fullmatch-str"]
    ) == (
        "pattern.fullmatch",
        "a(b|c)d",
        ("abd",),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_workload_args(fullmatch_workload) == ("abd",)
    assert support._grouped_alternation_workload_signature(fullmatch_workload) == (
        "pattern.fullmatch",
        "a(b|c)d",
        ("abd",),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_correctness_case_signature(
        cases["module-sub-template-nested-group-alternation-numbered-wrapper-str"]
    ) == (
        "module.sub",
        None,
        ("a((b|c))d", "<\\1>", "abdacd"),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_workload_args(legacy_module_sub_workload) == (
        "a((b|c))d",
        "<\\1>",
        "abdacd",
    )
    assert support._grouped_alternation_workload_signature(
        legacy_module_sub_workload
    ) == (
        "module.sub",
        None,
        ("a((b|c))d", "<\\1>", "abdacd"),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_correctness_case_signature(
        cases["pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str"]
    ) == (
        "pattern.subn",
        "a(?P<outer>(b|c))d",
        ("<\\g<outer>>", "abdacd", 1),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_workload_args(
        legacy_pattern_subn_workload
    ) == ("<\\g<outer>>", "abdacd", 1)
    assert support._grouped_alternation_workload_signature(
        legacy_pattern_subn_workload
    ) == (
        "pattern.subn",
        "a(?P<outer>(b|c))d",
        ("<\\g<outer>>", "abdacd", 1),
        (),
        0,
        "str",
    )


def test_grouped_alternation_replacement_live_signatures_cover_module_and_pattern_routes() -> None:
    cases = benchmark_test_support.published_cases_by_id()

    module_sub_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        "module-sub-template-grouped-alternation-warm-str",
    )
    module_subn_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        "module-subn-template-named-grouped-alternation-warm-str",
    )
    pattern_sub_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        "pattern-sub-template-grouped-alternation-purged-str",
    )
    pattern_subn_workload = benchmark_test_support.live_manifest_workload(
        benchmark_test_support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        "pattern-subn-template-named-grouped-alternation-purged-str",
    )

    assert support._grouped_alternation_replacement_correctness_case_signature(
        cases["module-sub-template-grouped-alternation-str"]
    ) == (
        "module.sub",
        None,
        ("a(b|c)d", "\\1x", "abdacd"),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_workload_args(module_sub_workload) == (
        "a(b|c)d",
        "\\1x",
        "abdacd",
    )
    assert support._grouped_alternation_workload_signature(module_sub_workload) == (
        "module.sub",
        None,
        ("a(b|c)d", "\\1x", "abdacd"),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_replacement_correctness_case_signature(
        cases["module-subn-template-named-grouped-alternation-str"]
    ) == (
        "module.subn",
        None,
        ("a(?P<word>b|c)d", "\\g<word>x", "abdacd", 1),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_workload_args(module_subn_workload) == (
        "a(?P<word>b|c)d",
        "\\g<word>x",
        "abdacd",
        1,
    )
    assert support._grouped_alternation_workload_signature(
        module_subn_workload
    ) == (
        "module.subn",
        None,
        ("a(?P<word>b|c)d", "\\g<word>x", "abdacd", 1),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_replacement_correctness_case_signature(
        cases["pattern-sub-template-grouped-alternation-str"]
    ) == (
        "pattern.sub",
        "a(b|c)d",
        ("\\1x", "acdabd"),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_workload_args(pattern_sub_workload) == (
        "\\1x",
        "acdabd",
    )
    assert support._grouped_alternation_workload_signature(pattern_sub_workload) == (
        "pattern.sub",
        "a(b|c)d",
        ("\\1x", "acdabd"),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_replacement_correctness_case_signature(
        cases["pattern-subn-template-named-grouped-alternation-str"]
    ) == (
        "pattern.subn",
        "a(?P<word>b|c)d",
        ("\\g<word>x", "acdabd", 1),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_workload_args(pattern_subn_workload) == (
        "\\g<word>x",
        "acdabd",
        1,
    )
    assert support._grouped_alternation_workload_signature(
        pattern_subn_workload
    ) == (
        "pattern.subn",
        "a(?P<word>b|c)d",
        ("\\g<word>x", "acdabd", 1),
        (),
        0,
        "str",
    )


def test_grouped_alternation_workload_helpers_reject_unsupported_operations() -> None:
    unsupported_workload = benchmark_test_support.synthetic_workload(
        manifest_id="grouped-alternation-boundary",
        workload_id="module-match-grouped-alternation-unsupported",
        operation="module.match",
        pattern="a(b|c)d",
        haystack="abdacd",
        replacement="\\1x",
    )

    with pytest.raises(AssertionError, match="unexpected grouped-alternation"):
        support._grouped_alternation_workload_args(unsupported_workload)
    with pytest.raises(AssertionError, match="unexpected grouped-alternation"):
        support._grouped_alternation_workload_signature(unsupported_workload)
