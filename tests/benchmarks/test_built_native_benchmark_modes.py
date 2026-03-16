from __future__ import annotations

import pathlib
import shutil
import tempfile
import unittest
from collections.abc import Callable
from unittest import mock

from rebar_harness import benchmarks

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
MATURIN = shutil.which("maturin")
_MISSING_MATURIN_REASON = (
    "built-native mode unavailable because no `maturin` executable was found on PATH"
)
_MISSING_MATURIN_PATTERN = "no `maturin` executable was found on PATH"


def _build_minimal_scorecard() -> dict[str, object]:
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


def _assert_native_mode_requires_real_built_runtime(
    testcase: unittest.TestCase,
    *,
    runner: Callable[..., dict[str, object]],
    report_name: str,
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = pathlib.Path(temp_dir) / report_name
        with mock.patch.object(
            benchmarks,
            "provision_built_native_runtime",
            return_value=(None, None, _MISSING_MATURIN_REASON),
        ):
            with testcase.assertRaisesRegex(
                benchmarks.NativeBenchmarkProvisionError,
                _MISSING_MATURIN_PATTERN,
            ):
                runner(report_path=report_path)

        testcase.assertFalse(report_path.exists())


def _run_native_benchmark_with_report(
    testcase: unittest.TestCase,
    *,
    runner: Callable[..., dict[str, object]],
    report_name: str,
) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = pathlib.Path(temp_dir) / report_name
        scorecard = runner(report_path=report_path)
        testcase.assertTrue(report_path.is_file())

    return scorecard


def _assert_native_runner_uses_optional_report_path(
    testcase: unittest.TestCase,
    *,
    runner: Callable[..., dict[str, object]],
    expected_manifest_selector: str,
    expected_smoke_only: bool,
) -> None:
    expected_manifest_paths = benchmarks.select_benchmark_manifest_paths(
        expected_manifest_selector
    )
    scorecard = _build_minimal_scorecard()
    explicit_report_path = REPO_ROOT / "reports" / "benchmarks" / "explicit-native-check.json"

    with mock.patch.object(benchmarks, "run_benchmarks", return_value=scorecard) as mocked_run:
        returned = runner()

    testcase.assertIs(returned, scorecard)
    mocked_run.assert_called_once_with(
        manifest_paths=list(expected_manifest_paths),
        report_path=None,
        smoke_only=expected_smoke_only,
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        allow_fallback=False,
    )

    with mock.patch.object(benchmarks, "run_benchmarks", return_value=scorecard) as mocked_run:
        returned = runner(report_path=explicit_report_path)

    testcase.assertIs(returned, scorecard)
    mocked_run.assert_called_once_with(
        manifest_paths=list(expected_manifest_paths),
        report_path=explicit_report_path,
        smoke_only=expected_smoke_only,
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        allow_fallback=False,
    )


def _assert_native_cli_uses_optional_report_path(
    testcase: unittest.TestCase,
    *,
    flag: str,
    runner_name: str,
    report_name: str,
) -> None:
    scorecard = _build_minimal_scorecard()

    with (
        mock.patch.object(benchmarks, runner_name, return_value=scorecard) as mocked_runner,
        mock.patch("builtins.print"),
    ):
        exit_code = benchmarks.main([flag])

    testcase.assertEqual(exit_code, 0)
    mocked_runner.assert_called_once_with(report_path=None)

    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = pathlib.Path(temp_dir) / report_name
        with (
            mock.patch.object(
                benchmarks, runner_name, return_value=scorecard
            ) as mocked_runner,
            mock.patch("builtins.print"),
        ):
            exit_code = benchmarks.main([flag, "--report", str(report_path)])

    testcase.assertEqual(exit_code, 0)
    mocked_runner.assert_called_once_with(report_path=report_path)


def _assert_built_native_combined_scorecard_fields(
    testcase: unittest.TestCase,
    scorecard: dict[str, object],
    *,
    expected_phase: str,
    expected_selection_mode: str,
    expected_manifest_count: int,
) -> None:
    implementation = scorecard["implementation"]
    environment = scorecard["environment"]
    artifacts = scorecard["artifacts"]

    testcase.assertEqual(scorecard["schema_version"], "1.0")
    testcase.assertEqual(scorecard["phase"], expected_phase)
    testcase.assertEqual(implementation["module_name"], "rebar")
    testcase.assertEqual(implementation["adapter_mode_requested"], "built-native")
    testcase.assertEqual(implementation["adapter_mode_resolved"], "built-native")
    testcase.assertEqual(implementation["build_mode"], "built-native")
    testcase.assertEqual(implementation["timing_path"], "built-native")
    testcase.assertTrue(implementation["native_module_loaded"])
    testcase.assertEqual(implementation["native_module_name"], "rebar._rebar")
    testcase.assertEqual(implementation["native_build_tool"], "maturin")
    testcase.assertTrue(str(implementation["native_wheel"]).startswith("rebar-"))
    testcase.assertIsNone(implementation["native_unavailable_reason"])
    testcase.assertEqual(
        environment["execution_model"],
        "single-interpreter subprocess workload probes against a built native wheel",
    )
    testcase.assertEqual(artifacts["manifest"], None)
    testcase.assertEqual(artifacts["manifest_id"], "combined-benchmark-suite")
    testcase.assertEqual(artifacts["selection_mode"], expected_selection_mode)
    testcase.assertEqual(len(artifacts["manifests"]), expected_manifest_count)


class BuiltNativeBenchmarkSmokeTest(unittest.TestCase):
    def test_native_smoke_runner_uses_explicit_report_paths_only(self) -> None:
        _assert_native_runner_uses_optional_report_path(
            self,
            runner=benchmarks.run_built_native_smoke_benchmarks,
            expected_manifest_selector=benchmarks.BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR,
            expected_smoke_only=True,
        )

    def test_native_smoke_cli_uses_explicit_report_paths_only(self) -> None:
        _assert_native_cli_uses_optional_report_path(
            self,
            flag="--native-smoke",
            runner_name="run_built_native_smoke_benchmarks",
            report_name="benchmarks-native-smoke.json",
        )

    def test_native_smoke_mode_requires_real_built_runtime(self) -> None:
        _assert_native_mode_requires_real_built_runtime(
            self,
            runner=benchmarks.run_built_native_smoke_benchmarks,
            report_name="benchmarks-native-smoke.json",
        )

    @unittest.skipUnless(
        MATURIN is not None,
        "built-native benchmark smoke requires a maturin executable on PATH",
    )
    def test_native_smoke_mode_writes_built_native_report(self) -> None:
        scorecard = _run_native_benchmark_with_report(
            self,
            runner=benchmarks.run_built_native_smoke_benchmarks,
            report_name="benchmarks-native-smoke.json",
        )
        _assert_built_native_combined_scorecard_fields(
            self,
            scorecard,
            expected_phase="phase2-module-boundary-suite",
            expected_selection_mode="smoke",
            expected_manifest_count=3,
        )
        self.assertEqual(scorecard["implementation"]["adapter"], "rebar.module-surface")
        self.assertEqual(scorecard["summary"]["total_workloads"], 6)
        self.assertEqual(scorecard["summary"]["parser_workloads"], 0)
        self.assertEqual(scorecard["summary"]["module_workloads"], 6)
        self.assertEqual(scorecard["summary"]["regression_workloads"], 0)
        self.assertEqual(scorecard["summary"]["measured_workloads"], 6)
        self.assertEqual(scorecard["summary"]["known_gap_count"], 0)
        self.assertEqual(
            [workload["id"] for workload in scorecard["workloads"]],
            [
                "pattern-search-literal-warm-hit",
                "pattern-fullmatch-bytes-purged-hit",
                "module-split-literal-warm-str",
                "pattern-subn-literal-purged-bytes",
                "module-search-inline-flag-warm-str-hit",
                "pattern-fullmatch-ignorecase-purged-bytes-hit",
            ],
        )


class BuiltNativeFullSuiteBenchmarkTest(unittest.TestCase):
    def test_native_full_runner_uses_explicit_report_paths_only(self) -> None:
        _assert_native_runner_uses_optional_report_path(
            self,
            runner=benchmarks.run_built_native_full_benchmarks,
            expected_manifest_selector=benchmarks.PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
            expected_smoke_only=False,
        )

    def test_native_full_cli_uses_explicit_report_paths_only(self) -> None:
        _assert_native_cli_uses_optional_report_path(
            self,
            flag="--native-full",
            runner_name="run_built_native_full_benchmarks",
            report_name="benchmarks-native-full.json",
        )

    def test_native_full_mode_requires_real_built_runtime(self) -> None:
        _assert_native_mode_requires_real_built_runtime(
            self,
            runner=benchmarks.run_built_native_full_benchmarks,
            report_name="benchmarks-native-full.json",
        )

    @unittest.skipUnless(
        MATURIN is not None,
        "built-native full-suite benchmark requires a maturin executable on PATH",
    )
    def test_native_full_mode_writes_built_native_report_with_known_gaps(self) -> None:
        published_manifest_paths = benchmarks.select_benchmark_manifest_paths(
            benchmarks.PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
        )
        _, selected_workloads = benchmarks.load_manifests(list(published_manifest_paths))
        expected_total = len(selected_workloads)
        expected_parser = sum(1 for workload in selected_workloads if workload.family == "parser")
        expected_module = sum(1 for workload in selected_workloads if workload.family == "module")
        expected_regression = sum(
            1 for workload in selected_workloads if workload.manifest_id == "regression-matrix"
        )

        scorecard = _run_native_benchmark_with_report(
            self,
            runner=benchmarks.run_built_native_full_benchmarks,
            report_name="benchmarks-native-full.json",
        )
        _assert_built_native_combined_scorecard_fields(
            self,
            scorecard,
            expected_phase="phase3-regression-stability-suite",
            expected_selection_mode="full",
            expected_manifest_count=len(published_manifest_paths),
        )
        self.assertEqual(scorecard["summary"]["total_workloads"], expected_total)
        self.assertEqual(scorecard["summary"]["parser_workloads"], expected_parser)
        self.assertEqual(scorecard["summary"]["module_workloads"], expected_module)
        self.assertEqual(scorecard["summary"]["regression_workloads"], expected_regression)

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
        self.assertGreater(len(unimplemented_workloads), 0)
        self.assertEqual(scorecard["summary"]["known_gap_count"], len(unimplemented_workloads))
        self.assertEqual(scorecard["summary"]["measured_workloads"], len(measured_workloads))
        self.assertEqual(len(measured_workloads) + len(unimplemented_workloads), expected_total)


if __name__ == "__main__":
    unittest.main()
