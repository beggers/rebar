from __future__ import annotations

import ast
from functools import cache
import inspect
import pathlib
from types import SimpleNamespace
import unittest

import pytest

from tests.benchmarks.benchmark_test_support import (
    MODULE_BOUNDARY_MANIFEST_PATH as SHARED_MODULE_BOUNDARY_MANIFEST_PATH,
    STANDARD_BENCHMARK_DEFINITIONS,
    _synthetic_case,
    _synthetic_manifest,
    _synthetic_manifest_loader,
    _synthetic_workload,
    _synthetic_workload_is_included,
    _synthetic_workload_signature,
    anchor_support_cache_guard,
)
from tests.benchmarks import benchmark_test_support as benchmark_support
from tests.benchmarks import (
    collection_replacement_benchmark_anchor_support as collection_support,
)
from tests.benchmarks.benchmark_test_support import (
    live_manifest_workload,
    synthetic_workload,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    EXACT_REPEAT_MANIFEST_PATH,
    GROUPED_ALTERNATION_MANIFEST_PATH,
    GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
    NESTED_GROUP_MANIFEST_PATH,
    NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,
    OPEN_ENDED_MANIFEST_PATH,
    OPTIONAL_GROUP_MANIFEST_PATH,
    RANGED_REPEAT_MANIFEST_PATH,
)
from tests.benchmarks import source_tree_benchmark_anchor_support as support
from tests.conftest import REPO_ROOT

_MOVED_SOURCE_TREE_CLASS_NAMES = (
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
)

_MOVED_SOURCE_TREE_FUNCTION_NAMES = (
    "source_tree_scorecard_case_ids",
    "source_tree_scorecard_case",
    "source_tree_combined_target_manifest_ids",
    "source_tree_combined_case",
    "source_tree_combined_manifest_shape_expectation",
    "source_tree_combined_slice_manifest_ids",
    "source_tree_combined_slice_derived_manifest_ids",
    "source_tree_combined_slice_expectations",
    "source_tree_combined_fully_measured_manifest_ids",
    "source_tree_combined_fully_measured_manifest_expectation",
    "source_tree_combined_manifest_representative_measured_workload_ids",
    "expected_summary_for_manifests",
    "representative_measured_workload_ids",
    "select_source_tree_combined_slice_rows",
)

_MOVED_SOURCE_TREE_CONSTANT_NAMES = (
    "SOURCE_TREE_SCORECARD_EXPECTATIONS",
    "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
    "SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS",
)

_MOVED_REPORT_CONTRACT_HELPER_NAMES = (
    "_assert_benchmark_summary_consistent",
    "_artifact_manifest_record",
    "assert_source_tree_benchmark_contract",
    "assert_benchmark_manifest_contract",
    "find_manifest_record",
)

_MOVED_CONDITIONAL_CALLABLE_HELPER_NAMES = (
    "_conditional_group_exists_callable_str_slice_workloads",
    "_conditional_group_exists_callable_bytes_slice_workloads",
    "_conditional_group_exists_quantified_callable_str_workloads",
    "_conditional_group_exists_nested_callable_str_workloads",
    "_conditional_group_exists_nested_callable_bytes_workloads",
    "_conditional_group_exists_quantified_callable_bytes_workloads",
    "_conditional_group_exists_alternation_callable_bytes_workloads",
    "_split_workload_ids_by_text_model",
    "_selected_workload_ids",
    "_mirrored_bytes_workload_ids",
    "_conditional_group_exists_template_replacement_expectation",
    "_conditional_group_exists_callable_replacement_expectations",
    "_conditional_group_exists_alternation_callable_replacement_expectation",
    "_conditional_group_exists_nested_callable_replacement_expectation",
    "_conditional_group_exists_nested_callable_bytes_replacement_expectation",
    "_conditional_group_exists_quantified_callable_replacement_expectation",
    "_conditional_group_exists_quantified_callable_bytes_replacement_expectation",
)


def _module_pattern_case(
    *,
    helper: str,
    operation: str,
    args: tuple[object, ...],
    kwargs: dict[str, object] | None = None,
    pattern: str = "abc",
    flags: int = 0,
    text_model: str | None = "str",
    use_compiled_pattern: bool = False,
) -> object:
    pattern_value = pattern.encode() if text_model == "bytes" else pattern
    return SimpleNamespace(
        helper=helper,
        operation=operation,
        args=args,
        kwargs={} if kwargs is None else kwargs,
        pattern=pattern,
        flags=flags,
        text_model=text_model,
        use_compiled_pattern=use_compiled_pattern,
        pattern_payload=lambda: pattern_value,
    )


def _compile_search_fullmatch_case(
    *,
    operation: str,
    helper: str = "",
    args: tuple[object, ...] = (),
    kwargs: dict[str, object] | None = None,
    flags: int | None = None,
    text_model: str | None = None,
) -> object:
    serialized_kwargs = {} if kwargs is None else kwargs
    return SimpleNamespace(
        operation=operation,
        helper=helper,
        flags=flags,
        text_model=text_model,
        serialized_args=lambda: list(args),
        serialized_kwargs=lambda: serialized_kwargs,
    )


def _compile_search_fullmatch_workload(
    *,
    operation: str,
    flags: int = 0,
    text_model: str = "str",
) -> object:
    return SimpleNamespace(
        operation=operation,
        flags=flags,
        text_model=text_model,
    )


@cache
def _parsed_module_ast(module: object) -> ast.Module:
    return ast.parse(inspect.getsource(module))


@cache
def _parsed_source_tree_combined_suite_ast() -> ast.Module:
    return ast.parse(
        (
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / "test_source_tree_combined_boundary_benchmarks.py"
        ).read_text()
    )


def _owner_definition_manifest_path_names(
    function_name: str,
) -> tuple[tuple[str, ...], ...]:
    builder = next(
        node
        for node in _parsed_module_ast(support).body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    )
    builder_return = next(
        node for node in builder.body if isinstance(node, ast.Return)
    )

    assert isinstance(builder_return.value, ast.Tuple)

    manifest_path_names: list[tuple[str, ...]] = []
    for element in builder_return.value.elts:
        assert isinstance(element, ast.Call)
        manifest_paths_keyword = next(
            keyword
            for keyword in element.keywords
            if keyword.arg == "manifest_paths"
        )
        assert isinstance(manifest_paths_keyword.value, ast.Tuple)
        assert all(
            isinstance(manifest_path, ast.Name)
            for manifest_path in manifest_paths_keyword.value.elts
        )
        manifest_path_names.append(
            tuple(
                manifest_path.id
                for manifest_path in manifest_paths_keyword.value.elts
            )
        )

    return tuple(manifest_path_names)


def _report_workload(
    *,
    workload_id: str,
    operation: str,
    family: str,
) -> object:
    return SimpleNamespace(
        workload_id=workload_id,
        operation=operation,
        family=family,
    )


def _report_manifest(
    *,
    manifest_id: str,
    workloads: tuple[object, ...],
    smoke_workload_ids: tuple[str, ...] = (),
    spec_refs: tuple[str, ...] = (),
    schema_version: int = 1,
    notes: str | None = None,
) -> object:
    workload_by_id = {
        workload.workload_id: workload
        for workload in workloads
    }

    def _selected_workloads(
        selected_workload_ids: tuple[str, ...] | None = None,
    ) -> tuple[object, ...]:
        if selected_workload_ids is None:
            return workloads
        return tuple(
            workload_by_id[workload_id]
            for workload_id in selected_workload_ids
        )

    return SimpleNamespace(
        manifest_id=manifest_id,
        schema_version=schema_version,
        workloads=workloads,
        smoke_workload_ids=lambda: smoke_workload_ids,
        spec_refs=spec_refs,
        notes=notes,
        selected_workloads=_selected_workloads,
    )


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

    assert benchmark_support.freeze_signature_value(value) == (
        ("a", (("x", 0), ("y", 1))),
        ("b", (2, (("c", (5, 6)), ("d", 4)))),
    )
    assert support.freeze_signature_value is benchmark_support.freeze_signature_value


def test_definition_anchor_expectations_expand_manifest_name() -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")

    assert benchmark_support._definition_anchor_expectations(
        manifest_path,
        {
            "workload-a": ("case-1", "case-2"),
            "workload-b": ("case-3",),
        },
    ) == {
        ("synthetic_boundary.py", "workload-a"): ("case-1", "case-2"),
        ("synthetic_boundary.py", "workload-b"): ("case-3",),
    }
    assert (
        support._definition_anchor_expectations
        is benchmark_support._definition_anchor_expectations
    )


def test_workload_case_pair_helpers_preserve_tuple_order() -> None:
    workload_case_pairs = (
        ("workload-a", "case-1"),
        ("workload-b", "case-2"),
        ("workload-c", "case-3"),
    )

    assert benchmark_support._workload_case_pairs_workload_ids(workload_case_pairs) == (
        "workload-a",
        "workload-b",
        "workload-c",
    )
    assert benchmark_support._workload_case_pairs_case_ids(workload_case_pairs) == (
        "case-1",
        "case-2",
        "case-3",
    )
    assert (
        support._workload_case_pairs_workload_ids
        is benchmark_support._workload_case_pairs_workload_ids
    )
    assert (
        support._workload_case_pairs_case_ids
        is benchmark_support._workload_case_pairs_case_ids
    )


def test_workload_case_pair_anchor_expectations_wrap_each_case_id() -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workload_case_pairs = (
        ("workload-a", "case-1"),
        ("workload-b", "case-2"),
    )

    assert benchmark_support._workload_case_pair_anchor_expectations(
        manifest_path,
        workload_case_pairs,
    ) == {
        ("synthetic_boundary.py", "workload-a"): ("case-1",),
        ("synthetic_boundary.py", "workload-b"): ("case-2",),
    }
    assert (
        support._workload_case_pair_anchor_expectations
        is benchmark_support._workload_case_pair_anchor_expectations
    )


def test_source_tree_combined_representative_workload_ids_prefer_explicit_manifest_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest_id = "synthetic-boundary"
    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
        {
            manifest_id: support.SourceTreeCombinedManifestExpectationDefinition(
                representative_measured_workload_ids=("explicit-a", "explicit-b"),
                shape_expectation=support.SourceTreeCombinedManifestShapeExpectation(
                    representative_measured_workload_ids=("shape-a",),
                ),
            ),
        },
    )
    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS",
        (
            support.SourceTreeCombinedSliceExpectation(
                manifest_id=manifest_id,
                slice_id="slice-a",
                expected_workload_ids=("slice-a", "slice-b"),
            ),
        ),
    )

    assert support.source_tree_combined_manifest_representative_measured_workload_ids(
        manifest_id
    ) == ("explicit-a", "explicit-b")


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
                    representative_measured_workload_ids=("shape-a", "shared"),
                ),
            ),
        },
    )
    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS",
        (
            support.SourceTreeCombinedSliceExpectation(
                manifest_id=manifest_id,
                slice_id="slice-a",
                expected_workload_ids=("shared", "slice-a"),
            ),
            support.SourceTreeCombinedSliceExpectation(
                manifest_id="other-boundary",
                slice_id="ignored",
                expected_workload_ids=("other",),
            ),
            support.SourceTreeCombinedSliceExpectation(
                manifest_id=manifest_id,
                slice_id="slice-b",
                expected_workload_ids=("slice-a", "slice-b", "shape-a"),
            ),
        ),
    )

    assert support.source_tree_combined_manifest_representative_measured_workload_ids(
        manifest_id
    ) == ("shape-a", "shared", "slice-a", "slice-b")


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


def test_source_tree_combined_slice_manifest_ids_rejects_expectations_outside_selector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        support,
        "source_tree_combined_target_manifest_ids",
        lambda: ("module-boundary",),
    )
    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS",
        (
            support.SourceTreeCombinedSliceExpectation(
                manifest_id="module-boundary",
                slice_id="module-slice",
            ),
            support.SourceTreeCombinedSliceExpectation(
                manifest_id="synthetic-boundary",
                slice_id="synthetic-slice",
            ),
        ),
    )

    with pytest.raises(
        AssertionError,
        match=(
            "source-tree combined slice expectations reference manifest ids outside "
            "the published combined selector: \\['synthetic-boundary'\\]"
        ),
    ):
        support.source_tree_combined_slice_manifest_ids()


@pytest.mark.parametrize(
    ("manifest_expectations", "manifest_id", "message"),
    (
        pytest.param(
            {},
            "synthetic-missing",
            "unknown source-tree combined manifest expectation 'synthetic-missing'",
            id="unknown-manifest",
        ),
        pytest.param(
            {
                "synthetic-no-shape": (
                    support.SourceTreeCombinedManifestExpectationDefinition()
                ),
            },
            "synthetic-no-shape",
            (
                "source-tree combined manifest 'synthetic-no-shape' does not define "
                "shared shape expectations"
            ),
            id="missing-shape",
        ),
    ),
)
def test_source_tree_combined_manifest_shape_expectation_rejects_invalid_manifests(
    monkeypatch: pytest.MonkeyPatch,
    manifest_expectations: dict[
        str, support.SourceTreeCombinedManifestExpectationDefinition
    ],
    manifest_id: str,
    message: str,
) -> None:
    support.source_tree_combined_manifest_shape_expectation.cache_clear()
    monkeypatch.setattr(
        support,
        "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
        manifest_expectations,
    )

    with pytest.raises(AssertionError, match=message):
        support.source_tree_combined_manifest_shape_expectation(manifest_id)

    support.source_tree_combined_manifest_shape_expectation.cache_clear()


@pytest.mark.parametrize(
    ("case", "pattern", "expected"),
    (
        pytest.param(
            _compile_search_fullmatch_case(
                operation="compile",
                kwargs={"window": [1, 3]},
            ),
            "a((b))d",
            ("module.compile", "a((b))d", (), (("window", (1, 3)),), 0, "str"),
            id="compile-defaults",
        ),
        pytest.param(
            _compile_search_fullmatch_case(
                operation="module_call",
                helper="search",
                args=(b"a((b))d", b"zzabdzz"),
                kwargs={"pos": [1, 4]},
                flags=4,
                text_model="bytes",
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
            _compile_search_fullmatch_case(
                operation="pattern_call",
                helper="fullmatch",
                args=(b"abd",),
                kwargs={"endpos": [3]},
                flags=2,
                text_model="bytes",
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
            _compile_search_fullmatch_case(
                operation="module_call",
                helper="match",
                args=("zzabdzz",),
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
            _compile_search_fullmatch_workload(operation="module.compile"),
            "a((b))d",
            ("unused-search",),
            ("unused-fullmatch",),
            ("module.compile", "a((b))d", (), (), 0, "str"),
            id="compile",
        ),
        pytest.param(
            _compile_search_fullmatch_workload(
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
            _compile_search_fullmatch_workload(
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
    workload = _compile_search_fullmatch_workload(operation="pattern.search")

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
                "_workload_case_pairs_case_ids",
                "_workload_case_pairs_workload_ids",
            ),
            id="collection-replacement",
        ),
    ),
)
def test_former_owner_modules_share_source_tree_helpers_without_local_duplicates(
    owner_module: object,
    helper_names: tuple[str, ...],
) -> None:
    local_function_names = {
        node.name
        for node in _parsed_module_ast(owner_module).body
        if isinstance(node, ast.FunctionDef)
    }

    for helper_name in helper_names:
        assert getattr(owner_module, helper_name) is getattr(benchmark_support, helper_name)
        assert helper_name not in local_function_names


def test_source_tree_support_module_exposes_moved_combined_case_surface() -> None:
    local_class_names = {
        node.name
        for node in _parsed_module_ast(support).body
        if isinstance(node, ast.ClassDef)
    }
    local_function_names = {
        node.name
        for node in _parsed_module_ast(support).body
        if isinstance(node, ast.FunctionDef)
    }
    local_assignment_names = {
        target.id
        for node in _parsed_module_ast(support).body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }

    for class_name in _MOVED_SOURCE_TREE_CLASS_NAMES:
        assert hasattr(support, class_name)
        assert class_name in local_class_names
    for function_name in _MOVED_SOURCE_TREE_FUNCTION_NAMES:
        assert hasattr(support, function_name)
        assert function_name in local_function_names
    for constant_name in _MOVED_SOURCE_TREE_CONSTANT_NAMES:
        assert hasattr(support, constant_name)
        assert constant_name in local_assignment_names


def test_source_tree_support_module_exposes_moved_report_contract_helpers() -> None:
    local_function_names = {
        node.name
        for node in _parsed_module_ast(support).body
        if isinstance(node, ast.FunctionDef)
    }

    for function_name in _MOVED_REPORT_CONTRACT_HELPER_NAMES:
        assert hasattr(support, function_name)
        assert function_name in local_function_names


def test_source_tree_support_module_exposes_moved_conditional_callable_helpers() -> None:
    local_function_names = {
        node.name
        for node in _parsed_module_ast(support).body
        if isinstance(node, ast.FunctionDef)
    }

    for function_name in _MOVED_CONDITIONAL_CALLABLE_HELPER_NAMES:
        assert hasattr(support, function_name)
        assert function_name in local_function_names


def test_combined_suite_no_longer_defines_moved_source_tree_case_surface_locally() -> None:
    local_class_names = {
        node.name
        for node in _parsed_source_tree_combined_suite_ast().body
        if isinstance(node, ast.ClassDef)
    }
    local_function_names = {
        node.name
        for node in _parsed_source_tree_combined_suite_ast().body
        if isinstance(node, ast.FunctionDef)
    }

    for class_name in _MOVED_SOURCE_TREE_CLASS_NAMES:
        assert class_name not in local_class_names
    for function_name in _MOVED_SOURCE_TREE_FUNCTION_NAMES:
        assert function_name not in local_function_names


def test_combined_suite_no_longer_defines_moved_report_contract_helpers_locally() -> None:
    local_function_names = {
        node.name
        for node in _parsed_source_tree_combined_suite_ast().body
        if isinstance(node, ast.FunctionDef)
    }

    for function_name in _MOVED_REPORT_CONTRACT_HELPER_NAMES:
        assert function_name not in local_function_names


def test_combined_suite_no_longer_defines_moved_conditional_callable_helpers_locally(
) -> None:
    local_function_names = {
        node.name
        for node in _parsed_source_tree_combined_suite_ast().body
        if isinstance(node, ast.FunctionDef)
    }

    for function_name in _MOVED_CONDITIONAL_CALLABLE_HELPER_NAMES:
        assert function_name not in local_function_names


def test_moved_conditional_callable_expectation_helpers_pin_current_slice_ids() -> None:
    expected_callable_slice_ids = (
        "minimal-callable-replacement-rows",
        "minimal-callable-replacement-exception-rows",
        "minimal-callable-replacement-none-count-exception-rows",
        "alternation-heavy-callable-replacement-rows",
    )
    callable_expectations = (
        support._conditional_group_exists_callable_replacement_expectations()
    )

    assert (
        support._conditional_group_exists_template_replacement_expectation().slice_id
        == "minimal-template-replacement-rows"
    )
    assert tuple(
        expectation.slice_id for expectation in callable_expectations
    ) == expected_callable_slice_ids
    assert {
        expectation.manifest_id for expectation in callable_expectations
    } == {"conditional-group-exists-boundary"}
    assert (
        support._conditional_group_exists_alternation_callable_replacement_expectation().slice_id
        == "alternation-heavy-callable-replacement-rows"
    )
    assert (
        support._conditional_group_exists_nested_callable_replacement_expectation().slice_id
        == "nested-callable-replacement-str-rows"
    )
    assert (
        support._conditional_group_exists_nested_callable_bytes_replacement_expectation().slice_id
        == "nested-callable-replacement-bytes-rows"
    )
    assert (
        support._conditional_group_exists_quantified_callable_replacement_expectation().slice_id
        == "quantified-callable-replacement-str-rows"
    )
    assert (
        support._conditional_group_exists_quantified_callable_bytes_replacement_expectation().slice_id
        == "quantified-callable-replacement-bytes-rows"
    )


def test_moved_conditional_callable_workload_loaders_pin_expected_ids() -> None:
    callable_expectations = (
        support._conditional_group_exists_callable_replacement_expectations()
    )
    expected_callable_workload_ids = tuple(
        workload_id
        for expectation in callable_expectations
        for workload_id in expectation.expected_workload_ids
    )
    expected_callable_str_workload_ids, expected_callable_bytes_workload_ids = (
        support._split_workload_ids_by_text_model(expected_callable_workload_ids)
    )

    callable_str_workloads = support._conditional_group_exists_callable_str_slice_workloads()
    callable_bytes_workloads = (
        support._conditional_group_exists_callable_bytes_slice_workloads()
    )
    nested_str_workloads = support._conditional_group_exists_nested_callable_str_workloads()
    nested_bytes_workloads = (
        support._conditional_group_exists_nested_callable_bytes_workloads()
    )
    quantified_str_workloads = (
        support._conditional_group_exists_quantified_callable_str_workloads()
    )
    quantified_bytes_workloads = (
        support._conditional_group_exists_quantified_callable_bytes_workloads()
    )
    alternation_bytes_workloads = (
        support._conditional_group_exists_alternation_callable_bytes_workloads()
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
        for expectation in support._conditional_group_exists_callable_replacement_expectations()
        for workload_id in expectation.expected_workload_ids
    )
    synthetic_workloads = (
        synthetic_workload(
            manifest_id="conditional-group-exists-boundary",
            workload_id="callable-negative-count-warm-str",
            operation="module.sub",
            text_model="str",
            categories=["callable", "negative-count", "replacement"],
        ),
        synthetic_workload(
            manifest_id="conditional-group-exists-boundary",
            workload_id="callable-negative-count-warm-bytes",
            operation="module.sub",
            text_model="bytes",
            categories=["callable", "negative-count", "replacement"],
        ),
        synthetic_workload(
            manifest_id="conditional-group-exists-boundary",
            workload_id="callable-negative-none-count-warm-str",
            operation="module.sub",
            text_model="str",
            categories=["callable", "negative-count", "none-count", "replacement"],
        ),
        synthetic_workload(
            manifest_id="conditional-group-exists-boundary",
            workload_id="callable-no-match-warm-str",
            operation="module.sub",
            text_model="str",
            categories=["callable", "no-match", "replacement"],
        ),
    )

    assert support._split_workload_ids_by_text_model(
        expected_callable_workload_ids
    ) == (
        tuple(
            workload_id
            for workload_id in expected_callable_workload_ids
            if not workload_id.endswith("-bytes")
        ),
        tuple(
            workload_id
            for workload_id in expected_callable_workload_ids
            if workload_id.endswith("-bytes")
        ),
    )
    assert support._mirrored_bytes_workload_ids(
        collection_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
    ) == (
        collection_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS
    )
    assert support._selected_workload_ids(
        synthetic_workloads,
        text_model="str",
        required_categories=("negative-count",),
    ) == (
        "callable-negative-count-warm-str",
        "callable-negative-none-count-warm-str",
    )
    assert support._selected_workload_ids(
        synthetic_workloads,
        text_model="str",
        required_categories=("negative-count",),
        excluded_categories=("none-count",),
    ) == ("callable-negative-count-warm-str",)
    assert support._selected_workload_ids(
        synthetic_workloads,
        text_model="bytes",
        required_categories=("negative-count",),
    ) == ("callable-negative-count-warm-bytes",)
    assert support._selected_workload_ids(
        synthetic_workloads,
        text_model="str",
        required_categories=("no-match",),
    ) == ("callable-no-match-warm-str",)


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

    support._assert_benchmark_summary_consistent(
        unittest.TestCase(),
        scorecard,
        _summary_view(scorecard),
    )


def test_source_tree_report_contract_accepts_single_manifest_native_loaded_scorecard(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
) -> None:
    monkeypatch.setattr(
        support,
        "build_cpython_baseline",
        lambda version_family: {
            "python": "synthetic",
            "version_family": version_family,
        },
    )
    manifest_path = "benchmarks/workloads/synthetic_boundary.py"
    manifest = _report_manifest(
        manifest_id="synthetic-boundary",
        schema_version=7,
        workloads=(
            _report_workload(
                workload_id="module-search-synthetic-warm-str",
                operation="module.search",
                family="module",
            ),
            _report_workload(
                workload_id="module-compile-synthetic-cold-gap",
                operation="module.compile",
                family="parser",
            ),
        ),
        smoke_workload_ids=("module-search-synthetic-warm-str",),
        spec_refs=("docs/spec/synthetic-boundary.md",),
    )
    manifest_record = support._artifact_manifest_record(manifest_path, manifest)
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
        support,
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
    manifests = [
        _report_manifest(
            manifest_id="first-boundary",
            schema_version=3,
            workloads=(
                _report_workload(
                    workload_id="module-search-first-warm-str",
                    operation="module.search",
                    family="module",
                ),
            ),
            smoke_workload_ids=("module-search-first-warm-str",),
            spec_refs=("docs/spec/first-boundary.md",),
        ),
        _report_manifest(
            manifest_id="second-boundary",
            schema_version=5,
            workloads=(
                _report_workload(
                    workload_id="module-compile-second-cold-gap",
                    operation="module.compile",
                    family="parser",
                ),
                _report_workload(
                    workload_id="pattern-fullmatch-second-purged-str",
                    operation="pattern.fullmatch",
                    family="module",
                ),
            ),
            smoke_workload_ids=("module-compile-second-cold-gap",),
            spec_refs=("docs/spec/second-boundary.md",),
        ),
    ]
    manifest_records = [
        support._artifact_manifest_record(manifest_path, manifest)
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
    manifest = _report_manifest(
        manifest_id="synthetic-boundary",
        workloads=(
            _report_workload(
                workload_id="module-compile-synthetic-cold",
                operation="module.compile",
                family="parser",
            ),
            _report_workload(
                workload_id="module-search-synthetic-warm",
                operation="module.search",
                family="module",
            ),
            _report_workload(
                workload_id="pattern-fullmatch-synthetic-purged",
                operation="pattern.fullmatch",
                family="module",
            ),
        ),
        smoke_workload_ids=("module-compile-synthetic-cold",),
        spec_refs=("docs/spec/synthetic-boundary.md",),
        notes="synthetic manifest notes",
    )
    manifest_record = support._artifact_manifest_record(manifest_path, manifest)
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

    support.assert_benchmark_manifest_contract(
        unittest.TestCase(),
        manifest_summary,
        support.find_manifest_record(scorecard, manifest.manifest_id),
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
        support.find_manifest_record(
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


def test_source_tree_owner_manifest_path_constants_point_to_current_workload_files() -> None:
    assert support.MODULE_BOUNDARY_MANIFEST_PATH == SHARED_MODULE_BOUNDARY_MANIFEST_PATH
    assert support.OPTIONAL_GROUP_MANIFEST_PATH == OPTIONAL_GROUP_MANIFEST_PATH
    assert support.NESTED_GROUP_MANIFEST_PATH == NESTED_GROUP_MANIFEST_PATH
    assert support.EXACT_REPEAT_MANIFEST_PATH == EXACT_REPEAT_MANIFEST_PATH
    assert support.RANGED_REPEAT_MANIFEST_PATH == RANGED_REPEAT_MANIFEST_PATH
    assert (
        support.GROUPED_ALTERNATION_MANIFEST_PATH
        == GROUPED_ALTERNATION_MANIFEST_PATH
    )
    assert (
        support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH
        == GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH
    )
    assert (
        support.NESTED_GROUP_REPLACEMENT_MANIFEST_PATH
        == NESTED_GROUP_REPLACEMENT_MANIFEST_PATH
    )
    assert support.OPEN_ENDED_MANIFEST_PATH == OPEN_ENDED_MANIFEST_PATH


@pytest.mark.parametrize(
    ("builder_name", "expected_manifest_path_names"),
    (
        pytest.param(
            "_source_tree_standard_benchmark_definitions",
            (
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
    assert _owner_definition_manifest_path_names(builder_name) == (
        expected_manifest_path_names
    )


def test_source_tree_owner_definition_exports_reuse_owner_manifest_path_constants() -> None:
    assert tuple(
        definition.manifest_paths[0]
        for definition in support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS
    ) == (
        support.OPTIONAL_GROUP_MANIFEST_PATH,
        support.NESTED_GROUP_MANIFEST_PATH,
        support.EXACT_REPEAT_MANIFEST_PATH,
        support.RANGED_REPEAT_MANIFEST_PATH,
        support.GROUPED_ALTERNATION_MANIFEST_PATH,
        support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        support.NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,
        support.OPEN_ENDED_MANIFEST_PATH,
    )


def test_source_tree_standard_definitions_export_stays_owned_by_source_tree() -> None:
    owner_definitions = support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS
    definition_names = tuple(definition.name for definition in owner_definitions)
    assert definition_names == (
        "optional-group-conditional",
        "nested-group",
        "exact-repeat",
        "ranged-repeat",
        "grouped-alternation",
        "grouped-alternation-replacement",
        "nested-group-replacement",
        "open-ended-grouped-alternation",
    )
    standard_definitions = STANDARD_BENCHMARK_DEFINITIONS
    start_index = next(
        index
        for index, definition in enumerate(standard_definitions)
        if definition.name == definition_names[0]
    )
    standard_owner_slice = standard_definitions[
        start_index : start_index + len(owner_definitions)
    ]

    assert tuple(definition.name for definition in standard_owner_slice) == definition_names
    assert standard_owner_slice == owner_definitions
    assert all(
        standard_definition is owner_definition
        for standard_definition, owner_definition in zip(
            standard_owner_slice, owner_definitions, strict=True
        )
    )


def test_optional_group_conditional_helpers_stay_on_the_search_anchor() -> None:
    cases = support.published_cases_by_id()
    workload = live_manifest_workload(
        OPTIONAL_GROUP_MANIFEST_PATH,
        support._OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID,
    )
    non_conditional_workload = live_manifest_workload(
        OPTIONAL_GROUP_MANIFEST_PATH,
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
            _module_pattern_case(
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
            synthetic_workload(
                manifest_id="optional-group-boundary",
                workload_id="optional-group-compile-unsupported",
                operation="module.compile",
                pattern="a(b)?(?(1)c|d)e",
            )
        )


def test_nested_group_live_signatures_cover_numbered_and_named_routes() -> None:
    cases = support.published_cases_by_id()

    assert support._nested_group_correctness_case_signature(
        cases["nested-group-compile-metadata-str"]
    ) == ("module.compile", "a((b))d", (), (), 0, "str")
    assert support._nested_group_workload_signature(
        live_manifest_workload(
            NESTED_GROUP_MANIFEST_PATH,
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
        live_manifest_workload(
            NESTED_GROUP_MANIFEST_PATH,
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
        live_manifest_workload(
            NESTED_GROUP_MANIFEST_PATH,
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
        live_manifest_workload(
            NESTED_GROUP_MANIFEST_PATH,
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
        live_manifest_workload(
            NESTED_GROUP_MANIFEST_PATH,
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
        live_manifest_workload(
            NESTED_GROUP_MANIFEST_PATH,
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
    cases = support.published_cases_by_id()

    assert support._counted_repeat_correctness_case_signature(
        cases["exact-repeat-numbered-group-compile-metadata-str"]
    ) == ("module.compile", "a(bc){2}d", (), (), 0, "str")
    assert support._counted_repeat_workload_signature(
        live_manifest_workload(
            EXACT_REPEAT_MANIFEST_PATH,
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
        live_manifest_workload(
            EXACT_REPEAT_MANIFEST_PATH,
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
        live_manifest_workload(
            RANGED_REPEAT_MANIFEST_PATH,
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
        live_manifest_workload(
            RANGED_REPEAT_MANIFEST_PATH,
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
        live_manifest_workload(
            OPEN_ENDED_MANIFEST_PATH,
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
        live_manifest_workload(
            OPEN_ENDED_MANIFEST_PATH,
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
        live_manifest_workload(
            EXACT_REPEAT_MANIFEST_PATH,
            "module-compile-numbered-exact-repeat-group-cold-str",
        )
    )
    assert support._is_non_alternation_counted_repeat_workload(
        live_manifest_workload(
            RANGED_REPEAT_MANIFEST_PATH,
            "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
        )
    )
    assert not support._is_non_alternation_counted_repeat_workload(
        live_manifest_workload(
            EXACT_REPEAT_MANIFEST_PATH,
            "module-search-numbered-exact-repeat-group-alternation-bc-bc-warm-str",
        )
    )
    assert not support._is_non_alternation_counted_repeat_workload(
        live_manifest_workload(
            OPEN_ENDED_MANIFEST_PATH,
            "module-search-numbered-open-ended-group-broader-range-cold-gap",
        )
    )


def test_published_case_ids_by_signature_groups_duplicate_case_ids(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest = _synthetic_manifest(
        cases=(
            _synthetic_case("case-b", ("shared",)),
            _synthetic_case("case-a", ("shared",)),
            _synthetic_case("case-c", ("unique",)),
            _synthetic_case("ignored", None),
        )
    )
    monkeypatch.setattr(
        benchmark_support,
        "published_fixture_manifests",
        lambda: (manifest,),
    )

    observed = support.published_case_ids_by_signature(lambda case: case.signature)

    assert observed == {
        ("shared",): ("case-a", "case-b"),
        ("unique",): ("case-c",),
    }


def test_source_tree_reuses_shared_published_case_helpers_by_identity() -> None:
    assert (
        support.published_case_ids_by_signature
        is benchmark_support.published_case_ids_by_signature
    )
    assert support.published_cases_by_id is benchmark_support.published_cases_by_id


def test_grouped_alternation_live_signatures_cover_non_replacement_routes() -> None:
    cases = support.published_cases_by_id()

    compile_workload = live_manifest_workload(
        GROUPED_ALTERNATION_MANIFEST_PATH,
        "module-compile-grouped-alternation-cold-str",
    )
    search_workload = live_manifest_workload(
        GROUPED_ALTERNATION_MANIFEST_PATH,
        "module-search-grouped-alternation-warm-str",
    )
    fullmatch_workload = live_manifest_workload(
        GROUPED_ALTERNATION_MANIFEST_PATH,
        "pattern-fullmatch-grouped-alternation-purged-str",
    )
    legacy_module_sub_workload = live_manifest_workload(
        GROUPED_ALTERNATION_MANIFEST_PATH,
        "module-sub-template-nested-grouped-alternation-warm-gap",
    )
    legacy_pattern_subn_workload = live_manifest_workload(
        GROUPED_ALTERNATION_MANIFEST_PATH,
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
    cases = support.published_cases_by_id()

    module_sub_workload = live_manifest_workload(
        GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        "module-sub-template-grouped-alternation-warm-str",
    )
    module_subn_workload = live_manifest_workload(
        GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        "module-subn-template-named-grouped-alternation-warm-str",
    )
    pattern_sub_workload = live_manifest_workload(
        GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        "pattern-sub-template-grouped-alternation-purged-str",
    )
    pattern_subn_workload = live_manifest_workload(
        GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
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
    unsupported_workload = synthetic_workload(
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
