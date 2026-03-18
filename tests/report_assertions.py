from __future__ import annotations

from collections.abc import Callable, Iterable
import pathlib
from typing import Any

from rebar_harness.benchmarks import BenchmarkManifest, Workload, workload_to_payload
from rebar_harness.scorecard_io import build_cpython_baseline

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


def _correctness_observation_summary(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    outcomes: dict[str, int] = {}
    warning_case_count = 0
    exception_case_count = 0
    warning_categories: dict[str, int] = {}
    exception_types: dict[str, int] = {}

    for observation in observations:
        outcome = str(observation["outcome"])
        outcomes[outcome] = outcomes.get(outcome, 0) + 1

        warnings_payload = observation.get("warnings") or []
        if warnings_payload:
            warning_case_count += 1
            for warning_record in warnings_payload:
                category = str(warning_record["category"])
                warning_categories[category] = warning_categories.get(category, 0) + 1

        exception = observation.get("exception")
        if exception is not None:
            exception_case_count += 1
            exception_type = str(exception["type"])
            exception_types[exception_type] = exception_types.get(exception_type, 0) + 1

    return {
        "outcomes": dict(sorted(outcomes.items())),
        "warning_case_count": warning_case_count,
        "exception_case_count": exception_case_count,
        "warning_categories": dict(sorted(warning_categories.items())),
        "exception_types": dict(sorted(exception_types.items())),
    }


def _correctness_diagnostics(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "by_adapter": {
            "cpython": _correctness_observation_summary(
                [case["observations"]["cpython"] for case in cases]
            ),
            "rebar": _correctness_observation_summary(
                [case["observations"]["rebar"] for case in cases]
            ),
        }
    }


def _assert_tracked_report_exists(
    testcase: Any,
    tracked_report_path: pathlib.Path | None,
) -> None:
    if tracked_report_path is not None:
        testcase.assertTrue(tracked_report_path.is_file())


def _assert_cpython_baseline_contract(
    testcase: Any,
    baseline: dict[str, Any],
    *,
    expected_re_module: str,
) -> None:
    expected_baseline = {
        **build_cpython_baseline(version_family="3.12.x"),
        "re_module": expected_re_module,
    }
    for key, expected_value in expected_baseline.items():
        testcase.assertEqual(baseline[key], expected_value)


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


def _find_record_by_id(
    records: Iterable[Any],
    *,
    record_id: str,
    get_id: Callable[[Any], str],
    missing_message: str,
) -> Any:
    for record in records:
        if get_id(record) == record_id:
            return record
    raise AssertionError(missing_message)


def find_correctness_suite_record(
    scorecard: dict[str, Any],
    suite_id: str,
) -> dict[str, Any]:
    return _find_record_by_id(
        scorecard["suites"],
        record_id=suite_id,
        get_id=lambda suite: str(suite["id"]),
        missing_message=f"missing correctness suite record for {suite_id!r}",
    )


def find_correctness_case_record(
    scorecard: dict[str, Any],
    case_id: str,
) -> dict[str, Any]:
    return _find_record_by_id(
        scorecard["cases"],
        record_id=case_id,
        get_id=lambda case: str(case["id"]),
        missing_message=f"missing correctness case record for {case_id!r}",
    )


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


def _assert_correctness_suite_summary_consistent(
    testcase: Any,
    scorecard: dict[str, Any],
    suite_id: str,
) -> dict[str, Any]:
    suite = find_correctness_suite_record(scorecard, suite_id)
    suite_cases = _correctness_cases_for_suite(scorecard, suite)
    testcase.assertEqual(suite["case_count"], len(suite_cases))
    testcase.assertEqual(suite["summary"], _correctness_summary(suite_cases))
    testcase.assertEqual(suite["diagnostics"], _correctness_diagnostics(suite_cases))
    return suite


def assert_correctness_suites_present(
    testcase: Any,
    scorecard: dict[str, Any],
    suite_ids: Iterable[str],
) -> tuple[dict[str, Any], ...]:
    return tuple(
        _assert_correctness_suite_summary_consistent(testcase, scorecard, suite_id)
        for suite_id in suite_ids
    )


def assert_correctness_report_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    summary: dict[str, Any],
    *,
    expected_phase: str,
    tracked_report_path: pathlib.Path | None = None,
) -> None:
    testcase.assertEqual(summary, scorecard["summary"])
    testcase.assertEqual(scorecard["summary"], _correctness_summary(scorecard["cases"]))
    testcase.assertEqual(scorecard["schema_version"], "1.0")
    testcase.assertEqual(scorecard["suite"], "correctness")
    testcase.assertEqual(scorecard["phase"], expected_phase)

    baseline = scorecard["baseline"]
    _assert_cpython_baseline_contract(
        testcase,
        baseline,
        expected_re_module="re",
    )
    testcase.assertEqual(baseline["oracle"], "cpython-stdlib-re")
    testcase.assertEqual(baseline["target_module"], "rebar")
    testcase.assertEqual(scorecard["diagnostics"], _correctness_diagnostics(scorecard["cases"]))
    _assert_tracked_report_exists(testcase, tracked_report_path)


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
    if len(expected_manifest_ids) == 1:
        testcase.assertEqual(fixtures["manifest_id"], expected_manifest_ids[0])
        testcase.assertEqual(fixtures["path"], expected_paths[0])


def assert_correctness_layer_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    layer_id: str,
    *,
    expected_manifest_ids: tuple[str, ...],
    expected_operations: tuple[str, ...],
    expected_text_models: tuple[str, ...],
) -> dict[str, Any]:
    layer = scorecard["layers"][layer_id]
    layer_cases = [case for case in scorecard["cases"] if case["layer"] == layer_id]
    testcase.assertEqual(layer["case_count"], len(layer_cases))
    testcase.assertEqual(layer["summary"], _correctness_summary(layer_cases))
    testcase.assertEqual(layer["diagnostics"], _correctness_diagnostics(layer_cases))
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
    suite = _assert_correctness_suite_summary_consistent(testcase, scorecard, suite_id)
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


def _smoke_workload_ids(workloads: list[Workload]) -> list[str]:
    return [workload.workload_id for workload in workloads if workload.smoke]


def _artifact_manifest_record(
    manifest_path: str,
    manifest: BenchmarkManifest,
) -> dict[str, Any]:
    return {
        "manifest": manifest_path,
        "manifest_id": manifest.manifest_id,
        "manifest_schema_version": manifest.schema_version,
        "workload_count": len(manifest.workloads),
        "smoke_workload_ids": _smoke_workload_ids(manifest.workloads),
        "spec_refs": list(manifest.spec_refs),
    }


def _selected_manifest_workloads(
    manifest: BenchmarkManifest,
    *,
    selected_workload_ids: tuple[str, ...] | None,
) -> list[Workload]:
    if selected_workload_ids is None:
        return list(manifest.workloads)

    workloads_by_id = {
        workload.workload_id: workload for workload in manifest.workloads
    }
    selected_workloads: list[Workload] = []
    for workload_id in selected_workload_ids:
        if workload_id not in workloads_by_id:
            raise AssertionError(
                f"missing workload definition {workload_id!r} in {manifest.manifest_id!r}"
            )
        selected_workloads.append(workloads_by_id[workload_id])
    return selected_workloads


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
    _assert_cpython_baseline_contract(
        testcase,
        scorecard["baseline"],
        expected_re_module="re",
    )
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
    _assert_tracked_report_exists(testcase, tracked_report_path)


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
    selected_workloads = _selected_manifest_workloads(
        manifest,
        selected_workload_ids=selected_workload_ids,
    )
    smoke_ids = _smoke_workload_ids(workloads)
    operations = sorted({workload.operation for workload in selected_workloads})
    families = sorted(
        {
            workload.family
            for workload in selected_workloads
        }
    )

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
    return _find_record_by_id(
        scorecard["artifacts"]["manifests"],
        record_id=manifest_id,
        get_id=lambda manifest_record: str(manifest_record["manifest_id"]),
        missing_message=f"missing manifest record for {manifest_id!r}",
    )


def find_workload_record(scorecard: dict[str, Any], workload_id: str) -> dict[str, Any]:
    return _find_record_by_id(
        scorecard["workloads"],
        record_id=workload_id,
        get_id=lambda workload: str(workload["id"]),
        missing_message=f"missing workload record for {workload_id!r}",
    )


def find_workload_document(
    manifest: BenchmarkManifest,
    workload_id: str,
) -> Workload:
    return _find_record_by_id(
        manifest.workloads,
        record_id=workload_id,
        get_id=lambda workload: workload.workload_id,
        missing_message=(
            f"missing workload definition {workload_id!r} in {manifest.manifest_id!r}"
        ),
    )
