from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import cache
import json
import pathlib
import re
import shutil
import sys
import textwrap
from types import SimpleNamespace
from typing import Any
import unittest
from unittest import mock

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    BenchmarkManifest,
    PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
    Workload,
    build_callable,
    determine_phase,
    determine_runner_version,
    load_manifest,
    load_manifests,
    published_benchmark_manifests,
    run_internal_workload_probe,
    select_benchmark_manifest_paths,
    select_workloads,
    workload_from_payload,
    workload_to_payload,
)
from rebar_harness.correctness import published_fixture_manifests
from rebar_harness.scorecard_io import (
    build_cpython_baseline,
    ordered_published_subset_filenames,
)
from tests.conftest import (
    REPO_ROOT,
    declared_string_constants_by_suffix,
    duplicate_items,
    run_harness_scorecard,
)
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    assert_match_result_parity,
    assert_pattern_parity,
    case_pattern,
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


def assert_benchmark_workload_contract(
    testcase: Any,
    workload_record: dict[str, Any],
    *,
    manifest_id: str,
    workload_document: Workload,
    expected_status: str,
) -> None:
    workload_payload = workload_to_payload(workload_document)
    expected_syntax_features = workload_payload.get(
        "syntax_features",
        workload_payload.get("categories", []),
    )
    testcase.assertEqual(workload_record["manifest_id"], manifest_id)
    testcase.assertEqual(
        workload_record["family"],
        workload_payload.get("family", "parser"),
    )
    testcase.assertEqual(workload_record["operation"], workload_payload["operation"])
    testcase.assertEqual(workload_record["pattern"], workload_payload.get("pattern", ""))
    testcase.assertEqual(workload_record["haystack"], workload_payload.get("haystack"))
    testcase.assertEqual(
        workload_record["replacement"],
        workload_payload.get("replacement"),
    )
    testcase.assertEqual(workload_record["flags"], workload_payload.get("flags", 0))
    testcase.assertEqual(workload_record["count"], workload_payload.get("count", 0))
    testcase.assertEqual(
        workload_record["maxsplit"],
        workload_payload.get("maxsplit", 0),
    )
    testcase.assertEqual(
        workload_record.get("pos"),
        workload_payload.get("pos"),
    )
    testcase.assertEqual(
        workload_record.get("endpos"),
        workload_payload.get("endpos"),
    )
    testcase.assertEqual(
        workload_record.get("kwargs"),
        workload_payload.get("kwargs"),
    )
    testcase.assertEqual(
        workload_record["text_model"],
        workload_payload.get("text_model", "str"),
    )
    testcase.assertEqual(
        workload_record.get("haystack_text_model"),
        workload_payload.get("haystack_text_model"),
    )
    testcase.assertEqual(workload_record["cache_mode"], workload_payload["cache_mode"])
    testcase.assertEqual(
        workload_record["timing_scope"],
        workload_payload.get("timing_scope", "compile-path-proxy"),
    )
    testcase.assertEqual(workload_record["syntax_features"], expected_syntax_features)
    testcase.assertEqual(workload_record["status"], expected_status)
    testcase.assertEqual(
        workload_record["baseline_timing"]["status"],
        "measured",
    )
    testcase.assertGreater(workload_record["baseline_ns"], 0)
    testcase.assertGreater(workload_record["baseline_ops_per_second"], 0)
    testcase.assertEqual(
        workload_record["implementation_timing"]["status"],
        expected_status,
    )
    if expected_status == "measured":
        testcase.assertGreater(workload_record["implementation_ns"], 0)
        testcase.assertGreater(workload_record["implementation_ops_per_second"], 0)
        testcase.assertIsInstance(workload_record["speedup_vs_cpython"], float)
    else:
        testcase.assertIsNone(workload_record["implementation_ns"])
        testcase.assertIsNone(workload_record["implementation_ops_per_second"])
        testcase.assertIsNone(workload_record["speedup_vs_cpython"])


def find_manifest_record(scorecard: dict[str, Any], manifest_id: str) -> dict[str, Any]:
    for manifest_record in scorecard["artifacts"]["manifests"]:
        if str(manifest_record["manifest_id"]) == manifest_id:
            return manifest_record
    raise AssertionError(f"missing manifest record for {manifest_id!r}")


def find_workload_record(scorecard: dict[str, Any], workload_id: str) -> dict[str, Any]:
    for workload in scorecard["workloads"]:
        if str(workload["id"]) == workload_id:
            return workload
    raise AssertionError(f"missing workload record for {workload_id!r}")


def find_workload_document(
    manifest: BenchmarkManifest,
    workload_id: str,
) -> Workload:
    for workload in manifest.workloads:
        if workload.workload_id == workload_id:
            return workload
    raise AssertionError(
        f"missing workload definition {workload_id!r} in {manifest.manifest_id!r}"
    )

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
            "pattern-subn-grouped-template-warm-str",
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
        expected_workload_ids=tuple(
            str(workload_id) for workload_id in expected_workload_ids
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
        required_syntax_features=("callable-replacement", "quantifiers"),
        excluded_syntax_features=("alternation", "branch-local-backreferences"),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-lower-bound-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-repeated-outer-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-purged-gap",
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
            "module-sub-template-named-conditional-group-exists-replacement-warm-str",
            "module-subn-template-named-conditional-group-exists-replacement-warm-str",
            "pattern-sub-template-named-conditional-group-exists-replacement-purged-str",
            "pattern-subn-template-named-conditional-group-exists-replacement-purged-str",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzacezz"},
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
            "exception",
            "nested-group",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-conditional-group-exists-replacement-warm-str",
            "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-str",
            "module-sub-callable-named-conditional-group-exists-replacement-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-str",
            "pattern-sub-callable-named-conditional-group-exists-replacement-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-purged-gap",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcdacezz"},
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
        excluded_categories=("alternation", "nested-group", "quantified", "unsupported"),
        expected_workload_ids=(
            "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-str",
            "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-str",
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


@cache
def _source_tree_manifest_records() -> dict[str, BenchmarkManifest]:
    return {
        manifest.manifest_id: manifest for manifest in published_benchmark_manifests()
    }


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
    manifest_records = _source_tree_manifest_records()
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


def _manifest_workload_ids_matching(
    manifest: BenchmarkManifest,
    include_workload: Callable[[Workload], bool],
    *,
    operation_prefix: str | None = None,
) -> tuple[str, ...]:
    return tuple(
        workload.workload_id
        for workload in manifest.workloads
        if include_workload(workload)
        and (
            operation_prefix is None
            or workload.operation.startswith(operation_prefix)
        )
    )


WIDER_RANGED_REPEAT_MANIFEST_ID = "wider-ranged-repeat-quantified-group-boundary"


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

    def test_collection_replacement_manifest_keeps_positional_indexlike_module_and_pattern_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("collection-replacement-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_collection_replacement_positional_indexlike_workload,
        )
        self.assertEqual(len(expected_measured_workload_ids), 6)
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "collection-replacement-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("collection-replacement-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_collection_replacement_keyword_workload,
            operation_prefix="pattern.",
        )
        self.assertEqual(len(expected_measured_workload_ids), 19)
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "collection-replacement-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("collection-replacement-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_collection_replacement_keyword_workload,
            operation_prefix="module.",
        )
        self.assertEqual(len(expected_measured_workload_ids), 33)
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "collection-replacement-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_collection_replacement_manifest_keeps_compiled_pattern_module_helper_keyword_error_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("collection-replacement-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_collection_replacement_compiled_pattern_keyword_error_workload,
        )
        self.assertEqual(len(expected_measured_workload_ids), 8)
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "collection-replacement-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_collection_replacement_manifest_keeps_compiled_pattern_success_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("collection-replacement-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_collection_replacement_compiled_pattern_success_workload,
        )
        self.assertEqual(len(expected_measured_workload_ids), 5)
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "collection-replacement-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("collection-replacement-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_collection_replacement_wrong_text_model_workload,
        )
        self.assertEqual(len(expected_measured_workload_ids), 5)
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "collection-replacement-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_collection_replacement_manifest_keeps_pattern_wrong_text_model_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("collection-replacement-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_collection_replacement_pattern_wrong_text_model_workload,
        )
        self.assertEqual(len(expected_measured_workload_ids), 3)
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "collection-replacement-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("module-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_module_workflow_compiled_pattern_wrong_text_model_workload,
        )
        self.assertEqual(len(expected_measured_workload_ids), 3)
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "module-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_module_boundary_manifest_keeps_literal_compiled_pattern_success_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("module-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_module_workflow_compiled_pattern_literal_success_workload,
        )
        self.assertEqual(
            expected_measured_workload_ids,
            (
                "module-search-literal-warm-hit-str-compiled-pattern",
                "module-match-literal-warm-hit-str-compiled-pattern",
                "module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
            ),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "module-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_module_boundary_manifest_keeps_compiled_pattern_module_compile_literal_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("module-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_module_workflow_compiled_pattern_compile_literal_success_workload,
        )
        self.assertEqual(
            expected_measured_workload_ids,
            (
                "module-compile-literal-warm-str-compiled-pattern",
                "module-compile-literal-purged-bytes-compiled-pattern",
            ),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "module-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_module_boundary_manifest_keeps_compiled_pattern_module_compile_named_group_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("module-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_module_workflow_compiled_pattern_compile_named_group_success_workload,
        )
        self.assertEqual(
            expected_measured_workload_ids,
            (
                "module-compile-named-group-warm-str-compiled-pattern",
                "module-compile-named-group-purged-bytes-compiled-pattern",
            ),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "module-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_module_boundary_manifest_keeps_compiled_pattern_module_compile_keyword_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("module-boundary")
        workload_count = len(case.target_manifest.workloads)
        cases = (
            (
                "int-zero",
                _is_module_workflow_compiled_pattern_compile_int_zero_keyword_workload,
                (
                    "module-compile-flags-int-zero-warm-str-compiled-pattern",
                    "module-compile-flags-int-zero-purged-bytes-compiled-pattern",
                ),
            ),
            (
                "int-zero-named-group",
                (
                    _is_module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_workload
                ),
                (
                    "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group",
                    "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group",
                ),
            ),
            (
                "bool-false",
                _is_module_workflow_compiled_pattern_compile_bool_false_keyword_workload,
                (
                    "module-compile-flags-bool-false-warm-str-compiled-pattern",
                    "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
                ),
            ),
            (
                "bool-false-named-group",
                (
                    _is_module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_workload
                ),
                (
                    "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group",
                    "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group",
                ),
            ),
            (
                "ignorecase-rejection-named-group",
                (
                    _is_module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_workload
                ),
                (
                    "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group",
                    "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group",
                ),
            ),
            (
                "ignorecase-rejection",
                (
                    _is_module_workflow_compiled_pattern_compile_ignorecase_keyword_workload
                ),
                (
                    "module-compile-flags-ignorecase-warm-str-compiled-pattern",
                    "module-compile-flags-ignorecase-purged-bytes-compiled-pattern",
                ),
            ),
        )

        for group_id, include_workload, expected_workload_ids in cases:
            with self.subTest(group_id=group_id):
                measured_workload_ids = _manifest_workload_ids_matching(
                    case.target_manifest,
                    include_workload,
                )
                self.assertEqual(measured_workload_ids, expected_workload_ids)
                self._assert_zero_gap_manifest_workloads_measured(
                    case,
                    "module-boundary",
                    measured_workload_ids,
                    workload_count,
                    expected_total_workload_count=workload_count,
                )

    def test_module_boundary_manifest_keeps_bounded_wildcard_compiled_pattern_success_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("module-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
        )
        self.assertEqual(
            expected_measured_workload_ids,
            (
                "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern",
                "module-match-bounded-wildcard-warm-hit-str-compiled-pattern",
                "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern",
            ),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "module-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_module_boundary_manifest_keeps_verbose_bytes_compiled_pattern_success_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("module-boundary")
        workload_count = len(case.target_manifest.workloads)
        expected_measured_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
        )
        self.assertEqual(
            expected_measured_workload_ids,
            (
                "module-search-verbose-regression-warm-hit-bytes-compiled-pattern",
                "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern",
            ),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "module-boundary",
            expected_measured_workload_ids,
            workload_count,
            expected_total_workload_count=workload_count,
        )

    def test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured(
        self,
    ) -> None:
        case = source_tree_combined_case("pattern-boundary")
        self.assertEqual(len(case.target_manifest.workloads), 18)
        keyword_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_pattern_keyword_window_workload,
        )
        positional_workload_ids = _manifest_workload_ids_matching(
            case.target_manifest,
            _is_pattern_window_positional_indexlike_workload,
        )
        self.assertEqual(
            keyword_workload_ids,
            (
                "pattern-search-pos-keyword-warm-str",
                "pattern-match-pos-keyword-purged-str",
                "pattern-match-window-indexlike-purged-bytes",
                "pattern-fullmatch-window-keyword-purged-bytes",
                "pattern-findall-bool-window-keyword-warm-str",
                "pattern-finditer-window-indexlike-purged-bytes",
            ),
        )
        self.assertEqual(
            positional_workload_ids,
            (
                "pattern-search-pos-indexlike-positional-warm-str",
                "pattern-search-endpos-indexlike-positional-purged-bytes",
                "pattern-match-window-indexlike-positional-purged-bytes",
                "pattern-fullmatch-window-indexlike-positional-purged-bytes",
                "pattern-findall-window-indexlike-positional-warm-str",
                "pattern-finditer-window-indexlike-positional-purged-bytes",
            ),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "pattern-boundary",
            keyword_workload_ids + positional_workload_ids,
            18,
            expected_total_workload_count=18,
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
        self.assertEqual(
            set(zero_gap_bytes_subsets_by_manifest),
            {
                "wider-ranged-repeat-quantified-group-boundary",
                "open-ended-quantified-group-boundary",
                "branch-local-backreference-boundary",
            },
        )
        self.assertEqual(
            len(
                zero_gap_bytes_subsets_by_manifest[
                    "wider-ranged-repeat-quantified-group-boundary"
                ]
            ),
            6,
        )
        self.assertEqual(
            len(
                zero_gap_bytes_subsets_by_manifest[
                    "open-ended-quantified-group-boundary"
                ]
            ),
            5,
        )
        self.assertEqual(
            len(
                zero_gap_bytes_subsets_by_manifest[
                    "branch-local-backreference-boundary"
                ]
            ),
            1,
        )
        self.assertEqual(
            sum(
                len(representative_subsets)
                for representative_subsets in zero_gap_bytes_subsets_by_manifest.values()
            ),
            12,
        )
        for manifest_id, representative_subsets in zero_gap_bytes_subsets_by_manifest.items():
            for expected_workload_ids in representative_subsets:
                with self.subTest(manifest_id=manifest_id):
                    self._assert_zero_gap_bytes_representative_subset(
                        manifest_id,
                        expected_workload_ids,
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
        self.assertEqual(
            expected_summary_for_manifests(manifests, selection_mode="full"),
            {
                "known_gap_count": 0,
                "measured_workloads": 889,
                "module_workloads": 881,
                "parser_workloads": 8,
                "regression_workloads": 8,
                "total_workloads": 889,
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

        for workload_id in expected_workload_ids:
            with self.subTest(manifest_id=manifest_id, workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                self.assertIn(
                    workload_id,
                    case.manifest_expectation.representative_measured_workload_ids,
                )

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

COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
REGRESSION_MATRIX_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"
)
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

support = sys.modules[__name__]
MATURIN = shutil.which("maturin")
_MISSING_MATURIN_REASON = (
    "built-native mode unavailable because no `maturin` executable was found on PATH"
)
_MISSING_MATURIN_PATTERN = "no `maturin` executable was found on PATH"


@pytest.fixture
def anchor_support_cache_guard() -> None:
    _clear_anchor_support_caches()
    yield
    _clear_anchor_support_caches()


def _clear_anchor_support_caches() -> None:
    for cached_function in (
        support._manifest_workloads,
        support.published_case_ids_by_signature,
        support.published_cases_by_id,
    ):
        cache_clear = getattr(cached_function, "cache_clear", None)
        if cache_clear is not None:
            cache_clear()


def _synthetic_manifest(
    *,
    cases: tuple[object, ...] = (),
    workloads: tuple[object, ...] = (),
) -> SimpleNamespace:
    return SimpleNamespace(cases=list(cases), workloads=list(workloads))


def _synthetic_case(
    case_id: str,
    signature: tuple[object, ...] | None,
) -> SimpleNamespace:
    return SimpleNamespace(case_id=case_id, signature=signature)


def _synthetic_workload(
    workload_id: str,
    signature: tuple[object, ...],
    *,
    include: bool = True,
) -> SimpleNamespace:
    return SimpleNamespace(workload_id=workload_id, signature=signature, include=include)


def _tracked_benchmark_manifest_paths() -> tuple[pathlib.Path, ...]:
    return tuple(sorted(BENCHMARK_WORKLOADS_ROOT.glob("*.py"), key=lambda path: path.name))


def _write_test_manifest(
    tmp_path: pathlib.Path,
    filename: str,
    source: str,
) -> pathlib.Path:
    path = tmp_path / filename
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


def _build_minimal_built_native_scorecard() -> dict[str, object]:
    return {
        "summary": {
            "total_workloads": 0,
            "parser_workloads": 0,
            "module_workloads": 0,
            "regression_workloads": 0,
            "measured_workloads": 0,
            "known_gap_count": 0,
        }
    }


def _assert_built_native_runner_uses_optional_report_path(
    *,
    runner: Callable[..., dict[str, object]],
    expected_manifest_selector: str,
    expected_smoke_only: bool,
) -> None:
    expected_manifest_paths = select_benchmark_manifest_paths(expected_manifest_selector)
    scorecard = _build_minimal_built_native_scorecard()
    explicit_report_path = (
        REPO_ROOT / "reports" / "benchmarks" / "explicit-native-check.json"
    )

    with mock.patch.object(benchmarks, "run_benchmarks", return_value=scorecard) as mocked_run:
        returned = runner()

    assert returned is scorecard
    mocked_run.assert_called_once_with(
        manifest_paths=list(expected_manifest_paths),
        report_path=None,
        smoke_only=expected_smoke_only,
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        allow_fallback=False,
    )

    with mock.patch.object(benchmarks, "run_benchmarks", return_value=scorecard) as mocked_run:
        returned = runner(report_path=explicit_report_path)

    assert returned is scorecard
    mocked_run.assert_called_once_with(
        manifest_paths=list(expected_manifest_paths),
        report_path=explicit_report_path,
        smoke_only=expected_smoke_only,
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        allow_fallback=False,
    )


def _assert_built_native_cli_uses_optional_report_path(
    tmp_path: pathlib.Path,
    *,
    flag: str,
    runner_name: str,
    report_name: str,
) -> None:
    scorecard = _build_minimal_built_native_scorecard()

    with (
        mock.patch.object(benchmarks, runner_name, return_value=scorecard) as mocked_runner,
        mock.patch("builtins.print"),
    ):
        exit_code = benchmarks.main([flag])

    assert exit_code == 0
    mocked_runner.assert_called_once_with(report_path=None)

    report_path = tmp_path / report_name
    with (
        mock.patch.object(benchmarks, runner_name, return_value=scorecard) as mocked_runner,
        mock.patch("builtins.print"),
    ):
        exit_code = benchmarks.main([flag, "--report", str(report_path)])

    assert exit_code == 0
    mocked_runner.assert_called_once_with(report_path=report_path)


def _assert_built_native_mode_requires_real_built_runtime(
    report_path: pathlib.Path,
    *,
    runner: Callable[..., dict[str, object]],
) -> None:
    with mock.patch.object(
        benchmarks,
        "provision_built_native_runtime",
        return_value=(None, None, _MISSING_MATURIN_REASON),
    ):
        with pytest.raises(
            benchmarks.NativeBenchmarkProvisionError,
            match=_MISSING_MATURIN_PATTERN,
        ):
            runner(report_path=report_path)

    assert not report_path.exists()


def _assert_built_native_combined_scorecard_fields(
    scorecard: dict[str, object],
    *,
    expected_phase: str,
    expected_selection_mode: str,
    expected_manifest_count: int,
) -> None:
    implementation = scorecard["implementation"]
    environment = scorecard["environment"]
    artifacts = scorecard["artifacts"]

    assert scorecard["schema_version"] == "1.0"
    assert scorecard["phase"] == expected_phase
    assert implementation["module_name"] == "rebar"
    assert implementation["adapter_mode_requested"] == "built-native"
    assert implementation["adapter_mode_resolved"] == "built-native"
    assert implementation["build_mode"] == "built-native"
    assert implementation["timing_path"] == "built-native"
    assert implementation["native_module_loaded"] is True
    assert implementation["native_module_name"] == "rebar._rebar"
    assert implementation["native_build_tool"] == "maturin"
    assert str(implementation["native_wheel"]).startswith("rebar-")
    assert implementation["native_unavailable_reason"] is None
    assert (
        environment["execution_model"]
        == "single-interpreter subprocess workload probes against a built native wheel"
    )
    assert artifacts["manifest"] is None
    assert artifacts["manifest_id"] == "combined-benchmark-suite"
    assert artifacts["selection_mode"] == expected_selection_mode
    assert len(artifacts["manifests"]) == expected_manifest_count


# Local anchor helpers stay in this file because this test module is their only consumer.
@dataclass(frozen=True, slots=True)
class AnchoredWorkloadCasePair:
    manifest_name: str
    workload_id: str
    case_id: str
    workload: Any
    case: Any


def freeze_signature_value(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(
            (str(key), freeze_signature_value(nested_value))
            for key, nested_value in sorted(value.items())
        )
    if isinstance(value, list):
        return tuple(freeze_signature_value(item) for item in value)
    return value


@cache
def published_case_ids_by_signature(
    case_signature: Callable[[Any], tuple[Any, ...] | None],
) -> dict[tuple[Any, ...], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[Any, ...], list[str]] = {}

    for case in published_cases_by_id().values():
        signature = case_signature(case)
        if signature is None:
            continue
        case_ids_by_signature.setdefault(signature, []).append(case.case_id)

    return {
        signature: tuple(sorted(case_ids))
        for signature, case_ids in case_ids_by_signature.items()
    }


@cache
def published_cases_by_id() -> dict[str, Any]:
    cases_by_id: dict[str, Any] = {}

    for manifest in published_fixture_manifests():
        for case in manifest.cases:
            if case.case_id in cases_by_id:
                raise AssertionError(
                    f"duplicate published correctness case id {case.case_id!r}"
                )
            cases_by_id[case.case_id] = case

    return cases_by_id


@cache
def _manifest_workloads(manifest_path: pathlib.Path) -> tuple[Any, ...]:
    return tuple(load_manifest(manifest_path).workloads)


def _selected_manifest_workloads(
    manifest_path: pathlib.Path,
    *,
    include_workload: Callable[[Any], bool] | None = None,
) -> tuple[Any, ...]:
    workloads = _manifest_workloads(manifest_path)
    if include_workload is None:
        return workloads

    return tuple(workload for workload in workloads if include_workload(workload))


def anchored_workload_case_ids(
    manifest_path: pathlib.Path,
    *,
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]],
    workload_signature: Callable[[Any], tuple[Any, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> dict[tuple[str, str], tuple[str, ...]]:
    workloads = _selected_manifest_workloads(
        manifest_path,
        include_workload=include_workload,
    )

    return {
        (manifest_path.name, workload.workload_id): anchor_case_ids.get(
            workload_signature(workload),
            (),
        )
        for workload in workloads
    }


def unanchored_workload_ids(
    manifest_path: pathlib.Path,
    *,
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]],
    workload_signature: Callable[[Any], tuple[Any, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> tuple[str, ...]:
    workloads = _selected_manifest_workloads(
        manifest_path,
        include_workload=include_workload,
    )

    return tuple(
        workload.workload_id
        for workload in workloads
        if workload_signature(workload) not in anchor_case_ids
    )


def expected_anchored_workload_case_pairs(
    manifest_path: pathlib.Path,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> tuple[AnchoredWorkloadCasePair, ...]:
    manifest_name = manifest_path.name
    workloads_by_id = {
        workload.workload_id: workload
        for workload in _selected_manifest_workloads(
            manifest_path,
            include_workload=include_workload,
        )
    }
    published_cases = published_cases_by_id()
    anchored_pairs: list[AnchoredWorkloadCasePair] = []

    for (expected_manifest_name, workload_id), case_ids in expected_anchor_case_ids.items():
        if expected_manifest_name != manifest_name:
            raise AssertionError(
                f"expected anchored manifest {expected_manifest_name!r} "
                f"does not match {manifest_name!r}"
            )
        if len(case_ids) != 1:
            raise AssertionError(
                "expected exactly one published correctness case for "
                f"{(expected_manifest_name, workload_id)!r}, got {case_ids!r}"
            )

        case_id = case_ids[0]
        if workload_id not in workloads_by_id:
            raise AssertionError(
                f"expected anchored workload {workload_id!r} to be in scope for "
                f"{manifest_name!r}"
            )
        if case_id not in published_cases:
            raise AssertionError(
                f"expected anchored correctness case {case_id!r} to be published"
            )

        anchored_pairs.append(
            AnchoredWorkloadCasePair(
                manifest_name=manifest_name,
                workload_id=workload_id,
                case_id=case_id,
                workload=workloads_by_id[workload_id],
                case=published_cases[case_id],
            )
        )

    return tuple(anchored_pairs)


def assert_anchored_workload_case_result_parity(
    anchored_pairs: Iterable[AnchoredWorkloadCasePair],
) -> None:
    for anchored_pair in anchored_pairs:
        try:
            expected = run_correctness_case_with_cpython(anchored_pair.case)
        except Exception as expected_exc:
            with pytest.raises(type(expected_exc)) as observed_exc:
                run_benchmark_workload_with_cpython(anchored_pair.workload)
            assert str(observed_exc.value) == str(expected_exc)
            continue
        assert_benchmark_workload_matches_expected_result(
            anchored_pair.workload,
            expected,
        )


def assert_benchmark_workload_matches_expected_result(
    workload: Any,
    expected: object,
) -> None:
    observed = run_benchmark_workload_with_cpython(workload)

    if workload.operation == "module.compile":
        assert_pattern_parity("stdlib", observed, expected)
        return

    if workload.operation in {
        "module.search",
        "module.match",
        "module.fullmatch",
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
    }:
        assert_match_result_parity(
            "stdlib",
            observed,
            expected,
            check_regs=True,
        )
        return

    if workload.operation in {
        "module.split",
        "module.findall",
        "pattern.findall",
        "module.sub",
        "module.subn",
        "pattern.split",
        "pattern.sub",
        "pattern.subn",
    }:
        assert observed == expected
        return

    if workload.operation in {"module.finditer", "pattern.finditer"}:
        assert isinstance(observed, list)
        expected_matches = list(expected)
        assert len(observed) == len(expected_matches)
        for observed_match, expected_match in zip(
            observed,
            expected_matches,
            strict=True,
        ):
            assert_match_result_parity(
                "stdlib",
                observed_match,
                expected_match,
                check_regs=True,
            )
        return

    raise AssertionError(
        "unexpected anchored benchmark workload operation "
        f"{workload.operation!r}"
    )


def run_benchmark_workload_with_cpython(workload: Any) -> object:
    re.purge()
    callback = build_callable(re, "re", workload)
    result = callback()
    re.purge()
    return result


def run_correctness_case_with_cpython(case: Any) -> object:
    if case.operation == "compile":
        return re.compile(case.pattern_payload(), case.flags or 0)

    if case.operation == "module_call":
        if case.helper is None:
            raise AssertionError(f"expected helper for {case.case_id!r}")
        compiled_pattern = None
        if case.use_compiled_pattern:
            compiled_pattern = re.compile(case.pattern_payload(), case.flags or 0)
        if not case.use_compiled_pattern and not case.include_pattern_arg:
            if case.pattern is None:
                return getattr(re, case.helper)(
                    *case.args,
                    **case.kwargs,
                )
            return getattr(re, case.helper)(
                case.pattern_payload(),
                *case.args,
                **case.kwargs,
            )
        return getattr(re, case.helper)(
            *case.module_call_args(compiled_pattern),
            **case.kwargs,
        )

    if case.operation == "pattern_call":
        if case.helper is None:
            raise AssertionError(f"expected helper for {case.case_id!r}")
        compiled = re.compile(case.pattern_payload(), case.flags or 0)
        return getattr(compiled, case.helper)(*case.args, **case.kwargs)

    raise AssertionError(f"unexpected correctness operation {case.operation!r}")


@dataclass(frozen=True, slots=True)
class StandardBenchmarkAnchorContractDefinition:
    name: str
    manifest_paths: tuple[pathlib.Path, ...]
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    include_workload: Callable[[Any], bool]
    correctness_case_signature: Callable[[Any], tuple[Any, ...] | None]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    run_callback_result_parity: bool = False
    expected_excluded_workload_ids: frozenset[str] = frozenset()
    expected_legacy_workload_ids: frozenset[str] = frozenset()
    callback_anchor_workload_ids: frozenset[str] = frozenset()
    expected_special_unanchored_workload_ids: tuple[str, ...] = ()
    direct_parity_supplemental_cases: tuple[Any, ...] = ()
    run_special_unanchored_result_parity: bool = False

    def includes_workload(self, workload: Any) -> bool:
        return (
            workload.workload_id not in self.expected_excluded_workload_ids
            and workload.workload_id not in self.expected_special_unanchored_workload_ids
            and self.include_workload(workload)
        )


def _anchor_case_subset(
    anchor_case_ids: dict[tuple[str, str], tuple[str, ...]],
    workload_ids: Iterable[str],
) -> dict[tuple[str, str], tuple[str, ...]]:
    selected_workload_ids = frozenset(workload_ids)
    return {
        key: case_ids
        for key, case_ids in anchor_case_ids.items()
        if key[1] in selected_workload_ids
    }


def _definition_anchor_expectations(
    manifest_path: pathlib.Path,
    anchor_expectations: dict[str, tuple[str, ...]],
) -> dict[tuple[str, str], tuple[str, ...]]:
    return {
        (manifest_path.name, workload_id): case_ids
        for workload_id, case_ids in anchor_expectations.items()
    }


OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID = (
    "module-search-numbered-optional-group-conditional-cold-gap"
)


def _compile_proxy_signature(
    pattern: str | bytes,
    *,
    flags: int,
    text_model: str,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str]:
    return ("module.compile", pattern, (), (), flags, text_model)


def _compile_proxy_correctness_case_signature(
    case: Any,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str] | None:
    if case.operation != "compile":
        return None
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, (str, bytes))
    return _compile_proxy_signature(
        pattern,
        flags=case.flags or 0,
        text_model=case.text_model or "str",
    )


def _compile_proxy_workload_signature(
    workload: Any,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str]:
    pattern = workload.pattern_payload()
    assert isinstance(pattern, (str, bytes))
    return _compile_proxy_signature(
        pattern,
        flags=workload.flags,
        text_model=workload.text_model,
    )


def _is_compile_proxy_workload(workload: Any) -> bool:
    return workload.operation in {"compile", "module.compile"}


_COLLECTION_REPLACEMENT_SPLIT_OPERATIONS = frozenset(
    {"module.split", "pattern.split"}
)
_COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS = frozenset(
    {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
)


def _is_encoded_indexlike_payload(value: object) -> bool:
    return (
        isinstance(value, dict)
        and value.get("type") == "indexlike"
        and isinstance(value.get("value"), int)
        and not isinstance(value.get("value"), bool)
    )


def _collection_replacement_keyword_parameter_name(
    workload: Any,
) -> str | None:
    if workload.operation in _COLLECTION_REPLACEMENT_SPLIT_OPERATIONS:
        return "maxsplit"
    if workload.operation in _COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS:
        return "count"
    return None


def _collection_replacement_parameter_payload(
    workload: Any,
) -> object | None:
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if keyword_parameter == "maxsplit":
        return workload.maxsplit
    if keyword_parameter == "count":
        return workload.count
    return None


def _collection_replacement_has_expected_unexpected_keyword_error(
    workload: Any,
) -> bool:
    if tuple(workload.kwargs) != ("missing",):
        return False
    expected_exception = workload.expected_exception
    if expected_exception is None or expected_exception.get("type") != "TypeError":
        return False
    message_substring = expected_exception.get("message_substring")
    if not isinstance(message_substring, str):
        return False
    if "unexpected keyword argument 'missing'" in message_substring:
        return True
    if workload.operation.startswith("pattern."):
        helper_name = workload.operation.removeprefix("pattern.")
        return (
            message_substring
            == f"'missing' is an invalid keyword argument for {helper_name}()"
        )
    return False


def _module_workflow_positional_args_signature(
    args: tuple[object, ...] | list[object],
) -> tuple[tuple[str, object], ...]:
    signature: list[tuple[str, object]] = []
    for value in args:
        if isinstance(value, bool):
            signature.append(("bool", value))
            continue
        if isinstance(value, int):
            signature.append(("int", int(value)))
            continue
        if isinstance(value, (str, bytes)):
            signature.append((type(value).__name__, value))
            continue
        if (
            isinstance(value, dict)
            and value.get("type") == "indexlike"
            and isinstance(value.get("value"), int)
            and not isinstance(value.get("value"), bool)
        ):
            signature.append(("indexlike", int(value["value"])))
            continue
        if hasattr(value, "__index__"):
            signature.append(("indexlike", int(value.__index__())))
            continue
        signature.append((type(value).__name__, repr(value)))
    return tuple(signature)


def _module_workflow_keyword_kwargs_signature(
    kwargs: dict[str, object],
) -> tuple[tuple[str, str, object], ...]:
    signature: list[tuple[str, str, object]] = []
    for name, value in sorted(kwargs.items()):
        if isinstance(value, bool):
            signature.append((name, "bool", value))
            continue
        if isinstance(value, int):
            signature.append((name, "int", int(value)))
            continue
        if (
            isinstance(value, dict)
            and value.get("type") == "indexlike"
            and isinstance(value.get("value"), int)
            and not isinstance(value.get("value"), bool)
        ):
            signature.append((name, "indexlike", int(value["value"])))
            continue
        if hasattr(value, "__index__"):
            signature.append((name, "indexlike", int(value.__index__())))
            continue
        signature.append((name, type(value).__name__, repr(value)))
    return tuple(signature)


def _module_workflow_positional_indexlike_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.helper not in {"split", "sub", "subn"} or case.kwargs:
        return None
    if case.operation == "module_call":
        if case.use_compiled_pattern or not case.include_pattern_arg:
            return None
    elif case.operation != "pattern_call":
        return None
    if not any(hasattr(argument, "__index__") for argument in case.args):
        return None
    return (
        case.helper,
        case_pattern(case),
        _module_workflow_positional_args_signature(case.args),
        case.text_model or "str",
    )


def _collection_replacement_positional_indexlike_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation in {"module.split", "pattern.split"}:
        return (
            workload.haystack_payload(),
            workload.maxsplit,
        )
    if workload.operation in {
        "module.sub",
        "module.subn",
        "pattern.sub",
        "pattern.subn",
    }:
        return (
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count,
        )
    raise AssertionError(
        "unexpected collection/replacement positional-indexlike workload operation "
        f"{workload.operation!r}"
    )


def _collection_replacement_positional_indexlike_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_positional_indexlike_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement positional-indexlike workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation.removeprefix("module.").removeprefix("pattern."),
        workload.pattern_payload(),
        _module_workflow_positional_args_signature(
            _collection_replacement_positional_indexlike_workload_args(workload)
        ),
        workload.text_model,
    )


def _is_collection_replacement_positional_indexlike_workload(workload: Any) -> bool:
    return (
        not workload.kwargs
        and workload.expected_exception is None
        and _is_encoded_indexlike_payload(
            _collection_replacement_parameter_payload(workload)
        )
    )


def _collection_replacement_expected_keyword_field(
    workload: Any,
) -> str | None:
    if workload.operation.startswith("module."):
        return (
            benchmarks._expected_duplicate_module_helper_keyword_field(workload)
            or benchmarks._expected_positional_module_helper_keyword_field(workload)
        )
    if workload.operation.startswith("pattern."):
        return benchmarks._expected_pattern_helper_positional_keyword_field(workload)
    return None


def _collection_replacement_positional_keyword_field(
    workload: Any,
) -> str | None:
    expected_keyword_field = _collection_replacement_expected_keyword_field(workload)
    if expected_keyword_field is None:
        return None
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if expected_keyword_field != keyword_parameter:
        return None
    return expected_keyword_field


def _collection_replacement_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if not case.kwargs:
        return None
    if case.helper not in {"split", "sub", "subn"}:
        return None
    use_compiled_pattern = False
    if case.operation == "module_call":
        use_compiled_pattern = case.use_compiled_pattern
    elif case.operation != "pattern_call":
        return None
    return (
        f"{'module' if case.operation == 'module_call' else 'pattern'}.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        _module_workflow_keyword_kwargs_signature(case.kwargs),
        use_compiled_pattern,
        case.flags or 0,
        case.text_model or "str",
    )


def _collection_replacement_keyword_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    positional_keyword_field = _collection_replacement_positional_keyword_field(
        workload
    )
    if workload.operation in {"module.split", "pattern.split"}:
        args: list[object] = [workload.haystack_payload()]
        if positional_keyword_field == "maxsplit":
            args.append(workload.maxsplit)
        return tuple(args)
    if workload.operation in {
        "module.sub",
        "module.subn",
        "pattern.sub",
        "pattern.subn",
    }:
        args: list[object] = [
            workload.replacement_payload(),
            workload.haystack_payload(),
        ]
        if positional_keyword_field == "count":
            args.append(workload.count)
        return tuple(args)
    raise AssertionError(
        "unexpected collection/replacement keyword workload operation "
        f"{workload.operation!r}"
    )


def _collection_replacement_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_keyword_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement keyword workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(
            list(_collection_replacement_keyword_workload_args(workload))
        ),
        _module_workflow_keyword_kwargs_signature(workload.kwargs),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_collection_replacement_keyword_workload(workload: Any) -> bool:
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if keyword_parameter is None or not workload.kwargs:
        return False
    keyword_names = tuple(workload.kwargs)
    if len(keyword_names) != 1:
        return False
    if keyword_names[0] == keyword_parameter:
        return True
    if _collection_replacement_expected_keyword_field(workload) is not None:
        return True
    return _collection_replacement_has_expected_unexpected_keyword_error(workload)


def _is_collection_replacement_compiled_pattern_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and workload.use_compiled_pattern
        and workload.operation in {"module.split", "module.sub", "module.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
    )


def _collection_replacement_wrong_text_model_haystack_index(operation: str) -> int:
    if operation in {"module.split", "module.findall", "module.finditer"}:
        return 0
    if operation in {"module.sub", "module.subn"}:
        return 1
    raise AssertionError(
        "unexpected collection/replacement wrong-text-model workload operation "
        f"{operation!r}"
    )


def _collection_replacement_compiled_pattern_success_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"split", "findall", "finditer", "sub", "subn"}:
        return None
    operation = f"module.{case.helper}"
    haystack_index = _collection_replacement_wrong_text_model_haystack_index(operation)
    if len(case.args) <= haystack_index:
        return None
    haystack = case.args[haystack_index]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, str):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, bytes):
        return None
    return (
        operation,
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_compiled_pattern_success_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation == "module.split":
        return (
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )
    if workload.operation in {"module.findall", "module.finditer"}:
        return (workload.haystack_payload(),)
    if workload.operation in {"module.sub", "module.subn"}:
        return (
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
    raise AssertionError(
        "unexpected collection/replacement compiled-pattern success workload "
        f"operation {workload.operation!r}"
    )


def _collection_replacement_compiled_pattern_success_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_compiled_pattern_success_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement compiled-pattern success workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(
            list(_collection_replacement_compiled_pattern_success_workload_args(workload))
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_collection_replacement_compiled_pattern_success_workload(
    workload: Any,
) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is None
        and not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation
        in {
            "module.split",
            "module.findall",
            "module.finditer",
            "module.sub",
            "module.subn",
        }
        and workload.expected_exception is None
        and workload.pattern == "abc"
    )


def _collection_replacement_wrong_text_model_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"split", "findall", "finditer", "sub", "subn"}:
        return None
    operation = f"module.{case.helper}"
    haystack_index = _collection_replacement_wrong_text_model_haystack_index(operation)
    if len(case.args) <= haystack_index:
        return None
    haystack = case.args[haystack_index]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, bytes):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, str):
        return None
    return (
        operation,
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_wrong_text_model_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation == "module.split":
        return (
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )
    if workload.operation in {"module.findall", "module.finditer"}:
        return (workload.haystack_payload(),)
    if workload.operation in {"module.sub", "module.subn"}:
        return (
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
    raise AssertionError(
        "unexpected collection/replacement wrong-text-model workload operation "
        f"{workload.operation!r}"
    )


def _collection_replacement_wrong_text_model_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_wrong_text_model_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement wrong-text-model workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(
            list(_collection_replacement_wrong_text_model_workload_args(workload))
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_collection_replacement_wrong_text_model_workload(workload: Any) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is not None
        and not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation
        in {
            "module.split",
            "module.findall",
            "module.finditer",
            "module.sub",
            "module.subn",
        }
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )


def _pattern_collection_replacement_wrong_text_model_haystack_index(
    operation: str,
) -> int:
    if operation == "pattern.split":
        return 0
    if operation in {"pattern.sub", "pattern.subn"}:
        return 1
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {operation!r}"
    )


def _collection_replacement_pattern_wrong_text_model_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"split", "sub", "subn"}:
        return None
    operation = f"pattern.{case.helper}"
    haystack_index = _pattern_collection_replacement_wrong_text_model_haystack_index(
        operation
    )
    case_args = list(case.args)
    if len(case_args) <= haystack_index:
        return None
    haystack = case_args[haystack_index]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, bytes):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, str):
        return None
    return (
        operation,
        case_pattern(case),
        freeze_signature_value(case_args),
        (),
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_pattern_wrong_text_model_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation == "pattern.split":
        args: list[object] = [workload.haystack_payload()]
        if workload.maxsplit:
            args.append(workload.maxsplit_argument())
        return tuple(args)
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [
            workload.replacement_payload(),
            workload.haystack_payload(),
        ]
        if workload.count:
            args.append(workload.count_argument())
        return tuple(args)
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {workload.operation!r}"
    )


def _collection_replacement_pattern_wrong_text_model_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_pattern_wrong_text_model_workload(workload):
        raise AssertionError(
            "unexpected direct Pattern collection/replacement wrong-text-model "
            f"workload {workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(
            list(
                _collection_replacement_pattern_wrong_text_model_workload_args(
                    workload
                )
            )
        ),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_collection_replacement_pattern_wrong_text_model_workload(
    workload: Any,
) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is not None
        and not workload.kwargs
        and not workload.use_compiled_pattern
        and workload.operation in {"pattern.split", "pattern.sub", "pattern.subn"}
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )


def _module_workflow_compiled_pattern_compile_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper != "compile" or case.args:
        return None
    case_text_model = case.text_model or "str"
    return (
        "module.compile",
        case_pattern(case),
        (),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_compile_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_compile_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern module.compile workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        (),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_compiled_pattern_compile_workload(workload: Any) -> bool:
    return (
        not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation == "module.compile"
    )


def _is_module_workflow_compiled_pattern_compile_literal_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_compile_workload(workload)
        and workload.expected_exception is None
        and workload.pattern == "abc"
        and workload.flags == 0
    )


def _is_module_workflow_compiled_pattern_compile_named_group_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_compile_workload(workload)
        and workload.expected_exception is None
        and workload.pattern == "(?P<word>abc)"
        and workload.flags == 0
    )


_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE = (
    ("flags", "int", 0),
)
_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE = (
    ("flags", "bool", False),
)
_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE = (
    ("flags", "int", int(re.IGNORECASE)),
)
_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS = ("abc",)
_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS = (
    "(?P<word>abc)",
)
_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION = {
    "type": "ValueError",
    "message_substring": "cannot process flags argument with a compiled pattern",
}


def _compiled_pattern_module_compile_keyword_kwargs_signature(
    kwargs: dict[str, object],
) -> tuple[tuple[str, str, object], ...]:
    signature: list[tuple[str, str, object]] = []
    for name, value in sorted(kwargs.items()):
        if isinstance(value, bool):
            signature.append((name, "bool", value))
            continue
        if isinstance(value, re.RegexFlag) and int(value) == 0:
            signature.append((name, "noflag", 0))
            continue
        if isinstance(value, int):
            signature.append((name, "int", int(value)))
            continue
        signature.append((name, type(value).__name__, repr(value)))
    return tuple(signature)


def _workload_matches_expected_exception(
    workload: Any,
    *,
    expected_exception: dict[str, str] | None,
) -> bool:
    if expected_exception is None:
        return workload.expected_exception is None
    return workload.expected_exception == expected_exception


def _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
    case: Any,
    *,
    keyword_signature: tuple[tuple[str, str, object], ...],
    allowed_patterns: tuple[str, ...],
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or not case.use_compiled_pattern:
        return None
    if case.helper != "compile" or case.args:
        return None
    if (
        _compiled_pattern_module_compile_keyword_kwargs_signature(case.kwargs)
        != keyword_signature
    ):
        return None
    if case.pattern not in allowed_patterns:
        return None
    case_text_model = case.text_model or "str"
    return (
        "module.compile",
        case_pattern(case),
        (),
        keyword_signature,
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_compile_keyword_workload_signature(
    workload: Any,
    *,
    keyword_label: str,
    keyword_signature: tuple[tuple[str, str, object], ...],
    allowed_patterns: tuple[str, ...],
    expected_exception: dict[str, str] | None = None,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_compile_keyword_workload(
        workload,
        keyword_signature=keyword_signature,
        allowed_patterns=allowed_patterns,
        expected_exception=expected_exception,
    ):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern module.compile "
            f"{keyword_label} keyword workload {workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        (),
        keyword_signature,
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_compiled_pattern_compile_keyword_workload(
    workload: Any,
    *,
    keyword_signature: tuple[tuple[str, str, object], ...],
    allowed_patterns: tuple[str, ...],
    expected_exception: dict[str, str] | None = None,
) -> bool:
    return (
        workload.use_compiled_pattern
        and workload.operation == "module.compile"
        and _workload_matches_expected_exception(
            workload,
            expected_exception=expected_exception,
        )
        and workload.pattern in allowed_patterns
        and workload.flags == 0
        and _compiled_pattern_module_compile_keyword_kwargs_signature(workload.kwargs)
        == keyword_signature
    )


def _module_workflow_compiled_pattern_compile_int_zero_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    return _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
        case,
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
    )


def _module_workflow_compiled_pattern_compile_int_zero_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    return _module_workflow_compiled_pattern_compile_keyword_workload_signature(
        workload,
        keyword_label="int-zero",
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
    )


def _is_module_workflow_compiled_pattern_compile_int_zero_keyword_workload(
    workload: Any,
) -> bool:
    return _is_module_workflow_compiled_pattern_compile_keyword_workload(
        workload,
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
    )


def _module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    return _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
        case,
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
    )


def _module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    return _module_workflow_compiled_pattern_compile_keyword_workload_signature(
        workload,
        keyword_label="int-zero-named-group",
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
    )


def _is_module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_workload(
    workload: Any,
) -> bool:
    return _is_module_workflow_compiled_pattern_compile_keyword_workload(
        workload,
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
    )


def _module_workflow_compiled_pattern_compile_bool_false_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    return _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
        case,
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
    )


def _module_workflow_compiled_pattern_compile_bool_false_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    return _module_workflow_compiled_pattern_compile_keyword_workload_signature(
        workload,
        keyword_label="bool-false",
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
    )


def _is_module_workflow_compiled_pattern_compile_bool_false_keyword_workload(
    workload: Any,
) -> bool:
    return _is_module_workflow_compiled_pattern_compile_keyword_workload(
        workload,
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
    )


def _module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    return _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
        case,
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
    )


def _module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    return _module_workflow_compiled_pattern_compile_keyword_workload_signature(
        workload,
        keyword_label="bool-false-named-group",
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
    )


def _is_module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_workload(
    workload: Any,
) -> bool:
    return _is_module_workflow_compiled_pattern_compile_keyword_workload(
        workload,
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
    )


def _module_workflow_compiled_pattern_compile_ignorecase_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    return _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
        case,
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
    )


def _module_workflow_compiled_pattern_compile_ignorecase_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    return _module_workflow_compiled_pattern_compile_keyword_workload_signature(
        workload,
        keyword_label="ignorecase",
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
        expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
    )


def _is_module_workflow_compiled_pattern_compile_ignorecase_keyword_workload(
    workload: Any,
) -> bool:
    return _is_module_workflow_compiled_pattern_compile_keyword_workload(
        workload,
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
        expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
    )


def _module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    return _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
        case,
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
    )


def _module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    return _module_workflow_compiled_pattern_compile_keyword_workload_signature(
        workload,
        keyword_label="ignorecase-named-group",
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
        expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
    )


def _is_module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_workload(
    workload: Any,
) -> bool:
    return _is_module_workflow_compiled_pattern_compile_keyword_workload(
        workload,
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
        expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
    )


def _module_workflow_compiled_pattern_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"search", "match", "fullmatch"}:
        return None
    if not case.args:
        return None
    case_text_model = case.text_model or "str"
    return (
        f"module.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_workload_args(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern workload "
            f"{workload.workload_id!r}"
        )
    return (workload.haystack_payload(),)


def _module_workflow_compiled_pattern_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(list(_module_workflow_compiled_pattern_workload_args(workload))),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_compiled_pattern_workload(workload: Any) -> bool:
    return (
        not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation in {"module.search", "module.match", "module.fullmatch"}
    )


def _is_module_workflow_compiled_pattern_literal_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is None
        and workload.expected_exception is None
        and workload.pattern == "abc"
    )


def _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is None
        and workload.expected_exception is None
        and workload.pattern == "a.c"
        and workload.text_model == "str"
    )


def _is_module_workflow_compiled_pattern_verbose_bytes_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is None
        and workload.expected_exception is None
        and workload.pattern == _VERBOSE_REGRESSION_PATTERN
        and workload.flags == _VERBOSE_REGRESSION_FLAGS
        and workload.text_model == "bytes"
    )


def _is_module_workflow_compiled_pattern_wrong_text_model_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is not None
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )


def _module_workflow_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or not case.kwargs:
        return None
    if case.use_compiled_pattern or case.helper not in {"search", "match", "fullmatch"}:
        return None
    return (
        f"module.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        _module_workflow_keyword_kwargs_signature(case.kwargs),
        case.flags or 0,
        case.text_model or "str",
    )


def _module_workflow_keyword_workload_args(
    workload: Any,
) -> tuple[Any, ...]:
    if not (
        _is_module_workflow_keyword_flags_workload(workload)
        or _is_module_workflow_keyword_error_workload(workload)
    ):
        raise AssertionError(
            "unexpected module-workflow keyword workload "
            f"{workload.workload_id!r}"
        )
    args: list[object] = [workload.haystack_payload()]
    if (
        workload.operation == "module.search"
        and workload.expected_exception is not None
        and "flags" in workload.kwargs
    ):
        args.append(workload.flags)
    return tuple(args)


def _module_workflow_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not (
        _is_module_workflow_keyword_flags_workload(workload)
        or _is_module_workflow_keyword_error_workload(workload)
    ):
        raise AssertionError(
            "unexpected module-workflow keyword workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(list(_module_workflow_keyword_workload_args(workload))),
        _module_workflow_keyword_kwargs_signature(workload.kwargs),
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_keyword_flags_workload(workload: Any) -> bool:
    keyword_names = tuple(workload.kwargs)
    return (
        workload.operation in {"module.search", "module.match", "module.fullmatch"}
        and bool(workload.kwargs)
        and len(keyword_names) == 1
        and keyword_names[0] == "flags"
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
    )


def _is_module_workflow_keyword_error_workload(workload: Any) -> bool:
    keyword_names = tuple(workload.kwargs)
    expected_exception = workload.expected_exception
    if (
        workload.operation
        not in {"module.search", "module.match", "module.fullmatch"}
        or not workload.kwargs
        or len(keyword_names) != 1
        or expected_exception is None
        or expected_exception.get("type") != "TypeError"
        or workload.use_compiled_pattern
    ):
        return False
    message = expected_exception.get("message_substring", "")
    if keyword_names[0] == "flags":
        return "multiple values for argument" in message
    if keyword_names[0] == "missing":
        return "unexpected keyword argument" in message
    return False


def _pattern_window_positional_indexlike_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch", "findall", "finditer"}:
        return None
    if not any(hasattr(argument, "__index__") for argument in case.args):
        return None
    return (
        case.helper,
        case_pattern(case),
        _module_workflow_positional_args_signature(case.args),
        case.text_model or "str",
    )


def _pattern_window_positional_indexlike_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation not in {
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
        "pattern.findall",
        "pattern.finditer",
    }:
        raise AssertionError(
            "unexpected pattern positional-indexlike workload operation "
            f"{workload.operation!r}"
        )

    args: list[object] = [workload.haystack_payload()]
    if workload.pos is not None or workload.endpos is not None:
        args.append(0 if workload.pos is None else workload.pos)
    if workload.endpos is not None:
        args.append(workload.endpos)
    return tuple(args)


def _pattern_window_positional_indexlike_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_window_positional_indexlike_workload(workload):
        raise AssertionError(
            "unexpected pattern positional-indexlike workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation.removeprefix("pattern."),
        workload.pattern_payload(),
        _module_workflow_positional_args_signature(
            _pattern_window_positional_indexlike_workload_args(workload)
        ),
        workload.text_model,
    )


def _is_pattern_window_positional_indexlike_workload(workload: Any) -> bool:
    categories = set(workload.categories)
    return (
        workload.operation in {
            "pattern.search",
            "pattern.match",
            "pattern.fullmatch",
            "pattern.findall",
            "pattern.finditer",
        }
        and workload.expected_exception is None
        and not workload.kwargs
        and {"positional-window", "indexlike"}.issubset(categories)
        and (
            _is_encoded_indexlike_payload(workload.pos)
            or _is_encoded_indexlike_payload(workload.endpos)
        )
    )


def _pattern_keyword_window_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or not case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch", "findall", "finditer"}:
        return None
    return (
        f"pattern.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        _module_workflow_keyword_kwargs_signature(case.kwargs),
        case.flags or 0,
        case.text_model or "str",
    )


def _pattern_keyword_window_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_keyword_window_workload(workload):
        raise AssertionError(
            "unexpected pattern keyword-window workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value([workload.haystack_payload()]),
        _module_workflow_keyword_kwargs_signature(workload.kwargs),
        workload.flags,
        workload.text_model,
    )


def _is_pattern_keyword_window_workload(workload: Any) -> bool:
    categories = set(workload.categories)
    return (
        workload.operation in {
            "pattern.search",
            "pattern.match",
            "pattern.fullmatch",
            "pattern.findall",
            "pattern.finditer",
        }
        and workload.expected_exception is None
        and workload.pos is None
        and workload.endpos is None
        and bool(workload.kwargs)
        and set(workload.kwargs).issubset({"pos", "endpos"})
        and "keyword" in categories
    )


def _optional_group_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.helper != "search":
        return None

    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"
    return (
        "module.search",
        None,
        freeze_signature_value(case.serialized_args()),
        kwargs_signature,
        flags,
        text_model,
    )


def _optional_group_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation != "module.search":
        raise AssertionError(
            "unexpected optional-group benchmark workload operation "
            f"{workload.operation!r}"
        )

    return (
        "module.search",
        None,
        freeze_signature_value([workload.pattern, workload.haystack]),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_optional_group_conditional_workload(workload: Any) -> bool:
    return workload.workload_id == OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID


def _nested_group_correctness_case_signature(case: Any) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", case.pattern, (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper == "search":
        return (
            "module.search",
            None,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper == "fullmatch":
        return (
            "pattern.fullmatch",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _nested_group_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            workload.pattern,
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "module.search":
        return (
            "module.search",
            None,
            (workload.pattern, workload.haystack),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "pattern.fullmatch":
        return (
            "pattern.fullmatch",
            workload.pattern,
            (workload.haystack,),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected nested-group workload operation {workload.operation!r}"
    )
def _counted_repeat_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return (
            "module.compile",
            case.pattern_payload(),
            (),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "module_call" and case.helper == "search":
        return (
            "module.search",
            None,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper == "fullmatch":
        return (
            "pattern.fullmatch",
            case.pattern_payload(),
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _counted_repeat_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            workload.pattern_payload(),
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "module.search":
        return (
            "module.search",
            None,
            freeze_signature_value(
                [
                    workload.pattern_payload(),
                    workload.haystack_payload(),
                ]
            ),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "pattern.fullmatch":
        return (
            "pattern.fullmatch",
            workload.pattern_payload(),
            freeze_signature_value([workload.haystack_payload()]),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected counted-repeat benchmark workload operation {workload.operation!r}"
    )


def _is_non_alternation_counted_repeat_workload(workload: Any) -> bool:
    return workload.operation in {
        "module.compile",
        "module.search",
        "pattern.fullmatch",
    } and "|" not in workload.pattern


def _grouped_alternation_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", case.pattern, (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper in {"search", "sub", "subn"}:
        return (
            f"module.{case.helper}",
            None,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"fullmatch", "sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _grouped_alternation_workload_args(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return ()
    if workload.operation == "module.search":
        return freeze_signature_value([workload.pattern, workload.haystack])
    if workload.operation == "pattern.fullmatch":
        return freeze_signature_value([workload.haystack])
    if workload.operation in {"module.sub", "module.subn"}:
        args = [workload.pattern, workload.replacement, workload.haystack]
        if workload.count:
            args.append(workload.count)
        return freeze_signature_value(args)
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [workload.replacement, workload.haystack]
        if workload.count:
            args.append(workload.count)
        return freeze_signature_value(args)
    raise AssertionError(
        f"unexpected grouped-alternation benchmark workload operation {workload.operation!r}"
    )


def _grouped_alternation_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            workload.pattern,
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"module.search", "module.sub", "module.subn"}:
        return (
            workload.operation,
            None,
            _grouped_alternation_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"pattern.fullmatch", "pattern.sub", "pattern.subn"}:
        return (
            workload.operation,
            workload.pattern,
            _grouped_alternation_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected grouped-alternation benchmark workload operation {workload.operation!r}"
    )


def _grouped_alternation_replacement_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "module_call" and case.helper in {"sub", "subn"}:
        return (
            f"module.{case.helper}",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _grouped_alternation_replacement_workload_args(workload: Any) -> tuple[Any, ...]:
    if workload.operation in {"module.sub", "module.subn"}:
        args = [workload.pattern, workload.replacement, workload.haystack]
    elif workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [workload.replacement, workload.haystack]
    else:
        raise AssertionError(
            "unexpected grouped-alternation replacement workload operation "
            f"{workload.operation!r}"
        )

    if workload.count:
        args.append(workload.count)
    return freeze_signature_value(args)


def _grouped_alternation_replacement_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if workload.operation in {"module.sub", "module.subn"}:
        return (
            workload.operation,
            None,
            _grouped_alternation_replacement_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        return (
            workload.operation,
            workload.pattern,
            _grouped_alternation_replacement_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        "unexpected grouped-alternation replacement workload operation "
        f"{workload.operation!r}"
    )


def _include_all_workloads(_: Any) -> bool:
    return True


@cache
def _manifest_workloads_by_id(manifest_path: pathlib.Path) -> dict[str, Any]:
    return {
        workload.workload_id: workload for workload in load_manifest(manifest_path).workloads
    }


def _definition_workloads_by_id(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[str, Any]:
    workloads_by_id: dict[str, Any] = {}
    for manifest_path in definition.manifest_paths:
        workloads_by_id.update(_manifest_workloads_by_id(manifest_path))
    return workloads_by_id


@cache
def _direct_parity_case_ids_by_signature(
    supplemental_cases: tuple[Any, ...],
) -> dict[tuple[str, bytes, bytes], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[str, bytes, bytes], list[str]] = {}

    for case in supplemental_cases:
        for haystack in case.search_matches + case.search_misses:
            case_ids_by_signature.setdefault(
                ("module.search", case.pattern, haystack),
                [],
            ).append(case.id)
        for haystack in case.fullmatch_matches + case.fullmatch_misses:
            case_ids_by_signature.setdefault(
                ("pattern.fullmatch", case.pattern, haystack),
                [],
            ).append(case.id)

    return {
        signature: tuple(case_ids)
        for signature, case_ids in case_ids_by_signature.items()
    }


def _manual_expected_result(workload: Any) -> object:
    pattern = workload.pattern_payload()
    re.purge()
    try:
        if workload.operation == "module.compile":
            pattern_argument = (
                re.compile(pattern, workload.flags)
                if workload.use_compiled_pattern
                else pattern
            )
            return re.compile(pattern_argument, workload.flags)
        if workload.operation == "module.search":
            return re.search(pattern, workload.haystack_payload(), workload.flags)
        if workload.operation == "pattern.search":
            compiled = re.compile(pattern, workload.flags)
            if workload.endpos is not None:
                return compiled.search(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                    workload.endpos_argument(),
                )
            if workload.pos is not None:
                return compiled.search(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                )
            return compiled.search(workload.haystack_payload())
        if workload.operation == "pattern.fullmatch":
            compiled = re.compile(pattern, workload.flags)
            if workload.endpos is not None:
                return compiled.fullmatch(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                    workload.endpos_argument(),
                )
            if workload.pos is not None:
                return compiled.fullmatch(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                )
            return compiled.fullmatch(workload.haystack_payload())
        if workload.operation == "pattern.findall":
            compiled = re.compile(pattern, workload.flags)
            if workload.endpos is not None:
                return compiled.findall(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                    workload.endpos_argument(),
                )
            if workload.pos is not None:
                return compiled.findall(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                )
            return compiled.findall(workload.haystack_payload())
        if workload.operation == "pattern.finditer":
            compiled = re.compile(pattern, workload.flags)
            if workload.endpos is not None:
                return list(
                    compiled.finditer(
                        workload.haystack_payload(),
                        workload.pos_argument(),
                        workload.endpos_argument(),
                    )
                )
            if workload.pos is not None:
                return list(
                    compiled.finditer(
                        workload.haystack_payload(),
                        workload.pos_argument(),
                    )
                )
            return list(compiled.finditer(workload.haystack_payload()))
        if workload.operation == "module.sub":
            return re.sub(
                pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
                workload.flags,
            )
        if workload.operation == "module.subn":
            return re.subn(
                pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
                workload.flags,
            )
        if workload.operation == "pattern.sub":
            compiled = re.compile(pattern, workload.flags)
            return compiled.sub(
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
            )
        if workload.operation == "pattern.subn":
            compiled = re.compile(pattern, workload.flags)
            return compiled.subn(
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
            )
    finally:
        re.purge()

    raise AssertionError(
        f"unexpected special-unanchored benchmark workload operation {workload.operation!r}"
    )


STANDARD_BENCHMARK_DEFINITIONS = (
    StandardBenchmarkAnchorContractDefinition(
        name="compile-proxy",
        manifest_paths=(
            COMPILE_MATRIX_MANIFEST_PATH,
            REGRESSION_MATRIX_MANIFEST_PATH,
        ),
        expected_anchor_case_ids=(
            _definition_anchor_expectations(
                COMPILE_MATRIX_MANIFEST_PATH,
                {
                    "compile-inline-locale-bytes-warm": (
                        "bytes-inline-locale-flag-success",
                    ),
                    "compile-lookbehind-cold": (
                        "str-fixed-width-lookbehind-success",
                    ),
                    "compile-character-class-ignorecase-warm": (
                        "str-character-class-ignorecase-success",
                    ),
                    "compile-possessive-quantifier-cold": (
                        "str-possessive-quantifier-success",
                    ),
                    "compile-atomic-group-purged": (
                        "str-atomic-group-success",
                    ),
                    "compile-parser-stress-cold": (
                        "str-parser-stress-compile-proxy-success",
                    ),
                },
            )
            | _definition_anchor_expectations(
                REGRESSION_MATRIX_MANIFEST_PATH,
                {
                    "regression-parser-atomic-lookbehind-cold": (
                        "str-parser-stress-compile-proxy-success",
                    ),
                    "regression-parser-bytes-backreference-purged": (
                        "bytes-named-backreference-compile-proxy-success",
                    ),
                    "regression-module-compile-verbose-purged": (
                        "workflow-compile-str-verbose-regression",
                    ),
                    "regression-module-compile-multiline-purged": (
                        "workflow-compile-str-multiline-regression",
                    ),
                    "regression-module-compile-multiline-purged-bytes": (
                        "workflow-compile-bytes-multiline-regression",
                    ),
                    "regression-module-compile-verbose-purged-bytes": (
                        "workflow-compile-bytes-verbose-regression",
                    ),
                },
            )
        ),
        include_workload=_is_compile_proxy_workload,
        correctness_case_signature=_compile_proxy_correctness_case_signature,
        workload_signature=_compile_proxy_workload_signature,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="collection-replacement-module-positional-indexlike",
        manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            COLLECTION_REPLACEMENT_MANIFEST_PATH,
            {
                "module-split-maxsplit-indexlike-positional-purged-bytes": (
                    "workflow-module-split-maxsplit-indexlike-positional-bytes",
                ),
                "module-sub-count-indexlike-positional-warm-str": (
                    "workflow-module-sub-count-indexlike-positional-str",
                ),
                "module-subn-count-indexlike-positional-purged-bytes": (
                    "workflow-module-subn-count-indexlike-positional-bytes",
                ),
                "pattern-split-maxsplit-indexlike-positional-warm-str": (
                    "workflow-pattern-split-str-maxsplit-indexlike-positional",
                ),
                "pattern-sub-count-indexlike-positional-purged-bytes": (
                    "workflow-pattern-sub-count-indexlike-positional-bytes",
                ),
                "pattern-subn-count-indexlike-positional-warm-str": (
                    "workflow-pattern-subn-count-indexlike-positional-str",
                ),
            },
        ),
        include_workload=_is_collection_replacement_positional_indexlike_workload,
        correctness_case_signature=(
            _module_workflow_positional_indexlike_correctness_case_signature
        ),
        workload_signature=_collection_replacement_positional_indexlike_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="collection-replacement-keyword",
        manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            COLLECTION_REPLACEMENT_MANIFEST_PATH,
            {
                "module-split-maxsplit-keyword-purged-bytes": (
                    "workflow-module-split-maxsplit-keyword-bytes",
                ),
                "module-split-maxsplit-bool-keyword-purged-bytes": (
                    "workflow-module-split-maxsplit-bool-false-bytes",
                ),
                "module-split-maxsplit-indexlike-keyword-purged-bytes": (
                    "workflow-module-split-maxsplit-indexlike-bytes",
                ),
                "module-split-maxsplit-keyword-purged-str-compiled-pattern": (
                    "workflow-module-split-maxsplit-keyword-str-compiled-pattern",
                ),
                "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern": (
                    "workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern",
                ),
                "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern": (
                    "workflow-module-split-maxsplit-bool-false-bytes-compiled-pattern",
                ),
                "module-split-duplicate-maxsplit-keyword-purged-str": (
                    "workflow-module-split-duplicate-maxsplit-keyword",
                ),
                "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern": (
                    "workflow-module-split-duplicate-maxsplit-keyword-str-compiled-pattern",
                ),
                "module-split-unexpected-keyword-purged-bytes-compiled-pattern": (
                    "workflow-module-split-unexpected-keyword-bytes-compiled-pattern",
                ),
                "module-sub-count-keyword-warm-str": (
                    "workflow-module-sub-count-keyword-str",
                ),
                "module-sub-count-bool-keyword-warm-str": (
                    "workflow-module-sub-count-bool-true-str",
                ),
                "module-sub-count-bool-false-keyword-warm-str": (
                    "workflow-module-sub-count-bool-false-str",
                ),
                "module-sub-count-indexlike-keyword-warm-str": (
                    "workflow-module-sub-count-indexlike-str",
                ),
                "module-sub-count-keyword-warm-str-compiled-pattern": (
                    "workflow-module-sub-count-keyword-str-compiled-pattern",
                ),
                "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern": (
                    "workflow-module-sub-count-indexlike-bytes-compiled-pattern",
                ),
                "module-sub-count-bool-keyword-warm-str-compiled-pattern": (
                    "workflow-module-sub-count-bool-true-str-compiled-pattern",
                ),
                "module-sub-count-bool-false-keyword-warm-str-compiled-pattern": (
                    "workflow-module-sub-count-bool-false-str-compiled-pattern",
                ),
                "module-sub-duplicate-count-keyword-warm-str": (
                    "workflow-module-sub-duplicate-count-keyword",
                ),
                "module-sub-unexpected-keyword-purged-str": (
                    "workflow-module-sub-unexpected-keyword",
                ),
                "module-sub-duplicate-count-keyword-warm-str-compiled-pattern": (
                    "workflow-module-sub-duplicate-count-keyword-str-compiled-pattern",
                ),
                "module-sub-unexpected-keyword-purged-str-compiled-pattern": (
                    "workflow-module-sub-unexpected-keyword-str-compiled-pattern",
                ),
                "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern": (
                    "workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern",
                ),
                "module-subn-count-keyword-purged-bytes": (
                    "workflow-module-subn-count-keyword-bytes",
                ),
                "module-subn-count-bool-keyword-purged-bytes": (
                    "workflow-module-subn-count-bool-false-bytes",
                ),
                "module-subn-count-bool-true-keyword-purged-bytes": (
                    "workflow-module-subn-count-bool-true-bytes",
                ),
                "module-subn-count-indexlike-keyword-purged-bytes": (
                    "workflow-module-subn-count-indexlike-bytes",
                ),
                "module-subn-count-keyword-purged-bytes-compiled-pattern": (
                    "workflow-module-subn-count-keyword-bytes-compiled-pattern",
                ),
                "module-subn-count-indexlike-keyword-purged-str-compiled-pattern": (
                    "workflow-module-subn-count-indexlike-str-compiled-pattern",
                ),
                "module-subn-count-bool-keyword-purged-bytes-compiled-pattern": (
                    "workflow-module-subn-count-bool-false-bytes-compiled-pattern",
                ),
                "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern": (
                    "workflow-module-subn-count-bool-true-bytes-compiled-pattern",
                ),
                "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern": (
                    "workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern",
                ),
                "module-subn-unexpected-keyword-purged-bytes-compiled-pattern": (
                    "workflow-module-subn-unexpected-keyword-bytes-compiled-pattern",
                ),
                "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern": (
                    "workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern",
                ),
                "pattern-split-maxsplit-keyword-warm-str": (
                    "workflow-pattern-split-str-maxsplit-keyword",
                ),
                "pattern-split-maxsplit-bool-keyword-warm-str": (
                    "workflow-pattern-split-str-maxsplit-bool-true",
                ),
                "pattern-split-maxsplit-indexlike-keyword-warm-str": (
                    "workflow-pattern-split-str-maxsplit-indexlike",
                ),
                "pattern-split-duplicate-maxsplit-keyword-warm-str": (
                    "workflow-pattern-split-duplicate-maxsplit-keyword-str",
                ),
                "pattern-split-unexpected-keyword-warm-bytes": (
                    "workflow-pattern-split-unexpected-keyword-bytes",
                ),
                "pattern-sub-count-keyword-purged-bytes": (
                    "workflow-pattern-sub-count-keyword-bytes",
                ),
                "pattern-sub-count-bool-keyword-purged-bytes": (
                    "workflow-pattern-sub-count-bool-false-bytes",
                ),
                "pattern-sub-count-bool-true-keyword-purged-bytes": (
                    "workflow-pattern-sub-count-bool-true-bytes",
                ),
                "pattern-sub-count-indexlike-keyword-purged-bytes": (
                    "workflow-pattern-sub-count-indexlike-bytes",
                ),
                "pattern-sub-duplicate-count-keyword-warm-str": (
                    "workflow-pattern-sub-duplicate-count-keyword-str",
                ),
                "pattern-sub-unexpected-keyword-warm-str": (
                    "workflow-pattern-sub-unexpected-keyword-str",
                ),
                "pattern-sub-unexpected-keyword-after-positional-count-warm-str": (
                    "workflow-pattern-sub-unexpected-keyword-after-positional-count-str",
                ),
                "pattern-subn-count-keyword-warm-str": (
                    "workflow-pattern-subn-count-keyword-str",
                ),
                "pattern-subn-count-bool-keyword-warm-str": (
                    "workflow-pattern-subn-count-bool-true-str",
                ),
                "pattern-subn-count-bool-false-keyword-warm-str": (
                    "workflow-pattern-subn-count-bool-false-str",
                ),
                "pattern-subn-count-indexlike-keyword-warm-str": (
                    "workflow-pattern-subn-count-indexlike-str",
                ),
                "pattern-subn-duplicate-count-keyword-warm-bytes": (
                    "workflow-pattern-subn-duplicate-count-keyword-bytes",
                ),
                "pattern-subn-unexpected-keyword-warm-bytes": (
                    "workflow-pattern-subn-unexpected-keyword-bytes",
                ),
                "pattern-subn-unexpected-keyword-after-positional-count-warm-bytes": (
                    "workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes",
                ),
            },
        ),
        include_workload=_is_collection_replacement_keyword_workload,
        correctness_case_signature=(
            _collection_replacement_keyword_correctness_case_signature
        ),
        workload_signature=_collection_replacement_keyword_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="collection-replacement-compiled-pattern-literal-success",
        manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            COLLECTION_REPLACEMENT_MANIFEST_PATH,
            {
                "module-split-literal-warm-str-compiled-pattern": (
                    "workflow-module-split-str-compiled-pattern",
                ),
                "module-findall-literal-purged-bytes-compiled-pattern": (
                    "workflow-module-findall-bytes-compiled-pattern",
                ),
                "module-finditer-literal-warm-str-compiled-pattern": (
                    "workflow-module-finditer-str-compiled-pattern",
                ),
                "module-sub-literal-warm-str-compiled-pattern": (
                    "workflow-module-sub-str-compiled-pattern",
                ),
                "module-subn-literal-purged-bytes-compiled-pattern": (
                    "workflow-module-subn-bytes-compiled-pattern",
                ),
            },
        ),
        include_workload=_is_collection_replacement_compiled_pattern_success_workload,
        correctness_case_signature=(
            _collection_replacement_compiled_pattern_success_correctness_case_signature
        ),
        workload_signature=(
            _collection_replacement_compiled_pattern_success_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="collection-replacement-compiled-pattern-wrong-text-model",
        manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            COLLECTION_REPLACEMENT_MANIFEST_PATH,
            {
                "module-split-on-bytes-string-purged-str-compiled-pattern": (
                    "workflow-module-split-str-compiled-pattern-on-bytes-string",
                ),
                "module-findall-on-str-string-purged-bytes-compiled-pattern": (
                    "workflow-module-findall-bytes-compiled-pattern-on-str-string",
                ),
                "module-finditer-on-bytes-string-warm-str-compiled-pattern": (
                    "workflow-module-finditer-str-compiled-pattern-on-bytes-string",
                ),
                "module-sub-on-bytes-string-warm-str-compiled-pattern": (
                    "workflow-module-sub-str-compiled-pattern-on-bytes-string",
                ),
                "module-subn-on-str-string-purged-bytes-compiled-pattern": (
                    "workflow-module-subn-bytes-compiled-pattern-on-str-string",
                ),
            },
        ),
        include_workload=_is_collection_replacement_wrong_text_model_workload,
        correctness_case_signature=(
            _collection_replacement_wrong_text_model_correctness_case_signature
        ),
        workload_signature=_collection_replacement_wrong_text_model_workload_signature,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="pattern-helper-collection-replacement-wrong-text-model",
        manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            COLLECTION_REPLACEMENT_MANIFEST_PATH,
            {
                "pattern-split-on-bytes-string-warm-str": (
                    "workflow-pattern-split-str-pattern-on-bytes-string",
                ),
                "pattern-sub-on-bytes-string-warm-str": (
                    "workflow-pattern-sub-str-pattern-on-bytes-string",
                ),
                "pattern-subn-on-str-string-purged-bytes": (
                    "workflow-pattern-subn-bytes-pattern-on-str-string",
                ),
            },
        ),
        include_workload=_is_collection_replacement_pattern_wrong_text_model_workload,
        correctness_case_signature=(
            _collection_replacement_pattern_wrong_text_model_correctness_case_signature
        ),
        workload_signature=(
            _collection_replacement_pattern_wrong_text_model_workload_signature
        ),
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-keyword-flags",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-flags-keyword-warm-str": (
                    "workflow-module-search-flags-keyword-str",
                ),
                "module-match-flags-keyword-purged-bytes": (
                    "workflow-module-match-flags-keyword-bytes",
                ),
                "module-fullmatch-flags-keyword-warm-str": (
                    "workflow-module-fullmatch-flags-keyword-str",
                ),
            },
        ),
        include_workload=_is_module_workflow_keyword_flags_workload,
        correctness_case_signature=_module_workflow_keyword_correctness_case_signature,
        workload_signature=_module_workflow_keyword_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-keyword-errors",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-duplicate-flags-keyword-warm-str": (
                    "workflow-module-search-duplicate-flags-keyword",
                ),
                "module-fullmatch-unexpected-keyword-purged-str": (
                    "workflow-module-fullmatch-unexpected-keyword",
                ),
            },
        ),
        include_workload=_is_module_workflow_keyword_error_workload,
        correctness_case_signature=_module_workflow_keyword_correctness_case_signature,
        workload_signature=_module_workflow_keyword_workload_signature,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-module-compile-literal-success",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-compile-literal-warm-str-compiled-pattern": (
                    "workflow-module-compile-str-compiled-pattern",
                ),
                "module-compile-literal-purged-bytes-compiled-pattern": (
                    "workflow-module-compile-bytes-compiled-pattern",
                ),
            },
        ),
        include_workload=(
            _is_module_workflow_compiled_pattern_compile_literal_success_workload
        ),
        correctness_case_signature=(
            _module_workflow_compiled_pattern_compile_correctness_case_signature
        ),
        workload_signature=(
            _module_workflow_compiled_pattern_compile_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-module-compile-named-group-success",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-compile-named-group-warm-str-compiled-pattern": (
                    "workflow-module-compile-str-compiled-pattern-named-group",
                ),
                "module-compile-named-group-purged-bytes-compiled-pattern": (
                    "workflow-module-compile-bytes-compiled-pattern-named-group",
                ),
            },
        ),
        include_workload=(
            _is_module_workflow_compiled_pattern_compile_named_group_success_workload
        ),
        correctness_case_signature=(
            _module_workflow_compiled_pattern_compile_correctness_case_signature
        ),
        workload_signature=(
            _module_workflow_compiled_pattern_compile_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-compile-flags-int-zero-warm-str-compiled-pattern": (
                    "workflow-module-compile-flags-int-zero-str-compiled-pattern",
                ),
                "module-compile-flags-int-zero-purged-bytes-compiled-pattern": (
                    "workflow-module-compile-flags-int-zero-bytes-compiled-pattern",
                ),
            },
        ),
        include_workload=(
            _is_module_workflow_compiled_pattern_compile_int_zero_keyword_workload
        ),
        correctness_case_signature=(
            _module_workflow_compiled_pattern_compile_int_zero_keyword_correctness_case_signature
        ),
        workload_signature=(
            _module_workflow_compiled_pattern_compile_int_zero_keyword_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword-named-group",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group": (
                    "workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group",
                ),
                "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group": (
                    "workflow-module-compile-flags-int-zero-bytes-compiled-pattern-named-group",
                ),
            },
        ),
        include_workload=(
            _is_module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_workload
        ),
        correctness_case_signature=(
            _module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_correctness_case_signature
        ),
        workload_signature=(
            _module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-compile-flags-bool-false-warm-str-compiled-pattern": (
                    "workflow-module-compile-flags-bool-false-str-compiled-pattern",
                ),
                "module-compile-flags-bool-false-purged-bytes-compiled-pattern": (
                    "workflow-module-compile-flags-bool-false-bytes-compiled-pattern",
                ),
            },
        ),
        include_workload=(
            _is_module_workflow_compiled_pattern_compile_bool_false_keyword_workload
        ),
        correctness_case_signature=(
            _module_workflow_compiled_pattern_compile_bool_false_keyword_correctness_case_signature
        ),
        workload_signature=(
            _module_workflow_compiled_pattern_compile_bool_false_keyword_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name=(
            "module-workflow-compiled-pattern-module-compile-flags-bool-false-"
            "keyword-named-group"
        ),
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group": (
                    "workflow-module-compile-flags-bool-false-str-compiled-pattern-named-group",
                ),
                "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group": (
                    "workflow-module-compile-flags-bool-false-bytes-compiled-pattern-named-group",
                ),
            },
        ),
        include_workload=(
            _is_module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_workload
        ),
        correctness_case_signature=(
            _module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_correctness_case_signature
        ),
        workload_signature=(
            _module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name=(
            "module-workflow-compiled-pattern-module-compile-flags-ignorecase-"
            "keyword-rejection"
        ),
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-compile-flags-ignorecase-warm-str-compiled-pattern": (
                    "workflow-module-compile-flags-ignorecase-str-compiled-pattern",
                ),
                "module-compile-flags-ignorecase-purged-bytes-compiled-pattern": (
                    "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern",
                ),
            },
        ),
        include_workload=(
            _is_module_workflow_compiled_pattern_compile_ignorecase_keyword_workload
        ),
        correctness_case_signature=(
            _module_workflow_compiled_pattern_compile_ignorecase_keyword_correctness_case_signature
        ),
        workload_signature=(
            _module_workflow_compiled_pattern_compile_ignorecase_keyword_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name=(
            "module-workflow-compiled-pattern-module-compile-flags-ignorecase-"
            "keyword-rejection-named-group"
        ),
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group": (
                    "workflow-module-compile-flags-ignorecase-str-compiled-pattern-named-group",
                ),
                "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group": (
                    "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group",
                ),
            },
        ),
        include_workload=(
            _is_module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_workload
        ),
        correctness_case_signature=(
            _module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_correctness_case_signature
        ),
        workload_signature=(
            _module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-literal-success",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-literal-warm-hit-str-compiled-pattern": (
                    "workflow-module-search-str-compiled-pattern",
                ),
                "module-match-literal-warm-hit-str-compiled-pattern": (
                    "workflow-module-match-str-compiled-pattern",
                ),
                "module-fullmatch-literal-purged-hit-bytes-compiled-pattern": (
                    "workflow-module-fullmatch-bytes-compiled-pattern",
                ),
            },
        ),
        include_workload=_is_module_workflow_compiled_pattern_literal_success_workload,
        correctness_case_signature=_module_workflow_compiled_pattern_correctness_case_signature,
        workload_signature=_module_workflow_compiled_pattern_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-bounded-wildcard-success",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern": (
                    "workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern",
                ),
                "module-match-bounded-wildcard-warm-hit-str-compiled-pattern": (
                    "workflow-module-match-str-bounded-wildcard-compiled-pattern",
                ),
                "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern": (
                    "workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern",
                ),
            },
        ),
        include_workload=_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
        correctness_case_signature=_module_workflow_compiled_pattern_correctness_case_signature,
        workload_signature=_module_workflow_compiled_pattern_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-verbose-bytes-success",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-verbose-regression-warm-hit-bytes-compiled-pattern": (
                    "workflow-module-search-bytes-verbose-regression-compiled-pattern",
                ),
                "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern": (
                    "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
                ),
            },
        ),
        include_workload=_is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
        correctness_case_signature=_module_workflow_compiled_pattern_correctness_case_signature,
        workload_signature=_module_workflow_compiled_pattern_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-wrong-text-model",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-on-bytes-string-warm-str-compiled-pattern": (
                    "workflow-module-search-str-compiled-pattern-on-bytes-string",
                ),
                "module-match-on-str-string-purged-bytes-compiled-pattern": (
                    "workflow-module-match-bytes-compiled-pattern-on-str-string",
                ),
                "module-fullmatch-on-bytes-string-warm-str-compiled-pattern": (
                    "workflow-module-fullmatch-str-compiled-pattern-on-bytes-string",
                ),
            },
        ),
        include_workload=_is_module_workflow_compiled_pattern_wrong_text_model_workload,
        correctness_case_signature=_module_workflow_compiled_pattern_correctness_case_signature,
        workload_signature=_module_workflow_compiled_pattern_workload_signature,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="pattern-window-positional-indexlike",
        manifest_paths=(PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-pos-indexlike-positional-warm-str": (
                    "workflow-pattern-search-str-pos-indexlike-positional",
                ),
                "pattern-search-endpos-indexlike-positional-purged-bytes": (
                    "workflow-pattern-search-bytes-endpos-indexlike-positional",
                ),
                "pattern-match-window-indexlike-positional-purged-bytes": (
                    "workflow-pattern-match-bytes-window-indexlike-positional",
                ),
                "pattern-fullmatch-window-indexlike-positional-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-window-indexlike-positional",
                ),
                "pattern-findall-window-indexlike-positional-warm-str": (
                    "workflow-pattern-findall-str-window-indexlike-positional",
                ),
                "pattern-finditer-window-indexlike-positional-purged-bytes": (
                    "workflow-pattern-finditer-bytes-window-indexlike-positional",
                ),
            },
        ),
        include_workload=_is_pattern_window_positional_indexlike_workload,
        correctness_case_signature=(
            _pattern_window_positional_indexlike_correctness_case_signature
        ),
        workload_signature=_pattern_window_positional_indexlike_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="pattern-window-keyword",
        manifest_paths=(PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-pos-keyword-warm-str": (
                    "workflow-pattern-search-str-pos-keyword",
                ),
                "pattern-match-pos-keyword-purged-str": (
                    "workflow-pattern-match-str-pos-keyword",
                ),
                "pattern-match-window-indexlike-purged-bytes": (
                    "workflow-pattern-match-bytes-window-indexlike",
                ),
                "pattern-fullmatch-window-keyword-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-window-keyword",
                ),
                "pattern-findall-bool-window-keyword-warm-str": (
                    "workflow-pattern-findall-str-bool-window-keyword",
                ),
                "pattern-finditer-window-indexlike-purged-bytes": (
                    "workflow-pattern-finditer-bytes-window-indexlike",
                ),
            },
        ),
        include_workload=_is_pattern_keyword_window_workload,
        correctness_case_signature=_pattern_keyword_window_correctness_case_signature,
        workload_signature=_pattern_keyword_window_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="optional-group-conditional",
        manifest_paths=(OPTIONAL_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            OPTIONAL_GROUP_MANIFEST_PATH,
            {
                OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID: (
                    "optional-group-conditional-module-search-present-str",
                ),
            },
        ),
        include_workload=_is_optional_group_conditional_workload,
        correctness_case_signature=_optional_group_correctness_case_signature,
        workload_signature=_optional_group_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="nested-group",
        manifest_paths=(NESTED_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            NESTED_GROUP_MANIFEST_PATH,
            {
                "module-compile-nested-group-cold-str": (
                    "nested-group-compile-metadata-str",
                ),
                "module-search-nested-group-warm-str": (
                    "nested-group-module-search-str",
                ),
                "pattern-fullmatch-nested-group-purged-str": (
                    "nested-group-pattern-fullmatch-str",
                ),
                "module-compile-named-nested-group-warm-str": (
                    "named-nested-group-compile-metadata-str",
                ),
                "module-search-named-nested-group-warm-str": (
                    "named-nested-group-module-search-str",
                ),
                "pattern-fullmatch-named-nested-group-purged-str": (
                    "named-nested-group-pattern-fullmatch-str",
                ),
            },
        ),
        include_workload=_include_all_workloads,
        correctness_case_signature=_nested_group_correctness_case_signature,
        workload_signature=_nested_group_workload_signature,
        run_callback_result_parity=True,
        expected_excluded_workload_ids=frozenset(
            {
                "module-search-triple-nested-group-cold-gap",
                "pattern-fullmatch-named-quantified-nested-group-purged-gap",
            }
        ),
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="exact-repeat",
        manifest_paths=(EXACT_REPEAT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            EXACT_REPEAT_MANIFEST_PATH,
            {
                "module-compile-numbered-exact-repeat-group-cold-str": (
                    "exact-repeat-numbered-group-compile-metadata-str",
                ),
                "module-search-numbered-exact-repeat-group-warm-str": (
                    "exact-repeat-numbered-group-module-search-str",
                ),
                "pattern-fullmatch-numbered-exact-repeat-group-purged-str": (
                    "exact-repeat-numbered-group-pattern-fullmatch-str",
                ),
                "module-compile-named-exact-repeat-group-warm-str": (
                    "exact-repeat-named-group-compile-metadata-str",
                ),
                "module-search-named-exact-repeat-group-warm-str": (
                    "exact-repeat-named-group-module-search-str",
                ),
                "pattern-fullmatch-named-exact-repeat-group-purged-str": (
                    "exact-repeat-named-group-pattern-fullmatch-str",
                ),
                "module-search-numbered-broader-ranged-repeat-group-cold-gap": (
                    "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
                ),
            },
        ),
        include_workload=_is_non_alternation_counted_repeat_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="ranged-repeat",
        manifest_paths=(RANGED_REPEAT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            RANGED_REPEAT_MANIFEST_PATH,
            {
                "module-compile-numbered-ranged-repeat-group-cold-str": (
                    "ranged-repeat-numbered-group-compile-metadata-str",
                ),
                "module-search-numbered-ranged-repeat-group-lower-bound-warm-str": (
                    "ranged-repeat-numbered-group-module-search-lower-bound-str",
                ),
                "pattern-fullmatch-numbered-ranged-repeat-group-upper-bound-purged-str": (
                    "ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",
                ),
                "module-compile-named-ranged-repeat-group-warm-str": (
                    "ranged-repeat-named-group-compile-metadata-str",
                ),
                "module-search-named-ranged-repeat-group-upper-bound-warm-str": (
                    "ranged-repeat-named-group-module-search-upper-bound-str",
                ),
                "pattern-fullmatch-named-ranged-repeat-group-lower-bound-purged-str": (
                    "ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
                ),
                "module-search-numbered-ranged-repeat-group-wider-range-cold-gap": (
                    "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
                ),
            },
        ),
        include_workload=_is_non_alternation_counted_repeat_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="grouped-alternation",
        manifest_paths=(GROUPED_ALTERNATION_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            GROUPED_ALTERNATION_MANIFEST_PATH,
            {
                "module-compile-grouped-alternation-cold-str": (
                    "grouped-alternation-compile-metadata-str",
                ),
                "module-search-grouped-alternation-warm-str": (
                    "grouped-alternation-module-search-str",
                ),
                "pattern-fullmatch-grouped-alternation-purged-str": (
                    "grouped-alternation-pattern-fullmatch-str",
                ),
                "module-compile-named-grouped-alternation-warm-str": (
                    "named-grouped-alternation-compile-metadata-str",
                ),
                "module-search-named-grouped-alternation-warm-str": (
                    "named-grouped-alternation-module-search-str",
                ),
                "pattern-fullmatch-named-grouped-alternation-purged-str": (
                    "named-grouped-alternation-pattern-fullmatch-str",
                ),
                "module-sub-template-nested-grouped-alternation-warm-gap": (
                    "module-sub-template-nested-group-alternation-numbered-wrapper-str",
                ),
                "pattern-subn-template-named-nested-grouped-alternation-purged-gap": (
                    "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
                ),
            },
        ),
        include_workload=_include_all_workloads,
        correctness_case_signature=_grouped_alternation_correctness_case_signature,
        workload_signature=_grouped_alternation_workload_signature,
        run_callback_result_parity=True,
        expected_legacy_workload_ids=frozenset(
            {
                "module-sub-template-nested-grouped-alternation-warm-gap",
                "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
            }
        ),
        callback_anchor_workload_ids=frozenset(
            {
                "module-sub-template-nested-grouped-alternation-warm-gap",
                "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
            }
        ),
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="grouped-alternation-replacement",
        manifest_paths=(GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
            {
                "module-sub-template-grouped-alternation-warm-str": (
                    "module-sub-template-grouped-alternation-str",
                ),
                "module-subn-template-grouped-alternation-warm-str": (
                    "module-subn-template-grouped-alternation-str",
                ),
                "pattern-sub-template-grouped-alternation-purged-str": (
                    "pattern-sub-template-grouped-alternation-str",
                ),
                "pattern-subn-template-grouped-alternation-purged-str": (
                    "pattern-subn-template-grouped-alternation-str",
                ),
                "module-sub-template-named-grouped-alternation-warm-str": (
                    "module-sub-template-named-grouped-alternation-str",
                ),
                "module-subn-template-named-grouped-alternation-warm-str": (
                    "module-subn-template-named-grouped-alternation-str",
                ),
                "pattern-sub-template-named-grouped-alternation-purged-str": (
                    "pattern-sub-template-named-grouped-alternation-str",
                ),
                "pattern-subn-template-named-grouped-alternation-purged-str": (
                    "pattern-subn-template-named-grouped-alternation-str",
                ),
                "module-sub-template-nested-grouped-alternation-cold-gap": (
                    "module-sub-template-nested-group-alternation-numbered-outer-str",
                ),
                "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap": (
                    "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
                ),
            },
        ),
        include_workload=_include_all_workloads,
        correctness_case_signature=(
            _grouped_alternation_replacement_correctness_case_signature
        ),
        workload_signature=_grouped_alternation_replacement_workload_signature,
        run_callback_result_parity=True,
        expected_legacy_workload_ids=frozenset(
            {
                "module-sub-template-nested-grouped-alternation-cold-gap",
                "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
            }
        ),
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="nested-group-replacement",
        manifest_paths=(NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,
            {
                "module-sub-template-nested-group-numbered-warm-str": (
                    "module-sub-template-nested-group-numbered-str",
                ),
                "module-subn-template-nested-group-numbered-warm-str": (
                    "module-subn-template-nested-group-numbered-str",
                ),
                "pattern-sub-template-nested-group-numbered-purged-str": (
                    "pattern-sub-template-nested-group-numbered-str",
                ),
                "pattern-subn-template-nested-group-numbered-purged-str": (
                    "pattern-subn-template-nested-group-numbered-str",
                ),
                "module-sub-template-nested-group-named-warm-str": (
                    "module-sub-template-nested-group-named-str",
                ),
                "module-subn-template-nested-group-named-warm-str": (
                    "module-subn-template-nested-group-named-str",
                ),
                "pattern-sub-template-nested-group-named-purged-str": (
                    "pattern-sub-template-nested-group-named-str",
                ),
                "pattern-subn-template-nested-group-named-purged-str": (
                    "pattern-subn-template-nested-group-named-str",
                ),
                "module-sub-template-numbered-quantified-nested-group-replacement-lower-bound-warm-str": (
                    "module-sub-template-quantified-nested-group-numbered-lower-bound-str",
                ),
                "module-subn-template-numbered-quantified-nested-group-replacement-first-match-only-warm-str": (
                    "module-subn-template-quantified-nested-group-numbered-first-match-only-str",
                ),
                "pattern-sub-template-named-quantified-nested-group-replacement-repeated-outer-purged-str": (
                    "pattern-sub-template-quantified-nested-group-named-repeated-outer-capture-str",
                ),
                "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap": (
                    "pattern-subn-template-quantified-nested-group-named-first-match-only-str",
                ),
                "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str": (
                    "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                ),
                "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str": (
                    "module-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                ),
                "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str": (
                    "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-str",
                ),
                "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str": (
                    "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                ),
                "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str": (
                    "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                ),
                "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str": (
                    "module-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                ),
                "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str": (
                    "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                ),
                "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str": (
                    "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                ),
                "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str": (
                    "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                ),
                "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str": (
                    "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                ),
                "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str": (
                    "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                ),
                "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str": (
                    "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                ),
                "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str": (
                    "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
                ),
                "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str": (
                    "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
                ),
                "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str": (
                    "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-str",
                ),
                "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str": (
                    "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
                ),
            },
        ),
        include_workload=_include_all_workloads,
        correctness_case_signature=(
            _grouped_alternation_replacement_correctness_case_signature
        ),
        workload_signature=_grouped_alternation_replacement_workload_signature,
        run_callback_result_parity=True,
        expected_special_unanchored_workload_ids=(
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
        ),
        run_special_unanchored_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="open-ended-grouped-alternation",
        manifest_paths=(OPEN_ENDED_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            OPEN_ENDED_MANIFEST_PATH,
            {
                "module-compile-numbered-open-ended-group-alternation-cold-str": (
                    "open-ended-quantified-group-alternation-numbered-compile-metadata-str",
                ),
                "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-str": (
                    "open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
                ),
                "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-str": (
                    "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
                ),
                "module-compile-named-open-ended-group-alternation-warm-str": (
                    "open-ended-quantified-group-alternation-named-compile-metadata-str",
                ),
                "module-search-named-open-ended-group-alternation-lower-bound-de-warm-str": (
                    "open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",
                ),
                "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-str": (
                    "open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",
                ),
                "module-compile-numbered-open-ended-group-alternation-cold-bytes": (
                    "open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",
                ),
                "module-compile-named-open-ended-group-alternation-warm-bytes": (
                    "open-ended-quantified-group-alternation-named-compile-metadata-bytes",
                ),
                "module-compile-numbered-open-ended-group-conditional-cold-str": (
                    "open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",
                ),
                "module-compile-numbered-open-ended-group-broader-range-cold-str": (
                    "broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-str",
                ),
                "module-search-numbered-open-ended-group-broader-range-cold-gap": (
                    "broader-range-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
                ),
                "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-str": (
                    "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
                ),
                "module-compile-named-open-ended-group-broader-range-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-named-compile-metadata-str",
                ),
                "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",
                ),
                "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-str": (
                    "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",
                ),
                "module-compile-numbered-open-ended-group-broader-range-cold-bytes": (
                    "broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",
                ),
                "module-compile-named-open-ended-group-broader-range-warm-bytes": (
                    "broader-range-open-ended-quantified-group-alternation-named-compile-metadata-bytes",
                ),
                "module-compile-numbered-open-ended-group-broader-range-conditional-cold-str": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",
                ),
                "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
                ),
                "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
                ),
                "module-compile-named-open-ended-group-broader-range-conditional-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",
                ),
                "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
                ),
                "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
                ),
                "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",
                ),
                "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",
                ),
                "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-str": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
                ),
                "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
                ),
                "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-str": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
                ),
                "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
                ),
                "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-str",
                ),
                "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
                ),
                "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",
                ),
                "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-str": (
                    "open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
                ),
                "module-compile-named-open-ended-group-conditional-warm-str": (
                    "open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",
                ),
                "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-str": (
                    "open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
                ),
                "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-str": (
                    "open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
                ),
                "module-compile-numbered-open-ended-group-conditional-cold-bytes": (
                    "open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",
                ),
                "module-compile-named-open-ended-group-conditional-warm-bytes": (
                    "open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",
                ),
                "module-compile-numbered-open-ended-group-backtracking-heavy-cold-str": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
                ),
                "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-str": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
                ),
                "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-str": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
                ),
                "module-compile-named-open-ended-group-backtracking-heavy-warm-str": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
                ),
                "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-str": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-str",
                ),
                "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-gap": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-fourth-repetition-short-only-str",
                ),
                "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
                ),
                "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",
                ),
            },
        ),
        include_workload=_include_all_workloads,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
        expected_special_unanchored_workload_ids=(
            "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
            "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
            "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
            "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
            "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
            "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
            "module-search-numbered-open-ended-group-conditional-warm-gap",
            "module-search-numbered-open-ended-group-conditional-second-repetition-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
            "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
            "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
        ),
        direct_parity_supplemental_cases=(
            *OPEN_ENDED_ALTERNATION_BYTES_CASES,
            *OPEN_ENDED_CONDITIONAL_BYTES_CASES,
            *OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
            *BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
            *BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
            *BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
        ),
        run_special_unanchored_result_parity=True,
    ),
)

def _has_standard_benchmark_legacy_workloads(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> bool:
    return bool(definition.expected_legacy_workload_ids)


def _runs_standard_benchmark_callback_result_parity(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> bool:
    return definition.run_callback_result_parity


def _has_standard_benchmark_special_unanchored_workloads(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> bool:
    return bool(definition.expected_special_unanchored_workload_ids)


def _has_standard_benchmark_special_unanchored_direct_parity_cases(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> bool:
    return bool(
        definition.expected_special_unanchored_workload_ids
        and definition.direct_parity_supplemental_cases
    )


def _standard_benchmark_manifest_params() -> tuple[Any, ...]:
    return tuple(
        pytest.param(
            definition,
            manifest_path,
            id=f"{definition.name}:{manifest_path.name}",
        )
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        for manifest_path in definition.manifest_paths
    )


def _standard_benchmark_definition_params(
    *,
    include_definition: Callable[[StandardBenchmarkAnchorContractDefinition], bool],
) -> tuple[Any, ...]:
    return tuple(
        pytest.param(definition, id=definition.name)
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        if include_definition(definition)
    )


def _standard_benchmark_special_unanchored_result_parity_params() -> tuple[Any, ...]:
    return tuple(
        pytest.param(
            definition,
            workload_id,
            id=f"{definition.name}:{workload_id}",
        )
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        if definition.run_special_unanchored_result_parity
        for workload_id in definition.expected_special_unanchored_workload_ids
    )


def _expected_workload_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return tuple(
        workload_id
        for (manifest_name, workload_id), _ in definition.expected_anchor_case_ids.items()
        if manifest_name == manifest_path.name
    )


def _expected_anchor_case_ids_for_manifest(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] | None = None,
) -> dict[tuple[str, str], tuple[str, ...]]:
    anchor_case_ids = (
        definition.expected_anchor_case_ids
        if expected_anchor_case_ids is None
        else expected_anchor_case_ids
    )
    return {
        (manifest_name, workload_id): case_ids
        for (manifest_name, workload_id), case_ids in anchor_case_ids.items()
        if manifest_name == manifest_path.name
    }


def _anchored_case_ids_for_manifest(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> dict[tuple[str, str], tuple[str, ...]]:
    return anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
        include_workload=definition.includes_workload,
    )


def _anchored_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[tuple[str, str], tuple[str, ...]]:
    anchored_case_ids: dict[tuple[str, str], tuple[str, ...]] = {}
    for manifest_path in definition.manifest_paths:
        anchored_case_ids.update(
            _anchored_case_ids_for_manifest(definition, manifest_path)
        )
    return anchored_case_ids


def _unanchored_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
        include_workload=definition.includes_workload,
    )


def _all_unanchored_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
    )


def _expected_callback_anchor_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[tuple[str, str], tuple[str, ...]]:
    if definition.callback_anchor_workload_ids:
        return _anchor_case_subset(
            definition.expected_anchor_case_ids,
            definition.callback_anchor_workload_ids,
        )
    return definition.expected_anchor_case_ids


def _expected_legacy_anchor_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[tuple[str, str], tuple[str, ...]]:
    return _anchor_case_subset(
        definition.expected_anchor_case_ids,
        definition.expected_legacy_workload_ids,
    )


def _expected_anchored_pairs(
    definition: StandardBenchmarkAnchorContractDefinition,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] | None = None,
) -> tuple[Any, ...]:
    anchored_pairs = []
    for manifest_path in definition.manifest_paths:
        manifest_anchor_case_ids = _expected_anchor_case_ids_for_manifest(
            definition,
            manifest_path,
            expected_anchor_case_ids=expected_anchor_case_ids,
        )
        if not manifest_anchor_case_ids:
            continue
        anchored_pairs.extend(
            expected_anchored_workload_case_pairs(
                manifest_path,
                expected_anchor_case_ids=manifest_anchor_case_ids,
                include_workload=definition.includes_workload,
            )
        )
    return tuple(anchored_pairs)


def test_default_benchmark_manifest_selector_rejects_unknown_selector() -> None:
    with pytest.raises(ValueError, match="unknown benchmark manifest selector"):
        select_benchmark_manifest_paths("missing-selector")


def test_default_benchmark_published_full_suite_selector_covers_tracked_manifests() -> None:
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )
    tracked_manifest_paths = _tracked_benchmark_manifest_paths()

    assert set(published_manifest_paths) == set(tracked_manifest_paths)
    assert len(published_manifest_paths) == len(set(published_manifest_paths))

    for path in published_manifest_paths:
        assert path.is_relative_to(BENCHMARK_WORKLOADS_ROOT)
        assert path.is_file()
        assert path.suffix == ".py"


@pytest.mark.parametrize(
    "selector",
    tuple(benchmarks._NONDEFAULT_BENCHMARK_MANIFEST_SELECTOR_REQUESTED_FILENAMES),
    ids=lambda selector: selector,
)
def test_shared_benchmark_manifest_selectors_resolve_published_subset_invariants(
    selector: str,
) -> None:
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )
    selected_paths = select_benchmark_manifest_paths(selector)
    selected_path_set = set(selected_paths)
    expected_ordered_subset = tuple(
        path for path in published_manifest_paths if path in selected_path_set
    )

    assert selected_paths
    assert len(selected_paths) == len(selected_path_set)
    assert selected_paths == expected_ordered_subset
    for path in selected_paths:
        assert path.is_relative_to(BENCHMARK_WORKLOADS_ROOT)
        assert path.is_file()
        assert path.suffix == ".py"
        assert path in published_manifest_paths


def test_built_native_smoke_manifest_selector_keeps_membership_contract() -> None:
    selector = benchmarks.BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR
    expected_filenames = (
        benchmarks._NONDEFAULT_BENCHMARK_MANIFEST_SELECTOR_REQUESTED_FILENAMES[
            selector
        ]
    )
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )
    published_ordered_subset = tuple(
        path.name for path in published_manifest_paths if path.name in set(expected_filenames)
    )

    assert published_ordered_subset == expected_filenames
    assert benchmarks._BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR[selector] == expected_filenames
    assert tuple(path.name for path in select_benchmark_manifest_paths(selector)) == (
        expected_filenames
    )


def test_benchmark_selector_subset_helper_keeps_benchmark_specific_missing_filename_error() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape(
            "unknown published benchmark manifest filename(s): ['missing_boundary.py']"
        ),
    ):
        ordered_published_subset_filenames(
            benchmarks._BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR[
                PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
            ],
            ("missing_boundary.py",),
            missing_filename_error_prefix=(
                benchmarks._PUBLISHED_BENCHMARK_MANIFEST_MISSING_ERROR_PREFIX
            ),
        )


def test_declared_benchmark_manifest_selectors_match_registry_keys() -> None:
    declared_selectors = declared_string_constants_by_suffix(
        benchmarks,
        name_suffix="_MANIFEST_SELECTOR",
    )

    assert declared_selectors
    assert len(declared_selectors) == len(set(declared_selectors.values()))
    assert set(declared_selectors.values()) == set(
        benchmarks._BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR
    )


def test_default_benchmark_published_manifest_helper_is_cached_and_preserves_selector_order() -> None:
    manifests = published_benchmark_manifests()
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )

    assert published_benchmark_manifests() is manifests
    assert tuple(manifest.path for manifest in manifests) == published_manifest_paths


def test_default_benchmark_published_manifest_inventory_has_unique_manifest_and_workload_ids() -> None:
    manifests = published_benchmark_manifests()
    manifest_ids = [manifest.manifest_id for manifest in manifests]
    workloads = [workload for manifest in manifests for workload in manifest.workloads]

    assert duplicate_items(Counter(manifest_ids)) == []
    assert duplicate_items(Counter(workload.workload_id for workload in workloads)) == []

    workloads_by_manifest = Counter(workload.manifest_id for workload in workloads)
    published_manifest_ids = set(manifest_ids)
    for manifest_id in published_manifest_ids:
        assert workloads_by_manifest[manifest_id] > 0

    for workload in workloads:
        assert workload.manifest_id in published_manifest_ids


def test_built_native_smoke_runner_uses_explicit_report_paths_only() -> None:
    _assert_built_native_runner_uses_optional_report_path(
        runner=benchmarks.run_built_native_smoke_benchmarks,
        expected_manifest_selector=benchmarks.BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR,
        expected_smoke_only=True,
    )


def test_built_native_smoke_cli_uses_explicit_report_paths_only(
    tmp_path: pathlib.Path,
) -> None:
    _assert_built_native_cli_uses_optional_report_path(
        tmp_path,
        flag="--native-smoke",
        runner_name="run_built_native_smoke_benchmarks",
        report_name="benchmarks-native-smoke.json",
    )


def test_built_native_smoke_mode_requires_real_built_runtime(
    tmp_path: pathlib.Path,
) -> None:
    _assert_built_native_mode_requires_real_built_runtime(
        tmp_path / "benchmarks-native-smoke.json",
        runner=benchmarks.run_built_native_smoke_benchmarks,
    )


@pytest.mark.skipif(
    MATURIN is None,
    reason="built-native benchmark smoke requires a maturin executable on PATH",
)
def test_built_native_smoke_mode_writes_built_native_report(
    tmp_path: pathlib.Path,
) -> None:
    report_path = tmp_path / "benchmarks-native-smoke.json"
    scorecard = benchmarks.run_built_native_smoke_benchmarks(
        report_path=report_path,
    )
    assert report_path.is_file()
    _assert_built_native_combined_scorecard_fields(
        scorecard,
        expected_phase="phase2-module-boundary-suite",
        expected_selection_mode="smoke",
        expected_manifest_count=3,
    )
    assert scorecard["implementation"]["adapter"] == "rebar.module-surface"
    assert scorecard["summary"]["total_workloads"] == 6
    assert scorecard["summary"]["parser_workloads"] == 0
    assert scorecard["summary"]["module_workloads"] == 6
    assert scorecard["summary"]["regression_workloads"] == 0
    assert scorecard["summary"]["measured_workloads"] == 6
    assert scorecard["summary"]["known_gap_count"] == 0
    assert [workload["id"] for workload in scorecard["workloads"]] == [
        "pattern-search-literal-warm-hit",
        "pattern-fullmatch-bytes-purged-hit",
        "module-split-literal-warm-str",
        "pattern-subn-literal-purged-bytes",
        "module-search-inline-flag-warm-str-hit",
        "pattern-fullmatch-ignorecase-purged-bytes-hit",
    ]


def test_run_benchmarks_falls_back_to_source_shim_when_build_tooling_is_unavailable(
    tmp_path: pathlib.Path,
) -> None:
    report_path = tmp_path / "benchmarks.json"
    with mock.patch.object(
        benchmarks,
        "provision_built_native_runtime",
        return_value=(None, None, _MISSING_MATURIN_REASON),
    ):
        scorecard = benchmarks.run_benchmarks(
            manifest_paths=[COMPILE_MATRIX_MANIFEST_PATH],
            report_path=report_path,
            adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        )

    implementation = scorecard["implementation"]
    assert implementation["adapter_mode_requested"] == "built-native"
    assert implementation["adapter_mode_resolved"] == "source-tree-shim"
    assert implementation["build_mode"] == "source-tree-shim"
    assert implementation["timing_path"] == "source-tree-shim"
    assert isinstance(implementation["native_module_loaded"], bool)
    assert "maturin" in implementation["native_unavailable_reason"]
    assert implementation["native_build_tool"] is None
    assert implementation["native_wheel"] is None


def test_run_benchmarks_rejects_smoke_only_selection_without_smoke_workloads(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-no-smoke-selection-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
        },
        "workloads": [
            {
                "id": "compile-nonsmoke-contract",
                "bucket": "compile",
                "family": "parser",
                "operation": "compile",
                "pattern": "abc",
                "notes": [
                    "Keeps the manifest valid while intentionally omitting any smoke-tagged workloads."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_no_smoke_selection_contract.py",
        manifest_source,
    )

    with pytest.raises(
        ValueError,
        match="no smoke-tagged workloads matched the selected benchmark manifests",
    ):
        benchmarks.run_benchmarks(
            manifest_paths=[manifest_path],
            report_path=None,
            smoke_only=True,
        )


@pytest.mark.skipif(
    MATURIN is None,
    reason="built-native benchmark provenance smoke requires a maturin executable on PATH",
)
def test_run_benchmarks_reports_built_native_provenance_when_available(
    tmp_path: pathlib.Path,
) -> None:
    scorecard = benchmarks.run_benchmarks(
        manifest_paths=[COMPILE_MATRIX_MANIFEST_PATH],
        report_path=tmp_path / "benchmarks-native.json",
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
    )

    implementation = scorecard["implementation"]
    assert implementation["adapter_mode_requested"] == "built-native"
    assert implementation["adapter_mode_resolved"] == "built-native"
    assert implementation["build_mode"] == "built-native"
    assert implementation["timing_path"] == "built-native"
    assert implementation["native_module_loaded"] is True
    assert implementation["native_module_name"] == "rebar._rebar"
    assert implementation["native_scaffold_status"] == "scaffold-only"
    assert implementation["native_target_cpython_series"] == "3.12.x"
    assert implementation["native_unavailable_reason"] is None
    assert implementation["native_build_tool"] == "maturin"
    assert str(implementation["native_wheel"]).startswith("rebar-")
    assert (
        scorecard["environment"]["execution_model"]
        == "single-interpreter subprocess workload probes against a built native wheel"
    )


def test_built_native_full_runner_uses_explicit_report_paths_only() -> None:
    _assert_built_native_runner_uses_optional_report_path(
        runner=benchmarks.run_built_native_full_benchmarks,
        expected_manifest_selector=benchmarks.PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
        expected_smoke_only=False,
    )


def test_built_native_full_cli_uses_explicit_report_paths_only(
    tmp_path: pathlib.Path,
) -> None:
    _assert_built_native_cli_uses_optional_report_path(
        tmp_path,
        flag="--native-full",
        runner_name="run_built_native_full_benchmarks",
        report_name="benchmarks-native-full.json",
    )


def test_built_native_full_mode_requires_real_built_runtime(
    tmp_path: pathlib.Path,
) -> None:
    _assert_built_native_mode_requires_real_built_runtime(
        tmp_path / "benchmarks-native-full.json",
        runner=benchmarks.run_built_native_full_benchmarks,
    )


@pytest.mark.skipif(
    MATURIN is None,
    reason="built-native full-suite benchmark requires a maturin executable on PATH",
)
def test_built_native_full_mode_writes_built_native_report_with_known_gaps(
    tmp_path: pathlib.Path,
) -> None:
    published_manifests = benchmarks.published_benchmark_manifests()
    selected_workloads = [
        workload
        for manifest in published_manifests
        for workload in manifest.workloads
    ]
    expected_total = len(selected_workloads)
    expected_parser = sum(1 for workload in selected_workloads if workload.family == "parser")
    expected_module = sum(1 for workload in selected_workloads if workload.family == "module")
    expected_regression = sum(
        1 for workload in selected_workloads if workload.manifest_id == "regression-matrix"
    )

    report_path = tmp_path / "benchmarks-native-full.json"
    scorecard = benchmarks.run_built_native_full_benchmarks(
        report_path=report_path,
    )
    assert report_path.is_file()
    _assert_built_native_combined_scorecard_fields(
        scorecard,
        expected_phase="phase3-regression-stability-suite",
        expected_selection_mode="full",
        expected_manifest_count=len(published_manifests),
    )
    assert scorecard["summary"]["total_workloads"] == expected_total
    assert scorecard["summary"]["parser_workloads"] == expected_parser
    assert scorecard["summary"]["module_workloads"] == expected_module
    assert scorecard["summary"]["regression_workloads"] == expected_regression

    unimplemented_workloads = [
        workload
        for workload in scorecard["workloads"]
        if workload["implementation_timing"]["status"] == "unimplemented"
    ]
    measured_workloads = [
        workload
        for workload in scorecard["workloads"]
        if workload["implementation_timing"]["status"] == "measured"
    ]
    assert len(unimplemented_workloads) > 0
    assert scorecard["summary"]["known_gap_count"] == len(unimplemented_workloads)
    assert scorecard["summary"]["measured_workloads"] == len(measured_workloads)
    assert len(measured_workloads) + len(unimplemented_workloads) == expected_total


def test_standard_benchmark_manifest_materializes_callable_replacement_descriptors(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-loader-contract",
        "defaults": {
            "warmup_iterations": 2,
            "sample_iterations": 3,
            "timed_samples": 4,
            "text_model": "str",
            "cache_mode": "warm",
            "timing_scope": "module-helper-call",
        },
        "workloads": [
            {
                "id": "module-sub-callable-numbered-contract-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": r"a((bc)+)d",
                "replacement": {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "haystack": "zzabcbcdzz",
                "count": 0,
                "categories": ["replacement", "callable", "numbered-group", "str"],
                "notes": [
                    "Ensures Python-backed benchmark manifests materialize numbered callable replacement descriptors."
                ],
            },
            {
                "id": "pattern-subn-callable-named-contract-str",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": r"a(?P<outer>(?P<inner>bc)+)d",
                "replacement": {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": "<",
                    "suffix": ">",
                },
                "haystack": "zzabcbcdabcbcdzz",
                "count": 1,
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "categories": ["replacement", "callable", "named-group", "str"],
                "notes": [
                    "Ensures Python-backed benchmark manifests materialize named callable replacement descriptors."
                ],
            },
            {
                "id": "module-sub-callable-constant-contract-bytes",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": r"a((bc)+)d",
                "replacement": {
                    "type": "callable_constant",
                    "value": {
                        "type": "bytes",
                        "value": "CONST",
                        "encoding": "ascii",
                    },
                },
                "haystack": "zzabcbcdzz",
                "text_model": "bytes",
                "categories": ["replacement", "callable", "constant", "bytes"],
                "notes": [
                    "Ensures Python-backed benchmark manifests keep bytes-aware callable constants available for subprocess serialization and runtime materialization."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_loader_contract.py",
        manifest_source,
    )
    manifest = load_manifest(manifest_path)
    workloads = manifest.workloads

    assert manifest.manifest_id == "python-benchmark-loader-contract"
    assert not hasattr(manifest, "defaults")
    assert [workload.workload_id for workload in workloads] == [
        "module-sub-callable-numbered-contract-str",
        "pattern-subn-callable-named-contract-str",
        "module-sub-callable-constant-contract-bytes",
    ]

    numbered_workload = workloads[0]
    assert numbered_workload.warmup_iterations == 2
    assert numbered_workload.sample_iterations == 3
    assert numbered_workload.timed_samples == 4
    assert numbered_workload.pattern_payload() == r"a((bc)+)d"
    assert numbered_workload.haystack_payload() == "zzabcbcdzz"
    numbered_replacement = numbered_workload.replacement_payload()
    assert callable(numbered_replacement)
    assert numbered_replacement.__module__ == "rebar_harness.benchmarks"
    assert numbered_replacement.__qualname__ == "callable_match_group"
    numbered_match = re.search(
        numbered_workload.pattern_payload(),
        numbered_workload.haystack_payload(),
    )
    assert numbered_match is not None
    assert numbered_replacement(numbered_match) == "bcbcx"
    assert workload_to_payload(numbered_workload)["replacement"] == {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x",
    }

    named_workload = workloads[1]
    assert named_workload.cache_mode == "purged"
    assert named_workload.timing_scope == "pattern-helper-call"
    named_replacement = named_workload.replacement_payload()
    assert callable(named_replacement)
    assert named_replacement.__module__ == "rebar_harness.benchmarks"
    assert named_replacement.__qualname__ == "callable_match_group"
    named_match = re.search(
        named_workload.pattern_payload(),
        named_workload.haystack_payload(),
    )
    assert named_match is not None
    assert named_replacement(named_match) == "<bc>"
    assert workload_to_payload(named_workload)["replacement"] == {
        "type": "callable_match_group",
        "group": "inner",
        "prefix": "<",
        "suffix": ">",
    }

    constant_bytes_workload = workloads[2]
    assert constant_bytes_workload.text_model == "bytes"
    assert constant_bytes_workload.pattern_payload() == rb"a((bc)+)d"
    assert constant_bytes_workload.haystack_payload() == b"zzabcbcdzz"
    constant_bytes_replacement = constant_bytes_workload.replacement_payload()
    assert callable(constant_bytes_replacement)
    assert constant_bytes_replacement.__module__ == "rebar_harness.benchmarks"
    assert constant_bytes_replacement.__qualname__ == "callable_constant"
    constant_bytes_match = re.search(
        constant_bytes_workload.pattern_payload(),
        constant_bytes_workload.haystack_payload(),
    )
    assert constant_bytes_match is not None
    assert constant_bytes_replacement(constant_bytes_match) == b"CONST"
    assert workload_to_payload(constant_bytes_workload)["replacement"] == {
        "type": "callable_constant",
        "value": {
            "type": "bytes",
            "value": "CONST",
            "encoding": "ascii",
        },
    }


def test_standard_benchmark_manifest_preserves_indexlike_numeric_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-indexlike-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
        },
        "workloads": [
            {
                "id": "module-split-indexlike-contract-bytes",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "zabcabcabc",
                "maxsplit": {
                    "type": "indexlike",
                    "value": 2,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.split positional indexlike descriptors JSON-safe until helper invocation."
                ],
            },
            {
                "id": "module-sub-indexlike-contract-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "count": {
                    "type": "indexlike",
                    "value": 2,
                },
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.sub positional indexlike descriptors JSON-safe until helper invocation."
                ],
            },
            {
                "id": "module-subn-indexlike-contract-bytes",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "count": {
                    "type": "indexlike",
                    "value": 2,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.subn positional indexlike descriptors JSON-safe until helper invocation."
                ],
            },
            {
                "id": "pattern-split-indexlike-contract-str",
                "bucket": "pattern-split",
                "family": "module",
                "operation": "pattern.split",
                "pattern": "abc",
                "haystack": "zabcabcabc",
                "maxsplit": {
                    "type": "indexlike",
                    "value": 2,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.split positional indexlike descriptors JSON-safe until helper invocation."
                ],
            },
            {
                "id": "pattern-sub-indexlike-contract-bytes",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "count": {
                    "type": "indexlike",
                    "value": 2,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.sub positional indexlike descriptors JSON-safe until helper invocation."
                ],
            },
            {
                "id": "pattern-subn-indexlike-contract-str",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "count": {
                    "type": "indexlike",
                    "value": 2,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.subn positional indexlike descriptors JSON-safe until helper invocation."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_indexlike_contract.py",
        manifest_source,
    )
    (
        split_workload,
        sub_workload,
        subn_workload,
        pattern_split_workload,
        pattern_sub_workload,
        pattern_subn_workload,
    ) = load_manifest(manifest_path).workloads

    assert split_workload.maxsplit == {
        "type": "indexlike",
        "value": 2,
    }
    round_tripped_split = workload_from_payload(workload_to_payload(split_workload))
    assert round_tripped_split.maxsplit_argument().__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_split) == [b"z", b"", b"abc"]

    assert sub_workload.count == {
        "type": "indexlike",
        "value": 2,
    }
    round_tripped_sub = workload_from_payload(workload_to_payload(sub_workload))
    assert round_tripped_sub.count_argument().__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_sub) == "xxabc"

    assert subn_workload.count == {
        "type": "indexlike",
        "value": 2,
    }
    round_tripped_subn = workload_from_payload(workload_to_payload(subn_workload))
    assert round_tripped_subn.count_argument().__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_subn) == (b"xxabc", 2)

    assert pattern_split_workload.maxsplit == {
        "type": "indexlike",
        "value": 2,
    }
    round_tripped_pattern_split = workload_from_payload(
        workload_to_payload(pattern_split_workload)
    )
    assert round_tripped_pattern_split.maxsplit_argument().__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_pattern_split) == [
        "z",
        "",
        "abc",
    ]

    assert pattern_sub_workload.count == {
        "type": "indexlike",
        "value": 2,
    }
    round_tripped_pattern_sub = workload_from_payload(
        workload_to_payload(pattern_sub_workload)
    )
    assert round_tripped_pattern_sub.count_argument().__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_pattern_sub) == b"xxabc"

    assert pattern_subn_workload.count == {
        "type": "indexlike",
        "value": 2,
    }
    round_tripped_pattern_subn = workload_from_payload(
        workload_to_payload(pattern_subn_workload)
    )
    assert round_tripped_pattern_subn.count_argument().__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_pattern_subn) == (
        "xxabc",
        2,
    )


@pytest.mark.parametrize(
    (
        "workload_id",
        "bucket",
        "operation",
        "haystack",
        "replacement",
        "count",
        "maxsplit",
        "text_model",
        "expected_result",
        "expected_field_name",
    ),
    (
        pytest.param(
            "module-split-indexlike-contract-bytes",
            "module-split",
            "module.split",
            "zabcabcabc",
            None,
            0,
            {"type": "indexlike", "value": 2},
            "bytes",
            [b"z", b"", b"abc"],
            "maxsplit",
            id="module-split",
        ),
        pytest.param(
            "module-sub-indexlike-contract-str",
            "module-sub",
            "module.sub",
            "abcabcabc",
            "x",
            {"type": "indexlike", "value": 2},
            0,
            "str",
            "xxabc",
            "count",
            id="module-sub",
        ),
        pytest.param(
            "module-subn-indexlike-contract-bytes",
            "module-subn",
            "module.subn",
            "abcabcabc",
            "x",
            {"type": "indexlike", "value": 2},
            0,
            "bytes",
            (b"xxabc", 2),
            "count",
            id="module-subn",
        ),
        pytest.param(
            "pattern-split-indexlike-contract-str",
            "pattern-split",
            "pattern.split",
            "zabcabcabc",
            None,
            0,
            {"type": "indexlike", "value": 2},
            "str",
            ["z", "", "abc"],
            "maxsplit",
            id="pattern-split",
        ),
        pytest.param(
            "pattern-sub-indexlike-contract-bytes",
            "pattern-sub",
            "pattern.sub",
            "abcabcabc",
            "x",
            {"type": "indexlike", "value": 2},
            0,
            "bytes",
            b"xxabc",
            "count",
            id="pattern-sub",
        ),
        pytest.param(
            "pattern-subn-indexlike-contract-str",
            "pattern-subn",
            "pattern.subn",
            "abcabcabc",
            "x",
            {"type": "indexlike", "value": 2},
            0,
            "str",
            ("xxabc", 2),
            "count",
            id="pattern-subn",
        ),
    ),
)
def test_collection_replacement_indexlike_descriptors_materialize_on_each_helper_call(
    monkeypatch,
    workload_id: str,
    bucket: str,
    operation: str,
    haystack: str,
    replacement: str | None,
    count: object,
    maxsplit: object,
    text_model: str,
    expected_result: object,
    expected_field_name: str,
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-indexlike-contract",
            "workload_id": workload_id,
            "bucket": bucket,
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "flags": 0,
            "count": count,
            "maxsplit": maxsplit,
            "text_model": text_model,
            "cache_mode": "purged",
            "timing_scope": (
                "module-helper-call"
                if operation.startswith("module.")
                else "pattern-helper-call"
            ),
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )
    observed_field_names: list[str] = []
    original_materialize = benchmarks.materialize_numeric_workload_argument

    def record_numeric_materialization(value: Any, *, field_name: str) -> Any:
        observed_field_names.append(field_name)
        return original_materialize(value, field_name=field_name)

    monkeypatch.setattr(
        benchmarks,
        "materialize_numeric_workload_argument",
        record_numeric_materialization,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []
        assert callback() == expected_result
        assert callback() == expected_result
    finally:
        re.purge()

    assert observed_field_names == [expected_field_name, expected_field_name]


def test_standard_benchmark_manifest_preserves_pattern_window_indexlike_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-pattern-window-indexlike-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
        },
        "workloads": [
            {
                "id": "pattern-search-pos-indexlike-contract-str",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "abc",
                "haystack": "zabcabc",
                "pos": {
                    "type": "indexlike",
                    "value": 2,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.search positional indexlike descriptors unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-search-endpos-indexlike-contract-bytes",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "abc",
                "haystack": "zabcabc",
                "pos": 0,
                "endpos": {
                    "type": "indexlike",
                    "value": 4,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.search endpos indexlike descriptors unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-match-window-indexlike-positional-contract-bytes",
                "bucket": "pattern-match",
                "family": "module",
                "operation": "pattern.match",
                "pattern": "abc",
                "haystack": "zabc",
                "pos": {
                    "type": "indexlike",
                    "value": 1,
                },
                "endpos": {
                    "type": "indexlike",
                    "value": 4,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.match positional pos/endpos indexlike descriptors unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-fullmatch-window-indexlike-contract-bytes",
                "bucket": "pattern-fullmatch",
                "family": "module",
                "operation": "pattern.fullmatch",
                "pattern": "abc",
                "haystack": "zabc",
                "pos": {
                    "type": "indexlike",
                    "value": 1,
                },
                "endpos": {
                    "type": "indexlike",
                    "value": 4,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.fullmatch window indexlike descriptors unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-findall-window-indexlike-contract-str",
                "bucket": "pattern-findall",
                "family": "module",
                "operation": "pattern.findall",
                "pattern": "abc",
                "haystack": "zabcabcabcz",
                "pos": {
                    "type": "indexlike",
                    "value": 1,
                },
                "endpos": {
                    "type": "indexlike",
                    "value": 7,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.findall window indexlike descriptors unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-finditer-window-indexlike-contract-bytes",
                "bucket": "pattern-finditer",
                "family": "module",
                "operation": "pattern.finditer",
                "pattern": "abc",
                "haystack": "zabcabcabcz",
                "pos": {
                    "type": "indexlike",
                    "value": 1,
                },
                "endpos": {
                    "type": "indexlike",
                    "value": 7,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.finditer window indexlike descriptors unresolved until helper invocation."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_pattern_window_indexlike_contract.py",
        manifest_source,
    )
    (
        search_pos_workload,
        search_endpos_workload,
        match_window_workload,
        fullmatch_window_workload,
        findall_window_workload,
        finditer_window_workload,
    ) = load_manifest(manifest_path).workloads

    assert search_pos_workload.pos == {
        "type": "indexlike",
        "value": 2,
    }
    assert search_pos_workload.endpos is None
    round_tripped_search_pos = workload_from_payload(
        workload_to_payload(search_pos_workload)
    )
    assert round_tripped_search_pos.pos_argument().__index__() == 2
    assert round_tripped_search_pos.endpos_argument() is None
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_search_pos),
        re.compile("abc").search("zabcabc", 2),
        check_regs=True,
    )

    assert search_endpos_workload.pos == 0
    assert search_endpos_workload.endpos == {
        "type": "indexlike",
        "value": 4,
    }
    round_tripped_search_endpos = workload_from_payload(
        workload_to_payload(search_endpos_workload)
    )
    assert round_tripped_search_endpos.pos_argument() == 0
    assert round_tripped_search_endpos.endpos_argument().__index__() == 4
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_search_endpos),
        re.compile(b"abc").search(b"zabcabc", 0, 4),
        check_regs=True,
    )

    assert match_window_workload.pos == {
        "type": "indexlike",
        "value": 1,
    }
    assert match_window_workload.endpos == {
        "type": "indexlike",
        "value": 4,
    }
    round_tripped_match = workload_from_payload(
        workload_to_payload(match_window_workload)
    )
    assert round_tripped_match.pos_argument().__index__() == 1
    assert round_tripped_match.endpos_argument().__index__() == 4
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_match),
        re.compile(b"abc").match(b"zabc", 1, 4),
        check_regs=True,
    )

    assert fullmatch_window_workload.pos == {
        "type": "indexlike",
        "value": 1,
    }
    assert fullmatch_window_workload.endpos == {
        "type": "indexlike",
        "value": 4,
    }
    round_tripped_fullmatch = workload_from_payload(
        workload_to_payload(fullmatch_window_workload)
    )
    assert round_tripped_fullmatch.pos_argument().__index__() == 1
    assert round_tripped_fullmatch.endpos_argument().__index__() == 4
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_fullmatch),
        re.compile(b"abc").fullmatch(b"zabc", 1, 4),
        check_regs=True,
    )

    assert findall_window_workload.pos == {
        "type": "indexlike",
        "value": 1,
    }
    assert findall_window_workload.endpos == {
        "type": "indexlike",
        "value": 7,
    }
    round_tripped_findall = workload_from_payload(
        workload_to_payload(findall_window_workload)
    )
    assert round_tripped_findall.pos_argument().__index__() == 1
    assert round_tripped_findall.endpos_argument().__index__() == 7
    assert run_benchmark_workload_with_cpython(round_tripped_findall) == [
        "abc",
        "abc",
    ]

    assert finditer_window_workload.pos == {
        "type": "indexlike",
        "value": 1,
    }
    assert finditer_window_workload.endpos == {
        "type": "indexlike",
        "value": 7,
    }
    round_tripped_finditer = workload_from_payload(
        workload_to_payload(finditer_window_workload)
    )
    assert round_tripped_finditer.pos_argument().__index__() == 1
    assert round_tripped_finditer.endpos_argument().__index__() == 7
    observed_finditer = run_benchmark_workload_with_cpython(round_tripped_finditer)
    expected_finditer = list(re.compile(b"abc").finditer(b"zabcabcabcz", 1, 7))
    assert len(observed_finditer) == len(expected_finditer) == 2
    for observed_match, expected_match in zip(
        observed_finditer,
        expected_finditer,
        strict=True,
    ):
        assert_match_result_parity(
            "stdlib",
            observed_match,
            expected_match,
            check_regs=True,
        )


@pytest.mark.parametrize(
    ("kwargs_payload", "operation", "pos", "endpos", "error_pattern"),
    (
        pytest.param(
            ["pos"],
            "pattern.search",
            None,
            None,
            "benchmark workload kwargs must be an object",
            id="non-object",
        ),
        pytest.param(
            {"pos": 1},
            "module.split",
            None,
            None,
            re.escape(
                "benchmark workload kwargs for module.split only supports the "
                "`maxsplit` key; got unsupported keys ['pos']"
            ),
            id="unsupported-module-key",
        ),
        pytest.param(
            {"count": 1},
            "module.search",
            None,
            None,
            re.escape(
                "benchmark workload kwargs for module.search only supports the "
                "`flags` key; got unsupported keys ['count']"
            ),
            id="unsupported-module-search-key",
        ),
        pytest.param(
            {"flags": 1},
            "module.findall",
            None,
            None,
            re.escape(
                "benchmark workload kwargs are only supported for pattern.search, "
                "pattern.match, pattern.fullmatch, pattern.findall, "
                "pattern.finditer, pattern.split, pattern.sub, pattern.subn, "
                "module.search, module.match, module.fullmatch, module.split, "
                "module.sub, and module.subn"
            ),
            id="unsupported-operation",
        ),
        pytest.param(
            {"endpos": 4},
            "pattern.search",
            0,
            None,
            re.escape(
                "benchmark workload cannot mix top-level pos/endpos fields with "
                "keyword kwargs carriers"
            ),
            id="mixed-carriers",
        ),
    ),
)
def test_standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points(
    tmp_path: pathlib.Path,
    kwargs_payload: object,
    operation: str,
    pos: object,
    endpos: object,
    error_pattern: str,
) -> None:
    manifest_source = f"""
    MANIFEST = {{
        "schema_version": 1,
        "manifest_id": "python-benchmark-invalid-pattern-keyword-window-contract",
        "workloads": [
            {{
                "id": "pattern-invalid-keyword-window-contract",
                "bucket": "pattern-search",
                "family": "module",
                "operation": {operation!r},
                "pattern": "abc",
                "haystack": "zabcabc",
                "pos": {pos!r},
                "endpos": {endpos!r},
                "kwargs": {kwargs_payload!r},
            }},
        ],
    }}
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_pattern_keyword_window_contract.py",
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(
            {
                "manifest_id": "python-benchmark-invalid-pattern-keyword-window-contract",
                "workload_id": "pattern-invalid-keyword-window-contract",
                "bucket": "pattern-search",
                "family": "module",
                "operation": operation,
                "pattern": "abc",
                "haystack": "zabcabc",
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "pos": pos,
                "endpos": endpos,
                "kwargs": kwargs_payload,
                "text_model": "str",
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            }
        )


def test_standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-pattern-keyword-window-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            {
                "id": "pattern-search-pos-keyword-contract-str",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "abc",
                "haystack": "zabcabc",
                "kwargs": {
                    "pos": 2,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.search keyword pos carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-match-pos-keyword-contract-str",
                "bucket": "pattern-match",
                "family": "module",
                "operation": "pattern.match",
                "pattern": "abc",
                "haystack": "zabcabc",
                "kwargs": {
                    "pos": 1,
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.match keyword pos carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-match-window-indexlike-keyword-contract-bytes",
                "bucket": "pattern-match",
                "family": "module",
                "operation": "pattern.match",
                "pattern": "abc",
                "haystack": "zabc",
                "text_model": "bytes",
                "kwargs": {
                    "pos": {
                        "type": "indexlike",
                        "value": 1,
                    },
                    "endpos": {
                        "type": "indexlike",
                        "value": 4,
                    },
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.match keyword pos/endpos indexlike carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-fullmatch-window-keyword-contract-bytes",
                "bucket": "pattern-fullmatch",
                "family": "module",
                "operation": "pattern.fullmatch",
                "pattern": "abc",
                "haystack": "zabc",
                "text_model": "bytes",
                "kwargs": {
                    "pos": 1,
                    "endpos": 4,
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.fullmatch keyword pos/endpos carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-findall-bool-window-keyword-contract-str",
                "bucket": "pattern-findall",
                "family": "module",
                "operation": "pattern.findall",
                "pattern": "abc",
                "haystack": "zabcabcz",
                "kwargs": {
                    "pos": True,
                    "endpos": 7,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.findall keyword bool/int carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-finditer-window-indexlike-keyword-contract-bytes",
                "bucket": "pattern-finditer",
                "family": "module",
                "operation": "pattern.finditer",
                "pattern": "abc",
                "haystack": "zabcabcabcz",
                "text_model": "bytes",
                "kwargs": {
                    "pos": {
                        "type": "indexlike",
                        "value": 1,
                    },
                    "endpos": {
                        "type": "indexlike",
                        "value": 7,
                    },
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.finditer keyword indexlike carriers unresolved until helper invocation."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_pattern_keyword_window_contract.py",
        manifest_source,
    )
    (
        search_pos_workload,
        match_pos_workload,
        match_window_workload,
        fullmatch_window_workload,
        findall_window_workload,
        finditer_window_workload,
    ) = load_manifest(manifest_path).workloads

    assert search_pos_workload.pos is None
    assert search_pos_workload.endpos is None
    assert search_pos_workload.kwargs == {"pos": 2}
    round_tripped_search_pos = workload_from_payload(
        workload_to_payload(search_pos_workload)
    )
    assert round_tripped_search_pos.kwargs == {"pos": 2}
    assert round_tripped_search_pos.keyword_arguments() == {"pos": 2}
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_search_pos),
        re.compile("abc").search("zabcabc", pos=2),
        check_regs=True,
    )

    assert match_pos_workload.pos is None
    assert match_pos_workload.endpos is None
    assert match_pos_workload.kwargs == {"pos": 1}
    round_tripped_match_pos = workload_from_payload(
        workload_to_payload(match_pos_workload)
    )
    assert round_tripped_match_pos.kwargs == {"pos": 1}
    assert round_tripped_match_pos.keyword_arguments() == {"pos": 1}
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_match_pos),
        re.compile("abc").match("zabcabc", pos=1),
        check_regs=True,
    )

    assert match_window_workload.pos is None
    assert match_window_workload.endpos is None
    assert match_window_workload.kwargs == {
        "endpos": {"type": "indexlike", "value": 4},
        "pos": {"type": "indexlike", "value": 1},
    }
    round_tripped_match_window = workload_from_payload(
        workload_to_payload(match_window_workload)
    )
    assert round_tripped_match_window.kwargs == {
        "endpos": {"type": "indexlike", "value": 4},
        "pos": {"type": "indexlike", "value": 1},
    }
    materialized_match_window_kwargs = (
        round_tripped_match_window.keyword_arguments()
    )
    assert materialized_match_window_kwargs["pos"].__index__() == 1
    assert materialized_match_window_kwargs["endpos"].__index__() == 4
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_match_window),
        re.compile(b"abc").match(b"zabc", pos=1, endpos=4),
        check_regs=True,
    )

    assert fullmatch_window_workload.pos is None
    assert fullmatch_window_workload.endpos is None
    assert fullmatch_window_workload.kwargs == {"endpos": 4, "pos": 1}
    round_tripped_fullmatch = workload_from_payload(
        workload_to_payload(fullmatch_window_workload)
    )
    assert round_tripped_fullmatch.kwargs == {"endpos": 4, "pos": 1}
    assert round_tripped_fullmatch.keyword_arguments() == {"endpos": 4, "pos": 1}
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_fullmatch),
        re.compile(b"abc").fullmatch(b"zabc", pos=1, endpos=4),
        check_regs=True,
    )

    assert findall_window_workload.pos is None
    assert findall_window_workload.endpos is None
    assert findall_window_workload.kwargs == {"endpos": 7, "pos": True}
    assert type(findall_window_workload.kwargs["pos"]) is bool
    round_tripped_findall = workload_from_payload(
        workload_to_payload(findall_window_workload)
    )
    assert round_tripped_findall.kwargs == {"endpos": 7, "pos": True}
    assert type(round_tripped_findall.kwargs["pos"]) is bool
    materialized_findall_kwargs = round_tripped_findall.keyword_arguments()
    assert materialized_findall_kwargs == {"endpos": 7, "pos": True}
    assert materialized_findall_kwargs["pos"] is True
    assert run_benchmark_workload_with_cpython(round_tripped_findall) == [
        "abc",
        "abc",
    ]

    assert finditer_window_workload.pos is None
    assert finditer_window_workload.endpos is None
    assert finditer_window_workload.kwargs == {
        "endpos": {"type": "indexlike", "value": 7},
        "pos": {"type": "indexlike", "value": 1},
    }
    round_tripped_finditer = workload_from_payload(
        workload_to_payload(finditer_window_workload)
    )
    assert round_tripped_finditer.kwargs == {
        "endpos": {"type": "indexlike", "value": 7},
        "pos": {"type": "indexlike", "value": 1},
    }
    materialized_finditer_kwargs = round_tripped_finditer.keyword_arguments()
    assert materialized_finditer_kwargs["pos"].__index__() == 1
    assert materialized_finditer_kwargs["endpos"].__index__() == 7
    observed_finditer = run_benchmark_workload_with_cpython(round_tripped_finditer)
    expected_finditer = list(
        re.compile(b"abc").finditer(b"zabcabcabcz", pos=1, endpos=7)
    )
    assert len(observed_finditer) == len(expected_finditer) == 2
    for observed_match, expected_match in zip(
        observed_finditer,
        expected_finditer,
        strict=True,
    ):
        assert_match_result_parity(
            "stdlib",
            observed_match,
            expected_match,
            check_regs=True,
        )


def test_pattern_helper_keyword_kwargs_materialize_at_callback_time(
    monkeypatch,
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-pattern-keyword-window-contract",
            "workload_id": "pattern-finditer-window-indexlike-keyword-contract-bytes",
            "bucket": "pattern-finditer",
            "family": "module",
            "operation": "pattern.finditer",
            "pattern": "abc",
            "haystack": "zabcabcabcz",
            "flags": 0,
            "count": 0,
            "maxsplit": 0,
            "kwargs": {
                "pos": {"type": "indexlike", "value": 1},
                "endpos": {"type": "indexlike", "value": 7},
            },
            "text_model": "bytes",
            "cache_mode": "warm",
            "timing_scope": "pattern-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )
    observed_field_names: list[str] = []
    original_materialize = benchmarks.materialize_numeric_workload_argument

    def record_numeric_materialization(value: Any, *, field_name: str) -> Any:
        observed_field_names.append(field_name)
        return original_materialize(value, field_name=field_name)

    monkeypatch.setattr(
        benchmarks,
        "materialize_numeric_workload_argument",
        record_numeric_materialization,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        observed_matches = callback()

        assert observed_field_names == ["kwargs.endpos", "kwargs.pos"]
        assert len(observed_matches) == 2
    finally:
        re.purge()


def test_standard_benchmark_manifest_preserves_collection_replacement_keyword_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-pattern-collection-replacement-keyword-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            {
                "id": "pattern-split-maxsplit-keyword-contract-str",
                "bucket": "pattern-split",
                "family": "module",
                "operation": "pattern.split",
                "pattern": "abc",
                "haystack": "zabczabc",
                "kwargs": {
                    "maxsplit": 1,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.split maxsplit= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-split-maxsplit-bool-keyword-contract-str",
                "bucket": "pattern-split",
                "family": "module",
                "operation": "pattern.split",
                "pattern": "abc",
                "haystack": "zabcabc",
                "kwargs": {
                    "maxsplit": True,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.split maxsplit= bool keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-split-duplicate-maxsplit-keyword-contract-str",
                "bucket": "pattern-split",
                "family": "module",
                "operation": "pattern.split",
                "pattern": "abc",
                "haystack": "abcabc",
                "maxsplit": 1,
                "kwargs": {
                    "maxsplit": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "split() takes at most 2 arguments (3 given)",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.split duplicate maxsplit= carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-split-unexpected-keyword-contract-bytes",
                "bucket": "pattern-split",
                "family": "module",
                "operation": "pattern.split",
                "pattern": "abc",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "'missing' is an invalid keyword argument for split()",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.split unexpected-keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-sub-count-keyword-contract-bytes",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {
                    "count": 1,
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.sub count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-sub-count-bool-keyword-contract-bytes",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {
                    "count": False,
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.sub count= bool keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-sub-unexpected-keyword-contract-str",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "'missing' is an invalid keyword argument for sub()",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.sub unexpected-keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-sub-unexpected-keyword-after-positional-count-contract-str",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "count": 1,
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "sub() takes at most 3 arguments (4 given)",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.sub positional count plus unexpected keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-subn-count-keyword-contract-str",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "kwargs": {
                    "count": 1,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.subn count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-subn-count-bool-keyword-contract-str",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "kwargs": {
                    "count": True,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.subn count= bool keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-subn-unexpected-keyword-contract-bytes",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "text_model": "bytes",
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "'missing' is an invalid keyword argument for subn()",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.subn unexpected-keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-subn-unexpected-keyword-after-positional-count-contract-bytes",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "text_model": "bytes",
                "count": 1,
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "subn() takes at most 3 arguments (4 given)",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.subn positional count plus unexpected keyword carriers unresolved until helper invocation."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_pattern_collection_replacement_keyword_contract.py",
        manifest_source,
    )
    workloads_by_id = {
        workload.workload_id: workload
        for workload in load_manifest(manifest_path).workloads
    }
    split_workload = workloads_by_id["pattern-split-maxsplit-keyword-contract-str"]
    split_bool_workload = workloads_by_id[
        "pattern-split-maxsplit-bool-keyword-contract-str"
    ]
    split_duplicate_workload = workloads_by_id[
        "pattern-split-duplicate-maxsplit-keyword-contract-str"
    ]
    split_missing_workload = workloads_by_id[
        "pattern-split-unexpected-keyword-contract-bytes"
    ]
    sub_workload = workloads_by_id["pattern-sub-count-keyword-contract-bytes"]
    sub_bool_workload = workloads_by_id["pattern-sub-count-bool-keyword-contract-bytes"]
    sub_missing_workload = workloads_by_id["pattern-sub-unexpected-keyword-contract-str"]
    sub_missing_after_positional_count_workload = workloads_by_id[
        "pattern-sub-unexpected-keyword-after-positional-count-contract-str"
    ]
    subn_workload = workloads_by_id["pattern-subn-count-keyword-contract-str"]
    subn_bool_workload = workloads_by_id["pattern-subn-count-bool-keyword-contract-str"]
    subn_missing_workload = workloads_by_id[
        "pattern-subn-unexpected-keyword-contract-bytes"
    ]
    subn_missing_after_positional_count_workload = workloads_by_id[
        "pattern-subn-unexpected-keyword-after-positional-count-contract-bytes"
    ]

    assert split_workload.kwargs == {"maxsplit": 1}
    round_tripped_split = workload_from_payload(workload_to_payload(split_workload))
    assert round_tripped_split.kwargs == {"maxsplit": 1}
    assert round_tripped_split.keyword_arguments() == {"maxsplit": 1}
    assert run_benchmark_workload_with_cpython(round_tripped_split) == ["z", "zabc"]

    assert split_bool_workload.kwargs == {"maxsplit": True}
    assert type(split_bool_workload.kwargs["maxsplit"]) is bool
    round_tripped_split_bool = workload_from_payload(
        workload_to_payload(split_bool_workload)
    )
    assert round_tripped_split_bool.kwargs == {"maxsplit": True}
    assert type(round_tripped_split_bool.kwargs["maxsplit"]) is bool
    materialized_split_bool_kwargs = round_tripped_split_bool.keyword_arguments()
    assert materialized_split_bool_kwargs == {"maxsplit": True}
    assert materialized_split_bool_kwargs["maxsplit"] is True
    assert run_benchmark_workload_with_cpython(round_tripped_split_bool) == [
        "z",
        "abc",
    ]

    assert split_duplicate_workload.maxsplit == 1
    assert split_duplicate_workload.kwargs == {"maxsplit": 1}
    round_tripped_split_duplicate = workload_from_payload(
        workload_to_payload(split_duplicate_workload)
    )
    assert round_tripped_split_duplicate.maxsplit == 1
    assert round_tripped_split_duplicate.kwargs == {"maxsplit": 1}
    assert round_tripped_split_duplicate.keyword_arguments() == {"maxsplit": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("split() takes at most 2 arguments (3 given)"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_split_duplicate)

    assert split_missing_workload.kwargs == {"missing": 1}
    round_tripped_split_missing = workload_from_payload(
        workload_to_payload(split_missing_workload)
    )
    assert round_tripped_split_missing.kwargs == {"missing": 1}
    assert round_tripped_split_missing.keyword_arguments() == {"missing": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("'missing' is an invalid keyword argument for split()"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_split_missing)

    assert sub_workload.kwargs == {"count": 1}
    round_tripped_sub = workload_from_payload(workload_to_payload(sub_workload))
    assert round_tripped_sub.kwargs == {"count": 1}
    assert round_tripped_sub.keyword_arguments() == {"count": 1}
    assert run_benchmark_workload_with_cpython(round_tripped_sub) == b"xabc"

    assert sub_bool_workload.kwargs == {"count": False}
    assert type(sub_bool_workload.kwargs["count"]) is bool
    round_tripped_sub_bool = workload_from_payload(
        workload_to_payload(sub_bool_workload)
    )
    assert round_tripped_sub_bool.kwargs == {"count": False}
    assert type(round_tripped_sub_bool.kwargs["count"]) is bool
    materialized_sub_bool_kwargs = round_tripped_sub_bool.keyword_arguments()
    assert materialized_sub_bool_kwargs == {"count": False}
    assert materialized_sub_bool_kwargs["count"] is False
    assert run_benchmark_workload_with_cpython(round_tripped_sub_bool) == b"xx"

    assert sub_missing_workload.kwargs == {"missing": 1}
    round_tripped_sub_missing = workload_from_payload(
        workload_to_payload(sub_missing_workload)
    )
    assert round_tripped_sub_missing.kwargs == {"missing": 1}
    assert round_tripped_sub_missing.keyword_arguments() == {"missing": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("'missing' is an invalid keyword argument for sub()"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_sub_missing)

    assert sub_missing_after_positional_count_workload.count == 1
    assert sub_missing_after_positional_count_workload.kwargs == {"missing": 1}
    round_tripped_sub_missing_after_positional_count = workload_from_payload(
        workload_to_payload(sub_missing_after_positional_count_workload)
    )
    assert round_tripped_sub_missing_after_positional_count.count == 1
    assert round_tripped_sub_missing_after_positional_count.kwargs == {"missing": 1}
    assert (
        round_tripped_sub_missing_after_positional_count.keyword_arguments()
        == {"missing": 1}
    )
    with pytest.raises(
        TypeError,
        match=re.escape("sub() takes at most 3 arguments (4 given)"),
    ):
        run_benchmark_workload_with_cpython(
            round_tripped_sub_missing_after_positional_count
        )

    assert subn_workload.kwargs == {"count": 1}
    round_tripped_subn = workload_from_payload(workload_to_payload(subn_workload))
    assert round_tripped_subn.kwargs == {"count": 1}
    assert round_tripped_subn.keyword_arguments() == {"count": 1}
    assert run_benchmark_workload_with_cpython(round_tripped_subn) == ("xabc", 1)

    assert subn_bool_workload.kwargs == {"count": True}
    assert type(subn_bool_workload.kwargs["count"]) is bool
    round_tripped_subn_bool = workload_from_payload(
        workload_to_payload(subn_bool_workload)
    )
    assert round_tripped_subn_bool.kwargs == {"count": True}
    assert type(round_tripped_subn_bool.kwargs["count"]) is bool
    materialized_subn_bool_kwargs = round_tripped_subn_bool.keyword_arguments()
    assert materialized_subn_bool_kwargs == {"count": True}
    assert materialized_subn_bool_kwargs["count"] is True
    assert run_benchmark_workload_with_cpython(round_tripped_subn_bool) == (
        "xabc",
        1,
    )

    assert subn_missing_workload.kwargs == {"missing": 1}
    round_tripped_subn_missing = workload_from_payload(
        workload_to_payload(subn_missing_workload)
    )
    assert round_tripped_subn_missing.kwargs == {"missing": 1}
    assert round_tripped_subn_missing.keyword_arguments() == {"missing": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("'missing' is an invalid keyword argument for subn()"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_subn_missing)

    assert subn_missing_after_positional_count_workload.count == 1
    assert subn_missing_after_positional_count_workload.kwargs == {"missing": 1}
    round_tripped_subn_missing_after_positional_count = workload_from_payload(
        workload_to_payload(subn_missing_after_positional_count_workload)
    )
    assert round_tripped_subn_missing_after_positional_count.count == 1
    assert round_tripped_subn_missing_after_positional_count.kwargs == {"missing": 1}
    assert (
        round_tripped_subn_missing_after_positional_count.keyword_arguments()
        == {"missing": 1}
    )
    with pytest.raises(
        TypeError,
        match=re.escape("subn() takes at most 3 arguments (4 given)"),
    ):
        run_benchmark_workload_with_cpython(
            round_tripped_subn_missing_after_positional_count
        )


def test_standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-module-collection-replacement-keyword-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            {
                "id": "module-split-maxsplit-keyword-contract-bytes",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "zabczabc",
                "text_model": "bytes",
                "kwargs": {
                    "maxsplit": 1,
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.split maxsplit= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-sub-count-keyword-contract-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "kwargs": {
                    "count": 1,
                },
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.sub count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-subn-count-keyword-contract-bytes",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {
                    "count": 1,
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.subn count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-split-maxsplit-bool-keyword-contract-str",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "zabcabc",
                "kwargs": {
                    "maxsplit": True,
                },
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.split bool maxsplit= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-sub-count-bool-keyword-contract-bytes",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {
                    "count": False,
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.sub bool count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-subn-count-bool-keyword-contract-str",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "kwargs": {
                    "count": True,
                },
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.subn bool count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-split-maxsplit-indexlike-keyword-purged-bytes",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "zabcabcabc",
                "text_model": "bytes",
                "kwargs": {
                    "maxsplit": {"type": "indexlike", "value": 2},
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.split keyword __index__ carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-sub-count-indexlike-keyword-warm-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "kwargs": {
                    "count": {"type": "indexlike", "value": 2},
                },
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.sub keyword __index__ carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-subn-count-indexlike-keyword-purged-bytes",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "text_model": "bytes",
                "kwargs": {
                    "count": {"type": "indexlike", "value": 2},
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.subn keyword __index__ carriers unresolved until helper invocation."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_module_collection_replacement_keyword_contract.py",
        manifest_source,
    )
    (
        split_workload,
        sub_workload,
        subn_workload,
        split_bool_workload,
        sub_bool_workload,
        subn_bool_workload,
        split_indexlike_workload,
        sub_indexlike_workload,
        subn_indexlike_workload,
    ) = load_manifest(manifest_path).workloads

    assert split_workload.kwargs == {"maxsplit": 1}
    round_tripped_split = workload_from_payload(workload_to_payload(split_workload))
    assert round_tripped_split.kwargs == {"maxsplit": 1}
    assert round_tripped_split.keyword_arguments() == {"maxsplit": 1}
    assert run_benchmark_workload_with_cpython(round_tripped_split) == [
        b"z",
        b"zabc",
    ]

    assert sub_workload.kwargs == {"count": 1}
    round_tripped_sub = workload_from_payload(workload_to_payload(sub_workload))
    assert round_tripped_sub.kwargs == {"count": 1}
    assert round_tripped_sub.keyword_arguments() == {"count": 1}
    assert run_benchmark_workload_with_cpython(round_tripped_sub) == "xabc"

    assert subn_workload.kwargs == {"count": 1}
    round_tripped_subn = workload_from_payload(workload_to_payload(subn_workload))
    assert round_tripped_subn.kwargs == {"count": 1}
    assert round_tripped_subn.keyword_arguments() == {"count": 1}
    assert run_benchmark_workload_with_cpython(round_tripped_subn) == (
        b"xabc",
        1,
    )

    assert split_bool_workload.kwargs == {"maxsplit": True}
    assert type(split_bool_workload.kwargs["maxsplit"]) is bool
    round_tripped_split_bool = workload_from_payload(
        workload_to_payload(split_bool_workload)
    )
    assert round_tripped_split_bool.kwargs == {"maxsplit": True}
    assert type(round_tripped_split_bool.kwargs["maxsplit"]) is bool
    materialized_split_bool_kwargs = round_tripped_split_bool.keyword_arguments()
    assert materialized_split_bool_kwargs == {"maxsplit": True}
    assert materialized_split_bool_kwargs["maxsplit"] is True
    assert run_benchmark_workload_with_cpython(round_tripped_split_bool) == [
        "z",
        "abc",
    ]

    assert sub_bool_workload.kwargs == {"count": False}
    assert type(sub_bool_workload.kwargs["count"]) is bool
    round_tripped_sub_bool = workload_from_payload(
        workload_to_payload(sub_bool_workload)
    )
    assert round_tripped_sub_bool.kwargs == {"count": False}
    assert type(round_tripped_sub_bool.kwargs["count"]) is bool
    materialized_sub_bool_kwargs = round_tripped_sub_bool.keyword_arguments()
    assert materialized_sub_bool_kwargs == {"count": False}
    assert materialized_sub_bool_kwargs["count"] is False
    assert run_benchmark_workload_with_cpython(round_tripped_sub_bool) == b"xx"

    assert subn_bool_workload.kwargs == {"count": True}
    assert type(subn_bool_workload.kwargs["count"]) is bool
    round_tripped_subn_bool = workload_from_payload(
        workload_to_payload(subn_bool_workload)
    )
    assert round_tripped_subn_bool.kwargs == {"count": True}
    assert type(round_tripped_subn_bool.kwargs["count"]) is bool
    materialized_subn_bool_kwargs = round_tripped_subn_bool.keyword_arguments()
    assert materialized_subn_bool_kwargs == {"count": True}
    assert materialized_subn_bool_kwargs["count"] is True
    assert run_benchmark_workload_with_cpython(round_tripped_subn_bool) == (
        "xabc",
        1,
    )

    assert split_indexlike_workload.kwargs == {
        "maxsplit": {"type": "indexlike", "value": 2}
    }
    round_tripped_split_indexlike = workload_from_payload(
        workload_to_payload(split_indexlike_workload)
    )
    assert round_tripped_split_indexlike.kwargs == {
        "maxsplit": {"type": "indexlike", "value": 2}
    }
    materialized_split_indexlike_kwargs = (
        round_tripped_split_indexlike.keyword_arguments()
    )
    assert materialized_split_indexlike_kwargs["maxsplit"].__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_split_indexlike) == [
        b"z",
        b"",
        b"abc",
    ]

    assert sub_indexlike_workload.kwargs == {
        "count": {"type": "indexlike", "value": 2}
    }
    round_tripped_sub_indexlike = workload_from_payload(
        workload_to_payload(sub_indexlike_workload)
    )
    assert round_tripped_sub_indexlike.kwargs == {
        "count": {"type": "indexlike", "value": 2}
    }
    materialized_sub_indexlike_kwargs = round_tripped_sub_indexlike.keyword_arguments()
    assert materialized_sub_indexlike_kwargs["count"].__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_sub_indexlike) == "xxabc"

    assert subn_indexlike_workload.kwargs == {
        "count": {"type": "indexlike", "value": 2}
    }
    round_tripped_subn_indexlike = workload_from_payload(
        workload_to_payload(subn_indexlike_workload)
    )
    assert round_tripped_subn_indexlike.kwargs == {
        "count": {"type": "indexlike", "value": 2}
    }
    materialized_subn_indexlike_kwargs = (
        round_tripped_subn_indexlike.keyword_arguments()
    )
    assert materialized_subn_indexlike_kwargs["count"].__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_subn_indexlike) == (
        b"xxabc",
        2,
    )


def _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
    monkeypatch,
    workload: Workload,
    *,
    expected_result: object,
    expected_field_names: list[str] | tuple[str, ...],
) -> None:
    observed_field_names: list[str] = []
    original_materialize = benchmarks.materialize_numeric_workload_argument

    def record_numeric_materialization(value: Any, *, field_name: str) -> Any:
        observed_field_names.append(field_name)
        return original_materialize(value, field_name=field_name)

    monkeypatch.setattr(
        benchmarks,
        "materialize_numeric_workload_argument",
        record_numeric_materialization,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        assert callback() == expected_result
        assert callback() == expected_result

        assert observed_field_names == list(expected_field_names) * 2
    finally:
        re.purge()


def _run_cpython_pattern_helper_keyword_error_workload(workload: Workload) -> object:
    helper_name = workload.operation.removeprefix("pattern.")
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    kwargs = dict(workload.kwargs)
    positional_keyword_field = _collection_replacement_positional_keyword_field(
        workload
    )

    if workload.operation == "pattern.split":
        args: list[object] = [workload.haystack_payload()]
        if positional_keyword_field == "maxsplit":
            args.append(workload.maxsplit_argument())
        return getattr(compiled_pattern, helper_name)(*args, **kwargs)

    if workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [workload.replacement_payload(), workload.haystack_payload()]
        if positional_keyword_field == "count":
            args.append(workload.count_argument())
        return getattr(compiled_pattern, helper_name)(*args, **kwargs)

    raise AssertionError(
        "unexpected pattern helper keyword-error workload operation "
        f"{workload.operation!r}"
    )


def _pattern_helper_collection_replacement_keyword_error_workload(
    *,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    expected_exception: dict[str, str],
    text_model: str,
) -> Workload:
    return workload_from_payload(
        {
            "manifest_id": "python-benchmark-pattern-collection-replacement-keyword-contract",
            "workload_id": f"{operation}-keyword-error-materialization-contract",
            "bucket": operation.replace("pattern.", "pattern-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "expected_exception": expected_exception,
            "flags": 0,
            "count": count,
            "maxsplit": maxsplit,
            "kwargs": kwargs_payload,
            "text_model": text_model,
            "cache_mode": "warm",
            "timing_scope": "pattern-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


@pytest.mark.parametrize(
    (
        "operation",
        "haystack",
        "kwargs_payload",
        "replacement",
        "text_model",
        "expected_result",
        "expected_field_names",
    ),
    (
        pytest.param(
            "pattern.split",
            "zabcabc",
            {"maxsplit": {"type": "indexlike", "value": 1}},
            None,
            "str",
            ["z", "abc"],
            ["kwargs.maxsplit"],
            id="split-maxsplit-indexlike",
        ),
        pytest.param(
            "pattern.sub",
            "abcabc",
            {"count": {"type": "indexlike", "value": 1}},
            "x",
            "bytes",
            b"xabc",
            ["kwargs.count"],
            id="sub-count-indexlike",
        ),
        pytest.param(
            "pattern.subn",
            "abcabc",
            {"count": {"type": "indexlike", "value": 1}},
            "x",
            "str",
            ("xabc", 1),
            ["kwargs.count"],
            id="subn-count-indexlike",
        ),
        pytest.param(
            "pattern.split",
            "zabcabc",
            {"maxsplit": True},
            None,
            "str",
            ["z", "abc"],
            ["kwargs.maxsplit"],
            id="split-maxsplit-bool",
        ),
        pytest.param(
            "pattern.sub",
            "abcabc",
            {"count": False},
            "x",
            "bytes",
            b"xx",
            ["kwargs.count"],
            id="sub-count-bool",
        ),
        pytest.param(
            "pattern.subn",
            "abcabc",
            {"count": True},
            "x",
            "str",
            ("xabc", 1),
            ["kwargs.count"],
            id="subn-count-bool",
        ),
    ),
)
def test_pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(
    monkeypatch,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    text_model: str,
    expected_result: object,
    expected_field_names: list[str],
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-pattern-collection-replacement-keyword-contract",
            "workload_id": f"{operation}-keyword-materialization-contract",
            "bucket": operation.replace("pattern.", "pattern-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "flags": 0,
            "count": 0,
            "maxsplit": 0,
            "kwargs": kwargs_payload,
            "text_model": text_model,
            "cache_mode": "warm",
            "timing_scope": "pattern-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )
    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result=expected_result,
        expected_field_names=expected_field_names,
    )


@pytest.mark.parametrize(
    (
        "operation",
        "haystack",
        "kwargs_payload",
        "replacement",
        "count",
        "maxsplit",
        "text_model",
        "expected_exception",
        "expected_field_names",
    ),
    (
        pytest.param(
            "pattern.split",
            "abcabc",
            {"maxsplit": 1},
            None,
            0,
            1,
            "str",
            {
                "type": "TypeError",
                "message_substring": "split() takes at most 2 arguments (3 given)",
            },
            ["maxsplit", "kwargs.maxsplit"],
            id="pattern-split-duplicate-maxsplit-keyword",
        ),
        pytest.param(
            "pattern.split",
            "abcabc",
            {"missing": 1},
            None,
            0,
            0,
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "'missing' is an invalid keyword argument for split()",
            },
            ["kwargs.missing"],
            id="pattern-split-unexpected-keyword",
        ),
        pytest.param(
            "pattern.sub",
            "abc",
            {"count": 1},
            "x",
            1,
            0,
            "str",
            {
                "type": "TypeError",
                "message_substring": "sub() takes at most 3 arguments (4 given)",
            },
            ["count", "kwargs.count"],
            id="pattern-sub-duplicate-count-keyword",
        ),
        pytest.param(
            "pattern.sub",
            "abc",
            {"missing": 1},
            "x",
            0,
            0,
            "str",
            {
                "type": "TypeError",
                "message_substring": "'missing' is an invalid keyword argument for sub()",
            },
            ["kwargs.missing"],
            id="pattern-sub-unexpected-keyword",
        ),
        pytest.param(
            "pattern.sub",
            "abc",
            {"missing": 1},
            "x",
            1,
            0,
            "str",
            {
                "type": "TypeError",
                "message_substring": "sub() takes at most 3 arguments (4 given)",
            },
            ["count", "kwargs.missing"],
            id="pattern-sub-unexpected-keyword-after-positional-count",
        ),
        pytest.param(
            "pattern.subn",
            "abc",
            {"count": 1},
            "x",
            1,
            0,
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "subn() takes at most 3 arguments (4 given)",
            },
            ["count", "kwargs.count"],
            id="pattern-subn-duplicate-count-keyword",
        ),
        pytest.param(
            "pattern.subn",
            "abc",
            {"missing": 1},
            "x",
            0,
            0,
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "'missing' is an invalid keyword argument for subn()",
            },
            ["kwargs.missing"],
            id="pattern-subn-unexpected-keyword",
        ),
        pytest.param(
            "pattern.subn",
            "abc",
            {"missing": 1},
            "x",
            1,
            0,
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "subn() takes at most 3 arguments (4 given)",
            },
            ["count", "kwargs.missing"],
            id="pattern-subn-unexpected-keyword-after-positional-count",
        ),
    ),
)
def test_pattern_helper_collection_replacement_keyword_error_callbacks_match_cpython_exceptions(
    monkeypatch,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    text_model: str,
    expected_exception: dict[str, str],
    expected_field_names: list[str],
) -> None:
    workload = _pattern_helper_collection_replacement_keyword_error_workload(
        operation=operation,
        haystack=haystack,
        kwargs_payload=kwargs_payload,
        replacement=replacement,
        count=count,
        maxsplit=maxsplit,
        expected_exception=expected_exception,
        text_model=text_model,
    )
    observed_field_names: list[str] = []
    callback_field_names: list[str] = []
    original_materialize = benchmarks.materialize_numeric_workload_argument

    def record_numeric_materialization(value: Any, *, field_name: str) -> Any:
        observed_field_names.append(field_name)
        return original_materialize(value, field_name=field_name)

    monkeypatch.setattr(
        benchmarks,
        "materialize_numeric_workload_argument",
        record_numeric_materialization,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        for _ in range(2):
            with pytest.raises(TypeError) as expected_error:
                _run_cpython_pattern_helper_keyword_error_workload(workload)
            observed_field_names.clear()
            with pytest.raises(TypeError) as observed_error:
                callback()
            callback_field_names.extend(observed_field_names)

            assert str(observed_error.value) == str(expected_error.value)

        assert callback_field_names == expected_field_names * 2
    finally:
        re.purge()


def _pattern_helper_collection_replacement_wrong_text_model_manifest_payload(
    workload: Workload,
) -> dict[str, object]:
    payload = workload_to_payload(workload)
    return {
        "id": f"{workload.workload_id}-contract",
        **{
            key: value
            for key, value in payload.items()
            if key
            not in {
                "manifest_id",
                "workload_id",
                "warmup_iterations",
                "sample_iterations",
                "timed_samples",
                "smoke",
            }
        },
    }


def _pattern_helper_collection_replacement_wrong_text_model_workloads() -> tuple[Workload, ...]:
    return _selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=_is_collection_replacement_pattern_wrong_text_model_workload,
    )


def _pattern_helper_collection_replacement_wrong_text_model_manifest() -> dict[str, object]:
    return {
        "schema_version": 1,
        "manifest_id": "collection-replacement-boundary",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            _pattern_helper_collection_replacement_wrong_text_model_manifest_payload(
                workload
            )
            for workload in _pattern_helper_collection_replacement_wrong_text_model_workloads()
        ],
    }


def _assert_pattern_helper_collection_replacement_wrong_text_model_payload_round_trip(
    workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if workload.text_model == "str" else bytes
    expected_haystack_type = str if workload.haystack_text_model == "str" else bytes

    assert payload.get("use_compiled_pattern") is None
    assert round_tripped.use_compiled_pattern is False
    assert payload["haystack_text_model"] == workload.haystack_text_model
    assert round_tripped.haystack_text_model == workload.haystack_text_model
    assert payload["expected_exception"] == workload.expected_exception
    assert round_tripped.expected_exception == workload.expected_exception
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_haystack_type)
    if workload.replacement is not None:
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


def _pattern_helper_collection_replacement_wrong_text_model_expected_callback_result(
    workload: Workload,
) -> object:
    if workload.operation == "pattern.subn":
        return ("pattern-result", 0)
    return "pattern-result"


def _pattern_helper_collection_replacement_wrong_text_model_expected_build_calls(
    workload: Workload,
) -> list[tuple[object, ...]]:
    compile_call = ("compile", workload.pattern_payload(), workload.flags)
    if workload.cache_mode == "purged":
        return [compile_call, ("purge",)]
    if workload.cache_mode == "warm":
        return [compile_call]
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"cache mode {workload.cache_mode!r}"
    )


def _pattern_helper_collection_replacement_wrong_text_model_expected_callback_call(
    workload: Workload,
) -> tuple[object, ...]:
    if workload.operation == "pattern.split":
        return (
            "pattern.split",
            workload.haystack_payload(),
            (workload.maxsplit_argument(),),
            {},
        )
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        return (
            workload.operation,
            workload.replacement_payload(),
            workload.haystack_payload(),
            (workload.count_argument(),),
            {},
        )
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {workload.operation!r}"
    )


def _run_cpython_pattern_helper_collection_replacement_wrong_text_model_workload(
    workload: Workload,
) -> object:
    helper_name = workload.operation.removeprefix("pattern.")
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)

    if workload.operation == "pattern.split":
        return getattr(compiled_pattern, helper_name)(
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )

    if workload.operation in {"pattern.sub", "pattern.subn"}:
        return getattr(compiled_pattern, helper_name)(
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )

    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {workload.operation!r}"
    )


def test_standard_benchmark_manifest_preserves_pattern_collection_replacement_wrong_text_model_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = _pattern_helper_collection_replacement_wrong_text_model_workloads()
    manifest = _pattern_helper_collection_replacement_wrong_text_model_manifest()
    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_pattern_collection_replacement_wrong_text_model_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        "pattern-split-on-bytes-string-warm-str",
        "pattern-sub-on-bytes-string-warm-str",
        "pattern-subn-on-str-string-purged-bytes",
    )
    assert tuple(workload.workload_id for workload in workloads) == (
        "pattern-split-on-bytes-string-warm-str-contract",
        "pattern-sub-on-bytes-string-warm-str-contract",
        "pattern-subn-on-str-string-purged-bytes-contract",
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        False
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        workload.haystack_text_model for workload in source_workloads
    ]

    for source_workload, workload in zip(
        source_workloads,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_pattern_helper_collection_replacement_wrong_text_model_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )

        with pytest.raises(TypeError) as expected_error:
            _run_cpython_pattern_helper_collection_replacement_wrong_text_model_workload(
                workload
            )
        with pytest.raises(TypeError) as observed_error:
            run_benchmark_workload_with_cpython(round_tripped)

        assert str(observed_error.value) == str(expected_error.value)


def test_pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases(
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = _pattern_helper_collection_replacement_wrong_text_model_workloads()
    manifest = _pattern_helper_collection_replacement_wrong_text_model_manifest()
    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_pattern_collection_replacement_wrong_text_model_anchor_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    assert tuple(
        workload.workload_id for workload in load_manifest(manifest_path).workloads
    ) == tuple(f"{workload.workload_id}-contract" for workload in source_workloads)
    expected_anchor_case_ids = _definition_anchor_expectations(
        manifest_path,
        {
            "pattern-split-on-bytes-string-warm-str-contract": (
                "workflow-pattern-split-str-pattern-on-bytes-string",
            ),
            "pattern-sub-on-bytes-string-warm-str-contract": (
                "workflow-pattern-sub-str-pattern-on-bytes-string",
            ),
            "pattern-subn-on-str-string-purged-bytes-contract": (
                "workflow-pattern-subn-bytes-pattern-on-str-string",
            ),
        },
    )
    anchor_case_ids = published_case_ids_by_signature(
        _collection_replacement_pattern_wrong_text_model_correctness_case_signature
    )

    assert anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=(
            _collection_replacement_pattern_wrong_text_model_workload_signature
        ),
        include_workload=_is_collection_replacement_pattern_wrong_text_model_workload,
    ) == expected_anchor_case_ids
    assert unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=(
            _collection_replacement_pattern_wrong_text_model_workload_signature
        ),
        include_workload=_is_collection_replacement_pattern_wrong_text_model_workload,
    ) == ()
    assert tuple(
        (pair.workload_id, pair.case_id)
        for pair in expected_anchored_workload_case_pairs(
            manifest_path,
            expected_anchor_case_ids=expected_anchor_case_ids,
            include_workload=_is_collection_replacement_pattern_wrong_text_model_workload,
        )
    ) == (
        (
            "pattern-split-on-bytes-string-warm-str-contract",
            "workflow-pattern-split-str-pattern-on-bytes-string",
        ),
        (
            "pattern-sub-on-bytes-string-warm-str-contract",
            "workflow-pattern-sub-str-pattern-on-bytes-string",
        ),
        (
            "pattern-subn-on-str-string-purged-bytes-contract",
            "workflow-pattern-subn-bytes-pattern-on-str-string",
        ),
    )


@pytest.mark.parametrize(
    "workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _pattern_helper_collection_replacement_wrong_text_model_workloads()
    ),
)
def test_pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time(
    monkeypatch,
    workload: Workload,
) -> None:
    observed_workload_ids: list[str] = []
    original_haystack_payload = benchmarks.Workload.haystack_payload

    def record_haystack_payload(self: Workload) -> object:
        observed_workload_ids.append(self.workload_id)
        return original_haystack_payload(self)

    monkeypatch.setattr(
        benchmarks.Workload,
        "haystack_payload",
        record_haystack_payload,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_workload_ids == []

        with pytest.raises(
            TypeError,
            match=re.escape(str(workload.expected_exception["message_substring"])),
        ):
            callback()

        assert observed_workload_ids == [workload.workload_id]
    finally:
        re.purge()


@pytest.mark.parametrize(
    "workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _pattern_helper_collection_replacement_wrong_text_model_workloads()
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_pattern_helper_collection_replacement_wrong_text_model_workloads(
    workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    _assert_pattern_helper_collection_replacement_wrong_text_model_payload_round_trip(
        workload,
        payload,
        round_tripped,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    (
        "operation",
        "haystack",
        "kwargs_payload",
        "replacement",
        "text_model",
        "expected_result",
        "expected_field_names",
    ),
    (
        pytest.param(
            "module.split",
            "zabczabc",
            {"maxsplit": 1},
            None,
            "bytes",
            [b"z", b"zabc"],
            ["kwargs.maxsplit"],
            id="module-split-maxsplit-int",
        ),
        pytest.param(
            "module.sub",
            "abcabc",
            {"count": 1},
            "x",
            "str",
            "xabc",
            ["kwargs.count"],
            id="module-sub-count-int",
        ),
        pytest.param(
            "module.subn",
            "abcabc",
            {"count": 1},
            "x",
            "bytes",
            (b"xabc", 1),
            ["kwargs.count"],
            id="module-subn-count-int",
        ),
        pytest.param(
            "module.split",
            "zabcabcabc",
            {"maxsplit": {"type": "indexlike", "value": 2}},
            None,
            "bytes",
            [b"z", b"", b"abc"],
            ["kwargs.maxsplit"],
            id="module-split-maxsplit-indexlike",
        ),
        pytest.param(
            "module.sub",
            "abcabcabc",
            {"count": {"type": "indexlike", "value": 2}},
            "x",
            "str",
            "xxabc",
            ["kwargs.count"],
            id="module-sub-count-indexlike",
        ),
        pytest.param(
            "module.subn",
            "abcabcabc",
            {"count": {"type": "indexlike", "value": 2}},
            "x",
            "bytes",
            (b"xxabc", 2),
            ["kwargs.count"],
            id="module-subn-count-indexlike",
        ),
        pytest.param(
            "module.split",
            "zabcabc",
            {"maxsplit": True},
            None,
            "str",
            ["z", "abc"],
            ["kwargs.maxsplit"],
            id="module-split-maxsplit-bool",
        ),
        pytest.param(
            "module.sub",
            "abcabc",
            {"count": False},
            "x",
            "bytes",
            b"xx",
            ["kwargs.count"],
            id="module-sub-count-bool",
        ),
        pytest.param(
            "module.subn",
            "abcabc",
            {"count": True},
            "x",
            "str",
            ("xabc", 1),
            ["kwargs.count"],
            id="module-subn-count-bool",
        ),
    ),
)
def test_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(
    monkeypatch,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    text_model: str,
    expected_result: object,
    expected_field_names: list[str],
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-module-collection-replacement-keyword-contract",
            "workload_id": f"{operation}-keyword-materialization-contract",
            "bucket": operation.replace("module.", "module-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "flags": 0,
            "count": 0,
            "maxsplit": 0,
            "kwargs": kwargs_payload,
            "text_model": text_model,
            "cache_mode": "purged",
            "timing_scope": "module-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )
    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result=expected_result,
        expected_field_names=expected_field_names,
    )


@pytest.mark.parametrize(
    ("operation", "haystack", "text_model"),
    (
        pytest.param(
            "module.search",
            "zAbc",
            "str",
            id="module-search-flags-keyword",
        ),
        pytest.param(
            "module.match",
            "Abc",
            "bytes",
            id="module-match-flags-keyword",
        ),
        pytest.param(
            "module.fullmatch",
            "Abc",
            "str",
            id="module-fullmatch-flags-keyword",
        ),
    ),
)
def test_module_helper_workflow_keyword_flags_materialize_at_callback_time(
    monkeypatch,
    operation: str,
    haystack: str,
    text_model: str,
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-module-workflow-keyword-flags-contract",
            "workload_id": f"{operation}-keyword-flags-materialization-contract",
            "bucket": operation.replace("module.", "module-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "flags": 0,
            "count": 0,
            "maxsplit": 0,
            "kwargs": {"flags": 2},
            "text_model": text_model,
            "cache_mode": "purged",
            "timing_scope": "module-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )
    observed_field_names: list[str] = []
    original_materialize = benchmarks.materialize_numeric_workload_argument

    def record_numeric_materialization(value: Any, *, field_name: str) -> Any:
        observed_field_names.append(field_name)
        return original_materialize(value, field_name=field_name)

    monkeypatch.setattr(
        benchmarks,
        "materialize_numeric_workload_argument",
        record_numeric_materialization,
    )

    helper_name = operation.removeprefix("module.")
    expected_result = getattr(re, helper_name)(
        workload.pattern_payload(),
        workload.haystack_payload(),
        flags=re.IGNORECASE,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        observed_result = callback()

        assert observed_field_names == ["kwargs.flags"]
        assert_match_result_parity(
            "stdlib",
            observed_result,
            expected_result,
            check_regs=True,
        )
    finally:
        re.purge()


@pytest.mark.parametrize(
    (
        "operation",
        "cache_mode",
        "haystack",
        "kwargs_payload",
        "replacement",
        "count",
        "maxsplit",
        "expected_exception",
        "expected_direct_exception",
        "expected_field_names",
    ),
    (
        pytest.param(
            "module.search",
            "warm",
            "abc",
            {"flags": 0},
            None,
            0,
            0,
            {
                "type": "TypeError",
                "message_substring": "multiple values for argument 'flags'",
            },
            lambda workload: re.search(
                workload.pattern_payload(),
                workload.haystack_payload(),
                workload.flags,
                flags=0,
            ),
            ["kwargs.flags"],
            id="module-search-duplicate-flags-keyword",
        ),
        pytest.param(
            "module.fullmatch",
            "purged",
            "abc",
            {"missing": 1},
            None,
            0,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            lambda workload: re.fullmatch(
                workload.pattern_payload(),
                workload.haystack_payload(),
                missing=1,
            ),
            ["kwargs.missing"],
            id="module-fullmatch-unexpected-keyword",
        ),
        pytest.param(
            "module.split",
            "purged",
            "abc",
            {"maxsplit": 1},
            None,
            0,
            1,
            {
                "type": "TypeError",
                "message_substring": "multiple values for argument 'maxsplit'",
            },
            lambda workload: re.split(
                workload.pattern_payload(),
                workload.haystack_payload(),
                workload.maxsplit,
                maxsplit=1,
            ),
            ["maxsplit", "kwargs.maxsplit"],
            id="module-split-duplicate-maxsplit-keyword",
        ),
        pytest.param(
            "module.sub",
            "warm",
            "abc",
            {"count": 1},
            "x",
            1,
            0,
            {
                "type": "TypeError",
                "message_substring": "multiple values for argument 'count'",
            },
            lambda workload: re.sub(
                workload.pattern_payload(),
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
                count=1,
            ),
            ["count", "kwargs.count"],
            id="module-sub-duplicate-count-keyword",
        ),
        pytest.param(
            "module.sub",
            "purged",
            "abc",
            {"missing": 1},
            "x",
            0,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            lambda workload: re.sub(
                workload.pattern_payload(),
                workload.replacement_payload(),
                workload.haystack_payload(),
                missing=1,
            ),
            ["kwargs.missing"],
            id="module-sub-unexpected-keyword",
        ),
    ),
)
def test_module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions(
    monkeypatch,
    operation: str,
    cache_mode: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    expected_exception: dict[str, str],
    expected_direct_exception,
    expected_field_names: list[str],
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-module-workflow-keyword-errors-contract",
            "workload_id": f"{operation}-keyword-error-materialization-contract",
            "bucket": operation.replace("module.", "module-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "expected_exception": expected_exception,
            "flags": 0,
            "count": count,
            "maxsplit": maxsplit,
            "kwargs": kwargs_payload,
            "text_model": "str",
            "cache_mode": cache_mode,
            "timing_scope": "module-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )
    observed_field_names: list[str] = []
    original_materialize = benchmarks.materialize_numeric_workload_argument

    def record_numeric_materialization(value: Any, *, field_name: str) -> Any:
        observed_field_names.append(field_name)
        return original_materialize(value, field_name=field_name)

    monkeypatch.setattr(
        benchmarks,
        "materialize_numeric_workload_argument",
        record_numeric_materialization,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        with pytest.raises(TypeError) as expected_error:
            expected_direct_exception(workload)
        with pytest.raises(TypeError) as observed_error:
            callback()

        assert observed_field_names == expected_field_names
        assert str(observed_error.value) == str(expected_error.value)
    finally:
        re.purge()


def _module_helper_keyword_error_probe_workload(
    *,
    operation: str,
    cache_mode: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    expected_exception: dict[str, str],
) -> Workload:
    return workload_from_payload(
        {
            "manifest_id": "python-benchmark-module-helper-keyword-error-probe-contract",
            "workload_id": f"{operation}-keyword-error-probe-contract",
            "bucket": operation.replace("module.", "module-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": "abc",
            "replacement": replacement,
            "expected_exception": expected_exception,
            "flags": 0,
            "count": count,
            "maxsplit": maxsplit,
            "kwargs": kwargs_payload,
            "text_model": "str",
            "cache_mode": cache_mode,
            "timing_scope": "module-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


@pytest.mark.parametrize(
    (
        "operation",
        "cache_mode",
        "kwargs_payload",
        "replacement",
        "count",
        "maxsplit",
        "expected_exception",
    ),
    (
        pytest.param(
            "module.search",
            "warm",
            {"flags": 0},
            None,
            0,
            0,
            {
                "type": "TypeError",
                "message_substring": "multiple values for argument 'flags'",
            },
            id="module-search-duplicate-flags-keyword",
        ),
        pytest.param(
            "module.fullmatch",
            "warm",
            {"missing": 1},
            None,
            0,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            id="module-fullmatch-unexpected-keyword",
        ),
        pytest.param(
            "module.split",
            "purged",
            {"maxsplit": 1},
            None,
            0,
            1,
            {
                "type": "TypeError",
                "message_substring": "multiple values for argument 'maxsplit'",
            },
            id="module-split-duplicate-maxsplit-keyword",
        ),
        pytest.param(
            "module.sub",
            "warm",
            {"count": 1},
            "x",
            1,
            0,
            {
                "type": "TypeError",
                "message_substring": "multiple values for argument 'count'",
            },
            id="module-sub-duplicate-count-keyword",
        ),
        pytest.param(
            "module.sub",
            "purged",
            {"missing": 1},
            "x",
            0,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            id="module-sub-unexpected-keyword",
        ),
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_module_helper_keyword_error_workloads(
    operation: str,
    cache_mode: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    expected_exception: dict[str, str],
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _module_helper_keyword_error_probe_workload(
        operation=operation,
        cache_mode=cache_mode,
        kwargs_payload=kwargs_payload,
        replacement=replacement,
        count=count,
        maxsplit=maxsplit,
        expected_exception=expected_exception,
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    assert payload["expected_exception"] == expected_exception
    assert round_tripped.expected_exception == expected_exception
    assert payload["kwargs"] == kwargs_payload
    assert round_tripped.kwargs == kwargs_payload

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@dataclass(frozen=True)
class CompiledPatternModuleKeywordCarrierCase:
    id: str
    operation: str
    cache_mode: str
    haystack: str
    kwargs_payload: dict[str, object]
    replacement: object
    text_model: str
    expected_result: object
    expected_field_names: tuple[str, ...]


COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES = (
    CompiledPatternModuleKeywordCarrierCase(
        id="module-split-maxsplit-keyword-purged-str-compiled-pattern",
        operation="module.split",
        cache_mode="purged",
        haystack="zabczabc",
        kwargs_payload={"maxsplit": 1},
        replacement=None,
        text_model="str",
        expected_result=["z", "zabc"],
        expected_field_names=("kwargs.maxsplit",),
    ),
    CompiledPatternModuleKeywordCarrierCase(
        id="module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern",
        operation="module.split",
        cache_mode="purged",
        haystack="zabcabcabc",
        kwargs_payload={"maxsplit": {"type": "indexlike", "value": 2}},
        replacement=None,
        text_model="bytes",
        expected_result=[b"z", b"", b"abc"],
        expected_field_names=("kwargs.maxsplit",),
    ),
    CompiledPatternModuleKeywordCarrierCase(
        id="module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern",
        operation="module.split",
        cache_mode="purged",
        haystack="abcabc",
        kwargs_payload={"maxsplit": False},
        replacement=None,
        text_model="bytes",
        expected_result=[b"", b"", b""],
        expected_field_names=("kwargs.maxsplit",),
    ),
    CompiledPatternModuleKeywordCarrierCase(
        id="module-sub-count-keyword-warm-str-compiled-pattern",
        operation="module.sub",
        cache_mode="warm",
        haystack="abcabc",
        kwargs_payload={"count": 1},
        replacement="x",
        text_model="str",
        expected_result="xabc",
        expected_field_names=("kwargs.count",),
    ),
    CompiledPatternModuleKeywordCarrierCase(
        id="module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern",
        operation="module.sub",
        cache_mode="warm",
        haystack="abcabcabc",
        kwargs_payload={"count": {"type": "indexlike", "value": 2}},
        replacement="x",
        text_model="bytes",
        expected_result=b"xxabc",
        expected_field_names=("kwargs.count",),
    ),
    CompiledPatternModuleKeywordCarrierCase(
        id="module-sub-count-bool-keyword-warm-str-compiled-pattern",
        operation="module.sub",
        cache_mode="warm",
        haystack="abcabc",
        kwargs_payload={"count": True},
        replacement="x",
        text_model="str",
        expected_result="xabc",
        expected_field_names=("kwargs.count",),
    ),
    CompiledPatternModuleKeywordCarrierCase(
        id="module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
        operation="module.sub",
        cache_mode="warm",
        haystack="abcabc",
        kwargs_payload={"count": False},
        replacement="x",
        text_model="str",
        expected_result="xx",
        expected_field_names=("kwargs.count",),
    ),
    CompiledPatternModuleKeywordCarrierCase(
        id="module-subn-count-keyword-purged-bytes-compiled-pattern",
        operation="module.subn",
        cache_mode="purged",
        haystack="abcabc",
        kwargs_payload={"count": 1},
        replacement="x",
        text_model="bytes",
        expected_result=(b"xabc", 1),
        expected_field_names=("kwargs.count",),
    ),
    CompiledPatternModuleKeywordCarrierCase(
        id="module-subn-count-indexlike-keyword-purged-str-compiled-pattern",
        operation="module.subn",
        cache_mode="purged",
        haystack="abcabcabc",
        kwargs_payload={"count": {"type": "indexlike", "value": 2}},
        replacement="x",
        text_model="str",
        expected_result=("xxabc", 2),
        expected_field_names=("kwargs.count",),
    ),
    CompiledPatternModuleKeywordCarrierCase(
        id="module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
        operation="module.subn",
        cache_mode="purged",
        haystack="abcabc",
        kwargs_payload={"count": False},
        replacement="x",
        text_model="bytes",
        expected_result=(b"xx", 2),
        expected_field_names=("kwargs.count",),
    ),
    CompiledPatternModuleKeywordCarrierCase(
        id="module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
        operation="module.subn",
        cache_mode="purged",
        haystack="abcabc",
        kwargs_payload={"count": True},
        replacement="x",
        text_model="bytes",
        expected_result=(b"xabc", 1),
        expected_field_names=("kwargs.count",),
    ),
)


def _compiled_pattern_module_helper_keyword_manifest_payload(
    case: CompiledPatternModuleKeywordCarrierCase,
) -> dict[str, object]:
    return {
        "id": f"{case.id}-contract",
        "bucket": case.operation.replace("module.", "module-"),
        "family": "module",
        "operation": case.operation,
        "pattern": "abc",
        "haystack": case.haystack,
        "replacement": case.replacement,
        "flags": 0,
        "use_compiled_pattern": True,
        "count": 0,
        "maxsplit": 0,
        "kwargs": case.kwargs_payload,
        "text_model": case.text_model,
        "cache_mode": case.cache_mode,
        "timing_scope": "module-helper-call",
        "notes": [
            "Ensures benchmark manifests keep compiled-pattern-first-argument "
            "collection/replacement keyword carriers unresolved until helper "
            "invocation."
        ],
    }


def _compiled_pattern_module_helper_keyword_workload(
    case: CompiledPatternModuleKeywordCarrierCase,
) -> Workload:
    manifest_payload = _compiled_pattern_module_helper_keyword_manifest_payload(case)
    return workload_from_payload(
        {
            "manifest_id": (
                "python-benchmark-compiled-pattern-module-helper-keyword-contract"
            ),
            "workload_id": str(manifest_payload["id"]),
            **{key: value for key, value in manifest_payload.items() if key != "id"},
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


def _compiled_pattern_module_keyword_carrier_case(
    case_id: str,
) -> CompiledPatternModuleKeywordCarrierCase:
    for case in COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES:
        if case.id == case_id:
            return case
    raise AssertionError(f"unknown compiled-pattern module keyword carrier case {case_id!r}")


def _assert_compiled_pattern_module_helper_keyword_payload_round_trip(
    case: CompiledPatternModuleKeywordCarrierCase,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["kwargs"] == case.kwargs_payload
    assert round_tripped.kwargs == case.kwargs_payload
    for name, value in case.kwargs_payload.items():
        if type(value) is bool:
            assert type(round_tripped.kwargs[name]) is bool


def test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements() -> None:
    assert {
        (
            case.id,
            case.operation,
            case.text_model,
            case.kwargs_payload["count"],
            case.expected_result,
        )
        for case in COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES
        if case.operation in {"module.sub", "module.subn"}
        and type(case.kwargs_payload.get("count")) is bool
    } == {
        (
            "module-sub-count-bool-keyword-warm-str-compiled-pattern",
            "module.sub",
            "str",
            True,
            "xabc",
        ),
        (
            "module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
            "module.sub",
            "str",
            False,
            "xx",
        ),
        (
            "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
            "module.subn",
            "bytes",
            False,
            (b"xx", 2),
        ),
        (
            "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
            "module.subn",
            "bytes",
            True,
            (b"xabc", 1),
        ),
    }


def test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest = {
        "schema_version": 1,
        "manifest_id": (
            "python-benchmark-compiled-pattern-collection-replacement-keyword-contract"
        ),
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            _compiled_pattern_module_helper_keyword_manifest_payload(case)
            for case in COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES
        ],
    }

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_collection_replacement_keyword_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES)

    for case, workload in zip(
        COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_compiled_pattern_module_helper_keyword_payload_round_trip(
            case,
            payload,
            round_tripped,
        )
        assert run_benchmark_workload_with_cpython(round_tripped) == case.expected_result


@pytest.mark.parametrize(
    "case",
    tuple(
        pytest.param(case, id=case.id)
        for case in COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES
    ),
)
def test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(
    monkeypatch,
    case: CompiledPatternModuleKeywordCarrierCase,
) -> None:
    workload = _compiled_pattern_module_helper_keyword_workload(case)
    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result=case.expected_result,
        expected_field_names=case.expected_field_names,
    )


@pytest.mark.parametrize(
    "case",
    tuple(
        pytest.param(case, id=case.id)
        for case in COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_workloads(
    case: CompiledPatternModuleKeywordCarrierCase,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _compiled_pattern_module_helper_keyword_workload(case)
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    _assert_compiled_pattern_module_helper_keyword_payload_round_trip(
        case,
        payload,
        round_tripped,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    ("case", "expected_build_calls", "expected_callback_call"),
    (
        pytest.param(
            _compiled_pattern_module_keyword_carrier_case(
                "module-split-maxsplit-keyword-purged-str-compiled-pattern"
            ),
            [("compile", "abc", 0), ("purge",)],
            ("module.split", "zabczabc", 0, 0, {"maxsplit": 1}),
            id="module-split-maxsplit-keyword-purged-str-compiled-pattern",
        ),
        pytest.param(
            _compiled_pattern_module_keyword_carrier_case(
                "module-sub-count-keyword-warm-str-compiled-pattern"
            ),
            [("compile", "abc", 0)],
            ("module.sub", "x", "abcabc", 0, 0, {"count": 1}),
            id="module-sub-count-keyword-warm-str-compiled-pattern",
        ),
        pytest.param(
            _compiled_pattern_module_keyword_carrier_case(
                "module-subn-count-keyword-purged-bytes-compiled-pattern"
            ),
            [("compile", b"abc", 0), ("purge",)],
            ("module.subn", b"x", b"abcabc", 0, 0, {"count": 1}),
            id="module-subn-count-keyword-purged-bytes-compiled-pattern",
        ),
    ),
)
def test_compiled_pattern_module_helper_keyword_callbacks_precompile_first_argument_before_timing(
    case: CompiledPatternModuleKeywordCarrierCase,
    expected_build_calls: list[tuple[object, ...]],
    expected_callback_call: tuple[object, ...],
) -> None:
    module = _RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _compiled_pattern_module_helper_keyword_workload(case),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() in {"module-result", ("module-result", 0)}

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]


def _compiled_pattern_module_collection_replacement_success_manifest_payload(
    source_workload: Workload,
) -> dict[str, object]:
    payload = workload_to_payload(source_workload)
    return {
        "id": f"{source_workload.workload_id}-contract",
        **{
            key: value
            for key, value in payload.items()
            if key
            not in {
                "manifest_id",
                "workload_id",
                "warmup_iterations",
                "sample_iterations",
                "timed_samples",
                "notes",
                "smoke",
                "categories",
                "syntax_features",
                "expected_exception",
                "haystack_text_model",
            }
        },
        "timing_scope": "module-helper-call",
        "notes": [
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            "successful collection/replacement rows unresolved until helper invocation."
        ],
    }


def _compiled_pattern_module_collection_replacement_success_workload(
    source_workload: Workload,
) -> Workload:
    manifest_payload = _compiled_pattern_module_collection_replacement_success_manifest_payload(
        source_workload
    )
    return workload_from_payload(
        {
            "manifest_id": "collection-replacement-boundary",
            "workload_id": str(manifest_payload["id"]),
            **{key: value for key, value in manifest_payload.items() if key != "id"},
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


def _compiled_pattern_module_collection_replacement_success_source_workloads() -> tuple[Workload, ...]:
    return _selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=_is_collection_replacement_compiled_pattern_success_workload,
    )


def _compiled_pattern_module_collection_replacement_success_manifest(
    source_workloads: tuple[Workload, ...],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "manifest_id": "collection-replacement-boundary",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            _compiled_pattern_module_collection_replacement_success_manifest_payload(
                workload
            )
            for workload in source_workloads
        ],
    }


def _assert_compiled_pattern_module_collection_replacement_success_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["count"] == source_workload.count
    assert round_tripped.count == source_workload.count
    assert payload["maxsplit"] == source_workload.maxsplit
    assert round_tripped.maxsplit == source_workload.maxsplit
    assert payload.get("expected_exception") is None
    assert round_tripped.expected_exception is None
    assert payload.get("haystack_text_model") is None
    assert round_tripped.haystack_text_model is None
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_text_type)
    if source_workload.replacement is not None:
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


def _compiled_pattern_module_collection_replacement_success_expected_callback_result(
    source_workload: Workload,
) -> object:
    if source_workload.operation == "module.subn":
        return ("module-result", 0)
    if source_workload.operation == "module.finditer":
        return ["module-finditer-result"]
    return "module-result"


def _compiled_pattern_module_collection_replacement_success_expected_build_calls(
    source_workload: Workload,
) -> list[tuple[object, ...]]:
    compile_call = ("compile", source_workload.pattern_payload(), source_workload.flags)
    if source_workload.cache_mode == "purged":
        return [compile_call, ("purge",)]
    if source_workload.cache_mode == "warm":
        return [compile_call]
    raise AssertionError(
        "unexpected compiled-pattern collection/replacement success workload "
        f"cache mode {source_workload.cache_mode!r}"
    )


def _compiled_pattern_module_collection_replacement_success_expected_callback_call(
    source_workload: Workload,
) -> tuple[object, ...]:
    if source_workload.operation == "module.split":
        return (
            source_workload.operation,
            source_workload.haystack_payload(),
            source_workload.maxsplit_argument(),
            source_workload.flags,
            {},
        )
    if source_workload.operation in {"module.findall", "module.finditer"}:
        return (
            source_workload.operation,
            source_workload.haystack_payload(),
            source_workload.flags,
        )
    if source_workload.operation in {"module.sub", "module.subn"}:
        return (
            source_workload.operation,
            source_workload.replacement_payload(),
            source_workload.haystack_payload(),
            source_workload.count_argument(),
            source_workload.flags,
            {},
        )
    raise AssertionError(
        "unexpected compiled-pattern collection/replacement success workload "
        f"operation {source_workload.operation!r}"
    )


def _run_cpython_compiled_pattern_module_collection_replacement_success_workload(
    workload: Workload,
) -> object:
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    if workload.operation == "module.split":
        return re.split(
            compiled_pattern,
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )
    if workload.operation == "module.findall":
        return re.findall(
            compiled_pattern,
            workload.haystack_payload(),
            workload.flags,
        )
    if workload.operation == "module.finditer":
        return list(
            re.finditer(
                compiled_pattern,
                workload.haystack_payload(),
                workload.flags,
            )
        )
    if workload.operation == "module.sub":
        return re.sub(
            compiled_pattern,
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
    if workload.operation == "module.subn":
        return re.subn(
            compiled_pattern,
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
    raise AssertionError(
        "unexpected compiled-pattern collection/replacement success workload "
        f"operation {workload.operation!r}"
    )


def test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = (
        _compiled_pattern_module_collection_replacement_success_source_workloads()
    )
    manifest = _compiled_pattern_module_collection_replacement_success_manifest(
        source_workloads
    )

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_collection_replacement_success_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        "module-split-literal-warm-str-compiled-pattern",
        "module-findall-literal-purged-bytes-compiled-pattern",
        "module-finditer-literal-warm-str-compiled-pattern",
        "module-sub-literal-warm-str-compiled-pattern",
        "module-subn-literal-purged-bytes-compiled-pattern",
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload.workload_id}-contract" for workload in source_workloads
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        None
    ] * len(source_workloads)

    for source_workload, workload in zip(
        source_workloads,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_compiled_pattern_module_collection_replacement_success_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )
        assert_benchmark_workload_matches_expected_result(
            round_tripped,
            _run_cpython_compiled_pattern_module_collection_replacement_success_workload(
                workload
            ),
        )


def test_compiled_pattern_module_collection_replacement_success_rows_stay_anchored_to_published_correctness_cases(
    tmp_path: pathlib.Path,
) -> None:
    manifest = _compiled_pattern_module_collection_replacement_success_manifest(
        _compiled_pattern_module_collection_replacement_success_source_workloads()
    )

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_collection_replacement_success_anchor_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    expected_anchor_case_ids = _definition_anchor_expectations(
        manifest_path,
        {
            "module-split-literal-warm-str-compiled-pattern-contract": (
                "workflow-module-split-str-compiled-pattern",
            ),
            "module-findall-literal-purged-bytes-compiled-pattern-contract": (
                "workflow-module-findall-bytes-compiled-pattern",
            ),
            "module-finditer-literal-warm-str-compiled-pattern-contract": (
                "workflow-module-finditer-str-compiled-pattern",
            ),
            "module-sub-literal-warm-str-compiled-pattern-contract": (
                "workflow-module-sub-str-compiled-pattern",
            ),
            "module-subn-literal-purged-bytes-compiled-pattern-contract": (
                "workflow-module-subn-bytes-compiled-pattern",
            ),
        },
    )
    anchor_case_ids = published_case_ids_by_signature(
        _collection_replacement_compiled_pattern_success_correctness_case_signature
    )

    assert anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=(
            _collection_replacement_compiled_pattern_success_workload_signature
        ),
        include_workload=_is_collection_replacement_compiled_pattern_success_workload,
    ) == expected_anchor_case_ids
    assert unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=(
            _collection_replacement_compiled_pattern_success_workload_signature
        ),
        include_workload=_is_collection_replacement_compiled_pattern_success_workload,
    ) == ()
    assert tuple(
        (pair.workload_id, pair.case_id)
        for pair in expected_anchored_workload_case_pairs(
            manifest_path,
            expected_anchor_case_ids=expected_anchor_case_ids,
            include_workload=_is_collection_replacement_compiled_pattern_success_workload,
        )
    ) == (
        (
            "module-split-literal-warm-str-compiled-pattern-contract",
            "workflow-module-split-str-compiled-pattern",
        ),
        (
            "module-findall-literal-purged-bytes-compiled-pattern-contract",
            "workflow-module-findall-bytes-compiled-pattern",
        ),
        (
            "module-finditer-literal-warm-str-compiled-pattern-contract",
            "workflow-module-finditer-str-compiled-pattern",
        ),
        (
            "module-sub-literal-warm-str-compiled-pattern-contract",
            "workflow-module-sub-str-compiled-pattern",
        ),
        (
            "module-subn-literal-purged-bytes-compiled-pattern-contract",
            "workflow-module-subn-bytes-compiled-pattern",
        ),
    )


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _compiled_pattern_module_collection_replacement_success_source_workloads()
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _compiled_pattern_module_collection_replacement_success_workload(
        source_workload
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    _assert_compiled_pattern_module_collection_replacement_success_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _compiled_pattern_module_collection_replacement_success_source_workloads()
    ),
)
def test_compiled_pattern_module_collection_replacement_success_callbacks_precompile_first_argument_before_timing(
    source_workload: Workload,
) -> None:
    expected_build_calls = (
        _compiled_pattern_module_collection_replacement_success_expected_build_calls(
            source_workload
        )
    )
    expected_callback_call = (
        _compiled_pattern_module_collection_replacement_success_expected_callback_call(
            source_workload
        )
    )
    module = _RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _compiled_pattern_module_collection_replacement_success_workload(
            source_workload
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == (
        _compiled_pattern_module_collection_replacement_success_expected_callback_result(
            source_workload
        )
    )

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]


def _compiled_pattern_module_compile_success_manifest_payload(
    source_workload: Workload,
) -> dict[str, object]:
    payload = workload_to_payload(source_workload)
    return {
        "id": f"{source_workload.workload_id}-contract",
        **{
            key: value
            for key, value in payload.items()
            if key
            not in {
                "manifest_id",
                "workload_id",
                "warmup_iterations",
                "sample_iterations",
                "timed_samples",
                "notes",
                "smoke",
            }
        },
        "timing_scope": "module-helper-call",
        "notes": [
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            "module.compile rows unresolved until helper invocation."
        ],
    }


def _compiled_pattern_module_compile_success_workload(
    source_workload: Workload,
) -> Workload:
    manifest_payload = _compiled_pattern_module_compile_success_manifest_payload(
        source_workload
    )
    return workload_from_payload(
        {
            "manifest_id": "module-boundary",
            "workload_id": str(manifest_payload["id"]),
            **{key: value for key, value in manifest_payload.items() if key != "id"},
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


def _compiled_pattern_module_compile_success_source_workloads() -> tuple[Workload, ...]:
    literal_workloads = _selected_manifest_workloads(
        MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload=_is_module_workflow_compiled_pattern_compile_literal_success_workload,
    )
    named_group_workloads = _selected_manifest_workloads(
        MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload=_is_module_workflow_compiled_pattern_compile_named_group_success_workload,
    )
    return (*literal_workloads, *named_group_workloads)


def _compiled_pattern_module_compile_success_manifest(
    source_workloads: tuple[Workload, ...],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "manifest_id": "module-boundary",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            _compiled_pattern_module_compile_success_manifest_payload(workload)
            for workload in source_workloads
        ],
    }


def _assert_compiled_pattern_module_compile_success_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["flags"] == source_workload.flags
    assert round_tripped.flags == source_workload.flags
    assert payload.get("expected_exception") == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert payload.get("haystack_text_model") == source_workload.haystack_text_model
    assert round_tripped.haystack_text_model == source_workload.haystack_text_model
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)


def _run_cpython_compiled_pattern_module_compile_success_workload(
    workload: Workload,
) -> object:
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    return re.compile(compiled_pattern, workload.flags)


def _compiled_pattern_module_compile_success_expected_build_calls(
    source_workload: Workload,
) -> list[tuple[object, ...]]:
    build_calls: list[tuple[object, ...]] = [
        (
            "compile",
            source_workload.pattern_payload(),
            source_workload.flags,
        )
    ]
    if source_workload.cache_mode == "purged":
        build_calls.append(("purge",))
    return build_calls


def test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = _compiled_pattern_module_compile_success_source_workloads()
    manifest = _compiled_pattern_module_compile_success_manifest(source_workloads)

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_module_compile_success_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        "module-compile-literal-warm-str-compiled-pattern",
        "module-compile-literal-purged-bytes-compiled-pattern",
        "module-compile-named-group-warm-str-compiled-pattern",
        "module-compile-named-group-purged-bytes-compiled-pattern",
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload.workload_id}-contract" for workload in source_workloads
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        workload.haystack_text_model for workload in source_workloads
    ]

    for source_workload, workload in zip(
        source_workloads,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_compiled_pattern_module_compile_success_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )
        assert_benchmark_workload_matches_expected_result(
            round_tripped,
            _run_cpython_compiled_pattern_module_compile_success_workload(workload),
        )


def test_compiled_pattern_module_compile_success_rows_stay_anchored_to_published_correctness_cases(
    tmp_path: pathlib.Path,
) -> None:
    manifest = _compiled_pattern_module_compile_success_manifest(
        _compiled_pattern_module_compile_success_source_workloads()
    )

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_module_compile_success_anchor_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    expected_anchor_case_ids = _definition_anchor_expectations(
        manifest_path,
        {
            "module-compile-literal-warm-str-compiled-pattern-contract": (
                "workflow-module-compile-str-compiled-pattern",
            ),
            "module-compile-literal-purged-bytes-compiled-pattern-contract": (
                "workflow-module-compile-bytes-compiled-pattern",
            ),
            "module-compile-named-group-warm-str-compiled-pattern-contract": (
                "workflow-module-compile-str-compiled-pattern-named-group",
            ),
            "module-compile-named-group-purged-bytes-compiled-pattern-contract": (
                "workflow-module-compile-bytes-compiled-pattern-named-group",
            ),
        },
    )
    anchor_case_ids = published_case_ids_by_signature(
        _module_workflow_compiled_pattern_compile_correctness_case_signature
    )

    assert anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=_module_workflow_compiled_pattern_compile_workload_signature,
        include_workload=_is_module_workflow_compiled_pattern_compile_workload,
    ) == expected_anchor_case_ids
    assert unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=_module_workflow_compiled_pattern_compile_workload_signature,
        include_workload=_is_module_workflow_compiled_pattern_compile_workload,
    ) == ()
    assert tuple(
        (pair.workload_id, pair.case_id)
        for pair in expected_anchored_workload_case_pairs(
            manifest_path,
            expected_anchor_case_ids=expected_anchor_case_ids,
            include_workload=_is_module_workflow_compiled_pattern_compile_workload,
        )
    ) == (
        (
            "module-compile-literal-warm-str-compiled-pattern-contract",
            "workflow-module-compile-str-compiled-pattern",
        ),
        (
            "module-compile-literal-purged-bytes-compiled-pattern-contract",
            "workflow-module-compile-bytes-compiled-pattern",
        ),
        (
            "module-compile-named-group-warm-str-compiled-pattern-contract",
            "workflow-module-compile-str-compiled-pattern-named-group",
        ),
        (
            "module-compile-named-group-purged-bytes-compiled-pattern-contract",
            "workflow-module-compile-bytes-compiled-pattern-named-group",
        ),
    )


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _compiled_pattern_module_compile_success_source_workloads()
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _compiled_pattern_module_compile_success_workload(source_workload)
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    _assert_compiled_pattern_module_compile_success_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _compiled_pattern_module_compile_success_source_workloads()
    ),
)
def test_compiled_pattern_module_compile_success_callbacks_precompile_first_argument_before_timing(
    source_workload: Workload,
) -> None:
    expected_build_calls = _compiled_pattern_module_compile_success_expected_build_calls(
        source_workload
    )
    module = _RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _compiled_pattern_module_compile_success_workload(source_workload),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1

    compiled_pattern = module.compiled_patterns[0]
    assert callback() is compiled_pattern

    last_call = module.calls[-1]
    assert last_call[0] == "compile"
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == (source_workload.flags,)


@dataclass(frozen=True)
class CompiledPatternModuleCompileKeywordCase:
    id: str
    cache_mode: str
    text_model: str
    kwargs_payload: dict[str, object]
    pattern: str = "abc"
    flags: int = 0
    expected_field_names: tuple[str, ...] = ("kwargs.flags",)
    expected_exception: dict[str, str] | None = None


@dataclass(frozen=True)
class CompiledPatternModuleCompileKeywordCaseGroup:
    group_id: str
    keyword_signature: tuple[tuple[str, str, object], ...]
    allowed_patterns: tuple[str, ...]
    cases: tuple[CompiledPatternModuleCompileKeywordCase, ...]
    contract_filename: str
    anchor_contract_filename: str
    expected_anchor_pairs: tuple[tuple[str, str], ...]
    expected_exception: dict[str, str] | None = None

    def correctness_case_signature(self, case: Any) -> tuple[Any, ...] | None:
        return _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
            case,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
        )

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        return _module_workflow_compiled_pattern_compile_keyword_workload_signature(
            workload,
            keyword_label=self.group_id,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            expected_exception=self.expected_exception,
        )

    def include_workload(self, workload: Any) -> bool:
        return _is_module_workflow_compiled_pattern_compile_keyword_workload(
            workload,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            expected_exception=self.expected_exception,
        )


COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASES = (
    CompiledPatternModuleCompileKeywordCase(
        id="module-compile-flags-int-zero-warm-str-compiled-pattern",
        cache_mode="warm",
        text_model="str",
        kwargs_payload={"flags": 0},
    ),
    CompiledPatternModuleCompileKeywordCase(
        id="module-compile-flags-int-zero-purged-bytes-compiled-pattern",
        cache_mode="purged",
        text_model="bytes",
        kwargs_payload={"flags": 0},
    ),
)

COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_CASES = (
    CompiledPatternModuleCompileKeywordCase(
        id="module-compile-flags-int-zero-warm-str-compiled-pattern-named-group",
        cache_mode="warm",
        text_model="str",
        kwargs_payload={"flags": 0},
        pattern="(?P<word>abc)",
    ),
    CompiledPatternModuleCompileKeywordCase(
        id="module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group",
        cache_mode="purged",
        text_model="bytes",
        kwargs_payload={"flags": 0},
        pattern="(?P<word>abc)",
    ),
)

COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_CASES = (
    CompiledPatternModuleCompileKeywordCase(
        id="module-compile-flags-bool-false-warm-str-compiled-pattern",
        cache_mode="warm",
        text_model="str",
        kwargs_payload={"flags": False},
    ),
    CompiledPatternModuleCompileKeywordCase(
        id="module-compile-flags-bool-false-purged-bytes-compiled-pattern",
        cache_mode="purged",
        text_model="bytes",
        kwargs_payload={"flags": False},
    ),
)

COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_NAMED_GROUP_KEYWORD_CASES = (
    CompiledPatternModuleCompileKeywordCase(
        id="module-compile-flags-bool-false-warm-str-compiled-pattern-named-group",
        cache_mode="warm",
        text_model="str",
        kwargs_payload={"flags": False},
        pattern="(?P<word>abc)",
    ),
    CompiledPatternModuleCompileKeywordCase(
        id="module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group",
        cache_mode="purged",
        text_model="bytes",
        kwargs_payload={"flags": False},
        pattern="(?P<word>abc)",
    ),
)

COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_CASES = (
    CompiledPatternModuleCompileKeywordCase(
        id="module-compile-flags-ignorecase-warm-str-compiled-pattern",
        cache_mode="warm",
        text_model="str",
        kwargs_payload={"flags": int(re.IGNORECASE)},
        expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
    ),
    CompiledPatternModuleCompileKeywordCase(
        id="module-compile-flags-ignorecase-purged-bytes-compiled-pattern",
        cache_mode="purged",
        text_model="bytes",
        kwargs_payload={"flags": int(re.IGNORECASE)},
        expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
    ),
)

COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_NAMED_GROUP_KEYWORD_CASES = (
    CompiledPatternModuleCompileKeywordCase(
        id="module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group",
        cache_mode="warm",
        text_model="str",
        pattern="(?P<word>abc)",
        kwargs_payload={"flags": int(re.IGNORECASE)},
        expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
    ),
    CompiledPatternModuleCompileKeywordCase(
        id="module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group",
        cache_mode="purged",
        text_model="bytes",
        pattern="(?P<word>abc)",
        kwargs_payload={"flags": int(re.IGNORECASE)},
        expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
    ),
)

COMPILED_PATTERN_MODULE_COMPILE_ALL_KEYWORD_CASES = (
    *COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASES,
    *COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_CASES,
    *COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_CASES,
    *COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_NAMED_GROUP_KEYWORD_CASES,
    *COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_CASES,
    *COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_NAMED_GROUP_KEYWORD_CASES,
)

COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS = (
    CompiledPatternModuleCompileKeywordCaseGroup(
        group_id="int-zero",
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
        cases=COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASES,
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-int-zero-warm-str-compiled-pattern-contract",
                "workflow-module-compile-flags-int-zero-str-compiled-pattern",
            ),
            (
                "module-compile-flags-int-zero-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-flags-int-zero-bytes-compiled-pattern",
            ),
        ),
    ),
    CompiledPatternModuleCompileKeywordCaseGroup(
        group_id="int-zero-named-group",
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
        cases=COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_CASES,
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_named_group_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_named_group_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group",
            ),
            (
                "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-int-zero-bytes-compiled-pattern-named-group",
            ),
        ),
    ),
    CompiledPatternModuleCompileKeywordCaseGroup(
        group_id="bool-false",
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
        cases=COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_CASES,
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_bool_false_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_bool_false_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-bool-false-warm-str-compiled-pattern-contract",
                "workflow-module-compile-flags-bool-false-str-compiled-pattern",
            ),
            (
                "module-compile-flags-bool-false-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-flags-bool-false-bytes-compiled-pattern",
            ),
        ),
    ),
    CompiledPatternModuleCompileKeywordCaseGroup(
        group_id="bool-false-named-group",
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
        cases=COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_NAMED_GROUP_KEYWORD_CASES,
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_bool_false_named_group_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_bool_false_named_group_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-bool-false-str-compiled-pattern-named-group",
            ),
            (
                "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-bool-false-bytes-compiled-pattern-named-group",
            ),
        ),
    ),
    CompiledPatternModuleCompileKeywordCaseGroup(
        group_id="ignorecase",
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
        cases=COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_CASES,
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_ignorecase_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_ignorecase_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-ignorecase-warm-str-compiled-pattern-contract",
                "workflow-module-compile-flags-ignorecase-str-compiled-pattern",
            ),
            (
                "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern",
            ),
        ),
        expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
    ),
    CompiledPatternModuleCompileKeywordCaseGroup(
        group_id="ignorecase-named-group",
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
        cases=COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_NAMED_GROUP_KEYWORD_CASES,
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_ignorecase_named_group_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_ignorecase_named_group_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-ignorecase-str-compiled-pattern-named-group",
            ),
            (
                "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group",
            ),
        ),
        expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
    ),
)


def _compiled_pattern_module_compile_keyword_manifest_payload(
    case: CompiledPatternModuleCompileKeywordCase,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": f"{case.id}-contract",
        "bucket": "module-compile",
        "family": "module",
        "operation": "module.compile",
        "pattern": case.pattern,
        "flags": case.flags,
        "use_compiled_pattern": True,
        "kwargs": case.kwargs_payload,
        "text_model": case.text_model,
        "cache_mode": case.cache_mode,
        "timing_scope": "module-helper-call",
        "notes": [
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            "module.compile flags= keyword rows unresolved until helper invocation."
        ],
    }
    if case.expected_exception is not None:
        payload["expected_exception"] = case.expected_exception
    return payload


def _compiled_pattern_module_compile_keyword_workload(
    case: CompiledPatternModuleCompileKeywordCase,
) -> Workload:
    manifest_payload = _compiled_pattern_module_compile_keyword_manifest_payload(case)
    return workload_from_payload(
        {
            "manifest_id": "module-boundary",
            "workload_id": str(manifest_payload["id"]),
            **{key: value for key, value in manifest_payload.items() if key != "id"},
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


def _assert_compiled_pattern_module_compile_keyword_payload_round_trip(
    case: CompiledPatternModuleCompileKeywordCase,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if case.text_model == "str" else bytes
    expected_keyword_value = case.kwargs_payload["flags"]

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["flags"] == case.flags
    assert round_tripped.flags == case.flags
    assert payload["kwargs"] == case.kwargs_payload
    assert round_tripped.kwargs == case.kwargs_payload
    assert type(round_tripped.kwargs["flags"]) is type(expected_keyword_value)
    assert payload.get("expected_exception") == case.expected_exception
    assert round_tripped.expected_exception == case.expected_exception
    assert payload.get("haystack_text_model") is None
    assert round_tripped.haystack_text_model is None
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)


def _run_cpython_compiled_pattern_module_compile_keyword_workload(
    workload: Workload,
) -> object:
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    return re.compile(compiled_pattern, **workload.keyword_arguments())


def _compiled_pattern_module_compile_keyword_manifest(
    cases: tuple[CompiledPatternModuleCompileKeywordCase, ...],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "manifest_id": "module-boundary",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            _compiled_pattern_module_compile_keyword_manifest_payload(case)
            for case in cases
        ],
    }


def _compiled_pattern_module_compile_keyword_expected_build_calls(
    case: CompiledPatternModuleCompileKeywordCase,
) -> list[tuple[object, ...]]:
    workload = _compiled_pattern_module_compile_keyword_workload(case)
    build_calls: list[tuple[object, ...]] = [
        ("compile", workload.pattern_payload(), workload.flags)
    ]
    if case.cache_mode == "purged":
        build_calls.append(("purge",))
    return build_calls


def _expected_exception_instance(
    expected_exception: dict[str, str],
) -> Exception:
    exception_type = {
        "TypeError": TypeError,
        "ValueError": ValueError,
    }[expected_exception["type"]]
    return exception_type(expected_exception["message_substring"])


@pytest.mark.parametrize(
    "case_group",
    COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS,
    ids=lambda case_group: case_group.group_id,
)
def test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_keyword_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
    case_group: CompiledPatternModuleCompileKeywordCaseGroup,
) -> None:
    manifest = _compiled_pattern_module_compile_keyword_manifest(case_group.cases)
    manifest_path = _write_test_manifest(
        tmp_path,
        case_group.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(case_group.cases)

    for case, workload in zip(
        case_group.cases,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_compiled_pattern_module_compile_keyword_payload_round_trip(
            case,
            payload,
            round_tripped,
        )
        if case.expected_exception is None:
            assert_benchmark_workload_matches_expected_result(
                round_tripped,
                _run_cpython_compiled_pattern_module_compile_keyword_workload(
                    workload
                ),
            )
            continue

        expected_exception = _expected_exception_instance(case.expected_exception)
        with pytest.raises(
            type(expected_exception),
            match=case.expected_exception["message_substring"],
        ) as expected_error:
            _run_cpython_compiled_pattern_module_compile_keyword_workload(workload)
        with pytest.raises(type(expected_error.value)) as observed_error:
            run_benchmark_workload_with_cpython(round_tripped)
        assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(
    "case_group",
    COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS,
    ids=lambda case_group: case_group.group_id,
)
def test_compiled_pattern_module_compile_keyword_rows_stay_anchored_to_published_correctness_cases(
    tmp_path: pathlib.Path,
    case_group: CompiledPatternModuleCompileKeywordCaseGroup,
) -> None:
    manifest = _compiled_pattern_module_compile_keyword_manifest(case_group.cases)
    manifest_path = _write_test_manifest(
        tmp_path,
        case_group.anchor_contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    expected_anchor_case_ids = _definition_anchor_expectations(
        manifest_path,
        {
            workload_id: (case_id,)
            for workload_id, case_id in case_group.expected_anchor_pairs
        },
    )
    anchor_case_ids = published_case_ids_by_signature(
        case_group.correctness_case_signature
    )

    assert anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=case_group.workload_signature,
        include_workload=case_group.include_workload,
    ) == expected_anchor_case_ids
    assert unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=case_group.workload_signature,
        include_workload=case_group.include_workload,
    ) == ()
    assert tuple(
        (pair.workload_id, pair.case_id)
        for pair in expected_anchored_workload_case_pairs(
            manifest_path,
            expected_anchor_case_ids=expected_anchor_case_ids,
            include_workload=case_group.include_workload,
        )
    ) == case_group.expected_anchor_pairs


@pytest.mark.parametrize(
    "case",
    tuple(
        pytest.param(case, id=case.id)
        for case in COMPILED_PATTERN_MODULE_COMPILE_ALL_KEYWORD_CASES
    ),
)
def test_compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time(
    monkeypatch,
    case: CompiledPatternModuleCompileKeywordCase,
) -> None:
    workload = _compiled_pattern_module_compile_keyword_workload(case)
    observed_field_names: list[str] = []
    original_materialize = benchmarks.materialize_numeric_workload_argument

    def record_numeric_materialization(value: Any, *, field_name: str) -> Any:
        observed_field_names.append(field_name)
        return original_materialize(value, field_name=field_name)

    monkeypatch.setattr(
        benchmarks,
        "materialize_numeric_workload_argument",
        record_numeric_materialization,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        if case.expected_exception is None:
            observed_result = callback()
            assert observed_result.pattern == workload.pattern_payload()
        else:
            expected_exception = _expected_exception_instance(case.expected_exception)
            with pytest.raises(
                type(expected_exception),
                match=case.expected_exception["message_substring"],
            ):
                callback()

        assert observed_field_names == list(case.expected_field_names)
    finally:
        re.purge()


@pytest.mark.parametrize(
    "case",
    tuple(
        pytest.param(case, id=case.id)
        for case in COMPILED_PATTERN_MODULE_COMPILE_ALL_KEYWORD_CASES
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_compile_keyword_workloads(
    case: CompiledPatternModuleCompileKeywordCase,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _compiled_pattern_module_compile_keyword_workload(case)
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    _assert_compiled_pattern_module_compile_keyword_payload_round_trip(
        case,
        payload,
        round_tripped,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    "case",
    tuple(
        pytest.param(case, id=case.id)
        for case in COMPILED_PATTERN_MODULE_COMPILE_ALL_KEYWORD_CASES
    ),
)
def test_compiled_pattern_module_compile_keyword_callbacks_precompile_first_argument_before_timing(
    case: CompiledPatternModuleCompileKeywordCase,
) -> None:
    expected_build_calls = _compiled_pattern_module_compile_keyword_expected_build_calls(
        case
    )
    compile_exception = (
        None
        if case.expected_exception is None
        else _expected_exception_instance(case.expected_exception)
    )
    module = _RecordingBenchmarkModule(compile_exception=compile_exception)
    callback = build_callable(
        module,
        "re",
        _compiled_pattern_module_compile_keyword_workload(case),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1

    compiled_pattern = module.compiled_patterns[0]
    if case.expected_exception is None:
        assert callback() is compiled_pattern
    else:
        with pytest.raises(
            type(compile_exception),
            match=case.expected_exception["message_substring"],
        ):
            callback()

    last_call = module.calls[-1]
    assert last_call[0] == "compile"
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == (case.kwargs_payload["flags"],)


@dataclass(frozen=True)
class CompiledPatternModuleBoundarySuccessCase:
    id: str
    operation: str
    pattern: str
    flags: int
    cache_mode: str
    haystack: str
    text_model: str
    expected_callback_result: object


_VERBOSE_REGRESSION_PATTERN = (
    r"^ (?P<key>[A-Z_]+) \s* = \s* (?:[A-Z]{2,4}+|\d{2,3}) $"
)
_VERBOSE_REGRESSION_FLAGS = int(re.VERBOSE | re.MULTILINE)
_VERBOSE_REGRESSION_PATTERN_BYTES = _VERBOSE_REGRESSION_PATTERN.encode("latin-1")


COMPILED_PATTERN_MODULE_BOUNDARY_LITERAL_SUCCESS_CASES = (
    CompiledPatternModuleBoundarySuccessCase(
        id="module-search-literal-warm-hit-str-compiled-pattern",
        operation="module.search",
        pattern="abc",
        flags=0,
        cache_mode="warm",
        haystack="zabczz",
        text_model="str",
        expected_callback_result="module-result",
    ),
    CompiledPatternModuleBoundarySuccessCase(
        id="module-match-literal-warm-hit-str-compiled-pattern",
        operation="module.match",
        pattern="abc",
        flags=0,
        cache_mode="warm",
        haystack="abcdef",
        text_model="str",
        expected_callback_result="module-result",
    ),
    CompiledPatternModuleBoundarySuccessCase(
        id="module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
        operation="module.fullmatch",
        pattern="abc",
        flags=0,
        cache_mode="purged",
        haystack="abc",
        text_model="bytes",
        expected_callback_result="module-result",
    ),
)


COMPILED_PATTERN_MODULE_BOUNDARY_BOUNDED_WILDCARD_SUCCESS_CASES = (
    CompiledPatternModuleBoundarySuccessCase(
        id="module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern",
        operation="module.search",
        pattern="a.c",
        flags=2,
        cache_mode="warm",
        haystack="ABC",
        text_model="str",
        expected_callback_result="module-result",
    ),
    CompiledPatternModuleBoundarySuccessCase(
        id="module-match-bounded-wildcard-warm-hit-str-compiled-pattern",
        operation="module.match",
        pattern="a.c",
        flags=0,
        cache_mode="warm",
        haystack="abc",
        text_model="str",
        expected_callback_result="module-result",
    ),
    CompiledPatternModuleBoundarySuccessCase(
        id="module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern",
        operation="module.fullmatch",
        pattern="a.c",
        flags=0,
        cache_mode="purged",
        haystack="abc",
        text_model="str",
        expected_callback_result="module-result",
    ),
)


COMPILED_PATTERN_MODULE_BOUNDARY_VERBOSE_BYTES_SUCCESS_CASES = (
    CompiledPatternModuleBoundarySuccessCase(
        id="module-search-verbose-regression-warm-hit-bytes-compiled-pattern",
        operation="module.search",
        pattern=_VERBOSE_REGRESSION_PATTERN,
        flags=_VERBOSE_REGRESSION_FLAGS,
        cache_mode="warm",
        haystack="prefix\nENV_VAR=ABCD\nsuffix",
        text_model="bytes",
        expected_callback_result="module-result",
    ),
    CompiledPatternModuleBoundarySuccessCase(
        id="module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern",
        operation="module.fullmatch",
        pattern=_VERBOSE_REGRESSION_PATTERN,
        flags=_VERBOSE_REGRESSION_FLAGS,
        cache_mode="purged",
        haystack="ENV_VAR = 123",
        text_model="bytes",
        expected_callback_result="module-result",
    ),
)


COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES = (
    COMPILED_PATTERN_MODULE_BOUNDARY_LITERAL_SUCCESS_CASES
    + COMPILED_PATTERN_MODULE_BOUNDARY_BOUNDED_WILDCARD_SUCCESS_CASES
    + COMPILED_PATTERN_MODULE_BOUNDARY_VERBOSE_BYTES_SUCCESS_CASES
)


def _compiled_pattern_module_boundary_success_manifest_payload(
    case: CompiledPatternModuleBoundarySuccessCase,
) -> dict[str, object]:
    return {
        "id": f"{case.id}-contract",
        "bucket": case.operation.replace("module.", "module-"),
        "family": "module",
        "operation": case.operation,
        "pattern": case.pattern,
        "haystack": case.haystack,
        "flags": case.flags,
        "use_compiled_pattern": True,
        "text_model": case.text_model,
        "cache_mode": case.cache_mode,
        "timing_scope": "module-helper-call",
        "notes": [
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            "successful module-boundary rows unresolved until helper invocation."
        ],
    }


def _compiled_pattern_module_boundary_success_workload(
    case: CompiledPatternModuleBoundarySuccessCase,
) -> Workload:
    manifest_payload = _compiled_pattern_module_boundary_success_manifest_payload(case)
    return workload_from_payload(
        {
            "manifest_id": "module-boundary",
            "workload_id": str(manifest_payload["id"]),
            **{key: value for key, value in manifest_payload.items() if key != "id"},
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


def _compiled_pattern_module_boundary_success_manifest(
    cases: tuple[CompiledPatternModuleBoundarySuccessCase, ...],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "manifest_id": "module-boundary",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            _compiled_pattern_module_boundary_success_manifest_payload(case)
            for case in cases
        ],
    }


def _assert_compiled_pattern_module_boundary_success_payload_round_trip(
    case: CompiledPatternModuleBoundarySuccessCase,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if case.text_model == "str" else bytes

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["flags"] == case.flags
    assert round_tripped.flags == case.flags
    assert payload.get("expected_exception") is None
    assert round_tripped.expected_exception is None
    assert payload.get("haystack_text_model") is None
    assert round_tripped.haystack_text_model is None
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_text_type)


def _run_cpython_compiled_pattern_module_boundary_success_workload(
    workload: Workload,
) -> object:
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    helper_name = workload.operation.removeprefix("module.")
    helper_flags = 0 if workload.use_compiled_pattern else workload.flags
    return getattr(re, helper_name)(
        compiled_pattern,
        workload.haystack_payload(),
        helper_flags,
    )


def test_standard_benchmark_manifest_preserves_compiled_pattern_module_boundary_success_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest = _compiled_pattern_module_boundary_success_manifest(
        COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES
    )

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_module_boundary_success_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES)
    assert [workload.haystack_text_model for workload in workloads] == [
        None
    ] * len(COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES)

    for case, workload in zip(
        COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_compiled_pattern_module_boundary_success_payload_round_trip(
            case,
            payload,
            round_tripped,
        )
        assert_benchmark_workload_matches_expected_result(
            round_tripped,
            _run_cpython_compiled_pattern_module_boundary_success_workload(workload),
        )


def test_compiled_pattern_module_boundary_verbose_bytes_success_rows_stay_anchored_to_published_correctness_cases(
    tmp_path: pathlib.Path,
) -> None:
    manifest = _compiled_pattern_module_boundary_success_manifest(
        COMPILED_PATTERN_MODULE_BOUNDARY_VERBOSE_BYTES_SUCCESS_CASES
    )

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_module_boundary_verbose_bytes_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    expected_anchor_case_ids = _definition_anchor_expectations(
        manifest_path,
        {
            "module-search-verbose-regression-warm-hit-bytes-compiled-pattern-contract": (
                "workflow-module-search-bytes-verbose-regression-compiled-pattern",
            ),
            "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern-contract": (
                "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
            ),
        },
    )
    anchor_case_ids = published_case_ids_by_signature(
        _module_workflow_compiled_pattern_correctness_case_signature
    )

    assert anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=_module_workflow_compiled_pattern_workload_signature,
        include_workload=_is_module_workflow_compiled_pattern_workload,
    ) == expected_anchor_case_ids
    assert unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=_module_workflow_compiled_pattern_workload_signature,
        include_workload=_is_module_workflow_compiled_pattern_workload,
    ) == ()
    assert tuple(
        (pair.workload_id, pair.case_id)
        for pair in expected_anchored_workload_case_pairs(
            manifest_path,
            expected_anchor_case_ids=expected_anchor_case_ids,
            include_workload=_is_module_workflow_compiled_pattern_workload,
        )
    ) == (
        (
            "module-search-verbose-regression-warm-hit-bytes-compiled-pattern-contract",
            "workflow-module-search-bytes-verbose-regression-compiled-pattern",
        ),
        (
            "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern-contract",
            "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
        ),
    )


@pytest.mark.parametrize(
    "case",
    tuple(
        pytest.param(case, id=case.id)
        for case in COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_boundary_success_workloads(
    case: CompiledPatternModuleBoundarySuccessCase,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _compiled_pattern_module_boundary_success_workload(case)
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    _assert_compiled_pattern_module_boundary_success_payload_round_trip(
        case,
        payload,
        round_tripped,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    ("case", "expected_build_calls", "expected_callback_call"),
    (
        pytest.param(
            COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES[0],
            [("compile", "abc", 0)],
            ("module.search", "zabczz", 0, {}),
            id="module-search-literal-warm-hit-str-compiled-pattern",
        ),
        pytest.param(
            COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES[1],
            [("compile", "abc", 0)],
            ("module.match", "abcdef", 0, {}),
            id="module-match-literal-warm-hit-str-compiled-pattern",
        ),
        pytest.param(
            COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES[2],
            [("compile", b"abc", 0), ("purge",)],
            ("module.fullmatch", b"abc", 0, {}),
            id="module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
        ),
        pytest.param(
            COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES[3],
            [("compile", "a.c", 2)],
            ("module.search", "ABC", 0, {}),
            id="module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern",
        ),
        pytest.param(
            COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES[4],
            [("compile", "a.c", 0)],
            ("module.match", "abc", 0, {}),
            id="module-match-bounded-wildcard-warm-hit-str-compiled-pattern",
        ),
        pytest.param(
            COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES[5],
            [("compile", "a.c", 0), ("purge",)],
            ("module.fullmatch", "abc", 0, {}),
            id="module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern",
        ),
        pytest.param(
            COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES[6],
            [("compile", _VERBOSE_REGRESSION_PATTERN_BYTES, _VERBOSE_REGRESSION_FLAGS)],
            ("module.search", b"prefix\nENV_VAR=ABCD\nsuffix", 0, {}),
            id="module-search-verbose-regression-warm-hit-bytes-compiled-pattern",
        ),
        pytest.param(
            COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES[7],
            [
                ("compile", _VERBOSE_REGRESSION_PATTERN_BYTES, _VERBOSE_REGRESSION_FLAGS),
                ("purge",),
            ],
            ("module.fullmatch", b"ENV_VAR = 123", 0, {}),
            id="module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern",
        ),
    ),
)
def test_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing(
    case: CompiledPatternModuleBoundarySuccessCase,
    expected_build_calls: list[tuple[object, ...]],
    expected_callback_call: tuple[object, ...],
) -> None:
    module = _RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _compiled_pattern_module_boundary_success_workload(case),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == case.expected_callback_result

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]


def _compiled_pattern_module_helper_wrong_text_model_manifest_payload(
    workload: Workload,
    *,
    note_surface: str = "collection/replacement",
) -> dict[str, object]:
    payload = workload_to_payload(workload)
    return {
        "id": f"{workload.workload_id}-contract",
        **{
            key: value
            for key, value in payload.items()
            if key
            not in {
                "manifest_id",
                "workload_id",
                "warmup_iterations",
                "sample_iterations",
                "timed_samples",
                "notes",
                "smoke",
            }
        },
        "notes": [
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            f"wrong-text-model {note_surface} rows unresolved until helper "
            "invocation."
        ],
    }


def _compiled_pattern_module_helper_wrong_text_model_workload_for_manifest(
    source_workload: Workload,
    *,
    manifest_id: str,
    note_surface: str,
) -> Workload:
    manifest_payload = _compiled_pattern_module_helper_wrong_text_model_manifest_payload(
        source_workload,
        note_surface=note_surface,
    )
    return workload_from_payload(
        {
            "manifest_id": manifest_id,
            "workload_id": str(manifest_payload["id"]),
            **{key: value for key, value in manifest_payload.items() if key != "id"},
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


def _compiled_pattern_module_helper_wrong_text_model_workload(
    source_workload: Workload,
) -> Workload:
    return _compiled_pattern_module_helper_wrong_text_model_workload_for_manifest(
        source_workload,
        manifest_id="collection-replacement-boundary",
        note_surface="collection/replacement",
    )


def _compiled_pattern_module_boundary_wrong_text_model_workload(
    source_workload: Workload,
) -> Workload:
    return _compiled_pattern_module_helper_wrong_text_model_workload_for_manifest(
        source_workload,
        manifest_id="module-boundary",
        note_surface="module-boundary",
    )


def _compiled_pattern_module_helper_wrong_text_model_manifest(
    source_workloads: tuple[Workload, ...],
    *,
    manifest_id: str,
    note_surface: str,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "manifest_id": manifest_id,
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            _compiled_pattern_module_helper_wrong_text_model_manifest_payload(
                workload,
                note_surface=note_surface,
            )
            for workload in source_workloads
        ],
    }


def _compiled_pattern_module_helper_wrong_text_model_source_workloads() -> tuple[Workload, ...]:
    return _selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=_is_collection_replacement_wrong_text_model_workload,
    )


def _compiled_pattern_module_boundary_wrong_text_model_source_workloads() -> tuple[Workload, ...]:
    return _selected_manifest_workloads(
        MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload=_is_module_workflow_compiled_pattern_wrong_text_model_workload,
    )


def _assert_compiled_pattern_module_helper_wrong_text_model_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes
    expected_haystack_type = (
        str if source_workload.haystack_text_model == "str" else bytes
    )

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["haystack_text_model"] == source_workload.haystack_text_model
    assert round_tripped.haystack_text_model == source_workload.haystack_text_model
    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_haystack_type)
    if source_workload.replacement is not None:
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


def _compiled_pattern_module_helper_wrong_text_model_expected_callback_result(
    source_workload: Workload,
) -> object:
    if source_workload.operation == "module.subn":
        return ("module-result", 0)
    if source_workload.operation == "module.finditer":
        return ["module-finditer-result"]
    return "module-result"


def _compiled_pattern_module_helper_wrong_text_model_expected_build_calls(
    source_workload: Workload,
) -> list[tuple[object, ...]]:
    compile_call = ("compile", source_workload.pattern_payload(), source_workload.flags)
    if source_workload.cache_mode == "purged":
        return [compile_call, ("purge",)]
    if source_workload.cache_mode == "warm":
        return [compile_call]
    raise AssertionError(
        "unexpected compiled-pattern module helper wrong-text-model workload "
        f"cache mode {source_workload.cache_mode!r}"
    )


def _compiled_pattern_module_helper_wrong_text_model_expected_callback_call(
    source_workload: Workload,
) -> tuple[object, ...]:
    if source_workload.operation in {
        "module.search",
        "module.match",
        "module.fullmatch",
    }:
        return (
            source_workload.operation,
            source_workload.haystack_payload(),
            0,
            {},
        )
    if source_workload.operation == "module.split":
        return (
            source_workload.operation,
            source_workload.haystack_payload(),
            source_workload.maxsplit_argument(),
            0,
            {},
        )
    if source_workload.operation in {"module.findall", "module.finditer"}:
        return (
            source_workload.operation,
            source_workload.haystack_payload(),
            0,
        )
    if source_workload.operation in {"module.sub", "module.subn"}:
        return (
            source_workload.operation,
            source_workload.replacement_payload(),
            source_workload.haystack_payload(),
            source_workload.count_argument(),
            0,
            {},
        )
    raise AssertionError(
        "unexpected compiled-pattern module helper wrong-text-model workload "
        f"operation {source_workload.operation!r}"
    )


def _run_cpython_compiled_pattern_module_helper_wrong_text_model_workload(
    workload: Workload,
) -> object:
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    helper_name = workload.operation.removeprefix("module.")

    if workload.operation in {"module.search", "module.match", "module.fullmatch"}:
        return getattr(re, helper_name)(
            compiled_pattern,
            workload.haystack_payload(),
            workload.flags,
        )

    if workload.operation == "module.split":
        return getattr(re, helper_name)(
            compiled_pattern,
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )

    if workload.operation == "module.findall":
        return getattr(re, helper_name)(
            compiled_pattern,
            workload.haystack_payload(),
            workload.flags,
        )

    if workload.operation == "module.finditer":
        return list(
            getattr(re, helper_name)(
                compiled_pattern,
                workload.haystack_payload(),
                workload.flags,
            )
        )

    if workload.operation in {"module.sub", "module.subn"}:
        return getattr(re, helper_name)(
            compiled_pattern,
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )

    raise AssertionError(
        "unexpected compiled-pattern module helper wrong-text-model workload "
        f"operation {workload.operation!r}"
    )


def test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_wrong_text_model_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = _compiled_pattern_module_helper_wrong_text_model_source_workloads()
    manifest = _compiled_pattern_module_helper_wrong_text_model_manifest(
        source_workloads,
        manifest_id="collection-replacement-boundary",
        note_surface="collection/replacement",
    )

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_collection_replacement_wrong_text_model_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        "module-split-on-bytes-string-purged-str-compiled-pattern",
        "module-findall-on-str-string-purged-bytes-compiled-pattern",
        "module-finditer-on-bytes-string-warm-str-compiled-pattern",
        "module-sub-on-bytes-string-warm-str-compiled-pattern",
        "module-subn-on-str-string-purged-bytes-compiled-pattern",
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload.workload_id}-contract" for workload in source_workloads
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        workload.haystack_text_model for workload in source_workloads
    ]

    for source_workload, workload in zip(
        source_workloads,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_compiled_pattern_module_helper_wrong_text_model_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )

        with pytest.raises(TypeError) as expected_error:
            _run_cpython_compiled_pattern_module_helper_wrong_text_model_workload(
                workload
            )
        with pytest.raises(TypeError) as observed_error:
            run_benchmark_workload_with_cpython(round_tripped)

        assert str(observed_error.value) == str(expected_error.value)


def test_standard_benchmark_manifest_preserves_compiled_pattern_module_boundary_wrong_text_model_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = _compiled_pattern_module_boundary_wrong_text_model_source_workloads()
    manifest = _compiled_pattern_module_helper_wrong_text_model_manifest(
        source_workloads,
        manifest_id="module-boundary",
        note_surface="module-boundary",
    )

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_module_boundary_wrong_text_model_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        "module-search-on-bytes-string-warm-str-compiled-pattern",
        "module-match-on-str-string-purged-bytes-compiled-pattern",
        "module-fullmatch-on-bytes-string-warm-str-compiled-pattern",
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload.workload_id}-contract" for workload in source_workloads
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        workload.haystack_text_model for workload in source_workloads
    ]

    for source_workload, workload in zip(
        source_workloads,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_compiled_pattern_module_helper_wrong_text_model_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )

        with pytest.raises(TypeError) as expected_error:
            _run_cpython_compiled_pattern_module_helper_wrong_text_model_workload(
                workload
            )
        with pytest.raises(TypeError) as observed_error:
            run_benchmark_workload_with_cpython(round_tripped)

        assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _compiled_pattern_module_helper_wrong_text_model_source_workloads()
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_helper_wrong_text_model_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _compiled_pattern_module_helper_wrong_text_model_workload(source_workload)
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    _assert_compiled_pattern_module_helper_wrong_text_model_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _compiled_pattern_module_boundary_wrong_text_model_source_workloads()
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_boundary_wrong_text_model_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _compiled_pattern_module_boundary_wrong_text_model_workload(
        source_workload
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    _assert_compiled_pattern_module_helper_wrong_text_model_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _compiled_pattern_module_helper_wrong_text_model_source_workloads()
    ),
)
def test_compiled_pattern_module_helper_wrong_text_model_callbacks_precompile_first_argument_before_timing(
    source_workload: Workload,
) -> None:
    expected_build_calls = (
        _compiled_pattern_module_helper_wrong_text_model_expected_build_calls(
            source_workload
        )
    )
    expected_callback_call = (
        _compiled_pattern_module_helper_wrong_text_model_expected_callback_call(
            source_workload
        )
    )
    module = _RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _compiled_pattern_module_helper_wrong_text_model_workload(source_workload),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == _compiled_pattern_module_helper_wrong_text_model_expected_callback_result(
        source_workload
    )

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _compiled_pattern_module_boundary_wrong_text_model_source_workloads()
    ),
)
def test_compiled_pattern_module_boundary_wrong_text_model_callbacks_precompile_first_argument_before_timing(
    source_workload: Workload,
) -> None:
    expected_build_calls = (
        _compiled_pattern_module_helper_wrong_text_model_expected_build_calls(
            source_workload
        )
    )
    expected_callback_call = (
        _compiled_pattern_module_helper_wrong_text_model_expected_callback_call(
            source_workload
        )
    )
    module = _RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _compiled_pattern_module_boundary_wrong_text_model_workload(source_workload),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == _compiled_pattern_module_helper_wrong_text_model_expected_callback_result(
        source_workload
    )

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]


def _compiled_pattern_module_helper_keyword_error_workload(
    *,
    operation: str,
    cache_mode: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    expected_exception: dict[str, str],
    text_model: str,
) -> Workload:
    return workload_from_payload(
        {
            "manifest_id": (
                "python-benchmark-compiled-pattern-module-helper-keyword-error-contract"
            ),
            "workload_id": (
                f"{operation}-compiled-pattern-keyword-error-{text_model}-contract"
            ),
            "bucket": operation.replace("module.", "module-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": "abc",
            "replacement": replacement,
            "expected_exception": expected_exception,
            "flags": 0,
            "use_compiled_pattern": True,
            "count": count,
            "maxsplit": maxsplit,
            "kwargs": kwargs_payload,
            "text_model": text_model,
            "cache_mode": cache_mode,
            "timing_scope": "module-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


def _run_cpython_compiled_pattern_module_helper_keyword_workload(
    workload: Workload,
) -> object:
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    helper_name = workload.operation.removeprefix("module.")
    kwargs = dict(workload.kwargs)
    positional_keyword_field = _collection_replacement_positional_keyword_field(
        workload
    )

    if workload.operation == "module.split":
        args: list[object] = [compiled_pattern, workload.haystack_payload()]
        if positional_keyword_field == "maxsplit":
            args.append(workload.maxsplit)
        return getattr(re, helper_name)(*args, **kwargs)

    if workload.operation in {"module.sub", "module.subn"}:
        args = [
            compiled_pattern,
            workload.replacement_payload(),
            workload.haystack_payload(),
        ]
        if positional_keyword_field == "count":
            args.append(workload.count)
        return getattr(re, helper_name)(*args, **kwargs)

    raise AssertionError(
        "unexpected compiled-pattern module helper keyword workload operation "
        f"{workload.operation!r}"
    )


def test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_error_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-compiled-pattern-collection-replacement-keyword-error-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
        },
        "workloads": [
            {
                "id": "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern-contract",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "abc",
                "flags": 0,
                "use_compiled_pattern": True,
                "maxsplit": 1,
                "kwargs": {"maxsplit": 1},
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "multiple values for argument 'maxsplit'",
                },
                "text_model": "str",
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
            },
            {
                "id": "module-sub-unexpected-keyword-purged-str-compiled-pattern-contract",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "flags": 0,
                "use_compiled_pattern": True,
                "kwargs": {"missing": 1},
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "unexpected keyword argument 'missing'",
                },
                "text_model": "str",
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
            },
            {
                "id": "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern-contract",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "flags": 0,
                "use_compiled_pattern": True,
                "count": 1,
                "kwargs": {"missing": 1},
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "unexpected keyword argument 'missing'",
                },
                "text_model": "str",
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
            },
            {
                "id": "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern-contract",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "flags": 0,
                "use_compiled_pattern": True,
                "count": 1,
                "kwargs": {"count": 1},
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "multiple values for argument 'count'",
                },
                "text_model": "bytes",
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
            },
            {
                "id": "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern-contract",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "flags": 0,
                "use_compiled_pattern": True,
                "count": 1,
                "kwargs": {"missing": 1},
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "unexpected keyword argument 'missing'",
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_collection_replacement_keyword_error_contract.py",
        manifest_source,
    )
    workloads = load_manifest(manifest_path).workloads

    assert [workload.use_compiled_pattern for workload in workloads] == [True] * len(
        workloads
    )

    for workload in workloads:
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)
        assert payload["use_compiled_pattern"] is True
        assert round_tripped.use_compiled_pattern is True

        with pytest.raises(TypeError) as expected_error:
            _run_cpython_compiled_pattern_module_helper_keyword_workload(workload)
        with pytest.raises(TypeError) as observed_error:
            run_benchmark_workload_with_cpython(round_tripped)

        assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(
    (
        "operation",
        "cache_mode",
        "kwargs_payload",
        "replacement",
        "count",
        "maxsplit",
        "expected_exception",
        "text_model",
        "expected_field_names",
    ),
    (
        pytest.param(
            "module.split",
            "purged",
            {"maxsplit": 1},
            None,
            0,
            1,
            {
                "type": "TypeError",
                "message_substring": "multiple values for argument 'maxsplit'",
            },
            "str",
            ["maxsplit", "kwargs.maxsplit"],
            id="module-split-duplicate-maxsplit-keyword-str-compiled-pattern",
        ),
        pytest.param(
            "module.split",
            "purged",
            {"missing": 1},
            None,
            0,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            "bytes",
            ["kwargs.missing"],
            id="module-split-unexpected-keyword-bytes-compiled-pattern",
        ),
        pytest.param(
            "module.sub",
            "warm",
            {"count": 1},
            "x",
            1,
            0,
            {
                "type": "TypeError",
                "message_substring": "multiple values for argument 'count'",
            },
            "str",
            ["count", "kwargs.count"],
            id="module-sub-duplicate-count-keyword-str-compiled-pattern",
        ),
        pytest.param(
            "module.sub",
            "purged",
            {"missing": 1},
            "x",
            0,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            "str",
            ["kwargs.missing"],
            id="module-sub-unexpected-keyword-str-compiled-pattern",
        ),
        pytest.param(
            "module.sub",
            "purged",
            {"missing": 1},
            "x",
            1,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            "str",
            ["count", "kwargs.missing"],
            id="module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern",
        ),
        pytest.param(
            "module.subn",
            "warm",
            {"count": 1},
            "x",
            1,
            0,
            {
                "type": "TypeError",
                "message_substring": "multiple values for argument 'count'",
            },
            "bytes",
            ["count", "kwargs.count"],
            id="module-subn-duplicate-count-keyword-bytes-compiled-pattern",
        ),
        pytest.param(
            "module.subn",
            "purged",
            {"missing": 1},
            "x",
            0,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            "bytes",
            ["kwargs.missing"],
            id="module-subn-unexpected-keyword-bytes-compiled-pattern",
        ),
        pytest.param(
            "module.subn",
            "purged",
            {"missing": 1},
            "x",
            1,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            "bytes",
            ["count", "kwargs.missing"],
            id="module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern",
        ),
    ),
)
def test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions(
    monkeypatch,
    operation: str,
    cache_mode: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    expected_exception: dict[str, str],
    text_model: str,
    expected_field_names: list[str],
) -> None:
    workload = _compiled_pattern_module_helper_keyword_error_workload(
        operation=operation,
        cache_mode=cache_mode,
        kwargs_payload=kwargs_payload,
        replacement=replacement,
        count=count,
        maxsplit=maxsplit,
        expected_exception=expected_exception,
        text_model=text_model,
    )
    observed_field_names: list[str] = []
    original_materialize = benchmarks.materialize_numeric_workload_argument

    def record_numeric_materialization(value: Any, *, field_name: str) -> Any:
        observed_field_names.append(field_name)
        return original_materialize(value, field_name=field_name)

    monkeypatch.setattr(
        benchmarks,
        "materialize_numeric_workload_argument",
        record_numeric_materialization,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        with pytest.raises(TypeError) as expected_error:
            _run_cpython_compiled_pattern_module_helper_keyword_workload(workload)
        with pytest.raises(TypeError) as observed_error:
            callback()

        assert observed_field_names == expected_field_names
        assert str(observed_error.value) == str(expected_error.value)
    finally:
        re.purge()


@pytest.mark.parametrize(
    (
        "operation",
        "cache_mode",
        "kwargs_payload",
        "replacement",
        "count",
        "maxsplit",
        "expected_exception",
        "text_model",
    ),
    (
        pytest.param(
            "module.split",
            "purged",
            {"maxsplit": 1},
            None,
            0,
            1,
            {
                "type": "TypeError",
                "message_substring": "multiple values for argument 'maxsplit'",
            },
            "str",
            id="module-split-duplicate-maxsplit-keyword-str-compiled-pattern",
        ),
        pytest.param(
            "module.split",
            "purged",
            {"missing": 1},
            None,
            0,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            "bytes",
            id="module-split-unexpected-keyword-bytes-compiled-pattern",
        ),
        pytest.param(
            "module.sub",
            "warm",
            {"count": 1},
            "x",
            1,
            0,
            {
                "type": "TypeError",
                "message_substring": "multiple values for argument 'count'",
            },
            "str",
            id="module-sub-duplicate-count-keyword-str-compiled-pattern",
        ),
        pytest.param(
            "module.sub",
            "purged",
            {"missing": 1},
            "x",
            0,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            "str",
            id="module-sub-unexpected-keyword-str-compiled-pattern",
        ),
        pytest.param(
            "module.sub",
            "purged",
            {"missing": 1},
            "x",
            1,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            "str",
            id="module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern",
        ),
        pytest.param(
            "module.subn",
            "warm",
            {"count": 1},
            "x",
            1,
            0,
            {
                "type": "TypeError",
                "message_substring": "multiple values for argument 'count'",
            },
            "bytes",
            id="module-subn-duplicate-count-keyword-bytes-compiled-pattern",
        ),
        pytest.param(
            "module.subn",
            "purged",
            {"missing": 1},
            "x",
            0,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            "bytes",
            id="module-subn-unexpected-keyword-bytes-compiled-pattern",
        ),
        pytest.param(
            "module.subn",
            "purged",
            {"missing": 1},
            "x",
            1,
            0,
            {
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            "bytes",
            id="module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern",
        ),
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_error_workloads(
    operation: str,
    cache_mode: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    expected_exception: dict[str, str],
    text_model: str,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _compiled_pattern_module_helper_keyword_error_workload(
        operation=operation,
        cache_mode=cache_mode,
        kwargs_payload=kwargs_payload,
        replacement=replacement,
        count=count,
        maxsplit=maxsplit,
        expected_exception=expected_exception,
        text_model=text_model,
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["expected_exception"] == expected_exception
    assert round_tripped.expected_exception == expected_exception
    assert payload["kwargs"] == kwargs_payload
    assert round_tripped.kwargs == kwargs_payload

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


class _RecordingBenchmarkCompiledPattern:
    def __init__(self, calls: list[tuple[object, ...]]) -> None:
        self._calls = calls

    def search(self, haystack: object, *args: object, **kwargs: object) -> object:
        self._calls.append(("pattern.search", haystack, args, kwargs))
        return "pattern-result"

    def split(self, haystack: object, *args: object, **kwargs: object) -> object:
        self._calls.append(("pattern.split", haystack, args, kwargs))
        return "pattern-result"

    def sub(
        self,
        repl: object,
        string: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        self._calls.append(("pattern.sub", repl, string, args, kwargs))
        return "pattern-result"

    def subn(
        self,
        repl: object,
        string: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        self._calls.append(("pattern.subn", repl, string, args, kwargs))
        return ("pattern-result", 0)


class _RecordingBenchmarkModule:
    def __init__(
        self,
        *,
        helper_exception: Exception | None = None,
        compile_exception: Exception | None = None,
    ) -> None:
        self.calls: list[tuple[object, ...]] = []
        self._helper_exception = helper_exception
        self._compile_exception = compile_exception
        self.compiled_patterns: list[_RecordingBenchmarkCompiledPattern] = []

    def purge(self) -> None:
        self.calls.append(("purge",))

    def compile(self, pattern: object, flags: int = 0) -> _RecordingBenchmarkCompiledPattern:
        self.calls.append(("compile", pattern, flags))
        if isinstance(pattern, _RecordingBenchmarkCompiledPattern):
            if self._compile_exception is not None:
                raise self._compile_exception
            return pattern
        compiled_pattern = _RecordingBenchmarkCompiledPattern(self.calls)
        self.compiled_patterns.append(compiled_pattern)
        return compiled_pattern

    def search(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
        **kwargs: object,
    ) -> object:
        self.calls.append(("module.search", pattern, haystack, flags, kwargs))
        if self._helper_exception is not None:
            raise self._helper_exception
        return "module-result"

    def match(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
        **kwargs: object,
    ) -> object:
        self.calls.append(("module.match", pattern, haystack, flags, kwargs))
        if self._helper_exception is not None:
            raise self._helper_exception
        return "module-result"

    def fullmatch(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
        **kwargs: object,
    ) -> object:
        self.calls.append(("module.fullmatch", pattern, haystack, flags, kwargs))
        if self._helper_exception is not None:
            raise self._helper_exception
        return "module-result"

    def split(
        self,
        pattern: object,
        haystack: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        maxsplit = args[0] if args else 0
        flags = args[1] if len(args) > 1 else 0
        self.calls.append(("module.split", pattern, haystack, maxsplit, flags, kwargs))
        if self._helper_exception is not None:
            raise self._helper_exception
        return "module-result"

    def findall(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
    ) -> object:
        self.calls.append(("module.findall", pattern, haystack, flags))
        if self._helper_exception is not None:
            raise self._helper_exception
        return "module-result"

    def finditer(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
    ) -> object:
        self.calls.append(("module.finditer", pattern, haystack, flags))
        if self._helper_exception is not None:
            raise self._helper_exception
        return iter(["module-finditer-result"])

    def sub(
        self,
        pattern: object,
        repl: object,
        string: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        count = args[0] if args else 0
        flags = args[1] if len(args) > 1 else 0
        self.calls.append(("module.sub", pattern, repl, string, count, flags, kwargs))
        if self._helper_exception is not None:
            raise self._helper_exception
        return "module-result"

    def subn(
        self,
        pattern: object,
        repl: object,
        string: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        count = args[0] if args else 0
        flags = args[1] if len(args) > 1 else 0
        self.calls.append(("module.subn", pattern, repl, string, count, flags, kwargs))
        if self._helper_exception is not None:
            raise self._helper_exception
        return ("module-result", 0)


def _module_search_cache_contract_workload(
    *,
    cache_mode: str,
    expected_exception: dict[str, str] | None = None,
) -> Workload:
    return workload_from_payload(
        {
            "manifest_id": "python-benchmark-module-helper-cache-contract",
            "workload_id": f"module-search-{cache_mode}-cache-contract",
            "bucket": "module-search",
            "family": "module",
            "operation": "module.search",
            "pattern": "abc",
            "haystack": "zabcabc",
            "flags": 0,
            "count": 0,
            "maxsplit": 0,
            "expected_exception": expected_exception,
            "text_model": "str",
            "cache_mode": cache_mode,
            "timing_scope": "module-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


def _pattern_search_cache_contract_workload(*, cache_mode: str) -> Workload:
    return workload_from_payload(
        {
            "manifest_id": "python-benchmark-pattern-helper-cache-contract",
            "workload_id": f"pattern-search-{cache_mode}-cache-contract",
            "bucket": "pattern-search",
            "family": "module",
            "operation": "pattern.search",
            "pattern": "abc",
            "haystack": "zabcabc",
            "flags": 0,
            "count": 0,
            "maxsplit": 0,
            "text_model": "str",
            "cache_mode": cache_mode,
            "timing_scope": "pattern-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


@pytest.mark.parametrize(
    ("cache_mode", "expected_build_calls", "expected_callback_calls"),
    (
        pytest.param(
            "cold",
            [],
            [
                ("purge",),
                ("module.search", "abc", "zabcabc", 0, {}),
            ],
            id="cold",
        ),
        pytest.param(
            "warm",
            [
                ("module.search", "abc", "zabcabc", 0, {}),
            ],
            [
                ("module.search", "abc", "zabcabc", 0, {}),
            ],
            id="warm",
        ),
        pytest.param(
            "purged",
            [],
            [
                ("purge",),
                ("module.search", "abc", "zabcabc", 0, {}),
                ("purge",),
            ],
            id="purged",
        ),
    ),
)
def test_module_helper_cache_modes_preserve_expected_purge_and_warmup_order(
    cache_mode: str,
    expected_build_calls: list[tuple[object, ...]],
    expected_callback_calls: list[tuple[object, ...]],
) -> None:
    module = _RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _module_search_cache_contract_workload(cache_mode=cache_mode),
    )

    assert module.calls == expected_build_calls
    assert callback() == "module-result"
    assert module.calls == [*expected_build_calls, *expected_callback_calls]


def test_module_helper_warm_expected_exception_prewarms_compile_cache_without_invoking_helper(
) -> None:
    module = _RecordingBenchmarkModule(
        helper_exception=TypeError("unexpected keyword argument 'missing'"),
    )
    callback = build_callable(
        module,
        "re",
        _module_search_cache_contract_workload(
            cache_mode="warm",
            expected_exception={
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
        ),
    )

    assert module.calls == [("compile", "abc", 0)]
    with pytest.raises(TypeError, match="unexpected keyword argument 'missing'"):
        callback()
    assert module.calls == [
        ("compile", "abc", 0),
        ("module.search", "abc", "zabcabc", 0, {}),
    ]


@pytest.mark.parametrize(
    (
        "operation",
        "cache_mode",
        "kwargs_payload",
        "replacement",
        "count",
        "maxsplit",
        "text_model",
        "expected_build_calls",
        "expected_callback_call",
    ),
    (
        pytest.param(
            "module.split",
            "warm",
            {"maxsplit": 1},
            None,
            0,
            1,
            "str",
            [("compile", "abc", 0)],
            ("module.split", "abc", 1, 0, {"maxsplit": 1}),
            id="module-split-duplicate-maxsplit-warm-compiled-pattern",
        ),
        pytest.param(
            "module.subn",
            "purged",
            {"missing": 1},
            "x",
            0,
            0,
            "bytes",
            [("compile", b"abc", 0), ("purge",)],
            ("module.subn", b"x", b"abc", 0, 0, {"missing": 1}),
            id="module-subn-unexpected-keyword-purged-compiled-pattern",
        ),
        pytest.param(
            "module.sub",
            "purged",
            {"missing": 1},
            "x",
            1,
            0,
            "str",
            [("compile", "abc", 0), ("purge",)],
            ("module.sub", "x", "abc", 1, 0, {"missing": 1}),
            id="module-sub-unexpected-keyword-after-positional-count-purged-compiled-pattern",
        ),
        pytest.param(
            "module.subn",
            "purged",
            {"missing": 1},
            "x",
            1,
            0,
            "bytes",
            [("compile", b"abc", 0), ("purge",)],
            ("module.subn", b"x", b"abc", 1, 0, {"missing": 1}),
            id="module-subn-unexpected-keyword-after-positional-count-purged-compiled-pattern",
        ),
    ),
)
def test_compiled_pattern_module_helper_callbacks_precompile_first_argument_before_timing(
    operation: str,
    cache_mode: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    text_model: str,
    expected_build_calls: list[tuple[object, ...]],
    expected_callback_call: tuple[object, ...],
) -> None:
    module = _RecordingBenchmarkModule()
    if "maxsplit" in kwargs_payload:
        expected_exception = {
            "type": "TypeError",
            "message_substring": "multiple values for argument 'maxsplit'",
        }
    elif "count" in kwargs_payload:
        expected_exception = {
            "type": "TypeError",
            "message_substring": "multiple values for argument 'count'",
        }
    else:
        expected_exception = {
            "type": "TypeError",
            "message_substring": "unexpected keyword argument 'missing'",
        }
    callback = build_callable(
        module,
        "re",
        _compiled_pattern_module_helper_keyword_error_workload(
            operation=operation,
            cache_mode=cache_mode,
            kwargs_payload=kwargs_payload,
            replacement=replacement,
            count=count,
            maxsplit=maxsplit,
            expected_exception=expected_exception,
            text_model=text_model,
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() in {"module-result", ("module-result", 0)}

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]


@pytest.mark.parametrize(
    ("cache_mode", "expected_build_calls", "expected_callback_calls"),
    (
        pytest.param(
            "cold",
            [],
            [
                ("purge",),
                ("compile", "abc", 0),
                ("pattern.search", "zabcabc", (), {}),
            ],
            id="cold",
        ),
        pytest.param(
            "warm",
            [
                ("compile", "abc", 0),
            ],
            [
                ("pattern.search", "zabcabc", (), {}),
            ],
            id="warm",
        ),
        pytest.param(
            "purged",
            [
                ("compile", "abc", 0),
                ("purge",),
            ],
            [
                ("pattern.search", "zabcabc", (), {}),
            ],
            id="purged",
        ),
    ),
)
def test_pattern_helper_cache_modes_preserve_expected_compile_and_purge_order(
    cache_mode: str,
    expected_build_calls: list[tuple[object, ...]],
    expected_callback_calls: list[tuple[object, ...]],
) -> None:
    module = _RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _pattern_search_cache_contract_workload(cache_mode=cache_mode),
    )

    assert module.calls == expected_build_calls
    assert callback() == "pattern-result"
    assert module.calls == [*expected_build_calls, *expected_callback_calls]


@pytest.mark.parametrize(
    "workload",
    tuple(
        pytest.param(
            workload,
            id=workload.workload_id,
        )
        for workload in _pattern_helper_collection_replacement_wrong_text_model_workloads()
    ),
)
def test_pattern_helper_collection_replacement_wrong_text_model_callbacks_precompile_before_timing(
    workload: Workload,
) -> None:
    module = _RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        workload,
    )

    assert module.calls == (
        _pattern_helper_collection_replacement_wrong_text_model_expected_build_calls(
            workload
        )
    )
    assert len(module.compiled_patterns) == 1
    assert callback() == (
        _pattern_helper_collection_replacement_wrong_text_model_expected_callback_result(
            workload
        )
    )
    assert module.calls[-1] == (
        _pattern_helper_collection_replacement_wrong_text_model_expected_callback_call(
            workload
        )
    )


def test_standard_benchmark_manifest_materializes_nested_constant_bytes_without_aliasing(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-nested-constant-contract",
        "defaults": {
            "warmup_iterations": 2,
            "sample_iterations": 3,
            "timed_samples": 4,
            "text_model": "bytes",
        },
        "workloads": [
            {
                "id": "module-sub-callable-nested-constant-contract-bytes",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": r"(abc)",
                "text_model": "bytes",
                "replacement": {
                    "type": "callable_constant",
                    "value": {
                        "literal": "literal",
                        "sequence": [
                            "inner",
                            {
                                "type": "bytes",
                                "value": "XYZ",
                                "encoding": "ascii",
                            },
                            {"nested": "value"},
                        ],
                    },
                },
                "haystack": "abc",
                "categories": ["replacement", "callable", "constant", "bytes"],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_nested_constant_contract.py",
        manifest_source,
    )
    manifest = load_manifest(manifest_path)
    workloads = manifest.workloads

    assert manifest.manifest_id == "python-benchmark-nested-constant-contract"
    assert [workload.workload_id for workload in workloads] == [
        "module-sub-callable-nested-constant-contract-bytes",
    ]

    workload = workloads[0]
    assert workload.text_model == "bytes"
    assert workload_to_payload(workload)["replacement"] == {
        "type": "callable_constant",
        "value": {
            "literal": "literal",
            "sequence": [
                "inner",
                {
                    "type": "bytes",
                    "value": "XYZ",
                    "encoding": "ascii",
                },
                {"nested": "value"},
            ],
        },
    }

    replacement = workload.replacement_payload()
    assert callable(replacement)
    assert replacement.__module__ == "rebar_harness.benchmarks"
    assert replacement.__qualname__ == "callable_constant"

    raw_replacement = workload.replacement
    assert isinstance(raw_replacement, dict)
    raw_value = raw_replacement["value"]
    assert isinstance(raw_value, dict)
    raw_sequence = raw_value["sequence"]
    assert isinstance(raw_sequence, list)
    raw_bytes_descriptor = raw_sequence[1]
    assert isinstance(raw_bytes_descriptor, dict)
    raw_nested_mapping = raw_sequence[2]
    assert isinstance(raw_nested_mapping, dict)

    raw_value["literal"] = "mutated"
    raw_sequence[0] = "changed"
    raw_bytes_descriptor["value"] = "CHANGED"
    raw_nested_mapping["nested"] = "changed"

    match = re.search(workload.pattern_payload(), workload.haystack_payload())
    assert match is not None
    assert replacement(match) == {
        "literal": b"literal",
        "sequence": [
            b"inner",
            b"XYZ",
            {"nested": b"value"},
        ],
    }


def test_standard_benchmark_manifest_replacement_payload_rejects_unsupported_text_model(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-invalid-text-model-contract",
        "workloads": [
            {
                "id": "module-sub-callable-invalid-text-model",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": {
                    "type": "callable_constant",
                    "value": "CONST",
                },
                "haystack": "abc",
                "text_model": "utf-16",
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_text_model_contract.py",
        manifest_source,
    )
    workloads = load_manifest(manifest_path).workloads

    with pytest.raises(ValueError, match=r"unsupported text model 'utf-16'"):
        workloads[0].replacement_payload()


def test_standard_benchmark_manifest_rejects_missing_and_non_dict_manifest_values(
    tmp_path: pathlib.Path,
) -> None:
    invalid_modules = (
        (
            "missing_manifest.py",
            "WORKLOADS = []",
            r"is missing a MANIFEST value",
        ),
        (
            "non_dict_manifest.py",
            "MANIFEST = ['not-a-dict']",
            r"must be a dict",
        ),
    )

    for filename, source, error_pattern in invalid_modules:
        manifest_path = _write_test_manifest(tmp_path, filename, source)
        with pytest.raises(ValueError, match=error_pattern):
            load_manifest(manifest_path)


@pytest.mark.parametrize(
    ("invalid_expected_exception", "error_pattern"),
    (
        pytest.param(
            ["TypeError"],
            "benchmark workload expected_exception must be an object",
            id="non-object",
        ),
        pytest.param(
            {"message_substring": "NoneType"},
            r"benchmark workload expected_exception requires a `type`",
            id="missing-type",
        ),
        pytest.param(
            {"type": "TypeError", "detail": "extra"},
            re.escape(
                "benchmark workload expected_exception contains unsupported keys: "
                "['detail']"
            ),
            id="unsupported-key",
        ),
        pytest.param(
            {"type": "TypeError", "message_substring": ("NoneType",)},
            "unsupported workload value",
            id="unsupported-nested-value",
        ),
    ),
)
def test_standard_benchmark_expected_exception_validation_matches_manifest_and_payload_entry_points(
    tmp_path: pathlib.Path,
    invalid_expected_exception: object,
    error_pattern: str,
) -> None:
    manifest_source = f"""
    MANIFEST = {{
        "schema_version": 1,
        "manifest_id": "python-benchmark-invalid-expected-exception-contract",
        "workloads": [
            {{
                "id": "module-sub-invalid-expected-exception-contract",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "expected_exception": {invalid_expected_exception!r},
            }},
        ],
    }}
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_expected_exception_contract.py",
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(
            {
                "manifest_id": "python-benchmark-invalid-expected-exception-contract",
                "workload_id": "module-sub-invalid-expected-exception-contract",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "haystack": "abc",
                "replacement": "x",
                "expected_exception": invalid_expected_exception,
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "text_model": "str",
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            }
        )


@pytest.mark.parametrize(
    (
        "manifest_id",
        "operation",
        "use_compiled_pattern",
        "kwargs_payload",
        "text_model",
        "haystack_text_model",
        "expected_exception",
        "error_pattern",
    ),
    (
        pytest.param(
            "python-benchmark-invalid-haystack-text-model-contract",
            "module.sub",
            True,
            {},
            "str",
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model is only supported on the "
                "`collection-replacement-boundary` manifest and the bounded "
                "`module-boundary` compiled-pattern wrong-text-model trio"
            ),
            id="manifest-scope",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "module.search",
            False,
            {},
            "str",
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "compiled-pattern module.split/module.findall/module.finditer/"
                "module.sub/module.subn workloads"
            ),
            id="operation-scope",
        ),
        pytest.param(
            "module-boundary",
            "module.sub",
            True,
            {},
            "str",
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "compiled-pattern module.search/module.match/module.fullmatch "
                "workloads on the `module-boundary` manifest"
            ),
            id="module-boundary-operation-scope",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "module.sub",
            True,
            {},
            "str",
            "str",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model must differ from the "
                "workload text_model"
            ),
            id="same-text-model",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "module.sub",
            True,
            {},
            "str",
            "bytes",
            None,
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "timed TypeError rows"
            ),
            id="missing-expected-exception",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "module.sub",
            True,
            {},
            "str",
            "utf-16",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model must be `str` or `bytes`; "
                "got 'utf-16'"
            ),
            id="invalid-override-model",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "pattern.findall",
            False,
            {},
            "bytes",
            "str",
            {
                "type": "TypeError",
                "message_substring": "cannot use a bytes pattern on a string-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "direct Pattern.split()/Pattern.sub()/Pattern.subn() positional "
                "helper workloads"
            ),
            id="pattern-operation-scope",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "pattern.split",
            False,
            {"maxsplit": 1},
            "str",
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "direct Pattern.split()/Pattern.sub()/Pattern.subn() positional "
                "helper workloads"
            ),
            id="pattern-keyword-carrier-not-supported",
        ),
    ),
)
def test_standard_benchmark_haystack_text_model_validation_matches_manifest_and_payload_entry_points(
    tmp_path: pathlib.Path,
    manifest_id: str,
    operation: str,
    use_compiled_pattern: bool,
    kwargs_payload: dict[str, object],
    text_model: str,
    haystack_text_model: str,
    expected_exception: dict[str, str] | None,
    error_pattern: str,
) -> None:
    bucket = operation.replace(".", "-")
    manifest_source = f"""
    MANIFEST = {{
        "schema_version": 1,
        "manifest_id": {manifest_id!r},
        "workloads": [
            {{
                "id": "module-sub-invalid-haystack-text-model-contract",
                "bucket": {bucket!r},
                "family": "module",
                "operation": {operation!r},
                "pattern": "abc",
                "haystack": "abc",
                "replacement": "x",
                "expected_exception": {expected_exception!r},
                "flags": 0,
                "use_compiled_pattern": {use_compiled_pattern!r},
                "count": 1,
                "maxsplit": 0,
                "kwargs": {kwargs_payload!r},
                "text_model": {text_model!r},
                "haystack_text_model": {haystack_text_model!r},
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
            }},
        ],
    }}
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_haystack_text_model_contract.py",
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(
            {
                "manifest_id": manifest_id,
                "workload_id": "module-sub-invalid-haystack-text-model-contract",
                "bucket": bucket,
                "family": "module",
                "operation": operation,
                "pattern": "abc",
                "haystack": "abc",
                "replacement": "x",
                "expected_exception": expected_exception,
                "flags": 0,
                "use_compiled_pattern": use_compiled_pattern,
                "count": 1,
                "maxsplit": 0,
                "kwargs": kwargs_payload,
                "text_model": text_model,
                "haystack_text_model": haystack_text_model,
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            }
        )


@pytest.mark.parametrize(
    (
        "manifest_id",
        "operation",
        "kwargs_payload",
        "haystack_text_model",
        "expected_exception",
        "error_pattern",
    ),
    (
        pytest.param(
            "module-boundary",
            "module.search",
            {},
            None,
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark compiled-pattern module-helper "
                "search/match/fullmatch workloads currently only support "
                "successful same-text-model rows or timed wrong-text-model "
                "TypeError rows"
            ),
            id="unexpected-exception-on-success-row",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "module.search",
            {},
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark compiled-pattern module-helper "
                "search/match/fullmatch workloads are only supported on the "
                "`module-boundary` manifest"
            ),
            id="module-boundary-manifest-scope",
        ),
        pytest.param(
            "module-boundary",
            "module.search",
            {"flags": 0},
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark compiled-pattern module-helper "
                "search/match/fullmatch workloads currently only support "
                "positional helper calls"
            ),
            id="keyword-carrier-not-supported",
        ),
    ),
)
def test_standard_benchmark_compiled_pattern_module_boundary_validation_matches_manifest_and_payload_entry_points(
    tmp_path: pathlib.Path,
    manifest_id: str,
    operation: str,
    kwargs_payload: dict[str, object],
    haystack_text_model: str | None,
    expected_exception: dict[str, str] | None,
    error_pattern: str,
) -> None:
    manifest_source = f"""
    MANIFEST = {{
        "schema_version": 1,
        "manifest_id": {manifest_id!r},
        "workloads": [
            {{
                "id": "module-search-invalid-compiled-pattern-boundary-contract",
                "bucket": "module-search",
                "family": "module",
                "operation": {operation!r},
                "pattern": "abc",
                "haystack": "abc",
                "expected_exception": {expected_exception!r},
                "flags": 0,
                "use_compiled_pattern": True,
                "count": 0,
                "maxsplit": 0,
                "kwargs": {kwargs_payload!r},
                "text_model": "str",
                "haystack_text_model": {haystack_text_model!r},
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
            }},
        ],
    }}
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_compiled_pattern_module_boundary_contract.py",
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(
            {
                "manifest_id": manifest_id,
                "workload_id": "module-search-invalid-compiled-pattern-boundary-contract",
                "bucket": "module-search",
                "family": "module",
                "operation": operation,
                "pattern": "abc",
                "haystack": "abc",
                "expected_exception": expected_exception,
                "flags": 0,
                "use_compiled_pattern": True,
                "count": 0,
                "maxsplit": 0,
                "kwargs": kwargs_payload,
                "text_model": "str",
                "haystack_text_model": haystack_text_model,
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            }
        )


@pytest.mark.parametrize(
    (
        "manifest_id",
        "kwargs_payload",
        "expected_exception",
        "pattern",
        "flags",
        "text_model",
        "error_pattern",
    ),
    (
        pytest.param(
            "collection-replacement-boundary",
            None,
            None,
            "abc",
            0,
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads are only supported on the "
                "`module-boundary` manifest"
            ),
            id="manifest-scope",
        ),
        pytest.param(
            "module-boundary",
            {"flags": True},
            None,
            "abc",
            0,
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `flags=0`, `flags=False`, and "
                "`flags=IGNORECASE` rejection keyword carriers"
            ),
            id="keyword-carrier-scope",
        ),
        pytest.param(
            "module-boundary",
            {"flags": int(re.IGNORECASE)},
            None,
            "abc",
            0,
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `flags=0`, `flags=False`, and "
                "`flags=IGNORECASE` rejection keyword carriers"
            ),
            id="ignorecase-rejection-missing-expected-exception",
        ),
        pytest.param(
            "module-boundary",
            None,
            {
                "type": "TypeError",
                "message_substring": "bad pattern",
            },
            "abc",
            0,
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "successful same-text-model literal or named-group rows or "
                "the bounded `flags=IGNORECASE` rejection rows"
            ),
            id="expected-exception-not-supported",
        ),
        pytest.param(
            "module-boundary",
            None,
            None,
            "(?:abc)",
            0,
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `abc` str/bytes literal success pair, "
                "the exact same-text-model `(?P<word>abc)` str/bytes "
                "named-group success pair, and `flags=IGNORECASE` "
                "rejection pairs"
            ),
            id="pattern-scope",
        ),
        pytest.param(
            "module-boundary",
            None,
            None,
            "abc",
            int(re.IGNORECASE),
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `abc` str/bytes literal success pair, "
                "the exact same-text-model `(?P<word>abc)` str/bytes "
                "named-group success pair, and `flags=IGNORECASE` "
                "rejection pairs"
            ),
            id="flags-scope",
        ),
        pytest.param(
            "module-boundary",
            None,
            None,
            "abc",
            0,
            "unicode",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `abc` str/bytes literal success pair, "
                "the exact same-text-model `(?P<word>abc)` str/bytes "
                "named-group success pair, and `flags=IGNORECASE` "
                "rejection pairs"
            ),
            id="text-model-scope",
        ),
    ),
)
def test_standard_benchmark_compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points(
    tmp_path: pathlib.Path,
    manifest_id: str,
    kwargs_payload: dict[str, object] | None,
    expected_exception: dict[str, str] | None,
    pattern: str,
    flags: int,
    text_model: str,
    error_pattern: str,
) -> None:
    kwargs_line = (
        f'                "kwargs": {kwargs_payload!r},\n'
        if kwargs_payload is not None
        else ""
    )
    manifest_source = f"""
    MANIFEST = {{
        "schema_version": 1,
        "manifest_id": {manifest_id!r},
        "workloads": [
            {{
                "id": "module-compile-invalid-compiled-pattern-contract",
                "bucket": "module-compile",
                "family": "module",
                "operation": "module.compile",
                "pattern": {pattern!r},
                "expected_exception": {expected_exception!r},
                "flags": {flags!r},
                "use_compiled_pattern": True,
                "count": 0,
                "maxsplit": 0,
{kwargs_line}                "text_model": {text_model!r},
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
            }},
        ],
    }}
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_compiled_pattern_module_compile_contract.py",
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    payload = {
        "manifest_id": manifest_id,
        "workload_id": "module-compile-invalid-compiled-pattern-contract",
        "bucket": "module-compile",
        "family": "module",
        "operation": "module.compile",
        "pattern": pattern,
        "expected_exception": expected_exception,
        "flags": flags,
        "use_compiled_pattern": True,
        "count": 0,
        "maxsplit": 0,
        "text_model": text_model,
        "cache_mode": "warm",
        "timing_scope": "module-helper-call",
        "warmup_iterations": 1,
        "sample_iterations": 1,
        "timed_samples": 1,
        "notes": [],
        "categories": [],
        "syntax_features": [],
        "smoke": False,
    }
    if kwargs_payload is not None:
        payload["kwargs"] = kwargs_payload

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(payload)


@pytest.mark.parametrize(
    "case",
    tuple(
        pytest.param(case, id=case.id)
        for case in (
            COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_CASES
            + COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_NAMED_GROUP_KEYWORD_CASES
        )
    ),
)
def test_standard_benchmark_compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows(
    tmp_path: pathlib.Path,
    case: CompiledPatternModuleCompileKeywordCase,
) -> None:
    manifest = _compiled_pattern_module_compile_keyword_manifest((case,))
    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_module_compile_ignorecase_validation_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workload = load_manifest(manifest_path).workloads[0]
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    _assert_compiled_pattern_module_compile_keyword_payload_round_trip(
        case,
        payload,
        round_tripped,
    )


@pytest.mark.parametrize(
    (
        "manifest_id",
        "operation",
        "cache_mode",
        "error_pattern",
    ),
    (
        pytest.param(
            "collection-replacement-boundary",
            "pattern.search",
            "warm",
            (
                re.escape(
                    "benchmark compiled-pattern module-helper workloads currently "
                    "only support"
                )
                + r".*"
                + re.escape("; got 'pattern.search'")
            ),
            id="operation-scope",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "module.findall",
            "cold",
            re.escape(
                "benchmark compiled-pattern module-helper workloads currently require "
                "`cache_mode` to be `warm` or `purged` so timed callbacks exclude "
                "pattern compilation"
            ),
            id="collection-replacement-cache-mode",
        ),
        pytest.param(
            "module-boundary",
            "module.search",
            "cold",
            re.escape(
                "benchmark compiled-pattern module-helper workloads currently require "
                "`cache_mode` to be `warm` or `purged` so timed callbacks exclude "
                "pattern compilation"
            ),
            id="module-boundary-cache-mode",
        ),
    ),
)
def test_standard_benchmark_compiled_pattern_validation_matches_manifest_and_payload_entry_points(
    tmp_path: pathlib.Path,
    manifest_id: str,
    operation: str,
    cache_mode: str,
    error_pattern: str,
) -> None:
    family = operation.split(".", 1)[0]
    bucket = operation.replace(".", "-")

    manifest_source = f"""
    MANIFEST = {{
        "schema_version": 1,
        "manifest_id": {manifest_id!r},
        "workloads": [
            {{
                "id": "compiled-pattern-invalid-workload-contract",
                "bucket": {bucket!r},
                "family": {family!r},
                "operation": {operation!r},
                "pattern": "abc",
                "haystack": "abc",
                "expected_exception": None,
                "flags": 0,
                "use_compiled_pattern": True,
                "count": 0,
                "maxsplit": 0,
                "text_model": "str",
                "cache_mode": {cache_mode!r},
                "timing_scope": "module-helper-call",
            }},
        ],
    }}
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_compiled_pattern_contract.py",
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(
            {
                "manifest_id": manifest_id,
                "workload_id": "compiled-pattern-invalid-workload-contract",
                "bucket": bucket,
                "family": family,
                "operation": operation,
                "pattern": "abc",
                "haystack": "abc",
                "expected_exception": None,
                "flags": 0,
                "use_compiled_pattern": True,
                "count": 0,
                "maxsplit": 0,
                "text_model": "str",
                "cache_mode": cache_mode,
                "timing_scope": "module-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            }
        )


def test_standard_benchmark_manifest_loader_rejects_duplicate_ids(
    tmp_path: pathlib.Path,
) -> None:
    duplicate_modules = (
        (
            (
                "duplicate_benchmark_manifest_a.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-manifest-id",
                    "workloads": [
                        {
                            "id": "benchmark-workload-a",
                            "operation": "module.search",
                            "pattern": "abc",
                            "haystack": "abc",
                        },
                    ],
                }
                """,
            ),
            (
                "duplicate_benchmark_manifest_b.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-manifest-id",
                    "workloads": [
                        {
                            "id": "benchmark-workload-b",
                            "operation": "module.search",
                            "pattern": "def",
                            "haystack": "def",
                        },
                    ],
                }
                """,
            ),
            r"duplicate benchmark manifest id .*duplicate-benchmark-manifest-id",
        ),
        (
            (
                "duplicate_benchmark_workload_a.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-workload-a",
                    "workloads": [
                        {
                            "id": "duplicate-benchmark-workload-id",
                            "operation": "module.search",
                            "pattern": "abc",
                            "haystack": "abc",
                        },
                    ],
                }
                """,
            ),
            (
                "duplicate_benchmark_workload_b.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-workload-b",
                    "workloads": [
                        {
                            "id": "duplicate-benchmark-workload-id",
                            "operation": "module.search",
                            "pattern": "def",
                            "haystack": "def",
                        },
                    ],
                }
                """,
            ),
            r"duplicate benchmark workload id .*duplicate-benchmark-workload-id",
        ),
    )

    for first_module, second_module, error_pattern in duplicate_modules:
        first_path = _write_test_manifest(tmp_path, *first_module)
        second_path = _write_test_manifest(tmp_path, *second_module)
        with pytest.raises(ValueError, match=error_pattern):
            load_manifests([first_path, second_path])


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    _standard_benchmark_manifest_params(),
)
def test_standard_benchmark_manifest_keeps_expected_workloads_in_scope(
    definition: StandardBenchmarkAnchorContractDefinition,
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
    ) == _expected_workload_ids(definition, manifest_path)


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    _standard_benchmark_manifest_params(),
)
def test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    assert _unanchored_case_ids(definition, manifest_path) == ()


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert _anchored_case_ids(definition) == definition.expected_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    _standard_benchmark_definition_params(
        include_definition=_has_standard_benchmark_special_unanchored_workloads
    ),
)
def test_standard_benchmark_special_unanchored_workloads_stay_explicit(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert tuple(
        workload_id
        for manifest_path in definition.manifest_paths
        for workload_id in _all_unanchored_case_ids(definition, manifest_path)
    ) == definition.expected_special_unanchored_workload_ids


@pytest.mark.parametrize(
    "definition",
    _standard_benchmark_definition_params(
        include_definition=_has_standard_benchmark_special_unanchored_direct_parity_cases
    ),
)
def test_standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    workloads_by_id = _definition_workloads_by_id(definition)
    direct_parity_case_ids = _direct_parity_case_ids_by_signature(
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
    _standard_benchmark_definition_params(
        include_definition=_has_standard_benchmark_legacy_workloads
    ),
)
def test_standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert {
        key: case_ids
        for key, case_ids in _anchored_case_ids(definition).items()
        if key[1] in definition.expected_legacy_workload_ids
    } == _expected_legacy_anchor_case_ids(definition)


@pytest.mark.parametrize(
    "definition",
    _standard_benchmark_definition_params(
        include_definition=_runs_standard_benchmark_callback_result_parity
    ),
)
def test_standard_benchmark_workload_callbacks_match_anchor_case_results(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert_anchored_workload_case_result_parity(
        _expected_anchored_pairs(
            definition,
            expected_anchor_case_ids=_expected_callback_anchor_case_ids(definition),
        )
    )


@pytest.mark.parametrize(
    ("definition", "workload_id"),
    _standard_benchmark_special_unanchored_result_parity_params(),
)
def test_standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch(
    definition: StandardBenchmarkAnchorContractDefinition,
    workload_id: str,
) -> None:
    workload = _definition_workloads_by_id(definition)[workload_id]
    assert_benchmark_workload_matches_expected_result(
        workload,
        _manual_expected_result(workload),
    )


def test_freeze_signature_value_canonicalizes_nested_mappings_and_lists() -> None:
    value = {
        "b": [2, {"d": 4, "c": [5, 6]}],
        "a": {"y": 1, "x": 0},
    }

    assert support.freeze_signature_value(value) == (
        ("a", (("x", 0), ("y", 1))),
        ("b", (2, (("c", (5, 6)), ("d", 4)))),
    )


def test_published_case_ids_by_signature_groups_duplicate_case_ids(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    manifest = _synthetic_manifest(
        cases=(
            _synthetic_case("case-b", ("shared",)),
            _synthetic_case("case-a", ("shared",)),
            _synthetic_case("case-c", ("unique",)),
            _synthetic_case("ignored", None),
        )
    )
    monkeypatch.setattr(support, "published_fixture_manifests", lambda: (manifest,))

    observed = support.published_case_ids_by_signature(lambda case: case.signature)

    assert observed == {
        ("shared",): ("case-a", "case-b"),
        ("unique",): ("case-c",),
    }


def test_anchored_and_unanchored_workload_helpers_follow_signatures_and_filters(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",)),
        _synthetic_workload("excluded", ("shared",), include=False),
    )
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(workloads=workloads),
    )

    anchor_case_ids = {("shared",): ("case-a", "case-b")}
    workload_signature = lambda workload: workload.signature
    include_workload = lambda workload: workload.include

    assert support.anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=workload_signature,
        include_workload=include_workload,
    ) == {
        ("synthetic_boundary.py", "anchored"): ("case-a", "case-b"),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert support.unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=workload_signature,
        include_workload=include_workload,
    ) == ("unanchored",)


def test_expected_anchored_workload_case_pairs_return_matching_objects(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workload = _synthetic_workload("anchored", ("shared",))
    case = SimpleNamespace(case_id="case-1")
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(workloads=(workload,)),
    )
    monkeypatch.setattr(support, "published_cases_by_id", lambda: {"case-1": case})

    anchored_pairs = support.expected_anchored_workload_case_pairs(
        manifest_path,
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
        },
    )

    assert len(anchored_pairs) == 1
    anchored_pair = anchored_pairs[0]
    assert anchored_pair.manifest_name == "synthetic_boundary.py"
    assert anchored_pair.workload_id == "anchored"
    assert anchored_pair.case_id == "case-1"
    assert anchored_pair.workload is workload
    assert anchored_pair.case is case


def test_manifest_workload_cache_reuses_one_load_for_repeated_anchor_queries(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",)),
    )
    case = SimpleNamespace(case_id="case-1")
    load_calls: list[pathlib.Path] = []

    def _load_manifest(path: pathlib.Path) -> SimpleNamespace:
        load_calls.append(path)
        return _synthetic_manifest(workloads=workloads)

    monkeypatch.setattr(support, "load_manifest", _load_manifest)
    monkeypatch.setattr(support, "published_cases_by_id", lambda: {"case-1": case})

    anchor_case_ids = {("shared",): ("case-1",)}
    workload_signature = lambda workload: workload.signature

    assert support.anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=workload_signature,
    ) == {
        ("synthetic_boundary.py", "anchored"): ("case-1",),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert support.unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=workload_signature,
    ) == ("unanchored",)
    assert support.expected_anchored_workload_case_pairs(
        manifest_path,
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
        },
    ) == (
        support.AnchoredWorkloadCasePair(
            manifest_name="synthetic_boundary.py",
            workload_id="anchored",
            case_id="case-1",
            workload=workloads[0],
            case=case,
        ),
    )
    assert load_calls == [manifest_path]


def test_expected_anchored_workload_case_pairs_rejects_manifest_name_drift(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(
            workloads=(_synthetic_workload("anchored", ("shared",)),)
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: {"case-1": SimpleNamespace(case_id="case-1")},
    )

    with pytest.raises(AssertionError, match="does not match"):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("other_boundary.py", "anchored"): ("case-1",),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_multiple_case_ids(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(
            workloads=(_synthetic_workload("anchored", ("shared",)),)
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: {
            "case-1": SimpleNamespace(case_id="case-1"),
            "case-2": SimpleNamespace(case_id="case-2"),
        },
    )

    with pytest.raises(
        AssertionError,
        match="expected exactly one published correctness case",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "anchored"): ("case-1", "case-2"),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_missing_workload(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(
            workloads=(_synthetic_workload("anchored", ("shared",)),)
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: {"case-1": SimpleNamespace(case_id="case-1")},
    )

    with pytest.raises(
        AssertionError,
        match=r"expected anchored workload 'missing' to be in scope",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "missing"): ("case-1",),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_unpublished_case(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(
            workloads=(_synthetic_workload("anchored", ("shared",)),)
        ),
    )
    monkeypatch.setattr(support, "published_cases_by_id", lambda: {})

    with pytest.raises(
        AssertionError,
        match=r"expected anchored correctness case 'case-1' to be published",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "anchored"): ("case-1",),
            },
        )


def test_assert_anchored_workload_case_result_parity_delegates_expected_values(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    workload = _synthetic_workload("anchored", ("shared",))
    pair = support.AnchoredWorkloadCasePair(
        manifest_name="synthetic_boundary.py",
        workload_id="anchored",
        case_id="case-1",
        workload=workload,
        case=SimpleNamespace(case_id="case-1"),
    )
    calls: list[tuple[object, object]] = []
    monkeypatch.setattr(
        support,
        "run_correctness_case_with_cpython",
        lambda case: f"expected:{case.case_id}",
    )
    monkeypatch.setattr(
        support,
        "assert_benchmark_workload_matches_expected_result",
        lambda workload, expected: calls.append((workload, expected)),
    )

    support.assert_anchored_workload_case_result_parity((pair,))

    assert calls == [(workload, "expected:case-1")]


if __name__ == "__main__":
    unittest.main()

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_loader_contract.py",
        manifest_source,
    )
    manifest = load_manifest(manifest_path)
    workloads = manifest.workloads

    assert manifest.manifest_id == "python-benchmark-loader-contract"
    assert not hasattr(manifest, "defaults")
    assert [workload.workload_id for workload in workloads] == [
        "module-sub-callable-numbered-contract-str",
        "pattern-subn-callable-named-contract-str",
        "module-sub-callable-constant-contract-bytes",
    ]

    numbered_workload = workloads[0]
    assert numbered_workload.warmup_iterations == 2
    assert numbered_workload.sample_iterations == 3
    assert numbered_workload.timed_samples == 4
    assert numbered_workload.pattern_payload() == r"a((bc)+)d"
    assert numbered_workload.haystack_payload() == "zzabcbcdzz"
    numbered_replacement = numbered_workload.replacement_payload()
    assert callable(numbered_replacement)
    assert numbered_replacement.__module__ == "rebar_harness.benchmarks"
    assert numbered_replacement.__qualname__ == "callable_match_group"
    numbered_match = re.search(
        numbered_workload.pattern_payload(),
        numbered_workload.haystack_payload(),
    )
    assert numbered_match is not None
    assert numbered_replacement(numbered_match) == "bcbcx"
    assert workload_to_payload(numbered_workload)["replacement"] == {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x",
    }

    named_workload = workloads[1]
    assert named_workload.cache_mode == "purged"
    assert named_workload.timing_scope == "pattern-helper-call"
    named_replacement = named_workload.replacement_payload()
    assert callable(named_replacement)
    assert named_replacement.__module__ == "rebar_harness.benchmarks"
    assert named_replacement.__qualname__ == "callable_match_group"
    named_match = re.search(
        named_workload.pattern_payload(),
        named_workload.haystack_payload(),
    )
    assert named_match is not None
    assert named_replacement(named_match) == "<bc>"
    assert workload_to_payload(named_workload)["replacement"] == {
        "type": "callable_match_group",
        "group": "inner",
        "prefix": "<",
        "suffix": ">",
    }

    constant_bytes_workload = workloads[2]
    assert constant_bytes_workload.text_model == "bytes"
    assert constant_bytes_workload.pattern_payload() == rb"a((bc)+)d"
    assert constant_bytes_workload.haystack_payload() == b"zzabcbcdzz"
    constant_bytes_replacement = constant_bytes_workload.replacement_payload()
    assert callable(constant_bytes_replacement)
    assert constant_bytes_replacement.__module__ == "rebar_harness.benchmarks"
    assert constant_bytes_replacement.__qualname__ == "callable_constant"
    constant_bytes_match = re.search(
        constant_bytes_workload.pattern_payload(),
        constant_bytes_workload.haystack_payload(),
    )
    assert constant_bytes_match is not None
    assert constant_bytes_replacement(constant_bytes_match) == b"CONST"
    assert workload_to_payload(constant_bytes_workload)["replacement"] == {
        "type": "callable_constant",
        "value": {
            "type": "bytes",
            "value": "CONST",
            "encoding": "ascii",
        },
    }


def test_standard_benchmark_manifest_selected_workloads_preserves_filters_and_order(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-selection-contract",
        "workloads": [
            {
                "id": "compile-literal-cold",
                "operation": "compile",
                "pattern": "abc",
            },
            {
                "id": "compile-smoke-flagged",
                "operation": "compile",
                "pattern": "def",
                "smoke": True,
            },
            {
                "id": "compile-smoke-categorized",
                "operation": "compile",
                "pattern": "ghi",
                "categories": ["smoke"],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_selection_contract.py",
        manifest_source,
    )
    manifest = load_manifest(manifest_path)

    assert [workload.workload_id for workload in manifest.selected_workloads()] == [
        "compile-literal-cold",
        "compile-smoke-flagged",
        "compile-smoke-categorized",
    ]
    assert manifest.smoke_workload_ids() == [
        "compile-smoke-flagged",
        "compile-smoke-categorized",
    ]
    assert [
        workload.workload_id
        for workload in manifest.selected_workloads(
            selected_workload_ids=(
                "compile-smoke-categorized",
                "compile-literal-cold",
            )
        )
    ] == ["compile-smoke-categorized", "compile-literal-cold"]
    assert [
        workload.workload_id
        for workload in manifest.selected_workloads(
            selection_mode="smoke",
            selected_workload_ids=(
                "compile-smoke-categorized",
                "compile-literal-cold",
                "compile-smoke-flagged",
            ),
        )
    ] == ["compile-smoke-categorized", "compile-smoke-flagged"]

    with pytest.raises(
        AssertionError,
        match=(
            "missing workload definition 'missing-workload' in "
            "'python-benchmark-selection-contract'"
        ),
    ):
        manifest.selected_workloads(selected_workload_ids=("missing-workload",))

    with pytest.raises(
        AssertionError,
        match="unknown benchmark selection mode 'unknown'",
    ):
        manifest.selected_workloads(selection_mode="unknown")


def test_standard_benchmark_manifest_measures_expected_exception_workloads(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-exception-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
            "text_model": "str",
            "cache_mode": "warm",
            "timing_scope": "module-helper-call",
        },
        "workloads": [
            {
                "id": "module-subn-callable-numbered-conditional-expected-exception-contract-str",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": r"a(b)?c(?(1)d|e)",
                "replacement": {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "NoneType",
                },
                "haystack": "zzacezz",
                "count": 1,
                "categories": [
                    "replacement",
                    "callable",
                    "conditional",
                    "exception",
                    "str",
                ],
                "notes": [
                    "Ensures Python-backed benchmark manifests can measure expected callable replacement exceptions instead of failing the run."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_exception_contract.py",
        manifest_source,
    )
    workloads = load_manifest(manifest_path).workloads

    workload = workloads[0]
    payload = workload_to_payload(workload)
    assert payload["expected_exception"] == {
        "type": "TypeError",
        "message_substring": "NoneType",
    }

    baseline_probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name="re",
        adapter_name="cpython.re",
    )
    assert baseline_probe["status"] == "measured"
    assert baseline_probe["median_ns"] > 0

    implementation_probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name="rebar",
        adapter_name="rebar",
    )
    assert implementation_probe["status"] == "measured"
    assert implementation_probe["median_ns"] > 0


@pytest.mark.parametrize(
    ("raised_exception", "expected_reason"),
    (
        pytest.param(
            ValueError("wrong exception"),
            (
                "AssertionError: workload "
                "'module-search-expected-exception-mismatch-contract' raised "
                "ValueError: wrong exception instead of the expected 'TypeError' "
                "exception"
            ),
            id="wrong-type",
        ),
        pytest.param(
            TypeError("wrong detail"),
            (
                "AssertionError: workload "
                "'module-search-expected-exception-mismatch-contract' raised "
                "TypeError: wrong detail instead of the expected 'TypeError' "
                "exception"
            ),
            id="wrong-message",
        ),
        pytest.param(
            None,
            (
                "AssertionError: workload "
                "'module-search-expected-exception-mismatch-contract' did not "
                "raise the expected 'TypeError' exception"
            ),
            id="missing-exception",
        ),
    ),
)
def test_run_internal_workload_probe_reports_expected_exception_mismatches_as_unavailable(
    monkeypatch,
    raised_exception: Exception | None,
    expected_reason: str,
) -> None:
    payload = {
        "manifest_id": "python-benchmark-expected-exception-mismatch-contract",
        "workload_id": "module-search-expected-exception-mismatch-contract",
        "bucket": "module-search",
        "family": "module",
        "operation": "module.search",
        "pattern": "abc",
        "haystack": "abc",
        "flags": 0,
        "count": 0,
        "maxsplit": 0,
        "expected_exception": {
            "type": "TypeError",
            "message_substring": "expected detail",
        },
        "text_model": "str",
        "cache_mode": "warm",
        "timing_scope": "module-helper-call",
        "warmup_iterations": 1,
        "sample_iterations": 1,
        "timed_samples": 1,
        "notes": [],
        "categories": [],
        "syntax_features": [],
        "smoke": False,
    }

    def fake_build_callable(module: Any, import_name: str, workload: Any) -> Any:
        del module, import_name, workload

        def callback() -> None:
            if raised_exception is not None:
                raise raised_exception
            return None

        return callback

    monkeypatch.setattr(benchmarks, "build_callable", fake_build_callable)

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name="re",
        adapter_name="cpython.re",
    )

    assert probe == {
        "adapter": "cpython.re",
        "status": "unavailable",
        "reason": expected_reason,
    }


@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_reports_unsupported_operations_as_unavailable(
    tmp_path: pathlib.Path,
    import_name: str,
    adapter_name: str,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-unsupported-operation-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
        },
        "workloads": [
            {
                "id": "module-escape-unsupported-operation-contract",
                "bucket": "module-escape",
                "family": "module",
                "operation": "module.escape",
                "pattern": "abc",
                "haystack": "abcabc",
                "notes": [
                    "Ensures the internal benchmark probe reports unsupported workload operations as unavailable diagnostics instead of crashing."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_unsupported_operation_contract.py",
        manifest_source,
    )
    (workload,) = load_manifest(manifest_path).workloads

    assert run_internal_workload_probe(
        workload_payload=json.dumps(workload_to_payload(workload), sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    ) == {
        "adapter": adapter_name,
        "status": "unavailable",
        "reason": "ValueError: unsupported benchmark operation 'module.escape'",
    }


def test_standard_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-bytes-template-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            {
                "id": "module-sub-template-numbered-conditional-contract-bytes",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": r"a((b|c){2,})\\2(?(2)d|e)",
                "replacement": r"\\1x",
                "haystack": "abbbd",
                "text_model": "bytes",
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "categories": [
                    "replacement",
                    "template",
                    "numbered-group",
                    "bytes",
                ],
                "notes": [
                    "Ensures bytes benchmark manifests materialize numbered template replacements through the same published nested-group helper path."
                ],
            },
            {
                "id": "pattern-subn-template-named-conditional-contract-bytes",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
                "replacement": r"\\g<inner>x",
                "haystack": "zzacccdabcbccdzz",
                "count": 1,
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "categories": [
                    "replacement",
                    "template",
                    "named-group",
                    "bytes",
                ],
                "notes": [
                    "Ensures bytes benchmark manifests materialize named template replacements through the same published nested-group helper path."
                ],
            },
        ],
    }
    """
