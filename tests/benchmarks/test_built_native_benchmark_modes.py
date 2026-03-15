from __future__ import annotations

import unittest

from tests.benchmarks.native_benchmark_test_support import (
    MATURIN,
    assert_built_native_combined_scorecard_fields,
    assert_native_cli_uses_optional_report_path,
    assert_native_mode_requires_real_built_runtime,
    assert_native_runner_uses_optional_report_path,
    benchmarks,
    run_native_benchmark_with_report,
)


class BuiltNativeBenchmarkSmokeTest(unittest.TestCase):
    def test_native_smoke_runner_uses_explicit_report_paths_only(self) -> None:
        assert_native_runner_uses_optional_report_path(
            self,
            runner=benchmarks.run_built_native_smoke_benchmarks,
            expected_manifest_selector=benchmarks.BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR,
            expected_smoke_only=True,
        )

    def test_native_smoke_cli_uses_explicit_report_paths_only(self) -> None:
        assert_native_cli_uses_optional_report_path(
            self,
            flag="--native-smoke",
            runner_name="run_built_native_smoke_benchmarks",
            report_name="benchmarks-native-smoke.json",
        )

    def test_native_smoke_mode_requires_real_built_runtime(self) -> None:
        assert_native_mode_requires_real_built_runtime(
            self,
            runner=benchmarks.run_built_native_smoke_benchmarks,
            report_name="benchmarks-native-smoke.json",
        )

    @unittest.skipUnless(
        MATURIN is not None,
        "built-native benchmark smoke requires a maturin executable on PATH",
    )
    def test_native_smoke_mode_writes_built_native_report(self) -> None:
        scorecard = run_native_benchmark_with_report(
            self,
            runner=benchmarks.run_built_native_smoke_benchmarks,
            report_name="benchmarks-native-smoke.json",
        )
        assert_built_native_combined_scorecard_fields(
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
        assert_native_runner_uses_optional_report_path(
            self,
            runner=benchmarks.run_built_native_full_benchmarks,
            expected_manifest_selector=benchmarks.PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
            expected_smoke_only=False,
        )

    def test_native_full_cli_uses_explicit_report_paths_only(self) -> None:
        assert_native_cli_uses_optional_report_path(
            self,
            flag="--native-full",
            runner_name="run_built_native_full_benchmarks",
            report_name="benchmarks-native-full.json",
        )

    def test_native_full_mode_requires_real_built_runtime(self) -> None:
        assert_native_mode_requires_real_built_runtime(
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

        scorecard = run_native_benchmark_with_report(
            self,
            runner=benchmarks.run_built_native_full_benchmarks,
            report_name="benchmarks-native-full.json",
        )
        assert_built_native_combined_scorecard_fields(
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
