from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cache, partial
import pathlib
import re
from typing import Any
import unittest

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    BenchmarkManifest,
    Workload,
    determine_phase,
    determine_runner_version,
    published_benchmark_manifests,
    select_workloads,
    workload_from_payload,
    workload_to_payload,
)
from rebar_harness.scorecard_io import build_cpython_baseline
from tests.benchmarks.benchmark_test_support import (
    _definition_anchor_expectations,
    _workload_case_pair_anchor_expectations,
    assert_benchmark_workload_contract,
    compile_proxy_correctness_case_signature,
    compile_proxy_workload_signature,
    find_workload_document,
    find_workload_record,
    is_compile_proxy_workload,
    live_manifest_workloads,
)
from tests.benchmarks.collection_replacement_benchmark_anchor_support import (
    _COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS,
    _COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES,
    _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR,
    _COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES,
    _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR,
    CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS,
    CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS,
    _collection_replacement_compiled_pattern_success_correctness_case_signature,
    _collection_replacement_compiled_pattern_success_workload_signature,
    _collection_replacement_grouped_callable_correctness_case_signature,
    _collection_replacement_grouped_callable_workload_signature,
    _collection_replacement_literal_replacement_correctness_case_signature,
    _collection_replacement_literal_replacement_workload_signature,
    _collection_replacement_keyword_correctness_case_signature,
    _conditional_group_exists_nested_callable_correctness_case_signature,
    _conditional_group_exists_nested_callable_workload_signature,
    _conditional_group_exists_quantified_callable_correctness_case_signature,
    _conditional_group_exists_quantified_callable_workload_signature,
    _collection_replacement_pattern_wrong_text_model_correctness_case_signature,
    _collection_replacement_pattern_wrong_text_model_workload_signature,
    _is_collection_replacement_compiled_pattern_success_workload,
    _collection_replacement_keyword_workload_signature,
    _collection_replacement_positional_indexlike_workload_signature,
    _collection_replacement_wrong_text_model_correctness_case_signature,
    _collection_replacement_wrong_text_model_workload_signature,
    _is_collection_replacement_keyword_workload,
    _is_collection_replacement_grouped_callable_workload,
    _is_collection_replacement_pattern_wrong_text_model_workload,
    _is_collection_replacement_positional_indexlike_workload,
    _is_collection_replacement_wrong_text_model_workload,
    _module_workflow_positional_indexlike_correctness_case_signature,
    _workload_ids_for_text_model,
)
from tests.benchmarks.pattern_boundary_benchmark_anchor_support import (
    _is_pattern_keyword_window_workload,
    _is_pattern_window_positional_indexlike_workload,
    _pattern_keyword_window_correctness_case_signature,
    _pattern_keyword_window_workload_signature,
    _pattern_window_positional_indexlike_correctness_case_signature,
    _pattern_window_positional_indexlike_workload_signature,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    _is_module_workflow_keyword_error_workload,
    _is_module_workflow_keyword_flags_workload,
    _module_workflow_keyword_correctness_case_signature,
    _module_workflow_keyword_workload_signature,
)
from tests.benchmarks.pattern_boundary_benchmark_anchor_support import (
    _is_pattern_bounded_wildcard_workload,
    _is_pattern_boundary_wrong_text_model_workload,
    _is_pattern_verbose_regression_workload,
    _pattern_bounded_wildcard_correctness_case_signature,
    _pattern_bounded_wildcard_workload_signature,
    _pattern_boundary_wrong_text_model_correctness_case_signature,
    _pattern_boundary_wrong_text_model_workload_signature,
    _pattern_verbose_regression_correctness_case_signature,
    _pattern_verbose_regression_workload_signature,
)
from tests.benchmarks.compiled_pattern_module_compile_benchmark_support import (
    _COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
    _COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
)
from tests.benchmarks.compiled_pattern_module_helper_benchmark_support import (
    _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
    _is_module_workflow_compiled_pattern_literal_success_workload,
    _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
    _module_workflow_compiled_pattern_correctness_case_signature,
    _module_workflow_compiled_pattern_workload_signature,
    _is_module_workflow_compiled_pattern_wrong_text_model_workload,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    _counted_repeat_correctness_case_signature,
    _counted_repeat_workload_signature,
    _grouped_alternation_correctness_case_signature,
    _grouped_alternation_replacement_correctness_case_signature,
    _grouped_alternation_workload_signature,
    _is_non_alternation_counted_repeat_workload,
    assert_benchmark_workload_matches_expected_result,
    _is_optional_group_conditional_workload,
    _nested_group_correctness_case_signature,
    _nested_group_workload_signature,
    _optional_group_correctness_case_signature,
    _optional_group_workload_signature,
    _OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID as OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID,
    published_case_ids_by_signature,
    run_benchmark_workload_with_cpython,
)
from tests.benchmarks.standard_benchmark_anchor_support import (
    STANDARD_BENCHMARK_DEFINITIONS,
    StandardBenchmarkAnchorContractDefinition,
)
from tests.conftest import (
    REPO_ROOT,
    manifest_records_by_id,
    records_by_string_id,
    run_harness_scorecard,
)
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    callable_match_group_signature,
)
TRACKED_REPORT_PATH = benchmarks.SCORECARD_REPORT.published_path

_KNOWN_GAP_STATUSES = {"known-gap", "unimplemented"}


def _assert_benchmark_summary_consistent(
    testcase: Any,
    scorecard: dict[str, Any],
    summary: dict[str, Any],
) -> None:
    workloads = scorecard["workloads"]
    expected_summary = {
        key: scorecard["summary"][key]
        for key in (
            "known_gap_count",
            "measured_workloads",
            "module_workloads",
            "parser_workloads",
            "regression_workloads",
            "total_workloads",
        )
    }
    testcase.assertEqual(summary, expected_summary)
    testcase.assertEqual(summary["total_workloads"], len(workloads))
    testcase.assertEqual(
        summary["measured_workloads"] + summary["known_gap_count"],
        summary["total_workloads"],
    )
    testcase.assertEqual(
        summary["parser_workloads"],
        scorecard["families"]["parser"]["workload_count"],
    )
    testcase.assertEqual(
        summary["module_workloads"],
        scorecard["families"]["module"]["workload_count"],
    )
    testcase.assertEqual(
        summary["regression_workloads"],
        sum(1 for workload in workloads if workload["manifest_id"] == "regression-matrix"),
    )

    for cache_mode, expected_count in scorecard["summary"]["workloads_by_cache_mode"].items():
        testcase.assertEqual(
            expected_count,
            sum(1 for workload in workloads if workload["cache_mode"] == cache_mode),
        )

    if summary["measured_workloads"] > 0:
        testcase.assertIsInstance(scorecard["summary"]["baseline_median_ns"], int)
        testcase.assertGreater(scorecard["summary"]["baseline_median_ns"], 0)
        testcase.assertGreater(scorecard["summary"]["baseline_median_ops_per_second"], 0)
        testcase.assertIsInstance(scorecard["summary"]["implementation_median_ns"], int)
        testcase.assertGreater(scorecard["summary"]["implementation_median_ns"], 0)
        testcase.assertGreater(
            scorecard["summary"]["implementation_median_ops_per_second"],
            0,
        )

    for family_id, family_summary in scorecard["families"].items():
        family_workloads = [workload for workload in workloads if workload["family"] == family_id]
        testcase.assertEqual(family_summary["workload_count"], len(family_workloads))
        testcase.assertEqual(
            family_summary["known_gap_count"],
            sum(
                1
                for workload in family_workloads
                if workload["status"] in _KNOWN_GAP_STATUSES
            ),
        )
        for cache_mode, cache_summary in family_summary["cache_modes"].items():
            testcase.assertEqual(
                cache_summary["workload_count"],
                sum(
                    1
                    for workload in family_workloads
                    if workload["cache_mode"] == cache_mode
                ),
            )

    for cache_mode, cache_summary in scorecard["cache_modes"].items():
        cache_workloads = [workload for workload in workloads if workload["cache_mode"] == cache_mode]
        testcase.assertEqual(cache_summary["workload_count"], len(cache_workloads))
        testcase.assertEqual(
            cache_summary["known_gap_count"],
            sum(1 for workload in cache_workloads if workload["status"] in _KNOWN_GAP_STATUSES),
        )


def _artifact_manifest_record(
    manifest_path: str,
    manifest: BenchmarkManifest,
) -> dict[str, Any]:
    return {
        "manifest": manifest_path,
        "manifest_id": manifest.manifest_id,
        "manifest_schema_version": manifest.schema_version,
        "workload_count": len(manifest.workloads),
        "smoke_workload_ids": manifest.smoke_workload_ids(),
        "spec_refs": list(manifest.spec_refs),
    }


def assert_source_tree_benchmark_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    summary: dict[str, Any],
    *,
    expected_phase: str,
    expected_runner_version: str,
    expected_adapter: str,
    expected_manifests: list[BenchmarkManifest],
    expected_manifest_paths: list[str],
    expected_selection_mode: str,
    tracked_report_path: pathlib.Path | None = None,
) -> None:
    expected_manifest_records = [
        _artifact_manifest_record(manifest_path, manifest)
        for manifest_path, manifest in zip(
            expected_manifest_paths,
            expected_manifests,
            strict=True,
        )
    ]

    _assert_benchmark_summary_consistent(testcase, scorecard, summary)
    testcase.assertEqual(scorecard["schema_version"], "1.0")
    testcase.assertEqual(scorecard["suite"], "benchmarks")
    testcase.assertEqual(scorecard["phase"], expected_phase)
    expected_baseline = {
        **build_cpython_baseline(version_family="3.12.x"),
        "re_module": "re",
    }
    for key, expected_value in expected_baseline.items():
        testcase.assertEqual(scorecard["baseline"][key], expected_value)
    testcase.assertEqual(scorecard["implementation"]["module_name"], "rebar")
    testcase.assertEqual(scorecard["implementation"]["adapter"], expected_adapter)
    testcase.assertEqual(
        scorecard["implementation"]["adapter_mode_requested"],
        "source-tree-shim",
    )
    testcase.assertEqual(
        scorecard["implementation"]["adapter_mode_resolved"],
        "source-tree-shim",
    )
    testcase.assertEqual(scorecard["implementation"]["build_mode"], "source-tree-shim")
    testcase.assertEqual(scorecard["implementation"]["timing_path"], "source-tree-shim")
    testcase.assertIsNone(scorecard["implementation"]["native_build_tool"])
    testcase.assertIsNone(scorecard["implementation"]["native_wheel"])
    testcase.assertIsInstance(scorecard["implementation"]["native_module_loaded"], bool)
    testcase.assertEqual(scorecard["implementation"]["native_module_name"], "rebar._rebar")
    if scorecard["implementation"]["native_module_loaded"]:
        testcase.assertEqual(scorecard["implementation"]["native_scaffold_status"], "scaffold-only")
        testcase.assertEqual(
            scorecard["implementation"]["native_target_cpython_series"],
            "3.12.x",
        )
    else:
        testcase.assertIsNone(scorecard["implementation"]["native_scaffold_status"])
        testcase.assertIsNone(
            scorecard["implementation"]["native_target_cpython_series"]
        )
    testcase.assertIn(
        "not requested",
        scorecard["implementation"]["native_unavailable_reason"],
    )
    testcase.assertEqual(scorecard["environment"]["runner_version"], expected_runner_version)
    testcase.assertEqual(
        scorecard["environment"]["execution_model"],
        "single-process in-process adapter comparison",
    )
    testcase.assertEqual(scorecard["artifacts"]["selection_mode"], expected_selection_mode)
    testcase.assertIsNone(scorecard["artifacts"]["raw_samples"])
    testcase.assertEqual(scorecard["artifacts"]["manifests"], expected_manifest_records)
    if len(expected_manifest_records) == 1:
        testcase.assertEqual(
            scorecard["artifacts"]["manifest"],
            expected_manifest_records[0]["manifest"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["manifest_id"],
            expected_manifest_records[0]["manifest_id"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["manifest_schema_version"],
            expected_manifest_records[0]["manifest_schema_version"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["workload_count"],
            expected_manifest_records[0]["workload_count"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["smoke_workload_ids"],
            expected_manifest_records[0]["smoke_workload_ids"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["spec_refs"],
            expected_manifest_records[0]["spec_refs"],
        )
    else:
        testcase.assertEqual(scorecard["artifacts"]["manifest"], None)
        testcase.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        testcase.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
    if tracked_report_path is not None:
        testcase.assertTrue(tracked_report_path.is_file())


def assert_benchmark_manifest_contract(
    testcase: Any,
    manifest_summary: dict[str, Any],
    manifest_record: dict[str, Any],
    *,
    manifest: BenchmarkManifest,
    manifest_path: str,
    known_gap_count: int,
    selection_mode: str = "full",
    selected_workload_ids: tuple[str, ...] | None = None,
) -> None:
    workloads = list(manifest.workloads)
    selected_workloads = manifest.selected_workloads(
        selected_workload_ids=selected_workload_ids
    )
    smoke_ids = manifest.smoke_workload_ids()
    operations = sorted({workload.operation for workload in selected_workloads})
    families = sorted({workload.family for workload in selected_workloads})

    testcase.assertEqual(manifest_summary["workload_count"], len(workloads))
    testcase.assertEqual(manifest_summary["selected_workload_count"], len(selected_workloads))
    testcase.assertEqual(
        manifest_summary["measured_workloads"],
        len(selected_workloads) - known_gap_count,
    )
    testcase.assertEqual(manifest_summary["known_gap_count"], known_gap_count)
    testcase.assertEqual(
        manifest_summary["readiness"],
        "measured" if known_gap_count == 0 else "partial",
    )
    testcase.assertEqual(manifest_summary["selection_mode"], selection_mode)
    testcase.assertEqual(manifest_summary["available_smoke_workload_count"], len(smoke_ids))
    testcase.assertEqual(manifest_summary["smoke_workload_ids"], smoke_ids)
    testcase.assertEqual(manifest_summary["families"], families)
    testcase.assertEqual(manifest_summary["operations"], operations)
    testcase.assertEqual(manifest_summary["spec_refs"], manifest.spec_refs)
    if manifest.notes:
        testcase.assertEqual(manifest_summary["notes"], manifest.notes)

    testcase.assertEqual(manifest_record["manifest_id"], manifest.manifest_id)
    testcase.assertEqual(manifest_record["manifest"], manifest_path)
    testcase.assertEqual(manifest_record["smoke_workload_ids"], smoke_ids)


def find_manifest_record(scorecard: dict[str, Any], manifest_id: str) -> dict[str, Any]:
    for manifest_record in scorecard["artifacts"]["manifests"]:
        if str(manifest_record["manifest_id"]) == manifest_id:
            return manifest_record
    raise AssertionError(f"missing manifest record for {manifest_id!r}")

@dataclass(frozen=True, slots=True)
class SourceTreeBenchmarkCommonCase:
    expected_adapter: str
    expected_phase: str
    expected_runner_version: str
    expected_summary: dict[str, int]
    manifests: list[BenchmarkManifest]
    selection_mode: str

    def manifest_for_id(self, manifest_id: str) -> BenchmarkManifest:
        for manifest in self.manifests:
            if manifest.manifest_id == manifest_id:
                return manifest
        raise AssertionError(f"unknown source-tree benchmark manifest {manifest_id!r}")

    def selected_workload_ids_for_manifest(self, manifest_id: str) -> tuple[str, ...]:
        return _selected_source_tree_manifest_workload_ids(
            self.manifest_for_id(manifest_id),
            selection_mode=self.selection_mode,
        )


@dataclass(frozen=True, slots=True)
class SourceTreeManifestExpectation:
    known_gap_count: int
    representative_measured_workload_ids: tuple[str, ...] = ()
    representative_known_gap_workload_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SourceTreeDeferredExpectation:
    area: str
    follow_up: str


@dataclass(frozen=True, slots=True)
class SourceTreeScorecardCase(SourceTreeBenchmarkCommonCase):
    case_id: str
    manifest_expectations: dict[str, SourceTreeManifestExpectation]
    representative_measured_workload_ids: tuple[str, ...]
    representative_known_gap_workload_ids: tuple[str, ...]
    expected_first_deferred: SourceTreeDeferredExpectation | None = None
    expected_workload_order: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class _SourceTreeScorecardDefinition:
    manifest_ids: tuple[str, ...]
    selection_mode: str = "full"
    representative_measured_workload_ids: tuple[str, ...] = ()
    representative_known_gap_workload_ids: tuple[str, ...] = ()
    expected_first_deferred: SourceTreeDeferredExpectation | None = None
    expected_workload_order: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedCase(SourceTreeBenchmarkCommonCase):
    manifest_expectation: SourceTreeManifestExpectation
    manifest_id: str
    target_manifest: BenchmarkManifest


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedPatternGroupExpectation:
    slice_id: str
    patterns: tuple[str, ...]
    minimum_rows: int
    required_operations: tuple[str, ...]
    required_categories: tuple[str, ...]
    search_haystacks: tuple[str, ...]
    search_haystack_substrings: tuple[str, ...]
    pattern_haystacks: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedManifestShapeExpectation:
    representative_measured_workload_ids: tuple[str, ...]
    pattern_groups: tuple[SourceTreeCombinedPatternGroupExpectation, ...] = ()


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedFullyMeasuredManifestExpectation:
    coverage_group: str
    representative_measured_workload_ids: tuple[str, ...]
    expected_measured_workload_count: int
    expected_total_workload_count: int | None = None


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedManifestExpectationDefinition:
    exclude_from_combined_targets: bool = False
    promote_zero_gap_representatives: bool = False
    known_gap_workload_ids: tuple[str, ...] | None = None
    representative_measured_workload_ids: tuple[str, ...] | None = None
    representative_known_gap_workload_ids: tuple[str, ...] | None = None
    fully_measured_expectation: SourceTreeCombinedFullyMeasuredManifestExpectation | None = None
    shape_expectation: SourceTreeCombinedManifestShapeExpectation | None = None
    zero_gap_bytes_representative_subsets: tuple[tuple[str, ...], ...] = ()


def _text_model_agnostic_callable_match_group_signature(
    replacement: object,
) -> tuple[object, ...] | None:
    signature = callable_match_group_signature(replacement)
    if signature is None:
        return None
    return tuple(
        value.decode("utf-8") if isinstance(value, bytes) else value
        for value in signature
    )


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedSliceExpectation:
    manifest_id: str
    slice_id: str
    required_syntax_features: tuple[str, ...] = ()
    excluded_syntax_features: tuple[str, ...] = ()
    required_categories: tuple[str, ...] = ()
    excluded_categories: tuple[str, ...] = ()
    required_id_suffix: str | None = None
    expected_workload_ids: tuple[str, ...] = ()
    expected_patterns: frozenset[str] = frozenset()
    expected_operations: frozenset[str] = frozenset()
    expected_haystacks: frozenset[str] = frozenset()
    required_row_categories: tuple[str, ...] = ()
    expected_status: str = "measured"


SOURCE_TREE_SCORECARD_EXPECTATIONS = {
    "compile-matrix": _SourceTreeScorecardDefinition(
        manifest_ids=("compile-matrix",),
        expected_first_deferred=SourceTreeDeferredExpectation(
            area="module-boundary",
            follow_up="RBR-0015",
        ),
        representative_measured_workload_ids=(
            "compile-inline-locale-bytes-warm",
            "compile-lookbehind-cold",
            "compile-atomic-group-purged",
            "compile-parser-stress-cold",
        ),
    ),
    "post-parser-workflows": _SourceTreeScorecardDefinition(
        manifest_ids=(
            "module-boundary",
            "collection-replacement-boundary",
            "literal-flag-boundary",
        ),
        representative_measured_workload_ids=(
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
            "module-search-grouped-literal-cold-hit",
            "module-search-flags-keyword-warm-str",
            "module-search-duplicate-flags-keyword-warm-str",
            "module-match-flags-keyword-purged-bytes",
            "module-fullmatch-flags-keyword-warm-str",
            "module-fullmatch-unexpected-keyword-purged-str",
            "module-findall-single-dot-warm-str",
            "module-sub-template-warm-str",
            "module-sub-callable-grouped-warm-str",
            "pattern-subn-grouped-template-warm-str",
            "pattern-subn-callable-named-grouped-warm-str",
            "module-search-inline-flag-warm-str-hit",
            "pattern-search-inline-flag-warm-str-hit",
            "module-search-locale-purged-bytes-hit",
            "pattern-search-locale-purged-bytes-hit",
            "module-search-ignorecase-ascii-cold-gap",
            "pattern-search-ignorecase-ascii-warm-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "numbered-backreference-boundary": _SourceTreeScorecardDefinition(
        manifest_ids=("numbered-backreference-boundary",),
    ),
    "nested-group-boundary": _SourceTreeScorecardDefinition(
        manifest_ids=("nested-group-boundary",),
    ),
    "nested-group-replacement-boundary": _SourceTreeScorecardDefinition(
        manifest_ids=("nested-group-replacement-boundary",),
    ),
    "nested-group-callable-replacement-boundary": _SourceTreeScorecardDefinition(
        manifest_ids=("nested-group-callable-replacement-boundary",),
    ),
    "branch-local-backreference-boundary": _SourceTreeScorecardDefinition(
        manifest_ids=("branch-local-backreference-boundary",),
    ),
    "conditional-group-exists-boundary": _SourceTreeScorecardDefinition(
        manifest_ids=("conditional-group-exists-boundary",),
    ),
    "regression-pack-full": _SourceTreeScorecardDefinition(
        manifest_ids=(
            "compile-matrix",
            "module-boundary",
            "regression-matrix",
        ),
        representative_measured_workload_ids=(
            "compile-inline-locale-bytes-warm",
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
            "regression-import-cold",
            "regression-parser-bytes-backreference-purged",
            "regression-module-compile-multiline-purged",
            "regression-module-compile-multiline-purged-bytes",
            "regression-module-compile-verbose-purged-bytes",
            "regression-module-search-bytes-cold-miss",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "regression-pack-smoke": _SourceTreeScorecardDefinition(
        manifest_ids=("regression-matrix",),
        selection_mode="smoke",
        expected_workload_order=(
            "regression-import-cold",
            "regression-parser-atomic-lookbehind-cold",
        ),
        representative_measured_workload_ids=(
            "regression-import-cold",
            "regression-parser-atomic-lookbehind-cold",
        ),
        representative_known_gap_workload_ids=(),
    ),
}

def _combined_manifest_definition(
    *,
    exclude_from_combined_targets: bool = False,
    promote_zero_gap_representatives: bool = False,
    known_gap_workload_ids: tuple[str, ...] | None = None,
    representative_measured_workload_ids: tuple[str, ...] | None = None,
    representative_known_gap_workload_ids: tuple[str, ...] | None = None,
    fully_measured_expectation: SourceTreeCombinedFullyMeasuredManifestExpectation
    | None = None,
    shape_expectation: SourceTreeCombinedManifestShapeExpectation | None = None,
    zero_gap_bytes_representative_subsets: tuple[tuple[str, ...], ...] = (),
) -> SourceTreeCombinedManifestExpectationDefinition:
    if fully_measured_expectation is not None:
        if representative_measured_workload_ids is None:
            representative_measured_workload_ids = (
                fully_measured_expectation.representative_measured_workload_ids
            )
        elif (
            representative_measured_workload_ids
            != fully_measured_expectation.representative_measured_workload_ids
        ):
            raise AssertionError(
                "fully measured manifest definitions must keep their "
                "representative rows on the shared definition-owned contract"
            )
    return SourceTreeCombinedManifestExpectationDefinition(
        exclude_from_combined_targets=exclude_from_combined_targets,
        promote_zero_gap_representatives=promote_zero_gap_representatives,
        known_gap_workload_ids=known_gap_workload_ids,
        representative_measured_workload_ids=representative_measured_workload_ids,
        representative_known_gap_workload_ids=representative_known_gap_workload_ids,
        fully_measured_expectation=fully_measured_expectation,
        shape_expectation=shape_expectation,
        zero_gap_bytes_representative_subsets=tuple(
            tuple(str(workload_id) for workload_id in workload_ids)
            for workload_ids in zero_gap_bytes_representative_subsets
        ),
    )


def _combined_fully_measured_manifest_expectation(
    *,
    coverage_group: str,
    representative_measured_workload_ids: tuple[str, ...],
    expected_measured_workload_count: int,
    expected_total_workload_count: int | None = None,
) -> SourceTreeCombinedFullyMeasuredManifestExpectation:
    return SourceTreeCombinedFullyMeasuredManifestExpectation(
        coverage_group=coverage_group,
        representative_measured_workload_ids=tuple(
            str(workload_id) for workload_id in representative_measured_workload_ids
        ),
        expected_measured_workload_count=expected_measured_workload_count,
        expected_total_workload_count=expected_total_workload_count,
    )


def _combined_manifest_shape(
    *,
    representative_measured_workload_ids: tuple[str, ...],
    pattern_groups: tuple[SourceTreeCombinedPatternGroupExpectation, ...] = (),
) -> SourceTreeCombinedManifestShapeExpectation:
    return SourceTreeCombinedManifestShapeExpectation(
        representative_measured_workload_ids=representative_measured_workload_ids,
        pattern_groups=pattern_groups,
    )


def _combined_pattern_group(
    *,
    slice_id: str,
    patterns: tuple[str, ...],
    minimum_rows: int,
    required_operations: tuple[str, ...],
    required_categories: tuple[str, ...],
    search_haystacks: tuple[str, ...] = (),
    search_haystack_substrings: tuple[str, ...] = (),
    pattern_haystacks: tuple[str, ...] = (),
) -> SourceTreeCombinedPatternGroupExpectation:
    return SourceTreeCombinedPatternGroupExpectation(
        slice_id=slice_id,
        patterns=patterns,
        minimum_rows=minimum_rows,
        required_operations=required_operations,
        required_categories=required_categories,
        search_haystacks=search_haystacks,
        search_haystack_substrings=search_haystack_substrings,
        pattern_haystacks=pattern_haystacks,
    )


@cache
def _published_benchmark_manifest_ids() -> frozenset[str]:
    return frozenset(
        manifest.manifest_id for manifest in published_benchmark_manifests()
    )


_SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION = _combined_manifest_definition()


class _SourceTreeCombinedManifestExpectations(
    dict[str, SourceTreeCombinedManifestExpectationDefinition]
):
    def _supports_fallback(self, manifest_id: object) -> bool:
        return (
            isinstance(manifest_id, str)
            and manifest_id in _published_benchmark_manifest_ids()
        )

    def __missing__(
        self,
        manifest_id: str,
    ) -> SourceTreeCombinedManifestExpectationDefinition:
        if self._supports_fallback(manifest_id):
            return _SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION
        raise KeyError(manifest_id)

    def get(
        self,
        manifest_id: str,
        default: SourceTreeCombinedManifestExpectationDefinition | None = None,
    ) -> SourceTreeCombinedManifestExpectationDefinition | None:
        if self._supports_fallback(manifest_id):
            return self[manifest_id]
        return default

    def __contains__(self, manifest_id: object) -> bool:
        return super().__contains__(manifest_id) or self._supports_fallback(
            manifest_id
        )


SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS = _SourceTreeCombinedManifestExpectations({
    "compile-matrix": _combined_manifest_definition(
        exclude_from_combined_targets=True,
    ),
    "module-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
            "import-module-cold",
            "module-search-grouped-literal-cold-hit",
            "module-search-literal-warm-hit",
            "module-search-flags-keyword-warm-str",
            "module-search-duplicate-flags-keyword-warm-str",
            "module-match-flags-keyword-purged-bytes",
            "module-fullmatch-flags-keyword-warm-str",
            "module-fullmatch-unexpected-keyword-purged-str",
            "module-search-bytes-cold-miss",
        ),
    ),
    "pattern-boundary": _combined_manifest_definition(
        shape_expectation=_combined_manifest_shape(
            representative_measured_workload_ids=(
                "pattern-search-literal-warm-hit",
                "pattern-fullmatch-bytes-purged-hit",
            ),
        ),
    ),
    "grouped-named-boundary": _combined_manifest_definition(
        promote_zero_gap_representatives=True,
        representative_measured_workload_ids=(
            "module-search-grouped-segment-cold-gap",
            "pattern-search-grouped-segment-warm-gap",
        ),
    ),
    "numbered-backreference-boundary": _combined_manifest_definition(
        promote_zero_gap_representatives=True,
        representative_measured_workload_ids=(
            "module-search-numbered-backreference-segment-cold-gap",
            "pattern-search-numbered-backreference-prefix-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "grouped-alternation-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-sub-template-nested-grouped-alternation-warm-gap",
            "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "grouped-alternation-replacement-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-sub-template-nested-grouped-alternation-cold-gap",
            "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "nested-group-boundary": _combined_manifest_definition(
        promote_zero_gap_representatives=True,
        representative_measured_workload_ids=(
            "module-search-triple-nested-group-cold-gap",
            "pattern-fullmatch-named-quantified-nested-group-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "branch-local-backreference-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-str",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-str",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-str",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-str",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-str",
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-bytes",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-bytes",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-bytes",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-bytes",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-bytes",
        ),
        zero_gap_bytes_representative_subsets=(
            (
                "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-bytes",
                "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-bytes",
                "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-bytes",
                "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-bytes",
                "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-bytes",
            ),
        ),
    ),
    "optional-group-boundary": _combined_manifest_definition(
        promote_zero_gap_representatives=True,
        representative_measured_workload_ids=(
            "module-search-numbered-optional-group-conditional-cold-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "exact-repeat-quantified-group-boundary": _combined_manifest_definition(
        fully_measured_expectation=_combined_fully_measured_manifest_expectation(
            coverage_group="counted-repeat",
            representative_measured_workload_ids=(
                "module-search-numbered-broader-ranged-repeat-group-cold-gap",
            ),
            expected_measured_workload_count=13,
        ),
        representative_known_gap_workload_ids=(),
    ),
    "ranged-repeat-quantified-group-boundary": _combined_manifest_definition(
        fully_measured_expectation=_combined_fully_measured_manifest_expectation(
            coverage_group="counted-repeat",
            representative_measured_workload_ids=(
                "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
            ),
            expected_measured_workload_count=8,
        ),
        representative_known_gap_workload_ids=(),
    ),
    "wider-ranged-repeat-quantified-group-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-third-repetition-mixed-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-str",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-str",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-conditional-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-bytes",
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-third-repetition-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-upper-bound-all-de-purged-bytes",
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-str",
            "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-conditional-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-broader-range-conditional-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-bytes",
            "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
            "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-open-ended-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-open-ended-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-open-ended-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-bytes",
        ),
        zero_gap_bytes_representative_subsets=(
            (
                "module-compile-numbered-wider-ranged-repeat-group-broader-range-conditional-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-broader-range-conditional-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-third-repetition-mixed-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-nested-broader-range-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-nested-broader-range-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-upper-bound-all-de-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-bytes",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-nested-broader-range-conditional-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-open-ended-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-open-ended-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-open-ended-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-bytes",
            ),
        ),
        shape_expectation=_combined_manifest_shape(
            representative_measured_workload_ids=(
                "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-str",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-str",
            ),
            pattern_groups=(
                _combined_pattern_group(
                    slice_id="broader-range-grouped-backtracking-heavy",
                    patterns=(
                        "a((bc|b)c){1,4}d",
                        "a(?P<word>(bc|b)c){1,4}d",
                    ),
                    minimum_rows=12,
                    required_operations=(
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    required_categories=(
                        "grouped",
                        "alternation",
                        "backtracking-heavy",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    search_haystacks=(
                        "zzabcdzz",
                        "zzabccdzz",
                    ),
                    pattern_haystacks=(
                        "abcbccd",
                        "abcbccbccbcd",
                    ),
                ),
                _combined_pattern_group(
                    slice_id="nested-broader-range-grouped-alternation",
                    patterns=(
                        "a((bc|de){1,4})d",
                        "a(?P<outer>(bc|de){1,4})d",
                    ),
                    minimum_rows=12,
                    required_operations=(
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    required_categories=(
                        "nested-group",
                        "alternation",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    search_haystack_substrings=(
                        "abcd",
                        "aded",
                    ),
                    pattern_haystacks=(
                        "abcbcded",
                        "adedededed",
                    ),
                ),
                _combined_pattern_group(
                    slice_id="nested-broader-range-grouped-conditional",
                    patterns=(
                        "a(((bc|de){1,4})d)?(?(1)e|f)",
                        "a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)",
                    ),
                    minimum_rows=14,
                    required_operations=(
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    required_categories=(
                        "nested-group",
                        "alternation",
                        "conditional",
                        "optional-group",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    search_haystacks=(
                        "zzafzz",
                        "zzabcdezz",
                        "zzadedezz",
                    ),
                    pattern_haystacks=(
                        "abcbcdede",
                        "adedededede",
                    ),
                ),
                _combined_pattern_group(
                    slice_id="nested-broader-range-grouped-backtracking-heavy",
                    patterns=(
                        "a(((bc|b)c){1,4})d",
                        "a(?P<outer>((bc|b)c){1,4})d",
                    ),
                    minimum_rows=14,
                    required_operations=(
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    required_categories=(
                        "grouped",
                        "nested-group",
                        "alternation",
                        "backtracking-heavy",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    search_haystacks=(
                        "zzabcdzz",
                        "zzabccdzz",
                    ),
                    pattern_haystacks=(
                        "abcbccd",
                        "abccbcd",
                        "abcbccbccbcd",
                    ),
                ),
            ),
        ),
    ),
    "open-ended-quantified-group-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-compile-numbered-open-ended-group-alternation-cold-bytes",
            "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-alternation-warm-bytes",
            "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
            "module-compile-numbered-open-ended-group-conditional-cold-bytes",
            "module-search-numbered-open-ended-group-conditional-second-repetition-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-conditional-warm-bytes",
            "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
            "module-compile-numbered-open-ended-group-broader-range-cold-bytes",
            "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-broader-range-warm-bytes",
            "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
            "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes",
            "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes",
            "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
            "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes",
            "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes",
            "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
        ),
        zero_gap_bytes_representative_subsets=(
            (
                "module-compile-numbered-open-ended-group-conditional-cold-bytes",
                "module-search-numbered-open-ended-group-conditional-second-repetition-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
                "module-compile-named-open-ended-group-conditional-warm-bytes",
                "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
                "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes",
                "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
                "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes",
                "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            ),
            (
                "module-compile-numbered-open-ended-group-alternation-cold-bytes",
                "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
                "module-compile-named-open-ended-group-alternation-warm-bytes",
                "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
            ),
            (
                "module-compile-numbered-open-ended-group-broader-range-cold-bytes",
                "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
                "module-compile-named-open-ended-group-broader-range-warm-bytes",
                "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
            ),
            (
                "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes",
                "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
                "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes",
                "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
            ),
            (
                "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes",
                "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
                "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes",
                "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
            ),
        ),
    ),
    "quantified-alternation-boundary": _combined_manifest_definition(
        fully_measured_expectation=_combined_fully_measured_manifest_expectation(
            coverage_group="quantified-alternation",
            representative_measured_workload_ids=(
                "module-compile-numbered-quantified-alternation-cold-bytes",
                "module-search-numbered-quantified-alternation-lower-bound-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-second-repetition-purged-bytes",
                "module-compile-named-quantified-alternation-warm-bytes",
                "module-search-named-quantified-alternation-second-repetition-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-lower-bound-purged-bytes",
                "module-compile-numbered-quantified-alternation-nested-branch-cold-bytes",
                "module-search-numbered-quantified-alternation-nested-branch-lower-bound-inner-branch-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-nested-branch-lower-bound-literal-branch-purged-bytes",
                "module-compile-named-quantified-alternation-nested-branch-warm-bytes",
                "module-search-named-quantified-alternation-nested-branch-lower-bound-literal-branch-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-nested-branch-second-repetition-mixed-purged-bytes",
                "module-search-numbered-quantified-alternation-branch-backref-cold-bytes",
                "module-compile-numbered-quantified-alternation-branch-backref-cold-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-branch-backref-second-repetition-purged-bytes",
                "module-compile-named-quantified-alternation-branch-backref-warm-bytes",
                "module-search-named-quantified-alternation-branch-backref-lower-bound-c-branch-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-branch-backref-second-repetition-purged-bytes",
                "module-compile-numbered-quantified-alternation-broader-range-cold-bytes",
                "module-search-numbered-quantified-alternation-broader-range-third-repetition-cold-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-broader-range-third-repetition-bcb-purged-bytes",
                "module-compile-named-quantified-alternation-broader-range-warm-bytes",
                "module-search-named-quantified-alternation-broader-range-third-repetition-bcc-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-broader-range-third-repetition-bbb-purged-bytes",
                "module-compile-numbered-quantified-alternation-open-ended-cold-bytes",
                "module-search-numbered-quantified-alternation-open-ended-lower-bound-b-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-open-ended-fourth-repetition-bcbc-purged-bytes",
                "module-compile-named-quantified-alternation-open-ended-warm-bytes",
                "module-search-named-quantified-alternation-open-ended-lower-bound-c-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-open-ended-fourth-repetition-bcbc-purged-bytes",
                "module-compile-numbered-quantified-alternation-conditional-cold-bytes",
                "module-search-numbered-quantified-alternation-conditional-lower-bound-b-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-conditional-second-repetition-mixed-purged-bytes",
                "module-compile-named-quantified-alternation-conditional-warm-bytes",
                "module-search-named-quantified-alternation-conditional-absent-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-conditional-second-repetition-c-purged-bytes",
                "module-compile-numbered-quantified-alternation-backtracking-heavy-cold-bytes",
                "module-search-numbered-quantified-alternation-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-backtracking-heavy-lower-bound-bc-branch-purged-bytes",
                "module-compile-named-quantified-alternation-backtracking-heavy-warm-bytes",
                "module-search-named-quantified-alternation-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            ),
            expected_measured_workload_count=84,
            expected_total_workload_count=84,
        ),
    ),
    "conditional-group-exists-boundary": _combined_manifest_definition(
        zero_gap_bytes_representative_subsets=(
            (
                "module-sub-template-numbered-conditional-group-exists-replacement-warm-bytes",
                "module-subn-template-numbered-conditional-group-exists-replacement-warm-bytes",
                "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-bytes",
                "module-sub-template-named-conditional-group-exists-replacement-warm-bytes",
                "module-subn-template-named-conditional-group-exists-replacement-warm-bytes",
                "pattern-sub-template-named-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-template-named-conditional-group-exists-replacement-purged-bytes",
                "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-bytes",
                "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-bytes",
            ),
            (
                "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged-bytes",
                "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm-bytes",
                "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged-bytes",
                "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
                "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
                "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
                "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
                "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
                "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
            ),
            (
                "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-bytes",
                "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
                "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
                "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-bytes",
                "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
                "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
                "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
                "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
                "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
                "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
                "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
                "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
                "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
                "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
                "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
                "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
                "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
                "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
            ),
            (
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm-bytes",
                "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-purged-bytes",
                "module-sub-callable-named-quantified-conditional-group-exists-replacement-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-warm-bytes",
                "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-purged-bytes",
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
                "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
                "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
                "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
                "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
                "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
                "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
                "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
                "module-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
                "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
            ),
            (
                "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
                "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
                "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
                "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
                "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
                "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
                "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
            ),
        ),
    ),
    "regression-matrix": _combined_manifest_definition(
        exclude_from_combined_targets=True,
        representative_measured_workload_ids=(
            "regression-parser-bytes-backreference-purged",
        ),
    ),
})


def _combined_slice_expectation(
    *,
    manifest_id: str,
    slice_id: str,
    required_syntax_features: tuple[str, ...] = (),
    excluded_syntax_features: tuple[str, ...] = (),
    required_categories: tuple[str, ...] = (),
    excluded_categories: tuple[str, ...] = (),
    required_id_suffix: str | None = None,
    expected_workload_ids: tuple[str, ...],
    expected_patterns: set[str],
    expected_operations: set[str],
    expected_haystacks: set[str],
    required_row_categories: tuple[str, ...],
    expected_status: str = "measured",
) -> SourceTreeCombinedSliceExpectation:
    return SourceTreeCombinedSliceExpectation(
        manifest_id=manifest_id,
        slice_id=slice_id,
        required_syntax_features=tuple(
            str(feature) for feature in required_syntax_features
        ),
        excluded_syntax_features=tuple(
            str(feature) for feature in excluded_syntax_features
        ),
        required_categories=tuple(str(category) for category in required_categories),
        excluded_categories=tuple(str(category) for category in excluded_categories),
        required_id_suffix=required_id_suffix,
        expected_workload_ids=(
            expected_workload_ids
            if isinstance(expected_workload_ids, tuple)
            and all(
                isinstance(workload_id, str)
                for workload_id in expected_workload_ids
            )
            else tuple(str(workload_id) for workload_id in expected_workload_ids)
        ),
        expected_patterns=frozenset(str(pattern) for pattern in expected_patterns),
        expected_operations=frozenset(
            str(operation) for operation in expected_operations
        ),
        expected_haystacks=frozenset(
            str(haystack) for haystack in expected_haystacks
        ),
        required_row_categories=tuple(
            str(category) for category in required_row_categories
        ),
        expected_status=expected_status,
    )


SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS = (
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="anchored-module-compile-cluster",
        required_syntax_features=("module-compile", "literal-text"),
        excluded_syntax_features=("compiled-pattern-first-argument",),
        required_categories=("compile", "literal"),
        expected_workload_ids=(
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
        ),
        expected_patterns={r"^abc$"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=("compile", "literal"),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-literal-success",
        required_syntax_features=(
            "module-compile",
            "literal-text",
            "compiled-pattern-first-argument",
        ),
        excluded_syntax_features=("keyword-flags",),
        required_categories=("compile", "literal", "compiled-pattern"),
        excluded_categories=("keyword", "flags"),
        expected_workload_ids=(
            "module-compile-literal-warm-str-compiled-pattern",
            "module-compile-literal-purged-bytes-compiled-pattern",
        ),
        expected_patterns={"abc"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=("compile", "literal", "compiled-pattern"),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-named-group-success",
        required_syntax_features=(
            "module-compile",
            "grouping-forms",
            "named-groups",
            "compiled-pattern-first-argument",
        ),
        required_categories=("compile", "named-group", "compiled-pattern"),
        excluded_syntax_features=("keyword-flags",),
        excluded_categories=("keyword", "flags"),
        expected_workload_ids=(
            "module-compile-named-group-warm-str-compiled-pattern",
            "module-compile-named-group-purged-bytes-compiled-pattern",
        ),
        expected_patterns={"(?P<word>abc)"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=("compile", "named-group", "compiled-pattern"),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-int-zero-keyword-named-group",
        required_syntax_features=(
            "module-compile",
            "grouping-forms",
            "named-groups",
            "compiled-pattern-first-argument",
            "keyword-flags",
        ),
        required_categories=("compile", "named-group", "compiled-pattern", "keyword", "flags"),
        excluded_categories=("bool", "ignorecase", "exception"),
        expected_workload_ids=(
            "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group",
            "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group",
        ),
        expected_patterns={"(?P<word>abc)"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
        ),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-bool-false-keyword-named-group",
        required_syntax_features=(
            "module-compile",
            "grouping-forms",
            "named-groups",
            "compiled-pattern-first-argument",
            "keyword-flags",
        ),
        required_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
            "bool",
        ),
        expected_workload_ids=(
            "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group",
            "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group",
        ),
        expected_patterns={"(?P<word>abc)"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
            "bool",
        ),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-ignorecase-keyword-rejection-named-group",
        required_syntax_features=(
            "module-compile",
            "grouping-forms",
            "named-groups",
            "compiled-pattern-first-argument",
            "keyword-flags",
            "ignorecase-flag",
        ),
        required_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
            "ignorecase",
            "exception",
        ),
        expected_workload_ids=(
            "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group",
            "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group",
        ),
        expected_patterns={"(?P<word>abc)"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
            "ignorecase",
            "exception",
        ),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-int-zero-keyword",
        required_syntax_features=(
            "module-compile",
            "literal-text",
            "compiled-pattern-first-argument",
            "keyword-flags",
        ),
        required_categories=("compile", "literal", "compiled-pattern", "keyword", "flags"),
        excluded_categories=("bool", "ignorecase", "exception"),
        expected_workload_ids=(
            "module-compile-flags-int-zero-warm-str-compiled-pattern",
            "module-compile-flags-int-zero-purged-bytes-compiled-pattern",
        ),
        expected_patterns={"abc"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=("compile", "literal", "compiled-pattern", "keyword", "flags"),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-bool-false-keyword",
        required_syntax_features=(
            "module-compile",
            "literal-text",
            "compiled-pattern-first-argument",
            "keyword-flags",
        ),
        required_categories=(
            "compile",
            "literal",
            "compiled-pattern",
            "keyword",
            "flags",
            "bool",
        ),
        expected_workload_ids=(
            "module-compile-flags-bool-false-warm-str-compiled-pattern",
            "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
        ),
        expected_patterns={"abc"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=(
            "compile",
            "literal",
            "compiled-pattern",
            "keyword",
            "flags",
            "bool",
        ),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-ignorecase-keyword-rejection",
        required_syntax_features=(
            "module-compile",
            "literal-text",
            "compiled-pattern-first-argument",
            "keyword-flags",
            "ignorecase-flag",
        ),
        required_categories=(
            "compile",
            "literal",
            "compiled-pattern",
            "keyword",
            "flags",
            "ignorecase",
            "exception",
        ),
        expected_workload_ids=(
            "module-compile-flags-ignorecase-warm-str-compiled-pattern",
            "module-compile-flags-ignorecase-purged-bytes-compiled-pattern",
        ),
        expected_patterns={"abc"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=(
            "compile",
            "literal",
            "compiled-pattern",
            "keyword",
            "flags",
            "ignorecase",
            "exception",
        ),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="branch-local-backreference-boundary",
        slice_id="broader-range-open-ended-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "conditionals",
            "nested-groups",
            "counted-repeats",
        ),
        required_categories=("open-ended-repeat", "broader-range"),
        expected_workload_ids=(
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-str",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-str",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-str",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-str",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-str",
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-bytes",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-bytes",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-bytes",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-bytes",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbbdzz", "abcbccd", "zzacccdzz", "abbbd"},
        required_row_categories=(
            "grouped",
            "nested-group",
            "alternation",
            "branch-local",
            "conditional",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="quantified-nested-alternation",
        required_syntax_features=("alternation", "quantifiers"),
        excluded_syntax_features=("branch-local-backreferences",),
        expected_workload_ids=(
            "module-search-nested-group-quantified-alternation-cold-gap",
            "pattern-fullmatch-numbered-quantified-nested-group-alternation-repeated-mixed-purged-str",
            "module-search-named-quantified-nested-group-alternation-lower-bound-c-warm-str",
            "pattern-fullmatch-named-quantified-nested-group-alternation-repeated-mixed-purged-str",
        ),
        expected_patterns={
            r"a((b|c)+)d",
            r"a(?P<outer>(?P<inner>b|c)+)d",
        },
        expected_operations={"module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabdzz", "acbbd", "zzacdzz", "abccd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="non-quantified-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences",),
        excluded_syntax_features=("quantifiers",),
        expected_workload_ids=(
            "module-search-numbered-nested-group-branch-local-backreference-b-branch-warm-str",
            "module-compile-named-nested-group-branch-local-backreference-warm-str",
            "pattern-fullmatch-named-nested-group-branch-local-backreference-purged-gap",
        ),
        expected_patterns={
            r"a((b|c))\2d",
            r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbdzz", "accd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="quantified-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences", "quantifiers"),
        excluded_syntax_features=("counted-repeats",),
        expected_workload_ids=(
            "module-search-numbered-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-search-numbered-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-compile-named-quantified-nested-group-branch-local-backreference-warm-str",
            "module-compile-named-quantified-nested-group-branch-local-backreference-warm-bytes",
            "pattern-fullmatch-named-quantified-nested-group-branch-local-backreference-repeated-mixed-purged-str",
            "pattern-fullmatch-named-quantified-nested-group-branch-local-backreference-repeated-mixed-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c)+)\2d",
            r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbdzz", "abccd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="broader-range-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "counted-repeats",
            "ranged-repeats",
        ),
        expected_workload_ids=(
            "module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-str",
            "module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbdzz", "acccccd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="broader-range-open-ended-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences", "counted-repeats"),
        excluded_syntax_features=("ranged-repeats",),
        required_categories=("open-ended-repeat", "broader-range"),
        expected_workload_ids=(
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-str",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-bytes",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbbdzz", "acccd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-group-bytes",
        required_syntax_features=("callable-replacement", "pattern-text-model"),
        excluded_syntax_features=(
            "alternation",
            "branch-local-backreferences",
            "quantifiers",
        ),
        expected_workload_ids=(
            "module-sub-callable-nested-group-numbered-warm-bytes",
            "module-subn-callable-nested-group-numbered-warm-bytes",
            "pattern-sub-callable-nested-group-numbered-purged-bytes",
            "pattern-subn-callable-nested-group-numbered-purged-bytes",
            "module-sub-callable-nested-group-named-warm-bytes",
            "module-subn-callable-nested-group-named-warm-bytes",
            "pattern-sub-callable-nested-group-named-purged-bytes",
            "pattern-subn-callable-nested-group-named-purged-bytes",
        ),
        expected_patterns={
            r"a((b))d",
            r"a(?P<outer>(?P<inner>b))d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abdabd"},
        required_row_categories=(
            "nested-group",
            "replacement",
            "callable",
            "bytes",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-alternation",
        required_syntax_features=("alternation", "callable-replacement"),
        excluded_syntax_features=("branch-local-backreferences", "quantifiers"),
        expected_workload_ids=(
            "module-sub-callable-nested-group-alternation-cold-gap",
            "pattern-subn-callable-numbered-nested-group-alternation-c-branch-first-match-only-purged-str",
            "module-sub-callable-named-nested-group-alternation-c-branch-warm-str",
            "pattern-subn-callable-named-nested-group-alternation-b-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c))d",
            r"a(?P<outer>(?P<inner>b|c))d",
        },
        expected_operations={"module.sub", "pattern.subn"},
        expected_haystacks={"abdacd", "acdabd", "acd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="quantified-nested-group",
        required_syntax_features=(
            "callable-replacement",
            "quantifiers",
        ),
        excluded_syntax_features=("alternation", "branch-local-backreferences"),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-lower-bound-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-repeated-outer-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-purged-gap",
            "module-sub-callable-numbered-quantified-nested-group-lower-bound-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-repeated-outer-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((bc)+)d",
            r"a(?P<outer>(?P<inner>bc)+)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcbcdabcbcdzz", "zzabcbcdzz"},
        required_row_categories=(
            "nested-group",
            "replacement",
            "callable",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="quantified-nested-alternation",
        required_syntax_features=("alternation", "callable-replacement", "quantifiers"),
        excluded_syntax_features=("branch-local-backreferences",),
        excluded_categories=("counted-repeat",),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-alternation-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-alternation-c-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-alternation-repeated-mixed-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-alternation-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-quantified-nested-group-alternation-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-alternation-c-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-alternation-repeated-mixed-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-alternation-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c)+)d",
            r"a(?P<outer>(?P<inner>b|c)+)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabdzz", "zzabccdacbbdzz", "zzabccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-broader-range-backtracking-heavy-callable-replacement",
        required_syntax_features=(
            "alternation",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
        ),
        excluded_syntax_features=("branch-local-backreferences", "conditionals"),
        required_categories=("broader-range", "backtracking-heavy"),
        expected_workload_ids=(
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a(((bc|b)c){1,4})d",
            r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={
            "abcd",
            "abccdabcbccd",
            "zzabcbccbccbcdzz",
            "zzabccbcdabccdzz",
        },
        required_row_categories=(
            "grouped",
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
            "backtracking-heavy",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-broader-range-open-ended-backtracking-heavy-callable-replacement",
        required_syntax_features=(
            "alternation",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=(
            "branch-local-backreferences",
            "conditionals",
            "ranged-repeats",
        ),
        required_categories=("open-ended-repeat", "broader-range", "backtracking-heavy"),
        expected_workload_ids=(
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a(((bc|b)c){2,})d",
            r"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={
            "abcbcd",
            "abccbccdabcbcd",
            "zzabcbcbcbcdzz",
            "zzabcbcbcbcdabccbccdzz",
        },
        required_row_categories=(
            "grouped",
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
            "backtracking-heavy",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="branch-local-backreference",
        required_syntax_features=("branch-local-backreferences", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        expected_workload_ids=(
            "module-sub-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-warm-str",
            "module-subn-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-nested-group-alternation-branch-local-backreference-c-branch-purged-str",
            "pattern-subn-callable-named-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-warm-bytes",
            "module-subn-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-nested-group-alternation-branch-local-backreference-c-branch-purged-bytes",
            "pattern-subn-callable-named-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c))\2d",
            r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbdaccd", "accd", "accdabbd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="quantified-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
        ),
        excluded_syntax_features=("counted-repeats", "ranged-repeats"),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c)+)\2d",
            r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzabccdzz", "zzaccdabbbdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
        ),
        excluded_syntax_features=("conditionals",),
        expected_workload_ids=(
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-str",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abcbccdabbd", "zzacccccdzz", "zzacccccdabbbdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
            "conditionals",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-str",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){1,4})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzacccccdzz", "zzacccccdabbbdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "conditional",
            "group-exists",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        excluded_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c){1,})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzaccdzz", "zzaccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-open-ended-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "conditionals",
        ),
        excluded_syntax_features=("ranged-repeats",),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "conditional",
            "group-exists",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="quantified-nested-group",
        required_syntax_features=("quantifiers", "replacement-template"),
        excluded_syntax_features=("branch-local-backreferences",),
        expected_workload_ids=(
            "module-sub-template-numbered-quantified-nested-group-replacement-lower-bound-warm-str",
            "module-subn-template-numbered-quantified-nested-group-replacement-first-match-only-warm-str",
            "pattern-sub-template-named-quantified-nested-group-replacement-repeated-outer-purged-str",
            "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap",
        ),
        expected_patterns={
            r"a((bc)+)d",
            r"a(?P<outer>(?P<inner>bc)+)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcbcdabcbcdzz", "zzabcbcdzz"},
        required_row_categories=(
            "nested-group",
            "replacement",
            "template",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="broader-range-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
        ),
        excluded_syntax_features=("conditionals",),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzacccccdzz", "zzacccccdabbbdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        excluded_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c){1,})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzaccdzz", "zzaccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="broader-range-open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str",
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="broader-range-open-ended-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
            "conditionals",
        ),
        excluded_syntax_features=("ranged-repeats",),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str",
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "conditional",
            "group-exists",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="open-ended-quantified-group-boundary",
        slice_id="broader-range-group-alternation",
        required_syntax_features=("module-search",),
        excluded_syntax_features=("conditionals", "named-groups"),
        required_categories=(
            "broader-range",
            "search",
            "module",
            "lower-bound",
            "bc-bc",
        ),
        excluded_categories=("backtracking-heavy",),
        expected_workload_ids=(
            "module-search-numbered-open-ended-group-broader-range-cold-gap",
            "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
        ),
        expected_patterns={r"a(bc|de){2,}d"},
        expected_operations={"module.search"},
        expected_haystacks={"zzabcbcdzz"},
        required_row_categories=(
            "grouped",
            "alternation",
            "quantifier",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
            "search",
            "module",
            "lower-bound",
            "bc-bc",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="open-ended-quantified-group-boundary",
        slice_id="broader-range-group-conditional",
        required_syntax_features=("module-search", "conditionals"),
        excluded_syntax_features=("named-groups",),
        required_categories=(
            "broader-range",
            "conditional",
            "search",
            "module",
            "present",
            "second-repetition",
            "bc-branch",
        ),
        excluded_categories=("backtracking-heavy",),
        expected_workload_ids=(
            "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap",
            "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
        ),
        expected_patterns={r"a((bc|de){2,})?(?(1)d|e)"},
        expected_operations={"module.search"},
        expected_haystacks={"zzabcbcdzz"},
        required_row_categories=(
            "grouped",
            "alternation",
            "quantifier",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
            "conditional",
            "optional-group",
            "search",
            "module",
            "present",
            "second-repetition",
            "bc-branch",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="open-ended-quantified-group-boundary",
        slice_id="broader-range-group-backtracking-heavy",
        required_syntax_features=("pattern-fullmatch", "named-groups"),
        excluded_syntax_features=("conditionals",),
        required_categories=(
            "broader-range",
            "backtracking-heavy",
            "pattern",
            "fullmatch",
            "named-group",
            "fourth-repetition",
            "b-branch",
        ),
        expected_workload_ids=(
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
        ),
        expected_patterns={r"a(?P<word>(bc|b)c){2,}d"},
        expected_operations={"pattern.fullmatch"},
        expected_haystacks={"abcbcbcbcd"},
        required_row_categories=(
            "grouped",
            "alternation",
            "quantifier",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
            "backtracking-heavy",
            "pattern",
            "fullmatch",
            "named-group",
            "fourth-repetition",
            "b-branch",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="grouped-alternation-callable-replacement-boundary",
        slice_id="former-gap-callable-replacement-rows",
        required_syntax_features=("callable-replacement",),
        required_id_suffix="gap",
        expected_workload_ids=(
            "module-sub-callable-nested-grouped-alternation-cold-gap",
            "pattern-subn-callable-named-nested-grouped-alternation-purged-gap",
        ),
        expected_patterns={
            r"a((b|c))d",
            r"a(?P<outer>(b|c))d",
        },
        expected_operations={"module.sub", "pattern.subn"},
        expected_haystacks={"abdacd", "acdabd"},
        required_row_categories=(
            "alternation",
            "replacement",
            "callable",
            "gap",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-template-replacement-rows",
        required_syntax_features=("conditionals", "replacement-template"),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation-heavy",
            "nested-group",
            "quantified",
            "unsupported",
            "callable",
        ),
        expected_workload_ids=(
            "module-sub-template-numbered-conditional-group-exists-replacement-warm-gap",
            "module-subn-template-numbered-conditional-group-exists-replacement-warm-str",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-str",
            "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-str",
            "module-sub-template-numbered-conditional-group-exists-replacement-warm-bytes",
            "module-subn-template-numbered-conditional-group-exists-replacement-warm-bytes",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-bytes",
            "module-sub-template-named-conditional-group-exists-replacement-warm-str",
            "module-subn-template-named-conditional-group-exists-replacement-warm-str",
            "pattern-sub-template-named-conditional-group-exists-replacement-purged-str",
            "pattern-subn-template-named-conditional-group-exists-replacement-purged-str",
            "module-sub-template-named-conditional-group-exists-replacement-warm-bytes",
            "module-subn-template-named-conditional-group-exists-replacement-warm-bytes",
            "pattern-sub-template-named-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-template-named-conditional-group-exists-replacement-purged-bytes",
            "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-str",
            "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-str",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-str",
            "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
            "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-bytes",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
            "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-bytes",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzacezz", "abcdaceabcd"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "template",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-callable-replacement-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "exception",
            "nested-conditional",
            "nested-group",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-conditional-group-exists-replacement-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-replacement-warm-bytes",
            "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-str",
            "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-bytes",
            "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
            "module-sub-callable-named-conditional-group-exists-replacement-warm-str",
            "module-sub-callable-named-conditional-group-exists-replacement-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-bytes",
            "pattern-sub-callable-named-conditional-group-exists-replacement-purged-str",
            "pattern-sub-callable-named-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-purged-gap",
            "pattern-subn-callable-named-conditional-group-exists-replacement-purged-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-bytes",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcdacezz", "abcdaceabcd"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "callable",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-callable-replacement-exception-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        required_categories=("exception",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "nested-conditional",
            "nested-group",
            "none-count",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-str",
            "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-bytes",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-bytes",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.subn", "pattern.subn"},
        expected_haystacks={"zzacezz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "callable",
            "absent",
            "count",
            "exception",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-callable-replacement-none-count-exception-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        required_categories=("none-count", "exception"),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "nested-conditional",
            "nested-group",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged-bytes",
            "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm-str",
            "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm-bytes",
            "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged-str",
            "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged-bytes",
            "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm-str",
            "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
            "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzacezz", "abcdaceabcd"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "callable",
            "count",
            "none-count",
            "exception",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="alternation-heavy-callable-replacement-rows",
        required_syntax_features=("conditionals", "alternation", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        required_categories=("alternation-heavy", "replacement", "callable"),
        expected_workload_ids=(
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-gap",
            "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-str",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
            "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
            "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
            "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
            "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
            "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
            "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-str",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-str",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
        ),
        expected_patterns={
            r"a(b)?c(?(1)(de|df)|(eg|eh))",
            r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={
            "zzabcdezz",
            "zzabcdfzz",
            "zzacegzz",
            "zzacehzz",
        },
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "alternation-heavy",
            "replacement",
            "callable",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="nested-callable-replacement-str-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        required_categories=("nested-conditional",),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "bytes",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-str",
            "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-str",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-str",
            "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-str",
            "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-str",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-str",
            "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-str",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-str",
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-str",
            "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-str",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-str",
            "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-str",
            "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-str",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-str",
            "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-str",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-str",
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-str",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-str",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-str",
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-str",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-str",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-str",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-str",
        ),
        expected_patterns={
            r"a(b)?c(?(1)(?(1)d|e)|f)",
            r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcezz", "zzacezz", "zzacfzz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "nested-conditional",
            "replacement",
            "callable",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="nested-callable-replacement-bytes-rows",
        required_syntax_features=(
            "pattern-text-model",
            "conditionals",
            "callable-replacement",
        ),
        required_categories=("nested-conditional", "bytes"),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "nested-group",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-bytes",
            "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
            "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-bytes",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
            "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
            "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
            "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
            "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
            "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
        ),
        expected_patterns={
            r"a(b)?c(?(1)(?(1)d|e)|f)",
            r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcezz", "zzacezz", "zzacfzz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "nested-conditional",
            "replacement",
            "callable",
            "bytes",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="quantified-callable-replacement-str-rows",
        required_syntax_features=(
            "conditionals",
            "quantifiers",
            "callable-replacement",
        ),
        required_categories=("quantified",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "bytes",
            "nested-conditional",
            "nested-group",
            "unsupported",
        ),
        expected_workload_ids=CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
        expected_patterns={
            r"a(b)?c(?(1)d|e){2}",
            r"a(?P<word>b)?c(?(word)d|e){2}",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcddzz", "zzaceezz", "zzabcdezz", "zzacedzz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "quantified",
            "replacement",
            "callable",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="quantified-callable-replacement-bytes-rows",
        required_syntax_features=(
            "pattern-text-model",
            "conditionals",
            "quantifiers",
            "callable-replacement",
        ),
        required_categories=("quantified", "bytes"),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "nested-conditional",
            "nested-group",
            "unsupported",
        ),
        expected_workload_ids=CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
        expected_patterns={
            r"a(b)?c(?(1)d|e){2}",
            r"a(?P<word>b)?c(?(word)d|e){2}",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcddzz", "zzaceezz", "zzabcdezz", "zzacedzz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "quantified",
            "replacement",
            "callable",
            "bytes",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="quantified-alternation-heavy-constant-replacement-rows",
        required_syntax_features=("conditionals", "alternation", "quantifiers"),
        required_categories=("alternation-heavy", "replacement", "quantified"),
        expected_workload_ids=(
            "module-sub-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "module-subn-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "pattern-sub-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
            "pattern-subn-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
            "module-sub-named-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "module-subn-named-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "pattern-sub-named-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
            "pattern-subn-named-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
        ),
        expected_patterns={
            r"a(b)?c(?(1)(de|df)|(eg|eh)){2}",
            r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={
            "zzabcdedezz",
            "zzabcdfdfzz",
            "zzacegegzz",
            "zzacehehzz",
        },
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "alternation-heavy",
            "quantified",
            "replacement",
        ),
    ),
)

def relative_manifest_path(path: pathlib.Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def ordered_operations(workloads: list[Workload]) -> list[str]:
    operations: list[str] = []
    for workload in workloads:
        operation = workload.operation
        if operation not in operations:
            operations.append(operation)
    return operations


def source_tree_scorecard_case_ids() -> tuple[str, ...]:
    return tuple(SOURCE_TREE_SCORECARD_EXPECTATIONS)


def _append_unique_workload_ids(
    representative_ids: list[str],
    workload_ids: Iterable[str],
) -> None:
    for workload_id in workload_ids:
        normalized_workload_id = str(workload_id)
        if normalized_workload_id not in representative_ids:
            representative_ids.append(normalized_workload_id)


def _filter_manifest_workload_ids(
    workload_ids: tuple[str, ...] | None,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> tuple[str, ...]:
    if workload_ids is None:
        return ()
    if selected_workload_ids is None or not workload_ids:
        return workload_ids

    selected_workload_id_set = {
        str(workload_id) for workload_id in selected_workload_ids
    }
    return tuple(
        workload_id
        for workload_id in workload_ids
        if workload_id in selected_workload_id_set
    )


def source_tree_combined_manifest_representative_measured_workload_ids(
    manifest_id: str,
) -> tuple[str, ...]:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )

    explicit_workload_ids = manifest_expectation.representative_measured_workload_ids
    if explicit_workload_ids is not None:
        return explicit_workload_ids

    representative_ids: list[str] = []
    shape_expectation = manifest_expectation.shape_expectation
    if shape_expectation is not None:
        _append_unique_workload_ids(
            representative_ids,
            shape_expectation.representative_measured_workload_ids,
        )
    for expectation in SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS:
        if expectation.manifest_id != manifest_id:
            continue
        _append_unique_workload_ids(
            representative_ids,
            expectation.expected_workload_ids,
        )
    return tuple(representative_ids)


def source_tree_combined_fully_measured_manifest_expectation(
    manifest_id: str,
) -> SourceTreeCombinedFullyMeasuredManifestExpectation:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )

    fully_measured_expectation = manifest_expectation.fully_measured_expectation
    if fully_measured_expectation is None:
        raise AssertionError(
            "source-tree combined manifest "
            f"{manifest_id!r} does not define a fully measured contract"
        )
    return fully_measured_expectation


def source_tree_combined_fully_measured_manifest_ids(
    coverage_group: str | None = None,
) -> tuple[str, ...]:
    return tuple(
        manifest_id
        for manifest_id, manifest_expectation in (
            SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
        )
        if manifest_expectation.fully_measured_expectation is not None
        and (
            coverage_group is None
            or manifest_expectation.fully_measured_expectation.coverage_group
            == coverage_group
        )
    )


def _source_tree_manifest_known_gap_count(
    manifest_expectation: SourceTreeCombinedManifestExpectationDefinition,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> int:
    return len(
        _filter_manifest_workload_ids(
            manifest_expectation.known_gap_workload_ids,
            selected_workload_ids=selected_workload_ids,
        )
    )


def _source_tree_manifest_representative_measured_workload_ids(
    manifest_expectation: SourceTreeCombinedManifestExpectationDefinition,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> tuple[str, ...]:
    return _filter_manifest_workload_ids(
        manifest_expectation.representative_measured_workload_ids,
        selected_workload_ids=selected_workload_ids,
    )


def _source_tree_manifest_representative_known_gap_workload_ids(
    manifest_expectation: SourceTreeCombinedManifestExpectationDefinition,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> tuple[str, ...]:
    return _filter_manifest_workload_ids(
        manifest_expectation.representative_known_gap_workload_ids,
        selected_workload_ids=selected_workload_ids,
    )


def _public_source_tree_manifest_expectation(
    manifest_id: str,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> SourceTreeManifestExpectation:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )
    return SourceTreeManifestExpectation(
        known_gap_count=_source_tree_manifest_known_gap_count(
            manifest_expectation,
            selected_workload_ids=selected_workload_ids,
        ),
        representative_measured_workload_ids=(
            _source_tree_manifest_representative_measured_workload_ids(
                manifest_expectation,
                selected_workload_ids=selected_workload_ids,
            )
        ),
        representative_known_gap_workload_ids=(
            _source_tree_manifest_representative_known_gap_workload_ids(
                manifest_expectation,
                selected_workload_ids=selected_workload_ids,
            )
        ),
    )


def _single_manifest_scorecard_fallback_expectation(
    manifest_id: str,
    *,
    case_definition: _SourceTreeScorecardDefinition,
    manifest_known_gap_counts: dict[str, int],
    selected_workload_ids: Iterable[str] | None = None,
) -> SourceTreeManifestExpectation:
    selected_workload_id_set = (
        {str(workload_id) for workload_id in selected_workload_ids}
        if selected_workload_ids is not None
        else None
    )

    def _filter_case_workload_ids(workload_ids: tuple[str, ...]) -> tuple[str, ...]:
        if selected_workload_id_set is None:
            return workload_ids
        return tuple(
            workload_id
            for workload_id in workload_ids
            if workload_id in selected_workload_id_set
        )

    return SourceTreeManifestExpectation(
        known_gap_count=manifest_known_gap_counts[manifest_id],
        representative_measured_workload_ids=_filter_case_workload_ids(
            case_definition.representative_measured_workload_ids
        ),
        representative_known_gap_workload_ids=_filter_case_workload_ids(
            case_definition.representative_known_gap_workload_ids
        ),
    )


def _source_tree_manifest_known_gap_counts(
    manifests: list[BenchmarkManifest],
    case_definition: _SourceTreeScorecardDefinition,
    *,
    selection_mode: str,
) -> dict[str, int]:
    known_gap_counts: dict[str, int] = {}
    for manifest in manifests:
        manifest_id = manifest.manifest_id
        manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
        if manifest_expectation is None:
            raise AssertionError(
                "missing known-gap expectation for source-tree scorecard manifest "
                f"{manifest_id!r}"
            )
        known_gap_counts[manifest_id] = _source_tree_manifest_known_gap_count(
            manifest_expectation,
            selected_workload_ids=_selected_source_tree_manifest_workload_ids(
                manifest,
                selection_mode=selection_mode,
            ),
        )
    return known_gap_counts


def _selected_source_tree_manifest_workload_ids(
    manifest: BenchmarkManifest,
    *,
    selection_mode: str,
) -> tuple[str, ...]:
    return tuple(
        workload.workload_id
        for workload in manifest.selected_workloads(selection_mode=selection_mode)
    )


def _flatten_manifest_workloads(manifests: list[BenchmarkManifest]) -> list[Workload]:
    return [workload for manifest in manifests for workload in manifest.workloads]


def _source_tree_benchmark_common_case_kwargs(
    *,
    manifests: list[BenchmarkManifest],
    workloads: list[Workload],
    selection_mode: str,
    manifest_known_gap_counts: dict[str, int] | None = None,
    expected_summary: dict[str, int] | None = None,
) -> dict[str, Any]:
    workload_payloads = [workload_to_payload(workload) for workload in workloads]
    return {
        "expected_adapter": (
            "rebar.module-surface"
            if any(workload.family == "module" for workload in workloads)
            else "rebar.compile"
        ),
        "expected_phase": determine_phase(workload_payloads),
        "expected_runner_version": determine_runner_version(workload_payloads),
        "expected_summary": (
            expected_summary
            if expected_summary is not None
            else expected_summary_for_manifests(
                manifests,
                selection_mode=selection_mode,
                manifest_known_gap_counts=manifest_known_gap_counts,
            )
        ),
        "manifests": manifests,
        "selection_mode": selection_mode,
    }


def source_tree_scorecard_case(case_id: str) -> SourceTreeScorecardCase:
    if case_id not in SOURCE_TREE_SCORECARD_EXPECTATIONS:
        raise AssertionError(f"unknown source-tree scorecard case {case_id!r}")

    case_definition = SOURCE_TREE_SCORECARD_EXPECTATIONS[case_id]
    manifest_ids = case_definition.manifest_ids
    manifest_records = manifest_records_by_id(published_benchmark_manifests())
    manifests: list[BenchmarkManifest] = []
    for manifest_id in manifest_ids:
        try:
            manifests.append(manifest_records[manifest_id])
        except KeyError as exc:
            raise AssertionError(
                f"unknown benchmark manifest id {manifest_id!r}"
            ) from exc
    selected_workloads = select_workloads(
        _flatten_manifest_workloads(manifests),
        smoke_only=case_definition.selection_mode == "smoke",
    )
    manifest_known_gap_counts = _source_tree_manifest_known_gap_counts(
        manifests,
        case_definition,
        selection_mode=case_definition.selection_mode,
    )
    manifest_expectations: dict[str, SourceTreeManifestExpectation] = {}
    for manifest in manifests:
        manifest_id = manifest.manifest_id
        selected_workload_ids = _selected_source_tree_manifest_workload_ids(
            manifest,
            selection_mode=case_definition.selection_mode,
        )
        manifest_expectations[manifest_id] = (
            _public_source_tree_manifest_expectation(
                manifest_id,
                selected_workload_ids=selected_workload_ids,
            )
            if manifest_id in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
            else _single_manifest_scorecard_fallback_expectation(
                manifest_id,
                case_definition=case_definition,
                manifest_known_gap_counts=manifest_known_gap_counts,
                selected_workload_ids=selected_workload_ids,
            )
        )
    representative_measured_workload_ids = (
        case_definition.representative_measured_workload_ids
    )
    representative_known_gap_workload_ids = (
        case_definition.representative_known_gap_workload_ids
    )
    if (
        len(manifest_ids) == 1
        and manifest_ids[0] in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
    ):
        manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_ids[0]]
        if not representative_measured_workload_ids:
            representative_measured_workload_ids = (
                source_tree_combined_manifest_representative_measured_workload_ids(
                    manifest_ids[0]
                )
            )
        if not representative_known_gap_workload_ids:
            representative_known_gap_workload_ids = (
                _source_tree_manifest_representative_known_gap_workload_ids(
                    manifest_expectation
                )
            )
    common_case_kwargs = _source_tree_benchmark_common_case_kwargs(
        manifests=manifests,
        workloads=selected_workloads,
        selection_mode=case_definition.selection_mode,
        manifest_known_gap_counts=manifest_known_gap_counts,
    )
    return SourceTreeScorecardCase(
        **common_case_kwargs,
        case_id=case_id,
        manifest_expectations=manifest_expectations,
        representative_measured_workload_ids=representative_measured_workload_ids,
        representative_known_gap_workload_ids=representative_known_gap_workload_ids,
        expected_first_deferred=case_definition.expected_first_deferred,
        expected_workload_order=case_definition.expected_workload_order,
    )


def source_tree_combined_target_manifest_ids() -> tuple[str, ...]:
    target_manifest_ids: list[str] = []
    missing_expectations: list[str] = []
    for manifest in published_benchmark_manifests():
        manifest_id = manifest.manifest_id
        manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(
            manifest_id
        )
        if manifest_expectation is None:
            missing_expectations.append(manifest_id)
            continue
        if manifest_expectation.exclude_from_combined_targets:
            continue
        target_manifest_ids.append(manifest_id)
    if missing_expectations:
        raise AssertionError(
            "source-tree combined manifest expectations drifted from the published full-suite selector: "
            f"missing {sorted(missing_expectations)}"
        )
    return tuple(target_manifest_ids)


def _selected_source_tree_manifests_for_target_manifest(
    target_manifest_id: str,
) -> list[BenchmarkManifest]:
    selected_manifests: list[BenchmarkManifest] = []
    published_manifests = published_benchmark_manifests()
    regression_manifest = next(
        (
            manifest
            for manifest in published_manifests
            if manifest.manifest_id == "regression-matrix"
        ),
        None,
    )
    for manifest in published_manifests:
        manifest_id = manifest.manifest_id
        if manifest_id == "regression-matrix":
            continue
        selected_manifests.append(manifest)
        if manifest_id == target_manifest_id:
            break
    else:
        raise AssertionError(
            f"target manifest {target_manifest_id!r} is not in the published full-suite selector"
        )
    if target_manifest_id != "module-boundary":
        if regression_manifest is None:
            raise AssertionError(
                "the published full-suite selector is missing the regression-matrix manifest"
            )
        selected_manifests.append(regression_manifest)
    return selected_manifests


def expected_summary_for_manifests(
    manifests: list[BenchmarkManifest],
    *,
    selection_mode: str,
    manifest_known_gap_counts: dict[str, int] | None = None,
) -> dict[str, int]:
    workloads: list[Workload] = []
    regression_workloads = 0
    selected_manifest_ids: list[str] = []
    for manifest in manifests:
        manifest_id = manifest.manifest_id
        selected_manifest_workloads = manifest.selected_workloads(
            selection_mode=selection_mode
        )
        if selected_manifest_workloads:
            selected_manifest_ids.append(manifest_id)
        if manifest_id == "regression-matrix":
            regression_workloads += len(selected_manifest_workloads)
        workloads.extend(selected_manifest_workloads)
    known_gap_counts = (
        manifest_known_gap_counts
        if manifest_known_gap_counts is not None
        else {
            manifest.manifest_id: _source_tree_manifest_known_gap_count(
                SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest.manifest_id],
                selected_workload_ids=_selected_source_tree_manifest_workload_ids(
                    manifest,
                    selection_mode=selection_mode,
                ),
            )
            for manifest in manifests
            if manifest.manifest_id in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
        }
    )
    known_gap_count = sum(
        known_gap_counts.get(manifest_id, 0) for manifest_id in selected_manifest_ids
    )
    return {
        "known_gap_count": known_gap_count,
        "measured_workloads": len(workloads) - known_gap_count,
        "module_workloads": sum(1 for workload in workloads if workload.family == "module"),
        "parser_workloads": sum(1 for workload in workloads if workload.family == "parser"),
        "regression_workloads": regression_workloads,
        "total_workloads": len(workloads),
    }


def representative_measured_workload_ids(
    scorecard: dict[str, Any],
    manifest: BenchmarkManifest,
    *,
    extra_workload_ids: tuple[str, ...] = (),
) -> list[str]:
    manifest_id = manifest.manifest_id
    representative_ids: list[str] = []
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is not None:
        _append_unique_workload_ids(
            representative_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            ),
        )
    _append_unique_workload_ids(representative_ids, extra_workload_ids)
    for operation in ordered_operations(manifest.workloads):
        for workload in scorecard["workloads"]:
            if workload["manifest_id"] != manifest_id:
                continue
            if workload["operation"] != operation or workload["status"] != "measured":
                continue
            workload_id = str(workload["id"])
            if workload_id not in representative_ids:
                representative_ids.append(workload_id)
            break
    return representative_ids


def source_tree_combined_case(target_manifest_id: str) -> SourceTreeCombinedCase:
    manifests = _selected_source_tree_manifests_for_target_manifest(target_manifest_id)
    workloads = _flatten_manifest_workloads(manifests)
    target_manifest = next(
        manifest for manifest in manifests if manifest.manifest_id == target_manifest_id
    )
    common_case_kwargs = _source_tree_benchmark_common_case_kwargs(
        manifests=manifests,
        workloads=workloads,
        selection_mode="full",
    )
    return SourceTreeCombinedCase(
        **common_case_kwargs,
        manifest_expectation=_public_source_tree_manifest_expectation(target_manifest_id),
        manifest_id=target_manifest_id,
        target_manifest=target_manifest,
    )


@cache
def source_tree_combined_manifest_shape_expectation(
    manifest_id: str,
) -> SourceTreeCombinedManifestShapeExpectation:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )
    shape_expectation = manifest_expectation.shape_expectation
    if shape_expectation is None:
        raise AssertionError(
            "source-tree combined manifest "
            f"{manifest_id!r} does not define shared shape expectations"
        )
    return shape_expectation


def source_tree_combined_slice_manifest_ids() -> tuple[str, ...]:
    manifest_ids_with_expectations = {
        expectation.manifest_id for expectation in SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS
    }
    combined_target_ids = source_tree_combined_target_manifest_ids()
    missing_manifest_ids = manifest_ids_with_expectations - set(combined_target_ids)
    if missing_manifest_ids:
        raise AssertionError(
            "source-tree combined slice expectations reference manifest ids outside the "
            f"published combined selector: {sorted(missing_manifest_ids)}"
        )
    return tuple(
        manifest_id
        for manifest_id in combined_target_ids
        if manifest_id in manifest_ids_with_expectations
    )


def source_tree_combined_slice_derived_manifest_ids() -> tuple[str, ...]:
    return tuple(
        manifest_id
        for manifest_id in source_tree_combined_slice_manifest_ids()
        if SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            manifest_id
        ].representative_measured_workload_ids
        is None
        and SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id].shape_expectation
        is None
    )


def source_tree_combined_slice_expectations(
    manifest_id: str,
) -> tuple[SourceTreeCombinedSliceExpectation, ...]:
    expectations = tuple(
        expectation
        for expectation in SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS
        if expectation.manifest_id == manifest_id
    )
    if not expectations:
        raise AssertionError(
            f"unknown source-tree combined slice expectation manifest {manifest_id!r}"
        )
    return expectations


def _workload_matches_source_tree_combined_slice(
    workload: Workload,
    expectation: SourceTreeCombinedSliceExpectation,
) -> bool:
    workload_id = workload.workload_id
    required_id_suffix = expectation.required_id_suffix
    if required_id_suffix is not None and not workload_id.endswith(required_id_suffix):
        return False

    syntax_features = set(workload.syntax_features)
    categories = set(workload.categories)
    return (
        set(expectation.required_syntax_features).issubset(syntax_features)
        and syntax_features.isdisjoint(expectation.excluded_syntax_features)
        and set(expectation.required_categories).issubset(categories)
        and categories.isdisjoint(expectation.excluded_categories)
    )


def select_source_tree_combined_slice_rows(
    manifest: BenchmarkManifest,
    expectation: SourceTreeCombinedSliceExpectation,
) -> list[Workload]:
    return [
        workload
        for workload in manifest.workloads
        if _workload_matches_source_tree_combined_slice(workload, expectation)
    ]


WIDER_RANGED_REPEAT_MANIFEST_ID = "wider-ranged-repeat-quantified-group-boundary"


@cache
def _conditional_group_exists_callable_str_slice_workloads() -> tuple[Workload, ...]:
    expected_workload_ids = tuple(
        workload_id
        for expectation in _conditional_group_exists_callable_replacement_expectations()
        for workload_id in expectation.expected_workload_ids
        if not workload_id.endswith("-bytes")
    )
    return live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        expected_workload_ids,
    )


@cache
def _conditional_group_exists_callable_bytes_slice_workloads(
) -> tuple[Workload, ...]:
    expected_workload_ids = tuple(
        workload_id
        for expectation in _conditional_group_exists_callable_replacement_expectations()
        for workload_id in expectation.expected_workload_ids
        if workload_id.endswith("-bytes")
    )
    return live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        expected_workload_ids,
    )


def _conditional_group_exists_quantified_callable_str_workloads(
) -> tuple[Workload, ...]:
    expectation = _conditional_group_exists_quantified_callable_replacement_expectation()
    return live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        expectation.expected_workload_ids,
    )


def _conditional_group_exists_nested_callable_str_workloads(
) -> tuple[Workload, ...]:
    expectation = _conditional_group_exists_nested_callable_replacement_expectation()
    return live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        expectation.expected_workload_ids,
    )


@cache
def _conditional_group_exists_nested_callable_bytes_workloads() -> tuple[Workload, ...]:
    expectation = _conditional_group_exists_nested_callable_bytes_replacement_expectation()
    return live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        expectation.expected_workload_ids,
    )


@cache
def _conditional_group_exists_quantified_callable_bytes_workloads(
) -> tuple[Workload, ...]:
    expectation = (
        _conditional_group_exists_quantified_callable_bytes_replacement_expectation()
    )
    return live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        expectation.expected_workload_ids,
    )


@cache
def _conditional_group_exists_alternation_callable_bytes_workloads(
) -> tuple[Workload, ...]:
    return live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS,
    )


def _split_workload_ids_by_text_model(
    workload_ids: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (
        tuple(
            workload_id
            for workload_id in workload_ids
            if not workload_id.endswith("-bytes")
        ),
        tuple(
            workload_id
            for workload_id in workload_ids
            if workload_id.endswith("-bytes")
        ),
    )


def _selected_workload_ids(
    workloads: Iterable[Workload],
    *,
    text_model: str,
    required_categories: tuple[str, ...],
    excluded_categories: tuple[str, ...] = (),
) -> tuple[str, ...]:
    return tuple(
        workload.workload_id
        for workload in workloads
        if workload.text_model == text_model
        and all(category in workload.categories for category in required_categories)
        and all(category not in workload.categories for category in excluded_categories)
    )


def _mirrored_bytes_workload_ids(str_workload_ids: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        f"{workload_id.removesuffix('-str')}-bytes" for workload_id in str_workload_ids
    )


def _conditional_group_exists_template_replacement_expectation(
) -> SourceTreeCombinedSliceExpectation:
    return next(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id == "minimal-template-replacement-rows"
    )


def _conditional_group_exists_callable_replacement_expectations(
) -> tuple[SourceTreeCombinedSliceExpectation, ...]:
    expected_slice_ids = (
        "minimal-callable-replacement-rows",
        "minimal-callable-replacement-exception-rows",
        "minimal-callable-replacement-none-count-exception-rows",
        "alternation-heavy-callable-replacement-rows",
    )
    expectations = tuple(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id in expected_slice_ids
    )
    actual_slice_ids = tuple(expectation.slice_id for expectation in expectations)
    if actual_slice_ids != expected_slice_ids:
        raise AssertionError(
            "conditional callable replacement slice expectations drifted: "
            f"expected {expected_slice_ids!r}, got {actual_slice_ids!r}"
        )
    return expectations


def _conditional_group_exists_alternation_callable_replacement_expectation(
) -> SourceTreeCombinedSliceExpectation:
    return next(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id == "alternation-heavy-callable-replacement-rows"
    )


def _conditional_group_exists_nested_callable_replacement_expectation(
) -> SourceTreeCombinedSliceExpectation:
    return next(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id == "nested-callable-replacement-str-rows"
    )


def _conditional_group_exists_nested_callable_bytes_replacement_expectation(
) -> SourceTreeCombinedSliceExpectation:
    return next(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id == "nested-callable-replacement-bytes-rows"
    )


def _conditional_group_exists_quantified_callable_replacement_expectation(
) -> SourceTreeCombinedSliceExpectation:
    return next(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id == "quantified-callable-replacement-str-rows"
    )


def _conditional_group_exists_quantified_callable_bytes_replacement_expectation(
) -> SourceTreeCombinedSliceExpectation:
    return next(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id == "quantified-callable-replacement-bytes-rows"
    )


class SourceTreeCombinedBoundaryBenchmarkSuiteTest(unittest.TestCase):
    maxDiff = None

    def _assert_manifest_workload_contracts(
        self,
        manifest: BenchmarkManifest,
        scorecard: dict[str, object],
        workload_expectations: Iterable[tuple[str, str]],
        *,
        subtest_label: str | None = None,
    ) -> None:
        manifest_id = manifest.manifest_id
        for workload_id, expected_status in workload_expectations:
            if subtest_label is None:
                assert_benchmark_workload_contract(
                    self,
                    find_workload_record(scorecard, workload_id),
                    manifest_id=manifest_id,
                    workload_document=find_workload_document(
                        manifest,
                        workload_id,
                    ),
                    expected_status=expected_status,
                )
                continue

            with self.subTest(**{subtest_label: workload_id}):
                assert_benchmark_workload_contract(
                    self,
                    find_workload_record(scorecard, workload_id),
                    manifest_id=manifest_id,
                    workload_document=find_workload_document(
                        manifest,
                        workload_id,
                    ),
                    expected_status=expected_status,
                )

    def _assert_zero_gap_manifest_workloads_measured(
        self,
        case,
        manifest_id: str,
        expected_measured_workload_ids: tuple[str, ...],
        expected_measured_workload_count: int,
        expected_total_workload_count: int | None = None,
    ) -> None:
        _, scorecard = run_harness_scorecard(
            "rebar_harness.benchmarks",
            ["--manifest", str(case.target_manifest.path)],
            report_name="benchmarks.json",
        )
        manifest_summary = scorecard["manifests"][manifest_id]
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(
            manifest_summary["measured_workloads"],
            expected_measured_workload_count,
        )
        if expected_total_workload_count is not None:
            self.assertEqual(
                manifest_summary["workload_count"],
                expected_total_workload_count,
            )

        subtest_label: str | None = None
        if expected_total_workload_count is not None:
            subtest_label = "measured_workload_id"
        elif len(expected_measured_workload_ids) > 1:
            subtest_label = "workload_id"

        self._assert_manifest_workload_contracts(
            case.target_manifest,
            scorecard,
            (
                (workload_id, "measured")
                for workload_id in expected_measured_workload_ids
            ),
            subtest_label=subtest_label,
        )

    def _assert_zero_gap_bytes_representative_subset(
        self,
        manifest_id: str,
        expected_workload_ids: tuple[str, ...],
    ) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        self.assertIn(
            expected_workload_ids,
            manifest_definition.zero_gap_bytes_representative_subsets,
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                if manifest_definition.representative_measured_workload_ids is not None:
                    self.assertIn(
                        workload_id,
                        manifest_definition.representative_measured_workload_ids,
                    )

        case = source_tree_combined_case(manifest_id)
        manifest_expectation = case.manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        expected_measured_workload_count = len(
            case.selected_workload_ids_for_manifest(manifest_id)
        )
        expected_total_workload_count = len(case.target_manifest.workloads)
        self.assertEqual(
            expected_measured_workload_count,
            expected_total_workload_count,
        )
        for workload_id in expected_workload_ids:
            with self.subTest(public_workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                if manifest_expectation.representative_measured_workload_ids:
                    self.assertIn(
                        workload_id,
                        manifest_expectation.representative_measured_workload_ids,
                    )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_measured_workload_count,
            expected_total_workload_count=expected_total_workload_count,
        )

    def _assert_zero_gap_manifest_representative_promotion(
        self,
        manifest_id: str,
    ) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        expected_workload_ids = (
            manifest_definition.representative_measured_workload_ids
        )
        self.assertIsNotNone(expected_workload_ids)
        assert expected_workload_ids is not None
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertEqual(
            manifest_definition.representative_measured_workload_ids,
            expected_workload_ids,
        )
        self.assertEqual(
            manifest_definition.representative_known_gap_workload_ids or (),
            (),
        )

        case = source_tree_combined_case(manifest_id)
        expected_measured_workload_count = len(
            case.selected_workload_ids_for_manifest(manifest_id)
        )
        manifest_expectation = case.manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_measured_workload_ids,
            expected_workload_ids,
        )
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_measured_workload_count,
        )

    def test_raw_manifest_expectations_omit_empty_measured_representative_defaults(
        self,
    ) -> None:
        stored_empty_representative_ids = sorted(
            manifest_id
            for manifest_id, expectation in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
            if expectation.representative_measured_workload_ids == ()
        )
        self.assertEqual(stored_empty_representative_ids, [])

    def test_manifest_gap_inventories_derive_public_known_gap_counts(self) -> None:
        for manifest_id, manifest_definition in (
            SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
        ):
            expected_ids = manifest_definition.known_gap_workload_ids
            if expected_ids is None:
                continue
            with self.subTest(manifest_id=manifest_id):
                self.assertFalse(hasattr(manifest_definition, "known_gap_count"))
                self.assertEqual(
                    source_tree_combined_case(manifest_id).manifest_expectation.known_gap_count,
                    len(expected_ids),
                )

    def test_zero_gap_manifests_omit_raw_defaults_but_public_case_restores_them(
        self,
    ) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            "pattern-boundary"
        ]
        self.assertFalse(hasattr(manifest_definition, "known_gap_count"))
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )

        manifest_expectation = source_tree_combined_case(
            "pattern-boundary"
        ).manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )

    def test_zero_default_public_manifest_expectations_restore_empty_representative_ids(
        self,
    ) -> None:
        manifest_expectation = source_tree_combined_case(
            "collection-replacement-boundary"
        ).manifest_expectation
        self.assertEqual(
            manifest_expectation.representative_measured_workload_ids,
            (),
        )

    def test_literal_flag_manifest_no_longer_classifies_ascii_pair_as_known_gaps(
        self,
    ) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            "literal-flag-boundary"
        ]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )

        case = source_tree_combined_case("literal-flag-boundary")
        manifest_expectation = case.manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "literal-flag-boundary",
            (
                "module-search-ignorecase-ascii-cold-gap",
                "pattern-search-ignorecase-ascii-warm-gap",
            ),
            10,
        )

    def test_zero_gap_manifest_representative_promotions_keep_selected_rows_measured(
        self,
    ) -> None:
        promotion_manifest_ids = tuple(
            manifest_id
            for manifest_id in source_tree_combined_target_manifest_ids()
            if SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                manifest_id
            ].promote_zero_gap_representatives
        )
        self.assertEqual(
            promotion_manifest_ids,
            (
                "grouped-named-boundary",
                "numbered-backreference-boundary",
                "nested-group-boundary",
                "optional-group-boundary",
            ),
        )
        for manifest_id in promotion_manifest_ids:
            with self.subTest(manifest_id=manifest_id):
                self._assert_zero_gap_manifest_representative_promotion(
                    manifest_id
                )

    def test_combined_target_manifest_ids_exclude_only_definition_owned_base_manifests(
        self,
    ) -> None:
        excluded_manifest_ids = tuple(
            manifest.manifest_id
            for manifest in published_benchmark_manifests()
            if SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                manifest.manifest_id
            ].exclude_from_combined_targets
        )
        self.assertEqual(
            excluded_manifest_ids,
            ("compile-matrix", "regression-matrix"),
        )
        self.assertEqual(
            source_tree_combined_target_manifest_ids(),
            tuple(
                manifest.manifest_id
                for manifest in published_benchmark_manifests()
                if not SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                    manifest.manifest_id
                ].exclude_from_combined_targets
            ),
        )

    def test_literal_flag_combined_case_preserves_expected_manifest_paths(self) -> None:
        case = source_tree_combined_case("literal-flag-boundary")

        self.assertEqual(
            [manifest.path.name for manifest in case.manifests],
            [
                "compile_matrix.py",
                "module_boundary.py",
                "pattern_boundary.py",
                "collection_replacement_boundary.py",
                "literal_flag_boundary.py",
                "regression_matrix.py",
            ],
        )
        self.assertEqual(
            [relative_manifest_path(manifest.path) for manifest in case.manifests],
            [
                "benchmarks/workloads/compile_matrix.py",
                "benchmarks/workloads/module_boundary.py",
                "benchmarks/workloads/pattern_boundary.py",
                "benchmarks/workloads/collection_replacement_boundary.py",
                "benchmarks/workloads/literal_flag_boundary.py",
                "benchmarks/workloads/regression_matrix.py",
            ],
        )

    def test_counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured(
        self,
    ) -> None:
        for manifest_id in source_tree_combined_fully_measured_manifest_ids(
            "counted-repeat"
        ):
            fully_measured_expectation = (
                source_tree_combined_fully_measured_manifest_expectation(manifest_id)
            )
            expected_workload_ids = (
                fully_measured_expectation.representative_measured_workload_ids
            )
            expected_measured_workload_count = (
                fully_measured_expectation.expected_measured_workload_count
            )
            with self.subTest(manifest_id=manifest_id):
                manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                    manifest_id
                ]
                self.assertIsNone(manifest_definition.known_gap_workload_ids)
                self.assertEqual(
                    manifest_definition.fully_measured_expectation,
                    fully_measured_expectation,
                )
                self.assertEqual(
                    manifest_definition.representative_measured_workload_ids,
                    expected_workload_ids,
                )
                self.assertEqual(
                    manifest_definition.representative_known_gap_workload_ids,
                    (),
                )

                case = source_tree_combined_case(manifest_id)
                manifest_expectation = case.manifest_expectation
                self.assertEqual(manifest_expectation.known_gap_count, 0)
                self.assertEqual(
                    manifest_expectation.representative_measured_workload_ids,
                    expected_workload_ids,
                )
                self.assertEqual(
                    manifest_expectation.representative_known_gap_workload_ids,
                    (),
                )

                self._assert_zero_gap_manifest_workloads_measured(
                    case,
                    manifest_id,
                    expected_workload_ids,
                    expected_measured_workload_count,
                )

    def test_zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured(
        self,
    ) -> None:
        zero_gap_bytes_subsets_by_manifest = {
            manifest_id: manifest_definition.zero_gap_bytes_representative_subsets
            for manifest_id, manifest_definition in (
                SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
            )
            if manifest_definition.zero_gap_bytes_representative_subsets
        }
        expected_subset_counts = {
            "conditional-group-exists-boundary": 5,
            "wider-ranged-repeat-quantified-group-boundary": 6,
            "open-ended-quantified-group-boundary": 5,
            "branch-local-backreference-boundary": 1,
        }
        self.assertEqual(
            {
                manifest_id: len(representative_subsets)
                for manifest_id, representative_subsets in (
                    zero_gap_bytes_subsets_by_manifest.items()
                )
            },
            expected_subset_counts,
        )
        self.assertEqual(
            sum(
                len(representative_subsets)
                for representative_subsets in zero_gap_bytes_subsets_by_manifest.values()
            ),
            sum(expected_subset_counts.values()),
        )
        for manifest_id, representative_subsets in zero_gap_bytes_subsets_by_manifest.items():
            for expected_workload_ids in representative_subsets:
                with self.subTest(manifest_id=manifest_id):
                    self._assert_zero_gap_bytes_representative_subset(
                        manifest_id,
                        expected_workload_ids,
                    )

    def test_nested_group_callable_replacement_manifest_promotes_bounded_nested_group_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-nested-group-numbered-warm-bytes",
            "module-subn-callable-nested-group-numbered-warm-bytes",
            "pattern-sub-callable-nested-group-numbered-purged-bytes",
            "pattern-subn-callable-nested-group-numbered-purged-bytes",
            "module-sub-callable-nested-group-named-warm-bytes",
            "module-subn-callable-nested-group-named-warm-bytes",
            "pattern-sub-callable-nested-group-named-purged-bytes",
            "pattern-subn-callable-nested-group-named-purged-bytes",
        )

        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )

        case = source_tree_combined_case(manifest_id)
        expected_workload_count = len(
            case.selected_workload_ids_for_manifest(manifest_id)
        )
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        manifest_expectation = case.manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self.assertEqual(manifest_expectation.representative_measured_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(public_workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    public_representatives,
                )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        template_expectation = (
            _conditional_group_exists_template_replacement_expectation()
        )
        case = source_tree_combined_case(manifest_id)
        matched_rows = tuple(
            select_source_tree_combined_slice_rows(
                case.target_manifest,
                template_expectation,
            )
        )
        expected_workload_ids = template_expectation.expected_workload_ids
        expected_workload_count = len(case.selected_workload_ids_for_manifest(manifest_id))

        self.assertEqual(
            tuple(workload.workload_id for workload in matched_rows),
            expected_workload_ids,
        )
        self.assertEqual({workload.text_model for workload in matched_rows}, {"str", "bytes"})
        for workload_id in CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_template_bytes_workloads_keep_bytes_template_payloads_through_round_trip(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        case = source_tree_combined_case(manifest_id)
        workloads_by_id = records_by_string_id(
            (
                workload
                for workload in case.target_manifest.workloads
                if workload.workload_id
                in CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS
                or workload.workload_id
                in CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
            ),
            id_attr="workload_id",
        )

        self.assertEqual(
            tuple(workloads_by_id),
            CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS,
        )

        for workload_id in CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS:
            expected_serialized_replacement = "\\g<word>x" if "-named-" in workload_id else "\\1x"
            expected_text_model = "bytes" if workload_id.endswith("-bytes") else "str"
            expected_template_payload = (
                b"\\g<word>x"
                if "-named-" in workload_id and workload_id.endswith("-bytes")
                else "\\g<word>x"
                if "-named-" in workload_id
                else b"\\1x"
                if workload_id.endswith("-bytes")
                else "\\1x"
            )
            if "negative-count" in workload_id:
                expected_count = -1
                expected_result = (
                    (b"abcdaceabcd", 0)
                    if workload_id.endswith("-bytes") and "-subn-" in workload_id
                    else ("abcdaceabcd", 0)
                    if "-subn-" in workload_id
                    else b"abcdaceabcd"
                    if workload_id.endswith("-bytes")
                    else "abcdaceabcd"
                )
            else:
                expected_count = 1 if "-subn-" in workload_id else 0
                expected_result = (
                    (b"zzxzz", 1)
                    if workload_id.endswith("-bytes") and "-subn-" in workload_id
                    else ("zzxzz", 1)
                    if "-subn-" in workload_id
                    else b"zzbxzz"
                    if workload_id.endswith("-bytes")
                    else "zzbxzz"
                )

            with self.subTest(workload_id=workload_id):
                workload = workloads_by_id[workload_id]
                payload = workload_to_payload(workload)
                round_tripped = workload_from_payload(payload)

                self.assertEqual(workload.text_model, expected_text_model)
                self.assertEqual(payload["text_model"], expected_text_model)
                self.assertEqual(payload["replacement"], expected_serialized_replacement)
                self.assertEqual(payload["count"], expected_count)
                self.assertIsInstance(
                    workload.pattern_payload(),
                    bytes if workload_id.endswith("-bytes") else str,
                )
                self.assertIsInstance(
                    workload.haystack_payload(),
                    bytes if workload_id.endswith("-bytes") else str,
                )
                self.assertEqual(
                    workload.replacement_payload(),
                    expected_template_payload,
                )
                self.assertEqual(
                    run_benchmark_workload_with_cpython(workload),
                    expected_result,
                )

                self.assertEqual(round_tripped.text_model, expected_text_model)
                self.assertEqual(round_tripped.count, expected_count)
                self.assertIsInstance(
                    round_tripped.pattern_payload(),
                    bytes if workload_id.endswith("-bytes") else str,
                )
                self.assertIsInstance(
                    round_tripped.haystack_payload(),
                    bytes if workload_id.endswith("-bytes") else str,
                )
                self.assertEqual(
                    round_tripped.replacement_payload(),
                    expected_template_payload,
                )
                self.assertEqual(
                    run_benchmark_workload_with_cpython(round_tripped),
                    expected_result,
                )

    def test_conditional_group_exists_callable_bytes_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expected_workload_ids = CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS
        case = source_tree_combined_case(manifest_id)
        expected_workload_count = len(case.selected_workload_ids_for_manifest(manifest_id))
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_callable_none_count_bytes_manifest_promotes_rows_to_measured(
        self,
    ) -> None:
        self._assert_zero_gap_bytes_representative_subset(
            "conditional-group-exists-boundary",
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS,
        )

    def test_conditional_group_exists_nested_callable_str_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectation = _conditional_group_exists_nested_callable_replacement_expectation()
        case = source_tree_combined_case(manifest_id)
        matched_rows = tuple(
            select_source_tree_combined_slice_rows(case.target_manifest, expectation)
        )
        expected_workload_ids = CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
        expected_workload_count = len(case.selected_workload_ids_for_manifest(manifest_id))

        self.assertEqual(
            tuple(workload.workload_id for workload in matched_rows),
            expected_workload_ids,
        )
        self.assertEqual({workload.text_model for workload in matched_rows}, {"str"})
        self.assertEqual(
            Counter((workload.operation, workload.count) for workload in matched_rows),
            Counter(
                {
                    ("module.sub", 0): 4,
                    ("module.sub", None): 1,
                    ("module.sub", -1): 1,
                    ("module.subn", 1): 4,
                    ("module.subn", None): 1,
                    ("module.subn", -1): 1,
                    ("pattern.sub", 0): 4,
                    ("pattern.sub", None): 1,
                    ("pattern.sub", -1): 1,
                    ("pattern.subn", 1): 4,
                    ("pattern.subn", None): 1,
                    ("pattern.subn", -1): 1,
                }
            ),
        )
        self.assertEqual(
            Counter("exception" in workload.categories for workload in matched_rows),
            Counter({False: 16, True: 8}),
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_nested_callable_bytes_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expected_workload_ids = CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
        self._assert_zero_gap_bytes_representative_subset(
            manifest_id,
            expected_workload_ids,
        )

    def test_conditional_group_exists_quantified_callable_str_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectation = _conditional_group_exists_quantified_callable_replacement_expectation()
        case = source_tree_combined_case(manifest_id)
        matched_rows = tuple(
            select_source_tree_combined_slice_rows(case.target_manifest, expectation)
        )
        expected_workload_ids = CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
        expected_workload_count = len(case.selected_workload_ids_for_manifest(manifest_id))

        self.assertEqual(
            tuple(workload.workload_id for workload in matched_rows),
            expected_workload_ids,
        )
        self.assertEqual({workload.text_model for workload in matched_rows}, {"str"})
        self.assertEqual(
            Counter((workload.operation, workload.count) for workload in matched_rows),
            Counter(
                {
                    ("module.sub", 0): 4,
                    ("module.sub", None): 1,
                    ("module.sub", -1): 4,
                    ("module.subn", 1): 4,
                    ("module.subn", None): 1,
                    ("module.subn", -1): 4,
                    ("pattern.sub", 0): 4,
                    ("pattern.sub", None): 1,
                    ("pattern.sub", -1): 4,
                    ("pattern.subn", 1): 4,
                    ("pattern.subn", None): 1,
                    ("pattern.subn", -1): 4,
                }
            ),
        )
        self.assertEqual(
            Counter("exception" in workload.categories for workload in matched_rows),
            Counter({False: 28, True: 8}),
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_quantified_callable_bytes_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expected_workload_ids = (
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
        )
        self._assert_zero_gap_bytes_representative_subset(
            manifest_id,
            expected_workload_ids,
        )

    def test_conditional_group_exists_nested_callable_str_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = _conditional_group_exists_nested_callable_str_workloads()

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS,
        )

        for source_workload in source_workloads:
            with self.subTest(workload_id=source_workload.workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)
                expected_signature = callable_match_group_signature(
                    source_workload.replacement_payload()
                )
                observed_signature = callable_match_group_signature(
                    round_tripped.replacement_payload()
                )

                self.assertEqual(payload["text_model"], "str")
                self.assertEqual(round_tripped.text_model, "str")
                self.assertEqual(payload["count"], source_workload.count)
                self.assertEqual(round_tripped.count, source_workload.count)
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.pattern_payload(),
                    source_workload.pattern_payload(),
                )
                self.assertEqual(
                    round_tripped.haystack_payload(),
                    source_workload.haystack_payload(),
                )
                self.assertEqual(observed_signature, expected_signature)
                self.assertIsNotNone(observed_signature)
                assert observed_signature is not None
                self.assertIsInstance(observed_signature[2], str)
                self.assertIsInstance(observed_signature[3], str)

                if source_workload.expected_exception is None:
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_nested_callable_bytes_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = _conditional_group_exists_nested_callable_bytes_workloads()

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS,
        )

        def normalized_text_model_payload(value: str | bytes | None) -> str | None:
            if isinstance(value, bytes):
                return value.decode("latin-1")
            return value

        for source_workload in source_workloads:
            workload_id = source_workload.workload_id
            expected_replacement = {
                "type": "callable_match_group",
                "group": "word" if "-named-" in workload_id else 1,
                "suffix": "x",
            }
            expected_signature = (
                "callable_match_group",
                expected_replacement["group"],
                b"",
                b"x",
            )

            with self.subTest(workload_id=workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)
                observed_signature = callable_match_group_signature(
                    round_tripped.replacement_payload()
                )

                self.assertEqual(payload["text_model"], "bytes")
                self.assertEqual(round_tripped.text_model, "bytes")
                self.assertEqual(payload["replacement"], expected_replacement)
                self.assertEqual(payload["count"], source_workload.count)
                self.assertEqual(round_tripped.count, source_workload.count)
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    normalized_text_model_payload(payload["pattern"]),
                    source_workload.pattern,
                )
                self.assertEqual(
                    normalized_text_model_payload(payload["haystack"]),
                    source_workload.haystack,
                )
                self.assertEqual(
                    normalized_text_model_payload(round_tripped.pattern),
                    source_workload.pattern,
                )
                self.assertEqual(
                    normalized_text_model_payload(round_tripped.haystack),
                    source_workload.haystack,
                )
                self.assertEqual(
                    callable_match_group_signature(
                        source_workload.replacement_payload()
                    ),
                    expected_signature,
                )
                self.assertEqual(observed_signature, expected_signature)
                self.assertIsNotNone(observed_signature)
                assert observed_signature is not None
                self.assertIsInstance(observed_signature[2], bytes)
                self.assertIsInstance(observed_signature[3], bytes)
                if source_workload.expected_exception is None:
                    expected_result = run_benchmark_workload_with_cpython(
                        source_workload
                    )
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        expected_result,
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_nested_callable_workloads_anchor_to_unique_published_cases(
        self,
    ) -> None:
        workloads = (
            _conditional_group_exists_nested_callable_str_workloads()
            + _conditional_group_exists_nested_callable_bytes_workloads()
        )
        case_ids_by_signature = published_case_ids_by_signature(
            _conditional_group_exists_nested_callable_correctness_case_signature
        )
        anchored_case_ids: list[str] = []

        for workload in workloads:
            signature = _conditional_group_exists_nested_callable_workload_signature(
                workload
            )
            with self.subTest(workload_id=workload.workload_id):
                case_ids = case_ids_by_signature.get(signature)
                self.assertIsNotNone(
                    case_ids,
                    f"missing published correctness case for {workload.workload_id!r}",
                )
                assert case_ids is not None
                self.assertEqual(
                    len(case_ids),
                    1,
                    f"expected a unique published case for {workload.workload_id!r}",
                )
                anchored_case_ids.append(case_ids[0])

        self.assertEqual(len(anchored_case_ids), len(workloads))
        self.assertEqual(len(set(anchored_case_ids)), len(anchored_case_ids))

    def test_conditional_group_exists_quantified_callable_str_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = _conditional_group_exists_quantified_callable_str_workloads()

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
        )

        for source_workload in source_workloads:
            with self.subTest(workload_id=source_workload.workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)
                expected_signature = callable_match_group_signature(
                    source_workload.replacement_payload()
                )
                observed_signature = callable_match_group_signature(
                    round_tripped.replacement_payload()
                )

                self.assertEqual(payload["text_model"], "str")
                self.assertEqual(round_tripped.text_model, "str")
                self.assertEqual(payload["count"], source_workload.count)
                self.assertEqual(round_tripped.count, source_workload.count)
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.pattern_payload(),
                    source_workload.pattern_payload(),
                )
                self.assertEqual(
                    round_tripped.haystack_payload(),
                    source_workload.haystack_payload(),
                )
                self.assertEqual(observed_signature, expected_signature)
                self.assertIsNotNone(observed_signature)
                assert observed_signature is not None
                self.assertIsInstance(observed_signature[2], str)
                self.assertIsInstance(observed_signature[3], str)

                if source_workload.expected_exception is None:
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_quantified_callable_bytes_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = _conditional_group_exists_quantified_callable_bytes_workloads()

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
        )

        for source_workload in source_workloads:
            with self.subTest(workload_id=source_workload.workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)
                expected_signature = callable_match_group_signature(
                    source_workload.replacement_payload()
                )
                observed_signature = callable_match_group_signature(
                    round_tripped.replacement_payload()
                )

                self.assertEqual(payload["text_model"], "bytes")
                self.assertEqual(round_tripped.text_model, "bytes")
                self.assertEqual(payload["count"], source_workload.count)
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.pattern_payload(),
                    source_workload.pattern_payload(),
                )
                self.assertEqual(
                    round_tripped.haystack_payload(),
                    source_workload.haystack_payload(),
                )
                self.assertEqual(observed_signature, expected_signature)

                if source_workload.expected_exception is None:
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_quantified_callable_workloads_anchor_to_unique_published_cases(
        self,
    ) -> None:
        workloads = (
            _conditional_group_exists_quantified_callable_str_workloads()
            + _conditional_group_exists_quantified_callable_bytes_workloads()
        )
        case_ids_by_signature = published_case_ids_by_signature(
            _conditional_group_exists_quantified_callable_correctness_case_signature
        )
        anchored_case_ids: list[str] = []

        for workload in workloads:
            signature = _conditional_group_exists_quantified_callable_workload_signature(
                workload
            )
            with self.subTest(workload_id=workload.workload_id):
                case_ids = case_ids_by_signature.get(signature)
                self.assertIsNotNone(
                    case_ids,
                    f"missing published correctness case for {workload.workload_id!r}",
                )
                assert case_ids is not None
                self.assertEqual(
                    len(case_ids),
                    1,
                    f"expected a unique published case for {workload.workload_id!r}",
                )
                anchored_case_ids.append(case_ids[0])

        self.assertEqual(len(anchored_case_ids), len(workloads))
        self.assertEqual(len(set(anchored_case_ids)), len(anchored_case_ids))

    def test_conditional_group_exists_callable_str_slice_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = _conditional_group_exists_callable_str_slice_workloads()

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            tuple(
                workload_id
                for expectation in _conditional_group_exists_callable_replacement_expectations()
                for workload_id in expectation.expected_workload_ids
                if not workload_id.endswith("-bytes")
            ),
        )

        for source_workload in source_workloads:
            with self.subTest(workload_id=source_workload.workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)
                expected_signature = callable_match_group_signature(
                    source_workload.replacement_payload()
                )
                observed_signature = callable_match_group_signature(
                    round_tripped.replacement_payload()
                )

                self.assertEqual(payload["text_model"], "str")
                self.assertEqual(round_tripped.text_model, "str")
                self.assertEqual(payload["count"], source_workload.count)
                self.assertEqual(round_tripped.count, source_workload.count)
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.pattern_payload(),
                    source_workload.pattern_payload(),
                )
                self.assertEqual(
                    round_tripped.haystack_payload(),
                    source_workload.haystack_payload(),
                )
                self.assertEqual(observed_signature, expected_signature)
                self.assertIsNotNone(observed_signature)
                assert observed_signature is not None
                self.assertIsInstance(observed_signature[2], str)
                self.assertIsInstance(observed_signature[3], str)

                if source_workload.expected_exception is None:
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_callable_bytes_slice_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = _conditional_group_exists_callable_bytes_slice_workloads()

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            tuple(
                workload_id
                for expectation in _conditional_group_exists_callable_replacement_expectations()
                for workload_id in expectation.expected_workload_ids
                if workload_id.endswith("-bytes")
            ),
        )

        for source_workload in source_workloads:
            with self.subTest(workload_id=source_workload.workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)
                expected_signature = callable_match_group_signature(
                    source_workload.replacement_payload()
                )
                observed_signature = callable_match_group_signature(
                    round_tripped.replacement_payload()
                )

                self.assertEqual(payload["text_model"], "bytes")
                self.assertEqual(round_tripped.text_model, "bytes")
                self.assertEqual(payload["count"], source_workload.count)
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.pattern_payload(),
                    source_workload.pattern_payload(),
                )
                self.assertEqual(
                    round_tripped.haystack_payload(),
                    source_workload.haystack_payload(),
                )
                self.assertEqual(observed_signature, expected_signature)
                self.assertIsNotNone(observed_signature)
                assert observed_signature is not None
                self.assertIsInstance(observed_signature[2], bytes)
                self.assertIsInstance(observed_signature[3], bytes)

                if source_workload.expected_exception is None:
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_alternation_callable_bytes_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        for source_workload in (
            _conditional_group_exists_alternation_callable_bytes_workloads()
        ):
            with self.subTest(workload_id=source_workload.workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)

                self.assertEqual(payload["text_model"], "bytes")
                self.assertEqual(round_tripped.text_model, "bytes")
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.pattern_payload(),
                    source_workload.pattern_payload(),
                )
                self.assertEqual(
                    round_tripped.haystack_payload(),
                    source_workload.haystack_payload(),
                )
                self.assertEqual(
                    _text_model_agnostic_callable_match_group_signature(
                        round_tripped.replacement_payload()
                    ),
                    _text_model_agnostic_callable_match_group_signature(
                        source_workload.replacement_payload()
                    ),
                )

                if source_workload.expected_exception is None:
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_nested_group_alternation_manifest_promotes_broader_range_open_ended_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-alternation-boundary"
        expected_workload_ids = (
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-bytes",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
        )

        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )

        case = source_tree_combined_case(manifest_id)
        expected_workload_count = len(
            case.selected_workload_ids_for_manifest(manifest_id)
        )
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        manifest_expectation = case.manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self.assertEqual(manifest_expectation.representative_measured_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(public_workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    public_representatives,
                )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_quantified_alternation_manifest_promotes_bounded_branch_backref_conditional_nested_branch_broader_range_open_ended_and_backtracking_heavy_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "quantified-alternation-boundary"
        fully_measured_expectation = (
            source_tree_combined_fully_measured_manifest_expectation(
                manifest_id
            )
        )
        expected_workload_ids = (
            fully_measured_expectation.representative_measured_workload_ids
        )
        expected_measured_workload_count = (
            fully_measured_expectation.expected_measured_workload_count
        )
        expected_total_workload_count = (
            fully_measured_expectation.expected_total_workload_count
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertEqual(
            manifest_definition.fully_measured_expectation,
            fully_measured_expectation,
        )
        self.assertEqual(
            manifest_definition.representative_measured_workload_ids,
            expected_workload_ids,
        )
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )

        case = source_tree_combined_case(manifest_id)
        manifest_expectation = case.manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_measured_workload_ids,
            expected_workload_ids,
        )
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_measured_workload_count,
            expected_total_workload_count=expected_total_workload_count,
        )

    def test_nested_group_replacement_manifest_promotes_broader_range_open_ended_conditional_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-replacement-boundary"
        expected_workload_ids = (
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_broader_range_open_ended_conditional_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_replacement_manifest_promotes_broader_range_open_ended_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-replacement-boundary"
        expected_workload_ids = (
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_replacement_manifest_promotes_broader_range_branch_local_backreference_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-replacement-boundary"
        expected_workload_ids = (
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_replacement_manifest_promotes_broader_range_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-replacement-boundary"
        expected_workload_ids = (
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_nested_broader_range_backtracking_heavy_str_and_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_nested_broader_range_open_ended_backtracking_heavy_str_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_nested_broader_range_open_ended_backtracking_heavy_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_broader_range_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_quantified_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_broader_range_conditional_branch_local_backreference_str_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-str",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-str",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_broader_range_conditional_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_broader_range_open_ended_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_shape_backed_manifests_keep_derived_representatives(self) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            "pattern-boundary"
        ]
        shape_expectation = source_tree_combined_manifest_shape_expectation(
            "pattern-boundary"
        )
        self.assertIs(manifest_definition.shape_expectation, shape_expectation)
        self.assertEqual(
            source_tree_combined_manifest_representative_measured_workload_ids(
                "pattern-boundary"
            ),
            shape_expectation.representative_measured_workload_ids,
        )

    def test_regression_manifest_is_fully_measured_on_the_shared_surface(self) -> None:
        scorecard_case = source_tree_scorecard_case("regression-pack-full")
        self.assertEqual(
            scorecard_case.manifest_expectations["regression-matrix"].known_gap_count,
            0,
        )

        _, scorecard = run_harness_scorecard(
            "rebar_harness.benchmarks",
            [
                "--manifest",
                str(REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"),
            ],
            report_name="benchmarks.json",
        )

        manifest_summary = scorecard["manifests"]["regression-matrix"]
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(manifest_summary["measured_workloads"], 8)

        self._assert_manifest_workload_contracts(
            scorecard_case.manifest_for_id("regression-matrix"),
            scorecard,
            (
                ("regression-parser-bytes-backreference-purged", "measured"),
                ("regression-module-compile-multiline-purged", "measured"),
                ("regression-module-compile-multiline-purged-bytes", "measured"),
                ("regression-module-compile-verbose-purged-bytes", "measured"),
            ),
        )

    def test_source_tree_combined_slice_filters_match_expected_manifest_rows(self) -> None:
        for manifest_id in source_tree_combined_slice_manifest_ids():
            with self.subTest(manifest_id=manifest_id):
                manifest = source_tree_combined_case(manifest_id).target_manifest
                for expectation in source_tree_combined_slice_expectations(manifest_id):
                    with self.subTest(slice_id=expectation.slice_id):
                        self.assertEqual(
                            tuple(
                                workload.workload_id
                                for workload in select_source_tree_combined_slice_rows(
                                    manifest,
                                    expectation,
                                )
                            ),
                            expectation.expected_workload_ids,
                        )

    def test_scoped_manifests_keep_slice_backed_representatives(self) -> None:
        for manifest_id in source_tree_combined_slice_derived_manifest_ids():
            with self.subTest(manifest_id=manifest_id):
                case = source_tree_combined_case(manifest_id)
                self.assertEqual(
                    case.manifest_expectation.representative_measured_workload_ids,
                    (),
                )
                self.assertEqual(
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                    tuple(
                        workload_id
                        for expectation in source_tree_combined_slice_expectations(
                            manifest_id
                        )
                        for workload_id in expectation.expected_workload_ids
                    ),
                )

    def test_runner_regenerates_combined_source_tree_boundary_scorecards(self) -> None:
        for target_manifest_id in source_tree_combined_target_manifest_ids():
            with self.subTest(manifest_id=target_manifest_id):
                case = source_tree_combined_case(target_manifest_id)
                manifest_expectation = case.manifest_expectation
                summary, scorecard = run_harness_scorecard(
                    "rebar_harness.benchmarks",
                    [
                        argument
                        for manifest in case.manifests
                        for argument in ("--manifest", str(manifest.path))
                    ],
                    report_name="benchmarks.json",
                )

                assert_source_tree_benchmark_contract(
                    self,
                    scorecard,
                    summary,
                    expected_phase=case.expected_phase,
                    expected_runner_version=case.expected_runner_version,
                    expected_adapter=case.expected_adapter,
                    expected_manifests=case.manifests,
                    expected_manifest_paths=[
                        relative_manifest_path(manifest.path)
                        for manifest in case.manifests
                    ],
                    expected_selection_mode=case.selection_mode,
                    tracked_report_path=TRACKED_REPORT_PATH,
                )
                self.assertEqual(summary, case.expected_summary)

                manifest_id = case.manifest_id
                manifest_summary = scorecard["manifests"][manifest_id]
                manifest_record = find_manifest_record(scorecard, manifest_id)
                assert_benchmark_manifest_contract(
                    self,
                    manifest_summary,
                    manifest_record,
                    manifest=case.target_manifest,
                    manifest_path=relative_manifest_path(case.target_manifest.path),
                    known_gap_count=manifest_expectation.known_gap_count,
                    selection_mode=case.selection_mode,
                    selected_workload_ids=case.selected_workload_ids_for_manifest(
                        manifest_id
                    ),
                )

                representative_ids = representative_measured_workload_ids(
                    scorecard,
                    case.target_manifest,
                    extra_workload_ids=manifest_expectation.representative_measured_workload_ids,
                )
                representative_gap_ids = set(
                    manifest_expectation.representative_known_gap_workload_ids
                )
                representative_ids.extend(
                    manifest_expectation.representative_known_gap_workload_ids
                )

                seen_ids: set[str] = set()
                workload_expectations: list[tuple[str, str]] = []
                for workload_id in representative_ids:
                    if workload_id in seen_ids:
                        continue
                    seen_ids.add(workload_id)
                    workload_expectations.append(
                        (
                            workload_id,
                            (
                                "unimplemented"
                                if workload_id in representative_gap_ids
                                else "measured"
                            ),
                        )
                    )

                self._assert_manifest_workload_contracts(
                    case.target_manifest,
                    scorecard,
                    workload_expectations,
                )

    def test_selected_combined_source_tree_manifest_slices_stay_covered(self) -> None:
        for manifest_id in source_tree_combined_slice_manifest_ids():
            with self.subTest(manifest_id=manifest_id):
                case = source_tree_combined_case(manifest_id)
                _, scorecard = run_harness_scorecard(
                    "rebar_harness.benchmarks",
                    [
                        argument
                        for manifest in case.manifests
                        for argument in ("--manifest", str(manifest.path))
                    ],
                    report_name="benchmarks.json",
                )

                manifest_summary = scorecard["manifests"][manifest_id]
                self.assertEqual(
                    manifest_summary["known_gap_count"],
                    case.manifest_expectation.known_gap_count,
                )

                for expectation in source_tree_combined_slice_expectations(manifest_id):
                    with self.subTest(slice_id=expectation.slice_id):
                        self._assert_source_tree_combined_manifest_slice(
                            case.target_manifest,
                            scorecard,
                            expectation=expectation,
                        )

    def _assert_source_tree_combined_manifest_slice(
        self,
        manifest: BenchmarkManifest,
        scorecard: dict[str, object],
        *,
        expectation: SourceTreeCombinedSliceExpectation,
    ) -> None:
        manifest_id = expectation.manifest_id
        expected_workload_ids = expectation.expected_workload_ids
        expected_status = expectation.expected_status
        matched_rows = select_source_tree_combined_slice_rows(
            manifest,
            expectation,
        )

        self.assertEqual(
            tuple(workload.workload_id for workload in matched_rows),
            expected_workload_ids,
        )
        self.assertEqual(
            {workload.pattern for workload in matched_rows},
            expectation.expected_patterns,
        )
        self.assertEqual(
            {workload.operation for workload in matched_rows},
            expectation.expected_operations,
        )
        self.assertEqual(
            {
                str(workload.haystack)
                for workload in matched_rows
                if workload.haystack is not None
            },
            expectation.expected_haystacks,
        )

        for workload in matched_rows:
            with self.subTest(
                slice_id=expectation.slice_id,
                workload_id=workload.workload_id,
            ):
                for category in expectation.required_row_categories:
                    self.assertIn(category, workload.categories)

        scorecard_rows = [
            workload
            for workload in scorecard["workloads"]
            if workload["manifest_id"] == manifest_id
            and workload["id"] in expected_workload_ids
        ]
        self.assertEqual(
            {workload["id"] for workload in scorecard_rows},
            set(expected_workload_ids),
        )

        with self.subTest(slice_id=expectation.slice_id):
            self._assert_manifest_workload_contracts(
                manifest,
                scorecard,
                (
                    (workload_id, expected_status)
                    for workload_id in expected_workload_ids
                ),
                subtest_label="workload_id",
            )

    def test_wider_ranged_repeat_manifest_shape_stays_covered_in_combined_suite(
        self,
    ) -> None:
        case = source_tree_combined_case(WIDER_RANGED_REPEAT_MANIFEST_ID)
        shape_expectation = source_tree_combined_manifest_shape_expectation(
            WIDER_RANGED_REPEAT_MANIFEST_ID
        )
        _, scorecard = run_harness_scorecard(
            "rebar_harness.benchmarks",
            [
                argument
                for manifest in case.manifests
                for argument in ("--manifest", str(manifest.path))
            ],
            report_name="benchmarks.json",
        )

        manifest_summary = scorecard["manifests"][WIDER_RANGED_REPEAT_MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(
            manifest_summary["measured_workloads"],
            len(case.target_manifest.workloads),
        )
        self.assertEqual(
            manifest_summary["workload_count"],
            len(case.target_manifest.workloads),
        )

        self._assert_manifest_workload_contracts(
            case.target_manifest,
            scorecard,
            (
                (workload_id, "measured")
                for workload_id in shape_expectation.representative_measured_workload_ids
            ),
            subtest_label="workload_id",
        )

        for pattern_group in shape_expectation.pattern_groups:
            with self.subTest(slice_id=pattern_group.slice_id):
                self._assert_source_tree_combined_pattern_group(
                    case.target_manifest,
                    scorecard,
                    manifest_id=WIDER_RANGED_REPEAT_MANIFEST_ID,
                    expectation=pattern_group,
                )

    def _assert_source_tree_combined_pattern_group(
        self,
        manifest: BenchmarkManifest,
        scorecard: dict[str, object],
        *,
        manifest_id: str,
        expectation: SourceTreeCombinedPatternGroupExpectation,
    ) -> None:
        slice_id = expectation.slice_id
        patterns = expectation.patterns
        required_operations = expectation.required_operations
        required_categories = expectation.required_categories
        search_haystacks = expectation.search_haystacks
        search_haystack_substrings = expectation.search_haystack_substrings
        pattern_haystacks = expectation.pattern_haystacks
        manifest_rows = [
            workload
            for workload in manifest.workloads
            if workload.pattern in patterns
        ]

        self.assertGreaterEqual(
            len(manifest_rows),
            expectation.minimum_rows,
            f"expected benchmark rows for the {slice_id} slice",
        )

        for pattern in patterns:
            pattern_rows = [
                workload for workload in manifest_rows if workload.pattern == pattern
            ]
            self.assertGreaterEqual(
                len(pattern_rows),
                3,
                f"expected compile/search/fullmatch coverage for {pattern!r}",
            )
            self.assertTrue(
                set(required_operations).issubset(
                    {workload.operation for workload in pattern_rows}
                )
            )
            for workload in pattern_rows:
                with self.subTest(pattern=pattern, workload_id=workload.workload_id):
                    for category in required_categories:
                        self.assertIn(category, workload.categories)

        manifest_search_haystacks = {
            str(workload.haystack)
            for workload in manifest_rows
            if workload.operation == "module.search"
        }
        for haystack in search_haystacks:
            self.assertIn(haystack, manifest_search_haystacks)
        for snippet in search_haystack_substrings:
            self.assertTrue(
                any(snippet in haystack for haystack in manifest_search_haystacks),
                f"expected a module.search workload covering {snippet!r}",
            )

        manifest_pattern_haystacks = {
            str(workload.haystack)
            for workload in manifest_rows
            if workload.operation == "pattern.fullmatch"
        }
        for haystack in pattern_haystacks:
            self.assertIn(haystack, manifest_pattern_haystacks)

        scorecard_rows = [
            workload
            for workload in scorecard["workloads"]
            if workload["manifest_id"] == manifest_id
            and workload["pattern"] in patterns
        ]
        self.assertEqual(
            {workload["id"] for workload in scorecard_rows},
            {workload.workload_id for workload in manifest_rows},
        )
        for workload in scorecard_rows:
            with self.subTest(scorecard_workload_id=workload["id"]):
                self.assertEqual(workload["status"], "measured")
                self.assertEqual(workload["implementation_timing"]["status"], "measured")
                self.assertGreater(workload["implementation_ns"], 0)


class SourceTreeScorecardBenchmarkSuiteTest(unittest.TestCase):
    maxDiff = None

    def test_combined_manifest_definition_defaults_to_fully_measured_representatives(
        self,
    ) -> None:
        fully_measured_expectation = _combined_fully_measured_manifest_expectation(
            coverage_group="contract",
            representative_measured_workload_ids=("measured-a", "measured-b"),
            expected_measured_workload_count=2,
        )

        definition = _combined_manifest_definition(
            fully_measured_expectation=fully_measured_expectation,
        )

        self.assertEqual(
            definition.representative_measured_workload_ids,
            ("measured-a", "measured-b"),
        )
        self.assertIs(
            definition.fully_measured_expectation,
            fully_measured_expectation,
        )

    def test_combined_manifest_definition_rejects_fully_measured_representative_drift(
        self,
    ) -> None:
        fully_measured_expectation = _combined_fully_measured_manifest_expectation(
            coverage_group="contract",
            representative_measured_workload_ids=("measured-a", "measured-b"),
            expected_measured_workload_count=2,
        )

        with self.assertRaisesRegex(
            AssertionError,
            re.escape(
                "fully measured manifest definitions must keep their "
                "representative rows on the shared definition-owned contract"
            ),
        ):
            _combined_manifest_definition(
                fully_measured_expectation=fully_measured_expectation,
                representative_measured_workload_ids=("drifted-measured-row",),
            )

    def _assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation(
        self,
        manifest_id: str,
    ) -> None:
        case = source_tree_scorecard_case(manifest_id)
        combined_case = source_tree_combined_case(manifest_id)

        self.assertEqual(
            case.manifest_expectations[manifest_id].known_gap_count,
            0,
        )
        self.assertEqual(
            case.representative_measured_workload_ids,
            combined_case.manifest_expectation.representative_measured_workload_ids,
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())

    def test_raw_scorecard_case_definitions_use_direct_manifest_ids(self) -> None:
        for case_id, case_definition in SOURCE_TREE_SCORECARD_EXPECTATIONS.items():
            with self.subTest(case_id=case_id):
                self.assertFalse(isinstance(case_definition, dict))
                self.assertFalse(hasattr(case_definition, "full_manifest_ids"))
                self.assertTrue(hasattr(case_definition, "manifest_ids"))
                self.assertGreaterEqual(len(case_definition.manifest_ids), 1)
                self.assertIn(case_definition.selection_mode, {"full", "smoke"})

    def test_full_scorecard_cases_derive_known_gap_counts_from_manifest_inventories(
        self,
    ) -> None:
        case = source_tree_scorecard_case("post-parser-workflows")
        self.assertEqual(
            case.manifest_expectations["literal-flag-boundary"].known_gap_count,
            0,
        )

    def test_published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks(
        self,
    ) -> None:
        manifests = list(published_benchmark_manifests())
        self.assertEqual(len(manifests), 30)
        tracked_report = benchmarks.SCORECARD_REPORT.load(TRACKED_REPORT_PATH)
        self.assertEqual(
            expected_summary_for_manifests(manifests, selection_mode="full"),
            {
                key: tracked_report["summary"][key]
                for key in (
                    "known_gap_count",
                    "measured_workloads",
                    "module_workloads",
                    "parser_workloads",
                    "regression_workloads",
                    "total_workloads",
                )
            },
        )

    def test_post_parser_workflows_promote_ignorecase_ascii_pair_to_measured_representatives(
        self,
    ) -> None:
        case = source_tree_scorecard_case("post-parser-workflows")
        for workload_id in (
            "module-search-ignorecase-ascii-cold-gap",
            "pattern-search-ignorecase-ascii-warm-gap",
        ):
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_regression_pack_full_promotes_regression_probes_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("regression-pack-full")
        for workload_id in (
            "regression-parser-bytes-backreference-purged",
            "regression-module-compile-multiline-purged",
            "regression-module-compile-multiline-purged-bytes",
            "regression-module-compile-verbose-purged-bytes",
        ):
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    case.representative_measured_workload_ids,
                )
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_numbered_backreference_manifest_promotes_grouped_segment_pair_to_measured(
        self,
    ) -> None:
        self._assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation(
            "numbered-backreference-boundary"
        )

    def test_nested_group_manifest_promotes_nested_pair_to_measured(self) -> None:
        self._assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation(
            "nested-group-boundary"
        )

    def test_case_builders_reuse_cached_source_tree_manifest_records(self) -> None:
        scorecard_case = source_tree_scorecard_case("post-parser-workflows")
        combined_case = source_tree_combined_case("literal-flag-boundary")

        self.assertEqual(
            [manifest.manifest_id for manifest in scorecard_case.manifests],
            [
                "module-boundary",
                "collection-replacement-boundary",
                "literal-flag-boundary",
            ],
        )
        self.assertEqual(
            [manifest.manifest_id for manifest in combined_case.manifests],
            [
                "compile-matrix",
                "module-boundary",
                "pattern-boundary",
                "collection-replacement-boundary",
                "literal-flag-boundary",
                "regression-matrix",
            ],
        )
        self.assertIs(
            scorecard_case.manifest_for_id("module-boundary"),
            combined_case.manifest_for_id("module-boundary"),
        )
        self.assertIs(
            scorecard_case.manifest_for_id("collection-replacement-boundary"),
            combined_case.manifest_for_id("collection-replacement-boundary"),
        )
        self.assertIs(
            scorecard_case.manifest_for_id("literal-flag-boundary"),
            combined_case.target_manifest,
        )
        self.assertEqual(
            combined_case.target_manifest.manifest_id,
            "literal-flag-boundary",
        )

    def test_post_parser_workflows_preserve_expected_manifest_paths(self) -> None:
        case = source_tree_scorecard_case("post-parser-workflows")

        self.assertEqual(
            [manifest.path.name for manifest in case.manifests],
            [
                "module_boundary.py",
                "collection_replacement_boundary.py",
                "literal_flag_boundary.py",
            ],
        )
        self.assertEqual(
            [relative_manifest_path(manifest.path) for manifest in case.manifests],
            [
                "benchmarks/workloads/module_boundary.py",
                "benchmarks/workloads/collection_replacement_boundary.py",
                "benchmarks/workloads/literal_flag_boundary.py",
            ],
        )

    def test_case_selection_helpers_derive_workload_ids_from_manifests(self) -> None:
        compile_matrix = source_tree_scorecard_case("compile-matrix")
        self.assertEqual(
            compile_matrix.selected_workload_ids_for_manifest("compile-matrix"),
            (
                "compile-inline-locale-bytes-warm",
                "compile-lookbehind-cold",
                "compile-character-class-ignorecase-warm",
                "compile-possessive-quantifier-cold",
                "compile-atomic-group-purged",
                "compile-parser-stress-cold",
            ),
        )

        post_parser = source_tree_scorecard_case("post-parser-workflows")
        self.assertEqual(
            post_parser.selected_workload_ids_for_manifest("module-boundary"),
            tuple(
                workload.workload_id
                for workload in post_parser.manifest_for_id("module-boundary").workloads
            ),
        )

        combined_case = source_tree_combined_case("literal-flag-boundary")
        self.assertEqual(
            combined_case.selected_workload_ids_for_manifest("regression-matrix"),
            tuple(
                workload.workload_id
                for workload in combined_case.manifest_for_id("regression-matrix").workloads
            ),
        )

    def _assert_zero_gap_representative_workload_subset(
        self,
        manifest_id: str,
        expected_workload_ids: tuple[str, ...],
    ) -> None:
        case = source_tree_combined_case(manifest_id)
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )

        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )

        explicit_representatives = (
            case.manifest_expectation.representative_measured_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(manifest_id=manifest_id, workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                if explicit_representatives:
                    self.assertIn(workload_id, explicit_representatives)

        if not explicit_representatives:
            self.assertEqual(explicit_representatives, ())

    def test_zero_gap_source_tree_manifests_keep_selected_bytes_representatives_publicly_measured(
        self,
    ) -> None:
        for manifest_id, manifest_definition in (
            SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
        ):
            for expected_workload_ids in (
                manifest_definition.zero_gap_bytes_representative_subsets
            ):
                with self.subTest(manifest_id=manifest_id):
                    self._assert_zero_gap_representative_workload_subset(
                        manifest_id,
                        expected_workload_ids,
                    )

    def test_combined_cases_treat_counted_repeat_manifest_pair_as_fully_measured(
        self,
    ) -> None:
        for manifest_id in source_tree_combined_fully_measured_manifest_ids(
            "counted-repeat"
        ):
            expected_workload_ids = (
                source_tree_combined_fully_measured_manifest_expectation(
                    manifest_id
                ).representative_measured_workload_ids
            )
            with self.subTest(manifest_id=manifest_id):
                case = source_tree_combined_case(manifest_id)
                self.assertEqual(case.manifest_expectation.known_gap_count, 0)
                self.assertEqual(
                    case.manifest_expectation.representative_measured_workload_ids,
                    expected_workload_ids,
                )
                self.assertEqual(
                    case.manifest_expectation.representative_known_gap_workload_ids,
                    (),
                )

    def test_compile_matrix_manifest_reuses_zero_gap_expectation(self) -> None:
        case = source_tree_scorecard_case("compile-matrix")
        manifest_expectation = case.manifest_expectations["compile-matrix"]
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.representative_measured_workload_ids,
            (
                "compile-inline-locale-bytes-warm",
                "compile-lookbehind-cold",
                "compile-atomic-group-purged",
                "compile-parser-stress-cold",
            ),
        )
        self.assertEqual(
            case.representative_known_gap_workload_ids,
            (),
        )
        self.assertIsNotNone(case.expected_first_deferred)
        assert case.expected_first_deferred is not None
        self.assertEqual(case.expected_first_deferred.area, "module-boundary")
        self.assertEqual(case.expected_first_deferred.follow_up, "RBR-0015")
        self.assertFalse(hasattr(case, "workload_note_substrings"))

    def test_single_manifest_scorecards_keep_slice_backed_representatives(self) -> None:
        for case_id in (
            "nested-group-replacement-boundary",
            "nested-group-callable-replacement-boundary",
            "branch-local-backreference-boundary",
            "conditional-group-exists-boundary",
        ):
            with self.subTest(case_id=case_id):
                case = source_tree_scorecard_case(case_id)
                self.assertEqual(
                    case.representative_measured_workload_ids,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        case_id
                    ),
                )
                self.assertEqual(
                    case.representative_measured_workload_ids,
                    tuple(
                        workload_id
                        for expectation in source_tree_combined_slice_expectations(
                            case_id
                        )
                        for workload_id in expectation.expected_workload_ids
                    ),
                )

    def test_conditional_group_exists_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectations = _conditional_group_exists_callable_replacement_expectations()
        case = source_tree_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        expected_negative_count_str_workload_ids = (
            "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-str",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
        )
        expected_negative_count_bytes_workload_ids = (
            "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-bytes",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
        )
        expected_callable_workload_ids = tuple(
            workload_id
            for expectation in expectations
            for workload_id in expectation.expected_workload_ids
        )
        callable_slice_rows = tuple(
            workload
            for expectation in expectations
            for workload in select_source_tree_combined_slice_rows(manifest, expectation)
        )
        representative_callable_workload_ids = tuple(
            workload_id
            for workload_id in case.representative_measured_workload_ids
            if workload_id in expected_callable_workload_ids
        )
        expected_str_workload_ids, expected_bytes_workload_ids = (
            _split_workload_ids_by_text_model(expected_callable_workload_ids)
        )
        representative_str_workload_ids, representative_bytes_workload_ids = (
            _split_workload_ids_by_text_model(representative_callable_workload_ids)
        )
        manifest_negative_count_str_workload_ids = tuple(
            workload.workload_id
            for workload in callable_slice_rows
            if workload.text_model == "str"
            and "negative-count" in workload.categories
            and "none-count" not in workload.categories
        )
        manifest_negative_count_bytes_workload_ids = tuple(
            workload.workload_id
            for workload in callable_slice_rows
            if workload.text_model == "bytes"
            and "negative-count" in workload.categories
            and "none-count" not in workload.categories
        )
        str_workload_signatures = Counter(
            (
                workload.operation,
                workload.pattern,
                workload.haystack,
                _text_model_agnostic_callable_match_group_signature(
                    workload.replacement_payload()
                ),
                workload.count,
                workload.cache_mode,
            )
            for workload in callable_slice_rows
            if workload.text_model == "str"
        )
        bytes_workload_signatures = Counter(
            (
                workload.operation,
                workload.pattern,
                workload.haystack,
                _text_model_agnostic_callable_match_group_signature(
                    workload.replacement_payload()
                ),
                workload.count,
                workload.cache_mode,
            )
            for workload in callable_slice_rows
            if workload.text_model == "bytes"
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual(
            representative_callable_workload_ids,
            expected_callable_workload_ids,
        )
        self.assertEqual(
            representative_str_workload_ids,
            expected_str_workload_ids,
        )
        self.assertEqual(
            representative_bytes_workload_ids,
            expected_bytes_workload_ids,
        )
        self.assertEqual(
            manifest_negative_count_str_workload_ids,
            expected_negative_count_str_workload_ids,
        )
        self.assertEqual(
            manifest_negative_count_bytes_workload_ids,
            expected_negative_count_bytes_workload_ids,
        )
        self.assertEqual(
            tuple(
                workload_id
                for workload_id in representative_str_workload_ids
                if workload_id in manifest_negative_count_str_workload_ids
            ),
            manifest_negative_count_str_workload_ids,
        )
        self.assertEqual(
            tuple(
                workload_id
                for workload_id in representative_bytes_workload_ids
                if workload_id in manifest_negative_count_bytes_workload_ids
            ),
            manifest_negative_count_bytes_workload_ids,
        )
        self.assertEqual(
            str_workload_signatures,
            bytes_workload_signatures,
        )
        self.assertEqual(
            Counter(
                (workload.operation, workload.count)
                for workload in callable_slice_rows
                if workload.workload_id in manifest_negative_count_str_workload_ids
            ),
            Counter(
                {
                    ("module.sub", -1): 2,
                    ("module.subn", -1): 2,
                    ("pattern.sub", -1): 2,
                    ("pattern.subn", -1): 2,
                }
            ),
        )
        self.assertEqual(
            Counter(
                (workload.operation, workload.count)
                for workload in callable_slice_rows
                if workload.workload_id in manifest_negative_count_bytes_workload_ids
            ),
            Counter(
                {
                    ("module.sub", -1): 2,
                    ("module.subn", -1): 2,
                    ("pattern.sub", -1): 2,
                    ("pattern.subn", -1): 2,
                }
            ),
        )

    def test_conditional_group_exists_callable_scorecards_keep_none_count_follow_on_workloads_in_sync(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectations = _conditional_group_exists_callable_replacement_expectations()
        case = source_tree_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        expected_none_count_workload_ids = (
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS
        )
        callable_slice_rows = tuple(
            workload
            for expectation in expectations
            for workload in select_source_tree_combined_slice_rows(manifest, expectation)
        )
        none_count_rows = tuple(
            workload
            for workload in callable_slice_rows
            if "none-count" in workload.categories
        )
        representative_none_count_workload_ids = tuple(
            workload_id
            for workload_id in case.representative_measured_workload_ids
            if workload_id in expected_none_count_workload_ids
        )
        representative_str_workload_ids, representative_bytes_workload_ids = (
            _split_workload_ids_by_text_model(representative_none_count_workload_ids)
        )
        manifest_none_count_str_workload_ids = tuple(
            workload.workload_id
            for workload in none_count_rows
            if workload.text_model == "str"
        )
        manifest_none_count_bytes_workload_ids = tuple(
            workload.workload_id
            for workload in none_count_rows
            if workload.text_model == "bytes"
        )

        def none_count_signature(workload: Workload) -> tuple[object, ...]:
            return (
                workload.operation,
                workload.pattern,
                workload.haystack,
                _text_model_agnostic_callable_match_group_signature(
                    workload.replacement_payload()
                ),
                workload.count,
                workload.cache_mode,
                frozenset(
                    category
                    for category in workload.categories
                    if category not in {"str", "bytes"}
                ),
            )

        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual(
            representative_str_workload_ids,
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            representative_bytes_workload_ids,
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(
            manifest_none_count_str_workload_ids,
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            manifest_none_count_bytes_workload_ids,
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(
            Counter(
                none_count_signature(workload)
                for workload in none_count_rows
                if workload.text_model == "str"
            ),
            Counter(
                none_count_signature(workload)
                for workload in none_count_rows
                if workload.text_model == "bytes"
            ),
        )
        self.assertEqual(
            Counter(
                (workload.operation, workload.count)
                for workload in none_count_rows
                if workload.text_model == "str"
            ),
            Counter(
                {
                    ("module.sub", None): 4,
                    ("module.subn", None): 4,
                    ("pattern.sub", None): 4,
                    ("pattern.subn", None): 4,
                }
            ),
        )
        self.assertEqual(
            Counter(
                (workload.operation, workload.count)
                for workload in none_count_rows
                if workload.text_model == "bytes"
            ),
            Counter(
                {
                    ("module.sub", None): 4,
                    ("module.subn", None): 4,
                    ("pattern.sub", None): 4,
                    ("pattern.subn", None): 4,
                }
            ),
        )

    def test_conditional_group_exists_nested_callable_scorecards_keep_bytes_rows_in_sync_with_str_slice(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        case = source_tree_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        str_expectation = _conditional_group_exists_nested_callable_replacement_expectation()
        bytes_expectation = _conditional_group_exists_nested_callable_bytes_replacement_expectation()
        str_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, str_expectation)
        )
        bytes_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, bytes_expectation)
        )
        representative_nested_workload_ids = tuple(
            workload_id
            for workload_id in case.representative_measured_workload_ids
            if workload_id
            in (
                CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
                + CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
            )
        )
        representative_str_workload_ids, representative_bytes_workload_ids = (
            _split_workload_ids_by_text_model(representative_nested_workload_ids)
        )

        def normalized_text_model_payload(value: str | bytes | None) -> str | None:
            if isinstance(value, bytes):
                return value.decode("latin-1")
            return value

        def expected_exception_signature(
            expected_exception: dict[str, str] | None,
        ) -> tuple[tuple[str, str], ...] | None:
            if expected_exception is None:
                return None
            return tuple(sorted(expected_exception.items()))

        def nested_workload_signature(workload: Workload) -> tuple[object, ...]:
            return (
                workload.operation,
                normalized_text_model_payload(workload.pattern_payload()),
                normalized_text_model_payload(workload.haystack_payload()),
                _text_model_agnostic_callable_match_group_signature(
                    workload.replacement_payload()
                ),
                workload.count,
                workload.cache_mode,
                frozenset(
                    category
                    for category in workload.categories
                    if category not in {"str", "bytes"}
                ),
                expected_exception_signature(workload.expected_exception),
            )

        self.assertEqual(
            tuple(workload.workload_id for workload in str_rows),
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            tuple(workload.workload_id for workload in bytes_rows),
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual(
            representative_str_workload_ids,
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            representative_bytes_workload_ids,
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(
            Counter(nested_workload_signature(workload) for workload in str_rows),
            Counter(nested_workload_signature(workload) for workload in bytes_rows),
        )

    def test_conditional_group_exists_quantified_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        case = source_tree_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        str_expectation = _conditional_group_exists_quantified_callable_replacement_expectation()
        bytes_expectation = (
            _conditional_group_exists_quantified_callable_bytes_replacement_expectation()
        )
        str_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, str_expectation)
        )
        bytes_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, bytes_expectation)
        )
        representative_quantified_workload_ids = tuple(
            workload_id
            for workload_id in case.representative_measured_workload_ids
            if workload_id
            in (
                CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
                + CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
            )
        )
        representative_str_workload_ids, representative_bytes_workload_ids = (
            _split_workload_ids_by_text_model(representative_quantified_workload_ids)
        )
        manifest_negative_count_str_workload_ids = _selected_workload_ids(
            str_rows,
            text_model="str",
            required_categories=("negative-count",),
        )
        manifest_negative_count_bytes_workload_ids = _selected_workload_ids(
            bytes_rows,
            text_model="bytes",
            required_categories=("negative-count",),
        )
        manifest_negative_count_no_match_str_workload_ids = _selected_workload_ids(
            str_rows,
            text_model="str",
            required_categories=("negative-count", "no-match"),
        )
        manifest_negative_count_no_match_bytes_workload_ids = _selected_workload_ids(
            bytes_rows,
            text_model="bytes",
            required_categories=("negative-count", "no-match"),
        )
        manifest_none_count_str_workload_ids = _selected_workload_ids(
            str_rows,
            text_model="str",
            required_categories=("none-count",),
        )
        manifest_none_count_bytes_workload_ids = _selected_workload_ids(
            bytes_rows,
            text_model="bytes",
            required_categories=("none-count",),
        )
        manifest_plain_no_match_str_workload_ids = _selected_workload_ids(
            str_rows,
            text_model="str",
            required_categories=("no-match",),
            excluded_categories=("negative-count",),
        )
        manifest_plain_no_match_bytes_workload_ids = _selected_workload_ids(
            bytes_rows,
            text_model="bytes",
            required_categories=("no-match",),
            excluded_categories=("negative-count",),
        )
        representative_negative_count_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_str_workload_ids
            if workload_id in manifest_negative_count_str_workload_ids
        )
        representative_negative_count_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_bytes_workload_ids
            if workload_id in manifest_negative_count_bytes_workload_ids
        )
        representative_negative_count_no_match_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_str_workload_ids
            if workload_id in manifest_negative_count_no_match_str_workload_ids
        )
        representative_negative_count_no_match_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_bytes_workload_ids
            if workload_id in manifest_negative_count_no_match_bytes_workload_ids
        )
        representative_none_count_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_str_workload_ids
            if workload_id in manifest_none_count_str_workload_ids
        )
        representative_none_count_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_bytes_workload_ids
            if workload_id in manifest_none_count_bytes_workload_ids
        )
        representative_plain_no_match_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_str_workload_ids
            if workload_id in manifest_plain_no_match_str_workload_ids
        )
        representative_plain_no_match_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_bytes_workload_ids
            if workload_id in manifest_plain_no_match_bytes_workload_ids
        )

        def normalized_text_model_payload(value: str | bytes | None) -> str | None:
            if isinstance(value, bytes):
                return value.decode("latin-1")
            return value

        def expected_exception_signature(
            expected_exception: dict[str, str] | None,
        ) -> tuple[tuple[str, str], ...] | None:
            if expected_exception is None:
                return None
            return tuple(sorted(expected_exception.items()))

        def quantified_workload_signature(workload: Workload) -> tuple[object, ...]:
            return (
                workload.operation,
                normalized_text_model_payload(workload.pattern_payload()),
                normalized_text_model_payload(workload.haystack_payload()),
                _text_model_agnostic_callable_match_group_signature(
                    workload.replacement_payload()
                ),
                workload.count,
                workload.cache_mode,
                frozenset(
                    category
                    for category in workload.categories
                    if category not in {"str", "bytes"}
                ),
                expected_exception_signature(workload.expected_exception),
            )

        self.assertEqual(
            tuple(workload.workload_id for workload in str_rows),
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            tuple(workload.workload_id for workload in bytes_rows),
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual(
            representative_str_workload_ids,
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            representative_bytes_workload_ids,
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(
            Counter(
                quantified_workload_signature(workload) for workload in str_rows
            ),
            Counter(
                quantified_workload_signature(workload) for workload in bytes_rows
            ),
        )
        self.assertEqual(
            len(manifest_negative_count_str_workload_ids),
            len(manifest_negative_count_bytes_workload_ids),
        )
        self.assertEqual(len(manifest_negative_count_str_workload_ids), 16)
        self.assertEqual(
            len(manifest_none_count_str_workload_ids),
            len(manifest_none_count_bytes_workload_ids),
        )
        self.assertEqual(len(manifest_none_count_str_workload_ids), 4)
        self.assertEqual(
            len(manifest_negative_count_no_match_str_workload_ids),
            len(manifest_negative_count_no_match_bytes_workload_ids),
        )
        self.assertEqual(len(manifest_negative_count_no_match_str_workload_ids), 8)
        self.assertEqual(
            len(manifest_plain_no_match_str_workload_ids),
            len(manifest_plain_no_match_bytes_workload_ids),
        )
        self.assertEqual(len(manifest_plain_no_match_str_workload_ids), 8)
        self.assertEqual(
            manifest_negative_count_bytes_workload_ids,
            _mirrored_bytes_workload_ids(manifest_negative_count_str_workload_ids),
        )
        self.assertEqual(
            manifest_negative_count_no_match_bytes_workload_ids,
            _mirrored_bytes_workload_ids(
                manifest_negative_count_no_match_str_workload_ids
            ),
        )
        self.assertEqual(
            manifest_none_count_bytes_workload_ids,
            _mirrored_bytes_workload_ids(manifest_none_count_str_workload_ids),
        )
        self.assertEqual(
            manifest_plain_no_match_bytes_workload_ids,
            _mirrored_bytes_workload_ids(manifest_plain_no_match_str_workload_ids),
        )
        self.assertEqual(
            representative_negative_count_str_workload_ids,
            manifest_negative_count_str_workload_ids,
        )
        self.assertEqual(
            representative_negative_count_bytes_workload_ids,
            _mirrored_bytes_workload_ids(representative_negative_count_str_workload_ids),
        )
        self.assertEqual(
            representative_negative_count_no_match_str_workload_ids,
            manifest_negative_count_no_match_str_workload_ids,
        )
        self.assertEqual(
            representative_negative_count_no_match_bytes_workload_ids,
            _mirrored_bytes_workload_ids(
                representative_negative_count_no_match_str_workload_ids
            ),
        )
        self.assertEqual(
            representative_none_count_str_workload_ids,
            manifest_none_count_str_workload_ids,
        )
        self.assertEqual(
            representative_none_count_bytes_workload_ids,
            _mirrored_bytes_workload_ids(representative_none_count_str_workload_ids),
        )
        self.assertEqual(
            representative_plain_no_match_str_workload_ids,
            manifest_plain_no_match_str_workload_ids,
        )
        self.assertEqual(
            representative_plain_no_match_bytes_workload_ids,
            _mirrored_bytes_workload_ids(representative_plain_no_match_str_workload_ids),
        )
        self.assertEqual(
            representative_negative_count_str_workload_ids[
                -len(representative_negative_count_no_match_str_workload_ids) :
            ],
            representative_negative_count_no_match_str_workload_ids,
        )
        self.assertEqual(
            representative_negative_count_bytes_workload_ids[
                -len(representative_negative_count_no_match_bytes_workload_ids) :
            ],
            representative_negative_count_no_match_bytes_workload_ids,
        )
        self.assertEqual(
            representative_str_workload_ids[
                -len(representative_plain_no_match_str_workload_ids) :
            ],
            representative_plain_no_match_str_workload_ids,
        )
        self.assertEqual(
            representative_bytes_workload_ids[
                -len(representative_plain_no_match_bytes_workload_ids) :
            ],
            representative_plain_no_match_bytes_workload_ids,
        )
        self.assertEqual(
            Counter(
                (workload.operation, workload.count)
                for workload in str_rows
                if workload.workload_id in manifest_negative_count_str_workload_ids
            ),
            Counter(
                {
                    ("module.sub", -1): 4,
                    ("module.subn", -1): 4,
                    ("pattern.sub", -1): 4,
                    ("pattern.subn", -1): 4,
                }
            ),
        )
        self.assertEqual(
            Counter(
                (workload.operation, workload.count)
                for workload in bytes_rows
                if workload.workload_id in manifest_negative_count_bytes_workload_ids
            ),
            Counter(
                {
                    ("module.sub", -1): 4,
                    ("module.subn", -1): 4,
                    ("pattern.sub", -1): 4,
                    ("pattern.subn", -1): 4,
                }
            ),
        )

    def test_conditional_group_exists_callable_scorecards_include_alternation_heavy_rows(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectation = (
            _conditional_group_exists_alternation_callable_replacement_expectation()
        )
        case = source_tree_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        matched_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, expectation)
        )

        self.assertEqual(
            tuple(workload.workload_id for workload in matched_rows),
            CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS,
        )
        self.assertEqual(
            Counter(workload.text_model for workload in matched_rows),
            Counter({"str": 16, "bytes": 16}),
        )
        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )
        self.assertEqual(
            Counter((workload.operation, workload.count) for workload in matched_rows),
            Counter(
                {
                    ("module.sub", 0): 4,
                    ("module.sub", None): 2,
                    ("module.sub", -1): 2,
                    ("module.subn", 1): 4,
                    ("module.subn", None): 2,
                    ("module.subn", -1): 2,
                    ("pattern.sub", 0): 4,
                    ("pattern.sub", None): 2,
                    ("pattern.sub", -1): 2,
                    ("pattern.subn", 1): 4,
                    ("pattern.subn", None): 2,
                    ("pattern.subn", -1): 2,
                }
            ),
        )
        self.assertEqual(
            Counter(
                "exception" in workload.categories for workload in matched_rows
            ),
            Counter({False: 16, True: 16}),
        )

    def test_conditional_group_exists_template_bytes_scorecard_promotes_minimal_replacement_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        template_expectation = (
            _conditional_group_exists_template_replacement_expectation()
        )
        case = source_tree_scorecard_case(manifest_id)
        matched_rows = tuple(
            select_source_tree_combined_slice_rows(
                case.manifest_for_id(manifest_id),
                template_expectation,
            )
        )
        expected_workload_ids = template_expectation.expected_workload_ids

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual({workload.text_model for workload in matched_rows}, {"str", "bytes"})
        for workload_id in CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )
        self.assertEqual(
            tuple(
                workload.workload_id
                for workload in matched_rows
                if workload.workload_id in case.representative_measured_workload_ids
            ),
            expected_workload_ids,
        )

    def test_conditional_group_exists_replacement_template_scorecards_keep_bytes_negative_count_follow_on_workloads_in_sync(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        template_expectation = (
            _conditional_group_exists_template_replacement_expectation()
        )
        case = source_tree_scorecard_case(manifest_id)
        expected_negative_count_str_workload_ids = (
            "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-str",
            "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-str",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-str",
        )
        expected_negative_count_bytes_workload_ids = (
            "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
            "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-bytes",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
            "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-bytes",
        )
        representative_template_workload_ids = tuple(
            workload_id
            for workload_id in case.representative_measured_workload_ids
            if workload_id in template_expectation.expected_workload_ids
        )
        expected_str_workload_ids, expected_bytes_workload_ids = (
            _split_workload_ids_by_text_model(template_expectation.expected_workload_ids)
        )
        representative_str_workload_ids, representative_bytes_workload_ids = (
            _split_workload_ids_by_text_model(representative_template_workload_ids)
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual(
            representative_template_workload_ids,
            template_expectation.expected_workload_ids,
        )
        self.assertEqual(
            representative_str_workload_ids,
            expected_str_workload_ids,
        )
        self.assertEqual(
            representative_bytes_workload_ids,
            expected_bytes_workload_ids,
        )
        self.assertEqual(
            expected_bytes_workload_ids,
            CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(
            representative_str_workload_ids[-len(expected_negative_count_str_workload_ids) :],
            expected_negative_count_str_workload_ids,
        )
        self.assertEqual(
            tuple(
                workload_id
                for workload_id in representative_str_workload_ids
                if "negative-count" in workload_id
            ),
            expected_negative_count_str_workload_ids,
        )
        self.assertEqual(
            representative_bytes_workload_ids[-len(expected_negative_count_bytes_workload_ids) :],
            expected_negative_count_bytes_workload_ids,
        )
        self.assertEqual(
            tuple(
                workload_id
                for workload_id in representative_bytes_workload_ids
                if "negative-count" in workload_id
            ),
            expected_negative_count_bytes_workload_ids,
        )

    def test_nested_group_callable_replacement_scorecard_promotes_broader_range_open_ended_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_bounded_nested_group_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-nested-group-numbered-warm-bytes",
            "module-subn-callable-nested-group-numbered-warm-bytes",
            "pattern-sub-callable-nested-group-numbered-purged-bytes",
            "pattern-subn-callable-nested-group-numbered-purged-bytes",
            "module-sub-callable-nested-group-named-warm-bytes",
            "module-subn-callable-nested-group-named-warm-bytes",
            "pattern-sub-callable-nested-group-named-purged-bytes",
            "pattern-subn-callable-nested-group-named-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_quantified_nested_group_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-quantified-nested-group-lower-bound-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-repeated-outer-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_quantified_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_replacement_scorecard_promotes_broader_range_branch_local_backreference_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-replacement-boundary")
        expected_workload_ids = (
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_replacement_scorecard_promotes_broader_range_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-replacement-boundary")
        expected_workload_ids = (
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_broader_range_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_exact_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-warm-bytes",
            "module-subn-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-nested-group-alternation-branch-local-backreference-c-branch-purged-bytes",
            "pattern-subn-callable-named-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_nested_broader_range_backtracking_heavy_str_and_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_nested_broader_range_open_ended_backtracking_heavy_str_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_nested_broader_range_open_ended_backtracking_heavy_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_broader_range_conditional_branch_local_backreference_str_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-str",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-str",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_broader_range_conditional_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_replacement_scorecard_promotes_broader_range_open_ended_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-replacement-boundary")
        expected_workload_ids = (
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_runner_regenerates_source_tree_scorecards(self) -> None:
        for case_id in source_tree_scorecard_case_ids():
            with self.subTest(case_id=case_id):
                case = source_tree_scorecard_case(case_id)
                command = [
                    argument
                    for manifest in case.manifests
                    for argument in ("--manifest", str(manifest.path))
                ]
                if case.selection_mode == "smoke":
                    command.append("--smoke")

                summary, scorecard = run_harness_scorecard(
                    "rebar_harness.benchmarks",
                    command,
                    report_name="benchmarks.json",
                )

                assert_source_tree_benchmark_contract(
                    self,
                    scorecard,
                    summary,
                    expected_phase=case.expected_phase,
                    expected_runner_version=case.expected_runner_version,
                    expected_adapter=case.expected_adapter,
                    expected_manifests=case.manifests,
                    expected_manifest_paths=[
                        relative_manifest_path(manifest.path)
                        for manifest in case.manifests
                    ],
                    expected_selection_mode=case.selection_mode,
                    tracked_report_path=TRACKED_REPORT_PATH,
                )
                self.assertEqual(summary, case.expected_summary)

                expected_first_deferred = case.expected_first_deferred
                if expected_first_deferred is not None:
                    self.assertGreaterEqual(len(scorecard["deferred"]), 1)
                    self.assertEqual(
                        scorecard["deferred"][0]["area"],
                        expected_first_deferred.area,
                    )
                    self.assertEqual(
                        scorecard["deferred"][0]["follow_up"],
                        expected_first_deferred.follow_up,
                    )

                expected_workload_order = case.expected_workload_order
                if expected_workload_order is not None:
                    self.assertEqual(
                        [workload["id"] for workload in scorecard["workloads"]],
                        list(expected_workload_order),
                    )

                self._assert_manifest_contracts(case, scorecard)
                self._assert_representative_workloads(case, scorecard)

    def _assert_manifest_contracts(
        self,
        case: SourceTreeScorecardCase,
        scorecard: dict[str, object],
    ) -> None:
        manifest_expectations = case.manifest_expectations
        for manifest_id, manifest_expectation in manifest_expectations.items():
            manifest_summary = scorecard["manifests"][manifest_id]
            manifest_record = find_manifest_record(scorecard, manifest_id)
            manifest = case.manifest_for_id(manifest_id)
            assert_benchmark_manifest_contract(
                self,
                manifest_summary,
                manifest_record,
                manifest=manifest,
                manifest_path=relative_manifest_path(manifest.path),
                known_gap_count=manifest_expectation.known_gap_count,
                selection_mode=case.selection_mode,
                selected_workload_ids=case.selected_workload_ids_for_manifest(
                    manifest_id
                ),
            )

    def _assert_representative_workloads(
        self,
        case: SourceTreeScorecardCase,
        scorecard: dict[str, object],
    ) -> None:
        self._assert_workloads(
            case,
            scorecard,
            case.representative_measured_workload_ids,
            expected_status="measured",
        )
        self._assert_workloads(
            case,
            scorecard,
            case.representative_known_gap_workload_ids,
            expected_status="unimplemented",
        )

    def _assert_workloads(
        self,
        case: SourceTreeScorecardCase,
        scorecard: dict[str, object],
        workload_ids: tuple[str, ...],
        *,
        expected_status: str,
    ) -> None:
        for workload_id in workload_ids:
            with self.subTest(workload_id=workload_id):
                workload_record = find_workload_record(scorecard, workload_id)
                manifest_id = workload_record["manifest_id"]
                manifest = case.manifest_for_id(manifest_id)
                assert_benchmark_workload_contract(
                    self,
                    workload_record,
                    manifest_id=manifest_id,
                    workload_document=find_workload_document(manifest, workload_id),
                    expected_status=expected_status,
                )


# Detached benchmark-anchor contract coverage from the former
# `test_standard_benchmark_correctness_anchor_contracts.py` lives below so this
# file is the single benchmark-owner suite.

MODULE_BOUNDARY_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "module_boundary.py"
)
PATTERN_BOUNDARY_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "pattern_boundary.py"
)
COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "collection_replacement_boundary.py"
)
OPTIONAL_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.py"
)
NESTED_GROUP_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py"
EXACT_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "exact_repeat_quantified_group_boundary.py"
)
RANGED_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "ranged_repeat_quantified_group_boundary.py"
)
GROUPED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py"
)
GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_replacement_boundary.py"
)
NESTED_GROUP_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_replacement_boundary.py"
)
OPEN_ENDED_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "open_ended_quantified_group_boundary.py"
)
