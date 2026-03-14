from __future__ import annotations

import pathlib
import platform
import sys
from typing import Any


_KNOWN_GAP_STATUSES = {"known-gap", "unimplemented"}


def _correctness_summary(cases: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "executed_cases": len(cases),
        "failed_cases": sum(1 for case in cases if case["comparison"] == "fail"),
        "passed_cases": sum(1 for case in cases if case["comparison"] == "pass"),
        "skipped_cases": sum(1 for case in cases if case["comparison"] == "skip"),
        "total_cases": len(cases),
        "unimplemented_cases": sum(
            1 for case in cases if case["comparison"] == "unimplemented"
        ),
    }


def assert_correctness_summary_consistent(
    testcase: Any,
    scorecard: dict[str, Any],
    summary: dict[str, Any],
) -> None:
    testcase.assertEqual(summary, scorecard["summary"])
    testcase.assertEqual(scorecard["summary"], _correctness_summary(scorecard["cases"]))


def assert_correctness_layer_summary_consistent(
    testcase: Any,
    scorecard: dict[str, Any],
    layer_id: str,
) -> dict[str, Any]:
    layer = scorecard["layers"][layer_id]
    layer_cases = [case for case in scorecard["cases"] if case["layer"] == layer_id]
    testcase.assertEqual(layer["case_count"], len(layer_cases))
    testcase.assertEqual(layer["summary"], _correctness_summary(layer_cases))
    return layer


def _correctness_cases_for_suite(
    scorecard: dict[str, Any],
    suite: dict[str, Any],
) -> list[dict[str, Any]]:
    suite_cases = [
        case
        for case in scorecard["cases"]
        if case["manifest_id"] in suite["manifest_ids"] and case["layer"] == suite["layer"]
    ]
    if suite["operations"]:
        suite_cases = [
            case for case in suite_cases if case["operation"] in suite["operations"]
        ]
    if suite["text_models"]:
        suite_cases = [
            case
            for case in suite_cases
            if case.get("text_model") in suite["text_models"]
        ]
    return suite_cases


def find_correctness_suite_record(
    scorecard: dict[str, Any],
    suite_id: str,
) -> dict[str, Any]:
    for suite in scorecard["suites"]:
        if suite["id"] == suite_id:
            return suite
    raise AssertionError(f"missing correctness suite record for {suite_id!r}")


def find_correctness_case_record(
    scorecard: dict[str, Any],
    case_id: str,
) -> dict[str, Any]:
    for case in scorecard["cases"]:
        if case["id"] == case_id:
            return case
    raise AssertionError(f"missing correctness case record for {case_id!r}")


def assert_correctness_case_record_matches(
    testcase: Any,
    actual_case: dict[str, Any],
    expected_case: dict[str, Any],
) -> None:
    for key in (
        "id",
        "manifest_id",
        "suite_id",
        "layer",
        "family",
        "operation",
        "notes",
        "categories",
        "comparison",
        "comparison_notes",
        "observations",
    ):
        testcase.assertEqual(actual_case.get(key), expected_case.get(key))

    for key in ("text_model", "pattern", "flags", "helper", "kwargs"):
        testcase.assertEqual(actual_case.get(key), expected_case.get(key))

    actual_args = actual_case.get("args")
    expected_args = expected_case.get("args")
    testcase.assertEqual(bool(actual_args), bool(expected_args))
    if not actual_args or not expected_args:
        return

    testcase.assertEqual(len(actual_args), len(expected_args))
    for actual_arg, expected_arg in zip(actual_args, expected_args):
        if (
            isinstance(actual_arg, dict)
            and isinstance(expected_arg, dict)
            and actual_arg.get("type") == "callable"
            and expected_arg.get("type") == "callable"
        ):
            testcase.assertEqual(actual_arg["type"], expected_arg["type"])
            testcase.assertEqual(actual_arg["qualname"], expected_arg["qualname"])
            continue
        testcase.assertEqual(actual_arg, expected_arg)


def assert_correctness_suite_summary_consistent(
    testcase: Any,
    scorecard: dict[str, Any],
    suite_id: str,
) -> dict[str, Any]:
    suite = find_correctness_suite_record(scorecard, suite_id)
    suite_cases = _correctness_cases_for_suite(scorecard, suite)
    testcase.assertEqual(suite["case_count"], len(suite_cases))
    testcase.assertEqual(suite["summary"], _correctness_summary(suite_cases))
    return suite


def assert_correctness_report_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    summary: dict[str, Any],
    *,
    expected_phase: str,
    tracked_report_path: pathlib.Path | None = None,
) -> None:
    assert_correctness_summary_consistent(testcase, scorecard, summary)
    testcase.assertEqual(scorecard["schema_version"], "1.0")
    testcase.assertEqual(scorecard["suite"], "correctness")
    testcase.assertEqual(scorecard["phase"], expected_phase)

    baseline = scorecard["baseline"]
    testcase.assertEqual(
        baseline["python_implementation"],
        platform.python_implementation(),
    )
    testcase.assertEqual(baseline["python_version"], platform.python_version())
    testcase.assertEqual(baseline["python_version_family"], "3.12.x")
    testcase.assertEqual(
        baseline["python_build"],
        {
            "name": platform.python_build()[0],
            "date": platform.python_build()[1],
        },
    )
    testcase.assertEqual(baseline["python_compiler"], platform.python_compiler())
    testcase.assertEqual(baseline["platform"], platform.platform())
    testcase.assertEqual(baseline["executable"], sys.executable)
    testcase.assertEqual(baseline["re_module"], "re")
    testcase.assertEqual(baseline["oracle"], "cpython-stdlib-re")
    testcase.assertEqual(baseline["target_module"], "rebar")

    if tracked_report_path is not None:
        testcase.assertTrue(tracked_report_path.is_file())


def assert_correctness_fixture_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    *,
    expected_manifest_ids: tuple[str, ...],
    expected_paths: tuple[str, ...],
    expected_case_count: int,
) -> None:
    fixtures = scorecard["fixtures"]
    testcase.assertEqual(fixtures["manifest_count"], len(expected_manifest_ids))
    testcase.assertEqual(fixtures["manifest_ids"], list(expected_manifest_ids))
    testcase.assertEqual(fixtures["paths"], list(expected_paths))
    testcase.assertEqual(fixtures["case_count"], expected_case_count)


def assert_correctness_layer_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    layer_id: str,
    *,
    expected_manifest_ids: tuple[str, ...],
    expected_operations: tuple[str, ...],
    expected_text_models: tuple[str, ...],
) -> dict[str, Any]:
    layer = assert_correctness_layer_summary_consistent(testcase, scorecard, layer_id)
    testcase.assertEqual(layer["manifest_ids"], list(expected_manifest_ids))
    testcase.assertEqual(layer["operations"], list(expected_operations))
    testcase.assertEqual(layer["text_models"], list(expected_text_models))
    return layer


def assert_correctness_suite_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    suite_id: str,
    *,
    expected_manifest_ids: tuple[str, ...],
    expected_families: tuple[str, ...],
    expected_operations: tuple[str, ...],
    expected_text_models: tuple[str, ...],
) -> dict[str, Any]:
    suite = assert_correctness_suite_summary_consistent(testcase, scorecard, suite_id)
    testcase.assertEqual(suite["manifest_ids"], list(expected_manifest_ids))
    testcase.assertEqual(suite["families"], list(expected_families))
    testcase.assertEqual(suite["operations"], list(expected_operations))
    testcase.assertEqual(suite["text_models"], list(expected_text_models))
    return suite


def assert_correctness_suite_case_accounting(
    testcase: Any,
    suite: dict[str, Any],
    *,
    expected_case_count: int,
) -> None:
    testcase.assertEqual(suite["summary"]["total_cases"], expected_case_count)
    testcase.assertEqual(suite["summary"]["failed_cases"], 0)
    testcase.assertEqual(suite["summary"]["skipped_cases"], 0)
    testcase.assertEqual(
        suite["summary"]["passed_cases"] + suite["summary"]["unimplemented_cases"],
        expected_case_count,
    )


def assert_benchmark_summary_consistent(
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
        scorecard["manifests"].get("regression-matrix", {}).get("workload_count", 0),
    )

    for cache_mode, expected_count in scorecard["summary"]["workloads_by_cache_mode"].items():
        testcase.assertEqual(
            expected_count,
            sum(1 for workload in workloads if workload["cache_mode"] == cache_mode),
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


def assert_source_tree_benchmark_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    summary: dict[str, Any],
    *,
    expected_phase: str,
    expected_runner_version: str,
    expected_manifest_paths: list[str],
    tracked_report_path: pathlib.Path | None = None,
) -> None:
    assert_benchmark_summary_consistent(testcase, scorecard, summary)
    testcase.assertEqual(scorecard["schema_version"], "1.0")
    testcase.assertEqual(scorecard["phase"], expected_phase)
    testcase.assertEqual(
        scorecard["baseline"]["python_implementation"],
        platform.python_implementation(),
    )
    testcase.assertEqual(scorecard["baseline"]["python_version"], platform.python_version())
    testcase.assertEqual(scorecard["implementation"]["module_name"], "rebar")
    testcase.assertEqual(scorecard["implementation"]["adapter"], "rebar.module-surface")
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
    testcase.assertIsInstance(scorecard["implementation"]["native_module_loaded"], bool)
    testcase.assertIn(
        "not requested",
        scorecard["implementation"]["native_unavailable_reason"],
    )
    testcase.assertEqual(scorecard["environment"]["runner_version"], expected_runner_version)
    testcase.assertEqual(scorecard["artifacts"]["manifest"], None)
    testcase.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
    testcase.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
    testcase.assertEqual(scorecard["artifacts"]["selection_mode"], "full")
    testcase.assertEqual(
        [artifact["manifest"] for artifact in scorecard["artifacts"]["manifests"]],
        expected_manifest_paths,
    )
    if tracked_report_path is not None:
        testcase.assertTrue(tracked_report_path.is_file())


def assert_benchmark_manifest_contract(
    testcase: Any,
    manifest_summary: dict[str, Any],
    manifest_record: dict[str, Any],
    *,
    manifest_document: dict[str, Any],
    manifest_path: str,
    known_gap_count: int,
) -> None:
    workloads = manifest_document["workloads"]
    smoke_ids = [workload["id"] for workload in workloads if workload.get("smoke", False)]
    operations = sorted({workload["operation"] for workload in workloads})

    testcase.assertEqual(manifest_summary["workload_count"], len(workloads))
    testcase.assertEqual(manifest_summary["selected_workload_count"], len(workloads))
    testcase.assertEqual(manifest_summary["measured_workloads"], len(workloads) - known_gap_count)
    testcase.assertEqual(manifest_summary["known_gap_count"], known_gap_count)
    testcase.assertEqual(
        manifest_summary["readiness"],
        "measured" if known_gap_count == 0 else "partial",
    )
    testcase.assertEqual(manifest_summary["selection_mode"], "full")
    testcase.assertEqual(manifest_summary["available_smoke_workload_count"], len(smoke_ids))
    testcase.assertEqual(manifest_summary["smoke_workload_ids"], smoke_ids)
    testcase.assertEqual(manifest_summary["operations"], operations)
    if "spec_refs" in manifest_document:
        testcase.assertEqual(manifest_summary["spec_refs"], manifest_document["spec_refs"])
    if "notes" in manifest_document:
        testcase.assertEqual(manifest_summary["notes"], manifest_document["notes"])

    testcase.assertEqual(manifest_record["manifest_id"], manifest_document["manifest_id"])
    testcase.assertEqual(manifest_record["manifest"], manifest_path)
    testcase.assertEqual(manifest_record["smoke_workload_ids"], smoke_ids)


def assert_benchmark_workload_contract(
    testcase: Any,
    workload_record: dict[str, Any],
    *,
    manifest_id: str,
    workload_document: dict[str, Any],
    expected_status: str,
) -> None:
    expected_syntax_features = workload_document.get(
        "syntax_features",
        workload_document.get("categories", []),
    )
    testcase.assertEqual(workload_record["manifest_id"], manifest_id)
    testcase.assertEqual(
        workload_record["family"],
        workload_document.get("family", "parser"),
    )
    testcase.assertEqual(workload_record["operation"], workload_document["operation"])
    testcase.assertEqual(workload_record["pattern"], workload_document.get("pattern", ""))
    testcase.assertEqual(workload_record["haystack"], workload_document.get("haystack"))
    testcase.assertEqual(workload_record["replacement"], workload_document.get("replacement"))
    testcase.assertEqual(workload_record["flags"], workload_document.get("flags", 0))
    testcase.assertEqual(workload_record["count"], workload_document.get("count", 0))
    testcase.assertEqual(workload_record["maxsplit"], workload_document.get("maxsplit", 0))
    testcase.assertEqual(
        workload_record["text_model"],
        workload_document.get("text_model", "str"),
    )
    testcase.assertEqual(workload_record["cache_mode"], workload_document["cache_mode"])
    testcase.assertEqual(workload_record["timing_scope"], workload_document["timing_scope"])
    testcase.assertEqual(workload_record["syntax_features"], expected_syntax_features)
    testcase.assertEqual(workload_record["status"], expected_status)
    testcase.assertEqual(
        workload_record["baseline_timing"]["status"],
        "measured",
    )
    testcase.assertGreater(workload_record["baseline_ns"], 0)
    testcase.assertEqual(
        workload_record["implementation_timing"]["status"],
        expected_status,
    )
    if expected_status == "measured":
        testcase.assertGreater(workload_record["implementation_ns"], 0)
        testcase.assertIsInstance(workload_record["speedup_vs_cpython"], float)


def find_manifest_record(scorecard: dict[str, Any], manifest_id: str) -> dict[str, Any]:
    for manifest_record in scorecard["artifacts"]["manifests"]:
        if manifest_record["manifest_id"] == manifest_id:
            return manifest_record
    raise AssertionError(f"missing manifest record for {manifest_id!r}")


def find_workload_record(scorecard: dict[str, Any], workload_id: str) -> dict[str, Any]:
    for workload in scorecard["workloads"]:
        if workload["id"] == workload_id:
            return workload
    raise AssertionError(f"missing workload record for {workload_id!r}")


def find_workload_document(
    manifest_document: dict[str, Any],
    workload_id: str,
) -> dict[str, Any]:
    for workload in manifest_document["workloads"]:
        if workload["id"] == workload_id:
            return workload
    raise AssertionError(
        f"missing workload definition {workload_id!r} in {manifest_document['manifest_id']!r}"
    )
