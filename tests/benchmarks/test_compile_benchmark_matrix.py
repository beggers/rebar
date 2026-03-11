from __future__ import annotations

import json
import pathlib
import platform
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.json"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"


class CompileBenchmarkMatrixTest(unittest.TestCase):
    def test_runner_regenerates_compile_matrix_scorecard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "benchmarks.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rebar_harness.benchmarks",
                    "--manifest",
                    str(MANIFEST_PATH),
                    "--report",
                    str(report_path),
                ],
                check=True,
                cwd=REPO_ROOT,
                env={"PYTHONPATH": str(PYTHON_SOURCE)},
                capture_output=True,
                text=True,
            )

            summary = json.loads(result.stdout.strip())
            self.assertEqual(
                summary,
                {
                    "known_gap_count": 6,
                    "measured_workloads": 0,
                    "module_workloads": 0,
                    "parser_workloads": 6,
                    "total_workloads": 6,
                },
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["phase"], "phase1-compile-path-suite")
        self.assertEqual(scorecard["baseline"]["python_implementation"], platform.python_implementation())
        self.assertEqual(scorecard["baseline"]["python_version"], platform.python_version())
        self.assertEqual(scorecard["baseline"]["python_version_family"], "3.12.x")
        self.assertEqual(scorecard["implementation"]["module_name"], "rebar")
        self.assertEqual(scorecard["implementation"]["build_mode"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["timing_path"], "source-tree-shim")
        self.assertFalse(scorecard["implementation"]["native_module_loaded"])
        self.assertEqual(scorecard["implementation"]["native_module_name"], "rebar._rebar")
        self.assertIsNone(scorecard["implementation"]["native_scaffold_status"])
        self.assertIsNone(scorecard["implementation"]["native_target_cpython_series"])
        self.assertEqual(scorecard["environment"]["runner_version"], "phase1")
        self.assertEqual(
            scorecard["artifacts"]["manifest"], "benchmarks/workloads/compile_matrix.json"
        )
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "compile-matrix")
        self.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
        self.assertEqual(scorecard["summary"]["total_workloads"], 6)
        self.assertEqual(scorecard["summary"]["parser_workloads"], 6)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 3)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 2)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 1)
        self.assertIsInstance(scorecard["summary"]["baseline_median_ns"], int)
        self.assertGreater(scorecard["summary"]["baseline_median_ns"], 0)
        self.assertGreater(scorecard["summary"]["baseline_median_ops_per_second"], 0)
        self.assertIsNone(scorecard["summary"]["implementation_median_ns"])
        self.assertEqual(scorecard["families"]["parser"]["workload_count"], 6)
        self.assertEqual(scorecard["families"]["parser"]["known_gap_count"], 6)
        self.assertEqual(scorecard["families"]["parser"]["cache_modes"]["cold"]["workload_count"], 3)
        self.assertEqual(scorecard["families"]["parser"]["cache_modes"]["warm"]["workload_count"], 2)
        self.assertEqual(scorecard["cache_modes"]["purged"]["workload_count"], 1)
        self.assertEqual(scorecard["deferred"][0]["area"], "module-boundary")
        self.assertEqual(scorecard["deferred"][0]["follow_up"], "RBR-0015")
        self.assertEqual(len(scorecard["workloads"]), 6)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        first_workload = scorecard["workloads"][0]
        self.assertEqual(first_workload["bucket"], "tiny-literal")
        self.assertEqual(first_workload["family"], "parser")
        self.assertEqual(first_workload["cache_mode"], "cold")
        self.assertEqual(first_workload["timing_scope"], "compile-path-proxy")
        self.assertEqual(first_workload["text_model"], "str")
        self.assertEqual(
            first_workload["syntax_features"],
            ["literal-text", "assertions-and-anchors"],
        )
        self.assertEqual(first_workload["baseline_timing"]["status"], "measured")
        self.assertGreater(first_workload["baseline_ns"], 0)
        self.assertGreater(first_workload["baseline_ops_per_second"], 0)
        self.assertEqual(first_workload["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(first_workload["implementation_ns"])
        self.assertIsNone(first_workload["implementation_ops_per_second"])
        self.assertIsNone(first_workload["speedup_vs_cpython"])

        bytes_workloads = [
            workload for workload in scorecard["workloads"] if workload["text_model"] == "bytes"
        ]
        self.assertEqual(len(bytes_workloads), 2)
        self.assertTrue(
            any("pattern-text-model" in workload["syntax_features"] for workload in bytes_workloads)
        )


if __name__ == "__main__":
    unittest.main()
