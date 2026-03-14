from __future__ import annotations

import unittest

from tests.benchmarks.native_benchmark_test_support import (
    MATURIN,
    assert_native_mode_requires_real_built_runtime,
    benchmarks,
    run_native_benchmark_with_report,
)


class BuiltNativeFullSuiteBenchmarkTest(unittest.TestCase):
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
        _, selected_workloads = benchmarks.load_manifests(list(benchmarks.DEFAULT_MANIFEST_PATHS))
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
        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["phase"], "phase3-regression-stability-suite")
        self.assertEqual(scorecard["implementation"]["module_name"], "rebar")
        self.assertEqual(scorecard["implementation"]["adapter_mode_requested"], "built-native")
        self.assertEqual(scorecard["implementation"]["adapter_mode_resolved"], "built-native")
        self.assertEqual(scorecard["implementation"]["build_mode"], "built-native")
        self.assertEqual(scorecard["implementation"]["timing_path"], "built-native")
        self.assertTrue(scorecard["implementation"]["native_module_loaded"])
        self.assertEqual(scorecard["implementation"]["native_module_name"], "rebar._rebar")
        self.assertEqual(scorecard["implementation"]["native_build_tool"], "maturin")
        self.assertTrue(str(scorecard["implementation"]["native_wheel"]).startswith("rebar-"))
        self.assertIsNone(scorecard["implementation"]["native_unavailable_reason"])
        self.assertEqual(
            scorecard["environment"]["execution_model"],
            "single-interpreter subprocess workload probes against a built native wheel",
        )
        self.assertEqual(scorecard["artifacts"]["manifest"], None)
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        self.assertEqual(scorecard["artifacts"]["selection_mode"], "full")
        self.assertEqual(
            len(scorecard["artifacts"]["manifests"]),
            len(benchmarks.DEFAULT_MANIFEST_PATHS),
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
