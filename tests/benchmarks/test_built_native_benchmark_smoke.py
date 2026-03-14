from __future__ import annotations

import unittest

from tests.benchmarks.native_benchmark_test_support import (
    MATURIN,
    assert_native_mode_requires_real_built_runtime,
    benchmarks,
    run_native_benchmark_with_report,
)


class BuiltNativeBenchmarkSmokeTest(unittest.TestCase):
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
        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["phase"], "phase2-module-boundary-suite")
        self.assertEqual(scorecard["implementation"]["module_name"], "rebar")
        self.assertEqual(scorecard["implementation"]["adapter"], "rebar.module-surface")
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
        self.assertEqual(scorecard["artifacts"]["selection_mode"], "smoke")
        self.assertEqual(len(scorecard["artifacts"]["manifests"]), 3)
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


if __name__ == "__main__":
    unittest.main()
