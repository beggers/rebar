from __future__ import annotations

import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest import mock


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

from rebar_harness import benchmarks


MATURIN = shutil.which("maturin")


class BuiltNativeBenchmarkSmokeTest(unittest.TestCase):
    def test_native_smoke_mode_requires_real_built_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "benchmarks-native-smoke.json"
            with mock.patch.object(
                benchmarks,
                "provision_built_native_runtime",
                return_value=(
                    None,
                    None,
                    "built-native mode unavailable because no `maturin` executable was found on PATH",
                ),
            ):
                with self.assertRaisesRegex(
                    benchmarks.NativeBenchmarkProvisionError,
                    "no `maturin` executable was found on PATH",
                ):
                    benchmarks.run_built_native_smoke_benchmarks(report_path=report_path)

            self.assertFalse(report_path.exists())

    @unittest.skipUnless(
        MATURIN is not None,
        "built-native benchmark smoke requires a maturin executable on PATH",
    )
    def test_native_smoke_mode_writes_built_native_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "benchmarks-native-smoke.json"
            scorecard = benchmarks.run_built_native_smoke_benchmarks(report_path=report_path)
            self.assertTrue(report_path.is_file())

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
