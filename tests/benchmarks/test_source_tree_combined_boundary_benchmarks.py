from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from functools import cache
import json
import pathlib
import re
import shutil
import subprocess
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
    BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR,
    COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR,
    PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
    Workload,
    build_callable,
    determine_phase,
    determine_runner_version,
    load_manifest,
    load_manifests,
    published_benchmark_manifests,
    run_internal_workload_probe,
    select_benchmark_manifest_path,
    select_benchmark_manifest_paths,
    select_workloads,
    workload_to_payload,
)
from rebar_harness.correctness import published_fixture_manifests
from rebar_harness.scorecard_io import build_cpython_baseline
from tests.harness_cli_support import REPO_ROOT, run_harness_scorecard
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    assert_match_result_parity,
    assert_pattern_parity,
)
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.py"

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
        workload_record["text_model"],
        workload_payload.get("text_model", "str"),
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

BASE_SOURCE_TREE_MANIFEST_IDS = frozenset({"compile-matrix", "regression-matrix"})

ZERO_GAP_PROMOTION_MANIFEST_IDS = (
    "grouped-named-boundary",
    "numbered-backreference-boundary",
    "nested-group-boundary",
    "optional-group-boundary",
)

COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS = (
    "exact-repeat-quantified-group-boundary",
    "ranged-repeat-quantified-group-boundary",
)

ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES = (
    (
        "exact-repeat-quantified-group-boundary",
        (
            "module-search-numbered-broader-ranged-repeat-group-cold-gap",
        ),
        13,
        None,
    ),
    (
        "ranged-repeat-quantified-group-boundary",
        (
            "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
        ),
        8,
        None,
    ),
    (
        "quantified-alternation-boundary",
        (
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
        84,
        84,
    ),
)

_ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID = {
    manifest_id: (
        expected_workload_ids,
        expected_measured_workload_count,
        expected_total_workload_count,
    )
    for (
        manifest_id,
        expected_workload_ids,
        expected_measured_workload_count,
        expected_total_workload_count,
    ) in ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES
}


def zero_gap_fully_measured_manifest_case(
    manifest_id: str,
) -> tuple[str, tuple[str, ...], int, int | None]:
    try:
        (
            expected_workload_ids,
            expected_measured_workload_count,
            expected_total_workload_count,
        ) = _ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID[manifest_id]
    except KeyError as exc:
        raise AssertionError(
            f"unknown zero-gap fully measured manifest {manifest_id!r}"
        ) from exc

    return (
        manifest_id,
        expected_workload_ids,
        expected_measured_workload_count,
        expected_total_workload_count,
    )


ZERO_GAP_BYTES_CASES = (
    (
        "wider-ranged-repeat-quantified-group-boundary",
        (
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-conditional-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-broader-range-conditional-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-bytes",
        ),
        100,
        100,
    ),
    (
        "wider-ranged-repeat-quantified-group-boundary",
        (
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
        ),
        100,
        100,
    ),
    (
        "wider-ranged-repeat-quantified-group-boundary",
        (
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
        ),
        100,
        100,
    ),
    (
        "wider-ranged-repeat-quantified-group-boundary",
        (
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-third-repetition-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-upper-bound-all-de-purged-bytes",
        ),
        100,
        100,
    ),
    (
        "wider-ranged-repeat-quantified-group-boundary",
        (
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-conditional-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-bytes",
        ),
        100,
        100,
    ),
    (
        "wider-ranged-repeat-quantified-group-boundary",
        (
            "module-compile-numbered-wider-ranged-repeat-group-open-ended-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-open-ended-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-open-ended-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-bytes",
        ),
        100,
        100,
    ),
    (
        "open-ended-quantified-group-boundary",
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
        72,
        72,
    ),
    (
        "open-ended-quantified-group-boundary",
        (
            "module-compile-numbered-open-ended-group-alternation-cold-bytes",
            "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-alternation-warm-bytes",
            "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
        ),
        72,
        72,
    ),
    (
        "open-ended-quantified-group-boundary",
        (
            "module-compile-numbered-open-ended-group-broader-range-cold-bytes",
            "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-broader-range-warm-bytes",
            "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
        ),
        72,
        72,
    ),
    (
        "open-ended-quantified-group-boundary",
        (
            "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes",
            "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes",
            "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
        ),
        72,
        72,
    ),
    (
        "open-ended-quantified-group-boundary",
        (
            "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
        ),
        72,
        72,
    ),
    (
        "branch-local-backreference-boundary",
        (
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-bytes",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-bytes",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-bytes",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-bytes",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-bytes",
        ),
        30,
        30,
    ),
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
class _SourceTreeManifestKnownGapCountOverride:
    manifest_id: str
    known_gap_count: int


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
    _manifest_known_gap_count_overrides: tuple[
        _SourceTreeManifestKnownGapCountOverride, ...
    ] = ()


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
class SourceTreeCombinedManifestExpectationDefinition:
    known_gap_workload_ids: tuple[str, ...] | None = None
    representative_measured_workload_ids: tuple[str, ...] | None = None
    representative_known_gap_workload_ids: tuple[str, ...] | None = None
    shape_expectation: SourceTreeCombinedManifestShapeExpectation | None = None


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
    "compile-smoke": _SourceTreeScorecardDefinition(
        manifest_ids=("compile-smoke",),
        selection_mode="full",
        _manifest_known_gap_count_overrides=(
            _SourceTreeManifestKnownGapCountOverride(
                manifest_id="compile-smoke",
                known_gap_count=1,
            ),
        ),
        expected_first_deferred=SourceTreeDeferredExpectation(
            area="module-boundary",
            follow_up="RBR-0015",
        ),
        representative_measured_workload_ids=("compile-literal-cold",),
        representative_known_gap_workload_ids=("compile-character-class-warm",),
    ),
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
    known_gap_workload_ids: tuple[str, ...] | None = None,
    representative_measured_workload_ids: tuple[str, ...] | None = None,
    representative_known_gap_workload_ids: tuple[str, ...] | None = None,
    shape_expectation: SourceTreeCombinedManifestShapeExpectation | None = None,
) -> SourceTreeCombinedManifestExpectationDefinition:
    return SourceTreeCombinedManifestExpectationDefinition(
        known_gap_workload_ids=known_gap_workload_ids,
        representative_measured_workload_ids=representative_measured_workload_ids,
        representative_known_gap_workload_ids=representative_known_gap_workload_ids,
        shape_expectation=shape_expectation,
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


SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS = {
    "compile-matrix": _combined_manifest_definition(),
    "module-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
            "import-module-cold",
            "module-search-grouped-literal-cold-hit",
            "module-search-literal-warm-hit",
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
    "collection-replacement-boundary": _combined_manifest_definition(),
    "literal-flag-boundary": _combined_manifest_definition(),
    "grouped-named-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-search-grouped-segment-cold-gap",
            "pattern-search-grouped-segment-warm-gap",
        ),
    ),
    "numbered-backreference-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-search-numbered-backreference-segment-cold-gap",
            "pattern-search-numbered-backreference-prefix-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "grouped-segment-boundary": _combined_manifest_definition(),
    "literal-alternation-boundary": _combined_manifest_definition(),
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
    "grouped-alternation-callable-replacement-boundary": _combined_manifest_definition(),
    "nested-group-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-search-triple-nested-group-cold-gap",
            "pattern-fullmatch-named-quantified-nested-group-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "nested-group-alternation-boundary": _combined_manifest_definition(),
    "nested-group-replacement-boundary": _combined_manifest_definition(),
    "nested-group-callable-replacement-boundary": _combined_manifest_definition(),
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
    ),
    "optional-group-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-search-numbered-optional-group-conditional-cold-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "exact-repeat-quantified-group-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=_ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID[
            "exact-repeat-quantified-group-boundary"
        ][0],
        representative_known_gap_workload_ids=(),
    ),
    "ranged-repeat-quantified-group-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=_ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID[
            "ranged-repeat-quantified-group-boundary"
        ][0],
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
    ),
    "quantified-alternation-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=_ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID[
            "quantified-alternation-boundary"
        ][0],
    ),
    "optional-group-alternation-boundary": _combined_manifest_definition(),
    "conditional-group-exists-boundary": _combined_manifest_definition(),
    "conditional-group-exists-no-else-boundary": _combined_manifest_definition(),
    "conditional-group-exists-empty-else-boundary": _combined_manifest_definition(),
    "conditional-group-exists-empty-yes-else-boundary": _combined_manifest_definition(),
    "conditional-group-exists-fully-empty-boundary": _combined_manifest_definition(),
    "regression-matrix": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "regression-parser-bytes-backreference-purged",
        ),
    ),
}


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
    compile_smoke_manifest = load_manifest(
        select_benchmark_manifest_path(COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR)
    )
    manifests = (compile_smoke_manifest, *published_benchmark_manifests())
    return {manifest.manifest_id: manifest for manifest in manifests}


def _source_tree_manifest_record(manifest_id: str) -> BenchmarkManifest:
    try:
        return _source_tree_manifest_records()[manifest_id]
    except KeyError as exc:
        raise AssertionError(f"unknown benchmark manifest id {manifest_id!r}") from exc


def _source_tree_manifests_for_ids(
    manifest_ids: Iterable[str],
) -> list[BenchmarkManifest]:
    return [_source_tree_manifest_record(manifest_id) for manifest_id in manifest_ids]


def relative_manifest_path(path: pathlib.Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def run_source_tree_benchmark_scorecard(
    manifest_paths: Iterable[pathlib.Path],
    *,
    smoke: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    command = []
    for manifest_path in manifest_paths:
        command.extend(("--manifest", str(manifest_path)))
    if smoke:
        command.append("--smoke")

    return run_harness_scorecard(
        "rebar_harness.benchmarks",
        command,
        report_name="benchmarks.json",
    )


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
    explicit_known_gap_counts = {
        override.manifest_id: override.known_gap_count
        for override in case_definition._manifest_known_gap_count_overrides
    }
    known_gap_counts: dict[str, int] = {}
    for manifest in manifests:
        manifest_id = manifest.manifest_id
        if manifest_id in explicit_known_gap_counts:
            known_gap_counts[manifest_id] = explicit_known_gap_counts[manifest_id]
            continue
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
    manifests = _source_tree_manifests_for_ids(manifest_ids)
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
    target_manifest_ids = tuple(
        manifest.manifest_id
        for manifest in published_benchmark_manifests()
        if manifest.manifest_id not in BASE_SOURCE_TREE_MANIFEST_IDS
    )
    target_ids = set(target_manifest_ids)
    missing_expectations = target_ids - set(SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS)
    if missing_expectations:
        raise AssertionError(
            "source-tree combined manifest expectations drifted from the published full-suite selector: "
            f"missing {sorted(missing_expectations)}"
        )
    return target_manifest_ids


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
        _, scorecard = run_source_tree_benchmark_scorecard(
            [case.target_manifest.path]
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
        expected_measured_workload_count: int,
        expected_total_workload_count: int,
    ) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
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
        for manifest_id in ZERO_GAP_PROMOTION_MANIFEST_IDS:
            with self.subTest(manifest_id=manifest_id):
                self._assert_zero_gap_manifest_representative_promotion(
                    manifest_id
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
        for manifest_id in COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS:
            (
                _,
                expected_workload_ids,
                expected_measured_workload_count,
                _,
            ) = zero_gap_fully_measured_manifest_case(manifest_id)
            with self.subTest(manifest_id=manifest_id):
                manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                    manifest_id
                ]
                self.assertIsNone(manifest_definition.known_gap_workload_ids)
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
        for (
            manifest_id,
            expected_workload_ids,
            expected_measured_workload_count,
            expected_total_workload_count,
        ) in ZERO_GAP_BYTES_CASES:
            with self.subTest(manifest_id=manifest_id):
                self._assert_zero_gap_bytes_representative_subset(
                    manifest_id,
                    expected_workload_ids,
                    expected_measured_workload_count,
                    expected_total_workload_count,
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
        (
            manifest_id,
            expected_workload_ids,
            expected_measured_workload_count,
            expected_total_workload_count,
        ) = zero_gap_fully_measured_manifest_case(
            "quantified-alternation-boundary"
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
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

        _, scorecard = run_source_tree_benchmark_scorecard(
            [REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"]
        )

        manifest_summary = scorecard["manifests"]["regression-matrix"]
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(manifest_summary["measured_workloads"], 5)

        self._assert_manifest_workload_contracts(
            scorecard_case.manifest_for_id("regression-matrix"),
            scorecard,
            (("regression-parser-bytes-backreference-purged", "measured"),),
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
                summary, scorecard = run_source_tree_benchmark_scorecard(
                    [manifest.path for manifest in case.manifests],
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
                _, scorecard = run_source_tree_benchmark_scorecard(
                    [manifest.path for manifest in case.manifests]
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
        _, scorecard = run_source_tree_benchmark_scorecard(
            [manifest.path for manifest in case.manifests]
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

    def test_regression_pack_full_promotes_bytes_backreference_probe_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("regression-pack-full")
        self.assertIn(
            "regression-parser-bytes-backreference-purged",
            case.representative_measured_workload_ids,
        )
        self.assertNotIn(
            "regression-parser-bytes-backreference-purged",
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
        compile_smoke = source_tree_scorecard_case("compile-smoke")
        self.assertEqual(
            compile_smoke.selected_workload_ids_for_manifest("compile-smoke"),
            (
                "compile-literal-cold",
                "compile-character-class-warm",
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
        for manifest_id, expected_workload_ids, _, _ in ZERO_GAP_BYTES_CASES:
            with self.subTest(manifest_id=manifest_id):
                self._assert_zero_gap_representative_workload_subset(
                    manifest_id,
                    expected_workload_ids,
                )

    def test_combined_cases_treat_counted_repeat_manifest_pair_as_fully_measured(
        self,
    ) -> None:
        for manifest_id in COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS:
            _, expected_workload_ids, _, _ = zero_gap_fully_measured_manifest_case(
                manifest_id
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

    def test_compile_smoke_case_restores_single_manifest_expectations(self) -> None:
        case = source_tree_scorecard_case("compile-smoke")
        manifest_expectation = case.manifest_expectations["compile-smoke"]
        self.assertEqual(manifest_expectation.known_gap_count, 1)
        self.assertEqual(
            manifest_expectation.representative_measured_workload_ids,
            ("compile-literal-cold",),
        )
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            ("compile-character-class-warm",),
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
                summary, scorecard = run_source_tree_benchmark_scorecard(
                    [manifest.path for manifest in case.manifests],
                    smoke=case.selection_mode == "smoke",
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

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
REGRESSION_MATRIX_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"
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

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR,
    COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR,
    PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
    build_callable,
    load_manifest,
    load_manifests,
    published_benchmark_manifests,
    run_internal_workload_probe,
    select_benchmark_manifest_path,
    select_benchmark_manifest_paths,
    workload_to_payload,
)
from rebar_harness.correctness import published_fixture_manifests
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    assert_match_result_parity,
    assert_pattern_parity,
)

support = sys.modules[__name__]
MATURIN = shutil.which("maturin")
COMPILE_SMOKE_PROVENANCE_MANIFEST_PATH = select_benchmark_manifest_path(
    COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR
)
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


def _duplicate_items(counter: Counter[str]) -> list[str]:
    return sorted(item for item, count in counter.items() if count > 1)


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
        expected = run_correctness_case_with_cpython(anchored_pair.case)
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

    if workload.operation in {"module.search", "pattern.fullmatch"}:
        assert_match_result_parity(
            "stdlib",
            observed,
            expected,
            check_regs=True,
        )
        return

    if workload.operation in {
        "module.sub",
        "module.subn",
        "pattern.sub",
        "pattern.subn",
    }:
        assert observed == expected
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
        return getattr(re, case.helper)(*case.args, **case.kwargs)

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
    callback_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] = field(
        default_factory=dict
    )
    expected_special_unanchored_workload_ids: tuple[str, ...] = ()
    direct_parity_supplemental_cases: tuple[Any, ...] = ()
    run_special_unanchored_result_parity: bool = False


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


EXPECTED_COMPILE_ANCHOR_CASE_IDS = {
    ("compile_matrix.py", "compile-inline-locale-bytes-warm"): (
        "bytes-inline-locale-flag-success",
    ),
    ("compile_matrix.py", "compile-lookbehind-cold"): (
        "str-fixed-width-lookbehind-success",
    ),
    ("compile_matrix.py", "compile-character-class-ignorecase-warm"): (
        "str-character-class-ignorecase-success",
    ),
    ("compile_matrix.py", "compile-possessive-quantifier-cold"): (
        "str-possessive-quantifier-success",
    ),
    ("compile_matrix.py", "compile-atomic-group-purged"): (
        "str-atomic-group-success",
    ),
    ("compile_matrix.py", "compile-parser-stress-cold"): (
        "str-parser-stress-compile-proxy-success",
    ),
    ("regression_matrix.py", "regression-parser-atomic-lookbehind-cold"): (
        "str-parser-stress-compile-proxy-success",
    ),
    ("regression_matrix.py", "regression-parser-bytes-backreference-purged"): (
        "bytes-named-backreference-compile-proxy-success",
    ),
    ("regression_matrix.py", "regression-module-compile-verbose-purged"): (
        "workflow-compile-str-verbose-regression",
    ),
}

OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID = (
    "module-search-numbered-optional-group-conditional-cold-gap"
)
EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS = {
    (
        "optional_group_boundary.py",
        OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID,
    ): ("optional-group-conditional-module-search-present-str",),
}

EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS = frozenset(
    {
        "module-search-triple-nested-group-cold-gap",
        "pattern-fullmatch-named-quantified-nested-group-purged-gap",
    }
)
EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS = {
    ("nested_group_boundary.py", "module-compile-nested-group-cold-str"): (
        "nested-group-compile-metadata-str",
    ),
    ("nested_group_boundary.py", "module-search-nested-group-warm-str"): (
        "nested-group-module-search-str",
    ),
    ("nested_group_boundary.py", "pattern-fullmatch-nested-group-purged-str"): (
        "nested-group-pattern-fullmatch-str",
    ),
    ("nested_group_boundary.py", "module-compile-named-nested-group-warm-str"): (
        "named-nested-group-compile-metadata-str",
    ),
    ("nested_group_boundary.py", "module-search-named-nested-group-warm-str"): (
        "named-nested-group-module-search-str",
    ),
    ("nested_group_boundary.py", "pattern-fullmatch-named-nested-group-purged-str"): (
        "named-nested-group-pattern-fullmatch-str",
    ),
}

EXACT_REPEAT_EXPECTED_ANCHOR_CASE_IDS = {
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-compile-numbered-exact-repeat-group-cold-str",
    ): ("exact-repeat-numbered-group-compile-metadata-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-search-numbered-exact-repeat-group-warm-str",
    ): ("exact-repeat-numbered-group-module-search-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-exact-repeat-group-purged-str",
    ): ("exact-repeat-numbered-group-pattern-fullmatch-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-compile-named-exact-repeat-group-warm-str",
    ): ("exact-repeat-named-group-compile-metadata-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-search-named-exact-repeat-group-warm-str",
    ): ("exact-repeat-named-group-module-search-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "pattern-fullmatch-named-exact-repeat-group-purged-str",
    ): ("exact-repeat-named-group-pattern-fullmatch-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-search-numbered-broader-ranged-repeat-group-cold-gap",
    ): (
        "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
    ),
}

RANGED_REPEAT_EXPECTED_ANCHOR_CASE_IDS = {
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-compile-numbered-ranged-repeat-group-cold-str",
    ): ("ranged-repeat-numbered-group-compile-metadata-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-search-numbered-ranged-repeat-group-lower-bound-warm-str",
    ): ("ranged-repeat-numbered-group-module-search-lower-bound-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-ranged-repeat-group-upper-bound-purged-str",
    ): ("ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-compile-named-ranged-repeat-group-warm-str",
    ): ("ranged-repeat-named-group-compile-metadata-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-search-named-ranged-repeat-group-upper-bound-warm-str",
    ): ("ranged-repeat-named-group-module-search-upper-bound-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "pattern-fullmatch-named-ranged-repeat-group-lower-bound-purged-str",
    ): ("ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
    ): (
        "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
    ),
}

EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS = frozenset(
    {
        "module-sub-template-nested-grouped-alternation-warm-gap",
        "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
    }
)
EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS = {
    (
        "grouped_alternation_boundary.py",
        "module-compile-grouped-alternation-cold-str",
    ): ("grouped-alternation-compile-metadata-str",),
    (
        "grouped_alternation_boundary.py",
        "module-search-grouped-alternation-warm-str",
    ): ("grouped-alternation-module-search-str",),
    (
        "grouped_alternation_boundary.py",
        "pattern-fullmatch-grouped-alternation-purged-str",
    ): ("grouped-alternation-pattern-fullmatch-str",),
    (
        "grouped_alternation_boundary.py",
        "module-compile-named-grouped-alternation-warm-str",
    ): ("named-grouped-alternation-compile-metadata-str",),
    (
        "grouped_alternation_boundary.py",
        "module-search-named-grouped-alternation-warm-str",
    ): ("named-grouped-alternation-module-search-str",),
    (
        "grouped_alternation_boundary.py",
        "pattern-fullmatch-named-grouped-alternation-purged-str",
    ): ("named-grouped-alternation-pattern-fullmatch-str",),
    (
        "grouped_alternation_boundary.py",
        "module-sub-template-nested-grouped-alternation-warm-gap",
    ): ("module-sub-template-nested-group-alternation-numbered-wrapper-str",),
    (
        "grouped_alternation_boundary.py",
        "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
    ): (
        "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
    ),
}

EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_WORKLOAD_IDS = frozenset(
    {
        "module-sub-template-nested-grouped-alternation-cold-gap",
        "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
    }
)
EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS = {
    (
        "grouped_alternation_replacement_boundary.py",
        "module-sub-template-grouped-alternation-warm-str",
    ): ("module-sub-template-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "module-subn-template-grouped-alternation-warm-str",
    ): ("module-subn-template-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-sub-template-grouped-alternation-purged-str",
    ): ("pattern-sub-template-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-subn-template-grouped-alternation-purged-str",
    ): ("pattern-subn-template-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "module-sub-template-named-grouped-alternation-warm-str",
    ): ("module-sub-template-named-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "module-subn-template-named-grouped-alternation-warm-str",
    ): ("module-subn-template-named-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-sub-template-named-grouped-alternation-purged-str",
    ): ("pattern-sub-template-named-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-subn-template-named-grouped-alternation-purged-str",
    ): ("pattern-subn-template-named-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "module-sub-template-nested-grouped-alternation-cold-gap",
    ): ("module-sub-template-nested-group-alternation-numbered-outer-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
    ): (
        "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
    ),
}
EXPECTED_NESTED_GROUP_REPLACEMENT_ANCHOR_CASE_IDS = {
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-nested-group-numbered-warm-str",
    ): ("module-sub-template-nested-group-numbered-str",),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-nested-group-numbered-warm-str",
    ): ("module-subn-template-nested-group-numbered-str",),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-nested-group-numbered-purged-str",
    ): ("pattern-sub-template-nested-group-numbered-str",),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-nested-group-numbered-purged-str",
    ): ("pattern-subn-template-nested-group-numbered-str",),
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-nested-group-named-warm-str",
    ): ("module-sub-template-nested-group-named-str",),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-nested-group-named-warm-str",
    ): ("module-subn-template-nested-group-named-str",),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-nested-group-named-purged-str",
    ): ("pattern-sub-template-nested-group-named-str",),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-nested-group-named-purged-str",
    ): ("pattern-subn-template-nested-group-named-str",),
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-numbered-quantified-nested-group-replacement-lower-bound-warm-str",
    ): ("module-sub-template-quantified-nested-group-numbered-lower-bound-str",),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-numbered-quantified-nested-group-replacement-first-match-only-warm-str",
    ): ("module-subn-template-quantified-nested-group-numbered-first-match-only-str",),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-named-quantified-nested-group-replacement-repeated-outer-purged-str",
    ): ("pattern-sub-template-quantified-nested-group-named-repeated-outer-capture-str",),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap",
    ): ("pattern-subn-template-quantified-nested-group-named-first-match-only-str",),
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
    ): (
        "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
    ): (
        "module-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
    ): (
        "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
    ): (
        "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
    ): (
        "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
    ): (
        "module-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str",
    ): (
        "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
    ): (
        "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
    ): (
        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str",
    ): (
        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
    ): (
        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str",
    ): (
        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
    ): (
        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str",
    ): (
        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str",
    ): (
        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str",
    ): (
        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
    ),
}
EXPECTED_NESTED_GROUP_REPLACEMENT_SPECIAL_UNANCHORED_WORKLOAD_IDS = (
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
)

EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS = (
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
)

EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS = {
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-alternation-cold-str",
    ): ("open-ended-quantified-group-alternation-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-str",
    ): ("open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-str",
    ): ("open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-alternation-warm-str",
    ): ("open-ended-quantified-group-alternation-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-alternation-lower-bound-de-warm-str",
    ): ("open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-str",
    ): ("open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-alternation-cold-bytes",
    ): ("open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-alternation-warm-bytes",
    ): ("open-ended-quantified-group-alternation-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-conditional-cold-str",
    ): ("open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-cold-str",
    ): ("broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-broader-range-cold-gap",
    ): (
        "broader-range-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-str",
    ): ("broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-warm-str",
    ): ("broader-range-open-ended-quantified-group-alternation-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-str",
    ): ("broader-range-open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-str",
    ): ("broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-cold-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-warm-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-conditional-cold-str",
    ): ("broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap",
    ): (
        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-conditional-warm-str",
    ): ("broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-str",
    ): ("broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-str",
    ): ("broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-str",
    ): ("open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-conditional-warm-str",
    ): ("open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-str",
    ): ("open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-str",
    ): ("open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-conditional-cold-bytes",
    ): ("open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-conditional-warm-bytes",
    ): ("open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-backtracking-heavy-cold-str",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-str",
    ): (
        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-str",
    ): (
        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-backtracking-heavy-warm-str",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-str",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-gap",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-fourth-repetition-short-only-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",),
}

OPEN_ENDED_DIRECT_PARITY_BYTES_CASES = (
    *OPEN_ENDED_ALTERNATION_BYTES_CASES,
    *OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    *OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    *BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    *BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    *BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
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


def _is_measured_nested_group_workload(workload: Any) -> bool:
    return workload.workload_id not in EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS


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


def _is_non_special_open_ended_workload(workload: Any) -> bool:
    return workload.workload_id not in EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS


def _is_non_special_nested_group_replacement_workload(workload: Any) -> bool:
    return (
        workload.workload_id
        not in EXPECTED_NESTED_GROUP_REPLACEMENT_SPECIAL_UNANCHORED_WORKLOAD_IDS
    )


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
            return re.compile(pattern, workload.flags)
        if workload.operation == "module.search":
            return re.search(pattern, workload.haystack_payload(), workload.flags)
        if workload.operation == "pattern.fullmatch":
            compiled = re.compile(pattern, workload.flags)
            return compiled.fullmatch(workload.haystack_payload())
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
        expected_anchor_case_ids=EXPECTED_COMPILE_ANCHOR_CASE_IDS,
        include_workload=_is_compile_proxy_workload,
        correctness_case_signature=_compile_proxy_correctness_case_signature,
        workload_signature=_compile_proxy_workload_signature,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="optional-group-conditional",
        manifest_paths=(OPTIONAL_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS,
        include_workload=_is_optional_group_conditional_workload,
        correctness_case_signature=_optional_group_correctness_case_signature,
        workload_signature=_optional_group_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="nested-group",
        manifest_paths=(NESTED_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS,
        include_workload=_is_measured_nested_group_workload,
        correctness_case_signature=_nested_group_correctness_case_signature,
        workload_signature=_nested_group_workload_signature,
        run_callback_result_parity=True,
        expected_excluded_workload_ids=EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="exact-repeat",
        manifest_paths=(EXACT_REPEAT_MANIFEST_PATH,),
        expected_anchor_case_ids=EXACT_REPEAT_EXPECTED_ANCHOR_CASE_IDS,
        include_workload=_is_non_alternation_counted_repeat_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="ranged-repeat",
        manifest_paths=(RANGED_REPEAT_MANIFEST_PATH,),
        expected_anchor_case_ids=RANGED_REPEAT_EXPECTED_ANCHOR_CASE_IDS,
        include_workload=_is_non_alternation_counted_repeat_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="grouped-alternation",
        manifest_paths=(GROUPED_ALTERNATION_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS,
        include_workload=_include_all_workloads,
        correctness_case_signature=_grouped_alternation_correctness_case_signature,
        workload_signature=_grouped_alternation_workload_signature,
        run_callback_result_parity=True,
        expected_legacy_workload_ids=EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS,
        callback_anchor_case_ids=_anchor_case_subset(
            EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS,
            EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS,
        ),
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="grouped-alternation-replacement",
        manifest_paths=(GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS,
        include_workload=_include_all_workloads,
        correctness_case_signature=(
            _grouped_alternation_replacement_correctness_case_signature
        ),
        workload_signature=_grouped_alternation_replacement_workload_signature,
        run_callback_result_parity=True,
        expected_legacy_workload_ids=(
            EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_WORKLOAD_IDS
        ),
        callback_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="nested-group-replacement",
        manifest_paths=(NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_NESTED_GROUP_REPLACEMENT_ANCHOR_CASE_IDS,
        include_workload=_is_non_special_nested_group_replacement_workload,
        correctness_case_signature=(
            _grouped_alternation_replacement_correctness_case_signature
        ),
        workload_signature=_grouped_alternation_replacement_workload_signature,
        run_callback_result_parity=True,
        expected_special_unanchored_workload_ids=(
            EXPECTED_NESTED_GROUP_REPLACEMENT_SPECIAL_UNANCHORED_WORKLOAD_IDS
        ),
        run_special_unanchored_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="open-ended-grouped-alternation",
        manifest_paths=(OPEN_ENDED_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS,
        include_workload=_is_non_special_open_ended_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
        expected_special_unanchored_workload_ids=(
            EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS
        ),
        direct_parity_supplemental_cases=OPEN_ENDED_DIRECT_PARITY_BYTES_CASES,
        run_special_unanchored_result_parity=True,
    ),
)

STANDARD_BENCHMARK_MANIFEST_DEFINITIONS = tuple(
    (definition, manifest_path)
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    for manifest_path in definition.manifest_paths
)
STANDARD_BENCHMARK_MANIFEST_IDS = [
    f"{definition.name}:{manifest_path.name}"
    for definition, manifest_path in STANDARD_BENCHMARK_MANIFEST_DEFINITIONS
]
STANDARD_BENCHMARK_LEGACY_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.expected_legacy_workload_ids
)
STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.run_callback_result_parity
)
STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.expected_special_unanchored_workload_ids
)
STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DIRECT_PARITY_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS
    if definition.direct_parity_supplemental_cases
)
STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES = tuple(
    (definition, workload_id)
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.run_special_unanchored_result_parity
    for workload_id in definition.expected_special_unanchored_workload_ids
)
STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_IDS = [
    f"{definition.name}:{workload_id}"
    for definition, workload_id in STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES
]


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
        include_workload=definition.include_workload,
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
        include_workload=definition.include_workload,
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
    if definition.callback_anchor_case_ids:
        return definition.callback_anchor_case_ids
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
                include_workload=definition.include_workload,
            )
        )
    return tuple(anchored_pairs)


def test_default_benchmark_manifest_selector_rejects_unknown_selector() -> None:
    with pytest.raises(ValueError, match="unknown benchmark manifest selector"):
        select_benchmark_manifest_paths("missing-selector")


def test_default_benchmark_single_manifest_selector_helper_rejects_full_suite_selector() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "benchmark manifest selector 'published-full-suite' "
            "does not resolve to exactly one path"
        ),
    ):
        select_benchmark_manifest_path(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR)


def test_default_benchmark_published_full_suite_selector_covers_tracked_manifests_except_compile_smoke() -> None:
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )
    tracked_manifest_paths = _tracked_benchmark_manifest_paths()
    compile_smoke_manifest_path = select_benchmark_manifest_path(
        COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR
    )

    assert set(published_manifest_paths) == set(tracked_manifest_paths) - {
        compile_smoke_manifest_path
    }
    assert len(published_manifest_paths) == len(set(published_manifest_paths))

    for path in published_manifest_paths:
        assert path.is_relative_to(BENCHMARK_WORKLOADS_ROOT)
        assert path.is_file()
        assert path.suffix == ".py"


def test_default_benchmark_shared_selectors_keep_expected_inventory_shapes() -> None:
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )
    native_smoke_manifest_paths = select_benchmark_manifest_paths(
        BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR
    )
    compile_smoke_manifest_path = select_benchmark_manifest_path(
        COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR
    )

    assert tuple(path.name for path in native_smoke_manifest_paths) == (
        "pattern_boundary.py",
        "collection_replacement_boundary.py",
        "literal_flag_boundary.py",
    )
    assert set(native_smoke_manifest_paths).issubset(set(published_manifest_paths))
    assert compile_smoke_manifest_path.name == "compile_smoke.py"
    assert compile_smoke_manifest_path.is_relative_to(BENCHMARK_WORKLOADS_ROOT)
    assert compile_smoke_manifest_path not in published_manifest_paths


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

    assert _duplicate_items(Counter(manifest_ids)) == []
    assert _duplicate_items(Counter(workload.workload_id for workload in workloads)) == []

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
            manifest_paths=[COMPILE_SMOKE_PROVENANCE_MANIFEST_PATH],
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


@pytest.mark.skipif(
    MATURIN is None,
    reason="built-native benchmark provenance smoke requires a maturin executable on PATH",
)
def test_run_benchmarks_reports_built_native_provenance_when_available(
    tmp_path: pathlib.Path,
) -> None:
    scorecard = benchmarks.run_benchmarks(
        manifest_paths=[COMPILE_SMOKE_PROVENANCE_MANIFEST_PATH],
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
    STANDARD_BENCHMARK_MANIFEST_DEFINITIONS,
    ids=STANDARD_BENCHMARK_MANIFEST_IDS,
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
        if definition.include_workload(workload)
    ) == _expected_workload_ids(definition, manifest_path)


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    STANDARD_BENCHMARK_MANIFEST_DEFINITIONS,
    ids=STANDARD_BENCHMARK_MANIFEST_IDS,
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
    STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS,
    ids=lambda definition: definition.name,
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
    STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DIRECT_PARITY_DEFINITIONS,
    ids=lambda definition: definition.name,
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
    STANDARD_BENCHMARK_LEGACY_DEFINITIONS,
    ids=lambda definition: definition.name,
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
    STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS,
    ids=lambda definition: definition.name,
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
    STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES,
    ids=STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_IDS,
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
