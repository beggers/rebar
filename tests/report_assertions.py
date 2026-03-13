from __future__ import annotations

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


def assert_correctness_summary_consistent(testcase: Any, scorecard: dict[str, Any], summary: dict[str, Any]) -> None:
    testcase.assertEqual(summary, scorecard["summary"])
    testcase.assertEqual(scorecard["summary"], _correctness_summary(scorecard["cases"]))


def assert_correctness_layer_summary_consistent(
    testcase: Any,
    scorecard: dict[str, Any],
    layer_id: str,
) -> dict[str, Any]:
    layer = scorecard["layers"][layer_id]
    layer_cases = [case for case in scorecard["cases"] if case["layer"] == layer_id]
    testcase.assertEqual(layer["summary"], _correctness_summary(layer_cases))
    return layer


def assert_correctness_suite_summary_consistent(
    testcase: Any,
    scorecard: dict[str, Any],
    suite_id: str,
) -> dict[str, Any]:
    suite = next(suite for suite in scorecard["suites"] if suite["id"] == suite_id)
    suite_case_ids = set(suite["case_ids"])
    suite_cases = [case for case in scorecard["cases"] if case["id"] in suite_case_ids]
    testcase.assertEqual(suite["summary"], _correctness_summary(suite_cases))
    return suite


def assert_benchmark_summary_consistent(testcase: Any, scorecard: dict[str, Any], summary: dict[str, Any]) -> None:
    workloads = scorecard["workloads"]
    testcase.assertEqual(summary, scorecard["summary"])
    testcase.assertEqual(
        scorecard["summary"],
        {
            "known_gap_count": sum(
                1 for workload in workloads if workload["status"] in _KNOWN_GAP_STATUSES
            ),
            "measured_workloads": sum(1 for workload in workloads if workload["status"] == "measured"),
            "module_workloads": sum(1 for workload in workloads if workload["family"] == "module"),
            "parser_workloads": sum(1 for workload in workloads if workload["family"] == "parser"),
            "regression_workloads": sum(
                1 for workload in workloads if workload["family"] == "regression"
            ),
            "total_workloads": len(workloads),
        },
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
            sum(1 for workload in family_workloads if workload["status"] in _KNOWN_GAP_STATUSES),
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
